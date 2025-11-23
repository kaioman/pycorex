import LibHanger.Library.uwLogger as Logger
from LibHanger.Library.uwGlobals import configer
from LibHanger.Library.uwGlobals import *
from pycorex.library.app_globals import *

class app_configer(configer):
    
    """
    pycorex共通設定クラス
    """
    
    def __init__(self, _tgv:app_globals, _file, _configFolderName = ''):
        
        """
        コンストラクタ
        """
        
        # pycorex.ini
        da = app_config()
        da.getConfig(_file, _configFolderName)

        # gvセット
        _tgv.pycorex_config = da
        
        # ロガー設定
        Logger.setting(da)
