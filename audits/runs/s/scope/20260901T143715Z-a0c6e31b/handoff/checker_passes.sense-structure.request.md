# Independent checker handoff

Stage: `checker_passes/sense-structure`

Run this request in its own independent agent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one agent for multiple passes.

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
  "input_body_sha256": "3f34e03e76f478959eb828c3e94f244b289a9a6e67ca0894cfa50e8f1869002b",
  "input_sections": {
    "core_image": [
      {
        "line": 34,
        "text": "＃コアイメージ"
      },
      {
        "line": 36,
        "text": "scope の中心には、「どこまで見渡せるか、扱えるかを区切った境界」というイメージがある。対象を含める範囲にも、行動できる余地にも、名前や演算子が届く領域にも使われ、動詞ではその境界を調べたり先に定めたりする。  "
      },
      {
        "line": 38,
        "text": "・行動や発展を許す余地 → 「余地、機会」（語義1）  "
      },
      {
        "line": 39,
        "text": "・主題や活動が扱う境界 → 「範囲、対象領域」（語義2）  "
      },
      {
        "line": 40,
        "text": "・人・組織の知識や権限が届く境界 → 「能力・権限の及ぶ範囲」（語義3）  "
      },
      {
        "line": 41,
        "text": "・遠く・内部を見る器具 → 「スコープ、観察器具」（語義4）  "
      },
      {
        "line": 42,
        "text": "・量化子や修飾語が意味に及ぼす領域 → 「作用域」（語義5）  "
      },
      {
        "line": 43,
        "text": "・プログラム内で名前を参照できる領域 → 「スコープ、可視範囲」（語義6）  "
      },
      {
        "line": 44,
        "text": "・対象を見て情報を得る → 「詳しく調べる、下見する」（語義7）  "
      },
      {
        "line": 45,
        "text": "・作業の大きさや必要条件を先に見積もる → 「範囲を定める、要件を見積もる」（語義8）  "
      },
      {
        "line": 46,
        "text": "・望遠鏡・内視鏡で見る → 「スコープで観察する」（語義9）  "
      },
      {
        "line": 47,
        "text": "・器具を取り付けて見る装備にする → 「スコープを装備する」（語義10）  "
      },
      {
        "line": 49,
        "text": "語義1〜3・5・6は、対象に届く境界という共通核から現代的に理解できる。語義4・9・10は「見る器具」への短縮・転用を含むため、範囲を表す名詞・動詞と文脈で区別する。  "
      }
    ],
    "sense_structure": [
      {
        "line": 53,
        "text": "1. 【名詞・不可算】行動・発展の余地、機会、自由裁量"
      },
      {
        "line": 55,
        "text": "【日本語訳・定義】人が何かをしたり、能力を伸ばしたりするために残されている余地・機会。scope for + 名詞・動名詞 が最も定着しており、十分な余地にも、ほとんど余地がない状態にも使える。実際に成功する機会を保証する語ではなく、可能性を活かせる空間を表す。  "
      },
      {
        "line": 133,
        "text": "2. 【名詞・不可算】主題・活動・調査などが扱う範囲、対象領域"
      },
      {
        "line": 135,
        "text": "【日本語訳・定義】本、議論、調査、計画、組織の活動などに含まれる主題・対象・作業の境界。scope of 〈対象〉、within/beyond/outside the scope of 〈対象〉、broad/narrow in scope の形で、何を含め何を含めないかを示す。物理的な大きさではなく、内容・活動・影響の広がりに焦点がある。  "
      },
      {
        "line": 209,
        "text": "3. 【名詞・不可算】人・組織の能力、知識、権限が及ぶ範囲"
      },
      {
        "line": 211,
        "text": "【日本語訳・定義】人、職種、組織、制度などが知識・技能・責任・権限によって扱える範囲。語義2の「調査や計画が何を含むか」と似るが、ここでは主体側の能力・担当・許可された権限に焦点がある。my scope、the scope of the role、within/outside one's scope などで使う。  "
      },
      {
        "line": 273,
        "text": "4. 【名詞・可算】望遠鏡・内視鏡・照準器などのスコープ、観察器具"
      },
      {
        "line": 275,
        "text": "【日本語訳・定義】遠くのもの、内部、または照準対象を見るための器具を指す短縮的な名詞。文脈により telescope、microscope、endoscope、rifle scope などを指し、scope 単独で器具の種類が決まるとは限らない。医療では検査用の内視鏡、射撃では銃に取り付ける照準望遠鏡を指すことがある。  "
      },
      {
        "line": 337,
        "text": "5. 【名詞・論理学・言語学】量化子・否定・修飾語などの作用域"
      },
      {
        "line": 339,
        "text": "【日本語訳・定義】論理式や文の中で、量化子、否定、修飾語などが意味・真偽の解釈に影響を及ぼす部分。scope of a quantifier はその量化子が支配する領域を指し、文の構造によって複数の解釈が生じると scope ambiguity「作用域の曖昧性」になる。一般的な「主題の範囲」と違い、意味解釈を決める構造上の領域である。  "
      },
      {
        "line": 401,
        "text": "6. 【名詞・コンピューター】プログラム内で名前や値を参照できる範囲、実行コンテキスト"
      },
      {
        "line": 403,
        "text": "【日本語訳・定義】変数、関数、値などがプログラムのどの部分から見え、参照できるかを決める実行上の範囲・文脈。global scope、function scope、block scope、lexical scope などがあり、内側の scope が外側の scope を参照できる階層構造を持つことがある。言語ごとの規則は異なるため、scope という一般概念と各言語の実装規則を分けて理解する。  "
      },
      {
        "line": 465,
        "text": "7. 【他動詞・くだけた用法】場所・人・状況などを詳しく調べる、下見する"
      },
      {
        "line": 467,
        "text": "【日本語訳・定義】場所、人、競争相手、状況、可能性などを注意深く見て、情報を得たり評価したりする。scope something は調査対象を直接置く形、scope something/someone out は「詳しく下見する・情報を集める」という句動詞で、くだけた用法である。対象を見ただけで最終判断や実行まで済ませたことは含まない。  "
      },
      {
        "line": 534,
        "text": "8. 【他動詞・主にビジネス／技術】仕事・計画・解決策の範囲や必要条件を見積もり、定める"
      },
      {
        "line": 536,
        "text": "【日本語訳・定義】作業に着手する前に、プロジェクト、解決策、機能、要件などを調べて、必要な作業量・費用・範囲・条件を明確にする。scope the project/solution のように目的語を直接取る。scope out は同じ準備段階をより口語的に表すが、scope は計画上の境界を定義する意味が強い。  "
      },
      {
        "line": 598,
        "text": "9. 【他動詞・技術】望遠鏡・内視鏡などで見る、観察する"
      },
      {
        "line": 600,
        "text": "【日本語訳・定義】対象を望遠鏡で見たり、内視鏡・関節鏡などで体内や狭い部分を検査したりする。scope the sky、scope the knee のように直接目的語を取る。一般の「詳しく調べる」より、どの器具を使うかが文脈で明らかな技術・医療用法である。  "
      },
      {
        "line": 657,
        "text": "10. 【他動詞・技術】銃などにスコープを取り付ける、スコープ付きにする"
      },
      {
        "line": 659,
        "text": "【日本語訳・定義】銃などの器具に照準用のスコープを取り付け、スコープを使える状態にする。scope a rifle、a scoped rifle のように使う低頻度の技術用法で、語義4の器具名から品詞転換したもの。対象を調べる scope と異なり、目的語は装備される器具である。  "
      }
    ],
    "usage_notes": [
      {
        "line": 53,
        "text": "1. 【名詞・不可算】行動・発展の余地、機会、自由裁量"
      },
      {
        "line": 90,
        "text": "【語法・注意】この語義の scope は通常不可算で、×a scope for improvement とはせず plenty of scope for improvement のように使う。scope for 〈名詞〉と scope for somebody to do を区別する。前者は改善・創造性などの活動の余地、後者は特定の人が行為をする余地である。  "
      },
      {
        "line": 133,
        "text": "2. 【名詞・不可算】主題・活動・調査などが扱う範囲、対象領域"
      },
      {
        "line": 175,
        "text": "【語法・注意】scope は「範囲」でも境界線そのものではなく、何が対象に含まれるかという内容上の広がりを表す。within the scope of は「～の範囲内で」、beyond/outside the scope of は「～の対象外で」であり、単に「～の外側にある」という物理的位置には通常使わない。scope of と scope for を混同しない。前者は対象に含まれる範囲、後者は行動・改善の余地である。  "
      },
      {
        "line": 209,
        "text": "3. 【名詞・不可算】人・組織の能力、知識、権限が及ぶ範囲"
      },
      {
        "line": 246,
        "text": "【語法・注意】「能力がない」と断定するより、outside my scope は「この担当・専門範囲では扱わない」という境界の表現である。専門職について scope of practice と言う場合、実際に許される行為、資格、監督、法域は制度ごとに異なるため、単なる担当範囲と法的資格を同一視しない。  "
      },
      {
        "line": 273,
        "text": "4. 【名詞・可算】望遠鏡・内視鏡・照準器などのスコープ、観察器具"
      },
      {
        "line": 310,
        "text": "【語法・注意】この scope は語義2の「範囲」と別の名詞系統から来た短縮用法である。a scope と単数で数えられ、the scope of the report のような of 構文とは意味が異なる。under the scope は専門文脈に限られ、一般的な「詳しく検討されている」には under scrutiny や under review が自然な場合が多い。  "
      },
      {
        "line": 337,
        "text": "5. 【名詞・論理学・言語学】量化子・否定・修飾語などの作用域"
      },
      {
        "line": 374,
        "text": "【語法・注意】この語義の scope は、単に「文が扱う主題の範囲」を指すのではなく、ある要素が他の要素の解釈を支配する領域を指す。take scope over は「～について広い範囲を調べる」ではなく、論理的・意味論的な作用関係を表す。wide/narrow は物理的な幅ではなく、支配する構造上の広さである。  "
      },
      {
        "line": 401,
        "text": "6. 【名詞・コンピューター】プログラム内で名前や値を参照できる範囲、実行コンテキスト"
      },
      {
        "line": 438,
        "text": "【語法・注意】プログラミングの scope は、変数の寿命そのもの、保存場所、値の型と同じではない。scope は主に「名前をどこから参照できるか」を表し、lifetime は値が存在する期間を表す。言語によって function scope と block scope の規則や、親 scope への名前解決の仕組みは異なる。  "
      },
      {
        "line": 465,
        "text": "7. 【他動詞・くだけた用法】場所・人・状況などを詳しく調べる、下見する"
      },
      {
        "line": 507,
        "text": "【語法・注意】句動詞 scope out は、目的語が名詞なら scope out the area と scope the area out の両方が可能だが、代名詞は scope it out であり、×scope out it とはしない。scope out は「下見・情報収集」で、inspect のような正式な検査や、decide のような決定そのものを意味しない。scope somebody out は、文脈によっては相手を品定めするようなくだけた含みを持つ。  "
      },
      {
        "line": 534,
        "text": "8. 【他動詞・主にビジネス／技術】仕事・計画・解決策の範囲や必要条件を見積もり、定める"
      },
      {
        "line": 571,
        "text": "【語法・注意】scope a project は「プロジェクトを実行する」ではなく、実行前に何を含めるか、どの程度の費用・時間が必要かを定めること。define は概念や境界を明確にする一般語、estimate は数量・費用を見積もる語であり、scope は両者を含む計画上の範囲決めである。scope creep は、この合意済みの範囲が管理されないまま広がる現象を指す。  "
      },
      {
        "line": 598,
        "text": "9. 【他動詞・技術】望遠鏡・内視鏡などで見る、観察する"
      },
      {
        "line": 630,
        "text": "【語法・注意】この用法の scope は「器具を使って観察・検査する」という動作であり、単に examine と同じ範囲の一般語ではない。be scoped は「スコープを使った検査を受ける」で、受動態の主語が自分で観察するという意味にはならない。medical context では、検査の種類・麻酔・結果などをこの語だけから推測しない。  "
      },
      {
        "line": 657,
        "text": "10. 【他動詞・技術】銃などにスコープを取り付ける、スコープ付きにする"
      },
      {
        "line": 689,
        "text": "【語法・注意】scope a rifle の目的語はスコープを取り付けられる器具であり、scope the rifle のように「ライフルを詳しく見る」とは通常解釈しない。装備の調整・使用・安全性は別の概念で、scope という動詞だけから照準の正確さや使用結果を推測しない。  "
      }
    ],
    "word_formation": [
      {
        "line": 23,
        "text": "＃語形成"
      },
      {
        "line": 25,
        "text": "・scopes：scope の複数形。複数の範囲、作用域、または複数の観察器具を表す。  "
      },
      {
        "line": 26,
        "text": "・scoped：scope の過去形・過去分詞。調査した、作業範囲を定めた、またはスコープを装備した。  "
      },
      {
        "line": 27,
        "text": "・scoping：scope の -ing形。調査・見積もり・作業範囲の定義を表し、scoping study「予備的な範囲調査」のようにも使う。  "
      },
      {
        "line": 28,
        "text": "・scope out：対象を詳しく調べる、可能性・必要条件を見積もる。out は分離できず、scope something out / scope out something の両方があるが、代名詞は scope it out の位置に置く。  "
      },
      {
        "line": 29,
        "text": "・scope creep：プロジェクト開始後に、合意した範囲へ要求や作業が少しずつ追加されること。単なる scope の拡大ではなく、管理上望ましくない含みを持つ。  "
      },
      {
        "line": 30,
        "text": "・scope of practice：資格を持つ専門職が行える業務の範囲。制度ごとの要件は職種・法域で異なり、一般名詞 scope の意味から手続きまで推測しない。  "
      },
      {
        "line": 31,
        "text": "・scope statement：プロジェクトで、含める作業・成果物・境界を記した文書または記述。  "
      },
      {
        "line": 32,
        "text": "・-scope：telescope、microscope、periscope、endoscope などで「見る・観察する器具」を表す結合形。単独名詞 scope の「範囲」とは系統・意味を分けて覚える。  "
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
