# Independent review handoff

Stage: `final_review`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session.

## Prompt

# final_review_spec_v2

この仕様は、最新版の記事本文、全checker/cold/final-blind finding、全resolution、固定済みblind inventoryを入力として、第三者最終審査が合否を判断するための意味基準だけを定める。入力分離、順序、hash、seal、記録、件数網羅、status同期は `scripts/run_word.py` と `scripts/generate_audit_manifest.py` が強制する。

## PASSの意味基準

次をすべて満たす場合だけ `PASS` とする。

1. 記事の事実、語法、発音、例文、訳が正しく、見出し語の意味方向・意味役割・適用範囲を誤学習させない。
2. 主要な品詞、語義、派生・転換、専門用法、完全な統語フレームが過不足なく扱われ、語義境界、コアイメージ、定義、語法、コロケーション、語彙関係の間に矛盾がない。
3. 例文と訳で、述語、主語・目的語・補語、行為者・経験者・対象・結果、肯否、比較基準、程度、数量、時制・相・法、条件・因果・目的、修飾範囲、焦点、情報構造、レジスター、話者評価が保存されている。
4. 地域差、専門・制度用法、頻度、語源、語形成、語義境界、文法制約、絶対表現などの高リスク主張が、当該主張へ適用できる根拠に支えられ、反例・矛盾・適用範囲が確認されている。検索見出し、資料名だけ、別義の用例は根拠にしない。
5. 通常棚卸しとblind棚卸しの差、すべてのfinding、採否理由、修正結果、残存リスクを個別に吟味し、問題確認済みfindingが最新版の本文全体で解決され、正しい意味関係が別箇所で再び破られていない。
6. blind inventoryの各 `semantic_assertion` を最新版へ適用しても、候補の境界・作用方向・包含/除外関係・一般化範囲に反する記述がない。

## REJECTの意味基準

上記のいずれかを満たさない場合は `REJECT` とする。blockerにできるのは、事実・語法・発音の誤り、例文/訳の誤り、主要語義・構文の欠落または過剰収録、根拠と本文の矛盾、内容仕様の必須項目違反、未判定・未解決項目である。各blockerには対象ID、問題、必要な修正を記録する。条件付き合格は使わない。

本文と矛盾しない分類粒度・棚卸し構成の差、より良い表現の提案、任意の改善余地は、それだけを理由に `REJECT` にせず、非blocking noteとして記録する。`REJECT` は審査失敗ではなく、問題を検出して完了した正常な最終判定である。

## 出力

`final_review_v2` JSONとして、全target/relation/normal candidate/blind candidate/finding/evidence/source-unionの個別結果、`decision` (`pass | reject`)、`blockers`、非blocking `notes` を返す。`PASS` は全個別結果がpass、未解決・holdが0件、blockerが0件の場合に限る。本文は変更しない。


## Input packet

