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
  "entry_body": "\n＃発音記号\n\n基本: /pʌbˈlɪsəti/。米語では /pəˈblɪsəti/ も使われる。いずれも4音節で、第2音節に主強勢がある。/pʌbˈlɪsəti/ では第1音節が /pʌb/、第2音節が /ˈlɪs/ となる。/pəˈblɪsəti/ では第1音節が弱い /pə/ となり、/b/ は第2音節頭の /bl/ と発音される。これは米英の絶対的な地域差というより、辞書や話者による発音差として覚えるとよい。語末は /əti/ で、綴りの -ity を /aɪti/ と読まない。  \n\n＃語源\n\nフランス語 publicité を経て、ラテン語 publicus「公の、人民の」にさかのぼる。英語ではもともと「公にされている状態・公開性」を表し、そこから「世間に知られるようにすること」や、現代の「宣伝・広報活動」へ意味が発展した。  \n\n＃語形成\n\n・publicist：publicity を作り、扱い、広める仕事をする人。映画、作家、芸能人、企業などの広報担当者を指す。  \n・publicity campaign：商品、作品、行事、主張などに注目を集めるための宣伝・広報キャンペーン。  \n・publicity material：宣伝・広報用の資料。  \n・publicity stunt：世間の注目を集めるために意図して行う行為・仕掛け。話題作りの含みを持つ。  \n\n＃意味・用法・関連表現\n\n1. 【名詞・不可算】公衆の注目、報道上の露出\n\n【日本語訳・定義】人・企業・作品・出来事などが、新聞、テレビなどのメディアを通じて世間から受ける注目や報道上の露出。好意的とは限らず、good/bad/negative/unwanted publicity のように評価を添えられる。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準的な一般語。複数の一般辞書で主要な名詞として扱われる。  \n\n【文法パターン】gain/receive publicity＝世間の注目・報道を得る／widespread publicity＝広範な世間の注目・報道／good/bad/negative/unwanted publicity＝好意的な・悪い・否定的な・望まない注目／shun publicity＝世間の注目・報道を避ける  \n\n【コロケーション】\n\n・gain/receive publicity  \n用途: 人・団体・作品・出来事が世間の注目や報道を受けることを表す。  \n例: The charity gained widespread publicity after the athlete supported its campaign.  \n訳: その慈善団体は、その選手がキャンペーンを支持した後、広く世間の注目を浴びた。  \n\n・widespread publicity  \n用途: 広い地域や多くの媒体に及ぶ世間の注目・報道を表す。  \n例: The discovery received widespread publicity in the national press.  \n訳: その発見は全国紙で広く報道された。  \n\n・good/bad publicity  \n用途: 注目が対象に好影響または悪影響を与えることを評価する。  \n例: The scandal gave the company bad publicity.  \n訳: その不祥事は会社に否定的な世間の注目をもたらした。  \n\n・negative publicity  \n用途: 批判、不祥事、悪い報道などによる否定的な世間の注目を表す。  \n例: The restaurant responded quickly to the negative publicity surrounding the safety complaint.  \n訳: そのレストランは、安全性に関する苦情をめぐる否定的な報道にすぐ対応した。  \n\n・shun publicity  \n用途: 世間の注目や報道を意図的に避けることを表す。  \n例: The novelist shuns publicity and rarely gives interviews.  \n訳: その小説家は世間の注目を避け、めったにインタビューに応じない。  \n\n【語法・注意】現代の一般用法ではこの語義の publicity は通常不可算で、a publicity や publicities は一般に避け、a lot of publicity、the publicity surrounding the case のように使う。publicity は注目・報道を表し、好評や長期的な名声を必ず含むわけではない。good/bad/negative/unwanted publicity のように評価を添えられる。  \n\npublicity about 〈話題〉は話題に関する注目・報道、publicity for 〈対象〉は対象を知らせる活動または対象が受ける注目を指し得る。結果として受けた注目を明確にするなら gain/receive publicity for のように動詞で示す。古風・形式的には「公開性、公然性」の意味で使われることもある。  \n\n【類義語】\n\n・attention  \n定義: 人や話題に関心が向けられていること。  \n頻度: 〈10/10〉  \n違い: publicity は特に新聞・テレビなどを通じた公的な注目・露出に焦点があり、attention より媒体や公衆に寄る。  \n例: The announcement attracted attention from local residents.  \n訳: その発表は地元住民の注目を集めた。  \n\n・exposure  \n定義: 人・商品・活動などが公衆や媒体に知られること。  \n頻度: 〈8/10〉  \n違い: publicity は露出の機会一般より、世間の注目・報道を受けること、またはそれを集める活動を表す。  \n例: The interview gave the small business valuable exposure.  \n訳: そのインタビューは、その小企業に貴重な公的露出をもたらした。  \n\n・coverage  \n定義: 新聞、テレビ、ウェブなどによる報道。  \n頻度: 〈9/10〉  \n違い: coverage はメディアによる報道内容を指し、publicity は報道による注目や、注目を集める活動まで含む。  \n例: The issue received extensive media coverage.  \n訳: その問題はメディアで大きく報道された。  \n\n・fame  \n定義: 多くの人に知られている状態。  \n頻度: 〈10/10〉  \n違い: fame は知名度という状態を指すのに対し、publicity は一時的な注目・報道も表し、negative publicity のように評価中立である。  \n例: The actor achieved international fame after the film won several awards.  \n訳: その俳優は、その映画がいくつも賞を取った後、国際的な名声を得た。  \n\n2. 【名詞・不可算】宣伝活動、広報\n\n【日本語訳・定義】人、商品、作品、行事、主張などに世間の関心を集めるために行う広報・宣伝活動。広告に限らず、情報提供などの広報手段を含み得る。ここでは世間の注目を集める側の活動・手段に焦点を置く。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準的な一般語。複数の一般辞書で活動・情報に関わる名詞用法として扱われる。  \n\n【文法パターン】publicity for/about 〈映画・商品・行事〉＝～に関する広報・注目／advance publicity for 〈発売・行事〉＝発売・行事の事前広報／publicity campaign/material/stunt＝宣伝キャンペーン・資料・仕掛け  \n\n【コロケーション】\n\n・a publicity campaign  \n用途: 商品、作品、行事、主張などへの注目を集める計画的な宣伝活動を表す。  \n例: The museum launched a publicity campaign for its new exhibition.  \n訳: その博物館は新しい展覧会の広報キャンペーンを始めた。  \n\n・publicity material  \n用途: メディアや一般の人に提供する広報・宣伝用の資料を表す。  \n例: The press office prepared publicity material for the product launch.  \n訳: 広報室は製品発売のための宣伝資料を用意した。  \n\n・advance publicity for 〈発売・行事〉  \n用途: 映画、書籍、製品、行事などの開始前に行う事前広報を表す。  \n例: The organizers arranged advance publicity for the festival several months before it opened.  \n訳: 主催者は祭りの開幕数か月前から事前広報を手配した。  \n\n・a publicity stunt  \n用途: メディアや世間の注目を集めるために意図して行う行為・仕掛けを表す。  \n例: The company staged a publicity stunt by projecting its logo onto the river bridge.  \n訳: その会社は川に架かる橋へロゴを投影する話題作りの仕掛けを行った。  \n\n【語法・注意】この語義でも publicity は通常不可算で、a publicity campaign、a publicity stunt のように、数えられるのは campaign や stunt などの具体的な活動である。the publicity for the film は映画の宣伝・広報活動を指し得るが、文脈によっては映画が受ける注目・報道も指す。  \n\nadvertising は通常、料金を払って掲載・放送する広告やその活動に焦点がある。一般的な区別では publicity と paid advertising を分けるが、辞書や文脈によっては publicity が有料広告・宣伝まで指すこともある。  \n\npublicity stunt は、世間の注目を集める意図を前面に出す行為・仕掛けを指す。publicity for 〈対象〉は活動と受けた注目の両方に読めるため、結果としての注目を明確にするなら gain/receive publicity for のように動詞で示す。  \n\n【類義語】\n\n・advertising  \n定義: 商品、サービス、組織などを広告によって公衆に知らせる活動。  \n頻度: 〈10/10〉  \n違い: advertising は有料の広告メッセージや広告業務に焦点がある。publicity は通常、情報・活動によって公衆の注目を集める語だが、辞書や文脈によって paid advertising を含むこともある。  \n例: The company increased its advertising budget before the holiday season.  \n訳: その会社は休暇シーズンの前に広告予算を増やした。  \n\n・promotion  \n定義: 商品、サービス、作品、考えなどの販売・普及・認知を高める活動。  \n頻度: 〈9/10〉  \n違い: promotion は販売・普及も含む広い活動語で、publicity は公衆の注目を集める情報・活動に焦点がある。  \n例: The festival used social media promotion to sell more tickets.  \n訳: その祭りは、より多くのチケットを売るためにSNSで販促を行った。  \n\n・public relations  \n定義: 企業・組織・人物と公衆との関係を管理する活動。  \n頻度: 〈9/10〉  \n違い: public relations は公衆との関係全体を扱う広い活動で、publicity は注目を集める広報活動やその結果を指しやすい。  \n例: The company hired a public relations firm after the data breach.  \n訳: その会社はデータ漏えいの後、広報会社を雇った。  \n\n・marketing  \n定義: 市場調査、商品設計、価格設定、流通、宣伝などを通じて需要と販売を形成する活動。  \n頻度: 〈10/10〉  \n違い: marketing は市場活動全体を扱う広い語で、publicity と重なる場合もある。ただし publicity は人・作品・行事・主張にも用いられる、注目を集める情報発信や活動を指す。  \n例: The marketing team tested the new packaging with several customer groups.  \n訳: マーケティングチームは複数の顧客グループで新しい包装を試した。  ",
  "_output_metadata": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-publicity-20260902T194039Z-23d464b6",
    "context_id": "blind-publicity-context-20260902T194039Z-23d464b6",
    "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
    "prompt_sha256": "1bb7b1a1c7f589a50a704d1ce6c1ecd0bfb1c9fb689fd481d21bf608438eb7b5",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false
  }
}
```
