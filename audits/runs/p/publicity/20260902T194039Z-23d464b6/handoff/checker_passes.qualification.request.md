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
  "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "フランス語 publicité を経て、ラテン語 publicus「公の、人民の」にさかのぼる。英語ではもともと「公にされている状態・公開性」を表し、そこから「世間に知られるようにすること」や、現代の「宣伝・広報活動」へ意味が発展した。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・publicist：publicity を作り、扱い、広める仕事をする人。映画、作家、芸能人、企業などの広報担当者を指す。  "
      },
      {
        "line": 24,
        "text": "・publicity campaign：商品、作品、行事、主張などに注目を集めるための宣伝・広報キャンペーン。  "
      },
      {
        "line": 25,
        "text": "・publicity material：宣伝・広報用の資料。  "
      },
      {
        "line": 26,
        "text": "・publicity stunt：世間の注目を集めるために意図して行う行為・仕掛け。話題作りの含みを持つ。  "
      }
    ],
    "sense_structure": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 32,
        "text": "【日本語訳・定義】人・企業・作品・出来事などが、新聞、テレビなどのメディアを通じて世間から受ける注目や報道上の露出。好意的とは限らず、good/bad/negative/unwanted publicity のように評価を添えられる。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 103,
        "text": "【日本語訳・定義】人、商品、作品、行事、主張などに世間の関心を集めるために行う広報・宣伝活動。広告に限らず、情報提供などの広報手段を含み得る。ここでは世間の注目を集める側の活動・手段に焦点を置く。  "
      }
    ],
    "frequency_register": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 34,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 36,
        "text": "【レジスター/領域】標準的な一般語。複数の一般辞書で主要な名詞として扱われる。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 105,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 107,
        "text": "【レジスター/領域】標準的な一般語。複数の一般辞書で活動・情報に関わる名詞用法として扱われる。  "
      }
    ],
    "usage_notes": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 67,
        "text": "【語法・注意】現代の一般用法ではこの語義の publicity は通常不可算で、a publicity や publicities は一般に避け、a lot of publicity、the publicity surrounding the case のように使う。publicity は注目・報道を表し、好評や長期的な名声を必ず含むわけではない。good/bad/negative/unwanted publicity のように評価を添えられる。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 133,
        "text": "【語法・注意】この語義でも publicity は通常不可算で、a publicity campaign、a publicity stunt のように、数えられるのは campaign や stunt などの具体的な活動である。the publicity for the film は映画の宣伝・広報活動を指し得るが、文脈によっては映画が受ける注目・報道も指す。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 40,
        "text": "【コロケーション】"
      },
      {
        "line": 42,
        "text": "・gain/receive publicity  "
      },
      {
        "line": 43,
        "text": "用途: 人・団体・作品・出来事が世間の注目や報道を受けることを表す。  "
      },
      {
        "line": 44,
        "text": "例: The charity gained widespread publicity after the athlete supported its campaign.  "
      },
      {
        "line": 45,
        "text": "訳: その慈善団体は、その選手がキャンペーンを支持した後、広く世間の注目を浴びた。  "
      },
      {
        "line": 47,
        "text": "・widespread publicity  "
      },
      {
        "line": 48,
        "text": "用途: 広い地域や多くの媒体に及ぶ世間の注目・報道を表す。  "
      },
      {
        "line": 49,
        "text": "例: The discovery received widespread publicity in the national press.  "
      },
      {
        "line": 50,
        "text": "訳: その発見は全国紙で広く報道された。  "
      },
      {
        "line": 52,
        "text": "・good/bad publicity  "
      },
      {
        "line": 53,
        "text": "用途: 注目が対象に好影響または悪影響を与えることを評価する。  "
      },
      {
        "line": 54,
        "text": "例: The scandal gave the company bad publicity.  "
      },
      {
        "line": 55,
        "text": "訳: その不祥事は会社に否定的な世間の注目をもたらした。  "
      },
      {
        "line": 57,
        "text": "・negative publicity  "
      },
      {
        "line": 58,
        "text": "用途: 批判、不祥事、悪い報道などによる否定的な世間の注目を表す。  "
      },
      {
        "line": 59,
        "text": "例: The restaurant responded quickly to the negative publicity surrounding the safety complaint.  "
      },
      {
        "line": 60,
        "text": "訳: そのレストランは、安全性に関する苦情をめぐる否定的な報道にすぐ対応した。  "
      },
      {
        "line": 62,
        "text": "・shun publicity  "
      },
      {
        "line": 63,
        "text": "用途: 世間の注目や報道を意図的に避けることを表す。  "
      },
      {
        "line": 64,
        "text": "例: The novelist shuns publicity and rarely gives interviews.  "
      },
      {
        "line": 65,
        "text": "訳: その小説家は世間の注目を避け、めったにインタビューに応じない。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 111,
        "text": "【コロケーション】"
      },
      {
        "line": 113,
        "text": "・a publicity campaign  "
      },
      {
        "line": 114,
        "text": "用途: 商品、作品、行事、主張などへの注目を集める計画的な宣伝活動を表す。  "
      },
      {
        "line": 115,
        "text": "例: The museum launched a publicity campaign for its new exhibition.  "
      },
      {
        "line": 116,
        "text": "訳: その博物館は新しい展覧会の広報キャンペーンを始めた。  "
      },
      {
        "line": 118,
        "text": "・publicity material  "
      },
      {
        "line": 119,
        "text": "用途: メディアや一般の人に提供する広報・宣伝用の資料を表す。  "
      },
      {
        "line": 120,
        "text": "例: The press office prepared publicity material for the product launch.  "
      },
      {
        "line": 121,
        "text": "訳: 広報室は製品発売のための宣伝資料を用意した。  "
      },
      {
        "line": 123,
        "text": "・advance publicity for 〈発売・行事〉  "
      },
      {
        "line": 124,
        "text": "用途: 映画、書籍、製品、行事などの開始前に行う事前広報を表す。  "
      },
      {
        "line": 125,
        "text": "例: The organizers arranged advance publicity for the festival several months before it opened.  "
      },
      {
        "line": 126,
        "text": "訳: 主催者は祭りの開幕数か月前から事前広報を手配した。  "
      },
      {
        "line": 128,
        "text": "・a publicity stunt  "
      },
      {
        "line": 129,
        "text": "用途: メディアや世間の注目を集めるために意図して行う行為・仕掛けを表す。  "
      },
      {
        "line": 130,
        "text": "例: The company staged a publicity stunt by projecting its logo onto the river bridge.  "
      },
      {
        "line": 131,
        "text": "訳: その会社は川に架かる橋へロゴを投影する話題作りの仕掛けを行った。  "
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
