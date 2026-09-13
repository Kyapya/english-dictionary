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
  "input_body_sha256": "f94b51a0c437869d997f727a89666bdfa4c5ffe575c78f10042998526972201c",
  "input_sections": {
    "core_image": [
      {
        "line": 32,
        "text": "＃コアイメージ"
      },
      {
        "line": 34,
        "text": "「同じ対象・尺度・型を前提に、値や状態が変わること、または同類のものの間に違いがあること」。この核から、変化の大きさ、同じ型の別形、集団内の差、主題を変形した作品という語義が生じる。  "
      },
      {
        "line": 35,
        "text": "・同じ尺度で見た値や状態の変化・ばらつき → 「変動・ばらつき」（語義1）  "
      },
      {
        "line": 36,
        "text": "・同じ基本型を保った別の形 → 「変形・別形」（語義2）  "
      },
      {
        "line": 37,
        "text": "・同類の個体や形式の間にある差 → 「個体差・変異」（語義3）  "
      },
      {
        "line": 38,
        "text": "・同じ主題をもとにした展開 → 「変奏・変奏曲」（語義4）  "
      },
      {
        "line": 39,
        "text": "・真北と磁北の間の方位差 → 「磁気偏角」（語義6）  "
      }
    ],
    "sense_structure": [
      {
        "line": 43,
        "text": "1. 【名詞・不可算／可算】変化、変動、ばらつき"
      },
      {
        "line": 45,
        "text": "【日本語訳・定義】量・水準・品質・状態などが一定ではなく変わること、またはその変化の幅・個々の違いを表す。変動・ばらつきを総体として述べる場合は不可算が多く、個々の変化・差・型を数える場合は可算になることが多い。変化が望ましいか望ましくないかは、文脈によって決まり、variation 自体には必ずしも悪い評価はない。  "
      },
      {
        "line": 124,
        "text": "2. 【名詞・可算】基準から少し変えたもの、変形、別形"
      },
      {
        "line": 126,
        "text": "【日本語訳・定義】同じ基本的な考え方・型・作品・方法を保ちながら、内容や構成の一部を変えたものを表す。元と無関係な別物ではなく、「元のものを少し変えた版」という含みがある。`a variation on ...` は「…を土台にした変形・アレンジ」として特に重要である。  "
      },
      {
        "line": 196,
        "text": "3. 【名詞・不可算／可算・生物学・遺伝学・医学】集団内の個体差、変異"
      },
      {
        "line": 198,
        "text": "【日本語訳・定義】同じ種・集団に属する個体の間に見られる、遺伝的・構造的・機能的な差を表す。基準や平均からの逸脱を必須とせず、個体間に自然に存在する差を中立的に指す。言語・地域・社会層などの一般的な形式差は語義1で扱う。  "
      },
      {
        "line": 272,
        "text": "4. 【名詞・可算・音楽】変奏；（複数・作品全体）変奏曲"
      },
      {
        "line": 274,
        "text": "【日本語訳・定義】主題や旋律をもとに、旋律・和声・リズム・調性などを変化させて作る楽曲・楽章、またはその中の一つの展開を表す。単数の `a variation` は通常、一連の変奏のうちの一つの変奏を指し、`variations` 全体や作品全体を指す場合に「変奏曲」とする。主題との連続性を保つ場合が多いが、変化の仕方や主題の現れ方は作品によって異なる。  "
      },
      {
        "line": 320,
        "text": "5. 【名詞・可算・バレエ】ソロ演目、独舞"
      },
      {
        "line": 322,
        "text": "【日本語訳・定義】クラシック・バレエで、踊り手が一人で踊る独立した演目または場面を表す。特に pas de deux などの中で、男女それぞれのソロとして踊られる部分を指すことがある。音楽の変奏曲ではなく、舞踊作品上の演目名である。  "
      },
      {
        "line": 363,
        "text": "6. 【名詞・不可算・航海・地球科学・測量】磁気偏角"
      },
      {
        "line": 365,
        "text": "【日本語訳・定義】地球上のある地点で、真北と磁北がなす水平角、またはその方位差を表す。地域や時期によって異なるため、航海・測量・方位の補正で考慮される。  "
      }
    ],
    "usage_notes": [
      {
        "line": 43,
        "text": "1. 【名詞・不可算／可算】変化、変動、ばらつき"
      },
      {
        "line": 90,
        "text": "【語法・注意】variation は変動やばらつきを総体として述べるときは不可算が多く、a variation/variations は個々の変化・差・型を数えるときに使われることが多い。`variation in prices` は価格の変動、`variations in prices` は複数の価格差・変動の例を指しやすい。`difference` は2つ以上の対象の差に焦点を置くが、variation は基準からの変化や集団全体のばらつきにも使える。`variety` は選択肢や種類の豊富さを表すことが多く、単なる数値の変動には通常 variation を使う。  "
      },
      {
        "line": 124,
        "text": "2. 【名詞・可算】基準から少し変えたもの、変形、別形"
      },
      {
        "line": 171,
        "text": "【語法・注意】`variation on` は元の型・設計・主題を土台にした別形を指すため、語義2の代表表現である。`variation of` も元のものの別形を表すことが多い。これに対し `variation from 〈the norm/standard/original〉` は比較の基準を示し、そこからの相違・ずれに焦点を置く。したがって、`a variation from the original` は文法的には可能だが、元の設計を基にした別形という意味なら `a variation on the original design` の方が自然である。`a variation on a theme` を単に「テーマについての違い」と訳さず、「同じ主題を変形した展開」と捉える。契約・法務の `variation of/to the contract` は「契約の変更」であり、元の型を基にした別形という語義2の一般用法とは文脈が異なる。`alternative` は元の案の代替として選べる別案、`variation` は元の案との連続性を保った変形である。  "
      },
      {
        "line": 196,
        "text": "3. 【名詞・不可算／可算・生物学・遺伝学・医学】集団内の個体差、変異"
      },
      {
        "line": 238,
        "text": "【語法・注意】生物学の `variation` は、集団内の差という現象にも、その差を示す特徴にも使われる。基準からの逸脱を必ずしも含まない点で、`deviation` より中立的である。`mutation` は遺伝物質の配列に起きる変化、`genetic variation` は個体・集団間に観察される遺伝的差の状態・分布を指し、mutation は variation の原因の一つである。両語は同義ではない。  "
      },
      {
        "line": 272,
        "text": "4. 【名詞・可算・音楽】変奏；（複数・作品全体）変奏曲"
      },
      {
        "line": 309,
        "text": "【語法・注意】音楽では通常可算で、`a variation on a theme` は「主題に基づく一つの変奏」、`play/perform a variation` は「変奏を演奏する」と捉える。`a set of variations` や `variations` が一連の変奏・作品全体を指す場合は「変奏曲」「変奏曲集」と訳す。比喩的な `variations on a theme` は元の考えを少し変えた複数の展開を意味する。単に別の演奏や録音を指すときは variation ではなく version や arrangement が自然な場合がある。  "
      },
      {
        "line": 320,
        "text": "5. 【名詞・可算・バレエ】ソロ演目、独舞"
      },
      {
        "line": 352,
        "text": "【語法・注意】この用法の variation は、演奏する曲ではなく踊る演目を指す。バレエ以外の一般的な一人の踊りを述べるなら solo または solo dance の方が広く使える。作品中の一場面全体ではなく、独舞として切り出された部分を指す点に注意する。  "
      },
      {
        "line": 363,
        "text": "6. 【名詞・不可算・航海・地球科学・測量】磁気偏角"
      },
      {
        "line": 380,
        "text": "【語法・注意】この用法は一般的な「変動」ではなく、真北に対する磁北の角度を指す。`magnetic declination` とほぼ同義だが、地理・海図の資料では `magnetic variation` が使われることがある。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "・vary：動詞。「変わる、異なる、変える」。variation と同語源の関連動詞で、vary in/from/with/according to の構文を取る。  "
      },
      {
        "line": 25,
        "text": "・variable：形容詞・名詞。「変動する、可変の；変数」。variation と同語源の重要な関連語で、変化しうる性質や変化する値・要因を表す。  "
      },
      {
        "line": 26,
        "text": "・variant：名詞・形容詞。「異形、変種；異なる」。同じ語族で、同種のものの別形や標準形と異なる型を表し、語義2と特に関係が深い。  "
      },
      {
        "line": 27,
        "text": "・varied：形容詞。「変化に富んだ、さまざまな」。単に variation があるという意味と、内容が豊富だという評価を区別する。  "
      },
      {
        "line": 28,
        "text": "・various：形容詞。「さまざまな、種々の」。同じ語族だが、通常は名詞の前に置いて種類の多さを表す。  "
      },
      {
        "line": 29,
        "text": "・variety：名詞。「多様性、種類、変種」。variation が変化や個々の違いに焦点を置くのに対し、variety は種類の豊富さや選択肢に焦点を置きやすい。  "
      },
      {
        "line": 30,
        "text": "・variational：形容詞。数学・物理などで「変分の、変分法の」。一般会話の「変化に富む」という意味では使わない。  "
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
  "source_artifact_sha256": "64c9981f230b9dfb6e39bf7c429f761f7c5f11a14216883237f10e45fddead74",
  "normalized_input_sha256": "06691232d3f00e15c56998b112b8e71f4d34e7825b1b3fbb9cf7b677ebf0f190"
}
```
