# Independent checker recheck handoff

Stage: `checker_recheck/round2/evidence`

Run this request in its own independent subagent/session. The seven invalidated checker passes are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `recheck/round2/evidence.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id. For `frame-relation`, this is stage 1; the same reviewer identity and model must continue to its stage-2 reconciliation request.
## Prompt

# check_pass_evidence_v6

## 目的

主張単位の根拠リンクが、対象主張を直接支持するかだけを検査する。source-first工程との二重チェックを避けるため、このパスは資料探索計画、source inventoryのcoverage、fact収集をやり直さない。

## 担当タクソノミー分類

- `evidence_claim_mismatch`

## 検査ルール

- source-first工程が固定したsource・fact・claim unit・対象sectionを入力として受け、claimと引用位置または忠実な要約の対応を確認する。
- 入力は `evidence_context_v1` とし、対象claimに関係するsource、fact、source union、claim unit、`source_supports` だけを含む。`source_inventory_sha256`、`source_first_artifact_sha256`、本文hashの一致を機械検証済みでなければ開始しない。
- source-first artifactが欠落、未完了、schema不正、参照切れ、本文hash不一致の場合はfail closedとし、再探索やfact追加で補わない。
- 資料名や検索結果見出しが存在するだけで合格にせず、locator、該当箇所、支持内容、当該語義・構文への適用範囲を確認する。
- 別義、別品詞、別法域、別地域、別時代の記述を現在の対象主張へ流用しない。
- 高リスク主張に `two_sources_or_primary` が指定される場合、同一引用元を別IDにした重複を独立2資料として数えない。一次資料1件を使う場合は当該主張へ直接適用できることを確認する。
- 発音、語源、語義境界、文法制約、完全フレーム、例文の自然さ、絶対表現、地域差、頻度、専門説明、類義語・反意語差のevidence linkを個別に確認する。
- 断定的主張では支持例だけでなく、source-first記録にある反例・矛盾探索の方法と結果が主張範囲に対応するか確認する。
- 資料が食い違う場合、本文が差を反映して範囲を限定しているかを確認する。根拠から決められない内容をpassにしない。
- このパスはclaimの辞書学的正しさを他パスの代わりに再判定せず、「提示された根拠がそのclaimを支えるか」に限定する。

## 入力として受け取るセクション

- `pronunciation`
- `etymology`
- `word_formation`
- `core_image`
- `sense_structure`
- `frequency_register`
- `frames`
- `collocations_examples`
- `usage_notes`
- `lexical_relations`
- source-first工程が生成したsource inventory、fact、claim unit、evidence link
- API modeとhandoff modeはいずれも `scripts/check_passes.py` が生成した同一の正規化requestを使う。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "evidence_claim_mismatch",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "根拠対象となる本文主張"
  },
  "severity": "blocking | minor",
  "rationale": "source locator・支持内容・適用範囲の不一致",
  "evidence_link_ids": ["問題のある既存link ID"],
  "suggested_direction": "主張限定、根拠差替え、holdの方向"
}
```

