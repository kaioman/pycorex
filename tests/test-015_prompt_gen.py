import json

# 1. 原点に基づいた Aoi.json のモックデータ
aoi_json_data = {
    "persona": {
        "name": "Aoi",
        # 成功プロンプトの構成 + アイデンティティ
        "base_identity_tags": "1girl, (Aoi:1.2), (pure black hair:1.3), long hair, blunt bangs, blue eyes, (pink and black headphones:1.2), (black leather choker:1.2)",
        "base_style": "1980s retro anime style, Haruhiko Mikimoto style, premium OVA aesthetic, (vintage_cel_shading:1.2), (hand-drawn_look:1.2)",
        "features": {
            "expression": "(gentle smile:1.1), (kind eyes:1.1), soft_expression"
        }
    },
    "system": {
        "core_quality": {
            "score_tags": "(score_9, score_8_up:1.2), rating_safe"
        },
        "environment_defaults": {
            "lighting": "golden hour lighting, cinematic grain",
            "background": "sitting in a classroom at dusk"
        }
    }
}

def generate_origin_prompt(data):
    p = data["persona"]
    s = data["system"]
    
    # 黄金比プロンプトの組み立て順序
    components = [
        s["core_quality"]["score_tags"],    # 1. 品質・レーティング
        p["base_identity_tags"],           # 2. 核心的な外見特徴（髪・瞳・キャラ名）
        p["base_style"],                   # 3. 美樹本・80年代OVAスタイル
        p["features"]["expression"],       # 4. 表情（原点のsoft/gentle）
        s["environment_defaults"]["background"], # 5. シチュエーション（教室）
        s["environment_defaults"]["lighting"],   # 6. ライティング（夕暮れ）
        "masterpiece, high quality"        # 7. 締め
    ]
    
    # カンマで結合して余計な空白を削除
    return ", ".join([c.strip() for c in components if c])

# テスト実行
if __name__ == "__main__":
    origin_prompt = generate_origin_prompt(aoi_json_data)
    print("--- Generated Origin Prompt ---")
    print(origin_prompt)