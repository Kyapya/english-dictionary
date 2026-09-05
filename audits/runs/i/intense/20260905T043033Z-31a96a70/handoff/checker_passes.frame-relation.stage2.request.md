# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`agent-frame-relation-stage1-31a96a70`, declared_model=`gpt-5`.

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
  "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
  "blind_request_sha256": "12baa8d9929aa1dceed6f2ef9d86d8309df6ebe453a5077882e7e52252112d25",
  "blind_record_sha256": "fe6c8b9bb0c53f45438baf55e045ee32989d28db77f1cada52386133a7f26c6d",
  "input_sections": {
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、色、関心、圧力などの程度・強度が非常に高いこと。intense pleasure「非常に強い喜び」のように、好ましい対象にも使う。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 111,
        "text": "【日本語訳・定義】活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 158,
        "text": "【日本語訳・定義】人・視線・表情・関係などについて、強い感情や意見が表れる、強く感じられる、または強い感情的な結びつきがあること。人・表情の表出、人物への評価、関係の情緒的な強さを区別する。  "
      }
    ],
    "frames": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 50,
        "text": "【文法パターン】intense + 〈感情・感覚・性質・熱・色などを表す名詞〉＝程度・強度が非常に高い～／intense energy・determination・concentration＝エネルギー・決意・集中の強度が非常に高い／under intense pressure/scrutiny＝強い圧力・厳しい監視の下で  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 117,
        "text": "【文法パターン】intense + 〈活動・競争・議論・訓練など〉＝強度・エネルギー・努力・緊張や負荷が非常に高い活動・競争など  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 164,
        "text": "【文法パターン】an intense person＝感情や態度が強く、存在感や圧のある人（評価は文脈依存）／an intense look/gaze＝集中・鋭さ・強い感情を帯びた視線／an intense relationship＝情緒的な結びつきや相互作用が強い関係  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 52,
        "text": "【コロケーション】"
      },
      {
        "line": 54,
        "text": "・intense pain  "
      },
      {
        "line": 55,
        "text": "用途: 身体的な痛みが非常に強いことを表す。  "
      },
      {
        "line": 56,
        "text": "例: He felt intense pain in his lower back.  "
      },
      {
        "line": 57,
        "text": "訳: 彼は腰の下部に激しい痛みを感じた。  "
      },
      {
        "line": 59,
        "text": "・intense heat  "
      },
      {
        "line": 60,
        "text": "用途: 暑さや熱が非常に強いことを表す。  "
      },
      {
        "line": 61,
        "text": "例: The intense heat made it dangerous to work outside.  "
      },
      {
        "line": 62,
        "text": "訳: 強烈な暑さのため、屋外で働くのは危険だった。  "
      },
      {
        "line": 64,
        "text": "・intense pressure  "
      },
      {
        "line": 65,
        "text": "用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  "
      },
      {
        "line": 66,
        "text": "例: The new manager is under intense pressure to improve the results.  "
      },
      {
        "line": 67,
        "text": "訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  "
      },
      {
        "line": 69,
        "text": "・intense interest  "
      },
      {
        "line": 70,
        "text": "用途: ある対象に向けられる関心が非常に強いことを表す。  "
      },
      {
        "line": 71,
        "text": "例: The discovery attracted intense interest from researchers around the world.  "
      },
      {
        "line": 72,
        "text": "訳: その発見は世界中の研究者から強い関心を集めた。  "
      },
      {
        "line": 74,
        "text": "・intense anger  "
      },
      {
        "line": 75,
        "text": "用途: 怒りの感情が非常に強いことを表す。  "
      },
      {
        "line": 76,
        "text": "例: The decision provoked intense anger among local residents.  "
      },
      {
        "line": 77,
        "text": "訳: その決定は地元住民の激しい怒りを引き起こした。  "
      },
      {
        "line": 79,
        "text": "・intense blue  "
      },
      {
        "line": 80,
        "text": "用途: 色の強さや濃さが際立ち、強い印象を与えることを表す。  "
      },
      {
        "line": 81,
        "text": "例: The intense blue of the lake stood out against the white snow.  "
      },
      {
        "line": 82,
        "text": "訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 119,
        "text": "【コロケーション】"
      },
      {
        "line": 121,
        "text": "・intense competition  "
      },
      {
        "line": 122,
        "text": "用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。  "
      },
      {
        "line": 123,
        "text": "例: There is intense competition for places at the top universities.  "
      },
      {
        "line": 124,
        "text": "訳: 一流大学の枠をめぐって激しい競争がある。  "
      },
      {
        "line": 126,
        "text": "・intense activity  "
      },
      {
        "line": 127,
        "text": "用途: 活動の強度・エネルギー・負荷が非常に高いことを表す。  "
      },
      {
        "line": 128,
        "text": "例: The airport experienced a period of intense activity before the holiday.  "
      },
      {
        "line": 129,
        "text": "訳: その空港では休暇前に活動が非常に活発な時期があった。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 166,
        "text": "【コロケーション】"
      },
      {
        "line": 168,
        "text": "・an intense look  "
      },
      {
        "line": 169,
        "text": "用途: 強い感情や集中を帯びた視線・表情を表す。  "
      },
      {
        "line": 170,
        "text": "例: She gave him an intense look when he mentioned the accusation.  "
      },
      {
        "line": 171,
        "text": "訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  "
      },
      {
        "line": 173,
        "text": "・an intense person  "
      },
      {
        "line": 174,
        "text": "用途: 感情や態度が強く、存在感や圧のある人を表す。肯定・否定の評価は文脈で変わる。  "
      },
      {
        "line": 175,
        "text": "例: He is an intense person who takes every project very seriously.  "
      },
      {
        "line": 176,
        "text": "訳: 彼はどのプロジェクトにも非常に真剣に取り組む、強い存在感のある人だ。  "
      },
      {
        "line": 178,
        "text": "・an intense relationship  "
      },
      {
        "line": 179,
        "text": "用途: 感情的な結びつきや相互作用が非常に強い関係を表す。  "
      },
      {
        "line": 180,
        "text": "例: Their intense relationship left little room for emotional distance.  "
      },
      {
        "line": 181,
        "text": "訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 86,
        "text": "【類義語】"
      },
      {
        "line": 88,
        "text": "・strong  "
      },
      {
        "line": 89,
        "text": "定義: intense と比較される、幅広い「強い」を表す関連語。  "
      },
      {
        "line": 90,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 91,
        "text": "違い: strong は幅広い強さを表し、intense は感覚・感情などの強度が非常に高いことに焦点を置く。  "
      },
      {
        "line": 92,
        "text": "例: intense pain  "
      },
      {
        "line": 93,
        "text": "訳: 強い痛み。  "
      },
      {
        "line": 95,
        "text": "・extreme  "
      },
      {
        "line": 96,
        "text": "定義: intense と比較される、通常の範囲からの逸脱に焦点を置く関連語。  "
      },
      {
        "line": 97,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 98,
        "text": "違い: extreme は通常の範囲や限界からの逸脱に焦点があり、intense は体感や感情の強さにも使う。  "
      },
      {
        "line": 99,
        "text": "例: intense heat  "
      },
      {
        "line": 100,
        "text": "訳: 強烈な暑さ。  "
      },
      {
        "line": 102,
        "text": "・powerful  "
      },
      {
        "line": 103,
        "text": "定義: intense と比較される、作用する力や影響に焦点を置く関連語。  "
      },
      {
        "line": 104,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 105,
        "text": "違い: powerful は作用する力や影響力に焦点があり、intense は経験される強度や圧にも使う。  "
      },
      {
        "line": 106,
        "text": "例: intense interest  "
      },
      {
        "line": 107,
        "text": "訳: 強い関心。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 133,
        "text": "【類義語】"
      },
      {
        "line": 135,
        "text": "・fierce  "
      },
      {
        "line": 136,
        "text": "定義: intense と比較される、競争・対立の激しさに焦点を置く関連語。  "
      },
      {
        "line": 137,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 138,
        "text": "違い: fierce は攻撃性や対立を含みやすく、intense は敵意のない活動の強さにも使える。  "
      },
      {
        "line": 139,
        "text": "例: intense competition  "
      },
      {
        "line": 140,
        "text": "訳: 激しい競争。  "
      },
      {
        "line": 142,
        "text": "・vigorous  "
      },
      {
        "line": 143,
        "text": "定義: intense と比較される、活力や積極的なエネルギーに焦点を置く関連語。  "
      },
      {
        "line": 144,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 145,
        "text": "違い: vigorous は活力や積極的なエネルギーに焦点があり、intense は活動の緊張や負荷も表す。  "
      },
      {
        "line": 146,
        "text": "例: intense activity  "
      },
      {
        "line": 147,
        "text": "訳: 激しい活動。  "
      },
      {
        "line": 149,
        "text": "・strenuous  "
      },
      {
        "line": 150,
        "text": "定義: intense と比較される、大きな努力を要する行為に焦点を置く関連語。  "
      },
      {
        "line": 151,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 152,
        "text": "違い: strenuous は行為がきつく多大な努力を要することに焦点があり、intense は活動の緊張感や負荷も表す。  "
      },
      {
        "line": 153,
        "text": "例: intense training  "
      },
      {
        "line": 154,
        "text": "訳: 激しい訓練。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 185,
        "text": "【類義語】"
      },
      {
        "line": 187,
        "text": "・serious  "
      },
      {
        "line": 188,
        "text": "定義: intense と比較される、真剣さや重要性に焦点を置く関連語。  "
      },
      {
        "line": 189,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 190,
        "text": "違い: serious は真面目さや重要性に焦点があり、intense は強い感情や張り詰めた印象も表す。  "
      },
      {
        "line": 191,
        "text": "例: an intense person  "
      },
      {
        "line": 192,
        "text": "訳: 感情や態度の強い人。  "
      },
      {
        "line": 194,
        "text": "・passionate  "
      },
      {
        "line": 195,
        "text": "定義: intense と比較される、熱意や強い関与に焦点を置く関連語。  "
      },
      {
        "line": 196,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 197,
        "text": "違い: passionate は熱意や強い関与を表し、intense より肯定的な評価になりやすい。  "
      },
      {
        "line": 198,
        "text": "例: an intense look  "
      },
      {
        "line": 199,
        "text": "訳: 強い視線。  "
      },
      {
        "line": 201,
        "text": "・earnest  "
      },
      {
        "line": 202,
        "text": "定義: intense と比較される、誠実さや真摯さに焦点を置く関連語。  "
      },
      {
        "line": 203,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 204,
        "text": "違い: earnest は誠実さや真摯さに焦点があり、intense は感情の強さや対人的な圧も表す。  "
      },
      {
        "line": 205,
        "text": "例: an intense relationship  "
      },
      {
        "line": 206,
        "text": "訳: 感情的な結びつきの強い関係。  "
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
