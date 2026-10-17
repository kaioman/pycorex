import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from pycorex.comfyui_client import ComfyUIClient
from pycorex.utils.pony_prompt_generator import PonyPromptGenerator


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "faceid_reference_images_urls.json"


class TestFaceIDReferenceImages:
    def test_resolve_faceid_image_paths_preserves_urls_and_resolves_local_paths(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
            config = json.load(fixture_file)

        generator = PonyPromptGenerator.__new__(PonyPromptGenerator)
        resolved = generator._resolve_faceid_image_paths(
            config=config,
            config_path=str(FIXTURE_PATH),
            persona_dir=str(FIXTURE_PATH.parent),
        )

        expected_local_path = str(FIXTURE_PATH.parent / "faceid" / "local_reference.png")
        assert resolved["load_image_nodes"]["9"] == expected_local_path
        assert resolved["load_image_nodes"]["41"] == (
            "https://example.com/remote%20reference.png"
        )
        assert resolved["color_match"]["image"] == (
            "http://example.com/color-match.png?variant=1"
        )


class TestComfyUIUploadImage:
    @staticmethod
    def create_client() -> ComfyUIClient:
        client = ComfyUIClient.__new__(ComfyUIClient)
        client.base_url = "http://comfyui.test"
        client.timeout_seconds = 5
        return client

    def test_upload_image_downloads_remote_url_before_uploading(self):
        client = self.create_client()
        download_response = MagicMock(
            content=b"remote-image",
            headers={"Content-Type": "image/png; charset=binary"},
        )
        upload_response = MagicMock()
        upload_response.json.return_value = {"name": "remote_reference.png"}

        with (
            patch(
                "pycorex.comfyui_client.requests.get",
                return_value=download_response,
            ) as get_mock,
            patch(
                "pycorex.comfyui_client.requests.post",
                return_value=upload_response,
            ) as post_mock,
        ):
            result = asyncio.run(
                client.upload_image(
                    "https://example.com/remote%20reference.png?variant=1"
                )
            )

        assert result == "remote_reference.png"
        get_mock.assert_called_once_with(
            "https://example.com/remote%20reference.png?variant=1",
            timeout=5,
        )
        download_response.raise_for_status.assert_called_once_with()
        upload_response.raise_for_status.assert_called_once_with()
        post_mock.assert_called_once()
        upload_kwargs = post_mock.call_args.kwargs
        assert upload_kwargs["data"] == {"overwrite": "true"}
        assert upload_kwargs["timeout"] == 5
        assert upload_kwargs["files"]["image"] == (
            "remote reference.png",
            b"remote-image",
            "image/png",
        )

    def test_upload_image_keeps_local_path_upload_behavior(self, tmp_path):
        client = self.create_client()
        image_path = tmp_path / "local_reference.png"
        image_path.write_bytes(b"local-image")
        upload_response = MagicMock()
        upload_response.json.return_value = {
            "name": "local_reference.png",
            "subfolder": "faceid",
        }

        uploaded_content = {}

        def capture_upload(*args, **kwargs):
            uploaded_file = kwargs["files"]["image"][1]
            uploaded_content["bytes"] = uploaded_file.read()
            return upload_response

        with patch(
            "pycorex.comfyui_client.requests.post",
            side_effect=capture_upload,
        ) as post_mock:
            result = asyncio.run(client.upload_image(image_path))

        assert result == "faceid/local_reference.png"
        post_mock.assert_called_once()
        uploaded_file = post_mock.call_args.kwargs["files"]["image"][1]
        assert uploaded_file.closed
        assert uploaded_content["bytes"] == b"local-image"