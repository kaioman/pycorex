import google.generativeai as genai
from enum import Enum
from datetime import datetime, timezone
from pycorex.core.base_ai_client import BaseAIClient

class GeminiClient(BaseAIClient):
    """
    Google Gemini API を利用してテキスト生成を行うクライアントクラス。

    Attributes
    ----------
    api_key : str
        Gemini API の認証キー
    model : GeminiModel
        使用する Gemini モデル
    client : google.generativeai
        初期化済みの Gemini API クライアント
    """

    class GeminiModel(Enum):
        """
        Google Gemini で利用可能なモデルを表す Enum クラス

        各メンバーは Gemini API に渡すモデル名の文字列を保持
        """

        GEMINI_3_PRO = "gemini-3-pro"
        """ GEMINI_3_PRO: 最新世代の高性能モデル。高度な推論やマルチモーダル処理に対応 """
        GEMINI_2_5_PRO = "gemini-2.5-pro"
        """ GEMINI_2_5_PRO: コード、数学、STEM 分野に強く、長いコンテキストを扱える """
        GEMINI_2_5_FLASH = "gemini-2.5-flash"
        """ GEMINI_2_5_FLASH: 高速・低レイテンシでリアルタイム用途に適したモデル """
        GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"
        """ GEMINI_2_5_FLASH_LITE: 軽量でコスト効率が高い。簡易タスクや大量リクエスト処理に向く """
        GEMINI_2_0_FLASH = "gemini-2.0-flash"
        """ GEMINI_2_0_FLASH: 第2世代 Flash モデル。最大100万トークンのコンテキストに対応 """
        GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
        """ GEMINI_2_0_FLASH_LITE: 第2世代 Flash の軽量版。高速処理に特化 """
        GEMINI_ULTRA = "gemini-ultra"
        """ GEMINI_ULTRA: 最上位モデル。有料プラン限定で利用可能 """
        GEMINI_PRO_VISION = "gemini-pro-vision"
        """ GEMINI_PRO_VISION: マルチモーダル対応モデル。テキスト＋画像入力を処理可能 """

        def __str__(self):
            """
            モデルの文字列値を返す

            使用例:
                str(GeminiModel.GEMINI_PRO_VISION) -> "gemini-pro-vision"
            """
            return self.value
    
    def __init__(self, api_key: str, model: GeminiModel):
        """
        コンストラクタ

        Parameters
        ----------
        api_key : str
            APIキー
        model : GeminiModel
            model(テキスト生成時のモデルを指定)
        """

        # APIキー
        self.api_key = api_key

        # モデル情報
        self.model = model

        # APIクライアントの初期化処理
        self._configuration_client()

    def set_authentication(self, api_key: str):
        """
        認証情報を再設定する

        Parameters
        ----------
        api_key : str
            APIキー
        """
        
        # APIキー再設定
        self.api_key = api_key
        
        # APIクライアント初期化
        self._configuration_client()
        
    def _configuration_client(self):
        """
        APIクライアントの初期化処理
        """

        # APIクライアントにAPIキーを設定する
        genai.configure(api_key=self.api_key)
        
        # APIクライアント(genai)をセット
        self.client = genai

    def calc_tokens(self, prompt, response_text) -> dict:
        """
        プロンプトと応答テキストのトークン数を計算する
        
        Parameters
        ----------
        prompt : str
            入力プロンプト
        response_text : str
            モデルからの応答テキスト

        Returns
        -------
        dict
            {
                "prompt_tokens": int,
                "response_tokens": int,
                "total_tokens": int
            }
            失敗時は {"error": str} を返す
        """

        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            
            prompt_tokens = len(enc.encode(prompt))
            response_tokens = len(enc.encode(response_text))
            total_tokens = prompt_tokens + response_tokens
            
            return {
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
                "total_tokens": total_tokens
            }
        except Exception as e:
            return {"error": f"Token calculation failed: {e}"}
    
    def generate_text(self, prompt: str, language = BaseAIClient.AILang.JP, include_row: bool = False) -> dict:
        """
        指定したプロンプトに基づいてテキストを生成する

        Parameters
        ----------
        prompt : str
            入力プロンプト
        language : BaseAIClient.AILang, optional
            応答言語の指定（デフォルト: 日本語）
        include_row : bool, optional
            True の場合、生レスポンス情報を追加する

        Returns
        -------
        dict
            {
                "type": "text",
                "model": str,
                "result": str,
                "metadata": {
                    "prompt": str,
                    "language": str,
                    "mode": "generate",
                    "timestamp": str,
                    "usage": Any,
                    "token_count": dict
                },
                "raw_response": dict (include_row=True の場合のみ)
            }
        """

        # プロンプト
        full_prompt = f"Respond in {language.value}. {prompt}"
        # テキスト生成
        response = self.client.GenerativeModel(self.model.value).generate_content(full_prompt)

        # 結果を取得する
        result = {
            "type": "text",
            "model": self.model.value,
            "result": response.text,
            "metadata": {
                "prompt": prompt,
                "language": language.value,
                "mode": "generate",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "usage": getattr(response, "usage", None)
            }
        }
        if include_row:
            result["raw_response"] = {
                "id": getattr(response, "id", None),
                "model": getattr(response, "model", None),
                "usage": getattr(response, "usage", None),
                "content": response.text
            }
        
        # トークン数を計算して追加する
        result["metadata"]["token_count"] = self.calc_tokens(prompt, response.text)
        
        return result
    