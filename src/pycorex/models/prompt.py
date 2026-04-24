from dataclasses import dataclass
from libcore_hng.core.base_config_model import BaseConfigModel

class PromptModel(BaseConfigModel):
    """
    プロンプト系設定クラス
    """ 
    
    json_path: str = ''
    """ JSONファイルパス """

@dataclass
class PromptContextModel():
    """
    プロンプトコンテキストモデルクラス
    """
    
    positive_prompt: str = ''
    """ ポジティブプロンプト """
    
    negative_prompt: str = ''
    """ ネガティブプロンプト """
    
    image_width: int = 1024
    """ 画像幅 """
    
    image_height: int = 1024
    """ 画像高さ """