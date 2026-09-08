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

出力契約: `reason` には、そのfindingの `scope_anchors[].exact_quote` の少なくとも1つを全文そのまま含め、その引用がなぜ問題なのかを具体的に説明してください。引用欄だけに引用を置いた応答は取り込めません。指摘ごとの理由を使い回さないでください。


## Input packet

```json
{
  "stage": "cold_review",
  "entry_body": "\n＃発音記号\n\n米: /mæɡˈnɪfəsənt/｜英: /mæɡˈnɪfɪsənt/。4音節で、第2音節に主強勢がある。米語では第3音節の母音が /ə/、英語では /ɪ/ と表記されることが多い。語末の `-cent` は /sent/ ではなく弱く /sənt/ と発音する。  \n\n＃語源\n\n中英語期に古フランス語 `magnificent` またはラテン語 `magnificent-` を経て入り、ラテン語 `magnificus`「偉大なことを行う、壮麗な」にさかのぼる。`magnus`「大きい、偉大な」と `facere`「作る、行う」に関係し、もともとの「偉大なことを行う」という評価が、現在の「壮麗な」「すばらしい」につながっている。`magnitude`「大きさ、重大さ」や `magnify`「拡大する、誇張する」は同じ `magn-` の語族である。  \n\n＃語形成\n\n・`magnificence`（名詞）— 壮麗さ、すばらしさ。建物・景観などの威容にも、行為・成果のすばらしさにも使う。  \n・`magnificently`（副詞）— 壮麗に、見事に、すばらしく。`perform magnificently`「見事に演じる」のように動作の出来も評価する。  \n\n＃意味・用法・関連表現\n\n1. 【形容詞・限定／叙述】壮麗な、非常に美しく印象的な\n\n【日本語訳・定義】建物、景色、部屋、衣装、動物などが、規模、美しさ、豪華さ、威厳によって見る人に強い感銘を与えることを表す。単に大きいだけでなく、目を見張るほど見事だという肯定的評価を含む。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】標準語。日常会話、旅行・芸術・建築の描写、報道、文学的な文章まで広く使う。`beautiful` より評価が強く、やや高揚した響きを持つことがある。  \n\n【文法パターン】`a magnificent + 〈建物・景色・物〉`＝壮麗な～／`〈建物・景色・物〉 + be/look/seem magnificent`＝～が壮麗である・壮麗に見える／`a magnificent view of 〈場所・景色〉`＝〈場所・景色〉のすばらしい眺め  \n\n【コロケーション】\n\n・`a magnificent building/palace`  \n用途: 規模、美しさ、威厳によって強い印象を与える建築物を表す。  \n例: The restored palace is a magnificent example of eighteenth-century architecture.  \n訳: 修復されたその宮殿は、18世紀建築の壮麗な一例である。  \n\n・`a magnificent view of 〈場所・景色〉`  \n用途: 広がりや美しさが際立ち、見る人を感動させる眺めを表す。  \n例: From the terrace, we had a magnificent view of the snow-covered mountains.  \n訳: テラスからは、雪に覆われた山々のすばらしい眺めが広がっていた。  \n\n・`a magnificent 〈animal/bird〉`  \n用途: 動物の大きさ、美しさ、威厳のある姿を称賛する。  \n例: A magnificent eagle circled above the valley.  \n訳: 一羽の堂々たるワシが谷の上空を旋回していた。  \n\n・`look magnificent in 〈服・色〉`  \n用途: ある服装や色によって、人が非常に美しく堂々として見えることを表す。  \n例: She looked magnificent in the deep blue gown.  \n訳: 彼女は濃い青のドレスをまとい、実に華やかで堂々として見えた。  \n\n・`a magnificent interior/display`  \n用途: 室内装飾や展示が豪華で、視覚的に強い感銘を与えることを表す。  \n例: Visitors stopped to admire the cathedral's magnificent interior.  \n訳: 来訪者たちは足を止めて、その大聖堂の壮麗な内部を眺めた。  \n\n【語法・注意】`magnificent` は限定用法にも叙述用法にも使える。外観について使うと、「きれいな」だけでなく、規模、豪華さ、威厳などが生む強い感銘まで表す。人に使う場合、`She looks magnificent.` のように外見を称賛できるが、`a magnificent person` は文脈により語義2の人格・力量への高い評価にもなる。比較変化は文法上可能だが、通常は `more/most magnificent` を用い、絶対的な称賛として原級で使うことも多い。  \n\n【類義語】\n\n・splendid  \n定義: 見た目、質、成果などが非常にすばらしく、称賛に値する。  \n頻度: 〈7/10〉  \n違い: `splendid` は外観にも出来にも広く使える。`magnificent` は特に壮大さ、豪華さ、強い感銘を伴いやすい。  \n例: The hall was decorated with splendid tapestries.  \n訳: その広間は見事なタペストリーで飾られていた。  \n\n・majestic  \n定義: 王侯のような威厳や堂々とした壮大さを感じさせる。  \n頻度: 〈6/10〉  \n違い: `majestic` は威厳と堂々とした姿に焦点を置く。`magnificent` は威厳がなくても豪華さや美しさによる感銘を表せる。  \n例: We watched the majestic mountains turn red at sunset.  \n訳: 私たちは雄大な山々が夕日に赤く染まるのを眺めた。  \n\n・grand  \n定義: 規模、設計、外観が大きく立派で、重要さや格式を感じさせる。  \n頻度: 〈8/10〉  \n違い: `grand` は規模や格式を中心に表し、ときに誇張された大げささも含む。`magnificent` は話者の強い称賛をより直接に示す。  \n例: A grand staircase led to the reception rooms.  \n訳: 壮大な階段が応接室へと続いていた。  \n\n・glorious  \n定義: 美しさ、輝かしさ、喜ばしさによって非常にすばらしい。  \n頻度: 〈7/10〉  \n違い: `glorious` は光、色、天候などの輝かしさや、体験の喜びを表しやすい。`magnificent` は建物や景観の規模・威容にも強く結びつく。  \n例: The garden was filled with glorious autumn colors.  \n訳: 庭は見事な秋の色彩で満ちていた。  \n\n【反意語】\n\n・unimpressive  \n定義: 特に感銘を与えず、目立った美点や迫力がない。  \n頻度: 〈6/10〉  \n違い: 見る人に与える印象の強さという軸で、`magnificent` が非常に強い肯定的な感銘を表すのに対し、`unimpressive` は感銘を与えないことを表す。  \n例: The building's plain exterior was rather unimpressive.  \n訳: その建物の簡素な外観は、あまり印象的ではなかった。  \n\n・plain  \n定義: 装飾や華やかさがなく、簡素な。  \n頻度: 〈8/10〉  \n違い: 豪華さ・華やかさという限定された軸で対照をなす。`plain` は必ずしも質が悪いという否定的評価を含まず、`magnificent` の全面的な反対語ではない。  \n例: The chapel has a plain wooden interior.  \n訳: その礼拝堂の内部は簡素な木造である。  \n\n2. 【形容詞・限定／叙述】すばらしい、見事な、極めて優れた\n\n【日本語訳・定義】成果、演技、仕事、行為、機会、出来事などの質や価値が非常に高く、強く称賛したくなることを表す。外見の壮麗さを必要とせず、能力、出来、効果、経験の満足度などを高く評価する。単独の `Magnificent!` は「見事だ」「すばらしい」という感嘆になる。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】標準語。やや強く高揚した称賛で、会話、批評、スポーツ、報道などに使う。日常会話では `great` や `excellent` のほうが中立的で頻繁である。  \n\n【文法パターン】`a magnificent + 〈成果・演技・仕事・機会〉`＝すばらしい～／`〈成果・演技・仕事〉 + be/seem magnificent`＝～が見事である／`do/play/perform magnificently`＝見事に行う・演じる／`Magnificent!`＝見事だ・すばらしい  \n\n【コロケーション】\n\n・`a magnificent achievement`  \n用途: 困難さや規模を踏まえて、成果を非常に高く評価する。  \n例: Completing the bridge ahead of schedule was a magnificent achievement.  \n訳: 予定より早く橋を完成させたことは、見事な偉業だった。  \n\n・`a magnificent performance`  \n用途: 演技、演奏、競技などの出来が極めて優れていることを表す。  \n例: The violinist gave a magnificent performance in the final movement.  \n訳: そのバイオリニストは最終楽章で見事な演奏を披露した。  \n\n・`do a magnificent job`  \n用途: 人や組織が仕事を非常にうまく成し遂げたことを称賛する。  \n例: The rescue team did a magnificent job under dangerous conditions.  \n訳: 救助隊は危険な状況下で実に見事な働きをした。  \n\n・`a magnificent opportunity`  \n用途: 価値や可能性が非常に大きい機会を強く肯定的に評価する。  \n例: The scholarship gave her a magnificent opportunity to study abroad.  \n訳: その奨学金は、彼女に留学するすばらしい機会を与えた。  \n\n・`feel magnificent`  \n用途: 心身の調子が非常によく、気分がすばらしいことを表す。  \n例: After a full night's sleep, I felt magnificent.  \n訳: 一晩ぐっすり眠った後、私は最高の気分だった。  \n\n・`Magnificent!`  \n用途: 出来事、成果、演技などに対する強い称賛を単独で表す。  \n例: “We finished the repairs.” “Magnificent! We can reopen tomorrow.”  \n訳: 「修理が終わりました」「すばらしい！ 明日には再開できる」  \n\n【語法・注意】語義2では、対象の外観ではなく質・出来・価値を評価する。`a magnificent performance` は演技や演奏が非常に優れていたという意味であり、必ずしも豪華な舞台だったという意味ではない。`feel magnificent` は「堂々として感じる」ではなく「気分・体調が最高だ」という読みになる。`magnificent` は強い称賛なので、日常の小さな良さに使うと意図的に大げさ、ユーモラス、または熱のこもった響きになることがある。  \n\n【類義語】\n\n・excellent  \n定義: 質、能力、出来が非常に高い。  \n頻度: 〈9/10〉  \n違い: `excellent` は評価基準に照らして質が高いことを比較的中立に述べる。`magnificent` は話者の感動や熱烈な称賛を強く表す。  \n例: She submitted an excellent final report.  \n訳: 彼女は非常に優れた最終報告書を提出した。  \n\n・superb  \n定義: 質や出来が最高水準である。  \n頻度: 〈7/10〉  \n違い: `superb` は洗練された出来や卓越した質に焦点を置く。`magnificent` は質に加えて規模や感銘の大きさを含みやすい。  \n例: The chef prepared a superb meal using local ingredients.  \n訳: その料理人は地元の食材で最高の料理を用意した。  \n\n・outstanding  \n定義: 同種のものの中で際立って優れている。  \n頻度: 〈8/10〉  \n違い: `outstanding` は比較集団の中で抜きん出ていることを示す。`magnificent` は比較対象を明示せず、強い感銘を直接表せる。  \n例: Her outstanding leadership kept the project on track.  \n訳: 彼女の卓越した指導力によって、プロジェクトは予定どおり進んだ。  \n\n・wonderful  \n定義: 喜び、満足、感嘆をもたらすほどすばらしい。  \n頻度: 〈9/10〉  \n違い: `wonderful` は楽しい経験や好ましい人・物に日常的に使う。`magnificent` はより強く、堂々とした、または劇的な称賛を帯びやすい。  \n例: We had a wonderful evening with old friends.  \n訳: 私たちは旧友たちとすばらしい夜を過ごした。  \n\n【反意語】\n\n・mediocre  \n定義: 質や能力が平凡で、特に優れていない。  \n頻度: 〈6/10〉  \n違い: 質の高さという軸で、`magnificent` が極めて高い評価を表すのに対し、`mediocre` は平均的で期待を満たさない評価を表す。  \n例: The sequel received mediocre reviews from critics.  \n訳: その続編は批評家から凡庸だという評価を受けた。  \n\n・terrible  \n定義: 質や出来が非常に悪い。  \n頻度: 〈9/10〉  \n違い: 質の評価という軸で、`terrible` は非常に低い側、`magnificent` は非常に高い側を表す。  \n例: The team gave a terrible performance in the second half.  \n訳: そのチームは後半にひどい出来のプレーをした。  ",
  "_output_metadata": {
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-magnificent-20260908T084401Z-657240cc",
    "context_id": "cold-magnificent-context-20260908T084401Z-657240cc",
    "input_body_sha256": "258c1b3a17708126df77cb8e5db1556a9e738d56dd4183d8ccca00569461cdb7",
    "prompt_sha256": "25c298d1a4305746147791bd442cd725a92737c8f0802b992ea88e5c6ff76a5d",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false
  },
  "contract_version": "review_preflight_v1"
}
```
