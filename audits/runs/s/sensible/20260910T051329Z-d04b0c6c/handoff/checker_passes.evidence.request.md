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
  "input_body_sha256": "dce1e8375f2e9709647eb4c0fd89fa016895cec32363a81b3950d8cdb28a2078",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米・英: /ˈsensəbl/。3音節で、第1音節に主強勢がある。第1音節の /sen/ を明瞭に発音し、第2音節は弱い /sə/、語尾は /bəl/ と続ける。強勢を後ろに移して「センシブゥル」のように発音しない。  "
      }
    ],
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "中英語後期に、古フランス語 sensible またはラテン語 sensibilis「感じ取れる、知覚できる」から英語に入った。ラテン語 sensibilis は sensus「感覚・知覚」に関係し、さらに sentire「感じる」にさかのぼる。  "
      },
      {
        "line": 20,
        "text": "もともとの「感覚で捉えられる」という意味から、「心で気づいている」、さらに「道理をわきまえて適切に判断する」という意味へ広がった。衣服についての「実用的な」という用法は後の発達で、語源上の意味をそのまま現代の各用法に当てはめない。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "・sensibly：副詞。「分別をもって、現実的に、適切に」。判断や行動の仕方を表す。  "
      },
      {
        "line": 25,
        "text": "・sensibleness：名詞。「分別のあること、現実的であること」。sensible より使用頻度が低い。  "
      },
      {
        "line": 26,
        "text": "・insensible：接頭辞 in- を伴う関連語。「感じない、意識がない、気づかない」。sensible のすべての意味の単純な反意語ではない。  "
      },
      {
        "line": 27,
        "text": "・sensitive、sensibility：同じラテン語の感覚・知覚の語族に属する関連語。ただし、sensitive は「影響を受けやすい・敏感な」、sensibility は「感受性・分別」という別の語として覚える。  "
      }
    ],
    "core_image": [
      {
        "line": 29,
        "text": "＃コアイメージ"
      },
      {
        "line": 31,
        "text": "「感覚・理解・判断を通して、対象をきちんと捉える」。この広い核から、対象を理解して妥当な判断をする用法、実用性を優先して選ぶ用法、対象が感覚や理解に届く用法、刺激を感覚として受け取る用法、事実や感情を意識に受け取る用法が生じる。  "
      },
      {
        "line": 32,
        "text": "1の「対象を理解して妥当な判断をする」から、分別のある・道理にかなった・現実的なという意味になる。  "
      },
      {
        "line": 33,
        "text": "2の「実用性を優先して選ぶ」から、衣服や靴などが実用的な、実用本位のという意味になる。  "
      },
      {
        "line": 34,
        "text": "3の「対象が感覚・理解に届く」から、差や変化などが感じ取れる、はっきりしたという意味になる。  "
      },
      {
        "line": 35,
        "text": "4の「外部刺激を感覚として受け取る」から、痛みや熱などを感じ取れるという意味になる。  "
      },
      {
        "line": 36,
        "text": "5の「事実・感情を意識に受け取る」から、事実や恩恵などを意識している、深く感じているという意味になる。  "
      }
    ],
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】感情だけで決めず、理由・経験・実際の条件を考えて、適切で無理のない判断や行動をすることを表す。人にも、考え・助言・計画・解決策などにも使い、話し手が妥当だと評価する含みがある。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 163,
        "text": "【日本語訳・定義】衣服・靴・かばんなどが、流行や見た目よりも、歩きやすさ・丈夫さ・防寒性などの実用性を重視して作られたり選ばれたりしていることを表す。必ずしも醜い、古い、または質が低いという意味ではない。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 232,
        "text": "【日本語訳・定義】差・変化・増減・量などが、感覚や判断によって認識できる程度にはっきりしていることを表す。現代の一般会話での「分別のある」という意味より形式的で、sensible difference や sensible increase のように、無視できない程度を述べる。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 312,
        "text": "【日本語訳・定義】痛み・熱・光などの外部刺激を、感覚器官や身体で受け取る能力があることを表す。現代の一般英語では sensitive to が普通で、sensible to は古風・形式的または専門的に響く。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 373,
        "text": "【日本語訳・定義】事実・危険・義務・誤り・親切などを心で認識し、強く意識していることを表す。通常 sensible of 〈名詞〉の形で使い、現代の会話では aware of、conscious of、grateful for などが自然なことが多い。  "
      }
    ],
    "frequency_register": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 44,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 46,
        "text": "【レジスター/領域】標準語で、会話にも文章にも使える基本語。practical は実行可能性、reasonable は道理・公平さ、rational は感情を抑えた論理性に焦点を置きやすいのに対し、sensible は日常の分別と現実感をまとめて表す。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 165,
        "text": "【頻度】〈6/10〉  "
      },
      {
        "line": 167,
        "text": "【レジスター/領域】標準語で、日常会話にも使う。sensible shoes は特に定着した組み合わせで、長時間歩く場面などに適した、派手さより快適さを優先した靴を指す。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 234,
        "text": "【頻度】〈3/10〉  "
      },
      {
        "line": 236,
        "text": "【レジスター/領域】形式的・書き言葉寄りで、一般会話では noticeable、clear、appreciable などが自然なことが多い。辞書によっては「知覚できる」「かなりの」という別項目として扱われる。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 314,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 316,
        "text": "【レジスター/領域】低頻度の形式的・古風な用法。一般学習者が自分の知覚について述べる場合は、通常 be sensitive to 〈刺激〉を使う。sensible to pain は「痛みを感じ取れる」であり、1の「分別のある」とは別の意味である。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 375,
        "text": "【頻度】〈3/10〉  "
      },
      {
        "line": 377,
        "text": "【レジスター/領域】形式的・文学的で、古風な響きがある。sensible of the fact、sensible of one's error、sensible of someone's kindness のように、抽象的な事実や感情を意識していることに使う。  "
      }
    ],
    "frames": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 48,
        "text": "【文法パターン】a sensible person/choice/decision/plan＝分別のある人・妥当な選択・判断・計画／sensible advice＝現実的で適切な助言／be sensible＝分別をもって行動する／be sensible about 〈money・risk・food〉＝〈お金・危険・食事〉について現実的に考える／it is sensible to do ＝～するのが妥当だ／it is sensible for someone to do ＝〈人〉が～するのが妥当だ／the sensible thing to do＝取るべき妥当な行動／be sensible enough to do ＝分別があるので～する。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 169,
        "text": "【文法パターン】sensible shoes/clothes/footwear＝実用的な靴・衣服・履物／a sensible coat＝実用本位のコート／wear/choose sensible clothing＝実用的な服を着る・選ぶ／something is sensible for 〈weather・travel〉＝〈天候・旅行〉に適して実用的だ。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 238,
        "text": "【文法パターン】a sensible difference＝感じ取れる明確な差／a sensible increase/decrease in something＝〈物事〉のかなりはっきりした増加・減少／a sensible change in something＝〈物事〉の認識できる変化／sensible 〈amount・degree〉＝無視できない程度の量・度合い。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 318,
        "text": "【文法パターン】be sensible to 〈pain・heat・light〉＝〈痛み・熱・光〉を感じ取れる／become sensible to 〈stimulus〉＝〈刺激〉を知覚するようになる／sensible to the touch＝触れて感じ取れる。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 379,
        "text": "【文法パターン】be sensible of 〈fact・danger・duty・error〉＝〈事実・危険・義務・誤り〉を意識している／be sensible of 〈kindness・benefit〉＝〈親切・恩恵〉を深く感じている／be deeply/keenly sensible of something＝～を深く・強く意識している／sensible of the fact that 〈節〉＝～という事実を認識している。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 50,
        "text": "【コロケーション】"
      },
      {
        "line": 52,
        "text": "・a sensible decision  "
      },
      {
        "line": 53,
        "text": "用途: 条件や結果を考えたうえで、妥当な判断であることを表す。  "
      },
      {
        "line": 54,
        "text": "例: Taking the earlier train was a sensible decision.  "
      },
      {
        "line": 55,
        "text": "訳: 早い方の電車に乗ったのは妥当な判断だった。  "
      },
      {
        "line": 57,
        "text": "・a sensible approach to 〈problem〉  "
      },
      {
        "line": 58,
        "text": "用途: 問題に対して、現実的で無理のない取り組み方を示す。  "
      },
      {
        "line": 59,
        "text": "例: We need a sensible approach to reducing unnecessary costs.  "
      },
      {
        "line": 60,
        "text": "訳: 不要な費用を減らすには、現実的な取り組み方が必要だ。  "
      },
      {
        "line": 62,
        "text": "・sensible advice  "
      },
      {
        "line": 63,
        "text": "用途: 経験や事情に基づく、実行しやすい助言を表す。  "
      },
      {
        "line": 64,
        "text": "例: Her sensible advice helped me avoid a costly mistake.  "
      },
      {
        "line": 65,
        "text": "訳: 彼女の現実的な助言のおかげで、私は高くつく間違いを避けられた。  "
      },
      {
        "line": 67,
        "text": "・it is sensible to do  "
      },
      {
        "line": 68,
        "text": "用途: ある行動を取るのが分別にかなっていると述べる基本構文。  "
      },
      {
        "line": 69,
        "text": "例: It is sensible to keep a copy of the receipt.  "
      },
      {
        "line": 70,
        "text": "訳: 領収書の写しを保管しておくのが賢明だ。  "
      },
      {
        "line": 72,
        "text": "・it is sensible for someone to do  "
      },
      {
        "line": 73,
        "text": "用途: 特定の人がある行動をするのが妥当だと述べる。  "
      },
      {
        "line": 74,
        "text": "例: It would be sensible for you to check the figures again.  "
      },
      {
        "line": 75,
        "text": "訳: あなたがもう一度数字を確認するのが賢明だろう。  "
      },
      {
        "line": 77,
        "text": "・the sensible thing to do  "
      },
      {
        "line": 78,
        "text": "用途: いくつかの選択肢の中で、最も妥当な行動を指す。  "
      },
      {
        "line": 79,
        "text": "例: The sensible thing to do is wait until the weather improves.  "
      },
      {
        "line": 80,
        "text": "訳: 天候が回復するまで待つのが妥当な行動だ。  "
      },
      {
        "line": 82,
        "text": "・be sensible about 〈issue〉  "
      },
      {
        "line": 83,
        "text": "用途: 問題や資源について、感情的にならず現実的に考える。  "
      },
      {
        "line": 84,
        "text": "例: Please be sensible about how much equipment you bring.  "
      },
      {
        "line": 85,
        "text": "訳: どれだけ機材を持ってくるかは、現実的に考えてください。  "
      },
      {
        "line": 87,
        "text": "・be sensible enough to do  "
      },
      {
        "line": 88,
        "text": "用途: 分別があるため、危険や不利益を避ける行動を取ることを表す。  "
      },
      {
        "line": 89,
        "text": "例: He was sensible enough to ask for help before the problem grew.  "
      },
      {
        "line": 90,
        "text": "訳: 彼は問題が大きくなる前に助けを求めるだけの分別があった。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 171,
        "text": "【コロケーション】"
      },
      {
        "line": 173,
        "text": "・sensible shoes  "
      },
      {
        "line": 174,
        "text": "用途: 流行性よりも歩きやすさや足の保護を重視した靴を表す。  "
      },
      {
        "line": 175,
        "text": "例: Wear sensible shoes because the tour involves a lot of walking.  "
      },
      {
        "line": 176,
        "text": "訳: たくさん歩くツアーなので、歩きやすい靴を履いてください。  "
      },
      {
        "line": 178,
        "text": "・sensible clothing  "
      },
      {
        "line": 179,
        "text": "用途: 天候や活動に合い、実用性を優先した衣服を表す。  "
      },
      {
        "line": 180,
        "text": "例: Pack sensible clothing for the cold and wet conditions.  "
      },
      {
        "line": 181,
        "text": "訳: 寒くて雨の多い状況に合う実用的な服を荷造りしてください。  "
      },
      {
        "line": 183,
        "text": "・sensible footwear  "
      },
      {
        "line": 184,
        "text": "用途: 見た目より機能性を重視した履物を、やや説明的に表す。  "
      },
      {
        "line": 185,
        "text": "例: The guide recommends sensible footwear for the uneven ground.  "
      },
      {
        "line": 186,
        "text": "訳: ガイドは、でこぼこした地面には実用的な履物を勧めている。  "
      },
      {
        "line": 188,
        "text": "・a sensible coat  "
      },
      {
        "line": 189,
        "text": "用途: 防寒・耐久性・天候への対応を重視したコートを表す。  "
      },
      {
        "line": 190,
        "text": "例: I bought a sensible coat rather than a delicate fashion jacket.  "
      },
      {
        "line": 191,
        "text": "訳: 繊細なファッションジャケットではなく、実用的なコートを買った。  "
      },
      {
        "line": 193,
        "text": "・choose sensible clothing  "
      },
      {
        "line": 194,
        "text": "用途: 活動や天候に合わせて、見た目より使いやすさを基準に衣服を選ぶ。  "
      },
      {
        "line": 195,
        "text": "例: Choose sensible clothing for the long flight.  "
      },
      {
        "line": 196,
        "text": "訳: 長時間のフライトには実用的な服を選んでください。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 240,
        "text": "【コロケーション】"
      },
      {
        "line": 242,
        "text": "・a sensible difference  "
      },
      {
        "line": 243,
        "text": "用途: 2つの状態や結果の間に、認識できるほどの差があることを表す。  "
      },
      {
        "line": 244,
        "text": "例: The software update made a sensible difference to the loading time.  "
      },
      {
        "line": 245,
        "text": "訳: ソフトウェアの更新によって、読み込み時間に明らかな違いが出た。  "
      },
      {
        "line": 247,
        "text": "・a sensible increase in something  "
      },
      {
        "line": 248,
        "text": "用途: 数値や量が、認識できる程度に増えたことを形式的に表す。  "
      },
      {
        "line": 249,
        "text": "例: The policy led to a sensible increase in public access.  "
      },
      {
        "line": 250,
        "text": "訳: その政策によって、一般の利用可能性がはっきり増した。  "
      },
      {
        "line": 252,
        "text": "・a sensible reduction in something  "
      },
      {
        "line": 253,
        "text": "用途: 費用・危険・排出量などが、無視できない程度に減ったことを表す。  "
      },
      {
        "line": 254,
        "text": "例: The new process produced a sensible reduction in waste.  "
      },
      {
        "line": 255,
        "text": "訳: 新しい工程によって、廃棄物が明らかに減少した。  "
      },
      {
        "line": 257,
        "text": "・a sensible change in something  "
      },
      {
        "line": 258,
        "text": "用途: 状態や傾向に、認識できるほどの変化が起きたことを述べる。  "
      },
      {
        "line": 259,
        "text": "例: There has been a sensible change in the patient's condition.  "
      },
      {
        "line": 260,
        "text": "訳: 患者の状態には、はっきり分かる変化があった。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 320,
        "text": "【コロケーション】"
      },
      {
        "line": 322,
        "text": "・be sensible to pain  "
      },
      {
        "line": 323,
        "text": "用途: 痛みを感覚として受け取る能力があることを、形式的に表す。  "
      },
      {
        "line": 324,
        "text": "例: The injured area remained sensible to pain after the procedure.  "
      },
      {
        "line": 325,
        "text": "訳: 処置後も、負傷した部位は痛みを感じ取る状態だった。  "
      },
      {
        "line": 327,
        "text": "・be sensible to heat  "
      },
      {
        "line": 328,
        "text": "用途: 熱を感じ取ることができることを述べる。  "
      },
      {
        "line": 329,
        "text": "例: The instrument is sensible to heat from a nearby flame.  "
      },
      {
        "line": 330,
        "text": "訳: その器具は近くの炎から出る熱を感知できる。  "
      },
      {
        "line": 332,
        "text": "・be sensible to light  "
      },
      {
        "line": 333,
        "text": "用途: 光を感知する性質があることを、古風または技術的に表す。  "
      },
      {
        "line": 334,
        "text": "例: The material is sensible to light and should be stored in the dark.  "
      },
      {
        "line": 335,
        "text": "訳: その素材は光を感知する性質があるので、暗所で保管すべきだ。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 381,
        "text": "【コロケーション】"
      },
      {
        "line": 383,
        "text": "・be sensible of 〈fact〉  "
      },
      {
        "line": 384,
        "text": "用途: ある事実を心で認識していることを、形式的に表す。  "
      },
      {
        "line": 385,
        "text": "例: She was sensible of the fact that her decision affected the whole team.  "
      },
      {
        "line": 386,
        "text": "訳: 彼女は、自分の決定がチーム全体に影響するという事実を意識していた。  "
      },
      {
        "line": 388,
        "text": "・be sensible of one's error  "
      },
      {
        "line": 389,
        "text": "用途: 自分の誤りに気づき、それを認識していることを表す。  "
      },
      {
        "line": 390,
        "text": "例: He soon became sensible of his error and apologized.  "
      },
      {
        "line": 391,
        "text": "訳: 彼はすぐに自分の誤りに気づき、謝罪した。  "
      },
      {
        "line": 393,
        "text": "・be sensible of someone's kindness  "
      },
      {
        "line": 394,
        "text": "用途: 人から受けた親切や恩恵を深く感じていることを表す。  "
      },
      {
        "line": 395,
        "text": "例: I am deeply sensible of your kindness during this difficult time.  "
      },
      {
        "line": 396,
        "text": "訳: この困難な時期にあなたが親切にしてくださったことを深く感じています。  "
      },
      {
        "line": 398,
        "text": "・be keenly sensible of something  "
      },
      {
        "line": 399,
        "text": "用途: 危険・責任・苦境などを強く意識していることを、硬い表現で述べる。  "
      },
      {
        "line": 400,
        "text": "例: The volunteers were keenly sensible of the risks involved.  "
      },
      {
        "line": 401,
        "text": "訳: ボランティアたちは、そこに伴う危険を強く意識していた。  "
      }
    ],
    "usage_notes": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 92,
        "text": "【語法・注意】人を主語にした be sensible は「分別をもって行動する」、物事を主語にした a sensible plan は「妥当で現実的な計画」を表す。sensible は必ずしも「賢さ」や高い知能を評価する語ではなく、その場の条件に合った判断をほめる語である。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 198,
        "text": "【語法・注意】この用法では、sensible は人の判断を直接修飾するのではなく、実用性を重視して選ばれた物を評価する。fashionable は「流行している」、comfortable は「快適な」に焦点があり、sensible shoes が必ず fashionable でない、または完全に comfortable であるとは限らない。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 262,
        "text": "【語法・注意】この用法の sensible は「妥当な」という意味ではなく、「感覚や判断に届くほど明らかな」という意味である。ただし、sensible amount は文脈によって「妥当な量」という1の意味にもなるため、差や増減の文脈で理解する。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 337,
        "text": "【語法・注意】現代英語の sensitive to は「刺激を感じやすい」だけでなく、「影響を受けやすい」「気を悪くしやすい」も表せる。一方、sensible to はこの語義では主に感覚的な知覚を述べ、一般的な「敏感な」の言い換えとして自由に使えるわけではない。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 403,
        "text": "【語法・注意】sensible of は「～を意識している」であり、1の sensible「分別のある」とは意味が異なる。sensible to は4の「刺激を感じ取れる」と結びつきやすく、事実・恩恵への意識には sensible of を使う。現代的な文章では aware of や conscious of の方が普通である。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 94,
        "text": "【類義語】"
      },
      {
        "line": 96,
        "text": "・reasonable  "
      },
      {
        "line": 97,
        "text": "定義: 道理にかなった、妥当な、無理のない。  "
      },
      {
        "line": 98,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 99,
        "text": "違い: reasonable は判断・要求・価格などが公平で受け入れやすいことに焦点がある。sensible は現実の結果を考えて適切に行動する分別を強調しやすい。  "
      },
      {
        "line": 100,
        "text": "例: That seems like a reasonable compromise.  "
      },
      {
        "line": 101,
        "text": "訳: それは妥当な妥協案のように思える。  "
      },
      {
        "line": 103,
        "text": "・practical  "
      },
      {
        "line": 104,
        "text": "定義: 実際に役立ち、実行できる、実用的な。  "
      },
      {
        "line": 105,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 106,
        "text": "違い: practical は理論や見た目より実用性・実行可能性に焦点がある。sensible は実用性に加え、状況に応じた判断の適切さも表す。  "
      },
      {
        "line": 107,
        "text": "例: We chose a practical solution that fit the budget.  "
      },
      {
        "line": 108,
        "text": "訳: 私たちは予算に合う実用的な解決策を選んだ。  "
      },
      {
        "line": 110,
        "text": "・rational  "
      },
      {
        "line": 111,
        "text": "定義: 理性や論理に基づく、合理的な。  "
      },
      {
        "line": 112,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 113,
        "text": "違い: rational は感情や衝動ではなく、論理的な理由に基づくことを強調する。sensible の方が日常的で、生活上の分別にも使いやすい。  "
      },
      {
        "line": 114,
        "text": "例: There is no rational reason to reject the proposal.  "
      },
      {
        "line": 115,
        "text": "訳: その提案を拒む合理的な理由はない。  "
      },
      {
        "line": 117,
        "text": "・prudent  "
      },
      {
        "line": 118,
        "text": "定義: 将来の危険や損失を考えて慎重で賢明な。  "
      },
      {
        "line": 119,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 120,
        "text": "違い: prudent は特に危険・費用・将来の結果を避ける慎重さを含み、sensible より硬い。  "
      },
      {
        "line": 121,
        "text": "例: It would be prudent to set aside some emergency savings.  "
      },
      {
        "line": 122,
        "text": "訳: 緊急時のために貯蓄をいくらか取っておくのが賢明だろう。  "
      },
      {
        "line": 124,
        "text": "・wise  "
      },
      {
        "line": 125,
        "text": "定義: 経験や深い理解に基づいて、賢明な。  "
      },
      {
        "line": 126,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 127,
        "text": "違い: wise は長期的な洞察や人生経験まで含むことがある。sensible はもっと身近な状況での現実的な判断に焦点を置く。  "
      },
      {
        "line": 128,
        "text": "例: It was wise to discuss the risks before signing.  "
      },
      {
        "line": 129,
        "text": "訳: 署名する前に危険性を話し合ったのは賢明だった。  "
      },
      {
        "line": 131,
        "text": "・judicious  "
      },
      {
        "line": 132,
        "text": "定義: 判断力があり、慎重で適切な。  "
      },
      {
        "line": 133,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 134,
        "text": "違い: judicious は選択・配分・発言などを慎重に見極めたことを表す硬い語。sensible の方が一般的で親しみやすい。  "
      },
      {
        "line": 135,
        "text": "例: A judicious use of examples can clarify the argument.  "
      },
      {
        "line": 136,
        "text": "訳: 例を適切に使えば、その議論を明確にできる。  "
      },
      {
        "line": 138,
        "text": "【反意語】"
      },
      {
        "line": 140,
        "text": "・silly  "
      },
      {
        "line": 141,
        "text": "定義: 分別を欠いた、ばかげた。  "
      },
      {
        "line": 142,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 143,
        "text": "違い: silly は判断や行動が軽率で、子どもっぽくばかげていることを表す。sensible の「現実を踏まえた分別」と対照的である。  "
      },
      {
        "line": 144,
        "text": "例: It would be silly to ignore the warning.  "
      },
      {
        "line": 145,
        "text": "訳: その警告を無視するのはばかげている。  "
      },
      {
        "line": 147,
        "text": "・foolish  "
      },
      {
        "line": 148,
        "text": "定義: 判断力や分別を欠いた、愚かな。  "
      },
      {
        "line": 149,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 150,
        "text": "違い: foolish は結果を考えない愚かな判断を強く非難する語で、sensible の反対側に位置する。  "
      },
      {
        "line": 151,
        "text": "例: It was foolish to spend all the money at once.  "
      },
      {
        "line": 152,
        "text": "訳: お金を全部一度に使うのは愚かなことだった。  "
      },
      {
        "line": 154,
        "text": "・impractical  "
      },
      {
        "line": 155,
        "text": "定義: 実行しにくく、現実の条件に合わない。  "
      },
      {
        "line": 156,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 157,
        "text": "違い: impractical は計画や提案などの実行可能性の不足に焦点を置く。人の分別全般の反意語ではないが、sensible plan などとは実用性の軸で対照をなす。  "
      },
      {
        "line": 158,
        "text": "例: The design is attractive but impractical for daily use.  "
      },
      {
        "line": 159,
        "text": "訳: そのデザインは魅力的だが、日常使用には実用的でない。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 200,
        "text": "【類義語】"
      },
      {
        "line": 202,
        "text": "・practical  "
      },
      {
        "line": 203,
        "text": "定義: 実際の用途に役立つ、実用的な。  "
      },
      {
        "line": 204,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 205,
        "text": "違い: practical は衣服・道具・計画の実用性を広く表す。sensible は使用場面に合うように選ばれたという判断の含みを持ちやすい。  "
      },
      {
        "line": 206,
        "text": "例: These practical boots are good for walking in the rain.  "
      },
      {
        "line": 207,
        "text": "訳: この実用的なブーツは雨の中を歩くのに向いている。  "
      },
      {
        "line": 209,
        "text": "・functional  "
      },
      {
        "line": 210,
        "text": "定義: 見た目より機能を果たすことを重視した、機能的な。  "
      },
      {
        "line": 211,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 212,
        "text": "違い: functional はデザインや構造が目的の機能を果たすかに焦点があり、sensible は日常の選択として妥当かを評価する。  "
      },
      {
        "line": 213,
        "text": "例: The clothes are simple but highly functional.  "
      },
      {
        "line": 214,
        "text": "訳: その服はシンプルだが、機能性が非常に高い。  "
      },
      {
        "line": 216,
        "text": "・serviceable  "
      },
      {
        "line": 217,
        "text": "定義: 十分に使える、丈夫で役に立つ。  "
      },
      {
        "line": 218,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 219,
        "text": "違い: serviceable は見た目の魅力より、必要な用途に耐えることを表すやや硬い語。sensible は選択の分別にも使える。  "
      },
      {
        "line": 220,
        "text": "例: The hotel provides clean and serviceable furnishings.  "
      },
      {
        "line": 221,
        "text": "訳: そのホテルは清潔で十分に使える備品を備えている。  "
      },
      {
        "line": 223,
        "text": "・utilitarian  "
      },
      {
        "line": 224,
        "text": "定義: 実用性だけを重視した、実用主義的な。  "
      },
      {
        "line": 225,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 226,
        "text": "違い: utilitarian は装飾性をほとんど考慮しない硬い・批評的な響きがある。sensible は実用的でも、見た目のよさを排除するとは限らない。  "
      },
      {
        "line": 227,
        "text": "例: The building has a plain, utilitarian design.  "
      },
      {
        "line": 228,
        "text": "訳: その建物は簡素で実用本位の設計になっている。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 264,
        "text": "【類義語】"
      },
      {
        "line": 266,
        "text": "・perceptible  "
      },
      {
        "line": 267,
        "text": "定義: 感覚や心によって知覚できる、感じ取れる。  "
      },
      {
        "line": 268,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 269,
        "text": "違い: perceptible は知覚可能性を直接表す硬い語で、sensible のこの用法と最も近い。sensible には「かなりの」という評価が加わることがある。  "
      },
      {
        "line": 270,
        "text": "例: There was a perceptible change in the tone of the discussion.  "
      },
      {
        "line": 271,
        "text": "訳: 議論の雰囲気には感じ取れる変化があった。  "
      },
      {
        "line": 273,
        "text": "・noticeable  "
      },
      {
        "line": 274,
        "text": "定義: 見たり感じたりして気づくことができる、目立つ。  "
      },
      {
        "line": 275,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 276,
        "text": "違い: noticeable は日常的で、目や耳などで気づきやすいことに焦点がある。sensible のこの用法はより形式的で、量や程度にも使いやすい。  "
      },
      {
        "line": 277,
        "text": "例: There was a noticeable improvement in her balance.  "
      },
      {
        "line": 278,
        "text": "訳: 彼女のバランスには目立った改善があった。  "
      },
      {
        "line": 280,
        "text": "・appreciable  "
      },
      {
        "line": 281,
        "text": "定義: はっきり認められる、かなりの、無視できない。  "
      },
      {
        "line": 282,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 283,
        "text": "違い: appreciable は差・量・変化が評価上無視できないことを強調する。sensible と近いが、程度の大きさに焦点を置きやすい。  "
      },
      {
        "line": 284,
        "text": "例: The repair resulted in an appreciable reduction in noise.  "
      },
      {
        "line": 285,
        "text": "訳: 修理によって騒音がかなり減少した。  "
      },
      {
        "line": 287,
        "text": "・marked  "
      },
      {
        "line": 288,
        "text": "定義: はっきりした、顕著な。  "
      },
      {
        "line": 289,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 290,
        "text": "違い: marked は変化や差が目立つことを簡潔に示す。sensible は、認識できる程度に達したことをやや控えめに述べる。  "
      },
      {
        "line": 291,
        "text": "例: The study found a marked difference between the two groups.  "
      },
      {
        "line": 292,
        "text": "訳: その研究は、2つのグループの間に顕著な差があることを見いだした。  "
      },
      {
        "line": 294,
        "text": "【反意語】"
      },
      {
        "line": 296,
        "text": "・imperceptible  "
      },
      {
        "line": 297,
        "text": "定義: 感覚や心では知覚できない、気づけない。  "
      },
      {
        "line": 298,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 299,
        "text": "違い: imperceptible は差や変化が小さすぎて感じ取れないことを表し、sensible の「認識できる」という軸と直接対照をなす。  "
      },
      {
        "line": 300,
        "text": "例: The change in temperature was almost imperceptible.  "
      },
      {
        "line": 301,
        "text": "訳: 気温の変化はほとんど感じ取れないほどだった。  "
      },
      {
        "line": 303,
        "text": "・negligible  "
      },
      {
        "line": 304,
        "text": "定義: 小さすぎて考慮する必要がない、取るに足りない。  "
      },
      {
        "line": 305,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 306,
        "text": "違い: negligible は重要性や影響の小ささに焦点がある。知覚できるかどうかを直接述べる語ではないが、sensible increase などの「無視できない程度」と量の軸で対照をなす。  "
      },
      {
        "line": 307,
        "text": "例: The difference in cost is negligible.  "
      },
      {
        "line": 308,
        "text": "訳: 費用の差は取るに足りない。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 339,
        "text": "【類義語】"
      },
      {
        "line": 341,
        "text": "・sensitive to 〈stimulus〉  "
      },
      {
        "line": 342,
        "text": "定義: 〈刺激〉を感じ取る、またはその影響を受けやすい。  "
      },
      {
        "line": 343,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 344,
        "text": "違い: sensitive to は現代英語で普通の表現で、感覚的な知覚に加えて化学反応・感情・社会的影響にも使える。sensible to は形式的・古風で範囲が狭い。  "
      },
      {
        "line": 345,
        "text": "例: Some people are highly sensitive to bright light.  "
      },
      {
        "line": 346,
        "text": "訳: 明るい光に非常に敏感な人もいる。  "
      },
      {
        "line": 348,
        "text": "・responsive to 〈stimulus〉  "
      },
      {
        "line": 349,
        "text": "定義: 〈刺激〉に反応する、反応を示す。  "
      },
      {
        "line": 350,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 351,
        "text": "違い: responsive to は刺激を感じることより、それに反応や変化が生じることを強調する。sensible to はまず知覚可能性を表す。  "
      },
      {
        "line": 352,
        "text": "例: The sensor is responsive to small changes in pressure.  "
      },
      {
        "line": 353,
        "text": "訳: そのセンサーは圧力の小さな変化にも反応する。  "
      },
      {
        "line": 355,
        "text": "【反意語】"
      },
      {
        "line": 357,
        "text": "・insensible to 〈stimulus〉  "
      },
      {
        "line": 358,
        "text": "定義: 〈刺激〉を感じない、意識しない。  "
      },
      {
        "line": 359,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 360,
        "text": "違い: insensible to は痛み・熱などを知覚できないことを表し、この用法の sensible to と直接対照をなす。  "
      },
      {
        "line": 361,
        "text": "例: The tissue was insensible to light touch.  "
      },
      {
        "line": 362,
        "text": "訳: その組織は軽く触れても感じなかった。  "
      },
      {
        "line": 364,
        "text": "・impervious to 〈stimulus〉  "
      },
      {
        "line": 365,
        "text": "定義: 〈刺激・影響〉を通さず、受け付けない。  "
      },
      {
        "line": 366,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 367,
        "text": "違い: impervious to は単に知覚できないだけでなく、刺激や影響が作用しないことを強く表す。sensible to より遮断の含みが強い。  "
      },
      {
        "line": 368,
        "text": "例: The coating is impervious to heat and moisture.  "
      },
      {
        "line": 369,
        "text": "訳: そのコーティングは熱や湿気を通さない。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 407,
        "text": "【類義語】"
      },
      {
        "line": 409,
        "text": "・aware of something  "
      },
      {
        "line": 410,
        "text": "定義: 〈事実・状況・問題〉に気づいている、知っている。  "
      },
      {
        "line": 411,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 412,
        "text": "違い: aware of は現代英語で最も普通の「認識している」で、感情の深さを必ずしも含まない。sensible of は形式的で、強く感じている含みを持つことがある。  "
      },
      {
        "line": 413,
        "text": "例: Are you aware of the possible consequences?  "
      },
      {
        "line": 414,
        "text": "訳: 起こりうる結果を認識していますか。  "
      },
      {
        "line": 416,
        "text": "・conscious of something  "
      },
      {
        "line": 417,
        "text": "定義: 〈事実・存在・自分の行動〉を意識している。  "
      },
      {
        "line": 418,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 419,
        "text": "違い: conscious of は意識に上っていることや自覚を強調する。sensible of より現代的だが、文脈によっては「気にしている」という含みも出る。  "
      },
      {
        "line": 420,
        "text": "例: She was conscious of every movement in the quiet room.  "
      },
      {
        "line": 421,
        "text": "訳: 彼女は静かな部屋でのあらゆる動きを意識していた。  "
      },
      {
        "line": 423,
        "text": "・cognizant of something  "
      },
      {
        "line": 424,
        "text": "定義: 〈事実・問題・義務〉を十分に認識している。  "
      },
      {
        "line": 425,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 426,
        "text": "違い: cognizant of は非常に形式的で、事実を理解・把握していることに焦点がある。sensible of は認識に加えて感情的な受け止め方も表しうる。  "
      },
      {
        "line": 427,
        "text": "例: The committee is cognizant of the need for further evidence.  "
      },
      {
        "line": 428,
        "text": "訳: 委員会は、さらなる証拠が必要であることを十分に認識している。  "
      },
      {
        "line": 430,
        "text": "・mindful of something  "
      },
      {
        "line": 431,
        "text": "定義: 〈危険・影響・必要性〉を意識し、注意を払っている。  "
      },
      {
        "line": 432,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 433,
        "text": "違い: mindful of は認識したうえで注意深く行動する含みが強い。sensible of は単に気づいていることや、恩恵を感じていることにも使える。  "
      },
      {
        "line": 434,
        "text": "例: Please be mindful of the needs of other passengers.  "
      },
      {
        "line": 435,
        "text": "訳: 他の乗客のニーズに配慮してください。  "
      },
      {
        "line": 437,
        "text": "【反意語】"
      },
      {
        "line": 439,
        "text": "・unaware of something  "
      },
      {
        "line": 440,
        "text": "定義: 〈事実・状況〉に気づいていない、知らない。  "
      },
      {
        "line": 441,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 442,
        "text": "違い: unaware of は認識がないことを直接表し、sensible of の「意識している」と対照をなす。  "
      },
      {
        "line": 443,
        "text": "例: He was unaware of the rule when he submitted the form.  "
      },
      {
        "line": 444,
        "text": "訳: 彼はその用紙を提出したとき、その規則を知らなかった。  "
      },
      {
        "line": 446,
        "text": "・oblivious to something  "
      },
      {
        "line": 447,
        "text": "定義: 〈事実・危険・周囲の状況〉にまったく気づいていない。  "
      },
      {
        "line": 448,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 449,
        "text": "違い: oblivious to は気づいていない程度が強く、しばしば周囲への無関心を含む。sensible of と反対方向だが、単なる知識不足より強い。  "
      },
      {
        "line": 450,
        "text": "例: The driver seemed oblivious to the warning signs.  "
      },
      {
        "line": 451,
        "text": "訳: その運転手は警告標識にまったく気づいていないようだった。  "
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
    "input_body_sha256": "dce1e8375f2e9709647eb4c0fd89fa016895cec32363a81b3950d8cdb28a2078",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "bb6877b2be871c70212827286aa646a1c56fbb86633b3c8d3072f7bc65bbb1cb",
    "source_first_artifact_sha256": "0035642740b1174f92eb8173dfb0455de3648f65c58090795bb3e13932a0c417",
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
        "locator": "https://www.oxfordlearnersdictionaries.com/definition/english/sensible",
        "source_type": "learner_dictionary",
        "independence_group": "oxford_university_press",
        "facts": [
          {
            "id": "F001",
            "form": "sensible",
            "kind": "lexical_sense",
            "statement": "Sensible describes people or behavior showing good judgement based on reason and experience rather than emotion.",
            "source_detail": "Oxford's first adjective sense defines sensible people and behavior in terms of good judgement and practical reason."
          },
          {
            "id": "F002",
            "form": "sensible",
            "kind": "lexical_sense",
            "statement": "Sensible clothing and shoes are useful and practical rather than mainly fashionable.",
            "source_detail": "Oxford gives a separate clothing sense for useful rather than fashionable clothes and shoes."
          },
          {
            "id": "F003",
            "form": "sensible",
            "kind": "lexical_sense",
            "statement": "Sensible of something is a formal or literary way to say aware of or conscious of it.",
            "source_detail": "Oxford lists the formal/literary sensible of construction for awareness of a fact or feeling."
          },
          {
            "id": "F004",
            "form": "sensible",
            "kind": "grammar_frame",
            "statement": "Sensible occurs in sensible about, sensible to do, sensible for somebody to do, and common sensible noun combinations.",
            "source_detail": "Oxford examples and usage patterns include sensible about a matter, sensible to do something, sensible for somebody to do something, and sensible idea/thing/approach/decision/solution."
          },
          {
            "id": "F005",
            "form": "sensible",
            "kind": "pronunciation",
            "statement": "Oxford gives the current learner-dictionary pronunciation /ˈsensəbl/.",
            "source_detail": "The Oxford entry displays /ˈsensəbl/ with the headword."
          },
          {
            "id": "F006",
            "form": "sensible",
            "kind": "etymology",
            "statement": "Sensible entered English in the late Middle English period through French or Latin forms related to sensation and feeling.",
            "source_detail": "Oxford traces sensible to Old French or Latin sensibilis, related to sensus and sentire."
          }
        ]
      },
      {
        "id": "S002",
        "locator": "https://www.merriam-webster.com/dictionary/sensible",
        "source_type": "general_dictionary",
        "independence_group": "merriam_webster",
        "facts": [
          {
            "id": "F007",
            "form": "sensible",
            "kind": "lexical_sense",
            "statement": "Sensible means having or showing good sense and reason.",
            "source_detail": "Merriam-Webster gives having or indicative of good sense and reason as a main adjective definition."
          },
          {
            "id": "F008",
            "form": "sensible",
            "kind": "lexical_sense",
            "statement": "Sensible can describe something designed for practical ends rather than appearance.",
            "source_detail": "Merriam-Webster gives the practical-ends-rather-than-appearance definition for objects and choices."
          },
          {
            "id": "F009",
            "form": "sensible",
            "kind": "lexical_sense",
            "statement": "Sensible can mean perceptible to the senses or reason and capable of receiving sensory impressions.",
            "source_detail": "Merriam-Webster lists perceptible and capable-of-sensory-impression definitions in its adjective entry."
          },
          {
            "id": "F010",
            "form": "sensible",
            "kind": "grammar_frame",
            "statement": "Sensible of can express direct or intuitive awareness of an intangible or emotional state.",
            "source_detail": "Merriam-Webster's usage note explains sensible of as perceiving directly or intuitively, especially an intangible or emotional state."
          },
          {
            "id": "F011",
            "form": "sensible",
            "kind": "specialist_use",
            "statement": "Sensible is also listed as a rare noun for something that can be sensed.",
            "source_detail": "Merriam-Webster includes a noun entry meaning something perceptible to the senses."
          },
          {
            "id": "F012",
            "form": "sensible",
            "kind": "etymology",
            "statement": "Sensible is recorded from Middle English through Anglo-French and Latin, with a first-known-use date in the fourteenth century.",
            "source_detail": "Merriam-Webster's etymology gives the Middle English, Anglo-French, and Latin route and dates the first known use to the 14th century."
          }
        ]
      },
      {
        "id": "S003",
        "locator": "https://www.collinsdictionary.com/dictionary/english/sensible",
        "source_type": "general_dictionary",
        "independence_group": "harpercollins",
        "facts": [
          {
            "id": "F013",
            "form": "sensible",
            "kind": "lexical_sense",
            "statement": "Sensible actions and decisions are based on reasons rather than emotions, and sensible people behave in that way.",
            "source_detail": "Collins COBUILD defines sensible actions and decisions as reason-based rather than emotion-based and supplies people and behavior examples."
          },
          {
            "id": "F014",
            "form": "sensible",
            "kind": "lexical_sense",
            "statement": "Sensible shoes and clothing are practical and strong rather than fashionable or attractive.",
            "source_detail": "Collins gives the practical-clothing sense and specifically describes sensible shoes and footwear."
          },
          {
            "id": "F015",
            "form": "sensible",
            "kind": "lexical_sense",
            "statement": "Broader dictionary entries include sensible to for sensory perception, sensible of for awareness, and perceptible or appreciable uses.",
            "source_detail": "Collins British and American entries list capacity for sensation, perceptibility, significant degree, and sensible of awareness constructions."
          },
          {
            "id": "F016",
            "form": "sensible",
            "kind": "specialist_use",
            "statement": "Sensible is also recorded as an uncommon musical noun for the leading note.",
            "source_detail": "Collins lists sensible note as a less common musical term for the leading note."
          },
          {
            "id": "F017",
            "form": "sensibly",
            "kind": "derived_form",
            "statement": "Sensibly is the related adverb, and sensibleness is the related noun for the quality of being sensible.",
            "source_detail": "Collins lists sensibly and sensibleness among the derivatives of sensible."
          }
        ]
      },
      {
        "id": "S004",
        "locator": "https://www.etymonline.com/word/sensible",
        "source_type": "etymology_dictionary",
        "independence_group": "etymonline",
        "facts": [
          {
            "id": "F018",
            "form": "sensible",
            "kind": "etymology",
            "statement": "The late-fourteenth-century adjective first referred to being capable of sensation or to being perceptible.",
            "source_detail": "Etymonline describes the late 14th-century sensation and perceptibility senses in its historical account."
          },
          {
            "id": "F019",
            "form": "sensible",
            "kind": "etymology",
            "statement": "By around the early fifteenth century sensible also referred to mental perception, good sense, and awareness.",
            "source_detail": "Etymonline records the developments toward mental perception, good sense, and being aware or cognizant."
          },
          {
            "id": "F020",
            "form": "sensible",
            "kind": "etymology",
            "statement": "The good-sense use for actions or discourse is later, while the practical-clothing use is attested in the nineteenth century.",
            "source_detail": "Etymonline dates the good-sense action/discourse use to the 1650s and the practical clothes/shoes use to 1855."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "U001",
        "source_fact_ids": [
          "F001",
          "F004",
          "F007",
          "F013"
        ],
        "canonical_statement": "Sensible describes people, behavior, actions, and decisions that show good sense and are based on reason rather than emotion.",
        "disposition": "included",
        "rationale": "This is the high-frequency core adjective sense and is the first article sense."
      },
      {
        "id": "U002",
        "source_fact_ids": [
          "F002",
          "F008",
          "F014"
        ],
        "canonical_statement": "Sensible clothing and shoes prioritize practical use over fashion or appearance.",
        "disposition": "included",
        "rationale": "The clothing use is common enough to deserve a separate learner sense and its own collocations."
      },
      {
        "id": "U003",
        "source_fact_ids": [
          "F003",
          "F010",
          "F015"
        ],
        "canonical_statement": "Sensible of expresses formal or literary awareness of a fact, feeling, or intangible state.",
        "disposition": "included",
        "rationale": "The sensible of frame is distinct from the judgment sense and is important for reading older or formal prose."
      },
      {
        "id": "U004",
        "source_fact_ids": [
          "F009",
          "F015",
          "F018"
        ],
        "canonical_statement": "Sensible can describe a difference, change, or other feature that is perceptible or appreciable.",
        "disposition": "included",
        "rationale": "This lower-frequency perceptibility sense explains formal examples such as sensible difference and sensible increase."
      },
      {
        "id": "U005",
        "source_fact_ids": [
          "F009",
          "F015",
          "F018"
        ],
        "canonical_statement": "Sensible to can describe the capacity to receive a physical sensation, especially in formal or old usage.",
        "disposition": "included",
        "rationale": "The sensory frame is separated from perceptibility of a difference because it takes stimulus complements such as pain, heat, and light."
      },
      {
        "id": "U006",
        "source_fact_ids": [
          "F011",
          "F016",
          "F017"
        ],
        "canonical_statement": "Sensible has related adverb and noun forms, while rare noun and musical uses are acknowledged but not promoted as main learner senses.",
        "disposition": "integrated",
        "rationale": "The article records the forms and the rare uses in word-formation or usage notes, with an explicit exclusion from the numbered main senses."
      },
      {
        "id": "U007",
        "source_fact_ids": [
          "F005",
          "F006",
          "F012",
          "F018",
          "F019",
          "F020"
        ],
        "canonical_statement": "Sensible is historically connected with sensation, mental awareness, and later good judgment and practical clothing.",
        "disposition": "included",
        "rationale": "The pronunciation and etymology sections state the current form and the bounded historical semantic development."
      }
    ],
    "claim_units": [
      {
        "id": "C001",
        "union_ids": [
          "U001"
        ],
        "subject_form": "sensible",
        "claim_type": "definition",
        "statement": "Sensible commonly praises a person, plan, or action for being reasonable, practical, and guided by good judgment.",
        "article_target_ids": [
          "definition:001",
          "sense_boundary:001",
          "usage_note:001",
          "core_image:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F001",
            "support_summary": "Oxford defines the core use through good judgement and practical reason."
          },
          {
            "source_fact_id": "F004",
            "support_summary": "Oxford attests the central sensible about and sensible to do patterns."
          },
          {
            "source_fact_id": "F007",
            "support_summary": "Merriam-Webster directly gives good sense and reason as the adjective meaning."
          },
          {
            "source_fact_id": "F013",
            "support_summary": "Collins ties sensible actions and decisions to reasons rather than emotions."
          }
        ]
      },
      {
        "id": "C002",
        "union_ids": [
          "U002"
        ],
        "subject_form": "sensible",
        "claim_type": "definition",
        "statement": "Sensible clothing and footwear are evaluated as practical rather than primarily fashionable.",
        "article_target_ids": [
          "definition:002",
          "register:002",
          "collocation:009",
          "usage_note:002",
          "core_image:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "F002",
            "support_summary": "Oxford separates the useful-rather-than-fashionable clothing sense."
          },
          {
            "source_fact_id": "F008",
            "support_summary": "Merriam-Webster describes practical ends rather than appearance."
          },
          {
            "source_fact_id": "F014",
            "support_summary": "Collins explicitly attests practical sensible shoes and clothing."
          }
        ]
      },
      {
        "id": "C003",
        "union_ids": [
          "U003"
        ],
        "subject_form": "sensible of",
        "claim_type": "grammar_frame",
        "statement": "Sensible of is a formal or literary frame for being aware of or deeply conscious of a fact, feeling, or intangible state.",
        "article_target_ids": [
          "definition:005",
          "grammar_pattern:020",
          "collocation:021",
          "usage_note:005",
          "usage_note:006",
          "core_image:006"
        ],
        "source_supports": [
          {
            "source_fact_id": "F003",
            "support_summary": "Oxford identifies sensible of as the formal awareness construction."
          },
          {
            "source_fact_id": "F010",
            "support_summary": "Merriam-Webster explains sensible of as direct or intuitive awareness."
          },
          {
            "source_fact_id": "F015",
            "support_summary": "Collins lists sensible of awareness and perceptual constructions."
          }
        ]
      },
      {
        "id": "C004",
        "union_ids": [
          "U004"
        ],
        "subject_form": "sensible",
        "claim_type": "definition",
        "statement": "In formal usage sensible can mean perceptible or appreciable, as in a sensible difference or increase.",
        "article_target_ids": [
          "definition:003",
          "grammar_pattern:013",
          "collocation:014",
          "usage_note:003",
          "synonym:011",
          "antonym:004",
          "core_image:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F009",
            "support_summary": "Merriam-Webster includes perceptible-to-the-senses-or-reason meanings."
          },
          {
            "source_fact_id": "F015",
            "support_summary": "Collins includes perceptible, appreciable, and significant uses in broader entries."
          },
          {
            "source_fact_id": "F018",
            "support_summary": "Etymonline records the historical perceptibility meaning."
          }
        ]
      },
      {
        "id": "C005",
        "union_ids": [
          "U005"
        ],
        "subject_form": "sensible to",
        "claim_type": "grammar_frame",
        "statement": "Sensible to can mean capable of receiving physical sensation, but sensitive to is the normal modern expression.",
        "article_target_ids": [
          "definition:004",
          "grammar_pattern:017",
          "collocation:018",
          "usage_note:004",
          "synonym:015",
          "antonym:006",
          "core_image:005"
        ],
        "source_supports": [
          {
            "source_fact_id": "F009",
            "support_summary": "Merriam-Webster records capable-of-sensory-impression meanings."
          },
          {
            "source_fact_id": "F015",
            "support_summary": "Collins lists sensible to in the sensory-capacity portion of the entry."
          },
          {
            "source_fact_id": "F018",
            "support_summary": "Etymonline documents the older capable-of-sensation history."
          }
        ]
      },
      {
        "id": "C006",
        "union_ids": [
          "U006"
        ],
        "subject_form": "sensible",
        "claim_type": "word_formation",
        "statement": "Sensibly and sensibleness are related forms, and rare noun or musical uses are acknowledged without being treated as core learner senses.",
        "article_target_ids": [
          "word_formation:001",
          "word_formation:002",
          "word_formation:003",
          "word_formation:004",
          "usage_note:006"
        ],
        "source_supports": [
          {
            "source_fact_id": "F011",
            "support_summary": "Merriam-Webster records a rare noun for something sensed."
          },
          {
            "source_fact_id": "F016",
            "support_summary": "Collins records the uncommon musical noun sensible note."
          },
          {
            "source_fact_id": "F017",
            "support_summary": "Collins lists sensibly and sensibleness as related forms."
          }
        ]
      },
      {
        "id": "C007",
        "union_ids": [
          "U007"
        ],
        "subject_form": "sensible",
        "claim_type": "etymology",
        "statement": "The word's historical path runs from sensation and perception through awareness to good judgment and practical evaluation.",
        "article_target_ids": [
          "pronunciation:001",
          "etymology:001",
          "etymology:002",
          "core_image:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F005",
            "support_summary": "Oxford supplies the current pronunciation used in the article."
          },
          {
            "source_fact_id": "F006",
            "support_summary": "Oxford supplies the French and Latin origin connected with sensation."
          },
          {
            "source_fact_id": "F012",
            "support_summary": "Merriam-Webster confirms the Middle English, French, and Latin route."
          },
          {
            "source_fact_id": "F018",
            "support_summary": "Etymonline establishes the earlier sensation and perceptibility meanings."
          },
          {
            "source_fact_id": "F019",
            "support_summary": "Etymonline records the movement toward mental perception and awareness."
          },
          {
            "source_fact_id": "F020",
            "support_summary": "Etymonline dates the later good-sense and practical-clothing developments."
          }
        ]
      }
    ]
  },
  "specification_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
  "source_artifact_sha256": "0035642740b1174f92eb8173dfb0455de3648f65c58090795bb3e13932a0c417",
  "normalized_input_sha256": "e85337d4646ad76eb9928ca16a028cf13c8a6ab4f98677f972f8b60b45d5cd35"
}
```
