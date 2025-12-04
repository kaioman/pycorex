from enum import Enum
from datetime import datetime, timezone
from pycorex.core.base_ai_client import BaseAIClient

class GeminiClient(BaseAIClient):
    
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
            model
        """

        super().__init__(api_key, model)
        self._configuration_client()

    def _configuration_client(self):
        """
        APIクライアントの初期化処理
        """

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.client = genai
    
    def calc_tokens(self, prompt, response_text):
        """
        プロンプトと応答テキストのトークン数を計算する
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
    
    def generate_text(self, prompt: str, language = BaseAIClient.AILang.jp, include_row: bool = False):
        
        full_prompt = f"Respond in {language.value}. {prompt}"
        response = self.client.GenerativeModel(self.model.value).generate_content(full_prompt)
        
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