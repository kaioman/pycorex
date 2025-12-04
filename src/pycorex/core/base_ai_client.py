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
        
        jp = 'ja'
        """ 日本語 """

        en = 'en'
        """ 英語 """

    # class promtDictElement():
        
    #     """
    #     PromptDict要素
    #     """
        
    #     systemContent = 'systemContent'
    #     """ systemContent """

    #     userContent = 'userContent'
    #     """ userContent """

    #     assistantContent = 'assistantContent'
    #     """ assistantContent """
        
    def __init__(self, api_key: str, model: Enum):
        """
        コンストラクタ
        
        Parameters
        ----------
        api_key : str
            APIキー
        model : Enum
            model
        """

        # APIキー
        self.api_key = api_key

        # モデル情報
        self.model = model
    
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
        
    @abstractmethod
    def _configuration_client(self):
        """
        APIクライアントの初期化処理
        """
        pass
    
    @abstractmethod
    def calc_tokens(self, prompt: str, response_text: str) -> dict:
        """
        プロンプトと応答テキストのトークン数を計算する
        """
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, language: AILang = AILang.jp, include_row: bool = False) -> Dict[str, Any]:
        pass
    
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
    