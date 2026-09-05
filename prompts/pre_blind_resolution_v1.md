# pre_blind_resolution_v1

通常7 checkerとcold reviewが同じ固定draftについて出したfindingだけを裁定する。
final blindの入力・出力・findingはこの段階へ渡さない。

## 判断と修正

- 各findingを重複なく1回だけ `adopted` または `rejected` とし、具体的理由を記録する。
- `adopted` を一括して本文へ反映し、修正前後の本文SHA-256と記録時刻を保存する。
- 未判定、hold、条件付き解決は完了扱いにしない。
- 修正前後を `scripts/workflow_revision.py` で比較し、変更意味単位と失効checkerをコードで決める。LLMの自己申告だけで再検査範囲を狭めない。
- 分類不能、複数section、語義統合・分割、品詞追加削除は全7 checkerを失効させる。
- source-first資料・fact・research roundを自動追加しない。既存根拠で解決不能なら未解決事項として停止する。

## 出力

`pre_blind_resolution_v1` JSONを返す。`resolutions` の各要素は `id`、同値の
`finding_id`、`status: resolved`、`disposition: adopted | rejected`、`rationale` を持つ。
修正記録は別の `pre_blind_revision_v1` artifactとし、`input_body_sha256`、
`output_body_sha256`、`recorded_at`、`changed_units`、`invalidated_passes`、
`full_recheck` を持つ。
