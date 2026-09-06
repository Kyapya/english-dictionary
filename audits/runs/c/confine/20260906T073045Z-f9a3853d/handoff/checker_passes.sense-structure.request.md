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
  "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
  "input_sections": {
    "core_image": [
      {
        "line": 28,
        "text": "＃コアイメージ"
      },
      {
        "line": 30,
        "text": "人・物・活動・内容などを、ある境界の内側にとどめ、外へ出たり広がったりしないようにする。形容詞ではその結果の状態や窮屈さを、名詞では境界そのものを表す。  "
      },
      {
        "line": 32,
        "text": "・対象の範囲を一定の境界内にとどめる → 「～を…に限る、限定する」（語義1）  "
      },
      {
        "line": 33,
        "text": "・人や動物を一定の場所から出られなくする → 「閉じ込める、拘束する」（語義2）  "
      },
      {
        "line": 34,
        "text": "・病気やけがで生活場所を狭い範囲にとどめる → 「～を寝床・自宅などにとどめる」（語義3）  "
      },
      {
        "line": 35,
        "text": "・空間や区域が狭い境界内に収まった状態 → 「狭く囲まれた、限られた」（語義4）  "
      },
      {
        "line": 36,
        "text": "・内外を分けて範囲を画する境界 → 「境界、範囲、領域」（語義5）  "
      }
    ],
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】話題、活動、作業、影響、現象などが及ぶ範囲を、特定の対象・場所・期間・分野などの内側に限定する。対象がすでにその範囲に収まっていることを述べる受動形と、話し手が意識的に扱う範囲を絞る能動形・再帰形の両方がよく使われる。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 120,
        "text": "【日本語訳・定義】人や動物を、部屋、施設、囲い、刑務所などの外へ自由に出られないようにする。物理的な障壁、命令、拘禁などによる移動の制限を表し、本人の自由意思で滞在している場合には通常使わない。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 193,
        "text": "【日本語訳・定義】病気、けが、身体状態などが原因で、人がベッド、自宅、病室など限られた場所から動けない、または外出できない状態にする。原因を主語にする能動文も可能だが、本人を主語にした be confined to が特に多い。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 250,
        "text": "【日本語訳・定義】confined の形で、空間や区域が壁や境界に囲まれて狭い、または内部で動ける余地が少ないことを表す。単に面積が小さいだけでなく、閉鎖性や動きにくさを含みやすい。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 323,
        "text": "【日本語訳・定義】通常 confines の形で、場所・組織・分野などの外縁をなす境界、またはその境界に囲まれた内部の領域を表す。現代の一般的な文章では単数形 confine より複数形 confines が圧倒的に普通である。  "
      }
    ],
    "usage_notes": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 77,
        "text": "【語法・注意】基本形は confine A to B であり、to の後ろには名詞または動名詞を置く。×confine A in doing B のように範囲を示す前置詞を機械的に in に替えない。場所の内部へ物理的に閉じ込める語義2では confine someone in a cell のように in も使う。confine oneself to は「自分を物理的に閉じ込める」ではなく、通常「話題・活動を自分で限定する」という再帰構文である。受動形 be confined to は、否定や mainly、largely などと結び付き、「～だけに限られる／限られない」を表しやすい。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 150,
        "text": "【語法・注意】この語義では能動形も可能だが、拘束される側を主語にした be confined in/to が多い。in は容器・部屋・施設の「内部」を、to は移動可能な「範囲」を示す。imprison は人を刑務所に入れる法的・物理的な拘禁に焦点があり、動物や一時的な行動制限には使いにくい。confine は刑罰に限らず、命令や安全上の理由による拘束にも使える。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 223,
        "text": "【語法・注意】be confined to a wheelchair は従来から見られる表現だが、車いすを人を閉じ込める物として否定的に描くため、不快・不適切と受け取られることがある。単に移動手段を述べるなら use a wheelchair または be a wheelchair user を用いる。be confined to bed は病気などで起きられない状態を表し、単にベッドで休む choose to stay in bed とは異なる。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 280,
        "text": "【語法・注意】confined space は一般には狭く囲まれた空間を表すが、労働安全上の専門用語では法域や制度ごとに定義・要件があるため、小さい部屋をすべて専門上の confined space と断定しない。be confined to 〈場所・範囲〉は動詞 confine の受動形で「～に限定・拘束されている」、a confined space は形容詞 confined が名詞を修飾して「狭く囲まれた空間」である。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 353,
        "text": "【語法・注意】名詞では動詞と強勢位置が異なる。現代英語では通常 the confines of ... の複数形で使い、単数の a confine はまれである。confines は「境界線」そのものと「境界に囲まれた領域」の両方を表し得るため、within the confines of the park は通常「公園の区域内」、beyond the confines of the law は比喩的に「法の枠を越えて」と理解する。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・confinement（名詞）— 閉じ込めること、拘禁、行動範囲が限られた状態。文脈によって物理的拘束、病気による外出不能、限定された環境などを表す。  "
      },
      {
        "line": 24,
        "text": "・confined（形容詞）— 狭く囲まれた、限られた。単なる過去分詞としての受動用法と、confined space のような形容詞用法がある。  "
      },
      {
        "line": 25,
        "text": "・confining（形容詞）— 自由な動きや活動を妨げる、窮屈な。物理的な狭さだけでなく、服装・役割・生活環境などの制約にも使う。  "
      },
      {
        "line": 26,
        "text": "・unconfined（形容詞）— 閉じ込められていない、境界内に制限されていない。一般語としては limited や restricted ほど頻繁ではない。  "
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
  "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
  "normalized_input_sha256": "2d398489b2dd867f315901b1bed47c01206aa1939f532fb1f82c0dcea08e5c3e"
}
```
