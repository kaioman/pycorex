import pycorex.configs.app_init as app
from pycorex.gemini_client import GeminiClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# ImagenClientを初期化
client = GeminiClient(
    api_key=app.core.config.gemini.api_key_vertexai,
    project_id=app.core.config.vertexai.project_id,
    location=app.core.config.vertexai.location
)

# プロンプトを設定
#prompt = "ビキニ姿の日本人女性が就職活動をしている"
#prompt = "12月10日は「アロースタートの日」。1945年のこの日、日本で初めてアローインディアカ（羽根つきバレーボール）の講習会が開かれたことに由来します。"
#prompt = "Two elegant figures with sharp, sophisticated facial features and slender proportions dance amidst a torrential downpour on a sunset beach, their voluminous hair flowing in the gale and rendered with extremely delicate fine lines. Captured in the signature premium 1980s OVA aesthetic with high-contrast cel shading and shimmering iris highlights, they wear flowing ballroom gowns that twist like silk ribbons against the crashing, high waves. The atmosphere is thick with an urban city-pop color palette, where dramatic ray-traced sunset light illuminates their messy buns and an expression of haunting vulnerability, their slender forms trembling slightly with a delicate, wide-eyed trepidation as they embrace the overwhelming majesty of the storm. Dynamic wind trails spiral around them, merging the roar of the ocean with a sophisticated, cinematic intensity that eschews soft curves for sharp, detailed precision. (safe for work, no nudity, high quality art)"
prompt = "リクルートスーツの女性が居酒屋で酒をあおっている。少しブラジャーが見える"

try:
    # 画像生成を実行　
    response = client.generate_image(
        prompt=prompt,
        model=GeminiClient.GeminiModel.GEMINI_3_0_PRO_IMAGE_PREVIEW,
        aspect_ratio=GeminiClient.AspectRatio.SQUARE,
        image_size=GeminiClient.ImageSize.TWO_K,
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
