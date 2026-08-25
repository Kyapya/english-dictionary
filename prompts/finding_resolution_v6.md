# finding_resolution_v6

この段は、checker、cold review、固定済みfinal-blindの全findingを、最新版の記事本文とsource inventoryに照らして個別に解決する。生成時文脈をcold reviewやfinal-blindへ逆流させてはならないため、blind sealの後にnormal resolution contextで実行する。順序、入力分離、本文hash、finding集合の完全一致は `scripts/run_word.py` と `scripts/generate_audit_manifest.py` が強制する。

## 判断

- findingごとに `adopted` または `rejected` を選び、根拠を記録する。
- `adopted` は本文を修正し、その記事だけをGit commitした後、新しい本文hashでchecker、cold、final-blind、seal、resolutionを再実行する。seal済み本文をその場で書き換えない。
- `rejected` は、findingが本文または根拠に適用できない理由を具体的に記す。単なる好み、無根拠な否定、まとめての棄却は禁止する。
- 未判定、hold、条件付き解決は出力しない。解決できないfindingがあればfinal reviewはREJECTとなる。

## 出力

`resolutions_v1` JSONとして `resolutions` 配列を返す。各要素は `id`、同値の `finding_id`、`status: resolved`、`disposition: adopted | rejected`、`rationale`、最新版本文の `resolved_body_sha256` を持つ。入力されたfinding IDを重複なくちょうど1回ずつ収録する。本文やfindingが0件なら空配列とする。
