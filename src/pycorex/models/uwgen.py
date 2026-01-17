from libcore_hng.core.base_config_model import BaseConfigModel

class UwgenModel(BaseConfigModel):
    """
    Uwgen設定クラス
    """ 
    
    api_key: str = ""
    """ Uwgen APIキー """
    
    endpoint: str = ""
    """ Uwgen APIエンドポイントURL """
