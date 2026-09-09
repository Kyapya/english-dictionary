# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`frame-relation-reviewer-2ef298f1-3777-47a1-96b1-b5b69da4a73b`, declared_model=`gpt-5`.

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
  "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
  "blind_request_sha256": "c0fb952058b6306c95f8c5af7d6f1105c8159da1366167059506fa8a4a7f4f05",
  "blind_record_sha256": "3d1527ee6368c14f987dd9a95c5d155553e2b9111a6f4627b2991ff1863ff3f4",
  "input_sections": {
    "sense_structure": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 31,
        "text": "【日本語訳・定義】前に述べた事実・状況・判断を理由として、後に述べる結果が続くことを示す。単に出来事が後の時点で起こることではなく、前件から後件が結果として導かれることを表す。`so` よりフォーマルで、報告、説明、論証などで使われやすい。  "
      }
    ],
    "frames": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 37,
        "text": "【文法パターン】`〈原因となる文〉. Consequently, 〈結果の文〉`＝その結果、…／`〈原因となる文〉; consequently, 〈結果の文〉`＝…、したがって…／`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する。文頭で使うときは通常後ろにコンマを置き、二つの独立した節をコンマだけでつなぐ `…, consequently, …` は避ける。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 39,
        "text": "【コロケーション】"
      },
      {
        "line": 41,
        "text": "・`Consequently, 〈結果の文〉`  "
      },
      {
        "line": 42,
        "text": "用途: 直前に述べた原因・根拠を受けて、文全体の結論や結果を明示する。  "
      },
      {
        "line": 43,
        "text": "例: The train service was suspended. Consequently, many employees worked from home.  "
      },
      {
        "line": 44,
        "text": "訳: 列車の運行が停止された。その結果、多くの従業員が在宅勤務をした。  "
      },
      {
        "line": 46,
        "text": "・`〈原因となる文〉; consequently, 〈結果の文〉`  "
      },
      {
        "line": 47,
        "text": "用途: 密接な因果関係にある二つの独立節を、セミコロンでつなぐフォーマルな書き方である。  "
      },
      {
        "line": 48,
        "text": "例: The evidence was incomplete; consequently, the committee postponed its decision.  "
      },
      {
        "line": 49,
        "text": "訳: 証拠が不十分だったため、委員会は決定を延期した。  "
      },
      {
        "line": 51,
        "text": "・`〈主語〉 + consequently + 〈動詞句〉`  "
      },
      {
        "line": 52,
        "text": "用途: 結果を表す副詞として、主語の後、主要動詞の前に置く。  "
      },
      {
        "line": 53,
        "text": "例: Demand fell sharply, and the company consequently reduced production.  "
      },
      {
        "line": 54,
        "text": "訳: 需要が急減したため、その会社は結果として生産を減らした。  "
      },
      {
        "line": 56,
        "text": "・`be consequently + 〈過去分詞・形容詞〉`  "
      },
      {
        "line": 57,
        "text": "用途: 原因の結果として生じた状態や判断を、`be` の後で説明する。  "
      },
      {
        "line": 58,
        "text": "例: The deadline was missed, and the application was consequently rejected.  "
      },
      {
        "line": 59,
        "text": "訳: 締切に間に合わなかったため、その申請は結果として却下された。  "
      },
      {
        "line": 61,
        "text": "・`and consequently + 〈動詞句〉`  "
      },
      {
        "line": 62,
        "text": "用途: 一つの節の中で、前の節・句に示された事情の帰結として後続の行為や状態を示す。  "
      },
      {
        "line": 63,
        "text": "例: The region receives little rainfall and consequently faces frequent water shortages.  "
      },
      {
        "line": 64,
        "text": "訳: その地域は降雨量が少なく、その結果しばしば水不足に直面する。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 68,
        "text": "【類義語】"
      },
      {
        "line": 70,
        "text": "・therefore  "
      },
      {
        "line": 71,
        "text": "定義: 前に述べた事実・理由から、論理的な結論や結果が導かれることを示す。  "
      },
      {
        "line": 72,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 73,
        "text": "違い: `therefore` は論証の結論を明示する響きが特に強い。`consequently` は出来事・状況から実際に続く結果を示すときにも自然である。  "
      },
      {
        "line": 74,
        "text": "例: The data are incomplete; therefore, no firm conclusion can be drawn.  "
      },
      {
        "line": 75,
        "text": "訳: データが不完全なので、確かな結論は導けない。  "
      },
      {
        "line": 77,
        "text": "・as a result  "
      },
      {
        "line": 78,
        "text": "定義: 前の出来事や状況の結果として、後の出来事が起こることを示す句。  "
      },
      {
        "line": 79,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 80,
        "text": "違い: `as a result` は日常的で分かりやすく、会話から文章まで広く使える。`consequently` は一語でよりフォーマルに因果関係をつなぐ。  "
      },
      {
        "line": 81,
        "text": "例: The supplier delayed delivery. As a result, the launch was postponed.  "
      },
      {
        "line": 82,
        "text": "訳: 供給業者が納品を遅らせた。その結果、発売は延期された。  "
      },
      {
        "line": 84,
        "text": "・thus  "
      },
      {
        "line": 85,
        "text": "定義: 前の内容を受けて、結果や論理的帰結を示す。  "
      },
      {
        "line": 86,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 87,
        "text": "違い: `thus` は書き言葉でより硬く、論文・技術文書では「このように」の意味も持つ。`consequently` はここでいう「その結果」の意味に限られる。  "
      },
      {
        "line": 88,
        "text": "例: The sample was contaminated and thus could not be analyzed.  "
      },
      {
        "line": 89,
        "text": "訳: 試料が汚染されていたため、したがって分析できなかった。  "
      },
      {
        "line": 91,
        "text": "・accordingly  "
      },
      {
        "line": 92,
        "text": "定義: ある事情・情報に応じて、またはその結果として行動・処置がなされることを示す。  "
      },
      {
        "line": 93,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 94,
        "text": "違い: `accordingly` は「事情に応じて」の意味で意図的な対応を表すことがある。`consequently` は、対応の意図がなくても因果の結果を示せる。  "
      },
      {
        "line": 95,
        "text": "例: The weather forecast changed, so the organizers adjusted the schedule accordingly.  "
      },
      {
        "line": 96,
        "text": "訳: 天気予報が変わったので、主催者はそれに応じて日程を調整した。  "
      },
      {
        "line": 98,
        "text": "・hence  "
      },
      {
        "line": 99,
        "text": "定義: 前に述べた理由・事実から結論または結果が生じることを示す。  "
      },
      {
        "line": 100,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 101,
        "text": "違い: 因果を示す `hence` は `consequently` より文語的で、簡潔な論証や固定表現に多い。また `hence` には「今から〜後」の時間表現など別の用法もある。  "
      },
      {
        "line": 102,
        "text": "例: The files were encrypted; hence, only authorized staff could read them.  "
      },
      {
        "line": 103,
        "text": "訳: ファイルは暗号化されていた。したがって、閲覧できたのは権限を持つ職員だけだった。  "
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
