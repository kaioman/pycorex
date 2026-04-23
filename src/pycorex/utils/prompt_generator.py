from typing import Type, Dict, Any
from pycorex.core.base_prompt_generator import BasePromptGenerator

class PromptGenerator:
    """
    様々なモデルのプロンプトジェネレーターを管理するファクトリクラス。
    設定に基づいて適切なプロンプトジェネレーターのインスタンスを生成して提供する
    """

    _generators: Dict[str, Type[BasePromptGenerator]] = {}

    @classmethod
    def register_generator(cls, name: str, generator_class: Type[BasePromptGenerator]):
        """
        プロンプトジェネレータークラスを登録します。

        Parameters
        ----------
        name : str
            ジェネレーターを一意に識別する名前 (例: "pony", "sdxl")。
        generator_class : Type[BasePromptGenerator]
            登録するプロンプトジェネレーターのクラス。
        """
        if not issubclass(generator_class, BasePromptGenerator):
            raise ValueError("generator_class は BasePromptGenerator を継承している必要があります。")
        cls._generators[name] = generator_class

    @classmethod
    def get_generator(cls, name: str, **kwargs: Any) -> BasePromptGenerator:
        """
        登録されているプロンプトジェネレーターのインスタンスを取得する

        Parameters
        ----------
        name : str
            取得するジェネレーターの名前。
        **kwargs : Any
            ジェネレーターのコンストラクタに渡すキーワード引数。

        Returns
        -------
        BasePromptGenerator
            指定された名前のプロンプトジェネレーターのインスタンス。

        Raises
        ------
        ValueError
            指定された名前のジェネレーターが登録されていない場合。
        """
        generator_class = cls._generators.get(name)
        if not generator_class:
            raise ValueError(f"ジェネレーター '{name}' は登録されていません。")
        return generator_class(**kwargs)

# 例: PonyPromptGeneratorを登録
# from .pony_prompt_generator import PonyPromptGenerator # 循環参照を避けるため、実際の使用時には動的インポートまたは外部からの登録を推奨

# 動的インポートの例 (必要に応じて)
# def _load_builtin_generators():
#     from .pony_prompt_generator import PonyPromptGenerator
#     PromptGenerator.register_generator("pony", PonyPromptGenerator)
# _load_builtin_generators()


