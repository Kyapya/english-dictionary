# Independent checker handoff

Stage: `checker_passes/translation`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.translation.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_translation_v6

## 目的

英文・訳文・定義における意味の保存と方向を検査する。自然な意訳は認めるが、見出し語の構文差・含意・作用関係を誤学習させる変化は認めない。

## 担当タクソノミー分類

- `example_translation_alignment`
- `semantic_direction_reversal`

## 検査ルール

- 各例文と訳について、述語、主語・目的語・補語、行為者・経験者・対象・結果の意味役割を対応させる。
- 肯定・否定、比較基準、程度、数量、時制、相、法、条件、因果、目的を保存する。
- 修飾範囲、焦点、対比、情報構造、明示内容と文脈推論の境界、レジスターと話者評価を保存する。
- コロケーションのpattern・用途・英文・訳が同じ語義、品詞、完全フレームを表すか確認する。英文が別語義でも成立するだけでは合格にしない。
- 作用する側／される側、上位／下位、原因／結果、全体／部分、評価主体／評価対象を逆転させない。
- 日本語訳が自然でも、英文にない必然性・意図・結果・専門的効果を追加していればfindingとする。
- 同じ例文を異なる構文や語義の証明に使い回していないか確認する。
- 問題が1箇所に見える場合も、同じ訳語・関係が入力section内の別箇所で再発していないか確認する。

## 入力として受け取るセクション

- `definitions`
- `collocations_examples`
- `lexical_relations`

front matter、生成過程、通常チェックの過去判断、ACTIVE.mdは受け取らない。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "example_translation_alignment | semantic_direction_reversal",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "何がどの方向・範囲・強さで不一致か",
  "evidence_link_ids": [],
  "suggested_direction": "意味を変えずに直す方向"
}
```

`taxonomy_id`、位置、severity、根拠を必須とする。事実・語法・例文/訳の正誤に関わるものは `blocking`、事実関係を変えない局所的な日本語調整だけを `minor` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "translation",
  "taxonomy_ids": [
    "example_translation_alignment",
    "semantic_direction_reversal"
  ],
  "specification": "prompts/check_pass_translation_v6.md",
  "input_body_sha256": "26cb15323105a5f53191ab8bffe12e1890ef2bf89d7587a1d12e97da3e56c157",
  "input_sections": {
    "definitions": [
      {
        "line": 31,
        "text": "1. 【副詞】それぞれ、順に、各々"
      },
      {
        "line": 33,
        "text": "【日本語訳・定義】2つ以上の人・物・項目のリストと、それらに対応する同数の結果、性質、数値、行為などを示し、1番目同士、2番目同士というように提示された順番で1対1に対応させることを表す。日本語の「それぞれ」に相当するが、単に別々であるだけでなく、対応する項目の順序を指定する点が重要である。  "
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
