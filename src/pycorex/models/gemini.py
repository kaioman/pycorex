from libcore_hng.core.base_config_model import BaseConfigModel

class GeminiModel(BaseConfigModel):
    """
    Gemini設定クラス
    """ 
    
    api_key: str = ''
    """ APIキー(generative language) """
    
    api_key_vertexai: str = ''
    """ APIキー(vertexai) """
