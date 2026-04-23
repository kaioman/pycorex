# pycorex - AI API統合のための軽量Pythonコアパッケージ

統一されたAI APIアクセスとスケーラブルなアプリケーション構築を支援する軽量Pythonコアパッケージ。

## 概要

`pycorex` は、Google Gemini, Imagen, ComfyUI など多様なAI APIおよびライブラリへのアクセスを統合し、スケーラブルなPythonアプリケーションを迅速に構築するための軽量なコア・ユーティリティライブラリです。本パッケージは、プロンプト生成、画像生成、AIモデルとの連携など、複雑なAIワークフローを効率的に管理するための機能を提供します。
アプリケーションの初期化や設定管理については、親プロジェクトである `libcore-hng`（[https://github.com/kaioman/libcore-hng.git](https://github.com/kaioman/libcore-hng.git)）を参照してください。

## 主な機能

- **統一されたAIクライアント**: Google Gemini, Imagen, ComfyUI など、主要なAIサービスへの統一されたインターフェースを提供します（随時追加予定）
- **高度なプロンプト生成**: 柔軟なテンプレートと設定に基づいたプロンプト生成機能により、AIモデルの性能を最大限に引き出します。
- **画像生成ワークフローの管理**: ComfyUIとの連携により、複雑な画像生成ワークフローをPythonコードから直接制御できます。
- **拡張性とモジュール性**: 新しいAIサービスや機能を追加しやすいモジュール構造を採用しています。

## インストール

`pycorex` は `pip` を使ってインストールできます。

```bash
pip install pycorex
```

## 使い方

基本的な使用例を以下に示します。

### GeminiClient の使用例

```python
import pycorex.configs.app_init as app
from pycorex.gemini_client import GeminiClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

# アプリ初期化
app.init_app(__file__, "app_config.json", "gcp_config.json", "pycorex.json.enc")

# GeminiClientを初期化
client = GeminiClient(
    api_key=app.core.config.gemini.api_key_vertexai,
    project_id=app.core.config.vertexai.project_id,
    location=app.core.config.vertexai.location
)

# プロンプトを設定
prompt = "リクルートスーツの女性が居酒屋で酒をあおっている"

# 画像生成を実行　
response = client.generate_image(
    prompt=prompt,
    model=GeminiClient.GeminiModel.GEMINI_3_0_PRO_IMAGE_PREVIEW,
    aspect_ratio=GeminiClient.AspectRatio.SQUARE,
    image_size=GeminiClient.ImageSize.TWO_K,
    harm_category = GeminiClient.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    safety_filter_level = GeminiClient.SafetyFilterLevel.BLOCK_ONLY_HIGH
)

# 画像ファイルを出力する
for idx, image_bytes in enumerate(response["result"]):
    with open(f"image_{idx}.png", "wb") as f:
        f.write(image_bytes)
    print(f"Saved: image_{idx}.png")
```

### プロンプト生成の例

```python
import pycorex.configs.app_init as app
from pycorex.utils.pony_prompt_generator import PonyPromptGenerator

# アプリ初期化
app.init_app(__file__, "app_config.json", "gcp_config.json", "pycorex.json.enc")

# PonyPromptGeneratorのインスタンスを作成
pony_generator = PonyPromptGenerator(
    persona_path="tests/prompt/pony/persona/Aoi.json",
    camera_path="tests/prompt/pony/camera_angules.json",
    wardrobe_path="tests/prompt/pony/wardrobe.json",
    environment_path="tests/prompt/pony/environments.json"
)

# プロンプトを生成
positive_prompt, negative_prompt, image_width, image_height = self.prompt_generator.generate_prompt(
    level=prompt_level,
    target_scene_id=target_scene_id,
    test_outfit_id=test_outfit_id,
    test_scene_id_override=test_scene_id_override,
    test_camera_name=test_camera_name,
)

print(f"Generated Positive Prompt: {positive_prompt[:100]}...")
print(f"Generated Negative Prompt: {negative_prompt[:100]}...")
print(f"Generated Image Resolution: {image_width}x{image_height}")

```

## 開発

リポジトリをクローンし、開発環境をセットアップする方法です。

```bash
git clone https://github.com/kaioman/pycorex.git
cd pycorex
```

## 貢献

貢献を歓迎します！バグ報告や機能提案、プルリクエストをお待ちしております。

## ライセンス

このプロジェクトは `BSD-3-Clause` ライセンスの下で公開されています。詳細については `LICENSE` ファイルをご覧ください。
