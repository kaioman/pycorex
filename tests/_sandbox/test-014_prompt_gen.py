import re
import json
import random

class AoiPromptGenerator:
    def __init__(self, json_data):
        self.persona = json_data["persona"]
        self.models = json_data["models"]
        self.modifiers = json_data["modifiers"]
        self.states = json_data["states"]
        self.system = json_data["system"]
        self.wardrobe = json_data["wardrobe"]
        self.aoi = json_data["persona"] # 'aoi'属性を'persona'データで初期化

    def clean_tag(self, tag):
        return re.sub(r'[\(\):0-9.]', '', tag).strip()

    def generate(self, level=1, situation_id=None, outfit_id=None):
        """
        指定されたレベルとシチュエーションに基づきプロンプトを生成。
        レベル(0-4)に応じて表情、露出、タグを動的に制御。
        """
        lv_key = f"level_{level}"
        mod = self.modifiers["intensity_definitions"][lv_key]

        # --- [1. シチュエーションと衣装の決定] ---
        sit = next((s for s in self.models["situations"] if s["id"] == situation_id), None)
        if not sit:
            sit = random.choice(self.models["situations"])

        # --- [2. 視線の抽選ロジック] ---
        # system_config.json の gaze_control
        gaze_cfg = self.system.get("gaze_control", {"options": [{"tags": "looking at viewer", "weight": 1}]})
        gaze_options = gaze_cfg.get("options", [])
        selected_gaze = random.choices(
            [g["tags"] for g in gaze_options],
            weights=[g["weight"] for g in gaze_options],
            k=1
        )[0]
        
        # --- [3. エクストリームパースの抽選 (たまに発生)] ---
        perspective_cfg = self.system.get("camera_logic", {}).get("extreme_perspective", "")
        perspective_tags = ""
        if random.random() < perspective_cfg.get("probability", 0.0):
            perspective_tags = perspective_cfg.get("tags", "")
        
        # --- [4. 表情と身体反応の合成] ---
        exp_range = [e for e in self.persona["features"]["expression_logic"]["emotional_range"]
                    if e.get("min_lv", 0) <= level <= e.get("max_lv", 4)]
        weights = [e["weight"] for e in exp_range]
        selected_exp = random.choices(exp_range, weights=weights, k=1)[0]
        
        # アイデンティティ(shakerato)とレベル別アイロジックの合成
        eye_logic = mod.get("eye_logic", "")        

        # mod["eye_logic"] から "looking ..." 系の古い視線指定を排除
        clean_eye_logic = ", ".join([t.strip() for t in eye_logic.split(",") 
                                if "looking" not in t and "at viewer" not in t])
        
        exclusive_tags = ", ".join(mod.get("exclusive_tags", [])) if mod.get("exclusive_tags", []) else ""
        if level == 3:
            # Lv.3は「動揺しつつ睨む」
            final_expression = f"shakerato expression, teary eyes, glaring, {selected_exp['tags']}, {clean_eye_logic}"
        elif level == 4:
            # Lv.4は「壊れ」を抑制し、「屈辱に耐えながら鋭く睨む」
            # shakeratoを外し、より鋭いタグを優先配置
            #final_expression = f"glaring, intense gaze, (teary eyes:1.1), indignant expression, {selected_exp['tags']}"
            final_expression = f"{selected_exp['tags']}, {clean_eye_logic}, {exclusive_tags}"
        else:
            final_expression = f"{selected_exp['tags']}, {clean_eye_logic}"
        
        if "looking" in final_expression:
            selected_gaze = ""
        if selected_gaze:
            final_expression = f"{final_expression}, {selected_gaze}"
                
        # 3. 衣装の決定と状態(Outfit States)の適用
        # 衣装のフィルタリング
        available_outfits = [o for o in self.wardrobe["outfits"] if o.get("min_lv", 0) <= level]
        
        if outfit_id:
            selected_outfit = next((o for o in available_outfits if o["id"] == outfit_id), available_outfits[0])
        else:
            # 20%の確率で完全ランダム、それ以外はシチュエーションのデフォルト
            if random.random() < self.models["global_logic"]["random_outfit_chance"]:
                selected_outfit = random.choice(available_outfits)
            else:
                default_id = sit["default_outfit"]
                selected_outfit = next((o for o in available_outfits if o["id"] == default_id), random.choice(available_outfits))

        # 衣装の乱れ状態 (Lvに応じてランダムまたは固定)
        state_lv = str(min(level, 4))
        
        # 基本の状態タグ（tops, bottoms）
        #outfit_state = f"{self.states['outfit_tags']['tops'][state_lv]}, {self.states['outfit_tags']['bottoms'][state_lv]}"
        tops_state = self.states['outfit_tags']['tops'][state_lv]
        bottoms_state = self.states['outfit_tags']['bottoms'][state_lv]
        outfit_state = f"{tops_state}, {bottoms_state}"
        
        # Lv.3以上の場合は、下着(underwear)の露出を物理的に追加
        if level >= 3:
            # シチュエーションや衣装に応じて下着の質感を指定（Aoiのアイデンティティに合わせる）
            underwear_tags = "(visible_panties:1.3), (bra_visible:1.2), (undressing:1.1), (skirt_lift:1.1)"
            outfit_state += f", {underwear_tags}"
            
            # Lv.3専用の「着崩し」をさらに強調
            outfit_state += ", (disheveled_clothes:1.2), (shoulder_drop:1.2)"
            
        # --- [2. 修正：髪と瞳のタグ構築] ---
        hair_data = self.persona["features"]["hair"]
                
        # 4. ネガティブプロンプトの動的構築
        neg_base = self.system["negative_prompts"]["default"]
        # 黒髪を守るために、forbidden(茶髪、金髪等)をネガティブに動的追加
        forbidden_hair = hair_data['protection']['forbidden']
        neg_base += f", {forbidden_hair}"
        
        if level < 4:
            # Lv.4未満は露出禁止タグを追加
            neg_base += ", (pussy_exposure:1.5), (nipples:1.5), (climax:1.5), (pubic_hair:1.5)"

        # 5. プロンプトの結合
        persona_name = self.persona["name"]
        persona_tag = f"({persona_name}:1.2)"

        #eyes_data = self.persona["features"]["eyes"]
        #eye_tags = f"{eyes_data['base']}, {eyes_data['logic']['active']}"
        # Base + Logic(looking at viewer等) を結合
        #eye_tags = f"{self.persona['features']['eyes']['base']}, {self.persona['features']['eyes']['logic']['active']}"
        eye_tags = f"{self.persona['features']['eyes']['base']}"

        # Base + Active(shiny hair等) を結合
        hair_tags = f"{hair_data['base']}, {hair_data['protection']['active']}"

        # シチュエーションごとの個別設定を取得
        selected_angle = random.choice(sit.get("camera_angles", ["eye level"]))
        if level >= 3:
            #angle_choices = ["from below, low angle", "dutch angle, close-up", "from front, intense gaze focus"]
            selected_angle = f"{selected_angle}, from below, low angle"
        selected_pose_desc = random.choice(sit.get("pose_variations", ["standing"]))
        
        positive_components = [
            self.system["core_quality"]["score_tags"],
            perspective_tags,
            selected_angle,
            f"1girl, {persona_tag}, {self.persona['base_style']}",
            final_expression,

            hair_tags,
            eye_tags,
            f"pose_{random.choice(sit['recommended_poses'])}, {selected_pose_desc}", # ポーズ番号＋具体的動作

            self.persona["physique"]["body"],
            self.persona["physique"]["breast_size"],            
            self.persona["fixed_accessories"],
            selected_outfit["tags"],
            outfit_state,
            sit["background"],
            sit["lighting"],
            self.system.get("environment_defaults", {}).get("lighting", "cinematic lighting"),
            #self.system["core_quality"]["technical"],
        ]

        ## Lv.4専用タグの追加
        #if level == 4:
        #    positive_components.insert(10, ", ".join(mod.get("exclusive_tags", [])))

        # 重複タグの削除ロジック (順番を維持したまま set で重複を除去)
        # seen = set()
        # clean_components = []
        # for comp in ", ".join(filter(None, positive_components)).split(","):
        #     tag = comp.strip()
        #     if tag and tag not in seen:
        #         clean_components.append(tag)
        #         seen.add(tag)
        
        seen_base_tags = set()
        final_components = []
        for comp in positive_components:
            base = self.clean_tag(comp)
            if base not in seen_base_tags:
                final_components.append(comp)
                seen_base_tags.add(base)
                
        final_positive = ", ".join(final_components)
        
        return {
            "positive": final_positive,
            "negative": neg_base,
            "meta": {
                "level": level,
                "label": mod["label"],
                "situation": sit["name"],
                "outfit": selected_outfit["id"]
            }
        }

# 1. 各JSONファイルのパス（実行スクリプトと同じディレクトリにある想定）

json_files = {
    "persona": "tests/prompt/persona/Aoi.json",
    "models": "tests/prompt/models.json",
    "modifiers": "tests/prompt/modifiers.json",
    "states": "tests/prompt/outfit_states.json",
    "system": "tests/prompt/system_config.json",
    "wardrobe": "tests/prompt/wardrobe.json"
}

# 2. データのロード
loaded_data = {}
try:
    for key, filename in json_files.items():
        with open(filename, 'r', encoding='utf-8') as f:
            loaded_data[key] = json.load(f)

    # --- 実行テスト ---
    # (ここにユーザーから提供された各JSON文字列が入る想定)
    generator = AoiPromptGenerator(loaded_data)

    # Lv.2 (Suggestive) でランダム生成
    result = generator.generate(level=3)

    print(f"--- [Lv.{result['meta']['level']}: {result['meta']['label']}] Situation: {result['meta']['situation']}")
    print(f"Outfit: {result['meta']['outfit']}")
    print(f"\nPOSITIVE PROMPT:\n{result['positive']}")
    print(f"\nNEGATIVE PROMPT:\n{result['negative']}")
except Exception as e:
    print(f"Error during prompt generation: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")