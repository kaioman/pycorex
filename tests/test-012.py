import pycorex.configs.app_init as app
from pycorex.gemini_client import GeminiClient
from pycorex.uwgen_client import UwgenClient

# アプリ初期化
app.init_app(__file__, "app_config.json", "pycorex.json.enc")

# UwgenClientを初期化
client = UwgenClient()

# プロンプトを設定
prompt = "ノブレス・オブ・リージュについて教えてください"

try:
    # 画像解析を実行
    result = client.generate_text(
        prompt=prompt,
        model=GeminiClient.GeminiModel.GEMINI_2_5_FLASH_LITE.value
    )
    
    # 解析結果を出力
    print(result["text"])

except Exception as e:
    print(f"Unexpected error: {e}")
