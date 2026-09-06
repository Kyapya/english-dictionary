# Process improvement v2

このディレクトリは、英単語解説の作成・修正・復旧で実際に確認された事象から、別の見出し語にも使える品質・効率・信頼性上の行動を育てる。記事仕様を上書きする第二仕様ではない。

## 正本と世代

- `epoch.json`: 現在の `knowledge_epoch` と一度だけの旧知識リセット記録。
- `records/PI2-*.json`: 1知見1ファイルの現行版。構造化JSONが正本。
- `history/`: 意味を改訂した旧版。過去snapshot・観測との対応を保持する。
- `observations/`: 配信・行動・再発・非再発・負担・結果不明等のimmutableな事実。
- `receipts/`: 同じ事象の再取込を防ぐ冪等receipt。
- `index.json`: recordsから生成する小型索引。
- `ACTIVE.md`: 互換用の派生一覧。通常の生成入力には使わない。

新世代 `pi2-2026-09-06` は知見0件で出荷する。旧 `PI-0001`〜`PI-0004`、`process-refactor-v1`、旧 `ACTIVE.md`、旧 `retirement_state.json` の本文・評価・退役状態は移行しない。履歴は移行前コミット `7cca3bc28b43d7e81940dadf84cb67e0ac8e3a80` で参照し、現行ツリーへバックアップを複製しない。過去run内の旧IDは過去の事実として読み取るが、新台帳の入力・集計対象にしない。

リセットは `migrate-v2` だけが行う。同じepochへの再実行はno-opで、新知見を消さない。通常起動、CI、resumeは移行処理を呼ばない。

## 登録対象

初稿、調査、通常check、cold review、final blind、裁定、局所修整、再試行、入力不整合、保存失敗、復旧、妥当と確認されたユーザー指摘から、次を具体的に説明できるものだけを扱う。

1. 観測した問題。
2. 固定参照または内容hashで特定できる根拠。
3. 他の見出し語でも成立する理由。
4. 適用条件で実行する具体的行動。
5. 除外条件と不確実性。

再発回数、高重大度、`escaped_defect_ids` は候補登録の必須条件ではない。1回目でも根拠と汎用性があれば候補にできる。escaped defectは実在根拠がある場合だけ任意で参照する。

単語固有の正解、作業日記、既存仕様の転載、行動が不明な標語、根拠のない一般化、既存知見の重複は登録しない。「知見なし」はrecordではなくrunのPI処理状態で表す。原因が未確定なら断定せず、`problem.uncertainties` に残す。

## 状態と責任

- `candidate`: 実観測はあるが、一般化・対策・仕様整合性のどれかが未確定。入力へ渡さない。
- `active`: 根拠、条件、除外条件、現行仕様との整合性を既存調整役が確認済み。効果実証済みという意味ではない。
- `integrated`: 正式仕様・コード・テストに統合済み。PI入力へ重複配信しない。
- `retired`: 誤り、悪影響、重複、前提消失等を根拠に停止。理由と根拠を残す。

採用・改訂・統合・退役の意味判断は既存調整役が行う。未裁定checker findingやユーザーの疑問を、そのまま確定事実や `active` にしない。文字列一致は重複候補の検出に使えるが、意味が同じという最終判断にはしない。

配信回数、欠陥0件、未使用期間だけで状態を自動変更しない。旧 `retirement-review` は終了し、実行しても知見・checkerを変更しない。checkerの構成・taxonomy・独立性はchecker側の正本で維持する。

## 通常runへの接続

`scripts/run_word.py` が新規run作成時にgenerator用snapshotを作る。pre/post blind resolutionへ進む際は、生成後に確認された `entry_features` でcoordinator用snapshotを機械的に再選択する。未知の必須タグは一致とみなさない。PI選択のための英語分析LLMは追加しない。

通常入力へ渡せるのは、同じepoch、`active`、仕様依存が現在も一致し、recipient・phase・既知特徴が合う知見だけである。初期上限は8件・8 KiB。保守的に複数の短い行動を渡しつつ、記事仕様を圧迫しない値として設定した。priority降順、ID、版で決定的に選び、知見を途中切断しない。未選択知見は削除しない。

