# Independent checker handoff

Stage: `checker_passes/translation`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.translation.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_translation_v6

## 目的

英文・訳文・定義における意味の保存と方向を検査する。自然な意訳は認めるが、見出し語の構文差・含意・作用関係を誤学習させる変化は認めない。

## 担当タクソノミー分類

- `example_translation_alignment`
- `semantic_direction_reversal`

## 検査ルール

- 各例文と訳について、述語、主語・目的語・補語、行為者・経験者・対象・結果の意味役割を対応させる。
- 肯定・否定、比較基準、程度、数量、時制、相、法、条件、因果、目的を保存する。
- 修飾範囲、焦点、対比、情報構造、明示内容と文脈推論の境界、レジスターと話者評価を保存する。
- コロケーションのpattern・用途・英文・訳が同じ語義、品詞、完全フレームを表すか確認する。英文が別語義でも成立するだけでは合格にしない。
- 作用する側／される側、上位／下位、原因／結果、全体／部分、評価主体／評価対象を逆転させない。
- 日本語訳が自然でも、英文にない必然性・意図・結果・専門的効果を追加していればfindingとする。
- 同じ例文を異なる構文や語義の証明に使い回していないか確認する。
- 問題が1箇所に見える場合も、同じ訳語・関係が入力section内の別箇所で再発していないか確認する。

## 入力として受け取るセクション

- `definitions`
- `collocations_examples`
- `lexical_relations`

