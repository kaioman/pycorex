import vertexai
import imghdr
from enum import Enum
from datetime import datetime, timezone
from vertexai.vision_models import ImageGenerationModel
from pycorex.core.base_ai_client import BaseAIClient

class ImagenClient(BaseAIClient):
    """
    Google Vertex AI / Gen AI SDK を利用して画像生成を行うクライアントクラス

    Attributes
    ----------
    project_id : str
        利用するGoogle CloudプロジェクトのID
    location : str
        Vertex AIのリージョン
    model : ImagenModel
        使用するImagenモデル
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
    
    class AspectRatio(Enum):
        """
        画像生成時に指定可能なアスペクト比を表すEnumクラス

        各メンバーは Vertex AI / Gen AI SDK の
        `generate_images` メソッドにおける `aspect_ratio` パラメータに対応する
        """

        SQUARE = "1:1"
        """ 正方形の画像(例：アイコンやサムネイル用途) """

        WIDE = "16:9"
        """ 横長の画像(例：プレゼン資料や動画用サムネイル) """
        
        TALL = "9:16"
        """ 縦長の画像(例：スマホ画面やSNSストーリー用途) """
        
        PORTRAIT = "3:4"
        """ 縦長の画像(例：ポートレート写真や印刷用途) """
        
        LANDSCAPE = "4:3"
        """ 横長の画像(例：一般的な写真やディスプレイ用途) """
        
        def __str__(self) -> str:
            """
            Enumの値を文字列として返す

            Returns
            -------
            str
                aspect_ratio の指定値 (例: "16:9")
            """
            return self.value

    class PersonGeneration(Enum):
        """
        画像生成時に人物の生成を制御するためのEnumクラス

        各メンバーは Vertex AI / Gen AI SDK の
        `generate_images` メソッドにおける `person_generation` パラメータに対応する
        """
        
        DONT_ALLOW = "dont_allow"
        """ 人物の画像生成をブロックする """

        ALLOW_ADULT = "allow_adult"
        """ 大人の画像のみ生成を許可し、子供の画像は生成しない """

        ALLOW_ALL = "allow_all"
        """ 大人と子供の画像の生成を許可する """

        def __str__(self):
            """
            Enumの値を文字列値として返す

            Returns
            -------
            str
                person_generation の指定値
            """
            return self.value
    
    class SafetyFilterLevel(Enum):
        """
        画像生成時に適用される安全フィルタリングレベルを表すEnumクラス

        各メンバーは Vertex AI / Gen AI SDK の
        `generate_images` メソッドにおける `safety_filter_level` パラメータに対応する
        
        Notes
        -----
        - BLOCK_NONE は allowlist 専用の設定であり、通常の環境では利用できない
        未許可の環境で指定すると以下の例外が発生する

            HTTP 400 Error:
            "The block_none safetySetting is currently an allowlist-only feature.
            Please check your current safetySetting value or contact your Google representative
            to request allowlisting."

        - 通常利用可能な値は以下の通り:
            * BLOCK_LOW_AND_ABOVE
            * BLOCK_MEDIUM_AND_ABOVE
            * BLOCK_ONLY_HIGH
        """
        
        BLOCK_LOW_AND_ABOVE = "block_low_and_above"
        """
        最も強力なフィルタリングレベル
        最も厳格なブロックが実施される
        非推奨の値: "block_most"
        """

        BLOCK_MEDIUM_AND_ABOVE = "block_medium_and_above"
        """
        中程度以上の問題のあるプロンプトやレスポンスをブロックする
        非推奨の値: "block_some"
        """

        BLOCK_ONLY_HIGH = "block_only_high"
        """
        高レベルの問題があるプロンプトやレスポンスのみをブロックする
        ブロック回数を削減する
        非推奨の値: "block_few"
        """

        BLOCK_NONE = "block_none"
        """
        ごく少数の問題のあるプロンプトやレスポンスをブロックする
        ほとんどフィルタリングを行わない
        非推奨の値: "block_fewest"
        """

        def __str__(self) -> str:
            """
            Enumの値を文字列として返す

            Returns
            -------
            str
                safety_filter_level の指定値
            """
            return self.value

    def __init__(self, project_id: str, location: str, model: ImagenModel):
        """
        コンストラクタ

        Parameters
        ----------
        project_id : str
            Google Cloud プロジェクトID
        location : str
            Vertex AIのリージョン
        model : ImagenModel
            画像生成モデル
        """

        # プロジェクトID
        self.project_id = project_id
        
        # ロケーション
        self.location = location
        
        # モデル情報
        self.model = model

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
        
        Notes
        -----
        内部的に `vertexai.init` を呼び出す
        """

        # vertexai初期化
        vertexai.init(project=self.project_id, location=self.location)

    def generate_image(self, 
        prompt: str, 
        aspect_ratio:AspectRatio = AspectRatio.SQUARE, 
        number_of_images:int = 1, 
        language = BaseAIClient.AILang.EN,
        person_generation = PersonGeneration.ALLOW_ADULT,
        safety_filter_level = SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
        include_row: bool = False) -> dict:
        
        """
        指定したプロンプトに基づいて画像を生成する

        Parameters
        ----------
        prompt : str
            生成する画像の説明文
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
        image_model = ImageGenerationModel.from_pretrained(self.model.value)
        
        # 画像生成
        # images = image_model.generate_images(
        #     prompt=prompt,
        #     number_of_images=number_of_images,
        #     aspect_ratio=aspect_ratio,
        #     language=language.value,
        #     person_generation="",
        #     safety_filter_level="",
        #     seed=-1,
        #     sample_image_size="",
        #     output_mime_type="",
        #     compression_quality=75
        # )
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
            "model": self.model.value,
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
                    "model": self.model.value
                }
                result["raw_response"].append(row_info)

        return result

    def guess_mime_type(self, image_bytes: bytes) -> str:
        """
        バイト列から画像のMIME typeを推測する

        Parameters
        ----------
        image_bytes : bytes
            画像データ

        Returns
        -------
        str
            MIME type (例: "image/png", "image/jpeg")
        """

        # フォーマット判定
        fmt = imghdr.what(None, h=image_bytes)
        
        if fmt == "png":
            return "image/png"
        elif fmt == "jpeg":
            return "image/jpeg"
        elif fmt == "gif":
            return "image/gif"
        elif fmt == "bmp":
            return "image/bmp"
        elif fmt == "webp":
            return "image/webp"
        else:
            return "application/octet-stream"
        
    def generate_image_newsdk(self, prompt: str, aspect_ratio:str, number_of_images:int = 1) -> dict:
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