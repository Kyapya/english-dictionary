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

入力に `inventories` / `response_template` がある場合、それが照合対象IDの正本である。IDを作り直さず、ひな形の未判定欄を独立に判定する。未判定は合格ではない。`target_results` / `relation_results` の `notes` には、対応する対象の `text` / 関係の `description` 全文を引用し、その対象固有の判断理由を記載する。入力欠落を空集合と推測しない。

`final_review_v2` JSONとして、全target/relation/normal candidate/blind candidate/finding/evidence/source-unionの個別結果、再検査・再利用manifestの照合結果、`decision` (`pass | reject`)、`blockers`、非blocking `notes` を返す。`PASS` は全個別結果がpass、未解決・hold・`insufficient_evidence`が0件、blockerが0件の場合に限る。本文は変更しない。新しい内容上のblockerを見つけた場合は正常なREJECTとし、修正、影響範囲再検査、final blind再実行へ戻す。


## Input packet

```json
{
  "stage": "final_review",
  "entry_body": "\n＃発音記号\n\n米（一般的な形）: /ˈkɑːnstəˌtuːt/｜英: /ˈkɒnstɪˌtjuːt/。3音節で、第1音節に主強勢、第3音節に第二強勢がある。米音では第1音節の母音が /ɑː/、第2音節が弱い /stə/ となり、第3音節は一般に /tuːt/ だが /tjuːt/ の変異もある。英音では第1音節が /ɒ/、第2音節が /stɪ/、第3音節が /tjuːt/ となる。  \n\n＃語源\n\n中英語を経て、ラテン語 constituere「立てる、据える、設ける、定める」に由来する。これは con- と statuere「立てる、置く」から成り、statuere は「立つ」を表す語根につながる。現在の「全体を構成する」「制度・組織を正式に成立させる」「人を役職に就ける」という用法には、「ある形・位置に据えて成立させる」という歴史的な意味が残っている。  \n同語源・同じ語族の学習語には constitution「構成、体質、憲法」、constitutional「構成上の、憲法上の」、constituent「構成要素、選挙区民；構成する」、statute「制定法」がある。  \n\n＃語形成\n\n`constitution` — 名詞。「構成・体質」のほか、国家・組織の基本原則を定める「憲法・規約」を表す。  \n`constitutional / constitutionally` — 形容詞「構成上の、体質上の、憲法上の」／副詞「体質的に、憲法上」。  \n`constituent` — 名詞「構成要素、選挙区民」、形容詞「構成する」。政治義の constituent は「constitute の目的語」を意味する名称ではなく、代表者を選ぶ constituency の構成員を指す。  \n`reconstitute` — 動詞「再構成する、元の状態に戻す」。乾燥食品・薬剤などに液体を加えて戻す用法もある。  \n\n＃コアイメージ\n\nconstitute の共通核は、要素・行為・組織・人を、ある全体・分類・制度・役割として成り立つ位置に据えることである。文脈によって、すでにそうであるという関係を述べる場合と、意図的・正式に成立させる行為を述べる場合がある。  \n・要素を全体として成り立つ位置に据える → 「構成する、占める」（語義1）  \n・行為や事実を分類として成り立つ位置に据える → 「～に当たる、～となる」（語義2）  \n・組織や契約を正式な制度・法的形式として成り立つ位置に据える → 「正式に設立する、所定の形式に整える」（語義3）  \n・人を公的な役割として成り立つ位置に据える → 「正式に任命・指定する」（語義4）  \n\n＃意味・用法・関連表現\n\n1. 【他動詞】構成する、（全体の一定割合を）占める\n\n【日本語訳・定義】一つまたは複数の人・物・部分・期間などが、一つの全体を形作る、またはその全体の一定割合・重要部分を占めることを表す。全体構成の能動構文では主語が構成要素、目的語がそれらによってできる全体である。一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は通常 of 句に現れるが、文脈上明らかな場合は省略できる。意図的に組み立てる行為ではなく、部分と全体の関係を記述することが多い。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】やや硬い標準語。報道、統計、学術、ビジネス、公式説明でよく使う。日常会話では make up や form の方が一般的なことが多い。  \n\n【文法パターン】`〈parts/members〉 constitute 〈whole/group〉`＝部分・構成員が全体・集団を構成する／`〈group/category〉 constitute 〈割合〉 (of 〈whole〉)`＝集団・分類が全体の一定割合を占める（全体が文脈上明らかなら of 句を省略可）／`〈whole〉 be constituted of 〈parts〉`＝全体が部分から構成されている  \n\n【コロケーション】\n\n・`〈parts/members〉 constitute 〈whole/group〉`  \n用途: 複数の部分・構成員が一つの全体や集団を作ることを述べる。  \n例: Twelve jurors constitute the full jury in this court.  \n訳: この裁判所では、12人の陪審員が陪審全体を構成する。  \n\n・`constitute the majority/minority of 〈group〉`  \n用途: ある分類の人・物が、集団の過半数または少数派を占めることを述べる。  \n例: Part-time employees constitute the majority of the evening staff.  \n訳: 非常勤職員が夜間スタッフの過半数を占めている。  \n\n・`constitute 〈percentage〉 of 〈whole〉`  \n用途: 全体に占める割合を、統計的・客観的に示す。  \n例: Online sales now constitute 35 percent of the company's revenue.  \n訳: オンライン販売は現在、その会社の売上高の35パーセントを占めている。  \n\n・`constitute a large/significant part of 〈whole〉`  \n用途: ある要素が全体の大きな部分・重要部分を占めることを示す。  \n例: Maintenance costs constitute a significant part of the annual budget.  \n訳: 維持費は年間予算のかなりの部分を占める。  \n\n・`be constituted of 〈parts/materials〉`  \n用途: 全体を主語にして、その構成要素や材料を示す硬い受動表現。  \n例: The panel is constituted of experts from five different fields.  \n訳: その委員会は5つの異なる分野の専門家で構成されている。  \n\n【語法・注意】能動の `A, B, and C constitute X` では A・B・C が部分、X が全体である。`X consists of A, B, and C` や `X is composed of A, B, and C` では向きが逆になり、X が全体、A・B・C が部分になる。  \n\n`be constituted of` は可能だが硬い。通常は `be composed of` または `consist of` が自然である。`consist` は自動詞なので `X is consisted of A` とはしない。  \n`comprise` は伝統的には `X comprises A, B, and C` のように全体を主語、部分を目的語にするため、能動の constitute とは基本方向が逆である。ただし現代英語では parts comprise a whole や be comprised of も広く使われるので、厳密さが必要な文章では parts/whole の関係が明確な表現を選ぶ。  \n\n【類義語】\n\n・make up  \n定義: 複数の部分・人が集まって全体を構成する。  \n頻度: 〈9/10〉  \n違い: make up は constitute より口語的で幅広い。`A and B make up X` と同じ parts-to-whole の向きで使える。  \n例: Small firms make up most of the local economy.  \n訳: 小規模企業が地域経済の大部分を構成している。  \n\n・form  \n定義: 部分が集まって全体・形・集団を作る。  \n頻度: 〈10/10〉  \n違い: form は中立的で、構成関係にも実際に作る過程にも使える。constitute は硬く、部分と全体の関係を分類・統計として述べることが多い。  \n例: These streams form the main river.  \n訳: これらの小川が本流を形作っている。  \n\n・compose  \n定義: 複数の要素が全体を構成する。  \n頻度: 〈7/10〉  \n違い: compose は構成要素の組み合わせに焦点があり、受動の `be composed of` が特に一般的である。constitute は割合を述べる構文にもよく使う。  \n例: Four short sections compose the final movement.  \n訳: 4つの短い部分が終楽章を構成している。  \n\n・account for  \n定義: 数量・割合・原因などのうち、特定の分を占める。  \n頻度: 〈8/10〉  \n違い: 割合の用法では近いが、account for は「全体のうちどれだけを説明できるか・占めるか」に焦点がある。constitute は割合だけでなく、部分が全体そのものを形作る関係にも使える。  \n例: Exports account for nearly half of total sales.  \n訳: 輸出が総売上高のほぼ半分を占める。  \n\n2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる\n\n【日本語訳・定義】行為、状況、事実、結果などが、ある分類・評価・状態の定義や成立条件を満たし、そのものと見なせることを表す。目的語には crime、breach、threat、evidence、change、problem などが来る。法律用語だけではなく一般の評価にも使うが、何がその分類に当たるかをやや改まって判断する響きがある。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】やや硬い標準語。報道、法律、規則、倫理、学術、ビジネス上の評価で頻出する。法律文脈では、実際に犯罪・違反などが成立するかは適用法と事実認定によって決まるため、単語自体が法的結論を保証するわけではない。  \n\n【文法パターン】`〈act/fact/situation〉 constitute 〈category/result〉`＝行為・事実・状況が分類・結果に当たる／`constitute a crime/breach/violation`＝犯罪・契約違反・規則違反に当たる／`constitute a threat/risk/problem`＝脅威・危険・問題となる／`what constitutes 〈category〉`＝何がその分類を成り立たせるか  \n\n【コロケーション】\n\n・`constitute a crime/offence`  \n用途: ある行為が法律上の犯罪・違反に当たり得ることを述べる。  \n例: Deliberately altering the records may constitute a criminal offence.  \n訳: 記録を故意に改ざんすることは、刑事犯罪に当たる可能性がある。  \n\n・`constitute a breach/violation of 〈rule/duty〉`  \n用途: 行為・不作為が契約、規則、義務などへの違反に当たると判断する。  \n例: Sharing the data without permission would constitute a breach of the agreement.  \n訳: 許可なくデータを共有すれば、その契約への違反に当たる。  \n\n・`constitute a threat/risk to 〈person/system〉`  \n用途: 状況・存在が人や制度への脅威・危険となることを示す。  \n例: The damaged bridge constitutes a serious risk to public safety.  \n訳: その損傷した橋は公共の安全に対する重大な危険となっている。  \n\n・`constitute evidence/proof of 〈事実〉`  \n用途: ある資料・行為が、事実を裏づける証拠に当たるかを論じる。  \n例: A single anonymous message does not constitute proof of fraud.  \n訳: 匿名のメッセージ一通だけでは、詐欺の証明にはならない。  \n\n・`constitute a significant change/improvement`  \n用途: 出来事や措置が、単なる小差ではなく、意味のある変化・改善に当たると評価する。  \n例: The revised policy constitutes a significant change in the company's approach.  \n訳: 改訂された方針は、その会社の取り組み方の大きな変化に当たる。  \n\n・`what constitutes 〈category/standard〉`  \n用途: 何がある概念・分類・基準に該当するのかを問う・定義する。  \n例: The guidelines explain what constitutes acceptable use of the system.  \n訳: その指針は、どのようなシステム利用が許容されるかを説明している。  \n\n【語法・注意】この語義の constitute は、主語と目的語を同一の分類関係で結ぶが、文法上は目的語を取る動詞であり、通常 `constitute as a threat` のように as を挟まない。`The delay constitutes a problem.` のように直接目的語を置く。  \n\n語義1との区別は、目的語が「主語を部分として含む全体」か、「主語が該当すると判断される分類・評価」かで行う。`Ten members constitute the committee.` は構成、`Their absence constitutes a problem.` は評価・該当である。  \n否定文の `does not constitute proof/consent/approval` は、「証拠・同意・承認として十分ではない」という境界を明示する定型的な用法である。constitute 自体は、事態を引き起こす cause や、証拠によって証明する prove を意味しない。  \n\n【類義語】\n\n・amount to  \n定義: 行為・状況が、実質的にある結果・評価と同じである。  \n頻度: 〈8/10〉  \n違い: amount to は「結局は～に等しい」という実質的帰結を強調する。constitute は定義・基準への該当を、より公式・分析的に述べやすい。  \n例: Ignoring repeated warnings amounts to negligence.  \n訳: 度重なる警告を無視することは、怠慢に等しい。  \n\n・qualify as  \n定義: 必要な条件を満たして、ある分類・資格に該当する。  \n頻度: 〈7/10〉  \n違い: qualify as は明示的な条件を満たす点を強調する。constitute は条件が厳密に列挙されていない一般評価にも使える。  \n例: The structure qualifies as a protected historic building.  \n訳: その構造物は、保護対象の歴史的建造物に該当する。  \n\n・count as  \n定義: 規則・判断・一般的理解の上で、あるものとして数えられる。  \n頻度: 〈8/10〉  \n違い: count as は口語的で、日常的な分類にも使いやすい。constitute はより硬く、公式の基準や重大な評価に合う。  \n例: Does volunteer work count as relevant experience?  \n訳: ボランティア活動は関連経験として認められますか。  \n\n・represent  \n定義: 状況・出来事が、ある意味・変化・危険などを体現する。  \n頻度: 〈9/10〉  \n違い: represent は象徴・典型・意味づけまで広く表す。constitute は主語が実際にその分類・状態に当たるという同一視がより強い。  \n例: The agreement represents an important step toward peace.  \n訳: その合意は、平和に向けた重要な一歩を意味する。  \n\n3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える\n\n【日本語訳・定義】組織、委員会、裁判所、政府などを正式に形成・設置し、公式の組織体として成立させることを表す。法律用法では、契約や組織体に所定の法的形式を与えることも表す。制度や文脈によって所定の手続きや権限付与を伴うことはあるが、constitute という語だけで法的有効性や実際の活動可能性まで一律に保証するわけではない。  \n\n【頻度】〈5/10〉  \n\n【レジスター/領域】非常に硬い公式・行政・法律・組織運営の用法。契約などを所定の法的形式に整える意味も法律文脈に限られる。一般的な会社・団体の設立では establish、form、set up がより広く使われる。  \n\n【文法パターン】`〈authority/institution/parties〉 constitute 〈committee/body/court/government〉`＝権限主体・機関・当事者が委員会・機関・裁判所・政府を正式に設ける／`constitute 〈agreement/body〉`＝契約・組織体に所定の法的形式を与える／`〈body〉 be constituted under/by 〈law/authority〉`＝機関が法律・権限に基づいて設立される／`a properly/legally/duly constituted 〈body/authority〉`＝適切・合法・正式に成立した機関・権限主体  \n\n【コロケーション】\n\n・`constitute a committee/panel`  \n用途: 特定の目的をもつ委員会や審査団を正式に設ける。  \n例: The ministry constituted an independent panel to investigate the accident.  \n訳: 同省は、その事故を調査する独立委員会を正式に設置した。  \n\n・`constitute a court/tribunal`  \n用途: 裁判所・審判機関を正式に設ける。  \n例: The treaty provides for a tribunal to be constituted when a dispute arises.  \n訳: その条約は、紛争が生じた際に審判機関を設置することを定めている。  \n\n・`constitute a government/authority`  \n用途: 政府・公的機関を正式な組織体として成立させる。  \n例: The parties agreed to constitute a transitional government.  \n訳: 当事者らは暫定政府を発足させることで合意した。  \n\n・`be constituted under 〈law/charter〉`  \n用途: 組織が法律・憲章などを根拠として設立されていることを示す。  \n例: The commission was constituted under the new environmental law.  \n訳: その委員会は新しい環境法に基づいて設置された。  \n\n・`a duly/properly constituted 〈body/meeting〉`  \n用途: 機関・会議が必要な手続きや構成要件を満たして正式に成立していることを示す。  \n例: Only a duly constituted board may approve the transaction.  \n訳: 正式に構成された取締役会だけが、その取引を承認できる。  \n\n【語法・注意】語義1の「部分が全体を構成している」は状態的な関係、語義3の「組織を正式に設立する」は意図的・制度的な行為である。`The members constitute the board.` は「構成員が取締役会を構成する」、`The agency constituted a board.` は「機関が取締役会を正式に設置した」となる。  \n\n法律文脈の `constitute an agreement/body` は、契約や組織体に必要な法的形式を与える意味になり得る。組織を新設する意味と、既存の契約・組織体を所定の形式に整える意味は文脈で区別する。  \n\n`be constituted under ...` は通常、設立根拠を示す。`be constituted by ...` の by 句は文脈により、設立主体を示す場合と、語義1で全体を形作る構成要素を示す場合がある。`be constituted of ...` は構成要素を示すため、前置詞だけで語義を機械的に判断しない。  \n`duly/properly/legally constituted` は constituted が過去分詞として名詞を修飾する定着表現で、「正当に権限をもつ・手続き上有効に成立した」という含みを持つ。ただし、その組織の個々の決定まで自動的に適法だと保証する表現ではない。  \n\n【類義語】\n\n・establish  \n定義: 組織・制度・関係などを作り、安定して存在するようにする。  \n頻度: 〈9/10〉  \n違い: establish は設立全般に使える標準的な語である。constitute は、組織体を公式な形で成立させる硬い表現である。  \n例: The university established a new research center.  \n訳: その大学は新しい研究センターを設立した。  \n\n・form  \n定義: 人・組織・要素を集めて、新しい集団・組織を作る。  \n頻度: 〈10/10〉  \n違い: form は日常的で、正式な法的手続きを必ずしも含まない。constitute は公式・制度的な文脈で使われやすい。  \n例: Residents formed a committee to protect the park.  \n訳: 住民たちは公園を守るために委員会を結成した。  \n\n・set up  \n定義: 組織・制度・仕組みなどを作って動かし始める。  \n頻度: 〈9/10〉  \n違い: set up は口語的で、準備・運用開始まで幅広く表す。constitute は設立の公式性・制度性に焦点がある。  \n例: The city set up a task force to address housing shortages.  \n訳: 市は住宅不足に対処する特別チームを立ち上げた。  \n\n4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する\n\n【日本語訳・定義】権限をもつ者・法律・公式文書などが、人を特定の役職・地位・役割に正式に任命・指定することを表す。任命の法的有効性、付与される権限、その立場で行動できる範囲は、該当する文書・制度・法域によって決まる。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】法律・公文書などの公式文体。`a legally constituted officer` のような表現では、法や制度に基づいて正式に任命された役職者を指す。  \n\n【文法パターン】`〈authority/law/document〉 constitute someone 〈office/role〉`＝権限者・法律・公式文書が人を役職・役割に任命する／`someone be constituted 〈office/role〉`＝人が役職に任命される／`a legally constituted 〈officer/official〉`＝法に基づいて正式に任命された役職者  \n\n【コロケーション】\n\n・`constitute someone 〈office/role〉`  \n用途: 人を特定の役職・職務に就けることを、古風または法律的に述べる。  \n例: The charter constituted him treasurer of the association.  \n訳: その憲章によって、彼は協会の会計役に任命された。  \n\n・`be constituted 〈office/role〉`  \n用途: 人が役職・地位に正式に任命されたことを受動態で示す。  \n例: She was constituted guardian for the limited purpose stated in the order.  \n訳: 彼女は、その命令に記された限定的な目的のための後見人に任命された。  \n\n・`a legally constituted 〈officer/official〉`  \n用途: 法や制度に基づいて正式に任命された役職者を指す。  \n例: The charter identifies the treasurer as a legally constituted officer of the association.  \n訳: その憲章は、会計役を協会において法に基づき正式に任命された役職者として明記している。  \n\n【語法・注意】人を直接目的語にし、役職を目的格補語として置く `constitute someone treasurer` のような形で使う。現代の一般文では非常に硬いため、通常は `appoint someone treasurer` などとする。  \n\n語義3は committee や court などの組織そのものを成立させ、語義4は person を役職・地位に就ける。`constitute a committee` と `constitute someone treasurer` を同じ目的語構造として扱わない。  \n`a legally constituted officer` は「構成された役職者」という逐語訳ではなく、「法に基づいて正式に任命された役職者」を意味する。  \n\n【類義語】\n\n・appoint  \n定義: 人を役職・職務に正式に就ける。  \n頻度: 〈9/10〉  \n違い: appoint は現代英語の標準表現で、constitute より広く自然に使う。constitute は法律・公文書などの硬い公式文体に現れる。  \n例: The board appointed Maya treasurer.  \n訳: 取締役会はマヤを会計責任者に任命した。  \n\n・designate  \n定義: 人を特定の役割・地位の担当者として公式に指定する。  \n頻度: 〈7/10〉  \n違い: designate は役割を割り当て、明示することに焦点がある。constitute は法律・公式文体で、人をその役職・地位に正式に就けることを表す。  \n例: The minister designated Lee as the official spokesperson.  \n訳: 大臣はリーを公式報道官に指定した。  \n\n・name  \n定義: 人を役職・候補・受賞者などとして発表・指定する。  \n頻度: 〈9/10〉  \n違い: name は簡潔で一般的であり、発表・選定に焦点がある。constitute は法律・制度上の役職へ正式に任命する文脈で使われる。  \n例: The council named Rivera chair of the committee.  \n訳: 評議会はリベラを委員会の議長に指名した。  ",
  "_output_metadata": {
    "schema_version": "final_review_v2",
    "stage": "final_review",
    "run_id": "blind-constitute-20260908T024208Z-fd1caf1b",
    "context_id": "blind-constitute-context-20260908T024208Z-fd1caf1b",
    "input_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
    "prompt_sha256": "5fa21ad0e8186e05e00c459e6201d7062a5d550a003831b40e182ba27c7a625a",
    "input_artifacts": [
      "entry_body",
      "sealed_final_blind",
      "pre_blind_resolution",
      "post_blind_resolution",
      "checker_recheck_manifest",
      "targeted_adjudications",
      "final_review_spec"
    ],
    "blind_output_sha256": "5383af808e242403140d65d6c48197237bf3eced080ab53f62e9e4e36cf9173d"
  },
  "pass_findings": {
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-constitute-20260908T024208Z-fd1caf1b",
    "context_id": "normal-constitute-context-20260908T024208Z-fd1caf1b",
    "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
    "prompt_sha256": "5178f5a14a9525317811a34e6cd307108436f4babc1299fcd2eb9031f28ba737",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-09-08T03:18:09.145725+00:00",
    "pass_outputs": [
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "translation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "constitute-fresh-translation-1"
        },
        "findings": [
          {
            "id": "normal-translation-001",
            "taxonomy_id": "example_translation_alignment",
            "location": {
              "section": "lexical_relations",
              "line_start": 107,
              "line_end": 107,
              "exact_quote": "違い: 割合の用法では近いが、account for は「全体のうちどれだけを説明・占有するか」に焦点がある。constitute は割合だけでなく、部分が全体そのものを形作る関係にも使える。  "
            },
            "severity": "minor",
            "rationale": "この割合用法で必要なのは「全体のうちどれだけを占めるか」という数量関係だが、「占有する」は物や権利を所有・占拠する意味に寄り、直後の割合例が示す意味と日本語の述語が局所的にずれる。部分と全体の方向自体は逆転していない。",
            "evidence_link_ids": [],
            "suggested_direction": "「全体のうちどれだけを説明できるか・占めるか」のように、数量的な割合を表す「占める」へ直す。"
          }
        ]
      },
      {
        "pass_id": "sense-structure",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "constitute-fresh-sense-structure-1"
        },
        "findings": [
          {
            "id": "normal-sense-structure-001",
            "taxonomy_id": "sense_boundary_overlap",
            "location": {
              "section": "sense_structure",
              "line_start": 190,
              "line_end": 190,
              "exact_quote": "【日本語訳・定義】組織、委員会、裁判所、政府などを正式に形成・設置し、公式の組織体として成立させることを表す。制度や文脈によって所定の手続きや権限付与を伴うことはあるが、constitute という語だけで法的有効性や実際の活動可能性まで一律に保証するわけではない。  "
            },
            "severity": "blocking",
            "rationale": "語義3の境界が「組織体を設立する」に限定されているため、法的用法の constitute an agreement（契約・合意を所定の形式に整える）に収録先がない。これは単なる対象分野の違いではなく、既存の設立フレームとは目的語の意味タイプと結果状態が異なる使役的な法的形式化であり、現行の定義・文法パターン・コアイメージ第3枝はいずれも agreement を「公式の組織体」として扱えない。",
            "evidence_link_ids": [
              "F005"
            ],
            "suggested_direction": "語義3を「組織・会議体を正式に成立させる／契約などを所定の法的形式に整える」まで明示的に拡張し、対応する目的語と構文を追加する。両フレームを一つの簡潔な定義で扱えない場合は、法的形式化を独立した語義として分割し、コアイメージにも対応枝を設ける。"
          }
        ],
        "unrouted_observations": []
      },
      {
        "pass_id": "frame-relation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "constitute-fresh-frame-relation-1"
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
          "blind_request_sha256": "192e4f92a6860dc8dca03245ec288359519ca4d13d67bd2eac7950bd30c5099e",
          "recorded_at": "2026-09-08T12:05:04+09:00",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "constitute-fresh-frame-relation-1"
          },
          "axes": []
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
          "stage2_request_sha256": "1ebd66dce0dc26cf8fd28ca373151258bb4d356db04b0378b11560e3ed310909",
          "blind_record_sha256": "24e9387e5773734a49f69fa844589de6d3615534ff559cc50c927ca9eb8dea65",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "constitute-fresh-frame-relation-1"
          },
          "adjudications": [],
          "frame_findings": [],
          "unrouted_observations": []
        },
        "aligned_at": "2026-09-08T03:18:26.264118+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "constitute-fresh-example-attribution-1"
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "pass_id": "example-attribution",
          "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
          "blind_request_sha256": "70e21040dce2821a824963110854118f966213806e57e481100140edf2f9e635",
          "recorded_at": "2026-09-08T03:06:30.391474Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "constitute-fresh-example-attribution-1"
          },
          "attributions": [
            {
              "example_id": "ex-20739e4f6ab2",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "constitute a breach of the agreement"
              ],
              "rationale": "「constitute a breach of the agreement」では、データ共有という行為が契約違反という分類に当たる関係なのでsense:002である。sense:001なら主語が目的語の全体またはその割合を構成する必要があるが、breachは構成される全体・部分量ではない。"
            },
            {
              "example_id": "ex-6580bc19b1b9",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "legally constituted officer"
              ],
              "rationale": "「legally constituted officer」は人である役職者が法的に任命された結果状態を表すためsense:004である。sense:003は委員会・政府などの組織体の正式設立だが、ここでconstitutedが直接修飾するofficerは組織体ではない。"
            },
            {
              "example_id": "ex-ce5a776418c8",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "constitute a criminal offence"
              ],
              "rationale": "「constitute a criminal offence」では記録改ざんという行為が刑事犯罪の成立条件を満たすかを述べるのでsense:002である。sense:003なら目的語が設立される組織体となるが、criminal offenceは組織ではない。"
            },
            {
              "example_id": "ex-8e811b406263",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "a significant part of the annual budget"
              ],
              "rationale": "「a significant part of the annual budget」が部分量とその全体を明示し、維持費が予算の一部を占めるsense:001に一意に帰属する。sense:002の分類・評価なら目的語自体がbreachやriskのようなカテゴリーとなるが、このpart of句は部分全体関係を符号化する。"
            },
            {
              "example_id": "ex-3250194bfa48",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "Twelve jurors constitute the full jury"
              ],
              "rationale": "「Twelve jurors constitute the full jury」では構成員である12人が全体である陪審を形成する能動の部分→全体関係なのでsense:001である。sense:003なら権限主体がjuryという組織を正式に設立する行為となるが、主語のjurorsはここでは設立者ではなく構成員である。"
            },
            {
              "example_id": "ex-fd73f5de867d",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "a tribunal to be constituted"
              ],
              "rationale": "「a tribunal to be constituted」は紛争時に審判機関を成立させる受動構文でありsense:003である。sense:001の受動的な組成なら通常partsを示すof句などが必要だが、この文は組成要素ではなく設置時点をwhen節で示す。"
            },
            {
              "example_id": "ex-924a4fd85622",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "the majority of the evening staff"
              ],
              "rationale": "「the majority of the evening staff」は非常勤職員が夜間スタッフ全体の過半数を占める割合関係を明示するためsense:001である。sense:002ならmajorityを分類・評価として認定する読みになるが、of the evening staffが全体に対する数量部分であることを直接示す。"
            },
            {
              "example_id": "ex-68e8f9d29819",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "constituted him treasurer"
              ],
              "rationale": "「constituted him treasurer」は人himを役職treasurerにする目的語＋目的格補語の任命構文なのでsense:004である。sense:003なら目的語そのものが設立対象の組織となるが、この文では人とその就任役職が別々に現れる。"
            },
            {
              "example_id": "ex-7022004a7a23",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "what constitutes acceptable use"
              ],
              "rationale": "「what constitutes acceptable use」は何がacceptable useという分類の成立条件を満たすかを問うためsense:002である。sense:001ならwhatが全体を作る部分となる必要があるが、acceptable useは構成物ではなく規範的カテゴリーである。"
            },
            {
              "example_id": "ex-5b909f57236c",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "She was constituted guardian"
              ],
              "rationale": "「She was constituted guardian」は人Sheが役割guardianに任命される受動の任命構文なのでsense:004である。sense:003は組織体の設立だが、主語は個人でguardianは就く役割であり組織ではない。"
            },
            {
              "example_id": "ex-a5fd77ea3b57",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "constitutes a serious risk to public safety"
              ],
              "rationale": "「constitutes a serious risk to public safety」では損傷した橋という状況を重大な危険と評価・分類するのでsense:002である。sense:001なら橋がriskという全体の構成部分になる関係だが、この文のriskは橋が該当する評価カテゴリーである。"
            },
            {
              "example_id": "ex-4637d54ddbed",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "35 percent of the company's revenue"
              ],
              "rationale": "「35 percent of the company's revenue」がオンライン販売の占める割合と全体を明示するのでsense:001である。sense:002の分類認定ではなく、percent ofという数量的な部分全体関係がconstituteの補部に直接現れている。"
            },
            {
              "example_id": "ex-01a49989788b",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "commission was constituted under the new environmental law"
              ],
              "rationale": "「commission was constituted under the new environmental law」は委員会が法律に基づいて正式に設置された結果を示すためsense:003である。sense:001ならcommissionの構成要素を示す読みになるが、この受動文のunder句は構成部分でなく設立根拠を表す。"
            },
            {
              "example_id": "ex-c3399241dc9b",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "constitutes a significant change"
              ],
              "rationale": "「constitutes a significant change」は改訂方針を会社の取り組み方における重大な変化と評価するためsense:002である。sense:001なら方針がchangeという全体を構成する部分でなければならないが、ここでは方針そのものがchangeに当たる。"
            },
            {
              "example_id": "ex-eae1a2d1edd9",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "is constituted of experts"
              ],
              "rationale": "「is constituted of experts」は全体panelとその構成要素expertsをof句で結ぶ組成関係なのでsense:001である。sense:003の正式設立ならconstitutedは機関の成立を表すが、このof句は設立権限や根拠ではなく構成員を提示している。"
            },
            {
              "example_id": "ex-3cd3bc2622ea",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "does not constitute proof of fraud"
              ],
              "rationale": "「does not constitute proof of fraud」は匿名メッセージが詐欺の証明として成立するかを否定する分類・評価なのでsense:002である。sense:001ならmessageがproofという全体の構成部分になる読みだが、否定と単数目的語proofは証拠資格の不足を判定している。"
            },
            {
              "example_id": "ex-d9ef24b6a41d",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "duly constituted board"
              ],
              "rationale": "「duly constituted board」は取締役会が適正な手続で正式に成立した結果状態を表すためsense:003である。sense:001の構成関係なら構成員やof句が必要だが、dulyはboardの組成内容ではなく設立の適正性をconstitutedに直接付加する。"
            },
            {
              "example_id": "ex-4bc1c5dc0c02",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "constituted an independent panel"
              ],
              "rationale": "「constituted an independent panel」では省が組織体panelを正式に設置する能動構文なのでsense:003である。sense:001なら主語が目的語全体を成す構成要素となるが、ministryはpanelの構成員ではなく設立主体である。"
            },
            {
              "example_id": "ex-3cfeeb6c7589",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "constitute a transitional government"
              ],
              "rationale": "「constitute a transitional government」では当事者らが暫定政府という組織体を発足させることに合意しておりsense:003である。sense:001ならpartiesが政府を構成する成員という静的関係になるが、agreed to constituteという意図的行為の不定詞が設立を示す。"
            }
          ]
        },
        "aligned_at": "2026-09-08T03:18:09.134173+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "qualification",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "constitute-fresh-qualification-1"
        },
        "findings": [
          {
            "id": "normal-qualification-001",
            "taxonomy_id": "absolute_scope_counterexample",
            "location": {
              "section": "word_formation",
              "line_start": 26,
              "line_end": 26,
              "exact_quote": "`constituent` — 名詞「構成要素、選挙区民」、形容詞「構成する」。政治の「選挙区民」は constitute の目的語ではなく、代表者を選ぶ constituency の構成員を指す。  "
            },
            "severity": "blocking",
            "rationale": "「選挙区民」は constitute の目的語ではない、という無限定の統語的主張には反例がある。たとえば `These voters constitute the senator's constituents.` では政治義の constituents が constitute の直接目的語になる。ここで説明すべきなのは constituent の語義・名称が『constitute の目的語』という関係から定義されるのではないことだが、現状の文は実際の文中で目的語にできないという禁止にも読め、誤った一般化を生む。",
            "evidence_link_ids": [],
            "suggested_direction": "絶対的な構文制約を削除し、「政治義の constituent は『constitute の目的語』を意味する名称ではなく、constituency の構成員を指す」のように語形成上の関係だけへ限定する。"
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
          "agent_id": "constitute-fresh-pronunciation-1"
        },
        "findings": []
      },
      {
        "pass_id": "evidence",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "constitute-fresh-evidence-1"
        },
        "findings": [
          {
            "id": "normal-evidence-001",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "pronunciation",
              "line_start": 15,
              "line_end": 15,
              "exact_quote": "米: /ˈkɑːnstəˌtuːt/｜英: /ˈkɒnstɪˌtjuːt/。3音節で、第1音節に主強勢、第3音節に第二強勢がある。米音では第1音節の母音が /ɑː/、第2音節が弱い /stə/、第3音節の初めが /t/ となる。英音では第1音節が /ɒ/、第2音節が /stɪ/、第3音節が /tjuːt/ となる。"
            },
            "severity": "blocking",
            "rationale": "C001 の F001 は米音の語末について /tuːt/ と /tjuːt/ の両方を記録し、F009 の根拠詳細も英音 /tjuːt/ に対して米音では一般的に /tuːt/ と限定している。本文は米音全般を単一の /tuːt/（第3音節初頭 /t/）として無限定に提示しており、引用根拠が示す米音 /tjuːt/ の変異を反映していない。",
            "evidence_link_ids": [
              "C001"
            ],
            "suggested_direction": "米音を『一般に /tuːt/』と限定し、/tjuːt/ も米音の変異として認められる旨を添えるか、米音を一つの代表形だけ示す表示だと明示する。"
          }
        ]
      }
    ],
    "checker_reviewers": {
      "translation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "constitute-fresh-translation-1"
      },
      "sense-structure": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "constitute-fresh-sense-structure-1"
      },
      "frame-relation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "constitute-fresh-frame-relation-1"
      },
      "example-attribution": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "constitute-fresh-example-attribution-1"
      },
      "qualification": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "constitute-fresh-qualification-1"
      },
      "pronunciation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "constitute-fresh-pronunciation-1"
      },
      "evidence": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "constitute-fresh-evidence-1"
      }
    },
    "independent_candidates": [],
    "summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency."
  },
  "cold_review": {
    "reviewer_agent_id": "constitute-fresh-cold-review-1",
    "model": "gpt-5",
    "summary": "記事全体は、主要語義の区分、用例、類義語との差、語源・発音の説明がおおむね正確である。低重大度の問題候補が1件ある。割合構文の説明が、文脈から全体が明らかな場合にも of 句が必須であるかのように読める。",
    "findings": [
      {
        "id": "cold-constitute-001",
        "location": "語義1「構成する、（全体の一定割合を）占める」の日本語訳・定義／文法パターン",
        "severity": "low",
        "description": "割合を表す constitute の構文で、全体を示す of 句が常に明示されるかのように一般化している。",
        "reason": "「一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は of 句に現れる。」という説明は、完全な形の構造説明としては有用だが、全体が文脈から回収できる場合の省略を扱っていない。たとえば、直前に対象集団が示されていれば `Women constitute 45 percent.` や `Part-time staff constitute the majority.` のように of 句なしでも自然に言える。このままだと、学習者が of 句を必須要素だと誤って一般化する可能性がある。",
        "suggested_direction": "全体は通常 `of ...` で示すが、文脈上明らかな場合は `constitute 45 percent` や `constitute the majority` のように省略できる、と補足する。文法パターンにも of 句を任意にできる表記または省略例を加える。",
        "scope_anchors": [
          {
            "id": "anchor-constitute-001-a",
            "exact_quote": "一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は of 句に現れる。",
            "location_hint": "語義1の【日本語訳・定義】第2文"
          },
          {
            "id": "anchor-constitute-001-b",
            "exact_quote": "`〈group/category〉 constitute 〈割合〉 of 〈whole〉`＝集団・分類が全体の一定割合を占める",
            "location_hint": "語義1の【文法パターン】中央"
          }
        ]
      }
    ],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "constitute-fresh-cold-review-1"
    },
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-constitute-20260908T024208Z-fd1caf1b",
    "context_id": "cold-constitute-context-20260908T024208Z-fd1caf1b",
    "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
    "prompt_sha256": "25c298d1a4305746147791bd442cd725a92737c8f0802b992ea88e5c6ff76a5d",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-08T03:25:44.325298+00:00"
  },
  "final_blind": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "reviewer_agent_id": "constitute-final-blind-1",
    "model": "gpt-5",
    "provisional_decision": "reject",
    "independent_candidates": [
      {
        "id": "IC-01",
        "surface_form": "constitute",
        "frame": "〈parts/members〉 constitute 〈whole/group〉",
        "meaning": "複数の部分・構成員が全体を構成する",
        "disposition": "included",
        "rationale": "〈parts/members〉 constitute 〈whole/group〉 は、主語側の要素から目的語側の全体へ向かう基本的な部分―全体関係を表し、記事はその方向を正しく区別している。",
        "semantic_assertions": [
          {
            "id": "IC-01-A1",
            "statement": "主語は目的語で表される全体の構成要素または構成員でなければならない。",
            "polarity": "must_hold",
            "scope": "能動態の parts-to-whole 構文"
          },
          {
            "id": "IC-01-A2",
            "statement": "このフレームを、全体を主語にして部分を目的語に取る方向として説明してはならない。",
            "polarity": "must_not_hold",
            "scope": "能動態の意味役割"
          }
        ]
      },
      {
        "id": "IC-02",
        "surface_form": "constitute",
        "frame": "〈group/category/item〉 constitute 〈percentage/majority/minority/part〉 (of 〈whole〉)",
        "meaning": "ある集団・項目が全体に占める割合または部分量を表す",
        "disposition": "included",
        "rationale": "〈group/category/item〉 constitute 〈percentage/majority/minority/part〉 (of 〈whole〉) は、完全な全体形成ではなく量的な占有関係を表す独立フレームであり、記事の用例と説明はこの境界を満たす。",
        "semantic_assertions": [
          {
            "id": "IC-02-A1",
            "statement": "目的語は主語が占める割合・多数／少数区分・部分量を表さなければならない。",
            "polarity": "must_hold",
            "scope": "割合・部分量フレーム"
          },
          {
            "id": "IC-02-A2",
            "statement": "of 句の全体は、文脈から回復できる場合に限って省略可能である。",
            "polarity": "must_hold",
            "scope": "割合・部分量フレームの省略"
          }
        ]
      },
      {
        "id": "IC-03",
        "surface_form": "be constituted of",
        "frame": "〈whole〉 be constituted of 〈parts/materials〉",
        "meaning": "全体が複数の部分・材料から構成されている",
        "disposition": "included",
        "rationale": "〈whole〉 be constituted of 〈parts/materials〉 は硬いが成立する受動的な構成表現であり、記事はより普通の be composed of / consist of とのレジスター差も示している。",
        "semantic_assertions": [
          {
            "id": "IC-03-A1",
            "statement": "主語は全体で、of 句はその構成要素または材料でなければならない。",
            "polarity": "must_hold",
            "scope": "be constituted of 構文"
          }
        ]
      },
      {
        "id": "IC-04",
        "surface_form": "constitute",
        "frame": "〈act/fact/situation/result〉 constitute 〈category/evaluation/state〉",
        "meaning": "行為・事実・状況などが分類・評価・状態に該当する",
        "disposition": "included",
        "rationale": "〈act/fact/situation/result〉 constitute 〈category/evaluation/state〉 は、部分―全体関係ではなく、主語が目的語の定義・評価に当たるという同定関係であり、記事は crime、breach、risk、change などを適切に扱う。",
        "semantic_assertions": [
          {
            "id": "IC-04-A1",
            "statement": "主語は目的語が表す分類・評価・状態の成立条件に該当すると判断されなければならない。",
            "polarity": "must_hold",
            "scope": "分類・評価用法"
          },
          {
            "id": "IC-04-A2",
            "statement": "constitute 自体を、その分類対象を引き起こす cause の意味として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "分類・評価用法"
          }
        ]
      },
      {
        "id": "IC-05",
        "surface_form": "does not constitute",
        "frame": "〈evidence/act/silence/etc.〉 does not constitute 〈proof/consent/approval/etc.〉",
        "meaning": "ある材料や行為だけでは所定の証明・同意・承認に該当するほど十分ではない",
        "disposition": "included",
        "rationale": "〈evidence/act/silence/etc.〉 does not constitute 〈proof/consent/approval/etc.〉 は分類境界の不充足を明示する定着した否定フレームであり、記事は prove という行為との混同も避けている。",
        "semantic_assertions": [
          {
            "id": "IC-05-A1",
            "statement": "否定は、主語が目的語の分類に達するための十分条件を満たさないことに作用しなければならない。",
            "polarity": "must_hold",
            "scope": "否定された分類フレーム"
          },
          {
            "id": "IC-05-A2",
            "statement": "このフレームを、主語が証拠によって何かを証明するという他動的な prove の意味にしてはならない。",
            "polarity": "must_not_hold",
            "scope": "proof/evidence を伴う否定フレーム"
          }
        ]
      },
      {
        "id": "IC-06",
        "surface_form": "what constitutes",
        "frame": "what constitutes 〈category/standard〉",
        "meaning": "何が特定の分類・基準を成立させるかを問う・定義する",
        "disposition": "included",
        "rationale": "what constitutes 〈category/standard〉 は、分類の境界や要件を問う埋込み疑問・自由関係節のフレームとして記事に正しく含まれている。",
        "semantic_assertions": [
          {
            "id": "IC-06-A1",
            "statement": "what は、目的語の分類・基準に該当する内容または条件を表さなければならない。",
            "polarity": "must_hold",
            "scope": "what constitutes フレーム"
          }
        ]
      },
      {
        "id": "IC-07",
        "surface_form": "constitute an agreement",
        "frame": "〈communications/documents/conduct/terms〉 constitute 〈agreement/contract〉",
        "meaning": "複数の言動・文書・条項などが総体として合意・契約に当たる",
        "disposition": "included",
        "rationale": "〈communications/documents/conduct/terms〉 constitute 〈agreement/contract〉 は分類・成立条件の用法であり、主語となる事実群が目的語の agreement / contract に該当するという方向で理解する必要がある。",
        "semantic_assertions": [
          {
            "id": "IC-07-A1",
            "statement": "主語となる言動・文書・条項が、目的語の合意・契約に該当するか、その成立条件を満たす関係でなければならない。",
            "polarity": "must_hold",
            "scope": "agreement/contract を目的語にする分類フレーム"
          },
          {
            "id": "IC-07-A2",
            "statement": "agreement/contract を、権限主体が目的語として法的形式に整える組織設立フレームへ自動的に移してはならない。",
            "polarity": "must_not_hold",
            "scope": "agreement/contract の語義帰属"
          }
        ]
      },
      {
        "id": "IC-08",
        "surface_form": "constitute",
        "frame": "〈authority/institution/parties〉 constitute 〈committee/body/court/government〉",
        "meaning": "権限主体などが組織・機関を公式に設立する",
        "disposition": "included",
        "rationale": "〈authority/institution/parties〉 constitute 〈committee/body/court/government〉 は、既存部分の構成関係ではなく、主体が制度的行為によって新たな組織体を成立させる用法として記事に適切に含まれている。",
        "semantic_assertions": [
          {
            "id": "IC-08-A1",
            "statement": "主語は組織体を公式に設ける行為主体で、目的語はその行為により成立する組織体でなければならない。",
            "polarity": "must_hold",
            "scope": "組織設立の能動フレーム"
          },
          {
            "id": "IC-08-A2",
            "statement": "単なる構成員と全体の静的関係を、公式な設立行為として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "組織設立と部分―全体の境界"
          }
        ]
      },
      {
        "id": "IC-09",
        "surface_form": "be constituted under/by",
        "frame": "〈body〉 be constituted under/by 〈law/charter/authority〉",
        "meaning": "機関が法律・憲章・権限主体を根拠または設立主体として公式に成立する",
        "disposition": "included",
        "rationale": "〈body〉 be constituted under/by 〈law/charter/authority〉 は設立根拠または設立主体を示す受動フレームであり、記事は by が構成要素を示す別解釈も持ち得ると注意している。",
        "semantic_assertions": [
          {
            "id": "IC-09-A1",
            "statement": "under 句は通常、機関の設立根拠となる法・憲章を表さなければならない。",
            "polarity": "must_hold",
            "scope": "be constituted under フレーム"
          },
          {
            "id": "IC-09-A2",
            "statement": "by 句は文脈により設立主体または構成要素となるため、前置詞だけで語義を固定してはならない。",
            "polarity": "must_not_hold",
            "scope": "be constituted by の曖昧性"
          }
        ]
      },
      {
        "id": "IC-10",
        "surface_form": "constituted",
        "frame": "a duly/properly/legally constituted 〈body/authority/meeting〉",
        "meaning": "機関・権限主体・会議が必要な手続きや構成要件を満たして正式に成立している",
        "disposition": "included",
        "rationale": "a duly/properly/legally constituted 〈body/authority/meeting〉 は、適式な設立・招集・構成を表す過去分詞修飾であり、個々の決定の適法性まで保証しないという記事の限定も適切である。",
        "semantic_assertions": [
          {
            "id": "IC-10-A1",
            "statement": "修飾対象そのものが必要な法的・手続的・構成上の要件を満たして成立していなければならない。",
            "polarity": "must_hold",
            "scope": "duly/properly/legally constituted の分詞修飾"
          },
          {
            "id": "IC-10-A2",
            "statement": "その修飾対象が行うすべての個別行為の適法性まで含意してはならない。",
            "polarity": "must_not_hold",
            "scope": "分詞修飾の含意範囲"
          }
        ]
      },
      {
        "id": "IC-11",
        "surface_form": "constitute",
        "frame": "〈authority/law/document〉 constitute someone 〈office/role〉",
        "meaning": "権限者・法・公式文書が人を役職・役割に正式に任命する",
        "disposition": "included",
        "rationale": "〈authority/law/document〉 constitute someone 〈office/role〉 は、人を直接目的語、役職を目的格補語とする古風・法律的な任命フレームであり、組織そのものを設立する用法とは意味役割が異なる。",
        "semantic_assertions": [
          {
            "id": "IC-11-A1",
            "statement": "直接目的語は任命される人、目的格補語はその人に付与される役職・役割でなければならない。",
            "polarity": "must_hold",
            "scope": "人の任命を表す能動フレーム"
          },
          {
            "id": "IC-11-A2",
            "statement": "一般的な現代文体で appoint と同程度に無標な表現として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "任命用法のレジスター"
          }
        ]
      },
      {
        "id": "IC-12",
        "surface_form": "be constituted",
        "frame": "someone be constituted 〈office/role〉",
        "meaning": "人が役職・役割に正式に任命される",
        "disposition": "included",
        "rationale": "someone be constituted 〈office/role〉 は任命用法の受動フレームであり、記事は人と役職の意味役割を維持したまま限定的・公式な用法として示している。",
        "semantic_assertions": [
          {
            "id": "IC-12-A1",
            "statement": "主語は任命される人で、補語は付与される役職・役割でなければならない。",
            "polarity": "must_hold",
            "scope": "人の任命を表す受動フレーム"
          }
        ]
      },
      {
        "id": "IC-13",
        "surface_form": "legally constituted",
        "frame": "a legally constituted 〈officer/official〉",
        "meaning": "法や制度に基づいて正式な地位・権限を与えられた役職者",
        "disposition": "included",
        "rationale": "a legally constituted 〈officer/official〉 は、役職者が適法な根拠によりその地位・権限を得ていることを表す分詞修飾として記事に適切に含まれている。",
        "semantic_assertions": [
          {
            "id": "IC-13-A1",
            "statement": "修飾される役職者は、法または制度上の正規の根拠により地位・権限を得ていなければならない。",
            "polarity": "must_hold",
            "scope": "役職者を修飾する legally constituted"
          }
        ]
      },
      {
        "id": "IC-14",
        "surface_form": "constitute",
        "frame": "constitute as 〈category/role〉",
        "meaning": "as を介して分類・評価または任命を表す一般的な基本構文",
        "disposition": "excluded",
        "rationale": "constitute as 〈category/role〉 は通常の基本構文としては採らず、分類用法では直接目的語、任命用法では人＋役職補語を取るという記事の境界が妥当である。",
        "semantic_assertions": [
          {
            "id": "IC-14-A1",
            "statement": "分類・評価用法の標準フレームに as を必須要素として立ててはならない。",
            "polarity": "must_not_hold",
            "scope": "分類・評価用法の補文型"
          }
        ]
      },
      {
        "id": "IC-15",
        "surface_form": "constitute",
        "frame": "〈authority/parties〉 constitute 〈agreement/contract〉",
        "meaning": "権限主体・当事者が契約を目的語に取り、それに所定の法的形式を与える",
        "disposition": "excluded",
        "rationale": "権限主体・当事者が契約を目的語に取り、それに所定の法的形式を与える という独立した使役的法律フレームは、組織を公式に設立する用法から agreement/contract へ一般化できず、通常の constitute an agreement は IC-07 の分類関係として扱うべきである。",
        "semantic_assertions": [
          {
            "id": "IC-15-A1",
            "statement": "agreement/contract を目的語とするだけで、主語がその法的形式を整える使役的設立用法が成立するとしてはならない。",
            "polarity": "must_not_hold",
            "scope": "agreement/contract を目的語にする想定上の使役フレーム"
          }
        ]
      },
      {
        "id": "IC-16",
        "surface_form": "constitution",
        "frame": "派生名詞 constitution",
        "meaning": "構成・体質、または国家・組織の基本原則を定める憲法・規約",
        "disposition": "included",
        "rationale": "constitution は constitute と同じ語族の主要な派生名詞であり、記事の「構成・体質」と「憲法・規約」という意味範囲は妥当である。",
        "semantic_assertions": [
          {
            "id": "IC-16-A1",
            "statement": "派生名詞は構成・体質の意味と、基本原則を定める憲法・規約の意味を区別して含まなければならない。",
            "polarity": "must_hold",
            "scope": "語形成欄の constitution"
          }
        ]
      },
      {
        "id": "IC-17",
        "surface_form": "constitutional / constitutionally",
        "frame": "派生形容詞 constitutional と派生副詞 constitutionally",
        "meaning": "構成上・体質上・憲法上の性質、またはその様態",
        "disposition": "included",
        "rationale": "constitutional / constitutionally は構成・体質・憲法に関わる形容詞／副詞として記事の語形成欄に適切に含まれている。",
        "semantic_assertions": [
          {
            "id": "IC-17-A1",
            "statement": "形容詞と副詞の品詞差を保ち、体質的意味と憲法上の意味の双方を文脈に応じて認めなければならない。",
            "polarity": "must_hold",
            "scope": "語形成欄の constitutional / constitutionally"
          }
        ]
      },
      {
        "id": "IC-18",
        "surface_form": "constituent",
        "frame": "派生名詞・形容詞 constituent",
        "meaning": "構成要素・選挙区民、または構成する性質",
        "disposition": "included",
        "rationale": "constituent は名詞「構成要素・選挙区民」と形容詞「構成する」を持ち、政治義を constituency の構成員として説明する記事の境界も適切である。",
        "semantic_assertions": [
          {
            "id": "IC-18-A1",
            "statement": "政治義の constituent は代表者を選ぶ constituency の構成員を指さなければならない。",
            "polarity": "must_hold",
            "scope": "語形成欄の政治義 constituent"
          },
          {
            "id": "IC-18-A2",
            "statement": "政治義を constitute の文法上の目的語という関係から定義してはならない。",
            "polarity": "must_not_hold",
            "scope": "語形成欄の政治義 constituent"
          }
        ]
      },
      {
        "id": "IC-19",
        "surface_form": "reconstitute",
        "frame": "派生動詞 reconstitute 〈thing/substance〉",
        "meaning": "再構成する、元の状態へ戻す、または乾燥品などを液体で戻す",
        "disposition": "included",
        "rationale": "reconstitute は再構成・復元に加え、乾燥食品や薬剤などへ液体を加えて使用可能な状態へ戻す専門的用法を持ち、記事の説明は妥当である。",
        "semantic_assertions": [
          {
            "id": "IC-19-A1",
            "statement": "液体を加える専門用法では、乾燥・濃縮された対象を所定の状態または濃度へ戻す作用でなければならない。",
            "polarity": "must_hold",
            "scope": "語形成欄の reconstitute"
          }
        ]
      }
    ],
    "article_findings": [
      {
        "id": "AF-01",
        "taxonomy_id": "sense_boundary_overlap",
        "location": {
          "section": "sense_structure",
          "line_start": 196,
          "line_end": 196,
          "exact_quote": "`constitute 〈agreement/body〉`＝契約・組織体に所定の法的形式を与える"
        },
        "severity": "blocking",
        "rationale": "「`constitute 〈agreement/body〉`＝契約・組織体に所定の法的形式を与える」は、正当な組織設立フレームと、agreement を目的語にする別の意味関係を一括している。さらに「法律文脈の `constitute an agreement/body` は、契約や組織体に必要な法的形式を与える意味になり得る。」と反復しているが、通常の constitute an agreement/contract は、言動・文書・条項などが合意・契約に「当たる／それを成す」という語義2の分類・成立条件フレームである。authority/parties が agreement を目的語に取って法的形式を付与するという使役的フレームを、constitute a body から一般化して教えるのは語義混入であり、学習者に不自然な産出を促すため修正が必要である。agreement/contract は語義2側へ再分類し、語義3は committee/body/court/government など公式に成立させる対象に限定すべきである。",
        "scope_anchors": [
          {
            "id": "AF-01-S1",
            "exact_quote": "`constitute 〈agreement/body〉`＝契約・組織体に所定の法的形式を与える",
            "location_hint": "語義3・文法パターン"
          },
          {
            "id": "AF-01-S2",
            "exact_quote": "法律文脈の `constitute an agreement/body` は、契約や組織体に必要な法的形式を与える意味になり得る。",
            "location_hint": "語義3・語法・注意"
          }
        ]
      }
    ],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "constitute-final-blind-1"
    },
    "run_id": "blind-constitute-20260908T024208Z-fd1caf1b",
    "context_id": "blind-constitute-context-20260908T024208Z-fd1caf1b",
    "input_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
    "prompt_sha256": "3a481b4b5b1236ff386e148bcacc574570b305e79f5e155e9afcd34091f7785c",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-08T04:18:57.569127+00:00"
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/c/constitute.md",
    "body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
    "final_blind_path": "audits/runs/c/constitute/20260908T024208Z-fd1caf1b/final_blind.json",
    "final_blind_sha256": "dd3b59cc2c2c68157bd84d96e995017bc6f8806e4232ba100bb8db71b8ec49d1",
    "blind_output_sha256": "5383af808e242403140d65d6c48197237bf3eced080ab53f62e9e4e36cf9173d",
    "sealed_at": "2026-09-08T13:21:07.351378+09:00"
  },
  "pre_blind_resolution": {
    "schema_version": "pre_blind_resolution_v1",
    "stage": "pre_blind_resolution",
    "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
    "output_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
    "recorded_at": "2026-09-08T03:31:33Z",
    "resolutions": [
      {
        "id": "normal-translation-001",
        "finding_id": "normal-translation-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "割合用法の account for は所有・占拠ではなく説明可能性または数量的割合を表すため、日本語を「説明できるか・占めるか」に修正した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "id": "normal-sense-structure-001",
        "finding_id": "normal-sense-structure-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "既存根拠 F005 が契約・組織体に所定の法的形式を与える用法を支えるため、語義3の定義・フレーム・コアイメージを法的形式化まで拡張した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "id": "normal-qualification-001",
        "finding_id": "normal-qualification-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "政治義 constituent が構文上 constitute の目的語になれないという無限定の主張を避け、名称・語形成上の関係だけを説明する表現へ限定した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "id": "normal-evidence-001",
        "finding_id": "normal-evidence-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "既存根拠 F001・F009 に合わせ、米音 /tuːt/ を一般形と限定し、米音にも /tjuːt/ の変異があることを明記した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "id": "cold-constitute-001",
        "finding_id": "cold-constitute-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "割合構文の全体を示す of 句は文脈上明らかな場合に省略できるため、定義と文法パターンの両方へ任意性を明記した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
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
    "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
    "output_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
    "recorded_at": "2026-09-08T03:31:33Z",
    "changed_units": [
      "core_image",
      "frames",
      "frequency_register",
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
    "full_recheck": true,
    "fallback_reasons": [
      "multiple_semantic_sections_changed"
    ],
    "reusable_passes": []
  },
  "checker_recheck_manifest": {
    "schema_version": "checker_recheck_manifest_v1",
    "current_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
    "revision_plan_sha256": "2235080ee5f9b9407c6e265bb3ba8dfa29176c5595e5658d2a76ba9af5d38dce",
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
        "pass_id": "translation",
        "mode": "rechecked",
        "spec_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
        "normalized_input_sha256": "98b9a9516855e6ad9cb39ca510bee9377c8cfdf741cba0e02aa18f4665aa416c",
        "source_artifact_sha256": "5f6d9ba28f4d326922742c4946737b36b8ea92f0c7114c9465cde03ff2c616dc",
        "output_sha256": "30ad36a62c51d3402b435f62e6e7edc35046d5599f8535ab0b854a48a164db3b",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "pass_id": "sense-structure",
        "mode": "rechecked",
        "spec_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
        "normalized_input_sha256": "51196436ca513b414d760dfb18c7679efca4e311d6a8cdab474ba2c37ec540ed",
        "source_artifact_sha256": "5f6d9ba28f4d326922742c4946737b36b8ea92f0c7114c9465cde03ff2c616dc",
        "output_sha256": "8dd28da7019f6111ed4269e4c0bfad482246e852a10dc6695a9ced2bf86771f1",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "pass_id": "frame-relation",
        "mode": "rechecked",
        "spec_sha256": "3598ca81a5784639c6b43a0806d0981a985bf4174f424c744aad1dde787bfcef",
        "normalized_input_sha256": "fcf76b799739b4390b77c92dbad61f4974f578b0fcdeab80f7383cde7c0644c0",
        "source_artifact_sha256": "5f6d9ba28f4d326922742c4946737b36b8ea92f0c7114c9465cde03ff2c616dc",
        "output_sha256": "31ea7d7ce4ac155fee23294abe0394add9800959859fcc50e2c60fe1a4e64fb8",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "pass_id": "example-attribution",
        "mode": "rechecked",
        "spec_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
        "normalized_input_sha256": "63737defaff358de7b5cf97cac6724abe478a615ce219f0c9476111f75896f93",
        "source_artifact_sha256": "5f6d9ba28f4d326922742c4946737b36b8ea92f0c7114c9465cde03ff2c616dc",
        "output_sha256": "8b9a1a2bea20a5ad8420b2c2ed7c8f342471b855573771d0b7a80f0a4fd1019f",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "pass_id": "qualification",
        "mode": "rechecked",
        "spec_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
        "normalized_input_sha256": "f3437b588fe7bd5d8d80538dee057b57f53fb8fae74da6f2283fe592f0e02b7c",
        "source_artifact_sha256": "5f6d9ba28f4d326922742c4946737b36b8ea92f0c7114c9465cde03ff2c616dc",
        "output_sha256": "6e45be4d13c1e7b28a304dbb5bfb523beb0fbbe217881a5389da4061c9877371",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "pass_id": "pronunciation",
        "mode": "rechecked",
        "spec_sha256": "7e3e94267ac9f917c901c12580b91e570b5989df7adfbf2a39b833478c766d8a",
        "normalized_input_sha256": "c3bb89233a4b315dd6c100c3b824bf2ba386fe8e640a1cd99fab3634ec6d804e",
        "source_artifact_sha256": "5f6d9ba28f4d326922742c4946737b36b8ea92f0c7114c9465cde03ff2c616dc",
        "output_sha256": "b2a07a0fc53562eabb8344b55273e3c44e9b1a7b451b5e4285f8548072bfd66b",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "pass_id": "evidence",
        "mode": "rechecked",
        "spec_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
        "normalized_input_sha256": "d68343aea4f95c11a39b3af2673ff19f6d3938a12ea5551b6b671415e800094a",
        "source_artifact_sha256": "5f6d9ba28f4d326922742c4946737b36b8ea92f0c7114c9465cde03ff2c616dc",
        "output_sha256": "467bd8e246f37f1a95a520afa1a529c057635f7022114511db43845d1c4455b6",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      }
    ]
  },
  "post_blind_resolution": {
    "schema_version": "post_blind_resolution_v1",
    "resolutions": [
      {
        "id": "AF-01",
        "finding_id": "AF-01",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "指摘は通常の分類用法 constitute an agreement と、既存根拠 F005 が明示する法律用法「agreement または body に所定・適法な形式を与える」を同一視している。本文は後者を法律文脈に限定し、法的有効性を一律に保証しないとも明記しており、U007/C007の直接根拠範囲内であるため修正しない。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
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
    "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
    "checker_recheck_completed": true,
    "final_blind_repeated": false,
    "final_blind_sha256": "dd3b59cc2c2c68157bd84d96e995017bc6f8806e4232ba100bb8db71b8ec49d1",
    "attempt_number": 1
  },
  "targeted_adjudications": {
    "requests": [],
    "adjudications": []
  },
  "source_inventory": {
    "schema_version": "source_inventory_v2",
    "stage": "source_inventory",
    "run_id": "20260908T024208Z-fd1caf1b",
    "context_id": "source-constitute-20260908T024208Z-fd1caf1b",
    "input_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
    "prompt_sha256": "9b098479af4d18acf89543a2b62c81ed21f99aac429743bed1aa2b0c489864dd",
    "recorded_at": "2026-09-08T02:59:08.052546Z",
    "input_artifacts": [
      "headword",
      "source_first_spec"
    ],
    "headword": "constitute",
    "source_first_audit": {
      "version": "source_first_audit_v2",
      "profile": "extended",
      "profile_reason": "post-cold recheck budget exhausted after evidence-driven revision; fresh validation required before merge",
      "limits": {
        "max_sources": 8,
        "max_facts": 80,
        "max_research_rounds": 3,
        "max_post_cold_rechecks": 2,
        "max_final_attempts": 2
      },
      "usage": {
        "sources_used": 7,
        "facts_used": 26,
        "research_rounds_used": 2,
        "post_cold_rechecks_used": 0,
        "final_attempts_used": 1
      },
      "research_status": "complete",
      "stop_reason": "coverage_axes_closed",
      "open_questions": [],
      "inventory_completed_before_article_comparison": true,
      "inventory_completed_at": "2026-09-08T00:12:00Z",
      "article_comparison_started_at": "2026-09-08T00:12:01Z",
      "coverage_axes": [
        {
          "axis": "lexical_senses",
          "status": "covered",
          "source_fact_ids": [
            "F003",
            "F004",
            "F005",
            "F006",
            "F007",
            "F010",
            "F011",
            "F012",
            "F013",
            "F014",
            "F015",
            "F017"
          ]
        },
        {
          "axis": "part_of_speech_and_frames",
          "status": "covered",
          "source_fact_ids": [
            "F002",
            "F005",
            "F006",
            "F010",
            "F011",
            "F012",
            "F013",
            "F014"
          ]
        },
        {
          "axis": "derived_and_related_forms",
          "status": "covered",
          "source_fact_ids": [
            "F002",
            "F021",
            "F022",
            "F023",
            "F024",
            "F025",
            "F026"
          ]
        },
        {
          "axis": "specialist_and_legal_uses",
          "status": "covered",
          "source_fact_ids": [
            "F005",
            "F006",
            "F007",
            "F012",
            "F013",
            "F016"
          ]
        },
        {
          "axis": "register_region_and_frequency",
          "status": "covered",
          "source_fact_ids": [
            "F010",
            "F012",
            "F013",
            "F015",
            "F016",
            "F019"
          ]
        },
        {
          "axis": "pronunciation_and_etymology",
          "status": "covered",
          "source_fact_ids": [
            "F001",
            "F008",
            "F009",
            "F018",
            "F020"
          ]
        }
      ],
      "sources": [
        {
          "id": "merriam-webster-constitute",
          "locator": "https://www.merriam-webster.com/dictionary/constitute",
          "source_type": "dictionary",
          "source_role": "general_lexicon",
          "independence_group": "merriam-webster",
          "facts": [
            {
              "id": "F001",
              "form": "constitute",
              "kind": "pronunciation",
              "statement": "American pronunciation has primary stress on the first syllable and permits final /tuːt/ or /tjuːt/.",
              "source_detail": "Merriam-Webster headword pronunciation line records /ˈkän(t)-stə-ˌtüt/ and /-ˌtyüt/."
            },
            {
              "id": "F002",
              "form": "constituted",
              "kind": "derived_form",
              "statement": "Constituted is the past tense and past participle; constituting is the present participle.",
              "source_detail": "Merriam-Webster inflection line lists constituted and constituting and labels constitute transitive."
            },
            {
              "id": "F003",
              "form": "constitute",
              "kind": "definition",
              "statement": "Parts or members constitute a whole by making it up, forming it, or composing it.",
              "source_detail": "Merriam-Webster sense 1 defines constitute as make up, form, compose and gives twelve months constitute a year."
            },
            {
              "id": "F004",
              "form": "constitute",
              "kind": "definition",
              "statement": "Constitute can mean to set up, establish, or found an institution or government.",
              "source_detail": "Merriam-Webster sense 2 includes set up, establish, and constitute a provisional government."
            },
            {
              "id": "F005",
              "form": "constitute",
              "kind": "legal_use",
              "statement": "In legal use constitute can give an agreement or body due or lawful form.",
              "source_detail": "Merriam-Webster general and legal definitions record giving due or required legal form."
            },
            {
              "id": "F006",
              "form": "constitute",
              "kind": "legal_use",
              "statement": "Constitute can appoint a person to an office, function, or dignity.",
              "source_detail": "Merriam-Webster sense 3 and legal sense 1 explicitly record appointment to an office or function."
            },
            {
              "id": "F007",
              "form": "constitute",
              "kind": "legal_use",
              "statement": "An act or document may constitute something by qualifying as it, as when failure to act constitutes negligence.",
              "source_detail": "Merriam-Webster legal sense 3b defines qualify as and illustrates failure to act may constitute negligence."
            },
            {
              "id": "F008",
              "form": "constitute",
              "kind": "etymology",
              "statement": "Constitute came through Middle English from Latin constitutus, the participle of constituere, from com- plus statuere to set.",
              "source_detail": "Merriam-Webster Word History gives the Middle English and Latin derivation and links statuere with set."
            }
          ]
        },
        {
          "id": "collins-constitute",
          "locator": "https://www.collinsdictionary.com/dictionary/english/constitute",
          "source_type": "dictionary",
          "source_role": "general_lexicon",
          "independence_group": "collins",
          "facts": [
            {
              "id": "F009",
              "form": "constitute",
              "kind": "pronunciation",
              "statement": "British pronunciation uses /ɒ/ and /tjuːt/, while the American form commonly uses /tuːt/.",
              "source_detail": "Collins COBUILD and British/American pronunciation entries contrast UK /ˈkɒnstɪtjuːt/ with a US ending /tuːt/."
            },
            {
              "id": "F010",
              "form": "constitute",
              "kind": "grammar",
              "statement": "The equivalence sense is a non-continuous linking-like verb followed directly by a noun phrase.",
              "source_detail": "Collins COBUILD labels the sense link verb, no continuous, with the pattern VERB noun and examples constitute an offence and constitute a victory."
            },
            {
              "id": "F011",
              "form": "constitute",
              "kind": "definition",
              "statement": "People or things constitute a whole when they are the parts or members forming it, including a stated percentage.",
              "source_detail": "Collins COBUILD sense 2 defines the parts-to-whole relation and illustrates volunteers constituting over 95 percent of a workforce."
            },
            {
              "id": "F012",
              "form": "constitute",
              "kind": "definition",
              "statement": "A committee, government, court, or similar body is constituted when formally established and authorized to operate.",
              "source_detail": "Collins COBUILD sense 3 and British senses 3-4 record formal establishment and legal form for institutions and courts."
            },
            {
              "id": "F013",
              "form": "constitute",
              "kind": "definition",
              "statement": "Constitute can give a person an office or function, including in passive constituted expressions.",
              "source_detail": "Collins British and American entries define appointment and give legally constituted officer and he was constituted treasurer."
            },
            {
              "id": "F014",
              "form": "constituted",
              "kind": "grammar",
              "statement": "The passive construction constituted of can identify the materials or parts composing a whole.",
              "source_detail": "Collins American entry illustrates mortar constituted of lime and sand."
            },
            {
              "id": "F015",
              "form": "constitute",
              "kind": "register",
              "statement": "The physical sense set or place is archaic.",
              "source_detail": "Collins American sense 6 explicitly labels to set or place archaic."
            },
            {
              "id": "F016",
              "form": "constituted",
              "kind": "register",
              "statement": "The formal-establishment use is formal and is commonly realized in the passive.",
              "source_detail": "Collins COBUILD labels the body-establishment sense formal and usually passive."
            }
          ]
        },
        {
          "id": "etymonline-constitute",
          "locator": "https://www.etymonline.com/word/constitute",
          "source_type": "etymology_reference",
          "source_role": "etymology_reference",
          "independence_group": "etymonline",
          "facts": [
            {
              "id": "F017",
              "form": "constitute",
              "kind": "definition",
              "statement": "The parts-to-whole formation sense is recorded from the mid-fifteenth century.",
              "source_detail": "Etymonline dates the formation-as-a-necessary-part sense to the mid-15th century."
            },
            {
              "id": "F018",
              "form": "constitute",
              "kind": "etymology",
              "statement": "Latin constituere covered causing to stand, setting up, fixing, establishing, and forming something new.",
              "source_detail": "Etymonline lists these meanings for Latin constituere."
            },
            {
              "id": "F019",
              "form": "constitute",
              "kind": "register",
              "statement": "The appoint-to-office sense is historically old and is recorded from around 1400.",
              "source_detail": "Etymonline dates appoint or elect to an office or position of power to about 1400."
            },
            {
              "id": "F020",
              "form": "constitute",
              "kind": "etymology",
              "statement": "The Latin source combines an assimilated form of com- with statuere to set, ultimately related to the root meaning stand.",
              "source_detail": "Etymonline analyzes constituere as com- plus statuere and connects statuere to the PIE root meaning stand."
            }
          ]
        },
        {
          "id": "merriam-webster-constitution",
          "locator": "https://www.merriam-webster.com/dictionary/constitution",
          "source_type": "dictionary",
          "source_role": "related_form_reference",
          "independence_group": "merriam-webster",
          "facts": [
            {
              "id": "F021",
              "form": "constitution",
              "kind": "derived_form",
              "statement": "Constitution is a noun for structure or physical makeup and for fundamental governing principles or their written instrument.",
              "source_detail": "Merriam-Webster constitution senses cover physical makeup, structure, organization, fundamental laws, and the written governing instrument."
            }
          ]
        },
        {
          "id": "merriam-webster-constitutional",
          "locator": "https://www.merriam-webster.com/dictionary/constitutional",
          "source_type": "dictionary",
          "source_role": "related_form_reference",
          "independence_group": "merriam-webster",
          "facts": [
            {
              "id": "F022",
              "form": "constitutional",
              "kind": "derived_form",
              "statement": "Constitutional is an adjective for constitution-related, constitution-authorized, bodily-constitution, or fundamental-makeup senses.",
              "source_detail": "Merriam-Webster adjective senses cover constitutional law, bodily makeup, and fundamental makeup."
            },
            {
              "id": "F023",
              "form": "constitutionally",
              "kind": "derived_form",
              "statement": "Constitutionally is the adverb derived from constitutional.",
              "source_detail": "Merriam-Webster records constitutionally as an adverb under constitutional."
            }
          ]
        },
        {
          "id": "merriam-webster-constituent",
          "locator": "https://www.merriam-webster.com/dictionary/constituent",
          "source_type": "dictionary",
          "source_role": "related_form_reference",
          "independence_group": "merriam-webster",
          "facts": [
            {
              "id": "F024",
              "form": "constituent",
              "kind": "derived_form",
              "statement": "Constituent as a noun can mean an essential component or a member of a political constituency.",
              "source_detail": "Merriam-Webster noun senses distinguish component and constituency-member meanings."
            },
            {
              "id": "F025",
              "form": "constituent",
              "kind": "derived_form",
              "statement": "Constituent as an adjective means serving to form or make up a whole.",
              "source_detail": "Merriam-Webster adjective sense 1 defines constituent as forming or composing a whole."
            }
          ]
        },
        {
          "id": "merriam-webster-reconstitute",
          "locator": "https://www.merriam-webster.com/dictionary/reconstitute",
          "source_type": "dictionary",
          "source_role": "related_form_reference",
          "independence_group": "merriam-webster",
          "facts": [
            {
              "id": "F026",
              "form": "reconstitute",
              "kind": "derived_form",
              "statement": "Reconstitute means constitute again or anew, especially restore by adding water or another liquid.",
              "source_detail": "Merriam-Webster defines reconstitute as constitute again or anew and especially restore by adding water."
            }
          ]
        }
      ],
      "source_union": [
        {
          "id": "U001",
          "source_fact_ids": [
            "F001",
            "F009"
          ],
          "canonical_statement": "Constitute has first-syllable primary stress, with UK /ɒ/ and /tjuːt/ and common US /ɑː/ and /tuːt/ realizations.",
          "disposition": "included",
          "rationale": "The pronunciation section records the regionally differentiated forms."
        },
        {
          "id": "U002",
          "source_fact_ids": [
            "F002"
          ],
          "canonical_statement": "Constituted and constituting are listed as inflected forms of the transitive verb constitute.",
          "disposition": "excluded",
          "rationale": "The selected locator lists the forms but does not atomically label each grammatical function, so the article omits the bundled inflection claim."
        },
        {
          "id": "U003",
          "source_fact_ids": [
            "F003",
            "F011",
            "F017"
          ],
          "canonical_statement": "Parts, members, or a category constitute a whole or a share of it in the parts-to-whole sense.",
          "disposition": "included",
          "rationale": "Sense 1 and its central frames directly express this well-attested relation."
        },
        {
          "id": "U004",
          "source_fact_ids": [
            "F007",
            "F010"
          ],
          "canonical_statement": "An act, fact, or situation constitutes a category when it qualifies as or can be regarded as that category.",
          "disposition": "included",
          "rationale": "Sense 2 separates this linking-like classification meaning from composition."
        },
        {
          "id": "U005",
          "source_fact_ids": [
            "F004",
            "F012",
            "F016",
            "F018"
          ],
          "canonical_statement": "Constitute formally establishes and authorizes an institution, committee, government, court, or similar body.",
          "disposition": "included",
          "rationale": "Sense 3 covers formal institutional establishment and its passive realization."
        },
        {
          "id": "U006",
          "source_fact_ids": [
            "F006",
            "F013",
            "F019"
          ],
          "canonical_statement": "In formal or legal language constitute can appoint a person to an office or function.",
          "disposition": "included",
          "rationale": "Sense 4 includes both direct-complement and as-complement appointment frames and labels their register."
        },
        {
          "id": "U007",
          "source_fact_ids": [
            "F005"
          ],
          "canonical_statement": "Constitute can give a body or agreement the form required for legal validity.",
          "disposition": "integrated",
          "rationale": "The lawful-form aspect is integrated into the formal-establishment sense without asserting universal legal effects."
        },
        {
          "id": "U008",
          "source_fact_ids": [
            "F014"
          ],
          "canonical_statement": "The passive constituted of construction may identify the components of a whole.",
          "disposition": "included",
          "rationale": "Sense 1 teaches this formal passive alongside the active direction contrast."
        },
        {
          "id": "U009",
          "source_fact_ids": [
            "F008",
            "F020"
          ],
          "canonical_statement": "Constitute derives through Middle English from Latin constituere, built from com- and statuere and associated with setting or establishing.",
          "disposition": "included",
          "rationale": "The etymology section presents the attested source and a restrained semantic bridge."
        },
        {
          "id": "U010",
          "source_fact_ids": [
            "F021"
          ],
          "canonical_statement": "Constitution is the related noun for makeup or structure and for fundamental governing principles or their document.",
          "disposition": "included",
          "rationale": "The word-formation section records these principal learner-relevant senses."
        },
        {
          "id": "U011",
          "source_fact_ids": [
            "F022"
          ],
          "canonical_statement": "Constitutional is the related adjective for bodily or structural makeup and for a governing constitution.",
          "disposition": "included",
          "rationale": "The word-formation section records both broad sense families."
        },
        {
          "id": "U012",
          "source_fact_ids": [
            "F023"
          ],
          "canonical_statement": "Constitutionally is the adverb derived from constitutional.",
          "disposition": "included",
          "rationale": "The word-formation section identifies the adverb and its broad meanings."
        },
        {
          "id": "U013",
          "source_fact_ids": [
            "F024",
            "F025"
          ],
          "canonical_statement": "Constituent is a related noun for a component or constituency member and an adjective meaning forming a whole.",
          "disposition": "included",
          "rationale": "The word-formation section distinguishes the noun and adjective and warns against confusing the political noun with a verb object."
        },
        {
          "id": "U014",
          "source_fact_ids": [
            "F026"
          ],
          "canonical_statement": "Reconstitute means constitute anew or restore a material by adding liquid.",
          "disposition": "included",
          "rationale": "The word-formation section records both the compositional and specialized restoration meanings."
        },
        {
          "id": "U015",
          "source_fact_ids": [
            "F015"
          ],
          "canonical_statement": "The physical set-or-place sense of constitute is archaic.",
          "disposition": "excluded",
          "rationale": "The generation inventory excludes this obsolete physical-placement sense because it has negligible modern learner value."
        }
      ],
      "claim_units": [
        {
          "id": "C001",
          "union_ids": [
            "U001"
          ],
          "subject_form": "constitute",
          "claim_type": "pronunciation",
          "statement": "Constitute has regionally differentiated UK and US pronunciation patterns.",
          "article_target_ids": [
            "pronunciation:001"
          ],
          "source_supports": [
            {
              "source_fact_id": "F001",
              "support_summary": "Merriam-Webster directly records the American stressed form and /tuːt/ or /tjuːt/ variation."
            },
            {
              "source_fact_id": "F009",
              "support_summary": "Collins independently contrasts British /ɒ, tjuːt/ with the common American /tuːt/ ending."
            }
          ]
        },
        {
          "id": "C003",
          "union_ids": [
            "U003"
          ],
          "subject_form": "constitute",
          "claim_type": "sense",
          "statement": "Parts or members constitute a whole, and a category may constitute a stated share of the whole.",
          "article_target_ids": [
            "definition:001",
            "grammar_pattern:001",
            "grammar_pattern:002"
          ],
          "source_supports": [
            {
              "source_fact_id": "F003",
              "support_summary": "Merriam-Webster defines the parts-to-whole sense as make up, form, or compose."
            },
            {
              "source_fact_id": "F011",
              "support_summary": "Collins independently defines members forming a whole and supplies a percentage example."
            },
            {
              "source_fact_id": "F017",
              "support_summary": "Etymonline confirms that the formation-as-a-part meaning is historically established."
            }
          ]
        },
        {
          "id": "C004",
          "union_ids": [
            "U004"
          ],
          "subject_form": "constitute",
          "claim_type": "sense",
          "statement": "A fact or act constitutes a category when it qualifies as or can be regarded as that category.",
          "article_target_ids": [
            "definition:002",
            "grammar_pattern:004",
            "usage_note:004"
          ],
          "source_supports": [
            {
              "source_fact_id": "F007",
              "support_summary": "Merriam-Webster legal usage directly defines constitute as qualify as and illustrates negligence."
            },
            {
              "source_fact_id": "F010",
              "support_summary": "Collins independently defines the regarded-as sense and specifies the direct VERB-noun pattern."
            }
          ]
        },
        {
          "id": "C005",
          "union_ids": [
            "U005"
          ],
          "subject_form": "constitute",
          "claim_type": "sense",
          "statement": "Constitute can formally establish and authorize an institution or public body.",
          "article_target_ids": [
            "definition:003",
            "grammar_pattern:008",
            "collocation:012",
            "collocation:013"
          ],
          "source_supports": [
            {
              "source_fact_id": "F004",
              "support_summary": "Merriam-Webster directly records set up, establish, found, and provisional-government use."
            },
            {
              "source_fact_id": "F012",
              "support_summary": "Collins independently defines formal establishment and authorization for committees and governments."
            },
            {
              "source_fact_id": "F016",
              "support_summary": "Collins marks this institutional-establishment sense formal and commonly passive."
            },
            {
              "source_fact_id": "F018",
              "support_summary": "Etymonline supplies the Latin establish-and-form semantic history supporting the restrained bridge."
            }
          ]
        },
        {
          "id": "C006",
          "union_ids": [
            "U006"
          ],
          "subject_form": "constitute",
          "claim_type": "sense",
          "statement": "Formal or legal constitute can appoint a person to an office or role.",
          "article_target_ids": [
            "definition:004",
            "grammar_pattern:011",
            "grammar_pattern:012",
            "register:004"
          ],
          "source_supports": [
            {
              "source_fact_id": "F006",
              "support_summary": "Merriam-Webster directly defines appointment to an office, function, or dignity."
            },
            {
              "source_fact_id": "F013",
              "support_summary": "Collins independently records legally constituted officer and constituted treasurer."
            },
            {
              "source_fact_id": "F019",
              "support_summary": "Etymonline records the appointment sense as an old use, supporting the register warning."
            }
          ]
        },
        {
          "id": "C007",
          "union_ids": [
            "U007"
          ],
          "subject_form": "constitute",
          "claim_type": "legal_use",
          "statement": "Constitute may give a body or agreement the required official or lawful form.",
          "article_target_ids": [
            "definition:003",
            "usage_note:009"
          ],
          "source_supports": [
            {
              "source_fact_id": "F005",
              "support_summary": "Merriam-Webster explicitly records giving an agreement or body due or required legal form."
            }
          ]
        },
        {
          "id": "C008",
          "union_ids": [
            "U008"
          ],
          "subject_form": "constituted of",
          "claim_type": "frame",
          "statement": "Constituted of may present the whole first and its component materials after of.",
          "article_target_ids": [
            "grammar_pattern:003",
            "collocation:005",
            "usage_note:002"
          ],
          "source_supports": [
            {
              "source_fact_id": "F014",
              "support_summary": "Collins directly illustrates the passive constituted of construction with material components."
            }
          ]
        },
        {
          "id": "C009",
          "union_ids": [
            "U009"
          ],
          "subject_form": "constitute",
          "claim_type": "etymology",
          "statement": "Constitute descends through Middle English from Latin constituere, involving com- and statuere.",
          "article_target_ids": [
            "etymology:001",
            "etymology:002"
          ],
          "source_supports": [
            {
              "source_fact_id": "F008",
              "support_summary": "Merriam-Webster gives the Middle English and Latin participial derivation."
            },
            {
              "source_fact_id": "F020",
              "support_summary": "Etymonline independently analyzes the com- plus statuere formation and stand root."
            }
          ]
        },
        {
          "id": "C010",
          "union_ids": [
            "U010"
          ],
          "subject_form": "constitution",
          "claim_type": "derived_form",
          "statement": "Constitution is the related noun for makeup, structure, or fundamental governing principles.",
          "article_target_ids": [
            "word_formation:002"
          ],
          "source_supports": [
            {
              "source_fact_id": "F021",
              "support_summary": "Merriam-Webster directly records structure, physical makeup, governing principles, and document senses."
            }
          ]
        },
        {
          "id": "C011",
          "union_ids": [
            "U011"
          ],
          "subject_form": "constitutional",
          "claim_type": "derived_form",
          "statement": "Constitutional is the related adjective for bodily or structural makeup and governing-constitution senses.",
          "article_target_ids": [
            "word_formation:003"
          ],
          "source_supports": [
            {
              "source_fact_id": "F022",
              "support_summary": "Merriam-Webster directly records constitutional adjective senses for makeup and a governing constitution."
            }
          ]
        },
        {
          "id": "C012",
          "union_ids": [
            "U012"
          ],
          "subject_form": "constitutionally",
          "claim_type": "derived_form",
          "statement": "Constitutionally is the adverb derived from constitutional.",
          "article_target_ids": [
            "word_formation:003"
          ],
          "source_supports": [
            {
              "source_fact_id": "F023",
              "support_summary": "Merriam-Webster explicitly lists constitutionally as the corresponding adverb."
            }
          ]
        },
        {
          "id": "C013",
          "union_ids": [
            "U013"
          ],
          "subject_form": "constituent",
          "claim_type": "derived_form",
          "statement": "Constituent can be a component or constituency member noun and a whole-forming adjective.",
          "article_target_ids": [
            "word_formation:004"
          ],
          "source_supports": [
            {
              "source_fact_id": "F024",
              "support_summary": "Merriam-Webster distinguishes the component and political constituency-member noun senses."
            },
            {
              "source_fact_id": "F025",
              "support_summary": "Merriam-Webster separately defines the adjective as serving to form or compose a whole."
            }
          ]
        },
        {
          "id": "C014",
          "union_ids": [
            "U014"
          ],
          "subject_form": "reconstitute",
          "claim_type": "derived_form",
          "statement": "Reconstitute means constitute anew and can mean restore by adding liquid.",
          "article_target_ids": [
            "word_formation:005"
          ],
          "source_supports": [
            {
              "source_fact_id": "F026",
              "support_summary": "Merriam-Webster directly defines both constitute anew and restoration by adding water."
            }
          ]
        }
      ]
    },
    "evidence_link_ids": [],
    "reused_from": "audits/runs/c/constitute/20260907T235852Z-0610bd0b/source_inventory.json"
  },
  "resolutions": {
    "schema_version": "resolutions_v1",
    "stage": "resolutions",
    "run_id": "resolution-constitute-20260908T024208Z-fd1caf1b",
    "context_id": "resolution-constitute-context-20260908T024208Z-fd1caf1b",
    "input_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
    "prompt_sha256": "7dfcaa0a828a334dbb84d1d31ed97312d0a9661a7aca70a7815a9f88b31ea2f1",
    "recorded_at": "2026-09-08T04:30:03Z",
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
        "rationale": "割合用法の account for は所有・占拠ではなく説明可能性または数量的割合を表すため、日本語を「説明できるか・占めるか」に修正した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "id": "normal-sense-structure-001",
        "finding_id": "normal-sense-structure-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "既存根拠 F005 が契約・組織体に所定の法的形式を与える用法を支えるため、語義3の定義・フレーム・コアイメージを法的形式化まで拡張した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "id": "normal-qualification-001",
        "finding_id": "normal-qualification-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "政治義 constituent が構文上 constitute の目的語になれないという無限定の主張を避け、名称・語形成上の関係だけを説明する表現へ限定した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "id": "normal-evidence-001",
        "finding_id": "normal-evidence-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "既存根拠 F001・F009 に合わせ、米音 /tuːt/ を一般形と限定し、米音にも /tjuːt/ の変異があることを明記した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "id": "cold-constitute-001",
        "finding_id": "cold-constitute-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "割合構文の全体を示す of 句は文脈上明らかな場合に省略できるため、定義と文法パターンの両方へ任意性を明記した。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      },
      {
        "id": "AF-01",
        "finding_id": "AF-01",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "指摘は通常の分類用法 constitute an agreement と、既存根拠 F005 が明示する法律用法「agreement または body に所定・適法な形式を与える」を同一視している。本文は後者を法律文脈に限定し、法的有効性を一律に保証しないとも明記しており、U007/C007の直接根拠範囲内であるため修正しない。",
        "resolved_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d"
      }
    ],
    "learning_delta": {
      "schema_version": "process_improvement_learning_delta_v2",
      "reviewed": true,
      "items": []
    }
  },
  "inventories": {
    "target_results": [
      {
        "id": "pronunciation:001",
        "kind": "pronunciation",
        "location": "line:4",
        "section": "＃発音記号",
        "sense": "",
        "text_sha256": "7d2100a784b5e533b913190b9de54a38171082fd2fa51c9ed812a8a8bd8a82b8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "米（一般的な形）: /ˈkɑːnstəˌtuːt/｜英: /ˈkɒnstɪˌtjuːt/。3音節で、第1音節に主強勢、第3音節に第二強勢がある。米音では第1音節の母音が /ɑː/、第2音節が弱い /stə/ となり、第3音節は一般に /tuːt/ だが /tjuːt/ の変異もある。英音では第1音節が /ɒ/、第2音節が /stɪ/、第3音節が /tjuːt/ となる。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text_sha256": "e24fef6ac81246adc7f1e8c4ee5e59432c76be3841173364d8966204aa4ea0a7",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "中英語を経て、ラテン語 constituere「立てる、据える、設ける、定める」に由来する。これは con- と statuere「立てる、置く」から成り、statuere は「立つ」を表す語根につながる。現在の「全体を構成する」「制度・組織を正式に成立させる」「人を役職に就ける」という用法には、「ある形・位置に据えて成立させる」という歴史的な意味が残っている。"
      },
      {
        "id": "etymology:002",
        "kind": "etymology",
        "location": "line:9",
        "section": "＃語源",
        "sense": "",
        "text_sha256": "330feda212c1e08c37201d45dba2e02fc1655d2bd9b65569032a2ddc2b9d6ac0",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "同語源・同じ語族の学習語には constitution「構成、体質、憲法」、constitutional「構成上の、憲法上の」、constituent「構成要素、選挙区民；構成する」、statute「制定法」がある。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "1f035e16b740822a9455dbcc86c721b5b2a967c25de7d30d67dd67d35cbeca5b",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`constitution` — 名詞。「構成・体質」のほか、国家・組織の基本原則を定める「憲法・規約」を表す。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "b835d9f84ff353478126887cd8f1ab36df8133d4caabf9b37e27d2896ceaaa0a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`constitutional / constitutionally` — 形容詞「構成上の、体質上の、憲法上の」／副詞「体質的に、憲法上」。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:15",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "2f193b9f22bca7ee53efc1a15b61b50bec4ba65e9000e02b985daac055a424fc",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`constituent` — 名詞「構成要素、選挙区民」、形容詞「構成する」。政治義の constituent は「constitute の目的語」を意味する名称ではなく、代表者を選ぶ constituency の構成員を指す。"
      },
      {
        "id": "word_formation:004",
        "kind": "word_formation",
        "location": "line:16",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "088ab58f744b6e9137fdfa156b2ad5c6b65cfd12437f234886d112fbb60c4df7",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`reconstitute` — 動詞「再構成する、元の状態に戻す」。乾燥食品・薬剤などに液体を加えて戻す用法もある。"
      },
      {
        "id": "core_image:001",
        "kind": "core_image",
        "location": "line:20",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "b6a16916bd55d39a2154519c5c59e4a1279af87ec1e45ba0c96f4ba68376e01e",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "constitute の共通核は、要素・行為・組織・人を、ある全体・分類・制度・役割として成り立つ位置に据えることである。文脈によって、すでにそうであるという関係を述べる場合と、意図的・正式に成立させる行為を述べる場合がある。"
      },
      {
        "id": "core_image:002",
        "kind": "core_image",
        "location": "line:21",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "4392abb542a0737095a3e49557e0921c08a58d24141b2b6d9e84681690eef777",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・要素を全体として成り立つ位置に据える → 「構成する、占める」（語義1）"
      },
      {
        "id": "core_image:003",
        "kind": "core_image",
        "location": "line:22",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "705427b6e0a6868336c62b314b095ea239d8c65c93fcaa230d1dbe9dd72c643b",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・行為や事実を分類として成り立つ位置に据える → 「～に当たる、～となる」（語義2）"
      },
      {
        "id": "core_image:004",
        "kind": "core_image",
        "location": "line:23",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "2d074eba10eff9b5fa684c70f5e9e6ba87dd3c37987cb4a37ff69ecd76f75f1a",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・組織や契約を正式な制度・法的形式として成り立つ位置に据える → 「正式に設立する、所定の形式に整える」（語義3）"
      },
      {
        "id": "core_image:005",
        "kind": "core_image",
        "location": "line:24",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "f816255f447e8c67aefc66f8f4b571de49c97740847f3d93d7ef5f756fba24ce",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・人を公的な役割として成り立つ位置に据える → 「正式に任命・指定する」（語義4）"
      },
      {
        "id": "sense_boundary:001",
        "kind": "sense_boundary",
        "location": "line:28",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "df99cb5d6121c3478200776c7f1e5cb049f9bb95cb1429d9b9169837a81a1c9c",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "1. 【他動詞】構成する、（全体の一定割合を）占める"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:30",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "92b3b7d027e117f4e4c5b07108a559c76e7b6c01834e71f266fd1cd367513350",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "一つまたは複数の人・物・部分・期間などが、一つの全体を形作る、またはその全体の一定割合・重要部分を占めることを表す。全体構成の能動構文では主語が構成要素、目的語がそれらによってできる全体である。一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は通常 of 句に現れるが、文脈上明らかな場合は省略できる。意図的に組み立てる行為ではなく、部分と全体の関係を記述することが多い。"
      },
      {
        "id": "frequency:001",
        "kind": "frequency",
        "location": "line:32",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "223f0f3bb105d64687ce0ff83ae044846c2f48c7a55d9d015dbc0ce12503d473",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈8/10〉"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "c7d96bc890cffcd054e6ba109df590fc883aafdd12123b9d11e8926d98cf9933",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "やや硬い標準語。報道、統計、学術、ビジネス、公式説明でよく使う。日常会話では make up や form の方が一般的なことが多い。"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:36",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "17c0771ea467251c5c9100adee599c1fa7d9823b225f38e1148175ecd2b606b9",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈parts/members〉 constitute 〈whole/group〉`＝部分・構成員が全体・集団を構成する"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:36",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "13cf23cd796f3faacb05e3039ecf2e6ecaaa37dcb156488d1563e56efb2a42ec",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈group/category〉 constitute 〈割合〉 (of 〈whole〉)`＝集団・分類が全体の一定割合を占める（全体が文脈上明らかなら of 句を省略可）"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:36",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "f8ec0f55d5db94e413ac1e1cca13573ecadcb90acf8fc8f4e75ba06a3573b1a9",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈whole〉 be constituted of 〈parts〉`＝全体が部分から構成されている"
      },
      {
        "id": "collocation:001",
        "kind": "collocation",
        "location": "lines:40-43",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "3858eb58d7c889d08baceeff0e0d259c30b66d5b3550c8d7c6e7b348d588a347",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`〈parts/members〉 constitute 〈whole/group〉`\n用途: 複数の部分・構成員が一つの全体や集団を作ることを述べる。\n例: Twelve jurors constitute the full jury in this court.\n訳: この裁判所では、12人の陪審員が陪審全体を構成する。"
      },
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:45-48",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "ccb9c7055fd56fbefa6b307a0799b38d471c8df9822c43643c7666b5a00707ee",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`constitute the majority/minority of 〈group〉`\n用途: ある分類の人・物が、集団の過半数または少数派を占めることを述べる。\n例: Part-time employees constitute the majority of the evening staff.\n訳: 非常勤職員が夜間スタッフの過半数を占めている。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:50-53",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "4e6d919101bc79bf806859460088435684a73695b63e0d63a7a866d7ad9ea010",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`constitute 〈percentage〉 of 〈whole〉`\n用途: 全体に占める割合を、統計的・客観的に示す。\n例: Online sales now constitute 35 percent of the company's revenue.\n訳: オンライン販売は現在、その会社の売上高の35パーセントを占めている。"
      },
      {
        "id": "collocation:004",
        "kind": "collocation",
        "location": "lines:55-58",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "a3ac0c0048dff7bcb0583fcc791240b01a4343bb907b9f9c572fd20041f93c92",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`constitute a large/significant part of 〈whole〉`\n用途: ある要素が全体の大きな部分・重要部分を占めることを示す。\n例: Maintenance costs constitute a significant part of the annual budget.\n訳: 維持費は年間予算のかなりの部分を占める。"
      },
      {
        "id": "collocation:005",
        "kind": "collocation",
        "location": "lines:60-63",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "d3eebd34871e19d250640c81511317136da381d391cc16b9eb2d888d0ee3551b",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`be constituted of 〈parts/materials〉`\n用途: 全体を主語にして、その構成要素や材料を示す硬い受動表現。\n例: The panel is constituted of experts from five different fields.\n訳: その委員会は5つの異なる分野の専門家で構成されている。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:65",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "46edd59e037f56aff5dcf05a66926506fee6e56692766578ad2cb503cb490495",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "能動の `A, B, and C constitute X` では A・B・C が部分、X が全体である。`X consists of A, B, and C` や `X is composed of A, B, and C` では向きが逆になり、X が全体、A・B・C が部分になる。"
      },
      {
        "id": "usage_note:002",
        "kind": "usage_note",
        "location": "line:67",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "c0a8137c6366b51d588236eb5ef5fdff9518d41077120bf01e2458292461127f",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`be constituted of` は可能だが硬い。通常は `be composed of` または `consist of` が自然である。`consist` は自動詞なので `X is consisted of A` とはしない。"
      },
      {
        "id": "usage_note:003",
        "kind": "usage_note",
        "location": "line:68",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "51585fce8ca9445cd80a5b81113823b40b92982b521adc314c1e355daa9a18d7",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`comprise` は伝統的には `X comprises A, B, and C` のように全体を主語、部分を目的語にするため、能動の constitute とは基本方向が逆である。ただし現代英語では parts comprise a whole や be comprised of も広く使われるので、厳密さが必要な文章では parts/whole の関係が明確な表現を選ぶ。"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:72-77",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "9a96838556b55c9b275bb522558faa6662c2695c23727c2fa525b1736f82c790",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・make up\n定義: 複数の部分・人が集まって全体を構成する。\n頻度: 〈9/10〉\n違い: make up は constitute より口語的で幅広い。`A and B make up X` と同じ parts-to-whole の向きで使える。\n例: Small firms make up most of the local economy.\n訳: 小規模企業が地域経済の大部分を構成している。"
      },
      {
        "id": "synonym:002",
        "kind": "synonym",
        "location": "lines:79-84",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "33b9335507c58feea458c91e07cd19c8ed5af244b621d3ee4557e446a06acba9",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・form\n定義: 部分が集まって全体・形・集団を作る。\n頻度: 〈10/10〉\n違い: form は中立的で、構成関係にも実際に作る過程にも使える。constitute は硬く、部分と全体の関係を分類・統計として述べることが多い。\n例: These streams form the main river.\n訳: これらの小川が本流を形作っている。"
      },
      {
        "id": "synonym:003",
        "kind": "synonym",
        "location": "lines:86-91",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "dbfb54e559c7fef124f1041a312bb45b08ff4f0b9676a9afde6fcb68dfbfa427",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・compose\n定義: 複数の要素が全体を構成する。\n頻度: 〈7/10〉\n違い: compose は構成要素の組み合わせに焦点があり、受動の `be composed of` が特に一般的である。constitute は割合を述べる構文にもよく使う。\n例: Four short sections compose the final movement.\n訳: 4つの短い部分が終楽章を構成している。"
      },
      {
        "id": "synonym:004",
        "kind": "synonym",
        "location": "lines:93-98",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "text_sha256": "c451e4fd6726ff37fce4489a7ae522f686ff7269a70f74ddaf76dd96abc3224c",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・account for\n定義: 数量・割合・原因などのうち、特定の分を占める。\n頻度: 〈8/10〉\n違い: 割合の用法では近いが、account for は「全体のうちどれだけを説明できるか・占めるか」に焦点がある。constitute は割合だけでなく、部分が全体そのものを形作る関係にも使える。\n例: Exports account for nearly half of total sales.\n訳: 輸出が総売上高のほぼ半分を占める。"
      },
      {
        "id": "sense_boundary:002",
        "kind": "sense_boundary",
        "location": "line:100",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "bdcdd41a1e491965484cce5a0c7663b0355e384e9d2f48bf259ba99155bfaa4a",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:102",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "90ff09a525d3bb7f970f89bca60bc77f84fb685dc1083b6ec9e820e24e51a532",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "行為、状況、事実、結果などが、ある分類・評価・状態の定義や成立条件を満たし、そのものと見なせることを表す。目的語には crime、breach、threat、evidence、change、problem などが来る。法律用語だけではなく一般の評価にも使うが、何がその分類に当たるかをやや改まって判断する響きがある。"
      },
      {
        "id": "frequency:002",
        "kind": "frequency",
        "location": "line:104",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "223f0f3bb105d64687ce0ff83ae044846c2f48c7a55d9d015dbc0ce12503d473",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈8/10〉"
      },
      {
        "id": "register:002",
        "kind": "register",
        "location": "line:106",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "bf02cfa7b79b5934844856462817cd390ac58d050e3c517113dfa231185cc516",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "やや硬い標準語。報道、法律、規則、倫理、学術、ビジネス上の評価で頻出する。法律文脈では、実際に犯罪・違反などが成立するかは適用法と事実認定によって決まるため、単語自体が法的結論を保証するわけではない。"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:108",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "e695d32d61cf899e57eac83a80d06850e756939343030aeb864e50deb50aaed6",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈act/fact/situation〉 constitute 〈category/result〉`＝行為・事実・状況が分類・結果に当たる"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:108",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "134594cc901cd060f60790278e4804da2c159382c2ebad08db7c555dec4a26b7",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`constitute a crime/breach/violation`＝犯罪・契約違反・規則違反に当たる"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:108",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "b0351d1111fa27f1a64f9bd3f596de64032be4db4496ef0d467b9f29031d6419",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`constitute a threat/risk/problem`＝脅威・危険・問題となる"
      },
      {
        "id": "grammar_pattern:007",
        "kind": "grammar_pattern",
        "location": "line:108",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "d5bda3458fe2d877c0a329aefcd8302e099754e383190cf90471b72107f13179",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`what constitutes 〈category〉`＝何がその分類を成り立たせるか"
      },
      {
        "id": "collocation:006",
        "kind": "collocation",
        "location": "lines:112-115",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "c99eceb9668aa25d4aa04c9ae6ad9799413377ccbebe9faca889e4567818aa75",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`constitute a crime/offence`\n用途: ある行為が法律上の犯罪・違反に当たり得ることを述べる。\n例: Deliberately altering the records may constitute a criminal offence.\n訳: 記録を故意に改ざんすることは、刑事犯罪に当たる可能性がある。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:117-120",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "4f9ab1a96b944d7454b22d4bc2f70cec33a95b08d0e7c36b95c65f1825cea773",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`constitute a breach/violation of 〈rule/duty〉`\n用途: 行為・不作為が契約、規則、義務などへの違反に当たると判断する。\n例: Sharing the data without permission would constitute a breach of the agreement.\n訳: 許可なくデータを共有すれば、その契約への違反に当たる。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:122-125",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "e71db533516711e7f06621bfae4429f4b67875707808aede5e114ff40f2e8d63",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`constitute a threat/risk to 〈person/system〉`\n用途: 状況・存在が人や制度への脅威・危険となることを示す。\n例: The damaged bridge constitutes a serious risk to public safety.\n訳: その損傷した橋は公共の安全に対する重大な危険となっている。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:127-130",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "15d5693b4bddff4903f101e70498bb987d838bce0893925196b9c73b0c3ca565",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`constitute evidence/proof of 〈事実〉`\n用途: ある資料・行為が、事実を裏づける証拠に当たるかを論じる。\n例: A single anonymous message does not constitute proof of fraud.\n訳: 匿名のメッセージ一通だけでは、詐欺の証明にはならない。"
      },
      {
        "id": "collocation:010",
        "kind": "collocation",
        "location": "lines:132-135",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "77eb2fdfb1b94df6890472c5fa73537ee998c620017d51efde8e9d21d446991d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`constitute a significant change/improvement`\n用途: 出来事や措置が、単なる小差ではなく、意味のある変化・改善に当たると評価する。\n例: The revised policy constitutes a significant change in the company's approach.\n訳: 改訂された方針は、その会社の取り組み方の大きな変化に当たる。"
      },
      {
        "id": "collocation:011",
        "kind": "collocation",
        "location": "lines:137-140",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "20e0d8f0596b7253f05147c0186001949ded71cadbc2fafabed773e4a0b8b55c",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`what constitutes 〈category/standard〉`\n用途: 何がある概念・分類・基準に該当するのかを問う・定義する。\n例: The guidelines explain what constitutes acceptable use of the system.\n訳: その指針は、どのようなシステム利用が許容されるかを説明している。"
      },
      {
        "id": "usage_note:004",
        "kind": "usage_note",
        "location": "line:142",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "27b20aae0090db44dfdd0bef4440f607b2f26c84872473e842e658410616bc20",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "この語義の constitute は、主語と目的語を同一の分類関係で結ぶが、文法上は目的語を取る動詞であり、通常 `constitute as a threat` のように as を挟まない。`The delay constitutes a problem.` のように直接目的語を置く。"
      },
      {
        "id": "usage_note:005",
        "kind": "usage_note",
        "location": "line:144",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "8be22c4a9a811e1327ee16d1f40552bad30b4c80ac343c5da26133d09777d18d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "語義1との区別は、目的語が「主語を部分として含む全体」か、「主語が該当すると判断される分類・評価」かで行う。`Ten members constitute the committee.` は構成、`Their absence constitutes a problem.` は評価・該当である。"
      },
      {
        "id": "usage_note:006",
        "kind": "usage_note",
        "location": "line:145",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "e64d46574c2bdcbb10ce30758f65a69f6ff45858f3e7d5fdb85ded3705799088",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "否定文の `does not constitute proof/consent/approval` は、「証拠・同意・承認として十分ではない」という境界を明示する定型的な用法である。constitute 自体は、事態を引き起こす cause や、証拠によって証明する prove を意味しない。"
      },
      {
        "id": "synonym:005",
        "kind": "synonym",
        "location": "lines:149-154",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "8bbb4bdc8c4b27d26b5ab3cc982551f0723ea2f6ce46604a8b64edee7d996e2a",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・amount to\n定義: 行為・状況が、実質的にある結果・評価と同じである。\n頻度: 〈8/10〉\n違い: amount to は「結局は～に等しい」という実質的帰結を強調する。constitute は定義・基準への該当を、より公式・分析的に述べやすい。\n例: Ignoring repeated warnings amounts to negligence.\n訳: 度重なる警告を無視することは、怠慢に等しい。"
      },
      {
        "id": "synonym:006",
        "kind": "synonym",
        "location": "lines:156-161",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "2485e3589d9240541d95609e14d25ce2415335141615fb071c41f4a7ca0ffd12",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・qualify as\n定義: 必要な条件を満たして、ある分類・資格に該当する。\n頻度: 〈7/10〉\n違い: qualify as は明示的な条件を満たす点を強調する。constitute は条件が厳密に列挙されていない一般評価にも使える。\n例: The structure qualifies as a protected historic building.\n訳: その構造物は、保護対象の歴史的建造物に該当する。"
      },
      {
        "id": "synonym:007",
        "kind": "synonym",
        "location": "lines:163-168",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "7906e37632db793752c619d8a1f2c55d889a215d4f529c46b06dd036f523ce37",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・count as\n定義: 規則・判断・一般的理解の上で、あるものとして数えられる。\n頻度: 〈8/10〉\n違い: count as は口語的で、日常的な分類にも使いやすい。constitute はより硬く、公式の基準や重大な評価に合う。\n例: Does volunteer work count as relevant experience?\n訳: ボランティア活動は関連経験として認められますか。"
      },
      {
        "id": "synonym:008",
        "kind": "synonym",
        "location": "lines:170-175",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "text_sha256": "32a5424c7d5875bff70aa756cc65a79a887589e1eaee72baf47d036a371e3361",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・represent\n定義: 状況・出来事が、ある意味・変化・危険などを体現する。\n頻度: 〈9/10〉\n違い: represent は象徴・典型・意味づけまで広く表す。constitute は主語が実際にその分類・状態に当たるという同一視がより強い。\n例: The agreement represents an important step toward peace.\n訳: その合意は、平和に向けた重要な一歩を意味する。"
      },
      {
        "id": "sense_boundary:003",
        "kind": "sense_boundary",
        "location": "line:177",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "7297e0b98a843da5422fd665f92d30ef30f5e660982e014c0422e245242f48b2",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える"
      },
      {
        "id": "definition:003",
        "kind": "definition",
        "location": "line:179",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "b52e0235a19f365374421cfbe54a9603e75b535d05ac2d5bfde907cb833323fa",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "組織、委員会、裁判所、政府などを正式に形成・設置し、公式の組織体として成立させることを表す。法律用法では、契約や組織体に所定の法的形式を与えることも表す。制度や文脈によって所定の手続きや権限付与を伴うことはあるが、constitute という語だけで法的有効性や実際の活動可能性まで一律に保証するわけではない。"
      },
      {
        "id": "frequency:003",
        "kind": "frequency",
        "location": "line:181",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "f75683d2ec70c01e8ef877fe56064d1d46ce1e20d9e5a13b41fe1f03202dbee8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈5/10〉"
      },
      {
        "id": "register:003",
        "kind": "register",
        "location": "line:183",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "ca81eb62556adb7eab69db531d29d278ab1cec52100f58b9a8df392a719e2d3d",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "非常に硬い公式・行政・法律・組織運営の用法。契約などを所定の法的形式に整える意味も法律文脈に限られる。一般的な会社・団体の設立では establish、form、set up がより広く使われる。"
      },
      {
        "id": "grammar_pattern:008",
        "kind": "grammar_pattern",
        "location": "line:185",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "ec678db2add1bcae792e7f075e812a35835846c964c0081e174ac7435ec79f61",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈authority/institution/parties〉 constitute 〈committee/body/court/government〉`＝権限主体・機関・当事者が委員会・機関・裁判所・政府を正式に設ける"
      },
      {
        "id": "grammar_pattern:009",
        "kind": "grammar_pattern",
        "location": "line:185",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "a09e3db0f0d5bbca4124730e57d2b1a22a03bb207040865c1b87ca08491b0f08",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`constitute 〈agreement/body〉`＝契約・組織体に所定の法的形式を与える"
      },
      {
        "id": "grammar_pattern:010",
        "kind": "grammar_pattern",
        "location": "line:185",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "599d32391185af0cc8e11fef7706fa10056c6df96c2daf10c45a037176544f8c",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`〈body〉 be constituted under/by 〈law/authority〉`＝機関が法律・権限に基づいて設立される"
      },
      {
        "id": "grammar_pattern:011",
        "kind": "grammar_pattern",
        "location": "line:185",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "eadb4b9770f8f46894bf15bc62d060629f3e8dd9015597f85f8c5a2d7cbb3662",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`a properly/legally/duly constituted 〈body/authority〉`＝適切・合法・正式に成立した機関・権限主体"
      },
      {
        "id": "collocation:012",
        "kind": "collocation",
        "location": "lines:189-192",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "2dcd9d722cf6ab214a4eee7a6b7a0498ede735ab5a94773ff53ac83b5c86f59d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`constitute a committee/panel`\n用途: 特定の目的をもつ委員会や審査団を正式に設ける。\n例: The ministry constituted an independent panel to investigate the accident.\n訳: 同省は、その事故を調査する独立委員会を正式に設置した。"
      },
      {
        "id": "collocation:013",
        "kind": "collocation",
        "location": "lines:194-197",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "5867ad4d80d9a0fef5bcf05eed66e2ea6ecc50530ef79f3a006fc92886b72f1e",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`constitute a court/tribunal`\n用途: 裁判所・審判機関を正式に設ける。\n例: The treaty provides for a tribunal to be constituted when a dispute arises.\n訳: その条約は、紛争が生じた際に審判機関を設置することを定めている。"
      },
      {
        "id": "collocation:014",
        "kind": "collocation",
        "location": "lines:199-202",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "df7af655efcf60a6b7d0c66638a8d32791dd793374f604b419f97a9d82a79aba",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`constitute a government/authority`\n用途: 政府・公的機関を正式な組織体として成立させる。\n例: The parties agreed to constitute a transitional government.\n訳: 当事者らは暫定政府を発足させることで合意した。"
      },
      {
        "id": "collocation:015",
        "kind": "collocation",
        "location": "lines:204-207",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "29146738f8c2c02a7d63ff47bf3a422635c6d996ab74b4510bd1b04c1f071530",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`be constituted under 〈law/charter〉`\n用途: 組織が法律・憲章などを根拠として設立されていることを示す。\n例: The commission was constituted under the new environmental law.\n訳: その委員会は新しい環境法に基づいて設置された。"
      },
      {
        "id": "collocation:016",
        "kind": "collocation",
        "location": "lines:209-212",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "0e373cbaae25441a7bb52826e206ab115af70638c41185cb18bae05d88f2c730",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`a duly/properly constituted 〈body/meeting〉`\n用途: 機関・会議が必要な手続きや構成要件を満たして正式に成立していることを示す。\n例: Only a duly constituted board may approve the transaction.\n訳: 正式に構成された取締役会だけが、その取引を承認できる。"
      },
      {
        "id": "usage_note:007",
        "kind": "usage_note",
        "location": "line:214",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "f57d8edf1a444d0bb1e526b3c83b1dc648f17138ede9e9aee62a9e7ef6957594",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "語義1の「部分が全体を構成している」は状態的な関係、語義3の「組織を正式に設立する」は意図的・制度的な行為である。`The members constitute the board.` は「構成員が取締役会を構成する」、`The agency constituted a board.` は「機関が取締役会を正式に設置した」となる。"
      },
      {
        "id": "usage_note:008",
        "kind": "usage_note",
        "location": "line:216",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "0dde7f625f95458cc25a422e274fc43c1582b76c1f8bdd2b5a3642e63ae46fc8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "法律文脈の `constitute an agreement/body` は、契約や組織体に必要な法的形式を与える意味になり得る。組織を新設する意味と、既存の契約・組織体を所定の形式に整える意味は文脈で区別する。"
      },
      {
        "id": "usage_note:009",
        "kind": "usage_note",
        "location": "line:218",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "516b6e86408c38c79fe7cff7c70bab52f24d8adc4214a83ae2c4bc90a7b1b759",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`be constituted under ...` は通常、設立根拠を示す。`be constituted by ...` の by 句は文脈により、設立主体を示す場合と、語義1で全体を形作る構成要素を示す場合がある。`be constituted of ...` は構成要素を示すため、前置詞だけで語義を機械的に判断しない。"
      },
      {
        "id": "usage_note:010",
        "kind": "usage_note",
        "location": "line:219",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "b661df35c35d38314e3d7fbcf004094c1f7648bac07458795e9589170957633f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`duly/properly/legally constituted` は constituted が過去分詞として名詞を修飾する定着表現で、「正当に権限をもつ・手続き上有効に成立した」という含みを持つ。ただし、その組織の個々の決定まで自動的に適法だと保証する表現ではない。"
      },
      {
        "id": "synonym:009",
        "kind": "synonym",
        "location": "lines:223-228",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "71bdf5ff1c06df9f16c2d7479ed773a7e840ec9b0298c7598511b59074b2af5b",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・establish\n定義: 組織・制度・関係などを作り、安定して存在するようにする。\n頻度: 〈9/10〉\n違い: establish は設立全般に使える標準的な語である。constitute は、組織体を公式な形で成立させる硬い表現である。\n例: The university established a new research center.\n訳: その大学は新しい研究センターを設立した。"
      },
      {
        "id": "synonym:010",
        "kind": "synonym",
        "location": "lines:230-235",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "7a980c97ee67eded8e338a391d6cc4fcba4d6d3de91d5b5954273bd278075ec9",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・form\n定義: 人・組織・要素を集めて、新しい集団・組織を作る。\n頻度: 〈10/10〉\n違い: form は日常的で、正式な法的手続きを必ずしも含まない。constitute は公式・制度的な文脈で使われやすい。\n例: Residents formed a committee to protect the park.\n訳: 住民たちは公園を守るために委員会を結成した。"
      },
      {
        "id": "synonym:011",
        "kind": "synonym",
        "location": "lines:237-242",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【他動詞】（組織などを）正式に設立する；（契約などを）所定の法的形式に整える",
        "text_sha256": "69d020a5274f824903e32d90cc5faae6f3821a7a34bce8a10b2daaf6ade5c01b",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・set up\n定義: 組織・制度・仕組みなどを作って動かし始める。\n頻度: 〈9/10〉\n違い: set up は口語的で、準備・運用開始まで幅広く表す。constitute は設立の公式性・制度性に焦点がある。\n例: The city set up a task force to address housing shortages.\n訳: 市は住宅不足に対処する特別チームを立ち上げた。"
      },
      {
        "id": "sense_boundary:004",
        "kind": "sense_boundary",
        "location": "line:244",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "c65dd9fabe3a40b9c487c6c9825bbc85bcdad5c1f95e283f9c1945906529a48d",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する"
      },
      {
        "id": "definition:004",
        "kind": "definition",
        "location": "line:246",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "16d9095b0f376b66e064a6263c8925a22f89bcef9541571a06cba374192da498",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "権限をもつ者・法律・公式文書などが、人を特定の役職・地位・役割に正式に任命・指定することを表す。任命の法的有効性、付与される権限、その立場で行動できる範囲は、該当する文書・制度・法域によって決まる。"
      },
      {
        "id": "frequency:004",
        "kind": "frequency",
        "location": "line:248",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "c9f89b3d40a42341908558a5512ad7d34bbc108cc33b512e22b76f6557469962",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈2/10〉"
      },
      {
        "id": "register:004",
        "kind": "register",
        "location": "line:250",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "27165159fdc61b9fc0d69a5109a0aaf24c1d3bb18218a82a79ddc06b1cbceabd",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "法律・公文書などの公式文体。`a legally constituted officer` のような表現では、法や制度に基づいて正式に任命された役職者を指す。"
      },
      {
        "id": "grammar_pattern:012",
        "kind": "grammar_pattern",
        "location": "line:252",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "f559e4b22c357a16123d859b2eb6d271e7ca102196e5eaf84d31c3a6384f5b0d",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`〈authority/law/document〉 constitute someone 〈office/role〉`＝権限者・法律・公式文書が人を役職・役割に任命する"
      },
      {
        "id": "grammar_pattern:013",
        "kind": "grammar_pattern",
        "location": "line:252",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "f3b2fdf8fd47135388343b701d273d73e8962f5f0c0dba89b8757988d498b43b",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`someone be constituted 〈office/role〉`＝人が役職に任命される"
      },
      {
        "id": "grammar_pattern:014",
        "kind": "grammar_pattern",
        "location": "line:252",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "b2710aeef2e7ae85e2e130efb4d785e351f2405406d213b0b6c7e05dabfa332b",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`a legally constituted 〈officer/official〉`＝法に基づいて正式に任命された役職者"
      },
      {
        "id": "collocation:017",
        "kind": "collocation",
        "location": "lines:256-259",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "74320573a7f97a18085969c1e64a7efa7a196aa02177a6e95ef6beee9cb9ae09",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`constitute someone 〈office/role〉`\n用途: 人を特定の役職・職務に就けることを、古風または法律的に述べる。\n例: The charter constituted him treasurer of the association.\n訳: その憲章によって、彼は協会の会計役に任命された。"
      },
      {
        "id": "collocation:018",
        "kind": "collocation",
        "location": "lines:261-264",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "021871f43b94730b22158fae4c37b6dc3958eede635c702a1515d9b4264f81d9",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`be constituted 〈office/role〉`\n用途: 人が役職・地位に正式に任命されたことを受動態で示す。\n例: She was constituted guardian for the limited purpose stated in the order.\n訳: 彼女は、その命令に記された限定的な目的のための後見人に任命された。"
      },
      {
        "id": "collocation:019",
        "kind": "collocation",
        "location": "lines:266-269",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "1c7dfd53259260da766db5fa90310bd7e978831ab3b2fe390b9035f41ccb0dda",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`a legally constituted 〈officer/official〉`\n用途: 法や制度に基づいて正式に任命された役職者を指す。\n例: The charter identifies the treasurer as a legally constituted officer of the association.\n訳: その憲章は、会計役を協会において法に基づき正式に任命された役職者として明記している。"
      },
      {
        "id": "usage_note:011",
        "kind": "usage_note",
        "location": "line:271",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "568cbca9f95b3980e68397c56c1c3b6f0d8964e74c2d1175db28666e77201e61",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "人を直接目的語にし、役職を目的格補語として置く `constitute someone treasurer` のような形で使う。現代の一般文では非常に硬いため、通常は `appoint someone treasurer` などとする。"
      },
      {
        "id": "usage_note:012",
        "kind": "usage_note",
        "location": "line:273",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "9b101aedafd5919ab54c490983de9db1f426bf2168bc19f9568297a4bef93b90",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "語義3は committee や court などの組織そのものを成立させ、語義4は person を役職・地位に就ける。`constitute a committee` と `constitute someone treasurer` を同じ目的語構造として扱わない。"
      },
      {
        "id": "usage_note:013",
        "kind": "usage_note",
        "location": "line:274",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "7bcb808772168a08b4310883659db7222ebbb3c1da01235ad451b291344bc146",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`a legally constituted officer` は「構成された役職者」という逐語訳ではなく、「法に基づいて正式に任命された役職者」を意味する。"
      },
      {
        "id": "synonym:012",
        "kind": "synonym",
        "location": "lines:278-283",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "b23a7bc00488ab7312ebbc11e22abb31463c157f3b7d81cf302613e7e949a85a",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・appoint\n定義: 人を役職・職務に正式に就ける。\n頻度: 〈9/10〉\n違い: appoint は現代英語の標準表現で、constitute より広く自然に使う。constitute は法律・公文書などの硬い公式文体に現れる。\n例: The board appointed Maya treasurer.\n訳: 取締役会はマヤを会計責任者に任命した。"
      },
      {
        "id": "synonym:013",
        "kind": "synonym",
        "location": "lines:285-290",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "ae84777292d427b7a450413de761ac6f119c9e530a94b4b42c3ece5ae1a29dd9",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・designate\n定義: 人を特定の役割・地位の担当者として公式に指定する。\n頻度: 〈7/10〉\n違い: designate は役割を割り当て、明示することに焦点がある。constitute は法律・公式文体で、人をその役職・地位に正式に就けることを表す。\n例: The minister designated Lee as the official spokesperson.\n訳: 大臣はリーを公式報道官に指定した。"
      },
      {
        "id": "synonym:014",
        "kind": "synonym",
        "location": "lines:292-297",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "text_sha256": "ba52893a046190fe586521acc8b49e0b173e601d94be3c472d3cdf410c3c9d54",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・name\n定義: 人を役職・候補・受賞者などとして発表・指定する。\n頻度: 〈9/10〉\n違い: name は簡潔で一般的であり、発表・選定に焦点がある。constitute は法律・制度上の役職へ正式に任命する文脈で使われる。\n例: The council named Rivera chair of the committee.\n訳: 評議会はリベラを委員会の議長に指名した。"
      }
    ],
    "relation_results": [
      {
        "id": "risk_sense_pair:001",
        "kind": "risk_sense_pair",
        "target_ids": [
          "sense_boundary:001",
          "sense_boundary:002"
        ],
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: usage_note:005 explicitly contrasts sense 2 with sense 1",
        "text_sha256": "b43c28f06b1a24503d06012831b7b7ebf595253dcd9c04b218e1ef9c907fc8ee",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "risk_sense_pair:002",
        "kind": "risk_sense_pair",
        "target_ids": [
          "sense_boundary:001",
          "sense_boundary:003"
        ],
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: usage_note:007 explicitly contrasts sense 3 with sense 1; usage_note:009 explicitly contrasts sense 3 with sense 1",
        "text_sha256": "23e3665c06975d19002487213203b866bbf32792293c40275d310ddeeb9ce5e4",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "risk_sense_pair:003",
        "kind": "risk_sense_pair",
        "target_ids": [
          "sense_boundary:003",
          "sense_boundary:004"
        ],
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: usage_note:012 explicitly contrasts sense 4 with sense 3",
        "text_sha256": "0548a58c946b63ac1a439cd4d3933331c8e3c1a4471dd460f51ad8789b54e2bd",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "example_translation:001",
        "kind": "example_translation",
        "target_ids": [
          "collocation:001"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "26750269ee9dd5b51b69765498e65b4a87effedbbc0238eb29e302fcc51b1271",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:002",
        "kind": "example_translation",
        "target_ids": [
          "collocation:002"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "0fddd7231b615b1468c1bb23515fe6ee82ffdf770efff68aeac4dbb2df355152",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:003",
        "kind": "example_translation",
        "target_ids": [
          "collocation:003"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "ae6f03bfc90aa62807a5306af7169ced4893be7f3fe0c7eef691a27f2c6671be",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:004",
        "kind": "example_translation",
        "target_ids": [
          "collocation:004"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "b7bd8e4f64f2b5b4416c868f399db21d336bb2525a56cb9582dc575f8de0f7d3",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:005",
        "kind": "example_translation",
        "target_ids": [
          "collocation:005"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "2c3d879214f4eaf61bfe50841656663a25b4c418dce8fa21d84fb2637c575cf5",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:006",
        "kind": "example_translation",
        "target_ids": [
          "collocation:006"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "e6b70b6f529d0afd20caa1af0a66c20b2b508c59841b4f32f3ef20f4e775bf02",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:007",
        "kind": "example_translation",
        "target_ids": [
          "collocation:007"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "70ef911dd4616153972b44f7c6764b22f0d4c69c0f3128250f4e79719f5c37d9",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:008",
        "kind": "example_translation",
        "target_ids": [
          "collocation:008"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "5f2bc65b94c6a305d15a4a7799b1b5f405b78d66c43ed082ddae23034fa9d638",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:009",
        "kind": "example_translation",
        "target_ids": [
          "collocation:009"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "0b4b10a1fbf88bacd5150465ea4b231fc56e5e27736eef3449c9f50b98a6fe2e",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:010",
        "kind": "example_translation",
        "target_ids": [
          "collocation:010"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "58d14b97f4826f5fe10d2313973b4228da01f3317e3edc280fd457b43980af45",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:011",
        "kind": "example_translation",
        "target_ids": [
          "collocation:011"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "43b8fe04035e437529cb24a74677df60f7d66c4b2f25c8fee27238aa8f1a3675",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:012",
        "kind": "example_translation",
        "target_ids": [
          "collocation:012"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "509ba966ede82e1b103e8461e7092b2e5bcccba6e77731ba860850397c816a49",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:013",
        "kind": "example_translation",
        "target_ids": [
          "collocation:013"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "fff01262eb1dccb4fd32f0e2eb32aeb8abdc2ff0ef1c5bdcca2d9ce346ebd89d",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:014",
        "kind": "example_translation",
        "target_ids": [
          "collocation:014"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "ed18c55011dc1dbb438a4c8003942bc2099c39c6d943b0d0d880b51e34cc60a8",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:015",
        "kind": "example_translation",
        "target_ids": [
          "collocation:015"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "f1f4d154221226e8731d52c15bca47cfcfc59bc3d3c11f1677dc93c077deea0c",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:016",
        "kind": "example_translation",
        "target_ids": [
          "collocation:016"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "9a5ba5f4b940826c43edfca9d891090221732523a58bf3f7e7aaa360336e79ec",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:017",
        "kind": "example_translation",
        "target_ids": [
          "collocation:017"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "b5ddc1ed1f0045303a9d382f34db7085e0dcade2526d929c2545f84c149949b8",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:018",
        "kind": "example_translation",
        "target_ids": [
          "collocation:018"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "aa3b76fa802a9dbaa226d786ff181ff927a73b3cdf429fb5b8f8312975477d7b",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:019",
        "kind": "example_translation",
        "target_ids": [
          "collocation:019"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "13054c78bdd6107f9bdbb5a51d181d661263fee2c8d251d8bf6aeb263ebffe6b",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:001",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "a610295e5ff2f26df8c51c3804bd7d2fb7fd9bef0c6ea2226069e2ad051c2267",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:001",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "usage_note:001"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "fce9e9eb0b0e86ca9ca46179914e226d1702b8d93d1ac7cbe7296a1d33593011",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:002",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "usage_note:002"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "643dbf15b2eb98a464600df9ff5cc7b8d233bdb7073c825c5f39381a28747679",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:003",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "usage_note:003"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "248a98e6c0b01dc71f2605b73299c4c3e9c6f079fab5529bfdc76486cc370bac",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:001",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "synonym:001",
          "synonym:002",
          "synonym:003",
          "synonym:004"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "af907e45ebd1bbe5583e824ad2363497306fb4e6a3b8c482ccda4d70d4fe8a2e",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:001",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:001",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "64266f8218e05b59fa5b328e57c30ff8773bcf7a71d4f83ce958af62d763bcd1",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:002",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:002",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "33e3dd99672a0cbf8186f4543cfaf38387d49b4c3e6f9fa3bc5989274908219d",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:003",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:003",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "ca4b8c251b857a52dc628a70fd4679f3bb7bcb9d3bc05c2f7cdbb60f1fc93be6",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:002",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "e254f29d0b4af1400fd7482afff3595556e4dd05869cb4266669e3b16e6c794a",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:004",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "usage_note:004"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "0b8226893f09be5051fd537239ca59e347f3789fc427595143dd3d9d614e1587",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:005",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "usage_note:005"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "967ce80fd4df1b96246a6ece81c733fd61384b52767f75577bd1dc0d7b113289",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:006",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "usage_note:006"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "282755a46f60f6a3e80b7eaa7b91edb1ed13bd3ebec40546f30a29c7734d8c13",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:002",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "synonym:005",
          "synonym:006",
          "synonym:007",
          "synonym:008"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "9ef5ef684d84e512c06d9021d7ac991f269ea843c00a3e2df5d03e85ac747cc8",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:004",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:004",
          "collocation:006",
          "collocation:007",
          "collocation:008",
          "collocation:009",
          "collocation:010",
          "collocation:011"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "5258999ddac733a6ffa75e97d26a40f8f52a7b141205d7aa8946b3ac33c91cca",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:005",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:005",
          "collocation:006",
          "collocation:007",
          "collocation:008",
          "collocation:009",
          "collocation:010",
          "collocation:011"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "8a6970f6373fa575092783d2caf718d722955bd13a22dc29db5dbd19fd19e83f",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:006",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:006",
          "collocation:006",
          "collocation:007",
          "collocation:008",
          "collocation:009",
          "collocation:010",
          "collocation:011"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "21ba1265c6c0c0cba51a654f241984a30004ab64c6af2de9e17c72c062d340c4",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:007",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:007",
          "collocation:006",
          "collocation:007",
          "collocation:008",
          "collocation:009",
          "collocation:010",
          "collocation:011"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "57c91414cbb36f3aab91a12e38b945415b167ac65dc952766cc522e7e2352c6f",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:003",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "7b33dfa1288ca4b8970a9d2adbdb7a6e92deaecbc7bcb6e5a9cc151753fe01e5",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:007",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003",
          "usage_note:007"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "db1ff24f6234e8ca249c1e0ac3e45ffd20a8e7405f3b8d070d84f2250eabe015",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:008",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003",
          "usage_note:008"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "10ce9405b2439fc0bfa2de243bae40c7647e1ce4c53841bbbe0d0e525c1c5241",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:009",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003",
          "usage_note:009"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "35287e496488e778999b79e70d3b317e195145fb6f6a068edd5dc43ce1e3235f",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:010",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003",
          "usage_note:010"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "2e04a1f5b03c42ea09ba37560e0a18ef386ba8e3752bbf4173c4be913e5d4db0",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:003",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003",
          "synonym:009",
          "synonym:010",
          "synonym:011"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "2474a084a3348507c93ffffc154613e9dbe43459f40cb88e0940702e3ff3720e",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:008",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:008",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "d2cd38b1cf5966bdaf4db8f704b5a9def41efe225e10bf9524a5d908a7b5cc46",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:009",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:009",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "ff665a72cb84b47060f3ed17671d997e0b9ffac453c666d72cfa9e32735450dd",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:010",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:010",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "f801b07b01e92bb392daa53e4ab09d981de9441279cdcd257155e134925ac95b",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:011",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:011",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "202f4344e72bb58dbeee925d543c950cae8e19e501ef23c1b8b8cb21538d8853",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:004",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "e7e9946cca35310439b0a30a66b684d37cd144eca7e8b4ee7e360722b5461a29",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:011",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004",
          "usage_note:011"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "b57256e74a311d5eada3abc0ade2545f45f1bab777eb2aa875edc46ce23d588b",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:012",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004",
          "usage_note:012"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "8517f5ac5ce7e17d4401bbc0184fec54a49c3da5de2f13df6e54e6203bba625c",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:013",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004",
          "usage_note:013"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "461fde3293658bd9384c4fbe81dc35d7c163f44f41cd3c7deabc30966335516e",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:004",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004",
          "synonym:012",
          "synonym:013",
          "synonym:014"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "1c30d3d65dcab4fdee0fe43a53c1ccce5546a8d1eb70cb10f17751691e2ec913",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:012",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:012",
          "collocation:017",
          "collocation:018",
          "collocation:019"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "2426e3078acc46a87dbb4c11e4c48816a735099ccb37a52ea39b00edc953b4d0",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:013",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:013",
          "collocation:017",
          "collocation:018",
          "collocation:019"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "a7fb17d0f41520aa349f741d44eaadec602de063c084cde1805d7822957e55bf",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:014",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:014",
          "collocation:017",
          "collocation:018",
          "collocation:019"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "4cade6acf7b9c7ad7bd0dff8ebc680ec1c191c08226ce16f14debbe90da07215",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "core_inventory_consistency:001",
        "kind": "core_inventory_consistency",
        "target_ids": [
          "core_image:001",
          "sense_boundary:001",
          "sense_boundary:002",
          "sense_boundary:003",
          "sense_boundary:004"
        ],
        "description": "語義番号を限定しない総括的なコアイメージが、記事の語義目録全体を不当に一般化していないことを確認する。",
        "text_sha256": "f36ce09ba6c335a837e46ef0d2fdc56e0179ca07495511e4b520e285a4835a65",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "core_sense_mapping:001",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:002",
          "sense_boundary:001",
          "definition:001",
          "usage_note:001",
          "usage_note:002",
          "usage_note:003"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "97fcd0f0056a63c2dd8e06b691c4540d3d0beeade6d1d85fb7bb2a4717a542d3",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "core_sense_mapping:002",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:003",
          "sense_boundary:002",
          "definition:002",
          "usage_note:004",
          "usage_note:005",
          "usage_note:006"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "5029ab29ed6ae53cbed590effd3eb469fe45031a52f5b75f7b57f86dd4e57f44",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "core_sense_mapping:003",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:004",
          "sense_boundary:003",
          "definition:003",
          "usage_note:007",
          "usage_note:008",
          "usage_note:009",
          "usage_note:010"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "642790d58972048ba6f1ca09d3f745fedf5b82e6c612b7f3f096ad9a14d55d44",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "core_sense_mapping:004",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:005",
          "sense_boundary:004",
          "definition:004",
          "usage_note:011",
          "usage_note:012",
          "usage_note:013"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "498ebfd700e109d467285b1a9f1e927ced7b1e8653091df098a217be9c9580a0",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "article_learning_risk:001",
        "kind": "article_learning_risk",
        "target_ids": [
          "core_image:001",
          "core_image:002",
          "core_image:003",
          "core_image:004",
          "core_image:005",
          "sense_boundary:001",
          "definition:001",
          "usage_note:001",
          "usage_note:002",
          "usage_note:003",
          "sense_boundary:002",
          "definition:002",
          "usage_note:004",
          "usage_note:005",
          "usage_note:006",
          "sense_boundary:003",
          "definition:003",
          "usage_note:007",
          "usage_note:008",
          "usage_note:009",
          "usage_note:010",
          "sense_boundary:004",
          "definition:004",
          "usage_note:011",
          "usage_note:012",
          "usage_note:013"
        ],
        "description": "記事全体の語義構成、対比、訳語、限定表現から学習者が誤った一般化をしないことを横断確認する。",
        "text_sha256": "30936daedfdb34d579a19afbc4555183e51e1b305202d65d0b08674667abef80",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "IC-01",
        "surface_form": "constitute",
        "frame": "〈parts/members〉 constitute 〈whole/group〉",
        "meaning": "複数の部分・構成員が全体を構成する",
        "disposition": "included",
        "rationale": "〈parts/members〉 constitute 〈whole/group〉 は、主語側の要素から目的語側の全体へ向かう基本的な部分―全体関係を表し、記事はその方向を正しく区別している。",
        "semantic_assertions": [
          {
            "id": "IC-01-A1",
            "statement": "主語は目的語で表される全体の構成要素または構成員でなければならない。",
            "polarity": "must_hold",
            "scope": "能動態の parts-to-whole 構文"
          },
          {
            "id": "IC-01-A2",
            "statement": "このフレームを、全体を主語にして部分を目的語に取る方向として説明してはならない。",
            "polarity": "must_not_hold",
            "scope": "能動態の意味役割"
          }
        ]
      },
      {
        "id": "IC-02",
        "surface_form": "constitute",
        "frame": "〈group/category/item〉 constitute 〈percentage/majority/minority/part〉 (of 〈whole〉)",
        "meaning": "ある集団・項目が全体に占める割合または部分量を表す",
        "disposition": "included",
        "rationale": "〈group/category/item〉 constitute 〈percentage/majority/minority/part〉 (of 〈whole〉) は、完全な全体形成ではなく量的な占有関係を表す独立フレームであり、記事の用例と説明はこの境界を満たす。",
        "semantic_assertions": [
          {
            "id": "IC-02-A1",
            "statement": "目的語は主語が占める割合・多数／少数区分・部分量を表さなければならない。",
            "polarity": "must_hold",
            "scope": "割合・部分量フレーム"
          },
          {
            "id": "IC-02-A2",
            "statement": "of 句の全体は、文脈から回復できる場合に限って省略可能である。",
            "polarity": "must_hold",
            "scope": "割合・部分量フレームの省略"
          }
        ]
      },
      {
        "id": "IC-03",
        "surface_form": "be constituted of",
        "frame": "〈whole〉 be constituted of 〈parts/materials〉",
        "meaning": "全体が複数の部分・材料から構成されている",
        "disposition": "included",
        "rationale": "〈whole〉 be constituted of 〈parts/materials〉 は硬いが成立する受動的な構成表現であり、記事はより普通の be composed of / consist of とのレジスター差も示している。",
        "semantic_assertions": [
          {
            "id": "IC-03-A1",
            "statement": "主語は全体で、of 句はその構成要素または材料でなければならない。",
            "polarity": "must_hold",
            "scope": "be constituted of 構文"
          }
        ]
      },
      {
        "id": "IC-04",
        "surface_form": "constitute",
        "frame": "〈act/fact/situation/result〉 constitute 〈category/evaluation/state〉",
        "meaning": "行為・事実・状況などが分類・評価・状態に該当する",
        "disposition": "included",
        "rationale": "〈act/fact/situation/result〉 constitute 〈category/evaluation/state〉 は、部分―全体関係ではなく、主語が目的語の定義・評価に当たるという同定関係であり、記事は crime、breach、risk、change などを適切に扱う。",
        "semantic_assertions": [
          {
            "id": "IC-04-A1",
            "statement": "主語は目的語が表す分類・評価・状態の成立条件に該当すると判断されなければならない。",
            "polarity": "must_hold",
            "scope": "分類・評価用法"
          },
          {
            "id": "IC-04-A2",
            "statement": "constitute 自体を、その分類対象を引き起こす cause の意味として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "分類・評価用法"
          }
        ]
      },
      {
        "id": "IC-05",
        "surface_form": "does not constitute",
        "frame": "〈evidence/act/silence/etc.〉 does not constitute 〈proof/consent/approval/etc.〉",
        "meaning": "ある材料や行為だけでは所定の証明・同意・承認に該当するほど十分ではない",
        "disposition": "included",
        "rationale": "〈evidence/act/silence/etc.〉 does not constitute 〈proof/consent/approval/etc.〉 は分類境界の不充足を明示する定着した否定フレームであり、記事は prove という行為との混同も避けている。",
        "semantic_assertions": [
          {
            "id": "IC-05-A1",
            "statement": "否定は、主語が目的語の分類に達するための十分条件を満たさないことに作用しなければならない。",
            "polarity": "must_hold",
            "scope": "否定された分類フレーム"
          },
          {
            "id": "IC-05-A2",
            "statement": "このフレームを、主語が証拠によって何かを証明するという他動的な prove の意味にしてはならない。",
            "polarity": "must_not_hold",
            "scope": "proof/evidence を伴う否定フレーム"
          }
        ]
      },
      {
        "id": "IC-06",
        "surface_form": "what constitutes",
        "frame": "what constitutes 〈category/standard〉",
        "meaning": "何が特定の分類・基準を成立させるかを問う・定義する",
        "disposition": "included",
        "rationale": "what constitutes 〈category/standard〉 は、分類の境界や要件を問う埋込み疑問・自由関係節のフレームとして記事に正しく含まれている。",
        "semantic_assertions": [
          {
            "id": "IC-06-A1",
            "statement": "what は、目的語の分類・基準に該当する内容または条件を表さなければならない。",
            "polarity": "must_hold",
            "scope": "what constitutes フレーム"
          }
        ]
      },
      {
        "id": "IC-07",
        "surface_form": "constitute an agreement",
        "frame": "〈communications/documents/conduct/terms〉 constitute 〈agreement/contract〉",
        "meaning": "複数の言動・文書・条項などが総体として合意・契約に当たる",
        "disposition": "included",
        "rationale": "〈communications/documents/conduct/terms〉 constitute 〈agreement/contract〉 は分類・成立条件の用法であり、主語となる事実群が目的語の agreement / contract に該当するという方向で理解する必要がある。",
        "semantic_assertions": [
          {
            "id": "IC-07-A1",
            "statement": "主語となる言動・文書・条項が、目的語の合意・契約に該当するか、その成立条件を満たす関係でなければならない。",
            "polarity": "must_hold",
            "scope": "agreement/contract を目的語にする分類フレーム"
          },
          {
            "id": "IC-07-A2",
            "statement": "agreement/contract を、権限主体が目的語として法的形式に整える組織設立フレームへ自動的に移してはならない。",
            "polarity": "must_not_hold",
            "scope": "agreement/contract の語義帰属"
          }
        ]
      },
      {
        "id": "IC-08",
        "surface_form": "constitute",
        "frame": "〈authority/institution/parties〉 constitute 〈committee/body/court/government〉",
        "meaning": "権限主体などが組織・機関を公式に設立する",
        "disposition": "included",
        "rationale": "〈authority/institution/parties〉 constitute 〈committee/body/court/government〉 は、既存部分の構成関係ではなく、主体が制度的行為によって新たな組織体を成立させる用法として記事に適切に含まれている。",
        "semantic_assertions": [
          {
            "id": "IC-08-A1",
            "statement": "主語は組織体を公式に設ける行為主体で、目的語はその行為により成立する組織体でなければならない。",
            "polarity": "must_hold",
            "scope": "組織設立の能動フレーム"
          },
          {
            "id": "IC-08-A2",
            "statement": "単なる構成員と全体の静的関係を、公式な設立行為として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "組織設立と部分―全体の境界"
          }
        ]
      },
      {
        "id": "IC-09",
        "surface_form": "be constituted under/by",
        "frame": "〈body〉 be constituted under/by 〈law/charter/authority〉",
        "meaning": "機関が法律・憲章・権限主体を根拠または設立主体として公式に成立する",
        "disposition": "included",
        "rationale": "〈body〉 be constituted under/by 〈law/charter/authority〉 は設立根拠または設立主体を示す受動フレームであり、記事は by が構成要素を示す別解釈も持ち得ると注意している。",
        "semantic_assertions": [
          {
            "id": "IC-09-A1",
            "statement": "under 句は通常、機関の設立根拠となる法・憲章を表さなければならない。",
            "polarity": "must_hold",
            "scope": "be constituted under フレーム"
          },
          {
            "id": "IC-09-A2",
            "statement": "by 句は文脈により設立主体または構成要素となるため、前置詞だけで語義を固定してはならない。",
            "polarity": "must_not_hold",
            "scope": "be constituted by の曖昧性"
          }
        ]
      },
      {
        "id": "IC-10",
        "surface_form": "constituted",
        "frame": "a duly/properly/legally constituted 〈body/authority/meeting〉",
        "meaning": "機関・権限主体・会議が必要な手続きや構成要件を満たして正式に成立している",
        "disposition": "included",
        "rationale": "a duly/properly/legally constituted 〈body/authority/meeting〉 は、適式な設立・招集・構成を表す過去分詞修飾であり、個々の決定の適法性まで保証しないという記事の限定も適切である。",
        "semantic_assertions": [
          {
            "id": "IC-10-A1",
            "statement": "修飾対象そのものが必要な法的・手続的・構成上の要件を満たして成立していなければならない。",
            "polarity": "must_hold",
            "scope": "duly/properly/legally constituted の分詞修飾"
          },
          {
            "id": "IC-10-A2",
            "statement": "その修飾対象が行うすべての個別行為の適法性まで含意してはならない。",
            "polarity": "must_not_hold",
            "scope": "分詞修飾の含意範囲"
          }
        ]
      },
      {
        "id": "IC-11",
        "surface_form": "constitute",
        "frame": "〈authority/law/document〉 constitute someone 〈office/role〉",
        "meaning": "権限者・法・公式文書が人を役職・役割に正式に任命する",
        "disposition": "included",
        "rationale": "〈authority/law/document〉 constitute someone 〈office/role〉 は、人を直接目的語、役職を目的格補語とする古風・法律的な任命フレームであり、組織そのものを設立する用法とは意味役割が異なる。",
        "semantic_assertions": [
          {
            "id": "IC-11-A1",
            "statement": "直接目的語は任命される人、目的格補語はその人に付与される役職・役割でなければならない。",
            "polarity": "must_hold",
            "scope": "人の任命を表す能動フレーム"
          },
          {
            "id": "IC-11-A2",
            "statement": "一般的な現代文体で appoint と同程度に無標な表現として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "任命用法のレジスター"
          }
        ]
      },
      {
        "id": "IC-12",
        "surface_form": "be constituted",
        "frame": "someone be constituted 〈office/role〉",
        "meaning": "人が役職・役割に正式に任命される",
        "disposition": "included",
        "rationale": "someone be constituted 〈office/role〉 は任命用法の受動フレームであり、記事は人と役職の意味役割を維持したまま限定的・公式な用法として示している。",
        "semantic_assertions": [
          {
            "id": "IC-12-A1",
            "statement": "主語は任命される人で、補語は付与される役職・役割でなければならない。",
            "polarity": "must_hold",
            "scope": "人の任命を表す受動フレーム"
          }
        ]
      },
      {
        "id": "IC-13",
        "surface_form": "legally constituted",
        "frame": "a legally constituted 〈officer/official〉",
        "meaning": "法や制度に基づいて正式な地位・権限を与えられた役職者",
        "disposition": "included",
        "rationale": "a legally constituted 〈officer/official〉 は、役職者が適法な根拠によりその地位・権限を得ていることを表す分詞修飾として記事に適切に含まれている。",
        "semantic_assertions": [
          {
            "id": "IC-13-A1",
            "statement": "修飾される役職者は、法または制度上の正規の根拠により地位・権限を得ていなければならない。",
            "polarity": "must_hold",
            "scope": "役職者を修飾する legally constituted"
          }
        ]
      },
      {
        "id": "IC-14",
        "surface_form": "constitute",
        "frame": "constitute as 〈category/role〉",
        "meaning": "as を介して分類・評価または任命を表す一般的な基本構文",
        "disposition": "excluded",
        "rationale": "constitute as 〈category/role〉 は通常の基本構文としては採らず、分類用法では直接目的語、任命用法では人＋役職補語を取るという記事の境界が妥当である。",
        "semantic_assertions": [
          {
            "id": "IC-14-A1",
            "statement": "分類・評価用法の標準フレームに as を必須要素として立ててはならない。",
            "polarity": "must_not_hold",
            "scope": "分類・評価用法の補文型"
          }
        ]
      },
      {
        "id": "IC-15",
        "surface_form": "constitute",
        "frame": "〈authority/parties〉 constitute 〈agreement/contract〉",
        "meaning": "権限主体・当事者が契約を目的語に取り、それに所定の法的形式を与える",
        "disposition": "excluded",
        "rationale": "権限主体・当事者が契約を目的語に取り、それに所定の法的形式を与える という独立した使役的法律フレームは、組織を公式に設立する用法から agreement/contract へ一般化できず、通常の constitute an agreement は IC-07 の分類関係として扱うべきである。",
        "semantic_assertions": [
          {
            "id": "IC-15-A1",
            "statement": "agreement/contract を目的語とするだけで、主語がその法的形式を整える使役的設立用法が成立するとしてはならない。",
            "polarity": "must_not_hold",
            "scope": "agreement/contract を目的語にする想定上の使役フレーム"
          }
        ]
      },
      {
        "id": "IC-16",
        "surface_form": "constitution",
        "frame": "派生名詞 constitution",
        "meaning": "構成・体質、または国家・組織の基本原則を定める憲法・規約",
        "disposition": "included",
        "rationale": "constitution は constitute と同じ語族の主要な派生名詞であり、記事の「構成・体質」と「憲法・規約」という意味範囲は妥当である。",
        "semantic_assertions": [
          {
            "id": "IC-16-A1",
            "statement": "派生名詞は構成・体質の意味と、基本原則を定める憲法・規約の意味を区別して含まなければならない。",
            "polarity": "must_hold",
            "scope": "語形成欄の constitution"
          }
        ]
      },
      {
        "id": "IC-17",
        "surface_form": "constitutional / constitutionally",
        "frame": "派生形容詞 constitutional と派生副詞 constitutionally",
        "meaning": "構成上・体質上・憲法上の性質、またはその様態",
        "disposition": "included",
        "rationale": "constitutional / constitutionally は構成・体質・憲法に関わる形容詞／副詞として記事の語形成欄に適切に含まれている。",
        "semantic_assertions": [
          {
            "id": "IC-17-A1",
            "statement": "形容詞と副詞の品詞差を保ち、体質的意味と憲法上の意味の双方を文脈に応じて認めなければならない。",
            "polarity": "must_hold",
            "scope": "語形成欄の constitutional / constitutionally"
          }
        ]
      },
      {
        "id": "IC-18",
        "surface_form": "constituent",
        "frame": "派生名詞・形容詞 constituent",
        "meaning": "構成要素・選挙区民、または構成する性質",
        "disposition": "included",
        "rationale": "constituent は名詞「構成要素・選挙区民」と形容詞「構成する」を持ち、政治義を constituency の構成員として説明する記事の境界も適切である。",
        "semantic_assertions": [
          {
            "id": "IC-18-A1",
            "statement": "政治義の constituent は代表者を選ぶ constituency の構成員を指さなければならない。",
            "polarity": "must_hold",
            "scope": "語形成欄の政治義 constituent"
          },
          {
            "id": "IC-18-A2",
            "statement": "政治義を constitute の文法上の目的語という関係から定義してはならない。",
            "polarity": "must_not_hold",
            "scope": "語形成欄の政治義 constituent"
          }
        ]
      },
      {
        "id": "IC-19",
        "surface_form": "reconstitute",
        "frame": "派生動詞 reconstitute 〈thing/substance〉",
        "meaning": "再構成する、元の状態へ戻す、または乾燥品などを液体で戻す",
        "disposition": "included",
        "rationale": "reconstitute は再構成・復元に加え、乾燥食品や薬剤などへ液体を加えて使用可能な状態へ戻す専門的用法を持ち、記事の説明は妥当である。",
        "semantic_assertions": [
          {
            "id": "IC-19-A1",
            "statement": "液体を加える専門用法では、乾燥・濃縮された対象を所定の状態または濃度へ戻す作用でなければならない。",
            "polarity": "must_hold",
            "scope": "語形成欄の reconstitute"
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "normal-translation-001",
        "taxonomy_id": "example_translation_alignment",
        "location": {
          "section": "lexical_relations",
          "line_start": 107,
          "line_end": 107,
          "exact_quote": "違い: 割合の用法では近いが、account for は「全体のうちどれだけを説明・占有するか」に焦点がある。constitute は割合だけでなく、部分が全体そのものを形作る関係にも使える。  "
        },
        "severity": "minor",
        "rationale": "この割合用法で必要なのは「全体のうちどれだけを占めるか」という数量関係だが、「占有する」は物や権利を所有・占拠する意味に寄り、直後の割合例が示す意味と日本語の述語が局所的にずれる。部分と全体の方向自体は逆転していない。",
        "evidence_link_ids": [],
        "suggested_direction": "「全体のうちどれだけを説明できるか・占めるか」のように、数量的な割合を表す「占める」へ直す。"
      },
      {
        "id": "normal-sense-structure-001",
        "taxonomy_id": "sense_boundary_overlap",
        "location": {
          "section": "sense_structure",
          "line_start": 190,
          "line_end": 190,
          "exact_quote": "【日本語訳・定義】組織、委員会、裁判所、政府などを正式に形成・設置し、公式の組織体として成立させることを表す。制度や文脈によって所定の手続きや権限付与を伴うことはあるが、constitute という語だけで法的有効性や実際の活動可能性まで一律に保証するわけではない。  "
        },
        "severity": "blocking",
        "rationale": "語義3の境界が「組織体を設立する」に限定されているため、法的用法の constitute an agreement（契約・合意を所定の形式に整える）に収録先がない。これは単なる対象分野の違いではなく、既存の設立フレームとは目的語の意味タイプと結果状態が異なる使役的な法的形式化であり、現行の定義・文法パターン・コアイメージ第3枝はいずれも agreement を「公式の組織体」として扱えない。",
        "evidence_link_ids": [
          "F005"
        ],
        "suggested_direction": "語義3を「組織・会議体を正式に成立させる／契約などを所定の法的形式に整える」まで明示的に拡張し、対応する目的語と構文を追加する。両フレームを一つの簡潔な定義で扱えない場合は、法的形式化を独立した語義として分割し、コアイメージにも対応枝を設ける。"
      },
      {
        "id": "normal-qualification-001",
        "taxonomy_id": "absolute_scope_counterexample",
        "location": {
          "section": "word_formation",
          "line_start": 26,
          "line_end": 26,
          "exact_quote": "`constituent` — 名詞「構成要素、選挙区民」、形容詞「構成する」。政治の「選挙区民」は constitute の目的語ではなく、代表者を選ぶ constituency の構成員を指す。  "
        },
        "severity": "blocking",
        "rationale": "「選挙区民」は constitute の目的語ではない、という無限定の統語的主張には反例がある。たとえば `These voters constitute the senator's constituents.` では政治義の constituents が constitute の直接目的語になる。ここで説明すべきなのは constituent の語義・名称が『constitute の目的語』という関係から定義されるのではないことだが、現状の文は実際の文中で目的語にできないという禁止にも読め、誤った一般化を生む。",
        "evidence_link_ids": [],
        "suggested_direction": "絶対的な構文制約を削除し、「政治義の constituent は『constitute の目的語』を意味する名称ではなく、constituency の構成員を指す」のように語形成上の関係だけへ限定する。"
      },
      {
        "id": "normal-evidence-001",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "pronunciation",
          "line_start": 15,
          "line_end": 15,
          "exact_quote": "米: /ˈkɑːnstəˌtuːt/｜英: /ˈkɒnstɪˌtjuːt/。3音節で、第1音節に主強勢、第3音節に第二強勢がある。米音では第1音節の母音が /ɑː/、第2音節が弱い /stə/、第3音節の初めが /t/ となる。英音では第1音節が /ɒ/、第2音節が /stɪ/、第3音節が /tjuːt/ となる。"
        },
        "severity": "blocking",
        "rationale": "C001 の F001 は米音の語末について /tuːt/ と /tjuːt/ の両方を記録し、F009 の根拠詳細も英音 /tjuːt/ に対して米音では一般的に /tuːt/ と限定している。本文は米音全般を単一の /tuːt/（第3音節初頭 /t/）として無限定に提示しており、引用根拠が示す米音 /tjuːt/ の変異を反映していない。",
        "evidence_link_ids": [
          "C001"
        ],
        "suggested_direction": "米音を『一般に /tuːt/』と限定し、/tjuːt/ も米音の変異として認められる旨を添えるか、米音を一つの代表形だけ示す表示だと明示する。"
      },
      {
        "id": "cold-constitute-001",
        "location": "語義1「構成する、（全体の一定割合を）占める」の日本語訳・定義／文法パターン",
        "severity": "low",
        "description": "割合を表す constitute の構文で、全体を示す of 句が常に明示されるかのように一般化している。",
        "reason": "「一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は of 句に現れる。」という説明は、完全な形の構造説明としては有用だが、全体が文脈から回収できる場合の省略を扱っていない。たとえば、直前に対象集団が示されていれば `Women constitute 45 percent.` や `Part-time staff constitute the majority.` のように of 句なしでも自然に言える。このままだと、学習者が of 句を必須要素だと誤って一般化する可能性がある。",
        "suggested_direction": "全体は通常 `of ...` で示すが、文脈上明らかな場合は `constitute 45 percent` や `constitute the majority` のように省略できる、と補足する。文法パターンにも of 句を任意にできる表記または省略例を加える。",
        "scope_anchors": [
          {
            "id": "anchor-constitute-001-a",
            "exact_quote": "一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は of 句に現れる。",
            "location_hint": "語義1の【日本語訳・定義】第2文"
          },
          {
            "id": "anchor-constitute-001-b",
            "exact_quote": "`〈group/category〉 constitute 〈割合〉 of 〈whole〉`＝集団・分類が全体の一定割合を占める",
            "location_hint": "語義1の【文法パターン】中央"
          }
        ]
      },
      {
        "id": "AF-01",
        "taxonomy_id": "sense_boundary_overlap",
        "location": {
          "section": "sense_structure",
          "line_start": 196,
          "line_end": 196,
          "exact_quote": "`constitute 〈agreement/body〉`＝契約・組織体に所定の法的形式を与える"
        },
        "severity": "blocking",
        "rationale": "「`constitute 〈agreement/body〉`＝契約・組織体に所定の法的形式を与える」は、正当な組織設立フレームと、agreement を目的語にする別の意味関係を一括している。さらに「法律文脈の `constitute an agreement/body` は、契約や組織体に必要な法的形式を与える意味になり得る。」と反復しているが、通常の constitute an agreement/contract は、言動・文書・条項などが合意・契約に「当たる／それを成す」という語義2の分類・成立条件フレームである。authority/parties が agreement を目的語に取って法的形式を付与するという使役的フレームを、constitute a body から一般化して教えるのは語義混入であり、学習者に不自然な産出を促すため修正が必要である。agreement/contract は語義2側へ再分類し、語義3は committee/body/court/government など公式に成立させる対象に限定すべきである。",
        "scope_anchors": [
          {
            "id": "AF-01-S1",
            "exact_quote": "`constitute 〈agreement/body〉`＝契約・組織体に所定の法的形式を与える",
            "location_hint": "語義3・文法パターン"
          },
          {
            "id": "AF-01-S2",
            "exact_quote": "法律文脈の `constitute an agreement/body` は、契約や組織体に必要な法的形式を与える意味になり得る。",
            "location_hint": "語義3・語法・注意"
          }
        ]
      }
    ],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U001",
        "source_fact_ids": [
          "F001",
          "F009"
        ],
        "canonical_statement": "Constitute has first-syllable primary stress, with UK /ɒ/ and /tjuːt/ and common US /ɑː/ and /tuːt/ realizations.",
        "disposition": "included",
        "rationale": "The pronunciation section records the regionally differentiated forms."
      },
      {
        "id": "U002",
        "source_fact_ids": [
          "F002"
        ],
        "canonical_statement": "Constituted and constituting are listed as inflected forms of the transitive verb constitute.",
        "disposition": "excluded",
        "rationale": "The selected locator lists the forms but does not atomically label each grammatical function, so the article omits the bundled inflection claim."
      },
      {
        "id": "U003",
        "source_fact_ids": [
          "F003",
          "F011",
          "F017"
        ],
        "canonical_statement": "Parts, members, or a category constitute a whole or a share of it in the parts-to-whole sense.",
        "disposition": "included",
        "rationale": "Sense 1 and its central frames directly express this well-attested relation."
      },
      {
        "id": "U004",
        "source_fact_ids": [
          "F007",
          "F010"
        ],
        "canonical_statement": "An act, fact, or situation constitutes a category when it qualifies as or can be regarded as that category.",
        "disposition": "included",
        "rationale": "Sense 2 separates this linking-like classification meaning from composition."
      },
      {
        "id": "U005",
        "source_fact_ids": [
          "F004",
          "F012",
          "F016",
          "F018"
        ],
        "canonical_statement": "Constitute formally establishes and authorizes an institution, committee, government, court, or similar body.",
        "disposition": "included",
        "rationale": "Sense 3 covers formal institutional establishment and its passive realization."
      },
      {
        "id": "U006",
        "source_fact_ids": [
          "F006",
          "F013",
          "F019"
        ],
        "canonical_statement": "In formal or legal language constitute can appoint a person to an office or function.",
        "disposition": "included",
        "rationale": "Sense 4 includes both direct-complement and as-complement appointment frames and labels their register."
      },
      {
        "id": "U007",
        "source_fact_ids": [
          "F005"
        ],
        "canonical_statement": "Constitute can give a body or agreement the form required for legal validity.",
        "disposition": "integrated",
        "rationale": "The lawful-form aspect is integrated into the formal-establishment sense without asserting universal legal effects."
      },
      {
        "id": "U008",
        "source_fact_ids": [
          "F014"
        ],
        "canonical_statement": "The passive constituted of construction may identify the components of a whole.",
        "disposition": "included",
        "rationale": "Sense 1 teaches this formal passive alongside the active direction contrast."
      },
      {
        "id": "U009",
        "source_fact_ids": [
          "F008",
          "F020"
        ],
        "canonical_statement": "Constitute derives through Middle English from Latin constituere, built from com- and statuere and associated with setting or establishing.",
        "disposition": "included",
        "rationale": "The etymology section presents the attested source and a restrained semantic bridge."
      },
      {
        "id": "U010",
        "source_fact_ids": [
          "F021"
        ],
        "canonical_statement": "Constitution is the related noun for makeup or structure and for fundamental governing principles or their document.",
        "disposition": "included",
        "rationale": "The word-formation section records these principal learner-relevant senses."
      },
      {
        "id": "U011",
        "source_fact_ids": [
          "F022"
        ],
        "canonical_statement": "Constitutional is the related adjective for bodily or structural makeup and for a governing constitution.",
        "disposition": "included",
        "rationale": "The word-formation section records both broad sense families."
      },
      {
        "id": "U012",
        "source_fact_ids": [
          "F023"
        ],
        "canonical_statement": "Constitutionally is the adverb derived from constitutional.",
        "disposition": "included",
        "rationale": "The word-formation section identifies the adverb and its broad meanings."
      },
      {
        "id": "U013",
        "source_fact_ids": [
          "F024",
          "F025"
        ],
        "canonical_statement": "Constituent is a related noun for a component or constituency member and an adjective meaning forming a whole.",
        "disposition": "included",
        "rationale": "The word-formation section distinguishes the noun and adjective and warns against confusing the political noun with a verb object."
      },
      {
        "id": "U014",
        "source_fact_ids": [
          "F026"
        ],
        "canonical_statement": "Reconstitute means constitute anew or restore a material by adding liquid.",
        "disposition": "included",
        "rationale": "The word-formation section records both the compositional and specialized restoration meanings."
      },
      {
        "id": "U015",
        "source_fact_ids": [
          "F015"
        ],
        "canonical_statement": "The physical set-or-place sense of constitute is archaic.",
        "disposition": "excluded",
        "rationale": "The generation inventory excludes this obsolete physical-placement sense because it has negligible modern learner value."
      }
    ]
  },
  "response_template": {
    "decision": null,
    "blockers": [],
    "notes": [],
    "target_results": [
      {
        "id": "pronunciation:001",
        "status": null,
        "notes": "",
        "target_id": "pronunciation:001"
      },
      {
        "id": "etymology:001",
        "status": null,
        "notes": "",
        "target_id": "etymology:001"
      },
      {
        "id": "etymology:002",
        "status": null,
        "notes": "",
        "target_id": "etymology:002"
      },
      {
        "id": "word_formation:001",
        "status": null,
        "notes": "",
        "target_id": "word_formation:001"
      },
      {
        "id": "word_formation:002",
        "status": null,
        "notes": "",
        "target_id": "word_formation:002"
      },
      {
        "id": "word_formation:003",
        "status": null,
        "notes": "",
        "target_id": "word_formation:003"
      },
      {
        "id": "word_formation:004",
        "status": null,
        "notes": "",
        "target_id": "word_formation:004"
      },
      {
        "id": "core_image:001",
        "status": null,
        "notes": "",
        "target_id": "core_image:001"
      },
      {
        "id": "core_image:002",
        "status": null,
        "notes": "",
        "target_id": "core_image:002"
      },
      {
        "id": "core_image:003",
        "status": null,
        "notes": "",
        "target_id": "core_image:003"
      },
      {
        "id": "core_image:004",
        "status": null,
        "notes": "",
        "target_id": "core_image:004"
      },
      {
        "id": "core_image:005",
        "status": null,
        "notes": "",
        "target_id": "core_image:005"
      },
      {
        "id": "sense_boundary:001",
        "status": null,
        "notes": "",
        "target_id": "sense_boundary:001"
      },
      {
        "id": "definition:001",
        "status": null,
        "notes": "",
        "target_id": "definition:001"
      },
      {
        "id": "frequency:001",
        "status": null,
        "notes": "",
        "target_id": "frequency:001"
      },
      {
        "id": "register:001",
        "status": null,
        "notes": "",
        "target_id": "register:001"
      },
      {
        "id": "grammar_pattern:001",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:001"
      },
      {
        "id": "grammar_pattern:002",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:002"
      },
      {
        "id": "grammar_pattern:003",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:003"
      },
      {
        "id": "collocation:001",
        "status": null,
        "notes": "",
        "target_id": "collocation:001"
      },
      {
        "id": "collocation:002",
        "status": null,
        "notes": "",
        "target_id": "collocation:002"
      },
      {
        "id": "collocation:003",
        "status": null,
        "notes": "",
        "target_id": "collocation:003"
      },
      {
        "id": "collocation:004",
        "status": null,
        "notes": "",
        "target_id": "collocation:004"
      },
      {
        "id": "collocation:005",
        "status": null,
        "notes": "",
        "target_id": "collocation:005"
      },
      {
        "id": "usage_note:001",
        "status": null,
        "notes": "",
        "target_id": "usage_note:001"
      },
      {
        "id": "usage_note:002",
        "status": null,
        "notes": "",
        "target_id": "usage_note:002"
      },
      {
        "id": "usage_note:003",
        "status": null,
        "notes": "",
        "target_id": "usage_note:003"
      },
      {
        "id": "synonym:001",
        "status": null,
        "notes": "",
        "target_id": "synonym:001"
      },
      {
        "id": "synonym:002",
        "status": null,
        "notes": "",
        "target_id": "synonym:002"
      },
      {
        "id": "synonym:003",
        "status": null,
        "notes": "",
        "target_id": "synonym:003"
      },
      {
        "id": "synonym:004",
        "status": null,
        "notes": "",
        "target_id": "synonym:004"
      },
      {
        "id": "sense_boundary:002",
        "status": null,
        "notes": "",
        "target_id": "sense_boundary:002"
      },
      {
        "id": "definition:002",
        "status": null,
        "notes": "",
        "target_id": "definition:002"
      },
      {
        "id": "frequency:002",
        "status": null,
        "notes": "",
        "target_id": "frequency:002"
      },
      {
        "id": "register:002",
        "status": null,
        "notes": "",
        "target_id": "register:002"
      },
      {
        "id": "grammar_pattern:004",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:004"
      },
      {
        "id": "grammar_pattern:005",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:005"
      },
      {
        "id": "grammar_pattern:006",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:006"
      },
      {
        "id": "grammar_pattern:007",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:007"
      },
      {
        "id": "collocation:006",
        "status": null,
        "notes": "",
        "target_id": "collocation:006"
      },
      {
        "id": "collocation:007",
        "status": null,
        "notes": "",
        "target_id": "collocation:007"
      },
      {
        "id": "collocation:008",
        "status": null,
        "notes": "",
        "target_id": "collocation:008"
      },
      {
        "id": "collocation:009",
        "status": null,
        "notes": "",
        "target_id": "collocation:009"
      },
      {
        "id": "collocation:010",
        "status": null,
        "notes": "",
        "target_id": "collocation:010"
      },
      {
        "id": "collocation:011",
        "status": null,
        "notes": "",
        "target_id": "collocation:011"
      },
      {
        "id": "usage_note:004",
        "status": null,
        "notes": "",
        "target_id": "usage_note:004"
      },
      {
        "id": "usage_note:005",
        "status": null,
        "notes": "",
        "target_id": "usage_note:005"
      },
      {
        "id": "usage_note:006",
        "status": null,
        "notes": "",
        "target_id": "usage_note:006"
      },
      {
        "id": "synonym:005",
        "status": null,
        "notes": "",
        "target_id": "synonym:005"
      },
      {
        "id": "synonym:006",
        "status": null,
        "notes": "",
        "target_id": "synonym:006"
      },
      {
        "id": "synonym:007",
        "status": null,
        "notes": "",
        "target_id": "synonym:007"
      },
      {
        "id": "synonym:008",
        "status": null,
        "notes": "",
        "target_id": "synonym:008"
      },
      {
        "id": "sense_boundary:003",
        "status": null,
        "notes": "",
        "target_id": "sense_boundary:003"
      },
      {
        "id": "definition:003",
        "status": null,
        "notes": "",
        "target_id": "definition:003"
      },
      {
        "id": "frequency:003",
        "status": null,
        "notes": "",
        "target_id": "frequency:003"
      },
      {
        "id": "register:003",
        "status": null,
        "notes": "",
        "target_id": "register:003"
      },
      {
        "id": "grammar_pattern:008",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:008"
      },
      {
        "id": "grammar_pattern:009",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:009"
      },
      {
        "id": "grammar_pattern:010",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:010"
      },
      {
        "id": "grammar_pattern:011",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:011"
      },
      {
        "id": "collocation:012",
        "status": null,
        "notes": "",
        "target_id": "collocation:012"
      },
      {
        "id": "collocation:013",
        "status": null,
        "notes": "",
        "target_id": "collocation:013"
      },
      {
        "id": "collocation:014",
        "status": null,
        "notes": "",
        "target_id": "collocation:014"
      },
      {
        "id": "collocation:015",
        "status": null,
        "notes": "",
        "target_id": "collocation:015"
      },
      {
        "id": "collocation:016",
        "status": null,
        "notes": "",
        "target_id": "collocation:016"
      },
      {
        "id": "usage_note:007",
        "status": null,
        "notes": "",
        "target_id": "usage_note:007"
      },
      {
        "id": "usage_note:008",
        "status": null,
        "notes": "",
        "target_id": "usage_note:008"
      },
      {
        "id": "usage_note:009",
        "status": null,
        "notes": "",
        "target_id": "usage_note:009"
      },
      {
        "id": "usage_note:010",
        "status": null,
        "notes": "",
        "target_id": "usage_note:010"
      },
      {
        "id": "synonym:009",
        "status": null,
        "notes": "",
        "target_id": "synonym:009"
      },
      {
        "id": "synonym:010",
        "status": null,
        "notes": "",
        "target_id": "synonym:010"
      },
      {
        "id": "synonym:011",
        "status": null,
        "notes": "",
        "target_id": "synonym:011"
      },
      {
        "id": "sense_boundary:004",
        "status": null,
        "notes": "",
        "target_id": "sense_boundary:004"
      },
      {
        "id": "definition:004",
        "status": null,
        "notes": "",
        "target_id": "definition:004"
      },
      {
        "id": "frequency:004",
        "status": null,
        "notes": "",
        "target_id": "frequency:004"
      },
      {
        "id": "register:004",
        "status": null,
        "notes": "",
        "target_id": "register:004"
      },
      {
        "id": "grammar_pattern:012",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:012"
      },
      {
        "id": "grammar_pattern:013",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:013"
      },
      {
        "id": "grammar_pattern:014",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:014"
      },
      {
        "id": "collocation:017",
        "status": null,
        "notes": "",
        "target_id": "collocation:017"
      },
      {
        "id": "collocation:018",
        "status": null,
        "notes": "",
        "target_id": "collocation:018"
      },
      {
        "id": "collocation:019",
        "status": null,
        "notes": "",
        "target_id": "collocation:019"
      },
      {
        "id": "usage_note:011",
        "status": null,
        "notes": "",
        "target_id": "usage_note:011"
      },
      {
        "id": "usage_note:012",
        "status": null,
        "notes": "",
        "target_id": "usage_note:012"
      },
      {
        "id": "usage_note:013",
        "status": null,
        "notes": "",
        "target_id": "usage_note:013"
      },
      {
        "id": "synonym:012",
        "status": null,
        "notes": "",
        "target_id": "synonym:012"
      },
      {
        "id": "synonym:013",
        "status": null,
        "notes": "",
        "target_id": "synonym:013"
      },
      {
        "id": "synonym:014",
        "status": null,
        "notes": "",
        "target_id": "synonym:014"
      }
    ],
    "relation_results": [
      {
        "id": "risk_sense_pair:001",
        "status": null,
        "notes": "",
        "relation_id": "risk_sense_pair:001"
      },
      {
        "id": "risk_sense_pair:002",
        "status": null,
        "notes": "",
        "relation_id": "risk_sense_pair:002"
      },
      {
        "id": "risk_sense_pair:003",
        "status": null,
        "notes": "",
        "relation_id": "risk_sense_pair:003"
      },
      {
        "id": "example_translation:001",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:001"
      },
      {
        "id": "example_translation:002",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:002"
      },
      {
        "id": "example_translation:003",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:003"
      },
      {
        "id": "example_translation:004",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:004"
      },
      {
        "id": "example_translation:005",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:005"
      },
      {
        "id": "example_translation:006",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:006"
      },
      {
        "id": "example_translation:007",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:007"
      },
      {
        "id": "example_translation:008",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:008"
      },
      {
        "id": "example_translation:009",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:009"
      },
      {
        "id": "example_translation:010",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:010"
      },
      {
        "id": "example_translation:011",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:011"
      },
      {
        "id": "example_translation:012",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:012"
      },
      {
        "id": "example_translation:013",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:013"
      },
      {
        "id": "example_translation:014",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:014"
      },
      {
        "id": "example_translation:015",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:015"
      },
      {
        "id": "example_translation:016",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:016"
      },
      {
        "id": "example_translation:017",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:017"
      },
      {
        "id": "example_translation:018",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:018"
      },
      {
        "id": "example_translation:019",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:019"
      },
      {
        "id": "sense_definition_consistency:001",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:001"
      },
      {
        "id": "definition_usage_consistency:001",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:001"
      },
      {
        "id": "definition_usage_consistency:002",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:002"
      },
      {
        "id": "definition_usage_consistency:003",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:003"
      },
      {
        "id": "definition_lexical_relation_consistency:001",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:001"
      },
      {
        "id": "pattern_example_coverage:001",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:001"
      },
      {
        "id": "pattern_example_coverage:002",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:002"
      },
      {
        "id": "pattern_example_coverage:003",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:003"
      },
      {
        "id": "sense_definition_consistency:002",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:002"
      },
      {
        "id": "definition_usage_consistency:004",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:004"
      },
      {
        "id": "definition_usage_consistency:005",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:005"
      },
      {
        "id": "definition_usage_consistency:006",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:006"
      },
      {
        "id": "definition_lexical_relation_consistency:002",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:002"
      },
      {
        "id": "pattern_example_coverage:004",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:004"
      },
      {
        "id": "pattern_example_coverage:005",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:005"
      },
      {
        "id": "pattern_example_coverage:006",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:006"
      },
      {
        "id": "pattern_example_coverage:007",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:007"
      },
      {
        "id": "sense_definition_consistency:003",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:003"
      },
      {
        "id": "definition_usage_consistency:007",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:007"
      },
      {
        "id": "definition_usage_consistency:008",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:008"
      },
      {
        "id": "definition_usage_consistency:009",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:009"
      },
      {
        "id": "definition_usage_consistency:010",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:010"
      },
      {
        "id": "definition_lexical_relation_consistency:003",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:003"
      },
      {
        "id": "pattern_example_coverage:008",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:008"
      },
      {
        "id": "pattern_example_coverage:009",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:009"
      },
      {
        "id": "pattern_example_coverage:010",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:010"
      },
      {
        "id": "pattern_example_coverage:011",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:011"
      },
      {
        "id": "sense_definition_consistency:004",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:004"
      },
      {
        "id": "definition_usage_consistency:011",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:011"
      },
      {
        "id": "definition_usage_consistency:012",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:012"
      },
      {
        "id": "definition_usage_consistency:013",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:013"
      },
      {
        "id": "definition_lexical_relation_consistency:004",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:004"
      },
      {
        "id": "pattern_example_coverage:012",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:012"
      },
      {
        "id": "pattern_example_coverage:013",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:013"
      },
      {
        "id": "pattern_example_coverage:014",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:014"
      },
      {
        "id": "core_inventory_consistency:001",
        "status": null,
        "notes": "",
        "relation_id": "core_inventory_consistency:001"
      },
      {
        "id": "core_sense_mapping:001",
        "status": null,
        "notes": "",
        "relation_id": "core_sense_mapping:001"
      },
      {
        "id": "core_sense_mapping:002",
        "status": null,
        "notes": "",
        "relation_id": "core_sense_mapping:002"
      },
      {
        "id": "core_sense_mapping:003",
        "status": null,
        "notes": "",
        "relation_id": "core_sense_mapping:003"
      },
      {
        "id": "core_sense_mapping:004",
        "status": null,
        "notes": "",
        "relation_id": "core_sense_mapping:004"
      },
      {
        "id": "article_learning_risk:001",
        "status": null,
        "notes": "",
        "relation_id": "article_learning_risk:001"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "IC-01",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-01-A1",
          "IC-01-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-01-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-01-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-02",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-02-A1",
          "IC-02-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-02-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-02-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-03",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-03-A1"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-03-A1",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-04",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-04-A1",
          "IC-04-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-04-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-04-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-05",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-05-A1",
          "IC-05-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-05-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-05-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-06",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-06-A1"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-06-A1",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-07",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-07-A1",
          "IC-07-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-07-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-07-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-08",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-08-A1",
          "IC-08-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-08-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-08-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-09",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-09-A1",
          "IC-09-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-09-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-09-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-10",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-10-A1",
          "IC-10-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-10-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-10-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-11",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-11-A1",
          "IC-11-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-11-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-11-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-12",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-12-A1"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-12-A1",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-13",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-13-A1"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-13-A1",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-14",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-14-A1"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-14-A1",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-15",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-15-A1"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-15-A1",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-16",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-16-A1"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-16-A1",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-17",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-17-A1"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-17-A1",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-18",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-18-A1",
          "IC-18-A2"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-18-A1",
            "status": null,
            "notes": ""
          },
          {
            "id": "IC-18-A2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "IC-19",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "IC-19-A1"
        ],
        "verified_body_sha256": "4d990864ada94369312c779118f82c92a81c8bb86dcc6edd10a482f9dabd0d0d",
        "assertion_results": [
          {
            "id": "IC-19-A1",
            "status": null,
            "notes": ""
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "normal-translation-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-sense-structure-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-qualification-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-evidence-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "cold-constitute-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "AF-01",
        "status": null,
        "notes": ""
      }
    ],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U001",
        "status": null,
        "notes": "",
        "union_id": "U001"
      },
      {
        "id": "U002",
        "status": null,
        "notes": "",
        "union_id": "U002"
      },
      {
        "id": "U003",
        "status": null,
        "notes": "",
        "union_id": "U003"
      },
      {
        "id": "U004",
        "status": null,
        "notes": "",
        "union_id": "U004"
      },
      {
        "id": "U005",
        "status": null,
        "notes": "",
        "union_id": "U005"
      },
      {
        "id": "U006",
        "status": null,
        "notes": "",
        "union_id": "U006"
      },
      {
        "id": "U007",
        "status": null,
        "notes": "",
        "union_id": "U007"
      },
      {
        "id": "U008",
        "status": null,
        "notes": "",
        "union_id": "U008"
      },
      {
        "id": "U009",
        "status": null,
        "notes": "",
        "union_id": "U009"
      },
      {
        "id": "U010",
        "status": null,
        "notes": "",
        "union_id": "U010"
      },
      {
        "id": "U011",
        "status": null,
        "notes": "",
        "union_id": "U011"
      },
      {
        "id": "U012",
        "status": null,
        "notes": "",
        "union_id": "U012"
      },
      {
        "id": "U013",
        "status": null,
        "notes": "",
        "union_id": "U013"
      },
      {
        "id": "U014",
        "status": null,
        "notes": "",
        "union_id": "U014"
      },
      {
        "id": "U015",
        "status": null,
        "notes": "",
        "union_id": "U015"
      }
    ],
    "checker_recheck_results": [
      {
        "id": "translation",
        "pass_id": "translation",
        "status": null,
        "notes": ""
      },
      {
        "id": "sense-structure",
        "pass_id": "sense-structure",
        "status": null,
        "notes": ""
      },
      {
        "id": "frame-relation",
        "pass_id": "frame-relation",
        "status": null,
        "notes": ""
      },
      {
        "id": "example-attribution",
        "pass_id": "example-attribution",
        "status": null,
        "notes": ""
      },
      {
        "id": "qualification",
        "pass_id": "qualification",
        "status": null,
        "notes": ""
      },
      {
        "id": "pronunciation",
        "pass_id": "pronunciation",
        "status": null,
        "notes": ""
      },
      {
        "id": "evidence",
        "pass_id": "evidence",
        "status": null,
        "notes": ""
      }
    ],
    "chronology_results": [
      {
        "id": "body_hash_binding",
        "check_id": "body_hash_binding",
        "status": null,
        "notes": ""
      },
      {
        "id": "cold_and_normal_before_revision",
        "check_id": "cold_and_normal_before_revision",
        "status": null,
        "notes": ""
      },
      {
        "id": "revision_before_final_blind",
        "check_id": "revision_before_final_blind",
        "status": null,
        "notes": ""
      },
      {
        "id": "final_blind_before_seal",
        "check_id": "final_blind_before_seal",
        "status": null,
        "notes": ""
      },
      {
        "id": "post_blind_completion",
        "check_id": "post_blind_completion",
        "status": null,
        "notes": ""
      }
    ]
  },
  "input_bindings": {
    "pass_findings.json": "7bd6383618cff085179a0d06094a3cae9ce04594a1c9f574b15ba0b98ada4548",
    "cold_review.json": "25640520be865f6272c68396a6751392d3204d08d7369df273adf3ec65558ce2",
    "final_blind.json": "dd3b59cc2c2c68157bd84d96e995017bc6f8806e4232ba100bb8db71b8ec49d1",
    "blind_seal.json": "ab27784813fcdc8841adcbc2188c535ff44cb1967b8d37245132b59205f2304d",
    "pre_blind_resolution.json": "9fa686c04c5fbc1a1fdda4ad79666e87ccef5af0f3fea718e3042528a1a04cc7",
    "pre_blind_revision.json": "3fb190dae6ffb7de37c270cefe677b9f57d3a8a42eaab0ca0092b931fb41fc9f",
    "checker_recheck_manifest.json": "2f2495a694b0492ed4c48d4b6032998fc611ff679b166839ed99c8e1370d89f3",
    "post_blind_resolution.json": "8c4c14fdced24797cf7902e9366d432abd9d1b7b3c991c6aff019aedd54f16cb",
    "post_blind_verification.json": "d01789a9c9ebd3cdc324c12f2d1d2bc068dfd6ac02e3c83254132c4baf6fc6fc",
    "targeted_adjudications.json": "170bcecc13fe9ab6439407fcebba3dfef9a7160d4f7ac76c211d38cd5d161b80",
    "source_inventory.json": "feb88c9d89dbe5e282f1db5bdd213ba1d2d91b174409d58781eadf2a1f19b44b",
    "resolutions.json": "3222a1cec6f7803574078362b10888ae921d8b2c9e6e7b4bf95b2fb9867fb646",
    "check_passes/checker_passes.stage1.json": "d532dfa4216cfd5c1a516930879ac24eefd0a2adf2ebeb1237b88316081e95d4",
    "check_passes/evidence.json": "413d31088e4a1987944113954b39f3a14397b8edbdcf694cc501d9adf9e794b6",
    "check_passes/evidence.request.json": "9a16e8529592ce245ea131e601fc31b7337ac7678f11c0901246c5508e61871d",
    "check_passes/example-attribution.alignment-key.json": "17e9a5c0a042ef0f8a4721e29f2f5e7fae0419ea29673f9198af63485c685ae6",
    "check_passes/example-attribution.blind-record.json": "40f6582c11c267f67a393ae597a4962d38cf699dcd3a8b0c98ad8645e69d0bd8",
    "check_passes/example-attribution.json": "f56f341bad994985a9a26cdd1b98aef2380ab6571121e59c403e3d9b20cd05a3",
    "check_passes/example-attribution.request.json": "74376e919561364f0cd0b4d93dd2c6974b5021c5288ae8928d2f8b63d024a281",
    "check_passes/frame-relation.antonym-axis.adjudication-record.json": "8a9a059af5abb06924252f829b842f63eacfc4ca6c42029e5b332e3ead78891b",
    "check_passes/frame-relation.antonym-axis.alignment-key.json": "719f21de0410fa9d033a06a54b21d74f0f50e86139456299b605176dafc9dd5b",
    "check_passes/frame-relation.antonym-axis.blind-record.json": "68587f33562a4d0f7b3cd2ceb546760d678fae74c435a448517311f8847a0f88",
    "check_passes/frame-relation.antonym-axis.stage2.request.json": "68cee4a667916f349fec0b5507517257391ce86fc6281d199b690458031f50bb",
    "check_passes/frame-relation.request.json": "78c072b528d5e50ab0ce176ab892aefe152f206bd33b25589a8e585d30363fef",
    "check_passes/input_snapshot.json": "e9536fa63fa006e8dba763be540d675ec007ea6565cb35831e16fd7b326f3980",
    "check_passes/pronunciation.json": "d8dde96513eb0b4fb67c6bbaaa0d1f6ee69a0a8eecb56a8743d481d2a7d21b30",
    "check_passes/pronunciation.request.json": "28c3ed035a9661f8452156d0d5d870ea33d84dc50fb3a4b6f0500bd835654c2a",
    "check_passes/qualification.json": "e4da484ca0508f7a6d25cb35ab3da9157c9baf485c4390474222e5fe2de0c252",
    "check_passes/qualification.request.json": "6f6336a0955cfb4379ca32fa0b297b1444bcb99a404ab39b5db29b082a57c7ba",
    "check_passes/sense-structure.json": "db574b03db4f6eb339cf870b0f59d7ff07c6c4b457ea0326df6137ce50ca7f24",
    "check_passes/sense-structure.request.json": "cd1e71ef37bc20d1504663ca04d408fc54a7c1b536e50282f64dd08c39e6f2de",
    "check_passes/translation.json": "803ad1b85da7796082aa83cf118f066e218e3974933fee343c7715c55c881dc3",
    "check_passes/translation.request.json": "d076406b972f9659506a617602a2819429311f79142eb457e80b24097cb7725f",
    "recheck/evidence.json": "72a5458c33f2b1c4d4e00e9a09871a4339d2798b3d50c0b04635b704020b0822",
    "recheck/evidence.request.json": "34f6e6882f093a1279eb24bbf5b32989d884b34c3e50a95346380eaa6d481d9a",
    "recheck/evidence.response.json": "72a5458c33f2b1c4d4e00e9a09871a4339d2798b3d50c0b04635b704020b0822",
    "recheck/example-attribution.alignment-key.json": "70d43c627d61cfbf3969287670e3a8a03f78665009466d13b7b48f7b98cb7779",
    "recheck/example-attribution.json": "486418906759ab37b6db49b0ae093e3220aed2c5b0ea13d5e83fe624d1e71a54",
    "recheck/example-attribution.request.json": "57561e2e6c9e95137435340d2de55740d6e9c58f031e71394a5dc68f4f023fda",
    "recheck/example-attribution.response.json": "486418906759ab37b6db49b0ae093e3220aed2c5b0ea13d5e83fe624d1e71a54",
    "recheck/frame-relation.antonym-axis.adjudication-record.json": "8e274cb3971523e26398d34cd0dfe10d66ca4ab9077e1b976fcc89c0811f98e6",
    "recheck/frame-relation.antonym-axis.alignment-key.json": "4d9e41841a9fcea6cf74c99d98751d865080b337443d76b6ad54f555dea4091f",
    "recheck/frame-relation.antonym-axis.blind-record.json": "547179d0e02ec7e3218dd79b5e95c2d2dc14fbbc1866b85a423ceff97490ccc4",
    "recheck/frame-relation.json": "eb9c1375e1b649f49af45001392febe35ddf5a1385f38c2439e7c48db0a10161",
    "recheck/frame-relation.request.json": "7ea112ae8136bcb08e335198e6e5d1729549d9b0709961561a9c6028b2808fd6",
    "recheck/frame-relation.response.json": "6df87f92447b172eb35d23e0ed31c3beef615d3212e6f86b0f58f6713a93c6a5",
    "recheck/frame-relation.stage2.request.json": "66e40adfe58e676688711a74d460fd012f92d6a6a00ae61d71832d32abd8cf59",
    "recheck/frame-relation.stage2.response.json": "8e274cb3971523e26398d34cd0dfe10d66ca4ab9077e1b976fcc89c0811f98e6",
    "recheck/pronunciation.json": "d578d73e9482b9dff91549a173f50893906973bbcc906350890aef6107145c7b",
    "recheck/pronunciation.request.json": "de087f2a82094892e05b58c9d64ffb54367b89ea8812a1a7b3d7d3bfbd033120",
    "recheck/pronunciation.response.json": "d578d73e9482b9dff91549a173f50893906973bbcc906350890aef6107145c7b",
    "recheck/qualification.json": "8a1e310e0776af90c2bfd2ddfe6d19392b52633da6202a7f67a1df6f63034226",
    "recheck/qualification.request.json": "0d770aeba49f252b29b85d6a7a92448aa87489d7de01723bb094f9fdf91f9872",
    "recheck/qualification.response.json": "8a1e310e0776af90c2bfd2ddfe6d19392b52633da6202a7f67a1df6f63034226",
    "recheck/sense-structure.json": "1f6b4eb450314fbfd68e843d36864a2cf2c231b86dc549cb2da23c48492ef8c2",
    "recheck/sense-structure.request.json": "109edc1e4e03697d279d83a430df8c0b9420142d313c04b97f7d048a2e8176d3",
    "recheck/sense-structure.response.json": "1f6b4eb450314fbfd68e843d36864a2cf2c231b86dc549cb2da23c48492ef8c2",
    "recheck/translation.json": "0e915c4df867901d0d663e6f0cc54cf79f3e55744c1a050fba09d0970440fd1f",
    "recheck/translation.request.json": "8a84e338ea864b65e425ab323db7470160f8708a03079f78e56b7e102f29f693",
    "recheck/translation.response.json": "0e915c4df867901d0d663e6f0cc54cf79f3e55744c1a050fba09d0970440fd1f"
  },
  "contract_version": "review_preflight_v1"
}
```
