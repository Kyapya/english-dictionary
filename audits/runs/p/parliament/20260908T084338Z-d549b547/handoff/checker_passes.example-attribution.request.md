# Independent checker handoff

Stage: `checker_passes/example-attribution`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.example-attribution.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_example_attribution_v6

## 目的

見出し語の各例文が、所属する語義ブロックへ意味的に帰属するかを、所属情報を参照しない先行判定（ブラインド再分類）で検査する。

## 担当タクソノミー分類

- `example_sense_attribution_mismatch`

## 検査ルール

- 検査は必ず次の2段階の順で行い、段階1の判定を段階2より先に確定・記録する。
- 段階1（ブラインド帰属判定）: `sense_structure` から語義番号、見出しの品詞・意味領域ラベル、訳語、定義の一覧を作る。次に `collocations_examples` の各例文（見出し語を含む例文のみ。類義語・反意語欄の例文は対象外）について、所属ブロック、コロケーション見出し、用途行を参照せず、例文と訳だけから最も自然な帰属語義を判定する。次点候補の有無と、判別根拠となった例文内の語句を記録する。
- 段階1では所属語義を含まない `example_attribution_blind_request_v1` だけを受け取り、判定を `example_attribution_blind_record_v1` として保存する。調整役はこの記録が保存されるまで所属キーを渡さない。
- `unique` 判定は、例文中で**見出し語そのものが担う意味関係、項構造、構文フレーム、結果状態、方向性**から他の有力候補語義を排除できる場合に限る。`doctor`、`project`、`variable`、`assignment`、`owner` など、単に話題分野・登場人物・対象領域を示す周辺語だけを根拠に `unique` としてはならない。
- `discriminating_terms` は、見出し語の意味選択に直接効く語句を記録する。可能なら見出し語に結び付く目的語・補語・前置詞句・小辞・結果表現・意味役割を用いる。単なる分野語・人物名詞・背景語は、それ自体が競合語義を意味的に排除することを説明できない限り判別語としない。
- `unique` の `rationale` では、最有力語義だけを説明して終えてはならない。少なくとも1つのもっともらしい競合語義を明示し、**同じ例文中の見出し語の使われ方**がなぜ競合語義では成立しないかを比較して述べる。
- 競合語義を排除する材料が話題分野などの周辺語しかない場合、または見出し語自体の意味関係から一意化できない場合は `ambiguous` とし、自然に成立する候補語義をすべて `candidate_sense_ids` に残す。表面的なトピック推定で曖昧性を消してはならない。
- 段階2（照合）: 保存済みの段階1判定を実際の所属ブロックと照合する。この段階で初めて、所属キーと所属語義の【語法・注意】を受け取る。照合時刻は段階1の記録時刻より後でなければならず、最終pass出力に段階1記録を変更せず埋め込む。
- 判定基準は次のとおり。
  - 帰属判定が所属ブロックと不一致: `blocking`。
  - 複数語義で同程度に自然であり、例文内に判別語がない: `blocking`。
  - 一致かつ一意: 問題なし。
- 訳文だけが別語義を示し英文は所属語義に一致する場合は、translationパスの担当として `unrouted_observation` で調整役へ返す。
- 語義の統合・分割そのものに問題があると疑われる場合は、sense-structureパスの担当として `unrouted_observation` で返す。
- 所属ブロックの【語法・注意】が示す語義区別に、そのブロック内の例文が反する場合は、本taxonomyのfindingとして例文側の位置をanchorにする。
- `example_translation_alignment` は英文と訳文の対応だけを扱い、英文自体の語義帰属は本パスが扱う。
- `argument_slot_role_mismatch` は統語スロットと意味役割の実現だけを扱い、統語的に正しいが意味的に別語義である例文は本パスが扱う。
- `cross_section_internal_contradiction` は例文を入力に含めないセクション間矛盾を扱い、例文起点の矛盾は本パスが扱う。

## 入力として受け取るセクション

- `sense_structure`
- `collocations_examples`

