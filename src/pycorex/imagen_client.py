import vertexai
#import imghdr
import libcore_hng.utils.app_logger as app_logger
from enum import Enum
from datetime import datetime, timezone
from google import genai
from vertexai.preview.vision_models import ImageGenerationModel
#from google.genai.types import GenerateContentConfig, Modality, ImageConfig
from pycorex.core.base_ai_client import BaseAIClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

class ImagenClient(BaseAIClient):
    """
    Google Vertex AI / Gen AI SDK を利用して画像生成を行うクライアントクラス

    Attributes
    ----------
    project_id : str
        利用するGoogle CloudプロジェクトのID
    location : str
        Vertex AIのリージョン
    """

    class ImagenModel(Enum):
        """
        画像生成に利用可能なImagenモデルを表すEnumクラス
        
        各メンバーはGoogle Gen AI SDKにおける`client.models.generate_content()`の呼び出し時に指定するモデル名に対応
        
        また、旧SDK(Vertex AI SDK)における`ImageGenerationModel.from_pretrained(...)`で指定する
        モデル名としても利用する
        """
        
        IMAGEN_4_GENERATE = "imagen-4.0-generate-001"
        """ 標準的な品質で画像生成を行うモデル """

        IMAGEN_4_FAST_GENERATE = "imagen-4.0-fast-generate-001"
        """ 高速生成用モデル（品質より速度を優先） """

        IMAGEN_4_ULTRA = "imagen-4.0-ultra-generate-001"
        """ 最高品質の画像生成を行うモデル """

        IMAGEN_3_GENERATE_002 = "imagen-3.0-generate-002"
        """ Imagen v3 系列の標準モデル（改良版） """

        IMAGEN_3_GENERATE_001 = "imagen-3.0-generate-001"
        """ Imagen v3 系列の初期モデル """

        IMAGEN_3_FAST_GENERATE = "imagen-3.0-fast-generate-001"
        """ Imagen v3 系列の高速生成モデル """

        IMAGEN_3_CAPABILITY = "imagen-3.0-capability-001"
        """ 特殊機能を持つImagen v3 系列モデル """

        def __str__(self):
            """
            モデルの文字列値を返す

            使用例:
                str(ImagenModel.IMAGEN_4_ULTRA) -> "imagen-4.0-ultra-generate-001"
            """
            return self.value
    
    class GeminiModel(Enum):
        """
        画像生成に利用可能なGeminiモデルを表すEnumクラス
        
        各メンバーはGoogle Gen AI SDKにおける`client.models.generate_content()`の呼び出し時に指定するモデル名に対応        
        """
        
        GEMINI_25_FLASH_IMAGE = "gemini-2.5-flash-image"
        """ 画像編集可能なGeminiモデル(edit_imageで指定可能な唯一のモデル) """

        def __str__(self):
            """
            モデルの文字列値を返す

            使用例:
                str(GeminiModel.GEMINI_25_FLASH_IMAGE) -> "gemini-2.5-flash-image"
            """
            return self.value
    # class AspectRatio(Enum):
    #     """
    #     画像生成時に指定可能なアスペクト比を表すEnumクラス

    #     各メンバーは Vertex AI / Gen AI SDK の
    #     `generate_images` メソッドにおける `aspect_ratio` パラメータに対応する
    #     """

    #     SQUARE = "1:1"
    #     """ 正方形の画像(例：アイコンやサムネイル用途) """

    #     WIDE = "16:9"
    #     """ 横長の画像(例：プレゼン資料や動画用サムネイル) """
        
    #     TALL = "9:16"
    #     """ 縦長の画像(例：スマホ画面やSNSストーリー用途) """
        
    #     PORTRAIT = "3:4"
    #     """ 縦長の画像(例：ポートレート写真や印刷用途) """
        
    #     LANDSCAPE = "4:3"
    #     """ 横長の画像(例：一般的な写真やディスプレイ用途) """
        
    #     def __str__(self) -> str:
    #         """
    #         Enumの値を文字列として返す

    #         Returns
    #         -------
    #         str
    #             aspect_ratio の指定値 (例: "16:9")
    #         """
    #         return self.value

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

    # class PersonGeneration(Enum):
    #     """
    #     画像生成時に人物の生成を制御するためのEnumクラス

    #     各メンバーは Vertex AI / Gen AI SDK の
    #     `generate_images` メソッドにおける `person_generation` パラメータに対応する
    #     """
        
    #     DONT_ALLOW = "dont_allow"
    #     """ 人物の画像生成をブロックする """

    #     ALLOW_ADULT = "allow_adult"
    #     """ 大人の画像のみ生成を許可し、子供の画像は生成しない """

    #     ALLOW_ALL = "allow_all"
    #     """ 大人と子供の画像の生成を許可する """

    #     def __str__(self):
    #         """
    #         Enumの値を文字列値として返す

    #         Returns
    #         -------
    #         str
    #             person_generation の指定値
    #         """
    #         return self.value
    
    # class SafetyFilterLevel(Enum):
    #     """
    #     画像生成時に適用される安全フィルタリングレベルを表すEnumクラス

    #     各メンバーは Vertex AI / Gen AI SDK の
    #     `generate_images` メソッドにおける `safety_filter_level` パラメータに対応する
        
    #     Notes
    #     -----
    #     - BLOCK_NONE は allowlist 専用の設定であり、通常の環境では利用できない
    #     未許可の環境で指定すると以下の例外が発生する

    #         HTTP 400 Error:
    #         "The block_none safetySetting is currently an allowlist-only feature.
    #         Please check your current safetySetting value or contact your Google representative
    #         to request allowlisting."

    #     - 通常利用可能な値は以下の通り:
    #         * BLOCK_LOW_AND_ABOVE
    #         * BLOCK_MEDIUM_AND_ABOVE
    #         * BLOCK_ONLY_HIGH
    #     """
        
    #     BLOCK_LOW_AND_ABOVE = "block_low_and_above"
    #     """
    #     最も強力なフィルタリングレベル
    #     最も厳格なブロックが実施される
    #     非推奨の値: "block_most"
    #     """

    #     BLOCK_MEDIUM_AND_ABOVE = "block_medium_and_above"
    #     """
    #     中程度以上の問題のあるプロンプトやレスポンスをブロックする
    #     非推奨の値: "block_some"
    #     """

    #     BLOCK_ONLY_HIGH = "block_only_high"
    #     """
    #     高レベルの問題があるプロンプトやレスポンスのみをブロックする
    #     ブロック回数を削減する
    #     非推奨の値: "block_few"
    #     """

    #     BLOCK_NONE = "block_none"
    #     """
    #     ごく少数の問題のあるプロンプトやレスポンスをブロックする
    #     ほとんどフィルタリングを行わない
    #     非推奨の値: "block_fewest"
    #     """

    #     def __str__(self) -> str:
    #         """
    #         Enumの値を文字列として返す

    #         Returns
    #         -------
    #         str
    #             safety_filter_level の指定値
    #         """
    #         return self.value

    # class HarmCategory(Enum):
    #     """
    #     Gemini API の安全フィルターカテゴリを表す Enum クラス。

    #     この Enum は、Google Generative AI (Gemini) の `GenerateContentConfig.safety_settings`
    #     に指定可能な「有害コンテンツカテゴリ」を定義する
    #     各カテゴリはモデルが生成するコンテンツをフィルタリングする際に利用される

    #     """

    #     HARM_CATEGORY_HARASSMENT = "HARM_CATEGORY_HARASSMENT"
    #     """ ハラスメントコンテンツ。嫌がらせや攻撃的な表現を含む可能性があるもの """

    #     HARM_CATEGORY_HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
    #     """ ヘイトスピーチコンテンツ。特定の人種、宗教、性別などに対する差別的表現 """

    #     HARM_CATEGORY_SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"
    #     """ 性的描写が露骨なコンテンツ。成人向けの性的表現を含むもの """

    #     HARM_CATEGORY_DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"
    #     """ 危険なコンテンツ。暴力、違法行為、危険な行動を助長する可能性があるもの """

    #     HARM_CATEGORY_CIVIC_INTEGRITY = "HARM_CATEGORY_CIVIC_INTEGRITY"
    #     """ 
    #     市民の清廉性を損なう可能性があるコンテンツ 
    #     非推奨
    #     """
    
    def __init__(self, project_id: str, location: str):
        """
        コンストラクタ

        Parameters
        ----------
        project_id : str
            Google Cloud プロジェクトID
        location : str
            Vertex AIのリージョン
        """

        # プロジェクトID
        self.project_id = project_id
        
        # ロケーション
        self.location = location
        
        # APIクライアントの初期化処理
        self._configuration_client()

        # ADC認証クライアント
        self.client = genai.Client(vertexai=True)
        
    def set_authentication(self, project_id: str, location: str):
        """
        認証情報を再設定する

        Parameters
        ----------
        project_id : str
            Google Cloud プロジェクトID
        location : str
            Vertex AIのリージョン
        """
        
        # プロジェクトID
        self.project_id = project_id
        
        # ロケーション
        self.location = location
        
        # APIクライアント初期化
        self._configuration_client()
        
    def _configuration_client(self):
        """
        APIクライアントの初期化処理
        
        Notes
        -----
        内部的に `vertexai.init` を呼び出す
        """

        # vertexai初期化
        vertexai.init(project=self.project_id, location=self.location)

    # def guess_mime_type(self, image_bytes: bytes) -> str:
    #     """
    #     バイト列から画像のMIME typeを推測する

    #     Parameters
    #     ----------
    #     image_bytes : bytes
    #         画像データ

    #     Returns
    #     -------
    #     str
    #         MIME type (例: "image/png", "image/jpeg")
    #     """

    #     # フォーマット判定
    #     fmt = imghdr.what(None, h=image_bytes)
        
    #     if fmt == "png":
    #         return "image/png"
    #     elif fmt == "jpeg":
    #         return "image/jpeg"
    #     elif fmt == "gif":
    #         return "image/gif"
    #     elif fmt == "bmp":
    #         return "image/bmp"
    #     elif fmt == "webp":
    #         return "image/webp"
    #     else:
    #         return "application/octet-stream"
    
    # def generate_image(self, 
    #     prompt: str, 
    #     model: GeminiModel,
    #     aspect_ratio:AspectRatio = AspectRatio.SQUARE,
    #     image_size = ImageSize.ONE_K,
    #     number_of_images:int = 1, 
    #     harm_category = HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    #     safety_filter_level = SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
    #     include_row: bool = False) -> dict:
    #     """
    #     画像生成メソッド【試験用】
        
    #     新SDKに対応した画像生成メソッドだが、2025年12月現在は画像生成モデルのエンドポイントが利用できない
    #     """

    #     # 画像生成リクエスト
    #     app_logger.info(f"Image generation request sent. Model={model.value}, Prompt={prompt}, CandidateCount={number_of_images}")
    #     response = self.client.models.generate_content(
    #         model = model.value,
    #         contents = [prompt],
    #         config = GenerateContentConfig(
    #             response_modalities = [Modality.IMAGE],
    #             candidate_count = number_of_images,                
    #             safety_settings = [
    #                 {"category": harm_category.value},
    #                 {"threshold": safety_filter_level.value.upper()},
    #             ],
    #             image_config = ImageConfig(
    #                 aspect_ratio = aspect_ratio.value,
    #                 image_size = image_size.value,
    #             )
    #         )
    #     )
        
    #     # 画像生成結果チェック
    #     if not response.candidates:
    #         raise NoCandidatesError("No candidates returned. Possibly blocked by safety filters.")
        
    #     # 生成画像をbytesでlist化して返す
    #     image_list: list[bytes] = []
    #     for candidate in response.candidates:
    #         for part in candidate.content.parts:
    #             if part.inline_data:
    #                 image_list.append(part.inline_data.data)
    #                 app_logger.info(f"Image candidate received. Size={len(part.inline_data.data)} bytes")
    #             elif part.text:
    #                 app_logger.warning(f"Text explanation returned instead of image: {part.text}")
        
    #     # 結果を取得する
    #     result = {
    #         "type": "image",
    #         "model": model.value,
    #         "result": image_list,
    #         "metadata": {
    #             "prompt": prompt,
    #             "mode": "generate",
    #             "timestamp": datetime.now(timezone.utc).isoformat()
    #         }
    #     }
    #     if include_row:
    #         result["raw_response"] = []
    #         for idx, image in enumerate(image_list):
    #             row_info = {
    #                 "index": idx,
    #                 "size_bytes": len(image) if isinstance(image, bytes) else None,
    #                 "mime_type": self.guess_mime_type(image),
    #                 "prompt": prompt,
    #                 "aspect_ratio": aspect_ratio.value,
    #                 "timestamp": datetime.now(timezone.utc).isoformat(),
    #                 "model": model.value
    #             }
    #             result["raw_response"].append(row_info)
    #     app_logger.info(f"Image generation completed. Total images={len(image_list)}")
    #     return result
    
    # def edit_image(self, 
    #     base_image,
    #     prompt: str, 
    #     model: GeminiModel,
    #     aspect_ratio:AspectRatio = AspectRatio.SQUARE,
    #     image_size = ImageSize.ONE_K,
    #     number_of_images:int = 1, 
    #     harm_category = HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    #     safety_filter_level = SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
    #     include_row: bool = False) -> dict:
    #     """
    #     元画像を指定して変化させる画像生成メソッド

    #     Parameters
    #     ----------
    #     base_image : bytes
    #         編集対象となる元画像データ
    #     prompt : str
    #         変化の内容を説明するプロンプト
    #     model: GeminiModel
    #         画像生成で使用するモデル
    #     aspect_ratio : AspectRatio, optional
    #         出力画像のアスペクト比 (例: "1:1", "16:9")
    #         default="1:1"
    #     image_size : ImageSize, optional
    #         画像サイズ(1K,2K,4K)
    #         default=1K
    #     number_of_images : int, optional
    #         生成する画像の枚数
    #         default=1
    #     harm_category : HarmCategory
    #         評価のカテゴリ
    #         default="HARM_CATEGORY_DANGEROUS_CONTENT"
    #     safety_filter_level : SafetyFilterLevel, optional
    #         安全フィルタリングのフィルタレベル
    #         default="block_medium_and_above"

    #     Returns
    #     -------
    #     dict
    #         生成結果を含む辞書
    #     """

    #     # 画像編集リクエスト
    #     app_logger.info(f"Image generation request sent. Model={model.value}, Prompt={prompt}, CandidateCount={number_of_images}")
    #     response = self.client.models.generate_content(
    #         model = model.value,
    #         contents = [base_image, prompt],
    #         config = GenerateContentConfig(
    #             response_modalities = [Modality.TEXT, Modality.IMAGE],
    #             candidate_count = number_of_images,                
    #             safety_settings = [
    #                 {"category": harm_category.value},
    #                 {"threshold": safety_filter_level.value.upper()},
    #             ],
    #             image_config = ImageConfig(
    #                 aspect_ratio = aspect_ratio.value,
    #                 image_size = image_size.value,
    #             )
    #         )
    #     )
        
    #     # 画像生成結果チェック
    #     if not response.candidates:
    #         raise NoCandidatesError("No candidates returned. Possibly blocked by safety filters.")
        
    #     # 生成画像をbytesでlist化して返す
    #     image_list: list[bytes] = []
    #     for candidate in response.candidates:
    #         for part in candidate.content.parts:
    #             if part.inline_data:
    #                 image_list.append(part.inline_data.data)
    #                 app_logger.info(f"Image candidate received. Size={len(part.inline_data.data)} bytes")
    #             elif part.text:
    #                 app_logger.warning(f"Text explanation returned instead of image: {part.text}")

    #     # 結果を取得する
    #     result = {
    #         "type": "image",
    #         "model": model.value,
    #         "result": image_list,
    #         "metadata": {
    #             "prompt": prompt,
    #             "mode": "edit",
    #             "timestamp": datetime.now(timezone.utc).isoformat()
    #         }
    #     }
    #     if include_row:
    #         result["raw_response"] = []
    #         for idx, image in enumerate(image_list):
    #             row_info = {
    #                 "index": idx,
    #                 "size_bytes": len(image) if isinstance(image, bytes) else None,
    #                 "mime_type": self.guess_mime_type(image),
    #                 "prompt": prompt,
    #                 "aspect_ratio": aspect_ratio.value,
    #                 "timestamp": datetime.now(timezone.utc).isoformat(),
    #                 "model": model.value
    #             }
    #             result["raw_response"].append(row_info)
    #     app_logger.info(f"Image editing completed. Total images={len(image_list)}")
    #     return result
    
    def generate_image_vertexai(self, 
        prompt: str, 
        model: ImagenModel,
        aspect_ratio:BaseAIClient.AspectRatio = BaseAIClient.AspectRatio.SQUARE, 
        number_of_images:int = 1, 
        language = BaseAIClient.AILang.EN,
        person_generation = BaseAIClient.PersonGeneration.ALLOW_ADULT,
        safety_filter_level = BaseAIClient.SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
        include_row: bool = False) -> dict:
        
        """
        指定したプロンプトに基づいて画像を生成する(Imagen版)

        Parameters
        ----------
        prompt : str
            生成する画像の説明文
        model: ImagenModel
            画像生成で使用するモデル
        aspect_ratio : AspectRatio, optional
            出力画像のアスペクト比 (例: "1:1", "16:9")
            default="1:1"
        number_of_images : int, optional
            生成する画像の枚数
            default=1
        language : BaseAIClient.AILang, optional
            プロンプトの言語指定
            default="en"
        person_generation : PersonGeneration, optional
            人物の画像生成許可
            default="allow_adult"
        safety_filter_level : SafetyFilterLevel, optional
            安全フィルタリングのフィルタレベル
            default="block_medium_and_above"
        include_row : bool, optional
            追加情報を含めるかどうか

        Returns
        -------
        dict
            生成結果を含む辞書。
            {
                "type": "image",
                "model": <使用モデル名>,
                "result": [画像データのリスト],
                "metadata": {
                    "prompt": <入力プロンプト>,
                    "mode": "generate",
                    "timestamp": <ISO8601形式の生成時刻>
                }
            }
        """

        # モデル取得
        image_model = ImageGenerationModel.from_pretrained(model.value)
        
        # 画像生成
        images = image_model.generate_images(
            prompt=prompt,
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio.value,
            language=language.value,
            person_generation=person_generation.value,
            safety_filter_level=safety_filter_level.value,
        )

        # 画像データをbytesでlistに追加
        image_list = [image._image_bytes for image in images]
        
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
            for idx, image in enumerate(images):
                row_info = {
                    "index": idx,
                    "size_bytes": len(image) if isinstance(image, bytes) else None,
                    "mime_type": self.guess_mime_type(image),
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": model.value
                }
                result["raw_response"].append(row_info)

        return result
