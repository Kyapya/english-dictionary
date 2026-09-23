# Independent review handoff

Stage: `final_blind`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session.

## Prompt

# final_blind_prompt_v2

## 目的

修正後の記事だけから、通常チェックや既知findingに誘導されない独立棚卸しと問題探索を行う。入力境界は `scripts/run_word.py` が強制し、この実行には生成文脈、`ACTIVE.md`、queue、監査記録、checker/cold finding、resolutionを渡さない。

## 独立棚卸し

- 見出し語から主要な品詞、語義、派生・転換、専門用法、完全な統語フレームをゼロベースで候補化し、各候補を `included` または `excluded` と判定する。
- 本文の語義番号や分類を候補集合の出発点にしない。
- candidate の `frame` は、同じ語義に属することを独立に確認できる粒度にする。表面上同じ見出し語だからという理由だけで、意味中心や主体側／対象側の境界が異なり得る複数フレームを `;` などで一候補へ束ねない。
- 複数フレームを一candidateにまとめる場合は、それらが同じ中心意味・同じ意味役割・同じ包含／除外境界を共有することを先に確認する。どれか1つでも別語義へ自然に帰属し得るなら、そのフレームだけを独立candidateへ分離する。
- とくに、同じ語義ブロック内に置かれた文法パターン・コロケーション・定着フレームのうち、別語義の定義にも自然に適合し得るものは高リスク項目として個別に再分類する。候補全体の代表ラベルが正しいことを理由に、内部の1フレームの帰属を自動的に正しいとみなさない。
- この粒度規則は新しいレビュー段階を追加するものではない。既存のfinal blind棚卸しの中で、語義混入リスクのあるフレームだけを必要な粒度に分ける。
- 各候補には、正しい意味関係が本文全体で満たすべき境界・作用方向・包含/除外関係・一般化範囲を、1件以上の原子的 `semantic_assertions` として付ける。
- 記事全体を横断し、事実・語法・発音、例文/訳、語義境界、主要語義/構文の欠落・過剰、内部矛盾、根拠との不整合になり得る問題を `article_findings` に記録する。
- 同一candidateにまとめた複数フレームのうち1つだけが assertion を満たさない場合も、candidate全体をpassさせず、そのフレームを分離して `article_findings` の対象として扱う。

## 出力

`final_blind_review_v2` JSONとして、`provisional_decision`、`independent_candidates`、`article_findings` を出力する。candidateは `id`、`surface_form`、`frame`、`meaning`、`disposition`、`rationale`、1件以上の `semantic_assertions` を持つ。assertionは `id`、`statement`、`polarity` (`must_hold | must_not_hold`)、`scope` を持つ。findingは `id`、`taxonomy_id`、`location`、`severity`、`rationale` を持つ。

本文側target ID、根拠リンクID、通常側candidate ID、resolution IDは出力しない。暫定合否は、内容上のblocker候補があれば `reject`、なければ `pass` とする。

出力契約: candidateの `rationale` には、そのcandidateの `surface_form`、`frame`、`meaning` のいずれか1つを全文そのまま含め、固有の理由を述べる。findingには本文から抜き出した `scope_anchors`（各要素に `id`、`exact_quote`、`location_hint`）を付け、`rationale` に少なくとも1つの `exact_quote` 全文と、その引用に即した理由を含める。


## Input packet

