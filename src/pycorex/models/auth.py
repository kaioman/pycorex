from libcore_hng.core.base_config_model import BaseConfigModel

class AuthModel(BaseConfigModel):
    """
    認証系設定クラス
    """ 
    
    api_key: str = ''
    """ APIキー """
    
