# English Dictionary project router

英単語・短い英語フレーズを1記事1 Markdownで管理する。内容基準は
`prompts/entry_spec_v5.md`、工程・入力分離・checkpoint・budget・statusは
`scripts/run_word.py` と参照スクリプトが正本である。

## 複数語・1語の依頼受付

通常の単語追加依頼は1語でも複数語でも `scripts/start_words.py` の共通入口を使う。
カンマ・読点・改行の一覧を受け付け、短いフレーズは1項目として渡す。
ユーザーに一語の完了を待って次を再依頼させない。具体的な局所修整は従来経路のまま。

```bash
python scripts/start_words.py alpha beta "take off" --enqueue-only
python scripts/start_words.py --dispatch --max-active 2
python scripts/start_words.py --status
```

`docs/multi_word_workflow.md` をcontrol担当だけが読む。受付票とjob状態をcontrol branchへ
保存し、利用可能な語担当の数だけdispatchする。枠を確認できない環境はmax-active 1とし、
受付だけはまとめる。各語担当には独立したworkspace/割当票を渡し、その場所で下記の
既存1語フローを最後まで進める。一語の停止で他語を止めず、空き枠へ待機語を渡す。
複数語の本文・監査を同じ生成contextに束ねない。start_wordsはLLMを自動起動しないため、
実行枠がない環境で並列生成済みと報告しない。旧1語CLIの互換性と全品質gateを維持する。
別cloneを独立したcontrolとして二重起動せず、既存controlとremote状態を先に確認する。

## オーケストレータ

```bash
python scripts/run_word.py --dry-run <headword>
python scripts/start_word.py <headword>
python scripts/run_word.py --resume <audits/workflow_runs/...json>
```

実行環境の保存経路は開始前に決める。WorkのGitHub接続を使う場合は
`start_word.py <headword> --publish-mode connector --reviewer-mode handoff` を使う。
`publication_pending` は正常な引き渡しであり、`scripts/publish_checkpoint.js` を
GitHub接続で実行してから同じrunをresumeする（手順はREADME）。通常pushの資格情報が
ないことが既知なら `git push` を試さない。認証済みGitを使う環境だけ `--publish-mode git`
を指定する。権限・保護ルールの拒否を別経路で回避しない。

handoffの担当は応答保存後、`--resume <run> --validate-review <stage>` と担当ID・モデルを
指定して事前検証し、指摘をまとめて修正したうえで正式取り込みする。事前検証はLLMを
呼ばず、正式取り込みと同じ処理を一時コピーで実行する。入力・応答の契約不備は `needs_review_correction` として履歴へ分離し、
実取り込み・通信・実行失敗の停止回数へ算入しない。同じ未修正応答の再投入は拒否する。
旧事前検証エラーだけによる停止は、修正した応答の完全検証後に同じrunで復旧する。
失敗回数を戻すための新run作成は禁止。開始時刻・完了工程・累積失敗履歴を維持する。
最終レビュー依頼前に入力不整合を一括検証し、missing/extra・期待値/実値・検証不能項目を
まとめて修正する。本文が不変で依頼済みの入力だけを直した場合は
`--resume <run> --refresh-review final_review` で旧依頼・応答を保存して再依頼する。
新応答はひな形の `input_revision_id` と一致させる。本文変更は従来のrevision/recheck経路を使う。

新runの検査入力は固定される。`check_passes/input_snapshot.json` と元のrequestを
上書きせず、変更後は既存のrevision/recheck経路を使う。出典の使用回数等も再検査前に
確定させる。最終レビュー前にblind/sealを先行commit・反映し、必須入力の存在、
最新版の検査、対象IDと回答ひな形を機械確認する。ひな形の未判定をpassとみなさない。

同一見出し語の未完了runは新規作成せず、オーケストレータの出力どおりに再開する。
全工程60/90分・draft20/30分は警告目安であり、超過を理由に停止・新run作成・
通常checker/coldの全面再実行をしない。`time_warnings` に超過時刻と工程を記録し、
調整役は遅延原因を報告して同じrunの未完了工程へ進む。旧時間切れだけの停止は
`--resume` が履歴を残して復帰する。開始時刻、期限目安、失敗回数、検査入力は戻さない。
修正後checker再検査は回数無制限とし、累積回数を記録して同じrunを続ける。
旧再検査回数だけの停止は `--resume` が履歴と未解決事項を保って復帰する。
検索・最終審査回数の上限、通信・コマンドtimeout、公開条件は維持する。時間停止と
回数上限停止を混同せず、後者を新runで回避しない。heartbeatの古さだけで停止と断定しない。
checker、example-attribution、cold review、final blind、final reviewは生成担当と
独立した `scripts/review_call.py` または handoff のサブエージェント出力だけを受け付ける。

### 局所修整

`checked` / `final` の具体的な修整は `prompts/targeted_correction_review_v1.md`
と `scripts/targeted_correction.py` の局所経路を使う。全面改稿は通常工程で行う。

局所reviewの既存出力に `learning_delta` を含め、`targeted_correction.py record --learning-delta`
から通常runと同じPI取込へ渡す。知見がなければ明示的な空配列、
未判断なら `pending` とし、PIのために全体reviewへ戻したり追加LLMを呼んだりしない。

### process improvement v2

公開入口は、同じknowledge epochで `active`、仕様依存・担当・工程・既知特徴が一致する
知見だけをrun内の `process_improvement_input_path` へ固定する。生成担当と既存調整役は
`prompts/process_improvement_learning_delta_v2.md` に従い、既存出力へ小さな
`learning_delta` を含める。完了・checkpoint・resumeは自動取込し、処理済み、該当なし、
整理未了、保存エラーを区別する。追加のPI専用LLM工程は作らない。

