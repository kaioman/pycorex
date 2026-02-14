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
prompt = "Two elegant figures with sharp, sophisticated facial features and slender proportions dance amidst a torrential downpour on a sunset beach, their voluminous hair flowing in the gale and rendered with extremely delicate fine lines. Captured in the signature premium 1980s OVA aesthetic with high-contrast cel shading and shimmering iris highlights, they wear flowing ballroom gowns that twist like silk ribbons against the crashing, high waves. The atmosphere is thick with an urban city-pop color palette, where dramatic ray-traced sunset light illuminates their messy buns and an expression of haunting vulnerability, their slender forms trembling slightly with a delicate, wide-eyed trepidation as they embrace the overwhelming majesty of the storm. Dynamic wind trails spiral around them, merging the roar of the ocean with a sophisticated, cinematic intensity that eschews soft curves for sharp, detailed precision. (safe for work, no nudity, high quality art)"

# 画像生成を実行
response = client.generate_image(
    prompt=prompt,
    model=ImagenClient.ImagenModel.IMAGEN_4_ULTRA,
    language=ImagenClient.AILang.EN,
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
