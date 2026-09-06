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
  "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "15世紀初頭に、フランス語を経てラテン語 intensus「引き伸ばされた、張り詰めた」から英語に入った。intensus は intendere の過去分詞に由来する。  "
      },
      {
        "line": 21,
        "text": "現在の intense は、程度・力・感情などの強度や度合いが非常に高いことを表す。  "
      }
    ],
    "word_formation": [
      {
        "line": 23,
        "text": "＃語形成"
      },
      {
        "line": 25,
        "text": "・intensity（名詞）— 強度、激しさ。  "
      },
      {
        "line": 26,
        "text": "・intensify（動詞）— 強まる、強める。自動詞・他動詞の両方で使う。  "
      },
      {
        "line": 27,
        "text": "・intensive（形容詞）— 集中的な、徹底的な。限られた期間・範囲に活動や資源を集中投入することを表す。intense と活動用法で重なる場合があるが、intense は強度・力・緊張・感情の高さに、intensive は集中投入の範囲・期間に焦点を置きやすい。  "
      },
      {
        "line": 28,
        "text": "・intensification（名詞）— 強化、激化。  "
      }
    ],
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、色、関心、圧力などの程度・強度が非常に高いこと。intense pleasure「非常に強い喜び」のように、好ましい対象にも使う。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 111,
        "text": "【日本語訳・定義】活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 158,
        "text": "【日本語訳・定義】人・視線・表情・関係などについて、強い感情や意見が表れる、強く感じられる、または強い感情的な結びつきがあること。人・表情の表出、人物への評価、関係の情緒的な強さを区別する。  "
      }
    ],
    "frequency_register": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 44,
        "text": "【頻度】〈5/10〉  "
      },
      {
        "line": 48,
        "text": "【レジスター/領域】一般語として使われる形容詞。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 113,
        "text": "【頻度】〈5/10〉  "
      },
      {
        "line": 115,
        "text": "【レジスター/領域】一般語として使われる形容詞。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 160,
        "text": "【頻度】〈5/10〉  "
      },
      {
        "line": 162,
        "text": "【レジスター/領域】一般語として使われる形容詞。  "
      }
    ],
    "usage_notes": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 84,
        "text": "【語法・注意】intense は感情、感覚、熱、色、関心、圧力など、強さの対象を表す名詞と結びつく。intense pleasure のような好ましい対象にも、intense pain や intense anger のような好ましくない対象にも使える。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 131,
        "text": "【語法・注意】intense は強度・力・緊張・感情が高いことを表し、intensive は限られた期間・範囲に活動や資源を集中投入することを表す傾向がある。活動用法では重なる場合があり、感情性・客観性だけを決め手にしない。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 183,
        "text": "【語法・注意】人への用法は強い感情や態度を持つという評価で、必ず外に表出するとは限らない。視線・表情では集中・鋭さ・感情の表れ、relationship では情緒的な結びつきや相互作用の強さを表す。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 52,
        "text": "【コロケーション】"
      },
      {
        "line": 54,
        "text": "・intense pain  "
      },
      {
        "line": 55,
        "text": "用途: 身体的な痛みが非常に強いことを表す。  "
      },
      {
        "line": 56,
        "text": "例: He felt intense pain in his lower back.  "
      },
      {
        "line": 57,
        "text": "訳: 彼は腰の下部に激しい痛みを感じた。  "
      },
      {
        "line": 59,
        "text": "・intense heat  "
      },
      {
        "line": 60,
        "text": "用途: 暑さや熱が非常に強いことを表す。  "
      },
      {
        "line": 61,
        "text": "例: The intense heat made it dangerous to work outside.  "
      },
      {
        "line": 62,
        "text": "訳: 強烈な暑さのため、屋外で働くのは危険だった。  "
      },
      {
        "line": 64,
        "text": "・intense pressure  "
      },
      {
        "line": 65,
        "text": "用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  "
      },
      {
        "line": 66,
        "text": "例: The new manager is under intense pressure to improve the results.  "
      },
      {
        "line": 67,
        "text": "訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  "
      },
      {
        "line": 69,
        "text": "・intense interest  "
      },
      {
        "line": 70,
        "text": "用途: ある対象に向けられる関心が非常に強いことを表す。  "
      },
      {
        "line": 71,
        "text": "例: The discovery attracted intense interest from researchers around the world.  "
      },
      {
        "line": 72,
        "text": "訳: その発見は世界中の研究者から強い関心を集めた。  "
      },
      {
        "line": 74,
        "text": "・intense anger  "
      },
      {
        "line": 75,
        "text": "用途: 怒りの感情が非常に強いことを表す。  "
      },
      {
        "line": 76,
        "text": "例: The decision provoked intense anger among local residents.  "
      },
      {
        "line": 77,
        "text": "訳: その決定は地元住民の激しい怒りを引き起こした。  "
      },
      {
        "line": 79,
        "text": "・intense blue  "
      },
      {
        "line": 80,
        "text": "用途: 色の強さや濃さが際立ち、強い印象を与えることを表す。  "
      },
      {
        "line": 81,
        "text": "例: The intense blue of the lake stood out against the white snow.  "
      },
      {
        "line": 82,
        "text": "訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 119,
        "text": "【コロケーション】"
      },
      {
        "line": 121,
        "text": "・intense competition  "
      },
      {
        "line": 122,
        "text": "用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。  "
      },
      {
        "line": 123,
        "text": "例: There is intense competition for places at the top universities.  "
      },
      {
        "line": 124,
        "text": "訳: 一流大学の枠をめぐって激しい競争がある。  "
      },
      {
        "line": 126,
        "text": "・intense activity  "
      },
      {
        "line": 127,
        "text": "用途: 活動の強度・エネルギー・負荷が非常に高いことを表す。  "
      },
      {
        "line": 128,
        "text": "例: The airport experienced a period of intense activity before the holiday.  "
      },
      {
        "line": 129,
        "text": "訳: その空港では休暇前に活動が非常に活発な時期があった。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 166,
        "text": "【コロケーション】"
      },
      {
        "line": 168,
        "text": "・an intense look  "
      },
      {
        "line": 169,
        "text": "用途: 強い感情や集中を帯びた視線・表情を表す。  "
      },
      {
        "line": 170,
        "text": "例: She gave him an intense look when he mentioned the accusation.  "
      },
      {
        "line": 171,
        "text": "訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  "
      },
      {
        "line": 173,
        "text": "・an intense person  "
      },
      {
        "line": 174,
        "text": "用途: 感情や態度が強く、存在感や圧のある人を表す。肯定・否定の評価は文脈で変わる。  "
      },
      {
        "line": 175,
        "text": "例: He is an intense person who takes every project very seriously.  "
      },
      {
        "line": 176,
        "text": "訳: 彼はどのプロジェクトにも非常に真剣に取り組む、強い存在感のある人だ。  "
      },
      {
        "line": 178,
        "text": "・an intense relationship  "
      },
      {
        "line": 179,
        "text": "用途: 感情的な結びつきや相互作用が非常に強い関係を表す。  "
      },
      {
        "line": 180,
        "text": "例: Their intense relationship left little room for emotional distance.  "
      },
      {
        "line": 181,
        "text": "訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  "
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
  }
}
```
