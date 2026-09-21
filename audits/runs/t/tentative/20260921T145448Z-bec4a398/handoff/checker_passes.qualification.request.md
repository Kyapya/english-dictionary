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
  "input_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "16世紀後半に使われ始めた語で、中世ラテン語 tentativus「試みる性質の、試験的な、暫定的な」から来た。これはラテン語 tentare／temptare「触れて確かめる、試す、試みる」に由来する。「まず試してみる段階」という意味から、まだ十分に固まっていない「暫定的な」と、試みる人の「自信のない、ためらいがちな」へ意味が広がった。attempt、tempt、tentatively、tentativeness は同じラテン語の語族に関係するが、tentative の単純な活用形ではない。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・tentatively：副詞。「暫定的に、仮に」または「ためらいがちに、自信なさそうに」。修飾する内容によって2つの形容詞義に対応する。  "
      },
      {
        "line": 24,
        "text": "・tentativeness：名詞。「暫定性、未確定性」または「ためらい、自信のなさ」。通常は不可算名詞で、性質や態度を表す。  "
      },
      {
        "line": 25,
        "text": "・tentative：名詞転用。「暫定的なもの、仮の項目」。まれで、予約・契約・日程などが確定する前の業務上の項目を指すことがある。  "
      },
      {
        "line": 26,
        "text": "・attempt／tempt：同じラテン語 tentare／temptare にさかのぼる関連語。attempt は「試み」、tempt は現代英語で主に「誘惑する」を表し、tentative の派生語ではない。  "
      }
    ],
    "sense_structure": [
      {
        "line": 37,
        "text": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない"
      },
      {
        "line": 39,
        "text": "【日本語訳・定義】計画、日程、合意、結論、説明、提案、識別などが、現時点では候補として置かれているものの、検討・交渉・確認が終わっておらず、後で変更または撤回される可能性があることを表す。単に「一時的」という期間の短さではなく、内容の確定性がまだ低いことに焦点がある。  "
      },
      {
        "line": 144,
        "text": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な"
      },
      {
        "line": 146,
        "text": "【日本語訳・定義】人の行動、声、表情、返答、提案などが、確信や自信を十分に示さず、様子をうかがいながら慎重に行われることを表す。単に静か・弱いという意味ではなく、失敗や拒否を恐れている、またはまだ慣れていないような不確かさが表れやすい。  "
      },
      {
        "line": 251,
        "text": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目"
      },
      {
        "line": 253,
        "text": "【日本語訳・定義】予約、契約、日程、出演枠などについて、正式な確定や契約が済む前に、仮のものとして記録・扱われる項目を表す。一般会話で広く使う名詞ではなく、複数形 tentatives を含む業務上・事務上の文脈で見られる低頻度用法である。  "
      }
    ],
    "frequency_register": [
      {
        "line": 37,
        "text": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない"
      },
      {
        "line": 41,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 43,
        "text": "【レジスター/領域】標準語で、会話・報道・ビジネス・学術・交渉まで広く使う。特に plan、date、schedule、arrangement、agreement、conclusion、explanation、identification など、後から確認や調整が入り得る名詞と結びつく。  "
      },
      {
        "line": 144,
        "text": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な"
      },
      {
        "line": 148,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 150,
        "text": "【レジスター/領域】標準語で、会話・描写・物語・心理描写・対人場面に広く使う。smile、voice、answer、reply、greeting、knock、step、attempt、gesture など、意志や動作の現れ方を表す語と結びつく。  "
      },
      {
        "line": 251,
        "text": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目"
      },
      {
        "line": 255,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 257,
        "text": "【レジスター/領域】低頻度。イベント予約、放送・興行、契約管理など、仮押さえや契約待ちの項目を区別する実務的な文脈に限られやすい。通常は a tentative booking、a tentative date、a tentative arrangement のように形容詞として言うほうが自然である。  "
      }
    ],
    "usage_notes": [
      {
        "line": 37,
        "text": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない"
      },
      {
        "line": 89,
        "text": "【語法・注意】tentative は「その場しのぎの」「短期間の」と同義ではない。`a tentative date` は期間が短い日付ではなく、まだ変更され得る候補日である。`a tentative agreement` も正式な契約・最終合意とは限らず、`final`、`confirmed`、`settled` などで確定段階を示す。`uncertain` は結果や真偽が不確かなことを広く表すのに対し、tentative は計画・判断などをいったん置いているが確定させていないことに焦点がある。`preliminary` は作業・調査の初期段階であること、`provisional` は正式なものに代わる仮の状態であることを強調しやすい。  "
      },
      {
        "line": 144,
        "text": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な"
      },
      {
        "line": 196,
        "text": "【語法・注意】この意味の tentative は、計画が未確定という語義1と異なり、行為者の態度や動作の仕方を描写する。`a tentative smile` は「仮の笑顔」ではなく、相手の反応を確かめるような笑顔である。`hesitant` は決断・発言・行動をためらうことを直接表す最も近い語、`cautious` は危険や失敗を避けるための用心深さを表し、必ずしも自信のなさを含まない。`tentative steps` は文字どおり歩く場合も、計画・改革への初期行動を比喩的に表す場合もある。  "
      },
      {
        "line": 251,
        "text": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目"
      },
      {
        "line": 273,
        "text": "【語法・注意】この名詞用法は一般的な「仮のもの」の言い換えとして自由に使う語ではない。通常の文章では `a tentative plan`、`a tentative booking` のように形容詞用法を選ぶ。名詞の tentative が必要かどうかは業界の慣行によって異なり、読者に伝わりにくい場合は provisional item、pending booking など具体的な表現で言い換える。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 37,
        "text": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない"
      },
      {
        "line": 47,
        "text": "【コロケーション】"
      },
      {
        "line": 49,
        "text": "・tentative plans for 〈event/activity〉  "
      },
      {
        "line": 50,
        "text": "用途: 予定はあるが、内容や日時がまだ変わる可能性があることを表す。  "
      },
      {
        "line": 51,
        "text": "例: We have tentative plans for a short trip in October.  "
      },
      {
        "line": 52,
        "text": "訳: 私たちは10月に短い旅行をする仮の予定がある。  "
      },
      {
        "line": 54,
        "text": "・a tentative date for 〈event〉  "
      },
      {
        "line": 55,
        "text": "用途: 会議・発売・開始などの日付を候補として置く。  "
      },
      {
        "line": 56,
        "text": "例: The organizers set a tentative date for the conference in early May.  "
      },
      {
        "line": 57,
        "text": "訳: 主催者は会議の開催日を5月初旬の仮の日付として設定した。  "
      },
      {
        "line": 59,
        "text": "・a tentative schedule  "
      },
      {
        "line": 60,
        "text": "用途: 今後の調整で変更され得る予定表を指す。  "
      },
      {
        "line": 61,
        "text": "例: The airline released a tentative schedule for the new route.  "
      },
      {
        "line": 62,
        "text": "訳: その航空会社は新路線の暫定的な運航予定を公表した。  "
      },
      {
        "line": 64,
        "text": "・a tentative agreement/deal  "
      },
      {
        "line": 65,
        "text": "用途: 当事者が大筋で合意したが、最終承認や正式契約がまだ済んでいない状態を表す。  "
      },
      {
        "line": 66,
        "text": "例: The two sides reached a tentative agreement after three days of talks.  "
      },
      {
        "line": 67,
        "text": "訳: 両者は3日間の協議の後、暫定合意に達した。  "
      },
      {
        "line": 69,
        "text": "・tentative conclusions/findings  "
      },
      {
        "line": 70,
        "text": "用途: 調査や分析の途中で得られ、追加の確認で修正され得る結論・結果を表す。  "
      },
      {
        "line": 71,
        "text": "例: The researchers presented their tentative findings at the workshop.  "
      },
      {
        "line": 72,
        "text": "訳: 研究者たちはワークショップで予備的な研究結果を発表した。  "
      },
      {
        "line": 74,
        "text": "・a tentative explanation for 〈phenomenon/problem〉  "
      },
      {
        "line": 75,
        "text": "用途: 現象や問題を説明する仮説を、確定的な説明としてではなく提示する。  "
      },
      {
        "line": 76,
        "text": "例: The team offered a tentative explanation for the sudden drop in demand.  "
      },
      {
        "line": 77,
        "text": "訳: チームは需要が急減したことについて暫定的な説明を示した。  "
      },
      {
        "line": 79,
        "text": "・a tentative identification of 〈person/object〉  "
      },
      {
        "line": 80,
        "text": "用途: 証拠が十分でなく、現段階での仮の同定であることを示す。  "
      },
      {
        "line": 81,
        "text": "例: The police made a tentative identification of the vehicle from the video.  "
      },
      {
        "line": 82,
        "text": "訳: 警察は映像からその車両を暫定的に特定した。  "
      },
      {
        "line": 84,
        "text": "・tentatively approve/accept/identify something  "
      },
      {
        "line": 85,
        "text": "用途: 承認・受諾・特定を行うが、最終確認や条件の充足を残していることを表す。  "
      },
      {
        "line": 86,
        "text": "例: The board tentatively approved the budget pending a legal review.  "
      },
      {
        "line": 87,
        "text": "訳: 取締役会は法務審査を条件として、その予算を暫定承認した。  "
      },
      {
        "line": 144,
        "text": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な"
      },
      {
        "line": 154,
        "text": "【コロケーション】"
      },
      {
        "line": 156,
        "text": "・a tentative smile  "
      },
      {
        "line": 157,
        "text": "用途: 相手の反応をうかがうような、確信のない笑顔を表す。  "
      },
      {
        "line": 158,
        "text": "例: She gave him a tentative smile before entering the unfamiliar room.  "
      },
      {
        "line": 159,
        "text": "訳: 彼女は見慣れない部屋に入る前、彼にためらいがちな笑顔を向けた。  "
      },
      {
        "line": 161,
        "text": "・a tentative answer/reply  "
      },
      {
        "line": 162,
        "text": "用途: 答えを断定せず、自信がないまま返すことを表す。  "
      },
      {
        "line": 163,
        "text": "例: He gave a tentative answer because he had not checked the figures.  "
      },
      {
        "line": 164,
        "text": "訳: 彼は数字を確認していなかったので、自信のない返答をした。  "
      },
      {
        "line": 166,
        "text": "・a tentative voice/tone  "
      },
      {
        "line": 167,
        "text": "用途: 声や口調にためらい・不確かさが表れていることを表す。  "
      },
      {
        "line": 168,
        "text": "例: “Perhaps we should wait,” she said in a tentative voice.  "
      },
      {
        "line": 169,
        "text": "訳: 「待ったほうがよいかもしれません」と、彼女はためらいがちな声で言った。  "
      },
      {
        "line": 171,
        "text": "・a tentative knock on 〈door〉  "
      },
      {
        "line": 172,
        "text": "用途: 在室や反応を確かめるように、強く決め込まずノックすることを表す。  "
      },
      {
        "line": 173,
        "text": "例: There was a tentative knock on the office door.  "
      },
      {
        "line": 174,
        "text": "訳: オフィスのドアをおそるおそるノックする音がした。  "
      },
      {
        "line": 176,
        "text": "・take tentative steps towards 〈goal/change〉  "
      },
      {
        "line": 177,
        "text": "用途: 目標や変化に向けて、確信はないが最初の行動を始めることを表す。  "
      },
      {
        "line": 178,
        "text": "例: The company is taking tentative steps toward reducing its use of plastic.  "
      },
      {
        "line": 179,
        "text": "訳: その会社はプラスチックの使用を減らすための最初の一歩を慎重に踏み出している。  "
      },
      {
        "line": 181,
        "text": "・make a tentative attempt to do something  "
      },
      {
        "line": 182,
        "text": "用途: 成功の確信はないが、試しに行動を起こすことを表す。  "
      },
      {
        "line": 183,
        "text": "例: The child made a tentative attempt to join the other players.  "
      },
      {
        "line": 184,
        "text": "訳: その子どもは、ほかの遊び仲間に加わろうとおそるおそる試みた。  "
      },
      {
        "line": 186,
        "text": "・be tentative about 〈doing something〉  "
      },
      {
        "line": 187,
        "text": "用途: 何かをすることに自信がなく、決めかねている状態を表す。  "
      },
      {
        "line": 188,
        "text": "例: She was tentative about speaking up in front of the whole team.  "
      },
      {
        "line": 189,
        "text": "訳: 彼女はチーム全員の前で発言することをためらっていた。  "
      },
      {
        "line": 191,
        "text": "・tentatively suggest/ask something  "
      },
      {
        "line": 192,
        "text": "用途: 相手の反応を見ながら、強く主張せずに提案・質問することを表す。  "
      },
      {
        "line": 193,
        "text": "例: He tentatively suggested moving the meeting to Friday.  "
      },
      {
        "line": 194,
        "text": "訳: 彼は会議を金曜日に移してはどうかと、ためらいがちに提案した。  "
      },
      {
        "line": 251,
        "text": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目"
      },
      {
        "line": 261,
        "text": "【コロケーション】"
      },
      {
        "line": 263,
        "text": "・list the dates as tentatives  "
      },
      {
        "line": 264,
        "text": "用途: 契約や正式確認が済んでいない日程を仮の枠として記録する。  "
      },
      {
        "line": 265,
        "text": "例: The theater listed the autumn dates as tentatives while it waited for the contracts.  "
      },
      {
        "line": 266,
        "text": "訳: その劇場は契約を待つ間、秋の日程を暫定枠として記録した。  "
      },
      {
        "line": 268,
        "text": "・hold a date as a tentative  "
      },
      {
        "line": 269,
        "text": "用途: 日程を正式決定前の仮押さえとして扱う。  "
      },
      {
        "line": 270,
        "text": "例: The producer asked us to hold the date as a tentative until Friday.  "
      },
      {
        "line": 271,
        "text": "訳: プロデューサーは、金曜日まではその日を仮押さえとしておくよう私たちに頼んだ。  "
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
  "source_artifact_sha256": "73787b3811419d4af99b6764bcacbf9685ac18522d5e2b856009599ce8e20810",
  "normalized_input_sha256": "7a5370235aef5b90d2926ef11e836a3b49897a6a1f463dfacb2ee22e5e8dbc79"
}
```
