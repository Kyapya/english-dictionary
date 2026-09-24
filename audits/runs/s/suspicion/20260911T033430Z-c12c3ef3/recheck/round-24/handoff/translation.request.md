# Independent checker handoff

Stage: `checker_passes/translation`

Use a fresh independent reviewer session. Do not inspect prior-round findings, outputs from other passes, or the private alignment key. Review only the exact packet below against the cited checker prompt. Preserve any finding decision and return one raw JSON response as the requested response file; do not edit earlier responses.

Save the raw response at `responses/translation.response.raw.json`. Include the exact `pass_id` and a top-level `reviewer` object with `mode: "handoff"`, your actual `declared_model`, `ingested_by: "human"`, and a unique non-empty `agent_id`. Use a different reviewer identity for each of the seven passes.

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


## Exact input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "translation",
  "taxonomy_ids": [
    "example_translation_alignment",
    "semantic_direction_reversal"
  ],
  "specification": "prompts/check_pass_translation_v6.md",
  "input_body_sha256": "18178e0a192307a41e4cccafaaf60c75ff89633d50774904ba389187e4d827b6",
  "input_sections": {
    "definitions": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 40,
        "text": "【日本語訳・定義】人が犯罪、不正、不誠実な行為をしたとして疑いの対象になること、またはその人の行為に不正の容疑を向けることを表す。焦点は、ある命題の真偽を予想すること自体より、特定の人がその行為をしたとして疑われている点にある。that節を伴う例もあるが、節の話題だけで語義を決めず、人への容疑を表す場合は語義1に置く。複数の個別の疑いを述べる suspicions は可算、疑いという状態を表す suspicion は不可算で使われる。on suspicion of ... のように特定の容疑でも無冠詞となる定型表現があるため、可算・不可算は意味だけで一律には決まらない。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 93,
        "text": "【日本語訳・定義】人、組織、動機、考えなどの真実性や信頼性を確信できず、すぐには信用しない態度を表す。相手や情報の裏に問題や意図があるのではないかという警戒を伴うこともある。語義1のように特定の犯罪・不正行為を想定する必要はなく、広い意味での mistrust / distrust に近い。  "
      },
      {
        "line": 131,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 133,
        "text": "【日本語訳・定義】十分な証拠がなくても、ある命題や状況が真かもしれないと考える、話者の暫定的な推測・予感を表す。焦点は命題の真偽にあり、特定の人を犯罪・不正の容疑者として扱うこと自体ではない。that節の話題だけで語義を決めず、節全体についての推測は語義3、特定の人へ行為の容疑を向ける用法は語義1に置く。この用法では個々の考えを表す可算形が典型。可算・不可算は意味だけで一律に決まらず、構文にも左右される。  "
      },
      {
        "line": 181,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 183,
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
        "text": "例: Among the auditors, the unexplained transfer of client funds aroused suspicion that the treasurer had committed fraud.  "
      },
      {
        "line": 53,
        "text": "訳: 監査担当者の間では、顧客資金の使途不明な移動により、会計係が詐欺を行ったのではないかという疑いが生じた。  "
      },
      {
        "line": 55,
        "text": "・on suspicion of 〈crime〉  "
      },
      {
        "line": 56,
        "text": "用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕したことを述べる。  "
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
        "text": "・cast suspicion on 〈person/action suspected of wrongdoing〉  "
      },
      {
        "line": 71,
        "text": "用途: 犯罪・不正をした可能性がある人や行為に疑いを向けることを表す。  "
      },
      {
        "line": 72,
        "text": "例: The altered timestamp cast suspicion on the clerk who had access to the report.  "
      },
      {
        "line": 73,
        "text": "訳: 変更された時刻表示によって、報告書にアクセスできた事務員に疑いが向けられた。  "
      },
      {
        "line": 75,
        "text": "・confirm suspicions  "
      },
      {
        "line": 76,
        "text": "用途: それまで抱いていた疑いが裏付けられることを表す。  "
      },
      {
        "line": 77,
        "text": "例: The security footage confirmed the manager's suspicions that a guard had stolen the missing laptops.  "
      },
      {
        "line": 78,
        "text": "訳: 防犯映像によって、警備員がなくなったノートパソコンを盗んだという管理者の疑いが裏付けられた。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 101,
        "text": "【コロケーション】"
      },
      {
        "line": 103,
        "text": "・regard/view 〈person/claim/proposal/action/decision〉 with suspicion  "
      },
      {
        "line": 104,
        "text": "用途: 人・主張・提案・行為・決定をすぐには信用せず、疑いの目で見ることを表す。  "
      },
      {
        "line": 105,
        "text": "例: Residents viewed the sudden policy change with suspicion.  "
      },
      {
        "line": 106,
        "text": "訳: 住民たちは突然の方針変更を疑いの目で見た。  "
      },
      {
        "line": 108,
        "text": "・be greeted with (some) suspicion  "
      },
      {
        "line": 109,
        "text": "用途: 申し出・提案などが、当初は信用されず、疑いをもって受け止められることを表す。  "
      },
      {
        "line": 110,
        "text": "例: The new monitoring system was initially greeted with some suspicion.  "
      },
      {
        "line": 111,
        "text": "訳: 新しい監視システムは当初、多少の疑いをもって受け止められた。  "
      },
      {
        "line": 131,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 141,
        "text": "【コロケーション】"
      },
      {
        "line": 143,
        "text": "・have a suspicion that 〈clause〉  "
      },
      {
        "line": 144,
        "text": "用途: 十分な証拠はないが、あることが本当ではないかと感じていることを表す。  "
      },
      {
        "line": 145,
        "text": "例: I have a suspicion that the meeting will finish earlier than planned.  "
      },
      {
        "line": 146,
        "text": "訳: その会議は予定より早く終わるのではないかという気がしている。  "
      },
      {
        "line": 148,
        "text": "・a sneaking suspicion that 〈clause〉  "
      },
      {
        "line": 149,
        "text": "用途: はっきり認めるほどではないが、心のどこかでそう思っていることを表す。  "
      },
      {
        "line": 150,
        "text": "例: She had a sneaking suspicion that everyone already knew the answer.  "
      },
      {
        "line": 151,
        "text": "訳: 彼女は、皆すでに答えを知っているのではないかとひそかに感じていた。  "
      },
      {
        "line": 153,
        "text": "・a strong suspicion that 〈clause〉  "
      },
      {
        "line": 154,
        "text": "用途: あることが本当ではないかという強い推測を表す。  "
      },
      {
        "line": 155,
        "text": "例: We had a strong suspicion that the delay was caused by a technical problem.  "
      },
      {
        "line": 156,
        "text": "訳: 私たちは、その遅延は技術的な問題によるのではないかという強い疑いを抱いていた。  "
      },
      {
        "line": 158,
        "text": "・confirm a suspicion  "
      },
      {
        "line": 159,
        "text": "用途: それまで確証のなかった推測が、後の情報によって正しかったと分かる。  "
      },
      {
        "line": 160,
        "text": "例: The test results confirmed her suspicion that the battery was failing.  "
      },
      {
        "line": 161,
        "text": "訳: 検査結果によって、バッテリーが劣化しているのではないかという彼女の推測が裏付けられた。  "
      },
      {
        "line": 181,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 191,
        "text": "【コロケーション】"
      },
      {
        "line": 193,
        "text": "・a suspicion of 〈color〉  "
      },
      {
        "line": 194,
        "text": "用途: 色合いがごくわずかに混じって見えることを描写する。  "
      },
      {
        "line": 195,
        "text": "例: The walls were white with a suspicion of blue in the evening light.  "
      },
      {
        "line": 196,
        "text": "訳: その壁は白かったが、夕方の光の中ではほんのり青みを帯びていた。  "
      },
      {
        "line": 198,
        "text": "・a suspicion of 〈flavor〉  "
      },
      {
        "line": 199,
        "text": "用途: 味や香りがごく弱く感じられることを表す。  "
      },
      {
        "line": 200,
        "text": "例: The sauce had a suspicion of citrus that made it taste fresher.  "
      },
      {
        "line": 201,
        "text": "訳: そのソースにはほんのり柑橘の風味があり、より爽やかに感じられた。  "
      },
      {
        "line": 203,
        "text": "・a suspicion of 〈emotion〉  "
      },
      {
        "line": 204,
        "text": "用途: 感情が表情・声などにわずかに現れていることを描写する。  "
      },
      {
        "line": 205,
        "text": "例: There was a suspicion of disappointment in his voice.  "
      },
      {
        "line": 206,
        "text": "訳: 彼の声にはかすかな失望がにじんでいた。  "
      },
      {
        "line": 208,
        "text": "・a suspicion of a smile  "
      },
      {
        "line": 209,
        "text": "用途: はっきり笑うほどではない、わずかな笑みを描写する。  "
      },
      {
        "line": 210,
        "text": "例: A suspicion of a smile appeared at the corner of her mouth.  "
      },
      {
        "line": 211,
        "text": "訳: 彼女の口元に、かすかな笑みが浮かんだ。  "
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
        "text": "・mistrust  "
      },
      {
        "line": 85,
        "text": "定義: 人の誠実さや動機を信用せず、不正をしている可能性を疑うこと。  "
      },
      {
        "line": 86,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 87,
        "text": "違い: mistrust は相手への信頼の欠如に焦点がある。suspicion は特定の不正の可能性や、疑いを向けられている状態も表せる。  "
      },
      {
        "line": 88,
        "text": "例: The missing receipts deepened the auditors' mistrust of the treasurer.  "
      },
      {
        "line": 89,
        "text": "訳: 領収書が見当たらなかったことで、監査担当者たちの会計係への不信が強まった。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 115,
        "text": "【類義語】"
      },
      {
        "line": 117,
        "text": "・distrust  "
      },
      {
        "line": 118,
        "text": "定義: 人・組織・情報などを信用できないという感覚。  "
      },
      {
        "line": 119,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 120,
        "text": "違い: distrust はこの意味での近い語で、信用できない状態を直接表す。suspicion は、真実性・公正さ・信頼性などへの信頼が薄いことを表す場合がある。  "
      },
      {
        "line": 121,
        "text": "例: Public distrust increased after the data leak.  "
      },
      {
        "line": 122,
        "text": "訳: データ流出後、世間の不信が強まった。  "
      },
      {
        "line": 124,
        "text": "・mistrust  "
      },
      {
        "line": 125,
        "text": "定義: 人・物事を十分には信頼しないこと。  "
      },
      {
        "line": 126,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 127,
        "text": "違い: Merriam-Webster の説明では、mistrust は suspicion に基づく信頼の欠如を強調する。  "
      },
      {
        "line": 128,
        "text": "例: There was longstanding mistrust between the two groups.  "
      },
      {
        "line": 129,
        "text": "訳: その二つの集団の間には長年の不信があった。  "
      },
      {
        "line": 131,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 165,
        "text": "【類義語】"
      },
      {
        "line": 167,
        "text": "・doubt  "
      },
      {
        "line": 168,
        "text": "定義: ある事実が真実かどうか、確信が持てないこと。  "
      },
      {
        "line": 169,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 170,
        "text": "違い: doubt は真偽への不確かさを広く表す。suspicion は「そうではないか」という暫定的な見方や予感に焦点がある。  "
      },
      {
        "line": 171,
        "text": "例: The test results raised doubts about whether the battery was failing.  "
      },
      {
        "line": 172,
        "text": "訳: 検査結果から、バッテリーが劣化しているのかどうか疑問が生じた。  "
      },
      {
        "line": 174,
        "text": "・belief  "
      },
      {
        "line": 175,
        "text": "定義: 十分な証明がなくても、あることが真実だと考えること。  "
      },
      {
        "line": 176,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 177,
        "text": "違い: belief はその考えへの確信を広く表し、疑いや不安を含むとは限らない。suspicion は確証のない見立てであることを前面に出す。  "
      },
      {
        "line": 178,
        "text": "例: The team had a strong belief that the repairs would solve the problem.  "
      },
      {
        "line": 179,
        "text": "訳: チームは修理で問題が解決すると強く考えていた。  "
      },
      {
        "line": 181,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 215,
        "text": "【類義語】"
      },
      {
        "line": 217,
        "text": "・hint  "
      },
      {
        "line": 218,
        "text": "定義: 色・味・感情などのかすかな兆し・少量。  "
      },
      {
        "line": 219,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 220,
        "text": "違い: hint はこの「少量」の意味で一般的。suspicion はやや改まった表現で、あえて「感じ取れる程度」という含みを出す。  "
      },
      {
        "line": 221,
        "text": "例: The tea has a hint of mint.  "
      },
      {
        "line": 222,
        "text": "訳: そのお茶にはほのかなミントの風味がある。  "
      },
      {
        "line": 224,
        "text": "・trace  "
      },
      {
        "line": 225,
        "text": "定義: かろうじて認められるごく少量・痕跡。  "
      },
      {
        "line": 226,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 227,
        "text": "違い: trace は量の少なさや痕跡性を直接表す。suspicion は比喩的で、感覚的な描写に使われやすい。  "
      },
      {
        "line": 228,
        "text": "例: There was only a trace of smoke in the air.  "
      },
      {
        "line": 229,
        "text": "訳: 空気中には煙がごくわずかにあるだけだった。  "
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
  "source_artifact_sha256": "73427b11130b2b4ffb18bbf3504e8054253863023f3237f7a828f43026047262",
  "normalization_version": "check_pass_semantic_input_v2",
  "normalized_input_sha256": "bf524c9e413c39ae59810027eac3129ea4f89cd3178c9344b7f3e30c8a61c72a"
}
```
