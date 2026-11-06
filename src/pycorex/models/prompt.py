from dataclasses import dataclass, field
from libcore_hng.core.base_config_model import BaseConfigModel
from pycorex.enums.rating_level import RatingLevel

class PromptModel(BaseConfigModel):
    """
    プロンプト系設定クラス
    """ 
    
    json_path: str = ''
    """ JSONファイルパス """

@dataclass
class SelectedAssets():
    """
    選択されたasset情報
    """

    scene_id: str = ''
    """ シーンID """

    environment_id: str = ''
    """ 環境ID """
    
    camera_id: str = ''
    """ カメラアングルID """
    
    outfits_id: str = ''
    """ 服装ID """
    
    inner_top: str = ''
    """ 下着ID(トップス) """
    
    inner_bottom: str = ''
    """ 下着ID(ボトムス) """
    
    outer_top: str = ''
    """ 上着ID(トップス) """
    
    outer_bottom: str = ''
    """ 上着ID(ボトムス) """
@dataclass
class PromptContextModel():
    """
    プロンプトコンテキストモデルクラス
    """
    
    prompt_level: RatingLevel = RatingLevel.SAFE
    """ プロンプトレベル """

    scene_id: str = ''
    """ scene_id """

    selected_assets: SelectedAssets = field(default_factory=SelectedAssets)
    """ 選択されたasset情報"""

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