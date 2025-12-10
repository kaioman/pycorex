import pycorex.configs.app_init as app
from PIL import Image as PIL_image
from pycorex.gemini_client import GeminiClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# 設定クラスメンバ参照確認
print(app.core.config.vertexai.project_id)
print(app.core.config.vertexai.location)

# GeminiClientを初期化
client = GeminiClient(
    api_key=app.core.config.gemini.api_key_vertexai
)

# プロンプトを設定
#prompt = "A chibi style sticker of a cute, blonde-haired girl with black demon wings and black horns, wearing a white tunic dress. She has big blue eyes and a small red flower in her hair. She is drawn in a slightly arrogant and confident pose, with a slight smirk on her face. Her arms are crossed in front of her chest. Digital art, clean lines, high resolution, white background."
# prompt = """Transform the original chibi-style sticker into a dramatically altered fantasy artwork. 
# The blonde-haired girl now appears as a powerful dark sorceress with glowing blue eyes, 
# her black demon wings expanded to a grand scale and her horns twisted into elaborate shapes. 
# She wears a flowing, ornate black and gold robe instead of a simple tunic, 
# and the small red flower in her hair has become a fiery magical emblem. 
# The background is no longer plain white but a stormy, mystical landscape filled with lightning and swirling energy. 
# Her pose remains confident and arrogant, but her arms now channel dark magic, 
# casting a spell that radiates across the scene. 
# Digital art, highly detailed, high resolution, dramatic atmosphere."""
prompt = "クリスマスコスチュームを着た姿に変えてください。ポーズも大胆に変えて。表情は楽し気な感じ"

# 画像ファイルをImageFile型で取得
#base_image = PIL_image.open("tests/source_image/00109-2381410371.png")
base_image = PIL_image.open("tests/source_image/00015-3838046869.png")

try:
    # 画像生成を実行
    response = client.edit_image(
        prompt=prompt,
        model=GeminiClient.GeminiModel.GEMINI_2_5_FLASH_IMAGE,
        base_image=base_image,
        aspect_ratio=GeminiClient.AspectRatio.SQUARE,
        image_size=GeminiClient.ImageSize.ONE_K,
        harm_category = GeminiClient.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        safety_filter_level = GeminiClient.SafetyFilterLevel.BLOCK_ONLY_HIGH
    )
    
    # 画像ファイルを出力する
    for idx, image_bytes in enumerate(response["result"]):
        with open(f"image_{idx}.png", "wb") as f:
            f.write(image_bytes)
        print(f"Saved: image_{idx}.png")

    # 結果を表示する
    print("=== 使用モデル ===")
    print(response["model"])
    print("\n=== メタ情報 ===")
    print(response["metadata"])

except NoCandidatesError as e:
    print(f"Image generation failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
