import random
from typing import List
from pycorex.utils.workflow_editor import NodeModification
from pycorex.models.prompt import PromptContextModel

class AoiWorkflowMod:
    """
    Aoi生成ワークフロー修正設定クラス（テスト用サンプル）
    """
    
    def create_modifications(
        prompt_context: PromptContextModel,
        batch_size: int = 1
    ) -> List[NodeModification]:
        """
        Aoi生成ワークフロー用の修正リストを作成する
        
        Parameters
        ----------
        prompt_context : PromptContextModel
            生成されたプロンプトコンテキスト
        batch_size : int
            バッチサイズ
        
        Returns
        -------
        List[NodeModification]
            ワークフロー修正リスト
        """
        return [
            # CLIPTextEncodeノードのポジティブプロンプト(node_id="12")
            NodeModification(
                node_id="12",
                modifications={
                    "inputs": {"text": prompt_context.positive_prompt}
                },
                condition=lambda node: node.get("class_type") == "CLIPTextEncode"
            ),
            # CLIPTextEncodeノードのネガティブプロンプト(node_id="13")
            NodeModification(
                node_id="13",
                modifications={
                    "inputs": {"text": prompt_context.negative_prompt}
                },
                condition=lambda node: node.get("class_type") == "CLIPTextEncode"
            ),
            # EmptyLatentImageノード(node_id="6")
            NodeModification(
                node_id="6",
                modifications={
                    "inputs": {
                        "width": prompt_context.image_width,
                        "height": prompt_context.image_height,
                        "batch_size": batch_size
                    }
                },
                condition=lambda node: node.get("class_type") == "EmptyLatentImage"
            ),
            # KSamplerノード(node_id="5")
            NodeModification(
                node_id="5",
                modifications={
                    "inputs": {"seed": random.randint(1, 1125899906842624)}
                },
                condition=lambda node: node.get("class_type") == "KSampler"
            )
        ]