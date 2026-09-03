# English Dictionary

英単語・短い英語フレーズの学習用辞書を、1見出し語1 Markdownで管理するリポジトリです。記事は `entries/`、進捗は `queue/words.csv`、レビュー原出力と派生監査は `audits/` に保存します。本文生成にOpenAI APIキーは不要です。独立レビュー段には、レビューAPI用のキーまたは生成担当とは独立したサブエージェント・別セッションを使うhandoffモードが必要です。同じモデルを使っても、独立サブエージェントとして実行・記録されていれば構いません。

## 1語の処理

工程本体は `scripts/run_word.py` が管理し、新規runの入口は `scripts/start_word.py` が管理します。実行前に、各段の仕様、入力範囲、出力先、指示bytesを確認できます。

```bash
python scripts/run_word.py --dry-run <headword>
python scripts/start_word.py <headword>
python scripts/run_word.py --resume <audits/workflow_runs/...json>
```

新規runでは `python scripts/run_word.py <headword>` を直接実行しません。`scripts/start_word.py` はremote branch上の同一見出し語のworkflow manifestを先に確認し、`in_progress` があれば既存runの再開を要求します。`budget_exhausted` の後も自動再試行せず、原因確認後に明示的に再実行する場合だけ次を使います。

```bash
python scripts/start_word.py <headword> --restart-after-budget-exhausted
```

remote run状態を取得できない場合はfail closedで新規runを開始しません。completed runより古い失敗runは履歴扱いになるため、正常完了後の将来の改訂は妨げません。

## 独立レビュー

APIモードは `DICT_REVIEW_PROVIDER`（`openai` / `anthropic`）、`DICT_REVIEW_MODEL`、`DICT_REVIEW_API_KEY` を使います。APIキーがない場合は `--reviewer-mode handoff` を指定し、生成されたhandoff requestを生成担当とは独立したサブエージェント/sessionへ渡します。

```bash
python scripts/run_word.py --resume <workflow-run.json> --call-review
```

非checkerのhandoff応答は `handoff/<stage>.response.json` に保存し、次で取り込みます。同一モデルを使う場合も、独立したサブエージェント provenanceを `--reviewer-agent-id` で記録します。`agent_id` は監査スキーマ上の安定したフィールド名であり、モデル名の一意性を要求するものではありません。

```bash
python scripts/run_word.py --resume <workflow-run.json> \
  --ingest-review <stage> --declared-model <model-name> \
  --reviewer-agent-id <independent-subagent-id>
```

cold review / final blind は生成担当とは独立したreview subagent/contextで実行します。コールドレビューと最終盲検には生成時の `process_improvement/ACTIVE.md` や既存findingを渡しません。

## checker_passes は7パス並列

通常チェックは13個の内容欠陥分類を7パスへ一意に割り当てます。

- translation
- example-attribution
- sense-structure
- frame-relation
- qualification
- pronunciation
- evidence

APIモードの `--call-review` はこの7パスを最大7 workerで同時実行します。各workerはルーターが選んだ自分のrequest JSONとpromptだけを受け取り、独立したサブエージェント呼び出しとして処理します。同じモデルを7パスで再利用して構いません。`frame-relation` だけは、同じworkerの中で `antonym_axis_blind_record` を作るstage 1と、その結果を開示して裁定するstage 2を順番に実行します。他の6パスはその待ち時間に独立して進みます。7結果は全worker終了後にルーター順へ機械的にfan-inし、`pass_findings.json` を作ります。

### handoff: 7並列 + frame-relationのみ2往復

handoffモードでchecker段へ到達すると、互換用index `handoff/checker_passes.request.md` と、次の7個の独立requestが生成されます。

```text
checker_passes.translation.request.md
checker_passes.example-attribution.request.md
checker_passes.sense-structure.request.md
checker_passes.frame-relation.request.md
checker_passes.qualification.request.md
checker_passes.pronunciation.request.md
checker_passes.evidence.request.md
```

これら7個を**同時に、1パス1独立サブエージェント**で実行します。七つのchecker promptを一つに連結して一つのサブエージェントへ渡してはいけません。各サブエージェントは対応する `checker_passes.<pass-id>.response.json` を返し、トップレベルに正しい `pass_id` と `reviewer` を含めます。`reviewer.agent_id` は7パスで一意でなければなりません。一方、`reviewer.declared_model` は重複して構いません。fan-inは7応答がすべて揃うまで完了せず、欠落、pass ID不一致、agent ID重複を拒否します。

第1往復のfan-inで `check_passes/checker_passes.stage1.json` を保存します。この時点で6パスは完了し、`frame-relation` だけが第2往復へ進みます。stage 1の `antonym_axis_blind_record` を使って `handoff/checker_passes.stage2.request.md`（互換名）と `handoff/checker_passes.frame-relation.stage2.request.md` を生成します。第2往復はframe-relationのstage 1と**同じサブエージェント ID・同じdeclared model**で実行します。

