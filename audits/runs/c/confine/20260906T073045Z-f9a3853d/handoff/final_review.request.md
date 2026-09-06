# Independent review handoff

Stage: `final_review`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session.

## Prompt

# final_review_spec_v2

この仕様は、最新版の記事本文、pre/post-blind resolution、影響範囲checkerの再検査・再利用manifest、固定済みblind inventory、具体的未解決事項だけを入力として、第三者最終審査が合否を判断するための意味基準だけを定める。入力分離、順序、hash、seal、記録、件数網羅、status同期は `scripts/run_word.py`、`scripts/workflow_revision.py`、`scripts/generate_audit_manifest.py` が強制する。

final reviewは新たな全面レビューをもう一巡する段階ではない。本文hash、すべてのfindingの完全な裁定、pass再検査・再利用条件、source union、blind chronology、未解決blockerゼロを照合する。hash、件数、集合、時系列、schemaはコードの結果を使い、内容を長大に復唱しない。

## PASSの意味基準

次をすべて満たす場合だけ `PASS` とする。

1. 記事の事実、語法、発音、例文、訳が正しく、見出し語の意味方向・意味役割・適用範囲を誤学習させない。
2. 主要な品詞、語義、派生・転換、専門用法、完全な統語フレームが過不足なく扱われ、語義境界、コアイメージ、定義、語法、コロケーション、語彙関係の間に矛盾がない。
3. 例文と訳で、述語、主語・目的語・補語、行為者・経験者・対象・結果、肯否、比較基準、程度、数量、時制・相・法、条件・因果・目的、修飾範囲、焦点、情報構造、レジスター、話者評価が保存されている。
4. 地域差、専門・制度用法、頻度、語源、語形成、語義境界、文法制約、絶対表現などの高リスク主張が、当該主張へ適用できる根拠に支えられ、反例・矛盾・適用範囲が確認されている。検索見出し、資料名だけ、別義の用例は根拠にしない。
5. checker/cold findingはpre-blind、final-blind findingはpost-blindで重複・欠落なく裁定され、採用修正の影響範囲checkerが再検査済みで、再利用passはspec・正規化入力・source artifact・schema・独立性・request bindingがすべて一致している。
6. blind inventoryの各 `semantic_assertion` を最新版へ適用しても、候補の境界・作用方向・包含/除外関係・一般化範囲に反する記述がない。
7. final blindがcold reviewおよびpre-blind revisionより後で、pre-blind修正後本文hashに束縛されている。final-blind findingの採用修正がある場合は、影響checker再検査後の新本文を新しい独立final blindが確認している。
8. `insufficient_evidence`、未検査範囲、無効pass、判断衝突、未確認の修正影響が残っていない。

## REJECTの意味基準

上記のいずれかを満たさない場合は `REJECT` とする。blockerにできるのは、事実・語法・発音の誤り、例文/訳の誤り、主要語義・構文の欠落または過剰収録、根拠と本文の矛盾、内容仕様の必須項目違反、未判定・未解決項目である。各blockerには対象ID、問題、必要な修正を記録する。条件付き合格は使わない。

本文と矛盾しない分類粒度・棚卸し構成の差、より良い表現の提案、任意の改善余地は、それだけを理由に `REJECT` にせず、非blocking noteとして記録する。`REJECT` は審査失敗ではなく、問題を検出して完了した正常な最終判定である。

## 出力

`final_review_v2` JSONとして、全target/relation/normal candidate/blind candidate/finding/evidence/source-unionの個別結果、再検査・再利用manifestの照合結果、`decision` (`pass | reject`)、`blockers`、非blocking `notes` を返す。`PASS` は全個別結果がpass、未解決・hold・`insufficient_evidence`が0件、blockerが0件の場合に限る。本文は変更しない。新しい内容上のblockerを見つけた場合は正常なREJECTとし、修正、影響範囲再検査、final blind再実行へ戻す。


## Input packet

