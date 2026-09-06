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
  "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
  "input_sections": {
    "etymology": [
      {
        "line": 19,
        "text": "＃語源"
      },
      {
        "line": 21,
        "text": "中英語期に、古フランス語 intense またはラテン語 intensus「きつく引き伸ばされた、張り詰めた、緊張した」から英語に入った。intensus は intendere「伸ばす、向ける、張る」の過去分詞で、in-「～へ」と tendere「伸ばす」に分解される。  "
      },
      {
        "line": 23,
        "text": "現代英語では、そこから「程度・力・感情・活動が極端に強い」という意味が発達した。intend「意図する」も語源上は同じラテン語系統に属するが、現代の意味は intense の派生義として理解しない。  "
      }
    ],
    "word_formation": [
      {
        "line": 25,
        "text": "＃語形成"
      },
      {
        "line": 27,
        "text": "・intensity（名詞）— 強度、激しさ。  "
      },
      {
        "line": 28,
        "text": "・intensify（動詞）— 強まる、強める。自動詞・他動詞の両方で使う。  "
      },
      {
        "line": 29,
        "text": "・intensely（副詞）— 激しく、強烈に。  "
      },
      {
        "line": 30,
        "text": "・intensive（形容詞）— 集中的な、徹底的な。intense と重なる場合もあるが、客観的な密度・集中を表しやすい。  "
      },
      {
        "line": 31,
        "text": "・intensification（名詞）— 強化、激化。  "
      }
    ],
    "sense_structure": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 45,
        "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、光、色、関心、圧力などの程度が極端に強いこと。単に「強い」というより、対象にかかる力や感じられる圧が大きいことを表す。必ず不快・否定的とは限らず、intense pleasure「非常に強い喜び」のように好ましい対象にも使う。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 156,
        "text": "【日本語訳・定義】活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。対象の客観的な密度だけでなく、それに参加・直面する人が感じる圧や負荷を表すことがある。  "
      },
      {
        "line": 258,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 260,
        "text": "【日本語訳・定義】人、視線、表情、会話、関係などが、非常に強い感情、意見、考え、目的意識を示すこと。真剣で集中しているという肯定的な意味にも、重い・圧が強い・感情的に負担が大きいという否定的な評価にもなり得る。  "
      }
    ],
    "frequency_register": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 47,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 49,
        "text": "【レジスター/領域】標準的な一般語。会話、ニュース、ビジネス、医学、スポーツ、文学などで広く使う。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 158,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 160,
        "text": "【レジスター/領域】標準的な一般語。仕事、学習、スポーツ、政治、ニュースなどで広く使う。  "
      },
      {
        "line": 258,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 262,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 264,
        "text": "【レジスター/領域】標準的な一般語。人物描写、会話、職場、文学、映画・演劇の批評などで使う。  "
      }
    ],
    "usage_notes": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 85,
        "text": "【語法・注意】intense は程度の高さを表す形容詞で、対象が大きいことや量が多いことを表す語ではない。たとえば「雨が大量に降る」は heavy rain、「色が鮮やかで強い」は intense color のように、対象に応じて自然な語を選ぶ。intense pain/heat/interest のように、身体感覚・環境・感情のいずれにも使えるが、強さの対象を文脈から明確にする。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 196,
        "text": "【語法・注意】intense と intensive は、どちらも短期間に多くの活動や努力が集中する対象を修飾できる。intense は参加者が感じる厳しさ・圧・感情的な強さを含みやすく、intensive は計画や内容の密度を客観的に述べやすい。したがって intense training は訓練の負荷の大きさ、an intensive training course は短期間に内容を詰め込む制度・課程の性質に焦点がある。ただし、この区別は絶対的ではない。  "
      },
      {
        "line": 258,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 300,
        "text": "【語法・注意】人に intense を使う場合は、単に serious「真面目な」や focused「集中した」と同じではない。強い感情や意見が外に表れ、相手に強い存在感・圧力を感じさせる含みがある。褒め言葉として passionate「情熱的な」に近くなることもあれば、too intense のように「重い、付き合うのが大変」という評価になることもある。an intense look は必ず怒りを意味せず、強い集中や関心だけでも成立する。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 43,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 53,
        "text": "【コロケーション】"
      },
      {
        "line": 55,
        "text": "・intense pain  "
      },
      {
        "line": 56,
        "text": "用途: 身体的な痛みが非常に強いことを表す。  "
      },
      {
        "line": 57,
        "text": "例: He felt intense pain in his lower back.  "
      },
      {
        "line": 58,
        "text": "訳: 彼は腰の下部に激しい痛みを感じた。  "
      },
      {
        "line": 60,
        "text": "・intense heat  "
      },
      {
        "line": 61,
        "text": "用途: 暑さや熱が極端に強いことを表す。  "
      },
      {
        "line": 62,
        "text": "例: The intense heat made it dangerous to work outside.  "
      },
      {
        "line": 63,
        "text": "訳: 強烈な暑さのため、屋外で働くのは危険だった。  "
      },
      {
        "line": 65,
        "text": "・intense pressure  "
      },
      {
        "line": 66,
        "text": "用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  "
      },
      {
        "line": 67,
        "text": "例: The new manager is under intense pressure to improve the results.  "
      },
      {
        "line": 68,
        "text": "訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  "
      },
      {
        "line": 70,
        "text": "・intense interest  "
      },
      {
        "line": 71,
        "text": "用途: ある対象に向けられる関心が非常に強いことを表す。  "
      },
      {
        "line": 72,
        "text": "例: The discovery attracted intense interest from researchers around the world.  "
      },
      {
        "line": 73,
        "text": "訳: その発見は世界中の研究者から強い関心を集めた。  "
      },
      {
        "line": 75,
        "text": "・intense anger  "
      },
      {
        "line": 76,
        "text": "用途: 怒りの感情が非常に強いことを表す。  "
      },
      {
        "line": 77,
        "text": "例: The decision provoked intense anger among local residents.  "
      },
      {
        "line": 78,
        "text": "訳: その決定は地元住民の激しい怒りを引き起こした。  "
      },
      {
        "line": 80,
        "text": "・intense blue  "
      },
      {
        "line": 81,
        "text": "用途: 色が非常に鮮やかで、見る人に強い印象を与えることを表す。  "
      },
      {
        "line": 82,
        "text": "例: The intense blue of the lake stood out against the white snow.  "
      },
      {
        "line": 83,
        "text": "訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定／叙述】激しい、集中的な"
      },
      {
        "line": 164,
        "text": "【コロケーション】"
      },
      {
        "line": 166,
        "text": "・intense competition  "
      },
      {
        "line": 167,
        "text": "用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。  "
      },
      {
        "line": 168,
        "text": "例: There is intense competition for places at the top universities.  "
      },
      {
        "line": 169,
        "text": "訳: 一流大学の枠をめぐって激しい競争がある。  "
      },
      {
        "line": 171,
        "text": "・intense debate  "
      },
      {
        "line": 172,
        "text": "用途: 議論が強い意見の対立や集中したやり取りを伴うことを表す。  "
      },
      {
        "line": 173,
        "text": "例: The proposal led to intense debate in parliament.  "
      },
      {
        "line": 174,
        "text": "訳: その提案は議会で激しい議論を引き起こした。  "
      },
      {
        "line": 176,
        "text": "・intense activity  "
      },
      {
        "line": 177,
        "text": "用途: 短期間に多くの活動が集中して行われることを表す。  "
      },
      {
        "line": 178,
        "text": "例: The airport experienced a period of intense activity before the holiday.  "
      },
      {
        "line": 179,
        "text": "訳: その空港では休暇前に活動が集中する時期があった。  "
      },
      {
        "line": 181,
        "text": "・intense effort  "
      },
      {
        "line": 182,
        "text": "用途: 目標達成のために大きな力と集中を注ぐ努力を表す。  "
      },
      {
        "line": 183,
        "text": "例: The rescue required intense effort from everyone on the team.  "
      },
      {
        "line": 184,
        "text": "訳: その救助にはチーム全員の大変な努力が必要だった。  "
      },
      {
        "line": 186,
        "text": "・intense negotiations  "
      },
      {
        "line": 187,
        "text": "用途: 短期間に意見を激しく交わし、妥結を目指す交渉を表す。  "
      },
      {
        "line": 188,
        "text": "例: The two sides held intense negotiations throughout the night.  "
      },
      {
        "line": 189,
        "text": "訳: 両陣営は一晩中、激しい交渉を続けた。  "
      },
      {
        "line": 191,
        "text": "・intense training  "
      },
      {
        "line": 192,
        "text": "用途: 参加者が大きな負荷や集中を感じる厳しい訓練を表す。  "
      },
      {
        "line": 193,
        "text": "例: The athletes completed an intense training camp before the tournament.  "
      },
      {
        "line": 194,
        "text": "訳: 選手たちは大会前に厳しい合宿を終えた。  "
      },
      {
        "line": 258,
        "text": "3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた"
      },
      {
        "line": 268,
        "text": "【コロケーション】"
      },
      {
        "line": 270,
        "text": "・an intense look  "
      },
      {
        "line": 271,
        "text": "用途: 強い感情や集中を帯びた視線・表情を表す。  "
      },
      {
        "line": 272,
        "text": "例: She gave him an intense look when he mentioned the accusation.  "
      },
      {
        "line": 273,
        "text": "訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  "
      },
      {
        "line": 275,
        "text": "・an intense person  "
      },
      {
        "line": 276,
        "text": "用途: 感情、意見、目的意識などが強く、存在感や圧のある人を表す。  "
      },
      {
        "line": 277,
        "text": "例: He is an intense person who takes every project very seriously.  "
      },
      {
        "line": 278,
        "text": "訳: 彼はどのプロジェクトにも非常に真剣に取り組む、熱の強い人だ。  "
      },
      {
        "line": 280,
        "text": "・be intense about 〈事柄〉  "
      },
      {
        "line": 281,
        "text": "用途: ある事柄について強い意見や熱意を持ち、真剣にこだわることを表す。  "
      },
      {
        "line": 282,
        "text": "例: She is intense about keeping every detail of the experiment accurate.  "
      },
      {
        "line": 283,
        "text": "訳: 彼女は実験の細部をすべて正確に保つことに非常にこだわっている。  "
      },
      {
        "line": 285,
        "text": "・an intense conversation  "
      },
      {
        "line": 286,
        "text": "用途: 強い感情や重大な問題を伴う真剣な会話を表す。  "
      },
      {
        "line": 287,
        "text": "例: We had an intense conversation about whether to end the relationship.  "
      },
      {
        "line": 288,
        "text": "訳: 私たちはその関係を終わらせるべきかについて、感情のこもった真剣な話をした。  "
      },
      {
        "line": 290,
        "text": "・an intense relationship  "
      },
      {
        "line": 291,
        "text": "用途: 感情的な結びつきや相互作用が非常に強い関係を表す。  "
      },
      {
        "line": 292,
        "text": "例: Their intense relationship left little room for emotional distance.  "
      },
      {
        "line": 293,
        "text": "訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  "
      },
      {
        "line": 295,
        "text": "・too intense  "
      },
      {
        "line": 296,
        "text": "用途: 人、会話、関係などが重すぎたり、圧が強すぎたりすることを表す。  "
      },
      {
        "line": 297,
        "text": "例: The first meeting felt too intense for a casual introduction.  "
      },
      {
        "line": 298,
        "text": "訳: 最初の会合は、気軽な顔合わせにしては重すぎる感じがした。  "
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
