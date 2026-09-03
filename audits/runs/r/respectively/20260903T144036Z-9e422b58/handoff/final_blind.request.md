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
  "entry_body": "\n＃発音記号\n\n米: /rɪˈspɛktɪvli/｜英: /rɪˈspɛktɪvli/。4音節で、強勢は第2音節の /ˈspɛk/ にある。おおよそ ri-SPEK-tiv-ly と区切って発音し、第1音節の /rɪ/、第3音節の /ɪ/、語末の /li/ は弱くなりやすい。  \n綴りの -tively は /tɪvli/ で、respectfully /rɪˈspɛktfəli/ のように /f/ を入れない。respectively は副詞、respective は形容詞で、respectively に活用語尾はない。  \n\n＃語源\n\nrespectively は、形容詞 respective に副詞接尾辞 -ly が付いた語である。respective は中英語を経て、中世ラテン語 respectivus「関係を持つ、考慮する」にさかのぼり、ラテン語 respicere「振り返って見る、考慮する」の過去分詞語幹 respect- と関係する。  \n「個々のものに関係する」という respective の意味に -ly が加わり、「個々のものに関係する形で」から、複数の対応項目を提示順に結び付ける現代の用法へ発達した。語源上は respect と関係するが、現代の respectively は「敬意をもって」という意味ではなく、respectfully とも別の語である。  \n\n＃語形成\n\n・respective + -ly → respectively：形容詞 respective「それぞれの、各自の」に副詞接尾辞 -ly が付いた形。並列する項目を順番どおりに対応づける。  \n・respective：形容詞「それぞれの、各自の」。their respective roles「それぞれの役割」のように名詞を修飾し、対応する複数の名詞句を必ずしも同時に並べるとは限らない。これは respectively の別品詞の語義ではなく、respectively がそこから作られた基底形である。  \n・respectfully：形容詞 respectful「礼儀正しい、敬意を示す」に -ly が付いた副詞。「謹んで、失礼ながら」の意味で、respectively とは綴りの一部が似るだけで用法が異なる。  \n\n＃意味・用法・関連表現\n\n1. 【副詞】それぞれ、順に、各々\n\n【日本語訳・定義】2つ以上の人・物・項目のリストと、それらに対応する同数の結果、性質、数値、行為などを示し、1番目同士、2番目同士というように提示された順番で1対1に対応させることを表す。日本語の「それぞれ」に相当するが、単に別々であるだけでなく、対応する項目の順序を指定する点が重要である。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準語。英語全体でも頻度が高く、説明文、学術・科学論文、統計、報告書、ニュース、ビジネス文書で特に多い。会話でも使えるが、対応関係が長くなると文が読みにくくなるため、表や2文に分けることも多い。  \n\n【文法パターン】〈対象1〉 and 〈対象2〉 + be・動詞 + 〈対応項目1〉 and 〈対応項目2〉, respectively＝〈対象1〉には〈対応項目1〉、〈対象2〉には〈対応項目2〉／〈値1〉 and 〈値2〉 apply to 〈対象1〉 and 〈対象2〉, respectively＝〈値1〉と〈値2〉が〈対象1〉と〈対象2〉にそれぞれ当てはまる／〈対象1〉 and 〈対象2〉 respectively + 〈動詞句1〉 and 〈動詞句2〉＝〈対象1〉は〈動詞句1〉、〈対象2〉は〈動詞句2〉をそれぞれ行う（文が長くなりやすいため、通常は文末配置が明快）／〈対象1〉 and 〈対象2〉, respectively, + 〈述語〉＝〈対象1〉と〈対象2〉についてそれぞれ（挿入位置。対応先が明確な場合に限る）  \n\n【コロケーション】\n\n・〈対象1〉 and 〈対象2〉 were 〈値1〉 and 〈値2〉, respectively  \n用途: 人・物・項目の順番と、年齢、順位、数値などの順番を対応させる。  \n例: Mia and Leo were 18 and 21 years old, respectively.  \n訳: ミアとレオは、それぞれ18歳と21歳だった。  \n\n・〈対象1〉 and 〈対象2〉 had 〈値1〉 and 〈値2〉, respectively  \n用途: 二つの対象について、売上、割合、得点などの数値を同じ順番で示す。  \n例: The two stores had sales of $2 million and $1.4 million, respectively.  \n訳: その2店舗の売上は、それぞれ200万ドルと140万ドルだった。  \n\n・〈名詞1〉 and 〈名詞2〉 correspond to 〈項目1〉 and 〈項目2〉, respectively  \n用途: 名前、記号、分類などの対応関係を明示する。  \n例: In the diagram, the solid and dashed lines correspond to observed and predicted values, respectively.  \n訳: 図では、実線と破線がそれぞれ観測値と予測値に対応している。  \n\n・〈値1〉 and 〈値2〉 apply to 〈対象1〉 and 〈対象2〉, respectively  \n用途: 規則、条件、料金、基準などが複数の対象に順番どおり適用されることを示す。  \n例: The lower and higher rates apply to part-time and full-time employees, respectively.  \n訳: 低い料率と高い料率は、それぞれパートタイム従業員とフルタイム従業員に適用される。  \n\n・〈対象1〉 and 〈対象2〉 finished 〈順位1〉 and 〈順位2〉, respectively  \n用途: 競技、試験、選挙などで、複数の対象の順位を列挙順に対応させる。  \n例: Brazil and Canada finished first and second, respectively, in the final ranking.  \n訳: 最終順位では、ブラジルとカナダがそれぞれ1位と2位になった。  \n\n・〈対象1〉 and 〈対象2〉 respectively represent 〈意味1〉 and 〈意味2〉  \n用途: 記号、変数、色などが表すものを、二つのリストの順に対応させる。文中配置だが、対応関係が短く明快な場合に使える。  \n例: In this equation, x and y respectively represent distance and time.  \n訳: この式では、xとyがそれぞれ距離と時間を表す。  \n\n・〈主語1〉 and 〈主語2〉 + 〈動詞句1〉 and 〈動詞句2〉, respectively  \n用途: 二つの主語が異なる行為や役割を担うことを、行為の提示順に対応させる。主語と動詞句の数をそろえる。  \n例: The editor and the designer checked the text and prepared the layout, respectively.  \n訳: 編集者は本文を確認し、デザイナーはレイアウトを準備した。  \n\n【語法・注意】respectively は、通常、先に示した2つ以上の項目と、後から示す同数の対応項目を伴う。The two samples weighed 8 and 11 grams, respectively. なら、先に挙げた第1試料が8グラム、第2試料が11グラムという対応である。項目数や順番から対応関係が明確でない場合は、各対応を明示して書き直す。  \n\n多くの場合、対応する後半のリストの末尾、つまり文末または節末に置き、その直前にコンマを置く。文中の respectively も可能だが、The editor and the designer respectively checked the text and prepared the layout. のように、長い要素を挟むと対応関係が追いにくい。通常は The editor and the designer checked the text and prepared the layout, respectively. のように末尾へ置く方が明快である。  \nrespectively は単なる「別々に」「個別に」を意味する語ではない。辞書で separately と説明される場合もあるが、学習上は「提示順に対応して、それぞれ」と理解すると誤用が少ない。対応する対象のリストを示さず、単に別々の処理を表したい ×We used compounds A and B, respectively. のような文では、respectively ではなく separately などを使う方が自然である。  \nrespective は形容詞で、それぞれの名詞を修飾する。The teams returned to their respective rooms. は「各チームが自分たちの部屋に戻った」で、二つのリストを順番に対応させる respectively とは異なる。respectfully は「礼儀正しく、敬意を示して」であり、順序や対応を表さない。  \n\n【類義語】\n\n・in the same order  \n定義: 先に示されたものと同じ順番で。  \n頻度: 〈8/10〉  \n違い: respectively の最も明確な言い換えで、順序対応を直接説明する。文中で副詞として使える respectively より長いが、対応関係を初めて説明するときに分かりやすい。  \n例: The figures refer to the three regions in the same order.  \n訳: その数値は、三つの地域に先に示したのと同じ順番で対応している。  \n\n・correspondingly  \n定義: 対応して、相応して、同じような関係で。  \n頻度: 〈6/10〉  \n違い: correspondingly は二つの事柄が対応・連動することや、変化の程度が釣り合うことを表し、明示されたリストの順番を必ずしも指定しない。  \n例: Costs rose, and prices increased correspondingly.  \n訳: 費用が上がり、それに応じて価格も上昇した。  \n\n・separately  \n定義: 一緒にせず、別々に、個別に。  \n頻度: 〈10/10〉  \n違い: separately は分離して扱うことを表すが、二つのリストを提示順に対応させる意味はない。respectively は別々であることより、順序を保った対応に焦点がある。  \n例: Please pack the two documents separately.  \n訳: その2通の書類は別々に梱包してください。  \n\n・individually  \n定義: 一つ一つ、個々に、各自で。  \n頻度: 〈8/10〉  \n違い: individually は集団ではなく個々を対象にすることを表す。個々の対象を別のリストの同順位項目と対応させる順序の意味は含まない。  \n例: Each application was reviewed individually.  \n訳: 各申請は個別に審査された。  \n\n・in turn  \n定義: 順番に、交代で、次々に。  \n頻度: 〈9/10〉  \n違い: in turn は時間的・行動的に順番が回ることを表し、二つのリストを同じ順で対応づける respectively とは異なる。  \n例: The speakers answered the questions in turn.  \n訳: 発表者たちは順番に質問へ答えた。  ",
  "_output_metadata": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-respectively-20260903T144036Z-9e422b58",
    "context_id": "blind-respectively-context-20260903T144036Z-9e422b58",
    "input_body_sha256": "26cb15323105a5f53191ab8bffe12e1890ef2bf89d7587a1d12e97da3e56c157",
    "prompt_sha256": "1bb7b1a1c7f589a50a704d1ce6c1ecd0bfb1c9fb689fd481d21bf608438eb7b5",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false
  }
}
```
