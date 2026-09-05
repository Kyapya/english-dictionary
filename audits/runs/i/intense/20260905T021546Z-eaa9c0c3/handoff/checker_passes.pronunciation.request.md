# Independent checker handoff

Stage: `checker_passes/pronunciation`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.pronunciation.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
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


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "pronunciation",
  "taxonomy_ids": [
    "pronunciation_symbol_explanation"
  ],
  "specification": "prompts/check_pass_pronunciation_v6.md",
  "input_body_sha256": "d9de6fa1c329e56869587ad1d22ba4bb95aba79b2d19d36eb494ea69d91b5bbf",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米・英: /ɪnˈtens/。2音節で、第2音節の /tens/ に主強勢がある。第1音節は弱めの /ɪn/ で、綴りの -tense は /tens/ と発音する。  "
      },
      {
        "line": 17,
        "text": "intensive /ɪnˈtensɪv/ と発音の始まりは似ているが、intense は最後の音節 /tens/、intensive は /ɪv/ で終わる。  "
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
