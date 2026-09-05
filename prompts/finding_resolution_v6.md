# finding_resolution_v6

この文書は旧runの読み取り互換用である。`workflow_improvement_v1` 以後の新規runは、checker/cold findingを `prompts/pre_blind_resolution_v1.md`、final-blind findingを `prompts/post_blind_resolution_v1.md` で別々に裁定する。旧runへ新しい曖昧なfallbackを設けず、既存artifactはこのv6契約で引き続き検証する。

## 判断

- findingごとに `adopted` または `rejected` を選び、根拠を記録する。
- 旧runの `adopted` は従来契約どおり扱う。新runでは意味上の影響範囲checkerだけを失効させ、cold reviewを全面再実行せず、修正後本文をfinal blindへ渡す。
- `rejected` は、findingが本文または根拠に適用できない理由を具体的に記す。単なる好み、無根拠な否定、まとめての棄却は禁止する。
- 未判定、hold、条件付き解決は出力しない。解決できないfindingがあればfinal reviewはREJECTとなる。

## 出力

`resolutions_v1` JSONとして `resolutions` 配列を返す。各要素は `id`、同値の `finding_id`、`status: resolved`、`disposition: adopted | rejected`、`rationale`、最新版本文の `resolved_body_sha256` を持つ。入力されたfinding IDを重複なくちょうど1回ずつ収録する。本文やfindingが0件なら空配列とする。
