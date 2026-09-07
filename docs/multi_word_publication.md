# 複数語受付の版固定と公開時の注意

1語・複数語の共通入口は `scripts/start_words.py` の一つだけを使う。
基本操作は `docs/multi_word_workflow.md` を参照する。別の受付実装を併設しない。

## 単語branchへ調整台帳を持ち込まない

受付時、originの公開済み `main` commitを一度照合し、新規jobの `base_sha` に固定する。
control branchのHEADには未統合の受付票や他語のjob状態が含まれ得るため、これを
単語branchの起点にしない。後続語を受付するときにも同じルールを使う。
remote照合はqueueロックの外で行い、他の配分操作の排他区間を長時間保持しない。
既存jobのbase、開始時刻、deadline、失敗回数は変更しない。

受付前に `git fetch origin main` で公開済みcommitを取得する。remote mainを
確認できない場合やcommitがローカルにない場合は、受付票を部分保存せずエラーにする。
status/recoverはこのremote照合を追加せず、保存済み状態の確認・再開に使える。
受付票とjob状態は従来どおりcontrol branchへ保存し、記事PRへ混ぜない。

## Notion同期の待機を置き換えない

`.github/workflows/sync-notion.yml` のconcurrencyに `queue: max` を指定する。
これにより既定の「待機1件を後続runで置換」ではなく、最大100件が待機できる。
実行中runのキャンセルは引き続き無効。100件を超える追加runはキャンセルされ得るため、
3,000語の一斉マージをしてよいという意味ではない。同期結果を見ながら順番に統合する。

GitHubの待機開始順とpush順が必ず一致するとは限らない。同じ記事の連続改訂では、
先行する同期の完了を確認してから後続版を公開する。失敗・上限キャンセル時は既存の
workflow_dispatchでentryを指定し、対象語の最新本文の同期だけを再実行する。
記事のworkflow completed、PRマージ、Notion同期の完了は別々に確認する。

公式仕様（2026-09-08確認）:
https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs

`tests/test_batch_published_base.py` はlocal bare remoteとstarter fixtureを用いた
6つの工程境界テスト。既存の全回帰テストと合わせてCIで実行する。
実LLMの複数語生成速度やNotionへの実同期を計測したテストではない。
