# Independent checker handoff

Stage: `checker_passes/sense-structure` round 26 (review)

Use a fresh independent reviewer. Review only the exact input packet below against the cited prompt. Do not inspect prior-round findings, outputs from other passes, the private alignment key, or the source inventory beyond the context supplied in this packet. Preserve the raw response unchanged at the path below; do not edit earlier responses.

Save one raw JSON response at `audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-26/responses/sense-structure.response.raw.json`. Include `pass_id`, your actual `declared_model`, `ingested_by: "human"`, and a unique non-empty `agent_id` in the top-level `reviewer` object. Each pass must use a different reviewer identity.

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


## Exact input packet

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
  "input_body_sha256": "d5fed3eeb1ca0acb9286fc85407b81982758943d11ecf86c3e1bf1c18bdd4978",
  "input_sections": {
    "core_image": [
      {
        "line": 26,
        "text": "＃コアイメージ"
      },
      {
        "line": 28,
        "text": "語義1は人の犯罪・不正行為への容疑や、その疑いを向けられた状態を表し、語義2は相手や情報への一般的な不信を表す。語義3は、特定の人に犯罪・不正の容疑を向けるのではなく、ある命題や状況全体の真偽を確証なく推測する焦点をもつ。本記事では、that節が特定の人の犯罪・不正行為を述べる用例は、命題の形であっても語義1に置き、語義3とは分ける。語義4はこれらと分けて、何かがごくわずかに感じられることを表す。  "
      },
      {
        "line": 29,
        "text": "・人が犯罪・不正をしたのではないかと見る → 「容疑、疑い」（語義1）  "
      },
      {
        "line": 30,
        "text": "・相手や考えをそのまま信用してよいのかと構える → 「不信、疑念」（語義2）  "
      },
      {
        "line": 31,
        "text": "・ある命題や状況全体が本当なのではないかと推測する → 「気がすること、疑い、予感」（語義3）  "
      },
      {
        "line": 32,
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
        "text": "【日本語訳・定義】人が犯罪、不正、不誠実な行為をしたとして疑いの対象になること、またはその人の行為に不正の容疑を向けることを表す。焦点は、ある命題の真偽を予想すること自体より、特定の人がその行為をしたとして疑われている点にある。that節を伴う例もあるが、節の話題だけで語義を決めず、人への容疑を表す場合は語義1に置く。複数の個別の疑いを述べる suspicions は可算、疑いという状態を表す suspicion は不可算で使われる。on suspicion of ... のように特定の容疑でも無冠詞となる定型表現があるため、可算・不可算は意味だけで一律には決まらない。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 93,
        "text": "【日本語訳・定義】人、組織、動機、考えなどの真実性や信頼性を確信できず、すぐには信用しない態度を表す。相手や情報の裏に問題や意図があるのではないかという警戒を伴うこともある。語義1のように特定の犯罪・不正行為を想定する必要はなく、広い意味での mistrust / distrust に近い。  "
      },
      {
        "line": 131,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 133,
        "text": "【日本語訳・定義】十分な証拠がなくても、ある命題や状況が真かもしれないと考える、話者の暫定的な推測・予感を表す。焦点は命題の真偽にあり、特定の人を犯罪・不正の容疑者として扱うこと自体ではない。that節の話題だけで語義を決めず、節全体についての推測は語義3、特定の人へ行為の容疑を向ける用法は語義1に置く。この用法では個々の考えを表す可算形が典型。可算・不可算は意味だけで一律に決まらず、構文にも左右される。  "
      },
      {
        "line": 181,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 183,
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
        "text": "【語法・注意】on suspicion of theft は「窃盗の疑いを理由に」という定型表現である。under suspicion は、Oxford の説明では不正をしたのではないかと疑われている状態を表す。that節の形だけでなく意味上の焦点を見る。話者が節全体の真偽を暫定的に推測する用法は語義3、人に不正行為の容疑を向ける用法は語義1に置く。accusation や allegation は類義語ではなく、誰かが不正をしたという主張・告発を指す関連語である。  "
      },
      {
        "line": 91,
        "text": "2. 【名詞・不可算中心】不信、警戒を伴う疑念"
      },
      {
        "line": 113,
        "text": "【語法・注意】with suspicion は「疑いの目で、信用せずに」という態度を表す。Oxford と American Heritage はこの語義を distrust / lack of confidence と説明する。Merriam-Webster は suspicion が真実性・現実性・公正さ・信頼性への信頼の薄さを強調すると説明し、mistrust は疑いに基づく信頼の欠如を強調するとしている。  "
      },
      {
        "line": 131,
        "text": "3. 【名詞・可算中心】～ではないかという気、確証のない推測"
      },
      {
        "line": 163,
        "text": "【語法・注意】この語義では内容は悪いことに限らず、I have a suspicion that she may surprise us with good news. のように中立・肯定的な内容についても「そうではないかという気」を表せる。that節の内容が犯罪・不正かどうかだけで語義を分けない。節全体を真偽未確定の命題として推し量る用法は語義3、特定の人に犯罪・不正の容疑を向ける用法は語義1として説明する。suspicion that ... の that は内容を導く接続詞で、suspicion of ... の of は名詞句を取る。a sneaking suspicion の sneaking はここでは「盗み歩く」という直訳ではなく、表立って確信してはいないが心の中にある感覚を表す。  "
      },
      {
        "line": 181,
        "text": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配"
      },
      {
        "line": 213,
        "text": "【語法・注意】この a suspicion of ... は「～を疑うこと」ではなく、「～がほんの少し存在すること」である。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "Oxford は suspect（動詞・名詞・形容詞）、suspicious（形容詞）、suspiciously（副詞）を suspicion の語族として挙げている。各語の詳しい意味はそれぞれの項目を参照。  "
      },
      {
        "line": 24,
        "text": "なお、動詞 suspicion は Merriam-Webster では主に方言的、American Heritage では口語的な用法として記載されるが、本記事ではその動詞用法を扱わず、名詞用法のみを説明する。  "
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
  "source_artifact_sha256": "71ecbb6ba67c4f2c9c14bc62d9ed607be1a54695728ccde7798ff3b3f68e0bc6",
  "normalization_version": "check_pass_semantic_input_v2",
  "normalized_input_sha256": "07281a5bfa7534361dc3eaf44f9c70ce43a663f721614c91197f0869d7c366f9"
}
```
