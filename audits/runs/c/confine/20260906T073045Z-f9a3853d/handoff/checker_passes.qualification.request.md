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
  "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "動詞は中期フランス語 confiner「境を接する、限界内にとどめる」から英語に入り、さらにラテン語 confinis「境を接する」にさかのぼる。con-「共に」と finis「境界、終わり」が結び付いた語で、「境界の内側に置く」という意味の核が、現代の「範囲を限る」「閉じ込める」につながった。名詞はフランス語の複数形 confins「境界」などを経て英語に入った。finite「有限の」、final「最後の」もラテン語 finis と関係する。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・confinement（名詞）— 閉じ込めること、拘禁、行動範囲が限られた状態。文脈によって物理的拘束、病気による外出不能、限定された環境などを表す。  "
      },
      {
        "line": 24,
        "text": "・confined（形容詞）— 狭く囲まれた、限られた。単なる過去分詞としての受動用法と、confined space のような形容詞用法がある。  "
      },
      {
        "line": 25,
        "text": "・confining（形容詞）— 自由な動きや活動を妨げる、窮屈な。物理的な狭さだけでなく、服装・役割・生活環境などの制約にも使う。  "
      },
      {
        "line": 26,
        "text": "・unconfined（形容詞）— 閉じ込められていない、境界内に制限されていない。一般語としては limited や restricted ほど頻繁ではない。  "
      }
    ],
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
    "frequency_register": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
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
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
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
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 195,
        "text": "【頻度】〈6/10〉  "
      },
      {
        "line": 197,
        "text": "【レジスター/領域】一般語・医療関連。病状や回復期間を述べるやや硬い表現。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
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
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 325,
        "text": "【頻度】〈4/10〉  "
      },
      {
        "line": 327,
        "text": "【レジスター/領域】格式的・文学的。within/beyond/outside the confines of の形で、抽象的・物理的な範囲を述べる文章に使われる。  "
      }
    ],
    "usage_notes": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 77,
        "text": "【語法・注意】基本形は confine A to B であり、to の後ろには名詞または動名詞を置く。×confine A in doing B のように範囲を示す前置詞を機械的に in に替えない。場所の内部へ物理的に閉じ込める語義2では confine someone in a cell のように in も使う。confine oneself to は「自分を物理的に閉じ込める」ではなく、通常「話題・活動を自分で限定する」という再帰構文である。受動形 be confined to は、否定や mainly、largely などと結び付き、「～だけに限られる／限られない」を表しやすい。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 150,
        "text": "【語法・注意】この語義では能動形も可能だが、拘束される側を主語にした be confined in/to が多い。in は容器・部屋・施設の「内部」を、to は移動可能な「範囲」を示す。imprison は人を刑務所に入れる法的・物理的な拘禁に焦点があり、動物や一時的な行動制限には使いにくい。confine は刑罰に限らず、命令や安全上の理由による拘束にも使える。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 223,
        "text": "【語法・注意】be confined to a wheelchair は従来から見られる表現だが、車いすを人を閉じ込める物として否定的に描くため、不快・不適切と受け取られることがある。単に移動手段を述べるなら use a wheelchair または be a wheelchair user を用いる。be confined to bed は病気などで起きられない状態を表し、単にベッドで休む choose to stay in bed とは異なる。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 280,
        "text": "【語法・注意】confined space は一般には狭く囲まれた空間を表すが、労働安全上の専門用語では法域や制度ごとに定義・要件があるため、小さい部屋をすべて専門上の confined space と断定しない。be confined to 〈場所・範囲〉は動詞 confine の受動形で「～に限定・拘束されている」、a confined space は形容詞 confined が名詞を修飾して「狭く囲まれた空間」である。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 353,
        "text": "【語法・注意】名詞では動詞と強勢位置が異なる。現代英語では通常 the confines of ... の複数形で使い、単数の a confine はまれである。confines は「境界線」そのものと「境界に囲まれた領域」の両方を表し得るため、within the confines of the park は通常「公園の区域内」、beyond the confines of the law は比喩的に「法の枠を越えて」と理解する。  "
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
  "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
  "normalized_input_sha256": "082a237a0b4d402c8ba365acd63a8ba9705c425b46b1af12a079ebb20511e5b6"
}
```