段階1入力の `collocations_examples` には、所属ブロック、コロケーション見出し、用途行を除いた例文と訳だけを入れる。段階2の所属キーと所属語義の【語法・注意】は、段階1記録の保存後に別artifactとして受け取る。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "example_sense_attribution_mismatch",
  "location": {
    "section": "collocations_examples",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない例文行"
  },
  "severity": "blocking",
  "rationale": "ブラインド帰属判定、実際の所属語義、曖昧性、判別語の有無",
  "evidence_link_ids": [],
  "suggested_direction": "例文置換 | 語義ブロック間の移動 | 判別語の追加"
}
```

最終pass出力にはfindingと併せて、段階1の `blind_attribution_record`、段階2の `aligned_at`、必要に応じて `unrouted_observations` を含める。`suggested_direction` は例文置換、語義ブロック間の移動、判別語の追加のいずれか1方向を記録する。

段階1はrun別の不透明ID・shuffle順を使う。非公開alignment keyで復元し、request hashを照合する。


## Input packet

```json
{
  "schema_version": "example_attribution_blind_request_v1",
  "pass_id": "example-attribution",
  "taxonomy_ids": [
    "example_sense_attribution_mismatch"
  ],
  "specification": "prompts/check_pass_example_attribution_v6.md",
  "input_body_sha256": "a79a267d48a57dc1c95b4c79fa1496950e4ca751f098fd6d46c4a89b6afdfcd2",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 34,
        "label": "1. 【名詞・可算／固有名詞的用法】議会、国会；議会を構成する議員たち",
        "definition": "国または地域の代表者が集まり、法律の制定・改正、政策や予算の審議、政府の監督などを行う制度的な機関、またはその構成員全体を指す。国によって正式名称・構成・権限が異なるため、日本語訳は文脈に応じて「議会」「国会」などとなる。特定国の正式または慣用的な機関名として用いる場合は `Parliament` と大文字で始めることがある。"
      },
      {
        "sense_id": "sense:002",
        "line": 118,
        "label": "2. 【名詞・可算】一議会期、ある選挙で成立した特定期の議会",
        "definition": "一度の総選挙後に成立した議会が、次の選挙や解散まで同じ制度上の単位として存続する期間、またはその期間に活動する特定の議員構成を指す。個々の会議や一日ごとの開会ではなく、複数の `session` を含み得る、より大きな単位である。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-b8cd9fdc0171",
        "example": "The proposal is unlikely to pass during the current parliament.",
        "translation": "その提案が今議会期中に可決される可能性は低い。"
      },
      {
        "example_id": "ex-b146a53dd60b",
        "example": "The committee recommended that the issue be reconsidered in the next parliament.",
        "translation": "委員会は、その問題を次の議会期に再検討するよう勧告した。"
      },
      {
        "example_id": "ex-601110af9a87",
        "example": "The prime minister asked the head of state to dissolve Parliament and call an election.",
        "translation": "首相は国家元首に国会を解散して選挙を実施するよう求めた。"
      },
      {
        "example_id": "ex-9538770a763d",
        "example": "The election resulted in a hung parliament, so the parties began coalition talks.",
        "translation": "選挙の結果、どの政党も単独過半数を持たない議会となり、各党は連立協議を始めた。"
      },
      {
        "example_id": "ex-c5f33fd7accb",
        "example": "He was elected to Parliament at the age of thirty-two.",
        "translation": "彼は32歳で国会議員に選出された。"
      },
      {
        "example_id": "ex-0e3c86dc7257",
        "example": "She was elected as a member of parliament for the first time last year.",
        "translation": "彼女は昨年、初めて国会議員に選出された。"
      },
      {
        "example_id": "ex-8f5e2ac8d6fa",
        "example": "The government promised to introduce the measure during this parliament.",
        "translation": "政府は今議会期中にその措置を導入すると約束した。"
      },
      {
        "example_id": "ex-4ca26aab1f40",
        "example": "The bill currently before Parliament would strengthen consumer protections.",
        "translation": "現在国会で審議中のその法案は、消費者保護を強化するものだ。"
      },
      {
        "example_id": "ex-fa0be8ce5cf8",
        "example": "The party won twelve additional seats in Parliament.",
        "translation": "その政党は国会でさらに12議席を獲得した。"
      },
      {
        "example_id": "ex-ba3af3198ddf",
        "example": "Major constitutional reform may take the lifetime of a parliament to complete.",
        "translation": "大規模な憲法改革は、一議会期を通じてようやく完了することもある。"
      },
      {
        "example_id": "ex-90a5a06d1da9",
        "example": "The requirement was introduced by an Act of Parliament.",
        "translation": "その要件は議会制定法によって導入された。"
      },
      {
        "example_id": "ex-afc5f66e3165",
        "example": "Parliament passed the bill after months of debate.",
        "translation": "国会は数か月にわたる審議の末、その法案を可決した。"
      }
    ]
  },
  "blind_protocol": {
    "stage": 1,
    "withheld_fields": [
      "assigned_sense_id",
      "collocation_heading",
      "usage_line",
      "example_group_boundary",
      "document_order"
    ],
    "required_output_schema": "example_attribution_blind_record_v1"
  },
  "finding_schema": {
    "required": [
      "taxonomy_id",
      "location",
      "severity",
      "rationale"
    ],
    "severity": [
      "blocking",
      "minor"
    ],
    "location_required": [
      "section",
      "line_start",
      "line_end",
      "exact_quote"
    ]
  },
  "specification_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
  "source_artifact_sha256": "8c3d3e8bc2bb85f93e6c7bd3c0bd855e1fcdc3416d4e6aac306d4c0d2c2683e4",
  "normalized_input_sha256": "a55d1729836e624fbd8daa8943c43e14d69afd0e1300c3b43450f36246213ac2"
}
```
