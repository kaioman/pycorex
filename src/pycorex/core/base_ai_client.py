import imghdr
from abc import ABC, abstractmethod

class BaseAIClient(ABC):
    """
    BaseAIClient
    """
    
    def __init__(self):
        """
        コンストラクタ
        """
        pass

    @abstractmethod
    def _configuration_client(self):
        """
        APIクライアントの初期化処理
        """
        pass
    
    def guess_mime_type(self, image_bytes: bytes) -> str:
        """
        バイト列から画像のMIME typeを推測する

        Parameters
        ----------
        image_bytes : bytes
            画像データ

        Returns
        -------
        str
            MIME type (例: "image/png", "image/jpeg")
        """

        # フォーマット判定
        fmt = imghdr.what(None, h=image_bytes)
        
        if fmt == "png":
            return "image/png"
        elif fmt == "jpeg":
            return "image/jpeg"
        elif fmt == "gif":
            return "image/gif"
        elif fmt == "bmp":
            return "image/bmp"
        elif fmt == "webp":
            return "image/webp"
        else:
            return "application/octet-stream"
