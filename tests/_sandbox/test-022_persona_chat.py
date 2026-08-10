import pycorex.configs.app_init as app
import json
import unittest
from google.genai.types import Content, Part
from pycorex.gemini_client import GeminiClient

class TestPersonaChat(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # アプリ初期化
        app.init_app(__file__, "app_config.json", "gcp_config.json", "pycorex.json.enc")

        # GeminiClientを初期化
        cls.client = GeminiClient(
            api_key=app.core.config.gemini.api_key,
        )

        # 設定ファイルのパスをセット
        cls.instruction_path = "tests/prompt/chat/instruction.json"
        cls.persona_path = "tests/prompt/chat/Aoi.json"
    
    def _build_instruction(self):
        with open(self.instruction_path, "r", encoding="utf-8") as f:
            inst_data = json.load(f)
        with open(self.persona_path, "r", encoding="utf-8") as f:
            persona_data = json.load(f)

        template = "\n".join(inst_data["meta_instruction"]["template_lines"])

        persona_str = json.dumps(persona_data, ensure_ascii=False, indent=2)
        full_instruction = template.format(persona_json=persona_str)
        return full_instruction
    
    def test_aoi_persona_behavior(self):
        
        # instructionのbuild
        system_inst = self._build_instruction()

        # セッション開始
        session = self.client.start_chat_session(
            model=GeminiClient.GeminiModel.GEMINI_2_5_FLASH, 
            system_instruction=system_inst
        )

        # 最初の問いかけ
        response1 = session.send_message("自己紹介をお願いします")
        print(f"\n[Aoi's Instroduction]:\n{response1.text}")

        # Aoiという名前が含まれているかチェック
        self.assertIn("Aoi", response1.text)

        # 会話の継続
        response2 = session.send_message("AIに仕事を奪われるという意見に反論可能でしょうか？")
        print(f"\n[Aoi's Second Response]:\n{response2.text}")

        # 文脈に沿った回答かチェック
        self.assertIsNotNone(response2.text)

if __name__ == "__main__":
    unittest.main()
    