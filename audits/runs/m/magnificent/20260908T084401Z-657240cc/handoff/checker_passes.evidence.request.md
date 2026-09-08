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
- 入力は `evidence_context_v1` とし、対象claimに関係するsource、fact、source union、claim unit、`source_supports` だけを含む。`source_inventory_sha256`、`source_first_artifact_sha256`、本文hashの一致を機械検証済みでなければ開始しない。
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


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "evidence",
  "taxonomy_ids": [
    "evidence_claim_mismatch"
  ],
  "specification": "prompts/check_pass_evidence_v6.md",
  "input_body_sha256": "258c1b3a17708126df77cb8e5db1556a9e738d56dd4183d8ccca00569461cdb7",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米: /mæɡˈnɪfəsənt/｜英: /mæɡˈnɪfɪsənt/。4音節で、第2音節に主強勢がある。米語では第3音節の母音が /ə/、英語では /ɪ/ と表記されることが多い。語末の `-cent` は /sent/ ではなく弱く /sənt/ と発音する。  "
      }
    ],
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "中英語期に古フランス語 `magnificent` またはラテン語 `magnificent-` を経て入り、ラテン語 `magnificus`「偉大なことを行う、壮麗な」にさかのぼる。`magnus`「大きい、偉大な」と `facere`「作る、行う」に関係し、もともとの「偉大なことを行う」という評価が、現在の「壮麗な」「すばらしい」につながっている。`magnitude`「大きさ、重大さ」や `magnify`「拡大する、誇張する」は同じ `magn-` の語族である。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・`magnificence`（名詞）— 壮麗さ、すばらしさ。建物・景観などの威容にも、行為・成果のすばらしさにも使う。  "
      },
      {
        "line": 24,
        "text": "・`magnificently`（副詞）— 壮麗に、見事に、すばらしく。`perform magnificently`「見事に演じる」のように動作の出来も評価する。  "
      }
    ],
    "core_image": [],
    "sense_structure": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 30,
        "text": "【日本語訳・定義】建物、景色、部屋、衣装、動物などが、規模、美しさ、豪華さ、威厳によって見る人に強い感銘を与えることを表す。単に大きいだけでなく、目を見張るほど見事だという肯定的評価を含む。  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 115,
        "text": "【日本語訳・定義】成果、演技、仕事、行為、機会、出来事などの質や価値が非常に高く、強く称賛したくなることを表す。外見の壮麗さを必要とせず、能力、出来、効果、経験の満足度などを高く評価する。単独の `Magnificent!` は「見事だ」「すばらしい」という感嘆になる。  "
      }
    ],
    "frequency_register": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 32,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 34,
        "text": "【レジスター/領域】標準語。日常会話、旅行・芸術・建築の描写、報道、文学的な文章まで広く使う。`beautiful` より評価が強く、やや高揚した響きを持つことがある。  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 117,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 119,
        "text": "【レジスター/領域】標準語。やや強く高揚した称賛で、会話、批評、スポーツ、報道などに使う。日常会話では `great` や `excellent` のほうが中立的で頻繁である。  "
      }
    ],
    "frames": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 36,
        "text": "【文法パターン】`a magnificent + 〈建物・景色・物〉`＝壮麗な～／`〈建物・景色・物〉 + be/look/seem magnificent`＝～が壮麗である・壮麗に見える／`a magnificent view of 〈場所・景色〉`＝〈場所・景色〉のすばらしい眺め  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 121,
        "text": "【文法パターン】`a magnificent + 〈成果・演技・仕事・機会〉`＝すばらしい～／`〈成果・演技・仕事〉 + be/seem magnificent`＝～が見事である／`do/play/perform magnificently`＝見事に行う・演じる／`Magnificent!`＝見事だ・すばらしい  "
      }
    ],
    "collocations_examples": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 38,
        "text": "【コロケーション】"
      },
      {
        "line": 40,
        "text": "・`a magnificent building/palace`  "
      },
      {
        "line": 41,
        "text": "用途: 規模、美しさ、威厳によって強い印象を与える建築物を表す。  "
      },
      {
        "line": 42,
        "text": "例: The restored palace is a magnificent example of eighteenth-century architecture.  "
      },
      {
        "line": 43,
        "text": "訳: 修復されたその宮殿は、18世紀建築の壮麗な一例である。  "
      },
      {
        "line": 45,
        "text": "・`a magnificent view of 〈場所・景色〉`  "
      },
      {
        "line": 46,
        "text": "用途: 広がりや美しさが際立ち、見る人を感動させる眺めを表す。  "
      },
      {
        "line": 47,
        "text": "例: From the terrace, we had a magnificent view of the snow-covered mountains.  "
      },
      {
        "line": 48,
        "text": "訳: テラスからは、雪に覆われた山々のすばらしい眺めが広がっていた。  "
      },
      {
        "line": 50,
        "text": "・`a magnificent 〈animal/bird〉`  "
      },
      {
        "line": 51,
        "text": "用途: 動物の大きさ、美しさ、威厳のある姿を称賛する。  "
      },
      {
        "line": 52,
        "text": "例: A magnificent eagle circled above the valley.  "
      },
      {
        "line": 53,
        "text": "訳: 一羽の堂々たるワシが谷の上空を旋回していた。  "
      },
      {
        "line": 55,
        "text": "・`look magnificent in 〈服・色〉`  "
      },
      {
        "line": 56,
        "text": "用途: ある服装や色によって、人が非常に美しく堂々として見えることを表す。  "
      },
      {
        "line": 57,
        "text": "例: She looked magnificent in the deep blue gown.  "
      },
      {
        "line": 58,
        "text": "訳: 彼女は濃い青のドレスをまとい、実に華やかで堂々として見えた。  "
      },
      {
        "line": 60,
        "text": "・`a magnificent interior/display`  "
      },
      {
        "line": 61,
        "text": "用途: 室内装飾や展示が豪華で、視覚的に強い感銘を与えることを表す。  "
      },
      {
        "line": 62,
        "text": "例: Visitors stopped to admire the cathedral's magnificent interior.  "
      },
      {
        "line": 63,
        "text": "訳: 来訪者たちは足を止めて、その大聖堂の壮麗な内部を眺めた。  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 123,
        "text": "【コロケーション】"
      },
      {
        "line": 125,
        "text": "・`a magnificent achievement`  "
      },
      {
        "line": 126,
        "text": "用途: 困難さや規模を踏まえて、成果を非常に高く評価する。  "
      },
      {
        "line": 127,
        "text": "例: Completing the bridge ahead of schedule was a magnificent achievement.  "
      },
      {
        "line": 128,
        "text": "訳: 予定より早く橋を完成させたことは、見事な偉業だった。  "
      },
      {
        "line": 130,
        "text": "・`a magnificent performance`  "
      },
      {
        "line": 131,
        "text": "用途: 演技、演奏、競技などの出来が極めて優れていることを表す。  "
      },
      {
        "line": 132,
        "text": "例: The violinist gave a magnificent performance in the final movement.  "
      },
      {
        "line": 133,
        "text": "訳: そのバイオリニストは最終楽章で見事な演奏を披露した。  "
      },
      {
        "line": 135,
        "text": "・`do a magnificent job`  "
      },
      {
        "line": 136,
        "text": "用途: 人や組織が仕事を非常にうまく成し遂げたことを称賛する。  "
      },
      {
        "line": 137,
        "text": "例: The rescue team did a magnificent job under dangerous conditions.  "
      },
      {
        "line": 138,
        "text": "訳: 救助隊は危険な状況下で実に見事な働きをした。  "
      },
      {
        "line": 140,
        "text": "・`a magnificent opportunity`  "
      },
      {
        "line": 141,
        "text": "用途: 価値や可能性が非常に大きい機会を強く肯定的に評価する。  "
      },
      {
        "line": 142,
        "text": "例: The scholarship gave her a magnificent opportunity to study abroad.  "
      },
      {
        "line": 143,
        "text": "訳: その奨学金は、彼女に留学するすばらしい機会を与えた。  "
      },
      {
        "line": 145,
        "text": "・`feel magnificent`  "
      },
      {
        "line": 146,
        "text": "用途: 心身の調子が非常によく、気分がすばらしいことを表す。  "
      },
      {
        "line": 147,
        "text": "例: After a full night's sleep, I felt magnificent.  "
      },
      {
        "line": 148,
        "text": "訳: 一晩ぐっすり眠った後、私は最高の気分だった。  "
      },
      {
        "line": 150,
        "text": "・`Magnificent!`  "
      },
      {
        "line": 151,
        "text": "用途: 出来事、成果、演技などに対する強い称賛を単独で表す。  "
      },
      {
        "line": 152,
        "text": "例: “We finished the repairs.” “Magnificent! We can reopen tomorrow.”  "
      },
      {
        "line": 153,
        "text": "訳: 「修理が終わりました」「すばらしい！ 明日には再開できる」  "
      }
    ],
    "usage_notes": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 65,
        "text": "【語法・注意】`magnificent` は限定用法にも叙述用法にも使える。外観について使うと、「きれいな」だけでなく、規模、豪華さ、威厳などが生む強い感銘まで表す。人に使う場合、`She looks magnificent.` のように外見を称賛できるが、`a magnificent person` は文脈により語義2の人格・力量への高い評価にもなる。比較変化は文法上可能だが、通常は `more/most magnificent` を用い、絶対的な称賛として原級で使うことも多い。  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 155,
        "text": "【語法・注意】語義2では、対象の外観ではなく質・出来・価値を評価する。`a magnificent performance` は演技や演奏が非常に優れていたという意味であり、必ずしも豪華な舞台だったという意味ではない。`feel magnificent` は「堂々として感じる」ではなく「気分・体調が最高だ」という読みになる。`magnificent` は強い称賛なので、日常の小さな良さに使うと意図的に大げさ、ユーモラス、または熱のこもった響きになることがある。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 28,
        "text": "1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な"
      },
      {
        "line": 67,
        "text": "【類義語】"
      },
      {
        "line": 69,
        "text": "・splendid  "
      },
      {
        "line": 70,
        "text": "定義: 見た目、質、成果などが非常にすばらしく、称賛に値する。  "
      },
      {
        "line": 71,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 72,
        "text": "違い: `splendid` は外観にも出来にも広く使える。`magnificent` は特に壮大さ、豪華さ、強い感銘を伴いやすい。  "
      },
      {
        "line": 73,
        "text": "例: The hall was decorated with splendid tapestries.  "
      },
      {
        "line": 74,
        "text": "訳: その広間は見事なタペストリーで飾られていた。  "
      },
      {
        "line": 76,
        "text": "・majestic  "
      },
      {
        "line": 77,
        "text": "定義: 王侯のような威厳や堂々とした壮大さを感じさせる。  "
      },
      {
        "line": 78,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 79,
        "text": "違い: `majestic` は威厳と堂々とした姿に焦点を置く。`magnificent` は威厳がなくても豪華さや美しさによる感銘を表せる。  "
      },
      {
        "line": 80,
        "text": "例: We watched the majestic mountains turn red at sunset.  "
      },
      {
        "line": 81,
        "text": "訳: 私たちは雄大な山々が夕日に赤く染まるのを眺めた。  "
      },
      {
        "line": 83,
        "text": "・grand  "
      },
      {
        "line": 84,
        "text": "定義: 規模、設計、外観が大きく立派で、重要さや格式を感じさせる。  "
      },
      {
        "line": 85,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 86,
        "text": "違い: `grand` は規模や格式を中心に表し、ときに誇張された大げささも含む。`magnificent` は話者の強い称賛をより直接に示す。  "
      },
      {
        "line": 87,
        "text": "例: A grand staircase led to the reception rooms.  "
      },
      {
        "line": 88,
        "text": "訳: 壮大な階段が応接室へと続いていた。  "
      },
      {
        "line": 90,
        "text": "・glorious  "
      },
      {
        "line": 91,
        "text": "定義: 美しさ、輝かしさ、喜ばしさによって非常にすばらしい。  "
      },
      {
        "line": 92,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 93,
        "text": "違い: `glorious` は光、色、天候などの輝かしさや、体験の喜びを表しやすい。`magnificent` は建物や景観の規模・威容にも強く結びつく。  "
      },
      {
        "line": 94,
        "text": "例: The garden was filled with glorious autumn colors.  "
      },
      {
        "line": 95,
        "text": "訳: 庭は見事な秋の色彩で満ちていた。  "
      },
      {
        "line": 97,
        "text": "【反意語】"
      },
      {
        "line": 99,
        "text": "・unimpressive  "
      },
      {
        "line": 100,
        "text": "定義: 特に感銘を与えず、目立った美点や迫力がない。  "
      },
      {
        "line": 101,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 102,
        "text": "違い: 見る人に与える印象の強さという軸で、`magnificent` が非常に強い肯定的な感銘を表すのに対し、`unimpressive` は感銘を与えないことを表す。  "
      },
      {
        "line": 103,
        "text": "例: The building's plain exterior was rather unimpressive.  "
      },
      {
        "line": 104,
        "text": "訳: その建物の簡素な外観は、あまり印象的ではなかった。  "
      },
      {
        "line": 106,
        "text": "・plain  "
      },
      {
        "line": 107,
        "text": "定義: 装飾や華やかさがなく、簡素な。  "
      },
      {
        "line": 108,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 109,
        "text": "違い: 豪華さ・華やかさという限定された軸で対照をなす。`plain` は必ずしも質が悪いという否定的評価を含まず、`magnificent` の全面的な反対語ではない。  "
      },
      {
        "line": 110,
        "text": "例: The chapel has a plain wooden interior.  "
      },
      {
        "line": 111,
        "text": "訳: その礼拝堂の内部は簡素な木造である。  "
      },
      {
        "line": 113,
        "text": "2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた"
      },
      {
        "line": 157,
        "text": "【類義語】"
      },
      {
        "line": 159,
        "text": "・excellent  "
      },
      {
        "line": 160,
        "text": "定義: 質、能力、出来が非常に高い。  "
      },
      {
        "line": 161,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 162,
        "text": "違い: `excellent` は評価基準に照らして質が高いことを比較的中立に述べる。`magnificent` は話者の感動や熱烈な称賛を強く表す。  "
      },
      {
        "line": 163,
        "text": "例: She submitted an excellent final report.  "
      },
      {
        "line": 164,
        "text": "訳: 彼女は非常に優れた最終報告書を提出した。  "
      },
      {
        "line": 166,
        "text": "・superb  "
      },
      {
        "line": 167,
        "text": "定義: 質や出来が最高水準である。  "
      },
      {
        "line": 168,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 169,
        "text": "違い: `superb` は洗練された出来や卓越した質に焦点を置く。`magnificent` は質に加えて規模や感銘の大きさを含みやすい。  "
      },
      {
        "line": 170,
        "text": "例: The chef prepared a superb meal using local ingredients.  "
      },
      {
        "line": 171,
        "text": "訳: その料理人は地元の食材で最高の料理を用意した。  "
      },
      {
        "line": 173,
        "text": "・outstanding  "
      },
      {
        "line": 174,
        "text": "定義: 同種のものの中で際立って優れている。  "
      },
      {
        "line": 175,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 176,
        "text": "違い: `outstanding` は比較集団の中で抜きん出ていることを示す。`magnificent` は比較対象を明示せず、強い感銘を直接表せる。  "
      },
      {
        "line": 177,
        "text": "例: Her outstanding leadership kept the project on track.  "
      },
      {
        "line": 178,
        "text": "訳: 彼女の卓越した指導力によって、プロジェクトは予定どおり進んだ。  "
      },
      {
        "line": 180,
        "text": "・wonderful  "
      },
      {
        "line": 181,
        "text": "定義: 喜び、満足、感嘆をもたらすほどすばらしい。  "
      },
      {
        "line": 182,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 183,
        "text": "違い: `wonderful` は楽しい経験や好ましい人・物に日常的に使う。`magnificent` はより強く、堂々とした、または劇的な称賛を帯びやすい。  "
      },
      {
        "line": 184,
        "text": "例: We had a wonderful evening with old friends.  "
      },
      {
        "line": 185,
        "text": "訳: 私たちは旧友たちとすばらしい夜を過ごした。  "
      },
      {
        "line": 187,
        "text": "【反意語】"
      },
      {
        "line": 189,
        "text": "・mediocre  "
      },
      {
        "line": 190,
        "text": "定義: 質や能力が平凡で、特に優れていない。  "
      },
      {
        "line": 191,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 192,
        "text": "違い: 質の高さという軸で、`magnificent` が極めて高い評価を表すのに対し、`mediocre` は平均的で期待を満たさない評価を表す。  "
      },
      {
        "line": 193,
        "text": "例: The sequel received mediocre reviews from critics.  "
      },
      {
        "line": 194,
        "text": "訳: その続編は批評家から凡庸だという評価を受けた。  "
      },
      {
        "line": 196,
        "text": "・terrible  "
      },
      {
        "line": 197,
        "text": "定義: 質や出来が非常に悪い。  "
      },
      {
        "line": 198,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 199,
        "text": "違い: 質の評価という軸で、`terrible` は非常に低い側、`magnificent` は非常に高い側を表す。  "
      },
      {
        "line": 200,
        "text": "例: The team gave a terrible performance in the second half.  "
      },
      {
        "line": 201,
        "text": "訳: そのチームは後半にひどい出来のプレーをした。  "
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
    "schema_version": "evidence_context_v1",
    "input_body_sha256": "258c1b3a17708126df77cb8e5db1556a9e738d56dd4183d8ccca00569461cdb7",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "02dfc9f3f8067ea6b05cc37abd71f3227060105459e11dad82d5920efb7f89f0",
    "source_first_artifact_sha256": "681a574947ead18b804096165079a4800c3edc22edfc1d7189d38bc0e6cafbb6",
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
        "id": "S001",
        "locator": "https://dictionary.cambridge.org/dictionary/english/magnificent",
        "source_type": "learner_dictionary",
        "independence_group": "cambridge-university-press",
        "facts": [
          {
            "id": "F001",
            "form": "magnificent",
            "kind": "sense",
            "statement": "Magnificent describes someone or something as extremely good, beautiful, impressive, or deserving admiration.",
            "source_detail": "Main Cambridge adjective definition and learner examples."
          },
          {
            "id": "F002",
            "form": "magnificent",
            "kind": "pronunciation",
            "statement": "Cambridge gives UK /mæɡˈnɪf.ɪ.sənt/ and a US pronunciation with a reduced third-syllable vowel.",
            "source_detail": "UK and US pronunciation panels for the adjective."
          }
        ]
      },
      {
        "id": "S002",
        "locator": "https://www.merriam-webster.com/dictionary/magnificent",
        "source_type": "general_dictionary",
        "independence_group": "merriam-webster",
        "facts": [
          {
            "id": "F003",
            "form": "magnificent",
            "kind": "sense",
            "statement": "Magnificent can mean marked by stately grandeur and lavishness or strikingly beautiful and impressive.",
            "source_detail": "Merriam-Webster adjective senses 2 and 3, including sight, cathedral, and physique examples."
          },
          {
            "id": "F004",
            "form": "magnificent",
            "kind": "sense",
            "statement": "Magnificent can mean exceptionally fine.",
            "source_detail": "Merriam-Webster adjective sense 5 and performance example."
          }
        ]
      },
      {
        "id": "S003",
        "locator": "https://www.collinsdictionary.com/dictionary/english/magnificent",
        "source_type": "general_dictionary",
        "independence_group": "harpercollins",
        "facts": [
          {
            "id": "F006",
            "form": "magnificent",
            "kind": "sense",
            "statement": "Magnificent can mean splendid or impressive in appearance.",
            "source_detail": "Collins British English adjective sense 1."
          },
          {
            "id": "F007",
            "form": "magnificent",
            "kind": "sense",
            "statement": "Magnificent can mean superb, exceptionally good, or very fine.",
            "source_detail": "Collins British and American English quality senses."
          },
          {
            "id": "F009",
            "form": "magnificently",
            "kind": "derived_form",
            "statement": "Magnificently is the adverb derived from magnificent.",
            "source_detail": "Collins derived-forms panel."
          }
        ]
      },
      {
        "id": "S004",
        "locator": "https://www.oxfordlearnersdictionaries.com/definition/english/magnificent",
        "source_type": "learner_dictionary",
        "independence_group": "oxford-university-press",
        "facts": [
          {
            "id": "F010",
            "form": "magnificent",
            "kind": "frame",
            "statement": "Magnificent is an adjective used both before a noun and after be or look for things that are extremely attractive, impressive, or deserving praise.",
            "source_detail": "Oxford definition, building/job examples, and be/look collocation panel."
          },
          {
            "id": "F011",
            "form": "magnificent",
            "kind": "pronunciation",
            "statement": "Oxford lists /mæɡˈnɪfɪsnt/ for both its British and American learner entries.",
            "source_detail": "Oxford pronunciation lines for the adjective."
          },
          {
            "id": "F012",
            "form": "magnificent",
            "kind": "etymology",
            "statement": "Magnificent entered late Middle English through Old French from Latin magnificent-, meaning making great and based on magnus, great.",
            "source_detail": "Oxford Word Origin note."
          }
        ]
      },
      {
        "id": "S005",
        "locator": "https://www.etymonline.com/word/magnificent",
        "source_type": "etymological_dictionary",
        "independence_group": "etymonline",
        "facts": [
          {
            "id": "F013",
            "form": "Magnificent!",
            "kind": "register",
            "statement": "Magnificent is attested as an exclamation expressing enthusiastic admiration by 1704.",
            "source_detail": "Etymonline chronology for the exclamatory use."
          },
          {
            "id": "F014",
            "form": "magnificent",
            "kind": "etymology",
            "statement": "Magnificent comes through Old French from Latin magnificus, literally doing great deeds, combining magnus with a form related to facere.",
            "source_detail": "Etymonline main etymology and morphological analysis."
          }
        ]
      },
      {
        "id": "S006",
        "locator": "https://www.dictionary.com/browse/magnificent",
        "source_type": "general_dictionary",
        "independence_group": "dictionary-com",
        "facts": [
          {
            "id": "F016",
            "form": "magnificence",
            "kind": "derived_form",
            "statement": "Magnificence is the corresponding noun for the quality or state of being magnificent.",
            "source_detail": "Dictionary word-family information cross-checked with Merriam-Webster's magnificence entry."
          },
          {
            "id": "F017",
            "form": "magnificent",
            "kind": "pronunciation",
            "statement": "Dictionary.com distinguishes American /mæɡˈnɪfəsənt/ from British /mæɡˈnɪfɪsənt/.",
            "source_detail": "American and British pronunciation lines."
          },
          {
            "id": "F018",
            "form": "magnificent",
            "kind": "register",
            "statement": "Magnificent is a high-admiration term and can also be used informally in weakened exaggeration.",
            "source_detail": "Dictionary.com synonym-usage note."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "U001",
        "source_fact_ids": [
          "F001",
          "F003",
          "F006",
          "F010"
        ],
        "canonical_statement": "Magnificent has a central adjective sense for visually splendid, grand, beautiful, or impressive people and things.",
        "disposition": "included",
        "rationale": "This is article sense 1."
      },
      {
        "id": "U002",
        "source_fact_ids": [
          "F001",
          "F004",
          "F007",
          "F010"
        ],
        "canonical_statement": "Magnificent has a central evaluative adjective sense meaning exceptionally good, excellent, or deserving high praise.",
        "disposition": "included",
        "rationale": "This is article sense 2."
      },
      {
        "id": "U003",
        "source_fact_ids": [
          "F002",
          "F011",
          "F017"
        ],
        "canonical_statement": "Current pronunciations place stress on the second syllable; sources record /ɪ/ or a reduced /ə/ in the third syllable, with /ə/ prominent in American transcription.",
        "disposition": "included",
        "rationale": "The article reports the major dictionary transcription difference without claiming an absolute regional split."
      },
      {
        "id": "U004",
        "source_fact_ids": [
          "F012",
          "F014"
        ],
        "canonical_statement": "Magnificent came through French from Latin material combining the idea of great with doing or making.",
        "disposition": "included",
        "rationale": "This supports the concise etymology section."
      },
      {
        "id": "U005",
        "source_fact_ids": [
          "F009",
          "F016"
        ],
        "canonical_statement": "Magnificently is the common adverb and magnificence is the common noun in the word family.",
        "disposition": "included",
        "rationale": "Both forms have current learner value and appear in word formation."
      },
      {
        "id": "U006",
        "source_fact_ids": [
          "F013"
        ],
        "canonical_statement": "Magnificent can stand alone as an enthusiastic exclamation of admiration.",
        "disposition": "included",
        "rationale": "The productive exclamation is included under the general evaluative sense."
      },
      {
        "id": "U009",
        "source_fact_ids": [
          "F018"
        ],
        "canonical_statement": "Magnificent is strongly admiring and may sound deliberately exaggerated in informal contexts.",
        "disposition": "included",
        "rationale": "This register distinction is explicitly taught in sense 2."
      }
    ],
    "claim_units": [
      {
        "id": "C001",
        "union_ids": [
          "U001"
        ],
        "subject_form": "magnificent",
        "claim_type": "sense",
        "statement": "Magnificent describes a visually splendid or strongly impressive person or thing.",
        "article_target_ids": [
          "sense_boundary:001",
          "definition:001",
          "grammar_pattern:001",
          "grammar_pattern:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F001",
            "support_summary": "Cambridge directly gives beautiful and impressive evaluation."
          },
          {
            "source_fact_id": "F003",
            "support_summary": "Merriam-Webster directly gives grandeur and striking appearance."
          },
          {
            "source_fact_id": "F006",
            "support_summary": "Collins directly gives impressive appearance."
          },
          {
            "source_fact_id": "F010",
            "support_summary": "Oxford attests adjective frames with building and appearance examples."
          }
        ]
      },
      {
        "id": "C002",
        "union_ids": [
          "U002"
        ],
        "subject_form": "magnificent",
        "claim_type": "sense",
        "statement": "Magnificent evaluates a result, performance, job, opportunity, or experience as exceptionally good.",
        "article_target_ids": [
          "sense_boundary:002",
          "definition:002",
          "grammar_pattern:004",
          "collocation:006",
          "collocation:007",
          "collocation:008",
          "collocation:009"
        ],
        "source_supports": [
          {
            "source_fact_id": "F001",
            "support_summary": "Cambridge directly gives the extremely good sense."
          },
          {
            "source_fact_id": "F004",
            "support_summary": "Merriam-Webster directly gives exceptionally fine."
          },
          {
            "source_fact_id": "F007",
            "support_summary": "Collins directly gives superb or very fine."
          },
          {
            "source_fact_id": "F010",
            "support_summary": "Oxford attests deserving praise and magnificent job."
          }
        ]
      },
      {
        "id": "C003",
        "union_ids": [
          "U003"
        ],
        "subject_form": "magnificent",
        "claim_type": "pronunciation",
        "statement": "Magnificent bears second-syllable stress and current dictionaries transcribe the third vowel as /ɪ/ or reduced /ə/.",
        "article_target_ids": [
          "pronunciation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F002",
            "support_summary": "Cambridge provides current UK and US audio/transcription panels."
          },
          {
            "source_fact_id": "F011",
            "support_summary": "Oxford records the /ɪ/ transcription in both learner varieties."
          },
          {
            "source_fact_id": "F017",
            "support_summary": "Dictionary.com explicitly records the US and UK transcription difference."
          }
        ]
      },
      {
        "id": "C004",
        "union_ids": [
          "U004"
        ],
        "subject_form": "magnificent",
        "claim_type": "etymology",
        "statement": "Magnificent entered through French from Latin material meaning making or doing great things.",
        "article_target_ids": [
          "etymology:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F012",
            "support_summary": "Oxford directly supplies French, Latin, and magnus history."
          },
          {
            "source_fact_id": "F014",
            "support_summary": "Etymonline supplies the Latin morphological analysis."
          }
        ]
      },
      {
        "id": "C005",
        "union_ids": [
          "U005"
        ],
        "subject_form": "magnificently",
        "claim_type": "derived_form",
        "statement": "Magnificently is the productive adverb derived from magnificent.",
        "article_target_ids": [
          "word_formation:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F009",
            "support_summary": "Collins explicitly lists magnificently as the derived adverb."
          }
        ]
      },
      {
        "id": "C006",
        "union_ids": [
          "U005"
        ],
        "subject_form": "magnificence",
        "claim_type": "derived_form",
        "statement": "Magnificence is the common noun for the quality or state of being magnificent.",
        "article_target_ids": [
          "word_formation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F016",
            "support_summary": "Dictionary and Merriam-Webster word-family information support magnificence."
          }
        ]
      },
      {
        "id": "C007",
        "union_ids": [
          "U006"
        ],
        "subject_form": "Magnificent!",
        "claim_type": "frame",
        "statement": "Magnificent can be used alone as an enthusiastic exclamation of approval.",
        "article_target_ids": [
          "grammar_pattern:007",
          "collocation:011"
        ],
        "source_supports": [
          {
            "source_fact_id": "F013",
            "support_summary": "Etymonline directly records the enthusiastic exclamation."
          }
        ]
      },
      {
        "id": "C008",
        "union_ids": [
          "U009"
        ],
        "subject_form": "magnificent",
        "claim_type": "register",
        "statement": "Magnificent is strongly admiring and can sound intentionally exaggerated for a small everyday matter.",
        "article_target_ids": [
          "register:002",
          "usage_note:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F018",
            "support_summary": "Dictionary.com directly notes high admiration and informal weak exaggeration."
          }
        ]
      }
    ]
  },
  "specification_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
  "source_artifact_sha256": "681a574947ead18b804096165079a4800c3edc22edfc1d7189d38bc0e6cafbb6",
  "normalized_input_sha256": "1f328c889077dbb1fe399d890f2a4e90fed95b079124e3c6196322f275b0186b"
}
```
