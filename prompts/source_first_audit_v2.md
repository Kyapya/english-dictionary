# source_first_audit_v2

この仕様は、PR #90の目的である「本文と複数レビューが同じ誤った候補集合を共有しても、外部資料との直接比較で検出できること」を維持しつつ、source-first監査を有限かつ再現可能に実行するための現行仕様である。

## 維持する品質保証

1. 通常チェックは本文の分類を見る前に、外部資料から語義・品詞・主要制約を抽出する。
2. 派生形は表層形ごとの原子的factとして扱う。
3. 外部factからsource union、claim unit、本文targetへの対応を残す。
4. 最終審査は盲検棚卸しをsealした後、通常候補との一致だけでなくsource unionを直接確認する。
5. コールドレビューへsource-first資料、監査、既知の問題を渡さない。最終盲検段階にも渡さない。

## 有限化の原則

source-firstは「ウェブ上の情報を見つからなくなるまで探す」工程ではない。選定した資料集合で次の6軸を閉じる有限監査である。

- `lexical_senses`
- `part_of_speech_and_frames`
- `derived_and_related_forms`
- `specialist_and_legal_uses`
- `register_region_and_frequency`
- `pronunciation_and_etymology`

各軸は `covered` または理由付き `not_applicable` にする。資料追加は未解決のcoverage軸を閉じる場合だけ行い、既に閉じた軸のために同種資料を増やさない。

## 実行profile

通常は `standard` を使う。

| profile | sources | atomic facts | research rounds | post-cold rechecks | final attempts |
|---|---:|---:|---:|---:|---:|
| standard | 6 | 48 | 2 | 1 | 2 |
| extended | 8 | 80 | 3 | 2 | 2 |

`extended` は、多義性または専門領域の広さからstandardでは6軸を閉じられない具体的理由を `profile_reason` に記録した場合だけ使う。profileの上限値を個別に引き上げてはならない。

1 research roundは、未解決coverage軸を明示してから行う一まとまりの資料確認を指す。資料を1件開くたびにroundを増やす意味ではない。

research roundの内部も無制限ではない。`scripts/entry_workflow_guard.py` の全体時間、検索query、候補pageの各上限を常に優先し、採用しなかった検索・候補資料もattempt budgetへ数える。round開始前に予定query数・候補page数を `record-research` へ記録し、終了後にheartbeatで進捗時刻を記録できる（heartbeat間隔に上限はない）。終了コード2ではsource-first側も `stop` し、存在するdraftと未解決coverage軸をcommit・pushして安全停止する。

## 資料選定と閉包条件

- `complete` には、異なる `independence_group` を持つ `general_lexicon` 資料が2件以上必要である。
- 専門・法律用法を `covered` とする場合は、その領域へ直接適用できる専門資料または一次資料を優先する。
- 同じ出版社・データ供給元を別URLで開いても独立資料として数えない。
- coverage軸がすべて閉じ、未解決の重要疑問がなく、上限内ならinventoryを `complete` とする。
- 上限へ達しても重要疑問が残る場合は探索を続けず `budget_exhausted` とし、`stop_reason` と `open_questions` を保存する。記事は `needs_review`、checked falseのまま停止する。これは正常な安全停止であり、PASSへ進めない。

## v2の正本構造

`source_first_audit` は次を持つ。

- `version: source_first_audit_v2`
- `profile` / `profile_reason`
- `limits` / `usage`
- `research_status`
- `stop_reason` / `open_questions`
- `inventory_completed_before_article_comparison`
- `inventory_completed_at` / `article_comparison_started_at`
- `coverage_axes`
- `sources`
- `source_union`
- `claim_units`

各sourceは `id`、`locator`、`source_type`、`source_role`、`independence_group`、`facts` を持つ。factは `id`、`form`、`kind`、`statement`、`source_detail` を持つ。`derived_form` のfactは一つの具体的表層形だけを扱う。

