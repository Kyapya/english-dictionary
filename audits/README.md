# 内容監査ファイル

`audits/` は、辞書記事の内容監査を会話内の自己申告ではなく、機械検証可能なJSONとして保存する場所です。`entries/` 以下と同じ相対パスを使い、拡張子だけを `.json` にします。

例: `entries/a/apple.md` に対する監査は `audits/a/apple.json`

## 作成と検証

```bash
python scripts/content_audit.py build entries/a/apple.md
python scripts/content_audit.py validate entries/a/apple.md
```

`build` は現在の本文から、本文ハッシュ、単一箇所の監査対象 `targets`、記事横断の監査対象 `relations` を生成します。新規または再審査する監査は `content_audit_v3` と `semantic_resolution_v2` を使い、次の3担当が互いに異なる実行・文脈識別子で各欄を完成させます。既存の未変更 `content_audit_v1` と `content_audit_v2` は互換読み込みされますが、semantic gateのない旧v3を `checked` / `final` の根拠にはできません。

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
- 資料台帳 `evidence` と、対象主張・該当箇所・短い引用または忠実な要約・支持内容・反例確認を結ぶ `evidence_links`、最終審査の全 `evidence_checks`。
- 本文引用付き `scope_anchors` を持つコールドレビューfindingと、全anchorを1対1で引き継いだresolution。
- 盲検出力のハッシュ、照合後の `PASS` または `REJECT`、blocker。
- `current_cycle.body_revisions` による各レビュー入力本文のハッシュ・本文スナップショット系列と、`audits/runs/` に保存した通常・コールド・最終盲検・最終照合の原出力参照。
- 既知の見逃し類型に対する `escaped_defects` と、汎用分類表 `escaped_defect_taxonomy.json` の全分類を確認した `regression_checks`。

`REJECT` も完了した監査結果として保存し、記事は `needs_review`、checked `false` にします。同一・定型的なnotesは偶然一致し得るため、検証スクリプトは文面の一致だけでは拒否しません。

relationは件数を網羅性の代用にしません。語義所属は各target自身の `sense` で表し、全語義ペアやコアイメージ×全語義の直積は生成しません。語義ペアは記事内の明示的な相互参照が混同リスクを示す組だけ生成します。一方、語義見出し↔詳細定義、定義↔類義語・反意語、コアイメージ↔明示語義と詳細説明、記事全体の学習リスクは必須relationとして生成します。生成されたrelationは件数にかかわらず全件を通常・最終の両方で判定します。

`evidence_links` は一般的な資料名だけで済ませず、`locator_kind`、`source_detail`、`source_excerpt_or_summary`、`applicability`、`counterexample_method` まで主張単位で記録します。地域差、専門・制度用法、語義境界、頻度、語彙関係、絶対表現など `evidence_policy: two_sources_or_primary` の対象は、IDが違うだけの同一引用元ではなく独立した2資料、または当該主張へ直接適用できる一次資料を必要とします。

通常・コールド・最終盲検・最終照合の原出力は別々のJSONで保存し、候補、target/relation判定、scope anchor、finding、evidence check、inventory check、blocker、decisionを監査マニフェストと項目単位で一致させます。件数集計だけの原出力は認めません。

見逃しが判明した旧PASSは `review_invalidations.json` へentry pathと本文SHA-256を登録し、本文を変更しなくても記事とqueueを `needs_review`、checked `false` へ戻します。次回審査で新しいsemantic gateを完成させるまで再びcheckedにはできません。

記事本文を修正した場合は同じ監査欄の本文ハッシュを上書きせず、まず次のように新しいcycleを開始します。コマンドは旧監査の原文を `audits/history/` に退避し、そのSHA-256を追記して、新しい本文から未判定のcycleを作ります。

```bash
python scripts/content_audit.py start-cycle entries/a/apple.md --reason "definition corrected"
```

同じcycle内でコールドレビュー後に本文を直す場合も、`body_revisions` へ新しい本文ハッシュと本文スナップショットを追記します。通常・コールド実行は各自が実際に読んだrevisionを参照でき、最終盲検・最終照合と監査の `body_sha256` は最新版に一致させます。CIは各スナップショットの実体、変更前の完了済み監査が履歴へ原文のまま追加されていること、過去の履歴prefixが不変であること、新しいcycle IDで再審査されたことを検証します。

```bash
python scripts/content_audit.py add-revision entries/a/apple.md --reason "adopted cold-review correction"
```

既存記事は一括して空の監査を付けず、次に本文または監査を変更するときからv3とsemantic gateへ移行します。Notion同期の直前にも `validate-sync` が完成状態の記事へ有効な監査を要求します。PRで変更された記事はCIで現行gateが強制され、未変更のv1/v2記事を手動再同期するときだけ互換検証を使います。

詳細な責務と判定基準は `prompts/check_spec_v5.md` と `prompts/final_review_spec_v1.md`、JSONの必須項目は `scripts/content_audit.py` を正本とします。
