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
  "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米: /ˌkɑːntrəˈvɝːʃəl/｜英: /ˌkɒntrəˈvɜːʃəl/。米英とも4音節で、第3音節の /vɝː/・/vɜː/ に主強勢がある。第1音節の /ˌkɑːn/・/ˌkɒn/ には副次強勢を示す。米語では /ˌkɑːntrəˈvɝːsiəl/ に近い5音節寄りの発音も聞かれるが、通常の学習上は /ˈvɝːʃəl/・/ˈvɜːʃəl/ の部分を基準にする。  "
      }
    ],
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "16世紀後半に使われ始めた語で、後期ラテン語 controversialis「論争に関する」から来た。controversia「論争」は controversus「反対方向に向けられた、争われた」に関係し、contra-/contro-「反対に」と versus「向けられた、転じた」（vertere「向きを変える」の過去分詞）に分けて考えられる。初出年代は資料により1580年代、1583年、1575–85年など差があるため、特定の年として暗記しない。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・controversy：名詞。「論争、論争点、物議」。controversial と同じ語族の中心語で、public controversy のように使う。  "
      },
      {
        "line": 24,
        "text": "・controversially：副詞。「物議を醸す形で、論争を呼ぶことに」。文全体や発言・判断の仕方を修飾する。  "
      },
      {
        "line": 25,
        "text": "・controversialist：名詞。「論争家、論争に加わる人」。人の性向または論争上の立場を指す硬めの語。  "
      },
      {
        "line": 26,
        "text": "・controvert：動詞。「反論する、論駁する」。controversial と意味は近いが、現代英語では controversial の直接の活用形ではなく、別の動詞として扱う。  "
      }
    ],
    "core_image": [],
    "sense_structure": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 32,
        "text": "【日本語訳・定義】政策・決定・主張・作品・発言・人物などが、社会全体または特定の集団の中で、強い意見の対立、批判、反対を引き起こしていることを表す。事実として真偽が決まっていないことを必ずしも含まず、悪い、違法、意図的に挑発的だという意味でもない。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 158,
        "text": "【日本語訳・定義】人が性格や態度の傾向として、議論を好んだり、既存の立場に反論して対立を生みやすかったりすることを表す。辞書に記載される低頻度の語義で、現代の controversial person は通常、語義1の「論争の的となっている人物」と解釈される。  "
      }
    ],
    "frequency_register": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 34,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 36,
        "text": "【レジスター/領域】標準語で、会話・ニュース・政治・文化・学術・ビジネスの文章まで広く使う。controversial は「多くの人が反対している」と同じではなく、賛成・反対の議論が強く起きている状態を指す。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 160,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 162,
        "text": "【レジスター/領域】まれで、辞書的・形式的・文学的な説明に現れやすい。現代の一般的な文章で人の性向を表すなら argumentative、disputatious、polemical の方が意味を明確にしやすい。  "
      }
    ],
    "frames": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 38,
        "text": "【文法パターン】be/become/remain/prove controversial＝論争を呼ぶ・論争の的であり続ける・結果的に物議を醸す／a controversial 〈issue・decision・policy・claim・statement・figure・book・film〉＝論争を呼ぶ〈問題・決定・政策・主張・発言・人物・本・映画〉／highly/widely controversial＝非常に／広く物議を醸す／controversial among/within 〈group〉＝〈集団〉の間で論争を呼ぶ／controversial in some circles＝一部の界隈では物議を醸す／it remains controversial whether ...＝…かどうかは依然として議論が分かれる／be controversial enough to do＝～するほど物議を醸す／too controversial to do＝物議を醸しすぎて～できない。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 164,
        "text": "【文法パターン】a controversial temperament＝論争を好む気質／a controversial manner＝対立を生みやすい態度／be controversial by temperament＝性向として論争的である／be controversial in debate＝議論で意図的に反論を重ねる。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 40,
        "text": "【コロケーション】"
      },
      {
        "line": 42,
        "text": "・a controversial issue  "
      },
      {
        "line": 43,
        "text": "用途: 社会的に賛否が対立している問題を指す。  "
      },
      {
        "line": 44,
        "text": "例: The use of facial-recognition technology remains a controversial issue.  "
      },
      {
        "line": 45,
        "text": "訳: 顔認証技術の利用は依然として論争を呼ぶ問題だ。  "
      },
      {
        "line": 47,
        "text": "・a controversial decision  "
      },
      {
        "line": 48,
        "text": "用途: 決定の妥当性や影響をめぐって強い反対・批判が出ていることを表す。  "
      },
      {
        "line": 49,
        "text": "例: The committee made a controversial decision to cancel the exhibition.  "
      },
      {
        "line": 50,
        "text": "訳: 委員会は展示会を中止するという物議を醸す決定を下した。  "
      },
      {
        "line": 52,
        "text": "・a controversial figure  "
      },
      {
        "line": 53,
        "text": "用途: 功績と批判の両方があり、評価が大きく割れている人物を指す。  "
      },
      {
        "line": 54,
        "text": "例: The historian remains a controversial figure in the region.  "
      },
      {
        "line": 55,
        "text": "訳: その歴史家はその地域で今も評価が大きく分かれる人物だ。  "
      },
      {
        "line": 57,
        "text": "・a highly controversial proposal  "
      },
      {
        "line": 58,
        "text": "用途: 提案に対して非常に強い賛否や反発が起きていることを強調する。  "
      },
      {
        "line": 59,
        "text": "例: The city council postponed a highly controversial proposal.  "
      },
      {
        "line": 60,
        "text": "訳: 市議会は非常に物議を醸している提案を延期した。  "
      },
      {
        "line": 62,
        "text": "・controversial among 〈group〉  "
      },
      {
        "line": 63,
        "text": "用途: どの集団の中で意見が割れているかを限定する。  "
      },
      {
        "line": 64,
        "text": "例: The interpretation is controversial among constitutional scholars.  "
      },
      {
        "line": 65,
        "text": "訳: その解釈は憲法学者の間で議論が分かれている。  "
      },
      {
        "line": 67,
        "text": "・controversial in some circles  "
      },
      {
        "line": 68,
        "text": "用途: 社会全体ではなく、特定の界隈で物議を醸していることを示す。  "
      },
      {
        "line": 69,
        "text": "例: The advertising campaign is controversial in some circles but popular with younger viewers.  "
      },
      {
        "line": 70,
        "text": "訳: その広告キャンペーンは一部では物議を醸しているが、若い視聴者には人気がある。  "
      },
      {
        "line": 72,
        "text": "・it remains controversial whether ...  "
      },
      {
        "line": 73,
        "text": "用途: 判断が現在も決着していないことを述べる。  "
      },
      {
        "line": 74,
        "text": "例: It remains controversial whether the policy reduced inequality.  "
      },
      {
        "line": 75,
        "text": "訳: その政策が格差を縮小したかどうかは、今も議論が分かれている。  "
      },
      {
        "line": 77,
        "text": "・a controversial remark  "
      },
      {
        "line": 78,
        "text": "用途: 発言が批判や反発を招く内容だったことを表す。  "
      },
      {
        "line": 79,
        "text": "例: The minister's controversial remark drew criticism from both parties.  "
      },
      {
        "line": 80,
        "text": "訳: 大臣の物議を醸す発言は両党から批判を招いた。  "
      },
      {
        "line": 82,
        "text": "・become controversial after ...  "
      },
      {
        "line": 83,
        "text": "用途: 当初は普通だった対象が、後から知られた事実や変化によって論争の的になることを表す。  "
      },
      {
        "line": 84,
        "text": "例: The renovation plan became controversial after residents learned the full cost.  "
      },
      {
        "line": 85,
        "text": "訳: 住民が総費用を知った後、その改修計画は物議を醸すようになった。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 166,
        "text": "【コロケーション】"
      },
      {
        "line": 168,
        "text": "・a controversial temperament  "
      },
      {
        "line": 169,
        "text": "用途: 人が性格的に議論や対立を好むことを、まれな形容詞用法で表す。  "
      },
      {
        "line": 170,
        "text": "例: The columnist has a controversial temperament and treats every meeting as a public debate.  "
      },
      {
        "line": 171,
        "text": "訳: そのコラムニストは論争を好む気質で、どの会議も公開討論のように扱う。  "
      },
      {
        "line": 173,
        "text": "・a controversial manner  "
      },
      {
        "line": 174,
        "text": "用途: 人が対立を招きやすい仕方で話したり振る舞ったりすることを表す。  "
      },
      {
        "line": 175,
        "text": "例: Her controversial manner turned minor technical disagreements into public arguments.  "
      },
      {
        "line": 176,
        "text": "訳: 彼女の対立を生みやすい態度は、ささいな技術上の意見の違いまで公の論争に変えた。  "
      },
      {
        "line": 178,
        "text": "・be controversial by temperament  "
      },
      {
        "line": 179,
        "text": "用途: 物議を醸す個別の行動ではなく、もともとの性向が論争的だと述べるまれな構文。  "
      },
      {
        "line": 180,
        "text": "例: He was controversial by temperament, challenging even minor points in every debate.  "
      },
      {
        "line": 181,
        "text": "訳: 彼は性向として論争的で、どの討論でもささいな点にまで反論した。  "
      },
      {
        "line": 183,
        "text": "・be controversial in debate  "
      },
      {
        "line": 184,
        "text": "用途: 議論の最中に、立場そのものよりも反論を重ねる性向が目立つことを表す。  "
      },
      {
        "line": 185,
        "text": "例: The speaker was controversial in debate because he deliberately attacked each established position.  "
      },
      {
        "line": 186,
        "text": "訳: その話者は確立した立場を一つ一つ意図的に攻撃したため、討論では論争的だった。  "
      }
    ],
    "usage_notes": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 87,
        "text": "【語法・注意】対象を主語にした be controversial は「その対象が論争の的だ」という意味で、必ずしも対象自身が議論を仕掛けるわけではない。人物についても通常は「評価が割れている人物」の意味であり、「論争を好む人」という性向を言いたいときは語義2を確認する。highly は対立の強さ、widely は論争が広い範囲に及ぶことを示す。controversial を「間違った」「受け入れられない」と自動的に訳さず、何が誰の間で争われているかを among/within 句や文脈で補う。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 188,
        "text": "【語法・注意】この語義では controversial が人の性向を直接表すが、現代の「論争の的となる人物」という普通の解釈と形が同じなので、文脈で区別する必要がある。a controversial politician は通常語義1であり、気質を明示する temperament、manner、by temperament などがあって初めて語義2に近づく。意見が割れているだけなら語義1、本人が反論・対立を好むことまで言うなら語義2である。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "line": 89,
        "text": "【類義語】"
      },
      {
        "line": 91,
        "text": "・contentious  "
      },
      {
        "line": 92,
        "text": "定義: 議論や対立を引き起こしやすい、争点になっている。  "
      },
      {
        "line": 93,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 94,
        "text": "違い: contentious は問題・決定が争いを生みやすい性質や、当事者間の対立の強さに焦点があり、controversial より対立的に響くことがある。  "
      },
      {
        "line": 95,
        "text": "例: The contentious issue delayed the negotiations for weeks.  "
      },
      {
        "line": 96,
        "text": "訳: その対立を招く争点のために、交渉は何週間も遅れた。  "
      },
      {
        "line": 98,
        "text": "・disputed  "
      },
      {
        "line": 99,
        "text": "定義: 真偽・権利・解釈などが争われている、意見が一致していない。  "
      },
      {
        "line": 100,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 101,
        "text": "違い: disputed は「正しいか、誰のものかなどが争われている」という未確定性を強調し、controversial のような広い世論上の物議まで必ずしも含まない。  "
      },
      {
        "line": 102,
        "text": "例: The map shows the disputed border in a different color.  "
      },
      {
        "line": 103,
        "text": "訳: その地図は争われている国境を別の色で示している。  "
      },
      {
        "line": 105,
        "text": "・debatable  "
      },
      {
        "line": 106,
        "text": "定義: 議論の余地があり、結論を一つに決めにくい。  "
      },
      {
        "line": 107,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 108,
        "text": "違い: debatable は主張や判断の妥当性を論じられることに焦点があり、controversial より感情的な反発や大きな社会的対立を含まない場合が多い。  "
      },
      {
        "line": 109,
        "text": "例: Whether the change improved efficiency is debatable.  "
      },
      {
        "line": 110,
        "text": "訳: その変更が効率を高めたかどうかは議論の余地がある。  "
      },
      {
        "line": 112,
        "text": "・polarizing  "
      },
      {
        "line": 113,
        "text": "定義: 人々を賛成側と反対側へ大きく分断する。  "
      },
      {
        "line": 114,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 115,
        "text": "違い: polarizing は意見の対立を二極化させる効果を強調する。controversial は意見が割れていても、二つの陣営に明確に分かれるとは限らない。  "
      },
      {
        "line": 116,
        "text": "例: The candidate's polarizing speech dominated the news cycle.  "
      },
      {
        "line": 117,
        "text": "訳: その候補者の社会を二極化させる演説が報道を席巻した。  "
      },
      {
        "line": 119,
        "text": "・provocative  "
      },
      {
        "line": 120,
        "text": "定義: 強い反応や議論を意図的または効果として引き起こす、挑発的な。  "
      },
      {
        "line": 121,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 122,
        "text": "違い: provocative は発言者・作者が反応を誘う性質や意図に焦点がある。controversial は実際に物議が生じている状態を表し、意図を必要としない。  "
      },
      {
        "line": 123,
        "text": "例: The artist is known for provocative questions about public memory.  "
      },
      {
        "line": 124,
        "text": "訳: その芸術家は公共の記憶について挑発的な問いを投げかけることで知られている。  "
      },
      {
        "line": 126,
        "text": "・divisive  "
      },
      {
        "line": 127,
        "text": "定義: 人々や集団の間に深い対立を生じさせる、分断を招く。  "
      },
      {
        "line": 128,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 129,
        "text": "違い: divisive は社会的な分断や関係悪化という結果を強く示す。controversial は分断に至らず、単に議論や批判を招く場合にも使える。  "
      },
      {
        "line": 130,
        "text": "例: The divisive reform split the professional association.  "
      },
      {
        "line": 131,
        "text": "訳: その分断を招く改革は専門職団体を二分した。  "
      },
      {
        "line": 133,
        "text": "・polemical  "
      },
      {
        "line": 134,
        "text": "定義: 論争を仕掛ける、または論争的な主張を展開する。  "
      },
      {
        "line": 135,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 136,
        "text": "違い: polemical は文章・議論・論者の攻撃的な論争スタイルに寄りやすく、controversial より硬く、意図的な論争性を含みやすい。  "
      },
      {
        "line": 137,
        "text": "例: The book adopts a polemical tone toward established theories.  "
      },
      {
        "line": 138,
        "text": "訳: その本は確立した理論に対して論争的な調子を取っている。  "
      },
      {
        "line": 140,
        "text": "【反意語】"
      },
      {
        "line": 142,
        "text": "・uncontroversial  "
      },
      {
        "line": 143,
        "text": "定義: 意見の強い対立や広い反発を招かない、異論の少ない。  "
      },
      {
        "line": 144,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 145,
        "text": "違い: controversial の直接的な反対語で、問題・判断・人物などについて大きな論争が起きていない状態を表す。  "
      },
      {
        "line": 146,
        "text": "例: The committee reached an uncontroversial agreement on the timetable.  "
      },
      {
        "line": 147,
        "text": "訳: 委員会は日程について異論の少ない合意に達した。  "
      },
      {
        "line": 149,
        "text": "・noncontroversial  "
      },
      {
        "line": 150,
        "text": "定義: 論争的でない、特に意見の対立を起こさない。  "
      },
      {
        "line": 151,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 152,
        "text": "違い: noncontroversial も直接的な反対語だが、uncontroversial より説明的・形式的に見えることがある。  "
      },
      {
        "line": 153,
        "text": "例: The report limits itself to noncontroversial background facts.  "
      },
      {
        "line": 154,
        "text": "訳: その報告書は論争のない背景事実に内容を限定している。  "
      },
      {
        "line": 156,
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "line": 190,
        "text": "【類義語】"
      },
      {
        "line": 192,
        "text": "・disputatious  "
      },
      {
        "line": 193,
        "text": "定義: 議論や口論を好む、論争好きな。  "
      },
      {
        "line": 194,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 195,
        "text": "違い: disputatious は人の性向そのものを表す明確な語で、controversial のまれな語義より自然に「口論好き」の意味を示す。  "
      },
      {
        "line": 196,
        "text": "例: His disputatious nature made routine committee work exhausting.  "
      },
      {
        "line": 197,
        "text": "訳: 彼の論争好きな性質のため、通常の委員会業務は疲れるものになった。  "
      },
      {
        "line": 199,
        "text": "・argumentative  "
      },
      {
        "line": 200,
        "text": "定義: すぐに反論する、議論好きな、口論を招く。  "
      },
      {
        "line": 201,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 202,
        "text": "違い: argumentative は日常的で、人が何にでも反論する傾向を表す。controversial より口論・反論の行動が前面に出る。  "
      },
      {
        "line": 203,
        "text": "例: The child became argumentative whenever the rules were explained.  "
      },
      {
        "line": 204,
        "text": "訳: その子は規則を説明されるといつも反論するようになった。  "
      },
      {
        "line": 206,
        "text": "・polemical  "
      },
      {
        "line": 207,
        "text": "定義: 論争を仕掛ける、攻撃的に論争する。  "
      },
      {
        "line": 208,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 209,
        "text": "違い: polemical は論者・文章・議論の意図的で攻撃的な論争性に焦点があり、controversial より文語的である。  "
      },
      {
        "line": 210,
        "text": "例: The polemical writer challenged every compromise proposed by the panel.  "
      },
      {
        "line": 211,
        "text": "訳: その論争的な筆者は、委員会が提案した妥協案すべてに異議を唱えた。  "
      },
      {
        "line": 213,
        "text": "・contentious  "
      },
      {
        "line": 214,
        "text": "定義: 対立的で、争いを引き起こしやすい。  "
      },
      {
        "line": 215,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 216,
        "text": "違い: contentious は人の態度にも使えるが、敵対的・喧嘩腰の含みが出やすい。controversial の語義2は、必ずしも敵意や攻撃性まで含まない。  "
      },
      {
        "line": 217,
        "text": "例: The manager's contentious style made open discussion difficult.  "
      },
      {
        "line": 218,
        "text": "訳: その管理職の対立的なスタイルは、率直な話し合いを難しくした。  "
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
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "ca6259eecf3e5a3819c71287f112c3d88e0517b377769234e3fcd32b4944e390",
    "source_first_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
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
        "locator": "https://www.oxfordlearnersdictionaries.com/definition/english/controversial",
        "source_type": "learner_dictionary",
        "independence_group": "oxford_university_press",
        "facts": [
          {
            "id": "F001",
            "form": "controversial",
            "kind": "lexical_sense",
            "statement": "Controversial describes something that causes a lot of angry public discussion and disagreement.",
            "source_detail": "Oxford gives the main adjective sense for topics, plans, and people that provoke public disagreement."
          },
          {
            "id": "F002",
            "form": "controversial",
            "kind": "grammar_frame",
            "statement": "Controversial is used before issue, plan, figure, and similar nouns and can be modified by highly.",
            "source_detail": "Oxford examples include a highly controversial topic, a controversial plan, and controversial figures."
          },
          {
            "id": "F003",
            "form": "controversial",
            "kind": "lexical_sense",
            "statement": "A controversial person or figure is one whose public reputation or views provoke disagreement.",
            "source_detail": "Oxford includes controversial figures among its examples for the adjective."
          },
          {
            "id": "F004",
            "form": "controversial",
            "kind": "register_frequency",
            "statement": "Controversial is a common learner-level adjective, listed at Oxford 5000 level B2.",
            "source_detail": "Oxford labels the headword B2 in its learner vocabulary information."
          },
          {
            "id": "F005",
            "form": "controversial",
            "kind": "pronunciation",
            "statement": "Oxford gives British /ˌkɒntrəˈvɜːʃl/ and American /ˌkɑːntrəˈvɜːrʃl/ pronunciations.",
            "source_detail": "The Oxford entry displays separate British and American pronunciation transcriptions."
          },
          {
            "id": "F006",
            "form": "controversial",
            "kind": "etymology",
            "statement": "Controversial comes from late Latin controversialis and is related to controversia and controversus.",
            "source_detail": "Oxford's word-origin note traces the adjective to late Latin forms associated with controversy."
          }
        ]
      },
      {
        "id": "S002",
        "locator": "https://www.merriam-webster.com/dictionary/controversial",
        "source_type": "general_dictionary",
        "independence_group": "merriam_webster",
        "facts": [
          {
            "id": "F007",
            "form": "controversial",
            "kind": "lexical_sense",
            "statement": "Controversial means relating to or arousing controversy.",
            "source_detail": "Merriam-Webster gives of, relating to, or arousing controversy as its first adjective definition."
          },
          {
            "id": "F008",
            "form": "controversial",
            "kind": "lexical_sense",
            "statement": "Controversial can also mean given to controversy or disputatious when describing a person or temperament.",
            "source_detail": "Merriam-Webster lists a second adjective sense meaning given to controversy and gives a controversial temperament example."
          },
          {
            "id": "F009",
            "form": "controversial",
            "kind": "grammar_frame",
            "statement": "Controversial commonly modifies policy, film, and similar nouns in attributive adjective phrases.",
            "source_detail": "Merriam-Webster illustrates the adjective with a controversial policy and a controversial film."
          },
          {
            "id": "F010",
            "form": "controversial",
            "kind": "pronunciation",
            "statement": "American pronunciation includes a main /ˌkän-trə-ˈvər-shəl/ form and a variant with a more syllabic final sequence.",
            "source_detail": "Merriam-Webster displays the US pronunciation and the -ˈvər-sē-əl variant."
          },
          {
            "id": "F011",
            "form": "controversial",
            "kind": "etymology",
            "statement": "Merriam-Webster records controversial as first known from 1583.",
            "source_detail": "The dictionary's first-known-use field gives 1583 for the adjective."
          },
          {
            "id": "F012",
            "form": "controversially",
            "kind": "derived_form",
            "statement": "Controversially is the related adverb, and controversialist and controversialism are related noun forms; controvert is a related verb.",
            "source_detail": "Merriam-Webster's related-word information lists the adverb, noun forms, and the related verb controvert."
          }
        ]
      },
      {
        "id": "S003",
        "locator": "https://www.collinsdictionary.com/dictionary/english/controversial",
        "source_type": "general_dictionary",
        "independence_group": "harpercollins",
        "facts": [
          {
            "id": "F013",
            "form": "controversial",
            "kind": "lexical_sense",
            "statement": "Controversial describes a person or thing that is the subject of intense public argument, disagreement, or disapproval, and it can rarely mean disputatious.",
            "source_detail": "Collins gives the public-argument sense and labels the disputatious personality sense rare in its American entry."
          },
          {
            "id": "F014",
            "form": "controversial",
            "kind": "grammar_frame",
            "statement": "Controversial forms common phrases with deal, decision, figure, film, issue, plan, proposal, remark, ruling, statement, theory, and view.",
            "source_detail": "Collins lists these noun collocations and degree modifiers such as highly, widely, and potentially."
          },
          {
            "id": "F015",
            "form": "controversial",
            "kind": "register_frequency",
            "statement": "Controversial is a B2 adjective, while its disputatious-personality use is rare.",
            "source_detail": "Collins labels the general headword B2 and marks the second American sense rare."
          },
          {
            "id": "F016",
            "form": "controversial",
            "kind": "pronunciation_etymology",
            "statement": "Collins gives American variants with both /-vɜrʃəl/ and /-vɜrsiəl/ and dates the origin to 1575–85.",
            "source_detail": "The Collins entry displays the pronunciation variants and the 1575–85 origin range."
          }
        ]
      },
      {
        "id": "S004",
        "locator": "https://www.etymonline.com/word/controversial",
        "source_type": "etymology_dictionary",
        "independence_group": "etymonline",
        "facts": [
          {
            "id": "F017",
            "form": "controversial",
            "kind": "etymology",
            "statement": "Controversial is recorded in the 1580s in the sense of debatable or disputed, from late Latin controversialis.",
            "source_detail": "Etymonline dates the early adjective use to the 1580s and gives the late Latin source."
          },
          {
            "id": "F018",
            "form": "controversial",
            "kind": "etymology",
            "statement": "The Latin form is related to controversus, literally turned against, from contra and versus, the past participle of vertere.",
            "source_detail": "Etymonline explains the Latin components and the underlying sense of being turned against."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "U001",
        "source_fact_ids": [
          "F001",
          "F002",
          "F003",
          "F007",
          "F009",
          "F013",
          "F014"
        ],
        "canonical_statement": "Controversial commonly describes an issue, decision, claim, work, remark, or person that arouses strong public or group disagreement.",
        "disposition": "included",
        "rationale": "This is the high-frequency main adjective sense and is the first numbered sense."
      },
      {
        "id": "U002",
        "source_fact_ids": [
          "F008",
          "F013",
          "F015"
        ],
        "canonical_statement": "Controversial can rarely describe a person or temperament inclined to controversy or disputation.",
        "disposition": "included",
        "rationale": "The rare personality sense is retained because independent dictionaries record it and it prevents a person-use ambiguity."
      },
      {
        "id": "U003",
        "source_fact_ids": [
          "F005",
          "F010",
          "F016"
        ],
        "canonical_statement": "Controversial has a four-syllable pronunciation with main stress on the third syllable and a US variant with a more syllabic ending.",
        "disposition": "included",
        "rationale": "The pronunciation section records the mainstream British/American forms and qualifies the US variant."
      },
      {
        "id": "U004",
        "source_fact_ids": [
          "F006",
          "F011",
          "F016",
          "F017",
          "F018"
        ],
        "canonical_statement": "Controversial is a late-sixteenth-century adjective from late Latin controversialis, related to controversia and controversus.",
        "disposition": "included",
        "rationale": "The etymology section states the shared late-sixteenth-century range and avoids treating conflicting first-use dates as exact."
      },
      {
        "id": "U005",
        "source_fact_ids": [
          "F012"
        ],
        "canonical_statement": "Controversially, controversialist, controversialism, and controvert are related forms, with different parts of speech and frequency.",
        "disposition": "integrated",
        "rationale": "The formation section records useful related forms without presenting the adverb or nouns as additional senses of the headword."
      },
      {
        "id": "U006",
        "source_fact_ids": [
          "F004",
          "F015"
        ],
        "canonical_statement": "The public-disagreement adjective is a common B2-level word, while the personality sense is rare.",
        "disposition": "integrated",
        "rationale": "The two frequency/register labels are attached to their respective numbered senses."
      }
    ],
    "claim_units": [
      {
        "id": "C001",
        "union_ids": [
          "U001"
        ],
        "subject_form": "controversial",
        "claim_type": "definition",
        "statement": "The common sense describes topics, decisions, claims, works, remarks, and people that provoke strong disagreement or criticism.",
        "article_target_ids": [
          "sense_boundary:001",
          "definition:001",
          "frequency:001",
          "register:001",
          "grammar_pattern:001",
          "grammar_pattern:002",
          "grammar_pattern:003",
          "grammar_pattern:004",
          "grammar_pattern:005",
          "grammar_pattern:006",
          "grammar_pattern:007",
          "grammar_pattern:008",
          "grammar_pattern:009",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007",
          "collocation:008",
          "collocation:009",
          "usage_note:001",
          "synonym:001",
          "synonym:002",
          "synonym:003",
          "synonym:004",
          "synonym:005",
          "synonym:006",
          "synonym:007",
          "antonym:001",
          "antonym:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F001",
            "support_summary": "Oxford directly defines the public discussion and disagreement sense."
          },
          {
            "source_fact_id": "F002",
            "support_summary": "Oxford supplies the main noun combinations and degree modifier."
          },
          {
            "source_fact_id": "F003",
            "support_summary": "Oxford attests the use for controversial figures."
          },
          {
            "source_fact_id": "F007",
            "support_summary": "Merriam-Webster defines the adjective through arousing controversy."
          },
          {
            "source_fact_id": "F009",
            "support_summary": "Merriam-Webster illustrates the attributive policy and film frames."
          },
          {
            "source_fact_id": "F013",
            "support_summary": "Collins defines intense public argument and disapproval."
          },
          {
            "source_fact_id": "F014",
            "support_summary": "Collins records the article's common noun collocations."
          }
        ]
      },
      {
        "id": "C002",
        "union_ids": [
          "U002"
        ],
        "subject_form": "controversial",
        "claim_type": "definition",
        "statement": "The rare personality sense describes a person inclined to controversy or disputation rather than merely a person who is being publicly debated.",
        "article_target_ids": [
          "sense_boundary:002",
          "definition:002",
          "frequency:002",
          "register:002",
          "grammar_pattern:010",
          "grammar_pattern:011",
          "grammar_pattern:012",
          "grammar_pattern:013",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013",
          "usage_note:002",
          "synonym:008",
          "synonym:009",
          "synonym:010",
          "synonym:011"
        ],
        "source_supports": [
          {
            "source_fact_id": "F008",
            "support_summary": "Merriam-Webster explicitly gives the disputatious personality sense."
          },
          {
            "source_fact_id": "F013",
            "support_summary": "Collins records the rare disputatious use in its American entry."
          },
          {
            "source_fact_id": "F015",
            "support_summary": "Collins marks the personality use rare and contrasts it with the common sense."
          }
        ]
      },
      {
        "id": "C003",
        "union_ids": [
          "U003"
        ],
        "subject_form": "controversial",
        "claim_type": "pronunciation",
        "statement": "The word normally has four syllables and main stress on the third, with a US variant that may realize the ending as an extra syllable.",
        "article_target_ids": [
          "pronunciation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F005",
            "support_summary": "Oxford supplies the main British and American transcriptions."
          },
          {
            "source_fact_id": "F010",
            "support_summary": "Merriam-Webster records the American ending variant."
          },
          {
            "source_fact_id": "F016",
            "support_summary": "Collins independently displays the American pronunciation variants."
          }
        ]
      },
      {
        "id": "C004",
        "union_ids": [
          "U004"
        ],
        "subject_form": "controversial",
        "claim_type": "etymology",
        "statement": "The adjective belongs to a late-sixteenth-century Latin-derived controversy word family involving the idea of being turned against.",
        "article_target_ids": [
          "etymology:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F006",
            "support_summary": "Oxford traces the adjective to late Latin controversialis."
          },
          {
            "source_fact_id": "F011",
            "support_summary": "Merriam-Webster's 1583 first-use date supports the late-sixteenth-century range."
          },
          {
            "source_fact_id": "F016",
            "support_summary": "Collins gives a 1575–85 origin range rather than a modern date."
          },
          {
            "source_fact_id": "F017",
            "support_summary": "Etymonline gives the 1580s debatable or disputed use."
          },
          {
            "source_fact_id": "F018",
            "support_summary": "Etymonline explains controversus, contra, versus, and vertere."
          }
        ]
      },
      {
        "id": "C005",
        "union_ids": [
          "U005"
        ],
        "subject_form": "controversially",
        "claim_type": "word_formation",
        "statement": "The article distinguishes the related adverb, noun forms, and verb rather than treating them as inflections of the adjective.",
        "article_target_ids": [
          "word_formation:001",
          "word_formation:002",
          "word_formation:003",
          "word_formation:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F012",
            "support_summary": "Merriam-Webster lists the related adverb, nouns, and verb forms."
          }
        ]
      },
      {
        "id": "C006",
        "union_ids": [
          "U006"
        ],
        "subject_form": "controversial",
        "claim_type": "register_frequency",
        "statement": "The public-disagreement use is standard and common, whereas the disputatious-personality use is rare and dictionary-oriented.",
        "article_target_ids": [
          "register:001",
          "frequency:001",
          "register:002",
          "frequency:002"
        ],
        "source_supports": [
          {
            "source_fact_id": "F004",
            "support_summary": "Oxford labels the headword B2 in its learner vocabulary."
          },
          {
            "source_fact_id": "F015",
            "support_summary": "Collins labels the personality use rare and the general word B2."
          }
        ]
      }
    ],
    "article_targets": [
      {
        "id": "antonym:001",
        "kind": "antonym",
        "location": "lines:131-136",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "87dedb582ccc998aeb8fea5e1248a7836b34e946df644efa4ad1b6aac7d12722",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・uncontroversial\n定義: 意見の強い対立や広い反発を招かない、異論の少ない。\n頻度: 〈6/10〉\n違い: controversial の直接的な反対語で、問題・判断・人物などについて大きな論争が起きていない状態を表す。\n例: The committee reached an uncontroversial agreement on the timetable.\n訳: 委員会は日程について異論の少ない合意に達した。"
      },
      {
        "id": "antonym:002",
        "kind": "antonym",
        "location": "lines:138-143",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "61614c1bd67cf88cbefb9bb099d8d71bafbe5a36af0bc81279d8f1a0a4d55e34",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・noncontroversial\n定義: 論争的でない、特に意見の対立を起こさない。\n頻度: 〈5/10〉\n違い: noncontroversial も直接的な反対語だが、uncontroversial より説明的・形式的に見えることがある。\n例: The report limits itself to noncontroversial background facts.\n訳: その報告書は論争のない背景事実に内容を限定している。"
      },
      {
        "id": "collocation:001",
        "kind": "collocation",
        "location": "lines:31-34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "a1cf7e37111868c2b2ceb8062836245b42728da67c9604c1406a652c351ace41",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial issue\n用途: 社会的に賛否が対立している問題を指す。\n例: The use of facial-recognition technology remains a controversial issue.\n訳: 顔認証技術の利用は依然として論争を呼ぶ問題だ。"
      },
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:36-39",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "5c29a8ee132fd1f2fa43bd53716d627a2f25e2b2c77e09a4dce491c4e69ce15c",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial decision\n用途: 決定の妥当性や影響をめぐって強い反対・批判が出ていることを表す。\n例: The committee made a controversial decision to cancel the exhibition.\n訳: 委員会は展示会を中止するという物議を醸す決定を下した。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:41-44",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "3c8e43292594fc4b0129a235261fa862aeee5c2d5468e1bb76415ce4e5485ced",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・a controversial figure\n用途: 功績と批判の両方があり、評価が大きく割れている人物を指す。\n例: The historian remains a controversial figure in the region.\n訳: その歴史家はその地域で今も評価が大きく分かれる人物だ。"
      },
      {
        "id": "collocation:004",
        "kind": "collocation",
        "location": "lines:46-49",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "4238292008a5a709b2008927a9ffe05020a77f0eff07e6b7cf09fdb268e173ca",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・a highly controversial proposal\n用途: 提案に対して非常に強い賛否や反発が起きていることを強調する。\n例: The city council postponed a highly controversial proposal.\n訳: 市議会は非常に物議を醸している提案を延期した。"
      },
      {
        "id": "collocation:005",
        "kind": "collocation",
        "location": "lines:51-54",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "9973ab472a7126616140cd7dd1b7c9f234dddce2da842225751b9b101a6c86d6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・controversial among 〈group〉\n用途: どの集団の中で意見が割れているかを限定する。\n例: The interpretation is controversial among constitutional scholars.\n訳: その解釈は憲法学者の間で議論が分かれている。"
      },
      {
        "id": "collocation:006",
        "kind": "collocation",
        "location": "lines:56-59",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "69b91f7b093ed158b555cab7c64af17a6135f83153e572b31f7a804175a6b820",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controversial in some circles\n用途: 社会全体ではなく、特定の界隈で物議を醸していることを示す。\n例: The advertising campaign is controversial in some circles but popular with younger viewers.\n訳: その広告キャンペーンは一部では物議を醸しているが、若い視聴者には人気がある。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:61-64",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "0e9c13970cd75209bfa2920cc1ddc24396f9675ad135af3c1f002d6addec9e3c",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・it remains controversial whether ...\n用途: 判断が現在も決着していないことを述べる。\n例: It remains controversial whether the policy reduced inequality.\n訳: その政策が格差を縮小したかどうかは、今も議論が分かれている。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:66-69",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "610fab7f6f88573761280e28fd6a7ac7b3f1ba28c245dd4153ac9144e10a980a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial remark\n用途: 発言が批判や反発を招く内容だったことを表す。\n例: The minister's controversial remark drew criticism from both parties.\n訳: 大臣の物議を醸す発言は両党から批判を招いた。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:71-74",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "7014ac2f2844b254010faeb64f5e68a2cecdf848f6b9e8c9f849aac6b2a9889f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・become controversial after ...\n用途: 当初は普通だった対象が、後から知られた事実や変化によって論争の的になることを表す。\n例: The renovation plan became controversial after residents learned the full cost.\n訳: 住民が総費用を知った後、その改修計画は物議を醸すようになった。"
      },
      {
        "id": "collocation:010",
        "kind": "collocation",
        "location": "lines:157-160",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "77ed9fdcc083671a735320ce03da9f962ebf436864ffad3e0a2a0c3bf89819fe",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial temperament\n用途: 人が性格的に議論や対立を好むことを、まれな形容詞用法で表す。\n例: The columnist has a controversial temperament and treats every meeting as a public debate.\n訳: そのコラムニストは論争を好む気質で、どの会議も公開討論のように扱う。"
      },
      {
        "id": "collocation:011",
        "kind": "collocation",
        "location": "lines:162-165",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "2c7a42caa5eae2b816a17a8c7ea4ca01a68f2f8f6eca8419b42edf51228b2886",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial manner\n用途: 人が対立を招きやすい仕方で話したり振る舞ったりすることを表す。\n例: Her controversial manner turned minor technical disagreements into public arguments.\n訳: 彼女の対立を生みやすい態度は、ささいな技術上の意見の違いまで公の論争に変えた。"
      },
      {
        "id": "collocation:012",
        "kind": "collocation",
        "location": "lines:167-170",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "2e168246a3d9798d04b358a4294df8642e81dea4a9b5589cc087bdb46d674220",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・be controversial by temperament\n用途: 物議を醸す個別の行動ではなく、もともとの性向が論争的だと述べるまれな構文。\n例: He was controversial by temperament, challenging even minor points in every debate.\n訳: 彼は性向として論争的で、どの討論でもささいな点にまで反論した。"
      },
      {
        "id": "collocation:013",
        "kind": "collocation",
        "location": "lines:172-175",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "507e3cda12e4b53134e308202185049db0203646a40d4c87792b0f2f7010989e",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・be controversial in debate\n用途: 議論の最中に、立場そのものよりも反論を重ねる性向が目立つことを表す。\n例: The speaker was controversial in debate because he deliberately attacked each established position.\n訳: その話者は確立した立場を一つ一つ意図的に攻撃したため、討論では論争的だった。"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:21",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "fdc630c604154dac805bfe0439bb985fc93a221cde5a898946d3042d09372602",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "政策・決定・主張・作品・発言・人物などが、社会全体または特定の集団の中で、強い意見の対立、批判、反対を引き起こしていることを表す。事実として真偽が決まっていないことを必ずしも含まず、悪い、違法、意図的に挑発的だという意味でもない。"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:147",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "770698baef047f7a431f943f1f5aa8a0d1ac9c177ec62befb1c3cee1aa6987f6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "人が性格や態度の傾向として、議論を好んだり、既存の立場に反論して対立を生みやすかったりすることを表す。辞書に記載される低頻度の語義で、現代の controversial person は通常、語義1の「論争の的となっている人物」と解釈される。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text_sha256": "9b40b877bd6485ba93fc1fc28627f013c8e6774cfab9314c3ca3fe3550fd87cc",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "16世紀後半に使われ始めた語で、後期ラテン語 controversialis「論争に関する」から来た。controversia「論争」は controversus「反対方向に向けられた、争われた」に関係し、contra-/contro-「反対に」と versus「向けられた、転じた」（vertere「向きを変える」の過去分詞）に分けて考えられる。初出年代は資料により1580年代、1583年、1575–85年など差があるため、特定の年として暗記しない。"
      },
      {
        "id": "frequency:001",
        "kind": "frequency",
        "location": "line:23",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "7a626327bdf4a8ce1246cb04f8b9692c985873b0ba478e5ff432ffa1425edf1f",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈9/10〉"
      },
      {
        "id": "frequency:002",
        "kind": "frequency",
        "location": "line:149",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "c9f89b3d40a42341908558a5512ad7d34bbc108cc33b512e22b76f6557469962",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈2/10〉"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "8a51d40f92625fcfafe41905bb27b9d1de5f7b70fb0495b3c7b6f31acc2cc17d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be/become/remain/prove controversial＝論争を呼ぶ・論争の的であり続ける・結果的に物議を醸す"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "276c6f4f505b6102cfa84e7d0cb5ed731f88ecebea08cae80a8c47508bef6593",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a controversial 〈issue・decision・policy・claim・statement・figure・book・film〉＝論争を呼ぶ〈問題・決定・政策・主張・発言・人物・本・映画〉"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "da5072e01c9e8e2435d969a406e4d108050e1c37aaa4ce1ba0a53d3b8aca48d9",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "highly/widely controversial＝非常に"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "e2efca3f936245704e0507fb913ac5b7e6461f1985b26aa93ade4cb1827c2721",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "広く物議を醸す"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "edbf232ada067dccfe65e56ee3cefd9d40f621f959657ab4a37fc26feaba37b4",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "controversial among/within 〈group〉＝〈集団〉の間で論争を呼ぶ"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "492a29aa7ef25560526c39136abdf43756f123f3d3a8f07c2d1cd091dbb75c4e",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "controversial in some circles＝一部の界隈では物議を醸す"
      },
      {
        "id": "grammar_pattern:007",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "5c4a65521e254079b19ba3196062d544693be779ebc6e55d6a9b87437b07ffcb",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "it remains controversial whether ...＝…かどうかは依然として議論が分かれる"
      },
      {
        "id": "grammar_pattern:008",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "d371617ffde65f279d7a9ac2ae3fe0f3d6408632728beb391ed69689fd6bc874",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be controversial enough to do＝～するほど物議を醸す"
      },
      {
        "id": "grammar_pattern:009",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "75abef7f6f54394460211bd59fe154d0875b89148b652bc7e938027968fca17e",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "too controversial to do＝物議を醸しすぎて～できない。"
      },
      {
        "id": "grammar_pattern:010",
        "kind": "grammar_pattern",
        "location": "line:153",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "a0e370216502c56615885a7143b5e30f6346ce59b6af135f64050fc27a1b2028",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a controversial temperament＝論争を好む気質"
      },
      {
        "id": "grammar_pattern:011",
        "kind": "grammar_pattern",
        "location": "line:153",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "261e65c9c3ca09635197820a48ecbe1373901bb2e76e3b45576875ee9201e7b9",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a controversial manner＝対立を生みやすい態度"
      },
      {
        "id": "grammar_pattern:012",
        "kind": "grammar_pattern",
        "location": "line:153",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "a841a89d53235b8e250142f42a691b54d2bc5b4a5830473bd317828b4dae532b",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be controversial by temperament＝性向として論争的である"
      },
      {
        "id": "grammar_pattern:013",
        "kind": "grammar_pattern",
        "location": "line:153",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "a0e4ad926223cf663c042c5563c8ad786f154b0dc148414ad93be779f2ebd5e3",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be controversial in debate＝議論で意図的に反論を重ねる。"
      },
      {
        "id": "pronunciation:001",
        "kind": "pronunciation",
        "location": "line:4",
        "section": "＃発音記号",
        "sense": "",
        "text_sha256": "8a744f0a9a73caae3c7cba7f57b44ebf31177e264541b358aeacee80fe786709",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "米: /ˌkɑːntrəˈvɝːʃəl/｜英: /ˌkɒntrəˈvɜːʃəl/。米英とも4音節で、第3音節の /vɝː/・/vɜː/ に主強勢がある。第1音節の /ˌkɑːn/・/ˌkɒn/ には副次強勢を示す。米語では /ˌkɑːntrəˈvɝːsiəl/ に近い5音節寄りの発音も聞かれるが、通常の学習上は /ˈvɝːʃəl/・/ˈvɜːʃəl/ の部分を基準にする。"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:25",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "eb99c9474ded18a839c17444991b8e0dea996743edf0f996576ea67763c96fdf",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "標準語で、会話・ニュース・政治・文化・学術・ビジネスの文章まで広く使う。controversial は「多くの人が反対している」と同じではなく、賛成・反対の議論が強く起きている状態を指す。"
      },
      {
        "id": "register:002",
        "kind": "register",
        "location": "line:151",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "ce266854a5a47558255071f27ac8b508e804061e9f0bc1bf99360f1d888d49b6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "まれで、辞書的・形式的・文学的な説明に現れやすい。現代の一般的な文章で人の性向を表すなら argumentative、disputatious、polemical の方が意味を明確にしやすい。"
      },
      {
        "id": "sense_boundary:001",
        "kind": "sense_boundary",
        "location": "line:19",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "501ce539724a3eee9ac6f4d3f97daf880eda292c4dd3e7459f438790f321c0cf",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "id": "sense_boundary:002",
        "kind": "sense_boundary",
        "location": "line:145",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "a2ad2cdcca50d3ca0d81c7c0981ed66a04e6458b4fee8b299252e2ba13d50e33",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:80-85",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "87442f983bf74a4c43c64588d7d05f3a145e60ddca2bf9e5ab119efddc4baa7f",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・contentious\n定義: 議論や対立を引き起こしやすい、争点になっている。\n頻度: 〈8/10〉\n違い: contentious は問題・決定が争いを生みやすい性質や、当事者間の対立の強さに焦点があり、controversial より対立的に響くことがある。\n例: The contentious issue delayed the negotiations for weeks.\n訳: その対立を招く争点のために、交渉は何週間も遅れた。"
      },
      {
        "id": "synonym:002",
        "kind": "synonym",
        "location": "lines:87-92",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "132313664d478c67ad7e01dc628f32735551e1c147c062495f394d8bd89c4d38",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・disputed\n定義: 真偽・権利・解釈などが争われている、意見が一致していない。\n頻度: 〈8/10〉\n違い: disputed は「正しいか、誰のものかなどが争われている」という未確定性を強調し、controversial のような広い世論上の物議まで必ずしも含まない。\n例: The map shows the disputed border in a different color.\n訳: その地図は争われている国境を別の色で示している。"
      },
      {
        "id": "synonym:003",
        "kind": "synonym",
        "location": "lines:94-99",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "6b9984c16d8519f7340048bf653a65230f1d408d8433289918c5fb9d1ab1394a",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・debatable\n定義: 議論の余地があり、結論を一つに決めにくい。\n頻度: 〈7/10〉\n違い: debatable は主張や判断の妥当性を論じられることに焦点があり、controversial より感情的な反発や大きな社会的対立を含まない場合が多い。\n例: Whether the change improved efficiency is debatable.\n訳: その変更が効率を高めたかどうかは議論の余地がある。"
      },
      {
        "id": "synonym:004",
        "kind": "synonym",
        "location": "lines:101-106",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "174810d420e5fb3e877bed9e9139904a03c59021233ea7b517ccf9b945df7117",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・polarizing\n定義: 人々を賛成側と反対側へ大きく分断する。\n頻度: 〈7/10〉\n違い: polarizing は意見の対立を二極化させる効果を強調する。controversial は意見が割れていても、二つの陣営に明確に分かれるとは限らない。\n例: The candidate's polarizing speech dominated the news cycle.\n訳: その候補者の社会を二極化させる演説が報道を席巻した。"
      },
      {
        "id": "synonym:005",
        "kind": "synonym",
        "location": "lines:108-113",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "56a8a933ec528fe3d64eb649a8ab62677c79d3e8cace1c7b821f3786d5f7e015",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・provocative\n定義: 強い反応や議論を意図的または効果として引き起こす、挑発的な。\n頻度: 〈8/10〉\n違い: provocative は発言者・作者が反応を誘う性質や意図に焦点がある。controversial は実際に物議が生じている状態を表し、意図を必要としない。\n例: The artist is known for provocative questions about public memory.\n訳: その芸術家は公共の記憶について挑発的な問いを投げかけることで知られている。"
      },
      {
        "id": "synonym:006",
        "kind": "synonym",
        "location": "lines:115-120",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "65c05ce6b632c80f8e62c5eaa90fad64a1da01cb8fb02fad3c2f10fd57a910c1",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・divisive\n定義: 人々や集団の間に深い対立を生じさせる、分断を招く。\n頻度: 〈7/10〉\n違い: divisive は社会的な分断や関係悪化という結果を強く示す。controversial は分断に至らず、単に議論や批判を招く場合にも使える。\n例: The divisive reform split the professional association.\n訳: その分断を招く改革は専門職団体を二分した。"
      },
      {
        "id": "synonym:007",
        "kind": "synonym",
        "location": "lines:122-127",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "9b0fa9ed047159a53753a1f4900cf4bf290a17e2018b217fd05844b787195ab8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・polemical\n定義: 論争を仕掛ける、または論争的な主張を展開する。\n頻度: 〈4/10〉\n違い: polemical は文章・議論・論者の攻撃的な論争スタイルに寄りやすく、controversial より硬く、意図的な論争性を含みやすい。\n例: The book adopts a polemical tone toward established theories.\n訳: その本は確立した理論に対して論争的な調子を取っている。"
      },
      {
        "id": "synonym:008",
        "kind": "synonym",
        "location": "lines:181-186",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "b5e82e464da36ae0828c0fff036552e8dc5d321c5b4508544d63787a6913b8c4",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・disputatious\n定義: 議論や口論を好む、論争好きな。\n頻度: 〈4/10〉\n違い: disputatious は人の性向そのものを表す明確な語で、controversial のまれな語義より自然に「口論好き」の意味を示す。\n例: His disputatious nature made routine committee work exhausting.\n訳: 彼の論争好きな性質のため、通常の委員会業務は疲れるものになった。"
      },
      {
        "id": "synonym:009",
        "kind": "synonym",
        "location": "lines:188-193",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "966bb2cde06675ce8015e7894df5957201267acdd9ec9e2eed5ef04a4b109302",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・argumentative\n定義: すぐに反論する、議論好きな、口論を招く。\n頻度: 〈7/10〉\n違い: argumentative は日常的で、人が何にでも反論する傾向を表す。controversial より口論・反論の行動が前面に出る。\n例: The child became argumentative whenever the rules were explained.\n訳: その子は規則を説明されるといつも反論するようになった。"
      },
      {
        "id": "synonym:010",
        "kind": "synonym",
        "location": "lines:195-200",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "b04a2150c53378acd552d2cd52980e92a33508399c1e55ccd60f90235c4cdd49",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・polemical\n定義: 論争を仕掛ける、攻撃的に論争する。\n頻度: 〈4/10〉\n違い: polemical は論者・文章・議論の意図的で攻撃的な論争性に焦点があり、controversial より文語的である。\n例: The polemical writer challenged every compromise proposed by the panel.\n訳: その論争的な筆者は、委員会が提案した妥協案すべてに異議を唱えた。"
      },
      {
        "id": "synonym:011",
        "kind": "synonym",
        "location": "lines:202-207",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "33e73aee9b4ecfebd7fe4e08c1ed635f02a6a9f6662c92d036390bf152b8cd24",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・contentious\n定義: 対立的で、争いを引き起こしやすい。\n頻度: 〈8/10〉\n違い: contentious は人の態度にも使えるが、敵対的・喧嘩腰の含みが出やすい。controversial の語義2は、必ずしも敵意や攻撃性まで含まない。\n例: The manager's contentious style made open discussion difficult.\n訳: その管理職の対立的なスタイルは、率直な話し合いを難しくした。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:76",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "4dd4d08d23cf463a59deea5d40e9fc26ebf739903676028c62a93463def83ff5",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "対象を主語にした be controversial は「その対象が論争の的だ」という意味で、必ずしも対象自身が議論を仕掛けるわけではない。人物についても通常は「評価が割れている人物」の意味であり、「論争を好む人」という性向を言いたいときは語義2を確認する。highly は対立の強さ、widely は論争が広い範囲に及ぶことを示す。controversial を「間違った」「受け入れられない」と自動的に訳さず、何が誰の間で争われているかを among/within 句や文脈で補う。"
      },
      {
        "id": "usage_note:002",
        "kind": "usage_note",
        "location": "line:177",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "4ead97ad6308fc47606922e75e40762463eb9dcb76d5394fcba8dae379f8aa48",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "この語義では controversial が人の性向を直接表すが、現代の「論争の的となる人物」という普通の解釈と形が同じなので、文脈で区別する必要がある。a controversial politician は通常語義1であり、気質を明示する temperament、manner、by temperament などがあって初めて語義2に近づく。意見が割れているだけなら語義1、本人が反論・対立を好むことまで言うなら語義2である。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "a40a3226b8413844f17f848c9bd0bf0dac4f1d7f2e779cf8165a9f0d62b15dbd",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controversy：名詞。「論争、論争点、物議」。controversial と同じ語族の中心語で、public controversy のように使う。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "bc38d22c77884d6d33d09b70f32a205c6cac646f541ad1b99df31258ae4490b4",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controversially：副詞。「物議を醸す形で、論争を呼ぶことに」。文全体や発言・判断の仕方を修飾する。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "f28c35178557e13d6e059bfd37a1b34b47e6f699ca131beaef5a7ff9800f2c8a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controversialist：名詞。「論争家、論争に加わる人」。人の性向または論争上の立場を指す硬めの語。"
      },
      {
        "id": "word_formation:004",
        "kind": "word_formation",
        "location": "line:15",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "63a3786a8446f66430eae1305a6ba0cbff1f1384e06009944b235aa17ee42bef",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controvert：動詞。「反論する、論駁する」。controversial と意味は近いが、現代英語では controversial の直接の活用形ではなく、別の動詞として扱う。"
      }
    ]
  },
  "specification_sha256": "f0de393d4d064190e23916b2e8bfda25b2b83fd29e14cf52395c894b8539d7e9",
  "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
  "normalized_input_sha256": "ecd65aba1b08fb830c82963545b431ea3abafbcdeaecd8b5a0edaa0febbebba3"
}
```
