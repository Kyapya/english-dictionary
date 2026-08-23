# source_first_audit_v1

> **履歴互換専用:** 新規または変更監査には使わない。現行仕様は `prompts/source_first_audit_v2.md` とする。

この仕様は、本文側の語義分類とレビュー担当の同じ思い込みが相互に正当化されることを防ぐため、通常チェックの根拠収集と最終審査の照合を source-first / claim-centric にする追加ハードゲートである。特定の見出し語向けルールではなく、すべての新規・変更監査へ適用する。

## 目的

次の失敗を防ぐ。

1. 本文や通常レビューが作った語義一覧を出発点にし、主要辞書にある別の語義・品詞・専門用法を候補集合から落とす。
2. 複数の派生語・関連形を一つの候補へまとめ、一部の形だけを直接支持する資料で全体を合格させる。
3. targetごとに「資料が支持する」とだけ記録し、資料のどの原子的事実がどの本文主張を支えるか不明なまま根拠要件を満たす。
4. 通常チェックと最終審査が同じ欠落を共有しただけなのに、両者一致を外部根拠との一致として扱う。

## 1. source-first 語義・用法棚卸し

通常チェックでは、本文との語義比較を始める前に、信頼できる複数資料または直接適用できる一次資料から、各資料が明示する語義・品詞・派生形・専門ラベル・主要制約を資料ごとに独立抽出する。本文の語義番号、語義名、候補数、既存 `independent_candidates` を抽出候補の上限にしてはならない。

監査JSONの `source_first_audit` に次を保存する。

- `version: source_first_audit_v1`
- `inventory_completed_before_article_comparison: true`
- `inventory_completed_at`
- `article_comparison_started_at`
- `sources[]`
- `source_union[]`
- `claim_units[]`

`inventory_completed_at` は `article_comparison_started_at` より前でなければならない。

### sources[].facts[]

各資料のfactは、その資料から直接読み取れる一つの事実だけを表す。

必須項目:

- `id`
- `form`
- `kind`: `sense` / `derived_form` / `usage_rule` / `etymology` / `pronunciation` / `register` / `other`
- `statement`
- `source_detail`

資料差を先に統合せず、同じ事実が複数資料にある場合もまず各資料側のfactとして保持する。

## 2. 派生語・関連形の原子化

`kind: derived_form` のfactと、`claim_type: derived_form` のclaimは一つの具体的な表層形だけを対象にする。`A/B/C`、`A, B`、`A・B` のように複数形を一つへまとめない。

派生語同士の役割が近くても、語形ごとに直接根拠、意味、レジスター、専門性を確認する。一つの派生語の辞書項目を、別の派生語の意味の直接根拠に流用しない。

## 3. source union と本文の双方向比較

資料ごとのfactを確認した後、同一または十分近い事実だけを `source_union[]` に束ねる。各union itemは次を持つ。

- `id`
- `source_fact_ids`
- `canonical_statement`
- `disposition`: `included` / `integrated` / `excluded`
- `rationale`
- `article_target_ids`

全source factは少なくとも一つのunion itemから参照されなければならない。本文へ独立語義として出さない場合も、`integrated` または `excluded` と理由を残す。主要資料にだけ存在し本文にも通常棚卸しにもないfactを黙って捨ててはならない。

## 4. claim-centric 根拠台帳

根拠の正本は、targetごとの一般的な「supported」宣言ではなく、原子的な `claim_units[]` とする。一つのclaim unitは一つの判定可能な主張だけを表す。

必須項目:

- `id`
- `subject_form`
- `claim_type`
- `statement`
- `source_fact_ids`
- `article_target_ids`
- `source_supports[]`

`source_supports[]` は少なくとも `source_fact_id` と `support_summary` を持ち、そのsource factがclaimのどの部分を直接支えるかを具体的に書く。資料名や「このtargetを支持する」というだけの記述を直接根拠として扱わない。

複数targetが同じclaimを表す場合は同じclaim unitを参照してよい。targetごとに同一根拠文を複製しない。これにより監査量の増加を品質の代用にしない。

## 5. 最終審査での直接source比較

最終審査の盲検棚卸し・sealまでは従来どおり、通常チェックやsource inventoryを見ない。

seal後の照合段階では、通常チェック側の `independent_candidates` との一致確認に加えて、`source_first_audit.source_union` を最終審査担当自身が直接確認する。通常候補と最終候補が一致していても、それだけでsource factの網羅性を合格にしない。

`final_review.source_inventory_results[]` を `source_union[]` と1対1で作り、各項目に次を記録する。

- `union_id`
- `source_fact_ids_checked`
- `article_target_ids_checked`
- `status`: `pass` / `fail`
- `notes`

`source_fact_ids_checked` は対応union itemのfactを漏れなく含み、`article_target_ids_checked` は本文へ収録・統合したunion itemについて対応targetを漏れなく含む。`excluded` でも除外理由と資料内容を直接確認する。

最終decisionが `pass` の場合、全source inventory resultが `pass` でなければならない。

## 6. 既存監査との関係

既存の `targets`、`relations`、`evidence_links`、`semantic_gate` は廃止しない。source-first gateはそれらより上流の候補集合と、根拠の原子的対応を保証する追加契約である。

- `targets` / `relations`: 本文内の検査単位。
- `source_first_audit.sources` / `source_union`: 外部資料から独立に作る候補集合。
- `claim_units`: 外部factと本文targetを結ぶ原子的主張。
- `semantic_gate`: 発見済み意味判断の後工程での消失を防ぐ。

同じ役割を重複生成せず、各層の責務を混同しない。

## 7. 必須機械検証

新規または変更された監査は次を通す。

```bash
python scripts/source_first_audit_gate.py validate-entries <entry path>
```

PRでは `validate-changed` を実行する。

このゲートは少なくとも、source-first inventoryの欠落、記事比較より後に作られたinventory、未回収source fact、派生語の一括監査、source factを持たないclaim、union itemとの最終直接照合漏れ、final PASS時のsource inventory failを拒否する。

機械検証は資料の意味そのものを判断しない。外部資料から候補集合を先に作り、各原子的主張と資料factを結び、最終審査がその外部集合へ直接戻ったという証跡を必須化するためのゲートである。
