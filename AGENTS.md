# English Dictionary — 通常の作成・修正

通常運用は **作成 → 形式確認 → 新規チャットで独立点検 → 必要箇所だけ修正 → 公開**。
品質基準は維持し、工程を証明するための監査管理は通常作業から外す。

## 最初に読むもの

- 作成者: このファイルと `prompts/entry_spec_v5.md`（完成物の内容・書式の正本）。
- 点検者: `prompts/independent_entry_review.md`、同じ完成物基準、対象本文だけ。
- 状態・公開・再開の詳細: `docs/workflow_integrity.md`。

## 実行

1. 最新mainと対象記事・未統合の作業を確認し、専用branchで作業する。
   1語でも複数語でも `python scripts/start_words.py alpha "take off"` で対象を整理できる。
   `scripts/start_word.py` / `scripts/run_word.py` も通常は同じ軽量な入口を使う。
   これらは対象と手順を表示するだけで、記事生成・レビュー実行・run作成はしない。
2. ルールに沿って本文を書く。必要な辞書・用例確認と執筆中の推敲は行う。
   既存記事の局所修正では、依頼外の語義・構成を作り直さない。
3. `python scripts/validate_entry.py <記事パス>` で形式を確認する。
   作成者は、点検前の記事を `review_ready` / `checked: false` として渡す。
4. 新規チャットまたは作成文脈を引き継がない別コンテキストで本文を点検する。
   `python scripts/simple_workflow.py --review-entry <記事パス>` で引渡し文を作成できる。
   このコマンドは点検依頼を組み立てるだけであり、独立点検の実行ではない。
   実行できなければ未点検と明示し、自己点検で代用して合格扱いにしない。
5. 指摘の妥当性を確認し、実際の誤り・重要な欠落・誤解を招く説明を修正する。
   修正後は変更箇所と関連部分を確認する。好みの言い換えは任意であり、
   固定回数の往復や、指摘件数のノルマは設けない。
6. 独立点検と必要な修正が済んだ記事だけを `checked` / `true` にする。
   front matterと `queue/words.csv` を揃え、形式・repository検証を実行する。
   PRのCI成功と権限・承認範囲を確認してマージし、記事変更時はNotion同期も確認する。
   通常Git pushの資格情報がない環境では認証済みコネクタを使う。

## 通常作業に追加しないもの

必須の自己監査、A/Bレビュー、7パス、cold/final blind、最終LLM審査、
source inventory、監査manifest、レビューhash・実行ID・時系列証明、
heartbeat、固定の調査件数・工程回数、PI記録の作成義務は設けない。
実際に調べること、重要な誤りを直すこと、未実施を未実施と報告することは省かない。

旧run・原応答・失敗履歴は書き換えない。旧工程は `docs/legacy_workflows.md` に隔離する。
古い指示・スクリプトが存在しても、新しい通常作業の追加要件にはしない。
