from libcore_hng.core.base_config import BaseConfig
from pycorex.models.auth import AuthModel
from pycorex.models.prompt import PromptModel

class PyCorexConfig(BaseConfig):
    """
    pycorex共通設定クラス
    """
    
    auth: AuthModel = AuthModel()
    """ 認証系設定クラスモデル """
    
    prompt: PromptModel = PromptModel()
    """ プロンプト系クラスモデル """