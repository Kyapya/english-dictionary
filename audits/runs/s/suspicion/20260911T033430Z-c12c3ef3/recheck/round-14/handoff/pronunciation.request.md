# Independent checker handoff

Pass: `pronunciation`

Review only the exact input packet included below and the specified checker prompt. Use an independent context. Do not consult earlier review outputs, resolutions, or final-blind findings. Return a single JSON object with the requested pass result. Set `reviewer.mode` to `handoff`, `reviewer.declared_model` to the actual model name available to you (do not guess), `reviewer.ingested_by` to `human`, and `reviewer.agent_id` to your actual unique agent path. Do not reuse an agent_id from another pass.

## Checker prompt

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


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "pronunciation",
  "taxonomy_ids": [
    "pronunciation_symbol_explanation"
  ],
  "specification": "prompts/check_pass_pronunciation_v6.md",
  "input_body_sha256": "8508fef1bf79309ca9c904c1a5b901698298454c0b9cddf6fe1227383f20bc7c",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "Oxford は米・英とも /səˈspɪʃn/ と表記する。Merriam-Webster の音節を区切る発音綴りは sə-ˈspi-shən で、3音節、第2音節に主強勢があることを示す。語頭の su- は強く /suː/ と読まず、弱い /sə/ になる。  "
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
  "source_artifact_sha256": "dc02fc70b5f11b78e5105b0158a8a845a6314d562d748f4e571433de0e727341",
  "normalization_version": "check_pass_semantic_input_v2",
  "normalized_input_sha256": "3872c519b0ecb1c3612a4831e2568bd20901c39ee2cc6d2f9e35da3bfea9646a"
}
```
