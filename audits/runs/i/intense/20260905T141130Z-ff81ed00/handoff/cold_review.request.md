# Independent review handoff

Stage: `cold_review`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session.

## Prompt

# Cold review prompt v1

英単語解説として問題がないか、記事全体を横断して徹底的に走査し、内容上の問題を前提なしで指摘してください。各文の正誤だけでなく、語義の分け方・境界・重複と、学習者が説明から誤った一般化をしないかも確認してください。また、断定的な主張に対して反例を探すことで記述に問題が無いか確認をしてください。

返答はJSONオブジェクトとし、`summary` と `findings` を含めてください。問題候補がなければ `findings` は空配列にし、`summary` に「問題候補なし」と明記してください。

各findingには次を含めてください。

- `id`
- `location`
- `severity`: `high` / `medium` / `low`
- `description`
- `reason`
- `suggested_direction`
- `scope_anchors`

`scope_anchors` は問題が現れる箇所ごとに分け、各要素へ `id`、本文からそのまま抜き出した `exact_quote`、人が位置を確認するための `location_hint` を記録してください。コアイメージと詳細定義など複数箇所に同じ問題がある場合は、1つのlocationへまとめず、別々のanchorにしてください。target ID、relation ID、監査履歴、既知の指摘は与えられていないため推測しないでください。

記事本文は変更しないでください。


## Input packet

