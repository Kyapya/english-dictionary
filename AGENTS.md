# English Dictionary project router

このリポジトリは、英単語・短い英語フレーズの学習用辞書をMarkdownで管理し、生成・機械検証・分類別チェック・独立コールドレビュー・第三者最終審査・公開を再現可能な工程として記録するプロジェクトである。辞書学的な内容品質は `prompts/entry_spec_v5.md` に保持し、工程の順序、入力分離、heartbeat、budget、checkpoint、status同期、exportは `scripts/run_word.py` と参照先スクリプトが強制する。

## オーケストレータ

1語の作業計画は次で確認する。

```bash
python scripts/run_word.py --dry-run <headword>
```

新規runと中断済みrunの再開は次を使う。同一見出し語の未完了runは新規作成しない。

```bash
python scripts/start_word.py <headword>
python scripts/run_word.py --resume <audits/workflow_runs/...json>
```

段階操作はオーケストレータの出力をそのまま使う。

レビュー段（checker pass、example-attribution、cold review、final blind、final review）の出力は、生成を行ったエージェントが作成してはならない。`scripts/review_call.py`（API）または handoff 取り込みのみを経路とし、`reviewer` フィールドのない出力は `scripts/check_passes.py` が拒否する。handoff応答は生成セッション外の別モデル・別セッションから人間が取り込む。

### ユーザー指定の局所修整はフルレビューへ戻さない

すでに `checked` または `final` の記事について、ユーザーが記事を確認したうえで具体的な誤り・修整箇所を指定した場合は **targeted correction** として扱う。この経路では `scripts/start_word.py` / `scripts/run_word.py` を起動せず、checker passes、cold review、final blind、final review、finding resolution、全記事のsource-first再監査を行わない。

対象は、既存記事の一部に対する明示的な修整依頼である。ユーザーが複数の具体的箇所を列挙した場合も、同一記事内の指定箇所だけを直す限りこの経路を使う。全面改稿、記事全体の再評価、大規模な語義再編、またはbase版が `checked` / `final` でない場合は通常工程を使う。

実施順序は次のとおり。

1. ユーザーが指定した箇所だけを必要最小限に修整する。無関係な表現改善を混ぜない。
2. `prompts/targeted_correction_review_v1.md` に従い、ユーザーの修整依頼、変更diff、各hunkの理解に必要な最小限の周辺文脈だけを確認する。別セッションへの独立handoffは不要で、未変更部分を探索的に再レビューしない。
3. 修整箇所が依頼どおりで、変更部分に事実・語義・例文・訳・隣接記述との明白な不整合がないことを確認したら `pass` とする。
4. `scripts/targeted_correction.py record` で `audits/targeted_corrections/<slug>/` に監査レコードを作る。レコードはbase本文、修整後本文、確認済みdiffのhashに結び付ける。
5. `scripts/targeted_correction.py validate-changed --base <base> --head <head>` と通常のMarkdown/queue検証を通して終了する。記事の `checked` / `final` 状態は維持する。

例:

```bash
BASE=$(git merge-base origin/main HEAD)
python scripts/targeted_correction.py record \
  --entry entries/d/dimension.md \
  --base "$BASE" \
  --request "<ユーザーが指定した修整内容>" \
  --reviewer "<この局所チェックを行ったモデル/セッション>" \
  --review-notes "指定箇所と変更hunkのみ確認"
```

修整PRでは、変更対象の記事と、その記事に対応する新規 `audits/targeted_corrections/...json` だけを変更する。これによりCIは局所修整経路を自動判定し、重い独立監査群の代わりに変更diffへ束縛された専用検証を実行する。

### checker_passes handoffは2往復

handoffモードの `checker_passes` は、反意語軸を盲検採取してから裁定する2段構成で、1往復では完了しない。

1. 第1応答は7パスを過不足なく1回ずつ含む1個のJSON。frame-relationは `prompts/check_pass_frame_relation_v7.md` に従い `antonym_axis_blind_record` を含める。保存先は `handoff/checker_passes.response.json`。
2. `--ingest-review checker_passes` は段階を完了させず、段階1を `check_passes/checker_passes.stage1.json` に保存し、次のhandoff `handoff/checker_passes.stage2.request.md` を返す。
3. 第2応答は `antonym_axis_adjudication_record_v1` 1個を別セッションで作り `checker_passes.stage2.response.json` へ保存する。もう一度取り込むと段階が完了する。

`handoff response is missing: …stage2.response.json` は第2応答が未作成という意味で、handoffの作り直しではない。取り込み失敗はguardが記録し、同じ段が3回失敗するとrunは `budget_exhausted` になる。

## ファイル命名

- 見出し語は `headword` と呼ぶ。
- slugは小文字の半角英数字とハイフンを基本とし、スペース・句読点は `scripts/slugify.py` の規則で変換する。
- 記事は `entries/{slugの先頭1文字}/{slug}.md` に置く。同名衝突時は `__word`、`__phrase`、`__verb` 等を付ける。
- 新規run成果物は `audits/workflow_runs/`、段階原出力は `audits/runs/`、日付付き要約は `logs/` に置く。
- 局所修整の監査レコードは `audits/targeted_corrections/<slug>/` に置く。

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

局所修整では、baseが `checked` / `final` かつ `checked: true` であることを前提とし、修整後も同じfinal statusを維持する。局所修整そのものを理由に `review_ready` へ戻さない。

## 仕様・実装の参照表

| 用途 | 正本 |
|---|---|
| 記事内容・構成・表示 | `prompts/entry_spec_v5.md` |
| 通常チェック | `prompts/check_router_v6.md`、`prompts/check_pass_frame_relation_v7.md`、6つの `prompts/check_pass_*_v6.md` |
| コールドレビュー入力 | `prompts/cold_review_prompt_v1.md` |
| 最終盲検入力 | `prompts/final_blind_prompt_v2.md` |
| finding解決 | `prompts/finding_resolution_v6.md` |
| 最終合否 | `prompts/final_review_spec_v2.md` |
| 局所修整チェック | `prompts/targeted_correction_review_v1.md`、`scripts/targeted_correction.py` |
| source-first根拠収集 | `prompts/source_first_audit_v2.md`、`scripts/source_first_audit_gate.py` |
| semantic constraint・blind seal・監査派生値 | `prompts/semantic_resolution_gate_v1.md`、`scripts/semantic_resolution_gate.py`、`scripts/generate_audit_manifest.py` |
| 工程順序・入力分離・status・export | `scripts/run_word.py` |
| heartbeat・budget・安全停止 | `scripts/entry_workflow_guard.py` |
| Markdown形式検証 | `scripts/validate_entry.py` |
| queue・記事整合 | `scripts/validate_repository.py` |
| Notion変換 | `prompts/notion_spec_v1.md`、`scripts/import_to_notion.py` |
| 工程改善（生成文脈のみ） | `process_improvement/ACTIVE.md`、`process_improvement/README.md`、`scripts/process_improvement.py` |

旧v5工程文書は `backups/2026-08-25-process-refactor/`、規範ルールの移設先は `prompts/migration_table_v5_to_v6.md` を参照する。