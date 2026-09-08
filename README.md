# English Dictionary

英単語・短い英語フレーズの学習用辞書を、1見出し語1 Markdownで管理するリポジトリです。記事は `entries/`、進捗は `queue/words.csv`、レビュー原出力と派生監査は `audits/` に保存します。本文生成にOpenAI APIキーは不要です。独立レビュー段には、レビューAPI用のキーまたは生成担当とは独立したサブエージェント・別セッションを使うhandoffモードが必要です。同じモデルを使っても、独立サブエージェントとして実行・記録されていれば構いません。

## 1語の処理

工程本体は `scripts/run_word.py` が管理し、新規runの入口は `scripts/start_word.py` が管理します。実行前に、各段の仕様、入力範囲、出力先、指示bytesを確認できます。

```bash
python scripts/run_word.py --dry-run <headword>
python scripts/start_word.py <headword>
python scripts/run_word.py --resume <audits/workflow_runs/...json>
```

### 実行前の保存経路・レビュー方式

新規runはAPIキーがなければhandoffを選ぶ。GitHub接続で作業するWorkでは、明示的に
`python scripts/start_word.py <headword> --publish-mode connector --reviewer-mode handoff`
を使う。通常のGit認証が設定済みの環境は `--publish-mode git` を指定する。
保存経路はrunにも記録される。開始後の `publication_pending` はエラーではなく、
ローカルcommitを接続APIへ渡す状態である。

Workのcode modeでは、以下の要領でchecked-inの転送処理を呼ぶ。`root` は実際の
checkoutの絶対パスにする。スクリプトを読む前に現在のcheckoutと変更内容を確認する。

```javascript
const root = "/absolute/path/to/english-dictionary";
const loaded = await tools.exec_command({
  cmd: "sed -n '1,240p' scripts/publish_checkpoint.js",
  workdir: root, max_output_tokens: 10000
});
if (loaded.exit_code !== 0) throw new Error(loaded.output);
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const receipt = await new AsyncFunction("tools", "root", "repository", loaded.output)(
  tools, root, "Kyapya/english-dictionary"
);
text(receipt);
```

この処理はコミット順を保ち、ファイルをbase64の分割読取りで転送してblob/treeのSHAを
照合する。ファイル本文をモデルの会話へ出力・再入力しない。refは非force更新し、
反映後にfetchして全commitのtreeと親を照合する。APIで作られたcommitはローカルとSHAが
異なり得るため、対応表をGit管理領域へ保存する。cloneし直した場合は再送を始めず、
remoteの実在checkpointを確認して再開する。

反映成功後は同じrunをresumeし、開始確認commitの `publication_pending` も同様に反映する。
以降のcheckpointもcommit後に同じ転送処理を使う。通信断でref更新だけ成功した場合は、
remote headを確認して `python scripts/publish_checkpoint.py accept --sha <remote-head>` で
内容・順序を照合してから再開する。資格情報を接続から抽出せず、権限拒否を迂回しない。

### 取り込み前の検証

```bash
python scripts/run_word.py --resume <workflow-run.json> \
  --validate-review cold_review --declared-model <model-name> \
  --reviewer-agent-id <independent-subagent-id>
```

checker/final_blind/final_reviewも同じ指定形式を使う。検証は一時コピーで正式取り込みを
実行し、実runの応答・時刻・失敗回数を変更しない。最終レビューは監査生成まで確認する。
新runの正式取り込みにもこの検証を組み込み、同じ入力・応答の失敗を再計上しない。
修正した応答も不正なら既存の有限な失敗budgetに計上し、新runで回避しない。

最終レビューは必須入力が揃い、盲検の先行commitが存在してから準備する。対象一覧と
未判定の回答ひな形を同梱し、入力不足を空集合として扱わない。元の検査入力はsnapshotに
保存し、後からハッシュを付け替えない。出典の内容・使用回数の更新を再検査より前に済ませ、
最終入力の固定後に変更があればレビュー開始前／取り込み前に検出する。

新規runでは `python scripts/run_word.py <headword>` を直接実行しません。`scripts/start_word.py` はremote branch上の同一見出し語のworkflow manifestを先に確認し、`in_progress` があれば既存runの再開を要求します。`budget_exhausted` の後も自動再試行せず、原因確認後に明示的に再実行する場合だけ次を使います。

