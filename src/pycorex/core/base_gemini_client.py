from enum import Enum
from pycorex.core.base_ai_client import BaseAIClient

class BaseGeminiClient(BaseAIClient):
    """
    BaseGeminiClient
    """
    
    class AILang(Enum):
        """
        言語設定
        """
        
        JP = 'ja'
        """ 日本語 """

        EN = 'en'
        """ 英語 """

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

    class HarmCategory(Enum):
        """
        Gemini API の安全フィルターカテゴリを表す Enum クラス。

        この Enum は、Google Generative AI (Gemini) の `GenerateContentConfig.safety_settings`
        に指定可能な「有害コンテンツカテゴリ」を定義する
        各カテゴリはモデルが生成するコンテンツをフィルタリングする際に利用される

        """

        HARM_CATEGORY_HARASSMENT = "HARM_CATEGORY_HARASSMENT"
        """ ハラスメントコンテンツ。嫌がらせや攻撃的な表現を含む可能性があるもの """

        HARM_CATEGORY_HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
        """ ヘイトスピーチコンテンツ。特定の人種、宗教、性別などに対する差別的表現 """

        HARM_CATEGORY_SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"
        """ 性的描写が露骨なコンテンツ。成人向けの性的表現を含むもの """

        HARM_CATEGORY_DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"
        """ 危険なコンテンツ。暴力、違法行為、危険な行動を助長する可能性があるもの """

        HARM_CATEGORY_CIVIC_INTEGRITY = "HARM_CATEGORY_CIVIC_INTEGRITY"
        """ 
        市民の清廉性を損なう可能性があるコンテンツ 
        非推奨
        """
        
    def __init__(self):
        """
        コンストラクタ
        """

        # 生成モデル
        self.model = None
    
    def set_model(self, model: Enum):
        """
        生成モデルをセットする
        """

        # 生成モデル
        self.model = model
    
