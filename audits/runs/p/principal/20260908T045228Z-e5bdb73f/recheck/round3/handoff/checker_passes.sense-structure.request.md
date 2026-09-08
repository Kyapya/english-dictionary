# Independent checker handoff

Stage: `checker_passes/sense-structure`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.sense-structure.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_sense_structure_v6

## 目的

見出し語をゼロベースで棚卸しし、語義境界、品詞転換、派生形、コアイメージ、セクション横断の意味範囲を検査する。旧本文の語義番号・見出し・項目数を候補集合の出発点にしない。

## 担当タクソノミー分類

- `sense_boundary_overlap`
- `cross_section_internal_contradiction`
- `compound_component_generalization`

## 検査ルール

- 主要品詞、主要義、字義・比喩・慣用義、句動詞、分詞形容詞、主要な品詞転換・派生形を独立候補として確認する。
- 一つの辞書の見出し分けを写さず、完全フレーム、中心意味、結果状態、評価、レジスター、頻度、学習価値から収録・統合・簡潔化・除外を判断する。
- 主語・目的語の種類や対象分野だけで語義を分けず、同じ程度表現・構文・例が複数語義を横断する場合は過剰分割を疑う。
- 基本義から生じる評価的・文脈的含意、特定構文の効果を独立した語彙的意味として立てない。一方、中心意味・品詞・項構造・結果状態・評価が学習上重要に異なる用法は統合しない。
- コアイメージ、語義見出し、定義、語法、文法パターン、類義語説明で同じ概念の範囲・方向が一致するか確認する。
- コアイメージがある場合、列挙枝と明示的除外の和集合が全語義にちょうど1回対応するか確認する。制度上の要件だけが特殊で語彙的核を共有する専門義を枝から除外しない。
- 同語源であることだけを理由に現代話者に結び付きにくい語義を同じ核へ押し込まない。
- 複合語・派生語・専門句の一構成要素の性質を、複合表現全体または見出し語の一般則へ拡張しない。
- 語形成欄や語法注記だけに主要品詞転換が存在する場合は、番号付き語義の欠落として扱う。
- 主要候補の収録先がなければ、形式上の欄が揃っていても欠落とする。除外には自由結合、極低頻度、根拠不足、既出義の言い換え等の具体理由が必要である。

## 入力として受け取るセクション

- `core_image`
- `sense_structure`
- `usage_notes`
- `word_formation`

## findingの出力スキーマ

```json
{
  "taxonomy_id": "sense_boundary_overlap | cross_section_internal_contradiction | compound_component_generalization",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "語義境界・矛盾・一般化の判定理由",
  "evidence_link_ids": [],
  "suggested_direction": "追加・統合・分割・移動・限定の方向"
}
```

