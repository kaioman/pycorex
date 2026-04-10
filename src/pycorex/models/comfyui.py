from libcore_hng.core.base_config_model import BaseConfigModel

class ComfyUIModel(BaseConfigModel):
    """
    ComfyUI系設定クラス
    """ 
    
    workflow_path: str = ''
    """ ワークフローJSONファイルパス """

