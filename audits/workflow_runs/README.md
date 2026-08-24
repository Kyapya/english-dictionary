# Entry workflow runs

このディレクトリは、記事本文やcontent auditが存在する前から、単語作業の開始・実行budget・durable checkpointを記録する。

## 開始順序

外部資料の検索、本文の語義判断、サブエージェント起動より先に、専用branchを作り、次を実行する。

```bash
python scripts/entry_workflow_guard.py start \
  --headword eliminate \
  --entry entries/e/eliminate.md \
  --branch add/eliminate-v5 \
  --base-sha "$BASE_SHA"
```

表示されたrun JSONを最初のcommitへ含め、branchをpushする。push後、そのcommitがrun JSONを実際に含むremote branch headであることを確認する。

```bash
python scripts/entry_workflow_guard.py confirm-remote \
  audits/workflow_runs/eliminate/<run-id>.json \
  --commit-sha "$CHECKPOINT_SHA"
git add audits/workflow_runs/eliminate/<run-id>.json
git commit -m "Confirm eliminate remote workflow checkpoint"
git push
```

`confirm-remote`が終了コード0になる前に調査を始めてはならない。これにより、その後に実行が停止しても、見出し語、branch、base SHA、開始時刻、budgetをGitHub上で確認できる。

## 実行budget

通常はstandardを使う。

| profile | 全体時間 | draft保存 | 検索query | 候補page | heartbeat間隔 |
|---|---:|---:|---:|---:|---:|
| standard | 60分 | 20分 | 12 | 18 | 10分 |
| extended | 90分 | 30分 | 18 | 26 | 10分 |

extendedは多義性や専門領域の広さについて具体的理由を記録した場合だけ使用する。個別上限を引き上げない。

検索queryと候補pageは、採用した資料だけでなく、確認を試みる件数を実行前に記録する。

```bash
python scripts/entry_workflow_guard.py record-research \
  audits/workflow_runs/eliminate/<run-id>.json \
  --queries 2 \
  --candidate-pages 4
```

外部調査の各batchの前後と、作業中少なくとも10分ごとにheartbeatを実行する。

```bash
python scripts/entry_workflow_guard.py heartbeat \
  audits/workflow_runs/eliminate/<run-id>.json
```

終了コード2は正常な安全停止である。run JSON、存在するdraft、未解決事項をcommit・pushし、同じ依頼内で探索や新cycleを続けない。

## checkpoint

次の順序を飛ばさず、各checkpoint後にrun JSONと成果物をcommit・pushする。

1. `draft_saved`
2. `source_inventory_complete`
3. `normal_review_complete`
4. `cold_review_complete`
5. `blind_seal_complete`
6. `final_review_complete`
7. `completed`

```bash
python scripts/entry_workflow_guard.py checkpoint \
  audits/workflow_runs/eliminate/<run-id>.json \
  --stage draft_saved \
  --notes "best-effort v5 draft persisted"
```

draftはstandardで開始20分以内に `status: draft`、`checked: false` として保存する。完成監査前のdraftをPRへ出したり、checked扱いにしたりしない。

## 検証

変更されたentryには、同じPRで変更された `status: completed` のworkflow runが必要である。CIは次を実行する。

```bash
python scripts/entry_workflow_guard.py validate-changed \
  --base "$BASE_SHA" \
  --head "$HEAD_SHA" \
  --merge-ready
```

`in_progress` と `budget_exhausted` は作業を失わないための正常なbranch状態だが、merge可能状態ではない。