語義・品詞・構文構成の追加、削除、統合、分割は `blocking` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "sense-structure",
  "taxonomy_ids": [
    "sense_boundary_overlap",
    "cross_section_internal_contradiction",
    "compound_component_generalization"
  ],
  "specification": "prompts/check_pass_sense_structure_v6.md",
  "input_body_sha256": "ab4f5e80d9bb3a91810ed5a9de22c2f3e3430a454ff6635d6a94a701f2ae9fe4",
  "input_sections": {
    "core_image": [
      {
        "line": 28,
        "text": "＃コアイメージ"
      },
      {
        "line": 30,
        "text": "`principal` の中心は、「重要度・権限・責任・金額の土台として第一に位置する」である。形容詞では主要なものを選び出し、名詞では組織で支配的権限・主導的地位を持つ人、教育機関の長や舞台芸術で確立した主要演者、利息・収益に対する元の金額や信託収益に対する財産本体、法的関係の主要当事者を指す。  "
      },
      {
        "line": 31,
        "text": "・重要度で第一に位置するもの → 「主要な、最も重要な」（語義1）  "
      },
      {
        "line": 32,
        "text": "・組織で権限・主導的地位を持つ人、特に教育機関の長 → 「責任者、校長、学長」（語義2）  "
      },
      {
        "line": 33,
        "text": "・利息・収益に対する基礎額、または信託収益に対する財産本体 → 「元金、元本、信託元本」（語義3）  "
      },
      {
        "line": 34,
        "text": "・代理関係で権限の源として第一に位置する当事者 → 「本人、依頼者」（語義4）  "
      },
      {
        "line": 35,
        "text": "・舞台芸術で主要な役割を担う人 → 「主要演者、オーケストラの首席奏者」（語義5）  "
      },
      {
        "line": 36,
        "text": "・適用法上 `principal` と分類される犯罪関与者 → 「犯罪関与者」（語義6）  "
      },
      {
        "line": 37,
        "text": "・債務・保証関係で第一次的責任を負う者 → 「主たる債務者・義務者」（語義7）  "
      }
    ],
    "sense_structure": [
      {
        "line": 41,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 43,
        "text": "【日本語訳・定義】複数の原因、目的、人物、場所、要素などの中で、重要度・影響力・順位が最も高い、または特に高いものを示す。単に時間的に最初という意味ではなく、重要性や中心性の評価を表す。  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 128,
        "text": "【日本語訳・定義】組織で支配的権限または主導的地位を持つ人。特に、学校、カレッジ、その他の教育機関を管理する最高責任者を指す。教育上どの種類の機関を指すかは地域と制度によって異なる。  "
      },
      {
        "line": 164,
        "text": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 166,
        "text": "【日本語訳・定義】借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。信託法では、収益と区別される信託財産そのもの、すなわち信託元本・corpusを指す。  "
      },
      {
        "line": 207,
        "text": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 209,
        "text": "【日本語訳・定義】別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。具体的な成立要件は適用法によって異なり得る。  "
      },
      {
        "line": 240,
        "text": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 242,
        "text": "【日本語訳・定義】舞台芸術で主要な役を担う演者、またはオーケストラで一つのセクションを率いる奏者。一般の重要人物ではなく、芸術分野で確立した役割名を指す。  "
      },
      {
        "line": 268,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 270,
        "text": "【日本語訳・定義】刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。  "
      },
      {
        "line": 301,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 303,
        "text": "【日本語訳・定義】債務・保証の文脈で、保証人などの二次的責任者と対比され、義務について第一次的に責任を負う人または法人。  "
      }
    ],
    "usage_notes": [
      {
        "line": 41,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 78,
        "text": "【語法・注意】`principal` と `principle` は綴りも意味も異なる。`principal` には形容詞で「最も重要な」を表す用法があり、別に人や金額などを指す名詞用法もある。一方、`principle` は「原理・原則」を表す名詞である。したがって「基本原則」は `basic principle` であり、`basic principal` ではない。  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 153,
        "text": "【語法・注意】一般の「重要人物」を自由に指す語ではなく、権限や主導的地位が文脈上確立した人に用いる。教育上の役職名は地域や制度によって異なるため、日本語の「校長」を機械的にすべて `principal` としない。  "
      },
      {
        "line": 164,
        "text": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 196,
        "text": "【語法・注意】`principal` は元の基礎額、`interest` は借入の対価または貸付・投資から生じる追加額であり、反意語ではなく関連する別の金額構成要素である。信託では `principal` が財産本体、`income` がそこから生じる収益を指す。`repay the principal` では `principal` 自体が目的語の名詞になる。日本語の「元利金」は `principal and interest` であり、`principal interest` とはしない。  "
      },
      {
        "line": 207,
        "text": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 229,
        "text": "【語法・注意】法律用語の `principal` は「重要人物」という一般義だけでなく、`agent` に対する特定の関係上の役割名である。`client` はサービスを受ける顧客・依頼人を広く指すが、必ずしも代理権を与える法律上の本人ではない。`the principal's agent` は「本人の代理人」であり、「校長の代理人」と決めつけない。  "
      },
      {
        "line": 240,
        "text": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 257,
        "text": "【語法・注意】舞台芸術やオーケストラ内で確立した役割名として用い、一般の「重要人物」には広げない。  "
      },
      {
        "line": 268,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 290,
        "text": "【語法・注意】刑事法の `principal` は適用される法的分類に従う役割名で、`accessory` と対比される。債務・保証関係の第一次的責任者は別の語義7である。  "
      },
      {
        "line": 301,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 328,
        "text": "【語法・注意】この語義では、`principal` は `be liable as principal` のように人・法人を指す名詞である。`principal debtor` や `principal obligor` では語義1の形容詞が `debtor`・`obligor` を修飾するため、名詞単独の構造と区別する。また、金額を指す語義3の「元金」とも区別する。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "・principally：`principal` の副詞形。  "
      },
      {
        "line": 25,
        "text": "・principalship：`principal` の名詞派生形。  "
      },
      {
        "line": 26,
        "text": "・principal-agent relationship：法律上の本人・代理人関係を表す複合表現。  "
      }
    ]
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
  "specification_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
  "source_artifact_sha256": "566785426a568ff079817e5fc120efa9cd081fc11eebe5f3170c5e6a910b890c",
  "normalized_input_sha256": "e46cf65044630559df139dcb6f12811342c46312a8c24f51c1fa2a987ebe68f8"
}
```
