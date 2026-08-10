import os
import pytest
from pycorex.configs.initialize_app import config
from pycorex.gemini_client import GeminiClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

class TestRequestGemini:

    def test_request_gemini_api(self):
        self.main()

    def main(self):

        # GeminiClientを初期化
        client = GeminiClient(
            api_key=config.gemini.api_key,
            project_id=config.vertexai.project_id,
            location=config.vertexai.location
        )

        # プロンプトを設定
        prompt = "リクルートスーツの女性が居酒屋で酒をあおっている。"

        try:
            # 画像生成を実行　
            response = client.generate_image(
                prompt=prompt,
                model=GeminiClient.GeminiModel.GEMINI_2_5_FLASH_IMAGE,
                aspect_ratio=GeminiClient.AspectRatio.WIDE,
                image_size=GeminiClient.ImageSize.TWO_K,
                harm_category = GeminiClient.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                safety_filter_level = GeminiClient.SafetyFilterLevel.BLOCK_ONLY_HIGH
            )
            
            # 画像ファイルを出力する
            for _, image_bytes in enumerate(response["result"]):
                file_name = client.get_gen_filename()
                image_path = os.path.join("gen_images", file_name)
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Saved: {image_path}")

            # 結果を表示する
            print("=== 使用モデル ===")
            print(response["model"])
            print("\n=== メタ情報 ===")
            print(response["metadata"])

        except NoCandidatesError as e:
            pytest.fail(f"Image generation failed: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_obj = TestRequestGemini()
    test_obj.test_request_gemini_api()
