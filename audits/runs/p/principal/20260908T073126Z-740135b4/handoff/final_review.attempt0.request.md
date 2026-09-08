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
  "entry_body": "\n＃発音記号\n\n発音: /ˈprɪnsəpəl/。形容詞と名詞で同じ発音を用いる。  \n\n＃語源\n\n中英語・古フランス語を経て、ラテン語 *principalis*「第一の、主要な」にさかのぼる。その基になった *princeps* は、*primus*「第一の」と *capere*「取る」に関係し、「第一の位置を占める者」という発想を持つ。語源には「第一の、主要な」という意味的なつながりがある。  \n\n＃語形成\n\n・principally：`principal` の副詞形。  \n・principalship：`principal` の名詞派生形。  \n・principal-agent relationship：法律上の本人・代理人関係を表す複合表現。  \n\n＃コアイメージ\n\n`principal` の中心は、「重要度・権限・責任・金額の土台として第一に位置する」である。形容詞では主要なものを選び出し、名詞では権限・主導的地位を持つ人や教育機関の長、舞台芸術の主要演者やオーケストラの首席奏者、利息・収益に対する元の金額や信託収益に対する財産本体、法的関係の主要当事者を指す。  \n・重要度で第一に位置するもの → 「主要な、最も重要な」（語義1）  \n・組織で権限・主導的地位を持つ人、特に教育機関の長 → 「上級責任者、校長、学長」（語義2）  \n・舞台芸術の主要演者、またはオーケストラで一つのセクションを率いる奏者 → 「主要演者、首席奏者」（語義3）  \n・利息・収益に対する基礎額、または信託収益に対する財産本体 → 「元金、元本、信託元本」（語義4）  \n・代理関係で権限の源として第一に位置する当事者 → 「本人、依頼者」（語義5）  \n・適用法上 `principal` と分類される犯罪関与者 → 「犯罪関与者」（語義6）  \n・債務・保証関係で第一次的責任を負う者 → 「主たる債務者・義務者」（語義7）  \n\n＃意味・用法・関連表現\n\n1. 【形容詞】主要な、最も重要な、第一の\n\n【日本語訳・定義】複数の原因、目的、人物、場所、要素などの中で、重要度・影響力・順位が最も高い、または特に高いものを示す。単に時間的に最初という意味ではなく、重要性や中心性の評価を表す。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準～やや形式的。報道、ビジネス、学術、行政で広く使う。日常会話では `main` がより普通なことが多い。  \n\n【文法パターン】限定用法で `principal + 〈名詞〉` の形を取り、「主要な～」を表す。  \n\n【コロケーション】\n\n・`the principal reason for ...`  \n用途: 出来事・状況・判断・行動などについて、最も重要な理由を示す。  \n例: The principal reason for the delay was a shortage of parts.  \n訳: 遅延の主な理由は部品不足だった。  \n\n・`the principal cause of ...`  \n用途: 出来事を引き起こした最も重要な原因を示す。  \n例: Investigators identified corrosion as the principal cause of the failure.  \n訳: 調査担当者は、腐食をその故障の主因と特定した。  \n\n・`a principal source of ...`  \n用途: 物・情報・収入などの主要な供給源を示す。  \n例: Tourism is a principal source of income for the island.  \n訳: 観光はその島の主要な収入源の一つである。  \n\n・`one of the principal 〈複数名詞〉`  \n用途: 最重要候補が複数ある中の一つであることを示す。  \n例: She is one of the principal architects of the reform.  \n訳: 彼女はその改革の主要な立案者の一人である。  \n\n・`a principal dancer`  \n用途: `principal` を限定用法の形容詞として用い、舞台芸術で主要な役を担うダンサーを表す。  \n例: She is a principal dancer.  \n訳: 彼女は主要な役を担うダンサーである。  \n\n【語法・注意】`principal` と `principle` は綴りも意味も異なる。`principle` は「基本的な規則・法則」を表す名詞で、`principal` は「最も重要な」を表す形容詞にもなるため、両者を混同しない。  \n\n【類義語】\n\n・main  \n定義: 複数のものの中で中心的・最重要である。  \n頻度: 〈10/10〉  \n違い: `main` は日常語で範囲が広い。`principal` はより形式的で、順位・重要性・影響力が高いことを意識させる。  \n例: Our main goal is to reduce waiting times.  \n訳: 私たちの主な目標は待ち時間を減らすことだ。  \n\n・primary  \n定義: 第一順位・第一段階である、または最も基本的である。  \n頻度: 〈9/10〉  \n違い: `primary` は重要性に加え、順序・段階・基本性にも焦点を置ける。`principal` は主として相対的な重要度や地位を表す。  \n例: Safety is our primary concern.  \n訳: 安全が私たちの最優先事項である。  \n\n・chief  \n定義: 同種の中で最上位・最重要である。  \n頻度: 〈8/10〉  \n違い: `chief` は役職名や「最大の原因・懸念」によく使われ、最上位性を強く示す。`principal` は文章語として原因・目的・人物・場所などに幅広く使う。  \n例: Cost remains the chief obstacle to expansion.  \n訳: 費用が依然として拡大の最大の障害である。  \n\n・leading  \n定義: ある分野で先頭に立ち、大きな影響力や高い評価を持つ。  \n頻度: 〈9/10〉  \n違い: `leading` は人・企業・研究機関などの実績や影響力を強調しやすい。`principal` は実績評価を必須とせず、対象内での中心性を示す。  \n例: She is a leading expert on marine ecosystems.  \n訳: 彼女は海洋生態系の第一人者である。  \n\n【反意語】\n\n・secondary  \n定義: 第一ではなく、重要度・順位が二次的である。  \n頻度: 〈8/10〉  \n違い: 重要度・順位の軸で `principal` と方向が反対になり、主要なものに対する従属的・補助的なものを表す。  \n例: Price was only a secondary consideration.  \n訳: 価格は二次的な考慮事項にすぎなかった。  \n\n・minor  \n定義: 重要性・規模・影響が比較的小さい。  \n頻度: 〈9/10〉  \n違い: `principal` との程度軸上の対立で、最重要・主要ではない小さな要素を表す。  \n例: The report contains a few minor errors.  \n訳: その報告書には小さな誤りがいくつかある。  \n\n2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長\n\n【日本語訳・定義】組織で支配的権限または主導的地位を持つ人。特に、学校、カレッジ、その他の教育機関を管理する最高責任者を指す。教育上どの種類の機関を指すかは地域と制度によって異なる。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】標準～やや形式的。企業・専門組織では権限または主導的地位を持つ人を表す。教育分野では学校・教育機関の長を表し、イングランドではカレッジの長を指す場合がある。  \n\n【文法パターン】一般の権限者は `a principal with controlling authority`。教育機関の長は `the principal + be + in charge of 〈学校〉`。  \n\n【コロケーション】\n\n・`a principal with controlling authority`  \n用途: 支配的権限を持つ人という一般の人物用法を表す。  \n例: A principal with controlling authority approved the proposal.  \n訳: 支配的権限を持つ責任者がその提案を承認した。  \n\n・`the principal + be + in charge of 〈学校〉`  \n用途: 教育機関を管理する長であることを表す。  \n例: The principal is in charge of the school.  \n訳: その校長が学校の管理を担っている。  \n\n【語法・注意】一般の「重要人物」を自由に指す語ではなく、権限や主導的地位が文脈上確立した人に用いる。教育上の役職名は地域や制度によって異なるため、日本語の「校長」を機械的にすべて `principal` としない。  \n\n【類義語】\n\n・head  \n定義: 学校・組織などの長。  \n頻度: 〈9/10〉  \n違い: `head` は組織の長を広く表す。`principal` は権限・主導的地位を持つ人を表し、特に教育機関で役職名として用いられる。  \n例: She is the head of a large secondary school.  \n訳: 彼女は大規模な中等学校の校長である。  \n\n3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者\n\n【日本語訳・定義】舞台芸術で主要な役を担う演者、またはオーケストラで一つのセクションを率いる奏者。一般の重要人物ではなく、芸術分野で確立した役割名を指す。  \n\n【頻度】〈3/10〉  \n\n【レジスター/領域】舞台芸術・オーケストラ・音楽の専門語。  \n\n【文法パターン】舞台芸術の主要演者を名詞で表す場合は `〈演者〉 + be + a principal`。オーケストラの役職は `the principal + be + the first player of 〈セクション〉`。  \n\n【コロケーション】\n\n・`be a principal`  \n用途: 舞台芸術の文脈で、主要な役を担う演者を名詞 `principal` で表す。  \n例: In this ballet company, she is a principal.  \n訳: このバレエ団で、彼女は主要な役を担う演者である。  \n\n・`the principal + be + the first player of 〈オーケストラのセクション〉`  \n用途: オーケストラのセクションで首席を務める奏者を表す。  \n例: The principal is the first player of the violin section.  \n訳: その首席奏者はバイオリン・セクションの第一奏者である。  \n\n【語法・注意】舞台芸術団体やオーケストラ内で確立した役割名として用い、一般の「重要人物」には広げない。  \n\n【類義語】\n\n・section leader  \n定義: オーケストラで一つのセクションを率いる奏者。  \n頻度: 〈4/10〉  \n違い: 役割を説明する一般的な表現で、`principal` は確立した役職名として用いられる。  \n例: The section leader rehearsed the difficult passage.  \n訳: セクションの首席奏者は難しい楽節を練習した。  \n\n4. 【名詞・金融／信託法】元金、元本、信託財産の元本\n\n【日本語訳・定義】借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。信託法では、収益と区別される信託財産そのもの、すなわち信託元本・corpusを指す。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】金融、融資、投資、会計、信託法。金融義は日常的なローン説明にも現れ、信託義は専門的である。  \n\n【文法パターン】金融では `principal + be + the initial amount invested`／`principal + be + distinct from interest`。信託法では `trust principal + be + distinct from income`。  \n\n【コロケーション】\n\n・`principal + be + the initial amount invested`  \n用途: 投資で、収益の基礎となる最初の金額を表す。  \n例: The principal is the initial amount invested.  \n訳: 元本とは最初に投資された金額である。  \n\n・`principal + be + distinct from interest`  \n用途: 借入・貸付の元金を利息と区別して表す。  \n例: Principal is distinct from interest on the loan.  \n訳: 元金はその融資の利息とは別のものである。  \n\n・`trust principal + be + distinct from income`  \n用途: 信託財産の元本を、そこから生じる収益と区別する。  \n例: Trust principal is distinct from income.  \n訳: 信託元本は収益とは別のものである。  \n\n【語法・注意】`principal` は元の基礎額、`interest` は借入の対価または貸付・投資から生じる追加額であり、反意語ではなく関連する別の金額構成要素である。信託では `principal` が財産本体、`income` がそこから生じる収益を指す。`repay the principal` では `principal` 自体が目的語の名詞になる。日本語の「元利金」は `principal and interest` であり、`principal interest` とはしない。  \n\n【類義語】\n\n・capital  \n定義: 投資・事業に用いられる資金または資産。  \n頻度: 〈9/10〉  \n違い: `capital` は事業資金・生産資産まで広く表す。`principal` は特定の貸付・借入・投資で利息や収益の基礎となる元の額を指す。  \n例: The company raised additional capital from investors.  \n訳: その会社は投資家から追加資金を調達した。  \n\n5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者\n\n【日本語訳・定義】別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。  \n\n【頻度】〈5/10〉  \n\n【レジスター/領域】法律、保険、不動産、商取引。日常語として人を「依頼主」と呼ぶだけなら `client` が自然な場合も多い。  \n\n【文法パターン】`a principal-agent relationship`＝本人・代理人関係／`act on behalf of the principal`＝本人を代理して行動する  \n\n【コロケーション】\n\n・`a principal-agent relationship`  \n用途: 権限を与える本人と、そのために行動する代理人との関係を表す。  \n例: The contract created a principal-agent relationship between the owner and the broker.  \n訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。  \n\n・`act on behalf of the principal`  \n用途: 代理人が本人を代理して行動することを表す。  \n例: The agent may sign the document on behalf of the principal.  \n訳: 代理人は本人を代理してその書類に署名できる。  \n\n【語法・注意】法律用語の `principal` は、`agent` に権限を与える側を表す関係上の役割名である。`principal` が権限の源となり、`agent` は本人のためにその権限の範囲で行動する。  \n\n【類義語】\n\n・mandator  \n定義: 他人に委任・代理の権限を与える者。  \n頻度: 〈2/10〉  \n違い: 特定の法体系や専門文脈で使われる低頻度語である。  \n例: The mandator may revoke the mandate subject to the agreement.  \n訳: 委任者は、契約の定めに従い、委任を撤回できる。  \n\n【反意語】\n\n・agent  \n定義: 他者から権限を与えられ、その者のために行動する人または法人。  \n頻度: 〈8/10〉  \n違い: 同じ代理関係の役割軸で、`principal` が権限を与える側、`agent` が与えられた権限で行動する側である。  \n例: The agent negotiated the sale for the owner.  \n訳: 代理人は所有者のために売却交渉を行った。  \n\n6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者\n\n【日本語訳・定義】刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】刑事法の専門語。犯罪に関するこの語義は法域によって分類法が異なる。  \n\n【文法パターン】`the principal + be + directly responsible for 〈犯罪〉`  \n\n【コロケーション】\n\n・`the principal + be + directly responsible for 〈犯罪〉`  \n用途: 適用法上、犯罪について直接責任を負う者を表す。  \n例: Under the statute, the principal is directly responsible for the crime.  \n訳: その制定法の下で、当該 `principal` はその犯罪について直接責任を負う。  \n\n【語法・注意】刑事法の `principal` は適用される法的分類に従う役割名で、`accessory` と対比される。債務・保証関係の第一次的責任者は別の語義7である。  \n\n【類義語】\n\n・perpetrator  \n定義: 犯罪・不正行為を実際に行った者。  \n頻度: 〈6/10〉  \n違い: `perpetrator` は実行者に焦点を置く一般的な法律・報道語。`principal` は適用される法的分類によって、実行者以外の一定の関与者を含む場合がある。  \n例: Police are still trying to identify the perpetrator.  \n訳: 警察は今も犯人の特定を進めている。  \n\n7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者\n\n【日本語訳・定義】債務・保証の文脈で、保証人などの二次的責任者と対比され、義務について第一次的に責任を負う人または法人。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】債務法・保証法の専門語。  \n\n【文法パターン】`the principal + be + primarily liable for 〈債務・義務〉`／`the principal + be + distinct from 〈surety/guarantor〉 with secondary liability`  \n\n【コロケーション】\n\n・`the principal + be + primarily liable for 〈債務・義務〉`  \n用途: 主たる当事者が義務について第一次的責任を負うことを示す。  \n例: The principal is primarily liable for the debt.  \n訳: 主たる債務者はその債務について第一次的責任を負う。  \n\n・`the principal + be + distinct from 〈surety/guarantor〉 with secondary liability`  \n用途: 第一次的責任者を、二次的責任を負う保証人と区別する。  \n例: The principal is distinct from the surety, who has secondary liability.  \n訳: 主たる債務者は、二次的責任を負う保証人とは別の当事者である。  \n\n【語法・注意】この語義では、`principal` は `be liable as principal` のように人・法人を指す名詞である。金額を指す語義4の「元金」とは区別する。  \n\n【類義語】\n\n・obligor  \n定義: 契約や法律上の義務を負う者。  \n頻度: 〈3/10〉  \n違い: `obligor` は義務を負う者を広く表す。`principal` は保証人などと対比して、その義務について第一次的に責任を負う側を示す。  \n例: The obligor must perform the duty by the stated date.  \n訳: 義務者は定められた日までに義務を履行しなければならない。  \n\n・debtor  \n定義: 金銭その他の債務を負う者。  \n頻度: 〈6/10〉  \n違い: `debtor` は債務者一般を指す。`principal` は保証関係で第一次的責任を負う当事者という役割を強調する。  \n例: The debtor made the payment on time.  \n訳: 債務者は期限どおりに支払った。  \n\n【反意語】\n\n・surety  \n定義: 主たる債務者が履行しない場合に責任を負う保証人。  \n頻度: 〈3/10〉  \n違い: 責任順位の軸で、`principal` が第一次的に責任を負うのに対し、`surety` は他人の義務を担保する側に立つ。  \n例: The surety paid after the borrower defaulted.  \n訳: 借り手が債務不履行となった後、保証人が支払った。  ",
  "_output_metadata": {
    "schema_version": "final_review_v2",
    "stage": "final_review",
    "run_id": "blind-principal-20260908T073126Z-740135b4",
    "context_id": "blind-principal-context-20260908T073126Z-740135b4",
    "input_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
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
    "blind_output_sha256": "5dda7c1f89ee9dcffa51e9270bff86e573b740a2d8124fc4a6a53090819fca40"
  },
  "pass_findings": {
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-principal-20260908T073126Z-740135b4",
    "context_id": "normal-principal-context-20260908T073126Z-740135b4",
    "input_body_sha256": "1a52681200f8151d905196cfb05550ddc423af07e1d4fee6da8e752e0a523528",
    "prompt_sha256": "5178f5a14a9525317811a34e6cd307108436f4babc1299fcd2eb9031f28ba737",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-09-08T07:58:14.299583+00:00",
    "pass_outputs": [
      {
        "pass_id": "translation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "principal-cycle3-translation-agent"
        },
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "sense-structure",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "/root/principal_cycle3_sense"
        },
        "findings": []
      },
      {
        "pass_id": "frame-relation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "/root/principal_cycle3_frame"
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "1a52681200f8151d905196cfb05550ddc423af07e1d4fee6da8e752e0a523528",
          "blind_request_sha256": "80a2ee136abfaee140b9490e0e3e6a8d92ccbe9598c8a91b5d86fd356f3f16e5",
          "recorded_at": "2026-09-08T16:49:11+09:00",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "/root/principal_cycle3_frame"
          },
          "axes": [
            {
              "item_id": "ant-c450e878c609",
              "axis": "重要度",
              "relation_type": "程度",
              "reason": ""
            },
            {
              "item_id": "ant-633fad4cce44",
              "axis": "責任順位",
              "relation_type": "補完",
              "reason": ""
            },
            {
              "item_id": "ant-65d902381b24",
              "axis": "重要度",
              "relation_type": "程度",
              "reason": ""
            },
            {
              "item_id": "ant-ab226152f491",
              "axis": "授権方向",
              "relation_type": "方向",
              "reason": ""
            }
          ]
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "1a52681200f8151d905196cfb05550ddc423af07e1d4fee6da8e752e0a523528",
          "stage2_request_sha256": "3d255cea4e86acc9414dd304df8796f4f9993d5fb146af43c9f3b58a412d20b7",
          "blind_record_sha256": "0b04735e9f3fc6e9ad0c98f7aa3d945f2e6d722c904e0c3a55b1d5841e7269bf",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "/root/principal_cycle3_frame"
          },
          "adjudications": [
            {
              "item_id": "ant-c450e878c609",
              "flags": [],
              "rationale": "重要度は当該語義の定義に明示され、principal と secondary はその高低を表す程度対立であり、違い行も対立の成立を否定・限定していない。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-65d902381b24",
              "flags": [],
              "rationale": "重要度は当該語義から直接導け、principal と minor は重要性・影響の大小を表す程度対立であり、違い行に自己否定はない。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-ab226152f491",
              "flags": [],
              "rationale": "授権方向は本人が権限を与え代理人がその権限で行動するという当該語義そのものから導け、両者は同一代理関係における方向対立であり、違い行もその対立を明確にしている。",
              "suggested_direction": null,
              "f4_severity": null
            },
            {
              "item_id": "ant-633fad4cce44",
              "flags": [],
              "rationale": "責任順位は第一次的責任者という当該語義から導け、保証関係で principal と surety は第一次責任側と二次的保証側という補完的役割を表し、違い行に対立の不成立を示す記述はない。",
              "suggested_direction": null,
              "f4_severity": null
            }
          ],
          "frame_findings": [],
          "unrouted_observations": []
        },
        "aligned_at": "2026-09-08T08:02:42.902808+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "principal_cycle3_example"
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "pass_id": "example-attribution",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "principal_cycle3_example"
          },
          "recorded_at": "2026-09-08T07:50:26Z",
          "input_body_sha256": "1a52681200f8151d905196cfb05550ddc423af07e1d4fee6da8e752e0a523528",
          "blind_request_sha256": "1b561aa1db1fa8f994f71c47943a24d938458742b0ab0a4ee80feea3a2fcf069",
          "attributions": [
            {
              "example_id": "ex-b7770efe14b0",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:007"
              ],
              "discriminating_terms": [
                "liable as principal for the debt",
                "guarantor is only secondarily liable"
              ],
              "rationale": "\"liable as principal for the debt\" が第一次的な債務責任を表し、\"guarantor is only secondarily liable\" が保証人との責任順位の対比を明示するため sense:007。一見近い代理関係の sense:005 では、本人と代理人の権限関係であって保証人との第一次・第二次責任の対比にならない。"
            },
            {
              "example_id": "ex-ff8a9f3de0b3",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "principal of the college",
                "welcomed the new students"
              ],
              "rationale": "\"principal of the college\" は教育機関の長を指し、\"welcomed the new students\" もその人物役割として自然なので sense:002。主要性を表す形容詞 sense:001 なら principal は名詞 college を前置修飾するはずで、ここでの \"The principal of\" という可算名詞構文にはならない。"
            },
            {
              "example_id": "ex-ba43c2e93bf7",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "principal architects of the reform",
                "one of the principal architects"
              ],
              "rationale": "\"principal architects of the reform\" では principal が architects の重要度を限定する形容詞なので sense:001。組織上の責任者を表す名詞 sense:002 なら \"a principal\" のように principal 自体が名詞となり、\"one of the principal architects\" の修飾構造にはならない。"
            },
            {
              "example_id": "ex-8588c3003173",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "principal cause of the failure",
                "identified corrosion as the principal cause"
              ],
              "rationale": "\"principal cause of the failure\" は複数の原因候補中で最重要の原因を示す形容詞用法で sense:001。犯罪関与者の名詞 sense:006 なら principal は人を指すが、ここでは \"cause\" を直接修飾しておりその解釈は成立しない。"
            },
            {
              "example_id": "ex-fb9a270c2e10",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:006"
              ],
              "discriminating_terms": [
                "knowingly assists the offense",
                "treats a person",
                "as a principal"
              ],
              "rationale": "\"knowingly assists the offense\" という犯罪関与を根拠に制定法が人を \"as a principal\" と分類しているため sense:006。代理関係の本人 sense:005 なら agent に権限を与える関係が必要で、犯罪への援助を直接の分類根拠にはしない。"
            },
            {
              "example_id": "ex-d8b6748e2197",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "school principal",
                "met with parents"
              ],
              "rationale": "\"school principal\" は学校の管理責任者を表し、\"met with parents\" もその人物の行為なので sense:002。芸術上の主要演者 sense:003 なら ballet company や orchestra の役割を示す必要があり、school の役職名としては成立しない。"
            },
            {
              "example_id": "ex-d1bb2ba25937",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "protect the principal",
                "generating modest returns"
              ],
              "rationale": "\"protect the principal\" と \"generating modest returns\" の対比は、運用収益と区別される投資元本を示すので sense:004。主要人物の名詞 sense:002 では protect の対象が人になり得ても、元本から returns を生むこの対比を説明できない。"
            },
            {
              "example_id": "ex-723f34fae887",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:007"
              ],
              "discriminating_terms": [
                "duties of the principal and the surety",
                "principal and the surety"
              ],
              "rationale": "\"duties of the principal and the surety\" は主たる義務者と保証人の義務を並置する保証法上の関係なので sense:007。代理関係の sense:005 で通常対になるのは principal と agent であり、\"principal and the surety\" という対比にはならない。"
            },
            {
              "example_id": "ex-ae5337089da5",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "performs as a principal",
                "with the ballet company"
              ],
              "rationale": "\"performs as a principal\" が舞台上の役割を表し、\"with the ballet company\" がその役割をバレエ団に結び付けるため sense:003。組織の上級責任者 sense:002 なら performs as ではなく管理職として works as などが自然で、この演者フレームには合わない。"
            },
            {
              "example_id": "ex-e51fd1fbad90",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "payments",
                "pay down the principal",
                "faster"
              ],
              "rationale": "\"payments\" によって \"pay down the principal\" するという減額構造は債務元金を指す sense:004。主たる債務者 sense:007 は人・法人であり、支払いによってその principal 自体を pay down するとは言えない。"
            },
            {
              "example_id": "ex-4d0ac6bd9b02",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:006"
              ],
              "discriminating_terms": [
                "court identified him",
                "as a principal in the crime",
                "in the crime"
              ],
              "rationale": "\"court identified him\" と \"as a principal in the crime\" は、犯罪への関与に基づく法的分類を明示するので sense:006。組織の責任者 sense:002 なら principal of/at an organization の形が自然で、\"in the crime\" を補部として犯罪者区分を表せない。"
            },
            {
              "example_id": "ex-c519f856e58d",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "college principal",
                "addressed the graduating class"
              ],
              "rationale": "\"college principal\" はカレッジの管理責任者で、\"addressed the graduating class\" はその役職者の行為として読むため sense:002。形容詞 sense:001 なら principal が別の名詞を修飾する必要があるが、ここでは principal 自体が addressed の主語である。"
            },
            {
              "example_id": "ex-0d27f4910c52",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "a principal at an architecture firm",
                "at an architecture firm"
              ],
              "rationale": "\"a principal at an architecture firm\" では可算名詞 principal が組織内の上級責任者という人物役割を表すため sense:002。形容詞 sense:001 なら a principal の後に被修飾名詞が必要であり、金融元本 sense:004 も人を主語とする \"She is a principal at\" には合わない。"
            },
            {
              "example_id": "ex-20560a47be0c",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "trust document",
                "distinguishes principal from income",
                "from income"
              ],
              "rationale": "\"trust document\" が \"distinguishes principal from income\" と定めるのは、信託財産の元本と収益の法的区別なので sense:004。重要人物 sense:002 なら income と対置される財産区分にならず、distinguish A from B の同種項目関係も崩れる。"
            },
            {
              "example_id": "ex-9076d82301ea",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "principal reason for the delay",
                "was a shortage of parts"
              ],
              "rationale": "\"principal reason for the delay\" は理由群のうち中心的な理由を示す形容詞用法で sense:001。人を指す名詞 sense:002 なら principal は reason を修飾できず、\"was a shortage of parts\" という理由内容を受ける構文にもならない。"
            },
            {
              "example_id": "ex-44f5af1e0087",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "principal-agent relationship",
                "between the owner and the broker"
              ],
              "rationale": "\"principal-agent relationship\" が本人と代理人の法的関係を名称として明示し、\"between the owner and the broker\" がその二者を具体化するため sense:005。主たる債務者 sense:007 なら counterpart は surety/guarantor であり、agent との権限関係とはならない。"
            },
            {
              "example_id": "ex-3ffcd59d349e",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "a principal source of income",
                "principal source"
              ],
              "rationale": "\"a principal source of income\" では principal が source の重要性を評価する形容詞なので sense:001。金融上の元本 sense:004 は principal 自体が名詞で income と区別されるが、この文では principal が source を修飾し、income の源を述べている。"
            },
            {
              "example_id": "ex-9c64883c678d",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "The agent",
                "on behalf of the principal",
                "may sign the document"
              ],
              "rationale": "\"The agent\" が \"on behalf of the principal\" 書類に署名するという代理権の行使なので sense:005。主たる債務者 sense:007 では agent が本人のために行為する関係を表さず、\"on behalf of\" の権限源を説明できない。"
            },
            {
              "example_id": "ex-94f8b9ecab35",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "borrower",
                "repaying principal",
                "next year"
              ],
              "rationale": "\"borrower\" が \"repaying principal\" する対象は借入元金なので sense:004。主たる債務者 sense:007 なら principal は返済する人側を指し、borrower が principal そのものを repay する目的語関係にはならない。"
            },
            {
              "example_id": "ex-fb3e273ffd49",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "concert program lists her",
                "one of the orchestra's principals",
                "orchestra's principals"
              ],
              "rationale": "\"concert program lists her\" と \"one of the orchestra's principals\" はオーケストラ内の首席奏者という確立した演奏役割を示すため sense:003。組織の一般的責任者 sense:002 では orchestra の所有格複数 principals が演奏会プログラムに演者として載る関係を説明できない。"
            },
            {
              "example_id": "ex-bbbad2c23b4a",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "monthly payment",
                "both principal and interest",
                "interest"
              ],
              "rationale": "\"monthly payment\" が \"both principal and interest\" を含むという内訳は、利息と区別される元金 sense:004 を直接示す。主たる債務者 sense:007 は人・法人なので interest と並列する支払内訳にはなれない。"
            },
            {
              "example_id": "ex-1cba258f3e43",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:007"
              ],
              "discriminating_terms": [
                "The guarantee",
                "obligation of the principal",
                "does not replace"
              ],
              "rationale": "\"The guarantee\" が \"does not replace\" する対象として \"obligation of the principal\" が置かれ、保証人に対する第一次的義務者を示すので sense:007。代理法の本人 sense:005 にも obligation はあり得るが、保証が主債務を代替しないという principal-guarantor の責任構造は sense:005 では成立しない。"
            }
          ]
        },
        "aligned_at": "2026-09-08T07:58:14.285050+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "qualification",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "/root/principal_cycle3_qualification"
        },
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "pronunciation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "principal-cycle3-pronunciation"
        },
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "evidence",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5.6-sol",
          "ingested_by": "human",
          "agent_id": "/root/principal_cycle3_evidence"
        },
        "findings": [
          {
            "id": "normal-evidence-001",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "usage_notes",
              "line_start": 72,
              "line_end": 72,
              "exact_quote": "`principal` と `principle` は綴りも意味も異なる。`principal` には形容詞で「最も重要な」を表す用法があり、別に人や金額などを指す名詞用法もある。一方、`principle` は「原理・原則」を表す名詞である。したがって「基本原則」は `basic principle` であり、`basic principal` ではない。"
            },
            "severity": "blocking",
            "rationale": "C-013 links this whole usage note only to F-032 at the Merriam-Webster locator. F-032 directly supports the principle-as-rule versus principal-as-adjective distinction, but its recorded statement and source detail do not directly support the added claim that principal has noun uses for people and amounts, nor do they preserve the specific basic principle/basic principal substitution example. Those noun assertions are supported elsewhere in the inventory (for example C-002 and C-004), but they are not linked to usage_note:001, so the existing link's scope is narrower than the target claim.",
            "evidence_link_ids": [
              "C-013"
            ],
            "suggested_direction": "Limit the note to the distinction directly recorded by F-032, or bind the noun-use clauses to the relevant person and finance claim units and add direct support for the specific substitution example."
          },
          {
            "id": "normal-evidence-002",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 128,
              "line_end": 128,
              "exact_quote": "【文法パターン】組織上の地位は `a principal at 〈企業・専門組織〉`。教育上の役職は `the principal of 〈限定詞を含む学校・教育機関の名詞句〉`／`a school principal`／`a college principal`。"
            },
            "severity": "blocking",
            "rationale": "C-002 maps F-002, F-003, F-014, and F-017 to grammar_pattern:002. At the Merriam-Webster, Cambridge, and Collins locators, the fixed fact statements support the authority/person sense, the school-head title, and the England-college qualification. None of the recorded source details directly attests the promised business at-frame or establishes all three education constructions as grammatical frames. A lexical definition cannot by itself support these exact complements and compounds.",
            "evidence_link_ids": [
              "C-002"
            ],
            "suggested_direction": "Retain only constructions directly attested in the fixed facts, or add fixed fact records with locators and passages that explicitly show each proposed frame."
          },
          {
            "id": "normal-evidence-003",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 171,
              "line_end": 171,
              "exact_quote": "【文法パターン】舞台芸術の役職は `perform/serve as a principal with 〈舞台芸術団体〉`。オーケストラの役職は `one of 〈オーケストラを表す所有格〉 principals`。"
            },
            "severity": "blocking",
            "rationale": "C-003 links grammar_pattern:003 to F-007 and F-018. The Merriam-Webster and Collins facts directly establish the leading-performer and orchestral-section-player senses, but their recorded source details do not attest perform/serve as ... with or the possessive one-of-principals construction. The evidence therefore supports the role meaning, not the complete syntactic frames stated here.",
            "evidence_link_ids": [
              "C-003"
            ],
            "suggested_direction": "Replace the patterns with constructions explicitly present at the fixed locators, or hold the frame claims until direct construction evidence is recorded."
          },
          {
            "id": "normal-evidence-004",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 204,
              "line_end": 204,
              "exact_quote": "【文法パターン】金融では `principal and interest`／`pay down, protect, or repay + (the) principal`。信託法では `distinguish + principal + from + income`。"
            },
            "severity": "blocking",
            "rationale": "C-004 and C-005 map the finance and trust facts to grammar_pattern:004. The facts directly support the principal-versus-interest/income contrasts and F-024 supports repayment reducing the obligation. However, none of F-008, F-015, F-019, F-024, F-025, or F-027 at the listed dictionary, Wex, and Investor.gov locators records protect the principal as a supported collocation or validates the bundled verb-frame pay down, protect, or repay + (the) principal. The target is broader than the linked evidence even though its underlying senses are supported.",
            "evidence_link_ids": [
              "C-004",
              "C-005"
            ],
            "suggested_direction": "Remove protect from the bundled frame or supply a direct fixed fact for that collocation; keep the remaining patterns only to the extent their exact construction is attested."
          },
          {
            "id": "normal-evidence-005",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 294,
              "line_end": 294,
              "exact_quote": "【文法パターン】`a principal in 〈犯罪を表す名詞句〉`／`treat 〈人〉 as a principal`"
            },
            "severity": "blocking",
            "rationale": "C-007 links F-005 and F-021 to grammar_pattern:006. Those fixed Merriam-Webster and Collins facts support the jurisdiction-sensitive criminal-participant classification and the accessory contrast, but their recorded passages do not directly attest both complete syntactic frames. Treating the legal classification as evidence for the exact in-complement and treat-as constructions exceeds the recorded support.",
            "evidence_link_ids": [
              "C-007"
            ],
            "suggested_direction": "State only the supported legal sense, or add locator-specific facts that directly attest each construction before presenting them as grammar patterns."
          },
          {
            "id": "normal-evidence-006",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 327,
              "line_end": 327,
              "exact_quote": "【文法パターン】`be/remain liable as principal for 〈債務・義務〉`／`the obligation of the principal`／`the principal and the surety`"
            },
            "severity": "blocking",
            "rationale": "C-008 maps F-006, F-022, and F-026 to grammar_pattern:007. These facts at Merriam-Webster, Collins, and Wex directly support primary liability and the contrast with a surety or guarantor, but the fixed source details do not attest the full be/remain liable as principal for frame or all two noun-phrase patterns. The responsibility contrast supports the definition, not every specific construction bundled here.",
            "evidence_link_ids": [
              "C-008"
            ],
            "suggested_direction": "Narrow this section to phrases directly attested by the fixed evidence, or add fact records with exact passages for the proposed liability constructions."
          }
        ]
      }
    ],
    "checker_reviewers": {
      "translation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "principal-cycle3-translation-agent"
      },
      "sense-structure": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "/root/principal_cycle3_sense"
      },
      "frame-relation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "/root/principal_cycle3_frame"
      },
      "example-attribution": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "principal_cycle3_example"
      },
      "qualification": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "/root/principal_cycle3_qualification"
      },
      "pronunciation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "principal-cycle3-pronunciation"
      },
      "evidence": {
        "mode": "handoff",
        "declared_model": "gpt-5.6-sol",
        "ingested_by": "human",
        "agent_id": "/root/principal_cycle3_evidence"
      }
    },
    "independent_candidates": [],
    "summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency."
  },
  "cold_review": {
    "summary": "記事全体を、語義の境界・用法上の一般化・各説明間の整合性・断定に対する反例の観点から確認した。形容詞の相対的重要性、組織・教育・舞台芸術の役職、金融・信託、代理法、刑事法、債務・保証法の各語義は区別され、適用範囲の限定も示されている。例文と訳にも本文の説明を損なう矛盾は認められず、問題候補なし。",
    "findings": [],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "/root/principal_cycle3_cold"
    },
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-principal-20260908T073126Z-740135b4",
    "context_id": "cold-principal-context-20260908T073126Z-740135b4",
    "input_body_sha256": "1a52681200f8151d905196cfb05550ddc423af07e1d4fee6da8e752e0a523528",
    "prompt_sha256": "25c298d1a4305746147791bd442cd725a92737c8f0802b992ea88e5c6ff76a5d",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-08T08:09:22.635150+00:00"
  },
  "final_blind": {
    "provisional_decision": "pass",
    "independent_candidates": [
      {
        "id": "FB-C001",
        "surface_form": "principal",
        "frame": "principal + noun",
        "meaning": "複数の候補の中で重要性・中心性・順位が第一級の、主要な",
        "disposition": "included",
        "rationale": "principal + noun は形容詞の中心用法であり、理由・原因・供給源・人物などを重要度の軸で主要と位置づける記事の語義1に明確に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A001",
            "statement": "形容詞 principal は原則として同じ集合内での相対的重要性または中心性を表す。",
            "polarity": "must_hold",
            "scope": "形容詞の定義、文法パターン、コロケーション、類義語比較"
          },
          {
            "id": "FB-A002",
            "statement": "形容詞 principal を単なる時間順の『最初の』と同一視してはならない。",
            "polarity": "must_not_hold",
            "scope": "形容詞の定義と語法"
          }
        ]
      },
      {
        "id": "FB-C002",
        "surface_form": "a principal",
        "frame": "a principal with controlling authority",
        "meaning": "組織で支配的権限または主導的地位を持つ人物",
        "disposition": "included",
        "rationale": "a principal with controlling authority は一般人物用法を権限の有無で限定しており、単なる著名人へ不当に広げず記事の語義2に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A003",
            "statement": "人物名詞 principal の一般用法には、その組織内での権限または主導的地位が必要である。",
            "polarity": "must_hold",
            "scope": "一般人物用法の定義、用例、注意"
          },
          {
            "id": "FB-A004",
            "statement": "人物名詞 principal を文脈上の地位を問わない一般的な『重要人物』として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "一般人物用法の包含・除外境界"
          }
        ]
      },
      {
        "id": "FB-C003",
        "surface_form": "the principal",
        "frame": "the principal + be + in charge of a school or educational institution",
        "meaning": "学校・カレッジなど教育機関を管理する長",
        "disposition": "included",
        "rationale": "the principal + be + in charge of a school or educational institution は一般の権限者より狭い教育上の役職フレームで、地域・制度差の注意を伴って記事の語義2に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A005",
            "statement": "教育用法の principal は教育機関を管理する長という制度上の役職を表す。",
            "polarity": "must_hold",
            "scope": "教育用法の定義、レジスター、文法パターン"
          },
          {
            "id": "FB-A006",
            "statement": "あらゆる地域・制度の日本語『校長』を無条件に principal と訳せると一般化してはならない。",
            "polarity": "must_not_hold",
            "scope": "教育用法の地域・制度上の限定"
          }
        ]
      },
      {
        "id": "FB-C004",
        "surface_form": "a principal",
        "frame": "performer + be + a principal",
        "meaning": "舞台芸術団体で主要な役を担う演者",
        "disposition": "included",
        "rationale": "performer + be + a principal は舞台芸術で確立した役割名としての記事の語義3に含まれ、一般人物用法とは領域で明確に分離されている。",
        "semantic_assertions": [
          {
            "id": "FB-A007",
            "statement": "舞台芸術の名詞 principal は団体内で主要な役を担う演者を指す。",
            "polarity": "must_hold",
            "scope": "舞台芸術用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A008",
            "statement": "舞台芸術の役割名を芸術分野外の重要人物一般へ拡張してはならない。",
            "polarity": "must_not_hold",
            "scope": "舞台芸術用法の除外境界"
          }
        ]
      },
      {
        "id": "FB-C005",
        "surface_form": "the principal",
        "frame": "the principal + be + the first player of an orchestra section",
        "meaning": "オーケストラの一つのセクションを率いる首席奏者",
        "disposition": "included",
        "rationale": "the principal + be + the first player of an orchestra section は舞台演者とは異なるオーケストラの職務フレームであり、記事の語義3の内部で個別に説明されている。",
        "semantic_assertions": [
          {
            "id": "FB-A009",
            "statement": "オーケストラ用法の principal は特定セクションの第一奏者または首席という役割を表す。",
            "polarity": "must_hold",
            "scope": "オーケストラ用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A010",
            "statement": "オーケストラの principal を団体全体の管理責任者という意味に取り違えてはならない。",
            "polarity": "must_not_hold",
            "scope": "オーケストラ用法の意味役割"
          }
        ]
      },
      {
        "id": "FB-C006",
        "surface_form": "principal",
        "frame": "principal + be + distinct from interest",
        "meaning": "貸付・借入・投資で利息や収益の基礎となる元金または元本",
        "disposition": "included",
        "rationale": "principal + be + distinct from interest は金融上の金額構成要素を区別する中心フレームで、記事の語義4に元金への返済効果も含めて説明されている。",
        "semantic_assertions": [
          {
            "id": "FB-A011",
            "statement": "金融用法の principal は利息・利益・収益の計算または発生の基礎となる資本額を指す。",
            "polarity": "must_hold",
            "scope": "金融用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A012",
            "statement": "principal と interest を反意語として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "金融用法の語法と関係分類"
          }
        ]
      },
      {
        "id": "FB-C007",
        "surface_form": "trust principal",
        "frame": "trust principal + be + distinct from income",
        "meaning": "信託で収益と区別される財産本体または corpus",
        "disposition": "included",
        "rationale": "trust principal + be + distinct from income は金融元金とは別の信託法上の対象を明示し、記事の語義4に専門的限定とともに含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A013",
            "statement": "信託用法の principal は信託財産の本体を指し、そこから生じる income と区別される。",
            "polarity": "must_hold",
            "scope": "信託法用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A014",
            "statement": "trust principal を信託から発生する収益そのものとして扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "信託法用法の作用方向と除外境界"
          }
        ]
      },
      {
        "id": "FB-C008",
        "surface_form": "principal",
        "frame": "agent + act on behalf of the principal",
        "meaning": "代理人に自分のために行動する権限を与える本人または法人",
        "disposition": "included",
        "rationale": "agent + act on behalf of the principal は代理関係の役割方向を固定し、権限の源である本人を受権者の agent と混同せず記事の語義5に含めている。",
        "semantic_assertions": [
          {
            "id": "FB-A015",
            "statement": "代理法上の principal は agent がその者のために行動する側であり、代理権の源となる。",
            "polarity": "must_hold",
            "scope": "代理関係用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A016",
            "statement": "代理関係で principal と agent の権限付与側・行動側を逆転させてはならない。",
            "polarity": "must_not_hold",
            "scope": "代理関係の役割軸と反意関係"
          }
        ]
      },
      {
        "id": "FB-C009",
        "surface_form": "principal",
        "frame": "act or trade as principal rather than as agent",
        "meaning": "取引で他人の代理ではなく自己の計算・責任で当事者として行動する",
        "disposition": "excluded",
        "rationale": "act or trade as principal rather than as agent は代理人との対比から生じる専門的な取引上の拡張であり、独立した主要語義として追加しなくても代理関係の役割境界から理解できるため除外できる。",
        "semantic_assertions": [
          {
            "id": "FB-A017",
            "statement": "自己勘定取引で as principal と言う場合は、他人の agent としてではなく自己の計算・責任で行動する対比が中心となる。",
            "polarity": "must_hold",
            "scope": "取引上の文脈的拡張を説明する場合"
          },
          {
            "id": "FB-A018",
            "statement": "この取引表現を教育機関の長や元金の語義へ帰属させてはならない。",
            "polarity": "must_not_hold",
            "scope": "取引表現の語義境界"
          }
        ]
      },
      {
        "id": "FB-C010",
        "surface_form": "the principal",
        "frame": "the principal + be + directly responsible for a crime under applicable law",
        "meaning": "適用法の分類により犯罪について直接の刑事責任を負う関与者",
        "disposition": "included",
        "rationale": "the principal + be + directly responsible for a crime under applicable law は犯罪の物理的実行者だけに絶対化せず、法域依存の分類として記事の語義6に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A019",
            "statement": "刑事法上の principal の範囲は適用法の分類に従い、犯罪への一定の関与による直接責任を表す。",
            "polarity": "must_hold",
            "scope": "刑事法用法の定義、レジスター、注意"
          },
          {
            "id": "FB-A020",
            "statement": "すべての法域で principal が物理的実行者だけを指すと絶対化してはならない。",
            "polarity": "must_not_hold",
            "scope": "刑事法用法の一般化範囲"
          }
        ]
      },
      {
        "id": "FB-C011",
        "surface_form": "the principal",
        "frame": "the principal + be + primarily liable for a debt or obligation",
        "meaning": "保証人などと対比して義務に第一次的責任を負う主たる債務者・義務者",
        "disposition": "included",
        "rationale": "the principal + be + primarily liable for a debt or obligation は責任順位を表す債務・保証法の役割であり、金額を指す元金用法と分離して記事の語義7に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A021",
            "statement": "債務・保証法上の principal は当該義務について第一次的責任を負う者を指す。",
            "polarity": "must_hold",
            "scope": "債務・保証法用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A022",
            "statement": "第一次的責任者を二次的責任を負う surety または guarantor と同一視してはならない。",
            "polarity": "must_not_hold",
            "scope": "債務・保証関係の責任順位軸"
          }
        ]
      },
      {
        "id": "FB-C012",
        "surface_form": "principally",
        "frame": "principally + verb, adjective, or clause",
        "meaning": "主として、主にという副詞派生",
        "disposition": "included",
        "rationale": "principally + verb, adjective, or clause は principal の重要性中心から規則的に派生する副詞であり、記事の語形成欄に principally として含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A023",
            "statement": "principally は『主として、主に』という割合または中心性を表す副詞派生である。",
            "polarity": "must_hold",
            "scope": "語形成欄"
          }
        ]
      },
      {
        "id": "FB-C013",
        "surface_form": "principalship",
        "frame": "the principalship of an institution",
        "meaning": "principal の地位・職、特に教育機関の長の職",
        "disposition": "included",
        "rationale": "the principalship of an institution は人物を表す principal から地位・職を作る規則的な名詞派生であり、記事の語形成欄に principalship として含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A024",
            "statement": "principalship は principal の役職またはその在職を表す名詞派生である。",
            "polarity": "must_hold",
            "scope": "語形成欄"
          }
        ]
      },
      {
        "id": "FB-C014",
        "surface_form": "principal-agent relationship",
        "frame": "a principal-agent relationship between principal and agent",
        "meaning": "本人と代理人の権限・行動関係を表す法律上の複合表現",
        "disposition": "included",
        "rationale": "a principal-agent relationship between principal and agent は語義5の役割対立を複合語に固定した表現で、記事の語形成欄と代理関係のコロケーションに含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A025",
            "statement": "principal-agent relationship は本人と、その本人のために行動する代理人との関係を表す。",
            "polarity": "must_hold",
            "scope": "語形成欄と代理関係用法"
          },
          {
            "id": "FB-A026",
            "statement": "複合表現内の principal と agent の意味役割を交換してはならない。",
            "polarity": "must_not_hold",
            "scope": "複合表現の構成要素と役割方向"
          }
        ]
      },
      {
        "id": "FB-C015",
        "surface_form": "principal",
        "frame": "principal rafter or another historically lexicalized technical noun",
        "meaning": "建築などで主部材を指す歴史的・限定的な名詞用法",
        "disposition": "excluded",
        "rationale": "principal rafter or another historically lexicalized technical noun は現代一般学習者向け記事で独立語義として必須となるほど中心的ではなく、形容詞 principal の専門的な限定用法として扱えるため除外できる。",
        "semantic_assertions": [
          {
            "id": "FB-A027",
            "statement": "歴史的・分野限定の部材名を扱う場合は、現代一般語の主要名詞用法と区別する。",
            "polarity": "must_hold",
            "scope": "稀な専門用法を追加する場合の語義境界"
          }
        ]
      }
    ],
    "article_findings": [],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "principal_cycle3_final_blind"
    },
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-principal-20260908T073126Z-740135b4",
    "context_id": "blind-principal-context-20260908T073126Z-740135b4",
    "input_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
    "prompt_sha256": "3a481b4b5b1236ff386e148bcacc574570b305e79f5e155e9afcd34091f7785c",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-08T09:40:41.654023+00:00"
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/p/principal.md",
    "body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
    "final_blind_path": "audits/runs/p/principal/20260908T073126Z-740135b4/final_blind.json",
    "final_blind_sha256": "4014793983931bc282a1e2c606b86e047f047d5b1d306673b43ba1ddf85aca65",
    "blind_output_sha256": "5dda7c1f89ee9dcffa51e9270bff86e573b740a2d8124fc4a6a53090819fca40",
    "sealed_at": "2026-09-08T18:44:11.856351+09:00"
  },
  "pre_blind_resolution": {
    "schema_version": "pre_blind_resolution_v1",
    "stage": "pre_blind_resolution",
    "run_id": "20260908T073126Z-740135b4",
    "input_body_sha256": "1a52681200f8151d905196cfb05550ddc423af07e1d4fee6da8e752e0a523528",
    "output_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9",
    "recorded_at": "2026-09-08T08:18:57Z",
    "resolutions": [
      {
        "id": "normal-evidence-001",
        "finding_id": "normal-evidence-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-032 supports the principle-as-rule versus principal-as-most-important-adjective distinction, but not the note's added noun inventory or its basic-principle substitution example.",
        "required_changes": [
          "Limit the spelling note to the distinction directly recorded by F-032."
        ],
        "implemented_changes": [
          "Removed the unbound person-and-amount noun summary and the unsupported basic principle/basic principal example; retained only F-032's rule-noun versus most-important-adjective contrast."
        ],
        "resolved_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9"
      },
      {
        "id": "normal-evidence-002",
        "finding_id": "normal-evidence-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-002 directly supports a person with controlling authority and F-014 directly supports a principal as the person in charge of a school, while the former at/of/compound templates were not recorded in the fixed facts.",
        "required_changes": [
          "Replace the unsupported organization and education templates with complete frames that directly express the fixed authority and school-in-charge facts without narrowing U-002."
        ],
        "implemented_changes": [
          "Replaced the at/of/school-principal/college-principal set with a principal with controlling authority and the principal be in charge of a school, each with a matching example; tightened the C-002 support summaries without changing facts or U-002."
        ],
        "resolved_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9"
      },
      {
        "id": "normal-evidence-003",
        "finding_id": "normal-evidence-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-018 directly records principal dancer and the first player of an orchestral section, but not perform or serve as a principal with an organization or the possessive one-of-principals construction.",
        "required_changes": [
          "Replace the unsupported complements with complete frames grounded in F-018 while preserving both branches of U-003."
        ],
        "implemented_changes": [
          "Replaced the perform/serve-with and possessive frames with a principal dancer and the principal be the first player of an orchestral section, each with a matching example; tightened C-003's F-018 binding without changing facts or U-003."
        ],
        "resolved_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9"
      },
      {
        "id": "normal-evidence-004",
        "finding_id": "normal-evidence-004",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The fixed finance and trust facts directly support an initial invested amount and contrasts with interest or income, but do not support the bundled pay-down, protect, repay, and distinguish verb frames.",
        "required_changes": [
          "Remove the unsupported verb bundle and retain complete frames that state only the directly supported amount and contrast relations."
        ],
        "implemented_changes": [
          "Replaced the former finance/trust construction set with principal as the initial amount invested, principal distinct from interest, and trust principal distinct from income, with matching examples; tightened the C-004/C-005 binding summaries without adding facts."
        ],
        "resolved_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9"
      },
      {
        "id": "normal-evidence-005",
        "finding_id": "normal-evidence-005",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-021 directly supports a principal as a person directly responsible for a crime, but not the former in-complement or treat-as constructions.",
        "required_changes": [
          "Replace both unsupported criminal-law templates with the complete directly-responsible-for-a-crime frame."
        ],
        "implemented_changes": [
          "Replaced the in and treat-as frames and examples with the principal be directly responsible for a crime, and tightened C-007's F-021 binding summary."
        ],
        "resolved_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9"
      },
      {
        "id": "normal-evidence-006",
        "finding_id": "normal-evidence-006",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-006 and F-022 directly support primary liability for an obligation, and F-026 directly supports the distinction from a surety or guarantor with secondary liability; the former liable-as, obligation-of, and coordination templates exceeded those records.",
        "required_changes": [
          "Replace the unsupported liability templates with complete frames directly expressing primary liability and the secondary-liability contrast."
        ],
        "implemented_changes": [
          "Replaced the former three-template set with the principal be primarily liable for an obligation and the principal distinct from a surety or guarantor with secondary liability, with matching examples; tightened C-008's binding summaries without adding facts."
        ],
        "resolved_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9"
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
    "input_body_sha256": "1a52681200f8151d905196cfb05550ddc423af07e1d4fee6da8e752e0a523528",
    "output_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
    "recorded_at": "2026-09-08T08:53:08Z",
    "changed_units": [
      "collocations_examples",
      "frames",
      "usage_notes"
    ],
    "invalidated_passes": [
      "evidence",
      "example-attribution",
      "frame-relation",
      "qualification",
      "sense-structure",
      "translation"
    ],
    "full_recheck": false
  },
  "checker_recheck_manifest": {
    "schema_version": "checker_recheck_manifest_v1",
    "current_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
    "revision_plan_sha256": "db83c0260df30fff92d97a8084d91e8e8350d72a4f0395cb0fe547612f86df79",
    "full_recheck": false,
    "invalidated_passes": [
      "evidence",
      "example-attribution",
      "frame-relation",
      "qualification",
      "translation"
    ],
    "pass_results": [
      {
        "pass_id": "translation",
        "mode": "rechecked",
        "spec_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
        "normalized_input_sha256": "d49a1c8d2572bb7422c8c4f921efbad44e328c94c6815c43a2026565821fc917",
        "source_artifact_sha256": "57ecc194056d5232d24f983cc040bf76672affb170a914f52cb992ce5879100c",
        "output_sha256": "8950e8c3210d823c742d43f9c4e41b71fa052776613e9aa2e3d4384633df0150",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "pass_id": "frame-relation",
        "mode": "rechecked",
        "spec_sha256": "3598ca81a5784639c6b43a0806d0981a985bf4174f424c744aad1dde787bfcef",
        "normalized_input_sha256": "974758b8ad1e7d277a14445e865ced0b8f59e1fff68c8f7ffd09f0488febe458",
        "source_artifact_sha256": "57ecc194056d5232d24f983cc040bf76672affb170a914f52cb992ce5879100c",
        "output_sha256": "70c1f08a0fff66a0868ca537780defe7c34704177ed7a83160c9596bf517ee91",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "pass_id": "example-attribution",
        "mode": "rechecked",
        "spec_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
        "normalized_input_sha256": "82691fc6ce329a30e9ba6bdffcd549e900eb64b27a7ea60b2a24de1e52805031",
        "source_artifact_sha256": "57ecc194056d5232d24f983cc040bf76672affb170a914f52cb992ce5879100c",
        "output_sha256": "475b6fd90bbdb3eef1b79eded9046abccec267c289d3400463e69f2420c8d073",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "pass_id": "qualification",
        "mode": "rechecked",
        "spec_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
        "normalized_input_sha256": "83a943844ec459b731a9e47ac646de3ea482aa121f9f8f3bcb9016649d07efe9",
        "source_artifact_sha256": "57ecc194056d5232d24f983cc040bf76672affb170a914f52cb992ce5879100c",
        "output_sha256": "134c86b5bac03f9981af5eff2fdcbb8bf2f6f714555cf2085135059c333e2fc8",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "pass_id": "evidence",
        "mode": "rechecked",
        "spec_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
        "normalized_input_sha256": "cb2815c6577bd7e932f8e7750254931ddd06fed16a16911ba2be59e4cf2c15bc",
        "source_artifact_sha256": "57ecc194056d5232d24f983cc040bf76672affb170a914f52cb992ce5879100c",
        "output_sha256": "3497a2b02b024e6761c5150fc64b8884d0a55253c95ecc1391fb064405394242",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "validated_on_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "pass_id": "sense-structure",
        "mode": "reused",
        "spec_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
        "normalized_input_sha256": "f97adfcc059c3b2aeece8fe04691e392254c53587b983988be7059e784f91506",
        "source_artifact_sha256": "57ecc194056d5232d24f983cc040bf76672affb170a914f52cb992ce5879100c",
        "output_sha256": "b3afd58b9a7425aa327a91163bed467378a09f2c4baa7e031c616e0f4937dd78",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reused_from_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9",
        "reused_output_path": "audits/runs/p/principal/20260908T073126Z-740135b4/recheck/sense-structure.json",
        "validated_on_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "pass_id": "pronunciation",
        "mode": "reused",
        "spec_sha256": "7e3e94267ac9f917c901c12580b91e570b5989df7adfbf2a39b833478c766d8a",
        "normalized_input_sha256": "ee10ead66e05a1ae925e7c3a11f269975c98c542ec08d1b8f2ad9c2159d3ca70",
        "source_artifact_sha256": "57ecc194056d5232d24f983cc040bf76672affb170a914f52cb992ce5879100c",
        "output_sha256": "bce4a8c4a134031a0ae262f3f1568d48d51732624bd6b8a900c2beaba1ae3054",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reused_from_body_sha256": "6d041d286fafcecc6d481e96bbf12f866ef901403ae837acea66431d99e70cc9",
        "reused_output_path": "audits/runs/p/principal/20260908T073126Z-740135b4/check_passes/pronunciation.json",
        "validated_on_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      }
    ]
  },
  "post_blind_resolution": {
    "schema_version": "post_blind_resolution_v1",
    "resolutions": [],
    "learning_delta": {
      "schema_version": "process_improvement_learning_delta_v2",
      "reviewed": true,
      "items": []
    }
  },
  "post_blind_verification": {
    "schema_version": "post_blind_verification_v1",
    "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
    "checker_recheck_completed": true,
    "final_blind_repeated": true,
    "final_blind_sha256": "4014793983931bc282a1e2c606b86e047f047d5b1d306673b43ba1ddf85aca65"
  },
  "targeted_adjudications": {
    "requests": [],
    "adjudications": []
  },
  "source_inventory": {
    "schema_version": "source_inventory_v2",
    "stage": "source_inventory",
    "headword": "principal",
    "run_id": "source-principal-20260907T233257Z-44da61f2",
    "context_id": "source-principal-context-20260907T233257Z-44da61f2",
    "input_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
    "prompt_sha256": "9b098479af4d18acf89543a2b62c81ed21f99aac429743bed1aa2b0c489864dd",
    "input_artifacts": [
      "headword",
      "source_first_spec"
    ],
    "recorded_at": "2026-09-07T23:55:00Z",
    "source_first_audit": {
      "version": "source_first_audit_v2",
      "profile": "standard",
      "profile_reason": "bounded default profile",
      "limits": {
        "max_sources": 6,
        "max_facts": 48,
        "max_research_rounds": 2,
        "max_post_cold_rechecks": 1,
        "max_final_attempts": 2
      },
      "usage": {
        "sources_used": 6,
        "facts_used": 32,
        "research_rounds_used": 2,
        "post_cold_rechecks_used": 0,
        "final_attempts_used": 0
      },
      "research_status": "complete",
      "stop_reason": "coverage_axes_closed",
      "open_questions": [],
      "inventory_completed_before_article_comparison": true,
      "inventory_completed_at": "2026-09-07T23:55:00Z",
      "article_comparison_started_at": "2026-09-07T23:55:01Z",
      "coverage_axes": [
        {
          "axis": "lexical_senses",
          "status": "covered",
          "source_fact_ids": [
            "F-001",
            "F-002",
            "F-003",
            "F-004",
            "F-005",
            "F-006",
            "F-007",
            "F-008",
            "F-013",
            "F-014",
            "F-015",
            "F-016",
            "F-017",
            "F-018",
            "F-019",
            "F-020",
            "F-021",
            "F-022",
            "F-023",
            "F-024",
            "F-025",
            "F-026",
            "F-027",
            "F-029",
            "F-030",
            "F-031"
          ],
          "notes": "Three independent general dictionaries cover the adjective and the education, leadership, performance, finance, agency, criminal, and obligation noun uses."
        },
        {
          "axis": "part_of_speech_and_frames",
          "status": "covered",
          "source_fact_ids": [
            "F-001",
            "F-002",
            "F-003",
            "F-004",
            "F-008",
            "F-013",
            "F-014",
            "F-015",
            "F-016",
            "F-017",
            "F-018",
            "F-019",
            "F-020",
            "F-023",
            "F-027"
          ],
          "notes": "Adjective premodification, countable person nouns, and mass/count uses of the finance noun are directly represented."
        },
        {
          "axis": "derived_and_related_forms",
          "status": "covered",
          "source_fact_ids": [
            "F-011",
            "F-012",
            "F-032",
            "F-023"
          ],
          "notes": "Principalship and principally are atomic derivative facts; principal-agent and the principal/principle distinction are also represented."
        },
        {
          "axis": "specialist_and_legal_uses",
          "status": "covered",
          "source_fact_ids": [
            "F-004",
            "F-005",
            "F-006",
            "F-008",
            "F-018",
            "F-019",
            "F-020",
            "F-021",
            "F-022",
            "F-023",
            "F-024",
            "F-025",
            "F-026",
            "F-027"
          ],
          "notes": "Cornell Wex and Investor.gov directly cover agency, primary liability, trust corpus, and financial principal; general dictionaries corroborate criminal and performance uses."
        },
        {
          "axis": "register_region_and_frequency",
          "status": "covered",
          "source_fact_ids": [
            "F-001",
            "F-003",
            "F-005",
            "F-006",
            "F-007",
            "F-013",
            "F-014",
            "F-016",
            "F-017",
            "F-018",
            "F-019",
            "F-021",
            "F-022"
          ],
          "notes": "Learner and general dictionaries distinguish ordinary attributive use, regional education titles, professional performance, and specialist legal-financial uses."
        },
        {
          "axis": "pronunciation_and_etymology",
          "status": "covered",
          "source_fact_ids": [
            "F-009",
            "F-010",
            "F-028",
            "F-029",
            "F-030",
            "F-031"
          ],
          "notes": "Merriam-Webster supplies pronunciation and a concise Latin lineage; Etymonline independently documents the adjective, person, education, and money histories."
        }
      ],
      "sources": [
        {
          "id": "S-001",
          "title": "Merriam-Webster — principal",
          "locator": "https://www.merriam-webster.com/dictionary/principal",
          "source_type": "general_dictionary",
          "source_role": "general_lexicon",
          "independence_group": "merriam_webster",
          "facts": [
            {
              "id": "F-001",
              "form": "principal",
              "kind": "lexical_sense",
              "statement": "As an adjective, principal means most important, consequential, or influential.",
              "source_detail": "Adjective sense 1 and examples principal ingredient and principal city."
            },
            {
              "id": "F-002",
              "form": "principal",
              "kind": "lexical_sense",
              "statement": "As a noun, principal can be a person with controlling authority or a leading position.",
              "source_detail": "Noun sense 1 introduces the authority and leading-position group."
            },
            {
              "id": "F-003",
              "form": "principal",
              "kind": "lexical_sense",
              "statement": "Principal can denote the chief executive of an educational institution.",
              "source_detail": "Noun sense 1b directly defines the education-head use."
            },
            {
              "id": "F-004",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "In agency, a principal engages another to act as an agent and is the source of the agent's authority.",
              "source_detail": "Noun sense 1c states both engagement and derivation of authority."
            },
            {
              "id": "F-005",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "In criminal-law usage, principal can denote a chief or actual participant in a crime.",
              "source_detail": "Noun sense 1d and the legal definition distinguish principal participation from accessory status."
            },
            {
              "id": "F-006",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "Principal can denote the person primarily or ultimately liable on a legal obligation.",
              "source_detail": "Noun sense 1e and legal sense 1c contrast primary and secondary liability."
            },
            {
              "id": "F-007",
              "form": "principal",
              "kind": "lexical_sense",
              "statement": "Principal can denote a leading performer or star.",
              "source_detail": "Noun sense 1f directly records the performer use."
            },
            {
              "id": "F-008",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "Financial principal is a capital sum earning interest, due as debt, or used as a fund.",
              "source_detail": "Noun sense 2a and the legal definition distinguish principal from interest."
            },
            {
              "id": "F-009",
              "form": "principal",
              "kind": "pronunciation",
              "statement": "Principal is pronounced /ˈprɪnsəpəl/, with optional phonetic variants represented in the dictionary respelling.",
              "source_detail": "The adjective and noun share the same pronunciation entry."
            },
            {
              "id": "F-010",
              "form": "principal",
              "kind": "etymology",
              "statement": "Principal entered Middle English through Anglo-French from Latin principalis and princeps.",
              "source_detail": "Merriam-Webster word history gives the Anglo-French and Latin lineage."
            },
            {
              "id": "F-011",
              "form": "principalship",
              "kind": "derived_form",
              "statement": "Principalship is listed as a noun derivative of principal.",
              "source_detail": "Merriam-Webster lists principalship as a derived noun."
            },
            {
              "id": "F-012",
              "form": "principally",
              "kind": "derived_form",
              "statement": "Principally is the adverb formed from principal.",
              "source_detail": "Merriam-Webster lists principally directly after the adjective."
            },
            {
              "id": "F-032",
              "form": "principle",
              "kind": "usage_distinction",
              "statement": "Principle is a noun for a fundamental rule or law, whereas principal is also an adjective for most important.",
              "source_detail": "The usage note explicitly warns against confusing principal with principle."
            }
          ]
        },
        {
          "id": "S-002",
          "title": "Cambridge Dictionary — principal",
          "locator": "https://dictionary.cambridge.org/dictionary/english/principal",
          "source_type": "learner_dictionary",
          "source_role": "general_lexicon",
          "independence_group": "cambridge_university_press",
          "facts": [
            {
              "id": "F-013",
              "form": "principal",
              "kind": "lexical_sense",
              "statement": "The adjective principal means first in order of importance.",
              "source_detail": "Cambridge learner definition and examples cover principal aim and principal reason."
            },
            {
              "id": "F-014",
              "form": "principal",
              "kind": "lexical_sense",
              "statement": "The noun principal denotes a person in charge of a school.",
              "source_detail": "Cambridge's school-person noun sense directly records the title."
            },
            {
              "id": "F-015",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "In finance, principal is an amount lent, borrowed, or invested apart from additional money such as interest.",
              "source_detail": "Cambridge's finance noun sense separates the underlying amount from additions."
            }
          ]
        },
        {
          "id": "S-003",
          "title": "Collins English Dictionary — principal",
          "locator": "https://www.collinsdictionary.com/dictionary/english/principal",
          "source_type": "general_dictionary",
          "source_role": "general_lexicon",
          "independence_group": "harpercollins",
          "facts": [
            {
              "id": "F-016",
              "form": "principal",
              "kind": "lexical_sense",
              "statement": "The adjective principal marks the highest or among the highest in rank, authority, importance, or degree.",
              "source_detail": "The American English adjective definition gives the rank-and-importance range."
            },
            {
              "id": "F-017",
              "form": "principal",
              "kind": "register_region",
              "statement": "Principal denotes the head of a school and, especially in England, may denote the head of a college.",
              "source_detail": "Collins distinguishes the school title and the English college use."
            },
            {
              "id": "F-018",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "In performing arts and orchestras, principal can denote a leading performer or the first player of a section.",
              "source_detail": "Collins lists leading actor, principal dancer, and orchestral first-player uses."
            },
            {
              "id": "F-019",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "In finance, principal is a capital sum distinguished from interest or profit and can include bond face value.",
              "source_detail": "The finance senses distinguish debt or investment amount from interest and income."
            },
            {
              "id": "F-020",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "In law, principal can be the person who employs or authorizes an agent.",
              "source_detail": "The law sense directly gives the principal-agent role."
            },
            {
              "id": "F-021",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "In law, principal can be a person directly responsible for a crime, including specified participation under the applicable classification.",
              "source_detail": "The criminal-law sense compares principal with accessory."
            },
            {
              "id": "F-022",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "Principal can be the person primarily liable for an obligation.",
              "source_detail": "The liability sense contrasts the principal with an endorser or similar secondary party."
            }
          ]
        },
        {
          "id": "S-004",
          "title": "Cornell Legal Information Institute Wex — principal",
          "locator": "https://www.law.cornell.edu/wex/principal",
          "source_type": "legal_reference",
          "source_role": "specialist_reference",
          "independence_group": "cornell_lii",
          "facts": [
            {
              "id": "F-023",
              "form": "principal-agent relationship",
              "kind": "specialist_use",
              "statement": "An agency-law principal is a person or entity authorizing an agent to act on its behalf and subject to its control.",
              "source_detail": "Wex states the authority, behalf, and control elements and notes duties owed by the agent."
            },
            {
              "id": "F-024",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "Financial principal is the original debt or investment amount excluding interest, profit, or other earnings.",
              "source_detail": "Wex separates the underlying amount from additions and explains that repayment reduces the obligation."
            },
            {
              "id": "F-025",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "In trust law, principal is the trust corpus or property itself, distinct from its income or earnings.",
              "source_detail": "Wex directly defines the trust-law corpus contrast."
            },
            {
              "id": "F-026",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "Principal can denote the party bearing primary responsibility for an obligation, as distinct from a surety or guarantor with secondary liability.",
              "source_detail": "Wex directly states the primary-versus-secondary liability contrast."
            }
          ]
        },
        {
          "id": "S-005",
          "title": "Investor.gov — Principal",
          "locator": "https://www.investor.gov/introduction-investing/investing-basics/glossary/principal",
          "source_type": "government_finance_glossary",
          "source_role": "specialist_reference",
          "independence_group": "us_sec_investor_gov",
          "facts": [
            {
              "id": "F-027",
              "form": "principal",
              "kind": "specialist_use",
              "statement": "Principal is the total amount borrowed or lent, or the initial amount invested.",
              "source_detail": "Investor.gov gives this concise finance glossary definition."
            }
          ]
        },
        {
          "id": "S-006",
          "title": "Online Etymology Dictionary — principal",
          "locator": "https://www.etymonline.com/word/principal",
          "source_type": "etymology_reference",
          "source_role": "etymology",
          "independence_group": "etymonline",
          "facts": [
            {
              "id": "F-028",
              "form": "principal",
              "kind": "etymology",
              "statement": "The adjective is attested around 1300 from Old French principal and Latin principalis, ultimately connected with princeps, primus, and capere.",
              "source_detail": "Etymonline records the main/chief adjective and analyzes princeps as first plus take."
            },
            {
              "id": "F-029",
              "form": "principal",
              "kind": "etymology",
              "statement": "The noun is attested around 1300 for a chief person or leading representative and also had an early legal use.",
              "source_detail": "Etymonline's noun history records chief-person and law senses from the early period."
            },
            {
              "id": "F-030",
              "form": "principal",
              "kind": "etymology",
              "statement": "The public-school-head use is recorded from 1827, while a college-head use is older.",
              "source_detail": "Etymonline distinguishes the nineteenth-century school use from the mid-fifteenth-century college use."
            },
            {
              "id": "F-031",
              "form": "principal",
              "kind": "etymology",
              "statement": "The main-sum-of-money noun use is recorded from the early fifteenth century.",
              "source_detail": "Etymonline connects this sense with money on which interest is paid."
            }
          ]
        }
      ],
      "source_union": [
        {
          "id": "U-001",
          "source_fact_ids": [
            "F-001",
            "F-013",
            "F-016"
          ],
          "canonical_statement": "The adjective principal marks something first or especially high in importance, rank, or influence.",
          "disposition": "included",
          "rationale": "High-frequency adjective sense supported by three independent dictionaries."
        },
        {
          "id": "U-002",
          "source_fact_ids": [
            "F-002",
            "F-003",
            "F-014",
            "F-017"
          ],
          "canonical_statement": "Principal denotes a person in authority and conventionally the head of specified educational institutions, with regional title differences.",
          "disposition": "included",
          "rationale": "Major person noun and education title supported by current dictionary facts."
        },
        {
          "id": "U-003",
          "source_fact_ids": [
            "F-007",
            "F-018"
          ],
          "canonical_statement": "Principal can denote a leading performer, including a principal artist or orchestral section leader.",
          "disposition": "included",
          "rationale": "Established performing-arts noun use."
        },
        {
          "id": "U-004",
          "source_fact_ids": [
            "F-008",
            "F-015",
            "F-019",
            "F-024",
            "F-027"
          ],
          "canonical_statement": "Financial principal is the underlying debt, loan, or investment amount distinguished from interest, profit, or later earnings.",
          "disposition": "included",
          "rationale": "Major specialist sense corroborated by current general and government-specialist sources."
        },
        {
          "id": "U-005",
          "source_fact_ids": [
            "F-025"
          ],
          "canonical_statement": "Trust principal is the property or corpus distinguished from income earned by it.",
          "disposition": "integrated",
          "rationale": "Direct specialist extension of the finance/property sense."
        },
        {
          "id": "U-006",
          "source_fact_ids": [
            "F-004",
            "F-020",
            "F-023"
          ],
          "canonical_statement": "An agency principal authorizes an agent to act on the principal's behalf and is the source of the agent's authority; the US-law account in Wex also specifies the principal's control.",
          "disposition": "included",
          "rationale": "Important legal and economics role supported by two dictionaries, with the control element qualified to the Wex account."
        },
        {
          "id": "U-007",
          "source_fact_ids": [
            "F-005",
            "F-021"
          ],
          "canonical_statement": "Criminal-law principal denotes a person treated as a primary participant under the applicable legal classification.",
          "disposition": "included",
          "rationale": "Low-frequency but encounterable specialist legal use; scope is explicitly jurisdiction-sensitive."
        },
        {
          "id": "U-008",
          "source_fact_ids": [
            "F-006",
            "F-022",
            "F-026"
          ],
          "canonical_statement": "In obligation law, principal denotes the primarily liable party, contrasted with a secondarily liable surety or guarantor.",
          "disposition": "included",
          "rationale": "Directly supported specialist responsibility contrast."
        },
        {
          "id": "U-009",
          "source_fact_ids": [
            "F-009"
          ],
          "canonical_statement": "The adjective and noun principal share the pronunciation /ˈprɪnsəpəl/.",
          "disposition": "included",
          "rationale": "Pronunciation support for the entry."
        },
        {
          "id": "U-010",
          "source_fact_ids": [
            "F-010",
            "F-028"
          ],
          "canonical_statement": "Principal came through French from Latin principalis and princeps, with a semantic core of first or chief.",
          "disposition": "included",
          "rationale": "Etymology is supported by two references."
        },
        {
          "id": "U-011",
          "source_fact_ids": [
            "F-011"
          ],
          "canonical_statement": "Principalship is listed as a noun derivative of principal.",
          "disposition": "included",
          "rationale": "Recorded noun derivative."
        },
        {
          "id": "U-012",
          "source_fact_ids": [
            "F-012"
          ],
          "canonical_statement": "Principally is the adverb formed from principal.",
          "disposition": "included",
          "rationale": "Recorded adverb derivative."
        },
        {
          "id": "U-013",
          "source_fact_ids": [
            "F-032"
          ],
          "canonical_statement": "Principal and principle differ in spelling, parts of speech, and current meanings.",
          "disposition": "included",
          "rationale": "Major learner confusion directly addressed by dictionary usage guidance."
        },
        {
          "id": "U-014",
          "source_fact_ids": [
            "F-029",
            "F-030",
            "F-031"
          ],
          "canonical_statement": "Etymonline records historical attestation dates for chief-person, education-head, and money senses.",
          "disposition": "excluded",
          "rationale": "These historical facts are retained in the fixed inventory but are not used to support current lexical scope or grammar claims."
        }
      ],
      "claim_units": [
        {
          "id": "C-001",
          "union_ids": [
            "U-001"
          ],
          "subject_form": "principal",
          "claim_type": "lexical_sense",
          "statement": "The adjective means principal, main, or first in relative importance.",
          "article_target_ids": [
            "definition:001",
            "grammar_pattern:001"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-001",
              "support_summary": "Merriam-Webster directly defines the adjective."
            },
            {
              "source_fact_id": "F-013",
              "support_summary": "Cambridge independently supplies the importance definition."
            },
            {
              "source_fact_id": "F-016",
              "support_summary": "Collins adds rank, authority, and degree."
            }
          ]
        },
        {
          "id": "C-002",
          "union_ids": [
            "U-002"
          ],
          "subject_form": "principal",
          "claim_type": "lexical_sense",
          "statement": "Principal is a person in authority and conventionally a school or education head, with the institution and preferred title varying by region.",
          "article_target_ids": [
            "definition:002",
            "grammar_pattern:002",
            "usage_note:002"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-002",
              "support_summary": "Merriam-Webster directly supports the person-with-controlling-authority wording used by the general person frame."
            },
            {
              "source_fact_id": "F-003",
              "support_summary": "Merriam-Webster directly gives the educational executive sense."
            },
            {
              "source_fact_id": "F-014",
              "support_summary": "Cambridge directly supports describing a principal as the person in charge of a school."
            },
            {
              "source_fact_id": "F-017",
              "support_summary": "Collins supplies the English college qualification."
            }
          ]
        },
        {
          "id": "C-003",
          "union_ids": [
            "U-003"
          ],
          "subject_form": "principal",
          "claim_type": "lexical_sense",
          "statement": "Principal can denote an established leading performer or orchestral section-player role rather than an important person generally.",
          "article_target_ids": [
            "definition:003",
            "grammar_pattern:003",
            "usage_note:003",
            "collocation:performing-arts-principal",
            "example:performing-arts-principal",
            "collocation:orchestra-principal",
            "example:orchestra-principal"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-007",
              "support_summary": "Merriam-Webster's noun sense directly supports using principal as the head of a copular noun phrase for a leading performer."
            },
            {
              "source_fact_id": "F-018",
              "support_summary": "Collins directly records the leading-performer and orchestral first-player uses, supporting the displayed noun-headed performing-arts realization and orchestral role frame."
            }
          ]
        },
        {
          "id": "C-004",
          "union_ids": [
            "U-004"
          ],
          "subject_form": "principal",
          "claim_type": "specialist_use",
          "statement": "Financial principal is the original or underlying borrowed, lent, or invested capital amount, distinct from interest and returns; principal repayment reduces the obligation.",
          "article_target_ids": [
            "definition:004",
            "grammar_pattern:004",
            "usage_note:004"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-008",
              "support_summary": "Merriam-Webster defines the capital-sum sense and distinguishes principal from interest."
            },
            {
              "source_fact_id": "F-015",
              "support_summary": "Cambridge directly supports principal as an amount lent, borrowed, or invested apart from interest."
            },
            {
              "source_fact_id": "F-019",
              "support_summary": "Collins independently distinguishes capital sum and bond face value from interest or profit."
            },
            {
              "source_fact_id": "F-024",
              "support_summary": "Wex states the original-amount contrast and explains that repayment reduces the principal obligation."
            },
            {
              "source_fact_id": "F-027",
              "support_summary": "Investor.gov directly supports the initial-amount-invested frame."
            }
          ]
        },
        {
          "id": "C-005",
          "union_ids": [
            "U-005"
          ],
          "subject_form": "principal",
          "claim_type": "specialist_use",
          "statement": "Trust principal is property or corpus distinct from the income it produces.",
          "article_target_ids": [
            "definition:004",
            "grammar_pattern:004",
            "usage_note:004"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-025",
              "support_summary": "Wex directly supports trust principal as property or corpus distinct from income."
            }
          ]
        },
        {
          "id": "C-006",
          "union_ids": [
            "U-006"
          ],
          "subject_form": "principal-agent relationship",
          "claim_type": "specialist_use",
          "statement": "An agency principal gives authority to an agent acting on its behalf and is the source of that authority; Wex's US-law account additionally states that the agent is subject to the principal's control.",
          "article_target_ids": [
            "definition:005",
            "grammar_pattern:005",
            "usage_note:005",
            "word_formation:003"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-004",
              "support_summary": "Merriam-Webster identifies the source-of-authority role."
            },
            {
              "source_fact_id": "F-020",
              "support_summary": "Collins independently gives the agent-employing principal."
            },
            {
              "source_fact_id": "F-023",
              "support_summary": "Wex gives authority, behalf, and control elements."
            }
          ]
        },
        {
          "id": "C-007",
          "union_ids": [
            "U-007"
          ],
          "subject_form": "principal",
          "claim_type": "specialist_use",
          "statement": "Criminal-law principal denotes a participant treated as a principal under the applicable legal classification and contrasted with an accessory.",
          "article_target_ids": [
            "definition:006",
            "grammar_pattern:006",
            "usage_note:006"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-005",
              "support_summary": "Merriam-Webster supplies the criminal-participant sense."
            },
            {
              "source_fact_id": "F-021",
              "support_summary": "Collins directly supports the displayed directly-responsible-for-a-crime frame and the classification context."
            }
          ]
        },
        {
          "id": "C-008",
          "union_ids": [
            "U-008"
          ],
          "subject_form": "principal obligor",
          "claim_type": "specialist_use",
          "statement": "An obligation-law principal is primarily liable, in contrast with a surety or guarantor with secondary liability.",
          "article_target_ids": [
            "definition:007",
            "grammar_pattern:007",
            "usage_note:007"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-006",
              "support_summary": "Merriam-Webster directly supports describing the principal as primarily liable for an obligation."
            },
            {
              "source_fact_id": "F-022",
              "support_summary": "Collins independently gives the obligation sense."
            },
            {
              "source_fact_id": "F-026",
              "support_summary": "Wex directly supports the displayed distinction between a primarily responsible principal and a surety or guarantor with secondary liability."
            }
          ]
        },
        {
          "id": "C-009",
          "union_ids": [
            "U-009"
          ],
          "subject_form": "principal",
          "claim_type": "pronunciation",
          "statement": "Principal is pronounced /ˈprɪnsəpəl/ as both adjective and noun.",
          "article_target_ids": [
            "pronunciation:001"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-009",
              "support_summary": "Merriam-Webster supplies the shared pronunciation."
            }
          ]
        },
        {
          "id": "C-010",
          "union_ids": [
            "U-010"
          ],
          "subject_form": "principal",
          "claim_type": "etymology",
          "statement": "Principal derives through French from Latin principalis and princeps and retains a first-or-chief semantic connection.",
          "article_target_ids": [
            "etymology:001"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-010",
              "support_summary": "Merriam-Webster supplies the transmission path."
            },
            {
              "source_fact_id": "F-028",
              "support_summary": "Etymonline supplies the semantic and morphological analysis."
            }
          ]
        },
        {
          "id": "C-011",
          "union_ids": [
            "U-011"
          ],
          "subject_form": "principalship",
          "claim_type": "derived_form",
          "statement": "Principalship is listed as a noun derivative of principal.",
          "article_target_ids": [
            "word_formation:002"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-011",
              "support_summary": "Merriam-Webster records principalship as the noun derivative."
            }
          ]
        },
        {
          "id": "C-012",
          "union_ids": [
            "U-012"
          ],
          "subject_form": "principally",
          "claim_type": "derived_form",
          "statement": "Principally is the adverb formed from principal.",
          "article_target_ids": [
            "word_formation:001"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-012",
              "support_summary": "Merriam-Webster records the adverb derivative."
            }
          ]
        },
        {
          "id": "C-013",
          "union_ids": [
            "U-013"
          ],
          "subject_form": "principle",
          "claim_type": "usage_distinction",
          "statement": "Principle is a noun for a rule or fundamental truth, whereas principal is an adjective for the most important item.",
          "article_target_ids": [
            "usage_note:001"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-032",
              "support_summary": "Merriam-Webster directly explains this spelling, meaning, and part-of-speech contrast."
            }
          ]
        },
        {
          "id": "C-014",
          "union_ids": [
            "U-003"
          ],
          "subject_form": "principal dancer",
          "claim_type": "collocation",
          "statement": "In principal dancer, principal is an attributive adjective identifying a dancer in a leading performing-arts role.",
          "article_target_ids": [
            "collocation:principal-dancer",
            "example:principal-dancer"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-018",
              "support_summary": "Collins directly records principal dancer in its performing-arts source detail, supporting the adjective collocation and example targets."
            }
          ]
        }
      ]
    }
  },
  "resolutions": {
    "schema_version": "resolutions_v1",
    "stage": "resolutions",
    "run_id": "resolution-principal-20260908T073126Z-740135b4",
    "context_id": "resolution-principal-context-20260908T073126Z-740135b4",
    "input_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
    "prompt_sha256": "7dfcaa0a828a334dbb84d1d31ed97312d0a9661a7aca70a7815a9f88b31ea2f1",
    "recorded_at": "2026-09-08T09:45:00Z",
    "input_artifacts": [
      "entry_body",
      "all_findings"
    ],
    "resolutions": [
      {
        "id": "normal-evidence-001",
        "finding_id": "normal-evidence-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-032 supports the principle-as-rule versus principal-as-most-important-adjective distinction, but not the note's added noun inventory or its basic-principle substitution example.",
        "required_changes": [
          "Limit the spelling note to the distinction directly recorded by F-032."
        ],
        "implemented_changes": [
          "Removed the unbound person-and-amount noun summary and the unsupported basic principle/basic principal example; retained only F-032's rule-noun versus most-important-adjective contrast."
        ],
        "resolved_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "id": "normal-evidence-002",
        "finding_id": "normal-evidence-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-002 directly supports a person with controlling authority and F-014 directly supports a principal as the person in charge of a school, while the former at/of/compound templates were not recorded in the fixed facts.",
        "required_changes": [
          "Replace the unsupported organization and education templates with complete frames that directly express the fixed authority and school-in-charge facts without narrowing U-002."
        ],
        "implemented_changes": [
          "Replaced the at/of/school-principal/college-principal set with a principal with controlling authority and the principal be in charge of a school, each with a matching example; tightened the C-002 support summaries without changing facts or U-002."
        ],
        "resolved_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "id": "normal-evidence-003",
        "finding_id": "normal-evidence-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-018 directly records principal dancer and the first player of an orchestral section, but not perform or serve as a principal with an organization or the possessive one-of-principals construction.",
        "required_changes": [
          "Replace the unsupported complements with complete frames grounded in F-018 while preserving both branches of U-003."
        ],
        "implemented_changes": [
          "Replaced the perform/serve-with and possessive frames with a principal dancer and the principal be the first player of an orchestral section, each with a matching example; tightened C-003's F-018 binding without changing facts or U-003."
        ],
        "resolved_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "id": "normal-evidence-004",
        "finding_id": "normal-evidence-004",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The fixed finance and trust facts directly support an initial invested amount and contrasts with interest or income, but do not support the bundled pay-down, protect, repay, and distinguish verb frames.",
        "required_changes": [
          "Remove the unsupported verb bundle and retain complete frames that state only the directly supported amount and contrast relations."
        ],
        "implemented_changes": [
          "Replaced the former finance/trust construction set with principal as the initial amount invested, principal distinct from interest, and trust principal distinct from income, with matching examples; tightened the C-004/C-005 binding summaries without adding facts."
        ],
        "resolved_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "id": "normal-evidence-005",
        "finding_id": "normal-evidence-005",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-021 directly supports a principal as a person directly responsible for a crime, but not the former in-complement or treat-as constructions.",
        "required_changes": [
          "Replace both unsupported criminal-law templates with the complete directly-responsible-for-a-crime frame."
        ],
        "implemented_changes": [
          "Replaced the in and treat-as frames and examples with the principal be directly responsible for a crime, and tightened C-007's F-021 binding summary."
        ],
        "resolved_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      },
      {
        "id": "normal-evidence-006",
        "finding_id": "normal-evidence-006",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "F-006 and F-022 directly support primary liability for an obligation, and F-026 directly supports the distinction from a surety or guarantor with secondary liability; the former liable-as, obligation-of, and coordination templates exceeded those records.",
        "required_changes": [
          "Replace the unsupported liability templates with complete frames directly expressing primary liability and the secondary-liability contrast."
        ],
        "implemented_changes": [
          "Replaced the former three-template set with the principal be primarily liable for an obligation and the principal distinct from a surety or guarantor with secondary liability, with matching examples; tightened C-008's binding summaries without adding facts."
        ],
        "resolved_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4"
      }
    ]
  },
  "inventories": {
    "target_results": [
      {
        "id": "pronunciation:001",
        "kind": "pronunciation",
        "location": "line:4",
        "section": "＃発音記号",
        "sense": "",
        "text_sha256": "44b1c0938418ce93ce8e11642cba3f81eac56b1116e7e02e6fa7827f85672b8e",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "発音: /ˈprɪnsəpəl/。形容詞と名詞で同じ発音を用いる。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text_sha256": "bae229b3d4fbc683bd59045563d77e2d85d75eefdf953bae0c2561b149b1ffb3",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "中英語・古フランス語を経て、ラテン語 *principalis*「第一の、主要な」にさかのぼる。その基になった *princeps* は、*primus*「第一の」と *capere*「取る」に関係し、「第一の位置を占める者」という発想を持つ。語源には「第一の、主要な」という意味的なつながりがある。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "ce245da0a062df1341b888cc87a63e55840006658f433d4380a88ab02cd60ef5",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・principally：`principal` の副詞形。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "036817bdb68a3a628d6f4eb172b4c3be6bc7be30a2884a881977709287899123",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・principalship：`principal` の名詞派生形。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "149c713b643bd7ea14ef62ebb939be3794a151eda105c35b79033dced9845f50",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・principal-agent relationship：法律上の本人・代理人関係を表す複合表現。"
      },
      {
        "id": "core_image:001",
        "kind": "core_image",
        "location": "line:18",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "047b082e9508ec25f7898af615237160c20dc09cb4931e6fc567c31fbcd9fd78",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`principal` の中心は、「重要度・権限・責任・金額の土台として第一に位置する」である。形容詞では主要なものを選び出し、名詞では権限・主導的地位を持つ人や教育機関の長、舞台芸術の主要演者やオーケストラの首席奏者、利息・収益に対する元の金額や信託収益に対する財産本体、法的関係の主要当事者を指す。"
      },
      {
        "id": "core_image:002",
        "kind": "core_image",
        "location": "line:19",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "0d83be404d622af2fe44c7b67bbbc45871bf19d6aef7657d17f1008df9e5835a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・重要度で第一に位置するもの → 「主要な、最も重要な」（語義1）"
      },
      {
        "id": "core_image:003",
        "kind": "core_image",
        "location": "line:20",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "b9f6db22ba472ff7401cf6a86a5afeebe12422318a0649e89c5dc98c617d16ee",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・組織で権限・主導的地位を持つ人、特に教育機関の長 → 「上級責任者、校長、学長」（語義2）"
      },
      {
        "id": "core_image:004",
        "kind": "core_image",
        "location": "line:21",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "c0049cde0a27e45c6acd51b31b5ab806d4cf912b6ea78a438ce5cc957d795b4b",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・舞台芸術の主要演者、またはオーケストラで一つのセクションを率いる奏者 → 「主要演者、首席奏者」（語義3）"
      },
      {
        "id": "core_image:005",
        "kind": "core_image",
        "location": "line:22",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "11467e11847d5c9242d81800f4c6c1bf230fc1a27b20b90f3bea09e785e81532",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・利息・収益に対する基礎額、または信託収益に対する財産本体 → 「元金、元本、信託元本」（語義4）"
      },
      {
        "id": "core_image:006",
        "kind": "core_image",
        "location": "line:23",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "9e19c86755ace446c69098f171577fdd63a4abd58e91f82cf5e42c12a7e419d2",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・代理関係で権限の源として第一に位置する当事者 → 「本人、依頼者」（語義5）"
      },
      {
        "id": "core_image:007",
        "kind": "core_image",
        "location": "line:24",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "462481c6e9bafd6489bb65b5288c9a9dcecd6cb905dc0279b8e52757fa0cfebe",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・適用法上 `principal` と分類される犯罪関与者 → 「犯罪関与者」（語義6）"
      },
      {
        "id": "core_image:008",
        "kind": "core_image",
        "location": "line:25",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "858b7c96bedab7b54b2e9c6400275f502261bc9fe870a3352e213c65bd822c40",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・債務・保証関係で第一次的責任を負う者 → 「主たる債務者・義務者」（語義7）"
      },
      {
        "id": "sense_boundary:001",
        "kind": "sense_boundary",
        "location": "line:29",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "0405096313f89435070b4ff2db2ef3318d925937279eddff323ea94a7ab23364",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "1. 【形容詞】主要な、最も重要な、第一の"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:31",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "06a6778bc18c2af7d80b2e0012d867e9bf587b91f2143ea70b4539fb99ae47e2",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "複数の原因、目的、人物、場所、要素などの中で、重要度・影響力・順位が最も高い、または特に高いものを示す。単に時間的に最初という意味ではなく、重要性や中心性の評価を表す。"
      },
      {
        "id": "frequency:001",
        "kind": "frequency",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "7a626327bdf4a8ce1246cb04f8b9692c985873b0ba478e5ff432ffa1425edf1f",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈9/10〉"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:35",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "67605dd5194898091cb2963ee8e85dafd1aa993754062c3f7ee7be210207be11",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "標準～やや形式的。報道、ビジネス、学術、行政で広く使う。日常会話では `main` がより普通なことが多い。"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:37",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "127d17439e0e22749fd3fbecc8b0829ed1a71c2b564e6d9c4bf567df94265787",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "限定用法で `principal + 〈名詞〉` の形を取り、「主要な～」を表す。"
      },
      {
        "id": "collocation:001",
        "kind": "collocation",
        "location": "lines:41-44",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "ecd029c4010067e8279a59384579e9937b03cb73393e3f2d9e707bfe889ae1f6",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`the principal reason for ...`\n用途: 出来事・状況・判断・行動などについて、最も重要な理由を示す。\n例: The principal reason for the delay was a shortage of parts.\n訳: 遅延の主な理由は部品不足だった。"
      },
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:46-49",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "ebbeff95e5fe167bf1179949500d2f2d9b74cd39f6ac5dc62c4d6db63abf4707",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`the principal cause of ...`\n用途: 出来事を引き起こした最も重要な原因を示す。\n例: Investigators identified corrosion as the principal cause of the failure.\n訳: 調査担当者は、腐食をその故障の主因と特定した。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:51-54",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "dcd63a8f0b7ceed4bca1c8f8688a74cc7b546f5e4f9a5ebdb954f1ecf2d4ee74",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`a principal source of ...`\n用途: 物・情報・収入などの主要な供給源を示す。\n例: Tourism is a principal source of income for the island.\n訳: 観光はその島の主要な収入源の一つである。"
      },
      {
        "id": "collocation:004",
        "kind": "collocation",
        "location": "lines:56-59",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "9df2b59aec335679725d34feebc361720dac93e85656e60047ed4c99a3cb08f6",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`one of the principal 〈複数名詞〉`\n用途: 最重要候補が複数ある中の一つであることを示す。\n例: She is one of the principal architects of the reform.\n訳: 彼女はその改革の主要な立案者の一人である。"
      },
      {
        "id": "collocation:005",
        "kind": "collocation",
        "location": "lines:61-64",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "9940caf00c24b690bb9c714908b287f874e12006739745f415f5e626a8681ea1",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`a principal dancer`\n用途: `principal` を限定用法の形容詞として用い、舞台芸術で主要な役を担うダンサーを表す。\n例: She is a principal dancer.\n訳: 彼女は主要な役を担うダンサーである。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:66",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "956f313e34514302cd15d61d972860496a8fb896a7c85634dc9bc22b3aacc1bb",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`principal` と `principle` は綴りも意味も異なる。`principle` は「基本的な規則・法則」を表す名詞で、`principal` は「最も重要な」を表す形容詞にもなるため、両者を混同しない。"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:70-75",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "3aeb0f0d3fa989ec84252109862fc64487347352e147a10e649dd1d7aaa0e3e4",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・main\n定義: 複数のものの中で中心的・最重要である。\n頻度: 〈10/10〉\n違い: `main` は日常語で範囲が広い。`principal` はより形式的で、順位・重要性・影響力が高いことを意識させる。\n例: Our main goal is to reduce waiting times.\n訳: 私たちの主な目標は待ち時間を減らすことだ。"
      },
      {
        "id": "synonym:002",
        "kind": "synonym",
        "location": "lines:77-82",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "debe9972bb133152fef65f0a631187d12faa87ae93caccd3f6f3439195dbc9fb",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・primary\n定義: 第一順位・第一段階である、または最も基本的である。\n頻度: 〈9/10〉\n違い: `primary` は重要性に加え、順序・段階・基本性にも焦点を置ける。`principal` は主として相対的な重要度や地位を表す。\n例: Safety is our primary concern.\n訳: 安全が私たちの最優先事項である。"
      },
      {
        "id": "synonym:003",
        "kind": "synonym",
        "location": "lines:84-89",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "fd5467b15a0f3c88a1f21076b0c6ba6f152bb7b809ead1dfe4caf04862c271e8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・chief\n定義: 同種の中で最上位・最重要である。\n頻度: 〈8/10〉\n違い: `chief` は役職名や「最大の原因・懸念」によく使われ、最上位性を強く示す。`principal` は文章語として原因・目的・人物・場所などに幅広く使う。\n例: Cost remains the chief obstacle to expansion.\n訳: 費用が依然として拡大の最大の障害である。"
      },
      {
        "id": "synonym:004",
        "kind": "synonym",
        "location": "lines:91-96",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "c2c257a086fc937d97b39f8958dc5c4d3fee9f105e3e3a5f62557869f8774016",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・leading\n定義: ある分野で先頭に立ち、大きな影響力や高い評価を持つ。\n頻度: 〈9/10〉\n違い: `leading` は人・企業・研究機関などの実績や影響力を強調しやすい。`principal` は実績評価を必須とせず、対象内での中心性を示す。\n例: She is a leading expert on marine ecosystems.\n訳: 彼女は海洋生態系の第一人者である。"
      },
      {
        "id": "antonym:001",
        "kind": "antonym",
        "location": "lines:100-105",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "f37859c82830add16c5b58637ca6d1e90f4ae91a9a97d83f05f37b22c40c186a",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・secondary\n定義: 第一ではなく、重要度・順位が二次的である。\n頻度: 〈8/10〉\n違い: 重要度・順位の軸で `principal` と方向が反対になり、主要なものに対する従属的・補助的なものを表す。\n例: Price was only a secondary consideration.\n訳: 価格は二次的な考慮事項にすぎなかった。"
      },
      {
        "id": "antonym:002",
        "kind": "antonym",
        "location": "lines:107-112",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "07915a2bb71c129e0341f40261fdf363920adff6a73e8ae5911ac3505382342c",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・minor\n定義: 重要性・規模・影響が比較的小さい。\n頻度: 〈9/10〉\n違い: `principal` との程度軸上の対立で、最重要・主要ではない小さな要素を表す。\n例: The report contains a few minor errors.\n訳: その報告書には小さな誤りがいくつかある。"
      },
      {
        "id": "sense_boundary:002",
        "kind": "sense_boundary",
        "location": "line:114",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "text_sha256": "2bad9de629189c1d68fb61c0eef2e648634db975b080a823f53dfa34c760582a",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:116",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "text_sha256": "b58d4fae859e82c7435794ccf65d6c8ebdba2894b4ccf600574268bda29fba4c",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "組織で支配的権限または主導的地位を持つ人。特に、学校、カレッジ、その他の教育機関を管理する最高責任者を指す。教育上どの種類の機関を指すかは地域と制度によって異なる。"
      },
      {
        "id": "frequency:002",
        "kind": "frequency",
        "location": "line:118",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "text_sha256": "223f0f3bb105d64687ce0ff83ae044846c2f48c7a55d9d015dbc0ce12503d473",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈8/10〉"
      },
      {
        "id": "register:002",
        "kind": "register",
        "location": "line:120",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "text_sha256": "e10b22ea073a27e0180a03c030af8abb0ad8e22bfba63fed911be798bab23a71",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "標準～やや形式的。企業・専門組織では権限または主導的地位を持つ人を表す。教育分野では学校・教育機関の長を表し、イングランドではカレッジの長を指す場合がある。"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:122",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "text_sha256": "2cac2021c8e4740f9e6866bf8d595c44e8f24d194ccdf053eb7396bea5006b67",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "一般の権限者は `a principal with controlling authority`。教育機関の長は `the principal + be + in charge of 〈学校〉`。"
      },
      {
        "id": "collocation:006",
        "kind": "collocation",
        "location": "lines:126-129",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "text_sha256": "b7f8c11f423297033629462a6ad6e32d08084ee75543b7840440f47c221fb059",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`a principal with controlling authority`\n用途: 支配的権限を持つ人という一般の人物用法を表す。\n例: A principal with controlling authority approved the proposal.\n訳: 支配的権限を持つ責任者がその提案を承認した。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:131-134",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "text_sha256": "728d9a8c17fd5d2f3c6672a6dc2a440c50c33e96cea9d013b27d138410cebe44",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`the principal + be + in charge of 〈学校〉`\n用途: 教育機関を管理する長であることを表す。\n例: The principal is in charge of the school.\n訳: その校長が学校の管理を担っている。"
      },
      {
        "id": "usage_note:002",
        "kind": "usage_note",
        "location": "line:136",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "text_sha256": "ca00f74adc329e64b940c8cbc000ff5af032512025a99881404fb88a89d811df",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "一般の「重要人物」を自由に指す語ではなく、権限や主導的地位が文脈上確立した人に用いる。教育上の役職名は地域や制度によって異なるため、日本語の「校長」を機械的にすべて `principal` としない。"
      },
      {
        "id": "synonym:005",
        "kind": "synonym",
        "location": "lines:140-145",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】権限・主導的地位を持つ人；特に校長、学長",
        "text_sha256": "c265c1fd04a84f63fb60e7cb00a6d1de188fac2494c6b4ddbfe0922c75b61a98",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・head\n定義: 学校・組織などの長。\n頻度: 〈9/10〉\n違い: `head` は組織の長を広く表す。`principal` は権限・主導的地位を持つ人を表し、特に教育機関で役職名として用いられる。\n例: She is the head of a large secondary school.\n訳: 彼女は大規模な中等学校の校長である。"
      },
      {
        "id": "sense_boundary:003",
        "kind": "sense_boundary",
        "location": "line:147",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "be88b8b9625ce6fc5c83a4b261d829bdb2ec9087ebcf298837b3003c7416f535",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "id": "definition:003",
        "kind": "definition",
        "location": "line:149",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "e0abacfc1040b69a7784fdf4eee9dc47585c584de13d05927e2bffe74cf45546",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "舞台芸術で主要な役を担う演者、またはオーケストラで一つのセクションを率いる奏者。一般の重要人物ではなく、芸術分野で確立した役割名を指す。"
      },
      {
        "id": "frequency:003",
        "kind": "frequency",
        "location": "line:151",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "a0e445b4ea32382084179e64d42d17cc5ca8def51850cf67e191301932796344",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈3/10〉"
      },
      {
        "id": "register:003",
        "kind": "register",
        "location": "line:153",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "988adda62185ee12eec15ac5ac092052d77fb841ee2fa34049263a5f60d5c01c",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "舞台芸術・オーケストラ・音楽の専門語。"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:155",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "23b604c28939a11c3217ab8187cc1990e5774c32ae881c3f12a81f29ea7b7e4f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "舞台芸術の主要演者を名詞で表す場合は `〈演者〉 + be + a principal`。オーケストラの役職は `the principal + be + the first player of 〈セクション〉`。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:159-162",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "82c1eecbcd4dd982ed7bcea79804bd91474ae384644a393ac46878014e96c0dc",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`be a principal`\n用途: 舞台芸術の文脈で、主要な役を担う演者を名詞 `principal` で表す。\n例: In this ballet company, she is a principal.\n訳: このバレエ団で、彼女は主要な役を担う演者である。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:164-167",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "e2ada2124d6161eeb12e4f44a569f454e36891d86848abc664f7db984fe796b0",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`the principal + be + the first player of 〈オーケストラのセクション〉`\n用途: オーケストラのセクションで首席を務める奏者を表す。\n例: The principal is the first player of the violin section.\n訳: その首席奏者はバイオリン・セクションの第一奏者である。"
      },
      {
        "id": "usage_note:003",
        "kind": "usage_note",
        "location": "line:169",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "e88a649e80217fb73ac6a2dbc340f36a8e21a0e3b6be8089d31c68c16b2fe10b",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "舞台芸術団体やオーケストラ内で確立した役割名として用い、一般の「重要人物」には広げない。"
      },
      {
        "id": "synonym:006",
        "kind": "synonym",
        "location": "lines:173-178",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "fac8779a8c865def95d243d10507f8dde8cb83efd694a963758811b319273cd6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・section leader\n定義: オーケストラで一つのセクションを率いる奏者。\n頻度: 〈4/10〉\n違い: 役割を説明する一般的な表現で、`principal` は確立した役職名として用いられる。\n例: The section leader rehearsed the difficult passage.\n訳: セクションの首席奏者は難しい楽節を練習した。"
      },
      {
        "id": "sense_boundary:004",
        "kind": "sense_boundary",
        "location": "line:180",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "09794c8b37895e4a6f2c72e6333bba75c57bb22ef567b52e9540085a27b382e8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "id": "definition:004",
        "kind": "definition",
        "location": "line:182",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "37f87f6e1bbb984d2bfb3ed69e8e68ea47c895b431b6fe7959b375a5509dfd73",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。信託法では、収益と区別される信託財産そのもの、すなわち信託元本・corpusを指す。"
      },
      {
        "id": "frequency:004",
        "kind": "frequency",
        "location": "line:184",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "4c83f924416ef4455522dc0ab9ad637bb8820d1ecc7c146513681f28e8bd4b71",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈7/10〉"
      },
      {
        "id": "register:004",
        "kind": "register",
        "location": "line:186",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "db5a8c219e02a4831c9d1c6d8797be7ac432a4d0e8d358ee2cf15457011274fb",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "金融、融資、投資、会計、信託法。金融義は日常的なローン説明にも現れ、信託義は専門的である。"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:188",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "52eeb5db8e03f48127f3cead64e4d991f24c0a6d6ce8a41f9f5d226047b9e60a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "金融では `principal + be + the initial amount invested`"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:188",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "0076e5f5ee8b14c9af3a2e4c83b3530fb4500e42063d9b9f4167498cde2b3412",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`principal + be + distinct from interest`。信託法では `trust principal + be + distinct from income`。"
      },
      {
        "id": "collocation:010",
        "kind": "collocation",
        "location": "lines:192-195",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "77d96d298c10617b26808a0e4c14249b0fa2542ef40b7053a92493891d4cc087",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`principal + be + the initial amount invested`\n用途: 投資で、収益の基礎となる最初の金額を表す。\n例: The principal is the initial amount invested.\n訳: 元本とは最初に投資された金額である。"
      },
      {
        "id": "collocation:011",
        "kind": "collocation",
        "location": "lines:197-200",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "b422e012efb14251fde989a07982ffd7b47b91fd9c2329662ab3b9b0a7742a63",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`principal + be + distinct from interest`\n用途: 借入・貸付の元金を利息と区別して表す。\n例: Principal is distinct from interest on the loan.\n訳: 元金はその融資の利息とは別のものである。"
      },
      {
        "id": "collocation:012",
        "kind": "collocation",
        "location": "lines:202-205",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "1f3b7b3afa7607835f8425b711d69317caa9d36b8a4ad4a697407060a25f4d31",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`trust principal + be + distinct from income`\n用途: 信託財産の元本を、そこから生じる収益と区別する。\n例: Trust principal is distinct from income.\n訳: 信託元本は収益とは別のものである。"
      },
      {
        "id": "usage_note:004",
        "kind": "usage_note",
        "location": "line:207",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "d001ea049b06832bc08d3d0bcf7eb6e4653b6a3df2192a21da0f192a12380927",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`principal` は元の基礎額、`interest` は借入の対価または貸付・投資から生じる追加額であり、反意語ではなく関連する別の金額構成要素である。信託では `principal` が財産本体、`income` がそこから生じる収益を指す。`repay the principal` では `principal` 自体が目的語の名詞になる。日本語の「元利金」は `principal and interest` であり、`principal interest` とはしない。"
      },
      {
        "id": "synonym:007",
        "kind": "synonym",
        "location": "lines:211-216",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "5ce1d09ecf03136c137d2220261d2d931c7c37c7ea18438c5a30554e6a8321a2",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・capital\n定義: 投資・事業に用いられる資金または資産。\n頻度: 〈9/10〉\n違い: `capital` は事業資金・生産資産まで広く表す。`principal` は特定の貸付・借入・投資で利息や収益の基礎となる元の額を指す。\n例: The company raised additional capital from investors.\n訳: その会社は投資家から追加資金を調達した。"
      },
      {
        "id": "sense_boundary:005",
        "kind": "sense_boundary",
        "location": "line:218",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "a2e2eb7f4ef3fe2258aa47dd420aa95b649afdbd5429cca61e0468cca64f1516",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "id": "definition:005",
        "kind": "definition",
        "location": "line:220",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "972881c8b7e8441373cc29eac8957330ec95620d858c9bb028c8d8e102604d0f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。"
      },
      {
        "id": "frequency:005",
        "kind": "frequency",
        "location": "line:222",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "f75683d2ec70c01e8ef877fe56064d1d46ce1e20d9e5a13b41fe1f03202dbee8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈5/10〉"
      },
      {
        "id": "register:005",
        "kind": "register",
        "location": "line:224",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "73e5f4ab1e818f59896212051d3e1cbd2c94f11774ce6576471146222ecf74bc",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "法律、保険、不動産、商取引。日常語として人を「依頼主」と呼ぶだけなら `client` が自然な場合も多い。"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:226",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "85abc4deb9f0d9671843d3dfa9c2fbc3ab8f942c426132cac8ffa0b003c01789",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`a principal-agent relationship`＝本人・代理人関係"
      },
      {
        "id": "grammar_pattern:007",
        "kind": "grammar_pattern",
        "location": "line:226",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "4df55c3bf5a7207372bf743629d014b75789666926ea68b23723ee909395a209",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`act on behalf of the principal`＝本人を代理して行動する"
      },
      {
        "id": "collocation:013",
        "kind": "collocation",
        "location": "lines:230-233",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "bf5d0e5cf8f37ad1abb6ea453cc81ba3f799267473a34c69802700d818dbecb7",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`a principal-agent relationship`\n用途: 権限を与える本人と、そのために行動する代理人との関係を表す。\n例: The contract created a principal-agent relationship between the owner and the broker.\n訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。"
      },
      {
        "id": "collocation:014",
        "kind": "collocation",
        "location": "lines:235-238",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "28de6ded590b27ced1e143c49506cbb12314d9475e752d038551c5955a6d8307",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`act on behalf of the principal`\n用途: 代理人が本人を代理して行動することを表す。\n例: The agent may sign the document on behalf of the principal.\n訳: 代理人は本人を代理してその書類に署名できる。"
      },
      {
        "id": "usage_note:005",
        "kind": "usage_note",
        "location": "line:240",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "e3c9059c36aa0ea8d86fd3eddf1d81bd1fe162d0f9a9ec801cb9e8a1f31b5f65",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "法律用語の `principal` は、`agent` に権限を与える側を表す関係上の役割名である。`principal` が権限の源となり、`agent` は本人のためにその権限の範囲で行動する。"
      },
      {
        "id": "synonym:008",
        "kind": "synonym",
        "location": "lines:244-249",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "8a100dc4cfab377b2f5c1f2958efa30d236575e253ef680a343da757dc4d3bb1",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・mandator\n定義: 他人に委任・代理の権限を与える者。\n頻度: 〈2/10〉\n違い: 特定の法体系や専門文脈で使われる低頻度語である。\n例: The mandator may revoke the mandate subject to the agreement.\n訳: 委任者は、契約の定めに従い、委任を撤回できる。"
      },
      {
        "id": "antonym:003",
        "kind": "antonym",
        "location": "lines:253-258",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "1f9ba717b7b80f87ccc7b7fb638b5ff17aa3c84bb61fd89050f06745e5aef7e2",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・agent\n定義: 他者から権限を与えられ、その者のために行動する人または法人。\n頻度: 〈8/10〉\n違い: 同じ代理関係の役割軸で、`principal` が権限を与える側、`agent` が与えられた権限で行動する側である。\n例: The agent negotiated the sale for the owner.\n訳: 代理人は所有者のために売却交渉を行った。"
      },
      {
        "id": "sense_boundary:006",
        "kind": "sense_boundary",
        "location": "line:260",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "3e74d590a8c50f6660b52d5faf153be125588dec134ccbef0c74a06cbe40861c",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者"
      },
      {
        "id": "definition:006",
        "kind": "definition",
        "location": "line:262",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "86b888c6189a9d4bd992d78facc4ff147c3b39ff9395e3f0aec4ccddaa49a030",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。"
      },
      {
        "id": "frequency:006",
        "kind": "frequency",
        "location": "line:264",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "c9f89b3d40a42341908558a5512ad7d34bbc108cc33b512e22b76f6557469962",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈2/10〉"
      },
      {
        "id": "register:006",
        "kind": "register",
        "location": "line:266",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "d609cd516794fbb67fdf8f0ba03b201698be0ef4de47b31b46857aeaf343a9d3",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "刑事法の専門語。犯罪に関するこの語義は法域によって分類法が異なる。"
      },
      {
        "id": "grammar_pattern:008",
        "kind": "grammar_pattern",
        "location": "line:268",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "b4b7c5aed89df1f51d9d9a7967bd66b2baf7943c02c6efcac487192814e376f7",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`the principal + be + directly responsible for 〈犯罪〉`"
      },
      {
        "id": "collocation:015",
        "kind": "collocation",
        "location": "lines:272-275",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "2abe45d58349fa8ec59fa4d48c4c7a79b97b547328784a3f39659865bd1bd129",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`the principal + be + directly responsible for 〈犯罪〉`\n用途: 適用法上、犯罪について直接責任を負う者を表す。\n例: Under the statute, the principal is directly responsible for the crime.\n訳: その制定法の下で、当該 `principal` はその犯罪について直接責任を負う。"
      },
      {
        "id": "usage_note:006",
        "kind": "usage_note",
        "location": "line:277",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "2c9ffb8f4a02726dacd9edefb2ed0004d1a23cd240761ed706bcec0ace8791c2",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "刑事法の `principal` は適用される法的分類に従う役割名で、`accessory` と対比される。債務・保証関係の第一次的責任者は別の語義7である。"
      },
      {
        "id": "synonym:009",
        "kind": "synonym",
        "location": "lines:281-286",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "c8e25735774d5f90277c91b38cf7b4c26d1445622d65f97873a9c07f5bcd66a8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・perpetrator\n定義: 犯罪・不正行為を実際に行った者。\n頻度: 〈6/10〉\n違い: `perpetrator` は実行者に焦点を置く一般的な法律・報道語。`principal` は適用される法的分類によって、実行者以外の一定の関与者を含む場合がある。\n例: Police are still trying to identify the perpetrator.\n訳: 警察は今も犯人の特定を進めている。"
      },
      {
        "id": "sense_boundary:007",
        "kind": "sense_boundary",
        "location": "line:288",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "01f4f53fd71a655c9387a42058192b683243d8c41da6ebf0a3b2c1486c84495f",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者"
      },
      {
        "id": "definition:007",
        "kind": "definition",
        "location": "line:290",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "50676cf1c94f309b6bd6f7faa702484996d1ad9ee5978670d4ae35a7bf3381d9",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "債務・保証の文脈で、保証人などの二次的責任者と対比され、義務について第一次的に責任を負う人または法人。"
      },
      {
        "id": "frequency:007",
        "kind": "frequency",
        "location": "line:292",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "c9f89b3d40a42341908558a5512ad7d34bbc108cc33b512e22b76f6557469962",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈2/10〉"
      },
      {
        "id": "register:007",
        "kind": "register",
        "location": "line:294",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "4ec9974bf35cdcb3b2c182a1e480471eb0839e4b9bdc471df554b8627cfbc621",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "債務法・保証法の専門語。"
      },
      {
        "id": "grammar_pattern:009",
        "kind": "grammar_pattern",
        "location": "line:296",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "a3cd9326e109c8be94e706a29cf5668053f882a1818469dcbe9038845be927ba",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`the principal + be + primarily liable for 〈債務・義務〉`"
      },
      {
        "id": "grammar_pattern:010",
        "kind": "grammar_pattern",
        "location": "line:296",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "ca7b9eccb7c0937cb852aeb40cb43cf90a313cd28ed3e7b44ec78928691c9106",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`the principal + be + distinct from 〈surety/guarantor〉 with secondary liability`"
      },
      {
        "id": "collocation:016",
        "kind": "collocation",
        "location": "lines:300-303",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "69abe0f4739a0e2f63403ee6dcf0d002e1111d3c42ab276697c7942ba8def7b3",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`the principal + be + primarily liable for 〈債務・義務〉`\n用途: 主たる当事者が義務について第一次的責任を負うことを示す。\n例: The principal is primarily liable for the debt.\n訳: 主たる債務者はその債務について第一次的責任を負う。"
      },
      {
        "id": "collocation:017",
        "kind": "collocation",
        "location": "lines:305-308",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "fe089503ef39cc3bc764e38dc3aaa1bd0cc8ed9a549ee5f1ab185deb8f3885f1",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`the principal + be + distinct from 〈surety/guarantor〉 with secondary liability`\n用途: 第一次的責任者を、二次的責任を負う保証人と区別する。\n例: The principal is distinct from the surety, who has secondary liability.\n訳: 主たる債務者は、二次的責任を負う保証人とは別の当事者である。"
      },
      {
        "id": "usage_note:007",
        "kind": "usage_note",
        "location": "line:310",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "fd647019879c4b4258ec7217c812b9229e6c8c14e218af78da52fbfbfb13652b",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "この語義では、`principal` は `be liable as principal` のように人・法人を指す名詞である。金額を指す語義4の「元金」とは区別する。"
      },
      {
        "id": "synonym:010",
        "kind": "synonym",
        "location": "lines:314-319",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "13250bbfaa1e02021a404b9ad57d8283c52916fb6604b90a500bd96417cb41f6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・obligor\n定義: 契約や法律上の義務を負う者。\n頻度: 〈3/10〉\n違い: `obligor` は義務を負う者を広く表す。`principal` は保証人などと対比して、その義務について第一次的に責任を負う側を示す。\n例: The obligor must perform the duty by the stated date.\n訳: 義務者は定められた日までに義務を履行しなければならない。"
      },
      {
        "id": "synonym:011",
        "kind": "synonym",
        "location": "lines:321-326",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "69be5ed0225c2445b4462ae603a41d640fd5f32056ac0aabf582e57dc3907b52",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・debtor\n定義: 金銭その他の債務を負う者。\n頻度: 〈6/10〉\n違い: `debtor` は債務者一般を指す。`principal` は保証関係で第一次的責任を負う当事者という役割を強調する。\n例: The debtor made the payment on time.\n訳: 債務者は期限どおりに支払った。"
      },
      {
        "id": "antonym:004",
        "kind": "antonym",
        "location": "lines:330-335",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "805131819f831328bc3544761907de5d1c5c24e5e4753e965d97bb77dff72724",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・surety\n定義: 主たる債務者が履行しない場合に責任を負う保証人。\n頻度: 〈3/10〉\n違い: 責任順位の軸で、`principal` が第一次的に責任を負うのに対し、`surety` は他人の義務を担保する側に立つ。\n例: The surety paid after the borrower defaulted.\n訳: 借り手が債務不履行となった後、保証人が支払った。"
      }
    ],
    "relation_results": [
      {
        "id": "risk_sense_pair:001",
        "kind": "risk_sense_pair",
        "target_ids": [
          "sense_boundary:004",
          "sense_boundary:007"
        ],
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: usage_note:007 explicitly contrasts sense 7 with sense 4",
        "text_sha256": "44f0cd24fbb5ed787b166ead9ebfd41e88dfbf98a7b143df258f6d0b85d5b9fb",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "risk_sense_pair:002",
        "kind": "risk_sense_pair",
        "target_ids": [
          "sense_boundary:006",
          "sense_boundary:007"
        ],
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: usage_note:006 explicitly contrasts sense 6 with sense 7",
        "text_sha256": "b69148560e0ef417a676d12a1811fc5100f8975e0dc2c4ec8696d9ce0f890fc0",
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
        "id": "definition_lexical_relation_consistency:001",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "synonym:001",
          "synonym:002",
          "synonym:003",
          "synonym:004",
          "antonym:001",
          "antonym:002"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "b8da0ccb470dfc1559172c992cbecacde47461531aabd003a5bd14ec7633c141",
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
        "id": "definition_usage_consistency:002",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "usage_note:002"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "295f3faddf88fe94a54769f3154c01213f59a8ec5ddd08a484c4323874f639ed",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:002",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "synonym:005"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "8301a0cba0c2d811bd9735e1c4ccad85371e01eb21d5648309f42bbc99274dc7",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:002",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:002",
          "collocation:006",
          "collocation:007"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "bb10365e40f9719e36ecd1be1d9037a0329ddb983f9058a9d8434ea125965b7e",
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
        "id": "definition_usage_consistency:003",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003",
          "usage_note:003"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "233035012abd8e6dad06be798eb7bf266a99c5ede5bfefe46647d659b4213c3f",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:003",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003",
          "synonym:006"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "a4aca817abca786613ff711db02df76f07ee194c52d99c23fef0f40475fb96b3",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:003",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:003",
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "f7c9c54053e7924c818aca69889e0ae1503c7fe09aec293e13f87d04a08dd4b1",
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
        "id": "definition_usage_consistency:004",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004",
          "usage_note:004"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "1e4a77a9e97267bb351bad88146c78fc6f1c67aaf762e2daf3e8c0f7286d872c",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:004",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004",
          "synonym:007"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "4a171e4809e8c2fef3b538ecb53f97fe6aef9a8d76256e74cf3594c45f7e61a9",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:004",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:004",
          "collocation:010",
          "collocation:011",
          "collocation:012"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "ab1603085cacae76f67b929c7ab894fd02b8c08396325ed04119697c8913fda0",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:005",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:005",
          "collocation:010",
          "collocation:011",
          "collocation:012"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "374d71553d6db324cc1eef05d99e30aaeb1ca82d8d309bf89d90932567648e2a",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:005",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:005",
          "definition:005"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "db0f21645c8588eda738bf3097ff2d7b7fa493bfd6152f5879343320d182f2e6",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:005",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:005",
          "definition:005",
          "usage_note:005"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "ed53d1197bfb7611e73d31e9583f93c764ea94b3722a8e2b8164c4fa3b50bb03",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:005",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:005",
          "definition:005",
          "synonym:008",
          "antonym:003"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "3dfd4b590b8c787d06523d7b0271b52e5b2a8b9e830e639010d9fcd87d75f948",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:006",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:006",
          "collocation:013",
          "collocation:014"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "85d796f0555c2bde0d7ec979fc69d0faa8e290e6efd058bbe2f7e44c2e6c47ce",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:007",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:007",
          "collocation:013",
          "collocation:014"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "a345b385d559f2a13744978e7cafc8f136470b1d1f156c1079f6fca502b0b4c2",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:006",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:006",
          "definition:006"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "630ad70d7f4a49e2c4869ebada1cf3d113406ba5459f6adc1af15ad15fcf9dae",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:006",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:006",
          "definition:006",
          "usage_note:006"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "a1e3c8c66526c4ba64d2f4a6aa73a651e0990ddbe90ff1ecab45822f6ba8de8a",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:006",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:006",
          "definition:006",
          "synonym:009"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "998dc691ac4cabb6544a3d48b20ea48d9e080d05a5258f5c84ec5c9d656d3352",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:008",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:008",
          "collocation:015"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "cca0a60e8e999643f92b8717c588bceb4012ce463cd2a70ad7bf9a3a6c68ba49",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:007",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:007",
          "definition:007"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "c7af55256804ed80c12347f5c8cc6a55f24dfb37c901396e3754e1f6a52edd05",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:007",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:007",
          "definition:007",
          "usage_note:007"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "2644d237f4e89b916f65c89f9971d3e3219b0c52c25c32bddad398bbd7764001",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:007",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:007",
          "definition:007",
          "synonym:010",
          "synonym:011",
          "antonym:004"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "7e05cfe51921394c2ebcfb962fbd04f758caf0d25a234b808985264a4a0ff712",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:009",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:009",
          "collocation:016",
          "collocation:017"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "ef7096d59c54a614d3d2d4784e892ae3bbee27996bfbe32baf6e7b153ca1f92a",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:010",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:010",
          "collocation:016",
          "collocation:017"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "af57fe42c83d2ada70faca65f56b51785cb9ff9cfb59f55f90e5ca1145774d3c",
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
          "sense_boundary:004",
          "sense_boundary:005",
          "sense_boundary:006",
          "sense_boundary:007"
        ],
        "description": "語義番号を限定しない総括的なコアイメージが、記事の語義目録全体を不当に一般化していないことを確認する。",
        "text_sha256": "0d5dbddc5fa01dc90eb178e6a30d1cac0d349fd7d3a9d3f2a5974e4cf2fdc38c",
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
          "usage_note:001"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "054a1725501eb1bd6dc5643181c3c50b4308ee7fdc944c1d691456d814e7b7bb",
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
          "usage_note:002"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "dd2d9bcfb68cb20480eef9070be46005e695d52a96014af726ebf91ade9a6e64",
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
          "usage_note:003"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "ed8dca2b1fe948899a7337fb9aa9c3537b6eb0da19a4a7597abb80355aaf85ad",
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
          "usage_note:004"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "593be98e61460a03f6981a2f8fa53513d63fa7df0ace88501562085c7f89c9af",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "core_sense_mapping:005",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:006",
          "sense_boundary:005",
          "definition:005",
          "usage_note:005"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "8c33e4fa14c1ee6dbc507b0762ddce2dbf3d588220f3bfb1561d632ed5c575bb",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "core_sense_mapping:006",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:007",
          "sense_boundary:006",
          "definition:006",
          "usage_note:006"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "4f7f12b001bb06473ae7d3ed52bd82b83b04f7bd8aa9604cd893fe2de1119c71",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "core_sense_mapping:007",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:008",
          "sense_boundary:007",
          "definition:007",
          "usage_note:007"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
        "text_sha256": "5db71ad3e873d3865aad8cff46eb128b6539e3b946dbbcb8cf515ded2521b21d",
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
          "core_image:006",
          "core_image:007",
          "core_image:008",
          "sense_boundary:001",
          "definition:001",
          "usage_note:001",
          "sense_boundary:002",
          "definition:002",
          "usage_note:002",
          "sense_boundary:003",
          "definition:003",
          "usage_note:003",
          "sense_boundary:004",
          "definition:004",
          "usage_note:004",
          "sense_boundary:005",
          "definition:005",
          "usage_note:005",
          "sense_boundary:006",
          "definition:006",
          "usage_note:006",
          "sense_boundary:007",
          "definition:007",
          "usage_note:007"
        ],
        "description": "記事全体の語義構成、対比、訳語、限定表現から学習者が誤った一般化をしないことを横断確認する。",
        "text_sha256": "b19be8e46f49457b4173fd03f9634be254f8c5e762194d0dfb5b8eafd4d9d287",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "FB-C001",
        "surface_form": "principal",
        "frame": "principal + noun",
        "meaning": "複数の候補の中で重要性・中心性・順位が第一級の、主要な",
        "disposition": "included",
        "rationale": "principal + noun は形容詞の中心用法であり、理由・原因・供給源・人物などを重要度の軸で主要と位置づける記事の語義1に明確に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A001",
            "statement": "形容詞 principal は原則として同じ集合内での相対的重要性または中心性を表す。",
            "polarity": "must_hold",
            "scope": "形容詞の定義、文法パターン、コロケーション、類義語比較"
          },
          {
            "id": "FB-A002",
            "statement": "形容詞 principal を単なる時間順の『最初の』と同一視してはならない。",
            "polarity": "must_not_hold",
            "scope": "形容詞の定義と語法"
          }
        ]
      },
      {
        "id": "FB-C002",
        "surface_form": "a principal",
        "frame": "a principal with controlling authority",
        "meaning": "組織で支配的権限または主導的地位を持つ人物",
        "disposition": "included",
        "rationale": "a principal with controlling authority は一般人物用法を権限の有無で限定しており、単なる著名人へ不当に広げず記事の語義2に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A003",
            "statement": "人物名詞 principal の一般用法には、その組織内での権限または主導的地位が必要である。",
            "polarity": "must_hold",
            "scope": "一般人物用法の定義、用例、注意"
          },
          {
            "id": "FB-A004",
            "statement": "人物名詞 principal を文脈上の地位を問わない一般的な『重要人物』として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "一般人物用法の包含・除外境界"
          }
        ]
      },
      {
        "id": "FB-C003",
        "surface_form": "the principal",
        "frame": "the principal + be + in charge of a school or educational institution",
        "meaning": "学校・カレッジなど教育機関を管理する長",
        "disposition": "included",
        "rationale": "the principal + be + in charge of a school or educational institution は一般の権限者より狭い教育上の役職フレームで、地域・制度差の注意を伴って記事の語義2に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A005",
            "statement": "教育用法の principal は教育機関を管理する長という制度上の役職を表す。",
            "polarity": "must_hold",
            "scope": "教育用法の定義、レジスター、文法パターン"
          },
          {
            "id": "FB-A006",
            "statement": "あらゆる地域・制度の日本語『校長』を無条件に principal と訳せると一般化してはならない。",
            "polarity": "must_not_hold",
            "scope": "教育用法の地域・制度上の限定"
          }
        ]
      },
      {
        "id": "FB-C004",
        "surface_form": "a principal",
        "frame": "performer + be + a principal",
        "meaning": "舞台芸術団体で主要な役を担う演者",
        "disposition": "included",
        "rationale": "performer + be + a principal は舞台芸術で確立した役割名としての記事の語義3に含まれ、一般人物用法とは領域で明確に分離されている。",
        "semantic_assertions": [
          {
            "id": "FB-A007",
            "statement": "舞台芸術の名詞 principal は団体内で主要な役を担う演者を指す。",
            "polarity": "must_hold",
            "scope": "舞台芸術用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A008",
            "statement": "舞台芸術の役割名を芸術分野外の重要人物一般へ拡張してはならない。",
            "polarity": "must_not_hold",
            "scope": "舞台芸術用法の除外境界"
          }
        ]
      },
      {
        "id": "FB-C005",
        "surface_form": "the principal",
        "frame": "the principal + be + the first player of an orchestra section",
        "meaning": "オーケストラの一つのセクションを率いる首席奏者",
        "disposition": "included",
        "rationale": "the principal + be + the first player of an orchestra section は舞台演者とは異なるオーケストラの職務フレームであり、記事の語義3の内部で個別に説明されている。",
        "semantic_assertions": [
          {
            "id": "FB-A009",
            "statement": "オーケストラ用法の principal は特定セクションの第一奏者または首席という役割を表す。",
            "polarity": "must_hold",
            "scope": "オーケストラ用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A010",
            "statement": "オーケストラの principal を団体全体の管理責任者という意味に取り違えてはならない。",
            "polarity": "must_not_hold",
            "scope": "オーケストラ用法の意味役割"
          }
        ]
      },
      {
        "id": "FB-C006",
        "surface_form": "principal",
        "frame": "principal + be + distinct from interest",
        "meaning": "貸付・借入・投資で利息や収益の基礎となる元金または元本",
        "disposition": "included",
        "rationale": "principal + be + distinct from interest は金融上の金額構成要素を区別する中心フレームで、記事の語義4に元金への返済効果も含めて説明されている。",
        "semantic_assertions": [
          {
            "id": "FB-A011",
            "statement": "金融用法の principal は利息・利益・収益の計算または発生の基礎となる資本額を指す。",
            "polarity": "must_hold",
            "scope": "金融用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A012",
            "statement": "principal と interest を反意語として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "金融用法の語法と関係分類"
          }
        ]
      },
      {
        "id": "FB-C007",
        "surface_form": "trust principal",
        "frame": "trust principal + be + distinct from income",
        "meaning": "信託で収益と区別される財産本体または corpus",
        "disposition": "included",
        "rationale": "trust principal + be + distinct from income は金融元金とは別の信託法上の対象を明示し、記事の語義4に専門的限定とともに含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A013",
            "statement": "信託用法の principal は信託財産の本体を指し、そこから生じる income と区別される。",
            "polarity": "must_hold",
            "scope": "信託法用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A014",
            "statement": "trust principal を信託から発生する収益そのものとして扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "信託法用法の作用方向と除外境界"
          }
        ]
      },
      {
        "id": "FB-C008",
        "surface_form": "principal",
        "frame": "agent + act on behalf of the principal",
        "meaning": "代理人に自分のために行動する権限を与える本人または法人",
        "disposition": "included",
        "rationale": "agent + act on behalf of the principal は代理関係の役割方向を固定し、権限の源である本人を受権者の agent と混同せず記事の語義5に含めている。",
        "semantic_assertions": [
          {
            "id": "FB-A015",
            "statement": "代理法上の principal は agent がその者のために行動する側であり、代理権の源となる。",
            "polarity": "must_hold",
            "scope": "代理関係用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A016",
            "statement": "代理関係で principal と agent の権限付与側・行動側を逆転させてはならない。",
            "polarity": "must_not_hold",
            "scope": "代理関係の役割軸と反意関係"
          }
        ]
      },
      {
        "id": "FB-C009",
        "surface_form": "principal",
        "frame": "act or trade as principal rather than as agent",
        "meaning": "取引で他人の代理ではなく自己の計算・責任で当事者として行動する",
        "disposition": "excluded",
        "rationale": "act or trade as principal rather than as agent は代理人との対比から生じる専門的な取引上の拡張であり、独立した主要語義として追加しなくても代理関係の役割境界から理解できるため除外できる。",
        "semantic_assertions": [
          {
            "id": "FB-A017",
            "statement": "自己勘定取引で as principal と言う場合は、他人の agent としてではなく自己の計算・責任で行動する対比が中心となる。",
            "polarity": "must_hold",
            "scope": "取引上の文脈的拡張を説明する場合"
          },
          {
            "id": "FB-A018",
            "statement": "この取引表現を教育機関の長や元金の語義へ帰属させてはならない。",
            "polarity": "must_not_hold",
            "scope": "取引表現の語義境界"
          }
        ]
      },
      {
        "id": "FB-C010",
        "surface_form": "the principal",
        "frame": "the principal + be + directly responsible for a crime under applicable law",
        "meaning": "適用法の分類により犯罪について直接の刑事責任を負う関与者",
        "disposition": "included",
        "rationale": "the principal + be + directly responsible for a crime under applicable law は犯罪の物理的実行者だけに絶対化せず、法域依存の分類として記事の語義6に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A019",
            "statement": "刑事法上の principal の範囲は適用法の分類に従い、犯罪への一定の関与による直接責任を表す。",
            "polarity": "must_hold",
            "scope": "刑事法用法の定義、レジスター、注意"
          },
          {
            "id": "FB-A020",
            "statement": "すべての法域で principal が物理的実行者だけを指すと絶対化してはならない。",
            "polarity": "must_not_hold",
            "scope": "刑事法用法の一般化範囲"
          }
        ]
      },
      {
        "id": "FB-C011",
        "surface_form": "the principal",
        "frame": "the principal + be + primarily liable for a debt or obligation",
        "meaning": "保証人などと対比して義務に第一次的責任を負う主たる債務者・義務者",
        "disposition": "included",
        "rationale": "the principal + be + primarily liable for a debt or obligation は責任順位を表す債務・保証法の役割であり、金額を指す元金用法と分離して記事の語義7に含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A021",
            "statement": "債務・保証法上の principal は当該義務について第一次的責任を負う者を指す。",
            "polarity": "must_hold",
            "scope": "債務・保証法用法の定義、文法パターン、用例"
          },
          {
            "id": "FB-A022",
            "statement": "第一次的責任者を二次的責任を負う surety または guarantor と同一視してはならない。",
            "polarity": "must_not_hold",
            "scope": "債務・保証関係の責任順位軸"
          }
        ]
      },
      {
        "id": "FB-C012",
        "surface_form": "principally",
        "frame": "principally + verb, adjective, or clause",
        "meaning": "主として、主にという副詞派生",
        "disposition": "included",
        "rationale": "principally + verb, adjective, or clause は principal の重要性中心から規則的に派生する副詞であり、記事の語形成欄に principally として含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A023",
            "statement": "principally は『主として、主に』という割合または中心性を表す副詞派生である。",
            "polarity": "must_hold",
            "scope": "語形成欄"
          }
        ]
      },
      {
        "id": "FB-C013",
        "surface_form": "principalship",
        "frame": "the principalship of an institution",
        "meaning": "principal の地位・職、特に教育機関の長の職",
        "disposition": "included",
        "rationale": "the principalship of an institution は人物を表す principal から地位・職を作る規則的な名詞派生であり、記事の語形成欄に principalship として含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A024",
            "statement": "principalship は principal の役職またはその在職を表す名詞派生である。",
            "polarity": "must_hold",
            "scope": "語形成欄"
          }
        ]
      },
      {
        "id": "FB-C014",
        "surface_form": "principal-agent relationship",
        "frame": "a principal-agent relationship between principal and agent",
        "meaning": "本人と代理人の権限・行動関係を表す法律上の複合表現",
        "disposition": "included",
        "rationale": "a principal-agent relationship between principal and agent は語義5の役割対立を複合語に固定した表現で、記事の語形成欄と代理関係のコロケーションに含まれる。",
        "semantic_assertions": [
          {
            "id": "FB-A025",
            "statement": "principal-agent relationship は本人と、その本人のために行動する代理人との関係を表す。",
            "polarity": "must_hold",
            "scope": "語形成欄と代理関係用法"
          },
          {
            "id": "FB-A026",
            "statement": "複合表現内の principal と agent の意味役割を交換してはならない。",
            "polarity": "must_not_hold",
            "scope": "複合表現の構成要素と役割方向"
          }
        ]
      },
      {
        "id": "FB-C015",
        "surface_form": "principal",
        "frame": "principal rafter or another historically lexicalized technical noun",
        "meaning": "建築などで主部材を指す歴史的・限定的な名詞用法",
        "disposition": "excluded",
        "rationale": "principal rafter or another historically lexicalized technical noun は現代一般学習者向け記事で独立語義として必須となるほど中心的ではなく、形容詞 principal の専門的な限定用法として扱えるため除外できる。",
        "semantic_assertions": [
          {
            "id": "FB-A027",
            "statement": "歴史的・分野限定の部材名を扱う場合は、現代一般語の主要名詞用法と区別する。",
            "polarity": "must_hold",
            "scope": "稀な専門用法を追加する場合の語義境界"
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "normal-evidence-001",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "usage_notes",
          "line_start": 72,
          "line_end": 72,
          "exact_quote": "`principal` と `principle` は綴りも意味も異なる。`principal` には形容詞で「最も重要な」を表す用法があり、別に人や金額などを指す名詞用法もある。一方、`principle` は「原理・原則」を表す名詞である。したがって「基本原則」は `basic principle` であり、`basic principal` ではない。"
        },
        "severity": "blocking",
        "rationale": "C-013 links this whole usage note only to F-032 at the Merriam-Webster locator. F-032 directly supports the principle-as-rule versus principal-as-adjective distinction, but its recorded statement and source detail do not directly support the added claim that principal has noun uses for people and amounts, nor do they preserve the specific basic principle/basic principal substitution example. Those noun assertions are supported elsewhere in the inventory (for example C-002 and C-004), but they are not linked to usage_note:001, so the existing link's scope is narrower than the target claim.",
        "evidence_link_ids": [
          "C-013"
        ],
        "suggested_direction": "Limit the note to the distinction directly recorded by F-032, or bind the noun-use clauses to the relevant person and finance claim units and add direct support for the specific substitution example."
      },
      {
        "id": "normal-evidence-002",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 128,
          "line_end": 128,
          "exact_quote": "【文法パターン】組織上の地位は `a principal at 〈企業・専門組織〉`。教育上の役職は `the principal of 〈限定詞を含む学校・教育機関の名詞句〉`／`a school principal`／`a college principal`。"
        },
        "severity": "blocking",
        "rationale": "C-002 maps F-002, F-003, F-014, and F-017 to grammar_pattern:002. At the Merriam-Webster, Cambridge, and Collins locators, the fixed fact statements support the authority/person sense, the school-head title, and the England-college qualification. None of the recorded source details directly attests the promised business at-frame or establishes all three education constructions as grammatical frames. A lexical definition cannot by itself support these exact complements and compounds.",
        "evidence_link_ids": [
          "C-002"
        ],
        "suggested_direction": "Retain only constructions directly attested in the fixed facts, or add fixed fact records with locators and passages that explicitly show each proposed frame."
      },
      {
        "id": "normal-evidence-003",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 171,
          "line_end": 171,
          "exact_quote": "【文法パターン】舞台芸術の役職は `perform/serve as a principal with 〈舞台芸術団体〉`。オーケストラの役職は `one of 〈オーケストラを表す所有格〉 principals`。"
        },
        "severity": "blocking",
        "rationale": "C-003 links grammar_pattern:003 to F-007 and F-018. The Merriam-Webster and Collins facts directly establish the leading-performer and orchestral-section-player senses, but their recorded source details do not attest perform/serve as ... with or the possessive one-of-principals construction. The evidence therefore supports the role meaning, not the complete syntactic frames stated here.",
        "evidence_link_ids": [
          "C-003"
        ],
        "suggested_direction": "Replace the patterns with constructions explicitly present at the fixed locators, or hold the frame claims until direct construction evidence is recorded."
      },
      {
        "id": "normal-evidence-004",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 204,
          "line_end": 204,
          "exact_quote": "【文法パターン】金融では `principal and interest`／`pay down, protect, or repay + (the) principal`。信託法では `distinguish + principal + from + income`。"
        },
        "severity": "blocking",
        "rationale": "C-004 and C-005 map the finance and trust facts to grammar_pattern:004. The facts directly support the principal-versus-interest/income contrasts and F-024 supports repayment reducing the obligation. However, none of F-008, F-015, F-019, F-024, F-025, or F-027 at the listed dictionary, Wex, and Investor.gov locators records protect the principal as a supported collocation or validates the bundled verb-frame pay down, protect, or repay + (the) principal. The target is broader than the linked evidence even though its underlying senses are supported.",
        "evidence_link_ids": [
          "C-004",
          "C-005"
        ],
        "suggested_direction": "Remove protect from the bundled frame or supply a direct fixed fact for that collocation; keep the remaining patterns only to the extent their exact construction is attested."
      },
      {
        "id": "normal-evidence-005",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 294,
          "line_end": 294,
          "exact_quote": "【文法パターン】`a principal in 〈犯罪を表す名詞句〉`／`treat 〈人〉 as a principal`"
        },
        "severity": "blocking",
        "rationale": "C-007 links F-005 and F-021 to grammar_pattern:006. Those fixed Merriam-Webster and Collins facts support the jurisdiction-sensitive criminal-participant classification and the accessory contrast, but their recorded passages do not directly attest both complete syntactic frames. Treating the legal classification as evidence for the exact in-complement and treat-as constructions exceeds the recorded support.",
        "evidence_link_ids": [
          "C-007"
        ],
        "suggested_direction": "State only the supported legal sense, or add locator-specific facts that directly attest each construction before presenting them as grammar patterns."
      },
      {
        "id": "normal-evidence-006",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 327,
          "line_end": 327,
          "exact_quote": "【文法パターン】`be/remain liable as principal for 〈債務・義務〉`／`the obligation of the principal`／`the principal and the surety`"
        },
        "severity": "blocking",
        "rationale": "C-008 maps F-006, F-022, and F-026 to grammar_pattern:007. These facts at Merriam-Webster, Collins, and Wex directly support primary liability and the contrast with a surety or guarantor, but the fixed source details do not attest the full be/remain liable as principal for frame or all two noun-phrase patterns. The responsibility contrast supports the definition, not every specific construction bundled here.",
        "evidence_link_ids": [
          "C-008"
        ],
        "suggested_direction": "Narrow this section to phrases directly attested by the fixed evidence, or add fact records with exact passages for the proposed liability constructions."
      }
    ],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U-001",
        "source_fact_ids": [
          "F-001",
          "F-013",
          "F-016"
        ],
        "canonical_statement": "The adjective principal marks something first or especially high in importance, rank, or influence.",
        "disposition": "included",
        "rationale": "High-frequency adjective sense supported by three independent dictionaries."
      },
      {
        "id": "U-002",
        "source_fact_ids": [
          "F-002",
          "F-003",
          "F-014",
          "F-017"
        ],
        "canonical_statement": "Principal denotes a person in authority and conventionally the head of specified educational institutions, with regional title differences.",
        "disposition": "included",
        "rationale": "Major person noun and education title supported by current dictionary facts."
      },
      {
        "id": "U-003",
        "source_fact_ids": [
          "F-007",
          "F-018"
        ],
        "canonical_statement": "Principal can denote a leading performer, including a principal artist or orchestral section leader.",
        "disposition": "included",
        "rationale": "Established performing-arts noun use."
      },
      {
        "id": "U-004",
        "source_fact_ids": [
          "F-008",
          "F-015",
          "F-019",
          "F-024",
          "F-027"
        ],
        "canonical_statement": "Financial principal is the underlying debt, loan, or investment amount distinguished from interest, profit, or later earnings.",
        "disposition": "included",
        "rationale": "Major specialist sense corroborated by current general and government-specialist sources."
      },
      {
        "id": "U-005",
        "source_fact_ids": [
          "F-025"
        ],
        "canonical_statement": "Trust principal is the property or corpus distinguished from income earned by it.",
        "disposition": "integrated",
        "rationale": "Direct specialist extension of the finance/property sense."
      },
      {
        "id": "U-006",
        "source_fact_ids": [
          "F-004",
          "F-020",
          "F-023"
        ],
        "canonical_statement": "An agency principal authorizes an agent to act on the principal's behalf and is the source of the agent's authority; the US-law account in Wex also specifies the principal's control.",
        "disposition": "included",
        "rationale": "Important legal and economics role supported by two dictionaries, with the control element qualified to the Wex account."
      },
      {
        "id": "U-007",
        "source_fact_ids": [
          "F-005",
          "F-021"
        ],
        "canonical_statement": "Criminal-law principal denotes a person treated as a primary participant under the applicable legal classification.",
        "disposition": "included",
        "rationale": "Low-frequency but encounterable specialist legal use; scope is explicitly jurisdiction-sensitive."
      },
      {
        "id": "U-008",
        "source_fact_ids": [
          "F-006",
          "F-022",
          "F-026"
        ],
        "canonical_statement": "In obligation law, principal denotes the primarily liable party, contrasted with a secondarily liable surety or guarantor.",
        "disposition": "included",
        "rationale": "Directly supported specialist responsibility contrast."
      },
      {
        "id": "U-009",
        "source_fact_ids": [
          "F-009"
        ],
        "canonical_statement": "The adjective and noun principal share the pronunciation /ˈprɪnsəpəl/.",
        "disposition": "included",
        "rationale": "Pronunciation support for the entry."
      },
      {
        "id": "U-010",
        "source_fact_ids": [
          "F-010",
          "F-028"
        ],
        "canonical_statement": "Principal came through French from Latin principalis and princeps, with a semantic core of first or chief.",
        "disposition": "included",
        "rationale": "Etymology is supported by two references."
      },
      {
        "id": "U-011",
        "source_fact_ids": [
          "F-011"
        ],
        "canonical_statement": "Principalship is listed as a noun derivative of principal.",
        "disposition": "included",
        "rationale": "Recorded noun derivative."
      },
      {
        "id": "U-012",
        "source_fact_ids": [
          "F-012"
        ],
        "canonical_statement": "Principally is the adverb formed from principal.",
        "disposition": "included",
        "rationale": "Recorded adverb derivative."
      },
      {
        "id": "U-013",
        "source_fact_ids": [
          "F-032"
        ],
        "canonical_statement": "Principal and principle differ in spelling, parts of speech, and current meanings.",
        "disposition": "included",
        "rationale": "Major learner confusion directly addressed by dictionary usage guidance."
      },
      {
        "id": "U-014",
        "source_fact_ids": [
          "F-029",
          "F-030",
          "F-031"
        ],
        "canonical_statement": "Etymonline records historical attestation dates for chief-person, education-head, and money senses.",
        "disposition": "excluded",
        "rationale": "These historical facts are retained in the fixed inventory but are not used to support current lexical scope or grammar claims."
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
        "id": "core_image:006",
        "status": null,
        "notes": "",
        "target_id": "core_image:006"
      },
      {
        "id": "core_image:007",
        "status": null,
        "notes": "",
        "target_id": "core_image:007"
      },
      {
        "id": "core_image:008",
        "status": null,
        "notes": "",
        "target_id": "core_image:008"
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
        "id": "antonym:001",
        "status": null,
        "notes": "",
        "target_id": "antonym:001"
      },
      {
        "id": "antonym:002",
        "status": null,
        "notes": "",
        "target_id": "antonym:002"
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
        "id": "grammar_pattern:002",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:002"
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
        "id": "usage_note:002",
        "status": null,
        "notes": "",
        "target_id": "usage_note:002"
      },
      {
        "id": "synonym:005",
        "status": null,
        "notes": "",
        "target_id": "synonym:005"
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
        "id": "grammar_pattern:003",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:003"
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
        "id": "usage_note:003",
        "status": null,
        "notes": "",
        "target_id": "usage_note:003"
      },
      {
        "id": "synonym:006",
        "status": null,
        "notes": "",
        "target_id": "synonym:006"
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
        "id": "collocation:012",
        "status": null,
        "notes": "",
        "target_id": "collocation:012"
      },
      {
        "id": "usage_note:004",
        "status": null,
        "notes": "",
        "target_id": "usage_note:004"
      },
      {
        "id": "synonym:007",
        "status": null,
        "notes": "",
        "target_id": "synonym:007"
      },
      {
        "id": "sense_boundary:005",
        "status": null,
        "notes": "",
        "target_id": "sense_boundary:005"
      },
      {
        "id": "definition:005",
        "status": null,
        "notes": "",
        "target_id": "definition:005"
      },
      {
        "id": "frequency:005",
        "status": null,
        "notes": "",
        "target_id": "frequency:005"
      },
      {
        "id": "register:005",
        "status": null,
        "notes": "",
        "target_id": "register:005"
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
        "id": "usage_note:005",
        "status": null,
        "notes": "",
        "target_id": "usage_note:005"
      },
      {
        "id": "synonym:008",
        "status": null,
        "notes": "",
        "target_id": "synonym:008"
      },
      {
        "id": "antonym:003",
        "status": null,
        "notes": "",
        "target_id": "antonym:003"
      },
      {
        "id": "sense_boundary:006",
        "status": null,
        "notes": "",
        "target_id": "sense_boundary:006"
      },
      {
        "id": "definition:006",
        "status": null,
        "notes": "",
        "target_id": "definition:006"
      },
      {
        "id": "frequency:006",
        "status": null,
        "notes": "",
        "target_id": "frequency:006"
      },
      {
        "id": "register:006",
        "status": null,
        "notes": "",
        "target_id": "register:006"
      },
      {
        "id": "grammar_pattern:008",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:008"
      },
      {
        "id": "collocation:015",
        "status": null,
        "notes": "",
        "target_id": "collocation:015"
      },
      {
        "id": "usage_note:006",
        "status": null,
        "notes": "",
        "target_id": "usage_note:006"
      },
      {
        "id": "synonym:009",
        "status": null,
        "notes": "",
        "target_id": "synonym:009"
      },
      {
        "id": "sense_boundary:007",
        "status": null,
        "notes": "",
        "target_id": "sense_boundary:007"
      },
      {
        "id": "definition:007",
        "status": null,
        "notes": "",
        "target_id": "definition:007"
      },
      {
        "id": "frequency:007",
        "status": null,
        "notes": "",
        "target_id": "frequency:007"
      },
      {
        "id": "register:007",
        "status": null,
        "notes": "",
        "target_id": "register:007"
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
        "id": "collocation:016",
        "status": null,
        "notes": "",
        "target_id": "collocation:016"
      },
      {
        "id": "collocation:017",
        "status": null,
        "notes": "",
        "target_id": "collocation:017"
      },
      {
        "id": "usage_note:007",
        "status": null,
        "notes": "",
        "target_id": "usage_note:007"
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
        "id": "antonym:004",
        "status": null,
        "notes": "",
        "target_id": "antonym:004"
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
        "id": "sense_definition_consistency:002",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:002"
      },
      {
        "id": "definition_usage_consistency:002",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:002"
      },
      {
        "id": "definition_lexical_relation_consistency:002",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:002"
      },
      {
        "id": "pattern_example_coverage:002",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:002"
      },
      {
        "id": "sense_definition_consistency:003",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:003"
      },
      {
        "id": "definition_usage_consistency:003",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:003"
      },
      {
        "id": "definition_lexical_relation_consistency:003",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:003"
      },
      {
        "id": "pattern_example_coverage:003",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:003"
      },
      {
        "id": "sense_definition_consistency:004",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:004"
      },
      {
        "id": "definition_usage_consistency:004",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:004"
      },
      {
        "id": "definition_lexical_relation_consistency:004",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:004"
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
        "id": "sense_definition_consistency:005",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:005"
      },
      {
        "id": "definition_usage_consistency:005",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:005"
      },
      {
        "id": "definition_lexical_relation_consistency:005",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:005"
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
        "id": "sense_definition_consistency:006",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:006"
      },
      {
        "id": "definition_usage_consistency:006",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:006"
      },
      {
        "id": "definition_lexical_relation_consistency:006",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:006"
      },
      {
        "id": "pattern_example_coverage:008",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:008"
      },
      {
        "id": "sense_definition_consistency:007",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:007"
      },
      {
        "id": "definition_usage_consistency:007",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:007"
      },
      {
        "id": "definition_lexical_relation_consistency:007",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:007"
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
        "id": "core_sense_mapping:005",
        "status": null,
        "notes": "",
        "relation_id": "core_sense_mapping:005"
      },
      {
        "id": "core_sense_mapping:006",
        "status": null,
        "notes": "",
        "relation_id": "core_sense_mapping:006"
      },
      {
        "id": "core_sense_mapping:007",
        "status": null,
        "notes": "",
        "relation_id": "core_sense_mapping:007"
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
        "id": "FB-C001",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A001",
          "FB-A002"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A001",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A002",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C002",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A003",
          "FB-A004"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A003",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A004",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C003",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A005",
          "FB-A006"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A005",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A006",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C004",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A007",
          "FB-A008"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A007",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A008",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C005",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A009",
          "FB-A010"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A009",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A010",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C006",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A011",
          "FB-A012"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A011",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A012",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C007",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A013",
          "FB-A014"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A013",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A014",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C008",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A015",
          "FB-A016"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A015",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A016",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C009",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A017",
          "FB-A018"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A017",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A018",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C010",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A019",
          "FB-A020"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A019",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A020",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C011",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A021",
          "FB-A022"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A021",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A022",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C012",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A023"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A023",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C013",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A024"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A024",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C014",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A025",
          "FB-A026"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A025",
            "status": null,
            "notes": ""
          },
          {
            "id": "FB-A026",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "FB-C015",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "FB-A027"
        ],
        "verified_body_sha256": "f54ace66c12f4781a172fbc2c1411245def9fed82b18b54471a45218306679b4",
        "assertion_results": [
          {
            "id": "FB-A027",
            "status": null,
            "notes": ""
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "normal-evidence-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-evidence-002",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-evidence-003",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-evidence-004",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-evidence-005",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-evidence-006",
        "status": null,
        "notes": ""
      }
    ],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U-001",
        "status": null,
        "notes": "",
        "union_id": "U-001"
      },
      {
        "id": "U-002",
        "status": null,
        "notes": "",
        "union_id": "U-002"
      },
      {
        "id": "U-003",
        "status": null,
        "notes": "",
        "union_id": "U-003"
      },
      {
        "id": "U-004",
        "status": null,
        "notes": "",
        "union_id": "U-004"
      },
      {
        "id": "U-005",
        "status": null,
        "notes": "",
        "union_id": "U-005"
      },
      {
        "id": "U-006",
        "status": null,
        "notes": "",
        "union_id": "U-006"
      },
      {
        "id": "U-007",
        "status": null,
        "notes": "",
        "union_id": "U-007"
      },
      {
        "id": "U-008",
        "status": null,
        "notes": "",
        "union_id": "U-008"
      },
      {
        "id": "U-009",
        "status": null,
        "notes": "",
        "union_id": "U-009"
      },
      {
        "id": "U-010",
        "status": null,
        "notes": "",
        "union_id": "U-010"
      },
      {
        "id": "U-011",
        "status": null,
        "notes": "",
        "union_id": "U-011"
      },
      {
        "id": "U-012",
        "status": null,
        "notes": "",
        "union_id": "U-012"
      },
      {
        "id": "U-013",
        "status": null,
        "notes": "",
        "union_id": "U-013"
      },
      {
        "id": "U-014",
        "status": null,
        "notes": "",
        "union_id": "U-014"
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
        "id": "evidence",
        "pass_id": "evidence",
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
        "id": "pronunciation",
        "pass_id": "pronunciation",
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
    "pass_findings.json": "85dd31e8fd8560f855a7b589a312b74d3404f95441a1951839ef8c1deb80fcdd",
    "cold_review.json": "63598185c7a2e8c1d6f6c8b7f292d24662242259d02879578216f70fdc330466",
    "final_blind.json": "4014793983931bc282a1e2c606b86e047f047d5b1d306673b43ba1ddf85aca65",
    "blind_seal.json": "9f8de37d0b2ad10aebdc98bf7c0cd45a94b2869ec655da69345ed2f745380bed",
    "pre_blind_resolution.json": "dfefbcef995d986f609c5f55facbaa165fd6913428c3bae8b6a02e76fd045105",
    "pre_blind_revision.json": "204bde5ad67a48cf36bc952dbd1bb0ec87e8fb4687b571b41689c37c089fe5fc",
    "checker_recheck_manifest.json": "44f1baa6f89a6680a5f414da3f89da083f9b00425995245e5cbf7c735aea42b8",
    "post_blind_resolution.json": "7dc2f920057bc5fa6ac3d76f75e2d66c3a0b209dd3c849f5a7dcb88dd57d0e51",
    "post_blind_verification.json": "9469da3210430f78ff59ccfd5b47865d967456e437205326fe940be0c5c8322f",
    "targeted_adjudications.json": "170bcecc13fe9ab6439407fcebba3dfef9a7160d4f7ac76c211d38cd5d161b80",
    "source_inventory.json": "39be89d772eb4ed8394a39c8a80a58cc08b261c8f374a86fbe4fac2abca7a5f6",
    "resolutions.json": "268f6be75ecf429750bff72738a9e12166a7590525ba85686b7cafca03230e20",
    "check_passes/checker_passes.stage1.json": "83301f25cffc1e0c36f82ad195944151d31bfe745b70ce92e7da2d037c557bf8",
    "check_passes/evidence.json": "e8aa1c88fbafd9005fd160f037fe22e36db5eb60a956d4ce0c3d295e3eee51f5",
    "check_passes/evidence.request.json": "45fd24b8306a3ae9fa42fcf0c9125a6bdf4aee69049e41cfcc64d28617ded21d",
    "check_passes/example-attribution.alignment-key.json": "18bd27a30b994ae6c2bc216c35a498e6479ac0217534db980c112d18703aeeb9",
    "check_passes/example-attribution.blind-record.json": "29e21dc974f9a9e03e314c6ba2a28f7e09c26d935b4d43454d26b999836bd096",
    "check_passes/example-attribution.json": "15accc5ecbd0c7c7ccee9f5b5e6b7f573f3393bb5e25e4064e92d28b4c31d067",
    "check_passes/example-attribution.request.json": "e39825d2afadf65c8d4916cac251f375bfc1542ba72d3ad6c84a420188989813",
    "check_passes/frame-relation.antonym-axis.adjudication-record.json": "ea99e1202f2af62e3773e102cf9200751dd5f68070e70374fcf9460925a16f2e",
    "check_passes/frame-relation.antonym-axis.alignment-key.json": "52d166573dfcb252c3eaeb1f64d0cd0f2bb78961aaf0e332798c24179e79a2c9",
    "check_passes/frame-relation.antonym-axis.blind-record.json": "541ca5e1fd4671a14eabc54bf836d1971398ba273cc8aa22401e8b1463900069",
    "check_passes/frame-relation.antonym-axis.stage2.request.json": "9c55d251c6502a051b35de95629aea081108d7f3edb3e46379b4d002a2eed382",
    "check_passes/frame-relation.request.json": "df4cbcd070f8bd7aa2dfe9d43b99d01f95d68ca0fadfbf1e3f137ee21157f92b",
    "check_passes/input_snapshot.json": "bdf401e4a918bb5651b8b58e5f1b6cb60fde601d87fea8def02acba6c9decd5e",
    "check_passes/pronunciation.json": "c71da17af4dabed98471bbda1b953130633a115ba6345d6e94ebfda7600d1516",
    "check_passes/pronunciation.request.json": "0d2c1312cdd4a323e0e58e1debb862677d9204b162f8e862821c10fd5143a9d9",
    "check_passes/qualification.json": "ef719eed52a4705f4933442a21c31efad9072d7f342135520adbeb7bc11f23df",
    "check_passes/qualification.request.json": "f6770599631226f6db7484b7abe16d356ccc3e661fb734cd8cd62219b48a949d",
    "check_passes/sense-structure.json": "b6aae3181824c5e8678deeb10221d66b64fa705e453e130cfb5b5f8907fc386a",
    "check_passes/sense-structure.request.json": "b7d58fabb3c7c05e6c6f08d9351fd8900f40eaafbb9eb571b5753dbe48894004",
    "check_passes/translation.json": "d2502a906fb2ffe0b527f3609e70fd7790714eb051e335e4bb366efed2fb0382",
    "check_passes/translation.request.json": "0cc921bb5dcced0cbe361af19476fb6a5142b76298c63f44b493990d98c40593",
    "recheck/checker_recheck.stage1.json": "3e77b79ad32fb9a0e0cbf2ad8f214cd06b834a27af370e0a89f1a75ee1f99700",
    "recheck/evidence.json": "094205f2c2c7c8f779d1ce0532245a03717810c9c9e42f7fb1afb58dd3c8f325",
    "recheck/evidence.request.json": "fe58d664889669fb33797186ed6f7b81aea837f07742c997392cd7bd9e24f5e5",
    "recheck/evidence.response.json": "094205f2c2c7c8f779d1ce0532245a03717810c9c9e42f7fb1afb58dd3c8f325",
    "recheck/example-attribution.alignment-key.json": "238df7c968734d0c7f55ec2983f92e5ebdc93bdf4420cc0569d3888a4f7d14a5",
    "recheck/example-attribution.blind-record.json": "ff1c84af1511f6b8635127fa80d89a6c66fc196c36eafbdd4942b4bac894240c",
    "recheck/example-attribution.json": "9baea2c40db31b18e2fbf356f40307a7c6a3db512c927f7e553f90a1cd958ee2",
    "recheck/example-attribution.request.json": "7190555b41f420cff822586de67b87fb9a2ffc5f3dc5150e10b35051ac96fb2a",
    "recheck/example-attribution.response.json": "3e97532810dcf2090296712047d96ee236600566c4bb3720cec372849dc38117",
    "recheck/frame-relation.antonym-axis.alignment-key.json": "de5ea5b8afd201092b488410ab5a83d8d6ecd2b3ab0ae0a7f03c354f3b1c9740",
    "recheck/frame-relation.antonym-axis.blind-record.json": "38f336fe57f1966f1e891666e39d509dcfbd291e06a2a7e0289d8ffe3084785b",
    "recheck/frame-relation.json": "1ca8d2dad3c8240245824dd61f3f1ef80f93a8a9d8f1e57005629bce4da1cb61",
    "recheck/frame-relation.request.json": "1134efac244d58d6fe34578a494d63758534bc6cb9dd00f1f5f445c5522e412c",
    "recheck/frame-relation.stage2.request.json": "cb54f83305fde7e7ada3c89b221a8bbb57548209e3d60f0ed3e8a2cea9e47da5",
    "recheck/frame-relation.stage2.response.json": "d6d14c11d94df0345d94adf4e370508f568c72a3fd54be4ff8c15631466cfea3",
    "recheck/input_snapshot.json": "e83efaad624cab2d192eaf722b22b409da3feac4ac7d822ecad67984b256b587",
    "recheck/pronunciation.request.json": "087036a99be407d8cc9989d9639b78f453d05c6822c510a20e42ab2ce52737a0",
    "recheck/pronunciation.reuse.json": "e73183231f3e91faa96c62724e142a947860c4fa673480e82cd3a3706894c13c",
    "recheck/qualification.json": "ef719eed52a4705f4933442a21c31efad9072d7f342135520adbeb7bc11f23df",
    "recheck/qualification.request.json": "44fff666700a7b7d34865b1c9316d553a8b1ebbadae460e0b9132b44b9ebd498",
    "recheck/qualification.response.json": "ef719eed52a4705f4933442a21c31efad9072d7f342135520adbeb7bc11f23df",
    "recheck/resolutions.json": "753fdad20f69eb3625fa9be6d1c8a53c8f11af43ac435aa372f8c54386abde11",
    "recheck/revision_plan.findings.json": "bbed08a05bc2ae50294591121707437529085011ca97b717bb7c9dfa84a09ce2",
    "recheck/sense-structure.json": "b6aae3181824c5e8678deeb10221d66b64fa705e453e130cfb5b5f8907fc386a",
    "recheck/sense-structure.request.json": "5570a6cebf5aa5a7d3dc73c22ac8c18c92b67efbeccd15423faa1f5d844b30e6",
    "recheck/sense-structure.response.json": "b6aae3181824c5e8678deeb10221d66b64fa705e453e130cfb5b5f8907fc386a",
    "recheck/translation.json": "89b32673a6c9858f1127f4d27341abe24fd073346cb5617692d7408171df88ef",
    "recheck/translation.request.json": "173adf32423c3bdbd13396c3346e63398dd191d3c43e3184b847ee04c3624816",
    "recheck/translation.response.json": "89b32673a6c9858f1127f4d27341abe24fd073346cb5617692d7408171df88ef"
  },
  "contract_version": "review_preflight_v1"
}
```
