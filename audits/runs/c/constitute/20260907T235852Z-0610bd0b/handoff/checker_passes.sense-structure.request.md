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
  "input_body_sha256": "bc5fd320a4e6026bd4209c99c588e7f87029232f85f6c73b9b166ce053d5b6f1",
  "input_sections": {
    "core_image": [
      {
        "line": 31,
        "text": "＃コアイメージ"
      },
      {
        "line": 33,
        "text": "constitute の共通核は、要素・行為・組織・人を、ある全体・分類・制度・役割として成り立つ位置に据えることである。文脈によって、すでにそうであるという関係を述べる場合と、意図的・正式に成立させる行為を述べる場合がある。  "
      },
      {
        "line": 34,
        "text": "・要素を全体として成り立つ位置に据える → 「構成する、占める」（語義1）  "
      },
      {
        "line": 35,
        "text": "・行為や事実を分類として成り立つ位置に据える → 「～に当たる、～となる」（語義2）  "
      },
      {
        "line": 36,
        "text": "・組織を正式な制度として成り立つ位置に据える → 「正式に設立する、組織する」（語義3）  "
      },
      {
        "line": 37,
        "text": "・人を公的な役割として成り立つ位置に据える → 「任命する、～の資格を与える」（語義4）  "
      }
    ],
    "sense_structure": [
      {
        "line": 41,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 43,
        "text": "【日本語訳・定義】複数の人・物・部分・期間などが、集まって一つの全体を形作る、またはその全体の一定割合・重要部分を占めることを表す。基本の能動構文では、主語が構成要素、目的語がそれらによってできる全体である。意図的に組み立てる行為ではなく、部分と全体の関係を記述することが多い。  "
      },
      {
        "line": 113,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 115,
        "text": "【日本語訳・定義】行為、状況、事実、結果などが、ある分類・評価・状態の定義や成立条件を満たし、そのものと見なせることを表す。目的語には crime、breach、threat、evidence、change、problem などが来る。法律用語だけではなく一般の評価にも使うが、何がその分類に当たるかをやや改まって判断する響きがある。  "
      },
      {
        "line": 190,
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 192,
        "text": "【日本語訳・定義】組織、委員会、裁判所、政府などを、所定の手続き・権限・構成によって正式に作り、活動できる形にする。単に人を集めるだけでなく、公式の組織体として成立させる意味を持つ。設立手続きや法的効果の具体的内容は制度・法域によって異なる。  "
      },
      {
        "line": 262,
        "text": "4. 【他動詞・公式・法律】（人を役職・資格に）任命する、～の資格を与える"
      },
      {
        "line": 264,
        "text": "【日本語訳・定義】権限をもつ者・法律・公式文書などが、人を特定の職務・地位・役割に就け、その資格で行動できるようにする。現代の日常英語ではまれで、appoint や designate が普通である。  "
      }
    ],
    "usage_notes": [
      {
        "line": 41,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 78,
        "text": "【語法・注意】能動の `A, B, and C constitute X` では A・B・C が部分、X が全体である。`X consists of A, B, and C` や `X is composed of A, B, and C` では向きが逆になり、X が全体、A・B・C が部分になる。  "
      },
      {
        "line": 113,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 155,
        "text": "【語法・注意】この語義の constitute は、主語と目的語を同一の分類関係で結ぶが、文法上は目的語を取る動詞であり、通常 `constitute as a threat` のように as を挟まない。`The delay constitutes a problem.` のように直接目的語を置く。  "
      },
      {
        "line": 190,
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 227,
        "text": "【語法・注意】語義1の「部分が全体を構成している」は状態的な関係、語義3の「組織を正式に設立する」は意図的・制度的な行為である。`The members constitute the board.` は「構成員が取締役会を構成する」、`The agency constituted a board.` は「機関が取締役会を正式に設置した」となる。  "
      },
      {
        "line": 262,
        "text": "4. 【他動詞・公式・法律】（人を役職・資格に）任命する、～の資格を与える"
      },
      {
        "line": 294,
        "text": "【語法・注意】人を直接目的語にし、役職を目的格補語として置く `constitute someone treasurer` と、as句で資格を示す `constitute someone as an agent` がある。ただし、どちらも現代の一般文では非常に硬く、通常は `appoint someone treasurer`、`appoint/designate someone as an agent` とする。  "
      }
    ],
    "word_formation": [
      {
        "line": 23,
        "text": "＃語形成"
      },
      {
        "line": 25,
        "text": "`constitutes / constituted / constituting` — 三人称単数現在形・過去形／過去分詞・現在分詞。語末の無音の e を取って constituting とする。  "
      },
      {
        "line": 26,
        "text": "`constitution` — 名詞。「構成・体質」のほか、国家・組織の基本原則を定める「憲法・規約」を表す。  "
      },
      {
        "line": 27,
        "text": "`constitutional / constitutionally` — 形容詞「構成上の、体質上の、憲法上の」／副詞「体質的に、憲法上」。  "
      },
      {
        "line": 28,
        "text": "`constituent` — 名詞「構成要素、選挙区民」、形容詞「構成する」。政治の「選挙区民」は constitute の目的語ではなく、代表者を選ぶ constituency の構成員を指す。  "
      },
      {
        "line": 29,
        "text": "`reconstitute` — 動詞「再構成する、元の状態に戻す」。乾燥食品・薬剤などに液体を加えて戻す用法もある。  "
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
  "source_artifact_sha256": "64fb191f6d61ca2c5c081905e3d5190bd1799b8fd52554f3d6a5d7629ea69b23",
  "normalized_input_sha256": "0fdaf23f0c0fa63fec38d1c41fc2aa5202367dc21aec24e3334b344cf1f5f833"
}
```
