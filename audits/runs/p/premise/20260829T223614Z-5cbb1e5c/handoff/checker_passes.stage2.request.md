# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

The response must be one `antonym_axis_adjudication_record_v1` JSON object and must be saved as `checker_passes.stage2.response.json`.

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
  "input_body_sha256": "1853b935aa8af00051a2dc94003c0f331997f6110d9b6181471417254083d528",
  "blind_request_sha256": "84c855eee79c12fcb69fa42cbe4e55d712be41ba6f6b8d9b17a8ba4b56fe5079",
  "blind_record_sha256": "4adf1ddf90aa3b5dfe4a37caf96c58044ca72cf56aa4d064d0941ebf60653863",
  "input_sections": {
    "sense_structure": [
      {
        "line": 43,
        "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
      },
      {
        "line": 45,
        "text": "【日本語訳・定義】議論、推論、判断、計画、行動などを進める際に、真である、またはひとまず受け入れるものとして置かれる考え・命題・仮定。その前提自体が実際に正しいことを `premise` という語が保証するわけではなく、`false premise`「誤った前提」のようにも使える。  "
      },
      {
        "line": 113,
        "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
      },
      {
        "line": 115,
        "text": "【日本語訳・定義】映画、小説、ドラマ、ゲーム、企画などを成立させる基本的な状況・設定・中心アイデア。作品によっては主要な筋立て・ストーリーラインの核まで指し、細かな出来事の並びをすべて指す `plot` より「作品を一文程度で要約できる土台」に焦点がある。  "
      },
      {
        "line": 165,
        "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
      },
      {
        "line": 167,
        "text": "【日本語訳・定義】論証・推論において、結論を導くための出発点として置かれる命題。三段論法では `major premise`「大前提」、`minor premise`「小前提」のように呼ぶ。一般語義1と連続しているが、ここでは論証の構成要素としてより厳密に用いる。  "
      },
      {
        "line": 217,
        "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
      },
      {
        "line": 219,
        "text": "【日本語訳・定義】人・会社・組織などが所有・占有・使用する土地、建物、建物の一部、およびそれに付随する敷地。会社・店舗・学校・病院・工場などの場所に特によく使うが、住宅や賃貸物件などにも使える。現代英語ではこの意味を通常 `premises` という複数形で表し、単数 `a premise` を「一つの建物・敷地」の意味では普通使わない。  "
      },
      {
        "line": 281,
        "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
      },
      {
        "line": 283,
        "text": "【日本語訳・定義】理論、議論、計画、判断などを、ある考え・仮定が真または受け入れられるものとして土台にして組み立てる。現代英語では、とくに受動態 `be premised on/upon ...`「～を前提としている、～に基づいている」が重要である。  "
      },
      {
        "line": 336,
        "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
      },
      {
        "line": 338,
        "text": "【日本語訳・定義】議論や推論を始める前に、ある命題・考えを前提として提示したり、真であるものとして仮に置いたりする。語義5の `premise A on B` では A が前提に基づいて組み立てられる対象だが、この語義では目的語・that節の内容そのものが「前提として置かれる内容」になる。  "
      }
    ],
    "frames": [
      {
        "line": 43,
        "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
      },
      {
        "line": 51,
        "text": "【文法パターン】`the premise that ...`＝～という前提／`on the premise that ...`＝～という前提で／`start/work/proceed from the premise that ...`＝～を前提として始める・進める／`base 〈議論・計画〉 on the premise that ...`＝議論・計画を～という前提に置く／`question/challenge/reject a premise`＝前提を疑う・異議を唱える・退ける／`a false/flawed/basic/underlying premise`＝誤った・欠陥のある・基本的な・根底の前提  "
      },
      {
        "line": 113,
        "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
      },
      {
        "line": 121,
        "text": "【文法パターン】`the premise of 〈作品・企画〉`＝作品・企画の基本設定／`a simple/interesting/intriguing premise`＝単純な・興味深い・魅力的な設定／`the premise is that ...`＝基本設定は～である／`build a story around a premise`＝ある設定を中心に物語を作る  "
      },
      {
        "line": 165,
        "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
      },
      {
        "line": 173,
        "text": "【文法パターン】`a premise of an argument`＝論証の前提命題／`major/minor premise`＝大前提・小前提／`premises and conclusion`＝前提群と結論／`derive/infer a conclusion from premises`＝前提から結論を導く／`the premises are true`＝前提群が真である  "
      },
      {
        "line": 217,
        "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
      },
      {
        "line": 225,
        "text": "【文法パターン】`on the premises`＝その構内・敷地内で／`off the premises`＝構外・敷地外で／`enter/leave/vacate the premises`＝構内に入る・出る・退去する／`business/commercial/industrial premises`＝事業用・商業用・工業用施設／`the premises are ...`＝その建物・敷地は～である  "
      },
      {
        "line": 281,
        "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
      },
      {
        "line": 289,
        "text": "【文法パターン】`premise 〈理論・主張・計画〉 on/upon 〈考え・仮定〉`＝理論などを考え・仮定に基づかせる／`〈理論・主張・計画〉 be premised on/upon 〈考え・仮定〉`＝理論などが考え・仮定を前提としている  "
      },
      {
        "line": 336,
        "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
      },
      {
        "line": 344,
        "text": "【文法パターン】`premise that ...`＝～だと前提として述べる・仮定する／`premise 〈命題・考え〉`＝命題・考えを前提として置く／`let us premise that ...`＝～だと前提としておこう  "
      }
    ],
    "collocations_examples": [
      {
        "line": 43,
        "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
      },
      {
        "line": 53,
        "text": "【コロケーション】"
      },
      {
        "line": 55,
        "text": "・`the premise that ...`  "
      },
      {
        "line": 56,
        "text": "用途: 内容を that節で明示して「～という前提」を表す。  "
      },
      {
        "line": 57,
        "text": "例: The proposal rests on the premise that demand will continue to grow.  "
      },
      {
        "line": 58,
        "text": "訳: その提案は、需要が今後も伸び続けるという前提に立っている。  "
      },
      {
        "line": 60,
        "text": "・`on the premise that ...`  "
      },
      {
        "line": 61,
        "text": "用途: 判断・行動を何らかの仮定に基づいて行うことを示す。  "
      },
      {
        "line": 62,
        "text": "例: We planned the schedule on the premise that the parts would arrive by Friday.  "
      },
      {
        "line": 63,
        "text": "訳: 私たちは、部品が金曜日までに届くという前提で日程を組んだ。  "
      },
      {
        "line": 65,
        "text": "・`start from the premise that ...`  "
      },
      {
        "line": 66,
        "text": "用途: 議論や分析の出発点となる考えを示す。  "
      },
      {
        "line": 67,
        "text": "例: The report starts from the premise that access to data should be limited by purpose.  "
      },
      {
        "line": 68,
        "text": "訳: その報告書は、データへのアクセスは目的に応じて制限されるべきだという前提から出発している。  "
      },
      {
        "line": 70,
        "text": "・`an underlying premise`  "
      },
      {
        "line": 71,
        "text": "用途: 明示されていなくても、議論や制度の根底で支えている前提を指す。  "
      },
      {
        "line": 72,
        "text": "例: An underlying premise of the policy is that most users will follow the rules voluntarily.  "
      },
      {
        "line": 73,
        "text": "訳: その方針の根底にある前提の一つは、大半の利用者が自発的に規則を守るということである。  "
      },
      {
        "line": 75,
        "text": "・`a false/flawed premise`  "
      },
      {
        "line": 76,
        "text": "用途: 結論以前に、出発点となる仮定そのものに誤りや欠陥があることを示す。  "
      },
      {
        "line": 77,
        "text": "例: A convincing argument can still fail if it begins with a false premise.  "
      },
      {
        "line": 78,
        "text": "訳: 説得力のある議論でも、誤った前提から始まれば成り立たないことがある。  "
      },
      {
        "line": 80,
        "text": "・`question/challenge the premise`  "
      },
      {
        "line": 81,
        "text": "用途: 相手の結論ではなく、その結論を支える出発点そのものを疑う。  "
      },
      {
        "line": 82,
        "text": "例: Before discussing the cost, we should challenge the premise that the change is necessary.  "
      },
      {
        "line": 83,
        "text": "訳: 費用を議論する前に、その変更が必要だという前提自体を検討し直すべきだ。  "
      },
      {
        "line": 113,
        "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
      },
      {
        "line": 123,
        "text": "【コロケーション】"
      },
      {
        "line": 125,
        "text": "・`the premise of the film/show/book`  "
      },
      {
        "line": 126,
        "text": "用途: 作品の基本設定や中心アイデアを述べる。  "
      },
      {
        "line": 127,
        "text": "例: The premise of the film is simple: nobody in the town can tell a lie.  "
      },
      {
        "line": 128,
        "text": "訳: その映画の基本設定は単純で、町の誰も嘘をつけないというものだ。  "
      },
      {
        "line": 130,
        "text": "・`an intriguing premise`  "
      },
      {
        "line": 131,
        "text": "用途: 読者・視聴者の興味を引く基本設定を評価する。  "
      },
      {
        "line": 132,
        "text": "例: The novel has an intriguing premise, even though the middle chapters move slowly.  "
      },
      {
        "line": 133,
        "text": "訳: 中盤の展開は遅いものの、その小説には興味を引く基本設定がある。  "
      },
      {
        "line": 135,
        "text": "・`build a story around a premise`  "
      },
      {
        "line": 136,
        "text": "用途: 一つの中心設定を核として物語を展開する。  "
      },
      {
        "line": 137,
        "text": "例: The writers built the series around the premise that memories could be traded.  "
      },
      {
        "line": 138,
        "text": "訳: 脚本家たちは、記憶を売買できるという設定を中心にシリーズを構成した。  "
      },
      {
        "line": 165,
        "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
      },
      {
        "line": 175,
        "text": "【コロケーション】"
      },
      {
        "line": 177,
        "text": "・`major premise`  "
      },
      {
        "line": 178,
        "text": "用途: 伝統的なカテゴリー三段論法で、結論の述語となる major term（大項）を含む前提を指す。「より一般的な内容だから大前提」と定義されるわけではない。  "
      },
      {
        "line": 179,
        "text": "例: In “All metals conduct electricity; copper is a metal; therefore copper conducts electricity,” the first statement is the major premise because it contains the predicate term of the conclusion.  "
      },
      {
        "line": 180,
        "text": "訳: 「すべての金属は電気を通す。銅は金属である。したがって銅は電気を通す」という三段論法では、最初の命題が結論の述語となる大項を含むため大前提である。  "
      },
      {
        "line": 182,
        "text": "・`minor premise`  "
      },
      {
        "line": 183,
        "text": "用途: 伝統的なカテゴリー三段論法で、結論の主語となる minor term（小項）を含む前提を指す。「個別的な内容だから小前提」と定義されるわけではない。  "
      },
      {
        "line": 184,
        "text": "例: In the same syllogism, “Copper is a metal” is the minor premise because it contains the subject term of the conclusion.  "
      },
      {
        "line": 185,
        "text": "訳: 同じ三段論法では、「銅は金属である」が結論の主語となる小項を含むため小前提である。  "
      },
      {
        "line": 187,
        "text": "・`premises and conclusion`  "
      },
      {
        "line": 188,
        "text": "用途: 論証を、根拠として置かれる命題群と、そこから導かれる結論に分けて捉える。  "
      },
      {
        "line": 189,
        "text": "例: To evaluate the argument, separate its premises from its conclusion.  "
      },
      {
        "line": 190,
        "text": "訳: その論証を評価するには、前提群と結論を分けて考えなさい。  "
      },
      {
        "line": 192,
        "text": "・`infer a conclusion from the premises`  "
      },
      {
        "line": 193,
        "text": "用途: 与えられた前提から推論によって結論を導く。  "
      },
      {
        "line": 194,
        "text": "例: The conclusion cannot be inferred from the premises without an additional assumption.  "
      },
      {
        "line": 195,
        "text": "訳: 追加の仮定がなければ、その前提群からその結論を導くことはできない。  "
      },
      {
        "line": 217,
        "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
      },
      {
        "line": 227,
        "text": "【コロケーション】"
      },
      {
        "line": 229,
        "text": "・`on the premises`  "
      },
      {
        "line": 230,
        "text": "用途: 建物・敷地の内側で行われることを表す。`premises` に所有格を付けず、特定の構内なら `the` を使うことが多い。  "
      },
      {
        "line": 231,
        "text": "例: Smoking is not permitted anywhere on the premises.  "
      },
      {
        "line": 232,
        "text": "訳: この敷地内では、どこであっても喫煙は認められていない。  "
      },
      {
        "line": 234,
        "text": "・`off the premises`  "
      },
      {
        "line": 235,
        "text": "用途: 建物・敷地の外へ出た場所、または外で行うことを表す。  "
      },
      {
        "line": 236,
        "text": "例: Confidential documents must not be taken off the premises without permission.  "
      },
      {
        "line": 237,
        "text": "訳: 機密文書を許可なく構外へ持ち出してはならない。  "
      },
      {
        "line": 239,
        "text": "・`leave/vacate the premises`  "
      },
      {
        "line": 240,
        "text": "用途: 人が構内を離れる、または占有者が建物・敷地から退去することを表す。`vacate` はより形式的。  "
      },
      {
        "line": 241,
        "text": "例: Visitors must leave the premises by 9 p.m.  "
      },
      {
        "line": 242,
        "text": "訳: 来訪者は午後9時までに構内から退出しなければならない。  "
      },
      {
        "line": 244,
        "text": "・`business/commercial premises`  "
      },
      {
        "line": 245,
        "text": "用途: 事業に使用される建物・敷地をまとめて表す。  "
      },
      {
        "line": 246,
        "text": "例: The company moved to larger business premises near the station.  "
      },
      {
        "line": 247,
        "text": "訳: その会社は駅の近くの、より広い事業用施設へ移転した。  "
      },
      {
        "line": 249,
        "text": "・`the premises are ...`  "
      },
      {
        "line": 250,
        "text": "用途: `premises` を複数扱いして状態を述べる。  "
      },
      {
        "line": 251,
        "text": "例: The premises are protected by security cameras at all times.  "
      },
      {
        "line": 252,
        "text": "訳: その施設は常時、防犯カメラで監視されている。  "
      },
      {
        "line": 281,
        "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
      },
      {
        "line": 291,
        "text": "【コロケーション】"
      },
      {
        "line": 293,
        "text": "・`be premised on the assumption that ...`  "
      },
      {
        "line": 294,
        "text": "用途: 理論・計画などの根底にある仮定を明示する。  "
      },
      {
        "line": 295,
        "text": "例: The forecast is premised on the assumption that interest rates will remain unchanged.  "
      },
      {
        "line": 296,
        "text": "訳: その予測は、金利が据え置かれるという仮定を前提にしている。  "
      },
      {
        "line": 298,
        "text": "・`be premised on the idea that ...`  "
      },
      {
        "line": 299,
        "text": "用途: 制度・主張などが、ある考えを出発点として構成されていることを表す。  "
      },
      {
        "line": 300,
        "text": "例: The program is premised on the idea that early support can prevent larger problems later.  "
      },
      {
        "line": 301,
        "text": "訳: そのプログラムは、早期支援によって後の大きな問題を防げるという考えに基づいている。  "
      },
      {
        "line": 303,
        "text": "・`premise an argument on/upon ...`  "
      },
      {
        "line": 304,
        "text": "用途: 議論を特定の前提に基づかせる。能動態は受動態より形式的で、頻度も低い。  "
      },
      {
        "line": 305,
        "text": "例: The author premises the argument on a distinction between legal ownership and practical control.  "
      },
      {
        "line": 306,
        "text": "訳: 著者は、法的所有と実質的支配の区別を前提としてその議論を組み立てている。  "
      },
      {
        "line": 336,
        "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
      },
      {
        "line": 346,
        "text": "【コロケーション】"
      },
      {
        "line": 348,
        "text": "・`premise that ...`  "
      },
      {
        "line": 349,
        "text": "用途: 後続の議論のため、that節の内容そのものを前提として置く。  "
      },
      {
        "line": 350,
        "text": "例: The author premises that each participant has access to the same information.  "
      },
      {
        "line": 351,
        "text": "訳: 著者は、各参加者が同じ情報にアクセスできることを前提として置いている。  "
      },
      {
        "line": 353,
        "text": "・`let us premise that ...`  "
      },
      {
        "line": 354,
        "text": "用途: 論証の冒頭で、検討のための前提を明示的に設定する。現代ではかなり硬い。  "
      },
      {
        "line": 355,
        "text": "例: Let us premise that the two measurements were taken under identical conditions.  "
      },
      {
        "line": 356,
        "text": "訳: 2回の測定は同一条件で行われたと前提としておこう。  "
      },
      {
        "line": 358,
        "text": "・`premise a proposition`  "
      },
      {
        "line": 359,
        "text": "用途: 命題そのものを、後の推論に先立つ前提として提示する。  "
      },
      {
        "line": 360,
        "text": "例: The author premises a proposition about human motivation before turning to the main argument.  "
      },
      {
        "line": 361,
        "text": "訳: 著者は本論に入る前に、人間の動機に関する命題を前提として提示している。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 43,
        "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
      },
      {
        "line": 90,
        "text": "【類義語】"
      },
      {
        "line": 92,
        "text": "・assumption  "
      },
      {
        "line": 93,
        "text": "定義: 証明・確認されていないが、ひとまず真として受け入れる考え。  "
      },
      {
        "line": 94,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 95,
        "text": "違い: `assumption` は日常的な思い込みや計画上の仮定にも広く使える。`premise` は、その考えを土台に議論・推論・判断を組み立てる関係をより強く示す。  "
      },
      {
        "line": 96,
        "text": "例: Our cost estimate is based on the assumption that fuel prices will remain stable.  "
      },
      {
        "line": 97,
        "text": "訳: 私たちの費用見積もりは、燃料価格が安定したままだという仮定に基づいている。  "
      },
      {
        "line": 99,
        "text": "・presupposition  "
      },
      {
        "line": 100,
        "text": "定義: 発言・理論・考えの背後ですでに成り立つものとして想定されている前提。  "
      },
      {
        "line": 101,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 102,
        "text": "違い: `premise` が明示的な論証の土台にも使えるのに対し、`presupposition` は暗黙に先取りされている前提という含みが強く、言語学・哲学でも使われる。  "
      },
      {
        "line": 103,
        "text": "例: The question contains the presupposition that someone made the decision deliberately.  "
      },
      {
        "line": 104,
        "text": "訳: その質問には、誰かが意図的にその決定をしたという前提が含まれている。  "
      },
      {
        "line": 106,
        "text": "・basis  "
      },
      {
        "line": 107,
        "text": "定義: 判断・主張・制度などを支える根拠・基礎。  "
      },
      {
        "line": 108,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 109,
        "text": "違い: `basis` は事実、証拠、原則、計算方法など幅広い「基礎」を表せる。`premise` は特に、真として置く考え・命題を指す。  "
      },
      {
        "line": 110,
        "text": "例: There is no factual basis for the claim.  "
      },
      {
        "line": 111,
        "text": "訳: その主張には事実上の根拠がない。  "
      },
      {
        "line": 113,
        "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
      },
      {
        "line": 142,
        "text": "【類義語】"
      },
      {
        "line": 144,
        "text": "・concept  "
      },
      {
        "line": 145,
        "text": "定義: 作品・企画・製品などの中心となる発想・概念。  "
      },
      {
        "line": 146,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 147,
        "text": "違い: `concept` は視覚的・商品的・抽象的なアイデアにも広く使える。`premise` は「この条件・状況を出発点にすると何が起こるか」という物語的な設定に向きやすい。  "
      },
      {
        "line": 148,
        "text": "例: The design concept combines a library with a community workspace.  "
      },
      {
        "line": 149,
        "text": "訳: その設計コンセプトは、図書館と地域の共同作業空間を組み合わせている。  "
      },
      {
        "line": 151,
        "text": "・setup  "
      },
      {
        "line": 152,
        "text": "定義: 物語の冒頭で人物・状況・対立関係を整える設定・導入。  "
      },
      {
        "line": 153,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 154,
        "text": "違い: `setup` は物語が動き出すための具体的な初期配置に焦点がある。`premise` は作品全体を支える中心アイデアまで含み得る。  "
      },
      {
        "line": 155,
        "text": "例: The opening scene establishes the setup for the mystery.  "
      },
      {
        "line": 156,
        "text": "訳: 冒頭の場面で、そのミステリーの初期設定が示される。  "
      },
      {
        "line": 158,
        "text": "・plot  "
      },
      {
        "line": 159,
        "text": "定義: 物語で起きる出来事の筋、展開。  "
      },
      {
        "line": 160,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 161,
        "text": "違い: `plot` は出来事の連鎖そのもの。`premise` はその連鎖を生み出す基本条件・着想である。  "
      },
      {
        "line": 162,
        "text": "例: The plot becomes more complicated after the second episode.  "
      },
      {
        "line": 163,
        "text": "訳: 物語の筋は第2話以降さらに複雑になる。  "
      },
      {
        "line": 165,
        "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
      },
      {
        "line": 201,
        "text": "【類義語】"
      },
      {
        "line": 203,
        "text": "・proposition  "
      },
      {
        "line": 204,
        "text": "定義: 真か偽かを問いうる内容を持つ命題。  "
      },
      {
        "line": 205,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 206,
        "text": "違い: `proposition` は命題そのものの種類を表し、結論にもなり得る。`premise` は論証の中で、その命題が結論を支える役割に置かれていることを表す。  "
      },
      {
        "line": 207,
        "text": "例: The proposition is false, but it can still be used to illustrate the form of the argument.  "
      },
      {
        "line": 208,
        "text": "訳: その命題は偽だが、論証の形式を示すためには使える。  "
      },
      {
        "line": 210,
        "text": "・assumption  "
      },
      {
        "line": 211,
        "text": "定義: 推論のために真として置く仮定。  "
      },
      {
        "line": 212,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 213,
        "text": "違い: `assumption` は明示されない補助的な仮定にも使える。`premise` は論証の構成要素として提示された命題を指しやすい。  "
      },
      {
        "line": 214,
        "text": "例: The proof depends on an unstated assumption about continuity.  "
      },
      {
        "line": 215,
        "text": "訳: その証明は、連続性についての明示されていない仮定に依存している。  "
      },
      {
        "line": 217,
        "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
      },
      {
        "line": 258,
        "text": "【類義語】"
      },
      {
        "line": 260,
        "text": "・property  "
      },
      {
        "line": 261,
        "text": "定義: 所有される土地・建物、不動産。  "
      },
      {
        "line": 262,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 263,
        "text": "違い: `property` は所有物・不動産としての法的・経済的な対象に焦点があり、個人住宅にも広く使える。`premises` は所有者が誰かより、その場所が占有・使用される物理的な建物・敷地として捉えられることが多い。  "
      },
      {
        "line": 264,
        "text": "例: The company owns several properties in the city.  "
      },
      {
        "line": 265,
        "text": "訳: その会社は市内に複数の不動産を所有している。  "
      },
      {
        "line": 267,
        "text": "・site  "
      },
      {
        "line": 268,
        "text": "定義: 建物・活動・工事などが置かれている、または行われる場所・敷地。  "
      },
      {
        "line": 269,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 270,
        "text": "違い: `site` は場所そのものに焦点があり、建物がまだない土地にも使える。`premises` は既に占有・使用されている建物・敷地をまとめて指しやすい。  "
      },
      {
        "line": 271,
        "text": "例: Construction will begin on the new site next month.  "
      },
      {
        "line": 272,
        "text": "訳: 新しい敷地では来月、建設工事が始まる。  "
      },
      {
        "line": 274,
        "text": "・facility  "
      },
      {
        "line": 275,
        "text": "定義: 特定の目的のために設けられた建物・設備。  "
      },
      {
        "line": 276,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 277,
        "text": "違い: `facility` は機能・設備に焦点があり、研究施設・製造施設など用途を強調する。`premises` は用途の詳細より、物理的な構内全体を指す。  "
      },
      {
        "line": 278,
        "text": "例: The laboratory operates a testing facility outside the city.  "
      },
      {
        "line": 279,
        "text": "訳: その研究所は市外で試験施設を運営している。  "
      },
      {
        "line": 281,
        "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
      },
      {
        "line": 313,
        "text": "【類義語】"
      },
      {
        "line": 315,
        "text": "・base  "
      },
      {
        "line": 316,
        "text": "定義: 考え・行動・判断などを、特定の根拠・情報・原則に基づかせる。  "
      },
      {
        "line": 317,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 318,
        "text": "違い: `base A on B` は証拠・データ・経験などにも非常に広く使える。`premise A on B` は B が「前提として置かれる考え・仮定」である場合に特に適し、より形式的。  "
      },
      {
        "line": 319,
        "text": "例: The decision was based on updated safety data.  "
      },
      {
        "line": 320,
        "text": "訳: その決定は最新の安全データに基づいていた。  "
      },
      {
        "line": 322,
        "text": "・found  "
      },
      {
        "line": 323,
        "text": "定義: 理論・制度・主張などを、ある原理・根拠の上に築く。  "
      },
      {
        "line": 324,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 325,
        "text": "違い: `be founded on ...` は基礎となる原理・価値・事実にも使え、`premised on` より「築かれている」という比喩が強い。  "
      },
      {
        "line": 326,
        "text": "例: The organization was founded on the principle of equal access.  "
      },
      {
        "line": 327,
        "text": "訳: その組織は、平等なアクセスという原則に基づいて設立された。  "
      },
      {
        "line": 329,
        "text": "・predicate  "
      },
      {
        "line": 330,
        "text": "定義: 主張・判断などを、ある条件・事実・前提に依存させる。  "
      },
      {
        "line": 331,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 332,
        "text": "違い: `predicate A on B` は非常に形式的で、法律・学術で見られる。`premise A on B` と近いが、`premise` は「前提命題を置く」という語源・論証とのつながりがより直接的である。  "
      },
      {
        "line": 333,
        "text": "例: The claim is predicated on evidence that has since been disputed.  "
      },
      {
        "line": 334,
        "text": "訳: その主張は、その後争われるようになった証拠を前提としている。  "
      },
      {
        "line": 336,
        "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
      },
      {
        "line": 367,
        "text": "【類義語】"
      },
      {
        "line": 369,
        "text": "・assume  "
      },
      {
        "line": 370,
        "text": "定義: 証明せずに、ある内容をひとまず真として受け入れる。  "
      },
      {
        "line": 371,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 372,
        "text": "違い: `assume` は日常・学術のどちらでも広く使え、`premise` よりはるかに一般的。`premise` は論証の前提として明示的に置くという硬い響きがある。  "
      },
      {
        "line": 373,
        "text": "例: Assume that the two samples are independent.  "
      },
      {
        "line": 374,
        "text": "訳: 2つの標本は独立していると仮定しなさい。  "
      },
      {
        "line": 376,
        "text": "・posit  "
      },
      {
        "line": 377,
        "text": "定義: 議論・理論のために、命題や仮説を明示的に提示する。  "
      },
      {
        "line": 378,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 379,
        "text": "違い: `posit` は学術・哲学で比較的自然に使える一方、この語義の `premise` はさらにまれで古風・形式的に感じられることがある。  "
      },
      {
        "line": 380,
        "text": "例: The model posits that agents act on incomplete information.  "
      },
      {
        "line": 381,
        "text": "訳: そのモデルは、行為者は不完全な情報に基づいて行動すると仮定している。  "
      },
      {
        "line": 383,
        "text": "・postulate  "
      },
      {
        "line": 384,
        "text": "定義: 理論や推論の出発点として、命題・原理を仮定する。  "
      },
      {
        "line": 385,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 386,
        "text": "違い: `postulate` は科学・数学・哲学で「理論上の仮定として置く」ことを明確に表せる。`premise` は同じ方向を表せるが、動詞としては使用範囲が狭い。  "
      },
      {
        "line": 387,
        "text": "例: The theory postulates the existence of an unobserved mechanism.  "
      },
      {
        "line": 388,
        "text": "訳: その理論は、観測されていない機構の存在を仮定している。  "
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
