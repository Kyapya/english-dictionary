# Independent checker handoff

Stage: `checker_passes/evidence`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.evidence.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
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
  "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米: /ˈkɑːnstəˌtuːt/｜英: /ˈkɒnstɪˌtjuːt/。3音節で、第1音節に主強勢、第3音節に第二強勢がある。米音では第1音節の母音が /ɑː/、第2音節が弱い /stə/、第3音節の初めが /t/ となる。英音では第1音節が /ɒ/、第2音節が /stɪ/、第3音節が /tjuːt/ となる。  "
      }
    ],
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
        "text": "`constituent` — 名詞「構成要素、選挙区民」、形容詞「構成する」。政治の「選挙区民」は constitute の目的語ではなく、代表者を選ぶ constituency の構成員を指す。  "
      },
      {
        "line": 27,
        "text": "`reconstitute` — 動詞「再構成する、元の状態に戻す」。乾燥食品・薬剤などに液体を加えて戻す用法もある。  "
      }
    ],
    "core_image": [
      {
        "line": 29,
        "text": "＃コアイメージ"
      },
      {
        "line": 31,
        "text": "constitute の共通核は、要素・行為・組織・人を、ある全体・分類・制度・役割として成り立つ位置に据えることである。文脈によって、すでにそうであるという関係を述べる場合と、意図的・正式に成立させる行為を述べる場合がある。  "
      },
      {
        "line": 32,
        "text": "・要素を全体として成り立つ位置に据える → 「構成する、占める」（語義1）  "
      },
      {
        "line": 33,
        "text": "・行為や事実を分類として成り立つ位置に据える → 「～に当たる、～となる」（語義2）  "
      },
      {
        "line": 34,
        "text": "・組織を正式な制度として成り立つ位置に据える → 「正式に設立する、組織する」（語義3）  "
      },
      {
        "line": 35,
        "text": "・人を公的な役割として成り立つ位置に据える → 「正式に任命・指定する」（語義4）  "
      }
    ],
    "sense_structure": [
      {
        "line": 39,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 41,
        "text": "【日本語訳・定義】一つまたは複数の人・物・部分・期間などが、一つの全体を形作る、またはその全体の一定割合・重要部分を占めることを表す。全体構成の能動構文では主語が構成要素、目的語がそれらによってできる全体である。一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は of 句に現れる。意図的に組み立てる行為ではなく、部分と全体の関係を記述することが多い。  "
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
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 190,
        "text": "【日本語訳・定義】組織、委員会、裁判所、政府などを正式に形成・設置し、公式の組織体として成立させることを表す。制度や文脈によって所定の手続きや権限付与を伴うことはあるが、constitute という語だけで法的有効性や実際の活動可能性まで一律に保証するわけではない。  "
      },
      {
        "line": 253,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 255,
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
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 192,
        "text": "【頻度】〈5/10〉  "
      },
      {
        "line": 194,
        "text": "【レジスター/領域】非常に硬い公式・行政・法律・組織運営の用法。一般的な会社・団体の設立では establish、form、set up がより広く使われる。  "
      },
      {
        "line": 253,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 257,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 259,
        "text": "【レジスター/領域】法律・公文書などの公式文体。`a legally constituted officer` のような表現では、法や制度に基づいて正式に任命された役職者を指す。  "
      }
    ],
    "frames": [
      {
        "line": 39,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 47,
        "text": "【文法パターン】`〈parts/members〉 constitute 〈whole/group〉`＝部分・構成員が全体・集団を構成する／`〈group/category〉 constitute 〈割合〉 of 〈whole〉`＝集団・分類が全体の一定割合を占める／`〈whole〉 be constituted of 〈parts〉`＝全体が部分から構成されている  "
      },
      {
        "line": 111,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 119,
        "text": "【文法パターン】`〈act/fact/situation〉 constitute 〈category/result〉`＝行為・事実・状況が分類・結果に当たる／`constitute a crime/breach/violation`＝犯罪・契約違反・規則違反に当たる／`constitute a threat/risk/problem`＝脅威・危険・問題となる／`what constitutes 〈category〉`＝何がその分類を成り立たせるか  "
      },
      {
        "line": 188,
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 196,
        "text": "【文法パターン】`〈authority/institution/parties〉 constitute 〈committee/body/court/government〉`＝権限主体・機関・当事者が委員会・機関・裁判所・政府を正式に設ける／`〈body〉 be constituted under/by 〈law/authority〉`＝機関が法律・権限に基づいて設立される／`a properly/legally/duly constituted 〈body/authority〉`＝適切・合法・正式に成立した機関・権限主体  "
      },
      {
        "line": 253,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 261,
        "text": "【文法パターン】`〈authority/law/document〉 constitute someone 〈office/role〉`＝権限者・法律・公式文書が人を役職・役割に任命する／`someone be constituted 〈office/role〉`＝人が役職に任命される／`a legally constituted 〈officer/official〉`＝法に基づいて正式に任命された役職者  "
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
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
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
        "line": 253,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 263,
        "text": "【コロケーション】"
      },
      {
        "line": 265,
        "text": "・`constitute someone 〈office/role〉`  "
      },
      {
        "line": 266,
        "text": "用途: 人を特定の役職・職務に就けることを、古風または法律的に述べる。  "
      },
      {
        "line": 267,
        "text": "例: The charter constituted him treasurer of the association.  "
      },
      {
        "line": 268,
        "text": "訳: その憲章によって、彼は協会の会計役に任命された。  "
      },
      {
        "line": 270,
        "text": "・`be constituted 〈office/role〉`  "
      },
      {
        "line": 271,
        "text": "用途: 人が役職・地位に正式に任命されたことを受動態で示す。  "
      },
      {
        "line": 272,
        "text": "例: She was constituted guardian for the limited purpose stated in the order.  "
      },
      {
        "line": 273,
        "text": "訳: 彼女は、その命令に記された限定的な目的のための後見人に任命された。  "
      },
      {
        "line": 275,
        "text": "・`a legally constituted 〈officer/official〉`  "
      },
      {
        "line": 276,
        "text": "用途: 法や制度に基づいて正式に任命された役職者を指す。  "
      },
      {
        "line": 277,
        "text": "例: The charter identifies the treasurer as a legally constituted officer of the association.  "
      },
      {
        "line": 278,
        "text": "訳: その憲章は、会計役を協会において法に基づき正式に任命された役職者として明記している。  "
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
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 225,
        "text": "【語法・注意】語義1の「部分が全体を構成している」は状態的な関係、語義3の「組織を正式に設立する」は意図的・制度的な行為である。`The members constitute the board.` は「構成員が取締役会を構成する」、`The agency constituted a board.` は「機関が取締役会を正式に設置した」となる。  "
      },
      {
        "line": 253,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 280,
        "text": "【語法・注意】人を直接目的語にし、役職を目的格補語として置く `constitute someone treasurer` のような形で使う。現代の一般文では非常に硬いため、通常は `appoint someone treasurer` などとする。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 39,
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "line": 81,
        "text": "【類義語】"
      },
      {
        "line": 83,
        "text": "・make up  "
      },
      {
        "line": 84,
        "text": "定義: 複数の部分・人が集まって全体を構成する。  "
      },
      {
        "line": 85,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 86,
        "text": "違い: make up は constitute より口語的で幅広い。`A and B make up X` と同じ parts-to-whole の向きで使える。  "
      },
      {
        "line": 87,
        "text": "例: Small firms make up most of the local economy.  "
      },
      {
        "line": 88,
        "text": "訳: 小規模企業が地域経済の大部分を構成している。  "
      },
      {
        "line": 90,
        "text": "・form  "
      },
      {
        "line": 91,
        "text": "定義: 部分が集まって全体・形・集団を作る。  "
      },
      {
        "line": 92,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 93,
        "text": "違い: form は中立的で、構成関係にも実際に作る過程にも使える。constitute は硬く、部分と全体の関係を分類・統計として述べることが多い。  "
      },
      {
        "line": 94,
        "text": "例: These streams form the main river.  "
      },
      {
        "line": 95,
        "text": "訳: これらの小川が本流を形作っている。  "
      },
      {
        "line": 97,
        "text": "・compose  "
      },
      {
        "line": 98,
        "text": "定義: 複数の要素が全体を構成する。  "
      },
      {
        "line": 99,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 100,
        "text": "違い: compose は構成要素の組み合わせに焦点があり、受動の `be composed of` が特に一般的である。constitute は割合を述べる構文にもよく使う。  "
      },
      {
        "line": 101,
        "text": "例: Four short sections compose the final movement.  "
      },
      {
        "line": 102,
        "text": "訳: 4つの短い部分が終楽章を構成している。  "
      },
      {
        "line": 104,
        "text": "・account for  "
      },
      {
        "line": 105,
        "text": "定義: 数量・割合・原因などのうち、特定の分を占める。  "
      },
      {
        "line": 106,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 107,
        "text": "違い: 割合の用法では近いが、account for は「全体のうちどれだけを説明・占有するか」に焦点がある。constitute は割合だけでなく、部分が全体そのものを形作る関係にも使える。  "
      },
      {
        "line": 108,
        "text": "例: Exports account for nearly half of total sales.  "
      },
      {
        "line": 109,
        "text": "訳: 輸出が総売上高のほぼ半分を占める。  "
      },
      {
        "line": 111,
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "line": 158,
        "text": "【類義語】"
      },
      {
        "line": 160,
        "text": "・amount to  "
      },
      {
        "line": 161,
        "text": "定義: 行為・状況が、実質的にある結果・評価と同じである。  "
      },
      {
        "line": 162,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 163,
        "text": "違い: amount to は「結局は～に等しい」という実質的帰結を強調する。constitute は定義・基準への該当を、より公式・分析的に述べやすい。  "
      },
      {
        "line": 164,
        "text": "例: Ignoring repeated warnings amounts to negligence.  "
      },
      {
        "line": 165,
        "text": "訳: 度重なる警告を無視することは、怠慢に等しい。  "
      },
      {
        "line": 167,
        "text": "・qualify as  "
      },
      {
        "line": 168,
        "text": "定義: 必要な条件を満たして、ある分類・資格に該当する。  "
      },
      {
        "line": 169,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 170,
        "text": "違い: qualify as は明示的な条件を満たす点を強調する。constitute は条件が厳密に列挙されていない一般評価にも使える。  "
      },
      {
        "line": 171,
        "text": "例: The structure qualifies as a protected historic building.  "
      },
      {
        "line": 172,
        "text": "訳: その構造物は、保護対象の歴史的建造物に該当する。  "
      },
      {
        "line": 174,
        "text": "・count as  "
      },
      {
        "line": 175,
        "text": "定義: 規則・判断・一般的理解の上で、あるものとして数えられる。  "
      },
      {
        "line": 176,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 177,
        "text": "違い: count as は口語的で、日常的な分類にも使いやすい。constitute はより硬く、公式の基準や重大な評価に合う。  "
      },
      {
        "line": 178,
        "text": "例: Does volunteer work count as relevant experience?  "
      },
      {
        "line": 179,
        "text": "訳: ボランティア活動は関連経験として認められますか。  "
      },
      {
        "line": 181,
        "text": "・represent  "
      },
      {
        "line": 182,
        "text": "定義: 状況・出来事が、ある意味・変化・危険などを体現する。  "
      },
      {
        "line": 183,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 184,
        "text": "違い: represent は象徴・典型・意味づけまで広く表す。constitute は主語が実際にその分類・状態に当たるという同一視がより強い。  "
      },
      {
        "line": 185,
        "text": "例: The agreement represents an important step toward peace.  "
      },
      {
        "line": 186,
        "text": "訳: その合意は、平和に向けた重要な一歩を意味する。  "
      },
      {
        "line": 188,
        "text": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する"
      },
      {
        "line": 230,
        "text": "【類義語】"
      },
      {
        "line": 232,
        "text": "・establish  "
      },
      {
        "line": 233,
        "text": "定義: 組織・制度・関係などを作り、安定して存在するようにする。  "
      },
      {
        "line": 234,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 235,
        "text": "違い: establish は設立全般に使える標準的な語である。constitute は、組織体を公式な形で成立させる硬い表現である。  "
      },
      {
        "line": 236,
        "text": "例: The university established a new research center.  "
      },
      {
        "line": 237,
        "text": "訳: その大学は新しい研究センターを設立した。  "
      },
      {
        "line": 239,
        "text": "・form  "
      },
      {
        "line": 240,
        "text": "定義: 人・組織・要素を集めて、新しい集団・組織を作る。  "
      },
      {
        "line": 241,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 242,
        "text": "違い: form は日常的で、正式な法的手続きを必ずしも含まない。constitute は公式・制度的な文脈で使われやすい。  "
      },
      {
        "line": 243,
        "text": "例: Residents formed a committee to protect the park.  "
      },
      {
        "line": 244,
        "text": "訳: 住民たちは公園を守るために委員会を結成した。  "
      },
      {
        "line": 246,
        "text": "・set up  "
      },
      {
        "line": 247,
        "text": "定義: 組織・制度・仕組みなどを作って動かし始める。  "
      },
      {
        "line": 248,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 249,
        "text": "違い: set up は口語的で、準備・運用開始まで幅広く表す。constitute は設立の公式性・制度性に焦点がある。  "
      },
      {
        "line": 250,
        "text": "例: The city set up a task force to address housing shortages.  "
      },
      {
        "line": 251,
        "text": "訳: 市は住宅不足に対処する特別チームを立ち上げた。  "
      },
      {
        "line": 253,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 285,
        "text": "【類義語】"
      },
      {
        "line": 287,
        "text": "・appoint  "
      },
      {
        "line": 288,
        "text": "定義: 人を役職・職務に正式に就ける。  "
      },
      {
        "line": 289,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 290,
        "text": "違い: appoint は現代英語の標準表現で、constitute より広く自然に使う。constitute は法律・公文書などの硬い公式文体に現れる。  "
      },
      {
        "line": 291,
        "text": "例: The board appointed Maya treasurer.  "
      },
      {
        "line": 292,
        "text": "訳: 取締役会はマヤを会計責任者に任命した。  "
      },
      {
        "line": 294,
        "text": "・designate  "
      },
      {
        "line": 295,
        "text": "定義: 人を特定の役割・地位の担当者として公式に指定する。  "
      },
      {
        "line": 296,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 297,
        "text": "違い: designate は役割を割り当て、明示することに焦点がある。constitute は法律・公式文体で、人をその役職・地位に正式に就けることを表す。  "
      },
      {
        "line": 298,
        "text": "例: The minister designated Lee as the official spokesperson.  "
      },
      {
        "line": 299,
        "text": "訳: 大臣はリーを公式報道官に指定した。  "
      },
      {
        "line": 301,
        "text": "・name  "
      },
      {
        "line": 302,
        "text": "定義: 人を役職・候補・受賞者などとして発表・指定する。  "
      },
      {
        "line": 303,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 304,
        "text": "違い: name は簡潔で一般的であり、発表・選定に焦点がある。constitute は法律・制度上の役職へ正式に任命する文脈で使われる。  "
      },
      {
        "line": 305,
        "text": "例: The council named Rivera chair of the committee.  "
      },
      {
        "line": 306,
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
  "evidence_context": {
    "schema_version": "evidence_context_v1",
    "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "c5afd0e4702fa4f6abcca1d9de93b5b51b4d5243adfdd2ede8fac110d10b33a4",
    "source_first_artifact_sha256": "f98ceb46d53d98a15da050b7cf90ea946c481b3b4bfa6a28e16261031574c94b",
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
        "id": "collins-constitute",
        "locator": "https://www.collinsdictionary.com/dictionary/english/constitute",
        "source_type": "dictionary",
        "independence_group": "collins",
        "facts": [
          {
            "id": "F009",
            "form": "constitute",
            "kind": "pronunciation",
            "statement": "British pronunciation uses /ɒ/ and /tjuːt/, while the American form commonly uses /tuːt/.",
            "source_detail": "Collins COBUILD and British/American pronunciation entries contrast UK /ˈkɒnstɪtjuːt/ with a US ending /tuːt/."
          },
          {
            "id": "F010",
            "form": "constitute",
            "kind": "grammar",
            "statement": "The equivalence sense is a non-continuous linking-like verb followed directly by a noun phrase.",
            "source_detail": "Collins COBUILD labels the sense link verb, no continuous, with the pattern VERB noun and examples constitute an offence and constitute a victory."
          },
          {
            "id": "F011",
            "form": "constitute",
            "kind": "definition",
            "statement": "People or things constitute a whole when they are the parts or members forming it, including a stated percentage.",
            "source_detail": "Collins COBUILD sense 2 defines the parts-to-whole relation and illustrates volunteers constituting over 95 percent of a workforce."
          },
          {
            "id": "F012",
            "form": "constitute",
            "kind": "definition",
            "statement": "A committee, government, court, or similar body is constituted when formally established and authorized to operate.",
            "source_detail": "Collins COBUILD sense 3 and British senses 3-4 record formal establishment and legal form for institutions and courts."
          },
          {
            "id": "F013",
            "form": "constitute",
            "kind": "definition",
            "statement": "Constitute can give a person an office or function, including in passive constituted expressions.",
            "source_detail": "Collins British and American entries define appointment and give legally constituted officer and he was constituted treasurer."
          },
          {
            "id": "F014",
            "form": "constituted",
            "kind": "grammar",
            "statement": "The passive construction constituted of can identify the materials or parts composing a whole.",
            "source_detail": "Collins American entry illustrates mortar constituted of lime and sand."
          },
          {
            "id": "F016",
            "form": "constituted",
            "kind": "register",
            "statement": "The formal-establishment use is formal and is commonly realized in the passive.",
            "source_detail": "Collins COBUILD labels the body-establishment sense formal and usually passive."
          }
        ]
      },
      {
        "id": "etymonline-constitute",
        "locator": "https://www.etymonline.com/word/constitute",
        "source_type": "etymology_reference",
        "independence_group": "etymonline",
        "facts": [
          {
            "id": "F017",
            "form": "constitute",
            "kind": "definition",
            "statement": "The parts-to-whole formation sense is recorded from the mid-fifteenth century.",
            "source_detail": "Etymonline dates the formation-as-a-necessary-part sense to the mid-15th century."
          },
          {
            "id": "F018",
            "form": "constitute",
            "kind": "etymology",
            "statement": "Latin constituere covered causing to stand, setting up, fixing, establishing, and forming something new.",
            "source_detail": "Etymonline lists these meanings for Latin constituere."
          },
          {
            "id": "F019",
            "form": "constitute",
            "kind": "register",
            "statement": "The appoint-to-office sense is historically old and is recorded from around 1400.",
            "source_detail": "Etymonline dates appoint or elect to an office or position of power to about 1400."
          },
          {
            "id": "F020",
            "form": "constitute",
            "kind": "etymology",
            "statement": "The Latin source combines an assimilated form of com- with statuere to set, ultimately related to the root meaning stand.",
            "source_detail": "Etymonline analyzes constituere as com- plus statuere and connects statuere to the PIE root meaning stand."
          }
        ]
      },
      {
        "id": "merriam-webster-constituent",
        "locator": "https://www.merriam-webster.com/dictionary/constituent",
        "source_type": "dictionary",
        "independence_group": "merriam-webster",
        "facts": [
          {
            "id": "F024",
            "form": "constituent",
            "kind": "derived_form",
            "statement": "Constituent as a noun can mean an essential component or a member of a political constituency.",
            "source_detail": "Merriam-Webster noun senses distinguish component and constituency-member meanings."
          },
          {
            "id": "F025",
            "form": "constituent",
            "kind": "derived_form",
            "statement": "Constituent as an adjective means serving to form or make up a whole.",
            "source_detail": "Merriam-Webster adjective sense 1 defines constituent as forming or composing a whole."
          }
        ]
      },
      {
        "id": "merriam-webster-constitute",
        "locator": "https://www.merriam-webster.com/dictionary/constitute",
        "source_type": "dictionary",
        "independence_group": "merriam-webster",
        "facts": [
          {
            "id": "F001",
            "form": "constitute",
            "kind": "pronunciation",
            "statement": "American pronunciation has primary stress on the first syllable and permits final /tuːt/ or /tjuːt/.",
            "source_detail": "Merriam-Webster headword pronunciation line records /ˈkän(t)-stə-ˌtüt/ and /-ˌtyüt/."
          },
          {
            "id": "F003",
            "form": "constitute",
            "kind": "definition",
            "statement": "Parts or members constitute a whole by making it up, forming it, or composing it.",
            "source_detail": "Merriam-Webster sense 1 defines constitute as make up, form, compose and gives twelve months constitute a year."
          },
          {
            "id": "F004",
            "form": "constitute",
            "kind": "definition",
            "statement": "Constitute can mean to set up, establish, or found an institution or government.",
            "source_detail": "Merriam-Webster sense 2 includes set up, establish, and constitute a provisional government."
          },
          {
            "id": "F005",
            "form": "constitute",
            "kind": "legal_use",
            "statement": "In legal use constitute can give an agreement or body due or lawful form.",
            "source_detail": "Merriam-Webster general and legal definitions record giving due or required legal form."
          },
          {
            "id": "F006",
            "form": "constitute",
            "kind": "legal_use",
            "statement": "Constitute can appoint a person to an office, function, or dignity.",
            "source_detail": "Merriam-Webster sense 3 and legal sense 1 explicitly record appointment to an office or function."
          },
          {
            "id": "F007",
            "form": "constitute",
            "kind": "legal_use",
            "statement": "An act or document may constitute something by qualifying as it, as when failure to act constitutes negligence.",
            "source_detail": "Merriam-Webster legal sense 3b defines qualify as and illustrates failure to act may constitute negligence."
          },
          {
            "id": "F008",
            "form": "constitute",
            "kind": "etymology",
            "statement": "Constitute came through Middle English from Latin constitutus, the participle of constituere, from com- plus statuere to set.",
            "source_detail": "Merriam-Webster Word History gives the Middle English and Latin derivation and links statuere with set."
          }
        ]
      },
      {
        "id": "merriam-webster-constitution",
        "locator": "https://www.merriam-webster.com/dictionary/constitution",
        "source_type": "dictionary",
        "independence_group": "merriam-webster",
        "facts": [
          {
            "id": "F021",
            "form": "constitution",
            "kind": "derived_form",
            "statement": "Constitution is a noun for structure or physical makeup and for fundamental governing principles or their written instrument.",
            "source_detail": "Merriam-Webster constitution senses cover physical makeup, structure, organization, fundamental laws, and the written governing instrument."
          }
        ]
      },
      {
        "id": "merriam-webster-constitutional",
        "locator": "https://www.merriam-webster.com/dictionary/constitutional",
        "source_type": "dictionary",
        "independence_group": "merriam-webster",
        "facts": [
          {
            "id": "F022",
            "form": "constitutional",
            "kind": "derived_form",
            "statement": "Constitutional is an adjective for constitution-related, constitution-authorized, bodily-constitution, or fundamental-makeup senses.",
            "source_detail": "Merriam-Webster adjective senses cover constitutional law, bodily makeup, and fundamental makeup."
          },
          {
            "id": "F023",
            "form": "constitutionally",
            "kind": "derived_form",
            "statement": "Constitutionally is the adverb derived from constitutional.",
            "source_detail": "Merriam-Webster records constitutionally as an adverb under constitutional."
          }
        ]
      },
      {
        "id": "merriam-webster-reconstitute",
        "locator": "https://www.merriam-webster.com/dictionary/reconstitute",
        "source_type": "dictionary",
        "independence_group": "merriam-webster",
        "facts": [
          {
            "id": "F026",
            "form": "reconstitute",
            "kind": "derived_form",
            "statement": "Reconstitute means constitute again or anew, especially restore by adding water or another liquid.",
            "source_detail": "Merriam-Webster defines reconstitute as constitute again or anew and especially restore by adding water."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "U001",
        "source_fact_ids": [
          "F001",
          "F009"
        ],
        "canonical_statement": "Constitute has first-syllable primary stress, with UK /ɒ/ and /tjuːt/ and common US /ɑː/ and /tuːt/ realizations.",
        "disposition": "included",
        "rationale": "The pronunciation section records the regionally differentiated forms."
      },
      {
        "id": "U003",
        "source_fact_ids": [
          "F003",
          "F011",
          "F017"
        ],
        "canonical_statement": "Parts, members, or a category constitute a whole or a share of it in the parts-to-whole sense.",
        "disposition": "included",
        "rationale": "Sense 1 and its central frames directly express this well-attested relation."
      },
      {
        "id": "U004",
        "source_fact_ids": [
          "F007",
          "F010"
        ],
        "canonical_statement": "An act, fact, or situation constitutes a category when it qualifies as or can be regarded as that category.",
        "disposition": "included",
        "rationale": "Sense 2 separates this linking-like classification meaning from composition."
      },
      {
        "id": "U005",
        "source_fact_ids": [
          "F004",
          "F012",
          "F016",
          "F018"
        ],
        "canonical_statement": "Constitute formally establishes and authorizes an institution, committee, government, court, or similar body.",
        "disposition": "included",
        "rationale": "Sense 3 covers formal institutional establishment and its passive realization."
      },
      {
        "id": "U006",
        "source_fact_ids": [
          "F006",
          "F013",
          "F019"
        ],
        "canonical_statement": "In formal or legal language constitute can appoint a person to an office or function.",
        "disposition": "included",
        "rationale": "Sense 4 includes both direct-complement and as-complement appointment frames and labels their register."
      },
      {
        "id": "U007",
        "source_fact_ids": [
          "F005"
        ],
        "canonical_statement": "Constitute can give a body or agreement the form required for legal validity.",
        "disposition": "integrated",
        "rationale": "The lawful-form aspect is integrated into the formal-establishment sense without asserting universal legal effects."
      },
      {
        "id": "U008",
        "source_fact_ids": [
          "F014"
        ],
        "canonical_statement": "The passive constituted of construction may identify the components of a whole.",
        "disposition": "included",
        "rationale": "Sense 1 teaches this formal passive alongside the active direction contrast."
      },
      {
        "id": "U009",
        "source_fact_ids": [
          "F008",
          "F020"
        ],
        "canonical_statement": "Constitute derives through Middle English from Latin constituere, built from com- and statuere and associated with setting or establishing.",
        "disposition": "included",
        "rationale": "The etymology section presents the attested source and a restrained semantic bridge."
      },
      {
        "id": "U010",
        "source_fact_ids": [
          "F021"
        ],
        "canonical_statement": "Constitution is the related noun for makeup or structure and for fundamental governing principles or their document.",
        "disposition": "included",
        "rationale": "The word-formation section records these principal learner-relevant senses."
      },
      {
        "id": "U011",
        "source_fact_ids": [
          "F022"
        ],
        "canonical_statement": "Constitutional is the related adjective for bodily or structural makeup and for a governing constitution.",
        "disposition": "included",
        "rationale": "The word-formation section records both broad sense families."
      },
      {
        "id": "U012",
        "source_fact_ids": [
          "F023"
        ],
        "canonical_statement": "Constitutionally is the adverb derived from constitutional.",
        "disposition": "included",
        "rationale": "The word-formation section identifies the adverb and its broad meanings."
      },
      {
        "id": "U013",
        "source_fact_ids": [
          "F024",
          "F025"
        ],
        "canonical_statement": "Constituent is a related noun for a component or constituency member and an adjective meaning forming a whole.",
        "disposition": "included",
        "rationale": "The word-formation section distinguishes the noun and adjective and warns against confusing the political noun with a verb object."
      },
      {
        "id": "U014",
        "source_fact_ids": [
          "F026"
        ],
        "canonical_statement": "Reconstitute means constitute anew or restore a material by adding liquid.",
        "disposition": "included",
        "rationale": "The word-formation section records both the compositional and specialized restoration meanings."
      }
    ],
    "claim_units": [
      {
        "id": "C001",
        "union_ids": [
          "U001"
        ],
        "subject_form": "constitute",
        "claim_type": "pronunciation",
        "statement": "Constitute has regionally differentiated UK and US pronunciation patterns.",
        "article_target_ids": [
          "pronunciation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F001",
            "support_summary": "Merriam-Webster directly records the American stressed form and /tuːt/ or /tjuːt/ variation."
          },
          {
            "source_fact_id": "F009",
            "support_summary": "Collins independently contrasts British /ɒ, tjuːt/ with the common American /tuːt/ ending."
          }
        ]
      },
      {
        "id": "C003",
        "union_ids": [
          "U003"
        ],
        "subject_form": "constitute",
        "claim_type": "sense",
        "statement": "Parts or members constitute a whole, and a category may constitute a stated share of the whole.",
        "article_target_ids": [
          "definition:001",
          "grammar_pattern:001",
          "grammar_pattern:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F003",
            "support_summary": "Merriam-Webster defines the parts-to-whole sense as make up, form, or compose."
          },
          {
            "source_fact_id": "F011",
            "support_summary": "Collins independently defines members forming a whole and supplies a percentage example."
          },
          {
            "source_fact_id": "F017",
            "support_summary": "Etymonline confirms that the formation-as-a-part meaning is historically established."
          }
        ]
      },
      {
        "id": "C004",
        "union_ids": [
          "U004"
        ],
        "subject_form": "constitute",
        "claim_type": "sense",
        "statement": "A fact or act constitutes a category when it qualifies as or can be regarded as that category.",
        "article_target_ids": [
          "definition:002",
          "grammar_pattern:004",
          "usage_note:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F007",
            "support_summary": "Merriam-Webster legal usage directly defines constitute as qualify as and illustrates negligence."
          },
          {
            "source_fact_id": "F010",
            "support_summary": "Collins independently defines the regarded-as sense and specifies the direct VERB-noun pattern."
          }
        ]
      },
      {
        "id": "C005",
        "union_ids": [
          "U005"
        ],
        "subject_form": "constitute",
        "claim_type": "sense",
        "statement": "Constitute can formally establish and authorize an institution or public body.",
        "article_target_ids": [
          "definition:003",
          "grammar_pattern:008",
          "collocation:012",
          "collocation:013"
        ],
        "source_supports": [
          {
            "source_fact_id": "F004",
            "support_summary": "Merriam-Webster directly records set up, establish, found, and provisional-government use."
          },
          {
            "source_fact_id": "F012",
            "support_summary": "Collins independently defines formal establishment and authorization for committees and governments."
          },
          {
            "source_fact_id": "F016",
            "support_summary": "Collins marks this institutional-establishment sense formal and commonly passive."
          },
          {
            "source_fact_id": "F018",
            "support_summary": "Etymonline supplies the Latin establish-and-form semantic history supporting the restrained bridge."
          }
        ]
      },
      {
        "id": "C006",
        "union_ids": [
          "U006"
        ],
        "subject_form": "constitute",
        "claim_type": "sense",
        "statement": "Formal or legal constitute can appoint a person to an office or role.",
        "article_target_ids": [
          "definition:004",
          "grammar_pattern:011",
          "grammar_pattern:012",
          "register:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F006",
            "support_summary": "Merriam-Webster directly defines appointment to an office, function, or dignity."
          },
          {
            "source_fact_id": "F013",
            "support_summary": "Collins independently records legally constituted officer and constituted treasurer."
          },
          {
            "source_fact_id": "F019",
            "support_summary": "Etymonline records the appointment sense as an old use, supporting the register warning."
          }
        ]
      },
      {
        "id": "C007",
        "union_ids": [
          "U007"
        ],
        "subject_form": "constitute",
        "claim_type": "legal_use",
        "statement": "Constitute may give a body or agreement the required official or lawful form.",
        "article_target_ids": [
          "definition:003",
          "usage_note:009"
        ],
        "source_supports": [
          {
            "source_fact_id": "F005",
            "support_summary": "Merriam-Webster explicitly records giving an agreement or body due or required legal form."
          }
        ]
      },
      {
        "id": "C008",
        "union_ids": [
          "U008"
        ],
        "subject_form": "constituted of",
        "claim_type": "frame",
        "statement": "Constituted of may present the whole first and its component materials after of.",
        "article_target_ids": [
          "grammar_pattern:003",
          "collocation:005",
          "usage_note:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F014",
            "support_summary": "Collins directly illustrates the passive constituted of construction with material components."
          }
        ]
      },
      {
        "id": "C009",
        "union_ids": [
          "U009"
        ],
        "subject_form": "constitute",
        "claim_type": "etymology",
        "statement": "Constitute descends through Middle English from Latin constituere, involving com- and statuere.",
        "article_target_ids": [
          "etymology:001",
          "etymology:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F008",
            "support_summary": "Merriam-Webster gives the Middle English and Latin participial derivation."
          },
          {
            "source_fact_id": "F020",
            "support_summary": "Etymonline independently analyzes the com- plus statuere formation and stand root."
          }
        ]
      },
      {
        "id": "C010",
        "union_ids": [
          "U010"
        ],
        "subject_form": "constitution",
        "claim_type": "derived_form",
        "statement": "Constitution is the related noun for makeup, structure, or fundamental governing principles.",
        "article_target_ids": [
          "word_formation:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F021",
            "support_summary": "Merriam-Webster directly records structure, physical makeup, governing principles, and document senses."
          }
        ]
      },
      {
        "id": "C011",
        "union_ids": [
          "U011"
        ],
        "subject_form": "constitutional",
        "claim_type": "derived_form",
        "statement": "Constitutional is the related adjective for bodily or structural makeup and governing-constitution senses.",
        "article_target_ids": [
          "word_formation:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "F022",
            "support_summary": "Merriam-Webster directly records constitutional adjective senses for makeup and a governing constitution."
          }
        ]
      },
      {
        "id": "C012",
        "union_ids": [
          "U012"
        ],
        "subject_form": "constitutionally",
        "claim_type": "derived_form",
        "statement": "Constitutionally is the adverb derived from constitutional.",
        "article_target_ids": [
          "word_formation:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "F023",
            "support_summary": "Merriam-Webster explicitly lists constitutionally as the corresponding adverb."
          }
        ]
      },
      {
        "id": "C013",
        "union_ids": [
          "U013"
        ],
        "subject_form": "constituent",
        "claim_type": "derived_form",
        "statement": "Constituent can be a component or constituency member noun and a whole-forming adjective.",
        "article_target_ids": [
          "word_formation:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F024",
            "support_summary": "Merriam-Webster distinguishes the component and political constituency-member noun senses."
          },
          {
            "source_fact_id": "F025",
            "support_summary": "Merriam-Webster separately defines the adjective as serving to form or compose a whole."
          }
        ]
      },
      {
        "id": "C014",
        "union_ids": [
          "U014"
        ],
        "subject_form": "reconstitute",
        "claim_type": "derived_form",
        "statement": "Reconstitute means constitute anew and can mean restore by adding liquid.",
        "article_target_ids": [
          "word_formation:005"
        ],
        "source_supports": [
          {
            "source_fact_id": "F026",
            "support_summary": "Merriam-Webster directly defines both constitute anew and restoration by adding water."
          }
        ]
      }
    ]
  },
  "specification_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
  "source_artifact_sha256": "f98ceb46d53d98a15da050b7cf90ea946c481b3b4bfa6a28e16261031574c94b",
  "normalized_input_sha256": "06266927280907552b2607c8d073932130736ff0d77a81eb02a1544a5b41a322"
}
```
