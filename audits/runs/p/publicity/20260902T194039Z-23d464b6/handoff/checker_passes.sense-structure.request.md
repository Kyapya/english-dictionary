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
  "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
  "input_sections": {
    "core_image": [],
    "sense_structure": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 32,
        "text": "【日本語訳・定義】人・企業・作品・出来事などが、新聞、テレビなどのメディアを通じて世間から受ける注目や報道上の露出。好意的とは限らず、good/bad/negative/unwanted publicity のように評価を添えられる。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 103,
        "text": "【日本語訳・定義】人、商品、作品、行事、主張などに世間の関心を集めるために行う広報・宣伝活動。広告に限らず、情報提供などの広報手段を含み得る。ここでは世間の注目を集める側の活動・手段に焦点を置く。  "
      }
    ],
    "usage_notes": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 67,
        "text": "【語法・注意】現代の一般用法ではこの語義の publicity は通常不可算で、a publicity や publicities は一般に避け、a lot of publicity、the publicity surrounding the case のように使う。publicity は注目・報道を表し、好評や長期的な名声を必ず含むわけではない。good/bad/negative/unwanted publicity のように評価を添えられる。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 133,
        "text": "【語法・注意】この語義でも publicity は通常不可算で、a publicity campaign、a publicity stunt のように、数えられるのは campaign や stunt などの具体的な活動である。the publicity for the film は映画の宣伝・広報活動を指し得るが、文脈によっては映画が受ける注目・報道も指す。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・publicist：publicity を作り、扱い、広める仕事をする人。映画、作家、芸能人、企業などの広報担当者を指す。  "
      },
      {
        "line": 24,
        "text": "・publicity campaign：商品、作品、行事、主張などに注目を集めるための宣伝・広報キャンペーン。  "
      },
      {
        "line": 25,
        "text": "・publicity material：宣伝・広報用の資料。  "
      },
      {
        "line": 26,
        "text": "・publicity stunt：世間の注目を集めるために意図して行う行為・仕掛け。話題作りの含みを持つ。  "
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
