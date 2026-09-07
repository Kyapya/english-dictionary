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
  "input_body_sha256": "4ab58d0a9b82ee8b0ade3bc81ddbd1b7a34b2d50961f3dbe201fd02a0f6e5ab8",
  "input_sections": {
    "core_image": [
      {
        "line": 30,
        "text": "＃コアイメージ"
      },
      {
        "line": 32,
        "text": "権限、仕事、取引などを正式に誰かへ委ね、その実行を担わせること。委ねられた主体、依頼された仕事、その対価、正式な権限へ焦点が移ることで各語義が生じる。語義5は「行為を実行する」という古くからの抽象名詞用法が犯罪などに固定した歴史的残存義で、現代の「委ねる」という核から導きにくいため個別に参照する。  "
      },
      {
        "line": 34,
        "text": "・公的な役目を集団へ委ねること → 「委員会、調査委員会、行政委員会」（語義1）  "
      },
      {
        "line": 35,
        "text": "・売買を担う人へ成果連動の対価を渡すこと → 「歩合、販売手数料」（語義2）  "
      },
      {
        "line": 36,
        "text": "・取引処理を担う業者へ対価を渡すこと → 「取扱手数料、仲介手数料」（語義3）  "
      },
      {
        "line": 37,
        "text": "・制作や調査を専門家へ正式に委ねること → 「正式な依頼、発注、依頼作品」（語義4）  "
      },
      {
        "line": 38,
        "text": "・軍務上の権限を将校へ正式に委ねること → 「士官任命、士官の地位・辞令」（語義6）  "
      },
      {
        "line": 39,
        "text": "・船舶や設備へ正式な役目を与えること → 「就役中、稼働中」（語義7）  "
      },
      {
        "line": 40,
        "text": "・制作や調査を人へ正式に委ねること → 「～を正式に依頼する、発注する」（語義8）  "
      },
      {
        "line": 41,
        "text": "・軍務上の権限を人へ正式に委ねること → 「～を士官に任命する」（語義9）  "
      },
      {
        "line": 42,
        "text": "・船舶や設備へ正式な役目を与えること → 「～を就役・稼働させる」（語義10）  "
      }
    ],
    "sense_structure": [
      {
        "line": 46,
        "text": "1. 【可算名詞】委員会、調査委員会、行政委員会"
      },
      {
        "line": 48,
        "text": "【日本語訳・定義】政府や公的機関などから、特定分野の調査、監督、規制、助言を行う正式な権限と責任を与えられた人々の組織を表す。固有の機関名では Commission と大文字で書くことがある。  "
      },
      {
        "line": 108,
        "text": "2. 【可算・不可算名詞】歩合、販売手数料"
      },
      {
        "line": 110,
        "text": "【日本語訳・定義】商品やサービスの販売、契約成立などの成果に応じて、販売員や代理人へ支払われる報酬。売上額の一定割合であることが多いが、必ず割合とは限らない。  "
      },
      {
        "line": 170,
        "text": "3. 【可算・不可算名詞】取扱手数料、仲介手数料"
      },
      {
        "line": 172,
        "text": "【日本語訳・定義】銀行、証券会社、仲介業者などが、両替、売買、送金その他の取引を処理する対価として顧客に請求する金額。取引額の一定割合の場合も定額の場合もある。  "
      },
      {
        "line": 220,
        "text": "4. 【可算名詞】正式な依頼、発注、依頼作品"
      },
      {
        "line": 222,
        "text": "【日本語訳・定義】芸術作品、建築、文章、調査などを特定の人・組織に作成・実施してもらう正式な依頼または発注。文脈によって、その依頼を受けて制作された作品や、請け負った仕事そのものも指す。  "
      },
      {
        "line": 277,
        "text": "5. 【不可算名詞・形式的】犯罪・不正行為を行うこと"
      },
      {
        "line": 279,
        "text": "【日本語訳・定義】犯罪、違反、不正行為などを実行することを表す形式的な名詞用法。通常、the commission of 〈crime/offence/act〉という固定的な形で使う。  "
      },
      {
        "line": 315,
        "text": "6. 【可算名詞・軍事】士官任命、士官の地位・辞令"
      },
      {
        "line": 317,
        "text": "【日本語訳・定義】軍で士官としての階級と権限を正式に与える任命、その地位、またはそれを証明する文書を表す。一般的な入隊や配属そのものではない。  "
      },
      {
        "line": 353,
        "text": "7. 【慣用的名詞句】就役中・稼働中／使用不能・任務不能"
      },
      {
        "line": 355,
        "text": "【日本語訳・定義】in commission は船舶・設備などが正式に就役中、または使用可能な状態にあることを表す。out of commission は就役していない、故障などで使用できない、または人が負傷・病気で一時的に活動できない状態を表す。  "
      },
      {
        "line": 412,
        "text": "8. 【他動詞】～を正式に依頼する、発注する"
      },
      {
        "line": 414,
        "text": "【日本語訳・定義】人や組織に、作品の制作、報告書・調査の作成、設計その他の専門的な仕事を正式に依頼し、実施するよう取り決める。依頼主を主語にし、人または成果物・仕事を目的語に取る。  "
      },
      {
        "line": 481,
        "text": "9. 【他動詞・通常受動・軍事】～を士官に任命する"
      },
      {
        "line": 483,
        "text": "【日本語訳・定義】軍で人を正式に士官として任官させ、階級と権限を与える。本人を主語にした受動形が特に多い。  "
      },
      {
        "line": 519,
        "text": "10. 【他動詞】船舶・設備などを就役・稼働させる"
      },
      {
        "line": 521,
        "text": "【日本語訳・定義】新しい船舶、機械、設備、システムなどについて、必要な試験・確認を経て正式に運用可能な状態へ移し、使用を開始する。船舶の正式な就役と、工学上の設備立ち上げの両方に使う。  "
      }
    ],
    "usage_notes": [
      {
        "line": 46,
        "text": "1. 【可算名詞】委員会、調査委員会、行政委員会"
      },
      {
        "line": 83,
        "text": "【語法・注意】committee は企業・学校・団体内の小委員会にも広く使うのに対し、commission は公的機関または特定の公的任務を与えられた組織に多い。ただし European Commission のように、単なる調査委員会ではなく恒常的な執行機関を指す固有名もある。  "
      },
      {
        "line": 108,
        "text": "2. 【可算・不可算名詞】歩合、販売手数料"
      },
      {
        "line": 145,
        "text": "【語法・注意】earn $2,000 in commission の in commission は得た歩合の総額を表す。一方、work on commission の on commission は報酬方式を表す。commission は bonus と異なり、通常は個々の売上・取引に直接連動する。  "
      },
      {
        "line": 170,
        "text": "3. 【可算・不可算名詞】取扱手数料、仲介手数料"
      },
      {
        "line": 202,
        "text": "【語法・注意】語義2は販売員・代理人が受け取る報酬の側から、語義3は顧客が業者へ支払う取引費用の側から捉える。実際の取引では同じ金銭を双方の立場から commission と呼ぶこともあり、誰が誰に何の対価を支払うかを確認する。  "
      },
      {
        "line": 220,
        "text": "4. 【可算名詞】正式な依頼、発注、依頼作品"
      },
      {
        "line": 252,
        "text": "【語法・注意】a commission to design は依頼された仕事をto不定詞で示し、a commission from the museum は依頼主を from で示す。語義2の on commission は報酬方式であり、take commissions for portraits の commissions は制作依頼である。  "
      },
      {
        "line": 277,
        "text": "5. 【不可算名詞・形式的】犯罪・不正行為を行うこと"
      },
      {
        "line": 304,
        "text": "【語法・注意】この語義の commission は「委員会」や「手数料」ではなく、commit「行う、犯す」に対応する行為名詞である。通常は単独で自由に使わず、the commission of の後ろに犯罪・違反・不正行為を置く。  "
      },
      {
        "line": 315,
        "text": "6. 【可算名詞・軍事】士官任命、士官の地位・辞令"
      },
      {
        "line": 342,
        "text": "【語法・注意】commissioned officer は正式な辞令によって任官した士官を指し、non-commissioned officer は下士官を指す。non-commissioned officer を「任務を与えられていない士官」と解釈してはいけない。  "
      },
      {
        "line": 353,
        "text": "7. 【慣用的名詞句】就役中・稼働中／使用不能・任務不能"
      },
      {
        "line": 385,
        "text": "【語法・注意】out of commission は必ずしも永久的な廃棄を意味せず、一時的な故障・負傷にも使う。船舶の正式な就役・退役を述べる場合は海事・軍事上の意味になり、一般の機械については「使用可能／不能」という比喩的拡張である。  "
      },
      {
        "line": 412,
        "text": "8. 【他動詞】～を正式に依頼する、発注する"
      },
      {
        "line": 449,
        "text": "【語法・注意】commission someone to do と commission something from someone は視点が異なる。前者は仕事をする人を直接目的語にし、後者は成果物を直接目的語にして制作者を from で示す。commission someone for a job は文脈によって不自然になりやすく、正式な制作依頼なら commission someone to do the work とする。  "
      },
      {
        "line": 481,
        "text": "9. 【他動詞・通常受動・軍事】～を士官に任命する"
      },
      {
        "line": 508,
        "text": "【語法・注意】この語義は単なる employ「雇う」や enlist「兵として入隊させる」と異なる。commissioned officer は士官、enlisted personnel は志願・徴募によって入隊した兵を表す。階級名の前の as は省略されることもあるが、学習者は be commissioned as a lieutenant の形を基本として覚えるとよい。  "
      },
      {
        "line": 519,
        "text": "10. 【他動詞】船舶・設備などを就役・稼働させる"
      },
      {
        "line": 551,
        "text": "【語法・注意】工学で commission は単に電源を入れることではなく、設置済み設備が設計どおり安全に作動するかを検証し、運用へ引き渡す工程を含み得る。decommission は運用から外すことで、必ずしも直ちに解体することを意味しない。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・commissioner（名詞）— 委員、行政機関などの長官、スポーツ組織の最高責任者。  "
      },
      {
        "line": 24,
        "text": "・commissioned（形容詞・過去分詞）— 正式に依頼された、または任官した。commissioned officer は「士官」。  "
      },
      {
        "line": 25,
        "text": "・commissioning（名詞・動名詞）— 発注・任命、または設備を試験して運用可能にする工程。  "
      },
      {
        "line": 26,
        "text": "・decommission（動詞）— 船舶、設備、原子力施設などを運用から外す。  "
      },
      {
        "line": 27,
        "text": "・recommission（動詞）— 運用を停止していた船舶・設備などを再び就役・稼働させる。  "
      },
      {
        "line": 28,
        "text": "・commission-free（形容詞）— 売買手数料のかからない。  "
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
  "source_artifact_sha256": "8518a3adc40ce4cbce1cb5cb38779fdae3e2432ff08a459a570ae20078ed7630",
  "normalized_input_sha256": "4b7af20ab076030f937863d93e4b062cfbfb8aa3bdf25b354d73a1cffdc9d125"
}
```
