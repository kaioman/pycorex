from libcore_hng.core.base_config_model import BaseConfigModel

class PromptModel(BaseConfigModel):
    """
    プロンプト系設定クラス
    """ 
    
    json_path: str = ''
    """ JSONファイルパス """