通常checker、cold review、final blindへ、PI snapshot、元の失敗例、過去finding、期待結論を
渡さない。PIは正式仕様やユーザー指示を上書きせず、品質guard・レビュー・公開条件を
変更しない。仕様依存が変わった知見は入力から外し、根拠付き再確認による版更新だけで
再利用する。配信、行動、再発、非再発、負担、結果不明は別の観測として版別集計する。
配信回数や欠陥0件だけで自動退役せず、PI操作からcheckerや統合済み安全策を削除しない。

### checker_passes: 7並列 + frame-relationのみ2往復

7パスを一つに連結せず独立実行する。APIは最大7 workerで7つの独立サブエージェント呼び出しを行い、`frame-relation`だけ同一worker
内で `antonym_axis_blind_record` のstage 1→2を直列化する。handoffは7個のrequestを
同時に1パス1独立サブエージェントへ渡し、応答の正しい `pass_id`・一意な `reviewer.agent_id` を
要求する。同じmodelを複数サブエージェントで使うことは許可し、model名の一意性は要求しない。欠落・ID不一致・agent ID重複はfan-inで拒否する。

7応答を `checker_passes.stage1.json` に保存し、frame-relationだけ第2往復へ進める。
`checker_passes.stage2.request.md` と並列名のrequestを作り、stage 1と同じサブエージェント/model
のcanonical response `checker_passes.frame-relation.stage2.response.json` だけを受け付ける。旧aggregate checker handoffへのフォールバックは認めない。この
2往復中の実取り込み・通信失敗3回は `budget_exhausted` とし、事前検証の契約不備は
修正待ちとして別記録する。並列中もheartbeat・budgetを進める。

新規runはmanifestに `checker_execution_protocol: parallel_subagents_v2` と
`checker_subagent_count` を持つ。`scripts/checker_subagent_gate.py` はcompleted handoff runの
7パス被覆と `reviewer.agent_id` 一意性をCIで再検証する。これはLLM checkerを追加する処理ではなく、
既存レビューのprovenanceを機械検証するだけである。

evidence passは、同じrunの完成済み `source_inventory.json` を正本とする
`evidence_context_v2`（`prompts/check_pass_evidence_v7.md`） を受け取る。対象claimのsource/fact/union/supportと最新本文の
対応targetを機械抽出し、本文・正本hash、schema、参照整合が不正ならfail closedとする。
reviewerは本文→claim→外部資料を照合し、意味上の接続違いも検出する。既存locatorを
実際に開く。作成者の要約だけで確認済みにせず、閲覧不能なら `insufficient_evidence`
をblocking findingにする。探索計画・全factの作り直しは不要だが、資料の再閲覧は省略しない。
標準APIには閲覧機能がないため、外部資料を閲覧できるhandoff reviewerを使う。

最終照合は `final_review_v3`。全IDの判定を保ち、正常passのnotes・本文全文引用を省略する。
failとfindingの修正確認・不採用判断だけに短い説明を残す。hash・時系列・再検査条件を
機械検証し、合格理由表を再作成しない。未判定のpass補完は禁止。過去runは旧schemaで検証する。

### 修正・final blind・追加裁定

固定draftに通常7 checkerとcold reviewを実行し、APIではcoldも同じ最大7 worker枠へ
投入する。checker/cold findingは `pre_blind_resolution` で一括反映し、
`scripts/workflow_revision.py` が変更意味単位に依存するpassだけを失効させる。
複数sectionでも分類できる局所修正は依存passの和集合だけを失効させる。
分類不能、語義統合・分割、品詞・語義順序の変更は全7 passへ倒す。

影響passの再検査後、最新本文だけをfinal blindへ渡す。final-blind findingは
`post_blind_resolution` だけで裁定し、採用修正時は影響pass再検査後に新本文で
final blindを再実行する。findingゼロは追加レビュー理由にしない。具体的な判断衝突、
明示的不確実性、未解決evidenceだけを独立 `targeted_adjudication` へ渡し、
`insufficient_evidence` はPASSにしない。

## ファイル・status

記事は `entries/{slugの先頭1文字}/{slug}.md`、run成果物は `audits/workflow_runs/` と
`audits/runs/` に置く。statusは `pending`、`draft`、`format_error`、`needs_review`、
`review_ready`、`checked`、`final`、`skip` を使う。

## 正本

| 用途 | 正本 |
|---|---|
| 記事内容 | `prompts/entry_spec_v5.md` |
| 通常チェック | `prompts/check_router_v6.md`、`prompts/check_pass_frame_relation_v7.md`、`prompts/check_pass_*_v6.md` |
| コールドレビュー | `prompts/cold_review_prompt_v1.md` |
| 最終盲検 | `prompts/final_blind_prompt_v2.md` |
| finding解決・最終合否 | `prompts/pre_blind_resolution_v1.md`、`prompts/post_blind_resolution_v1.md`、`prompts/targeted_adjudication_v1.md`、`prompts/final_review_spec_v3.md` |
| 局所修整 | `prompts/targeted_correction_review_v1.md`、`scripts/targeted_correction.py` |
| source-first・semantic gate | `prompts/source_first_audit_v2.md`、`prompts/semantic_resolution_gate_v1.md` |
| 工程・形式・整合 | `scripts/run_word.py`、`scripts/workflow_revision.py`、`scripts/checker_subagent_gate.py`、`scripts/entry_workflow_guard.py`、`scripts/validate_entry.py`、`scripts/validate_repository.py` |
| Notion・改善 | `prompts/notion_spec_v1.md`、`process_improvement/README.md`、`prompts/process_improvement_learning_delta_v2.md`、`scripts/process_improvement.py` |

旧工程文書は `backups/2026-08-25-process-refactor/`、規範移設表は
`prompts/migration_table_v5_to_v6.md` を参照する。
