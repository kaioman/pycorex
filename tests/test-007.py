import pycorex.configs.app_init as app
from pycorex.imagen_client import ImagenClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# ImagenClientを初期化
client = ImagenClient(
    project_id=app.core.config.vertexai.project_id,
    location=app.core.config.vertexai.location
)

# プロンプトを設定
#prompt = "Youtuberが緊急で動画を撮っているが、どうみても緊急でもなければ大したことがない件"
prompt = "複数の女の子が踊っている"

try:
    # 画像生成を実行
    response = client.generate_image(
        prompt=prompt,
        model=ImagenClient.GeminiModel.GEMINI_25_FLASH_IMAGE,
        aspect_ratio=ImagenClient.AspectRatio.SQUARE,
        image_size=ImagenClient.ImageSize.ONE_K,
        harm_category = ImagenClient.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        safety_filter_level = ImagenClient.SafetyFilterLevel.BLOCK_ONLY_HIGH
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
