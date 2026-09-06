# process-improvement v2 rebuild 実装報告

- 実施日: 2026-09-06
- 実装時の基準SHA: `7cca3bc28b43d7e81940dadf84cb67e0ac8e3a80`
- knowledge epoch: `pi2-2026-09-06`
- 結果: 要求された再構築、空台帳での出荷、通常経路・局所修整経路への接続、A01〜A25を実装・実行した。

## 接続図

| 契機 | 実経路 | 保存／次の利用 |
|---|---|---|
| 公開開始 | `run_word.py` → `run_word_parallel.py` → `run_word_v3.py` | 現epochを読み、generator用の選択済みsnapshotをrun内へ固定する。 |
| 生成・事前裁定・事後裁定 | 既存LLM出力の `learning_delta` → `process_stage_learning()` | 同じ取込処理がreceipt、知見または版付き観測を冪等保存する。 |
| 特徴判明後 | `generation.json.entry_features` → 次のcoordinator工程前に再選択 | 未知条件を一致扱いせず、対象工程の実入力だけを作る。 |
| 中断・失敗・再開 | 保存済みpending event／stage output → resume時のretry | 未保存事実は復元せず、pending・save_errorを成功扱いしない。 |
| 局所修整 | `targeted_correction.py record --learning-delta ...` | 通常経路と同じ取込処理を使い、全体レビューへ戻さない。 |
| 次run | 小さい `index.json` → active・現仕様有効・条件一致レコードのみ読込 | ID・版・recipient・hash・bytesを持つ不変snapshotとして渡す。 |
| 工程完了 | snapshot deliveryとcoordinatorの結果観測を別々に保存 | `observations/` を同じ知見ID・版へ集計し、配信を効果とみなさない。 |

通常checker、cold review、final blindにはPIのsnapshot、元finding、期待結論を渡さない。PI読込に失敗した場合だけ、失敗理由を持つPIなしsnapshotへ退避する。既存guard、7 checker、再検査、公開条件はそのまま維持する。

## 正本と自動処理

- `process_improvement/records/PI2-*.json`: 1知見1レコードの正本。状態は `candidate`、`active`、`integrated`、`retired`。
- `process_improvement/epoch.json`: 世代とリセット証跡。旧本文を含めない。
- `process_improvement/history/`: 意味改訂前の版。旧版の観測を新版へ混ぜない。
- `process_improvement/observations/`: 配信、行動、再発、負担、不明等の不変な実行事実。
- `process_improvement/receipts/`: event単位の冪等取込結果。
- `index.json` と `ACTIVE.md`: 正本から作る派生物。通常入力は `ACTIVE.md` を読まない。

登録、選択、依存確認、snapshot作成、観測、集計、構造検証は機械処理する。一般化の妥当性、`active` 採用、意味改訂、統合、退役は既存の調整役が根拠と適用条件を確認して判断する。検出0件、未使用期間、配信回数から自動退役しない。

## 旧知識のリセット

削除した現行ツリー上の旧知識は `PI-0001`〜`PI-0004` と `process-refactor-v1`、旧 `ACTIVE.md` 本文、`retirement_state.json` である。旧本文をバックアップや新レコードへ複製せず、歴史参照は基準SHAのGit履歴に限定した。過去run内の旧IDは変更せず読み取り互換を維持し、新台帳の検索・入力・集計から除外した。

明示的な `migrate-v2` だけがリセットを行う。同じepochで再実行した場合は、途中で残った旧形式だけを清掃して派生物を再生成し、蓄積済みの `PI2-*` は削除しない。通常起動、CI、resumeは移行を実行しない。

出荷時確認:

- current records: 0
- current observations: 0
- current receipts: 0
- `ACTIVE.md`: 使用可能知見なし

## 主な変更ファイル

| ファイル | 目的 |
|---|---|
| `process_improvement/epoch.json`, `index.json`, `ACTIVE.md`, 各台帳ディレクトリ | 新世代の空台帳、移行証跡、派生表示を確立。 |
| `scripts/process_improvement.py` | 構造検証、明示移行、冪等取込、版管理、対象選択、依存失効、snapshot、観測・集計、根拠付き再確認を実装。 |
| `scripts/run_word_v3.py`, `scripts/run_word.py` | 公開実行経路の開始・工程完了・失敗・resumeとPIを接続し、実入力と費用を記録。 |
| `scripts/targeted_correction.py` | 局所修整の同一取込経路と、receiptに限定した変更検証を追加。 |
| `prompts/process_improvement_learning_delta_v2.md`, `prompts/targeted_correction_review_v1.md` | 既存担当の出力へ小さい判断結果を追加し、追加LLM工程を作らない契約を明記。 |
| `process_improvement/README.md`, `README.md`, `AGENTS.md` | 新運用、上限、責任分界、独立性、エラー退避、CLI例を文書化。 |
| `tests/test_process_improvement.py`, `tests/test_targeted_correction.py`, `tests/test_run_word.py`, `tests/test_source_first_contract_wiring.py` | A01〜A25、公開経路、局所修整、既存安全策、テストデータ分離を検証。 |

