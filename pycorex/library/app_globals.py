from LibHanger.Library.uwGlobals import globalValues
from pycorex.library.app_config import app_config

class app_globals(globalValues):
    
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ呼び出し
        super().__init__()

        self.pycorex_config:app_config = None
        """ pycorex共通設定 """

# インスタンス生成(import時に実行される)
gvPyco = app_globals()
