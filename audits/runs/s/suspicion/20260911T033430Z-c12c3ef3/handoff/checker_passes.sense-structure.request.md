# Independent checker handoff

Stage: `checker_passes/sense-structure`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.sense-structure.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_sense_structure_v6

## 目的

見出し語をゼロベースで棚卸しし、語義境界、品詞転換、派生形、コアイメージ、セクション横断の意味範囲を検査する。旧本文の語義番号・見出し・項目数を候補集合の出発点にしない。

## 担当タクソノミー分類

- `sense_boundary_overlap`
- `cross_section_internal_contradiction`
- `compound_component_generalization`

## 検査ルール

- 主要品詞、主要義、字義・比喩・慣用義、句動詞、分詞形容詞、主要な品詞転換・派生形を独立候補として確認する。
- 一つの辞書の見出し分けを写さず、完全フレーム、中心意味、結果状態、評価、レジスター、頻度、学習価値から収録・統合・簡潔化・除外を判断する。
- 主語・目的語の種類や対象分野だけで語義を分けず、同じ程度表現・構文・例が複数語義を横断する場合は過剰分割を疑う。
- 基本義から生じる評価的・文脈的含意、特定構文の効果を独立した語彙的意味として立てない。一方、中心意味・品詞・項構造・結果状態・評価が学習上重要に異なる用法は統合しない。
- コアイメージ、語義見出し、定義、語法、文法パターン、類義語説明で同じ概念の範囲・方向が一致するか確認する。
- コアイメージがある場合、列挙枝と明示的除外の和集合が全語義にちょうど1回対応するか確認する。制度上の要件だけが特殊で語彙的核を共有する専門義を枝から除外しない。
- 同語源であることだけを理由に現代話者に結び付きにくい語義を同じ核へ押し込まない。
- 複合語・派生語・専門句の一構成要素の性質を、複合表現全体または見出し語の一般則へ拡張しない。
- 語形成欄や語法注記だけに主要品詞転換が存在する場合は、番号付き語義の欠落として扱う。
- 主要候補の収録先がなければ、形式上の欄が揃っていても欠落とする。除外には自由結合、極低頻度、根拠不足、既出義の言い換え等の具体理由が必要である。

## 入力として受け取るセクション

- `core_image`
- `sense_structure`
- `usage_notes`
- `word_formation`

## findingの出力スキーマ

```json
{
  "taxonomy_id": "sense_boundary_overlap | cross_section_internal_contradiction | compound_component_generalization",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "語義境界・矛盾・一般化の判定理由",
  "evidence_link_ids": [],
  "suggested_direction": "追加・統合・分割・移動・限定の方向"
}
```