ただし旧来の時間超過だけで停止したrunは例外です。新runを作らず通常の `--resume` で
同じrunを復帰し、`time_stop_recoveries` に旧停止理由と時刻を保存します。復帰checkpointも
通常の公開経路で保存します。旧late-draft停止でdraft checkpointと工程cursorがずれた
場合も、保存済みの全生成出力・計測値を確認してcursorだけを同期し、生成をやり直しません。
修正後checkerの再検査回数も無制限です。旧回数制限だけの停止は `--resume` が
`recheck_stop_recoveries` に理由を保存し、同じrunと累積回数・未解決事項を保って復帰します。
出力が欠けている場合は復帰を拒否します。検索上限・最終審査回数上限・取り込み失敗・理由不明の停止は
自動解除しません。下記のrestartフラグでも時間切れrunの再作成は許可しません。

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

cold review / final blind は生成担当とは独立したreview subagent/contextで実行します。コールドレビュー、通常checker、最終盲検には生成側のprocess-improvement入力スナップショットや既存findingを渡しません。通常checkerとcold reviewは同じ固定draftを対象とし、API modeでは最大7 worker枠の中で同時進行します。

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

checker_passes handoffは以上の意味で **2往復** ですが、最初の往復は7つのcheckerを直列に処理するのではなく7並列です。並列サブエージェント実行中も経過時間を計測しますが、時間超過だけでは停止しません。heartbeatは監査用の進捗時刻であり、間隔超過だけでは停止しません。guardを止めたり、新runを作ってdeadlineを回避したりしません。同じ段の取り込み失敗が3回に達したrunは `budget_exhausted` で停止します。

新規runのorchestrator manifestには `checker_execution_protocol: parallel_subagents_v2` と `checker_subagent_count` を記録します。CIの `scripts/checker_subagent_gate.py` は、このプロトコルを持つcompleted handoff runについて7パスの被覆と `reviewer.agent_id` の一意性を再検証します。モデル名の一意性は要求しません。旧runは過去の監査証跡を改変しないため、この新プロトコルを持たない限り遡及的に失敗させません。

evidence checker requestには、完成済みsource-first正本から対象claimに関係するsource、fact、source union、claim unit、source supportだけを抽出した `evidence_context_v1` を入れます。全artifactの丸ごと複製や再探索は行いません。source-first欠落・未完了・参照切れ・本文hash不一致はchecker開始前に拒否し、API/handoffはいずれも同じrequest JSONを使います。

## オーケストレータ

全工程60/90分・下書き20/30分は警告目安です。`deadline_at` 等の旧フィールド名・値は
履歴互換と計測のため保持しますが、どの工程でも時間超過だけでは停止しません。
`time_warnings` に最初の超過観測時刻・工程・同一run継続の指示を保存します。
調整役は原因を報告し、未完了工程を続けます。時間のために完了済みのchecker/coldを
再実行しません。検索・最終審査回数上限、不正応答の反復停止、通信・コマンドtimeout、
CIの実行timeoutは別の安全策として維持します。更新時刻だけで実行停止と断定しません。

オーケストレータはguard開始、生成、機械validator、同一固定draftへの7 checker/cold、pre-blind resolution、一括修正、影響範囲checker再検査、最新版への独立final blind、blind seal、post-blind resolution、final review、status同期、exportの順序を記録します。final-blind修正を採用した場合は、影響pass再検査後に新本文でfinal blindを再実行します。budget、remote checkpoint、段階成果物の存在、blind入力分離、本文hash、seal時系列、status遷移はスクリプトが強制します。

修正影響は `scripts/workflow_revision.py` が意味単位で判定します。pronunciationだけならpronunciation/evidence、例文・訳ならtranslation/example-attribution/frame-relation等を失効させます。spec hash、正規化入力hash、source-first hash、schema、reviewer independence、request bindingがすべて一致し、影響対象外のpassだけ再利用できます。複数sectionの局所修正は依存passの和集合を再検査します。分類不能、語義統合・分割、品詞・語義順序の変更は全7 checkerを再実行します。cold reviewは同じ目的で全面再実行しません。

