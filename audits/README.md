# 内容監査ファイル

`audits/` は、辞書記事の内容監査を会話内の自己申告ではなく、機械検証可能なJSONとして保存する場所です。`entries/` 以下と同じ相対パスを使い、拡張子だけを `.json` にします。

例: `entries/a/apple.md` に対する監査は `audits/a/apple.json`

## 作成と検証

```bash
python scripts/content_audit.py build entries/a/apple.md
python scripts/content_audit.py validate entries/a/apple.md
```

`build` は現在の本文から、本文ハッシュと監査対象一覧を生成します。生成後、次の3担当が互いに異なる実行・担当識別子で各欄を完成させます。

1. `normal_checker`: 全監査対象の通常チェック、独立棚卸し、根拠台帳、コールドレビュー候補の解決を記録する。
2. `cold_reviewer`: 通常仕様が想定していない問題候補を独立に発見する。
3. `final_adjudicator`: 本文を変更せず、全target、全独立候補、全findingと根拠を個別判定し、最終合否を記録する。

記事本文を変更すると本文ハッシュと監査対象一覧が変わるため、以前の最終判定は無効になります。既存記事は一括して空の監査を付けず、次に本文を変更するときからこの形式へ移行します。

詳細な責務と判定基準は `prompts/check_spec_v5.md` と `prompts/final_review_spec_v1.md`、JSONの必須項目は `scripts/content_audit.py` を正本とします。
