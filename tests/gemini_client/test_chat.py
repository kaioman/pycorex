import pytest
from google.genai.types import Content, Part
from pycorex.configs.initialize_app import config
from pycorex.gemini_client import GeminiClient

class TestGeminiChat:

    @pytest.fixture(autouse=True)
    def setup(self):

        # GeminiClientを初期化
        self.client = GeminiClient(
            api_key=config.gemini.api_key,
        )

    def test_start_chat_session_success(self):

        system_inst = "あなたは丁寧な執事です"
        session = self.client.start_chat_session(
                model=GeminiClient.GeminiModel.GEMINI_2_5_FLASH, 
                system_instruction=system_inst
        )

        # セッションオブジェクトの確認
        assert session is not None

        # 最初のメッセージ送信テスト
        response = session.send_message("こんにちは、今日の天気は？")
        print(f"{response.text}")
        assert response.text is not None

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

        # 検証
        assert response.text is not None, "レスポンステキストが空です"
        assert "雨" in response.text, f"回答に'雨'が含まれていません"

        current_history = session.get_history()
        assert len(current_history) == 4, f"履歴の件数が不整合です: {len(current_history)}"

        assert current_history[-2].role == "user"
        assert "今日の天気は何でしたっけ？" in current_history[-2].parts[0].text
        assert current_history[-1].role == "model"

if __name__ == "__main__":
    pytest.main(["-s", "-v", __file__])