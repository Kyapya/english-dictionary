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
  "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
  "input_sections": {
    "core_image": [],
    "sense_structure": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 32,
        "text": "【日本語訳・定義】政策・決定・主張・作品・発言・人物などが、社会全体または特定の集団の中で、強い意見の対立、批判、反対を引き起こしていることを表す。事実として真偽が決まっていないことを必ずしも含まず、悪い、違法、意図的に挑発的だという意味でもない。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 158,
        "text": "【日本語訳・定義】人が性格や態度の傾向として、議論を好んだり、既存の立場に反論して対立を生みやすかったりすることを表す。辞書に記載される低頻度の語義で、現代の controversial person は通常、語義1の「論争の的となっている人物」と解釈される。  "
      }
    ],
    "usage_notes": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 87,
        "text": "【語法・注意】対象を主語にした be controversial は「その対象が論争の的だ」という意味で、必ずしも対象自身が議論を仕掛けるわけではない。人物についても通常は「評価が割れている人物」の意味であり、「論争を好む人」という性向を言いたいときは語義2を確認する。highly は対立の強さ、widely は論争が広い範囲に及ぶことを示す。controversial を「間違った」「受け入れられない」と自動的に訳さず、何が誰の間で争われているかを among/within 句や文脈で補う。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 188,
        "text": "【語法・注意】この語義では controversial が人の性向を直接表すが、現代の「論争の的となる人物」という普通の解釈と形が同じなので、文脈で区別する必要がある。a controversial politician は通常語義1であり、気質を明示する temperament、manner、by temperament などがあって初めて語義2に近づく。意見が割れているだけなら語義1、本人が反論・対立を好むことまで言うなら語義2である。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・controversy：名詞。「論争、論争点、物議」。controversial と同じ語族の中心語で、public controversy のように使う。  "
      },
      {
        "line": 24,
        "text": "・controversially：副詞。「物議を醸す形で、論争を呼ぶことに」。文全体や発言・判断の仕方を修飾する。  "
      },
      {
        "line": 25,
        "text": "・controversialist：名詞。「論争家、論争に加わる人」。人の性向または論争上の立場を指す硬めの語。  "
      },
      {
        "line": 26,
        "text": "・controvert：動詞。「反論する、論駁する」。controversial と意味は近いが、現代英語では controversial の直接の活用形ではなく、別の動詞として扱う。  "
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
  "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
  "normalized_input_sha256": "ab0cd927622ac8b16615d9a6c156bd064a1138c9631add75fe3ffc00d9fec4c8"
}
```
