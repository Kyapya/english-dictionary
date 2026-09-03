# Independent checker handoff

Stage: `checker_passes/evidence`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.evidence.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_evidence_v6

## 目的

主張単位の根拠リンクが、対象主張を直接支持するかだけを検査する。source-first工程との二重チェックを避けるため、このパスは資料探索計画、source inventoryのcoverage、fact収集をやり直さない。

## 担当タクソノミー分類

- `evidence_claim_mismatch`

## 検査ルール

- source-first工程が固定したsource・fact・claim unit・対象sectionを入力として受け、claimと引用位置または忠実な要約の対応を確認する。
- 資料名や検索結果見出しが存在するだけで合格にせず、locator、該当箇所、支持内容、当該語義・構文への適用範囲を確認する。
- 別義、別品詞、別法域、別地域、別時代の記述を現在の対象主張へ流用しない。
- 高リスク主張に `two_sources_or_primary` が指定される場合、同一引用元を別IDにした重複を独立2資料として数えない。一次資料1件を使う場合は当該主張へ直接適用できることを確認する。
- 発音、語源、語義境界、文法制約、完全フレーム、例文の自然さ、絶対表現、地域差、頻度、専門説明、類義語・反意語差のevidence linkを個別に確認する。
- 断定的主張では支持例だけでなく、source-first記録にある反例・矛盾探索の方法と結果が主張範囲に対応するか確認する。
- 資料が食い違う場合、本文が差を反映して範囲を限定しているかを確認する。根拠から決められない内容をpassにしない。
- このパスはclaimの辞書学的正しさを他パスの代わりに再判定せず、「提示された根拠がそのclaimを支えるか」に限定する。

## 入力として受け取るセクション

- `pronunciation`
- `etymology`
- `word_formation`
- `core_image`
- `sense_structure`
- `frequency_register`
- `frames`
- `collocations_examples`
- `usage_notes`
- `lexical_relations`
- source-first工程が生成したsource inventory、fact、claim unit、evidence link

## findingの出力スキーマ

```json
{
  "taxonomy_id": "evidence_claim_mismatch",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "根拠対象となる本文主張"
  },
  "severity": "blocking | minor",
  "rationale": "source locator・支持内容・適用範囲の不一致",
  "evidence_link_ids": ["問題のある既存link ID"],
  "suggested_direction": "主張限定、根拠差替え、holdの方向"
}
```

