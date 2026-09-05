# post_blind_resolution_v1

この段階は、pre-blind修正と影響範囲checker再検査後の最新版本文に対する
final blind findingだけを裁定する。checker/cold findingを再裁定しない。

## 判断と再確認

- 各final blind findingを重複なく1回だけ `adopted` または `rejected` とする。
- 未判定、hold、条件付き解決は完了扱いにしない。
- 採用修正がなければ、現在のfinal blindを終端検査として保持する。
- 採用修正がある場合、`scripts/workflow_revision.py` で影響範囲を決め、必要checkerだけを再検査した後、必ず新本文に対して独立final blindを再実行する。
- 新final blindはchecker/cold finding、resolution、生成文脈を受け取らない。
- final attempt上限で収束しなければ `needs_review`、checked falseで停止し、基準を緩めない。

## 出力

`post_blind_resolution_v1` JSONの `resolutions` を返す。各要素は `id`、同値の
`finding_id`、`status: resolved`、`disposition: adopted | rejected`、`rationale` を持つ。
採用修正時は `post_blind_verification_v1` に最新本文hash、checker recheck manifest、
再実行final blindのhash・時刻・attempt番号を記録する。
