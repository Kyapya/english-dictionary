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
