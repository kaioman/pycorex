import libcore_hng.utils.app_logger as app_logger
from enum import Enum
from datetime import datetime, timezone
from google import genai
from google.genai.types import GenerateImagesConfig, EditImageConfig
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
        """

        # ADC認証クライアント
        self.client = genai.Client(vertexai=True, project=self.project_id, location=self.location)

    def generate_image(self, 
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

        # 開始ログ
        app_logger.info(f"Image generation request sent. Model={model.value}, Prompt={prompt}, CandidateCount={number_of_images}")

        # 画像生成リクエスト
        response = self.client.models.generate_images(
            prompt=prompt,
            model=model.value,
            config=GenerateImagesConfig(
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio.value,
                person_generation=person_generation.value,
                safety_filter_level=safety_filter_level.value,
                language=language.value,
            )
        )

        # 画像データをbytesでlistに追加
        image_list = [generated.image.image_bytes for generated in response.generated_images]
        
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
                    "aspect_ratio": aspect_ratio,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": model.value
                }
                result["raw_response"].append(row_info)

        return result
    
    def edit_image(self, 
        base_image,
        prompt: str, 
        model: ImagenModel,
        aspect_ratio:BaseAIClient.AspectRatio = BaseAIClient.AspectRatio.SQUARE, 
        number_of_images:int = 1, 
        language = BaseAIClient.AILang.EN,
        person_generation = BaseAIClient.PersonGeneration.ALLOW_ADULT,
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

        Returns
        -------
        dict
            生成結果を含む辞書
        """

        # 開始ログ
        app_logger.info(f"Image edit request sent. Model={model.value}, Prompt={prompt}, CandidateCount={number_of_images}")

        # 画像編集リクエスト
        response = self.client.models.edit_image(
            model=model.value,
            prompt=prompt,
            reference_images=base_image,
            config=EditImageConfig(
                number_of_images=number_of_images,                
                aspect_ratio=aspect_ratio.value,
                safety_filter_level=safety_filter_level.value.upper(),
                person_generation=person_generation.value,
                language=language.value,
                output_mime_type="image/png",
            )
        )
        
        # 画像生成結果チェック
        if not response.generated_images:
            raise NoCandidatesError("No candidates returned. Possibly blocked by safety filters.")
        
        # 画像データをbytesでlistに追加
        image_list = [generated.image.image_bytes for generated in response.generated_images]

        # 生成画像をbytesでlist化して返す
        image_list: list[bytes] = []
        for generated in response.generated_images:
            # 生成画像(bytes)をリストに追加
            if generated.image and generated.image.image_bytes:
                image_list.append(generated.image.image_bytes)
            # テキストを含む場合はテキスト内容をログ出力
            if hasattr(generated, 'text') and generated.text:
                app_logger.warning(f"Text explanation returned instead of image: {generated.text}")

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
    
