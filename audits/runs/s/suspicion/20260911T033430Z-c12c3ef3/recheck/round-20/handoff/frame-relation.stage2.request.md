# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the serial second stage. Continue using the same reviewer id and the same independent review context as stage 1. Use this exact packet, including its sealed stage-1 record hash. Do not inspect prior rounds/findings or other passes. Save one antonym_axis_adjudication_record_v1 JSON object at `frame-relation.stage2.response.raw.json` with the actual same top-level reviewer metadata.

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

## 中断後の段階2再開

同じ担当contextが利用できる場合は継続する。失われた場合は、新しい独立contextが保存済み段階1の推論と固定の段階2入力を読んで照合だけを行う。段階1を再推論・改変せず、生成担当や他のcheckerを兼ねない。`sealed_stage1_replay_v1` の `stage1_replay` に、元の担当ID、保存済みrecord hash、段階2request hash、交代理由を記録し、reviewerには新担当の実際のID/modelを記す。原応答の保存がない場合は引き継ぎを証明した扱いにしない。


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
  "input_body_sha256": "22115ff16b934a7bee72be158df65dd1569ca9a64c670adb9cd408a03b504ebd",
  "blind_request_sha256": "ed44c6a081b1d2e895010211a338df1e100711a1765c79f5d763813c2cc75fdb",
  "blind_record_sha256": "4853c4e574d845759b8d6e34c418984791dff1c2b94a363676e830969cbd4a71",
  "input_sections": {
    "sense_structure": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 40,
        "text": "【日本語訳・定義】人が犯罪、不正、不誠実な行為などをした可能性があると、十分な証明がない段階で考えること、またはその疑いを向けられている状態を表す。複数の個別の疑いを述べる suspicions は可算、疑いという状態を表す suspicion は不可算で使われる。on suspicion of ... のように特定の容疑でも無冠詞となる定型表現があるため、可算・不可算は意味だけで一律には決まらない。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 93,
        "text": "【日本語訳・定義】人、組織、動機、考えなどの真実性や信頼性を確信できず、すぐには信用しない態度を表す。相手や情報の裏に問題や意図があるのではないかという警戒を伴うこともある。語義1のように特定の犯罪・不正行為を想定する必要はなく、広い意味での mistrust / distrust に近い。  "
      },
      {
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 138,
        "text": "【日本語訳・定義】十分な証拠はないが、犯罪・不正を含まない事実や状況が本当なのではないかと感じる推測・予感に焦点がある。本記事では、that節が特定の人の犯罪・不正行為を述べる用例は語義1に置き、語義3はそれ以外の事実・状況への推測に用いる。この用法では個々の考えを表す可算形が典型。可算・不可算は意味だけで一律に決まらず、構文にも左右される。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 188,
        "text": "【日本語訳・定義】色、味、匂い、感情、表情などが、はっきり大量に存在するのではなく「あるかないか分かる程度」にわずかに感じられることを表す。通常 a suspicion of ... の形で用いられる比喩的な用法である。  "
      }
    ],
    "frames": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 46,
        "text": "【文法パターン】suspicion that 〈person committed a crime/wrongdoing〉＝〈人が犯罪・不正をした〉のではないかという疑い／suspicion of 〈crime/wrongdoing〉＝〈犯罪・不正〉の疑い／suspicions about 〈person/behavior〉＝〈人・行動〉に関する疑い／arouse/raise suspicion＝疑いを招く／on suspicion of 〈crime〉＝〈犯罪〉の容疑で／be under suspicion＝疑いをかけられている／come/fall under suspicion＝疑いをかけられるようになる／cast suspicion on 〈person/action suspected of wrongdoing〉＝〈人・行為〉に犯罪・不正の疑いを向ける／confirm suspicions that 〈person committed a crime/wrongdoing〉＝〈人が犯罪・不正をした〉という疑いを裏付ける。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 99,
        "text": "【文法パターン】regard/view 〈person/claim/proposal/action/decision〉 with suspicion＝〈人・主張・提案・行為・決定〉を疑いの目で見る／〈offer/proposal〉 be greeted with (some) suspicion＝〈申し出・提案〉が（多少の）疑いをもって受け止められる／cast suspicion on 〈claim/statement or its truth/reliability〉＝〈主張・説明、またはその真実性・信頼性〉に疑いを向ける。  "
      },
      {
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 144,
        "text": "【文法パターン】a suspicion that 〈non-wrongdoing clause〉＝〈犯罪・不正を含まない節〉ではないかという気／have a suspicion that 〈non-wrongdoing clause〉＝〈犯罪・不正を含まない節〉ではないかと思う／a sneaking suspicion that 〈non-wrongdoing clause〉＝〈犯罪・不正を含まない節〉ではないかと思う気持ち／a strong suspicion that 〈non-wrongdoing clause〉＝〈犯罪・不正を含まない節〉という強い推測／confirm a suspicion＝推測を裏付ける。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 194,
        "text": "【文法パターン】a suspicion of 〈color/flavor/smell/emotion〉＝ほんの少しの〈色・味・匂い・感情〉／a suspicion of a smile＝かすかな笑み。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 48,
        "text": "【コロケーション】"
      },
      {
        "line": 50,
        "text": "・arouse suspicion  "
      },
      {
        "line": 51,
        "text": "用途: 行動・説明・状況が「何かおかしい」という疑いを生じさせる。  "
      },
      {
        "line": 52,
        "text": "例: The unexplained transfer of client funds aroused suspicion of fraud among the auditors.  "
      },
      {
        "line": 53,
        "text": "訳: 顧客資金の説明のない移動が、監査担当者たちに詐欺の疑いを抱かせた。  "
      },
      {
        "line": 55,
        "text": "・on suspicion of 〈crime〉  "
      },
      {
        "line": 56,
        "text": "用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕・拘束したことを述べる。  "
      },
      {
        "line": 57,
        "text": "例: Two people were arrested on suspicion of fraud after the investigation.  "
      },
      {
        "line": 58,
        "text": "訳: 捜査後、2人が詐欺の容疑で逮捕された。  "
      },
      {
        "line": 60,
        "text": "・be under suspicion  "
      },
      {
        "line": 61,
        "text": "用途: 人・組織などが不正や犯罪をしたのではないかと疑われている状態を表す。  "
      },
      {
        "line": 62,
        "text": "例: The contractor remained under suspicion until the records were checked.  "
      },
      {
        "line": 63,
        "text": "訳: 記録が確認されるまで、その請負業者には疑いがかけられたままだった。  "
      },
      {
        "line": 65,
        "text": "・come/fall under suspicion  "
      },
      {
        "line": 66,
        "text": "用途: 新しい情報などをきっかけに、疑いの対象になることを表す。  "
      },
      {
        "line": 67,
        "text": "例: The employee came under suspicion when several invoices disappeared.  "
      },
      {
        "line": 68,
        "text": "訳: 複数の請求書がなくなったことで、その従業員が疑われるようになった。  "
      },
      {
        "line": 70,
        "text": "・cast suspicion on 〈person/action suspected of wrongdoing〉  "
      },
      {
        "line": 71,
        "text": "用途: 犯罪・不正をした可能性がある人や行為に疑いを向けることを表す。  "
      },
      {
        "line": 72,
        "text": "例: The altered timestamp cast suspicion on the clerk who had access to the report.  "
      },
      {
        "line": 73,
        "text": "訳: 変更された時刻表示によって、報告書にアクセスできた事務員に疑いが向けられた。  "
      },
      {
        "line": 75,
        "text": "・confirm suspicions  "
      },
      {
        "line": 76,
        "text": "用途: それまで抱いていた疑いが裏付けられることを表す。  "
      },
      {
        "line": 77,
        "text": "例: The security footage confirmed the manager's suspicions that a guard had stolen the missing laptops.  "
      },
      {
        "line": 78,
        "text": "訳: 防犯映像によって、警備員がなくなったノートパソコンを盗んだという管理者の疑いが裏付けられた。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 101,
        "text": "【コロケーション】"
      },
      {
        "line": 103,
        "text": "・regard/view 〈person/claim/proposal/action/decision〉 with suspicion  "
      },
      {
        "line": 104,
        "text": "用途: 人・主張・提案・行為・決定をすぐには信用せず、疑いの目で見ることを表す。  "
      },
      {
        "line": 105,
        "text": "例: Residents viewed the sudden policy change with suspicion.  "
      },
      {
        "line": 106,
        "text": "訳: 住民たちは突然の方針変更を疑いの目で見た。  "
      },
      {
        "line": 108,
        "text": "・be greeted with (some) suspicion  "
      },
      {
        "line": 109,
        "text": "用途: 申し出・提案などが、当初は信用されず、疑いをもって受け止められることを表す。  "
      },
      {
        "line": 110,
        "text": "例: The new monitoring system was initially greeted with some suspicion.  "
      },
      {
        "line": 111,
        "text": "訳: 新しい監視システムは当初、多少の疑いをもって受け止められた。  "
      },
      {
        "line": 113,
        "text": "・cast suspicion on 〈claim/statement or its truth/reliability〉  "
      },
      {
        "line": 114,
        "text": "用途: 主張や説明の真実性・信頼性を疑わしいものとして扱うことを表す。  "
      },
      {
        "line": 115,
        "text": "例: The discrepancy cast suspicion on the reliability of the company's explanation.  "
      },
      {
        "line": 116,
        "text": "訳: その食い違いによって、その会社の説明の信頼性に疑いが向けられた。  "
      },
      {
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 146,
        "text": "【コロケーション】"
      },
      {
        "line": 148,
        "text": "・have a suspicion that 〈clause〉  "
      },
      {
        "line": 149,
        "text": "用途: 十分な証拠はないが、あることが本当ではないかと感じていることを表す。  "
      },
      {
        "line": 150,
        "text": "例: I have a suspicion that the meeting will finish earlier than planned.  "
      },
      {
        "line": 151,
        "text": "訳: その会議は予定より早く終わるのではないかという気がしている。  "
      },
      {
        "line": 153,
        "text": "・a sneaking suspicion that 〈clause〉  "
      },
      {
        "line": 154,
        "text": "用途: はっきり認めるほどではないが、心のどこかでそう思っていることを表す。  "
      },
      {
        "line": 155,
        "text": "例: She had a sneaking suspicion that everyone already knew the answer.  "
      },
      {
        "line": 156,
        "text": "訳: 彼女は、皆すでに答えを知っているのではないかとひそかに感じていた。  "
      },
      {
        "line": 158,
        "text": "・a strong suspicion that 〈clause〉  "
      },
      {
        "line": 159,
        "text": "用途: あることが本当ではないかという強い推測を表す。  "
      },
      {
        "line": 160,
        "text": "例: We had a strong suspicion that the delay was caused by a technical problem.  "
      },
      {
        "line": 161,
        "text": "訳: 私たちは、その遅延は技術的な問題によるのではないかという強い疑いを抱いていた。  "
      },
      {
        "line": 163,
        "text": "・confirm a suspicion  "
      },
      {
        "line": 164,
        "text": "用途: それまで確証のなかった推測が、後の情報によって正しかったと分かる。  "
      },
      {
        "line": 165,
        "text": "例: The test results confirmed her suspicion that the battery was failing.  "
      },
      {
        "line": 166,
        "text": "訳: 検査結果によって、バッテリーが劣化しているのではないかという彼女の推測が裏付けられた。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 196,
        "text": "【コロケーション】"
      },
      {
        "line": 198,
        "text": "・a suspicion of 〈color〉  "
      },
      {
        "line": 199,
        "text": "用途: 色合いがごくわずかに混じって見えることを描写する。  "
      },
      {
        "line": 200,
        "text": "例: The walls were white with a suspicion of blue in the evening light.  "
      },
      {
        "line": 201,
        "text": "訳: その壁は白かったが、夕方の光の中ではほんのり青みを帯びていた。  "
      },
      {
        "line": 203,
        "text": "・a suspicion of 〈flavor〉  "
      },
      {
        "line": 204,
        "text": "用途: 味や香りがごく弱く感じられることを表す。  "
      },
      {
        "line": 205,
        "text": "例: The sauce had a suspicion of citrus that made it taste fresher.  "
      },
      {
        "line": 206,
        "text": "訳: そのソースにはほんのり柑橘の風味があり、より爽やかに感じられた。  "
      },
      {
        "line": 208,
        "text": "・a suspicion of 〈emotion〉  "
      },
      {
        "line": 209,
        "text": "用途: 感情が表情・声などにわずかに現れていることを描写する。  "
      },
      {
        "line": 210,
        "text": "例: There was a suspicion of disappointment in his voice.  "
      },
      {
        "line": 211,
        "text": "訳: 彼の声にはかすかな失望がにじんでいた。  "
      },
      {
        "line": 213,
        "text": "・a suspicion of a smile  "
      },
      {
        "line": 214,
        "text": "用途: はっきり笑うほどではない、わずかな笑みを描写する。  "
      },
      {
        "line": 215,
        "text": "例: A suspicion of a smile appeared at the corner of her mouth.  "
      },
      {
        "line": 216,
        "text": "訳: 彼女の口元に、かすかな笑みが浮かんだ。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 82,
        "text": "【類義語】"
      },
      {
        "line": 84,
        "text": "・mistrust  "
      },
      {
        "line": 85,
        "text": "定義: 人の誠実さや動機を信用せず、不正をしている可能性を疑うこと。  "
      },
      {
        "line": 86,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 87,
        "text": "違い: mistrust は相手への信頼の欠如に焦点がある。suspicion は特定の不正の可能性や、疑いを向けられている状態も表せる。  "
      },
      {
        "line": 88,
        "text": "例: The missing receipts deepened the auditors' mistrust of the treasurer.  "
      },
      {
        "line": 89,
        "text": "訳: 領収書が見当たらなかったことで、監査担当者たちの会計係への不信が強まった。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 120,
        "text": "【類義語】"
      },
      {
        "line": 122,
        "text": "・distrust  "
      },
      {
        "line": 123,
        "text": "定義: 人・組織・情報などを信用できないという感覚。  "
      },
      {
        "line": 124,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 125,
        "text": "違い: distrust はこの意味での近い語で、信用できない状態を直接表す。suspicion は、真実性・公正さ・信頼性などへの信頼が薄いことを表す場合がある。  "
      },
      {
        "line": 126,
        "text": "例: Public distrust increased after the data leak.  "
      },
      {
        "line": 127,
        "text": "訳: データ流出後、世間の不信が強まった。  "
      },
      {
        "line": 129,
        "text": "・mistrust  "
      },
      {
        "line": 130,
        "text": "定義: 人・物事を十分には信頼しないこと。  "
      },
      {
        "line": 131,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 132,
        "text": "違い: Merriam-Webster の説明では、mistrust は suspicion に基づく信頼の欠如を強調する。  "
      },
      {
        "line": 133,
        "text": "例: There was longstanding mistrust between the two groups.  "
      },
      {
        "line": 134,
        "text": "訳: その二つの集団の間には長年の不信があった。  "
      },
      {
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 170,
        "text": "【類義語】"
      },
      {
        "line": 172,
        "text": "・doubt  "
      },
      {
        "line": 173,
        "text": "定義: ある事実が真実かどうか、確信が持てないこと。  "
      },
      {
        "line": 174,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 175,
        "text": "違い: doubt は真偽への不確かさを広く表す。suspicion は「そうではないか」という暫定的な見方や予感に焦点がある。  "
      },
      {
        "line": 176,
        "text": "例: The test results raised doubts about whether the battery was failing.  "
      },
      {
        "line": 177,
        "text": "訳: 検査結果から、バッテリーが劣化しているのかどうか疑問が生じた。  "
      },
      {
        "line": 179,
        "text": "・belief  "
      },
      {
        "line": 180,
        "text": "定義: 十分な証明がなくても、あることが真実だと考えること。  "
      },
      {
        "line": 181,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 182,
        "text": "違い: belief はその考えへの確信を広く表し、疑いや不安を含むとは限らない。suspicion は確証のない見立てであることを前面に出す。  "
      },
      {
        "line": 183,
        "text": "例: The team had a strong belief that the repairs would solve the problem.  "
      },
      {
        "line": 184,
        "text": "訳: チームは修理で問題が解決すると強く考えていた。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 220,
        "text": "【類義語】"
      },
      {
        "line": 222,
        "text": "・hint  "
      },
      {
        "line": 223,
        "text": "定義: 色・味・感情などのかすかな兆し・少量。  "
      },
      {
        "line": 224,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 225,
        "text": "違い: hint はこの「少量」の意味で一般的。suspicion はやや改まった表現で、あえて「感じ取れる程度」という含みを出す。  "
      },
      {
        "line": 226,
        "text": "例: The tea has a hint of mint.  "
      },
      {
        "line": 227,
        "text": "訳: そのお茶にはほのかなミントの風味がある。  "
      },
      {
        "line": 229,
        "text": "・trace  "
      },
      {
        "line": 230,
        "text": "定義: かろうじて認められるごく少量・痕跡。  "
      },
      {
        "line": 231,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 232,
        "text": "違い: trace は量の少なさや痕跡性を直接表す。suspicion は比喩的で、感覚的な描写に使われやすい。  "
      },
      {
        "line": 233,
        "text": "例: There was only a trace of smoke in the air.  "
      },
      {
        "line": 234,
        "text": "訳: 空気中には煙がごくわずかにあるだけだった。  "
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
