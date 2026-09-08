# Independent checker recheck handoff

Stage: `checker_recheck/qualification`

Run this request in its own independent subagent/session. The seven checker recheck requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

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
  "input_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "中英語を経て、ラテン語 constituere「立てる、据える、設ける、定める」に由来する。これは con- と statuere「立てる、置く」から成り、statuere は「立つ」を表す語根につながる。現在の「全体を構成する」「制度・組織を正式に成立させる」「人を役職に就ける」という用法には、「ある形・位置に据えて成立させる」という歴史的な意味が残っている。  "
      },
      {
        "line": 20,
        "text": "同語源・同じ語族の学習語には constitution「構成、体質、憲法」、constitutional「構成上の、憲法上の」、constituent「構成要素、選挙区民；構成する」、statute「制定法」がある。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "`constitution` — 名詞。「構成・体質」のほか、国家・組織の基本原則を定める「憲法・規約」を表す。  "
      },
      {
        "line": 25,
        "text": "`constitutional / constitutionally` — 形容詞「構成上の、体質上の、憲法上の」／副詞「体質的に、憲法上」。  "
      },
      {
        "line": 26,
        "text": "`constituent` — 名詞「構成要素、選挙区民」、形容詞「構成する」。政治義の constituent は「constitute の目的語」を意味する名称ではなく、代表者を選ぶ constituency の構成員を指す。  "
      },
      {
        "line": 27,
        "text": "`reconstitute` — 動詞「再構成する、元の状態に戻す」。乾燥食品・薬剤などに液体を加えて戻す用法もある。  "
      }
    ],
    "sense_structure": [
      {
        "line": 39,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 41,
        "text": "【日本語訳・定義】一つまたは複数の人・物・部分・期間などが、一つの全体を形作る、またはその全体の一定割合・重要部分を占めることを表す。全体構成の能動構文では主語が構成要素、目的語がそれらによってできる全体である。一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は通常 of 句に現れるが、文脈上明らかな場合は省略できる。意図的に組み立てる行為ではなく、部分と全体の関係を記述することが多い。  "
      },
      {
        "line": 111,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 113,
        "text": "【日本語訳・定義】行為、状況、事実、結果などが、ある分類・評価・状態の定義や成立条件を満たし、そのものと見なせることを表す。目的語には crime、breach、threat、evidence、change、problem などが来る。法律用語だけではなく一般の評価にも使うが、何がその分類に当たるかをやや改まって判断する響きがある。  "
      },
      {
        "line": 188,
        "text": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える"
      },
      {
        "line": 190,
        "text": "【日本語訳・定義】組織、委員会、裁判所、政府などを正式に形成・設置し、公式の組織体として成立させることを表す。法律用法では、契約や組織体に所定の法的形式を与えることも表す。制度や文脈によって所定の手続きや権限付与を伴うことはあるが、constitute という語だけで法的有効性や実際の活動可能性まで一律に保証するわけではない。  "
      },
      {
        "line": 255,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 257,
        "text": "【日本語訳・定義】権限をもつ者・法律・公式文書などが、人を特定の役職・地位・役割に正式に任命・指定することを表す。任命の法的有効性、付与される権限、その立場で行動できる範囲は、該当する文書・制度・法域によって決まる。  "
      }
    ],
    "frequency_register": [
      {
        "line": 39,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 43,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 45,
        "text": "【レジスター/領域】やや硬い標準語。報道、統計、学術、ビジネス、公式説明でよく使う。日常会話では make up や form の方が一般的なことが多い。  "
      },
      {
        "line": 111,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 115,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 117,
        "text": "【レジスター/領域】やや硬い標準語。報道、法律、規則、倫理、学術、ビジネス上の評価で頻出する。法律文脈では、実際に犯罪・違反などが成立するかは適用法と事実認定によって決まるため、単語自体が法的結論を保証するわけではない。  "
      },
      {
        "line": 188,
        "text": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える"
      },
      {
        "line": 192,
        "text": "【頻度】〈5/10〉  "
      },
      {
        "line": 194,
        "text": "【レジスター/領域】非常に硬い公式・行政・法律・組織運営の用法。契約などを所定の法的形式に整える意味も法律文脈に限られる。一般的な会社・団体の設立では establish、form、set up がより広く使われる。  "
      },
      {
        "line": 255,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 259,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 261,
        "text": "【レジスター/領域】法律・公文書などの公式文体。`a legally constituted officer` のような表現では、法や制度に基づいて正式に任命された役職者を指す。  "
      }
    ],
    "usage_notes": [
      {
        "line": 39,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 76,
        "text": "【語法・注意】能動の `A, B, and C constitute X` では A・B・C が部分、X が全体である。`X consists of A, B, and C` や `X is composed of A, B, and C` では向きが逆になり、X が全体、A・B・C が部分になる。  "
      },
      {
        "line": 111,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 153,
        "text": "【語法・注意】この語義の constitute は、主語と目的語を同一の分類関係で結ぶが、文法上は目的語を取る動詞であり、通常 `constitute as a threat` のように as を挟まない。`The delay constitutes a problem.` のように直接目的語を置く。  "
      },
      {
        "line": 188,
        "text": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える"
      },
      {
        "line": 225,
        "text": "【語法・注意】語義1の「部分が全体を構成している」は状態的な関係、語義3の「組織を正式に設立する」は意図的・制度的な行為である。`The members constitute the board.` は「構成員が取締役会を構成する」、`The agency constituted a board.` は「機関が取締役会を正式に設置した」となる。  "
      },
      {
        "line": 255,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 282,
        "text": "【語法・注意】人を直接目的語にし、役職を目的格補語として置く `constitute someone treasurer` のような形で使う。現代の一般文では非常に硬いため、通常は `appoint someone treasurer` などとする。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 39,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 49,
        "text": "【コロケーション】"
      },
      {
        "line": 51,
        "text": "・`〈parts/members〉 constitute 〈whole/group〉`  "
      },
      {
        "line": 52,
        "text": "用途: 複数の部分・構成員が一つの全体や集団を作ることを述べる。  "
      },
      {
        "line": 53,
        "text": "例: Twelve jurors constitute the full jury in this court.  "
      },
      {
        "line": 54,
        "text": "訳: この裁判所では、12人の陪審員が陪審全体を構成する。  "
      },
      {
        "line": 56,
        "text": "・`constitute the majority/minority of 〈group〉`  "
      },
      {
        "line": 57,
        "text": "用途: ある分類の人・物が、集団の過半数または少数派を占めることを述べる。  "
      },
      {
        "line": 58,
        "text": "例: Part-time employees constitute the majority of the evening staff.  "
      },
      {
        "line": 59,
        "text": "訳: 非常勤職員が夜間スタッフの過半数を占めている。  "
      },
      {
        "line": 61,
        "text": "・`constitute 〈percentage〉 of 〈whole〉`  "
      },
      {
        "line": 62,
        "text": "用途: 全体に占める割合を、統計的・客観的に示す。  "
      },
      {
        "line": 63,
        "text": "例: Online sales now constitute 35 percent of the company's revenue.  "
      },
      {
        "line": 64,
        "text": "訳: オンライン販売は現在、その会社の売上高の35パーセントを占めている。  "
      },
      {
        "line": 66,
        "text": "・`constitute a large/significant part of 〈whole〉`  "
      },
      {
        "line": 67,
        "text": "用途: ある要素が全体の大きな部分・重要部分を占めることを示す。  "
      },
      {
        "line": 68,
        "text": "例: Maintenance costs constitute a significant part of the annual budget.  "
      },
      {
        "line": 69,
        "text": "訳: 維持費は年間予算のかなりの部分を占める。  "
      },
      {
        "line": 71,
        "text": "・`be constituted of 〈parts/materials〉`  "
      },
      {
        "line": 72,
        "text": "用途: 全体を主語にして、その構成要素や材料を示す硬い受動表現。  "
      },
      {
        "line": 73,
        "text": "例: The panel is constituted of experts from five different fields.  "
      },
      {
        "line": 74,
        "text": "訳: その委員会は5つの異なる分野の専門家で構成されている。  "
      },
      {
        "line": 111,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 121,
        "text": "【コロケーション】"
      },
      {
        "line": 123,
        "text": "・`constitute a crime/offence`  "
      },
      {
        "line": 124,
        "text": "用途: ある行為が法律上の犯罪・違反に当たり得ることを述べる。  "
      },
      {
        "line": 125,
        "text": "例: Deliberately altering the records may constitute a criminal offence.  "
      },
      {
        "line": 126,
        "text": "訳: 記録を故意に改ざんすることは、刑事犯罪に当たる可能性がある。  "
      },
      {
        "line": 128,
        "text": "・`constitute a breach/violation of 〈rule/duty〉`  "
      },
      {
        "line": 129,
        "text": "用途: 行為・不作為が契約、規則、義務などへの違反に当たると判断する。  "
      },
      {
        "line": 130,
        "text": "例: Sharing the data without permission would constitute a breach of the agreement.  "
      },
      {
        "line": 131,
        "text": "訳: 許可なくデータを共有すれば、その契約への違反に当たる。  "
      },
      {
        "line": 133,
        "text": "・`constitute a threat/risk to 〈person/system〉`  "
      },
      {
        "line": 134,
        "text": "用途: 状況・存在が人や制度への脅威・危険となることを示す。  "
      },
      {
        "line": 135,
        "text": "例: The damaged bridge constitutes a serious risk to public safety.  "
      },
      {
        "line": 136,
        "text": "訳: その損傷した橋は公共の安全に対する重大な危険となっている。  "
      },
      {
        "line": 138,
        "text": "・`constitute evidence/proof of 〈事実〉`  "
      },
      {
        "line": 139,
        "text": "用途: ある資料・行為が、事実を裏づける証拠に当たるかを論じる。  "
      },
      {
        "line": 140,
        "text": "例: A single anonymous message does not constitute proof of fraud.  "
      },
      {
        "line": 141,
        "text": "訳: 匿名のメッセージ一通だけでは、詐欺の証明にはならない。  "
      },
      {
        "line": 143,
        "text": "・`constitute a significant change/improvement`  "
      },
      {
        "line": 144,
        "text": "用途: 出来事や措置が、単なる小差ではなく、意味のある変化・改善に当たると評価する。  "
      },
      {
        "line": 145,
        "text": "例: The revised policy constitutes a significant change in the company's approach.  "
      },
      {
        "line": 146,
        "text": "訳: 改訂された方針は、その会社の取り組み方の大きな変化に当たる。  "
      },
      {
        "line": 148,
        "text": "・`what constitutes 〈category/standard〉`  "
      },
      {
        "line": 149,
        "text": "用途: 何がある概念・分類・基準に該当するのかを問う・定義する。  "
      },
      {
        "line": 150,
        "text": "例: The guidelines explain what constitutes acceptable use of the system.  "
      },
      {
        "line": 151,
        "text": "訳: その指針は、どのようなシステム利用が許容されるかを説明している。  "
      },
      {
        "line": 188,
        "text": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える"
      },
      {
        "line": 198,
        "text": "【コロケーション】"
      },
      {
        "line": 200,
        "text": "・`constitute a committee/panel`  "
      },
      {
        "line": 201,
        "text": "用途: 特定の目的をもつ委員会や審査団を正式に設ける。  "
      },
      {
        "line": 202,
        "text": "例: The ministry constituted an independent panel to investigate the accident.  "
      },
      {
        "line": 203,
        "text": "訳: 同省は、その事故を調査する独立委員会を正式に設置した。  "
      },
      {
        "line": 205,
        "text": "・`constitute a court/tribunal`  "
      },
      {
        "line": 206,
        "text": "用途: 裁判所・審判機関を正式に設ける。  "
      },
      {
        "line": 207,
        "text": "例: The treaty provides for a tribunal to be constituted when a dispute arises.  "
      },
      {
        "line": 208,
        "text": "訳: その条約は、紛争が生じた際に審判機関を設置することを定めている。  "
      },
      {
        "line": 210,
        "text": "・`constitute a government/authority`  "
      },
      {
        "line": 211,
        "text": "用途: 政府・公的機関を正式な組織体として成立させる。  "
      },
      {
        "line": 212,
        "text": "例: The parties agreed to constitute a transitional government.  "
      },
      {
        "line": 213,
        "text": "訳: 当事者らは暫定政府を発足させることで合意した。  "
      },
      {
        "line": 215,
        "text": "・`be constituted under 〈law/charter〉`  "
      },
      {
        "line": 216,
        "text": "用途: 組織が法律・憲章などを根拠として設立されていることを示す。  "
      },
      {
        "line": 217,
        "text": "例: The commission was constituted under the new environmental law.  "
      },
      {
        "line": 218,
        "text": "訳: その委員会は新しい環境法に基づいて設置された。  "
      },
      {
        "line": 220,
        "text": "・`a duly/properly constituted 〈body/meeting〉`  "
      },
      {
        "line": 221,
        "text": "用途: 機関・会議が必要な手続きや構成要件を満たして正式に成立していることを示す。  "
      },
      {
        "line": 222,
        "text": "例: Only a duly constituted board may approve the transaction.  "
      },
      {
        "line": 223,
        "text": "訳: 正式に構成された取締役会だけが、その取引を承認できる。  "
      },
      {
        "line": 255,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 265,
        "text": "【コロケーション】"
      },
      {
        "line": 267,
        "text": "・`constitute someone 〈office/role〉`  "
      },
      {
        "line": 268,
        "text": "用途: 人を特定の役職・職務に就けることを、古風または法律的に述べる。  "
      },
      {
        "line": 269,
        "text": "例: The charter constituted him treasurer of the association.  "
      },
      {
        "line": 270,
        "text": "訳: その憲章によって、彼は協会の会計役に任命された。  "
      },
      {
        "line": 272,
        "text": "・`be constituted 〈office/role〉`  "
      },
      {
        "line": 273,
        "text": "用途: 人が役職・地位に正式に任命されたことを受動態で示す。  "
      },
      {
        "line": 274,
        "text": "例: She was constituted guardian for the limited purpose stated in the order.  "
      },
      {
        "line": 275,
        "text": "訳: 彼女は、その命令に記された限定的な目的のための後見人に任命された。  "
      },
      {
        "line": 277,
        "text": "・`a legally constituted 〈officer/official〉`  "
      },
      {
        "line": 278,
        "text": "用途: 法や制度に基づいて正式に任命された役職者を指す。  "
      },
      {
        "line": 279,
        "text": "例: The charter identifies the treasurer as a legally constituted officer of the association.  "
      },
      {
        "line": 280,
        "text": "訳: その憲章は、会計役を協会において法に基づき正式に任命された役職者として明記している。  "
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
  "source_artifact_sha256": "f98ceb46d53d98a15da050b7cf90ea946c481b3b4bfa6a28e16261031574c94b",
  "normalized_input_sha256": "f3437b588fe7bd5d8d80538dee057b57f53fb8fae74da6f2283fe592f0e02b7c"
}
```
