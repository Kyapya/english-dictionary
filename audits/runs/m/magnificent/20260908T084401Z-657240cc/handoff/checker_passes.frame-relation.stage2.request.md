# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`/root/magnificent_word/check_frame`, declared_model=`gpt-5`.

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
  "input_body_sha256": "258c1b3a17708126df77cb8e5db1556a9e738d56dd4183d8ccca00569461cdb7",
  "blind_request_sha256": "24d50335cff6e225b21794df08d676967a9621c79eaf52c6cc09b182fa689ef6",
  "blind_record_sha256": "26ff9c12b3a53077a99a0fd3075b7b7a12b37d23a594a9dce91bd54d0ae0e7e8",
  "input_sections": {
    "sense_structure": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 30,
        "text": "【日本語訳・定義】建物、景色、部屋、衣装、動物などが、規模、美しさ、豪華さ、威厳によって見る人に強い感銘を与えることを表す。単に大きいだけでなく、目を見張るほど見事だという肯定的評価を含む。  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 115,
        "text": "【日本語訳・定義】成果、演技、仕事、行為、機会、出来事などの質や価値が非常に高く、強く称賛したくなることを表す。外見の壮麗さを必要とせず、能力、出来、効果、経験の満足度などを高く評価する。単独の `Magnificent!` は「見事だ」「すばらしい」という感嘆になる。  "
      }
    ],
    "frames": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 36,
        "text": "【文法パターン】`a magnificent + 〈建物・景色・物〉`＝壮麗な～／`〈建物・景色・物〉 + be/look/seem magnificent`＝～が壮麗である・壮麗に見える／`a magnificent view of 〈場所・景色〉`＝〈場所・景色〉のすばらしい眺め  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 121,
        "text": "【文法パターン】`a magnificent + 〈成果・演技・仕事・機会〉`＝すばらしい～／`〈成果・演技・仕事〉 + be/seem magnificent`＝～が見事である／`do/play/perform magnificently`＝見事に行う・演じる／`Magnificent!`＝見事だ・すばらしい  "
      }
    ],
    "collocations_examples": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 38,
        "text": "【コロケーション】"
      },
      {
        "line": 40,
        "text": "・`a magnificent building/palace`  "
      },
      {
        "line": 41,
        "text": "用途: 規模、美しさ、威厳によって強い印象を与える建築物を表す。  "
      },
      {
        "line": 42,
        "text": "例: The restored palace is a magnificent example of eighteenth-century architecture.  "
      },
      {
        "line": 43,
        "text": "訳: 修復されたその宮殿は、18世紀建築の壮麗な一例である。  "
      },
      {
        "line": 45,
        "text": "・`a magnificent view of 〈場所・景色〉`  "
      },
      {
        "line": 46,
        "text": "用途: 広がりや美しさが際立ち、見る人を感動させる眺めを表す。  "
      },
      {
        "line": 47,
        "text": "例: From the terrace, we had a magnificent view of the snow-covered mountains.  "
      },
      {
        "line": 48,
        "text": "訳: テラスからは、雪に覆われた山々のすばらしい眺めが広がっていた。  "
      },
      {
        "line": 50,
        "text": "・`a magnificent 〈animal/bird〉`  "
      },
      {
        "line": 51,
        "text": "用途: 動物の大きさ、美しさ、威厳のある姿を称賛する。  "
      },
      {
        "line": 52,
        "text": "例: A magnificent eagle circled above the valley.  "
      },
      {
        "line": 53,
        "text": "訳: 一羽の堂々たるワシが谷の上空を旋回していた。  "
      },
      {
        "line": 55,
        "text": "・`look magnificent in 〈服・色〉`  "
      },
      {
        "line": 56,
        "text": "用途: ある服装や色によって、人が非常に美しく堂々として見えることを表す。  "
      },
      {
        "line": 57,
        "text": "例: She looked magnificent in the deep blue gown.  "
      },
      {
        "line": 58,
        "text": "訳: 彼女は濃い青のドレスをまとい、実に華やかで堂々として見えた。  "
      },
      {
        "line": 60,
        "text": "・`a magnificent interior/display`  "
      },
      {
        "line": 61,
        "text": "用途: 室内装飾や展示が豪華で、視覚的に強い感銘を与えることを表す。  "
      },
      {
        "line": 62,
        "text": "例: Visitors stopped to admire the cathedral's magnificent interior.  "
      },
      {
        "line": 63,
        "text": "訳: 来訪者たちは足を止めて、その大聖堂の壮麗な内部を眺めた。  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 123,
        "text": "【コロケーション】"
      },
      {
        "line": 125,
        "text": "・`a magnificent achievement`  "
      },
      {
        "line": 126,
        "text": "用途: 困難さや規模を踏まえて、成果を非常に高く評価する。  "
      },
      {
        "line": 127,
        "text": "例: Completing the bridge ahead of schedule was a magnificent achievement.  "
      },
      {
        "line": 128,
        "text": "訳: 予定より早く橋を完成させたことは、見事な偉業だった。  "
      },
      {
        "line": 130,
        "text": "・`a magnificent performance`  "
      },
      {
        "line": 131,
        "text": "用途: 演技、演奏、競技などの出来が極めて優れていることを表す。  "
      },
      {
        "line": 132,
        "text": "例: The violinist gave a magnificent performance in the final movement.  "
      },
      {
        "line": 133,
        "text": "訳: そのバイオリニストは最終楽章で見事な演奏を披露した。  "
      },
      {
        "line": 135,
        "text": "・`do a magnificent job`  "
      },
      {
        "line": 136,
        "text": "用途: 人や組織が仕事を非常にうまく成し遂げたことを称賛する。  "
      },
      {
        "line": 137,
        "text": "例: The rescue team did a magnificent job under dangerous conditions.  "
      },
      {
        "line": 138,
        "text": "訳: 救助隊は危険な状況下で実に見事な働きをした。  "
      },
      {
        "line": 140,
        "text": "・`a magnificent opportunity`  "
      },
      {
        "line": 141,
        "text": "用途: 価値や可能性が非常に大きい機会を強く肯定的に評価する。  "
      },
      {
        "line": 142,
        "text": "例: The scholarship gave her a magnificent opportunity to study abroad.  "
      },
      {
        "line": 143,
        "text": "訳: その奨学金は、彼女に留学するすばらしい機会を与えた。  "
      },
      {
        "line": 145,
        "text": "・`feel magnificent`  "
      },
      {
        "line": 146,
        "text": "用途: 心身の調子が非常によく、気分がすばらしいことを表す。  "
      },
      {
        "line": 147,
        "text": "例: After a full night's sleep, I felt magnificent.  "
      },
      {
        "line": 148,
        "text": "訳: 一晩ぐっすり眠った後、私は最高の気分だった。  "
      },
      {
        "line": 150,
        "text": "・`Magnificent!`  "
      },
      {
        "line": 151,
        "text": "用途: 出来事、成果、演技などに対する強い称賛を単独で表す。  "
      },
      {
        "line": 152,
        "text": "例: “We finished the repairs.” “Magnificent! We can reopen tomorrow.”  "
      },
      {
        "line": 153,
        "text": "訳: 「修理が終わりました」「すばらしい！ 明日には再開できる」  "
      }
    ],
    "lexical_relations": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 67,
        "text": "【類義語】"
      },
      {
        "line": 69,
        "text": "・splendid  "
      },
      {
        "line": 70,
        "text": "定義: 見た目、質、成果などが非常にすばらしく、称賛に値する。  "
      },
      {
        "line": 71,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 72,
        "text": "違い: `splendid` は外観にも出来にも広く使える。`magnificent` は特に壮大さ、豪華さ、強い感銘を伴いやすい。  "
      },
      {
        "line": 73,
        "text": "例: The hall was decorated with splendid tapestries.  "
      },
      {
        "line": 74,
        "text": "訳: その広間は見事なタペストリーで飾られていた。  "
      },
      {
        "line": 76,
        "text": "・majestic  "
      },
      {
        "line": 77,
        "text": "定義: 王侯のような威厳や堂々とした壮大さを感じさせる。  "
      },
      {
        "line": 78,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 79,
        "text": "違い: `majestic` は威厳と堂々とした姿に焦点を置く。`magnificent` は威厳がなくても豪華さや美しさによる感銘を表せる。  "
      },
      {
        "line": 80,
        "text": "例: We watched the majestic mountains turn red at sunset.  "
      },
      {
        "line": 81,
        "text": "訳: 私たちは雄大な山々が夕日に赤く染まるのを眺めた。  "
      },
      {
        "line": 83,
        "text": "・grand  "
      },
      {
        "line": 84,
        "text": "定義: 規模、設計、外観が大きく立派で、重要さや格式を感じさせる。  "
      },
      {
        "line": 85,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 86,
        "text": "違い: `grand` は規模や格式を中心に表し、ときに誇張された大げささも含む。`magnificent` は話者の強い称賛をより直接に示す。  "
      },
      {
        "line": 87,
        "text": "例: A grand staircase led to the reception rooms.  "
      },
      {
        "line": 88,
        "text": "訳: 壮大な階段が応接室へと続いていた。  "
      },
      {
        "line": 90,
        "text": "・glorious  "
      },
      {
        "line": 91,
        "text": "定義: 美しさ、輝かしさ、喜ばしさによって非常にすばらしい。  "
      },
      {
        "line": 92,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 93,
        "text": "違い: `glorious` は光、色、天候などの輝かしさや、体験の喜びを表しやすい。`magnificent` は建物や景観の規模・威容にも強く結びつく。  "
      },
      {
        "line": 94,
        "text": "例: The garden was filled with glorious autumn colors.  "
      },
      {
        "line": 95,
        "text": "訳: 庭は見事な秋の色彩で満ちていた。  "
      },
      {
        "line": 97,
        "text": "【反意語】"
      },
      {
        "line": 99,
        "text": "・unimpressive  "
      },
      {
        "line": 100,
        "text": "定義: 特に感銘を与えず、目立った美点や迫力がない。  "
      },
      {
        "line": 101,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 102,
        "text": "違い: 見る人に与える印象の強さという軸で、`magnificent` が非常に強い肯定的な感銘を表すのに対し、`unimpressive` は感銘を与えないことを表す。  "
      },
      {
        "line": 103,
        "text": "例: The building's plain exterior was rather unimpressive.  "
      },
      {
        "line": 104,
        "text": "訳: その建物の簡素な外観は、あまり印象的ではなかった。  "
      },
      {
        "line": 106,
        "text": "・plain  "
      },
      {
        "line": 107,
        "text": "定義: 装飾や華やかさがなく、簡素な。  "
      },
      {
        "line": 108,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 109,
        "text": "違い: 豪華さ・華やかさという限定された軸で対照をなす。`plain` は必ずしも質が悪いという否定的評価を含まず、`magnificent` の全面的な反対語ではない。  "
      },
      {
        "line": 110,
        "text": "例: The chapel has a plain wooden interior.  "
      },
      {
        "line": 111,
        "text": "訳: その礼拝堂の内部は簡素な木造である。  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 157,
        "text": "【類義語】"
      },
      {
        "line": 159,
        "text": "・excellent  "
      },
      {
        "line": 160,
        "text": "定義: 質、能力、出来が非常に高い。  "
      },
      {
        "line": 161,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 162,
        "text": "違い: `excellent` は評価基準に照らして質が高いことを比較的中立に述べる。`magnificent` は話者の感動や熱烈な称賛を強く表す。  "
      },
      {
        "line": 163,
        "text": "例: She submitted an excellent final report.  "
      },
      {
        "line": 164,
        "text": "訳: 彼女は非常に優れた最終報告書を提出した。  "
      },
      {
        "line": 166,
        "text": "・superb  "
      },
      {
        "line": 167,
        "text": "定義: 質や出来が最高水準である。  "
      },
      {
        "line": 168,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 169,
        "text": "違い: `superb` は洗練された出来や卓越した質に焦点を置く。`magnificent` は質に加えて規模や感銘の大きさを含みやすい。  "
      },
      {
        "line": 170,
        "text": "例: The chef prepared a superb meal using local ingredients.  "
      },
      {
        "line": 171,
        "text": "訳: その料理人は地元の食材で最高の料理を用意した。  "
      },
      {
        "line": 173,
        "text": "・outstanding  "
      },
      {
        "line": 174,
        "text": "定義: 同種のものの中で際立って優れている。  "
      },
      {
        "line": 175,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 176,
        "text": "違い: `outstanding` は比較集団の中で抜きん出ていることを示す。`magnificent` は比較対象を明示せず、強い感銘を直接表せる。  "
      },
      {
        "line": 177,
        "text": "例: Her outstanding leadership kept the project on track.  "
      },
      {
        "line": 178,
        "text": "訳: 彼女の卓越した指導力によって、プロジェクトは予定どおり進んだ。  "
      },
      {
        "line": 180,
        "text": "・wonderful  "
      },
      {
        "line": 181,
        "text": "定義: 喜び、満足、感嘆をもたらすほどすばらしい。  "
      },
      {
        "line": 182,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 183,
        "text": "違い: `wonderful` は楽しい経験や好ましい人・物に日常的に使う。`magnificent` はより強く、堂々とした、または劇的な称賛を帯びやすい。  "
      },
      {
        "line": 184,
        "text": "例: We had a wonderful evening with old friends.  "
      },
      {
        "line": 185,
        "text": "訳: 私たちは旧友たちとすばらしい夜を過ごした。  "
      },
      {
        "line": 187,
        "text": "【反意語】"
      },
      {
        "line": 189,
        "text": "・mediocre  "
      },
      {
        "line": 190,
        "text": "定義: 質や能力が平凡で、特に優れていない。  "
      },
      {
        "line": 191,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 192,
        "text": "違い: 質の高さという軸で、`magnificent` が極めて高い評価を表すのに対し、`mediocre` は平均的で期待を満たさない評価を表す。  "
      },
      {
        "line": 193,
        "text": "例: The sequel received mediocre reviews from critics.  "
      },
      {
        "line": 194,
        "text": "訳: その続編は批評家から凡庸だという評価を受けた。  "
      },
      {
        "line": 196,
        "text": "・terrible  "
      },
      {
        "line": 197,
        "text": "定義: 質や出来が非常に悪い。  "
      },
      {
        "line": 198,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 199,
        "text": "違い: 質の評価という軸で、`terrible` は非常に低い側、`magnificent` は非常に高い側を表す。  "
      },
      {
        "line": 200,
        "text": "例: The team gave a terrible performance in the second half.  "
      },
      {
        "line": 201,
        "text": "訳: そのチームは後半にひどい出来のプレーをした。  "
      }
    ],
    "antonym_axis_items": [
      {
        "item_id": "ant-2a37f3ed9ae8",
        "stage1_axis": {
          "item_id": "ant-2a37f3ed9ae8",
          "axis": "感銘度",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 99,
          "line_end": 99,
          "exact_quote": "・unimpressive  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 102,
          "line_end": 102,
          "exact_quote": "違い: 見る人に与える印象の強さという軸で、`magnificent` が非常に強い肯定的な感銘を表すのに対し、`unimpressive` は感銘を与えないことを表す。  "
        }
      },
      {
        "item_id": "ant-5372ba08044e",
        "stage1_axis": {
          "item_id": "ant-5372ba08044e",
          "axis": "華美性",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 106,
          "line_end": 106,
          "exact_quote": "・plain  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 109,
          "line_end": 109,
          "exact_quote": "違い: 豪華さ・華やかさという限定された軸で対照をなす。`plain` は必ずしも質が悪いという否定的評価を含まず、`magnificent` の全面的な反対語ではない。  "
        }
      },
      {
        "item_id": "ant-f61ced8cd873",
        "stage1_axis": {
          "item_id": "ant-f61ced8cd873",
          "axis": "卓越性",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:002",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 189,
          "line_end": 189,
          "exact_quote": "・mediocre  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 192,
          "line_end": 192,
          "exact_quote": "違い: 質の高さという軸で、`magnificent` が極めて高い評価を表すのに対し、`mediocre` は平均的で期待を満たさない評価を表す。  "
        }
      },
      {
        "item_id": "ant-d110bb7bd5b1",
        "stage1_axis": {
          "item_id": "ant-d110bb7bd5b1",
          "axis": "品質",
          "relation_type": "評価",
          "reason": ""
        },
        "sense_id": "sense:002",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 196,
          "line_end": 196,
          "exact_quote": "・terrible  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 199,
          "line_end": 199,
          "exact_quote": "違い: 質の評価という軸で、`terrible` は非常に低い側、`magnificent` は非常に高い側を表す。  "
        }
      }
    ],
    "antonym_axis_senses": [
      {
        "sense_id": "sense:001",
        "full_sense": [
          {
            "line": 28,
            "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
          },
          {
            "line": 30,
            "text": "【日本語訳・定義】建物、景色、部屋、衣装、動物などが、規模、美しさ、豪華さ、威厳によって見る人に強い感銘を与えることを表す。単に大きいだけでなく、目を見張るほど見事だという肯定的評価を含む。  "
          },
          {
            "line": 32,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 34,
            "text": "【レジスター/領域】標準語。日常会話、旅行・芸術・建築の描写、報道、文学的な文章まで広く使う。`beautiful` より評価が強く、やや高揚した響きを持つことがある。  "
          },
          {
            "line": 36,
            "text": "【文法パターン】`a magnificent + 〈建物・景色・物〉`＝壮麗な～／`〈建物・景色・物〉 + be/look/seem magnificent`＝～が壮麗である・壮麗に見える／`a magnificent view of 〈場所・景色〉`＝〈場所・景色〉のすばらしい眺め  "
          },
          {
            "line": 38,
            "text": "【コロケーション】"
          },
          {
            "line": 40,
            "text": "・`a magnificent building/palace`  "
          },
          {
            "line": 41,
            "text": "用途: 規模、美しさ、威厳によって強い印象を与える建築物を表す。  "
          },
          {
            "line": 42,
            "text": "例: The restored palace is a magnificent example of eighteenth-century architecture.  "
          },
          {
            "line": 43,
            "text": "訳: 修復されたその宮殿は、18世紀建築の壮麗な一例である。  "
          },
          {
            "line": 45,
            "text": "・`a magnificent view of 〈場所・景色〉`  "
          },
          {
            "line": 46,
            "text": "用途: 広がりや美しさが際立ち、見る人を感動させる眺めを表す。  "
          },
          {
            "line": 47,
            "text": "例: From the terrace, we had a magnificent view of the snow-covered mountains.  "
          },
          {
            "line": 48,
            "text": "訳: テラスからは、雪に覆われた山々のすばらしい眺めが広がっていた。  "
          },
          {
            "line": 50,
            "text": "・`a magnificent 〈animal/bird〉`  "
          },
          {
            "line": 51,
            "text": "用途: 動物の大きさ、美しさ、威厳のある姿を称賛する。  "
          },
          {
            "line": 52,
            "text": "例: A magnificent eagle circled above the valley.  "
          },
          {
            "line": 53,
            "text": "訳: 一羽の堂々たるワシが谷の上空を旋回していた。  "
          },
          {
            "line": 55,
            "text": "・`look magnificent in 〈服・色〉`  "
          },
          {
            "line": 56,
            "text": "用途: ある服装や色によって、人が非常に美しく堂々として見えることを表す。  "
          },
          {
            "line": 57,
            "text": "例: She looked magnificent in the deep blue gown.  "
          },
          {
            "line": 58,
            "text": "訳: 彼女は濃い青のドレスをまとい、実に華やかで堂々として見えた。  "
          },
          {
            "line": 60,
            "text": "・`a magnificent interior/display`  "
          },
          {
            "line": 61,
            "text": "用途: 室内装飾や展示が豪華で、視覚的に強い感銘を与えることを表す。  "
          },
          {
            "line": 62,
            "text": "例: Visitors stopped to admire the cathedral's magnificent interior.  "
          },
          {
            "line": 63,
            "text": "訳: 来訪者たちは足を止めて、その大聖堂の壮麗な内部を眺めた。  "
          },
          {
            "line": 65,
            "text": "【語法・注意】`magnificent` は限定用法にも叙述用法にも使える。外観について使うと、「きれいな」だけでなく、規模、豪華さ、威厳などが生む強い感銘まで表す。人に使う場合、`She looks magnificent.` のように外見を称賛できるが、`a magnificent person` は文脈により語義2の人格・力量への高い評価にもなる。比較変化は文法上可能だが、通常は `more/most magnificent` を用い、絶対的な称賛として原級で使うことも多い。  "
          },
          {
            "line": 67,
            "text": "【類義語】"
          },
          {
            "line": 69,
            "text": "・splendid  "
          },
          {
            "line": 70,
            "text": "定義: 見た目、質、成果などが非常にすばらしく、称賛に値する。  "
          },
          {
            "line": 71,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 72,
            "text": "違い: `splendid` は外観にも出来にも広く使える。`magnificent` は特に壮大さ、豪華さ、強い感銘を伴いやすい。  "
          },
          {
            "line": 73,
            "text": "例: The hall was decorated with splendid tapestries.  "
          },
          {
            "line": 74,
            "text": "訳: その広間は見事なタペストリーで飾られていた。  "
          },
          {
            "line": 76,
            "text": "・majestic  "
          },
          {
            "line": 77,
            "text": "定義: 王侯のような威厳や堂々とした壮大さを感じさせる。  "
          },
          {
            "line": 78,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 79,
            "text": "違い: `majestic` は威厳と堂々とした姿に焦点を置く。`magnificent` は威厳がなくても豪華さや美しさによる感銘を表せる。  "
          },
          {
            "line": 80,
            "text": "例: We watched the majestic mountains turn red at sunset.  "
          },
          {
            "line": 81,
            "text": "訳: 私たちは雄大な山々が夕日に赤く染まるのを眺めた。  "
          },
          {
            "line": 83,
            "text": "・grand  "
          },
          {
            "line": 84,
            "text": "定義: 規模、設計、外観が大きく立派で、重要さや格式を感じさせる。  "
          },
          {
            "line": 85,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 86,
            "text": "違い: `grand` は規模や格式を中心に表し、ときに誇張された大げささも含む。`magnificent` は話者の強い称賛をより直接に示す。  "
          },
          {
            "line": 87,
            "text": "例: A grand staircase led to the reception rooms.  "
          },
          {
            "line": 88,
            "text": "訳: 壮大な階段が応接室へと続いていた。  "
          },
          {
            "line": 90,
            "text": "・glorious  "
          },
          {
            "line": 91,
            "text": "定義: 美しさ、輝かしさ、喜ばしさによって非常にすばらしい。  "
          },
          {
            "line": 92,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 93,
            "text": "違い: `glorious` は光、色、天候などの輝かしさや、体験の喜びを表しやすい。`magnificent` は建物や景観の規模・威容にも強く結びつく。  "
          },
          {
            "line": 94,
            "text": "例: The garden was filled with glorious autumn colors.  "
          },
          {
            "line": 95,
            "text": "訳: 庭は見事な秋の色彩で満ちていた。  "
          },
          {
            "line": 97,
            "text": "【反意語】"
          },
          {
            "line": 99,
            "text": "・unimpressive  "
          },
          {
            "line": 100,
            "text": "定義: 特に感銘を与えず、目立った美点や迫力がない。  "
          },
          {
            "line": 101,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 102,
            "text": "違い: 見る人に与える印象の強さという軸で、`magnificent` が非常に強い肯定的な感銘を表すのに対し、`unimpressive` は感銘を与えないことを表す。  "
          },
          {
            "line": 103,
            "text": "例: The building's plain exterior was rather unimpressive.  "
          },
          {
            "line": 104,
            "text": "訳: その建物の簡素な外観は、あまり印象的ではなかった。  "
          },
          {
            "line": 106,
            "text": "・plain  "
          },
          {
            "line": 107,
            "text": "定義: 装飾や華やかさがなく、簡素な。  "
          },
          {
            "line": 108,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 109,
            "text": "違い: 豪華さ・華やかさという限定された軸で対照をなす。`plain` は必ずしも質が悪いという否定的評価を含まず、`magnificent` の全面的な反対語ではない。  "
          },
          {
            "line": 110,
            "text": "例: The chapel has a plain wooden interior.  "
          },
          {
            "line": 111,
            "text": "訳: その礼拝堂の内部は簡素な木造である。  "
          }
        ]
      },
      {
        "sense_id": "sense:002",
        "full_sense": [
          {
            "line": 113,
            "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
          },
          {
            "line": 115,
            "text": "【日本語訳・定義】成果、演技、仕事、行為、機会、出来事などの質や価値が非常に高く、強く称賛したくなることを表す。外見の壮麗さを必要とせず、能力、出来、効果、経験の満足度などを高く評価する。単独の `Magnificent!` は「見事だ」「すばらしい」という感嘆になる。  "
          },
          {
            "line": 117,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 119,
            "text": "【レジスター/領域】標準語。やや強く高揚した称賛で、会話、批評、スポーツ、報道などに使う。日常会話では `great` や `excellent` のほうが中立的で頻繁である。  "
          },
          {
            "line": 121,
            "text": "【文法パターン】`a magnificent + 〈成果・演技・仕事・機会〉`＝すばらしい～／`〈成果・演技・仕事〉 + be/seem magnificent`＝～が見事である／`do/play/perform magnificently`＝見事に行う・演じる／`Magnificent!`＝見事だ・すばらしい  "
          },
          {
            "line": 123,
            "text": "【コロケーション】"
          },
          {
            "line": 125,
            "text": "・`a magnificent achievement`  "
          },
          {
            "line": 126,
            "text": "用途: 困難さや規模を踏まえて、成果を非常に高く評価する。  "
          },
          {
            "line": 127,
            "text": "例: Completing the bridge ahead of schedule was a magnificent achievement.  "
          },
          {
            "line": 128,
            "text": "訳: 予定より早く橋を完成させたことは、見事な偉業だった。  "
          },
          {
            "line": 130,
            "text": "・`a magnificent performance`  "
          },
          {
            "line": 131,
            "text": "用途: 演技、演奏、競技などの出来が極めて優れていることを表す。  "
          },
          {
            "line": 132,
            "text": "例: The violinist gave a magnificent performance in the final movement.  "
          },
          {
            "line": 133,
            "text": "訳: そのバイオリニストは最終楽章で見事な演奏を披露した。  "
          },
          {
            "line": 135,
            "text": "・`do a magnificent job`  "
          },
          {
            "line": 136,
            "text": "用途: 人や組織が仕事を非常にうまく成し遂げたことを称賛する。  "
          },
          {
            "line": 137,
            "text": "例: The rescue team did a magnificent job under dangerous conditions.  "
          },
          {
            "line": 138,
            "text": "訳: 救助隊は危険な状況下で実に見事な働きをした。  "
          },
          {
            "line": 140,
            "text": "・`a magnificent opportunity`  "
          },
          {
            "line": 141,
            "text": "用途: 価値や可能性が非常に大きい機会を強く肯定的に評価する。  "
          },
          {
            "line": 142,
            "text": "例: The scholarship gave her a magnificent opportunity to study abroad.  "
          },
          {
            "line": 143,
            "text": "訳: その奨学金は、彼女に留学するすばらしい機会を与えた。  "
          },
          {
            "line": 145,
            "text": "・`feel magnificent`  "
          },
          {
            "line": 146,
            "text": "用途: 心身の調子が非常によく、気分がすばらしいことを表す。  "
          },
          {
            "line": 147,
            "text": "例: After a full night's sleep, I felt magnificent.  "
          },
          {
            "line": 148,
            "text": "訳: 一晩ぐっすり眠った後、私は最高の気分だった。  "
          },
          {
            "line": 150,
            "text": "・`Magnificent!`  "
          },
          {
            "line": 151,
            "text": "用途: 出来事、成果、演技などに対する強い称賛を単独で表す。  "
          },
          {
            "line": 152,
            "text": "例: “We finished the repairs.” “Magnificent! We can reopen tomorrow.”  "
          },
          {
            "line": 153,
            "text": "訳: 「修理が終わりました」「すばらしい！ 明日には再開できる」  "
          },
          {
            "line": 155,
            "text": "【語法・注意】語義2では、対象の外観ではなく質・出来・価値を評価する。`a magnificent performance` は演技や演奏が非常に優れていたという意味であり、必ずしも豪華な舞台だったという意味ではない。`feel magnificent` は「堂々として感じる」ではなく「気分・体調が最高だ」という読みになる。`magnificent` は強い称賛なので、日常の小さな良さに使うと意図的に大げさ、ユーモラス、または熱のこもった響きになることがある。  "
          },
          {
            "line": 157,
            "text": "【類義語】"
          },
          {
            "line": 159,
            "text": "・excellent  "
          },
          {
            "line": 160,
            "text": "定義: 質、能力、出来が非常に高い。  "
          },
          {
            "line": 161,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 162,
            "text": "違い: `excellent` は評価基準に照らして質が高いことを比較的中立に述べる。`magnificent` は話者の感動や熱烈な称賛を強く表す。  "
          },
          {
            "line": 163,
            "text": "例: She submitted an excellent final report.  "
          },
          {
            "line": 164,
            "text": "訳: 彼女は非常に優れた最終報告書を提出した。  "
          },
          {
            "line": 166,
            "text": "・superb  "
          },
          {
            "line": 167,
            "text": "定義: 質や出来が最高水準である。  "
          },
          {
            "line": 168,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 169,
            "text": "違い: `superb` は洗練された出来や卓越した質に焦点を置く。`magnificent` は質に加えて規模や感銘の大きさを含みやすい。  "
          },
          {
            "line": 170,
            "text": "例: The chef prepared a superb meal using local ingredients.  "
          },
          {
            "line": 171,
            "text": "訳: その料理人は地元の食材で最高の料理を用意した。  "
          },
          {
            "line": 173,
            "text": "・outstanding  "
          },
          {
            "line": 174,
            "text": "定義: 同種のものの中で際立って優れている。  "
          },
          {
            "line": 175,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 176,
            "text": "違い: `outstanding` は比較集団の中で抜きん出ていることを示す。`magnificent` は比較対象を明示せず、強い感銘を直接表せる。  "
          },
          {
            "line": 177,
            "text": "例: Her outstanding leadership kept the project on track.  "
          },
          {
            "line": 178,
            "text": "訳: 彼女の卓越した指導力によって、プロジェクトは予定どおり進んだ。  "
          },
          {
            "line": 180,
            "text": "・wonderful  "
          },
          {
            "line": 181,
            "text": "定義: 喜び、満足、感嘆をもたらすほどすばらしい。  "
          },
          {
            "line": 182,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 183,
            "text": "違い: `wonderful` は楽しい経験や好ましい人・物に日常的に使う。`magnificent` はより強く、堂々とした、または劇的な称賛を帯びやすい。  "
          },
          {
            "line": 184,
            "text": "例: We had a wonderful evening with old friends.  "
          },
          {
            "line": 185,
            "text": "訳: 私たちは旧友たちとすばらしい夜を過ごした。  "
          },
          {
            "line": 187,
            "text": "【反意語】"
          },
          {
            "line": 189,
            "text": "・mediocre  "
          },
          {
            "line": 190,
            "text": "定義: 質や能力が平凡で、特に優れていない。  "
          },
          {
            "line": 191,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 192,
            "text": "違い: 質の高さという軸で、`magnificent` が極めて高い評価を表すのに対し、`mediocre` は平均的で期待を満たさない評価を表す。  "
          },
          {
            "line": 193,
            "text": "例: The sequel received mediocre reviews from critics.  "
          },
          {
            "line": 194,
            "text": "訳: その続編は批評家から凡庸だという評価を受けた。  "
          },
          {
            "line": 196,
            "text": "・terrible  "
          },
          {
            "line": 197,
            "text": "定義: 質や出来が非常に悪い。  "
          },
          {
            "line": 198,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 199,
            "text": "違い: 質の評価という軸で、`terrible` は非常に低い側、`magnificent` は非常に高い側を表す。  "
          },
          {
            "line": 200,
            "text": "例: The team gave a terrible performance in the second half.  "
          },
          {
            "line": 201,
            "text": "訳: そのチームは後半にひどい出来のプレーをした。  "
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
