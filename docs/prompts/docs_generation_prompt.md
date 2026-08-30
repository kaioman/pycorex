GitHub Copilot として、このリポジトリを対象に作業してください。

プロジェクト全体を分析し、以下の設計ドキュメント群を生成してください。
このタスクはドキュメント生成専用タスクです。

生成対象:
- index.md
- architecture.md
- architecture_rules.md
- business_rules.md
- coding_rules.md
- directory_rules.md
- naming_rules.md
- testing_rules.md
- overview.md

要件:
- 出力は日本語で行ってください
- 文体はですます調にしてください
- Markdown 形式で出力してください
- 既存の実装構成と docs の内容を照合してください
- 不整合があれば、設計変更の必要性を明記してください
- 既存ドキュメントに追記できる最小差分でまとめてください
- 本リポジトリ固有のモジュール名に縛られず、汎用的な責務として整理してください
- 生成した Markdown 文書(architecture.mdなど)は、次のディレクトリに保存してください: E:\Dev\029 pycorex\pycorex\docs\reference
- ただし、`index.md` は docs 配下の入り口ページとして扱い、保存先は E:\Dev\029 pycorex\pycorex\docs の直下にしてください
- 生成対象のファイルはまだ存在しない場合があるため、既存の実装・設計文書をもとに新規作成してください。
- `index.md` は docs の入口ページとして生成し、生成対象の設計書一覧と参照順を案内する目次ページにしてください。
- overview.md を必ず生成してください。
- overview.md は、このリポジトリ全体の設計ドキュメントにおける概要ページとして作成し、
  プロジェクト全体の主要な責務、構成の概要、設計書の役割をまとめてください。
- overview.md には、`[src]` 参考入力に含まれる主要な Python ファイルやモジュールの代表例を
  Markdown の表形式でまとめてください。
  表には少なくとも「ファイル / モジュール」「主な責務」「代表的な機能または備考」の列を含めてください。
  すべてのファイルを列挙せず、代表的な実装単位や主要機能を中心に整理してください。
- overview.md の内容は、特定のディレクトリ構成（例: utils フォルダ）に依存しない汎用的な説明にしてください。
- `src` のファイル一覧は分析用の参考入力です。ソースコードの修正は行わず、Markdown ファイル生成のみを行ってください。
- 生成した Markdown 文書は指定した出力先ディレクトリに保存し、`src/` や既存ソースコードには変更を加えないでください。
- 出力は Markdown のみとし、ソースファイルの追加・編集・削除を含めないでください。

禁止事項:
- src配下の編集
- 既存Markdownの編集
- 設定ファイルの編集
- テストコードの編集
- PR作成
- コミット作成
- コード提案の適用

許可事項:
- ファイル参照
- ドキュメント生成
- Markdown出力

参考入力:
[docs]
docs-1. E:/Dev/029 pycorex/pycorex/docs/index.md
docs-2. E:/Dev/029 pycorex/pycorex/docs/prompts/docs_generation_prompt.md
docs-3. E:/Dev/029 pycorex/pycorex/docs/reference/architecture.md
docs-4. E:/Dev/029 pycorex/pycorex/docs/reference/architecture_rules.md
docs-5. E:/Dev/029 pycorex/pycorex/docs/reference/business_rules.md
docs-6. E:/Dev/029 pycorex/pycorex/docs/reference/coding_rules.md
docs-7. E:/Dev/029 pycorex/pycorex/docs/reference/directory_rules.md
docs-8. E:/Dev/029 pycorex/pycorex/docs/reference/naming_rules.md
docs-9. E:/Dev/029 pycorex/pycorex/docs/reference/overview.md
docs-10. E:/Dev/029 pycorex/pycorex/docs/reference/testing_rules.md

[src]
src-1. E:/Dev/029 pycorex/pycorex/src/pycorex/__init__.py
src-2. E:/Dev/029 pycorex/pycorex/src/pycorex/comfyui_client.py
src-3. E:/Dev/029 pycorex/pycorex/src/pycorex/configs/app_init.py
src-4. E:/Dev/029 pycorex/pycorex/src/pycorex/configs/initialize_app.py
src-5. E:/Dev/029 pycorex/pycorex/src/pycorex/configs/pycorex.py
src-6. E:/Dev/029 pycorex/pycorex/src/pycorex/core/base_ai_client.py
src-7. E:/Dev/029 pycorex/pycorex/src/pycorex/core/base_gemini_client.py
src-8. E:/Dev/029 pycorex/pycorex/src/pycorex/core/base_prompt_generator.py
src-9. E:/Dev/029 pycorex/pycorex/src/pycorex/enums/rating_level.py
src-10. E:/Dev/029 pycorex/pycorex/src/pycorex/exceptions/api_error.py
src-11. E:/Dev/029 pycorex/pycorex/src/pycorex/exceptions/comfyui_exceptions.py
src-12. E:/Dev/029 pycorex/pycorex/src/pycorex/exceptions/no_candidates_error.py
src-13. E:/Dev/029 pycorex/pycorex/src/pycorex/gemini_client.py
src-14. E:/Dev/029 pycorex/pycorex/src/pycorex/imagen_client.py
src-15. E:/Dev/029 pycorex/pycorex/src/pycorex/models/comfyui.py
src-16. E:/Dev/029 pycorex/pycorex/src/pycorex/models/gemini.py
src-17. E:/Dev/029 pycorex/pycorex/src/pycorex/models/prompt.py
src-18. E:/Dev/029 pycorex/pycorex/src/pycorex/models/uwgen.py
src-19. E:/Dev/029 pycorex/pycorex/src/pycorex/models/vertexai.py
src-20. E:/Dev/029 pycorex/pycorex/src/pycorex/utils/pony_prompt_generator.py
src-21. E:/Dev/029 pycorex/pycorex/src/pycorex/utils/prompt_generator.py
src-22. E:/Dev/029 pycorex/pycorex/src/pycorex/utils/workflow_editor.py
src-23. E:/Dev/029 pycorex/pycorex/src/pycorex/utils/workflow_mod.py
src-24. E:/Dev/029 pycorex/pycorex/src/pycorex/uwgen_client.py