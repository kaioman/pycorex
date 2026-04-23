# PonyPromptGenerator 設計書

## 1. 概要

`PonyPromptGenerator` クラスは、Pony モデル専用の txt2img (text-to-image) 用ランダムプロンプトジェネレーターです。persona に基づくコアなアイデンティティタグ、衣装の抽選、シーンロジック、カメラアングル、環境要素を組み合わせて、指定されたレベルに応じたプロンプトを生成します。これにより、多様なシチュエーションやキャラクター表現に対応した高品質な画像を効率的に生成することを目指します。

## 2. クラス構造

### `PonyPromptGenerator(BasePromptGenerator)`

`BasePromptGenerator` を継承し、Pony モデルに特化したプロンプト生成ロジックを実装します。

#### メソッド

* `__init__`
  * **説明**: クラスの初期化を行います。各種設定ファイルのパスを受け取り、JSONデータをロードします。
  * **引数**:
    * `persona_path` (str): ペルソナ設定ファイルへのパス。デフォルト: `tests/prompt/pony/persona/Aoi.json`
      * `camera_path` (str): カメラアングル設定ファイルへのパス。デフォルト: `tests/prompt/pony/camera_angules.json`
      * `wardrobe_path` (str): 衣装設定ファイルへのパス。デフォルト: `tests/prompt/pony/wardrobe.json`
      * `environment_path` (str): 環境設定ファイルへのパス。デフォルト: `tests/prompt/pony/environments.json`
    * **ロードされるデータ**:
      * `self.environment_data`: 環境データ (`environments.json`)
      * `self.data`: ペルソナデータ (`Aoi.json`)
      * `self.camera_data`: カメラアングルデータ (`camera_angules.json`)
      * `self.wardrobe_data`: 衣装データ (`wardrobe.json`)

* `_load_json(self, path: str) -> dict[str, Any]`
  * **説明**: 指定されたパスから JSON ファイルを安全にロードするプライベートメソッドです。ファイルが存在しない場合は `FileNotFoundError` を発生させます。

* `_pick_weighted_item(self, item_list: list[dict], current_level: int, target_id: Optional[str] = None) -> Optional[dict]`
  * **説明**: アイテムリストから、`min_lv`, `max_lv` の範囲内かつ `weight` に基づいてアイテムを抽選する共通ロジックです。`target_id` が指定された場合は、その ID に合致するアイテムを返します。

* `_get_environment_tags(self, scene_tags: str, outfit_id: str) -> str`
  * **説明**: シーンタグに `location`, `lighting`, `texture` のタグが含まれていない場合に、環境データ (`self.environment_data`) から互換性のあるアイテムを抽選し、タグを取得します。

* `_get_specific_env_tag(self, scene_tags: str, env_list: list[dict], outfit_id: str) -> Optional[str]`
  * **説明**: シーンタグに既存の環境要素が含まれていないかチェックし、互換性のあるアイテムをフィルタリングしてからランダムにタグを抽選するプライベートメソッドです。

* `_get_base_identity(self) -> dict[str, Any]`
  * **説明**: ペルソナデータ (`self.data`) の `body_parts` セクションを再帰的に処理し、カテゴリごとのタグを収集して `base_identity_tags` として統合します。

* `generate_prompt(self, level: BasePromptGenerator.RatingLevel, target_scene_id: Optional[str] = None, test_outfit_id: Optional[str] = None, test_scene_id_override: Optional[str] = None, test_camera_name: Optional[str] = None) -> tuple[str, str, int, int]`
  * **説明**: 指定されたレベルに基づき、画風を維持したポジティブプロンプトとネガティブプロンプトを生成します。テスト用のオプション引数も提供されています。
    * **引数**:
      * `level` (BasePromptGenerator.RatingLevel): 生成するプロンプトのレベル。
      * `target_scene_id` (str, optional): 特定のシーンID。指定された場合、そのシーンに特化したプロンプトが生成されます。
      * `test_outfit_id` (str, optional): テスト用の衣装ID。
      * `test_scene_id_override` (str, optional): `target_scene_id` とは別にテスト用のシーンID。
      * `test_camera_name` (str, optional): テスト用のカメラアングル名。
    * **戻り値**:
      * `tuple[str, str, int, int]`: ポジティブプロンプト、ネガティブプロンプト、画像の幅、画像の高さのタプル。

## 3. 設定ファイルの詳細

### `configs/comfyui_config.json`

ComfyUI との連携に関する設定を定義します。

```json
{
    "comfyui": {
        "comfyui_endpoint": "http://127.0.0.1:8188",
        "workflow_path": "tests/comfyui_workflow/aoi-IPAdapter9.json",
        "timeout_seconds": 120,
        "polling_interval": 1
    }
}
```

* `comfyui_endpoint`: ComfyUI の API エンドポイントURL。
* `workflow_path`: 使用する ComfyUI ワークフローのJSONファイルへのパス。
* `timeout_seconds`: API リクエストのタイムアウト時間 (秒)。
* `polling_interval`: API のポーリング間隔 (秒)。

### `tests/prompt/pony/persona/Aoi.json`

キャラクターのペルソナに関する詳細な設定を定義します。表情、身体的特徴、基本的なスタイル、ネガティブプロンプトの聖域などが含まれます。この例ではキャラクター名をペルソナ設定ファイルにしています。