語義・品詞・構文構成の追加、削除、統合、分割は `blocking` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "sense-structure",
  "taxonomy_ids": [
    "sense_boundary_overlap",
    "cross_section_internal_contradiction",
    "compound_component_generalization"
  ],
  "specification": "prompts/check_pass_sense_structure_v6.md",
  "input_body_sha256": "82f343438dd0057f0cc4edd16ece26ba75380521e8c02dfb806b6da7eb43d3f8",
  "input_sections": {
    "core_image": [
      {
        "line": 28,
        "text": "＃コアイメージ"
      },
      {
        "line": 30,
        "text": "suspicion の共通核は、「まだ確証はないが、表面に見えていることの背後に別の事実・意図・問題があるのではないかと感じる」ことである。  "
      },
      {
        "line": 31,
        "text": "・人が犯罪・不正をしたのではないかと見る → 「容疑、疑い」（語義1）  "
      },
      {
        "line": 32,
        "text": "・相手や考えをそのまま信用してよいのかと構える → 「不信、疑念」（語義2）  "
      },
      {
        "line": 33,
        "text": "・ある事実が本当なのではないかと推測する → 「気がすること、疑い、予感」（語義3）  "
      },
      {
        "line": 34,
        "text": "・存在を断定するほどではないが、わずかに感じ取れる → 「ほんの少し、かすかな気配」（語義4）  "
      }
    ],
    "sense_structure": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 40,
        "text": "【日本語訳・定義】人が犯罪、不正、不誠実な行為などをした可能性があると、十分な証明がない段階で考えること、またはその疑いを向けられている状態を表す。個々の疑いを数えるときは可算、疑いという状態・雰囲気をまとめて述べるときは不可算で使われる。  "
      },
      {
        "line": 105,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 107,
        "text": "【日本語訳・定義】人、組織、動機、考えなどをそのまま信用せず、「裏に何か問題・意図があるかもしれない」と疑って見る態度を表す。語義1のように特定の犯罪・不正行為を想定する必要はなく、広い意味での mistrust / distrust に近い。  "
      },
      {
        "line": 176,
        "text": "3. 【名詞・可算】～ではないかという気、確証のない推測"
      },
      {
        "line": 178,
        "text": "【日本語訳・定義】ある事実・状況が本当なのではないかと感じることを表す。ここでは犯罪・不正や相手への不信に限らず、証明はないが「たぶんそうだ」という予感・推測を指す。通常は個々の考えとして可算で、a suspicion that ... の形が非常に重要である。  "
      },
      {
        "line": 243,
        "text": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配"
      },
      {
        "line": 245,
        "text": "【日本語訳・定義】色、味、匂い、感情、表情などが、はっきり大量に存在するのではなく「あるかないか分かる程度」にわずかに感じられることを表す。通常 a suspicion of ... の形で用いられる比喩的な用法である。  "
      }
    ],
    "usage_notes": [
      {
        "line": 38,
        "text": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い"
      },
      {
        "line": 80,
        "text": "【語法・注意】on suspicion of theft は「窃盗で有罪になった」ではなく、「窃盗をした疑いを理由に」という意味である。under suspicion も罪が確定した状態を表さない。suspicion of fraud では of の後ろに「疑われている行為・犯罪」が来る一方、suspicion of strangers のような形は文脈によって「見知らぬ人への不信」を表し、語義2に近くなる。accusation や allegation は疑いそのものよりも、誰かが不正をしたという主張を明示的に表に出す点で強い。  "
      },
      {
        "line": 105,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 142,
        "text": "【語法・注意】with suspicion は「疑い深く、信用せずに」という態度を表す。suspicion of fraud の of は通常「詐欺が起きたという疑い」だが、suspicion of outsiders では「よそ者への不信」という対象関係になりやすいので、of を機械的に一つの意味で解釈しない。distrust / mistrust は「信用していない状態」をより直接的に表し、suspicion はしばしば「何か良くない理由・意図があるのではないか」という推測を伴う。skepticism は主張・考えを真だと受け入れることへの慎重さに焦点があり、人の悪意を必ずしも想定しない。  "
      },
      {
        "line": 176,
        "text": "3. 【名詞・可算】～ではないかという気、確証のない推測"
      },
      {
        "line": 218,
        "text": "【語法・注意】この語義では内容が必ず悪いとは限らない。I have a suspicion that she may surprise us with good news. のように、中立・肯定的な内容についても「そうではないかという気」を表せる。ただし語そのものには doubt や hunch より「裏に何かあるのでは」というニュアンスが残りやすい。suspicion that ... の that は内容を導く接続詞で、suspicion of ... の of は名詞句を取る。a sneaking suspicion の sneaking はここでは「盗み歩く」という直訳ではなく、表立って確信してはいないが心の中にある感覚を表す。  "
      },
      {
        "line": 243,
        "text": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配"
      },
      {
        "line": 275,
        "text": "【語法・注意】この a suspicion of ... は「～を疑うこと」ではなく、「～がほんの少し存在すること」である。文体的な比喩なので、意味を誤解されそうな場面では a hint of、a touch of、a trace of が無難である。一部の辞書には suspicion を動詞「疑う」として扱う非標準・方言的な用法も載るが、現代の標準英語では通常 suspect を使うため、本記事では主要語義として立てない。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・suspect：動詞では「～ではないかと疑う、〈人〉を犯人・不正の当事者ではないかと疑う」、名詞では「容疑者」、形容詞では「疑わしい、怪しい」。suspicion はその「疑い・疑念」を名詞として表す。  "
      },
      {
        "line": 24,
        "text": "・suspicious：形容詞。「疑っている、怪しいと思っている」または「疑わしい、怪しい」。人の心理と、対象の性質の両方を表せる。  "
      },
      {
        "line": 25,
        "text": "・suspiciously：副詞。「疑わしそうに、怪しいほど」。行動の見え方にも、程度が不自然に高いことにも使う。  "
      },
      {
        "line": 26,
        "text": "・suspiciousness：名詞。「疑い深さ、疑わしさ」。語としては成立するが、一般には suspicion の方がはるかに広く用いられる。  "
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
  "specification_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
  "source_artifact_sha256": "358a6ef905363f010a31dece02f1dd57e94ea0fad57f759488d3898360d8fc54",
  "normalized_input_sha256": "57e45ba0aaf100a1a4513cb960cca618f9817fa899c0a0ac352896a0b4a3972d"
}
```
