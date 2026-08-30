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
  "entry_body": "\n＃発音記号\n\n名詞は米・英: /ˈpremɪs/。2音節の PREM-iss で、第1音節に主強勢がある。語末の `-ise` を /aɪz/ と読む語ではなく、名詞では /ɪs/ で終わる。  \n動詞は米・英で /prɪˈmaɪz/ と /ˈpremɪs/ の両方が辞書に載る。/prɪˈmaɪz/ では第2音節に強勢があり、語末は /aɪz/、/ˈpremɪs/ では名詞と同じ発音になる。とくに `be premised on/upon ...` を聞くときは、話者によってこの二つがあり得る。  \n複数形 premises は /ˈpremɪsɪz/。建物・敷地を表す `premises` も同じ発音で、綴りは複数形と同一である。動詞の過去形・過去分詞 premised、-ing形 premising は、採用する動詞発音に応じて発音も変わる。  \n\n＃語源\n\n中英語の *premise* は、古フランス語を経て中世ラテン語 *praemissa (propositio)*「前に置かれた命題」にさかのぼる。*praemissa* はラテン語 *praemittere*「前に送る、先に述べる」に由来し、*prae-*「前に」＋ *mittere*「送る」から成る。論証で結論より先に置かれる命題という発想が、現在の「推論・議論の前提」につながった。  \n`premises` の「建物・敷地」という意味は、単に「前提が複数ある」ことから生じたのではない。法律文書で先に述べられた事項や、譲渡文書で記載された対象を *premises* と呼んだ歴史を経て、そこに記載された土地・建物そのものを指すようになった。現代英語では、建物・敷地を指すときは複数形 `premises` が標準的な形である。一方、法務・規制・不動産管理などの限定された専門文脈では、単一の場所を指して単数の `a premise` / `one premise` が現れることもあるが、まれで法域や文書慣行に依存する。学習者は通常 `premises` を優先し、単一の場所を一般文で言うなら `a building`、`a property`、`a site` などを選ぶのが安全である。したがって「常に複数形」や「単数形は常に誤り」と一般化せず、一般用法の標準形と専門文脈に限られるまれな単数形を分けて覚えるのが実用的である。  \n\n＃語形成\n\n・premises：文脈により、`premise` の通常の複数形（複数の前提）または、建物・敷地を指す定着した不動産用法を表す。後者は単一の場所にも使われ、見た目は複数形だが通常は複数動詞を取る。  \n・premised：動詞 *premise* の過去形・過去分詞。とくに `be premised on/upon ...`「～を前提としている、～に基づいている」で頻出する。  \n・premising：動詞 *premise* の現在分詞・動名詞。一般語としての頻度は高くなく、論証や形式的な説明で現れる。  \n・premiss：主にイギリス英語で見られる異綴り。とくに論理学の「前提命題」で用いられることがあるが、`premise` のほうが広く通用する。  \n\n＃コアイメージ\n\n`premise` の中心は、「後に続く結論・判断・構成を支えるものを、先に置いて土台にする」である。議論では命題を先に置き、判断では仮定を土台にし、作品では物語を成立させる基本設定を置く。動詞では、その土台の上に理論や主張を組み立てることを表す。以下の語義5・6は別々の意味を暗記するためのものではなく、この同じ「前提を置く」という意味核を、項の取り方が異なる二つの構文として示している。  \n・議論・判断の土台として置く考え → 「前提、仮定」  \n・作品を成立させる土台の設定・筋立ての核 → 「基本設定、中心的な着想」  \n・論理学で議論の土台となる命題 → 「前提命題」  \n・理論・主張などをある考えの上に置く → 「～を…に基づかせる」  \n・命題や考え自体を前提として先に置く → 「～を前提として述べる・仮定する」  \n`premises` の「建物・敷地」という用法は歴史的には同じ語から発達したが、現代話者にとって上のコアイメージから直接推測しにくい定着義なので、語義4として別に意識する。ただし、一般用法の標準形は複数形 `premises` であり、限定的でまれな単数形 `a premise` は法域や文書慣行に依存するため、通常の言い換えとしては `a building`、`a property`、`a site` などを使う。名詞の「前提」と「前提命題」は同じ中心概念を共有し、論理学では後者の専門的な枠組みとして現れる。動詞の二つの説明も、同じ「前提を置く」という核を目的語の取り方の違いから整理したものである。  \n\n＃意味・用法・関連表現\n\n1. 【名詞・可算】前提、仮定、議論・判断の出発点\n\n【日本語訳・定義】議論、推論、判断、計画、行動などを進める際に、真である、またはひとまず受け入れるものとして置かれる考え・命題・仮定。その前提自体が実際に正しいことを `premise` という語が保証するわけではなく、`false premise`「誤った前提」のようにも使える。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準～やや形式的。議論、ビジネス、学術、政策、分析、日常の説明で広く使う。日常会話では `assumption` のほうが軽く自然な場面も多い。  \n\n【文法パターン】`the premise that ...`＝～という前提／`on the premise that ...`＝～という前提で／`start/work/proceed from the premise that ...`＝～を前提として始める・進める／`base 〈議論・計画〉 on the premise that ...`＝議論・計画を～という前提に置く／`question/challenge/reject a premise`＝前提を疑う・異議を唱える・退ける／`a false/flawed/basic/underlying premise`＝誤った・欠陥のある・基本的な・根底の前提  \n\n【コロケーション】\n\n・`the premise that ...`  \n用途: 内容を that節で明示して「～という前提」を表す。  \n例: The proposal rests on the premise that demand will continue to grow.  \n訳: その提案は、需要が今後も伸び続けるという前提に立っている。  \n\n・`on the premise that ...`  \n用途: 判断・行動を何らかの仮定に基づいて行うことを示す。  \n例: We planned the schedule on the premise that the parts would arrive by Friday.  \n訳: 私たちは、部品が金曜日までに届くという前提で日程を組んだ。  \n\n・`start from the premise that ...`  \n用途: 議論や分析の出発点となる考えを示す。  \n例: The report starts from the premise that access to data should be limited by purpose.  \n訳: その報告書は、データへのアクセスは目的に応じて制限されるべきだという前提から出発している。  \n\n・`an underlying premise`  \n用途: 明示されていなくても、議論や制度の根底で支えている前提を指す。  \n例: An underlying premise of the policy is that most users will follow the rules voluntarily.  \n訳: その方針の根底にある前提の一つは、大半の利用者が自発的に規則を守るということである。  \n\n・`a false/flawed premise`  \n用途: 結論以前に、出発点となる仮定そのものに誤りや欠陥があることを示す。  \n例: A convincing argument can still fail if it begins with a false premise.  \n訳: 説得力のある議論でも、誤った前提から始まれば成り立たないことがある。  \n\n・`question/challenge the premise`  \n用途: 相手の結論ではなく、その結論を支える出発点そのものを疑う。  \n例: Before discussing the cost, we should challenge the premise that the change is necessary.  \n訳: 費用を議論する前に、その変更が必要だという前提自体を検討し直すべきだ。  \n\n【語法・注意】`premise` は「結論を支える土台」に焦点があり、単に未確認の予想を表す `assumption` より論証・判断との結びつきが強い。`on the premise that ...` と `on the assumption that ...` は重なるが、前者は議論・方針の明示的な根拠という響きがやや強い。  \n\n`premise` は可算名詞なので、単数なら通常 `a/the premise`、複数なら `premises` となる。ただし複数形 `premises` には別に「建物・敷地」という定着義（語義4）がある。文脈によって `the premises` が「複数の前提」なのか「建物・敷地」なのかを区別する。  \n「前提が正しければ結論も必ず正しい」とは限らない。とくに論理学では、前提の真偽と、前提から結論が正しく導かれるかという妥当性は別問題である。  \n\n【類義語】\n\n・assumption  \n定義: 証明・確認されていないが、ひとまず真として受け入れる考え。  \n頻度: 〈10/10〉  \n違い: `assumption` は日常的な思い込みや計画上の仮定にも広く使える。`premise` は、その考えを土台に議論・推論・判断を組み立てる関係をより強く示す。  \n例: Our cost estimate is based on the assumption that fuel prices will remain stable.  \n訳: 私たちの費用見積もりは、燃料価格が安定したままだという仮定に基づいている。  \n\n・presupposition  \n定義: 発言・理論・考えの背後ですでに成り立つものとして想定されている前提。  \n頻度: 〈5/10〉  \n違い: `premise` が明示的な論証の土台にも使えるのに対し、`presupposition` は暗黙に先取りされている前提という含みが強く、言語学・哲学でも使われる。  \n例: The question contains the presupposition that someone made the decision deliberately.  \n訳: その質問には、誰かが意図的にその決定をしたという前提が含まれている。  \n\n・basis  \n定義: 判断・主張・制度などを支える根拠・基礎。  \n頻度: 〈10/10〉  \n違い: `basis` は事実、証拠、原則、計算方法など幅広い「基礎」を表せる。`premise` は特に、真として置く考え・命題を指す。  \n例: There is no factual basis for the claim.  \n訳: その主張には事実上の根拠がない。  \n\n2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想\n\n【日本語訳・定義】映画、小説、ドラマ、ゲーム、企画などを成立させる基本的な状況・設定・中心アイデア。作品によっては主要な筋立て・ストーリーラインの核まで指し、細かな出来事の並びをすべて指す `plot` より「作品を一文程度で要約できる土台」に焦点がある。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】標準語。映画・小説・テレビ番組・ゲームの紹介や批評、企画説明でよく使う。  \n\n【文法パターン】`the premise of 〈作品・企画〉`＝作品・企画の基本設定／`a simple/interesting/intriguing premise`＝単純な・興味深い・魅力的な設定／`the premise is that ...`＝基本設定は～である／`build a story around a premise`＝ある設定を中心に物語を作る  \n\n【コロケーション】\n\n・`the premise of the film/show/book`  \n用途: 作品の基本設定や中心アイデアを述べる。  \n例: The premise of the film is simple: nobody in the town can tell a lie.  \n訳: その映画の基本設定は単純で、町の誰も嘘をつけないというものだ。  \n\n・`an intriguing premise`  \n用途: 読者・視聴者の興味を引く基本設定を評価する。  \n例: The novel has an intriguing premise, even though the middle chapters move slowly.  \n訳: 中盤の展開は遅いものの、その小説には興味を引く基本設定がある。  \n\n・`build a story around a premise`  \n用途: 一つの中心設定を核として物語を展開する。  \n例: The writers built the series around the premise that memories could be traded.  \n訳: 脚本家たちは、記憶を売買できるという設定を中心にシリーズを構成した。  \n\n【語法・注意】この語義の `premise` と `plot` は重なることがあるが、通常は焦点が異なる。`premise` は物語を生む基本状況・中心アイデア、または主要な筋立ての核を要約するのに向き、`plot` は出来事がどのような順序・因果で展開するかという具体的な筋書きに焦点がある。`concept` はさらに広く、作品以外の発想や概念にも使える。  \n\n【類義語】\n\n・concept  \n定義: 作品・企画・製品などの中心となる発想・概念。  \n頻度: 〈9/10〉  \n違い: `concept` は視覚的・商品的・抽象的なアイデアにも広く使える。`premise` は「この条件・状況を出発点にすると何が起こるか」という物語的な設定に向きやすい。  \n例: The design concept combines a library with a community workspace.  \n訳: その設計コンセプトは、図書館と地域の共同作業空間を組み合わせている。  \n\n・setup  \n定義: 物語の冒頭で人物・状況・対立関係を整える設定・導入。  \n頻度: 〈8/10〉  \n違い: `setup` は物語が動き出すための具体的な初期配置に焦点がある。`premise` は作品全体を支える中心アイデアまで含み得る。  \n例: The opening scene establishes the setup for the mystery.  \n訳: 冒頭の場面で、そのミステリーの初期設定が示される。  \n\n・plot  \n定義: 物語で起きる出来事の筋、展開。  \n頻度: 〈9/10〉  \n違い: `plot` は出来事の連鎖そのもの。`premise` はその連鎖を生み出す基本条件・着想である。  \n例: The plot becomes more complicated after the second episode.  \n訳: 物語の筋は第2話以降さらに複雑になる。  \n\n3. 【名詞・可算・論理学】前提命題、推論の前提\n\n【日本語訳・定義】論証・推論において、結論を導くための出発点として置かれる命題。三段論法では `major premise`「大前提」、`minor premise`「小前提」のように呼ぶ。語義1の「議論の土台」という意味が、論理学で論証の構成要素として具体化した用法であり、まったく別の概念ではない。ここでは学習上、`major premise` / `minor premise` などの専門語法をまとめて示す。  \n\n【頻度】〈6/10〉  \n\n【レジスター/領域】論理学、哲学、批判的思考、議論分析。専門用語として標準的。  \n\n【文法パターン】`a premise of an argument`＝論証の前提命題／`major/minor premise`＝大前提・小前提／`premises and conclusion`＝前提群と結論／`derive/infer a conclusion from premises`＝前提から結論を導く／`the premises are true`＝前提群が真である  \n\n【コロケーション】\n\n・`major premise`  \n用途: 伝統的なカテゴリー三段論法で、結論の述語となる major term（大項）を含む前提を指す。「より一般的な内容だから大前提」と定義されるわけではない。  \n例: In “All metals conduct electricity; copper is a metal; therefore copper conducts electricity,” the first statement is the major premise because it contains the predicate term of the conclusion.  \n訳: 「すべての金属は電気を通す。銅は金属である。したがって銅は電気を通す」という三段論法では、最初の命題が結論の述語となる大項を含むため大前提である。  \n\n・`minor premise`  \n用途: 伝統的なカテゴリー三段論法で、結論の主語となる minor term（小項）を含む前提を指す。「個別的な内容だから小前提」と定義されるわけではない。  \n例: In the same syllogism, “Copper is a metal” is the minor premise because it contains the subject term of the conclusion.  \n訳: 同じ三段論法では、「銅は金属である」が結論の主語となる小項を含むため小前提である。  \n\n・`premises and conclusion`  \n用途: 論証を、根拠として置かれる命題群と、そこから導かれる結論に分けて捉える。  \n例: To evaluate the argument, separate its premises from its conclusion.  \n訳: その論証を評価するには、前提群と結論を分けて考えなさい。  \n\n・`infer a conclusion from the premises`  \n用途: 与えられた前提から推論によって結論を導く。  \n例: The conclusion cannot be inferred from the premises without an additional assumption.  \n訳: 追加の仮定がなければ、その前提群からその結論を導くことはできない。  \n\n【語法・注意】論理学では、「前提が真であること」と「推論が妥当であること」を混同しない。妥当な論証は、前提が真なら結論が偽にならない形を持つことを問題にするのであり、`valid premise` を単純に「真の前提」の意味で使うより、`true premise` と `valid argument/inference` を区別するほうが正確である。  \n\nイギリス英語では、この論理学上の語義に綴り `premiss` が使われることがある。現代の一般文では `premise` でも広く通用する。  \n\n【類義語】\n\n・proposition  \n定義: 真か偽かを問いうる内容を持つ命題。  \n頻度: 〈6/10〉  \n違い: `proposition` は命題そのものの種類を表し、結論にもなり得る。`premise` は論証の中で、その命題が結論を支える役割に置かれていることを表す。  \n例: The proposition is false, but it can still be used to illustrate the form of the argument.  \n訳: その命題は偽だが、論証の形式を示すためには使える。  \n\n・assumption  \n定義: 推論のために真として置く仮定。  \n頻度: 〈9/10〉  \n違い: `assumption` は明示されない補助的な仮定にも使える。`premise` は論証の構成要素として提示された命題を指しやすい。  \n例: The proof depends on an unstated assumption about continuity.  \n訳: その証明は、連続性についての明示されていない仮定に依存している。  \n\n4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）\n\n【日本語訳・定義】人・会社・組織などが所有・占有・使用する土地、建物、建物の一部、およびそれに付随する敷地。会社・店舗・学校・病院・工場などの場所に特によく使うが、住宅や賃貸物件などにも使える。現代英語ではこの意味を通常 `premises` という複数形で表す。単一の施設でもこの複数形を使うのが一般的で、法務・規制・不動産管理などの限定された文脈に単数の `a premise` / `one premise` が現れることもあるが、まれで法域や文書慣行に依存する。学習者が一般文で単一の場所を言うなら `a building`、`a property`、`a site` のほうが安全で自然なことが多い。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】標準～やや形式的。規則、契約、警告表示、警備、保険、不動産、事業運営、住宅・賃貸関係でよく使う。  \n\n【文法パターン】`on the premises`＝その構内・敷地内で／`off the premises`＝構外・敷地外で／`enter/leave/vacate the premises`＝構内に入る・出る・退去する／`business/commercial/industrial premises`＝事業用・商業用・工業用施設／`the premises are ...`＝その建物・敷地は～である  \n\n【コロケーション】\n\n・`on the premises`  \n用途: 建物・敷地の内側で行われることを表す。`premises` に所有格を付けず、特定の構内なら `the` を使うことが多い。  \n例: Smoking is not permitted anywhere on the premises.  \n訳: この敷地内では、どこであっても喫煙は認められていない。  \n\n・`off the premises`  \n用途: 建物・敷地の外へ出た場所、または外で行うことを表す。  \n例: Confidential documents must not be taken off the premises without permission.  \n訳: 機密文書を許可なく構外へ持ち出してはならない。  \n\n・`leave/vacate the premises`  \n用途: 人が構内を離れる、または占有者が建物・敷地から退去することを表す。`vacate` はより形式的。  \n例: Visitors must leave the premises by 9 p.m.  \n訳: 来訪者は午後9時までに構内から退出しなければならない。  \n\n・`business/commercial premises`  \n用途: 事業に使用される建物・敷地をまとめて表す。  \n例: The company moved to larger business premises near the station.  \n訳: その会社は駅の近くの、より広い事業用施設へ移転した。  \n\n・`the premises are ...`  \n用途: `premises` を複数扱いして状態を述べる。  \n例: The premises are protected by security cameras at all times.  \n訳: その施設は常時、防犯カメラで監視されている。  \n\n【語法・注意】この意味の `premises` は見た目が複数形で、標準的には複数動詞を取る。`These premises are ...`、`the premises have ...` のように考える。単数の建物や物件を指すときも、一般的な文では `a building`、`a property`、`a site` などのほうが自然で、学習者はこれらを優先するとよい。法務・規制・施設管理などでは `a premise`、`a single premise`、`one premise` のような単数形が現れることもあるが、まれで法域や文書慣行に依存する。したがって、通常の建物・物件の意味で `a premise` を自分から使うのは避けつつ、実例で見た単数形を一律に誤用と決めつけない。  \n\n`premises` は建物だけに限定されず、土地・敷地や建物の一部まで含み得る。したがって、日本語訳は文脈に応じて「建物」「施設」「敷地」「構内」「事業所」「物件」などを選ぶ。語義1の複数形 `premises`「複数の前提」と綴り・発音が同じなので、`on/off the premises` や不動産・警備文脈を手掛かりに区別する。  \n\n【類義語】\n\n・property  \n定義: 所有される土地・建物、不動産。  \n頻度: 〈10/10〉  \n違い: `property` は所有物・不動産としての法的・経済的な対象に焦点があり、個人住宅にも広く使える。`premises` は所有者が誰かより、その場所が占有・使用される物理的な建物・敷地として捉えられることが多い。  \n例: The company owns several properties in the city.  \n訳: その会社は市内に複数の不動産を所有している。  \n\n・site  \n定義: 建物・活動・工事などが置かれている、または行われる場所・敷地。  \n頻度: 〈10/10〉  \n違い: `site` は場所そのものに焦点があり、建物がまだない土地にも使える。`premises` は既に占有・使用されている建物・敷地をまとめて指しやすい。  \n例: Construction will begin on the new site next month.  \n訳: 新しい敷地では来月、建設工事が始まる。  \n\n・facility  \n定義: 特定の目的のために設けられた建物・設備。  \n頻度: 〈9/10〉  \n違い: `facility` は機能・設備に焦点があり、研究施設・製造施設など用途を強調する。`premises` は用途の詳細より、物理的な構内全体を指す。  \n例: The laboratory operates a testing facility outside the city.  \n訳: その研究所は市外で試験施設を運営している。  \n\n【動詞の整理】語義5と語義6は、意味核が連続する一つの動詞用法を、構文の違いで分けて示したものである。語義5は `premise A on/upon B` の形で、A（理論・主張など）をB（前提となる考え）の上に組み立てる。語義6は `premise that P` の形で、Pの内容そのものを前提として置く。したがって、二つをまったく別の意味としてではなく、「前提を置く」という共通の核と項の取り方の違いとして読む。  \n\n5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる\n\n【日本語訳・定義】理論、議論、計画、判断などを、ある考え・仮定が真または受け入れられるものとして土台にして組み立てる。語義6と同じ「前提を置く」という核を持つが、ここでは目的語Aを前提Bの上に組み立てる `A on B` の構文に焦点を置く。現代英語では、とくに受動態 `be premised on/upon ...`「～を前提としている、～に基づいている」が重要である。  \n\n【頻度】〈6/10〉  \n\n【レジスター/領域】形式的。学術、政策、法律、ビジネス分析、評論で使う。日常会話では `base ... on ...` のほうが一般的。  \n\n【文法パターン】`premise 〈理論・主張・計画〉 on/upon 〈考え・仮定〉`＝理論などを考え・仮定に基づかせる／`〈理論・主張・計画〉 be premised on/upon 〈考え・仮定〉`＝理論などが考え・仮定を前提としている  \n\n【コロケーション】\n\n・`be premised on the assumption that ...`  \n用途: 理論・計画などの根底にある仮定を明示する。  \n例: The forecast is premised on the assumption that interest rates will remain unchanged.  \n訳: その予測は、金利が据え置かれるという仮定を前提にしている。  \n\n・`be premised on the idea that ...`  \n用途: 制度・主張などが、ある考えを出発点として構成されていることを表す。  \n例: The program is premised on the idea that early support can prevent larger problems later.  \n訳: そのプログラムは、早期支援によって後の大きな問題を防げるという考えに基づいている。  \n\n・`premise an argument on/upon ...`  \n用途: 議論を特定の前提に基づかせる。能動態は受動態より形式的で、頻度も低い。  \n例: The author premises the argument on a distinction between legal ownership and practical control.  \n訳: 著者は、法的所有と実質的支配の区別を前提としてその議論を組み立てている。  \n\n【語法・注意】動詞の中心構文は `premise A on/upon B` で、A が「組み立てられる理論・主張・行動」、B が「その土台となる前提」である。方向を逆にしない。受動態では `A is premised on B` となり、学習者にとって最も遭遇しやすい形である。  \n\n`be premised on ...` と `be based on ...` は近いが、`premised on` は「ある考え・仮定を前提として組み立てられている」ことを強く示す。証拠・データなど広い根拠には `based on` のほうが自然な場合が多い。  \n動詞の発音には /prɪˈmaɪz/ と /ˈpremɪs/ の両方がある。名詞と同じ綴りだからといって、常に名詞と同じ発音だけだと決めつけない。  \n\n【類義語】\n\n・base  \n定義: 考え・行動・判断などを、特定の根拠・情報・原則に基づかせる。  \n頻度: 〈10/10〉  \n違い: `base A on B` は証拠・データ・経験などにも非常に広く使える。`premise A on B` は B が「前提として置かれる考え・仮定」である場合に特に適し、より形式的。  \n例: The decision was based on updated safety data.  \n訳: その決定は最新の安全データに基づいていた。  \n\n・found  \n定義: 理論・制度・主張などを、ある原理・根拠の上に築く。  \n頻度: 〈5/10〉  \n違い: `be founded on ...` は基礎となる原理・価値・事実にも使え、`premised on` より「築かれている」という比喩が強い。  \n例: The organization was founded on the principle of equal access.  \n訳: その組織は、平等なアクセスという原則に基づいて設立された。  \n\n・predicate  \n定義: 主張・判断などを、ある条件・事実・前提に依存させる。  \n頻度: 〈4/10〉  \n違い: `predicate A on B` は非常に形式的で、法律・学術で見られる。`premise A on B` と近いが、`premise` は「前提命題を置く」という語源・論証とのつながりがより直接的である。  \n例: The claim is predicated on evidence that has since been disputed.  \n訳: その主張は、その後争われるようになった証拠を前提としている。  \n\n6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する\n\n【日本語訳・定義】語義5と同じ「前提を置く」という核を持つが、ここでは目的語・that節の内容そのものを前提として提示する。議論や推論を始める前に、ある命題・考えを前提として提示したり、真であるものとして仮に置いたりする。語義5の `premise A on B` では A が前提に基づいて組み立てられる対象だが、この語義では目的語・that節の内容そのものが「前提として置かれる内容」になる。  \n\n【頻度】〈3/10〉  \n\n【レジスター/領域】非常に形式的で低頻度。論証、哲学、古風・硬い説明文で見られる。現代の一般文では `assume`、`posit`、`postulate` などのほうが普通。  \n\n【文法パターン】`premise that ...`＝～だと前提として述べる・仮定する／`premise 〈命題・考え〉`＝命題・考えを前提として置く／`let us premise that ...`＝～だと前提としておこう  \n\n【コロケーション】\n\n・`premise that ...`  \n用途: 後続の議論のため、that節の内容そのものを前提として置く。  \n例: The author premises that each participant has access to the same information.  \n訳: 著者は、各参加者が同じ情報にアクセスできることを前提として置いている。  \n\n・`let us premise that ...`  \n用途: 論証の冒頭で、検討のための前提を明示的に設定する。現代ではかなり硬い。  \n例: Let us premise that the two measurements were taken under identical conditions.  \n訳: 2回の測定は同一条件で行われたことを前提としておこう。  \n\n・`premise a proposition`  \n用途: 命題そのものを、後の推論に先立つ前提として提示する。  \n例: The author premises a proposition about human motivation before turning to the main argument.  \n訳: 著者は本論に入る前に、人間の動機に関する命題を前提として提示している。  \n\n【語法・注意】語義5と語義6は意味の核が連続しており、主な違いは項の取り方である。この語義は現代英語では低頻度で、学習上は語義5の `be premised on/upon ...` のほうを優先する。`premise that P` では P 自体を前提として置くのに対し、`A is premised on P` では A が P を土台として組み立てられている。項の方向が異なるので混同しない。  \n\n古い・非常に形式的な英語には、主題に先立って何かを述べる「前置きする」という用法もあるが、現代の一般的な産出用法として優先度は低い。  \n\n【類義語】\n\n・assume  \n定義: 証明せずに、ある内容をひとまず真として受け入れる。  \n頻度: 〈10/10〉  \n違い: `assume` は日常・学術のどちらでも広く使え、`premise` よりはるかに一般的。`premise` は論証の前提として明示的に置くという硬い響きがある。  \n例: Assume that the two samples are independent.  \n訳: 2つの標本は独立していると仮定しなさい。  \n\n・posit  \n定義: 議論・理論のために、命題や仮説を明示的に提示する。  \n頻度: 〈5/10〉  \n違い: `posit` は学術・哲学で比較的自然に使える一方、この語義の `premise` はさらにまれで古風・形式的に感じられることがある。  \n例: The model posits that agents act on incomplete information.  \n訳: そのモデルは、行為者は不完全な情報に基づいて行動すると仮定している。  \n\n・postulate  \n定義: 理論や推論の出発点として、命題・原理を仮定する。  \n頻度: 〈5/10〉  \n違い: `postulate` は科学・数学・哲学で「理論上の仮定として置く」ことを明確に表せる。`premise` は同じ方向を表せるが、動詞としては使用範囲が狭い。  \n例: The theory postulates the existence of an unobserved mechanism.  \n訳: その理論は、観測されていない機構の存在を仮定している。  ",
  "_output_metadata": {
    "schema_version": "final_review_v2",
    "stage": "final_review",
    "run_id": "blind-premise-20260830T050603Z-70fc66a4",
    "context_id": "blind-premise-context-20260830T050603Z-70fc66a4",
    "input_body_sha256": "aee242be6021273395bb3c43a5d3c50db5a4c830c70c9d2021b265adad4afe9a",
    "prompt_sha256": "3158e690b19b0f822a032dffa1cbfe1d38d64a0de2c1dba582554fa2b729f117",
    "input_artifacts": [
      "entry_body",
      "all_findings",
      "resolutions",
      "sealed_final_blind",
      "final_review_spec"
    ],
    "blind_output_sha256": "512bbc41fc38da0eb652d4204684af387a592246fd3ccdc0dbdc2dcbf06db16b"
  },
  "pass_findings": {
    "summary": "Independent checker passes completed by two-stage handoff.",
    "pass_outputs": [
      {
        "pass_id": "translation",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "multi_agent_v1 inherited (no model override)",
          "ingested_by": "human",
          "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
        }
      },
      {
        "pass_id": "sense-structure",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "multi_agent_v1 inherited (no model override)",
          "ingested_by": "human",
          "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
        }
      },
      {
        "pass_id": "frame-relation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "multi_agent_v1 inherited (no model override)",
          "ingested_by": "human",
          "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "axes": [],
          "reviewer": {
            "mode": "handoff",
            "declared_model": "multi_agent_v1 inherited (no model override)",
            "ingested_by": "human",
            "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
          },
          "input_body_sha256": "aee242be6021273395bb3c43a5d3c50db5a4c830c70c9d2021b265adad4afe9a",
          "blind_request_sha256": "b67af89342a029acc7a531ad34c733b9f2617cfa41e7cd13f951ff6e5abf1f28",
          "recorded_at": "2026-08-30T05:13:11.473622+00:00"
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "adjudications": [],
          "frame_findings": [],
          "unrouted_observations": [],
          "reviewer": {
            "mode": "handoff",
            "declared_model": "multi_agent_v1 inherited (no model override)",
            "ingested_by": "human",
            "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
          },
          "input_body_sha256": "aee242be6021273395bb3c43a5d3c50db5a4c830c70c9d2021b265adad4afe9a",
          "stage2_request_sha256": "f257af60fbbf3183df2fa5893b3a4c8d07797b451c85e3059aa365fa3b8e72a8",
          "blind_record_sha256": "fb0ec022c9ebc52dd245a52f76906903b8b12d47d5b83980e07b72f8ca3354db"
        },
        "aligned_at": "2026-08-30T05:13:28.352244+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "multi_agent_v1 inherited (no model override)",
          "ingested_by": "human",
          "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "pass_id": "example-attribution",
          "input_body_sha256": "aee242be6021273395bb3c43a5d3c50db5a4c830c70c9d2021b265adad4afe9a",
          "blind_request_sha256": "23d40d9ec5e790fe8e0a17b6dd1ed36309b36131b9f52f746c7dc13667813602",
          "recorded_at": "2026-08-30T05:13:11.404653+00:00",
          "attributions": [
            {
              "example_id": "ex-35e3e3410780",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "false premise"
              ],
              "rationale": "The phrase \"false premise\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-542f57c9e399",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "intriguing premise"
              ],
              "rationale": "The phrase \"intriguing premise\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-90181657bf26",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "premises are protected"
              ],
              "rationale": "The phrase \"premises are protected\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-a26bfb673244",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "leave the premises"
              ],
              "rationale": "The phrase \"leave the premises\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-60c0d14e4b83",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "premise of the film"
              ],
              "rationale": "The phrase \"premise of the film\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-bcba7d0c7ecc",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "around the premise that"
              ],
              "rationale": "The phrase \"around the premise that\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-9af159ff49a5",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "challenge the premise that"
              ],
              "rationale": "The phrase \"challenge the premise that\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-90e286d2a0ab",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "underlying premise"
              ],
              "rationale": "The phrase \"underlying premise\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-1f6ec537a5dc",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "on the premise that the parts"
              ],
              "rationale": "The phrase \"on the premise that the parts\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-29296cc96fc6",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "is premised on the assumption"
              ],
              "rationale": "The phrase \"is premised on the assumption\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-6aee6bdd74b9",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "premises the argument on"
              ],
              "rationale": "The phrase \"premises the argument on\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-ac2c211c0d05",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "major premise"
              ],
              "rationale": "The phrase \"major premise\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-80db9366a9fc",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "on the premises"
              ],
              "rationale": "The phrase \"on the premises\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-6631bf9d65c1",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "is premised on the idea"
              ],
              "rationale": "The phrase \"is premised on the idea\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-44950d084e23",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "business premises"
              ],
              "rationale": "The phrase \"business premises\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-13697499d3ae",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "off the premises"
              ],
              "rationale": "The phrase \"off the premises\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-251cafe6da52",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "its premises"
              ],
              "rationale": "The phrase \"its premises\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-1ba429b22f56",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:006"
              ],
              "discriminating_terms": [
                "premises that each participant"
              ],
              "rationale": "The phrase \"premises that each participant\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-3701ae3f4776",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "rests on the premise"
              ],
              "rationale": "The phrase \"rests on the premise\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-7dc731c78855",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "starts from the premise"
              ],
              "rationale": "The phrase \"starts from the premise\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-9fb2d052bc49",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "minor premise"
              ],
              "rationale": "The phrase \"minor premise\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-2c6afed91986",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:006"
              ],
              "discriminating_terms": [
                "premises a proposition"
              ],
              "rationale": "The phrase \"premises a proposition\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-4fb411c06a9c",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "inferred from the premises"
              ],
              "rationale": "The phrase \"inferred from the premises\" identifies the example's use of premise."
            },
            {
              "example_id": "ex-5346afeaa3bd",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:006"
              ],
              "discriminating_terms": [
                "premise that the two measurements"
              ],
              "rationale": "The phrase \"premise that the two measurements\" identifies the example's use of premise."
            }
          ],
          "reviewer": {
            "mode": "handoff",
            "declared_model": "multi_agent_v1 inherited (no model override)",
            "ingested_by": "human",
            "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
          }
        },
        "aligned_at": "2026-08-30T05:13:11.473913+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "qualification",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "multi_agent_v1 inherited (no model override)",
          "ingested_by": "human",
          "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
        }
      },
      {
        "pass_id": "pronunciation",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "multi_agent_v1 inherited (no model override)",
          "ingested_by": "human",
          "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
        }
      },
      {
        "pass_id": "evidence",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "multi_agent_v1 inherited (no model override)",
          "ingested_by": "human",
          "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
        }
      }
    ],
    "independent_candidates": [],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "multi_agent_v1 inherited (no model override)",
      "ingested_by": "human",
      "agent_id": "multi-agent:01a05101-2767-72b3-8b77-74a083df20b4:checker_passes"
    },
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-premise-20260830T050603Z-70fc66a4",
    "context_id": "normal-premise-context-20260830T050603Z-70fc66a4",
    "input_body_sha256": "aee242be6021273395bb3c43a5d3c50db5a4c830c70c9d2021b265adad4afe9a",
    "prompt_sha256": "5178f5a14a9525317811a34e6cd307108436f4babc1299fcd2eb9031f28ba737",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-08-30T05:13:11.473559+00:00"
  },
  "cold_review": {
    "summary": "Fresh context-free cold review found no learner-significant content defects.",
    "findings": [],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "multi_agent_v1 inherited (no model override)",
      "ingested_by": "human",
      "agent_id": "multi-agent:01a050fa-cafe-7700-a2b3-d33468c970b5:cold_review"
    },
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-premise-20260830T050603Z-70fc66a4",
    "context_id": "cold-premise-context-20260830T050603Z-70fc66a4",
    "input_body_sha256": "aee242be6021273395bb3c43a5d3c50db5a4c830c70c9d2021b265adad4afe9a",
    "prompt_sha256": "0ed4409a73095a9a2968bdcdb20bc397be345af84bff2c3558a48f08a5488aae",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-08-30T05:14:22.373084+00:00"
  },
  "final_blind": {
    "provisional_decision": "pass",
    "independent_candidates": [
      {
        "id": "noun-basis",
        "surface_form": "premise",
        "frame": "a/the premise; premises",
        "meaning": "a proposition or assumption used as a basis for reasoning, judgment, planning, or action",
        "disposition": "included",
        "rationale": "The entry includes premise as a countable general noun for a proposition or assumption that supports reasoning and decisions.",
        "semantic_assertions": [
          {
            "id": "sa-noun-basis",
            "statement": "A premise must function as a proposition, assumption, or starting point supporting reasoning or judgment.",
            "polarity": "must_hold",
            "scope": "general noun sense"
          }
        ]
      },
      {
        "id": "noun-content-clause",
        "surface_form": "the premise that P / on the premise that P",
        "frame": "the premise that P; on the premise that P; start from the premise that P",
        "meaning": "a that-clause identifying the proposition used as an assumed basis",
        "disposition": "included",
        "rationale": "The frame the premise that P / on the premise that P is explicitly included for contentful assumptions.",
        "semantic_assertions": [
          {
            "id": "sa-noun-content-clause",
            "statement": "The that-clause must identify the proposition treated as the premise, while on the premise that P marks reasoning or action based on it.",
            "polarity": "must_hold",
            "scope": "noun content-clause constructions"
          }
        ]
      },
      {
        "id": "noun-narrative",
        "surface_form": "premise",
        "frame": "the premise of a film/show/book; build a story around a premise",
        "meaning": "the basic situation or central idea underlying a story, film, show, game, or project",
        "disposition": "included",
        "rationale": "The frame the premise of a film/show/book; build a story around a premise is included for the narrative sense, distinct from plot.",
        "semantic_assertions": [
          {
            "id": "sa-noun-narrative",
            "statement": "A story premise must denote its basic situation or central idea rather than the full sequence of plot events.",
            "polarity": "must_hold",
            "scope": "narrative and project usage"
          }
        ]
      },
      {
        "id": "noun-logic",
        "surface_form": "premise",
        "frame": "major/minor premise; premises and conclusion; infer a conclusion from premises",
        "meaning": "a proposition functioning as a premise in a logical argument or syllogism",
        "disposition": "included",
        "rationale": "The frame major/minor premise; premises and conclusion; infer a conclusion from premises is included for the specialized logic sense.",
        "semantic_assertions": [
          {
            "id": "sa-noun-logic",
            "statement": "In logic, a premise must function as a supporting proposition from which a conclusion is inferred.",
            "polarity": "must_hold",
            "scope": "logic and syllogistic usage"
          }
        ]
      },
      {
        "id": "noun-property-plural",
        "surface_form": "premises",
        "frame": "on/off the premises; enter/leave/vacate the premises; the premises are ...",
        "meaning": "the building, land, or property occupied or used by a business, organization, or other occupant",
        "disposition": "included",
        "rationale": "The frame on/off the premises; enter/leave/vacate the premises; the premises are ... is included for the property sense.",
        "semantic_assertions": [
          {
            "id": "sa-noun-property-plural",
            "statement": "In the property sense, premises must normally remain plural in form and take plural agreement even when one location is meant.",
            "polarity": "must_hold",
            "scope": "general property usage"
          }
        ]
      },
      {
        "id": "noun-property-singular-rare",
        "surface_form": "a premise / one premise",
        "frame": "singular property usage in specialist legal, regulatory, real-estate, or document contexts",
        "meaning": "a rare singular variant referring to one property or location",
        "disposition": "included",
        "rationale": "The surface form a premise / one premise is included descriptively as a rare, jurisdiction- and document-practice-dependent property variant, not as a spontaneous learner form.",
        "semantic_assertions": [
          {
            "id": "sa-noun-property-singular-rare",
            "statement": "The singular property use a premise / one premise must be rare and dependent on jurisdiction or document practice, and must not be treated as the default general-English form.",
            "polarity": "must_hold",
            "scope": "specialist property usage and learner guidance"
          }
        ]
      },
      {
        "id": "verb-premise-on",
        "surface_form": "premise",
        "frame": "premise A on/upon B; A is premised on/upon B",
        "meaning": "to base a theory, claim, plan, forecast, or action on an assumed proposition",
        "disposition": "included",
        "rationale": "The frame premise A on/upon B; A is premised on/upon B is explicitly included with the argument roles A as the based object and B as its foundation.",
        "semantic_assertions": [
          {
            "id": "sa-verb-premise-on",
            "statement": "In premise A on/upon B, A must be the object being based and B must be the premise or foundation; the roles must not be reversed.",
            "polarity": "must_hold",
            "scope": "transitive verb sense and passive construction"
          }
        ]
      },
      {
        "id": "verb-premise-that",
        "surface_form": "premise",
        "frame": "premise that P; premise NP; let us premise that P",
        "meaning": "to state or assume a proposition as a premise in very formal or rare usage",
        "disposition": "included",
        "rationale": "The frame premise that P; premise NP; let us premise that P is included and explicitly marked as formal and low-frequency.",
        "semantic_assertions": [
          {
            "id": "sa-verb-premise-that",
            "statement": "In premise that P, P must be the proposition being posited as a premise, unlike A in premise A on/upon B.",
            "polarity": "must_hold",
            "scope": "formal and rare transitive verb usage"
          }
        ]
      }
    ],
    "article_findings": [],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "multi_agent_v1 inherited (no model override)",
      "ingested_by": "human",
      "agent_id": "multi-agent:01a050fa-f816-7391-a463-a7f60d55b0bc:final_blind"
    },
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-premise-20260830T050603Z-70fc66a4",
    "context_id": "blind-premise-context-20260830T050603Z-70fc66a4",
    "input_body_sha256": "aee242be6021273395bb3c43a5d3c50db5a4c830c70c9d2021b265adad4afe9a",
    "prompt_sha256": "fe20d444c973f78bd4f37856337d412cdcdf9860a761f523f93a3cefc8e58bee",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-08-30T05:21:16.204437+00:00"
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/p/premise.md",
    "body_sha256": "aee242be6021273395bb3c43a5d3c50db5a4c830c70c9d2021b265adad4afe9a",
    "final_blind_path": "audits/runs/p/premise/20260830T050603Z-70fc66a4/final_blind.json",
    "final_blind_sha256": "f456e0adee0969ca647e38017fa3830f8b20e1235f8c70a252539571348d659b",
    "blind_output_sha256": "512bbc41fc38da0eb652d4204684af387a592246fd3ccdc0dbdc2dcbf06db16b",
    "sealed_at": "2026-08-30T14:22:18.144006+09:00"
  },
  "resolutions": {
    "schema_version": "resolutions_v1",
    "stage": "resolutions",
    "run_id": "normal-premise-20260830T050603Z-70fc66a4",
    "context_id": "normal-premise-context-20260830T050603Z-70fc66a4",
    "input_body_sha256": "aee242be6021273395bb3c43a5d3c50db5a4c830c70c9d2021b265adad4afe9a",
    "prompt_sha256": "no-findings-empty-resolution",
    "input_artifacts": [
      "entry_body",
      "all_findings"
    ],
    "recorded_at": "2026-08-30T05:22:29.345765+00:00",
    "resolutions": []
  }
}
```
