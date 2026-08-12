from custom_app_init.custom_app_init_enc_no_gcp import config

class TestSetupConfiguration:

    def test_reference_config_value(self):
        config.comfyui.workflow_path == "tests/comfyui_workflow/aoi-IPAdapter9a.json"
        config.gemini.api_key != ""

if __name__ == "__main__":
    testobj = TestSetupConfiguration()
    testobj.test_reference_config_value()
    