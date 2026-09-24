# Independent checker handoff

Stage: `checker_passes/sense-structure`

Run this request in its own independent agent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one agent for multiple passes.

Save exactly one JSON response as `sense-structure.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
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
  "input_body_sha256": "13559d31b050882ff1d24890c8d22914c8f87e20f0ddb0e509e2a8178469bd82",
  "input_sections": {
    "core_image": [
      {
        "line": 28,
        "text": "＃コアイメージ"
      },
      {
        "line": 30,
        "text": "学習上は「確証のない段階で、ある事柄が真実かもしれないと考える」という見立てを中心にする。人の犯罪・不正を疑う用法はその具体例であり、suspicion that ... の節には別の出来事や状態も続く。人や物事を信用できず疑いの目で見る用法は、対象への不信・警戒という態度に焦点を置く。a suspicion of a smile / truth は「ごく少量・かすかな兆し」を表す形式的な比喩用法。この整理は学習上の目安で、全用法が一つの語源的意味を共有するという主張ではない。  "
      }
    ],
    "sense_structure": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 38,
        "text": "【日本語訳・定義】確証がない段階で、ある事柄が真実かもしれないと考えることを表す。人が犯罪・不正をした可能性への疑いもこの意味に含む。Oxfordは犯罪・不正の疑いでは可算・不可算の両用法を、命題の真偽については可算用法を記している。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 91,
        "text": "【日本語訳・定義】人や物事を十分に信用できず、疑いの目で見る態度を表す。ある事柄が真実かどうかについての見立てを表す語義1とは異なり、対象への不信や警戒に焦点を置く。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 119,
        "text": "【日本語訳・定義】ものがごく少量、またはかすかな兆候として感じられることを表す。通常 a suspicion of ... の形で使われる。  "
      }
    ],
    "usage_notes": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 78,
        "text": "【語法・注意】on suspicion of theft は「窃盗で有罪になった」ではなく、「窃盗をした疑いを理由に」という意味である。under suspicion も罪が確定した状態を表さない。Merriam-Webster の法律辞典は suspicion を通常、信念に至らない精神状態として説明し、reasonable suspicion の項目に関連づけている。ここでは特定の法域の法的基準を述べない。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 106,
        "text": "【語法・注意】with suspicion は、対象を信頼できるか疑って見る態度を表す。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 139,
        "text": "【語法・注意】この a suspicion of ... は「～を疑うこと」ではなく、「～がごく少量、または兆候としてわずかに感じられること」である。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・suspicious：形容詞。「疑っている、不信に思っている」、または人に疑いを起こさせる「疑わしい」。  "
      },
      {
        "line": 24,
        "text": "・suspiciously：副詞形。  "
      },
      {
        "line": 25,
        "text": "・suspiciousness：名詞形。  "
      },
      {
        "line": 26,
        "text": "・suspicion（動詞）：他動詞で「～を疑う」。Merriam-Webster では chiefly dialectal とされる。  "
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
  "source_artifact_sha256": "d44f6f1eb825f6bfcff285716c87db277e5c8ceaeff55140e230ec57726868a2",
  "normalized_input_sha256": "aea81546f7d282a1955ab433fd530241bdc6be896e4f8c5de00253202cc549b0"
}
```
