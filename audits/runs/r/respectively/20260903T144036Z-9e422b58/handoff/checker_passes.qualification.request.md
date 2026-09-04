# Independent checker handoff

Stage: `checker_passes/qualification`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.qualification.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_qualification_v6

## 目的

地域・レジスター・頻度・専門制度の限定と、絶対表現の適用範囲を検査する。

## 担当タクソノミー分類

- `regional_qualification`
- `absolute_scope_counterexample`
- `technical_terminology_conventionality`

## 検査ルール

- 米英差・地域差は綴りや発音だけでなく、語義、構文、頻度、自然さ、法域・制度の範囲を確認する。一地域の資料を英語全体へ一般化しない。
- 頻度は英語全体での遭遇頻度として判定し、同一見出し語内の相対順位や特定領域内だけの頻度を使わない。
- 高頻度の主要品詞・主要構文を低頻度の古語・地域語・専門語より先に置き、説明量も優先する。項目数の多さで主要用法の欠落を相殺しない。
- 「必ず」「常に」「最低限」「のみ」「できない」「人なら／物なら」等は、否定、比較、程度表現、別フレームによる反例・打ち消し可能性を探す。傾向・含みを必須条件にしない。
- 各定義主張を、必須条件、傾向・含み、特定条件に限定されるものへ分け、主要フレームへの適用範囲を確認する。
- 法律、保険、税務、医療、資格制度等では、辞書上の語彙的意味と制度上の成立要件、手続き、当事者、対象、効果を分ける。
- 専門訳語・慣用表現を一般語の直訳で置換せず、対象法域・制度の一次資料または信頼できる専門資料で慣用性と範囲を確認する。
- 専門義ブロックの各pattern・collocation・exampleが当該専門義として明確に成立するか確認する。一般義にも同程度に読める例は専門義の中心例にしない。
- 専門・地域ラベルを語義全体へ付けたとき、ブロック内の別一般義・別法域・別レジスターが混入しないか確認する。
- 語源、年代、意味変化、地域差、頻度を根拠以上に断定しない。資料が食い違い範囲を限定できなければhold相当のfindingを返す。

## 入力として受け取るセクション

- `etymology`
- `word_formation`
- `sense_structure`
- `frequency_register`
- `usage_notes`
- `collocations_examples`

## findingの出力スキーマ

