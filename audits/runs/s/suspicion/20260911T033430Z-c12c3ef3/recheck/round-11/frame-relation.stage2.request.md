# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

The response must be one `antonym_axis_adjudication_record_v1` JSON object and must be saved as `frame-relation.stage2.response.json`.

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
  "input_body_sha256": "13559d31b050882ff1d24890c8d22914c8f87e20f0ddb0e509e2a8178469bd82",
  "blind_request_sha256": "0b632797f15af5e5cbc7db5557467f444d16e6ed5d4c1782713ff9084c507bf3",
  "blind_record_sha256": "219da6a10811da155b929566328b809f3883a51b873eabf10a2d683dfbb32eaa",
  "input_sections": {
    "sense_structure": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 38,
        "text": "【日本語訳・定義】確証がない段階で、ある事柄が真実かもしれないと考えることを表す。人が犯罪・不正をした可能性への疑いもこの意味に含む。Oxfordは犯罪・不正の疑いでは可算・不可算の両用法を、命題の真偽については可算用法を記している。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 91,
        "text": "【日本語訳・定義】人や物事を十分に信用できず、疑いの目で見る態度を表す。ある事柄が真実かどうかについての見立てを表す語義1とは異なり、対象への不信や警戒に焦点を置く。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 119,
        "text": "【日本語訳・定義】ものがごく少量、またはかすかな兆候として感じられることを表す。通常 a suspicion of ... の形で使われる。  "
      }
    ],
    "frames": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 44,
        "text": "【文法パターン】suspicion that 〈clause〉＝～ではないかという疑い／have a suspicion that 〈clause〉＝～ではないかという疑いを抱く／arouse 〈person〉's suspicions that 〈clause〉＝〈人〉に～ではないかという疑いを起こさせる／raise some suspicion among 〈people〉 that 〈clause〉＝〈人々〉の間に～ではないかという疑いを生じさせる／on suspicion of 〈offence〉＝〈犯罪〉の容疑で／be under suspicion＝疑いをかけられている。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 97,
        "text": "【文法パターン】regard 〈person/thing〉 with suspicion＝〈人・物事〉を疑いの目で見る。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 125,
        "text": "【文法パターン】a suspicion of 〈a smile〉＝笑みがかすかに感じられること／a suspicion of 〈truth〉＝真実味がかすかに感じられること。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 46,
        "text": "【コロケーション】"
      },
      {
        "line": 48,
        "text": "・on suspicion of 〈crime〉  "
      },
      {
        "line": 49,
        "text": "用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕・拘束したことを述べる。  "
      },
      {
        "line": 50,
        "text": "例: Two people were arrested on suspicion of fraud after the investigation.  "
      },
      {
        "line": 51,
        "text": "訳: 捜査後、2人が詐欺の容疑で逮捕された。  "
      },
      {
        "line": 53,
        "text": "・be under suspicion  "
      },
      {
        "line": 54,
        "text": "用途: 人が不正や犯罪をしたのではないかと疑われている状態を表す。  "
      },
      {
        "line": 55,
        "text": "例: The contractor remained under suspicion while investigators checked whether it had falsified invoices.  "
      },
      {
        "line": 56,
        "text": "訳: 請求書を改ざんしたかどうかを捜査員が調べる間、その請負業者は疑いをかけられたままだった。  "
      },
      {
        "line": 58,
        "text": "・a suspicion that 〈clause〉  "
      },
      {
        "line": 59,
        "text": "用途: 確証がない段階で、節の内容が事実かもしれないという見立てを表す。  "
      },
      {
        "line": 60,
        "text": "例: The manager had a suspicion that the cashier had altered the sales records.  "
      },
      {
        "line": 61,
        "text": "訳: その管理者は、レジ係が売上記録を改ざんしたのではないかと疑っていた。  "
      },
      {
        "line": 63,
        "text": "・have a suspicion that 〈clause〉  "
      },
      {
        "line": 64,
        "text": "用途: 出来事や状態が実際に起きた、または成り立つのではないかという考えを抱く。  "
      },
      {
        "line": 65,
        "text": "例: I had a suspicion that the meeting had been canceled.  "
      },
      {
        "line": 66,
        "text": "訳: 会議は中止されたのではないかと私は疑っていた。  "
      },
      {
        "line": 68,
        "text": "・arouse someone's suspicions  "
      },
      {
        "line": 69,
        "text": "用途: ある出来事を受け、〈人〉が節の内容を真実かもしれないと疑うきっかけになる。  "
      },
      {
        "line": 70,
        "text": "例: The abrupt policy reversal aroused residents' suspicions that officials had concealed the project's true cost.  "
      },
      {
        "line": 71,
        "text": "訳: 突然の方針転換を受けて、住民たちは当局が事業の本当の費用を隠していたのではないかと疑い始めた。  "
      },
      {
        "line": 73,
        "text": "・raise some suspicion among 〈people〉  "
      },
      {
        "line": 74,
        "text": "用途: 説明できない事実が、人々の間に節の内容への疑いを生じさせる。  "
      },
      {
        "line": 75,
        "text": "例: The unexplained gap in the records raised some suspicion among auditors that several invoices had been altered.  "
      },
      {
        "line": 76,
        "text": "訳: 記録の説明できない欠落から、複数の請求書が改ざんされていたのではないかという疑いが監査担当者の間に生じた。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 99,
        "text": "【コロケーション】"
      },
      {
        "line": 101,
        "text": "・regard 〈person/thing〉 with suspicion  "
      },
      {
        "line": 102,
        "text": "用途: 人や物事をすぐには信用せず、疑いの目で見ることを表す。  "
      },
      {
        "line": 103,
        "text": "例: Residents regarded the sudden policy change with suspicion.  "
      },
      {
        "line": 104,
        "text": "訳: 住民たちは突然の方針変更を疑いの目で見た。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 127,
        "text": "【コロケーション】"
      },
      {
        "line": 129,
        "text": "・a suspicion of a smile  "
      },
      {
        "line": 130,
        "text": "用途: はっきり表れるほどではない、かすかな兆しを描写する。  "
      },
      {
        "line": 131,
        "text": "例: There was a suspicion of a smile in her reply.  "
      },
      {
        "line": 132,
        "text": "訳: 彼女の返事にはかすかな笑みが感じられた。  "
      },
      {
        "line": 134,
        "text": "・a suspicion of truth  "
      },
      {
        "line": 135,
        "text": "用途: 話や印象に真実味がかすかに感じられることを表す。  "
      },
      {
        "line": 136,
        "text": "例: The old tale had a suspicion of truth in it.  "
      },
      {
        "line": 137,
        "text": "訳: その古い物語には、どこか真実味が感じられた。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 80,
        "text": "【類義語】"
      },
      {
        "line": 82,
        "text": "・doubt  "
      },
      {
        "line": 83,
        "text": "定義: ある事柄の真偽について確信が持てない状態。  "
      },
      {
        "line": 84,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 85,
        "text": "違い: doubt は真偽の不確かさを広く表し、suspicion はある事柄が真実かもしれないという見立ても表す。  "
      },
      {
        "line": 86,
        "text": "例: There was some doubt about whether the meeting had been canceled.  "
      },
      {
        "line": 87,
        "text": "訳: 会議が中止されたかどうかについて、多少の疑問があった。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 108,
        "text": "【類義語】"
      },
      {
        "line": 110,
        "text": "・distrust  "
      },
      {
        "line": 111,
        "text": "定義: 人や物事を信頼できない気持ち。  "
      },
      {
        "line": 112,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 113,
        "text": "違い: distrust は信頼できない気持ちを直接表し、with suspicion は人や物事を疑いの目で見る態度を表す。Oxford Advanced American Dictionary は suspicion の第3語義を「人や物事を信頼できない気持ち」と説明し、両者の意味の重なりを示す。  "
      },
      {
        "line": 114,
        "text": "例: Residents regarded the proposal with distrust.  "
      },
      {
        "line": 115,
        "text": "訳: 住民たちはその提案を信用しなかった。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 141,
        "text": "【類義語】"
      },
      {
        "line": 143,
        "text": "・hint  "
      },
      {
        "line": 144,
        "text": "定義: Oxfordがこのごく少量・かすかな兆しの語義で挙げる類義語。  "
      },
      {
        "line": 145,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 146,
        "text": "違い: Oxfordはhintをこの語義の類義語として挙げ、suspicionの用法をformalと記している。  "
      },
      {
        "line": 147,
        "text": "例: The tea has a hint of mint.  "
      },
      {
        "line": 148,
        "text": "訳: そのお茶にはほのかなミントの風味がある。  "
      },
      {
        "line": 150,
        "text": "・trace  "
      },
      {
        "line": 151,
        "text": "定義: ごくわずかな量や痕跡を表す語。Merriam-Websterは本語義の類義語として挙げている。  "
      },
      {
        "line": 152,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 153,
        "text": "違い: Merriam-Websterはsuspicionの本語義をbarely detectable amount or traceと説明し、Oxfordはこの用法をformalとしている。  "
      },
      {
        "line": 154,
        "text": "例: There was only a trace of smoke in the air.  "
      },
      {
        "line": 155,
        "text": "訳: 空気中には煙がほんのわずかに漂っていた。  "
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
