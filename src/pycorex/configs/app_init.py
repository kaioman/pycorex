import warnings
from libcore_hng.utils.app_core import AppInitializer
from pycorex.configs.pycorex import PyCorexConfig

class PyCorexAppInitializer(AppInitializer[PyCorexConfig]):
    """
    AppInitializer拡張クラス
    """
    def __init__(self, base_file: str = __file__, *config_file: str):
        # 基底コンストラクタに拡張Configクラスを渡す
        super().__init__(PyCorexConfig, base_file, *config_file)

core: PyCorexAppInitializer | None = None
""" AppInitializer拡張クラスインスタンス """

def init_app(base_file: str = __file__, *config_file: str) -> PyCorexAppInitializer:
    """
    アプリケーション初期化
    """

    warnings.warn(
        "`init_app()` は非推奨です。代わりに `initialize_app()` を使用してください。",
        DeprecationWarning,
        stacklevel=2
    )
    global core
    core = PyCorexAppInitializer(base_file, *config_file)
    return core
