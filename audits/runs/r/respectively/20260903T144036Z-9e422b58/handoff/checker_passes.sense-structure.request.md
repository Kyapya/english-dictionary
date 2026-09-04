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
  "input_body_sha256": "26cb15323105a5f53191ab8bffe12e1890ef2bf89d7587a1d12e97da3e56c157",
  "input_sections": {
    "core_image": [],
    "sense_structure": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 33,
        "text": "【日本語訳・定義】2つ以上の人・物・項目のリストと、それらに対応する同数の結果、性質、数値、行為などを示し、1番目同士、2番目同士というように提示された順番で1対1に対応させることを表す。日本語の「それぞれ」に相当するが、単に別々であるだけでなく、対応する項目の順序を指定する点が重要である。  "
      }
    ],
    "usage_notes": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 78,
        "text": "【語法・注意】respectively は、通常、先に示した2つ以上の項目と、後から示す同数の対応項目を伴う。The two samples weighed 8 and 11 grams, respectively. なら、先に挙げた第1試料が8グラム、第2試料が11グラムという対応である。項目数や順番から対応関係が明確でない場合は、各対応を明示して書き直す。  "
      }
    ],
    "word_formation": [
      {
        "line": 23,
        "text": "＃語形成"
      },
      {
        "line": 25,
        "text": "・respective + -ly → respectively：形容詞 respective「それぞれの、各自の」に副詞接尾辞 -ly が付いた形。並列する項目を順番どおりに対応づける。  "
      },
      {
        "line": 26,
        "text": "・respective：形容詞「それぞれの、各自の」。their respective roles「それぞれの役割」のように名詞を修飾し、対応する複数の名詞句を必ずしも同時に並べるとは限らない。これは respectively の別品詞の語義ではなく、respectively がそこから作られた基底形である。  "
      },
      {
        "line": 27,
        "text": "・respectfully：形容詞 respectful「礼儀正しい、敬意を示す」に -ly が付いた副詞。「謹んで、失礼ながら」の意味で、respectively とは綴りの一部が似るだけで用法が異なる。  "
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
  }
}
```
