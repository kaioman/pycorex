import pycorex.configs.app_init as app
import unittest
from google.genai.types import Content, Part
from pycorex.gemini_client import GeminiClient

class TestGeminiChat(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # アプリ初期化
        app.init_app(__file__, "app_config.json", "gcp_config.json", "pycorex.json.enc")

        # GeminiClientを初期化
        cls.client = GeminiClient(
            api_key=app.core.config.gemini.api_key,
        )

    def test_start_chat_session_success(self):

        system_inst = "あなたは丁寧な執事です"
        session = self.client.start_chat_session(
                model=GeminiClient.GeminiModel.GEMINI_2_5_FLASH, 
                system_instruction=system_inst
        )

        # セッションオブジェクトの確認
        self.assertIsNotNone(session)

        # 最初のメッセージ送信テスト
        response = session.send_message("こんにちは、今日の天気は？")
        self.assertIsNotNone(response.text)
        print(f"\n[Response 1]: {response.text}")

    def test_chat_history_consistency(self):

        # 履歴を模倣する
        history=[
            Content(
                role="user",
                parts=[Part(text="今日の天気は雨です")]
            ),
            Content(
                role="model",
                parts=[Part(text="ここのところ、雨が続きますね")]
            )
        ]

        # セッション開始 
        session = self.client.start_chat_session(
            model=GeminiClient.GeminiModel.GEMINI_2_5_FLASH,
            history=history,
            system_instruction="あなたは丁寧な執事です"
        )

        # 履歴に基づいた質問
        response = session.send_message("今日の天気は何でしたっけ？")

        # 応答を出力する
        print(f"{response.text}")

if __name__ == "__main__":
    unittest.main()
    