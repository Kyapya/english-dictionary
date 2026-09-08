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
  "input_body_sha256": "a79a267d48a57dc1c95b4c79fa1496950e4ca751f098fd6d46c4a89b6afdfcd2",
  "input_sections": {
    "core_image": [
      {
        "line": 26,
        "text": "＃コアイメージ"
      },
      {
        "line": 28,
        "text": "`parliament` の中心は、「代表者が集まり、公的事項を審議して決定する制度的な会議体」である。そこから、その継続的な立法機関そのものと、一度の選挙によって構成され次の選挙まで活動する特定期の会議体を表す。  "
      },
      {
        "line": 29,
        "text": "・制度として存在し、法律や政策を審議する代表者の機関 → 「議会、国会」（語義1）  "
      },
      {
        "line": 30,
        "text": "・ある選挙後に成立し、次の選挙まで存続する具体的な構成・期間 → 「一議会期、特定期の議会」（語義2）  "
      }
    ],
    "sense_structure": [
      {
        "line": 34,
        "text": "1. 【名詞・可算／固有名詞的用法】議会、国会；議会を構成する議員たち"
      },
      {
        "line": 36,
        "text": "【日本語訳・定義】国または地域の代表者が集まり、法律の制定・改正、政策や予算の審議、政府の監督などを行う制度的な機関、またはその構成員全体を指す。国によって正式名称・構成・権限が異なるため、日本語訳は文脈に応じて「議会」「国会」などとなる。特定国の正式または慣用的な機関名として用いる場合は `Parliament` と大文字で始めることがある。  "
      },
      {
        "line": 118,
        "text": "2. 【名詞・可算】一議会期、ある選挙で成立した特定期の議会"
      },
      {
        "line": 120,
        "text": "【日本語訳・定義】一度の総選挙後に成立した議会が、次の選挙や解散まで同じ制度上の単位として存続する期間、またはその期間に活動する特定の議員構成を指す。個々の会議や一日ごとの開会ではなく、複数の `session` を含み得る、より大きな単位である。  "
      }
    ],
    "usage_notes": [
      {
        "line": 34,
        "text": "1. 【名詞・可算／固有名詞的用法】議会、国会；議会を構成する議員たち"
      },
      {
        "line": 86,
        "text": "【語法・注意】`parliament` は第一に立法・審議を行う機関またはその議員集団を指し、`government`「政府・政権」と同じではない。議院内閣制では両者の構成員が重なることがあるが、制度上の役割は区別される。また、建物を明示するなら `parliament building`、イギリスのウェストミンスター宮殿なら `the Houses of Parliament` とするのが明確であり、`parliament` 自体を常に「国会議事堂」と訳してはならない。国名によって正式名称が異なり、日本の国会は通常 `the Diet` または `the National Diet`、アメリカ合衆国の連邦議会は `Congress` と呼ぶ。  "
      },
      {
        "line": 118,
        "text": "2. 【名詞・可算】一議会期、ある選挙で成立した特定期の議会"
      },
      {
        "line": 150,
        "text": "【語法・注意】語義1の制度としての `parliament` は選挙を越えて継続し得るが、この語義は選挙ごとに成立する具体的な構成・期間を数える。`parliament` と `session` も同じではない。イギリスでは一つの `Parliament` が通常、複数の約1年単位の `session` に分かれ、`prorogation` は一つの会期を終えるのに対し、`dissolution` はその議会期自体を終える。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "・parliamentary：`parliament` に接尾辞 `-ary` が付いた形容詞。「議会の」「議会制の」のほか、`parliamentary procedure` では「議事手続きの」を表す。  "
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
  "source_artifact_sha256": "8c3d3e8bc2bb85f93e6c7bd3c0bd855e1fcdc3416d4e6aac306d4c0d2c2683e4",
  "normalized_input_sha256": "9bc8f8134be97f366dfb7eeedcd6a8211a3e9ba53d5617627f94fd33aaaeeb3d"
}
```
