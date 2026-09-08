# Independent checker recheck handoff

Stage: `checker_recheck/translation`

Run this request in its own independent subagent/session. The six invalidated checker passes are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes. Pronunciation is deterministically reused and must not be reviewed again.

Save exactly one JSON response as `recheck/translation.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each rechecked pass must use a different agent_id.
## Prompt

# check_pass_translation_v6

## 目的

英文・訳文・定義における意味の保存と方向を検査する。自然な意訳は認めるが、見出し語の構文差・含意・作用関係を誤学習させる変化は認めない。

## 担当タクソノミー分類

- `example_translation_alignment`
- `semantic_direction_reversal`

## 検査ルール

- 各例文と訳について、述語、主語・目的語・補語、行為者・経験者・対象・結果の意味役割を対応させる。
- 肯定・否定、比較基準、程度、数量、時制、相、法、条件、因果、目的を保存する。
- 修飾範囲、焦点、対比、情報構造、明示内容と文脈推論の境界、レジスターと話者評価を保存する。
- コロケーションのpattern・用途・英文・訳が同じ語義、品詞、完全フレームを表すか確認する。英文が別語義でも成立するだけでは合格にしない。
- 作用する側／される側、上位／下位、原因／結果、全体／部分、評価主体／評価対象を逆転させない。
- 日本語訳が自然でも、英文にない必然性・意図・結果・専門的効果を追加していればfindingとする。
- 同じ例文を異なる構文や語義の証明に使い回していないか確認する。
- 問題が1箇所に見える場合も、同じ訳語・関係が入力section内の別箇所で再発していないか確認する。

## 入力として受け取るセクション

- `definitions`
- `collocations_examples`
- `lexical_relations`

front matter、生成過程、通常チェックの過去判断、ACTIVE.mdは受け取らない。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "example_translation_alignment | semantic_direction_reversal",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "何がどの方向・範囲・強さで不一致か",
  "evidence_link_ids": [],
  "suggested_direction": "意味を変えずに直す方向"
}
```

