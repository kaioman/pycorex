from unittest.mock import patch
import pytest
from libcore_hng.exceptions.config_exception import ConfigurationException

class TestConfigurationException:

    def test_init_does_not_trigger_log(self):
        """
        コンストラクタの初期化のみでログ出力が実行されないことを検証
        """
        with patch("libcore_hng.utils.app_logger.error") as mock_logger_error, \
             patch("libcore_hng.utils.app_logger.logger_config", True):
            # インスタンス化のみ実行
            err = ConfigurationException("Test error message")

            # 検証
            mock_logger_error.assert_not_called()
            assert err.exc_value == "Test error message"

    def test_explicit_log_method_triggers_log(self):
        """
        .log()メソッドを明示的に呼び出した際にログ出力が実行されることを検証
        """
        with patch("libcore_hng.utils.app_logger.error") as mock_logger_error, \
             patch("libcore_hng.utils.app_logger.logger_config", True):
            # 明示的にlog()を呼び出す
            err = ConfigurationException("Test error message")
            result = err.log()

            # 検証
            assert mock_logger_error.called
            assert result is err

    def test_method_chaining_on_raise(self):
        """
        raise Exception().log() のチェーン呼び出しで正しく例外が送出されログ出力されるか検証
        """
        msg = "Configuration raise failed"

        with patch("libcore_hng.utils.app_logger.error") as mock_logger_error, \
             patch("libcore_hng.utils.app_logger.logger_config", True):
            with pytest.raises(ConfigurationException) as exc_info:
                # 実際の運用コードでの書き方で実行
                raise ConfigurationException(msg).log()

            # 検証
            captured_err = exc_info.value
            assert msg in str(captured_err)
            assert mock_logger_error.called

    def test_log_method_returns_self_for_chaining(self):
        """
        log()メソッドがselfを返すことでraiseにそのまま渡せるか検証
        """
        err = ConfigurationException("Chain test")
        chaining_obj = err.log()

        assert chaining_obj is err