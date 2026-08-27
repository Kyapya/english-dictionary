# English Dictionary

英単語・短い英語フレーズの学習用辞書を、1見出し語1 Markdownで管理するリポジトリです。記事は `entries/`、進捗は `queue/words.csv`、レビュー原出力と派生監査は `audits/` に保存します。本文生成にOpenAI APIキーは不要です。独立レビュー段には、レビューAPI用のキーまたは別モデル・別セッションを使うhandoffモードが必要です。

## 1語の処理

工程は `scripts/run_word.py` が管理します。実行前に、各段の仕様、入力範囲、出力先、指示bytesを確認できます。

```bash
python scripts/run_word.py --dry-run <headword>
python scripts/run_word.py <headword>
python scripts/run_word.py --resume <audits/workflow_runs/...json>
```

APIモードは `DICT_REVIEW_PROVIDER`（`openai` / `anthropic`）、`DICT_REVIEW_MODEL`、`DICT_REVIEW_API_KEY` を使います。APIキーがない場合は `--reviewer-mode handoff` を指定し、生成された `handoff/<stage>.request.md` を別セッションへ渡します。応答を `handoff/<stage>.response.json` に保存後、次で取り込みます。

APIレビューは、resume時に生成されるrequest JSONとdry-runに示されるpromptを `scripts/review_call.py` に渡します。通常は次の `--call-review` を使い、API応答の保存・検証、example-attributionの復元、7passの機械集約までをまとめて実行します。cold review / final blind のモデルは記事front matterの生成モデルと異なるものを既定とし、同一モデルを明示的に使う場合は出力provenanceへ `same_model_as_generation: true` が付きます。

```bash
python scripts/run_word.py --resume <workflow-run.json> --call-review
```

```bash
python scripts/review_call.py <stage> <request.json> <prompt.md> \
  --cycle-dir <audits/runs/.../cycle-id> --output <stage-output.json> \
  --generation-model <generation-model>
```

```bash
python scripts/run_word.py --resume <workflow-run.json> \
  --ingest-review <stage> --declared-model <model-name>
```

オーケストレータはguard開始、生成、機械validator、7つのchecker pass、独立cold review、独立final blind、blind seal、finding解決、final review、status同期、exportの順序を記録します。heartbeat、budget、remote checkpoint、段階成果物の存在、blind入力分離、seal時系列、status遷移はスクリプトが強制します。詳しい入力契約は `python scripts/run_word.py --dry-run <headword>` のJSONを正本とします。

`process_improvement/ACTIVE.md` は生成段だけへ渡し、コールドレビューと最終盲検には渡しません。registryは `scripts/process_improvement.py` が検証し、単語固有のメモや「新しい知見なし」はrecordにしません。

記事本文を改稿した場合は、オーケストレータが記事だけの個別Git commitを作り、Gitを改稿履歴の正本にします。新規runでは `revision-00N.md` を生成しません。

## 仕様の分担

| 用途 | 正本 |
|---|---|
| 辞書内容・表示 | `prompts/entry_spec_v5.md` |
| checker routing | `prompts/check_router_v6.md` |
| 内容checker | 7つの `prompts/check_pass_*_v6.md` |
| cold review | `prompts/cold_review_prompt_v1.md` |
| final blind | `prompts/final_blind_prompt_v2.md` |
| finding解決 | `prompts/finding_resolution_v6.md` |
| 最終合否 | `prompts/final_review_spec_v2.md` |
| source-first | `prompts/source_first_audit_v2.md` |
| Notion表示変換 | `prompts/notion_spec_v1.md` |

`entry_spec_v5.md` の辞書学的な内容基準は変更していません。旧工程文書は `backups/2026-08-25-process-refactor/`、全規範の移設証跡は `prompts/migration_table_v5_to_v6.md` にあります。

## v6 checker

通常チェックは13個の内容欠陥分類を7パスへ一意に割り当て、各パスへ必要なentry sectionだけを渡します。

- translation
- example-attribution
- sense-structure
- frame-relation
- qualification
- pronunciation
- evidence

Markdown構造、front matter、固定行数、空行、行末、頻度表記などは `scripts/validate_entry.py` が先に検査し、checker promptには重複させません。`finding_scope_transfer_loss` と `raw_adjudication_manifest_divergence` は内容パスへ割り当てず、rawからの集合一致と完全再生成比較で防止します。

## 監査記録

新規runは `content_audit_v4` を使います。レビュー担当のraw JSONを `audits/runs/<initial>/<slug>/<cycle-id>/` に保存し、次でroot manifestを生成します。

```bash
python scripts/generate_audit_manifest.py generate \
  entries/a/apple.md audits/runs/a/apple/cycle-001 \
  --output audits/a/apple.json
```

root manifestはrawのhash、finding、resolution、最終判定の派生物であり、手動値を正本にしません。既存のv1〜v3監査、過去raw、history、revision snapshotは互換資産として残します。詳細は `audits/README.md` を参照してください。

## 検証

```bash
python -m pytest
python scripts/validate_entry.py entries
python scripts/validate_repository.py
python scripts/check_passes.py validate-router
python scripts/migration_table.py validate
python scripts/process_improvement.py validate
python scripts/review_liveness.py regression \
  audits/runs/y/yield/20260826T131200Z-yield02
python scripts/queue_status.py escaped-by-stage
```

Pull Requestでは `.github/workflows/validate.yml` が変更記事と監査の整合、workflow guard、source-first、semantic resolution、blind chronology、raw→manifest一致も検証します。`checked` / `final` の記事だけがNotion同期と完成版exportの対象です。

## 主なディレクトリ

- `entries/`: 辞書記事
- `queue/words.csv`: statusと記事パス
- `prompts/`: 内容仕様と小型review prompt
- `scripts/`: オーケストレータと機械gate
- `audits/`: workflow run、review raw、派生manifest、過去互換監査
- `process_improvement/`: active/trial/retiredの工程改善record
- `logs/`: 試行・計測ログ
- `tests/`: 契約・回帰テスト
- `exports/`: 結合Markdownと索引

Notion同期は `prompts/notion_spec_v1.md` と `.github/workflows/sync-notion.yml` に従います。GitHub上のMarkdownを現行本文の正本とし、既存の同一見出し語ページは内容を更新します。
