# Independent cold-review handoff

Run concurrently with the seven checker subagents when a slot is available. The input contains only the fixed entry body and cold-review prompt; checker findings, source-first artifacts, and generation context are prohibited.

Save one JSON response as `cold_review.response.json`.

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
  "entry_body": "\n＃発音記号\n\n発音: イギリス英語 /ˈpɑːləmənt/、アメリカ英語 /ˈpɑːrləmənt/。綴りの `lia` を一音ずつ読まず、通常は3音節で発音する。イギリス英語では母音の後の `r` を発音せず、アメリカ英語では発音する。  \n\n＃語源\n\n中英語 *parlement* を経て、古フランス語 *parlement*「話し合い、会議」にさかのぼり、その基になった *parler* は「話す」を意味する。もともとの「話し合う場」から、公的事項を審議する会議、さらに立法を担う代表者の機関という意味へ発達した。現在の綴りにある `ia` は、中世ラテン語 *parliamentum* に合わせた形の影響を受けている。  \n同語源語には `parley`「交渉、会談」があり、派生語には `parliamentary`「議会の」がある。  \n\n＃語形成\n\n・parliamentary：`parliament` に接尾辞 `-ary` が付いた形容詞。「議会の」「議会制の」のほか、`parliamentary procedure` では「議事手続きの」を表す。  \n\n＃コアイメージ\n\n`parliament` の中心は、「代表者が集まり、公的事項を審議して決定する制度的な会議体」である。そこから、その継続的な立法機関そのものと、一度の選挙によって構成され次の選挙まで活動する特定期の会議体を表す。  \n・制度として存在し、法律や政策を審議する代表者の機関 → 「議会、国会」（語義1）  \n・ある選挙後に成立し、次の選挙まで存続する具体的な構成・期間 → 「一議会期、特定期の議会」（語義2）  \n\n＃意味・用法・関連表現\n\n1. 【名詞・可算／固有名詞的用法】議会、国会；議会を構成する議員たち\n\n【日本語訳・定義】国または地域の代表者が集まり、法律の制定・改正、政策や予算の審議、政府の監督などを行う制度的な機関、またはその構成員全体を指す。国によって正式名称・構成・権限が異なるため、日本語訳は文脈に応じて「議会」「国会」などとなる。特定国の正式または慣用的な機関名として用いる場合は `Parliament` と大文字で始めることがある。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】標準。政治、法律、報道で高頻度。特にイギリスや議会制を採る国・地域について用いられ、アメリカ合衆国の連邦議会の通常の固有名は `Congress` である。  \n\n【文法パターン】普通名詞では `a/the + parliament`、`the parliament of 〈国・地域〉` の形を取る。イギリスの国会などを固有の制度として指す `Parliament` は、`in Parliament`、`before Parliament`、`elect someone to Parliament` のように無冠詞で使われることがある。一方、名称を前から限定する `the UK Parliament` や、普通名詞として国を特定する `the French parliament` では定冠詞を用いる。集合名詞としての動詞の単複は、地域差と、機関を一体として見るか構成員を意識するかによって変わり得る。  \n\n【コロケーション】\n\n・`a member of parliament`  \n用途: ある国・地域の議会の議員を一般的に指す。イギリスの正式な役職表現では `Member of Parliament` と大文字で書き、略して `MP` とする。  \n例: She was elected as a member of parliament for the first time last year.  \n訳: 彼女は昨年、初めて国会議員に選出された。  \n\n・`be elected to Parliament`  \n用途: 議員として国会に選出されることを表す。ここでの `to` は所属先・到達先を示し、`elect Parliament` とはしない。  \n例: He was elected to Parliament at the age of thirty-two.  \n訳: 彼は32歳で国会議員に選出された。  \n\n・`a bill before Parliament`  \n用途: 法案が国会に提出され、審議対象となっていることを表す。  \n例: The bill currently before Parliament would strengthen consumer protections.  \n訳: 現在国会で審議中のその法案は、消費者保護を強化するものだ。  \n\n・`Parliament passes 〈a bill/an Act〉`  \n用途: 国会が法案を可決する、または法律を成立させることを表す。法案が法律になるための具体的手続きは国・制度によって異なる。  \n例: Parliament passed the bill after months of debate.  \n訳: 国会は数か月にわたる審議の末、その法案を可決した。  \n\n・`an Act of Parliament`  \n用途: イギリスなどの文脈で、議会の立法手続きを経て成立した制定法を指す。  \n例: The requirement was introduced by an Act of Parliament.  \n訳: その要件は議会制定法によって導入された。  \n\n・`a hung parliament`  \n用途: 選挙後、単独で過半数を持つ政党がない議会を指す。主にイギリス英語および議会制の政治報道で用いる。  \n例: The election resulted in a hung parliament, so the parties began coalition talks.  \n訳: 選挙の結果、どの政党も単独過半数を持たない議会となり、各党は連立協議を始めた。  \n\n・`dissolve Parliament`  \n用途: 選挙などに先立ち、制度上の手続きによって特定期の議会を正式に終了させることを表す。  \n例: The prime minister asked the head of state to dissolve Parliament and call an election.  \n訳: 首相は国家元首に国会を解散して選挙を実施するよう求めた。  \n\n・`a seat in Parliament`  \n用途: 国会での議席、または議員としての地位を表す。  \n例: The party won twelve additional seats in Parliament.  \n訳: その政党は国会でさらに12議席を獲得した。  \n\n【語法・注意】`parliament` は第一に立法・審議を行う機関またはその議員集団を指し、`government`「政府・政権」と同じではない。議院内閣制では両者の構成員が重なることがあるが、制度上の役割は区別される。また、建物を明示するなら `parliament building`、イギリスのウェストミンスター宮殿なら `the Houses of Parliament` とするのが明確であり、`parliament` 自体を常に「国会議事堂」と訳してはならない。国名によって正式名称が異なり、日本の国会は通常 `the Diet` または `the National Diet`、アメリカ合衆国の連邦議会は `Congress` と呼ぶ。  \n\n【類義語】\n\n・legislature  \n定義: 法律を制定する権限を持つ機関。  \n頻度: 〈7/10〉  \n違い: `legislature` は制度名にかかわらず立法機関を機能面から指す一般語である。`parliament` は特定の政治制度・正式名称と結びつき、審議機関やその議員集団としての側面も表しやすい。  \n例: The state legislature approved the revised budget.  \n訳: 州議会は修正予算を承認した。  \n\n・congress  \n定義: 代表者が集まる会議または立法機関。特に大文字の `Congress` はアメリカ合衆国の連邦議会を指す。  \n頻度: 〈7/10〉  \n違い: `parliament` と近い立法機関名だが、どちらを使うかは各国・機関の正式名称と制度上の慣用で決まる。任意に置き換えられる一般的な同義語ではない。  \n例: Congress approved the spending package late Friday.  \n訳: 連邦議会は金曜遅く、その歳出法案一式を承認した。  \n\n・assembly  \n定義: 特定の目的のために集まる人々、または名称に `Assembly` を持つ審議・立法機関。  \n頻度: 〈7/10〉  \n違い: `assembly` は会合一般や地方・国際機関の名称にも使える広い語で、立法権を必ず含まない。`parliament` は政治的な代表制議会を中心に指す。  \n例: The regional assembly debated the transport plan.  \n訳: 地域議会はその交通計画を審議した。  \n\n・diet  \n定義: 日本など一部の国の立法機関を指す伝統的な英語名称。  \n頻度: 〈3/10〉  \n違い: この意味の `diet` は特定国の機関名に限られる。一般名詞として各国の議会を指す `parliament` より適用範囲が狭く、日本では `the National Diet` が正式な英語名称として使われる。  \n例: The bill was submitted to the National Diet.  \n訳: その法案は国会に提出された。  \n\n2. 【名詞・可算】一議会期、ある選挙で成立した特定期の議会\n\n【日本語訳・定義】一度の総選挙後に成立した議会が、次の選挙や解散まで同じ制度上の単位として存続する期間、またはその期間に活動する特定の議員構成を指す。個々の会議や一日ごとの開会ではなく、複数の `session` を含み得る、より大きな単位である。  \n\n【頻度】〈5/10〉  \n\n【レジスター/領域】政治・行政の形式的用法。特にイギリスおよび関連する議会制度の説明・報道で用いる。  \n\n【文法パターン】可算名詞として `the current/present/next parliament`、`the first/second year of a parliament` の形を取る。イギリスの特定の議会期を制度名として扱うときは `the current Parliament`、`the next Parliament` のように大文字で書かれることもある。  \n\n【コロケーション】\n\n・`the current parliament`  \n用途: 現在の選挙で構成され、活動中の議会期または議員構成を指す。  \n例: The proposal is unlikely to pass during the current parliament.  \n訳: その提案が今議会期中に可決される可能性は低い。  \n\n・`the next parliament`  \n用途: 次の選挙後に成立する議会期または議員構成を指す。  \n例: The committee recommended that the issue be reconsidered in the next parliament.  \n訳: 委員会は、その問題を次の議会期に再検討するよう勧告した。  \n\n・`the lifetime of a parliament`  \n用途: ある議会が成立してから解散・終了するまでの存続期間を指す。  \n例: Major constitutional reform may take the lifetime of a parliament to complete.  \n訳: 大規模な憲法改革は、一議会期を通じてようやく完了することもある。  \n\n・`during this parliament`  \n用途: 現在の議会期・議員構成が存続している間に、という期間を表す。  \n例: The government promised to introduce the measure during this parliament.  \n訳: 政府は今議会期中にその措置を導入すると約束した。  \n\n【語法・注意】語義1の制度としての `parliament` は選挙を越えて継続し得るが、この語義は選挙ごとに成立する具体的な構成・期間を数える。`parliament` と `session` も同じではない。イギリスでは一つの `Parliament` が通常、複数の約1年単位の `session` に分かれ、`prorogation` は一つの会期を終えるのに対し、`dissolution` はその議会期自体を終える。  \n\n【類義語】\n\n・legislative term  \n定義: 選挙された立法機関または議員が職務を行う一定の期間。  \n頻度: 〈4/10〉  \n違い: `legislative term` は制度を問わず期間を説明する一般的な句である。`parliament` のこの語義は、特定の議会制度における選挙から次の選挙・解散までの会議体と期間を一語で表せる。  \n例: Several tax reforms were enacted during the legislative term.  \n訳: その議会任期中に複数の税制改革が制定された。  ",
  "_output_metadata": {
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-parliament-20260908T084338Z-d549b547",
    "context_id": "cold-parliament-context-20260908T084338Z-d549b547",
    "input_body_sha256": "a79a267d48a57dc1c95b4c79fa1496950e4ca751f098fd6d46c4a89b6afdfcd2",
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