```json
{
  "stage": "cold_review",
  "entry_body": "\n＃発音記号\n\n米・英: /ɪnˈtens/。2音節で、第2音節の /tens/ に主強勢がある。  \n\n＃語源\n\n15世紀初頭に、フランス語を経てラテン語 intensus「引き伸ばされた、張り詰めた」から英語に入った。intensus は intendere の過去分詞に由来する。  \n\n現在の intense は、程度・力・感情などの強度や度合いが非常に高いことを表す。  \n\n＃語形成\n\n・intensity（名詞）— 強度、激しさ。  \n・intensify（動詞）— 強まる、強める。自動詞・他動詞の両方で使う。  \n・intensive（形容詞）— 集中的な、徹底的な。活動・訓練などの集中度・密度・徹底性が高いことを表し、限られた期間・範囲に集中する傾向もある。intense と活動用法で重なる場合があるが、intense は高い強度・活動量・速度・負荷などに、intensive は集中度・密度・徹底性に焦点を置きやすい。  \n・intensification（名詞）— 強化、激化。  \n\n＃コアイメージ\n\n程度・力・エネルギー・感情の強度や度合いが非常に高い。活動や行動では、その高強度が活動量・速度・忙しさ・負荷の大きさとして現れる。人・視線・表情・関係では、強い感情や態度、鋭さ、または強い相互作用として現れる。  \n\n・対象の程度・感覚・感情の強度が非常に高い → 「強烈な、非常に強い」（語義1）  \n・活動や行動の強度・活動量・速度・忙しさ・負荷が非常に高い → 「激しい、活動量の多い」（語義2）  \n・人が強い感情や態度を持つ／そうした印象を与える → 「感情や態度の強い」（語義3）  \n・視線・表情に鋭さや強い感情が感じられる → 「鋭い、強い」（語義3）  \n・関係の感情的な結びつきや相互作用が強い → 「張り詰めた、濃密な」（語義3）  \n\n＃意味・用法・関連表現\n\n1. 【形容詞・限定／叙述】強烈な、非常に強い\n\n【日本語訳・定義】感情、感覚、痛み、暑さ、色、関心、圧力などの程度・強度が非常に高いこと。intense pleasure「非常に強い喜び」のように、好ましい対象にも使う。  \n\n【頻度】〈6/10〉  \n\n※Oxford 5000ではC1レベル。〈6/10〉はコーパスに基づく全体頻度と辞書情報を参照した編集上の目安であり、語義別の厳密な順位ではない。  \n\n【レジスター/領域】一般語として使われる形容詞。  \n\n【文法パターン】intense + 〈感情・感覚・性質・熱・色などを表す名詞〉＝程度・強度が非常に高い～／intense energy・determination・concentration＝エネルギー・決意・集中の強度が非常に高い／under intense pressure/scrutiny＝強い圧力・厳しい監視・精査の下で  \n\n【コロケーション】\n\n・intense pain  \n用途: 身体的な痛みが非常に強いことを表す。  \n例: He felt intense pain in his lower back.  \n訳: 彼は腰の下部に激しい痛みを感じた。  \n\n・intense heat  \n用途: 暑さや熱が非常に強いことを表す。  \n例: The intense heat made it dangerous to work outside.  \n訳: 強烈な暑さのため、屋外で働くのは危険だった。  \n\n・intense pressure  \n用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  \n例: The new manager is under intense pressure to improve the results.  \n訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  \n\n・intense interest  \n用途: ある対象に向けられる関心が非常に強いことを表す。  \n例: The discovery attracted intense interest from researchers around the world.  \n訳: その発見は世界中の研究者から強い関心を集めた。  \n\n・intense anger  \n用途: 怒りの感情が非常に強いことを表す。  \n例: The decision provoked intense anger among local residents.  \n訳: その決定は地元住民の激しい怒りを引き起こした。  \n\n・intense blue  \n用途: 色の鮮やかさや彩度が際立ち、強い印象を与えることを表す。  \n例: The intense blue of the lake stood out against the white snow.  \n訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  \n\n【語法・注意】intense は感情、感覚、熱、色、関心、圧力など、強さの対象を表す名詞と結びつく。intense colour/blue では色の鮮やかさ・彩度、intense scrutiny では精査・吟味の厳しさも表す。extreme と重なる場合があるが、extreme は通常の範囲や限界からの逸脱、intense は経験される強さ・圧・力の高さに焦点を置きやすい。intense pleasure のような好ましい対象にも、intense pain や intense anger のような好ましくない対象にも使える。類義語欄の頻度スコアも、コーパス全体の頻度と辞書情報を参照した編集上の目安であり、各語義の厳密な順位ではない。  \n\n【類義語】\n\n・strong  \n定義: intense と同じく、力・程度・感情などが大きいことを表す基本語。  \n頻度: 〈8/10〉  \n違い: strong は幅広い強さを表し、intense は感覚・感情などの強度が非常に高いことに焦点を置く。  \n例: intense pain  \n訳: 強い痛み。  \n\n・extreme  \n定義: 通常の範囲や限界から大きく外れた状態を表す関連語。  \n頻度: 〈6/10〉  \n違い: extreme は通常の範囲や限界からの逸脱に焦点があり、intense は体感や感情の強さにも使う。  \n例: intense heat  \n訳: 強烈な暑さ。  \n\n・powerful  \n定義: 物理的・心理的な力や他者への影響が大きいことを表す関連語。  \n頻度: 〈6/10〉  \n違い: powerful は作用する力や影響力に焦点があり、intense は経験される強度や圧にも使う。  \n例: intense interest  \n訳: 強い関心。  \n\n2. 【形容詞・限定／叙述】激しい、活動量の多い\n\n【日本語訳・定義】活動・競争・議論・訓練などが高い強度で行われ、活動量・速度・忙しさ・負荷が大きいこと。強い努力や緊張を伴う場合もあるが、それらは必須ではない。短期集中を伴う場合にも使うが、短期間であることは必須ではない。  \n\n【頻度】〈5/10〉  \n\n※〈5/10〉はコーパスに基づく全体頻度と辞書情報を参照した編集上の目安であり、語義別の厳密な順位ではない。  \n\n【レジスター/領域】一般語として使われる形容詞。  \n\n【文法パターン】intense + 〈活動・競争・議論・訓練など〉＝高い強度で行われ、活動量・速度・忙しさ・負荷が大きい活動・競争など  \n\n【コロケーション】\n\n・intense competition  \n用途: 競争の強度や激しさが非常に高いことを表す。  \n例: There is intense competition for places at the top universities.  \n訳: 一流大学の枠をめぐって激しい競争がある。  \n\n・intense activity  \n用途: 活動の強度・活動量・速度・忙しさ・負荷が非常に高いことを表す。  \n例: The airport experienced a period of intense activity before the holiday.  \n訳: その空港では休暇前に活動が非常に活発な時期があった。  \n\n【語法・注意】intense は活動の強度・活動量・速度・忙しさ・負荷が高いことを表し、intensive は活動・訓練の集中度・密度・徹底性を表す傾向がある。intensive に期間・範囲の限定が伴うことは多いが必須ではなく、両語は活動用法で重なる場合がある。感情性・客観性だけを決め手にしない。類義語欄の頻度スコアは、コーパス全体の頻度と辞書情報を参照した編集上の目安である。  \n\n【類義語】\n\n・fierce  \n定義: 競争・対立・攻撃性などの激しさが非常に強いことを表す関連語。  \n頻度: 〈6/10〉  \n違い: fierce は攻撃性や対立を含みやすく、intense は敵意のない活動の強さにも使える。  \n例: intense competition  \n訳: 激しい競争。  \n\n・intensive  \n定義: 活動・訓練などを集中して行うことを表す関連語。  \n頻度: 〈6/10〉  \n違い: intensive は集中度・密度・徹底性を、intense は高い強度・活動量・速度・負荷を前面に出す。期間・範囲限定は intensive に伴う傾向だが必須ではない。  \n例: intensive training  \n訳: 集中的な訓練。  \n\n・concentrated  \n定義: 活動・注意・資源などが一箇所や短期間に集められた状態を表す関連語。  \n頻度: 〈5/10〉  \n違い: concentrated は集中配置や密度に焦点があり、intense は活動そのものの強度・活動量・速度・負荷に焦点を置く。  \n例: concentrated training  \n訳: 集中的な訓練。  \n\n3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた\n\n【日本語訳・定義】人については強い感情や態度を持つ、またはそうした印象を与えること、視線や表情については集中・鋭さ・強い感情が感じられること、関係については情緒的な結びつきや相互作用が強いことを表す。関係は緊張・衝突・不安定さを伴う場合もある。  \n\n【頻度】〈4/10〉  \n\n※〈4/10〉はコーパスに基づく全体頻度と辞書情報を参照した編集上の目安であり、語義別の厳密な順位ではない。  \n\n【レジスター/領域】一般語として使われる形容詞。  \n\n【文法パターン】an intense person＝強い感情や態度を持つ、またはそうした印象を与える人（評価は文脈依存）／an intense look/gaze＝集中・鋭さ・強い感情を帯びた視線／an intense relationship＝情緒的な結びつきや相互作用が強く、緊張や衝突を伴うこともある関係  \n\n【コロケーション】\n\n・an intense look  \n用途: 強い感情や集中を帯びた視線・表情を表す。  \n例: She gave him an intense look when he mentioned the accusation.  \n訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  \n\n・an intense person  \n用途: 感情や態度が強く、存在感や圧のある人を表す。肯定・否定の評価は文脈で変わる。  \n例: He is an intense person who takes every project very seriously.  \n訳: 彼はどのプロジェクトにも非常に真剣に取り組む、強い存在感のある人だ。  \n\n・an intense relationship  \n用途: 感情的な結びつきや相互作用が非常に強い関係を表す。必ずしも良好・安定とは限らない。  \n例: Their intense relationship left little room for emotional distance.  \n訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  \n\n【語法・注意】人への用法は強い感情や態度を持つ、またはそうした印象を与えるという評価で、必ず外に表出するとは限らない。視線・表情では集中・鋭さ・感情の表れ、relationship では情緒的な結びつきや相互作用の強さを表し、緊張・衝突・不安定さも含み得る。類義語欄の頻度スコアは、コーパス全体の頻度と辞書情報を参照した編集上の目安である。  \n\n【類義語】\n\n・passionate  \n定義: intense と同じく強い感情や関与を表すが、熱意や情熱を前面に出す関連語。  \n頻度: 〈5/10〉  \n違い: passionate は熱意・情熱や積極的な関与を含みやすく、intense は肯定・否定を問わず感情や態度の強さを表す。  \n例: a passionate advocate  \n訳: 熱心な擁護者。  \n\n・deep  \n定義: 感情・関係・結びつきなどの深さを表す関連語。  \n頻度: 〈8/10〉  \n違い: deep は内面の深さや持続する結びつきに焦点があり、intense はその場の強い感情や張り詰めた印象にも使う。  \n例: a deep emotional bond  \n訳: 深い感情的な結びつき。  \n\n・fervent  \n定義: 支持・願い・感情などの熱烈さを表す関連語。  \n頻度: 〈3/10〉  \n違い: fervent は熱意や支持の強さを肯定的に表しやすく、intense は人・視線・関係の張り詰めた印象など、より広い対象に使う。  \n例: fervent support  \n訳: 熱烈な支持。  ",
  "_output_metadata": {
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-intense-20260905T141130Z-ff81ed00",
    "context_id": "cold-intense-context-20260905T141130Z-ff81ed00",
    "input_body_sha256": "3a1ecd39179a54df37a738e19b1b01cfb3f4fc1ccfad52e3eed9dcbf378473a7",
    "prompt_sha256": "0ed4409a73095a9a2968bdcdb20bc397be345af84bff2c3558a48f08a5488aae",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false
  }
}
```
