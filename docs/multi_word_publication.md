# 複数語の公開

通常工程と状態の意味は `docs/workflow_integrity.md` に従う。
最新mainを基点とする専用branchを使い、他語の未完了作業を記事PRに混ぜない。
同じ語の未統合変更があれば、別の完成版を競合して作らず、その差分を確認する。

点検・修正済みの語だけ `checked` / `true` にし、対応するqueue行を更新する。
PR単位で最新headのCI成功を確認してから、承認範囲内で順にマージする。
旧監査のrun、raw、失敗記録は公開のために書き換えない。

Notion同期のconcurrencyと `cancel-in-progress: false` は維持する。
大量のPRを一斉マージせず、同期結果を確認しながら統合する。
同じ記事の連続改訂では先の同期完了を確認してから後続版を公開する。
同期失敗時は既存のworkflow_dispatchで対象記事の最新mainを指定して再実行する。
記事の点検完了、PRのマージ、Notion同期成功は別の事実として報告する。

旧queue/jobの版固定や公開用台帳は `docs/legacy_multi_word_publication.md` に保存し、
新しい通常作業には適用しない。
