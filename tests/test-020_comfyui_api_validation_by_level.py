import os
import json
import pycorex.configs.app_init as app
from pathlib import Path
from pycorex.comfyui_client import ComfyUIClient
from pycorex.utils.pony_prompt_generator import PonyPromptGenerator
from pycorex.utils.workflow_editor import WorkflowEditor
from pycorex.utils.workflow_mod import WorkflowMod
from pycorex.enums.rating_level import RatingLevel

def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _settings():

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

    # PonyPromptGeneratorのインスタンスを作成
    return (workflow, PonyPromptGenerator(
        persona_conf=_load_json("tests/prompt/pony/persona/Aoi.json"),
        camera_conf=_load_json("tests/prompt/pony/camera_angules.json"),
        wardrobe_conf=_load_json("tests/prompt/pony/wardrobe.json"),
        environment_conf=_load_json("tests/prompt/pony/environments.json")
    ))

def _gen_test(workflow, pony_generator: PonyPromptGenerator, level: RatingLevel, scene_id: str):

    # Comfyui API エンドポイントを取得
    comfyui_endpoint = app.core.config.comfyui.comfyui_endpoint
    # Comfyui API タイムアウト設定を取得
    timeout_seconds = app.core.config.comfyui.timeout_seconds
    # Comfyui API ポーリング設定を取得
    polling_interval = app.core.config.comfyui.polling_interval

    # PromptContextを生成
    prompt_context = pony_generator.generate_prompt(
        rating_level=level,
        target_scene_id=scene_id
    )

    # ワークフロー修正定義
    modification_list = WorkflowMod.create_modifications(
        prompt_context=prompt_context, 
        mod_config=_load_json("tests/comfyui_workflow/modifications/aoi_workflow_config.json"),
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
        response = client.run_workflow(workflow_data=workflow, modifications=modification_list)
        
        # 生成された画像を保存する
        if response and response["result"]:
            for i, image_bytes in enumerate(response["result"]):
                output_dir = Path("gen_images") / "validation_by_level" / scene_id
                os.makedirs(output_dir, exist_ok=True)
                image_path = os.path.join(output_dir, client.get_gen_filename())
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                print(f"Generated image saved to: {image_path}")
        else:
            print("No images were generated.") 

    except Exception as e:
        print(f"Error: {e}")

def _get_ids_by_level(target_json, level):
    items = target_json.get("scene_logic", {}).get("items", [])

    matched_ids = [
        item["id"] for item in items
        if item["min_lv"] <= level <= item["max_lv"]
    ]
    return matched_ids

def gen_main(level):
    persona_conf = _load_json("tests/prompt/pony/persona/Aoi.json")
    target_scene_ids = _get_ids_by_level(persona_conf, level)

    # 生成テスト
    for scene_id in target_scene_ids:
        for i in range(5):
            _gen_test(workflow, pony_generator, level, scene_id)

# ワークフローとPonyPromptGeneratorの設定を取得
workflow, pony_generator = _settings()

gen_main(RatingLevel.SAFE)
gen_main(RatingLevel.EMOTIVE)
gen_main(RatingLevel.QUESTIONABLE)
gen_main(RatingLevel.EXPLICIT)
