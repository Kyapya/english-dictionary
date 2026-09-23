# Independent review handoff

Stage: `final_blind`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session. For runs using self_attested_handoff_v1, the raw response must include a top-level reviewer object with mode=handoff, the actual agent_id, and the actual declared_model. The ingester will reject identity supplied only after the response was created.

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

出力契約: candidateの `rationale` には、そのcandidateの `surface_form`、`frame`、`meaning` のいずれか1つを全文そのまま含め、固有の理由を述べる。findingには本文から抜き出した `scope_anchors`（各要素に `id`、`exact_quote`、`location_hint`）を付け、`rationale` に少なくとも1つの `exact_quote` 全文と、その引用に即した理由を含める。


## Input packet

```json
{
  "stage": "final_blind",
  "entry_body": "\n＃発音記号\n\n米: Oxford の米語IPAは /səˈspɪʃn/。Merriam-Webster は sus·pi·cion と3音節に区切り、第2音節に主強勢を示す。両辞書で表記形式が異なる。  \n\n＃語源\n\nsuspicion は中英語を経て、アングロフランス語・古フランス語からラテン語系の形へさかのぼる。辞書によってラテン語形は suspicio、suspectio、suspectio(n-) と記され、中継経路の説明にも差がある。Merriam-Webster は suspicere「疑う」に由来すると説明している。  \n\n＃語形成\n\n・suspicious：形容詞。「疑っている、不信に思っている」、または人に疑いを起こさせる「疑わしい」。  \n・suspiciously：副詞形。  \n・suspiciousness：名詞形。  \n・suspicion（動詞）は他動詞で「～を疑う」。Merriam-Webster では chiefly dialectal とされるため、以下の主要な学習語義には採録しない。  \n\n＃コアイメージ\n\n学習上は「確証のない段階で、ある事柄が真実かもしれないと考える」という見立てを中心にする。人の犯罪・不正を疑う用法はその具体例であり、suspicion that ... の節には別の出来事や状態も続く。人や物事を信用できず疑いの目で見る用法は、対象への不信・警戒という態度に焦点を置く。a suspicion of a smile / truth は「ごく少量・かすかな兆し」を表す形式的な比喩用法。この整理は学習上の目安で、全用法が一つの語源的意味を共有するという主張ではない。  \n\n＃意味・用法・関連表現\n\nこの節の各語義・類義語の頻度スコアは、英語全体での遭遇頻度を entry_spec_v5 の10段階基準に照らした編集上の定性的推定である。厳密なコーパス集計値や辞書掲載の数値ではなく、地域・専門・古風な用法を過大評価しない目安として付けている。類義語のスコアは、各項目の「定義」に示す意味に限る。  \n\n1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い\n\n【日本語訳・定義】確証がない段階で、ある事柄が真実かもしれないと考えることを表す。人が犯罪・不正をした可能性への疑いもこの意味に含む。Oxfordは犯罪・不正の疑いでは可算・不可算の両用法を、命題の真偽については可算用法を記している。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】標準語。犯罪・不正の可能性から、会議の中止など出来事や状態の真偽まで、確証のない考えを述べる。  \n\n【文法パターン】suspicion that 〈clause〉＝～ではないかという疑い／have a suspicion that 〈clause〉＝～ではないかという疑いを抱く／arouse 〈person〉's suspicions that 〈clause〉＝〈人〉に～ではないかという疑いを起こさせる／raise some suspicion＝疑いを招く／on suspicion of 〈offence〉＝〈犯罪〉の容疑で／be under suspicion＝疑いをかけられている。  \n\n【コロケーション】\n\n・on suspicion of 〈crime〉  \n用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕・拘束したことを述べる。  \n例: Two people were arrested on suspicion of fraud after the investigation.  \n訳: 捜査後、2人が詐欺の容疑で逮捕された。  \n\n・be under suspicion  \n用途: 人が不正や犯罪をしたのではないかと疑われている状態を表す。  \n例: The contractor remained under suspicion while investigators checked whether it had falsified invoices.  \n訳: 請求書を改ざんしたかどうかを捜査員が調べる間、その請負業者は疑いをかけられたままだった。  \n\n・a suspicion that 〈clause〉  \n用途: 確証がない段階で、節の内容が事実かもしれないという見立てを表す。  \n例: The manager had a suspicion that the cashier had altered the sales records.  \n訳: その管理者は、レジ係が売上記録を改ざんしたのではないかと疑っていた。  \n\n・have a suspicion that 〈clause〉  \n用途: 出来事や状態が実際に起きた、または成り立つのではないかという考えを抱く。  \n例: I had a suspicion that the meeting had been canceled.  \n訳: 会議は中止されたのではないかと私は疑っていた。  \n\n・arouse someone's suspicions  \n用途: ある出来事を受け、〈人〉が節の内容を真実かもしれないと疑うきっかけになる。  \n例: The abrupt policy reversal aroused residents' suspicions that officials had concealed the project's true cost.  \n訳: 突然の方針転換を受けて、住民たちは当局が事業の本当の費用を隠していたのではないかと疑い始めた。  \n\n・raise some suspicion  \n用途: ある発言や出来事が疑いを招くことを表す。  \n例: The unexplained delay raised some suspicion.  \n訳: 説明のつかない遅れが、多少の疑いを招いた。  \n\n【語法・注意】on suspicion of theft は「窃盗で有罪になった」ではなく、「窃盗をした疑いを理由に」という意味である。under suspicion も罪が確定した状態を表さない。Merriam-Webster の法律辞典は suspicion を通常、信念に至らない精神状態として説明し、reasonable suspicion の項目に関連づけている。ここでは特定の法域の法的基準を述べない。  \n\n【類義語】\n\n・doubt  \n定義: ある事柄の真偽について確信が持てない状態。  \n頻度: 〈8/10〉  \n違い: doubt は真偽の不確かさを広く表し、suspicion はある事柄が真実かもしれないという見立ても表す。  \n例: There was some doubt about whether the meeting had been canceled.  \n訳: 会議が中止されたかどうかについて、多少の疑問があった。  \n\n2. 【名詞・可算／不可算】不信、警戒を伴う疑念\n\n【日本語訳・定義】人や物事を十分に信用できず、疑いの目で見る態度を表す。ある事柄が真実かどうかについての見立てを表す語義1とは異なり、対象への不信や警戒に焦点を置く。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】標準語。人や物事、説明などを信用できず、疑いの目で見る態度を述べる。  \n\n【文法パターン】regard 〈person/thing〉 with suspicion＝〈人・物事〉を疑いの目で見る。  \n\n【コロケーション】\n\n・regard 〈person/thing〉 with suspicion  \n用途: 人や物事をすぐには信用せず、疑いの目で見ることを表す。  \n例: Residents regarded the sudden policy change with suspicion.  \n訳: 住民たちは突然の方針変更を疑いの目で見た。  \n\n【語法・注意】with suspicion は、対象を信頼できるか疑って見る態度を表す。  \n\n【類義語】\n\n・distrust  \n定義: 人や物事を信頼できない気持ち。  \n頻度: 〈8/10〉  \n違い: distrust は信頼できない気持ちを直接表し、with suspicion は人や物事を疑いの目で見る態度を表す。Oxford Advanced American Dictionary は suspicion の第3語義を「人や物事を信頼できない気持ち」と説明し、両者の意味の重なりを示す。  \n例: Residents regarded the proposal with distrust.  \n訳: 住民たちはその提案を信用しなかった。  \n\n3. 【名詞・単数／形式的】ごく少量、かすかな兆し\n\n【日本語訳・定義】ものがごく少量、またはかすかな兆候として感じられることを表す。通常 a suspicion of ... の形で使われる。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】単数形で用いる形式的な用法。  \n\n【文法パターン】a suspicion of 〈a smile〉＝笑みがかすかに感じられること／a suspicion of 〈truth〉＝真実味がかすかに感じられること。  \n\n【コロケーション】\n\n・a suspicion of a smile  \n用途: はっきり表れるほどではない、かすかな兆しを描写する。  \n例: There was a suspicion of a smile in her reply.  \n訳: 彼女の返事にはかすかな笑みが感じられた。  \n\n・a suspicion of truth  \n用途: 話や印象に真実味がかすかに感じられることを表す。  \n例: The old tale had a suspicion of truth in it.  \n訳: その古い物語には、どこか真実味が感じられた。  \n\n【語法・注意】この a suspicion of ... は「～を疑うこと」ではなく、「～がごく少量、または兆候としてわずかに感じられること」である。  \n\n【類義語】\n\n・hint  \n定義: Oxfordがこのごく少量・かすかな兆しの語義で挙げる類義語。  \n頻度: 〈8/10〉  \n違い: Oxfordはhintをこの語義の類義語として挙げ、suspicionの用法をformalと記している。  \n例: The tea has a hint of mint.  \n訳: そのお茶にはほのかなミントの風味がある。  \n\n・trace  \n定義: ごくわずかな量や痕跡を表す語。Merriam-Websterは本語義の類義語として挙げている。  \n頻度: 〈8/10〉  \n違い: Merriam-Websterはsuspicionの本語義をbarely detectable amount or traceと説明し、Oxfordはこの用法をformalとしている。  \n例: There was only a trace of smoke in the air.  \n訳: 空気中には煙がほんのわずかに漂っていた。  ",
  "_output_metadata": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-suspicion-20260911T033430Z-c12c3ef3",
    "context_id": "blind-suspicion-context-20260911T033430Z-c12c3ef3",
    "input_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426",
    "prompt_sha256": "3a481b4b5b1236ff386e148bcacc574570b305e79f5e155e9afcd34091f7785c",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false
  },
  "contract_version": "review_preflight_v1"
}
```
