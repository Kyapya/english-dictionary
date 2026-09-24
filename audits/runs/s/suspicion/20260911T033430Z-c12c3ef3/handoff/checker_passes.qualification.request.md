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
  "input_body_sha256": "82f343438dd0057f0cc4edd16ece26ba75380521e8c02dfb806b6da7eb43d3f8",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "suspicion は中英語・アングロフランス語／古フランス語を経て、ラテン語 suspīciō / suspectionem「疑い、不信」にさかのぼる。さらに suspicere「ひそかに見る、疑って見る、疑う」と関係し、sub-「下から・ひそかに」と specere「見る」に結び付く語族である。現代語の意味では、目の前の証拠だけでは確定できないものを「何かあるのではないか」と見る感覚が中心に残っている。suspect、suspicious も同じ語族に属する。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・suspect：動詞では「～ではないかと疑う、〈人〉を犯人・不正の当事者ではないかと疑う」、名詞では「容疑者」、形容詞では「疑わしい、怪しい」。suspicion はその「疑い・疑念」を名詞として表す。  "
      },
      {
        "line": 24,
        "text": "・suspicious：形容詞。「疑っている、怪しいと思っている」または「疑わしい、怪しい」。人の心理と、対象の性質の両方を表せる。  "
      },
      {
        "line": 25,
        "text": "・suspiciously：副詞。「疑わしそうに、怪しいほど」。行動の見え方にも、程度が不自然に高いことにも使う。  "
      },
      {
        "line": 26,
        "text": "・suspiciousness：名詞。「疑い深さ、疑わしさ」。語としては成立するが、一般には suspicion の方がはるかに広く用いられる。  "
      }
    ],
    "sense_structure": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 40,
        "text": "【日本語訳・定義】人が犯罪、不正、不誠実な行為などをした可能性があると、十分な証明がない段階で考えること、またはその疑いを向けられている状態を表す。個々の疑いを数えるときは可算、疑いという状態・雰囲気をまとめて述べるときは不可算で使われる。  "
      },
      {
        "line": 105,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 107,
        "text": "【日本語訳・定義】人、組織、動機、考えなどをそのまま信用せず、「裏に何か問題・意図があるかもしれない」と疑って見る態度を表す。語義1のように特定の犯罪・不正行為を想定する必要はなく、広い意味での mistrust / distrust に近い。  "
      },
      {
        "line": 176,
        "text": "3. 【名詞・可算】～ではないかという気、確証のない推測"
      },
      {
        "line": 178,
        "text": "【日本語訳・定義】ある事実・状況が本当なのではないかと感じることを表す。ここでは犯罪・不正や相手への不信に限らず、証明はないが「たぶんそうだ」という予感・推測を指す。通常は個々の考えとして可算で、a suspicion that ... の形が非常に重要である。  "
      },
      {
        "line": 243,
        "text": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配"
      },
      {
        "line": 245,
        "text": "【日本語訳・定義】色、味、匂い、感情、表情などが、はっきり大量に存在するのではなく「あるかないか分かる程度」にわずかに感じられることを表す。通常 a suspicion of ... の形で用いられる比喩的な用法である。  "
      }
    ],
    "frequency_register": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 42,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 44,
        "text": "【レジスター/領域】標準語。日常会話、報道、警察・司法関連の記事で広く使う。on suspicion of ...、under suspicion は報道や法執行の文脈で特に多い。ここでいう suspicion は有罪が立証されたことを意味しない。頻度の数値はこの辞書内の学習上の相対目安である。  "
      },
      {
        "line": 105,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 109,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 111,
        "text": "【レジスター/領域】標準語。会話、報道、政治・社会・ビジネスなど広い領域で使う。with suspicion、suspicion of ...、deep/widespread suspicion が典型的。  "
      },
      {
        "line": 176,
        "text": "3. 【名詞・可算】～ではないかという気、確証のない推測"
      },
      {
        "line": 180,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 182,
        "text": "【レジスター/領域】標準語。会話・文章ともに普通に使う。a sneaking suspicion、a nagging suspicion などは、はっきり言い切れないが消えない予感を表す定番表現。  "
      },
      {
        "line": 243,
        "text": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配"
      },
      {
        "line": 247,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 249,
        "text": "【レジスター/領域】やや文語的・描写的。小説、食・色・香りの描写などで見られる。日常会話では a hint of ...、a touch of ...、a trace of ... の方が分かりやすく一般的なことが多い。  "
      }
    ],
    "usage_notes": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 80,
        "text": "【語法・注意】on suspicion of theft は「窃盗で有罪になった」ではなく、「窃盗をした疑いを理由に」という意味である。under suspicion も罪が確定した状態を表さない。suspicion of fraud では of の後ろに「疑われている行為・犯罪」が来る一方、suspicion of strangers のような形は文脈によって「見知らぬ人への不信」を表し、語義2に近くなる。accusation や allegation は疑いそのものよりも、誰かが不正をしたという主張を明示的に表に出す点で強い。  "
      },
      {
        "line": 105,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 142,
        "text": "【語法・注意】with suspicion は「疑い深く、信用せずに」という態度を表す。suspicion of fraud の of は通常「詐欺が起きたという疑い」だが、suspicion of outsiders では「よそ者への不信」という対象関係になりやすいので、of を機械的に一つの意味で解釈しない。distrust / mistrust は「信用していない状態」をより直接的に表し、suspicion はしばしば「何か良くない理由・意図があるのではないか」という推測を伴う。skepticism は主張・考えを真だと受け入れることへの慎重さに焦点があり、人の悪意を必ずしも想定しない。  "
      },
      {
        "line": 176,
        "text": "3. 【名詞・可算】～ではないかという気、確証のない推測"
      },
      {
        "line": 218,
        "text": "【語法・注意】この語義では内容が必ず悪いとは限らない。I have a suspicion that she may surprise us with good news. のように、中立・肯定的な内容についても「そうではないかという気」を表せる。ただし語そのものには doubt や hunch より「裏に何かあるのでは」というニュアンスが残りやすい。suspicion that ... の that は内容を導く接続詞で、suspicion of ... の of は名詞句を取る。a sneaking suspicion の sneaking はここでは「盗み歩く」という直訳ではなく、表立って確信してはいないが心の中にある感覚を表す。  "
      },
      {
        "line": 243,
        "text": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配"
      },
      {
        "line": 275,
        "text": "【語法・注意】この a suspicion of ... は「～を疑うこと」ではなく、「～がほんの少し存在すること」である。文体的な比喩なので、意味を誤解されそうな場面では a hint of、a touch of、a trace of が無難である。一部の辞書には suspicion を動詞「疑う」として扱う非標準・方言的な用法も載るが、現代の標準英語では通常 suspect を使うため、本記事では主要語義として立てない。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 48,
        "text": "【コロケーション】"
      },
      {
        "line": 50,
        "text": "・arouse suspicion  "
      },
      {
        "line": 51,
        "text": "用途: 行動・説明・状況が「何かおかしい」という疑いを生じさせる。  "
      },
      {
        "line": 52,
        "text": "例: The unexplained transfer of funds aroused suspicion among the auditors.  "
      },
      {
        "line": 53,
        "text": "訳: 説明のつかない資金移動が監査担当者たちの疑いを招いた。  "
      },
      {
        "line": 55,
        "text": "・on suspicion of 〈crime〉  "
      },
      {
        "line": 56,
        "text": "用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕・拘束したことを述べる。  "
      },
      {
        "line": 57,
        "text": "例: Two people were arrested on suspicion of fraud after the investigation.  "
      },
      {
        "line": 58,
        "text": "訳: 捜査後、2人が詐欺の容疑で逮捕された。  "
      },
      {
        "line": 60,
        "text": "・be under suspicion  "
      },
      {
        "line": 61,
        "text": "用途: 人・組織などが不正や犯罪をしたのではないかと疑われている状態を表す。  "
      },
      {
        "line": 62,
        "text": "例: The contractor remained under suspicion until the records were checked.  "
      },
      {
        "line": 63,
        "text": "訳: 記録が確認されるまで、その請負業者には疑いがかけられたままだった。  "
      },
      {
        "line": 65,
        "text": "・come/fall under suspicion  "
      },
      {
        "line": 66,
        "text": "用途: 新しい情報などをきっかけに、疑いの対象になることを表す。  "
      },
      {
        "line": 67,
        "text": "例: The employee came under suspicion when several invoices disappeared.  "
      },
      {
        "line": 68,
        "text": "訳: 複数の請求書がなくなったことで、その従業員が疑われるようになった。  "
      },
      {
        "line": 70,
        "text": "・cast suspicion on 〈person/action〉  "
      },
      {
        "line": 71,
        "text": "用途: 証拠や発言などが、特定の人・行為に疑いを向けることを表す。  "
      },
      {
        "line": 72,
        "text": "例: The altered timestamp cast suspicion on the authenticity of the document.  "
      },
      {
        "line": 73,
        "text": "訳: 変更された時刻表示によって、その文書の真正性に疑いが向けられた。  "
      },
      {
        "line": 75,
        "text": "・confirm/dispel suspicions  "
      },
      {
        "line": 76,
        "text": "用途: それまで抱いていた疑いが裏付けられる／解消されることを表す。  "
      },
      {
        "line": 77,
        "text": "例: The security footage confirmed the manager's suspicions.  "
      },
      {
        "line": 78,
        "text": "訳: 防犯映像によって、管理者が抱いていた疑いが裏付けられた。  "
      },
      {
        "line": 105,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 115,
        "text": "【コロケーション】"
      },
      {
        "line": 117,
        "text": "・regard/view 〈person/claim〉 with suspicion  "
      },
      {
        "line": 118,
        "text": "用途: 人や主張をすぐには信用せず、疑いの目で見ることを表す。  "
      },
      {
        "line": 119,
        "text": "例: Residents viewed the sudden policy change with suspicion.  "
      },
      {
        "line": 120,
        "text": "訳: 住民たちは突然の方針変更を疑いの目で見た。  "
      },
      {
        "line": 122,
        "text": "・be met with suspicion  "
      },
      {
        "line": 123,
        "text": "用途: 提案・説明・新制度などが、周囲から信用されずに受け止められる。  "
      },
      {
        "line": 124,
        "text": "例: The new monitoring system was initially met with suspicion by employees.  "
      },
      {
        "line": 125,
        "text": "訳: 新しい監視システムは当初、従業員から疑いをもって受け止められた。  "
      },
      {
        "line": 127,
        "text": "・suspicion of 〈person/group〉  "
      },
      {
        "line": 128,
        "text": "用途: 特定の人・集団に対して根強い不信感を持つことを表す。  "
      },
      {
        "line": 129,
        "text": "例: Years of secrecy created a lasting suspicion of the agency.  "
      },
      {
        "line": 130,
        "text": "訳: 長年の秘密主義によって、その機関に対する根強い不信が生まれた。  "
      },
      {
        "line": 132,
        "text": "・deep suspicion  "
      },
      {
        "line": 133,
        "text": "用途: 単なる軽い疑問ではなく、強い不信感を表す。  "
      },
      {
        "line": 134,
        "text": "例: The unexplained changes led to deep suspicion among investors.  "
      },
      {
        "line": 135,
        "text": "訳: 説明のない変更によって、投資家の間に強い不信が生じた。  "
      },
      {
        "line": 137,
        "text": "・widespread suspicion  "
      },
      {
        "line": 138,
        "text": "用途: 多くの人に不信が共有されていることを表す。  "
      },
      {
        "line": 139,
        "text": "例: The lack of transparency caused widespread suspicion about the process.  "
      },
      {
        "line": 140,
        "text": "訳: 透明性の欠如によって、その手続きに対する不信が広く生じた。  "
      },
      {
        "line": 176,
        "text": "3. 【名詞・可算】～ではないかという気、確証のない推測"
      },
      {
        "line": 186,
        "text": "【コロケーション】"
      },
      {
        "line": 188,
        "text": "・have a suspicion that 〈clause〉  "
      },
      {
        "line": 189,
        "text": "用途: 十分な証拠はないが、あることが本当ではないかと感じていることを表す。  "
      },
      {
        "line": 190,
        "text": "例: I have a suspicion that the meeting will finish earlier than planned.  "
      },
      {
        "line": 191,
        "text": "訳: その会議は予定より早く終わるのではないかという気がしている。  "
      },
      {
        "line": 193,
        "text": "・a sneaking suspicion that 〈clause〉  "
      },
      {
        "line": 194,
        "text": "用途: はっきり認めるほどではないが、心のどこかでそう思っていることを表す。  "
      },
      {
        "line": 195,
        "text": "例: She had a sneaking suspicion that everyone already knew the answer.  "
      },
      {
        "line": 196,
        "text": "訳: 彼女は、皆すでに答えを知っているのではないかとひそかに感じていた。  "
      },
      {
        "line": 198,
        "text": "・a nagging suspicion that 〈clause〉  "
      },
      {
        "line": 199,
        "text": "用途: 消そうとしても繰り返し気になる疑い・予感を表す。  "
      },
      {
        "line": 200,
        "text": "例: He could not shake the nagging suspicion that he had forgotten something important.  "
      },
      {
        "line": 201,
        "text": "訳: 彼は何か大事なことを忘れたのではないかという消えない疑いを振り払えなかった。  "
      },
      {
        "line": 203,
        "text": "・a growing suspicion that 〈clause〉  "
      },
      {
        "line": 204,
        "text": "用途: 時間の経過や新しい情報によって、ある推測が強くなっていくことを表す。  "
      },
      {
        "line": 205,
        "text": "例: We had a growing suspicion that the delay was caused by a technical problem.  "
      },
      {
        "line": 206,
        "text": "訳: その遅延は技術的な問題によるのではないかという疑いが、私たちの中で強まっていった。  "
      },
      {
        "line": 208,
        "text": "・confirm a suspicion  "
      },
      {
        "line": 209,
        "text": "用途: それまで確証のなかった推測が、後の情報によって正しかったと分かる。  "
      },
      {
        "line": 210,
        "text": "例: The test results confirmed her suspicion that the battery was failing.  "
      },
      {
        "line": 211,
        "text": "訳: 検査結果によって、バッテリーが劣化しているのではないかという彼女の推測が裏付けられた。  "
      },
      {
        "line": 213,
        "text": "・dispel a suspicion  "
      },
      {
        "line": 214,
        "text": "用途: 情報や証拠によって、抱いていた推測・疑いを取り除く。  "
      },
      {
        "line": 215,
        "text": "例: A detailed explanation dispelled our suspicion that the figures had been altered.  "
      },
      {
        "line": 216,
        "text": "訳: 詳しい説明によって、数値が改変されたのではないかという私たちの疑いは解消された。  "
      },
      {
        "line": 243,
        "text": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配"
      },
      {
        "line": 253,
        "text": "【コロケーション】"
      },
      {
        "line": 255,
        "text": "・a suspicion of 〈color〉  "
      },
      {
        "line": 256,
        "text": "用途: 色合いがごくわずかに混じって見えることを描写する。  "
      },
      {
        "line": 257,
        "text": "例: The walls were white with a suspicion of blue in the evening light.  "
      },
      {
        "line": 258,
        "text": "訳: その壁は白かったが、夕方の光の中ではほんのり青みを帯びていた。  "
      },
      {
        "line": 260,
        "text": "・a suspicion of 〈flavor〉  "
      },
      {
        "line": 261,
        "text": "用途: 味や香りがごく弱く感じられることを表す。  "
      },
      {
        "line": 262,
        "text": "例: The sauce had a suspicion of citrus that made it taste fresher.  "
      },
      {
        "line": 263,
        "text": "訳: そのソースにはほんのり柑橘の風味があり、より爽やかに感じられた。  "
      },
      {
        "line": 265,
        "text": "・a suspicion of 〈emotion〉  "
      },
      {
        "line": 266,
        "text": "用途: 感情が表情・声などにわずかに現れていることを描写する。  "
      },
      {
        "line": 267,
        "text": "例: There was a suspicion of disappointment in his voice.  "
      },
      {
        "line": 268,
        "text": "訳: 彼の声にはかすかな失望がにじんでいた。  "
      },
      {
        "line": 270,
        "text": "・with a suspicion of a smile  "
      },
      {
        "line": 271,
        "text": "用途: はっきり笑うほどではない、わずかな笑みを描写する。  "
      },
      {
        "line": 272,
        "text": "例: She answered with a suspicion of a smile.  "
      },
      {
        "line": 273,
        "text": "訳: 彼女はほんのかすかな笑みを浮かべて答えた。  "
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
  "source_artifact_sha256": "358a6ef905363f010a31dece02f1dd57e94ea0fad57f759488d3898360d8fc54",
  "normalized_input_sha256": "debe55cf7df5d112cb545a87a0a928e6bd5335c40b5957347aedc933345e6b92"
}
```
