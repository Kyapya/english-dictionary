# Independent checker handoff

Stage: `checker_passes/frame-relation`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.frame-relation.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
This is frame-relation stage 1 only. Keep this exact subagent available. After the coordinator fans in all seven stage-1 responses, the same subagent reviewer.agent_id and declared_model must execute the generated frame-relation stage-2 request before this pass is complete.

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
  "schema_version": "antonym_axis_blind_request_v1",
  "pass_id": "frame-relation",
  "taxonomy_ids": [
    "argument_slot_role_mismatch",
    "lexical_relation_mislabel"
  ],
  "specification": "prompts/check_pass_frame_relation_v7.md",
  "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
  "input_sections": {
    "antonym_items": [
      {
        "item_id": "ant-af2cb1b9bd23",
        "headword": "intense",
        "sense_definition": "【日本語訳・定義】人、視線、表情、会話、関係などが、非常に強い感情、意見、考え、目的意識を示すこと。真剣で集中しているという肯定的な意味にも、重い・圧が強い・感情的に負担が大きいという否定的な評価にもなり得る。",
        "antonym": "detached",
        "antonym_definition": "定義: 感情的に関与せず、距離を置いた。"
      },
      {
        "item_id": "ant-80779d1bfcd6",
        "headword": "intense",
        "sense_definition": "【日本語訳・定義】人、視線、表情、会話、関係などが、非常に強い感情、意見、考え、目的意識を示すこと。真剣で集中しているという肯定的な意味にも、重い・圧が強い・感情的に負担が大きいという否定的な評価にもなり得る。",
        "antonym": "casual",
        "antonym_definition": "定義: 態度、会話、関係などが気軽で、形式張らない。"
      },
      {
        "item_id": "ant-41690c7b43ad",
        "headword": "intense",
        "sense_definition": "【日本語訳・定義】活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。対象の客観的な密度だけでなく、それに参加・直面する人が感じる圧や負荷を表すことがある。",
        "antonym": "light",
        "antonym_definition": "定義: 仕事、運動、訓練などの負荷が小さい。"
      },
      {
        "item_id": "ant-f114c7dc9bc6",
        "headword": "intense",
        "sense_definition": "【日本語訳・定義】感情、感覚、痛み、暑さ、光、色、関心、圧力などの程度が極端に強いこと。単に「強い」というより、対象にかかる力や感じられる圧が大きいことを表す。必ず不快・否定的とは限らず、intense pleasure「非常に強い喜び」のように好ましい対象にも使う。",
        "antonym": "weak",
        "antonym_definition": "定義: 力、効果、信号などが弱い。"
      },
      {
        "item_id": "ant-464499db347e",
        "headword": "intense",
        "sense_definition": "【日本語訳・定義】感情、感覚、痛み、暑さ、光、色、関心、圧力などの程度が極端に強いこと。単に「強い」というより、対象にかかる力や感じられる圧が大きいことを表す。必ず不快・否定的とは限らず、intense pleasure「非常に強い喜び」のように好ましい対象にも使う。",
        "antonym": "mild",
        "antonym_definition": "定義: 程度が穏やかで、強すぎない。"
      },
      {
        "item_id": "ant-1a4b697f8e4b",
        "headword": "intense",
        "sense_definition": "【日本語訳・定義】活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。対象の客観的な密度だけでなく、それに参加・直面する人が感じる圧や負荷を表すことがある。",
        "antonym": "moderate",
        "antonym_definition": "定義: 程度や強さが中程度の。"
      },
      {
        "item_id": "ant-f870f7405e53",
        "headword": "intense",
        "sense_definition": "【日本語訳・定義】人、視線、表情、会話、関係などが、非常に強い感情、意見、考え、目的意識を示すこと。真剣で集中しているという肯定的な意味にも、重い・圧が強い・感情的に負担が大きいという否定的な評価にもなり得る。",
        "antonym": "relaxed",
        "antonym_definition": "定義: 緊張や気負いがなく、落ち着いている。"
      },
      {
        "item_id": "ant-06d30634b64f",
        "headword": "intense",
        "sense_definition": "【日本語訳・定義】感情、感覚、痛み、暑さ、光、色、関心、圧力などの程度が極端に強いこと。単に「強い」というより、対象にかかる力や感じられる圧が大きいことを表す。必ず不快・否定的とは限らず、intense pleasure「非常に強い喜び」のように好ましい対象にも使う。",
        "antonym": "faint",
        "antonym_definition": "定義: 光、音、色、においなどがかすかな。"
      }
    ]
  },
  "blind_protocol": {
    "stage": 1,
    "withheld_fields": [
      "difference_line",
      "frequency_line",
      "example_line",
      "translation_line",
      "synonym_section",
      "core_image",
      "other_senses",
      "document_order"
    ],
    "questions": [
      "name_axis_as_one_noun",
      "classify_as_補完_程度_方向_評価_状態",
      "record_unnamable_with_one_sentence_reason"
    ],
    "required_output_schema": "antonym_axis_blind_record_v1"
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
