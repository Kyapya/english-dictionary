# Independent checker handoff

Stage: `checker_passes/translation`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.translation.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_translation_v6

## 目的

英文・訳文・定義における意味の保存と方向を検査する。自然な意訳は認めるが、見出し語の構文差・含意・作用関係を誤学習させる変化は認めない。

## 担当タクソノミー分類

- `example_translation_alignment`
- `semantic_direction_reversal`

## 検査ルール

- 各例文と訳について、述語、主語・目的語・補語、行為者・経験者・対象・結果の意味役割を対応させる。
- 肯定・否定、比較基準、程度、数量、時制、相、法、条件、因果、目的を保存する。
- 修飾範囲、焦点、対比、情報構造、明示内容と文脈推論の境界、レジスターと話者評価を保存する。
- コロケーションのpattern・用途・英文・訳が同じ語義、品詞、完全フレームを表すか確認する。英文が別語義でも成立するだけでは合格にしない。
- 作用する側／される側、上位／下位、原因／結果、全体／部分、評価主体／評価対象を逆転させない。
- 日本語訳が自然でも、英文にない必然性・意図・結果・専門的効果を追加していればfindingとする。
- 同じ例文を異なる構文や語義の証明に使い回していないか確認する。
- 問題が1箇所に見える場合も、同じ訳語・関係が入力section内の別箇所で再発していないか確認する。

## 入力として受け取るセクション

- `definitions`
- `collocations_examples`
- `lexical_relations`

front matter、生成過程、通常チェックの過去判断、ACTIVE.mdは受け取らない。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "example_translation_alignment | semantic_direction_reversal",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "何がどの方向・範囲・強さで不一致か",
  "evidence_link_ids": [],
  "suggested_direction": "意味を変えずに直す方向"
}
```

`taxonomy_id`、位置、severity、根拠を必須とする。事実・語法・例文/訳の正誤に関わるものは `blocking`、事実関係を変えない局所的な日本語調整だけを `minor` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "translation",
  "taxonomy_ids": [
    "example_translation_alignment",
    "semantic_direction_reversal"
  ],
  "specification": "prompts/check_pass_translation_v6.md",
  "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
  "input_sections": {
    "definitions": [
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
  "specification_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
  "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
  "normalized_input_sha256": "7b8bedb6417de84814f037c78f8c3fcfff1eef494565178e617ea7389c2fb7e8"
}
```