根拠が主張を支持しない状態は原則 `blocking` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "evidence",
  "taxonomy_ids": [
    "evidence_claim_mismatch"
  ],
  "specification": "prompts/check_pass_evidence_v6.md",
  "input_body_sha256": "3d410d15a07e5ede38ffe04fc9929e6ee735c87298a38c54ed813514dcdbd7be",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米: /rɪˈspɛktɪvli/｜英: /rɪˈspɛktɪvli/。4音節で、強勢は第2音節の /ˈspɛk/ にある。おおよそ ri-SPEK-tiv-ly と区切って発音し、第1音節の /rɪ/、第3音節の /ɪ/、語末の /li/ は弱くなりやすい。  "
      },
      {
        "line": 16,
        "text": "綴りの -tively は /tɪvli/ で、respectfully /rɪˈspɛktfəli/ のように /f/ を入れない。respectively は副詞、respective は形容詞で、respectively に活用語尾はない。  "
      }
    ],
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
        "text": "・respective：形容詞「それぞれの、各自の」。their respective roles「それぞれの役割」のように名詞を修飾し、対応する複数の名詞句を必ずしも同時に並べるとは限らない。  "
      },
      {
        "line": 27,
        "text": "・respectfully：形容詞 respectful「礼儀正しい、敬意を示す」に -ly が付いた副詞。「謹んで、失礼ながら」の意味で、respectively とは綴りの一部が似るだけで用法が異なる。  "
      }
    ],
    "core_image": [],
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
        "text": "【レジスター/領域】標準語。説明文、学術・科学論文、統計、報告書、ニュース、ビジネス文書で特に多い。会話でも使えるが、対応関係が長くなると文が読みにくくなるため、表や2文に分けることも多い。  "
      }
    ],
    "frames": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 39,
        "text": "【文法パターン】〈対象1〉 and 〈対象2〉 + be・動詞 + 〈対応項目1〉 and 〈対応項目2〉, respectively＝〈対象1〉には〈対応項目1〉、〈対象2〉には〈対応項目2〉／〈値1〉 and 〈値2〉 apply to 〈対象1〉 and 〈対象2〉, respectively＝〈値1〉と〈値2〉が〈対象1〉と〈対象2〉にそれぞれ当てはまる／〈対象1〉 and 〈対象2〉 respectively + 〈動詞句1〉 and 〈動詞句2〉＝〈対象1〉は〈動詞句1〉、〈対象2〉は〈動詞句2〉をそれぞれ行う（文が長くなりやすいため、通常は文末配置が明快）／〈対象1〉 and 〈対象2〉, respectively, + 〈述語〉＝〈対象1〉と〈対象2〉についてそれぞれ（挿入位置。対応先が明確な場合に限る）  "
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
        "text": "訳: 編集者とデザイナーは、それぞれ本文を確認し、レイアウトを準備した。  "
      }
    ],
    "usage_notes": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 78,
        "text": "【語法・注意】respectively は、通常、先に示した2つ以上の項目と、後から示す同数の対応項目を必要とする。The two samples weighed 8 and 11 grams, respectively. なら、先に挙げた第1試料が8グラム、第2試料が11グラムという対応である。項目数が一致しない、対応する先がない、または順番が読み取れない場合は使わず、各対応を明示して書き直す。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 84,
        "text": "【類義語】"
      },
      {
        "line": 86,
        "text": "・in the same order  "
      },
      {
        "line": 87,
        "text": "定義: 先に示されたものと同じ順番で。  "
      },
      {
        "line": 88,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 89,
        "text": "違い: respectively の最も明確な言い換えで、順序対応を直接説明する。文中で副詞として使える respectively より長いが、対応関係を初めて説明するときに分かりやすい。  "
      },
      {
        "line": 90,
        "text": "例: The figures refer to the three regions in the same order.  "
      },
      {
        "line": 91,
        "text": "訳: その数値は、三つの地域に先に示したのと同じ順番で対応している。  "
      },
      {
        "line": 93,
        "text": "・correspondingly  "
      },
      {
        "line": 94,
        "text": "定義: 対応して、相応して、同じような関係で。  "
      },
      {
        "line": 95,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 96,
        "text": "違い: correspondingly は二つの事柄が対応・連動することや、変化の程度が釣り合うことを表し、明示されたリストの順番を必ずしも指定しない。  "
      },
      {
        "line": 97,
        "text": "例: Costs rose, and prices increased correspondingly.  "
      },
      {
        "line": 98,
        "text": "訳: 費用が上がり、それに応じて価格も上昇した。  "
      },
      {
        "line": 100,
        "text": "・separately  "
      },
      {
        "line": 101,
        "text": "定義: 一緒にせず、別々に、個別に。  "
      },
      {
        "line": 102,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 103,
        "text": "違い: separately は分離して扱うことを表すが、二つのリストを提示順に対応させる意味はない。respectively は別々であることより、順序を保った対応に焦点がある。  "
      },
      {
        "line": 104,
        "text": "例: Please pack the two documents separately.  "
      },
      {
        "line": 105,
        "text": "訳: その2通の書類は別々に梱包してください。  "
      },
      {
        "line": 107,
        "text": "・individually  "
      },
      {
        "line": 108,
        "text": "定義: 一つ一つ、個々に、各自で。  "
      },
      {
        "line": 109,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 110,
        "text": "違い: individually は集団ではなく個々を対象にすることを表す。個々の対象を別のリストの同順位項目と対応させる順序の意味は含まない。  "
      },
      {
        "line": 111,
        "text": "例: Each application was reviewed individually.  "
      },
      {
        "line": 112,
        "text": "訳: 各申請は個別に審査された。  "
      },
      {
        "line": 114,
        "text": "・in turn  "
      },
      {
        "line": 115,
        "text": "定義: 順番に、交代で、次々に。  "
      },
      {
        "line": 116,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 117,
        "text": "違い: in turn は時間的・行動的に順番が回ることを表し、二つのリストを同じ順で対応づける respectively とは異なる。  "
      },
      {
        "line": 118,
        "text": "例: The speakers answered the questions in turn.  "
      },
      {
        "line": 119,
        "text": "訳: 発表者たちは順番に質問へ答えた。  "
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
