# 1語・複数語の共通受付と独立実行

## 適用範囲

新規作成依頼は、1語でも複数語でも `scripts/run_words.py` で受け付ける。
本文・source-first・7 checker・cold review・final blind・最終レビュー・guardは変更しない。
`start_word.py` / `run_word.py` は各単語の内部実行と既存runの再開に引き続き使う。
`checked` 済みの語は受付結果を `existing` とし、黙って全面再生成しない。
具体的な修整は既存のtargeted correction、明示的な全面再作成は従来の単語別経路を使う。

これは常駐LLMサービスではない。受付・予約・状態保存はスクリプトが行い、本文作成と
独立レビューはWorkの実際の担当に渡す。requestファイル作成を「生成を並列実行した」
と報告しない。利用できる独立担当がなければ未開始語はキューに残し、開始済みの1語を
先に進める。利用者に複数語を再送させない。

## 受付

```bash
# 単語1語でも同じ入口
python scripts/run_words.py enqueue apple --batch-id request-one

# 複数語（CLIの引数、カンマ、改行、読点で区切れる）
python scripts/run_words.py enqueue apple banana cherry --batch-id request-many
python scripts/run_words.py enqueue 'apple, banana, cherry'

# ファイルは1行1語のUTF-8テキスト、又はJSON文字列配列
python scripts/run_words.py enqueue --file words.txt

# 短いフレーズは1引数として保持する
python scripts/run_words.py enqueue 'in spite of'
```

対話で改行・カンマ区切りの複数語を渡された場合は、全件を1回の受付に渡す。
フレーズと単語リストを勝手に相互変換しない。日本語の依頼文・改修指示そのものを
単語リストとして登録しない。大文字小文字と空白を正規化し、同じ語は重複排除する。
異なる見出し語が同じslugになる場合は、黙って併合せず受付全体を拒否する。

受付は `queue/batches/<batch-id>.json` に保存する。この時点ではworkflow run、
開始時刻、deadline、reviewを作らない。3,000語を登録しても、待機する2,999語に
生成予算を開始しない。同じbatch ID・同じ内容の再投入は同じ受付を返し、内容が
違うID再利用は拒否する。既存受付に同じ語があれば元のjobを参照し、二重開始しない。

受付前に `origin/main` を更新する。各受付の内容仕様baseはそのcommitに固定し、
調整branchだけにある未統合の台帳変更を単語branchへ持ち込まない。
受付台帳を管理するcheckout/branchは一つの調整役に集約する。新しい会話で受付を
追加するときは、その台帳の最新branchを確認し、既存ファイルを上書きしない。
受付・配分・状態更新後は台帳だけをそのbranchにcommitし、既存のGitHub接続による
publish処理で保存する。別cloneで別々の台帳を作る運用は、全体の実行枠を共有しない。
並列実行枠は同じ調整用checkoutの全受付を合算して管理する。別cloneから同じ語を
開始しようとした場合にも、後述のremote予約で二重開始を拒否する。

## 配分、予約の保存、開始

```bash
python scripts/run_words.py prepare request-many
python scripts/run_words.py status request-many
```

`queue/batch_config.json` の `max_active_words`（初期値2）まで、各語を別branch
`batch-word/<slug>` と別Git worktreeへ割り当てる。絶対workdirと次の操作をJSONで返す。
1にすると単語間を逐次実行できる。これは「同時に担当する単語数」であり、LLM呼出し
総数の上限ではない。各語の既存checkerは最大7担当を使うため、実際のWork/API枠を
確認してから単語の開始数を決める。既に始めた語を待機させてdeadlineを消費させない。

準備段階では `queue/word_claims/<slug>.json` の小さな予約だけをcommitする。
この予約にはjob IDと元の受付・調整branchが入り、記事や監査判定は入れない。
生成の開始前に、返された**単語側workdir**で既存の `scripts/publish_checkpoint.js`
をGitHub接続経由で実行し、予約branchを保存する（READMEのconnector手順）。
認証済みGit環境で明示的に `--publish-mode git` を選んだ場合だけ通常pushを使える。
同じ調整用checkout配下では保存モードを混在させない。Git configはworktree間で共有される。

同じslugのremote branch作成はGitHub側で競合する。一方の予約が既に存在すれば、
もう一方は `external` として元の受付を案内し、上書き・force push・別名での再予約はしない。
予約branchを削除してguardを迂回しない。予約を作っただけでは生成開始にならない。

