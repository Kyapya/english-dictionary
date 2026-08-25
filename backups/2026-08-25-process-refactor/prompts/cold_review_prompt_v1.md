# Cold review prompt v1

英単語解説として問題がないか、記事全体を横断して徹底的に走査し、内容上の問題を前提なしで指摘してください。各文の正誤だけでなく、語義の分け方・境界・重複と、学習者が説明から誤った一般化をしないかも確認してください。また、断定的な主張に対して反例を探すことで記述に問題が無いか確認をしてください。

返答はJSONオブジェクトとし、`summary` と `findings` を含めてください。問題候補がなければ `findings` は空配列にし、`summary` に「問題候補なし」と明記してください。

各findingには次を含めてください。

- `id`
- `location`
- `severity`: `high` / `medium` / `low`
- `description`
- `reason`
- `suggested_direction`
- `scope_anchors`

`scope_anchors` は問題が現れる箇所ごとに分け、各要素へ `id`、本文からそのまま抜き出した `exact_quote`、人が位置を確認するための `location_hint` を記録してください。コアイメージと詳細定義など複数箇所に同じ問題がある場合は、1つのlocationへまとめず、別々のanchorにしてください。target ID、relation ID、監査履歴、既知の指摘は与えられていないため推測しないでください。

記事本文は変更しないでください。
