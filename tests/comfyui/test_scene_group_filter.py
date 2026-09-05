import json
from pathlib import Path
from pycorex.configs.initialize_app import config 
from pycorex.utils.pony_prompt_generator import PonyPromptGenerator
from pycorex.enums.rating_level import RatingLevel

class TestSceneGroupFilter:
    """
    SceneGroupFilterテスト
    
    実行コマンド例:
    pytest -sv .\\tests\\comfyui\\test_comfyui_api.py --persona-name=Lotta  
    """

    def _load_json(self, relative_path):
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / relative_path
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_oversized_hoodie_excludes_bottom_exposure_scene(self, persona_name):
            """
            outfitのincompatible_scene_groupsに含まれるscene_groupを持つscene_logicを除外する        
            """
    
            # PonyPromptGeneratorのインスタンスを作成
            pony_generator = PonyPromptGenerator(
                persona_conf=self._load_json(f"personas/{persona_name}/character_spec.json"),
            )
    
            # PromptContextを生成
            prompt_context = pony_generator.generate_prompt(
                rating_level=RatingLevel.QUESTIONABLE,
                test_outfit_id="oversized_hoodie",
                test_scene_id_override="lv3_phys_sitting_triangle_stable",
            )

            # scene_idが指定したscene_id_overrideと異なることを確認
            assert prompt_context.scene_id != "lv3_phys_sitting_triangle_stable"

            # scene_logicから指定したscene_id_overrideを持つsceneを取得
            selected_scene = next(
                item
                for item in pony_generator.scene_data["scene_logic"]
                if item["id"] == prompt_context.scene_id
            )

            # selected_sceneのscene_groupsに"bottom_exposure"が含まれていないことを確認
            assert "bottom_exposure" not in selected_scene.get("scene_groups", [])

            # outfitのincompatible_scene_groupsに含まれるscene_groupを持つscene_logicを除外する
            outfit = next(
                 item
                 for item in pony_generator.wardrobe_data["outfits"]
                 if item["id"] == "oversized_hoodie"
            )

            # incompatible_scene_groupsを取得
            excluded_groups = set(outfit.get("incompatible_scene_groups", []))

            # scene_logicからincompatible_scene_groupsに含まれるscene_groupを持つsceneを除外する
            filtered_scene_logic = [
                scene["id"]
                for scene in pony_generator.scene_data["scene_logic"]
                if not excluded_groups.intersection(scene.get("scene_groups", []))
            ]

            # filtered_scene_logicに"lv3_phys_sitting_triangle_stable"が含まれていないことを確認
            assert "lv3_phys_sitting_triangle_stable" not in filtered_scene_logic