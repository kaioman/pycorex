import os
import json
import pycorex.configs.app_init as app
from pycorex.comfyui_client import ComfyUIClient

# アプリ初期化
app.init_app(
    __file__, 
    "app_config.json", 
    "gcp_config.json", 
    "pycorex.json.enc", 
    "comfyui_config.json"
)

# ワークフローパスを取得
comfyui_workflow_path = app.core.config.comfyui.workflow_path
# ワークフローを読み込む
with open(comfyui_workflow_path, "r") as f:
    workflow = json.load(f)

# Comfyui API エンドポイントを取得
comfyui_endpoint = app.core.config.comfyui.comfyui_endpoint

# ComfyUIクライアントを初期化する
client = ComfyUIClient(base_url=comfyui_endpoint)

try:
    result = client.generate_image(workflow_data=workflow)
    
    if result and result["images"]:
        for i, image_bytes in enumerate(result["images"]):
            output_dir = "gen_images"
            os.makedirs(output_dir, exist_ok=True)
            image_path = os.path.join(output_dir, client.get_gen_filename())
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            print(f"Generated image saved to: {image_path}")
    else:
        print("No images were generated.") 

except Exception as e:
    print(f"Error: {e}")