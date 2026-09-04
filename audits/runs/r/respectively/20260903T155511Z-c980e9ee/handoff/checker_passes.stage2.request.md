# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`01a06a93-187d-78e2-a368-2ce1d68aa084`, declared_model=`gpt-5`.

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
  "input_body_sha256": "58022cced2f43061792f990efbc72f49cd43ba2f108c4a0bb038fa325c7f4890",
  "blind_request_sha256": "3a3da09b53e760a7ff71130df75d68743343bcf656f21359da673b145b34a84e",
  "blind_record_sha256": "d87fa55de7ba8a4e4b2b213096233d7db3cfcdd8606daac5859153d9cf8626c3",
  "input_sections": {
    "sense_structure": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 33,
        "text": "【日本語訳・定義】2つ以上の人・物・項目のリストと、それらに対応する同数の結果、性質、数値、行為などを、同じ文または前後の明確な文脈で示し、1番目同士、2番目同士というように提示された順番で1対1に対応させることを表す。日本語の「それぞれ」に相当するが、単に別々であるだけでなく、対応する項目の順序を指定する点が重要である。  "
      }
    ],
    "frames": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 39,
        "text": "【文法パターン】〈対象1〉 and 〈対象2〉 + be・動詞 + 〈対応項目1〉 and 〈対応項目2〉, respectively＝〈対象1〉には〈対応項目1〉、〈対象2〉には〈対応項目2〉／〈値1〉 and 〈値2〉 apply to 〈対象1〉 and 〈対象2〉, respectively＝〈値1〉と〈値2〉が〈対象1〉と〈対象2〉にそれぞれ当てはまる／〈対象1〉 and 〈対象2〉 respectively + 〈動詞句1〉 and 〈動詞句2〉＝〈対象1〉は〈動詞句1〉、〈対象2〉は〈動詞句2〉をそれぞれ行う（文が長くなりやすいため、通常は文末配置が明快）  "
      }
    ],
    "collocations_examples": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 41,
        "text": "【コロケーション】"
      },
      {
        "line": 43,
        "text": "・〈対象1〉 and 〈対象2〉 were 〈値1〉 and 〈値2〉, respectively  "
      },
      {
        "line": 44,
        "text": "用途: 人・物・項目の順番と、年齢、順位、数値などの順番を対応させる。  "
      },
      {
        "line": 45,
        "text": "例: Mia and Leo were 18 and 21 years old, respectively.  "
      },
      {
        "line": 46,
        "text": "訳: ミアとレオは、それぞれ18歳と21歳だった。  "
      },
      {
        "line": 48,
        "text": "・〈対象1〉 and 〈対象2〉 had 〈値1〉 and 〈値2〉, respectively  "
      },
      {
        "line": 49,
        "text": "用途: 二つの対象について、売上、割合、得点などの数値を同じ順番で示す。  "
      },
      {
        "line": 50,
        "text": "例: The two stores had sales of $2 million and $1.4 million, respectively.  "
      },
      {
        "line": 51,
        "text": "訳: その2店舗の売上は、それぞれ200万ドルと140万ドルだった。  "
      },
      {
        "line": 53,
        "text": "・〈名詞1〉 and 〈名詞2〉 correspond to 〈項目1〉 and 〈項目2〉, respectively  "
      },
      {
        "line": 54,
        "text": "用途: 名前、記号、分類などの対応関係を明示する。  "
      },
      {
        "line": 55,
        "text": "例: In the diagram, the solid and dashed lines correspond to observed and predicted values, respectively.  "
      },
      {
        "line": 56,
        "text": "訳: 図では、実線と破線がそれぞれ観測値と予測値に対応している。  "
      },
      {
        "line": 58,
        "text": "・〈値1〉 and 〈値2〉 apply to 〈対象1〉 and 〈対象2〉, respectively  "
      },
      {
        "line": 59,
        "text": "用途: 規則、条件、料金、基準などが複数の対象に順番どおり適用されることを示す。  "
      },
      {
        "line": 60,
        "text": "例: The lower and higher rates apply to part-time and full-time employees, respectively.  "
      },
      {
        "line": 61,
        "text": "訳: 低い料率と高い料率は、それぞれパートタイム従業員とフルタイム従業員に適用される。  "
      },
      {
        "line": 63,
        "text": "・〈対象1〉 and 〈対象2〉 finished 〈順位1〉 and 〈順位2〉, respectively  "
      },
      {
        "line": 64,
        "text": "用途: 競技、試験、選挙などで、複数の対象の順位を列挙順に対応させる。  "
      },
      {
        "line": 65,
        "text": "例: Brazil and Canada finished first and second, respectively, in the final ranking.  "
      },
      {
        "line": 66,
        "text": "訳: 最終順位では、ブラジルとカナダがそれぞれ1位と2位になった。  "
      },
      {
        "line": 68,
        "text": "・〈対象1〉 and 〈対象2〉 respectively represent 〈意味1〉 and 〈意味2〉  "
      },
      {
        "line": 69,
        "text": "用途: 記号、変数、色などが表すものを、二つのリストの順に対応させる。文中配置だが、対応関係が短く明快な場合に使える。  "
      },
      {
        "line": 70,
        "text": "例: In this equation, x and y respectively represent distance and time.  "
      },
      {
        "line": 71,
        "text": "訳: この式では、xとyがそれぞれ距離と時間を表す。  "
      },
      {
        "line": 73,
        "text": "・〈主語1〉 and 〈主語2〉 + 〈動詞句1〉 and 〈動詞句2〉, respectively  "
      },
      {
        "line": 74,
        "text": "用途: 二つの主語が異なる行為や役割を担うことを、行為の提示順に対応させる。主語と動詞句の数をそろえる。  "
      },
      {
        "line": 75,
        "text": "例: The editor and the designer checked the text and prepared the layout, respectively.  "
      },
      {
        "line": 76,
        "text": "訳: 編集者は本文を確認し、デザイナーはレイアウトを準備した。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 84,
        "text": "【類義語】"
      },
      {
        "line": 86,
        "text": "・in the same order  "
      },
      {
        "line": 87,
        "text": "定義: 先に示されたものと同じ順番で。  "
      },
      {
        "line": 88,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 89,
        "text": "違い: 順序対応を直接説明する説明的な言い換えだが、常に respectively と置換できるわけではない。文中で副詞として使える respectively より長いが、対応関係を初めて説明するときに分かりやすい。  "
      },
      {
        "line": 90,
        "text": "例: The figures refer to the three regions in the same order.  "
      },
      {
        "line": 91,
        "text": "訳: その数値は、三つの地域に先に示したのと同じ順番で対応している。  "
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
