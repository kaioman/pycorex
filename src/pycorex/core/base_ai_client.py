from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any

class BaseAIClient(ABC):
    """
    BaseAIClient
    """
    
    class AILang(Enum):
        """
        言語設定
        """
        
        JP = 'ja'
        """ 日本語 """

        EN = 'en'
        """ 英語 """

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
    
    @abstractmethod
    def _configuration_client(self):
        """
        APIクライアントの初期化処理
        
        Notes
        -----
        内部的に `genai.configure(api_key=...)` を呼び出し、
        `self.client` に設定する
        """
        pass
    
    #@abstractmethod
    #def calc_tokens(self, prompt: str, response_text: str) -> dict:
    #    """
    #    プロンプトと応答テキストのトークン数を計算する
    #    """
    #    pass
    
    #@abstractmethod
    #def generate_text(self, prompt: str, language: AILang = AILang.JP, include_row: bool = False) -> Dict[str, Any]:
    #    pass

    #@abstractmethod
    #def generate_image(self, prompt: str, pspect_ratio:str, number_of_images:int = 1, include_row: bool = False) -> list[bytes]:
    #    pass
    
    # def set_prompt(self, _jsonFileName):
        
    #     """
    #     プロンプトをセットする
        
    #     Parameters
    #     ----------
    #     _jsonFileName : str
    #         プロンプトのjsonファイル名
    #     """

    #     # ファイル名
    #     jsonFilePath = os.path.join(
    #         os.path.dirname(self.rootPath), 
    #         self.jsonFilePath,
    #         _jsonFileName)
        
    #     # jsonファイルチェック
    #     if not os.path.exists(jsonFilePath):
    #         Logger.logging.info('jsonfile is not found.')
    #         return

    #     # jsonファイルOpen
    #     with open(jsonFilePath, encoding="utf-8") as f:
    #         self.promptList = json.loads(f.read())
        
    # def request(self):
        
    #     """
    #     APIから応答を取得する

    #     Parameters
    #     ----------
    #     None
    #     """

    #     pass
    
    # def get_content(self, _targetContent):
        
    #     """
    #     jsonファイルからContentsを取得する
        
    #     Parameters
    #     ----------
    #     _targetContent : str or list
    #         対象のContent
    #     """
        
    #     if isinstance(self.promptList[_targetContent], list):
    #         return '\n'.join(self.promptList[_targetContent])
    #     else:
    #         return self.promptList[_targetContent]
    