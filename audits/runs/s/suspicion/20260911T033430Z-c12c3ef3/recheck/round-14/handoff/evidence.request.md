# Independent checker handoff

Pass: `evidence`

Review only the exact input packet included below and the specified checker prompt. Use an independent context. Do not consult earlier review outputs, resolutions, or final-blind findings. Return a single JSON object with the requested pass result. Set `reviewer.mode` to `handoff`, `reviewer.declared_model` to the actual model name available to you (do not guess), `reviewer.ingested_by` to `human`, and `reviewer.agent_id` to your actual unique agent path. Do not reuse an agent_id from another pass.

## Checker prompt

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

## 頻度の評価基準

entry_spec_v5 の頻度スコアは英語全体での遭遇頻度を10段階で示す編集上の定性的な目安であり、厳密な統計値がないことだけで不合格にしない。本文の頻度基準・地域・専門・古風の限定を合わせて検査する。実測値を装う記述、出典との矛盾、地域限定義や古語の過大評価は引き続き指摘する。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "evidence",
  "taxonomy_ids": [
    "evidence_claim_mismatch"
  ],
  "specification": "prompts/check_pass_evidence_v7.md",
  "input_body_sha256": "8508fef1bf79309ca9c904c1a5b901698298454c0b9cddf6fe1227383f20bc7c",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "Oxford は米・英とも /səˈspɪʃn/ と表記する。Merriam-Webster の音節を区切る発音綴りは sə-ˈspi-shən で、3音節、第2音節に主強勢があることを示す。語頭の su- は強く /suː/ と読まず、弱い /sə/ になる。  "
      }
    ],
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "suspicion は中英語を経て、アングロフランス語／古フランス語形から英語に入った。語源資料はラテン語形を Oxford が suspectio(n-)、Merriam-Webster が suspicion- / suspicio、Etymonline が後期ラテン語 suspectionem（主格 suspectio）と記している。語源はラテン語 suspicere に関係し、英語の綴りには14世紀の古フランス語形の影響があったとされる。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "Oxford は suspect（動詞・名詞・形容詞）、suspicious（形容詞）、suspiciously（副詞）を suspicion の語族として挙げている。各語の詳しい意味はそれぞれの項目を参照。  "
      },
      {
        "line": 24,
        "text": "なお、動詞 suspicion は Merriam-Webster では主に方言的、American Heritage では口語的な用法として記載されるが、本記事ではその動詞用法を扱わず、名詞用法のみを説明する。  "
      }
    ],
    "core_image": [
      {
        "line": 26,
        "text": "＃コアイメージ"
      },
      {
        "line": 28,
        "text": "語義1は人の犯罪・不正の可能性や、その疑いを向けられた状態を表し、語義2は相手や情報への一般的な不信を表す。語義3は特定の人の不正を疑うのでなく、犯罪・不正を前提としない事実や状況についての推測を表す。語義4はこれらと分けて、何かがごくわずかに感じられることを表す。  "
      },
      {
        "line": 29,
        "text": "・人が犯罪・不正をしたのではないかと見る → 「容疑、疑い」（語義1）  "
      },
      {
        "line": 30,
        "text": "・相手や考えをそのまま信用してよいのかと構える → 「不信、疑念」（語義2）  "
      },
      {
        "line": 31,
        "text": "・犯罪・不正を前提としない事実や状況が本当なのではないかと推測する → 「気がすること、疑い、予感」（語義3）  "
      },
      {
        "line": 32,
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
        "text": "【日本語訳・定義】人が犯罪、不正、不誠実な行為などをした可能性があると、十分な証明がない段階で考えること、またはその疑いを向けられている状態を表す。複数の個別の疑いを述べる suspicions は可算、疑いという状態を表す suspicion は不可算で使われる。on suspicion of ... のように特定の容疑でも無冠詞となる定型表現があるため、可算・不可算は意味だけで一律には決まらない。  "
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
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 138,
        "text": "【日本語訳・定義】特定の人が犯罪・不正をしたという疑いではなく、犯罪・不正を前提としない事実や状況が本当なのではないかと、確証のないまま感じることを表す。人物への容疑や一般的な不信ではなく、「そうではないか」という推測・予感に焦点がある。この意味では a suspicion that ... のように個々の考えを表す可算形が典型。可算・不可算は意味だけで一律に決まらず、構文にも左右される。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 188,
        "text": "【日本語訳・定義】色、味、匂い、感情、表情などが、はっきり大量に存在するのではなく「あるかないか分かる程度」にわずかに感じられることを表す。通常 a suspicion of ... の形で用いられる比喩的な用法である。  "
      }
    ],
    "frequency_register": [
      {
        "line": 36,
        "text": "【頻度表記】頻度スコアは語全体の使用回数やコーパス値ではなく、直前の定義が示す語義について、現代英語全体での遭遇機会を編集上評価した目安である。10＝会話・文章で日常的に出会う基本語、8～9＝日常・新聞・ビジネスで広く使われる、6～7＝使われる機会はあるが語義や場面がやや限られる、4～5＝比較的限られた場面で使われる、2～3＝特定の分野・地域・文体に偏る、1＝現代英語ではまれ。厳密な統計値や語義間の順位を示さない。  "
      },
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
        "text": "【レジスター/領域】一般名詞。辞書には on suspicion of ... を逮捕理由として用いる例がある。Merriam-Webster は法的な suspicion を、証明やわずかな証拠しかない段階で、何かが間違っている、またはある事実が存在すると考える、通常は信念に至らない心理状態として説明する。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 95,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 97,
        "text": "【レジスター/領域】一般的な用法。with suspicion は人や物事を信用せずに見る態度を表す。  "
      },
      {
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 140,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 142,
        "text": "【レジスター/領域】a suspicion that ...、a sneaking suspicion などの形で用いる。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 190,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 192,
        "text": "【レジスター/領域】Oxford はこの意味に formal のラベルを付け、hint を類義語として挙げている。  "
      }
    ],
    "frames": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 46,
        "text": "【文法パターン】suspicion that 〈節〉＝～ではないかという疑い／suspicion of 〈crime/wrongdoing〉＝〈犯罪・不正〉の疑い／suspicions about 〈person/behavior〉＝〈人・行動〉に関する疑い／arouse/raise suspicion＝疑いを招く／on suspicion of 〈crime〉＝〈犯罪〉の容疑で／be under suspicion＝疑いをかけられている／come/fall under suspicion＝疑いをかけられるようになる／cast suspicion on 〈person/action suspected of wrongdoing〉＝〈人・行為〉に犯罪・不正の疑いを向ける／confirm suspicions that 〈節〉＝～という疑いを裏付ける。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 99,
        "text": "【文法パターン】regard/view 〈person/claim/proposal/action/decision〉 with suspicion＝〈人・主張・提案・行為・決定〉を疑いの目で見る／〈offer/proposal〉 be greeted with (some) suspicion＝〈申し出・提案〉が（多少の）疑いをもって受け止められる／cast suspicion on 〈claim/statement〉＝〈主張・説明〉の真実性・信頼性に疑いを向ける。  "
      },
      {
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 144,
        "text": "【文法パターン】a suspicion that 〈節〉＝～ではないかという気／have a suspicion that 〈節〉＝～ではないかと思う／a sneaking suspicion that 〈節〉＝ひそかに～ではないかと思う気持ち／a strong suspicion that 〈節〉＝強い疑い／confirm a suspicion＝推測を裏付ける。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 194,
        "text": "【文法パターン】a suspicion of 〈color/flavor/smell/emotion〉＝ほんの少しの〈色・味・匂い・感情〉／a suspicion of a smile＝かすかな笑み。  "
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
        "text": "例: The unexplained transfer of client funds aroused suspicion of fraud among the auditors.  "
      },
      {
        "line": 53,
        "text": "訳: 顧客資金の説明のない移動が、監査担当者たちに詐欺の疑いを抱かせた。  "
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
        "text": "例: The security footage confirmed the manager's suspicions that a guard had taken the missing laptops.  "
      },
      {
        "line": 78,
        "text": "訳: 防犯映像によって、警備員がなくなったノートパソコンを持ち去ったという管理者の疑いが裏付けられた。  "
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
        "line": 113,
        "text": "・cast suspicion on 〈claim/statement〉  "
      },
      {
        "line": 114,
        "text": "用途: 主張や説明の真実性・信頼性を疑わしいものとして扱うことを表す。  "
      },
      {
        "line": 115,
        "text": "例: The discrepancy cast suspicion on the reliability of the company's explanation.  "
      },
      {
        "line": 116,
        "text": "訳: その食い違いによって、その会社の説明の信頼性に疑いが向けられた。  "
      },
      {
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 146,
        "text": "【コロケーション】"
      },
      {
        "line": 148,
        "text": "・have a suspicion that 〈clause〉  "
      },
      {
        "line": 149,
        "text": "用途: 十分な証拠はないが、あることが本当ではないかと感じていることを表す。  "
      },
      {
        "line": 150,
        "text": "例: I have a suspicion that the meeting will finish earlier than planned.  "
      },
      {
        "line": 151,
        "text": "訳: その会議は予定より早く終わるのではないかという気がしている。  "
      },
      {
        "line": 153,
        "text": "・a sneaking suspicion that 〈clause〉  "
      },
      {
        "line": 154,
        "text": "用途: はっきり認めるほどではないが、心のどこかでそう思っていることを表す。  "
      },
      {
        "line": 155,
        "text": "例: She had a sneaking suspicion that everyone already knew the answer.  "
      },
      {
        "line": 156,
        "text": "訳: 彼女は、皆すでに答えを知っているのではないかとひそかに感じていた。  "
      },
      {
        "line": 158,
        "text": "・a strong suspicion that 〈clause〉  "
      },
      {
        "line": 159,
        "text": "用途: あることが本当ではないかという強い推測を表す。  "
      },
      {
        "line": 160,
        "text": "例: We had a strong suspicion that the delay was caused by a technical problem.  "
      },
      {
        "line": 161,
        "text": "訳: 私たちは、その遅延は技術的な問題によるのではないかという強い疑いを抱いていた。  "
      },
      {
        "line": 163,
        "text": "・confirm a suspicion  "
      },
      {
        "line": 164,
        "text": "用途: それまで確証のなかった推測が、後の情報によって正しかったと分かる。  "
      },
      {
        "line": 165,
        "text": "例: The test results confirmed her suspicion that the battery was failing.  "
      },
      {
        "line": 166,
        "text": "訳: 検査結果によって、バッテリーが劣化しているのではないかという彼女の推測が裏付けられた。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 196,
        "text": "【コロケーション】"
      },
      {
        "line": 198,
        "text": "・a suspicion of 〈color〉  "
      },
      {
        "line": 199,
        "text": "用途: 色合いがごくわずかに混じって見えることを描写する。  "
      },
      {
        "line": 200,
        "text": "例: The walls were white with a suspicion of blue in the evening light.  "
      },
      {
        "line": 201,
        "text": "訳: その壁は白かったが、夕方の光の中ではほんのり青みを帯びていた。  "
      },
      {
        "line": 203,
        "text": "・a suspicion of 〈flavor〉  "
      },
      {
        "line": 204,
        "text": "用途: 味や香りがごく弱く感じられることを表す。  "
      },
      {
        "line": 205,
        "text": "例: The sauce had a suspicion of citrus that made it taste fresher.  "
      },
      {
        "line": 206,
        "text": "訳: そのソースにはほんのり柑橘の風味があり、より爽やかに感じられた。  "
      },
      {
        "line": 208,
        "text": "・a suspicion of 〈emotion〉  "
      },
      {
        "line": 209,
        "text": "用途: 感情が表情・声などにわずかに現れていることを描写する。  "
      },
      {
        "line": 210,
        "text": "例: There was a suspicion of disappointment in his voice.  "
      },
      {
        "line": 211,
        "text": "訳: 彼の声にはかすかな失望がにじんでいた。  "
      },
      {
        "line": 213,
        "text": "・a suspicion of a smile  "
      },
      {
        "line": 214,
        "text": "用途: はっきり笑うほどではない、わずかな笑みを描写する。  "
      },
      {
        "line": 215,
        "text": "例: A suspicion of a smile appeared at the corner of her mouth.  "
      },
      {
        "line": 216,
        "text": "訳: 彼女の口元に、かすかな笑みが浮かんだ。  "
      }
    ],
    "usage_notes": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 80,
        "text": "【語法・注意】on suspicion of theft は「窃盗の疑いを理由に」という定型表現である。under suspicion は、Oxford の説明では不正をしたのではないかと疑われている状態を表す。accusation や allegation は類義語ではなく、誰かが不正をしたという主張・告発を指す関連語である。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 118,
        "text": "【語法・注意】with suspicion は「疑いの目で、信用せずに」という態度を表す。Oxford と American Heritage はこの語義を distrust / lack of confidence と説明する。Merriam-Webster は suspicion が真実性・現実性・公正さ・信頼性への信頼の薄さを強調すると説明し、mistrust は疑いに基づく信頼の欠如を強調するとしている。  "
      },
      {
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 168,
        "text": "【語法・注意】この語義では内容が必ず悪いとは限らない。I have a suspicion that she may surprise us with good news. のように、中立・肯定的な内容についても「そうではないかという気」を表せる。この語義は、犯罪・不正を疑う意味や人物への不信とは異なり、非難を伴わない事実推測を表す。suspicion that ... の that は内容を導く接続詞で、suspicion of ... の of は名詞句を取る。a sneaking suspicion の sneaking はここでは「盗み歩く」という直訳ではなく、表立って確信してはいないが心の中にある感覚を表す。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 218,
        "text": "【語法・注意】この a suspicion of ... は「～を疑うこと」ではなく、「～がほんの少し存在すること」である。  "
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
        "line": 120,
        "text": "【類義語】"
      },
      {
        "line": 122,
        "text": "・distrust  "
      },
      {
        "line": 123,
        "text": "定義: 人・組織・情報などを信用できないという感覚。  "
      },
      {
        "line": 124,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 125,
        "text": "違い: distrust はこの意味での近い語で、信用できない状態を直接表す。suspicion は、真実性・公正さ・信頼性などへの信頼が薄いことを表す場合がある。  "
      },
      {
        "line": 126,
        "text": "例: Public distrust increased after the data leak.  "
      },
      {
        "line": 127,
        "text": "訳: データ流出後、世間の不信が強まった。  "
      },
      {
        "line": 129,
        "text": "・mistrust  "
      },
      {
        "line": 130,
        "text": "定義: 人・物事を十分には信頼しないこと。  "
      },
      {
        "line": 131,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 132,
        "text": "違い: Merriam-Webster の説明では、mistrust は suspicion に基づく信頼の欠如を強調する。  "
      },
      {
        "line": 133,
        "text": "例: There was longstanding mistrust between the two groups.  "
      },
      {
        "line": 134,
        "text": "訳: その二つの集団の間には長年の不信があった。  "
      },
      {
        "line": 136,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 170,
        "text": "【類義語】"
      },
      {
        "line": 172,
        "text": "・doubt  "
      },
      {
        "line": 173,
        "text": "定義: ある事実が真実かどうか、確信が持てないこと。  "
      },
      {
        "line": 174,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 175,
        "text": "違い: doubt は真偽への不確かさを広く表す。suspicion は「そうではないか」という暫定的な見方や予感に焦点がある。  "
      },
      {
        "line": 176,
        "text": "例: The test results raised doubts about whether the battery was failing.  "
      },
      {
        "line": 177,
        "text": "訳: 検査結果から、バッテリーが劣化しているのかどうか疑問が生じた。  "
      },
      {
        "line": 179,
        "text": "・belief  "
      },
      {
        "line": 180,
        "text": "定義: 十分な証明がなくても、あることが真実だと考えること。  "
      },
      {
        "line": 181,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 182,
        "text": "違い: belief はその考えへの確信を広く表し、疑いや不安を含むとは限らない。suspicion は確証のない見立てであることを前面に出す。  "
      },
      {
        "line": 183,
        "text": "例: The team had a strong belief that the repairs would solve the problem.  "
      },
      {
        "line": 184,
        "text": "訳: チームは修理で問題が解決すると強く考えていた。  "
      },
      {
        "line": 186,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 220,
        "text": "【類義語】"
      },
      {
        "line": 222,
        "text": "・hint  "
      },
      {
        "line": 223,
        "text": "定義: 色・味・感情などのかすかな兆し・少量。  "
      },
      {
        "line": 224,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 225,
        "text": "違い: hint はこの「少量」の意味で一般的。suspicion はやや改まった表現で、あえて「感じ取れる程度」という含みを出す。  "
      },
      {
        "line": 226,
        "text": "例: The tea has a hint of mint.  "
      },
      {
        "line": 227,
        "text": "訳: そのお茶にはほのかなミントの風味がある。  "
      },
      {
        "line": 229,
        "text": "・trace  "
      },
      {
        "line": 230,
        "text": "定義: かろうじて認められるごく少量・痕跡。  "
      },
      {
        "line": 231,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 232,
        "text": "違い: trace は量の少なさや痕跡性を直接表す。suspicion は比喩的で、感覚的な描写に使われやすい。  "
      },
      {
        "line": 233,
        "text": "例: There was only a trace of smoke in the air.  "
      },
      {
        "line": 234,
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
  "evidence_context": {
    "schema_version": "evidence_context_v2",
    "input_body_sha256": "8508fef1bf79309ca9c904c1a5b901698298454c0b9cddf6fe1227383f20bc7c",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "3e7ba747339a13859b8bb250b1868c9533207d7605822df36e6ffbf029ce37ae",
    "source_first_artifact_sha256": "dc02fc70b5f11b78e5105b0158a8a845a6314d562d748f4e571433de0e727341",
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
          "grammar_pattern:013",
          "grammar_pattern:014",
          "grammar_pattern:015",
          "grammar_pattern:016",
          "grammar_pattern:017"
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
          "grammar_pattern:010",
          "grammar_pattern:011",
          "grammar_pattern:012",
          "collocation:007",
          "collocation:008",
          "collocation:009",
          "synonym:002",
          "synonym:003"
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
          "grammar_pattern:018",
          "grammar_pattern:019",
          "collocation:014",
          "collocation:015",
          "collocation:016",
          "collocation:017"
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
          "word_formation:001"
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
          "word_formation:002"
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
        "location": "lines:92-95",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "89cf4c87e8287d3549d92f194ba7e76813eb54c7e5880cc21e0b10e819a9e772",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・regard/view 〈person/claim/proposal/action/decision〉 with suspicion\n用途: 人・主張・提案・行為・決定をすぐには信用せず、疑いの目で見ることを表す。\n例: Residents viewed the sudden policy change with suspicion.\n訳: 住民たちは突然の方針変更を疑いの目で見た。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:97-100",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "ab0a05a905edc2a6465eeb57d522c7c1c95c37db2fcd2ceeb87a97c22658a463",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・be greeted with (some) suspicion\n用途: 申し出・提案などが、当初は信用されず、疑いをもって受け止められることを表す。\n例: The new monitoring system was initially greeted with some suspicion.\n訳: 新しい監視システムは当初、多少の疑いをもって受け止められた。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:102-105",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "2ce77007c0e4a5d3afcf6c68b3197e7beac0b68edfce8126289dc1cd9d25d7b7",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・cast suspicion on 〈claim/statement〉\n用途: 主張や説明の真実性・信頼性を疑わしいものとして扱うことを表す。\n例: The discrepancy cast suspicion on the reliability of the company's explanation.\n訳: その食い違いによって、その会社の説明の信頼性に疑いが向けられた。"
      },
      {
        "id": "collocation:014",
        "kind": "collocation",
        "location": "lines:187-190",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配",
        "text_sha256": "1118f1caca791c946a4374f28956ecb690a469665d6aaa286dbd7795f5f84a39",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a suspicion of 〈color〉\n用途: 色合いがごくわずかに混じって見えることを描写する。\n例: The walls were white with a suspicion of blue in the evening light.\n訳: その壁は白かったが、夕方の光の中ではほんのり青みを帯びていた。"
      },
      {
        "id": "collocation:015",
        "kind": "collocation",
        "location": "lines:192-195",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配",
        "text_sha256": "c89a2a8c8073d7afe0baf46085b64ac90bb6c7a93c29d405413a771b58175f0d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a suspicion of 〈flavor〉\n用途: 味や香りがごく弱く感じられることを表す。\n例: The sauce had a suspicion of citrus that made it taste fresher.\n訳: そのソースにはほんのり柑橘の風味があり、より爽やかに感じられた。"
      },
      {
        "id": "collocation:016",
        "kind": "collocation",
        "location": "lines:197-200",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配",
        "text_sha256": "8de4791b39bd28319bb7b4a9677fdf24141e7947ed0b7e7834c7b57795cf171e",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a suspicion of 〈emotion〉\n用途: 感情が表情・声などにわずかに現れていることを描写する。\n例: There was a suspicion of disappointment in his voice.\n訳: 彼の声にはかすかな失望がにじんでいた。"
      },
      {
        "id": "collocation:017",
        "kind": "collocation",
        "location": "lines:202-205",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配",
        "text_sha256": "d9af8abc4846116ac9c3efed992840d1bd02bfc190f7784568e1ac489f307d03",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a suspicion of a smile\n用途: はっきり笑うほどではない、わずかな笑みを描写する。\n例: A suspicion of a smile appeared at the corner of her mouth.\n訳: 彼女の口元に、かすかな笑みが浮かんだ。"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:29",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "55ec2c7a535a203bbb25fed2dec7c06a8406d146b9a187e060697870913d7a73",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "人が犯罪、不正、不誠実な行為などをした可能性があると、十分な証明がない段階で考えること、またはその疑いを向けられている状態を表す。複数の個別の疑いを述べる suspicions は可算、疑いという状態を表す suspicion は不可算で使われる。on suspicion of ... のように特定の容疑でも無冠詞となる定型表現があるため、可算・不可算は意味だけで一律には決まらない。"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:82",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "5339e3d19a1009b5ddf7e927e8e81890190fea3b1a9bd3aa513bfd5c6985122a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "人、組織、動機、考えなどの真実性や信頼性を確信できず、すぐには信用しない態度を表す。相手や情報の裏に問題や意図があるのではないかという警戒を伴うこともある。語義1のように特定の犯罪・不正行為を想定する必要はなく、広い意味での mistrust / distrust に近い。"
      },
      {
        "id": "definition:003",
        "kind": "definition",
        "location": "line:127",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算中心】～ではないかという気、確証のない推測",
        "text_sha256": "15d2e38a868b9cb7f14e26eafd6b01f73ca6efef73aa0a3b1d1706f626a5eee8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "特定の人が犯罪・不正をしたという疑いではなく、犯罪・不正を前提としない事実や状況が本当なのではないかと、確証のないまま感じることを表す。人物への容疑や一般的な不信ではなく、「そうではないか」という推測・予感に焦点がある。この意味では a suspicion that ... のように個々の考えを表す可算形が典型。可算・不可算は意味だけで一律に決まらず、構文にも左右される。"
      },
      {
        "id": "definition:004",
        "kind": "definition",
        "location": "line:177",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配",
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
        "text_sha256": "2dd21a934dd67e740c409da842da789c3d0aadc89132c39ce8aee776f4d70fd4",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "suspicion は中英語を経て、アングロフランス語／古フランス語形から英語に入った。語源資料はラテン語形を Oxford が suspectio(n-)、Merriam-Webster が suspicion- / suspicio、Etymonline が後期ラテン語 suspectionem（主格 suspectio）と記している。語源はラテン語 suspicere に関係し、英語の綴りには14世紀の古フランス語形の影響があったとされる。"
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
        "id": "grammar_pattern:010",
        "kind": "grammar_pattern",
        "location": "line:88",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "8d131f23fb824b5c797e9ad9770855251e0e6b648321faa370e6e153507e27a8",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "regard/view 〈person/claim/proposal/action/decision〉 with suspicion＝〈人・主張・提案・行為・決定〉を疑いの目で見る"
      },
      {
        "id": "grammar_pattern:011",
        "kind": "grammar_pattern",
        "location": "line:88",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "957c27037e22644519a8e762108eed0d1b72d12b212af2c743a5c611f6ae716d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "〈offer/proposal〉 be greeted with (some) suspicion＝〈申し出・提案〉が（多少の）疑いをもって受け止められる"
      },
      {
        "id": "grammar_pattern:012",
        "kind": "grammar_pattern",
        "location": "line:88",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "21bd5e5b3053eec66f458629cf15b1d168362223de568b72d8adf2d3026e96cf",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "cast suspicion on 〈claim/statement〉＝〈主張・説明〉の真実性・信頼性に疑いを向ける。"
      },
      {
        "id": "grammar_pattern:013",
        "kind": "grammar_pattern",
        "location": "line:133",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算中心】～ではないかという気、確証のない推測",
        "text_sha256": "97bcf6700f683ef654902cbe48db71aeb8f1cce9fd1dc74f50a08024453ce418",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a suspicion that 〈節〉＝～ではないかという気"
      },
      {
        "id": "grammar_pattern:014",
        "kind": "grammar_pattern",
        "location": "line:133",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算中心】～ではないかという気、確証のない推測",
        "text_sha256": "b2fc72853e7506721d961e8918195cb7663831f248ba59156aabea5c5e14319f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "have a suspicion that 〈節〉＝～ではないかと思う"
      },
      {
        "id": "grammar_pattern:015",
        "kind": "grammar_pattern",
        "location": "line:133",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算中心】～ではないかという気、確証のない推測",
        "text_sha256": "e3d9b60b4c8d339330741db8f3af98e47c3489641070740676c6048f2daf8cc6",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a sneaking suspicion that 〈節〉＝ひそかに～ではないかと思う気持ち"
      },
      {
        "id": "grammar_pattern:016",
        "kind": "grammar_pattern",
        "location": "line:133",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算中心】～ではないかという気、確証のない推測",
        "text_sha256": "79c3819875e459049bbce8c995716c14b5b4c34bb30e62effb483e67abf6becb",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a strong suspicion that 〈節〉＝強い疑い"
      },
      {
        "id": "grammar_pattern:017",
        "kind": "grammar_pattern",
        "location": "line:133",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算中心】～ではないかという気、確証のない推測",
        "text_sha256": "49730bb23853be373a3538f5cfb82107abc1b0c1fb8c500a174820d5fc69cee4",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "confirm a suspicion＝推測を裏付ける。"
      },
      {
        "id": "grammar_pattern:018",
        "kind": "grammar_pattern",
        "location": "line:183",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配",
        "text_sha256": "b2be76c2a7e38194e62f6d5af1c2d54a3ccde0f8ac84d841d238866c01de3e0c",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a suspicion of 〈color/flavor/smell/emotion〉＝ほんの少しの〈色・味・匂い・感情〉"
      },
      {
        "id": "grammar_pattern:019",
        "kind": "grammar_pattern",
        "location": "line:183",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配",
        "text_sha256": "fc8db1aa5afdb3fe49cdcfbd51376a710140e533ceb1d70f1bf70eebb622edf3",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a suspicion of a smile＝かすかな笑み。"
      },
      {
        "id": "pronunciation:001",
        "kind": "pronunciation",
        "location": "line:4",
        "section": "＃発音記号",
        "sense": "",
        "text_sha256": "2d3f23b9fc96355db131e2dd4e85fba733a67a0ef62cca4ea64f85355a890f9f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "Oxford は米・英とも /səˈspɪʃn/ と表記する。Merriam-Webster の音節を区切る発音綴りは sə-ˈspi-shən で、3音節、第2音節に主強勢があることを示す。語頭の su- は強く /suː/ と読まず、弱い /sə/ になる。"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "text_sha256": "3fbeea497a7e4718e9a93f32cf75ccded4322c9c28507ce95aaf873410628865",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "一般名詞。辞書には on suspicion of ... を逮捕理由として用いる例がある。Merriam-Webster は法的な suspicion を、証明やわずかな証拠しかない段階で、何かが間違っている、またはある事実が存在すると考える、通常は信念に至らない心理状態として説明する。"
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
        "location": "line:80",
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
        "location": "line:175",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配",
        "text_sha256": "5ba1f4d2559161fc63f210f9fd66563b4d517f531a646cf6301a4df6d5287e07",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "id": "synonym:002",
        "kind": "synonym",
        "location": "lines:111-116",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "f4a7fef9a38c6c173d8ca8b4a859b434b5d9a95171412e0a9003c61428bc7d44",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・distrust\n定義: 人・組織・情報などを信用できないという感覚。\n頻度: 〈8/10〉\n違い: distrust はこの意味での近い語で、信用できない状態を直接表す。suspicion は、真実性・公正さ・信頼性などへの信頼が薄いことを表す場合がある。\n例: Public distrust increased after the data leak.\n訳: データ流出後、世間の不信が強まった。"
      },
      {
        "id": "synonym:003",
        "kind": "synonym",
        "location": "lines:118-123",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "text_sha256": "57668a0f0d31229a6a2c118fde6a98fc207b1490ae4434cebd5037e93344fe80",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・mistrust\n定義: 人・物事を十分には信頼しないこと。\n頻度: 〈7/10〉\n違い: Merriam-Webster の説明では、mistrust は suspicion に基づく信頼の欠如を強調する。\n例: There was longstanding mistrust between the two groups.\n訳: その二つの集団の間には長年の不信があった。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "7065b442456724c92e7a577fc24069776baf20f64c597cf40ec6defcc31772aa",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "Oxford は suspect（動詞・名詞・形容詞）、suspicious（形容詞）、suspiciously（副詞）を suspicion の語族として挙げている。各語の詳しい意味はそれぞれの項目を参照。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "bf560e16d34526852fc4487bfbace519494b62fcb7f8d746b1b22654d4cd8ff8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "なお、動詞 suspicion は Merriam-Webster では主に方言的、American Heritage では口語的な用法として記載されるが、本記事ではその動詞用法を扱わず、名詞用法のみを説明する。"
      }
    ]
  },
  "specification_sha256": "e372f665bc0a79993669da4879e33456e4f8542f6fac523fa0d665c92986b89c",
  "source_artifact_sha256": "dc02fc70b5f11b78e5105b0158a8a845a6314d562d748f4e571433de0e727341",
  "normalization_version": "check_pass_semantic_input_v2",
  "normalized_input_sha256": "a7512e396b2b17e7bd6f511281f876191fd7d4f7764bd72a18b41664f8c989a3"
}
```
