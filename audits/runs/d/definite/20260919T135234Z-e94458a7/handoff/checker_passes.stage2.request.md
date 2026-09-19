# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`reviewer-definite-frame-relation-20260919`, declared_model=`gpt-6-astra`.

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
  "input_body_sha256": "6bf439cde2a5a009f8e4e4d27f7041f7af5c66dd15e9e51aaf59bfb705b46752",
  "blind_request_sha256": "b295dc96952152716214e3e8cfd5e5666a4da5a8e6b280aec2c4447030e67c33",
  "blind_record_sha256": "7bd2966f5f112b47b8cf79b92a71a3ad04b2831e0fb27f7de9171f46a750c80e",
  "input_sections": {
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】答え、決定、計画、日付、合意、意図などが、曖昧な候補や一時的な案ではなく、内容として定まり、変更される可能性が低いことを表す。必ずしも今後絶対に変更できないという意味ではなく、現時点で決定・約束・判断が明確になっていることに焦点がある。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
      },
      {
        "line": 156,
        "text": "【日本語訳・定義】変化、差、効果、兆候、利点などが、観察や比較によって実際に認められるほど明瞭・顕著であることを表す。必ずしも論理的に証明済み、絶対に疑いがないという意味ではなく、話し手が変化や特徴をはっきり認識しているという評価を含むことがある。  "
      },
      {
        "line": 268,
        "text": "3. 【形容詞・限定用法】具体的な、特定の"
      },
      {
        "line": 270,
        "text": "【日本語訳・定義】数量、期間、範囲、時点、形、情報などに明確な境界や内容があり、漠然としたものではないことを表す。特定の対象を指す場合でも、文脈上その対象を識別できるという文法上の意味とは異なり、ここでは内容・範囲・条件が具体的に定まっていることに焦点がある。  "
      },
      {
        "line": 384,
        "text": "4. 【形容詞・文法用語】定の、特定できる"
      },
      {
        "line": 386,
        "text": "【日本語訳・定義】文法で、名詞句の指示対象が、既出、状況上の唯一性、修飾語、共有知識などによって聞き手・読み手に特定可能であることを表す。英語では the が definite article「定冠詞」であり、対象が必ず世界に一つしかないこと、単数であること、以前に必ず言及されたことだけを意味するわけではない。  "
      },
      {
        "line": 474,
        "text": "5. 【形容詞・植物学】有限の、定数の"
      },
      {
        "line": 476,
        "text": "【日本語訳・定義】植物学で、花器官の数が一定で、通常は20未満で花弁数の倍数になること、または花序の主軸が花で終わり成長に限りがあることを表す専門用法である。一般語の「確実な」ではなく、数や成長が定まっているという意味で、definite inflorescence は determinate／cymose inflorescence に当たる。  "
      }
    ],
    "frames": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
      },
      {
        "line": 48,
        "text": "【文法パターン】a definite answer/decision/plan/date/deadline＝確定した答え・決定・計画・日付・期限／a definite agreement/offer/commitment＝明確に成立した合意・正式な申し出・確約／have no definite plans/ideas＝決まった計画・具体的な考えがない／anything/nothing definite＝何か／何も確定したもの／be definite about something＝ある事柄について態度・内容を明確にする／a definite yes/no＝はっきりした賛成／拒否。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
      },
      {
        "line": 162,
        "text": "【文法パターン】a definite improvement/change/difference＝明らかな改善・変化・違い／a definite sign/indication of something＝～の明らかな兆候・指標／have a definite effect/impact on something＝ある物事に明確な効果・影響を及ぼす／a definite advantage/disadvantage＝明確な利点・不利／a definite possibility＝現実味のある可能性／see/feel a definite difference＝はっきり違いを感じる。  "
      },
      {
        "line": 268,
        "text": "3. 【形容詞・限定用法】具体的な、特定の"
      },
      {
        "line": 276,
        "text": "【文法パターン】a definite amount/number/quantity/period＝具体的な量・数・期間／at a definite time/stage＝特定の時点・段階で／within definite limits＝明確な範囲内で／definite information/details＝具体的な情報・詳細／a definite shape/form＝はっきり定まった形・形式／a definite integral＝定積分。  "
      },
      {
        "line": 384,
        "text": "4. 【形容詞・文法用語】定の、特定できる"
      },
      {
        "line": 392,
        "text": "【文法パターン】the definite article＝定冠詞 the／a definite noun phrase＝定名詞句／definite reference to 〈person/thing〉＝〈人・物〉への定の指示／a definite description of 〈person/thing〉＝〈人・物〉を同定する確定記述／a definite referent＝特定可能な指示対象／a noun phrase is definite＝名詞句が定である。  "
      },
      {
        "line": 474,
        "text": "5. 【形容詞・植物学】有限の、定数の"
      },
      {
        "line": 482,
        "text": "【文法パターン】definite stamens＝数が一定の雄しべ／a definite inflorescence＝主軸が花で終わる有限花序／definite growth＝成長が一定の段階で止まる定限成長。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
      },
      {
        "line": 50,
        "text": "【コロケーション】"
      },
      {
        "line": 52,
        "text": "・a definite answer  "
      },
      {
        "line": 53,
        "text": "用途: 予想や曖昧な返事ではなく、決定した答えを求める。  "
      },
      {
        "line": 54,
        "text": "例: We need a definite answer by Friday, not another tentative suggestion.  "
      },
      {
        "line": 55,
        "text": "訳: 私たちは金曜日までに、また別の仮案ではなく確定した答えを必要としている。  "
      },
      {
        "line": 57,
        "text": "・a definite date for 〈event〉  "
      },
      {
        "line": 58,
        "text": "用途: 行事・開始・発売などの日付が決まっていることを表す。  "
      },
      {
        "line": 59,
        "text": "例: The organizers have not announced a definite date for the launch.  "
      },
      {
        "line": 60,
        "text": "訳: 主催者は発売の確定した日付をまだ発表していない。  "
      },
      {
        "line": 62,
        "text": "・no definite plans  "
      },
      {
        "line": 63,
        "text": "用途: 将来の予定がまだ決まっていないことを表す。  "
      },
      {
        "line": 64,
        "text": "例: I have no definite plans for the weekend yet.  "
      },
      {
        "line": 65,
        "text": "訳: 私は週末の具体的な予定をまだ決めていない。  "
      },
      {
        "line": 67,
        "text": "・anything definite about something  "
      },
      {
        "line": 68,
        "text": "用途: ある事柄について確定した情報があるかを尋ねる。  "
      },
      {
        "line": 69,
        "text": "例: Do you know anything definite about when the train will leave?  "
      },
      {
        "line": 70,
        "text": "訳: 列車がいつ出るかについて、何か確定した情報を知っていますか。  "
      },
      {
        "line": 72,
        "text": "・a definite yes/no  "
      },
      {
        "line": 73,
        "text": "用途: ためらいや条件付きではない、明確な肯定・拒否を表す。  "
      },
      {
        "line": 74,
        "text": "例: Her reply was a definite no, so we stopped asking.  "
      },
      {
        "line": 75,
        "text": "訳: 彼女の返事は明確な拒否だったので、私たちは尋ねるのをやめた。  "
      },
      {
        "line": 77,
        "text": "・be definite about 〈decision/position〉  "
      },
      {
        "line": 78,
        "text": "用途: 決定や立場を曖昧にせず、はっきり示す。  "
      },
      {
        "line": 79,
        "text": "例: Please be definite about your position before the meeting begins.  "
      },
      {
        "line": 80,
        "text": "訳: 会議が始まる前に、自分の立場を明確にしてください。  "
      },
      {
        "line": 82,
        "text": "・a definite commitment to do  "
      },
      {
        "line": 83,
        "text": "用途: ある行動を実行するという明確な確約を表す。  "
      },
      {
        "line": 84,
        "text": "例: The grant requires a definite commitment to complete the project.  "
      },
      {
        "line": 85,
        "text": "訳: その助成金には、プロジェクトを完了するという明確な確約が必要だ。  "
      },
      {
        "line": 87,
        "text": "・a definite agreement  "
      },
      {
        "line": 88,
        "text": "用途: 条件や内容が定まり、当事者間で成立した合意を表す。  "
      },
      {
        "line": 89,
        "text": "例: No definite agreement had been reached by the end of the meeting.  "
      },
      {
        "line": 90,
        "text": "訳: 会議の終了時までに、確定した合意は成立していなかった。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
      },
      {
        "line": 164,
        "text": "【コロケーション】"
      },
      {
        "line": 166,
        "text": "・a definite improvement  "
      },
      {
        "line": 167,
        "text": "用途: 状態や成績が実際に良くなったと認められることを表す。  "
      },
      {
        "line": 168,
        "text": "例: The new treatment produced a definite improvement in her symptoms.  "
      },
      {
        "line": 169,
        "text": "訳: 新しい治療によって、彼女の症状には明らかな改善が見られた。  "
      },
      {
        "line": 171,
        "text": "・a definite difference between 〈A〉 and 〈B〉  "
      },
      {
        "line": 172,
        "text": "用途: 二つの対象の違いがはっきり認められることを表す。  "
      },
      {
        "line": 173,
        "text": "例: There is a definite difference between the two versions of the report.  "
      },
      {
        "line": 174,
        "text": "訳: その報告書の二つの版には明らかな違いがある。  "
      },
      {
        "line": 176,
        "text": "・a definite sign of something  "
      },
      {
        "line": 177,
        "text": "用途: ある状態や出来事を示す、見分けやすい兆候を表す。  "
      },
      {
        "line": 178,
        "text": "例: A sudden drop in demand is a definite sign of weakening consumer confidence.  "
      },
      {
        "line": 179,
        "text": "訳: 需要の急減は、消費者信頼感が弱まっている明らかな兆候だ。  "
      },
      {
        "line": 181,
        "text": "・have a definite effect on something  "
      },
      {
        "line": 182,
        "text": "用途: 行為・条件・政策などが、結果に明確な影響を与えることを表す。  "
      },
      {
        "line": 183,
        "text": "例: Sleep has a definite effect on how well people remember new information.  "
      },
      {
        "line": 184,
        "text": "訳: 睡眠は、人が新しい情報をどれだけよく覚えるかに明確な影響を及ぼす。  "
      },
      {
        "line": 186,
        "text": "・a definite advantage  "
      },
      {
        "line": 187,
        "text": "用途: 他と比べて認めやすい具体的な利点を強調する。  "
      },
      {
        "line": 188,
        "text": "例: The shorter route offers a definite advantage during the winter.  "
      },
      {
        "line": 189,
        "text": "訳: その短い経路は冬の間、明確な利点をもたらす。  "
      },
      {
        "line": 191,
        "text": "・a definite possibility  "
      },
      {
        "line": 192,
        "text": "用途: 単なる空想ではなく、現実に起こり得る可能性を表す。  "
      },
      {
        "line": 193,
        "text": "例: A delay is a definite possibility if the storm continues.  "
      },
      {
        "line": 194,
        "text": "訳: 嵐が続けば、遅延は十分に現実的な可能性だ。  "
      },
      {
        "line": 196,
        "text": "・see a definite change in something  "
      },
      {
        "line": 197,
        "text": "用途: 状態や傾向の変化を観察してはっきり認める。  "
      },
      {
        "line": 198,
        "text": "例: We can see a definite change in customer behavior after the price increase.  "
      },
      {
        "line": 199,
        "text": "訳: 値上げ後、顧客の行動に明らかな変化が見られる。  "
      },
      {
        "line": 201,
        "text": "・with a definite sense of 〈emotion〉  "
      },
      {
        "line": 202,
        "text": "用途: 表情・声・行動などに特定の感情が明確に表れている様子を示す。  "
      },
      {
        "line": 203,
        "text": "例: He left the room with a definite sense of relief.  "
      },
      {
        "line": 204,
        "text": "訳: 彼は明らかに安堵した様子で部屋を出た。  "
      },
      {
        "line": 268,
        "text": "3. 【形容詞・限定用法】具体的な、特定の"
      },
      {
        "line": 278,
        "text": "【コロケーション】"
      },
      {
        "line": 280,
        "text": "・a definite amount of 〈money/material〉  "
      },
      {
        "line": 281,
        "text": "用途: 金額や物質の量が一定の範囲・数量として定まっていることを表す。  "
      },
      {
        "line": 282,
        "text": "例: The machine requires a definite amount of oil to operate safely.  "
      },
      {
        "line": 283,
        "text": "訳: その機械を安全に稼働させるには、一定量の油が必要だ。  "
      },
      {
        "line": 285,
        "text": "・a definite number of 〈people/items〉  "
      },
      {
        "line": 286,
        "text": "用途: 人数や個数が曖昧でなく、決まった数であることを表す。  "
      },
      {
        "line": 287,
        "text": "例: Only a definite number of students can join the laboratory tour.  "
      },
      {
        "line": 288,
        "text": "訳: 研究室見学に参加できる学生数には上限が決まっている。  "
      },
      {
        "line": 290,
        "text": "・for a definite period  "
      },
      {
        "line": 291,
        "text": "用途: 期間の終点または長さがあらかじめ定められていることを表す。  "
      },
      {
        "line": 292,
        "text": "例: The equipment may be rented for a definite period of six months.  "
      },
      {
        "line": 293,
        "text": "訳: その設備は6か月という定められた期間、借りることができる。  "
      },
      {
        "line": 295,
        "text": "・within definite limits  "
      },
      {
        "line": 296,
        "text": "用途: 許容範囲や境界を明確に限定する。  "
      },
      {
        "line": 297,
        "text": "例: The temperature must remain within definite limits during transport.  "
      },
      {
        "line": 298,
        "text": "訳: 輸送中、温度は明確に定められた範囲内に保たなければならない。  "
      },
      {
        "line": 300,
        "text": "・definite information about 〈topic〉  "
      },
      {
        "line": 301,
        "text": "用途: 推測や噂ではなく、内容が確認できる具体的な情報を表す。  "
      },
      {
        "line": 302,
        "text": "例: We need definite information about the delivery schedule before placing the order.  "
      },
      {
        "line": 303,
        "text": "訳: 注文を出す前に、納入予定について具体的な情報が必要だ。  "
      },
      {
        "line": 305,
        "text": "・a definite shape/form  "
      },
      {
        "line": 306,
        "text": "用途: 輪郭や形式が一定で、別の形と区別できることを表す。  "
      },
      {
        "line": 307,
        "text": "例: The crystals grow into a definite shape under controlled conditions.  "
      },
      {
        "line": 308,
        "text": "訳: その結晶は、管理された条件下で一定の形に成長する。  "
      },
      {
        "line": 310,
        "text": "・a definite integral  "
      },
      {
        "line": 311,
        "text": "用途: 数学で、積分区間の上下端が指定された定積分を指す。  "
      },
      {
        "line": 312,
        "text": "例: The area under the curve can be calculated with a definite integral.  "
      },
      {
        "line": 313,
        "text": "訳: 曲線の下の面積は定積分で計算できる。  "
      },
      {
        "line": 384,
        "text": "4. 【形容詞・文法用語】定の、特定できる"
      },
      {
        "line": 394,
        "text": "【コロケーション】"
      },
      {
        "line": 396,
        "text": "・the definite article  "
      },
      {
        "line": 397,
        "text": "用途: 英語の the のように、聞き手・読み手が指示対象を特定できることを示す冠詞を指す。  "
      },
      {
        "line": 398,
        "text": "例: In English, the is the definite article used before singular and plural noun phrases.  "
      },
      {
        "line": 399,
        "text": "訳: 英語では the が、単数・複数の名詞句の前に使われる定冠詞である。  "
      },
      {
        "line": 401,
        "text": "・a definite noun phrase  "
      },
      {
        "line": 402,
        "text": "用途: 指示対象が文脈から特定可能な名詞句を指す。  "
      },
      {
        "line": 403,
        "text": "例: In “the book on the desk,” the whole phrase is a definite noun phrase.  "
      },
      {
        "line": 404,
        "text": "訳: 「机の上のその本」では、句全体が定名詞句である。  "
      },
      {
        "line": 406,
        "text": "・definite reference to 〈person/thing〉  "
      },
      {
        "line": 407,
        "text": "用途: ある人物・物を、聞き手がどれか判断できる形で指すことを表す。  "
      },
      {
        "line": 408,
        "text": "例: The article makes a definite reference to the company’s earlier report.  "
      },
      {
        "line": 409,
        "text": "訳: その記事は会社の以前の報告書を明確に指し示している。  "
      },
      {
        "line": 411,
        "text": "・a definite description of 〈person/thing〉  "
      },
      {
        "line": 412,
        "text": "用途: 固有名を使わず、記述によって指示対象を同定する表現を指す。  "
      },
      {
        "line": 413,
        "text": "例: “The first person to arrive” is a definite description in this context.  "
      },
      {
        "line": 414,
        "text": "訳: この文脈では、「最初に到着した人」は確定記述である。  "
      },
      {
        "line": 416,
        "text": "・a definite referent  "
      },
      {
        "line": 417,
        "text": "用途: 名詞句が指し示す、文脈上特定可能な対象を指す。  "
      },
      {
        "line": 418,
        "text": "例: The plural noun phrase can still have a definite referent.  "
      },
      {
        "line": 419,
        "text": "訳: 複数名詞句でも、指示対象を特定できる場合がある。  "
      },
      {
        "line": 421,
        "text": "・definite and indefinite articles  "
      },
      {
        "line": 422,
        "text": "用途: the と a/an のように、指示対象の特定可能性が異なる冠詞を対比する。  "
      },
      {
        "line": 423,
        "text": "例: The lesson contrasts definite and indefinite articles in everyday sentences.  "
      },
      {
        "line": 424,
        "text": "訳: その授業では、日常文における定冠詞と不定冠詞を対比している。  "
      },
      {
        "line": 474,
        "text": "5. 【形容詞・植物学】有限の、定数の"
      },
      {
        "line": 484,
        "text": "【コロケーション】"
      },
      {
        "line": 486,
        "text": "・definite stamens  "
      },
      {
        "line": 487,
        "text": "用途: 花弁数との関係で数が一定の雄しべを指す。  "
      },
      {
        "line": 488,
        "text": "例: The species has definite stamens, usually in a fixed multiple of the number of petals.  "
      },
      {
        "line": 489,
        "text": "訳: その種には、通常、花弁数の決まった倍数になる定数の雄しべがある。  "
      },
      {
        "line": 491,
        "text": "・a definite inflorescence  "
      },
      {
        "line": 492,
        "text": "用途: 主軸が花で終わり、伸長に限りがある有限花序を指す。  "
      },
      {
        "line": 493,
        "text": "例: The plant develops a definite inflorescence in which the main axis ends in a flower.  "
      },
      {
        "line": 494,
        "text": "訳: その植物は、主軸が花で終わる有限花序を形成する。  "
      },
      {
        "line": 496,
        "text": "・definite growth  "
      },
      {
        "line": 497,
        "text": "用途: 植物体や器官の成長が一定の段階で止まる定限成長を表す。  "
      },
      {
        "line": 498,
        "text": "例: Definite growth is common in some compact flowering plants.  "
      },
      {
        "line": 499,
        "text": "訳: 定限成長は、一部の小型の開花植物でよく見られる。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
      },
      {
        "line": 94,
        "text": "【類義語】"
      },
      {
        "line": 96,
        "text": "・certain  "
      },
      {
        "line": 97,
        "text": "定義: 疑いがなく、確かだと判断される。  "
      },
      {
        "line": 98,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 99,
        "text": "違い: certain は事実・未来・話者の確信を広く表す。definite は答えや予定が決定済みで曖昧でないことを表しやすい。  "
      },
      {
        "line": 100,
        "text": "例: I am certain that she will accept the offer.  "
      },
      {
        "line": 101,
        "text": "訳: 彼女がその申し出を受けると私は確信している。  "
      },
      {
        "line": 103,
        "text": "・settled  "
      },
      {
        "line": 104,
        "text": "定義: 議論や検討の後に、決定・合意されている。  "
      },
      {
        "line": 105,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 106,
        "text": "違い: settled は未決の状態が終わったことに焦点があり、definite は決まった内容が明確であることに焦点がある。  "
      },
      {
        "line": 107,
        "text": "例: The venue for the conference is now settled.  "
      },
      {
        "line": 108,
        "text": "訳: 会議の会場は今や決まっている。  "
      },
      {
        "line": 110,
        "text": "・firm  "
      },
      {
        "line": 111,
        "text": "定義: 意思・約束・態度が強く、簡単には変わらない。  "
      },
      {
        "line": 112,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 113,
        "text": "違い: firm は人の決意や約束の強さを示し、definite は決定内容や情報の確定性を示す。  "
      },
      {
        "line": 114,
        "text": "例: She made a firm promise to return the money.  "
      },
      {
        "line": 115,
        "text": "訳: 彼女はそのお金を返すと固く約束した。  "
      },
      {
        "line": 117,
        "text": "・fixed  "
      },
      {
        "line": 118,
        "text": "定義: 位置・日時・数量などが変更されないように定められている。  "
      },
      {
        "line": 119,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 120,
        "text": "違い: fixed は変更不能・変更予定なしという状態を強く示し、definite は曖昧さが解消されていることを広く示す。  "
      },
      {
        "line": 121,
        "text": "例: The shop has fixed opening hours.  "
      },
      {
        "line": 122,
        "text": "訳: その店には固定された営業時間がある。  "
      },
      {
        "line": 124,
        "text": "【反意語】"
      },
      {
        "line": 126,
        "text": "・uncertain  "
      },
      {
        "line": 127,
        "text": "定義: 確実でなく、結果や内容がまだ分からない。  "
      },
      {
        "line": 128,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 129,
        "text": "違い: uncertain は確定性の反対で、definite が決定・情報の明確さを示すのに対し、見通しや判断が定まらない。  "
      },
      {
        "line": 130,
        "text": "例: The outcome remains uncertain.  "
      },
      {
        "line": 131,
        "text": "訳: 結果は依然として不確かだ。  "
      },
      {
        "line": 133,
        "text": "・tentative  "
      },
      {
        "line": 134,
        "text": "定義: 仮のもので、後で変更される可能性がある。  "
      },
      {
        "line": 135,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 136,
        "text": "違い: tentative は計画・合意などが試案段階であることを示し、definite はそこから確定した段階を示す。  "
      },
      {
        "line": 137,
        "text": "例: We made a tentative booking for next month.  "
      },
      {
        "line": 138,
        "text": "訳: 私たちは来月について仮予約をした。  "
      },
      {
        "line": 140,
        "text": "・undecided  "
      },
      {
        "line": 141,
        "text": "定義: 選択・判断・決定がまだ行われていない。  "
      },
      {
        "line": 142,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 143,
        "text": "違い: undecided は決める主体や問題が未決定であること、definite は答えや立場が決まっていることを表す。  "
      },
      {
        "line": 144,
        "text": "例: The committee is still undecided about the proposal.  "
      },
      {
        "line": 145,
        "text": "訳: 委員会はその提案についてまだ決めていない。  "
      },
      {
        "line": 147,
        "text": "・indefinite  "
      },
      {
        "line": 148,
        "text": "定義: 明確な範囲・期間・内容が定まっていない。  "
      },
      {
        "line": 149,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 150,
        "text": "違い: indefinite は期間・数量・指示対象などの境界が不明確であることを表し、definite は境界が定まっていることを表す。  "
      },
      {
        "line": 151,
        "text": "例: The project was postponed for an indefinite period.  "
      },
      {
        "line": 152,
        "text": "訳: そのプロジェクトは無期限に延期された。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
      },
      {
        "line": 208,
        "text": "【類義語】"
      },
      {
        "line": 210,
        "text": "・clear  "
      },
      {
        "line": 211,
        "text": "定義: 意味・事実・視界などに混乱や曖昧さがない。  "
      },
      {
        "line": 212,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 213,
        "text": "違い: clear は理解可能性や障害のなさを広く表す。definite は変化・差・効果などが明確に認められることを強調しやすい。  "
      },
      {
        "line": 214,
        "text": "例: The instructions are clear and easy to follow.  "
      },
      {
        "line": 215,
        "text": "訳: その指示は明確で、従いやすい。  "
      },
      {
        "line": 217,
        "text": "・obvious  "
      },
      {
        "line": 218,
        "text": "定義: 見たり考えたりすれば、すぐに分かる。  "
      },
      {
        "line": 219,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 220,
        "text": "違い: obvious は認識の容易さを強く示す。definite は明らかさを示すが、必ずしも誰にとっても自明とは限らない。  "
      },
      {
        "line": 221,
        "text": "例: It was obvious that the machine had stopped working.  "
      },
      {
        "line": 222,
        "text": "訳: その機械が動かなくなったことは明らかだった。  "
      },
      {
        "line": 224,
        "text": "・noticeable  "
      },
      {
        "line": 225,
        "text": "定義: 見たり感じたりして気づくことができる。  "
      },
      {
        "line": 226,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 227,
        "text": "違い: noticeable は知覚上の目立ちやすさに焦点がある。definite は目立つだけでなく、差や効果を明確なものとして評価する。  "
      },
      {
        "line": 228,
        "text": "例: There was a noticeable drop in temperature overnight.  "
      },
      {
        "line": 229,
        "text": "訳: 一晩で気温が目に見えて下がった。  "
      },
      {
        "line": 231,
        "text": "・distinct  "
      },
      {
        "line": 232,
        "text": "定義: ほかのものと区別できるほど特徴がはっきりしている。  "
      },
      {
        "line": 233,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 234,
        "text": "違い: distinct は境界や識別可能性を強調する。definite は結果・変化・効果が明確に認められることにも使う。  "
      },
      {
        "line": 235,
        "text": "例: The two methods produce distinct results.  "
      },
      {
        "line": 236,
        "text": "訳: その二つの方法は明確に異なる結果を生む。  "
      },
      {
        "line": 238,
        "text": "・marked  "
      },
      {
        "line": 239,
        "text": "定義: 程度や差が目立つほど顕著である。  "
      },
      {
        "line": 240,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 241,
        "text": "違い: marked は変化・差・改善の大きさを強く示し、definite はそこまで大きくなくても、存在が明確であることを表せる。  "
      },
      {
        "line": 242,
        "text": "例: The report shows a marked reduction in waste.  "
      },
      {
        "line": 243,
        "text": "訳: その報告書は廃棄物の顕著な削減を示している。  "
      },
      {
        "line": 245,
        "text": "【反意語】"
      },
      {
        "line": 247,
        "text": "・unclear  "
      },
      {
        "line": 248,
        "text": "定義: 意味・原因・結果などがはっきりしない。  "
      },
      {
        "line": 249,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 250,
        "text": "違い: unclear は理解や判断の明瞭さの反対で、definite は観察・評価の対象が明らかであることを示す。  "
      },
      {
        "line": 251,
        "text": "例: The cause of the failure is still unclear.  "
      },
      {
        "line": 252,
        "text": "訳: 故障の原因はまだはっきりしない。  "
      },
      {
        "line": 254,
        "text": "・indistinct  "
      },
      {
        "line": 255,
        "text": "定義: 輪郭・音・違いなどがぼんやりして区別しにくい。  "
      },
      {
        "line": 256,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 257,
        "text": "違い: indistinct は知覚上の境界が弱いことを表し、definite は特徴や差が明瞭に取り出せることを表す。  "
      },
      {
        "line": 258,
        "text": "例: The distant hills were indistinct in the fog.  "
      },
      {
        "line": 259,
        "text": "訳: 遠くの丘は霧の中でぼんやりしていた。  "
      },
      {
        "line": 261,
        "text": "・imperceptible  "
      },
      {
        "line": 262,
        "text": "定義: 感覚や観察ではほとんど気づけない。  "
      },
      {
        "line": 263,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 264,
        "text": "違い: imperceptible は変化や差が知覚できないほど小さいことを示し、definite は明確に認められることを示す。  "
      },
      {
        "line": 265,
        "text": "例: The change in pressure was almost imperceptible.  "
      },
      {
        "line": 266,
        "text": "訳: 圧力の変化はほとんど知覚できなかった。  "
      },
      {
        "line": 268,
        "text": "3. 【形容詞・限定用法】具体的な、特定の"
      },
      {
        "line": 317,
        "text": "【類義語】"
      },
      {
        "line": 319,
        "text": "・specific  "
      },
      {
        "line": 320,
        "text": "定義: ほかのものではなく、特定の対象・内容に関する。  "
      },
      {
        "line": 321,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 322,
        "text": "違い: specific は個別の対象を選び出すことを強調し、definite は数量・範囲・条件などが明確に定まっていることを強調する。  "
      },
      {
        "line": 323,
        "text": "例: Please give me a specific example.  "
      },
      {
        "line": 324,
        "text": "訳: 具体的な例を一つ挙げてください。  "
      },
      {
        "line": 326,
        "text": "・precise  "
      },
      {
        "line": 327,
        "text": "定義: 細部や数値が正確で、曖昧さがない。  "
      },
      {
        "line": 328,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 329,
        "text": "違い: precise は細かい正確さを要求する。definite は必ずしも数値の厳密さを求めず、境界や内容が決まっていることを示す。  "
      },
      {
        "line": 330,
        "text": "例: The report provides precise measurements.  "
      },
      {
        "line": 331,
        "text": "訳: その報告書は正確な測定値を示している。  "
      },
      {
        "line": 333,
        "text": "・specified  "
      },
      {
        "line": 334,
        "text": "定義: 条件・文書・規則などで明示的に指定されている。  "
      },
      {
        "line": 335,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 336,
        "text": "違い: specified は誰かが明示して指定したことに焦点があり、definite は指定の有無にかかわらず内容が定まっていることを表せる。  "
      },
      {
        "line": 337,
        "text": "例: The work must be completed within the specified time.  "
      },
      {
        "line": 338,
        "text": "訳: 作業は指定された時間内に完了しなければならない。  "
      },
      {
        "line": 340,
        "text": "・determinate  "
      },
      {
        "line": 341,
        "text": "定義: 限界・終点・結果が決まっている。  "
      },
      {
        "line": 342,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 343,
        "text": "違い: determinate は形式的・専門的で、数学・科学・哲学などで境界や結果の決定性を述べる。definite は一般語としてより広く使う。  "
      },
      {
        "line": 344,
        "text": "例: The process has a determinate end point.  "
      },
      {
        "line": 345,
        "text": "訳: その過程には明確に定まった終点がある。  "
      },
      {
        "line": 347,
        "text": "・fixed  "
      },
      {
        "line": 348,
        "text": "定義: 位置・数量・時期などが動かないように定められている。  "
      },
      {
        "line": 349,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 350,
        "text": "違い: fixed は変更されない状態を強く示し、definite は具体的に境界づけられた情報や範囲にも使う。  "
      },
      {
        "line": 351,
        "text": "例: The fee is fixed for the entire contract period.  "
      },
      {
        "line": 352,
        "text": "訳: 料金は契約期間全体を通じて固定されている。  "
      },
      {
        "line": 354,
        "text": "【反意語】"
      },
      {
        "line": 356,
        "text": "・indefinite  "
      },
      {
        "line": 357,
        "text": "定義: 範囲・期間・数量・内容などが決まっていない。  "
      },
      {
        "line": 358,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 359,
        "text": "違い: indefinite は定まった境界がないことを直接表し、definite は範囲や条件が具体化されていることを表す。  "
      },
      {
        "line": 360,
        "text": "例: The meeting was postponed for an indefinite period.  "
      },
      {
        "line": 361,
        "text": "訳: 会議は無期限に延期された。  "
      },
      {
        "line": 363,
        "text": "・unspecified  "
      },
      {
        "line": 364,
        "text": "定義: 必要な内容や条件が明示されていない。  "
      },
      {
        "line": 365,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 366,
        "text": "違い: unspecified は情報が指定されていないことに焦点があり、definite は情報の境界や内容が明らかであることを表す。  "
      },
      {
        "line": 367,
        "text": "例: The shipment was delayed for unspecified reasons.  "
      },
      {
        "line": 368,
        "text": "訳: その発送は理由が明示されないまま遅れた。  "
      },
      {
        "line": 370,
        "text": "・vague  "
      },
      {
        "line": 371,
        "text": "定義: 表現・考え・範囲などがぼんやりして具体性に欠ける。  "
      },
      {
        "line": 372,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 373,
        "text": "違い: vague は内容の輪郭が弱いことを表し、definite は内容を具体的に切り出せることを表す。  "
      },
      {
        "line": 374,
        "text": "例: His answer was too vague to be useful.  "
      },
      {
        "line": 375,
        "text": "訳: 彼の答えは曖昧すぎて役に立たなかった。  "
      },
      {
        "line": 377,
        "text": "・unlimited  "
      },
      {
        "line": 378,
        "text": "定義: 数量・範囲・期間などに上限がない。  "
      },
      {
        "line": 379,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 380,
        "text": "違い: unlimited は上限の不存在を示し、definite は上限や範囲が定められていることを示す。ただし、definite が必ず有限量を意味するわけではない。  "
      },
      {
        "line": 381,
        "text": "例: The plan offers unlimited data usage.  "
      },
      {
        "line": 382,
        "text": "訳: そのプランはデータ通信を無制限で提供する。  "
      },
      {
        "line": 384,
        "text": "4. 【形容詞・文法用語】定の、特定できる"
      },
      {
        "line": 428,
        "text": "【類義語】"
      },
      {
        "line": 430,
        "text": "・identified  "
      },
      {
        "line": 431,
        "text": "定義: どの人物・物を指すかが分かっている、または特定されている。  "
      },
      {
        "line": 432,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 433,
        "text": "違い: identified は対象が同定されている状態を平易に述べる。definite は名詞句の文法的な指示性を表す用語である。  "
      },
      {
        "line": 434,
        "text": "例: The identified object was removed from the scene.  "
      },
      {
        "line": 435,
        "text": "訳: 特定された物体は現場から取り除かれた。  "
      },
      {
        "line": 437,
        "text": "・determinate  "
      },
      {
        "line": 438,
        "text": "定義: 境界・値・指示対象などが決まっている。  "
      },
      {
        "line": 439,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 440,
        "text": "違い: determinate は形式的・専門的で、definite は英語の冠詞や名詞句の性質を説明する標準用語である。  "
      },
      {
        "line": 441,
        "text": "例: The expression has a determinate meaning in this context.  "
      },
      {
        "line": 442,
        "text": "訳: その表現はこの文脈では明確に定まった意味を持つ。  "
      },
      {
        "line": 444,
        "text": "・specific  "
      },
      {
        "line": 445,
        "text": "定義: 一般的なものではなく、特定の人物・物・内容に関する。  "
      },
      {
        "line": 446,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 447,
        "text": "違い: specific は個別性を表す一般語で、文法上の definite と重なることはあるが、`a specific book` のように不定名詞句にも使える。  "
      },
      {
        "line": 448,
        "text": "例: She was looking for a specific file.  "
      },
      {
        "line": 449,
        "text": "訳: 彼女は特定のファイルを探していた。  "
      },
      {
        "line": 451,
        "text": "【反意語】"
      },
      {
        "line": 453,
        "text": "・indefinite  "
      },
      {
        "line": 454,
        "text": "定義: 名詞句の指示対象が特定できない、または特定の一つとして提示されない。  "
      },
      {
        "line": 455,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 456,
        "text": "違い: 文法上の indefinite は definite の直接の反対で、英語の a/an や、文脈によっては無冠詞の名詞句に関係する。  "
      },
      {
        "line": 457,
        "text": "例: “A book” is indefinite because the listener does not know which book is meant.  "
      },
      {
        "line": 458,
        "text": "訳: 「ある本」は、どの本を指すか聞き手に分からないため不定である。  "
      },
      {
        "line": 460,
        "text": "・unidentified  "
      },
      {
        "line": 461,
        "text": "定義: どの人物・物であるかが特定されていない。  "
      },
      {
        "line": 462,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 463,
        "text": "違い: unidentified は現実の対象を同定できない状態を示し、definite は文法上の名詞句が対象を特定可能に提示する状態を示す。  "
      },
      {
        "line": 464,
        "text": "例: An unidentified caller left a message.  "
      },
      {
        "line": 465,
        "text": "訳: 身元不明の発信者がメッセージを残した。  "
      },
      {
        "line": 467,
        "text": "・generic  "
      },
      {
        "line": 468,
        "text": "定義: 個別の一つではなく、種類全体や一般的な概念に関する。  "
      },
      {
        "line": 469,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 470,
        "text": "違い: generic は指示の範囲が一般化されていることを表す。definite と対照できるが、英語では definite article が総称的に使われる場合もあるため、完全な形の反意語ではない。  "
      },
      {
        "line": 471,
        "text": "例: “Dogs are social animals” has a generic reference.  "
      },
      {
        "line": 472,
        "text": "訳: 「犬は社会的な動物だ」は総称的な指示を持つ。  "
      },
      {
        "line": 474,
        "text": "5. 【形容詞・植物学】有限の、定数の"
      },
      {
        "line": 503,
        "text": "【類義語】"
      },
      {
        "line": 505,
        "text": "・determinate  "
      },
      {
        "line": 506,
        "text": "定義: 植物の成長・花序・器官の数などが一定の限界で決まる。  "
      },
      {
        "line": 507,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 508,
        "text": "違い: determinate はこの植物学上の意味でより一般的な専門語で、definite は同じ特徴を別の語彙で表す。  "
      },
      {
        "line": 509,
        "text": "例: The plant produces a determinate inflorescence.  "
      },
      {
        "line": 510,
        "text": "訳: その植物は有限花序を形成する。  "
      },
      {
        "line": 512,
        "text": "・fixed-number  "
      },
      {
        "line": 513,
        "text": "定義: 数が一定に定められている。  "
      },
      {
        "line": 514,
        "text": "頻度: 〈2/10〉  "
      },
      {
        "line": 515,
        "text": "違い: fixed-number は説明的な表現で、definite stamens の特徴を言い換えるが、単独の標準用語としての使用は限定的である。  "
      },
      {
        "line": 516,
        "text": "例: The flower has a fixed number of stamens.  "
      },
      {
        "line": 517,
        "text": "訳: その花には一定数の雄しべがある。  "
      },
      {
        "line": 519,
        "text": "【反意語】"
      },
      {
        "line": 521,
        "text": "・indefinite  "
      },
      {
        "line": 522,
        "text": "定義: 数が一定でない、または花序の成長に固定された終点がない。  "
      },
      {
        "line": 523,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 524,
        "text": "違い: indefinite は definite stamens や definite inflorescence の反対側にある植物学用語で、器官数や成長の上限が定まらないことを示す。  "
      },
      {
        "line": 525,
        "text": "例: An indefinite inflorescence can continue producing flowers along its main axis.  "
      },
      {
        "line": 526,
        "text": "訳: 無限花序は主軸に沿って花を作り続けることがある。  "
      },
      {
        "line": 528,
        "text": "・indeterminate  "
      },
      {
        "line": 529,
        "text": "定義: 成長や結果の終点があらかじめ固定されていない。  "
      },
      {
        "line": 530,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 531,
        "text": "違い: indeterminate は植物学で definite／determinate と対立し、主軸の成長が花で終わらないことなどを表す。  "
      },
      {
        "line": 532,
        "text": "例: The species shows indeterminate rather than definite growth.  "
      },
      {
        "line": 533,
        "text": "訳: その種は定限成長ではなく不定成長を示す。  "
      }
    ],
    "antonym_axis_items": [
      {
        "item_id": "ant-ff69a1a9f3cd",
        "stage1_axis": {
          "item_id": "ant-ff69a1a9f3cd",
          "axis": "確定性",
          "relation_type": "状態",
          "reason": "uncertain は definite の確定性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 126,
          "line_end": 126,
          "exact_quote": "・uncertain  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 129,
          "line_end": 129,
          "exact_quote": "違い: uncertain は確定性の反対で、definite が決定・情報の明確さを示すのに対し、見通しや判断が定まらない。  "
        }
      },
      {
        "item_id": "ant-c5c7ab207470",
        "stage1_axis": {
          "item_id": "ant-c5c7ab207470",
          "axis": "確定性",
          "relation_type": "状態",
          "reason": "tentative は definite の確定性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 133,
          "line_end": 133,
          "exact_quote": "・tentative  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 136,
          "line_end": 136,
          "exact_quote": "違い: tentative は計画・合意などが試案段階であることを示し、definite はそこから確定した段階を示す。  "
        }
      },
      {
        "item_id": "ant-0f692a54b438",
        "stage1_axis": {
          "item_id": "ant-0f692a54b438",
          "axis": "確定性",
          "relation_type": "状態",
          "reason": "undecided は definite の確定性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 140,
          "line_end": 140,
          "exact_quote": "・undecided  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 143,
          "line_end": 143,
          "exact_quote": "違い: undecided は決める主体や問題が未決定であること、definite は答えや立場が決まっていることを表す。  "
        }
      },
      {
        "item_id": "ant-e4bf06db3822",
        "stage1_axis": {
          "item_id": "ant-e4bf06db3822",
          "axis": "有限性",
          "relation_type": "状態",
          "reason": "indefinite は definite の有限性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 147,
          "line_end": 147,
          "exact_quote": "・indefinite  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 150,
          "line_end": 150,
          "exact_quote": "違い: indefinite は期間・数量・指示対象などの境界が不明確であることを表し、definite は境界が定まっていることを表す。  "
        }
      },
      {
        "item_id": "ant-b94874c1fb0a",
        "stage1_axis": {
          "item_id": "ant-b94874c1fb0a",
          "axis": "明瞭性",
          "relation_type": "程度",
          "reason": "unclear は definite の明瞭性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:002",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 247,
          "line_end": 247,
          "exact_quote": "・unclear  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 250,
          "line_end": 250,
          "exact_quote": "違い: unclear は理解や判断の明瞭さの反対で、definite は観察・評価の対象が明らかであることを示す。  "
        }
      },
      {
        "item_id": "ant-d8cdab9d17a7",
        "stage1_axis": {
          "item_id": "ant-d8cdab9d17a7",
          "axis": "明瞭性",
          "relation_type": "程度",
          "reason": "indistinct は definite の明瞭性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:002",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 254,
          "line_end": 254,
          "exact_quote": "・indistinct  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 257,
          "line_end": 257,
          "exact_quote": "違い: indistinct は知覚上の境界が弱いことを表し、definite は特徴や差が明瞭に取り出せることを表す。  "
        }
      },
      {
        "item_id": "ant-9a3ffea3963f",
        "stage1_axis": {
          "item_id": "ant-9a3ffea3963f",
          "axis": "明瞭性",
          "relation_type": "程度",
          "reason": "imperceptible は definite の明瞭性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:002",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 261,
          "line_end": 261,
          "exact_quote": "・imperceptible  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 264,
          "line_end": 264,
          "exact_quote": "違い: imperceptible は変化や差が知覚できないほど小さいことを示し、definite は明確に認められることを示す。  "
        }
      },
      {
        "item_id": "ant-edb72631391b",
        "stage1_axis": {
          "item_id": "ant-edb72631391b",
          "axis": "有限性",
          "relation_type": "状態",
          "reason": "indefinite は definite の有限性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 356,
          "line_end": 356,
          "exact_quote": "・indefinite  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 359,
          "line_end": 359,
          "exact_quote": "違い: indefinite は定まった境界がないことを直接表し、definite は範囲や条件が具体化されていることを表す。  "
        }
      },
      {
        "item_id": "ant-1c347dcd4402",
        "stage1_axis": {
          "item_id": "ant-1c347dcd4402",
          "axis": "具体性",
          "relation_type": "状態",
          "reason": "unspecified は definite の具体性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 363,
          "line_end": 363,
          "exact_quote": "・unspecified  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 366,
          "line_end": 366,
          "exact_quote": "違い: unspecified は情報が指定されていないことに焦点があり、definite は情報の境界や内容が明らかであることを表す。  "
        }
      },
      {
        "item_id": "ant-e02007848369",
        "stage1_axis": {
          "item_id": "ant-e02007848369",
          "axis": "具体性",
          "relation_type": "状態",
          "reason": "vague は definite の具体性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 370,
          "line_end": 370,
          "exact_quote": "・vague  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 373,
          "line_end": 373,
          "exact_quote": "違い: vague は内容の輪郭が弱いことを表し、definite は内容を具体的に切り出せることを表す。  "
        }
      },
      {
        "item_id": "ant-c7e3f2e53104",
        "stage1_axis": {
          "item_id": "ant-c7e3f2e53104",
          "axis": "有限性",
          "relation_type": "状態",
          "reason": "unlimited は definite の有限性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:003",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 377,
          "line_end": 377,
          "exact_quote": "・unlimited  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 380,
          "line_end": 380,
          "exact_quote": "違い: unlimited は上限の不存在を示し、definite は上限や範囲が定められていることを示す。ただし、definite が必ず有限量を意味するわけではない。  "
        }
      },
      {
        "item_id": "ant-72aede0d05ae",
        "stage1_axis": {
          "item_id": "ant-72aede0d05ae",
          "axis": "有限性",
          "relation_type": "状態",
          "reason": "indefinite は definite の有限性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:004",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 453,
          "line_end": 453,
          "exact_quote": "・indefinite  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 456,
          "line_end": 456,
          "exact_quote": "違い: 文法上の indefinite は definite の直接の反対で、英語の a/an や、文脈によっては無冠詞の名詞句に関係する。  "
        }
      },
      {
        "item_id": "ant-474db3bb568c",
        "stage1_axis": {
          "item_id": "ant-474db3bb568c",
          "axis": "同定性",
          "relation_type": "状態",
          "reason": "unidentified は definite の同定性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:004",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 460,
          "line_end": 460,
          "exact_quote": "・unidentified  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 463,
          "line_end": 463,
          "exact_quote": "違い: unidentified は現実の対象を同定できない状態を示し、definite は文法上の名詞句が対象を特定可能に提示する状態を示す。  "
        }
      },
      {
        "item_id": "ant-818f8d4e4aa3",
        "stage1_axis": {
          "item_id": "ant-818f8d4e4aa3",
          "axis": "指示性",
          "relation_type": "状態",
          "reason": "generic は definite の指示性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:004",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 467,
          "line_end": 467,
          "exact_quote": "・generic  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 470,
          "line_end": 470,
          "exact_quote": "違い: generic は指示の範囲が一般化されていることを表す。definite と対照できるが、英語では definite article が総称的に使われる場合もあるため、完全な形の反意語ではない。  "
        }
      },
      {
        "item_id": "ant-bd78359dead5",
        "stage1_axis": {
          "item_id": "ant-bd78359dead5",
          "axis": "有限性",
          "relation_type": "状態",
          "reason": "indefinite は definite の有限性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:005",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 521,
          "line_end": 521,
          "exact_quote": "・indefinite  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 524,
          "line_end": 524,
          "exact_quote": "違い: indefinite は definite stamens や definite inflorescence の反対側にある植物学用語で、器官数や成長の上限が定まらないことを示す。  "
        }
      },
      {
        "item_id": "ant-26ef8568abaf",
        "stage1_axis": {
          "item_id": "ant-26ef8568abaf",
          "axis": "有限性",
          "relation_type": "状態",
          "reason": "indeterminate は definite の有限性に対する反対側の状態・程度を示す。"
        },
        "sense_id": "sense:005",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 528,
          "line_end": 528,
          "exact_quote": "・indeterminate  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 531,
          "line_end": 531,
          "exact_quote": "違い: indeterminate は植物学で definite／determinate と対立し、主軸の成長が花で終わらないことなどを表す。  "
        }
      }
    ],
    "antonym_axis_senses": [
      {
        "sense_id": "sense:001",
        "full_sense": [
          {
            "line": 40,
            "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
          },
          {
            "line": 42,
            "text": "【日本語訳・定義】答え、決定、計画、日付、合意、意図などが、曖昧な候補や一時的な案ではなく、内容として定まり、変更される可能性が低いことを表す。必ずしも今後絶対に変更できないという意味ではなく、現時点で決定・約束・判断が明確になっていることに焦点がある。  "
          },
          {
            "line": 44,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 46,
            "text": "【レジスター/領域】標準語で、会話・ビジネス・報道・公式文書まで広く使う。計画や合意の確定性を述べるときに多く、日常会話では sure が話者の確信、definite が決定や内容の確定を表しやすい。  "
          },
          {
            "line": 48,
            "text": "【文法パターン】a definite answer/decision/plan/date/deadline＝確定した答え・決定・計画・日付・期限／a definite agreement/offer/commitment＝明確に成立した合意・正式な申し出・確約／have no definite plans/ideas＝決まった計画・具体的な考えがない／anything/nothing definite＝何か／何も確定したもの／be definite about something＝ある事柄について態度・内容を明確にする／a definite yes/no＝はっきりした賛成／拒否。  "
          },
          {
            "line": 50,
            "text": "【コロケーション】"
          },
          {
            "line": 52,
            "text": "・a definite answer  "
          },
          {
            "line": 53,
            "text": "用途: 予想や曖昧な返事ではなく、決定した答えを求める。  "
          },
          {
            "line": 54,
            "text": "例: We need a definite answer by Friday, not another tentative suggestion.  "
          },
          {
            "line": 55,
            "text": "訳: 私たちは金曜日までに、また別の仮案ではなく確定した答えを必要としている。  "
          },
          {
            "line": 57,
            "text": "・a definite date for 〈event〉  "
          },
          {
            "line": 58,
            "text": "用途: 行事・開始・発売などの日付が決まっていることを表す。  "
          },
          {
            "line": 59,
            "text": "例: The organizers have not announced a definite date for the launch.  "
          },
          {
            "line": 60,
            "text": "訳: 主催者は発売の確定した日付をまだ発表していない。  "
          },
          {
            "line": 62,
            "text": "・no definite plans  "
          },
          {
            "line": 63,
            "text": "用途: 将来の予定がまだ決まっていないことを表す。  "
          },
          {
            "line": 64,
            "text": "例: I have no definite plans for the weekend yet.  "
          },
          {
            "line": 65,
            "text": "訳: 私は週末の具体的な予定をまだ決めていない。  "
          },
          {
            "line": 67,
            "text": "・anything definite about something  "
          },
          {
            "line": 68,
            "text": "用途: ある事柄について確定した情報があるかを尋ねる。  "
          },
          {
            "line": 69,
            "text": "例: Do you know anything definite about when the train will leave?  "
          },
          {
            "line": 70,
            "text": "訳: 列車がいつ出るかについて、何か確定した情報を知っていますか。  "
          },
          {
            "line": 72,
            "text": "・a definite yes/no  "
          },
          {
            "line": 73,
            "text": "用途: ためらいや条件付きではない、明確な肯定・拒否を表す。  "
          },
          {
            "line": 74,
            "text": "例: Her reply was a definite no, so we stopped asking.  "
          },
          {
            "line": 75,
            "text": "訳: 彼女の返事は明確な拒否だったので、私たちは尋ねるのをやめた。  "
          },
          {
            "line": 77,
            "text": "・be definite about 〈decision/position〉  "
          },
          {
            "line": 78,
            "text": "用途: 決定や立場を曖昧にせず、はっきり示す。  "
          },
          {
            "line": 79,
            "text": "例: Please be definite about your position before the meeting begins.  "
          },
          {
            "line": 80,
            "text": "訳: 会議が始まる前に、自分の立場を明確にしてください。  "
          },
          {
            "line": 82,
            "text": "・a definite commitment to do  "
          },
          {
            "line": 83,
            "text": "用途: ある行動を実行するという明確な確約を表す。  "
          },
          {
            "line": 84,
            "text": "例: The grant requires a definite commitment to complete the project.  "
          },
          {
            "line": 85,
            "text": "訳: その助成金には、プロジェクトを完了するという明確な確約が必要だ。  "
          },
          {
            "line": 87,
            "text": "・a definite agreement  "
          },
          {
            "line": 88,
            "text": "用途: 条件や内容が定まり、当事者間で成立した合意を表す。  "
          },
          {
            "line": 89,
            "text": "例: No definite agreement had been reached by the end of the meeting.  "
          },
          {
            "line": 90,
            "text": "訳: 会議の終了時までに、確定した合意は成立していなかった。  "
          },
          {
            "line": 92,
            "text": "【語法・注意】certain は「真実だと確信している」「起こる可能性が高い」という話者の認識にも使えるが、definite は答え・計画・日付などの内容が決まっていることを強調しやすい。final は「それ以上変更しない最終段階」、firm は意思・態度の強さに焦点があるため、definite と完全には交換できない。`I have no definite plans.` は「将来の予定が一切ない」ではなく「決まった予定はない」という意味である。definite と definitely、definite と definitive を品詞や意味を考えずに置き換えない。綴りは definite であり、definate ではない。  "
          },
          {
            "line": 94,
            "text": "【類義語】"
          },
          {
            "line": 96,
            "text": "・certain  "
          },
          {
            "line": 97,
            "text": "定義: 疑いがなく、確かだと判断される。  "
          },
          {
            "line": 98,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 99,
            "text": "違い: certain は事実・未来・話者の確信を広く表す。definite は答えや予定が決定済みで曖昧でないことを表しやすい。  "
          },
          {
            "line": 100,
            "text": "例: I am certain that she will accept the offer.  "
          },
          {
            "line": 101,
            "text": "訳: 彼女がその申し出を受けると私は確信している。  "
          },
          {
            "line": 103,
            "text": "・settled  "
          },
          {
            "line": 104,
            "text": "定義: 議論や検討の後に、決定・合意されている。  "
          },
          {
            "line": 105,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 106,
            "text": "違い: settled は未決の状態が終わったことに焦点があり、definite は決まった内容が明確であることに焦点がある。  "
          },
          {
            "line": 107,
            "text": "例: The venue for the conference is now settled.  "
          },
          {
            "line": 108,
            "text": "訳: 会議の会場は今や決まっている。  "
          },
          {
            "line": 110,
            "text": "・firm  "
          },
          {
            "line": 111,
            "text": "定義: 意思・約束・態度が強く、簡単には変わらない。  "
          },
          {
            "line": 112,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 113,
            "text": "違い: firm は人の決意や約束の強さを示し、definite は決定内容や情報の確定性を示す。  "
          },
          {
            "line": 114,
            "text": "例: She made a firm promise to return the money.  "
          },
          {
            "line": 115,
            "text": "訳: 彼女はそのお金を返すと固く約束した。  "
          },
          {
            "line": 117,
            "text": "・fixed  "
          },
          {
            "line": 118,
            "text": "定義: 位置・日時・数量などが変更されないように定められている。  "
          },
          {
            "line": 119,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 120,
            "text": "違い: fixed は変更不能・変更予定なしという状態を強く示し、definite は曖昧さが解消されていることを広く示す。  "
          },
          {
            "line": 121,
            "text": "例: The shop has fixed opening hours.  "
          },
          {
            "line": 122,
            "text": "訳: その店には固定された営業時間がある。  "
          },
          {
            "line": 124,
            "text": "【反意語】"
          },
          {
            "line": 126,
            "text": "・uncertain  "
          },
          {
            "line": 127,
            "text": "定義: 確実でなく、結果や内容がまだ分からない。  "
          },
          {
            "line": 128,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 129,
            "text": "違い: uncertain は確定性の反対で、definite が決定・情報の明確さを示すのに対し、見通しや判断が定まらない。  "
          },
          {
            "line": 130,
            "text": "例: The outcome remains uncertain.  "
          },
          {
            "line": 131,
            "text": "訳: 結果は依然として不確かだ。  "
          },
          {
            "line": 133,
            "text": "・tentative  "
          },
          {
            "line": 134,
            "text": "定義: 仮のもので、後で変更される可能性がある。  "
          },
          {
            "line": 135,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 136,
            "text": "違い: tentative は計画・合意などが試案段階であることを示し、definite はそこから確定した段階を示す。  "
          },
          {
            "line": 137,
            "text": "例: We made a tentative booking for next month.  "
          },
          {
            "line": 138,
            "text": "訳: 私たちは来月について仮予約をした。  "
          },
          {
            "line": 140,
            "text": "・undecided  "
          },
          {
            "line": 141,
            "text": "定義: 選択・判断・決定がまだ行われていない。  "
          },
          {
            "line": 142,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 143,
            "text": "違い: undecided は決める主体や問題が未決定であること、definite は答えや立場が決まっていることを表す。  "
          },
          {
            "line": 144,
            "text": "例: The committee is still undecided about the proposal.  "
          },
          {
            "line": 145,
            "text": "訳: 委員会はその提案についてまだ決めていない。  "
          },
          {
            "line": 147,
            "text": "・indefinite  "
          },
          {
            "line": 148,
            "text": "定義: 明確な範囲・期間・内容が定まっていない。  "
          },
          {
            "line": 149,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 150,
            "text": "違い: indefinite は期間・数量・指示対象などの境界が不明確であることを表し、definite は境界が定まっていることを表す。  "
          },
          {
            "line": 151,
            "text": "例: The project was postponed for an indefinite period.  "
          },
          {
            "line": 152,
            "text": "訳: そのプロジェクトは無期限に延期された。  "
          }
        ]
      },
      {
        "sense_id": "sense:002",
        "full_sense": [
          {
            "line": 154,
            "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
          },
          {
            "line": 156,
            "text": "【日本語訳・定義】変化、差、効果、兆候、利点などが、観察や比較によって実際に認められるほど明瞭・顕著であることを表す。必ずしも論理的に証明済み、絶対に疑いがないという意味ではなく、話し手が変化や特徴をはっきり認識しているという評価を含むことがある。  "
          },
          {
            "line": 158,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 160,
            "text": "【レジスター/領域】標準語で、会話・報道・評価・ビジネス文書まで使える。clear や obvious よりやや説明的・形式的で、improvement、difference、effect、sign など、観察できる変化や結果を修飾することが多い。  "
          },
          {
            "line": 162,
            "text": "【文法パターン】a definite improvement/change/difference＝明らかな改善・変化・違い／a definite sign/indication of something＝～の明らかな兆候・指標／have a definite effect/impact on something＝ある物事に明確な効果・影響を及ぼす／a definite advantage/disadvantage＝明確な利点・不利／a definite possibility＝現実味のある可能性／see/feel a definite difference＝はっきり違いを感じる。  "
          },
          {
            "line": 164,
            "text": "【コロケーション】"
          },
          {
            "line": 166,
            "text": "・a definite improvement  "
          },
          {
            "line": 167,
            "text": "用途: 状態や成績が実際に良くなったと認められることを表す。  "
          },
          {
            "line": 168,
            "text": "例: The new treatment produced a definite improvement in her symptoms.  "
          },
          {
            "line": 169,
            "text": "訳: 新しい治療によって、彼女の症状には明らかな改善が見られた。  "
          },
          {
            "line": 171,
            "text": "・a definite difference between 〈A〉 and 〈B〉  "
          },
          {
            "line": 172,
            "text": "用途: 二つの対象の違いがはっきり認められることを表す。  "
          },
          {
            "line": 173,
            "text": "例: There is a definite difference between the two versions of the report.  "
          },
          {
            "line": 174,
            "text": "訳: その報告書の二つの版には明らかな違いがある。  "
          },
          {
            "line": 176,
            "text": "・a definite sign of something  "
          },
          {
            "line": 177,
            "text": "用途: ある状態や出来事を示す、見分けやすい兆候を表す。  "
          },
          {
            "line": 178,
            "text": "例: A sudden drop in demand is a definite sign of weakening consumer confidence.  "
          },
          {
            "line": 179,
            "text": "訳: 需要の急減は、消費者信頼感が弱まっている明らかな兆候だ。  "
          },
          {
            "line": 181,
            "text": "・have a definite effect on something  "
          },
          {
            "line": 182,
            "text": "用途: 行為・条件・政策などが、結果に明確な影響を与えることを表す。  "
          },
          {
            "line": 183,
            "text": "例: Sleep has a definite effect on how well people remember new information.  "
          },
          {
            "line": 184,
            "text": "訳: 睡眠は、人が新しい情報をどれだけよく覚えるかに明確な影響を及ぼす。  "
          },
          {
            "line": 186,
            "text": "・a definite advantage  "
          },
          {
            "line": 187,
            "text": "用途: 他と比べて認めやすい具体的な利点を強調する。  "
          },
          {
            "line": 188,
            "text": "例: The shorter route offers a definite advantage during the winter.  "
          },
          {
            "line": 189,
            "text": "訳: その短い経路は冬の間、明確な利点をもたらす。  "
          },
          {
            "line": 191,
            "text": "・a definite possibility  "
          },
          {
            "line": 192,
            "text": "用途: 単なる空想ではなく、現実に起こり得る可能性を表す。  "
          },
          {
            "line": 193,
            "text": "例: A delay is a definite possibility if the storm continues.  "
          },
          {
            "line": 194,
            "text": "訳: 嵐が続けば、遅延は十分に現実的な可能性だ。  "
          },
          {
            "line": 196,
            "text": "・see a definite change in something  "
          },
          {
            "line": 197,
            "text": "用途: 状態や傾向の変化を観察してはっきり認める。  "
          },
          {
            "line": 198,
            "text": "例: We can see a definite change in customer behavior after the price increase.  "
          },
          {
            "line": 199,
            "text": "訳: 値上げ後、顧客の行動に明らかな変化が見られる。  "
          },
          {
            "line": 201,
            "text": "・with a definite sense of 〈emotion〉  "
          },
          {
            "line": 202,
            "text": "用途: 表情・声・行動などに特定の感情が明確に表れている様子を示す。  "
          },
          {
            "line": 203,
            "text": "例: He left the room with a definite sense of relief.  "
          },
          {
            "line": 204,
            "text": "訳: 彼は明らかに安堵した様子で部屋を出た。  "
          },
          {
            "line": 206,
            "text": "【語法・注意】この用法の definite は「証明された」と同義ではない。`a definite improvement` は改善がはっきり認められるという意味で、科学的な因果関係が完全に証明されたという意味ではない。`a definite possibility` は「確実に起こること」ではなく「現実味のある可能性」である。obvious は誰にとってもすぐ分かること、clear は混乱や曖昧さがないこと、noticeable は知覚上目立つことを強調し、definite は変化・差・効果などを明確なものとして認めることに焦点がある。  "
          },
          {
            "line": 208,
            "text": "【類義語】"
          },
          {
            "line": 210,
            "text": "・clear  "
          },
          {
            "line": 211,
            "text": "定義: 意味・事実・視界などに混乱や曖昧さがない。  "
          },
          {
            "line": 212,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 213,
            "text": "違い: clear は理解可能性や障害のなさを広く表す。definite は変化・差・効果などが明確に認められることを強調しやすい。  "
          },
          {
            "line": 214,
            "text": "例: The instructions are clear and easy to follow.  "
          },
          {
            "line": 215,
            "text": "訳: その指示は明確で、従いやすい。  "
          },
          {
            "line": 217,
            "text": "・obvious  "
          },
          {
            "line": 218,
            "text": "定義: 見たり考えたりすれば、すぐに分かる。  "
          },
          {
            "line": 219,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 220,
            "text": "違い: obvious は認識の容易さを強く示す。definite は明らかさを示すが、必ずしも誰にとっても自明とは限らない。  "
          },
          {
            "line": 221,
            "text": "例: It was obvious that the machine had stopped working.  "
          },
          {
            "line": 222,
            "text": "訳: その機械が動かなくなったことは明らかだった。  "
          },
          {
            "line": 224,
            "text": "・noticeable  "
          },
          {
            "line": 225,
            "text": "定義: 見たり感じたりして気づくことができる。  "
          },
          {
            "line": 226,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 227,
            "text": "違い: noticeable は知覚上の目立ちやすさに焦点がある。definite は目立つだけでなく、差や効果を明確なものとして評価する。  "
          },
          {
            "line": 228,
            "text": "例: There was a noticeable drop in temperature overnight.  "
          },
          {
            "line": 229,
            "text": "訳: 一晩で気温が目に見えて下がった。  "
          },
          {
            "line": 231,
            "text": "・distinct  "
          },
          {
            "line": 232,
            "text": "定義: ほかのものと区別できるほど特徴がはっきりしている。  "
          },
          {
            "line": 233,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 234,
            "text": "違い: distinct は境界や識別可能性を強調する。definite は結果・変化・効果が明確に認められることにも使う。  "
          },
          {
            "line": 235,
            "text": "例: The two methods produce distinct results.  "
          },
          {
            "line": 236,
            "text": "訳: その二つの方法は明確に異なる結果を生む。  "
          },
          {
            "line": 238,
            "text": "・marked  "
          },
          {
            "line": 239,
            "text": "定義: 程度や差が目立つほど顕著である。  "
          },
          {
            "line": 240,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 241,
            "text": "違い: marked は変化・差・改善の大きさを強く示し、definite はそこまで大きくなくても、存在が明確であることを表せる。  "
          },
          {
            "line": 242,
            "text": "例: The report shows a marked reduction in waste.  "
          },
          {
            "line": 243,
            "text": "訳: その報告書は廃棄物の顕著な削減を示している。  "
          },
          {
            "line": 245,
            "text": "【反意語】"
          },
          {
            "line": 247,
            "text": "・unclear  "
          },
          {
            "line": 248,
            "text": "定義: 意味・原因・結果などがはっきりしない。  "
          },
          {
            "line": 249,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 250,
            "text": "違い: unclear は理解や判断の明瞭さの反対で、definite は観察・評価の対象が明らかであることを示す。  "
          },
          {
            "line": 251,
            "text": "例: The cause of the failure is still unclear.  "
          },
          {
            "line": 252,
            "text": "訳: 故障の原因はまだはっきりしない。  "
          },
          {
            "line": 254,
            "text": "・indistinct  "
          },
          {
            "line": 255,
            "text": "定義: 輪郭・音・違いなどがぼんやりして区別しにくい。  "
          },
          {
            "line": 256,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 257,
            "text": "違い: indistinct は知覚上の境界が弱いことを表し、definite は特徴や差が明瞭に取り出せることを表す。  "
          },
          {
            "line": 258,
            "text": "例: The distant hills were indistinct in the fog.  "
          },
          {
            "line": 259,
            "text": "訳: 遠くの丘は霧の中でぼんやりしていた。  "
          },
          {
            "line": 261,
            "text": "・imperceptible  "
          },
          {
            "line": 262,
            "text": "定義: 感覚や観察ではほとんど気づけない。  "
          },
          {
            "line": 263,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 264,
            "text": "違い: imperceptible は変化や差が知覚できないほど小さいことを示し、definite は明確に認められることを示す。  "
          },
          {
            "line": 265,
            "text": "例: The change in pressure was almost imperceptible.  "
          },
          {
            "line": 266,
            "text": "訳: 圧力の変化はほとんど知覚できなかった。  "
          }
        ]
      },
      {
        "sense_id": "sense:003",
        "full_sense": [
          {
            "line": 268,
            "text": "3. 【形容詞・限定用法】具体的な、特定の"
          },
          {
            "line": 270,
            "text": "【日本語訳・定義】数量、期間、範囲、時点、形、情報などに明確な境界や内容があり、漠然としたものではないことを表す。特定の対象を指す場合でも、文脈上その対象を識別できるという文法上の意味とは異なり、ここでは内容・範囲・条件が具体的に定まっていることに焦点がある。  "
          },
          {
            "line": 272,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 274,
            "text": "【レジスター/領域】標準語だが、契約・行政・学術・数学・技術文書で特に多い。specific は選び出された個別性、exact は数値や内容の厳密な一致、definite は範囲や条件が定まっていることを強調しやすい。  "
          },
          {
            "line": 276,
            "text": "【文法パターン】a definite amount/number/quantity/period＝具体的な量・数・期間／at a definite time/stage＝特定の時点・段階で／within definite limits＝明確な範囲内で／definite information/details＝具体的な情報・詳細／a definite shape/form＝はっきり定まった形・形式／a definite integral＝定積分。  "
          },
          {
            "line": 278,
            "text": "【コロケーション】"
          },
          {
            "line": 280,
            "text": "・a definite amount of 〈money/material〉  "
          },
          {
            "line": 281,
            "text": "用途: 金額や物質の量が一定の範囲・数量として定まっていることを表す。  "
          },
          {
            "line": 282,
            "text": "例: The machine requires a definite amount of oil to operate safely.  "
          },
          {
            "line": 283,
            "text": "訳: その機械を安全に稼働させるには、一定量の油が必要だ。  "
          },
          {
            "line": 285,
            "text": "・a definite number of 〈people/items〉  "
          },
          {
            "line": 286,
            "text": "用途: 人数や個数が曖昧でなく、決まった数であることを表す。  "
          },
          {
            "line": 287,
            "text": "例: Only a definite number of students can join the laboratory tour.  "
          },
          {
            "line": 288,
            "text": "訳: 研究室見学に参加できる学生数には上限が決まっている。  "
          },
          {
            "line": 290,
            "text": "・for a definite period  "
          },
          {
            "line": 291,
            "text": "用途: 期間の終点または長さがあらかじめ定められていることを表す。  "
          },
          {
            "line": 292,
            "text": "例: The equipment may be rented for a definite period of six months.  "
          },
          {
            "line": 293,
            "text": "訳: その設備は6か月という定められた期間、借りることができる。  "
          },
          {
            "line": 295,
            "text": "・within definite limits  "
          },
          {
            "line": 296,
            "text": "用途: 許容範囲や境界を明確に限定する。  "
          },
          {
            "line": 297,
            "text": "例: The temperature must remain within definite limits during transport.  "
          },
          {
            "line": 298,
            "text": "訳: 輸送中、温度は明確に定められた範囲内に保たなければならない。  "
          },
          {
            "line": 300,
            "text": "・definite information about 〈topic〉  "
          },
          {
            "line": 301,
            "text": "用途: 推測や噂ではなく、内容が確認できる具体的な情報を表す。  "
          },
          {
            "line": 302,
            "text": "例: We need definite information about the delivery schedule before placing the order.  "
          },
          {
            "line": 303,
            "text": "訳: 注文を出す前に、納入予定について具体的な情報が必要だ。  "
          },
          {
            "line": 305,
            "text": "・a definite shape/form  "
          },
          {
            "line": 306,
            "text": "用途: 輪郭や形式が一定で、別の形と区別できることを表す。  "
          },
          {
            "line": 307,
            "text": "例: The crystals grow into a definite shape under controlled conditions.  "
          },
          {
            "line": 308,
            "text": "訳: その結晶は、管理された条件下で一定の形に成長する。  "
          },
          {
            "line": 310,
            "text": "・a definite integral  "
          },
          {
            "line": 311,
            "text": "用途: 数学で、積分区間の上下端が指定された定積分を指す。  "
          },
          {
            "line": 312,
            "text": "例: The area under the curve can be calculated with a definite integral.  "
          },
          {
            "line": 313,
            "text": "訳: 曲線の下の面積は定積分で計算できる。  "
          },
          {
            "line": 315,
            "text": "【語法・注意】`a definite amount` は「量が決まっている」ことを示すが、必ずしも聞き手がその数値を知っているとは限らない。`specific` は「その特定のもの」という選択に、`exact` は誤差のない数値・内容に焦点がある。`definite information` は具体的で確認可能な情報、`definite plans` は決定済みの予定というように、名詞によって「具体的」と「確定した」のどちらが前面に出るかが変わる。`definite integral` は「確実な積分」ではなく、積分区間が定まった数学用語である。  "
          },
          {
            "line": 317,
            "text": "【類義語】"
          },
          {
            "line": 319,
            "text": "・specific  "
          },
          {
            "line": 320,
            "text": "定義: ほかのものではなく、特定の対象・内容に関する。  "
          },
          {
            "line": 321,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 322,
            "text": "違い: specific は個別の対象を選び出すことを強調し、definite は数量・範囲・条件などが明確に定まっていることを強調する。  "
          },
          {
            "line": 323,
            "text": "例: Please give me a specific example.  "
          },
          {
            "line": 324,
            "text": "訳: 具体的な例を一つ挙げてください。  "
          },
          {
            "line": 326,
            "text": "・precise  "
          },
          {
            "line": 327,
            "text": "定義: 細部や数値が正確で、曖昧さがない。  "
          },
          {
            "line": 328,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 329,
            "text": "違い: precise は細かい正確さを要求する。definite は必ずしも数値の厳密さを求めず、境界や内容が決まっていることを示す。  "
          },
          {
            "line": 330,
            "text": "例: The report provides precise measurements.  "
          },
          {
            "line": 331,
            "text": "訳: その報告書は正確な測定値を示している。  "
          },
          {
            "line": 333,
            "text": "・specified  "
          },
          {
            "line": 334,
            "text": "定義: 条件・文書・規則などで明示的に指定されている。  "
          },
          {
            "line": 335,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 336,
            "text": "違い: specified は誰かが明示して指定したことに焦点があり、definite は指定の有無にかかわらず内容が定まっていることを表せる。  "
          },
          {
            "line": 337,
            "text": "例: The work must be completed within the specified time.  "
          },
          {
            "line": 338,
            "text": "訳: 作業は指定された時間内に完了しなければならない。  "
          },
          {
            "line": 340,
            "text": "・determinate  "
          },
          {
            "line": 341,
            "text": "定義: 限界・終点・結果が決まっている。  "
          },
          {
            "line": 342,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 343,
            "text": "違い: determinate は形式的・専門的で、数学・科学・哲学などで境界や結果の決定性を述べる。definite は一般語としてより広く使う。  "
          },
          {
            "line": 344,
            "text": "例: The process has a determinate end point.  "
          },
          {
            "line": 345,
            "text": "訳: その過程には明確に定まった終点がある。  "
          },
          {
            "line": 347,
            "text": "・fixed  "
          },
          {
            "line": 348,
            "text": "定義: 位置・数量・時期などが動かないように定められている。  "
          },
          {
            "line": 349,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 350,
            "text": "違い: fixed は変更されない状態を強く示し、definite は具体的に境界づけられた情報や範囲にも使う。  "
          },
          {
            "line": 351,
            "text": "例: The fee is fixed for the entire contract period.  "
          },
          {
            "line": 352,
            "text": "訳: 料金は契約期間全体を通じて固定されている。  "
          },
          {
            "line": 354,
            "text": "【反意語】"
          },
          {
            "line": 356,
            "text": "・indefinite  "
          },
          {
            "line": 357,
            "text": "定義: 範囲・期間・数量・内容などが決まっていない。  "
          },
          {
            "line": 358,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 359,
            "text": "違い: indefinite は定まった境界がないことを直接表し、definite は範囲や条件が具体化されていることを表す。  "
          },
          {
            "line": 360,
            "text": "例: The meeting was postponed for an indefinite period.  "
          },
          {
            "line": 361,
            "text": "訳: 会議は無期限に延期された。  "
          },
          {
            "line": 363,
            "text": "・unspecified  "
          },
          {
            "line": 364,
            "text": "定義: 必要な内容や条件が明示されていない。  "
          },
          {
            "line": 365,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 366,
            "text": "違い: unspecified は情報が指定されていないことに焦点があり、definite は情報の境界や内容が明らかであることを表す。  "
          },
          {
            "line": 367,
            "text": "例: The shipment was delayed for unspecified reasons.  "
          },
          {
            "line": 368,
            "text": "訳: その発送は理由が明示されないまま遅れた。  "
          },
          {
            "line": 370,
            "text": "・vague  "
          },
          {
            "line": 371,
            "text": "定義: 表現・考え・範囲などがぼんやりして具体性に欠ける。  "
          },
          {
            "line": 372,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 373,
            "text": "違い: vague は内容の輪郭が弱いことを表し、definite は内容を具体的に切り出せることを表す。  "
          },
          {
            "line": 374,
            "text": "例: His answer was too vague to be useful.  "
          },
          {
            "line": 375,
            "text": "訳: 彼の答えは曖昧すぎて役に立たなかった。  "
          },
          {
            "line": 377,
            "text": "・unlimited  "
          },
          {
            "line": 378,
            "text": "定義: 数量・範囲・期間などに上限がない。  "
          },
          {
            "line": 379,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 380,
            "text": "違い: unlimited は上限の不存在を示し、definite は上限や範囲が定められていることを示す。ただし、definite が必ず有限量を意味するわけではない。  "
          },
          {
            "line": 381,
            "text": "例: The plan offers unlimited data usage.  "
          },
          {
            "line": 382,
            "text": "訳: そのプランはデータ通信を無制限で提供する。  "
          }
        ]
      },
      {
        "sense_id": "sense:004",
        "full_sense": [
          {
            "line": 384,
            "text": "4. 【形容詞・文法用語】定の、特定できる"
          },
          {
            "line": 386,
            "text": "【日本語訳・定義】文法で、名詞句の指示対象が、既出、状況上の唯一性、修飾語、共有知識などによって聞き手・読み手に特定可能であることを表す。英語では the が definite article「定冠詞」であり、対象が必ず世界に一つしかないこと、単数であること、以前に必ず言及されたことだけを意味するわけではない。  "
          },
          {
            "line": 388,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 390,
            "text": "【レジスター/領域】文法・言語学の用語。英語学習では the と a/an、無冠詞の使い分けを説明するときに頻出する。definite は「特定の」という一般語義にも近いが、文法では指示対象を同定できるという性質を指す。  "
          },
          {
            "line": 392,
            "text": "【文法パターン】the definite article＝定冠詞 the／a definite noun phrase＝定名詞句／definite reference to 〈person/thing〉＝〈人・物〉への定の指示／a definite description of 〈person/thing〉＝〈人・物〉を同定する確定記述／a definite referent＝特定可能な指示対象／a noun phrase is definite＝名詞句が定である。  "
          },
          {
            "line": 394,
            "text": "【コロケーション】"
          },
          {
            "line": 396,
            "text": "・the definite article  "
          },
          {
            "line": 397,
            "text": "用途: 英語の the のように、聞き手・読み手が指示対象を特定できることを示す冠詞を指す。  "
          },
          {
            "line": 398,
            "text": "例: In English, the is the definite article used before singular and plural noun phrases.  "
          },
          {
            "line": 399,
            "text": "訳: 英語では the が、単数・複数の名詞句の前に使われる定冠詞である。  "
          },
          {
            "line": 401,
            "text": "・a definite noun phrase  "
          },
          {
            "line": 402,
            "text": "用途: 指示対象が文脈から特定可能な名詞句を指す。  "
          },
          {
            "line": 403,
            "text": "例: In “the book on the desk,” the whole phrase is a definite noun phrase.  "
          },
          {
            "line": 404,
            "text": "訳: 「机の上のその本」では、句全体が定名詞句である。  "
          },
          {
            "line": 406,
            "text": "・definite reference to 〈person/thing〉  "
          },
          {
            "line": 407,
            "text": "用途: ある人物・物を、聞き手がどれか判断できる形で指すことを表す。  "
          },
          {
            "line": 408,
            "text": "例: The article makes a definite reference to the company’s earlier report.  "
          },
          {
            "line": 409,
            "text": "訳: その記事は会社の以前の報告書を明確に指し示している。  "
          },
          {
            "line": 411,
            "text": "・a definite description of 〈person/thing〉  "
          },
          {
            "line": 412,
            "text": "用途: 固有名を使わず、記述によって指示対象を同定する表現を指す。  "
          },
          {
            "line": 413,
            "text": "例: “The first person to arrive” is a definite description in this context.  "
          },
          {
            "line": 414,
            "text": "訳: この文脈では、「最初に到着した人」は確定記述である。  "
          },
          {
            "line": 416,
            "text": "・a definite referent  "
          },
          {
            "line": 417,
            "text": "用途: 名詞句が指し示す、文脈上特定可能な対象を指す。  "
          },
          {
            "line": 418,
            "text": "例: The plural noun phrase can still have a definite referent.  "
          },
          {
            "line": 419,
            "text": "訳: 複数名詞句でも、指示対象を特定できる場合がある。  "
          },
          {
            "line": 421,
            "text": "・definite and indefinite articles  "
          },
          {
            "line": 422,
            "text": "用途: the と a/an のように、指示対象の特定可能性が異なる冠詞を対比する。  "
          },
          {
            "line": 423,
            "text": "例: The lesson contrasts definite and indefinite articles in everyday sentences.  "
          },
          {
            "line": 424,
            "text": "訳: その授業では、日常文における定冠詞と不定冠詞を対比している。  "
          },
          {
            "line": 426,
            "text": "【語法・注意】文法上の definite は「前に一度出た名詞」に限られない。`the door` はその場に一つしかないドアを指せるし、`the book on the desk` は修飾語によってどの本か分かるため定になる。単数か複数か、可算か不可算かも決定条件ではなく、`the books`、`the water` も定になり得る。specific は「特定のものを意図している」という意味で、`a specific book` のように不定冠詞と共存できるが、specific だから文法上 definite になるわけではない。英語の the には、種類全体を述べる `The tiger is endangered.` のような総称的用法もあるため、definite と「唯一の個体」を機械的に同一視しない。  "
          },
          {
            "line": 428,
            "text": "【類義語】"
          },
          {
            "line": 430,
            "text": "・identified  "
          },
          {
            "line": 431,
            "text": "定義: どの人物・物を指すかが分かっている、または特定されている。  "
          },
          {
            "line": 432,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 433,
            "text": "違い: identified は対象が同定されている状態を平易に述べる。definite は名詞句の文法的な指示性を表す用語である。  "
          },
          {
            "line": 434,
            "text": "例: The identified object was removed from the scene.  "
          },
          {
            "line": 435,
            "text": "訳: 特定された物体は現場から取り除かれた。  "
          },
          {
            "line": 437,
            "text": "・determinate  "
          },
          {
            "line": 438,
            "text": "定義: 境界・値・指示対象などが決まっている。  "
          },
          {
            "line": 439,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 440,
            "text": "違い: determinate は形式的・専門的で、definite は英語の冠詞や名詞句の性質を説明する標準用語である。  "
          },
          {
            "line": 441,
            "text": "例: The expression has a determinate meaning in this context.  "
          },
          {
            "line": 442,
            "text": "訳: その表現はこの文脈では明確に定まった意味を持つ。  "
          },
          {
            "line": 444,
            "text": "・specific  "
          },
          {
            "line": 445,
            "text": "定義: 一般的なものではなく、特定の人物・物・内容に関する。  "
          },
          {
            "line": 446,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 447,
            "text": "違い: specific は個別性を表す一般語で、文法上の definite と重なることはあるが、`a specific book` のように不定名詞句にも使える。  "
          },
          {
            "line": 448,
            "text": "例: She was looking for a specific file.  "
          },
          {
            "line": 449,
            "text": "訳: 彼女は特定のファイルを探していた。  "
          },
          {
            "line": 451,
            "text": "【反意語】"
          },
          {
            "line": 453,
            "text": "・indefinite  "
          },
          {
            "line": 454,
            "text": "定義: 名詞句の指示対象が特定できない、または特定の一つとして提示されない。  "
          },
          {
            "line": 455,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 456,
            "text": "違い: 文法上の indefinite は definite の直接の反対で、英語の a/an や、文脈によっては無冠詞の名詞句に関係する。  "
          },
          {
            "line": 457,
            "text": "例: “A book” is indefinite because the listener does not know which book is meant.  "
          },
          {
            "line": 458,
            "text": "訳: 「ある本」は、どの本を指すか聞き手に分からないため不定である。  "
          },
          {
            "line": 460,
            "text": "・unidentified  "
          },
          {
            "line": 461,
            "text": "定義: どの人物・物であるかが特定されていない。  "
          },
          {
            "line": 462,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 463,
            "text": "違い: unidentified は現実の対象を同定できない状態を示し、definite は文法上の名詞句が対象を特定可能に提示する状態を示す。  "
          },
          {
            "line": 464,
            "text": "例: An unidentified caller left a message.  "
          },
          {
            "line": 465,
            "text": "訳: 身元不明の発信者がメッセージを残した。  "
          },
          {
            "line": 467,
            "text": "・generic  "
          },
          {
            "line": 468,
            "text": "定義: 個別の一つではなく、種類全体や一般的な概念に関する。  "
          },
          {
            "line": 469,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 470,
            "text": "違い: generic は指示の範囲が一般化されていることを表す。definite と対照できるが、英語では definite article が総称的に使われる場合もあるため、完全な形の反意語ではない。  "
          },
          {
            "line": 471,
            "text": "例: “Dogs are social animals” has a generic reference.  "
          },
          {
            "line": 472,
            "text": "訳: 「犬は社会的な動物だ」は総称的な指示を持つ。  "
          }
        ]
      },
      {
        "sense_id": "sense:005",
        "full_sense": [
          {
            "line": 474,
            "text": "5. 【形容詞・植物学】有限の、定数の"
          },
          {
            "line": 476,
            "text": "【日本語訳・定義】植物学で、花器官の数が一定で、通常は20未満で花弁数の倍数になること、または花序の主軸が花で終わり成長に限りがあることを表す専門用法である。一般語の「確実な」ではなく、数や成長が定まっているという意味で、definite inflorescence は determinate／cymose inflorescence に当たる。  "
          },
          {
            "line": 478,
            "text": "【頻度】〈2/10〉  "
          },
          {
            "line": 480,
            "text": "【レジスター/領域】植物学に限られる低頻度の専門語。一般の文章では通常この意味で解釈せず、専門文献で floral organs、stamens、inflorescence などと共に現れる。  "
          },
          {
            "line": 482,
            "text": "【文法パターン】definite stamens＝数が一定の雄しべ／a definite inflorescence＝主軸が花で終わる有限花序／definite growth＝成長が一定の段階で止まる定限成長。  "
          },
          {
            "line": 484,
            "text": "【コロケーション】"
          },
          {
            "line": 486,
            "text": "・definite stamens  "
          },
          {
            "line": 487,
            "text": "用途: 花弁数との関係で数が一定の雄しべを指す。  "
          },
          {
            "line": 488,
            "text": "例: The species has definite stamens, usually in a fixed multiple of the number of petals.  "
          },
          {
            "line": 489,
            "text": "訳: その種には、通常、花弁数の決まった倍数になる定数の雄しべがある。  "
          },
          {
            "line": 491,
            "text": "・a definite inflorescence  "
          },
          {
            "line": 492,
            "text": "用途: 主軸が花で終わり、伸長に限りがある有限花序を指す。  "
          },
          {
            "line": 493,
            "text": "例: The plant develops a definite inflorescence in which the main axis ends in a flower.  "
          },
          {
            "line": 494,
            "text": "訳: その植物は、主軸が花で終わる有限花序を形成する。  "
          },
          {
            "line": 496,
            "text": "・definite growth  "
          },
          {
            "line": 497,
            "text": "用途: 植物体や器官の成長が一定の段階で止まる定限成長を表す。  "
          },
          {
            "line": 498,
            "text": "例: Definite growth is common in some compact flowering plants.  "
          },
          {
            "line": 499,
            "text": "訳: 定限成長は、一部の小型の開花植物でよく見られる。  "
          },
          {
            "line": 501,
            "text": "【語法・注意】この用法は一般英語の definite answer や definite plan とは別の専門的な意味である。`definite inflorescence` は花序の成長様式を指し、単に「明確な花序」という意味ではない。植物学では `indefinite` や `indeterminate` が、数や主軸の成長に固定された終点がない対照表現として使われる。  "
          },
          {
            "line": 503,
            "text": "【類義語】"
          },
          {
            "line": 505,
            "text": "・determinate  "
          },
          {
            "line": 506,
            "text": "定義: 植物の成長・花序・器官の数などが一定の限界で決まる。  "
          },
          {
            "line": 507,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 508,
            "text": "違い: determinate はこの植物学上の意味でより一般的な専門語で、definite は同じ特徴を別の語彙で表す。  "
          },
          {
            "line": 509,
            "text": "例: The plant produces a determinate inflorescence.  "
          },
          {
            "line": 510,
            "text": "訳: その植物は有限花序を形成する。  "
          },
          {
            "line": 512,
            "text": "・fixed-number  "
          },
          {
            "line": 513,
            "text": "定義: 数が一定に定められている。  "
          },
          {
            "line": 514,
            "text": "頻度: 〈2/10〉  "
          },
          {
            "line": 515,
            "text": "違い: fixed-number は説明的な表現で、definite stamens の特徴を言い換えるが、単独の標準用語としての使用は限定的である。  "
          },
          {
            "line": 516,
            "text": "例: The flower has a fixed number of stamens.  "
          },
          {
            "line": 517,
            "text": "訳: その花には一定数の雄しべがある。  "
          },
          {
            "line": 519,
            "text": "【反意語】"
          },
          {
            "line": 521,
            "text": "・indefinite  "
          },
          {
            "line": 522,
            "text": "定義: 数が一定でない、または花序の成長に固定された終点がない。  "
          },
          {
            "line": 523,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 524,
            "text": "違い: indefinite は definite stamens や definite inflorescence の反対側にある植物学用語で、器官数や成長の上限が定まらないことを示す。  "
          },
          {
            "line": 525,
            "text": "例: An indefinite inflorescence can continue producing flowers along its main axis.  "
          },
          {
            "line": 526,
            "text": "訳: 無限花序は主軸に沿って花を作り続けることがある。  "
          },
          {
            "line": 528,
            "text": "・indeterminate  "
          },
          {
            "line": 529,
            "text": "定義: 成長や結果の終点があらかじめ固定されていない。  "
          },
          {
            "line": 530,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 531,
            "text": "違い: indeterminate は植物学で definite／determinate と対立し、主軸の成長が花で終わらないことなどを表す。  "
          },
          {
            "line": 532,
            "text": "例: The species shows indeterminate rather than definite growth.  "
          },
          {
            "line": 533,
            "text": "訳: その種は定限成長ではなく不定成長を示す。  "
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
