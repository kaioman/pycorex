from libcore_hng.exceptions.api_exception import ApiException

class ComfyUIAPIError(ApiException):
    """
    ComfyUI API呼び出しエラーを表す例外クラス
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