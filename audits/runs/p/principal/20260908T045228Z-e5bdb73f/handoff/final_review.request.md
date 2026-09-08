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
  "entry_body": "\n＃発音記号\n\n発音: /ˈprɪnsəpəl/。形容詞と名詞で同じ発音を用いる。  \n\n＃語源\n\n中英語・古フランス語を経て、ラテン語 *principalis*「第一の、主要な」にさかのぼる。その基になった *princeps* は、*primus*「第一の」と *capere*「取る」に関係し、「第一の位置を占める者」という発想を持つ。語源には「第一の、主要な」という意味的なつながりがある。  \n同語源語には `prince`「王子、君主」と `principality`「公国」がある。綴りのよく似た `principle`「原理、原則」も同じラテン語群に由来するが、現代英語では別の単語として使い分ける。  \n\n＃語形成\n\n・principally：`principal` の副詞形。  \n・principalship：`principal` の名詞派生形。  \n・principal-agent relationship：法律上の本人・代理人関係を表す複合表現。  \n\n＃コアイメージ\n\n`principal` の中心は、「重要度・権限・責任・金額の土台として第一に位置する」である。形容詞では主要なものを選び出し、名詞では組織・活動の主要人物や取引の当事者本人、教育機関の長や舞台芸術で確立した主要演者、利息・収益に対する元の金額や信託収益に対する財産本体、法的関係の主要当事者を指す。  \n・重要度で第一に位置するもの → 「主要な、最も重要な」（語義1）  \n・組織・活動・取引で主要な立場にある人、特に教育機関の長 → 「主要人物・当事者、校長、学長」（語義2）  \n・利息・収益に対する基礎額、または信託収益に対する財産本体 → 「元金、元本、信託元本」（語義3）  \n・代理関係で権限の源として第一に位置する当事者 → 「本人、依頼者」（語義4）  \n・舞台芸術で主要な役割を担う人 → 「主要演者、オーケストラの首席奏者」（語義5）  \n・適用法上 `principal` と分類される犯罪関与者 → 「犯罪関与者」（語義6）  \n・債務・保証関係で第一次的責任を負う者 → 「主たる債務者・義務者」（語義7）  \n\n＃意味・用法・関連表現\n\n1. 【形容詞】主要な、最も重要な、第一の\n\n【日本語訳・定義】複数の原因、目的、人物、場所、要素などの中で、重要度・影響力・順位が最も高い、または特に高いものを示す。単に時間的に最初という意味ではなく、重要性や中心性の評価を表す。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準～やや形式的。報道、ビジネス、学術、行政で広く使う。日常会話では `main` がより普通なことが多い。  \n\n【文法パターン】限定用法で `principal + 〈名詞〉` の形を取り、「主要な～」を表す。  \n\n【コロケーション】\n\n・`the principal reason for ...`  \n用途: 出来事・状況・判断・行動などについて、最も重要な理由を示す。  \n例: The principal reason for the delay was a shortage of parts.  \n訳: 遅延の主な理由は部品不足だった。  \n\n・`the principal cause of ...`  \n用途: 出来事を引き起こした最も重要な原因を示す。  \n例: Investigators identified corrosion as the principal cause of the failure.  \n訳: 調査担当者は、腐食をその故障の主因と特定した。  \n\n・`a principal source of ...`  \n用途: 物・情報・収入などの主要な供給源を示す。  \n例: Tourism is a principal source of income for the island.  \n訳: 観光はその島の主要な収入源の一つである。  \n\n・`one of the principal 〈複数名詞〉`  \n用途: 最重要候補が複数ある中の一つであることを示す。  \n例: She is one of the principal architects of the reform.  \n訳: 彼女はその改革の主要な立案者の一人である。  \n\n・`the principal place of business`  \n用途: 企業の主たる事業所を指す定着した法律・ビジネス表現。該当場所を決める法的基準や効果は、適用される法や法域によって異なる。  \n例: The company moved its principal place of business to Osaka.  \n訳: その会社は主たる事業所を大阪に移した。  \n\n【語法・注意】`principal` と `principle` は綴りも意味も異なる。`principal` には形容詞で「最も重要な」を表す用法があり、別に人や金額などを指す名詞用法もある。一方、`principle` は「原理・原則」を表す名詞である。したがって「基本原則」は `basic principle` であり、`basic principal` ではない。  \n\n【類義語】\n\n・main  \n定義: 複数のものの中で中心的・最重要である。  \n頻度: 〈10/10〉  \n違い: `main` は日常語で範囲が広い。`principal` はより形式的で、順位・重要性・影響力が高いことを意識させる。  \n例: Our main goal is to reduce waiting times.  \n訳: 私たちの主な目標は待ち時間を減らすことだ。  \n\n・primary  \n定義: 第一順位・第一段階である、または最も基本的である。  \n頻度: 〈9/10〉  \n違い: `primary` は重要性に加え、順序・段階・基本性にも焦点を置ける。`principal` は主として相対的な重要度や地位を表す。  \n例: Safety is our primary concern.  \n訳: 安全が私たちの最優先事項である。  \n\n・chief  \n定義: 同種の中で最上位・最重要である。  \n頻度: 〈8/10〉  \n違い: `chief` は役職名や「最大の原因・懸念」によく使われ、最上位性を強く示す。`principal` は文章語として原因・目的・人物・場所などに幅広く使う。  \n例: Cost remains the chief obstacle to expansion.  \n訳: 費用が依然として拡大の最大の障害である。  \n\n・leading  \n定義: ある分野で先頭に立ち、大きな影響力や高い評価を持つ。  \n頻度: 〈9/10〉  \n違い: `leading` は人・企業・研究機関などの実績や影響力を強調しやすい。`principal` は実績評価を必須とせず、対象内での中心性を示す。  \n例: She is a leading expert on marine ecosystems.  \n訳: 彼女は海洋生態系の第一人者である。  \n\n【反意語】\n\n・secondary  \n定義: 第一ではなく、重要度・順位が二次的である。  \n頻度: 〈8/10〉  \n違い: 重要度・順位の軸で `principal` と方向が反対になり、主要なものに対する従属的・補助的なものを表す。  \n例: Price was only a secondary consideration.  \n訳: 価格は二次的な考慮事項にすぎなかった。  \n\n・minor  \n定義: 重要性・規模・影響が比較的小さい。  \n頻度: 〈9/10〉  \n違い: `principal` との程度軸上の対立で、最重要・主要ではない小さな要素を表す。  \n例: The report contains a few minor errors.  \n訳: その報告書には小さな誤りがいくつかある。  \n\n2. 【名詞・可算】主要人物・当事者；特に校長、学長\n\n【日本語訳・定義】組織・事業・交渉などで主導的地位を持つ人、または行為・取引の主要な当事者。権限を持つ人を指すことが多いが、組織を支配することを必須とはしない。特に教育では、学校、カレッジ、その他の教育機関を管理する最高責任者を指す。教育上どの種類の機関を指すかは地域と制度によって異なる。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】標準～やや形式的。教育分野では学校・教育機関の長を表し、イングランドではカレッジの長を指す場合がある。  \n\n【文法パターン】可算名詞として、組織・活動の主要人物や取引の当事者を指す。`act as principal` は取引の当事者本人の資格で行動することを表す。教育文脈では学校・カレッジなどの長を表す役職名として用いる。  \n\n【コロケーション】\n\n・`the principal of 〈限定詞を含む学校・教育機関の名詞句〉`  \n用途: どの教育機関の長かを `of` で示す。  \n例: The principal of the college welcomed the new students.  \n訳: そのカレッジの学長は新入生を歓迎した。  \n\n・`a school principal`  \n用途: 学校を管理する責任者を職種として表す。  \n例: The school principal met with parents after the incident.  \n訳: 校長はその出来事の後、保護者と面会した。  \n\n・`a college principal`  \n用途: カレッジを管理する責任者を職種として表す。  \n例: A college principal addressed the graduating class.  \n訳: カレッジの学長が卒業生に向けて話した。  \n\n・`act as principal`  \n用途: 他者の代理人としてだけではなく、取引の当事者本人の資格で行動することを表す。  \n例: In this transaction, the firm acts as principal, buying the goods for its own account rather than as another company's agent.  \n訳: この取引では、その会社は当事者本人として行動し、別会社の代理人としてではなく自己の勘定で商品を購入する。  \n\n【語法・注意】一般の「重要人物」を自由に指す語ではなく、特定の組織・活動・取引で主要な立場にある人や当事者に用いる。取引の `principal` は当事者本人の立場を示し、自分が代理人を任命していることを必須としない。代理人との関係で権限の源となる本人は語義4で詳しく扱う。教育上の役職名は地域や制度によって異なるため、日本語の「校長」を機械的にすべて `principal` としない。  \n\n【類義語】\n\n・head  \n定義: 学校・組織などの長。  \n頻度: 〈9/10〉  \n違い: `head` は組織の長を広く表す。`principal` は権限・主導的地位を持つ人を表し、特に教育機関で役職名として用いられる。  \n例: She is the head of a large secondary school.  \n訳: 彼女は大規模な中等学校の校長である。  \n\n3. 【名詞・金融／信託法】元金、元本、信託財産の元本\n\n【日本語訳・定義】借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。信託法では、収益と区別される信託財産そのもの、すなわち信託元本・corpusを指す。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】金融、融資、投資、会計、信託法。金融義は日常的なローン説明にも現れ、信託義は専門的である。  \n\n【文法パターン】金融では利息・収益の基礎となる金額を、信託法では収益と区別される財産本体を表す名詞として用いる。  \n\n【コロケーション】\n\n・`principal and interest`  \n用途: 借入金の元金と、それに対して発生する利息を対で示す。  \n例: The monthly payment includes both principal and interest.  \n訳: 毎月の返済額には元金と利息の両方が含まれる。  \n\n・`pay down the principal`  \n用途: 返済によって未返済の元金を減らすことを表す。  \n例: Extra payments can help you pay down the principal faster.  \n訳: 追加返済をすれば、元金をより早く減らせる。  \n\n・`protect the principal`  \n用途: 投資で、元本そのものの毀損を避けることを表す。  \n例: The fund aims to protect the principal—the amount originally invested—while generating modest returns.  \n訳: そのファンドは、控えめな収益を生みながら元本、すなわち当初の投資額を保全することを目指している。  \n\n・`repay principal`  \n用途: 利息とは別に借入の元金を返済することを表す。  \n例: The borrower will begin repaying principal next year.  \n訳: 借り手は来年、元金の返済を開始する。  \n\n【語法・注意】`principal` は元の基礎額、`interest` は借入の対価または貸付・投資から生じる追加額であり、反意語ではなく関連する別の金額構成要素である。信託では `principal` が財産本体、`income` がそこから生じる収益を指す。`repay the principal` では `principal` 自体が目的語の名詞になる。日本語の「元利金」は `principal and interest` であり、`principal interest` とはしない。  \n\n【類義語】\n\n・capital  \n定義: 投資・事業に用いられる資金または資産。  \n頻度: 〈9/10〉  \n違い: `capital` は事業資金・生産資産まで広く表す。`principal` は特定の貸付・借入・投資で利息や収益の基礎となる元の額を指す。  \n例: The company raised additional capital from investors.  \n訳: その会社は投資家から追加資金を調達した。  \n\n4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者\n\n【日本語訳・定義】別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。具体的な成立要件は適用法によって異なり得る。  \n\n【頻度】〈5/10〉  \n\n【レジスター/領域】法律、保険、不動産、商取引。日常語として人を「依頼主」と呼ぶだけなら `client` が自然な場合も多い。  \n\n【文法パターン】`a principal-agent relationship`＝本人・代理人関係／`act on behalf of the principal`＝本人を代理して行動する  \n\n【コロケーション】\n\n・`a principal-agent relationship`  \n用途: 権限を与える本人と、そのために行動する代理人との関係を表す。  \n例: The contract created a principal-agent relationship between the owner and the broker.  \n訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。  \n\n・`act on behalf of the principal`  \n用途: 代理人が本人を代理して行動することを表す。  \n例: The agent may sign the document on behalf of the principal.  \n訳: 代理人は本人を代理してその書類に署名できる。  \n\n【語法・注意】法律用語の `principal` は「重要人物」という一般義だけでなく、`agent` に対する特定の関係上の役割名である。`client` はサービスを受ける顧客・依頼人を広く指すが、必ずしも代理権を与える法律上の本人ではない。`the principal's agent` は「本人の代理人」であり、「校長の代理人」と決めつけない。  \n\n【類義語】\n\n・mandator  \n定義: 他人に委任・代理の権限を与える者。  \n頻度: 〈2/10〉  \n違い: 特定の法体系や専門文脈で使われる低頻度語である。  \n例: The mandator may revoke the mandate subject to the agreement.  \n訳: 委任者は、契約の定めに従い、委任を撤回できる。  \n\n5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者\n\n【日本語訳・定義】舞台芸術で主要な役を担う演者、またはオーケストラで一つのセクションを率いる奏者。一般の重要人物ではなく、芸術分野で確立した役割名を指す。  \n\n【頻度】〈3/10〉  \n\n【レジスター/領域】舞台芸術・オーケストラ・音楽の専門語。  \n\n【文法パターン】可算名詞として、舞台芸術・音楽で確立した主要演者や首席奏者の役割を表す。  \n\n【コロケーション】\n\n・`one of the orchestra's principals`  \n用途: オーケストラで各セクションを率いる奏者を名詞で指す。  \n例: As one of the orchestra's principals, she leads the cello section.  \n訳: オーケストラの首席奏者の一人として、彼女はチェロのセクションを率いている。  \n\n【語法・注意】舞台芸術やオーケストラ内で確立した役割名として用い、一般の「重要人物」には広げない。  \n\n【類義語】\n\n・section leader  \n定義: オーケストラで一つのセクションを率いる奏者。  \n頻度: 〈4/10〉  \n違い: 役割を説明する一般的な表現で、`principal` は確立した役職名として用いられる。  \n例: The section leader rehearsed the difficult passage.  \n訳: セクションの首席奏者は難しい楽節を練習した。  \n\n6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者\n\n【日本語訳・定義】刑事法の文脈で、犯罪を実行する者、または適用される分類の下で犯罪への一定の関与により直接の刑事責任を負う者。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】刑事法の専門語。犯罪に関するこの語義は法域によって分類法が異なる。  \n\n【文法パターン】刑事法で可算名詞として用い、犯罪関与者を適用される法的分類に従って指す。  \n\n【コロケーション】\n\n・`a principal in a crime`  \n用途: 犯罪について直接の刑事責任を負う者を指す。  \n例: The court held him directly criminally liable as a principal in the crime, rather than classifying him as an accessory.  \n訳: 裁判所は彼をその犯罪の `accessory` と分類するのではなく、`principal` として直接の刑事責任を負うものとした。  \n\n・`treat someone as a principal`  \n用途: 一定の関与者を適用法上 `principal` として扱うことを表す。  \n例: The statute treats a person who knowingly assists the offense as a principal.  \n訳: その制定法は、情を知って犯罪を援助する者を `principal` として扱う。  \n\n【語法・注意】刑事法の `principal` は適用される法的分類に従う役割名で、`accessory` と対比される。債務・保証関係の第一次的責任者は別の語義7である。  \n\n【類義語】\n\n・perpetrator  \n定義: 犯罪・不正行為を実際に行った者。  \n頻度: 〈6/10〉  \n違い: `perpetrator` は実行者に焦点を置く一般的な法律・報道語。`principal` は適用される法的分類によって、実行者以外の一定の関与者を含む場合がある。  \n例: Police are still trying to identify the perpetrator.  \n訳: 警察は今も犯人の特定を進めている。  \n\n7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者\n\n【日本語訳・定義】債務・保証の文脈で、保証人などの二次的責任者と対比され、義務について第一次的に責任を負う人または法人。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】債務法・保証法の専門語。  \n\n【文法パターン】可算名詞として、保証人・`surety`・`guarantor` と対比される第一次的責任者を指す。  \n\n【コロケーション】\n\n・`be liable as principal`  \n用途: 二次的な保証責任ではなく、主たる当事者として第一次的責任を負うことを示す。  \n例: Under the agreement, the company remains liable as principal for the debt, while the guarantor is only secondarily liable.  \n訳: その契約の下で、会社はその債務について主たる当事者として引き続き責任を負い、保証人は二次的にのみ責任を負う。  \n\n・`the obligation of the principal`  \n用途: 主たる当事者が第一次的に負う義務を示す。  \n例: The obligation of the principal is to repay the debt; the guarantor is only secondarily liable.  \n訳: 主たる義務者の義務は債務を返済することであり、保証人は二次的にのみ責任を負う。  \n\n・`the principal and the surety`  \n用途: 第一次的責任を負う当事者と、保証する側を対で示す。  \n例: Under the agreement, the principal and the surety are primarily and secondarily liable for the debt, respectively.  \n訳: その契約の下で、主たる義務者と保証人は、その債務についてそれぞれ第一次的責任と二次的責任を負う。  \n\n【語法・注意】この語義では、`principal` は `be liable as principal` のように人・法人を指す名詞である。`principal debtor` や `principal obligor` では語義1の形容詞が `debtor`・`obligor` を修飾するため、名詞単独の構造と区別する。また、金額を指す語義3の「元金」とも区別する。  \n\n【類義語】\n\n・obligor  \n定義: 契約や法律上の義務を負う者。  \n頻度: 〈3/10〉  \n違い: `obligor` は義務を負う者を広く表す。`principal` は保証人などと対比して、その義務について第一次的に責任を負う側を示す。  \n例: The obligor must perform the duty by the stated date.  \n訳: 義務者は定められた日までに義務を履行しなければならない。  \n\n・debtor  \n定義: 金銭その他の債務を負う者。  \n頻度: 〈6/10〉  \n違い: `debtor` は債務者一般を指す。`principal` は保証関係で第一次的責任を負う当事者という役割を強調する。  \n例: The debtor made the payment on time.  \n訳: 債務者は期限どおりに支払った。  ",
  "_output_metadata": {
    "schema_version": "final_review_v2",
    "stage": "final_review",
    "run_id": "blind-principal-20260908T045228Z-e5bdb73f",
    "context_id": "blind-principal-context-20260908T045228Z-e5bdb73f",
    "input_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
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
    "blind_output_sha256": "c716b5a23c9bd56fb0631dc6129f4ff9f21897df7f209d4eaaec428f0c77d65b"
  },
  "pass_findings": {
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-principal-20260908T045228Z-e5bdb73f",
    "context_id": "normal-principal-context-20260908T045228Z-e5bdb73f",
    "input_body_sha256": "bef5bc3e080249e45970356cb808049daba9970c09685b874ac37c61208b6bbf",
    "prompt_sha256": "5178f5a14a9525317811a34e6cd307108436f4babc1299fcd2eb9031f28ba737",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-09-08T05:41:52.222294+00:00",
    "pass_outputs": [
      {
        "pass_id": "translation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "principal-cycle2-translation-1"
        },
        "findings": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "sense-structure",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "principal-cycle2-sense-structure-1"
        },
        "findings": [
          {
            "taxonomy_id": "sense_boundary_overlap",
            "location": {
              "section": "sense_structure",
              "line_start": 128,
              "line_end": 128,
              "exact_quote": "【日本語訳・定義】学校、カレッジ、その他の教育機関を管理する最高責任者。どの種類の教育機関を指すかは地域と制度によって異なる。  "
            },
            "severity": "blocking",
            "rationale": "固定済み source union の U-002 は、教育機関の長だけでなく、組織で支配的権限または主導的地位を持つ人物という名詞用法も収録対象としている。しかし語義2は教育機関の最高責任者に限定され、他の番号付き名詞語義もこの一般的な権限・主導者用法を受け入れない。コアイメージ本文の「組織や行為の中心人物」に対応する収録先も学校・オーケストラ以外にはなく、主要な名詞候補が語義構造から欠落している。",
            "evidence_link_ids": [
              "F-002",
              "F-003",
              "F-014",
              "F-017"
            ],
            "suggested_direction": "人物を指す一般的な権限・主導者用法を、教育機関の役職名と学習上区別できる番号付き語義として追加するか、語義2をその用法まで明示的に含む構造へ再編し、コアイメージ枝・フレーム・例も対応させる。",
            "id": "normal-sense-structure-001"
          },
          {
            "taxonomy_id": "sense_boundary_overlap",
            "location": {
              "section": "sense_structure",
              "line_start": 166,
              "line_end": 166,
              "exact_quote": "【日本語訳・定義】オーケストラで一つのセクションを率いる奏者。重要人物一般の呼称ではない。  "
            },
            "severity": "blocking",
            "rationale": "固定済み source union の U-003 は、オーケストラのセクション首席だけでなく、舞台芸術の principal artist や leading performer まで含む確立した名詞用法を収録対象としている。現行語義3はオーケストラに限定し、レジスター、フレーム、コアイメージ枝もその範囲だけなので、裏付けられた舞台芸術上の主要用法に収録先がない。",
            "evidence_link_ids": [
              "F-007",
              "F-018"
            ],
            "suggested_direction": "語義3を、根拠が支える舞台芸術の主役・主要演者とオーケストラの首席奏者を包含する範囲へ広げ、各下位用法のフレームと例を区別して示す。",
            "id": "normal-sense-structure-002"
          },
          {
            "taxonomy_id": "sense_boundary_overlap",
            "location": {
              "section": "sense_structure",
              "line_start": 194,
              "line_end": 194,
              "exact_quote": "【日本語訳・定義】借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。  "
            },
            "severity": "blocking",
            "rationale": "固定済み source union の U-005 は、信託で income と区別される財産本体・corpus の用法を、金融上の principal に統合する収録対象としている。現行語義4は借入・貸付・投資の「金額」に限定され、信託財産は金銭以外も含み得るため、この専門用法を包含しない。コアイメージ枝、領域、フレームにも信託用法の収録先がない。",
            "evidence_link_ids": [
              "F-025"
            ],
            "suggested_direction": "語義4へ、信託の income と対比される財産本体・corpus の専門用法を明示的に統合し、見出し・コアイメージ枝・領域・フレームを金額だけに閉じない形へ広げる。学習上別フレームと判断するなら独立語義に分ける。",
            "id": "normal-sense-structure-003"
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
          "agent_id": "principal-fresh2-frame-relation-1"
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "bef5bc3e080249e45970356cb808049daba9970c09685b874ac37c61208b6bbf",
          "blind_request_sha256": "2f30dd68c37f53e653cf370543e1026cd9e61beb7fd75f2dca4ad3d566ab02a4",
          "recorded_at": "2026-09-08T14:12:42+09:00",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "principal-fresh2-frame-relation-1"
          },
          "axes": [
            {
              "item_id": "ant-28424ac40a56",
              "axis": "代理役割",
              "relation_type": "補完",
              "reason": ""
            },
            {
              "item_id": "ant-7a5355b6c049",
              "axis": "重要度",
              "relation_type": "程度",
              "reason": ""
            },
            {
              "item_id": "ant-eb9ac1e6e466",
              "axis": "責任順位",
              "relation_type": "補完",
              "reason": ""
            },
            {
              "item_id": "ant-7477e18058ee",
              "axis": "元利区分",
              "relation_type": "補完",
              "reason": ""
            },
            {
              "item_id": "ant-f5f13e9b951b",
              "axis": "重要度",
              "relation_type": "程度",
              "reason": ""
            }
          ]
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "bef5bc3e080249e45970356cb808049daba9970c09685b874ac37c61208b6bbf",
          "stage2_request_sha256": "200b7308d27c8938b31c0439961998e66162304372ae83d7181ea71661be70c6",
          "blind_record_sha256": "9fcca29dc650677e5a5581eaacd8bad4a6a62a636395066b1189707d80641346",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "principal-fresh2-frame-relation-1"
          },
          "adjudications": [
            {
              "item_id": "ant-7a5355b6c049",
              "flags": [],
              "rationale": "`principal` の最重要・高順位と `secondary` の二次的重要性は、当該語義の定義から重要度の程度対立として直接導出でき、違い行も対立を否定または限定していない。",
              "f4_severity": null
            },
            {
              "item_id": "ant-f5f13e9b951b",
              "flags": [],
              "rationale": "`principal` の高い重要性と `minor` の比較的小さい重要性は、当該語義に属する重要度の程度対立であり、違い行に自己否定はない。",
              "f4_severity": null
            },
            {
              "item_id": "ant-7477e18058ee",
              "flags": [
                "F3"
              ],
              "rationale": "`principal` と `interest` は一つの返済額に含まれ得る別々の金額構成要素であり、基礎額とそこから生じる追加額という関連はあっても、補完・程度・方向・評価・状態のいずれかの反意対立ではない。違い行も両者を構成カテゴリーとして説明している。",
              "suggested_direction": "語法・注意への対照表現としての移動",
              "f4_severity": null
            },
            {
              "item_id": "ant-28424ac40a56",
              "flags": [],
              "rationale": "権限を与える `principal` と、その権限で本人のために行動する `agent` は、当該定義に明示された同一代理関係内の補完的役割であり、違い行も対立の不成立を示していない。",
              "f4_severity": null
            },
            {
              "item_id": "ant-eb9ac1e6e466",
              "flags": [],
              "rationale": "第一次的に責任を負う `principal` と、不履行時に保証責任を負う `surety` は、当該債務・保証語義から導出できる責任順位上の補完対立であり、違い行にも自己否定はない。",
              "f4_severity": null
            }
          ],
          "frame_findings": [
            {
              "taxonomy_id": "argument_slot_role_mismatch",
              "location": {
                "section": "frames",
                "line_start": 172,
                "line_end": 172,
                "exact_quote": "【文法パターン】`one of 〈オーケストラなどの所有格〉 principals`＝その団体の首席奏者の一人  "
              },
              "severity": "blocking",
              "rationale": "当該語義はオーケストラの各セクションを率いる奏者に限定されているのに、所有格スロットの「など」と訳の「団体」が、バレエ団や企業などを含む無限定な団体名の代入を許す。すると `principal` が首席奏者ではない別の役職・身分を表す候補までこの語義の完全フレームとして生成され、定義とスロットの意味役割が一致しない。",
              "evidence_link_ids": [],
              "suggested_direction": "所有格スロットと訳をオーケストラ（必要なら定義で明示した音楽アンサンブル）に限定する。"
            },
            {
              "taxonomy_id": "argument_slot_role_mismatch",
              "location": {
                "section": "frames",
                "line_start": 252,
                "line_end": 252,
                "exact_quote": "【文法パターン】`a principal appoints/authorizes an agent to do ...`＝本人が代理人に～する権限を与える／`act on behalf of the principal`＝本人を代理して行動する／`owe a duty to the principal`＝本人に対して義務を負う／`a principal-agent relationship`＝本人・代理人関係  "
              },
              "severity": "blocking",
              "rationale": "代理権を与える側を主語、代理人を目的語、行為を不定詞補部に置く能動フレームだけが、この語義のコロケーションと例文に実現されていない。他の三つの主要パターンには対応例があるため、主要構文とコロケーションの相互対応がこのフレームで欠けている。",
              "evidence_link_ids": [],
              "suggested_direction": "`a principal authorizes an agent to do ...` を独立したコロケーションとして、本人・代理人・許可された行為の三スロットが明示された例文で実現する。"
            }
          ],
          "unrouted_observations": []
        },
        "aligned_at": "2026-09-08T05:47:40.744632+00:00",
        "findings": [
          {
            "taxonomy_id": "argument_slot_role_mismatch",
            "location": {
              "section": "frames",
              "line_start": 172,
              "line_end": 172,
              "exact_quote": "【文法パターン】`one of 〈オーケストラなどの所有格〉 principals`＝その団体の首席奏者の一人  "
            },
            "severity": "blocking",
            "rationale": "当該語義はオーケストラの各セクションを率いる奏者に限定されているのに、所有格スロットの「など」と訳の「団体」が、バレエ団や企業などを含む無限定な団体名の代入を許す。すると `principal` が首席奏者ではない別の役職・身分を表す候補までこの語義の完全フレームとして生成され、定義とスロットの意味役割が一致しない。",
            "evidence_link_ids": [],
            "suggested_direction": "所有格スロットと訳をオーケストラ（必要なら定義で明示した音楽アンサンブル）に限定する。",
            "id": "normal-frame-relation-001"
          },
          {
            "taxonomy_id": "argument_slot_role_mismatch",
            "location": {
              "section": "frames",
              "line_start": 252,
              "line_end": 252,
              "exact_quote": "【文法パターン】`a principal appoints/authorizes an agent to do ...`＝本人が代理人に～する権限を与える／`act on behalf of the principal`＝本人を代理して行動する／`owe a duty to the principal`＝本人に対して義務を負う／`a principal-agent relationship`＝本人・代理人関係  "
            },
            "severity": "blocking",
            "rationale": "代理権を与える側を主語、代理人を目的語、行為を不定詞補部に置く能動フレームだけが、この語義のコロケーションと例文に実現されていない。他の三つの主要パターンには対応例があるため、主要構文とコロケーションの相互対応がこのフレームで欠けている。",
            "evidence_link_ids": [],
            "suggested_direction": "`a principal authorizes an agent to do ...` を独立したコロケーションとして、本人・代理人・許可された行為の三スロットが明示された例文で実現する。",
            "id": "normal-frame-relation-002"
          },
          {
            "taxonomy_id": "lexical_relation_mislabel",
            "location": {
              "section": "lexical_relations",
              "line_start": 237,
              "line_end": 237,
              "exact_quote": "・interest  "
            },
            "severity": "blocking",
            "rationale": "F3: `principal` と `interest` は一つの返済額に含まれ得る別々の金額構成要素であり、基礎額とそこから生じる追加額という関連はあっても、補完・程度・方向・評価・状態のいずれかの反意対立ではない。違い行も両者を構成カテゴリーとして説明している。",
            "evidence_link_ids": [],
            "suggested_direction": "語法・注意への対照表現としての移動",
            "id": "normal-frame-relation-003"
          }
        ],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "inherited session model (not exposed)",
          "ingested_by": "human",
          "agent_id": "/root/principal/example"
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "pass_id": "example-attribution",
          "input_body_sha256": "bef5bc3e080249e45970356cb808049daba9970c09685b874ac37c61208b6bbf",
          "recorded_at": "2026-09-08T05:25:10.719Z",
          "attributions": [
            {
              "example_id": "ex-7dab22053856",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "a principal source of income"
              ],
              "rationale": "In \"Tourism is a principal source of income for the island.\" Principal adjectivally ranks a source by importance. Financial sense 004 would denote capital itself, not modify source.",
              "classification": "unique"
            },
            {
              "example_id": "ex-520ae0c81995",
              "candidate_sense_ids": [
                "sense:006"
              ],
              "discriminating_terms": [
                "a principal in the crime"
              ],
              "rationale": "In \"The court identified him as a principal in the crime.\" The complement in the crime classifies criminal participation. Agency sense 005 requires a represented party, which this criminal-role complement does not express.",
              "classification": "unique"
            },
            {
              "example_id": "ex-49355501caac",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "repaying principal"
              ],
              "rationale": "In \"The borrower will begin repaying principal next year.\" Principal is the amount repaid. Debtor sense 007 denotes the obligor, not the repayment amount.",
              "classification": "unique"
            },
            {
              "example_id": "ex-1e57e2430a98",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "owes duties of loyalty and care to the principal"
              ],
              "rationale": "In \"An agent generally owes duties of loyalty and care to the principal.\" Principal is the beneficiary of an agent's fiduciary duties. Sense 007 concerns primary liability contrasted with a surety, not the represented party to whom an agent owes loyalty.",
              "classification": "unique"
            },
            {
              "example_id": "ex-9dbc67db030d",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "The principal of the college"
              ],
              "rationale": "In \"The principal of the college welcomed the new students.\" The definite institutional-head construction principal of the college denotes its head. Agency sense 005 would require an agent representing this party; the institutional office construction does not express that relationship.",
              "classification": "unique"
            },
            {
              "example_id": "ex-a643dfd29d91",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "principal-agent relationship"
              ],
              "rationale": "In \"The contract created a principal-agent relationship between the owner and the broker.\" The compound explicitly identifies the represented-party/agent relationship. Sense 007 instead pairs a primary obligor with a surety and is not the principal-agent relationship.",
              "classification": "unique"
            },
            {
              "example_id": "ex-157beac2d8f2",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "one of the principal architects"
              ],
              "rationale": "In \"She is one of the principal architects of the reform.\" Principal adjectivally ranks architects in importance. Sense 002 is a noun for an institutional head, not this modifier of plural architects.",
              "classification": "unique"
            },
            {
              "example_id": "ex-59d4fc91ccdf",
              "candidate_sense_ids": [
                "sense:006"
              ],
              "discriminating_terms": [
                "as a principal in the first degree"
              ],
              "rationale": "In \"The older judgment classified the defendant as a principal in the first degree.\" Principal in the first degree is a criminal-participation classification. Agency sense 005 does not classify represented parties into criminal degrees.",
              "classification": "unique"
            },
            {
              "example_id": "ex-2a415e1227b0",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "principal reason for the delay"
              ],
              "rationale": "In \"The principal reason for the delay was a shortage of parts.\" Principal modifies reason to rank its importance. Capital sense 004 is a nominal monetary amount and cannot supply this attributive meaning.",
              "classification": "unique"
            },
            {
              "example_id": "ex-29b0de50abd4",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "The school principal"
              ],
              "rationale": "In \"The school principal met with parents after the incident.\" School principal is the institutional-head office noun. Agency sense 005 is a represented party, not the office denoted by school principal.",
              "classification": "unique"
            },
            {
              "example_id": "ex-18bb0ddb5ba9",
              "candidate_sense_ids": [
                "sense:006"
              ],
              "discriminating_terms": [
                "treats a person who knowingly assists the offense as a principal"
              ],
              "rationale": "In \"The statute treats a person who knowingly assists the offense as a principal.\" The classification is predicated directly on knowing participation in an offense. Agency sense 005 instead depends on authorizing representation; assistance in an offense is not that semantic relation.",
              "classification": "unique"
            },
            {
              "example_id": "ex-da8e5eeb0a02",
              "candidate_sense_ids": [
                "sense:007"
              ],
              "discriminating_terms": [
                "guarantee does not replace the obligation of the principal"
              ],
              "rationale": "In \"The guarantee does not replace the obligation of the principal.\" Principal bears the underlying obligation contrasted with its guarantee. Agency sense 005 identifies the party represented by an agent, not the underlying obligor in this guarantee/obligation opposition.",
              "classification": "unique"
            },
            {
              "example_id": "ex-fe17b24d87b1",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "one of the orchestra's principals"
              ],
              "rationale": "In \"The concert program lists her as one of the orchestra's principals.\" The plural possessive construction names members holding principal-player positions in an orchestra. Sense 002 denotes the head of an educational institution, incompatible with these orchestra positions; agency sense 005 would denote represented parties rather than orchestral offices.",
              "classification": "unique"
            },
            {
              "example_id": "ex-96969658d75c",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "its principal place of business"
              ],
              "rationale": "In \"The company moved its principal place of business to Osaka.\" Principal ranks a place of business as primary. Agency sense 005 is a represented party and cannot supply this adjectival relation to place.",
              "classification": "unique"
            },
            {
              "example_id": "ex-9f21a9f9e7ab",
              "candidate_sense_ids": [
                "sense:007",
                "sense:005"
              ],
              "discriminating_terms": [],
              "rationale": "In \"Under the agreement, the company remains liable as principal for the debt.\" Most naturally principal denotes the primary obligor (007), but liability as principal for a debt also naturally denotes a represented party's liability for debt incurred through an agent (005). Neither a surety contrast nor an agent relationship is specified; liable as principal for the debt alone cannot exclude either reading.",
              "classification": "ambiguous"
            },
            {
              "example_id": "ex-09c5a98499dd",
              "candidate_sense_ids": [
                "sense:005"
              ],
              "discriminating_terms": [
                "on behalf of the principal"
              ],
              "rationale": "In \"The agent may sign the document on behalf of the principal.\" Principal is explicitly the party represented in the agent's signing. Sense 007 is primary obligation relative to a surety, not the on-behalf-of relationship expressed here.",
              "classification": "unique"
            },
            {
              "example_id": "ex-2d3d6de2e03f",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "protect the principal while generating modest returns"
              ],
              "rationale": "In \"The fund aims to protect the principal while generating modest returns.\" Principal is capital preserved while returns are generated, contrasting original amount with earnings. Sense 005 would denote a represented person or entity, not the investment base contrasted with returns.",
              "classification": "unique"
            },
            {
              "example_id": "ex-d08371ee31ca",
              "candidate_sense_ids": [
                "sense:007"
              ],
              "discriminating_terms": [
                "duties of the principal and the surety"
              ],
              "rationale": "In \"The agreement states the duties of the principal and the surety.\" The principal/surety pairing directly contrasts primary and secondary obligors. Agency sense 005 requires a principal/agent relationship, not this surety-role pairing.",
              "classification": "unique"
            },
            {
              "example_id": "ex-3b81e36f6569",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "the principal cause of the failure"
              ],
              "rationale": "In \"Investigators identified corrosion as the principal cause of the failure.\" Principal modifies cause to rank causal importance. Criminal noun sense 006 denotes an offender, not a ranking adjective applied to cause.",
              "classification": "unique"
            },
            {
              "example_id": "ex-40742cac4b7e",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "payment includes both principal and interest"
              ],
              "rationale": "In \"The monthly payment includes both principal and interest.\" Principal is a payment component opposed to interest. Sense 007 denotes the debtor, not an amount included in a payment.",
              "classification": "unique"
            },
            {
              "example_id": "ex-a33f869a820c",
              "candidate_sense_ids": [
                "sense:004"
              ],
              "discriminating_terms": [
                "pay down the principal"
              ],
              "rationale": "In \"Extra payments can help you pay down the principal faster.\" The pay down construction makes principal a reducible outstanding amount. Sense 007 denotes the obligor and cannot be paid down.",
              "classification": "unique"
            },
            {
              "example_id": "ex-f4720456a0d5",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "A college principal"
              ],
              "rationale": "In \"A college principal addressed the graduating class.\" College principal is an institutional-head office title. Agency sense 005 denotes a represented party, not the office named by the compound.",
              "classification": "unique"
            }
          ],
          "reviewer": {
            "mode": "handoff",
            "declared_model": "inherited session model (not exposed)",
            "ingested_by": "human",
            "agent_id": "/root/principal/example"
          },
          "blind_request_sha256": "ba5b490ac2eeec9df2c1124affd127421a1b4188ac18824da0e1e40ef575ce94"
        },
        "aligned_at": "2026-09-08T05:41:52.208159+00:00",
        "findings": [
          {
            "taxonomy_id": "example_sense_attribution_mismatch",
            "location": {
              "section": "collocations_examples",
              "line_start": 343,
              "line_end": 343,
              "exact_quote": "例: Under the agreement, the company remains liable as principal for the debt.  "
            },
            "severity": "blocking",
            "rationale": "段階1でsense:007, sense:005が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
            "evidence_link_ids": [],
            "suggested_direction": "判別語の追加",
            "id": "normal-example-attribution-001"
          }
        ],
        "unrouted_observations": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "qualification",
        "input_body_sha256": "bef5bc3e080249e45970356cb808049daba9970c09685b874ac37c61208b6bbf",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "principal-cycle2-qualification-1"
        },
        "findings": [
          {
            "taxonomy_id": "regional_qualification",
            "location": {
              "section": "frequency_register",
              "line_start": 168,
              "line_end": 168,
              "exact_quote": "【頻度】〈6/10〉"
            },
            "severity": "minor",
            "rationale": "この語義は直後に「オーケストラ・音楽の専門語」と限定され、一般英語では遭遇場面が狭い。6/10は仕様上「中頻度（場面・分野・レジスターがやや限定）」に当たるため、オーケストラ領域内での定着度を英語全体の遭遇頻度へ一般化している。",
            "evidence_link_ids": [
              "F-007",
              "F-018",
              "U-003",
              "C-003"
            ],
            "suggested_direction": "英語全体を基準に2～3/10程度の低頻度へ下げ、専門領域内では確立した役割名であることはレジスター欄で維持する。",
            "id": "normal-qualification-001"
          }
        ]
      },
      {
        "pass_id": "pronunciation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "principal-pronunciation-1"
        },
        "findings": []
      },
      {
        "pass_id": "evidence",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "inherited session model (not exposed)",
          "ingested_by": "human",
          "agent_id": "/root/principal/evidence"
        },
        "findings": [
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "sense_structure",
              "line_start": 166,
              "line_end": 166,
              "exact_quote": "【日本語訳・定義】オーケストラで一つのセクションを率いる奏者。重要人物一般の呼称ではない。"
            },
            "severity": "blocking",
            "rationale": "C-002 routes the education/authority claim to definition:003 (the orchestral definition). Its F-002/F-003/F-014/F-017 sources concern general authority or educational heads and do not directly support this orchestral role. C-003 has separately relevant performer evidence, but that does not make C-002's cross-sense link valid. No link IDs are supplied; this identifies the existing C-002 article_target_ids/source_supports relationship.",
            "evidence_link_ids": [],
            "suggested_direction": "Remove definition:003 from C-002's targets; retain the directly applicable C-003/F-018 support for the orchestral definition.",
            "id": "normal-evidence-001"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 49,
              "line_end": 49,
              "exact_quote": "【文法パターン】`the principal 〈名詞〉`＝主要な～／`a principal 〈名詞〉`＝主な～の一つ／`one of the principal 〈複数名詞〉`＝主要な～の一つ／`the principal cause of ...`＝～の主因／`a principal source of ...`＝～の主要源の一つ／`the principal reason for ...`＝～の主な理由"
            },
            "severity": "blocking",
            "rationale": "C-001 targets this grammar_pattern, but F-001 (Merriam-Webster adjective sense 1), F-013 (Cambridge learner definition), F-016 (Collins American adjective definition) establish adjective meaning and a few noun combinations. They do not document the complete article/number/preposition frames or the proposed a-principal versus the-principal interpretation. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
            "evidence_link_ids": [],
            "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
            "id": "normal-evidence-002"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 134,
              "line_end": 134,
              "exact_quote": "【文法パターン】`the principal of 〈限定詞を含む学校・教育機関の名詞句〉`＝～の校長・学長／`a school principal`＝学校の校長／`a college principal`＝カレッジの学長"
            },
            "severity": "blocking",
            "rationale": "C-002 targets this grammar_pattern, but F-002/F-003 (Merriam-Webster noun senses 1/1b), F-014 (Cambridge school-person definition), and F-017 (Collins title definition) establish school/college leadership meanings and one regional qualification. Their supplied passages do not establish the complete principal of determiner-containing NP, a school principal, and a college principal frames. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
            "evidence_link_ids": [],
            "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
            "id": "normal-evidence-003"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 172,
              "line_end": 172,
              "exact_quote": "【文法パターン】`one of 〈オーケストラなどの所有格〉 principals`＝その団体の首席奏者の一人"
            },
            "severity": "blocking",
            "rationale": "C-003 targets this grammar_pattern, but F-007 (Merriam-Webster noun sense 1f) and F-018 (Collins performer/first-player uses) establish the performer meaning. Neither supplied passage documents one of + orchestra possessive + plural principals or the proposed possessive-slot generalization. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
            "evidence_link_ids": [],
            "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
            "id": "normal-evidence-004"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 200,
              "line_end": 200,
              "exact_quote": "【文法パターン】`principal and interest`＝元金と利息／`pay down the principal`＝元金を減らす／`repay principal`＝元金を返済する／`protect the principal`＝元本を保全する"
            },
            "severity": "blocking",
            "rationale": "C-004 targets this grammar_pattern, but F-008/F-015/F-019/F-024/F-027 establish financial principal and, for F-024, repayment reducing the obligation. They do not document the complete pay down the principal, repay principal, or protect the principal frames, including their article choices. Semantic compatibility alone does not verify these as evidenced complete frames. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
            "evidence_link_ids": [],
            "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
            "id": "normal-evidence-005"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 252,
              "line_end": 252,
              "exact_quote": "【文法パターン】`a principal appoints/authorizes an agent to do ...`＝本人が代理人に～する権限を与える／`act on behalf of the principal`＝本人を代理して行動する／`owe a duty to the principal`＝本人に対して義務を負う／`a principal-agent relationship`＝本人・代理人関係"
            },
            "severity": "blocking",
            "rationale": "C-006 targets this grammar_pattern, but F-004/F-020/F-023 establish authority, behalf, control, and unspecified agent duties. The supplied passages do not establish the full appoints/authorizes an agent to do frame or the complete owe a duty to the principal construction. Wex's mention of duties is not a recorded syntax example. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
            "evidence_link_ids": [],
            "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
            "id": "normal-evidence-006"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 299,
              "line_end": 299,
              "exact_quote": "【文法パターン】`a principal in a crime`＝犯罪について `principal` とされる関与者／`treat someone as a principal`＝人を `principal` として扱う／`a principal in the first/second degree`＝歴史的分類上の第一級・第二級 `principal`"
            },
            "severity": "blocking",
            "rationale": "C-007 targets this grammar_pattern, but F-005 (Merriam-Webster noun sense 1d/legal definition) and F-021 (Collins criminal-law sense) support criminal participation and the accessory contrast. Neither fact statement nor source_detail records first/second degree, historical common-law scope, or the supplied complete frames. C-007's support_summary asserts historical degree classifications beyond the underlying F-005 passage summary. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
            "evidence_link_ids": [],
            "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
            "id": "normal-evidence-007"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "frames",
              "line_start": 337,
              "line_end": 337,
              "exact_quote": "【文法パターン】`be liable as principal`＝主たる当事者として責任を負う／`the obligation of the principal`＝主たる義務者の義務／`the principal and the surety`＝主たる義務者と保証人"
            },
            "severity": "blocking",
            "rationale": "C-008 targets this grammar_pattern, but F-006/F-022/F-026 establish primary liability and the surety/guarantor contrast. They do not document the zero-article be liable as principal frame or the other complete obligation/surety phrases. Their definition-level support does not establish those grammatical constructions. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
            "evidence_link_ids": [],
            "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
            "id": "normal-evidence-008"
          }
        ],
        "notes": [
          "Read the complete fixed request only; no source exploration, inventory coverage assessment, or independent dictionary-correctness adjudication was performed.",
          "Internal packet hash-field equality and fact/union references were checked. Parent confirmed validate_request_integrity and validate_evidence_context returned no errors, rebuilt evidence_context from the real inventory equals this packet, and inventory body binding agrees. External digest verification was performed by the parent, not this reviewer.",
          "The request supplies source_supports without independent evidence-link IDs. Empty evidence_link_ids arrays avoid inventing IDs; rationales identify the affected existing claim/fact relationships.",
          "The source summaries support the central pronunciation, etymological path, derivatives, and most sense definitions. These findings address mapped evidence relationships and construction support, not missing source-inventory coverage."
        ]
      }
    ],
    "checker_reviewers": {
      "translation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "principal-cycle2-translation-1"
      },
      "sense-structure": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "principal-cycle2-sense-structure-1"
      },
      "frame-relation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "principal-fresh2-frame-relation-1"
      },
      "example-attribution": {
        "mode": "handoff",
        "declared_model": "inherited session model (not exposed)",
        "ingested_by": "human",
        "agent_id": "/root/principal/example"
      },
      "qualification": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "principal-cycle2-qualification-1"
      },
      "pronunciation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "principal-pronunciation-1"
      },
      "evidence": {
        "mode": "handoff",
        "declared_model": "inherited session model (not exposed)",
        "ingested_by": "human",
        "agent_id": "/root/principal/evidence"
      }
    },
    "independent_candidates": [],
    "summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency."
  },
  "cold_review": {
    "summary": "問題候補1件。個別の語義説明は慎重に限定されている一方、コアイメージにある名詞用法の総括だけが、その限定を越えて一般化されている。",
    "findings": [
      {
        "id": "COLD-001",
        "location": "コアイメージ（名詞用法の総括）と語義3（適用範囲の限定）",
        "severity": "medium",
        "description": "コアイメージの「組織や行為の中心人物」という表現は、名詞の principal を重要人物一般に使えるかのように読めるが、列挙された具体的語義は教育機関の長、首席奏者、法律上の当事者など役割ごとに限定され、語義3では重要人物一般ではないと明記している。この範囲差により、学習者が任意の組織の中心人物を a principal と呼べると誤って一般化するおそれがある。",
        "reason": "コアイメージは「形容詞では主要なものを選び出し、名詞では組織や行為の中心人物、利息に対する元の金額、代理関係などの主要当事者を指す。」と名詞の人物用法を広く総括している。しかし本文の人物語義は役職・法的関係ごとに限定され、語義3はさらに「重要人物一般の呼称ではない。」と反例を明示しているため、総括だけを読んだ学習者には適用範囲が実際の説明より広く見える。",
        "suggested_direction": "コアイメージを「教育機関の長やオーケストラの首席奏者など、特定の制度・役割で中心となる人物」のように、本文で立てた語義へ対応する表現に狭める。重要人物一般を表す独立した名詞語義も扱う意図がある場合は、適用できる文脈と用例を明示した別語義として検証のうえ追加し、コアイメージだけで暗示しない。",
        "scope_anchors": [
          {
            "id": "COLD-001-A1",
            "exact_quote": "形容詞では主要なものを選び出し、名詞では組織や行為の中心人物、利息に対する元の金額、代理関係などの主要当事者を指す。",
            "location_hint": "＃コアイメージの第1段落、第2文"
          },
          {
            "id": "COLD-001-A2",
            "exact_quote": "オーケストラで一つのセクションを率いる奏者。重要人物一般の呼称ではない。",
            "location_hint": "語義3【日本語訳・定義】"
          }
        ]
      }
    ],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "principal_cycle2_cold"
    },
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-principal-20260908T045228Z-e5bdb73f",
    "context_id": "cold-principal-context-20260908T045228Z-e5bdb73f",
    "input_body_sha256": "bef5bc3e080249e45970356cb808049daba9970c09685b874ac37c61208b6bbf",
    "prompt_sha256": "25c298d1a4305746147791bd442cd725a92737c8f0802b992ea88e5c6ff76a5d",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-08T05:56:50.966099+00:00"
  },
  "final_blind": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-principal-20260908T045228Z-e5bdb73f",
    "context_id": "blind-principal-context-20260908T045228Z-e5bdb73f",
    "input_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
    "prompt_sha256": "3a481b4b5b1236ff386e148bcacc574570b305e79f5e155e9afcd34091f7785c",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "contract_version": "review_preflight_v1",
    "reviewer_handoff": {
      "declared_model": "Codex (inherited session model)",
      "agent_id": "/root/finish_principal/finalblind2"
    },
    "provisional_decision": "pass",
    "independent_candidates": [
      {
        "id": "independent-1",
        "surface_form": "principal",
        "frame": "principal + noun",
        "meaning": "主要な、最も重要な、第一の",
        "disposition": "included",
        "rationale": "principal の「principal + noun」は「主要な、最も重要な、第一の」。重要性・地位の形容詞義が定義と例文に一貫して現れる。",
        "semantic_assertions": [
          {
            "id": "assertion-1",
            "statement": "時間的に最初であることだけを意味しない",
            "polarity": "must_hold",
            "scope": "principal + noun"
          }
        ]
      },
      {
        "id": "independent-2",
        "surface_form": "principal",
        "frame": "a principal source of income",
        "meaning": "複数ある主要な供給源の一つ",
        "disposition": "included",
        "rationale": "principal の「a principal source of income」は「複数ある主要な供給源の一つ」。不定冠詞の例も主要性を表し、唯一性を要求していない。",
        "semantic_assertions": [
          {
            "id": "assertion-2",
            "statement": "主要な供給源は一つに限定されない",
            "polarity": "must_hold",
            "scope": "a principal source of income"
          }
        ]
      },
      {
        "id": "independent-3",
        "surface_form": "principal",
        "frame": "one of the principal + plural noun",
        "meaning": "主要な複数の対象のうちの一つ",
        "disposition": "included",
        "rationale": "principal の「one of the principal + plural noun」は「主要な複数の対象のうちの一つ」。改革の立案者の例は最重要対象の複数性を保つ。",
        "semantic_assertions": [
          {
            "id": "assertion-3",
            "statement": "principal は複数の主要対象に適用できる",
            "polarity": "must_hold",
            "scope": "one of the principal + plural noun"
          }
        ]
      },
      {
        "id": "independent-4",
        "surface_form": "principal",
        "frame": "the principal place of business",
        "meaning": "主たる事業所",
        "disposition": "included",
        "rationale": "principal の「the principal place of business」は「主たる事業所」。形容詞と事業所名詞句の定着表現で、適用法による判定差も明示する。",
        "semantic_assertions": [
          {
            "id": "assertion-4",
            "statement": "この複合表現から principal 単独に事業所の名詞義を導かない",
            "polarity": "must_hold",
            "scope": "the principal place of business"
          }
        ]
      },
      {
        "id": "independent-5",
        "surface_form": "principal",
        "frame": "a principal of an organization",
        "meaning": "組織の主要人物・責任者",
        "disposition": "included",
        "rationale": "principal の「a principal of an organization」は「組織の主要人物・責任者」。組織・事業の主導的地位を持つ人という定義に含まれる。",
        "semantic_assertions": [
          {
            "id": "assertion-5",
            "statement": "組織を支配する者だけに限定しない",
            "polarity": "must_hold",
            "scope": "a principal of an organization"
          }
        ]
      },
      {
        "id": "independent-6",
        "surface_form": "principal",
        "frame": "the principals in a negotiation",
        "meaning": "交渉・活動の主要当事者",
        "disposition": "included",
        "rationale": "principal の「the principals in a negotiation」は「交渉・活動の主要当事者」。交渉などの主要な当事者が明示されている。",
        "semantic_assertions": [
          {
            "id": "assertion-6",
            "statement": "単に世間で有名な人物であることだけでは足りない",
            "polarity": "must_hold",
            "scope": "the principals in a negotiation"
          }
        ]
      },
      {
        "id": "independent-7",
        "surface_form": "principal",
        "frame": "the principal of a school or college",
        "meaning": "学校・教育機関の長",
        "disposition": "included",
        "rationale": "principal の「the principal of a school or college」は「学校・教育機関の長」。教育機関の長の定義と校長・カレッジの例が対応する。",
        "semantic_assertions": [
          {
            "id": "assertion-7",
            "statement": "教育機関の種類と役職呼称には地域・制度差がある",
            "polarity": "must_hold",
            "scope": "the principal of a school or college"
          }
        ]
      },
      {
        "id": "independent-8",
        "surface_form": "principal",
        "frame": "act as principal",
        "meaning": "取引の当事者本人として行動する",
        "disposition": "included",
        "rationale": "principal の「act as principal」は「取引の当事者本人として行動する」。自己勘定で購入する例により代理関係上の本人とは独立に具体化される。",
        "semantic_assertions": [
          {
            "id": "assertion-8",
            "statement": "代理人を任命することを必要条件にしない",
            "polarity": "must_hold",
            "scope": "act as principal"
          }
        ]
      },
      {
        "id": "independent-9",
        "surface_form": "principal",
        "frame": "principal and interest",
        "meaning": "利息と区別される借入・貸付の元金",
        "disposition": "included",
        "rationale": "principal の「principal and interest」は「利息と区別される借入・貸付の元金」。返済の構成要素として元金と利息を区別する。",
        "semantic_assertions": [
          {
            "id": "assertion-9",
            "statement": "元金と利息は金額構成要素の区別であり反意語ではない",
            "polarity": "must_hold",
            "scope": "principal and interest"
          }
        ]
      },
      {
        "id": "independent-10",
        "surface_form": "principal",
        "frame": "pay down the principal",
        "meaning": "未返済元金を返済により減らす",
        "disposition": "included",
        "rationale": "principal の「pay down the principal」は「未返済元金を返済により減らす」。残額が減る作用方向を用途と訳がともに保つ。",
        "semantic_assertions": [
          {
            "id": "assertion-10",
            "statement": "元金への支払いは未返済元金を減らす",
            "polarity": "must_hold",
            "scope": "pay down the principal"
          }
        ]
      },
      {
        "id": "independent-11",
        "surface_form": "principal",
        "frame": "repay principal",
        "meaning": "借入の元金を返済する",
        "disposition": "included",
        "rationale": "principal の「repay principal」は「借入の元金を返済する」。principal は返済の対象となる金額の名詞である。",
        "semantic_assertions": [
          {
            "id": "assertion-11",
            "statement": "返済する主体と返済される金額を入れ替えない",
            "polarity": "must_hold",
            "scope": "repay principal"
          }
        ]
      },
      {
        "id": "independent-12",
        "surface_form": "principal",
        "frame": "protect the principal",
        "meaning": "投資の元本を保全する",
        "disposition": "included",
        "rationale": "principal の「protect the principal」は「投資の元本を保全する」。投資額の保全目標を述べ、保証の存在までは主張しない。",
        "semantic_assertions": [
          {
            "id": "assertion-12",
            "statement": "投資元本はそこから生じる収益と区別される",
            "polarity": "must_hold",
            "scope": "protect the principal"
          }
        ]
      },
      {
        "id": "independent-13",
        "surface_form": "principal",
        "frame": "the principal of a trust",
        "meaning": "信託収益と区別される信託財産本体",
        "disposition": "included",
        "rationale": "principal の「the principal of a trust」は「信託収益と区別される信託財産本体」。金額義だけに還元せず財産本体・corpus として明示する。",
        "semantic_assertions": [
          {
            "id": "assertion-13",
            "statement": "信託元本は現金額だけに限定されない",
            "polarity": "must_hold",
            "scope": "the principal of a trust"
          }
        ]
      },
      {
        "id": "independent-14",
        "surface_form": "principal",
        "frame": "a principal-agent relationship",
        "meaning": "本人と代理人の権限関係",
        "disposition": "included",
        "rationale": "principal の「a principal-agent relationship」は「本人と代理人の権限関係」。権限を与える側と本人のために行動する側の区別が保たれる。",
        "semantic_assertions": [
          {
            "id": "assertion-14",
            "statement": "principal は agent のために代理行為をする側ではなく権限の源となる",
            "polarity": "must_hold",
            "scope": "a principal-agent relationship"
          }
        ]
      },
      {
        "id": "independent-15",
        "surface_form": "principal",
        "frame": "act on behalf of the principal",
        "meaning": "代理人が本人のために行動する",
        "disposition": "included",
        "rationale": "principal の「act on behalf of the principal」は「代理人が本人のために行動する」。例文の主語は agent であり principal は代理される側である。",
        "semantic_assertions": [
          {
            "id": "assertion-15",
            "statement": "on behalf of の補語はこの例で本人を指す",
            "polarity": "must_hold",
            "scope": "act on behalf of the principal"
          }
        ]
      },
      {
        "id": "independent-16",
        "surface_form": "principal",
        "frame": "a principal in a stage production",
        "meaning": "舞台芸術で主要な役を担う演者",
        "disposition": "included",
        "rationale": "principal の「a principal in a stage production」は「舞台芸術で主要な役を担う演者」。舞台芸術で確立した役割として定義されている。",
        "semantic_assertions": [
          {
            "id": "assertion-16",
            "statement": "一般の重要人物と舞台芸術の役割名を同一視しない",
            "polarity": "must_hold",
            "scope": "a principal in a stage production"
          }
        ]
      },
      {
        "id": "independent-17",
        "surface_form": "principal",
        "frame": "one of the orchestra's principals",
        "meaning": "オーケストラのセクションを率いる首席奏者",
        "disposition": "included",
        "rationale": "principal の「one of the orchestra's principals」は「オーケストラのセクションを率いる首席奏者」。チェロのセクションを率いる例が名詞の役割と合致する。",
        "semantic_assertions": [
          {
            "id": "assertion-17",
            "statement": "オーケストラ全体の唯一の長であることを要求しない",
            "polarity": "must_hold",
            "scope": "one of the orchestra's principals"
          }
        ]
      },
      {
        "id": "independent-18",
        "surface_form": "principal",
        "frame": "a principal in a crime",
        "meaning": "刑事法の分類における犯罪関与者",
        "disposition": "included",
        "rationale": "principal の「a principal in a crime」は「刑事法の分類における犯罪関与者」。実行者と一定の関与者を適用法に即して扱う。",
        "semantic_assertions": [
          {
            "id": "assertion-18",
            "statement": "すべての法域で直接実行者だけを指すと断定しない",
            "polarity": "must_hold",
            "scope": "a principal in a crime"
          }
        ]
      },
      {
        "id": "independent-19",
        "surface_form": "principal",
        "frame": "treat someone as a principal",
        "meaning": "関与者を適用法上 principal に分類する",
        "disposition": "included",
        "rationale": "principal の「treat someone as a principal」は「関与者を適用法上 principal に分類する」。援助者を含める制定法の例として範囲が限定される。",
        "semantic_assertions": [
          {
            "id": "assertion-19",
            "statement": "援助者が含まれるかどうかは適用される分類による",
            "polarity": "must_hold",
            "scope": "treat someone as a principal"
          }
        ]
      },
      {
        "id": "independent-20",
        "surface_form": "principal",
        "frame": "be liable as principal",
        "meaning": "義務について第一次的責任を負う当事者",
        "disposition": "included",
        "rationale": "principal の「be liable as principal」は「義務について第一次的責任を負う当事者」。債務例で名詞の義務者を示し金額義や刑事義と分離する。",
        "semantic_assertions": [
          {
            "id": "assertion-20",
            "statement": "この用例で principal は元金という金額ではない",
            "polarity": "must_hold",
            "scope": "be liable as principal"
          }
        ]
      },
      {
        "id": "independent-21",
        "surface_form": "principal",
        "frame": "the obligation of the principal",
        "meaning": "主たる義務者が負う義務",
        "disposition": "included",
        "rationale": "principal の「the obligation of the principal」は「主たる義務者が負う義務」。of の補語は義務を負う人・法人である。",
        "semantic_assertions": [
          {
            "id": "assertion-21",
            "statement": "principal はこの義務を負う側であり義務の受益者とは限らない",
            "polarity": "must_hold",
            "scope": "the obligation of the principal"
          }
        ]
      },
      {
        "id": "independent-22",
        "surface_form": "principal",
        "frame": "the principal and the surety",
        "meaning": "主たる義務者と保証する側",
        "disposition": "included",
        "rationale": "principal の「the principal and the surety」は「主たる義務者と保証する側」。対比される役割と例文の respectively の対応が一致する。",
        "semantic_assertions": [
          {
            "id": "assertion-22",
            "statement": "例文では第一次的責任が principal に、二次的責任が surety に対応する",
            "polarity": "must_hold",
            "scope": "the principal and the surety"
          }
        ]
      },
      {
        "id": "independent-23",
        "surface_form": "principal",
        "frame": "principal debtor / principal obligor",
        "meaning": "主たる債務者・義務者を修飾する形容詞",
        "disposition": "included",
        "rationale": "principal の「principal debtor / principal obligor」は「主たる債務者・義務者を修飾する形容詞」。名詞単独の役割と形容詞による修飾を明示的に区別する。",
        "semantic_assertions": [
          {
            "id": "assertion-23",
            "statement": "複合表現の debtor・obligor の意味を形容詞 principal 単独へ移さない",
            "polarity": "must_hold",
            "scope": "principal debtor / principal obligor"
          }
        ]
      },
      {
        "id": "independent-24",
        "surface_form": "principally",
        "frame": "principally + predicate",
        "meaning": "主として、主に",
        "disposition": "included",
        "rationale": "principally の「principally + predicate」は「主として、主に」。副詞派生形として語形成に含まれ、独立した principal の品詞とはされていない。",
        "semantic_assertions": [
          {
            "id": "assertion-24",
            "statement": "principally は principal そのものの副詞用法ではなく派生語である",
            "polarity": "must_hold",
            "scope": "principally + predicate"
          }
        ]
      },
      {
        "id": "independent-25",
        "surface_form": "principalship",
        "frame": "the principalship of an institution",
        "meaning": "校長・学長などの職または在職",
        "disposition": "included",
        "rationale": "principalship の「the principalship of an institution」は「校長・学長などの職または在職」。名詞派生形として列挙される範囲は適切である。",
        "semantic_assertions": [
          {
            "id": "assertion-25",
            "statement": "principalship は役職者本人を表す principal と同一の語形ではない",
            "polarity": "must_hold",
            "scope": "the principalship of an institution"
          }
        ]
      },
      {
        "id": "independent-26",
        "surface_form": "principal",
        "frame": "a principal in an organ",
        "meaning": "オルガンの主要なストップまたはそのパイプ",
        "disposition": "excluded",
        "rationale": "principal の「a principal in an organ」は「オルガンの主要なストップまたはそのパイプ」。オルガン構造の低頻度専門義は一般学習記事に必須の主要用法ではない。",
        "semantic_assertions": [
          {
            "id": "assertion-26",
            "statement": "オーケストラの首席奏者義から楽器部品義を推論しない",
            "polarity": "must_hold",
            "scope": "a principal in an organ"
          }
        ]
      },
      {
        "id": "independent-27",
        "surface_form": "principal",
        "frame": "a principal in a roof truss",
        "meaning": "屋根組の主要な垂木・支持部材",
        "disposition": "excluded",
        "rationale": "principal の「a principal in a roof truss」は「屋根組の主要な垂木・支持部材」。建築部材の低頻度専門義は本記事の主要な学習範囲外と判断する。",
        "semantic_assertions": [
          {
            "id": "assertion-27",
            "statement": "人物名詞義から建築部材義へ一般化しない",
            "polarity": "must_hold",
            "scope": "a principal in a roof truss"
          }
        ]
      },
      {
        "id": "independent-28",
        "surface_form": "principle",
        "frame": "a basic principle",
        "meaning": "原理・原則",
        "disposition": "excluded",
        "rationale": "principle の「a basic principle」は「原理・原則」。別の見出し語であり、混同注意としてのみ扱うのが適切である。",
        "semantic_assertions": [
          {
            "id": "assertion-28",
            "statement": "同音・近い綴りを理由に principal の原則義を設けない",
            "polarity": "must_hold",
            "scope": "a basic principle"
          }
        ]
      }
    ],
    "article_findings": [],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "Codex (inherited session model)",
      "ingested_by": "human",
      "agent_id": "/root/finish_principal/finalblind2"
    },
    "recorded_at": "2026-09-08T07:55:14.679388+00:00"
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/p/principal.md",
    "body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
    "final_blind_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/final_blind.json",
    "final_blind_sha256": "4399f0a1afc2f6cac2c7961d36136c108e5ae7e771d5b274566bf645be561b33",
    "blind_output_sha256": "c716b5a23c9bd56fb0631dc6129f4ff9f21897df7f209d4eaaec428f0c77d65b",
    "sealed_at": "2026-09-08T16:55:14.862227+09:00"
  },
  "pre_blind_resolution": {
    "schema_version": "pre_blind_resolution_v1",
    "stage": "pre_blind_resolution",
    "run_id": "20260908T045228Z-e5bdb73f",
    "input_body_sha256": "bef5bc3e080249e45970356cb808049daba9970c09685b874ac37c61208b6bbf",
    "output_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694",
    "recorded_at": "2026-09-08T06:06:48Z",
    "resolutions": [
      {
        "id": "normal-sense-structure-001",
        "finding_id": "normal-sense-structure-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Fixed union U-002 and fact F-002 directly support a person with controlling authority or a leading position, while the draft confined the person sense to education titles.",
        "required_changes": [
          "Give the supported authority or leading-position noun use an explicit home without inventing a new frame."
        ],
        "implemented_changes": [
          "Broadened sense 2's heading and definition to the supported authority or leading-position use while retaining education as its prominent conventional title use."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-sense-structure-002",
        "finding_id": "normal-sense-structure-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "U-003, F-007, and F-018 support an established leading-performer use beyond orchestral section leaders.",
        "required_changes": [
          "Extend sense 3 only to the directly supported performing-arts range."
        ],
        "implemented_changes": [
          "Expanded sense 3's heading, definition, register, grammar note, core-image branch, and usage note to leading performers in the performing arts and orchestral principals."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-sense-structure-003",
        "finding_id": "normal-sense-structure-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "U-005 and F-025 directly define trust principal as the property or corpus distinct from income.",
        "required_changes": [
          "Integrate the supported trust-corpus use without treating all principal as a money amount."
        ],
        "implemented_changes": [
          "Added trust principal to sense 4's heading, definition, domain note, grammar note, usage note, and core-image branch."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-frame-relation-001",
        "finding_id": "normal-frame-relation-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The generic possessive slot licensed organizations outside the performing-arts role described by the sense.",
        "required_changes": [
          "Do not expose an unrestricted organization slot for this specialized noun."
        ],
        "implemented_changes": [
          "Removed the generic possessive construction from the grammar line; the remaining collocation explicitly names an orchestra."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-frame-relation-002",
        "finding_id": "normal-frame-relation-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The missing-example symptom came from an asserted authorize/appoint frame that the frozen facts did not establish as a complete construction; adding another unevidenced example would compound the issue.",
        "required_changes": [
          "Remove the unsupported complete frame rather than manufacture a matching example."
        ],
        "implemented_changes": [
          "Reduced the agency grammar line to the directly grounded principal-agent relationship and on-behalf relationship, and removed the unsupported duty collocation."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-frame-relation-003",
        "finding_id": "normal-frame-relation-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Principal and interest are related components, not opposites on an accepted lexical opposition axis.",
        "required_changes": [
          "Remove interest from the antonym inventory and retain the useful contrast as usage guidance."
        ],
        "implemented_changes": [
          "Deleted the interest antonym block and stated the related-component contrast in the finance usage note."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-example-attribution-001",
        "finding_id": "normal-example-attribution-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The original liable-as-principal example did not distinguish obligation liability from an agency principal.",
        "required_changes": [
          "Add a directly supported surety or guarantor contrast to disambiguate the role."
        ],
        "implemented_changes": [
          "Extended the example and translation with the guarantor's secondary liability, binding it to the obligation-law sense."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-qualification-001",
        "finding_id": "normal-qualification-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The performing-arts noun is a specialized low-frequency use in English overall, so 6/10 overstated its encounter frequency.",
        "required_changes": [
          "Lower the English-wide frequency while retaining the established specialist label."
        ],
        "implemented_changes": [
          "Changed sense 3 from 6/10 to 3/10 and retained its performing-arts and orchestral domain qualification."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-evidence-001",
        "finding_id": "normal-evidence-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "C-002's education and authority facts did not support the performing-arts definition target.",
        "required_changes": [
          "Remove the cross-sense target while preserving C-003's performer support."
        ],
        "implemented_changes": [
          "Removed definition:003 from C-002 and kept performing-arts support exclusively under C-003."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-evidence-002",
        "finding_id": "normal-evidence-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The fixed adjective facts support meaning and attested noun combinations, not the draft's full article, number, and preposition system.",
        "required_changes": [
          "Restrict the grammar claim to the supported attributive shape and stop binding definition evidence to the full frame."
        ],
        "implemented_changes": [
          "Simplified sense 1 grammar to attributive principal plus noun and removed grammar_pattern:001 from C-001's source binding."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-evidence-003",
        "finding_id": "normal-evidence-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The education facts establish the role but do not establish the complete determiner and of-complement templates as quoted.",
        "required_changes": [
          "Replace the unevidenced complete frame with a count-noun role note and narrow its source binding."
        ],
        "implemented_changes": [
          "Replaced the sense 2 grammar templates with a count-noun role description and removed grammar_pattern:002 from C-002."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-evidence-004",
        "finding_id": "normal-evidence-004",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The performer facts establish the specialist role but not an unrestricted possessive-plus-plural frame.",
        "required_changes": [
          "Remove the generalized possessive template and narrow its source binding."
        ],
        "implemented_changes": [
          "Replaced the sense 3 grammar template with a specialist count-noun role note and removed grammar_pattern:003 from C-003."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-evidence-005",
        "finding_id": "normal-evidence-005",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The finance facts establish the capital-versus-interest concept and repayment effect, not every article-bearing construction listed in the grammar line.",
        "required_changes": [
          "Replace the complete construction list with a meaning-and-countability note grounded in the fixed facts."
        ],
        "implemented_changes": [
          "Replaced sense 4's grammar list with a finance/trust noun-use note and removed grammar_pattern:004 from C-004."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-evidence-006",
        "finding_id": "normal-evidence-006",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The agency facts support authority and acting on behalf but not the full appoint/authorize and owe-a-duty syntax asserted by the draft.",
        "required_changes": [
          "Keep only directly grounded relations and remove the grammar target from C-006."
        ],
        "implemented_changes": [
          "Removed the appoint/authorize and duty frames, retained the directly grounded relationship expressions, and removed grammar_pattern:005 from C-006."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-evidence-007",
        "finding_id": "normal-evidence-007",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The criminal-law facts support participant classification and the accessory contrast, but the inventory did not support the historical degree claim or the complete quoted frames.",
        "required_changes": [
          "Remove the historical-degree material and narrow the grammar/source binding to the supported classification."
        ],
        "implemented_changes": [
          "Removed the degree statement and example, simplified the grammar note, removed grammar_pattern:006 from C-007, and corrected F-005's support summary to omit historical degrees."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "normal-evidence-008",
        "finding_id": "normal-evidence-008",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The obligation facts establish primary liability and the surety/guarantor contrast, not each complete phrase in the former grammar list.",
        "required_changes": [
          "State the directly supported role contrast without claiming the full constructions are source-attested."
        ],
        "implemented_changes": [
          "Replaced sense 7's grammar list with a count-noun role contrast and removed grammar_pattern:007 from C-008."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
      },
      {
        "id": "COLD-001",
        "finding_id": "COLD-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The core image's generic central-person wording licensed uses broader than either the directly supported authority sense or the draft's established institutional and specialist roles.",
        "required_changes": [
          "Tie the core image to the supported authority, education, performing-arts, finance/trust, and legal roles."
        ],
        "implemented_changes": [
          "Rewrote the core summary and branches to name the supported roles and to avoid presenting principal as a free synonym for any important person."
        ],
        "resolved_body_sha256": "cdfd31b9e0407f51f99397eda23de6ad98b0113bd74d922527ec37125ae83694"
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
    "input_body_sha256": "bef5bc3e080249e45970356cb808049daba9970c09685b874ac37c61208b6bbf",
    "output_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
    "recorded_at": "2026-09-08T07:53:40.144305+00:00",
    "changed_units": [
      "collocations_examples",
      "core_image",
      "frames",
      "frequency_register",
      "lexical_relations",
      "sense_structure",
      "usage_notes"
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
    "revision_history_paths": [
      "recheck/round2/pre_blind_revision.before.json",
      "recheck_resolution_checkpoint.json",
      "recheck/round2/resolution.json",
      "final_attempt1/pre_blind_revision.json",
      "final_attempt1/post_blind_resolution.json",
      "recheck/round4/resolution.json"
    ],
    "notes": "Cumulative revision binding for latest final blind; original pre-blind and subsequent post-blind correction chronology preserved in history artifacts."
  },
  "checker_recheck_manifest": {
    "schema_version": "checker_recheck_manifest_v1",
    "current_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
    "revision_plan_sha256": "d03f47137a9e8f61e96234917945961aeb0d62b8a3d4cba0024181db99cb3d22",
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
        "normalized_input_sha256": "55e2434122bf39c23a18b658d180fe7f932b970cb4e5ff30c7c6ba486eb2f710",
        "source_artifact_sha256": "11b53e4537ab0802f8abdeb7c750354823713e2aade7daa2f5113504efd8d765",
        "output_sha256": "6a6299403745e8fa0f73118e9c5e9a0379abb0a1e778be3b08305d8a39145f60",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": false,
        "reviewer_agent_id": "/root/finish_principal/translation5",
        "output_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/recheck/round5/pass_findings.json",
        "reuse_proof_path": null,
        "validated_on_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "pass_id": "sense-structure",
        "mode": "reused",
        "spec_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
        "normalized_input_sha256": "5da7b8bcb9bc7d555df0b9cb68b0502cb887aeaeef1bef72fef16c0d20508c72",
        "source_artifact_sha256": "11b53e4537ab0802f8abdeb7c750354823713e2aade7daa2f5113504efd8d765",
        "output_sha256": "14ac7847071b716a29074931ae89094d9fc602a56ab501a0553243c64c56474d",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reviewer_agent_id": "/root/finish_principal/sense4",
        "output_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/recheck/round5/pass_findings.json",
        "reuse_proof_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/recheck/round5/reuse_proof.json",
        "validated_on_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "pass_id": "frame-relation",
        "mode": "rechecked",
        "spec_sha256": "3598ca81a5784639c6b43a0806d0981a985bf4174f424c744aad1dde787bfcef",
        "normalized_input_sha256": "45b49aa2f05b3e87e0bb641c7a9b62bed88d52fca70048386cbd0cd6b6bf209e",
        "source_artifact_sha256": "11b53e4537ab0802f8abdeb7c750354823713e2aade7daa2f5113504efd8d765",
        "output_sha256": "b13f7e5e34c0f9acd263ae0c9d66b82e59aebbc26479222b22f019f58795d3bf",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": false,
        "reviewer_agent_id": "/root/finish_principal/frame5",
        "output_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/recheck/round5/pass_findings.json",
        "reuse_proof_path": null,
        "validated_on_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "pass_id": "example-attribution",
        "mode": "rechecked",
        "spec_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
        "normalized_input_sha256": "2ba630323cd200acd0118fc11a4d5ac71fd2df6059611e92af89920af67b3e59",
        "source_artifact_sha256": "11b53e4537ab0802f8abdeb7c750354823713e2aade7daa2f5113504efd8d765",
        "output_sha256": "49a030952b89d13fc727b77bb4bc667dab5bd2cb0dc4651c7a2a73069c08952e",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": false,
        "reviewer_agent_id": "/root/finish_principal/example5",
        "output_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/recheck/round5/pass_findings.json",
        "reuse_proof_path": null,
        "validated_on_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "pass_id": "qualification",
        "mode": "rechecked",
        "spec_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
        "normalized_input_sha256": "0890f7d4c3d0cd087160734c70f9537b6d0b06dff906e71eb027e53122cebcbe",
        "source_artifact_sha256": "11b53e4537ab0802f8abdeb7c750354823713e2aade7daa2f5113504efd8d765",
        "output_sha256": "db15876f175792df10fe38b4d98fa80bd942317cfefa202a2bd46c8784901ce4",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": false,
        "reviewer_agent_id": "/root/finish_principal/qualification5",
        "output_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/recheck/round5/pass_findings.json",
        "reuse_proof_path": null,
        "validated_on_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "pass_id": "pronunciation",
        "mode": "reused",
        "spec_sha256": "7e3e94267ac9f917c901c12580b91e570b5989df7adfbf2a39b833478c766d8a",
        "normalized_input_sha256": "ee10ead66e05a1ae925e7c3a11f269975c98c542ec08d1b8f2ad9c2159d3ca70",
        "source_artifact_sha256": "11b53e4537ab0802f8abdeb7c750354823713e2aade7daa2f5113504efd8d765",
        "output_sha256": "b34f79a86c878714accf4fe57903d5fab329a4e126cb67af6fc4baeaed422b06",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reviewer_agent_id": "/root/finish_principal/pronunciation4",
        "output_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/recheck/round5/pass_findings.json",
        "reuse_proof_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/recheck/round5/reuse_proof.json",
        "validated_on_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "pass_id": "evidence",
        "mode": "rechecked",
        "spec_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
        "normalized_input_sha256": "bb1a04345662e53ff1f5924b2b3f6246c0f01145bb04956d11179f36f6c5e805",
        "source_artifact_sha256": "11b53e4537ab0802f8abdeb7c750354823713e2aade7daa2f5113504efd8d765",
        "output_sha256": "89711e03e209f2794fd26a5dd59a8f055d933a5395603bce895d019bef598c80",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": false,
        "reviewer_agent_id": "/root/finish_principal/evidence5",
        "output_path": "audits/runs/p/principal/20260908T045228Z-e5bdb73f/recheck/round5/pass_findings.json",
        "reuse_proof_path": null,
        "validated_on_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      }
    ]
  },
  "post_blind_resolution": {
    "schema_version": "post_blind_resolution_v1",
    "recorded_at": "2026-09-08T08:01:13.797000+00:00",
    "input_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
    "output_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
    "resolutions": [],
    "previous_attempt_resolution_path": "final_attempt1/post_blind_resolution.json",
    "rationale": "Latest independent blind has no findings. Prior two adopted scope corrections are preserved in attempt1 and verified by round4/5 plus this new body-only blind.",
    "learning_delta": {
      "schema_version": "process_improvement_learning_delta_v2",
      "reviewed": true,
      "items": []
    }
  },
  "post_blind_verification": {
    "schema_version": "post_blind_verification_v1",
    "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
    "recorded_at": "2026-09-08T08:01:13.797000+00:00",
    "checker_recheck_completed": true,
    "checker_recheck_manifest_sha256": "13c0daf50b6e128eade7f500a7fd53210ceb6cebd4f05773da7735f0aee19917",
    "final_blind_repeated": true,
    "final_blind_sha256": "4399f0a1afc2f6cac2c7961d36136c108e5ae7e771d5b274566bf645be561b33",
    "final_blind_recorded_at": "2026-09-08T07:55:14.679388+00:00",
    "attempt_number": 2,
    "previous_attempt": {
      "final_blind_path": "final_attempt1/final_blind.json",
      "final_blind_sha256": "31d13a9a7266c1528340209a85b023a545a6c53fbf8ccae52d8e875b452bb343",
      "resolution_path": "final_attempt1/post_blind_resolution.json",
      "resolution_sha256": "1e1b9a7b81ae8ddd48b4716709afca278c95ffbe3a8249356d23c39cee4ba9f9"
    },
    "status": "complete"
  },
  "targeted_adjudications": {
    "schema_version": "targeted_adjudications_v1",
    "requests": [],
    "adjudications": []
  },
  "source_inventory": {
    "schema_version": "source_inventory_v2",
    "stage": "source_inventory",
    "headword": "principal",
    "run_id": "source-principal-20260907T233257Z-44da61f2",
    "context_id": "source-principal-context-20260907T233257Z-44da61f2",
    "input_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
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
        "post_cold_rechecks_used": 5,
        "final_attempts_used": 2
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
              "statement": "As a noun, principal can denote a person in a leading position or a main participant in an action or transaction, especially one having control or authority.",
              "source_detail": "General noun sense1 and Legal Definition noun sense1 of the same Merriam-Webster entry: the broad person/participant sense precedes the specialized subtypes. Control or authority is typical rather than mandatory."
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
            "definition:001"
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
          "statement": "Principal denotes a leading person or main party in an activity/transaction and conventionally an education head; the direct-party usage does not itself require appointing an agent.",
          "article_target_ids": [
            "definition:002",
            "usage_note:002"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-002",
              "support_summary": "Merriam-Webster general noun1 and Legal Definition noun1 give the broad leading-person/direct participant range; authority is typical, not required."
            },
            {
              "source_fact_id": "F-003",
              "support_summary": "Merriam-Webster directly gives the educational executive sense."
            },
            {
              "source_fact_id": "F-014",
              "support_summary": "Cambridge independently gives school head."
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
            "definition:005",
            "usage_note:005"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-007",
              "support_summary": "Merriam-Webster gives leading performer."
            },
            {
              "source_fact_id": "F-018",
              "support_summary": "Collins supplies performer and orchestral uses."
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
            "definition:003",
            "usage_note:003"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-008",
              "support_summary": "Merriam-Webster defines the capital-sum sense."
            },
            {
              "source_fact_id": "F-015",
              "support_summary": "Cambridge independently covers lending, borrowing, and investment."
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
              "support_summary": "Investor.gov supplies the government finance definition."
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
            "definition:003",
            "usage_note:003"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-025",
              "support_summary": "Wex directly defines trust principal and its income contrast."
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
            "definition:004",
            "usage_note:004",
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
            "usage_note:006"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-005",
              "support_summary": "Merriam-Webster supplies the criminal-participant sense."
            },
            {
              "source_fact_id": "F-021",
              "support_summary": "Collins independently compares principal and accessory and makes the classification context explicit."
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
            "usage_note:007"
          ],
          "source_supports": [
            {
              "source_fact_id": "F-006",
              "support_summary": "Merriam-Webster gives primary or ultimate liability."
            },
            {
              "source_fact_id": "F-022",
              "support_summary": "Collins independently gives the obligation sense."
            },
            {
              "source_fact_id": "F-026",
              "support_summary": "Wex directly states the surety and guarantor contrast."
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
        }
      ],
      "recheck_stop_recoveries": [
        {
          "recovered_at": "2026-09-08T16:17:22.084712+09:00",
          "previous_stop_reason": "post-cold recheck limit reached with adopted corrections awaiting verification",
          "previous_open_questions": [
            "Translation continuity and sense-order corrections need a second checker round; source-first standard profile permits only one."
          ]
        }
      ]
    }
  },
  "resolutions": {
    "schema_version": "resolutions_v1",
    "stage": "resolutions",
    "run_id": "resolution-principal-20260908T045228Z-e5bdb73f",
    "context_id": "resolution-principal-context-20260908T045228Z-e5bdb73f",
    "input_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
    "prompt_sha256": "7dfcaa0a828a334dbb84d1d31ed97312d0a9661a7aca70a7815a9f88b31ea2f1",
    "input_artifacts": [
      "entry_body",
      "all_findings"
    ],
    "recorded_at": "2026-09-08T08:01:13.797000+00:00",
    "resolutions": [
      {
        "id": "normal-sense-structure-001",
        "finding_id": "normal-sense-structure-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Fixed union U-002 and fact F-002 directly support a person with controlling authority or a leading position, while the draft confined the person sense to education titles.",
        "required_changes": [
          "Give the supported authority or leading-position noun use an explicit home without inventing a new frame."
        ],
        "implemented_changes": [
          "Broadened sense 2's heading and definition to the supported authority or leading-position use while retaining education as its prominent conventional title use."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-sense-structure-002",
        "finding_id": "normal-sense-structure-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "U-003, F-007, and F-018 support an established leading-performer use beyond orchestral section leaders.",
        "required_changes": [
          "Extend sense 3 only to the directly supported performing-arts range."
        ],
        "implemented_changes": [
          "Expanded sense 3's heading, definition, register, grammar note, core-image branch, and usage note to leading performers in the performing arts and orchestral principals."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-sense-structure-003",
        "finding_id": "normal-sense-structure-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "U-005 and F-025 directly define trust principal as the property or corpus distinct from income.",
        "required_changes": [
          "Integrate the supported trust-corpus use without treating all principal as a money amount."
        ],
        "implemented_changes": [
          "Added trust principal to sense 4's heading, definition, domain note, grammar note, usage note, and core-image branch."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-frame-relation-001",
        "finding_id": "normal-frame-relation-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The generic possessive slot licensed organizations outside the performing-arts role described by the sense.",
        "required_changes": [
          "Do not expose an unrestricted organization slot for this specialized noun."
        ],
        "implemented_changes": [
          "Removed the generic possessive construction from the grammar line; the remaining collocation explicitly names an orchestra."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-frame-relation-002",
        "finding_id": "normal-frame-relation-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The missing-example symptom came from an asserted authorize/appoint frame that the frozen facts did not establish as a complete construction; adding another unevidenced example would compound the issue.",
        "required_changes": [
          "Remove the unsupported complete frame rather than manufacture a matching example."
        ],
        "implemented_changes": [
          "Reduced the agency grammar line to the directly grounded principal-agent relationship and on-behalf relationship, and removed the unsupported duty collocation."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-frame-relation-003",
        "finding_id": "normal-frame-relation-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Principal and interest are related components, not opposites on an accepted lexical opposition axis.",
        "required_changes": [
          "Remove interest from the antonym inventory and retain the useful contrast as usage guidance."
        ],
        "implemented_changes": [
          "Deleted the interest antonym block and stated the related-component contrast in the finance usage note."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-example-attribution-001",
        "finding_id": "normal-example-attribution-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The original liable-as-principal example did not distinguish obligation liability from an agency principal.",
        "required_changes": [
          "Add a directly supported surety or guarantor contrast to disambiguate the role."
        ],
        "implemented_changes": [
          "Extended the example and translation with the guarantor's secondary liability, binding it to the obligation-law sense."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-qualification-001",
        "finding_id": "normal-qualification-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The performing-arts noun is a specialized low-frequency use in English overall, so 6/10 overstated its encounter frequency.",
        "required_changes": [
          "Lower the English-wide frequency while retaining the established specialist label."
        ],
        "implemented_changes": [
          "Changed sense 3 from 6/10 to 3/10 and retained its performing-arts and orchestral domain qualification."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-evidence-001",
        "finding_id": "normal-evidence-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "C-002's education and authority facts did not support the performing-arts definition target.",
        "required_changes": [
          "Remove the cross-sense target while preserving C-003's performer support."
        ],
        "implemented_changes": [
          "Removed definition:003 from C-002 and kept performing-arts support exclusively under C-003."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-evidence-002",
        "finding_id": "normal-evidence-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The fixed adjective facts support meaning and attested noun combinations, not the draft's full article, number, and preposition system.",
        "required_changes": [
          "Restrict the grammar claim to the supported attributive shape and stop binding definition evidence to the full frame."
        ],
        "implemented_changes": [
          "Simplified sense 1 grammar to attributive principal plus noun and removed grammar_pattern:001 from C-001's source binding."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-evidence-003",
        "finding_id": "normal-evidence-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The education facts establish the role but do not establish the complete determiner and of-complement templates as quoted.",
        "required_changes": [
          "Replace the unevidenced complete frame with a count-noun role note and narrow its source binding."
        ],
        "implemented_changes": [
          "Replaced the sense 2 grammar templates with a count-noun role description and removed grammar_pattern:002 from C-002."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-evidence-004",
        "finding_id": "normal-evidence-004",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The performer facts establish the specialist role but not an unrestricted possessive-plus-plural frame.",
        "required_changes": [
          "Remove the generalized possessive template and narrow its source binding."
        ],
        "implemented_changes": [
          "Replaced the sense 3 grammar template with a specialist count-noun role note and removed grammar_pattern:003 from C-003."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-evidence-005",
        "finding_id": "normal-evidence-005",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The finance facts establish the capital-versus-interest concept and repayment effect, not every article-bearing construction listed in the grammar line.",
        "required_changes": [
          "Replace the complete construction list with a meaning-and-countability note grounded in the fixed facts."
        ],
        "implemented_changes": [
          "Replaced sense 4's grammar list with a finance/trust noun-use note and removed grammar_pattern:004 from C-004."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-evidence-006",
        "finding_id": "normal-evidence-006",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The agency facts support authority and acting on behalf but not the full appoint/authorize and owe-a-duty syntax asserted by the draft.",
        "required_changes": [
          "Keep only directly grounded relations and remove the grammar target from C-006."
        ],
        "implemented_changes": [
          "Removed the appoint/authorize and duty frames, retained the directly grounded relationship expressions, and removed grammar_pattern:005 from C-006."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-evidence-007",
        "finding_id": "normal-evidence-007",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The criminal-law facts support participant classification and the accessory contrast, but the inventory did not support the historical degree claim or the complete quoted frames.",
        "required_changes": [
          "Remove the historical-degree material and narrow the grammar/source binding to the supported classification."
        ],
        "implemented_changes": [
          "Removed the degree statement and example, simplified the grammar note, removed grammar_pattern:006 from C-007, and corrected F-005's support summary to omit historical degrees."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "normal-evidence-008",
        "finding_id": "normal-evidence-008",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The obligation facts establish primary liability and the surety/guarantor contrast, not each complete phrase in the former grammar list.",
        "required_changes": [
          "State the directly supported role contrast without claiming the full constructions are source-attested."
        ],
        "implemented_changes": [
          "Replaced sense 7's grammar list with a count-noun role contrast and removed grammar_pattern:007 from C-008."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
      },
      {
        "id": "COLD-001",
        "finding_id": "COLD-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "The core image's generic central-person wording licensed uses broader than either the directly supported authority sense or the draft's established institutional and specialist roles.",
        "required_changes": [
          "Tie the core image to the supported authority, education, performing-arts, finance/trust, and legal roles."
        ],
        "implemented_changes": [
          "Rewrote the core summary and branches to name the supported roles and to avoid presenting principal as a free synonym for any important person."
        ],
        "resolved_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9"
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
        "id": "etymology:002",
        "kind": "etymology",
        "location": "line:9",
        "section": "＃語源",
        "sense": "",
        "text_sha256": "284fb27bdea3cd9757538899841370acc051cd87d6997136f5f08ec179b5a549",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "同語源語には `prince`「王子、君主」と `principality`「公国」がある。綴りのよく似た `principle`「原理、原則」も同じラテン語群に由来するが、現代英語では別の単語として使い分ける。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:13",
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
        "location": "line:14",
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
        "location": "line:15",
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
        "location": "line:19",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "1a0dd92a59931374d4a11a5acb11b43d9b52fcaa785ddf672e6823c9f0dc1b95",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`principal` の中心は、「重要度・権限・責任・金額の土台として第一に位置する」である。形容詞では主要なものを選び出し、名詞では組織・活動の主要人物や取引の当事者本人、教育機関の長や舞台芸術で確立した主要演者、利息・収益に対する元の金額や信託収益に対する財産本体、法的関係の主要当事者を指す。"
      },
      {
        "id": "core_image:002",
        "kind": "core_image",
        "location": "line:20",
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
        "location": "line:21",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "420b5ad9047584426e27a3b5ea822a4983aef169c1f1f35033b5215fc7c84a71",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・組織・活動・取引で主要な立場にある人、特に教育機関の長 → 「主要人物・当事者、校長、学長」（語義2）"
      },
      {
        "id": "core_image:004",
        "kind": "core_image",
        "location": "line:22",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "1993aaadeef34da6206e220e4a390261825a1a0ac4fe5c7a537acd4f0467510d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・利息・収益に対する基礎額、または信託収益に対する財産本体 → 「元金、元本、信託元本」（語義3）"
      },
      {
        "id": "core_image:005",
        "kind": "core_image",
        "location": "line:23",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "5cccfda76aef7d022e3e7d2891235f42154a2a7f7f3aa5db7048a009a8130296",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・代理関係で権限の源として第一に位置する当事者 → 「本人、依頼者」（語義4）"
      },
      {
        "id": "core_image:006",
        "kind": "core_image",
        "location": "line:24",
        "section": "＃コアイメージ",
        "sense": "",
        "text_sha256": "359bb66d2c6f215603eb72825a6275b2bdd9aeef023481b59a4fc447ee64865a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・舞台芸術で主要な役割を担う人 → 「主要演者、オーケストラの首席奏者」（語義5）"
      },
      {
        "id": "core_image:007",
        "kind": "core_image",
        "location": "line:25",
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
        "location": "line:26",
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
        "location": "line:30",
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
        "location": "line:32",
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
        "location": "line:34",
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
        "location": "line:36",
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
        "location": "line:38",
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
        "location": "lines:42-45",
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
        "location": "lines:47-50",
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
        "location": "lines:52-55",
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
        "location": "lines:57-60",
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
        "location": "lines:62-65",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "57f15c13e84d19024c1b57fa580037cd38745d3e2ea220a3d2693820262b73c9",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`the principal place of business`\n用途: 企業の主たる事業所を指す定着した法律・ビジネス表現。該当場所を決める法的基準や効果は、適用される法や法域によって異なる。\n例: The company moved its principal place of business to Osaka.\n訳: その会社は主たる事業所を大阪に移した。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:67",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞】主要な、最も重要な、第一の",
        "text_sha256": "359fcbb1968dadcf093bd71dc205188bec713d8eb4d9181d51c5c589ef731dfc",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`principal` と `principle` は綴りも意味も異なる。`principal` には形容詞で「最も重要な」を表す用法があり、別に人や金額などを指す名詞用法もある。一方、`principle` は「原理・原則」を表す名詞である。したがって「基本原則」は `basic principle` であり、`basic principal` ではない。"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:71-76",
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
        "location": "lines:78-83",
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
        "location": "lines:85-90",
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
        "location": "lines:92-97",
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
        "location": "lines:101-106",
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
        "location": "lines:108-113",
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
        "location": "line:115",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "e697726d77e33d46bee8004e6192379d391a8c586117750fafa22e60964cb771",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "2. 【名詞・可算】主要人物・当事者；特に校長、学長"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:117",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "b5a5415b53915555299bcb365accc730230d049ac8c785c744443cea8166ccd0",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "組織・事業・交渉などで主導的地位を持つ人、または行為・取引の主要な当事者。権限を持つ人を指すことが多いが、組織を支配することを必須とはしない。特に教育では、学校、カレッジ、その他の教育機関を管理する最高責任者を指す。教育上どの種類の機関を指すかは地域と制度によって異なる。"
      },
      {
        "id": "frequency:002",
        "kind": "frequency",
        "location": "line:119",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "223f0f3bb105d64687ce0ff83ae044846c2f48c7a55d9d015dbc0ce12503d473",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈8/10〉"
      },
      {
        "id": "register:002",
        "kind": "register",
        "location": "line:121",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "2fef7b364b57c4f9071be1e78ee90c1e8b2fb0f37a2dfe94057d63035f5755bb",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "標準～やや形式的。教育分野では学校・教育機関の長を表し、イングランドではカレッジの長を指す場合がある。"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:123",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "f83ed2e5723bb328141395431db2b1af68189a34798bccb0453fd70b45f3d8d1",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "可算名詞として、組織・活動の主要人物や取引の当事者を指す。`act as principal` は取引の当事者本人の資格で行動することを表す。教育文脈では学校・カレッジなどの長を表す役職名として用いる。"
      },
      {
        "id": "collocation:006",
        "kind": "collocation",
        "location": "lines:127-130",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "ef69b41d92055c7288654af511d706b973bf8567d721d2be275b55ede09585e3",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`the principal of 〈限定詞を含む学校・教育機関の名詞句〉`\n用途: どの教育機関の長かを `of` で示す。\n例: The principal of the college welcomed the new students.\n訳: そのカレッジの学長は新入生を歓迎した。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:132-135",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "9a5e8281af0651072d77a283c5abd55141e54bacade93f8c017d422bcce0bcae",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`a school principal`\n用途: 学校を管理する責任者を職種として表す。\n例: The school principal met with parents after the incident.\n訳: 校長はその出来事の後、保護者と面会した。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:137-140",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "be62863a801407a484da6a4923a08a129941451a909161297b0906c10a2e95e6",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`a college principal`\n用途: カレッジを管理する責任者を職種として表す。\n例: A college principal addressed the graduating class.\n訳: カレッジの学長が卒業生に向けて話した。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:142-145",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "c7c490975675af65505d4bea61602e2220168f53ae2a555cf339371781484cc9",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`act as principal`\n用途: 他者の代理人としてだけではなく、取引の当事者本人の資格で行動することを表す。\n例: In this transaction, the firm acts as principal, buying the goods for its own account rather than as another company's agent.\n訳: この取引では、その会社は当事者本人として行動し、別会社の代理人としてではなく自己の勘定で商品を購入する。"
      },
      {
        "id": "usage_note:002",
        "kind": "usage_note",
        "location": "line:147",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "479bf2906cd7b680aa0ce9d1f069df4cf7f04259f7bdd58d81e47402239a9e69",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "一般の「重要人物」を自由に指す語ではなく、特定の組織・活動・取引で主要な立場にある人や当事者に用いる。取引の `principal` は当事者本人の立場を示し、自分が代理人を任命していることを必須としない。代理人との関係で権限の源となる本人は語義4で詳しく扱う。教育上の役職名は地域や制度によって異なるため、日本語の「校長」を機械的にすべて `principal` としない。"
      },
      {
        "id": "synonym:005",
        "kind": "synonym",
        "location": "lines:151-156",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算】主要人物・当事者；特に校長、学長",
        "text_sha256": "c265c1fd04a84f63fb60e7cb00a6d1de188fac2494c6b4ddbfe0922c75b61a98",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・head\n定義: 学校・組織などの長。\n頻度: 〈9/10〉\n違い: `head` は組織の長を広く表す。`principal` は権限・主導的地位を持つ人を表し、特に教育機関で役職名として用いられる。\n例: She is the head of a large secondary school.\n訳: 彼女は大規模な中等学校の校長である。"
      },
      {
        "id": "sense_boundary:003",
        "kind": "sense_boundary",
        "location": "line:158",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "7021678189f9783b20526be51ac39a64d567c582aeb5ab5febc877ec40bd8639",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本"
      },
      {
        "id": "definition:003",
        "kind": "definition",
        "location": "line:160",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "37f87f6e1bbb984d2bfb3ed69e8e68ea47c895b431b6fe7959b375a5509dfd73",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。信託法では、収益と区別される信託財産そのもの、すなわち信託元本・corpusを指す。"
      },
      {
        "id": "frequency:003",
        "kind": "frequency",
        "location": "line:162",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "4c83f924416ef4455522dc0ab9ad637bb8820d1ecc7c146513681f28e8bd4b71",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈7/10〉"
      },
      {
        "id": "register:003",
        "kind": "register",
        "location": "line:164",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "db5a8c219e02a4831c9d1c6d8797be7ac432a4d0e8d358ee2cf15457011274fb",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "金融、融資、投資、会計、信託法。金融義は日常的なローン説明にも現れ、信託義は専門的である。"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:166",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "ccc3927bbac93548d0ccc821ffb0820e4b708493662106fce20c703386db8e50",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "金融では利息・収益の基礎となる金額を、信託法では収益と区別される財産本体を表す名詞として用いる。"
      },
      {
        "id": "collocation:010",
        "kind": "collocation",
        "location": "lines:170-173",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "1cfb7f70cb274f5173350345e94ffd5b8ae94f08d0407f9e63f890bcfd74a4d3",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`principal and interest`\n用途: 借入金の元金と、それに対して発生する利息を対で示す。\n例: The monthly payment includes both principal and interest.\n訳: 毎月の返済額には元金と利息の両方が含まれる。"
      },
      {
        "id": "collocation:011",
        "kind": "collocation",
        "location": "lines:175-178",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "edae6599544f929386e133b62934aa4c732905d8db2d5f161fe13f309c961a0f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`pay down the principal`\n用途: 返済によって未返済の元金を減らすことを表す。\n例: Extra payments can help you pay down the principal faster.\n訳: 追加返済をすれば、元金をより早く減らせる。"
      },
      {
        "id": "collocation:012",
        "kind": "collocation",
        "location": "lines:180-183",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "155b17cb5b662c2a715ff55ddcf99ee3e08c15068450b97b5bb839d0504a5a4c",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`protect the principal`\n用途: 投資で、元本そのものの毀損を避けることを表す。\n例: The fund aims to protect the principal—the amount originally invested—while generating modest returns.\n訳: そのファンドは、控えめな収益を生みながら元本、すなわち当初の投資額を保全することを目指している。"
      },
      {
        "id": "collocation:013",
        "kind": "collocation",
        "location": "lines:185-188",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "bcfad238947d78892bada3fefff1fb0c22dc178cd8ada636150422cd006e1b34",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`repay principal`\n用途: 利息とは別に借入の元金を返済することを表す。\n例: The borrower will begin repaying principal next year.\n訳: 借り手は来年、元金の返済を開始する。"
      },
      {
        "id": "usage_note:003",
        "kind": "usage_note",
        "location": "line:190",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "d001ea049b06832bc08d3d0bcf7eb6e4653b6a3df2192a21da0f192a12380927",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`principal` は元の基礎額、`interest` は借入の対価または貸付・投資から生じる追加額であり、反意語ではなく関連する別の金額構成要素である。信託では `principal` が財産本体、`income` がそこから生じる収益を指す。`repay the principal` では `principal` 自体が目的語の名詞になる。日本語の「元利金」は `principal and interest` であり、`principal interest` とはしない。"
      },
      {
        "id": "synonym:006",
        "kind": "synonym",
        "location": "lines:194-199",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・金融／信託法】元金、元本、信託財産の元本",
        "text_sha256": "5ce1d09ecf03136c137d2220261d2d931c7c37c7ea18438c5a30554e6a8321a2",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・capital\n定義: 投資・事業に用いられる資金または資産。\n頻度: 〈9/10〉\n違い: `capital` は事業資金・生産資産まで広く表す。`principal` は特定の貸付・借入・投資で利息や収益の基礎となる元の額を指す。\n例: The company raised additional capital from investors.\n訳: その会社は投資家から追加資金を調達した。"
      },
      {
        "id": "sense_boundary:004",
        "kind": "sense_boundary",
        "location": "line:201",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "d4d3865112e041b15988c9762fd822ca8689faced2e1209db881057c9667cc1c",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者"
      },
      {
        "id": "definition:004",
        "kind": "definition",
        "location": "line:203",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "14a09851610b29919b97d8cf86318989686a5c392b0bbb7dd9678e4c126879c4",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "別の人・法人である `agent` に、自分のために行動する権限を与える人または法人。代理人は本人のために行動し、代理関係では `principal` が権限の源となる。米国の一般的な代理法の説明では、代理人は本人のために、かつ本人の支配の下で行動する。具体的な成立要件は適用法によって異なり得る。"
      },
      {
        "id": "frequency:004",
        "kind": "frequency",
        "location": "line:205",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "f75683d2ec70c01e8ef877fe56064d1d46ce1e20d9e5a13b41fe1f03202dbee8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈5/10〉"
      },
      {
        "id": "register:004",
        "kind": "register",
        "location": "line:207",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "73e5f4ab1e818f59896212051d3e1cbd2c94f11774ce6576471146222ecf74bc",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "法律、保険、不動産、商取引。日常語として人を「依頼主」と呼ぶだけなら `client` が自然な場合も多い。"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:209",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "85abc4deb9f0d9671843d3dfa9c2fbc3ab8f942c426132cac8ffa0b003c01789",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`a principal-agent relationship`＝本人・代理人関係"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:209",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "4df55c3bf5a7207372bf743629d014b75789666926ea68b23723ee909395a209",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`act on behalf of the principal`＝本人を代理して行動する"
      },
      {
        "id": "collocation:014",
        "kind": "collocation",
        "location": "lines:213-216",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "bf5d0e5cf8f37ad1abb6ea453cc81ba3f799267473a34c69802700d818dbecb7",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`a principal-agent relationship`\n用途: 権限を与える本人と、そのために行動する代理人との関係を表す。\n例: The contract created a principal-agent relationship between the owner and the broker.\n訳: その契約は所有者と仲介業者の間に本人・代理人関係を成立させた。"
      },
      {
        "id": "collocation:015",
        "kind": "collocation",
        "location": "lines:218-221",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "28de6ded590b27ced1e143c49506cbb12314d9475e752d038551c5955a6d8307",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`act on behalf of the principal`\n用途: 代理人が本人を代理して行動することを表す。\n例: The agent may sign the document on behalf of the principal.\n訳: 代理人は本人を代理してその書類に署名できる。"
      },
      {
        "id": "usage_note:004",
        "kind": "usage_note",
        "location": "line:223",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "22eff499d885e31f96c79abcc2224f55db5626025a58eb292ae752b0b7dcc1fa",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "法律用語の `principal` は「重要人物」という一般義だけでなく、`agent` に対する特定の関係上の役割名である。`client` はサービスを受ける顧客・依頼人を広く指すが、必ずしも代理権を与える法律上の本人ではない。`the principal's agent` は「本人の代理人」であり、「校長の代理人」と決めつけない。"
      },
      {
        "id": "synonym:007",
        "kind": "synonym",
        "location": "lines:227-232",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【名詞・可算・法律／代理関係】本人、依頼者、代理権を与える当事者",
        "text_sha256": "8a100dc4cfab377b2f5c1f2958efa30d236575e253ef680a343da757dc4d3bb1",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・mandator\n定義: 他人に委任・代理の権限を与える者。\n頻度: 〈2/10〉\n違い: 特定の法体系や専門文脈で使われる低頻度語である。\n例: The mandator may revoke the mandate subject to the agreement.\n訳: 委任者は、契約の定めに従い、委任を撤回できる。"
      },
      {
        "id": "sense_boundary:005",
        "kind": "sense_boundary",
        "location": "line:234",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "70b203575ce7519480555e76f86decab5ec99c6becea8dc3099e04cc2429db16",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者"
      },
      {
        "id": "definition:005",
        "kind": "definition",
        "location": "line:236",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "e0abacfc1040b69a7784fdf4eee9dc47585c584de13d05927e2bffe74cf45546",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "舞台芸術で主要な役を担う演者、またはオーケストラで一つのセクションを率いる奏者。一般の重要人物ではなく、芸術分野で確立した役割名を指す。"
      },
      {
        "id": "frequency:005",
        "kind": "frequency",
        "location": "line:238",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "a0e445b4ea32382084179e64d42d17cc5ca8def51850cf67e191301932796344",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈3/10〉"
      },
      {
        "id": "register:005",
        "kind": "register",
        "location": "line:240",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "988adda62185ee12eec15ac5ac092052d77fb841ee2fa34049263a5f60d5c01c",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "舞台芸術・オーケストラ・音楽の専門語。"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:242",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "bc2b18a43e8ddcd6c708aa392a91c955ef514fd94f8c7427ca405b3897549dbb",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "可算名詞として、舞台芸術・音楽で確立した主要演者や首席奏者の役割を表す。"
      },
      {
        "id": "collocation:016",
        "kind": "collocation",
        "location": "lines:246-249",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "b26794562e4ff3e81de7004b0fc98832a4fe4eee4cabd529bd1a4d8f4f9d6dee",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`one of the orchestra's principals`\n用途: オーケストラで各セクションを率いる奏者を名詞で指す。\n例: As one of the orchestra's principals, she leads the cello section.\n訳: オーケストラの首席奏者の一人として、彼女はチェロのセクションを率いている。"
      },
      {
        "id": "usage_note:005",
        "kind": "usage_note",
        "location": "line:251",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "facc08ddb6d89fae24fe44402f941f4ccda66fbc155f9899bd9f989a15229195",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "舞台芸術やオーケストラ内で確立した役割名として用い、一般の「重要人物」には広げない。"
      },
      {
        "id": "synonym:008",
        "kind": "synonym",
        "location": "lines:255-260",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【名詞・可算】舞台芸術の主要演者、オーケストラの首席奏者",
        "text_sha256": "fac8779a8c865def95d243d10507f8dde8cb83efd694a963758811b319273cd6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・section leader\n定義: オーケストラで一つのセクションを率いる奏者。\n頻度: 〈4/10〉\n違い: 役割を説明する一般的な表現で、`principal` は確立した役職名として用いられる。\n例: The section leader rehearsed the difficult passage.\n訳: セクションの首席奏者は難しい楽節を練習した。"
      },
      {
        "id": "sense_boundary:006",
        "kind": "sense_boundary",
        "location": "line:262",
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
        "location": "line:264",
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
        "location": "line:266",
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
        "location": "line:268",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "d609cd516794fbb67fdf8f0ba03b201698be0ef4de47b31b46857aeaf343a9d3",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "刑事法の専門語。犯罪に関するこの語義は法域によって分類法が異なる。"
      },
      {
        "id": "grammar_pattern:007",
        "kind": "grammar_pattern",
        "location": "line:270",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "c9dacb2d22131b7e7d5722a1c11157dceae2709674dc5f1192ade194df9a537b",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "刑事法で可算名詞として用い、犯罪関与者を適用される法的分類に従って指す。"
      },
      {
        "id": "collocation:017",
        "kind": "collocation",
        "location": "lines:274-277",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "c4a6f55b49045fc3817494854a2e9a1563d9592cbc3e533cc774a68c784b9ad1",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`a principal in a crime`\n用途: 犯罪について直接の刑事責任を負う者を指す。\n例: The court held him directly criminally liable as a principal in the crime, rather than classifying him as an accessory.\n訳: 裁判所は彼をその犯罪の `accessory` と分類するのではなく、`principal` として直接の刑事責任を負うものとした。"
      },
      {
        "id": "collocation:018",
        "kind": "collocation",
        "location": "lines:279-282",
        "section": "＃意味・用法・関連表現",
        "sense": "6. 【名詞・可算・刑事法】適用法上 `principal` と分類される犯罪関与者",
        "text_sha256": "b4016ea75dc66c1f40ce64ccb776c855f0f53bc63b871fbdb914dd48a1afddd2",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`treat someone as a principal`\n用途: 一定の関与者を適用法上 `principal` として扱うことを表す。\n例: The statute treats a person who knowingly assists the offense as a principal.\n訳: その制定法は、情を知って犯罪を援助する者を `principal` として扱う。"
      },
      {
        "id": "usage_note:006",
        "kind": "usage_note",
        "location": "line:284",
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
        "location": "lines:288-293",
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
        "location": "line:295",
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
        "location": "line:297",
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
        "location": "line:299",
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
        "location": "line:301",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "4ec9974bf35cdcb3b2c182a1e480471eb0839e4b9bdc471df554b8627cfbc621",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "債務法・保証法の専門語。"
      },
      {
        "id": "grammar_pattern:008",
        "kind": "grammar_pattern",
        "location": "line:303",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "9df5f0bd907cd1ee01119b323917fc22fbf41db9872421ba0e533998e7f958b7",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "可算名詞として、保証人・`surety`・`guarantor` と対比される第一次的責任者を指す。"
      },
      {
        "id": "collocation:019",
        "kind": "collocation",
        "location": "lines:307-310",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "ed07baa54f5407cb4121e37ed25a340464f316e8d95dea81f3c6e1912d936167",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`be liable as principal`\n用途: 二次的な保証責任ではなく、主たる当事者として第一次的責任を負うことを示す。\n例: Under the agreement, the company remains liable as principal for the debt, while the guarantor is only secondarily liable.\n訳: その契約の下で、会社はその債務について主たる当事者として引き続き責任を負い、保証人は二次的にのみ責任を負う。"
      },
      {
        "id": "collocation:020",
        "kind": "collocation",
        "location": "lines:312-315",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "d2e6eedf93bbed71318a807dabce33538e989b34cbde0d0a13bf0fc6286e02ac",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`the obligation of the principal`\n用途: 主たる当事者が第一次的に負う義務を示す。\n例: The obligation of the principal is to repay the debt; the guarantor is only secondarily liable.\n訳: 主たる義務者の義務は債務を返済することであり、保証人は二次的にのみ責任を負う。"
      },
      {
        "id": "collocation:021",
        "kind": "collocation",
        "location": "lines:317-320",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "c31c9ece7495d5aac00c288042c70b54102298e802d8c553c8f940d97e0ce02f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`the principal and the surety`\n用途: 第一次的責任を負う当事者と、保証する側を対で示す。\n例: Under the agreement, the principal and the surety are primarily and secondarily liable for the debt, respectively.\n訳: その契約の下で、主たる義務者と保証人は、その債務についてそれぞれ第一次的責任と二次的責任を負う。"
      },
      {
        "id": "usage_note:007",
        "kind": "usage_note",
        "location": "line:322",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "d33b8abc06aa795fdab8f18188e91bd08bbdeabb85f93bcf49aec59138b1a137",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "この語義では、`principal` は `be liable as principal` のように人・法人を指す名詞である。`principal debtor` や `principal obligor` では語義1の形容詞が `debtor`・`obligor` を修飾するため、名詞単独の構造と区別する。また、金額を指す語義3の「元金」とも区別する。"
      },
      {
        "id": "synonym:010",
        "kind": "synonym",
        "location": "lines:326-331",
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
        "location": "lines:333-338",
        "section": "＃意味・用法・関連表現",
        "sense": "7. 【名詞・可算・債務／保証法】主たる債務者・義務者、第一次的責任者",
        "text_sha256": "69be5ed0225c2445b4462ae603a41d640fd5f32056ac0aabf582e57dc3907b52",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・debtor\n定義: 金銭その他の債務を負う者。\n頻度: 〈6/10〉\n違い: `debtor` は債務者一般を指す。`principal` は保証関係で第一次的責任を負う当事者という役割を強調する。\n例: The debtor made the payment on time.\n訳: 債務者は期限どおりに支払った。"
      }
    ],
    "relation_results": [
      {
        "id": "risk_sense_pair:001",
        "kind": "risk_sense_pair",
        "target_ids": [
          "sense_boundary:001",
          "sense_boundary:007"
        ],
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: usage_note:007 explicitly contrasts sense 7 with sense 1",
        "text_sha256": "ce63fbb1b38dc169ff63e7ca1f4d0872ad6dceca00de80b09c482500add689e0",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "risk_sense_pair:002",
        "kind": "risk_sense_pair",
        "target_ids": [
          "sense_boundary:002",
          "sense_boundary:004"
        ],
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: usage_note:002 explicitly contrasts sense 2 with sense 4",
        "text_sha256": "3c29951a9d793251b17602f66f590cecf3e5af59908106fb363f1e0c3016d5aa",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "risk_sense_pair:003",
        "kind": "risk_sense_pair",
        "target_ids": [
          "sense_boundary:003",
          "sense_boundary:007"
        ],
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: usage_note:007 explicitly contrasts sense 7 with sense 3",
        "text_sha256": "bc67e82a7daa0ebc4eebb6c29437a5839d05dba42f754b1423bff479e304d091",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "risk_sense_pair:004",
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
        "id": "example_translation:020",
        "kind": "example_translation",
        "target_ids": [
          "collocation:020"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "3aa15a03db6c5911970c1214d9e56ad47ecc60f9a9726f19bcf132c531ac61a5",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:021",
        "kind": "example_translation",
        "target_ids": [
          "collocation:021"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "43eec0b79bfe21c4bfcaa005e347305ec22ec75e745563ad0c1f41d75244a0b2",
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
          "collocation:007",
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "b5ed528c732f2f3f3074f4be86b3500868b7c69a03aef58ba3072c4a0c4a37a5",
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
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "39349fd252a6368811c09cfd502577605d67417a6940a7426146c99a18b995e6",
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
          "collocation:014",
          "collocation:015"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "34777a168decc73173fdf8ee80593aa609b568f01d10af3c280bb0457dedb0d4",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:005",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:005",
          "collocation:014",
          "collocation:015"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "482640854d448be9256fe411e0def2f80f451791ed0c1542fb56ec3dcbcd7c38",
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
          "synonym:008"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "08d1612a08e2521e253fc1943c4e67f9b8761f2c6459b2ddcb1d9871129e48d8",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:006",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:006",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "e7dd1711f2bf99786f658f84ec04b33667c90106ea8d96ef3016565de758f4a1",
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
        "id": "pattern_example_coverage:007",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:007",
          "collocation:017",
          "collocation:018"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "87c3f65227b1f0ecbf945ff32509a38d2670292a9075e2a3a1a3980abf4c18cc",
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
          "synonym:011"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "cb2bc6447c9fa30551b5de7239ab86fa4027f9611047672fb31993fae54db1f2",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:008",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:008",
          "collocation:019",
          "collocation:020",
          "collocation:021"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "dd296aee156ce53499d69e999517490b079e2bb87dcebcf3ea683d080aca5969",
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
        "id": "independent-1",
        "surface_form": "principal",
        "frame": "principal + noun",
        "meaning": "主要な、最も重要な、第一の",
        "disposition": "included",
        "rationale": "principal の「principal + noun」は「主要な、最も重要な、第一の」。重要性・地位の形容詞義が定義と例文に一貫して現れる。",
        "semantic_assertions": [
          {
            "id": "assertion-1",
            "statement": "時間的に最初であることだけを意味しない",
            "polarity": "must_hold",
            "scope": "principal + noun"
          }
        ]
      },
      {
        "id": "independent-2",
        "surface_form": "principal",
        "frame": "a principal source of income",
        "meaning": "複数ある主要な供給源の一つ",
        "disposition": "included",
        "rationale": "principal の「a principal source of income」は「複数ある主要な供給源の一つ」。不定冠詞の例も主要性を表し、唯一性を要求していない。",
        "semantic_assertions": [
          {
            "id": "assertion-2",
            "statement": "主要な供給源は一つに限定されない",
            "polarity": "must_hold",
            "scope": "a principal source of income"
          }
        ]
      },
      {
        "id": "independent-3",
        "surface_form": "principal",
        "frame": "one of the principal + plural noun",
        "meaning": "主要な複数の対象のうちの一つ",
        "disposition": "included",
        "rationale": "principal の「one of the principal + plural noun」は「主要な複数の対象のうちの一つ」。改革の立案者の例は最重要対象の複数性を保つ。",
        "semantic_assertions": [
          {
            "id": "assertion-3",
            "statement": "principal は複数の主要対象に適用できる",
            "polarity": "must_hold",
            "scope": "one of the principal + plural noun"
          }
        ]
      },
      {
        "id": "independent-4",
        "surface_form": "principal",
        "frame": "the principal place of business",
        "meaning": "主たる事業所",
        "disposition": "included",
        "rationale": "principal の「the principal place of business」は「主たる事業所」。形容詞と事業所名詞句の定着表現で、適用法による判定差も明示する。",
        "semantic_assertions": [
          {
            "id": "assertion-4",
            "statement": "この複合表現から principal 単独に事業所の名詞義を導かない",
            "polarity": "must_hold",
            "scope": "the principal place of business"
          }
        ]
      },
      {
        "id": "independent-5",
        "surface_form": "principal",
        "frame": "a principal of an organization",
        "meaning": "組織の主要人物・責任者",
        "disposition": "included",
        "rationale": "principal の「a principal of an organization」は「組織の主要人物・責任者」。組織・事業の主導的地位を持つ人という定義に含まれる。",
        "semantic_assertions": [
          {
            "id": "assertion-5",
            "statement": "組織を支配する者だけに限定しない",
            "polarity": "must_hold",
            "scope": "a principal of an organization"
          }
        ]
      },
      {
        "id": "independent-6",
        "surface_form": "principal",
        "frame": "the principals in a negotiation",
        "meaning": "交渉・活動の主要当事者",
        "disposition": "included",
        "rationale": "principal の「the principals in a negotiation」は「交渉・活動の主要当事者」。交渉などの主要な当事者が明示されている。",
        "semantic_assertions": [
          {
            "id": "assertion-6",
            "statement": "単に世間で有名な人物であることだけでは足りない",
            "polarity": "must_hold",
            "scope": "the principals in a negotiation"
          }
        ]
      },
      {
        "id": "independent-7",
        "surface_form": "principal",
        "frame": "the principal of a school or college",
        "meaning": "学校・教育機関の長",
        "disposition": "included",
        "rationale": "principal の「the principal of a school or college」は「学校・教育機関の長」。教育機関の長の定義と校長・カレッジの例が対応する。",
        "semantic_assertions": [
          {
            "id": "assertion-7",
            "statement": "教育機関の種類と役職呼称には地域・制度差がある",
            "polarity": "must_hold",
            "scope": "the principal of a school or college"
          }
        ]
      },
      {
        "id": "independent-8",
        "surface_form": "principal",
        "frame": "act as principal",
        "meaning": "取引の当事者本人として行動する",
        "disposition": "included",
        "rationale": "principal の「act as principal」は「取引の当事者本人として行動する」。自己勘定で購入する例により代理関係上の本人とは独立に具体化される。",
        "semantic_assertions": [
          {
            "id": "assertion-8",
            "statement": "代理人を任命することを必要条件にしない",
            "polarity": "must_hold",
            "scope": "act as principal"
          }
        ]
      },
      {
        "id": "independent-9",
        "surface_form": "principal",
        "frame": "principal and interest",
        "meaning": "利息と区別される借入・貸付の元金",
        "disposition": "included",
        "rationale": "principal の「principal and interest」は「利息と区別される借入・貸付の元金」。返済の構成要素として元金と利息を区別する。",
        "semantic_assertions": [
          {
            "id": "assertion-9",
            "statement": "元金と利息は金額構成要素の区別であり反意語ではない",
            "polarity": "must_hold",
            "scope": "principal and interest"
          }
        ]
      },
      {
        "id": "independent-10",
        "surface_form": "principal",
        "frame": "pay down the principal",
        "meaning": "未返済元金を返済により減らす",
        "disposition": "included",
        "rationale": "principal の「pay down the principal」は「未返済元金を返済により減らす」。残額が減る作用方向を用途と訳がともに保つ。",
        "semantic_assertions": [
          {
            "id": "assertion-10",
            "statement": "元金への支払いは未返済元金を減らす",
            "polarity": "must_hold",
            "scope": "pay down the principal"
          }
        ]
      },
      {
        "id": "independent-11",
        "surface_form": "principal",
        "frame": "repay principal",
        "meaning": "借入の元金を返済する",
        "disposition": "included",
        "rationale": "principal の「repay principal」は「借入の元金を返済する」。principal は返済の対象となる金額の名詞である。",
        "semantic_assertions": [
          {
            "id": "assertion-11",
            "statement": "返済する主体と返済される金額を入れ替えない",
            "polarity": "must_hold",
            "scope": "repay principal"
          }
        ]
      },
      {
        "id": "independent-12",
        "surface_form": "principal",
        "frame": "protect the principal",
        "meaning": "投資の元本を保全する",
        "disposition": "included",
        "rationale": "principal の「protect the principal」は「投資の元本を保全する」。投資額の保全目標を述べ、保証の存在までは主張しない。",
        "semantic_assertions": [
          {
            "id": "assertion-12",
            "statement": "投資元本はそこから生じる収益と区別される",
            "polarity": "must_hold",
            "scope": "protect the principal"
          }
        ]
      },
      {
        "id": "independent-13",
        "surface_form": "principal",
        "frame": "the principal of a trust",
        "meaning": "信託収益と区別される信託財産本体",
        "disposition": "included",
        "rationale": "principal の「the principal of a trust」は「信託収益と区別される信託財産本体」。金額義だけに還元せず財産本体・corpus として明示する。",
        "semantic_assertions": [
          {
            "id": "assertion-13",
            "statement": "信託元本は現金額だけに限定されない",
            "polarity": "must_hold",
            "scope": "the principal of a trust"
          }
        ]
      },
      {
        "id": "independent-14",
        "surface_form": "principal",
        "frame": "a principal-agent relationship",
        "meaning": "本人と代理人の権限関係",
        "disposition": "included",
        "rationale": "principal の「a principal-agent relationship」は「本人と代理人の権限関係」。権限を与える側と本人のために行動する側の区別が保たれる。",
        "semantic_assertions": [
          {
            "id": "assertion-14",
            "statement": "principal は agent のために代理行為をする側ではなく権限の源となる",
            "polarity": "must_hold",
            "scope": "a principal-agent relationship"
          }
        ]
      },
      {
        "id": "independent-15",
        "surface_form": "principal",
        "frame": "act on behalf of the principal",
        "meaning": "代理人が本人のために行動する",
        "disposition": "included",
        "rationale": "principal の「act on behalf of the principal」は「代理人が本人のために行動する」。例文の主語は agent であり principal は代理される側である。",
        "semantic_assertions": [
          {
            "id": "assertion-15",
            "statement": "on behalf of の補語はこの例で本人を指す",
            "polarity": "must_hold",
            "scope": "act on behalf of the principal"
          }
        ]
      },
      {
        "id": "independent-16",
        "surface_form": "principal",
        "frame": "a principal in a stage production",
        "meaning": "舞台芸術で主要な役を担う演者",
        "disposition": "included",
        "rationale": "principal の「a principal in a stage production」は「舞台芸術で主要な役を担う演者」。舞台芸術で確立した役割として定義されている。",
        "semantic_assertions": [
          {
            "id": "assertion-16",
            "statement": "一般の重要人物と舞台芸術の役割名を同一視しない",
            "polarity": "must_hold",
            "scope": "a principal in a stage production"
          }
        ]
      },
      {
        "id": "independent-17",
        "surface_form": "principal",
        "frame": "one of the orchestra's principals",
        "meaning": "オーケストラのセクションを率いる首席奏者",
        "disposition": "included",
        "rationale": "principal の「one of the orchestra's principals」は「オーケストラのセクションを率いる首席奏者」。チェロのセクションを率いる例が名詞の役割と合致する。",
        "semantic_assertions": [
          {
            "id": "assertion-17",
            "statement": "オーケストラ全体の唯一の長であることを要求しない",
            "polarity": "must_hold",
            "scope": "one of the orchestra's principals"
          }
        ]
      },
      {
        "id": "independent-18",
        "surface_form": "principal",
        "frame": "a principal in a crime",
        "meaning": "刑事法の分類における犯罪関与者",
        "disposition": "included",
        "rationale": "principal の「a principal in a crime」は「刑事法の分類における犯罪関与者」。実行者と一定の関与者を適用法に即して扱う。",
        "semantic_assertions": [
          {
            "id": "assertion-18",
            "statement": "すべての法域で直接実行者だけを指すと断定しない",
            "polarity": "must_hold",
            "scope": "a principal in a crime"
          }
        ]
      },
      {
        "id": "independent-19",
        "surface_form": "principal",
        "frame": "treat someone as a principal",
        "meaning": "関与者を適用法上 principal に分類する",
        "disposition": "included",
        "rationale": "principal の「treat someone as a principal」は「関与者を適用法上 principal に分類する」。援助者を含める制定法の例として範囲が限定される。",
        "semantic_assertions": [
          {
            "id": "assertion-19",
            "statement": "援助者が含まれるかどうかは適用される分類による",
            "polarity": "must_hold",
            "scope": "treat someone as a principal"
          }
        ]
      },
      {
        "id": "independent-20",
        "surface_form": "principal",
        "frame": "be liable as principal",
        "meaning": "義務について第一次的責任を負う当事者",
        "disposition": "included",
        "rationale": "principal の「be liable as principal」は「義務について第一次的責任を負う当事者」。債務例で名詞の義務者を示し金額義や刑事義と分離する。",
        "semantic_assertions": [
          {
            "id": "assertion-20",
            "statement": "この用例で principal は元金という金額ではない",
            "polarity": "must_hold",
            "scope": "be liable as principal"
          }
        ]
      },
      {
        "id": "independent-21",
        "surface_form": "principal",
        "frame": "the obligation of the principal",
        "meaning": "主たる義務者が負う義務",
        "disposition": "included",
        "rationale": "principal の「the obligation of the principal」は「主たる義務者が負う義務」。of の補語は義務を負う人・法人である。",
        "semantic_assertions": [
          {
            "id": "assertion-21",
            "statement": "principal はこの義務を負う側であり義務の受益者とは限らない",
            "polarity": "must_hold",
            "scope": "the obligation of the principal"
          }
        ]
      },
      {
        "id": "independent-22",
        "surface_form": "principal",
        "frame": "the principal and the surety",
        "meaning": "主たる義務者と保証する側",
        "disposition": "included",
        "rationale": "principal の「the principal and the surety」は「主たる義務者と保証する側」。対比される役割と例文の respectively の対応が一致する。",
        "semantic_assertions": [
          {
            "id": "assertion-22",
            "statement": "例文では第一次的責任が principal に、二次的責任が surety に対応する",
            "polarity": "must_hold",
            "scope": "the principal and the surety"
          }
        ]
      },
      {
        "id": "independent-23",
        "surface_form": "principal",
        "frame": "principal debtor / principal obligor",
        "meaning": "主たる債務者・義務者を修飾する形容詞",
        "disposition": "included",
        "rationale": "principal の「principal debtor / principal obligor」は「主たる債務者・義務者を修飾する形容詞」。名詞単独の役割と形容詞による修飾を明示的に区別する。",
        "semantic_assertions": [
          {
            "id": "assertion-23",
            "statement": "複合表現の debtor・obligor の意味を形容詞 principal 単独へ移さない",
            "polarity": "must_hold",
            "scope": "principal debtor / principal obligor"
          }
        ]
      },
      {
        "id": "independent-24",
        "surface_form": "principally",
        "frame": "principally + predicate",
        "meaning": "主として、主に",
        "disposition": "included",
        "rationale": "principally の「principally + predicate」は「主として、主に」。副詞派生形として語形成に含まれ、独立した principal の品詞とはされていない。",
        "semantic_assertions": [
          {
            "id": "assertion-24",
            "statement": "principally は principal そのものの副詞用法ではなく派生語である",
            "polarity": "must_hold",
            "scope": "principally + predicate"
          }
        ]
      },
      {
        "id": "independent-25",
        "surface_form": "principalship",
        "frame": "the principalship of an institution",
        "meaning": "校長・学長などの職または在職",
        "disposition": "included",
        "rationale": "principalship の「the principalship of an institution」は「校長・学長などの職または在職」。名詞派生形として列挙される範囲は適切である。",
        "semantic_assertions": [
          {
            "id": "assertion-25",
            "statement": "principalship は役職者本人を表す principal と同一の語形ではない",
            "polarity": "must_hold",
            "scope": "the principalship of an institution"
          }
        ]
      },
      {
        "id": "independent-26",
        "surface_form": "principal",
        "frame": "a principal in an organ",
        "meaning": "オルガンの主要なストップまたはそのパイプ",
        "disposition": "excluded",
        "rationale": "principal の「a principal in an organ」は「オルガンの主要なストップまたはそのパイプ」。オルガン構造の低頻度専門義は一般学習記事に必須の主要用法ではない。",
        "semantic_assertions": [
          {
            "id": "assertion-26",
            "statement": "オーケストラの首席奏者義から楽器部品義を推論しない",
            "polarity": "must_hold",
            "scope": "a principal in an organ"
          }
        ]
      },
      {
        "id": "independent-27",
        "surface_form": "principal",
        "frame": "a principal in a roof truss",
        "meaning": "屋根組の主要な垂木・支持部材",
        "disposition": "excluded",
        "rationale": "principal の「a principal in a roof truss」は「屋根組の主要な垂木・支持部材」。建築部材の低頻度専門義は本記事の主要な学習範囲外と判断する。",
        "semantic_assertions": [
          {
            "id": "assertion-27",
            "statement": "人物名詞義から建築部材義へ一般化しない",
            "polarity": "must_hold",
            "scope": "a principal in a roof truss"
          }
        ]
      },
      {
        "id": "independent-28",
        "surface_form": "principle",
        "frame": "a basic principle",
        "meaning": "原理・原則",
        "disposition": "excluded",
        "rationale": "principle の「a basic principle」は「原理・原則」。別の見出し語であり、混同注意としてのみ扱うのが適切である。",
        "semantic_assertions": [
          {
            "id": "assertion-28",
            "statement": "同音・近い綴りを理由に principal の原則義を設けない",
            "polarity": "must_hold",
            "scope": "a basic principle"
          }
        ]
      }
    ],
    "finding_results": [
      {
        "taxonomy_id": "sense_boundary_overlap",
        "location": {
          "section": "sense_structure",
          "line_start": 128,
          "line_end": 128,
          "exact_quote": "【日本語訳・定義】学校、カレッジ、その他の教育機関を管理する最高責任者。どの種類の教育機関を指すかは地域と制度によって異なる。  "
        },
        "severity": "blocking",
        "rationale": "固定済み source union の U-002 は、教育機関の長だけでなく、組織で支配的権限または主導的地位を持つ人物という名詞用法も収録対象としている。しかし語義2は教育機関の最高責任者に限定され、他の番号付き名詞語義もこの一般的な権限・主導者用法を受け入れない。コアイメージ本文の「組織や行為の中心人物」に対応する収録先も学校・オーケストラ以外にはなく、主要な名詞候補が語義構造から欠落している。",
        "evidence_link_ids": [
          "F-002",
          "F-003",
          "F-014",
          "F-017"
        ],
        "suggested_direction": "人物を指す一般的な権限・主導者用法を、教育機関の役職名と学習上区別できる番号付き語義として追加するか、語義2をその用法まで明示的に含む構造へ再編し、コアイメージ枝・フレーム・例も対応させる。",
        "id": "normal-sense-structure-001"
      },
      {
        "taxonomy_id": "sense_boundary_overlap",
        "location": {
          "section": "sense_structure",
          "line_start": 166,
          "line_end": 166,
          "exact_quote": "【日本語訳・定義】オーケストラで一つのセクションを率いる奏者。重要人物一般の呼称ではない。  "
        },
        "severity": "blocking",
        "rationale": "固定済み source union の U-003 は、オーケストラのセクション首席だけでなく、舞台芸術の principal artist や leading performer まで含む確立した名詞用法を収録対象としている。現行語義3はオーケストラに限定し、レジスター、フレーム、コアイメージ枝もその範囲だけなので、裏付けられた舞台芸術上の主要用法に収録先がない。",
        "evidence_link_ids": [
          "F-007",
          "F-018"
        ],
        "suggested_direction": "語義3を、根拠が支える舞台芸術の主役・主要演者とオーケストラの首席奏者を包含する範囲へ広げ、各下位用法のフレームと例を区別して示す。",
        "id": "normal-sense-structure-002"
      },
      {
        "taxonomy_id": "sense_boundary_overlap",
        "location": {
          "section": "sense_structure",
          "line_start": 194,
          "line_end": 194,
          "exact_quote": "【日本語訳・定義】借入・貸付・投資で利息・利益・収益と区別される元の資本額を指す。元金への支払いは債務額を減らす。  "
        },
        "severity": "blocking",
        "rationale": "固定済み source union の U-005 は、信託で income と区別される財産本体・corpus の用法を、金融上の principal に統合する収録対象としている。現行語義4は借入・貸付・投資の「金額」に限定され、信託財産は金銭以外も含み得るため、この専門用法を包含しない。コアイメージ枝、領域、フレームにも信託用法の収録先がない。",
        "evidence_link_ids": [
          "F-025"
        ],
        "suggested_direction": "語義4へ、信託の income と対比される財産本体・corpus の専門用法を明示的に統合し、見出し・コアイメージ枝・領域・フレームを金額だけに閉じない形へ広げる。学習上別フレームと判断するなら独立語義に分ける。",
        "id": "normal-sense-structure-003"
      },
      {
        "taxonomy_id": "argument_slot_role_mismatch",
        "location": {
          "section": "frames",
          "line_start": 172,
          "line_end": 172,
          "exact_quote": "【文法パターン】`one of 〈オーケストラなどの所有格〉 principals`＝その団体の首席奏者の一人  "
        },
        "severity": "blocking",
        "rationale": "当該語義はオーケストラの各セクションを率いる奏者に限定されているのに、所有格スロットの「など」と訳の「団体」が、バレエ団や企業などを含む無限定な団体名の代入を許す。すると `principal` が首席奏者ではない別の役職・身分を表す候補までこの語義の完全フレームとして生成され、定義とスロットの意味役割が一致しない。",
        "evidence_link_ids": [],
        "suggested_direction": "所有格スロットと訳をオーケストラ（必要なら定義で明示した音楽アンサンブル）に限定する。",
        "id": "normal-frame-relation-001"
      },
      {
        "taxonomy_id": "argument_slot_role_mismatch",
        "location": {
          "section": "frames",
          "line_start": 252,
          "line_end": 252,
          "exact_quote": "【文法パターン】`a principal appoints/authorizes an agent to do ...`＝本人が代理人に～する権限を与える／`act on behalf of the principal`＝本人を代理して行動する／`owe a duty to the principal`＝本人に対して義務を負う／`a principal-agent relationship`＝本人・代理人関係  "
        },
        "severity": "blocking",
        "rationale": "代理権を与える側を主語、代理人を目的語、行為を不定詞補部に置く能動フレームだけが、この語義のコロケーションと例文に実現されていない。他の三つの主要パターンには対応例があるため、主要構文とコロケーションの相互対応がこのフレームで欠けている。",
        "evidence_link_ids": [],
        "suggested_direction": "`a principal authorizes an agent to do ...` を独立したコロケーションとして、本人・代理人・許可された行為の三スロットが明示された例文で実現する。",
        "id": "normal-frame-relation-002"
      },
      {
        "taxonomy_id": "lexical_relation_mislabel",
        "location": {
          "section": "lexical_relations",
          "line_start": 237,
          "line_end": 237,
          "exact_quote": "・interest  "
        },
        "severity": "blocking",
        "rationale": "F3: `principal` と `interest` は一つの返済額に含まれ得る別々の金額構成要素であり、基礎額とそこから生じる追加額という関連はあっても、補完・程度・方向・評価・状態のいずれかの反意対立ではない。違い行も両者を構成カテゴリーとして説明している。",
        "evidence_link_ids": [],
        "suggested_direction": "語法・注意への対照表現としての移動",
        "id": "normal-frame-relation-003"
      },
      {
        "taxonomy_id": "example_sense_attribution_mismatch",
        "location": {
          "section": "collocations_examples",
          "line_start": 343,
          "line_end": 343,
          "exact_quote": "例: Under the agreement, the company remains liable as principal for the debt.  "
        },
        "severity": "blocking",
        "rationale": "段階1でsense:007, sense:005が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
        "evidence_link_ids": [],
        "suggested_direction": "判別語の追加",
        "id": "normal-example-attribution-001"
      },
      {
        "taxonomy_id": "regional_qualification",
        "location": {
          "section": "frequency_register",
          "line_start": 168,
          "line_end": 168,
          "exact_quote": "【頻度】〈6/10〉"
        },
        "severity": "minor",
        "rationale": "この語義は直後に「オーケストラ・音楽の専門語」と限定され、一般英語では遭遇場面が狭い。6/10は仕様上「中頻度（場面・分野・レジスターがやや限定）」に当たるため、オーケストラ領域内での定着度を英語全体の遭遇頻度へ一般化している。",
        "evidence_link_ids": [
          "F-007",
          "F-018",
          "U-003",
          "C-003"
        ],
        "suggested_direction": "英語全体を基準に2～3/10程度の低頻度へ下げ、専門領域内では確立した役割名であることはレジスター欄で維持する。",
        "id": "normal-qualification-001"
      },
      {
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "sense_structure",
          "line_start": 166,
          "line_end": 166,
          "exact_quote": "【日本語訳・定義】オーケストラで一つのセクションを率いる奏者。重要人物一般の呼称ではない。"
        },
        "severity": "blocking",
        "rationale": "C-002 routes the education/authority claim to definition:003 (the orchestral definition). Its F-002/F-003/F-014/F-017 sources concern general authority or educational heads and do not directly support this orchestral role. C-003 has separately relevant performer evidence, but that does not make C-002's cross-sense link valid. No link IDs are supplied; this identifies the existing C-002 article_target_ids/source_supports relationship.",
        "evidence_link_ids": [],
        "suggested_direction": "Remove definition:003 from C-002's targets; retain the directly applicable C-003/F-018 support for the orchestral definition.",
        "id": "normal-evidence-001"
      },
      {
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 49,
          "line_end": 49,
          "exact_quote": "【文法パターン】`the principal 〈名詞〉`＝主要な～／`a principal 〈名詞〉`＝主な～の一つ／`one of the principal 〈複数名詞〉`＝主要な～の一つ／`the principal cause of ...`＝～の主因／`a principal source of ...`＝～の主要源の一つ／`the principal reason for ...`＝～の主な理由"
        },
        "severity": "blocking",
        "rationale": "C-001 targets this grammar_pattern, but F-001 (Merriam-Webster adjective sense 1), F-013 (Cambridge learner definition), F-016 (Collins American adjective definition) establish adjective meaning and a few noun combinations. They do not document the complete article/number/preposition frames or the proposed a-principal versus the-principal interpretation. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
        "evidence_link_ids": [],
        "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
        "id": "normal-evidence-002"
      },
      {
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 134,
          "line_end": 134,
          "exact_quote": "【文法パターン】`the principal of 〈限定詞を含む学校・教育機関の名詞句〉`＝～の校長・学長／`a school principal`＝学校の校長／`a college principal`＝カレッジの学長"
        },
        "severity": "blocking",
        "rationale": "C-002 targets this grammar_pattern, but F-002/F-003 (Merriam-Webster noun senses 1/1b), F-014 (Cambridge school-person definition), and F-017 (Collins title definition) establish school/college leadership meanings and one regional qualification. Their supplied passages do not establish the complete principal of determiner-containing NP, a school principal, and a college principal frames. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
        "evidence_link_ids": [],
        "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
        "id": "normal-evidence-003"
      },
      {
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 172,
          "line_end": 172,
          "exact_quote": "【文法パターン】`one of 〈オーケストラなどの所有格〉 principals`＝その団体の首席奏者の一人"
        },
        "severity": "blocking",
        "rationale": "C-003 targets this grammar_pattern, but F-007 (Merriam-Webster noun sense 1f) and F-018 (Collins performer/first-player uses) establish the performer meaning. Neither supplied passage documents one of + orchestra possessive + plural principals or the proposed possessive-slot generalization. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
        "evidence_link_ids": [],
        "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
        "id": "normal-evidence-004"
      },
      {
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 200,
          "line_end": 200,
          "exact_quote": "【文法パターン】`principal and interest`＝元金と利息／`pay down the principal`＝元金を減らす／`repay principal`＝元金を返済する／`protect the principal`＝元本を保全する"
        },
        "severity": "blocking",
        "rationale": "C-004 targets this grammar_pattern, but F-008/F-015/F-019/F-024/F-027 establish financial principal and, for F-024, repayment reducing the obligation. They do not document the complete pay down the principal, repay principal, or protect the principal frames, including their article choices. Semantic compatibility alone does not verify these as evidenced complete frames. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
        "evidence_link_ids": [],
        "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
        "id": "normal-evidence-005"
      },
      {
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 252,
          "line_end": 252,
          "exact_quote": "【文法パターン】`a principal appoints/authorizes an agent to do ...`＝本人が代理人に～する権限を与える／`act on behalf of the principal`＝本人を代理して行動する／`owe a duty to the principal`＝本人に対して義務を負う／`a principal-agent relationship`＝本人・代理人関係"
        },
        "severity": "blocking",
        "rationale": "C-006 targets this grammar_pattern, but F-004/F-020/F-023 establish authority, behalf, control, and unspecified agent duties. The supplied passages do not establish the full appoints/authorizes an agent to do frame or the complete owe a duty to the principal construction. Wex's mention of duties is not a recorded syntax example. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
        "evidence_link_ids": [],
        "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
        "id": "normal-evidence-006"
      },
      {
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 299,
          "line_end": 299,
          "exact_quote": "【文法パターン】`a principal in a crime`＝犯罪について `principal` とされる関与者／`treat someone as a principal`＝人を `principal` として扱う／`a principal in the first/second degree`＝歴史的分類上の第一級・第二級 `principal`"
        },
        "severity": "blocking",
        "rationale": "C-007 targets this grammar_pattern, but F-005 (Merriam-Webster noun sense 1d/legal definition) and F-021 (Collins criminal-law sense) support criminal participation and the accessory contrast. Neither fact statement nor source_detail records first/second degree, historical common-law scope, or the supplied complete frames. C-007's support_summary asserts historical degree classifications beyond the underlying F-005 passage summary. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
        "evidence_link_ids": [],
        "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
        "id": "normal-evidence-007"
      },
      {
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "frames",
          "line_start": 337,
          "line_end": 337,
          "exact_quote": "【文法パターン】`be liable as principal`＝主たる当事者として責任を負う／`the obligation of the principal`＝主たる義務者の義務／`the principal and the surety`＝主たる義務者と保証人"
        },
        "severity": "blocking",
        "rationale": "C-008 targets this grammar_pattern, but F-006/F-022/F-026 establish primary liability and the surety/guarantor contrast. They do not document the zero-article be liable as principal frame or the other complete obligation/surety phrases. Their definition-level support does not establish those grammatical constructions. No independent evidence-link IDs are supplied in this normalized packet; the existing source_supports relationship is identified here by claim/fact IDs.",
        "evidence_link_ids": [],
        "suggested_direction": "Hold the unsupported complete-frame claims, or restrict them to what the fixed evidence directly supports. Have the source-first owner provide directly applicable construction evidence before restoring the full frames.",
        "id": "normal-evidence-008"
      },
      {
        "id": "COLD-001",
        "location": "コアイメージ（名詞用法の総括）と語義3（適用範囲の限定）",
        "severity": "medium",
        "description": "コアイメージの「組織や行為の中心人物」という表現は、名詞の principal を重要人物一般に使えるかのように読めるが、列挙された具体的語義は教育機関の長、首席奏者、法律上の当事者など役割ごとに限定され、語義3では重要人物一般ではないと明記している。この範囲差により、学習者が任意の組織の中心人物を a principal と呼べると誤って一般化するおそれがある。",
        "reason": "コアイメージは「形容詞では主要なものを選び出し、名詞では組織や行為の中心人物、利息に対する元の金額、代理関係などの主要当事者を指す。」と名詞の人物用法を広く総括している。しかし本文の人物語義は役職・法的関係ごとに限定され、語義3はさらに「重要人物一般の呼称ではない。」と反例を明示しているため、総括だけを読んだ学習者には適用範囲が実際の説明より広く見える。",
        "suggested_direction": "コアイメージを「教育機関の長やオーケストラの首席奏者など、特定の制度・役割で中心となる人物」のように、本文で立てた語義へ対応する表現に狭める。重要人物一般を表す独立した名詞語義も扱う意図がある場合は、適用できる文脈と用例を明示した別語義として検証のうえ追加し、コアイメージだけで暗示しない。",
        "scope_anchors": [
          {
            "id": "COLD-001-A1",
            "exact_quote": "形容詞では主要なものを選び出し、名詞では組織や行為の中心人物、利息に対する元の金額、代理関係などの主要当事者を指す。",
            "location_hint": "＃コアイメージの第1段落、第2文"
          },
          {
            "id": "COLD-001-A2",
            "exact_quote": "オーケストラで一つのセクションを率いる奏者。重要人物一般の呼称ではない。",
            "location_hint": "語義3【日本語訳・定義】"
          }
        ]
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
        "id": "collocation:013",
        "status": null,
        "notes": "",
        "target_id": "collocation:013"
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
        "id": "collocation:016",
        "status": null,
        "notes": "",
        "target_id": "collocation:016"
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
        "id": "grammar_pattern:007",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:007"
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
        "id": "grammar_pattern:008",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:008"
      },
      {
        "id": "collocation:019",
        "status": null,
        "notes": "",
        "target_id": "collocation:019"
      },
      {
        "id": "collocation:020",
        "status": null,
        "notes": "",
        "target_id": "collocation:020"
      },
      {
        "id": "collocation:021",
        "status": null,
        "notes": "",
        "target_id": "collocation:021"
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
        "id": "risk_sense_pair:004",
        "status": null,
        "notes": "",
        "relation_id": "risk_sense_pair:004"
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
        "id": "example_translation:020",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:020"
      },
      {
        "id": "example_translation:021",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:021"
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
        "id": "pattern_example_coverage:007",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:007"
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
        "id": "pattern_example_coverage:008",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:008"
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
        "id": "independent-1",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-1"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-1",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-2",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-2"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-3",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-3"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-3",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-4",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-4"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-4",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-5",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-5"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-5",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-6",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-6"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-6",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-7",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-7"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-7",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-8",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-8"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-8",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-9",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-9"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-9",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-10",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-10"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-10",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-11",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-11"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-11",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-12",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-12"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-12",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-13",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-13"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-13",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-14",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-14"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-14",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-15",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-15"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-15",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-16",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-16"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-16",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-17",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-17"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-17",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-18",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-18"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-18",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-19",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-19"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-19",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-20",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-20"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-20",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-21",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-21"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-21",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-22",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-22"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-22",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-23",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-23"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-23",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-24",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-24"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-24",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-25",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-25"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-25",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-26",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-26"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-26",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-27",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-27"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-27",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-28",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-28"
        ],
        "verified_body_sha256": "123827dd106005ebf2c17c3d35574b46f945a65f12b8eb144998b0b911e86de9",
        "assertion_results": [
          {
            "id": "assertion-28",
            "status": null,
            "notes": ""
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "normal-sense-structure-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-sense-structure-002",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-sense-structure-003",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-frame-relation-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-frame-relation-002",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-frame-relation-003",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-example-attribution-001",
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
      },
      {
        "id": "normal-evidence-007",
        "status": null,
        "notes": ""
      },
      {
        "id": "normal-evidence-008",
        "status": null,
        "notes": ""
      },
      {
        "id": "COLD-001",
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
    "pass_findings.json": "7eddf77f95c5e8f0d6c1c7ed162d9e391188f92e5f650051caf6c596b4062405",
    "cold_review.json": "4c203585c7f6ce2cbe1167f94df71541cdb20eabc25b8d1de6252f1413f6124f",
    "final_blind.json": "4399f0a1afc2f6cac2c7961d36136c108e5ae7e771d5b274566bf645be561b33",
    "blind_seal.json": "c1e53b2442e0dd34362d48882c7b13ad664dc2e7582fdb5c61b37794976f6150",
    "pre_blind_resolution.json": "62550a294aa5077cb81cc24497aef445765b39188ee1d3d0a33003e3018c28ac",
    "pre_blind_revision.json": "b9897b96c2d623b08c1c6eddf20e093f4f1592cd22a911129f5bb41ba9ee8f19",
    "checker_recheck_manifest.json": "13c0daf50b6e128eade7f500a7fd53210ceb6cebd4f05773da7735f0aee19917",
    "post_blind_resolution.json": "9caa4cb41b8144ba6c7b1107941eb70a3ee5f5ee8a95c5f8ab74d76de499db3f",
    "post_blind_verification.json": "3fdeb10344479f3e3e8ef0b650ade38c1d970932c46786998427741e17cf28ad",
    "targeted_adjudications.json": "af5af9b139e61078d584a712c70a3ce285f0407cc7fa63836b8195db9ea9f3b6",
    "source_inventory.json": "71e14e961e1592b84b5a651295f424b42fb44231a82f17cb7d10a27350b8fef4",
    "resolutions.json": "10f89b818fcf481019c022a991f46d52d18091ef6ff782e44070bffae16c5c6f",
    "check_passes/checker_passes.stage1.json": "db2a737a5421fdae1e07fc07ae276c50b41bd0e7594ec13bd4d348a8dda9e84e",
    "check_passes/evidence.json": "e41117e93b56dc8cb4a70529ea4ea14283423ba429370cbda85afd3b8dffc4f0",
    "check_passes/evidence.request.json": "8279266e856c1603ebb4cad0704e4f7c75a1dc47145c2b2029c1ea2cb5c973f1",
    "check_passes/example-attribution.alignment-key.json": "f694d7845f5ecea281408a8f2024acce00dab17f4db849393c272faed7b5dcd8",
    "check_passes/example-attribution.blind-record.json": "737bcf91bcb2962c9ddff53b1b622e03d5e053a3f8b7a22739da3938581cfcd4",
    "check_passes/example-attribution.json": "d29c276312131fe7d4ccffb206de167b9893c414d47ec81985d36082de160837",
    "check_passes/example-attribution.request.json": "fe4d97d365b43fc4f704ed663a43f91411aa3d056e9b160c4d6fb16a09e445b5",
    "check_passes/frame-relation.antonym-axis.adjudication-record.json": "6ab89833f3c6b7f9d16331c6335e018227624af406e1963befa3cccec87059c4",
    "check_passes/frame-relation.antonym-axis.alignment-key.json": "1d888f0eec67d45c3be51561f6d9af9da5f88b02f868c0cd744ce898f3ca496e",
    "check_passes/frame-relation.antonym-axis.blind-record.json": "fe1a5a069c14a3477b8bbb6b80987e848c5348fd6a19735d322bedcfb82fe514",
    "check_passes/frame-relation.antonym-axis.stage2.request.json": "50770a916065ab6f698689123d409a46fd13973528ba57d37ae4f77ac67ac6b3",
    "check_passes/frame-relation.request.json": "ab6a25304aad09c4b5b45789c4b7c8607ea700a2af1bb0e422ddc63f713d6dc3",
    "check_passes/input_snapshot.json": "af2d8150b0a34823e574af4b760d7351ef9a3df28d5803591739752b27254048",
    "check_passes/pronunciation.json": "42f5c2b77aa4d0507f429bced234d7b3e2a170058bfe07630ef0d1a66b0b31f2",
    "check_passes/pronunciation.request.json": "bde7456b65ea41982bc5a10025c64175cf70862311e7a7d0085e9266af18c502",
    "check_passes/qualification.json": "63031c6459a7c761b17199030780b4d087ef32297d83a66ddb0cd3071e5b0cce",
    "check_passes/qualification.request.json": "0e027d735da2ca17285eef259c238a8ba9745bdf05027ad83e9c098d5cd2b79f",
    "check_passes/sense-structure.json": "ba6533dcc91adf5958362cee98e6b5d0bc9d5d49e9f58464e8561a722c99274b",
    "check_passes/sense-structure.request.json": "0812e29a39160ee8a8f55e60a193196505053c0e18cc028cf78de2f286a2bba0",
    "check_passes/translation.json": "e8d85f07636e00d385c13ef71cd5698962b92d63ea14a117d9c60164ece1882e",
    "check_passes/translation.request.json": "9e753a989eacbf3bd4381644880fd43fb4dd76cdf2619b65f9d6c1fe720f3dea"
  },
  "contract_version": "review_preflight_v1"
}
```
