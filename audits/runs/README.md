# Reviewer raw outputs

新規runは `audits/runs/<initial>/<slug>/<cycle-id>/` に、source inventory、6パスの集約、cold review、resolution、final blind、blind seal、final reviewを別々のraw JSONとして保存する。各rawはrun/context ID、入力本文・prompt hash、入力artifact、時刻を持ち、`scripts/generate_audit_manifest.py` が検証する。

このディレクトリへ新しい `revision-00N.md` は保存しない。本文改稿の正本は、`scripts/run_word.py` が作る記事単独のGit commitである。既存のraw JSON、revision snapshot、historyは過去監査の参照資産なので編集・移動・削除しない。
