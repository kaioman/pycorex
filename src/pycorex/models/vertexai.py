from libcore_hng.core.base_config_model import BaseConfigModel

class VertexaiModel(BaseConfigModel):
    """
    Vertexai設定クラス
    """ 
    
    project_id: str = ''
    """ プロジェクトID(vertexai) """

    location: str = ''
    """ ロケーション(vertexai) """