実際に担当できる語だけ、**調整側checkout**で開始する。

```bash
python scripts/run_words.py start request-many apple
python scripts/run_words.py start request-many banana
```

remoteの予約が同じjob IDであることを確認してから、各worktreeの
`start_word.py <headword> --publish-mode connector --reviewer-mode handoff` を呼ぶ。
予約未保存は `prepared` のままで、runを開始しない。以降は単語ごとに既存の
publication checkpoint・生成・独立レビュー・修正・完了を実行する。
同じ語への二度目のstartは新runを作らず、実在するrunの再開先を返す。

担当には自分の語のworkdir・headword・runだけを渡し、他の語の本文やfindingを
連結しない。単語担当が調整側の台帳や他語のworktreeを書き換えてはいけない。
単語側checkoutから新たな配分を行う操作はスクリプトでも拒否する。

## 進捗、追加受付、再開

```bash
# 先行語が動いていても、新たな依頼を保存できる
python scripts/run_words.py enqueue date elderberry --batch-id later-request

# statusは読取りのみ。refreshもheartbeatや失敗回数を変更しない
python scripts/run_words.py status request-many
python scripts/run_words.py refresh request-many

# 完成後、空いた枠へ次の語を準備する（自動LLM起動ではない）
python scripts/run_words.py prepare request-many
python scripts/run_words.py prepare later-request
```

`queued` は未割当、`prepared` は予約済み・未開始、`in_progress` は単語別runが存在する状態。
`review_complete` は既存workflowの完了を観測した状態であり、GitHubマージやNotion同期の
完了ではない。レビューを省略したり `checked: true` を直接付けたりする経路はない。

`blocked` の1語は他語の配分を止めない。`guard_report` がある場合は同一runの
再開・明示的な再実行承認に関する既存guardの指示を使う。失敗回数・deadlineの
リセット、batch IDを変えての新run作成、自動無限再試行は禁止。

`inspection_required` は開始操作の成否等が不明な状態。安全のため枠を保持する。
実際のmanifestを確認し、見つかれば同じrunを再開する。見つからないだけで
「未開始だった」と扱わない。ほかの語を動かすためにこの状態を削除しない。

中断後は保存済み台帳を読み、同じword branchとrunを復元する。

```bash
python scripts/run_words.py recover request-many apple
python scripts/run_words.py refresh request-many
```

`recover` は開始前の予約準備失敗、又は失われたworktreeの復元だけに使う。
開始を試みたのにmanifestが回収できない場合は、再開始せず停止する。
`remote_run_scan_failed` はrun作成より前の失敗なので、明示的recover後に改めて
remote確認できるが、予算超過・未完了runのブロックには使えない。
connector receiptが失われた場合は、既存READMEの `publish_checkpoint.py accept`
で実在checkpointを照合し、内容を無確認で再送しない。

## 統合と公開

合格した単語のbranchだけを、既存CIと承認条件に従って順番に統合する。
未完了語を同じPRに混ぜない。`merged` を確認した完了語のbranchは通常の
GitHub branch削除で整理してよい。未完了・予算超過の予約を削除して再開始しない。単語別の監査commitの履歴を保持し、seal時系列を壊す
cherry-pick/squashやhashの付替えで競合を解消しない。
`queue/words.csv`、共通export、PI共通知見に競合が出た場合は調整役が最新mainを取り込み、
双方の単語と知見を保持して既存のqueue/export/PI検証を再実行する。ファイル全体を
片側で上書きしない。解消できなければ該当語の統合だけを保留する。

```bash
# 実在するcompleted runがorigin/mainにあることを確認してmergedへ更新
python scripts/run_words.py refresh request-many --fetch
python scripts/run_words.py validate
```

Notion同期は別の完了条件として実行結果を確認する。同期workflowは `queue: max`
により連続マージ時の待機置換を避けるが、GitHub側の待機上限は100であり、無制限の
公開キューではない。生成済み3,000語を一斉マージしない。同期失敗・キュー上限による
キャンセル時は既存workflow_dispatchのentry指定で同期だけを再実行する。

公式仕様: https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs

## 検証範囲

`tests/test_run_words.py` はlocal bare remoteと小さなstarter代替で、受付、3,000語、
worktree分離、予約競合、枠、失敗隔離、再開、完了とマージの区別を検証する。
実際の記事の品質・review guardは既存テスト群とCIで検証する。
LLMによる複数語の実生成速度やWorkの同時実行数を、このテストの結果から推定しない。