```json
{
  "stage": "final_review",
  "entry_body": "\n＃発音記号\n\n米・英: /ɪnˈtens/。2音節で、第2音節の /tens/ に主強勢がある。第1音節は弱めの /ɪn/ で、綴りの -tense は /tens/ と発音する。  \n\nintensive /ɪnˈtensɪv/ と発音の始まりは似ているが、intense は形容詞の語末が /ens/、intensive は /ɪv/ で終わる。  \n\n＃語源\n\n中英語期に、古フランス語 intense またはラテン語 intensus「きつく引き伸ばされた、張り詰めた、緊張した」から英語に入った。intensus は intendere「伸ばす、向ける、張る」の過去分詞で、in-「～へ」と tendere「伸ばす」に分解される。  \n\n現代英語では、そこから「程度・力・感情・活動が極端に強い」という意味が発達した。intend「意図する」も語源上は同じラテン語系統に属するが、現代の意味は intense の派生義として理解しない。  \n\n＃語形成\n\n・intensity（名詞）— 強度、激しさ。  \n・intensify（動詞）— 強まる、強める。自動詞・他動詞の両方で使う。  \n・intensely（副詞）— 激しく、強烈に。  \n・intensive（形容詞）— 集中的な、徹底的な。intense と重なる場合もあるが、客観的な密度・集中を表しやすい。  \n・intensification（名詞）— 強化、激化。  \n\n＃コアイメージ\n\n力・感情・注意が一点に強く集まり、圧や張りが大きい状態。  \n\n・対象の性質や感覚に強く現れる圧 → 「強烈な、非常に強い」（語義1）  \n・短時間に集中的に現れる行為の圧 → 「激しい、集中的な」（語義2）  \n・人や表情に現れる感情・意見の圧 → 「真剣で感情の強い、張り詰めた」（語義3）  \n\n＃意味・用法・関連表現\n\n1. 【形容詞・限定／叙述】強烈な、非常に強い\n\n【日本語訳・定義】感情、感覚、痛み、暑さ、光、色、関心、圧力などの程度が極端に強いこと。単に「強い」というより、対象にかかる力や感じられる圧が大きいことを表す。必ず不快・否定的とは限らず、intense pleasure「非常に強い喜び」のように好ましい対象にも使う。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準的な一般語。会話、ニュース、ビジネス、医学、スポーツ、文学などで広く使う。  \n\n【文法パターン】intense + 〈感情・感覚・性質を表す名詞〉＝非常に強い～／become/get/feel intense＝程度や感じ方が強くなる／under intense pressure/scrutiny＝強い圧力・厳しい監視の下で／intense + 〈色・光・熱など〉＝非常に鮮やかな・強烈な～  \n\n【コロケーション】\n\n・intense pain  \n用途: 身体的な痛みが非常に強いことを表す。  \n例: He felt intense pain in his lower back.  \n訳: 彼は腰の下部に激しい痛みを感じた。  \n\n・intense heat  \n用途: 暑さや熱が極端に強いことを表す。  \n例: The intense heat made it dangerous to work outside.  \n訳: 強烈な暑さのため、屋外で働くのは危険だった。  \n\n・intense pressure  \n用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  \n例: The new manager is under intense pressure to improve the results.  \n訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  \n\n・intense interest  \n用途: ある対象に向けられる関心が非常に強いことを表す。  \n例: The discovery attracted intense interest from researchers around the world.  \n訳: その発見は世界中の研究者から強い関心を集めた。  \n\n・intense anger  \n用途: 怒りの感情が非常に強いことを表す。  \n例: The decision provoked intense anger among local residents.  \n訳: その決定は地元住民の激しい怒りを引き起こした。  \n\n・intense blue  \n用途: 色が非常に鮮やかで、見る人に強い印象を与えることを表す。  \n例: The intense blue of the lake stood out against the white snow.  \n訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  \n\n【語法・注意】intense は程度の高さを表す形容詞で、対象が大きいことや量が多いことを表す語ではない。たとえば「雨が大量に降る」は heavy rain、「色が鮮やかで強い」は intense color のように、対象に応じて自然な語を選ぶ。intense pain/heat/interest のように、身体感覚・環境・感情のいずれにも使えるが、強さの対象を文脈から明確にする。  \n\n【類義語】\n\n・strong  \n定義: 力、程度、効果などが大きい。  \n頻度: 〈10/10〉  \n違い: strong は最も広い「強い」で、intense は感覚・感情・圧力などが極端で、張り詰めた感じを伴いやすい。  \n例: The coffee has a strong flavor.  \n訳: そのコーヒーは味が濃い。  \n\n・extreme  \n定義: 普通の範囲を超え、極端な。  \n頻度: 〈9/10〉  \n違い: extreme は程度が限界に近いことに焦点があり、intense のような体感的な圧や集中を必ずしも含まない。  \n例: The region experienced extreme temperatures last summer.  \n訳: その地域は昨夏、極端な気温に見舞われた。  \n\n・severe  \n定義: 被害、痛み、問題などが深刻で重い。  \n頻度: 〈8/10〉  \n違い: severe は悪影響や深刻さに焦点があり、intense は好ましい感情や色など、害のない強さにも使える。  \n例: The storm caused severe damage to the coast.  \n訳: その嵐は沿岸部に深刻な被害をもたらした。  \n\n・powerful  \n定義: 大きな力や効果を持つ。  \n頻度: 〈9/10〉  \n違い: powerful は作用する力・影響力に焦点があり、intense は経験される強度や圧に焦点がある。  \n例: The film presents a powerful image of life after the disaster.  \n訳: その映画は災害後の生活を力強い映像で描いている。  \n\n・acute  \n定義: 痛み、問題、感覚などが激しく、差し迫っている。  \n頻度: 〈7/10〉  \n違い: acute は特に痛み・不足・問題などの鋭さや深刻さを表す硬い語で、intense より対象が限定されやすい。  \n例: The shortage created an acute need for clean water.  \n訳: その不足により、きれいな水が緊急に必要になった。  \n\n・vivid  \n定義: 色、記憶、描写などが鮮明で強く印象に残る。  \n頻度: 〈7/10〉  \n違い: vivid は目立つ鮮明さや心に浮かぶ明瞭さに焦点があり、intense のように圧力や痛みの強さ全般を表さない。  \n例: She has a vivid memory of the accident.  \n訳: 彼女はその事故を鮮明に覚えている。  \n\n【反意語】\n\n・mild  \n定義: 程度が穏やかで、強すぎない。  \n頻度: 〈8/10〉  \n違い: mild は痛み、症状、天候、反応などの程度が低く穏やかなことを表し、intense と程度の軸で対立する。  \n例: She had only mild pain after the treatment.  \n訳: 治療後の痛みは軽いものだった。  \n\n・weak  \n定義: 力、効果、信号などが弱い。  \n頻度: 〈9/10〉  \n違い: weak は強さや作用が不足していることを表し、intense の極端な強さと反対方向にある。  \n例: The radio signal was too weak to hear clearly.  \n訳: その無線信号は弱すぎて、はっきり聞こえなかった。  \n\n・faint  \n定義: 光、音、色、においなどがかすかな。  \n頻度: 〈8/10〉  \n違い: faint は感覚刺激がほとんど感じ取れないほど弱いことに焦点があり、intense と特に光・色・音の強さで対立する。  \n例: A faint light was visible through the fog.  \n訳: 霧の中にかすかな光が見えた。  \n\n2. 【形容詞・限定／叙述】激しい、集中的な\n\n【日本語訳・定義】活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。対象の客観的な密度だけでなく、それに参加・直面する人が感じる圧や負荷を表すことがある。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】標準的な一般語。仕事、学習、スポーツ、政治、ニュースなどで広く使う。  \n\n【文法パターン】intense + 〈活動・競争・議論・努力〉＝激しい・集中した～／an intense period of 〈活動〉＝激しい～の期間／become/get intense＝活動や状況が激しくなる／intense + 〈活動〉 over 〈期間〉＝一定期間に集中して行われる激しい～  \n\n【コロケーション】\n\n・intense competition  \n用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。  \n例: There is intense competition for places at the top universities.  \n訳: 一流大学の枠をめぐって激しい競争がある。  \n\n・intense debate  \n用途: 議論が強い意見の対立や集中したやり取りを伴うことを表す。  \n例: The proposal led to intense debate in parliament.  \n訳: その提案は議会で激しい議論を引き起こした。  \n\n・intense activity  \n用途: 短期間に多くの活動が集中して行われることを表す。  \n例: The airport experienced a period of intense activity before the holiday.  \n訳: その空港では休暇前に活動が集中する時期があった。  \n\n・intense effort  \n用途: 目標達成のために大きな力と集中を注ぐ努力を表す。  \n例: The rescue required intense effort from everyone on the team.  \n訳: その救助にはチーム全員の大変な努力が必要だった。  \n\n・intense negotiations  \n用途: 短期間に意見を激しく交わし、妥結を目指す交渉を表す。  \n例: The two sides held intense negotiations throughout the night.  \n訳: 両陣営は一晩中、激しい交渉を続けた。  \n\n・intense training  \n用途: 参加者が大きな負荷や集中を感じる厳しい訓練を表す。  \n例: The athletes completed an intense training camp before the tournament.  \n訳: 選手たちは大会前に厳しい合宿を終えた。  \n\n【語法・注意】intense と intensive は、どちらも短期間に多くの活動や努力が集中する対象を修飾できる。intense は参加者が感じる厳しさ・圧・感情的な強さを含みやすく、intensive は計画や内容の密度を客観的に述べやすい。したがって intense training は訓練の負荷の大きさ、an intensive training course は短期間に内容を詰め込む制度・課程の性質に焦点がある。ただし、この区別は絶対的ではない。  \n\n【類義語】\n\n・fierce  \n定義: 競争、対立、議論などが非常に激しい。  \n頻度: 〈8/10〉  \n違い: fierce は攻撃性・対立・荒々しさを含みやすく、intense は敵意のない努力や活動の集中にも使える。  \n例: The teams are in fierce competition for the championship.  \n訳: そのチームたちは優勝をめぐって激しく競い合っている。  \n\n・vigorous  \n定義: 活動や努力が精力的で力強い。  \n頻度: 〈7/10〉  \n違い: vigorous は活力や積極的なエネルギーに焦点があり、intense のような緊張・負荷・心理的圧力を必ずしも含まない。  \n例: The proposal prompted vigorous discussion among the experts.  \n訳: その提案は専門家の間で活発な議論を促した。  \n\n・strenuous  \n定義: 身体的・精神的に大きな努力を要する。  \n頻度: 〈6/10〉  \n違い: strenuous は行為がきつく、多大な努力を要することに焦点があり、intense は活動の集中度や緊張感も表す。  \n例: The climbers faced a strenuous ascent in freezing weather.  \n訳: 登山者たちは極寒の中で厳しい登りに挑んだ。  \n\n・hectic  \n定義: 活動や予定が非常に多く、慌ただしい。  \n頻度: 〈8/10〉  \n違い: hectic は忙しさや混乱を含む時間の状態に焦点があり、intense のように競争・感情・議論の強さ全般を表さない。  \n例: It was a hectic week at the hospital.  \n訳: 病院では慌ただしい一週間だった。  \n\n・concentrated  \n定義: 力、資源、活動などが一箇所や短期間に集中的に向けられた。  \n頻度: 〈7/10〉  \n違い: concentrated は分散していない配置や客観的な集中に焦点があり、intense のような体感的な激しさを必ずしも含まない。  \n例: The program provides concentrated language practice over two weeks.  \n訳: そのプログラムは2週間にわたり集中的な語学練習を提供する。  \n\n・demanding  \n定義: 多くの時間、技術、努力を要求する。  \n頻度: 〈9/10〉  \n違い: demanding は参加者にとって負担が大きいことに焦点があり、活動自体の対立や感情の強さまでは示さない。  \n例: The job is demanding but rewarding.  \n訳: その仕事は大変だが、やりがいがある。  \n\n【反意語】\n\n・moderate  \n定義: 程度や強さが中程度の。  \n頻度: 〈8/10〉  \n違い: moderate は活動、負荷、競争などが極端ではないことを表し、intense と程度の軸で対立する。  \n例: Start with moderate exercise and increase the load gradually.  \n訳: 中程度の運動から始め、負荷を徐々に増やしなさい。  \n\n・light  \n定義: 仕事、運動、訓練などの負荷が小さい。  \n頻度: 〈9/10〉  \n違い: light は特に作業量や身体的負荷が少ないことを表し、intense の高い負荷と対立する。  \n例: The doctor recommended light exercise for the first week.  \n訳: 医師は最初の1週間、軽い運動を勧めた。  \n\n3. 【形容詞・人・表情・関係】真剣で感情の強い、張り詰めた\n\n【日本語訳・定義】人、視線、表情、会話、関係などが、非常に強い感情、意見、考え、目的意識を示すこと。真剣で集中しているという肯定的な意味にも、重い・圧が強い・感情的に負担が大きいという否定的な評価にもなり得る。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】標準的な一般語。人物描写、会話、職場、文学、映画・演劇の批評などで使う。  \n\n【文法パターン】an intense person＝感情や目的意識の強い人／an intense look/gaze/expression＝強い感情や集中を帯びた視線・表情／an intense conversation/relationship＝感情的な圧や結びつきの強い会話・関係／be intense about 〈事柄〉＝〈事柄〉に非常に熱心・真剣である／too intense＝人ややり取りが重すぎる、圧が強すぎる  \n\n【コロケーション】\n\n・an intense look  \n用途: 強い感情や集中を帯びた視線・表情を表す。  \n例: She gave him an intense look when he mentioned the accusation.  \n訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  \n\n・an intense person  \n用途: 感情、意見、目的意識などが強く、存在感や圧のある人を表す。  \n例: He is an intense person who takes every project very seriously.  \n訳: 彼はどのプロジェクトにも非常に真剣に取り組む、熱の強い人だ。  \n\n・be intense about 〈事柄〉  \n用途: ある事柄について強い意見や熱意を持ち、真剣にこだわることを表す。  \n例: She is intense about keeping every detail of the experiment accurate.  \n訳: 彼女は実験の細部をすべて正確に保つことに非常にこだわっている。  \n\n・an intense conversation  \n用途: 強い感情や重大な問題を伴う真剣な会話を表す。  \n例: We had an intense conversation about whether to end the relationship.  \n訳: 私たちはその関係を終わらせるべきかについて、感情のこもった真剣な話をした。  \n\n・an intense relationship  \n用途: 感情的な結びつきや相互作用が非常に強い関係を表す。  \n例: Their intense relationship left little room for emotional distance.  \n訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  \n\n・too intense  \n用途: 人、会話、関係などが重すぎたり、圧が強すぎたりすることを表す。  \n例: The first meeting felt too intense for a casual introduction.  \n訳: 最初の会合は、気軽な顔合わせにしては重すぎる感じがした。  \n\n【語法・注意】人に intense を使う場合は、単に serious「真面目な」や focused「集中した」と同じではない。強い感情や意見が外に表れ、相手に強い存在感・圧力を感じさせる含みがある。褒め言葉として passionate「情熱的な」に近くなることもあれば、too intense のように「重い、付き合うのが大変」という評価になることもある。an intense look は必ず怒りを意味せず、強い集中や関心だけでも成立する。  \n\n【類義語】\n\n・serious  \n定義: ふざけておらず、真剣な、または重大な。  \n頻度: 〈10/10〉  \n違い: serious は真面目さや重要性に焦点があり、intense のような強い感情の圧や相手に与える重さを必ずしも含まない。  \n例: She looked serious during the interview.  \n訳: 面接中、彼女は真剣な表情をしていた。  \n\n・passionate  \n定義: 人や活動に強い熱意・愛着を持つ。  \n頻度: 〈9/10〉  \n違い: passionate は熱意や好意を示す肯定的な語で、intense のように緊張感や重い圧を含むとは限らない。  \n例: He is passionate about improving access to education.  \n訳: 彼は教育へのアクセス改善に情熱を注いでいる。  \n\n・earnest  \n定義: 目的や発言が誠実で、真剣な。  \n頻度: 〈6/10〉  \n違い: earnest は誠実さ・真摯さに焦点があり、intense より感情の強さや対人的な圧が弱い。  \n例: She made an earnest appeal for help.  \n訳: 彼女は助けを求めて真摯に訴えた。  \n\n・focused  \n定義: 注意や努力の対象が明確で、集中している。  \n頻度: 〈9/10〉  \n違い: focused は注意が一点に定まっていることを表す中立的な語で、intense のような強い感情や重い雰囲気を必ずしも含まない。  \n例: The researcher remained focused on the data.  \n訳: その研究者はデータに集中し続けた。  \n\n・emotional  \n定義: 強い感情を示す、感情に動かされた。  \n頻度: 〈9/10〉  \n違い: emotional は感情が表に出ていることに焦点があり、intense のような強い目的意識や集中だけを表す場合には使えない。  \n例: His speech was emotional but carefully reasoned.  \n訳: 彼のスピーチは感情的だったが、論理的によく考えられていた。  \n\n・forceful  \n定義: 意見、表現、態度などが力強く、強い影響を与える。  \n頻度: 〈7/10〉  \n違い: forceful は外に表れた主張や表現の押し出しに焦点があり、intense の内面的な感情の深さまで含むとは限らない。  \n例: The lawyer gave a forceful argument in court.  \n訳: その弁護士は法廷で力強い主張を展開した。  \n\n【反意語】\n\n・casual  \n定義: 態度、会話、関係などが気軽で、形式張らない。  \n頻度: 〈10/10〉  \n違い: casual は深い感情的関与や張り詰めた圧が少ないことを表し、intense と対人的な雰囲気の軸で対立する。  \n例: We had a casual conversation over coffee.  \n訳: 私たちはコーヒーを飲みながら気軽な会話をした。  \n\n・relaxed  \n定義: 緊張や気負いがなく、落ち着いている。  \n頻度: 〈9/10〉  \n違い: relaxed は人、雰囲気、やり取りの力が抜けていることを表し、intense の張り詰めた圧と反対方向にある。  \n例: The interview became more relaxed after the first few questions.  \n訳: 最初の数問を過ぎると、面接はより和やかになった。  \n\n・detached  \n定義: 感情的に関与せず、距離を置いた。  \n頻度: 〈7/10〉  \n違い: detached は感情や個人的な関与を抑えていることを表し、intense の強い感情的関与と対立する。  \n例: He remained detached while discussing the breakup.  \n訳: 彼は別れについて話している間も、感情的に距離を置いていた。  ",
  "_output_metadata": {
    "schema_version": "final_review_v2",
    "stage": "final_review",
    "run_id": "blind-intense-20260904T160121Z-35cedac0",
    "context_id": "blind-intense-context-20260904T160121Z-35cedac0",
    "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
    "prompt_sha256": "3158e690b19b0f822a032dffa1cbfe1d38d64a0de2c1dba582554fa2b729f117",
    "input_artifacts": [
      "entry_body",
      "all_findings",
      "resolutions",
      "sealed_final_blind",
      "final_review_spec"
    ],
    "blind_output_sha256": "018c8602883832eab184d1258670bf5df8957963ed71f77409b3cafdbd16c50d"
  },
  "pass_findings": {
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-intense-20260904T160121Z-35cedac0",
    "context_id": "normal-intense-context-20260904T160121Z-35cedac0",
    "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
    "prompt_sha256": "5178f5a14a9525317811a34e6cd307108436f4babc1299fcd2eb9031f28ba737",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-09-04T16:52:52.562978+00:00",
    "pass_outputs": [
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "translation",
        "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a06d38-d628-7841-8e59-29308963a0b1"
        },
        "findings": [
          {
            "id": "normal-translation-001",
            "taxonomy_id": "example_translation_alignment",
            "location": {
              "section": "collocations_examples",
              "line_start": 278,
              "line_end": 278,
              "exact_quote": "訳: 彼はどのプロジェクトにも非常に真剣に取り組む、熱の強い人だ。"
            },
            "severity": "minor",
            "rationale": "「熱の強い人」は定着した日本語表現ではなく、物理的な熱や発熱の含意も生じ得るため、intense person の人物における強い感情・意欲・存在感を明確に表せていない。",
            "evidence_link_ids": [],
            "suggested_direction": "「熱意の強い人」「感情の強い人」「気迫のある人」など、人物の強い感情・意欲・存在感を表す表現に直す。"
          },
          {
            "id": "normal-translation-002",
            "taxonomy_id": "example_translation_alignment",
            "location": {
              "section": "lexical_relations",
              "line_start": 100,
              "line_end": 101,
              "exact_quote": "例: The region experienced extreme temperatures last summer.\n訳: その地域は昨夏、極端な気温に見舞われた。"
            },
            "severity": "blocking",
            "rationale": "experienced extreme temperatures は中立的な経験・観測を述べるだけだが、「見舞われた」はその地域が気温による被害や災難を受けたという否定的評価を加え、原文にない被害含意を生じさせている。",
            "evidence_link_ids": [],
            "suggested_direction": "「その地域では昨夏、極端な気温が観測された」または「その地域は昨夏、極端な気温を経験した」のように中立に訳す。"
          }
        ]
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "sense-structure",
        "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a06d38-db8e-7f13-a306-1332a3a1f0ac"
        },
        "findings": [],
        "records": [
          {
            "record_type": "masked_antonym_axis",
            "stage": 1,
            "status": "masked",
            "axis": "[MASKED]"
          }
        ]
      },
      {
        "pass_id": "frame-relation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a06d38-eb50-7b73-a126-1ec01be250b5"
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
          "blind_request_sha256": "bb7ac6fe828f9b6c609d2665f7e237e63afc7832e4e313208d36d064a9d38225",
          "recorded_at": "2026-09-04T16:22:00Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "01a06d38-eb50-7b73-a126-1ec01be250b5"
          },
          "axes": [
            {
              "item_id": "ant-af2cb1b9bd23",
              "axis": "関与",
              "relation_type": "状態",
              "reason": "強い感情や目的意識の示し方と、感情的に距離を置くことの対立。"
            },
            {
              "item_id": "ant-80779d1bfcd6",
              "axis": "真剣さ",
              "relation_type": "状態",
              "reason": "真剣で集中した態度と、気軽で形式張らない態度の対立。"
            },
            {
              "item_id": "ant-41690c7b43ad",
              "axis": "負荷",
              "relation_type": "程度",
              "reason": "短時間に必要な力や注意の大きさと、仕事や運動の小さな負荷の対立。"
            },
            {
              "item_id": "ant-f114c7dc9bc6",
              "axis": "強度",
              "relation_type": "程度",
              "reason": "感情や感覚などの力の大きさと、力や効果の弱さの対立。"
            },
            {
              "item_id": "ant-464499db347e",
              "axis": "強度",
              "relation_type": "程度",
              "reason": "対象の極端な強さと、穏やかで強すぎない程度の対立。"
            },
            {
              "item_id": "ant-1a4b697f8e4b",
              "axis": "強度",
              "relation_type": "程度",
              "reason": "活動に必要な力や注意の強さと、中程度の強さの対立。"
            },
            {
              "item_id": "ant-f870f7405e53",
              "axis": "緊張",
              "relation_type": "状態",
              "reason": "重く圧のある集中状態と、緊張や気負いのない落ち着いた状態の対立。"
            },
            {
              "item_id": "ant-06d30634b64f",
              "axis": "強度",
              "relation_type": "程度",
              "reason": "光や音などの強さと、かすかな強さの対立。"
            }
          ]
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
          "stage2_request_sha256": "0646203f1fc9897898e765c6478868c086b8ce2f6a28d51fa5c7672a120f6d79",
          "blind_record_sha256": "83807b503479733863986124a338274049a4caa16c19d3492b892fa6e4d75e04",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "01a06d38-eb50-7b73-a126-1ec01be250b5"
          },
          "aligned_at": "2026-09-04T16:23:00Z",
          "adjudications": [
            {
              "item_id": "ant-464499db347e",
              "flags": [],
              "rationale": "sense:001の定義が程度の極端な強さを直接示し、mildの穏やかさとの程度対立が違い行にも明記されている。F1〜F4なし。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-f114c7dc9bc6",
              "flags": [],
              "rationale": "sense:001の対象にかかる力や圧の大きさと、weakの力・作用の不足が同じ強度の程度軸で対応する。F1〜F4なし。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-06d30634b64f",
              "flags": [],
              "rationale": "sense:001の光や色などの強さと、faintの感覚刺激の弱さが同じ強度軸で対応し、違い行も対立を明記している。F1〜F4なし。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-1a4b697f8e4b",
              "flags": [],
              "rationale": "sense:002の活動・負荷の激しさに対し、moderateの中程度が同じ強度の程度軸で対応する。F1〜F4なし。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-41690c7b43ad",
              "flags": [],
              "rationale": "sense:002が参加者の圧や負荷を含む活動強度を定義し、lightの小さい作業・身体負荷が同じ負荷の程度軸で対応する。F1〜F4なし。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-80779d1bfcd6",
              "flags": [],
              "rationale": "sense:003の真剣さ・感情的圧力から真剣さの軸を導出でき、casualの気軽さとの対立を違い行が明記している。F1〜F4なし。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-f870f7405e53",
              "flags": [],
              "rationale": "sense:003の張り詰めた圧から緊張軸を導出でき、relaxedの緊張のない状態との対立が成立する。F1〜F4なし。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-af2cb1b9bd23",
              "flags": [],
              "rationale": "sense:003の強い感情や関係性から関与軸を導出でき、detachedの感情的距離との対立を違い行が明記している。F1〜F4なし。",
              "suggested_direction": null,
              "f4_severity": null
            }
          ],
          "frame_findings": [],
          "unrouted_observations": []
        },
        "aligned_at": "2026-09-04T16:59:51.746848+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a06d4c-2571-7c50-b875-ca487c86c08e"
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "pass_id": "example-attribution",
          "stage": 1,
          "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
          "blind_request_sha256": "edac8b06c708c78fa2d78a3fc9cd9ee5167264ccf72365a92b7dfb223046510c",
          "recorded_at": "2026-09-04T16:49:10Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "01a06d4c-2571-7c50-b875-ca487c86c08e"
          },
          "attributions": [
            {
              "example_id": "ex-f53769a5a6bc",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "competition"
              ],
              "rationale": "Competition is an activity whose fierceness is intensified; sense:001 concerns sensations or properties, and sense:003 concerns people or charged interpersonal expressions."
            },
            {
              "example_id": "ex-b28f6d7f1845",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "conversation"
              ],
              "rationale": "The conversation is emotionally serious and charged; this use emphasizes interpersonal and emotional force rather than intensive activity."
            },
            {
              "example_id": "ex-05fbd8b092d1",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "blue"
              ],
              "rationale": "Blue is a color whose perceptual strength is extreme; the other senses require activity or people and interpersonal expressions."
            },
            {
              "example_id": "ex-2e6814e0327b",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "training"
              ],
              "rationale": "Training is a concentrated activity demanding sustained effort; it is not a sensation or property being modified."
            },
            {
              "example_id": "ex-24587d18761a",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "emotional"
              ],
              "rationale": "The adjective characterizes the emotional closeness and pressure of an interpersonal bond, not activity intensity."
            },
            {
              "example_id": "ex-fe8446a73293",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "negotiations"
              ],
              "rationale": "Negotiations are a sustained activity involving concentrated effort; the sentence does not characterize a person's disposition or relationship."
            },
            {
              "example_id": "ex-eef6da74d93f",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "person"
              ],
              "rationale": "Intense directly characterizes the person's serious disposition; the project is only the topic of that disposition."
            },
            {
              "example_id": "ex-9aba6a848ed0",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "look"
              ],
              "rationale": "The look is a directed interpersonal expression of a strong reaction, not the strength of a visual property."
            },
            {
              "example_id": "ex-90020462b558",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "pain"
              ],
              "rationale": "Pain is the sensation whose degree is extreme; the other senses describe activities or people and interpersonal expressions."
            },
            {
              "example_id": "ex-7c4d2f6942d9",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "meeting"
              ],
              "rationale": "The meeting is socially and emotionally overcharged for an introduction; this emphasizes interpersonal pressure."
            },
            {
              "example_id": "ex-82a3302b23ce",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "effort"
              ],
              "rationale": "Effort is the activity or exertion requiring great force and attention, not a sensation or property."
            },
            {
              "example_id": "ex-ff0a1082d768",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "debate"
              ],
              "rationale": "Debate is a vigorous, demanding argumentative activity; the sentence describes discussion rather than a person's emotional expression."
            },
            {
              "example_id": "ex-6751dd691f7b",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "heat"
              ],
              "rationale": "Heat is a physical sensation or condition with extreme degree; the activity sense does not apply."
            },
            {
              "example_id": "ex-2a4f0bdbf31e",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "interest"
              ],
              "rationale": "Interest is the mental response whose strength is extreme; the other senses require activity or people and interpersonal expressions."
            },
            {
              "example_id": "ex-8fcafcf693f4",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "activity"
              ],
              "rationale": "Activity is explicitly concentrated in the period, matching a high density of actions rather than sensory or interpersonal intensity."
            },
            {
              "example_id": "ex-c9dfb6fde6ae",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "pressure"
              ],
              "rationale": "Pressure is the burden or force felt as extremely strong, explicitly covered by the first sense."
            },
            {
              "example_id": "ex-c44f7f9515a3",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "keeping"
              ],
              "rationale": "The predicate characterizes a serious, strongly purposeful attitude about keeping the details accurate; its object does not make the adjective an activity sense."
            },
            {
              "example_id": "ex-67d25c6bd763",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "anger"
              ],
              "rationale": "Anger is the emotion whose strength is extreme; the third sense characterizes a person or expression, not the emotion noun itself."
            }
          ],
          "findings": [],
          "records": []
        },
        "aligned_at": "2026-09-04T16:52:52.557975+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "qualification",
        "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a06d38-f0af-76a3-b732-755bbe16b0a1"
        },
        "findings": [
          {
            "id": "normal-qualification-001",
            "taxonomy_id": "absolute_scope_counterexample",
            "location": {
              "section": "sense_structure",
              "line_start": 45,
              "line_end": 45,
              "exact_quote": "【日本語訳・定義】感情、感覚、痛み、暑さ、光、色、関心、圧力などの程度が極端に強いこと。単に「強い」というより、対象にかかる力や感じられる圧が大きいことを表す。必ず不快・否定的とは限らず、intense pleasure「非常に強い喜び」のように好ましい対象にも使う。"
            },
            "severity": "minor",
            "rationale": "「対象にかかる力や感じられる圧」が中心的な条件のように読めるが、色・関心・喜びなどでは知覚的鮮明さや感情・関心の強度を表し、物理的・対人的な圧力を含まない場合がある。適用範囲が狭い。",
            "evidence_link_ids": [],
            "suggested_direction": "程度・感情・感覚・知覚的鮮明さなどの強さを中心義とし、力や圧力は一つの文脈例として限定する。"
          },
          {
            "id": "normal-qualification-002",
            "taxonomy_id": "regional_qualification",
            "location": {
              "section": "frequency_register",
              "line_start": 47,
              "line_end": 47,
              "exact_quote": "【頻度】〈9/10〉"
            },
            "severity": "minor",
            "rationale": "9/10の尺度、コーパス、期間、英語変種の範囲が示されず、英語全体での遭遇頻度なのか、項目内の相対順位や特定領域の頻度なのか判定できない。同形式の8/10・7/10にも同じ問題がある。",
            "evidence_link_ids": [],
            "suggested_direction": "英語全体を対象にした頻度基準またはコーパス範囲を明示し、根拠を示せない場合は「高頻度」などの定性的表現にする。"
          },
          {
            "id": "normal-qualification-003",
            "taxonomy_id": "absolute_scope_counterexample",
            "location": {
              "section": "usage_notes",
              "line_start": 85,
              "line_end": 85,
              "exact_quote": "【語法・注意】intense は程度の高さを表す形容詞で、対象が大きいことや量が多いことを表す語ではない。たとえば「雨が大量に降る」は heavy rain、「色が鮮やかで強い」は intense color のように、対象に応じて自然な語を選ぶ。"
            },
            "severity": "minor",
            "rationale": "「量が多いことを表す語ではない」という一括否定は強すぎる。intense rain/rainfallは降水の強度・降水率・勢いを表す用法として成立し、heavy rainが総量や一般的な言い換えとして好まれる場合があるという区別にすべきである。",
            "evidence_link_ids": [],
            "suggested_direction": "総量そのものとは同義でないと説明しつつ、降水率や物理的強度を表す intense rain/rainfall を排除しない。"
          },
          {
            "id": "normal-qualification-004",
            "taxonomy_id": "absolute_scope_counterexample",
            "location": {
              "section": "sense_structure",
              "line_start": 156,
              "line_end": 156,
              "exact_quote": "【日本語訳・定義】活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。"
            },
            "severity": "minor",
            "rationale": "「短い期間」と多くの行動・力・注意を必要とすることが定義上の条件のように置かれているが、intense competition、intense debate、intense activityなどは長期または持続的な状態の強度を表すこともあり、参加者の主観的負荷を必ず含まない。",
            "evidence_link_ids": [],
            "suggested_direction": "活動量、対立、努力、注意の投入などが非常に大きいという中心を示し、短期間への集中や参加者の負荷は典型的な傾向として限定する。"
          },
          {
            "id": "normal-qualification-005",
            "taxonomy_id": "regional_qualification",
            "location": {
              "section": "collocations_examples",
              "line_start": 280,
              "line_end": 280,
              "exact_quote": "・be intense about 〈事柄〉"
            },
            "severity": "minor",
            "rationale": "be intense aboutは成立し得るが、passionate aboutやserious aboutより頻度が低く、文脈によってはやや marked／口語的で「過度に真剣」という評価を帯びる。標準的な一般パターンとして無標で提示すると自然さを過大評価し得る。",
            "evidence_link_ids": [],
            "suggested_direction": "低頻度・口語的または評価的な用法であることを注記し、必要に応じてより一般的な代替表現やintense commitment toなどを併記する。"
          }
        ]
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "pronunciation",
        "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a06d38-e0b1-7692-9ff4-bb671eee00a8"
        },
        "findings": [
          {
            "id": "normal-pronunciation-001",
            "taxonomy_id": "pronunciation_symbol_explanation",
            "location": {
              "section": "pronunciation",
              "line_start": 17,
              "line_end": 17,
              "exact_quote": "intensive /ɪnˈtensɪv/ と発音の始まりは似ているが、intense は形容詞の語末が /ens/、intensive は /ɪv/ で終わる。  "
            },
            "severity": "blocking",
            "rationale": "intense の提示IPA /ɪnˈtens/ の語末は /tens/ であり、/ens/ ではない。説明が語末の /t/ を落としており、IPAと矛盾する。",
            "evidence_link_ids": [],
            "suggested_direction": "intense の語末を /tens/ に修正し、intensive の語末 /ɪv/ との差分として説明する。"
          }
        ],
        "records": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "evidence",
        "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a06d38-e5c8-7000-8cf3-29302d8440a8"
        },
        "status": "hold",
        "findings": [
          {
            "id": "normal-evidence-001",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "pronunciation",
              "line_start": 15,
              "line_end": 15,
              "exact_quote": "米・英: /ɪnˈtens/。2音節で、第2音節の /tens/ に主強勢がある。第1音節は弱めの /ɪn/ で、綴りの -tense は /tens/ と発音する。  "
            },
            "severity": "blocking",
            "rationale": "入力パケットには source inventory、fact、claim unit、evidence link ID、locator、反例・矛盾探索結果が含まれていないため、この発音主張への直接支持と適用範囲を確認できない。同じ欠落が全入力セクションに及ぶため、根拠対応の判定を完了できない。",
            "evidence_link_ids": [],
            "suggested_direction": "source-firstのsource inventory・fact・claim unitと、各主張に直接適用できるlocator付きevidence linkを補充するまでhold。"
          }
        ],
        "records": []
      }
    ],
    "checker_reviewers": {
      "translation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a06d38-d628-7841-8e59-29308963a0b1"
      },
      "sense-structure": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a06d38-db8e-7f13-a306-1332a3a1f0ac"
      },
      "frame-relation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a06d38-eb50-7b73-a126-1ec01be250b5"
      },
      "example-attribution": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a06d4c-2571-7c50-b875-ca487c86c08e"
      },
      "qualification": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a06d38-f0af-76a3-b732-755bbe16b0a1"
      },
      "pronunciation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a06d38-e0b1-7692-9ff4-bb671eee00a8"
      },
      "evidence": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a06d38-e5c8-7000-8cf3-29302d8440a8"
      }
    },
    "independent_candidates": [],
    "summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency."
  },
  "cold_review": {
    "summary": "語義3の欠落、語義境界の曖昧さ、intense と intensive の区別および「短期間・集中」への過度な限定がある。",
    "findings": [
      {
        "id": "f1",
        "location": "コアイメージと詳細語義の対応",
        "severity": "medium",
        "description": "コアイメージで語義3を提示しているが、詳細な語義3の節が存在しない。",
        "reason": "人・表情・態度に関する主要な用法が説明されず、記事内の構成も不一致になる。該当箇所: 「・人や表情に現れる感情・意見の圧 → 「真剣で感情の強い、張り詰めた」（語義3）」",
        "suggested_direction": "人・表情・態度に現れる強い感情や張り詰めた印象の語義を独立して追加する。",
        "scope_anchors": [
          {
            "id": "f1-a1",
            "exact_quote": "・人や表情に現れる感情・意見の圧 → 「真剣で感情の強い、張り詰めた」（語義3）",
            "location_hint": "＃コアイメージの第3項"
          },
          {
            "id": "f1-a2",
            "exact_quote": "2. 【形容詞・限定／叙述】激しい、集中的な",
            "location_hint": "＃意味・用法・関連表現の最後の詳細語義見出し。語義3の本文がない"
          }
        ]
      },
      {
        "id": "f2",
        "location": "コアイメージ・語義1の定義",
        "severity": "medium",
        "description": "intense の中心を「一点への集中」「圧」「張り」として描きすぎている。",
        "reason": "痛み、暑さ、色、喜びなどは、集中や圧力を伴わず単に程度・強度が非常に高い場合にも intense になるため、誤った一般化を招く。該当箇所: 「力・感情・注意が一点に強く集まり、圧や張りが大きい状態。」",
        "suggested_direction": "基本義を「程度・強度・感情の強さが非常に高い」とし、集中や張りは一部の文脈で生じる含意として扱う。",
        "scope_anchors": [
          {
            "id": "f2-a1",
            "exact_quote": "力・感情・注意が一点に強く集まり、圧や張りが大きい状態。",
            "location_hint": "＃コアイメージ冒頭"
          },
          {
            "id": "f2-a2",
            "exact_quote": "単に「強い」というより、対象にかかる力や感じられる圧が大きいことを表す。",
            "location_hint": "語義1の日本語訳・定義"
          }
        ]
      },
      {
        "id": "f3",
        "location": "語義2の定義・文法パターン・語法注意",
        "severity": "medium",
        "description": "語義2を短期間の集中や活動密度を必要条件のように説明している。",
        "reason": "intense competition、debate、effort などは長期間続いても激しさや緊張が高ければ intense であり、短期間性は必須ではない。intensive との境界も曖昧になる。該当箇所: 「活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。」",
        "suggested_direction": "活動・状況の強度、激しさ、負荷、緊張を中心に定義し、短期間の集中はよくある文脈にとどめる。",
        "scope_anchors": [
          {
            "id": "f3-a1",
            "exact_quote": "活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。",
            "location_hint": "語義2の日本語訳・定義"
          },
          {
            "id": "f3-a2",
            "exact_quote": "intense + 〈活動〉 over 〈期間〉＝一定期間に集中して行われる激しい～",
            "location_hint": "語義2の文法パターン"
          },
          {
            "id": "f3-a3",
            "exact_quote": "どちらも短期間に多くの活動や努力が集中する対象を修飾できる。",
            "location_hint": "語義2の語法・注意"
          }
        ]
      },
      {
        "id": "f4",
        "location": "intensive との比較",
        "severity": "medium",
        "description": "intense は主観的な負荷、intensive は客観的な密度という対比を強く打ち出しすぎている。",
        "reason": "両語の違いは傾向やコロケーションによることが多く、intense が客観的対象に使われたり、intensive が学習者に大きな負荷を与える内容を表したりするため、二分法では判断できない。該当箇所: 「intensive（形容詞）— 集中的な、徹底的な。intense と重なる場合もあるが、客観的な密度・集中を表しやすい。」",
        "suggested_direction": "主観／客観を必要条件とせず、強度・厳しさと、短期間に内容や活動を集中的に投入する性質という傾向として説明する。",
        "scope_anchors": [
          {
            "id": "f4-a1",
            "exact_quote": "intensive（形容詞）— 集中的な、徹底的な。intense と重なる場合もあるが、客観的な密度・集中を表しやすい。",
            "location_hint": "＃語形成の intensive の項目"
          },
          {
            "id": "f4-a2",
            "exact_quote": "intense は参加者が感じる厳しさ・圧・感情的な強さを含みやすく、intensive は計画や内容の密度を客観的に述べやすい。",
            "location_hint": "語義2の語法・注意"
          },
          {
            "id": "f4-a3",
            "exact_quote": "intense training は訓練の負荷の大きさ、an intensive training course は短期間に内容を詰め込む制度・課程の性質に焦点がある。",
            "location_hint": "語義2の語法・注意"
          }
        ]
      },
      {
        "id": "f5",
        "location": "語義1・語義2の境界",
        "severity": "medium",
        "description": "二つの語義がともに「程度・力・圧の強さ」を扱い、分類基準が十分に明示されていない。",
        "reason": "activity、debate、pressure、interest などは感情的強度・状況の圧力・活動の激しさの複数の読みが可能で、学習者が語義を使い分けにくい。該当箇所: 「intense + 〈感情・感覚・性質を表す名詞〉＝非常に強い～」",
        "suggested_direction": "一つの広い基本義にまとめて用法群を示すか、「経験される強度」と「活動・競争の激しさ」の境界を具体例付きで明示する。",
        "scope_anchors": [
          {
            "id": "f5-a1",
            "exact_quote": "intense + 〈感情・感覚・性質を表す名詞〉＝非常に強い～",
            "location_hint": "語義1の文法パターン"
          },
          {
            "id": "f5-a2",
            "exact_quote": "intense + 〈活動・競争・議論・努力〉＝激しい・集中した～",
            "location_hint": "語義2の文法パターン"
          },
          {
            "id": "f5-a3",
            "exact_quote": "短時間に集中的に現れる行為の圧 → 「激しい、集中的な」（語義2）",
            "location_hint": "＃コアイメージの第2項"
          }
        ]
      },
      {
        "id": "f6",
        "location": "語義1の語法・注意",
        "severity": "low",
        "description": "intense は量を表さないという断定が強すぎる。",
        "reason": "heavy rain が量の多さの標準表現である一方、intense rain／rainfall のように降雨の強度・率を表す用法もあり、量と強度を完全に切り離す説明は不正確。該当箇所: 「intense は程度の高さを表す形容詞で、対象が大きいことや量が多いことを表す語ではない。」",
        "suggested_direction": "「単純な大きさ・量より強度を表す」と弱め、heavy rain との違いを強度・降水量・率の観点で説明する。",
        "scope_anchors": [
          {
            "id": "f6-a1",
            "exact_quote": "intense は程度の高さを表す形容詞で、対象が大きいことや量が多いことを表す語ではない。",
            "location_hint": "語義1の語法・注意"
          }
        ]
      },
      {
        "id": "f7",
        "location": "語義2の intense negotiations",
        "severity": "low",
        "description": "intense negotiations の用途説明を、短期間の激しい意見交換に限定している。",
        "reason": "交渉の重要性、緊張、利害、困難さ、圧力によって intense になる場合もあり、必ず短期間または激しい応酬とは限らない。該当箇所: 「用途: 短期間に意見を激しく交わし、妥結を目指す交渉を表す。」",
        "suggested_direction": "高い緊張・利害・困難さを伴う交渉という広い説明にする。",
        "scope_anchors": [
          {
            "id": "f7-a1",
            "exact_quote": "用途: 短期間に意見を激しく交わし、妥結を目指す交渉を表す。",
            "location_hint": "語義2のコロケーション intense negotiations"
          }
        ]
      }
    ],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "01a06d61-5d36-7b00-85b3-65adc613308d"
    },
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-intense-20260904T160121Z-35cedac0",
    "context_id": "cold-intense-context-20260904T160121Z-35cedac0",
    "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
    "prompt_sha256": "0ed4409a73095a9a2968bdcdb20bc397be345af84bff2c3558a48f08a5488aae",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-04T17:12:38.123090+00:00"
  },
  "final_blind": {
    "provisional_decision": "reject",
    "independent_candidates": [
      {
        "id": "candidate_1",
        "surface_form": "intense",
        "frame": "intense + pain, heat, light, colorなど",
        "meaning": "感覚・物理的性質の程度や強度が極端に高い",
        "disposition": "included",
        "rationale": "語義1と例文がこの用法を明示している。対象フレーム: intense + pain, heat, light, colorなど",
        "semantic_assertions": [
          {
            "id": "candidate_1_assertion_1",
            "statement": "強度の高さを表し、単純な量や大きさの多さを必須条件としない。",
            "polarity": "must_hold",
            "scope": "感覚・物理的性質名詞"
          }
        ]
      },
      {
        "id": "candidate_2",
        "surface_form": "intense",
        "frame": "intense + interest, anger, pleasureなど",
        "meaning": "感情・関心・心理状態が非常に強い",
        "disposition": "included",
        "rationale": "肯定的・否定的な感情の双方を含めて語義1に記載されている。対象フレーム: intense + interest, anger, pleasureなど",
        "semantic_assertions": [
          {
            "id": "candidate_2_assertion_1",
            "statement": "感情または関心の強度が高いことを表し、不快・否定的な対象に限定されない。",
            "polarity": "must_hold",
            "scope": "感情・関心名詞"
          }
        ]
      },
      {
        "id": "candidate_3",
        "surface_form": "intense",
        "frame": "under intense pressure/scrutiny",
        "meaning": "非常に強い圧力または厳しい監視・精査",
        "disposition": "included",
        "rationale": "語義1の文法パターンとして明示されている。対象フレーム: under intense pressure/scrutiny",
        "semantic_assertions": [
          {
            "id": "candidate_3_assertion_1",
            "statement": "対象に作用する圧力が強い、または対象への監視・精査が非常に厳しい。",
            "polarity": "must_hold",
            "scope": "under + intense + pressure/scrutiny"
          }
        ]
      },
      {
        "id": "candidate_4",
        "surface_form": "intense",
        "frame": "intense + competition, debate, negotiations",
        "meaning": "競争・議論・交渉が激しく緊張度の高い",
        "disposition": "included",
        "rationale": "語義2の活動・相互作用用法として例示されている。対象フレーム: intense + competition, debate, negotiations",
        "semantic_assertions": [
          {
            "id": "candidate_4_assertion_1",
            "statement": "相互作用に通常以上の対立・力・緊張または集中したやり取りがある。",
            "polarity": "must_hold",
            "scope": "競争・議論・交渉"
          }
        ]
      },
      {
        "id": "candidate_5",
        "surface_form": "intense",
        "frame": "intense + activity, effort, training",
        "meaning": "活動・努力・訓練が非常に激しく負荷が大きい",
        "disposition": "included",
        "rationale": "語義2の定義とコロケーションがこの用法をカバーしている。対象フレーム: intense + activity, effort, training",
        "semantic_assertions": [
          {
            "id": "candidate_5_assertion_1",
            "statement": "活動や努力のエネルギー・負荷・要求水準が高く、短期間であること自体は必要条件ではない。",
            "polarity": "must_hold",
            "scope": "活動・努力・訓練"
          }
        ]
      },
      {
        "id": "candidate_6",
        "surface_form": "intense",
        "frame": "an intense person; be intense about X",
        "meaning": "強い感情・意見・目的意識を示し、存在感や圧のある人・態度",
        "disposition": "included",
        "rationale": "語義3の人物・態度用法として記載されている。対象フレーム: an intense person; be intense about X",
        "semantic_assertions": [
          {
            "id": "candidate_6_assertion_1",
            "statement": "人またはその態度が強い感情・意見・目的意識を示し、単なる真面目さだけに還元されない。",
            "polarity": "must_hold",
            "scope": "人物・態度"
          }
        ]
      },
      {
        "id": "candidate_7",
        "surface_form": "intense",
        "frame": "an intense look/gaze/expression",
        "meaning": "強い感情または集中を帯びた視線・表情",
        "disposition": "included",
        "rationale": "語義3の視線・表情用法と例文がある。対象フレーム: an intense look/gaze/expression",
        "semantic_assertions": [
          {
            "id": "candidate_7_assertion_1",
            "statement": "視線または表情が強い感情・集中を伝えるが、怒りだけを意味しない。",
            "polarity": "must_hold",
            "scope": "look/gaze/expression"
          }
        ]
      },
      {
        "id": "candidate_8",
        "surface_form": "intense",
        "frame": "an intense conversation",
        "meaning": "感情的または重大な問題を伴う、張り詰めた会話",
        "disposition": "included",
        "rationale": "語義3に明示され、関係の終了をめぐる例文で具体化されている。対象フレーム: an intense conversation",
        "semantic_assertions": [
          {
            "id": "candidate_8_assertion_1",
            "statement": "会話に強い感情・重大な利害または心理的緊張があり、単なる長さや発話量を意味しない。",
            "polarity": "must_hold",
            "scope": "conversation"
          }
        ]
      },
      {
        "id": "candidate_9",
        "surface_form": "intense",
        "frame": "an intense relationship",
        "meaning": "感情的な結びつきや相互作用が非常に強い関係",
        "disposition": "included",
        "rationale": "語義3に明示され、感情的距離の少なさとして説明されている。対象フレーム: an intense relationship",
        "semantic_assertions": [
          {
            "id": "candidate_9_assertion_1",
            "statement": "関係の感情的関与または相互作用の強さが高い。",
            "polarity": "must_hold",
            "scope": "relationship"
          }
        ]
      },
      {
        "id": "candidate_10",
        "surface_form": "intense",
        "frame": "too intense（人・会話・関係）",
        "meaning": "対人的な圧や感情的負荷が強すぎる",
        "disposition": "included",
        "rationale": "語義3の評価的な用法として例文がある。対象フレーム: too intense（人・会話・関係）",
        "semantic_assertions": [
          {
            "id": "candidate_10_assertion_1",
            "statement": "文脈上、人物または対人的相互作用が受け手にとって過度に重く、圧が強い。",
            "polarity": "must_hold",
            "scope": "too intense"
          }
        ]
      },
      {
        "id": "candidate_11",
        "surface_form": "intense",
        "frame": "objective short-duration concentration as a strict synonym of intensive",
        "meaning": "客観的密度・短時間集中だけを表す用法",
        "disposition": "excluded",
        "rationale": "intenseとintensiveの重なりは説明されるが、厳密な同義語とは扱われていない。",
        "semantic_assertions": [
          {
            "id": "candidate_11_assertion_1",
            "statement": "intenseは短期間または客観的密度を必須とするintensiveの完全な同義語であってはならない。",
            "polarity": "must_not_hold",
            "scope": "intense/intensive distinction"
          }
        ]
      },
      {
        "id": "candidate_12",
        "surface_form": "intense",
        "frame": "noun, verb, or adverb use",
        "meaning": "形容詞以外の主要品詞用法",
        "disposition": "excluded",
        "rationale": "本文は標準的な形容詞としてのみ扱っている。対象フレーム: noun, verb, or adverb use",
        "semantic_assertions": [
          {
            "id": "candidate_12_assertion_1",
            "statement": "標準的な見出し語用法を名詞・動詞・副詞として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "品詞"
          }
        ]
      }
    ],
    "article_findings": [
      {
        "id": "finding_1",
        "taxonomy_id": "pronunciation_symbol_explanation",
        "location": {
          "section": "発音記号 > intensiveとの比較",
          "line_start": 6,
          "line_end": 6,
          "exact_quote": "intense は形容詞の語末が /ens/、intensive は /ɪv/ で終わる。"
        },
        "severity": "minor",
        "rationale": "本文前半はintenseの第2音節を /tens/ と正しく示す一方、後半でintenseの語末を /ens/ としており、/t/を欠く誤記かつ内部矛盾になっている。該当箇所: 「intense は形容詞の語末が /ens/、intensive は /ɪv/ で終わる。」"
      },
      {
        "id": "finding_2",
        "taxonomy_id": "absolute_scope_counterexample",
        "location": {
          "section": "語義2 > 日本語訳・定義",
          "line_start": 145,
          "line_end": 145,
          "exact_quote": "【日本語訳・定義】活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。対象の客観的な密度だけでなく、それに参加・直面する人が感じる圧や負荷を表すことがある。"
        },
        "severity": "blocking",
        "rationale": "intense activity/effort/trainingを短期間に多くの行動が集中する用法として狭く定義しているが、intenseは活動の力・負荷・緊張の高さを表し、短い期間や客観的密度は必要条件ではない。該当箇所: 「【日本語訳・定義】活動、競争、議論、努力、訓練などが、短い期間に多くの行動・力・注意を必要とするほど激しいこと。対象の客観的な密度だけでなく、それに参加・直面する人が感じる圧や負荷を表すことがある。」"
      },
      {
        "id": "finding_3",
        "taxonomy_id": "sense_boundary_overlap",
        "location": {
          "section": "語義3 > 文法パターン",
          "line_start": 255,
          "line_end": 255,
          "exact_quote": "an intense conversation/relationship＝感情的な圧や結びつきの強い会話・関係"
        },
        "severity": "blocking",
        "rationale": "an intense conversationは感情的で重大な会話という語義3にも、激しい議論・相互作用という語義2にも自然に適合する。本文はこのフレームを語義3だけに置き、別義としての境界または文脈差を明示していない。該当箇所: 「an intense conversation/relationship＝感情的な圧や結びつきの強い会話・関係」"
      }
    ],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "01a06d68-e815-78a1-a11b-74e1925c5084"
    },
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-intense-20260904T160121Z-35cedac0",
    "context_id": "blind-intense-context-20260904T160121Z-35cedac0",
    "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
    "prompt_sha256": "1bb7b1a1c7f589a50a704d1ce6c1ecd0bfb1c9fb689fd481d21bf608438eb7b5",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-04T17:24:24.299529+00:00"
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/i/intense.md",
    "body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
    "final_blind_path": "audits/runs/i/intense/20260904T160121Z-35cedac0/final_blind.json",
    "final_blind_sha256": "28e24ce968b9c15d3ad39215afdd6bc2914a41f2bf2445534ab970d758bd7925",
    "blind_output_sha256": "018c8602883832eab184d1258670bf5df8957963ed71f77409b3cafdbd16c50d",
    "sealed_at": "2026-09-05T02:24:30.732178+09:00"
  },
  "resolutions": {
    "schema_version": "resolutions_v1",
    "stage": "finding_resolution",
    "run_id": "resolution-intense-20260904T160121Z-35cedac0",
    "context_id": "resolution-intense-context-20260904T160121Z-35cedac0",
    "input_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315",
    "prompt_sha256": "04ab1fe768a576a6f376dbb82c98e96d9d3cf1938ad860af031a5ca86538b86d",
    "recorded_at": "2026-09-05T02:30:00+09:00",
    "input_artifacts": [
      "entry_body",
      "all_findings"
    ],
    "resolutions": [
      {
        "id": "normal-translation-001",
        "finding_id": "normal-translation-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。人物の強い感情・意欲を表す訳へ修正する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "normal-translation-002",
        "finding_id": "normal-translation-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。原文にない被害評価を加えない中立的な訳へ修正する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "normal-qualification-001",
        "finding_id": "normal-qualification-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。中心義を程度・強度の高さとして明示し、圧力を一例に限定する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "normal-qualification-002",
        "finding_id": "normal-qualification-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。10段階表示が編集上の目安であることを明記する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "normal-qualification-003",
        "finding_id": "normal-qualification-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。総量と降水の強度・率を区別する説明へ修正する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "normal-qualification-004",
        "finding_id": "normal-qualification-004",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。活動の強度を中心にし、短期間性と参加者の主観的負荷を必要条件から外す。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "normal-qualification-005",
        "finding_id": "normal-qualification-005",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。be intense about を低頻度・評価的な用法として注記する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "normal-pronunciation-001",
        "finding_id": "normal-pronunciation-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。語末の説明を /tens/ に修正する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "normal-evidence-001",
        "finding_id": "normal-evidence-001",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "棄却。これは本文内容ではなく、証拠パスケットへsource inventoryが追加される前の確認可能性に関する指摘であり、同一runのsource inventoryとevidence linkを最終審査で確認できる。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "f1",
        "finding_id": "f1",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "棄却。入力本文には語義3の詳細節、定義、例文、語法、語彙関係が実際に存在し、指摘の前提が本文全体と一致しない。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "f2",
        "finding_id": "f2",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。コアイメージと語義1の定義を、集中や圧力を必須としない強度中心の説明へ修正する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "f3",
        "finding_id": "f3",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。語義2では活動の強度・負荷を中心にし、短期間性を典型例に限定する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "f4",
        "finding_id": "f4",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。intense/intensiveの差を必要条件ではなく傾向とコロケーションの違いとして説明する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "f5",
        "finding_id": "f5",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。語義1と語義2の共通する強度と、対象領域による用法差を明示する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "f6",
        "finding_id": "f6",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。雨の総量と降水強度・率を区別する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "f7",
        "finding_id": "f7",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。intense negotiationsを短期間性に限定せず、緊張・利害・困難さを含む説明へ修正する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "finding_1",
        "finding_id": "finding_1",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。intenseの語末表記を /tens/ に修正する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "finding_2",
        "finding_id": "finding_2",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。活動用法の定義から短期間性を必要条件として読める表現を除く。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      },
      {
        "id": "finding_3",
        "finding_id": "finding_3",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用。conversationを活動・相互作用用法と人物・関係用法の両方から判断できるよう文脈差を明示する。",
        "resolved_body_sha256": "5ba75d0fe18b071aca651e357d6042fee5605d5781140b398381ab1b004c8315"
      }
    ]
  }
}
```
