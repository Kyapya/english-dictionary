# English Dictionary project router

このリポジトリは、英単語・短い英語フレーズの学習用辞書をMarkdownで管理し、生成・機械検証・分類別チェック・独立コールドレビュー・第三者最終審査・公開を再現可能な工程として記録するプロジェクトである。辞書学的な内容品質は `prompts/entry_spec_v5.md` に保持し、工程の順序、入力分離、heartbeat、budget、checkpoint、status同期、exportは `scripts/run_word.py` と参照先スクリプトが強制する。

## オーケストレータ

1語の作業計画は次で確認する。

```bash
python scripts/run_word.py --dry-run <headword>
```

実行または中断済みrunの再開は次を使う。

```bash
python scripts/run_word.py <headword>
python scripts/run_word.py --resume <audits/workflow_runs/...json>
```

個別の手続きコマンドをLLMが組み立てず、オーケストレータが表示・保存する段階入力と出力先をそのまま使う。

レビュー段（checker pass、example-attribution、cold review、final blind、final review）の出力は、生成を行ったエージェントが作成してはならない。`scripts/review_call.py`（API）または handoff 取り込みのみを経路とし、`reviewer` フィールドのない出力は `scripts/check_passes.py` が拒否する。handoff応答は生成セッション外の別モデル・別セッションから人間が取り込む。

## ファイル命名

- 見出し語は `headword` と呼ぶ。
- slugは小文字の半角英数字とハイフンを基本とし、スペース・句読点は `scripts/slugify.py` の規則で変換する。
- 記事は `entries/{slugの先頭1文字}/{slug}.md` に置く。同名衝突時は `__word`、`__phrase`、`__verb` 等を付ける。
- 新規run成果物は `audits/workflow_runs/`、段階原出力は `audits/runs/`、日付付き要約は `logs/` に置く。

## status

`queue/words.csv` と記事front matterでは次を使う。

- `pending`: 未生成
- `draft`: 生成済み・未チェック
- `format_error`: 機械的な形式不備あり
- `needs_review`: 内容確認またはblockerあり
- `review_ready`: 通常チェックとコールドレビュー対応済み・最終審査待ち
- `checked`: 最終審査合格済み
- `final`: 完成扱い
- `skip`: 処理対象外

## 仕様・実装の参照表

| 用途 | 正本 |
|---|---|
| 記事内容・構成・表示 | `prompts/entry_spec_v5.md` |
| 通常チェック | `prompts/check_router_v6.md` と7つの `prompts/check_pass_*_v6.md` |
| コールドレビュー入力 | `prompts/cold_review_prompt_v1.md` |
| 最終盲検入力 | `prompts/final_blind_prompt_v2.md` |
| finding解決 | `prompts/finding_resolution_v6.md` |
| 最終合否 | `prompts/final_review_spec_v2.md` |
| source-first根拠収集 | `prompts/source_first_audit_v2.md`、`scripts/source_first_audit_gate.py` |
| semantic constraint・blind seal・監査派生値 | `prompts/semantic_resolution_gate_v1.md`、`scripts/semantic_resolution_gate.py`、`scripts/generate_audit_manifest.py` |
| 工程順序・入力分離・status・export | `scripts/run_word.py` |
| heartbeat・budget・安全停止 | `scripts/entry_workflow_guard.py` |
| Markdown形式検証 | `scripts/validate_entry.py` |
| queue・記事整合 | `scripts/validate_repository.py` |
| Notion変換 | `prompts/notion_spec_v1.md`、`scripts/import_to_notion.py` |
| 工程改善（生成文脈のみ） | `process_improvement/ACTIVE.md`、`process_improvement/README.md`、`scripts/process_improvement.py` |

旧v5工程文書は `backups/2026-08-25-process-refactor/`、規範ルールの移設先は `prompts/migration_table_v5_to_v6.md` を参照する。
