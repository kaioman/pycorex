import pycorex.configs.app_init as app
from pycorex.gemini_client import GeminiClient
from pycorex.uwgen_client import UwgenClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# UwgenClientを初期化
client = UwgenClient()

# プロンプトを設定
prompt = "悪がらみした様子にする"

# 元画像取得
source_file_path = client.get_source_file_path("gen_images", "20260117_085628_0.png")

try:
    # 画像生成を実行
    result = client.edit_image(
        prompt=prompt,
        source_image_path=source_file_path,
        model=GeminiClient.GeminiModel.GEMINI_3_0_PRO_IMAGE_PREVIEW.value,
        resolution=GeminiClient.ImageSize.TWO_K.value,
        aspect=GeminiClient.AspectRatio.SQUARE.value,
        safety_filter = GeminiClient.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT.value,
        safety_level = GeminiClient.SafetyFilterLevel.BLOCK_ONLY_HIGH.value
    )
    
    # 画像ファイルを出力する
    client.output_images(result["images"], "gen_images")

except NoCandidatesError as e:
    print(f"Image generation failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
