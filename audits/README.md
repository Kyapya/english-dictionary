# 内容監査ファイル

`audits/` は、辞書記事の内容監査を会話内の自己申告ではなく、機械検証可能なJSONとして保存する場所です。`entries/` 以下と同じ相対パスを使い、拡張子だけを `.json` にします。

例: `entries/a/apple.md` に対する監査は `audits/a/apple.json`

## 作成と検証

```bash
python scripts/content_audit.py build entries/a/apple.md
python scripts/content_audit.py validate entries/a/apple.md
```

`build` は現在の本文から、本文ハッシュ、単一箇所の監査対象 `targets`、記事横断の監査対象 `relations` を生成します。新規または変更する監査は `content_audit_v2` を使い、次の3担当が互いに異なる実行・文脈識別子で各欄を完成させます。既存の未変更 `content_audit_v1` は互換読み込みされます。

1. `normal_checker`: 全target・relationの通常チェック、独立棚卸し、主張単位の根拠リンク、コールドレビュー候補の構造化された解決を記録する。
2. `cold_reviewer`: 通常仕様が想定していない問題候補を独立に発見する。
3. `final_adjudicator`: 先に本文だけで盲検棚卸しと問題探索を行い、出力を固定した後に監査記録を開き、全target・relation・棚卸し候補・finding・根拠を個別判定して最終合否を記録する。

盲検審査の候補内容と問題候補を記録したら、監査記録を最終審査担当へ見せる前に次を実行します。最終審査側候補のtarget・根拠リンクIDは監査記録を開いた後の照合データなので、固定後に追加できますが、候補の表層形・フレーム・意味・収録判断・理由は変更できません。

```bash
python scripts/content_audit.py seal-blind audits/a/apple.json
```

監査ファイルには少なくとも次が残ります。

- 三者のrun ID、context ID、開始・終了時刻、本文・promptハッシュ、文脈モード、入力物一覧。
- 自動生成された全targetと全relation、および通常チェックと最終審査の個別判定。
- 通常チェックと最終審査が別々に作った棚卸し、および両者の双方向比較。
- 資料台帳 `evidence` と、対象主張・該当箇所・支持内容・反例確認を結ぶ `evidence_links`。
- コールドレビューfinding、問題確認、必要変更、影響範囲、実施変更、残存リスクを含むresolution。
- 盲検出力のハッシュ、照合後の `PASS` または `REJECT`、blocker。

`REJECT` も完了した監査結果として保存し、記事は `needs_review`、checked `false` にします。同一・定型的なnotesは偶然一致し得るため、検証スクリプトは文面の一致だけでは拒否しません。

記事本文を変更すると本文ハッシュ、監査対象一覧、盲検出力の固定値が変わるため、以前の最終判定は無効になります。既存記事は一括して空の監査を付けず、次に本文または監査を変更するときからこの形式へ移行します。

詳細な責務と判定基準は `prompts/check_spec_v5.md` と `prompts/final_review_spec_v1.md`、JSONの必須項目は `scripts/content_audit.py` を正本とします。
