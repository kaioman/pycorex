from libcore_hng.core.base_config import BaseConfig
from pycorex.models.gemini import GeminiModel
from pycorex.models.vertexai import VertexaiModel
from pycorex.models.prompt import PromptModel

class PyCorexConfig(BaseConfig):
    """
    pycorex共通設定クラス
    """
    
    gemini: GeminiModel = GeminiModel()
    """ Gemini設定クラスモデル """
    
    vertexai: VertexaiModel = VertexaiModel()
    """ Vertexai設定クラスモデル """
    
    prompt: PromptModel = PromptModel()
    """ プロンプト系クラスモデル """