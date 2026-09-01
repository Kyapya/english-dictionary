# Independent checker handoff

Stage: `checker_passes/qualification`

Run this request in its own independent agent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one agent for multiple passes.

Save exactly one JSON response as `checker_passes.qualification.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_qualification_v6

## 目的

地域・レジスター・頻度・専門制度の限定と、絶対表現の適用範囲を検査する。

## 担当タクソノミー分類

- `regional_qualification`
- `absolute_scope_counterexample`
- `technical_terminology_conventionality`

## 検査ルール

- 米英差・地域差は綴りや発音だけでなく、語義、構文、頻度、自然さ、法域・制度の範囲を確認する。一地域の資料を英語全体へ一般化しない。
- 頻度は英語全体での遭遇頻度として判定し、同一見出し語内の相対順位や特定領域内だけの頻度を使わない。
- 高頻度の主要品詞・主要構文を低頻度の古語・地域語・専門語より先に置き、説明量も優先する。項目数の多さで主要用法の欠落を相殺しない。
- 「必ず」「常に」「最低限」「のみ」「できない」「人なら／物なら」等は、否定、比較、程度表現、別フレームによる反例・打ち消し可能性を探す。傾向・含みを必須条件にしない。
- 各定義主張を、必須条件、傾向・含み、特定条件に限定されるものへ分け、主要フレームへの適用範囲を確認する。
- 法律、保険、税務、医療、資格制度等では、辞書上の語彙的意味と制度上の成立要件、手続き、当事者、対象、効果を分ける。
- 専門訳語・慣用表現を一般語の直訳で置換せず、対象法域・制度の一次資料または信頼できる専門資料で慣用性と範囲を確認する。
- 専門義ブロックの各pattern・collocation・exampleが当該専門義として明確に成立するか確認する。一般義にも同程度に読める例は専門義の中心例にしない。
- 専門・地域ラベルを語義全体へ付けたとき、ブロック内の別一般義・別法域・別レジスターが混入しないか確認する。
- 語源、年代、意味変化、地域差、頻度を根拠以上に断定しない。資料が食い違い範囲を限定できなければhold相当のfindingを返す。

## 入力として受け取るセクション

- `etymology`
- `word_formation`
- `sense_structure`
- `frequency_register`
- `usage_notes`
- `collocations_examples`

## findingの出力スキーマ

```json
{
  "taxonomy_id": "regional_qualification | absolute_scope_counterexample | technical_terminology_conventionality",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "限定不足・反例・専門慣用性の問題",
  "evidence_link_ids": [],
  "suggested_direction": "適用範囲、法域、傾向、専門訳を直す方向"
}
```


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "qualification",
  "taxonomy_ids": [
    "regional_qualification",
    "absolute_scope_counterexample",
    "technical_terminology_conventionality"
  ],
  "specification": "prompts/check_pass_qualification_v6.md",
  "input_body_sha256": "3f34e03e76f478959eb828c3e94f244b289a9a6e67ca0894cfa50e8f1869002b",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "一般名詞の scope は、イタリア語 scopo「目的、目標、対象」からラテン語 scopus、ギリシャ語 skopos「目標、見張る人、注目の対象」へさかのぼる。英語では「目指す対象」から「考えや活動が及ぶ範囲」「行動の余地」へ意味が広がった。  "
      },
      {
        "line": 21,
        "text": "視覚器具を表す scope は、telescope、microscope、endoscope などの短縮形として発達した用法で、見ることを表すギリシャ語 skopein と関係する。動詞 scope は名詞の「範囲を見積もる」用法から発達し、現代の「調べる」「作業範囲を定める」へ展開した。  "
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
    "frequency_register": [
      {
        "line": 53,
        "text": "1. 【名詞・不可算】行動・発展の余地、機会、自由裁量"
      },
      {
        "line": 57,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 59,
        "text": "【レジスター/領域】標準的な一般語。会話、仕事、教育、政策、評価で使う。scope for improvement は特に頻度が高く、やや客観的・分析的に「改善の余地」を述べる。  "
      },
      {
        "line": 133,
        "text": "2. 【名詞・不可算】主題・活動・調査などが扱う範囲、対象領域"
      },
      {
        "line": 137,
        "text": "【頻度】〈10/10〉  "
      },
      {
        "line": 139,
        "text": "【レジスター/領域】標準的な一般語。報道、学術、法律、ビジネス、政策、プロジェクト管理で非常に広く使う。scope of the investigation、scope of the project は定型性が高い。  "
      },
      {
        "line": 209,
        "text": "3. 【名詞・不可算】人・組織の能力、知識、権限が及ぶ範囲"
      },
      {
        "line": 213,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 215,
        "text": "【レジスター/領域】標準的。仕事、専門職、資格、組織運営、技術支援でよく使う。制度上の scope of practice の具体的な許可範囲は、語彙的意味とは別に各制度の資料で確認する。  "
      },
      {
        "line": 273,
        "text": "4. 【名詞・可算】望遠鏡・内視鏡・照準器などのスコープ、観察器具"
      },
      {
        "line": 277,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 279,
        "text": "【レジスター/領域】一般語としては技術・医療・天文・射撃で使う。何の器具かが重要な文章では telescope、endoscope、rifle scope など正式名称を使う。射撃関連は地域・制度・安全文脈に依存するため、ここでは語彙的な器具名として扱う。  "
      },
      {
        "line": 337,
        "text": "5. 【名詞・論理学・言語学】量化子・否定・修飾語などの作用域"
      },
      {
        "line": 341,
        "text": "【頻度】〈5/10〉  "
      },
      {
        "line": 343,
        "text": "【レジスター/領域】論理学、形式意味論、言語学、文法説明で使う専門語。一般記事の scope of the discussion などと同じ綴りだが、量化・否定・修飾の支配関係を述べる。  "
      },
      {
        "line": 401,
        "text": "6. 【名詞・コンピューター】プログラム内で名前や値を参照できる範囲、実行コンテキスト"
      },
      {
        "line": 405,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 407,
        "text": "【レジスター/領域】コンピューター科学、ソフトウェア開発、プログラミング教育で標準的な専門語。JavaScript、Python などの公式資料でも、名前の可視性・束縛・解決範囲を説明する語として使われる。  "
      },
      {
        "line": 465,
        "text": "7. 【他動詞・くだけた用法】場所・人・状況などを詳しく調べる、下見する"
      },
      {
        "line": 469,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 471,
        "text": "【レジスター/領域】scope はくだけた会話・報道・ビジネスで使う。scope out は特に口語的で、米国英語の informal として辞書に記載される。正式な報告書では examine、assess、survey などが適切なことがある。  "
      },
      {
        "line": 534,
        "text": "8. 【他動詞・主にビジネス／技術】仕事・計画・解決策の範囲や必要条件を見積もり、定める"
      },
      {
        "line": 538,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 540,
        "text": "【レジスター/領域】ビジネス、プロジェクト管理、ソフトウェア開発、設計、コンサルティングで標準的。一般会話の「調べる」より専門的で、作業内容・コスト・納期などを見積もって合意可能な範囲にする用法である。  "
      },
      {
        "line": 598,
        "text": "9. 【他動詞・技術】望遠鏡・内視鏡などで見る、観察する"
      },
      {
        "line": 602,
        "text": "【頻度】〈4/10〉  "
      },
      {
        "line": 604,
        "text": "【レジスター/領域】天文、医療、スポーツ報道などの専門・くだけた用法。医療では受動態 be scoped がよく見られるが、処置の具体的な内容は endoscopy、arthroscopy などの専門名で確認する。  "
      },
      {
        "line": 657,
        "text": "10. 【他動詞・技術】銃などにスコープを取り付ける、スコープ付きにする"
      },
      {
        "line": 661,
        "text": "【頻度】〈3/10〉  "
      },
      {
        "line": 663,
        "text": "【レジスター/領域】射撃・装備・製品説明などの限定的な用法。銃器の使用方法を説明する語ではなく、ここでは辞書にある語彙的な「スコープを装備する」という意味だけを示す。  "
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
    "collocations_examples": [
      {
        "line": 53,
        "text": "1. 【名詞・不可算】行動・発展の余地、機会、自由裁量"
      },
      {
        "line": 63,
        "text": "【コロケーション】"
      },
      {
        "line": 65,
        "text": "・plenty of scope for 〈改善・創造性〉  "
      },
      {
        "line": 66,
        "text": "用途: 何かをさらに良くしたり発展させたりする余地が十分にあることを表す。  "
      },
      {
        "line": 67,
        "text": "例: The first draft is clear, but there is still plenty of scope for improvement.  "
      },
      {
        "line": 68,
        "text": "訳: 初稿は明快だが、まだ改善の余地は十分にある。  "
      },
      {
        "line": 70,
        "text": "・limited scope for 〈行動・選択〉  "
      },
      {
        "line": 71,
        "text": "用途: 条件や制約のために、行動・選択できる余地が限られていることを表す。  "
      },
      {
        "line": 72,
        "text": "例: The narrow budget leaves us with limited scope for experimentation.  "
      },
      {
        "line": 73,
        "text": "訳: 予算が少ないため、私たちには試行の余地がほとんどない。  "
      },
      {
        "line": 75,
        "text": "・give somebody scope to do  "
      },
      {
        "line": 76,
        "text": "用途: 人が能力や判断を発揮して何かをする余地を与えることを表す。  "
      },
      {
        "line": 77,
        "text": "例: The flexible schedule gives the designers scope to test several ideas.  "
      },
      {
        "line": 78,
        "text": "訳: 柔軟な日程によって、デザイナーたちは複数の案を試す余地を得ている。  "
      },
      {
        "line": 80,
        "text": "・scope for creativity  "
      },
      {
        "line": 81,
        "text": "用途: 決められた手順に縛られず、創造的な工夫を加える余地を表す。  "
      },
      {
        "line": 82,
        "text": "例: The assignment offers students considerable scope for creativity.  "
      },
      {
        "line": 83,
        "text": "訳: その課題には、学生が創造性を発揮するかなりの余地がある。  "
      },
      {
        "line": 85,
        "text": "・within somebody's scope  "
      },
      {
        "line": 86,
        "text": "用途: ある人の能力、担当、裁量で処理できる範囲内であることを表す。  "
      },
      {
        "line": 87,
        "text": "例: Choosing the colors is within my scope, but changing the wiring is not.  "
      },
      {
        "line": 88,
        "text": "訳: 色を選ぶのは私の裁量内だが、配線を変えるのは範囲外だ。  "
      },
      {
        "line": 133,
        "text": "2. 【名詞・不可算】主題・活動・調査などが扱う範囲、対象領域"
      },
      {
        "line": 143,
        "text": "【コロケーション】"
      },
      {
        "line": 145,
        "text": "・the scope of the investigation  "
      },
      {
        "line": 146,
        "text": "用途: 調査が対象とする事件、資料、期間、関係者などの範囲を表す。  "
      },
      {
        "line": 147,
        "text": "例: The committee clarified the scope of the investigation before interviewing witnesses.  "
      },
      {
        "line": 148,
        "text": "訳: 委員会は証人への聞き取りの前に、調査の範囲を明確にした。  "
      },
      {
        "line": 150,
        "text": "・within the scope of 〈規則・契約・研究〉  "
      },
      {
        "line": 151,
        "text": "用途: ある規則、契約、研究などが対象として扱う範囲に含まれることを表す。  "
      },
      {
        "line": 152,
        "text": "例: Data security is within the scope of the proposed audit.  "
      },
      {
        "line": 153,
        "text": "訳: データセキュリティは、提案された監査の対象範囲に含まれる。  "
      },
      {
        "line": 155,
        "text": "・beyond the scope of 〈記事・調査・権限〉  "
      },
      {
        "line": 156,
        "text": "用途: 対象の境界を越え、そこでは扱わないことを表す。  "
      },
      {
        "line": 157,
        "text": "例: The causes of the conflict are beyond the scope of this short report.  "
      },
      {
        "line": 158,
        "text": "訳: その紛争の原因は、この短い報告書の扱う範囲を超えている。  "
      },
      {
        "line": 160,
        "text": "・broaden the scope of 〈議論・計画〉  "
      },
      {
        "line": 161,
        "text": "用途: 扱う主題、対象、地域、目的などを増やして範囲を広げることを表す。  "
      },
      {
        "line": 162,
        "text": "例: The new evidence broadened the scope of the debate.  "
      },
      {
        "line": 163,
        "text": "訳: 新しい証拠によって、その議論の範囲は広がった。  "
      },
      {
        "line": 165,
        "text": "・narrow the scope of 〈作業・研究〉  "
      },
      {
        "line": 166,
        "text": "用途: 対象を絞り、作業や研究を扱いやすい範囲に限定することを表す。  "
      },
      {
        "line": 167,
        "text": "例: We narrowed the scope of the study to three coastal towns.  "
      },
      {
        "line": 168,
        "text": "訳: 私たちはその研究の対象を三つの沿岸都市に絞った。  "
      },
      {
        "line": 170,
        "text": "・a project of considerable scope  "
      },
      {
        "line": 171,
        "text": "用途: 内容、作業量、影響などが大きく、広がりのあるプロジェクトを表す。  "
      },
      {
        "line": 172,
        "text": "例: Restoring the wetlands is a project of considerable scope.  "
      },
      {
        "line": 173,
        "text": "訳: 湿地を再生することは、かなり大規模なプロジェクトである。  "
      },
      {
        "line": 209,
        "text": "3. 【名詞・不可算】人・組織の能力、知識、権限が及ぶ範囲"
      },
      {
        "line": 219,
        "text": "【コロケーション】"
      },
      {
        "line": 221,
        "text": "・outside my scope  "
      },
      {
        "line": 222,
        "text": "用途: 自分の技能、担当、権限では扱えないことを簡潔に示す。  "
      },
      {
        "line": 223,
        "text": "例: Diagnosing the hardware fault is outside my scope, so I called a technician.  "
      },
      {
        "line": 224,
        "text": "訳: ハードウェアの故障を診断するのは私の担当外なので、技術者を呼んだ。  "
      },
      {
        "line": 226,
        "text": "・within the scope of the role  "
      },
      {
        "line": 227,
        "text": "用途: ある職務に正式または実務上含まれる責任・活動を表す。  "
      },
      {
        "line": 228,
        "text": "例: Training new staff is within the scope of her role.  "
      },
      {
        "line": 229,
        "text": "訳: 新しい職員の訓練は彼女の職務範囲に含まれる。  "
      },
      {
        "line": 231,
        "text": "・the scope of authority  "
      },
      {
        "line": 232,
        "text": "用途: 人・組織が決定し、許可し、指示できる権限の範囲を表す。  "
      },
      {
        "line": 233,
        "text": "例: The policy sets out the scope of authority for regional managers.  "
      },
      {
        "line": 234,
        "text": "訳: その方針は地域管理者の権限範囲を定めている。  "
      },
      {
        "line": 236,
        "text": "・fall within somebody's scope  "
      },
      {
        "line": 237,
        "text": "用途: 課題や判断事項が、ある人・部署の担当範囲に含まれることを表す。  "
      },
      {
        "line": 238,
        "text": "例: Routine maintenance falls within the facilities team's scope.  "
      },
      {
        "line": 239,
        "text": "訳: 定期的な保守は施設チームの担当範囲に入る。  "
      },
      {
        "line": 241,
        "text": "・expand the scope of 〈a service・a team〉  "
      },
      {
        "line": 242,
        "text": "用途: サービスやチームが扱える対象・地域・業務を広げることを表す。  "
      },
      {
        "line": 243,
        "text": "例: The clinic expanded the scope of its service to include evening appointments.  "
      },
      {
        "line": 244,
        "text": "訳: その診療所はサービスの範囲を広げ、夜間の予約も受け付けるようにした。  "
      },
      {
        "line": 273,
        "text": "4. 【名詞・可算】望遠鏡・内視鏡・照準器などのスコープ、観察器具"
      },
      {
        "line": 283,
        "text": "【コロケーション】"
      },
      {
        "line": 285,
        "text": "・look through a scope  "
      },
      {
        "line": 286,
        "text": "用途: スコープをのぞいて遠くの対象や照準対象を見ることを表す。  "
      },
      {
        "line": 287,
        "text": "例: The astronomer looked through the scope and identified a faint ring around the planet.  "
      },
      {
        "line": 288,
        "text": "訳: 天文学者はスコープをのぞき、その惑星の周りのかすかな輪を確認した。  "
      },
      {
        "line": 290,
        "text": "・a rifle scope  "
      },
      {
        "line": 291,
        "text": "用途: ライフルなどに取り付ける照準用の望遠鏡を表す。  "
      },
      {
        "line": 292,
        "text": "例: The manual explains how to adjust the rifle scope safely.  "
      },
      {
        "line": 293,
        "text": "訳: その説明書はライフルスコープを安全に調整する方法を説明している。  "
      },
      {
        "line": 295,
        "text": "・a medical scope  "
      },
      {
        "line": 296,
        "text": "用途: 体内を観察する医療用の内視鏡を、種類を特定せずに表す。  "
      },
      {
        "line": 297,
        "text": "例: The doctor used a medical scope to examine the patient's throat.  "
      },
      {
        "line": 298,
        "text": "訳: 医師は医療用スコープで患者の喉を調べた。  "
      },
      {
        "line": 300,
        "text": "・mount a scope on 〈器具〉  "
      },
      {
        "line": 301,
        "text": "用途: 観察・照準器具を別の器具に取り付けることを表す。  "
      },
      {
        "line": 302,
        "text": "例: The technician mounted a scope on the surveying instrument.  "
      },
      {
        "line": 303,
        "text": "訳: 技術者は測量機器にスコープを取り付けた。  "
      },
      {
        "line": 305,
        "text": "・adjust the scope  "
      },
      {
        "line": 306,
        "text": "用途: 焦点、倍率、照準などを見やすく・正確になるよう調整することを表す。  "
      },
      {
        "line": 307,
        "text": "例: She adjusted the scope until the distant marker came into focus.  "
      },
      {
        "line": 308,
        "text": "訳: 彼女は遠くの標識に焦点が合うまでスコープを調整した。  "
      },
      {
        "line": 337,
        "text": "5. 【名詞・論理学・言語学】量化子・否定・修飾語などの作用域"
      },
      {
        "line": 347,
        "text": "【コロケーション】"
      },
      {
        "line": 349,
        "text": "・the scope of a quantifier  "
      },
      {
        "line": 350,
        "text": "用途: every、some、no などの量化子が意味上支配する表現の範囲を表す。  "
      },
      {
        "line": 351,
        "text": "例: The scope of the quantifier determines whether the sentence allows one reading or two.  "
      },
      {
        "line": 352,
        "text": "訳: 量化子の作用域によって、その文が一つの解釈を許すか二つを許すかが決まる。  "
      },
      {
        "line": 354,
        "text": "・take scope over 〈an expression〉  "
      },
      {
        "line": 355,
        "text": "用途: 否定、量化子、修飾語などが、別の表現の解釈を支配することを表す。  "
      },
      {
        "line": 356,
        "text": "例: In this reading, the negation takes scope over the entire conditional.  "
      },
      {
        "line": 357,
        "text": "訳: この解釈では、否定が条件文全体に作用域を及ぼす。  "
      },
      {
        "line": 359,
        "text": "・wide scope  "
      },
      {
        "line": 360,
        "text": "用途: 演算子が文や命題の広い部分に及ぶ解釈を表す。  "
      },
      {
        "line": 361,
        "text": "例: The adverb has wide scope and modifies both clauses.  "
      },
      {
        "line": 362,
        "text": "訳: その副詞は広い作用域を持ち、二つの節を修飾する。  "
      },
      {
        "line": 364,
        "text": "・narrow scope  "
      },
      {
        "line": 365,
        "text": "用途: 演算子が直近の語句や一部の表現だけに及ぶ解釈を表す。  "
      },
      {
        "line": 366,
        "text": "例: Under the narrow-scope reading, the speaker denies only the final claim.  "
      },
      {
        "line": 367,
        "text": "訳: 狭い作用域の解釈では、話者は最後の主張だけを否定している。  "
      },
      {
        "line": 369,
        "text": "・scope ambiguity  "
      },
      {
        "line": 370,
        "text": "用途: 一つの文が、量化子や否定の作用域の違いによって複数の意味に読めることを表す。  "
      },
      {
        "line": 371,
        "text": "例: The textbook uses a simple example of scope ambiguity.  "
      },
      {
        "line": 372,
        "text": "訳: その教科書は作用域の曖昧性の簡単な例を使っている。  "
      },
      {
        "line": 401,
        "text": "6. 【名詞・コンピューター】プログラム内で名前や値を参照できる範囲、実行コンテキスト"
      },
      {
        "line": 411,
        "text": "【コロケーション】"
      },
      {
        "line": 413,
        "text": "・variable scope  "
      },
      {
        "line": 414,
        "text": "用途: 変数名を参照できるコード上の範囲を表す。  "
      },
      {
        "line": 415,
        "text": "例: The variable scope ends when the function returns.  "
      },
      {
        "line": 416,
        "text": "訳: その変数のスコープは関数が戻ると終わる。  "
      },
      {
        "line": 418,
        "text": "・global scope  "
      },
      {
        "line": 419,
        "text": "用途: プログラム全体またはモジュール全体から参照され得る最上位の範囲を表す。  "
      },
      {
        "line": 420,
        "text": "例: Avoid putting mutable configuration in the global scope.  "
      },
      {
        "line": 421,
        "text": "訳: 変更可能な設定をグローバルスコープに置くのは避けなさい。  "
      },
      {
        "line": 423,
        "text": "・function scope  "
      },
      {
        "line": 424,
        "text": "用途: 関数の本体を境界とする名前の可視範囲を表す。  "
      },
      {
        "line": 425,
        "text": "例: The parameter is available throughout the function scope.  "
      },
      {
        "line": 426,
        "text": "訳: その引数は関数スコープ全体で利用できる。  "
      },
      {
        "line": 428,
        "text": "・block scope  "
      },
      {
        "line": 429,
        "text": "用途: 波括弧などで区切られたブロックを境界とするスコープを表す。  "
      },
      {
        "line": 430,
        "text": "例: In this language, a constant declared inside the block scope cannot be used outside it.  "
      },
      {
        "line": 431,
        "text": "訳: この言語では、ブロックスコープ内で宣言した定数を外では使えない。  "
      },
      {
        "line": 433,
        "text": "・be out of scope  "
      },
      {
        "line": 434,
        "text": "用途: 参照しようとする名前が現在の実行・構文範囲から見えないことを表す。  "
      },
      {
        "line": 435,
        "text": "例: The helper is out of scope here because it was declared inside another function.  "
      },
      {
        "line": 436,
        "text": "訳: そのヘルパーは別の関数内で宣言されたので、ここではスコープ外である。  "
      },
      {
        "line": 465,
        "text": "7. 【他動詞・くだけた用法】場所・人・状況などを詳しく調べる、下見する"
      },
      {
        "line": 475,
        "text": "【コロケーション】"
      },
      {
        "line": 477,
        "text": "・scope out the area  "
      },
      {
        "line": 478,
        "text": "用途: 地域や場所を前もって見て、安全性、雰囲気、利便性などの情報を集める。  "
      },
      {
        "line": 479,
        "text": "例: We scoped out the area before choosing a hotel.  "
      },
      {
        "line": 480,
        "text": "訳: 私たちはホテルを選ぶ前に、その地域を下見した。  "
      },
      {
        "line": 482,
        "text": "・scope out the competition  "
      },
      {
        "line": 483,
        "text": "用途: 競争相手の動き、強み、位置づけなどを調べる。  "
      },
      {
        "line": 484,
        "text": "例: The startup is scoping out the competition before launching its product.  "
      },
      {
        "line": 485,
        "text": "訳: その新興企業は製品を発売する前に競合を調べている。  "
      },
      {
        "line": 487,
        "text": "・scope the room  "
      },
      {
        "line": 488,
        "text": "用途: 部屋を見回し、人や物の位置を注意深く確認する。  "
      },
      {
        "line": 489,
        "text": "例: He scoped the room for an empty seat before the lecture began.  "
      },
      {
        "line": 490,
        "text": "訳: 彼は講義が始まる前に、空いている席がないか部屋を見回した。  "
      },
      {
        "line": 492,
        "text": "・scope out the possibilities  "
      },
      {
        "line": 493,
        "text": "用途: 選択肢や実現可能性を検討するため、情報を集めて評価する。  "
      },
      {
        "line": 494,
        "text": "例: The team spent a week scoping out the possibilities for a remote launch.  "
      },
      {
        "line": 495,
        "text": "訳: そのチームは遠隔での発売の可能性を一週間かけて検討した。  "
      },
      {
        "line": 497,
        "text": "・scope somebody out  "
      },
      {
        "line": 498,
        "text": "用途: 人の様子、能力、魅力、意図などを観察して情報を得る。くだけた表現。  "
      },
      {
        "line": 499,
        "text": "例: The recruiter quietly scoped the candidates out during the workshop.  "
      },
      {
        "line": 500,
        "text": "訳: 採用担当者は研修中に候補者たちをひそかに観察した。  "
      },
      {
        "line": 502,
        "text": "・scope it out  "
      },
      {
        "line": 503,
        "text": "用途: 代名詞を使って、場所・計画・状況などを詳しく調べる。  "
      },
      {
        "line": 504,
        "text": "例: I cannot decide yet; let me scope it out first.  "
      },
      {
        "line": 505,
        "text": "訳: まだ決められない。まずそれを詳しく調べさせてください。  "
      },
      {
        "line": 534,
        "text": "8. 【他動詞・主にビジネス／技術】仕事・計画・解決策の範囲や必要条件を見積もり、定める"
      },
      {
        "line": 544,
        "text": "【コロケーション】"
      },
      {
        "line": 546,
        "text": "・scope the project  "
      },
      {
        "line": 547,
        "text": "用途: プロジェクトに含める作業、成果物、境界、前提を定める。  "
      },
      {
        "line": 548,
        "text": "例: We need to scope the project before we promise a delivery date.  "
      },
      {
        "line": 549,
        "text": "訳: 納期を約束する前に、そのプロジェクトの範囲を定める必要がある。  "
      },
      {
        "line": 551,
        "text": "・scope the work  "
      },
      {
        "line": 552,
        "text": "用途: 必要な作業の量、順序、担当、条件などを具体化する。  "
      },
      {
        "line": 553,
        "text": "例: The consultant scoped the work in three phases.  "
      },
      {
        "line": 554,
        "text": "訳: コンサルタントは作業を三段階に分けて範囲を定めた。  "
      },
      {
        "line": 556,
        "text": "・scope a solution  "
      },
      {
        "line": 557,
        "text": "用途: 問題を解決するための機能、対象、制約、実装範囲を見積もる。  "
      },
      {
        "line": 558,
        "text": "例: The team scoped a solution that could be delivered within six weeks.  "
      },
      {
        "line": 559,
        "text": "訳: そのチームは6週間以内に提供できる解決策の範囲を定めた。  "
      },
      {
        "line": 561,
        "text": "・scope out requirements and costs  "
      },
      {
        "line": 562,
        "text": "用途: 作業開始前に必要条件と費用を下調べし、計画の大きさを把握する。  "
      },
      {
        "line": 563,
        "text": "例: They scoped out the requirements and costs before writing the proposal.  "
      },
      {
        "line": 564,
        "text": "訳: 彼らは提案書を書く前に要件と費用を下調べした。  "
      },
      {
        "line": 566,
        "text": "・be fully scoped  "
      },
      {
        "line": 567,
        "text": "用途: プロジェクトや機能の範囲・要件が十分に定義され、見積もり可能であることを表す。  "
      },
      {
        "line": 568,
        "text": "例: The feature is not fully scoped, so the estimate may change.  "
      },
      {
        "line": 569,
        "text": "訳: その機能の範囲はまだ十分に定義されていないので、見積もりは変わるかもしれない。  "
      },
      {
        "line": 598,
        "text": "9. 【他動詞・技術】望遠鏡・内視鏡などで見る、観察する"
      },
      {
        "line": 608,
        "text": "【コロケーション】"
      },
      {
        "line": 610,
        "text": "・scope the sky  "
      },
      {
        "line": 611,
        "text": "用途: 望遠鏡などで空や天体を観察する。  "
      },
      {
        "line": 612,
        "text": "例: The students scoped the sky for the comet after sunset.  "
      },
      {
        "line": 613,
        "text": "訳: 学生たちは日没後、彗星を探して空を観察した。  "
      },
      {
        "line": 615,
        "text": "・scope the knee  "
      },
      {
        "line": 616,
        "text": "用途: 関節鏡などで膝関節を検査する。医療のくだけた短縮表現。  "
      },
      {
        "line": 617,
        "text": "例: The surgeon decided to scope the knee after the scan showed a possible tear.  "
      },
      {
        "line": 618,
        "text": "訳: スキャンで裂傷の可能性が示されたため、外科医は膝を関節鏡で検査することにした。  "
      },
      {
        "line": 620,
        "text": "・be scoped for 〈condition〉  "
      },
      {
        "line": 621,
        "text": "用途: ある病状の確認のために内視鏡検査を受けることを表す。  "
      },
      {
        "line": 622,
        "text": "例: She was scoped for internal bleeding after the accident.  "
      },
      {
        "line": 623,
        "text": "訳: 彼女は事故の後、内出血がないか内視鏡検査を受けた。  "
      },
      {
        "line": 625,
        "text": "・scope 〈a joint〉 with 〈an arthroscope〉  "
      },
      {
        "line": 626,
        "text": "用途: 関節鏡を使って関節を検査することを明示する。  "
      },
      {
        "line": 627,
        "text": "例: The specialist scoped the joint with an arthroscope before repairing it.  "
      },
      {
        "line": 628,
        "text": "訳: 専門医は修復する前に関節鏡でその関節を検査した。  "
      },
      {
        "line": 657,
        "text": "10. 【他動詞・技術】銃などにスコープを取り付ける、スコープ付きにする"
      },
      {
        "line": 667,
        "text": "【コロケーション】"
      },
      {
        "line": 669,
        "text": "・scope a rifle  "
      },
      {
        "line": 670,
        "text": "用途: ライフルに照準用スコープを取り付けることを表す。  "
      },
      {
        "line": 671,
        "text": "例: The owner had a specialist scope the rifle at a licensed range.  "
      },
      {
        "line": 672,
        "text": "訳: 所有者は認可された射撃場で専門家にライフルへスコープを取り付けてもらった。  "
      },
      {
        "line": 674,
        "text": "・a scoped rifle  "
      },
      {
        "line": 675,
        "text": "用途: 照準用スコープを装備したライフルを表す。  "
      },
      {
        "line": 676,
        "text": "例: The catalog lists the weight of the scoped rifle separately from the bare rifle.  "
      },
      {
        "line": 677,
        "text": "訳: そのカタログは、スコープ付きライフルの重量を、ライフル単体とは別に記載している。  "
      },
      {
        "line": 679,
        "text": "・be scoped for 〈use・range〉  "
      },
      {
        "line": 680,
        "text": "用途: 特定の用途や距離に合わせたスコープを装備していることを表す。  "
      },
      {
        "line": 681,
        "text": "例: The equipment was scoped for short-range observation rather than long-distance use.  "
      },
      {
        "line": 682,
        "text": "訳: その装備は長距離用ではなく、近距離観察用のスコープを備えていた。  "
      },
      {
        "line": 684,
        "text": "・a scope-equipped 〈device〉  "
      },
      {
        "line": 685,
        "text": "用途: scope の動詞ではなく、スコープを備えた装置を明示的に表す複合的な言い方。  "
      },
      {
        "line": 686,
        "text": "例: The safety sheet describes the scope-equipped device in neutral technical terms.  "
      },
      {
        "line": 687,
        "text": "訳: その安全資料は、スコープ付き装置を中立的な技術用語で説明している。  "
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
