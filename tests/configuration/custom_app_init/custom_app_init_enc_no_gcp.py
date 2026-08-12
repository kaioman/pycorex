import libcore_hng.utils.app_core as app
from pycorex.configs.pycorex import PyCorexConfig

# アプリ初期化処理(import時に1度だけ実行される)
app.init_app(PyCorexConfig, __file__, "app_config.json", "comfyui_config.json", "pycorex.json.enc")
config = app.get_config(PyCorexConfig)