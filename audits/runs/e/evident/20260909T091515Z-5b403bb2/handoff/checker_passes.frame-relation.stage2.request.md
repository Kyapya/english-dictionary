# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`evident-checker-frame-relation-20260909`, declared_model=`gpt-6-astra-wm`.

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
  "input_body_sha256": "7daa0d416ecef06000548e2f59c08bd4394750574e23f19e24855a4a6339257a",
  "blind_request_sha256": "b73825d6a66022d6fa67a1530a3a3f3603ae8158d505f5cc1a45279a64a9c4f8",
  "blind_record_sha256": "10eb70dbef73fe372f8a3204b68af59d1fd87bf2c59436f304d426ca64beb33e",
  "input_sections": {
    "sense_structure": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 32,
        "text": "【日本語訳・定義】見える特徴、行動、データ、状況などから、ある事実・状態・感情・評価を容易に認識または理解できることを表す。観察した人にとって明白だという意味であり、語そのものが論理的な証明や絶対的な確実性まで保証するわけではない。  "
      }
    ],
    "frames": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 38,
        "text": "【文法パターン】something + be・seem・become・remain evident＝事実・状態などが明らかである／it + be・become + evident + that 〈節〉＝～であることが明らかだ／something + be evident to someone＝〈人〉にとって明らかだ／it + be evident to someone + that 〈節〉＝〈人〉には～が明らかだ／it + be evident from 〈data・evidence・behavior〉 + that 〈節〉＝〈データ・証拠・行動〉から～が明らかだ／something + be evident in 〈expression・results・pattern〉＝感情・特徴などが〈表情・結果・パターン〉に表れている／make something・make it evident + that 〈節〉＝何かを明白にする・～であることを明らかにする／evident + 〈change・difference・sign・need〉＝明らかな〈変化・違い・兆候・必要性〉。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 40,
        "text": "【コロケーション】"
      },
      {
        "line": 42,
        "text": "・it is evident that 〈節〉  "
      },
      {
        "line": 43,
        "text": "用途: 状況や観察結果から、ある判断が明らかだと述べる基本構文。  "
      },
      {
        "line": 44,
        "text": "例: It is evident that the current plan cannot meet the deadline.  "
      },
      {
        "line": 45,
        "text": "訳: 現在の計画では期限に間に合わないことが明らかだ。  "
      },
      {
        "line": 47,
        "text": "・be evident to someone  "
      },
      {
        "line": 48,
        "text": "用途: 何が誰にとって明らかなのかを示す。  "
      },
      {
        "line": 49,
        "text": "例: The benefits of the new system were immediately evident to the staff.  "
      },
      {
        "line": 50,
        "text": "訳: 新しいシステムの利点は職員にはすぐに明らかになった。  "
      },
      {
        "line": 52,
        "text": "・be evident from 〈data・evidence・results〉 that 〈節〉  "
      },
      {
        "line": 53,
        "text": "用途: 明白だと判断する根拠や情報源を示す。  "
      },
      {
        "line": 54,
        "text": "例: It was evident from the audit results that several invoices had been duplicated.  "
      },
      {
        "line": 55,
        "text": "訳: 監査結果から、複数の請求書が重複していたことは明らかだった。  "
      },
      {
        "line": 57,
        "text": "・be evident in 〈expression・behavior・pattern〉  "
      },
      {
        "line": 58,
        "text": "用途: 感情や特徴が表情・行動・結果などに現れていることを表す。  "
      },
      {
        "line": 59,
        "text": "例: Her disappointment was evident in the way she avoided eye contact.  "
      },
      {
        "line": 60,
        "text": "訳: 彼女が目を合わせようとしなかったことに、失望がはっきり表れていた。  "
      },
      {
        "line": 62,
        "text": "・become evident  "
      },
      {
        "line": 63,
        "text": "用途: 時間の経過や追加情報によって、それまで不明だったことが明らかになることを表す。  "
      },
      {
        "line": 64,
        "text": "例: The scale of the damage became evident after the smoke cleared.  "
      },
      {
        "line": 65,
        "text": "訳: 煙が晴れた後、被害の規模が明らかになった。  "
      },
      {
        "line": 67,
        "text": "・make it evident that 〈節〉  "
      },
      {
        "line": 68,
        "text": "用途: 数値、言動、結果などによって、ある判断を明白にする。  "
      },
      {
        "line": 69,
        "text": "例: The revised figures made it evident that the original estimate was too optimistic.  "
      },
      {
        "line": 70,
        "text": "訳: 修正後の数値によって、当初の見積もりが楽観的すぎたことが明らかになった。  "
      },
      {
        "line": 72,
        "text": "・evident signs of 〈change・stress・recovery〉  "
      },
      {
        "line": 73,
        "text": "用途: 変化、ストレス、回復などが起きていると分かる兆候を表す。  "
      },
      {
        "line": 74,
        "text": "例: The patient showed evident signs of recovery after the treatment.  "
      },
      {
        "line": 75,
        "text": "訳: その患者には治療後、回復の明らかな兆候が見られた。  "
      },
      {
        "line": 77,
        "text": "・with evident 〈relief・pleasure・concern〉  "
      },
      {
        "line": 78,
        "text": "用途: 表情や声などに感情が明確に現れている様子を表す。  "
      },
      {
        "line": 79,
        "text": "例: She spoke with evident relief after the results were announced.  "
      },
      {
        "line": 80,
        "text": "訳: 結果が発表された後、彼女はほっとした様子をはっきり見せて話した。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 88,
        "text": "【類義語】"
      },
      {
        "line": 90,
        "text": "・obvious  "
      },
      {
        "line": 91,
        "text": "定義: 見たり考えたりすれば容易に分かる、明白な。  "
      },
      {
        "line": 92,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 93,
        "text": "違い: obvious は日常的で、証拠がなくても直観的に分かることに使える。evident は兆候や状況から判断できることをやや形式的に述べる。  "
      },
      {
        "line": 94,
        "text": "例: It was obvious from his expression that he was disappointed.  "
      },
      {
        "line": 95,
        "text": "訳: 彼の表情から、彼が失望しているのは明らかだった。  "
      },
      {
        "line": 97,
        "text": "・clear  "
      },
      {
        "line": 98,
        "text": "定義: 意味・事実・状況などが疑いなく理解できる、明確な。  "
      },
      {
        "line": 99,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 100,
        "text": "違い: clear は説明や指示を「分かりやすくする」意図にも使え、対象範囲が広い。evident は観察可能な兆候から明らかになることに焦点を置きやすい。  "
      },
      {
        "line": 101,
        "text": "例: The instructions were clear to everyone on the team.  "
      },
      {
        "line": 102,
        "text": "訳: その指示はチームの全員にとって明確だった。  "
      },
      {
        "line": 104,
        "text": "・apparent  "
      },
      {
        "line": 105,
        "text": "定義: 観察や状況から、そうだと見て取れる・思われる。  "
      },
      {
        "line": 106,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 107,
        "text": "違い: apparent は「そう見える」という含みから、実際には異なる可能性を残すことがある。evident は通常、利用可能な兆候から明らかだという判断をより直接に表す。  "
      },
      {
        "line": 108,
        "text": "例: It soon became apparent that the schedule was unrealistic.  "
      },
      {
        "line": 109,
        "text": "訳: その予定が現実的でないことは、まもなく明らかになった。  "
      },
      {
        "line": 111,
        "text": "・plain  "
      },
      {
        "line": 112,
        "text": "定義: 隠れたところがなく、見たり聞いたりすれば明らかな。  "
      },
      {
        "line": 113,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 114,
        "text": "違い: plain は `plain to see`、`make it plain` などで、率直に明示する感じも持つ。evident は感情や結果が兆候として現れる説明に向く。  "
      },
      {
        "line": 115,
        "text": "例: It was plain to see that the proposal needed more work.  "
      },
      {
        "line": 116,
        "text": "訳: その提案にさらに検討が必要なのは一目瞭然だった。  "
      },
      {
        "line": 118,
        "text": "・manifest  "
      },
      {
        "line": 119,
        "text": "定義: 性質・事実・感情などがはっきり外に現れている、明白な。  "
      },
      {
        "line": 120,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 121,
        "text": "違い: manifest は evident より硬く、文学・学術・形式的な文脈で、隠れたものが明確に現れたことを強調する。  "
      },
      {
        "line": 122,
        "text": "例: The report revealed a manifest lack of oversight.  "
      },
      {
        "line": 123,
        "text": "訳: その報告書は監督が明らかに欠けていたことを示した。  "
      },
      {
        "line": 125,
        "text": "・noticeable  "
      },
      {
        "line": 126,
        "text": "定義: 見たり感じたりして気づくことができる、目立つ。  "
      },
      {
        "line": 127,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 128,
        "text": "違い: noticeable は知覚上の目立ちやすさに焦点があり、そこから命題や判断が理解できることまでは含まない。evident は抽象的な事実や結論にも使える。  "
      },
      {
        "line": 129,
        "text": "例: There was a noticeable change in his attitude.  "
      },
      {
        "line": 130,
        "text": "訳: 彼の態度には目立った変化があった。  "
      },
      {
        "line": 132,
        "text": "【反意語】"
      },
      {
        "line": 134,
        "text": "・unclear  "
      },
      {
        "line": 135,
        "text": "定義: 意味・理由・状況などがはっきりせず、容易には理解できない。  "
      },
      {
        "line": 136,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 137,
        "text": "違い: evident の「情報や兆候から明らかである」という理解可能性の軸に対し、unclear は解釈や判断がまだ定まらない状態を表す。  "
      },
      {
        "line": 138,
        "text": "例: The reason for the sudden change remains unclear.  "
      },
      {
        "line": 139,
        "text": "訳: その突然の変化の理由は依然として不明だ。  "
      },
      {
        "line": 141,
        "text": "・obscure  "
      },
      {
        "line": 142,
        "text": "定義: 見えにくく、知られておらず、理解しにくい。  "
      },
      {
        "line": 143,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 144,
        "text": "違い: obscure は情報や特徴が隠れている・目立たないために認識しにくいことを強調し、evident の「前面に現れて分かる」と程度の軸で対照をなす。  "
      },
      {
        "line": 145,
        "text": "例: The connection between the two events was initially obscure.  "
      },
      {
        "line": 146,
        "text": "訳: その2つの出来事のつながりは、当初は分かりにくかった。  "
      }
    ],
    "antonym_axis_items": [
      {
        "item_id": "ant-4cdb1196ed11",
        "stage1_axis": {
          "item_id": "ant-4cdb1196ed11",
          "axis": "明瞭性",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 134,
          "line_end": 134,
          "exact_quote": "・unclear  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 137,
          "line_end": 137,
          "exact_quote": "違い: evident の「情報や兆候から明らかである」という理解可能性の軸に対し、unclear は解釈や判断がまだ定まらない状態を表す。  "
        }
      },
      {
        "item_id": "ant-bae621c7c63f",
        "stage1_axis": {
          "item_id": "ant-bae621c7c63f",
          "axis": "明瞭性",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 141,
          "line_end": 141,
          "exact_quote": "・obscure  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 144,
          "line_end": 144,
          "exact_quote": "違い: obscure は情報や特徴が隠れている・目立たないために認識しにくいことを強調し、evident の「前面に現れて分かる」と程度の軸で対照をなす。  "
        }
      }
    ],
    "antonym_axis_senses": [
      {
        "sense_id": "sense:001",
        "full_sense": [
          {
            "line": 30,
            "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
          },
          {
            "line": 32,
            "text": "【日本語訳・定義】見える特徴、行動、データ、状況などから、ある事実・状態・感情・評価を容易に認識または理解できることを表す。観察した人にとって明白だという意味であり、語そのものが論理的な証明や絶対的な確実性まで保証するわけではない。  "
          },
          {
            "line": 34,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 36,
            "text": "【レジスター/領域】標準語だが、会話中心の obvious や clear よりやや形式的。報告書、学術文、ニュース、ビジネスの説明で多く、感情や特徴が外から読み取れることにも使う。  "
          },
          {
            "line": 38,
            "text": "【文法パターン】something + be・seem・become・remain evident＝事実・状態などが明らかである／it + be・become + evident + that 〈節〉＝～であることが明らかだ／something + be evident to someone＝〈人〉にとって明らかだ／it + be evident to someone + that 〈節〉＝〈人〉には～が明らかだ／it + be evident from 〈data・evidence・behavior〉 + that 〈節〉＝〈データ・証拠・行動〉から～が明らかだ／something + be evident in 〈expression・results・pattern〉＝感情・特徴などが〈表情・結果・パターン〉に表れている／make something・make it evident + that 〈節〉＝何かを明白にする・～であることを明らかにする／evident + 〈change・difference・sign・need〉＝明らかな〈変化・違い・兆候・必要性〉。  "
          },
          {
            "line": 40,
            "text": "【コロケーション】"
          },
          {
            "line": 42,
            "text": "・it is evident that 〈節〉  "
          },
          {
            "line": 43,
            "text": "用途: 状況や観察結果から、ある判断が明らかだと述べる基本構文。  "
          },
          {
            "line": 44,
            "text": "例: It is evident that the current plan cannot meet the deadline.  "
          },
          {
            "line": 45,
            "text": "訳: 現在の計画では期限に間に合わないことが明らかだ。  "
          },
          {
            "line": 47,
            "text": "・be evident to someone  "
          },
          {
            "line": 48,
            "text": "用途: 何が誰にとって明らかなのかを示す。  "
          },
          {
            "line": 49,
            "text": "例: The benefits of the new system were immediately evident to the staff.  "
          },
          {
            "line": 50,
            "text": "訳: 新しいシステムの利点は職員にはすぐに明らかになった。  "
          },
          {
            "line": 52,
            "text": "・be evident from 〈data・evidence・results〉 that 〈節〉  "
          },
          {
            "line": 53,
            "text": "用途: 明白だと判断する根拠や情報源を示す。  "
          },
          {
            "line": 54,
            "text": "例: It was evident from the audit results that several invoices had been duplicated.  "
          },
          {
            "line": 55,
            "text": "訳: 監査結果から、複数の請求書が重複していたことは明らかだった。  "
          },
          {
            "line": 57,
            "text": "・be evident in 〈expression・behavior・pattern〉  "
          },
          {
            "line": 58,
            "text": "用途: 感情や特徴が表情・行動・結果などに現れていることを表す。  "
          },
          {
            "line": 59,
            "text": "例: Her disappointment was evident in the way she avoided eye contact.  "
          },
          {
            "line": 60,
            "text": "訳: 彼女が目を合わせようとしなかったことに、失望がはっきり表れていた。  "
          },
          {
            "line": 62,
            "text": "・become evident  "
          },
          {
            "line": 63,
            "text": "用途: 時間の経過や追加情報によって、それまで不明だったことが明らかになることを表す。  "
          },
          {
            "line": 64,
            "text": "例: The scale of the damage became evident after the smoke cleared.  "
          },
          {
            "line": 65,
            "text": "訳: 煙が晴れた後、被害の規模が明らかになった。  "
          },
          {
            "line": 67,
            "text": "・make it evident that 〈節〉  "
          },
          {
            "line": 68,
            "text": "用途: 数値、言動、結果などによって、ある判断を明白にする。  "
          },
          {
            "line": 69,
            "text": "例: The revised figures made it evident that the original estimate was too optimistic.  "
          },
          {
            "line": 70,
            "text": "訳: 修正後の数値によって、当初の見積もりが楽観的すぎたことが明らかになった。  "
          },
          {
            "line": 72,
            "text": "・evident signs of 〈change・stress・recovery〉  "
          },
          {
            "line": 73,
            "text": "用途: 変化、ストレス、回復などが起きていると分かる兆候を表す。  "
          },
          {
            "line": 74,
            "text": "例: The patient showed evident signs of recovery after the treatment.  "
          },
          {
            "line": 75,
            "text": "訳: その患者には治療後、回復の明らかな兆候が見られた。  "
          },
          {
            "line": 77,
            "text": "・with evident 〈relief・pleasure・concern〉  "
          },
          {
            "line": 78,
            "text": "用途: 表情や声などに感情が明確に現れている様子を表す。  "
          },
          {
            "line": 79,
            "text": "例: She spoke with evident relief after the results were announced.  "
          },
          {
            "line": 80,
            "text": "訳: 結果が発表された後、彼女はほっとした様子をはっきり見せて話した。  "
          },
          {
            "line": 82,
            "text": "【語法・注意】`evident to someone` は「誰にとって明らかか」、`evident from something` は「何を根拠に明らかか」、`evident in something` は「どこに表れているか」を示す。`evident that ...` のように内容を続ける場合は、通常 `It is evident that ...` と形式主語 it を置く。  "
          },
          {
            "line": 84,
            "text": "evident は「観察や情報から明らかだ」という評価であり、必ずしも「証明済み」「疑いなく真実」と同じではない。`It was evident from the preliminary data that ...` のように、判断の根拠が限定的であることも表せる。  "
          },
          {
            "line": 86,
            "text": "日常会話では obvious や clear の方が自然な場面が多い。`evident` は報告・説明調の響きがあり、`evident concern`、`evident improvement` のように、外から読み取れる感情や変化を名詞の前で修飾できる。`evidently` は副詞なので、`It is evident that ...` と `Evidently, ...` を品詞ごとに使い分ける。  "
          },
          {
            "line": 88,
            "text": "【類義語】"
          },
          {
            "line": 90,
            "text": "・obvious  "
          },
          {
            "line": 91,
            "text": "定義: 見たり考えたりすれば容易に分かる、明白な。  "
          },
          {
            "line": 92,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 93,
            "text": "違い: obvious は日常的で、証拠がなくても直観的に分かることに使える。evident は兆候や状況から判断できることをやや形式的に述べる。  "
          },
          {
            "line": 94,
            "text": "例: It was obvious from his expression that he was disappointed.  "
          },
          {
            "line": 95,
            "text": "訳: 彼の表情から、彼が失望しているのは明らかだった。  "
          },
          {
            "line": 97,
            "text": "・clear  "
          },
          {
            "line": 98,
            "text": "定義: 意味・事実・状況などが疑いなく理解できる、明確な。  "
          },
          {
            "line": 99,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 100,
            "text": "違い: clear は説明や指示を「分かりやすくする」意図にも使え、対象範囲が広い。evident は観察可能な兆候から明らかになることに焦点を置きやすい。  "
          },
          {
            "line": 101,
            "text": "例: The instructions were clear to everyone on the team.  "
          },
          {
            "line": 102,
            "text": "訳: その指示はチームの全員にとって明確だった。  "
          },
          {
            "line": 104,
            "text": "・apparent  "
          },
          {
            "line": 105,
            "text": "定義: 観察や状況から、そうだと見て取れる・思われる。  "
          },
          {
            "line": 106,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 107,
            "text": "違い: apparent は「そう見える」という含みから、実際には異なる可能性を残すことがある。evident は通常、利用可能な兆候から明らかだという判断をより直接に表す。  "
          },
          {
            "line": 108,
            "text": "例: It soon became apparent that the schedule was unrealistic.  "
          },
          {
            "line": 109,
            "text": "訳: その予定が現実的でないことは、まもなく明らかになった。  "
          },
          {
            "line": 111,
            "text": "・plain  "
          },
          {
            "line": 112,
            "text": "定義: 隠れたところがなく、見たり聞いたりすれば明らかな。  "
          },
          {
            "line": 113,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 114,
            "text": "違い: plain は `plain to see`、`make it plain` などで、率直に明示する感じも持つ。evident は感情や結果が兆候として現れる説明に向く。  "
          },
          {
            "line": 115,
            "text": "例: It was plain to see that the proposal needed more work.  "
          },
          {
            "line": 116,
            "text": "訳: その提案にさらに検討が必要なのは一目瞭然だった。  "
          },
          {
            "line": 118,
            "text": "・manifest  "
          },
          {
            "line": 119,
            "text": "定義: 性質・事実・感情などがはっきり外に現れている、明白な。  "
          },
          {
            "line": 120,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 121,
            "text": "違い: manifest は evident より硬く、文学・学術・形式的な文脈で、隠れたものが明確に現れたことを強調する。  "
          },
          {
            "line": 122,
            "text": "例: The report revealed a manifest lack of oversight.  "
          },
          {
            "line": 123,
            "text": "訳: その報告書は監督が明らかに欠けていたことを示した。  "
          },
          {
            "line": 125,
            "text": "・noticeable  "
          },
          {
            "line": 126,
            "text": "定義: 見たり感じたりして気づくことができる、目立つ。  "
          },
          {
            "line": 127,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 128,
            "text": "違い: noticeable は知覚上の目立ちやすさに焦点があり、そこから命題や判断が理解できることまでは含まない。evident は抽象的な事実や結論にも使える。  "
          },
          {
            "line": 129,
            "text": "例: There was a noticeable change in his attitude.  "
          },
          {
            "line": 130,
            "text": "訳: 彼の態度には目立った変化があった。  "
          },
          {
            "line": 132,
            "text": "【反意語】"
          },
          {
            "line": 134,
            "text": "・unclear  "
          },
          {
            "line": 135,
            "text": "定義: 意味・理由・状況などがはっきりせず、容易には理解できない。  "
          },
          {
            "line": 136,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 137,
            "text": "違い: evident の「情報や兆候から明らかである」という理解可能性の軸に対し、unclear は解釈や判断がまだ定まらない状態を表す。  "
          },
          {
            "line": 138,
            "text": "例: The reason for the sudden change remains unclear.  "
          },
          {
            "line": 139,
            "text": "訳: その突然の変化の理由は依然として不明だ。  "
          },
          {
            "line": 141,
            "text": "・obscure  "
          },
          {
            "line": 142,
            "text": "定義: 見えにくく、知られておらず、理解しにくい。  "
          },
          {
            "line": 143,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 144,
            "text": "違い: obscure は情報や特徴が隠れている・目立たないために認識しにくいことを強調し、evident の「前面に現れて分かる」と程度の軸で対照をなす。  "
          },
          {
            "line": 145,
            "text": "例: The connection between the two events was initially obscure.  "
          },
          {
            "line": 146,
            "text": "訳: その2つの出来事のつながりは、当初は分かりにくかった。  "
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
