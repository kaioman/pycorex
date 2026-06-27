from dataclasses import dataclass
from libcore_hng.core.base_config_model import BaseConfigModel
from pycorex.enums.rating_level import RatingLevel

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
    
    prompt_level: RatingLevel = RatingLevel.SAFE
    """ プロンプトレベル """

    scene_id: str = ''
    """ scene_id """

    positive_prompt: str = ''
    """ ポジティブプロンプト """
    
    negative_prompt: str = ''
    """ ネガティブプロンプト """
    
    image_width: int = 1024
    """ 画像幅 """
    
    image_height: int = 1024
    """ 画像高さ """

    face_detailer_positive_prompt: str = ''
    """ Face Detailer用ポジティブプロンプト """

    face_detailer_negative_prompt: str = ''
    """ Face Detailer用ポジティブプロンプト """