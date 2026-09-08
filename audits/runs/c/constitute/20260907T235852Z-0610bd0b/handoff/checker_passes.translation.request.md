# Independent checker handoff

Stage: `checker_passes/translation`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.translation.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
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
  "input_body_sha256": "bc5fd320a4e6026bd4209c99c588e7f87029232f85f6c73b9b166ce053d5b6f1",
  "input_sections": {
    "definitions": [
      {
        "line": 41,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 43,
        "text": "【日本語訳・定義】複数の人・物・部分・期間などが、集まって一つの全体を形作る、またはその全体の一定割合・重要部分を占めることを表す。基本の能動構文では、主語が構成要素、目的語がそれらによってできる全体である。意図的に組み立てる行為ではなく、部分と全体の関係を記述することが多い。  "
      },
      {
        "line": 113,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 115,
        "text": "【日本語訳・定義】行為、状況、事実、結果などが、ある分類・評価・状態の定義や成立条件を満たし、そのものと見なせることを表す。目的語には crime、breach、threat、evidence、change、problem などが来る。法律用語だけではなく一般の評価にも使うが、何がその分類に当たるかをやや改まって判断する響きがある。  "
      },
      {
        "line": 190,
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 192,
        "text": "【日本語訳・定義】組織、委員会、裁判所、政府などを、所定の手続き・権限・構成によって正式に作り、活動できる形にする。単に人を集めるだけでなく、公式の組織体として成立させる意味を持つ。設立手続きや法的効果の具体的内容は制度・法域によって異なる。  "
      },
      {
        "line": 262,
        "text": "4. 【他動詞・公式・法律】（人を役職・資格に）任命する、～の資格を与える"
      },
      {
        "line": 264,
        "text": "【日本語訳・定義】権限をもつ者・法律・公式文書などが、人を特定の職務・地位・役割に就け、その資格で行動できるようにする。現代の日常英語ではまれで、appoint や designate が普通である。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 41,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 51,
        "text": "【コロケーション】"
      },
      {
        "line": 53,
        "text": "・`〈parts/members〉 constitute 〈whole/group〉`  "
      },
      {
        "line": 54,
        "text": "用途: 複数の部分・構成員が一つの全体や集団を作ることを述べる。  "
      },
      {
        "line": 55,
        "text": "例: Twelve jurors constitute the full jury in this court.  "
      },
      {
        "line": 56,
        "text": "訳: この裁判所では、12人の陪審員が陪審全体を構成する。  "
      },
      {
        "line": 58,
        "text": "・`constitute the majority/minority of 〈group〉`  "
      },
      {
        "line": 59,
        "text": "用途: ある分類の人・物が、集団の過半数または少数派を占めることを述べる。  "
      },
      {
        "line": 60,
        "text": "例: Part-time employees constitute the majority of the evening staff.  "
      },
      {
        "line": 61,
        "text": "訳: 非常勤職員が夜間スタッフの大半を占めている。  "
      },
      {
        "line": 63,
        "text": "・`constitute 〈percentage〉 of 〈whole〉`  "
      },
      {
        "line": 64,
        "text": "用途: 全体に占める割合を、統計的・客観的に示す。  "
      },
      {
        "line": 65,
        "text": "例: Online sales now constitute 35 percent of the company's revenue.  "
      },
      {
        "line": 66,
        "text": "訳: オンライン販売は現在、その会社の売上高の35パーセントを占めている。  "
      },
      {
        "line": 68,
        "text": "・`constitute a large/significant part of 〈whole〉`  "
      },
      {
        "line": 69,
        "text": "用途: ある要素が全体の大きな部分・重要部分を占めることを示す。  "
      },
      {
        "line": 70,
        "text": "例: Maintenance costs constitute a significant part of the annual budget.  "
      },
      {
        "line": 71,
        "text": "訳: 維持費は年間予算のかなりの部分を占める。  "
      },
      {
        "line": 73,
        "text": "・`be constituted of 〈parts/materials〉`  "
      },
      {
        "line": 74,
        "text": "用途: 全体を主語にして、その構成要素や材料を示す硬い受動表現。  "
      },
      {
        "line": 75,
        "text": "例: The panel is constituted of experts from five different fields.  "
      },
      {
        "line": 76,
        "text": "訳: その委員会は5つの異なる分野の専門家で構成されている。  "
      },
      {
        "line": 113,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 123,
        "text": "【コロケーション】"
      },
      {
        "line": 125,
        "text": "・`constitute a crime/offence`  "
      },
      {
        "line": 126,
        "text": "用途: ある行為が法律上の犯罪・違反に当たり得ることを述べる。  "
      },
      {
        "line": 127,
        "text": "例: Deliberately altering the records may constitute a criminal offence.  "
      },
      {
        "line": 128,
        "text": "訳: 記録を故意に改ざんすることは、刑事犯罪に当たる可能性がある。  "
      },
      {
        "line": 130,
        "text": "・`constitute a breach/violation of 〈rule/duty〉`  "
      },
      {
        "line": 131,
        "text": "用途: 行為・不作為が契約、規則、義務などへの違反に当たると判断する。  "
      },
      {
        "line": 132,
        "text": "例: Sharing the data without permission would constitute a breach of the agreement.  "
      },
      {
        "line": 133,
        "text": "訳: 許可なくデータを共有すれば、その契約への違反に当たる。  "
      },
      {
        "line": 135,
        "text": "・`constitute a threat/risk to 〈person/system〉`  "
      },
      {
        "line": 136,
        "text": "用途: 状況・存在が人や制度への脅威・危険となることを示す。  "
      },
      {
        "line": 137,
        "text": "例: The damaged bridge constitutes a serious risk to public safety.  "
      },
      {
        "line": 138,
        "text": "訳: その損傷した橋は公共の安全に対する重大な危険となっている。  "
      },
      {
        "line": 140,
        "text": "・`constitute evidence/proof of 〈事実〉`  "
      },
      {
        "line": 141,
        "text": "用途: ある資料・行為が、事実を裏づける証拠に当たるかを論じる。  "
      },
      {
        "line": 142,
        "text": "例: A single anonymous message does not constitute proof of fraud.  "
      },
      {
        "line": 143,
        "text": "訳: 匿名のメッセージ一通だけでは、詐欺の証明にはならない。  "
      },
      {
        "line": 145,
        "text": "・`constitute a significant change/improvement`  "
      },
      {
        "line": 146,
        "text": "用途: 出来事や措置が、単なる小差ではなく、意味のある変化・改善に当たると評価する。  "
      },
      {
        "line": 147,
        "text": "例: The revised policy constitutes a significant change in the company's approach.  "
      },
      {
        "line": 148,
        "text": "訳: 改訂された方針は、その会社の取り組み方の大きな変化に当たる。  "
      },
      {
        "line": 150,
        "text": "・`what constitutes 〈category/standard〉`  "
      },
      {
        "line": 151,
        "text": "用途: 何がある概念・分類・基準に該当するのかを問う・定義する。  "
      },
      {
        "line": 152,
        "text": "例: The guidelines explain what constitutes acceptable use of the system.  "
      },
      {
        "line": 153,
        "text": "訳: その指針は、何がシステムの許容される使用に当たるかを説明している。  "
      },
      {
        "line": 190,
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 200,
        "text": "【コロケーション】"
      },
      {
        "line": 202,
        "text": "・`constitute a committee/panel`  "
      },
      {
        "line": 203,
        "text": "用途: 特定の目的・権限・構成員を持つ委員会や審査団を正式に設ける。  "
      },
      {
        "line": 204,
        "text": "例: The ministry constituted an independent panel to investigate the accident.  "
      },
      {
        "line": 205,
        "text": "訳: 同省は、その事故を調査する独立委員会を正式に設置した。  "
      },
      {
        "line": 207,
        "text": "・`constitute a court/tribunal`  "
      },
      {
        "line": 208,
        "text": "用途: 裁判所・審判機関を権限ある機関として正式に設ける。  "
      },
      {
        "line": 209,
        "text": "例: The treaty provides for a tribunal to be constituted when a dispute arises.  "
      },
      {
        "line": 210,
        "text": "訳: その条約は、紛争が生じた際に審判機関を設置することを定めている。  "
      },
      {
        "line": 212,
        "text": "・`constitute a government/authority`  "
      },
      {
        "line": 213,
        "text": "用途: 政府・公的機関を正式な組織体として成立させる。  "
      },
      {
        "line": 214,
        "text": "例: The parties agreed to constitute a transitional government.  "
      },
      {
        "line": 215,
        "text": "訳: 各党は暫定政府を発足させることで合意した。  "
      },
      {
        "line": 217,
        "text": "・`be constituted under 〈law/charter〉`  "
      },
      {
        "line": 218,
        "text": "用途: 組織が法律・憲章などを根拠として設立されていることを示す。  "
      },
      {
        "line": 219,
        "text": "例: The commission was constituted under the new environmental law.  "
      },
      {
        "line": 220,
        "text": "訳: その委員会は新しい環境法に基づいて設置された。  "
      },
      {
        "line": 222,
        "text": "・`a duly/properly constituted 〈body/meeting〉`  "
      },
      {
        "line": 223,
        "text": "用途: 機関・会議が必要な手続きや構成要件を満たして正式に成立していることを示す。  "
      },
      {
        "line": 224,
        "text": "例: Only a duly constituted board may approve the transaction.  "
      },
      {
        "line": 225,
        "text": "訳: 正式に構成された取締役会だけが、その取引を承認できる。  "
      },
      {
        "line": 262,
        "text": "4. 【他動詞・公式・法律】（人を役職・資格に）任命する、～の資格を与える"
      },
      {
        "line": 272,
        "text": "【コロケーション】"
      },
      {
        "line": 274,
        "text": "・`constitute someone as 〈agent/representative〉`  "
      },
      {
        "line": 275,
        "text": "用途: 人を代理人・代表者として正式に指定し、権限を与える。  "
      },
      {
        "line": 276,
        "text": "例: The document constituted her as the owner's legal representative.  "
      },
      {
        "line": 277,
        "text": "訳: その文書は、彼女を所有者の法的代理人として正式に指定した。  "
      },
      {
        "line": 279,
        "text": "・`constitute someone 〈office/role〉`  "
      },
      {
        "line": 280,
        "text": "用途: 人を特定の役職・職務に就けることを、古風または法律的に述べる。  "
      },
      {
        "line": 281,
        "text": "例: The charter constituted him treasurer of the association.  "
      },
      {
        "line": 282,
        "text": "訳: その憲章によって、彼は協会の会計役に任命された。  "
      },
      {
        "line": 284,
        "text": "・`be constituted 〈office/role〉`  "
      },
      {
        "line": 285,
        "text": "用途: 人が権限ある手続きによって役職・資格を与えられたことを受動態で示す。  "
      },
      {
        "line": 286,
        "text": "例: She was constituted guardian for the limited purpose stated in the order.  "
      },
      {
        "line": 287,
        "text": "訳: 彼女は、その命令に記された限定的な目的のための後見人に任命された。  "
      },
      {
        "line": 289,
        "text": "・`constituted authorities`  "
      },
      {
        "line": 290,
        "text": "用途: 法律・制度に従って正式な権限を与えられている政府・当局を集合的に指す。  "
      },
      {
        "line": 291,
        "text": "例: Citizens were urged to report the matter to the constituted authorities.  "
      },
      {
        "line": 292,
        "text": "訳: 市民には、その件を正式な権限をもつ当局へ報告するよう求められた。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 41,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 83,
        "text": "【類義語】"
      },
      {
        "line": 85,
        "text": "・make up  "
      },
      {
        "line": 86,
        "text": "定義: 複数の部分・人が集まって全体を構成する。  "
      },
      {
        "line": 87,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 88,
        "text": "違い: make up は constitute より口語的で幅広い。`A and B make up X` と同じ parts-to-whole の向きで使える。  "
      },
      {
        "line": 89,
        "text": "例: Small firms make up most of the local economy.  "
      },
      {
        "line": 90,
        "text": "訳: 小規模企業が地域経済の大部分を構成している。  "
      },
      {
        "line": 92,
        "text": "・form  "
      },
      {
        "line": 93,
        "text": "定義: 部分が集まって全体・形・集団を作る。  "
      },
      {
        "line": 94,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 95,
        "text": "違い: form は中立的で、構成関係にも実際に作る過程にも使える。constitute は硬く、部分と全体の関係を分類・統計として述べることが多い。  "
      },
      {
        "line": 96,
        "text": "例: These streams form the main river.  "
      },
      {
        "line": 97,
        "text": "訳: これらの小川が合流して本流を形作る。  "
      },
      {
        "line": 99,
        "text": "・compose  "
      },
      {
        "line": 100,
        "text": "定義: 複数の要素が全体を構成する。  "
      },
      {
        "line": 101,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 102,
        "text": "違い: compose は構成要素の組み合わせに焦点があり、受動の `be composed of` が特に一般的である。constitute は割合を述べる構文にもよく使う。  "
      },
      {
        "line": 103,
        "text": "例: Four short sections compose the final movement.  "
      },
      {
        "line": 104,
        "text": "訳: 4つの短い部分が終楽章を構成している。  "
      },
      {
        "line": 106,
        "text": "・account for  "
      },
      {
        "line": 107,
        "text": "定義: 数量・割合・原因などのうち、特定の分を占める。  "
      },
      {
        "line": 108,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 109,
        "text": "違い: 割合の用法では近いが、account for は「全体のうちどれだけを説明・占有するか」に焦点がある。constitute は割合だけでなく、部分が全体そのものを形作る関係にも使える。  "
      },
      {
        "line": 110,
        "text": "例: Exports account for nearly half of total sales.  "
      },
      {
        "line": 111,
        "text": "訳: 輸出が総売上高のほぼ半分を占める。  "
      },
      {
        "line": 113,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 160,
        "text": "【類義語】"
      },
      {
        "line": 162,
        "text": "・amount to  "
      },
      {
        "line": 163,
        "text": "定義: 行為・状況が、実質的にある結果・評価と同じである。  "
      },
      {
        "line": 164,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 165,
        "text": "違い: amount to は「結局は～に等しい」という実質的帰結を強調する。constitute は定義・基準への該当を、より公式・分析的に述べやすい。  "
      },
      {
        "line": 166,
        "text": "例: Ignoring repeated warnings amounts to negligence.  "
      },
      {
        "line": 167,
        "text": "訳: 度重なる警告を無視することは、怠慢に等しい。  "
      },
      {
        "line": 169,
        "text": "・qualify as  "
      },
      {
        "line": 170,
        "text": "定義: 必要な条件を満たして、ある分類・資格に該当する。  "
      },
      {
        "line": 171,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 172,
        "text": "違い: qualify as は明示的な条件を満たす点を強調する。constitute は条件が厳密に列挙されていない一般評価にも使える。  "
      },
      {
        "line": 173,
        "text": "例: The structure qualifies as a protected historic building.  "
      },
      {
        "line": 174,
        "text": "訳: その建物は、保護対象の歴史的建造物に該当する。  "
      },
      {
        "line": 176,
        "text": "・count as  "
      },
      {
        "line": 177,
        "text": "定義: 規則・判断・一般的理解の上で、あるものとして数えられる。  "
      },
      {
        "line": 178,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 179,
        "text": "違い: count as は口語的で、日常的な分類にも使いやすい。constitute はより硬く、公式の基準や重大な評価に合う。  "
      },
      {
        "line": 180,
        "text": "例: Does volunteer work count as relevant experience?  "
      },
      {
        "line": 181,
        "text": "訳: ボランティア活動は関連経験として認められますか。  "
      },
      {
        "line": 183,
        "text": "・represent  "
      },
      {
        "line": 184,
        "text": "定義: 状況・出来事が、ある意味・変化・危険などを体現する。  "
      },
      {
        "line": 185,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 186,
        "text": "違い: represent は象徴・典型・意味づけまで広く表す。constitute は主語が実際にその分類・状態に当たるという同一視がより強い。  "
      },
      {
        "line": 187,
        "text": "例: The agreement represents an important step toward peace.  "
      },
      {
        "line": 188,
        "text": "訳: その合意は、平和に向けた重要な一歩を意味する。  "
      },
      {
        "line": 190,
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 232,
        "text": "【類義語】"
      },
      {
        "line": 234,
        "text": "・establish  "
      },
      {
        "line": 235,
        "text": "定義: 組織・制度・関係などを作り、安定して存在するようにする。  "
      },
      {
        "line": 236,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 237,
        "text": "違い: establish は設立全般に使える標準的な語である。constitute は、権限・手続き・構成を整えて公式に成立させる点を強く示す。  "
      },
      {
        "line": 238,
        "text": "例: The university established a new research center.  "
      },
      {
        "line": 239,
        "text": "訳: その大学は新しい研究センターを設立した。  "
      },
      {
        "line": 241,
        "text": "・form  "
      },
      {
        "line": 242,
        "text": "定義: 人・組織・要素を集めて、新しい集団・組織を作る。  "
      },
      {
        "line": 243,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 244,
        "text": "違い: form は日常的で、正式な法的手続きを必ずしも含まない。constitute は公式の権限や所定の構成を伴う文脈に適する。  "
      },
      {
        "line": 245,
        "text": "例: Residents formed a committee to protect the park.  "
      },
      {
        "line": 246,
        "text": "訳: 住民たちは公園を守るために委員会を結成した。  "
      },
      {
        "line": 248,
        "text": "・set up  "
      },
      {
        "line": 249,
        "text": "定義: 組織・制度・仕組みなどを作って動かし始める。  "
      },
      {
        "line": 250,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 251,
        "text": "違い: set up は口語的で、準備・運用開始まで幅広く表す。constitute は設立の公式性・制度性に焦点がある。  "
      },
      {
        "line": 252,
        "text": "例: The city set up a task force to address housing shortages.  "
      },
      {
        "line": 253,
        "text": "訳: 市は住宅不足に対処する特別チームを立ち上げた。  "
      },
      {
        "line": 255,
        "text": "・institute  "
      },
      {
        "line": 256,
        "text": "定義: 制度、手続き、調査などを公式に導入・開始する。  "
      },
      {
        "line": 257,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 258,
        "text": "違い: institute は制度・手続き・訴訟などを開始することに焦点がある。constitute は主に組織体を正式な形に整えて成立させる。  "
      },
      {
        "line": 259,
        "text": "例: The regulator instituted a formal inquiry.  "
      },
      {
        "line": 260,
        "text": "訳: 規制当局は正式な調査を開始した。  "
      },
      {
        "line": 262,
        "text": "4. 【他動詞・公式・法律】（人を役職・資格に）任命する、～の資格を与える"
      },
      {
        "line": 299,
        "text": "【類義語】"
      },
      {
        "line": 301,
        "text": "・appoint  "
      },
      {
        "line": 302,
        "text": "定義: 人を役職・職務に正式に就ける。  "
      },
      {
        "line": 303,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 304,
        "text": "違い: appoint は現代英語の標準表現で、constitute よりはるかに広く自然に使う。constitute は法律・古風な公式文体に限られやすい。  "
      },
      {
        "line": 305,
        "text": "例: The board appointed Maya treasurer.  "
      },
      {
        "line": 306,
        "text": "訳: 取締役会はマヤを会計責任者に任命した。  "
      },
      {
        "line": 308,
        "text": "・designate  "
      },
      {
        "line": 309,
        "text": "定義: 人を特定の役割・地位の担当者として公式に指定する。  "
      },
      {
        "line": 310,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 311,
        "text": "違い: designate は役割を割り当て、明示することに焦点がある。constitute は古い法律文体で、その資格や権限を正式に成立させる響きが強い。  "
      },
      {
        "line": 312,
        "text": "例: The minister designated Lee as the official spokesperson.  "
      },
      {
        "line": 313,
        "text": "訳: 大臣はリーを公式報道官に指定した。  "
      },
      {
        "line": 315,
        "text": "・name  "
      },
      {
        "line": 316,
        "text": "定義: 人を役職・候補・受賞者などとして発表・指定する。  "
      },
      {
        "line": 317,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 318,
        "text": "違い: name は簡潔で一般的であり、発表・選定に焦点がある。constitute は法的・制度的に地位を与える文脈で使われる。  "
      },
      {
        "line": 319,
        "text": "例: The council named Rivera chair of the committee.  "
      },
      {
        "line": 320,
        "text": "訳: 評議会はリベラを委員会の議長に指名した。  "
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
  "source_artifact_sha256": "64fb191f6d61ca2c5c081905e3d5190bd1799b8fd52554f3d6a5d7629ea69b23",
  "normalized_input_sha256": "031c897042b6aa7933596fa242075745ee460b50cd0cb76d72e54df6d945ca2a"
}
```
