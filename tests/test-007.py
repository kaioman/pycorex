import pycorex.configs.app_init as app
from pycorex.gemini_client import GeminiClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# ImagenClientを初期化
client = GeminiClient(
    api_key=app.core.config.gemini.api_key_vertexai
)

# プロンプトを設定
prompt = "リクルートスーツの女性が就職活動をしている"
#prompt = "12月10日は「アロースタートの日」。1945年のこの日、日本で初めてアローインディアカ（羽根つきバレーボール）の講習会が開かれたことに由来します。"

try:
    # 画像生成を実行
    response = client.generate_image(
        prompt=prompt,
        model=GeminiClient.GeminiModel.GEMINI_3_0_PRO_IMAGE_PREVIEW,
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
