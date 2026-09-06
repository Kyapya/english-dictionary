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
  "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
  "input_sections": {
    "core_image": [
      {
        "line": 30,
        "text": "＃コアイメージ"
      },
      {
        "line": 32,
        "text": "程度・力・エネルギー・感情の強度や度合いが非常に高い。対象により、経験される強さ、活動の負荷、または人・視線・関係に表れる強い感情として現れる。  "
      },
      {
        "line": 34,
        "text": "・対象の程度・感覚・感情の強度が非常に高い → 「強烈な、非常に強い」（語義1）  "
      },
      {
        "line": 35,
        "text": "・活動や行動の強度・エネルギー・努力・緊張や負荷が非常に高い → 「激しい、活動量の多い」（語義2）  "
      },
      {
        "line": 36,
        "text": "・人・視線・表情・関係に強い感情や態度が表れる／強い結びつきがある → 「感情や態度の強い、張り詰めた」（語義3）  "
      }
    ],
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、色、関心、圧力などの程度・強度が非常に高いこと。intense pleasure「非常に強い喜び」のように、好ましい対象にも使う。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 111,
        "text": "【日本語訳・定義】活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 158,
        "text": "【日本語訳・定義】人・視線・表情・関係などについて、強い感情や意見が表れる、強く感じられる、または強い感情的な結びつきがあること。人・表情の表出、人物への評価、関係の情緒的な強さを区別する。  "
      }
    ],
    "usage_notes": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 84,
        "text": "【語法・注意】intense は感情、感覚、熱、色、関心、圧力など、強さの対象を表す名詞と結びつく。intense pleasure のような好ましい対象にも、intense pain や intense anger のような好ましくない対象にも使える。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 131,
        "text": "【語法・注意】intense は強度・力・緊張・感情が高いことを表し、intensive は限られた期間・範囲に活動や資源を集中投入することを表す傾向がある。活動用法では重なる場合があり、感情性・客観性だけを決め手にしない。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 183,
        "text": "【語法・注意】人への用法は強い感情や態度を持つという評価で、必ず外に表出するとは限らない。視線・表情では集中・鋭さ・感情の表れ、relationship では情緒的な結びつきや相互作用の強さを表す。  "
      }
    ],
    "word_formation": [
      {
        "line": 23,
        "text": "＃語形成"
      },
      {
        "line": 25,
        "text": "・intensity（名詞）— 強度、激しさ。  "
      },
      {
        "line": 26,
        "text": "・intensify（動詞）— 強まる、強める。自動詞・他動詞の両方で使う。  "
      },
      {
        "line": 27,
        "text": "・intensive（形容詞）— 集中的な、徹底的な。限られた期間・範囲に活動や資源を集中投入することを表す。intense と活動用法で重なる場合があるが、intense は強度・力・緊張・感情の高さに、intensive は集中投入の範囲・期間に焦点を置きやすい。  "
      },
      {
        "line": 28,
        "text": "・intensification（名詞）— 強化、激化。  "
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
