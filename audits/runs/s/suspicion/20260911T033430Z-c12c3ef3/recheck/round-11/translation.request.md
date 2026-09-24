# Independent checker handoff

Stage: `checker_passes/translation`

Run this request in its own independent agent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one agent for multiple passes.

Save exactly one JSON response as `translation.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
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
  "input_body_sha256": "13559d31b050882ff1d24890c8d22914c8f87e20f0ddb0e509e2a8178469bd82",
  "input_sections": {
    "definitions": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 38,
        "text": "【日本語訳・定義】確証がない段階で、ある事柄が真実かもしれないと考えることを表す。人が犯罪・不正をした可能性への疑いもこの意味に含む。Oxfordは犯罪・不正の疑いでは可算・不可算の両用法を、命題の真偽については可算用法を記している。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 91,
        "text": "【日本語訳・定義】人や物事を十分に信用できず、疑いの目で見る態度を表す。ある事柄が真実かどうかについての見立てを表す語義1とは異なり、対象への不信や警戒に焦点を置く。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 119,
        "text": "【日本語訳・定義】ものがごく少量、またはかすかな兆候として感じられることを表す。通常 a suspicion of ... の形で使われる。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 46,
        "text": "【コロケーション】"
      },
      {
        "line": 48,
        "text": "・on suspicion of 〈crime〉  "
      },
      {
        "line": 49,
        "text": "用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕・拘束したことを述べる。  "
      },
      {
        "line": 50,
        "text": "例: Two people were arrested on suspicion of fraud after the investigation.  "
      },
      {
        "line": 51,
        "text": "訳: 捜査後、2人が詐欺の容疑で逮捕された。  "
      },
      {
        "line": 53,
        "text": "・be under suspicion  "
      },
      {
        "line": 54,
        "text": "用途: 人が不正や犯罪をしたのではないかと疑われている状態を表す。  "
      },
      {
        "line": 55,
        "text": "例: The contractor remained under suspicion while investigators checked whether it had falsified invoices.  "
      },
      {
        "line": 56,
        "text": "訳: 請求書を改ざんしたかどうかを捜査員が調べる間、その請負業者は疑いをかけられたままだった。  "
      },
      {
        "line": 58,
        "text": "・a suspicion that 〈clause〉  "
      },
      {
        "line": 59,
        "text": "用途: 確証がない段階で、節の内容が事実かもしれないという見立てを表す。  "
      },
      {
        "line": 60,
        "text": "例: The manager had a suspicion that the cashier had altered the sales records.  "
      },
      {
        "line": 61,
        "text": "訳: その管理者は、レジ係が売上記録を改ざんしたのではないかと疑っていた。  "
      },
      {
        "line": 63,
        "text": "・have a suspicion that 〈clause〉  "
      },
      {
        "line": 64,
        "text": "用途: 出来事や状態が実際に起きた、または成り立つのではないかという考えを抱く。  "
      },
      {
        "line": 65,
        "text": "例: I had a suspicion that the meeting had been canceled.  "
      },
      {
        "line": 66,
        "text": "訳: 会議は中止されたのではないかと私は疑っていた。  "
      },
      {
        "line": 68,
        "text": "・arouse someone's suspicions  "
      },
      {
        "line": 69,
        "text": "用途: ある出来事を受け、〈人〉が節の内容を真実かもしれないと疑うきっかけになる。  "
      },
      {
        "line": 70,
        "text": "例: The abrupt policy reversal aroused residents' suspicions that officials had concealed the project's true cost.  "
      },
      {
        "line": 71,
        "text": "訳: 突然の方針転換を受けて、住民たちは当局が事業の本当の費用を隠していたのではないかと疑い始めた。  "
      },
      {
        "line": 73,
        "text": "・raise some suspicion among 〈people〉  "
      },
      {
        "line": 74,
        "text": "用途: 説明できない事実が、人々の間に節の内容への疑いを生じさせる。  "
      },
      {
        "line": 75,
        "text": "例: The unexplained gap in the records raised some suspicion among auditors that several invoices had been altered.  "
      },
      {
        "line": 76,
        "text": "訳: 記録の説明できない欠落から、複数の請求書が改ざんされていたのではないかという疑いが監査担当者の間に生じた。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 99,
        "text": "【コロケーション】"
      },
      {
        "line": 101,
        "text": "・regard 〈person/thing〉 with suspicion  "
      },
      {
        "line": 102,
        "text": "用途: 人や物事をすぐには信用せず、疑いの目で見ることを表す。  "
      },
      {
        "line": 103,
        "text": "例: Residents regarded the sudden policy change with suspicion.  "
      },
      {
        "line": 104,
        "text": "訳: 住民たちは突然の方針変更を疑いの目で見た。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 127,
        "text": "【コロケーション】"
      },
      {
        "line": 129,
        "text": "・a suspicion of a smile  "
      },
      {
        "line": 130,
        "text": "用途: はっきり表れるほどではない、かすかな兆しを描写する。  "
      },
      {
        "line": 131,
        "text": "例: There was a suspicion of a smile in her reply.  "
      },
      {
        "line": 132,
        "text": "訳: 彼女の返事にはかすかな笑みが感じられた。  "
      },
      {
        "line": 134,
        "text": "・a suspicion of truth  "
      },
      {
        "line": 135,
        "text": "用途: 話や印象に真実味がかすかに感じられることを表す。  "
      },
      {
        "line": 136,
        "text": "例: The old tale had a suspicion of truth in it.  "
      },
      {
        "line": 137,
        "text": "訳: その古い物語には、どこか真実味が感じられた。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 80,
        "text": "【類義語】"
      },
      {
        "line": 82,
        "text": "・doubt  "
      },
      {
        "line": 83,
        "text": "定義: ある事柄の真偽について確信が持てない状態。  "
      },
      {
        "line": 84,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 85,
        "text": "違い: doubt は真偽の不確かさを広く表し、suspicion はある事柄が真実かもしれないという見立ても表す。  "
      },
      {
        "line": 86,
        "text": "例: There was some doubt about whether the meeting had been canceled.  "
      },
      {
        "line": 87,
        "text": "訳: 会議が中止されたかどうかについて、多少の疑問があった。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 108,
        "text": "【類義語】"
      },
      {
        "line": 110,
        "text": "・distrust  "
      },
      {
        "line": 111,
        "text": "定義: 人や物事を信頼できない気持ち。  "
      },
      {
        "line": 112,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 113,
        "text": "違い: distrust は信頼できない気持ちを直接表し、with suspicion は人や物事を疑いの目で見る態度を表す。Oxford Advanced American Dictionary は suspicion の第3語義を「人や物事を信頼できない気持ち」と説明し、両者の意味の重なりを示す。  "
      },
      {
        "line": 114,
        "text": "例: Residents regarded the proposal with distrust.  "
      },
      {
        "line": 115,
        "text": "訳: 住民たちはその提案を信用しなかった。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 141,
        "text": "【類義語】"
      },
      {
        "line": 143,
        "text": "・hint  "
      },
      {
        "line": 144,
        "text": "定義: Oxfordがこのごく少量・かすかな兆しの語義で挙げる類義語。  "
      },
      {
        "line": 145,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 146,
        "text": "違い: Oxfordはhintをこの語義の類義語として挙げ、suspicionの用法をformalと記している。  "
      },
      {
        "line": 147,
        "text": "例: The tea has a hint of mint.  "
      },
      {
        "line": 148,
        "text": "訳: そのお茶にはほのかなミントの風味がある。  "
      },
      {
        "line": 150,
        "text": "・trace  "
      },
      {
        "line": 151,
        "text": "定義: ごくわずかな量や痕跡を表す語。Merriam-Websterは本語義の類義語として挙げている。  "
      },
      {
        "line": 152,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 153,
        "text": "違い: Merriam-Websterはsuspicionの本語義をbarely detectable amount or traceと説明し、Oxfordはこの用法をformalとしている。  "
      },
      {
        "line": 154,
        "text": "例: There was only a trace of smoke in the air.  "
      },
      {
        "line": 155,
        "text": "訳: 空気中には煙がほんのわずかに漂っていた。  "
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
  "source_artifact_sha256": "d44f6f1eb825f6bfcff285716c87db277e5c8ceaeff55140e230ec57726868a2",
  "normalized_input_sha256": "f94b0b6eadf480072516bf32ee8d05d8e2caea44579dd9b0f217277f02a49956"
}
```
