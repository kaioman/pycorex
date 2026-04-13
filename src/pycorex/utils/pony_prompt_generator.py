import json
import os
import random
from typing import Optional, Any
from pycorex.core.base_prompt_generator import BasePromptGenerator

class PonyPromptGenerator(BasePromptGenerator):
    """
    Ponyモデル専用のtxt2img用ランダムプロンプトジェネレータークラス。
    「Aoi」という架空のアンドロイドをモチーフとしたキャラを生成するためのメソッドを備えています。
    """

    def __init__(
        self, 
        aoi_path: str = "tests/prompt/persona/Aoi.json",
        camera_path: str = "tests/prompt/camera_angules.json",
        wardrobe_path: str = "tests/prompt/wardrobe.json",
        environment_path: str = "tests/prompt/environments.json"):
        self.environment_data = self._load_json(environment_path)
        self.data = self._load_json(aoi_path)
        self.camera_data = self._load_json(camera_path)
        self.wardrobe_data = self._load_json(wardrobe_path)
    
    def _load_json(self, path: str) -> dict[str, Any]:
        """
        指定されたパスからJSONファイルをロードします。
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} が見つかりません。")
            
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _pick_weighted_item(self, item_list: list[dict], current_level: int, target_id: Optional[str] = None) -> Optional[dict]:
        """
        【共通ロジック】
        min_lv, max_lv の範囲内にあり、かつ weight に基づいた抽選を行う。
        """
        
        # ID直接指定
        if target_id:
            for item in item_list:
                if item.get("id") == target_id:
                    return item
        
        # 1. レベル適合チェック (記述がない場合は全レベル対応とみなす)
        candidates = [
            item for item in item_list 
            if item.get("min_lv", 0) <= current_level <= item.get("max_lv", 5)
        ]
        
        if not candidates:
            return None
            
        # 2. 重み(weight)の取得 (記述がない場合は 1.0)
        weights = [item.get("weight", 1.0) for item in candidates]
        
        # 3. 確率に基づき1つ選択
        return random.choices(candidates, weights=weights, k=1)[0]
    
    def _get_environment_tags(self, scene_tags: str, outfit_id: str) -> str:
        location_tag = self._get_specific_env_tag(scene_tags, self.environment_data["locations"], outfit_id)
        lighting_tag = self._get_specific_env_tag(scene_tags, self.environment_data["lightings"], outfit_id)
        texture_tag = self._get_specific_env_tag(scene_tags, self.environment_data["textures"], outfit_id)
        
        # 決定された環境タグを結合
        env_tags = ",".join(filter(None, [location_tag, lighting_tag, texture_tag]))
        return env_tags

    def _get_specific_env_tag(self, scene_tags: str, env_list: list[dict], outfit_id: str) -> Optional[str]:

        # シーンタグに既存の環境要素が含まれているかチェック
        #if any(f' {env_item["tags"]}' in f' {scene_tags}' or scene_tags.startswith(env_item["tags"]) for env_item in env_list):
        #    return None # シーンタグに存在する場合は抽選しない
        scene_tag_names = set()
        for tag in scene_tags.split(","):
            cleaned_tag = tag.strip()
            if cleaned_tag.startswith("(") and ":" in cleaned_tag:
                cleaned_tag = cleaned_tag[1:cleaned_tag.rfind(":")].strip() # (tag:1.X) -> tag
            cleaned_tag = cleaned_tag.replace("_", " ")
            scene_tag_names.add(cleaned_tag)
        if any(env_item["tags"].replace("_", "") in scene_tag_names for env_item in env_list):
            return None

        # 互換性のあるアイテムをフィルタリング
        compatible_items =[
            item for item in env_list
            if outfit_id not in item.get("not_compatible_outfits", [])
        ]
        
        if not compatible_items:
            return None
        
        # ランダム抽選
        return random.choice(compatible_items)["tags"]

    def generate_prompt(
        self, 
        level: int = 1, 
        target_scene_id: Optional[str] = None,
        test_outfit_id: Optional[str] = None,
        test_scene_id_override: Optional[str] = None, # target_scene_id とは別にテスト用
        test_camera_name: Optional[str] = None) -> tuple[str, str]:
        """
        指定されたレベルに基づき、画風を死守したプロンプトを生成する。

        Parameters
        ----------
        level : int
            生成するプロンプトのレベル。高レベルほど詳細なプロンプトが生成される場合があります。
        target_scene_id : str, optional
            特定のシーンID。指定された場合、そのシーンに特化したプロンプトが生成されます。

        Returns
        -------
        tuple[str, str]
            ポジティブプロンプトとネガティブプロンプトのタプルを返します。
        """
        
        # --- [1. 基礎・画風設定] ---
        rating = "rating_explicit" if level >= 3 else "rating_safe"
        quality = f"(score_9, score_8_up:1.2), {rating}"
        core = self.data["base_identity_tags"]
        style = self.data["base_style"]
        
        # --- [2. 衣装の抽選 (Outfits & Innerwear)] ---
        if test_outfit_id:
            outfit = next((item for item in self.wardrobe_data["outfits"] if item["id"] == test_outfit_id), None)
            if not outfit:
                self.logger.warning(f"Test outfit ID {test_outfit_id} not found. Falling back to random selection.")
                outfit = self._pick_weighted_item(self.wardrobe_data["outfits"], level)
        else:
            outfit = self._pick_weighted_item(self.wardrobe_data["outfits"], level)
        
        wardrobe_tags = outfit['tags']
        
        # innerwearの結合判定
        roll = random.random() * 100
        threshold = {1: 0, 2:20, 3: 85, 4:100}.get(level, 100)
        inner = {}
        if roll < threshold:
            inner = self._pick_weighted_item(self.wardrobe_data["innerwear_sets"]["styles"], level)
            if inner:
                wardrobe_tags += f",{inner['tags']}"
        
        target_fabric = random.choice(outfit["parts"]) if outfit["parts"] else "clothing"

        # --- [3. 感情・シーン・カメラの抽選] ---
        exp_data = self._pick_weighted_item(self.data["expression_logic"]["emotional_range"], level)

        # outfitに定義されたcompatible_emotional_rangeを考慮して感情データを抽選
        compatible_emotional_range_ids = outfit.get("compatible_emotional_range")
        if compatible_emotional_range_ids:
            filtered_emotional_range = [item for item in self.data["expression_logic"]["emotional_range"] if item["id"] in compatible_emotional_range_ids]
            exp_data = self._pick_weighted_item(filtered_emotional_range, level)
        else:
            exp_data = self._pick_weighted_item(self.data["expression_logic"]["emotional_range"], level)

        # outfitに定義されたcompatible_scene_logicを考慮してシーンデータを抽選
        compatible_scene_logic_ids = outfit.get("compatible_scene_logic")
        if compatible_scene_logic_ids:
            filtered_scene_logic = [item for item in self.data["scene_logic"]["items"] if item["id"] in compatible_scene_logic_ids]
            if test_scene_id_override:
                scene_data = self._pick_weighted_item(filtered_scene_logic, level, test_scene_id_override)
            else:
                scene_data = self._pick_weighted_item(filtered_scene_logic, level, target_scene_id)
        else:
            scene_data = self._pick_weighted_item(self.data["scene_logic"]["items"], level, target_scene_id)
        
        # 破壊可能シーン判定
        if scene_data and scene_data.get("destructible_scene", False):
            target_fabric = outfit.get("destructible_tags", "clothing")
        else:
            target_fabric = random.choice(outfit["parts"]) if outfit["parts"] else "clothing"
        
        if test_camera_name:
            cam_data = next((item for item in self.camera_data["camera_angles"] if item["name"] == test_camera_name), None)
            if not cam_data:
                self.logger.warning(f"Test camera name {test_camera_name} not found. Falling back to random selection.")
                cam_data = random.choice(self.camera_data["camera_angles"])
        else:
            cam_data = random.choice(self.camera_data["camera_angles"])

        # --- [3.5. 環境の抽選]
        # scene_logicにlocation, lighting, textureのタグが含まれていない場合に抽選する
        environment_tags = self._get_environment_tags(scene_data["tags"], outfit["id"])
            
        # --- [4. プレースホルダーの置換] ---
        #expression = exp_data["tags"] if exp_data else "soft_expression"
        scene_raw = scene_data["tags"] if scene_data else ""
        # 置換実行
        scene = scene_raw.replace("{camera}", cam_data["tags"])
        scene = scene.replace("{target_fabric}", target_fabric)
        scene = scene.replace("{target_edge}", f"{target_fabric}_edge")
        
        # 構図と衣装の解決ロジック
        if "sitting" in scene_raw:
            if "standing" in wardrobe_tags:
                wardrobe_tags = wardrobe_tags.replace("standing", "(standing:0.5)")
        elif "standing" in scene_raw:
            if "sitting" in wardrobe_tags:
                wardrobe_tags = wardrobe_tags.replace("sitting", "(sitting:0.5)")
        
        # 構図による映らないタグの自動尾削除
        if any(clip in scene for clip in ["close-up", "portrait", "upper_body", "sitting"]):
            # 下半身系のタグをリストアップして一括削除
            lower_body_tags_to_remove = ["sneakers", "joggers", "pants", "skirt", "shimapan", "boots"]

            if outfit and outfit["id"] == "china_dress":
                lower_body_tags_to_remove.remove("skirt")
                
            for t in lower_body_tags_to_remove:
                # カンマも含めて綺麗に削除
                if t in wardrobe_tags:
                    wardrobe_tags = wardrobe_tags.replace(f", {t}", "").replace(t, "")

        # --- [5. 環境・ネガティブ設定] ---
        #env = self.data.get("default_environment", {})
        #env_tags = f"{env['location']}, {env['lighting']}, {env['texture']}"
        
        # シーン側で「外を見る」系のタグがある場合、coreの「こちらを見る」を無効化する
        if "looking_out_window" in scene or "looking_away" in scene:
            core = core.replace("looking_at_viewer", "(looking away:1.2)")
        
        # --- [6. プロンプト結合] ---
        # 黄金比：品質 -> 画風 -> 核心 -> 状況 -> 表情 -> 環境
        positive = " BREAK ".join([
            quality, 
            style, 
            core, 
            scene + ", " + environment_tags, 
            wardrobe_tags,
            #expression, 
            #env_tags, 
            "masterpiece, high quality"
        ])

        # --- [7. 鉄壁のネガティブプロンプト] ---
        # 1. 全レベル共通の『聖域』を取得
        holy_grail = self.data.get("negative_holy_grail", "")

        # 2. 【新設】レベルに応じた追加の拒絶要素を抽選/取得
        neg_logic_items = self.data.get("negative_logic", {}).get("items", [])
        active_tier_negs = [
            item["tags"] for item in neg_logic_items
            if item.get("min_lv", 0) <= level <= item.get("max_lv", 5)
        ]
        tier_neg_tags = ", ".join(active_tier_negs)
        
        # 3. 低品質排除のベース
        base_neg = "(worst quality:1.4), (low quality:1.4), lowres, bad anatomy, bad hands, text, error, blurry"
        
        # 4. 全てを融合
        # 聖域(基本) + ティア別防壁(動的) + 品質ベース
        negative = f"{holy_grail}, {tier_neg_tags}, {base_neg}"
        #negative = f"{holy_grail}, {base_neg}"
        
        # --- [8. ログ出力] ---
        print(f"--- [Lv{level}] Dynamic Synthesis Log ---")
        print(f"Outfit:   {outfit['id']} (Target: {target_fabric})")
        if inner:
            print(f"Inner:    {inner['id']}")
        print(f"Scene:    {scene_data['id']}")
        print(f"Environment:   {environment_tags}")
        print(f"Camera:   {cam_data['name']}")
        print(f'Final Scene Tags: {scene + ", " + environment_tags}') 
        print(f"--- Prompt ---") 
        print(f"Positive Prompt:") 
        print(f"{positive}") 
        print(f"Negative Prompt:") 
        print(f"{negative}") 
        
        return positive, negative