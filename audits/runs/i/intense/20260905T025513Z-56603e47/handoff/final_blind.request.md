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


## Input packet

```json
{
  "stage": "final_blind",
  "entry_body": "\n＃発音記号\n\n米・英: /ɪnˈtens/。2音節で、第2音節の /tens/ に主強勢がある。  \n\n＃語源\n\n15世紀初頭に、フランス語を経てラテン語 intensus「引き伸ばされた、張り詰めた」から英語に入った。intensus は intendere の過去分詞に由来する。  \n\n現在の intense は、程度・力・感情などが極端に強いことを表す。  \n\n＃語形成\n\n・intensity（名詞）— 強度、激しさ。  \n・intensify（動詞）— 強まる、強める。自動詞・他動詞の両方で使う。  \n・intensive（形容詞）— 集中的な、徹底的な。intense と同じく短期間の多くの活動を表せるが、intense は参加者の感情を示唆しやすく、intensive はより客観的な説明になりやすい。  \n・intensification（名詞）— 強化、激化。  \n\n＃コアイメージ\n\n程度・力・エネルギー・感情の強さが高く、対象に応じて「非常に強い」「活動が激しい」「強い感情が表に出る」と枝分かれする。  \n\n・対象の程度・感覚・感情が極端に高い → 「強烈な、非常に強い」（語義1）  \n・活動や行動が短期間に激しく展開する → 「激しい、活動量の多い」（語義2）  \n・人や表情などに強い感情・意見・考えが現れる → 「真剣で感情の強い、張り詰めた」（語義3）  \n\n＃意味・用法・関連表現\n\n1. 【形容詞・限定／叙述】強烈な、非常に強い\n\n【日本語訳・定義】感情、感覚、痛み、暑さ、色、関心、圧力などの程度・強度が極端に高いこと。intense pleasure「非常に強い喜び」のように、好ましい対象にも使う。  \n\n【頻度】〈9/10〉  \n\n※Oxford 5000ではC1レベルの学習語彙ラベルで、上の数値は語義別の厳密な順位ではない。  \n\n【レジスター/領域】一般語として使われる形容詞。  \n\n【文法パターン】intense + 〈感情・感覚・性質・熱・色などを表す名詞〉＝程度・強度が非常に高い～／under intense pressure/scrutiny＝強い圧力・厳しい監視の下で  \n\n【コロケーション】\n\n・intense pain  \n用途: 身体的な痛みが非常に強いことを表す。  \n例: He felt intense pain in his lower back.  \n訳: 彼は腰の下部に激しい痛みを感じた。  \n\n・intense heat  \n用途: 暑さや熱が極端に強いことを表す。  \n例: The intense heat made it dangerous to work outside.  \n訳: 強烈な暑さのため、屋外で働くのは危険だった。  \n\n・intense pressure  \n用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  \n例: The new manager is under intense pressure to improve the results.  \n訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  \n\n・intense interest  \n用途: ある対象に向けられる関心が非常に強いことを表す。  \n例: The discovery attracted intense interest from researchers around the world.  \n訳: その発見は世界中の研究者から強い関心を集めた。  \n\n・intense anger  \n用途: 怒りの感情が非常に強いことを表す。  \n例: The decision provoked intense anger among local residents.  \n訳: その決定は地元住民の激しい怒りを引き起こした。  \n\n・intense blue  \n用途: 色が非常に鮮やかで、強い印象を与えることを表す。  \n例: The intense blue of the lake stood out against the white snow.  \n訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  \n\n【語法・注意】intense は感情、感覚、熱、色、関心、圧力など、強さの対象を表す名詞と結びつく。intense pleasure のような好ましい対象にも、intense pain や intense anger のような好ましくない対象にも使える。  \n\n【類義語】\n\n・strong  \n定義: 力、程度、効果などが大きい。  \n頻度: 〈10/10〉  \n違い: strong は幅広い強さを表し、intense は程度が極端に高い場合に使う。  \n例: The coffee has a strong flavor.  \n訳: そのコーヒーは味が濃い。  \n\n・extreme  \n定義: 普通の範囲を超え、極端な。  \n頻度: 〈8/10〉  \n違い: extreme は通常の範囲や限界からの逸脱に焦点があり、intense は体感や感情の強さにも使う。  \n例: The region experienced extreme temperatures last summer.  \n訳: その地域は昨夏、極端な気温に見舞われた。  \n\n・powerful  \n定義: 大きな力や効果を持つ。  \n頻度: 〈8/10〉  \n違い: powerful は作用する力や影響力に焦点があり、intense は経験される強度や圧にも使う。  \n例: The film presents a powerful image of life after the disaster.  \n訳: その映画は災害後の生活を力強い映像で描いている。  \n\n2. 【形容詞・限定／叙述】激しい、活動量の多い\n\n【日本語訳・定義】活動や行動が深刻で、短い期間に多くの動き・エネルギー・決意・集中を伴うこと。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】一般語として使われる形容詞。  \n\n【文法パターン】intense + 〈活動・競争〉＝短期間に展開する非常に激しい活動・競争／intense + 〈energy・determination・concentration〉＝極端に強いエネルギー・決意・集中  \n\n【コロケーション】\n\n・intense competition  \n用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。  \n例: There is intense competition for places at the top universities.  \n訳: 一流大学の枠をめぐって激しい競争がある。  \n\n・intense activity  \n用途: 活動が短期間に激しく展開し、多くの動きを伴うことを表す。  \n例: The airport experienced a period of intense activity before the holiday.  \n訳: その空港では休暇前に活動が非常に活発な時期があった。  \n\n【語法・注意】intense と intensive は、どちらも短期間に多くの活動があることを表せる。intense は参加者の感情を示唆しやすく、intensive はより客観的な説明になりやすい。  \n\n【類義語】\n\n・fierce  \n定義: 競争、対立、議論などが非常に激しい。  \n頻度: 〈8/10〉  \n違い: fierce は攻撃性や対立を含みやすく、intense は敵意のない活動の強さにも使える。  \n例: The teams are in fierce competition for the championship.  \n訳: そのチームたちは優勝をめぐって激しく競い合っている。  \n\n・vigorous  \n定義: 活動や努力が精力的で力強い。  \n頻度: 〈7/10〉  \n違い: vigorous は活力や積極的なエネルギーに焦点があり、intense は活動の緊張や負荷も表す。  \n例: The proposal prompted vigorous discussion among the experts.  \n訳: その提案は専門家の間で活発な議論を促した。  \n\n・strenuous  \n定義: 身体的・精神的に大きな努力を要する。  \n頻度: 〈6/10〉  \n違い: strenuous は行為がきつく多大な努力を要することに焦点があり、intense は活動の集中度や緊張感も表す。  \n例: The climbers faced a strenuous ascent in freezing weather.  \n訳: 登山者たちは極寒の中で厳しい登りに直面した。  \n\n3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた\n\n【日本語訳・定義】人、視線、表情、関係などが、非常に強い感情、意見、考え、目的意識を示すこと。真剣で集中しているという印象や、感情が強く張り詰めた印象を表す。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】一般語として使われる形容詞。  \n\n【文法パターン】an intense person＝強い感情・意見・考えを示す人／an intense look/gaze＝強い感情を帯びた視線／be intense about 〈事柄〉＝〈事柄〉について強い意見や熱意を示す／an intense relationship＝感情的な結びつきの強い関係  \n\n【コロケーション】\n\n・an intense look  \n用途: 強い感情や集中を帯びた視線・表情を表す。  \n例: She gave him an intense look when he mentioned the accusation.  \n訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  \n\n・an intense person  \n用途: 感情、意見、目的意識などが強く、存在感のある人を表す。  \n例: He is an intense person who takes every project very seriously.  \n訳: 彼はどのプロジェクトにも非常に真剣に取り組む、熱意の強い人だ。  \n\n・be intense about 〈事柄〉  \n用途: ある事柄について強い意見や熱意を持ち、真剣にこだわることを表す。  \n例: She is intense about keeping every detail of the experiment accurate.  \n訳: 彼女は実験の細部をすべて正確に保つことに非常にこだわっている。  \n\n・an intense relationship  \n用途: 感情的な結びつきや相互作用が非常に強い関係を表す。  \n例: Their intense relationship left little room for emotional distance.  \n訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  \n\n【語法・注意】人や表情に intense を使うと、強い感情・意見・考えが表に現れ、真剣で張り詰めた印象を表す。人、視線、関係、about 〈事柄〉など、何の強さを述べるかによって日本語訳を調整する。  \n\n【類義語】\n\n・serious  \n定義: ふざけておらず、真剣な、または重大な。  \n頻度: 〈10/10〉  \n違い: serious は真面目さや重要性に焦点があり、intense は強い感情や張り詰めた印象も表す。  \n例: She looked serious during the interview.  \n訳: 面接中、彼女は真剣な表情をしていた。  \n\n・passionate  \n定義: 人や活動に強い熱意・愛着を持つ。  \n頻度: 〈9/10〉  \n違い: passionate は熱意や強い関与を表し、intense より肯定的な評価になりやすい。  \n例: He is passionate about improving access to education.  \n訳: 彼は教育へのアクセス改善に情熱を注いでいる。  \n\n・earnest  \n定義: 目的や発言が誠実で、真剣な。  \n頻度: 〈6/10〉  \n違い: earnest は誠実さや真摯さに焦点があり、intense は感情の強さや対人的な圧も表す。  \n例: She made an earnest appeal for help.  \n訳: 彼女は助けを求めて真摯に訴えた。  ",
  "_output_metadata": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-intense-20260905T025513Z-56603e47",
    "context_id": "blind-intense-context-20260905T025513Z-56603e47",
    "input_body_sha256": "775f1956389033859823911e7aa86ac43f54a7d67c8c24eda12de863b53444dc",
    "prompt_sha256": "1bb7b1a1c7f589a50a704d1ce6c1ecd0bfb1c9fb689fd481d21bf608438eb7b5",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false
  }
}
```