```json
{
  "stage": "final_blind",
  "entry_body": "\n＃発音記号\n\n米: /ˌkɑːntrəˈvɝːʃəl/｜英: /ˌkɒntrəˈvɜːʃəl/。米英とも4音節で、第3音節の /vɝː/・/vɜː/ に主強勢がある。第1音節の /ˌkɑːn/・/ˌkɒn/ には副次強勢を示す。米語では /ˌkɑːntrəˈvɝːsiəl/ に近い5音節寄りの発音も聞かれるが、通常の学習上は /ˈvɝːʃəl/・/ˈvɜːʃəl/ の部分を基準にする。  \n\n＃語源\n\n16世紀後半に使われ始めた語で、後期ラテン語 controversialis「論争に関する」から来た。controversia「論争」は controversus「反対方向に向けられた、争われた」に関係し、contra-/contro-「反対に」と versus「向けられた、転じた」（vertere「向きを変える」の過去分詞）に分けて考えられる。初出年代は資料により1580年代、1583年、1575–85年など差があるため、特定の年として暗記しない。  \n\n＃語形成\n\n・controversy：名詞。「論争、論争点、物議」。controversial と同じ語族の中心語で、public controversy のように使う。  \n・controversially：副詞。「物議を醸す形で、論争を呼ぶことに」。文全体や発言・判断の仕方を修飾する。  \n・controversialist：名詞。「論争家、論争に加わる人」。人の性向または論争上の立場を指す硬めの語。  \n・controvert：動詞。「反論する、論駁する」。controversial と意味は近いが、現代英語では controversial の直接の活用形ではなく、別の動詞として扱う。  \n\n＃意味・用法・関連表現\n\n1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す\n\n【日本語訳・定義】政策・決定・主張・作品・発言・人物などが、社会全体または特定の集団の中で、強い意見の対立、批判、反対を引き起こしていることを表す。事実として真偽が決まっていないことを必ずしも含まず、悪い、違法、意図的に挑発的だという意味でもない。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準語で、会話・ニュース・政治・文化・学術・ビジネスの文章まで広く使う。controversial は「多くの人が反対している」と同じではなく、賛成・反対の議論が強く起きている状態を指す。  \n\n【文法パターン】be/become/remain/prove controversial＝論争を呼ぶ・論争の的であり続ける・結果的に物議を醸す／a controversial 〈issue・decision・policy・claim・statement・figure・book・film〉＝論争を呼ぶ〈問題・決定・政策・主張・発言・人物・本・映画〉／highly/widely controversial＝非常に／広く物議を醸す／controversial among/within 〈group〉＝〈集団〉の間で論争を呼ぶ／controversial in some circles＝一部の界隈では物議を醸す／it remains controversial whether ...＝…かどうかは依然として議論が分かれる／be controversial enough to do＝～するほど物議を醸す／too controversial to do＝物議を醸しすぎて～できない。  \n\n【コロケーション】\n\n・a controversial issue  \n用途: 社会的に賛否が対立している問題を指す。  \n例: The use of facial-recognition technology remains a controversial issue.  \n訳: 顔認証技術の利用は依然として論争を呼ぶ問題だ。  \n\n・a controversial decision  \n用途: 決定の妥当性や影響をめぐって強い反対・批判が出ていることを表す。  \n例: The committee made a controversial decision to cancel the exhibition.  \n訳: 委員会は展示会を中止するという物議を醸す決定を下した。  \n\n・a controversial figure  \n用途: 功績と批判の両方があり、評価が大きく割れている人物を指す。  \n例: The historian remains a controversial figure in the region.  \n訳: その歴史家はその地域で今も評価が大きく分かれる人物だ。  \n\n・a highly controversial proposal  \n用途: 提案に対して非常に強い賛否や反発が起きていることを強調する。  \n例: The city council postponed a highly controversial proposal.  \n訳: 市議会は非常に物議を醸している提案を延期した。  \n\n・controversial among 〈group〉  \n用途: どの集団の中で意見が割れているかを限定する。  \n例: The interpretation is controversial among constitutional scholars.  \n訳: その解釈は憲法学者の間で議論が分かれている。  \n\n・controversial in some circles  \n用途: 社会全体ではなく、特定の界隈で物議を醸していることを示す。  \n例: The advertising campaign is controversial in some circles but popular with younger viewers.  \n訳: その広告キャンペーンは一部では物議を醸しているが、若い視聴者には人気がある。  \n\n・it remains controversial whether ...  \n用途: 判断が現在も決着していないことを述べる。  \n例: It remains controversial whether the policy reduced inequality.  \n訳: その政策が格差を縮小したかどうかは、今も議論が分かれている。  \n\n・a controversial remark  \n用途: 発言が批判や反発を招く内容だったことを表す。  \n例: The minister's controversial remark drew criticism from both parties.  \n訳: 大臣の物議を醸す発言は両党から批判を招いた。  \n\n・become controversial after ...  \n用途: 当初は普通だった対象が、後から知られた事実や変化によって論争の的になることを表す。  \n例: The renovation plan became controversial after residents learned the full cost.  \n訳: 住民が総費用を知った後、その改修計画は物議を醸すようになった。  \n\n【語法・注意】対象を主語にした be controversial は「その対象が論争の的だ」という意味で、必ずしも対象自身が議論を仕掛けるわけではない。人物についても通常は「評価が割れている人物」の意味であり、「論争を好む人」という性向を言いたいときは語義2を確認する。highly は対立の強さ、widely は論争が広い範囲に及ぶことを示す。controversial を「間違った」「受け入れられない」と自動的に訳さず、何が誰の間で争われているかを among/within 句や文脈で補う。  \n\n【類義語】\n\n・contentious  \n定義: 議論や対立を引き起こしやすい、争点になっている。  \n頻度: 〈8/10〉  \n違い: contentious は問題・決定が争いを生みやすい性質や、当事者間の対立の強さに焦点があり、controversial より対立的に響くことがある。  \n例: The contentious issue delayed the negotiations for weeks.  \n訳: その対立を招く争点のために、交渉は何週間も遅れた。  \n\n・disputed  \n定義: 真偽・権利・解釈などが争われている、意見が一致していない。  \n頻度: 〈8/10〉  \n違い: disputed は「正しいか、誰のものかなどが争われている」という未確定性を強調し、controversial のような広い世論上の物議まで必ずしも含まない。  \n例: The map shows the disputed border in a different color.  \n訳: その地図は争われている国境を別の色で示している。  \n\n・debatable  \n定義: 議論の余地があり、結論を一つに決めにくい。  \n頻度: 〈7/10〉  \n違い: debatable は主張や判断の妥当性を論じられることに焦点があり、controversial より感情的な反発や大きな社会的対立を含まない場合が多い。  \n例: Whether the change improved efficiency is debatable.  \n訳: その変更が効率を高めたかどうかは議論の余地がある。  \n\n・polarizing  \n定義: 人々を賛成側と反対側へ大きく分断する。  \n頻度: 〈7/10〉  \n違い: polarizing は意見の対立を二極化させる効果を強調する。controversial は意見が割れていても、二つの陣営に明確に分かれるとは限らない。  \n例: The candidate's polarizing speech dominated the news cycle.  \n訳: その候補者の社会を二極化させる演説が報道を席巻した。  \n\n・provocative  \n定義: 強い反応や議論を意図的または効果として引き起こす、挑発的な。  \n頻度: 〈8/10〉  \n違い: provocative は発言者・作者が反応を誘う性質や意図に焦点がある。controversial は実際に物議が生じている状態を表し、意図を必要としない。  \n例: The artist is known for provocative questions about public memory.  \n訳: その芸術家は公共の記憶について挑発的な問いを投げかけることで知られている。  \n\n・divisive  \n定義: 人々や集団の間に深い対立を生じさせる、分断を招く。  \n頻度: 〈7/10〉  \n違い: divisive は社会的な分断や関係悪化という結果を強く示す。controversial は分断に至らず、単に議論や批判を招く場合にも使える。  \n例: The divisive reform split the professional association.  \n訳: その分断を招く改革は専門職団体を二分した。  \n\n・polemical  \n定義: 論争を仕掛ける、または論争的な主張を展開する。  \n頻度: 〈4/10〉  \n違い: polemical は文章・議論・論者の攻撃的な論争スタイルに寄りやすく、controversial より硬く、意図的な論争性を含みやすい。  \n例: The book adopts a polemical tone toward established theories.  \n訳: その本は確立した理論に対して論争的な調子を取っている。  \n\n【反意語】\n\n・uncontroversial  \n定義: 意見の強い対立や広い反発を招かない、異論の少ない。  \n頻度: 〈6/10〉  \n違い: controversial の直接的な反対語で、問題・判断・人物などについて大きな論争が起きていない状態を表す。  \n例: The committee reached an uncontroversial agreement on the timetable.  \n訳: 委員会は日程について異論の少ない合意に達した。  \n\n・noncontroversial  \n定義: 論争的でない、特に意見の対立を起こさない。  \n頻度: 〈5/10〉  \n違い: noncontroversial も直接的な反対語だが、uncontroversial より説明的・形式的に見えることがある。  \n例: The report limits itself to noncontroversial background facts.  \n訳: その報告書は論争のない背景事実に内容を限定している。  \n\n2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な\n\n【日本語訳・定義】人が性格や態度の傾向として、議論を好んだり、既存の立場に反論して対立を生みやすかったりすることを表す。辞書に記載される低頻度の語義で、現代の controversial person は通常、語義1の「論争の的となっている人物」と解釈される。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】まれで、辞書的・形式的・文学的な説明に現れやすい。現代の一般的な文章で人の性向を表すなら argumentative、disputatious、polemical の方が意味を明確にしやすい。  \n\n【文法パターン】a controversial temperament＝論争を好む気質／a controversial manner＝対立を生みやすい態度／be controversial by temperament＝性向として論争的である／be controversial in debate＝議論で意図的に反論を重ねる。  \n\n【コロケーション】\n\n・a controversial temperament  \n用途: 人が性格的に議論や対立を好むことを、まれな形容詞用法で表す。  \n例: The columnist has a controversial temperament and treats every meeting as a public debate.  \n訳: そのコラムニストは論争を好む気質で、どの会議も公開討論のように扱う。  \n\n・a controversial manner  \n用途: 人が対立を招きやすい仕方で話したり振る舞ったりすることを表す。  \n例: Her controversial manner turned minor technical disagreements into public arguments.  \n訳: 彼女の対立を生みやすい態度は、ささいな技術上の意見の違いまで公の論争に変えた。  \n\n・be controversial by temperament  \n用途: 物議を醸す個別の行動ではなく、もともとの性向が論争的だと述べるまれな構文。  \n例: He was controversial by temperament, challenging even minor points in every debate.  \n訳: 彼は性向として論争的で、どの討論でもささいな点にまで反論した。  \n\n・be controversial in debate  \n用途: 議論の最中に、立場そのものよりも反論を重ねる性向が目立つことを表す。  \n例: The speaker was controversial in debate because he deliberately attacked each established position.  \n訳: その話者は確立した立場を一つ一つ意図的に攻撃したため、討論では論争的だった。  \n\n【語法・注意】この語義では controversial が人の性向を直接表すが、現代の「論争の的となる人物」という普通の解釈と形が同じなので、文脈で区別する必要がある。a controversial politician は通常語義1であり、気質を明示する temperament、manner、by temperament などがあって初めて語義2に近づく。意見が割れているだけなら語義1、本人が反論・対立を好むことまで言うなら語義2である。  \n\n【類義語】\n\n・disputatious  \n定義: 議論や口論を好む、論争好きな。  \n頻度: 〈4/10〉  \n違い: disputatious は人の性向そのものを表す明確な語で、controversial のまれな語義より自然に「口論好き」の意味を示す。  \n例: His disputatious nature made routine committee work exhausting.  \n訳: 彼の論争好きな性質のため、通常の委員会業務は疲れるものになった。  \n\n・argumentative  \n定義: すぐに反論する、議論好きな、口論を招く。  \n頻度: 〈7/10〉  \n違い: argumentative は日常的で、人が何にでも反論する傾向を表す。controversial より口論・反論の行動が前面に出る。  \n例: The child became argumentative whenever the rules were explained.  \n訳: その子は規則を説明されるといつも反論するようになった。  \n\n・polemical  \n定義: 論争を仕掛ける、攻撃的に論争する。  \n頻度: 〈4/10〉  \n違い: polemical は論者・文章・議論の意図的で攻撃的な論争性に焦点があり、controversial より文語的である。  \n例: The polemical writer challenged every compromise proposed by the panel.  \n訳: その論争的な筆者は、委員会が提案した妥協案すべてに異議を唱えた。  \n\n・contentious  \n定義: 対立的で、争いを引き起こしやすい。  \n頻度: 〈8/10〉  \n違い: contentious は人の態度にも使えるが、敵対的・喧嘩腰の含みが出やすい。controversial の語義2は、必ずしも敵意や攻撃性まで含まない。  \n例: The manager's contentious style made open discussion difficult.  \n訳: その管理職の対立的なスタイルは、率直な話し合いを難しくした。  ",
  "_output_metadata": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-controversial-20260912T015542Z-872034dc",
    "context_id": "blind-controversial-context-20260912T015542Z-872034dc",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "prompt_sha256": "3a481b4b5b1236ff386e148bcacc574570b305e79f5e155e9afcd34091f7785c",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false
  },
  "contract_version": "review_preflight_v1"
}
```
