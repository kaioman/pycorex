class APIError(Exception):
    """
    外部API呼び出し時のエラー例外クラス
    """
    
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self._build_message())
        
    def _build_message(self) -> str:
        """
        例外メッセージを組み立てる内部メソッド
        """
        
        base  = self.message
        
        if self.status_code is not None:
            base += f"(status_code={self.status_code})"
            
        if self.response_text:
            base += f" | response={self.response_text}"
            
        return base