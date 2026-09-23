# Independent checker handoff

Stage: `checker_passes/evidence`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.evidence.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
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
  "input_body_sha256": "82f343438dd0057f0cc4edd16ece26ba75380521e8c02dfb806b6da7eb43d3f8",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米: /səˈspɪʃən/｜英: /səˈspɪʃən/。3音節で、第2音節に主強勢がある。Oxford 系の辞書では語末を /ʃn/ と圧縮して表記することもあるが、Cambridge 系の /ʃ.ən/ と大きく異なる発音を示すものではない。語頭の su- は強く /suː/ と読まず、弱い /sə/ になる。  "
      }
    ],
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
    "core_image": [
      {
        "line": 28,
        "text": "＃コアイメージ"
      },
      {
        "line": 30,
        "text": "suspicion の共通核は、「まだ確証はないが、表面に見えていることの背後に別の事実・意図・問題があるのではないかと感じる」ことである。  "
      },
      {
        "line": 31,
        "text": "・人が犯罪・不正をしたのではないかと見る → 「容疑、疑い」（語義1）  "
      },
      {
        "line": 32,
        "text": "・相手や考えをそのまま信用してよいのかと構える → 「不信、疑念」（語義2）  "
      },
      {
        "line": 33,
        "text": "・ある事実が本当なのではないかと推測する → 「気がすること、疑い、予感」（語義3）  "
      },
      {
        "line": 34,
        "text": "・存在を断定するほどではないが、わずかに感じ取れる → 「ほんの少し、かすかな気配」（語義4）  "
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
    "frames": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 46,
        "text": "【文法パターン】suspicion that 〈節〉＝～ではないかという疑い／suspicion of 〈crime/wrongdoing〉＝〈犯罪・不正〉の疑い／suspicions about 〈person/behavior〉＝〈人・行動〉に関する疑い／arouse/raise suspicion＝疑いを招く／on suspicion of 〈crime〉＝〈犯罪〉の容疑で／be under suspicion＝疑いをかけられている／come/fall under suspicion＝疑いをかけられるようになる／cast suspicion on 〈person/action〉＝〈人・行為〉に疑いを向ける。  "
      },
      {
        "line": 105,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 113,
        "text": "【文法パターン】regard/view/treat 〈person/claim〉 with suspicion＝〈人・主張〉を疑いの目で見る／be met with suspicion＝疑いをもって受け止められる／suspicion of 〈person/group/idea〉＝〈人・集団・考え〉への不信／deep/widespread suspicion＝強い／広範な不信／without suspicion＝疑わずに。  "
      },
      {
        "line": 176,
        "text": "3. 【名詞・可算】～ではないかという気、確証のない推測"
      },
      {
        "line": 184,
        "text": "【文法パターン】a suspicion that 〈節〉＝～ではないかという気／have a suspicion that 〈節〉＝～ではないかと思う／a sneaking suspicion that 〈節〉＝ひそかに～ではないかと思う気持ち／a nagging suspicion that 〈節〉＝頭から離れない疑い／a strong/growing suspicion that 〈節〉＝強い／高まる疑い／confirm/dispel a suspicion＝推測を裏付ける／打ち消す。  "
      },
      {
        "line": 243,
        "text": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配"
      },
      {
        "line": 251,
        "text": "【文法パターン】a suspicion of 〈color/flavor/smell/emotion〉＝ほんの少しの〈色・味・匂い・感情〉／with a suspicion of 〈smile/irony〉＝かすかな〈笑み・皮肉〉を帯びて。  "
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
  "evidence_context": {
    "schema_version": "evidence_context_v2",
    "input_body_sha256": "82f343438dd0057f0cc4edd16ece26ba75380521e8c02dfb806b6da7eb43d3f8",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "5063f35d9bdceaf9a08c24ab7f7be9bb41fe938157c5586f929a57a2727c2c4c",
    "source_first_artifact_sha256": "358a6ef905363f010a31dece02f1dd57e94ea0fad57f759488d3898360d8fc54",
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
        "id": "american_heritage",
        "locator": "https://ahdictionary.com/word/search.html?q=suspicion",
        "source_type": "general_dictionary",
        "independence_group": "american_heritage_harpercollins",
        "facts": [
          {
            "id": "ahd_wrongdoing",
            "form": "suspicion",
            "kind": "definition",
            "statement": "American Heritage distinguishes suspecting something on little or no evidence from the condition of being suspected, especially of wrongdoing.",
            "source_detail": "American Heritage, noun senses 1 and 2."
          },
          {
            "id": "ahd_distrust",
            "form": "suspicion",
            "kind": "definition",
            "statement": "American Heritage also defines a state of no confidence or certainty as distrust.",
            "source_detail": "American Heritage, noun sense 3."
          },
          {
            "id": "ahd_trace",
            "form": "a suspicion of",
            "kind": "definition",
            "statement": "American Heritage defines a suspicion as a minute amount or slight indication, a trace.",
            "source_detail": "American Heritage, noun sense 4."
          },
          {
            "id": "ahd_verb",
            "form": "suspicion",
            "kind": "derived_form",
            "statement": "American Heritage records an informal verb suspicion meaning suspect, with suspicioned and suspicioning forms.",
            "source_detail": "American Heritage, verb entry."
          },
          {
            "id": "ahd_origin",
            "form": "suspicion",
            "kind": "etymology",
            "statement": "American Heritage traces suspicion from Middle English via Anglo-Norman and Old French to Latin suspectio, from suspectus and suspicere.",
            "source_detail": "American Heritage etymology note."
          }
        ]
      },
      {
        "id": "etymonline",
        "locator": "https://www.etymonline.com/word/suspicion",
        "source_type": "etymological_reference",
        "independence_group": "online_etymology_dictionary",
        "facts": [
          {
            "id": "ety_origin",
            "form": "suspicion",
            "kind": "etymology",
            "statement": "Etymonline records suspicion around 1300 through Anglo-French and Old French from Late Latin suspectionem, nominative suspectio, related to Latin suspicere.",
            "source_detail": "Online Etymology Dictionary, suspicion entry."
          },
          {
            "id": "ety_spelling",
            "form": "suspicion",
            "kind": "historical_spelling",
            "statement": "Etymonline says the English spelling was influenced in the fourteenth century by learned Old French forms closer to Latin.",
            "source_detail": "Online Etymology Dictionary, suspicion entry."
          },
          {
            "id": "ety_verb",
            "form": "suspicion",
            "kind": "historical_attestation",
            "statement": "Etymonline notes a verb use meaning suspect in nineteenth-century U.S. Western slang.",
            "source_detail": "Online Etymology Dictionary, suspicion entry."
          }
        ]
      },
      {
        "id": "merriam_webster",
        "locator": "https://www.merriam-webster.com/dictionary/suspicion",
        "source_type": "general_dictionary",
        "independence_group": "merriam_webster",
        "facts": [
          {
            "id": "mw_wrongdoing",
            "form": "suspicion",
            "kind": "definition",
            "statement": "Merriam-Webster defines a noun sense as suspecting something wrong without proof or on slight evidence, and links it with mistrust.",
            "source_detail": "Merriam-Webster, noun sense 1a."
          },
          {
            "id": "mw_uncertainty",
            "form": "suspicion",
            "kind": "definition",
            "statement": "Merriam-Webster gives a noun sense for mental uneasiness and uncertainty, comparable to doubt.",
            "source_detail": "Merriam-Webster, noun sense 1b."
          },
          {
            "id": "mw_trace",
            "form": "a suspicion of",
            "kind": "definition",
            "statement": "Merriam-Webster lists a barely detectable amount or trace sense and illustrates it with garlic.",
            "source_detail": "Merriam-Webster, noun sense 2."
          },
          {
            "id": "mw_verb",
            "form": "suspicion",
            "kind": "derived_form",
            "statement": "Merriam-Webster records a transitive verb suspicion with forms suspicioned and suspicioning, labelled chiefly dialectal.",
            "source_detail": "Merriam-Webster, verb entry."
          },
          {
            "id": "mw_origin",
            "form": "suspicion",
            "kind": "etymology",
            "statement": "Merriam-Webster traces the noun from Middle English through Anglo-French to Latin suspicion-, suspicio, and suspicere.",
            "source_detail": "Merriam-Webster, Etymology."
          },
          {
            "id": "mw_legal",
            "form": "suspicion",
            "kind": "legal_definition",
            "statement": "Merriam-Webster's legal definition describes suspicion as a mental state usually short of belief, based on no proof or slight evidence.",
            "source_detail": "Merriam-Webster, Legal Definition."
          },
          {
            "id": "mw_pron",
            "form": "suspicion",
            "kind": "pronunciation",
            "statement": "Merriam-Webster's pronunciation respelling marks primary stress on the second syllable.",
            "source_detail": "Merriam-Webster pronunciation respelling sə-ˈspi-shən."
          },
          {
            "id": "mw_contrast",
            "form": "suspicion / mistrust",
            "kind": "sense_boundary",
            "statement": "Merriam-Webster says suspicion emphasizes lack of faith in someone's or something's truth, fairness, or reliability; mistrust implies doubt based on suspicion.",
            "source_detail": "Merriam-Webster, Choose the Right Synonym."
          },
          {
            "id": "mw_clause",
            "form": "suspicion that",
            "kind": "collocation",
            "statement": "Merriam-Webster gives examples of suspicion followed by a that-clause and of viewing policies with suspicion.",
            "source_detail": "Merriam-Webster, example sentences."
          }
        ]
      },
      {
        "id": "merseyside_police",
        "locator": "https://www.merseyside.police.uk/news/merseyside/news/2026/june-2026/man-arrested-on-suspicion-of-breach-of-the-peace-on-county-road/",
        "source_type": "official_primary",
        "independence_group": "merseyside_police",
        "facts": [
          {
            "id": "police_on",
            "form": "arrested on suspicion of",
            "kind": "official_usage",
            "statement": "A Merseyside Police release uses arrested on suspicion of + an offence and says the person will be taken for questioning.",
            "source_detail": "Official police news release, published 13 June 2026."
          }
        ]
      },
      {
        "id": "oxford_learner",
        "locator": "https://www.oxfordlearnersdictionaries.com/definition/english/suspicion",
        "source_type": "learner_dictionary",
        "independence_group": "oxford_university_press",
        "facts": [
          {
            "id": "oxf_s1",
            "form": "suspicion",
            "kind": "definition",
            "statement": "Oxford lists a countable or uncountable noun sense for believing someone has done something wrong, illegal, or dishonest without proof.",
            "source_detail": "Oxford entry, sense 1; countability label and definition."
          },
          {
            "id": "oxf_on",
            "form": "on suspicion of",
            "kind": "grammar_pattern",
            "statement": "Oxford gives on suspicion of + a crime as a phrase used with arrest, and supplies an arrest example.",
            "source_detail": "Oxford entry, sense 1 examples."
          },
          {
            "id": "oxf_that",
            "form": "suspicion that",
            "kind": "collocation",
            "statement": "Oxford gives suspicion that + clause and a sneaking suspicion example.",
            "source_detail": "Oxford entry, sense 1 examples."
          },
          {
            "id": "oxf_belief",
            "form": "suspicion",
            "kind": "definition",
            "statement": "Oxford lists a countable sense for a belief that something is true despite lacking proof.",
            "source_detail": "Oxford entry, sense 2."
          },
          {
            "id": "oxf_distrust",
            "form": "suspicion",
            "kind": "definition",
            "statement": "Oxford lists a countable or uncountable sense for being unable to trust someone or something, with regard/view with suspicion examples.",
            "source_detail": "Oxford entry, sense 3."
          },
          {
            "id": "oxf_trace",
            "form": "a suspicion of",
            "kind": "definition",
            "statement": "Oxford labels a singular use formal and defines it as a small amount, with hint as a synonym and a suspicion of a smile example.",
            "source_detail": "Oxford entry, sense 4."
          },
          {
            "id": "oxf_family",
            "form": "suspect / suspected / suspicious / suspiciously",
            "kind": "word_formation",
            "statement": "Oxford's word-family list includes suspect, suspected, suspicion, suspicious, and suspiciously.",
            "source_detail": "Oxford entry, Word Family."
          },
          {
            "id": "oxf_pron",
            "form": "suspicion",
            "kind": "pronunciation",
            "statement": "Oxford displays the same pronunciation /səˈspɪʃn/ in its British and American fields.",
            "source_detail": "Oxford entry, pronunciation fields."
          },
          {
            "id": "oxf_origin",
            "form": "suspicion",
            "kind": "etymology",
            "statement": "Oxford traces suspicion through Middle English and Anglo-Norman to medieval Latin suspectio(n-), related to suspicere, and notes influence from Old French and Latin forms.",
            "source_detail": "Oxford entry, Word Origin."
          },
          {
            "id": "oxf_under",
            "form": "under suspicion",
            "kind": "grammar_pattern",
            "statement": "Oxford's idiom section defines under suspicion as suspected of wrongdoing.",
            "source_detail": "Oxford entry, idiom under suspicion."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "u_arrest_pattern",
        "source_fact_ids": [
          "oxf_on",
          "police_on"
        ],
        "canonical_statement": "On suspicion of + an offence is used in arrest reporting to state the suspected basis.",
        "disposition": "integrated",
        "rationale": "The article includes the on suspicion of + offence pattern and an arrest example."
      },
      {
        "id": "u_distrust",
        "source_fact_ids": [
          "oxf_distrust",
          "mw_contrast",
          "ahd_distrust"
        ],
        "canonical_statement": "Suspicion can describe distrust or a lack of confidence in a person, claim, or thing.",
        "disposition": "integrated",
        "rationale": "The article includes the distrust sense and with suspicion / suspicion of patterns."
      },
      {
        "id": "u_etymology",
        "source_fact_ids": [
          "oxf_origin",
          "mw_origin",
          "ahd_origin",
          "ety_origin",
          "ety_spelling"
        ],
        "canonical_statement": "Suspicion entered English through Middle English and Anglo-French or Old French, from Latin suspectio/suspectionem related to suspicere; the spelling was influenced by learned forms.",
        "disposition": "integrated",
        "rationale": "The article traces the English and Latin history of suspicion."
      },
      {
        "id": "u_legal_definition",
        "source_fact_ids": [
          "mw_legal"
        ],
        "canonical_statement": "The legal dictionary sense describes suspicion as a mental state short of belief and based on no or slight evidence.",
        "disposition": "integrated",
        "rationale": "The article describes the no-proof boundary and distinguishes suspicion from conviction in legal/reporting contexts."
      },
      {
        "id": "u_pronunciation",
        "source_fact_ids": [
          "oxf_pron",
          "mw_pron"
        ],
        "canonical_statement": "The word has second-syllable primary stress; Oxford gives the same UK and US transcription.",
        "disposition": "integrated",
        "rationale": "The article gives IPA and second-syllable primary stress."
      },
      {
        "id": "u_rare_verb",
        "source_fact_ids": [
          "mw_verb",
          "ahd_verb",
          "ety_verb"
        ],
        "canonical_statement": "Some dictionaries record a rare, chiefly dialectal or informal verb suspicion meaning suspect.",
        "disposition": "integrated",
        "rationale": "The article notes that some dictionaries record a marginal verb use."
      },
      {
        "id": "u_that_belief",
        "source_fact_ids": [
          "oxf_that",
          "oxf_belief",
          "mw_uncertainty",
          "mw_clause"
        ],
        "canonical_statement": "Suspicion can take a that-clause and express a belief or uneasy uncertainty without proof.",
        "disposition": "integrated",
        "rationale": "The article uses the no-proof belief/uncertainty sense and the suspicion that construction."
      },
      {
        "id": "u_trace",
        "source_fact_ids": [
          "oxf_trace",
          "mw_trace",
          "ahd_trace"
        ],
        "canonical_statement": "A suspicion of something can formally or descriptively mean a very small amount or slight trace.",
        "disposition": "integrated",
        "rationale": "The article includes the formal small-amount sense and a suspicion of constructions."
      },
      {
        "id": "u_under_suspicion",
        "source_fact_ids": [
          "oxf_under"
        ],
        "canonical_statement": "Under suspicion describes being suspected of wrongdoing.",
        "disposition": "integrated",
        "rationale": "The article includes under suspicion and being under suspicion."
      },
      {
        "id": "u_word_family",
        "source_fact_ids": [
          "oxf_family"
        ],
        "canonical_statement": "Oxford lists suspect, suspected, suspicion, suspicious, and suspiciously in the word family.",
        "disposition": "integrated",
        "rationale": "The article lists suspect, suspicious, and suspiciously as related forms."
      },
      {
        "id": "u_wrongdoing",
        "source_fact_ids": [
          "oxf_s1",
          "mw_wrongdoing",
          "ahd_wrongdoing"
        ],
        "canonical_statement": "A suspicion can be a belief that someone did something wrong without proof or sufficient evidence.",
        "disposition": "integrated",
        "rationale": "The article uses this distinction in sense 1 and its definition."
      }
    ],
    "claim_units": [
      {
        "id": "claim_wrongdoing",
        "union_ids": [
          "u_wrongdoing"
        ],
        "subject_form": "suspicion",
        "claim_type": "definition",
        "statement": "A suspicion can be a belief that someone has done something wrong without proof.",
        "article_target_ids": [
          "sense_boundary:001",
          "definition:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "oxf_s1",
            "support_summary": "Oxford defines a countable or uncountable noun sense as believing someone did wrong without proof."
          },
          {
            "source_fact_id": "mw_wrongdoing",
            "support_summary": "Merriam-Webster defines suspicion as suspecting wrongdoing without proof or on slight evidence."
          },
          {
            "source_fact_id": "ahd_wrongdoing",
            "support_summary": "American Heritage distinguishes suspecting wrongdoing on little evidence from being suspected of it."
          }
        ]
      },
      {
        "id": "claim_arrest_pattern",
        "union_ids": [
          "u_arrest_pattern"
        ],
        "subject_form": "on suspicion of",
        "claim_type": "grammar_pattern",
        "statement": "On suspicion of plus an offence is used to state the suspected basis for an arrest.",
        "article_target_ids": [
          "grammar_pattern:005",
          "collocation:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "oxf_on",
            "support_summary": "Oxford gives on suspicion of plus a crime in its arrest phrase and example."
          },
          {
            "source_fact_id": "police_on",
            "support_summary": "Merseyside Police uses arrested on suspicion of an offence and says the person was taken for questioning."
          }
        ]
      },
      {
        "id": "claim_that_belief",
        "union_ids": [
          "u_that_belief"
        ],
        "subject_form": "suspicion that",
        "claim_type": "definition_and_pattern",
        "statement": "Suspicion can express an unproved belief or uncertainty and can be followed by a that-clause.",
        "article_target_ids": [
          "definition:003",
          "grammar_pattern:001",
          "grammar_pattern:015",
          "grammar_pattern:016"
        ],
        "source_supports": [
          {
            "source_fact_id": "oxf_that",
            "support_summary": "Oxford gives suspicion that plus a clause and the phrase a sneaking suspicion."
          },
          {
            "source_fact_id": "oxf_belief",
            "support_summary": "Oxford defines a suspicion as a belief that something is true despite lacking proof."
          },
          {
            "source_fact_id": "mw_uncertainty",
            "support_summary": "Merriam-Webster gives suspicion the sense of mental uneasiness and uncertainty comparable to doubt."
          },
          {
            "source_fact_id": "mw_clause",
            "support_summary": "Merriam-Webster examples use suspicion followed by a that-clause."
          }
        ]
      },
      {
        "id": "claim_distrust",
        "union_ids": [
          "u_distrust"
        ],
        "subject_form": "suspicion",
        "claim_type": "definition_and_pattern",
        "statement": "Suspicion can describe distrust or lack of confidence toward a person, claim, or thing.",
        "article_target_ids": [
          "sense_boundary:002",
          "definition:002",
          "grammar_pattern:009",
          "grammar_pattern:011",
          "collocation:007",
          "collocation:009",
          "synonym:004",
          "synonym:005"
        ],
        "source_supports": [
          {
            "source_fact_id": "oxf_distrust",
            "support_summary": "Oxford defines suspicion as inability to trust and gives regard/view with suspicion examples."
          },
          {
            "source_fact_id": "mw_contrast",
            "support_summary": "Merriam-Webster explains suspicion as lack of faith and contrasts it with mistrust."
          },
          {
            "source_fact_id": "ahd_distrust",
            "support_summary": "American Heritage defines suspicion as a state of no confidence or certainty, or distrust."
          }
        ]
      },
      {
        "id": "claim_trace",
        "union_ids": [
          "u_trace"
        ],
        "subject_form": "a suspicion of",
        "claim_type": "definition_and_pattern",
        "statement": "A suspicion of something can mean a very small amount or slight indication, including a faint smile.",
        "article_target_ids": [
          "sense_boundary:004",
          "definition:004",
          "grammar_pattern:023",
          "grammar_pattern:024",
          "collocation:021"
        ],
        "source_supports": [
          {
            "source_fact_id": "oxf_trace",
            "support_summary": "Oxford labels a suspicion of a small amount formal and gives a suspicion of a smile as an example."
          },
          {
            "source_fact_id": "mw_trace",
            "support_summary": "Merriam-Webster defines the sense as a barely detectable amount or trace and gives garlic as an example."
          },
          {
            "source_fact_id": "ahd_trace",
            "support_summary": "American Heritage defines a suspicion as a minute amount or slight indication."
          }
        ]
      },
      {
        "id": "claim_pronunciation",
        "union_ids": [
          "u_pronunciation"
        ],
        "subject_form": "suspicion",
        "claim_type": "pronunciation",
        "statement": "Oxford gives the same British and American IPA form, and Merriam-Webster marks primary stress on the second syllable.",
        "article_target_ids": [
          "pronunciation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "oxf_pron",
            "support_summary": "Oxford shows /səˈspɪʃn/ in both its British and American pronunciation fields."
          },
          {
            "source_fact_id": "mw_pron",
            "support_summary": "Merriam-Webster's respelling marks primary stress on the second syllable."
          }
        ]
      },
      {
        "id": "claim_word_family",
        "union_ids": [
          "u_word_family"
        ],
        "subject_form": "suspicion",
        "claim_type": "word_family",
        "statement": "Oxford lists suspect, suspicious, and suspiciously in the word family of suspicion.",
        "article_target_ids": [
          "word_formation:001",
          "word_formation:002",
          "word_formation:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "oxf_family",
            "support_summary": "Oxford's word-family list includes suspect, suspected, suspicious, and suspiciously."
          }
        ]
      },
      {
        "id": "claim_etymology",
        "union_ids": [
          "u_etymology"
        ],
        "subject_form": "suspicion",
        "claim_type": "etymology",
        "statement": "Suspicion entered English through Middle English and Anglo-French or Old French from Latin forms related to suspicere; learned forms influenced its spelling.",
        "article_target_ids": [
          "etymology:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "oxf_origin",
            "support_summary": "Oxford traces the noun through Middle English and Anglo-Norman to Latin suspectio related to suspicere."
          },
          {
            "source_fact_id": "mw_origin",
            "support_summary": "Merriam-Webster traces the noun through Anglo-French to Latin suspicio and suspicere."
          },
          {
            "source_fact_id": "ahd_origin",
            "support_summary": "American Heritage traces the noun via Anglo-Norman and Old French to Latin suspectio and suspicere."
          },
          {
            "source_fact_id": "ety_origin",
            "support_summary": "Etymonline records the route through Anglo-French and Old French from Late Latin suspectionem related to suspicere."
          },
          {
            "source_fact_id": "ety_spelling",
            "support_summary": "Etymonline says learned Old French forms closer to Latin influenced the fourteenth-century English spelling."
          }
        ]
      },
      {
        "id": "claim_legal_boundary",
        "union_ids": [
          "u_legal_definition"
        ],
        "subject_form": "suspicion",
        "claim_type": "legal_definition",
        "statement": "In legal usage, suspicion is a mental state short of belief based on no or slight evidence.",
        "article_target_ids": [
          "definition:001",
          "register:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "mw_legal",
            "support_summary": "Merriam-Webster's legal definition describes suspicion as a mental state usually short of belief, based on no or slight evidence."
          }
        ]
      },
      {
        "id": "claim_under_suspicion",
        "union_ids": [
          "u_under_suspicion"
        ],
        "subject_form": "under suspicion",
        "claim_type": "grammar_pattern",
        "statement": "Under suspicion describes being suspected of wrongdoing.",
        "article_target_ids": [
          "grammar_pattern:006",
          "collocation:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "oxf_under",
            "support_summary": "Oxford defines under suspicion as being suspected of wrongdoing."
          }
        ]
      },
      {
        "id": "claim_rare_verb",
        "union_ids": [
          "u_rare_verb"
        ],
        "subject_form": "suspicion",
        "claim_type": "marginal_verb",
        "statement": "Some dictionaries record suspicion as a rare verb meaning suspect, with dialectal, informal, or historical labels.",
        "article_target_ids": [
          "usage_note:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "mw_verb",
            "support_summary": "Merriam-Webster records suspicion as a transitive verb, chiefly dialectal, with suspicioned and suspicioning forms."
          },
          {
            "source_fact_id": "ahd_verb",
            "support_summary": "American Heritage records an informal verb suspicion meaning suspect, with suspicioned and suspicioning forms."
          },
          {
            "source_fact_id": "ety_verb",
            "support_summary": "Etymonline notes a nineteenth-century U.S. Western slang verb use meaning suspect."
          }
        ]
      }
    ],
    "article_targets": [
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:44-47",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "5ef102eef7cc8b8b801d5743c5b965d3d4735889d4c7d15d4397179ac8049b00",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・on suspicion of 〈crime〉\n用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕・拘束したことを述べる。\n例: Two people were arrested on suspicion of fraud after the investigation.\n訳: 捜査後、2人が詐欺の容疑で逮捕された。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:49-52",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "4c1e202a046c808793f9d6ea37ebde49b08ee323c396492ec6a589da76b39950",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・be under suspicion\n用途: 人・組織などが不正や犯罪をしたのではないかと疑われている状態を表す。\n例: The contractor remained under suspicion until the records were checked.\n訳: 記録が確認されるまで、その請負業者には疑いがかけられたままだった。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:106-109",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "ecca96a20ce0cee12c7880e442d90b0de512c00d3a23646a17338237e814373a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・regard/view 〈person/claim〉 with suspicion\n用途: 人や主張をすぐには信用せず、疑いの目で見ることを表す。\n例: Residents viewed the sudden policy change with suspicion.\n訳: 住民たちは突然の方針変更を疑いの目で見た。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:116-119",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "0e0e44e506d67f230f579727939532dc6070fd026616855329e2a9e6d4655747",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・suspicion of 〈person/group〉\n用途: 特定の人・集団に対して根強い不信感を持つことを表す。\n例: Years of secrecy created a lasting suspicion of the agency.\n訳: 長年の秘密主義によって、その機関に対する根強い不信が生まれた。"
      },
      {
        "id": "collocation:021",
        "kind": "collocation",
        "location": "lines:259-262",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配",
        "text_sha256": "32d95eb1b15ec0aa17521f4e31cf66b73432110d7fba505516aded9b8e56a758",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・with a suspicion of a smile\n用途: はっきり笑うほどではない、わずかな笑みを描写する。\n例: She answered with a suspicion of a smile.\n訳: 彼女はほんのかすかな笑みを浮かべて答えた。"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:29",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "f57226e0350c880f4846a6b89e23f25c7de90a71d21ca2be572256b6695fa068",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "人が犯罪、不正、不誠実な行為などをした可能性があると、十分な証明がない段階で考えること、またはその疑いを向けられている状態を表す。個々の疑いを数えるときは可算、疑いという状態・雰囲気をまとめて述べるときは不可算で使われる。"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:96",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "d6067b2e139ed4ef80d8a10db168395473d269087d4b03d3e12a8b4581ff4edb",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "人、組織、動機、考えなどをそのまま信用せず、「裏に何か問題・意図があるかもしれない」と疑って見る態度を表す。語義1のように特定の犯罪・不正行為を想定する必要はなく、広い意味での mistrust / distrust に近い。"
      },
      {
        "id": "definition:003",
        "kind": "definition",
        "location": "line:167",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】～ではないかという気、確証のない推測",
        "text_sha256": "82541b469350ecf347107b7c76454189979f4769c5c04d7a4724a2cdb79d3b73",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "ある事実・状況が本当なのではないかと感じることを表す。ここでは犯罪・不正や相手への不信に限らず、証明はないが「たぶんそうだ」という予感・推測を指す。通常は個々の考えとして可算で、a suspicion that ... の形が非常に重要である。"
      },
      {
        "id": "definition:004",
        "kind": "definition",
        "location": "line:234",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配",
        "text_sha256": "b0355da882656ce2ac0793979fa79047500df1d3eea79d6e7a92a87c0eec57ea",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "色、味、匂い、感情、表情などが、はっきり大量に存在するのではなく「あるかないか分かる程度」にわずかに感じられることを表す。通常 a suspicion of ... の形で用いられる比喩的な用法である。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text_sha256": "b6326f82bf48f4c1248980c678afe90ce00d9bbb661e9336475fde4773156514",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "suspicion は中英語・アングロフランス語／古フランス語を経て、ラテン語 suspīciō / suspectionem「疑い、不信」にさかのぼる。さらに suspicere「ひそかに見る、疑って見る、疑う」と関係し、sub-「下から・ひそかに」と specere「見る」に結び付く語族である。現代語の意味では、目の前の証拠だけでは確定できないものを「何かあるのではないか」と見る感覚が中心に残っている。suspect、suspicious も同じ語族に属する。"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:35",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "7b6799c588c2df17cad08a9cb95127b4fd1a19acac9f23d440218e19d9657c8e",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "suspicion that 〈節〉＝～ではないかという疑い"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:35",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "443cb4aa2e279a7ff38dd67e2a737081a18d79544552e0c94519c897184ab4d8",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "on suspicion of 〈crime〉＝〈犯罪〉の容疑で"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:35",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "87c048752e918f868f4a2653adff11b202f157b5ae9aa34be40587e0163a0147",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be under suspicion＝疑いをかけられている"
      },
      {
        "id": "grammar_pattern:009",
        "kind": "grammar_pattern",
        "location": "line:102",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "00647b8474c9f57d171d47e797514a2f231041c78f2cdc97f3e289d804ece9c6",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "regard/view/treat 〈person/claim〉 with suspicion＝〈人・主張〉を疑いの目で見る"
      },
      {
        "id": "grammar_pattern:011",
        "kind": "grammar_pattern",
        "location": "line:102",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "71a448af5d5b52fe2a62c9b8cbc7851cb90ce058ae2235f2f96d63d9a35b72d1",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "suspicion of 〈person/group/idea〉＝〈人・集団・考え〉への不信"
      },
      {
        "id": "grammar_pattern:015",
        "kind": "grammar_pattern",
        "location": "line:173",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】～ではないかという気、確証のない推測",
        "text_sha256": "97bcf6700f683ef654902cbe48db71aeb8f1cce9fd1dc74f50a08024453ce418",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a suspicion that 〈節〉＝～ではないかという気"
      },
      {
        "id": "grammar_pattern:016",
        "kind": "grammar_pattern",
        "location": "line:173",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】～ではないかという気、確証のない推測",
        "text_sha256": "b2fc72853e7506721d961e8918195cb7663831f248ba59156aabea5c5e14319f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "have a suspicion that 〈節〉＝～ではないかと思う"
      },
      {
        "id": "grammar_pattern:023",
        "kind": "grammar_pattern",
        "location": "line:240",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配",
        "text_sha256": "b2be76c2a7e38194e62f6d5af1c2d54a3ccde0f8ac84d841d238866c01de3e0c",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a suspicion of 〈color/flavor/smell/emotion〉＝ほんの少しの〈色・味・匂い・感情〉"
      },
      {
        "id": "grammar_pattern:024",
        "kind": "grammar_pattern",
        "location": "line:240",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配",
        "text_sha256": "526a4b85202d813c75e1b0277d7b84f2e869d1dc4e70f37807e1232b9ddcfd03",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "with a suspicion of 〈smile/irony〉＝かすかな〈笑み・皮肉〉を帯びて。"
      },
      {
        "id": "pronunciation:001",
        "kind": "pronunciation",
        "location": "line:4",
        "section": "＃発音記号",
        "sense": "",
        "text_sha256": "aeb453109ae45430046966728abadb17f6b86fa859a14237e741a7772ada33dc",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "米: /səˈspɪʃən/｜英: /səˈspɪʃən/。3音節で、第2音節に主強勢がある。Oxford 系の辞書では語末を /ʃn/ と圧縮して表記することもあるが、Cambridge 系の /ʃ.ən/ と大きく異なる発音を示すものではない。語頭の su- は強く /suː/ と読まず、弱い /sə/ になる。"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "a7654a838f9be7fb84d0c69dcbef1925fac6359c41042f348c49ff83ad3cdf34",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "標準語。日常会話、報道、警察・司法関連の記事で広く使う。on suspicion of ...、under suspicion は報道や法執行の文脈で特に多い。ここでいう suspicion は有罪が立証されたことを意味しない。頻度の数値はこの辞書内の学習上の相対目安である。"
      },
      {
        "id": "sense_boundary:001",
        "kind": "sense_boundary",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "69cc762ea9830b45c2f5fc076e40e8138b2cebb6f7bd92578cc36de184c3aaa1",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "id": "sense_boundary:002",
        "kind": "sense_boundary",
        "location": "line:94",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "21d67591592c9ffb28fc5fef048a46bd7e7b11ae2256cb9c31b19acdd2deacd3",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "id": "sense_boundary:004",
        "kind": "sense_boundary",
        "location": "line:232",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配",
        "text_sha256": "3e827fd5807e3a67bc3fe0d583132bcba76b11b242b1bee1c63333d22b724e12",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配"
      },
      {
        "id": "synonym:004",
        "kind": "synonym",
        "location": "lines:135-140",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "6c85d93ae0f4196ce3e161f781447881899bd852594031b271e6d916982e9ec4",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・distrust\n定義: 人・組織・情報などを信用できないという感覚。\n頻度: 〈8/10〉\n違い: distrust は信用の欠如そのものを直接表し、suspicion はその背後に隠れた問題・意図があるのではないかという推測を帯びやすい。\n例: Public distrust increased after the data leak.\n訳: データ流出後、世間の不信が強まった。"
      },
      {
        "id": "synonym:005",
        "kind": "synonym",
        "location": "lines:142-147",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "01f2a05c9ebc86a6e876d37c9664ca1543d28438a36043c6b72a1fd27353d479",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・mistrust\n定義: 人・物事を十分には信頼しないこと。\n頻度: 〈7/10〉\n違い: mistrust は distrust に近い一般的な不信。suspicion はより「何か怪しい」という感覚を含みやすい。\n例: There was longstanding mistrust between the two groups.\n訳: その二つの集団の間には長年の不信があった。"
      },
      {
        "id": "usage_note:004",
        "kind": "usage_note",
        "location": "line:264",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配",
        "text_sha256": "d843c726be3ff6954e206561628e942c41a2506db2a486acc884ef0a0c2e227f",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "この a suspicion of ... は「～を疑うこと」ではなく、「～がほんの少し存在すること」である。文体的な比喩なので、意味を誤解されそうな場面では a hint of、a touch of、a trace of が無難である。一部の辞書には suspicion を動詞「疑う」として扱う非標準・方言的な用法も載るが、現代の標準英語では通常 suspect を使うため、本記事では主要語義として立てない。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "a3a4c491bedb0731ae8a24864d7909920b1bbde1b0b73ebc0c19911ed929dc9a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・suspect：動詞では「～ではないかと疑う、〈人〉を犯人・不正の当事者ではないかと疑う」、名詞では「容疑者」、形容詞では「疑わしい、怪しい」。suspicion はその「疑い・疑念」を名詞として表す。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "09ba73c440481a2ed0fc2e777885e48f81b5476e9a08204bd07c49e7d8d0d6e8",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・suspicious：形容詞。「疑っている、怪しいと思っている」または「疑わしい、怪しい」。人の心理と、対象の性質の両方を表せる。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "d9ec33ee4673dba286dc91c01049c2d4f9e7ef4e94f82d53a7b39aedb4a8d2eb",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・suspiciously：副詞。「疑わしそうに、怪しいほど」。行動の見え方にも、程度が不自然に高いことにも使う。"
      }
    ]
  },
  "specification_sha256": "f0de393d4d064190e23916b2e8bfda25b2b83fd29e14cf52395c894b8539d7e9",
  "source_artifact_sha256": "358a6ef905363f010a31dece02f1dd57e94ea0fad57f759488d3898360d8fc54",
  "normalized_input_sha256": "1d72af3e95597ba7111df3d34a2c548f1c927b28ed489e88e573df9084837076"
}
```
