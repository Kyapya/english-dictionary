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
  "input_body_sha256": "3a1ecd39179a54df37a738e19b1b01cfb3f4fc1ccfad52e3eed9dcbf378473a7",
  "input_sections": {
    "core_image": [
      {
        "line": 30,
        "text": "＃コアイメージ"
      },
      {
        "line": 32,
        "text": "程度・力・エネルギー・感情の強度や度合いが非常に高い。活動や行動では、その高強度が活動量・速度・忙しさ・負荷の大きさとして現れる。人・視線・表情・関係では、強い感情や態度、鋭さ、または強い相互作用として現れる。  "
      },
      {
        "line": 34,
        "text": "・対象の程度・感覚・感情の強度が非常に高い → 「強烈な、非常に強い」（語義1）  "
      },
      {
        "line": 35,
        "text": "・活動や行動の強度・活動量・速度・忙しさ・負荷が非常に高い → 「激しい、活動量の多い」（語義2）  "
      },
      {
        "line": 36,
        "text": "・人が強い感情や態度を持つ／そうした印象を与える → 「感情や態度の強い」（語義3）  "
      },
      {
        "line": 37,
        "text": "・視線・表情に鋭さや強い感情が感じられる → 「鋭い、強い」（語義3）  "
      },
      {
        "line": 38,
        "text": "・関係の感情的な結びつきや相互作用が強い → 「張り詰めた、濃密な」（語義3）  "
      }
    ],
    "sense_structure": [
      {
        "line": 42,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 44,
        "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、色、関心、圧力などの程度・強度が非常に高いこと。intense pleasure「非常に強い喜び」のように、好ましい対象にも使う。  "
      },
      {
        "line": 111,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 113,
        "text": "【日本語訳・定義】活動・競争・議論・訓練などが高い強度で行われ、活動量・速度・忙しさ・負荷が大きいこと。強い努力や緊張を伴う場合もあるが、それらは必須ではない。短期集中を伴う場合にも使うが、短期間であることは必須ではない。  "
      },
      {
        "line": 160,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 162,
        "text": "【日本語訳・定義】人については強い感情や態度を持つ、またはそうした印象を与えること、視線や表情については集中・鋭さ・強い感情が感じられること、関係については情緒的な結びつきや相互作用が強いことを表す。関係は緊張・衝突・不安定さを伴う場合もある。  "
      }
    ],
    "usage_notes": [
      {
        "line": 42,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 86,
        "text": "【語法・注意】intense は感情、感覚、熱、色、関心、圧力など、強さの対象を表す名詞と結びつく。intense colour/blue では色の鮮やかさ・彩度、intense scrutiny では精査・吟味の厳しさも表す。extreme と重なる場合があるが、extreme は通常の範囲や限界からの逸脱、intense は経験される強さ・圧・力の高さに焦点を置きやすい。intense pleasure のような好ましい対象にも、intense pain や intense anger のような好ましくない対象にも使える。類義語欄の頻度スコアも、コーパス全体の頻度と辞書情報を参照した編集上の目安であり、各語義の厳密な順位ではない。  "
      },
      {
        "line": 111,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 135,
        "text": "【語法・注意】intense は活動の強度・活動量・速度・忙しさ・負荷が高いことを表し、intensive は活動・訓練の集中度・密度・徹底性を表す傾向がある。intensive に期間・範囲の限定が伴うことは多いが必須ではなく、両語は活動用法で重なる場合がある。感情性・客観性だけを決め手にしない。類義語欄の頻度スコアは、コーパス全体の頻度と辞書情報を参照した編集上の目安である。  "
      },
      {
        "line": 160,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 189,
        "text": "【語法・注意】人への用法は強い感情や態度を持つ、またはそうした印象を与えるという評価で、必ず外に表出するとは限らない。視線・表情では集中・鋭さ・感情の表れ、relationship では情緒的な結びつきや相互作用の強さを表し、緊張・衝突・不安定さも含み得る。類義語欄の頻度スコアは、コーパス全体の頻度と辞書情報を参照した編集上の目安である。  "
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
        "text": "・intensive（形容詞）— 集中的な、徹底的な。活動・訓練などの集中度・密度・徹底性が高いことを表し、限られた期間・範囲に集中する傾向もある。intense と活動用法で重なる場合があるが、intense は高い強度・活動量・速度・負荷などに、intensive は集中度・密度・徹底性に焦点を置きやすい。  "
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
