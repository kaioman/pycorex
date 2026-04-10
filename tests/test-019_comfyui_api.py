import json
import pycorex.configs.app_init as app

# アプリ初期化
app.init_app(__file__, "app_config.json", "pycorex.json.enc", "comfyui_config.json")

comfyui_workflow_path = app.core.config.comfyui.workflow_path

with open(comfyui_workflow_path, "r") as f:
    workflow = json.load(f)
    
print(workflow)

