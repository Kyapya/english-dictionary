# Independent checker handoff

Stage: `checker_passes/pronunciation`

Use a fresh independent reviewer session. Do not inspect prior-round findings, outputs from other passes, or the private alignment key. Review only the exact packet below against the cited checker prompt. Preserve any finding decision and return one raw JSON response as the requested response file; do not edit earlier responses.

Save the raw response at `responses/pronunciation.response.raw.json`. Include the exact `pass_id` and a top-level `reviewer` object with `mode: "handoff"`, your actual `declared_model`, `ingested_by: "human"`, and a unique non-empty `agent_id`. Use a different reviewer identity for each of the seven passes.

## Prompt

# check_pass_pronunciation_v6

## 目的

提示した発音記号と説明文を独立に照合し、記号にない現象、矛盾、変種差分の漏れを検出する。

## 担当タクソノミー分類

- `pronunciation_symbol_explanation`

## 検査ルール

- 示した各IPAを音節に分解し、強勢、各母音・子音、語末、弱形、活用語尾等の説明を記号内の具体位置へ対応させる。
- 説明に対応する記号がない、記号と矛盾する、位置を特定できない記述は誤りとする。
- 米英・地域・品詞・派生形など複数の記号を示した場合、全差分を列挙し、説明文が差分をすべて扱うか確認する。一差分だけを「唯一の差」としない。
- 連結、脱落、同化、フラッピング等を説明する場合、記号が広音表記で現象を直接表さないのか、実際の発音変異として別に述べるのかを明確にする。
- 日本語の近似音をIPAと同一視せず、近似であることと転写方式差を区別する。
- 活用形・派生語の強勢移動や語尾発音は、綴り規則を取り違えず、実在形ごとに確認する。

## 入力として受け取るセクション

- `pronunciation`

## findingの出力スキーマ

```json
{
  "taxonomy_id": "pronunciation_symbol_explanation",
  "location": {
    "section": "pronunciation",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "記号と説明のどの対応が誤りまたは欠落か",
  "evidence_link_ids": [],
  "suggested_direction": "IPAまたは説明を整合させる方向"
}
```

発音記号・強勢・音節・変種差の誤りは `blocking` とする。


## Exact input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "pronunciation",
  "taxonomy_ids": [
    "pronunciation_symbol_explanation"
  ],
  "specification": "prompts/check_pass_pronunciation_v6.md",
  "input_body_sha256": "18178e0a192307a41e4cccafaaf60c75ff89633d50774904ba389187e4d827b6",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "Oxford は米・英とも /səˈspɪʃn/ と表記する。Oxford Advanced Learner’s Dictionary（OALD10）の解説では、位置から分かる音節主音 /n/ は [n̩] のような補助記号を付けずに表す。このため /səˈspɪʃn/ の語末 /n/ が音節を担い、全体は3音節と読める。Merriam-Webster の音節別表記 sə-ˈspi-shən も3音節で、第2音節に主強勢を置く。語頭の su- は強く /suː/ と読まず、弱い /sə/ になる。  "
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
  "specification_sha256": "7e3e94267ac9f917c901c12580b91e570b5989df7adfbf2a39b833478c766d8a",
  "source_artifact_sha256": "73427b11130b2b4ffb18bbf3504e8054253863023f3237f7a828f43026047262",
  "normalization_version": "check_pass_semantic_input_v2",
  "normalized_input_sha256": "058873935f54fe4a7655f589e82ea2fecb2e3728ea1385285c2a319a32db8f2d"
}
```
