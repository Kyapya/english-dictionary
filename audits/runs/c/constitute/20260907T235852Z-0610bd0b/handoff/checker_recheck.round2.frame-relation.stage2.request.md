# Independent checker recheck handoff — round 2, frame-relation stage 2

Stage: `checker_recheck/round2/frame-relation/stage2`

This request must be executed by the same subagent that produced the sealed round-2 frame-relation stage-1 record.

Required reviewer identity: `constitute-round2-frame-relation-1` with declared_model `gpt-5`, mode `handoff`, ingested_by `human`.

Save exactly one JSON response as `checker_recheck.round2.frame-relation.stage2.response.json`. Do not change the stage-1 axes.

## Prompt

# check_pass_frame_relation_v7

## 目的

完全な統語フレームと項の意味役割、および類義語・反意語の語彙関係を検査する。

## 担当タクソノミー分類

- `argument_slot_role_mismatch`
- `lexical_relation_mislabel`

## 検査ルール

- 各語義の宣言品詞・自他・構文種別と、定義、全文法パターン、全コロケーション、全例文を一致させる。
- V、V+O、V+O+O、V+C、V+O+C、補文、前置詞、小辞、受動、分詞形容詞を、実在し学習価値がある完全フレーム単位で確認する。
- 必須要素と任意要素、主語・目的語・補語の典型的意味種類、行為者・経験者・対象・結果を明示し、patternのslotと例文内の実現を一対一で照合する。
- 自他、人目的語／物目的語、能動／受動／分詞形容詞、通常目的語／再帰代名詞、小辞位置、代名詞位置、支配前置詞の差を最小対立で確認する。
- `V + oneself`、`V + oneself + particle/preposition`、対応する受動・形容詞を省略関係として誤説明しない。
- 一つの語義内の全主要フレームへ定義が適用できなければ、不適切な統合としてsense-structure passへunrouted observationを返す。
- `【文法パターン】` の主要構文とコロケーションを相互に対応させる。プレースホルダの各候補を代入したとき冠詞、所有格、前置詞、補語、節構造、語形を補わず成立するか確認する。
- 類義語は中心義が十分に重なる語または定着句に限り、見出し語自身・単なる関連語を含めない。強度、対象、結果、意図性、評価、フォーマル度、地域差等の具体軸で差を示す。
- 反意語は同じ意味軸上の補完、程度、方向、評価、状態の対立に限る。解決策、結果、原因、関連概念を反意語としない。明確な反意語がなければ欄省略を認める。
- 類義語・反意語の頻度と定義は、そのentryが置かれた直前の語義に限定して判定する。

## 入力として受け取るセクション

- `sense_structure`
- `frames`
- `collocations_examples`
- `lexical_relations`

## findingの出力スキーマ

```json
{
  "taxonomy_id": "argument_slot_role_mismatch | lexical_relation_mislabel",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "slot-roleまたは語彙関係の不一致",
  "evidence_link_ids": [],
  "suggested_direction": "完全フレーム化、移動、削除、対立軸修正の方向"
}
```

## 4. 反意語対立軸の2段階ブラインド検査

各語義ブロックの `【反意語】` 欄にある全アイテムを対象とする。同じ反意語が複数語義に現れる場合も語義ごとに独立して判定する。類義語・反意語欄内の例文は対象外であり、反意語欄が存在しないことは正常な完成状態なのでfindingを出さない。

### 4.1 段階1: ブラインド軸命名

段階1では `antonym_axis_blind_request_v1` だけを受け取る。各アイテムに開示されるのは、見出し語、当該語義の `【日本語訳・定義】` 全文、反意語の語、反意語の `定義:` 行だけである。`違い:` 行、`頻度:` 行、`例:` 行、`訳:` 行、類義語欄全体、コアイメージ、他語義の情報を参照してはならない。アイテムはrun別の不透明IDを持ち、shuffleされた順で提示される。

各アイテムについて次を記録する。

1. 二語が対立する意味軸を名詞一語で命名する。複合語は可とするが、「〜の度合い」などの説明句は不可とする。
2. 対立型を `補完 | 程度 | 方向 | 評価 | 状態` のいずれか一つに分類する。
3. 軸を命名できない場合は軸を `unnamable` とし、対立型を空値にして、理由を一文で述べる。

回答は `antonym_axis_blind_record_v1` として確定・保存する。調整役は、この記録の保存、request hash照合、全不透明IDの被覆を確認するまで段階2入力を作成・開示してはならない。

段階1では次のJSON形を返す。`input_body_sha256`、`blind_request_sha256`、`recorded_at`、`reviewer` は調整役が実際のrequestと保存時刻から封印するメタデータであり、判定者は `axes` の内容を作成する。

```json
{
  "schema_version": "antonym_axis_blind_record_v1",
  "pass_id": "frame-relation",
  "input_body_sha256": "stage 1 requestの値",
  "blind_request_sha256": "stage 1 request全体のsha256",
  "recorded_at": "aware ISO-8601 timestamp",
  "reviewer": {},
  "axes": [
    {
      "item_id": "ant-opaque-id",
      "axis": "名詞一語 | unnamable",
      "relation_type": "補完 | 程度 | 方向 | 評価 | 状態 | null",
      "reason": "unnamableの場合は必須の一文理由"
    }
  ]
}
```

