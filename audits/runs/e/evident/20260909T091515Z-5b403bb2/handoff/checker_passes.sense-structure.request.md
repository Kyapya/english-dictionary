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
  "input_body_sha256": "7daa0d416ecef06000548e2f59c08bd4394750574e23f19e24855a4a6339257a",
  "input_sections": {
    "core_image": [],
    "sense_structure": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 32,
        "text": "【日本語訳・定義】見える特徴、行動、データ、状況などから、ある事実・状態・感情・評価を容易に認識または理解できることを表す。観察した人にとって明白だという意味であり、語そのものが論理的な証明や絶対的な確実性まで保証するわけではない。  "
      }
    ],
    "usage_notes": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 82,
        "text": "【語法・注意】`evident to someone` は「誰にとって明らかか」、`evident from something` は「何を根拠に明らかか」、`evident in something` は「どこに表れているか」を示す。`evident that ...` のように内容を続ける場合は、通常 `It is evident that ...` と形式主語 it を置く。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "・evidently：副詞。「明らかに、見たところ」。文全体を修飾して「どうやら、伝えられるところでは」のように使うこともある。  "
      },
      {
        "line": 25,
        "text": "・self-evident：複合形容詞。「証明や説明を必要としないほど明らかな、自明の」。  "
      },
      {
        "line": 26,
        "text": "・evidence：名詞・動詞。evident と同じ語源系統に属し、名詞では「証拠」、動詞では「証拠を示す」を表す。現代英語で evident に単純に接尾辞を付けた派生語ではない。  "
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
  "source_artifact_sha256": "30b66db08f75dd69b45d2c04e3c7e49edce013c046dafbcd965f201c1691195c",
  "normalized_input_sha256": "20c9ab2ad32d698573629c73070ea9654c2a22d8998e12300014c2edb13e9638"
}
```
