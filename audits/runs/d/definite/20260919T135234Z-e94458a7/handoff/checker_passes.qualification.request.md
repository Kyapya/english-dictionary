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
  "input_body_sha256": "6bf439cde2a5a009f8e4e4d27f7041f7af5c66dd15e9e51aaf59bfb705b46752",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "definite は16世紀初頭の英語で「固定された、確かな」の意味で使われ、ラテン語 dēfīnītus「境界を定められた、限定された、確定した」から来た。これは dēfīnīre「限界を定める、決定する、説明する」の過去分詞で、de-「完全に」と finis「境界、終わり」に分けて考えられる。18世紀初頭には文法用語として「限定する」の意味でも使われた。define、finite、definition、definitive、indefinite は同じ語源の語族に属する。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・definitely：副詞。「確実に、間違いなく、はっきりと」。話者の確信を表す文副詞としても、動詞・形容詞を強める副詞としても使う。  "
      },
      {
        "line": 24,
        "text": "・definiteness：名詞。「明確さ、確定性、定性」。文法では名詞句の指示対象が特定可能である性質を表す。  "
      },
      {
        "line": 25,
        "text": "・indefinite：接頭辞 in-「否定」を伴う関連形。「不確定な、漠然とした、定のない」。definite の単純な反意語になる用法と、文法用語としての用法がある。  "
      },
      {
        "line": 26,
        "text": "・definitive：同じラテン語幹系統の形容詞。「決定的な、最終的な」。definite よりも最終判断・決着の含みが強く、単なる語尾違いとして置き換えない。  "
      },
      {
        "line": 27,
        "text": "・define / definition：同じ語源にさかのぼる動詞・名詞。「境界を定める」「定義」。definite の直接の活用形ではないが、「曖昧さを境界づける」という意味のつながりがある。  "
      }
    ],
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】答え、決定、計画、日付、合意、意図などが、曖昧な候補や一時的な案ではなく、内容として定まり、変更される可能性が低いことを表す。必ずしも今後絶対に変更できないという意味ではなく、現時点で決定・約束・判断が明確になっていることに焦点がある。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
      },
      {
        "line": 156,
        "text": "【日本語訳・定義】変化、差、効果、兆候、利点などが、観察や比較によって実際に認められるほど明瞭・顕著であることを表す。必ずしも論理的に証明済み、絶対に疑いがないという意味ではなく、話し手が変化や特徴をはっきり認識しているという評価を含むことがある。  "
      },
      {
        "line": 268,
        "text": "3. 【形容詞・限定用法】具体的な、特定の"
      },
      {
        "line": 270,
        "text": "【日本語訳・定義】数量、期間、範囲、時点、形、情報などに明確な境界や内容があり、漠然としたものではないことを表す。特定の対象を指す場合でも、文脈上その対象を識別できるという文法上の意味とは異なり、ここでは内容・範囲・条件が具体的に定まっていることに焦点がある。  "
      },
      {
        "line": 384,
        "text": "4. 【形容詞・文法用語】定の、特定できる"
      },
      {
        "line": 386,
        "text": "【日本語訳・定義】文法で、名詞句の指示対象が、既出、状況上の唯一性、修飾語、共有知識などによって聞き手・読み手に特定可能であることを表す。英語では the が definite article「定冠詞」であり、対象が必ず世界に一つしかないこと、単数であること、以前に必ず言及されたことだけを意味するわけではない。  "
      },
      {
        "line": 474,
        "text": "5. 【形容詞・植物学】有限の、定数の"
      },
      {
        "line": 476,
        "text": "【日本語訳・定義】植物学で、花器官の数が一定で、通常は20未満で花弁数の倍数になること、または花序の主軸が花で終わり成長に限りがあることを表す専門用法である。一般語の「確実な」ではなく、数や成長が定まっているという意味で、definite inflorescence は determinate／cymose inflorescence に当たる。  "
      }
    ],
    "frequency_register": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
      },
      {
        "line": 44,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 46,
        "text": "【レジスター/領域】標準語で、会話・ビジネス・報道・公式文書まで広く使う。計画や合意の確定性を述べるときに多く、日常会話では sure が話者の確信、definite が決定や内容の確定を表しやすい。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
      },
      {
        "line": 158,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 160,
        "text": "【レジスター/領域】標準語で、会話・報道・評価・ビジネス文書まで使える。clear や obvious よりやや説明的・形式的で、improvement、difference、effect、sign など、観察できる変化や結果を修飾することが多い。  "
      },
      {
        "line": 268,
        "text": "3. 【形容詞・限定用法】具体的な、特定の"
      },
      {
        "line": 272,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 274,
        "text": "【レジスター/領域】標準語だが、契約・行政・学術・数学・技術文書で特に多い。specific は選び出された個別性、exact は数値や内容の厳密な一致、definite は範囲や条件が定まっていることを強調しやすい。  "
      },
      {
        "line": 384,
        "text": "4. 【形容詞・文法用語】定の、特定できる"
      },
      {
        "line": 388,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 390,
        "text": "【レジスター/領域】文法・言語学の用語。英語学習では the と a/an、無冠詞の使い分けを説明するときに頻出する。definite は「特定の」という一般語義にも近いが、文法では指示対象を同定できるという性質を指す。  "
      },
      {
        "line": 474,
        "text": "5. 【形容詞・植物学】有限の、定数の"
      },
      {
        "line": 478,
        "text": "【頻度】〈2/10〉  "
      },
      {
        "line": 480,
        "text": "【レジスター/領域】植物学に限られる低頻度の専門語。一般の文章では通常この意味で解釈せず、専門文献で floral organs、stamens、inflorescence などと共に現れる。  "
      }
    ],
    "usage_notes": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
      },
      {
        "line": 92,
        "text": "【語法・注意】certain は「真実だと確信している」「起こる可能性が高い」という話者の認識にも使えるが、definite は答え・計画・日付などの内容が決まっていることを強調しやすい。final は「それ以上変更しない最終段階」、firm は意思・態度の強さに焦点があるため、definite と完全には交換できない。`I have no definite plans.` は「将来の予定が一切ない」ではなく「決まった予定はない」という意味である。definite と definitely、definite と definitive を品詞や意味を考えずに置き換えない。綴りは definite であり、definate ではない。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
      },
      {
        "line": 206,
        "text": "【語法・注意】この用法の definite は「証明された」と同義ではない。`a definite improvement` は改善がはっきり認められるという意味で、科学的な因果関係が完全に証明されたという意味ではない。`a definite possibility` は「確実に起こること」ではなく「現実味のある可能性」である。obvious は誰にとってもすぐ分かること、clear は混乱や曖昧さがないこと、noticeable は知覚上目立つことを強調し、definite は変化・差・効果などを明確なものとして認めることに焦点がある。  "
      },
      {
        "line": 268,
        "text": "3. 【形容詞・限定用法】具体的な、特定の"
      },
      {
        "line": 315,
        "text": "【語法・注意】`a definite amount` は「量が決まっている」ことを示すが、必ずしも聞き手がその数値を知っているとは限らない。`specific` は「その特定のもの」という選択に、`exact` は誤差のない数値・内容に焦点がある。`definite information` は具体的で確認可能な情報、`definite plans` は決定済みの予定というように、名詞によって「具体的」と「確定した」のどちらが前面に出るかが変わる。`definite integral` は「確実な積分」ではなく、積分区間が定まった数学用語である。  "
      },
      {
        "line": 384,
        "text": "4. 【形容詞・文法用語】定の、特定できる"
      },
      {
        "line": 426,
        "text": "【語法・注意】文法上の definite は「前に一度出た名詞」に限られない。`the door` はその場に一つしかないドアを指せるし、`the book on the desk` は修飾語によってどの本か分かるため定になる。単数か複数か、可算か不可算かも決定条件ではなく、`the books`、`the water` も定になり得る。specific は「特定のものを意図している」という意味で、`a specific book` のように不定冠詞と共存できるが、specific だから文法上 definite になるわけではない。英語の the には、種類全体を述べる `The tiger is endangered.` のような総称的用法もあるため、definite と「唯一の個体」を機械的に同一視しない。  "
      },
      {
        "line": 474,
        "text": "5. 【形容詞・植物学】有限の、定数の"
      },
      {
        "line": 501,
        "text": "【語法・注意】この用法は一般英語の definite answer や definite plan とは別の専門的な意味である。`definite inflorescence` は花序の成長様式を指し、単に「明確な花序」という意味ではない。植物学では `indefinite` や `indeterminate` が、数や主軸の成長に固定された終点がない対照表現として使われる。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
      },
      {
        "line": 50,
        "text": "【コロケーション】"
      },
      {
        "line": 52,
        "text": "・a definite answer  "
      },
      {
        "line": 53,
        "text": "用途: 予想や曖昧な返事ではなく、決定した答えを求める。  "
      },
      {
        "line": 54,
        "text": "例: We need a definite answer by Friday, not another tentative suggestion.  "
      },
      {
        "line": 55,
        "text": "訳: 私たちは金曜日までに、また別の仮案ではなく確定した答えを必要としている。  "
      },
      {
        "line": 57,
        "text": "・a definite date for 〈event〉  "
      },
      {
        "line": 58,
        "text": "用途: 行事・開始・発売などの日付が決まっていることを表す。  "
      },
      {
        "line": 59,
        "text": "例: The organizers have not announced a definite date for the launch.  "
      },
      {
        "line": 60,
        "text": "訳: 主催者は発売の確定した日付をまだ発表していない。  "
      },
      {
        "line": 62,
        "text": "・no definite plans  "
      },
      {
        "line": 63,
        "text": "用途: 将来の予定がまだ決まっていないことを表す。  "
      },
      {
        "line": 64,
        "text": "例: I have no definite plans for the weekend yet.  "
      },
      {
        "line": 65,
        "text": "訳: 私は週末の具体的な予定をまだ決めていない。  "
      },
      {
        "line": 67,
        "text": "・anything definite about something  "
      },
      {
        "line": 68,
        "text": "用途: ある事柄について確定した情報があるかを尋ねる。  "
      },
      {
        "line": 69,
        "text": "例: Do you know anything definite about when the train will leave?  "
      },
      {
        "line": 70,
        "text": "訳: 列車がいつ出るかについて、何か確定した情報を知っていますか。  "
      },
      {
        "line": 72,
        "text": "・a definite yes/no  "
      },
      {
        "line": 73,
        "text": "用途: ためらいや条件付きではない、明確な肯定・拒否を表す。  "
      },
      {
        "line": 74,
        "text": "例: Her reply was a definite no, so we stopped asking.  "
      },
      {
        "line": 75,
        "text": "訳: 彼女の返事は明確な拒否だったので、私たちは尋ねるのをやめた。  "
      },
      {
        "line": 77,
        "text": "・be definite about 〈decision/position〉  "
      },
      {
        "line": 78,
        "text": "用途: 決定や立場を曖昧にせず、はっきり示す。  "
      },
      {
        "line": 79,
        "text": "例: Please be definite about your position before the meeting begins.  "
      },
      {
        "line": 80,
        "text": "訳: 会議が始まる前に、自分の立場を明確にしてください。  "
      },
      {
        "line": 82,
        "text": "・a definite commitment to do  "
      },
      {
        "line": 83,
        "text": "用途: ある行動を実行するという明確な確約を表す。  "
      },
      {
        "line": 84,
        "text": "例: The grant requires a definite commitment to complete the project.  "
      },
      {
        "line": 85,
        "text": "訳: その助成金には、プロジェクトを完了するという明確な確約が必要だ。  "
      },
      {
        "line": 87,
        "text": "・a definite agreement  "
      },
      {
        "line": 88,
        "text": "用途: 条件や内容が定まり、当事者間で成立した合意を表す。  "
      },
      {
        "line": 89,
        "text": "例: No definite agreement had been reached by the end of the meeting.  "
      },
      {
        "line": 90,
        "text": "訳: 会議の終了時までに、確定した合意は成立していなかった。  "
      },
      {
        "line": 154,
        "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
      },
      {
        "line": 164,
        "text": "【コロケーション】"
      },
      {
        "line": 166,
        "text": "・a definite improvement  "
      },
      {
        "line": 167,
        "text": "用途: 状態や成績が実際に良くなったと認められることを表す。  "
      },
      {
        "line": 168,
        "text": "例: The new treatment produced a definite improvement in her symptoms.  "
      },
      {
        "line": 169,
        "text": "訳: 新しい治療によって、彼女の症状には明らかな改善が見られた。  "
      },
      {
        "line": 171,
        "text": "・a definite difference between 〈A〉 and 〈B〉  "
      },
      {
        "line": 172,
        "text": "用途: 二つの対象の違いがはっきり認められることを表す。  "
      },
      {
        "line": 173,
        "text": "例: There is a definite difference between the two versions of the report.  "
      },
      {
        "line": 174,
        "text": "訳: その報告書の二つの版には明らかな違いがある。  "
      },
      {
        "line": 176,
        "text": "・a definite sign of something  "
      },
      {
        "line": 177,
        "text": "用途: ある状態や出来事を示す、見分けやすい兆候を表す。  "
      },
      {
        "line": 178,
        "text": "例: A sudden drop in demand is a definite sign of weakening consumer confidence.  "
      },
      {
        "line": 179,
        "text": "訳: 需要の急減は、消費者信頼感が弱まっている明らかな兆候だ。  "
      },
      {
        "line": 181,
        "text": "・have a definite effect on something  "
      },
      {
        "line": 182,
        "text": "用途: 行為・条件・政策などが、結果に明確な影響を与えることを表す。  "
      },
      {
        "line": 183,
        "text": "例: Sleep has a definite effect on how well people remember new information.  "
      },
      {
        "line": 184,
        "text": "訳: 睡眠は、人が新しい情報をどれだけよく覚えるかに明確な影響を及ぼす。  "
      },
      {
        "line": 186,
        "text": "・a definite advantage  "
      },
      {
        "line": 187,
        "text": "用途: 他と比べて認めやすい具体的な利点を強調する。  "
      },
      {
        "line": 188,
        "text": "例: The shorter route offers a definite advantage during the winter.  "
      },
      {
        "line": 189,
        "text": "訳: その短い経路は冬の間、明確な利点をもたらす。  "
      },
      {
        "line": 191,
        "text": "・a definite possibility  "
      },
      {
        "line": 192,
        "text": "用途: 単なる空想ではなく、現実に起こり得る可能性を表す。  "
      },
      {
        "line": 193,
        "text": "例: A delay is a definite possibility if the storm continues.  "
      },
      {
        "line": 194,
        "text": "訳: 嵐が続けば、遅延は十分に現実的な可能性だ。  "
      },
      {
        "line": 196,
        "text": "・see a definite change in something  "
      },
      {
        "line": 197,
        "text": "用途: 状態や傾向の変化を観察してはっきり認める。  "
      },
      {
        "line": 198,
        "text": "例: We can see a definite change in customer behavior after the price increase.  "
      },
      {
        "line": 199,
        "text": "訳: 値上げ後、顧客の行動に明らかな変化が見られる。  "
      },
      {
        "line": 201,
        "text": "・with a definite sense of 〈emotion〉  "
      },
      {
        "line": 202,
        "text": "用途: 表情・声・行動などに特定の感情が明確に表れている様子を示す。  "
      },
      {
        "line": 203,
        "text": "例: He left the room with a definite sense of relief.  "
      },
      {
        "line": 204,
        "text": "訳: 彼は明らかに安堵した様子で部屋を出た。  "
      },
      {
        "line": 268,
        "text": "3. 【形容詞・限定用法】具体的な、特定の"
      },
      {
        "line": 278,
        "text": "【コロケーション】"
      },
      {
        "line": 280,
        "text": "・a definite amount of 〈money/material〉  "
      },
      {
        "line": 281,
        "text": "用途: 金額や物質の量が一定の範囲・数量として定まっていることを表す。  "
      },
      {
        "line": 282,
        "text": "例: The machine requires a definite amount of oil to operate safely.  "
      },
      {
        "line": 283,
        "text": "訳: その機械を安全に稼働させるには、一定量の油が必要だ。  "
      },
      {
        "line": 285,
        "text": "・a definite number of 〈people/items〉  "
      },
      {
        "line": 286,
        "text": "用途: 人数や個数が曖昧でなく、決まった数であることを表す。  "
      },
      {
        "line": 287,
        "text": "例: Only a definite number of students can join the laboratory tour.  "
      },
      {
        "line": 288,
        "text": "訳: 研究室見学に参加できる学生数には上限が決まっている。  "
      },
      {
        "line": 290,
        "text": "・for a definite period  "
      },
      {
        "line": 291,
        "text": "用途: 期間の終点または長さがあらかじめ定められていることを表す。  "
      },
      {
        "line": 292,
        "text": "例: The equipment may be rented for a definite period of six months.  "
      },
      {
        "line": 293,
        "text": "訳: その設備は6か月という定められた期間、借りることができる。  "
      },
      {
        "line": 295,
        "text": "・within definite limits  "
      },
      {
        "line": 296,
        "text": "用途: 許容範囲や境界を明確に限定する。  "
      },
      {
        "line": 297,
        "text": "例: The temperature must remain within definite limits during transport.  "
      },
      {
        "line": 298,
        "text": "訳: 輸送中、温度は明確に定められた範囲内に保たなければならない。  "
      },
      {
        "line": 300,
        "text": "・definite information about 〈topic〉  "
      },
      {
        "line": 301,
        "text": "用途: 推測や噂ではなく、内容が確認できる具体的な情報を表す。  "
      },
      {
        "line": 302,
        "text": "例: We need definite information about the delivery schedule before placing the order.  "
      },
      {
        "line": 303,
        "text": "訳: 注文を出す前に、納入予定について具体的な情報が必要だ。  "
      },
      {
        "line": 305,
        "text": "・a definite shape/form  "
      },
      {
        "line": 306,
        "text": "用途: 輪郭や形式が一定で、別の形と区別できることを表す。  "
      },
      {
        "line": 307,
        "text": "例: The crystals grow into a definite shape under controlled conditions.  "
      },
      {
        "line": 308,
        "text": "訳: その結晶は、管理された条件下で一定の形に成長する。  "
      },
      {
        "line": 310,
        "text": "・a definite integral  "
      },
      {
        "line": 311,
        "text": "用途: 数学で、積分区間の上下端が指定された定積分を指す。  "
      },
      {
        "line": 312,
        "text": "例: The area under the curve can be calculated with a definite integral.  "
      },
      {
        "line": 313,
        "text": "訳: 曲線の下の面積は定積分で計算できる。  "
      },
      {
        "line": 384,
        "text": "4. 【形容詞・文法用語】定の、特定できる"
      },
      {
        "line": 394,
        "text": "【コロケーション】"
      },
      {
        "line": 396,
        "text": "・the definite article  "
      },
      {
        "line": 397,
        "text": "用途: 英語の the のように、聞き手・読み手が指示対象を特定できることを示す冠詞を指す。  "
      },
      {
        "line": 398,
        "text": "例: In English, the is the definite article used before singular and plural noun phrases.  "
      },
      {
        "line": 399,
        "text": "訳: 英語では the が、単数・複数の名詞句の前に使われる定冠詞である。  "
      },
      {
        "line": 401,
        "text": "・a definite noun phrase  "
      },
      {
        "line": 402,
        "text": "用途: 指示対象が文脈から特定可能な名詞句を指す。  "
      },
      {
        "line": 403,
        "text": "例: In “the book on the desk,” the whole phrase is a definite noun phrase.  "
      },
      {
        "line": 404,
        "text": "訳: 「机の上のその本」では、句全体が定名詞句である。  "
      },
      {
        "line": 406,
        "text": "・definite reference to 〈person/thing〉  "
      },
      {
        "line": 407,
        "text": "用途: ある人物・物を、聞き手がどれか判断できる形で指すことを表す。  "
      },
      {
        "line": 408,
        "text": "例: The article makes a definite reference to the company’s earlier report.  "
      },
      {
        "line": 409,
        "text": "訳: その記事は会社の以前の報告書を明確に指し示している。  "
      },
      {
        "line": 411,
        "text": "・a definite description of 〈person/thing〉  "
      },
      {
        "line": 412,
        "text": "用途: 固有名を使わず、記述によって指示対象を同定する表現を指す。  "
      },
      {
        "line": 413,
        "text": "例: “The first person to arrive” is a definite description in this context.  "
      },
      {
        "line": 414,
        "text": "訳: この文脈では、「最初に到着した人」は確定記述である。  "
      },
      {
        "line": 416,
        "text": "・a definite referent  "
      },
      {
        "line": 417,
        "text": "用途: 名詞句が指し示す、文脈上特定可能な対象を指す。  "
      },
      {
        "line": 418,
        "text": "例: The plural noun phrase can still have a definite referent.  "
      },
      {
        "line": 419,
        "text": "訳: 複数名詞句でも、指示対象を特定できる場合がある。  "
      },
      {
        "line": 421,
        "text": "・definite and indefinite articles  "
      },
      {
        "line": 422,
        "text": "用途: the と a/an のように、指示対象の特定可能性が異なる冠詞を対比する。  "
      },
      {
        "line": 423,
        "text": "例: The lesson contrasts definite and indefinite articles in everyday sentences.  "
      },
      {
        "line": 424,
        "text": "訳: その授業では、日常文における定冠詞と不定冠詞を対比している。  "
      },
      {
        "line": 474,
        "text": "5. 【形容詞・植物学】有限の、定数の"
      },
      {
        "line": 484,
        "text": "【コロケーション】"
      },
      {
        "line": 486,
        "text": "・definite stamens  "
      },
      {
        "line": 487,
        "text": "用途: 花弁数との関係で数が一定の雄しべを指す。  "
      },
      {
        "line": 488,
        "text": "例: The species has definite stamens, usually in a fixed multiple of the number of petals.  "
      },
      {
        "line": 489,
        "text": "訳: その種には、通常、花弁数の決まった倍数になる定数の雄しべがある。  "
      },
      {
        "line": 491,
        "text": "・a definite inflorescence  "
      },
      {
        "line": 492,
        "text": "用途: 主軸が花で終わり、伸長に限りがある有限花序を指す。  "
      },
      {
        "line": 493,
        "text": "例: The plant develops a definite inflorescence in which the main axis ends in a flower.  "
      },
      {
        "line": 494,
        "text": "訳: その植物は、主軸が花で終わる有限花序を形成する。  "
      },
      {
        "line": 496,
        "text": "・definite growth  "
      },
      {
        "line": 497,
        "text": "用途: 植物体や器官の成長が一定の段階で止まる定限成長を表す。  "
      },
      {
        "line": 498,
        "text": "例: Definite growth is common in some compact flowering plants.  "
      },
      {
        "line": 499,
        "text": "訳: 定限成長は、一部の小型の開花植物でよく見られる。  "
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
  "source_artifact_sha256": "6c4a9cb96ef979d6caee6685612f8a3af1eadb335e8d0d86ec675b47df5e2d67",
  "normalized_input_sha256": "82167ed161dae69f253ad6653e0f1bc55a1eb1730ce36969f254b29f8de66122"
}
```
