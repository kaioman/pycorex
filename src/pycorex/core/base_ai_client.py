import os
import uuid
import imghdr
import asyncio
import libcore_hng.utils.app_logger as app_logger
from abc import ABC, abstractmethod
from typing import Callable, Any
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
    
    async def execute_with_retry(
        self, 
        func: Callable[..., Any], 
        *args, 
        validator: Callable[[Any], bool] = None, 
        **kwargs) -> Any:
        """
        同期メソッドをリトライ付きで実行す
        
        Parameters
        ----------
        func : Callable[..., Any]
            実行するメソッド
        validator : Callable[[Any], bool]
            検証メソッド(未指定時は実行メソッドがNoneで無ければOKと見なす)

        Returns
        -------
        Any
            応答結果
        """

        # 最大試行回数と実行間隔を取得する
        max_retryies = os.getenv("SEND_MESSAGE_MAX_RETRYIES", 3)
        retry_interval = os.getenv("SEND_MESSAGE_RETRY_INTERVAL", 2)

        # 最大試行回数だけループする
        for attempt in range(max_retryies):
            try:
                # 実行
                result = await asyncio.to_thread(func, *args, **kwargs)

                # validatorが指定されていない場合はresultがあれば成功とみなす
                if validator is None:
                    if result is not None:
                        return result
                # validatorが指定されている場合は、その判定に従う
                elif validator(result):
                    return result
                
                # 試行警告ログ
                app_logger.warning(f"Attempt {attempt + 1}: Validation falied.")

            except Exception as e:
                # 試行エラーログ
                app_logger.error(f"Attempt {attempt + 1} failed: {e}")
                # 最終試行時は例外をスローする
                if attempt == max_retryies - 1:
                    raise e
                
            # 実行間隔の値に基づき待機
            await asyncio.sleep(retry_interval)

        return None