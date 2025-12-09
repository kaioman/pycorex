from libcore_hng.core.base_app_exception import AppBaseException

class NoCandidatesError(AppBaseException):
    """
    画像生成失敗例外クラス
    
    - 画像生成候補が返されなかった場合に発生する例外
    """
    
    def __init__(self, exc: Exception = None):
        """
        コンストラクタ
        
        Parameters
        ----------
        exc : Exception, optional
            捕捉した例外オブジェクト。指定しない場合は None
            渡された例外の型・値・トレースバックを保持する
        """
        super().__init__(exc)