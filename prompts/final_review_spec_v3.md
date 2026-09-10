# final_review_spec_v3

最新版本文と固定済みレビューを照合し、最終合否を判断する。正常項目の合格理由を大量に作る時間を、本文・資料・修正箇所の実読へ戻す。品質基準、全件の判定、独立性、未解決事項を残さない条件は維持する。

## 照合

- `inventories` / `response_template` を対象IDの正本とする。欠落を空集合と推測しない。未判定は合格ではない。
- 事実、語法、発音、例文、訳が正しく、主要な品詞、語義、派生・転換、専門用法、完全な統語フレームが過不足なく扱われていることを確認する。語義境界、コアイメージ、定義、語法、コロケーション、語彙関係に矛盾がないこと。例文と訳の意味役割、作用方向、肯否、数量、時制・法、条件、修飾範囲、レジスターを確認する。
- 証拠の内容確認は evidence checker が本文・claim・外部資料を照合した結果を使う。合格理由の長さや findings が0件であることは正確さの根拠にしない。高リスク主張の反例・矛盾・適用範囲が未確認、資料にアクセスできない、主張と根拠が食い違う場合は `insufficient_evidence` として解決するまで合格にしない。
- すべてのfindingについて、採用修正が最新版へ反映され、不採用理由が資料と仕様に支えられ、修正の影響が再検査されているかを確認する。修正前の説明だけで解決扱いにしない。
- 固定済みblind candidateの各 `semantic_assertion` を最新版へ適用し、候補の境界・作用方向・包含/除外関係・一般化範囲に反する記述がないことを確認する。
- final reviewは全面レビューを繰り返す工程ではない。具体的な矛盾・未解決事項・修正確認に注力する。疑義のある外部資料は該当箇所を再確認する。hash、ID集合、時系列、seal、再検査・再利用条件は `scripts/run_word.py`、`scripts/workflow_revision.py`、`scripts/generate_audit_manifest.py` の検証を使い、説明文を作り直さない。

## 出力

`final_review_v3` JSONを返す。対象ID・判定・必要な束縛情報を記録する。

`response_template` の結果欄と `_output_metadata` を使う。同じ結果を `adjudication` 配下へ再掲したり、固定済み `independent_candidates` を応答へ複製したりしない。

- `target_results`、`relation_results`、`normal_candidate_results`、`blind_candidate_results`、`evidence_checks`、`source_inventory_results` は全IDを重複なく含み、各 `status` を `pass` または `fail` とする。
- 正常な `pass` の `notes` は省略する。本文の全文引用、対象ごとの「問題なし」の言い換え、合格理由の水増しは不要。判定を初期値のpassで一括補完してはならない。
- `fail` は `notes` に問題と必要な修正を短く記す。引用は問題の特定に必要な範囲だけにする。
- `finding_results` は各findingを一度だけ含め、`pass` でも最新版のどの修正または不採用根拠を確認したかを `notes` に短く残す。元のfinding・resolutionを全文再掲しない。
- `blind_candidate_results` は全 `assertion_ids` と `verified_body_sha256` を保持する。candidateのpassは列挙した全assertionの確認を意味する。一つでも未確認または不成立ならfailとする。assertionごとの合格理由表を別に作らない。
- `source_inventory_results` の `union_id` は `id` と一致させる。
- `checker_recheck_results` / `chronology_results` の説明表は作らない。機械検証の原記録を参照する。
- `decision` は `pass | reject`、`blockers` と全体の非blocking `notes` は配列とする。本文は変更しない。

## 合否

全対象がpass、未解決・hold・`insufficient_evidence`・未検査範囲・無効pass・判断衝突・未確認の修正影響が0件、blockerが0件の場合だけPASSとする。条件付き合格は使わない。

誤り、主要語義・構文の欠落や過剰収録、根拠との矛盾、必須内容の違反、未判定・未解決事項があればREJECTとする。blockerには対象ID、問題、必要な修正を記録し、修正・影響範囲の再検査・final blind再実行へ戻す。`REJECT` は審査失敗ではなく、問題を検出した正常な成果である。分類粒度や任意の表現改善だけを理由にrejectせず、非blocking noteとする。

v1/v2は旧runの検証・再現専用。保存済みraw出力は書き換えず、そのschemaの条件で検証する。