snapshotはID・版・recipient・phase・条件・行動・除外条件、実入力hash、実bytes、機械処理時間を固定する。根拠本文は含めない。snapshot作成と実際のstage完了時の配信観測は別に記録する。配信だけで行動・効果ありにしない。

通常checker、cold review、final blindへPI snapshot、過去finding、元の失敗例、期待結論を渡さない。PI読込・選択失敗時は、既存品質guardを維持して明示的な「PIなし」snapshotへ退避し、成功扱いにはしない。旧 `ACTIVE.md` やcacheへ戻らない。

## 収集、完了、失敗、resume

生成担当と既存調整役は `prompts/process_improvement_learning_delta_v2.md` に従い、既存stage出力へ `learning_delta` を含める。追加LLM呼び出しは行わない。`items: []` は確認済み・該当なし、項目欠落は整理未了である。

`complete-stage` は保存済み出力を同じ冪等取込へ渡し、run manifestへ次を記録する。

- `processed`: 新規・改訂・観測を保存済み。
- `no_applicable`: 確認したが知見なし。
- `pending`: 判断または整理が未了。
- `save_error`: 不正入力、競合、保存失敗等。成功として隠さない。

review失敗・budget到達は、保存できた事実だけをrunの `pending_events` に残す。そこで新しいLLM呼び出しを強制しない。resumeは保存済みのpending出力を再取込し、同一event receiptなら件数を増やさない。改修前に始まったrunにはresume時点のepochを付け、resume後に新しく保存された事象だけを対象にする。古い出力の読み直しだけで新知見を作らない。

局所修整は既存の局所reviewだけを使い、次で同じ取込へ接続する。PIのために通常生成や全体reviewへ戻らない。

```bash
python scripts/targeted_correction.py record \
  --entry entries/x/example.md --base <sha> \
  --request <request> --reviewer <reviewer> \
  --learning-delta <review-output.json>
```

## 版、依存、観測

意味のある改訂はversionを増やし、直前版を `history/` に保存する。観測は必ずIDと実際に渡されたversionへ結び、旧版の結果を新版へ混ぜない。

`validation.specification_context` は依存するファイルまたはMarkdown sectionとhashを持つ。依存範囲が変わるか参照不能なら `needs_recheck` として入力から外す。無関係の記事追加で失効しない。再確認は根拠参照と理由を必須とし、hashだけの更新を拒否する。

観測は次を区別する: `delivered`、`action_confirmed`、`no_opportunity`、`recurred`、`no_recurrence_observed`、`burden`、`unknown`、`supporting_evidence`。所要時間・bytes・修正回数は実測がある場合だけ数値を入れ、未計測は `null` とする。集計は知見本体の手入力counterではなく、immutable observationから版別に生成する。相関する観測を因果効果と断定しない。

## CLI

```bash
# 台帳、参照、派生index、観測の検証
python scripts/process_improvement.py validate

# 状態、整理結果、要再確認、版別観測の要約
python scripts/process_improvement.py summary --json

# 対象run用の実入力snapshot
python scripts/process_improvement.py select \
  --recipient generator --phase generation --run-id <run-id> \
  --feature <confirmed-feature> --output <snapshot.md>

# 根拠付きdeltaの冪等取込
python scripts/process_improvement.py ingest \
  --source <event-or-stage-output.json> --delta <delta.json>

# 仕様変更後の根拠付き再確認（新版を作る）
python scripts/process_improvement.py reconfirm \
  --record-id <PI2-ID> --expected-version <N> \
  --evidence-ref <fixed-reference> --rationale <reviewed-reason>

# 一度だけの移行。通常run/CI/resumeは呼ばない
python scripts/process_improvement.py migrate-v2 \
  --knowledge-epoch <epoch> --pre-migration-sha <full-sha>
```

recordや観測の更新は同一repository内のfile lock、同一directoryのatomic replace、expected version、event receiptで保護する。異なるpayloadのID衝突、同じrecordの同時改訂、履歴衝突は黙って後勝ちにせず拒否する。複数branchの意味的重複はCIの候補検出後、調整役が統合判断する。
