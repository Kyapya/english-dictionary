# English Dictionary

英語学習者向けの1語1記事Markdown辞書。記事は `entries/`、受付は
`queue/words.csv`、レビュー記録は `audits/` に保存する。

## 単語追加

```bash
python scripts/environment_preflight.py
python scripts/start_word.py suspicion --publish-mode connector --reviewer-mode handoff
```

専用branchの新規runは `compact_review_v1`。下書きとsource inventoryを作り、
`python scripts/compact_workflow.py --resume <run> --request A` および `--request B`
で独立したレビューを準備する。A/Bの原応答を別の実行コンテキストから保存して受領し、
修正した内容areaだけを再確認する。`--resume <run>` で公開判定を確認し、
`--finalize` で本文・queue・audit・runを揃える。CI成功後にPRをマージし、同期を確認する。
具体的なコマンド、受領schema、旧runの互換性は [AGENTS.md](AGENTS.md) を参照。

複数語は `scripts/start_words.py` の同じ入口を使用する。旧7パスworkflowは
保存済みrunの再開・検証専用。履歴上の旧工程は
[legacy workflow](docs/legacy_workflow_integrity.md) に残す。

## 内容

本文の簡潔な執筆チェックリストは
[prompts/compact_entry_content_v1.md](prompts/compact_entry_content_v1.md)。
形式と学習内容の詳細な既存仕様は `prompts/entry_spec_v5.md` に残す。
機械検証は `scripts/validate_entry.py` とCIで行う。
