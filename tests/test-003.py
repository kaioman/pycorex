import pycorex.configs.app_init as app
from pycorex.gemini_client import GeminiClient

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# 設定クラスメンバ参照確認
print(app.core.config.prompt.json_path)
print(app.core.config.gemini.api_key)

# GeminiClientを初期化
client = GeminiClient(
    api_key=app.core.config.gemini.api_key, 
    model=GeminiClient.GeminiModel.GEMINI_2_5_FLASH_LITE)

# プロンプトを設定
prompt = "相対性理論と特殊相対性理論について簡潔に説明してください"

# テキスト生成を実行
response = client.generate_text(
    prompt=prompt,
    language=GeminiClient.AILang.JP
)

# 結果を表示する
print("=== 使用モデル ===")
print(response["model"])
print("\n=== 生成結果 ===")
print(response["result"])
print("\n=== メタ情報 ===")
print(response["metadata"])
