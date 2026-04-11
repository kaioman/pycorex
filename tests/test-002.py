import pycorex.configs.app_init as app

# アプリ初期化
app.init_app(__file__, "app_config.json", "gcp_config.json", "pycorex.json.enc")

# 設定クラスメンバ参照確認
print(app.core.config.prompt.json_path)
print(app.core.config.gemini.api_key)
