import os
import json
import pycorex.configs.app_init as app
from pycorex.comfyui_client import ComfyUIClient
from pycorex.utils.pony_prompt_generator import PonyPromptGenerator

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
# Comfyui API タイムアウト設定を取得
timeout_seconds = app.core.config.comfyui.timeout_seconds
# Comfyui API ポーリング設定を取得
polling_interval = app.core.config.comfyui.polling_interval

# PonyPromptGeneratorのインスタンスを作成
pony_generator = PonyPromptGenerator(
    aoi_path="tests/prompt/pony/persona/Aoi.json",
    camera_path="tests/prompt/pony/camera_angules.json",
    wardrobe_path="tests/prompt/pony/wardrobe.json",
    environment_path="tests/prompt/pony/environments.json"
)

# ComfyUIクライアントを初期化する
client = ComfyUIClient(
    base_url=comfyui_endpoint,
    prompt_generator=pony_generator,
    timeout_seconds=timeout_seconds,
    polling_interval=polling_interval
)

try:
    result = client.generate_image(
        workflow_data=workflow, 
        prompt_level=3,
        test_outfit_id="turtleneck",
        test_scene_id_override="lv3_phys_deep_squat",
        #test_camera_name="背面視点・バックビュー"
    )
    
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