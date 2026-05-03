from abc import ABC, abstractmethod
from pycorex.models.prompt import PromptContextModel
from pycorex.enums.rating_level import RatingLevel

class BasePromptGenerator(ABC):
    """
    すべてのプロンプトジェネレーターの抽象基底クラス。
    モデル固有のプロンプト生成ロジックを実装するための共通インターフェースを定義します。
    """
    
    @abstractmethod
    def generate_prompt(self, level: RatingLevel, target_scene_id: str | None = None) -> PromptContextModel:
        """
        指定されたレベルとシーンIDに基づき、ポジティブおよびネガティブプロンプトを生成します。

        Parameters
        ----------
        level : RatingLevel
            生成するプロンプトのレベル。高レベルほど詳細なプロンプトが生成される場合があります。
        target_scene_id : str, optional
            特定のシーンID。指定された場合、そのシーンに特化したプロンプトが生成されます。

        Returns
        -------
        PromptContextModel
            プロンプトコンテキストモデルを返します。
        """
        pass