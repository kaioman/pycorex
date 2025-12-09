import pycorex.configs.app_init as app
from pycorex.imagen_client import ImagenClient

# アプリ初期化
app.init_app(__file__, "logger.json", "pycorex.json")

# 設定クラスメンバ参照確認
print(app.core.config.vertexai.project_id)
print(app.core.config.vertexai.location)

# ImagenClientを初期化
client = ImagenClient(
    project_id=app.core.config.vertexai.project_id,
    location=app.core.config.vertexai.location
)

# プロンプトを設定
prompt = "A full body portrait of an adult woman in stylish clothing, soft lighting, studio background"

# テキスト生成を実行
response = client.generate_image_vertexai(
    prompt=prompt,
    model=ImagenClient.ImagenModel.IMAGEN_4_ULTRA,
    language=ImagenClient.AILang.EN,
    aspect_ratio=ImagenClient.AspectRatio.SQUARE,
)

# 結果を表示する
#print("=== 使用モデル ===")
#print(response["model"])
#print("\n=== 生成結果 ===")
#print(response["result"])
#print("\n=== メタ情報 ===")
#print(response["metadata"])
