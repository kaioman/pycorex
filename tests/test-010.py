import pycorex.configs.app_init as app
from pycorex.gemini_client import GeminiClient

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# GeminiClientを初期化
client = GeminiClient(
    api_key=app.core.config.gemini.api_key
)

# プロンプトを設定
prompt = "西暦2200年のイラストレーターになりきって、この画像の説明をしてください。口調は丁寧語。内容は毒舌。文字数はX(Twitter)の1ポスト(140文字以内)に収まるよう作成してください"

# 画像ファイルをbyte型で取得
with open("tests/source_image/00015-3838046869.png", "rb") as f:
    base_image = f.read()

# 画像解析を実行
response = client.analyze_image(
    base_image=base_image,
    prompt=prompt,
    model=GeminiClient.GeminiModel.GEMINI_3_0_FLASH_PREVIEW,
    max_output_tokens=2048
)

# 結果を表示する
print("\n=== 生成結果 ===")
print(response["result"])
