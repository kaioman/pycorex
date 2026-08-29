import os
import json
import asyncio
import pytest
from pathlib import Path
from pycorex.configs.initialize_app import config
from pycorex.comfyui_client import ComfyUIClient
from pycorex.utils.pony_prompt_generator import PonyPromptGenerator
from pycorex.utils.workflow_editor import WorkflowEditor
from pycorex.utils.workflow_mod import WorkflowMod
from pycorex.enums.rating_level import RatingLevel

class TestRequestComfyUI:
    """
    ComfyUIリクエストテスト

    実行コマンド例:
    pytest -sv .\\tests\\comfyui\\test_comfyui_api.py --persona-name=Lotta  
    """
    def test_request_comfyui_api(self, persona_name):
        asyncio.run(self.main(persona_name))
    
    def _load_json(self, relative_path):
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / relative_path
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def main(self, persona_name):

        # Comfyui API エンドポイントを取得
        comfyui_endpoint = config.comfyui.comfyui_endpoint
        # Comfyui API タイムアウト設定を取得
        timeout_seconds = config.comfyui.timeout_seconds
        # Comfyui API ポーリング設定を取得
        polling_interval = config.comfyui.polling_interval

        # PonyPromptGeneratorのインスタンスを作成
        pony_generator = PonyPromptGenerator(
            persona_conf=self._load_json(f"personas/{persona_name}/character_spec.json"),
        )
        # PromptContextを生成
        prompt_context = pony_generator.generate_prompt(
            rating_level=RatingLevel.QUESTIONABLE,
            test_outfit_id="recruit_suit",
            test_scene_id_override="lv3_phys_sitting_triangle_wet",
        )

        # ワークフロー取得
        workflow = pony_generator.workflow_data
        
        # ワークフロー修正定義
        modification_list = WorkflowMod.create_modifications(
            prompt_context=prompt_context, 
            mod_config=pony_generator.mod_config,
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
                for _, image_bytes in enumerate(result["result"]):
                    output_dir = "gen_images"
                    os.makedirs(output_dir, exist_ok=True)
                    image_path = os.path.join(output_dir, client.get_gen_filename())
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    print(f"Generated image saved to: {image_path}")
            else:
                pytest.fail("No images were generated.")

        except Exception as e:
            pytest.fail(f"ComfyUI execution failed: {e}")

if __name__ == "__main__":
    test_obj = TestRequestComfyUI()
    test_obj.test_request_comfyui_api("Lotta")
    test_obj.test_request_comfyui_api("Aoi")