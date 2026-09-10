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
  "input_body_sha256": "dce1e8375f2e9709647eb4c0fd89fa016895cec32363a81b3950d8cdb28a2078",
  "input_sections": {
    "core_image": [
      {
        "line": 29,
        "text": "＃コアイメージ"
      },
      {
        "line": 31,
        "text": "「感覚・理解・判断を通して、対象をきちんと捉える」。この広い核から、対象を理解して妥当な判断をする用法、実用性を優先して選ぶ用法、対象が感覚や理解に届く用法、刺激を感覚として受け取る用法、事実や感情を意識に受け取る用法が生じる。  "
      },
      {
        "line": 32,
        "text": "1の「対象を理解して妥当な判断をする」から、分別のある・道理にかなった・現実的なという意味になる。  "
      },
      {
        "line": 33,
        "text": "2の「実用性を優先して選ぶ」から、衣服や靴などが実用的な、実用本位のという意味になる。  "
      },
      {
        "line": 34,
        "text": "3の「対象が感覚・理解に届く」から、差や変化などが感じ取れる、はっきりしたという意味になる。  "
      },
      {
        "line": 35,
        "text": "4の「外部刺激を感覚として受け取る」から、痛みや熱などを感じ取れるという意味になる。  "
      },
      {
        "line": 36,
        "text": "5の「事実・感情を意識に受け取る」から、事実や恩恵などを意識している、深く感じているという意味になる。  "
      }
    ],
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】感情だけで決めず、理由・経験・実際の条件を考えて、適切で無理のない判断や行動をすることを表す。人にも、考え・助言・計画・解決策などにも使い、話し手が妥当だと評価する含みがある。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 163,
        "text": "【日本語訳・定義】衣服・靴・かばんなどが、流行や見た目よりも、歩きやすさ・丈夫さ・防寒性などの実用性を重視して作られたり選ばれたりしていることを表す。必ずしも醜い、古い、または質が低いという意味ではない。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 232,
        "text": "【日本語訳・定義】差・変化・増減・量などが、感覚や判断によって認識できる程度にはっきりしていることを表す。現代の一般会話での「分別のある」という意味より形式的で、sensible difference や sensible increase のように、無視できない程度を述べる。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 312,
        "text": "【日本語訳・定義】痛み・熱・光などの外部刺激を、感覚器官や身体で受け取る能力があることを表す。現代の一般英語では sensitive to が普通で、sensible to は古風・形式的または専門的に響く。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 373,
        "text": "【日本語訳・定義】事実・危険・義務・誤り・親切などを心で認識し、強く意識していることを表す。通常 sensible of 〈名詞〉の形で使い、現代の会話では aware of、conscious of、grateful for などが自然なことが多い。  "
      }
    ],
    "usage_notes": [
      {
        "line": 40,
        "text": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な"
      },
      {
        "line": 92,
        "text": "【語法・注意】人を主語にした be sensible は「分別をもって行動する」、物事を主語にした a sensible plan は「妥当で現実的な計画」を表す。sensible は必ずしも「賢さ」や高い知能を評価する語ではなく、その場の条件に合った判断をほめる語である。  "
      },
      {
        "line": 161,
        "text": "2. 【形容詞・衣類・靴】実用的な、実用本位の"
      },
      {
        "line": 198,
        "text": "【語法・注意】この用法では、sensible は人の判断を直接修飾するのではなく、実用性を重視して選ばれた物を評価する。fashionable は「流行している」、comfortable は「快適な」に焦点があり、sensible shoes が必ず fashionable でない、または完全に comfortable であるとは限らない。  "
      },
      {
        "line": 230,
        "text": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの"
      },
      {
        "line": 262,
        "text": "【語法・注意】この用法の sensible は「妥当な」という意味ではなく、「感覚や判断に届くほど明らかな」という意味である。ただし、sensible amount は文脈によって「妥当な量」という1の意味にもなるため、差や増減の文脈で理解する。  "
      },
      {
        "line": 310,
        "text": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる"
      },
      {
        "line": 337,
        "text": "【語法・注意】現代英語の sensitive to は「刺激を感じやすい」だけでなく、「影響を受けやすい」「気を悪くしやすい」も表せる。一方、sensible to はこの語義では主に感覚的な知覚を述べ、一般的な「敏感な」の言い換えとして自由に使えるわけではない。  "
      },
      {
        "line": 371,
        "text": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている"
      },
      {
        "line": 403,
        "text": "【語法・注意】sensible of は「～を意識している」であり、1の sensible「分別のある」とは意味が異なる。sensible to は4の「刺激を感じ取れる」と結びつきやすく、事実・恩恵への意識には sensible of を使う。現代的な文章では aware of や conscious of の方が普通である。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "・sensibly：副詞。「分別をもって、現実的に、適切に」。判断や行動の仕方を表す。  "
      },
      {
        "line": 25,
        "text": "・sensibleness：名詞。「分別のあること、現実的であること」。sensible より使用頻度が低い。  "
      },
      {
        "line": 26,
        "text": "・insensible：接頭辞 in- を伴う関連語。「感じない、意識がない、気づかない」。sensible のすべての意味の単純な反意語ではない。  "
      },
      {
        "line": 27,
        "text": "・sensitive、sensibility：同じラテン語の感覚・知覚の語族に属する関連語。ただし、sensitive は「影響を受けやすい・敏感な」、sensibility は「感受性・分別」という別の語として覚える。  "
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
  "source_artifact_sha256": "0035642740b1174f92eb8173dfb0455de3648f65c58090795bb3e13932a0c417",
  "normalized_input_sha256": "600c31b4e9be9f76a4df3259ebcc4ab132a6e2ddd7a3a38204938a3a6fc88683"
}
```
