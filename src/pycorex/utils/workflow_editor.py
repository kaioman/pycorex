from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable

@dataclass
class NodeModification:
    """
    ワークフローのノード修正を定義
    """
    
    node_id: str
    """ ノードID """
    modifications: Dict[str, Any]
    """ パラメーター修正内容 {"inputs": {"text": "新しいプロンプト" }}など """
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    """ オプション:条件付き適用"""

    def apply(self, workflow: Dict[str, Any]) -> bool:
        """
        ワークフローにノード修正を適用する
        
        Parameters
        ----------
        workflow : Dict[str, Any]
            ワークフローデータ

        Returns
        -------
        bool
            修正が適用されたかどうか
        """
        
        # ノードIDがワークフロー内に存在するか確認
        if self.node_id not in workflow:
            return False
        
        # 対象のノード取得
        node = workflow[self.node_id]
            
        # 条件が指定されている場合はチェック
        if self.condition and not self.condition(node):
            return False

        # ワークフローに修正を適用する
        for key, value in self.modifications.items():
            if key == "inputs" and isinstance(value, dict):
                node["inputs"].update(value)
            else:
                node[key] = value
        
        return True
    
class WorkflowEditor:
    """
    ComfyUIワークフロー編集ユーティリティクラス
    """
    
    @staticmethod
    def apply_modifications(
        workflow: Dict[str, Any],
        modifications: List[NodeModification]
    ) -> Dict[str, Any]:
        """
        ワークフローに修正を適用する
        
        Parameters
        ----------
        workflow : Dict[str, Any]
            ワークフローデータ
        modifications : List[NodeModification]
            修正リスト

        Returns
        -------
        Dict[str, Any]
            修正が適用されたワークフローデータ
        """
        
        # ワークフロー内のノードを走査して修正を適用
        applied_count = 0
        for modification in modifications:
            if modification.apply(workflow):
                applied_count += 1

        return workflow

    @staticmethod
    def set_node_input(
        workflow: Dict[str, Any], 
        node_id: str, 
        input_name: str,
        value: Any
    ) -> Dict[str, Any]:
        """
        ノードの入力値を設定する

        Parameters
        ----------
        workflow : Dict[str, Any]
            ワークフローデータ
        node_id : str
            ノードID
        input_name : str
            入力名
        value : Any
            設定する値

        Returns
        -------
        Dict[str, Any]
            修正が適用されたワークフローデータ
        """
        
        if node_id in workflow and "inputs" in workflow[node_id]:
            workflow[node_id]["inputs"][input_name] = value
        return workflow
    
    def find_nodes_by_type(
        workflow: Dict[str, Any],
        class_type: str
    ) -> Dict[str, Any]:
        """
        ワークフロー内の特定のクラスのノードを検索する
        
        Parameters
        ----------
        workflow : Dict[str, Any]
            ワークフローデータ
        class_type : str
            クラス名

        Returns
        -------
        Dict[str, Any]
            クラスに一致するノードIDとノードデータの辞書
        """
        
        return {
            node_id: node_data
            for node_id, node_data in workflow.items()
            if node_data.get("class_type") == class_type
        }