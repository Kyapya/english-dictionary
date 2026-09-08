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
  "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
  "input_sections": {
    "core_image": [
      {
        "line": 29,
        "text": "＃コアイメージ"
      },
      {
        "line": 31,
        "text": "constitute の共通核は、要素・行為・組織・人を、ある全体・分類・制度・役割として成り立つ位置に据えることである。文脈によって、すでにそうであるという関係を述べる場合と、意図的・正式に成立させる行為を述べる場合がある。  "
      },
      {
        "line": 32,
        "text": "・要素を全体として成り立つ位置に据える → 「構成する、占める」（語義1）  "
      },
      {
        "line": 33,
        "text": "・行為や事実を分類として成り立つ位置に据える → 「～に当たる、～となる」（語義2）  "
      },
      {
        "line": 34,
        "text": "・組織を正式な制度として成り立つ位置に据える → 「正式に設立する、組織する」（語義3）  "
      },
      {
        "line": 35,
        "text": "・人を公的な役割として成り立つ位置に据える → 「正式に任命・指定する」（語義4）  "
      }
    ],
    "sense_structure": [
      {
        "line": 39,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 41,
        "text": "【日本語訳・定義】一つまたは複数の人・物・部分・期間などが、一つの全体を形作る、またはその全体の一定割合・重要部分を占めることを表す。全体構成の能動構文では主語が構成要素、目的語がそれらによってできる全体である。一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は of 句に現れる。意図的に組み立てる行為ではなく、部分と全体の関係を記述することが多い。  "
      },
      {
        "line": 111,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 113,
        "text": "【日本語訳・定義】行為、状況、事実、結果などが、ある分類・評価・状態の定義や成立条件を満たし、そのものと見なせることを表す。目的語には crime、breach、threat、evidence、change、problem などが来る。法律用語だけではなく一般の評価にも使うが、何がその分類に当たるかをやや改まって判断する響きがある。  "
      },
      {
        "line": 188,
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 190,
        "text": "【日本語訳・定義】組織、委員会、裁判所、政府などを正式に形成・設置し、公式の組織体として成立させることを表す。制度や文脈によって所定の手続きや権限付与を伴うことはあるが、constitute という語だけで法的有効性や実際の活動可能性まで一律に保証するわけではない。  "
      },
      {
        "line": 253,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 255,
        "text": "【日本語訳・定義】権限をもつ者・法律・公式文書などが、人を特定の役職・地位・役割に正式に任命・指定することを表す。任命の法的有効性、付与される権限、その立場で行動できる範囲は、該当する文書・制度・法域によって決まる。  "
      }
    ],
    "usage_notes": [
      {
        "line": 39,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 76,
        "text": "【語法・注意】能動の `A, B, and C constitute X` では A・B・C が部分、X が全体である。`X consists of A, B, and C` や `X is composed of A, B, and C` では向きが逆になり、X が全体、A・B・C が部分になる。  "
      },
      {
        "line": 111,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 153,
        "text": "【語法・注意】この語義の constitute は、主語と目的語を同一の分類関係で結ぶが、文法上は目的語を取る動詞であり、通常 `constitute as a threat` のように as を挟まない。`The delay constitutes a problem.` のように直接目的語を置く。  "
      },
      {
        "line": 188,
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 225,
        "text": "【語法・注意】語義1の「部分が全体を構成している」は状態的な関係、語義3の「組織を正式に設立する」は意図的・制度的な行為である。`The members constitute the board.` は「構成員が取締役会を構成する」、`The agency constituted a board.` は「機関が取締役会を正式に設置した」となる。  "
      },
      {
        "line": 253,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 280,
        "text": "【語法・注意】人を直接目的語にし、役職を目的格補語として置く `constitute someone treasurer` のような形で使う。現代の一般文では非常に硬いため、通常は `appoint someone treasurer` などとする。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "`constitution` — 名詞。「構成・体質」のほか、国家・組織の基本原則を定める「憲法・規約」を表す。  "
      },
      {
        "line": 25,
        "text": "`constitutional / constitutionally` — 形容詞「構成上の、体質上の、憲法上の」／副詞「体質的に、憲法上」。  "
      },
      {
        "line": 26,
        "text": "`constituent` — 名詞「構成要素、選挙区民」、形容詞「構成する」。政治の「選挙区民」は constitute の目的語ではなく、代表者を選ぶ constituency の構成員を指す。  "
      },
      {
        "line": 27,
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
  "source_artifact_sha256": "f98ceb46d53d98a15da050b7cf90ea946c481b3b4bfa6a28e16261031574c94b",
  "normalized_input_sha256": "cb1e0a8a3e9c8513bfda57bdf7bb58e2d1187a318c8c56fd7caa5706cbec25b7"
}
```
