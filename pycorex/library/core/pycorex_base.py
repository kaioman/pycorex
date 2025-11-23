import os
import json
import LibHanger.Library.uwLogger as Logger

class pycorex_base():
    
    """
    pycorex_base
    """
    
    class aiLang():
        
        """
        言語設定
        """
        
        jp = 'Jp'
        """ 日本語 """

        en = 'En'
        """ 英語 """

    class promtDictElement():
        
        """
        PromptDict要素
        """
        
        systemContent = 'systemContent'
        """ systemContent """

        userContent = 'userContent'
        """ userContent """

        assistantContent = 'assistantContent'
        """ assistantContent """
        
    def __init__(self, _rootPath, _jsonFilePath, _organization, _api_key) -> None:
        
        """
        コンストラクタ
        
        Parameters
        ----------
        _rootPath : str
            Root path
        _jsonFilePath : str
            Promt jsonFile path
        _organization : str
            organization
        _api_key : str
            api_key
        """

        # 認証情報
        self.set_authentication(_organization, _api_key)

        # ルートパス
        self.rootPathFull = _rootPath
        self.rootPath = os.path.dirname(_rootPath)

        # pycorex - response
        self.response = None

        # PromptJsonFile Path
        self.jsonFilePath = _jsonFilePath

        # PromptList
        self.promptList = []
        
    @property
    def response_message(self):
        
        """
        APIからの応答メッセージ
        """
        pass
    
    @property
    def prompt(self) -> list:
        
        """
        Promptリスト
        """
        return self.promptList
    
    def set_prompt(self, _jsonFileName):
        
        """
        プロンプトをセットする
        
        Parameters
        ----------
        _jsonFileName : str
            プロンプトのjsonファイル名
        """

        # ファイル名
        jsonFilePath = os.path.join(
            os.path.dirname(self.rootPath), 
            self.jsonFilePath,
            _jsonFileName)
        
        # jsonファイルチェック
        if not os.path.exists(jsonFilePath):
            Logger.logging.info('jsonfile is not found.')
            return

        # jsonファイルOpen
        with open(jsonFilePath, encoding="utf-8") as f:
            self.promptList = json.loads(f.read())
    
    def set_authentication(self, _organization, _api_key):
        pass
    
    def request(self):
        
        """
        APIから応答を取得する

        Parameters
        ----------
        None
        """

        pass
    
    def get_content(self, _targetContent):
        
        """
        jsonファイルからContentsを取得する
        
        Parameters
        ----------
        _targetContent : str or list
            対象のContent
        """
        
        if isinstance(self.promptList[_targetContent], list):
            return '\n'.join(self.promptList[_targetContent])
        else:
            return self.promptList[_targetContent]
    