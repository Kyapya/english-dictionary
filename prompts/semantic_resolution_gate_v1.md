# semantic_resolution_gate_v2

この仕様は、レビューで一度得た正しい意味判断を後工程が無視したまま `PASS` することを防ぐためのハードゲートである。`content_audit_v3` の既存監査を置き換えず、意味上の指摘・修正・最終照合を本文ハッシュへ結び付ける。

## 目的

次の失敗を禁止する。

- コールドレビューが正しい問題を発見したのに、修正後本文へ同じ問題または同値の問題が残ったまま解決済みにする。
- 指摘を修正した後に本文が再変更されたのに、古い解決判定をそのまま使う。
- 最終盲検棚卸しで正しい語義境界・除外判断を作ったのに、その判断と本文を照合しないまま `PASS` する。
- 指摘箇所だけ直し、同じ概念が現れるコアイメージ、定義、語法、例文、類義語等の影響範囲を確認しない。

## 基本原則

1. 内容上の問題が確認されたfindingは、自由文の修正指示だけで閉じない。検証可能な原子的意味制約へ変換する。
2. 解決判定は必ず最新版の `body_sha256` へ結び付ける。本文が1文字でも変われば、以前の解決確認はstaleとして再確認する。
3. semantic constraintは、対象target、relation、または記事内検索語の少なくとも一つを持ち、どこまで再確認したかを外部化する。
4. 最終審査はfindingの修正箇所だけでなく、そのconstraintが影響するblast radiusを再確認する。
5. 最終盲検棚卸しの各候補には、本文が満たすべき／満たしてはならない意味上のassertionを盲検段階で作る。照合段階で後付けしてはならない。
6. 最終 `PASS` では、全semantic constraint、全盲検candidate assertion、全finding resolutionが現在の本文ハッシュに対して `pass` でなければならない。

## 監査JSONの `semantic_gate`

現行本文を変更した `content_audit_v3` 監査には次を追加する。

```json
{
  "semantic_gate": {
    "version": "semantic_resolution_v2",
    "body_sha256": "<current body sha256>",
    "constraints": [],
    "final_inventory_checks": []
  }
}
```

semantic gateのない旧監査を互換読み込みする場合も、`checked` / `final` の根拠にはできない。見逃しが判明した旧PASSは `audits/review_invalidations.json` に本文ハッシュ付きで登録し、本文を変えなくても `needs_review`、checked `false` へ戻す。本文を修正した後も記録は削除せず、`superseded` と修正版本文ハッシュを記録する。次回審査ではv2 gateを必須とする。

## コールドレビューfindingから意味制約を作る

`resolutions[].problem_confirmed` が `true` のfindingは、1件以上の `semantic_gate.constraints` を持たなければならない。単に「修正した」ではなく、再発したら不合格にできる関係として書く。

例の形式は次のとおりである。ここに示す内容は特定単語向けテンプレートではなく、関係の書き方の例である。

```json
{
  "id": "SC001",
  "source_type": "cold_finding",
  "source_id": "CR-001-001",
  "statement": "AはBに作用する側であり、Bから作用を受ける対象として説明しない",
  "polarity": "must_hold",
  "scope": "technical definition and all summaries",
  "source_anchor_ids": ["CR-001-001:A1"],
  "affected_target_ids": ["definition:007", "core_image:002"],
  "affected_relation_ids": ["core_sense_mapping:007"],
  "article_queries": ["作用対象", "作用する"],
  "verified_on_body_sha256": "<current body sha256>",
  "verification_notes": "最新版全文で定義・コアイメージ・語法を照合し、逆向きの説明が残っていないことを確認した"
}
```

- `polarity` は `must_hold` または `must_not_hold`。
- `statement` は1つの判定可能な意味関係にする。複数関係を1文へ詰め込まない。
- `affected_target_ids` と `affected_relation_ids` は現在の監査IDを使う。
- 既存targetで表せない「記事全体にこの誤った表現がないこと」の確認には `article_queries` を使う。
- target/relation/queryの少なくとも一つを必須とする。
- `verified_on_body_sha256` は、constraintを最後に全文照合した本文ハッシュである。本文を再修正したら必ず更新前に再照合する。

対応するresolutionには次を追加する。

```json
{
  "semantic_invariant_ids": ["SC001"],
  "resolved_on_body_sha256": "<current body sha256>",
  "scope_anchor_results": [
    {
      "id": "CR-001-001:A1",
      "status": "corrected",
      "affected_target_ids": ["core_image:002"],
      "article_queries": ["作用対象"],
      "notes": "最新版のコアイメージを確認した"
    }
  ]
}
```

`resolved_on_body_sha256` は「修正を入れた時点のハッシュ」ではない。**そのfindingが最新版全文で解決していると最後に確認した本文ハッシュ**である。後続修正で本文ハッシュが変わった場合、同じコールドレビューをやり直す必要はないが、全constraintとblast radiusは最新版へ再照合する。

## blast radius

採用findingの再確認では、元の指摘位置だけを見ない。少なくとも次を対象にする。

- resolutionの `affected_target_ids` と `affected_relation_ids`。
- semantic constraintの全target・relation。
- constraintの `article_queries` が該当する全文箇所。
- 同じ概念を要約するコアイメージ、定義、語法、相互参照、例文、類義語・対照表現。

最終審査の `final_review.finding_results[]` には次を追加する。

