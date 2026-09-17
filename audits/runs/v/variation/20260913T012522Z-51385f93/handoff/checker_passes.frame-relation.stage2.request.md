# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`variation-20260913T012522Z-51385f93-frame-relation-reviewer`, declared_model=`gpt-6-pro`.

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
  "input_body_sha256": "f94b51a0c437869d997f727a89666bdfa4c5ffe575c78f10042998526972201c",
  "blind_request_sha256": "b02a5b32878bfdb488bb0f79ea02e12f8c87fc20f84a477ea60f4188ea0ad50c",
  "blind_record_sha256": "af4060ba9d12718cd02ecd00ab1b82c55cf083eadddee422f4bba00c1788bc88",
  "input_sections": {
    "sense_structure": [
      {
        "line": 43,
        "text": "1. 【名詞・不可算／可算】変化、変動、ばらつき"
      },
      {
        "line": 45,
        "text": "【日本語訳・定義】量・水準・品質・状態などが一定ではなく変わること、またはその変化の幅・個々の違いを表す。変動・ばらつきを総体として述べる場合は不可算が多く、個々の変化・差・型を数える場合は可算になることが多い。変化が望ましいか望ましくないかは、文脈によって決まり、variation 自体には必ずしも悪い評価はない。  "
      },
      {
        "line": 124,
        "text": "2. 【名詞・可算】基準から少し変えたもの、変形、別形"
      },
      {
        "line": 126,
        "text": "【日本語訳・定義】同じ基本的な考え方・型・作品・方法を保ちながら、内容や構成の一部を変えたものを表す。元と無関係な別物ではなく、「元のものを少し変えた版」という含みがある。`a variation on ...` は「…を土台にした変形・アレンジ」として特に重要である。  "
      },
      {
        "line": 196,
        "text": "3. 【名詞・不可算／可算・生物学・遺伝学・医学】集団内の個体差、変異"
      },
      {
        "line": 198,
        "text": "【日本語訳・定義】同じ種・集団に属する個体の間に見られる、遺伝的・構造的・機能的な差を表す。基準や平均からの逸脱を必須とせず、個体間に自然に存在する差を中立的に指す。言語・地域・社会層などの一般的な形式差は語義1で扱う。  "
      },
      {
        "line": 272,
        "text": "4. 【名詞・可算・音楽】変奏；（複数・作品全体）変奏曲"
      },
      {
        "line": 274,
        "text": "【日本語訳・定義】主題や旋律をもとに、旋律・和声・リズム・調性などを変化させて作る楽曲・楽章、またはその中の一つの展開を表す。単数の `a variation` は通常、一連の変奏のうちの一つの変奏を指し、`variations` 全体や作品全体を指す場合に「変奏曲」とする。主題との連続性を保つ場合が多いが、変化の仕方や主題の現れ方は作品によって異なる。  "
      },
      {
        "line": 320,
        "text": "5. 【名詞・可算・バレエ】ソロ演目、独舞"
      },
      {
        "line": 322,
        "text": "【日本語訳・定義】クラシック・バレエで、踊り手が一人で踊る独立した演目または場面を表す。特に pas de deux などの中で、男女それぞれのソロとして踊られる部分を指すことがある。音楽の変奏曲ではなく、舞踊作品上の演目名である。  "
      },
      {
        "line": 363,
        "text": "6. 【名詞・不可算・航海・地球科学・測量】磁気偏角"
      },
      {
        "line": 365,
        "text": "【日本語訳・定義】地球上のある地点で、真北と磁北がなす水平角、またはその方位差を表す。地域や時期によって異なるため、航海・測量・方位の補正で考慮される。  "
      }
    ],
    "frames": [
      {
        "line": 43,
        "text": "1. 【名詞・不可算／可算】変化、変動、ばらつき"
      },
      {
        "line": 51,
        "text": "【文法パターン】variation in 〈amount/level/quality〉＝〈量・水準・品質〉の変動／variation of 〈temperature/pressure〉＝〈温度・圧力〉の変化／variation between 〈A〉 and 〈B〉＝〈A〉と〈B〉の差／variation among 〈people/regions〉＝〈人・地域〉の間のばらつき／variation according to 〈a factor〉＝〈要因〉に応じた変化／the variation of 〈A〉 with 〈B〉＝〈B〉に伴う〈A〉の変化／show/reflect variation in something＝何かの変動を示す／take seasonal variation into account＝季節変動を考慮に入れる。  "
      },
      {
        "line": 124,
        "text": "2. 【名詞・可算】基準から少し変えたもの、変形、別形"
      },
      {
        "line": 132,
        "text": "【文法パターン】a variation on 〈the original design/a theme/a story/a recipe〉＝〈元の設計・主題・物語・レシピ〉を土台にした変形／a variation of 〈a method/a design〉＝〈方法・デザイン〉の別形／a variation from 〈the norm/standard/original〉＝〈基準・標準・原型〉からの相違やずれ／variation of/to 〈a contract〉＝契約の変更／variation clause＝契約変更条項／variation order＝契約・工事内容の変更指示／variations on a theme＝同じ主題を変形した複数の展開／a slight variation＝わずかな変形。  "
      },
      {
        "line": 196,
        "text": "3. 【名詞・不可算／可算・生物学・遺伝学・医学】集団内の個体差、変異"
      },
      {
        "line": 204,
        "text": "【文法パターン】genetic/biological variation＝遺伝的・生物学的変異／variation within 〈a species/group〉＝〈種・集団〉内の変異／variation among 〈individuals〉＝〈個体〉間の差／variation between 〈populations〉＝〈集団〉間の差／show variation in 〈a characteristic〉＝〈特徴〉に差を示す。  "
      },
      {
        "line": 272,
        "text": "4. 【名詞・可算・音楽】変奏；（複数・作品全体）変奏曲"
      },
      {
        "line": 280,
        "text": "【文法パターン】a variation on 〈a theme/melody〉＝〈主題・旋律〉に基づく変奏／a set of variations on 〈a theme〉＝〈主題〉による変奏曲集／theme and variations＝主題と変奏／play/perform a variation＝変奏を演奏する／variations by 〈a composer〉＝〈作曲家〉による複数の変奏・変奏曲。  "
      },
      {
        "line": 320,
        "text": "5. 【名詞・可算・バレエ】ソロ演目、独舞"
      },
      {
        "line": 328,
        "text": "【文法パターン】perform a variation＝ソロ演目を踊る／a classical ballet variation＝クラシック・バレエのソロ演目／a variation from 〈a ballet〉＝〈バレエ作品〉からのソロ演目／learn/rehearse a variation＝ソロ演目を習う・リハーサルする。  "
      },
      {
        "line": 363,
        "text": "6. 【名詞・不可算・航海・地球科学・測量】磁気偏角"
      },
      {
        "line": 371,
        "text": "【文法パターン】magnetic variation＝磁気偏角／magnetic variation at 〈a location〉＝〈地点〉の磁気偏角／account for magnetic variation＝磁気偏角を考慮する。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 43,
        "text": "1. 【名詞・不可算／可算】変化、変動、ばらつき"
      },
      {
        "line": 53,
        "text": "【コロケーション】"
      },
      {
        "line": 55,
        "text": "・considerable variation in something  "
      },
      {
        "line": 56,
        "text": "用途: 〈何か〉にかなり大きな差やばらつきがあることを表す。  "
      },
      {
        "line": 57,
        "text": "例: There is considerable variation in the time needed to complete the task.  "
      },
      {
        "line": 58,
        "text": "訳: その作業を終えるのに必要な時間にはかなりのばらつきがある。  "
      },
      {
        "line": 60,
        "text": "・slight variation in something  "
      },
      {
        "line": 61,
        "text": "用途: 基本的には同じだが、わずかな違いがあることを表す。  "
      },
      {
        "line": 62,
        "text": "例: The two samples showed only slight variation in color.  "
      },
      {
        "line": 63,
        "text": "訳: その2つの試料には色のわずかな違いしか見られなかった。  "
      },
      {
        "line": 65,
        "text": "・wide variation between 〈A〉 and 〈B〉  "
      },
      {
        "line": 66,
        "text": "用途: 2つの対象の値・状態・結果が大きく異なることを示す。  "
      },
      {
        "line": 67,
        "text": "例: The study found wide variation between schools in the use of digital devices.  "
      },
      {
        "line": 68,
        "text": "訳: その研究では、デジタル機器の使用について学校間に大きな差が見つかった。  "
      },
      {
        "line": 70,
        "text": "・seasonal variation in 〈demand/temperature〉  "
      },
      {
        "line": 71,
        "text": "用途: 季節によって繰り返し生じる需要や温度の変化を指す。  "
      },
      {
        "line": 72,
        "text": "例: The store adjusts its stock for seasonal variation in demand.  "
      },
      {
        "line": 73,
        "text": "訳: その店は需要の季節変動に合わせて在庫を調整する。  "
      },
      {
        "line": 75,
        "text": "・variation according to 〈a factor〉  "
      },
      {
        "line": 76,
        "text": "用途: 地域・条件・時間などの要因に応じて値が変わることを述べる。  "
      },
      {
        "line": 77,
        "text": "例: The survey found considerable variation according to age and region.  "
      },
      {
        "line": 78,
        "text": "訳: その調査では、年齢と地域によってかなりの差が見つかった。  "
      },
      {
        "line": 80,
        "text": "・the variation of 〈A〉 with 〈B〉  "
      },
      {
        "line": 81,
        "text": "用途: 〈B〉の変化に伴って〈A〉がどう変わるかという関係を、やや学術的に表す。  "
      },
      {
        "line": 82,
        "text": "例: The graph shows the variation of pressure with altitude.  "
      },
      {
        "line": 83,
        "text": "訳: そのグラフは高度に伴う圧力の変化を示している。  "
      },
      {
        "line": 85,
        "text": "・take 〈seasonal variation〉 into account  "
      },
      {
        "line": 86,
        "text": "用途: 予測や計画で、一定ではない季節要因を考慮する。  "
      },
      {
        "line": 87,
        "text": "例: The forecast takes seasonal variation into account.  "
      },
      {
        "line": 88,
        "text": "訳: その予測は季節変動を考慮に入れている。  "
      },
      {
        "line": 124,
        "text": "2. 【名詞・可算】基準から少し変えたもの、変形、別形"
      },
      {
        "line": 134,
        "text": "【コロケーション】"
      },
      {
        "line": 136,
        "text": "・a variation on a theme  "
      },
      {
        "line": 137,
        "text": "用途: 同じ中心的な考えや筋を保った別の展開を表す。音楽にも比喩にも使える。  "
      },
      {
        "line": 138,
        "text": "例: The novel is a clever variation on a familiar coming-of-age story.  "
      },
      {
        "line": 139,
        "text": "訳: その小説は、よく知られた成長物語を巧みに変形した作品だ。  "
      },
      {
        "line": 141,
        "text": "・a variation on 〈a traditional dish/a traditional story〉  "
      },
      {
        "line": 142,
        "text": "用途: 伝統的な料理や物語を少し変えたものを指す。  "
      },
      {
        "line": 143,
        "text": "例: This soup is a lighter variation on a traditional winter dish.  "
      },
      {
        "line": 144,
        "text": "訳: このスープは伝統的な冬の料理をより軽めにしたアレンジだ。  "
      },
      {
        "line": 146,
        "text": "・a variation of 〈method/design〉  "
      },
      {
        "line": 147,
        "text": "用途: 既存の方法や設計と基本は同じで、一部が異なる版を表す。  "
      },
      {
        "line": 148,
        "text": "例: The team tested a variation of the original method.  "
      },
      {
        "line": 149,
        "text": "訳: そのチームは元の方法を変形した手法を試した。  "
      },
      {
        "line": 151,
        "text": "・a slight variation in 〈wording/format〉  "
      },
      {
        "line": 152,
        "text": "用途: 表現や形式の小さな違いを、内容の同一性を保ったまま述べる。  "
      },
      {
        "line": 153,
        "text": "例: The instructions show a slight variation in wording.  "
      },
      {
        "line": 154,
        "text": "訳: その説明書には表現のわずかな違いが見られる。  "
      },
      {
        "line": 156,
        "text": "・a variation on the original design  "
      },
      {
        "line": 157,
        "text": "用途: 元の設計を土台にした別形・アレンジを表す。語義2の代表的な表現。  "
      },
      {
        "line": 158,
        "text": "例: This version is a useful variation on the original design.  "
      },
      {
        "line": 159,
        "text": "訳: この版は元の設計を土台にした有用なアレンジだ。  "
      },
      {
        "line": 161,
        "text": "・a variation from 〈the norm/standard〉  "
      },
      {
        "line": 162,
        "text": "用途: 基準・標準からの相違やずれを強調する。元のものを土台にした別形を中立的に指す場合は、`variation on` の方が典型的である。  "
      },
      {
        "line": 163,
        "text": "例: The revised procedure is a minor variation from the standard procedure.  "
      },
      {
        "line": 164,
        "text": "訳: 改訂された手順は、標準手順からわずかに異なる形になっている。  "
      },
      {
        "line": 166,
        "text": "・develop a variation on 〈an idea〉  "
      },
      {
        "line": 167,
        "text": "用途: 既存の考えを土台に、新しい展開を作ることを表す。  "
      },
      {
        "line": 168,
        "text": "例: The workshop asks students to develop a variation on the basic pattern.  "
      },
      {
        "line": 169,
        "text": "訳: その講習では、基本パターンを変形したものを学生に考案させる。  "
      },
      {
        "line": 196,
        "text": "3. 【名詞・不可算／可算・生物学・遺伝学・医学】集団内の個体差、変異"
      },
      {
        "line": 206,
        "text": "【コロケーション】"
      },
      {
        "line": 208,
        "text": "・genetic variation within 〈a species〉  "
      },
      {
        "line": 209,
        "text": "用途: 同じ種の個体間にある遺伝的な違いを表す。  "
      },
      {
        "line": 210,
        "text": "例: Genetic variation within a species can affect its response to disease.  "
      },
      {
        "line": 211,
        "text": "訳: 種内の遺伝的変異は、病気への反応に影響することがある。  "
      },
      {
        "line": 213,
        "text": "・genetic variation among 〈individuals〉  "
      },
      {
        "line": 214,
        "text": "用途: 個体ごとの遺伝的な違いが一様でないことを述べる。  "
      },
      {
        "line": 215,
        "text": "例: The study found substantial genetic variation among individuals in their response to the vaccine.  "
      },
      {
        "line": 216,
        "text": "訳: その研究では、ワクチンへの反応に個体間の大きな遺伝的差が見つかった。  "
      },
      {
        "line": 218,
        "text": "・variation within 〈a population〉  "
      },
      {
        "line": 219,
        "text": "用途: 同じ集団内で見られる、遺伝的・形態的・生理的などの個体差を表す。  "
      },
      {
        "line": 220,
        "text": "例: The study measured variation within a population over several generations.  "
      },
      {
        "line": 221,
        "text": "訳: その研究は、数世代にわたる集団内の変異を測定した。  "
      },
      {
        "line": 223,
        "text": "・genetic variation between 〈populations〉  "
      },
      {
        "line": 224,
        "text": "用途: 異なる集団の間にある遺伝的な違いを表す。  "
      },
      {
        "line": 225,
        "text": "例: The researchers compared genetic variation between populations living in different environments.  "
      },
      {
        "line": 226,
        "text": "訳: 研究者たちは、異なる環境に住む集団間の遺伝的変異を比較した。  "
      },
      {
        "line": 228,
        "text": "・genetic variation in 〈drug response〉  "
      },
      {
        "line": 229,
        "text": "用途: 遺伝的な違いによって薬への反応が異なることを表す。  "
      },
      {
        "line": 230,
        "text": "例: Genetic variation in drug response should be considered when interpreting the results.  "
      },
      {
        "line": 231,
        "text": "訳: 結果を解釈する際は、薬物反応における遺伝的変異を考慮すべきだ。  "
      },
      {
        "line": 233,
        "text": "・show variation in 〈a characteristic〉  "
      },
      {
        "line": 234,
        "text": "用途: 特定の特徴に個体差や形式差があることを、観察・調査結果として述べる。  "
      },
      {
        "line": 235,
        "text": "例: The samples show variation in leaf shape and size.  "
      },
      {
        "line": 236,
        "text": "訳: その試料には葉の形と大きさに違いが見られる。  "
      },
      {
        "line": 272,
        "text": "4. 【名詞・可算・音楽】変奏；（複数・作品全体）変奏曲"
      },
      {
        "line": 282,
        "text": "【コロケーション】"
      },
      {
        "line": 284,
        "text": "・a set of variations on 〈a theme〉  "
      },
      {
        "line": 285,
        "text": "用途: 1つの主題を順に変形した複数の楽曲からなる作品を表す。  "
      },
      {
        "line": 286,
        "text": "例: The concert opened with a set of variations on a folk melody.  "
      },
      {
        "line": 287,
        "text": "訳: その演奏会は民謡の旋律による変奏曲集で幕を開けた。  "
      },
      {
        "line": 289,
        "text": "・theme and variations  "
      },
      {
        "line": 290,
        "text": "用途: 主題を最初に示し、その後に複数の変奏を続ける形式を指す。  "
      },
      {
        "line": 291,
        "text": "例: The pianist chose a demanding theme and variations for the recital.  "
      },
      {
        "line": 292,
        "text": "訳: そのピアニストはリサイタルに、難度の高い主題と変奏曲を選んだ。  "
      },
      {
        "line": 294,
        "text": "・a variation on 〈a melody〉  "
      },
      {
        "line": 295,
        "text": "用途: ある旋律をもとにした、一連の変奏のうちの一つの変奏を指す。  "
      },
      {
        "line": 296,
        "text": "例: The pianist performed a variation on the melody with subtle rhythmic changes.  "
      },
      {
        "line": 297,
        "text": "訳: そのピアニストは、リズムを微妙に変えたその旋律の一つの変奏を演奏した。  "
      },
      {
        "line": 299,
        "text": "・play a variation  "
      },
      {
        "line": 300,
        "text": "用途: 演奏者が一連の変奏のうちの一つの変奏を演奏することを表す。  "
      },
      {
        "line": 301,
        "text": "例: She played the final variation with remarkable clarity.  "
      },
      {
        "line": 302,
        "text": "訳: 彼女は最後の変奏を見事な明瞭さで演奏した。  "
      },
      {
        "line": 304,
        "text": "・variations by 〈a composer〉  "
      },
      {
        "line": 305,
        "text": "用途: 特定の作曲家が作った変奏曲を示す。  "
      },
      {
        "line": 306,
        "text": "例: The program included variations by Beethoven and Brahms.  "
      },
      {
        "line": 307,
        "text": "訳: そのプログラムにはベートーベンとブラームスの変奏曲が含まれていた。  "
      },
      {
        "line": 320,
        "text": "5. 【名詞・可算・バレエ】ソロ演目、独舞"
      },
      {
        "line": 330,
        "text": "【コロケーション】"
      },
      {
        "line": 332,
        "text": "・perform a variation  "
      },
      {
        "line": 333,
        "text": "用途: バレエのソロ演目を舞台や審査で踊ることを表す。  "
      },
      {
        "line": 334,
        "text": "例: The dancer performed her variation with controlled, precise movements.  "
      },
      {
        "line": 335,
        "text": "訳: そのダンサーは抑制の効いた正確な動きでソロ演目を踊った。  "
      },
      {
        "line": 337,
        "text": "・a classical ballet variation  "
      },
      {
        "line": 338,
        "text": "用途: クラシック・バレエの定型的なソロ演目を指す。  "
      },
      {
        "line": 339,
        "text": "例: She is preparing a classical ballet variation for the competition.  "
      },
      {
        "line": 340,
        "text": "訳: 彼女はコンクールに向けてクラシック・バレエのソロ演目を準備している。  "
      },
      {
        "line": 342,
        "text": "・a variation from 〈a ballet〉  "
      },
      {
        "line": 343,
        "text": "用途: 特定のバレエ作品に含まれるソロ演目を示す。  "
      },
      {
        "line": 344,
        "text": "例: He chose a variation from The Sleeping Beauty for the audition.  "
      },
      {
        "line": 345,
        "text": "訳: 彼はオーディションに『眠れる森の美女』のソロ演目を選んだ。  "
      },
      {
        "line": 347,
        "text": "・rehearse a variation  "
      },
      {
        "line": 348,
        "text": "用途: 本番用のソロ演目を繰り返し練習することを表す。  "
      },
      {
        "line": 349,
        "text": "例: The students rehearsed a variation from the ballet before class.  "
      },
      {
        "line": 350,
        "text": "訳: 生徒たちは授業の前に、そのバレエ作品のソロ演目を練習した。  "
      },
      {
        "line": 363,
        "text": "6. 【名詞・不可算・航海・地球科学・測量】磁気偏角"
      },
      {
        "line": 373,
        "text": "【コロケーション】"
      },
      {
        "line": 375,
        "text": "・magnetic variation  "
      },
      {
        "line": 376,
        "text": "用途: 真北と磁北の方位差を、航海や測量で扱う専門表現。  "
      },
      {
        "line": 377,
        "text": "例: Navigators must account for magnetic variation when plotting a course.  "
      },
      {
        "line": 378,
        "text": "訳: 航海者は航路を設定する際に磁気偏角を考慮しなければならない。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 43,
        "text": "1. 【名詞・不可算／可算】変化、変動、ばらつき"
      },
      {
        "line": 92,
        "text": "【類義語】"
      },
      {
        "line": 94,
        "text": "・change  "
      },
      {
        "line": 95,
        "text": "定義: 状態・量・性質が別のものになること。  "
      },
      {
        "line": 96,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 97,
        "text": "違い: 最も広い語で、変化そのものに焦点を置く。variation は同じ型の範囲内での差や変動幅を示しやすい。  "
      },
      {
        "line": 98,
        "text": "例: The change in temperature was easy to notice.  "
      },
      {
        "line": 99,
        "text": "訳: 気温の変化は簡単に気づけた。  "
      },
      {
        "line": 101,
        "text": "・fluctuation  "
      },
      {
        "line": 102,
        "text": "定義: 数値や水準が上下を繰り返す変動。  "
      },
      {
        "line": 103,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 104,
        "text": "違い: 価格・為替・体温などの上下動を強く含む。variation は一方向の変化や対象間のばらつきにも使える。  "
      },
      {
        "line": 105,
        "text": "例: Daily fluctuations in demand make planning difficult.  "
      },
      {
        "line": 106,
        "text": "訳: 需要の日々の変動は計画を難しくする。  "
      },
      {
        "line": 108,
        "text": "・difference  "
      },
      {
        "line": 109,
        "text": "定義: 2つ以上のものが同じでない点や、その隔たり。  "
      },
      {
        "line": 110,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 111,
        "text": "違い: 比較対象間の差に焦点を置く。variation は基準からの変化や同種の複数対象のばらつきにも使う。  "
      },
      {
        "line": 112,
        "text": "例: There is a clear difference between the two measurements.  "
      },
      {
        "line": 113,
        "text": "訳: その2つの測定値には明確な差がある。  "
      },
      {
        "line": 115,
        "text": "【反意語】"
      },
      {
        "line": 117,
        "text": "・uniformity  "
      },
      {
        "line": 118,
        "text": "定義: 対象の間に差がほとんどなく、同じ状態や性質がそろっていること。  "
      },
      {
        "line": 119,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 120,
        "text": "違い: variation が差やばらつきを指すのに対し、uniformity は一様である状態を指す。  "
      },
      {
        "line": 121,
        "text": "例: The process aims to improve uniformity across all factories.  "
      },
      {
        "line": 122,
        "text": "訳: その工程は全工場での一様性を高めることを目指している。  "
      },
      {
        "line": 124,
        "text": "2. 【名詞・可算】基準から少し変えたもの、変形、別形"
      },
      {
        "line": 173,
        "text": "【類義語】"
      },
      {
        "line": 175,
        "text": "・variant  "
      },
      {
        "line": 176,
        "text": "定義: 同じ種類のものから分かれた、少し異なる形や型。  "
      },
      {
        "line": 177,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 178,
        "text": "違い: variant は別形そのものを簡潔に指し、医学・生物・言語などで標準形との差を分類する語としても使う。variation は変形の過程や関係も表しやすい。  "
      },
      {
        "line": 179,
        "text": "例: The researchers compared regional variants of the expression.  "
      },
      {
        "line": 180,
        "text": "訳: 研究者たちはその表現の地域別の異形を比較した。  "
      },
      {
        "line": 182,
        "text": "・version  "
      },
      {
        "line": 183,
        "text": "定義: 同じものの異なる版・形態・編集結果。  "
      },
      {
        "line": 184,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 185,
        "text": "違い: version は製品・文書・作品の版を中立的に指す。variation は元の型を部分的に変えたという関係をより強く示す。  "
      },
      {
        "line": 186,
        "text": "例: Please use the latest version of the report.  "
      },
      {
        "line": 187,
        "text": "訳: 報告書の最新版を使ってください。  "
      },
      {
        "line": 189,
        "text": "・modification  "
      },
      {
        "line": 190,
        "text": "定義: 目的に合わせて既存のものに加えた変更・改変。  "
      },
      {
        "line": 191,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 192,
        "text": "違い: modification は意図的な改変という行為・結果に焦点を置き、variation は自然に生じた差や創作上の変形にも使う。  "
      },
      {
        "line": 193,
        "text": "例: The device requires a minor modification to fit the new component.  "
      },
      {
        "line": 194,
        "text": "訳: その装置は新しい部品に合うよう、少し改変する必要がある。  "
      },
      {
        "line": 196,
        "text": "3. 【名詞・不可算／可算・生物学・遺伝学・医学】集団内の個体差、変異"
      },
      {
        "line": 240,
        "text": "【類義語】"
      },
      {
        "line": 242,
        "text": "・diversity  "
      },
      {
        "line": 243,
        "text": "定義: 集団や範囲の中に異なる種類・特徴が存在すること。  "
      },
      {
        "line": 244,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 245,
        "text": "違い: diversity は多様性の存在や価値に焦点を置き、variation は同じ集団内でどの特徴がどの程度異なるかを分析する語として使いやすい。  "
      },
      {
        "line": 246,
        "text": "例: The forest supports remarkable biological diversity.  "
      },
      {
        "line": 247,
        "text": "訳: その森林は際立った生物多様性を支えている。  "
      },
      {
        "line": 249,
        "text": "・difference  "
      },
      {
        "line": 250,
        "text": "定義: 2つ以上の個体・形式・集団が同じでない点。  "
      },
      {
        "line": 251,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 252,
        "text": "違い: difference は比較結果を一般に表し、variation は同じ種・体系の内部で生じる差や分布を含意しやすい。  "
      },
      {
        "line": 253,
        "text": "例: The researchers recorded differences in color between the populations.  "
      },
      {
        "line": 254,
        "text": "訳: 研究者たちは集団間の色の違いを記録した。  "
      },
      {
        "line": 256,
        "text": "・deviation  "
      },
      {
        "line": 257,
        "text": "定義: 基準・平均・通常の状態から外れること。  "
      },
      {
        "line": 258,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 259,
        "text": "違い: deviation は基準からの逸脱に焦点があり、通常から外れているという含みを帯びやすい。variation は中立的な個体差にも使う。  "
      },
      {
        "line": 260,
        "text": "例: The measurement showed a small deviation from the expected value.  "
      },
      {
        "line": 261,
        "text": "訳: その測定値には予想値からの小さなずれがあった。  "
      },
      {
        "line": 263,
        "text": "【反意語】"
      },
      {
        "line": 265,
        "text": "・homogeneity  "
      },
      {
        "line": 266,
        "text": "定義: 集団や資料の構成要素が互いによく似ていて、一様であること。  "
      },
      {
        "line": 267,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 268,
        "text": "違い: variation が内部の差を指すのに対し、homogeneity は内部の差が小さい状態を指す。  "
      },
      {
        "line": 269,
        "text": "例: The analysis assumes homogeneity within each group.  "
      },
      {
        "line": 270,
        "text": "訳: その分析は各集団内が均質であると仮定している。  "
      },
      {
        "line": 272,
        "text": "4. 【名詞・可算・音楽】変奏；（複数・作品全体）変奏曲"
      },
      {
        "line": 311,
        "text": "【類義語】"
      },
      {
        "line": 313,
        "text": "・reworking  "
      },
      {
        "line": 314,
        "text": "定義: 既存の主題・作品・素材を改作して、別の形に仕上げたもの。  "
      },
      {
        "line": 315,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 316,
        "text": "違い: reworking は改作の行為や結果に焦点を置き、音楽の variation ほど一定の形式や主題との反復関係を必須としない。  "
      },
      {
        "line": 317,
        "text": "例: The composer presented a bold reworking of the old melody.  "
      },
      {
        "line": 318,
        "text": "訳: その作曲家は古い旋律を大胆に改作した作品を発表した。  "
      },
      {
        "line": 320,
        "text": "5. 【名詞・可算・バレエ】ソロ演目、独舞"
      },
      {
        "line": 354,
        "text": "【類義語】"
      },
      {
        "line": 356,
        "text": "・solo  "
      },
      {
        "line": 357,
        "text": "定義: 一人で行う演奏・踊り・演技、またはその演目。  "
      },
      {
        "line": 358,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 359,
        "text": "違い: solo は一人で行うこと全般を表す。ballet の variation は、特定の作品・伝統に属する独舞の演目という専門性が加わる。  "
      },
      {
        "line": 360,
        "text": "例: The dancer performed a solo at the end of the show.  "
      },
      {
        "line": 361,
        "text": "訳: そのダンサーは公演の最後にソロを踊った。  "
      },
      {
        "line": 363,
        "text": "6. 【名詞・不可算・航海・地球科学・測量】磁気偏角"
      },
      {
        "line": 382,
        "text": "【類義語】"
      },
      {
        "line": 384,
        "text": "・magnetic declination  "
      },
      {
        "line": 385,
        "text": "定義: 真北と磁北の方向の差、またはその角度。  "
      },
      {
        "line": 386,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 387,
        "text": "違い: magnetic declination は現在の地球科学・航海で一般的な用語で、magnetic variation は同じ概念を表す別称として使われる。  "
      },
      {
        "line": 388,
        "text": "例: The chart gives the magnetic declination for the harbor.  "
      },
      {
        "line": 389,
        "text": "訳: その海図はその港の磁気偏角を示している。  "
      }
    ],
    "antonym_axis_items": [
      {
        "item_id": "ant-e33b31a1b0ea",
        "stage1_axis": {
          "item_id": "ant-e33b31a1b0ea",
          "axis": "差異",
          "relation_type": "程度",
          "reason": "変化の幅や個々の違いと、差がほとんどない状態が差の大きさを軸に対立する。"
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 117,
          "line_end": 117,
          "exact_quote": "・uniformity  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 120,
          "line_end": 120,
          "exact_quote": "違い: variation が差やばらつきを指すのに対し、uniformity は一様である状態を指す。  "
        }
      },
      {
        "item_id": "ant-8a1cd6b0b0fd",
        "stage1_axis": {
          "item_id": "ant-8a1cd6b0b0fd",
          "axis": "個体差",
          "relation_type": "程度",
          "reason": "個体間の遺伝的・構造的・機能的な差と、構成要素がよく似た状態が差の大きさを軸に対立する。"
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 265,
          "line_end": 265,
          "exact_quote": "・homogeneity  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 268,
          "line_end": 268,
          "exact_quote": "違い: variation が内部の差を指すのに対し、homogeneity は内部の差が小さい状態を指す。  "
        }
      }
    ],
    "antonym_axis_senses": [
      {
        "sense_id": "sense:001",
        "full_sense": [
          {
            "line": 43,
            "text": "1. 【名詞・不可算／可算】変化、変動、ばらつき"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】量・水準・品質・状態などが一定ではなく変わること、またはその変化の幅・個々の違いを表す。変動・ばらつきを総体として述べる場合は不可算が多く、個々の変化・差・型を数える場合は可算になることが多い。変化が望ましいか望ましくないかは、文脈によって決まり、variation 自体には必ずしも悪い評価はない。  "
          },
          {
            "line": 47,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 49,
            "text": "【レジスター/領域】標準語。日常会話にも使うが、文章・報道・ビジネス・学術で特に頻出する。データや価格では「変動」「ばらつき」、地域・人・意見では「差異」「違い」と訳し分ける。統計では variation はばらつき一般または変化量を指し、variance は平均からの偏差の二乗平均という特定の統計量であるため、両語は自動的に置き換えない。  "
          },
          {
            "line": 51,
            "text": "【文法パターン】variation in 〈amount/level/quality〉＝〈量・水準・品質〉の変動／variation of 〈temperature/pressure〉＝〈温度・圧力〉の変化／variation between 〈A〉 and 〈B〉＝〈A〉と〈B〉の差／variation among 〈people/regions〉＝〈人・地域〉の間のばらつき／variation according to 〈a factor〉＝〈要因〉に応じた変化／the variation of 〈A〉 with 〈B〉＝〈B〉に伴う〈A〉の変化／show/reflect variation in something＝何かの変動を示す／take seasonal variation into account＝季節変動を考慮に入れる。  "
          },
          {
            "line": 53,
            "text": "【コロケーション】"
          },
          {
            "line": 55,
            "text": "・considerable variation in something  "
          },
          {
            "line": 56,
            "text": "用途: 〈何か〉にかなり大きな差やばらつきがあることを表す。  "
          },
          {
            "line": 57,
            "text": "例: There is considerable variation in the time needed to complete the task.  "
          },
          {
            "line": 58,
            "text": "訳: その作業を終えるのに必要な時間にはかなりのばらつきがある。  "
          },
          {
            "line": 60,
            "text": "・slight variation in something  "
          },
          {
            "line": 61,
            "text": "用途: 基本的には同じだが、わずかな違いがあることを表す。  "
          },
          {
            "line": 62,
            "text": "例: The two samples showed only slight variation in color.  "
          },
          {
            "line": 63,
            "text": "訳: その2つの試料には色のわずかな違いしか見られなかった。  "
          },
          {
            "line": 65,
            "text": "・wide variation between 〈A〉 and 〈B〉  "
          },
          {
            "line": 66,
            "text": "用途: 2つの対象の値・状態・結果が大きく異なることを示す。  "
          },
          {
            "line": 67,
            "text": "例: The study found wide variation between schools in the use of digital devices.  "
          },
          {
            "line": 68,
            "text": "訳: その研究では、デジタル機器の使用について学校間に大きな差が見つかった。  "
          },
          {
            "line": 70,
            "text": "・seasonal variation in 〈demand/temperature〉  "
          },
          {
            "line": 71,
            "text": "用途: 季節によって繰り返し生じる需要や温度の変化を指す。  "
          },
          {
            "line": 72,
            "text": "例: The store adjusts its stock for seasonal variation in demand.  "
          },
          {
            "line": 73,
            "text": "訳: その店は需要の季節変動に合わせて在庫を調整する。  "
          },
          {
            "line": 75,
            "text": "・variation according to 〈a factor〉  "
          },
          {
            "line": 76,
            "text": "用途: 地域・条件・時間などの要因に応じて値が変わることを述べる。  "
          },
          {
            "line": 77,
            "text": "例: The survey found considerable variation according to age and region.  "
          },
          {
            "line": 78,
            "text": "訳: その調査では、年齢と地域によってかなりの差が見つかった。  "
          },
          {
            "line": 80,
            "text": "・the variation of 〈A〉 with 〈B〉  "
          },
          {
            "line": 81,
            "text": "用途: 〈B〉の変化に伴って〈A〉がどう変わるかという関係を、やや学術的に表す。  "
          },
          {
            "line": 82,
            "text": "例: The graph shows the variation of pressure with altitude.  "
          },
          {
            "line": 83,
            "text": "訳: そのグラフは高度に伴う圧力の変化を示している。  "
          },
          {
            "line": 85,
            "text": "・take 〈seasonal variation〉 into account  "
          },
          {
            "line": 86,
            "text": "用途: 予測や計画で、一定ではない季節要因を考慮する。  "
          },
          {
            "line": 87,
            "text": "例: The forecast takes seasonal variation into account.  "
          },
          {
            "line": 88,
            "text": "訳: その予測は季節変動を考慮に入れている。  "
          },
          {
            "line": 90,
            "text": "【語法・注意】variation は変動やばらつきを総体として述べるときは不可算が多く、a variation/variations は個々の変化・差・型を数えるときに使われることが多い。`variation in prices` は価格の変動、`variations in prices` は複数の価格差・変動の例を指しやすい。`difference` は2つ以上の対象の差に焦点を置くが、variation は基準からの変化や集団全体のばらつきにも使える。`variety` は選択肢や種類の豊富さを表すことが多く、単なる数値の変動には通常 variation を使う。  "
          },
          {
            "line": 92,
            "text": "【類義語】"
          },
          {
            "line": 94,
            "text": "・change  "
          },
          {
            "line": 95,
            "text": "定義: 状態・量・性質が別のものになること。  "
          },
          {
            "line": 96,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 97,
            "text": "違い: 最も広い語で、変化そのものに焦点を置く。variation は同じ型の範囲内での差や変動幅を示しやすい。  "
          },
          {
            "line": 98,
            "text": "例: The change in temperature was easy to notice.  "
          },
          {
            "line": 99,
            "text": "訳: 気温の変化は簡単に気づけた。  "
          },
          {
            "line": 101,
            "text": "・fluctuation  "
          },
          {
            "line": 102,
            "text": "定義: 数値や水準が上下を繰り返す変動。  "
          },
          {
            "line": 103,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 104,
            "text": "違い: 価格・為替・体温などの上下動を強く含む。variation は一方向の変化や対象間のばらつきにも使える。  "
          },
          {
            "line": 105,
            "text": "例: Daily fluctuations in demand make planning difficult.  "
          },
          {
            "line": 106,
            "text": "訳: 需要の日々の変動は計画を難しくする。  "
          },
          {
            "line": 108,
            "text": "・difference  "
          },
          {
            "line": 109,
            "text": "定義: 2つ以上のものが同じでない点や、その隔たり。  "
          },
          {
            "line": 110,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 111,
            "text": "違い: 比較対象間の差に焦点を置く。variation は基準からの変化や同種の複数対象のばらつきにも使う。  "
          },
          {
            "line": 112,
            "text": "例: There is a clear difference between the two measurements.  "
          },
          {
            "line": 113,
            "text": "訳: その2つの測定値には明確な差がある。  "
          },
          {
            "line": 115,
            "text": "【反意語】"
          },
          {
            "line": 117,
            "text": "・uniformity  "
          },
          {
            "line": 118,
            "text": "定義: 対象の間に差がほとんどなく、同じ状態や性質がそろっていること。  "
          },
          {
            "line": 119,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 120,
            "text": "違い: variation が差やばらつきを指すのに対し、uniformity は一様である状態を指す。  "
          },
          {
            "line": 121,
            "text": "例: The process aims to improve uniformity across all factories.  "
          },
          {
            "line": 122,
            "text": "訳: その工程は全工場での一様性を高めることを目指している。  "
          }
        ]
      },
      {
        "sense_id": "sense:003",
        "full_sense": [
          {
            "line": 196,
            "text": "3. 【名詞・不可算／可算・生物学・遺伝学・医学】集団内の個体差、変異"
          },
          {
            "line": 198,
            "text": "【日本語訳・定義】同じ種・集団に属する個体の間に見られる、遺伝的・構造的・機能的な差を表す。基準や平均からの逸脱を必須とせず、個体間に自然に存在する差を中立的に指す。言語・地域・社会層などの一般的な形式差は語義1で扱う。  "
          },
          {
            "line": 200,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 202,
            "text": "【レジスター/領域】生物学、遺伝学、医学などで使う学術語。一般文脈の「違い」より、同じ種・集団の内部に生じる個体差や、その分布を意識させる。  "
          },
          {
            "line": 204,
            "text": "【文法パターン】genetic/biological variation＝遺伝的・生物学的変異／variation within 〈a species/group〉＝〈種・集団〉内の変異／variation among 〈individuals〉＝〈個体〉間の差／variation between 〈populations〉＝〈集団〉間の差／show variation in 〈a characteristic〉＝〈特徴〉に差を示す。  "
          },
          {
            "line": 206,
            "text": "【コロケーション】"
          },
          {
            "line": 208,
            "text": "・genetic variation within 〈a species〉  "
          },
          {
            "line": 209,
            "text": "用途: 同じ種の個体間にある遺伝的な違いを表す。  "
          },
          {
            "line": 210,
            "text": "例: Genetic variation within a species can affect its response to disease.  "
          },
          {
            "line": 211,
            "text": "訳: 種内の遺伝的変異は、病気への反応に影響することがある。  "
          },
          {
            "line": 213,
            "text": "・genetic variation among 〈individuals〉  "
          },
          {
            "line": 214,
            "text": "用途: 個体ごとの遺伝的な違いが一様でないことを述べる。  "
          },
          {
            "line": 215,
            "text": "例: The study found substantial genetic variation among individuals in their response to the vaccine.  "
          },
          {
            "line": 216,
            "text": "訳: その研究では、ワクチンへの反応に個体間の大きな遺伝的差が見つかった。  "
          },
          {
            "line": 218,
            "text": "・variation within 〈a population〉  "
          },
          {
            "line": 219,
            "text": "用途: 同じ集団内で見られる、遺伝的・形態的・生理的などの個体差を表す。  "
          },
          {
            "line": 220,
            "text": "例: The study measured variation within a population over several generations.  "
          },
          {
            "line": 221,
            "text": "訳: その研究は、数世代にわたる集団内の変異を測定した。  "
          },
          {
            "line": 223,
            "text": "・genetic variation between 〈populations〉  "
          },
          {
            "line": 224,
            "text": "用途: 異なる集団の間にある遺伝的な違いを表す。  "
          },
          {
            "line": 225,
            "text": "例: The researchers compared genetic variation between populations living in different environments.  "
          },
          {
            "line": 226,
            "text": "訳: 研究者たちは、異なる環境に住む集団間の遺伝的変異を比較した。  "
          },
          {
            "line": 228,
            "text": "・genetic variation in 〈drug response〉  "
          },
          {
            "line": 229,
            "text": "用途: 遺伝的な違いによって薬への反応が異なることを表す。  "
          },
          {
            "line": 230,
            "text": "例: Genetic variation in drug response should be considered when interpreting the results.  "
          },
          {
            "line": 231,
            "text": "訳: 結果を解釈する際は、薬物反応における遺伝的変異を考慮すべきだ。  "
          },
          {
            "line": 233,
            "text": "・show variation in 〈a characteristic〉  "
          },
          {
            "line": 234,
            "text": "用途: 特定の特徴に個体差や形式差があることを、観察・調査結果として述べる。  "
          },
          {
            "line": 235,
            "text": "例: The samples show variation in leaf shape and size.  "
          },
          {
            "line": 236,
            "text": "訳: その試料には葉の形と大きさに違いが見られる。  "
          },
          {
            "line": 238,
            "text": "【語法・注意】生物学の `variation` は、集団内の差という現象にも、その差を示す特徴にも使われる。基準からの逸脱を必ずしも含まない点で、`deviation` より中立的である。`mutation` は遺伝物質の配列に起きる変化、`genetic variation` は個体・集団間に観察される遺伝的差の状態・分布を指し、mutation は variation の原因の一つである。両語は同義ではない。  "
          },
          {
            "line": 240,
            "text": "【類義語】"
          },
          {
            "line": 242,
            "text": "・diversity  "
          },
          {
            "line": 243,
            "text": "定義: 集団や範囲の中に異なる種類・特徴が存在すること。  "
          },
          {
            "line": 244,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 245,
            "text": "違い: diversity は多様性の存在や価値に焦点を置き、variation は同じ集団内でどの特徴がどの程度異なるかを分析する語として使いやすい。  "
          },
          {
            "line": 246,
            "text": "例: The forest supports remarkable biological diversity.  "
          },
          {
            "line": 247,
            "text": "訳: その森林は際立った生物多様性を支えている。  "
          },
          {
            "line": 249,
            "text": "・difference  "
          },
          {
            "line": 250,
            "text": "定義: 2つ以上の個体・形式・集団が同じでない点。  "
          },
          {
            "line": 251,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 252,
            "text": "違い: difference は比較結果を一般に表し、variation は同じ種・体系の内部で生じる差や分布を含意しやすい。  "
          },
          {
            "line": 253,
            "text": "例: The researchers recorded differences in color between the populations.  "
          },
          {
            "line": 254,
            "text": "訳: 研究者たちは集団間の色の違いを記録した。  "
          },
          {
            "line": 256,
            "text": "・deviation  "
          },
          {
            "line": 257,
            "text": "定義: 基準・平均・通常の状態から外れること。  "
          },
          {
            "line": 258,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 259,
            "text": "違い: deviation は基準からの逸脱に焦点があり、通常から外れているという含みを帯びやすい。variation は中立的な個体差にも使う。  "
          },
          {
            "line": 260,
            "text": "例: The measurement showed a small deviation from the expected value.  "
          },
          {
            "line": 261,
            "text": "訳: その測定値には予想値からの小さなずれがあった。  "
          },
          {
            "line": 263,
            "text": "【反意語】"
          },
          {
            "line": 265,
            "text": "・homogeneity  "
          },
          {
            "line": 266,
            "text": "定義: 集団や資料の構成要素が互いによく似ていて、一様であること。  "
          },
          {
            "line": 267,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 268,
            "text": "違い: variation が内部の差を指すのに対し、homogeneity は内部の差が小さい状態を指す。  "
          },
          {
            "line": 269,
            "text": "例: The analysis assumes homogeneity within each group.  "
          },
          {
            "line": 270,
            "text": "訳: その分析は各集団内が均質であると仮定している。  "
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
