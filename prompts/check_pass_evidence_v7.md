# check_pass_evidence_v7

## 目的

主張単位の根拠リンクが、対象主張を直接支持するかだけを検査する。source-first工程との二重チェックを避けるため、このパスは資料探索計画、source inventoryのcoverage、fact収集をやり直さない。

## 担当タクソノミー分類

- `evidence_claim_mismatch`

## 検査ルール

- source-first工程が固定したsource・fact・claim unit・対象sectionを受け、本文→claim→外部資料の三者を照合する。まず `article_target_ids` に対応する `article_targets[].text` と周辺の本文を読み、claimがその箇所で実際に述べられているか確認する。実在するIDでも、発音の箇所へ意味説明が結び付いているなど意味上の接続違いはblocking findingにする。
- 現行入力は `evidence_context_v2`。対象claimに関係するsource、fact、source union、claim unit、`source_supports` に、スクリプトが最新本文から抽出した `article_targets` を加える。旧 `evidence_context_v1` は過去runの再現用。`source_inventory_sha256`、`source_first_artifact_sha256`、本文hashの一致を機械検証済みでなければ開始しない。
- locatorの外部資料を実際に開き、該当箇所を本文と照合する。作成者のfactや `support_summary` は照合の手掛かりであり、独立した外部確認の代わりにならない。同じページは一度開いて関係claimをまとめて確認できる。新しい探索計画や全factの作り直しは不要だが、既存資料の再閲覧は必要である。
- 資料名・著者・locator・引用箇所が同じ資料を指すかを確認する。複数辞書名を一つのlocatorで代表させたり、別資料の語源説明をそのページの記述として扱ったりしない。
- 外部閲覧機能がない実行、アクセス不能、該当箇所不明では、既知知識や要約で補って確認済みにせず、対象claimのblocking findingに `insufficient_evidence` と確認できなかったlocatorを記す。API/handoffのどちらでもこの条件は同じ。現在の標準API呼出しには閲覧ツールがないため、外部資料を閲覧できるhandoff reviewerを使う。
- source-first artifactが欠落、未完了、schema不正、参照切れ、本文hash不一致の場合はfail closedとし、再探索やfact追加で補わない。
- 資料名や検索結果見出しが存在するだけで合格にせず、locator、該当箇所、支持内容、当該語義・構文への適用範囲を確認する。
- 別義、別品詞、別法域、別地域、別時代の記述を現在の対象主張へ流用しない。
- 高リスク主張に `two_sources_or_primary` が指定される場合、同一引用元を別IDにした重複を独立2資料として数えない。一次資料1件を使う場合は当該主張へ直接適用できることを確認する。
- 発音、語源、語義境界、文法制約、完全フレーム、例文の自然さ、絶対表現、地域差、頻度、専門説明、類義語・反意語差のevidence linkを個別に確認する。
- 断定的主張では支持例だけでなく、source-first記録にある反例・矛盾探索の方法と結果が主張範囲に対応するか確認する。
- 資料が食い違う場合、本文が差を反映して範囲を限定しているかを確認する。根拠から決められない内容をpassにしない。
- このパスはclaimの辞書学的正しさを他パスの代わりに再判定せず、「提示された根拠がそのclaimを支えるか」に限定する。

## 入力として受け取るセクション

- `pronunciation`
- `etymology`
- `word_formation`
- `core_image`
- `sense_structure`
- `frequency_register`
- `frames`
- `collocations_examples`
- `usage_notes`
- `lexical_relations`
- source-first工程が生成したsource inventory、fact、claim unit、evidence link
- API modeとhandoff modeはいずれも `scripts/check_passes.py` が生成した同一の正規化requestを使う。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "evidence_claim_mismatch",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "根拠対象となる本文主張"
  },
  "severity": "blocking | minor",
  "rationale": "source locator・支持内容・適用範囲の不一致",
  "evidence_link_ids": ["問題のある既存link ID"],
  "suggested_direction": "主張限定、根拠差替え、holdの方向"
}
```

根拠が主張を支持しない状態は原則 `blocking` とする。

出力は問題のある箇所のfindingsに集中する。正常claimごとの合格理由・本文の再掲・別の全件証明表は作らない。全対象を確認して問題がなければ空のfindingsでよい。これは未確認範囲を省略してよいという意味ではない。
