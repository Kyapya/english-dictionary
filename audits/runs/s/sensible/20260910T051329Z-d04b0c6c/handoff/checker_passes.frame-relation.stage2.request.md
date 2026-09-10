# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`sensible-checker-frame-relation-20260910T051329Z-d04b0c6c`, declared_model=`codex-gpt-5`.

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
  "input_body_sha256": "dce1e8375f2e9709647eb4c0fd89fa016895cec32363a81b3950d8cdb28a2078",
  "blind_request_sha256": "324fbc20c9552add4105e28ee93abb8a6a1e81c82ab0da9e8f96795adbf4aef0",
  "blind_record_sha256": "76b4fe8f0c43c288e99ff35521b6c455c559d6569c27dde2d5d88a610cf1f848",
  "input_sections": {
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】感情だけで決めず、理由・経験・実際の条件を考えて、適切で無理のない判断や行動をすることを表す。人にも、考え・助言・計画・解決策などにも使い、話し手が妥当だと評価する含みがある。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 163,
        "text": "【日本語訳・定義】衣服・靴・かばんなどが、流行や見た目よりも、歩きやすさ・丈夫さ・防寒性などの実用性を重視して作られたり選ばれたりしていることを表す。必ずしも醜い、古い、または質が低いという意味ではない。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 232,
        "text": "【日本語訳・定義】差・変化・増減・量などが、感覚や判断によって認識できる程度にはっきりしていることを表す。現代の一般会話での「分別のある」という意味より形式的で、sensible difference や sensible increase のように、無視できない程度を述べる。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 312,
        "text": "【日本語訳・定義】痛み・熱・光などの外部刺激を、感覚器官や身体で受け取る能力があることを表す。現代の一般英語では sensitive to が普通で、sensible to は古風・形式的または専門的に響く。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 373,
        "text": "【日本語訳・定義】事実・危険・義務・誤り・親切などを心で認識し、強く意識していることを表す。通常 sensible of 〈名詞〉の形で使い、現代の会話では aware of、conscious of、grateful for などが自然なことが多い。  "
      }
    ],
    "frames": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 48,
        "text": "【文法パターン】a sensible person/choice/decision/plan＝分別のある人・妥当な選択・判断・計画／sensible advice＝現実的で適切な助言／be sensible＝分別をもって行動する／be sensible about 〈money・risk・food〉＝〈お金・危険・食事〉について現実的に考える／it is sensible to do ＝～するのが妥当だ／it is sensible for someone to do ＝〈人〉が～するのが妥当だ／the sensible thing to do＝取るべき妥当な行動／be sensible enough to do ＝分別があるので～する。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 169,
        "text": "【文法パターン】sensible shoes/clothes/footwear＝実用的な靴・衣服・履物／a sensible coat＝実用本位のコート／wear/choose sensible clothing＝実用的な服を着る・選ぶ／something is sensible for 〈weather・travel〉＝〈天候・旅行〉に適して実用的だ。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 238,
        "text": "【文法パターン】a sensible difference＝感じ取れる明確な差／a sensible increase/decrease in something＝〈物事〉のかなりはっきりした増加・減少／a sensible change in something＝〈物事〉の認識できる変化／sensible 〈amount・degree〉＝無視できない程度の量・度合い。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 318,
        "text": "【文法パターン】be sensible to 〈pain・heat・light〉＝〈痛み・熱・光〉を感じ取れる／become sensible to 〈stimulus〉＝〈刺激〉を知覚するようになる／sensible to the touch＝触れて感じ取れる。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 379,
        "text": "【文法パターン】be sensible of 〈fact・danger・duty・error〉＝〈事実・危険・義務・誤り〉を意識している／be sensible of 〈kindness・benefit〉＝〈親切・恩恵〉を深く感じている／be deeply/keenly sensible of something＝～を深く・強く意識している／sensible of the fact that 〈節〉＝～という事実を認識している。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 50,
        "text": "【コロケーション】"
      },
      {
        "line": 52,
        "text": "・a sensible decision  "
      },
      {
        "line": 53,
        "text": "用途: 条件や結果を考えたうえで、妥当な判断であることを表す。  "
      },
      {
        "line": 54,
        "text": "例: Taking the earlier train was a sensible decision.  "
      },
      {
        "line": 55,
        "text": "訳: 早い方の電車に乗ったのは妥当な判断だった。  "
      },
      {
        "line": 57,
        "text": "・a sensible approach to 〈problem〉  "
      },
      {
        "line": 58,
        "text": "用途: 問題に対して、現実的で無理のない取り組み方を示す。  "
      },
      {
        "line": 59,
        "text": "例: We need a sensible approach to reducing unnecessary costs.  "
      },
      {
        "line": 60,
        "text": "訳: 不要な費用を減らすには、現実的な取り組み方が必要だ。  "
      },
      {
        "line": 62,
        "text": "・sensible advice  "
      },
      {
        "line": 63,
        "text": "用途: 経験や事情に基づく、実行しやすい助言を表す。  "
      },
      {
        "line": 64,
        "text": "例: Her sensible advice helped me avoid a costly mistake.  "
      },
      {
        "line": 65,
        "text": "訳: 彼女の現実的な助言のおかげで、私は高くつく間違いを避けられた。  "
      },
      {
        "line": 67,
        "text": "・it is sensible to do  "
      },
      {
        "line": 68,
        "text": "用途: ある行動を取るのが分別にかなっていると述べる基本構文。  "
      },
      {
        "line": 69,
        "text": "例: It is sensible to keep a copy of the receipt.  "
      },
      {
        "line": 70,
        "text": "訳: 領収書の写しを保管しておくのが賢明だ。  "
      },
      {
        "line": 72,
        "text": "・it is sensible for someone to do  "
      },
      {
        "line": 73,
        "text": "用途: 特定の人がある行動をするのが妥当だと述べる。  "
      },
      {
        "line": 74,
        "text": "例: It would be sensible for you to check the figures again.  "
      },
      {
        "line": 75,
        "text": "訳: あなたがもう一度数字を確認するのが賢明だろう。  "
      },
      {
        "line": 77,
        "text": "・the sensible thing to do  "
      },
      {
        "line": 78,
        "text": "用途: いくつかの選択肢の中で、最も妥当な行動を指す。  "
      },
      {
        "line": 79,
        "text": "例: The sensible thing to do is wait until the weather improves.  "
      },
      {
        "line": 80,
        "text": "訳: 天候が回復するまで待つのが妥当な行動だ。  "
      },
      {
        "line": 82,
        "text": "・be sensible about 〈issue〉  "
      },
      {
        "line": 83,
        "text": "用途: 問題や資源について、感情的にならず現実的に考える。  "
      },
      {
        "line": 84,
        "text": "例: Please be sensible about how much equipment you bring.  "
      },
      {
        "line": 85,
        "text": "訳: どれだけ機材を持ってくるかは、現実的に考えてください。  "
      },
      {
        "line": 87,
        "text": "・be sensible enough to do  "
      },
      {
        "line": 88,
        "text": "用途: 分別があるため、危険や不利益を避ける行動を取ることを表す。  "
      },
      {
        "line": 89,
        "text": "例: He was sensible enough to ask for help before the problem grew.  "
      },
      {
        "line": 90,
        "text": "訳: 彼は問題が大きくなる前に助けを求めるだけの分別があった。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 171,
        "text": "【コロケーション】"
      },
      {
        "line": 173,
        "text": "・sensible shoes  "
      },
      {
        "line": 174,
        "text": "用途: 流行性よりも歩きやすさや足の保護を重視した靴を表す。  "
      },
      {
        "line": 175,
        "text": "例: Wear sensible shoes because the tour involves a lot of walking.  "
      },
      {
        "line": 176,
        "text": "訳: たくさん歩くツアーなので、歩きやすい靴を履いてください。  "
      },
      {
        "line": 178,
        "text": "・sensible clothing  "
      },
      {
        "line": 179,
        "text": "用途: 天候や活動に合い、実用性を優先した衣服を表す。  "
      },
      {
        "line": 180,
        "text": "例: Pack sensible clothing for the cold and wet conditions.  "
      },
      {
        "line": 181,
        "text": "訳: 寒くて雨の多い状況に合う実用的な服を荷造りしてください。  "
      },
      {
        "line": 183,
        "text": "・sensible footwear  "
      },
      {
        "line": 184,
        "text": "用途: 見た目より機能性を重視した履物を、やや説明的に表す。  "
      },
      {
        "line": 185,
        "text": "例: The guide recommends sensible footwear for the uneven ground.  "
      },
      {
        "line": 186,
        "text": "訳: ガイドは、でこぼこした地面には実用的な履物を勧めている。  "
      },
      {
        "line": 188,
        "text": "・a sensible coat  "
      },
      {
        "line": 189,
        "text": "用途: 防寒・耐久性・天候への対応を重視したコートを表す。  "
      },
      {
        "line": 190,
        "text": "例: I bought a sensible coat rather than a delicate fashion jacket.  "
      },
      {
        "line": 191,
        "text": "訳: 繊細なファッションジャケットではなく、実用的なコートを買った。  "
      },
      {
        "line": 193,
        "text": "・choose sensible clothing  "
      },
      {
        "line": 194,
        "text": "用途: 活動や天候に合わせて、見た目より使いやすさを基準に衣服を選ぶ。  "
      },
      {
        "line": 195,
        "text": "例: Choose sensible clothing for the long flight.  "
      },
      {
        "line": 196,
        "text": "訳: 長時間のフライトには実用的な服を選んでください。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 240,
        "text": "【コロケーション】"
      },
      {
        "line": 242,
        "text": "・a sensible difference  "
      },
      {
        "line": 243,
        "text": "用途: 2つの状態や結果の間に、認識できるほどの差があることを表す。  "
      },
      {
        "line": 244,
        "text": "例: The software update made a sensible difference to the loading time.  "
      },
      {
        "line": 245,
        "text": "訳: ソフトウェアの更新によって、読み込み時間に明らかな違いが出た。  "
      },
      {
        "line": 247,
        "text": "・a sensible increase in something  "
      },
      {
        "line": 248,
        "text": "用途: 数値や量が、認識できる程度に増えたことを形式的に表す。  "
      },
      {
        "line": 249,
        "text": "例: The policy led to a sensible increase in public access.  "
      },
      {
        "line": 250,
        "text": "訳: その政策によって、一般の利用可能性がはっきり増した。  "
      },
      {
        "line": 252,
        "text": "・a sensible reduction in something  "
      },
      {
        "line": 253,
        "text": "用途: 費用・危険・排出量などが、無視できない程度に減ったことを表す。  "
      },
      {
        "line": 254,
        "text": "例: The new process produced a sensible reduction in waste.  "
      },
      {
        "line": 255,
        "text": "訳: 新しい工程によって、廃棄物が明らかに減少した。  "
      },
      {
        "line": 257,
        "text": "・a sensible change in something  "
      },
      {
        "line": 258,
        "text": "用途: 状態や傾向に、認識できるほどの変化が起きたことを述べる。  "
      },
      {
        "line": 259,
        "text": "例: There has been a sensible change in the patient's condition.  "
      },
      {
        "line": 260,
        "text": "訳: 患者の状態には、はっきり分かる変化があった。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 320,
        "text": "【コロケーション】"
      },
      {
        "line": 322,
        "text": "・be sensible to pain  "
      },
      {
        "line": 323,
        "text": "用途: 痛みを感覚として受け取る能力があることを、形式的に表す。  "
      },
      {
        "line": 324,
        "text": "例: The injured area remained sensible to pain after the procedure.  "
      },
      {
        "line": 325,
        "text": "訳: 処置後も、負傷した部位は痛みを感じ取る状態だった。  "
      },
      {
        "line": 327,
        "text": "・be sensible to heat  "
      },
      {
        "line": 328,
        "text": "用途: 熱を感じ取ることができることを述べる。  "
      },
      {
        "line": 329,
        "text": "例: The instrument is sensible to heat from a nearby flame.  "
      },
      {
        "line": 330,
        "text": "訳: その器具は近くの炎から出る熱を感知できる。  "
      },
      {
        "line": 332,
        "text": "・be sensible to light  "
      },
      {
        "line": 333,
        "text": "用途: 光を感知する性質があることを、古風または技術的に表す。  "
      },
      {
        "line": 334,
        "text": "例: The material is sensible to light and should be stored in the dark.  "
      },
      {
        "line": 335,
        "text": "訳: その素材は光を感知する性質があるので、暗所で保管すべきだ。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 381,
        "text": "【コロケーション】"
      },
      {
        "line": 383,
        "text": "・be sensible of 〈fact〉  "
      },
      {
        "line": 384,
        "text": "用途: ある事実を心で認識していることを、形式的に表す。  "
      },
      {
        "line": 385,
        "text": "例: She was sensible of the fact that her decision affected the whole team.  "
      },
      {
        "line": 386,
        "text": "訳: 彼女は、自分の決定がチーム全体に影響するという事実を意識していた。  "
      },
      {
        "line": 388,
        "text": "・be sensible of one's error  "
      },
      {
        "line": 389,
        "text": "用途: 自分の誤りに気づき、それを認識していることを表す。  "
      },
      {
        "line": 390,
        "text": "例: He soon became sensible of his error and apologized.  "
      },
      {
        "line": 391,
        "text": "訳: 彼はすぐに自分の誤りに気づき、謝罪した。  "
      },
      {
        "line": 393,
        "text": "・be sensible of someone's kindness  "
      },
      {
        "line": 394,
        "text": "用途: 人から受けた親切や恩恵を深く感じていることを表す。  "
      },
      {
        "line": 395,
        "text": "例: I am deeply sensible of your kindness during this difficult time.  "
      },
      {
        "line": 396,
        "text": "訳: この困難な時期にあなたが親切にしてくださったことを深く感じています。  "
      },
      {
        "line": 398,
        "text": "・be keenly sensible of something  "
      },
      {
        "line": 399,
        "text": "用途: 危険・責任・苦境などを強く意識していることを、硬い表現で述べる。  "
      },
      {
        "line": 400,
        "text": "例: The volunteers were keenly sensible of the risks involved.  "
      },
      {
        "line": 401,
        "text": "訳: ボランティアたちは、そこに伴う危険を強く意識していた。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 94,
        "text": "【類義語】"
      },
      {
        "line": 96,
        "text": "・reasonable  "
      },
      {
        "line": 97,
        "text": "定義: 道理にかなった、妥当な、無理のない。  "
      },
      {
        "line": 98,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 99,
        "text": "違い: reasonable は判断・要求・価格などが公平で受け入れやすいことに焦点がある。sensible は現実の結果を考えて適切に行動する分別を強調しやすい。  "
      },
      {
        "line": 100,
        "text": "例: That seems like a reasonable compromise.  "
      },
      {
        "line": 101,
        "text": "訳: それは妥当な妥協案のように思える。  "
      },
      {
        "line": 103,
        "text": "・practical  "
      },
      {
        "line": 104,
        "text": "定義: 実際に役立ち、実行できる、実用的な。  "
      },
      {
        "line": 105,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 106,
        "text": "違い: practical は理論や見た目より実用性・実行可能性に焦点がある。sensible は実用性に加え、状況に応じた判断の適切さも表す。  "
      },
      {
        "line": 107,
        "text": "例: We chose a practical solution that fit the budget.  "
      },
      {
        "line": 108,
        "text": "訳: 私たちは予算に合う実用的な解決策を選んだ。  "
      },
      {
        "line": 110,
        "text": "・rational  "
      },
      {
        "line": 111,
        "text": "定義: 理性や論理に基づく、合理的な。  "
      },
      {
        "line": 112,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 113,
        "text": "違い: rational は感情や衝動ではなく、論理的な理由に基づくことを強調する。sensible の方が日常的で、生活上の分別にも使いやすい。  "
      },
      {
        "line": 114,
        "text": "例: There is no rational reason to reject the proposal.  "
      },
      {
        "line": 115,
        "text": "訳: その提案を拒む合理的な理由はない。  "
      },
      {
        "line": 117,
        "text": "・prudent  "
      },
      {
        "line": 118,
        "text": "定義: 将来の危険や損失を考えて慎重で賢明な。  "
      },
      {
        "line": 119,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 120,
        "text": "違い: prudent は特に危険・費用・将来の結果を避ける慎重さを含み、sensible より硬い。  "
      },
      {
        "line": 121,
        "text": "例: It would be prudent to set aside some emergency savings.  "
      },
      {
        "line": 122,
        "text": "訳: 緊急時のために貯蓄をいくらか取っておくのが賢明だろう。  "
      },
      {
        "line": 124,
        "text": "・wise  "
      },
      {
        "line": 125,
        "text": "定義: 経験や深い理解に基づいて、賢明な。  "
      },
      {
        "line": 126,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 127,
        "text": "違い: wise は長期的な洞察や人生経験まで含むことがある。sensible はもっと身近な状況での現実的な判断に焦点を置く。  "
      },
      {
        "line": 128,
        "text": "例: It was wise to discuss the risks before signing.  "
      },
      {
        "line": 129,
        "text": "訳: 署名する前に危険性を話し合ったのは賢明だった。  "
      },
      {
        "line": 131,
        "text": "・judicious  "
      },
      {
        "line": 132,
        "text": "定義: 判断力があり、慎重で適切な。  "
      },
      {
        "line": 133,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 134,
        "text": "違い: judicious は選択・配分・発言などを慎重に見極めたことを表す硬い語。sensible の方が一般的で親しみやすい。  "
      },
      {
        "line": 135,
        "text": "例: A judicious use of examples can clarify the argument.  "
      },
      {
        "line": 136,
        "text": "訳: 例を適切に使えば、その議論を明確にできる。  "
      },
      {
        "line": 138,
        "text": "【反意語】"
      },
      {
        "line": 140,
        "text": "・silly  "
      },
      {
        "line": 141,
        "text": "定義: 分別を欠いた、ばかげた。  "
      },
      {
        "line": 142,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 143,
        "text": "違い: silly は判断や行動が軽率で、子どもっぽくばかげていることを表す。sensible の「現実を踏まえた分別」と対照的である。  "
      },
      {
        "line": 144,
        "text": "例: It would be silly to ignore the warning.  "
      },
      {
        "line": 145,
        "text": "訳: その警告を無視するのはばかげている。  "
      },
      {
        "line": 147,
        "text": "・foolish  "
      },
      {
        "line": 148,
        "text": "定義: 判断力や分別を欠いた、愚かな。  "
      },
      {
        "line": 149,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 150,
        "text": "違い: foolish は結果を考えない愚かな判断を強く非難する語で、sensible の反対側に位置する。  "
      },
      {
        "line": 151,
        "text": "例: It was foolish to spend all the money at once.  "
      },
      {
        "line": 152,
        "text": "訳: お金を全部一度に使うのは愚かなことだった。  "
      },
      {
        "line": 154,
        "text": "・impractical  "
      },
      {
        "line": 155,
        "text": "定義: 実行しにくく、現実の条件に合わない。  "
      },
      {
        "line": 156,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 157,
        "text": "違い: impractical は計画や提案などの実行可能性の不足に焦点を置く。人の分別全般の反意語ではないが、sensible plan などとは実用性の軸で対照をなす。  "
      },
      {
        "line": 158,
        "text": "例: The design is attractive but impractical for daily use.  "
      },
      {
        "line": 159,
        "text": "訳: そのデザインは魅力的だが、日常使用には実用的でない。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 200,
        "text": "【類義語】"
      },
      {
        "line": 202,
        "text": "・practical  "
      },
      {
        "line": 203,
        "text": "定義: 実際の用途に役立つ、実用的な。  "
      },
      {
        "line": 204,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 205,
        "text": "違い: practical は衣服・道具・計画の実用性を広く表す。sensible は使用場面に合うように選ばれたという判断の含みを持ちやすい。  "
      },
      {
        "line": 206,
        "text": "例: These practical boots are good for walking in the rain.  "
      },
      {
        "line": 207,
        "text": "訳: この実用的なブーツは雨の中を歩くのに向いている。  "
      },
      {
        "line": 209,
        "text": "・functional  "
      },
      {
        "line": 210,
        "text": "定義: 見た目より機能を果たすことを重視した、機能的な。  "
      },
      {
        "line": 211,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 212,
        "text": "違い: functional はデザインや構造が目的の機能を果たすかに焦点があり、sensible は日常の選択として妥当かを評価する。  "
      },
      {
        "line": 213,
        "text": "例: The clothes are simple but highly functional.  "
      },
      {
        "line": 214,
        "text": "訳: その服はシンプルだが、機能性が非常に高い。  "
      },
      {
        "line": 216,
        "text": "・serviceable  "
      },
      {
        "line": 217,
        "text": "定義: 十分に使える、丈夫で役に立つ。  "
      },
      {
        "line": 218,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 219,
        "text": "違い: serviceable は見た目の魅力より、必要な用途に耐えることを表すやや硬い語。sensible は選択の分別にも使える。  "
      },
      {
        "line": 220,
        "text": "例: The hotel provides clean and serviceable furnishings.  "
      },
      {
        "line": 221,
        "text": "訳: そのホテルは清潔で十分に使える備品を備えている。  "
      },
      {
        "line": 223,
        "text": "・utilitarian  "
      },
      {
        "line": 224,
        "text": "定義: 実用性だけを重視した、実用主義的な。  "
      },
      {
        "line": 225,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 226,
        "text": "違い: utilitarian は装飾性をほとんど考慮しない硬い・批評的な響きがある。sensible は実用的でも、見た目のよさを排除するとは限らない。  "
      },
      {
        "line": 227,
        "text": "例: The building has a plain, utilitarian design.  "
      },
      {
        "line": 228,
        "text": "訳: その建物は簡素で実用本位の設計になっている。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 264,
        "text": "【類義語】"
      },
      {
        "line": 266,
        "text": "・perceptible  "
      },
      {
        "line": 267,
        "text": "定義: 感覚や心によって知覚できる、感じ取れる。  "
      },
      {
        "line": 268,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 269,
        "text": "違い: perceptible は知覚可能性を直接表す硬い語で、sensible のこの用法と最も近い。sensible には「かなりの」という評価が加わることがある。  "
      },
      {
        "line": 270,
        "text": "例: There was a perceptible change in the tone of the discussion.  "
      },
      {
        "line": 271,
        "text": "訳: 議論の雰囲気には感じ取れる変化があった。  "
      },
      {
        "line": 273,
        "text": "・noticeable  "
      },
      {
        "line": 274,
        "text": "定義: 見たり感じたりして気づくことができる、目立つ。  "
      },
      {
        "line": 275,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 276,
        "text": "違い: noticeable は日常的で、目や耳などで気づきやすいことに焦点がある。sensible のこの用法はより形式的で、量や程度にも使いやすい。  "
      },
      {
        "line": 277,
        "text": "例: There was a noticeable improvement in her balance.  "
      },
      {
        "line": 278,
        "text": "訳: 彼女のバランスには目立った改善があった。  "
      },
      {
        "line": 280,
        "text": "・appreciable  "
      },
      {
        "line": 281,
        "text": "定義: はっきり認められる、かなりの、無視できない。  "
      },
      {
        "line": 282,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 283,
        "text": "違い: appreciable は差・量・変化が評価上無視できないことを強調する。sensible と近いが、程度の大きさに焦点を置きやすい。  "
      },
      {
        "line": 284,
        "text": "例: The repair resulted in an appreciable reduction in noise.  "
      },
      {
        "line": 285,
        "text": "訳: 修理によって騒音がかなり減少した。  "
      },
      {
        "line": 287,
        "text": "・marked  "
      },
      {
        "line": 288,
        "text": "定義: はっきりした、顕著な。  "
      },
      {
        "line": 289,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 290,
        "text": "違い: marked は変化や差が目立つことを簡潔に示す。sensible は、認識できる程度に達したことをやや控えめに述べる。  "
      },
      {
        "line": 291,
        "text": "例: The study found a marked difference between the two groups.  "
      },
      {
        "line": 292,
        "text": "訳: その研究は、2つのグループの間に顕著な差があることを見いだした。  "
      },
      {
        "line": 294,
        "text": "【反意語】"
      },
      {
        "line": 296,
        "text": "・imperceptible  "
      },
      {
        "line": 297,
        "text": "定義: 感覚や心では知覚できない、気づけない。  "
      },
      {
        "line": 298,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 299,
        "text": "違い: imperceptible は差や変化が小さすぎて感じ取れないことを表し、sensible の「認識できる」という軸と直接対照をなす。  "
      },
      {
        "line": 300,
        "text": "例: The change in temperature was almost imperceptible.  "
      },
      {
        "line": 301,
        "text": "訳: 気温の変化はほとんど感じ取れないほどだった。  "
      },
      {
        "line": 303,
        "text": "・negligible  "
      },
      {
        "line": 304,
        "text": "定義: 小さすぎて考慮する必要がない、取るに足りない。  "
      },
      {
        "line": 305,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 306,
        "text": "違い: negligible は重要性や影響の小ささに焦点がある。知覚できるかどうかを直接述べる語ではないが、sensible increase などの「無視できない程度」と量の軸で対照をなす。  "
      },
      {
        "line": 307,
        "text": "例: The difference in cost is negligible.  "
      },
      {
        "line": 308,
        "text": "訳: 費用の差は取るに足りない。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 339,
        "text": "【類義語】"
      },
      {
        "line": 341,
        "text": "・sensitive to 〈stimulus〉  "
      },
      {
        "line": 342,
        "text": "定義: 〈刺激〉を感じ取る、またはその影響を受けやすい。  "
      },
      {
        "line": 343,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 344,
        "text": "違い: sensitive to は現代英語で普通の表現で、感覚的な知覚に加えて化学反応・感情・社会的影響にも使える。sensible to は形式的・古風で範囲が狭い。  "
      },
      {
        "line": 345,
        "text": "例: Some people are highly sensitive to bright light.  "
      },
      {
        "line": 346,
        "text": "訳: 明るい光に非常に敏感な人もいる。  "
      },
      {
        "line": 348,
        "text": "・responsive to 〈stimulus〉  "
      },
      {
        "line": 349,
        "text": "定義: 〈刺激〉に反応する、反応を示す。  "
      },
      {
        "line": 350,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 351,
        "text": "違い: responsive to は刺激を感じることより、それに反応や変化が生じることを強調する。sensible to はまず知覚可能性を表す。  "
      },
      {
        "line": 352,
        "text": "例: The sensor is responsive to small changes in pressure.  "
      },
      {
        "line": 353,
        "text": "訳: そのセンサーは圧力の小さな変化にも反応する。  "
      },
      {
        "line": 355,
        "text": "【反意語】"
      },
      {
        "line": 357,
        "text": "・insensible to 〈stimulus〉  "
      },
      {
        "line": 358,
        "text": "定義: 〈刺激〉を感じない、意識しない。  "
      },
      {
        "line": 359,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 360,
        "text": "違い: insensible to は痛み・熱などを知覚できないことを表し、この用法の sensible to と直接対照をなす。  "
      },
      {
        "line": 361,
        "text": "例: The tissue was insensible to light touch.  "
      },
      {
        "line": 362,
        "text": "訳: その組織は軽く触れても感じなかった。  "
      },
      {
        "line": 364,
        "text": "・impervious to 〈stimulus〉  "
      },
      {
        "line": 365,
        "text": "定義: 〈刺激・影響〉を通さず、受け付けない。  "
      },
      {
        "line": 366,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 367,
        "text": "違い: impervious to は単に知覚できないだけでなく、刺激や影響が作用しないことを強く表す。sensible to より遮断の含みが強い。  "
      },
      {
        "line": 368,
        "text": "例: The coating is impervious to heat and moisture.  "
      },
      {
        "line": 369,
        "text": "訳: そのコーティングは熱や湿気を通さない。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 407,
        "text": "【類義語】"
      },
      {
        "line": 409,
        "text": "・aware of something  "
      },
      {
        "line": 410,
        "text": "定義: 〈事実・状況・問題〉に気づいている、知っている。  "
      },
      {
        "line": 411,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 412,
        "text": "違い: aware of は現代英語で最も普通の「認識している」で、感情の深さを必ずしも含まない。sensible of は形式的で、強く感じている含みを持つことがある。  "
      },
      {
        "line": 413,
        "text": "例: Are you aware of the possible consequences?  "
      },
      {
        "line": 414,
        "text": "訳: 起こりうる結果を認識していますか。  "
      },
      {
        "line": 416,
        "text": "・conscious of something  "
      },
      {
        "line": 417,
        "text": "定義: 〈事実・存在・自分の行動〉を意識している。  "
      },
      {
        "line": 418,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 419,
        "text": "違い: conscious of は意識に上っていることや自覚を強調する。sensible of より現代的だが、文脈によっては「気にしている」という含みも出る。  "
      },
      {
        "line": 420,
        "text": "例: She was conscious of every movement in the quiet room.  "
      },
      {
        "line": 421,
        "text": "訳: 彼女は静かな部屋でのあらゆる動きを意識していた。  "
      },
      {
        "line": 423,
        "text": "・cognizant of something  "
      },
      {
        "line": 424,
        "text": "定義: 〈事実・問題・義務〉を十分に認識している。  "
      },
      {
        "line": 425,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 426,
        "text": "違い: cognizant of は非常に形式的で、事実を理解・把握していることに焦点がある。sensible of は認識に加えて感情的な受け止め方も表しうる。  "
      },
      {
        "line": 427,
        "text": "例: The committee is cognizant of the need for further evidence.  "
      },
      {
        "line": 428,
        "text": "訳: 委員会は、さらなる証拠が必要であることを十分に認識している。  "
      },
      {
        "line": 430,
        "text": "・mindful of something  "
      },
      {
        "line": 431,
        "text": "定義: 〈危険・影響・必要性〉を意識し、注意を払っている。  "
      },
      {
        "line": 432,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 433,
        "text": "違い: mindful of は認識したうえで注意深く行動する含みが強い。sensible of は単に気づいていることや、恩恵を感じていることにも使える。  "
      },
      {
        "line": 434,
        "text": "例: Please be mindful of the needs of other passengers.  "
      },
      {
        "line": 435,
        "text": "訳: 他の乗客のニーズに配慮してください。  "
      },
      {
        "line": 437,
        "text": "【反意語】"
      },
      {
        "line": 439,
        "text": "・unaware of something  "
      },
      {
        "line": 440,
        "text": "定義: 〈事実・状況〉に気づいていない、知らない。  "
      },
      {
        "line": 441,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 442,
        "text": "違い: unaware of は認識がないことを直接表し、sensible of の「意識している」と対照をなす。  "
      },
      {
        "line": 443,
        "text": "例: He was unaware of the rule when he submitted the form.  "
      },
      {
        "line": 444,
        "text": "訳: 彼はその用紙を提出したとき、その規則を知らなかった。  "
      },
      {
        "line": 446,
        "text": "・oblivious to something  "
      },
      {
        "line": 447,
        "text": "定義: 〈事実・危険・周囲の状況〉にまったく気づいていない。  "
      },
      {
        "line": 448,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 449,
        "text": "違い: oblivious to は気づいていない程度が強く、しばしば周囲への無関心を含む。sensible of と反対方向だが、単なる知識不足より強い。  "
      },
      {
        "line": 450,
        "text": "例: The driver seemed oblivious to the warning signs.  "
      },
      {
        "line": 451,
        "text": "訳: その運転手は警告標識にまったく気づいていないようだった。  "
      }
    ],
    "antonym_axis_items": [
      {
        "item_id": "ant-5626f8a7c604",
        "stage1_axis": {
          "item_id": "ant-5626f8a7c604",
          "axis": "判断",
          "relation_type": "評価",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 140,
          "line_end": 140,
          "exact_quote": "・silly  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 143,
          "line_end": 143,
          "exact_quote": "違い: silly は判断や行動が軽率で、子どもっぽくばかげていることを表す。sensible の「現実を踏まえた分別」と対照的である。  "
        }
      },
      {
        "item_id": "ant-ea4f2536cd8a",
        "stage1_axis": {
          "item_id": "ant-ea4f2536cd8a",
          "axis": "判断",
          "relation_type": "評価",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 147,
          "line_end": 147,
          "exact_quote": "・foolish  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 150,
          "line_end": 150,
          "exact_quote": "違い: foolish は結果を考えない愚かな判断を強く非難する語で、sensible の反対側に位置する。  "
        }
      },
      {
        "item_id": "ant-dfcdf1299624",
        "stage1_axis": {
          "item_id": "ant-dfcdf1299624",
          "axis": "判断",
          "relation_type": "評価",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 154,
          "line_end": 154,
          "exact_quote": "・impractical  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 157,
          "line_end": 157,
          "exact_quote": "違い: impractical は計画や提案などの実行可能性の不足に焦点を置く。人の分別全般の反意語ではないが、sensible plan などとは実用性の軸で対照をなす。  "
        }
      },
      {
        "item_id": "ant-11aa9f87d4f9",
        "stage1_axis": {
          "item_id": "ant-11aa9f87d4f9",
          "axis": "明確さ",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 296,
          "line_end": 296,
          "exact_quote": "・imperceptible  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 299,
          "line_end": 299,
          "exact_quote": "違い: imperceptible は差や変化が小さすぎて感じ取れないことを表し、sensible の「認識できる」という軸と直接対照をなす。  "
        }
      },
      {
        "item_id": "ant-8e3389b271b8",
        "stage1_axis": {
          "item_id": "ant-8e3389b271b8",
          "axis": "明確さ",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 303,
          "line_end": 303,
          "exact_quote": "・negligible  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 306,
          "line_end": 306,
          "exact_quote": "違い: negligible は重要性や影響の小ささに焦点がある。知覚できるかどうかを直接述べる語ではないが、sensible increase などの「無視できない程度」と量の軸で対照をなす。  "
        }
      },
      {
        "item_id": "ant-5963409236b4",
        "stage1_axis": {
          "item_id": "ant-5963409236b4",
          "axis": "知覚",
          "relation_type": "状態",
          "reason": ""
        },
        "sense_id": "sense:004",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 357,
          "line_end": 357,
          "exact_quote": "・insensible to 〈stimulus〉  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 360,
          "line_end": 360,
          "exact_quote": "違い: insensible to は痛み・熱などを知覚できないことを表し、この用法の sensible to と直接対照をなす。  "
        }
      },
      {
        "item_id": "ant-d73ee3c0122f",
        "stage1_axis": {
          "item_id": "ant-d73ee3c0122f",
          "axis": "知覚",
          "relation_type": "状態",
          "reason": ""
        },
        "sense_id": "sense:004",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 364,
          "line_end": 364,
          "exact_quote": "・impervious to 〈stimulus〉  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 367,
          "line_end": 367,
          "exact_quote": "違い: impervious to は単に知覚できないだけでなく、刺激や影響が作用しないことを強く表す。sensible to より遮断の含みが強い。  "
        }
      },
      {
        "item_id": "ant-e4cada59addd",
        "stage1_axis": {
          "item_id": "ant-e4cada59addd",
          "axis": "意識",
          "relation_type": "状態",
          "reason": ""
        },
        "sense_id": "sense:005",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 439,
          "line_end": 439,
          "exact_quote": "・unaware of something  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 442,
          "line_end": 442,
          "exact_quote": "違い: unaware of は認識がないことを直接表し、sensible of の「意識している」と対照をなす。  "
        }
      },
      {
        "item_id": "ant-33c897156157",
        "stage1_axis": {
          "item_id": "ant-33c897156157",
          "axis": "意識",
          "relation_type": "状態",
          "reason": ""
        },
        "sense_id": "sense:005",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 446,
          "line_end": 446,
          "exact_quote": "・oblivious to something  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 449,
          "line_end": 449,
          "exact_quote": "違い: oblivious to は気づいていない程度が強く、しばしば周囲への無関心を含む。sensible of と反対方向だが、単なる知識不足より強い。  "
        }
      }
    ],
    "antonym_axis_senses": [
      {
        "sense_id": "sense:001",
        "full_sense": [
          {
            "line": 40,
            "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
          },
          {
            "line": 42,
            "text": "【日本語訳・定義】感情だけで決めず、理由・経験・実際の条件を考えて、適切で無理のない判断や行動をすることを表す。人にも、考え・助言・計画・解決策などにも使い、話し手が妥当だと評価する含みがある。  "
          },
          {
            "line": 44,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 46,
            "text": "【レジスター/領域】標準語で、会話にも文章にも使える基本語。practical は実行可能性、reasonable は道理・公平さ、rational は感情を抑えた論理性に焦点を置きやすいのに対し、sensible は日常の分別と現実感をまとめて表す。  "
          },
          {
            "line": 48,
            "text": "【文法パターン】a sensible person/choice/decision/plan＝分別のある人・妥当な選択・判断・計画／sensible advice＝現実的で適切な助言／be sensible＝分別をもって行動する／be sensible about 〈money・risk・food〉＝〈お金・危険・食事〉について現実的に考える／it is sensible to do ＝～するのが妥当だ／it is sensible for someone to do ＝〈人〉が～するのが妥当だ／the sensible thing to do＝取るべき妥当な行動／be sensible enough to do ＝分別があるので～する。  "
          },
          {
            "line": 50,
            "text": "【コロケーション】"
          },
          {
            "line": 52,
            "text": "・a sensible decision  "
          },
          {
            "line": 53,
            "text": "用途: 条件や結果を考えたうえで、妥当な判断であることを表す。  "
          },
          {
            "line": 54,
            "text": "例: Taking the earlier train was a sensible decision.  "
          },
          {
            "line": 55,
            "text": "訳: 早い方の電車に乗ったのは妥当な判断だった。  "
          },
          {
            "line": 57,
            "text": "・a sensible approach to 〈problem〉  "
          },
          {
            "line": 58,
            "text": "用途: 問題に対して、現実的で無理のない取り組み方を示す。  "
          },
          {
            "line": 59,
            "text": "例: We need a sensible approach to reducing unnecessary costs.  "
          },
          {
            "line": 60,
            "text": "訳: 不要な費用を減らすには、現実的な取り組み方が必要だ。  "
          },
          {
            "line": 62,
            "text": "・sensible advice  "
          },
          {
            "line": 63,
            "text": "用途: 経験や事情に基づく、実行しやすい助言を表す。  "
          },
          {
            "line": 64,
            "text": "例: Her sensible advice helped me avoid a costly mistake.  "
          },
          {
            "line": 65,
            "text": "訳: 彼女の現実的な助言のおかげで、私は高くつく間違いを避けられた。  "
          },
          {
            "line": 67,
            "text": "・it is sensible to do  "
          },
          {
            "line": 68,
            "text": "用途: ある行動を取るのが分別にかなっていると述べる基本構文。  "
          },
          {
            "line": 69,
            "text": "例: It is sensible to keep a copy of the receipt.  "
          },
          {
            "line": 70,
            "text": "訳: 領収書の写しを保管しておくのが賢明だ。  "
          },
          {
            "line": 72,
            "text": "・it is sensible for someone to do  "
          },
          {
            "line": 73,
            "text": "用途: 特定の人がある行動をするのが妥当だと述べる。  "
          },
          {
            "line": 74,
            "text": "例: It would be sensible for you to check the figures again.  "
          },
          {
            "line": 75,
            "text": "訳: あなたがもう一度数字を確認するのが賢明だろう。  "
          },
          {
            "line": 77,
            "text": "・the sensible thing to do  "
          },
          {
            "line": 78,
            "text": "用途: いくつかの選択肢の中で、最も妥当な行動を指す。  "
          },
          {
            "line": 79,
            "text": "例: The sensible thing to do is wait until the weather improves.  "
          },
          {
            "line": 80,
            "text": "訳: 天候が回復するまで待つのが妥当な行動だ。  "
          },
          {
            "line": 82,
            "text": "・be sensible about 〈issue〉  "
          },
          {
            "line": 83,
            "text": "用途: 問題や資源について、感情的にならず現実的に考える。  "
          },
          {
            "line": 84,
            "text": "例: Please be sensible about how much equipment you bring.  "
          },
          {
            "line": 85,
            "text": "訳: どれだけ機材を持ってくるかは、現実的に考えてください。  "
          },
          {
            "line": 87,
            "text": "・be sensible enough to do  "
          },
          {
            "line": 88,
            "text": "用途: 分別があるため、危険や不利益を避ける行動を取ることを表す。  "
          },
          {
            "line": 89,
            "text": "例: He was sensible enough to ask for help before the problem grew.  "
          },
          {
            "line": 90,
            "text": "訳: 彼は問題が大きくなる前に助けを求めるだけの分別があった。  "
          },
          {
            "line": 92,
            "text": "【語法・注意】人を主語にした be sensible は「分別をもって行動する」、物事を主語にした a sensible plan は「妥当で現実的な計画」を表す。sensible は必ずしも「賢さ」や高い知能を評価する語ではなく、その場の条件に合った判断をほめる語である。  "
          },
          {
            "line": 94,
            "text": "【類義語】"
          },
          {
            "line": 96,
            "text": "・reasonable  "
          },
          {
            "line": 97,
            "text": "定義: 道理にかなった、妥当な、無理のない。  "
          },
          {
            "line": 98,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 99,
            "text": "違い: reasonable は判断・要求・価格などが公平で受け入れやすいことに焦点がある。sensible は現実の結果を考えて適切に行動する分別を強調しやすい。  "
          },
          {
            "line": 100,
            "text": "例: That seems like a reasonable compromise.  "
          },
          {
            "line": 101,
            "text": "訳: それは妥当な妥協案のように思える。  "
          },
          {
            "line": 103,
            "text": "・practical  "
          },
          {
            "line": 104,
            "text": "定義: 実際に役立ち、実行できる、実用的な。  "
          },
          {
            "line": 105,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 106,
            "text": "違い: practical は理論や見た目より実用性・実行可能性に焦点がある。sensible は実用性に加え、状況に応じた判断の適切さも表す。  "
          },
          {
            "line": 107,
            "text": "例: We chose a practical solution that fit the budget.  "
          },
          {
            "line": 108,
            "text": "訳: 私たちは予算に合う実用的な解決策を選んだ。  "
          },
          {
            "line": 110,
            "text": "・rational  "
          },
          {
            "line": 111,
            "text": "定義: 理性や論理に基づく、合理的な。  "
          },
          {
            "line": 112,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 113,
            "text": "違い: rational は感情や衝動ではなく、論理的な理由に基づくことを強調する。sensible の方が日常的で、生活上の分別にも使いやすい。  "
          },
          {
            "line": 114,
            "text": "例: There is no rational reason to reject the proposal.  "
          },
          {
            "line": 115,
            "text": "訳: その提案を拒む合理的な理由はない。  "
          },
          {
            "line": 117,
            "text": "・prudent  "
          },
          {
            "line": 118,
            "text": "定義: 将来の危険や損失を考えて慎重で賢明な。  "
          },
          {
            "line": 119,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 120,
            "text": "違い: prudent は特に危険・費用・将来の結果を避ける慎重さを含み、sensible より硬い。  "
          },
          {
            "line": 121,
            "text": "例: It would be prudent to set aside some emergency savings.  "
          },
          {
            "line": 122,
            "text": "訳: 緊急時のために貯蓄をいくらか取っておくのが賢明だろう。  "
          },
          {
            "line": 124,
            "text": "・wise  "
          },
          {
            "line": 125,
            "text": "定義: 経験や深い理解に基づいて、賢明な。  "
          },
          {
            "line": 126,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 127,
            "text": "違い: wise は長期的な洞察や人生経験まで含むことがある。sensible はもっと身近な状況での現実的な判断に焦点を置く。  "
          },
          {
            "line": 128,
            "text": "例: It was wise to discuss the risks before signing.  "
          },
          {
            "line": 129,
            "text": "訳: 署名する前に危険性を話し合ったのは賢明だった。  "
          },
          {
            "line": 131,
            "text": "・judicious  "
          },
          {
            "line": 132,
            "text": "定義: 判断力があり、慎重で適切な。  "
          },
          {
            "line": 133,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 134,
            "text": "違い: judicious は選択・配分・発言などを慎重に見極めたことを表す硬い語。sensible の方が一般的で親しみやすい。  "
          },
          {
            "line": 135,
            "text": "例: A judicious use of examples can clarify the argument.  "
          },
          {
            "line": 136,
            "text": "訳: 例を適切に使えば、その議論を明確にできる。  "
          },
          {
            "line": 138,
            "text": "【反意語】"
          },
          {
            "line": 140,
            "text": "・silly  "
          },
          {
            "line": 141,
            "text": "定義: 分別を欠いた、ばかげた。  "
          },
          {
            "line": 142,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 143,
            "text": "違い: silly は判断や行動が軽率で、子どもっぽくばかげていることを表す。sensible の「現実を踏まえた分別」と対照的である。  "
          },
          {
            "line": 144,
            "text": "例: It would be silly to ignore the warning.  "
          },
          {
            "line": 145,
            "text": "訳: その警告を無視するのはばかげている。  "
          },
          {
            "line": 147,
            "text": "・foolish  "
          },
          {
            "line": 148,
            "text": "定義: 判断力や分別を欠いた、愚かな。  "
          },
          {
            "line": 149,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 150,
            "text": "違い: foolish は結果を考えない愚かな判断を強く非難する語で、sensible の反対側に位置する。  "
          },
          {
            "line": 151,
            "text": "例: It was foolish to spend all the money at once.  "
          },
          {
            "line": 152,
            "text": "訳: お金を全部一度に使うのは愚かなことだった。  "
          },
          {
            "line": 154,
            "text": "・impractical  "
          },
          {
            "line": 155,
            "text": "定義: 実行しにくく、現実の条件に合わない。  "
          },
          {
            "line": 156,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 157,
            "text": "違い: impractical は計画や提案などの実行可能性の不足に焦点を置く。人の分別全般の反意語ではないが、sensible plan などとは実用性の軸で対照をなす。  "
          },
          {
            "line": 158,
            "text": "例: The design is attractive but impractical for daily use.  "
          },
          {
            "line": 159,
            "text": "訳: そのデザインは魅力的だが、日常使用には実用的でない。  "
          }
        ]
      },
      {
        "sense_id": "sense:003",
        "full_sense": [
          {
            "line": 230,
            "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
          },
          {
            "line": 232,
            "text": "【日本語訳・定義】差・変化・増減・量などが、感覚や判断によって認識できる程度にはっきりしていることを表す。現代の一般会話での「分別のある」という意味より形式的で、sensible difference や sensible increase のように、無視できない程度を述べる。  "
          },
          {
            "line": 234,
            "text": "【頻度】〈3/10〉  "
          },
          {
            "line": 236,
            "text": "【レジスター/領域】形式的・書き言葉寄りで、一般会話では noticeable、clear、appreciable などが自然なことが多い。辞書によっては「知覚できる」「かなりの」という別項目として扱われる。  "
          },
          {
            "line": 238,
            "text": "【文法パターン】a sensible difference＝感じ取れる明確な差／a sensible increase/decrease in something＝〈物事〉のかなりはっきりした増加・減少／a sensible change in something＝〈物事〉の認識できる変化／sensible 〈amount・degree〉＝無視できない程度の量・度合い。  "
          },
          {
            "line": 240,
            "text": "【コロケーション】"
          },
          {
            "line": 242,
            "text": "・a sensible difference  "
          },
          {
            "line": 243,
            "text": "用途: 2つの状態や結果の間に、認識できるほどの差があることを表す。  "
          },
          {
            "line": 244,
            "text": "例: The software update made a sensible difference to the loading time.  "
          },
          {
            "line": 245,
            "text": "訳: ソフトウェアの更新によって、読み込み時間に明らかな違いが出た。  "
          },
          {
            "line": 247,
            "text": "・a sensible increase in something  "
          },
          {
            "line": 248,
            "text": "用途: 数値や量が、認識できる程度に増えたことを形式的に表す。  "
          },
          {
            "line": 249,
            "text": "例: The policy led to a sensible increase in public access.  "
          },
          {
            "line": 250,
            "text": "訳: その政策によって、一般の利用可能性がはっきり増した。  "
          },
          {
            "line": 252,
            "text": "・a sensible reduction in something  "
          },
          {
            "line": 253,
            "text": "用途: 費用・危険・排出量などが、無視できない程度に減ったことを表す。  "
          },
          {
            "line": 254,
            "text": "例: The new process produced a sensible reduction in waste.  "
          },
          {
            "line": 255,
            "text": "訳: 新しい工程によって、廃棄物が明らかに減少した。  "
          },
          {
            "line": 257,
            "text": "・a sensible change in something  "
          },
          {
            "line": 258,
            "text": "用途: 状態や傾向に、認識できるほどの変化が起きたことを述べる。  "
          },
          {
            "line": 259,
            "text": "例: There has been a sensible change in the patient's condition.  "
          },
          {
            "line": 260,
            "text": "訳: 患者の状態には、はっきり分かる変化があった。  "
          },
          {
            "line": 262,
            "text": "【語法・注意】この用法の sensible は「妥当な」という意味ではなく、「感覚や判断に届くほど明らかな」という意味である。ただし、sensible amount は文脈によって「妥当な量」という1の意味にもなるため、差や増減の文脈で理解する。  "
          },
          {
            "line": 264,
            "text": "【類義語】"
          },
          {
            "line": 266,
            "text": "・perceptible  "
          },
          {
            "line": 267,
            "text": "定義: 感覚や心によって知覚できる、感じ取れる。  "
          },
          {
            "line": 268,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 269,
            "text": "違い: perceptible は知覚可能性を直接表す硬い語で、sensible のこの用法と最も近い。sensible には「かなりの」という評価が加わることがある。  "
          },
          {
            "line": 270,
            "text": "例: There was a perceptible change in the tone of the discussion.  "
          },
          {
            "line": 271,
            "text": "訳: 議論の雰囲気には感じ取れる変化があった。  "
          },
          {
            "line": 273,
            "text": "・noticeable  "
          },
          {
            "line": 274,
            "text": "定義: 見たり感じたりして気づくことができる、目立つ。  "
          },
          {
            "line": 275,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 276,
            "text": "違い: noticeable は日常的で、目や耳などで気づきやすいことに焦点がある。sensible のこの用法はより形式的で、量や程度にも使いやすい。  "
          },
          {
            "line": 277,
            "text": "例: There was a noticeable improvement in her balance.  "
          },
          {
            "line": 278,
            "text": "訳: 彼女のバランスには目立った改善があった。  "
          },
          {
            "line": 280,
            "text": "・appreciable  "
          },
          {
            "line": 281,
            "text": "定義: はっきり認められる、かなりの、無視できない。  "
          },
          {
            "line": 282,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 283,
            "text": "違い: appreciable は差・量・変化が評価上無視できないことを強調する。sensible と近いが、程度の大きさに焦点を置きやすい。  "
          },
          {
            "line": 284,
            "text": "例: The repair resulted in an appreciable reduction in noise.  "
          },
          {
            "line": 285,
            "text": "訳: 修理によって騒音がかなり減少した。  "
          },
          {
            "line": 287,
            "text": "・marked  "
          },
          {
            "line": 288,
            "text": "定義: はっきりした、顕著な。  "
          },
          {
            "line": 289,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 290,
            "text": "違い: marked は変化や差が目立つことを簡潔に示す。sensible は、認識できる程度に達したことをやや控えめに述べる。  "
          },
          {
            "line": 291,
            "text": "例: The study found a marked difference between the two groups.  "
          },
          {
            "line": 292,
            "text": "訳: その研究は、2つのグループの間に顕著な差があることを見いだした。  "
          },
          {
            "line": 294,
            "text": "【反意語】"
          },
          {
            "line": 296,
            "text": "・imperceptible  "
          },
          {
            "line": 297,
            "text": "定義: 感覚や心では知覚できない、気づけない。  "
          },
          {
            "line": 298,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 299,
            "text": "違い: imperceptible は差や変化が小さすぎて感じ取れないことを表し、sensible の「認識できる」という軸と直接対照をなす。  "
          },
          {
            "line": 300,
            "text": "例: The change in temperature was almost imperceptible.  "
          },
          {
            "line": 301,
            "text": "訳: 気温の変化はほとんど感じ取れないほどだった。  "
          },
          {
            "line": 303,
            "text": "・negligible  "
          },
          {
            "line": 304,
            "text": "定義: 小さすぎて考慮する必要がない、取るに足りない。  "
          },
          {
            "line": 305,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 306,
            "text": "違い: negligible は重要性や影響の小ささに焦点がある。知覚できるかどうかを直接述べる語ではないが、sensible increase などの「無視できない程度」と量の軸で対照をなす。  "
          },
          {
            "line": 307,
            "text": "例: The difference in cost is negligible.  "
          },
          {
            "line": 308,
            "text": "訳: 費用の差は取るに足りない。  "
          }
        ]
      },
      {
        "sense_id": "sense:004",
        "full_sense": [
          {
            "line": 310,
            "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
          },
          {
            "line": 312,
            "text": "【日本語訳・定義】痛み・熱・光などの外部刺激を、感覚器官や身体で受け取る能力があることを表す。現代の一般英語では sensitive to が普通で、sensible to は古風・形式的または専門的に響く。  "
          },
          {
            "line": 314,
            "text": "【頻度】〈2/10〉  "
          },
          {
            "line": 316,
            "text": "【レジスター/領域】低頻度の形式的・古風な用法。一般学習者が自分の知覚について述べる場合は、通常 be sensitive to 〈刺激〉を使う。sensible to pain は「痛みを感じ取れる」であり、1の「分別のある」とは別の意味である。  "
          },
          {
            "line": 318,
            "text": "【文法パターン】be sensible to 〈pain・heat・light〉＝〈痛み・熱・光〉を感じ取れる／become sensible to 〈stimulus〉＝〈刺激〉を知覚するようになる／sensible to the touch＝触れて感じ取れる。  "
          },
          {
            "line": 320,
            "text": "【コロケーション】"
          },
          {
            "line": 322,
            "text": "・be sensible to pain  "
          },
          {
            "line": 323,
            "text": "用途: 痛みを感覚として受け取る能力があることを、形式的に表す。  "
          },
          {
            "line": 324,
            "text": "例: The injured area remained sensible to pain after the procedure.  "
          },
          {
            "line": 325,
            "text": "訳: 処置後も、負傷した部位は痛みを感じ取る状態だった。  "
          },
          {
            "line": 327,
            "text": "・be sensible to heat  "
          },
          {
            "line": 328,
            "text": "用途: 熱を感じ取ることができることを述べる。  "
          },
          {
            "line": 329,
            "text": "例: The instrument is sensible to heat from a nearby flame.  "
          },
          {
            "line": 330,
            "text": "訳: その器具は近くの炎から出る熱を感知できる。  "
          },
          {
            "line": 332,
            "text": "・be sensible to light  "
          },
          {
            "line": 333,
            "text": "用途: 光を感知する性質があることを、古風または技術的に表す。  "
          },
          {
            "line": 334,
            "text": "例: The material is sensible to light and should be stored in the dark.  "
          },
          {
            "line": 335,
            "text": "訳: その素材は光を感知する性質があるので、暗所で保管すべきだ。  "
          },
          {
            "line": 337,
            "text": "【語法・注意】現代英語の sensitive to は「刺激を感じやすい」だけでなく、「影響を受けやすい」「気を悪くしやすい」も表せる。一方、sensible to はこの語義では主に感覚的な知覚を述べ、一般的な「敏感な」の言い換えとして自由に使えるわけではない。  "
          },
          {
            "line": 339,
            "text": "【類義語】"
          },
          {
            "line": 341,
            "text": "・sensitive to 〈stimulus〉  "
          },
          {
            "line": 342,
            "text": "定義: 〈刺激〉を感じ取る、またはその影響を受けやすい。  "
          },
          {
            "line": 343,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 344,
            "text": "違い: sensitive to は現代英語で普通の表現で、感覚的な知覚に加えて化学反応・感情・社会的影響にも使える。sensible to は形式的・古風で範囲が狭い。  "
          },
          {
            "line": 345,
            "text": "例: Some people are highly sensitive to bright light.  "
          },
          {
            "line": 346,
            "text": "訳: 明るい光に非常に敏感な人もいる。  "
          },
          {
            "line": 348,
            "text": "・responsive to 〈stimulus〉  "
          },
          {
            "line": 349,
            "text": "定義: 〈刺激〉に反応する、反応を示す。  "
          },
          {
            "line": 350,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 351,
            "text": "違い: responsive to は刺激を感じることより、それに反応や変化が生じることを強調する。sensible to はまず知覚可能性を表す。  "
          },
          {
            "line": 352,
            "text": "例: The sensor is responsive to small changes in pressure.  "
          },
          {
            "line": 353,
            "text": "訳: そのセンサーは圧力の小さな変化にも反応する。  "
          },
          {
            "line": 355,
            "text": "【反意語】"
          },
          {
            "line": 357,
            "text": "・insensible to 〈stimulus〉  "
          },
          {
            "line": 358,
            "text": "定義: 〈刺激〉を感じない、意識しない。  "
          },
          {
            "line": 359,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 360,
            "text": "違い: insensible to は痛み・熱などを知覚できないことを表し、この用法の sensible to と直接対照をなす。  "
          },
          {
            "line": 361,
            "text": "例: The tissue was insensible to light touch.  "
          },
          {
            "line": 362,
            "text": "訳: その組織は軽く触れても感じなかった。  "
          },
          {
            "line": 364,
            "text": "・impervious to 〈stimulus〉  "
          },
          {
            "line": 365,
            "text": "定義: 〈刺激・影響〉を通さず、受け付けない。  "
          },
          {
            "line": 366,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 367,
            "text": "違い: impervious to は単に知覚できないだけでなく、刺激や影響が作用しないことを強く表す。sensible to より遮断の含みが強い。  "
          },
          {
            "line": 368,
            "text": "例: The coating is impervious to heat and moisture.  "
          },
          {
            "line": 369,
            "text": "訳: そのコーティングは熱や湿気を通さない。  "
          }
        ]
      },
      {
        "sense_id": "sense:005",
        "full_sense": [
          {
            "line": 371,
            "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
          },
          {
            "line": 373,
            "text": "【日本語訳・定義】事実・危険・義務・誤り・親切などを心で認識し、強く意識していることを表す。通常 sensible of 〈名詞〉の形で使い、現代の会話では aware of、conscious of、grateful for などが自然なことが多い。  "
          },
          {
            "line": 375,
            "text": "【頻度】〈3/10〉  "
          },
          {
            "line": 377,
            "text": "【レジスター/領域】形式的・文学的で、古風な響きがある。sensible of the fact、sensible of one's error、sensible of someone's kindness のように、抽象的な事実や感情を意識していることに使う。  "
          },
          {
            "line": 379,
            "text": "【文法パターン】be sensible of 〈fact・danger・duty・error〉＝〈事実・危険・義務・誤り〉を意識している／be sensible of 〈kindness・benefit〉＝〈親切・恩恵〉を深く感じている／be deeply/keenly sensible of something＝～を深く・強く意識している／sensible of the fact that 〈節〉＝～という事実を認識している。  "
          },
          {
            "line": 381,
            "text": "【コロケーション】"
          },
          {
            "line": 383,
            "text": "・be sensible of 〈fact〉  "
          },
          {
            "line": 384,
            "text": "用途: ある事実を心で認識していることを、形式的に表す。  "
          },
          {
            "line": 385,
            "text": "例: She was sensible of the fact that her decision affected the whole team.  "
          },
          {
            "line": 386,
            "text": "訳: 彼女は、自分の決定がチーム全体に影響するという事実を意識していた。  "
          },
          {
            "line": 388,
            "text": "・be sensible of one's error  "
          },
          {
            "line": 389,
            "text": "用途: 自分の誤りに気づき、それを認識していることを表す。  "
          },
          {
            "line": 390,
            "text": "例: He soon became sensible of his error and apologized.  "
          },
          {
            "line": 391,
            "text": "訳: 彼はすぐに自分の誤りに気づき、謝罪した。  "
          },
          {
            "line": 393,
            "text": "・be sensible of someone's kindness  "
          },
          {
            "line": 394,
            "text": "用途: 人から受けた親切や恩恵を深く感じていることを表す。  "
          },
          {
            "line": 395,
            "text": "例: I am deeply sensible of your kindness during this difficult time.  "
          },
          {
            "line": 396,
            "text": "訳: この困難な時期にあなたが親切にしてくださったことを深く感じています。  "
          },
          {
            "line": 398,
            "text": "・be keenly sensible of something  "
          },
          {
            "line": 399,
            "text": "用途: 危険・責任・苦境などを強く意識していることを、硬い表現で述べる。  "
          },
          {
            "line": 400,
            "text": "例: The volunteers were keenly sensible of the risks involved.  "
          },
          {
            "line": 401,
            "text": "訳: ボランティアたちは、そこに伴う危険を強く意識していた。  "
          },
          {
            "line": 403,
            "text": "【語法・注意】sensible of は「～を意識している」であり、1の sensible「分別のある」とは意味が異なる。sensible to は4の「刺激を感じ取れる」と結びつきやすく、事実・恩恵への意識には sensible of を使う。現代的な文章では aware of や conscious of の方が普通である。  "
          },
          {
            "line": 405,
            "text": "辞書によっては、名詞 sensible「感覚で知覚できるもの」や音楽の用語 sensible「導音」を載せることがあるが、いずれも非常にまれで、一般学習者がまず覚える形容詞の用法ではないため、本文の独立した語義には含めない。  "
          },
          {
            "line": 407,
            "text": "【類義語】"
          },
          {
            "line": 409,
            "text": "・aware of something  "
          },
          {
            "line": 410,
            "text": "定義: 〈事実・状況・問題〉に気づいている、知っている。  "
          },
          {
            "line": 411,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 412,
            "text": "違い: aware of は現代英語で最も普通の「認識している」で、感情の深さを必ずしも含まない。sensible of は形式的で、強く感じている含みを持つことがある。  "
          },
          {
            "line": 413,
            "text": "例: Are you aware of the possible consequences?  "
          },
          {
            "line": 414,
            "text": "訳: 起こりうる結果を認識していますか。  "
          },
          {
            "line": 416,
            "text": "・conscious of something  "
          },
          {
            "line": 417,
            "text": "定義: 〈事実・存在・自分の行動〉を意識している。  "
          },
          {
            "line": 418,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 419,
            "text": "違い: conscious of は意識に上っていることや自覚を強調する。sensible of より現代的だが、文脈によっては「気にしている」という含みも出る。  "
          },
          {
            "line": 420,
            "text": "例: She was conscious of every movement in the quiet room.  "
          },
          {
            "line": 421,
            "text": "訳: 彼女は静かな部屋でのあらゆる動きを意識していた。  "
          },
          {
            "line": 423,
            "text": "・cognizant of something  "
          },
          {
            "line": 424,
            "text": "定義: 〈事実・問題・義務〉を十分に認識している。  "
          },
          {
            "line": 425,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 426,
            "text": "違い: cognizant of は非常に形式的で、事実を理解・把握していることに焦点がある。sensible of は認識に加えて感情的な受け止め方も表しうる。  "
          },
          {
            "line": 427,
            "text": "例: The committee is cognizant of the need for further evidence.  "
          },
          {
            "line": 428,
            "text": "訳: 委員会は、さらなる証拠が必要であることを十分に認識している。  "
          },
          {
            "line": 430,
            "text": "・mindful of something  "
          },
          {
            "line": 431,
            "text": "定義: 〈危険・影響・必要性〉を意識し、注意を払っている。  "
          },
          {
            "line": 432,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 433,
            "text": "違い: mindful of は認識したうえで注意深く行動する含みが強い。sensible of は単に気づいていることや、恩恵を感じていることにも使える。  "
          },
          {
            "line": 434,
            "text": "例: Please be mindful of the needs of other passengers.  "
          },
          {
            "line": 435,
            "text": "訳: 他の乗客のニーズに配慮してください。  "
          },
          {
            "line": 437,
            "text": "【反意語】"
          },
          {
            "line": 439,
            "text": "・unaware of something  "
          },
          {
            "line": 440,
            "text": "定義: 〈事実・状況〉に気づいていない、知らない。  "
          },
          {
            "line": 441,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 442,
            "text": "違い: unaware of は認識がないことを直接表し、sensible of の「意識している」と対照をなす。  "
          },
          {
            "line": 443,
            "text": "例: He was unaware of the rule when he submitted the form.  "
          },
          {
            "line": 444,
            "text": "訳: 彼はその用紙を提出したとき、その規則を知らなかった。  "
          },
          {
            "line": 446,
            "text": "・oblivious to something  "
          },
          {
            "line": 447,
            "text": "定義: 〈事実・危険・周囲の状況〉にまったく気づいていない。  "
          },
          {
            "line": 448,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 449,
            "text": "違い: oblivious to は気づいていない程度が強く、しばしば周囲への無関心を含む。sensible of と反対方向だが、単なる知識不足より強い。  "
          },
          {
            "line": 450,
            "text": "例: The driver seemed oblivious to the warning signs.  "
          },
          {
            "line": 451,
            "text": "訳: その運転手は警告標識にまったく気づいていないようだった。  "
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
