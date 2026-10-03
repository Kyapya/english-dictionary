# English Dictionary project router

英単語の追加は1語でも複数語でも `scripts/start_words.py` から受ける。
未完了の同一語runを発見した場合は新runを作らず同じrunを再開する。
複数語受付・独立workspaceは `docs/multi_word_workflow.md` に従う。

## 新しい通常工程: compact_review_v1

1. `scripts/environment_preflight.py` を実行し、専用branchで
   `scripts/start_word.py <word> --publish-mode connector --reviewer-mode handoff`
   を起動する。通常Git pushの資格情報がないと分かっている環境では試さない。
2. 主要辞書の独立した2系統以上を照合し、`prompts/compact_entry_content_v1.md`
   に従って本文を執筆する。根拠はsource inventoryに対応付ける。
   `source_inventory_v2` の固定件数上限は旧runのみに適用する。追加調査は未解決の
   重要な主張に集中し、検索コストと採用資料数を別に記録する。
3. `scripts/compact_workflow.py --resume <run> --request A` と `--request B`
   で、同一本文から独立したレビュー依頼を作る。Aは本文の英日・語義・構文・例文・
   語彙関係・発音等、Bは外部資料との照合・主要語義の欠落を確認する。
   原応答を保存し、別の実行コンテキストで担当する。作成者の自己合格判定を渡さない。
4. `--ingest A/B --request-path <path> --raw <path> --execution-id <id> --model <model>`
   で受領する。形式だけの既知の別名は原応答を変えず派生記録で正規化する。
   出所を確認できない原応答を機械的に合格へ補完しない。
5. blockingを解消し、minorは一括修正または理由付き不採用、editorialは任意とする。
   修正したareaだけのレビューを更新する。`--resume <run>` で未被覆・未解決を確認。
   同一争点の修正後確認が2回続いても解消しない場合、限定裁定に切り替える。
   主要用法を削って完了率を稼がない。
6. 公開判定がpassなら `--finalize` でentry・queue・audit・runを同じ本文版に揃える。
   CIとPRを確認し、承認済みならマージとNotion同期の状態まで確認する。
   公開判定のためだけに別のLLM最終レビューを起動しない。

`prompts/compact_review_contract_v1.json` はA/Bのreview schema正本。
対象内容の依存hashと本文版hashは `scripts/review_dependency_v4.py` で分離する。
旧レビューのrawと現在版への機械的再利用記録は別々に保存する。
出典・修正の未確認範囲はPASSにしない。本文形式と既存サイト・Notion互換性を守る。

## 旧runと局所修正

旧 `workflow_contract_version` のrunは旧runner/validatorで読み、その工程を勝手に
新版PASSへ書き換えない。`run_word.py --resume <legacy-run>` は旧版へ分岐する。
旧7パス、cold、final blind、LLM final reviewは新規runの必須工程ではない。
保存済みの旧runを移行する場合は `compact_workflow.py --migrate <old-run>` で
原レビュー、採用済み指摘、最新版本文を機械照合し、別のmigration記録を作る。
十分性を検証できない範囲は個別に確認する。旧版の運用詳細は
`docs/legacy_workflow_integrity.md` に残す。

`checked` / `final` 記事の具体的な局所修正は
`prompts/targeted_correction_review_v1.md` と `scripts/targeted_correction.py` を使う。
全面改稿は通常工程。PIは専用LLM工程を作らず、関連する既存出力で取込む。