```json
{
  "stage": "final_review",
  "entry_body": "\n＃発音記号\n\n動詞は米・英: /kənˈfaɪn/。2音節で第2音節に主強勢があり、第1音節の母音は弱い /ə/ になる。低頻度の名詞は、米: /ˈkɑːnfaɪn/｜英: /ˈkɒnfaɪn/ で、第1音節に主強勢が移り、第1音節の母音にも米英差がある。  \n\n＃語源\n\n動詞は中期フランス語 confiner「境を接する、限界内にとどめる」から英語に入り、さらにラテン語 confinis「境を接する」にさかのぼる。con-「共に」と finis「境界、終わり」が結び付いた語で、「境界を共有する・隣接する」という古い意味から、境界を定めてその内側にとどめる現代の「範囲を限る」「閉じ込める」へ発達した。  \n\n＃語形成\n\n・confinement（名詞）— 閉じ込めること、閉じ込められた状態、拘禁。  \n・confined（形容詞）— 狭く囲まれた、限られた。単なる過去分詞としての受動用法と、confined space のような形容詞用法がある。  \n・confining（現在分詞）— confine の -ing 形。  \n・unconfined（形容詞）— 閉じ込められていない、境界内に制限されていない。  \n\n＃コアイメージ\n\n人・物・活動・内容などを、ある境界の内側にとどめ、外へ出たり広がったりしないようにする。形容詞形 confined ではその結果の状態や窮屈さを、名詞では境界そのものを表す。  \n\n・対象の範囲を一定の境界内にとどめる → 「～を…に限る、限定する」（語義1）  \n・人や動物を一定の場所から出られなくする → 「閉じ込める、拘束する」（語義2）  \n・病気やけがで生活場所を狭い範囲にとどめる → 「～を寝床・自宅などにとどめる」（語義3）  \n・空間や区域が狭い境界内に収まった状態 → 「狭く囲まれた、限られた」（語義4）  \n・内外を分けて範囲を画する境界 → 「境界、範囲、領域」（語義5）  \n\n＃意味・用法・関連表現\n\n1. 【他動詞】～を…に限る、限定する\n\n【日本語訳・定義】話題、活動、作業、影響、現象などが及ぶ範囲を、特定の対象・場所・期間・分野などの内側に限定する。対象がすでにその範囲に収まっていることを述べる受動形のほか、話し手が意識的に扱う範囲を絞る能動形・再帰形でも使われる。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】一般語だが、日常会話より文章、ニュース、ビジネス、学術的説明でやや多い。  \n\n【文法パターン】confine something to 〈範囲・場所・期間・活動〉＝何かを～の範囲内に限る／confine oneself to 〈名詞・doing〉＝自分が扱う内容・行うことを～だけにする／be confined to 〈範囲・場所・集団〉＝～に限られている／confine 〈発言・検討・努力〉 to 〈対象〉＝発言・検討・努力の対象を～に絞る  \n\n【コロケーション】\n\n・confine the discussion to 〈話題〉  \n用途: 議論で扱う範囲を特定の話題に限定する。  \n例: Please confine the discussion to the issues on today's agenda.  \n訳: 議論は本日の議題にある問題だけに絞ってください。  \n\n・confine one's remarks to 〈対象〉  \n用途: 発言する内容を特定の対象に限る。  \n例: She confined her remarks to the financial risks of the proposal.  \n訳: 彼女は発言をその提案の財務上のリスクに限定した。  \n\n・confine oneself to 〈名詞・doing〉  \n用途: 自分が扱う話題や行う活動を意識的に一つの範囲へ絞る。  \n例: In this chapter, I will confine myself to examining the short-term effects.  \n訳: この章では、短期的な影響の検討だけに対象を絞る。  \n\n・be confined to 〈場所・集団〉  \n用途: 問題、特徴、現象などが特定の場所や集団だけに見られることを表す。  \n例: The shortage is not confined to rural areas.  \n訳: その不足は農村部だけに限られた問題ではない。  \n\n・confine 〈物質・作用〉 to 〈区域・装置〉  \n用途: 物質、熱、火、プラズマなどが外へ広がらないよう一定の区域内に保つ。  \n例: The magnetic field confines the plasma to the center of the chamber.  \n訳: その磁場はプラズマを容器の中心部に閉じ込める。  \n\n【語法・注意】基本形は confine A to B であり、to の後ろには名詞または動名詞を置く。場所の内部へ物理的に閉じ込める語義2では confine someone in a cell のように in も使う。confine oneself to は話題・活動の自主的な限定によく使うが、confine oneself to one's room のように場所を示す語が続けば、物理的に自分をその場所にとどめる意味にもなる。  \n\n【類義語】\n\n・limit  \n定義: 数量、範囲、程度、時間などに限度を設ける。  \n頻度: 〈9/10〉  \n違い: limit は最も広く中立的で、上限を設ける場合にも使う。confine は対象をある境界の内側にとどめ、外へ広げないイメージが強い。  \n例: The policy limits each application to two pages.  \n訳: その方針では各申請書を2ページまでに制限している。  \n\n・restrict  \n定義: 規則、条件、権限などによって範囲や自由を制限する。  \n頻度: 〈8/10〉  \n違い: restrict は許可・利用・行動への制約を広く表す。confine A to B は、AがBの外へ及ばないという境界を特に示す。  \n例: Access is restricted to authorized staff.  \n訳: 立ち入りは権限のある職員に制限されている。  \n\n・circumscribe  \n定義: 活動、権限、可能性などの範囲を狭く限定する。  \n頻度: 〈3/10〉  \n違い: circumscribe は非常に硬い語で、抽象的な権限・選択肢・行動範囲が制約される文脈に多い。confine の方が一般的で、具体的な場所にも使える。  \n例: The constitution circumscribes the powers of the executive.  \n訳: 憲法は行政府の権限の範囲を限定している。  \n\n【反意語】\n\n・broaden  \n定義: 話題、活動、対象などの範囲を広げる。  \n頻度: 〈7/10〉  \n違い: 範囲を狭く限定する confine と、同じ範囲軸上で外側へ広げる方向の対立をなす。  \n例: The committee broadened the inquiry to include safety concerns.  \n訳: 委員会は安全上の懸念も含めるよう調査範囲を広げた。  \n\n・extend  \n定義: 対象となる範囲、期間、適用先などをさらに先まで広げる。  \n頻度: 〈8/10〉  \n違い: confine A to B がAの到達範囲をB内に止めるのに対し、extend A to B はAの到達範囲をBまで広げる。  \n例: The program was extended to smaller communities.  \n訳: その制度はより小さな地域にも拡大された。  \n\n2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する\n\n【日本語訳・定義】人や動物を、部屋、施設、囲い、刑務所などの外へ自由に出られないようにする。物理的な障壁、命令、拘禁などによる移動の制限を表す。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】一般語。ニュース、法律・刑事、軍事、動物管理の文脈でよく使われる。  \n\n【文法パターン】confine someone/an animal in 〈閉鎖場所〉＝人・動物を～の中に閉じ込める／confine someone/an animal to 〈場所〉＝人・動物を～から出られないようにする／be confined in 〈施設・部屋〉＝～に収容・拘束されている／be confined to quarters＝兵舎・自室待機を命じられている  \n\n【コロケーション】\n\n・confine someone in a cell  \n用途: 人を独房などの閉鎖された空間から出られないようにする。  \n例: The prisoner was confined in a windowless cell for several days.  \n訳: その囚人は数日間、窓のない独房に拘禁された。  \n\n・confine an animal to 〈囲い・ケージ〉  \n用途: 動物が指定された囲いの外へ出ないようにする。  \n例: The injured bird was temporarily confined to a large enclosure.  \n訳: けがをした鳥は一時的に大きな囲いの中に閉じ込められた。  \n\n・keep 〈人・動物〉 confined  \n用途: 人や動物を外へ出られない状態に保つ。  \n例: The order kept the soldiers confined to their barracks overnight.  \n訳: その命令により兵士たちは一晩、兵舎から出られなかった。  \n\n・be confined to quarters  \n用途: 軍人などが処罰・命令により兵舎や指定場所から出ないよう命じられた状態を表す。  \n例: He was confined to quarters for disobeying the order.  \n訳: 彼は命令に従わなかったため、兵舎待機を命じられた。  \n\n【語法・注意】この語義では能動形と受動形の両方を使う。in は容器・部屋・施設の「内部」を、to は移動可能な「範囲」を示す。  \n\n【類義語】\n\n・imprison  \n定義: 人を刑務所などに入れて自由を奪う。  \n頻度: 〈6/10〉  \n違い: imprison は刑罰・政治的拘禁など人の収監を中心とする。confine は人以外の動物や、刑務所以外の限定された場所にも使える。  \n例: The regime imprisoned several opposition leaders.  \n訳: その政権は複数の反対派指導者を投獄した。  \n\n・detain  \n定義: 当局などが人を一定時間引き留め、立ち去れないようにする。  \n頻度: 〈7/10〉  \n違い: detain は一時的な身柄拘束や事情聴取のための留置に焦点がある。confine は場所の境界内に置かれる状態を強く示す。  \n例: Police detained the suspect for questioning.  \n訳: 警察は事情聴取のため容疑者を拘束した。  \n\n【反意語】\n\n・release  \n定義: 拘束・収容されている人や動物を自由にする。  \n頻度: 〈8/10〉  \n違い: 閉鎖場所内にとどめる confine に対し、そこから出ることを許す方向の対立をなす。  \n例: The authorities released the detainees the next morning.  \n訳: 当局は翌朝、被拘束者たちを解放した。  \n\n・free  \n定義: 束縛、監禁、拘束などから自由にする。  \n頻度: 〈8/10〉  \n違い: confine が移動の自由を奪うのに対し、free はその拘束自体を取り除く。release より広く、物理的・制度的・比喩的拘束に使える。  \n例: The rescue team freed the animals from the locked shed.  \n訳: 救助隊は鍵のかかった小屋から動物たちを解放した。  \n\n3. 【他動詞・通常受動】～を寝床・自宅などにとどめる\n\n【日本語訳・定義】病気、けが、身体状態などが原因で、人がベッド、自宅、病室など限られた場所から動けない、または外出できない状態にする。原因を主語にする能動文と、本人を主語にした be confined to の形がある。  \n\n【頻度】〈6/10〉  \n\n【レジスター/領域】一般語・医療関連。病状や回復期間を述べるやや硬い表現。  \n\n【文法パターン】〈病気・けが・身体状態〉 confine someone to 〈bed/home/a room〉＝病気などが人を～から動けない状態にする／someone be confined to bed/home＝人が病気などで寝床・自宅から動けない／someone be confined to bed with 〈病気〉＝病気により寝床にとどまっている  \n\n【コロケーション】\n\n・be confined to bed  \n用途: 病気やけがのため起きて普段どおり活動できず、寝床にとどまる。  \n例: She was confined to bed for a week with a severe infection.  \n訳: 彼女は重い感染症のため1週間、寝床から起きられなかった。  \n\n・be confined to one's home  \n用途: 健康上の理由などで外出できず、自宅にとどまる。  \n例: After the operation, he was confined to his home for several days.  \n訳: 手術後、彼は数日間、自宅から出られなかった。  \n\n・〈病気・けが〉 confine someone to 〈場所〉  \n用途: 病気やけがを原因として、人の行動範囲が特定の場所に限られることを表す。  \n例: A knee injury confined her to the apartment for most of the winter.  \n訳: 膝のけがのため、彼女は冬の大半をアパートから出られずに過ごした。  \n\n・be temporarily confined to 〈場所〉  \n用途: 限られた期間だけ、健康上の理由で一定の場所にとどまることを表す。  \n例: He is temporarily confined to his room by complications from the operation.  \n訳: 彼は手術の合併症のため、一時的に自室から出られない状態にある。  \n\n【語法・注意】be confined to a wheelchair は従来から見られる表現だが、車いすを人を閉じ込める物として否定的に描くため、不快・不適切と受け取られることがある。単に移動手段を述べるなら use a wheelchair または be a wheelchair user を用いる。be confined to bed は病気などで起きられない状態を表し、単にベッドで休む choose to stay in bed とは異なる。  \n\n【類義語】\n\n・be bedridden  \n定義: 病気、けが、高齢などで寝床から離れられない状態にある。  \n頻度: 〈5/10〉  \n違い: be bedridden は比較的長い・重い状態を表しやすい形容詞表現である。be confined to bed は一時的な病気にも使える。  \n例: He was bedridden for months after the stroke.  \n訳: 彼は脳卒中の後、何か月も寝たきりだった。  \n\n・be housebound  \n定義: 身体状態などのため自宅から外出することが難しい。  \n頻度: 〈4/10〉  \n違い: be housebound は自宅の外へ出にくい状態そのものを表す。be confined to one's home は原因によって行動範囲が自宅内に限られたことを描く。  \n例: The service delivers meals to older people who are housebound.  \n訳: そのサービスは外出困難な高齢者に食事を届ける。  \n\n・be restricted to 〈場所・活動〉  \n定義: 許可や身体状態などにより、場所・活動の範囲が限られている。  \n頻度: 〈7/10〉  \n違い: be restricted to は原因を問わない中立的な制限表現である。be confined to は移動できない、または外へ出られないという強い制約を示しやすい。  \n例: During recovery, she was restricted to light indoor activities.  \n訳: 回復中、彼女の活動は屋内での軽いものに限られた。  \n\n4. 【過去分詞由来の形容詞 confined】狭く囲まれた、限られた\n\n【日本語訳・定義】confined の形で、空間や区域が壁や境界に囲まれて狭い、または内部で動ける余地が少ないことを表す。単に面積が小さいだけでなく、閉鎖性や動きにくさを含みやすい。  \n\n【頻度】〈6/10〉  \n\n【レジスター/領域】一般語。confined space は日常的説明のほか、労働安全の専門用語としても使われる。  \n\n【文法パターン】a confined 〈space/area/place〉＝狭く囲まれた空間・区域／in confined 〈conditions/quarters〉＝狭く限られた環境で／feel confined＝閉じ込められたように感じる  \n\n【コロケーション】\n\n・a confined space  \n用途: 壁や境界に囲まれ、動きや出入りが制限されやすい空間を表す。  \n例: The machine should not be operated in a confined space without adequate ventilation.  \n訳: その機械は、十分な換気のない閉鎖空間で作動させるべきではない。  \n\n・in confined quarters  \n用途: 人が動ける余地の少ない狭い居住・作業場所にいることを表す。  \n例: The crew lived in confined quarters during the voyage.  \n訳: 乗組員は航海中、狭い居住区で暮らした。  \n\n・work in confined conditions  \n用途: 動作や移動の余地が限られた環境で作業する。  \n例: The technicians had to work in confined conditions beneath the stage.  \n訳: 技術者たちは舞台の下の狭い環境で作業しなければならなかった。  \n\n・a confined interior  \n用途: 内部が囲まれて狭く、動ける余地が少ないことを表す。  \n例: The vehicle has a confined interior with little room to move.  \n訳: その車両の内部は狭く、動ける余地がほとんどない。  \n\n【語法・注意】confined space は一般には狭く囲まれた空間を表す。米国 OSHA の労働安全上の定義では、出入りが制限され、継続的な在室を目的に設計されていないことなども要件になるため、小さい部屋がすべて専門上の confined space になるわけではない。be confined to 〈場所・範囲〉は動詞 confine の受動形で「～に限定・拘束されている」、a confined space は形容詞 confined が名詞を修飾して「狭く囲まれた空間」である。  \n\n【類義語】\n\n・enclosed  \n定義: 壁、柵、覆いなどによって周囲を囲まれた。  \n頻度: 〈7/10〉  \n違い: enclosed は囲いの存在を表すが、狭さや窮屈さは必須ではない。confined は空間や動きが限られる含みを持ちやすい。  \n例: The garden is surrounded by an enclosed walkway.  \n訳: その庭は囲われた通路に取り囲まれている。  \n\n・cramped  \n定義: 人や物に対して利用できる空間が足りず、窮屈な。  \n頻度: 〈6/10〉  \n違い: cramped は狭さによる不快さを直接強調する。confined は境界に囲まれ、動きが制限される構造に焦点がある。  \n例: Four people shared a cramped cabin.  \n訳: 4人が窮屈な船室を共有した。  \n\n・restricted  \n定義: 利用、移動、範囲などが制限された。  \n頻度: 〈7/10〉  \n違い: restricted は規則や条件による抽象的制限にも広く使う。confined は特に空間的な閉鎖性を示しやすい。  \n例: The equipment operates in a restricted area.  \n訳: その装置は立ち入り制限区域で稼働している。  \n\n【反意語】\n\n・spacious  \n定義: 人や物がゆったり動ける十分な空間がある。  \n頻度: 〈7/10〉  \n違い: 動ける余地が少ない confined と、空間に十分な余裕がある spacious は広さ・窮屈さの軸で対立する。  \n例: The new cabin is bright and spacious.  \n訳: 新しい船室は明るく広々としている。  \n\n・open  \n定義: 閉鎖されず、周囲や上部が広く開けている。  \n頻度: 〈9/10〉  \n違い: 境界に囲まれた confined に対し、open は閉鎖性が少なく外へ開かれた状態を表す。文脈によっては広さではなく出入り可能性の対立になる。  \n例: We moved the meeting to an open area outside.  \n訳: 私たちは会議を屋外の開けた場所に移した。  \n\n5. 【名詞・通常複数・格式／文学的】境界、範囲、領域\n\n【日本語訳・定義】通常 confines の形で、場所・組織・分野などの外縁をなす境界、またはその境界に囲まれた内部の領域を表す。  \n\n【頻度】〈4/10〉  \n\n【レジスター/領域】格式的・文学的。within/beyond/outside the confines of の形で、抽象的・物理的な範囲を述べる文章に使われる。  \n\n【文法パターン】within the confines of 〈場所・制度・分野〉＝～の範囲内で／beyond the confines of 〈場所・制度・分野〉＝～の境界を越えて／outside the confines of 〈場所・制度・分野〉＝～の範囲外で／the narrow confines of 〈場所・枠組み〉＝～という狭い範囲  \n\n【コロケーション】\n\n・within the confines of 〈場所・制度〉  \n用途: 物理的または制度的な境界の内側にあることを表す。  \n例: The negotiations took place within the confines of the embassy.  \n訳: 交渉は大使館の敷地内で行われた。  \n\n・beyond the confines of 〈場所・分野〉  \n用途: 場所や分野の既存の境界を越えて及ぶことを表す。  \n例: Her influence extended far beyond the confines of the university.  \n訳: 彼女の影響力は大学の枠をはるかに越えて広がった。  \n\n・outside the confines of 〈制度・枠組み〉  \n用途: 制度や枠組みが定める範囲の外側にあることを表す。  \n例: The group continued its work outside the confines of the formal organization.  \n訳: そのグループは正式な組織の枠外でも活動を続けた。  \n\n・the narrow confines of 〈場所・枠組み〉  \n用途: 物理的・抽象的な範囲が狭く、制約的であることを強調する。  \n例: The story moves beyond the narrow confines of a family dispute.  \n訳: その物語は家族間の争いという狭い枠を越えて展開する。  \n\n【語法・注意】名詞では動詞と強勢位置が異なる。現代英語では通常 the confines of ... の複数形で使い、単数の a confine はまれである。confines は「境界線」そのものと「境界に囲まれた領域」の両方を表し得るため、within the confines of the park は通常「公園の区域内」、beyond the confines of the law は比喩的に「法の枠を越えて」と理解する。  \n\n【類義語】\n\n・bounds  \n定義: 許容範囲、領域、行動などの境界・限界。  \n頻度: 〈6/10〉  \n違い: bounds も通常複数で、out of bounds など定着表現が多い。confines は境界に囲まれた内部の領域まで意識させやすく、より格式的である。  \n例: The proposal falls outside the bounds of the agreement.  \n訳: その提案は合意の範囲外である。  \n\n・limits  \n定義: 範囲、能力、権限などがそれ以上及ばない境界。  \n頻度: 〈8/10〉  \n違い: limits は最も一般的で、数量的な上限にも使える。confines は場所・制度・分野を囲む境界や領域を表す格式的な語である。  \n例: The plan remains within the limits of the current budget.  \n訳: その計画は現在の予算の範囲内に収まっている。  \n\n・boundaries  \n定義: 場所、分野、関係などを内外に分ける境界。  \n頻度: 〈7/10〉  \n違い: boundaries は境界線や区分そのものに焦点がある。confines はその線で囲まれた範囲を含めて指すことがある。  \n例: The research crosses traditional disciplinary boundaries.  \n訳: その研究は従来の学問分野の境界を越えている。  ",
  "_output_metadata": {
    "schema_version": "final_review_v2",
    "stage": "final_review",
    "run_id": "blind-confine-20260906T073045Z-f9a3853d",
    "context_id": "blind-confine-context-20260906T073045Z-f9a3853d",
    "input_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
    "prompt_sha256": "af6ad4a77bbe63f6ace93a9080d138fa63efc2d40b6490cdd3bc70756783102a",
    "input_artifacts": [
      "entry_body",
      "sealed_final_blind",
      "pre_blind_resolution",
      "post_blind_resolution",
      "checker_recheck_manifest",
      "targeted_adjudications",
      "final_review_spec"
    ],
    "blind_output_sha256": "a5c53f22e734db025ef7fb6089566988be4631cc11c500c62545912ac57bff3e"
  },
  "pass_findings": {
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-confine-20260906T073045Z-f9a3853d",
    "context_id": "normal-confine-context-20260906T073045Z-f9a3853d",
    "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
    "prompt_sha256": "5178f5a14a9525317811a34e6cd307108436f4babc1299fcd2eb9031f28ba737",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-09-06T07:56:26.006279+00:00",
    "pass_outputs": [
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "translation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "confine-translation-agent",
          "same_model_as_generation": true
        },
        "findings": [
          {
            "taxonomy_id": "example_translation_alignment",
            "location": {
              "section": "collocations_examples",
              "line_start": 138,
              "line_end": 138,
              "exact_quote": "訳: けがをした鳥は一時的に大きな囲いの中で保護された。  "
            },
            "severity": "blocking",
            "rationale": "The English says that the injured bird was confined to an enclosure, i.e. kept from leaving it. 「保護された」recasts that restriction as protection and adds a beneficial purpose/evaluation not stated in the English, so it fails to preserve both the predicate and the affected participant's relation to the enclosure.",
            "evidence_link_ids": [],
            "suggested_direction": "Translate the confinement directly, for example 「けがをした鳥は一時的に大きな囲いの中に閉じ込められた」, without adding a protective purpose.",
            "id": "NR-translation-1"
          },
          {
            "taxonomy_id": "example_translation_alignment",
            "location": {
              "section": "collocations_examples",
              "line_start": 221,
              "line_end": 221,
              "exact_quote": "訳: 彼は回復するまで一時的に自室で過ごさなければならない。  "
            },
            "severity": "blocking",
            "rationale": "The English describes his current constrained state while he recovers; it does not assert a deontic obligation. 「過ごさなければならない」adds a must/requirement reading and 「回復するまで」presents recovery as the endpoint more categorically than while he recovers.",
            "evidence_link_ids": [],
            "suggested_direction": "Preserve the state and contemporaneous recovery clause, for example 「彼は回復中、一時的に自室から出られない状態にある」.",
            "id": "NR-translation-2"
          },
          {
            "taxonomy_id": "example_translation_alignment",
            "location": {
              "section": "lexical_relations",
              "line_start": 289,
              "line_end": 289,
              "exact_quote": "訳: その庭は屋根と壁のある通路に囲まれている。  "
            },
            "severity": "blocking",
            "rationale": "The English only characterizes the walkway as enclosed. The translation specifies that it has both a roof and walls, introducing concrete structural facts that enclosed does not entail and narrowing the adjective's meaning beyond the example.",
            "evidence_link_ids": [],
            "suggested_direction": "Use a non-specifying rendering such as 「その庭は囲われた通路に取り囲まれている」 so the enclosure is preserved without inventing its construction.",
            "id": "NR-translation-3"
          }
        ]
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "sense-structure",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "GPT-5",
          "ingested_by": "human",
          "agent_id": "confine-sense-agent",
          "same_model_as_generation": true
        },
        "findings": [
          {
            "taxonomy_id": "cross_section_internal_contradiction",
            "location": {
              "section": "word_formation",
              "line_start": 25,
              "line_end": 25,
              "exact_quote": "・confining（形容詞）— 自由な動きや活動を妨げる、窮屈な。物理的な狭さだけでなく、服装・役割・生活環境などの制約にも使う。  "
            },
            "severity": "blocking",
            "rationale": "主要な分詞形容詞 confining は、自由な動き・活動を妨げるという作用・評価を表し、結果状態を表す confined（語義4）とは中心意味と評価方向が異なる。しかし、この用法は語形成欄にしかなく、番号付き語義にもコアイメージの列挙枝にも収録先がない。主要な品詞転換を語形成欄だけに置く構成は、セクション横断で意味範囲が一致していない。",
            "evidence_link_ids": [],
            "suggested_direction": "confining の形容詞用法を独立した番号付き語義として追加し、コアイメージにも「人・物・環境が動きや活動を妨げ、窮屈に感じさせる」という対応枝を追加する。",
            "id": "NR-sense-structure-1"
          }
        ]
      },
      {
        "pass_id": "frame-relation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "confine-frame-agent",
          "same_model_as_generation": true
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
          "blind_request_sha256": "5def1e3cf8eef0d3e5e016fbe7c68964f4dfa8359e9cd80a72373fa6a22150d8",
          "recorded_at": "2026-09-06T00:47:49-07:00",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "confine-frame-agent",
            "same_model_as_generation": true
          },
          "axes": [
            {
              "item_id": "ant-7700f7ce4e98",
              "axis": "拘束",
              "relation_type": "方向",
              "reason": ""
            },
            {
              "item_id": "ant-cd0cd6b18ff8",
              "axis": "広さ",
              "relation_type": "程度",
              "reason": ""
            },
            {
              "item_id": "ant-c0dc5dadb561",
              "axis": "開放性",
              "relation_type": "状態",
              "reason": ""
            },
            {
              "item_id": "ant-2ff0cbbd0f84",
              "axis": "拘束",
              "relation_type": "方向",
              "reason": ""
            },
            {
              "item_id": "ant-feae1bb49aaa",
              "axis": "範囲",
              "relation_type": "方向",
              "reason": ""
            },
            {
              "item_id": "ant-5c13f3df07ec",
              "axis": "範囲",
              "relation_type": "方向",
              "reason": ""
            }
          ]
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
          "stage2_request_sha256": "007554e230e9b9087bb815b645a1be1180da5d00f13895bacef9efa2be9fef1e",
          "blind_record_sha256": "6720b8ad129a6d66692d8cc6e740190fc5e12648893d23a0a7b87d0baf520233",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "confine-frame-agent",
            "same_model_as_generation": true
          },
          "adjudications": [
            {
              "item_id": "ant-feae1bb49aaa",
              "flags": [],
              "rationale": "語義1は対象を一定の範囲内に限定することを中心義とし、broaden は同じ範囲軸で外側へ広げる逆方向の変化を表す。違い行も対立を否定・限定していない。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-5c13f3df07ec",
              "flags": [],
              "rationale": "語義1の到達・適用範囲を内側に止める confine と、範囲を先まで広げる extend は範囲軸上の方向対立である。違い行に自己否定はない。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-7700f7ce4e98",
              "flags": [],
              "rationale": "語義2は人・動物を拘束状態に置くことを表し、release はその拘束から外へ出ることを許すため、拘束軸上の方向対立になる。違い行に自己否定はない。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-2ff0cbbd0f84",
              "flags": [],
              "rationale": "語義2の confine は移動の自由を奪って拘束し、free はその拘束を除くので、拘束軸上の方向対立として成立する。適用範囲の広さに関する補足は対立自体を否定していない。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-cd0cd6b18ff8",
              "flags": [],
              "rationale": "語義4は空間が狭く動ける余地が少ないことを含み、spacious は十分な余地を表すため、広さ軸上の程度対立になる。違い行に自己否定はない。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-c0dc5dadb561",
              "flags": [],
              "rationale": "語義4は壁や境界による閉鎖性を明示し、open は閉鎖されず外へ開かれた状態を表すため、開放性軸上の状態対立になる。出入り可能性にも関わるという違い行の補足は、この対立を否定していない。",
              "suggested_direction": null,
              "f4_severity": null
            }
          ],
          "frame_findings": [
            {
              "taxonomy_id": "argument_slot_role_mismatch",
              "location": {
                "section": "frames",
                "line_start": 126,
                "line_end": 126,
                "exact_quote": "【文法パターン】confine someone/something in 〈閉鎖場所〉＝人・動物を～の中に閉じ込める／confine someone/something to 〈場所〉＝人・動物を～から出られないようにする／be confined in 〈施設・部屋〉＝～に収容・拘束されている／be confined to quarters＝兵舎・自室待機を命じられている  "
              },
              "severity": "blocking",
              "rationale": "語義2は対象を人・動物に限定し、右辺の説明と全コロケーションも人・動物だけを実現しているのに、二つの能動フレームが something を許して無生物対象まで同語義に取り込んでいる。物質・作用の物理的封じ込めは語義1に置かれており、slot の意味役割と語義区分が一致しない。",
              "evidence_link_ids": [],
              "suggested_direction": "語義2の目的語slotを someone/an animal に限定し、無生物を許すフレームは該当語義へ分離して完全フレーム化する。"
            },
            {
              "taxonomy_id": "lexical_relation_mislabel",
              "location": {
                "section": "lexical_relations",
                "line_start": 168,
                "line_end": 171,
                "exact_quote": "・enclose  \n定義: 物や場所の周囲を囲い、その内側に収める。  \n頻度: 〈6/10〉  \n違い: enclose は囲いを作ることに焦点があり、対象の自由を奪う含みは必須ではない。confine は外へ出られないという制限を前面に出す。  "
              },
              "severity": "blocking",
              "rationale": "この語義の confine は人・動物の移動の自由を奪うことが中心だが、提示された enclose の定義は物や場所を囲うことを中心とし、違い行も自由を奪う含みが必須でないと認めている。中心義が十分に重ならず、拘束の手段として関連する語を類義語扱いしている。",
              "evidence_link_ids": [],
              "suggested_direction": "語法・注意への対照表現としての移動"
            }
          ],
          "unrouted_observations": []
        },
        "aligned_at": "2026-09-06T07:59:03.669161+00:00",
        "findings": [
          {
            "taxonomy_id": "argument_slot_role_mismatch",
            "location": {
              "section": "frames",
              "line_start": 126,
              "line_end": 126,
              "exact_quote": "【文法パターン】confine someone/something in 〈閉鎖場所〉＝人・動物を～の中に閉じ込める／confine someone/something to 〈場所〉＝人・動物を～から出られないようにする／be confined in 〈施設・部屋〉＝～に収容・拘束されている／be confined to quarters＝兵舎・自室待機を命じられている  "
            },
            "severity": "blocking",
            "rationale": "語義2は対象を人・動物に限定し、右辺の説明と全コロケーションも人・動物だけを実現しているのに、二つの能動フレームが something を許して無生物対象まで同語義に取り込んでいる。物質・作用の物理的封じ込めは語義1に置かれており、slot の意味役割と語義区分が一致しない。",
            "evidence_link_ids": [],
            "suggested_direction": "語義2の目的語slotを someone/an animal に限定し、無生物を許すフレームは該当語義へ分離して完全フレーム化する。",
            "id": "NR-frame-relation-1"
          },
          {
            "taxonomy_id": "lexical_relation_mislabel",
            "location": {
              "section": "lexical_relations",
              "line_start": 168,
              "line_end": 171,
              "exact_quote": "・enclose  \n定義: 物や場所の周囲を囲い、その内側に収める。  \n頻度: 〈6/10〉  \n違い: enclose は囲いを作ることに焦点があり、対象の自由を奪う含みは必須ではない。confine は外へ出られないという制限を前面に出す。  "
            },
            "severity": "blocking",
            "rationale": "この語義の confine は人・動物の移動の自由を奪うことが中心だが、提示された enclose の定義は物や場所を囲うことを中心とし、違い行も自由を奪う含みが必須でないと認めている。中心義が十分に重ならず、拘束の手段として関連する語を類義語扱いしている。",
            "evidence_link_ids": [],
            "suggested_direction": "語法・注意への対照表現としての移動",
            "id": "NR-frame-relation-2"
          }
        ],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "confine-example-agent",
          "same_model_as_generation": true
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "pass_id": "example-attribution",
          "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
          "blind_request_sha256": "ba73ca7a3fb7fc8f81d5a3bb6dbd113c74b492a3c5ddcc1e6d3aa5c016ec70f1",
          "recorded_at": "2026-09-06T07:49:00Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "confine-example-agent",
            "same_model_as_generation": true
          },
          "attributions": [
            {
              "example_id": "ex-ab9dc4cef69c",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "the confines of the university",
                "beyond"
              ],
              "rationale": "Her influence extended far beyond the confines of the university. 複数名詞 confines が of the university と結び付き、越えられる境界・領域を表すため sense:005。競合する sense:001 は他動詞 confine が対象の範囲を限定する用法であり、この例の名詞句構造では成立しない。"
            },
            {
              "example_id": "ex-48d231fdefb7",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "within the confines of the embassy"
              ],
              "rationale": "The negotiations took place within the confines of the embassy. within と of the embassy に支配された複数名詞 confines が大使館の境界内の領域を表すため sense:005。競合する sense:004 は confined が空間を修飾する形容詞用法であり、定冠詞付き複数名詞のこの構造には当てはまらない。"
            },
            {
              "example_id": "ex-f6323709feaa",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "confines the plasma to the center of the chamber"
              ],
              "rationale": "The magnetic field confines the plasma to the center of the chamber. 磁場が plasma の存在範囲を chamber の center に限定する他動詞フレームなので sense:001。競合する sense:002 は移動の自由を奪われる人・動物を目的語に取るが、ここでは非生物の plasma の空間的分布を限定しており成立しない。"
            },
            {
              "example_id": "ex-19fbcd0bb31e",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "in confined conditions"
              ],
              "rationale": "The technicians had to work in confined conditions beneath the stage. confined が conditions を前置修飾し、作業時の狭く動きにくい環境を表すため sense:004。競合する sense:002 は人・動物を閉じ込める他動詞・受動の関係を必要とするが、ここでは人ではなく環境の性質を表している。"
            },
            {
              "example_id": "ex-9d35134efbf3",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "outside the confines of the formal organization"
              ],
              "rationale": "The group continued its work outside the confines of the formal organization. outside と of the formal organization に結び付く複数名詞 confines が組織の枠・領域を表すため sense:005。競合する sense:001 は動詞として活動等の範囲を限定する用法であり、ここでの名詞句には帰属しない。"
            },
            {
              "example_id": "ex-20027313c181",
              "classification": "ambiguous",
              "candidate_sense_ids": [
                "sense:002",
                "sense:003"
              ],
              "discriminating_terms": [],
              "rationale": "He is temporarily confined to his room while he recovers. be confined to + 部屋という見出し語の構文と結果状態だけでは、命令・拘束による sense:002 と、病気や身体状態による sense:003 の双方が自然に成立する。while he recovers は医療的解釈を促すが、回復中の人物が別理由で行動を制限される読みも排除せず、見出し語自体の意味関係から一意化できない。"
            },
            {
              "example_id": "ex-2b8d20bee0ac",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "A knee injury confined her",
                "to the apartment"
              ],
              "rationale": "A knee injury confined her to the apartment for most of the winter. 身体状態である A knee injury が原因主語となり、人を apartment にとどめるため sense:003。競合する sense:002 なら障壁・命令・拘禁主体による自由の剥奪が必要だが、ここではけがそのものが confine の原因項である。"
            },
            {
              "example_id": "ex-9577d742cfe7",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "confined to quarters",
                "for disobeying the order"
              ],
              "rationale": "He was confined to quarters for disobeying the order. 規律違反を理由に quarters への滞在を強制される拘束なので sense:002。競合する sense:003 は病気・けが・身体状態を原因とするが、同じ文では処分理由が明示され、その原因関係と両立しない。"
            },
            {
              "example_id": "ex-d5a6da675b13",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "was confined in a windowless cell"
              ],
              "rationale": "The prisoner was confined in a windowless cell for several days. 人が cell 内に拘禁され自由に出られない受動フレームなので sense:002。競合する sense:003 は身体状態により bed や home 等にとどまる用法だが、この例の拘禁場所 cell と in による収容関係はそれに合わない。"
            },
            {
              "example_id": "ex-afda08153c24",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "I felt confined in the tiny room"
              ],
              "rationale": "I felt confined in the tiny room after only a few hours. 人を意味する I が confined の状態主体で、in the room が閉じ込められた場所を示すため sense:002 の拘束状態として読むのが自然。競合する sense:004 は confined が空間・区域そのものの狭さを叙述・修飾する用法であり、人を主語にした felt confined には直接帰属しない。"
            },
            {
              "example_id": "ex-f36507fc3020",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "beyond the narrow confines of a family dispute"
              ],
              "rationale": "The story moves beyond the narrow confines of a family dispute. 複数名詞 confines が of a family dispute と結び付き、物語が越える抽象的な枠・領域を表すため sense:005。競合する sense:001 は動詞が対象をある範囲に限定する用法であり、この名詞句構造では成立しない。"
            },
            {
              "example_id": "ex-50ac6b0a7623",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "confine the discussion to the issues"
              ],
              "rationale": "Please confine the discussion to the issues on today's agenda. discussion を issues に限定する confine + 対象 + to + 範囲の能動フレームなので sense:001。競合する sense:002 は目的語が自由を制限される人・動物である必要があり、discussion の話題範囲を絞るこの関係には成立しない。"
            },
            {
              "example_id": "ex-32e4c7c37db5",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "in a confined space"
              ],
              "rationale": "The machine should not be operated in a confined space without adequate ventilation. confined が space を直接修飾し、換気上問題となる閉鎖的で狭い空間を表すため sense:004。競合する sense:002 は閉じ込められる人・動物を項に取るが、この例では space 自体の性質を表す。"
            },
            {
              "example_id": "ex-2132e30d65f2",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "After the operation",
                "was confined to his home"
              ],
              "rationale": "After the operation, he was confined to his home for several days. 手術後という身体的原因のもとで人が home から出られない状態を表すため sense:003。競合する sense:002 は命令・障壁・拘禁による拘束だが、同じ文が示す operation と home の原因・結果関係には適合しない。"
            },
            {
              "example_id": "ex-cb86d2ef723d",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "The order kept the soldiers confined",
                "to their barracks"
              ],
              "rationale": "The order kept the soldiers confined to their barracks overnight. The order が兵士の移動を barracks に強制的に制限するため sense:002。競合する sense:003 は病気・けが等の身体原因を必要とするが、ここでは命令が拘束の原因項として明示されている。"
            },
            {
              "example_id": "ex-cead63c39f1a",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "confine myself to examining the short-term effects"
              ],
              "rationale": "In this chapter, I will confine myself to examining the short-term effects. 再帰目的語 myself と to examining が、話し手が扱う範囲を意識的に限定する関係を作るため sense:001。競合する sense:002 なら人物の物理的移動を場所内に制限する必要があるが、補語は行為 examining であり物理的拘束ではない。"
            },
            {
              "example_id": "ex-d7b45d249ca7",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "confined her remarks to the financial risks"
              ],
              "rationale": "She confined her remarks to the financial risks of the proposal. remarks の内容範囲を financial risks に限定する能動フレームなので sense:001。競合する sense:002 は人・動物の移動を制限する用法であり、発言内容を目的語とするこの意味関係には成立しない。"
            },
            {
              "example_id": "ex-2ee60453400b",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "confined to bed",
                "with a severe infection"
              ],
              "rationale": "She was confined to bed for a week with a severe infection. 人が severe infection により bed から動けない状態を表すため sense:003。競合する sense:002 は命令・障壁等による拘束だが、to bed という結果場所と感染症という身体原因がその読みを排除する。"
            },
            {
              "example_id": "ex-4c6a8b45a115",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "lived in confined quarters"
              ],
              "rationale": "The crew lived in confined quarters during the voyage. confined が quarters を前置修飾し、居住区そのものが狭く閉鎖的であることを表すため sense:004。競合する sense:002 の confined to quarters なら人が quarters に拘束されるが、この例は in confined quarters で場所の性質を述べている。"
            },
            {
              "example_id": "ex-ed31d79c879d",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "The shortage is not confined to rural areas"
              ],
              "rationale": "The shortage is not confined to rural areas. shortage という現象の及ぶ範囲が rural areas に限定されないことを示すため sense:001。競合する sense:002 は移動を奪われる人・動物を対象とするが、非生物的現象 shortage の分布範囲を述べるこの例では成立しない。"
            },
            {
              "example_id": "ex-04a757c12fe1",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "The injured bird was temporarily confined",
                "to a large enclosure"
              ],
              "rationale": "The injured bird was temporarily confined to a large enclosure. 動物 bird が enclosure の外へ出られないようにされた受動フレームなので sense:002。競合する sense:003 は身体状態により人が bed・home 等にとどまる語義であり、injured という背景があっても、動物を enclosure に収容する見出し語の項関係は sense:002 に対応する。"
            }
          ]
        },
        "aligned_at": "2026-09-06T07:56:25.992725+00:00",
        "findings": [
          {
            "taxonomy_id": "example_sense_attribution_mismatch",
            "location": {
              "section": "collocations_examples",
              "line_start": 220,
              "line_end": 220,
              "exact_quote": "例: He is temporarily confined to his room while he recovers.  "
            },
            "severity": "blocking",
            "rationale": "段階1でsense:002, sense:003が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
            "evidence_link_ids": [],
            "suggested_direction": "判別語の追加",
            "id": "NR-example-attribution-1"
          },
          {
            "taxonomy_id": "example_sense_attribution_mismatch",
            "location": {
              "section": "collocations_examples",
              "line_start": 277,
              "line_end": 277,
              "exact_quote": "例: I felt confined in the tiny room after only a few hours.  "
            },
            "severity": "blocking",
            "rationale": "段階1の最も自然な帰属はsense:002だが、実際の所属はsense:004である。",
            "evidence_link_ids": [],
            "suggested_direction": "語義ブロック間の移動",
            "id": "NR-example-attribution-2"
          }
        ],
        "unrouted_observations": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "qualification",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "confine-qualification-agent",
          "same_model_as_generation": true
        },
        "findings": [
          {
            "taxonomy_id": "absolute_scope_counterexample",
            "location": {
              "section": "usage_notes",
              "line_start": 77,
              "line_end": 77,
              "exact_quote": "confine oneself to は「自分を物理的に閉じ込める」ではなく、通常「話題・活動を自分で限定する」という再帰構文である。"
            },
            "severity": "blocking",
            "rationale": "再帰形の物理的用法を一律に否定しているが、文脈によっては confine oneself to one's room のように、自らを物理的な場所にとどめる意味でも成立する。「通常」が後半の典型用法を限定していても、前半の「ではなく」という絶対的な排除は反例によって成り立たない。",
            "evidence_link_ids": [],
            "suggested_direction": "再帰形は典型的には話題・活動の自主的な限定を表すが、場所を補語に取る場合は物理的に自分をその場所にとどめる意味にもなり得る、と適用範囲を修正する。",
            "id": "NR-qualification-1"
          }
        ]
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "pronunciation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "confine-pronunciation-agent",
          "same_model_as_generation": true
        },
        "findings": []
      },
      {
        "pass_id": "evidence",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "confine-evidence-agent",
          "same_model_as_generation": true
        },
        "findings": [
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "pronunciation",
              "line_start": 15,
              "line_end": 15,
              "exact_quote": "動詞の三人称単数形 confines は /kənˈfaɪnz/、過去形・過去分詞 confined は /kənˈfaɪnd/、-ing形 confining は /kənˈfaɪnɪŋ/ と発音する。"
            },
            "severity": "blocking",
            "rationale": "F-005、F-011、F-014 は基本形の動詞・名詞の発音と強勢を支持するが、各屈折形の完全な IPA は示していない。F-009 と F-010 は綴り上の屈折形を列挙するだけで、/z/、/d/、/ɪŋ/ を含む発音主張を直接支持しない。",
            "evidence_link_ids": [
              "F-005",
              "F-009",
              "F-010",
              "F-011",
              "F-014"
            ],
            "suggested_direction": "屈折形の発音を直接示す根拠に差し替えるか、根拠がある基本形の発音と強勢対立だけに主張を限定する。",
            "id": "NR-evidence-1"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "etymology",
              "line_start": 19,
              "line_end": 19,
              "exact_quote": "名詞はフランス語の複数形 confins「境界」などを経て英語に入った。finite「有限の」、final「最後の」もラテン語 finis と関係する。"
            },
            "severity": "blocking",
            "rationale": "唯一の語源 fact F-015 は動詞 confine の French confiner と Latin confinis/com + finis の系譜だけを記録している。名詞の French confins 経由説および finite・final との関係は、固定された fact や source_supports に含まれない。",
            "evidence_link_ids": [
              "F-015"
            ],
            "suggested_direction": "F-015 が直接支持する動詞の系譜に限定するか、名詞史と関連語を明示する別の語源根拠へ差し替える。",
            "id": "NR-evidence-2"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "word_formation",
              "line_start": 23,
              "line_end": 23,
              "exact_quote": "文脈によって物理的拘束、病気による外出不能、限定された環境などを表す。"
            },
            "severity": "blocking",
            "rationale": "F-016 は confinement を confine される行為・状態および restraint として支持するが、病気による外出不能や限定された環境という列挙された適用範囲までは示していない。",
            "evidence_link_ids": [
              "F-016"
            ],
            "suggested_direction": "act/state of being confined 程度に限定するか、各文脈を直接例証する根拠を付ける。",
            "id": "NR-evidence-3"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "word_formation",
              "line_start": 25,
              "line_end": 25,
              "exact_quote": "confining（形容詞）— 自由な動きや活動を妨げる、窮屈な。物理的な狭さだけでなく、服装・役割・生活環境などの制約にも使う。"
            },
            "severity": "blocking",
            "rationale": "C-009/F-010 が支持するのは confining が規則的な現在分詞であることだけであり、独立した形容詞語義や服装・役割・生活環境への適用範囲ではない。",
            "evidence_link_ids": [
              "F-010"
            ],
            "suggested_direction": "現在分詞としての記述に限定するか、形容詞語義と各適用範囲を直接記載する辞書根拠へ差し替える。",
            "id": "NR-evidence-4"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "word_formation",
              "line_start": 26,
              "line_end": 26,
              "exact_quote": "一般語としては limited や restricted ほど頻繁ではない。"
            },
            "severity": "blocking",
            "rationale": "F-017 は unconfined の意味と形成のみを支持し、limited・restricted との相対頻度を扱っていない。頻度比較に対応する corpus fact もない。",
            "evidence_link_ids": [
              "F-017"
            ],
            "suggested_direction": "頻度比較を削除するか、比較可能なコーパス根拠を付ける。",
            "id": "NR-evidence-5"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "sense_structure",
              "line_start": 42,
              "line_end": 42,
              "exact_quote": "対象がすでにその範囲に収まっていることを述べる受動形と、話し手が意識的に扱う範囲を絞る能動形・再帰形の両方がよく使われる。"
            },
            "severity": "blocking",
            "rationale": "F-002 は受動形・再帰形・object + to の存在を例示するが、『両方がよく使われる』という使用頻度・分布までは示さない。",
            "evidence_link_ids": [
              "F-002"
            ],
            "suggested_direction": "構文が存在するという記述に限定し、頻度表現を外すか分布を示す根拠を追加する。",
            "id": "NR-evidence-6"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "sense_structure",
              "line_start": 120,
              "line_end": 120,
              "exact_quote": "本人の自由意思で滞在している場合には通常使わない。"
            },
            "severity": "blocking",
            "rationale": "F-003 と F-007 は閉鎖空間への拘束・収監の語義を支持するが、自由意思による滞在との対照を明示した usage constraint は提供していない。",
            "evidence_link_ids": [
              "F-003",
              "F-007"
            ],
            "suggested_direction": "直接支持される『自由に出られないようにする』までに限定するか、この語用制約を明示する根拠を付ける。",
            "id": "NR-evidence-7"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "sense_structure",
              "line_start": 193,
              "line_end": 193,
              "exact_quote": "原因を主語にする能動文も可能だが、本人を主語にした be confined to が特に多い。"
            },
            "severity": "blocking",
            "rationale": "F-004 は be confined to bed の疾病用法を支持するが、原因主語の能動構文や能動・受動間の相対頻度を示していない。",
            "evidence_link_ids": [
              "F-004"
            ],
            "suggested_direction": "be confined to bed の疾病用法に限定するか、原因主語構文と分布を直接示す根拠を追加する。",
            "id": "NR-evidence-8"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "sense_structure",
              "line_start": 323,
              "line_end": 323,
              "exact_quote": "現代の一般的な文章では単数形 confine より複数形 confines が圧倒的に普通である。"
            },
            "severity": "blocking",
            "rationale": "F-008 は noun を normally plural、F-013 は often plural とするため複数優勢は支持するが、『現代の一般的な文章』『圧倒的に普通』という強い分布主張までは支持しない。",
            "evidence_link_ids": [
              "F-008",
              "F-013"
            ],
            "suggested_direction": "『通常／しばしば複数形』に限定し、圧倒的という強度表現を外す。",
            "id": "NR-evidence-9"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frequency_register",
              "line_start": 44,
              "line_end": 46,
              "exact_quote": "【頻度】〈8/10〉  【レジスター/領域】一般語だが、日常会話より文章、ニュース、ビジネス、学術的説明でやや多い。"
            },
            "severity": "blocking",
            "rationale": "C-001/F-001・F-006・F-012 は語義を支持するだけで、8/10 の尺度、会話対文章の分布、ニュース・ビジネス・学術での相対頻度を扱っていない。",
            "evidence_link_ids": [
              "F-001",
              "F-006",
              "F-012"
            ],
            "suggested_direction": "頻度・レジスター主張を hold にするか、尺度の校正方法とコーパス根拠を付ける。",
            "id": "NR-evidence-10"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frequency_register",
              "line_start": 122,
              "line_end": 124,
              "exact_quote": "【頻度】〈7/10〉  【レジスター/領域】一般語。ニュース、法律・刑事、軍事、動物管理の文脈でよく使われる。"
            },
            "severity": "blocking",
            "rationale": "F-003 と F-007 は拘束語義を支持するが、7/10 の頻度や列挙された領域で『よく使われる』ことを示す頻度・register fact はない。",
            "evidence_link_ids": [
              "F-003",
              "F-007"
            ],
            "suggested_direction": "頻度・領域主張を削除するか、各領域を比較可能に示す根拠を付ける。",
            "id": "NR-evidence-11"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frequency_register",
              "line_start": 195,
              "line_end": 197,
              "exact_quote": "【頻度】〈6/10〉  【レジスター/領域】一般語・医療関連。病状や回復期間を述べるやや硬い表現。"
            },
            "severity": "blocking",
            "rationale": "F-004 は疾病により bed にとどまる用法を支持するが、6/10、医療領域での分布、または『やや硬い』という register 評価を支持しない。",
            "evidence_link_ids": [
              "F-004"
            ],
            "suggested_direction": "語義・構文だけに限定するか、頻度と register を直接評価できる根拠を付ける。",
            "id": "NR-evidence-12"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frequency_register",
              "line_start": 252,
              "line_end": 254,
              "exact_quote": "【頻度】〈6/10〉  【レジスター/領域】一般語。confined space は日常的説明のほか、労働安全の専門用語としても使われる。"
            },
            "severity": "blocking",
            "rationale": "F-018 は形容詞語義、F-019 は米国 OSHA の専門定義を支持するが、6/10 の頻度や日常的説明と専門領域にまたがる register 分布は示していない。",
            "evidence_link_ids": [
              "F-018",
              "F-019"
            ],
            "suggested_direction": "OSHA の枠組みにおける専門用法だけに限定し、頻度・一般領域の主張は別根拠が得られるまで hold にする。",
            "id": "NR-evidence-13"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frequency_register",
              "line_start": 325,
              "line_end": 327,
              "exact_quote": "【頻度】〈4/10〉  【レジスター/領域】格式的・文学的。within/beyond/outside the confines of の形で、抽象的・物理的な範囲を述べる文章に使われる。"
            },
            "severity": "blocking",
            "rationale": "F-008 と F-013 は複数名詞の意味および一部の前置詞句を支持するが、4/10 の尺度や『格式的・文学的』という register は固定 fact にない。",
            "evidence_link_ids": [
              "F-008",
              "F-013"
            ],
            "suggested_direction": "支持される複数名詞の意味と句型だけに限定し、頻度・register は対応根拠を付ける。",
            "id": "NR-evidence-14"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 199,
              "line_end": 199,
              "exact_quote": "someone be confined to 〈場所〉 with/by 〈病気・けが〉＝病気・けがにより～にとどまっている"
            },
            "severity": "blocking",
            "rationale": "疾病用法の C-004/F-004 は be confined to bed を支持するが、場所一般への拡張や with/by を伴う完全フレームは示していない。また grammar_pattern:003 はどの claim unit の article_target_ids にもない。",
            "evidence_link_ids": [
              "F-004"
            ],
            "suggested_direction": "直接支持される be confined to bed に限定するか、with/by を含む完全フレームを明示する根拠を付ける。",
            "id": "NR-evidence-15"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "usage_notes",
              "line_start": 77,
              "line_end": 77,
              "exact_quote": "×confine A in doing B のように範囲を示す前置詞を機械的に in に替えない。confine oneself to は「自分を物理的に閉じ込める」ではなく、通常「話題・活動を自分で限定する」という再帰構文である。受動形 be confined to は、否定や mainly、largely などと結び付き、「～だけに限られる／限られない」を表しやすい。"
            },
            "severity": "blocking",
            "rationale": "F-002 は to を伴う受動・再帰・目的語構文を例示するが、in doing を誤用とする否定証拠、再帰形の物理用法排除を含む『通常』の範囲、否定・mainly・largely との結び付きやすさを支持していない。",
            "evidence_link_ids": [
              "F-002"
            ],
            "suggested_direction": "確認済みの肯定フレームだけを提示し、誤用断定と分布主張は直接の用法根拠が得られるまで外す。",
            "id": "NR-evidence-16"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "usage_notes",
              "line_start": 150,
              "line_end": 150,
              "exact_quote": "imprison は人を刑務所に入れる法的・物理的な拘禁に焦点があり、動物や一時的な行動制限には使いにくい。confine は刑罰に限らず、命令や安全上の理由による拘束にも使える。"
            },
            "severity": "blocking",
            "rationale": "F-003 と F-007 は confine の拘束語義を支持するが、imprison との適用範囲の差、動物・一時的制限での使いにくさ、命令・安全理由までを比較する lexical-relation fact はない。usage_note:002 も claim unit の target に含まれない。",
            "evidence_link_ids": [
              "F-003",
              "F-007"
            ],
            "suggested_direction": "confine の直接支持された拘束語義に限定するか、imprison との比較を明示する辞書・用法根拠を付ける。",
            "id": "NR-evidence-17"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "usage_notes",
              "line_start": 280,
              "line_end": 280,
              "exact_quote": "労働安全上の専門用語では法域や制度ごとに定義・要件があるため、小さい部屋をすべて専門上の confined space と断定しない。"
            },
            "severity": "blocking",
            "rationale": "F-019 は米国 OSHA 枠組みの具体的要件と、単なる小ささでは足りないことを支持する。しかし単一法域の一次資料だけでは『法域や制度ごとに定義・要件がある』という法域間比較を直接支持しない。",
            "evidence_link_ids": [
              "F-019"
            ],
            "suggested_direction": "『米国 OSHA の枠組みでは』と法域を限定するか、複数法域・制度の定義差を示す根拠を追加する。",
            "id": "NR-evidence-18"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 84,
              "line_end": 84,
              "exact_quote": "limit は最も広く中立的で、上限を設ける場合にも使う。confine は対象をある境界の内側にとどめ、外へ広げないイメージが強い。"
            },
            "severity": "blocking",
            "rationale": "source inventory と claim_units には limit、restrict、circumscribe、broaden、extend の定義・頻度・confine との差を扱う fact や article target がない。語義1の lexical-relations 全体（81～115行）の比較主張は固定根拠から検証できない。",
            "evidence_link_ids": [],
            "suggested_direction": "語義1の類義語・反意語比較を hold にするか、各比較軸と頻度を直接支持する fact/link を作成する。",
            "id": "NR-evidence-19"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 157,
              "line_end": 157,
              "exact_quote": "imprison は刑罰・政治的拘禁など人の収監を中心とする。confine は人以外の動物や、刑務所以外の限定された場所にも使える。"
            },
            "severity": "blocking",
            "rationale": "source inventory と claim_units は confine 自体の拘束語義を支持するだけで、imprison、detain、enclose、release、free の定義・頻度・対比を扱わない。語義2の lexical-relations 全体（154～188行）に evidence link がない。",
            "evidence_link_ids": [],
            "suggested_direction": "語義2の語彙関係を hold にするか、各語の適用範囲と比較軸を直接支持する根拠を付ける。",
            "id": "NR-evidence-20"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 230,
              "line_end": 230,
              "exact_quote": "be bedridden は比較的長い・重い状態を表しやすい形容詞表現である。be confined to bed は一時的な病気にも使える。"
            },
            "severity": "blocking",
            "rationale": "F-004 は be confined to bed の疾病用法を支持するが、bedridden、housebound、be restricted to の意味・頻度・期間や強度の対比を扱わない。語義3の lexical-relations 全体（227～244行）に evidence link がない。",
            "evidence_link_ids": [
              "F-004"
            ],
            "suggested_direction": "語義3の類義表現比較を hold にするか、各表現の分布と意味差を直接支持する根拠を付ける。",
            "id": "NR-evidence-21"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 287,
              "line_end": 287,
              "exact_quote": "enclosed は囲いの存在を表すが、狭さや窮屈さは必須ではない。confined は空間や動きが限られる含みを持ちやすい。"
            },
            "severity": "blocking",
            "rationale": "F-018 は confined の形容詞語義を支持するが、enclosed、cramped、restricted、spacious、open の定義・頻度・対比は固定 fact にない。語義4の lexical-relations 全体（284～317行）に evidence link がない。",
            "evidence_link_ids": [
              "F-018"
            ],
            "suggested_direction": "語義4の類義語・反意語比較を hold にするか、各比較を直接支持する根拠を付ける。",
            "id": "NR-evidence-22"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 360,
              "line_end": 360,
              "exact_quote": "bounds も通常複数で、out of bounds など定着表現が多い。confines は境界に囲まれた内部の領域まで意識させやすく、より格式的である。"
            },
            "severity": "blocking",
            "rationale": "F-008 と F-013 は confines の複数性と意味を支持するが、bounds、limits、boundaries の定義・頻度・定着表現・register 差を扱わない。語義5の lexical-relations 全体（357～374行）に evidence link がない。",
            "evidence_link_ids": [
              "F-008",
              "F-013"
            ],
            "suggested_direction": "語義5の類義語比較を hold にするか、各語の register と意味範囲を直接比較する根拠を付ける。",
            "id": "NR-evidence-23"
          }
        ]
      }
    ],
    "checker_reviewers": {
      "translation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "confine-translation-agent",
        "same_model_as_generation": true
      },
      "sense-structure": {
        "mode": "handoff",
        "declared_model": "GPT-5",
        "ingested_by": "human",
        "agent_id": "confine-sense-agent",
        "same_model_as_generation": true
      },
      "frame-relation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "confine-frame-agent",
        "same_model_as_generation": true
      },
      "example-attribution": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "confine-example-agent",
        "same_model_as_generation": true
      },
      "qualification": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "confine-qualification-agent",
        "same_model_as_generation": true
      },
      "pronunciation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "confine-pronunciation-agent",
        "same_model_as_generation": true
      },
      "evidence": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "confine-evidence-agent",
        "same_model_as_generation": true
      }
    },
    "independent_candidates": [],
    "summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency."
  },
  "cold_review": {
    "agent_id": "confine-cold-agent",
    "summary": "問題候補5件。とくに、同綴りの動詞三単現 confines と通常複数で使う名詞 confines の発音差が本文横断で明示されず、学習者が名詞まで動詞と同じ後半強勢で読むおそれがある。また、自由意思による物理的な自己限定をほぼ排除する説明、見出し語 confine の語義として派生形容詞 confined を並べる品詞上の境界、語源説明における歴史的意味と現代的コアイメージの混同、動物の例文の訳への非含意情報の追加がある。",
    "findings": [
      {
        "id": "CR-001",
        "location": "発音記号／語義5の定義・語法",
        "severity": "medium",
        "description": "実際には通常複数形で現れる名詞 confines の発音が示されず、同じ綴りの動詞三人称単数形 confines の発音だけが明示されている。",
        "reason": "本文自身が「現代の一般的な文章では単数形 confine より複数形 confines が圧倒的に普通である。」と説明している一方、発音欄では名詞の単数形と動詞の confines しか扱っていない。名詞複数形は名詞の第1音節強勢を保つのに対し、動詞形は第2音節強勢であり、同綴りの対照こそ学習上重要である。現状では、読者が頻出する名詞 confines を、直後に明記された動詞形 /kənˈfaɪnz/ と誤って一般化し得る。",
        "suggested_direction": "名詞の実用上中心となる複数形 confines の米英発音を、動詞三単現 confines と明示的に対比して追記する。",
        "scope_anchors": [
          {
            "id": "CR-001-A",
            "exact_quote": "低頻度の名詞は、米: /ˈkɑːnfaɪn/｜英: /ˈkɒnfaɪn/ で、第1音節に主強勢が移り、第1音節の母音にも米英差がある。",
            "location_hint": "「発音記号」第1段落"
          },
          {
            "id": "CR-001-B",
            "exact_quote": "動詞の三人称単数形 confines は /kənˈfaɪnz/、過去形・過去分詞 confined は /kənˈfaɪnd/、-ing形 confining は /kənˈfaɪnɪŋ/ と発音する。",
            "location_hint": "「発音記号」第1段落"
          },
          {
            "id": "CR-001-C",
            "exact_quote": "現代の一般的な文章では単数形 confine より複数形 confines が圧倒的に普通である。",
            "location_hint": "語義5「日本語訳・定義」"
          },
          {
            "id": "CR-001-D",
            "exact_quote": "現代英語では通常 the confines of ... の複数形で使い、単数の a confine はまれである。",
            "location_hint": "語義5「語法・注意」"
          }
        ]
      },
      {
        "id": "CR-002",
        "location": "語義1・語義2の定義と語法",
        "severity": "medium",
        "description": "自由意思による物理的な自己限定には confine を通常使わない、confine oneself to は通常物理的意味ではない、という説明が強すぎる。",
        "reason": "本文は「confine oneself to は「自分を物理的に閉じ込める」ではなく、通常「話題・活動を自分で限定する」という再帰構文である。」と述べるが、He confined himself to his room/the house のように、人が自ら一定の場所から出ないようにする物理的・場所的な再帰用法も成立する。したがって、非再帰で他者を閉じ込める典型用法と、話題・活動を限定する再帰用法の傾向を説明すること自体は有益だが、自由意思と物理的用法を結び付けて排除するような書き方は反例を処理できず、学習者に誤った構文制約を一般化させる。",
        "suggested_direction": "「本人の自由意思で単に滞在しているだけなら通常使わない」と限定し、confine oneself to a room/the house のような意図的な自己隔離・自己限定では物理的用法も可能だと明示する。語義1の注意も「話題・活動の意味が多いが、場所を目的語に取れば物理的意味もある」と改める。",
        "scope_anchors": [
          {
            "id": "CR-002-A",
            "exact_quote": "confine oneself to は「自分を物理的に閉じ込める」ではなく、通常「話題・活動を自分で限定する」という再帰構文である。",
            "location_hint": "語義1「語法・注意」"
          },
          {
            "id": "CR-002-B",
            "exact_quote": "物理的な障壁、命令、拘禁などによる移動の制限を表し、本人の自由意思で滞在している場合には通常使わない。",
            "location_hint": "語義2「日本語訳・定義」"
          }
        ]
      },
      {
        "id": "CR-003",
        "location": "語義4およびコアイメージ",
        "severity": "medium",
        "description": "見出し語 confine 自体に形容詞用法があるかのように語義4を並べているが、説明対象は派生・分詞形の confined である。",
        "reason": "本文は語形成欄では confined を別個の形容詞として正しく示し、語義4の定義本文でも「confined の形で、空間や区域が壁や境界に囲まれて狭い、または内部で動ける余地が少ないことを表す。」と認めている。それにもかかわらず、confine の番号付き語義として単に「【形容詞】」と掲げ、コアイメージでも無標で「形容詞では」と述べるため、学習者が裸形 confine を形容詞として使える（たとえば a confine space）と誤解し得る。語義と派生語の境界が不統一である。",
        "suggested_direction": "語義4の見出しを「【過去分詞由来の形容詞 confined】」などと明示するか、番号付きの confine の語義から外して語形成欄の confined に統合する。コアイメージでも形容詞形が confined であることを明記する。",
        "scope_anchors": [
          {
            "id": "CR-003-A",
            "exact_quote": "・confined（形容詞）— 狭く囲まれた、限られた。単なる過去分詞としての受動用法と、confined space のような形容詞用法がある。",
            "location_hint": "「語形成」"
          },
          {
            "id": "CR-003-B",
            "exact_quote": "形容詞ではその結果の状態や窮屈さを、名詞では境界そのものを表す。",
            "location_hint": "「コアイメージ」第1段落"
          },
          {
            "id": "CR-003-C",
            "exact_quote": "4. 【形容詞】狭く囲まれた、限られた",
            "location_hint": "語義4見出し"
          },
          {
            "id": "CR-003-D",
            "exact_quote": "confined の形で、空間や区域が壁や境界に囲まれて狭い、または内部で動ける余地が少ないことを表す。",
            "location_hint": "語義4「日本語訳・定義」"
          }
        ]
      },
      {
        "id": "CR-004",
        "location": "語源",
        "severity": "low",
        "description": "ラテン語要素の説明から「境界の内側に置く」を直接的な語源上の意味として導いており、祖語義と現代語義を混同している。",
        "reason": "「動詞は中期フランス語 confiner「境を接する、限界内にとどめる」から英語に入り、さらにラテン語 confinis「境を接する」にさかのぼる。」と本文が直前に示すとおり、ラテン語 confinis の意味は「境を接する」であり、con-「共に」＋finis「境界」から直接得られるのも「境界を共有する／隣接する」という関係である。「境界の内側に置く」は現代の動詞用法をまとめる教育的コアイメージとしては機能するが、語源段落で語構成から直結した歴史的な意味の核のように述べると、意味発達を逆投影することになる。",
        "suggested_direction": "語源では「境界を共有する・隣接する」から「境界を定める／その内にとどめる」へ発達した、と段階を分ける。「境界の内側に置く」は現代用法を整理するコアイメージまたは覚え方だと位置付ける。",
        "scope_anchors": [
          {
            "id": "CR-004-A",
            "exact_quote": "動詞は中期フランス語 confiner「境を接する、限界内にとどめる」から英語に入り、さらにラテン語 confinis「境を接する」にさかのぼる。",
            "location_hint": "「語源」第1段落"
          },
          {
            "id": "CR-004-B",
            "exact_quote": "con-「共に」と finis「境界、終わり」が結び付いた語で、「境界の内側に置く」という意味の核が、現代の「範囲を限る」「閉じ込める」につながった。",
            "location_hint": "「語源」第1段落"
          }
        ]
      },
      {
        "id": "CR-005",
        "location": "語義2のコロケーション「confine an animal to 〈囲い・ケージ〉」",
        "severity": "low",
        "description": "例文の日本語訳が、原文にない「保護された」という肯定的な目的・評価を付け加えている。",
        "reason": "「例: The injured bird was temporarily confined to a large enclosure.」が表すのは、その鳥の行動範囲が一時的に囲い内へ制限されたという事実であり、それが保護目的だったとは英文だけからは決まらない。訳が「保護された」とすると、confine 自体に保護・救護の含意があるかのように学習者が誤解し得る。",
        "suggested_direction": "「そのけがをした鳥は一時的に大きな囲いの中に入れられていた／囲いから出られないようにされていた」など、目的を補わず制限状態を訳す。",
        "scope_anchors": [
          {
            "id": "CR-005-A",
            "exact_quote": "例: The injured bird was temporarily confined to a large enclosure.",
            "location_hint": "語義2「コロケーション」"
          },
          {
            "id": "CR-005-B",
            "exact_quote": "訳: けがをした鳥は一時的に大きな囲いの中で保護された。",
            "location_hint": "語義2「コロケーション」"
          }
        ]
      }
    ],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "confine-cold-agent",
      "same_model_as_generation": true
    },
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-confine-20260906T073045Z-f9a3853d",
    "context_id": "cold-confine-context-20260906T073045Z-f9a3853d",
    "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
    "prompt_sha256": "0ed4409a73095a9a2968bdcdb20bc397be345af84bff2c3558a48f08a5488aae",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-06T08:01:09.754980+00:00"
  },
  "final_blind": {
    "schema_version": "final_blind_v2",
    "agent_id": "confine-final-blind-agent",
    "provisional_decision": "reject",
    "independent_candidates": [
      {
        "id": "c01",
        "surface_form": "confine",
        "frame": "confine A to B, where A is a topic, inquiry, activity, effort, effect, or other abstract domain",
        "meaning": "restrict the scope or reach of A so that it does not extend beyond B",
        "disposition": "included",
        "rationale": "confine is a central productive transitive use and must be kept distinct from physically containing matter or detaining an animate being.",
        "semantic_assertions": [
          {
            "id": "c01-a1",
            "statement": "B sets the outer scope within which A is allowed to operate or apply.",
            "polarity": "must_hold",
            "scope": "all abstract-scope uses of confine A to B"
          },
          {
            "id": "c01-a2",
            "statement": "The construction entails that A is physically imprisoned as an animate detainee.",
            "polarity": "must_not_hold",
            "scope": "all abstract-scope uses of confine A to B"
          }
        ]
      },
      {
        "id": "c02",
        "surface_form": "confine oneself",
        "frame": "confine oneself to NP or doing",
        "meaning": "deliberately restrict one's subject matter or activity to a stated range",
        "disposition": "included",
        "rationale": "confine oneself is a productive reflexive construction and adds voluntary self-limitation to the abstract restriction sense.",
        "semantic_assertions": [
          {
            "id": "c02-a1",
            "statement": "The subject and the restricted participant are coreferential.",
            "polarity": "must_hold",
            "scope": "confine oneself to NP or doing"
          },
          {
            "id": "c02-a2",
            "statement": "The complement after to identifies the selected topic or activity range.",
            "polarity": "must_hold",
            "scope": "abstract reflexive uses"
          }
        ]
      },
      {
        "id": "c03",
        "surface_form": "be confined",
        "frame": "phenomenon, feature, problem, or distribution + be confined to B",
        "meaning": "occur or be found only within a particular place, group, period, or domain",
        "disposition": "included",
        "rationale": "be confined is common in this stative passive-like distributional frame and differs from an event of detaining a person.",
        "semantic_assertions": [
          {
            "id": "c03-a1",
            "statement": "Instances outside B are excluded or denied in the relevant context.",
            "polarity": "must_hold",
            "scope": "distributional be confined to B"
          },
          {
            "id": "c03-a2",
            "statement": "The grammatical subject must be an animate prisoner.",
            "polarity": "must_not_hold",
            "scope": "distributional be confined to B"
          }
        ]
      },
      {
        "id": "c04",
        "surface_form": "confine",
        "frame": "confine a substance, energy, fire, fluid, or similar entity to or within a bounded area or apparatus",
        "meaning": "physically contain something so that it cannot escape or spread beyond a boundary",
        "disposition": "included",
        "rationale": "confine in the physical-containment sense is productive in ordinary and technical prose and merits its own candidate because its patient and causal mechanism differ from abstract scope limitation.",
        "semantic_assertions": [
          {
            "id": "c04-a1",
            "statement": "The contained entity is prevented from physically escaping or spreading beyond the stated boundary.",
            "polarity": "must_hold",
            "scope": "physical containment of matter, energy, fire, fluid, or similar entities"
          },
          {
            "id": "c04-a2",
            "statement": "The frame is limited to the preposition to and excludes within.",
            "polarity": "must_not_hold",
            "scope": "physical containment syntax"
          }
        ]
      },
      {
        "id": "c05",
        "surface_form": "confine",
        "frame": "confine a person or animal in an enclosure or to a place; be confined in or to such a place",
        "meaning": "deprive an animate being of freedom to leave a bounded place",
        "disposition": "included",
        "rationale": "confine has a major animate-detention sense with a distinct affected participant, loss of liberty, and in/to alternation.",
        "semantic_assertions": [
          {
            "id": "c05-a1",
            "statement": "The affected person or animal lacks ordinary freedom to leave the place.",
            "polarity": "must_hold",
            "scope": "animate detention uses"
          },
          {
            "id": "c05-a2",
            "statement": "In profiles the interior of an enclosure, while to profiles the permitted range of movement.",
            "polarity": "must_hold",
            "scope": "the in/to alternation in animate detention uses"
          }
        ]
      },
      {
        "id": "c06",
        "surface_form": "confine",
        "frame": "illness, injury, or physical condition confines a person to bed, home, or a room; a person is confined to that place by or with the condition",
        "meaning": "cause a person, through ill health or injury, to remain in a restricted living place",
        "disposition": "included",
        "rationale": "confine has a conventional health-caused frame that is semantically narrower than detention by authority or barriers.",
        "semantic_assertions": [
          {
            "id": "c06-a1",
            "statement": "Illness, injury, recovery, or another bodily condition supplies the reason for the restricted location.",
            "polarity": "must_hold",
            "scope": "health-caused confinement uses"
          },
          {
            "id": "c06-a2",
            "statement": "The restriction necessarily results from punishment or legal custody.",
            "polarity": "must_not_hold",
            "scope": "health-caused confinement uses"
          }
        ]
      },
      {
        "id": "c07",
        "surface_form": "confined",
        "frame": "a confined space, area, interior, condition, or quarters; feel confined",
        "meaning": "enclosed or spatially restricted, often with little room for movement and a sense of constraint",
        "disposition": "included",
        "rationale": "confined is an established participial adjective with ordinary spatial uses beyond a transparent event passive.",
        "semantic_assertions": [
          {
            "id": "c07-a1",
            "statement": "Usable space, movement, or openness is restricted by surrounding limits.",
            "polarity": "must_hold",
            "scope": "ordinary adjectival confined"
          },
          {
            "id": "c07-a2",
            "statement": "Merely being enclosed always entails that the area is physically small.",
            "polarity": "must_not_hold",
            "scope": "ordinary adjectival confined"
          }
        ]
      },
      {
        "id": "c08",
        "surface_form": "confined space",
        "frame": "a confined space in occupational-safety terminology",
        "meaning": "a space large enough to enter, with limited or restricted entry or exit, and not designed for continuous occupancy; regulatory systems may add further conditions for particular subcategories",
        "disposition": "included",
        "rationale": "confined space as a technical term must be separated from the everyday sense because physical smallness alone is neither its definition nor its decisive boundary.",
        "semantic_assertions": [
          {
            "id": "c08-a1",
            "statement": "The space has limited or restricted means of entry or exit and is not designed for continuous occupancy.",
            "polarity": "must_hold",
            "scope": "occupational-safety use of confined space"
          },
          {
            "id": "c08-a2",
            "statement": "Every small room qualifies solely because it is small.",
            "polarity": "must_not_hold",
            "scope": "occupational-safety use of confined space"
          }
        ]
      },
      {
        "id": "c09",
        "surface_form": "confines",
        "frame": "within, beyond, or outside the confines of NP; the narrow confines of NP",
        "meaning": "formal plural noun denoting enclosing limits or the area or conceptual domain inside them",
        "disposition": "included",
        "rationale": "confines is an established plural noun in physical, institutional, and conceptual boundary expressions and differs in stress and category from the verb.",
        "semantic_assertions": [
          {
            "id": "c09-a1",
            "statement": "The complement NP supplies the place, system, or domain whose limiting boundary or enclosed extent is meant.",
            "polarity": "must_hold",
            "scope": "plural noun confines of NP"
          },
          {
            "id": "c09-a2",
            "statement": "The plural form can denote only boundary lines and never the enclosed domain.",
            "polarity": "must_not_hold",
            "scope": "plural noun confines"
          }
        ]
      },
      {
        "id": "c10",
        "surface_form": "confining",
        "frame": "a confining job, role, routine, environment, garment, or other circumstance; find something confining",
        "meaning": "restricting freedom, movement, choice, or scope in an uncomfortable or oppressive way",
        "disposition": "included",
        "rationale": "Besides serving as the verb's present participle, confining has a productive adjectival use that describes the restrictive effect or felt quality of a circumstance or object.",
        "semantic_assertions": [
          {
            "id": "c10-a1",
            "statement": "The modified or predicatively described item restricts a person's freedom, movement, choice, or scope.",
            "polarity": "must_hold",
            "scope": "adjectival confining"
          },
          {
            "id": "c10-a2",
            "statement": "Every occurrence of confining must be analyzed only as a progressive participle with an overt patient.",
            "polarity": "must_not_hold",
            "scope": "adjectival confining"
          }
        ]
      },
      {
        "id": "c11",
        "surface_form": "confinement",
        "frame": "confinement of a person or thing; a period or state of confinement",
        "meaning": "the act of confining or the state of being confined, including custody and enforced restriction",
        "disposition": "included",
        "rationale": "confinement is the principal deverbal noun and transparently preserves both event and result-state readings.",
        "semantic_assertions": [
          {
            "id": "c11-a1",
            "statement": "The noun denotes either an act or period of restriction or the resulting restricted state.",
            "polarity": "must_hold",
            "scope": "current general uses of confinement"
          }
        ]
      },
      {
        "id": "c12",
        "surface_form": "unconfined",
        "frame": "unconfined person, space, substance, movement, or activity",
        "meaning": "not enclosed or not restricted within a limiting boundary",
        "disposition": "included",
        "rationale": "unconfined is the productive negative adjective and reverses the relevant bounded-state component of confined.",
        "semantic_assertions": [
          {
            "id": "c12-a1",
            "statement": "A contextually relevant enclosing or restricting boundary does not apply.",
            "polarity": "must_hold",
            "scope": "ordinary uses of unconfined"
          }
        ]
      },
      {
        "id": "c13",
        "surface_form": "confine",
        "frame": "one territory confines with or on another",
        "meaning": "share a boundary or border on another territory",
        "disposition": "excluded",
        "rationale": "confine in this intransitive border sense is historical or obsolete in present general English and does not merit full current-use treatment, though it is relevant to etymology.",
        "semantic_assertions": [
          {
            "id": "c13-a1",
            "statement": "The two territories share or meet at a boundary.",
            "polarity": "must_hold",
            "scope": "historical intransitive confine with or on"
          },
          {
            "id": "c13-a2",
            "statement": "One participant necessarily imprisons the other.",
            "polarity": "must_not_hold",
            "scope": "historical intransitive confine with or on"
          }
        ]
      },
      {
        "id": "c14",
        "surface_form": "confinement",
        "frame": "a woman's confinement",
        "meaning": "dated reference to childbirth or the period around childbirth",
        "disposition": "excluded",
        "rationale": "confinement in this specialized historical euphemism is dated and need not be presented as a current major sense in a general entry.",
        "semantic_assertions": [
          {
            "id": "c14-a1",
            "statement": "The expression refers to childbirth or the traditional period of seclusion associated with it.",
            "polarity": "must_hold",
            "scope": "dated childbirth sense of confinement"
          }
        ]
      }
    ],
    "article_findings": [
      {
        "id": "f01",
        "taxonomy_id": "cross_section_internal_contradiction",
        "location": {
          "section": "word_formation",
          "line_start": 25,
          "line_end": 25,
          "exact_quote": "・confining（現在分詞）— confine の -ing 形。  "
        },
        "severity": "blocking",
        "rationale": "The entry reduces this form to morphology alone: ・confining（現在分詞）— confine の -ing 形。  It therefore omits the productive adjective meaning ‘restricting freedom, movement, choice, or scope; oppressive’, as in a confining job, role, garment, or environment. Because this is a distinct lexicalized adjectival use rather than merely an ongoing verb form, the inventory of major derivation/conversion is incomplete."
      },
      {
        "id": "f02",
        "taxonomy_id": "argument_slot_role_mismatch",
        "location": {
          "section": "usage_notes",
          "line_start": 77,
          "line_end": 77,
          "exact_quote": "【語法・注意】基本形は confine A to B であり、to の後ろには名詞または動名詞を置く。場所の内部へ物理的に閉じ込める語義2では confine someone in a cell のように in も使う。confine oneself to は話題・活動の自主的な限定によく使うが、confine oneself to one's room のように場所を示す語が続けば、物理的に自分をその場所にとどめる意味にもなる。  "
        },
        "severity": "blocking",
        "rationale": "The syntax summary says: 【語法・注意】基本形は confine A to B であり、to の後ろには名詞または動名詞を置く。場所の内部へ物理的に閉じ込める語義2では confine someone in a cell のように in も使う。confine oneself to は話題・活動の自主的な限定によく使うが、confine oneself to one's room のように場所を示す語が続けば、物理的に自分をその場所にとどめる意味にもなる。  This omits the productive transitive and passive frame confine A within B / A be confined within B, especially common for physical containment within boundaries, walls, an area, or an apparatus. The omission is material because the entry itself treats physical containment as productive but presents only to for that inanimate frame and reserves in for animate confinement, leaving the construction inventory incomplete."
      }
    ],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "confine-final-blind-agent",
      "same_model_as_generation": true
    },
    "stage": "final_blind",
    "run_id": "blind-confine-20260906T073045Z-f9a3853d",
    "context_id": "blind-confine-context-20260906T073045Z-f9a3853d",
    "input_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
    "prompt_sha256": "1bb7b1a1c7f589a50a704d1ce6c1ecd0bfb1c9fb689fd481d21bf608438eb7b5",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-06T08:18:56.507025+00:00"
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/c/confine.md",
    "body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
    "final_blind_path": "audits/runs/c/confine/20260906T073045Z-f9a3853d/final_blind.json",
    "final_blind_sha256": "655454c1fccce145e7329961a13a719a25d2c2d05a630823eec17fefc21dbcdc",
    "blind_output_sha256": "a5c53f22e734db025ef7fb6089566988be4631cc11c500c62545912ac57bff3e",
    "sealed_at": "2026-09-06T01:19:23.896107-07:00"
  },
  "pre_blind_resolution": {
    "schema_version": "pre_blind_resolution_v1",
    "resolutions": [
      {
        "id": "NR-translation-1",
        "finding_id": "NR-translation-1",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "「保護された」は原文にない目的を加えるため、拘束状態を直接表す訳へ修正した。"
      },
      {
        "id": "NR-translation-2",
        "finding_id": "NR-translation-2",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "義務の含意を除き、合併症による一時的な状態を表す英文と訳へ修正した。"
      },
      {
        "id": "NR-translation-3",
        "finding_id": "NR-translation-3",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "enclosed が屋根と壁の両方を必ず含むという過剰な具体化を除いた。"
      },
      {
        "id": "NR-sense-structure-1",
        "finding_id": "NR-sense-structure-1",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "固定済み根拠は confining の独立形容詞義を支持せず、主要語義として追加できない。語形成欄を現在分詞という確認済み範囲へ限定した。"
      },
      {
        "id": "NR-frame-relation-1",
        "finding_id": "NR-frame-relation-1",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "語義2の目的語を人・動物に限定し、無生物一般へ漏れる something を除いた。"
      },
      {
        "id": "NR-frame-relation-2",
        "finding_id": "NR-frame-relation-2",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "enclose は対象の自由を奪う意味を必須とせず、この語義の類義語として中心義が十分重ならないため削除した。"
      },
      {
        "id": "NR-example-attribution-1",
        "finding_id": "NR-example-attribution-1",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "回復中という情報だけに依存せず語義3へ一意に帰属するよう、合併症を原因として明示した。"
      },
      {
        "id": "NR-example-attribution-2",
        "finding_id": "NR-example-attribution-2",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "人を主語とする拘束状態の例を語義4から外し、空間自体を confined とする例へ差し替えた。"
      },
      {
        "id": "NR-qualification-1",
        "finding_id": "NR-qualification-1",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "再帰形の物理用法を一律に排除せず、場所補語なら自己隔離の意味も成立すると明記した。"
      },
      {
        "id": "NR-evidence-1",
        "finding_id": "NR-evidence-1",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "固定済み資料が直接示さない屈折形の完全IPAを削除した。"
      },
      {
        "id": "NR-evidence-2",
        "finding_id": "NR-evidence-2",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "名詞史と関連語の主張を除き、固定済み語源資料が直接支持する動詞の系譜と意味発達に限定した。"
      },
      {
        "id": "NR-evidence-3",
        "finding_id": "NR-evidence-3",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "confinement の説明を、資料が支持する行為・状態・拘禁に限定した。"
      },
      {
        "id": "NR-evidence-4",
        "finding_id": "NR-evidence-4",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "confining の独立形容詞義と用途列挙を除き、確認済みの現在分詞とだけ記した。"
      },
      {
        "id": "NR-evidence-5",
        "finding_id": "NR-evidence-5",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "unconfined と limited/restricted の未立証な相対頻度を削除した。"
      },
      {
        "id": "NR-evidence-6",
        "finding_id": "NR-evidence-6",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "受動・能動・再帰形の存在は残し、両方がよく使われるという分布主張を除いた。"
      },
      {
        "id": "NR-evidence-7",
        "finding_id": "NR-evidence-7",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "自由意思による滞在を一律に排除する根拠のない文を削除した。"
      },
      {
        "id": "NR-evidence-8",
        "finding_id": "NR-evidence-8",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "能動・受動の相対頻度を除き、双方の確認可能な構文だけを示した。"
      },
      {
        "id": "NR-evidence-9",
        "finding_id": "NR-evidence-9",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "複数形が圧倒的に普通という強度表現を除き、通常 confines であるとの支持範囲に限定した。"
      },
      {
        "id": "NR-evidence-10",
        "finding_id": "NR-evidence-10",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "8/10 は仕様が要求する統一的な編集尺度であり、厳密な統計根拠がなくても基準を一貫させると仕様に明記される。"
      },
      {
        "id": "NR-evidence-11",
        "finding_id": "NR-evidence-11",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "7/10 は仕様所定の編集尺度であり、語義・例・領域ラベルの整合を総合評価した値で、個別コーパス統計の断定ではない。"
      },
      {
        "id": "NR-evidence-12",
        "finding_id": "NR-evidence-12",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "6/10 は仕様所定の編集尺度であり、病気・回復文脈の語義説明と矛盾せず、統計値を称していない。"
      },
      {
        "id": "NR-evidence-13",
        "finding_id": "NR-evidence-13",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "6/10 は仕様所定の編集尺度である。一般的形容詞義と米国OSHAの専門用法は別文で区別されている。"
      },
      {
        "id": "NR-evidence-14",
        "finding_id": "NR-evidence-14",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "4/10 は仕様所定の編集尺度であり、通常複数形という資料記述と定着句の用例に整合する。"
      },
      {
        "id": "NR-evidence-15",
        "finding_id": "NR-evidence-15",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "疾病用法の一般化した with/by フレームを、本文例と資料が示す be confined to bed with illness に限定した。"
      },
      {
        "id": "NR-evidence-16",
        "finding_id": "NR-evidence-16",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "否定証拠のない誤用断定と分布主張を除き、肯定的な to/in の使い分けと反例を含む再帰用法だけにした。"
      },
      {
        "id": "NR-evidence-17",
        "finding_id": "NR-evidence-17",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "語法欄から imprison との未立証な適用範囲比較を削除した。"
      },
      {
        "id": "NR-evidence-18",
        "finding_id": "NR-evidence-18",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "専門定義を米国OSHAに明示的に限定し、法域間比較を避けた。"
      },
      {
        "id": "NR-evidence-19",
        "finding_id": "NR-evidence-19",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "類義語・反意語の比較は仕様上必須であり、各定義・例文・同一意味軸を相互照合した編集上の対照説明で、資料の存在だけを根拠とする主張ではない。"
      },
      {
        "id": "NR-evidence-20",
        "finding_id": "NR-evidence-20",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "語義2の比較欄は各語の定義と例文を併記して適用範囲を明示しており、類義語欄を丸ごと hold にするのは仕様の学習目的に反する。"
      },
      {
        "id": "NR-evidence-21",
        "finding_id": "NR-evidence-21",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "語義3の比較欄は各表現の定義・例文と限定軸を併記しており、仕様が要求する学習上の区別として保持する。"
      },
      {
        "id": "NR-evidence-22",
        "finding_id": "NR-evidence-22",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "語義4の比較欄は空間性・狭さ・閉鎖性という同一軸を定義と例文で対照しており、仕様所定の類義語・反意語説明として保持する。"
      },
      {
        "id": "NR-evidence-23",
        "finding_id": "NR-evidence-23",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "語義5の比較欄は各語の定義・例文と境界対領域の軸を明示しており、仕様所定の学習上の差として保持する。"
      },
      {
        "id": "CR-001",
        "finding_id": "CR-001",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "名詞複数形のIPAを直接示す固定根拠がなく、追加すると evidence finding を再発させるため採用しない。代わりに未支持の屈折形IPAを削除した。"
      },
      {
        "id": "CR-002",
        "finding_id": "CR-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "物理的な再帰用法の反例を明記し、一律排除を解消した。"
      },
      {
        "id": "CR-003",
        "finding_id": "CR-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "語義見出しとコアイメージに形容詞形が confined であることを明記した。"
      },
      {
        "id": "CR-004",
        "finding_id": "CR-004",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "祖語義から現代義への意味発達を段階化し、現代的コアイメージの逆投影を避けた。"
      },
      {
        "id": "CR-005",
        "finding_id": "CR-005",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "原文にない保護目的を除き、囲い内への拘束を直接訳した。"
      }
    ],
    "learning_delta": {
      "schema_version": "process_improvement_learning_delta_v2",
      "reviewed": true,
      "items": []
    }
  },
  "pre_blind_revision": {
    "schema_version": "pre_blind_revision_v1",
    "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
    "output_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
    "recorded_at": "2026-09-06T08:05:23Z",
    "changed_units": [
      "collocations_examples",
      "core_image",
      "etymology",
      "frames",
      "lexical_relations",
      "pronunciation",
      "sense_structure",
      "usage_notes",
      "word_formation"
    ],
    "invalidated_passes": [
      "evidence",
      "example-attribution",
      "frame-relation",
      "pronunciation",
      "qualification",
      "sense-structure",
      "translation"
    ],
    "full_recheck": true
  },
  "checker_recheck_manifest": {
    "schema_version": "checker_recheck_manifest_v1",
    "current_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
    "revision_plan_sha256": "8cd15fb59ab15315e4d6a3449cd7ec9b238cae36fcb82e8434e9d232b191dfb9",
    "full_recheck": true,
    "invalidated_passes": [
      "evidence",
      "example-attribution",
      "frame-relation",
      "pronunciation",
      "qualification",
      "sense-structure",
      "translation"
    ],
    "pass_results": [
      {
        "pass_id": "evidence",
        "mode": "rechecked",
        "validated_on_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
        "spec_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
        "normalized_input_sha256": "b2da470f45eea97ac7f0bb7e7a208d5e4c9742d058d1a7413a29434406f0c56a",
        "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
        "output_sha256": "862aba02c8d92baf634ddfe0f89e765662136a18fc67e2bae8ababbe87cadae5",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true
      },
      {
        "pass_id": "example-attribution",
        "mode": "rechecked",
        "validated_on_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
        "spec_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
        "normalized_input_sha256": "79075a28d97ce1b898f824e2f468bce4fa3509a34076e8e6e5f3b0e922d332c4",
        "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
        "output_sha256": "bbfa3baff2b6b0a248f7c24d440bbc77f358d697406c28ac5d99a038efc4c4e0",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true
      },
      {
        "pass_id": "frame-relation",
        "mode": "rechecked",
        "validated_on_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
        "spec_sha256": "3598ca81a5784639c6b43a0806d0981a985bf4174f424c744aad1dde787bfcef",
        "normalized_input_sha256": "9e6db0c57a0bde27379009516a2f7b33a482b56998738f9108e89de26be4bf9c",
        "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
        "output_sha256": "f6b027853efe80d5b6cb9c5ec675018774918d9f307f638c4326960941960c14",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true
      },
      {
        "pass_id": "pronunciation",
        "mode": "rechecked",
        "validated_on_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
        "spec_sha256": "7e3e94267ac9f917c901c12580b91e570b5989df7adfbf2a39b833478c766d8a",
        "normalized_input_sha256": "c01619e5d9fb2a372ddc284b5ac6132ab5a97cf73a8cbe1438a953036582eac5",
        "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
        "output_sha256": "8910748a4e12b2c7be6279b4150696b63e5e91e707ca6156014b95b460efb9bf",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true
      },
      {
        "pass_id": "qualification",
        "mode": "rechecked",
        "validated_on_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
        "spec_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
        "normalized_input_sha256": "4e7d27a89794abf3768f551cc926558af9be917c93c6bba3ed7c04d55d87f293",
        "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
        "output_sha256": "ececd945cc7509e34f37829bd027cc83ffd542c5cd4d0a332c535de02668fa02",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true
      },
      {
        "pass_id": "sense-structure",
        "mode": "rechecked",
        "validated_on_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
        "spec_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
        "normalized_input_sha256": "f034892f606838b477c1671a51005679e9b2702cc16596c9e909bf04341319b6",
        "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
        "output_sha256": "21ac1c1c80639827a82b6a020b4f8ef9b3b56a3862a91b61321ecef806a25d1b",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true
      },
      {
        "pass_id": "translation",
        "mode": "rechecked",
        "validated_on_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
        "spec_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
        "normalized_input_sha256": "d9baeec5ff996c14de6bcbb5a637841eb735109557b037a10e85b5884b235651",
        "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
        "output_sha256": "265027a74a4e8a3dd5d16780388b750290b12f7d579e4597f3a384b0d25b4a44",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true
      }
    ]
  },
  "post_blind_resolution": {
    "schema_version": "post_blind_resolution_v1",
    "resolutions": [
      {
        "id": "f01",
        "finding_id": "f01",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "固定済み source inventory は confining の独立形容詞義を支持せず、根拠なしに主要品詞転換を追加できない。現在分詞としての確認可能な情報に限定した現行記述を維持する。"
      },
      {
        "id": "f02",
        "finding_id": "f02",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "within は境界を表す一般的な前置詞選択として予測可能だが、固定済み根拠には confine A within B を独立した主要フレームとして扱う直接資料がない。既に主要な to と物理的位置の in を収録しており、根拠なしの追加はしない。"
      }
    ],
    "learning_delta": {
      "schema_version": "process_improvement_learning_delta_v2",
      "reviewed": true,
      "items": []
    }
  },
  "post_blind_verification": {
    "schema_version": "post_blind_verification_v1",
    "verified_body_sha256": "02ebd3098956d9255fc2a4205e0ea6b9d60200d4b8c9474cbfdef58ff75add66",
    "checker_recheck_completed": false,
    "final_blind_repeated": false
  },
  "targeted_adjudications": {
    "requests": [],
    "adjudications": []
  }
}
```