```json
{
  "verified_body_sha256": "<current body sha256>",
  "verified_invariant_ids": ["SC001"],
  "blast_radius_target_ids": ["definition:007", "core_image:002"],
  "blast_radius_relation_ids": ["core_sense_mapping:007"],
  "blast_radius_queries_checked": ["作用対象", "作用する"]
}
```

元findingの全scope anchor、全ID、affected targetを含む全生成relation、全queryを再確認していないfindingを `resolution_status: resolved` / `status: pass` にしない。`blast_radius_queries_checked` の各queryには `blast_radius_query_results` で最新版本文の一致件数と一致target IDを記録し、スクリプトの再計算結果と一致させる。

## 最終盲検棚卸しと本文の強制照合

最終盲検審査では、`final_review.independent_candidates` の各候補に `semantic_assertions` を1件以上付ける。これは監査台帳を開く前に、候補の `surface_form`、`frame`、`meaning`、`disposition`、`rationale` と同時に作る。

```json
{
  "id": "IC20",
  "surface_form": "...",
  "frame": "...",
  "meaning": "...",
  "disposition": "excluded",
  "rationale": "...",
  "semantic_assertions": [
    {
      "id": "IC20:A1",
      "statement": "この候補を見出し語の通常義として本文へ一般化しない",
      "polarity": "must_not_hold",
      "scope": "definitions, core image, usage notes and examples"
    }
  ]
}
```

`semantic_assertions` は盲検原出力 `audits/runs/.../final_blind.json` に実体を残す。照合開始後に追加・変更してはならない。ハードゲートは盲検原出力と最終監査JSONのassertionが一致することを確認する。

監査台帳を開いた後、各最終candidateについて `semantic_gate.final_inventory_checks` を1件ずつ作る。

```json
{
  "candidate_id": "IC20",
  "assertion_ids": ["IC20:A1"],
  "checked_on_body_sha256": "<current body sha256>",
  "article_target_ids_checked": ["definition:001", "core_image:001"],
  "article_relation_ids_checked": ["learner_generalization:001"],
  "article_queries_checked": ["個別", "配送", "delivery"],
  "article_query_results": [
    {"query": "delivery", "match_count": 2, "matched_target_ids": ["definition:003", "usage_note:003"]}
  ],
  "status": "pass",
  "notes": "除外境界と矛盾する記述が定義・コアイメージ・語法にないことを確認した"
}
```

- `final_inventory_checks` は最終盲検candidateと1対1で対応する。
- `included` 候補では、照合段階で追加された `article_target_ids` をすべて再確認する。
- `excluded` 候補でも「本文に対応targetがない」だけで済ませない。境界を侵食しうる関連target、relation、または明示的な全文queryを確認する。
- 最終decisionが `pass` の場合、全inventory checkも `pass` でなければならない。
- `included` 候補では対応targetだけでなく、そのtargetを含む全生成relationを確認する。
- `article_queries_checked` は `article_query_results` と1対1で対応し、最新版本文の一致件数・一致target IDが機械的再計算と一致しなければならない。

## 原出力と監査マニフェストの完全照合

通常、コールド、最終盲検、最終照合の原出力は別々のJSONとして保存する。v2 gateでは、次を件数ではなく項目内容まで完全照合する。

- 通常レビューの `independent_candidates`、`target_results`、`relation_results`。
- コールドレビューの `summary`、全finding、全`scope_anchors`。
- 最終盲検の候補内容・収録判断・semantic assertions・article findings。
- 最終照合のinventory comparison、全target/relation/candidate/finding結果、全evidence check、全inventory check、blocker、decision。

原出力が集計件数しか持たない場合や、監査マニフェストにだけ個別PASSが存在する場合は不合格とする。

## 根拠適合性の最終確認

各 `evidence_link` は資料位置に加えて `source_excerpt_or_summary` を持つ。高リスク対象の2資料要件は、別IDではなく異なる引用元として数え、いずれも対象主張を直接支持しなければならない。最終審査は使用した全根拠リンクについて `final_review.evidence_checks` を作り、主張支持、locator、適用範囲、矛盾探索を個別判定する。最終PASSでは全checkがpassでなければならず、この配列も最終照合の原出力と完全一致させる。

## stale判定

次のいずれかが現在の `body_sha256` と一致しなければ、最終PASSを禁止する。

- `semantic_gate.body_sha256`
- 全constraintの `verified_on_body_sha256`
- 問題確認済みresolutionの `resolved_on_body_sha256`
- 対応するfinal finding resultの `verified_body_sha256`
- 全final inventory checkの `checked_on_body_sha256`

後続修正で本文ハッシュが変わった場合は、古い確認日時や「revision-003で修正した」等の説明が残っていても解決済みとは扱わない。

## 機械検証

PRでは次を必須にする。

```bash
python scripts/semantic_resolution_gate.py validate-changed --base "$BASE_SHA" --head "$HEAD_SHA"
```

特定記事の完成状態は次で確認する。

```bash
python scripts/semantic_resolution_gate.py validate-entries entries/a/apple.md
```

既存の未移行監査を含む全体確認では互換モードを使う。

```bash
python scripts/semantic_resolution_gate.py validate-audited --compat
```

互換モードはsemantic gateが存在しない未変更旧監査を許容するだけであり、gateが存在する監査の不整合は許容しない。

【semantic resolution gate v2 終わり】
