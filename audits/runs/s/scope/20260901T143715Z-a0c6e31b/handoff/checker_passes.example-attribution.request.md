# Independent checker handoff

Stage: `checker_passes/example-attribution`

Run this request in its own independent agent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one agent for multiple passes.

Save exactly one JSON response as `checker_passes.example-attribution.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_example_attribution_v6

## 目的

見出し語の各例文が、所属する語義ブロックへ意味的に帰属するかを、所属情報を参照しない先行判定（ブラインド再分類）で検査する。

## 担当タクソノミー分類

- `example_sense_attribution_mismatch`

## 検査ルール

- 検査は必ず次の2段階の順で行い、段階1の判定を段階2より先に確定・記録する。
- 段階1（ブラインド帰属判定）: `sense_structure` から語義番号、見出しの品詞・意味領域ラベル、訳語、定義の一覧を作る。次に `collocations_examples` の各例文（見出し語を含む例文のみ。類義語・反意語欄の例文は対象外）について、所属ブロック、コロケーション見出し、用途行を参照せず、例文と訳だけから最も自然な帰属語義を判定する。次点候補の有無と、判別根拠となった例文内の語句を記録する。
- 段階1では所属語義を含まない `example_attribution_blind_request_v1` だけを受け取り、判定を `example_attribution_blind_record_v1` として保存する。調整役はこの記録が保存されるまで所属キーを渡さない。
- 段階2（照合）: 保存済みの段階1判定を実際の所属ブロックと照合する。この段階で初めて、所属キーと所属語義の【語法・注意】を受け取る。照合時刻は段階1の記録時刻より後でなければならず、最終pass出力に段階1記録を変更せず埋め込む。
- 判定基準は次のとおり。
  - 帰属判定が所属ブロックと不一致: `blocking`。
  - 複数語義で同程度に自然であり、例文内に判別語がない: `blocking`。
  - 一致かつ一意: 問題なし。
- 訳文だけが別語義を示し英文は所属語義に一致する場合は、translationパスの担当として `unrouted_observation` で調整役へ返す。
- 語義の統合・分割そのものに問題があると疑われる場合は、sense-structureパスの担当として `unrouted_observation` で返す。
- 所属ブロックの【語法・注意】が示す語義区別に、そのブロック内の例文が反する場合は、本taxonomyのfindingとして例文側の位置をanchorにする。
- `example_translation_alignment` は英文と訳文の対応だけを扱い、英文自体の語義帰属は本パスが扱う。
- `argument_slot_role_mismatch` は統語スロットと意味役割の実現だけを扱い、統語的に正しいが意味的に別語義である例文は本パスが扱う。
- `cross_section_internal_contradiction` は例文を入力に含めないセクション間矛盾を扱い、例文起点の矛盾は本パスが扱う。

## 入力として受け取るセクション

- `sense_structure`
- `collocations_examples`

段階1入力の `collocations_examples` には、所属ブロック、コロケーション見出し、用途行を除いた例文と訳だけを入れる。段階2の所属キーと所属語義の【語法・注意】は、段階1記録の保存後に別artifactとして受け取る。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "example_sense_attribution_mismatch",
  "location": {
    "section": "collocations_examples",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない例文行"
  },
  "severity": "blocking",
  "rationale": "ブラインド帰属判定、実際の所属語義、曖昧性、判別語の有無",
  "evidence_link_ids": [],
  "suggested_direction": "例文置換 | 語義ブロック間の移動 | 判別語の追加"
}
```

最終pass出力にはfindingと併せて、段階1の `blind_attribution_record`、段階2の `aligned_at`、必要に応じて `unrouted_observations` を含める。`suggested_direction` は例文置換、語義ブロック間の移動、判別語の追加のいずれか1方向を記録する。

段階1はrun別の不透明ID・shuffle順を使う。非公開alignment keyで復元し、request hashを照合する。


## Input packet

