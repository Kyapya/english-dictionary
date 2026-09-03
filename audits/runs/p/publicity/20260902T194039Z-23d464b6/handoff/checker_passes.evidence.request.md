# Independent checker handoff

Stage: `checker_passes/evidence`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.evidence.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_evidence_v6

## 目的

主張単位の根拠リンクが、対象主張を直接支持するかだけを検査する。source-first工程との二重チェックを避けるため、このパスは資料探索計画、source inventoryのcoverage、fact収集をやり直さない。

## 担当タクソノミー分類

- `evidence_claim_mismatch`

## 検査ルール

- source-first工程が固定したsource・fact・claim unit・対象sectionを入力として受け、claimと引用位置または忠実な要約の対応を確認する。
- 資料名や検索結果見出しが存在するだけで合格にせず、locator、該当箇所、支持内容、当該語義・構文への適用範囲を確認する。
- 別義、別品詞、別法域、別地域、別時代の記述を現在の対象主張へ流用しない。
- 高リスク主張に `two_sources_or_primary` が指定される場合、同一引用元を別IDにした重複を独立2資料として数えない。一次資料1件を使う場合は当該主張へ直接適用できることを確認する。
- 発音、語源、語義境界、文法制約、完全フレーム、例文の自然さ、絶対表現、地域差、頻度、専門説明、類義語・反意語差のevidence linkを個別に確認する。
- 断定的主張では支持例だけでなく、source-first記録にある反例・矛盾探索の方法と結果が主張範囲に対応するか確認する。
- 資料が食い違う場合、本文が差を反映して範囲を限定しているかを確認する。根拠から決められない内容をpassにしない。
- このパスはclaimの辞書学的正しさを他パスの代わりに再判定せず、「提示された根拠がそのclaimを支えるか」に限定する。

## 入力として受け取るセクション

- `pronunciation`
- `etymology`
- `word_formation`
- `core_image`
- `sense_structure`
- `frequency_register`
- `frames`
- `collocations_examples`
- `usage_notes`
- `lexical_relations`
- source-first工程が生成したsource inventory、fact、claim unit、evidence link

## findingの出力スキーマ

```json
{
  "taxonomy_id": "evidence_claim_mismatch",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "根拠対象となる本文主張"
  },
  "severity": "blocking | minor",
  "rationale": "source locator・支持内容・適用範囲の不一致",
  "evidence_link_ids": ["問題のある既存link ID"],
  "suggested_direction": "主張限定、根拠差替え、holdの方向"
}
```

