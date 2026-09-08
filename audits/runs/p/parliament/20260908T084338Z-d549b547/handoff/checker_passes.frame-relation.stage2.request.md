# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`/root/parliament_word/check_frame_relation`, declared_model=`gpt-5`.

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
  "input_body_sha256": "a79a267d48a57dc1c95b4c79fa1496950e4ca751f098fd6d46c4a89b6afdfcd2",
  "blind_request_sha256": "d35b886db23447d86da4e3b300d8a531e76d3f79394b170ad98e3af93ac496a5",
  "blind_record_sha256": "386a86a3c5027c55851da5762d4910edf883e2f99064f75b5cca399f796418e7",
  "input_sections": {
    "sense_structure": [
      {
        "line": 34,
        "text": "1. 【名詞・可算／固有名詞的用法】議会、国会；議会を構成する議員たち"
      },
      {
        "line": 36,
        "text": "【日本語訳・定義】国または地域の代表者が集まり、法律の制定・改正、政策や予算の審議、政府の監督などを行う制度的な機関、またはその構成員全体を指す。国によって正式名称・構成・権限が異なるため、日本語訳は文脈に応じて「議会」「国会」などとなる。特定国の正式または慣用的な機関名として用いる場合は `Parliament` と大文字で始めることがある。  "
      },
      {
        "line": 118,
        "text": "2. 【名詞・可算】一議会期、ある選挙で成立した特定期の議会"
      },
      {
        "line": 120,
        "text": "【日本語訳・定義】一度の総選挙後に成立した議会が、次の選挙や解散まで同じ制度上の単位として存続する期間、またはその期間に活動する特定の議員構成を指す。個々の会議や一日ごとの開会ではなく、複数の `session` を含み得る、より大きな単位である。  "
      }
    ],
    "frames": [
      {
        "line": 34,
        "text": "1. 【名詞・可算／固有名詞的用法】議会、国会；議会を構成する議員たち"
      },
      {
        "line": 42,
        "text": "【文法パターン】普通名詞では `a/the + parliament`、`the parliament of 〈国・地域〉` の形を取る。イギリスの国会などを固有の制度として指す `Parliament` は、`in Parliament`、`before Parliament`、`elect someone to Parliament` のように無冠詞で使われることがある。一方、名称を前から限定する `the UK Parliament` や、普通名詞として国を特定する `the French parliament` では定冠詞を用いる。集合名詞としての動詞の単複は、地域差と、機関を一体として見るか構成員を意識するかによって変わり得る。  "
      },
      {
        "line": 118,
        "text": "2. 【名詞・可算】一議会期、ある選挙で成立した特定期の議会"
      },
      {
        "line": 126,
        "text": "【文法パターン】可算名詞として `the current/present/next parliament`、`the first/second year of a parliament` の形を取る。イギリスの特定の議会期を制度名として扱うときは `the current Parliament`、`the next Parliament` のように大文字で書かれることもある。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 34,
        "text": "1. 【名詞・可算／固有名詞的用法】議会、国会；議会を構成する議員たち"
      },
      {
        "line": 44,
        "text": "【コロケーション】"
      },
      {
        "line": 46,
        "text": "・`a member of parliament`  "
      },
      {
        "line": 47,
        "text": "用途: ある国・地域の議会の議員を一般的に指す。イギリスの正式な役職表現では `Member of Parliament` と大文字で書き、略して `MP` とする。  "
      },
      {
        "line": 48,
        "text": "例: She was elected as a member of parliament for the first time last year.  "
      },
      {
        "line": 49,
        "text": "訳: 彼女は昨年、初めて国会議員に選出された。  "
      },
      {
        "line": 51,
        "text": "・`be elected to Parliament`  "
      },
      {
        "line": 52,
        "text": "用途: 議員として国会に選出されることを表す。ここでの `to` は所属先・到達先を示し、`elect Parliament` とはしない。  "
      },
      {
        "line": 53,
        "text": "例: He was elected to Parliament at the age of thirty-two.  "
      },
      {
        "line": 54,
        "text": "訳: 彼は32歳で国会議員に選出された。  "
      },
      {
        "line": 56,
        "text": "・`a bill before Parliament`  "
      },
      {
        "line": 57,
        "text": "用途: 法案が国会に提出され、審議対象となっていることを表す。  "
      },
      {
        "line": 58,
        "text": "例: The bill currently before Parliament would strengthen consumer protections.  "
      },
      {
        "line": 59,
        "text": "訳: 現在国会で審議中のその法案は、消費者保護を強化するものだ。  "
      },
      {
        "line": 61,
        "text": "・`Parliament passes 〈a bill/an Act〉`  "
      },
      {
        "line": 62,
        "text": "用途: 国会が法案を可決する、または法律を成立させることを表す。法案が法律になるための具体的手続きは国・制度によって異なる。  "
      },
      {
        "line": 63,
        "text": "例: Parliament passed the bill after months of debate.  "
      },
      {
        "line": 64,
        "text": "訳: 国会は数か月にわたる審議の末、その法案を可決した。  "
      },
      {
        "line": 66,
        "text": "・`an Act of Parliament`  "
      },
      {
        "line": 67,
        "text": "用途: イギリスなどの文脈で、議会の立法手続きを経て成立した制定法を指す。  "
      },
      {
        "line": 68,
        "text": "例: The requirement was introduced by an Act of Parliament.  "
      },
      {
        "line": 69,
        "text": "訳: その要件は議会制定法によって導入された。  "
      },
      {
        "line": 71,
        "text": "・`a hung parliament`  "
      },
      {
        "line": 72,
        "text": "用途: 選挙後、単独で過半数を持つ政党がない議会を指す。主にイギリス英語および議会制の政治報道で用いる。  "
      },
      {
        "line": 73,
        "text": "例: The election resulted in a hung parliament, so the parties began coalition talks.  "
      },
      {
        "line": 74,
        "text": "訳: 選挙の結果、どの政党も単独過半数を持たない議会となり、各党は連立協議を始めた。  "
      },
      {
        "line": 76,
        "text": "・`dissolve Parliament`  "
      },
      {
        "line": 77,
        "text": "用途: 選挙などに先立ち、制度上の手続きによって特定期の議会を正式に終了させることを表す。  "
      },
      {
        "line": 78,
        "text": "例: The prime minister asked the head of state to dissolve Parliament and call an election.  "
      },
      {
        "line": 79,
        "text": "訳: 首相は国家元首に国会を解散して選挙を実施するよう求めた。  "
      },
      {
        "line": 81,
        "text": "・`a seat in Parliament`  "
      },
      {
        "line": 82,
        "text": "用途: 国会での議席、または議員としての地位を表す。  "
      },
      {
        "line": 83,
        "text": "例: The party won twelve additional seats in Parliament.  "
      },
      {
        "line": 84,
        "text": "訳: その政党は国会でさらに12議席を獲得した。  "
      },
      {
        "line": 118,
        "text": "2. 【名詞・可算】一議会期、ある選挙で成立した特定期の議会"
      },
      {
        "line": 128,
        "text": "【コロケーション】"
      },
      {
        "line": 130,
        "text": "・`the current parliament`  "
      },
      {
        "line": 131,
        "text": "用途: 現在の選挙で構成され、活動中の議会期または議員構成を指す。  "
      },
      {
        "line": 132,
        "text": "例: The proposal is unlikely to pass during the current parliament.  "
      },
      {
        "line": 133,
        "text": "訳: その提案が今議会期中に可決される可能性は低い。  "
      },
      {
        "line": 135,
        "text": "・`the next parliament`  "
      },
      {
        "line": 136,
        "text": "用途: 次の選挙後に成立する議会期または議員構成を指す。  "
      },
      {
        "line": 137,
        "text": "例: The committee recommended that the issue be reconsidered in the next parliament.  "
      },
      {
        "line": 138,
        "text": "訳: 委員会は、その問題を次の議会期に再検討するよう勧告した。  "
      },
      {
        "line": 140,
        "text": "・`the lifetime of a parliament`  "
      },
      {
        "line": 141,
        "text": "用途: ある議会が成立してから解散・終了するまでの存続期間を指す。  "
      },
      {
        "line": 142,
        "text": "例: Major constitutional reform may take the lifetime of a parliament to complete.  "
      },
      {
        "line": 143,
        "text": "訳: 大規模な憲法改革は、一議会期を通じてようやく完了することもある。  "
      },
      {
        "line": 145,
        "text": "・`during this parliament`  "
      },
      {
        "line": 146,
        "text": "用途: 現在の議会期・議員構成が存続している間に、という期間を表す。  "
      },
      {
        "line": 147,
        "text": "例: The government promised to introduce the measure during this parliament.  "
      },
      {
        "line": 148,
        "text": "訳: 政府は今議会期中にその措置を導入すると約束した。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 34,
        "text": "1. 【名詞・可算／固有名詞的用法】議会、国会；議会を構成する議員たち"
      },
      {
        "line": 88,
        "text": "【類義語】"
      },
      {
        "line": 90,
        "text": "・legislature  "
      },
      {
        "line": 91,
        "text": "定義: 法律を制定する権限を持つ機関。  "
      },
      {
        "line": 92,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 93,
        "text": "違い: `legislature` は制度名にかかわらず立法機関を機能面から指す一般語である。`parliament` は特定の政治制度・正式名称と結びつき、審議機関やその議員集団としての側面も表しやすい。  "
      },
      {
        "line": 94,
        "text": "例: The state legislature approved the revised budget.  "
      },
      {
        "line": 95,
        "text": "訳: 州議会は修正予算を承認した。  "
      },
      {
        "line": 97,
        "text": "・congress  "
      },
      {
        "line": 98,
        "text": "定義: 代表者が集まる会議または立法機関。特に大文字の `Congress` はアメリカ合衆国の連邦議会を指す。  "
      },
      {
        "line": 99,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 100,
        "text": "違い: `parliament` と近い立法機関名だが、どちらを使うかは各国・機関の正式名称と制度上の慣用で決まる。任意に置き換えられる一般的な同義語ではない。  "
      },
      {
        "line": 101,
        "text": "例: Congress approved the spending package late Friday.  "
      },
      {
        "line": 102,
        "text": "訳: 連邦議会は金曜遅く、その歳出法案一式を承認した。  "
      },
      {
        "line": 104,
        "text": "・assembly  "
      },
      {
        "line": 105,
        "text": "定義: 特定の目的のために集まる人々、または名称に `Assembly` を持つ審議・立法機関。  "
      },
      {
        "line": 106,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 107,
        "text": "違い: `assembly` は会合一般や地方・国際機関の名称にも使える広い語で、立法権を必ず含まない。`parliament` は政治的な代表制議会を中心に指す。  "
      },
      {
        "line": 108,
        "text": "例: The regional assembly debated the transport plan.  "
      },
      {
        "line": 109,
        "text": "訳: 地域議会はその交通計画を審議した。  "
      },
      {
        "line": 111,
        "text": "・diet  "
      },
      {
        "line": 112,
        "text": "定義: 日本など一部の国の立法機関を指す伝統的な英語名称。  "
      },
      {
        "line": 113,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 114,
        "text": "違い: この意味の `diet` は特定国の機関名に限られる。一般名詞として各国の議会を指す `parliament` より適用範囲が狭く、日本では `the National Diet` が正式な英語名称として使われる。  "
      },
      {
        "line": 115,
        "text": "例: The bill was submitted to the National Diet.  "
      },
      {
        "line": 116,
        "text": "訳: その法案は国会に提出された。  "
      },
      {
        "line": 118,
        "text": "2. 【名詞・可算】一議会期、ある選挙で成立した特定期の議会"
      },
      {
        "line": 152,
        "text": "【類義語】"
      },
      {
        "line": 154,
        "text": "・legislative term  "
      },
      {
        "line": 155,
        "text": "定義: 選挙された立法機関または議員が職務を行う一定の期間。  "
      },
      {
        "line": 156,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 157,
        "text": "違い: `legislative term` は制度を問わず期間を説明する一般的な句である。`parliament` のこの語義は、特定の議会制度における選挙から次の選挙・解散までの会議体と期間を一語で表せる。  "
      },
      {
        "line": 158,
        "text": "例: Several tax reforms were enacted during the legislative term.  "
      },
      {
        "line": 159,
        "text": "訳: その議会任期中に複数の税制改革が制定された。  "
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
