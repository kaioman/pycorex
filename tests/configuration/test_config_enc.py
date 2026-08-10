from custom_app_init.custom_app_init_enc import config

class TestSetupConfiguration:

    def test_reference_config_value(self):
        config.comfyui.workflow_path == "tests/comfyui_workflow/aoi-IPAdapter9a.json"
        config.gemini.api_key != ""