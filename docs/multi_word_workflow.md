# 複数語・1語共通の依頼入口

`start_words.py` は受付・単語別割当を追加する。本文仕様、7 checker、cold review、
final blind、裁定、budget、公開条件は変更しない。`start_word.py` / `run_word.py`
は引き続き1語の実行本体であり、旧CLIもそのまま使える。

## ユーザーが送るもの

`alpha` の1語でも、`alpha, beta, gamma` や改行した単語一覧でも受け付ける。
短いフレーズは1項目として扱う。空白だけで複数語とフレーズを機械判定しない。
一覧にない語を追加せず、明示的な修整依頼は既存の局所修整ルートへ送る。

## 担当LLMの操作

単語一覧をユーザーにCLIへ書き直させる必要はない。担当LLMが下記を実行する。

```sh
# まず受付だけ保存する。1語でも同じ。
python scripts/start_words.py alpha beta "take off" --enqueue-only
# テキストは1行1項目（カンマ・読点も可）、JSONは文字列の配列。
python scripts/start_words.py --words-file words.txt --enqueue-only

# 空き枠だけを準備する。独立した語担当を2つ使える環境の例。
python scripts/start_words.py --dispatch --max-active 2
python scripts/start_words.py --status

# 先行語の作成中にも受付できる。
python scripts/start_words.py gamma delta --enqueue-only
python scripts/start_words.py --dispatch

# 設定済み枠は省略時に継承する。明示的な変更のみ許可。
python scripts/start_words.py --set-max-active 1
```

`python scripts/start_words.py alpha beta` は受付と割当準備をまとめて行う便利な入口。
ただし中断に備える通常のWork運用では、まず `--enqueue-only` の受付ファイルを
control branchへcommitし、既存のGitHub接続経路で保存してからdispatchする。
rootには実際のcontrol checkoutを使い、main上で無関係な変更をまとめてcommitしない。
`queue/words.csv` は記事statusの台帳なので、受付キューの代用として書き換えない。

1. 1リポジトリにつき一つの **control checkout** を使う。`queue/batches/` は受付票、
   `queue/jobs/` は見出し語slug単位の状態。両方をcontrol branchへ保存する。
   入力全体を検証し、同一slugの重複依頼は既存jobへ集約する。
2. 利用可能な独立した **語担当** の数を確認し `--dispatch --max-active N` を使う。
   最初の既定は2。枠が確認できなければ1を使う。受付済みの待機語にはrunもdeadlineも
   作られず、割当された語だけで従来の60/90分budgetが開始する。開始後のdeadline、
   失敗回数、研究budgetは変更・一時停止しない。
3. 出力の `workspace` / `assignment_path` ごとに別の語担当を起動する。
   初期化のclone/fetchは短い直列処理であり、LLM並列実行の証拠とは呼ばない。
   語担当はその作業場所のAGENTS.mdと `run_word.py --resume ...` のnext_stageに従う。
   一語を終えてから次を担当へ渡すのではなく、空き枠分を先に渡す。
4. 語担当は原稿・レビュー・checkpointを自分のworkspaceへ保存する。他語の本文や
   監査履歴を同じ生成contextへ混ぜない。レビューは生成者とは独立したcontextで行う。
   語ごとのGitHub保存は従来の `publish_checkpoint.js` を **各workspaceをrootとして**
   実行する。既知の無認証git pushは試さない。
5. control側は `--status` / `--dispatch` を再度呼び、completedやbudget_exhaustedを
   読み取って空き枠を次へ渡す。語担当の停止は他語の受付・処理を停止する理由にしない。
   activeのまま応答がない担当を勝手に二重起動しない。
6. 各語の完了は既存の機械検証・レビュー・PR経路で確認する。PRと共通台帳の統合は
   control担当が順番に行い、最新mainとの競合時には検証せずに上書きしない。
   queueのcompletedは **workflow manifestのcompletedを観測した状態** であって、
   PRマージ済み・Notion同期済みの意味ではない。公開結果は別途確認する。

`queue/jobs` のstatusは `queued / preparing / active / blocked / completed`。
記事のstatusや `checked` をこのキューから設定してはならない。
出力は全件の件数と最大100件の詳細に制限する。3,000語の受付内容は受付票に残し、
全記事をcontrol担当の会話へ読み込まない。

## 分離と同時実行の範囲

語ごとに独立したローカルclone・index・branch・Git設定を作る。Gitオブジェクトは
`clone --shared` でcontrol checkoutと共有するため、作業中にcontrolのオブジェクトを
削除・pruneしない。workerは `.git` 管理領域の `dictionary-batches/workers/` 配下にあり、
controlの通常のgit addには混入しない。成果物は語ごとのremote branchへ必ず保存する。

SQLiteの短い排他区間で受付と割当を制御する。複数の受付/dispatchプロセスが
同じcontrol checkoutで重なっても、同じjobを二重に割り当てない。
clone/fetch/本文作成中にはこのロックを保持しないので、追加受付を妨げない。

**別マシン・別cloneを独立したcontrolとして同時に起動する分散queueは今回の対象外。**
GitHub上の同一語の未完了run検査は従来どおり残すが、それを分散ロックだとは扱わない。
別のWork実行へ引き継ぐ場合は既存のcontrol状態とremote checkpointを確認し、
その語の既存担当が停止したことを確認してから同じrunを引き継ぐ。

`max-active` は **進行中の語数** であり、全LLM呼出し数の上限ではない。
各語の7 checker/coldの実行枠は従来どおり。ホストの全体利用枠に収まるように語数を
選ぶ。子担当を作れない環境では一括受付＋逐次処理とし、並列処理済みと報告しない。
このスクリプト単体がChatGPTの会話・LLM・常駐サービスを自動起動するわけではない。

## 中断・重複・復旧

```sh
python scripts/start_words.py --recover alpha
```

同じworkspaceに存在する一意のrunへ再接続し、割当票を再生成する。deadline・開始時刻・
失敗回数は変更しない。budget_exhaustedはblockedのままで、dispatchは新runを作らない。
初期化中の停止もqueuedへ自動で戻さない。runがない/複数ある/branchが違う場合は
fail closedで止め、`.git/.../<job_id>.start.log` とremote状態を確認する。

従来の `start_word.py` が `resume_required` を返した語は、その既存runとbranchを
`existing_runs` に表示してblockedにする。既存担当が動いている可能性があるため、
バッチが勝手に所有権を奪ってresumeしない。他の語はそのまま進める。
新しい環境でworkspaceが存在しない場合も新runを作り直さず、保存済みbranchとrunを
既存の再開手順で取得する。未公開のローカル成果物を復元できたと偽らない。

同じ語の再依頼は完了後も既存jobを返す。新しい改訂・全面再作成が明示された場合は、
履歴を削除せず従来の局所修整/再作成ルートを使う。重複入力で自動全面改稿しない。

## 検証

`python -m unittest discover -s tests -p 'test_start_words.py' -v`

単一語、複数語、既存run、途中の追加、同時受付/割当、個別失敗、作業場所とGit設定の
分離、途中再開、予算不変、入力検証、3,000語受付と出力量を検査する。
テスト用starterは工程境界のfixtureであり、本物のLLMレビューの実行証拠ではない。
通常CIでは既存の全回帰テストも併せて実行する。
