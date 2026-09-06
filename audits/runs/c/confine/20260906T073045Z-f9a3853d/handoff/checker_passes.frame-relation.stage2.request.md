# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`confine-frame-agent`, declared_model=`gpt-5`.

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
  "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
  "blind_request_sha256": "5def1e3cf8eef0d3e5e016fbe7c68964f4dfa8359e9cd80a72373fa6a22150d8",
  "blind_record_sha256": "6720b8ad129a6d66692d8cc6e740190fc5e12648893d23a0a7b87d0baf520233",
  "input_sections": {
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】話題、活動、作業、影響、現象などが及ぶ範囲を、特定の対象・場所・期間・分野などの内側に限定する。対象がすでにその範囲に収まっていることを述べる受動形と、話し手が意識的に扱う範囲を絞る能動形・再帰形の両方がよく使われる。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 120,
        "text": "【日本語訳・定義】人や動物を、部屋、施設、囲い、刑務所などの外へ自由に出られないようにする。物理的な障壁、命令、拘禁などによる移動の制限を表し、本人の自由意思で滞在している場合には通常使わない。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 193,
        "text": "【日本語訳・定義】病気、けが、身体状態などが原因で、人がベッド、自宅、病室など限られた場所から動けない、または外出できない状態にする。原因を主語にする能動文も可能だが、本人を主語にした be confined to が特に多い。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 250,
        "text": "【日本語訳・定義】confined の形で、空間や区域が壁や境界に囲まれて狭い、または内部で動ける余地が少ないことを表す。単に面積が小さいだけでなく、閉鎖性や動きにくさを含みやすい。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 323,
        "text": "【日本語訳・定義】通常 confines の形で、場所・組織・分野などの外縁をなす境界、またはその境界に囲まれた内部の領域を表す。現代の一般的な文章では単数形 confine より複数形 confines が圧倒的に普通である。  "
      }
    ],
    "frames": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 48,
        "text": "【文法パターン】confine something to 〈範囲・場所・期間・活動〉＝何かを～の範囲内に限る／confine oneself to 〈名詞・doing〉＝自分が扱う内容・行うことを～だけにする／be confined to 〈範囲・場所・集団〉＝～に限られている／confine 〈発言・検討・努力〉 to 〈対象〉＝発言・検討・努力の対象を～に絞る  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 126,
        "text": "【文法パターン】confine someone/something in 〈閉鎖場所〉＝人・動物を～の中に閉じ込める／confine someone/something to 〈場所〉＝人・動物を～から出られないようにする／be confined in 〈施設・部屋〉＝～に収容・拘束されている／be confined to quarters＝兵舎・自室待機を命じられている  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 199,
        "text": "【文法パターン】〈病気・けが・身体状態〉 confine someone to 〈bed/home/a room〉＝病気などが人を～から動けない状態にする／someone be confined to bed/home＝人が病気などで寝床・自宅から動けない／someone be confined to 〈場所〉 with/by 〈病気・けが〉＝病気・けがにより～にとどまっている  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 256,
        "text": "【文法パターン】a confined 〈space/area/place〉＝狭く囲まれた空間・区域／in confined 〈conditions/quarters〉＝狭く限られた環境で／feel confined＝閉じ込められたように感じる  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 329,
        "text": "【文法パターン】within the confines of 〈場所・制度・分野〉＝～の範囲内で／beyond the confines of 〈場所・制度・分野〉＝～の境界を越えて／outside the confines of 〈場所・制度・分野〉＝～の範囲外で／the narrow confines of 〈場所・枠組み〉＝～という狭い範囲  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 50,
        "text": "【コロケーション】"
      },
      {
        "line": 52,
        "text": "・confine the discussion to 〈話題〉  "
      },
      {
        "line": 53,
        "text": "用途: 議論で扱う範囲を特定の話題に限定する。  "
      },
      {
        "line": 54,
        "text": "例: Please confine the discussion to the issues on today's agenda.  "
      },
      {
        "line": 55,
        "text": "訳: 議論は本日の議題にある問題だけに絞ってください。  "
      },
      {
        "line": 57,
        "text": "・confine one's remarks to 〈対象〉  "
      },
      {
        "line": 58,
        "text": "用途: 発言する内容を特定の対象に限る。  "
      },
      {
        "line": 59,
        "text": "例: She confined her remarks to the financial risks of the proposal.  "
      },
      {
        "line": 60,
        "text": "訳: 彼女は発言をその提案の財務上のリスクに限定した。  "
      },
      {
        "line": 62,
        "text": "・confine oneself to 〈名詞・doing〉  "
      },
      {
        "line": 63,
        "text": "用途: 自分が扱う話題や行う活動を意識的に一つの範囲へ絞る。  "
      },
      {
        "line": 64,
        "text": "例: In this chapter, I will confine myself to examining the short-term effects.  "
      },
      {
        "line": 65,
        "text": "訳: この章では、短期的な影響の検討だけに対象を絞る。  "
      },
      {
        "line": 67,
        "text": "・be confined to 〈場所・集団〉  "
      },
      {
        "line": 68,
        "text": "用途: 問題、特徴、現象などが特定の場所や集団だけに見られることを表す。  "
      },
      {
        "line": 69,
        "text": "例: The shortage is not confined to rural areas.  "
      },
      {
        "line": 70,
        "text": "訳: その不足は農村部だけに限られた問題ではない。  "
      },
      {
        "line": 72,
        "text": "・confine 〈物質・作用〉 to 〈区域・装置〉  "
      },
      {
        "line": 73,
        "text": "用途: 物質、熱、火、プラズマなどが外へ広がらないよう一定の区域内に保つ。  "
      },
      {
        "line": 74,
        "text": "例: The magnetic field confines the plasma to the center of the chamber.  "
      },
      {
        "line": 75,
        "text": "訳: その磁場はプラズマを容器の中心部に閉じ込める。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 128,
        "text": "【コロケーション】"
      },
      {
        "line": 130,
        "text": "・confine someone in a cell  "
      },
      {
        "line": 131,
        "text": "用途: 人を独房などの閉鎖された空間から出られないようにする。  "
      },
      {
        "line": 132,
        "text": "例: The prisoner was confined in a windowless cell for several days.  "
      },
      {
        "line": 133,
        "text": "訳: その囚人は数日間、窓のない独房に拘禁された。  "
      },
      {
        "line": 135,
        "text": "・confine an animal to 〈囲い・ケージ〉  "
      },
      {
        "line": 136,
        "text": "用途: 動物が指定された囲いの外へ出ないようにする。  "
      },
      {
        "line": 137,
        "text": "例: The injured bird was temporarily confined to a large enclosure.  "
      },
      {
        "line": 138,
        "text": "訳: けがをした鳥は一時的に大きな囲いの中で保護された。  "
      },
      {
        "line": 140,
        "text": "・keep 〈人・動物〉 confined  "
      },
      {
        "line": 141,
        "text": "用途: 人や動物を外へ出られない状態に保つ。  "
      },
      {
        "line": 142,
        "text": "例: The order kept the soldiers confined to their barracks overnight.  "
      },
      {
        "line": 143,
        "text": "訳: その命令により兵士たちは一晩、兵舎から出られなかった。  "
      },
      {
        "line": 145,
        "text": "・be confined to quarters  "
      },
      {
        "line": 146,
        "text": "用途: 軍人などが処罰・命令により兵舎や指定場所から出ないよう命じられた状態を表す。  "
      },
      {
        "line": 147,
        "text": "例: He was confined to quarters for disobeying the order.  "
      },
      {
        "line": 148,
        "text": "訳: 彼は命令に従わなかったため、兵舎待機を命じられた。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 201,
        "text": "【コロケーション】"
      },
      {
        "line": 203,
        "text": "・be confined to bed  "
      },
      {
        "line": 204,
        "text": "用途: 病気やけがのため起きて普段どおり活動できず、寝床にとどまる。  "
      },
      {
        "line": 205,
        "text": "例: She was confined to bed for a week with a severe infection.  "
      },
      {
        "line": 206,
        "text": "訳: 彼女は重い感染症のため1週間、寝床から起きられなかった。  "
      },
      {
        "line": 208,
        "text": "・be confined to one's home  "
      },
      {
        "line": 209,
        "text": "用途: 健康上の理由などで外出できず、自宅にとどまる。  "
      },
      {
        "line": 210,
        "text": "例: After the operation, he was confined to his home for several days.  "
      },
      {
        "line": 211,
        "text": "訳: 手術後、彼は数日間、自宅から出られなかった。  "
      },
      {
        "line": 213,
        "text": "・〈病気・けが〉 confine someone to 〈場所〉  "
      },
      {
        "line": 214,
        "text": "用途: 病気やけがを原因として、人の行動範囲が特定の場所に限られることを表す。  "
      },
      {
        "line": 215,
        "text": "例: A knee injury confined her to the apartment for most of the winter.  "
      },
      {
        "line": 216,
        "text": "訳: 膝のけがのため、彼女は冬の大半をアパートから出られずに過ごした。  "
      },
      {
        "line": 218,
        "text": "・be temporarily confined to 〈場所〉  "
      },
      {
        "line": 219,
        "text": "用途: 限られた期間だけ、健康上の理由で一定の場所にとどまることを表す。  "
      },
      {
        "line": 220,
        "text": "例: He is temporarily confined to his room while he recovers.  "
      },
      {
        "line": 221,
        "text": "訳: 彼は回復するまで一時的に自室で過ごさなければならない。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 258,
        "text": "【コロケーション】"
      },
      {
        "line": 260,
        "text": "・a confined space  "
      },
      {
        "line": 261,
        "text": "用途: 壁や境界に囲まれ、動きや出入りが制限されやすい空間を表す。  "
      },
      {
        "line": 262,
        "text": "例: The machine should not be operated in a confined space without adequate ventilation.  "
      },
      {
        "line": 263,
        "text": "訳: その機械は、十分な換気のない閉鎖空間で作動させるべきではない。  "
      },
      {
        "line": 265,
        "text": "・in confined quarters  "
      },
      {
        "line": 266,
        "text": "用途: 人が動ける余地の少ない狭い居住・作業場所にいることを表す。  "
      },
      {
        "line": 267,
        "text": "例: The crew lived in confined quarters during the voyage.  "
      },
      {
        "line": 268,
        "text": "訳: 乗組員は航海中、狭い居住区で暮らした。  "
      },
      {
        "line": 270,
        "text": "・work in confined conditions  "
      },
      {
        "line": 271,
        "text": "用途: 動作や移動の余地が限られた環境で作業する。  "
      },
      {
        "line": 272,
        "text": "例: The technicians had to work in confined conditions beneath the stage.  "
      },
      {
        "line": 273,
        "text": "訳: 技術者たちは舞台の下の狭い環境で作業しなければならなかった。  "
      },
      {
        "line": 275,
        "text": "・feel confined in 〈場所〉  "
      },
      {
        "line": 276,
        "text": "用途: 場所が狭い、または自由に動けず、閉じ込められたように感じる。  "
      },
      {
        "line": 277,
        "text": "例: I felt confined in the tiny room after only a few hours.  "
      },
      {
        "line": 278,
        "text": "訳: その小さな部屋に数時間いただけで、私は閉じ込められたように感じた。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 331,
        "text": "【コロケーション】"
      },
      {
        "line": 333,
        "text": "・within the confines of 〈場所・制度〉  "
      },
      {
        "line": 334,
        "text": "用途: 物理的または制度的な境界の内側にあることを表す。  "
      },
      {
        "line": 335,
        "text": "例: The negotiations took place within the confines of the embassy.  "
      },
      {
        "line": 336,
        "text": "訳: 交渉は大使館の敷地内で行われた。  "
      },
      {
        "line": 338,
        "text": "・beyond the confines of 〈場所・分野〉  "
      },
      {
        "line": 339,
        "text": "用途: 場所や分野の既存の境界を越えて及ぶことを表す。  "
      },
      {
        "line": 340,
        "text": "例: Her influence extended far beyond the confines of the university.  "
      },
      {
        "line": 341,
        "text": "訳: 彼女の影響力は大学の枠をはるかに越えて広がった。  "
      },
      {
        "line": 343,
        "text": "・outside the confines of 〈制度・枠組み〉  "
      },
      {
        "line": 344,
        "text": "用途: 制度や枠組みが定める範囲の外側にあることを表す。  "
      },
      {
        "line": 345,
        "text": "例: The group continued its work outside the confines of the formal organization.  "
      },
      {
        "line": 346,
        "text": "訳: そのグループは正式な組織の枠外でも活動を続けた。  "
      },
      {
        "line": 348,
        "text": "・the narrow confines of 〈場所・枠組み〉  "
      },
      {
        "line": 349,
        "text": "用途: 物理的・抽象的な範囲が狭く、制約的であることを強調する。  "
      },
      {
        "line": 350,
        "text": "例: The story moves beyond the narrow confines of a family dispute.  "
      },
      {
        "line": 351,
        "text": "訳: その物語は家族間の争いという狭い枠を越えて展開する。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 79,
        "text": "【類義語】"
      },
      {
        "line": 81,
        "text": "・limit  "
      },
      {
        "line": 82,
        "text": "定義: 数量、範囲、程度、時間などに限度を設ける。  "
      },
      {
        "line": 83,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 84,
        "text": "違い: limit は最も広く中立的で、上限を設ける場合にも使う。confine は対象をある境界の内側にとどめ、外へ広げないイメージが強い。  "
      },
      {
        "line": 85,
        "text": "例: The policy limits each application to two pages.  "
      },
      {
        "line": 86,
        "text": "訳: その方針では各申請書を2ページまでに制限している。  "
      },
      {
        "line": 88,
        "text": "・restrict  "
      },
      {
        "line": 89,
        "text": "定義: 規則、条件、権限などによって範囲や自由を制限する。  "
      },
      {
        "line": 90,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 91,
        "text": "違い: restrict は許可・利用・行動への制約を広く表す。confine A to B は、AがBの外へ及ばないという境界を特に示す。  "
      },
      {
        "line": 92,
        "text": "例: Access is restricted to authorized staff.  "
      },
      {
        "line": 93,
        "text": "訳: 立ち入りは権限のある職員に制限されている。  "
      },
      {
        "line": 95,
        "text": "・circumscribe  "
      },
      {
        "line": 96,
        "text": "定義: 活動、権限、可能性などの範囲を狭く限定する。  "
      },
      {
        "line": 97,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 98,
        "text": "違い: circumscribe は非常に硬い語で、抽象的な権限・選択肢・行動範囲が制約される文脈に多い。confine の方が一般的で、具体的な場所にも使える。  "
      },
      {
        "line": 99,
        "text": "例: The constitution circumscribes the powers of the executive.  "
      },
      {
        "line": 100,
        "text": "訳: 憲法は行政府の権限の範囲を限定している。  "
      },
      {
        "line": 102,
        "text": "【反意語】"
      },
      {
        "line": 104,
        "text": "・broaden  "
      },
      {
        "line": 105,
        "text": "定義: 話題、活動、対象などの範囲を広げる。  "
      },
      {
        "line": 106,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 107,
        "text": "違い: 範囲を狭く限定する confine と、同じ範囲軸上で外側へ広げる方向の対立をなす。  "
      },
      {
        "line": 108,
        "text": "例: The committee broadened the inquiry to include safety concerns.  "
      },
      {
        "line": 109,
        "text": "訳: 委員会は安全上の懸念も含めるよう調査範囲を広げた。  "
      },
      {
        "line": 111,
        "text": "・extend  "
      },
      {
        "line": 112,
        "text": "定義: 対象となる範囲、期間、適用先などをさらに先まで広げる。  "
      },
      {
        "line": 113,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 114,
        "text": "違い: confine A to B がAの到達範囲をB内に止めるのに対し、extend A to B はAの到達範囲をBまで広げる。  "
      },
      {
        "line": 115,
        "text": "例: The program was extended to smaller communities.  "
      },
      {
        "line": 116,
        "text": "訳: その制度はより小さな地域にも拡大された。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 152,
        "text": "【類義語】"
      },
      {
        "line": 154,
        "text": "・imprison  "
      },
      {
        "line": 155,
        "text": "定義: 人を刑務所などに入れて自由を奪う。  "
      },
      {
        "line": 156,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 157,
        "text": "違い: imprison は刑罰・政治的拘禁など人の収監を中心とする。confine は人以外の動物や、刑務所以外の限定された場所にも使える。  "
      },
      {
        "line": 158,
        "text": "例: The regime imprisoned several opposition leaders.  "
      },
      {
        "line": 159,
        "text": "訳: その政権は複数の反対派指導者を投獄した。  "
      },
      {
        "line": 161,
        "text": "・detain  "
      },
      {
        "line": 162,
        "text": "定義: 当局などが人を一定時間引き留め、立ち去れないようにする。  "
      },
      {
        "line": 163,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 164,
        "text": "違い: detain は一時的な身柄拘束や事情聴取のための留置に焦点がある。confine は場所の境界内に置かれる状態を強く示す。  "
      },
      {
        "line": 165,
        "text": "例: Police detained the suspect for questioning.  "
      },
      {
        "line": 166,
        "text": "訳: 警察は事情聴取のため容疑者を拘束した。  "
      },
      {
        "line": 168,
        "text": "・enclose  "
      },
      {
        "line": 169,
        "text": "定義: 物や場所の周囲を囲い、その内側に収める。  "
      },
      {
        "line": 170,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 171,
        "text": "違い: enclose は囲いを作ることに焦点があり、対象の自由を奪う含みは必須ではない。confine は外へ出られないという制限を前面に出す。  "
      },
      {
        "line": 172,
        "text": "例: A stone wall enclosed the garden.  "
      },
      {
        "line": 173,
        "text": "訳: 石垣が庭を取り囲んでいた。  "
      },
      {
        "line": 175,
        "text": "【反意語】"
      },
      {
        "line": 177,
        "text": "・release  "
      },
      {
        "line": 178,
        "text": "定義: 拘束・収容されている人や動物を自由にする。  "
      },
      {
        "line": 179,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 180,
        "text": "違い: 閉鎖場所内にとどめる confine に対し、そこから出ることを許す方向の対立をなす。  "
      },
      {
        "line": 181,
        "text": "例: The authorities released the detainees the next morning.  "
      },
      {
        "line": 182,
        "text": "訳: 当局は翌朝、被拘束者たちを解放した。  "
      },
      {
        "line": 184,
        "text": "・free  "
      },
      {
        "line": 185,
        "text": "定義: 束縛、監禁、拘束などから自由にする。  "
      },
      {
        "line": 186,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 187,
        "text": "違い: confine が移動の自由を奪うのに対し、free はその拘束自体を取り除く。release より広く、物理的・制度的・比喩的拘束に使える。  "
      },
      {
        "line": 188,
        "text": "例: The rescue team freed the animals from the locked shed.  "
      },
      {
        "line": 189,
        "text": "訳: 救助隊は鍵のかかった小屋から動物たちを解放した。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 225,
        "text": "【類義語】"
      },
      {
        "line": 227,
        "text": "・be bedridden  "
      },
      {
        "line": 228,
        "text": "定義: 病気、けが、高齢などで寝床から離れられない状態にある。  "
      },
      {
        "line": 229,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 230,
        "text": "違い: be bedridden は比較的長い・重い状態を表しやすい形容詞表現である。be confined to bed は一時的な病気にも使える。  "
      },
      {
        "line": 231,
        "text": "例: He was bedridden for months after the stroke.  "
      },
      {
        "line": 232,
        "text": "訳: 彼は脳卒中の後、何か月も寝たきりだった。  "
      },
      {
        "line": 234,
        "text": "・be housebound  "
      },
      {
        "line": 235,
        "text": "定義: 身体状態などのため自宅から外出することが難しい。  "
      },
      {
        "line": 236,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 237,
        "text": "違い: be housebound は自宅の外へ出にくい状態そのものを表す。be confined to one's home は原因によって行動範囲が自宅内に限られたことを描く。  "
      },
      {
        "line": 238,
        "text": "例: The service delivers meals to older people who are housebound.  "
      },
      {
        "line": 239,
        "text": "訳: そのサービスは外出困難な高齢者に食事を届ける。  "
      },
      {
        "line": 241,
        "text": "・be restricted to 〈場所・活動〉  "
      },
      {
        "line": 242,
        "text": "定義: 許可や身体状態などにより、場所・活動の範囲が限られている。  "
      },
      {
        "line": 243,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 244,
        "text": "違い: be restricted to は原因を問わない中立的な制限表現である。be confined to は移動できない、または外へ出られないという強い制約を示しやすい。  "
      },
      {
        "line": 245,
        "text": "例: During recovery, she was restricted to light indoor activities.  "
      },
      {
        "line": 246,
        "text": "訳: 回復中、彼女の活動は屋内での軽いものに限られた。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 282,
        "text": "【類義語】"
      },
      {
        "line": 284,
        "text": "・enclosed  "
      },
      {
        "line": 285,
        "text": "定義: 壁、柵、覆いなどによって周囲を囲まれた。  "
      },
      {
        "line": 286,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 287,
        "text": "違い: enclosed は囲いの存在を表すが、狭さや窮屈さは必須ではない。confined は空間や動きが限られる含みを持ちやすい。  "
      },
      {
        "line": 288,
        "text": "例: The garden is surrounded by an enclosed walkway.  "
      },
      {
        "line": 289,
        "text": "訳: その庭は屋根と壁のある通路に囲まれている。  "
      },
      {
        "line": 291,
        "text": "・cramped  "
      },
      {
        "line": 292,
        "text": "定義: 人や物に対して利用できる空間が足りず、窮屈な。  "
      },
      {
        "line": 293,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 294,
        "text": "違い: cramped は狭さによる不快さを直接強調する。confined は境界に囲まれ、動きが制限される構造に焦点がある。  "
      },
      {
        "line": 295,
        "text": "例: Four people shared a cramped cabin.  "
      },
      {
        "line": 296,
        "text": "訳: 4人が窮屈な船室を共有した。  "
      },
      {
        "line": 298,
        "text": "・restricted  "
      },
      {
        "line": 299,
        "text": "定義: 利用、移動、範囲などが制限された。  "
      },
      {
        "line": 300,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 301,
        "text": "違い: restricted は規則や条件による抽象的制限にも広く使う。confined は特に空間的な閉鎖性を示しやすい。  "
      },
      {
        "line": 302,
        "text": "例: The equipment operates in a restricted area.  "
      },
      {
        "line": 303,
        "text": "訳: その装置は立ち入り制限区域で稼働している。  "
      },
      {
        "line": 305,
        "text": "【反意語】"
      },
      {
        "line": 307,
        "text": "・spacious  "
      },
      {
        "line": 308,
        "text": "定義: 人や物がゆったり動ける十分な空間がある。  "
      },
      {
        "line": 309,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 310,
        "text": "違い: 動ける余地が少ない confined と、空間に十分な余裕がある spacious は広さ・窮屈さの軸で対立する。  "
      },
      {
        "line": 311,
        "text": "例: The new cabin is bright and spacious.  "
      },
      {
        "line": 312,
        "text": "訳: 新しい船室は明るく広々としている。  "
      },
      {
        "line": 314,
        "text": "・open  "
      },
      {
        "line": 315,
        "text": "定義: 閉鎖されず、周囲や上部が広く開けている。  "
      },
      {
        "line": 316,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 317,
        "text": "違い: 境界に囲まれた confined に対し、open は閉鎖性が少なく外へ開かれた状態を表す。文脈によっては広さではなく出入り可能性の対立になる。  "
      },
      {
        "line": 318,
        "text": "例: We moved the meeting to an open area outside.  "
      },
      {
        "line": 319,
        "text": "訳: 私たちは会議を屋外の開けた場所に移した。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 355,
        "text": "【類義語】"
      },
      {
        "line": 357,
        "text": "・bounds  "
      },
      {
        "line": 358,
        "text": "定義: 許容範囲、領域、行動などの境界・限界。  "
      },
      {
        "line": 359,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 360,
        "text": "違い: bounds も通常複数で、out of bounds など定着表現が多い。confines は境界に囲まれた内部の領域まで意識させやすく、より格式的である。  "
      },
      {
        "line": 361,
        "text": "例: The proposal falls outside the bounds of the agreement.  "
      },
      {
        "line": 362,
        "text": "訳: その提案は合意の範囲外である。  "
      },
      {
        "line": 364,
        "text": "・limits  "
      },
      {
        "line": 365,
        "text": "定義: 範囲、能力、権限などがそれ以上及ばない境界。  "
      },
      {
        "line": 366,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 367,
        "text": "違い: limits は最も一般的で、数量的な上限にも使える。confines は場所・制度・分野を囲む境界や領域を表す格式的な語である。  "
      },
      {
        "line": 368,
        "text": "例: The plan remains within the limits of the current budget.  "
      },
      {
        "line": 369,
        "text": "訳: その計画は現在の予算の範囲内に収まっている。  "
      },
      {
        "line": 371,
        "text": "・boundaries  "
      },
      {
        "line": 372,
        "text": "定義: 場所、分野、関係などを内外に分ける境界。  "
      },
      {
        "line": 373,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 374,
        "text": "違い: boundaries は境界線や区分そのものに焦点がある。confines はその線で囲まれた範囲を含めて指すことがある。  "
      },
      {
        "line": 375,
        "text": "例: The research crosses traditional disciplinary boundaries.  "
      },
      {
        "line": 376,
        "text": "訳: その研究は従来の学問分野の境界を越えている。  "
      }
    ],
    "antonym_axis_items": [
      {
        "item_id": "ant-feae1bb49aaa",
        "stage1_axis": {
          "item_id": "ant-feae1bb49aaa",
          "axis": "範囲",
          "relation_type": "方向",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 104,
          "line_end": 104,
          "exact_quote": "・broaden  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 107,
          "line_end": 107,
          "exact_quote": "違い: 範囲を狭く限定する confine と、同じ範囲軸上で外側へ広げる方向の対立をなす。  "
        }
      },
      {
        "item_id": "ant-5c13f3df07ec",
        "stage1_axis": {
          "item_id": "ant-5c13f3df07ec",
          "axis": "範囲",
          "relation_type": "方向",
          "reason": ""
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 111,
          "line_end": 111,
          "exact_quote": "・extend  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 114,
          "line_end": 114,
          "exact_quote": "違い: confine A to B がAの到達範囲をB内に止めるのに対し、extend A to B はAの到達範囲をBまで広げる。  "
        }
      },
      {
        "item_id": "ant-7700f7ce4e98",
        "stage1_axis": {
          "item_id": "ant-7700f7ce4e98",
          "axis": "拘束",
          "relation_type": "方向",
          "reason": ""
        },
        "sense_id": "sense:002",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 177,
          "line_end": 177,
          "exact_quote": "・release  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 180,
          "line_end": 180,
          "exact_quote": "違い: 閉鎖場所内にとどめる confine に対し、そこから出ることを許す方向の対立をなす。  "
        }
      },
      {
        "item_id": "ant-2ff0cbbd0f84",
        "stage1_axis": {
          "item_id": "ant-2ff0cbbd0f84",
          "axis": "拘束",
          "relation_type": "方向",
          "reason": ""
        },
        "sense_id": "sense:002",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 184,
          "line_end": 184,
          "exact_quote": "・free  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 187,
          "line_end": 187,
          "exact_quote": "違い: confine が移動の自由を奪うのに対し、free はその拘束自体を取り除く。release より広く、物理的・制度的・比喩的拘束に使える。  "
        }
      },
      {
        "item_id": "ant-cd0cd6b18ff8",
        "stage1_axis": {
          "item_id": "ant-cd0cd6b18ff8",
          "axis": "広さ",
          "relation_type": "程度",
          "reason": ""
        },
        "sense_id": "sense:004",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 307,
          "line_end": 307,
          "exact_quote": "・spacious  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 310,
          "line_end": 310,
          "exact_quote": "違い: 動ける余地が少ない confined と、空間に十分な余裕がある spacious は広さ・窮屈さの軸で対立する。  "
        }
      },
      {
        "item_id": "ant-c0dc5dadb561",
        "stage1_axis": {
          "item_id": "ant-c0dc5dadb561",
          "axis": "開放性",
          "relation_type": "状態",
          "reason": ""
        },
        "sense_id": "sense:004",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 314,
          "line_end": 314,
          "exact_quote": "・open  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 317,
          "line_end": 317,
          "exact_quote": "違い: 境界に囲まれた confined に対し、open は閉鎖性が少なく外へ開かれた状態を表す。文脈によっては広さではなく出入り可能性の対立になる。  "
        }
      }
    ],
    "antonym_axis_senses": [
      {
        "sense_id": "sense:001",
        "full_sense": [
          {
            "line": 40,
            "text": "1. 【他動詞】～を…に限る、限定する"
          },
          {
            "line": 42,
            "text": "【日本語訳・定義】話題、活動、作業、影響、現象などが及ぶ範囲を、特定の対象・場所・期間・分野などの内側に限定する。対象がすでにその範囲に収まっていることを述べる受動形と、話し手が意識的に扱う範囲を絞る能動形・再帰形の両方がよく使われる。  "
          },
          {
            "line": 44,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 46,
            "text": "【レジスター/領域】一般語だが、日常会話より文章、ニュース、ビジネス、学術的説明でやや多い。  "
          },
          {
            "line": 48,
            "text": "【文法パターン】confine something to 〈範囲・場所・期間・活動〉＝何かを～の範囲内に限る／confine oneself to 〈名詞・doing〉＝自分が扱う内容・行うことを～だけにする／be confined to 〈範囲・場所・集団〉＝～に限られている／confine 〈発言・検討・努力〉 to 〈対象〉＝発言・検討・努力の対象を～に絞る  "
          },
          {
            "line": 50,
            "text": "【コロケーション】"
          },
          {
            "line": 52,
            "text": "・confine the discussion to 〈話題〉  "
          },
          {
            "line": 53,
            "text": "用途: 議論で扱う範囲を特定の話題に限定する。  "
          },
          {
            "line": 54,
            "text": "例: Please confine the discussion to the issues on today's agenda.  "
          },
          {
            "line": 55,
            "text": "訳: 議論は本日の議題にある問題だけに絞ってください。  "
          },
          {
            "line": 57,
            "text": "・confine one's remarks to 〈対象〉  "
          },
          {
            "line": 58,
            "text": "用途: 発言する内容を特定の対象に限る。  "
          },
          {
            "line": 59,
            "text": "例: She confined her remarks to the financial risks of the proposal.  "
          },
          {
            "line": 60,
            "text": "訳: 彼女は発言をその提案の財務上のリスクに限定した。  "
          },
          {
            "line": 62,
            "text": "・confine oneself to 〈名詞・doing〉  "
          },
          {
            "line": 63,
            "text": "用途: 自分が扱う話題や行う活動を意識的に一つの範囲へ絞る。  "
          },
          {
            "line": 64,
            "text": "例: In this chapter, I will confine myself to examining the short-term effects.  "
          },
          {
            "line": 65,
            "text": "訳: この章では、短期的な影響の検討だけに対象を絞る。  "
          },
          {
            "line": 67,
            "text": "・be confined to 〈場所・集団〉  "
          },
          {
            "line": 68,
            "text": "用途: 問題、特徴、現象などが特定の場所や集団だけに見られることを表す。  "
          },
          {
            "line": 69,
            "text": "例: The shortage is not confined to rural areas.  "
          },
          {
            "line": 70,
            "text": "訳: その不足は農村部だけに限られた問題ではない。  "
          },
          {
            "line": 72,
            "text": "・confine 〈物質・作用〉 to 〈区域・装置〉  "
          },
          {
            "line": 73,
            "text": "用途: 物質、熱、火、プラズマなどが外へ広がらないよう一定の区域内に保つ。  "
          },
          {
            "line": 74,
            "text": "例: The magnetic field confines the plasma to the center of the chamber.  "
          },
          {
            "line": 75,
            "text": "訳: その磁場はプラズマを容器の中心部に閉じ込める。  "
          },
          {
            "line": 77,
            "text": "【語法・注意】基本形は confine A to B であり、to の後ろには名詞または動名詞を置く。×confine A in doing B のように範囲を示す前置詞を機械的に in に替えない。場所の内部へ物理的に閉じ込める語義2では confine someone in a cell のように in も使う。confine oneself to は「自分を物理的に閉じ込める」ではなく、通常「話題・活動を自分で限定する」という再帰構文である。受動形 be confined to は、否定や mainly、largely などと結び付き、「～だけに限られる／限られない」を表しやすい。  "
          },
          {
            "line": 79,
            "text": "【類義語】"
          },
          {
            "line": 81,
            "text": "・limit  "
          },
          {
            "line": 82,
            "text": "定義: 数量、範囲、程度、時間などに限度を設ける。  "
          },
          {
            "line": 83,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 84,
            "text": "違い: limit は最も広く中立的で、上限を設ける場合にも使う。confine は対象をある境界の内側にとどめ、外へ広げないイメージが強い。  "
          },
          {
            "line": 85,
            "text": "例: The policy limits each application to two pages.  "
          },
          {
            "line": 86,
            "text": "訳: その方針では各申請書を2ページまでに制限している。  "
          },
          {
            "line": 88,
            "text": "・restrict  "
          },
          {
            "line": 89,
            "text": "定義: 規則、条件、権限などによって範囲や自由を制限する。  "
          },
          {
            "line": 90,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 91,
            "text": "違い: restrict は許可・利用・行動への制約を広く表す。confine A to B は、AがBの外へ及ばないという境界を特に示す。  "
          },
          {
            "line": 92,
            "text": "例: Access is restricted to authorized staff.  "
          },
          {
            "line": 93,
            "text": "訳: 立ち入りは権限のある職員に制限されている。  "
          },
          {
            "line": 95,
            "text": "・circumscribe  "
          },
          {
            "line": 96,
            "text": "定義: 活動、権限、可能性などの範囲を狭く限定する。  "
          },
          {
            "line": 97,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 98,
            "text": "違い: circumscribe は非常に硬い語で、抽象的な権限・選択肢・行動範囲が制約される文脈に多い。confine の方が一般的で、具体的な場所にも使える。  "
          },
          {
            "line": 99,
            "text": "例: The constitution circumscribes the powers of the executive.  "
          },
          {
            "line": 100,
            "text": "訳: 憲法は行政府の権限の範囲を限定している。  "
          },
          {
            "line": 102,
            "text": "【反意語】"
          },
          {
            "line": 104,
            "text": "・broaden  "
          },
          {
            "line": 105,
            "text": "定義: 話題、活動、対象などの範囲を広げる。  "
          },
          {
            "line": 106,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 107,
            "text": "違い: 範囲を狭く限定する confine と、同じ範囲軸上で外側へ広げる方向の対立をなす。  "
          },
          {
            "line": 108,
            "text": "例: The committee broadened the inquiry to include safety concerns.  "
          },
          {
            "line": 109,
            "text": "訳: 委員会は安全上の懸念も含めるよう調査範囲を広げた。  "
          },
          {
            "line": 111,
            "text": "・extend  "
          },
          {
            "line": 112,
            "text": "定義: 対象となる範囲、期間、適用先などをさらに先まで広げる。  "
          },
          {
            "line": 113,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 114,
            "text": "違い: confine A to B がAの到達範囲をB内に止めるのに対し、extend A to B はAの到達範囲をBまで広げる。  "
          },
          {
            "line": 115,
            "text": "例: The program was extended to smaller communities.  "
          },
          {
            "line": 116,
            "text": "訳: その制度はより小さな地域にも拡大された。  "
          }
        ]
      },
      {
        "sense_id": "sense:002",
        "full_sense": [
          {
            "line": 118,
            "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
          },
          {
            "line": 120,
            "text": "【日本語訳・定義】人や動物を、部屋、施設、囲い、刑務所などの外へ自由に出られないようにする。物理的な障壁、命令、拘禁などによる移動の制限を表し、本人の自由意思で滞在している場合には通常使わない。  "
          },
          {
            "line": 122,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 124,
            "text": "【レジスター/領域】一般語。ニュース、法律・刑事、軍事、動物管理の文脈でよく使われる。  "
          },
          {
            "line": 126,
            "text": "【文法パターン】confine someone/something in 〈閉鎖場所〉＝人・動物を～の中に閉じ込める／confine someone/something to 〈場所〉＝人・動物を～から出られないようにする／be confined in 〈施設・部屋〉＝～に収容・拘束されている／be confined to quarters＝兵舎・自室待機を命じられている  "
          },
          {
            "line": 128,
            "text": "【コロケーション】"
          },
          {
            "line": 130,
            "text": "・confine someone in a cell  "
          },
          {
            "line": 131,
            "text": "用途: 人を独房などの閉鎖された空間から出られないようにする。  "
          },
          {
            "line": 132,
            "text": "例: The prisoner was confined in a windowless cell for several days.  "
          },
          {
            "line": 133,
            "text": "訳: その囚人は数日間、窓のない独房に拘禁された。  "
          },
          {
            "line": 135,
            "text": "・confine an animal to 〈囲い・ケージ〉  "
          },
          {
            "line": 136,
            "text": "用途: 動物が指定された囲いの外へ出ないようにする。  "
          },
          {
            "line": 137,
            "text": "例: The injured bird was temporarily confined to a large enclosure.  "
          },
          {
            "line": 138,
            "text": "訳: けがをした鳥は一時的に大きな囲いの中で保護された。  "
          },
          {
            "line": 140,
            "text": "・keep 〈人・動物〉 confined  "
          },
          {
            "line": 141,
            "text": "用途: 人や動物を外へ出られない状態に保つ。  "
          },
          {
            "line": 142,
            "text": "例: The order kept the soldiers confined to their barracks overnight.  "
          },
          {
            "line": 143,
            "text": "訳: その命令により兵士たちは一晩、兵舎から出られなかった。  "
          },
          {
            "line": 145,
            "text": "・be confined to quarters  "
          },
          {
            "line": 146,
            "text": "用途: 軍人などが処罰・命令により兵舎や指定場所から出ないよう命じられた状態を表す。  "
          },
          {
            "line": 147,
            "text": "例: He was confined to quarters for disobeying the order.  "
          },
          {
            "line": 148,
            "text": "訳: 彼は命令に従わなかったため、兵舎待機を命じられた。  "
          },
          {
            "line": 150,
            "text": "【語法・注意】この語義では能動形も可能だが、拘束される側を主語にした be confined in/to が多い。in は容器・部屋・施設の「内部」を、to は移動可能な「範囲」を示す。imprison は人を刑務所に入れる法的・物理的な拘禁に焦点があり、動物や一時的な行動制限には使いにくい。confine は刑罰に限らず、命令や安全上の理由による拘束にも使える。  "
          },
          {
            "line": 152,
            "text": "【類義語】"
          },
          {
            "line": 154,
            "text": "・imprison  "
          },
          {
            "line": 155,
            "text": "定義: 人を刑務所などに入れて自由を奪う。  "
          },
          {
            "line": 156,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 157,
            "text": "違い: imprison は刑罰・政治的拘禁など人の収監を中心とする。confine は人以外の動物や、刑務所以外の限定された場所にも使える。  "
          },
          {
            "line": 158,
            "text": "例: The regime imprisoned several opposition leaders.  "
          },
          {
            "line": 159,
            "text": "訳: その政権は複数の反対派指導者を投獄した。  "
          },
          {
            "line": 161,
            "text": "・detain  "
          },
          {
            "line": 162,
            "text": "定義: 当局などが人を一定時間引き留め、立ち去れないようにする。  "
          },
          {
            "line": 163,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 164,
            "text": "違い: detain は一時的な身柄拘束や事情聴取のための留置に焦点がある。confine は場所の境界内に置かれる状態を強く示す。  "
          },
          {
            "line": 165,
            "text": "例: Police detained the suspect for questioning.  "
          },
          {
            "line": 166,
            "text": "訳: 警察は事情聴取のため容疑者を拘束した。  "
          },
          {
            "line": 168,
            "text": "・enclose  "
          },
          {
            "line": 169,
            "text": "定義: 物や場所の周囲を囲い、その内側に収める。  "
          },
          {
            "line": 170,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 171,
            "text": "違い: enclose は囲いを作ることに焦点があり、対象の自由を奪う含みは必須ではない。confine は外へ出られないという制限を前面に出す。  "
          },
          {
            "line": 172,
            "text": "例: A stone wall enclosed the garden.  "
          },
          {
            "line": 173,
            "text": "訳: 石垣が庭を取り囲んでいた。  "
          },
          {
            "line": 175,
            "text": "【反意語】"
          },
          {
            "line": 177,
            "text": "・release  "
          },
          {
            "line": 178,
            "text": "定義: 拘束・収容されている人や動物を自由にする。  "
          },
          {
            "line": 179,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 180,
            "text": "違い: 閉鎖場所内にとどめる confine に対し、そこから出ることを許す方向の対立をなす。  "
          },
          {
            "line": 181,
            "text": "例: The authorities released the detainees the next morning.  "
          },
          {
            "line": 182,
            "text": "訳: 当局は翌朝、被拘束者たちを解放した。  "
          },
          {
            "line": 184,
            "text": "・free  "
          },
          {
            "line": 185,
            "text": "定義: 束縛、監禁、拘束などから自由にする。  "
          },
          {
            "line": 186,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 187,
            "text": "違い: confine が移動の自由を奪うのに対し、free はその拘束自体を取り除く。release より広く、物理的・制度的・比喩的拘束に使える。  "
          },
          {
            "line": 188,
            "text": "例: The rescue team freed the animals from the locked shed.  "
          },
          {
            "line": 189,
            "text": "訳: 救助隊は鍵のかかった小屋から動物たちを解放した。  "
          }
        ]
      },
      {
        "sense_id": "sense:004",
        "full_sense": [
          {
            "line": 248,
            "text": "4. 【形容詞】狭く囲まれた、限られた"
          },
          {
            "line": 250,
            "text": "【日本語訳・定義】confined の形で、空間や区域が壁や境界に囲まれて狭い、または内部で動ける余地が少ないことを表す。単に面積が小さいだけでなく、閉鎖性や動きにくさを含みやすい。  "
          },
          {
            "line": 252,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 254,
            "text": "【レジスター/領域】一般語。confined space は日常的説明のほか、労働安全の専門用語としても使われる。  "
          },
          {
            "line": 256,
            "text": "【文法パターン】a confined 〈space/area/place〉＝狭く囲まれた空間・区域／in confined 〈conditions/quarters〉＝狭く限られた環境で／feel confined＝閉じ込められたように感じる  "
          },
          {
            "line": 258,
            "text": "【コロケーション】"
          },
          {
            "line": 260,
            "text": "・a confined space  "
          },
          {
            "line": 261,
            "text": "用途: 壁や境界に囲まれ、動きや出入りが制限されやすい空間を表す。  "
          },
          {
            "line": 262,
            "text": "例: The machine should not be operated in a confined space without adequate ventilation.  "
          },
          {
            "line": 263,
            "text": "訳: その機械は、十分な換気のない閉鎖空間で作動させるべきではない。  "
          },
          {
            "line": 265,
            "text": "・in confined quarters  "
          },
          {
            "line": 266,
            "text": "用途: 人が動ける余地の少ない狭い居住・作業場所にいることを表す。  "
          },
          {
            "line": 267,
            "text": "例: The crew lived in confined quarters during the voyage.  "
          },
          {
            "line": 268,
            "text": "訳: 乗組員は航海中、狭い居住区で暮らした。  "
          },
          {
            "line": 270,
            "text": "・work in confined conditions  "
          },
          {
            "line": 271,
            "text": "用途: 動作や移動の余地が限られた環境で作業する。  "
          },
          {
            "line": 272,
            "text": "例: The technicians had to work in confined conditions beneath the stage.  "
          },
          {
            "line": 273,
            "text": "訳: 技術者たちは舞台の下の狭い環境で作業しなければならなかった。  "
          },
          {
            "line": 275,
            "text": "・feel confined in 〈場所〉  "
          },
          {
            "line": 276,
            "text": "用途: 場所が狭い、または自由に動けず、閉じ込められたように感じる。  "
          },
          {
            "line": 277,
            "text": "例: I felt confined in the tiny room after only a few hours.  "
          },
          {
            "line": 278,
            "text": "訳: その小さな部屋に数時間いただけで、私は閉じ込められたように感じた。  "
          },
          {
            "line": 280,
            "text": "【語法・注意】confined space は一般には狭く囲まれた空間を表すが、労働安全上の専門用語では法域や制度ごとに定義・要件があるため、小さい部屋をすべて専門上の confined space と断定しない。be confined to 〈場所・範囲〉は動詞 confine の受動形で「～に限定・拘束されている」、a confined space は形容詞 confined が名詞を修飾して「狭く囲まれた空間」である。  "
          },
          {
            "line": 282,
            "text": "【類義語】"
          },
          {
            "line": 284,
            "text": "・enclosed  "
          },
          {
            "line": 285,
            "text": "定義: 壁、柵、覆いなどによって周囲を囲まれた。  "
          },
          {
            "line": 286,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 287,
            "text": "違い: enclosed は囲いの存在を表すが、狭さや窮屈さは必須ではない。confined は空間や動きが限られる含みを持ちやすい。  "
          },
          {
            "line": 288,
            "text": "例: The garden is surrounded by an enclosed walkway.  "
          },
          {
            "line": 289,
            "text": "訳: その庭は屋根と壁のある通路に囲まれている。  "
          },
          {
            "line": 291,
            "text": "・cramped  "
          },
          {
            "line": 292,
            "text": "定義: 人や物に対して利用できる空間が足りず、窮屈な。  "
          },
          {
            "line": 293,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 294,
            "text": "違い: cramped は狭さによる不快さを直接強調する。confined は境界に囲まれ、動きが制限される構造に焦点がある。  "
          },
          {
            "line": 295,
            "text": "例: Four people shared a cramped cabin.  "
          },
          {
            "line": 296,
            "text": "訳: 4人が窮屈な船室を共有した。  "
          },
          {
            "line": 298,
            "text": "・restricted  "
          },
          {
            "line": 299,
            "text": "定義: 利用、移動、範囲などが制限された。  "
          },
          {
            "line": 300,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 301,
            "text": "違い: restricted は規則や条件による抽象的制限にも広く使う。confined は特に空間的な閉鎖性を示しやすい。  "
          },
          {
            "line": 302,
            "text": "例: The equipment operates in a restricted area.  "
          },
          {
            "line": 303,
            "text": "訳: その装置は立ち入り制限区域で稼働している。  "
          },
          {
            "line": 305,
            "text": "【反意語】"
          },
          {
            "line": 307,
            "text": "・spacious  "
          },
          {
            "line": 308,
            "text": "定義: 人や物がゆったり動ける十分な空間がある。  "
          },
          {
            "line": 309,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 310,
            "text": "違い: 動ける余地が少ない confined と、空間に十分な余裕がある spacious は広さ・窮屈さの軸で対立する。  "
          },
          {
            "line": 311,
            "text": "例: The new cabin is bright and spacious.  "
          },
          {
            "line": 312,
            "text": "訳: 新しい船室は明るく広々としている。  "
          },
          {
            "line": 314,
            "text": "・open  "
          },
          {
            "line": 315,
            "text": "定義: 閉鎖されず、周囲や上部が広く開けている。  "
          },
          {
            "line": 316,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 317,
            "text": "違い: 境界に囲まれた confined に対し、open は閉鎖性が少なく外へ開かれた状態を表す。文脈によっては広さではなく出入り可能性の対立になる。  "
          },
          {
            "line": 318,
            "text": "例: We moved the meeting to an open area outside.  "
          },
          {
            "line": 319,
            "text": "訳: 私たちは会議を屋外の開けた場所に移した。  "
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
