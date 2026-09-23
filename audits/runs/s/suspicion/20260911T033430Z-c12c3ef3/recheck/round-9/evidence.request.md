# Independent review handoff

Stage: `checker_recheck/round-9/evidence`

Review only this packet and its named specification. Do not inspect other round files, prior findings, or alignment keys. Save the raw response at the exact path requested in your task, with required reviewer metadata.

## Prompt

# check_pass_evidence_v7

## 目的

主張単位の根拠リンクが、対象主張を直接支持するかだけを検査する。source-first工程との二重チェックを避けるため、このパスは資料探索計画、source inventoryのcoverage、fact収集をやり直さない。

## 担当タクソノミー分類

- `evidence_claim_mismatch`

## 検査ルール

- source-first工程が固定したsource・fact・claim unit・対象sectionを受け、本文→claim→外部資料の三者を照合する。まず `article_target_ids` に対応する `article_targets[].text` と周辺の本文を読み、claimがその箇所で実際に述べられているか確認する。実在するIDでも、発音の箇所へ意味説明が結び付いているなど意味上の接続違いはblocking findingにする。
- 現行入力は `evidence_context_v2`。対象claimに関係するsource、fact、source union、claim unit、`source_supports` に、スクリプトが最新本文から抽出した `article_targets` を加える。旧 `evidence_context_v1` は過去runの再現用。`source_inventory_sha256`、`source_first_artifact_sha256`、本文hashの一致を機械検証済みでなければ開始しない。
- locatorの外部資料を実際に開き、該当箇所を本文と照合する。作成者のfactや `support_summary` は照合の手掛かりであり、独立した外部確認の代わりにならない。同じページは一度開いて関係claimをまとめて確認できる。新しい探索計画や全factの作り直しは不要だが、既存資料の再閲覧は必要である。
- 資料名・著者・locator・引用箇所が同じ資料を指すかを確認する。複数辞書名を一つのlocatorで代表させたり、別資料の語源説明をそのページの記述として扱ったりしない。
- 外部閲覧機能がない実行、アクセス不能、該当箇所不明では、既知知識や要約で補って確認済みにせず、対象claimのblocking findingに `insufficient_evidence` と確認できなかったlocatorを記す。API/handoffのどちらでもこの条件は同じ。現在の標準API呼出しには閲覧ツールがないため、外部資料を閲覧できるhandoff reviewerを使う。
- source-first artifactが欠落、未完了、schema不正、参照切れ、本文hash不一致の場合はfail closedとし、再探索やfact追加で補わない。
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
- API modeとhandoff modeはいずれも `scripts/check_passes.py` が生成した同一の正規化requestを使う。

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

