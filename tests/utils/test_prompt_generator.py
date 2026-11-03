import pytest
from pycorex.enums.rating_level import RatingLevel
from pycorex.utils.pony_prompt_generator import PonyPromptGenerator

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

@pytest.fixture
def silence_prompt_logger(monkeypatch):
    monkeypatch.setattr(
        "pycorex.utils.pony_prompt_generator.app_logger.info",
        lambda *_args, **_kwargs: None,
    )

def make_generator(identity_tags=None):
    generator = PonyPromptGenerator.__new__(PonyPromptGenerator)
    generator.persona_data = {
        "rating": {"safe": "rating_safe"},
        "base_score_tags": "score",
        "base_style": "style",
        "innerwear_thresholds": {"1": 0},
        "negative_holy_grail": "",
        "negative_base": "",
        "negative_logic": {"items": []},
    }
    if identity_tags is not None:
        generator.persona_data["face_detailer_identity_tags"] = identity_tags

    generator.wardrobe_data = {
        "outfits": [{
            "id": "outfit",
            "tags": {
                "top": "clothes",
                "bottom": "",
                "accessories": "",
                "quality": "",
            },
            "outer_tags": {"top": "top", "bottom": "bottom"},
        }],
        "innerwear_sets": {"styles": []},
    }
    generator.scene_data = {
        "scene_logic": [{
            "id": "scene",
            "tags": "portrait",
            "inner_inclusion": {},
            "camera_angle_exclude": [],
        }],
    }
    generator.camera_data = {
        "camera_angles": [{
            "id": "camera",
            "name": "camera",
            "tags": "portrait",
        }],
    }
    generator.expression_data = {
        "expressions": [{"name": "neutral", "tags": "smile"}],
    }

    generator._get_base_identity = lambda: {
        "base_identity_tags": "core_only",
    }
    generator._pick_weighted_item = lambda items, current_level, target_id=None: items[0]
    generator._get_environment_tags = lambda scene_tags, outfit_id: ""

    return generator

@pytest.mark.parametrize("identity_tags", [None, "", "   "])
def test_face_detailer_prompt_omits_empty_identity_and_core(identity_tags, silence_prompt_logger):
    generator = make_generator(identity_tags)

    prompt = generator.generate_prompt(
        rating_level=RatingLevel.SAFE,
        test_outfit_id="outfit",
    ).face_detailer_positive_prompt

    assert prompt == "score, rating_safe, style, smile"
    assert "core_only" not in prompt

def test_face_detailer_prompt_includes_dedicated_identity(silence_prompt_logger):
    generator = make_generator("Aoi, blue eyes")

    prompt = generator.generate_prompt(
        rating_level=RatingLevel.SAFE,
        test_outfit_id="outfit",
    ).face_detailer_positive_prompt

    assert prompt == "score, rating_safe, style, Aoi, blue eyes, smile"
    assert "core_only" not in prompt
