# Independent review handoff

Stage: `checker_passes/frame-relation-antonym-axis-stage2`

This is the only serial dependency inside the parallel checker fan-out. Do not rerun the other six checker passes.
This stage must be executed by the same frame-relation agent from stage 1: reviewer.agent_id=`controversial-checker-frame-axis-20260912T015542Z-872034dc`, declared_model=`codex-gpt-5`.

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
  "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
  "blind_request_sha256": "a8571c606a5b65fde1bda9ca43c3af9db0eda2c0023b6c6059b42b9173c7c8c6",
  "blind_record_sha256": "7982b752e545a329ab06e389ce7d9dd69d2ed38b682e987daeb43d186eebedce",
  "input_sections": {
    "sense_structure": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 32,
        "text": "【日本語訳・定義】政策・決定・主張・作品・発言・人物などが、社会全体または特定の集団の中で、強い意見の対立、批判、反対を引き起こしていることを表す。事実として真偽が決まっていないことを必ずしも含まず、悪い、違法、意図的に挑発的だという意味でもない。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 158,
        "text": "【日本語訳・定義】人が性格や態度の傾向として、議論を好んだり、既存の立場に反論して対立を生みやすかったりすることを表す。辞書に記載される低頻度の語義で、現代の controversial person は通常、語義1の「論争の的となっている人物」と解釈される。  "
      }
    ],
    "frames": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 38,
        "text": "【文法パターン】be/become/remain/prove controversial＝論争を呼ぶ・論争の的であり続ける・結果的に物議を醸す／a controversial 〈issue・decision・policy・claim・statement・figure・book・film〉＝論争を呼ぶ〈問題・決定・政策・主張・発言・人物・本・映画〉／highly/widely controversial＝非常に／広く物議を醸す／controversial among/within 〈group〉＝〈集団〉の間で論争を呼ぶ／controversial in some circles＝一部の界隈では物議を醸す／it remains controversial whether ...＝…かどうかは依然として議論が分かれる／be controversial enough to do＝～するほど物議を醸す／too controversial to do＝物議を醸しすぎて～できない。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 164,
        "text": "【文法パターン】a controversial temperament＝論争を好む気質／a controversial manner＝対立を生みやすい態度／be controversial by temperament＝性向として論争的である／be controversial in debate＝議論で意図的に反論を重ねる。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 40,
        "text": "【コロケーション】"
      },
      {
        "line": 42,
        "text": "・a controversial issue  "
      },
      {
        "line": 43,
        "text": "用途: 社会的に賛否が対立している問題を指す。  "
      },
      {
        "line": 44,
        "text": "例: The use of facial-recognition technology remains a controversial issue.  "
      },
      {
        "line": 45,
        "text": "訳: 顔認証技術の利用は依然として論争を呼ぶ問題だ。  "
      },
      {
        "line": 47,
        "text": "・a controversial decision  "
      },
      {
        "line": 48,
        "text": "用途: 決定の妥当性や影響をめぐって強い反対・批判が出ていることを表す。  "
      },
      {
        "line": 49,
        "text": "例: The committee made a controversial decision to cancel the exhibition.  "
      },
      {
        "line": 50,
        "text": "訳: 委員会は展示会を中止するという物議を醸す決定を下した。  "
      },
      {
        "line": 52,
        "text": "・a controversial figure  "
      },
      {
        "line": 53,
        "text": "用途: 功績と批判の両方があり、評価が大きく割れている人物を指す。  "
      },
      {
        "line": 54,
        "text": "例: The historian remains a controversial figure in the region.  "
      },
      {
        "line": 55,
        "text": "訳: その歴史家はその地域で今も評価が大きく分かれる人物だ。  "
      },
      {
        "line": 57,
        "text": "・a highly controversial proposal  "
      },
      {
        "line": 58,
        "text": "用途: 提案に対して非常に強い賛否や反発が起きていることを強調する。  "
      },
      {
        "line": 59,
        "text": "例: The city council postponed a highly controversial proposal.  "
      },
      {
        "line": 60,
        "text": "訳: 市議会は非常に物議を醸している提案を延期した。  "
      },
      {
        "line": 62,
        "text": "・controversial among 〈group〉  "
      },
      {
        "line": 63,
        "text": "用途: どの集団の中で意見が割れているかを限定する。  "
      },
      {
        "line": 64,
        "text": "例: The interpretation is controversial among constitutional scholars.  "
      },
      {
        "line": 65,
        "text": "訳: その解釈は憲法学者の間で議論が分かれている。  "
      },
      {
        "line": 67,
        "text": "・controversial in some circles  "
      },
      {
        "line": 68,
        "text": "用途: 社会全体ではなく、特定の界隈で物議を醸していることを示す。  "
      },
      {
        "line": 69,
        "text": "例: The advertising campaign is controversial in some circles but popular with younger viewers.  "
      },
      {
        "line": 70,
        "text": "訳: その広告キャンペーンは一部では物議を醸しているが、若い視聴者には人気がある。  "
      },
      {
        "line": 72,
        "text": "・it remains controversial whether ...  "
      },
      {
        "line": 73,
        "text": "用途: 判断が現在も決着していないことを述べる。  "
      },
      {
        "line": 74,
        "text": "例: It remains controversial whether the policy reduced inequality.  "
      },
      {
        "line": 75,
        "text": "訳: その政策が格差を縮小したかどうかは、今も議論が分かれている。  "
      },
      {
        "line": 77,
        "text": "・a controversial remark  "
      },
      {
        "line": 78,
        "text": "用途: 発言が批判や反発を招く内容だったことを表す。  "
      },
      {
        "line": 79,
        "text": "例: The minister's controversial remark drew criticism from both parties.  "
      },
      {
        "line": 80,
        "text": "訳: 大臣の物議を醸す発言は両党から批判を招いた。  "
      },
      {
        "line": 82,
        "text": "・become controversial after ...  "
      },
      {
        "line": 83,
        "text": "用途: 当初は普通だった対象が、後から知られた事実や変化によって論争の的になることを表す。  "
      },
      {
        "line": 84,
        "text": "例: The renovation plan became controversial after residents learned the full cost.  "
      },
      {
        "line": 85,
        "text": "訳: 住民が総費用を知った後、その改修計画は物議を醸すようになった。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 166,
        "text": "【コロケーション】"
      },
      {
        "line": 168,
        "text": "・a controversial temperament  "
      },
      {
        "line": 169,
        "text": "用途: 人が性格的に議論や対立を好むことを、まれな形容詞用法で表す。  "
      },
      {
        "line": 170,
        "text": "例: The columnist has a controversial temperament and treats every meeting as a public debate.  "
      },
      {
        "line": 171,
        "text": "訳: そのコラムニストは論争を好む気質で、どの会議も公開討論のように扱う。  "
      },
      {
        "line": 173,
        "text": "・a controversial manner  "
      },
      {
        "line": 174,
        "text": "用途: 人が対立を招きやすい仕方で話したり振る舞ったりすることを表す。  "
      },
      {
        "line": 175,
        "text": "例: Her controversial manner turned minor technical disagreements into public arguments.  "
      },
      {
        "line": 176,
        "text": "訳: 彼女の対立を生みやすい態度は、ささいな技術上の意見の違いまで公の論争に変えた。  "
      },
      {
        "line": 178,
        "text": "・be controversial by temperament  "
      },
      {
        "line": 179,
        "text": "用途: 物議を醸す個別の行動ではなく、もともとの性向が論争的だと述べるまれな構文。  "
      },
      {
        "line": 180,
        "text": "例: He was controversial by temperament, challenging even minor points in every debate.  "
      },
      {
        "line": 181,
        "text": "訳: 彼は性向として論争的で、どの討論でもささいな点にまで反論した。  "
      },
      {
        "line": 183,
        "text": "・be controversial in debate  "
      },
      {
        "line": 184,
        "text": "用途: 議論の最中に、立場そのものよりも反論を重ねる性向が目立つことを表す。  "
      },
      {
        "line": 185,
        "text": "例: The speaker was controversial in debate because he deliberately attacked each established position.  "
      },
      {
        "line": 186,
        "text": "訳: その話者は確立した立場を一つ一つ意図的に攻撃したため、討論では論争的だった。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 89,
        "text": "【類義語】"
      },
      {
        "line": 91,
        "text": "・contentious  "
      },
      {
        "line": 92,
        "text": "定義: 議論や対立を引き起こしやすい、争点になっている。  "
      },
      {
        "line": 93,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 94,
        "text": "違い: contentious は問題・決定が争いを生みやすい性質や、当事者間の対立の強さに焦点があり、controversial より対立的に響くことがある。  "
      },
      {
        "line": 95,
        "text": "例: The contentious issue delayed the negotiations for weeks.  "
      },
      {
        "line": 96,
        "text": "訳: その対立を招く争点のために、交渉は何週間も遅れた。  "
      },
      {
        "line": 98,
        "text": "・disputed  "
      },
      {
        "line": 99,
        "text": "定義: 真偽・権利・解釈などが争われている、意見が一致していない。  "
      },
      {
        "line": 100,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 101,
        "text": "違い: disputed は「正しいか、誰のものかなどが争われている」という未確定性を強調し、controversial のような広い世論上の物議まで必ずしも含まない。  "
      },
      {
        "line": 102,
        "text": "例: The map shows the disputed border in a different color.  "
      },
      {
        "line": 103,
        "text": "訳: その地図は争われている国境を別の色で示している。  "
      },
      {
        "line": 105,
        "text": "・debatable  "
      },
      {
        "line": 106,
        "text": "定義: 議論の余地があり、結論を一つに決めにくい。  "
      },
      {
        "line": 107,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 108,
        "text": "違い: debatable は主張や判断の妥当性を論じられることに焦点があり、controversial より感情的な反発や大きな社会的対立を含まない場合が多い。  "
      },
      {
        "line": 109,
        "text": "例: Whether the change improved efficiency is debatable.  "
      },
      {
        "line": 110,
        "text": "訳: その変更が効率を高めたかどうかは議論の余地がある。  "
      },
      {
        "line": 112,
        "text": "・polarizing  "
      },
      {
        "line": 113,
        "text": "定義: 人々を賛成側と反対側へ大きく分断する。  "
      },
      {
        "line": 114,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 115,
        "text": "違い: polarizing は意見の対立を二極化させる効果を強調する。controversial は意見が割れていても、二つの陣営に明確に分かれるとは限らない。  "
      },
      {
        "line": 116,
        "text": "例: The candidate's polarizing speech dominated the news cycle.  "
      },
      {
        "line": 117,
        "text": "訳: その候補者の社会を二極化させる演説が報道を席巻した。  "
      },
      {
        "line": 119,
        "text": "・provocative  "
      },
      {
        "line": 120,
        "text": "定義: 強い反応や議論を意図的または効果として引き起こす、挑発的な。  "
      },
      {
        "line": 121,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 122,
        "text": "違い: provocative は発言者・作者が反応を誘う性質や意図に焦点がある。controversial は実際に物議が生じている状態を表し、意図を必要としない。  "
      },
      {
        "line": 123,
        "text": "例: The artist is known for provocative questions about public memory.  "
      },
      {
        "line": 124,
        "text": "訳: その芸術家は公共の記憶について挑発的な問いを投げかけることで知られている。  "
      },
      {
        "line": 126,
        "text": "・divisive  "
      },
      {
        "line": 127,
        "text": "定義: 人々や集団の間に深い対立を生じさせる、分断を招く。  "
      },
      {
        "line": 128,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 129,
        "text": "違い: divisive は社会的な分断や関係悪化という結果を強く示す。controversial は分断に至らず、単に議論や批判を招く場合にも使える。  "
      },
      {
        "line": 130,
        "text": "例: The divisive reform split the professional association.  "
      },
      {
        "line": 131,
        "text": "訳: その分断を招く改革は専門職団体を二分した。  "
      },
      {
        "line": 133,
        "text": "・polemical  "
      },
      {
        "line": 134,
        "text": "定義: 論争を仕掛ける、または論争的な主張を展開する。  "
      },
      {
        "line": 135,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 136,
        "text": "違い: polemical は文章・議論・論者の攻撃的な論争スタイルに寄りやすく、controversial より硬く、意図的な論争性を含みやすい。  "
      },
      {
        "line": 137,
        "text": "例: The book adopts a polemical tone toward established theories.  "
      },
      {
        "line": 138,
        "text": "訳: その本は確立した理論に対して論争的な調子を取っている。  "
      },
      {
        "line": 140,
        "text": "【反意語】"
      },
      {
        "line": 142,
        "text": "・uncontroversial  "
      },
      {
        "line": 143,
        "text": "定義: 意見の強い対立や広い反発を招かない、異論の少ない。  "
      },
      {
        "line": 144,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 145,
        "text": "違い: controversial の直接的な反対語で、問題・判断・人物などについて大きな論争が起きていない状態を表す。  "
      },
      {
        "line": 146,
        "text": "例: The committee reached an uncontroversial agreement on the timetable.  "
      },
      {
        "line": 147,
        "text": "訳: 委員会は日程について異論の少ない合意に達した。  "
      },
      {
        "line": 149,
        "text": "・noncontroversial  "
      },
      {
        "line": 150,
        "text": "定義: 論争的でない、特に意見の対立を起こさない。  "
      },
      {
        "line": 151,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 152,
        "text": "違い: noncontroversial も直接的な反対語だが、uncontroversial より説明的・形式的に見えることがある。  "
      },
      {
        "line": 153,
        "text": "例: The report limits itself to noncontroversial background facts.  "
      },
      {
        "line": 154,
        "text": "訳: その報告書は論争のない背景事実に内容を限定している。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 190,
        "text": "【類義語】"
      },
      {
        "line": 192,
        "text": "・disputatious  "
      },
      {
        "line": 193,
        "text": "定義: 議論や口論を好む、論争好きな。  "
      },
      {
        "line": 194,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 195,
        "text": "違い: disputatious は人の性向そのものを表す明確な語で、controversial のまれな語義より自然に「口論好き」の意味を示す。  "
      },
      {
        "line": 196,
        "text": "例: His disputatious nature made routine committee work exhausting.  "
      },
      {
        "line": 197,
        "text": "訳: 彼の論争好きな性質のため、通常の委員会業務は疲れるものになった。  "
      },
      {
        "line": 199,
        "text": "・argumentative  "
      },
      {
        "line": 200,
        "text": "定義: すぐに反論する、議論好きな、口論を招く。  "
      },
      {
        "line": 201,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 202,
        "text": "違い: argumentative は日常的で、人が何にでも反論する傾向を表す。controversial より口論・反論の行動が前面に出る。  "
      },
      {
        "line": 203,
        "text": "例: The child became argumentative whenever the rules were explained.  "
      },
      {
        "line": 204,
        "text": "訳: その子は規則を説明されるといつも反論するようになった。  "
      },
      {
        "line": 206,
        "text": "・polemical  "
      },
      {
        "line": 207,
        "text": "定義: 論争を仕掛ける、攻撃的に論争する。  "
      },
      {
        "line": 208,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 209,
        "text": "違い: polemical は論者・文章・議論の意図的で攻撃的な論争性に焦点があり、controversial より文語的である。  "
      },
      {
        "line": 210,
        "text": "例: The polemical writer challenged every compromise proposed by the panel.  "
      },
      {
        "line": 211,
        "text": "訳: その論争的な筆者は、委員会が提案した妥協案すべてに異議を唱えた。  "
      },
      {
        "line": 213,
        "text": "・contentious  "
      },
      {
        "line": 214,
        "text": "定義: 対立的で、争いを引き起こしやすい。  "
      },
      {
        "line": 215,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 216,
        "text": "違い: contentious は人の態度にも使えるが、敵対的・喧嘩腰の含みが出やすい。controversial の語義2は、必ずしも敵意や攻撃性まで含まない。  "
      },
      {
        "line": 217,
        "text": "例: The manager's contentious style made open discussion difficult.  "
      },
      {
        "line": 218,
        "text": "訳: その管理職の対立的なスタイルは、率直な話し合いを難しくした。  "
      }
    ],
    "antonym_axis_items": [
      {
        "item_id": "ant-9155f1ca66db",
        "stage1_axis": {
          "item_id": "ant-9155f1ca66db",
          "axis": "状態",
          "relation_type": "状態",
          "reason": "The adjective contrasts a state of being publicly disputed with a state in which that dispute is absent."
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 142,
          "line_end": 142,
          "exact_quote": "・uncontroversial  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 145,
          "line_end": 145,
          "exact_quote": "違い: controversial の直接的な反対語で、問題・判断・人物などについて大きな論争が起きていない状態を表す。  "
        }
      },
      {
        "item_id": "ant-5e1d39a9d098",
        "stage1_axis": {
          "item_id": "ant-5e1d39a9d098",
          "axis": "状態",
          "relation_type": "状態",
          "reason": "The negative adjective describes the corresponding noncontroversial state rather than a higher or lower degree of controversy."
        },
        "sense_id": "sense:001",
        "anchor": {
          "section": "lexical_relations",
          "line_start": 149,
          "line_end": 149,
          "exact_quote": "・noncontroversial  "
        },
        "difference_anchor": {
          "section": "lexical_relations",
          "line_start": 152,
          "line_end": 152,
          "exact_quote": "違い: noncontroversial も直接的な反対語だが、uncontroversial より説明的・形式的に見えることがある。  "
        }
      }
    ],
    "antonym_axis_senses": [
      {
        "sense_id": "sense:001",
        "full_sense": [
          {
            "line": 30,
            "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
          },
          {
            "line": 32,
            "text": "【日本語訳・定義】政策・決定・主張・作品・発言・人物などが、社会全体または特定の集団の中で、強い意見の対立、批判、反対を引き起こしていることを表す。事実として真偽が決まっていないことを必ずしも含まず、悪い、違法、意図的に挑発的だという意味でもない。  "
          },
          {
            "line": 34,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 36,
            "text": "【レジスター/領域】標準語で、会話・ニュース・政治・文化・学術・ビジネスの文章まで広く使う。controversial は「多くの人が反対している」と同じではなく、賛成・反対の議論が強く起きている状態を指す。  "
          },
          {
            "line": 38,
            "text": "【文法パターン】be/become/remain/prove controversial＝論争を呼ぶ・論争の的であり続ける・結果的に物議を醸す／a controversial 〈issue・decision・policy・claim・statement・figure・book・film〉＝論争を呼ぶ〈問題・決定・政策・主張・発言・人物・本・映画〉／highly/widely controversial＝非常に／広く物議を醸す／controversial among/within 〈group〉＝〈集団〉の間で論争を呼ぶ／controversial in some circles＝一部の界隈では物議を醸す／it remains controversial whether ...＝…かどうかは依然として議論が分かれる／be controversial enough to do＝～するほど物議を醸す／too controversial to do＝物議を醸しすぎて～できない。  "
          },
          {
            "line": 40,
            "text": "【コロケーション】"
          },
          {
            "line": 42,
            "text": "・a controversial issue  "
          },
          {
            "line": 43,
            "text": "用途: 社会的に賛否が対立している問題を指す。  "
          },
          {
            "line": 44,
            "text": "例: The use of facial-recognition technology remains a controversial issue.  "
          },
          {
            "line": 45,
            "text": "訳: 顔認証技術の利用は依然として論争を呼ぶ問題だ。  "
          },
          {
            "line": 47,
            "text": "・a controversial decision  "
          },
          {
            "line": 48,
            "text": "用途: 決定の妥当性や影響をめぐって強い反対・批判が出ていることを表す。  "
          },
          {
            "line": 49,
            "text": "例: The committee made a controversial decision to cancel the exhibition.  "
          },
          {
            "line": 50,
            "text": "訳: 委員会は展示会を中止するという物議を醸す決定を下した。  "
          },
          {
            "line": 52,
            "text": "・a controversial figure  "
          },
          {
            "line": 53,
            "text": "用途: 功績と批判の両方があり、評価が大きく割れている人物を指す。  "
          },
          {
            "line": 54,
            "text": "例: The historian remains a controversial figure in the region.  "
          },
          {
            "line": 55,
            "text": "訳: その歴史家はその地域で今も評価が大きく分かれる人物だ。  "
          },
          {
            "line": 57,
            "text": "・a highly controversial proposal  "
          },
          {
            "line": 58,
            "text": "用途: 提案に対して非常に強い賛否や反発が起きていることを強調する。  "
          },
          {
            "line": 59,
            "text": "例: The city council postponed a highly controversial proposal.  "
          },
          {
            "line": 60,
            "text": "訳: 市議会は非常に物議を醸している提案を延期した。  "
          },
          {
            "line": 62,
            "text": "・controversial among 〈group〉  "
          },
          {
            "line": 63,
            "text": "用途: どの集団の中で意見が割れているかを限定する。  "
          },
          {
            "line": 64,
            "text": "例: The interpretation is controversial among constitutional scholars.  "
          },
          {
            "line": 65,
            "text": "訳: その解釈は憲法学者の間で議論が分かれている。  "
          },
          {
            "line": 67,
            "text": "・controversial in some circles  "
          },
          {
            "line": 68,
            "text": "用途: 社会全体ではなく、特定の界隈で物議を醸していることを示す。  "
          },
          {
            "line": 69,
            "text": "例: The advertising campaign is controversial in some circles but popular with younger viewers.  "
          },
          {
            "line": 70,
            "text": "訳: その広告キャンペーンは一部では物議を醸しているが、若い視聴者には人気がある。  "
          },
          {
            "line": 72,
            "text": "・it remains controversial whether ...  "
          },
          {
            "line": 73,
            "text": "用途: 判断が現在も決着していないことを述べる。  "
          },
          {
            "line": 74,
            "text": "例: It remains controversial whether the policy reduced inequality.  "
          },
          {
            "line": 75,
            "text": "訳: その政策が格差を縮小したかどうかは、今も議論が分かれている。  "
          },
          {
            "line": 77,
            "text": "・a controversial remark  "
          },
          {
            "line": 78,
            "text": "用途: 発言が批判や反発を招く内容だったことを表す。  "
          },
          {
            "line": 79,
            "text": "例: The minister's controversial remark drew criticism from both parties.  "
          },
          {
            "line": 80,
            "text": "訳: 大臣の物議を醸す発言は両党から批判を招いた。  "
          },
          {
            "line": 82,
            "text": "・become controversial after ...  "
          },
          {
            "line": 83,
            "text": "用途: 当初は普通だった対象が、後から知られた事実や変化によって論争の的になることを表す。  "
          },
          {
            "line": 84,
            "text": "例: The renovation plan became controversial after residents learned the full cost.  "
          },
          {
            "line": 85,
            "text": "訳: 住民が総費用を知った後、その改修計画は物議を醸すようになった。  "
          },
          {
            "line": 87,
            "text": "【語法・注意】対象を主語にした be controversial は「その対象が論争の的だ」という意味で、必ずしも対象自身が議論を仕掛けるわけではない。人物についても通常は「評価が割れている人物」の意味であり、「論争を好む人」という性向を言いたいときは語義2を確認する。highly は対立の強さ、widely は論争が広い範囲に及ぶことを示す。controversial を「間違った」「受け入れられない」と自動的に訳さず、何が誰の間で争われているかを among/within 句や文脈で補う。  "
          },
          {
            "line": 89,
            "text": "【類義語】"
          },
          {
            "line": 91,
            "text": "・contentious  "
          },
          {
            "line": 92,
            "text": "定義: 議論や対立を引き起こしやすい、争点になっている。  "
          },
          {
            "line": 93,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 94,
            "text": "違い: contentious は問題・決定が争いを生みやすい性質や、当事者間の対立の強さに焦点があり、controversial より対立的に響くことがある。  "
          },
          {
            "line": 95,
            "text": "例: The contentious issue delayed the negotiations for weeks.  "
          },
          {
            "line": 96,
            "text": "訳: その対立を招く争点のために、交渉は何週間も遅れた。  "
          },
          {
            "line": 98,
            "text": "・disputed  "
          },
          {
            "line": 99,
            "text": "定義: 真偽・権利・解釈などが争われている、意見が一致していない。  "
          },
          {
            "line": 100,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 101,
            "text": "違い: disputed は「正しいか、誰のものかなどが争われている」という未確定性を強調し、controversial のような広い世論上の物議まで必ずしも含まない。  "
          },
          {
            "line": 102,
            "text": "例: The map shows the disputed border in a different color.  "
          },
          {
            "line": 103,
            "text": "訳: その地図は争われている国境を別の色で示している。  "
          },
          {
            "line": 105,
            "text": "・debatable  "
          },
          {
            "line": 106,
            "text": "定義: 議論の余地があり、結論を一つに決めにくい。  "
          },
          {
            "line": 107,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 108,
            "text": "違い: debatable は主張や判断の妥当性を論じられることに焦点があり、controversial より感情的な反発や大きな社会的対立を含まない場合が多い。  "
          },
          {
            "line": 109,
            "text": "例: Whether the change improved efficiency is debatable.  "
          },
          {
            "line": 110,
            "text": "訳: その変更が効率を高めたかどうかは議論の余地がある。  "
          },
          {
            "line": 112,
            "text": "・polarizing  "
          },
          {
            "line": 113,
            "text": "定義: 人々を賛成側と反対側へ大きく分断する。  "
          },
          {
            "line": 114,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 115,
            "text": "違い: polarizing は意見の対立を二極化させる効果を強調する。controversial は意見が割れていても、二つの陣営に明確に分かれるとは限らない。  "
          },
          {
            "line": 116,
            "text": "例: The candidate's polarizing speech dominated the news cycle.  "
          },
          {
            "line": 117,
            "text": "訳: その候補者の社会を二極化させる演説が報道を席巻した。  "
          },
          {
            "line": 119,
            "text": "・provocative  "
          },
          {
            "line": 120,
            "text": "定義: 強い反応や議論を意図的または効果として引き起こす、挑発的な。  "
          },
          {
            "line": 121,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 122,
            "text": "違い: provocative は発言者・作者が反応を誘う性質や意図に焦点がある。controversial は実際に物議が生じている状態を表し、意図を必要としない。  "
          },
          {
            "line": 123,
            "text": "例: The artist is known for provocative questions about public memory.  "
          },
          {
            "line": 124,
            "text": "訳: その芸術家は公共の記憶について挑発的な問いを投げかけることで知られている。  "
          },
          {
            "line": 126,
            "text": "・divisive  "
          },
          {
            "line": 127,
            "text": "定義: 人々や集団の間に深い対立を生じさせる、分断を招く。  "
          },
          {
            "line": 128,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 129,
            "text": "違い: divisive は社会的な分断や関係悪化という結果を強く示す。controversial は分断に至らず、単に議論や批判を招く場合にも使える。  "
          },
          {
            "line": 130,
            "text": "例: The divisive reform split the professional association.  "
          },
          {
            "line": 131,
            "text": "訳: その分断を招く改革は専門職団体を二分した。  "
          },
          {
            "line": 133,
            "text": "・polemical  "
          },
          {
            "line": 134,
            "text": "定義: 論争を仕掛ける、または論争的な主張を展開する。  "
          },
          {
            "line": 135,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 136,
            "text": "違い: polemical は文章・議論・論者の攻撃的な論争スタイルに寄りやすく、controversial より硬く、意図的な論争性を含みやすい。  "
          },
          {
            "line": 137,
            "text": "例: The book adopts a polemical tone toward established theories.  "
          },
          {
            "line": 138,
            "text": "訳: その本は確立した理論に対して論争的な調子を取っている。  "
          },
          {
            "line": 140,
            "text": "【反意語】"
          },
          {
            "line": 142,
            "text": "・uncontroversial  "
          },
          {
            "line": 143,
            "text": "定義: 意見の強い対立や広い反発を招かない、異論の少ない。  "
          },
          {
            "line": 144,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 145,
            "text": "違い: controversial の直接的な反対語で、問題・判断・人物などについて大きな論争が起きていない状態を表す。  "
          },
          {
            "line": 146,
            "text": "例: The committee reached an uncontroversial agreement on the timetable.  "
          },
          {
            "line": 147,
            "text": "訳: 委員会は日程について異論の少ない合意に達した。  "
          },
          {
            "line": 149,
            "text": "・noncontroversial  "
          },
          {
            "line": 150,
            "text": "定義: 論争的でない、特に意見の対立を起こさない。  "
          },
          {
            "line": 151,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 152,
            "text": "違い: noncontroversial も直接的な反対語だが、uncontroversial より説明的・形式的に見えることがある。  "
          },
          {
            "line": 153,
            "text": "例: The report limits itself to noncontroversial background facts.  "
          },
          {
            "line": 154,
            "text": "訳: その報告書は論争のない背景事実に内容を限定している。  "
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
