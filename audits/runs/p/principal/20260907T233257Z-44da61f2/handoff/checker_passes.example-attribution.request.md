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
  "input_body_sha256": "0ce3b3f2256f78d6a313ae1445d684390dfb421a0112c14efeaaec945bd42057",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 40,
        "label": "1. 【形容詞・主に限定用法】主要な、最も重要な、第一の",
        "definition": "複数の原因、目的、人物、場所、要素などの中で、重要度・影響力・順位が最も高い、または特に高いものを示す。単に時間的に最初という意味ではなく、重要性や中心性の評価を表す。"
      },
      {
        "sense_id": "sense:002",
        "line": 125,
        "label": "2. 【名詞・可算】校長、学長、教育機関の長",
        "definition": "学校、カレッジ、その他の教育機関を管理する最高責任者。どの種類の教育機関を指すかは地域と制度によって異なる。"
      },
      {
        "sense_id": "sense:003",
        "line": 182,
        "label": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー",
        "definition": "会社、専門業務、交渉、舞台芸術などで、指導的地位・所有上の中心的地位・主要な役割を持つ人。具体的には企業の共同経営者・責任者、交渉の主要当事者、バレエ団の首席ダンサー、オーケストラの首席奏者などを指し、肩書きとして大文字で書かれることもある。"
      },
      {
        "sense_id": "sense:004",
        "line": 239,
        "label": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額",
        "definition": "借入・貸付の元の金額、または投資された当初の金額で、そこから生じる利息・利益・収益とは区別される金額。返済文脈では、元金への支払いは未返済債務の基礎額を減らす。個別の元本額や複数の契約上の元金を数える専門文脈では可算的にも扱われる。"
      },
      {
        "sense_id": "sense:005",
        "line": 303,
        "label": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "definition": "別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人はその権限の範囲内で本人のために行動し、代理関係では `principal` が権限の源となる。具体的な法的効果や責任範囲は法域、実際の権限、外観上の権限などによって異なるため、この語自体だけから一律に決まらない。"
      },
      {
        "sense_id": "sense:006",
        "line": 362,
        "label": "6. 【名詞・可算・法律】正犯、犯罪の主要関与者；主たる債務者・第一次的責任者",
        "definition": "刑事法の文脈では、犯罪を実行する、または法体系によっては犯罪の実行を指示・援助するなどして主要な刑事責任を負う者を指す。債務・保証の文脈では、保証人・連帯保証人などの二次的責任者と対比して、義務について第一次的に責任を負う者を指す。これらの具体的分類と責任範囲は法域・時代・制定法によって異なる。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-fdf173bc7ad4",
        "example": "The seller later learned that the buyer had acted for an undisclosed principal.",
        "translation": "売主は後に、買主が非顕名の本人のために行動していたことを知った。"
      },
      {
        "example_id": "ex-72934a48c8b4",
        "example": "Interest is calculated on the outstanding principal amount.",
        "translation": "利息は未返済の元本金額に対して計算される。"
      },
      {
        "example_id": "ex-4232909ceaa2",
        "example": "She is a principal at an engineering consultancy.",
        "translation": "彼女はエンジニアリング・コンサルティング会社の上級責任者である。"
      },
      {
        "example_id": "ex-0d47a04a7fd9",
        "example": "The agent may sign the document on behalf of the principal.",
        "translation": "代理人は本人を代理してその書類に署名できる。"
      },
      {
        "example_id": "ex-48416206aa83",
        "example": "She served as principal for twelve years.",
        "translation": "彼女は12年間校長を務めた。"
      },
      {
        "example_id": "ex-d440a4c1cda5",
        "example": "The fund aims to protect the principal while generating modest returns.",
        "translation": "そのファンドは、控えめな収益を生みながら元本を保全することを目指している。"
      },
      {
        "example_id": "ex-8a67f3525667",
        "example": "The guarantor may seek reimbursement from the principal obligor after payment.",
        "translation": "保証人は支払い後、主たる債務者に償還を求められる場合がある。"
      },
      {
        "example_id": "ex-163c63b2967b",
        "example": "The board appointed Dr. Lee principal of the academy.",
        "translation": "理事会はリー博士をそのアカデミーの学長に任命した。"
      },
      {
        "example_id": "ex-94b7a91f4962",
        "example": "He became a principal dancer with the company at age twenty-four.",
        "translation": "彼は24歳でそのバレエ団の首席ダンサーになった。"
      },
      {
        "example_id": "ex-47c18b5436d2",
        "example": "The school principal met with parents after the incident.",
        "translation": "校長はその出来事の後、保護者と面会した。"
      },
      {
        "example_id": "ex-49c6d1fe1f87",
        "example": "The company moved its principal place of business to Osaka.",
        "translation": "その会社は主たる事業所を大阪に移した。"
      },
      {
        "example_id": "ex-f14d2b17bc1e",
        "example": "Extra payments can help you pay down the principal faster.",
        "translation": "追加返済をすれば、元金をより早く減らせる。"
      },
      {
        "example_id": "ex-ae3b36dcca8e",
        "example": "The borrower will begin repaying principal next year.",
        "translation": "借り手は来年、元金の返済を開始する。"
      },
      {
        "example_id": "ex-0bd92573efd0",
        "example": "Investigators identified corrosion as the principal cause of the failure.",
        "translation": "調査担当者は、腐食をその故障の主因と特定した。"
      },
      {
        "example_id": "ex-8eb0261eda14",
        "example": "The older judgment classified the defendant as a principal in the first degree.",
        "translation": "その古い判決は被告人を第一級正犯に分類した。"
      },
      {
        "example_id": "ex-5367d0414df6",
        "example": "The principal of the college welcomed the new students.",
        "translation": "そのカレッジの学長は新入生を歓迎した。"
      },
      {
        "example_id": "ex-64fcb271ebf1",
        "example": "An agent generally owes duties of loyalty and care to the principal.",
        "translation": "代理人は一般に、本人に対して忠実義務と注意義務を負う。"
      },
      {
        "example_id": "ex-3703bb49e52f",
        "example": "The principal reason for the delay was a shortage of parts.",
        "translation": "遅延の主な理由は部品不足だった。"
      },
      {
        "example_id": "ex-31ca39a064e5",
        "example": "The principals in the merger met without their advisers.",
        "translation": "合併の主要当事者たちは、助言者を交えずに会談した。"
      },
      {
        "example_id": "ex-92549cf1f6b9",
        "example": "The statute treats a person who knowingly assists the offense as a principal.",
        "translation": "その制定法は、情を知って犯罪を援助する者を正犯として扱う。"
      },
      {
        "example_id": "ex-cc28294ad89a",
        "example": "The principal clarinet played the opening solo.",
        "translation": "首席クラリネット奏者が冒頭のソロを演奏した。"
      },
      {
        "example_id": "ex-4203a9ed810b",
        "example": "Tourism is a principal source of income for the island.",
        "translation": "観光はその島の主要な収入源の一つである。"
      },
      {
        "example_id": "ex-3a660aec3db3",
        "example": "She is one of the principal architects of the reform.",
        "translation": "彼女はその改革の主要な立案者の一人である。"
      },
      {
        "example_id": "ex-118a0c4f74a1",
        "example": "The contract created a principal-agent relationship between the owner and the broker.",
        "translation": "その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。"
      },
      {
        "example_id": "ex-c391c2db4b1c",
        "example": "The monthly payment includes both principal and interest.",
        "translation": "毎月の返済額には元金と利息の両方が含まれる。"
      },
      {
        "example_id": "ex-9ce5caa56e39",
        "example": "Under the agreement, the company remains liable as principal for the debt.",
        "translation": "その契約の下で、会社はその債務について主たる当事者として引き続き責任を負う。"
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
  "source_artifact_sha256": "716ae619355b7e599eb5e976d897049d038933873f4f3902aa220ecdbdddd065",
  "normalized_input_sha256": "44fa4108aa8f4ba9ba29c3c025180f2b0ea3600603ee54ebae214693abd4949a"
}
```
