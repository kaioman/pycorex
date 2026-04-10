import json
import os
import random

class AoiIroncladGenerator:
    def __init__(self, 
                api_path="tests/prompt/persona/Aoi.json",
                camera_path="tests/prompt/camera_angules.json",
                wardrobe_path="tests/prompt/wardrobe.json"):
        self.data = self._load_json(api_path)
        self.camera_data = self._load_json(camera_path)
        self.wardrobe_data = self._load_json(wardrobe_path)
    
    def _load_json(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} が見つかりません。")
            
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _pick_weighted_item(self, item_list, current_level, target_id=None):
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
    
    def generate(self, level=1, target_scene_id=None):
        """
        指定されたレベルに基づき、画風を死守したプロンプトを生成する。
        """
        
        # --- [1. 基礎・画風設定] ---
        rating = "rating_explicit" if level >= 3 else "rating_safe"
        quality = f"(score_9, score_8_up:1.2), {rating}"
        core = self.data["base_identity_tags"]
        style = self.data["base_style"]
        
        # --- [2. 衣装の抽選 (Outfits & Innerwear)] ---
        outfit = self._pick_weighted_item(self.wardrobe_data["outfits"], level)
        wardrobe_tags = f"{outfit['tags']}:1.3"
        
        # innerwearの結合判定
        roll = random.random() * 100
        threshold = {1: 0, 2:20, 3: 85, 4:100}.get(level, 100)
        inner = {}
        if roll < threshold:
            inner = self._pick_weighted_item(self.wardrobe_data["innerwear_sets"]["styles"], level)
            if inner:
                wardrobe_tags += f", {inner['tags']}:1.2"
        
        target_fabric = random.choice(outfit["parts"]) if outfit["parts"] else "clothing"

        # --- [3. 感情・シーン・カメラの抽選] ---
        exp_data = self._pick_weighted_item(self.data["expression_logic"]["emotional_range"], level)
        scene_data = self._pick_weighted_item(self.data["scene_logic"]["items"], level, target_scene_id)
        cam_data = random.choice(self.camera_data["camera_angles"])
        
        # --- [4. プレースホルダーの置換] ---
        expression = exp_data["tags"] if exp_data else "soft_expression"
        scene_raw = scene_data["tags"] if scene_data else ""
        # 置換実行
        scene = scene_raw.replace("{camera}", cam_data["tags"])
        scene = scene.replace("{target_fabric}", target_fabric)
        scene = scene.replace("{target_edge}", f"{target_fabric}_edge")
        
        # 構図による映らないタグの自動尾削除
        if any(clip in scene for clip in ["close-up", "portrait", "upper_body", "sitting"]):
            # 下半身系のタグをリストアップして一括削除
            lower_body_tags = ["sneakers", "joggers", "pants", "skirt", "shimapan", "boots"]
            for t in lower_body_tags:
                # カンマも含めて綺麗に削除
                wardrobe_tags = wardrobe_tags.replace(f", {t}", "").replace(t, "")
        
        # --- [5. 環境・ネガティブ設定] ---
        env = self.data.get("default_environment", {})
        env_tags = f"{env['location']}, {env['lighting']}, {env['texture']}"
        
        # シーン側で「外を見る」系のタグがある場合、coreの「こちらを見る」を無効化する
        if "looking_out_window" in scene or "looking_away" in scene:
            core = core.replace("looking_at_viewer", "(looking away:1.2)")
        
        # --- [6. プロンプト結合] ---
        # 黄金比：品質 -> 核心 -> 画風 -> 表情 -> 状況 -> 環境
        positive = ", ".join([
            quality, 
            scene, 
            wardrobe_tags,
            core, 
            style, 
            expression, 
            env_tags, 
            "masterpiece"
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

        # --- [8. ログ出力] ---
        print(f"--- [Lv{level}] Dynamic Synthesis Log ---")
        print(f"Outfit:   {outfit['id']} (Target: {target_fabric})")
        if inner:
            print(f"Inner:    {inner['id']}")
        print(f"Scene:    {scene_data['id']}")
        print(f"Camera:   {cam_data['name']}")
        
        return positive, negative

# --- 実行と出力 ---
if __name__ == "__main__":
    json_path = "tests/prompt/persona/Aoi.json"
    
    try:
        generator = AoiIroncladGenerator(json_path)
        
        # 通常版（Lv1）
        pos_1, neg_e = generator.generate(level=1)
        # 微エロ版（Lv2）
        pos_2, neg_e = generator.generate(level=2)
        # 官能版（Lv3）
        pos_3, neg_e = generator.generate(level=3, target_scene_id="lv3_true_shirt_shredded")
        # 限界突破版（Lv4）
        pos_4, neg_e4 = generator.generate(level=4, target_scene_id="lv4_phys_torn_ecstasy")
        
        print(f"=== POSITIVE (Level 1) ===\n{pos_1}\n")
        print(f"=== POSITIVE (Level 2) ===\n{pos_2}\n")
        print(f"=== POSITIVE (Level 3) ===\n{pos_3}\n")
        print(f"=== POSITIVE (Level 4) ===\n{pos_4}\n")
        print(f"=== NEGATIVE (Common) ===\n{neg_e}")
        print(f"=== NEGATIVE (Level 4) ===\n{neg_e4}")
        
    except Exception as e:
        print(f"Error: {e}")