import google.generativeai as genai
import vertexai
from enum import Enum
from datetime import datetime, timezone
from vertexai.vision_models import ImageGenerationModel
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
    
    class ImagenMode(Enum):
        """
        画像生成に利用可能なImagenモデルを表すEnumクラス
        
        各メンバーはGoogle Gen AI SDKにおける`client.models.generate_content()`の呼び出し時に指定するモデル名に対応
        
        また、旧SDK(Vertex AI SDK)における`ImageGenerationModel.from_pretrained(...)`で指定する
        モデル名としても利用する
        """
        
        IMAGEN_4_ULTRA = "imagen-4.0-ultra-generate-001"
        
    
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

        super().__init__(api_key, model)
        self._configuration_client()

    def _configuration_client(self):
        """
        APIクライアントの初期化処理
        """

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
    
    def generate_image(self, prompt: str, aspect_ratio:str, number_of_images:int = 1, include_row: bool = False) -> list[bytes]:
        
        # vertexai初期化
        vertexai.init(project="gen-lang-client-0452718754", location="us-east4")

        # モデル取得
        image_model = ImageGenerationModel.from_pretrained("imagen-4.0-ultra-generate-001")
        
        # 画像生成
        images = image_model.generate_images(
            prompt=prompt,
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio
        )
        
        # 画像データをbytesでlistに追加
        image_list = []
        for _, image in enumerate(images):
            image_list.append(image)
        
        # 結果を取得する
        result = {
            "type": "image",
            "model": "imagen-4.0-ultra-generate-001",
            "result": image_list,
            "metadata": {
                "prompt": prompt,
                "mode": "generate",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

        return result

    def generate_image_newsdk(self, prompt: str, aspect_ratio:str, number_of_images:int = 1) -> list[bytes]:
        """
        画像生成メソッド【試験用】
        
        新SDKに対応した画像生成メソッドだが、2025年12月現在は画像生成モデルのエンドポイントが利用できない
        """

        # 画像生成モデルを定義
        image_model = self.client.GenerativeModel("imagen-4.0-ultra")
        
        # 画像生成
        response = image_model.generate_content(
            contents=f"{prompt} (aspect ratio {aspect_ratio}, {number_of_images} images)"
        )
        
        # 画像データをbytesでlistに追加
        image_list = [img.data for img in response.images]
        
        # 結果を取得する
        result = {
            "type": "image",
            "model": "imagen-4.0-ultra",
            "result": image_list,
            "metadata": {
                "prompt": prompt,
                "mode": "generate",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

        return result