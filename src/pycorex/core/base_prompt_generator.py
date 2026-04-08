from abc import ABC, abstractmethod

class BasePromptGenerator(ABC):
    """
    すべてのプロンプトジェネレーターの抽象基底クラス。
    モデル固有のプロンプト生成ロジックを実装するための共通インターフェースを定義します。
    """

    @abstractmethod
    def generate_prompt(self, level: int, target_scene_id: str | None = None) -> tuple[str, str]:
        """
        指定されたレベルとシーンIDに基づき、ポジティブおよびネガティブプロンプトを生成します。

        Parameters
        ----------
        level : int
            生成するプロンプトのレベル。高レベルほど詳細なプロンプトが生成される場合があります。
        target_scene_id : str, optional
            特定のシーンID。指定された場合、そのシーンに特化したプロンプトが生成されます。

        Returns
        -------
        tuple[str, str]
            ポジティブプロンプトとネガティブプロンプトのタプルを返します。
        """
        pass