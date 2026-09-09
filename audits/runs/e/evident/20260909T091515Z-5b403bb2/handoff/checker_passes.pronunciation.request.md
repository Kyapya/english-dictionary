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
  "input_body_sha256": "7daa0d416ecef06000548e2f59c08bd4394750574e23f19e24855a4a6339257a",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米・英: /ˈevɪdənt/。3音節で、第1音節に主強勢がある。第1音節の /ˈev/ に強勢を置き、第2音節の /ɪ/ は弱く、第3音節は /dənt/ と発音する。語尾の /t/ を落として「エビデン」のようにせず、最後を閉じる。派生副詞 evidently は /ˈevɪdəntli/、同語族の名詞 evidence は /ˈevɪdəns/ で、いずれも語頭側に強勢がある。  "
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
  "source_artifact_sha256": "332d09df7349e755d8dc6fd003742cfb167fb68b64ad41f2a7d6f90fd5d329d9",
  "normalized_input_sha256": "a28cf8cd22927fa516f795888ef0fe4d4d0bd7a1960fba17084613633357192b"
}
```
