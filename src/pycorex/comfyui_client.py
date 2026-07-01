import json
import time
import uuid
import asyncio
import requests
import libcore_hng.utils.app_logger as app_logger
from http import HTTPStatus
from typing import Dict, Any, List, Union, Optional
from pathlib import Path
from datetime import datetime, timezone
from pycorex.core.base_ai_client import BaseAIClient
from pycorex.exceptions.comfyui_exceptions import ComfyUIAPIError
from pycorex.utils.workflow_editor import NodeModification, WorkflowEditor
from pycorex.exceptions.no_candidates_error import NoCandidatesError

class ComfyUIClient(BaseAIClient):
    """
    ComfyUI APIとの通信クライアントクラス
    """

    def __init__(
        self, 
        base_url: str,
        timeout_seconds: int = 120,
        polling_interval: int = 1
        ):
        """
        コンストラクタ
        
        Parameters
        ----------
        base_url : str
            ComfyUI APIのベースURL
                            
        timeout_seconds : int, optional
            画像生成のタイムアウト時間（秒）。デフォルトは120秒。
            
        polling_interval : int, optional
            画像生成の進捗を確認するためのポーリング間隔（秒）。デフォルトは1秒。
        """
        super().__init__()
        
        self.base_url = base_url
        self.logger = app_logger
        self.timeout_seconds = timeout_seconds
        self.polling_interval = polling_interval
        self._configuration_client()

    def _configuration_client(self):
        """
        _configuration_clientの実装（BaseAIClientの抽象メソッドの実装）
        """
        return super()._configuration_client()
    
    def _get_image(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """
        ComfyUIから指定された画像をダウンロードする
        """

        url = f"{self.base_url}/view"
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise ComfyUIAPIError(f"Failed to download image from ComfyUI: {e}") from e

    async def _get_image_from_history(self, prompt_id: str) -> list[bytes]:
        """
        historyエンドポイントから生成された画像をダウンロードする
        """

        images_data: list[bytes] = []
        start_time = time.time()
        
        while True:
            
            # タイムアウトチェック
            if (time.time() - start_time) > self.timeout_seconds:
                raise ComfyUIAPIError(f"Timeout while waiting for image generation. Prompt ID: {prompt_id}")

            # historyエンドポイントからダウンロード対象となる画像を取得する
            history_url = f"{self.base_url}/history/{prompt_id}"
            history_response = requests.get(history_url)
            if history_response.raise_for_status() == HTTPStatus.NOT_FOUND:
                self.logger.info(f"History for prompt ID {prompt_id} not yet available. Retrying...")
                await asyncio.sleep(self.polling_interval)
                continue
            
            history_response.raise_for_status()
            history = history_response.json()
            if len(history) == 0:
                continue

            current_images = []

            # history[prompt_id]内の情報を取得
            prompt_history = history.get(prompt_id, {})
            output_nodes = prompt_history.get('outputs', {})
            
            # ワークフロー側のノード定義を取得
            workflow_nodes = prompt_history.get('prompt', {})

            for node_id, node_output in output_nodes.items():
                
                # workflow_nodesからnode_idを持つ要素を動的に探索する
                node_meta = {}

                if isinstance(workflow_nodes, list):
                    # workflow_nodesをループしてnode_idがキーとして存在する辞書を探す
                    for item in workflow_nodes:
                        if isinstance(item, dict) and node_id in item:
                            node_meta = item.get(node_id, {})
                            break
                elif isinstance(workflow_nodes, dict):
                    # 最初から辞書型で返ってきた時のフォールバック  
                    node_meta = workflow_nodes.get(node_id, {})

                # ノードのclass_typeを取得
                class_type = node_meta.get('class_type', '')

                # class_typeがSaveImage出ない場合はダウンロードせずスキップする
                if class_type != 'SaveImage':
                    continue

                if 'images' in node_output:
                    for image_info in node_output['images']:
                        filename = image_info.get('filename')
                        subfolder = image_info.get('subfolder', '')
                        folder_type = image_info.get('type', 'output')
                        
                        if filename:
                            # すでにダウンロードした画像と同じものがないかチェックする
                            try:
                                # 画像をダウンロードしてバイナリデータを取得する
                                image_bytes = self._get_image(filename, subfolder, folder_type)
                                
                                # ダウンロード済リストに無い場合のみ追加する
                                if image_bytes not in images_data:
                                    self.logger.info(f"Found image: {filename} in {subfolder}/{folder_type}")                                    
                                    current_images.append(image_bytes)
                            except ComfyUIAPIError as e:
                                self.logger.warning(f"Cloud not download image {filename}: {e}")
                        
            images_data.extend(current_images)
            if not current_images and images_data:
                self.logger.info("No new images found in history. Assuming generation is complete.")
                break

            await asyncio.sleep(self.polling_interval)
            
        # 生成された画像のバイナリデータを返す
        return images_data

    async def run_workflow(
        self, 
        workflow_data: Union[Dict[str, Any], str],
        modifications: Optional[List[NodeModification]] = None,
        **params) -> list[bytes]:
        
        """
        ComfyUI APIを呼び出してワークフローを実行する

        Parameters
        ----------
        workflow_data : Union[Dict[str, Any], str]
            ComfyUIのワークフローデータ
            辞書型、またはワークフローJOSNファイルへのパスを文字列で指定
        modifications : Optional[List[NodeModification]], optional
            ワークフローに適用するノード修正のリスト。デフォルトはNone

        Returns
        -------
        Dict[str, Any]
            生成された画像のバイナリデータとメタデータを含む辞書
            例：
            {
                "type": "image",
                "model": "ComfyUI",
                "images": [bytes],
                "metadata": {
                    "workflow": workflow_data_json,
                    "mode": "generate",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "params": params
                }
            }
            
        Raises
        ------
        ComfyUIAPIError
            API呼び出しに失敗した場合
        """
        
        workflow_data_json = workflow_data
        
        # ワークフローに修正を適用する
        if modifications:
            workflow_data_json = WorkflowEditor.apply_modifications(
                workflow_data_json, modifications
            )
        
        if isinstance(workflow_data, str):
            # ファイルパスが指定された場合
            file_path = Path(workflow_data)
            if not file_path.is_file():
                raise ComfyUIAPIError(f"Workflow JSON file not found: {workflow_data}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    workflow_data_json = json.load(f)
            
                self.logger.info(f"Loaded workflow JSON from file: {workflow_data}")
            except json.JSONDecodeError as e:
                raise ComfyUIAPIError(f"Failed to decode workflow JSON from file: {workflow_data}: {e}")            
            except IOError as e:
                raise ComfyUIAPIError(f"Failed to read workflow JSON file: {workflow_data}: {e}")
        elif isinstance(workflow_data, dict):
            # 辞書が直接指定された場合
            workflow_data_json = workflow_data
        else:
            raise ComfyUIAPIError("Invalid workflow_data type. Must be dict or a file path string.")
        
        payload = {
            "prompt": workflow_data_json,
            "client_id": str(uuid.uuid4())
        }
        
        url = f"{self.base_url}/prompt"
        headers = {"Content-Type": "application/json"}
        try:
            self.logger.info("Sending workflow to ComfyUI API.")
            response = await asyncio.to_thread(
                requests.post,
                url,
                headers=headers, 
                data=json.dumps(payload)
            )
            response.raise_for_status()
            prompt_response = response.json()

            # 生成された画像をポーリングして取得
            prompt_id = prompt_response.get('prompt_id')
            if not prompt_id:
                raise ComfyUIAPIError("ComfyUI API did not return a prompt_id.")
            self.logger.info(f"ComfyUI API prompt request successful. Prompt ID: {prompt_id}")

        except requests.exceptions.RequestException as e:
            raise ComfyUIAPIError(f"Failed to communicate with ComfyUI API: {e}") from e
        
        # historyエンドポイントから画像をダウンロードする
        images_data = await self._get_image_from_history(prompt_id)
        if not images_data:
            raise NoCandidatesError("No candidates returned.")

        result = {
            "type": "image",
            "model": params.get("model", "ComfyUI"),
            "result": images_data,
            "metadata": {
                "workflow": workflow_data_json,
                "mode": "generate",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "params": params
            }
        }
        return result