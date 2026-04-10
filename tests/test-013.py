import io
import pycorex.configs.app_init as app
from PIL import Image as PIL_image
from pycorex.imagen_client import ImagenClient
from google.genai import types

# アプリ初期化
app.init_app(__file__, "app_config.json", "pycorex.json.enc")

# 設定クラスメンバ参照確認
print(f"project_id={app.core.config.vertexai.project_id}")
print(f"location={app.core.config.vertexai.location}")

# ImagenClientを初期化
client = ImagenClient(
    project_id=app.core.config.vertexai.project_id,
    location=app.core.config.vertexai.location
)

# プロンプトを設定
prompt = "クリスマスコスチュームを着た姿に変えてください。ポーズも大胆に変えて。表情は楽し気な感じ"

# 画像ファイルをImageFile型で取得
base_image = PIL_image.open("tests/source_image/00109-2381410371.png")
img_byte_arr = io.BytesIO()
base_image.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()
sdk_image = types.Image(image_bytes=img_bytes, mime_type="image/png")

raw_ref_image = types.RawReferenceImage(
    reference_image=sdk_image,
    reference_id=0
)

# 画像生成を実行
response = client.edit_image(
    base_image=[raw_ref_image],
    prompt=prompt,
    model=ImagenClient.ImagenModel.IMAGEN_3_CAPABILITY,
    language=ImagenClient.AILang.JP,
    aspect_ratio=ImagenClient.AspectRatio.SQUARE,
)

# 画像ファイルを出力する
for idx, image_bytes in enumerate(response["result"]):
    with open(f"image_{idx}.png", "wb") as f:
        f.write(image_bytes)
    print(f"Saved: image_{idx}.png")

# 結果を表示する
print("=== 使用モデル ===")
print(response["model"])
print("\n=== メタ情報 ===")
print(response["metadata"])
