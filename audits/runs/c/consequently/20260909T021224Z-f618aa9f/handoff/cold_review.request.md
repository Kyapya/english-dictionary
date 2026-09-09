# Independent review handoff

Stage: `cold_review`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session.

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
  "entry_body": "\n＃発音記号\n\n米: /ˈkɑːn.sə.kwənt.li/｜英: /ˈkɒn.sɪ.kwənt.li/。いずれも4音節で、第1音節に主強勢がある。米語は第1音節が /ɑː/、英語は /ɒ/ で、さらに米語では第2音節が /ə/、英語では /ɪ/ となる。`quent` の母音はいずれも弱く /ə/ と発音する。  \n\n＃語源\n\n形容詞 `consequent` に副詞語尾 `-ly` が付いた語である。`consequent` はラテン語 *consequi*「あとに従う、続いて起こる」にさかのぼり、`con-`「ともに」と *sequi*「従う」に関係する。  \n\n＃語形成\n\n・`consequence`：名詞。「結果、影響」。特に複数形 `consequences` は好ましくない結果を指しやすい。  \n・`consequent`：形容詞。ある出来事の結果として続くことを表す、ややフォーマルな語。  \n・`consequential`：形容詞。「重要な、重大な」。`consequently` と違い、因果関係をつなぐ副詞ではない。  \n\n＃意味・用法・関連表現\n\n1. 【副詞・文副詞／接続副詞】その結果、したがって\n\n【日本語訳・定義】前に述べた事実・状況・判断を理由として、後に述べる結果が続くことを示す。単に出来事が後の時点で起こることではなく、前件から後件が結果として導かれることを表す。`so` よりフォーマルで、報告、説明、論証などで使われやすい。  \n\n【頻度】〈6/10〉  \n\n【レジスター/領域】ややフォーマル。学術文、報告書、ニュース、論理的な説明でよく用いられる。  \n\n【文法パターン】`〈原因となる文〉. Consequently, 〈結果の文〉`＝その結果、…／`〈原因となる文〉; consequently, 〈結果の文〉`＝…、したがって…／`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する。文頭で使うときは通常後ろにコンマを置き、二つの独立した節をコンマだけでつなぐ `…, consequently, …` は避ける。  \n\n【コロケーション】\n\n・`Consequently, 〈結果の文〉`  \n用途: 直前に述べた原因・根拠を受けて、文全体の結論や結果を明示する。  \n例: The train service was suspended. Consequently, many employees worked from home.  \n訳: 列車の運行が停止された。その結果、多くの従業員が在宅勤務をした。  \n\n・`〈原因となる文〉; consequently, 〈結果の文〉`  \n用途: 密接な因果関係にある二つの独立節を、セミコロンでつなぐフォーマルな書き方である。  \n例: The evidence was incomplete; consequently, the committee postponed its decision.  \n訳: 証拠が不十分だったため、委員会は決定を延期した。  \n\n・`〈主語〉 + consequently + 〈動詞句〉`  \n用途: 結果を表す副詞として、主語の後、主要動詞の前に置く。  \n例: Demand fell sharply, and the company consequently reduced production.  \n訳: 需要が急減したため、その会社は結果として生産を減らした。  \n\n・`be consequently + 〈過去分詞・形容詞〉`  \n用途: 原因の結果として生じた状態や判断を、`be` の後で説明する。  \n例: The deadline was missed, and the application was consequently rejected.  \n訳: 締切に間に合わなかったため、その申請は結果として却下された。  \n\n・`and consequently + 〈動詞句〉`  \n用途: 一つの節の中で、前の節・句に示された事情の帰結として後続の行為や状態を示す。  \n例: The region receives little rainfall and consequently faces frequent water shortages.  \n訳: その地域は降雨量が少なく、その結果しばしば水不足に直面する。  \n\n【語法・注意】`consequently` が示すのは因果関係であり、単なる時間順ではない。後に起きただけなら `subsequently`、次の手順を示すなら `then` を使う。`Because the road was closed, we took a detour.` のように原因を従属節で述べる形と違い、`consequently` は原因から帰結を示す副詞である。`The road was closed; consequently, we took a detour.` のようにピリオドまたはセミコロンで二つの独立節をつなぐのは代表的な書き方だが、`the application was consequently rejected` のように文中でも使える。  \n\n【類義語】\n\n・therefore  \n定義: 前に述べた事実・理由から、論理的な結論や結果が導かれることを示す。  \n頻度: 〈7/10〉  \n違い: `therefore` は論証の結論を明示する響きが特に強い。`consequently` は出来事・状況から実際に続く結果を示すときにも自然である。  \n例: The data are incomplete; therefore, no firm conclusion can be drawn.  \n訳: データが不完全なので、確かな結論は導けない。  \n\n・as a result  \n定義: 前の出来事や状況の結果として、後の出来事が起こることを示す句。  \n頻度: 〈8/10〉  \n違い: `as a result` は日常的で分かりやすく、会話から文章まで広く使える。`consequently` は一語でよりフォーマルに因果関係をつなぐ。  \n例: The supplier delayed delivery. As a result, the launch was postponed.  \n訳: 供給業者が納品を遅らせた。その結果、発売は延期された。  \n\n・thus  \n定義: 前の内容を受けて、結果や論理的帰結を示す。  \n頻度: 〈5/10〉  \n違い: `thus` は書き言葉でより硬く、論文・技術文書では「このように」の意味も持つ。`consequently` はここでいう「その結果」の意味に限られる。  \n例: The sample was contaminated and thus could not be analyzed.  \n訳: 試料が汚染されていたため、したがって分析できなかった。  \n\n・accordingly  \n定義: ある事情・情報に応じて、またはその結果として行動・処置がなされることを示す。  \n頻度: 〈5/10〉  \n違い: `accordingly` は「事情に応じて」の意味で意図的な対応を表すことがある。`consequently` は、対応の意図がなくても因果の結果を示せる。  \n例: The weather forecast changed, so the organizers adjusted the schedule accordingly.  \n訳: 天気予報が変わったので、主催者はそれに応じて日程を調整した。  \n\n・hence  \n定義: 前に述べた理由・事実から結論または結果が生じることを示す。  \n頻度: 〈4/10〉  \n違い: 因果を示す `hence` は `consequently` より文語的で、簡潔な論証や固定表現に多い。また `hence` には「今から〜後」の時間表現など別の用法もある。  \n例: The files were encrypted; hence, only authorized staff could read them.  \n訳: ファイルは暗号化されていた。したがって、閲覧できたのは権限を持つ職員だけだった。  ",
  "_output_metadata": {
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-consequently-20260909T021224Z-f618aa9f",
    "context_id": "cold-consequently-context-20260909T021224Z-f618aa9f",
    "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
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
