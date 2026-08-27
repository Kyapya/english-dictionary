# Independent review handoff

Stage: `checker_passes`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session.

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


# check_pass_frame_relation_v6

## 目的

完全な統語フレームと項の意味役割、および類義語・反意語の語彙関係を検査する。

## 担当タクソノミー分類

- `argument_slot_role_mismatch`
- `lexical_relation_mislabel`

## 検査ルール

- 各語義の宣言品詞・自他・構文種別と、定義、全文法パターン、全コロケーション、全例文を一致させる。
- V、V+O、V+O+O、V+C、V+O+C、補文、前置詞、小辞、受動、分詞形容詞を、実在し学習価値がある完全フレーム単位で確認する。
- 必須要素と任意要素、主語・目的語・補語の典型的意味種類、行為者・経験者・対象・結果を明示し、patternのslotと例文内の実現を一対一で照合する。
- 自他、人目的語／物目的語、能動／受動／分詞形容詞、通常目的語／再帰代名詞、小辞位置、代名詞位置、支配前置詞の差を最小対立で確認する。
- `V + oneself`、`V + oneself + particle/preposition`、対応する受動・形容詞を省略関係として誤説明しない。
- 一つの語義内の全主要フレームへ定義が適用できなければ、不適切な統合としてsense-structure passへunrouted observationを返す。
- `【文法パターン】` の主要構文とコロケーションを相互に対応させる。プレースホルダの各候補を代入したとき冠詞、所有格、前置詞、補語、節構造、語形を補わず成立するか確認する。
- 類義語は中心義が十分に重なる語または定着句に限り、見出し語自身・単なる関連語を含めない。強度、対象、結果、意図性、評価、フォーマル度、地域差等の具体軸で差を示す。
- 反意語は同じ意味軸上の補完、程度、方向、評価、状態の対立に限る。解決策、結果、原因、関連概念を反意語としない。明確な反意語がなければ欄省略を認める。
- 類義語・反意語の頻度と定義は、そのentryが置かれた直前の語義に限定して判定する。

## 入力として受け取るセクション

- `sense_structure`
- `frames`
- `collocations_examples`
- `lexical_relations`

## findingの出力スキーマ

```json
{
  "taxonomy_id": "argument_slot_role_mismatch | lexical_relation_mislabel",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "slot-roleまたは語彙関係の不一致",
  "evidence_link_ids": [],
  "suggested_direction": "完全フレーム化、移動、削除、対立軸修正の方向"
}
```


# check_pass_example_attribution_v6

## 目的

見出し語の各例文が、所属する語義ブロックへ意味的に帰属するかを、所属情報を参照しない先行判定（ブラインド再分類）で検査する。

## 担当タクソノミー分類

- `example_sense_attribution_mismatch`

## 検査ルール

- 検査は必ず次の2段階の順で行い、段階1の判定を段階2より先に確定・記録する。
- 段階1（ブラインド帰属判定）: `sense_structure` から語義番号、見出しの品詞・意味領域ラベル、訳語、定義の一覧を作る。次に `collocations_examples` の各例文（見出し語を含む例文のみ。類義語・反意語欄の例文は対象外）について、所属ブロック、コロケーション見出し、用途行を参照せず、例文と訳だけから最も自然な帰属語義を判定する。次点候補の有無と、判別根拠となった例文内の語句を記録する。
- 段階1では所属語義を含まない `example_attribution_blind_request_v1` だけを受け取り、判定を `example_attribution_blind_record_v1` として保存する。調整役はこの記録が保存されるまで所属キーを渡さない。
- 段階2（照合）: 保存済みの段階1判定を実際の所属ブロックと照合する。この段階で初めて、所属キーと所属語義の【語法・注意】を受け取る。照合時刻は段階1の記録時刻より後でなければならず、最終pass出力に段階1記録を変更せず埋め込む。
- 判定基準は次のとおり。
  - 帰属判定が所属ブロックと不一致: `blocking`。
  - 複数語義で同程度に自然であり、例文内に判別語がない: `blocking`。
  - 一致かつ一意: 問題なし。
- 訳文だけが別語義を示し英文は所属語義に一致する場合は、translationパスの担当として `unrouted_observation` で調整役へ返す。
- 語義の統合・分割そのものに問題があると疑われる場合は、sense-structureパスの担当として `unrouted_observation` で返す。
- 所属ブロックの【語法・注意】が示す語義区別に、そのブロック内の例文が反する場合は、本taxonomyのfindingとして例文側の位置をanchorにする。
- `example_translation_alignment` は英文と訳文の対応だけを扱い、英文自体の語義帰属は本パスが扱う。
- `argument_slot_role_mismatch` は統語スロットと意味役割の実現だけを扱い、統語的に正しいが意味的に別語義である例文は本パスが扱う。
- `cross_section_internal_contradiction` は例文を入力に含めないセクション間矛盾を扱い、例文起点の矛盾は本パスが扱う。

## 入力として受け取るセクション

- `sense_structure`
- `collocations_examples`

