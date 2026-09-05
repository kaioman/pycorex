
class TestPonyPromptGenerator:
    """
    PonyPromptGeneratorテスト
    """

    def test_outfit_excludes_scene_group(self):
        """
        outfitのincompatible_scene_groupsに含まれるscene_groupを持つscene_logicを除外する
        """
        scene_data = {
            "scene_logic": [
                {
                    "id": "safe_scene",
                    "scene_groups": ["normal"],
                    "min_lv": 1,
                    "max_lv": 5,
                    "weight": 1.0,
                },
                {
                    "id": "exposure_scene",
                    "scene_groups": ["bottom_exposure"],
                    "min_lv": 1,
                    "max_lv": 5,
                    "weight": 1.0,
                },
            ],
        }

        outfit = {
            "id": "pants_outfit",
            "incompatible_scene_groups": ["bottom_exposure"],
        }

        filtered = [
            item
            for item in scene_data["scene_logic"]
            if not set(outfit["incompatible_scene_groups"]).intersection(
                item.get("scene_groups", [])
            )
        ]

        assert [item["id"] for item in filtered] == ["safe_scene"]
