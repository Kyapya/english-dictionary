# Reviewer raw outputs

`content_audit_v3` では、通常レビュー、コールドレビュー、最終ブラインド判定、最終照合の出力原文をここへ保存する。

パスは `audits/runs/<entry>/<cycle-id>/<stage>.<ext>` とし、監査JSONの `current_cycle.raw_outputs` から、ファイルの SHA-256、入力本文 SHA-256、プロンプト SHA-256、run ID、context ID を参照する。同じファイルを複数ステージで共有してはならない。

本文を修正した場合は `body_revisions` を追記する。完了済み監査を再実行するときは `start-cycle` で旧監査を `audits/history/` に原文のまま退避し、新しい cycle を開始する。既存の履歴ファイルは編集しない。
