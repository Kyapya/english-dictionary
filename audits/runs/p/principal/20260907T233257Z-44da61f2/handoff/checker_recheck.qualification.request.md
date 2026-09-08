# Independent checker recheck handoff

Stage: `checker_recheck/qualification`

Run this request in its own independent subagent/session. The seven invalidated checker passes are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `recheck/qualification.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
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
  "input_body_sha256": "2b3b6dd3f94b88f1e95996ccb124e6098140e05c5e401b90503892d4368c3fca",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "中英語・古フランス語を経て、ラテン語 *principalis*「第一の、主要な」にさかのぼる。その基になった *princeps* は、*primus*「第一の」と *capere*「取る」に関係し、「第一の位置を占める者」という発想を持つ。「重要度や責任において第一」という核が、形容詞の「主要な」、組織の長、元金、法律上の主要当事者という現代の用法につながっている。  "
      },
      {
        "line": 20,
        "text": "同語源語には `prince`「王子、君主」と `principality`「公国」がある。綴りのよく似た `principle`「原理、原則」も同じラテン語群に由来するが、現代英語では別の単語として使い分ける。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "・principally：`principal` の副詞形。  "
      },
      {
        "line": 25,
        "text": "・principalship：名詞。校長・学長など `principal` の職・地位を表す。  "
      },
      {
        "line": 26,
        "text": "・principal-agent：複合形。本人と代理人の関係を表す。  "
      }
    ],
    "sense_structure": [
      {
        "line": 41,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 43,
        "text": "【日本語訳・定義】複数の原因、目的、人物、場所、要素などの中で、重要度・影響力・順位が最も高い、または特に高いものを示す。単に時間的に最初という意味ではなく、重要性や中心性の評価を表す。  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】校長、学長、教育機関の長"
      },
      {
        "line": 128,
        "text": "【日本語訳・定義】学校、カレッジ、その他の教育機関を管理する最高責任者。どの種類の教育機関を指すかは地域と制度によって異なる。  "
      },
      {
        "line": 183,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 185,
        "text": "【日本語訳・定義】専門業務や舞台芸術などで、指導的地位または主要な役割を持つ人。企業・専門組織の上級責任者や、バレエ団・オペラ団の首席出演者、オーケストラのセクションを率いる奏者などを指す。  "
      },
      {
        "line": 240,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 242,
        "text": "【日本語訳・定義】借入・貸付の元の金額、または投資された当初の金額で、そこから生じる利息・利益・収益とは区別される金額。返済文脈では、元金への支払いは未返済債務の基礎額を減らす。個別の元本額や複数の契約上の元金を数える専門文脈では可算的にも扱われる。  "
      },
      {
        "line": 297,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 299,
        "text": "【日本語訳・定義】別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。  "
      },
      {
        "line": 356,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 358,
        "text": "【日本語訳・定義】刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。  "
      },
      {
        "line": 394,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 396,
        "text": "【日本語訳・定義】債務・保証の文脈で、保証人などの二次的責任者と対比され、義務について第一次的に責任を負う人または法人。  "
      }
    ],
    "frequency_register": [
      {
        "line": 41,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 45,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 47,
        "text": "【レジスター/領域】標準～やや形式的。報道、ビジネス、学術、行政で広く使う。日常会話では `main` がより普通なことが多い。  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】校長、学長、教育機関の長"
      },
      {
        "line": 130,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 132,
        "text": "【レジスター/領域】標準語。米国・カナダなどでは小中高校の「校長」に一般的。イギリスでは学校の長には `head teacher` または `head` が一般的で、`principal` はカレッジなど特定の教育機関の長に使われることがある。  "
      },
      {
        "line": 183,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 187,
        "text": "【頻度】〈6/10〉  "
      },
      {
        "line": 189,
        "text": "【レジスター/領域】ビジネス、コンサルティング、専門職、舞台芸術・音楽で用いる。一般会話で単に「リーダー」と言うなら `leader` や `head` のほうが普通。  "
      },
      {
        "line": 240,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 244,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 246,
        "text": "【レジスター/領域】金融、融資、投資、会計、信託。米国英語で特に一般的で、日常的なローン説明にも現れる。  "
      },
      {
        "line": 297,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 301,
        "text": "【頻度】〈5/10〉  "
      },
      {
        "line": 303,
        "text": "【レジスター/領域】法律、保険、不動産、商取引、経済学。日常語として人を「依頼主」と呼ぶだけなら `client` が自然な場合も多い。  "
      },
      {
        "line": 356,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 360,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 362,
        "text": "【レジスター/領域】刑事法の専門語。犯罪に関するこの語義は法域によって分類法が異なり、`principal in the first/second degree` はとくに歴史的なコモンロー分類として現れる。  "
      },
      {
        "line": 394,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 398,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 400,
        "text": "【レジスター/領域】債務法・保証法の専門語。  "
      }
    ],
    "usage_notes": [
      {
        "line": 41,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 78,
        "text": "【語法・注意】`principal` と `principle` は綴りも意味も異なる。前者は形容詞「主要な」または人・金額などを指す名詞、後者は名詞「原理・原則」である。したがって「基本原則」は `basic principle` であり、`basic principal` ではない。`a principal reason` は「主な理由の一つ」、`the principal reason` は通常「最も重要な理由」を表す。`principal` が常に唯一性を保証するわけではなく、`one of the principal reasons` のように複数の主要項目を認めることもできる。`principal dancer` や `principal clarinetist` では、この形容詞が人を表す名詞を修飾する。一方、名詞単独の `a principal` は語義3を参照する。  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】校長、学長、教育機関の長"
      },
      {
        "line": 158,
        "text": "【語法・注意】単数の職名として一般的に `the principal` と言えるが、補語として役職を表すときは `She became principal in 2024.` のように冠詞を省くことがある。地域によって対応する役職名が異なるため、日本語の「校長」を機械的にすべて `principal` とせず、英米差と学校種を確認する。  "
      },
      {
        "line": 183,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 215,
        "text": "【語法・注意】この語義の `principal` は、組織ごとに意味する階級・権限が異なる肩書きでもある。`a principal at a consulting firm` を必ず「社長」と訳さず、文脈に応じて「責任者」「上級職」などと訳す。`principal dancer` や `principal clarinetist` の `principal` は形容詞として人を表す名詞を修飾するため、名詞単独の `a principal` と構造を区別する。  "
      },
      {
        "line": 240,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 277,
        "text": "【語法・注意】`principal` は元の基礎額、`interest` は借入の対価または貸付・投資から生じる収益であり、同じ金額を指さない。`principal amount` や `principal balance` は、語義4の名詞が前から金額・残高の種類を限定する複合的な名詞句として扱い、`repay the principal` では `principal` 自体が目的語の名詞になる。日本語の「元利金」は `principal and interest` であり、`principal interest` とはしない。信託・遺産の文脈では、収益を生む財産本体を `principal` または `corpus` と呼び、そこから生じる `income` と区別する。この用法も「収益に対する元の財産」という同じ金融・財産上の対立に属する。  "
      },
      {
        "line": 297,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 329,
        "text": "【語法・注意】法律用語の `principal` は「重要人物」という一般義だけでなく、`agent` に対する特定の関係上の役割名である。`client` はサービスを受ける顧客・依頼人を広く指すが、必ずしも代理権を与える法律上の本人ではない。`the principal's agent` は「本人の代理人」であり、「校長の代理人」と決めつけない。  "
      },
      {
        "line": 356,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 383,
        "text": "【語法・注意】刑事法の `principal` を現代のすべての法体系で同じ範囲の「主犯」と訳すのは危険である。日常語の `ringleader` は集団を主導した人物という含みを持つが、法律上の `principal` と一致するとは限らない。債務・保証関係の第一次的責任者は別の語義7である。  "
      },
      {
        "line": 394,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 426,
        "text": "【語法・注意】この語義では、`principal` は `be liable as principal` や `recover from the principal` のように人・法人を指す名詞である。`principal debtor` や `principal obligor` では語義1の形容詞が `debtor`・`obligor` を修飾するため、名詞単独の構造と区別する。また、金額を指す語義4の「元金」とも区別する。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 41,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 51,
        "text": "【コロケーション】"
      },
      {
        "line": 53,
        "text": "・`the principal reason for ...`  "
      },
      {
        "line": 54,
        "text": "用途: 判断や行動を生じさせた最も重要な理由を示す。  "
      },
      {
        "line": 55,
        "text": "例: The principal reason for the delay was a shortage of parts.  "
      },
      {
        "line": 56,
        "text": "訳: 遅延の主な理由は部品不足だった。  "
      },
      {
        "line": 58,
        "text": "・`the principal cause of ...`  "
      },
      {
        "line": 59,
        "text": "用途: 出来事を引き起こした最も重要な原因を示す。  "
      },
      {
        "line": 60,
        "text": "例: Investigators identified corrosion as the principal cause of the failure.  "
      },
      {
        "line": 61,
        "text": "訳: 調査担当者は、腐食をその故障の主因と特定した。  "
      },
      {
        "line": 63,
        "text": "・`a principal source of ...`  "
      },
      {
        "line": 64,
        "text": "用途: 物・情報・収入などの主要な供給源を示す。  "
      },
      {
        "line": 65,
        "text": "例: Tourism is a principal source of income for the island.  "
      },
      {
        "line": 66,
        "text": "訳: 観光はその島の主要な収入源の一つである。  "
      },
      {
        "line": 68,
        "text": "・`one of the principal 〈複数名詞〉`  "
      },
      {
        "line": 69,
        "text": "用途: 最重要候補が複数ある中の一つであることを示す。  "
      },
      {
        "line": 70,
        "text": "例: She is one of the principal architects of the reform.  "
      },
      {
        "line": 71,
        "text": "訳: 彼女はその改革の主要な立案者の一人である。  "
      },
      {
        "line": 73,
        "text": "・`the principal place of business`  "
      },
      {
        "line": 74,
        "text": "用途: 企業の主たる事業所を指す定着した法律・ビジネス表現。該当場所を決める法的基準や効果は、適用される法や法域によって異なる。  "
      },
      {
        "line": 75,
        "text": "例: The company moved its principal place of business to Osaka.  "
      },
      {
        "line": 76,
        "text": "訳: その会社は主たる事業所を大阪に移した。  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】校長、学長、教育機関の長"
      },
      {
        "line": 136,
        "text": "【コロケーション】"
      },
      {
        "line": 138,
        "text": "・`the principal of 〈学校・教育機関〉`  "
      },
      {
        "line": 139,
        "text": "用途: どの教育機関の長かを `of` で示す。  "
      },
      {
        "line": 140,
        "text": "例: The principal of the college welcomed the new students.  "
      },
      {
        "line": 141,
        "text": "訳: そのカレッジの学長は新入生を歓迎した。  "
      },
      {
        "line": 143,
        "text": "・`a school principal`  "
      },
      {
        "line": 144,
        "text": "用途: 学校を管理する責任者を職種として表す。  "
      },
      {
        "line": 145,
        "text": "例: The school principal met with parents after the incident.  "
      },
      {
        "line": 146,
        "text": "訳: 校長はその出来事の後、保護者と面会した。  "
      },
      {
        "line": 148,
        "text": "・`appoint someone principal`  "
      },
      {
        "line": 149,
        "text": "用途: 人を校長・学長の職に就けることを表す。  "
      },
      {
        "line": 150,
        "text": "例: The board appointed Dr. Lee principal of the academy.  "
      },
      {
        "line": 151,
        "text": "訳: 理事会はリー博士をそのアカデミーの学長に任命した。  "
      },
      {
        "line": 153,
        "text": "・`serve as principal`  "
      },
      {
        "line": 154,
        "text": "用途: 校長・学長の職務を務めることを表す。  "
      },
      {
        "line": 155,
        "text": "例: She served as principal of the high school for twelve years.  "
      },
      {
        "line": 156,
        "text": "訳: 彼女はその高校の校長を12年間務めた。  "
      },
      {
        "line": 183,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 193,
        "text": "【コロケーション】"
      },
      {
        "line": 195,
        "text": "・`a principal at 〈会社〉`  "
      },
      {
        "line": 196,
        "text": "用途: 企業や専門サービス会社の上級責任者・共同経営者を表す。  "
      },
      {
        "line": 197,
        "text": "例: She is a principal at an engineering consultancy.  "
      },
      {
        "line": 198,
        "text": "訳: 彼女はエンジニアリング・コンサルティング会社の上級責任者である。  "
      },
      {
        "line": 200,
        "text": "・`a principal in 〈専門組織〉`  "
      },
      {
        "line": 201,
        "text": "用途: 専門組織で指導的地位にある人を表す。  "
      },
      {
        "line": 202,
        "text": "例: He works as a principal in an architecture firm.  "
      },
      {
        "line": 203,
        "text": "訳: 彼は建築事務所で上級責任者として働いている。  "
      },
      {
        "line": 205,
        "text": "・`a principal with 〈バレエ団・オペラ団〉`  "
      },
      {
        "line": 206,
        "text": "用途: バレエ団・オペラ団などで首席の地位にある出演者を名詞で表す。  "
      },
      {
        "line": 207,
        "text": "例: She was promoted to principal with the ballet company.  "
      },
      {
        "line": 208,
        "text": "訳: 彼女はそのバレエ団の首席に昇格した。  "
      },
      {
        "line": 210,
        "text": "・`the orchestra's section principals`  "
      },
      {
        "line": 211,
        "text": "用途: オーケストラの各楽器セクションの首席奏者を名詞でまとめて指す。  "
      },
      {
        "line": 212,
        "text": "例: The orchestra's section principals met before rehearsal.  "
      },
      {
        "line": 213,
        "text": "訳: そのオーケストラの各セクションの首席奏者はリハーサル前に集まった。  "
      },
      {
        "line": 240,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 250,
        "text": "【コロケーション】"
      },
      {
        "line": 252,
        "text": "・`principal and interest`  "
      },
      {
        "line": 253,
        "text": "用途: 借入金の元金と、それに対して発生する利息を対で示す。  "
      },
      {
        "line": 254,
        "text": "例: The monthly payment includes both principal and interest.  "
      },
      {
        "line": 255,
        "text": "訳: 毎月の返済額には元金と利息の両方が含まれる。  "
      },
      {
        "line": 257,
        "text": "・`pay down the principal`  "
      },
      {
        "line": 258,
        "text": "用途: 返済によって未返済の元金を減らすことを表す。  "
      },
      {
        "line": 259,
        "text": "例: Extra payments can help you pay down the principal faster.  "
      },
      {
        "line": 260,
        "text": "訳: 追加返済をすれば、元金をより早く減らせる。  "
      },
      {
        "line": 262,
        "text": "・`the principal amount`  "
      },
      {
        "line": 263,
        "text": "用途: 契約・債券・ローンで利息等を除いた基礎額を明示する。  "
      },
      {
        "line": 264,
        "text": "例: Interest is calculated on the outstanding principal amount.  "
      },
      {
        "line": 265,
        "text": "訳: 利息は未返済の元本金額に対して計算される。  "
      },
      {
        "line": 267,
        "text": "・`protect the principal`  "
      },
      {
        "line": 268,
        "text": "用途: 投資で、元本そのものの毀損を避けることを表す。  "
      },
      {
        "line": 269,
        "text": "例: The fund aims to protect the principal while generating modest returns.  "
      },
      {
        "line": 270,
        "text": "訳: そのファンドは、控えめな収益を生みながら元本を保全することを目指している。  "
      },
      {
        "line": 272,
        "text": "・`repay principal`  "
      },
      {
        "line": 273,
        "text": "用途: 利息とは別に借入の元金を返済することを表す。  "
      },
      {
        "line": 274,
        "text": "例: The borrower will begin repaying principal next year.  "
      },
      {
        "line": 275,
        "text": "訳: 借り手は来年、元金の返済を開始する。  "
      },
      {
        "line": 297,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 307,
        "text": "【コロケーション】"
      },
      {
        "line": 309,
        "text": "・`a principal-agent relationship`  "
      },
      {
        "line": 310,
        "text": "用途: 権限を与える本人と、そのために行動する代理人との関係を表す。  "
      },
      {
        "line": 311,
        "text": "例: The contract created a principal-agent relationship between the owner and the broker.  "
      },
      {
        "line": 312,
        "text": "訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。  "
      },
      {
        "line": 314,
        "text": "・`act on behalf of the principal`  "
      },
      {
        "line": 315,
        "text": "用途: 代理人が本人を代理して行動することを表す。  "
      },
      {
        "line": 316,
        "text": "例: The agent may sign the document on behalf of the principal.  "
      },
      {
        "line": 317,
        "text": "訳: 代理人は本人を代理してその書類に署名できる。  "
      },
      {
        "line": 319,
        "text": "・`owe a duty to the principal`  "
      },
      {
        "line": 320,
        "text": "用途: 代理人が本人に対して忠実義務・注意義務などを負うことを示す。  "
      },
      {
        "line": 321,
        "text": "例: An agent generally owes duties of loyalty and care to the principal.  "
      },
      {
        "line": 322,
        "text": "訳: 代理人は一般に、本人に対して忠実義務と注意義務を負う。  "
      },
      {
        "line": 324,
        "text": "・`an undisclosed principal`  "
      },
      {
        "line": 325,
        "text": "用途: 代理人が取引相手に存在または身元を明らかにしていない本人を指す。  "
      },
      {
        "line": 326,
        "text": "例: The seller later learned that the buyer had acted for an undisclosed principal.  "
      },
      {
        "line": 327,
        "text": "訳: 売主は後に、買主が非顕名の本人のために行動していたことを知った。  "
      },
      {
        "line": 356,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 366,
        "text": "【コロケーション】"
      },
      {
        "line": 368,
        "text": "・`a principal in a crime`  "
      },
      {
        "line": 369,
        "text": "用途: 犯罪について直接の刑事責任を負う者を指す。  "
      },
      {
        "line": 370,
        "text": "例: The court identified him as a principal in the crime.  "
      },
      {
        "line": 371,
        "text": "訳: 裁判所は彼をその犯罪の正犯と認定した。  "
      },
      {
        "line": 373,
        "text": "・`treat someone as a principal`  "
      },
      {
        "line": 374,
        "text": "用途: 一定の関与者を法的分類上の正犯として扱うことを表す。  "
      },
      {
        "line": 375,
        "text": "例: The statute treats a person who knowingly assists the offense as a principal.  "
      },
      {
        "line": 376,
        "text": "訳: その制定法は、情を知って犯罪を援助する者を正犯として扱う。  "
      },
      {
        "line": 378,
        "text": "・`a principal in the first degree`  "
      },
      {
        "line": 379,
        "text": "用途: 歴史的なコモンローで、第一級正犯という分類を表す。  "
      },
      {
        "line": 380,
        "text": "例: The older judgment classified the defendant as a principal in the first degree.  "
      },
      {
        "line": 381,
        "text": "訳: その古い判決は被告人を第一級正犯に分類した。  "
      },
      {
        "line": 394,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 404,
        "text": "【コロケーション】"
      },
      {
        "line": 406,
        "text": "・`be liable as principal`  "
      },
      {
        "line": 407,
        "text": "用途: 二次的な保証責任ではなく、主たる当事者として第一次的責任を負うことを示す。  "
      },
      {
        "line": 408,
        "text": "例: Under the agreement, the company remains liable as principal for the debt.  "
      },
      {
        "line": 409,
        "text": "訳: その契約の下で、会社はその債務について主たる当事者として引き続き責任を負う。  "
      },
      {
        "line": 411,
        "text": "・`the obligation of the principal`  "
      },
      {
        "line": 412,
        "text": "用途: 主たる当事者が第一次的に負う義務を示す。  "
      },
      {
        "line": 413,
        "text": "例: The guarantee does not replace the obligation of the principal.  "
      },
      {
        "line": 414,
        "text": "訳: その保証は主たる義務者の義務に取って代わるものではない。  "
      },
      {
        "line": 416,
        "text": "・`recover from the principal`  "
      },
      {
        "line": 417,
        "text": "用途: 保証人などが支払い後に主たる義務者へ償還を求めることを表す。  "
      },
      {
        "line": 418,
        "text": "例: After payment, the surety sought to recover from the principal.  "
      },
      {
        "line": 419,
        "text": "訳: 支払い後、保証人は主たる義務者からの償還を求めた。  "
      },
      {
        "line": 421,
        "text": "・`the principal and the surety`  "
      },
      {
        "line": 422,
        "text": "用途: 第一次的責任を負う当事者と、保証する側を対で示す。  "
      },
      {
        "line": 423,
        "text": "例: The agreement states the duties of the principal and the surety.  "
      },
      {
        "line": 424,
        "text": "訳: その契約は主たる義務者と保証人の義務を定めている。  "
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
  "specification_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
  "source_artifact_sha256": "aa1779766eda8637c5e7e020ab81117c845bedfb53b9b4eeae14ec9df7732826",
  "normalized_input_sha256": "6231f25f1e4f159f18054692be7abb0c98bc659cba7de0f2fcfdc8fbcd43fb41"
}
```
