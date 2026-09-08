# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`/root/principal_cycle3_frame`, declared_model=`gpt-5`.

Save one `antonym_axis_adjudication_record_v1` JSON object as `checker_passes.frame-relation.stage2.response.json`. Include the same top-level handoff `reviewer` metadata used by the frame-relation stage-1 response.

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
  "input_body_sha256": "1a52681200f8151d905196cfb05550ddc423af07e1d4fee6da8e752e0a523528",
  "blind_request_sha256": "80a2ee136abfaee140b9490e0e3e6a8d92ccbe9598c8a91b5d86fd356f3f16e5",
  "blind_record_sha256": "0b04735e9f3fc6e9ad0c98f7aa3d945f2e6d722c904e0c3a55b1d5841e7269bf",
  "input_sections": {
    "sense_structure": [
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
        "line": 163,
        "text": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 165,
        "text": "【日本語訳・定義】舞台芸術で主要な役を担う演者、またはオーケストラで一つのセクションを率いる奏者。一般の重要人物ではなく、芸術分野で確立した役割名を指す。  "
      },
      {
        "line": 196,
        "text": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 198,
        "text": "【日本語訳・定義】借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。信託法では、収益と区別される信託財産そのもの、すなわち信託元本・corpusを指す。  "
      },
      {
        "line": 244,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 246,
        "text": "【日本語訳・定義】別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。  "
      },
      {
        "line": 286,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 288,
        "text": "【日本語訳・定義】刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。  "
      },
      {
        "line": 319,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 321,
        "text": "【日本語訳・定義】債務・保証の文脈で、保証人などの二次的責任者と対比され、義務について第一次的に責任を負う人または法人。  "
      }
    ],
    "frames": [
      {
        "line": 40,
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "line": 48,
        "text": "【文法パターン】限定用法で `principal + 〈名詞〉` の形を取り、「主要な～」を表す。  "
      },
      {
        "line": 120,
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "line": 128,
        "text": "【文法パターン】組織上の地位は `a principal at 〈企業・専門組織〉`。教育上の役職は `the principal of 〈限定詞を含む学校・教育機関の名詞句〉`／`a school principal`／`a college principal`。  "
      },
      {
        "line": 163,
        "text": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 171,
        "text": "【文法パターン】舞台芸術の役職は `perform/serve as a principal with 〈舞台芸術団体〉`。オーケストラの役職は `one of 〈オーケストラを表す所有格〉 principals`。  "
      },
      {
        "line": 196,
        "text": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 204,
        "text": "【文法パターン】金融では `principal and interest`／`pay down, protect, or repay + (the) principal`。信託法では `distinguish + principal + from + income`。  "
      },
      {
        "line": 244,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 252,
        "text": "【文法パターン】`a principal-agent relationship`＝本人・代理人関係／`act on behalf of the principal`＝本人を代理して行動する  "
      },
      {
        "line": 286,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 294,
        "text": "【文法パターン】`a principal in 〈犯罪を表す名詞句〉`／`treat 〈人〉 as a principal`  "
      },
      {
        "line": 319,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 327,
        "text": "【文法パターン】`be/remain liable as principal for 〈債務・義務〉`／`the obligation of the principal`／`the principal and the surety`  "
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
        "text": "・`a principal at 〈企業・専門組織〉`  "
      },
      {
        "line": 133,
        "text": "用途: 組織で権限または主導的地位を持つ人を表す。  "
      },
      {
        "line": 134,
        "text": "例: She is a principal at an architecture firm.  "
      },
      {
        "line": 135,
        "text": "訳: 彼女は建築事務所の上級責任者である。  "
      },
      {
        "line": 137,
        "text": "・`the principal of 〈限定詞を含む学校・教育機関の名詞句〉`  "
      },
      {
        "line": 138,
        "text": "用途: どの教育機関の長かを `of` で示す。  "
      },
      {
        "line": 139,
        "text": "例: The principal of the college welcomed the new students.  "
      },
      {
        "line": 140,
        "text": "訳: そのカレッジの学長は新入生を歓迎した。  "
      },
      {
        "line": 142,
        "text": "・`a school principal`  "
      },
      {
        "line": 143,
        "text": "用途: 学校を管理する責任者を職種として表す。  "
      },
      {
        "line": 144,
        "text": "例: The school principal met with parents after the incident.  "
      },
      {
        "line": 145,
        "text": "訳: 校長はその出来事の後、保護者と面会した。  "
      },
      {
        "line": 147,
        "text": "・`a college principal`  "
      },
      {
        "line": 148,
        "text": "用途: カレッジを管理する責任者を職種として表す。  "
      },
      {
        "line": 149,
        "text": "例: A college principal addressed the graduating class.  "
      },
      {
        "line": 150,
        "text": "訳: カレッジの学長が卒業生に向けて話した。  "
      },
      {
        "line": 163,
        "text": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 173,
        "text": "【コロケーション】"
      },
      {
        "line": 175,
        "text": "・`perform as a principal with 〈舞台芸術団体〉`  "
      },
      {
        "line": 176,
        "text": "用途: 舞台芸術団体で主要演者の役職を担うことを表す。  "
      },
      {
        "line": 177,
        "text": "例: She performs as a principal with the ballet company.  "
      },
      {
        "line": 178,
        "text": "訳: 彼女はそのバレエ団で主要演者を務めている。  "
      },
      {
        "line": 180,
        "text": "・`one of the orchestra's principals`  "
      },
      {
        "line": 181,
        "text": "用途: オーケストラで各セクションを率いる奏者を名詞で指す。  "
      },
      {
        "line": 182,
        "text": "例: The concert program lists her as one of the orchestra's principals.  "
      },
      {
        "line": 183,
        "text": "訳: その演奏会プログラムには、彼女がオーケストラの首席奏者の一人として載っている。  "
      },
      {
        "line": 196,
        "text": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 206,
        "text": "【コロケーション】"
      },
      {
        "line": 208,
        "text": "・`principal and interest`  "
      },
      {
        "line": 209,
        "text": "用途: 借入金の元金と、それに対して発生する利息を対で示す。  "
      },
      {
        "line": 210,
        "text": "例: The monthly payment includes both principal and interest.  "
      },
      {
        "line": 211,
        "text": "訳: 毎月の返済額には元金と利息の両方が含まれる。  "
      },
      {
        "line": 213,
        "text": "・`pay down the principal`  "
      },
      {
        "line": 214,
        "text": "用途: 返済によって未返済の元金を減らすことを表す。  "
      },
      {
        "line": 215,
        "text": "例: Extra payments can help you pay down the principal faster.  "
      },
      {
        "line": 216,
        "text": "訳: 追加返済をすれば、元金をより早く減らせる。  "
      },
      {
        "line": 218,
        "text": "・`protect the principal`  "
      },
      {
        "line": 219,
        "text": "用途: 投資で、元本そのものの毀損を避けることを表す。  "
      },
      {
        "line": 220,
        "text": "例: The fund aims to protect the principal while generating modest returns.  "
      },
      {
        "line": 221,
        "text": "訳: そのファンドは、控えめな収益を生みながら元本を保全することを目指している。  "
      },
      {
        "line": 223,
        "text": "・`repay principal`  "
      },
      {
        "line": 224,
        "text": "用途: 利息とは別に借入の元金を返済することを表す。  "
      },
      {
        "line": 225,
        "text": "例: The borrower will begin repaying principal next year.  "
      },
      {
        "line": 226,
        "text": "訳: 借り手は来年、元金の返済を開始する。  "
      },
      {
        "line": 228,
        "text": "・`distinguish principal from income`  "
      },
      {
        "line": 229,
        "text": "用途: 信託財産の元本と、そこから生じる収益を区別する。  "
      },
      {
        "line": 230,
        "text": "例: The trust document distinguishes principal from income.  "
      },
      {
        "line": 231,
        "text": "訳: その信託文書は元本と収益を区別している。  "
      },
      {
        "line": 244,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 254,
        "text": "【コロケーション】"
      },
      {
        "line": 256,
        "text": "・`a principal-agent relationship`  "
      },
      {
        "line": 257,
        "text": "用途: 権限を与える本人と、そのために行動する代理人との関係を表す。  "
      },
      {
        "line": 258,
        "text": "例: The contract created a principal-agent relationship between the owner and the broker.  "
      },
      {
        "line": 259,
        "text": "訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。  "
      },
      {
        "line": 261,
        "text": "・`act on behalf of the principal`  "
      },
      {
        "line": 262,
        "text": "用途: 代理人が本人を代理して行動することを表す。  "
      },
      {
        "line": 263,
        "text": "例: The agent may sign the document on behalf of the principal.  "
      },
      {
        "line": 264,
        "text": "訳: 代理人は本人を代理してその書類に署名できる。  "
      },
      {
        "line": 286,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 296,
        "text": "【コロケーション】"
      },
      {
        "line": 298,
        "text": "・`a principal in a crime`  "
      },
      {
        "line": 299,
        "text": "用途: 犯罪について直接の刑事責任を負う者を指す。  "
      },
      {
        "line": 300,
        "text": "例: The court identified him as a principal in the crime.  "
      },
      {
        "line": 301,
        "text": "訳: 裁判所は彼をその犯罪について `principal` に当たる者と認定した。  "
      },
      {
        "line": 303,
        "text": "・`treat someone as a principal`  "
      },
      {
        "line": 304,
        "text": "用途: 一定の関与者を適用法上 `principal` として扱うことを表す。  "
      },
      {
        "line": 305,
        "text": "例: The statute treats a person who knowingly assists the offense as a principal.  "
      },
      {
        "line": 306,
        "text": "訳: その制定法は、情を知って犯罪を援助する者を `principal` として扱う。  "
      },
      {
        "line": 319,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 329,
        "text": "【コロケーション】"
      },
      {
        "line": 331,
        "text": "・`be liable as principal`  "
      },
      {
        "line": 332,
        "text": "用途: 二次的な保証責任ではなく、主たる当事者として第一次的責任を負うことを示す。  "
      },
      {
        "line": 333,
        "text": "例: Under the agreement, the company remains liable as principal for the debt, while the guarantor is only secondarily liable.  "
      },
      {
        "line": 334,
        "text": "訳: その契約の下で、会社はその債務について主たる当事者として引き続き責任を負い、保証人は二次的にのみ責任を負う。  "
      },
      {
        "line": 336,
        "text": "・`the obligation of the principal`  "
      },
      {
        "line": 337,
        "text": "用途: 主たる当事者が第一次的に負う義務を示す。  "
      },
      {
        "line": 338,
        "text": "例: The guarantee does not replace the obligation of the principal.  "
      },
      {
        "line": 339,
        "text": "訳: その保証は主たる義務者の義務に取って代わるものではない。  "
      },
      {
        "line": 341,
        "text": "・`the principal and the surety`  "
      },
      {
        "line": 342,
        "text": "用途: 第一次的責任を負う当事者と、保証する側を対で示す。  "
      },
      {
        "line": 343,
        "text": "例: The agreement states the duties of the principal and the surety.  "
      },
      {
        "line": 344,
        "text": "訳: その契約は主たる義務者と保証人の義務を定めている。  "
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
        "line": 154,
        "text": "【類義語】"
      },
      {
        "line": 156,
        "text": "・head  "
      },
      {
        "line": 157,
        "text": "定義: 学校・組織などの長。  "
      },
      {
        "line": 158,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 159,
        "text": "違い: `head` は組織の長を広く表す。`principal` は権限・主導的地位を持つ人を表し、特に教育機関で役職名として用いられる。  "
      },
      {
        "line": 160,
        "text": "例: She is the head of a large secondary school.  "
      },
      {
        "line": 161,
        "text": "訳: 彼女は大規模な中等学校の校長である。  "
      },
      {
        "line": 163,
        "text": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "line": 187,
        "text": "【類義語】"
      },
      {
        "line": 189,
        "text": "・section leader  "
      },
      {
        "line": 190,
        "text": "定義: オーケストラで一つのセクションを率いる奏者。  "
      },
      {
        "line": 191,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 192,
        "text": "違い: 役割を説明する一般的な表現で、`principal` は確立した役職名として用いられる。  "
      },
      {
        "line": 193,
        "text": "例: The section leader rehearsed the difficult passage.  "
      },
      {
        "line": 194,
        "text": "訳: セクションの首席奏者は難しい楽節を練習した。  "
      },
      {
        "line": 196,
        "text": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "line": 235,
        "text": "【類義語】"
      },
      {
        "line": 237,
        "text": "・capital  "
      },
      {
        "line": 238,
        "text": "定義: 投資・事業に用いられる資金または資産。  "
      },
      {
        "line": 239,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 240,
        "text": "違い: `capital` は事業資金・生産資産まで広く表す。`principal` は特定の貸付・借入・投資で利息や収益の基礎となる元の額を指す。  "
      },
      {
        "line": 241,
        "text": "例: The company raised additional capital from investors.  "
      },
      {
        "line": 242,
        "text": "訳: その会社は投資家から追加資金を調達した。  "
      },
      {
        "line": 244,
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "line": 268,
        "text": "【類義語】"
      },
      {
        "line": 270,
        "text": "・mandator  "
      },
      {
        "line": 271,
        "text": "定義: 他人に委任・代理の権限を与える者。  "
      },
      {
        "line": 272,
        "text": "頻度: 〈2/10〉  "
      },
      {
        "line": 273,
        "text": "違い: 特定の法体系や専門文脈で使われる低頻度語である。  "
      },
      {
        "line": 274,
        "text": "例: The mandator may revoke the mandate subject to the agreement.  "
      },
      {
        "line": 275,
        "text": "訳: 委任者は、契約の定めに従い、委任を撤回できる。  "
      },
      {
        "line": 277,
        "text": "【反意語】"
      },
      {
        "line": 279,
        "text": "・agent  "
      },
      {
        "line": 280,
        "text": "定義: 他者から権限を与えられ、その者のために行動する人または法人。  "
      },
      {
        "line": 281,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 282,
        "text": "違い: 同じ代理関係の役割軸で、`principal` が権限を与える側、`agent` が与えられた権限で行動する側である。  "
      },
      {
        "line": 283,
        "text": "例: The agent negotiated the sale for the owner.  "
      },
      {
        "line": 284,
        "text": "訳: 代理人は所有者のために売却交渉を行った。  "
      },
      {
        "line": 286,
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "line": 310,
        "text": "【類義語】"
      },
      {
        "line": 312,
        "text": "・perpetrator  "
      },
      {
        "line": 313,
        "text": "定義: 犯罪・不正行為を実際に行った者。  "
      },
      {
        "line": 314,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 315,
        "text": "違い: `perpetrator` は実行者に焦点を置く一般的な法律・報道語。`principal` は適用される法的分類によって、実行者以外の一定の関与者を含む場合がある。  "
      },
      {
        "line": 316,
        "text": "例: Police are still trying to identify the perpetrator.  "
      },
      {
        "line": 317,
        "text": "訳: 警察は今も犯人の特定を進めている。  "
      },
      {
        "line": 319,
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "line": 348,
        "text": "【類義語】"
      },
      {
        "line": 350,
        "text": "・obligor  "
      },
      {
        "line": 351,
        "text": "定義: 契約や法律上の義務を負う者。  "
      },
      {
        "line": 352,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 353,
        "text": "違い: `obligor` は義務を負う者を広く表す。`principal` は保証人などと対比して、その義務について第一次的に責任を負う側を示す。  "
      },
      {
        "line": 354,
        "text": "例: The obligor must perform the duty by the stated date.  "
      },
      {
        "line": 355,
        "text": "訳: 義務者は定められた日までに義務を履行しなければならない。  "
      },
      {
        "line": 357,
        "text": "・debtor  "
      },
      {
        "line": 358,
        "text": "定義: 金銭その他の債務を負う者。  "
      },
      {
        "line": 359,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 360,
        "text": "違い: `debtor` は債務者一般を指す。`principal` は保証関係で第一次的責任を負う当事者という役割を強調する。  "
      },
      {
        "line": 361,
        "text": "例: The debtor made the payment on time.  "
      },
      {
        "line": 362,
        "text": "訳: 債務者は期限どおりに支払った。  "
      },
      {
        "line": 364,
        "text": "【反意語】"
      },
      {
        "line": 366,
        "text": "・surety  "
      },
      {
        "line": 367,
        "text": "定義: 主たる債務者が履行しない場合に責任を負う保証人。  "
      },
      {
        "line": 368,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 369,
        "text": "違い: 責任順位の軸で、`principal` が第一次的に責任を負うのに対し、`surety` は他人の義務を担保する側に立つ。  "
      },
      {
        "line": 370,
        "text": "例: The surety paid after the borrower defaulted.  "
      },
      {
        "line": 371,
        "text": "訳: 借り手が債務不履行となった後、保証人が支払った。  "
      }
    ],
    "antonym_axis_items": [
      {
        "item_id": "ant-c450e878c609",
        "stage1_axis": {
          "item_id": "ant-c450e878c609",
          "axis": "重要度",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 106,
          "line_end": 106,
          "exact_quote": "・secondary  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 109,
          "line_end": 109,
          "exact_quote": "違い: 重要度・順位の軸で `principal` と方向が反対になり、主要なものに対する従属的・補助的なものを表す。  "
        }
      },
      {
        "item_id": "ant-65d902381b24",
        "stage1_axis": {
          "item_id": "ant-65d902381b24",
          "axis": "重要度",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 113,
          "line_end": 113,
          "exact_quote": "・minor  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 116,
          "line_end": 116,
          "exact_quote": "違い: `principal` との程度軸上の対立で、最重要・主要ではない小さな要素を表す。  "
        }
      },
      {
        "item_id": "ant-ab226152f491",
        "stage1_axis": {
          "item_id": "ant-ab226152f491",
          "axis": "授権方向",
          "relation_type": "方向",
          "reason": ""
        },
        "sense_id": "sense:005",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 279,
          "line_end": 279,
          "exact_quote": "・agent  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 282,
          "line_end": 282,
          "exact_quote": "違い: 同じ代理関係の役割軸で、`principal` が権限を与える側、`agent` が与えられた権限で行動する側である。  "
        }
      },
      {
        "item_id": "ant-633fad4cce44",
        "stage1_axis": {
          "item_id": "ant-633fad4cce44",
          "axis": "責任順位",
          "relation_type": "補完",
          "reason": ""
        },
        "sense_id": "sense:007",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 366,
          "line_end": 366,
          "exact_quote": "・surety  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 369,
          "line_end": 369,
          "exact_quote": "違い: 責任順位の軸で、`principal` が第一次的に責任を負うのに対し、`surety` は他人の義務を担保する側に立つ。  "
        }
      }
    ],
    "antonym_axis_senses": [
      {
        "sense_id": "sense:001",
        "full_sense": [
          {
            "line": 40,
            "text": "1. 【形容詞】主要な、最も重要な、第一の"
          },
          {
            "line": 42,
            "text": "【日本語訳・定義】複数の原因、目的、人物、場所、要素などの中で、重要度・影響力・順位が最も高い、または特に高いものを示す。単に時間的に最初という意味ではなく、重要性や中心性の評価を表す。  "
          },
          {
            "line": 44,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 46,
            "text": "【レジスター/領域】標準～やや形式的。報道、ビジネス、学術、行政で広く使う。日常会話では `main` がより普通なことが多い。  "
          },
          {
            "line": 48,
            "text": "【文法パターン】限定用法で `principal + 〈名詞〉` の形を取り、「主要な～」を表す。  "
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
            "line": 72,
            "text": "【語法・注意】`principal` と `principle` は綴りも意味も異なる。`principal` には形容詞で「最も重要な」を表す用法があり、別に人や金額などを指す名詞用法もある。一方、`principle` は「原理・原則」を表す名詞である。したがって「基本原則」は `basic principle` であり、`basic principal` ではない。  "
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
          }
        ]
      },
      {
        "sense_id": "sense:005",
        "full_sense": [
          {
            "line": 244,
            "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
          },
          {
            "line": 246,
            "text": "【日本語訳・定義】別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。  "
          },
          {
            "line": 248,
            "text": "【頻度】〈5/10〉  "
          },
          {
            "line": 250,
            "text": "【レジスター/領域】法律、保険、不動産、商取引。日常語として人を「依頼主」と呼ぶだけなら `client` が自然な場合も多い。  "
          },
          {
            "line": 252,
            "text": "【文法パターン】`a principal-agent relationship`＝本人・代理人関係／`act on behalf of the principal`＝本人を代理して行動する  "
          },
          {
            "line": 254,
            "text": "【コロケーション】"
          },
          {
            "line": 256,
            "text": "・`a principal-agent relationship`  "
          },
          {
            "line": 257,
            "text": "用途: 権限を与える本人と、そのために行動する代理人との関係を表す。  "
          },
          {
            "line": 258,
            "text": "例: The contract created a principal-agent relationship between the owner and the broker.  "
          },
          {
            "line": 259,
            "text": "訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。  "
          },
          {
            "line": 261,
            "text": "・`act on behalf of the principal`  "
          },
          {
            "line": 262,
            "text": "用途: 代理人が本人を代理して行動することを表す。  "
          },
          {
            "line": 263,
            "text": "例: The agent may sign the document on behalf of the principal.  "
          },
          {
            "line": 264,
            "text": "訳: 代理人は本人を代理してその書類に署名できる。  "
          },
          {
            "line": 266,
            "text": "【語法・注意】法律用語の `principal` は、`agent` に権限を与える側を表す関係上の役割名である。`principal` が権限の源となり、`agent` は本人のためにその権限の範囲で行動する。  "
          },
          {
            "line": 268,
            "text": "【類義語】"
          },
          {
            "line": 270,
            "text": "・mandator  "
          },
          {
            "line": 271,
            "text": "定義: 他人に委任・代理の権限を与える者。  "
          },
          {
            "line": 272,
            "text": "頻度: 〈2/10〉  "
          },
          {
            "line": 273,
            "text": "違い: 特定の法体系や専門文脈で使われる低頻度語である。  "
          },
          {
            "line": 274,
            "text": "例: The mandator may revoke the mandate subject to the agreement.  "
          },
          {
            "line": 275,
            "text": "訳: 委任者は、契約の定めに従い、委任を撤回できる。  "
          },
          {
            "line": 277,
            "text": "【反意語】"
          },
          {
            "line": 279,
            "text": "・agent  "
          },
          {
            "line": 280,
            "text": "定義: 他者から権限を与えられ、その者のために行動する人または法人。  "
          },
          {
            "line": 281,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 282,
            "text": "違い: 同じ代理関係の役割軸で、`principal` が権限を与える側、`agent` が与えられた権限で行動する側である。  "
          },
          {
            "line": 283,
            "text": "例: The agent negotiated the sale for the owner.  "
          },
          {
            "line": 284,
            "text": "訳: 代理人は所有者のために売却交渉を行った。  "
          }
        ]
      },
      {
        "sense_id": "sense:007",
        "full_sense": [
          {
            "line": 319,
            "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
          },
          {
            "line": 321,
            "text": "【日本語訳・定義】債務・保証の文脈で、保証人などの二次的責任者と対比され、義務について第一次的に責任を負う人または法人。  "
          },
          {
            "line": 323,
            "text": "【頻度】〈2/10〉  "
          },
          {
            "line": 325,
            "text": "【レジスター/領域】債務法・保証法の専門語。  "
          },
          {
            "line": 327,
            "text": "【文法パターン】`be/remain liable as principal for 〈債務・義務〉`／`the obligation of the principal`／`the principal and the surety`  "
          },
          {
            "line": 329,
            "text": "【コロケーション】"
          },
          {
            "line": 331,
            "text": "・`be liable as principal`  "
          },
          {
            "line": 332,
            "text": "用途: 二次的な保証責任ではなく、主たる当事者として第一次的責任を負うことを示す。  "
          },
          {
            "line": 333,
            "text": "例: Under the agreement, the company remains liable as principal for the debt, while the guarantor is only secondarily liable.  "
          },
          {
            "line": 334,
            "text": "訳: その契約の下で、会社はその債務について主たる当事者として引き続き責任を負い、保証人は二次的にのみ責任を負う。  "
          },
          {
            "line": 336,
            "text": "・`the obligation of the principal`  "
          },
          {
            "line": 337,
            "text": "用途: 主たる当事者が第一次的に負う義務を示す。  "
          },
          {
            "line": 338,
            "text": "例: The guarantee does not replace the obligation of the principal.  "
          },
          {
            "line": 339,
            "text": "訳: その保証は主たる義務者の義務に取って代わるものではない。  "
          },
          {
            "line": 341,
            "text": "・`the principal and the surety`  "
          },
          {
            "line": 342,
            "text": "用途: 第一次的責任を負う当事者と、保証する側を対で示す。  "
          },
          {
            "line": 343,
            "text": "例: The agreement states the duties of the principal and the surety.  "
          },
          {
            "line": 344,
            "text": "訳: その契約は主たる義務者と保証人の義務を定めている。  "
          },
          {
            "line": 346,
            "text": "【語法・注意】この語義では、`principal` は `be liable as principal` のように人・法人を指す名詞である。金額を指す語義4の「元金」とは区別する。  "
          },
          {
            "line": 348,
            "text": "【類義語】"
          },
          {
            "line": 350,
            "text": "・obligor  "
          },
          {
            "line": 351,
            "text": "定義: 契約や法律上の義務を負う者。  "
          },
          {
            "line": 352,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 353,
            "text": "違い: `obligor` は義務を負う者を広く表す。`principal` は保証人などと対比して、その義務について第一次的に責任を負う側を示す。  "
          },
          {
            "line": 354,
            "text": "例: The obligor must perform the duty by the stated date.  "
          },
          {
            "line": 355,
            "text": "訳: 義務者は定められた日までに義務を履行しなければならない。  "
          },
          {
            "line": 357,
            "text": "・debtor  "
          },
          {
            "line": 358,
            "text": "定義: 金銭その他の債務を負う者。  "
          },
          {
            "line": 359,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 360,
            "text": "違い: `debtor` は債務者一般を指す。`principal` は保証関係で第一次的責任を負う当事者という役割を強調する。  "
          },
          {
            "line": 361,
            "text": "例: The debtor made the payment on time.  "
          },
          {
            "line": 362,
            "text": "訳: 債務者は期限どおりに支払った。  "
          },
          {
            "line": 364,
            "text": "【反意語】"
          },
          {
            "line": 366,
            "text": "・surety  "
          },
          {
            "line": 367,
            "text": "定義: 主たる債務者が履行しない場合に責任を負う保証人。  "
          },
          {
            "line": 368,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 369,
            "text": "違い: 責任順位の軸で、`principal` が第一次的に責任を負うのに対し、`surety` は他人の義務を担保する側に立つ。  "
          },
          {
            "line": 370,
            "text": "例: The surety paid after the borrower defaulted.  "
          },
          {
            "line": 371,
            "text": "訳: 借り手が債務不履行となった後、保証人が支払った。  "
          }
        ]
      }
    ]
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
