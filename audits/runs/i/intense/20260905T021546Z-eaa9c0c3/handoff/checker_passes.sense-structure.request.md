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
  "input_body_sha256": "d9de6fa1c329e56869587ad1d22ba4bb95aba79b2d19d36eb494ea69d91b5bbf",
  "input_sections": {
    "core_image": [
      {
        "line": 33,
        "text": "＃コアイメージ"
      },
      {
        "line": 35,
        "text": "程度・強度・感情の強さが非常に高く、対象によっては大きな力・緊張・集中を伴う状態。  "
      },
      {
        "line": 37,
        "text": "・対象の程度・感覚・感情が非常に高い → 「強烈な、非常に強い」（語義1）  "
      },
      {
        "line": 38,
        "text": "・活動・競争・議論・努力などの強度や負荷が非常に高い → 「激しい、集中的な」（語義2）  "
      },
      {
        "line": 39,
        "text": "・人・表情・会話・関係に強い感情や張り詰めた印象が現れる → 「真剣で感情の強い、張り詰めた」（語義3）  "
      }
    ],
    "sense_structure": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 45,
        "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、光、色、関心、圧力などの程度・強度が極端に高いこと。集中や物理的な圧力を必ず含むわけではなく、intense pleasure「非常に強い喜び」のように好ましい対象にも使う。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 158,
        "text": "【日本語訳・定義】活動、競争、議論、努力、訓練などの強度・激しさ・負荷・緊張が非常に高いこと。短期間に活動が集中する文脈もあるが、短期間であることや参加者の主観的な負荷は必要条件ではない。  "
      },
      {
        "line": 265,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 267,
        "text": "【日本語訳・定義】人、視線、表情、会話、関係などが、非常に強い感情、意見、考え、目的意識を示すこと。真剣で集中しているという肯定的な意味にも、重い・圧が強い・感情的に負担が大きいという否定的な評価にもなり得る。  "
      }
    ],
    "usage_notes": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 87,
        "text": "【語法・注意】intense は単純な総量・大きさより、程度や強度を表す。雨では heavy rain が雨量の多さの通常表現だが、intense rain/rainfall は降り方の強さ・降水率を表し得る。intense pain/heat/interest のように、身体感覚・環境・感情のいずれにも使えるが、強さの対象を文脈から明確にする。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 203,
        "text": "【語法・注意】intense と intensive は、どちらも training、activity、effort などを修飾できる。intense は活動・体験の強度や厳しさに、intensive は短期間に内容や活動を集中的に投入する課程・計画の性質に傾く。ただし境界は絶対ではなく、期間や主観／客観だけで機械的に区別しない。  "
      },
      {
        "line": 265,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 307,
        "text": "【語法・注意】人に intense を使う場合は、単に serious「真面目な」や focused「集中した」と同じではない。強い感情や意見が外に表れ、相手に強い存在感・圧力を感じさせる含みがある。褒め言葉として passionate「情熱的な」に近くなることもあれば、too intense のように「重い、付き合うのが大変」という評価になることもある。an intense look は必ず怒りを意味せず、強い集中や関心だけでも成立する。会話では、意見の対立や交渉の激しさなら語義2、個人的な感情や重大な関係の問題なら語義3として読むことが多い。  "
      }
    ],
    "word_formation": [
      {
        "line": 25,
        "text": "＃語形成"
      },
      {
        "line": 27,
        "text": "・intensity（名詞）— 強度、激しさ。  "
      },
      {
        "line": 28,
        "text": "・intensify（動詞）— 強まる、強める。自動詞・他動詞の両方で使う。  "
      },
      {
        "line": 29,
        "text": "・intensely（副詞）— 非常に、強く、極めて。  "
      },
      {
        "line": 30,
        "text": "・intensive（形容詞）— 集中的な、徹底的な。intense と重なる場合もあるが、短期間に内容や活動を集中的に投入する課程・計画を表しやすい。  "
      },
      {
        "line": 31,
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
