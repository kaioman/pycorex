import google.generativeai as genai
import libcore_hng.utils.app_logger as app_logger
from google import genai as image_genai
from google.genai.types import GenerateContentConfig, Modality, ImageConfig
from enum import Enum
from datetime import datetime, timezone
from pycorex.core.base_ai_client import BaseAIClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

class GeminiClient(BaseAIClient):
    """
    Google Gemini API を利用してテキスト生成を行うクライアントクラス。

    Attributes
    ----------
    api_key : str
        Gemini API の認証キー
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
        GEMINI_2_5_FLASH_IMAGE = "gemini-2.5-flash-image"
        """ 画像編集可能なGeminiモデル(edit_imageで指定可能な唯一のモデル) """
        GEMINI_2_0_FLASH = "gemini-2.0-flash"
        """ GEMINI_2_0_FLASH: 第2世代 Flash モデル。最大100万トークンのコンテキストに対応 """
        GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
        """ GEMINI_2_0_FLASH_LITE: 第2世代 Flash の軽量版。高速処理に特化 """
        GEMINI_ULTRA = "gemini-ultra"
        """ GEMINI_ULTRA: 最上位モデル。有料プラン限定で利用可能 """
        GEMINI_PRO_VISION = "gemini-pro-vision"
        """ GEMINI_PRO_VISION: マルチモーダル対応モデル。テキスト＋画像入力を処理可能 """
        GEMINI_3_0_PRO_IMAGE_PREVIEW = "gemini-3-pro-image-preview"
        """ GEMINI_3_0_PRO_IMAGE_PREVIEW: Gemini 3 Pro Image (Nano Banana Pro) プレビュー版 """
        
        def __str__(self):
            """
            モデルの文字列値を返す

            使用例:
                str(GeminiModel.GEMINI_PRO_VISION) -> "gemini-pro-vision"
            """
            return self.value
    
    class ImageSize(Enum):
        """
        Gemini API などで画像生成時に利用する解像度指定を表す Enum クラス。

        この Enum は、画像生成・編集の際に出力サイズを指定するための定数を定義する
        各値は文字列として API に渡され、生成される画像の解像度を決定する
        """

        ONE_K = "1K"
        """ "1K" 解像度。標準的なサイズで軽量な出力に適する """

        TWO_K = "2K"
        """ "2K" 解像度。より高精細な出力が必要な場合に利用 """

        FOUR_K = "4K"
        """ "4K" 解像度。非常に高解像度の出力を生成する場合に利用 """
        
    def __init__(self, api_key: str):
        """
        コンストラクタ

        Parameters
        ----------
        api_key : str
            APIキー
        """

        # APIキー
        self.api_key = api_key

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
        
        # APIクライアント(テキスト)をセット
        self.text_client = genai
        # APIクライアント(画像)をセット        
        self.image_client = image_genai.Client(vertexai=True, api_key=self.api_key)
        
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
    
    def generate_text(self, 
        prompt: str, 
        model: GeminiModel,
        language = BaseAIClient.AILang.JP, 
        include_row: bool = False) -> dict:
        """
        指定したプロンプトに基づいてテキストを生成する

        Parameters
        ----------
        prompt : str
            入力プロンプト
        model : GeminiModel
            model(テキスト生成時のモデルを指定)
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
        response = self.text_client.GenerativeModel(model.value).generate_content(full_prompt)

        # 結果を取得する
        result = {
            "type": "text",
            "model": model.value,
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
    
    def generate_image(self, 
        prompt: str, 
        model: GeminiModel,
        aspect_ratio:BaseAIClient.AspectRatio = BaseAIClient.AspectRatio.SQUARE,
        image_size = ImageSize.ONE_K,
        number_of_images:int = 1, 
        harm_category = BaseAIClient.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        safety_filter_level = BaseAIClient.SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
        include_row: bool = False) -> dict:
        """
        画像生成メソッド【試験用】
        
        新SDKに対応した画像生成メソッドだが、2025年12月現在は画像生成モデルのエンドポイントが利用できない
        """

        # 画像生成リクエスト
        app_logger.info(f"Image generation request sent. Model={model.value}, Prompt={prompt}, CandidateCount={number_of_images}")
        response = self.image_client.models.generate_content(
            model = model.value,
            contents = [prompt],
            config = GenerateContentConfig(
                response_modalities = [Modality.IMAGE],
                candidate_count = number_of_images,                
                safety_settings = [
                    {"category": harm_category.value},
                    {"threshold": safety_filter_level.value.upper()},
                ],
                image_config = ImageConfig(
                    aspect_ratio = aspect_ratio.value,
                    image_size = image_size.value,
                )
            )
        )
        
        # 画像生成結果チェック
        if not response.candidates:
            raise NoCandidatesError("No candidates returned. Possibly blocked by safety filters.")
        
        # 生成画像をbytesでlist化して返す
        image_list: list[bytes] = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    image_list.append(part.inline_data.data)
                    app_logger.info(f"Image candidate received. Size={len(part.inline_data.data)} bytes")
                elif part.text:
                    app_logger.warning(f"Text explanation returned instead of image: {part.text}")
        
        # 結果を取得する
        result = {
            "type": "image",
            "model": model.value,
            "result": image_list,
            "metadata": {
                "prompt": prompt,
                "mode": "generate",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        if include_row:
            result["raw_response"] = []
            for idx, image in enumerate(image_list):
                row_info = {
                    "index": idx,
                    "size_bytes": len(image) if isinstance(image, bytes) else None,
                    "mime_type": self.guess_mime_type(image),
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": model.value
                }
                result["raw_response"].append(row_info)
        app_logger.info(f"Image generation completed. Total images={len(image_list)}")
        return result
    
    def edit_image(self, 
        base_image,
        prompt: str, 
        model: GeminiModel,
        aspect_ratio:BaseAIClient.AspectRatio = BaseAIClient.AspectRatio.SQUARE,
        image_size = ImageSize.ONE_K,
        number_of_images:int = 1, 
        harm_category = BaseAIClient.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        safety_filter_level = BaseAIClient.SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
        include_row: bool = False) -> dict:
        """
        元画像を指定して変化させる画像生成メソッド

        Parameters
        ----------
        base_image : bytes
            編集対象となる元画像データ
        prompt : str
            変化の内容を説明するプロンプト
        model: GeminiModel
            画像生成で使用するモデル
        aspect_ratio : AspectRatio, optional
            出力画像のアスペクト比 (例: "1:1", "16:9")
            default="1:1"
        image_size : ImageSize, optional
            画像サイズ(1K,2K,4K)
            default=1K
        number_of_images : int, optional
            生成する画像の枚数
            default=1
        harm_category : HarmCategory
            評価のカテゴリ
            default="HARM_CATEGORY_DANGEROUS_CONTENT"
        safety_filter_level : SafetyFilterLevel, optional
            安全フィルタリングのフィルタレベル
            default="block_medium_and_above"

        Returns
        -------
        dict
            生成結果を含む辞書
        """

        # 画像編集リクエスト
        app_logger.info(f"Image generation request sent. Model={model.value}, Prompt={prompt}, CandidateCount={number_of_images}")
        response = self.image_client.models.generate_content(
            model = model.value,
            contents = [base_image, prompt],
            config = GenerateContentConfig(
                response_modalities = [Modality.TEXT, Modality.IMAGE],
                candidate_count = number_of_images,                
                safety_settings = [
                    {"category": harm_category.value},
                    {"threshold": safety_filter_level.value.upper()},
                ],
                image_config = ImageConfig(
                    aspect_ratio = aspect_ratio.value,
                    image_size = image_size.value,
                )
            )
        )
        
        # 画像生成結果チェック
        if not response.candidates:
            raise NoCandidatesError("No candidates returned. Possibly blocked by safety filters.")
        
        # 生成画像をbytesでlist化して返す
        image_list: list[bytes] = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    image_list.append(part.inline_data.data)
                    app_logger.info(f"Image candidate received. Size={len(part.inline_data.data)} bytes")
                elif part.text:
                    app_logger.warning(f"Text explanation returned instead of image: {part.text}")

        # 結果を取得する
        result = {
            "type": "image",
            "model": model.value,
            "result": image_list,
            "metadata": {
                "prompt": prompt,
                "mode": "edit",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        if include_row:
            result["raw_response"] = []
            for idx, image in enumerate(image_list):
                row_info = {
                    "index": idx,
                    "size_bytes": len(image) if isinstance(image, bytes) else None,
                    "mime_type": self.guess_mime_type(image),
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": model.value
                }
                result["raw_response"].append(row_info)
        app_logger.info(f"Image editing completed. Total images={len(image_list)}")
        return result