段階1入力の `collocations_examples` には、所属ブロック、コロケーション見出し、用途行を除いた例文と訳だけを入れる。段階2の所属キーと所属語義の【語法・注意】は、段階1記録の保存後に別artifactとして受け取る。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "example_sense_attribution_mismatch",
  "location": {
    "section": "collocations_examples",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない例文行"
  },
  "severity": "blocking",
  "rationale": "ブラインド帰属判定、実際の所属語義、曖昧性、判別語の有無",
  "evidence_link_ids": [],
  "suggested_direction": "例文置換 | 語義ブロック間の移動 | 判別語の追加"
}
```

最終pass出力にはfindingと併せて、段階1の `blind_attribution_record`、段階2の `aligned_at`、必要に応じて `unrouted_observations` を含める。`suggested_direction` は例文置換、語義ブロック間の移動、判別語の追加のいずれか1方向を記録する。

段階1はrun別の不透明ID・shuffle順を使う。非公開alignment keyで復元し、request hashを照合する。


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


# check_pass_evidence_v6

## 目的

主張単位の根拠リンクが、対象主張を直接支持するかだけを検査する。source-first工程との二重チェックを避けるため、このパスは資料探索計画、source inventoryのcoverage、fact収集をやり直さない。

## 担当タクソノミー分類

- `evidence_claim_mismatch`

## 検査ルール

- source-first工程が固定したsource・fact・claim unit・対象sectionを入力として受け、claimと引用位置または忠実な要約の対応を確認する。
- 資料名や検索結果見出しが存在するだけで合格にせず、locator、該当箇所、支持内容、当該語義・構文への適用範囲を確認する。
- 別義、別品詞、別法域、別地域、別時代の記述を現在の対象主張へ流用しない。
- 高リスク主張に `two_sources_or_primary` が指定される場合、同一引用元を別IDにした重複を独立2資料として数えない。一次資料1件を使う場合は当該主張へ直接適用できることを確認する。
- 発音、語源、語義境界、文法制約、完全フレーム、例文の自然さ、絶対表現、地域差、頻度、専門説明、類義語・反意語差のevidence linkを個別に確認する。
- 断定的主張では支持例だけでなく、source-first記録にある反例・矛盾探索の方法と結果が主張範囲に対応するか確認する。
- 資料が食い違う場合、本文が差を反映して範囲を限定しているかを確認する。根拠から決められない内容をpassにしない。
- このパスはclaimの辞書学的正しさを他パスの代わりに再判定せず、「提示された根拠がそのclaimを支えるか」に限定する。

## 入力として受け取るセクション

- `pronunciation`
- `etymology`
- `word_formation`
- `core_image`
- `sense_structure`
- `frequency_register`
- `frames`
- `collocations_examples`
- `usage_notes`
- `lexical_relations`
- source-first工程が生成したsource inventory、fact、claim unit、evidence link

## findingの出力スキーマ

```json
{
  "taxonomy_id": "evidence_claim_mismatch",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "根拠対象となる本文主張"
  },
  "severity": "blocking | minor",
  "rationale": "source locator・支持内容・適用範囲の不一致",
  "evidence_link_ids": ["問題のある既存link ID"],
  "suggested_direction": "主張限定、根拠差替え、holdの方向"
}
```

根拠が主張を支持しない状態は原則 `blocking` とする。


## Input packet

```json
{
  "stage": "checker_passes",
  "requests": [
    {
      "schema_version": "check_pass_request_v6",
      "pass_id": "translation",
      "taxonomy_ids": [
        "example_translation_alignment",
        "semantic_direction_reversal"
      ],
      "specification": "prompts/check_pass_translation_v6.md",
      "input_body_sha256": "20ff4e261a57880a6d1394ca4bc4aab61f39016aa205908b40e8d9d4cd222e08",
      "input_sections": {
        "definitions": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 44,
            "text": "【日本語訳・定義】水、エネルギー、森林、野生生物などの自然資源や環境を、浪費、枯渇、破壊から守るために、計画的・慎重に利用し管理すること。利用を一切禁止することではなく、将来も利用できる状態を保つことに重点がある。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 144,
            "text": "【日本語訳・定義】絵画、彫刻、文書、遺跡、歴史的建造物などの文化遺産を、劣化や損傷から守り、その材料、情報、価値を将来へ引き継ぐ専門的な実践・工程。調査、記録、処置、予防的な環境管理を含み、常に元の外観へ作り直すことを意味しない。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 243,
            "text": "【日本語訳・定義】ある系と条件のもとで、エネルギー、運動量、質量、電荷などの物理量の総量が、移動したり別の形に変換されたりしても一定に保たれること。また、その関係を述べる法則。系の一部の量や形が変化しないという意味ではなく、境界を定めた全体の収支が変わらないという意味である。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 52,
            "text": "【コロケーション】"
          },
          {
            "line": 54,
            "text": "・`conservation of 〈natural resource〉`  "
          },
          {
            "line": 55,
            "text": "用途: 水、森林、土壌などの自然資源を、使い切ったり損なったりしないよう管理することを表す。  "
          },
          {
            "line": 56,
            "text": "例: The region introduced strict conservation of groundwater after several dry years.  "
          },
          {
            "line": 57,
            "text": "訳: その地域は数年続いた干ばつの後、地下水の厳格な保全を導入した。  "
          },
          {
            "line": 59,
            "text": "・`wildlife conservation`  "
          },
          {
            "line": 60,
            "text": "用途: 野生動物、その生息地、個体群を保護・管理する活動を表す。  "
          },
          {
            "line": 61,
            "text": "例: Wildlife conservation depends on protecting habitats as well as individual animals.  "
          },
          {
            "line": 62,
            "text": "訳: 野生生物の保全には、個々の動物だけでなく生息地を守ることも必要である。  "
          },
          {
            "line": 64,
            "text": "・`energy conservation`  "
          },
          {
            "line": 65,
            "text": "用途: エネルギーの使用量や浪費を減らし、限られた資源を効率よく使うことを表す。  "
          },
          {
            "line": 66,
            "text": "例: The school installed motion sensors as part of its energy conservation program.  "
          },
          {
            "line": 67,
            "text": "訳: その学校は省エネルギー計画の一環として人感センサーを設置した。  "
          },
          {
            "line": 69,
            "text": "・`water conservation`  "
          },
          {
            "line": 70,
            "text": "用途: 水の使用を抑え、供給源を将来の需要のために維持することを表す。  "
          },
          {
            "line": 71,
            "text": "例: Rain barrels were provided to residents as a water conservation measure.  "
          },
          {
            "line": 72,
            "text": "訳: 節水対策として、住民に雨水貯留タンクが配られた。  "
          },
          {
            "line": 74,
            "text": "・`conservation efforts/measures`  "
          },
          {
            "line": 75,
            "text": "用途: 自然環境や資源を守るための具体的な努力・政策・対策をまとめて表す。  "
          },
          {
            "line": 76,
            "text": "例: The new conservation measures reduced logging in the protected forest.  "
          },
          {
            "line": 77,
            "text": "訳: 新しい保全対策によって、保護林での伐採が減った。  "
          },
          {
            "line": 79,
            "text": "・`marine conservation`  "
          },
          {
            "line": 80,
            "text": "用途: 海洋の生態系、魚類、沿岸環境を保護・管理する活動を表す。  "
          },
          {
            "line": 81,
            "text": "例: The research station funds marine conservation around the coral reef.  "
          },
          {
            "line": 82,
            "text": "訳: その研究所はサンゴ礁周辺の海洋保全に資金を提供している。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 152,
            "text": "【コロケーション】"
          },
          {
            "line": 154,
            "text": "・`conservation of 〈artwork〉`  "
          },
          {
            "line": 155,
            "text": "用途: 絵画、彫刻、工芸品などを調査・処置して安定した状態に保つことを表す。  "
          },
          {
            "line": 156,
            "text": "例: The conservation of the oil painting took six months because the canvas was fragile.  "
          },
          {
            "line": 157,
            "text": "訳: その油彩画はキャンバスがもろかったため、保存修復に6か月かかった。  "
          },
          {
            "line": 159,
            "text": "・`art/heritage conservation`  "
          },
          {
            "line": 160,
            "text": "用途: 美術作品や文化遺産を対象とする専門分野・活動を表す。  "
          },
          {
            "line": 161,
            "text": "例: She studied heritage conservation before joining the national museum.  "
          },
          {
            "line": 162,
            "text": "訳: 彼女は国立博物館に入る前に文化遺産保存を学んだ。  "
          },
          {
            "line": 164,
            "text": "・`conservation treatment`  "
          },
          {
            "line": 165,
            "text": "用途: 専門家が作品や資料に施す具体的な保存修復処置を表す。  "
          },
          {
            "line": 166,
            "text": "例: The conservator recommended a gentle conservation treatment for the cracked varnish.  "
          },
          {
            "line": 167,
            "text": "訳: 保存修復家は、ひびの入ったニスに穏やかな保存修復処置を勧めた。  "
          },
          {
            "line": 169,
            "text": "・`conservation work`  "
          },
          {
            "line": 170,
            "text": "用途: 文化財の安定化、清掃、補修、記録などの保存修復作業をまとめて表す。  "
          },
          {
            "line": 171,
            "text": "例: Conservation work on the medieval manuscript revealed ink beneath a later repair.  "
          },
          {
            "line": 172,
            "text": "訳: その中世写本の保存修復作業によって、後世の補修の下にあるインクが明らかになった。  "
          },
          {
            "line": 174,
            "text": "・`conservation of historic buildings`  "
          },
          {
            "line": 175,
            "text": "用途: 歴史的建造物の材料、構造、特徴を調べ、損傷を抑えて維持することを表す。  "
          },
          {
            "line": 176,
            "text": "例: The conservation of historic buildings must respect evidence of their earlier alterations.  "
          },
          {
            "line": 177,
            "text": "訳: 歴史的建造物の保存では、過去の改変の証拠を尊重しなければならない。  "
          },
          {
            "line": 179,
            "text": "・`a conservation laboratory`  "
          },
          {
            "line": 180,
            "text": "用途: 美術品・文化財の材料分析、状態確認、処置を行う施設を表す。  "
          },
          {
            "line": 181,
            "text": "例: The museum’s conservation laboratory monitors humidity around the wooden sculpture.  "
          },
          {
            "line": 182,
            "text": "訳: その博物館の保存修復研究室は、木彫像の周囲の湿度を監視している。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 251,
            "text": "【コロケーション】"
          },
          {
            "line": 253,
            "text": "・`the law of conservation of energy`  "
          },
          {
            "line": 254,
            "text": "用途: 孤立した系の全エネルギーが、形を変えても一定であるという法則を表す。  "
          },
          {
            "line": 255,
            "text": "例: The law of conservation of energy explains why the total energy of the isolated system stayed constant.  "
          },
          {
            "line": 256,
            "text": "訳: エネルギー保存則は、その孤立系の全エネルギーが一定に保たれた理由を説明する。  "
          },
          {
            "line": 258,
            "text": "・`conservation of momentum`  "
          },
          {
            "line": 259,
            "text": "用途: 外部からの正味の力積が無視できる系で、全運動量が衝突の前後で等しいことを表す。  "
          },
          {
            "line": 260,
            "text": "例: The students used conservation of momentum to calculate the speeds after the collision.  "
          },
          {
            "line": 261,
            "text": "訳: 学生たちは運動量保存を使って、衝突後の速度を計算した。  "
          },
          {
            "line": 263,
            "text": "・`conservation of mass`  "
          },
          {
            "line": 264,
            "text": "用途: 通常の化学反応で原子が消滅・生成せず、反応前後の質量収支が保たれることを表す。  "
          },
          {
            "line": 265,
            "text": "例: The balanced equation reflects conservation of mass: the atoms are rearranged, not created or destroyed.  "
          },
          {
            "line": 266,
            "text": "訳: 係数をそろえた化学式は質量保存を反映している。原子は組み替えられるのであって、生成・消滅するのではない。  "
          },
          {
            "line": 268,
            "text": "・`conservation of charge`  "
          },
          {
            "line": 269,
            "text": "用途: 閉じた収支で電荷が勝手に生じたり消えたりせず、電気回路や反応で電荷の総量が保たれることを表す。  "
          },
          {
            "line": 270,
            "text": "例: Kirchhoff’s current law follows from conservation of electric charge at a circuit junction.  "
          },
          {
            "line": 271,
            "text": "訳: キルヒホッフの電流則は、回路の接点で電気の電荷が保存されることから導かれる。  "
          },
          {
            "line": 273,
            "text": "・`a conservation law`  "
          },
          {
            "line": 274,
            "text": "用途: 特定の物理量の総量が、許された変化の前後で一定であることを述べる法則を表す。  "
          },
          {
            "line": 275,
            "text": "例: A simulation is suspect if it changes total charge without an external source, because it violates a conservation law.  "
          },
          {
            "line": 276,
            "text": "訳: 外部源なしに全電荷を変えるシミュレーションは、保存則に反するため疑わしい。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 89,
            "text": "【類義語】"
          },
          {
            "line": 91,
            "text": "・preservation  "
          },
          {
            "line": 92,
            "text": "定義: 損傷、変化、消失から守り、元の状態に近いまま残すこと。  "
          },
          {
            "line": 93,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 94,
            "text": "違い: `preservation` は変化を避けて現状を保つ焦点が強い。`conservation` は、自然資源を管理しながら使うことや、文化財を処置して安定させることも含む。  "
          },
          {
            "line": 95,
            "text": "例: The preservation of the wetland prevents developers from draining it.  "
          },
          {
            "line": 96,
            "text": "訳: その湿地の保存・保全は、開発業者が排水してしまうのを防ぐ。  "
          },
          {
            "line": 98,
            "text": "・protection  "
          },
          {
            "line": 99,
            "text": "定義: 危険、損害、攻撃などから守ること。  "
          },
          {
            "line": 100,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 101,
            "text": "違い: `protection` は脅威から守るという広い語で、資源を計画的に利用し続ける管理や、総量を保つ技術概念までは必ずしも含まない。  "
          },
          {
            "line": 102,
            "text": "例: The law provides protection for nesting birds during the breeding season.  "
          },
          {
            "line": 103,
            "text": "訳: その法律は繁殖期の営巣する鳥を保護する。  "
          },
          {
            "line": 105,
            "text": "・stewardship  "
          },
          {
            "line": 106,
            "text": "定義: 預かった土地、資源、環境を責任を持って管理すること。  "
          },
          {
            "line": 107,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 108,
            "text": "違い: `stewardship` は管理者の責任や倫理を強調する。`conservation` はその責任から行う具体的な保全活動や政策を指しやすい。  "
          },
          {
            "line": 109,
            "text": "例: Good stewardship of the forest requires both careful harvesting and replanting.  "
          },
          {
            "line": 110,
            "text": "訳: 森林を適切に管理するには、慎重な伐採と再植林の両方が必要である。  "
          },
          {
            "line": 112,
            "text": "・sustainable management  "
          },
          {
            "line": 113,
            "text": "定義: 将来の利用可能性を損なわないよう、資源や活動を管理すること。  "
          },
          {
            "line": 114,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 115,
            "text": "違い: `sustainable management` は将来も成り立つ利用水準や仕組みを明示する複合表現である。`conservation` は保護・損失防止に重点があり、持続可能性全体を必ずしも論じない。  "
          },
          {
            "line": 116,
            "text": "例: Sustainable management of the fishery limits the annual catch.  "
          },
          {
            "line": 117,
            "text": "訳: その漁業の持続可能な管理は年間漁獲量を制限している。  "
          },
          {
            "line": 119,
            "text": "【反意語】"
          },
          {
            "line": 121,
            "text": "・exploitation  "
          },
          {
            "line": 122,
            "text": "定義: 資源や環境を利益のために強く利用し、しばしば限界まで消費すること。  "
          },
          {
            "line": 123,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 124,
            "text": "違い: `exploitation` は利用そのものを指すが、過剰利用や搾取という否定的な含みを持ちやすい。`conservation` は長期的な損失を避ける管理に焦点がある。  "
          },
          {
            "line": 125,
            "text": "例: Uncontrolled exploitation of the forest has reduced the river’s water quality.  "
          },
          {
            "line": 126,
            "text": "訳: 森林の無制限な開発・利用によって、その川の水質が低下した。  "
          },
          {
            "line": 128,
            "text": "・depletion  "
          },
          {
            "line": 129,
            "text": "定義: 資源や蓄えが使われて減少し、ほとんど残らなくなること。  "
          },
          {
            "line": 130,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 131,
            "text": "違い: `depletion` は保全に失敗した結果としての量の減少を表す。故意の利用だけでなく、自然な消耗にも使える。  "
          },
          {
            "line": 132,
            "text": "例: The depletion of the aquifer forced farmers to reduce irrigation.  "
          },
          {
            "line": 133,
            "text": "訳: 帯水層の枯渇によって、農家は灌漑を減らさざるを得なかった。  "
          },
          {
            "line": 135,
            "text": "・waste  "
          },
          {
            "line": 136,
            "text": "定義: 役立つ資源を不注意に、または必要以上に使うこと。  "
          },
          {
            "line": 137,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 138,
            "text": "違い: `waste` は個々の行動や使用の浪費を指す日常語で、自然環境全体の計画的な管理を表す `conservation` より狭い。  "
          },
          {
            "line": 139,
            "text": "例: Leaving the tap running is an unnecessary waste of water.  "
          },
          {
            "line": 140,
            "text": "訳: 蛇口を出しっぱなしにするのは、水の不必要な浪費である。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 188,
            "text": "【類義語】"
          },
          {
            "line": 190,
            "text": "・preservation  "
          },
          {
            "line": 191,
            "text": "定義: 文化財や記録を損傷・劣化から守り、できるだけその状態で残すこと。  "
          },
          {
            "line": 192,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 193,
            "text": "違い: `preservation` は現状を保つ一般語で、専門的な調査・処置の体系まで必ずしも示さない。`conservation` は材料分析、処置、予防管理を含む専門領域を指しやすい。  "
          },
          {
            "line": 194,
            "text": "例: Digital preservation protects the files from becoming unreadable as software changes.  "
          },
          {
            "line": 195,
            "text": "訳: デジタル保存は、ソフトウェアの変化でファイルが読めなくなるのを防ぐ。  "
          },
          {
            "line": 197,
            "text": "・restoration  "
          },
          {
            "line": 198,
            "text": "定義: 作品、建物、物品などを以前の状態・外観に戻すこと。  "
          },
          {
            "line": 199,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 200,
            "text": "違い: `restoration` は欠損の補充や過去の姿の再現に重点がある。`conservation` は現存する材料を安定させることを優先し、完全な復元を目標にしないことがある。  "
          },
          {
            "line": 201,
            "text": "例: The restoration recreated the missing colors, while the conservation treatment stabilized the original paint.  "
          },
          {
            "line": 202,
            "text": "訳: 復元では失われた色を再現し、保存修復処置では元の絵具を安定させた。  "
          },
          {
            "line": 204,
            "text": "・stabilization  "
          },
          {
            "line": 205,
            "text": "定義: 損傷や劣化の進行を止め、対象を安全に扱える状態にすること。  "
          },
          {
            "line": 206,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 207,
            "text": "違い: `stabilization` は保存修復の一工程に焦点を置く。`conservation` は状態確認、記録、予防管理、処置を含むより広い活動である。  "
          },
          {
            "line": 208,
            "text": "例: Stabilization of the loose pages came before the manuscript was put on display.  "
          },
          {
            "line": 209,
            "text": "訳: 写本を展示する前に、外れかけたページの安定化が行われた。  "
          },
          {
            "line": 211,
            "text": "・repair  "
          },
          {
            "line": 212,
            "text": "定義: 壊れたり傷んだりした物を、使える状態に戻すため直すこと。  "
          },
          {
            "line": 213,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 214,
            "text": "違い: `repair` は機能回復の日常語で、元の材料・情報・外観を尊重する専門的な保存判断までは含まない。  "
          },
          {
            "line": 215,
            "text": "例: The repair fixed the frame, but it was not a full conservation treatment.  "
          },
          {
            "line": 216,
            "text": "訳: その修理で額縁は直ったが、完全な保存修復処置ではなかった。  "
          },
          {
            "line": 218,
            "text": "【反意語】"
          },
          {
            "line": 220,
            "text": "・neglect  "
          },
          {
            "line": 221,
            "text": "定義: 必要な世話、管理、処置を怠り、対象を悪化させること。  "
          },
          {
            "line": 222,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 223,
            "text": "違い: `neglect` は保全のために必要な注意や手入れをしないことを表す。故意に壊すことまで必ずしも含まない。  "
          },
          {
            "line": 224,
            "text": "例: Years of neglect left the wooden sculpture vulnerable to insects and moisture.  "
          },
          {
            "line": 225,
            "text": "訳: 何年も放置されたため、その木彫像は虫と湿気に弱い状態になった。  "
          },
          {
            "line": 227,
            "text": "・deterioration  "
          },
          {
            "line": 228,
            "text": "定義: 物の状態、品質、材料が時間とともに悪化すること。  "
          },
          {
            "line": 229,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 230,
            "text": "違い: `deterioration` は保存に失敗した結果として起こる劣化を指す状態名詞で、誰かの行為を直接示す `neglect` とは異なる。  "
          },
          {
            "line": 231,
            "text": "例: The archive reduced deterioration by controlling light and humidity.  "
          },
          {
            "line": 232,
            "text": "訳: その文書館は光と湿度を管理して劣化を抑えた。  "
          },
          {
            "line": 234,
            "text": "・destruction  "
          },
          {
            "line": 235,
            "text": "定義: 物、建物、資料などを壊して存在・形を失わせること。  "
          },
          {
            "line": 236,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 237,
            "text": "違い: `destruction` は保存の目的と正反対の結果を表すが、保存修復が防ごうとするすべての損傷が完全な破壊に至るわけではない。  "
          },
          {
            "line": 238,
            "text": "例: The conservation plan was created to prevent the destruction of the historic site.  "
          },
          {
            "line": 239,
            "text": "訳: その保存計画は、史跡の破壊を防ぐために作られた。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 283,
            "text": "【類義語】"
          },
          {
            "line": 285,
            "text": "・invariance  "
          },
          {
            "line": 286,
            "text": "定義: ある変換、操作、条件のもとで、性質や量が変わらないこと。  "
          },
          {
            "line": 287,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 288,
            "text": "違い: `invariance` は変換に対して同じであるという数学・物理学の性質を強調する。`conservation` は時間発展や相互作用の前後で総量が保たれる収支・法則を指しやすい。  "
          },
          {
            "line": 289,
            "text": "例: The symmetry implies invariance of the equations under a change of coordinates.  "
          },
          {
            "line": 290,
            "text": "訳: その対称性は、座標変換に対して方程式が不変であることを意味する。  "
          },
          {
            "line": 292,
            "text": "・constancy  "
          },
          {
            "line": 293,
            "text": "定義: 量や状態が変わらず一定であること。  "
          },
          {
            "line": 294,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 295,
            "text": "違い: `constancy` は単に変化がないことを表す一般語で、何が保存され、どの系で収支が保たれるかという物理法則の含みは弱い。  "
          },
          {
            "line": 296,
            "text": "例: The experiment measured the constancy of the temperature in the sealed chamber.  "
          },
          {
            "line": 297,
            "text": "訳: その実験は密閉室内の温度が一定であることを測定した。  "
          },
          {
            "line": 299,
            "text": "・preservation  "
          },
          {
            "line": 300,
            "text": "定義: ある性質、量、状態を失わせずに保つこと。  "
          },
          {
            "line": 301,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 302,
            "text": "違い: `preservation` は「保つ」という一般的な意味で技術文書にも現れるが、物理学では特定の量と法則を示す `conservation` が定着している。  "
          },
          {
            "line": 303,
            "text": "例: The model assumes preservation of total mass during the reaction.  "
          },
          {
            "line": 304,
            "text": "訳: そのモデルは反応中に全質量が保たれると仮定している。  "
          },
          {
            "line": 306,
            "text": "【反意語】"
          },
          {
            "line": 308,
            "text": "・nonconservation  "
          },
          {
            "line": 309,
            "text": "定義: 保存されるはずの量が、定めた系や理論のもとで一定に保たれないこと。  "
          },
          {
            "line": 310,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 311,
            "text": "違い: `nonconservation` は一般会話の反対語ではなく、特定の保存則が成り立たないことを述べる専門的な表現である。  "
          },
          {
            "line": 312,
            "text": "例: The proposed interaction would imply nonconservation of electric charge.  "
          },
          {
            "line": 313,
            "text": "訳: その相互作用の提案は、電荷非保存を意味することになる。  "
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
    },
    {
      "schema_version": "check_pass_request_v6",
      "pass_id": "sense-structure",
      "taxonomy_ids": [
        "sense_boundary_overlap",
        "cross_section_internal_contradiction",
        "compound_component_generalization"
      ],
      "specification": "prompts/check_pass_sense_structure_v6.md",
      "input_body_sha256": "20ff4e261a57880a6d1394ca4bc4aab61f39016aa205908b40e8d9d4cd222e08",
      "input_sections": {
        "core_image": [
          {
            "line": 33,
            "text": "＃コアイメージ"
          },
          {
            "line": 35,
            "text": "`conservation` の核は、資源・物・価値・総量などを、損失や望ましくない変化から守って保つことである。何を保つかによって、環境・文化財の実践的な「保全」と、物理学の「総量が変わらない」という専門用法に分かれる。  "
          },
          {
            "line": 36,
            "text": "・自然資源や環境を使い尽くしたり損なったりしないように保つ → 「保全、環境保護、節約」（語義1）  "
          },
          {
            "line": 37,
            "text": "・作品や文化財の材料・情報・価値を損なわずに将来へ保つ → 「保存、保全、保存修復」（語義2）  "
          },
          {
            "line": 38,
            "text": "・系の物理量の総量を変化や変換の前後で保つ → 「保存則、保存」（語義3）  "
          }
        ],
        "sense_structure": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 44,
            "text": "【日本語訳・定義】水、エネルギー、森林、野生生物などの自然資源や環境を、浪費、枯渇、破壊から守るために、計画的・慎重に利用し管理すること。利用を一切禁止することではなく、将来も利用できる状態を保つことに重点がある。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 144,
            "text": "【日本語訳・定義】絵画、彫刻、文書、遺跡、歴史的建造物などの文化遺産を、劣化や損傷から守り、その材料、情報、価値を将来へ引き継ぐ専門的な実践・工程。調査、記録、処置、予防的な環境管理を含み、常に元の外観へ作り直すことを意味しない。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 243,
            "text": "【日本語訳・定義】ある系と条件のもとで、エネルギー、運動量、質量、電荷などの物理量の総量が、移動したり別の形に変換されたりしても一定に保たれること。また、その関係を述べる法則。系の一部の量や形が変化しないという意味ではなく、境界を定めた全体の収支が変わらないという意味である。  "
          }
        ],
        "usage_notes": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 84,
            "text": "【語法・注意】この語義では通常不可算で、`a conservation` とは言わず、`conservation of water`、`conservation efforts` のように使う。`conservation` は「使わないこと」だけでなく、使用量を管理し、損失や破壊を防ぐことを含む。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 184,
            "text": "【語法・注意】この語義の `conservation` は通常不可算で、専門家が対象を記録・安定化・処置しながら残すことを指す。`conservation` と `restoration` は重なるが、`restoration` は過去の状態や外観を再現することに焦点が置かれやすい。保存修復では、後から加えた部分を隠さず、現存する材料と将来の研究可能性を尊重する場合がある。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 278,
            "text": "【語法・注意】物理学の `conservation` は「何も変化しない」という意味ではない。エネルギーが熱や運動エネルギーへ移る、運動量が複数の物体へ分配されるなど、系の内部では形や配分が変わっても、定義した系全体の総量が一定なら保存という。  "
          }
        ],
        "word_formation": [
          {
            "line": 24,
            "text": "＃語形成"
          },
          {
            "line": 26,
            "text": "`conserve` — 動詞「保全する、節約する、保存する」。`conserve water`「水を節約する」、`conserve a historic building`「歴史的建造物を保存する」のように、対象を直接目的語に取る。  "
          },
          {
            "line": 27,
            "text": "`conservationist` — 名詞「自然保護活動家、保全論者」。自然環境や資源の保護を支持・実践する人を指し、文化財保存の専門家を通常この語で呼ぶわけではない。  "
          },
          {
            "line": 28,
            "text": "`conservator` — 名詞「保存修復専門家、保全担当者」。特に美術品・文化財の調査、処置、予防的保存を行う専門家を指す。文脈によっては、資産や組織を管理・保全する人も指す。  "
          },
          {
            "line": 29,
            "text": "`conservancy` — 名詞「保全団体、保全区域、保全活動」。`a land conservancy`「土地保全団体」、`river conservancy`「河川保全活動」のように、組織や制度を指すことが多い。  "
          },
          {
            "line": 30,
            "text": "`conservational` — 形容詞「保全の、保存に関する」。一般会話では頻度が低く、専門的・制度的な文脈で使う。  "
          },
          {
            "line": 31,
            "text": "`conserved quantity` — 物理学で「保存量」。系の条件のもとで総量が一定に保たれる物理量を指す。  "
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
    },
    {
      "schema_version": "check_pass_request_v6",
      "pass_id": "frame-relation",
      "taxonomy_ids": [
        "argument_slot_role_mismatch",
        "lexical_relation_mislabel"
      ],
      "specification": "prompts/check_pass_frame_relation_v6.md",
      "input_body_sha256": "20ff4e261a57880a6d1394ca4bc4aab61f39016aa205908b40e8d9d4cd222e08",
      "input_sections": {
        "sense_structure": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 44,
            "text": "【日本語訳・定義】水、エネルギー、森林、野生生物などの自然資源や環境を、浪費、枯渇、破壊から守るために、計画的・慎重に利用し管理すること。利用を一切禁止することではなく、将来も利用できる状態を保つことに重点がある。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 144,
            "text": "【日本語訳・定義】絵画、彫刻、文書、遺跡、歴史的建造物などの文化遺産を、劣化や損傷から守り、その材料、情報、価値を将来へ引き継ぐ専門的な実践・工程。調査、記録、処置、予防的な環境管理を含み、常に元の外観へ作り直すことを意味しない。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 243,
            "text": "【日本語訳・定義】ある系と条件のもとで、エネルギー、運動量、質量、電荷などの物理量の総量が、移動したり別の形に変換されたりしても一定に保たれること。また、その関係を述べる法則。系の一部の量や形が変化しないという意味ではなく、境界を定めた全体の収支が変わらないという意味である。  "
          }
        ],
        "frames": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 50,
            "text": "【文法パターン】`conservation of 〈natural resource〉`＝～の保全／`wildlife/forest/marine conservation`＝野生生物・森林・海洋の保全／`energy/water conservation`＝省エネルギー・節水／`conservation efforts/measures`＝保全の取り組み・対策／`promote/support conservation`＝保全を促進・支援する  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 150,
            "text": "【文法パターン】`conservation of 〈artwork/manuscript/building〉`＝～の保存修復／`art/heritage conservation`＝美術品・文化遺産の保存／`conservation treatment`＝保存修復処置／`conservation work`＝保存修復作業／`a conservation laboratory`＝保存修復研究室／`conservation and restoration`＝保存修復と復元  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 249,
            "text": "【文法パターン】`conservation of 〈energy/momentum/mass/charge〉`＝エネルギー・運動量・質量・電荷の保存／`the law/principle of conservation of 〈quantity〉`＝～保存の法則・原理／`a conservation law`＝保存則／`obey/test conservation of 〈quantity〉`＝～の保存則に従う・～の保存を検証する  "
          }
        ],
        "collocations_examples": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 52,
            "text": "【コロケーション】"
          },
          {
            "line": 54,
            "text": "・`conservation of 〈natural resource〉`  "
          },
          {
            "line": 55,
            "text": "用途: 水、森林、土壌などの自然資源を、使い切ったり損なったりしないよう管理することを表す。  "
          },
          {
            "line": 56,
            "text": "例: The region introduced strict conservation of groundwater after several dry years.  "
          },
          {
            "line": 57,
            "text": "訳: その地域は数年続いた干ばつの後、地下水の厳格な保全を導入した。  "
          },
          {
            "line": 59,
            "text": "・`wildlife conservation`  "
          },
          {
            "line": 60,
            "text": "用途: 野生動物、その生息地、個体群を保護・管理する活動を表す。  "
          },
          {
            "line": 61,
            "text": "例: Wildlife conservation depends on protecting habitats as well as individual animals.  "
          },
          {
            "line": 62,
            "text": "訳: 野生生物の保全には、個々の動物だけでなく生息地を守ることも必要である。  "
          },
          {
            "line": 64,
            "text": "・`energy conservation`  "
          },
          {
            "line": 65,
            "text": "用途: エネルギーの使用量や浪費を減らし、限られた資源を効率よく使うことを表す。  "
          },
          {
            "line": 66,
            "text": "例: The school installed motion sensors as part of its energy conservation program.  "
          },
          {
            "line": 67,
            "text": "訳: その学校は省エネルギー計画の一環として人感センサーを設置した。  "
          },
          {
            "line": 69,
            "text": "・`water conservation`  "
          },
          {
            "line": 70,
            "text": "用途: 水の使用を抑え、供給源を将来の需要のために維持することを表す。  "
          },
          {
            "line": 71,
            "text": "例: Rain barrels were provided to residents as a water conservation measure.  "
          },
          {
            "line": 72,
            "text": "訳: 節水対策として、住民に雨水貯留タンクが配られた。  "
          },
          {
            "line": 74,
            "text": "・`conservation efforts/measures`  "
          },
          {
            "line": 75,
            "text": "用途: 自然環境や資源を守るための具体的な努力・政策・対策をまとめて表す。  "
          },
          {
            "line": 76,
            "text": "例: The new conservation measures reduced logging in the protected forest.  "
          },
          {
            "line": 77,
            "text": "訳: 新しい保全対策によって、保護林での伐採が減った。  "
          },
          {
            "line": 79,
            "text": "・`marine conservation`  "
          },
          {
            "line": 80,
            "text": "用途: 海洋の生態系、魚類、沿岸環境を保護・管理する活動を表す。  "
          },
          {
            "line": 81,
            "text": "例: The research station funds marine conservation around the coral reef.  "
          },
          {
            "line": 82,
            "text": "訳: その研究所はサンゴ礁周辺の海洋保全に資金を提供している。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 152,
            "text": "【コロケーション】"
          },
          {
            "line": 154,
            "text": "・`conservation of 〈artwork〉`  "
          },
          {
            "line": 155,
            "text": "用途: 絵画、彫刻、工芸品などを調査・処置して安定した状態に保つことを表す。  "
          },
          {
            "line": 156,
            "text": "例: The conservation of the oil painting took six months because the canvas was fragile.  "
          },
          {
            "line": 157,
            "text": "訳: その油彩画はキャンバスがもろかったため、保存修復に6か月かかった。  "
          },
          {
            "line": 159,
            "text": "・`art/heritage conservation`  "
          },
          {
            "line": 160,
            "text": "用途: 美術作品や文化遺産を対象とする専門分野・活動を表す。  "
          },
          {
            "line": 161,
            "text": "例: She studied heritage conservation before joining the national museum.  "
          },
          {
            "line": 162,
            "text": "訳: 彼女は国立博物館に入る前に文化遺産保存を学んだ。  "
          },
          {
            "line": 164,
            "text": "・`conservation treatment`  "
          },
          {
            "line": 165,
            "text": "用途: 専門家が作品や資料に施す具体的な保存修復処置を表す。  "
          },
          {
            "line": 166,
            "text": "例: The conservator recommended a gentle conservation treatment for the cracked varnish.  "
          },
          {
            "line": 167,
            "text": "訳: 保存修復家は、ひびの入ったニスに穏やかな保存修復処置を勧めた。  "
          },
          {
            "line": 169,
            "text": "・`conservation work`  "
          },
          {
            "line": 170,
            "text": "用途: 文化財の安定化、清掃、補修、記録などの保存修復作業をまとめて表す。  "
          },
          {
            "line": 171,
            "text": "例: Conservation work on the medieval manuscript revealed ink beneath a later repair.  "
          },
          {
            "line": 172,
            "text": "訳: その中世写本の保存修復作業によって、後世の補修の下にあるインクが明らかになった。  "
          },
          {
            "line": 174,
            "text": "・`conservation of historic buildings`  "
          },
          {
            "line": 175,
            "text": "用途: 歴史的建造物の材料、構造、特徴を調べ、損傷を抑えて維持することを表す。  "
          },
          {
            "line": 176,
            "text": "例: The conservation of historic buildings must respect evidence of their earlier alterations.  "
          },
          {
            "line": 177,
            "text": "訳: 歴史的建造物の保存では、過去の改変の証拠を尊重しなければならない。  "
          },
          {
            "line": 179,
            "text": "・`a conservation laboratory`  "
          },
          {
            "line": 180,
            "text": "用途: 美術品・文化財の材料分析、状態確認、処置を行う施設を表す。  "
          },
          {
            "line": 181,
            "text": "例: The museum’s conservation laboratory monitors humidity around the wooden sculpture.  "
          },
          {
            "line": 182,
            "text": "訳: その博物館の保存修復研究室は、木彫像の周囲の湿度を監視している。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 251,
            "text": "【コロケーション】"
          },
          {
            "line": 253,
            "text": "・`the law of conservation of energy`  "
          },
          {
            "line": 254,
            "text": "用途: 孤立した系の全エネルギーが、形を変えても一定であるという法則を表す。  "
          },
          {
            "line": 255,
            "text": "例: The law of conservation of energy explains why the total energy of the isolated system stayed constant.  "
          },
          {
            "line": 256,
            "text": "訳: エネルギー保存則は、その孤立系の全エネルギーが一定に保たれた理由を説明する。  "
          },
          {
            "line": 258,
            "text": "・`conservation of momentum`  "
          },
          {
            "line": 259,
            "text": "用途: 外部からの正味の力積が無視できる系で、全運動量が衝突の前後で等しいことを表す。  "
          },
          {
            "line": 260,
            "text": "例: The students used conservation of momentum to calculate the speeds after the collision.  "
          },
          {
            "line": 261,
            "text": "訳: 学生たちは運動量保存を使って、衝突後の速度を計算した。  "
          },
          {
            "line": 263,
            "text": "・`conservation of mass`  "
          },
          {
            "line": 264,
            "text": "用途: 通常の化学反応で原子が消滅・生成せず、反応前後の質量収支が保たれることを表す。  "
          },
          {
            "line": 265,
            "text": "例: The balanced equation reflects conservation of mass: the atoms are rearranged, not created or destroyed.  "
          },
          {
            "line": 266,
            "text": "訳: 係数をそろえた化学式は質量保存を反映している。原子は組み替えられるのであって、生成・消滅するのではない。  "
          },
          {
            "line": 268,
            "text": "・`conservation of charge`  "
          },
          {
            "line": 269,
            "text": "用途: 閉じた収支で電荷が勝手に生じたり消えたりせず、電気回路や反応で電荷の総量が保たれることを表す。  "
          },
          {
            "line": 270,
            "text": "例: Kirchhoff’s current law follows from conservation of electric charge at a circuit junction.  "
          },
          {
            "line": 271,
            "text": "訳: キルヒホッフの電流則は、回路の接点で電気の電荷が保存されることから導かれる。  "
          },
          {
            "line": 273,
            "text": "・`a conservation law`  "
          },
          {
            "line": 274,
            "text": "用途: 特定の物理量の総量が、許された変化の前後で一定であることを述べる法則を表す。  "
          },
          {
            "line": 275,
            "text": "例: A simulation is suspect if it changes total charge without an external source, because it violates a conservation law.  "
          },
          {
            "line": 276,
            "text": "訳: 外部源なしに全電荷を変えるシミュレーションは、保存則に反するため疑わしい。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 89,
            "text": "【類義語】"
          },
          {
            "line": 91,
            "text": "・preservation  "
          },
          {
            "line": 92,
            "text": "定義: 損傷、変化、消失から守り、元の状態に近いまま残すこと。  "
          },
          {
            "line": 93,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 94,
            "text": "違い: `preservation` は変化を避けて現状を保つ焦点が強い。`conservation` は、自然資源を管理しながら使うことや、文化財を処置して安定させることも含む。  "
          },
          {
            "line": 95,
            "text": "例: The preservation of the wetland prevents developers from draining it.  "
          },
          {
            "line": 96,
            "text": "訳: その湿地の保存・保全は、開発業者が排水してしまうのを防ぐ。  "
          },
          {
            "line": 98,
            "text": "・protection  "
          },
          {
            "line": 99,
            "text": "定義: 危険、損害、攻撃などから守ること。  "
          },
          {
            "line": 100,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 101,
            "text": "違い: `protection` は脅威から守るという広い語で、資源を計画的に利用し続ける管理や、総量を保つ技術概念までは必ずしも含まない。  "
          },
          {
            "line": 102,
            "text": "例: The law provides protection for nesting birds during the breeding season.  "
          },
          {
            "line": 103,
            "text": "訳: その法律は繁殖期の営巣する鳥を保護する。  "
          },
          {
            "line": 105,
            "text": "・stewardship  "
          },
          {
            "line": 106,
            "text": "定義: 預かった土地、資源、環境を責任を持って管理すること。  "
          },
          {
            "line": 107,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 108,
            "text": "違い: `stewardship` は管理者の責任や倫理を強調する。`conservation` はその責任から行う具体的な保全活動や政策を指しやすい。  "
          },
          {
            "line": 109,
            "text": "例: Good stewardship of the forest requires both careful harvesting and replanting.  "
          },
          {
            "line": 110,
            "text": "訳: 森林を適切に管理するには、慎重な伐採と再植林の両方が必要である。  "
          },
          {
            "line": 112,
            "text": "・sustainable management  "
          },
          {
            "line": 113,
            "text": "定義: 将来の利用可能性を損なわないよう、資源や活動を管理すること。  "
          },
          {
            "line": 114,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 115,
            "text": "違い: `sustainable management` は将来も成り立つ利用水準や仕組みを明示する複合表現である。`conservation` は保護・損失防止に重点があり、持続可能性全体を必ずしも論じない。  "
          },
          {
            "line": 116,
            "text": "例: Sustainable management of the fishery limits the annual catch.  "
          },
          {
            "line": 117,
            "text": "訳: その漁業の持続可能な管理は年間漁獲量を制限している。  "
          },
          {
            "line": 119,
            "text": "【反意語】"
          },
          {
            "line": 121,
            "text": "・exploitation  "
          },
          {
            "line": 122,
            "text": "定義: 資源や環境を利益のために強く利用し、しばしば限界まで消費すること。  "
          },
          {
            "line": 123,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 124,
            "text": "違い: `exploitation` は利用そのものを指すが、過剰利用や搾取という否定的な含みを持ちやすい。`conservation` は長期的な損失を避ける管理に焦点がある。  "
          },
          {
            "line": 125,
            "text": "例: Uncontrolled exploitation of the forest has reduced the river’s water quality.  "
          },
          {
            "line": 126,
            "text": "訳: 森林の無制限な開発・利用によって、その川の水質が低下した。  "
          },
          {
            "line": 128,
            "text": "・depletion  "
          },
          {
            "line": 129,
            "text": "定義: 資源や蓄えが使われて減少し、ほとんど残らなくなること。  "
          },
          {
            "line": 130,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 131,
            "text": "違い: `depletion` は保全に失敗した結果としての量の減少を表す。故意の利用だけでなく、自然な消耗にも使える。  "
          },
          {
            "line": 132,
            "text": "例: The depletion of the aquifer forced farmers to reduce irrigation.  "
          },
          {
            "line": 133,
            "text": "訳: 帯水層の枯渇によって、農家は灌漑を減らさざるを得なかった。  "
          },
          {
            "line": 135,
            "text": "・waste  "
          },
          {
            "line": 136,
            "text": "定義: 役立つ資源を不注意に、または必要以上に使うこと。  "
          },
          {
            "line": 137,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 138,
            "text": "違い: `waste` は個々の行動や使用の浪費を指す日常語で、自然環境全体の計画的な管理を表す `conservation` より狭い。  "
          },
          {
            "line": 139,
            "text": "例: Leaving the tap running is an unnecessary waste of water.  "
          },
          {
            "line": 140,
            "text": "訳: 蛇口を出しっぱなしにするのは、水の不必要な浪費である。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 188,
            "text": "【類義語】"
          },
          {
            "line": 190,
            "text": "・preservation  "
          },
          {
            "line": 191,
            "text": "定義: 文化財や記録を損傷・劣化から守り、できるだけその状態で残すこと。  "
          },
          {
            "line": 192,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 193,
            "text": "違い: `preservation` は現状を保つ一般語で、専門的な調査・処置の体系まで必ずしも示さない。`conservation` は材料分析、処置、予防管理を含む専門領域を指しやすい。  "
          },
          {
            "line": 194,
            "text": "例: Digital preservation protects the files from becoming unreadable as software changes.  "
          },
          {
            "line": 195,
            "text": "訳: デジタル保存は、ソフトウェアの変化でファイルが読めなくなるのを防ぐ。  "
          },
          {
            "line": 197,
            "text": "・restoration  "
          },
          {
            "line": 198,
            "text": "定義: 作品、建物、物品などを以前の状態・外観に戻すこと。  "
          },
          {
            "line": 199,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 200,
            "text": "違い: `restoration` は欠損の補充や過去の姿の再現に重点がある。`conservation` は現存する材料を安定させることを優先し、完全な復元を目標にしないことがある。  "
          },
          {
            "line": 201,
            "text": "例: The restoration recreated the missing colors, while the conservation treatment stabilized the original paint.  "
          },
          {
            "line": 202,
            "text": "訳: 復元では失われた色を再現し、保存修復処置では元の絵具を安定させた。  "
          },
          {
            "line": 204,
            "text": "・stabilization  "
          },
          {
            "line": 205,
            "text": "定義: 損傷や劣化の進行を止め、対象を安全に扱える状態にすること。  "
          },
          {
            "line": 206,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 207,
            "text": "違い: `stabilization` は保存修復の一工程に焦点を置く。`conservation` は状態確認、記録、予防管理、処置を含むより広い活動である。  "
          },
          {
            "line": 208,
            "text": "例: Stabilization of the loose pages came before the manuscript was put on display.  "
          },
          {
            "line": 209,
            "text": "訳: 写本を展示する前に、外れかけたページの安定化が行われた。  "
          },
          {
            "line": 211,
            "text": "・repair  "
          },
          {
            "line": 212,
            "text": "定義: 壊れたり傷んだりした物を、使える状態に戻すため直すこと。  "
          },
          {
            "line": 213,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 214,
            "text": "違い: `repair` は機能回復の日常語で、元の材料・情報・外観を尊重する専門的な保存判断までは含まない。  "
          },
          {
            "line": 215,
            "text": "例: The repair fixed the frame, but it was not a full conservation treatment.  "
          },
          {
            "line": 216,
            "text": "訳: その修理で額縁は直ったが、完全な保存修復処置ではなかった。  "
          },
          {
            "line": 218,
            "text": "【反意語】"
          },
          {
            "line": 220,
            "text": "・neglect  "
          },
          {
            "line": 221,
            "text": "定義: 必要な世話、管理、処置を怠り、対象を悪化させること。  "
          },
          {
            "line": 222,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 223,
            "text": "違い: `neglect` は保全のために必要な注意や手入れをしないことを表す。故意に壊すことまで必ずしも含まない。  "
          },
          {
            "line": 224,
            "text": "例: Years of neglect left the wooden sculpture vulnerable to insects and moisture.  "
          },
          {
            "line": 225,
            "text": "訳: 何年も放置されたため、その木彫像は虫と湿気に弱い状態になった。  "
          },
          {
            "line": 227,
            "text": "・deterioration  "
          },
          {
            "line": 228,
            "text": "定義: 物の状態、品質、材料が時間とともに悪化すること。  "
          },
          {
            "line": 229,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 230,
            "text": "違い: `deterioration` は保存に失敗した結果として起こる劣化を指す状態名詞で、誰かの行為を直接示す `neglect` とは異なる。  "
          },
          {
            "line": 231,
            "text": "例: The archive reduced deterioration by controlling light and humidity.  "
          },
          {
            "line": 232,
            "text": "訳: その文書館は光と湿度を管理して劣化を抑えた。  "
          },
          {
            "line": 234,
            "text": "・destruction  "
          },
          {
            "line": 235,
            "text": "定義: 物、建物、資料などを壊して存在・形を失わせること。  "
          },
          {
            "line": 236,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 237,
            "text": "違い: `destruction` は保存の目的と正反対の結果を表すが、保存修復が防ごうとするすべての損傷が完全な破壊に至るわけではない。  "
          },
          {
            "line": 238,
            "text": "例: The conservation plan was created to prevent the destruction of the historic site.  "
          },
          {
            "line": 239,
            "text": "訳: その保存計画は、史跡の破壊を防ぐために作られた。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 283,
            "text": "【類義語】"
          },
          {
            "line": 285,
            "text": "・invariance  "
          },
          {
            "line": 286,
            "text": "定義: ある変換、操作、条件のもとで、性質や量が変わらないこと。  "
          },
          {
            "line": 287,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 288,
            "text": "違い: `invariance` は変換に対して同じであるという数学・物理学の性質を強調する。`conservation` は時間発展や相互作用の前後で総量が保たれる収支・法則を指しやすい。  "
          },
          {
            "line": 289,
            "text": "例: The symmetry implies invariance of the equations under a change of coordinates.  "
          },
          {
            "line": 290,
            "text": "訳: その対称性は、座標変換に対して方程式が不変であることを意味する。  "
          },
          {
            "line": 292,
            "text": "・constancy  "
          },
          {
            "line": 293,
            "text": "定義: 量や状態が変わらず一定であること。  "
          },
          {
            "line": 294,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 295,
            "text": "違い: `constancy` は単に変化がないことを表す一般語で、何が保存され、どの系で収支が保たれるかという物理法則の含みは弱い。  "
          },
          {
            "line": 296,
            "text": "例: The experiment measured the constancy of the temperature in the sealed chamber.  "
          },
          {
            "line": 297,
            "text": "訳: その実験は密閉室内の温度が一定であることを測定した。  "
          },
          {
            "line": 299,
            "text": "・preservation  "
          },
          {
            "line": 300,
            "text": "定義: ある性質、量、状態を失わせずに保つこと。  "
          },
          {
            "line": 301,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 302,
            "text": "違い: `preservation` は「保つ」という一般的な意味で技術文書にも現れるが、物理学では特定の量と法則を示す `conservation` が定着している。  "
          },
          {
            "line": 303,
            "text": "例: The model assumes preservation of total mass during the reaction.  "
          },
          {
            "line": 304,
            "text": "訳: そのモデルは反応中に全質量が保たれると仮定している。  "
          },
          {
            "line": 306,
            "text": "【反意語】"
          },
          {
            "line": 308,
            "text": "・nonconservation  "
          },
          {
            "line": 309,
            "text": "定義: 保存されるはずの量が、定めた系や理論のもとで一定に保たれないこと。  "
          },
          {
            "line": 310,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 311,
            "text": "違い: `nonconservation` は一般会話の反対語ではなく、特定の保存則が成り立たないことを述べる専門的な表現である。  "
          },
          {
            "line": 312,
            "text": "例: The proposed interaction would imply nonconservation of electric charge.  "
          },
          {
            "line": 313,
            "text": "訳: その相互作用の提案は、電荷非保存を意味することになる。  "
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
    },
    {
      "schema_version": "example_attribution_blind_request_v1",
      "pass_id": "example-attribution",
      "taxonomy_ids": [
        "example_sense_attribution_mismatch"
      ],
      "specification": "prompts/check_pass_example_attribution_v6.md",
      "input_body_sha256": "20ff4e261a57880a6d1394ca4bc4aab61f39016aa205908b40e8d9d4cd222e08",
      "input_sections": {
        "sense_structure": [
          {
            "sense_id": "sense:001",
            "line": 42,
            "label": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約",
            "definition": "水、エネルギー、森林、野生生物などの自然資源や環境を、浪費、枯渇、破壊から守るために、計画的・慎重に利用し管理すること。利用を一切禁止することではなく、将来も利用できる状態を保つことに重点がある。"
          },
          {
            "sense_id": "sense:002",
            "line": 142,
            "label": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復",
            "definition": "絵画、彫刻、文書、遺跡、歴史的建造物などの文化遺産を、劣化や損傷から守り、その材料、情報、価値を将来へ引き継ぐ専門的な実践・工程。調査、記録、処置、予防的な環境管理を含み、常に元の外観へ作り直すことを意味しない。"
          },
          {
            "sense_id": "sense:003",
            "line": 241,
            "label": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則",
            "definition": "ある系と条件のもとで、エネルギー、運動量、質量、電荷などの物理量の総量が、移動したり別の形に変換されたりしても一定に保たれること。また、その関係を述べる法則。系の一部の量や形が変化しないという意味ではなく、境界を定めた全体の収支が変わらないという意味である。"
          }
        ],
        "collocations_examples": [
          {
            "example_id": "ex-a6ad5fff061c",
            "example": "The law of conservation of energy explains why the total energy of the isolated system stayed constant.",
            "translation": "エネルギー保存則は、その孤立系の全エネルギーが一定に保たれた理由を説明する。"
          },
          {
            "example_id": "ex-8171ee78e7b1",
            "example": "The conservation of the oil painting took six months because the canvas was fragile.",
            "translation": "その油彩画はキャンバスがもろかったため、保存修復に6か月かかった。"
          },
          {
            "example_id": "ex-5845b0cabab0",
            "example": "The conservation of historic buildings must respect evidence of their earlier alterations.",
            "translation": "歴史的建造物の保存では、過去の改変の証拠を尊重しなければならない。"
          },
          {
            "example_id": "ex-28d1f5892ebb",
            "example": "Wildlife conservation depends on protecting habitats as well as individual animals.",
            "translation": "野生生物の保全には、個々の動物だけでなく生息地を守ることも必要である。"
          },
          {
            "example_id": "ex-e5eb0bfa0d9e",
            "example": "The new conservation measures reduced logging in the protected forest.",
            "translation": "新しい保全対策によって、保護林での伐採が減った。"
          },
          {
            "example_id": "ex-464057260ced",
            "example": "The conservator recommended a gentle conservation treatment for the cracked varnish.",
            "translation": "保存修復家は、ひびの入ったニスに穏やかな保存修復処置を勧めた。"
          },
          {
            "example_id": "ex-6d485aea4fdf",
            "example": "Kirchhoff’s current law follows from conservation of electric charge at a circuit junction.",
            "translation": "キルヒホッフの電流則は、回路の接点で電気の電荷が保存されることから導かれる。"
          },
          {
            "example_id": "ex-674b0e2105ca",
            "example": "The region introduced strict conservation of groundwater after several dry years.",
            "translation": "その地域は数年続いた干ばつの後、地下水の厳格な保全を導入した。"
          },
          {
            "example_id": "ex-838068ba5036",
            "example": "The school installed motion sensors as part of its energy conservation program.",
            "translation": "その学校は省エネルギー計画の一環として人感センサーを設置した。"
          },
          {
            "example_id": "ex-2804b62504c3",
            "example": "Conservation work on the medieval manuscript revealed ink beneath a later repair.",
            "translation": "その中世写本の保存修復作業によって、後世の補修の下にあるインクが明らかになった。"
          },
          {
            "example_id": "ex-8c1b795c6ccf",
            "example": "The balanced equation reflects conservation of mass: the atoms are rearranged, not created or destroyed.",
            "translation": "係数をそろえた化学式は質量保存を反映している。原子は組み替えられるのであって、生成・消滅するのではない。"
          },
          {
            "example_id": "ex-a638f6e5db91",
            "example": "Rain barrels were provided to residents as a water conservation measure.",
            "translation": "節水対策として、住民に雨水貯留タンクが配られた。"
          },
          {
            "example_id": "ex-75643da5be04",
            "example": "The students used conservation of momentum to calculate the speeds after the collision.",
            "translation": "学生たちは運動量保存を使って、衝突後の速度を計算した。"
          },
          {
            "example_id": "ex-da2bdf7fa51c",
            "example": "She studied heritage conservation before joining the national museum.",
            "translation": "彼女は国立博物館に入る前に文化遺産保存を学んだ。"
          },
          {
            "example_id": "ex-3e586d6909fd",
            "example": "A simulation is suspect if it changes total charge without an external source, because it violates a conservation law.",
            "translation": "外部源なしに全電荷を変えるシミュレーションは、保存則に反するため疑わしい。"
          },
          {
            "example_id": "ex-e3e9babc0d1f",
            "example": "The research station funds marine conservation around the coral reef.",
            "translation": "その研究所はサンゴ礁周辺の海洋保全に資金を提供している。"
          },
          {
            "example_id": "ex-ca0b7f8b7289",
            "example": "The museum’s conservation laboratory monitors humidity around the wooden sculpture.",
            "translation": "その博物館の保存修復研究室は、木彫像の周囲の湿度を監視している。"
          }
        ]
      },
      "blind_protocol": {
        "stage": 1,
        "withheld_fields": [
          "assigned_sense_id",
          "collocation_heading",
          "usage_line",
          "example_group_boundary",
          "document_order"
        ],
        "required_output_schema": "example_attribution_blind_record_v1"
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
    },
    {
      "schema_version": "check_pass_request_v6",
      "pass_id": "qualification",
      "taxonomy_ids": [
        "regional_qualification",
        "absolute_scope_counterexample",
        "technical_terminology_conventionality"
      ],
      "specification": "prompts/check_pass_qualification_v6.md",
      "input_body_sha256": "20ff4e261a57880a6d1394ca4bc4aab61f39016aa205908b40e8d9d4cd222e08",
      "input_sections": {
        "etymology": [
          {
            "line": 19,
            "text": "＃語源"
          },
          {
            "line": 21,
            "text": "`conservation` は中英語 `conservacioun`、古フランス語 `conservation` を経て、ラテン語 `conservatio`「保存、保全」に由来する。ラテン語 `conservare`「保つ、損なわないようにする」にさかのぼり、英語では「失われたり損なわれたりしないように保つこと」を中心に意味を発達させた。  "
          },
          {
            "line": 22,
            "text": "現代英語では、自然資源を使いながら将来の損失を防ぐ保全、文化財の材料と価値を守る専門的保存、変化の前後で物理量の総量を保つ保存則へと用法が分かれる。物理学の用法は、日常的な「節約」から直接導かれたというより、「総量を失わせず保つ」という共通の概念を技術用語として用いるものである。  "
          }
        ],
        "word_formation": [
          {
            "line": 24,
            "text": "＃語形成"
          },
          {
            "line": 26,
            "text": "`conserve` — 動詞「保全する、節約する、保存する」。`conserve water`「水を節約する」、`conserve a historic building`「歴史的建造物を保存する」のように、対象を直接目的語に取る。  "
          },
          {
            "line": 27,
            "text": "`conservationist` — 名詞「自然保護活動家、保全論者」。自然環境や資源の保護を支持・実践する人を指し、文化財保存の専門家を通常この語で呼ぶわけではない。  "
          },
          {
            "line": 28,
            "text": "`conservator` — 名詞「保存修復専門家、保全担当者」。特に美術品・文化財の調査、処置、予防的保存を行う専門家を指す。文脈によっては、資産や組織を管理・保全する人も指す。  "
          },
          {
            "line": 29,
            "text": "`conservancy` — 名詞「保全団体、保全区域、保全活動」。`a land conservancy`「土地保全団体」、`river conservancy`「河川保全活動」のように、組織や制度を指すことが多い。  "
          },
          {
            "line": 30,
            "text": "`conservational` — 形容詞「保全の、保存に関する」。一般会話では頻度が低く、専門的・制度的な文脈で使う。  "
          },
          {
            "line": 31,
            "text": "`conserved quantity` — 物理学で「保存量」。系の条件のもとで総量が一定に保たれる物理量を指す。  "
          }
        ],
        "sense_structure": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 44,
            "text": "【日本語訳・定義】水、エネルギー、森林、野生生物などの自然資源や環境を、浪費、枯渇、破壊から守るために、計画的・慎重に利用し管理すること。利用を一切禁止することではなく、将来も利用できる状態を保つことに重点がある。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 144,
            "text": "【日本語訳・定義】絵画、彫刻、文書、遺跡、歴史的建造物などの文化遺産を、劣化や損傷から守り、その材料、情報、価値を将来へ引き継ぐ専門的な実践・工程。調査、記録、処置、予防的な環境管理を含み、常に元の外観へ作り直すことを意味しない。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 243,
            "text": "【日本語訳・定義】ある系と条件のもとで、エネルギー、運動量、質量、電荷などの物理量の総量が、移動したり別の形に変換されたりしても一定に保たれること。また、その関係を述べる法則。系の一部の量や形が変化しないという意味ではなく、境界を定めた全体の収支が変わらないという意味である。  "
          }
        ],
        "frequency_register": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 46,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 48,
            "text": "【レジスター/領域】標準語。環境政策、資源管理、科学教育、行政、報道、日常の節電・節水の説明で広く使う。対象が自然環境ではなく、文化財や美術品なら通常は語義2、物理量の総量なら語義3である。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 146,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 148,
            "text": "【レジスター/領域】専門語・標準語。美術館、文書館、図書館、文化財行政、建築保存、博物館学で使う。米国英語では `art conservation`、`heritage conservation`、`architectural conservation` などの形が多い。自然環境の保全なら語義1である。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 245,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 247,
            "text": "【レジスター/領域】専門語。物理学、化学、工学、科学教育で使う。`conservation of energy` や `conservation of momentum` のように保存される量を明示することが多い。日常的な節電・節水を表す `energy conservation` とは、周囲の語で区別する。  "
          }
        ],
        "usage_notes": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 84,
            "text": "【語法・注意】この語義では通常不可算で、`a conservation` とは言わず、`conservation of water`、`conservation efforts` のように使う。`conservation` は「使わないこと」だけでなく、使用量を管理し、損失や破壊を防ぐことを含む。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 184,
            "text": "【語法・注意】この語義の `conservation` は通常不可算で、専門家が対象を記録・安定化・処置しながら残すことを指す。`conservation` と `restoration` は重なるが、`restoration` は過去の状態や外観を再現することに焦点が置かれやすい。保存修復では、後から加えた部分を隠さず、現存する材料と将来の研究可能性を尊重する場合がある。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 278,
            "text": "【語法・注意】物理学の `conservation` は「何も変化しない」という意味ではない。エネルギーが熱や運動エネルギーへ移る、運動量が複数の物体へ分配されるなど、系の内部では形や配分が変わっても、定義した系全体の総量が一定なら保存という。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 52,
            "text": "【コロケーション】"
          },
          {
            "line": 54,
            "text": "・`conservation of 〈natural resource〉`  "
          },
          {
            "line": 55,
            "text": "用途: 水、森林、土壌などの自然資源を、使い切ったり損なったりしないよう管理することを表す。  "
          },
          {
            "line": 56,
            "text": "例: The region introduced strict conservation of groundwater after several dry years.  "
          },
          {
            "line": 57,
            "text": "訳: その地域は数年続いた干ばつの後、地下水の厳格な保全を導入した。  "
          },
          {
            "line": 59,
            "text": "・`wildlife conservation`  "
          },
          {
            "line": 60,
            "text": "用途: 野生動物、その生息地、個体群を保護・管理する活動を表す。  "
          },
          {
            "line": 61,
            "text": "例: Wildlife conservation depends on protecting habitats as well as individual animals.  "
          },
          {
            "line": 62,
            "text": "訳: 野生生物の保全には、個々の動物だけでなく生息地を守ることも必要である。  "
          },
          {
            "line": 64,
            "text": "・`energy conservation`  "
          },
          {
            "line": 65,
            "text": "用途: エネルギーの使用量や浪費を減らし、限られた資源を効率よく使うことを表す。  "
          },
          {
            "line": 66,
            "text": "例: The school installed motion sensors as part of its energy conservation program.  "
          },
          {
            "line": 67,
            "text": "訳: その学校は省エネルギー計画の一環として人感センサーを設置した。  "
          },
          {
            "line": 69,
            "text": "・`water conservation`  "
          },
          {
            "line": 70,
            "text": "用途: 水の使用を抑え、供給源を将来の需要のために維持することを表す。  "
          },
          {
            "line": 71,
            "text": "例: Rain barrels were provided to residents as a water conservation measure.  "
          },
          {
            "line": 72,
            "text": "訳: 節水対策として、住民に雨水貯留タンクが配られた。  "
          },
          {
            "line": 74,
            "text": "・`conservation efforts/measures`  "
          },
          {
            "line": 75,
            "text": "用途: 自然環境や資源を守るための具体的な努力・政策・対策をまとめて表す。  "
          },
          {
            "line": 76,
            "text": "例: The new conservation measures reduced logging in the protected forest.  "
          },
          {
            "line": 77,
            "text": "訳: 新しい保全対策によって、保護林での伐採が減った。  "
          },
          {
            "line": 79,
            "text": "・`marine conservation`  "
          },
          {
            "line": 80,
            "text": "用途: 海洋の生態系、魚類、沿岸環境を保護・管理する活動を表す。  "
          },
          {
            "line": 81,
            "text": "例: The research station funds marine conservation around the coral reef.  "
          },
          {
            "line": 82,
            "text": "訳: その研究所はサンゴ礁周辺の海洋保全に資金を提供している。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 152,
            "text": "【コロケーション】"
          },
          {
            "line": 154,
            "text": "・`conservation of 〈artwork〉`  "
          },
          {
            "line": 155,
            "text": "用途: 絵画、彫刻、工芸品などを調査・処置して安定した状態に保つことを表す。  "
          },
          {
            "line": 156,
            "text": "例: The conservation of the oil painting took six months because the canvas was fragile.  "
          },
          {
            "line": 157,
            "text": "訳: その油彩画はキャンバスがもろかったため、保存修復に6か月かかった。  "
          },
          {
            "line": 159,
            "text": "・`art/heritage conservation`  "
          },
          {
            "line": 160,
            "text": "用途: 美術作品や文化遺産を対象とする専門分野・活動を表す。  "
          },
          {
            "line": 161,
            "text": "例: She studied heritage conservation before joining the national museum.  "
          },
          {
            "line": 162,
            "text": "訳: 彼女は国立博物館に入る前に文化遺産保存を学んだ。  "
          },
          {
            "line": 164,
            "text": "・`conservation treatment`  "
          },
          {
            "line": 165,
            "text": "用途: 専門家が作品や資料に施す具体的な保存修復処置を表す。  "
          },
          {
            "line": 166,
            "text": "例: The conservator recommended a gentle conservation treatment for the cracked varnish.  "
          },
          {
            "line": 167,
            "text": "訳: 保存修復家は、ひびの入ったニスに穏やかな保存修復処置を勧めた。  "
          },
          {
            "line": 169,
            "text": "・`conservation work`  "
          },
          {
            "line": 170,
            "text": "用途: 文化財の安定化、清掃、補修、記録などの保存修復作業をまとめて表す。  "
          },
          {
            "line": 171,
            "text": "例: Conservation work on the medieval manuscript revealed ink beneath a later repair.  "
          },
          {
            "line": 172,
            "text": "訳: その中世写本の保存修復作業によって、後世の補修の下にあるインクが明らかになった。  "
          },
          {
            "line": 174,
            "text": "・`conservation of historic buildings`  "
          },
          {
            "line": 175,
            "text": "用途: 歴史的建造物の材料、構造、特徴を調べ、損傷を抑えて維持することを表す。  "
          },
          {
            "line": 176,
            "text": "例: The conservation of historic buildings must respect evidence of their earlier alterations.  "
          },
          {
            "line": 177,
            "text": "訳: 歴史的建造物の保存では、過去の改変の証拠を尊重しなければならない。  "
          },
          {
            "line": 179,
            "text": "・`a conservation laboratory`  "
          },
          {
            "line": 180,
            "text": "用途: 美術品・文化財の材料分析、状態確認、処置を行う施設を表す。  "
          },
          {
            "line": 181,
            "text": "例: The museum’s conservation laboratory monitors humidity around the wooden sculpture.  "
          },
          {
            "line": 182,
            "text": "訳: その博物館の保存修復研究室は、木彫像の周囲の湿度を監視している。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 251,
            "text": "【コロケーション】"
          },
          {
            "line": 253,
            "text": "・`the law of conservation of energy`  "
          },
          {
            "line": 254,
            "text": "用途: 孤立した系の全エネルギーが、形を変えても一定であるという法則を表す。  "
          },
          {
            "line": 255,
            "text": "例: The law of conservation of energy explains why the total energy of the isolated system stayed constant.  "
          },
          {
            "line": 256,
            "text": "訳: エネルギー保存則は、その孤立系の全エネルギーが一定に保たれた理由を説明する。  "
          },
          {
            "line": 258,
            "text": "・`conservation of momentum`  "
          },
          {
            "line": 259,
            "text": "用途: 外部からの正味の力積が無視できる系で、全運動量が衝突の前後で等しいことを表す。  "
          },
          {
            "line": 260,
            "text": "例: The students used conservation of momentum to calculate the speeds after the collision.  "
          },
          {
            "line": 261,
            "text": "訳: 学生たちは運動量保存を使って、衝突後の速度を計算した。  "
          },
          {
            "line": 263,
            "text": "・`conservation of mass`  "
          },
          {
            "line": 264,
            "text": "用途: 通常の化学反応で原子が消滅・生成せず、反応前後の質量収支が保たれることを表す。  "
          },
          {
            "line": 265,
            "text": "例: The balanced equation reflects conservation of mass: the atoms are rearranged, not created or destroyed.  "
          },
          {
            "line": 266,
            "text": "訳: 係数をそろえた化学式は質量保存を反映している。原子は組み替えられるのであって、生成・消滅するのではない。  "
          },
          {
            "line": 268,
            "text": "・`conservation of charge`  "
          },
          {
            "line": 269,
            "text": "用途: 閉じた収支で電荷が勝手に生じたり消えたりせず、電気回路や反応で電荷の総量が保たれることを表す。  "
          },
          {
            "line": 270,
            "text": "例: Kirchhoff’s current law follows from conservation of electric charge at a circuit junction.  "
          },
          {
            "line": 271,
            "text": "訳: キルヒホッフの電流則は、回路の接点で電気の電荷が保存されることから導かれる。  "
          },
          {
            "line": 273,
            "text": "・`a conservation law`  "
          },
          {
            "line": 274,
            "text": "用途: 特定の物理量の総量が、許された変化の前後で一定であることを述べる法則を表す。  "
          },
          {
            "line": 275,
            "text": "例: A simulation is suspect if it changes total charge without an external source, because it violates a conservation law.  "
          },
          {
            "line": 276,
            "text": "訳: 外部源なしに全電荷を変えるシミュレーションは、保存則に反するため疑わしい。  "
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
    },
    {
      "schema_version": "check_pass_request_v6",
      "pass_id": "pronunciation",
      "taxonomy_ids": [
        "pronunciation_symbol_explanation"
      ],
      "specification": "prompts/check_pass_pronunciation_v6.md",
      "input_body_sha256": "20ff4e261a57880a6d1394ca4bc4aab61f39016aa205908b40e8d9d4cd222e08",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "米: /ˌkɑːnsərˈveɪʃən/、英: /ˌkɒnsəˈveɪʃən/。4音節で、主強勢は第3音節の `-va-` /veɪ/、第1音節に弱い副強勢がある。語末の `-tion` は /ʃən/ と発音する。  "
          },
          {
            "line": 16,
            "text": "`conservation` の `-serva-` と `conversation` の `-versa-` は、つづり上 `s` と `v` の位置が入れ替わっている。音も異なり、前者の該当部分は /sərˈveɪ/、後者の該当部分は米音で /vərˈseɪ/ と発音する（全体ではそれぞれ /ˌkɑːnsərˈveɪʃən/、/ˌkɑːnvərˈseɪʃən/）。  "
          },
          {
            "line": 17,
            "text": "`conservationist` は /ˌkɑːnsərˈveɪʃənɪst/（米）で、基本的に `conservation` と同じ主強勢を保つ。  "
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
    },
    {
      "schema_version": "check_pass_request_v6",
      "pass_id": "evidence",
      "taxonomy_ids": [
        "evidence_claim_mismatch"
      ],
      "specification": "prompts/check_pass_evidence_v6.md",
      "input_body_sha256": "20ff4e261a57880a6d1394ca4bc4aab61f39016aa205908b40e8d9d4cd222e08",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "米: /ˌkɑːnsərˈveɪʃən/、英: /ˌkɒnsəˈveɪʃən/。4音節で、主強勢は第3音節の `-va-` /veɪ/、第1音節に弱い副強勢がある。語末の `-tion` は /ʃən/ と発音する。  "
          },
          {
            "line": 16,
            "text": "`conservation` の `-serva-` と `conversation` の `-versa-` は、つづり上 `s` と `v` の位置が入れ替わっている。音も異なり、前者の該当部分は /sərˈveɪ/、後者の該当部分は米音で /vərˈseɪ/ と発音する（全体ではそれぞれ /ˌkɑːnsərˈveɪʃən/、/ˌkɑːnvərˈseɪʃən/）。  "
          },
          {
            "line": 17,
            "text": "`conservationist` は /ˌkɑːnsərˈveɪʃənɪst/（米）で、基本的に `conservation` と同じ主強勢を保つ。  "
          }
        ],
        "etymology": [
          {
            "line": 19,
            "text": "＃語源"
          },
          {
            "line": 21,
            "text": "`conservation` は中英語 `conservacioun`、古フランス語 `conservation` を経て、ラテン語 `conservatio`「保存、保全」に由来する。ラテン語 `conservare`「保つ、損なわないようにする」にさかのぼり、英語では「失われたり損なわれたりしないように保つこと」を中心に意味を発達させた。  "
          },
          {
            "line": 22,
            "text": "現代英語では、自然資源を使いながら将来の損失を防ぐ保全、文化財の材料と価値を守る専門的保存、変化の前後で物理量の総量を保つ保存則へと用法が分かれる。物理学の用法は、日常的な「節約」から直接導かれたというより、「総量を失わせず保つ」という共通の概念を技術用語として用いるものである。  "
          }
        ],
        "word_formation": [
          {
            "line": 24,
            "text": "＃語形成"
          },
          {
            "line": 26,
            "text": "`conserve` — 動詞「保全する、節約する、保存する」。`conserve water`「水を節約する」、`conserve a historic building`「歴史的建造物を保存する」のように、対象を直接目的語に取る。  "
          },
          {
            "line": 27,
            "text": "`conservationist` — 名詞「自然保護活動家、保全論者」。自然環境や資源の保護を支持・実践する人を指し、文化財保存の専門家を通常この語で呼ぶわけではない。  "
          },
          {
            "line": 28,
            "text": "`conservator` — 名詞「保存修復専門家、保全担当者」。特に美術品・文化財の調査、処置、予防的保存を行う専門家を指す。文脈によっては、資産や組織を管理・保全する人も指す。  "
          },
          {
            "line": 29,
            "text": "`conservancy` — 名詞「保全団体、保全区域、保全活動」。`a land conservancy`「土地保全団体」、`river conservancy`「河川保全活動」のように、組織や制度を指すことが多い。  "
          },
          {
            "line": 30,
            "text": "`conservational` — 形容詞「保全の、保存に関する」。一般会話では頻度が低く、専門的・制度的な文脈で使う。  "
          },
          {
            "line": 31,
            "text": "`conserved quantity` — 物理学で「保存量」。系の条件のもとで総量が一定に保たれる物理量を指す。  "
          }
        ],
        "core_image": [
          {
            "line": 33,
            "text": "＃コアイメージ"
          },
          {
            "line": 35,
            "text": "`conservation` の核は、資源・物・価値・総量などを、損失や望ましくない変化から守って保つことである。何を保つかによって、環境・文化財の実践的な「保全」と、物理学の「総量が変わらない」という専門用法に分かれる。  "
          },
          {
            "line": 36,
            "text": "・自然資源や環境を使い尽くしたり損なったりしないように保つ → 「保全、環境保護、節約」（語義1）  "
          },
          {
            "line": 37,
            "text": "・作品や文化財の材料・情報・価値を損なわずに将来へ保つ → 「保存、保全、保存修復」（語義2）  "
          },
          {
            "line": 38,
            "text": "・系の物理量の総量を変化や変換の前後で保つ → 「保存則、保存」（語義3）  "
          }
        ],
        "sense_structure": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 44,
            "text": "【日本語訳・定義】水、エネルギー、森林、野生生物などの自然資源や環境を、浪費、枯渇、破壊から守るために、計画的・慎重に利用し管理すること。利用を一切禁止することではなく、将来も利用できる状態を保つことに重点がある。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 144,
            "text": "【日本語訳・定義】絵画、彫刻、文書、遺跡、歴史的建造物などの文化遺産を、劣化や損傷から守り、その材料、情報、価値を将来へ引き継ぐ専門的な実践・工程。調査、記録、処置、予防的な環境管理を含み、常に元の外観へ作り直すことを意味しない。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 243,
            "text": "【日本語訳・定義】ある系と条件のもとで、エネルギー、運動量、質量、電荷などの物理量の総量が、移動したり別の形に変換されたりしても一定に保たれること。また、その関係を述べる法則。系の一部の量や形が変化しないという意味ではなく、境界を定めた全体の収支が変わらないという意味である。  "
          }
        ],
        "frequency_register": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 46,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 48,
            "text": "【レジスター/領域】標準語。環境政策、資源管理、科学教育、行政、報道、日常の節電・節水の説明で広く使う。対象が自然環境ではなく、文化財や美術品なら通常は語義2、物理量の総量なら語義3である。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 146,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 148,
            "text": "【レジスター/領域】専門語・標準語。美術館、文書館、図書館、文化財行政、建築保存、博物館学で使う。米国英語では `art conservation`、`heritage conservation`、`architectural conservation` などの形が多い。自然環境の保全なら語義1である。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 245,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 247,
            "text": "【レジスター/領域】専門語。物理学、化学、工学、科学教育で使う。`conservation of energy` や `conservation of momentum` のように保存される量を明示することが多い。日常的な節電・節水を表す `energy conservation` とは、周囲の語で区別する。  "
          }
        ],
        "frames": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 50,
            "text": "【文法パターン】`conservation of 〈natural resource〉`＝～の保全／`wildlife/forest/marine conservation`＝野生生物・森林・海洋の保全／`energy/water conservation`＝省エネルギー・節水／`conservation efforts/measures`＝保全の取り組み・対策／`promote/support conservation`＝保全を促進・支援する  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 150,
            "text": "【文法パターン】`conservation of 〈artwork/manuscript/building〉`＝～の保存修復／`art/heritage conservation`＝美術品・文化遺産の保存／`conservation treatment`＝保存修復処置／`conservation work`＝保存修復作業／`a conservation laboratory`＝保存修復研究室／`conservation and restoration`＝保存修復と復元  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 249,
            "text": "【文法パターン】`conservation of 〈energy/momentum/mass/charge〉`＝エネルギー・運動量・質量・電荷の保存／`the law/principle of conservation of 〈quantity〉`＝～保存の法則・原理／`a conservation law`＝保存則／`obey/test conservation of 〈quantity〉`＝～の保存則に従う・～の保存を検証する  "
          }
        ],
        "collocations_examples": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 52,
            "text": "【コロケーション】"
          },
          {
            "line": 54,
            "text": "・`conservation of 〈natural resource〉`  "
          },
          {
            "line": 55,
            "text": "用途: 水、森林、土壌などの自然資源を、使い切ったり損なったりしないよう管理することを表す。  "
          },
          {
            "line": 56,
            "text": "例: The region introduced strict conservation of groundwater after several dry years.  "
          },
          {
            "line": 57,
            "text": "訳: その地域は数年続いた干ばつの後、地下水の厳格な保全を導入した。  "
          },
          {
            "line": 59,
            "text": "・`wildlife conservation`  "
          },
          {
            "line": 60,
            "text": "用途: 野生動物、その生息地、個体群を保護・管理する活動を表す。  "
          },
          {
            "line": 61,
            "text": "例: Wildlife conservation depends on protecting habitats as well as individual animals.  "
          },
          {
            "line": 62,
            "text": "訳: 野生生物の保全には、個々の動物だけでなく生息地を守ることも必要である。  "
          },
          {
            "line": 64,
            "text": "・`energy conservation`  "
          },
          {
            "line": 65,
            "text": "用途: エネルギーの使用量や浪費を減らし、限られた資源を効率よく使うことを表す。  "
          },
          {
            "line": 66,
            "text": "例: The school installed motion sensors as part of its energy conservation program.  "
          },
          {
            "line": 67,
            "text": "訳: その学校は省エネルギー計画の一環として人感センサーを設置した。  "
          },
          {
            "line": 69,
            "text": "・`water conservation`  "
          },
          {
            "line": 70,
            "text": "用途: 水の使用を抑え、供給源を将来の需要のために維持することを表す。  "
          },
          {
            "line": 71,
            "text": "例: Rain barrels were provided to residents as a water conservation measure.  "
          },
          {
            "line": 72,
            "text": "訳: 節水対策として、住民に雨水貯留タンクが配られた。  "
          },
          {
            "line": 74,
            "text": "・`conservation efforts/measures`  "
          },
          {
            "line": 75,
            "text": "用途: 自然環境や資源を守るための具体的な努力・政策・対策をまとめて表す。  "
          },
          {
            "line": 76,
            "text": "例: The new conservation measures reduced logging in the protected forest.  "
          },
          {
            "line": 77,
            "text": "訳: 新しい保全対策によって、保護林での伐採が減った。  "
          },
          {
            "line": 79,
            "text": "・`marine conservation`  "
          },
          {
            "line": 80,
            "text": "用途: 海洋の生態系、魚類、沿岸環境を保護・管理する活動を表す。  "
          },
          {
            "line": 81,
            "text": "例: The research station funds marine conservation around the coral reef.  "
          },
          {
            "line": 82,
            "text": "訳: その研究所はサンゴ礁周辺の海洋保全に資金を提供している。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 152,
            "text": "【コロケーション】"
          },
          {
            "line": 154,
            "text": "・`conservation of 〈artwork〉`  "
          },
          {
            "line": 155,
            "text": "用途: 絵画、彫刻、工芸品などを調査・処置して安定した状態に保つことを表す。  "
          },
          {
            "line": 156,
            "text": "例: The conservation of the oil painting took six months because the canvas was fragile.  "
          },
          {
            "line": 157,
            "text": "訳: その油彩画はキャンバスがもろかったため、保存修復に6か月かかった。  "
          },
          {
            "line": 159,
            "text": "・`art/heritage conservation`  "
          },
          {
            "line": 160,
            "text": "用途: 美術作品や文化遺産を対象とする専門分野・活動を表す。  "
          },
          {
            "line": 161,
            "text": "例: She studied heritage conservation before joining the national museum.  "
          },
          {
            "line": 162,
            "text": "訳: 彼女は国立博物館に入る前に文化遺産保存を学んだ。  "
          },
          {
            "line": 164,
            "text": "・`conservation treatment`  "
          },
          {
            "line": 165,
            "text": "用途: 専門家が作品や資料に施す具体的な保存修復処置を表す。  "
          },
          {
            "line": 166,
            "text": "例: The conservator recommended a gentle conservation treatment for the cracked varnish.  "
          },
          {
            "line": 167,
            "text": "訳: 保存修復家は、ひびの入ったニスに穏やかな保存修復処置を勧めた。  "
          },
          {
            "line": 169,
            "text": "・`conservation work`  "
          },
          {
            "line": 170,
            "text": "用途: 文化財の安定化、清掃、補修、記録などの保存修復作業をまとめて表す。  "
          },
          {
            "line": 171,
            "text": "例: Conservation work on the medieval manuscript revealed ink beneath a later repair.  "
          },
          {
            "line": 172,
            "text": "訳: その中世写本の保存修復作業によって、後世の補修の下にあるインクが明らかになった。  "
          },
          {
            "line": 174,
            "text": "・`conservation of historic buildings`  "
          },
          {
            "line": 175,
            "text": "用途: 歴史的建造物の材料、構造、特徴を調べ、損傷を抑えて維持することを表す。  "
          },
          {
            "line": 176,
            "text": "例: The conservation of historic buildings must respect evidence of their earlier alterations.  "
          },
          {
            "line": 177,
            "text": "訳: 歴史的建造物の保存では、過去の改変の証拠を尊重しなければならない。  "
          },
          {
            "line": 179,
            "text": "・`a conservation laboratory`  "
          },
          {
            "line": 180,
            "text": "用途: 美術品・文化財の材料分析、状態確認、処置を行う施設を表す。  "
          },
          {
            "line": 181,
            "text": "例: The museum’s conservation laboratory monitors humidity around the wooden sculpture.  "
          },
          {
            "line": 182,
            "text": "訳: その博物館の保存修復研究室は、木彫像の周囲の湿度を監視している。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 251,
            "text": "【コロケーション】"
          },
          {
            "line": 253,
            "text": "・`the law of conservation of energy`  "
          },
          {
            "line": 254,
            "text": "用途: 孤立した系の全エネルギーが、形を変えても一定であるという法則を表す。  "
          },
          {
            "line": 255,
            "text": "例: The law of conservation of energy explains why the total energy of the isolated system stayed constant.  "
          },
          {
            "line": 256,
            "text": "訳: エネルギー保存則は、その孤立系の全エネルギーが一定に保たれた理由を説明する。  "
          },
          {
            "line": 258,
            "text": "・`conservation of momentum`  "
          },
          {
            "line": 259,
            "text": "用途: 外部からの正味の力積が無視できる系で、全運動量が衝突の前後で等しいことを表す。  "
          },
          {
            "line": 260,
            "text": "例: The students used conservation of momentum to calculate the speeds after the collision.  "
          },
          {
            "line": 261,
            "text": "訳: 学生たちは運動量保存を使って、衝突後の速度を計算した。  "
          },
          {
            "line": 263,
            "text": "・`conservation of mass`  "
          },
          {
            "line": 264,
            "text": "用途: 通常の化学反応で原子が消滅・生成せず、反応前後の質量収支が保たれることを表す。  "
          },
          {
            "line": 265,
            "text": "例: The balanced equation reflects conservation of mass: the atoms are rearranged, not created or destroyed.  "
          },
          {
            "line": 266,
            "text": "訳: 係数をそろえた化学式は質量保存を反映している。原子は組み替えられるのであって、生成・消滅するのではない。  "
          },
          {
            "line": 268,
            "text": "・`conservation of charge`  "
          },
          {
            "line": 269,
            "text": "用途: 閉じた収支で電荷が勝手に生じたり消えたりせず、電気回路や反応で電荷の総量が保たれることを表す。  "
          },
          {
            "line": 270,
            "text": "例: Kirchhoff’s current law follows from conservation of electric charge at a circuit junction.  "
          },
          {
            "line": 271,
            "text": "訳: キルヒホッフの電流則は、回路の接点で電気の電荷が保存されることから導かれる。  "
          },
          {
            "line": 273,
            "text": "・`a conservation law`  "
          },
          {
            "line": 274,
            "text": "用途: 特定の物理量の総量が、許された変化の前後で一定であることを述べる法則を表す。  "
          },
          {
            "line": 275,
            "text": "例: A simulation is suspect if it changes total charge without an external source, because it violates a conservation law.  "
          },
          {
            "line": 276,
            "text": "訳: 外部源なしに全電荷を変えるシミュレーションは、保存則に反するため疑わしい。  "
          }
        ],
        "usage_notes": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 84,
            "text": "【語法・注意】この語義では通常不可算で、`a conservation` とは言わず、`conservation of water`、`conservation efforts` のように使う。`conservation` は「使わないこと」だけでなく、使用量を管理し、損失や破壊を防ぐことを含む。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 184,
            "text": "【語法・注意】この語義の `conservation` は通常不可算で、専門家が対象を記録・安定化・処置しながら残すことを指す。`conservation` と `restoration` は重なるが、`restoration` は過去の状態や外観を再現することに焦点が置かれやすい。保存修復では、後から加えた部分を隠さず、現存する材料と将来の研究可能性を尊重する場合がある。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 278,
            "text": "【語法・注意】物理学の `conservation` は「何も変化しない」という意味ではない。エネルギーが熱や運動エネルギーへ移る、運動量が複数の物体へ分配されるなど、系の内部では形や配分が変わっても、定義した系全体の総量が一定なら保存という。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 42,
            "text": "1. 【名詞・不可算】自然資源・環境の保全、環境保護、資源の節約"
          },
          {
            "line": 89,
            "text": "【類義語】"
          },
          {
            "line": 91,
            "text": "・preservation  "
          },
          {
            "line": 92,
            "text": "定義: 損傷、変化、消失から守り、元の状態に近いまま残すこと。  "
          },
          {
            "line": 93,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 94,
            "text": "違い: `preservation` は変化を避けて現状を保つ焦点が強い。`conservation` は、自然資源を管理しながら使うことや、文化財を処置して安定させることも含む。  "
          },
          {
            "line": 95,
            "text": "例: The preservation of the wetland prevents developers from draining it.  "
          },
          {
            "line": 96,
            "text": "訳: その湿地の保存・保全は、開発業者が排水してしまうのを防ぐ。  "
          },
          {
            "line": 98,
            "text": "・protection  "
          },
          {
            "line": 99,
            "text": "定義: 危険、損害、攻撃などから守ること。  "
          },
          {
            "line": 100,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 101,
            "text": "違い: `protection` は脅威から守るという広い語で、資源を計画的に利用し続ける管理や、総量を保つ技術概念までは必ずしも含まない。  "
          },
          {
            "line": 102,
            "text": "例: The law provides protection for nesting birds during the breeding season.  "
          },
          {
            "line": 103,
            "text": "訳: その法律は繁殖期の営巣する鳥を保護する。  "
          },
          {
            "line": 105,
            "text": "・stewardship  "
          },
          {
            "line": 106,
            "text": "定義: 預かった土地、資源、環境を責任を持って管理すること。  "
          },
          {
            "line": 107,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 108,
            "text": "違い: `stewardship` は管理者の責任や倫理を強調する。`conservation` はその責任から行う具体的な保全活動や政策を指しやすい。  "
          },
          {
            "line": 109,
            "text": "例: Good stewardship of the forest requires both careful harvesting and replanting.  "
          },
          {
            "line": 110,
            "text": "訳: 森林を適切に管理するには、慎重な伐採と再植林の両方が必要である。  "
          },
          {
            "line": 112,
            "text": "・sustainable management  "
          },
          {
            "line": 113,
            "text": "定義: 将来の利用可能性を損なわないよう、資源や活動を管理すること。  "
          },
          {
            "line": 114,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 115,
            "text": "違い: `sustainable management` は将来も成り立つ利用水準や仕組みを明示する複合表現である。`conservation` は保護・損失防止に重点があり、持続可能性全体を必ずしも論じない。  "
          },
          {
            "line": 116,
            "text": "例: Sustainable management of the fishery limits the annual catch.  "
          },
          {
            "line": 117,
            "text": "訳: その漁業の持続可能な管理は年間漁獲量を制限している。  "
          },
          {
            "line": 119,
            "text": "【反意語】"
          },
          {
            "line": 121,
            "text": "・exploitation  "
          },
          {
            "line": 122,
            "text": "定義: 資源や環境を利益のために強く利用し、しばしば限界まで消費すること。  "
          },
          {
            "line": 123,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 124,
            "text": "違い: `exploitation` は利用そのものを指すが、過剰利用や搾取という否定的な含みを持ちやすい。`conservation` は長期的な損失を避ける管理に焦点がある。  "
          },
          {
            "line": 125,
            "text": "例: Uncontrolled exploitation of the forest has reduced the river’s water quality.  "
          },
          {
            "line": 126,
            "text": "訳: 森林の無制限な開発・利用によって、その川の水質が低下した。  "
          },
          {
            "line": 128,
            "text": "・depletion  "
          },
          {
            "line": 129,
            "text": "定義: 資源や蓄えが使われて減少し、ほとんど残らなくなること。  "
          },
          {
            "line": 130,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 131,
            "text": "違い: `depletion` は保全に失敗した結果としての量の減少を表す。故意の利用だけでなく、自然な消耗にも使える。  "
          },
          {
            "line": 132,
            "text": "例: The depletion of the aquifer forced farmers to reduce irrigation.  "
          },
          {
            "line": 133,
            "text": "訳: 帯水層の枯渇によって、農家は灌漑を減らさざるを得なかった。  "
          },
          {
            "line": 135,
            "text": "・waste  "
          },
          {
            "line": 136,
            "text": "定義: 役立つ資源を不注意に、または必要以上に使うこと。  "
          },
          {
            "line": 137,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 138,
            "text": "違い: `waste` は個々の行動や使用の浪費を指す日常語で、自然環境全体の計画的な管理を表す `conservation` より狭い。  "
          },
          {
            "line": 139,
            "text": "例: Leaving the tap running is an unnecessary waste of water.  "
          },
          {
            "line": 140,
            "text": "訳: 蛇口を出しっぱなしにするのは、水の不必要な浪費である。  "
          },
          {
            "line": 142,
            "text": "2. 【名詞・不可算】美術品・文化財・歴史的建造物の保存、保全、保存修復"
          },
          {
            "line": 188,
            "text": "【類義語】"
          },
          {
            "line": 190,
            "text": "・preservation  "
          },
          {
            "line": 191,
            "text": "定義: 文化財や記録を損傷・劣化から守り、できるだけその状態で残すこと。  "
          },
          {
            "line": 192,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 193,
            "text": "違い: `preservation` は現状を保つ一般語で、専門的な調査・処置の体系まで必ずしも示さない。`conservation` は材料分析、処置、予防管理を含む専門領域を指しやすい。  "
          },
          {
            "line": 194,
            "text": "例: Digital preservation protects the files from becoming unreadable as software changes.  "
          },
          {
            "line": 195,
            "text": "訳: デジタル保存は、ソフトウェアの変化でファイルが読めなくなるのを防ぐ。  "
          },
          {
            "line": 197,
            "text": "・restoration  "
          },
          {
            "line": 198,
            "text": "定義: 作品、建物、物品などを以前の状態・外観に戻すこと。  "
          },
          {
            "line": 199,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 200,
            "text": "違い: `restoration` は欠損の補充や過去の姿の再現に重点がある。`conservation` は現存する材料を安定させることを優先し、完全な復元を目標にしないことがある。  "
          },
          {
            "line": 201,
            "text": "例: The restoration recreated the missing colors, while the conservation treatment stabilized the original paint.  "
          },
          {
            "line": 202,
            "text": "訳: 復元では失われた色を再現し、保存修復処置では元の絵具を安定させた。  "
          },
          {
            "line": 204,
            "text": "・stabilization  "
          },
          {
            "line": 205,
            "text": "定義: 損傷や劣化の進行を止め、対象を安全に扱える状態にすること。  "
          },
          {
            "line": 206,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 207,
            "text": "違い: `stabilization` は保存修復の一工程に焦点を置く。`conservation` は状態確認、記録、予防管理、処置を含むより広い活動である。  "
          },
          {
            "line": 208,
            "text": "例: Stabilization of the loose pages came before the manuscript was put on display.  "
          },
          {
            "line": 209,
            "text": "訳: 写本を展示する前に、外れかけたページの安定化が行われた。  "
          },
          {
            "line": 211,
            "text": "・repair  "
          },
          {
            "line": 212,
            "text": "定義: 壊れたり傷んだりした物を、使える状態に戻すため直すこと。  "
          },
          {
            "line": 213,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 214,
            "text": "違い: `repair` は機能回復の日常語で、元の材料・情報・外観を尊重する専門的な保存判断までは含まない。  "
          },
          {
            "line": 215,
            "text": "例: The repair fixed the frame, but it was not a full conservation treatment.  "
          },
          {
            "line": 216,
            "text": "訳: その修理で額縁は直ったが、完全な保存修復処置ではなかった。  "
          },
          {
            "line": 218,
            "text": "【反意語】"
          },
          {
            "line": 220,
            "text": "・neglect  "
          },
          {
            "line": 221,
            "text": "定義: 必要な世話、管理、処置を怠り、対象を悪化させること。  "
          },
          {
            "line": 222,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 223,
            "text": "違い: `neglect` は保全のために必要な注意や手入れをしないことを表す。故意に壊すことまで必ずしも含まない。  "
          },
          {
            "line": 224,
            "text": "例: Years of neglect left the wooden sculpture vulnerable to insects and moisture.  "
          },
          {
            "line": 225,
            "text": "訳: 何年も放置されたため、その木彫像は虫と湿気に弱い状態になった。  "
          },
          {
            "line": 227,
            "text": "・deterioration  "
          },
          {
            "line": 228,
            "text": "定義: 物の状態、品質、材料が時間とともに悪化すること。  "
          },
          {
            "line": 229,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 230,
            "text": "違い: `deterioration` は保存に失敗した結果として起こる劣化を指す状態名詞で、誰かの行為を直接示す `neglect` とは異なる。  "
          },
          {
            "line": 231,
            "text": "例: The archive reduced deterioration by controlling light and humidity.  "
          },
          {
            "line": 232,
            "text": "訳: その文書館は光と湿度を管理して劣化を抑えた。  "
          },
          {
            "line": 234,
            "text": "・destruction  "
          },
          {
            "line": 235,
            "text": "定義: 物、建物、資料などを壊して存在・形を失わせること。  "
          },
          {
            "line": 236,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 237,
            "text": "違い: `destruction` は保存の目的と正反対の結果を表すが、保存修復が防ごうとするすべての損傷が完全な破壊に至るわけではない。  "
          },
          {
            "line": 238,
            "text": "例: The conservation plan was created to prevent the destruction of the historic site.  "
          },
          {
            "line": 239,
            "text": "訳: その保存計画は、史跡の破壊を防ぐために作られた。  "
          },
          {
            "line": 241,
            "text": "3. 【名詞・不可算／物理学・化学】物理量の保存、保存則"
          },
          {
            "line": 283,
            "text": "【類義語】"
          },
          {
            "line": 285,
            "text": "・invariance  "
          },
          {
            "line": 286,
            "text": "定義: ある変換、操作、条件のもとで、性質や量が変わらないこと。  "
          },
          {
            "line": 287,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 288,
            "text": "違い: `invariance` は変換に対して同じであるという数学・物理学の性質を強調する。`conservation` は時間発展や相互作用の前後で総量が保たれる収支・法則を指しやすい。  "
          },
          {
            "line": 289,
            "text": "例: The symmetry implies invariance of the equations under a change of coordinates.  "
          },
          {
            "line": 290,
            "text": "訳: その対称性は、座標変換に対して方程式が不変であることを意味する。  "
          },
          {
            "line": 292,
            "text": "・constancy  "
          },
          {
            "line": 293,
            "text": "定義: 量や状態が変わらず一定であること。  "
          },
          {
            "line": 294,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 295,
            "text": "違い: `constancy` は単に変化がないことを表す一般語で、何が保存され、どの系で収支が保たれるかという物理法則の含みは弱い。  "
          },
          {
            "line": 296,
            "text": "例: The experiment measured the constancy of the temperature in the sealed chamber.  "
          },
          {
            "line": 297,
            "text": "訳: その実験は密閉室内の温度が一定であることを測定した。  "
          },
          {
            "line": 299,
            "text": "・preservation  "
          },
          {
            "line": 300,
            "text": "定義: ある性質、量、状態を失わせずに保つこと。  "
          },
          {
            "line": 301,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 302,
            "text": "違い: `preservation` は「保つ」という一般的な意味で技術文書にも現れるが、物理学では特定の量と法則を示す `conservation` が定着している。  "
          },
          {
            "line": 303,
            "text": "例: The model assumes preservation of total mass during the reaction.  "
          },
          {
            "line": 304,
            "text": "訳: そのモデルは反応中に全質量が保たれると仮定している。  "
          },
          {
            "line": 306,
            "text": "【反意語】"
          },
          {
            "line": 308,
            "text": "・nonconservation  "
          },
          {
            "line": 309,
            "text": "定義: 保存されるはずの量が、定めた系や理論のもとで一定に保たれないこと。  "
          },
          {
            "line": 310,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 311,
            "text": "違い: `nonconservation` は一般会話の反対語ではなく、特定の保存則が成り立たないことを述べる専門的な表現である。  "
          },
          {
            "line": 312,
            "text": "例: The proposed interaction would imply nonconservation of electric charge.  "
          },
          {
            "line": 313,
            "text": "訳: その相互作用の提案は、電荷非保存を意味することになる。  "
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
  ]
}
```