findingゼロだけを理由とする二次cold/example-attribution reviewは新規runでは行いません。必須pass欠落・hash不一致等は機械拒否し、具体的な判断衝突、明示的不確実性、未解決evidenceだけを争点単位の `targeted_adjudication` へ送ります。`insufficient_evidence` はPASSへ変換しません。

## Process improvement v2

`process_improvement/records/` の構造化JSONが知見の正本です。新世代 `pi2-2026-09-06` は空台帳から開始し、旧PI本文・旧 `ACTIVE.md`・旧退役状態は通常検索、入力、集計へ戻しません。`epoch.json` は移行前SHAと除外した旧パス／IDだけを保持し、旧本文はGit履歴で参照します。

公開入口はrun作成時に、同じ世代・`active`・仕様依存が有効で、担当・工程・特徴条件が一致する知見だけを選び、`audits/runs/.../process_improvement/*.snapshot.md` へ固定します。初期上限は8件・8 KiBです。これは一般的な作業知見を数件渡せる一方、記事仕様やレビュー入力を圧迫しない保守的な初期値です。上限超過時はpriority、ID、版の決定順で知見単位に選び、条件・例外を途中切断しません。選択ID・版・届け先・hash・実bytes・機械処理秒・PI専用追加LLM呼び出し数をsnapshotとrun metricsへ保存します。

生成担当と既存調整役は、既存工程の出力に小さな `learning_delta` を含めます。完了・checkpoint・resumeが同じ冪等取込を実行し、結果を `processed` / `no_applicable` / `pending` / `save_error` としてrunへ残します。局所修整も `--learning-delta` から同じ取込へ接続します。知見抽出専用のLLM工程はありません。入力に渡した事実、行動確認、再発、非再発、負担、結果不明は版別のimmutable observationとして分離し、未計測は `null` のまま集計します。

意味判断は既存調整役が行います。初回の有用な事象でも候補化でき、escaped defectや固定回数は必須ではありません。未裁定findingや原因推測は `active` にできません。仕様依存が変わった知見は次回入力から外れ、根拠と再確認理由を伴う版更新だけが復活できます。`integrated` と `retired` は入力へ重複配信せず、PI状態からcheckerや正式実装を削除する処理はありません。

主要操作は次のとおりです。`ACTIVE.md` と `index.json` は派生表示であり、実行入力の正本ではありません。

```bash
python scripts/process_improvement.py validate
python scripts/process_improvement.py summary --json
python scripts/process_improvement.py select \
  --recipient generator --phase generation --run-id <run-id> \
  --feature <confirmed-feature> --output <snapshot.md>
python scripts/process_improvement.py ingest --source <event.json> --delta <delta.json>
python scripts/process_improvement.py reconfirm \
  --record-id <PI2-ID> --expected-version <N> \
  --evidence-ref <fixed-reference> --rationale <reviewed-reason>
```

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
| checker/cold finding解決 | `prompts/pre_blind_resolution_v1.md` |
| final-blind finding解決 | `prompts/post_blind_resolution_v1.md` |
| 争点別追加裁定 | `prompts/targeted_adjudication_v1.md` |
| 最終合否 | `prompts/final_review_spec_v2.md` |
| source-first | `prompts/source_first_audit_v2.md` |
| process improvement | `process_improvement/README.md`、`prompts/process_improvement_learning_delta_v2.md`、`scripts/process_improvement.py` |
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

root manifestはrawのhash、finding、pre/post resolution、checker再検査・再利用、最終判定の派生物であり、手動値を正本にしません。`workflow_improvement_v1` より前のcompleted runは旧resolution契約のまま読み取り可能で、遡及的に無効化・再生成しません。

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
- `process_improvement/`: v2知見、版履歴、観測、冪等取込receipt、派生index
- `logs/`: 試行・計測ログ
- `tests/`: 契約・回帰テスト
- `exports/`: 結合Markdownと索引

Notion同期は `prompts/notion_spec_v1.md` と `.github/workflows/sync-notion.yml` に従います。GitHub上のMarkdownを現行本文の正本とし、既存の同一見出し語ページは内容を更新します。
