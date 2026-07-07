import json
import os
import random
import libcore_hng.utils.app_logger as app_logger
from typing import Optional, Union, Any
from pycorex.core.base_prompt_generator import BasePromptGenerator
from pycorex.enums.rating_level import RatingLevel
from pycorex.models.prompt import PromptContextModel

class PonyPromptGenerator(BasePromptGenerator):
    """
    Ponyモデル専用のtxt2img用ランダムプロンプトジェネレータークラス。
    personaに基づくコアなアイデンティティタグ、衣装の抽選、シーンロジック、
    カメラアングル、環境要素を組み合わせて、レベルに応じたプロンプトを生成する
    """

    def __init__(
        self, 
        persona_conf: Union[str, dict] = "tests/prompt/pony/persona/Aoi.json",
        camera_conf: Optional[Union[str, dict]] = None,
        wardrobe_conf: Optional[Union[str, dict]] = None,
        environment_conf: Optional[Union[str, dict]] = None,
        expression_conf: Optional[Union[str, dict]] = None,
        scene_conf: Optional[Union[str, dict]] = None,
        mod_config: Optional[Union[str, dict]] = None,
        workflow_path: Optional[Union[str, dict]] = None
    ):
        self.persona_data = self._get_conf(persona_conf)
        persona_path = persona_conf if isinstance(persona_conf, str) else None
        persona_dir = os.path.dirname(os.path.abspath(persona_path)) if persona_path else None
        config_paths = self.persona_data.get("config_paths", {})

        self.camera_data = self._get_conf(
            self._resolve_config_path(camera_conf, config_paths.get("camera_conf"), persona_dir, "tests/prompt/pony/camera_angules.json")
        )
        self.wardrobe_data = self._get_conf(
            self._resolve_config_path(wardrobe_conf, config_paths.get("wardrobe_conf"), persona_dir, "tests/prompt/pony/wardrobe.json")
        )
        self.environment_data = self._get_conf(
            self._resolve_config_path(environment_conf, config_paths.get("environment_conf"), persona_dir, "tests/prompt/pony/environments.json")
        )
        self.expression_data = self._get_conf(
            self._resolve_config_path(expression_conf, config_paths.get("expression_conf"), persona_dir, "tests/prompt/pony/expressions.json")
        )
        self.scene_data = self._get_conf(
            self._resolve_config_path(scene_conf, config_paths.get("scene_conf"), persona_dir, "tests/prompt/pony/scene.json")
        )
        self.mod_config = self._get_conf(
            self._resolve_config_path(mod_config, config_paths.get("mod_config"), persona_dir, "tests/comfyui_workflow/modifications/aoi_workflow_config.json")
        )
        self.workflow_path = self._get_conf(
            self._resolve_config_path(workflow_path, config_paths.get("workflow_path"), persona_dir, "tests/comfyui_workflow/aoi-IPAdapter9_fd1.json")
        )
 
    def _resolve_config_path(
        self,
        conf: Optional[Union[str, dict]],
        persona_config_path: Optional[Union[str, dict]],
        persona_dir: Optional[str],
        default_path: str
    ) -> Union[str, dict]:
        """
        設定ファイルの解決順を定義する。

        優先順位は以下の通り。
        1. 明示的に渡された conf
        2. persona JSON に定義された config_paths
        3. 既定のデフォルトパス
        """
        if conf is not None:
            # 直接指定された設定ファイル／辞書を優先して使用する
            return conf
        if persona_config_path is not None:
            # persona側の config_paths から相対パスを解決する
            return self._resolve_path(persona_config_path, persona_dir)
        # どちらも未指定の場合は既定パスを使用する
        return self._resolve_path(default_path, persona_dir)

    def _resolve_path(self, path: Union[str, dict], persona_dir: Optional[str]) -> Union[str, dict]:
        """
        パス文字列を解決する。

        絶対パス・既存ファイルパスはそのまま返し、相対パスの場合は
        personaファイルのディレクトリ基準で解決を試みる。
        """
        if isinstance(path, dict):
            # すでに辞書データが渡された場合はそのまま返す
            return path
        if not path:
            # 空文字列や None はそのまま返す
            return path
        if os.path.isabs(path) or os.path.exists(path):
            # すでに有効な絶対パスまたは相対パスとして存在する場合はそのまま使用する
            return path
        if persona_dir:
            # personaファイルと同じディレクトリにある設定ファイルを探す
            candidate = os.path.join(persona_dir, path)
            if os.path.exists(candidate):
                return candidate
        # どこにも見つからない場合は元の相対パスを返す
        return path
    
    def _get_conf(self, conf: Union[str, dict]) -> dict[str, Any]:
        """
        指定されたパスからJSONファイルをロードする
        pathがdict型の場合はそのまま返す

        Parameters
        ----------
        conf : Union[str, dict]
            プロンプト生成に関連する設定。JSONファイルへのpath、もしくは設定のdictそのものが入る

        Returns
        -------
        dict[str, Any]
            指定した設定のdict
        """
        
        # dict型の場合はそのまま返す
        if isinstance(conf, dict):
            return conf
        
        # JSONファイルパスチェック
        if not os.path.exists(conf):
            raise FileNotFoundError(f"{conf} が見つかりません。")
        
        # JSONファイルをloadして返す
        with open(conf, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _pick_weighted_item(
        self, 
        item_list: list[dict], 
        current_level: int, 
        target_id: Optional[str] = None) -> Optional[dict]:
        """
        【共通ロジック】
        min_lv, max_lv の範囲内にあり、かつ weight に基づいた抽選を行う
        
        Parameters
        ----------
        item_list : list[dict]
            重み付けされている設定のリスト
        current_level : int
            対象Ratingレベル
        target_id : Optional[str]
            対象ID
            
        Returns
        -------
        Optional[dict]
            ランダム抽選されたtarget_idに対する設定
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
        """
        scene_tagsにlocation, lighting, textureのタグが含まれていない場合に、
        環境データから互換性のあるアイテムを抽選してタグを取得する

        Parameters
        ----------
        scene_tags : str
            検査するsceneタグ
        outfit_id : str
            対象outfit_id

        Returns
        -------
        str
            environmentタグ
        """
        
        location_tag = self._get_specific_env_tag(scene_tags, self.environment_data["locations"], outfit_id)
        lighting_tag = self._get_specific_env_tag(scene_tags, self.environment_data["lightings"], outfit_id)
        texture_tag = self._get_specific_env_tag(scene_tags, self.environment_data["textures"], outfit_id)
        
        # 決定された環境タグを結合
        env_tags = ",".join(filter(None, [location_tag, lighting_tag, texture_tag]))
        return env_tags

    def _get_specific_env_tag(self, scene_tags: str, env_list: list[dict], outfit_id: str) -> Optional[str]:
        """
        シーンタグに既存の環境要素が含まれていないかチェックし、
        互換性のあるアイテムをフィルタリングしてからランダム抽選する

        Parameters
        ----------
        scene_tags : str
            検査するsceneタグ
        env_list : list[dict]
            environmentタグリスト
        outfit_id : str
            対象outfit_id

        Returns
        -------
        Optional[str]
            sceneタグに対して互換性のあるenvironmentタグ
        """
        
        # シーンタグに既存の環境要素が含まれているかチェック
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

    def _get_base_identity(self) -> dict[str, Any]:
        """
        personaのbody_partsセクションを再帰的に処理して、カテゴリごとのタグを収集し、base_identity_tagsとして統合する

        Returns
        -------
        dict[str, Any]
            base_identity_tagsのdict
        """

        # persona_dataのbase_identity_tagsを
        base_identity_tags = self.persona_data.get("base_identity_tags", "")

        # persona_dataのbody_partsを再帰的に処理してtagを収集
        active_body_parts_by_category = {}
        if "body_parts" in self.persona_data:
            def collect_tags_by_category(data, prefix=""):
                for key, value in data.items():
                    full_key = f"{prefix}_{key}" if prefix else key
                    if isinstance(value, list):
                        active_body_parts_by_category[f"{full_key}_parts_tags"] = ", ".join(value)
                    elif isinstance(value, dict):
                        collect_tags_by_category(value, full_key)
            
            collect_tags_by_category(self.persona_data["body_parts"])
        
        all_tags = []
        for _, v in active_body_parts_by_category.items():
            all_tags.append(v)
        body_parts_tags = ", ".join(all_tags)

        # base_identityとbody_partsを結合
        base_identity_tags = f"{base_identity_tags},{body_parts_tags}"

        # base_identity_tagsとして統合
        active_body_parts_by_category["base_identity_tags"] = base_identity_tags
        
        return active_body_parts_by_category
    
    def generate_prompt(
        self, 
        rating_level: RatingLevel = RatingLevel.SAFE, 
        target_scene_id: Optional[str] = None,
        test_outfit_id: Optional[str] = None,
        test_scene_id_override: Optional[str] = None, # target_scene_id とは別にテスト用
        test_camera_name: Optional[str] = None) -> PromptContextModel:
        """
        指定されたレベルに基づき、画風を死守したプロンプトを生成する。

        Parameters
        ----------
        rating_level : RatingLevel
            生成するプロンプトのレベル。高レベルほど詳細なプロンプトが生成される場合があります。
        target_scene_id : str, optional
            特定のシーンID。指定された場合、そのシーンに特化したプロンプトが生成されます。

        Returns
        -------
        PromptContextModel
            プロンプトコンテキストモデルを返す
        """
        
        # --- [1. 基礎・画風設定] ---
        if rating_level <= RatingLevel.EMOTIVE:
            rating = self.persona_data.get("rating", {}).get("safe", "rating_safe")
        elif rating_level == RatingLevel.QUESTIONABLE:
            rating = self.persona_data.get("rating", {}).get("questionable", "rating_questionable")
        elif rating_level >= RatingLevel.EXPLICIT:
            rating = self.persona_data.get("rating", {}).get("explicit", "rating_explicit")
        
        base_score_tags = self.persona_data.get("base_score_tags", "(score_9, score_8_up:1.2)")
        quality = f"{base_score_tags}, {rating}"
        body_parts_data = self._get_base_identity()
        core = body_parts_data.get("base_identity_tags", "")
        style = self.persona_data["base_style"]
        
        # --- [2. 衣装の抽選 (Outfits & Innerwear)] ---
        if test_outfit_id:
            outfit = next((item for item in self.wardrobe_data["outfits"] if item["id"] == test_outfit_id), None)
            if not outfit:
                app_logger.warning(f"Test outfit ID {test_outfit_id} not found. Falling back to random selection.")
                outfit = self._pick_weighted_item(self.wardrobe_data["outfits"], rating_level)
        else:
            outfit = self._pick_weighted_item(self.wardrobe_data["outfits"], rating_level)
        
        # {color}プレースホルダ―をランダムな色に置換
        wardrobe_tags = outfit['tags']
        if "{color}" in wardrobe_tags:
            random_color = random.choice(self.wardrobe_data.get("colors", [""]))
            wardrobe_tags = wardrobe_tags.replace("{color}", random_color)
        
        ## --- [3. シーン(衣服破壊含む)・カメラの抽選] ---

        # target_scene_idのoverride
        if test_scene_id_override:
            target_scene_id = test_scene_id_override
        
        # outfitに定義されたincompatible_scene_logicを考慮してシーンデータを抽選
        incompatible_scene_logic_ids = outfit.get("incompatible_scene_logic", [])
        all_scene_logic_items = self.scene_data.get("scene_logic", [])
        if incompatible_scene_logic_ids:
            filtered_scene_logic = [item for item in all_scene_logic_items if item["id"] not in incompatible_scene_logic_ids]
            scene_data = self._pick_weighted_item(filtered_scene_logic, rating_level, target_scene_id)
        else:
            scene_data = self._pick_weighted_item(all_scene_logic_items, rating_level, target_scene_id)

        # scene_rawを取得
        scene_raw = scene_data["tags"] if scene_data else ""
        
        # innerwearの抽選
        roll = random.random() * 100
        threshold = self.persona_data.get("innerwear_thresholds", {}).get(str(rating_level), 100)
        inner = {}
        inner_top_tags = ""
        inner_bottom_tags = ""
        if roll < threshold:
            # シーンデータのinner_inclusionを考慮して、必要に応じてinnerwearを抽選
            inner = self._pick_weighted_item(self.wardrobe_data["innerwear_sets"]["styles"], rating_level)
            if inner:
                # scene_dataのinner_inclusionに基づいて、innerwearのタグを衣装タグに追加
                inner_tags = inner.get("tags", "")
                inner_top_tags = inner_tags.get("top", "")
                inner_top_other_tags = inner_tags.get("top_other", "")
                inner_bottom_tags = inner_tags.get("bottom", "")
                inner_bottom_other_tags = inner_tags.get("bottom_other", "")
                inner_inclusion = scene_data.get("inner_inclusion")
                
                # inner_inclusionのtop, bottomの両方がTrueの場合、
                # innerwearのトップとボトム両方のタグを衣装タグに追加する
                inner_top_included = False
                inner_bottom_included = False
                if inner_inclusion:
                    inner_top_included = inner_inclusion.get("top", False)
                    inner_bottom_included = inner_inclusion.get("bottom", False)
                if inner_top_included:
                    if inner_top_tags:
                        wardrobe_tags += f", {inner_top_tags}"
                    if inner_top_other_tags:
                        wardrobe_tags += f", {inner_top_other_tags}"
                if inner_bottom_included:
                    if inner_bottom_tags:
                        wardrobe_tags += f", {inner_bottom_tags}"
                    if inner_bottom_other_tags:
                        wardrobe_tags += f", {inner_bottom_other_tags}"

        # カメラアングルの抽選
        if test_camera_name:
            cam_data = next((item for item in self.camera_data["camera_angles"] if item["name"] == test_camera_name), None)
            if not cam_data:
                app_logger.warning(f"Test camera name {test_camera_name} not found. Falling back to random selection.")
                cam_data = random.choice(self.camera_data["camera_angles"])
        else:
            # scene_dataにある除外対象となるカメラアングルを取得
            excluded_angles = scene_data.get("camera_angle_exclude", [])
            
            # 除外リストに含まれないカメラアングルのみ抽選対象とする
            eligible_camera_angles = [
                cam for cam in self.camera_data["camera_angles"]
                if cam["id"] not in excluded_angles
            ]
            if not eligible_camera_angles:
                app_logger.warning("No eligible camera angles found after applying exclusion. Falling back to full list.")
                eligible_camera_angles = self.camera_data["camera_angles"]
            cam_data = random.choice(eligible_camera_angles)
        
        # --- [3.4. 表情の抽選]
        expression_item = self._pick_weighted_item(
            self.expression_data.get("expressions", []),
            rating_level
        )
        expression_tags = expression_item.get("tags", "") if expression_item else ""

        # --- [3.5. 環境の抽選]
        # scene_logicにlocation, lighting, textureのタグが含まれていない場合に抽選する
        environment_tags = self._get_environment_tags(scene_data["tags"], outfit["id"])
        
        # --- [4. プレースホルダーの置換] ---

        ## 置換実行：カメラアングルタグ
        scene = scene_raw.replace("{camera}", cam_data["tags"])
        ## 置換実行：衣服破壊ベースタグ
        if scene_data.get("destructible_scene", False):
            dest_tags_key = scene_data.get("destructible_tags_key", "normal")
            if self.wardrobe_data.get("destructible_base_tags"):
                dest_tags_str = ", ".join(self.wardrobe_data["destructible_base_tags"][dest_tags_key])
                scene = scene.replace("{destructible_fabric}", dest_tags_str)
    
        ## カメラアングルから解像度の推奨値を取得
        ## scene側にsuggested_resolutionがあればそちらを優先
        image_width = scene_data.get("suggested_resolution", {}).get("width", 1024)
        image_height = scene_data.get("suggested_resolution", {}).get("height", 1024)
        if "{camera}" in scene_raw:
            image_width = cam_data.get("suggested_resolution", {}).get("width", 1024)
            image_height = cam_data.get("suggested_resolution", {}).get("height", 1024)

        ## 対象衣服のトップス、ボトムス取得
        outer_top_tags_str = "clothing"
        outer_bottom_tags_str = "clothing"
        outer_socks_tags_str = ""
        if scene_data and outfit.get("outer_tags"):
            if outfit["outer_tags"]["top"]:
                outer_top_tags_str = outfit["outer_tags"]["top"]
            if outfit["outer_tags"]["bottom"]:
                outer_bottom_tags_str = outfit["outer_tags"]["bottom"]
            if outfit["outer_tags"].get("socks"):
                outer_socks_tags_str = outfit["outer_tags"]["socks"]

        ## 置換実行：衣服破壊
        scene = scene.replace("{target_destructible_top}", outer_top_tags_str)
        scene = scene.replace("{target_destructible_bottom}", outer_bottom_tags_str)
        ## 置換実行：フィジカル・インタラクション
        scene = scene.replace("{target_fabric_outer_top}", outer_top_tags_str)
        scene = scene.replace("{target_fabric_outer_bottom}", outer_bottom_tags_str)
        ## 置換実行：インナー
        scene = scene.replace("{target_inner_top}", inner_top_tags)
        scene = scene.replace("{target_inner_bottom}", inner_bottom_tags)
        scene = scene.replace("{target_inner_socks}", outer_socks_tags_str)
        
        # 構図と衣装の解決ロジック
        if "sitting" in scene_raw:
            if "standing" in wardrobe_tags:
                wardrobe_tags = wardrobe_tags.replace("standing", "(standing:0.5)")
        elif "standing" in scene_raw:
            if "sitting" in wardrobe_tags:
                wardrobe_tags = wardrobe_tags.replace("sitting", "(sitting:0.5)")
        
        # シーン側で「外を見る」系のタグがある場合、coreの「こちらを見る」を無効化する
        if "looking_out_window" in scene or "looking_away" in scene:
            core = core.replace("looking_at_viewer", "(looking away:1.2)")
        
        # 競合タグの処理
        if outfit and "conflict_outfits" in outfit:
            for category, conflict_tag_templates in outfit["conflict_outfits"].items():
                body_part_key_in_persona = f"{category}_parts_tags"
                if body_part_key_in_persona in body_parts_data:
                    placeholder = f"{{{body_part_key_in_persona}}}"
                    resoleved_conflict_tags = [
                        template.replace(placeholder, body_parts_data[body_part_key_in_persona])
                        for template in conflict_tag_templates
                    ]
                wardrobe_tags += ", " + ", ".join(resoleved_conflict_tags)

        # --- [5. プロンプト結合] ---
        # 黄金比：品質 -> 画風 -> 核心 -> 表情 -> 状況 -> 服装 -> 環境
        positive_parts = [
            quality, 
            style, 
            core, 
            expression_tags,
            scene,
            wardrobe_tags,
            environment_tags
        ]
        positive = " BREAK ".join(
            [part for part in positive_parts if part]
        )
        # FaceDetailerのポジティブプロンプト
        face_detailer_positive_prompt = f"{quality},{style},{core},{expression_tags}"

        # --- [6. 鉄壁のネガティブプロンプト] ---
        ## 1. 全レベル共通の『聖域』を取得
        holy_grail = self.persona_data.get("negative_holy_grail", "")

        ## 2. レベルに応じた追加の拒絶要素を抽選/取得
        neg_logic_items = self.persona_data.get("negative_logic", {}).get("items", [])
        active_tier_negs = [
            item["tags"] for item in neg_logic_items
            if item.get("min_lv", 0) <= rating_level <= item.get("max_lv", 5)
        ]
        tier_neg_tags = ", ".join(active_tier_negs)
        
        ## 3. 低品質排除のベース
        base_neg = self.persona_data.get("negative_base", "")
        
        ## 4. 全てを融合
        ## 聖域(基本) + ティア別防壁(動的) + 品質ベース
        negative = f"{holy_grail}, {tier_neg_tags}, {base_neg}"
        ## 5. FaceDetailerのネガティブプロンプト
        face_detailer_negative_prompt = f"{holy_grail},{base_neg}"

        # --- [7. ログ出力] ---
        app_logger.info(f"--- [Lv{rating_level}] Dynamic Synthesis Log ---")
        app_logger.info(f"Outfit:   {outfit['id']}")
        if inner:
            app_logger.info(f"Inner:    {inner['id']}")
        app_logger.info(f"Scene:    {scene_data['id']}")
        app_logger.info(f"Environment:   {environment_tags}")
        app_logger.info(f"Camera:   {cam_data['name']}")
        app_logger.info(f"Expression:   {expression_item['name']}")
        app_logger.info(f"Image Resolution: {image_width}x{image_height}")
        app_logger.info(f'Final Scene Tags: {scene + ", " + environment_tags}') 
        app_logger.info(f"--- Prompt ---") 
        app_logger.info(f"Positive Prompt:") 
        app_logger.info(f"{positive}") 
        app_logger.info(f"Negative Prompt:") 
        app_logger.info(f"{negative}") 
        
        return PromptContextModel(
            prompt_level=rating_level,
            scene_id=scene_data["id"],
            positive_prompt=positive,
            negative_prompt=negative,
            image_width=image_width,
            image_height=image_height,
            face_detailer_positive_prompt=face_detailer_positive_prompt,
            face_detailer_negative_prompt=face_detailer_negative_prompt
        )