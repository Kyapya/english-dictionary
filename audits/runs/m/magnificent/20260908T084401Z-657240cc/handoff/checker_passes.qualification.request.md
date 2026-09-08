# Independent checker handoff

Stage: `checker_passes/qualification`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.qualification.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_qualification_v6

## 目的

地域・レジスター・頻度・専門制度の限定と、絶対表現の適用範囲を検査する。

## 担当タクソノミー分類

- `regional_qualification`
- `absolute_scope_counterexample`
- `technical_terminology_conventionality`

## 検査ルール

- 米英差・地域差は綴りや発音だけでなく、語義、構文、頻度、自然さ、法域・制度の範囲を確認する。一地域の資料を英語全体へ一般化しない。
- 頻度は英語全体での遭遇頻度として判定し、同一見出し語内の相対順位や特定領域内だけの頻度を使わない。
- 高頻度の主要品詞・主要構文を低頻度の古語・地域語・専門語より先に置き、説明量も優先する。項目数の多さで主要用法の欠落を相殺しない。
- 「必ず」「常に」「最低限」「のみ」「できない」「人なら／物なら」等は、否定、比較、程度表現、別フレームによる反例・打ち消し可能性を探す。傾向・含みを必須条件にしない。
- 各定義主張を、必須条件、傾向・含み、特定条件に限定されるものへ分け、主要フレームへの適用範囲を確認する。
- 法律、保険、税務、医療、資格制度等では、辞書上の語彙的意味と制度上の成立要件、手続き、当事者、対象、効果を分ける。
- 専門訳語・慣用表現を一般語の直訳で置換せず、対象法域・制度の一次資料または信頼できる専門資料で慣用性と範囲を確認する。
- 専門義ブロックの各pattern・collocation・exampleが当該専門義として明確に成立するか確認する。一般義にも同程度に読める例は専門義の中心例にしない。
- 専門・地域ラベルを語義全体へ付けたとき、ブロック内の別一般義・別法域・別レジスターが混入しないか確認する。
- 語源、年代、意味変化、地域差、頻度を根拠以上に断定しない。資料が食い違い範囲を限定できなければhold相当のfindingを返す。

## 入力として受け取るセクション

- `etymology`
- `word_formation`
- `sense_structure`
- `frequency_register`
- `usage_notes`
- `collocations_examples`

## findingの出力スキーマ

```json
{
  "taxonomy_id": "regional_qualification | absolute_scope_counterexample | technical_terminology_conventionality",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "限定不足・反例・専門慣用性の問題",
  "evidence_link_ids": [],
  "suggested_direction": "適用範囲、法域、傾向、専門訳を直す方向"
}
```


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "qualification",
  "taxonomy_ids": [
    "regional_qualification",
    "absolute_scope_counterexample",
    "technical_terminology_conventionality"
  ],
  "specification": "prompts/check_pass_qualification_v6.md",
  "input_body_sha256": "258c1b3a17708126df77cb8e5db1556a9e738d56dd4183d8ccca00569461cdb7",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "中英語期に古フランス語 `magnificent` またはラテン語 `magnificent-` を経て入り、ラテン語 `magnificus`「偉大なことを行う、壮麗な」にさかのぼる。`magnus`「大きい、偉大な」と `facere`「作る、行う」に関係し、もともとの「偉大なことを行う」という評価が、現在の「壮麗な」「すばらしい」につながっている。`magnitude`「大きさ、重大さ」や `magnify`「拡大する、誇張する」は同じ `magn-` の語族である。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・`magnificence`（名詞）— 壮麗さ、すばらしさ。建物・景観などの威容にも、行為・成果のすばらしさにも使う。  "
      },
      {
        "line": 24,
        "text": "・`magnificently`（副詞）— 壮麗に、見事に、すばらしく。`perform magnificently`「見事に演じる」のように動作の出来も評価する。  "
      }
    ],
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
    "frequency_register": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
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
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 117,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 119,
        "text": "【レジスター/領域】標準語。やや強く高揚した称賛で、会話、批評、スポーツ、報道などに使う。日常会話では `great` や `excellent` のほうが中立的で頻繁である。  "
      }
    ],
    "usage_notes": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 65,
        "text": "【語法・注意】`magnificent` は限定用法にも叙述用法にも使える。外観について使うと、「きれいな」だけでなく、規模、豪華さ、威厳などが生む強い感銘まで表す。人に使う場合、`She looks magnificent.` のように外見を称賛できるが、`a magnificent person` は文脈により語義2の人格・力量への高い評価にもなる。比較変化は文法上可能だが、通常は `more/most magnificent` を用い、絶対的な称賛として原級で使うことも多い。  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 155,
        "text": "【語法・注意】語義2では、対象の外観ではなく質・出来・価値を評価する。`a magnificent performance` は演技や演奏が非常に優れていたという意味であり、必ずしも豪華な舞台だったという意味ではない。`feel magnificent` は「堂々として感じる」ではなく「気分・体調が最高だ」という読みになる。`magnificent` は強い称賛なので、日常の小さな良さに使うと意図的に大げさ、ユーモラス、または熱のこもった響きになることがある。  "
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
    ]
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
  },
  "specification_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
  "source_artifact_sha256": "681a574947ead18b804096165079a4800c3edc22edfc1d7189d38bc0e6cafbb6",
  "normalized_input_sha256": "2d7c645b23ad5389a9c31c97bdd9550630194277ca076980d4e39c97b7e91fb6"
}
```
