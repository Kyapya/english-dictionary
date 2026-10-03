# 旧工程の入口（通常作業では使わない）

2026-10-03以降の通常作業は `AGENTS.md` と `docs/workflow_integrity.md` に従う。
ここにある文書・ツールは過去のrunの再開・検証・問題調査のために残している。
存在することを理由に新規記事へ追加適用しない。

## 保存された指示

- compact A/B工程: `docs/legacy_compact_AGENTS.md`、
  `docs/legacy_compact_workflow_integrity.md`。
- それ以前の工程: `docs/legacy_AGENTS.md`、`docs/legacy_workflow_integrity.md`、
  `docs/legacy_workflow_readme.md`。
- 旧生成仕様の手順込み原本: `prompts/legacy_entry_spec_v5.md`。
- 旧複数語queue: `docs/legacy_multi_word_workflow.md`、
  `docs/legacy_multi_word_publication.md`。

上の保存文書に「現行」「通常」「必須」とあっても、その文書が使われた当時の意味である。
旧runのprompt/hashを、新しい内容基準に合わせて再計算・上書きしない。
厳密な当時の再現が必要なら、対象runが使用したcommitのworkspaceを使う。

## 明示的な互換コマンド

`python scripts/run_word.py --resume <保存済みrun>` は保存済みの契約を使う。
compactの操作は `scripts/compact_workflow.py`、旧v3は `run_word.py --legacy ...`。
旧compact開始の再現には `start_word.py <word> --compact` を使う。
旧複数語queueのstatus/recover/dispatch等は `start_words.py --legacy ...`。
通常の開始コマンドにこれらのflagを付けない。

旧validatorは必要な調査範囲に対して明示実行できる。通常CI・Notion同期からは
呼ばない。互換性のユニットテストは残し、歴史の書き換えによって通さない。
局所修正用の旧 `targeted_correction.py` も過去記録の再現専用である。

通常工程へ移るときは最新本文と未解決の具体的指摘を引き継ぎ、旧runの状態を
新工程のPASSへ変換しない。過去のPASSも新しい本文の点検済み証明には使わない。
