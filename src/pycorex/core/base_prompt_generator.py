from abc import ABC, abstractmethod
from enum import IntEnum
from pycorex.models.prompt import PromptContextModel

class BasePromptGenerator(ABC):
    """
    すべてのプロンプトジェネレーターの抽象基底クラス。
    モデル固有のプロンプト生成ロジックを実装するための共通インターフェースを定義します。
    """

    class RatingLevel(IntEnum):
        """
        Ratingレベルの列挙体
        高レベルほどセンシティブな内容を含むプロンプトが生成される可能性がある
        """
        
        SAFE = 1
        """ 健全な内容 """

        EMOTIVE = 2
        """ 少しだけ情緒的(フェティッシュなニュアンス) """

        QUESTIONABLE = 3
        """ 下着露出、胸チラなどのギリギリの内容 """

        EXPLICIT = 4
        """ ハードコア一歩手前 """

        LIMITLESS = 5
        """ 制限なし。ナイトメアレベル """
    
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