```json
{
  "schema_version": "example_attribution_blind_request_v1",
  "pass_id": "example-attribution",
  "taxonomy_ids": [
    "example_sense_attribution_mismatch"
  ],
  "specification": "prompts/check_pass_example_attribution_v6.md",
  "input_body_sha256": "3f34e03e76f478959eb828c3e94f244b289a9a6e67ca0894cfa50e8f1869002b",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 53,
        "label": "1. 【名詞・不可算】行動・発展の余地、機会、自由裁量",
        "definition": "人が何かをしたり、能力を伸ばしたりするために残されている余地・機会。scope for + 名詞・動名詞 が最も定着しており、十分な余地にも、ほとんど余地がない状態にも使える。実際に成功する機会を保証する語ではなく、可能性を活かせる空間を表す。"
      },
      {
        "sense_id": "sense:002",
        "line": 133,
        "label": "2. 【名詞・不可算】主題・活動・調査などが扱う範囲、対象領域",
        "definition": "本、議論、調査、計画、組織の活動などに含まれる主題・対象・作業の境界。scope of 〈対象〉、within/beyond/outside the scope of 〈対象〉、broad/narrow in scope の形で、何を含め何を含めないかを示す。物理的な大きさではなく、内容・活動・影響の広がりに焦点がある。"
      },
      {
        "sense_id": "sense:003",
        "line": 209,
        "label": "3. 【名詞・不可算】人・組織の能力、知識、権限が及ぶ範囲",
        "definition": "人、職種、組織、制度などが知識・技能・責任・権限によって扱える範囲。語義2の「調査や計画が何を含むか」と似るが、ここでは主体側の能力・担当・許可された権限に焦点がある。my scope、the scope of the role、within/outside one's scope などで使う。"
      },
      {
        "sense_id": "sense:004",
        "line": 273,
        "label": "4. 【名詞・可算】望遠鏡・内視鏡・照準器などのスコープ、観察器具",
        "definition": "遠くのもの、内部、または照準対象を見るための器具を指す短縮的な名詞。文脈により telescope、microscope、endoscope、rifle scope などを指し、scope 単独で器具の種類が決まるとは限らない。医療では検査用の内視鏡、射撃では銃に取り付ける照準望遠鏡を指すことがある。"
      },
      {
        "sense_id": "sense:005",
        "line": 337,
        "label": "5. 【名詞・論理学・言語学】量化子・否定・修飾語などの作用域",
        "definition": "論理式や文の中で、量化子、否定、修飾語などが意味・真偽の解釈に影響を及ぼす部分。scope of a quantifier はその量化子が支配する領域を指し、文の構造によって複数の解釈が生じると scope ambiguity「作用域の曖昧性」になる。一般的な「主題の範囲」と違い、意味解釈を決める構造上の領域である。"
      },
      {
        "sense_id": "sense:006",
        "line": 401,
        "label": "6. 【名詞・コンピューター】プログラム内で名前や値を参照できる範囲、実行コンテキスト",
        "definition": "変数、関数、値などがプログラムのどの部分から見え、参照できるかを決める実行上の範囲・文脈。global scope、function scope、block scope、lexical scope などがあり、内側の scope が外側の scope を参照できる階層構造を持つことがある。言語ごとの規則は異なるため、scope という一般概念と各言語の実装規則を分けて理解する。"
      },
      {
        "sense_id": "sense:007",
        "line": 465,
        "label": "7. 【他動詞・くだけた用法】場所・人・状況などを詳しく調べる、下見する",
        "definition": "場所、人、競争相手、状況、可能性などを注意深く見て、情報を得たり評価したりする。scope something は調査対象を直接置く形、scope something/someone out は「詳しく下見する・情報を集める」という句動詞で、くだけた用法である。対象を見ただけで最終判断や実行まで済ませたことは含まない。"
      },
      {
        "sense_id": "sense:008",
        "line": 534,
        "label": "8. 【他動詞・主にビジネス／技術】仕事・計画・解決策の範囲や必要条件を見積もり、定める",
        "definition": "作業に着手する前に、プロジェクト、解決策、機能、要件などを調べて、必要な作業量・費用・範囲・条件を明確にする。scope the project/solution のように目的語を直接取る。scope out は同じ準備段階をより口語的に表すが、scope は計画上の境界を定義する意味が強い。"
      },
      {
        "sense_id": "sense:009",
        "line": 598,
        "label": "9. 【他動詞・技術】望遠鏡・内視鏡などで見る、観察する",
        "definition": "対象を望遠鏡で見たり、内視鏡・関節鏡などで体内や狭い部分を検査したりする。scope the sky、scope the knee のように直接目的語を取る。一般の「詳しく調べる」より、どの器具を使うかが文脈で明らかな技術・医療用法である。"
      },
      {
        "sense_id": "sense:010",
        "line": 657,
        "label": "10. 【他動詞・技術】銃などにスコープを取り付ける、スコープ付きにする",
        "definition": "銃などの器具に照準用のスコープを取り付け、スコープを使える状態にする。scope a rifle、a scoped rifle のように使う低頻度の技術用法で、語義4の器具名から品詞転換したもの。対象を調べる scope と異なり、目的語は装備される器具である。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-a2ae993f5b2a",
        "example": "The owner had a specialist scope the rifle at a licensed range.",
        "translation": "所有者は認可された射撃場で専門家にライフルへスコープを取り付けてもらった。"
      },
      {
        "example_id": "ex-41375c397c1e",
        "example": "She was scoped for internal bleeding after the accident.",
        "translation": "彼女は事故の後、内出血がないか内視鏡検査を受けた。"
      },
      {
        "example_id": "ex-253bb056adec",
        "example": "The astronomer looked through the scope and identified a faint ring around the planet.",
        "translation": "天文学者はスコープをのぞき、その惑星の周りのかすかな輪を確認した。"
      },
      {
        "example_id": "ex-75be596f75e5",
        "example": "We need to scope the project before we promise a delivery date.",
        "translation": "納期を約束する前に、そのプロジェクトの範囲を定める必要がある。"
      },
      {
        "example_id": "ex-fb04f78fdb3f",
        "example": "The surgeon decided to scope the knee after the scan showed a possible tear.",
        "translation": "スキャンで裂傷の可能性が示されたため、外科医は膝を関節鏡で検査することにした。"
      },
      {
        "example_id": "ex-6de8905779b0",
        "example": "The variable scope ends when the function returns.",
        "translation": "その変数のスコープは関数が戻ると終わる。"
      },
      {
        "example_id": "ex-33402b73a628",
        "example": "The safety sheet describes the scope-equipped device in neutral technical terms.",
        "translation": "その安全資料は、スコープ付き装置を中立的な技術用語で説明している。"
      },
      {
        "example_id": "ex-ce889c4916d0",
        "example": "Restoring the wetlands is a project of considerable scope.",
        "translation": "湿地を再生することは、かなり大規模なプロジェクトである。"
      },
      {
        "example_id": "ex-f8537c15f504",
        "example": "Avoid putting mutable configuration in the global scope.",
        "translation": "変更可能な設定をグローバルスコープに置くのは避けなさい。"
      },
      {
        "example_id": "ex-c22790a906f4",
        "example": "The manual explains how to adjust the rifle scope safely.",
        "translation": "その説明書はライフルスコープを安全に調整する方法を説明している。"
      },
      {
        "example_id": "ex-bfe54043efb1",
        "example": "The policy sets out the scope of authority for regional managers.",
        "translation": "その方針は地域管理者の権限範囲を定めている。"
      },
      {
        "example_id": "ex-9fb3fb579644",
        "example": "The parameter is available throughout the function scope.",
        "translation": "その引数は関数スコープ全体で利用できる。"
      },
      {
        "example_id": "ex-d5e0d9168856",
        "example": "The scope of the quantifier determines whether the sentence allows one reading or two.",
        "translation": "量化子の作用域によって、その文が一つの解釈を許すか二つを許すかが決まる。"
      },
      {
        "example_id": "ex-49117997bc66",
        "example": "The clinic expanded the scope of its service to include evening appointments.",
        "translation": "その診療所はサービスの範囲を広げ、夜間の予約も受け付けるようにした。"
      },
      {
        "example_id": "ex-d226fa6f7761",
        "example": "She adjusted the scope until the distant marker came into focus.",
        "translation": "彼女は遠くの標識に焦点が合うまでスコープを調整した。"
      },
      {
        "example_id": "ex-c6d234773106",
        "example": "The textbook uses a simple example of scope ambiguity.",
        "translation": "その教科書は作用域の曖昧性の簡単な例を使っている。"
      },
      {
        "example_id": "ex-54b0597198d7",
        "example": "He scoped the room for an empty seat before the lecture began.",
        "translation": "彼は講義が始まる前に、空いている席がないか部屋を見回した。"
      },
      {
        "example_id": "ex-2d6e1f2941ae",
        "example": "The committee clarified the scope of the investigation before interviewing witnesses.",
        "translation": "委員会は証人への聞き取りの前に、調査の範囲を明確にした。"
      },
      {
        "example_id": "ex-dfdf9cc30419",
        "example": "The first draft is clear, but there is still plenty of scope for improvement.",
        "translation": "初稿は明快だが、まだ改善の余地は十分にある。"
      },
      {
        "example_id": "ex-863cbafce951",
        "example": "The assignment offers students considerable scope for creativity.",
        "translation": "その課題には、学生が創造性を発揮するかなりの余地がある。"
      },
      {
        "example_id": "ex-a6fd0f704884",
        "example": "Routine maintenance falls within the facilities team's scope.",
        "translation": "定期的な保守は施設チームの担当範囲に入る。"
      },
      {
        "example_id": "ex-99802014c794",
        "example": "Diagnosing the hardware fault is outside my scope, so I called a technician.",
        "translation": "ハードウェアの故障を診断するのは私の担当外なので、技術者を呼んだ。"
      },
      {
        "example_id": "ex-fb7086c19662",
        "example": "The doctor used a medical scope to examine the patient's throat.",
        "translation": "医師は医療用スコープで患者の喉を調べた。"
      },
      {
        "example_id": "ex-305f52b88bcd",
        "example": "The adverb has wide scope and modifies both clauses.",
        "translation": "その副詞は広い作用域を持ち、二つの節を修飾する。"
      },
      {
        "example_id": "ex-ea7b36d18300",
        "example": "The narrow budget leaves us with limited scope for experimentation.",
        "translation": "予算が少ないため、私たちには試行の余地がほとんどない。"
      },
      {
        "example_id": "ex-61fd1a8c9193",
        "example": "The team scoped a solution that could be delivered within six weeks.",
        "translation": "そのチームは6週間以内に提供できる解決策の範囲を定めた。"
      },
      {
        "example_id": "ex-8ab2a19753a9",
        "example": "The new evidence broadened the scope of the debate.",
        "translation": "新しい証拠によって、その議論の範囲は広がった。"
      },
      {
        "example_id": "ex-22083379f331",
        "example": "In this reading, the negation takes scope over the entire conditional.",
        "translation": "この解釈では、否定が条件文全体に作用域を及ぼす。"
      },
      {
        "example_id": "ex-9c560a888f62",
        "example": "We scoped out the area before choosing a hotel.",
        "translation": "私たちはホテルを選ぶ前に、その地域を下見した。"
      },
      {
        "example_id": "ex-dd1d0d34a4e4",
        "example": "The causes of the conflict are beyond the scope of this short report.",
        "translation": "その紛争の原因は、この短い報告書の扱う範囲を超えている。"
      },
      {
        "example_id": "ex-57dbedeb70ef",
        "example": "The students scoped the sky for the comet after sunset.",
        "translation": "学生たちは日没後、彗星を探して空を観察した。"
      },
      {
        "example_id": "ex-e823f8fc8487",
        "example": "The technician mounted a scope on the surveying instrument.",
        "translation": "技術者は測量機器にスコープを取り付けた。"
      },
      {
        "example_id": "ex-4a36c566f7c0",
        "example": "The specialist scoped the joint with an arthroscope before repairing it.",
        "translation": "専門医は修復する前に関節鏡でその関節を検査した。"
      },
      {
        "example_id": "ex-303848d8a7a4",
        "example": "The consultant scoped the work in three phases.",
        "translation": "コンサルタントは作業を三段階に分けて範囲を定めた。"
      },
      {
        "example_id": "ex-97ce1d6e20e3",
        "example": "The equipment was scoped for short-range observation rather than long-distance use.",
        "translation": "その装備は長距離用ではなく、近距離観察用のスコープを備えていた。"
      },
      {
        "example_id": "ex-21bd205b0863",
        "example": "I cannot decide yet; let me scope it out first.",
        "translation": "まだ決められない。まずそれを詳しく調べさせてください。"
      },
      {
        "example_id": "ex-d017e0892427",
        "example": "The helper is out of scope here because it was declared inside another function.",
        "translation": "そのヘルパーは別の関数内で宣言されたので、ここではスコープ外である。"
      },
      {
        "example_id": "ex-4d0cfdb1e863",
        "example": "The flexible schedule gives the designers scope to test several ideas.",
        "translation": "柔軟な日程によって、デザイナーたちは複数の案を試す余地を得ている。"
      },
      {
        "example_id": "ex-dcb1415a3a8a",
        "example": "Training new staff is within the scope of her role.",
        "translation": "新しい職員の訓練は彼女の職務範囲に含まれる。"
      },
      {
        "example_id": "ex-6aece8c92a69",
        "example": "The recruiter quietly scoped the candidates out during the workshop.",
        "translation": "採用担当者は研修中に候補者たちをひそかに観察した。"
      },
      {
        "example_id": "ex-265051c18500",
        "example": "We narrowed the scope of the study to three coastal towns.",
        "translation": "私たちはその研究の対象を三つの沿岸都市に絞った。"
      },
      {
        "example_id": "ex-8cec1d0ad140",
        "example": "The startup is scoping out the competition before launching its product.",
        "translation": "その新興企業は製品を発売する前に競合を調べている。"
      },
      {
        "example_id": "ex-fd87ad2d207c",
        "example": "The team spent a week scoping out the possibilities for a remote launch.",
        "translation": "そのチームは遠隔での発売の可能性を一週間かけて検討した。"
      },
      {
        "example_id": "ex-caff79695733",
        "example": "Choosing the colors is within my scope, but changing the wiring is not.",
        "translation": "色を選ぶのは私の裁量内だが、配線を変えるのは範囲外だ。"
      },
      {
        "example_id": "ex-58e0a9677293",
        "example": "Data security is within the scope of the proposed audit.",
        "translation": "データセキュリティは、提案された監査の対象範囲に含まれる。"
      },
      {
        "example_id": "ex-60fd659feb66",
        "example": "They scoped out the requirements and costs before writing the proposal.",
        "translation": "彼らは提案書を書く前に要件と費用を下調べした。"
      },
      {
        "example_id": "ex-ff88772c4a02",
        "example": "The catalog lists the weight of the scoped rifle separately from the bare rifle.",
        "translation": "そのカタログは、スコープ付きライフルの重量を、ライフル単体とは別に記載している。"
      },
      {
        "example_id": "ex-547ff0a59cc8",
        "example": "The feature is not fully scoped, so the estimate may change.",
        "translation": "その機能の範囲はまだ十分に定義されていないので、見積もりは変わるかもしれない。"
      },
      {
        "example_id": "ex-42d947b8d2ee",
        "example": "Under the narrow-scope reading, the speaker denies only the final claim.",
        "translation": "狭い作用域の解釈では、話者は最後の主張だけを否定している。"
      },
      {
        "example_id": "ex-b27b2f17de42",
        "example": "In this language, a constant declared inside the block scope cannot be used outside it.",
        "translation": "この言語では、ブロックスコープ内で宣言した定数を外では使えない。"
      }
    ]
  },
  "blind_protocol": {
    "stage": 1,
    "withheld_fields": [
      "assigned_sense_id",
      "collocation_heading",
      "usage_line",
      "example_group_boundary",
      "document_order"
    ],
    "required_output_schema": "example_attribution_blind_record_v1"
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