旧5レコードと `retirement_state.json` は削除した。関連しない記事、queue、過去run・監査・レビュー結果は変更していない。

## A01〜A25

| ID | 結果 | 実行確認 |
|---|---|---|
| A01 | PASS | 空台帳、通常開始、validate、旧本文非流入。 |
| A02 | PASS | 同一移行の再実行がPI2知見を保持し、途中に残った旧形式だけを除去。 |
| A03 | PASS | 旧record／ACTIVE／退役状態を既定選択・集計から除外。 |
| A04 | PASS | 旧epoch事象を拒否し、現epochの新しい確認だけを取込。 |
| A05 | PASS | escaped defect・再発・重大度なしの初回事象からcandidateを登録。 |
| A06 | PASS | 未裁定・推測をactiveにできない状態遷移と調整役向け指示を確認。意味妥当性の自動保証は主張しない。 |
| A07 | PASS | 単語固有、仕様転載、標語を拒否し、空deltaはrecordを作らない。 |
| A08 | PASS | 別見出し語run Aのactive知見をrun Bへ横断配信。 |
| A09 | PASS | 条件不一致・不明、非active、別世代、要再確認を除外。 |
| A10 | PASS | 公開module経路のguard manifest作成から実generator snapshotの本文・ID・版を検査。 |
| A11 | PASS | checker、cold、final blindの実stage入力にPI pathなし。 |
| A12 | PASS | 局所修整が同一取込関数へ接続し、局所範囲を維持。 |
| A13 | PASS | 欠落をpending、保存済みdeltaをresume retryし、追加LLMを要求しない。 |
| A14 | PASS | 同一event、delta、observationの再取込で増殖なし。 |
| A15 | PASS | ID・版・履歴衝突と中断atomic replaceを検出し、既存recordを保持。 |
| A16 | PASS | Markdown section依存だけを失効させ、無関係なsection変更では維持。 |
| A17 | PASS | hash-only再確認を拒否し、根拠・理由付き再確認を新版として保存。 |
| A18 | PASS | delivery、action、effectを分離し、`null` と実測0を別集計。 |
| A19 | PASS | 旧retirement操作を無効化し、10件超の検出0でもchecker構成を変更しない。 |
| A20 | PASS | run Bのdelivery・結果観測がrun A由来の同一ID・版へ還流。 |
| A21 | PASS | 旧版をhistoryへ固定し、版別観測を分離。 |
| A22 | PASS | integration根拠を必須化し、integratedを通常入力から除外。 |
| A23 | PASS | 8件／8192 bytesの決定的上限、項目非切断、PI専用LLM 0回。 |
| A24 | PASS | 壊れたJSONと型不正indexで明示fallbackし、既存品質guardと7 checkerを維持。 |
| A25 | PASS | 旧監査を読み取れるまま新集計から除外し、全回帰を通過。 |

A08・A10・A20は、空台帳 → synthetic run A事象 → 調整役の採用判断をmockした正規取込 → 別見出し語run Bの公開経路相当 → 実snapshot → B観測の同一版集計 → 依存変更後の除外、という一続きの試験も実行した。このmockは実際のLLMの一般化能力または記事品質向上を証明しない。

## 測定と検証

空の本番台帳に対する `select_knowledge(generator, generation)` を同一ローカルプロセスで200回実行した。

| 指標 | 結果 |
|---|---:|
| 実入力 | 336 bytes |
| 選択件数 | 0 |
| 機械処理時間 中央値 | 0.0609 ms |
| 機械処理時間 p95 | 0.1736 ms |
| PI専用の追加LLM呼び出し | 0 |

時間は `time.perf_counter()` で選択処理だけを測り、待ち時間やLLM処理を含めていない。環境依存の単回測定であり、効率改善率や実運用の品質向上は推測しない。既定上限は1入力あたり8件・8192 bytesで、条件と除外を含む項目単位で採否する。

実行済み検証:

- `python -m compileall -q scripts tests`: PASS
- `python -m unittest discover -s tests -v`: 278 tests, PASS
- `python scripts/validate_entry.py entries`: PASS（既存の分類warningのみ）
- `python scripts/validate_repository.py`: PASS
- `python scripts/check_passes.py validate-router`: PASS
- `python scripts/checker_subagent_gate.py validate --merge-ready`: PASS
- `python scripts/migration_table.py validate`: PASS
- `python scripts/process_improvement.py validate`: PASS
- `python scripts/review_liveness.py regression audits/runs/y/yield/20260826T131200Z-yield02`: PASS（既知の失効理由を期待どおり検出）
- `python scripts/queue_status.py escaped-by-stage`: PASS
- PR用の `entry_workflow_guard`、`content_audit`、`semantic_resolution_gate`、`source_first_audit_gate` のchanged検証: PASS

未実行・未達の受入項目はない。実装テストは接続・分離・保存・再利用を確認したもので、実際の英語解説の品質向上、時間短縮、因果効果は運用後の版付き観測で評価する。
