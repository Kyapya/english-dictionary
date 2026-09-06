# Process-improvement learning delta v2

この指示は生成担当または既存の調整役だけが使う。通常checker、cold review、final blindへは渡さない。記事の内容基準、検査数、合格条件、レビュー独立性、公開条件を変更しない。

## 入力知見

run内の `process_improvement_input_path` に固定された選択済み知見だけを参照する。現行の正式仕様と今回の明示的なユーザー指示が常に優先する。入力に含まれただけで、知見を実行した、効果があった、再発を防いだとは記録しない。

## 完了出力

この工程の既存JSON出力のうち、生成では `generation.json`、事前裁定では
`pre_blind_resolution.json`、事後裁定では `post_blind_resolution.json` の1ファイルだけに、
次のトップレベル項目を追加する。同じ工程の複数ファイルへ複製しない。

```json
{
  "entry_features": ["必要に応じた汎用的な特徴タグ"],
  "learning_delta": {
    "schema_version": "process_improvement_learning_delta_v2",
    "reviewed": true,
    "items": []
  }
}
```

`entry_features` は生成工程だけで出力し、品詞・多義性・専門領域など、実際に確認できた特徴だけを書く。未知の特徴を推測で追加しない。

`items` は、今回新しく確認した事実から、別の見出し語にも使える具体的行動が得られた場合、既存知見への版付き観測がある場合、または根拠付きの改訂・停止・正式統合判断を行う場合だけ埋める。知見がなければ空配列にする。項目自体を省略した場合は「知見なし」ではなく「整理未了」と扱われる。

### 新規候補または使用可能知見

`action: create` と `record` を返す。単語固有の正解、作業日記、既存仕様の転載、「注意する」のような標語、根拠のない一般化は返さない。初回の有用なつまずきでも候補にでき、escaped defect・再発回数・重大度は必須ではない。

`active` にできるのは、採用理由、採用根拠、現行仕様との整合性、適用条件・除外条件を調整役が確認した場合だけである。未裁定finding、原因推測、ユーザーの疑問をそのまま `active` にしない。不足があれば `candidate` とし、不足事項を `validation.rationale` または `problem.uncertainties` に残す。

`record` は `title`、`status`、`category`、`priority`、`problem`、`delivery`、`validation`、`evidence_observation` を持つ。`problem` は `observed`、`action`、`reusable_because`、`conditions.required_tags`、`conditions.excluded_tags`、`exclusions`、`uncertainties` を持つ。`delivery.recipients` は `generator` / `coordinator`、`delivery.phases` は対象工程を指定する。`validation` は `decision`、`rationale`、`evidence_refs`、`specification_context` を持つ。

### 観測

既存知見に結果を戻す場合は `action: observe`、`knowledge_id`、実際に渡された `knowledge_version`、`outcome`、短い `observation`、必要なら実測 `metrics` を返す。`outcome` は `action_confirmed`、`no_opportunity`、`recurred`、`no_recurrence_observed`、`burden`、`unknown`、`supporting_evidence` のいずれかとする。未計測値は `null` とし、0に置き換えない。

### 改訂・統合・退役

意味の変更は `action: revise` とし、`knowledge_id`、`expected_version`、改訂後の完全な `record` を返す。版を増やさずに本文や状態を上書きしない。`integrated` は正式仕様・コードと検証根拠が確認できた場合、`retired` は誤り・悪影響・重複・前提消失等の理由と根拠がある場合だけ使う。検出欠陥0、未使用期間、配信回数だけでは退役させない。

原因が確定していない場合は、事実と推測を分けて `problem.uncertainties` に「原因未確定」と明記する。知見整理のための追加レビューや追加LLM呼び出しは行わない。
