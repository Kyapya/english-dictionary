# Independent checker handoff

Stage: `checker_passes/qualification`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

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
  "input_body_sha256": "ab4f5e80d9bb3a91810ed5a9de22c2f3e3430a454ff6635d6a94a701f2ae9fe4",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "中英語・古フランス語を経て、ラテン語 *principalis*「第一の、主要な」にさかのぼる。その基になった *princeps* は、*primus*「第一の」と *capere*「取る」に関係し、「第一の位置を占める者」という発想を持つ。語源には「第一の、主要な」という意味的なつながりがある。  "
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
        "text": "・principalship：`principal` の名詞派生形。  "
      },
      {
        "line": 26,
        "text": "・principal-agent relationship：法律上の本人・代理人関係を表す複合表現。  "
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
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 128,
        "text": "【日本語訳・定義】組織で支配的権限または主導的地位を持つ人。特に、学校、カレッジ、その他の教育機関を管理する最高責任者を指す。教育上どの種類の機関を指すかは地域と制度によって異なる。  "
      },
      {
        "line": 164,
        "text": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 166,
        "text": "【日本語訳・定義】借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。信託法では、収益と区別される信託財産そのもの、すなわち信託元本・corpusを指す。  "
      },
      {
        "line": 207,
        "text": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 209,
        "text": "【日本語訳・定義】別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。具体的な成立要件は適用法によって異なり得る。  "
      },
      {
        "line": 240,
        "text": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 242,
        "text": "【日本語訳・定義】舞台芸術で主要な役を担う演者、またはオーケストラで一つのセクションを率いる奏者。一般の重要人物ではなく、芸術分野で確立した役割名を指す。  "
      },
      {
        "line": 268,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 270,
        "text": "【日本語訳・定義】刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。  "
      },
      {
        "line": 301,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 303,
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
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 130,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 132,
        "text": "【レジスター/領域】標準～やや形式的。教育分野では学校・教育機関の長を表し、イングランドではカレッジの長を指す場合がある。  "
      },
      {
        "line": 164,
        "text": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 168,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 170,
        "text": "【レジスター/領域】金融、融資、投資、会計、信託法。金融義は日常的なローン説明にも現れ、信託義は専門的である。  "
      },
      {
        "line": 207,
        "text": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 211,
        "text": "【頻度】〈5/10〉  "
      },
      {
        "line": 213,
        "text": "【レジスター/領域】法律、保険、不動産、商取引。日常語として人を「依頼主」と呼ぶだけなら `client` が自然な場合も多い。  "
      },
      {
        "line": 240,
        "text": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 244,
        "text": "【頻度】〈3/10〉  "
      },
      {
        "line": 246,
        "text": "【レジスター/領域】舞台芸術・オーケストラ・音楽の専門語。  "
      },
      {
        "line": 268,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 272,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 274,
        "text": "【レジスター/領域】刑事法の専門語。犯罪に関するこの語義は法域によって分類法が異なる。  "
      },
      {
        "line": 301,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 305,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 307,
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
        "text": "【語法・注意】`principal` と `principle` は綴りも意味も異なる。`principal` には形容詞で「最も重要な」を表す用法があり、別に人や金額などを指す名詞用法もある。一方、`principle` は「原理・原則」を表す名詞である。したがって「基本原則」は `basic principle` であり、`basic principal` ではない。  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 153,
        "text": "【語法・注意】一般の「重要人物」を自由に指す語ではなく、権限や主導的地位が文脈上確立した人に用いる。教育上の役職名は地域や制度によって異なるため、日本語の「校長」を機械的にすべて `principal` としない。  "
      },
      {
        "line": 164,
        "text": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 196,
        "text": "【語法・注意】`principal` は元の基礎額、`interest` は借入の対価または貸付・投資から生じる追加額であり、反意語ではなく関連する別の金額構成要素である。信託では `principal` が財産本体、`income` がそこから生じる収益を指す。`repay the principal` では `principal` 自体が目的語の名詞になる。日本語の「元利金」は `principal and interest` であり、`principal interest` とはしない。  "
      },
      {
        "line": 207,
        "text": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 229,
        "text": "【語法・注意】法律用語の `principal` は「重要人物」という一般義だけでなく、`agent` に対する特定の関係上の役割名である。`client` はサービスを受ける顧客・依頼人を広く指すが、必ずしも代理権を与える法律上の本人ではない。`the principal's agent` は「本人の代理人」であり、「校長の代理人」と決めつけない。  "
      },
      {
        "line": 240,
        "text": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 257,
        "text": "【語法・注意】舞台芸術やオーケストラ内で確立した役割名として用い、一般の「重要人物」には広げない。  "
      },
      {
        "line": 268,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 290,
        "text": "【語法・注意】刑事法の `principal` は適用される法的分類に従う役割名で、`accessory` と対比される。債務・保証関係の第一次的責任者は別の語義7である。  "
      },
      {
        "line": 301,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 328,
        "text": "【語法・注意】この語義では、`principal` は `be liable as principal` のように人・法人を指す名詞である。`principal debtor` や `principal obligor` では語義1の形容詞が `debtor`・`obligor` を修飾するため、名詞単独の構造と区別する。また、金額を指す語義3の「元金」とも区別する。  "
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
        "text": "用途: 出来事・状況・判断・行動などについて、最も重要な理由を示す。  "
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
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 136,
        "text": "【コロケーション】"
      },
      {
        "line": 138,
        "text": "・`the principal of 〈限定詞を含む学校・教育機関の名詞句〉`  "
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
        "text": "・`a college principal`  "
      },
      {
        "line": 149,
        "text": "用途: カレッジを管理する責任者を職種として表す。  "
      },
      {
        "line": 150,
        "text": "例: A college principal addressed the graduating class.  "
      },
      {
        "line": 151,
        "text": "訳: カレッジの学長が卒業生に向けて話した。  "
      },
      {
        "line": 164,
        "text": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 174,
        "text": "【コロケーション】"
      },
      {
        "line": 176,
        "text": "・`principal and interest`  "
      },
      {
        "line": 177,
        "text": "用途: 借入金の元金と、それに対して発生する利息を対で示す。  "
      },
      {
        "line": 178,
        "text": "例: The monthly payment includes both principal and interest.  "
      },
      {
        "line": 179,
        "text": "訳: 毎月の返済額には元金と利息の両方が含まれる。  "
      },
      {
        "line": 181,
        "text": "・`pay down the principal`  "
      },
      {
        "line": 182,
        "text": "用途: 返済によって未返済の元金を減らすことを表す。  "
      },
      {
        "line": 183,
        "text": "例: Extra payments can help you pay down the principal faster.  "
      },
      {
        "line": 184,
        "text": "訳: 追加返済をすれば、元金をより早く減らせる。  "
      },
      {
        "line": 186,
        "text": "・`protect the principal`  "
      },
      {
        "line": 187,
        "text": "用途: 投資で、元本そのものの毀損を避けることを表す。  "
      },
      {
        "line": 188,
        "text": "例: The fund aims to protect the principal—the amount originally invested—while generating modest returns.  "
      },
      {
        "line": 189,
        "text": "訳: そのファンドは、控えめな収益を生みながら元本、すなわち当初の投資額を保全することを目指している。  "
      },
      {
        "line": 191,
        "text": "・`repay principal`  "
      },
      {
        "line": 192,
        "text": "用途: 利息とは別に借入の元金を返済することを表す。  "
      },
      {
        "line": 193,
        "text": "例: The borrower will begin repaying principal next year.  "
      },
      {
        "line": 194,
        "text": "訳: 借り手は来年、元金の返済を開始する。  "
      },
      {
        "line": 207,
        "text": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 217,
        "text": "【コロケーション】"
      },
      {
        "line": 219,
        "text": "・`a principal-agent relationship`  "
      },
      {
        "line": 220,
        "text": "用途: 権限を与える本人と、そのために行動する代理人との関係を表す。  "
      },
      {
        "line": 221,
        "text": "例: The contract created a principal-agent relationship between the owner and the broker.  "
      },
      {
        "line": 222,
        "text": "訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。  "
      },
      {
        "line": 224,
        "text": "・`act on behalf of the principal`  "
      },
      {
        "line": 225,
        "text": "用途: 代理人が本人を代理して行動することを表す。  "
      },
      {
        "line": 226,
        "text": "例: The agent may sign the document on behalf of the principal.  "
      },
      {
        "line": 227,
        "text": "訳: 代理人は本人を代理してその書類に署名できる。  "
      },
      {
        "line": 240,
        "text": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 250,
        "text": "【コロケーション】"
      },
      {
        "line": 252,
        "text": "・`one of the orchestra's principals`  "
      },
      {
        "line": 253,
        "text": "用途: オーケストラで各セクションを率いる奏者を名詞で指す。  "
      },
      {
        "line": 254,
        "text": "例: As one of the orchestra's principals, she leads the cello section.  "
      },
      {
        "line": 255,
        "text": "訳: オーケストラの首席奏者の一人として、彼女はチェロのセクションを率いている。  "
      },
      {
        "line": 268,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 278,
        "text": "【コロケーション】"
      },
      {
        "line": 280,
        "text": "・`a principal in a crime`  "
      },
      {
        "line": 281,
        "text": "用途: 犯罪について直接の刑事責任を負う者を指す。  "
      },
      {
        "line": 282,
        "text": "例: The court identified him as a principal in the crime.  "
      },
      {
        "line": 283,
        "text": "訳: 裁判所は彼をその犯罪について `principal` に当たる者と認定した。  "
      },
      {
        "line": 285,
        "text": "・`treat someone as a principal`  "
      },
      {
        "line": 286,
        "text": "用途: 一定の関与者を適用法上 `principal` として扱うことを表す。  "
      },
      {
        "line": 287,
        "text": "例: The statute treats a person who knowingly assists the offense as a principal.  "
      },
      {
        "line": 288,
        "text": "訳: その制定法は、情を知って犯罪を援助する者を `principal` として扱う。  "
      },
      {
        "line": 301,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 311,
        "text": "【コロケーション】"
      },
      {
        "line": 313,
        "text": "・`be liable as principal`  "
      },
      {
        "line": 314,
        "text": "用途: 二次的な保証責任ではなく、主たる当事者として第一次的責任を負うことを示す。  "
      },
      {
        "line": 315,
        "text": "例: Under the agreement, the company remains liable as principal for the debt, while the guarantor is only secondarily liable.  "
      },
      {
        "line": 316,
        "text": "訳: その契約の下で、会社はその債務について主たる当事者として引き続き責任を負い、保証人は二次的にのみ責任を負う。  "
      },
      {
        "line": 318,
        "text": "・`the obligation of the principal`  "
      },
      {
        "line": 319,
        "text": "用途: 主たる当事者が第一次的に負う義務を示す。  "
      },
      {
        "line": 320,
        "text": "例: The obligation of the principal is to repay the debt; the guarantor is only secondarily liable.  "
      },
      {
        "line": 321,
        "text": "訳: 主たる義務者の義務は債務を返済することであり、保証人は二次的にのみ責任を負う。  "
      },
      {
        "line": 323,
        "text": "・`the principal and the surety`  "
      },
      {
        "line": 324,
        "text": "用途: 第一次的責任を負う当事者と、保証する側を対で示す。  "
      },
      {
        "line": 325,
        "text": "例: Under the agreement, the principal and the surety are primarily and secondarily liable for the debt, respectively.  "
      },
      {
        "line": 326,
        "text": "訳: その契約の下で、主たる義務者と保証人は、その債務についてそれぞれ第一次的責任と二次的責任を負う。  "
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
  "source_artifact_sha256": "566785426a568ff079817e5fc120efa9cd081fc11eebe5f3170c5e6a910b890c",
  "normalized_input_sha256": "1568e5008fd02aa3d1136f18139613e5506feae31d424826549cb2d634eac7a0"
}
```
