# English Dictionary

英語学習者向けの1語1記事Markdown辞書。記事は `entries/`、記事の状態は
`queue/words.csv` で管理する。`audits/` は旧工程の履歴であり、新規作成の必須成果物ではない。

## 通常の進め方

**ルールに沿って作成 → 形式確認 → 新規チャットで独立点検 → 必要箇所だけ修正 → 公開**。

```sh
# 対象パスと手順を表示する。記事・監査runは自動生成しない。
python scripts/start_words.py alpha beta "take off"
# 1語の既存入口も同じ軽量な動作
python scripts/start_word.py alpha
# 本文形式の確認
python scripts/validate_entry.py entries/a/alpha.md
# 新規チャットへ渡す「点検指示＋完成物基準＋本文」を標準出力へ
python scripts/simple_workflow.py --review-entry entries/a/alpha.md
```

作成者は [AGENTS.md](AGENTS.md) と
[完成物の仕様](prompts/entry_spec_v5.md) を読む。
点検者は [独立点検の指示](prompts/independent_entry_review.md) に従う。
[状態と公開のルール](docs/workflow_integrity.md) と
[複数語の扱い](docs/multi_word_workflow.md) は必要な場面で参照する。

独立点検を実行できない場合は `review_ready` / `checked: false` のまま残す。
点検依頼の生成やCI成功は、本文の独立点検が済んだ証拠ではない。

CIは自動テスト、記事形式、queue整合を確認する。レビューのhash・実行ID・
監査台帳は要求しない。Notionは従来どおり `checked` / `final` かつ `checked: true`
の記事だけを同期する。

旧runの再現が必要な場合だけ [旧工程の入口](docs/legacy_workflows.md) を使う。
従来の詳細は [legacy workflow](docs/legacy_workflow_integrity.md) に保存されている。