根拠が主張を支持しない状態は原則 `blocking` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "evidence",
  "taxonomy_ids": [
    "evidence_claim_mismatch"
  ],
  "specification": "prompts/check_pass_evidence_v6.md",
  "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "基本: /pʌbˈlɪsəti/。米語では /pəˈblɪsəti/ も使われる。いずれも4音節で、第2音節に主強勢がある。/pʌbˈlɪsəti/ では第1音節が /pʌb/、第2音節が /ˈlɪs/ となる。/pəˈblɪsəti/ では第1音節が弱い /pə/ となり、/b/ は第2音節頭の /bl/ と発音される。これは米英の絶対的な地域差というより、辞書や話者による発音差として覚えるとよい。語末は /əti/ で、綴りの -ity を /aɪti/ と読まない。  "
      }
    ],
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
    "core_image": [],
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
    "frames": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 38,
        "text": "【文法パターン】gain/receive publicity＝世間の注目・報道を得る／widespread publicity＝広範な世間の注目・報道／good/bad/negative/unwanted publicity＝好意的な・悪い・否定的な・望まない注目／shun publicity＝世間の注目・報道を避ける  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 109,
        "text": "【文法パターン】publicity for/about 〈映画・商品・行事〉＝～に関する広報・注目／advance publicity for 〈発売・行事〉＝発売・行事の事前広報／publicity campaign/material/stunt＝宣伝キャンペーン・資料・仕掛け  "
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
    "lexical_relations": [
      {
        "line": 30,
        "text": "1. 【名詞・不可算】公衆の注目、報道上の露出"
      },
      {
        "line": 71,
        "text": "【類義語】"
      },
      {
        "line": 73,
        "text": "・attention  "
      },
      {
        "line": 74,
        "text": "定義: 人や話題に関心が向けられていること。  "
      },
      {
        "line": 75,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 76,
        "text": "違い: publicity は特に新聞・テレビなどを通じた公的な注目・露出に焦点があり、attention より媒体や公衆に寄る。  "
      },
      {
        "line": 77,
        "text": "例: The announcement attracted attention from local residents.  "
      },
      {
        "line": 78,
        "text": "訳: その発表は地元住民の注目を集めた。  "
      },
      {
        "line": 80,
        "text": "・exposure  "
      },
      {
        "line": 81,
        "text": "定義: 人・商品・活動などが公衆や媒体に知られること。  "
      },
      {
        "line": 82,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 83,
        "text": "違い: publicity は露出の機会一般より、世間の注目・報道を受けること、またはそれを集める活動を表す。  "
      },
      {
        "line": 84,
        "text": "例: The interview gave the small business valuable exposure.  "
      },
      {
        "line": 85,
        "text": "訳: そのインタビューは、その小企業に貴重な公的露出をもたらした。  "
      },
      {
        "line": 87,
        "text": "・coverage  "
      },
      {
        "line": 88,
        "text": "定義: 新聞、テレビ、ウェブなどによる報道。  "
      },
      {
        "line": 89,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 90,
        "text": "違い: coverage はメディアによる報道内容を指し、publicity は報道による注目や、注目を集める活動まで含む。  "
      },
      {
        "line": 91,
        "text": "例: The issue received extensive media coverage.  "
      },
      {
        "line": 92,
        "text": "訳: その問題はメディアで大きく報道された。  "
      },
      {
        "line": 94,
        "text": "・fame  "
      },
      {
        "line": 95,
        "text": "定義: 多くの人に知られている状態。  "
      },
      {
        "line": 96,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 97,
        "text": "違い: fame は知名度という状態を指すのに対し、publicity は一時的な注目・報道も表し、negative publicity のように評価中立である。  "
      },
      {
        "line": 98,
        "text": "例: The actor achieved international fame after the film won several awards.  "
      },
      {
        "line": 99,
        "text": "訳: その俳優は、その映画がいくつも賞を取った後、国際的な名声を得た。  "
      },
      {
        "line": 101,
        "text": "2. 【名詞・不可算】宣伝活動、広報"
      },
      {
        "line": 139,
        "text": "【類義語】"
      },
      {
        "line": 141,
        "text": "・advertising  "
      },
      {
        "line": 142,
        "text": "定義: 商品、サービス、組織などを広告によって公衆に知らせる活動。  "
      },
      {
        "line": 143,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 144,
        "text": "違い: advertising は有料の広告メッセージや広告業務に焦点がある。publicity は通常、情報・活動によって公衆の注目を集める語だが、辞書や文脈によって paid advertising を含むこともある。  "
      },
      {
        "line": 145,
        "text": "例: The company increased its advertising budget before the holiday season.  "
      },
      {
        "line": 146,
        "text": "訳: その会社は休暇シーズンの前に広告予算を増やした。  "
      },
      {
        "line": 148,
        "text": "・promotion  "
      },
      {
        "line": 149,
        "text": "定義: 商品、サービス、作品、考えなどの販売・普及・認知を高める活動。  "
      },
      {
        "line": 150,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 151,
        "text": "違い: promotion は販売・普及も含む広い活動語で、publicity は公衆の注目を集める情報・活動に焦点がある。  "
      },
      {
        "line": 152,
        "text": "例: The festival used social media promotion to sell more tickets.  "
      },
      {
        "line": 153,
        "text": "訳: その祭りは、より多くのチケットを売るためにSNSで販促を行った。  "
      },
      {
        "line": 155,
        "text": "・public relations  "
      },
      {
        "line": 156,
        "text": "定義: 企業・組織・人物と公衆との関係を管理する活動。  "
      },
      {
        "line": 157,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 158,
        "text": "違い: public relations は公衆との関係全体を扱う広い活動で、publicity は注目を集める広報活動やその結果を指しやすい。  "
      },
      {
        "line": 159,
        "text": "例: The company hired a public relations firm after the data breach.  "
      },
      {
        "line": 160,
        "text": "訳: その会社はデータ漏えいの後、広報会社を雇った。  "
      },
      {
        "line": 162,
        "text": "・marketing  "
      },
      {
        "line": 163,
        "text": "定義: 市場調査、商品設計、価格設定、流通、宣伝などを通じて需要と販売を形成する活動。  "
      },
      {
        "line": 164,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 165,
        "text": "違い: marketing は市場活動全体を扱う広い語で、publicity と重なる場合もある。ただし publicity は人・作品・行事・主張にも用いられる、注目を集める情報発信や活動を指す。  "
      },
      {
        "line": 166,
        "text": "例: The marketing team tested the new packaging with several customer groups.  "
      },
      {
        "line": 167,
        "text": "訳: マーケティングチームは複数の顧客グループで新しい包装を試した。  "
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
