from LibHanger.Library.uwConfig import cmnConfig

class app_config(cmnConfig):
    
    """
    pycorex共通設定クラス
    """ 
    
    class settingValueStruct(cmnConfig.settingValueStruct):

        """
        設定値構造体
        """ 

        pass
    
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ
        super().__init__()
        
        self.organization = ''
        """ organization """
        
        self.api_key = ''
        """ api_key """
        
        self.jsonFilePath = ''
        """ PromptJsonFile Path """
        
        # 設定ファイル名追加
        self.setConfigFileName('pycorex.ini')
        
    def getConfig(self, _scriptFilePath: str, _configFileDir: str = ''):
        
        """ 
        設定ファイルを読み込む 
        
        Parameters
        ----------
        _scriptFilePath : str
            スクリプトファイルパス
        _configFileDir : str
            設定ファイルの格納場所となるディレクトリ
        """

        # 基底側のiniファイル読込
        super().getConfig(_scriptFilePath, _configFileDir)
        
    def setInstanceMemberValues(self):
        
        """ 
        インスタンス変数に読み取った設定値をセットする
        """
        
        # 基底側実行
        super().setInstanceMemberValues()
        
        # organization
        self.setConfigValue('organization',self.config_ini,'AUTH','ORGANIZATION',str)

        # api_key
        self.setConfigValue('api_key',self.config_ini,'AUTH','API_KEY',str)

        # PromptJsonFile Path
        self.setConfigValue('jsonFilePath',self.config_ini,'DIR','PROMPT_JSON_PATH',str)