front matter、生成過程、通常チェックの過去判断、ACTIVE.mdは受け取らない。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "example_translation_alignment | semantic_direction_reversal",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "何がどの方向・範囲・強さで不一致か",
  "evidence_link_ids": [],
  "suggested_direction": "意味を変えずに直す方向"
}
```

`taxonomy_id`、位置、severity、根拠を必須とする。事実・語法・例文/訳の正誤に関わるものは `blocking`、事実関係を変えない局所的な日本語調整だけを `minor` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "translation",
  "taxonomy_ids": [
    "example_translation_alignment",
    "semantic_direction_reversal"
  ],
  "specification": "prompts/check_pass_translation_v6.md",
  "input_body_sha256": "82f343438dd0057f0cc4edd16ece26ba75380521e8c02dfb806b6da7eb43d3f8",
  "input_sections": {
    "definitions": [
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
    ],
    "lexical_relations": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 82,
        "text": "【類義語】"
      },
      {
        "line": 84,
        "text": "・accusation  "
      },
      {
        "line": 85,
        "text": "定義: ある人が悪事・犯罪をしたという非難・告発。  "
      },
      {
        "line": 86,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 87,
        "text": "違い: accusation は人に対する明示的な主張で、suspicion は証明前の内的な疑い・推測でも成立する。  "
      },
      {
        "line": 88,
        "text": "例: The accusation was denied by everyone involved.  "
      },
      {
        "line": 89,
        "text": "訳: その告発は関係者全員によって否定された。  "
      },
      {
        "line": 91,
        "text": "・allegation  "
      },
      {
        "line": 92,
        "text": "定義: 証明されていない段階で公に述べられた不正・違法行為についての主張。  "
      },
      {
        "line": 93,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 94,
        "text": "違い: allegation は「主張として提示された内容」に焦点があり、suspicion は発言されていない疑いにも使える。  "
      },
      {
        "line": 95,
        "text": "例: The company is investigating the allegation of misconduct.  "
      },
      {
        "line": 96,
        "text": "訳: その会社は不正行為についての申し立てを調査している。  "
      },
      {
        "line": 98,
        "text": "・doubt  "
      },
      {
        "line": 99,
        "text": "定義: あることが真実・正当・確実かどうかについての不確かさ。  "
      },
      {
        "line": 100,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 101,
        "text": "違い: doubt は真偽一般への不確かさで、犯罪・不正を疑うとは限らない。suspicion は「何か隠れた問題があるのではないか」という方向を持ちやすい。  "
      },
      {
        "line": 102,
        "text": "例: There is some doubt about whether the figures are complete.  "
      },
      {
        "line": 103,
        "text": "訳: その数値が完全かどうかには多少の疑問がある。  "
      },
      {
        "line": 105,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 144,
        "text": "【類義語】"
      },
      {
        "line": 146,
        "text": "・distrust  "
      },
      {
        "line": 147,
        "text": "定義: 人・組織・情報などを信用できないという感覚。  "
      },
      {
        "line": 148,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 149,
        "text": "違い: distrust は信用の欠如そのものを直接表し、suspicion はその背後に隠れた問題・意図があるのではないかという推測を帯びやすい。  "
      },
      {
        "line": 150,
        "text": "例: Public distrust increased after the data leak.  "
      },
      {
        "line": 151,
        "text": "訳: データ流出後、世間の不信が強まった。  "
      },
      {
        "line": 153,
        "text": "・mistrust  "
      },
      {
        "line": 154,
        "text": "定義: 人・物事を十分には信頼しないこと。  "
      },
      {
        "line": 155,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 156,
        "text": "違い: mistrust は distrust に近い一般的な不信。suspicion はより「何か怪しい」という感覚を含みやすい。  "
      },
      {
        "line": 157,
        "text": "例: There was longstanding mistrust between the two groups.  "
      },
      {
        "line": 158,
        "text": "訳: その二つの集団の間には長年の不信があった。  "
      },
      {
        "line": 160,
        "text": "・skepticism  "
      },
      {
        "line": 161,
        "text": "定義: 主張・計画・考えをすぐには真実・有効だと認めない態度。  "
      },
      {
        "line": 162,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 163,
        "text": "違い: skepticism は証拠を求める知的・批判的な態度にも使え、悪意や不正を疑うとは限らない。suspicion は相手の動機や隠れた問題への警戒を帯びやすい。  "
      },
      {
        "line": 164,
        "text": "例: The proposal was greeted with skepticism by several experts.  "
      },
      {
        "line": 165,
        "text": "訳: その提案は複数の専門家から懐疑的に受け止められた。  "
      },
      {
        "line": 167,
        "text": "【反意語】"
      },
      {
        "line": 169,
        "text": "・trust  "
      },
      {
        "line": 170,
        "text": "定義: 人・組織・情報などを信頼し、頼ってよいと考えること。  "
      },
      {
        "line": 171,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 172,
        "text": "違い: 語義2の suspicion が「信用せず警戒する態度」を表すのに対し、trust は相手を信用する側の軸にある。  "
      },
      {
        "line": 173,
        "text": "例: Mutual trust is essential for the partnership.  "
      },
      {
        "line": 174,
        "text": "訳: 相互の信頼はその協力関係に不可欠だ。  "
      },
      {
        "line": 176,
        "text": "3. 【名詞・可算】～ではないかという気、確証のない推測"
      },
      {
        "line": 220,
        "text": "【類義語】"
      },
      {
        "line": 222,
        "text": "・hunch  "
      },
      {
        "line": 223,
        "text": "定義: 明確な根拠なしに直感的にそうだと思うこと。  "
      },
      {
        "line": 224,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 225,
        "text": "違い: hunch は口語的で直感性が強い。suspicion は手掛かりや違和感から「そうではないか」と考える感じを持ちやすい。  "
      },
      {
        "line": 226,
        "text": "例: I had a hunch that the train would be late.  "
      },
      {
        "line": 227,
        "text": "訳: その列車は遅れる気がしていた。  "
      },
      {
        "line": 229,
        "text": "・inkling  "
      },
      {
        "line": 230,
        "text": "定義: あることについてのごくわずかな知識・予感。  "
      },
      {
        "line": 231,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 232,
        "text": "違い: inkling は「少しだけ分かっている／気づいている」という弱さに焦点があり、suspicion はより具体的な仮説を持つことが多い。  "
      },
      {
        "line": 233,
        "text": "例: She had no inkling of what was about to happen.  "
      },
      {
        "line": 234,
        "text": "訳: 彼女はこれから何が起こるのか少しも察していなかった。  "
      },
      {
        "line": 236,
        "text": "・feeling  "
      },
      {
        "line": 237,
        "text": "定義: 論理的な根拠より感覚に基づく考え・予感。  "
      },
      {
        "line": 238,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 239,
        "text": "違い: feeling は非常に広い一般語。suspicion は「まだ確証はないが、裏にその事実があるのでは」と疑う方向がより明確である。  "
      },
      {
        "line": 240,
        "text": "例: I have a feeling that this plan will work.  "
      },
      {
        "line": 241,
        "text": "訳: この計画はうまくいく気がする。  "
      },
      {
        "line": 243,
        "text": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配"
      },
      {
        "line": 277,
        "text": "【類義語】"
      },
      {
        "line": 279,
        "text": "・hint  "
      },
      {
        "line": 280,
        "text": "定義: 色・味・感情などのかすかな兆し・少量。  "
      },
      {
        "line": 281,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 282,
        "text": "違い: hint はこの「少量」の意味で一般的。suspicion はより描写的・文語的で、あえて「感じ取れる程度」という含みを出す。  "
      },
      {
        "line": 283,
        "text": "例: The tea has a hint of mint.  "
      },
      {
        "line": 284,
        "text": "訳: そのお茶にはほのかなミントの風味がある。  "
      },
      {
        "line": 286,
        "text": "・trace  "
      },
      {
        "line": 287,
        "text": "定義: かろうじて認められるごく少量・痕跡。  "
      },
      {
        "line": 288,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 289,
        "text": "違い: trace は量の少なさや痕跡性を直接表す。suspicion は比喩的で、感覚的な描写に使われやすい。  "
      },
      {
        "line": 290,
        "text": "例: There was only a trace of smoke in the air.  "
      },
      {
        "line": 291,
        "text": "訳: 空気中には煙がほんのわずかに残っているだけだった。  "
      },
      {
        "line": 293,
        "text": "・touch  "
      },
      {
        "line": 294,
        "text": "定義: 色・味・感情などを少し加えるもの、ほんの少しの程度。  "
      },
      {
        "line": 295,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 296,
        "text": "違い: touch は会話・描写で自然に使える。suspicion はより控えめで文学的な響きがある。  "
      },
      {
        "line": 297,
        "text": "例: Add a touch of lemon before serving.  "
      },
      {
        "line": 298,
        "text": "訳: 出す前にレモンをほんの少し加えてください。  "
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
  "specification_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
  "source_artifact_sha256": "358a6ef905363f010a31dece02f1dd57e94ea0fad57f759488d3898360d8fc54",
  "normalized_input_sha256": "c9eab2a4d932e8f24f66758e4828b4aacca33136fc57a1ab0c209e9f347d6586"
}
```
