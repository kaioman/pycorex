import pycorex.configs.app_init as app
from pycorex.imagen_client import ImagenClient

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# 設定クラスメンバ参照確認
print(f"project_id={app.core.config.vertexai.project_id}")
print(f"location={app.core.config.vertexai.location}")

# ImagenClientを初期化
client = ImagenClient(
    project_id=app.core.config.vertexai.project_id,
    location=app.core.config.vertexai.location
)

# プロンプトを設定
#prompt = "A full body portrait of an adult woman in stylish clothing, soft lighting, studio background"
prompt = "複数の日本の女子が踊っている。写実的。幻想的な雰囲気"

# 画像生成を実行
response = client.generate_image_vertexai(
    prompt=prompt,
    model=ImagenClient.ImagenModel.IMAGEN_4_ULTRA,
    aspect_ratio=ImagenClient.AspectRatio.SQUARE,
    language=ImagenClient.AILang.JP,
    person_generation=ImagenClient.PersonGeneration.ALLOW_ALL,
    safety_filter_level=ImagenClient.SafetyFilterLevel.BLOCK_ONLY_HIGH
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
