# プロジェクト改善知識

このディレクトリは、個々の英単語の記事内容ではなく、単語作成を繰り返す過程で得た**見出し語をまたいで再利用できる品質・効率・信頼性上の知見**を管理する。

日々の感想、単語固有の修正内容、未整理のメモを保存する場所ではない。通常の作業事実は `logs/`、記事内容の監査は `audits/` に置く。

## 登録条件

新しいrecordは、次をすべて満たす場合だけ作成する。

1. 複数の実行で再発したか、1回でもデータ破損、誤った合格、重大な手戻りなど高影響だった。
2. 特定の見出し語を別の語へ置き換えても成立する。
3. 問題の観測だけでなく、次回の具体的な行動規則に変換できる。
4. 効果を再発件数、手戻り、変更量、所要時間などで確認できる。
5. 既存recordと同じ規則ではない。
6. `2026-08-27` 以降に作るrecordは `escaped_defect_ids` で `audits/escaped_defects.json` の実在IDを1件以上参照する。

条件を満たさない気づきはrecordにしない。「新しい知見なし」という記録も作らない。

## 状態

- `candidate`: 汎用性はあるが、適用方法または検証方法をまだ確定していない。
- `trial`: 次回以降の限定された実行で適用し、効果を測定している。
- `active`: 所定の実行数で効果を確認し、恒久的な仕様・スクリプト・CI・調整役規則へ反映済み。
- `retired`: 効果がなかった、前提が変わった、または別の仕組みに置き換えられた。

`candidate`は次回の強制規則にしない。`trial`と、調整役が直接適用すべき`active`だけが `ACTIVE.md` に出る。

## 内容品質と運用知識の境界

内容品質の知見を `ACTIVE.md` だけに書いて、隠れた第二仕様にしてはならない。記事の生成・通常チェック・最終審査へ恒久適用する品質規則は、対応する `prompts/` の正本とテストへ反映し、その参照をrecordの `enforcement.refs` に残す。

`ACTIVE.md` は元の作業を統括する調整役だけが読む。文脈非継承のコールドレビュー担当と最終盲検担当には渡さない。

## 実行ごとの使い方

作業開始時:

```bash
python scripts/process_improvement.py summary
python scripts/process_improvement.py validate
```

調整役は `ACTIVE.md` の試行中・有効規則を、既存の標準フローを壊さない範囲で適用する。

作業終了前:

1. 今回、避けられた手戻り、再発した失敗、データ破損、不要な大規模変更、機械化できる反復作業があったかを確認する。
2. 登録条件を満たさなければ何も追加しない。
3. 満たす場合だけ `records/PI-NNNN.json` を追加するか、既存recordへ新しい根拠・検証結果を追加する。
4. `trial`の評価期間を満たしたら、結果に基づき`active`または`retired`へ変更する。効果未確認のまま`active`にしない。
5. `python scripts/process_improvement.py render` と `validate` を実行する。

## 肥大化防止

- 1 recordは16 KiB以下、根拠は最大10件とする。長い原出力を複製せず、PR、ログ、監査ファイルなどの参照と短い観測事実だけを残す。
- `ACTIVE.md`へ表示する規則は最大20件・12 KiBとする。
- 機械的に強制できる規則は、確認後に仕様、スクリプト、テスト、CIへ移し、`ACTIVE.md`で重複説明しない。
- 同じ問題の発生例は新しいrecordにせず、既存recordのevidenceと検証結果へ集約する。

JSONの正確な必須項目と状態制約は `scripts/process_improvement.py` を正本とする。

## 10語ごとのROI退役審査

初期windowは10語とし、`process_improvement/retirement_state.json` にactiveな運用規則とchecker passの審査位置を保存する。完了した `workflow_cost_v1` runが10語分増えるごとに次を実行する。

```bash
python scripts/process_improvement.py retirement-review
```

スクリプトは各unitについて、検出欠陥数、instruction+input bytes、所要秒、欠陥/KiB、欠陥/秒を同じ10語windowから集計する。検出欠陥が0件なら `retired`、1件以上なら `active` を維持する。運用規則の退役は対応するPI recordへ反映する。checker passが退役した場合は、担当taxonomyを別のactive passへ再割当するまでregistry検証と次runを停止し、検査観点を黙って消さない。

window未満では状態を変えない。費用だけ、件数だけ、または主観的な有用感で状態を変更せず、workflow runの実測値を使う。
