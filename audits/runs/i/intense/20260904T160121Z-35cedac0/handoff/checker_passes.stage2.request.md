# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`01a06d38-eb50-7b73-a126-1ec01be250b5`, declared_model=`gpt-5`.

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
  "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
  "blind_request_sha256": "bb7ac6fe828f9b6c609d2665f7e237e63afc7832e4e313208d36d064a9d38225",
  "blind_record_sha256": "83807b503479733863986124a338274049a4caa16c19d3492b892fa6e4d75e04",
  "input_sections": {
    "sense_structure": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 45,
        "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、光、色、関心、圧力などの程度が極端に強いこと。単に「強い」というより、対象にかかる力や感じられる圧が大きいことを表す。必ず不快・否定的とは限らず、intense pleasure「非常に強い喜び」のように好ましい対象にも使う。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 156,
        "text": "【日本語訳・定義】活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。対象の客観的な密度だけでなく、それに参加・直面する人が感じる圧や負荷を表すことがある。  "
      },
      {
        "line": 258,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 260,
        "text": "【日本語訳・定義】人、視線、表情、会話、関係などが、非常に強い感情、意見、考え、目的意識を示すこと。真剣で集中しているという肯定的な意味にも、重い・圧が強い・感情的に負担が大きいという否定的な評価にもなり得る。  "
      }
    ],
    "frames": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 51,
        "text": "【文法パターン】intense + 〈感情・感覚・性質を表す名詞〉＝非常に強い～／become/get/feel intense＝程度や感じ方が強くなる／under intense pressure/scrutiny＝強い圧力・厳しい監視の下で／intense + 〈色・光・熱など〉＝非常に鮮やかな・強烈な～  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 162,
        "text": "【文法パターン】intense + 〈活動・競争・議論・努力〉＝激しい・集中した～／an intense period of 〈活動〉＝激しい～の期間／become/get intense＝活動や状況が激しくなる／intense + 〈活動〉 over 〈期間〉＝一定期間に集中して行われる激しい～  "
      },
      {
        "line": 258,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 266,
        "text": "【文法パターン】an intense person＝感情や目的意識の強い人／an intense look/gaze/expression＝強い感情や集中を帯びた視線・表情／an intense conversation/relationship＝感情的な圧や結びつきの強い会話・関係／be intense about 〈事柄〉＝〈事柄〉に非常に熱心・真剣である／too intense＝人ややり取りが重すぎる、圧が強すぎる  "
      }
    ],
    "collocations_examples": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 53,
        "text": "【コロケーション】"
      },
      {
        "line": 55,
        "text": "・intense pain  "
      },
      {
        "line": 56,
        "text": "用途: 身体的な痛みが非常に強いことを表す。  "
      },
      {
        "line": 57,
        "text": "例: He felt intense pain in his lower back.  "
      },
      {
        "line": 58,
        "text": "訳: 彼は腰の下部に激しい痛みを感じた。  "
      },
      {
        "line": 60,
        "text": "・intense heat  "
      },
      {
        "line": 61,
        "text": "用途: 暑さや熱が極端に強いことを表す。  "
      },
      {
        "line": 62,
        "text": "例: The intense heat made it dangerous to work outside.  "
      },
      {
        "line": 63,
        "text": "訳: 強烈な暑さのため、屋外で働くのは危険だった。  "
      },
      {
        "line": 65,
        "text": "・intense pressure  "
      },
      {
        "line": 66,
        "text": "用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  "
      },
      {
        "line": 67,
        "text": "例: The new manager is under intense pressure to improve the results.  "
      },
      {
        "line": 68,
        "text": "訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  "
      },
      {
        "line": 70,
        "text": "・intense interest  "
      },
      {
        "line": 71,
        "text": "用途: ある対象に向けられる関心が非常に強いことを表す。  "
      },
      {
        "line": 72,
        "text": "例: The discovery attracted intense interest from researchers around the world.  "
      },
      {
        "line": 73,
        "text": "訳: その発見は世界中の研究者から強い関心を集めた。  "
      },
      {
        "line": 75,
        "text": "・intense anger  "
      },
      {
        "line": 76,
        "text": "用途: 怒りの感情が非常に強いことを表す。  "
      },
      {
        "line": 77,
        "text": "例: The decision provoked intense anger among local residents.  "
      },
      {
        "line": 78,
        "text": "訳: その決定は地元住民の激しい怒りを引き起こした。  "
      },
      {
        "line": 80,
        "text": "・intense blue  "
      },
      {
        "line": 81,
        "text": "用途: 色が非常に鮮やかで、見る人に強い印象を与えることを表す。  "
      },
      {
        "line": 82,
        "text": "例: The intense blue of the lake stood out against the white snow.  "
      },
      {
        "line": 83,
        "text": "訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 164,
        "text": "【コロケーション】"
      },
      {
        "line": 166,
        "text": "・intense competition  "
      },
      {
        "line": 167,
        "text": "用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。  "
      },
      {
        "line": 168,
        "text": "例: There is intense competition for places at the top universities.  "
      },
      {
        "line": 169,
        "text": "訳: 一流大学の枠をめぐって激しい競争がある。  "
      },
      {
        "line": 171,
        "text": "・intense debate  "
      },
      {
        "line": 172,
        "text": "用途: 議論が強い意見の対立や集中したやり取りを伴うことを表す。  "
      },
      {
        "line": 173,
        "text": "例: The proposal led to intense debate in parliament.  "
      },
      {
        "line": 174,
        "text": "訳: その提案は議会で激しい議論を引き起こした。  "
      },
      {
        "line": 176,
        "text": "・intense activity  "
      },
      {
        "line": 177,
        "text": "用途: 短期間に多くの活動が集中して行われることを表す。  "
      },
      {
        "line": 178,
        "text": "例: The airport experienced a period of intense activity before the holiday.  "
      },
      {
        "line": 179,
        "text": "訳: その空港では休暇前に活動が集中する時期があった。  "
      },
      {
        "line": 181,
        "text": "・intense effort  "
      },
      {
        "line": 182,
        "text": "用途: 目標達成のために大きな力と集中を注ぐ努力を表す。  "
      },
      {
        "line": 183,
        "text": "例: The rescue required intense effort from everyone on the team.  "
      },
      {
        "line": 184,
        "text": "訳: その救助にはチーム全員の大変な努力が必要だった。  "
      },
      {
        "line": 186,
        "text": "・intense negotiations  "
      },
      {
        "line": 187,
        "text": "用途: 短期間に意見を激しく交わし、妥結を目指す交渉を表す。  "
      },
      {
        "line": 188,
        "text": "例: The two sides held intense negotiations throughout the night.  "
      },
      {
        "line": 189,
        "text": "訳: 両陣営は一晩中、激しい交渉を続けた。  "
      },
      {
        "line": 191,
        "text": "・intense training  "
      },
      {
        "line": 192,
        "text": "用途: 参加者が大きな負荷や集中を感じる厳しい訓練を表す。  "
      },
      {
        "line": 193,
        "text": "例: The athletes completed an intense training camp before the tournament.  "
      },
      {
        "line": 194,
        "text": "訳: 選手たちは大会前に厳しい合宿を終えた。  "
      },
      {
        "line": 258,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 268,
        "text": "【コロケーション】"
      },
      {
        "line": 270,
        "text": "・an intense look  "
      },
      {
        "line": 271,
        "text": "用途: 強い感情や集中を帯びた視線・表情を表す。  "
      },
      {
        "line": 272,
        "text": "例: She gave him an intense look when he mentioned the accusation.  "
      },
      {
        "line": 273,
        "text": "訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  "
      },
      {
        "line": 275,
        "text": "・an intense person  "
      },
      {
        "line": 276,
        "text": "用途: 感情、意見、目的意識などが強く、存在感や圧のある人を表す。  "
      },
      {
        "line": 277,
        "text": "例: He is an intense person who takes every project very seriously.  "
      },
      {
        "line": 278,
        "text": "訳: 彼はどのプロジェクトにも非常に真剣に取り組む、熱の強い人だ。  "
      },
      {
        "line": 280,
        "text": "・be intense about 〈事柄〉  "
      },
      {
        "line": 281,
        "text": "用途: ある事柄について強い意見や熱意を持ち、真剣にこだわることを表す。  "
      },
      {
        "line": 282,
        "text": "例: She is intense about keeping every detail of the experiment accurate.  "
      },
      {
        "line": 283,
        "text": "訳: 彼女は実験の細部をすべて正確に保つことに非常にこだわっている。  "
      },
      {
        "line": 285,
        "text": "・an intense conversation  "
      },
      {
        "line": 286,
        "text": "用途: 強い感情や重大な問題を伴う真剣な会話を表す。  "
      },
      {
        "line": 287,
        "text": "例: We had an intense conversation about whether to end the relationship.  "
      },
      {
        "line": 288,
        "text": "訳: 私たちはその関係を終わらせるべきかについて、感情のこもった真剣な話をした。  "
      },
      {
        "line": 290,
        "text": "・an intense relationship  "
      },
      {
        "line": 291,
        "text": "用途: 感情的な結びつきや相互作用が非常に強い関係を表す。  "
      },
      {
        "line": 292,
        "text": "例: Their intense relationship left little room for emotional distance.  "
      },
      {
        "line": 293,
        "text": "訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  "
      },
      {
        "line": 295,
        "text": "・too intense  "
      },
      {
        "line": 296,
        "text": "用途: 人、会話、関係などが重すぎたり、圧が強すぎたりすることを表す。  "
      },
      {
        "line": 297,
        "text": "例: The first meeting felt too intense for a casual introduction.  "
      },
      {
        "line": 298,
        "text": "訳: 最初の会合は、気軽な顔合わせにしては重すぎる感じがした。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 87,
        "text": "【類義語】"
      },
      {
        "line": 89,
        "text": "・strong  "
      },
      {
        "line": 90,
        "text": "定義: 力、程度、効果などが大きい。  "
      },
      {
        "line": 91,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 92,
        "text": "違い: strong は最も広い「強い」で、intense は感覚・感情・圧力などが極端で、張り詰めた感じを伴いやすい。  "
      },
      {
        "line": 93,
        "text": "例: The coffee has a strong flavor.  "
      },
      {
        "line": 94,
        "text": "訳: そのコーヒーは味が濃い。  "
      },
      {
        "line": 96,
        "text": "・extreme  "
      },
      {
        "line": 97,
        "text": "定義: 普通の範囲を超え、極端な。  "
      },
      {
        "line": 98,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 99,
        "text": "違い: extreme は程度が限界に近いことに焦点があり、intense のような体感的な圧や集中を必ずしも含まない。  "
      },
      {
        "line": 100,
        "text": "例: The region experienced extreme temperatures last summer.  "
      },
      {
        "line": 101,
        "text": "訳: その地域は昨夏、極端な気温に見舞われた。  "
      },
      {
        "line": 103,
        "text": "・severe  "
      },
      {
        "line": 104,
        "text": "定義: 被害、痛み、問題などが深刻で重い。  "
      },
      {
        "line": 105,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 106,
        "text": "違い: severe は悪影響や深刻さに焦点があり、intense は好ましい感情や色など、害のない強さにも使える。  "
      },
      {
        "line": 107,
        "text": "例: The storm caused severe damage to the coast.  "
      },
      {
        "line": 108,
        "text": "訳: その嵐は沿岸部に深刻な被害をもたらした。  "
      },
      {
        "line": 110,
        "text": "・powerful  "
      },
      {
        "line": 111,
        "text": "定義: 大きな力や効果を持つ。  "
      },
      {
        "line": 112,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 113,
        "text": "違い: powerful は作用する力・影響力に焦点があり、intense は経験される強度や圧に焦点がある。  "
      },
      {
        "line": 114,
        "text": "例: The film presents a powerful image of life after the disaster.  "
      },
      {
        "line": 115,
        "text": "訳: その映画は災害後の生活を力強い映像で描いている。  "
      },
      {
        "line": 117,
        "text": "・acute  "
      },
      {
        "line": 118,
        "text": "定義: 痛み、問題、感覚などが激しく、差し迫っている。  "
      },
      {
        "line": 119,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 120,
        "text": "違い: acute は特に痛み・不足・問題などの鋭さや深刻さを表す硬い語で、intense より対象が限定されやすい。  "
      },
      {
        "line": 121,
        "text": "例: The shortage created an acute need for clean water.  "
      },
      {
        "line": 122,
        "text": "訳: その不足により、きれいな水が緊急に必要になった。  "
      },
      {
        "line": 124,
        "text": "・vivid  "
      },
      {
        "line": 125,
        "text": "定義: 色、記憶、描写などが鮮明で強く印象に残る。  "
      },
      {
        "line": 126,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 127,
        "text": "違い: vivid は目立つ鮮明さや心に浮かぶ明瞭さに焦点があり、intense のように圧力や痛みの強さ全般を表さない。  "
      },
      {
        "line": 128,
        "text": "例: She has a vivid memory of the accident.  "
      },
      {
        "line": 129,
        "text": "訳: 彼女はその事故を鮮明に覚えている。  "
      },
      {
        "line": 131,
        "text": "【反意語】"
      },
      {
        "line": 133,
        "text": "・mild  "
      },
      {
        "line": 134,
        "text": "定義: 程度が穏やかで、強すぎない。  "
      },
      {
        "line": 135,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 136,
        "text": "違い: mild は痛み、症状、天候、反応などの程度が低く穏やかなことを表し、intense と程度の軸で対立する。  "
      },
      {
        "line": 137,
        "text": "例: She had only mild pain after the treatment.  "
      },
      {
        "line": 138,
        "text": "訳: 治療後の痛みは軽いものだった。  "
      },
      {
        "line": 140,
        "text": "・weak  "
      },
      {
        "line": 141,
        "text": "定義: 力、効果、信号などが弱い。  "
      },
      {
        "line": 142,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 143,
        "text": "違い: weak は強さや作用が不足していることを表し、intense の極端な強さと反対方向にある。  "
      },
      {
        "line": 144,
        "text": "例: The radio signal was too weak to hear clearly.  "
      },
      {
        "line": 145,
        "text": "訳: その無線信号は弱すぎて、はっきり聞こえなかった。  "
      },
      {
        "line": 147,
        "text": "・faint  "
      },
      {
        "line": 148,
        "text": "定義: 光、音、色、においなどがかすかな。  "
      },
      {
        "line": 149,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 150,
        "text": "違い: faint は感覚刺激がほとんど感じ取れないほど弱いことに焦点があり、intense と特に光・色・音の強さで対立する。  "
      },
      {
        "line": 151,
        "text": "例: A faint light was visible through the fog.  "
      },
      {
        "line": 152,
        "text": "訳: 霧の中にかすかな光が見えた。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 198,
        "text": "【類義語】"
      },
      {
        "line": 200,
        "text": "・fierce  "
      },
      {
        "line": 201,
        "text": "定義: 競争、対立、議論などが非常に激しい。  "
      },
      {
        "line": 202,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 203,
        "text": "違い: fierce は攻撃性・対立・荒々しさを含みやすく、intense は敵意のない努力や活動の集中にも使える。  "
      },
      {
        "line": 204,
        "text": "例: The teams are in fierce competition for the championship.  "
      },
      {
        "line": 205,
        "text": "訳: そのチームたちは優勝をめぐって激しく競い合っている。  "
      },
      {
        "line": 207,
        "text": "・vigorous  "
      },
      {
        "line": 208,
        "text": "定義: 活動や努力が精力的で力強い。  "
      },
      {
        "line": 209,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 210,
        "text": "違い: vigorous は活力や積極的なエネルギーに焦点があり、intense のような緊張・負荷・心理的圧力を必ずしも含まない。  "
      },
      {
        "line": 211,
        "text": "例: The proposal prompted vigorous discussion among the experts.  "
      },
      {
        "line": 212,
        "text": "訳: その提案は専門家の間で活発な議論を促した。  "
      },
      {
        "line": 214,
        "text": "・strenuous  "
      },
      {
        "line": 215,
        "text": "定義: 身体的・精神的に大きな努力を要する。  "
      },
      {
        "line": 216,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 217,
        "text": "違い: strenuous は行為がきつく、多大な努力を要することに焦点があり、intense は活動の集中度や緊張感も表す。  "
      },
      {
        "line": 218,
        "text": "例: The climbers faced a strenuous ascent in freezing weather.  "
      },
      {
        "line": 219,
        "text": "訳: 登山者たちは極寒の中で厳しい登りに挑んだ。  "
      },
      {
        "line": 221,
        "text": "・hectic  "
      },
      {
        "line": 222,
        "text": "定義: 活動や予定が非常に多く、慌ただしい。  "
      },
      {
        "line": 223,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 224,
        "text": "違い: hectic は忙しさや混乱を含む時間の状態に焦点があり、intense のように競争・感情・議論の強さ全般を表さない。  "
      },
      {
        "line": 225,
        "text": "例: It was a hectic week at the hospital.  "
      },
      {
        "line": 226,
        "text": "訳: 病院では慌ただしい一週間だった。  "
      },
      {
        "line": 228,
        "text": "・concentrated  "
      },
      {
        "line": 229,
        "text": "定義: 力、資源、活動などが一箇所や短期間に集中的に向けられた。  "
      },
      {
        "line": 230,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 231,
        "text": "違い: concentrated は分散していない配置や客観的な集中に焦点があり、intense のような体感的な激しさを必ずしも含まない。  "
      },
      {
        "line": 232,
        "text": "例: The program provides concentrated language practice over two weeks.  "
      },
      {
        "line": 233,
        "text": "訳: そのプログラムは2週間にわたり集中的な語学練習を提供する。  "
      },
      {
        "line": 235,
        "text": "・demanding  "
      },
      {
        "line": 236,
        "text": "定義: 多くの時間、技術、努力を要求する。  "
      },
      {
        "line": 237,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 238,
        "text": "違い: demanding は参加者にとって負担が大きいことに焦点があり、活動自体の対立や感情の強さまでは示さない。  "
      },
      {
        "line": 239,
        "text": "例: The job is demanding but rewarding.  "
      },
      {
        "line": 240,
        "text": "訳: その仕事は大変だが、やりがいがある。  "
      },
      {
        "line": 242,
        "text": "【反意語】"
      },
      {
        "line": 244,
        "text": "・moderate  "
      },
      {
        "line": 245,
        "text": "定義: 程度や強さが中程度の。  "
      },
      {
        "line": 246,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 247,
        "text": "違い: moderate は活動、負荷、競争などが極端ではないことを表し、intense と程度の軸で対立する。  "
      },
      {
        "line": 248,
        "text": "例: Start with moderate exercise and increase the load gradually.  "
      },
      {
        "line": 249,
        "text": "訳: 中程度の運動から始め、負荷を徐々に増やしなさい。  "
      },
      {
        "line": 251,
        "text": "・light  "
      },
      {
        "line": 252,
        "text": "定義: 仕事、運動、訓練などの負荷が小さい。  "
      },
      {
        "line": 253,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 254,
        "text": "違い: light は特に作業量や身体的負荷が少ないことを表し、intense の高い負荷と対立する。  "
      },
      {
        "line": 255,
        "text": "例: The doctor recommended light exercise for the first week.  "
      },
      {
        "line": 256,
        "text": "訳: 医師は最初の1週間、軽い運動を勧めた。  "
      },
      {
        "line": 258,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 302,
        "text": "【類義語】"
      },
      {
        "line": 304,
        "text": "・serious  "
      },
      {
        "line": 305,
        "text": "定義: ふざけておらず、真剣な、または重大な。  "
      },
      {
        "line": 306,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 307,
        "text": "違い: serious は真面目さや重要性に焦点があり、intense のような強い感情の圧や相手に与える重さを必ずしも含まない。  "
      },
      {
        "line": 308,
        "text": "例: She looked serious during the interview.  "
      },
      {
        "line": 309,
        "text": "訳: 面接中、彼女は真剣な表情をしていた。  "
      },
      {
        "line": 311,
        "text": "・passionate  "
      },
      {
        "line": 312,
        "text": "定義: 人や活動に強い熱意・愛着を持つ。  "
      },
      {
        "line": 313,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 314,
        "text": "違い: passionate は熱意や好意を示す肯定的な語で、intense のように緊張感や重い圧を含むとは限らない。  "
      },
      {
        "line": 315,
        "text": "例: He is passionate about improving access to education.  "
      },
      {
        "line": 316,
        "text": "訳: 彼は教育へのアクセス改善に情熱を注いでいる。  "
      },
      {
        "line": 318,
        "text": "・earnest  "
      },
      {
        "line": 319,
        "text": "定義: 目的や発言が誠実で、真剣な。  "
      },
      {
        "line": 320,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 321,
        "text": "違い: earnest は誠実さ・真摯さに焦点があり、intense より感情の強さや対人的な圧が弱い。  "
      },
      {
        "line": 322,
        "text": "例: She made an earnest appeal for help.  "
      },
      {
        "line": 323,
        "text": "訳: 彼女は助けを求めて真摯に訴えた。  "
      },
      {
        "line": 325,
        "text": "・focused  "
      },
      {
        "line": 326,
        "text": "定義: 注意や努力の対象が明確で、集中している。  "
      },
      {
        "line": 327,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 328,
        "text": "違い: focused は注意が一点に定まっていることを表す中立的な語で、intense のような強い感情や重い雰囲気を必ずしも含まない。  "
      },
      {
        "line": 329,
        "text": "例: The researcher remained focused on the data.  "
      },
      {
        "line": 330,
        "text": "訳: その研究者はデータに集中し続けた。  "
      },
      {
        "line": 332,
        "text": "・emotional  "
      },
      {
        "line": 333,
        "text": "定義: 強い感情を示す、感情に動かされた。  "
      },
      {
        "line": 334,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 335,
        "text": "違い: emotional は感情が表に出ていることに焦点があり、intense のような強い目的意識や集中だけを表す場合には使えない。  "
      },
      {
        "line": 336,
        "text": "例: His speech was emotional but carefully reasoned.  "
      },
      {
        "line": 337,
        "text": "訳: 彼のスピーチは感情的だったが、論理的によく考えられていた。  "
      },
      {
        "line": 339,
        "text": "・forceful  "
      },
      {
        "line": 340,
        "text": "定義: 意見、表現、態度などが力強く、強い影響を与える。  "
      },
      {
        "line": 341,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 342,
        "text": "違い: forceful は外に表れた主張や表現の押し出しに焦点があり、intense の内面的な感情の深さまで含むとは限らない。  "
      },
      {
        "line": 343,
        "text": "例: The lawyer gave a forceful argument in court.  "
      },
      {
        "line": 344,
        "text": "訳: その弁護士は法廷で力強い主張を展開した。  "
      },
      {
        "line": 346,
        "text": "【反意語】"
      },
      {
        "line": 348,
        "text": "・casual  "
      },
      {
        "line": 349,
        "text": "定義: 態度、会話、関係などが気軽で、形式張らない。  "
      },
      {
        "line": 350,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 351,
        "text": "違い: casual は深い感情的関与や張り詰めた圧が少ないことを表し、intense と対人的な雰囲気の軸で対立する。  "
      },
      {
        "line": 352,
        "text": "例: We had a casual conversation over coffee.  "
      },
      {
        "line": 353,
        "text": "訳: 私たちはコーヒーを飲みながら気軽な会話をした。  "
      },
      {
        "line": 355,
        "text": "・relaxed  "
      },
      {
        "line": 356,
        "text": "定義: 緊張や気負いがなく、落ち着いている。  "
      },
      {
        "line": 357,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 358,
        "text": "違い: relaxed は人、雰囲気、やり取りの力が抜けていることを表し、intense の張り詰めた圧と反対方向にある。  "
      },
      {
        "line": 359,
        "text": "例: The interview became more relaxed after the first few questions.  "
      },
      {
        "line": 360,
        "text": "訳: 最初の数問を過ぎると、面接はより和やかになった。  "
      },
      {
        "line": 362,
        "text": "・detached  "
      },
      {
        "line": 363,
        "text": "定義: 感情的に関与せず、距離を置いた。  "
      },
      {
        "line": 364,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 365,
        "text": "違い: detached は感情や個人的な関与を抑えていることを表し、intense の強い感情的関与と対立する。  "
      },
      {
        "line": 366,
        "text": "例: He remained detached while discussing the breakup.  "
      },
      {
        "line": 367,
        "text": "訳: 彼は別れについて話している間も、感情的に距離を置いていた。  "
      }
    ],
    "antonym_axis_items": [
      {
        "item_id": "ant-464499db347e",
        "stage1_axis": {
          "item_id": "ant-464499db347e",
          "axis": "強度",
          "relation_type": "程度",
          "reason": "対象の極端な強さと、穏やかで強すぎない程度の対立。"
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 133,
          "line_end": 133,
          "exact_quote": "・mild  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 136,
          "line_end": 136,
          "exact_quote": "違い: mild は痛み、症状、天候、反応などの程度が低く穏やかなことを表し、intense と程度の軸で対立する。  "
        }
      },
      {
        "item_id": "ant-f114c7dc9bc6",
        "stage1_axis": {
          "item_id": "ant-f114c7dc9bc6",
          "axis": "強度",
          "relation_type": "程度",
          "reason": "感情や感覚などの力の大きさと、力や効果の弱さの対立。"
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 140,
          "line_end": 140,
          "exact_quote": "・weak  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 143,
          "line_end": 143,
          "exact_quote": "違い: weak は強さや作用が不足していることを表し、intense の極端な強さと反対方向にある。  "
        }
      },
      {
        "item_id": "ant-06d30634b64f",
        "stage1_axis": {
          "item_id": "ant-06d30634b64f",
          "axis": "強度",
          "relation_type": "程度",
          "reason": "光や音などの強さと、かすかな強さの対立。"
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 147,
          "line_end": 147,
          "exact_quote": "・faint  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 150,
          "line_end": 150,
          "exact_quote": "違い: faint は感覚刺激がほとんど感じ取れないほど弱いことに焦点があり、intense と特に光・色・音の強さで対立する。  "
        }
      },
      {
        "item_id": "ant-1a4b697f8e4b",
        "stage1_axis": {
          "item_id": "ant-1a4b697f8e4b",
          "axis": "強度",
          "relation_type": "程度",
          "reason": "活動に必要な力や注意の強さと、中程度の強さの対立。"
        },
        "sense_id": "sense:002",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 244,
          "line_end": 244,
          "exact_quote": "・moderate  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 247,
          "line_end": 247,
          "exact_quote": "違い: moderate は活動、負荷、競争などが極端ではないことを表し、intense と程度の軸で対立する。  "
        }
      },
      {
        "item_id": "ant-41690c7b43ad",
        "stage1_axis": {
          "item_id": "ant-41690c7b43ad",
          "axis": "負荷",
          "relation_type": "程度",
          "reason": "短時間に必要な力や注意の大きさと、仕事や運動の小さな負荷の対立。"
        },
        "sense_id": "sense:002",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 251,
          "line_end": 251,
          "exact_quote": "・light  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 254,
          "line_end": 254,
          "exact_quote": "違い: light は特に作業量や身体的負荷が少ないことを表し、intense の高い負荷と対立する。  "
        }
      },
      {
        "item_id": "ant-80779d1bfcd6",
        "stage1_axis": {
          "item_id": "ant-80779d1bfcd6",
          "axis": "真剣さ",
          "relation_type": "状態",
          "reason": "真剣で集中した態度と、気軽で形式張らない態度の対立。"
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 348,
          "line_end": 348,
          "exact_quote": "・casual  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 351,
          "line_end": 351,
          "exact_quote": "違い: casual は深い感情的関与や張り詰めた圧が少ないことを表し、intense と対人的な雰囲気の軸で対立する。  "
        }
      },
      {
        "item_id": "ant-f870f7405e53",
        "stage1_axis": {
          "item_id": "ant-f870f7405e53",
          "axis": "緊張",
          "relation_type": "状態",
          "reason": "重く圧のある集中状態と、緊張や気負いのない落ち着いた状態の対立。"
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 355,
          "line_end": 355,
          "exact_quote": "・relaxed  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 358,
          "line_end": 358,
          "exact_quote": "違い: relaxed は人、雰囲気、やり取りの力が抜けていることを表し、intense の張り詰めた圧と反対方向にある。  "
        }
      },
      {
        "item_id": "ant-af2cb1b9bd23",
        "stage1_axis": {
          "item_id": "ant-af2cb1b9bd23",
          "axis": "関与",
          "relation_type": "状態",
          "reason": "強い感情や目的意識の示し方と、感情的に距離を置くことの対立。"
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 362,
          "line_end": 362,
          "exact_quote": "・detached  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 365,
          "line_end": 365,
          "exact_quote": "違い: detached は感情や個人的な関与を抑えていることを表し、intense の強い感情的関与と対立する。  "
        }
      }
    ],
    "antonym_axis_senses": [
      {
        "sense_id": "sense:001",
        "full_sense": [
          {
            "line": 43,
            "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、光、色、関心、圧力などの程度が極端に強いこと。単に「強い」というより、対象にかかる力や感じられる圧が大きいことを表す。必ず不快・否定的とは限らず、intense pleasure「非常に強い喜び」のように好ましい対象にも使う。  "
          },
          {
            "line": 47,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 49,
            "text": "【レジスター/領域】標準的な一般語。会話、ニュース、ビジネス、医学、スポーツ、文学などで広く使う。  "
          },
          {
            "line": 51,
            "text": "【文法パターン】intense + 〈感情・感覚・性質を表す名詞〉＝非常に強い～／become/get/feel intense＝程度や感じ方が強くなる／under intense pressure/scrutiny＝強い圧力・厳しい監視の下で／intense + 〈色・光・熱など〉＝非常に鮮やかな・強烈な～  "
          },
          {
            "line": 53,
            "text": "【コロケーション】"
          },
          {
            "line": 55,
            "text": "・intense pain  "
          },
          {
            "line": 56,
            "text": "用途: 身体的な痛みが非常に強いことを表す。  "
          },
          {
            "line": 57,
            "text": "例: He felt intense pain in his lower back.  "
          },
          {
            "line": 58,
            "text": "訳: 彼は腰の下部に激しい痛みを感じた。  "
          },
          {
            "line": 60,
            "text": "・intense heat  "
          },
          {
            "line": 61,
            "text": "用途: 暑さや熱が極端に強いことを表す。  "
          },
          {
            "line": 62,
            "text": "例: The intense heat made it dangerous to work outside.  "
          },
          {
            "line": 63,
            "text": "訳: 強烈な暑さのため、屋外で働くのは危険だった。  "
          },
          {
            "line": 65,
            "text": "・intense pressure  "
          },
          {
            "line": 66,
            "text": "用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  "
          },
          {
            "line": 67,
            "text": "例: The new manager is under intense pressure to improve the results.  "
          },
          {
            "line": 68,
            "text": "訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  "
          },
          {
            "line": 70,
            "text": "・intense interest  "
          },
          {
            "line": 71,
            "text": "用途: ある対象に向けられる関心が非常に強いことを表す。  "
          },
          {
            "line": 72,
            "text": "例: The discovery attracted intense interest from researchers around the world.  "
          },
          {
            "line": 73,
            "text": "訳: その発見は世界中の研究者から強い関心を集めた。  "
          },
          {
            "line": 75,
            "text": "・intense anger  "
          },
          {
            "line": 76,
            "text": "用途: 怒りの感情が非常に強いことを表す。  "
          },
          {
            "line": 77,
            "text": "例: The decision provoked intense anger among local residents.  "
          },
          {
            "line": 78,
            "text": "訳: その決定は地元住民の激しい怒りを引き起こした。  "
          },
          {
            "line": 80,
            "text": "・intense blue  "
          },
          {
            "line": 81,
            "text": "用途: 色が非常に鮮やかで、見る人に強い印象を与えることを表す。  "
          },
          {
            "line": 82,
            "text": "例: The intense blue of the lake stood out against the white snow.  "
          },
          {
            "line": 83,
            "text": "訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  "
          },
          {
            "line": 85,
            "text": "【語法・注意】intense は程度の高さを表す形容詞で、対象が大きいことや量が多いことを表す語ではない。たとえば「雨が大量に降る」は heavy rain、「色が鮮やかで強い」は intense color のように、対象に応じて自然な語を選ぶ。intense pain/heat/interest のように、身体感覚・環境・感情のいずれにも使えるが、強さの対象を文脈から明確にする。  "
          },
          {
            "line": 87,
            "text": "【類義語】"
          },
          {
            "line": 89,
            "text": "・strong  "
          },
          {
            "line": 90,
            "text": "定義: 力、程度、効果などが大きい。  "
          },
          {
            "line": 91,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 92,
            "text": "違い: strong は最も広い「強い」で、intense は感覚・感情・圧力などが極端で、張り詰めた感じを伴いやすい。  "
          },
          {
            "line": 93,
            "text": "例: The coffee has a strong flavor.  "
          },
          {
            "line": 94,
            "text": "訳: そのコーヒーは味が濃い。  "
          },
          {
            "line": 96,
            "text": "・extreme  "
          },
          {
            "line": 97,
            "text": "定義: 普通の範囲を超え、極端な。  "
          },
          {
            "line": 98,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 99,
            "text": "違い: extreme は程度が限界に近いことに焦点があり、intense のような体感的な圧や集中を必ずしも含まない。  "
          },
          {
            "line": 100,
            "text": "例: The region experienced extreme temperatures last summer.  "
          },
          {
            "line": 101,
            "text": "訳: その地域は昨夏、極端な気温に見舞われた。  "
          },
          {
            "line": 103,
            "text": "・severe  "
          },
          {
            "line": 104,
            "text": "定義: 被害、痛み、問題などが深刻で重い。  "
          },
          {
            "line": 105,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 106,
            "text": "違い: severe は悪影響や深刻さに焦点があり、intense は好ましい感情や色など、害のない強さにも使える。  "
          },
          {
            "line": 107,
            "text": "例: The storm caused severe damage to the coast.  "
          },
          {
            "line": 108,
            "text": "訳: その嵐は沿岸部に深刻な被害をもたらした。  "
          },
          {
            "line": 110,
            "text": "・powerful  "
          },
          {
            "line": 111,
            "text": "定義: 大きな力や効果を持つ。  "
          },
          {
            "line": 112,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 113,
            "text": "違い: powerful は作用する力・影響力に焦点があり、intense は経験される強度や圧に焦点がある。  "
          },
          {
            "line": 114,
            "text": "例: The film presents a powerful image of life after the disaster.  "
          },
          {
            "line": 115,
            "text": "訳: その映画は災害後の生活を力強い映像で描いている。  "
          },
          {
            "line": 117,
            "text": "・acute  "
          },
          {
            "line": 118,
            "text": "定義: 痛み、問題、感覚などが激しく、差し迫っている。  "
          },
          {
            "line": 119,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 120,
            "text": "違い: acute は特に痛み・不足・問題などの鋭さや深刻さを表す硬い語で、intense より対象が限定されやすい。  "
          },
          {
            "line": 121,
            "text": "例: The shortage created an acute need for clean water.  "
          },
          {
            "line": 122,
            "text": "訳: その不足により、きれいな水が緊急に必要になった。  "
          },
          {
            "line": 124,
            "text": "・vivid  "
          },
          {
            "line": 125,
            "text": "定義: 色、記憶、描写などが鮮明で強く印象に残る。  "
          },
          {
            "line": 126,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 127,
            "text": "違い: vivid は目立つ鮮明さや心に浮かぶ明瞭さに焦点があり、intense のように圧力や痛みの強さ全般を表さない。  "
          },
          {
            "line": 128,
            "text": "例: She has a vivid memory of the accident.  "
          },
          {
            "line": 129,
            "text": "訳: 彼女はその事故を鮮明に覚えている。  "
          },
          {
            "line": 131,
            "text": "【反意語】"
          },
          {
            "line": 133,
            "text": "・mild  "
          },
          {
            "line": 134,
            "text": "定義: 程度が穏やかで、強すぎない。  "
          },
          {
            "line": 135,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 136,
            "text": "違い: mild は痛み、症状、天候、反応などの程度が低く穏やかなことを表し、intense と程度の軸で対立する。  "
          },
          {
            "line": 137,
            "text": "例: She had only mild pain after the treatment.  "
          },
          {
            "line": 138,
            "text": "訳: 治療後の痛みは軽いものだった。  "
          },
          {
            "line": 140,
            "text": "・weak  "
          },
          {
            "line": 141,
            "text": "定義: 力、効果、信号などが弱い。  "
          },
          {
            "line": 142,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 143,
            "text": "違い: weak は強さや作用が不足していることを表し、intense の極端な強さと反対方向にある。  "
          },
          {
            "line": 144,
            "text": "例: The radio signal was too weak to hear clearly.  "
          },
          {
            "line": 145,
            "text": "訳: その無線信号は弱すぎて、はっきり聞こえなかった。  "
          },
          {
            "line": 147,
            "text": "・faint  "
          },
          {
            "line": 148,
            "text": "定義: 光、音、色、においなどがかすかな。  "
          },
          {
            "line": 149,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 150,
            "text": "違い: faint は感覚刺激がほとんど感じ取れないほど弱いことに焦点があり、intense と特に光・色・音の強さで対立する。  "
          },
          {
            "line": 151,
            "text": "例: A faint light was visible through the fog.  "
          },
          {
            "line": 152,
            "text": "訳: 霧の中にかすかな光が見えた。  "
          }
        ]
      },
      {
        "sense_id": "sense:002",
        "full_sense": [
          {
            "line": 154,
            "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
          },
          {
            "line": 156,
            "text": "【日本語訳・定義】活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。対象の客観的な密度だけでなく、それに参加・直面する人が感じる圧や負荷を表すことがある。  "
          },
          {
            "line": 158,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 160,
            "text": "【レジスター/領域】標準的な一般語。仕事、学習、スポーツ、政治、ニュースなどで広く使う。  "
          },
          {
            "line": 162,
            "text": "【文法パターン】intense + 〈活動・競争・議論・努力〉＝激しい・集中した～／an intense period of 〈活動〉＝激しい～の期間／become/get intense＝活動や状況が激しくなる／intense + 〈活動〉 over 〈期間〉＝一定期間に集中して行われる激しい～  "
          },
          {
            "line": 164,
            "text": "【コロケーション】"
          },
          {
            "line": 166,
            "text": "・intense competition  "
          },
          {
            "line": 167,
            "text": "用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。  "
          },
          {
            "line": 168,
            "text": "例: There is intense competition for places at the top universities.  "
          },
          {
            "line": 169,
            "text": "訳: 一流大学の枠をめぐって激しい競争がある。  "
          },
          {
            "line": 171,
            "text": "・intense debate  "
          },
          {
            "line": 172,
            "text": "用途: 議論が強い意見の対立や集中したやり取りを伴うことを表す。  "
          },
          {
            "line": 173,
            "text": "例: The proposal led to intense debate in parliament.  "
          },
          {
            "line": 174,
            "text": "訳: その提案は議会で激しい議論を引き起こした。  "
          },
          {
            "line": 176,
            "text": "・intense activity  "
          },
          {
            "line": 177,
            "text": "用途: 短期間に多くの活動が集中して行われることを表す。  "
          },
          {
            "line": 178,
            "text": "例: The airport experienced a period of intense activity before the holiday.  "
          },
          {
            "line": 179,
            "text": "訳: その空港では休暇前に活動が集中する時期があった。  "
          },
          {
            "line": 181,
            "text": "・intense effort  "
          },
          {
            "line": 182,
            "text": "用途: 目標達成のために大きな力と集中を注ぐ努力を表す。  "
          },
          {
            "line": 183,
            "text": "例: The rescue required intense effort from everyone on the team.  "
          },
          {
            "line": 184,
            "text": "訳: その救助にはチーム全員の大変な努力が必要だった。  "
          },
          {
            "line": 186,
            "text": "・intense negotiations  "
          },
          {
            "line": 187,
            "text": "用途: 短期間に意見を激しく交わし、妥結を目指す交渉を表す。  "
          },
          {
            "line": 188,
            "text": "例: The two sides held intense negotiations throughout the night.  "
          },
          {
            "line": 189,
            "text": "訳: 両陣営は一晩中、激しい交渉を続けた。  "
          },
          {
            "line": 191,
            "text": "・intense training  "
          },
          {
            "line": 192,
            "text": "用途: 参加者が大きな負荷や集中を感じる厳しい訓練を表す。  "
          },
          {
            "line": 193,
            "text": "例: The athletes completed an intense training camp before the tournament.  "
          },
          {
            "line": 194,
            "text": "訳: 選手たちは大会前に厳しい合宿を終えた。  "
          },
          {
            "line": 196,
            "text": "【語法・注意】intense と intensive は、どちらも短期間に多くの活動や努力が集中する対象を修飾できる。intense は参加者が感じる厳しさ・圧・感情的な強さを含みやすく、intensive は計画や内容の密度を客観的に述べやすい。したがって intense training は訓練の負荷の大きさ、an intensive training course は短期間に内容を詰め込む制度・課程の性質に焦点がある。ただし、この区別は絶対的ではない。  "
          },
          {
            "line": 198,
            "text": "【類義語】"
          },
          {
            "line": 200,
            "text": "・fierce  "
          },
          {
            "line": 201,
            "text": "定義: 競争、対立、議論などが非常に激しい。  "
          },
          {
            "line": 202,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 203,
            "text": "違い: fierce は攻撃性・対立・荒々しさを含みやすく、intense は敵意のない努力や活動の集中にも使える。  "
          },
          {
            "line": 204,
            "text": "例: The teams are in fierce competition for the championship.  "
          },
          {
            "line": 205,
            "text": "訳: そのチームたちは優勝をめぐって激しく競い合っている。  "
          },
          {
            "line": 207,
            "text": "・vigorous  "
          },
          {
            "line": 208,
            "text": "定義: 活動や努力が精力的で力強い。  "
          },
          {
            "line": 209,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 210,
            "text": "違い: vigorous は活力や積極的なエネルギーに焦点があり、intense のような緊張・負荷・心理的圧力を必ずしも含まない。  "
          },
          {
            "line": 211,
            "text": "例: The proposal prompted vigorous discussion among the experts.  "
          },
          {
            "line": 212,
            "text": "訳: その提案は専門家の間で活発な議論を促した。  "
          },
          {
            "line": 214,
            "text": "・strenuous  "
          },
          {
            "line": 215,
            "text": "定義: 身体的・精神的に大きな努力を要する。  "
          },
          {
            "line": 216,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 217,
            "text": "違い: strenuous は行為がきつく、多大な努力を要することに焦点があり、intense は活動の集中度や緊張感も表す。  "
          },
          {
            "line": 218,
            "text": "例: The climbers faced a strenuous ascent in freezing weather.  "
          },
          {
            "line": 219,
            "text": "訳: 登山者たちは極寒の中で厳しい登りに挑んだ。  "
          },
          {
            "line": 221,
            "text": "・hectic  "
          },
          {
            "line": 222,
            "text": "定義: 活動や予定が非常に多く、慌ただしい。  "
          },
          {
            "line": 223,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 224,
            "text": "違い: hectic は忙しさや混乱を含む時間の状態に焦点があり、intense のように競争・感情・議論の強さ全般を表さない。  "
          },
          {
            "line": 225,
            "text": "例: It was a hectic week at the hospital.  "
          },
          {
            "line": 226,
            "text": "訳: 病院では慌ただしい一週間だった。  "
          },
          {
            "line": 228,
            "text": "・concentrated  "
          },
          {
            "line": 229,
            "text": "定義: 力、資源、活動などが一箇所や短期間に集中的に向けられた。  "
          },
          {
            "line": 230,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 231,
            "text": "違い: concentrated は分散していない配置や客観的な集中に焦点があり、intense のような体感的な激しさを必ずしも含まない。  "
          },
          {
            "line": 232,
            "text": "例: The program provides concentrated language practice over two weeks.  "
          },
          {
            "line": 233,
            "text": "訳: そのプログラムは2週間にわたり集中的な語学練習を提供する。  "
          },
          {
            "line": 235,
            "text": "・demanding  "
          },
          {
            "line": 236,
            "text": "定義: 多くの時間、技術、努力を要求する。  "
          },
          {
            "line": 237,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 238,
            "text": "違い: demanding は参加者にとって負担が大きいことに焦点があり、活動自体の対立や感情の強さまでは示さない。  "
          },
          {
            "line": 239,
            "text": "例: The job is demanding but rewarding.  "
          },
          {
            "line": 240,
            "text": "訳: その仕事は大変だが、やりがいがある。  "
          },
          {
            "line": 242,
            "text": "【反意語】"
          },
          {
            "line": 244,
            "text": "・moderate  "
          },
          {
            "line": 245,
            "text": "定義: 程度や強さが中程度の。  "
          },
          {
            "line": 246,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 247,
            "text": "違い: moderate は活動、負荷、競争などが極端ではないことを表し、intense と程度の軸で対立する。  "
          },
          {
            "line": 248,
            "text": "例: Start with moderate exercise and increase the load gradually.  "
          },
          {
            "line": 249,
            "text": "訳: 中程度の運動から始め、負荷を徐々に増やしなさい。  "
          },
          {
            "line": 251,
            "text": "・light  "
          },
          {
            "line": 252,
            "text": "定義: 仕事、運動、訓練などの負荷が小さい。  "
          },
          {
            "line": 253,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 254,
            "text": "違い: light は特に作業量や身体的負荷が少ないことを表し、intense の高い負荷と対立する。  "
          },
          {
            "line": 255,
            "text": "例: The doctor recommended light exercise for the first week.  "
          },
          {
            "line": 256,
            "text": "訳: 医師は最初の1週間、軽い運動を勧めた。  "
          }
        ]
      },
      {
        "sense_id": "sense:003",
        "full_sense": [
          {
            "line": 258,
            "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
          },
          {
            "line": 260,
            "text": "【日本語訳・定義】人、視線、表情、会話、関係などが、非常に強い感情、意見、考え、目的意識を示すこと。真剣で集中しているという肯定的な意味にも、重い・圧が強い・感情的に負担が大きいという否定的な評価にもなり得る。  "
          },
          {
            "line": 262,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 264,
            "text": "【レジスター/領域】標準的な一般語。人物描写、会話、職場、文学、映画・演劇の批評などで使う。  "
          },
          {
            "line": 266,
            "text": "【文法パターン】an intense person＝感情や目的意識の強い人／an intense look/gaze/expression＝強い感情や集中を帯びた視線・表情／an intense conversation/relationship＝感情的な圧や結びつきの強い会話・関係／be intense about 〈事柄〉＝〈事柄〉に非常に熱心・真剣である／too intense＝人ややり取りが重すぎる、圧が強すぎる  "
          },
          {
            "line": 268,
            "text": "【コロケーション】"
          },
          {
            "line": 270,
            "text": "・an intense look  "
          },
          {
            "line": 271,
            "text": "用途: 強い感情や集中を帯びた視線・表情を表す。  "
          },
          {
            "line": 272,
            "text": "例: She gave him an intense look when he mentioned the accusation.  "
          },
          {
            "line": 273,
            "text": "訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  "
          },
          {
            "line": 275,
            "text": "・an intense person  "
          },
          {
            "line": 276,
            "text": "用途: 感情、意見、目的意識などが強く、存在感や圧のある人を表す。  "
          },
          {
            "line": 277,
            "text": "例: He is an intense person who takes every project very seriously.  "
          },
          {
            "line": 278,
            "text": "訳: 彼はどのプロジェクトにも非常に真剣に取り組む、熱の強い人だ。  "
          },
          {
            "line": 280,
            "text": "・be intense about 〈事柄〉  "
          },
          {
            "line": 281,
            "text": "用途: ある事柄について強い意見や熱意を持ち、真剣にこだわることを表す。  "
          },
          {
            "line": 282,
            "text": "例: She is intense about keeping every detail of the experiment accurate.  "
          },
          {
            "line": 283,
            "text": "訳: 彼女は実験の細部をすべて正確に保つことに非常にこだわっている。  "
          },
          {
            "line": 285,
            "text": "・an intense conversation  "
          },
          {
            "line": 286,
            "text": "用途: 強い感情や重大な問題を伴う真剣な会話を表す。  "
          },
          {
            "line": 287,
            "text": "例: We had an intense conversation about whether to end the relationship.  "
          },
          {
            "line": 288,
            "text": "訳: 私たちはその関係を終わらせるべきかについて、感情のこもった真剣な話をした。  "
          },
          {
            "line": 290,
            "text": "・an intense relationship  "
          },
          {
            "line": 291,
            "text": "用途: 感情的な結びつきや相互作用が非常に強い関係を表す。  "
          },
          {
            "line": 292,
            "text": "例: Their intense relationship left little room for emotional distance.  "
          },
          {
            "line": 293,
            "text": "訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  "
          },
          {
            "line": 295,
            "text": "・too intense  "
          },
          {
            "line": 296,
            "text": "用途: 人、会話、関係などが重すぎたり、圧が強すぎたりすることを表す。  "
          },
          {
            "line": 297,
            "text": "例: The first meeting felt too intense for a casual introduction.  "
          },
          {
            "line": 298,
            "text": "訳: 最初の会合は、気軽な顔合わせにしては重すぎる感じがした。  "
          },
          {
            "line": 300,
            "text": "【語法・注意】人に intense を使う場合は、単に serious「真面目な」や focused「集中した」と同じではない。強い感情や意見が外に表れ、相手に強い存在感・圧力を感じさせる含みがある。褒め言葉として passionate「情熱的な」に近くなることもあれば、too intense のように「重い、付き合うのが大変」という評価になることもある。an intense look は必ず怒りを意味せず、強い集中や関心だけでも成立する。  "
          },
          {
            "line": 302,
            "text": "【類義語】"
          },
          {
            "line": 304,
            "text": "・serious  "
          },
          {
            "line": 305,
            "text": "定義: ふざけておらず、真剣な、または重大な。  "
          },
          {
            "line": 306,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 307,
            "text": "違い: serious は真面目さや重要性に焦点があり、intense のような強い感情の圧や相手に与える重さを必ずしも含まない。  "
          },
          {
            "line": 308,
            "text": "例: She looked serious during the interview.  "
          },
          {
            "line": 309,
            "text": "訳: 面接中、彼女は真剣な表情をしていた。  "
          },
          {
            "line": 311,
            "text": "・passionate  "
          },
          {
            "line": 312,
            "text": "定義: 人や活動に強い熱意・愛着を持つ。  "
          },
          {
            "line": 313,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 314,
            "text": "違い: passionate は熱意や好意を示す肯定的な語で、intense のように緊張感や重い圧を含むとは限らない。  "
          },
          {
            "line": 315,
            "text": "例: He is passionate about improving access to education.  "
          },
          {
            "line": 316,
            "text": "訳: 彼は教育へのアクセス改善に情熱を注いでいる。  "
          },
          {
            "line": 318,
            "text": "・earnest  "
          },
          {
            "line": 319,
            "text": "定義: 目的や発言が誠実で、真剣な。  "
          },
          {
            "line": 320,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 321,
            "text": "違い: earnest は誠実さ・真摯さに焦点があり、intense より感情の強さや対人的な圧が弱い。  "
          },
          {
            "line": 322,
            "text": "例: She made an earnest appeal for help.  "
          },
          {
            "line": 323,
            "text": "訳: 彼女は助けを求めて真摯に訴えた。  "
          },
          {
            "line": 325,
            "text": "・focused  "
          },
          {
            "line": 326,
            "text": "定義: 注意や努力の対象が明確で、集中している。  "
          },
          {
            "line": 327,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 328,
            "text": "違い: focused は注意が一点に定まっていることを表す中立的な語で、intense のような強い感情や重い雰囲気を必ずしも含まない。  "
          },
          {
            "line": 329,
            "text": "例: The researcher remained focused on the data.  "
          },
          {
            "line": 330,
            "text": "訳: その研究者はデータに集中し続けた。  "
          },
          {
            "line": 332,
            "text": "・emotional  "
          },
          {
            "line": 333,
            "text": "定義: 強い感情を示す、感情に動かされた。  "
          },
          {
            "line": 334,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 335,
            "text": "違い: emotional は感情が表に出ていることに焦点があり、intense のような強い目的意識や集中だけを表す場合には使えない。  "
          },
          {
            "line": 336,
            "text": "例: His speech was emotional but carefully reasoned.  "
          },
          {
            "line": 337,
            "text": "訳: 彼のスピーチは感情的だったが、論理的によく考えられていた。  "
          },
          {
            "line": 339,
            "text": "・forceful  "
          },
          {
            "line": 340,
            "text": "定義: 意見、表現、態度などが力強く、強い影響を与える。  "
          },
          {
            "line": 341,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 342,
            "text": "違い: forceful は外に表れた主張や表現の押し出しに焦点があり、intense の内面的な感情の深さまで含むとは限らない。  "
          },
          {
            "line": 343,
            "text": "例: The lawyer gave a forceful argument in court.  "
          },
          {
            "line": 344,
            "text": "訳: その弁護士は法廷で力強い主張を展開した。  "
          },
          {
            "line": 346,
            "text": "【反意語】"
          },
          {
            "line": 348,
            "text": "・casual  "
          },
          {
            "line": 349,
            "text": "定義: 態度、会話、関係などが気軽で、形式張らない。  "
          },
          {
            "line": 350,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 351,
            "text": "違い: casual は深い感情的関与や張り詰めた圧が少ないことを表し、intense と対人的な雰囲気の軸で対立する。  "
          },
          {
            "line": 352,
            "text": "例: We had a casual conversation over coffee.  "
          },
          {
            "line": 353,
            "text": "訳: 私たちはコーヒーを飲みながら気軽な会話をした。  "
          },
          {
            "line": 355,
            "text": "・relaxed  "
          },
          {
            "line": 356,
            "text": "定義: 緊張や気負いがなく、落ち着いている。  "
          },
          {
            "line": 357,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 358,
            "text": "違い: relaxed は人、雰囲気、やり取りの力が抜けていることを表し、intense の張り詰めた圧と反対方向にある。  "
          },
          {
            "line": 359,
            "text": "例: The interview became more relaxed after the first few questions.  "
          },
          {
            "line": 360,
            "text": "訳: 最初の数問を過ぎると、面接はより和やかになった。  "
          },
          {
            "line": 362,
            "text": "・detached  "
          },
          {
            "line": 363,
            "text": "定義: 感情的に関与せず、距離を置いた。  "
          },
          {
            "line": 364,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 365,
            "text": "違い: detached は感情や個人的な関与を抑えていることを表し、intense の強い感情的関与と対立する。  "
          },
          {
            "line": 366,
            "text": "例: He remained detached while discussing the breakup.  "
          },
          {
            "line": 367,
            "text": "訳: 彼は別れについて話している間も、感情的に距離を置いていた。  "
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
