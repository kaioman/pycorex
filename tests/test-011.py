import pycorex.configs.app_init as app
from pycorex.gemini_client import GeminiClient
from pycorex.uwgen_client import UwgenClient

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# UwgenClientを初期化
client = UwgenClient()

# プロンプトを設定
prompt = "西暦2200年のイラストレーターになりきって、この画像の説明をしてください。口調は丁寧語。内容は毒舌。文字数はX(Twitter)の1ポスト(140文字以内)に収まるよう作成してください"

# 元画像取得
source_file_path = client.get_source_file_path("gen_images", "20260117_085628_0.png")

try:
    # 画像解析を実行
    result = client.analyze_image(
        prompt=prompt,
        source_image_path=source_file_path,
        model=GeminiClient.GeminiModel.GEMINI_3_0_PRO_IMAGE_PREVIEW.value
    )
    
    # 解析結果を出力
    print(result["text"])

except Exception as e:
    print(f"Unexpected error: {e}")
