import uuid
import imghdr
from abc import ABC, abstractmethod
from datetime import datetime, timezone

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

    def get_gen_filename(self):
        """
        生成画像のファイル名を取得する(例: "20240601T123456Z_abcdef123456.png")
        """
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        unique = uuid.uuid4().hex
        return f"{timestamp}_{unique}.png"