```json
{
  "taxonomy_id": "regional_qualification | absolute_scope_counterexample | technical_terminology_conventionality",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "限定不足・反例・専門慣用性の問題",
  "evidence_link_ids": [],
  "suggested_direction": "適用範囲、法域、傾向、専門訳を直す方向"
}
```


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "qualification",
  "taxonomy_ids": [
    "regional_qualification",
    "absolute_scope_counterexample",
    "technical_terminology_conventionality"
  ],
  "specification": "prompts/check_pass_qualification_v6.md",
  "input_body_sha256": "26cb15323105a5f53191ab8bffe12e1890ef2bf89d7587a1d12e97da3e56c157",
  "input_sections": {
    "etymology": [
      {
        "line": 18,
        "text": "＃語源"
      },
      {
        "line": 20,
        "text": "respectively は、形容詞 respective に副詞接尾辞 -ly が付いた語である。respective は中英語を経て、中世ラテン語 respectivus「関係を持つ、考慮する」にさかのぼり、ラテン語 respicere「振り返って見る、考慮する」の過去分詞語幹 respect- と関係する。  "
      },
      {
        "line": 21,
        "text": "「個々のものに関係する」という respective の意味に -ly が加わり、「個々のものに関係する形で」から、複数の対応項目を提示順に結び付ける現代の用法へ発達した。語源上は respect と関係するが、現代の respectively は「敬意をもって」という意味ではなく、respectfully とも別の語である。  "
      }
    ],
    "word_formation": [
      {
        "line": 23,
        "text": "＃語形成"
      },
      {
        "line": 25,
        "text": "・respective + -ly → respectively：形容詞 respective「それぞれの、各自の」に副詞接尾辞 -ly が付いた形。並列する項目を順番どおりに対応づける。  "
      },
      {
        "line": 26,
        "text": "・respective：形容詞「それぞれの、各自の」。their respective roles「それぞれの役割」のように名詞を修飾し、対応する複数の名詞句を必ずしも同時に並べるとは限らない。これは respectively の別品詞の語義ではなく、respectively がそこから作られた基底形である。  "
      },
      {
        "line": 27,
        "text": "・respectfully：形容詞 respectful「礼儀正しい、敬意を示す」に -ly が付いた副詞。「謹んで、失礼ながら」の意味で、respectively とは綴りの一部が似るだけで用法が異なる。  "
      }
    ],
    "sense_structure": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 33,
        "text": "【日本語訳・定義】2つ以上の人・物・項目のリストと、それらに対応する同数の結果、性質、数値、行為などを示し、1番目同士、2番目同士というように提示された順番で1対1に対応させることを表す。日本語の「それぞれ」に相当するが、単に別々であるだけでなく、対応する項目の順序を指定する点が重要である。  "
      }
    ],
    "frequency_register": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 35,
        "text": "【頻度】〈9/10〉  "
      },
      {
        "line": 37,
        "text": "【レジスター/領域】標準語。英語全体でも頻度が高く、説明文、学術・科学論文、統計、報告書、ニュース、ビジネス文書で特に多い。会話でも使えるが、対応関係が長くなると文が読みにくくなるため、表や2文に分けることも多い。  "
      }
    ],
    "usage_notes": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 78,
        "text": "【語法・注意】respectively は、通常、先に示した2つ以上の項目と、後から示す同数の対応項目を伴う。The two samples weighed 8 and 11 grams, respectively. なら、先に挙げた第1試料が8グラム、第2試料が11グラムという対応である。項目数や順番から対応関係が明確でない場合は、各対応を明示して書き直す。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 41,
        "text": "【コロケーション】"
      },
      {
        "line": 43,
        "text": "・〈対象1〉 and 〈対象2〉 were 〈値1〉 and 〈値2〉, respectively  "
      },
      {
        "line": 44,
        "text": "用途: 人・物・項目の順番と、年齢、順位、数値などの順番を対応させる。  "
      },
      {
        "line": 45,
        "text": "例: Mia and Leo were 18 and 21 years old, respectively.  "
      },
      {
        "line": 46,
        "text": "訳: ミアとレオは、それぞれ18歳と21歳だった。  "
      },
      {
        "line": 48,
        "text": "・〈対象1〉 and 〈対象2〉 had 〈値1〉 and 〈値2〉, respectively  "
      },
      {
        "line": 49,
        "text": "用途: 二つの対象について、売上、割合、得点などの数値を同じ順番で示す。  "
      },
      {
        "line": 50,
        "text": "例: The two stores had sales of $2 million and $1.4 million, respectively.  "
      },
      {
        "line": 51,
        "text": "訳: その2店舗の売上は、それぞれ200万ドルと140万ドルだった。  "
      },
      {
        "line": 53,
        "text": "・〈名詞1〉 and 〈名詞2〉 correspond to 〈項目1〉 and 〈項目2〉, respectively  "
      },
      {
        "line": 54,
        "text": "用途: 名前、記号、分類などの対応関係を明示する。  "
      },
      {
        "line": 55,
        "text": "例: In the diagram, the solid and dashed lines correspond to observed and predicted values, respectively.  "
      },
      {
        "line": 56,
        "text": "訳: 図では、実線と破線がそれぞれ観測値と予測値に対応している。  "
      },
      {
        "line": 58,
        "text": "・〈値1〉 and 〈値2〉 apply to 〈対象1〉 and 〈対象2〉, respectively  "
      },
      {
        "line": 59,
        "text": "用途: 規則、条件、料金、基準などが複数の対象に順番どおり適用されることを示す。  "
      },
      {
        "line": 60,
        "text": "例: The lower and higher rates apply to part-time and full-time employees, respectively.  "
      },
      {
        "line": 61,
        "text": "訳: 低い料率と高い料率は、それぞれパートタイム従業員とフルタイム従業員に適用される。  "
      },
      {
        "line": 63,
        "text": "・〈対象1〉 and 〈対象2〉 finished 〈順位1〉 and 〈順位2〉, respectively  "
      },
      {
        "line": 64,
        "text": "用途: 競技、試験、選挙などで、複数の対象の順位を列挙順に対応させる。  "
      },
      {
        "line": 65,
        "text": "例: Brazil and Canada finished first and second, respectively, in the final ranking.  "
      },
      {
        "line": 66,
        "text": "訳: 最終順位では、ブラジルとカナダがそれぞれ1位と2位になった。  "
      },
      {
        "line": 68,
        "text": "・〈対象1〉 and 〈対象2〉 respectively represent 〈意味1〉 and 〈意味2〉  "
      },
      {
        "line": 69,
        "text": "用途: 記号、変数、色などが表すものを、二つのリストの順に対応させる。文中配置だが、対応関係が短く明快な場合に使える。  "
      },
      {
        "line": 70,
        "text": "例: In this equation, x and y respectively represent distance and time.  "
      },
      {
        "line": 71,
        "text": "訳: この式では、xとyがそれぞれ距離と時間を表す。  "
      },
      {
        "line": 73,
        "text": "・〈主語1〉 and 〈主語2〉 + 〈動詞句1〉 and 〈動詞句2〉, respectively  "
      },
      {
        "line": 74,
        "text": "用途: 二つの主語が異なる行為や役割を担うことを、行為の提示順に対応させる。主語と動詞句の数をそろえる。  "
      },
      {
        "line": 75,
        "text": "例: The editor and the designer checked the text and prepared the layout, respectively.  "
      },
      {
        "line": 76,
        "text": "訳: 編集者は本文を確認し、デザイナーはレイアウトを準備した。  "
      }
    ]
  },
  "finding_schema": {
    "required": [
      "taxonomy_id",
      "location",
      "severity",
      "rationale"
    ],
    "severity": [
      "blocking",
      "minor"
    ],
    "location_required": [
      "section",
      "line_start",
      "line_end",
      "exact_quote"
    ]
  }
}
```