出力は問題のある箇所のfindingsに集中する。正常claimごとの合格理由・本文の再掲・別の全件証明表は作らない。全対象を確認して問題がなければ空のfindingsでよい。これは未確認範囲を省略してよいという意味ではない。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "evidence",
  "taxonomy_ids": [
    "evidence_claim_mismatch"
  ],
  "specification": "prompts/check_pass_evidence_v7.md",
  "input_body_sha256": "4ab0d5d71a7c1f54616c6e43ea3bd1cf78edf3d0d530028f0398efd73951f200",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米: Oxford の米語IPAは /səˈspɪʃn/。Merriam-Webster は sus·pi·cion と3音節に区切り、第2音節に主強勢を示す。両辞書で表記形式が異なる。  "
      }
    ],
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "suspicion は中英語を経て、アングロフランス語・古フランス語からラテン語系の形へさかのぼる。辞書によってラテン語形は suspicio、suspectio、suspectio(n-) と記され、中継経路の説明にも差がある。Merriam-Webster は suspicere「疑う」に由来すると説明している。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・suspicious：形容詞。「疑っている、不信に思っている」、または人に疑いを起こさせる「疑わしい」。  "
      },
      {
        "line": 24,
        "text": "・suspiciously：副詞形。  "
      },
      {
        "line": 25,
        "text": "・suspiciousness：名詞形。  "
      },
      {
        "line": 26,
        "text": "・suspicion（動詞）：他動詞で「～を疑う」。Merriam-Webster では chiefly dialectal とされる。  "
      }
    ],
    "core_image": [
      {
        "line": 28,
        "text": "＃コアイメージ"
      },
      {
        "line": 30,
        "text": "学習上は「確証のない段階で、ある事柄が真実かもしれないと考える」という見立てを中心にする。人の犯罪・不正を疑う用法はその具体例であり、suspicion that ... の節には別の出来事や状態も続く。人や物事を信用できず疑いの目で見る用法は、対象への不信・警戒という態度に焦点を置く。a suspicion of a smile / truth は「ごく少量・かすかな兆し」を表す形式的な比喩用法。この整理は学習上の目安で、全用法が一つの語源的意味を共有するという主張ではない。  "
      }
    ],
    "sense_structure": [
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
    "frequency_register": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 40,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 42,
        "text": "【レジスター/領域】標準語。犯罪・不正の可能性から、会議の中止など出来事や状態の真偽まで、確証のない考えを述べる。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 93,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 95,
        "text": "【レジスター/領域】標準語。人や物事、説明などを信用できず、疑いの目で見る態度を述べる。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 121,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 123,
        "text": "【レジスター/領域】単数形で用いる形式的な用法。  "
      }
    ],
    "frames": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 44,
        "text": "【文法パターン】suspicion that 〈clause〉＝～ではないかという疑い／have a suspicion that 〈clause〉＝～ではないかという疑いを抱く／arouse 〈person〉's suspicions that 〈clause〉＝〈人〉に～ではないかという疑いを起こさせる／raise some suspicion among 〈people〉 that 〈clause〉＝〈人々〉の間に～ではないかという疑いを生じさせる／on suspicion of 〈offence〉＝〈犯罪〉の容疑で／be under suspicion＝疑いをかけられている。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 97,
        "text": "【文法パターン】regard 〈person/thing〉 with suspicion＝〈人・物事〉を疑いの目で見る。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 125,
        "text": "【文法パターン】a suspicion of 〈a smile〉＝笑みがかすかに感じられること／a suspicion of 〈truth〉＝真実味がかすかに感じられること。  "
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
    "usage_notes": [
      {
        "line": 36,
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "line": 78,
        "text": "【語法・注意】on suspicion of theft は「窃盗で有罪になった」ではなく、「窃盗をした疑いを理由に」という意味である。under suspicion も罪が確定した状態を表さない。Merriam-Webster の法律辞典は suspicion を通常、信念に至らない精神状態として説明し、reasonable suspicion の項目に関連づけている。ここでは特定の法域の法的基準を述べない。  "
      },
      {
        "line": 89,
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "line": 106,
        "text": "【語法・注意】with suspicion は、対象を信頼できるか疑って見る態度を表す。  "
      },
      {
        "line": 117,
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "line": 139,
        "text": "【語法・注意】この a suspicion of ... は「～を疑うこと」ではなく、「～がごく少量、または兆候としてわずかに感じられること」である。  "
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
        "text": "定義: 信用できない気持ち。Oxfordはこの語を本語義の説明に含めている。  "
      },
      {
        "line": 112,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 113,
        "text": "違い: Oxfordは本語義を doubt or distrust と説明し、両語の意味が重なることを示している。  "
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
  "evidence_context": {
    "schema_version": "evidence_context_v2",
    "input_body_sha256": "4ab0d5d71a7c1f54616c6e43ea3bd1cf78edf3d0d530028f0398efd73951f200",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "347e233f306bdc49da8f511b1faae45617cfdfb9c77c157a2a102273308cf8cb",
    "source_first_artifact_sha256": "e90fd78ac088d2024598beed6ae0af6133d299beb74c373437b548466fce7266",
    "relevant_sections": [
      "collocations_examples",
      "core_image",
      "etymology",
      "frames",
      "frequency_register",
      "lexical_relations",
      "pronunciation",
      "sense_structure",
      "usage_notes",
      "word_formation"
    ],
    "sources": [
      {
        "id": "S-ENTRY-SPEC",
        "locator": "prompts/entry_spec_v5.md#頻度 (repository source, lines 433-447)",
        "source_type": "internal_authoring_specification",
        "independence_group": "repository_entry_spec",
        "facts": [
          {
            "id": "F-ENTRY-SPEC-FREQUENCY",
            "form": "entry_spec_v5 frequency rating rubric",
            "kind": "editorial_rating_method",
            "statement": "The article must assign each sense and sense-specific synonym a ten-point rating of English-wide encounter frequency. The rubric permits estimates without strict statistical data, while requiring consistent criteria and caution against overstating regional, specialist, or dated uses.",
            "source_detail": "Repository authoring specification, section “頻度”, lines 433-447; internal methodology source, not an external dictionary or corpus."
          }
        ]
      },
      {
        "id": "S-ETY",
        "locator": "https://www.etymonline.com/word/suspicion",
        "source_type": "etymology_reference",
        "independence_group": "etymonline",
        "facts": [
          {
            "id": "F-ETY-1",
            "form": "suspicion",
            "kind": "etymology",
            "statement": "The noun is recorded around 1300 through Anglo-French and Old French from Late Latin suspectio(n-), from suspicere.",
            "source_detail": "Online Etymology Dictionary, “suspicion” etymology; retrieved lines 52–56."
          }
        ]
      },
      {
        "id": "S-MW",
        "locator": "suspicion: https://www.merriam-webster.com/dictionary/suspicion; suspicious: https://www.merriam-webster.com/dictionary/suspicious",
        "source_type": "general_dictionary",
        "independence_group": "merriam_webster",
        "facts": [
          {
            "id": "F-MW-1",
            "form": "suspicion",
            "kind": "sense",
            "statement": "The noun can mean an act or instance of suspecting something wrong without proof or on slight evidence; mistrust is given as a synonym.",
            "source_detail": "Merriam-Webster Dictionary, noun sense 1a; retrieved lines 31–50."
          },
          {
            "id": "F-MW-2",
            "form": "suspicion",
            "kind": "sense",
            "statement": "The noun can mean a state of mental uneasiness and uncertainty or doubt.",
            "source_detail": "Merriam-Webster Dictionary, noun sense 1b; retrieved lines 48–50."
          },
          {
            "id": "F-MW-3",
            "form": "suspicion",
            "kind": "sense",
            "statement": "The noun can mean a barely detectable amount or trace.",
            "source_detail": "Merriam-Webster Dictionary, noun sense 2 and example; retrieved lines 52–56."
          },
          {
            "id": "F-MW-4",
            "form": "suspicion",
            "kind": "frame",
            "statement": "Examples attest suspicion that + clause, suspicion about someone’s motives, with suspicion, arouse someone’s suspicions, raise some suspicion, and suspicions being confirmed.",
            "source_detail": "Merriam-Webster Dictionary, example set; retrieved lines 115–116. The painting example is paraphrased as a direct illustration of a proposition believed possibly true."
          },
          {
            "id": "F-MW-5",
            "form": "suspicion",
            "kind": "pronunciation",
            "statement": "The headword shows spelling syllabification sus·pi·cion and pronunciation respelling sə-ˈspi-shən, whose stress mark precedes the second syllable.",
            "source_detail": "Merriam-Webster Dictionary, headword pronunciation; the entry shows sus·pi·cion and the distinct pronunciation respelling sə-ˈspi-shən; retrieved line 36."
          },
          {
            "id": "F-MW-6",
            "form": "suspicion",
            "kind": "etymology",
            "statement": "The noun is traced through Middle English and Anglo-French to Latin suspicio, from suspicere “to suspect”; first known use is dated to the 14th century.",
            "source_detail": "Merriam-Webster Dictionary, Word History and First Known Use; retrieved lines 124–136."
          },
          {
            "id": "F-MW-7",
            "form": "suspicion",
            "kind": "legal_use",
            "statement": "The legal dictionary describes suspicion as a mental state usually short of belief in which one entertains a notion that something is wrong or a fact exists without proof or slight evidence; it cross-references reasonable suspicion.",
            "source_detail": "Merriam-Webster Legal Definition; retrieved lines 199–209. This supports the general lexical note only, not a jurisdiction-specific legal test."
          },
          {
            "id": "F-MW-8",
            "form": "suspicion",
            "kind": "derived_form",
            "statement": "The same entry also lists suspicion as a chiefly dialectal transitive verb meaning suspect.",
            "source_detail": "Merriam-Webster Dictionary, second part-of-speech entry; retrieved lines 58–69."
          },
          {
            "id": "F-MW-9",
            "form": "suspicious",
            "kind": "derived_form",
            "statement": "The related adjective suspicious can mean tending to arouse suspicion, disposed to suspect or distrust, or expressing suspicion.",
            "source_detail": "Merriam-Webster Dictionary, suspicious entry, senses 1–3; retrieved lines 31–56."
          },
          {
            "id": "F-MW-10",
            "form": "suspiciously",
            "kind": "derived_form",
            "statement": "The suspicious entry lists suspiciously as its adverb form.",
            "source_detail": "Merriam-Webster Dictionary, suspicious entry; retrieved line 58."
          },
          {
            "id": "F-MW-11",
            "form": "suspiciousness",
            "kind": "derived_form",
            "statement": "The suspicious entry lists suspiciousness as its noun form.",
            "source_detail": "Merriam-Webster Dictionary, suspicious entry; retrieved line 60."
          },
          {
            "id": "F-MW-12",
            "form": "suspicion",
            "kind": "register",
            "statement": "The entry labels the verb use chiefly dialectal, distinguishing it from the standard noun uses.",
            "source_detail": "Merriam-Webster Dictionary, second part-of-speech entry; retrieved lines 60–69."
          }
        ]
      },
      {
        "id": "S-OUP",
        "locator": "https://www.oxfordlearnersdictionaries.com/definition/american_english/suspicion ; https://www.oxfordlearnersdictionaries.com/definition/english/suspicion",
        "source_type": "learner_dictionary",
        "independence_group": "oxford_university_press",
        "facts": [
          {
            "id": "F-OUP-1",
            "form": "suspicion",
            "kind": "sense",
            "statement": "A belief that a person has done something wrong, dishonest, or illegal without proof; countable and uncountable use.",
            "source_detail": "Oxford Advanced American Dictionary, senses 1 and idiom entries; retrieved lines 97–110."
          },
          {
            "id": "F-OUP-2",
            "form": "suspicion",
            "kind": "sense",
            "statement": "A countable belief or suspicion that a proposition is true, despite lack of proof.",
            "source_detail": "Oxford Advanced American Dictionary, sense 2; retrieved lines 97–110."
          },
          {
            "id": "F-OUP-3",
            "form": "suspicion",
            "kind": "sense",
            "statement": "Doubt or distrust directed toward a person or thing; countable and uncountable use.",
            "source_detail": "Oxford Advanced American Dictionary, sense 3; retrieved lines 97–110."
          },
          {
            "id": "F-OUP-4",
            "form": "suspicion",
            "kind": "sense",
            "statement": "A singular, formal use for a very small amount or slight sign of something, comparable to a hint.",
            "source_detail": "Oxford Advanced Learner’s Dictionary, sense 4; retrieved lines 249–256."
          },
          {
            "id": "F-OUP-5",
            "form": "suspicion",
            "kind": "pronunciation",
            "statement": "North American pronunciation is shown as /səˈspɪʃn/.",
            "source_detail": "Oxford Advanced American Dictionary, headword pronunciation; retrieved line 97."
          },
          {
            "id": "F-OUP-6",
            "form": "suspicion",
            "kind": "frame",
            "statement": "The entry records patterns including suspicion that + clause, suspicion of + noun, on suspicion of + offence, and under suspicion.",
            "source_detail": "Oxford Advanced American Dictionary, senses and idioms; retrieved lines 97–110."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "U-DIALECT-VERB",
        "source_fact_ids": [
          "F-MW-8",
          "F-MW-12"
        ],
        "canonical_statement": "Merriam-Webster records a chiefly dialectal transitive verb suspicion meaning suspect.",
        "disposition": "integrated",
        "rationale": "The article mentions this uncommon verb separately and does not present it as a main standard noun sense."
      },
      {
        "id": "U-DISTRUST",
        "source_fact_ids": [
          "F-OUP-3"
        ],
        "canonical_statement": "Oxford records a suspicion sense meaning doubt or distrust directed toward a person or thing.",
        "disposition": "included",
        "rationale": "The article uses Oxford’s direct definition; Merriam-Webster examples remain assigned to the separate frame union."
      },
      {
        "id": "U-ETYMOLOGY",
        "source_fact_ids": [
          "F-MW-6",
          "F-ETY-1"
        ],
        "canonical_statement": "Dictionary accounts trace suspicion through Middle English and French to Latin forms related to suspicere, with source-specific forms and routes.",
        "disposition": "included",
        "rationale": "The article reports the source-specific route and removes the unsupported suspect-family claim."
      },
      {
        "id": "U-FRAMES",
        "source_fact_ids": [
          "F-OUP-6",
          "F-MW-4"
        ],
        "canonical_statement": "Oxford records suspicion that + clause, on suspicion of + offence, and under suspicion; Merriam-Webster examples separately attest arouse someone’s suspicions, raise some suspicion, suspicion that + clause, and with suspicion.",
        "disposition": "integrated",
        "rationale": "The article retains separately attested patterns and distinguishes the number and frame in arouse someone’s suspicions from raise some suspicion. It omits unsupported bare suspicion of crime/wrongdoing and confirm suspicions that combinations."
      },
      {
        "id": "U-FREQUENCY-RUBRIC",
        "source_fact_ids": [
          "F-ENTRY-SPEC-FREQUENCY"
        ],
        "canonical_statement": "The entry-spec requires learner-facing editorial frequency ratings under a ten-point English-wide encounter rubric and explicitly allows estimates without strict statistical basis.",
        "disposition": "integrated",
        "rationale": "The article explicitly labels its values as editorial qualitative estimates, not corpus counts or dictionary-published numbers; the local specification is the primary source for the required rating method."
      },
      {
        "id": "U-GUILT",
        "source_fact_ids": [
          "F-OUP-1",
          "F-MW-1"
        ],
        "canonical_statement": "Suspicion can denote a countable or uncountable belief that someone did something wrong without proof.",
        "disposition": "included",
        "rationale": "The article retains the evidence-limited wrongdoing sense; it no longer claims a separate state-of-being-suspected meaning."
      },
      {
        "id": "U-LEGAL-USE",
        "source_fact_ids": [
          "F-MW-7"
        ],
        "canonical_statement": "The legal dictionary entry describes suspicion as a mental state generally short of belief and cross-references reasonable suspicion.",
        "disposition": "integrated",
        "rationale": "The article limits its legal note to the general meaning and the phrase on suspicion of; it does not explain a jurisdiction-specific reasonable-suspicion test."
      },
      {
        "id": "U-MW-UNCERTAINTY",
        "source_fact_ids": [
          "F-MW-2"
        ],
        "canonical_statement": "Merriam-Webster records a broader state of mental uneasiness, uncertainty, or doubt.",
        "disposition": "integrated",
        "rationale": "This broader dictionary use informs the article’s comparison with doubt; it is not presented as a separate additional numbered sense."
      },
      {
        "id": "U-PRONUNCIATION",
        "source_fact_ids": [
          "F-OUP-5",
          "F-MW-5"
        ],
        "canonical_statement": "Oxford gives the North American IPA /səˈspɪʃn/; Merriam-Webster separately shows spelling syllabification and a pronunciation respelling with primary stress on the second syllable.",
        "disposition": "included",
        "rationale": "The article distinguishes Oxford’s IPA from Merriam-Webster’s spelling division and stress-marked pronunciation respelling; it makes no regional or phonetic equivalence claim."
      },
      {
        "id": "U-SMALL-AMOUNT",
        "source_fact_ids": [
          "F-OUP-4",
          "F-MW-3"
        ],
        "canonical_statement": "A singular suspicion can denote a very small amount or faint sign of something.",
        "disposition": "included",
        "rationale": "Oxford and Merriam-Webster directly support the retained small-amount use and its examples."
      },
      {
        "id": "U-SUSPICIOUS",
        "source_fact_ids": [
          "F-MW-9"
        ],
        "canonical_statement": "Suspicious is a related adjective that can describe a person disposed to distrust and something that arouses suspicion.",
        "disposition": "integrated",
        "rationale": "The article includes the related adjective and distinguishes psychological from property uses."
      },
      {
        "id": "U-SUSPICIOUSLY",
        "source_fact_ids": [
          "F-MW-10"
        ],
        "canonical_statement": "Suspiciously is listed as an adverb related to suspicious.",
        "disposition": "integrated",
        "rationale": "The article includes suspiciously as a related form."
      },
      {
        "id": "U-SUSPICIOUSNESS",
        "source_fact_ids": [
          "F-MW-11"
        ],
        "canonical_statement": "Suspiciousness is listed as a noun related to suspicious.",
        "disposition": "integrated",
        "rationale": "The article includes suspiciousness as a related form."
      },
      {
        "id": "U-UNCERTAIN-BELIEF",
        "source_fact_ids": [
          "F-OUP-2"
        ],
        "canonical_statement": "Oxford records a countable belief or suspicion that a proposition is true despite lack of proof.",
        "disposition": "included",
        "rationale": "The article uses the directly accessible Oxford meaning only. Cambridge’s search-result record and Merriam-Webster’s broader doubt definition are not treated as direct support for this sense."
      }
    ],
    "claim_units": [
      {
        "id": "C-CORE-IMAGE",
        "union_ids": [
          "U-GUILT",
          "U-UNCERTAIN-BELIEF",
          "U-DISTRUST",
          "U-SMALL-AMOUNT"
        ],
        "subject_form": "suspicion",
        "claim_type": "core_image",
        "statement": "As a learner-facing aid, the article centers on an evidence-limited belief that something may be true, treats wrongdoing as one common object of that belief, distinguishes distrust as an attitude, and keeps the figurative small-amount use separate; it does not assert one historical core.",
        "article_target_ids": [
          "core_image:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-OUP-1",
            "support_summary": "Oxford defines the wrongdoing use as a belief held without proof."
          },
          {
            "source_fact_id": "F-MW-1",
            "support_summary": "Merriam-Webster defines suspecting something wrong without proof or slight evidence."
          },
          {
            "source_fact_id": "F-OUP-2",
            "support_summary": "Oxford records a separate countable belief that a proposition may be true."
          },
          {
            "source_fact_id": "F-OUP-3",
            "support_summary": "Oxford records a doubt or distrust use directed toward a person or thing."
          },
          {
            "source_fact_id": "F-OUP-4",
            "support_summary": "Oxford records the formal small-amount or slight-sign use."
          },
          {
            "source_fact_id": "F-MW-3",
            "support_summary": "Merriam-Webster records a barely detectable amount or trace."
          }
        ]
      },
      {
        "id": "C-GUILT",
        "union_ids": [
          "U-GUILT",
          "U-UNCERTAIN-BELIEF"
        ],
        "subject_form": "suspicion",
        "claim_type": "sense",
        "statement": "Suspicion can denote an evidence-limited belief that something may be true; wrongdoing is one common object, and the wrongdoing use is countable or uncountable.",
        "article_target_ids": [
          "definition:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-OUP-1",
            "support_summary": "Oxford defines a belief that a person did something wrong without proof and marks the wrongdoing use countable and uncountable."
          },
          {
            "source_fact_id": "F-MW-1",
            "support_summary": "Merriam-Webster defines suspecting something wrong without proof or slight evidence."
          },
          {
            "source_fact_id": "F-OUP-2",
            "support_summary": "Oxford also records a countable belief-that use beyond wrongdoing."
          }
        ]
      },
      {
        "id": "C-DOUBT-RELATION",
        "union_ids": [
          "U-UNCERTAIN-BELIEF",
          "U-MW-UNCERTAINTY"
        ],
        "subject_form": "suspicion / doubt",
        "claim_type": "lexical_relation",
        "statement": "The article uses doubt for uncertainty about whether a proposition is true and suspicion also for an evidence-limited belief that the proposition may be true.",
        "article_target_ids": [
          "synonym:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-OUP-2",
            "support_summary": "Oxford describes suspicion as a countable belief that a proposition may be true despite lack of proof."
          },
          {
            "source_fact_id": "F-MW-2",
            "support_summary": "Merriam-Webster describes a broader state of mental uneasiness, uncertainty, or doubt."
          }
        ]
      },
      {
        "id": "C-DISTRUST",
        "union_ids": [
          "U-DISTRUST"
        ],
        "subject_form": "suspicion",
        "claim_type": "sense",
        "statement": "Suspicion can mean doubt or lack of trust directed toward a person or thing.",
        "article_target_ids": [
          "definition:002",
          "synonym:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-OUP-3",
            "support_summary": "Oxford describes this use as doubt or distrust directed toward a person or thing."
          }
        ]
      },
      {
        "id": "C-TRACE-MEANING",
        "union_ids": [
          "U-SMALL-AMOUNT"
        ],
        "subject_form": "suspicion",
        "claim_type": "sense",
        "statement": "A suspicion can mean a barely detectable amount or slight sign of something.",
        "article_target_ids": [
          "definition:003",
          "synonym:003",
          "synonym:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-OUP-4",
            "support_summary": "Oxford defines the singular formal use as a small amount or hint."
          },
          {
            "source_fact_id": "F-MW-3",
            "support_summary": "Merriam-Webster defines a barely detectable amount or trace."
          }
        ]
      },
      {
        "id": "C-TRACE-FRAMES",
        "union_ids": [
          "U-SMALL-AMOUNT"
        ],
        "subject_form": "suspicion",
        "claim_type": "frame",
        "statement": "The small-amount use occurs in a suspicion of a smile and a suspicion of truth.",
        "article_target_ids": [
          "grammar_pattern:008",
          "grammar_pattern:009",
          "collocation:008",
          "collocation:009"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-OUP-4",
            "support_summary": "Oxford gives a suspicion of a smile and a suspicion of truth in its small-amount sense."
          }
        ]
      },
      {
        "id": "C-FRAMES-OXFORD",
        "union_ids": [
          "U-FRAMES"
        ],
        "subject_form": "suspicion",
        "claim_type": "frame",
        "statement": "Oxford records suspicion that + clause, on suspicion of + offence, and under suspicion as separate patterns.",
        "article_target_ids": [
          "grammar_pattern:001",
          "grammar_pattern:005",
          "grammar_pattern:006",
          "collocation:001",
          "collocation:002",
          "collocation:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-OUP-6",
            "support_summary": "Oxford directly lists suspicion that, on suspicion of an offence, and under suspicion patterns."
          }
        ]
      },
      {
        "id": "C-FRAMES-MW",
        "union_ids": [
          "U-FRAMES"
        ],
        "subject_form": "suspicion",
        "claim_type": "frame",
        "statement": "Merriam-Webster examples attest suspicion that + clause, arouse someone’s suspicions, raise some suspicion, and regard a plan with suspicion as separate patterns.",
        "article_target_ids": [
          "grammar_pattern:001",
          "grammar_pattern:002",
          "grammar_pattern:003",
          "grammar_pattern:004",
          "grammar_pattern:007",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-MW-4",
            "support_summary": "Merriam-Webster examples distinguish arousing someone’s suspicions from raising some suspicion, and attest suspicion-that and with-suspicion patterns."
          }
        ]
      },
      {
        "id": "C-PRON",
        "union_ids": [
          "U-PRONUNCIATION"
        ],
        "subject_form": "suspicion",
        "claim_type": "pronunciation",
        "statement": "Oxford gives the North American IPA /səˈspɪʃn/; Merriam-Webster shows sus·pi·cion as a spelling division and sə-ˈspi-shən as a pronunciation respelling with second-syllable stress.",
        "article_target_ids": [
          "pronunciation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-OUP-5",
            "support_summary": "Oxford’s headword pronunciation gives the North American IPA /səˈspɪʃn/."
          },
          {
            "source_fact_id": "F-MW-5",
            "support_summary": "Merriam-Webster distinguishes the syllabified spelling from its stress-marked pronunciation respelling sə-ˈspi-shən."
          }
        ]
      },
      {
        "id": "C-ETYMOLOGY",
        "union_ids": [
          "U-ETYMOLOGY"
        ],
        "subject_form": "suspicion",
        "claim_type": "etymology",
        "statement": "Dictionary accounts trace suspicion through Middle English and French to Latin forms related to suspicere; sources differ in the Latin form and route.",
        "article_target_ids": [
          "etymology:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-MW-6",
            "support_summary": "Merriam-Webster gives the Middle English and Anglo-French route to Latin suspicio from suspicere."
          },
          {
            "source_fact_id": "F-ETY-1",
            "support_summary": "Etymonline records the Anglo-French and Old French route to Late Latin suspectio(n-) from suspicere."
          }
        ]
      },
      {
        "id": "C-SUSPICIOUS",
        "union_ids": [
          "U-SUSPICIOUS"
        ],
        "subject_form": "suspicious",
        "claim_type": "derived_form",
        "statement": "Suspicious can describe a person disposed to distrust and something that arouses suspicion.",
        "article_target_ids": [
          "word_formation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-MW-9",
            "support_summary": "The Merriam-Webster suspicious entry gives distrustful-person and suspicion-arousing-property meanings."
          }
        ]
      },
      {
        "id": "C-SUSPICIOUSLY",
        "union_ids": [
          "U-SUSPICIOUSLY"
        ],
        "subject_form": "suspiciously",
        "claim_type": "derived_form",
        "statement": "Suspiciously is listed as the adverb form related to suspicious.",
        "article_target_ids": [
          "word_formation:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-MW-10",
            "support_summary": "The Merriam-Webster suspicious entry lists suspiciously as its adverb form."
          }
        ]
      },
      {
        "id": "C-SUSPICIOUSNESS",
        "union_ids": [
          "U-SUSPICIOUSNESS"
        ],
        "subject_form": "suspiciousness",
        "claim_type": "derived_form",
        "statement": "Suspiciousness is listed as the noun form related to suspicious.",
        "article_target_ids": [
          "word_formation:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-MW-11",
            "support_summary": "The Merriam-Webster suspicious entry lists suspiciousness as its noun form."
          }
        ]
      },
      {
        "id": "C-DIALECT-VERB",
        "union_ids": [
          "U-DIALECT-VERB"
        ],
        "subject_form": "suspicion",
        "claim_type": "usage",
        "statement": "Merriam-Webster records a transitive verb suspicion meaning suspect and labels it chiefly dialectal.",
        "article_target_ids": [
          "word_formation:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-MW-8",
            "support_summary": "Merriam-Webster records the dialectal transitive verb suspicion meaning suspect."
          },
          {
            "source_fact_id": "F-MW-12",
            "support_summary": "Merriam-Webster labels that verb use chiefly dialectal."
          }
        ]
      },
      {
        "id": "C-LEGAL-NOTE",
        "union_ids": [
          "U-LEGAL-USE"
        ],
        "subject_form": "suspicion",
        "claim_type": "usage",
        "statement": "A legal dictionary describes suspicion as a mental state usually short of belief and cross-references reasonable suspicion, without asserting a jurisdiction-specific legal test.",
        "article_target_ids": [
          "usage_note:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-MW-7",
            "support_summary": "The Merriam-Webster legal definition says suspicion is usually short of belief and cross-references reasonable suspicion."
          }
        ]
      },
      {
        "id": "C-FREQUENCY-RATINGS",
        "union_ids": [
          "U-FREQUENCY-RUBRIC"
        ],
        "subject_form": "suspicion and the listed synonyms",
        "claim_type": "editorial_frequency_rating",
        "statement": "The article labels each sense and sense-specific synonym score as an editorial learner-facing estimate under the entry-spec ten-point English-wide encounter rubric; it does not attribute the figures to a dictionary or corpus.",
        "article_target_ids": [
          "narrative:001",
          "frequency:001",
          "frequency:002",
          "frequency:003",
          "synonym:001",
          "synonym:002",
          "synonym:003",
          "synonym:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-ENTRY-SPEC-FREQUENCY",
            "support_summary": "The repository specification mandates these editorial ratings, defines their intended scale, and permits estimates without strict statistical data."
          }
        ]
      }
    ],
    "article_targets": [
      {
        "id": "collocation:001",
        "kind": "collocation",
        "location": "lines:37-40",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "5ef102eef7cc8b8b801d5743c5b965d3d4735889d4c7d15d4397179ac8049b00",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・on suspicion of 〈crime〉\n用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕・拘束したことを述べる。\n例: Two people were arrested on suspicion of fraud after the investigation.\n訳: 捜査後、2人が詐欺の容疑で逮捕された。"
      },
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:42-45",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "7688df6035a8d599101b2d46b541efcb1319db3b5923d348e0bd287be972a817",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・be under suspicion\n用途: 人が不正や犯罪をしたのではないかと疑われている状態を表す。\n例: The contractor remained under suspicion while investigators checked whether it had falsified invoices.\n訳: 請求書を改ざんしたかどうかを捜査員が調べる間、その請負業者は疑いをかけられたままだった。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:47-50",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "ef426f07ec1d06c148eaf4f41547369cbaafdbb04330f48dcba76fc1e8352087",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a suspicion that 〈clause〉\n用途: 確証がない段階で、節の内容が事実かもしれないという見立てを表す。\n例: The manager had a suspicion that the cashier had altered the sales records.\n訳: その管理者は、レジ係が売上記録を改ざんしたのではないかと疑っていた。"
      },
      {
        "id": "collocation:004",
        "kind": "collocation",
        "location": "lines:52-55",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "a8b87b5f7b9f13a180417c9087c72a078fbd3a3efa4f4a375d5692fa72ce649a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・have a suspicion that 〈clause〉\n用途: 出来事や状態が実際に起きた、または成り立つのではないかという考えを抱く。\n例: I had a suspicion that the meeting had been canceled.\n訳: 会議は中止されたのではないかと私は疑っていた。"
      },
      {
        "id": "collocation:005",
        "kind": "collocation",
        "location": "lines:57-60",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "86f02c242bc973abf10bbbfe51740b1ca54d276991dbd2d20de3b1deae72d680",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・arouse someone's suspicions\n用途: ある出来事を受け、〈人〉が節の内容を真実かもしれないと疑うきっかけになる。\n例: The abrupt policy reversal aroused residents' suspicions that officials had concealed the project's true cost.\n訳: 突然の方針転換を受けて、住民たちは当局が事業の本当の費用を隠していたのではないかと疑い始めた。"
      },
      {
        "id": "collocation:006",
        "kind": "collocation",
        "location": "lines:62-65",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "13e56c485b7b9cc3746aa189b7003736972679814d33b013f07ca8c9386de831",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・raise some suspicion among 〈people〉\n用途: 説明できない事実が、人々の間に節の内容への疑いを生じさせる。\n例: The unexplained gap in the records raised some suspicion among auditors that several invoices had been altered.\n訳: 記録の説明できない欠落から、複数の請求書が改ざんされていたのではないかという疑いが監査担当者の間に生じた。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:90-93",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text_sha256": "32d83e504c27a520e0b36ba4e11d9a8c5ef76a87d54031e3169e6c3a9f93653f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・regard 〈person/thing〉 with suspicion\n用途: 人や物事をすぐには信用せず、疑いの目で見ることを表す。\n例: Residents regarded the sudden policy change with suspicion.\n訳: 住民たちは突然の方針変更を疑いの目で見た。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:118-121",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text_sha256": "5497644993570a2b335a335ba892b80c139967204abf5131200d90cb314b04d2",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a suspicion of a smile\n用途: はっきり表れるほどではない、かすかな兆しを描写する。\n例: There was a suspicion of a smile in her reply.\n訳: 彼女の返事にはかすかな笑みが感じられた。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:123-126",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text_sha256": "c7a5570858c47f49a650f0a201835a9a20a2a52039ba5905838bbb047de591e4",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a suspicion of truth\n用途: 話や印象に真実味がかすかに感じられることを表す。\n例: The old tale had a suspicion of truth in it.\n訳: その古い物語には、どこか真実味が感じられた。"
      },
      {
        "id": "core_image:001",
        "kind": "core_image",
        "location": "line:19",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "505f789e1258e8153fc5f32a9aa96db957214900b5d0518eadd02cb5a43dbfd5",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "学習上は「確証のない段階で、ある事柄が真実かもしれないと考える」という見立てを中心にする。人の犯罪・不正を疑う用法はその具体例であり、suspicion that ... の節には別の出来事や状態も続く。人や物事を信用できず疑いの目で見る用法は、対象への不信・警戒という態度に焦点を置く。a suspicion of a smile / truth は「ごく少量・かすかな兆し」を表す形式的な比喩用法。この整理は学習上の目安で、全用法が一つの語源的意味を共有するという主張ではない。"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "b561ea930acbab5b5a5e325eae5e2df3fcade6873029ee05904849aec2f08562",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "確証がない段階で、ある事柄が真実かもしれないと考えることを表す。人が犯罪・不正をした可能性への疑いもこの意味に含む。Oxfordは犯罪・不正の疑いでは可算・不可算の両用法を、命題の真偽については可算用法を記している。"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:80",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text_sha256": "62f13286ceef0255b3030d06b5ffc8a75c1ab24b0d3212f7e7e859198a106f3d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "人や物事を十分に信用できず、疑いの目で見る態度を表す。ある事柄が真実かどうかについての見立てを表す語義1とは異なり、対象への不信や警戒に焦点を置く。"
      },
      {
        "id": "definition:003",
        "kind": "definition",
        "location": "line:108",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text_sha256": "d560545f0112c5f05bb2ff715b6b7c54ca25f2203287eed670e2e3e06c2ddf00",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "ものがごく少量、またはかすかな兆候として感じられることを表す。通常 a suspicion of ... の形で使われる。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text_sha256": "d00a67a5c57d1c442fa0e09c8b5bee7a410b577b50e062aa8e016b620cc1b522",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "suspicion は中英語を経て、アングロフランス語・古フランス語からラテン語系の形へさかのぼる。辞書によってラテン語形は suspicio、suspectio、suspectio(n-) と記され、中継経路の説明にも差がある。Merriam-Webster は suspicere「疑う」に由来すると説明している。"
      },
      {
        "id": "frequency:001",
        "kind": "frequency",
        "location": "line:29",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "223f0f3bb105d64687ce0ff83ae044846c2f48c7a55d9d015dbc0ce12503d473",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈8/10〉"
      },
      {
        "id": "frequency:002",
        "kind": "frequency",
        "location": "line:82",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text_sha256": "4c83f924416ef4455522dc0ab9ad637bb8820d1ecc7c146513681f28e8bd4b71",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈7/10〉"
      },
      {
        "id": "frequency:003",
        "kind": "frequency",
        "location": "line:110",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text_sha256": "c9f89b3d40a42341908558a5512ad7d34bbc108cc33b512e22b76f6557469962",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈2/10〉"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "f590c4ce261f0f2c95a2d51f0692869be134c0e72e90be5e51a5fea29f8f0d41",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "suspicion that 〈clause〉＝～ではないかという疑い"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "f1bc3e6c4a16095942531c6a8995bb2706ec98945fd4c6e6995fa17235e91d2f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "have a suspicion that 〈clause〉＝～ではないかという疑いを抱く"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "af1bfa8f881d59a06fd5c7c9b0baf2b4eff153b4377633abd23761301622939f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "arouse 〈person〉's suspicions that 〈clause〉＝〈人〉に～ではないかという疑いを起こさせる"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "893dc037b06ef4b525182b1516299b8dedce550d3b1c92c7340cb457f492e662",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "raise some suspicion among 〈people〉 that 〈clause〉＝〈人々〉の間に～ではないかという疑いを生じさせる"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "c1a93b829562619617f0e307761530b6439a7564c45fcf30038f754f570c3b0e",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "on suspicion of 〈offence〉＝〈犯罪〉の容疑で"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "e39f4766fd90ce60c8a9769ce54e50ab3e1ec1fb7ba4061614819ca4d2cefcac",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be under suspicion＝疑いをかけられている。"
      },
      {
        "id": "grammar_pattern:007",
        "kind": "grammar_pattern",
        "location": "line:86",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text_sha256": "d09dfc93c859f5e40f1d7298b3b638460e4e3d3ca99714676d96221abea3df99",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "regard 〈person/thing〉 with suspicion＝〈人・物事〉を疑いの目で見る。"
      },
      {
        "id": "grammar_pattern:008",
        "kind": "grammar_pattern",
        "location": "line:114",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text_sha256": "a62441f25e236a505738eab608aad6f206f144a39f2e26aa8e6c3a801f410b1d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a suspicion of 〈a smile〉＝笑みがかすかに感じられること"
      },
      {
        "id": "grammar_pattern:009",
        "kind": "grammar_pattern",
        "location": "line:114",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text_sha256": "003396d78ff59a525cefe046a37b15838b90deb4609d6b505b046b11ebfbe877",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a suspicion of 〈truth〉＝真実味がかすかに感じられること。"
      },
      {
        "id": "narrative:001",
        "kind": "narrative",
        "location": "line:23",
        "section": "＃意味・用法・関連表現",
        "sense": "",
        "text_sha256": "57d94c036a1420c5523fceea9274ca437d4a03b78b9b145ddcfec2626c1ea151",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "この節の各語義・類義語の頻度スコアは、英語全体での遭遇頻度を entry_spec_v5 の10段階基準に照らした編集上の定性的推定である。厳密なコーパス集計値や辞書掲載の数値ではなく、地域・専門・古風な用法を過大評価しない目安として付けている。類義語のスコアは、各項目の「定義」に示す意味に限る。"
      },
      {
        "id": "pronunciation:001",
        "kind": "pronunciation",
        "location": "line:4",
        "section": "＃発音記号",
        "sense": "",
        "text_sha256": "4da6bcc06fc02ee319919d638196f5d5c553562eb2fc5589d4c7245b552f9fe7",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "米: Oxford の米語IPAは /səˈspɪʃn/。Merriam-Webster は sus·pi·cion と3音節に区切り、第2音節に主強勢を示す。両辞書で表記形式が異なる。"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:71-76",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "cf0d4516c9a34face0f595cead9410c4ed75e943e6c435568a25c92e626ec519",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・doubt\n定義: ある事柄の真偽について確信が持てない状態。\n頻度: 〈8/10〉\n違い: doubt は真偽の不確かさを広く表し、suspicion はある事柄が真実かもしれないという見立ても表す。\n例: There was some doubt about whether the meeting had been canceled.\n訳: 会議が中止されたかどうかについて、多少の疑問があった。"
      },
      {
        "id": "synonym:002",
        "kind": "synonym",
        "location": "lines:99-104",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text_sha256": "1c150bc385e3795b204b6cca80c3be324c0d02cdfd093f7c8aff05447728d733",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・distrust\n定義: 信用できない気持ち。Oxfordはこの語を本語義の説明に含めている。\n頻度: 〈8/10〉\n違い: Oxfordは本語義を doubt or distrust と説明し、両語の意味が重なることを示している。\n例: Residents regarded the proposal with distrust.\n訳: 住民たちはその提案を信用しなかった。"
      },
      {
        "id": "synonym:003",
        "kind": "synonym",
        "location": "lines:132-137",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text_sha256": "ae4a9ebce83a0811ed228cb08ccad9ca7b7d374f11e42340dd720a04fe936e4f",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・hint\n定義: Oxfordがこのごく少量・かすかな兆しの語義で挙げる類義語。\n頻度: 〈8/10〉\n違い: Oxfordはhintをこの語義の類義語として挙げ、suspicionの用法をformalと記している。\n例: The tea has a hint of mint.\n訳: そのお茶にはほのかなミントの風味がある。"
      },
      {
        "id": "synonym:004",
        "kind": "synonym",
        "location": "lines:139-144",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text_sha256": "f07947c6fe9b158b6fa167a78c9a16d4346ceeab4108b0ee8756b625632df312",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・trace\n定義: ごくわずかな量や痕跡を表す語。Merriam-Websterは本語義の類義語として挙げている。\n頻度: 〈8/10〉\n違い: Merriam-Websterはsuspicionの本語義をbarely detectable amount or traceと説明し、Oxfordはこの用法をformalとしている。\n例: There was only a trace of smoke in the air.\n訳: 空気中には煙がほんのわずかに漂っていた。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:67",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text_sha256": "461b430971cb11159232ccf0a00700276ca65167a65437914c472c6817670cf6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "on suspicion of theft は「窃盗で有罪になった」ではなく、「窃盗をした疑いを理由に」という意味である。under suspicion も罪が確定した状態を表さない。Merriam-Webster の法律辞典は suspicion を通常、信念に至らない精神状態として説明し、reasonable suspicion の項目に関連づけている。ここでは特定の法域の法的基準を述べない。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "a8c5fd77a34b141a7f2dc5802b13900fd66cb3c0009d59f22674c951763252fe",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・suspicious：形容詞。「疑っている、不信に思っている」、または人に疑いを起こさせる「疑わしい」。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "3649d380df0f8699a142092afab76c921b64e8f66d957a868fde889c841b9517",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・suspiciously：副詞形。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "e70de87e639978c1a71a907c23d8e63c103c719fc8e225a5a2d83cf11aa370c4",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・suspiciousness：名詞形。"
      },
      {
        "id": "word_formation:004",
        "kind": "word_formation",
        "location": "line:15",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "d9c7f4fd2fa57701351f2815515117571ac8101041cbbcf5359ef9870d37be43",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・suspicion（動詞）：他動詞で「～を疑う」。Merriam-Webster では chiefly dialectal とされる。"
      }
    ]
  },
  "specification_sha256": "f0de393d4d064190e23916b2e8bfda25b2b83fd29e14cf52395c894b8539d7e9",
  "source_artifact_sha256": "e90fd78ac088d2024598beed6ae0af6133d299beb74c373437b548466fce7266",
  "normalized_input_sha256": "617921f77a818a5e270c40b2ff469807fdf657752ee81231299a7b17b0a0062d"
}
```
