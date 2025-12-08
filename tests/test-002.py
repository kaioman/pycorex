import pycorex.configs.app_init as app

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# 設定クラスメンバ参照確認
print(app.core.config.prompt.json_path)
print(app.core.config.gemini.api_key)