### 4.2 段階2: 照合・裁定

段階1記録の封印後に限り、当該語義の全文（`違い:` 行と類義語欄を含む）を開示する。段階1で命名した軸と型を変更せず、次の基準で裁定する。担当taxonomyはすべて既存の `lexical_relation_mislabel` とする。

- **F1（unnamable）**: 段階1が `unnamable` なら `blocking`。
- **F2（軸の帰属不正）**: 命名された軸が当該語義の `【日本語訳・定義】` から導出できず、同語義の類義語欄の語との対立としてのみ成立する軸転移なら `blocking`。
- **F3（型の不正）**: 段階1の分類が5型のいずれにも実質的に収まらず、解決策・結果・原因・関連概念の対立なら `blocking`。
- **F4（違い行の自己否定）**: `違い:` 行が対立の不成立・限定を自認する記述（「〜まで意味しない」「〜とは限らない」「対立しない」等の趣旨）を含むなら `minor` 以上。段階1がpassでもF4単独でfindingを出す。

段階1で軸を命名でき、F2〜F4のいずれにも該当しなければ問題なしとする。各flagの `suggested_direction` は `削除 | 語法・注意への対照表現としての移動 | 対立軸修正` のいずれか一方向とする。

段階2の回答は `antonym_axis_adjudication_record_v1` として、各不透明IDの `flags`、根拠、修正方向、F4のseverity、既存v6ルールによるframe finding、必要な `unrouted_observations` を返す。F1は段階1記録から機械照合され、段階2で解除してはならない。

段階2では次のJSON形を返す。hash群と `reviewer` は調整役が実際のartifactから封印するメタデータである。問題なしのアイテムも `flags: []` として必ず一度だけ記録する。

```json
{
  "schema_version": "antonym_axis_adjudication_record_v1",
  "pass_id": "frame-relation",
  "input_body_sha256": "stage 2 requestの値",
  "stage2_request_sha256": "stage 2 request全体のsha256",
  "blind_record_sha256": "保存済みstage 1 record全体のsha256",
  "reviewer": {},
  "adjudications": [
    {
      "item_id": "ant-opaque-id",
      "flags": ["F1 | F2 | F3 | F4"],
      "rationale": "裁定理由",
      "suggested_direction": "削除 | 語法・注意への対照表現としての移動 | 対立軸修正",
      "f4_severity": "blocking | minor | null"
    }
  ],
  "frame_findings": [],
  "unrouted_observations": []
}
```

### 4.3 出力と時系列封印

最終frame-relation pass出力にはfindingと併せて、段階1の `antonym_axis_blind_record` を改変せず埋め込み、段階2の `aligned_at` と `unrouted_observations` を記録する。`aligned_at` は段階1の `recorded_at` より後でなければならない。不透明ID、shuffle、alignment key、stage 1 request hash、保存済みrecord hashの照合はexample-attributionの既存機構と同じ方式を使い、`audits/BLIND_SEAL_CHRONOLOGY_REQUIRED` に従って段階1保存前の段階2開示をprocess欠陥として失敗させる。所要時間の長短は合否に使わない。

## Input packet

```json
{
  "schema_version": "antonym_axis_adjudication_request_v1",
  "pass_id": "frame-relation",
  "taxonomy_ids": [
    "argument_slot_role_mismatch",
    "lexical_relation_mislabel"
  ],
  "specification": "prompts/check_pass_frame_relation_v7.md",
  "input_body_sha256": "438440ad672a2ee1a035ade560c75d44d526b4a396bcd3f2706cda02c2ae9d93",
  "blind_request_sha256": "762dfea1e619a046009c854e8b4e2ba59711a1b13fc90a52f196c4ff0f032317",
  "blind_record_sha256": "dcc0a88315b5152bbb72c240ba143d50e456b28d3ac230b110ffa0a56886c8a4",
  "input_sections": {
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
        "text": "【文法パターン】`constitute 〈committee/body/court/government〉`＝委員会・機関・裁判所・政府を正式に設ける／`〈body〉 be constituted under/by 〈law/authority〉`＝機関が法律・権限に基づいて設立される／`a properly/legally/duly constituted 〈body/authority〉`＝適切・合法・正式に成立した機関・権限主体  "
      },
      {
        "line": 253,
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "line": 261,
        "text": "【文法パターン】`constitute someone 〈office/role〉`＝人を役職・役割に任命する／`someone be constituted 〈office/role〉`＝人が役職に任命される／`a legally constituted 〈officer/official〉`＝法に基づいて正式に任命された役職者  "
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
        "text": "訳: その憲章は、会計役を協会の正式に任命された役職者として定めている。  "
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
        "text": "訳: これらの小川が合流して本流を形作る。  "
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
        "text": "訳: その建物は、保護対象の歴史的建造物に該当する。  "
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
    ],
    "antonym_axis_items": [],
    "antonym_axis_senses": []
  },
  "blind_protocol": {
    "stage": 2,
    "stage1_record_saved": true,
    "chronology_marker": "audits/BLIND_SEAL_CHRONOLOGY_REQUIRED",
    "required_output_schema": "antonym_axis_adjudication_record_v1"
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