同一または十分近いfactだけを一つのsource unionへまとめる。各unionは `id`、`source_fact_ids`、`canonical_statement`、`disposition`、`rationale` を持つ。v1のようにunionへ大量の `article_target_ids` を複製しない。

本文へ `included` または `integrated` したunionだけ、原子的なclaim unitを作る。各claimは `id`、`union_ids`、`subject_form`、`claim_type`、`statement`、直接対応する `article_target_ids`、`source_supports` を持つ。除外factを形式的な本文claimへ複製しない。

最終審査はblind seal後に全unionを直接確認する。`final_review.source_inventory_results` はunionごとに `union_id`、`status`、`notes` だけを記録する。fact IDとtarget IDはunionとclaimから導出できるため、v1のように最終結果へ再複製しない。

## 機械支援コマンド

監査構造を手作業で組み立てない。

```bash
python scripts/entry_workflow_guard.py record-research \
  audits/workflow_runs/apple/<run-id>.json \
  --queries 2 \
  --candidate-pages 4
python scripts/source_first_audit_gate.py init entries/a/apple.md
python scripts/source_first_audit_gate.py close-inventory entries/a/apple.md --research-rounds 1
python scripts/source_first_audit_gate.py start-comparison entries/a/apple.md
python scripts/entry_workflow_guard.py checkpoint \
  audits/workflow_runs/apple/<run-id>.json \
  --stage source_inventory_complete
python scripts/source_first_audit_gate.py prepare-final entries/a/apple.md
python scripts/source_first_audit_gate.py record-attempt entries/a/apple.md --stage final
python scripts/source_first_audit_gate.py summary entries/a/apple.md
```

extended profileは理由を明示する。

```bash
python scripts/source_first_audit_gate.py init entries/c/cast.md \
  --profile extended \
  --reason "主要品詞と専門領域が多くstandardの48 factsでは6軸を閉じられない"
```

budgetを使い切った場合は、未解決事項を失わず停止する。

```bash
python scripts/source_first_audit_gate.py stop entries/a/apple.md \
  --reason "standard fact budget reached" \
  --open-question "法律用法の地域境界が未確定"
```

## 再審査上限

- コールドレビューは固定draftに対して1回だけ行い、採用修正後に同じ目的で全面再実行しない。
- 採用修正後は `scripts/workflow_revision.py` が意味上の影響範囲checkerだけを失効させる。分類不能、複数section、語義統合・分割、品詞追加削除は全checkerへ倒す。
- `post_cold_rechecks_used` は影響範囲checkerの再検査roundを数え、未変更passの有効な結果再利用を再実行として数えない。
- 再検査のためにsource、fact、research roundを自動追加しない。根拠対象claimを変更した場合は、同じ既存資料に基づくclaim/source support対応と本文hashを更新して検証する。
- 最終審査は初回とREJECT後の再審査を合わせて最大2回とする。
- 上限で問題が残る場合、同じ依頼内で新cycleを自動開始しない。`needs_review`、checked false、blocker付きで停止する。
- 次の明示的なユーザー依頼で新cycleを開始できる。停止を避けるために合否基準を緩めてはならない。
- source-firstの資料・fact・round数が上限内でも、entry workflowの時間・query・候補page budgetに達した場合は停止する。選定済み件数が少ないことを、追加探索を無制限に続ける理由にしない。

## 移行と合否

未変更の `source_first_audit_v1` は履歴互換として検証できる。新規または変更されたentry/canonical auditは `source_first_audit_v2` を必須とする。一括変換せず、次に対象を変更するcycleで移行する。

CIはv1のままの変更監査、profile上限超過、2系統未満のgeneral lexicon、pending coverage軸、未回収fact、派生形一括、included/integrated unionとclaimの不対応、union外support、final source result欠落、final PASSとsource result failの併存、budget_exhausted/in_progressのmergeを拒否する。

このゲートは資料の意味内容を代わりに判断しない。外部候補集合を独立に作るというPR #90の理想を、有限coverage、正規化された単一の正本、機械支援、安全停止によって実運用可能にする。