根拠が主張を支持しない状態は原則 `blocking` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "evidence",
  "taxonomy_ids": [
    "evidence_claim_mismatch"
  ],
  "specification": "prompts/check_pass_evidence_v6.md",
  "input_body_sha256": "a90e8ce4e9b278894c354be6358063e378816073104700b90e9a801635efff87",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "発音: /ˈprɪnsəpəl/。形容詞と名詞で同じ発音を用いる。  "
      }
    ],
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
        "text": "・principalship：`principal` の名詞派生形。  "
      },
      {
        "line": 26,
        "text": "・principal-agent relationship：本人・代理人関係を表す複合表現。  "
      }
    ],
    "core_image": [
      {
        "line": 28,
        "text": "＃コアイメージ"
      },
      {
        "line": 30,
        "text": "`principal` の中心は、「重要度・権限・責任・金額の土台として第一に位置する」である。形容詞では主要なものを選び出し、名詞では組織や行為の中心人物、利息に対する元の金額、代理関係などの主要当事者を指す。  "
      },
      {
        "line": 31,
        "text": "・重要度で第一に位置するもの → 「主要な、最も重要な」（語義1）  "
      },
      {
        "line": 32,
        "text": "・学校組織の権限で第一に位置する人 → 「校長、学長」（語義2）  "
      },
      {
        "line": 33,
        "text": "・活動・組織内の地位で第一に位置する人 → 「責任者、中心人物、首席」（語義3）  "
      },
      {
        "line": 34,
        "text": "・利息・収益の土台として第一に置かれた金額 → 「元金、元本」（語義4）  "
      },
      {
        "line": 35,
        "text": "・代理関係で権限の源として第一に位置する当事者 → 「本人、依頼者」（語義5）  "
      },
      {
        "line": 36,
        "text": "・犯罪について主要な刑事責任を負う者 → 「正犯、犯罪の主要関与者」（語義6）  "
      },
      {
        "line": 37,
        "text": "・債務・保証関係で第一次的責任を負う者 → 「主たる債務者・義務者」（語義7）  "
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
        "line": 178,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 180,
        "text": "【日本語訳・定義】専門業務や舞台芸術などで、指導的地位または主要な役割を持つ人。企業・専門組織の上級責任者や、バレエ団・オペラ団の首席出演者、オーケストラのセクションを率いる奏者などを指す。  "
      },
      {
        "line": 235,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 237,
        "text": "【日本語訳・定義】借入・貸付の元の金額、または投資された当初の金額で、そこから生じる利息・利益・収益とは区別される金額。返済文脈では、元金への支払いは未返済債務の基礎額を減らす。個別の元本額や複数の契約上の元金を数える専門文脈では可算的にも扱われる。  "
      },
      {
        "line": 292,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 294,
        "text": "【日本語訳・定義】別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。  "
      },
      {
        "line": 346,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 348,
        "text": "【日本語訳・定義】刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。  "
      },
      {
        "line": 384,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 386,
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
        "line": 178,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 182,
        "text": "【頻度】〈6/10〉  "
      },
      {
        "line": 184,
        "text": "【レジスター/領域】ビジネス、コンサルティング、専門職、舞台芸術・音楽で用いる。一般会話で単に「リーダー」と言うなら `leader` や `head` のほうが普通。  "
      },
      {
        "line": 235,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 239,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 241,
        "text": "【レジスター/領域】金融、融資、投資、会計、信託。米国英語で特に一般的で、日常的なローン説明にも現れる。  "
      },
      {
        "line": 292,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 296,
        "text": "【頻度】〈5/10〉  "
      },
      {
        "line": 298,
        "text": "【レジスター/領域】法律、保険、不動産、商取引、経済学。日常語として人を「依頼主」と呼ぶだけなら `client` が自然な場合も多い。  "
      },
      {
        "line": 346,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 350,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 352,
        "text": "【レジスター/領域】刑事法の専門語。犯罪に関するこの語義は法域によって分類法が異なり、`principal in the first/second degree` はとくに歴史的なコモンロー分類として現れる。  "
      },
      {
        "line": 384,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 388,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 390,
        "text": "【レジスター/領域】債務法・保証法の専門語。  "
      }
    ],
    "frames": [
      {
        "line": 41,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 49,
        "text": "【文法パターン】`the principal 〈名詞〉`＝主要な～／`a principal 〈名詞〉`＝主な～の一つ／`one of the principal 〈複数名詞〉`＝主要な～の一つ／`the principal cause of ...`＝～の主因／`a principal source of ...`＝～の主要源の一つ／`the principal reason for ...`＝～の主な理由  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】校長、学長、教育機関の長"
      },
      {
        "line": 134,
        "text": "【文法パターン】`the principal of 〈学校・教育機関〉`＝～の校長・学長／`a school principal`＝学校の校長／`a college principal`＝カレッジの学長  "
      },
      {
        "line": 178,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 186,
        "text": "【文法パターン】`a principal at/in 〈会社・組織〉`＝会社・組織の上級責任者／`a principal with 〈バレエ団・オペラ団〉`＝その団体の首席出演者／`the orchestra's section principals`＝オーケストラの各セクションの首席奏者  "
      },
      {
        "line": 235,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 243,
        "text": "【文法パターン】`pay/repay 〈金額〉 of principal`＝元金を～返済する／`pay down/reduce the principal`＝元金を減らす／`principal and interest`＝元利金／`the principal on a loan`＝ローンの元金／`an outstanding principal balance`＝未返済元金残高／`the principal amount`＝元本金額  "
      },
      {
        "line": 292,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 300,
        "text": "【文法パターン】`a principal appoints/authorizes an agent to do ...`＝本人が代理人に～する権限を与える／`act on behalf of the principal`＝本人を代理して行動する／`owe a duty to the principal`＝本人に対して義務を負う／`a principal-agent relationship`＝本人・代理人関係  "
      },
      {
        "line": 346,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 354,
        "text": "【文法パターン】`a principal in a crime`＝犯罪の正犯・主要関与者／`treat someone as a principal`＝人を正犯として扱う／`a principal in the first/second degree`＝第一級・第二級正犯  "
      },
      {
        "line": 384,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 392,
        "text": "【文法パターン】`be liable as principal`＝主たる当事者として責任を負う／`the obligation of the principal`＝主たる義務者の義務／`the principal and the surety`＝主たる義務者と保証人  "
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
        "line": 178,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 188,
        "text": "【コロケーション】"
      },
      {
        "line": 190,
        "text": "・`a principal at 〈会社〉`  "
      },
      {
        "line": 191,
        "text": "用途: 企業や専門サービス会社の上級責任者・共同経営者を表す。  "
      },
      {
        "line": 192,
        "text": "例: She is a principal at an engineering consultancy.  "
      },
      {
        "line": 193,
        "text": "訳: 彼女はエンジニアリング・コンサルティング会社の上級責任者である。  "
      },
      {
        "line": 195,
        "text": "・`a principal in 〈専門組織〉`  "
      },
      {
        "line": 196,
        "text": "用途: 専門組織で指導的地位にある人を表す。  "
      },
      {
        "line": 197,
        "text": "例: He works as a principal in an architecture firm.  "
      },
      {
        "line": 198,
        "text": "訳: 彼は建築事務所で上級責任者として働いている。  "
      },
      {
        "line": 200,
        "text": "・`a principal with 〈バレエ団・オペラ団〉`  "
      },
      {
        "line": 201,
        "text": "用途: バレエ団・オペラ団などで首席の地位にある出演者を名詞で表す。  "
      },
      {
        "line": 202,
        "text": "例: She was promoted to principal with the ballet company.  "
      },
      {
        "line": 203,
        "text": "訳: 彼女はそのバレエ団の首席に昇格した。  "
      },
      {
        "line": 205,
        "text": "・`the orchestra's section principals`  "
      },
      {
        "line": 206,
        "text": "用途: オーケストラの各楽器セクションの首席奏者を名詞でまとめて指す。  "
      },
      {
        "line": 207,
        "text": "例: The orchestra's section principals met before rehearsal.  "
      },
      {
        "line": 208,
        "text": "訳: そのオーケストラの各セクションの首席奏者はリハーサル前に集まった。  "
      },
      {
        "line": 235,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 245,
        "text": "【コロケーション】"
      },
      {
        "line": 247,
        "text": "・`principal and interest`  "
      },
      {
        "line": 248,
        "text": "用途: 借入金の元金と、それに対して発生する利息を対で示す。  "
      },
      {
        "line": 249,
        "text": "例: The monthly payment includes both principal and interest.  "
      },
      {
        "line": 250,
        "text": "訳: 毎月の返済額には元金と利息の両方が含まれる。  "
      },
      {
        "line": 252,
        "text": "・`pay down the principal`  "
      },
      {
        "line": 253,
        "text": "用途: 返済によって未返済の元金を減らすことを表す。  "
      },
      {
        "line": 254,
        "text": "例: Extra payments can help you pay down the principal faster.  "
      },
      {
        "line": 255,
        "text": "訳: 追加返済をすれば、元金をより早く減らせる。  "
      },
      {
        "line": 257,
        "text": "・`the principal amount`  "
      },
      {
        "line": 258,
        "text": "用途: 契約・債券・ローンで利息等を除いた基礎額を明示する。  "
      },
      {
        "line": 259,
        "text": "例: Interest is calculated on the outstanding principal amount.  "
      },
      {
        "line": 260,
        "text": "訳: 利息は未返済の元本金額に対して計算される。  "
      },
      {
        "line": 262,
        "text": "・`protect the principal`  "
      },
      {
        "line": 263,
        "text": "用途: 投資で、元本そのものの毀損を避けることを表す。  "
      },
      {
        "line": 264,
        "text": "例: The fund aims to protect the principal while generating modest returns.  "
      },
      {
        "line": 265,
        "text": "訳: そのファンドは、控えめな収益を生みながら元本を保全することを目指している。  "
      },
      {
        "line": 267,
        "text": "・`repay principal`  "
      },
      {
        "line": 268,
        "text": "用途: 利息とは別に借入の元金を返済することを表す。  "
      },
      {
        "line": 269,
        "text": "例: The borrower will begin repaying principal next year.  "
      },
      {
        "line": 270,
        "text": "訳: 借り手は来年、元金の返済を開始する。  "
      },
      {
        "line": 292,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 302,
        "text": "【コロケーション】"
      },
      {
        "line": 304,
        "text": "・`a principal-agent relationship`  "
      },
      {
        "line": 305,
        "text": "用途: 権限を与える本人と、そのために行動する代理人との関係を表す。  "
      },
      {
        "line": 306,
        "text": "例: The contract created a principal-agent relationship between the owner and the broker.  "
      },
      {
        "line": 307,
        "text": "訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。  "
      },
      {
        "line": 309,
        "text": "・`act on behalf of the principal`  "
      },
      {
        "line": 310,
        "text": "用途: 代理人が本人を代理して行動することを表す。  "
      },
      {
        "line": 311,
        "text": "例: The agent may sign the document on behalf of the principal.  "
      },
      {
        "line": 312,
        "text": "訳: 代理人は本人を代理してその書類に署名できる。  "
      },
      {
        "line": 314,
        "text": "・`owe a duty to the principal`  "
      },
      {
        "line": 315,
        "text": "用途: 代理人が本人に対して忠実義務・注意義務などを負うことを示す。  "
      },
      {
        "line": 316,
        "text": "例: An agent generally owes duties of loyalty and care to the principal.  "
      },
      {
        "line": 317,
        "text": "訳: 代理人は一般に、本人に対して忠実義務と注意義務を負う。  "
      },
      {
        "line": 346,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 356,
        "text": "【コロケーション】"
      },
      {
        "line": 358,
        "text": "・`a principal in a crime`  "
      },
      {
        "line": 359,
        "text": "用途: 犯罪について直接の刑事責任を負う者を指す。  "
      },
      {
        "line": 360,
        "text": "例: The court identified him as a principal in the crime.  "
      },
      {
        "line": 361,
        "text": "訳: 裁判所は彼をその犯罪の正犯と認定した。  "
      },
      {
        "line": 363,
        "text": "・`treat someone as a principal`  "
      },
      {
        "line": 364,
        "text": "用途: 一定の関与者を法的分類上の正犯として扱うことを表す。  "
      },
      {
        "line": 365,
        "text": "例: The statute treats a person who knowingly assists the offense as a principal.  "
      },
      {
        "line": 366,
        "text": "訳: その制定法は、情を知って犯罪を援助する者を正犯として扱う。  "
      },
      {
        "line": 368,
        "text": "・`a principal in the first degree`  "
      },
      {
        "line": 369,
        "text": "用途: 歴史的なコモンローで、第一級正犯という分類を表す。  "
      },
      {
        "line": 370,
        "text": "例: The older judgment classified the defendant as a principal in the first degree.  "
      },
      {
        "line": 371,
        "text": "訳: その古い判決は被告人を第一級正犯に分類した。  "
      },
      {
        "line": 384,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 394,
        "text": "【コロケーション】"
      },
      {
        "line": 396,
        "text": "・`be liable as principal`  "
      },
      {
        "line": 397,
        "text": "用途: 二次的な保証責任ではなく、主たる当事者として第一次的責任を負うことを示す。  "
      },
      {
        "line": 398,
        "text": "例: Under the agreement, the company remains liable as principal for the debt.  "
      },
      {
        "line": 399,
        "text": "訳: その契約の下で、会社はその債務について主たる当事者として引き続き責任を負う。  "
      },
      {
        "line": 401,
        "text": "・`the obligation of the principal`  "
      },
      {
        "line": 402,
        "text": "用途: 主たる当事者が第一次的に負う義務を示す。  "
      },
      {
        "line": 403,
        "text": "例: The guarantee does not replace the obligation of the principal.  "
      },
      {
        "line": 404,
        "text": "訳: その保証は主たる義務者の義務に取って代わるものではない。  "
      },
      {
        "line": 406,
        "text": "・`the principal and the surety`  "
      },
      {
        "line": 407,
        "text": "用途: 第一次的責任を負う当事者と、保証する側を対で示す。  "
      },
      {
        "line": 408,
        "text": "例: The agreement states the duties of the principal and the surety.  "
      },
      {
        "line": 409,
        "text": "訳: その契約は主たる義務者と保証人の義務を定めている。  "
      }
    ],
    "usage_notes": [
      {
        "line": 41,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 78,
        "text": "【語法・注意】`principal` と `principle` は綴りも意味も異なる。前者は形容詞「主要な」または人・金額などを指す名詞、後者は名詞「原理・原則」である。したがって「基本原則」は `basic principle` であり、`basic principal` ではない。`a principal reason` は「主な理由の一つ」、`the principal reason` は通常「最も重要な理由」を表す。`principal` が常に唯一性を保証するわけではなく、`one of the principal reasons` のように複数の主要項目を認めることもできる。`principal dancer` や `principal clarinetist` では、この形容詞が人を表す名詞を修飾する。専門職・舞台芸術の当該文脈で名詞単独の `a principal` と言う場合は語義3を参照し、ほかの名詞語義は文脈で判別する。  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】校長、学長、教育機関の長"
      },
      {
        "line": 153,
        "text": "【語法・注意】地域によって対応する役職名が異なるため、日本語の「校長」を機械的にすべて `principal` とせず、英米差と学校種を確認する。  "
      },
      {
        "line": 178,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 210,
        "text": "【語法・注意】この語義の `principal` は、組織ごとに意味する階級・権限が異なる肩書きでもある。`a principal at a consulting firm` を必ず「社長」と訳さず、文脈に応じて「責任者」「上級職」などと訳す。`principal dancer` や `principal clarinetist` の `principal` は形容詞として人を表す名詞を修飾するため、名詞単独の `a principal` と構造を区別する。  "
      },
      {
        "line": 235,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 272,
        "text": "【語法・注意】`principal` は元の基礎額、`interest` は借入の対価または貸付・投資から生じる収益であり、同じ金額を指さない。`principal amount` や `principal balance` は、語義4の名詞が前から金額・残高の種類を限定する複合的な名詞句として扱い、`repay the principal` では `principal` 自体が目的語の名詞になる。日本語の「元利金」は `principal and interest` であり、`principal interest` とはしない。信託・遺産の文脈では、収益を生む財産本体を `principal` または `corpus` と呼び、そこから生じる `income` と区別する。この用法も「収益に対する元の財産」という同じ金融・財産上の対立に属する。  "
      },
      {
        "line": 292,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 319,
        "text": "【語法・注意】法律用語の `principal` は「重要人物」という一般義だけでなく、`agent` に対する特定の関係上の役割名である。`client` はサービスを受ける顧客・依頼人を広く指すが、必ずしも代理権を与える法律上の本人ではない。`the principal's agent` は「本人の代理人」であり、「校長の代理人」と決めつけない。  "
      },
      {
        "line": 346,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 373,
        "text": "【語法・注意】刑事法の `principal` を現代のすべての法体系で同じ範囲の「主犯」と訳すのは危険である。日常語の `ringleader` は集団を主導した人物という含みを持つが、法律上の `principal` と一致するとは限らない。債務・保証関係の第一次的責任者は別の語義7である。  "
      },
      {
        "line": 384,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 411,
        "text": "【語法・注意】この語義では、`principal` は `be liable as principal` のように人・法人を指す名詞である。`principal debtor` や `principal obligor` では語義1の形容詞が `debtor`・`obligor` を修飾するため、名詞単独の構造と区別する。また、金額を指す語義4の「元金」とも区別する。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 41,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 80,
        "text": "【類義語】"
      },
      {
        "line": 82,
        "text": "・main  "
      },
      {
        "line": 83,
        "text": "定義: 複数のものの中で中心的・最重要である。  "
      },
      {
        "line": 84,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 85,
        "text": "違い: `main` は日常語で範囲が広い。`principal` はより形式的で、順位・重要性・影響力が高いことを意識させる。  "
      },
      {
        "line": 86,
        "text": "例: Our main goal is to reduce waiting times.  "
      },
      {
        "line": 87,
        "text": "訳: 私たちの主な目標は待ち時間を減らすことだ。  "
      },
      {
        "line": 89,
        "text": "・primary  "
      },
      {
        "line": 90,
        "text": "定義: 第一順位・第一段階である、または最も基本的である。  "
      },
      {
        "line": 91,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 92,
        "text": "違い: `primary` は重要性に加え、順序・段階・基本性にも焦点を置ける。`principal` は主として相対的な重要度や地位を表す。  "
      },
      {
        "line": 93,
        "text": "例: Safety is our primary concern.  "
      },
      {
        "line": 94,
        "text": "訳: 安全が私たちの最優先事項である。  "
      },
      {
        "line": 96,
        "text": "・chief  "
      },
      {
        "line": 97,
        "text": "定義: 同種の中で最上位・最重要である。  "
      },
      {
        "line": 98,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 99,
        "text": "違い: `chief` は役職名や「最大の原因・懸念」によく使われ、最上位性を強く示す。`principal` は文章語として原因・目的・人物・場所などに幅広く使う。  "
      },
      {
        "line": 100,
        "text": "例: Cost remains the chief obstacle to expansion.  "
      },
      {
        "line": 101,
        "text": "訳: 費用が依然として拡大の最大の障害である。  "
      },
      {
        "line": 103,
        "text": "・leading  "
      },
      {
        "line": 104,
        "text": "定義: ある分野で先頭に立ち、大きな影響力や高い評価を持つ。  "
      },
      {
        "line": 105,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 106,
        "text": "違い: `leading` は人・企業・研究機関などの実績や影響力を強調しやすい。`principal` は実績評価を必須とせず、対象内での中心性を示す。  "
      },
      {
        "line": 107,
        "text": "例: She is a leading expert on marine ecosystems.  "
      },
      {
        "line": 108,
        "text": "訳: 彼女は海洋生態系の第一人者である。  "
      },
      {
        "line": 110,
        "text": "【反意語】"
      },
      {
        "line": 112,
        "text": "・secondary  "
      },
      {
        "line": 113,
        "text": "定義: 第一ではなく、重要度・順位が二次的である。  "
      },
      {
        "line": 114,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 115,
        "text": "違い: 重要度・順位の軸で `principal` と方向が反対になり、主要なものに対する従属的・補助的なものを表す。  "
      },
      {
        "line": 116,
        "text": "例: Price was only a secondary consideration.  "
      },
      {
        "line": 117,
        "text": "訳: 価格は二次的な考慮事項にすぎなかった。  "
      },
      {
        "line": 119,
        "text": "・minor  "
      },
      {
        "line": 120,
        "text": "定義: 重要性・規模・影響が比較的小さい。  "
      },
      {
        "line": 121,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 122,
        "text": "違い: `principal` との程度軸上の対立で、最重要・主要ではない小さな要素を表す。  "
      },
      {
        "line": 123,
        "text": "例: The report contains a few minor errors.  "
      },
      {
        "line": 124,
        "text": "訳: その報告書には小さな誤りがいくつかある。  "
      },
      {
        "line": 126,
        "text": "2. 【名詞・可算】校長、学長、教育機関の長"
      },
      {
        "line": 155,
        "text": "【類義語】"
      },
      {
        "line": 157,
        "text": "・head teacher  "
      },
      {
        "line": 158,
        "text": "定義: 学校の運営を統括する教員・責任者。  "
      },
      {
        "line": 159,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 160,
        "text": "違い: 主にイギリス英語で学校の「校長」に使う。`principal` は北米などで一般的で、イギリスではカレッジ等の長を指す場合がある。  "
      },
      {
        "line": 161,
        "text": "例: The head teacher spoke at the assembly.  "
      },
      {
        "line": 162,
        "text": "訳: 校長は全校集会で話した。  "
      },
      {
        "line": 164,
        "text": "・head  "
      },
      {
        "line": 165,
        "text": "定義: 学校・学部・組織などの長。  "
      },
      {
        "line": 166,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 167,
        "text": "違い: `head` は教育以外にも広く使える一般語で、地域に応じて `head of school` などと言う。`principal` は制度上の正式な役職名として使われやすい。  "
      },
      {
        "line": 168,
        "text": "例: She is the head of a large secondary school.  "
      },
      {
        "line": 169,
        "text": "訳: 彼女は大規模な中等学校の校長である。  "
      },
      {
        "line": 171,
        "text": "・headmaster  "
      },
      {
        "line": 172,
        "text": "定義: 男性の校長。  "
      },
      {
        "line": 173,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 174,
        "text": "違い: 性別を明示する伝統的な語で、現在は性別中立の `head teacher` や `head` が選ばれることも多い。`principal` は性別を示さない。  "
      },
      {
        "line": 175,
        "text": "例: The former headmaster returned for the anniversary ceremony.  "
      },
      {
        "line": 176,
        "text": "訳: 元校長が創立記念式典のために戻ってきた。  "
      },
      {
        "line": 178,
        "text": "3. 【名詞・可算】責任者、中心人物、首席・主要メンバー"
      },
      {
        "line": 212,
        "text": "【類義語】"
      },
      {
        "line": 214,
        "text": "・leader  "
      },
      {
        "line": 215,
        "text": "定義: 集団を導き、方向づける人。  "
      },
      {
        "line": 216,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 217,
        "text": "違い: `leader` は実際に人々を率いる機能を強調する。`principal` は制度上の地位、所有、主要当事者性、専門職上の階級を指すことがある。  "
      },
      {
        "line": 218,
        "text": "例: The team leader assigned the tasks.  "
      },
      {
        "line": 219,
        "text": "訳: チームリーダーが作業を割り当てた。  "
      },
      {
        "line": 221,
        "text": "・director  "
      },
      {
        "line": 222,
        "text": "定義: 組織・部門・活動を管理または統括する人。  "
      },
      {
        "line": 223,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 224,
        "text": "違い: `director` は特定の管理職・取締役・芸術監督などの正式役職を指す。`principal` は別の職階であり、肩書きは相互に置換できない。  "
      },
      {
        "line": 225,
        "text": "例: The artistic director announced the new season.  "
      },
      {
        "line": 226,
        "text": "訳: 芸術監督が新シーズンを発表した。  "
      },
      {
        "line": 228,
        "text": "・chief  "
      },
      {
        "line": 229,
        "text": "定義: 組織・集団で最上位の責任者。  "
      },
      {
        "line": 230,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 231,
        "text": "違い: `chief` は指揮系統の最上位を強く表す。`principal` は中心人物・主要当事者や専門職の職階も表し、必ずしも組織全体の長とは限らない。  "
      },
      {
        "line": 232,
        "text": "例: The fire chief ordered an evacuation.  "
      },
      {
        "line": 233,
        "text": "訳: 消防署長が避難を命じた。  "
      },
      {
        "line": 235,
        "text": "4. 【名詞・不可算を中心に可算用法もある】元金、元本、利息計算の基礎額"
      },
      {
        "line": 274,
        "text": "【類義語】"
      },
      {
        "line": 276,
        "text": "・capital  "
      },
      {
        "line": 277,
        "text": "定義: 投資・事業に用いられる資金または資産。  "
      },
      {
        "line": 278,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 279,
        "text": "違い: `capital` は事業資金・生産資産まで広く表す。`principal` は特定の貸付・借入・投資で利息や収益の基礎となる元の額を指す。  "
      },
      {
        "line": 280,
        "text": "例: The company raised additional capital from investors.  "
      },
      {
        "line": 281,
        "text": "訳: その会社は投資家から追加資金を調達した。  "
      },
      {
        "line": 283,
        "text": "【反意語】"
      },
      {
        "line": 285,
        "text": "・interest  "
      },
      {
        "line": 286,
        "text": "定義: 借りた元金に対して支払う、または貸した・預けた元金から得る金額。  "
      },
      {
        "line": 287,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 288,
        "text": "違い: 金額構成の軸で、`principal` が基礎となる元の額なのに対し、`interest` は時間の経過と利率に応じて生じる追加額である。  "
      },
      {
        "line": 289,
        "text": "例: Most of the first payment went toward interest.  "
      },
      {
        "line": 290,
        "text": "訳: 初回の支払いの大部分は利息に充てられた。  "
      },
      {
        "line": 292,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 321,
        "text": "【類義語】"
      },
      {
        "line": 323,
        "text": "・client  "
      },
      {
        "line": 324,
        "text": "定義: 専門家や事業者からサービスを受ける顧客・依頼人。  "
      },
      {
        "line": 325,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 326,
        "text": "違い: `client` はサービス関係を表す広い語で、代理権の付与を必要としない。`principal` は代理人が権限を得る法律関係上の本人に焦点がある。  "
      },
      {
        "line": 327,
        "text": "例: The lawyer advised the client to seek a second opinion.  "
      },
      {
        "line": 328,
        "text": "訳: 弁護士は依頼人にセカンドオピニオンを求めるよう助言した。  "
      },
      {
        "line": 330,
        "text": "・mandator  "
      },
      {
        "line": 331,
        "text": "定義: 他人に委任・代理の権限を与える者。  "
      },
      {
        "line": 332,
        "text": "頻度: 〈2/10〉  "
      },
      {
        "line": 333,
        "text": "違い: 特定の法体系や専門文脈で使われる低頻度語である。英米法の一般的な代理関係では `principal` が標準的。  "
      },
      {
        "line": 334,
        "text": "例: The mandator may revoke the mandate subject to the agreement.  "
      },
      {
        "line": 335,
        "text": "訳: 委任者は、契約に従って委任を撤回できる場合がある。  "
      },
      {
        "line": 337,
        "text": "【反意語】"
      },
      {
        "line": 339,
        "text": "・agent  "
      },
      {
        "line": 340,
        "text": "定義: 他者から権限を与えられ、その者のために行動する人または法人。  "
      },
      {
        "line": 341,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 342,
        "text": "違い: 同じ代理関係の役割軸で、`principal` が権限を与える側、`agent` が与えられた権限で行動する側である。  "
      },
      {
        "line": 343,
        "text": "例: The agent negotiated the sale for the owner.  "
      },
      {
        "line": 344,
        "text": "訳: 代理人は所有者のために売却交渉を行った。  "
      },
      {
        "line": 346,
        "text": "6. 【名詞・可算・刑事法】正犯、犯罪の主要関与者"
      },
      {
        "line": 375,
        "text": "【類義語】"
      },
      {
        "line": 377,
        "text": "・perpetrator  "
      },
      {
        "line": 378,
        "text": "定義: 犯罪・不正行為を実際に行った者。  "
      },
      {
        "line": 379,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 380,
        "text": "違い: `perpetrator` は実行者に焦点を置く一般的な法律・報道語。`principal` は適用される法的分類によって、実行者以外の一定の関与者を含む場合がある。  "
      },
      {
        "line": 381,
        "text": "例: Police are still trying to identify the perpetrator.  "
      },
      {
        "line": 382,
        "text": "訳: 警察は今も犯人の特定を進めている。  "
      },
      {
        "line": 384,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 413,
        "text": "【類義語】"
      },
      {
        "line": 415,
        "text": "・obligor  "
      },
      {
        "line": 416,
        "text": "定義: 契約や法律上の義務を負う者。  "
      },
      {
        "line": 417,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 418,
        "text": "違い: `obligor` は義務を負う者を広く表す。`principal` は保証人などと対比して、その義務について第一次的に責任を負う側を示す。  "
      },
      {
        "line": 419,
        "text": "例: The obligor must perform the duty by the stated date.  "
      },
      {
        "line": 420,
        "text": "訳: 義務者は定められた日までに義務を履行しなければならない。  "
      },
      {
        "line": 422,
        "text": "・debtor  "
      },
      {
        "line": 423,
        "text": "定義: 金銭その他の債務を負う者。  "
      },
      {
        "line": 424,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 425,
        "text": "違い: `debtor` は債務者一般を指す。`principal` は保証関係で第一次的責任を負う当事者という役割を強調する。  "
      },
      {
        "line": 426,
        "text": "例: The debtor made the payment on time.  "
      },
      {
        "line": 427,
        "text": "訳: 債務者は期限どおりに支払った。  "
      },
      {
        "line": 429,
        "text": "【反意語】"
      },
      {
        "line": 431,
        "text": "・surety  "
      },
      {
        "line": 432,
        "text": "定義: 主たる債務者が履行しない場合に責任を負う保証人。  "
      },
      {
        "line": 433,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 434,
        "text": "違い: 責任順位の軸で、`principal` が第一次的に責任を負うのに対し、`surety` は他人の義務を担保する側に立つ。  "
      },
      {
        "line": 435,
        "text": "例: The surety paid after the borrower defaulted.  "
      },
      {
        "line": 436,
        "text": "訳: 借り手が債務不履行となった後、保証人が支払った。  "
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
  "evidence_context": {
    "schema_version": "evidence_context_v1",
    "input_body_sha256": "a90e8ce4e9b278894c354be6358063e378816073104700b90e9a801635efff87",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "bf4dfc4dfe48ca5d906ad1e4136211d090d6f6586502036076c95fb2dcc9b813",
    "source_first_artifact_sha256": "75775826336e48ec69bfa9e1d8457a9bb317da958651705395575df377922cf5",
    "relevant_sections": [
      "collocations_examples",
      "core_image",
      "etymology",
      "frames",
      "frequency_register",
      "lexical_relations",
      "pronunciation",
      "sense_structure",
      "usage_notes",
      "word_formation"
    ],
    "sources": [
      {
        "id": "S-001",
        "locator": "https://www.merriam-webster.com/dictionary/principal",
        "source_type": "general_dictionary",
        "independence_group": "merriam_webster",
        "facts": [
          {
            "id": "F-001",
            "form": "principal",
            "kind": "lexical_sense",
            "statement": "As an adjective, principal means most important, consequential, or influential.",
            "source_detail": "Adjective sense 1 and examples principal ingredient and principal city."
          },
          {
            "id": "F-002",
            "form": "principal",
            "kind": "lexical_sense",
            "statement": "As a noun, principal can be a person with controlling authority or a leading position.",
            "source_detail": "Noun sense 1 introduces the authority and leading-position group."
          },
          {
            "id": "F-003",
            "form": "principal",
            "kind": "lexical_sense",
            "statement": "Principal can denote the chief executive of an educational institution.",
            "source_detail": "Noun sense 1b directly defines the education-head use."
          },
          {
            "id": "F-004",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "In agency, a principal engages another to act as an agent and is the source of the agent's authority.",
            "source_detail": "Noun sense 1c states both engagement and derivation of authority."
          },
          {
            "id": "F-005",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "In criminal-law usage, principal can denote a chief or actual participant in a crime.",
            "source_detail": "Noun sense 1d and the legal definition distinguish principal participation from accessory status."
          },
          {
            "id": "F-006",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "Principal can denote the person primarily or ultimately liable on a legal obligation.",
            "source_detail": "Noun sense 1e and legal sense 1c contrast primary and secondary liability."
          },
          {
            "id": "F-007",
            "form": "principal",
            "kind": "lexical_sense",
            "statement": "Principal can denote a leading performer or star.",
            "source_detail": "Noun sense 1f directly records the performer use."
          },
          {
            "id": "F-008",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "Financial principal is a capital sum earning interest, due as debt, or used as a fund.",
            "source_detail": "Noun sense 2a and the legal definition distinguish principal from interest."
          },
          {
            "id": "F-009",
            "form": "principal",
            "kind": "pronunciation",
            "statement": "Principal is pronounced /ˈprɪnsəpəl/, with optional phonetic variants represented in the dictionary respelling.",
            "source_detail": "The adjective and noun share the same pronunciation entry."
          },
          {
            "id": "F-010",
            "form": "principal",
            "kind": "etymology",
            "statement": "Principal entered Middle English through Anglo-French from Latin principalis and princeps.",
            "source_detail": "Merriam-Webster word history gives the Anglo-French and Latin lineage."
          },
          {
            "id": "F-011",
            "form": "principalship",
            "kind": "derived_form",
            "statement": "Principalship is listed as a noun derivative of principal.",
            "source_detail": "Merriam-Webster lists principalship as a derived noun."
          },
          {
            "id": "F-012",
            "form": "principally",
            "kind": "derived_form",
            "statement": "Principally is the adverb formed from principal.",
            "source_detail": "Merriam-Webster lists principally directly after the adjective."
          },
          {
            "id": "F-032",
            "form": "principle",
            "kind": "usage_distinction",
            "statement": "Principle is a noun for a fundamental rule or law, whereas principal is also an adjective for most important.",
            "source_detail": "The usage note explicitly warns against confusing principal with principle."
          }
        ]
      },
      {
        "id": "S-002",
        "locator": "https://dictionary.cambridge.org/dictionary/english/principal",
        "source_type": "learner_dictionary",
        "independence_group": "cambridge_university_press",
        "facts": [
          {
            "id": "F-013",
            "form": "principal",
            "kind": "lexical_sense",
            "statement": "The adjective principal means first in order of importance.",
            "source_detail": "Cambridge learner definition and examples cover principal aim and principal reason."
          },
          {
            "id": "F-014",
            "form": "principal",
            "kind": "lexical_sense",
            "statement": "The noun principal denotes a person in charge of a school.",
            "source_detail": "Cambridge's school-person noun sense directly records the title."
          },
          {
            "id": "F-015",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "In finance, principal is an amount lent, borrowed, or invested apart from additional money such as interest.",
            "source_detail": "Cambridge's finance noun sense separates the underlying amount from additions."
          }
        ]
      },
      {
        "id": "S-003",
        "locator": "https://www.collinsdictionary.com/dictionary/english/principal",
        "source_type": "general_dictionary",
        "independence_group": "harpercollins",
        "facts": [
          {
            "id": "F-016",
            "form": "principal",
            "kind": "lexical_sense",
            "statement": "The adjective principal marks the highest or among the highest in rank, authority, importance, or degree.",
            "source_detail": "The American English adjective definition gives the rank-and-importance range."
          },
          {
            "id": "F-017",
            "form": "principal",
            "kind": "register_region",
            "statement": "Principal denotes the head of a school and, especially in England, may denote the head of a college.",
            "source_detail": "Collins distinguishes the school title and the English college use."
          },
          {
            "id": "F-018",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "In performing arts and orchestras, principal can denote a leading performer or the first player of a section.",
            "source_detail": "Collins lists leading actor, principal dancer, and orchestral first-player uses."
          },
          {
            "id": "F-019",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "In finance, principal is a capital sum distinguished from interest or profit and can include bond face value.",
            "source_detail": "The finance senses distinguish debt or investment amount from interest and income."
          },
          {
            "id": "F-020",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "In law, principal can be the person who employs or authorizes an agent.",
            "source_detail": "The law sense directly gives the principal-agent role."
          },
          {
            "id": "F-021",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "In law, principal can be a person directly responsible for a crime, including specified participation under the applicable classification.",
            "source_detail": "The criminal-law sense compares principal with accessory."
          },
          {
            "id": "F-022",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "Principal can be the person primarily liable for an obligation.",
            "source_detail": "The liability sense contrasts the principal with an endorser or similar secondary party."
          }
        ]
      },
      {
        "id": "S-004",
        "locator": "https://www.law.cornell.edu/wex/principal",
        "source_type": "legal_reference",
        "independence_group": "cornell_lii",
        "facts": [
          {
            "id": "F-023",
            "form": "principal-agent relationship",
            "kind": "specialist_use",
            "statement": "An agency-law principal is a person or entity authorizing an agent to act on its behalf and subject to its control.",
            "source_detail": "Wex states the authority, behalf, and control elements and notes duties owed by the agent."
          },
          {
            "id": "F-024",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "Financial principal is the original debt or investment amount excluding interest, profit, or other earnings.",
            "source_detail": "Wex separates the underlying amount from additions and explains that repayment reduces the obligation."
          },
          {
            "id": "F-025",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "In trust law, principal is the trust corpus or property itself, distinct from its income or earnings.",
            "source_detail": "Wex directly defines the trust-law corpus contrast."
          },
          {
            "id": "F-026",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "Principal can denote the party bearing primary responsibility for an obligation, as distinct from a surety or guarantor with secondary liability.",
            "source_detail": "Wex directly states the primary-versus-secondary liability contrast."
          }
        ]
      },
      {
        "id": "S-005",
        "locator": "https://www.investor.gov/introduction-investing/investing-basics/glossary/principal",
        "source_type": "government_finance_glossary",
        "independence_group": "us_sec_investor_gov",
        "facts": [
          {
            "id": "F-027",
            "form": "principal",
            "kind": "specialist_use",
            "statement": "Principal is the total amount borrowed or lent, or the initial amount invested.",
            "source_detail": "Investor.gov gives this concise finance glossary definition."
          }
        ]
      },
      {
        "id": "S-006",
        "locator": "https://www.etymonline.com/word/principal",
        "source_type": "etymology_reference",
        "independence_group": "etymonline",
        "facts": [
          {
            "id": "F-028",
            "form": "principal",
            "kind": "etymology",
            "statement": "The adjective is attested around 1300 from Old French principal and Latin principalis, ultimately connected with princeps, primus, and capere.",
            "source_detail": "Etymonline records the main/chief adjective and analyzes princeps as first plus take."
          },
          {
            "id": "F-029",
            "form": "principal",
            "kind": "etymology",
            "statement": "The noun is attested around 1300 for a chief person or leading representative and also had an early legal use.",
            "source_detail": "Etymonline's noun history records chief-person and law senses from the early period."
          },
          {
            "id": "F-030",
            "form": "principal",
            "kind": "etymology",
            "statement": "The public-school-head use is recorded from 1827, while a college-head use is older.",
            "source_detail": "Etymonline distinguishes the nineteenth-century school use from the mid-fifteenth-century college use."
          },
          {
            "id": "F-031",
            "form": "principal",
            "kind": "etymology",
            "statement": "The main-sum-of-money noun use is recorded from the early fifteenth century.",
            "source_detail": "Etymonline connects this sense with money on which interest is paid."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "U-001",
        "source_fact_ids": [
          "F-001",
          "F-013",
          "F-016"
        ],
        "canonical_statement": "The adjective principal marks something first or especially high in importance, rank, or influence.",
        "disposition": "included",
        "rationale": "High-frequency adjective sense supported by three independent dictionaries."
      },
      {
        "id": "U-002",
        "source_fact_ids": [
          "F-002",
          "F-003",
          "F-014",
          "F-017",
          "F-029",
          "F-030"
        ],
        "canonical_statement": "Principal denotes a person in authority and conventionally the head of specified educational institutions, with regional title differences.",
        "disposition": "included",
        "rationale": "Major person noun and education title with regional qualification; F-029 supplies the historical chief-person sense."
      },
      {
        "id": "U-003",
        "source_fact_ids": [
          "F-007",
          "F-018"
        ],
        "canonical_statement": "Principal can denote a leading performer, including a principal artist or orchestral section leader.",
        "disposition": "included",
        "rationale": "Established performing-arts noun use."
      },
      {
        "id": "U-004",
        "source_fact_ids": [
          "F-008",
          "F-015",
          "F-019",
          "F-024",
          "F-027",
          "F-031"
        ],
        "canonical_statement": "Financial principal is the underlying debt, loan, or investment amount distinguished from interest, profit, or later earnings.",
        "disposition": "included",
        "rationale": "Major specialist sense corroborated by general and government-specialist sources."
      },
      {
        "id": "U-005",
        "source_fact_ids": [
          "F-025"
        ],
        "canonical_statement": "Trust principal is the property or corpus distinguished from income earned by it.",
        "disposition": "integrated",
        "rationale": "Direct specialist extension of the finance/property sense."
      },
      {
        "id": "U-006",
        "source_fact_ids": [
          "F-004",
          "F-020",
          "F-023"
        ],
        "canonical_statement": "An agency principal authorizes an agent to act on the principal's behalf and is the source of the agent's authority.",
        "disposition": "included",
        "rationale": "Important legal and economics role supported by two dictionaries and Wex."
      },
      {
        "id": "U-007",
        "source_fact_ids": [
          "F-005",
          "F-021"
        ],
        "canonical_statement": "Criminal-law principal denotes a person treated as a primary participant under the applicable legal classification.",
        "disposition": "included",
        "rationale": "Low-frequency but encounterable specialist legal use; scope is explicitly jurisdiction-sensitive."
      },
      {
        "id": "U-008",
        "source_fact_ids": [
          "F-006",
          "F-022",
          "F-026"
        ],
        "canonical_statement": "In obligation law, principal denotes the primarily liable party, contrasted with a secondarily liable surety or guarantor.",
        "disposition": "included",
        "rationale": "Directly supported specialist responsibility contrast."
      },
      {
        "id": "U-009",
        "source_fact_ids": [
          "F-009"
        ],
        "canonical_statement": "The adjective and noun principal share the pronunciation /ˈprɪnsəpəl/.",
        "disposition": "included",
        "rationale": "Pronunciation support for the entry."
      },
      {
        "id": "U-010",
        "source_fact_ids": [
          "F-010",
          "F-028"
        ],
        "canonical_statement": "Principal came through French from Latin principalis and princeps, with a semantic core of first or chief.",
        "disposition": "included",
        "rationale": "Etymology is supported by two references."
      },
      {
        "id": "U-011",
        "source_fact_ids": [
          "F-011"
        ],
        "canonical_statement": "Principalship is listed as a noun derivative of principal.",
        "disposition": "included",
        "rationale": "Recorded noun derivative."
      },
      {
        "id": "U-012",
        "source_fact_ids": [
          "F-012"
        ],
        "canonical_statement": "Principally is the adverb formed from principal.",
        "disposition": "included",
        "rationale": "Recorded adverb derivative."
      },
      {
        "id": "U-013",
        "source_fact_ids": [
          "F-032"
        ],
        "canonical_statement": "Principal and principle differ in spelling, parts of speech, and current meanings.",
        "disposition": "included",
        "rationale": "Major learner confusion directly addressed by dictionary usage guidance."
      }
    ],
    "claim_units": [
      {
        "id": "C-001",
        "union_ids": [
          "U-001"
        ],
        "subject_form": "principal",
        "claim_type": "lexical_sense",
        "statement": "The adjective means principal, main, or first in relative importance.",
        "article_target_ids": [
          "definition:001",
          "grammar_pattern:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-001",
            "support_summary": "Merriam-Webster directly defines the adjective."
          },
          {
            "source_fact_id": "F-013",
            "support_summary": "Cambridge independently supplies the importance definition."
          },
          {
            "source_fact_id": "F-016",
            "support_summary": "Collins adds rank, authority, and degree."
          }
        ]
      },
      {
        "id": "C-002",
        "union_ids": [
          "U-002"
        ],
        "subject_form": "principal",
        "claim_type": "lexical_sense",
        "statement": "Principal is a person in authority and conventionally a school or education head, with the institution and preferred title varying by region.",
        "article_target_ids": [
          "definition:002",
          "definition:003",
          "grammar_pattern:002",
          "usage_note:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-002",
            "support_summary": "Merriam-Webster supplies the broader authority and leading-position sense."
          },
          {
            "source_fact_id": "F-003",
            "support_summary": "Merriam-Webster directly gives the educational executive sense."
          },
          {
            "source_fact_id": "F-014",
            "support_summary": "Cambridge independently gives school head."
          },
          {
            "source_fact_id": "F-017",
            "support_summary": "Collins supplies the English college qualification."
          },
          {
            "source_fact_id": "F-029",
            "support_summary": "Etymonline records the historical chief-person and leading-representative noun sense."
          },
          {
            "source_fact_id": "F-030",
            "support_summary": "Etymonline documents the different historical dates for public-school and college-head uses."
          }
        ]
      },
      {
        "id": "C-003",
        "union_ids": [
          "U-003"
        ],
        "subject_form": "principal",
        "claim_type": "lexical_sense",
        "statement": "Principal can be a leading performer or orchestral section player.",
        "article_target_ids": [
          "definition:003",
          "grammar_pattern:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-007",
            "support_summary": "Merriam-Webster gives leading performer."
          },
          {
            "source_fact_id": "F-018",
            "support_summary": "Collins supplies performer and orchestral uses."
          }
        ]
      },
      {
        "id": "C-004",
        "union_ids": [
          "U-004"
        ],
        "subject_form": "principal",
        "claim_type": "specialist_use",
        "statement": "Financial principal is the underlying borrowed, lent, or invested amount, distinct from interest and returns.",
        "article_target_ids": [
          "definition:004",
          "grammar_pattern:004",
          "usage_note:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-008",
            "support_summary": "Merriam-Webster defines the capital-sum sense."
          },
          {
            "source_fact_id": "F-015",
            "support_summary": "Cambridge independently covers lending, borrowing, and investment."
          },
          {
            "source_fact_id": "F-019",
            "support_summary": "Collins independently distinguishes capital sum and bond face value from interest or profit."
          },
          {
            "source_fact_id": "F-024",
            "support_summary": "Wex states the interest and earnings contrast."
          },
          {
            "source_fact_id": "F-027",
            "support_summary": "Investor.gov supplies the government finance definition."
          },
          {
            "source_fact_id": "F-031",
            "support_summary": "Etymonline documents the early-fifteenth-century main-sum history."
          }
        ]
      },
      {
        "id": "C-005",
        "union_ids": [
          "U-005"
        ],
        "subject_form": "principal",
        "claim_type": "specialist_use",
        "statement": "Trust principal is property or corpus distinct from the income it produces.",
        "article_target_ids": [
          "usage_note:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-025",
            "support_summary": "Wex directly defines trust principal and its income contrast."
          }
        ]
      },
      {
        "id": "C-006",
        "union_ids": [
          "U-006"
        ],
        "subject_form": "principal-agent relationship",
        "claim_type": "specialist_use",
        "statement": "An agency principal gives authority to an agent acting on its behalf and is the source of that authority.",
        "article_target_ids": [
          "definition:005",
          "grammar_pattern:005",
          "word_formation:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-004",
            "support_summary": "Merriam-Webster identifies the source-of-authority role."
          },
          {
            "source_fact_id": "F-020",
            "support_summary": "Collins independently gives the agent-employing principal."
          },
          {
            "source_fact_id": "F-023",
            "support_summary": "Wex gives authority, behalf, and control elements."
          }
        ]
      },
      {
        "id": "C-007",
        "union_ids": [
          "U-007"
        ],
        "subject_form": "principal",
        "claim_type": "specialist_use",
        "statement": "Criminal-law principal denotes a primary participant according to a jurisdiction-specific legal classification.",
        "article_target_ids": [
          "definition:006",
          "grammar_pattern:006",
          "usage_note:006"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-005",
            "support_summary": "Merriam-Webster supplies criminal participant and historical degree classifications."
          },
          {
            "source_fact_id": "F-021",
            "support_summary": "Collins independently compares principal and accessory."
          }
        ]
      },
      {
        "id": "C-008",
        "union_ids": [
          "U-008"
        ],
        "subject_form": "principal obligor",
        "claim_type": "specialist_use",
        "statement": "An obligation-law principal is primarily liable, in contrast with a surety or guarantor with secondary liability.",
        "article_target_ids": [
          "definition:007",
          "grammar_pattern:007",
          "usage_note:007"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-006",
            "support_summary": "Merriam-Webster gives primary or ultimate liability."
          },
          {
            "source_fact_id": "F-022",
            "support_summary": "Collins independently gives the obligation sense."
          },
          {
            "source_fact_id": "F-026",
            "support_summary": "Wex directly states the surety and guarantor contrast."
          }
        ]
      },
      {
        "id": "C-009",
        "union_ids": [
          "U-009"
        ],
        "subject_form": "principal",
        "claim_type": "pronunciation",
        "statement": "Principal is pronounced /ˈprɪnsəpəl/ as both adjective and noun.",
        "article_target_ids": [
          "pronunciation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-009",
            "support_summary": "Merriam-Webster supplies the shared pronunciation."
          }
        ]
      },
      {
        "id": "C-010",
        "union_ids": [
          "U-010"
        ],
        "subject_form": "principal",
        "claim_type": "etymology",
        "statement": "Principal derives through French from Latin principalis and princeps and retains a first-or-chief semantic connection.",
        "article_target_ids": [
          "etymology:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-010",
            "support_summary": "Merriam-Webster supplies the transmission path."
          },
          {
            "source_fact_id": "F-028",
            "support_summary": "Etymonline supplies the semantic and morphological analysis."
          }
        ]
      },
      {
        "id": "C-011",
        "union_ids": [
          "U-011"
        ],
        "subject_form": "principalship",
        "claim_type": "derived_form",
        "statement": "Principalship is listed as a noun derivative of principal.",
        "article_target_ids": [
          "word_formation:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-011",
            "support_summary": "Merriam-Webster records principalship as the noun derivative."
          }
        ]
      },
      {
        "id": "C-012",
        "union_ids": [
          "U-012"
        ],
        "subject_form": "principally",
        "claim_type": "derived_form",
        "statement": "Principally is the adverb formed from principal.",
        "article_target_ids": [
          "word_formation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-012",
            "support_summary": "Merriam-Webster records the adverb derivative."
          }
        ]
      },
      {
        "id": "C-013",
        "union_ids": [
          "U-013"
        ],
        "subject_form": "principle",
        "claim_type": "usage_distinction",
        "statement": "Principle is the noun for a rule or fundamental truth and must not replace principal as the adjective or person-and-money noun.",
        "article_target_ids": [
          "usage_note:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-032",
            "support_summary": "Merriam-Webster directly explains the spelling, meaning, and part-of-speech contrast."
          }
        ]
      }
    ]
  },
  "specification_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
  "source_artifact_sha256": "75775826336e48ec69bfa9e1d8457a9bb317da958651705395575df377922cf5",
  "normalized_input_sha256": "4cd6906f44e93c8c82453c0c8292c68603c9ffa741d46be9a2671de74af20db2"
}
```
