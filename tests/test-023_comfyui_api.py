import os
import json
import asyncio
import pycorex.configs.app_init as app
from pycorex.comfyui_client import ComfyUIClient
from pycorex.utils.pony_prompt_generator import PonyPromptGenerator
from pycorex.utils.workflow_editor import WorkflowEditor
from pycorex.utils.workflow_mod import WorkflowMod
from pycorex.enums.rating_level import RatingLevel

def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

async def main():

    # アプリ初期化
    app.init_app(
        __file__, 
        "app_config.json", 
        "gcp_config.json", 
        "pycorex.json.enc", 
        "comfyui_config.json"
    )

    # ワークフローパスを取得
    #comfyui_workflow_path = app.core.config.comfyui.workflow_path
    comfyui_workflow_path = "tests/comfyui_workflow/lotta-IPAdapter9_three_src_fd4.json"

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
        persona_conf=_load_json("tests/prompt/pony_realism/persona/Lotta.json"),
        camera_conf=_load_json("tests/prompt/pony_realism/camera_angules.json"),
        wardrobe_conf=_load_json("tests/prompt/pony_realism/wardrobe.json"),
        environment_conf=_load_json("tests/prompt/pony_realism/environments.json")
    )
    # PromptContextを生成
    prompt_context = pony_generator.generate_prompt(
        rating_level=RatingLevel.EMOTIVE,
        #test_outfit_id="denim_setup",
        #test_scene_id_override="lv3_phys_panty_pull_down",
        #test_camera_name="背面視点・バックビュー"
        #test_camera_name="ハイアングル・俯瞰"
    )

    # ワークフロー修正定義
    modification_list = WorkflowMod.create_modifications(
        prompt_context=prompt_context, 
        mod_config=_load_json("tests/comfyui_workflow/modifications/lotta_workflow_config.json"),
        batch_size=1
    )

    # WorkflowEditorを使用してワークフローに修正を適用
    workflow = WorkflowEditor.apply_modifications(workflow, modification_list)

    # ComfyUIクライアントを初期化する
    client = ComfyUIClient(
        base_url=comfyui_endpoint,
        timeout_seconds=timeout_seconds,
        polling_interval=polling_interval
    )

    try:
        # ワークフローを実行する
        result = await client.run_workflow(workflow_data=workflow, modifications=modification_list)
        
        # 生成された画像を保存する
        if result and result["result"]:
            for i, image_bytes in enumerate(result["result"]):
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

if __name__ == "__main__":
    asyncio.run(main())
