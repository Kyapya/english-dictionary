# Independent checker recheck handoff

Stage: `checker_recheck/example-attribution`

Run this request in its own independent subagent/session. The six invalidated checker passes are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes. Pronunciation is deterministically reused and must not be reviewed again.

Save exactly one JSON response as `recheck/example-attribution.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each rechecked pass must use a different agent_id.
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
  "input_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 40,
        "label": "1. 【形容詞】主要な、最も重要な、第一の",
        "definition": "複数の原因、目的、人物、場所、要素などの中で、重要度・影響力・順位が最も高い、または特に高いものを示す。単に時間的に最初という意味ではなく、重要性や中心性の評価を表す。"
      },
      {
        "sense_id": "sense:002",
        "line": 120,
        "label": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "definition": "組織で支配的権限または主導的地位を持つ人。特に、学校、カレッジ、その他の教育機関を管理する最高責任者を指す。教育上どの種類の機関を指すかは地域と制度によって異なる。"
      },
      {
        "sense_id": "sense:003",
        "line": 153,
        "label": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "definition": "舞台芸術で主要な役を担う演者、またはオーケストラで一つのセクションを率いる奏者。一般の重要人物ではなく、芸術分野で確立した役割名を指す。"
      },
      {
        "sense_id": "sense:004",
        "line": 186,
        "label": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "definition": "借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。信託法では、収益と区別される信託財産そのもの、すなわち信託元本・corpusを指す。"
      },
      {
        "sense_id": "sense:005",
        "line": 224,
        "label": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "definition": "別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。"
      },
      {
        "sense_id": "sense:006",
        "line": 266,
        "label": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "definition": "刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。"
      },
      {
        "sense_id": "sense:007",
        "line": 294,
        "label": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "definition": "債務・保証の文脈で、保証人などの二次的責任者と対比され、義務について第一次的に責任を負う人または法人。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-8ca9f0f7fb75",
        "example": "Investigators identified corrosion as the principal cause of the failure.",
        "translation": "調査担当者は、腐食をその故障の主因と特定した。"
      },
      {
        "example_id": "ex-38069d83ef5e",
        "example": "A principal with controlling authority approved the proposal.",
        "translation": "支配的権限を持つ責任者がその提案を承認した。"
      },
      {
        "example_id": "ex-9cfdbc4c2144",
        "example": "She is one of the principal architects of the reform.",
        "translation": "彼女はその改革の主要な立案者の一人である。"
      },
      {
        "example_id": "ex-f4568670c1d0",
        "example": "Trust principal is distinct from income.",
        "translation": "信託元本は収益とは別のものである。"
      },
      {
        "example_id": "ex-8ece0513fcc7",
        "example": "The contract created a principal-agent relationship between the owner and the broker.",
        "translation": "その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。"
      },
      {
        "example_id": "ex-2ca65afc4e96",
        "example": "Principal is distinct from interest on the loan.",
        "translation": "元金はその融資の利息とは別のものである。"
      },
      {
        "example_id": "ex-db4b59de548e",
        "example": "The principal is distinct from the surety, who has secondary liability.",
        "translation": "主たる債務者は、二次的責任を負う保証人とは別の当事者である。"
      },
      {
        "example_id": "ex-92ade043c583",
        "example": "The principal is the first player of the violin section.",
        "translation": "その首席奏者はバイオリン・セクションの第一奏者である。"
      },
      {
        "example_id": "ex-0f398057ecca",
        "example": "The principal is primarily liable for the debt.",
        "translation": "主たる債務者はその債務について第一次的責任を負う。"
      },
      {
        "example_id": "ex-97117752dad4",
        "example": "The principal is the initial amount invested.",
        "translation": "元本とは最初に投資された金額である。"
      },
      {
        "example_id": "ex-c02d25a31625",
        "example": "The principal reason for the delay was a shortage of parts.",
        "translation": "遅延の主な理由は部品不足だった。"
      },
      {
        "example_id": "ex-e17424d5a189",
        "example": "Tourism is a principal source of income for the island.",
        "translation": "観光はその島の主要な収入源の一つである。"
      },
      {
        "example_id": "ex-391b762438b0",
        "example": "She is a principal dancer.",
        "translation": "彼女は主要な役を担うダンサーである。"
      },
      {
        "example_id": "ex-8ba8399dc1d4",
        "example": "Under the statute, the principal is directly responsible for the crime.",
        "translation": "その制定法の下で、当該 `principal` はその犯罪について直接責任を負う。"
      },
      {
        "example_id": "ex-d0531d4fbc57",
        "example": "The principal is in charge of the school.",
        "translation": "その校長が学校の管理を担っている。"
      },
      {
        "example_id": "ex-f83a76d740f8",
        "example": "The agent may sign the document on behalf of the principal.",
        "translation": "代理人は本人を代理してその書類に署名できる。"
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
  "source_artifact_sha256": "e97de23f48433c92c1418c79368c269f37025be735dd52c0dced6832eb2c7705",
  "normalized_input_sha256": "a045d265c6e1769d5bea7e23eb98ac13671b7939b8a55686d45a6f5515cf30a4"
}
```