`taxonomy_id`、位置、severity、根拠を必須とする。事実・語法・例文/訳の正誤に関わるものは `blocking`、事実関係を変えない局所的な日本語調整だけを `minor` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "translation",
  "taxonomy_ids": [
    "example_translation_alignment",
    "semantic_direction_reversal"
  ],
  "specification": "prompts/check_pass_translation_v6.md",
  "input_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9",
  "input_sections": {
    "definitions": [
      {
        "line": 40,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】複数の原因、目的、人物、場所、要素などの中で、重要度・影響力・順位が最も高い、または特に高いものを示す。単に時間的に最初という意味ではなく、重要性や中心性の評価を表す。  "
      },
      {
        "line": 120,
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 122,
        "text": "【日本語訳・定義】組織で支配的権限または主導的地位を持つ人。特に、学校、カレッジ、その他の教育機関を管理する最高責任者を指す。教育上どの種類の機関を指すかは地域と制度によって異なる。  "
      },
      {
        "line": 153,
        "text": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 155,
        "text": "【日本語訳・定義】舞台芸術で主要な役を担う演者、またはオーケストラで一つのセクションを率いる奏者。一般の重要人物ではなく、芸術分野で確立した役割名を指す。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 188,
        "text": "【日本語訳・定義】借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。信託法では、収益と区別される信託財産そのもの、すなわち信託元本・corpusを指す。  "
      },
      {
        "line": 224,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 226,
        "text": "【日本語訳・定義】別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。  "
      },
      {
        "line": 266,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 268,
        "text": "【日本語訳・定義】刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。  "
      },
      {
        "line": 294,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 296,
        "text": "【日本語訳・定義】債務・保証の文脈で、保証人などの二次的責任者と対比され、義務について第一次的に責任を負う人または法人。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 50,
        "text": "【コロケーション】"
      },
      {
        "line": 52,
        "text": "・`the principal reason for ...`  "
      },
      {
        "line": 53,
        "text": "用途: 出来事・状況・判断・行動などについて、最も重要な理由を示す。  "
      },
      {
        "line": 54,
        "text": "例: The principal reason for the delay was a shortage of parts.  "
      },
      {
        "line": 55,
        "text": "訳: 遅延の主な理由は部品不足だった。  "
      },
      {
        "line": 57,
        "text": "・`the principal cause of ...`  "
      },
      {
        "line": 58,
        "text": "用途: 出来事を引き起こした最も重要な原因を示す。  "
      },
      {
        "line": 59,
        "text": "例: Investigators identified corrosion as the principal cause of the failure.  "
      },
      {
        "line": 60,
        "text": "訳: 調査担当者は、腐食をその故障の主因と特定した。  "
      },
      {
        "line": 62,
        "text": "・`a principal source of ...`  "
      },
      {
        "line": 63,
        "text": "用途: 物・情報・収入などの主要な供給源を示す。  "
      },
      {
        "line": 64,
        "text": "例: Tourism is a principal source of income for the island.  "
      },
      {
        "line": 65,
        "text": "訳: 観光はその島の主要な収入源の一つである。  "
      },
      {
        "line": 67,
        "text": "・`one of the principal 〈複数名詞〉`  "
      },
      {
        "line": 68,
        "text": "用途: 最重要候補が複数ある中の一つであることを示す。  "
      },
      {
        "line": 69,
        "text": "例: She is one of the principal architects of the reform.  "
      },
      {
        "line": 70,
        "text": "訳: 彼女はその改革の主要な立案者の一人である。  "
      },
      {
        "line": 120,
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 130,
        "text": "【コロケーション】"
      },
      {
        "line": 132,
        "text": "・`a principal with controlling authority`  "
      },
      {
        "line": 133,
        "text": "用途: 支配的権限を持つ人という一般の人物用法を表す。  "
      },
      {
        "line": 134,
        "text": "例: A principal with controlling authority approved the proposal.  "
      },
      {
        "line": 135,
        "text": "訳: 支配的権限を持つ責任者がその提案を承認した。  "
      },
      {
        "line": 137,
        "text": "・`the principal + be + in charge of 〈学校〉`  "
      },
      {
        "line": 138,
        "text": "用途: 教育機関を管理する長であることを表す。  "
      },
      {
        "line": 139,
        "text": "例: The principal is in charge of the school.  "
      },
      {
        "line": 140,
        "text": "訳: その校長が学校の管理を担っている。  "
      },
      {
        "line": 153,
        "text": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 163,
        "text": "【コロケーション】"
      },
      {
        "line": 165,
        "text": "・`a principal dancer`  "
      },
      {
        "line": 166,
        "text": "用途: 舞台芸術で主要な役を担う演者を表す。  "
      },
      {
        "line": 167,
        "text": "例: She is a principal dancer.  "
      },
      {
        "line": 168,
        "text": "訳: 彼女は主要な役を担うダンサーである。  "
      },
      {
        "line": 170,
        "text": "・`the principal + be + the first player of 〈オーケストラのセクション〉`  "
      },
      {
        "line": 171,
        "text": "用途: オーケストラのセクションで首席を務める奏者を表す。  "
      },
      {
        "line": 172,
        "text": "例: The principal is the first player of the violin section.  "
      },
      {
        "line": 173,
        "text": "訳: その首席奏者はバイオリン・セクションの第一奏者である。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 196,
        "text": "【コロケーション】"
      },
      {
        "line": 198,
        "text": "・`principal + be + the initial amount invested`  "
      },
      {
        "line": 199,
        "text": "用途: 投資で、収益の基礎となる最初の金額を表す。  "
      },
      {
        "line": 200,
        "text": "例: The principal is the initial amount invested.  "
      },
      {
        "line": 201,
        "text": "訳: 元本とは最初に投資された金額である。  "
      },
      {
        "line": 203,
        "text": "・`principal + be + distinct from interest`  "
      },
      {
        "line": 204,
        "text": "用途: 借入・貸付の元金を利息と区別して表す。  "
      },
      {
        "line": 205,
        "text": "例: Principal is distinct from interest on the loan.  "
      },
      {
        "line": 206,
        "text": "訳: 元金はその融資の利息とは別のものである。  "
      },
      {
        "line": 208,
        "text": "・`trust principal + be + distinct from income`  "
      },
      {
        "line": 209,
        "text": "用途: 信託財産の元本を、そこから生じる収益と区別する。  "
      },
      {
        "line": 210,
        "text": "例: Trust principal is distinct from income.  "
      },
      {
        "line": 211,
        "text": "訳: 信託元本は収益とは別のものである。  "
      },
      {
        "line": 224,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 234,
        "text": "【コロケーション】"
      },
      {
        "line": 236,
        "text": "・`a principal-agent relationship`  "
      },
      {
        "line": 237,
        "text": "用途: 権限を与える本人と、そのために行動する代理人との関係を表す。  "
      },
      {
        "line": 238,
        "text": "例: The contract created a principal-agent relationship between the owner and the broker.  "
      },
      {
        "line": 239,
        "text": "訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。  "
      },
      {
        "line": 241,
        "text": "・`act on behalf of the principal`  "
      },
      {
        "line": 242,
        "text": "用途: 代理人が本人を代理して行動することを表す。  "
      },
      {
        "line": 243,
        "text": "例: The agent may sign the document on behalf of the principal.  "
      },
      {
        "line": 244,
        "text": "訳: 代理人は本人を代理してその書類に署名できる。  "
      },
      {
        "line": 266,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 276,
        "text": "【コロケーション】"
      },
      {
        "line": 278,
        "text": "・`the principal + be + directly responsible for 〈犯罪〉`  "
      },
      {
        "line": 279,
        "text": "用途: 適用法上、犯罪について直接責任を負う者を表す。  "
      },
      {
        "line": 280,
        "text": "例: Under the statute, the principal is directly responsible for the crime.  "
      },
      {
        "line": 281,
        "text": "訳: その制定法の下で、当該 `principal` はその犯罪について直接責任を負う。  "
      },
      {
        "line": 294,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 304,
        "text": "【コロケーション】"
      },
      {
        "line": 306,
        "text": "・`the principal + be + primarily liable for 〈債務・義務〉`  "
      },
      {
        "line": 307,
        "text": "用途: 主たる当事者が義務について第一次的責任を負うことを示す。  "
      },
      {
        "line": 308,
        "text": "例: The principal is primarily liable for the debt.  "
      },
      {
        "line": 309,
        "text": "訳: 主たる債務者はその債務について第一次的責任を負う。  "
      },
      {
        "line": 311,
        "text": "・`the principal + be + distinct from 〈surety/guarantor〉 with secondary liability`  "
      },
      {
        "line": 312,
        "text": "用途: 第一次的責任者を、二次的責任を負う保証人と区別する。  "
      },
      {
        "line": 313,
        "text": "例: The principal is distinct from the surety, who has secondary liability.  "
      },
      {
        "line": 314,
        "text": "訳: 主たる債務者は、二次的責任を負う保証人とは別の当事者である。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 40,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 74,
        "text": "【類義語】"
      },
      {
        "line": 76,
        "text": "・main  "
      },
      {
        "line": 77,
        "text": "定義: 複数のものの中で中心的・最重要である。  "
      },
      {
        "line": 78,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 79,
        "text": "違い: `main` は日常語で範囲が広い。`principal` はより形式的で、順位・重要性・影響力が高いことを意識させる。  "
      },
      {
        "line": 80,
        "text": "例: Our main goal is to reduce waiting times.  "
      },
      {
        "line": 81,
        "text": "訳: 私たちの主な目標は待ち時間を減らすことだ。  "
      },
      {
        "line": 83,
        "text": "・primary  "
      },
      {
        "line": 84,
        "text": "定義: 第一順位・第一段階である、または最も基本的である。  "
      },
      {
        "line": 85,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 86,
        "text": "違い: `primary` は重要性に加え、順序・段階・基本性にも焦点を置ける。`principal` は主として相対的な重要度や地位を表す。  "
      },
      {
        "line": 87,
        "text": "例: Safety is our primary concern.  "
      },
      {
        "line": 88,
        "text": "訳: 安全が私たちの最優先事項である。  "
      },
      {
        "line": 90,
        "text": "・chief  "
      },
      {
        "line": 91,
        "text": "定義: 同種の中で最上位・最重要である。  "
      },
      {
        "line": 92,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 93,
        "text": "違い: `chief` は役職名や「最大の原因・懸念」によく使われ、最上位性を強く示す。`principal` は文章語として原因・目的・人物・場所などに幅広く使う。  "
      },
      {
        "line": 94,
        "text": "例: Cost remains the chief obstacle to expansion.  "
      },
      {
        "line": 95,
        "text": "訳: 費用が依然として拡大の最大の障害である。  "
      },
      {
        "line": 97,
        "text": "・leading  "
      },
      {
        "line": 98,
        "text": "定義: ある分野で先頭に立ち、大きな影響力や高い評価を持つ。  "
      },
      {
        "line": 99,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 100,
        "text": "違い: `leading` は人・企業・研究機関などの実績や影響力を強調しやすい。`principal` は実績評価を必須とせず、対象内での中心性を示す。  "
      },
      {
        "line": 101,
        "text": "例: She is a leading expert on marine ecosystems.  "
      },
      {
        "line": 102,
        "text": "訳: 彼女は海洋生態系の第一人者である。  "
      },
      {
        "line": 104,
        "text": "【反意語】"
      },
      {
        "line": 106,
        "text": "・secondary  "
      },
      {
        "line": 107,
        "text": "定義: 第一ではなく、重要度・順位が二次的である。  "
      },
      {
        "line": 108,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 109,
        "text": "違い: 重要度・順位の軸で `principal` と方向が反対になり、主要なものに対する従属的・補助的なものを表す。  "
      },
      {
        "line": 110,
        "text": "例: Price was only a secondary consideration.  "
      },
      {
        "line": 111,
        "text": "訳: 価格は二次的な考慮事項にすぎなかった。  "
      },
      {
        "line": 113,
        "text": "・minor  "
      },
      {
        "line": 114,
        "text": "定義: 重要性・規模・影響が比較的小さい。  "
      },
      {
        "line": 115,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 116,
        "text": "違い: `principal` との程度軸上の対立で、最重要・主要ではない小さな要素を表す。  "
      },
      {
        "line": 117,
        "text": "例: The report contains a few minor errors.  "
      },
      {
        "line": 118,
        "text": "訳: その報告書には小さな誤りがいくつかある。  "
      },
      {
        "line": 120,
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 144,
        "text": "【類義語】"
      },
      {
        "line": 146,
        "text": "・head  "
      },
      {
        "line": 147,
        "text": "定義: 学校・組織などの長。  "
      },
      {
        "line": 148,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 149,
        "text": "違い: `head` は組織の長を広く表す。`principal` は権限・主導的地位を持つ人を表し、特に教育機関で役職名として用いられる。  "
      },
      {
        "line": 150,
        "text": "例: She is the head of a large secondary school.  "
      },
      {
        "line": 151,
        "text": "訳: 彼女は大規模な中等学校の校長である。  "
      },
      {
        "line": 153,
        "text": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 177,
        "text": "【類義語】"
      },
      {
        "line": 179,
        "text": "・section leader  "
      },
      {
        "line": 180,
        "text": "定義: オーケストラで一つのセクションを率いる奏者。  "
      },
      {
        "line": 181,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 182,
        "text": "違い: 役割を説明する一般的な表現で、`principal` は確立した役職名として用いられる。  "
      },
      {
        "line": 183,
        "text": "例: The section leader rehearsed the difficult passage.  "
      },
      {
        "line": 184,
        "text": "訳: セクションの首席奏者は難しい楽節を練習した。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 215,
        "text": "【類義語】"
      },
      {
        "line": 217,
        "text": "・capital  "
      },
      {
        "line": 218,
        "text": "定義: 投資・事業に用いられる資金または資産。  "
      },
      {
        "line": 219,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 220,
        "text": "違い: `capital` は事業資金・生産資産まで広く表す。`principal` は特定の貸付・借入・投資で利息や収益の基礎となる元の額を指す。  "
      },
      {
        "line": 221,
        "text": "例: The company raised additional capital from investors.  "
      },
      {
        "line": 222,
        "text": "訳: その会社は投資家から追加資金を調達した。  "
      },
      {
        "line": 224,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 248,
        "text": "【類義語】"
      },
      {
        "line": 250,
        "text": "・mandator  "
      },
      {
        "line": 251,
        "text": "定義: 他人に委任・代理の権限を与える者。  "
      },
      {
        "line": 252,
        "text": "頻度: 〈2/10〉  "
      },
      {
        "line": 253,
        "text": "違い: 特定の法体系や専門文脈で使われる低頻度語である。  "
      },
      {
        "line": 254,
        "text": "例: The mandator may revoke the mandate subject to the agreement.  "
      },
      {
        "line": 255,
        "text": "訳: 委任者は、契約の定めに従い、委任を撤回できる。  "
      },
      {
        "line": 257,
        "text": "【反意語】"
      },
      {
        "line": 259,
        "text": "・agent  "
      },
      {
        "line": 260,
        "text": "定義: 他者から権限を与えられ、その者のために行動する人または法人。  "
      },
      {
        "line": 261,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 262,
        "text": "違い: 同じ代理関係の役割軸で、`principal` が権限を与える側、`agent` が与えられた権限で行動する側である。  "
      },
      {
        "line": 263,
        "text": "例: The agent negotiated the sale for the owner.  "
      },
      {
        "line": 264,
        "text": "訳: 代理人は所有者のために売却交渉を行った。  "
      },
      {
        "line": 266,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 285,
        "text": "【類義語】"
      },
      {
        "line": 287,
        "text": "・perpetrator  "
      },
      {
        "line": 288,
        "text": "定義: 犯罪・不正行為を実際に行った者。  "
      },
      {
        "line": 289,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 290,
        "text": "違い: `perpetrator` は実行者に焦点を置く一般的な法律・報道語。`principal` は適用される法的分類によって、実行者以外の一定の関与者を含む場合がある。  "
      },
      {
        "line": 291,
        "text": "例: Police are still trying to identify the perpetrator.  "
      },
      {
        "line": 292,
        "text": "訳: 警察は今も犯人の特定を進めている。  "
      },
      {
        "line": 294,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 318,
        "text": "【類義語】"
      },
      {
        "line": 320,
        "text": "・obligor  "
      },
      {
        "line": 321,
        "text": "定義: 契約や法律上の義務を負う者。  "
      },
      {
        "line": 322,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 323,
        "text": "違い: `obligor` は義務を負う者を広く表す。`principal` は保証人などと対比して、その義務について第一次的に責任を負う側を示す。  "
      },
      {
        "line": 324,
        "text": "例: The obligor must perform the duty by the stated date.  "
      },
      {
        "line": 325,
        "text": "訳: 義務者は定められた日までに義務を履行しなければならない。  "
      },
      {
        "line": 327,
        "text": "・debtor  "
      },
      {
        "line": 328,
        "text": "定義: 金銭その他の債務を負う者。  "
      },
      {
        "line": 329,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 330,
        "text": "違い: `debtor` は債務者一般を指す。`principal` は保証関係で第一次的責任を負う当事者という役割を強調する。  "
      },
      {
        "line": 331,
        "text": "例: The debtor made the payment on time.  "
      },
      {
        "line": 332,
        "text": "訳: 債務者は期限どおりに支払った。  "
      },
      {
        "line": 334,
        "text": "【反意語】"
      },
      {
        "line": 336,
        "text": "・surety  "
      },
      {
        "line": 337,
        "text": "定義: 主たる債務者が履行しない場合に責任を負う保証人。  "
      },
      {
        "line": 338,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 339,
        "text": "違い: 責任順位の軸で、`principal` が第一次的に責任を負うのに対し、`surety` は他人の義務を担保する側に立つ。  "
      },
      {
        "line": 340,
        "text": "例: The surety paid after the borrower defaulted.  "
      },
      {
        "line": 341,
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
  "specification_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
  "source_artifact_sha256": "e97de23f48433c92c1418c79368c269f37025be735dd52c0dced6832eb2c7705",
  "normalized_input_sha256": "f4447524470672122708c1c0d5ffdad3f5285969859daedb4c32fbb69fd8a69a"
}
```
