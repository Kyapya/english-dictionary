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
  "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
  "input_sections": {
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "形容詞 `consequent` に副詞語尾 `-ly` が付いた語である。`consequent` はラテン語 *consequi*「あとに従う、続いて起こる」にさかのぼり、`con-`「ともに」と *sequi*「従う」に関係する。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・`consequence`：名詞。「結果、影響」。特に複数形 `consequences` は好ましくない結果を指しやすい。  "
      },
      {
        "line": 24,
        "text": "・`consequent`：形容詞。ある出来事の結果として続くことを表す、ややフォーマルな語。  "
      },
      {
        "line": 25,
        "text": "・`consequential`：形容詞。「重要な、重大な」。`consequently` と違い、因果関係をつなぐ副詞ではない。  "
      }
    ],
    "sense_structure": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 31,
        "text": "【日本語訳・定義】前に述べた事実・状況・判断を理由として、後に述べる結果が続くことを示す。単に出来事が後の時点で起こることではなく、前件から後件が結果として導かれることを表す。`so` よりフォーマルで、報告、説明、論証などで使われやすい。  "
      }
    ],
    "frequency_register": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 33,
        "text": "【頻度】〈6/10〉  "
      },
      {
        "line": 35,
        "text": "【レジスター/領域】ややフォーマル。学術文、報告書、ニュース、論理的な説明でよく用いられる。  "
      }
    ],
    "usage_notes": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 66,
        "text": "【語法・注意】`consequently` が示すのは因果関係であり、単なる時間順ではない。後に起きただけなら `subsequently`、次の手順を示すなら `then` を使う。`Because the road was closed, we took a detour.` のように原因を従属節で述べる形と違い、`consequently` は原因から帰結を示す副詞である。`The road was closed; consequently, we took a detour.` のようにピリオドまたはセミコロンで二つの独立節をつなぐのは代表的な書き方だが、`the application was consequently rejected` のように文中でも使える。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 39,
        "text": "【コロケーション】"
      },
      {
        "line": 41,
        "text": "・`Consequently, 〈結果の文〉`  "
      },
      {
        "line": 42,
        "text": "用途: 直前に述べた原因・根拠を受けて、文全体の結論や結果を明示する。  "
      },
      {
        "line": 43,
        "text": "例: The train service was suspended. Consequently, many employees worked from home.  "
      },
      {
        "line": 44,
        "text": "訳: 列車の運行が停止された。その結果、多くの従業員が在宅勤務をした。  "
      },
      {
        "line": 46,
        "text": "・`〈原因となる文〉; consequently, 〈結果の文〉`  "
      },
      {
        "line": 47,
        "text": "用途: 密接な因果関係にある二つの独立節を、セミコロンでつなぐフォーマルな書き方である。  "
      },
      {
        "line": 48,
        "text": "例: The evidence was incomplete; consequently, the committee postponed its decision.  "
      },
      {
        "line": 49,
        "text": "訳: 証拠が不十分だったため、委員会は決定を延期した。  "
      },
      {
        "line": 51,
        "text": "・`〈主語〉 + consequently + 〈動詞句〉`  "
      },
      {
        "line": 52,
        "text": "用途: 結果を表す副詞として、主語の後、主要動詞の前に置く。  "
      },
      {
        "line": 53,
        "text": "例: Demand fell sharply, and the company consequently reduced production.  "
      },
      {
        "line": 54,
        "text": "訳: 需要が急減したため、その会社は結果として生産を減らした。  "
      },
      {
        "line": 56,
        "text": "・`be consequently + 〈過去分詞・形容詞〉`  "
      },
      {
        "line": 57,
        "text": "用途: 原因の結果として生じた状態や判断を、`be` の後で説明する。  "
      },
      {
        "line": 58,
        "text": "例: The deadline was missed, and the application was consequently rejected.  "
      },
      {
        "line": 59,
        "text": "訳: 締切に間に合わなかったため、その申請は結果として却下された。  "
      },
      {
        "line": 61,
        "text": "・`and consequently + 〈動詞句〉`  "
      },
      {
        "line": 62,
        "text": "用途: 一つの節の中で、前の節・句に示された事情の帰結として後続の行為や状態を示す。  "
      },
      {
        "line": 63,
        "text": "例: The region receives little rainfall and consequently faces frequent water shortages.  "
      },
      {
        "line": 64,
        "text": "訳: その地域は降雨量が少なく、その結果しばしば水不足に直面する。  "
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
  },
  "specification_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
  "source_artifact_sha256": "bcea85e6857e24d95179eec8199560c6b551bb2889d5dae928b29cda43626824",
  "normalized_input_sha256": "9a3a86599a97c970e4bf098b1169bfbbcb38d9eae9f5358085a01495b2e8afb4"
}
```
