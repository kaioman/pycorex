import os
import base64
import requests
import libcore_hng.utils.app_logger as app_logger
import pycorex.configs.app_init as app
from enum import Enum
from http import HTTPStatus
from datetime import datetime, timezone
from pycorex.core.base_ai_client import BaseAIClient
from pycorex.exceptions.api_error import APIError
from pycorex.exceptions.no_candidates_error import NoCandidatesError

class UwgenClient(BaseAIClient):
    """
    Uwgen APIを利用して画像生成・編集・解析を行うクライアントクラス
    """
    
    class UwgenModel(Enum):
        """
        Uwgenモデル
        """

        IMAGE_GEN = "image_gen"
        """ 画像生成 """
        
        IMAGE_EDIT = "image_edit"
        """ 画像編集 """
        
        IMAGE_ANALYZE = "image_analyze"
        """ 画像解析 """

        def __str__(self):
            return self.value
        
    def __init__(self):
        """
        コンストラクタ
        """
        
        # Authorizationヘッダーの設定
        self.headers = { "Authorization": f"Uwgen {app.core.config.uwgen.api_key}"}
        # エンドポイントURLの設定
        self.endpoint = app.core.config.uwgen.endpoint.rstrip("/")
    
    def _configuration_client(self):
        """
        APIクライアントの初期化処理
        """

        pass
        
    def generate_image(self, prompt: str, **params):
        """
        画像生成処理
        """

        # payloadの組み立て        
        payload = {"prompt": prompt, **params}
        
        # エンドポイントURL取得
        url = f"{self.endpoint}/{UwgenClient.UwgenModel.IMAGE_GEN.value}"
        
        # payloadをログ出力
        app_logger.info(f"[Uwgen] Request image_gen: {payload}")

        # 画像生成をリクエストする
        res = requests.post(url, json=payload, headers=self.headers)

        # Httpステータスコード判定
        if not (HTTPStatus.OK <= res.status_code < HTTPStatus.MULTIPLE_CHOICES):
            raise APIError(
                message="Uwgen API error",
                status_code=res.status_code,
                response_text=res.text
            )
        
        # 画像データ(base64)取得
        json_data = res.json()
        images_base64 = json_data["data"]["generated"]["images"]
        if not images_base64:
            raise NoCandidatesError(f"No images returned from Uwgen API")
        
        # 画像データをBase64 -> bytesに変換
        image_bytes_list = []
        for img in images_base64:
            try:
                image_bytes_list.append(base64.b64decode(img))
            except Exception:
                raise APIError("Failed to decode base64 image returned by Uwgen API")
        
        # 結果を取得する
        result = {
            "type": "image",
            "model": payload.get("model", "unkwon model"),
            "images": image_bytes_list,
            "metadata": {
                "prompt": prompt,
                "mode": "generate",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "params": params
            }
        }
        
        # 生成結果を返す
        return result

    def edit_image(self, prompt: str, source_image_path: str, **params):
        """
        画像を編集する
        """
        
        # payloadの組み立て        
        payload = {"prompt": prompt, **params}
        
        # エンドポイントURL取得
        url = f"{self.endpoint}/{UwgenClient.UwgenModel.IMAGE_EDIT.value}"

        # payloadをログ出力
        app_logger.info(f"[Uwgen] Request image_edit: {payload}")

        # 編集元画像を取得する
        files = {
            "sourceImage": open(source_image_path, "rb")
        }

        # 画像生成をリクエストする
        res = requests.post(url, data=payload, files=files, headers=self.headers)

        # Httpステータスコード判定
        if not (HTTPStatus.OK <= res.status_code < HTTPStatus.MULTIPLE_CHOICES):
            raise APIError(
                message="Uwgen API error",
                status_code=res.status_code,
                response_text=res.text
            )
        
        # 画像データ(base64)取得
        json_data = res.json()
        images_base64 = json_data["data"]["generated"]["images"]
        if not images_base64:
            raise NoCandidatesError(f"No images returned from Uwgen API")
        
        # 画像データをBase64 -> bytesに変換
        image_bytes_list = []
        for img in images_base64:
            try:
                image_bytes_list.append(base64.b64decode(img))
            except Exception:
                raise APIError("Failed to decode base64 image returned by Uwgen API")
        
        # 結果を取得する
        result = {
            "type": "image",
            "model": payload.get("model", "unkwon model"),
            "images": image_bytes_list,
            "metadata": {
                "prompt": prompt,
                "mode": "edit",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "params": params
            }
        }
        
        # 生成結果を返す
        return result

    def analyze_image(self, prompt: str, source_image_path: str, **params):
        """
        画像を解析する
        """
        
        # payloadの組み立て        
        payload = {"prompt": prompt, **params}
        
        # エンドポイントURL取得
        url = f"{self.endpoint}/{UwgenClient.UwgenModel.IMAGE_ANALYZE.value}"

        # payloadをログ出力
        app_logger.info(f"[Uwgen] Request image_analyze: {payload}")

        # 解析画像を取得する
        files = {
            "sourceImage": open(source_image_path, "rb")
        }

        # 画像解析をリクエストする
        res = requests.post(url, data=payload, files=files, headers=self.headers)

        # Httpステータスコード判定
        if not (HTTPStatus.OK <= res.status_code < HTTPStatus.MULTIPLE_CHOICES):
            raise APIError(
                message="Uwgen API error",
                status_code=res.status_code,
                response_text=res.text
            )
        
        # レスポンスをjsonで取得
        json_data = res.json()
        
        # 結果を取得する
        result = {
            "type": "text",
            "model": payload.get("model", "unkwon model"),
            "text": json_data["data"]["generated"]["result"],
            "metadata": {
                "prompt": prompt,
                "mode": "analyze",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "params": params
            }
        }
        
        # 生成結果を返す
        return result
    
    def output_images(self, images, output_abs_path):
        """
        画像を保存する
        """
        
        # 出力パスルート取得
        output_root_path = app.core.config.project_root_path / output_abs_path
        
        # タイムスタンプ生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 画像出力処理
        for idx, img_bytes in enumerate(images):
            
            # ファイル名生成
            filename = f"{timestamp}_{idx}.png"
            file_path = os.path.join(output_root_path, filename)

            # ファイル出力
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            
            # ログ出力
            app_logger.info(f"Saved: {file_path}")
    
    def get_source_file_path(self, input_abs_path, filename):
        """
        元画像ファイルパスを取得する
        """

        # 入力パスルート取得
        input_root_path = app.core.config.project_root_path / input_abs_path
        
        # 入力画像パス取得
        image_path = os.path.join(input_root_path, filename)

        # 戻り値を返す
        return image_path