第2応答は `handoff/checker_passes.frame-relation.stage2.response.json` に保存します。checker段では旧aggregate handoffへのフォールバックを認めません。7個の個別stage-1応答がない場合、またはcanonicalなframe-relation stage-2応答がない場合はfail closedで停止します。第2応答を取り込むとframe-relationを裁定・復元し、7パスを `pass_findings.json` へ機械集約します。第2応答のsubagent/modelがstage 1と違う場合は拒否します。

checker_passes handoffは以上の意味で **2往復** ですが、最初の往復は7つのcheckerを直列に処理するのではなく7並列です。並列サブエージェント実行中もbudgetは進行します。heartbeatは監査用の進捗時刻であり、間隔超過だけでは停止しません。guardを止めたり、新runを作ってdeadlineを回避したりしません。同じ段の取り込み失敗が3回に達したrunは `budget_exhausted` で停止します。

新規runのorchestrator manifestには `checker_execution_protocol: parallel_subagents_v2` と `checker_subagent_count` を記録します。CIの `scripts/checker_subagent_gate.py` は、このプロトコルを持つcompleted handoff runについて7パスの被覆と `reviewer.agent_id` の一意性を再検証します。モデル名の一意性は要求しません。旧runは過去の監査証跡を改変しないため、この新プロトコルを持たない限り遡及的に失敗させません。

## オーケストレータ

オーケストレータはguard開始、生成、機械validator、7つのchecker pass、独立コールドレビュー、独立final blind、blind seal、finding解決、final review、status同期、exportの順序を記録します。budget、remote checkpoint、段階成果物の存在、blind入力分離、seal時系列、status遷移はスクリプトが強制します。heartbeatは監査用の進捗時刻として記録します。詳しい入力契約は `python scripts/run_word.py --dry-run <headword>` のJSONを正本とします。

`process_improvement/ACTIVE.md` は生成段だけへ渡し、コールドレビューと最終盲検には渡しません。registryは `scripts/process_improvement.py` が検証し、単語固有のメモや「新しい知見なし」はrecordにしません。

記事本文を改稿した場合は、オーケストレータが記事だけの個別Git commitを作り、Gitを改稿履歴の正本にします。新規runでは `revision-00N.md` を生成しません。

## 仕様の分担

| 用途 | 正本 |
|---|---|
| 辞書内容・表示 | `prompts/entry_spec_v5.md` |
| 新規runの単一化・再開判定 | `scripts/start_word.py` |
| checker routing | `prompts/check_router_v6.md` |
| 内容checker | frame-relationは `prompts/check_pass_frame_relation_v7.md`、他6パスは `prompts/check_pass_*_v6.md` |
| cold review | `prompts/cold_review_prompt_v1.md` |
| final blind | `prompts/final_blind_prompt_v2.md` |
| finding解決 | `prompts/finding_resolution_v6.md` |
| 最終合否 | `prompts/final_review_spec_v2.md` |
| source-first | `prompts/source_first_audit_v2.md` |
| Notion表示変換 | `prompts/notion_spec_v1.md` |

`entry_spec_v5.md` の辞書学的な内容基準は変更していません。旧工程文書は `backups/2026-08-25-process-refactor/`、全規範の移設証跡は `prompts/migration_table_v5_to_v6.md` にあります。

Markdown構造、front matter、固定行数、空行、行末、頻度表記などは `scripts/validate_entry.py` が先に検査し、checker promptには重複させません。`finding_scope_transfer_loss` と `raw_adjudication_manifest_divergence` は内容パスへ割り当てず、rawからの集合一致と完全再生成比較で防止します。

## 監査記録

新規runは `content_audit_v4` を使います。レビュー担当のraw JSONを `audits/runs/<initial>/<slug>/<cycle-id>/` に保存し、次でroot manifestを生成します。

```bash
python scripts/generate_audit_manifest.py generate \
  entries/a/apple.md audits/runs/a/apple/cycle-001 \
  --output audits/a/apple.json
```

root manifestはrawのhash、finding、resolution、最終判定の派生物であり、手動値を正本にしません。既存のv1〜v3監査、過去raw、history、revision snapshotは互換資産として残します。

## 検証

```bash
python -m pytest
python scripts/validate_entry.py entries
python scripts/validate_repository.py
python scripts/check_passes.py validate-router
python scripts/checker_subagent_gate.py validate --merge-ready
python scripts/migration_table.py validate
python scripts/process_improvement.py validate
python scripts/review_liveness.py regression \
  audits/runs/y/yield/20260826T131200Z-yield02
python scripts/queue_status.py escaped-by-stage
```

Pull Requestでは `.github/workflows/validate.yml` が変更記事と監査の整合、workflow guard、checker subagent provenance、source-first、semantic resolution、blind chronology、raw→manifest一致も検証します。`checked` / `final` の記事だけがNotion同期と完成版exportの対象です。

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