* `name`: キャラクター名。
* `rating`: プロンプトのレベルに応じたレーティングタグ。
* `base_score_tags`: 品質に関するベーススコアタグ。
* `base_identity_tags`: 基本的なアイデンティティタグ。
* `body_parts`: 髪、瞳、アクセサリーなどの身体的特徴を定義し、それぞれに対応するタグを持つ。
  * `hair`: 髪の色や長さ。
  * `eyes`: 瞳の色。
  * `accesories`: 頭部や首のアクセサリー。
* `base_style`: 基本的な画風。例: 80年代レトロアニメスタイル。
* `negative_holy_grail`: 全レベル共通で適用されるネガティブプロンプトの「聖域」。
* `innerwear_thresholds`: 各レベルにおけるインナーウェア出現の抽選閾値。
* `scene_logic`: シーンに関する詳細なロジック。各シーンアイテムは ID、説明、タグ、レベル範囲、重み、衣服破壊の有無、インナーウェアの露出設定などを持つ。
  * `items`: 個々のシーン定義のリスト。
* `negative_logic`: ネガティブプロンプトに関するロジック。レベルに応じた追加の拒絶要素を定義。
  * `items`: 個々のネガティブロジック定義のリスト。
* `expression_logic`: 表情に関するロジック。レベルに応じた表情のタグや説明を定義。
  * `emotional_range`: 表情定義のリスト。

### `tests/prompt/pony/camera_angules.json`

様々なカメラアングルに関する設定を定義します。各アングルには ID、名称、推奨解像度、説明、関連するタグ、雰囲気、最適なレベルが含まれます。

* `camera_angles`: カメラアングル定義のリスト。
  * `id`: カメラアングルの一意なID。
  * `name`: カメラアングルの名称。例: 「斜め構図（ダッチアングル）」
  * `suggested_resolution`: そのアングルに推奨される画像の幅と高さ。
  * `description`: カメラアングルの説明と意図。
  * `tags`: そのアングルを表現するためのプロンプトタグ。
  * `vibe`: そのアングルが持つ雰囲気。例: `dramatic`, `intimate`
  * `best_for`: そのアングルが最適なレベル。

### `tests/prompt/pony/environments.json`

ロケーション、ライティング、テクスチャなどの環境要素に関する設定を定義します。各要素には ID、タグ、説明、互換性のない衣装 (`not_compatible_outfits`) が含まれます。

* `locations`: ロケーション定義のリスト。
  * `id`: ロケーションの一意なID。
  * `tags`: ロケーションを表現するためのプロンプトタグ。
  * `description`: ロケーションの説明。
  * `not_compatible_outfits`: そのロケーションと互換性のない衣装のIDリスト。
* `lightings`: ライティング定義のリスト。
  * `id`: ライティングの一意なID。
  * `tags`: ライティングを表現するためのプロンプトタグ。
  * `description`: ライティングの説明。
  * `not_compatible_outfits`: そのライティングと互換性のない衣装のIDリスト。
* `textures`: テクスチャ定義のリスト。
  * `id`: テクスチャの一意なID。
  * `tags`: テクスチャを表現するためのプロンプトタグ。
  * `description`: テクスチャの説明。
  * `not_compatible_outfits`: そのテクスチャと互換性のない衣装のIDリスト。

### `tests/prompt/pony/wardrobe.json`

衣装、インナーウェア、破壊可能な衣服のベースタグなどを定義します。衣装には ID、タグ、雰囲気、レベル範囲、破壊可能フラグ、パーツ、互換性のないシーンロジック、破壊タグキー、アウタータグなどが含まれます。

* `colors`: 衣装にランダムに適用される可能性のある色のリスト。
* `destructible_base_tags`: 衣服破壊時に適用されるベースタグの定義。`normal` キーの下に破壊表現のタグリストを持つ。
* `outfits`: 衣装定義のリスト。
  * `id`: 衣装の一意なID。
  * `tags`: 衣装を表現するためのプロンプトタグ。`{color}` プレースホルダーを含む場合がある。
  * `vibe`: 衣装が持つ雰囲気。
  * `min_lv`, `max_lv`: 衣装が利用可能なレベル範囲。
  * `destructible`: 衣服破壊が可能かどうかを示すブール値。
  * `parts`: 衣装を構成するパーツのリスト。
  * `incompatible_scene_logic`: その衣装と互換性のないシーンロジックのIDリスト。
  * `destructible_tags_key`: 衣服破壊時に使用する `destructible_base_tags` のキー。
  * `outer_tags`: 衣装のアウター部分のタグ（例: `top`, `bottom`, `socks`）。
  * `conflict_outfits`: 特定のカテゴリにおける競合タグの解決ロジック。
* `innerwear_sets`: インナーウェアのスタイル定義のリスト。
  * `styles`: 個々のインナーウェアスタイル定義のリスト。
    * `id`: インナーウェアスタイルの一意なID。
    * `tags`: インナーウェアを表現するためのプロンプトタグ。`top`, `bottom` などのキーを持つ。
    * `vibe`: インナーウェアが持つ雰囲気。
    * `min_lv`: インナーウェアが利用可能な最低レベル。
