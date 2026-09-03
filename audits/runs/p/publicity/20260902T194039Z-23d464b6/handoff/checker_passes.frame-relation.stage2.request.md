# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`01a063ad-98d2-7430-8a73-13aa483c109e`, declared_model=`gpt-5`.

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
  "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
  "blind_request_sha256": "8e9b4d7dc0f727c40f58097f13aeb2bc780ac7c0d65ce94d7a482d33f740b124",
  "blind_record_sha256": "19206392037543fe2be8499c9b3fb24c77339a105bbbe24d932e6fa4b2297b41",
  "input_sections": {
    "sense_structure": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 32,
        "text": "【日本語訳・定義】人・企業・作品・出来事などが、新聞、テレビなどのメディアを通じて世間から受ける注目や報道上の露出。好意的とは限らず、good/bad/negative/unwanted publicity のように評価を添えられる。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 103,
        "text": "【日本語訳・定義】人、商品、作品、行事、主張などに世間の関心を集めるために行う広報・宣伝活動。広告に限らず、情報提供などの広報手段を含み得る。ここでは世間の注目を集める側の活動・手段に焦点を置く。  "
      }
    ],
    "frames": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 38,
        "text": "【文法パターン】gain/receive publicity＝世間の注目・報道を得る／widespread publicity＝広範な世間の注目・報道／good/bad/negative/unwanted publicity＝好意的な・悪い・否定的な・望まない注目／shun publicity＝世間の注目・報道を避ける  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 109,
        "text": "【文法パターン】publicity for/about 〈映画・商品・行事〉＝～に関する広報・注目／advance publicity for 〈発売・行事〉＝発売・行事の事前広報／publicity campaign/material/stunt＝宣伝キャンペーン・資料・仕掛け  "
      }
    ],
    "collocations_examples": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 40,
        "text": "【コロケーション】"
      },
      {
        "line": 42,
        "text": "・gain/receive publicity  "
      },
      {
        "line": 43,
        "text": "用途: 人・団体・作品・出来事が世間の注目や報道を受けることを表す。  "
      },
      {
        "line": 44,
        "text": "例: The charity gained widespread publicity after the athlete supported its campaign.  "
      },
      {
        "line": 45,
        "text": "訳: その慈善団体は、その選手がキャンペーンを支持した後、広く世間の注目を浴びた。  "
      },
      {
        "line": 47,
        "text": "・widespread publicity  "
      },
      {
        "line": 48,
        "text": "用途: 広い地域や多くの媒体に及ぶ世間の注目・報道を表す。  "
      },
      {
        "line": 49,
        "text": "例: The discovery received widespread publicity in the national press.  "
      },
      {
        "line": 50,
        "text": "訳: その発見は全国紙で広く報道された。  "
      },
      {
        "line": 52,
        "text": "・good/bad publicity  "
      },
      {
        "line": 53,
        "text": "用途: 注目が対象に好影響または悪影響を与えることを評価する。  "
      },
      {
        "line": 54,
        "text": "例: The scandal gave the company bad publicity.  "
      },
      {
        "line": 55,
        "text": "訳: その不祥事は会社に否定的な世間の注目をもたらした。  "
      },
      {
        "line": 57,
        "text": "・negative publicity  "
      },
      {
        "line": 58,
        "text": "用途: 批判、不祥事、悪い報道などによる否定的な世間の注目を表す。  "
      },
      {
        "line": 59,
        "text": "例: The restaurant responded quickly to the negative publicity surrounding the safety complaint.  "
      },
      {
        "line": 60,
        "text": "訳: そのレストランは、安全性に関する苦情をめぐる否定的な報道にすぐ対応した。  "
      },
      {
        "line": 62,
        "text": "・shun publicity  "
      },
      {
        "line": 63,
        "text": "用途: 世間の注目や報道を意図的に避けることを表す。  "
      },
      {
        "line": 64,
        "text": "例: The novelist shuns publicity and rarely gives interviews.  "
      },
      {
        "line": 65,
        "text": "訳: その小説家は世間の注目を避け、めったにインタビューに応じない。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 111,
        "text": "【コロケーション】"
      },
      {
        "line": 113,
        "text": "・a publicity campaign  "
      },
      {
        "line": 114,
        "text": "用途: 商品、作品、行事、主張などへの注目を集める計画的な宣伝活動を表す。  "
      },
      {
        "line": 115,
        "text": "例: The museum launched a publicity campaign for its new exhibition.  "
      },
      {
        "line": 116,
        "text": "訳: その博物館は新しい展覧会の広報キャンペーンを始めた。  "
      },
      {
        "line": 118,
        "text": "・publicity material  "
      },
      {
        "line": 119,
        "text": "用途: メディアや一般の人に提供する広報・宣伝用の資料を表す。  "
      },
      {
        "line": 120,
        "text": "例: The press office prepared publicity material for the product launch.  "
      },
      {
        "line": 121,
        "text": "訳: 広報室は製品発売のための宣伝資料を用意した。  "
      },
      {
        "line": 123,
        "text": "・advance publicity for 〈発売・行事〉  "
      },
      {
        "line": 124,
        "text": "用途: 映画、書籍、製品、行事などの開始前に行う事前広報を表す。  "
      },
      {
        "line": 125,
        "text": "例: The organizers arranged advance publicity for the festival several months before it opened.  "
      },
      {
        "line": 126,
        "text": "訳: 主催者は祭りの開幕数か月前から事前広報を手配した。  "
      },
      {
        "line": 128,
        "text": "・a publicity stunt  "
      },
      {
        "line": 129,
        "text": "用途: メディアや世間の注目を集めるために意図して行う行為・仕掛けを表す。  "
      },
      {
        "line": 130,
        "text": "例: The company staged a publicity stunt by projecting its logo onto the river bridge.  "
      },
      {
        "line": 131,
        "text": "訳: その会社は川に架かる橋へロゴを投影する話題作りの仕掛けを行った。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 71,
        "text": "【類義語】"
      },
      {
        "line": 73,
        "text": "・attention  "
      },
      {
        "line": 74,
        "text": "定義: 人や話題に関心が向けられていること。  "
      },
      {
        "line": 75,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 76,
        "text": "違い: publicity は特に新聞・テレビなどを通じた公的な注目・露出に焦点があり、attention より媒体や公衆に寄る。  "
      },
      {
        "line": 77,
        "text": "例: The announcement attracted attention from local residents.  "
      },
      {
        "line": 78,
        "text": "訳: その発表は地元住民の注目を集めた。  "
      },
      {
        "line": 80,
        "text": "・exposure  "
      },
      {
        "line": 81,
        "text": "定義: 人・商品・活動などが公衆や媒体に知られること。  "
      },
      {
        "line": 82,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 83,
        "text": "違い: publicity は露出の機会一般より、世間の注目・報道を受けること、またはそれを集める活動を表す。  "
      },
      {
        "line": 84,
        "text": "例: The interview gave the small business valuable exposure.  "
      },
      {
        "line": 85,
        "text": "訳: そのインタビューは、その小企業に貴重な公的露出をもたらした。  "
      },
      {
        "line": 87,
        "text": "・coverage  "
      },
      {
        "line": 88,
        "text": "定義: 新聞、テレビ、ウェブなどによる報道。  "
      },
      {
        "line": 89,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 90,
        "text": "違い: coverage はメディアによる報道内容を指し、publicity は報道による注目や、注目を集める活動まで含む。  "
      },
      {
        "line": 91,
        "text": "例: The issue received extensive media coverage.  "
      },
      {
        "line": 92,
        "text": "訳: その問題はメディアで大きく報道された。  "
      },
      {
        "line": 94,
        "text": "・fame  "
      },
      {
        "line": 95,
        "text": "定義: 多くの人に知られている状態。  "
      },
      {
        "line": 96,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 97,
        "text": "違い: fame は知名度という状態を指すのに対し、publicity は一時的な注目・報道も表し、negative publicity のように評価中立である。  "
      },
      {
        "line": 98,
        "text": "例: The actor achieved international fame after the film won several awards.  "
      },
      {
        "line": 99,
        "text": "訳: その俳優は、その映画がいくつも賞を取った後、国際的な名声を得た。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 139,
        "text": "【類義語】"
      },
      {
        "line": 141,
        "text": "・advertising  "
      },
      {
        "line": 142,
        "text": "定義: 商品、サービス、組織などを広告によって公衆に知らせる活動。  "
      },
      {
        "line": 143,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 144,
        "text": "違い: advertising は有料の広告メッセージや広告業務に焦点がある。publicity は通常、情報・活動によって公衆の注目を集める語だが、辞書や文脈によって paid advertising を含むこともある。  "
      },
      {
        "line": 145,
        "text": "例: The company increased its advertising budget before the holiday season.  "
      },
      {
        "line": 146,
        "text": "訳: その会社は休暇シーズンの前に広告予算を増やした。  "
      },
      {
        "line": 148,
        "text": "・promotion  "
      },
      {
        "line": 149,
        "text": "定義: 商品、サービス、作品、考えなどの販売・普及・認知を高める活動。  "
      },
      {
        "line": 150,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 151,
        "text": "違い: promotion は販売・普及も含む広い活動語で、publicity は公衆の注目を集める情報・活動に焦点がある。  "
      },
      {
        "line": 152,
        "text": "例: The festival used social media promotion to sell more tickets.  "
      },
      {
        "line": 153,
        "text": "訳: その祭りは、より多くのチケットを売るためにSNSで販促を行った。  "
      },
      {
        "line": 155,
        "text": "・public relations  "
      },
      {
        "line": 156,
        "text": "定義: 企業・組織・人物と公衆との関係を管理する活動。  "
      },
      {
        "line": 157,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 158,
        "text": "違い: public relations は公衆との関係全体を扱う広い活動で、publicity は注目を集める広報活動やその結果を指しやすい。  "
      },
      {
        "line": 159,
        "text": "例: The company hired a public relations firm after the data breach.  "
      },
      {
        "line": 160,
        "text": "訳: その会社はデータ漏えいの後、広報会社を雇った。  "
      },
      {
        "line": 162,
        "text": "・marketing  "
      },
      {
        "line": 163,
        "text": "定義: 市場調査、商品設計、価格設定、流通、宣伝などを通じて需要と販売を形成する活動。  "
      },
      {
        "line": 164,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 165,
        "text": "違い: marketing は市場活動全体を扱う広い語で、publicity と重なる場合もある。ただし publicity は人・作品・行事・主張にも用いられる、注目を集める情報発信や活動を指す。  "
      },
      {
        "line": 166,
        "text": "例: The marketing team tested the new packaging with several customer groups.  "
      },
      {
        "line": 167,
        "text": "訳: マーケティングチームは複数の顧客グループで新しい包装を試した。  "
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
