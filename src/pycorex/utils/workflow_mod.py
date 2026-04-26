import json
import random
from typing import List, Dict, Union, Any, Optional
from pathlib import Path
from pycorex.utils.workflow_editor import NodeModification
from pycorex.models.prompt import PromptContextModel


class WorkflowMod:
    """
    汎用ワークフロー修正設定クラス（JSON設定ベース）
    """
    
    @staticmethod
    def load_mod_config(mod_config: Union[Dict[str, Any], str]) -> dict:
        """
        JSONから修正設定を読み込む
        
        Parameters
        ----------
        mod_config : Union[Dict[str, Any]
            ワークフロー変更設定
        
        Returns
        -------
        dict
            修正設定
        """
        if isinstance(mod_config, dict):
            return mod_config
        
        if isinstance(mod_config, str):
            path = Path(mod_config)
            if not path.exists():
                raise FileNotFoundError(f"設定ファイルが見つかりません: {mod_config}")
            
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    @staticmethod
    def _evaluate_condition(condition: Dict[str, Any]) -> Optional[callable]:
        """
        JSONの条件定義をLambda関数に変換
        
        例: {"class_type": "CLIPTextEncode"} 
        → lambda node: node.get("class_type") == "CLIPTextEncode"
        
        複数条件の場合、全てがマッチする必要がある（AND結合）
        
        Parameters
        ----------
        condition : Dict[str, Any]
            条件の辞書
        
        Returns
        -------
        Optional[callable]
            条件チェック関数、または None
        """
        if not condition:
            return None
        
        def condition_func(node: Dict[str, Any]) -> bool:
            for key, value in condition.items():
                if node.get(key) != value:
                    return False
            return True
        
        return condition_func
    
    @staticmethod
    def _interpolate_values(
        mods: dict,
        prompt_context: PromptContextModel,
        batch_size: int
    ) -> dict:
        """
        JSONの値をPromptContextの実際の値に置換
        
        サポートされるプレースホルダー:
        - ${positive_prompt}
        - ${negative_prompt}
        - ${image_width}
        - ${image_height}
        - ${batch_size}
        - ${random_seed}
        - ${属性名} - PromptContextの任意の属性
        
        Parameters
        ----------
        mods : dict
            修正内容の辞書
        prompt_context : PromptContextModel
            プロンプトコンテキスト
        batch_size : int
            バッチサイズ
        
        Returns
        -------
        dict
            置換後の修正内容
        """
        result = {}
        for key, value in mods.items():
            if isinstance(value, dict):
                # ネストされた辞書は再帰的に処理
                result[key] = WorkflowMod._interpolate_values(
                    value, prompt_context, batch_size
                )
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # プレースホルダーの処理
                placeholder = value[2:-1]  # "${...}" から "..." を抽出
                
                if placeholder == "random_seed":
                    result[key] = random.randint(1, 1125899906842624)
                elif placeholder == "batch_size":
                    result[key] = batch_size
                elif hasattr(prompt_context, placeholder):
                    result[key] = getattr(prompt_context, placeholder)
                else:
                    # プレースホルダーが見つからない場合は元の値のまま
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def create_modifications(
        prompt_context: PromptContextModel,
        mod_config: Union[Dict[str, Any], str],
        batch_size: int = 1
    ) -> List[NodeModification]:
        """
        JSONから読み込んだ設定に基づいてNodeModificationリストを作成
        
        Parameters
        ----------
        prompt_context : PromptContextModel
            生成されたプロンプトコンテキスト
        mod_config : Union[Dict[str, Any]
            ワークフロー変更設定
        batch_size : int
            バッチサイズ
        
        Returns
        -------
        List[NodeModification]
            ワークフロー修正リスト
        """
        mod_config_dict = WorkflowMod.load_mod_config(mod_config)
        modifications = []
        
        for mcd in mod_config_dict.get("modifications", []):
            node_id = mcd["node_id"]
            mods = mcd.get("modifications", {})
            condition_config = mcd.get("condition")
            
            # プロンプトやバッチサイズなどを動的に置換
            mods = WorkflowMod._interpolate_values(
                mods, prompt_context, batch_size
            )
            
            # 条件を動的に生成
            condition = None
            if condition_config:
                condition = WorkflowMod._evaluate_condition(condition_config)
            
            modifications.append(
                NodeModification(
                    node_id=node_id,
                    modifications=mods,
                    condition=condition
                )
            )
        
        return modifications