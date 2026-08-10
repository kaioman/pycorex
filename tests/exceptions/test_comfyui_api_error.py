import requests
from libcore_hng.exceptions.api_exception import ApiException
from pycorex.exceptions.comfyui_exceptions import ComfyUIAPIError

class TestComfyUIAPIError:

    def test_init_with_string_message(self):

        msg = "Failed to commnuicate with ComfyUI API: connection timeout"
        err = ComfyUIAPIError(msg)

        # 検証
        assert isinstance(err, ApiException)
        assert err.exc_type is None
        assert err.exc_value == msg
        assert "No exception captured" not in str(err)
        assert msg in str(err)

    def test_init_with_exception_object(self):

        cause_exc = requests.exceptions.RequestException("Connection refused")
        err = ComfyUIAPIError(cause_exc)

        # 検証
        assert err.exc_type == requests.exceptions.RequestException
        assert err.exc_value == cause_exc
        assert "RequestException" in str(err)
        assert "Connection refused" in str(err)

    def test_raise_and_catch_fstring_formatting(self):

        workflow_data = "workflow_v1.json"

        try:
            try:
                raise ValueError("JSON decode error")
            except ValueError as inner_e:
                raise ComfyUIAPIError(
                    f"Failed to decode workflow JSON from file: {workflow_data}: {inner_e}"
                ) from inner_e
        except Exception as e:
            error_str = f"ComfyUI API Error: {e}"

            # 検証
            assert "No exception captured" not in error_str
            assert "Failed to decode workflow JSON from file: workflow_v1.json: JSON decode error" in error_str
            assert e.exc_uuid is not None

    def test_default_init_without_args(self):

        err = ComfyUIAPIError()

        # 検証
        assert err.exc_type is None
        assert err.exc_value is None
        assert "No exception captured." in str(err)