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

出力契約: candidateの `rationale` には、そのcandidateの `surface_form`、`frame`、`meaning` のいずれか1つを全文そのまま含め、固有の理由を述べる。findingには本文から抜き出した `scope_anchors`（各要素に `id`、`exact_quote`、`location_hint`）を付け、`rationale` に少なくとも1つの `exact_quote` 全文と、その引用に即した理由を含める。


## Input packet

```json
{
  "stage": "final_blind",
  "entry_body": "\n＃発音記号\n\nCambridge: 米 /ˈkɑːn.sə.kwənt.li/｜英 /ˈkɒn.sɪ.kwənt.li/。Oxford: 米 /ˈkɑːn.sɪ.kwent.li/｜英 /ˈkɒn.sɪ.kwənt.li/。いずれも4音節で、第1音節に主強勢がある。第1音節は米語で /ɑː/、英語で /ɒ/ と表記される。米語では、Cambridge は第2音節を /ə/・第3音節を /kwənt/、Oxford は /ɪ/・/kwent/ と表記する。英語の表記は両辞書で同じである。  \n\n＃語源\n\n`consequently` は `consequent` と関連し、`consequent` はラテン語 *consequi*「あとに従う」にさかのぼる。  \n\n＃語形成\n\n・`consequence`：名詞。「結果、影響」。特に複数形 `consequences` は好ましくない結果を指しやすい。  \n・`consequent`：形容詞。ある出来事の結果として続くことを表す。  \n・`consequential`：形容詞。「結果として生じる」、また「重要な結果を伴う、重要な」。`consequently` と違い、因果関係をつなぐ副詞ではなく形容詞である。  \n\n＃意味・用法・関連表現\n\n1. 【副詞・文副詞／接続副詞】その結果、したがって\n\n【日本語訳・定義】前に述べた事実・状況・判断を理由として、後に述べる結果が続くことを示す。単に出来事が後の時点で起こることではなく、前件から後件が結果または論理的帰結として導かれることを表す。  \n\n【頻度】〈6/10〉  \n\n【レジスター/領域】結果や帰結を述べる文章・説明で用いられる。  \n\n【文法パターン】`〈原因となる文〉. Consequently, 〈結果の文〉`＝その結果、…／`〈原因となる文〉; consequently, 〈結果の文〉`＝…、したがって…／`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する／`〈主語〉 + be + consequently + 〈補語〉`＝〈主語〉はその結果…である／`〈主語〉 + 〈動詞句1〉 and consequently + 〈動詞句2〉`＝〈主語〉は…し、その結果…する。文中では主語の後で主要動詞の前に置く形のほか、`be` の後で補語の前に置く形がある。  \n\n【コロケーション】\n\n・`Consequently, 〈結果の文〉`  \n用途: 直前に述べた原因・根拠を受けて、文全体の結果を明示する。  \n例: The train service was suspended. Consequently, many employees worked from home.  \n訳: 列車の運行が停止された。その結果、多くの従業員が在宅勤務をした。  \n\n・`〈原因となる文〉; consequently, 〈結果の文〉`  \n用途: 原因と結果を一続きの文で示す。  \n例: The evidence was incomplete; consequently, the committee postponed its decision.  \n訳: 証拠が不十分だった。その結果、委員会は決定を延期した。  \n\n・`〈主語〉 + consequently + 〈動詞句〉`  \n用途: 結果を表す副詞として、主語の後、主要動詞の前に置く。  \n例: Demand fell sharply, and the company consequently reduced production.  \n訳: 需要が急減したため、その会社は結果として生産を減らした。  \n\n・`〈主語〉 + be + consequently + 〈過去分詞・形容詞〉`  \n用途: `be` の後で、ある事情の結果としての状態や判断を補語で説明する。  \n例: The deadline was missed, and the application was consequently rejected.  \n訳: 締切に間に合わなかったため、その申請は結果として却下された。  \n\n・`〈主語〉 + 〈動詞句1〉 and consequently + 〈動詞句2〉`  \n用途: 同じ主語の二つの述語を結び、前の内容の結果として後の行為や状態を示す。  \n例: The region receives little rainfall and consequently faces frequent water shortages.  \n訳: その地域は降雨量が少なく、その結果しばしば水不足に直面する。  \n\n【語法・注意】`consequently` は、前に述べた事情・根拠から結果または論理的帰結を示す副詞であり、単なる時間順だけを示す語ではない。文頭だけでなく、接続詞の後や `be` の後で補語の前にも置ける。  \n\n【類義語】\n\n・therefore  \n定義: 前に述べた事実・理由から結果または結論が導かれることを示す。  \n頻度: 〈7/10〉  \n違い: `consequently` と同様に、前の事情を受けた結果を示す。  \n例: The data are incomplete; therefore, no firm conclusion can be drawn.  \n訳: データが不完全なので、確かな結論は導けない。  ",
  "_output_metadata": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-consequently-20260909T021224Z-f618aa9f",
    "context_id": "blind-consequently-context-20260909T021224Z-f618aa9f",
    "input_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
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
