from libcore_hng.core.base_config_model import BaseConfigModel

class ComfyUIModel(BaseConfigModel):
    """
    ComfyUI系設定クラス
    """ 
    
    comfyui_endpoint: str = ''
    """ ComfyUI APIエンドポイントURL """

    workflow_path: str = ''
    """ ワークフローJSONファイルパス """

    timeout_seconds: int = 120
    """ ワークフロー実行のタイムアウト時間（秒） """

    polling_interval: int = 1
    """ ワークフロー実行のポーリング間隔（秒） """