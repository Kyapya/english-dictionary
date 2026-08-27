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
      "input_body_sha256": "ecdf6518adf955d45f677a4e2c5e7d9356b4725cf87db77db64fbf1e69380614",
      "input_sections": {
        "definitions": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 49,
            "text": "【日本語訳・定義】事物や状況が、誰か・何かにとって対処を要する危険、リスク、問題、困難などを生じさせること。主語が意図的に脅すとは限らず、客観的に「〜という危険をもたらす」「〜の障害となる」と述べる硬めの表現である。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 125,
            "text": "【日本語訳・定義】質問、問題、論点、仮説などを、他者が考えたり議論したりする対象として提示すること。単に発言するより、検討すべき論点を前に置く含みがあり、会議・論文・評論などで使われる。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 196,
            "text": "【日本語訳・定義】人や物を写真、絵画、彫刻、舞台上の構図などに適した姿勢・位置に置くこと。また、人がそのような姿勢を保って写真家や画家のためにポーズを取ること。自分がポーズを取る場合は自動詞、モデルなどに姿勢を取らせる場合は他動詞になる。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 272,
            "text": "【日本語訳・定義】人に良く見せたり、印象づけたりする目的で、自然ではない態度、服装、振る舞いを意識的に演じること。写真撮影のために姿勢を取る語義3と違い、ここでは「気取っている」という批判的な評価が含まれやすい。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 324,
            "text": "【日本語訳・定義】本当はそうではない人や立場であるかのように振る舞い、他人をだますこと。身分を隠して接近する場合や、資格・専門性を持つように見せる場合に使う。単なる遊びの演技にも使えるが、通常は欺きの含みがある。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 395,
            "text": "【日本語訳・定義】人が立つ・座る・体を構えるなどして保つ、特定の身体の姿勢。写真、絵画、彫刻、ダンス、演技、運動などのために意識して取る姿勢を指すことが多いが、写真以外の表現的な姿勢にも使う。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 471,
            "text": "【日本語訳・定義】本当の感情・性格・立場とは別に、他人に特定の印象を与えるために作った態度や人物像。実際にはそう思っていないのに、知的、勇敢、無関心、親切などであるかのように振る舞うことを批判的に表す。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 577,
            "text": "【日本語訳・定義】難しい質問や問題によって、人を困らせて答えに窮させること。現代の一般英語では `puzzle`、`baffle`、`perplex` のほうが普通で、この `pose` は辞書に残る低頻度・硬い用法として理解するとよい。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 57,
            "text": "【コロケーション】"
          },
          {
            "line": 59,
            "text": "・`pose a threat to 〈人・動物・環境〉`  "
          },
          {
            "line": 60,
            "text": "用途: 人、動物、環境などに危害を及ぼす可能性があることを表す。  "
          },
          {
            "line": 61,
            "text": "例: The invasive plant poses a serious threat to native species.  "
          },
          {
            "line": 62,
            "text": "訳: その外来植物は在来種に深刻な脅威をもたらしている。  "
          },
          {
            "line": 64,
            "text": "・`pose a risk to 〈health/safety〉`  "
          },
          {
            "line": 65,
            "text": "用途: 健康や安全に悪い結果が生じる可能性を、客観的・説明的に述べる。  "
          },
          {
            "line": 66,
            "text": "例: Long-term exposure to the chemical may pose a risk to workers' health.  "
          },
          {
            "line": 67,
            "text": "訳: その化学物質への長期的な曝露は、作業員の健康にリスクをもたらす可能性がある。  "
          },
          {
            "line": 69,
            "text": "・`pose a danger to 〈人・集団〉`  "
          },
          {
            "line": 70,
            "text": "用途: 具体的な人や集団に危険が及ぶことを表す。  "
          },
          {
            "line": 71,
            "text": "例: The damaged bridge could pose a danger to pedestrians.  "
          },
          {
            "line": 72,
            "text": "訳: 損傷した橋は歩行者に危険を及ぼすおそれがある。  "
          },
          {
            "line": 74,
            "text": "・`pose a problem for 〈person/system〉`  "
          },
          {
            "line": 75,
            "text": "用途: 事物や状況が、誰かや制度に解決すべき問題を生じさせることを表す。  "
          },
          {
            "line": 76,
            "text": "例: The sudden loss of data posed a serious problem for the research team.  "
          },
          {
            "line": 77,
            "text": "訳: 突然のデータ消失は研究チームに深刻な問題をもたらした。  "
          },
          {
            "line": 79,
            "text": "・`pose a challenge to 〈team/plan〉`  "
          },
          {
            "line": 80,
            "text": "用途: 目標達成や作業の進行を難しくする課題を生じさせることを表す。  "
          },
          {
            "line": 81,
            "text": "例: The steep terrain posed a major challenge to the rescue team.  "
          },
          {
            "line": 82,
            "text": "訳: 険しい地形は救助隊に大きな課題を突きつけた。  "
          },
          {
            "line": 84,
            "text": "・`the threat/risk posed by 〈cause〉`  "
          },
          {
            "line": 85,
            "text": "用途: ある原因がもたらす危険や問題を、名詞句の中で説明する。  "
          },
          {
            "line": 86,
            "text": "例: Officials assessed the risks posed by the overloaded electrical system.  "
          },
          {
            "line": 87,
            "text": "訳: 当局は過負荷状態の電気系統がもたらすリスクを評価した。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 133,
            "text": "【コロケーション】"
          },
          {
            "line": 135,
            "text": "・`pose a question to 〈person/group〉`  "
          },
          {
            "line": 136,
            "text": "用途: 相手に、考える価値のある質問を正式に投げかけることを表す。  "
          },
          {
            "line": 137,
            "text": "例: The moderator posed a question to the panel about the cost of reform.  "
          },
          {
            "line": 138,
            "text": "訳: 司会者は改革の費用についてパネリストたちに質問を投げかけた。  "
          },
          {
            "line": 140,
            "text": "・`pose the question of whether 〈節〉`  "
          },
          {
            "line": 141,
            "text": "用途: 「〜かどうか」という論点を、検討すべき問題として提示する。  "
          },
          {
            "line": 142,
            "text": "例: The discovery poses the question of whether the species can survive in warmer seas.  "
          },
          {
            "line": 143,
            "text": "訳: その発見は、その種がより温暖な海で生き残れるのかという問題を提起する。  "
          },
          {
            "line": 145,
            "text": "・`pose a difficult question`  "
          },
          {
            "line": 146,
            "text": "用途: 答えや判断が容易でない質問を提起することを表す。  "
          },
          {
            "line": 147,
            "text": "例: The final chapter poses a difficult question about personal responsibility.  "
          },
          {
            "line": 148,
            "text": "訳: 最終章は、個人の責任について難しい問いを投げかけている。  "
          },
          {
            "line": 150,
            "text": "・`pose a problem for discussion`  "
          },
          {
            "line": 151,
            "text": "用途: 解決・検討すべき問題を議論の場に提示することを表す。  "
          },
          {
            "line": 152,
            "text": "例: The teacher posed a problem for discussion before explaining the formula.  "
          },
          {
            "line": 153,
            "text": "訳: その教師は公式を説明する前に、議論する問題を提示した。  "
          },
          {
            "line": 155,
            "text": "・`pose a challenge to 〈theory/assumption〉`  "
          },
          {
            "line": 156,
            "text": "用途: 新しい証拠や議論が、既存の理論・前提を再検討させる論点になることを表す。  "
          },
          {
            "line": 157,
            "text": "例: The results pose a serious challenge to the assumption that demand is stable.  "
          },
          {
            "line": 158,
            "text": "訳: その結果は、需要は安定しているという前提に重大な疑問を投げかける。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 204,
            "text": "【コロケーション】"
          },
          {
            "line": 206,
            "text": "・`pose for a photograph/portrait`  "
          },
          {
            "line": 207,
            "text": "用途: 写真や肖像画に写るため、一定の姿勢を保つことを表す。  "
          },
          {
            "line": 208,
            "text": "例: The two actors posed for a photograph after the ceremony.  "
          },
          {
            "line": 209,
            "text": "訳: その2人の俳優は式典の後、写真撮影のためにポーズを取った。  "
          },
          {
            "line": 211,
            "text": "・`pose for the camera`  "
          },
          {
            "line": 212,
            "text": "用途: カメラに向けて、撮影されるための姿勢を取ることを表す。  "
          },
          {
            "line": 213,
            "text": "例: The children laughed and posed for the camera.  "
          },
          {
            "line": 214,
            "text": "訳: 子どもたちは笑いながらカメラに向かってポーズを取った。  "
          },
          {
            "line": 216,
            "text": "・`pose with 〈person〉`  "
          },
          {
            "line": 217,
            "text": "用途: 他の人と一緒に写真に写る姿勢を取ることを表す。  "
          },
          {
            "line": 218,
            "text": "例: The award winner posed with her parents backstage.  "
          },
          {
            "line": 219,
            "text": "訳: その受賞者は舞台裏で両親と一緒にポーズを取った。  "
          },
          {
            "line": 221,
            "text": "・`pose beside/next to 〈object/person〉`  "
          },
          {
            "line": 222,
            "text": "用途: 特定の物や人の隣で写真に写ることを表す。  "
          },
          {
            "line": 223,
            "text": "例: The visitors posed beside the old locomotive.  "
          },
          {
            "line": 224,
            "text": "訳: 来場者たちは古い機関車の隣でポーズを取った。  "
          },
          {
            "line": 226,
            "text": "・`pose someone for 〈photograph/portrait〉`  "
          },
          {
            "line": 227,
            "text": "用途: 写真家や画家が、モデルの姿勢や位置を決めて撮影・制作することを表す。  "
          },
          {
            "line": 228,
            "text": "例: The photographer posed the family for a formal portrait.  "
          },
          {
            "line": 229,
            "text": "訳: 写真家は正式な家族写真のために、家族を配置した。  "
          },
          {
            "line": 231,
            "text": "・`pose a model in 〈position〉`  "
          },
          {
            "line": 232,
            "text": "用途: モデルを特定の身体の向きや姿勢に置くことを表す。  "
          },
          {
            "line": 233,
            "text": "例: The artist posed the model in a seated position.  "
          },
          {
            "line": 234,
            "text": "訳: その芸術家はモデルを座った姿勢に置いた。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 280,
            "text": "【コロケーション】"
          },
          {
            "line": 282,
            "text": "・`pose in a designer outfit`  "
          },
          {
            "line": 283,
            "text": "用途: 高価・目立つ服装を見せ、印象づけようとして気取ることを表す。  "
          },
          {
            "line": 284,
            "text": "例: He kept posing in a designer outfit instead of helping with the work.  "
          },
          {
            "line": 285,
            "text": "訳: 彼は仕事を手伝わず、高級な服を着て気取ってばかりいた。  "
          },
          {
            "line": 287,
            "text": "・`pose in 〈car/clothes〉`  "
          },
          {
            "line": 288,
            "text": "用途: 車や服などを見せびらかすように、外で気取って振る舞うことを表す。  "
          },
          {
            "line": 289,
            "text": "例: They were out posing in a rented sports car all afternoon.  "
          },
          {
            "line": 290,
            "text": "訳: 彼らは午後ずっと、借りたスポーツカーを見せびらかして外で気取っていた。  "
          },
          {
            "line": 292,
            "text": "・`pose to impress 〈people〉`  "
          },
          {
            "line": 293,
            "text": "用途: 他人に好印象や威圧感を与えようとして、わざと態度を作ることを表す。  "
          },
          {
            "line": 294,
            "text": "例: She was posing to impress the investors, but the presentation lacked evidence.  "
          },
          {
            "line": 295,
            "text": "訳: 彼女は投資家に好印象を与えようと気取っていたが、発表には根拠が欠けていた。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 332,
            "text": "【コロケーション】"
          },
          {
            "line": 334,
            "text": "・`pose as a doctor/police officer`  "
          },
          {
            "line": 335,
            "text": "用途: 医師や警察官ではない人が、その身分を偽って行動することを表す。  "
          },
          {
            "line": 336,
            "text": "例: The man posed as a doctor to gain access to the restricted ward.  "
          },
          {
            "line": 337,
            "text": "訳: その男は立入制限された病棟に入るため、医師を装った。  "
          },
          {
            "line": 339,
            "text": "・`pose as an expert`  "
          },
          {
            "line": 340,
            "text": "用途: 実際には十分な知識や資格がないのに、専門家のように振る舞うことを表す。  "
          },
          {
            "line": 341,
            "text": "例: He posed as an expert on tax law and gave the client incorrect advice.  "
          },
          {
            "line": 342,
            "text": "訳: 彼は税法の専門家を装い、顧客に誤った助言をした。  "
          },
          {
            "line": 344,
            "text": "・`pose as someone's assistant`  "
          },
          {
            "line": 345,
            "text": "用途: 他人の助手だと偽って、情報や場所へのアクセスを得ようとすることを表す。  "
          },
          {
            "line": 346,
            "text": "例: The caller posed as the director's assistant and requested confidential files.  "
          },
          {
            "line": 347,
            "text": "訳: その電話の相手は部長の助手を装い、機密ファイルを要求した。  "
          },
          {
            "line": 349,
            "text": "・`pose as a security guard`  "
          },
          {
            "line": 350,
            "text": "用途: 身分を偽っているところを発見・逮捕されることを表す。  "
          },
          {
            "line": 351,
            "text": "例: The suspect was caught posing as a security guard.  "
          },
          {
            "line": 352,
            "text": "訳: その容疑者は警備員を装っていたところを捕まった。  "
          },
          {
            "line": 354,
            "text": "・`pose as a potential buyer`  "
          },
          {
            "line": 355,
            "text": "用途: 実際には購入者ではない人が、購入希望者を装って接近することを表す。  "
          },
          {
            "line": 356,
            "text": "例: Investigators posed as potential buyers to document the illegal sales.  "
          },
          {
            "line": 357,
            "text": "訳: 調査員たちは違法販売を記録するため、購入希望者を装った。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 403,
            "text": "【コロケーション】"
          },
          {
            "line": 405,
            "text": "・`strike a pose`  "
          },
          {
            "line": 406,
            "text": "用途: 特定の印象を与える姿勢を、意識して素早く取ることを表す。比喩的に、態度を演出する意味にもなる。  "
          },
          {
            "line": 407,
            "text": "例: She struck a confident pose before the interview began.  "
          },
          {
            "line": 408,
            "text": "訳: 彼女は面接が始まる前に自信ありげなポーズを取った。  "
          },
          {
            "line": 410,
            "text": "・`hold a pose`  "
          },
          {
            "line": 411,
            "text": "用途: 写真、絵画、ダンス、運動などで、同じ姿勢を一定時間保つことを表す。  "
          },
          {
            "line": 412,
            "text": "例: The dancer held the pose until the music stopped.  "
          },
          {
            "line": 413,
            "text": "訳: そのダンサーは音楽が止まるまでそのポーズを保った。  "
          },
          {
            "line": 415,
            "text": "・`adopt a relaxed pose`  "
          },
          {
            "line": 416,
            "text": "用途: 体の力を抜いた、落ち着いた姿勢を取ることを表す。  "
          },
          {
            "line": 417,
            "text": "例: He adopted a relaxed pose for the family photograph.  "
          },
          {
            "line": 418,
            "text": "訳: 彼は家族写真のためにくつろいだ姿勢を取った。  "
          },
          {
            "line": 420,
            "text": "・`a pose for the camera`  "
          },
          {
            "line": 421,
            "text": "用途: カメラに写ることを目的とした姿勢を表す。  "
          },
          {
            "line": 422,
            "text": "例: The athlete found a dramatic pose for the camera.  "
          },
          {
            "line": 423,
            "text": "訳: その選手はカメラに向けて劇的なポーズを決めた。  "
          },
          {
            "line": 425,
            "text": "・`a yoga/dance pose`  "
          },
          {
            "line": 426,
            "text": "用途: ヨガやダンスで定められた身体の形・姿勢を表す。  "
          },
          {
            "line": 427,
            "text": "例: The instructor demonstrated a difficult yoga pose.  "
          },
          {
            "line": 428,
            "text": "訳: インストラクターは難しいヨガのポーズを実演した。  "
          },
          {
            "line": 430,
            "text": "・`change/try a pose`  "
          },
          {
            "line": 431,
            "text": "用途: 撮影や演技のために、取る姿勢を変えたり別の姿勢を試したりすることを表す。  "
          },
          {
            "line": 432,
            "text": "例: Try a different pose so the light reaches your face.  "
          },
          {
            "line": 433,
            "text": "訳: 光が顔に当たるように、別のポーズを試してみて。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 479,
            "text": "【コロケーション】"
          },
          {
            "line": 481,
            "text": "・`a mere pose`  "
          },
          {
            "line": 482,
            "text": "用途: 表面上の態度が本心ではなく、効果を狙った見せかけにすぎないことを表す。  "
          },
          {
            "line": 483,
            "text": "例: His concern for the workers was a mere pose.  "
          },
          {
            "line": 484,
            "text": "訳: 彼の労働者への心配は、単なる見せかけだった。  "
          },
          {
            "line": 486,
            "text": "・`a pose of confidence`  "
          },
          {
            "line": 487,
            "text": "用途: 本当の自信があるかどうかにかかわらず、自信があるように見せる態度を表す。  "
          },
          {
            "line": 488,
            "text": "例: Her pose of confidence disappeared when the questions became technical.  "
          },
          {
            "line": 489,
            "text": "訳: 質問が専門的になると、彼女の自信ありげな見せかけは消えた。  "
          },
          {
            "line": 491,
            "text": "・`strike a pose of indifference`  "
          },
          {
            "line": 492,
            "text": "用途: 無関心であるかのような態度を意識して作ることを表す。  "
          },
          {
            "line": 493,
            "text": "例: He struck a pose of indifference, although the criticism clearly hurt him.  "
          },
          {
            "line": 494,
            "text": "訳: その批判は明らかに彼を傷つけたが、彼は無関心を装った。  "
          },
          {
            "line": 496,
            "text": "・`a pose as an expert`  "
          },
          {
            "line": 497,
            "text": "用途: 専門家であるかのように見せる、実体を伴わない立場・態度を表す。  "
          },
          {
            "line": 498,
            "text": "例: Her pose as an expert collapsed when she could not explain the basic terms.  "
          },
          {
            "line": 499,
            "text": "訳: 基本用語を説明できなかったため、彼女の専門家を装う態度は崩れた。  "
          },
          {
            "line": 501,
            "text": "・`see through someone's pose`  "
          },
          {
            "line": 502,
            "text": "用途: 人が作っている態度の裏にある本心や実態を見抜くことを表す。  "
          },
          {
            "line": 503,
            "text": "例: The audience quickly saw through the speaker's pose of certainty.  "
          },
          {
            "line": 504,
            "text": "訳: 聴衆はその話者の確信ありげな見せかけをすぐに見抜いた。  "
          },
          {
            "line": 506,
            "text": "・`drop/abandon the pose`  "
          },
          {
            "line": 507,
            "text": "用途: 作っていた態度をやめ、本来の感情や態度を見せることを表す。  "
          },
          {
            "line": 508,
            "text": "例: Once the cameras were gone, she dropped the pose and admitted that she was worried.  "
          },
          {
            "line": 509,
            "text": "訳: カメラがなくなると、彼女は取り繕うのをやめ、心配していたと認めた。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 585,
            "text": "【コロケーション】"
          },
          {
            "line": 587,
            "text": "・`be completely posed by 〈question〉`  "
          },
          {
            "line": 588,
            "text": "用途: 難しい質問に答えられず、すっかり困惑していることを古風・硬く表す。  "
          },
          {
            "line": 589,
            "text": "例: The witness was completely posed by the examiner's final question.  "
          },
          {
            "line": 590,
            "text": "訳: その証人は試験官の最後の質問にすっかり困惑した。  "
          },
          {
            "line": 592,
            "text": "・`a problem that poses 〈person〉`  "
          },
          {
            "line": 593,
            "text": "用途: 人を手こずらせる問題を、低頻度の他動詞用法で表す。  "
          },
          {
            "line": 594,
            "text": "例: The riddle was a problem that posed even the most experienced solver.  "
          },
          {
            "line": 595,
            "text": "訳: そのなぞなぞは、最も経験豊富な解答者さえ手こずらせる問題だった。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 93,
            "text": "【類義語】"
          },
          {
            "line": 95,
            "text": "・create  "
          },
          {
            "line": 96,
            "text": "定義: 何かを新たに生じさせる。  "
          },
          {
            "line": 97,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 98,
            "text": "違い: `create` は結果を生じさせること全般を表す広い語で、`pose` のように危険・問題を対処対象として提示する硬い含みはない。  "
          },
          {
            "line": 99,
            "text": "例: The change created additional work for the accounting team.  "
          },
          {
            "line": 100,
            "text": "訳: その変更は経理チームに追加の作業を生じさせた。  "
          },
          {
            "line": 102,
            "text": "・present  "
          },
          {
            "line": 103,
            "text": "定義: 問題、機会、危険などを人の前に現れさせる、または直面させる。  "
          },
          {
            "line": 104,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 105,
            "text": "違い: `present` は危険に限らず、状況や機会を提示する中立的な語である。`pose` は特に対処を要する問題・リスクとの結びつきが強い。  "
          },
          {
            "line": 106,
            "text": "例: The new evidence presents a difficulty for the proposed explanation.  "
          },
          {
            "line": 107,
            "text": "訳: 新しい証拠は、提案された説明に難点をもたらす。  "
          },
          {
            "line": 109,
            "text": "・constitute  "
          },
          {
            "line": 110,
            "text": "定義: 全体として、ある危険・問題・脅威に当たる。  "
          },
          {
            "line": 111,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 112,
            "text": "違い: `constitute` は「それ自体が〜である」という分類・評価に焦点があり、`pose` は誰かにとって危険や問題を生じさせる関係に焦点がある。  "
          },
          {
            "line": 113,
            "text": "例: The leak constitutes a serious violation of the safety rules.  "
          },
          {
            "line": 114,
            "text": "訳: その漏えいは安全規則への重大な違反に当たる。  "
          },
          {
            "line": 116,
            "text": "・threaten  "
          },
          {
            "line": 117,
            "text": "定義: 危害や不利益を及ぼすおそれがある、または脅す。  "
          },
          {
            "line": 118,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 119,
            "text": "違い: `threaten` は危険の切迫性や、場合によっては意図的な脅しを強く示す。`pose` は自然現象や制度上の問題にも使う客観的な表現である。  "
          },
          {
            "line": 120,
            "text": "例: Rising sea levels threaten coastal communities.  "
          },
          {
            "line": 121,
            "text": "訳: 海面上昇は沿岸地域社会を脅かしている。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 164,
            "text": "【類義語】"
          },
          {
            "line": 166,
            "text": "・ask  "
          },
          {
            "line": 167,
            "text": "定義: 答えや情報を求めて質問する。  "
          },
          {
            "line": 168,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 169,
            "text": "違い: `ask` は日常会話から正式な場面まで使える基本語で、`pose` よりも「相手から答えを求める行為」に焦点がある。  "
          },
          {
            "line": 170,
            "text": "例: I asked the manager whether the deadline could be extended.  "
          },
          {
            "line": 171,
            "text": "訳: 私は締め切りを延ばせるかどうかマネージャーに尋ねた。  "
          },
          {
            "line": 173,
            "text": "・raise  "
          },
          {
            "line": 174,
            "text": "定義: 問題、疑問、懸念などを話題として持ち出す。  "
          },
          {
            "line": 175,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 176,
            "text": "違い: `raise a question/issue` は論点を会議や議論に持ち込むことに重点があり、`pose` は問いを検討対象として組み立てて提示する含みがある。  "
          },
          {
            "line": 177,
            "text": "例: Several members raised concerns about the new procedure.  "
          },
          {
            "line": 178,
            "text": "訳: 何人かのメンバーが新しい手続きについて懸念を提起した。  "
          },
          {
            "line": 180,
            "text": "・put forward  "
          },
          {
            "line": 181,
            "text": "定義: 考え、提案、議論などを検討のために提示する。  "
          },
          {
            "line": 182,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 183,
            "text": "違い: `put forward` は質問に限らず、案や意見を明示的に提示する句動詞である。`pose` は問い・問題を前に置く表現として硬く響きやすい。  "
          },
          {
            "line": 184,
            "text": "例: The committee put forward three alternatives for reducing costs.  "
          },
          {
            "line": 185,
            "text": "訳: 委員会は費用を削減するための3つの代案を提示した。  "
          },
          {
            "line": 187,
            "text": "・propose  "
          },
          {
            "line": 188,
            "text": "定義: 計画、案、説明などを採用候補として提案する。  "
          },
          {
            "line": 189,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 190,
            "text": "違い: `propose` は実行・採用を期待する案を示すことが多い。`pose a question` は、答えや議論を求める問いを置く表現である。  "
          },
          {
            "line": 191,
            "text": "例: The engineer proposed a simpler design for the device.  "
          },
          {
            "line": 192,
            "text": "訳: その技術者は装置のより簡単な設計を提案した。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 240,
            "text": "【類義語】"
          },
          {
            "line": 242,
            "text": "・position  "
          },
          {
            "line": 243,
            "text": "定義: 人や物を特定の場所・位置に意図的に置く。  "
          },
          {
            "line": 244,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 245,
            "text": "違い: `position` は配置そのものに焦点があり、写真や芸術のために身体の姿勢を作る含みは `pose` ほど強くない。  "
          },
          {
            "line": 246,
            "text": "例: The nurse positioned the lamp beside the examination table.  "
          },
          {
            "line": 247,
            "text": "訳: 看護師は診察台のそばにランプを配置した。  "
          },
          {
            "line": 249,
            "text": "・arrange  "
          },
          {
            "line": 250,
            "text": "定義: 人や物を、見た目や目的に合うように整えて配置する。  "
          },
          {
            "line": 251,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 252,
            "text": "違い: `arrange` は複数の人・物の全体的な並べ方を表す。`pose` は特にモデルの身体の向きや姿勢を決める。  "
          },
          {
            "line": 253,
            "text": "例: The assistant arranged the flowers around the sculpture.  "
          },
          {
            "line": 254,
            "text": "訳: アシスタントは彫刻の周りに花を配置した。  "
          },
          {
            "line": 256,
            "text": "・model  "
          },
          {
            "line": 257,
            "text": "定義: 芸術家のために座ったり立ったりして、作品のモデルを務める。  "
          },
          {
            "line": 258,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 259,
            "text": "違い: `model` は描く側のためにポーズを保つ役割を表し、`pose` のように特定の姿勢を取る行為一般を表すわけではない。  "
          },
          {
            "line": 260,
            "text": "例: She modeled for a sculptor during the winter.  "
          },
          {
            "line": 261,
            "text": "訳: 彼女は冬の間、彫刻家のモデルを務めた。  "
          },
          {
            "line": 263,
            "text": "・sit/stand for 〈artist/photographer〉  "
          },
          {
            "line": 264,
            "text": "定義: 画家や写真家のために座ったり立ったりして姿勢を保つ。  "
          },
          {
            "line": 265,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 266,
            "text": "違い: `sit/stand for` は実際の姿勢とその持続を具体的に述べる句で、`pose` よりも動作の種類が限定される。  "
          },
          {
            "line": 267,
            "text": "例: The child stood for the painter for nearly an hour.  "
          },
          {
            "line": 268,
            "text": "訳: その子どもは1時間近く画家のために立っていた。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 299,
            "text": "【類義語】"
          },
          {
            "line": 301,
            "text": "・posture  "
          },
          {
            "line": 302,
            "text": "定義: 特定の態度や立場を、しばしば実際以上に強く見せるように取る。  "
          },
          {
            "line": 303,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 304,
            "text": "違い: 動詞 `posture` は政治・交渉などで強硬な立場を演じる用法が目立つ。`pose` は服装、態度、人物像を気取って見せる一般的な含みが強い。  "
          },
          {
            "line": 305,
            "text": "例: The two sides postured during the negotiations but later reached an agreement.  "
          },
          {
            "line": 306,
            "text": "訳: 両陣営は交渉中は強硬姿勢を演じたが、後に合意に達した。  "
          },
          {
            "line": 308,
            "text": "・affect  "
          },
          {
            "line": 309,
            "text": "定義: 自然ではない話し方、態度、感情などを意図的に身につけて見せる。  "
          },
          {
            "line": 310,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 311,
            "text": "違い: `affect` は人工的な声・アクセント・態度そのものを作ることに焦点があり、`pose` より硬く、対象が限定されやすい。  "
          },
          {
            "line": 312,
            "text": "例: He affected a calm manner even though he was nervous.  "
          },
          {
            "line": 313,
            "text": "訳: 彼は緊張していたが、平静な態度を装った。  "
          },
          {
            "line": 315,
            "text": "・show off  "
          },
          {
            "line": 316,
            "text": "定義: 能力、所有物、外見などを目立つように示して自慢する。  "
          },
          {
            "line": 317,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 318,
            "text": "違い: `show off` は誇示する行為を直接表す口語である。`pose` は何かを見せるだけでなく、特定の人物像や態度を演出する点を強調する。  "
          },
          {
            "line": 319,
            "text": "例: The teenager was showing off his new motorcycle.  "
          },
          {
            "line": 320,
            "text": "訳: その10代の若者は新しいオートバイを見せびらかしていた。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 363,
            "text": "【類義語】"
          },
          {
            "line": 365,
            "text": "・pretend to be 〈someone/something〉  "
          },
          {
            "line": 366,
            "text": "定義: 本当はそうではない人・物であるふりをする。  "
          },
          {
            "line": 367,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 368,
            "text": "違い: `pretend to be` は遊び、冗談、想像、欺きのすべてに使える最も広い表現で、必ずしも実害のある偽装を示さない。  "
          },
          {
            "line": 369,
            "text": "例: The children pretended to be astronauts during the game.  "
          },
          {
            "line": 370,
            "text": "訳: 子どもたちは遊びの間、宇宙飛行士のふりをした。  "
          },
          {
            "line": 372,
            "text": "・impersonate 〈person/official〉  "
          },
          {
            "line": 373,
            "text": "定義: 特定の人物や公的役割の話し方・身分などをまねて本人のように振る舞う。  "
          },
          {
            "line": 374,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 375,
            "text": "違い: `impersonate` は本人の身元や役割の再現に焦点があり、詐欺・違法行為の文脈で使われやすい。`pose as` はより広く、専門家や購入者などの立場を装う場合にも使う。  "
          },
          {
            "line": 376,
            "text": "例: The caller was charged with impersonating a government official.  "
          },
          {
            "line": 377,
            "text": "訳: その電話の発信者は政府職員になりすましたとして起訴された。  "
          },
          {
            "line": 379,
            "text": "・pass oneself off as 〈someone/something〉  "
          },
          {
            "line": 380,
            "text": "定義: 本当はそうではないのに、他人にそうだと信じさせる。  "
          },
          {
            "line": 381,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 382,
            "text": "違い: `pass oneself off as` は相手に本物だと認めさせようとする欺きの含みが特に強い。`pose as` よりも「見破られずに通す」点に焦点がある。  "
          },
          {
            "line": 383,
            "text": "例: He passed himself off as a qualified electrician.  "
          },
          {
            "line": 384,
            "text": "訳: 彼は資格のある電気技師だと偽って通した。  "
          },
          {
            "line": 386,
            "text": "・masquerade as 〈someone/something〉  "
          },
          {
            "line": 387,
            "text": "定義: 別の人・物・立場を装う。  "
          },
          {
            "line": 388,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 389,
            "text": "違い: `masquerade as` は仮面をかぶるような明白な偽装や、実体を隠す比喩に使われ、`pose as` より文語的・劇的に響くことがある。  "
          },
          {
            "line": 390,
            "text": "例: The website masqueraded as an official public-service portal.  "
          },
          {
            "line": 391,
            "text": "訳: そのウェブサイトは公式の行政サービス窓口を装っていた。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 439,
            "text": "【類義語】"
          },
          {
            "line": 441,
            "text": "・posture  "
          },
          {
            "line": 442,
            "text": "定義: 体の位置や構え、またはその人に特徴的な体の保ち方。  "
          },
          {
            "line": 443,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 444,
            "text": "違い: `posture` は習慣的な姿勢や身体の配列に焦点がある。`pose` は特定の場面で意識して取る一時的・表現的な姿勢に焦点がある。  "
          },
          {
            "line": 445,
            "text": "例: Good posture can reduce strain on the neck.  "
          },
          {
            "line": 446,
            "text": "訳: 良い姿勢は首への負担を減らせる。  "
          },
          {
            "line": 448,
            "text": "・stance  "
          },
          {
            "line": 449,
            "text": "定義: 立っているときの足や体の構え、または意見・立場。  "
          },
          {
            "line": 450,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 451,
            "text": "違い: 身体についての `stance` は安定性や構えを強調し、`pose` のような撮影・演出の含みは弱い。比喩的な意見の意味は `pose` より広く定着している。  "
          },
          {
            "line": 452,
            "text": "例: The boxer changed his stance before the next round.  "
          },
          {
            "line": 453,
            "text": "訳: そのボクサーは次のラウンドの前に構えを変えた。  "
          },
          {
            "line": 455,
            "text": "・position  "
          },
          {
            "line": 456,
            "text": "定義: 人や物が置かれている場所・向き・状態。  "
          },
          {
            "line": 457,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 458,
            "text": "違い: `position` は「どこにあるか」という中立的な位置を指す。`pose` は身体を見せるために取る姿勢や、その姿勢が作る印象を含みやすい。  "
          },
          {
            "line": 459,
            "text": "例: The camera records the exact position of each joint.  "
          },
          {
            "line": 460,
            "text": "訳: そのカメラは各関節の正確な位置を記録する。  "
          },
          {
            "line": 462,
            "text": "・attitude  "
          },
          {
            "line": 463,
            "text": "定義: 体の構え、または人・物事に対する心理的な態度。  "
          },
          {
            "line": 464,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 465,
            "text": "違い: 身体の意味の `attitude` はやや専門的・芸術的で、日常の写真の姿勢には `pose` が普通である。心理的な態度を表す場合は、`pose` と違って本心に反する見せかけを必ずしも含まない。  "
          },
          {
            "line": 466,
            "text": "例: The sculpture has an attitude of quiet movement.  "
          },
          {
            "line": 467,
            "text": "訳: その彫刻には静かな動きを感じさせる姿勢がある。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 515,
            "text": "【類義語】"
          },
          {
            "line": 517,
            "text": "・affectation  "
          },
          {
            "line": 518,
            "text": "定義: 他人に良く見せようとして作る、不自然でわざとらしい話し方や態度。  "
          },
          {
            "line": 519,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 520,
            "text": "違い: `affectation` は特定の仕草、発音、言葉遣いなどの不自然さを指しやすい。`pose` はより広く、人物全体の役割や立場を演出することも表す。  "
          },
          {
            "line": 521,
            "text": "例: Her exaggerated accent was an affectation.  "
          },
          {
            "line": 522,
            "text": "訳: 彼女の大げさなアクセントは、わざとらしい気取りだった。  "
          },
          {
            "line": 524,
            "text": "・pretense  "
          },
          {
            "line": 525,
            "text": "定義: 本当ではないものを本当らしく見せること、またはその見せかけ。  "
          },
          {
            "line": 526,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 527,
            "text": "違い: `pretense` は事実、感情、身分などの偽装全般を表す。`pose` は特に人目を意識して作る態度・人物像に焦点がある。  "
          },
          {
            "line": 528,
            "text": "例: His pretense of being calm did not convince anyone.  "
          },
          {
            "line": 529,
            "text": "訳: 彼が冷静なふりをしても、誰も納得しなかった。  "
          },
          {
            "line": 531,
            "text": "・front  "
          },
          {
            "line": 532,
            "text": "定義: 本当の感情や弱さを隠すために外向きに見せる態度。  "
          },
          {
            "line": 533,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 534,
            "text": "違い: `front` は防御・隠蔽のための外面に焦点がある。`pose` は防御に限らず、印象を良くしたり優位に見せたりする演出にも使う。  "
          },
          {
            "line": 535,
            "text": "例: His cheerful manner was a front for his anxiety.  "
          },
          {
            "line": 536,
            "text": "訳: 彼の陽気な態度は不安を隠すための外面だった。  "
          },
          {
            "line": 538,
            "text": "・act  "
          },
          {
            "line": 539,
            "text": "定義: 本心とは異なる感情や人物を演じること。  "
          },
          {
            "line": 540,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 541,
            "text": "違い: `act` は演技一般を表す口語的な語で、舞台上の演技にも使える。`pose` は短い態度や見せかけを批判的に指しやすい。  "
          },
          {
            "line": 542,
            "text": "例: His apology sounded like an act rather than a sincere admission.  "
          },
          {
            "line": 543,
            "text": "訳: 彼の謝罪は、誠実な認め方というより演技のように聞こえた。  "
          },
          {
            "line": 545,
            "text": "・airs  "
          },
          {
            "line": 546,
            "text": "定義: 実際以上に洗練され、重要であるかのように振る舞う気取り。  "
          },
          {
            "line": 547,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 548,
            "text": "違い: `airs` は上品さや優越感を誇示する含みが強い複数形の表現である。`pose` は優越感に限らず、勇気・無関心・専門性など任意の態度を装える。  "
          },
          {
            "line": 549,
            "text": "例: She puts on airs whenever senior managers enter the room.  "
          },
          {
            "line": 550,
            "text": "訳: 彼女は上級管理職が部屋に入ると、いつも気取った態度を取る。  "
          },
          {
            "line": 552,
            "text": "【反意語】"
          },
          {
            "line": 554,
            "text": "・sincerity  "
          },
          {
            "line": 555,
            "text": "定義: 本心から出た感情や態度で、見せかけでないこと。  "
          },
          {
            "line": 556,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 557,
            "text": "違い: `sincerity` は、効果を狙って作った `pose` と反対に、言動が本心に基づくことを表す。  "
          },
          {
            "line": 558,
            "text": "例: The sincerity of her apology was clear from her actions.  "
          },
          {
            "line": 559,
            "text": "訳: 彼女の謝罪が誠実なものだということは、行動から明らかだった。  "
          },
          {
            "line": 561,
            "text": "・authenticity  "
          },
          {
            "line": 562,
            "text": "定義: 人の感情・態度・作品などが本物で、作為的でないこと。  "
          },
          {
            "line": 563,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 564,
            "text": "違い: `authenticity` は「本物らしさ・本来の自分らしさ」を強調し、`pose` の人工的に作った人物像と対立する。  "
          },
          {
            "line": 565,
            "text": "例: The singer's authenticity mattered more to the audience than her image.  "
          },
          {
            "line": 566,
            "text": "訳: その歌手の本物らしさは、イメージよりも聴衆にとって重要だった。  "
          },
          {
            "line": 568,
            "text": "・genuineness  "
          },
          {
            "line": 569,
            "text": "定義: 感情や態度が偽りなく、本心から出ていること。  "
          },
          {
            "line": 570,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 571,
            "text": "違い: `genuineness` は個々の感情・反応が本物であることを表し、他人に見せるために作られた `pose` と反対の性質である。  "
          },
          {
            "line": 572,
            "text": "例: The genuineness of his surprise was obvious.  "
          },
          {
            "line": 573,
            "text": "訳: 彼の驚きが本物であることは明らかだった。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 599,
            "text": "【類義語】"
          },
          {
            "line": 601,
            "text": "・puzzle  "
          },
          {
            "line": 602,
            "text": "定義: 問題や状況が人を困惑させ、理解や解決を難しくする。  "
          },
          {
            "line": 603,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 604,
            "text": "違い: `puzzle` は現代英語で自然な一般語で、好奇心を刺激する軽い困惑にも、解けない問題にも使える。  "
          },
          {
            "line": 605,
            "text": "例: The unexpected result puzzled the researchers.  "
          },
          {
            "line": 606,
            "text": "訳: 予想外の結果は研究者たちを困惑させた。  "
          },
          {
            "line": 608,
            "text": "・baffle  "
          },
          {
            "line": 609,
            "text": "定義: 難しさや不可解さによって、完全に困らせる。  "
          },
          {
            "line": 610,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 611,
            "text": "違い: `baffle` は `puzzle` より困惑の程度が強く、答えや説明が見つからない含みがある。  "
          },
          {
            "line": 612,
            "text": "例: The strange pattern baffled the police.  "
          },
          {
            "line": 613,
            "text": "訳: その奇妙なパターンは警察を困惑させた。  "
          },
          {
            "line": 615,
            "text": "・perplex  "
          },
          {
            "line": 616,
            "text": "定義: 複雑な問題や矛盾によって、深く困惑させる。  "
          },
          {
            "line": 617,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 618,
            "text": "違い: `perplex` は `puzzle` より文語的で、考えを整理できない深い困惑を表しやすい。  "
          },
          {
            "line": 619,
            "text": "例: The contradictory instructions perplexed the new employees.  "
          },
          {
            "line": 620,
            "text": "訳: 矛盾した指示は新入社員たちを困惑させた。  "
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
      "input_body_sha256": "ecdf6518adf955d45f677a4e2c5e7d9356b4725cf87db77db64fbf1e69380614",
      "input_sections": {
        "core_image": [
          {
            "line": 33,
            "text": "＃コアイメージ"
          },
          {
            "line": 35,
            "text": "`pose` の中心義は、人・物・問い・危険などを、他者が見る・考える・対処する位置へ「置く」ことである。そこから、身体を特定の姿勢に置く用法、質問や問題を検討の前に置く用法、危険を対処すべきものとして生じさせる用法が分かれる。  "
          },
          {
            "line": 36,
            "text": "・危険や困難を対処すべき位置に置く → 「危険・問題を引き起こす」（語義1）  "
          },
          {
            "line": 37,
            "text": "・質問や問題を検討の前に置く → 「質問・問題を提起する」（語義2）  "
          },
          {
            "line": 38,
            "text": "・人や物を見せる姿勢に置く → 「ポーズを取らせる・取る」（語義3）  "
          },
          {
            "line": 39,
            "text": "・自分を人目を引く態度に置く → 「気取って振る舞う」（語義4）  "
          },
          {
            "line": 40,
            "text": "・自分を別人・別の立場として置く → 「〜を装う、なりすます」（語義5）  "
          },
          {
            "line": 41,
            "text": "・身体を置いた姿勢そのもの → 「姿勢、ポーズ」（語義6）  "
          },
          {
            "line": 42,
            "text": "・本心とは別の態度を見せるために置いた姿勢 → 「見せかけの態度」（語義7）  "
          },
          {
            "line": 43,
            "text": "語義8は、古い `appose`／`oppose` に関係する同綴異義の動詞で、語彙的意味がこの「置く」という共通核から導けないため、個別に参照する。  "
          }
        ],
        "sense_structure": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 49,
            "text": "【日本語訳・定義】事物や状況が、誰か・何かにとって対処を要する危険、リスク、問題、困難などを生じさせること。主語が意図的に脅すとは限らず、客観的に「〜という危険をもたらす」「〜の障害となる」と述べる硬めの表現である。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 125,
            "text": "【日本語訳・定義】質問、問題、論点、仮説などを、他者が考えたり議論したりする対象として提示すること。単に発言するより、検討すべき論点を前に置く含みがあり、会議・論文・評論などで使われる。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 196,
            "text": "【日本語訳・定義】人や物を写真、絵画、彫刻、舞台上の構図などに適した姿勢・位置に置くこと。また、人がそのような姿勢を保って写真家や画家のためにポーズを取ること。自分がポーズを取る場合は自動詞、モデルなどに姿勢を取らせる場合は他動詞になる。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 272,
            "text": "【日本語訳・定義】人に良く見せたり、印象づけたりする目的で、自然ではない態度、服装、振る舞いを意識的に演じること。写真撮影のために姿勢を取る語義3と違い、ここでは「気取っている」という批判的な評価が含まれやすい。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 324,
            "text": "【日本語訳・定義】本当はそうではない人や立場であるかのように振る舞い、他人をだますこと。身分を隠して接近する場合や、資格・専門性を持つように見せる場合に使う。単なる遊びの演技にも使えるが、通常は欺きの含みがある。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 395,
            "text": "【日本語訳・定義】人が立つ・座る・体を構えるなどして保つ、特定の身体の姿勢。写真、絵画、彫刻、ダンス、演技、運動などのために意識して取る姿勢を指すことが多いが、写真以外の表現的な姿勢にも使う。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 471,
            "text": "【日本語訳・定義】本当の感情・性格・立場とは別に、他人に特定の印象を与えるために作った態度や人物像。実際にはそう思っていないのに、知的、勇敢、無関心、親切などであるかのように振る舞うことを批判的に表す。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 577,
            "text": "【日本語訳・定義】難しい質問や問題によって、人を困らせて答えに窮させること。現代の一般英語では `puzzle`、`baffle`、`perplex` のほうが普通で、この `pose` は辞書に残る低頻度・硬い用法として理解するとよい。  "
          }
        ],
        "usage_notes": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 89,
            "text": "【語法・注意】`pose` はこの用法では通常、主語に危険や問題を生じさせる事物・状況を置き、危険の受け手は `to`、問題の受け手は `for` で示す。`*pose someone a threat` とせず、`pose a threat to someone` とする。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 160,
            "text": "【語法・注意】この用法の `pose` は、質問や問題を検討の前に置く表現で、`ask` より形式的である。`raise a question` は疑問や論点を持ち出すこと、`propose` は計画・案を提案することに重点がある。`pose a problem` は語義1の「問題を引き起こす」と形が同じなので、`for discussion` や議論を行う主語があれば語義2、被害や障害を受ける対象があれば語義1と判断しやすい。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 236,
            "text": "【語法・注意】自分が姿勢を取るときは `She posed for the camera.` のように目的語を置かない。撮影者がモデルを配置するときは `The photographer posed her for the portrait.` のように人を目的語にする。`pose with` は「〜と一緒に写る」であり、必ずしも特別に気取った姿勢を意味しない。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 297,
            "text": "【語法・注意】この用法の `pose` は、単に写真のためにポーズを取ることではない。写真撮影の文脈で `pose for the camera` と言えば通常は中立的な語義3だが、`pose in an expensive car`、`be posing to impress` のように見せびらかしや人工的な態度が焦点になると語義4になる。`show off` は能力・所有物などを誇示すること、`pose` は態度や人物像を作って見せることに焦点がある。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 359,
            "text": "【語法・注意】`pose as` の `as` は省略できず、後ろには通常、人物・役割・組織などを表す名詞句を置く。`*pose to be a doctor` ではなく、`pose as a doctor` または `pretend to be a doctor` とする。`pretend to be` は冗談や子どものごっこにも使えるが、`pose as` は身元や資格を偽って人を欺く場面に結びつきやすい。`impersonate` は特定の人物や公的役割になりすます行為そのものに焦点があり、`pose as` はその立場を装って相手を欺く文脈を強く示す。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 435,
            "text": "【語法・注意】`pose` は通常 `a pose` と数え、`three different poses` のように複数形にできる。`posture` は普段の体の構えや健康上の姿勢、`position` は身体に限らない位置全般、`stance` は立ち方に加えて意見・立場も表す。したがって「姿勢が悪い」という一般的な身体状態には `bad posture` が自然で、撮影で一時的に取る姿勢には `a pose` が自然である。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 511,
            "text": "【語法・注意】この名詞の `pose` は、単なる意見や態度を中立的に表す `attitude` と異なり、人工的に作られた印象という含みを持つ。`affectation` は話し方や仕草などの不自然な気取り、`pretense` は事実・感情・身分などを偽る見せかけ全般を表す。身体の姿勢なら語義6であり、`a relaxed pose` は通常、批判的な「見せかけ」ではない。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 597,
            "text": "【語法・注意】この意味の `pose` は、写真の姿勢、質問の提起、危険の発生とは別の語義である。`The question posed him` のように人を直接目的語に取る形は現代では非常にまれで、通常は `The question puzzled him.` や `He was baffled by the question.` と言う。  "
          }
        ],
        "word_formation": [
          {
            "line": 26,
            "text": "＃語形成"
          },
          {
            "line": 28,
            "text": "`poser` — 名詞「ポーズを取る人、気取り屋」。別系統の困惑義から「難問、手こずらせる問題」という意味も生じる。  "
          },
          {
            "line": 29,
            "text": "`poseur` — 名詞「気取り屋、見せかけの人物」。フランス語由来の語で、実際以上の知識・洗練・所属を装う人を批判的に指す。  "
          },
          {
            "line": 30,
            "text": "`posable/poseable` — 形容詞「ポーズを取らせられる、望む姿勢に置ける」。人形やフィギュアなど、関節を動かして姿勢を作れる物について使うことが多い。  "
          },
          {
            "line": 31,
            "text": "`posing` — 現在分詞・動名詞形で、「ポーズを取っていること」「気取って振る舞うこと」の両方を文脈に応じて表す。  "
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
      "input_body_sha256": "ecdf6518adf955d45f677a4e2c5e7d9356b4725cf87db77db64fbf1e69380614",
      "input_sections": {
        "sense_structure": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 49,
            "text": "【日本語訳・定義】事物や状況が、誰か・何かにとって対処を要する危険、リスク、問題、困難などを生じさせること。主語が意図的に脅すとは限らず、客観的に「〜という危険をもたらす」「〜の障害となる」と述べる硬めの表現である。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 125,
            "text": "【日本語訳・定義】質問、問題、論点、仮説などを、他者が考えたり議論したりする対象として提示すること。単に発言するより、検討すべき論点を前に置く含みがあり、会議・論文・評論などで使われる。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 196,
            "text": "【日本語訳・定義】人や物を写真、絵画、彫刻、舞台上の構図などに適した姿勢・位置に置くこと。また、人がそのような姿勢を保って写真家や画家のためにポーズを取ること。自分がポーズを取る場合は自動詞、モデルなどに姿勢を取らせる場合は他動詞になる。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 272,
            "text": "【日本語訳・定義】人に良く見せたり、印象づけたりする目的で、自然ではない態度、服装、振る舞いを意識的に演じること。写真撮影のために姿勢を取る語義3と違い、ここでは「気取っている」という批判的な評価が含まれやすい。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 324,
            "text": "【日本語訳・定義】本当はそうではない人や立場であるかのように振る舞い、他人をだますこと。身分を隠して接近する場合や、資格・専門性を持つように見せる場合に使う。単なる遊びの演技にも使えるが、通常は欺きの含みがある。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 395,
            "text": "【日本語訳・定義】人が立つ・座る・体を構えるなどして保つ、特定の身体の姿勢。写真、絵画、彫刻、ダンス、演技、運動などのために意識して取る姿勢を指すことが多いが、写真以外の表現的な姿勢にも使う。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 471,
            "text": "【日本語訳・定義】本当の感情・性格・立場とは別に、他人に特定の印象を与えるために作った態度や人物像。実際にはそう思っていないのに、知的、勇敢、無関心、親切などであるかのように振る舞うことを批判的に表す。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 577,
            "text": "【日本語訳・定義】難しい質問や問題によって、人を困らせて答えに窮させること。現代の一般英語では `puzzle`、`baffle`、`perplex` のほうが普通で、この `pose` は辞書に残る低頻度・硬い用法として理解するとよい。  "
          }
        ],
        "frames": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 55,
            "text": "【文法パターン】`〈事物・状況〉 pose a threat/risk/danger to 〈対象〉`＝〈対象〉に危険をもたらす／`〈事物・状況〉 pose a problem/challenge for 〈人・組織〉`＝〈人・組織〉に問題・課題を生じさせる／`pose a hazard/obstacle/barrier to 〈活動・進行〉`＝活動・進行の障害となる  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 131,
            "text": "【文法パターン】`pose a question to 〈person/group〉`＝〈人・集団〉に質問を提起する／`pose the question of whether 〈節〉`＝〜かどうかという問題を提起する／`pose a problem/issue for discussion`＝議論のために問題・論点を提示する／`pose a challenge to 〈theory/assumption〉`＝理論・前提に対する反論となる論点を提示する／`pose a dilemma for 〈decision-maker〉`＝意思決定者に難しい選択を突きつける  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 202,
            "text": "【文法パターン】`pose for 〈photographer/camera/portrait〉`＝写真家・カメラ・肖像画のためにポーズを取る／`pose with/next to/beside 〈person/object〉`＝人・物と一緒にポーズを取る／`pose in 〈position/place〉`＝特定の姿勢・場所でポーズを取る／`pose someone/something for 〈photograph/portrait〉`＝人・物を写真・肖像画のために配置する／`pose a model in 〈position〉`＝モデルを特定の姿勢に置く  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 278,
            "text": "【文法パターン】`pose in 〈clothes/setting〉`＝服装・場面を利用して気取る／`pose to impress 〈people〉`＝人を感心させようとして気取る  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 330,
            "text": "【文法パターン】`pose as 〈名詞〉`＝〜を装う、〜になりすます／`be posing as 〈名詞〉`＝〜を装っている／`a person posing as 〈role〉`＝〜を装う人  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 401,
            "text": "【文法パターン】`adopt/take/strike a pose`＝ポーズを取る／`hold a pose`＝ポーズを保つ／`in a 〈adjective〉 pose`＝〜な姿勢で／`a pose for the camera/portrait`＝カメラ・肖像画のためのポーズ／`change/try a pose`＝ポーズを変える・試す  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 477,
            "text": "【文法パターン】`a mere pose`＝単なる見せかけ／`a pose of 〈quality/emotion〉`＝〜を装う態度／`strike a pose/an attitude of 〈quality〉`＝〜の態度を演じる／`someone's pose as 〈role〉`＝〜を装う人の見せかけ／`see through/drop the pose`＝見せかけを見抜く・やめる  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 583,
            "text": "【文法パターン】`〈難問・問題〉 pose 〈人〉`＝難問が人を困惑させる  "
          }
        ],
        "collocations_examples": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 57,
            "text": "【コロケーション】"
          },
          {
            "line": 59,
            "text": "・`pose a threat to 〈人・動物・環境〉`  "
          },
          {
            "line": 60,
            "text": "用途: 人、動物、環境などに危害を及ぼす可能性があることを表す。  "
          },
          {
            "line": 61,
            "text": "例: The invasive plant poses a serious threat to native species.  "
          },
          {
            "line": 62,
            "text": "訳: その外来植物は在来種に深刻な脅威をもたらしている。  "
          },
          {
            "line": 64,
            "text": "・`pose a risk to 〈health/safety〉`  "
          },
          {
            "line": 65,
            "text": "用途: 健康や安全に悪い結果が生じる可能性を、客観的・説明的に述べる。  "
          },
          {
            "line": 66,
            "text": "例: Long-term exposure to the chemical may pose a risk to workers' health.  "
          },
          {
            "line": 67,
            "text": "訳: その化学物質への長期的な曝露は、作業員の健康にリスクをもたらす可能性がある。  "
          },
          {
            "line": 69,
            "text": "・`pose a danger to 〈人・集団〉`  "
          },
          {
            "line": 70,
            "text": "用途: 具体的な人や集団に危険が及ぶことを表す。  "
          },
          {
            "line": 71,
            "text": "例: The damaged bridge could pose a danger to pedestrians.  "
          },
          {
            "line": 72,
            "text": "訳: 損傷した橋は歩行者に危険を及ぼすおそれがある。  "
          },
          {
            "line": 74,
            "text": "・`pose a problem for 〈person/system〉`  "
          },
          {
            "line": 75,
            "text": "用途: 事物や状況が、誰かや制度に解決すべき問題を生じさせることを表す。  "
          },
          {
            "line": 76,
            "text": "例: The sudden loss of data posed a serious problem for the research team.  "
          },
          {
            "line": 77,
            "text": "訳: 突然のデータ消失は研究チームに深刻な問題をもたらした。  "
          },
          {
            "line": 79,
            "text": "・`pose a challenge to 〈team/plan〉`  "
          },
          {
            "line": 80,
            "text": "用途: 目標達成や作業の進行を難しくする課題を生じさせることを表す。  "
          },
          {
            "line": 81,
            "text": "例: The steep terrain posed a major challenge to the rescue team.  "
          },
          {
            "line": 82,
            "text": "訳: 険しい地形は救助隊に大きな課題を突きつけた。  "
          },
          {
            "line": 84,
            "text": "・`the threat/risk posed by 〈cause〉`  "
          },
          {
            "line": 85,
            "text": "用途: ある原因がもたらす危険や問題を、名詞句の中で説明する。  "
          },
          {
            "line": 86,
            "text": "例: Officials assessed the risks posed by the overloaded electrical system.  "
          },
          {
            "line": 87,
            "text": "訳: 当局は過負荷状態の電気系統がもたらすリスクを評価した。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 133,
            "text": "【コロケーション】"
          },
          {
            "line": 135,
            "text": "・`pose a question to 〈person/group〉`  "
          },
          {
            "line": 136,
            "text": "用途: 相手に、考える価値のある質問を正式に投げかけることを表す。  "
          },
          {
            "line": 137,
            "text": "例: The moderator posed a question to the panel about the cost of reform.  "
          },
          {
            "line": 138,
            "text": "訳: 司会者は改革の費用についてパネリストたちに質問を投げかけた。  "
          },
          {
            "line": 140,
            "text": "・`pose the question of whether 〈節〉`  "
          },
          {
            "line": 141,
            "text": "用途: 「〜かどうか」という論点を、検討すべき問題として提示する。  "
          },
          {
            "line": 142,
            "text": "例: The discovery poses the question of whether the species can survive in warmer seas.  "
          },
          {
            "line": 143,
            "text": "訳: その発見は、その種がより温暖な海で生き残れるのかという問題を提起する。  "
          },
          {
            "line": 145,
            "text": "・`pose a difficult question`  "
          },
          {
            "line": 146,
            "text": "用途: 答えや判断が容易でない質問を提起することを表す。  "
          },
          {
            "line": 147,
            "text": "例: The final chapter poses a difficult question about personal responsibility.  "
          },
          {
            "line": 148,
            "text": "訳: 最終章は、個人の責任について難しい問いを投げかけている。  "
          },
          {
            "line": 150,
            "text": "・`pose a problem for discussion`  "
          },
          {
            "line": 151,
            "text": "用途: 解決・検討すべき問題を議論の場に提示することを表す。  "
          },
          {
            "line": 152,
            "text": "例: The teacher posed a problem for discussion before explaining the formula.  "
          },
          {
            "line": 153,
            "text": "訳: その教師は公式を説明する前に、議論する問題を提示した。  "
          },
          {
            "line": 155,
            "text": "・`pose a challenge to 〈theory/assumption〉`  "
          },
          {
            "line": 156,
            "text": "用途: 新しい証拠や議論が、既存の理論・前提を再検討させる論点になることを表す。  "
          },
          {
            "line": 157,
            "text": "例: The results pose a serious challenge to the assumption that demand is stable.  "
          },
          {
            "line": 158,
            "text": "訳: その結果は、需要は安定しているという前提に重大な疑問を投げかける。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 204,
            "text": "【コロケーション】"
          },
          {
            "line": 206,
            "text": "・`pose for a photograph/portrait`  "
          },
          {
            "line": 207,
            "text": "用途: 写真や肖像画に写るため、一定の姿勢を保つことを表す。  "
          },
          {
            "line": 208,
            "text": "例: The two actors posed for a photograph after the ceremony.  "
          },
          {
            "line": 209,
            "text": "訳: その2人の俳優は式典の後、写真撮影のためにポーズを取った。  "
          },
          {
            "line": 211,
            "text": "・`pose for the camera`  "
          },
          {
            "line": 212,
            "text": "用途: カメラに向けて、撮影されるための姿勢を取ることを表す。  "
          },
          {
            "line": 213,
            "text": "例: The children laughed and posed for the camera.  "
          },
          {
            "line": 214,
            "text": "訳: 子どもたちは笑いながらカメラに向かってポーズを取った。  "
          },
          {
            "line": 216,
            "text": "・`pose with 〈person〉`  "
          },
          {
            "line": 217,
            "text": "用途: 他の人と一緒に写真に写る姿勢を取ることを表す。  "
          },
          {
            "line": 218,
            "text": "例: The award winner posed with her parents backstage.  "
          },
          {
            "line": 219,
            "text": "訳: その受賞者は舞台裏で両親と一緒にポーズを取った。  "
          },
          {
            "line": 221,
            "text": "・`pose beside/next to 〈object/person〉`  "
          },
          {
            "line": 222,
            "text": "用途: 特定の物や人の隣で写真に写ることを表す。  "
          },
          {
            "line": 223,
            "text": "例: The visitors posed beside the old locomotive.  "
          },
          {
            "line": 224,
            "text": "訳: 来場者たちは古い機関車の隣でポーズを取った。  "
          },
          {
            "line": 226,
            "text": "・`pose someone for 〈photograph/portrait〉`  "
          },
          {
            "line": 227,
            "text": "用途: 写真家や画家が、モデルの姿勢や位置を決めて撮影・制作することを表す。  "
          },
          {
            "line": 228,
            "text": "例: The photographer posed the family for a formal portrait.  "
          },
          {
            "line": 229,
            "text": "訳: 写真家は正式な家族写真のために、家族を配置した。  "
          },
          {
            "line": 231,
            "text": "・`pose a model in 〈position〉`  "
          },
          {
            "line": 232,
            "text": "用途: モデルを特定の身体の向きや姿勢に置くことを表す。  "
          },
          {
            "line": 233,
            "text": "例: The artist posed the model in a seated position.  "
          },
          {
            "line": 234,
            "text": "訳: その芸術家はモデルを座った姿勢に置いた。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 280,
            "text": "【コロケーション】"
          },
          {
            "line": 282,
            "text": "・`pose in a designer outfit`  "
          },
          {
            "line": 283,
            "text": "用途: 高価・目立つ服装を見せ、印象づけようとして気取ることを表す。  "
          },
          {
            "line": 284,
            "text": "例: He kept posing in a designer outfit instead of helping with the work.  "
          },
          {
            "line": 285,
            "text": "訳: 彼は仕事を手伝わず、高級な服を着て気取ってばかりいた。  "
          },
          {
            "line": 287,
            "text": "・`pose in 〈car/clothes〉`  "
          },
          {
            "line": 288,
            "text": "用途: 車や服などを見せびらかすように、外で気取って振る舞うことを表す。  "
          },
          {
            "line": 289,
            "text": "例: They were out posing in a rented sports car all afternoon.  "
          },
          {
            "line": 290,
            "text": "訳: 彼らは午後ずっと、借りたスポーツカーを見せびらかして外で気取っていた。  "
          },
          {
            "line": 292,
            "text": "・`pose to impress 〈people〉`  "
          },
          {
            "line": 293,
            "text": "用途: 他人に好印象や威圧感を与えようとして、わざと態度を作ることを表す。  "
          },
          {
            "line": 294,
            "text": "例: She was posing to impress the investors, but the presentation lacked evidence.  "
          },
          {
            "line": 295,
            "text": "訳: 彼女は投資家に好印象を与えようと気取っていたが、発表には根拠が欠けていた。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 332,
            "text": "【コロケーション】"
          },
          {
            "line": 334,
            "text": "・`pose as a doctor/police officer`  "
          },
          {
            "line": 335,
            "text": "用途: 医師や警察官ではない人が、その身分を偽って行動することを表す。  "
          },
          {
            "line": 336,
            "text": "例: The man posed as a doctor to gain access to the restricted ward.  "
          },
          {
            "line": 337,
            "text": "訳: その男は立入制限された病棟に入るため、医師を装った。  "
          },
          {
            "line": 339,
            "text": "・`pose as an expert`  "
          },
          {
            "line": 340,
            "text": "用途: 実際には十分な知識や資格がないのに、専門家のように振る舞うことを表す。  "
          },
          {
            "line": 341,
            "text": "例: He posed as an expert on tax law and gave the client incorrect advice.  "
          },
          {
            "line": 342,
            "text": "訳: 彼は税法の専門家を装い、顧客に誤った助言をした。  "
          },
          {
            "line": 344,
            "text": "・`pose as someone's assistant`  "
          },
          {
            "line": 345,
            "text": "用途: 他人の助手だと偽って、情報や場所へのアクセスを得ようとすることを表す。  "
          },
          {
            "line": 346,
            "text": "例: The caller posed as the director's assistant and requested confidential files.  "
          },
          {
            "line": 347,
            "text": "訳: その電話の相手は部長の助手を装い、機密ファイルを要求した。  "
          },
          {
            "line": 349,
            "text": "・`pose as a security guard`  "
          },
          {
            "line": 350,
            "text": "用途: 身分を偽っているところを発見・逮捕されることを表す。  "
          },
          {
            "line": 351,
            "text": "例: The suspect was caught posing as a security guard.  "
          },
          {
            "line": 352,
            "text": "訳: その容疑者は警備員を装っていたところを捕まった。  "
          },
          {
            "line": 354,
            "text": "・`pose as a potential buyer`  "
          },
          {
            "line": 355,
            "text": "用途: 実際には購入者ではない人が、購入希望者を装って接近することを表す。  "
          },
          {
            "line": 356,
            "text": "例: Investigators posed as potential buyers to document the illegal sales.  "
          },
          {
            "line": 357,
            "text": "訳: 調査員たちは違法販売を記録するため、購入希望者を装った。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 403,
            "text": "【コロケーション】"
          },
          {
            "line": 405,
            "text": "・`strike a pose`  "
          },
          {
            "line": 406,
            "text": "用途: 特定の印象を与える姿勢を、意識して素早く取ることを表す。比喩的に、態度を演出する意味にもなる。  "
          },
          {
            "line": 407,
            "text": "例: She struck a confident pose before the interview began.  "
          },
          {
            "line": 408,
            "text": "訳: 彼女は面接が始まる前に自信ありげなポーズを取った。  "
          },
          {
            "line": 410,
            "text": "・`hold a pose`  "
          },
          {
            "line": 411,
            "text": "用途: 写真、絵画、ダンス、運動などで、同じ姿勢を一定時間保つことを表す。  "
          },
          {
            "line": 412,
            "text": "例: The dancer held the pose until the music stopped.  "
          },
          {
            "line": 413,
            "text": "訳: そのダンサーは音楽が止まるまでそのポーズを保った。  "
          },
          {
            "line": 415,
            "text": "・`adopt a relaxed pose`  "
          },
          {
            "line": 416,
            "text": "用途: 体の力を抜いた、落ち着いた姿勢を取ることを表す。  "
          },
          {
            "line": 417,
            "text": "例: He adopted a relaxed pose for the family photograph.  "
          },
          {
            "line": 418,
            "text": "訳: 彼は家族写真のためにくつろいだ姿勢を取った。  "
          },
          {
            "line": 420,
            "text": "・`a pose for the camera`  "
          },
          {
            "line": 421,
            "text": "用途: カメラに写ることを目的とした姿勢を表す。  "
          },
          {
            "line": 422,
            "text": "例: The athlete found a dramatic pose for the camera.  "
          },
          {
            "line": 423,
            "text": "訳: その選手はカメラに向けて劇的なポーズを決めた。  "
          },
          {
            "line": 425,
            "text": "・`a yoga/dance pose`  "
          },
          {
            "line": 426,
            "text": "用途: ヨガやダンスで定められた身体の形・姿勢を表す。  "
          },
          {
            "line": 427,
            "text": "例: The instructor demonstrated a difficult yoga pose.  "
          },
          {
            "line": 428,
            "text": "訳: インストラクターは難しいヨガのポーズを実演した。  "
          },
          {
            "line": 430,
            "text": "・`change/try a pose`  "
          },
          {
            "line": 431,
            "text": "用途: 撮影や演技のために、取る姿勢を変えたり別の姿勢を試したりすることを表す。  "
          },
          {
            "line": 432,
            "text": "例: Try a different pose so the light reaches your face.  "
          },
          {
            "line": 433,
            "text": "訳: 光が顔に当たるように、別のポーズを試してみて。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 479,
            "text": "【コロケーション】"
          },
          {
            "line": 481,
            "text": "・`a mere pose`  "
          },
          {
            "line": 482,
            "text": "用途: 表面上の態度が本心ではなく、効果を狙った見せかけにすぎないことを表す。  "
          },
          {
            "line": 483,
            "text": "例: His concern for the workers was a mere pose.  "
          },
          {
            "line": 484,
            "text": "訳: 彼の労働者への心配は、単なる見せかけだった。  "
          },
          {
            "line": 486,
            "text": "・`a pose of confidence`  "
          },
          {
            "line": 487,
            "text": "用途: 本当の自信があるかどうかにかかわらず、自信があるように見せる態度を表す。  "
          },
          {
            "line": 488,
            "text": "例: Her pose of confidence disappeared when the questions became technical.  "
          },
          {
            "line": 489,
            "text": "訳: 質問が専門的になると、彼女の自信ありげな見せかけは消えた。  "
          },
          {
            "line": 491,
            "text": "・`strike a pose of indifference`  "
          },
          {
            "line": 492,
            "text": "用途: 無関心であるかのような態度を意識して作ることを表す。  "
          },
          {
            "line": 493,
            "text": "例: He struck a pose of indifference, although the criticism clearly hurt him.  "
          },
          {
            "line": 494,
            "text": "訳: その批判は明らかに彼を傷つけたが、彼は無関心を装った。  "
          },
          {
            "line": 496,
            "text": "・`a pose as an expert`  "
          },
          {
            "line": 497,
            "text": "用途: 専門家であるかのように見せる、実体を伴わない立場・態度を表す。  "
          },
          {
            "line": 498,
            "text": "例: Her pose as an expert collapsed when she could not explain the basic terms.  "
          },
          {
            "line": 499,
            "text": "訳: 基本用語を説明できなかったため、彼女の専門家を装う態度は崩れた。  "
          },
          {
            "line": 501,
            "text": "・`see through someone's pose`  "
          },
          {
            "line": 502,
            "text": "用途: 人が作っている態度の裏にある本心や実態を見抜くことを表す。  "
          },
          {
            "line": 503,
            "text": "例: The audience quickly saw through the speaker's pose of certainty.  "
          },
          {
            "line": 504,
            "text": "訳: 聴衆はその話者の確信ありげな見せかけをすぐに見抜いた。  "
          },
          {
            "line": 506,
            "text": "・`drop/abandon the pose`  "
          },
          {
            "line": 507,
            "text": "用途: 作っていた態度をやめ、本来の感情や態度を見せることを表す。  "
          },
          {
            "line": 508,
            "text": "例: Once the cameras were gone, she dropped the pose and admitted that she was worried.  "
          },
          {
            "line": 509,
            "text": "訳: カメラがなくなると、彼女は取り繕うのをやめ、心配していたと認めた。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 585,
            "text": "【コロケーション】"
          },
          {
            "line": 587,
            "text": "・`be completely posed by 〈question〉`  "
          },
          {
            "line": 588,
            "text": "用途: 難しい質問に答えられず、すっかり困惑していることを古風・硬く表す。  "
          },
          {
            "line": 589,
            "text": "例: The witness was completely posed by the examiner's final question.  "
          },
          {
            "line": 590,
            "text": "訳: その証人は試験官の最後の質問にすっかり困惑した。  "
          },
          {
            "line": 592,
            "text": "・`a problem that poses 〈person〉`  "
          },
          {
            "line": 593,
            "text": "用途: 人を手こずらせる問題を、低頻度の他動詞用法で表す。  "
          },
          {
            "line": 594,
            "text": "例: The riddle was a problem that posed even the most experienced solver.  "
          },
          {
            "line": 595,
            "text": "訳: そのなぞなぞは、最も経験豊富な解答者さえ手こずらせる問題だった。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 93,
            "text": "【類義語】"
          },
          {
            "line": 95,
            "text": "・create  "
          },
          {
            "line": 96,
            "text": "定義: 何かを新たに生じさせる。  "
          },
          {
            "line": 97,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 98,
            "text": "違い: `create` は結果を生じさせること全般を表す広い語で、`pose` のように危険・問題を対処対象として提示する硬い含みはない。  "
          },
          {
            "line": 99,
            "text": "例: The change created additional work for the accounting team.  "
          },
          {
            "line": 100,
            "text": "訳: その変更は経理チームに追加の作業を生じさせた。  "
          },
          {
            "line": 102,
            "text": "・present  "
          },
          {
            "line": 103,
            "text": "定義: 問題、機会、危険などを人の前に現れさせる、または直面させる。  "
          },
          {
            "line": 104,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 105,
            "text": "違い: `present` は危険に限らず、状況や機会を提示する中立的な語である。`pose` は特に対処を要する問題・リスクとの結びつきが強い。  "
          },
          {
            "line": 106,
            "text": "例: The new evidence presents a difficulty for the proposed explanation.  "
          },
          {
            "line": 107,
            "text": "訳: 新しい証拠は、提案された説明に難点をもたらす。  "
          },
          {
            "line": 109,
            "text": "・constitute  "
          },
          {
            "line": 110,
            "text": "定義: 全体として、ある危険・問題・脅威に当たる。  "
          },
          {
            "line": 111,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 112,
            "text": "違い: `constitute` は「それ自体が〜である」という分類・評価に焦点があり、`pose` は誰かにとって危険や問題を生じさせる関係に焦点がある。  "
          },
          {
            "line": 113,
            "text": "例: The leak constitutes a serious violation of the safety rules.  "
          },
          {
            "line": 114,
            "text": "訳: その漏えいは安全規則への重大な違反に当たる。  "
          },
          {
            "line": 116,
            "text": "・threaten  "
          },
          {
            "line": 117,
            "text": "定義: 危害や不利益を及ぼすおそれがある、または脅す。  "
          },
          {
            "line": 118,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 119,
            "text": "違い: `threaten` は危険の切迫性や、場合によっては意図的な脅しを強く示す。`pose` は自然現象や制度上の問題にも使う客観的な表現である。  "
          },
          {
            "line": 120,
            "text": "例: Rising sea levels threaten coastal communities.  "
          },
          {
            "line": 121,
            "text": "訳: 海面上昇は沿岸地域社会を脅かしている。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 164,
            "text": "【類義語】"
          },
          {
            "line": 166,
            "text": "・ask  "
          },
          {
            "line": 167,
            "text": "定義: 答えや情報を求めて質問する。  "
          },
          {
            "line": 168,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 169,
            "text": "違い: `ask` は日常会話から正式な場面まで使える基本語で、`pose` よりも「相手から答えを求める行為」に焦点がある。  "
          },
          {
            "line": 170,
            "text": "例: I asked the manager whether the deadline could be extended.  "
          },
          {
            "line": 171,
            "text": "訳: 私は締め切りを延ばせるかどうかマネージャーに尋ねた。  "
          },
          {
            "line": 173,
            "text": "・raise  "
          },
          {
            "line": 174,
            "text": "定義: 問題、疑問、懸念などを話題として持ち出す。  "
          },
          {
            "line": 175,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 176,
            "text": "違い: `raise a question/issue` は論点を会議や議論に持ち込むことに重点があり、`pose` は問いを検討対象として組み立てて提示する含みがある。  "
          },
          {
            "line": 177,
            "text": "例: Several members raised concerns about the new procedure.  "
          },
          {
            "line": 178,
            "text": "訳: 何人かのメンバーが新しい手続きについて懸念を提起した。  "
          },
          {
            "line": 180,
            "text": "・put forward  "
          },
          {
            "line": 181,
            "text": "定義: 考え、提案、議論などを検討のために提示する。  "
          },
          {
            "line": 182,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 183,
            "text": "違い: `put forward` は質問に限らず、案や意見を明示的に提示する句動詞である。`pose` は問い・問題を前に置く表現として硬く響きやすい。  "
          },
          {
            "line": 184,
            "text": "例: The committee put forward three alternatives for reducing costs.  "
          },
          {
            "line": 185,
            "text": "訳: 委員会は費用を削減するための3つの代案を提示した。  "
          },
          {
            "line": 187,
            "text": "・propose  "
          },
          {
            "line": 188,
            "text": "定義: 計画、案、説明などを採用候補として提案する。  "
          },
          {
            "line": 189,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 190,
            "text": "違い: `propose` は実行・採用を期待する案を示すことが多い。`pose a question` は、答えや議論を求める問いを置く表現である。  "
          },
          {
            "line": 191,
            "text": "例: The engineer proposed a simpler design for the device.  "
          },
          {
            "line": 192,
            "text": "訳: その技術者は装置のより簡単な設計を提案した。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 240,
            "text": "【類義語】"
          },
          {
            "line": 242,
            "text": "・position  "
          },
          {
            "line": 243,
            "text": "定義: 人や物を特定の場所・位置に意図的に置く。  "
          },
          {
            "line": 244,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 245,
            "text": "違い: `position` は配置そのものに焦点があり、写真や芸術のために身体の姿勢を作る含みは `pose` ほど強くない。  "
          },
          {
            "line": 246,
            "text": "例: The nurse positioned the lamp beside the examination table.  "
          },
          {
            "line": 247,
            "text": "訳: 看護師は診察台のそばにランプを配置した。  "
          },
          {
            "line": 249,
            "text": "・arrange  "
          },
          {
            "line": 250,
            "text": "定義: 人や物を、見た目や目的に合うように整えて配置する。  "
          },
          {
            "line": 251,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 252,
            "text": "違い: `arrange` は複数の人・物の全体的な並べ方を表す。`pose` は特にモデルの身体の向きや姿勢を決める。  "
          },
          {
            "line": 253,
            "text": "例: The assistant arranged the flowers around the sculpture.  "
          },
          {
            "line": 254,
            "text": "訳: アシスタントは彫刻の周りに花を配置した。  "
          },
          {
            "line": 256,
            "text": "・model  "
          },
          {
            "line": 257,
            "text": "定義: 芸術家のために座ったり立ったりして、作品のモデルを務める。  "
          },
          {
            "line": 258,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 259,
            "text": "違い: `model` は描く側のためにポーズを保つ役割を表し、`pose` のように特定の姿勢を取る行為一般を表すわけではない。  "
          },
          {
            "line": 260,
            "text": "例: She modeled for a sculptor during the winter.  "
          },
          {
            "line": 261,
            "text": "訳: 彼女は冬の間、彫刻家のモデルを務めた。  "
          },
          {
            "line": 263,
            "text": "・sit/stand for 〈artist/photographer〉  "
          },
          {
            "line": 264,
            "text": "定義: 画家や写真家のために座ったり立ったりして姿勢を保つ。  "
          },
          {
            "line": 265,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 266,
            "text": "違い: `sit/stand for` は実際の姿勢とその持続を具体的に述べる句で、`pose` よりも動作の種類が限定される。  "
          },
          {
            "line": 267,
            "text": "例: The child stood for the painter for nearly an hour.  "
          },
          {
            "line": 268,
            "text": "訳: その子どもは1時間近く画家のために立っていた。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 299,
            "text": "【類義語】"
          },
          {
            "line": 301,
            "text": "・posture  "
          },
          {
            "line": 302,
            "text": "定義: 特定の態度や立場を、しばしば実際以上に強く見せるように取る。  "
          },
          {
            "line": 303,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 304,
            "text": "違い: 動詞 `posture` は政治・交渉などで強硬な立場を演じる用法が目立つ。`pose` は服装、態度、人物像を気取って見せる一般的な含みが強い。  "
          },
          {
            "line": 305,
            "text": "例: The two sides postured during the negotiations but later reached an agreement.  "
          },
          {
            "line": 306,
            "text": "訳: 両陣営は交渉中は強硬姿勢を演じたが、後に合意に達した。  "
          },
          {
            "line": 308,
            "text": "・affect  "
          },
          {
            "line": 309,
            "text": "定義: 自然ではない話し方、態度、感情などを意図的に身につけて見せる。  "
          },
          {
            "line": 310,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 311,
            "text": "違い: `affect` は人工的な声・アクセント・態度そのものを作ることに焦点があり、`pose` より硬く、対象が限定されやすい。  "
          },
          {
            "line": 312,
            "text": "例: He affected a calm manner even though he was nervous.  "
          },
          {
            "line": 313,
            "text": "訳: 彼は緊張していたが、平静な態度を装った。  "
          },
          {
            "line": 315,
            "text": "・show off  "
          },
          {
            "line": 316,
            "text": "定義: 能力、所有物、外見などを目立つように示して自慢する。  "
          },
          {
            "line": 317,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 318,
            "text": "違い: `show off` は誇示する行為を直接表す口語である。`pose` は何かを見せるだけでなく、特定の人物像や態度を演出する点を強調する。  "
          },
          {
            "line": 319,
            "text": "例: The teenager was showing off his new motorcycle.  "
          },
          {
            "line": 320,
            "text": "訳: その10代の若者は新しいオートバイを見せびらかしていた。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 363,
            "text": "【類義語】"
          },
          {
            "line": 365,
            "text": "・pretend to be 〈someone/something〉  "
          },
          {
            "line": 366,
            "text": "定義: 本当はそうではない人・物であるふりをする。  "
          },
          {
            "line": 367,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 368,
            "text": "違い: `pretend to be` は遊び、冗談、想像、欺きのすべてに使える最も広い表現で、必ずしも実害のある偽装を示さない。  "
          },
          {
            "line": 369,
            "text": "例: The children pretended to be astronauts during the game.  "
          },
          {
            "line": 370,
            "text": "訳: 子どもたちは遊びの間、宇宙飛行士のふりをした。  "
          },
          {
            "line": 372,
            "text": "・impersonate 〈person/official〉  "
          },
          {
            "line": 373,
            "text": "定義: 特定の人物や公的役割の話し方・身分などをまねて本人のように振る舞う。  "
          },
          {
            "line": 374,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 375,
            "text": "違い: `impersonate` は本人の身元や役割の再現に焦点があり、詐欺・違法行為の文脈で使われやすい。`pose as` はより広く、専門家や購入者などの立場を装う場合にも使う。  "
          },
          {
            "line": 376,
            "text": "例: The caller was charged with impersonating a government official.  "
          },
          {
            "line": 377,
            "text": "訳: その電話の発信者は政府職員になりすましたとして起訴された。  "
          },
          {
            "line": 379,
            "text": "・pass oneself off as 〈someone/something〉  "
          },
          {
            "line": 380,
            "text": "定義: 本当はそうではないのに、他人にそうだと信じさせる。  "
          },
          {
            "line": 381,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 382,
            "text": "違い: `pass oneself off as` は相手に本物だと認めさせようとする欺きの含みが特に強い。`pose as` よりも「見破られずに通す」点に焦点がある。  "
          },
          {
            "line": 383,
            "text": "例: He passed himself off as a qualified electrician.  "
          },
          {
            "line": 384,
            "text": "訳: 彼は資格のある電気技師だと偽って通した。  "
          },
          {
            "line": 386,
            "text": "・masquerade as 〈someone/something〉  "
          },
          {
            "line": 387,
            "text": "定義: 別の人・物・立場を装う。  "
          },
          {
            "line": 388,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 389,
            "text": "違い: `masquerade as` は仮面をかぶるような明白な偽装や、実体を隠す比喩に使われ、`pose as` より文語的・劇的に響くことがある。  "
          },
          {
            "line": 390,
            "text": "例: The website masqueraded as an official public-service portal.  "
          },
          {
            "line": 391,
            "text": "訳: そのウェブサイトは公式の行政サービス窓口を装っていた。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 439,
            "text": "【類義語】"
          },
          {
            "line": 441,
            "text": "・posture  "
          },
          {
            "line": 442,
            "text": "定義: 体の位置や構え、またはその人に特徴的な体の保ち方。  "
          },
          {
            "line": 443,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 444,
            "text": "違い: `posture` は習慣的な姿勢や身体の配列に焦点がある。`pose` は特定の場面で意識して取る一時的・表現的な姿勢に焦点がある。  "
          },
          {
            "line": 445,
            "text": "例: Good posture can reduce strain on the neck.  "
          },
          {
            "line": 446,
            "text": "訳: 良い姿勢は首への負担を減らせる。  "
          },
          {
            "line": 448,
            "text": "・stance  "
          },
          {
            "line": 449,
            "text": "定義: 立っているときの足や体の構え、または意見・立場。  "
          },
          {
            "line": 450,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 451,
            "text": "違い: 身体についての `stance` は安定性や構えを強調し、`pose` のような撮影・演出の含みは弱い。比喩的な意見の意味は `pose` より広く定着している。  "
          },
          {
            "line": 452,
            "text": "例: The boxer changed his stance before the next round.  "
          },
          {
            "line": 453,
            "text": "訳: そのボクサーは次のラウンドの前に構えを変えた。  "
          },
          {
            "line": 455,
            "text": "・position  "
          },
          {
            "line": 456,
            "text": "定義: 人や物が置かれている場所・向き・状態。  "
          },
          {
            "line": 457,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 458,
            "text": "違い: `position` は「どこにあるか」という中立的な位置を指す。`pose` は身体を見せるために取る姿勢や、その姿勢が作る印象を含みやすい。  "
          },
          {
            "line": 459,
            "text": "例: The camera records the exact position of each joint.  "
          },
          {
            "line": 460,
            "text": "訳: そのカメラは各関節の正確な位置を記録する。  "
          },
          {
            "line": 462,
            "text": "・attitude  "
          },
          {
            "line": 463,
            "text": "定義: 体の構え、または人・物事に対する心理的な態度。  "
          },
          {
            "line": 464,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 465,
            "text": "違い: 身体の意味の `attitude` はやや専門的・芸術的で、日常の写真の姿勢には `pose` が普通である。心理的な態度を表す場合は、`pose` と違って本心に反する見せかけを必ずしも含まない。  "
          },
          {
            "line": 466,
            "text": "例: The sculpture has an attitude of quiet movement.  "
          },
          {
            "line": 467,
            "text": "訳: その彫刻には静かな動きを感じさせる姿勢がある。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 515,
            "text": "【類義語】"
          },
          {
            "line": 517,
            "text": "・affectation  "
          },
          {
            "line": 518,
            "text": "定義: 他人に良く見せようとして作る、不自然でわざとらしい話し方や態度。  "
          },
          {
            "line": 519,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 520,
            "text": "違い: `affectation` は特定の仕草、発音、言葉遣いなどの不自然さを指しやすい。`pose` はより広く、人物全体の役割や立場を演出することも表す。  "
          },
          {
            "line": 521,
            "text": "例: Her exaggerated accent was an affectation.  "
          },
          {
            "line": 522,
            "text": "訳: 彼女の大げさなアクセントは、わざとらしい気取りだった。  "
          },
          {
            "line": 524,
            "text": "・pretense  "
          },
          {
            "line": 525,
            "text": "定義: 本当ではないものを本当らしく見せること、またはその見せかけ。  "
          },
          {
            "line": 526,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 527,
            "text": "違い: `pretense` は事実、感情、身分などの偽装全般を表す。`pose` は特に人目を意識して作る態度・人物像に焦点がある。  "
          },
          {
            "line": 528,
            "text": "例: His pretense of being calm did not convince anyone.  "
          },
          {
            "line": 529,
            "text": "訳: 彼が冷静なふりをしても、誰も納得しなかった。  "
          },
          {
            "line": 531,
            "text": "・front  "
          },
          {
            "line": 532,
            "text": "定義: 本当の感情や弱さを隠すために外向きに見せる態度。  "
          },
          {
            "line": 533,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 534,
            "text": "違い: `front` は防御・隠蔽のための外面に焦点がある。`pose` は防御に限らず、印象を良くしたり優位に見せたりする演出にも使う。  "
          },
          {
            "line": 535,
            "text": "例: His cheerful manner was a front for his anxiety.  "
          },
          {
            "line": 536,
            "text": "訳: 彼の陽気な態度は不安を隠すための外面だった。  "
          },
          {
            "line": 538,
            "text": "・act  "
          },
          {
            "line": 539,
            "text": "定義: 本心とは異なる感情や人物を演じること。  "
          },
          {
            "line": 540,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 541,
            "text": "違い: `act` は演技一般を表す口語的な語で、舞台上の演技にも使える。`pose` は短い態度や見せかけを批判的に指しやすい。  "
          },
          {
            "line": 542,
            "text": "例: His apology sounded like an act rather than a sincere admission.  "
          },
          {
            "line": 543,
            "text": "訳: 彼の謝罪は、誠実な認め方というより演技のように聞こえた。  "
          },
          {
            "line": 545,
            "text": "・airs  "
          },
          {
            "line": 546,
            "text": "定義: 実際以上に洗練され、重要であるかのように振る舞う気取り。  "
          },
          {
            "line": 547,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 548,
            "text": "違い: `airs` は上品さや優越感を誇示する含みが強い複数形の表現である。`pose` は優越感に限らず、勇気・無関心・専門性など任意の態度を装える。  "
          },
          {
            "line": 549,
            "text": "例: She puts on airs whenever senior managers enter the room.  "
          },
          {
            "line": 550,
            "text": "訳: 彼女は上級管理職が部屋に入ると、いつも気取った態度を取る。  "
          },
          {
            "line": 552,
            "text": "【反意語】"
          },
          {
            "line": 554,
            "text": "・sincerity  "
          },
          {
            "line": 555,
            "text": "定義: 本心から出た感情や態度で、見せかけでないこと。  "
          },
          {
            "line": 556,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 557,
            "text": "違い: `sincerity` は、効果を狙って作った `pose` と反対に、言動が本心に基づくことを表す。  "
          },
          {
            "line": 558,
            "text": "例: The sincerity of her apology was clear from her actions.  "
          },
          {
            "line": 559,
            "text": "訳: 彼女の謝罪が誠実なものだということは、行動から明らかだった。  "
          },
          {
            "line": 561,
            "text": "・authenticity  "
          },
          {
            "line": 562,
            "text": "定義: 人の感情・態度・作品などが本物で、作為的でないこと。  "
          },
          {
            "line": 563,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 564,
            "text": "違い: `authenticity` は「本物らしさ・本来の自分らしさ」を強調し、`pose` の人工的に作った人物像と対立する。  "
          },
          {
            "line": 565,
            "text": "例: The singer's authenticity mattered more to the audience than her image.  "
          },
          {
            "line": 566,
            "text": "訳: その歌手の本物らしさは、イメージよりも聴衆にとって重要だった。  "
          },
          {
            "line": 568,
            "text": "・genuineness  "
          },
          {
            "line": 569,
            "text": "定義: 感情や態度が偽りなく、本心から出ていること。  "
          },
          {
            "line": 570,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 571,
            "text": "違い: `genuineness` は個々の感情・反応が本物であることを表し、他人に見せるために作られた `pose` と反対の性質である。  "
          },
          {
            "line": 572,
            "text": "例: The genuineness of his surprise was obvious.  "
          },
          {
            "line": 573,
            "text": "訳: 彼の驚きが本物であることは明らかだった。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 599,
            "text": "【類義語】"
          },
          {
            "line": 601,
            "text": "・puzzle  "
          },
          {
            "line": 602,
            "text": "定義: 問題や状況が人を困惑させ、理解や解決を難しくする。  "
          },
          {
            "line": 603,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 604,
            "text": "違い: `puzzle` は現代英語で自然な一般語で、好奇心を刺激する軽い困惑にも、解けない問題にも使える。  "
          },
          {
            "line": 605,
            "text": "例: The unexpected result puzzled the researchers.  "
          },
          {
            "line": 606,
            "text": "訳: 予想外の結果は研究者たちを困惑させた。  "
          },
          {
            "line": 608,
            "text": "・baffle  "
          },
          {
            "line": 609,
            "text": "定義: 難しさや不可解さによって、完全に困らせる。  "
          },
          {
            "line": 610,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 611,
            "text": "違い: `baffle` は `puzzle` より困惑の程度が強く、答えや説明が見つからない含みがある。  "
          },
          {
            "line": 612,
            "text": "例: The strange pattern baffled the police.  "
          },
          {
            "line": 613,
            "text": "訳: その奇妙なパターンは警察を困惑させた。  "
          },
          {
            "line": 615,
            "text": "・perplex  "
          },
          {
            "line": 616,
            "text": "定義: 複雑な問題や矛盾によって、深く困惑させる。  "
          },
          {
            "line": 617,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 618,
            "text": "違い: `perplex` は `puzzle` より文語的で、考えを整理できない深い困惑を表しやすい。  "
          },
          {
            "line": 619,
            "text": "例: The contradictory instructions perplexed the new employees.  "
          },
          {
            "line": 620,
            "text": "訳: 矛盾した指示は新入社員たちを困惑させた。  "
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
      "input_body_sha256": "ecdf6518adf955d45f677a4e2c5e7d9356b4725cf87db77db64fbf1e69380614",
      "input_sections": {
        "sense_structure": [
          {
            "sense_id": "sense:001",
            "line": 47,
            "label": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす",
            "definition": "事物や状況が、誰か・何かにとって対処を要する危険、リスク、問題、困難などを生じさせること。主語が意図的に脅すとは限らず、客観的に「〜という危険をもたらす」「〜の障害となる」と述べる硬めの表現である。"
          },
          {
            "sense_id": "sense:002",
            "line": 123,
            "label": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する",
            "definition": "質問、問題、論点、仮説などを、他者が考えたり議論したりする対象として提示すること。単に発言するより、検討すべき論点を前に置く含みがあり、会議・論文・評論などで使われる。"
          },
          {
            "sense_id": "sense:003",
            "line": 194,
            "label": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る",
            "definition": "人や物を写真、絵画、彫刻、舞台上の構図などに適した姿勢・位置に置くこと。また、人がそのような姿勢を保って写真家や画家のためにポーズを取ること。自分がポーズを取る場合は自動詞、モデルなどに姿勢を取らせる場合は他動詞になる。"
          },
          {
            "sense_id": "sense:004",
            "line": 270,
            "label": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする",
            "definition": "人に良く見せたり、印象づけたりする目的で、自然ではない態度、服装、振る舞いを意識的に演じること。写真撮影のために姿勢を取る語義3と違い、ここでは「気取っている」という批判的な評価が含まれやすい。"
          },
          {
            "sense_id": "sense:005",
            "line": 322,
            "label": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます",
            "definition": "本当はそうではない人や立場であるかのように振る舞い、他人をだますこと。身分を隠して接近する場合や、資格・専門性を持つように見せる場合に使う。単なる遊びの演技にも使えるが、通常は欺きの含みがある。"
          },
          {
            "sense_id": "sense:006",
            "line": 393,
            "label": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ",
            "definition": "人が立つ・座る・体を構えるなどして保つ、特定の身体の姿勢。写真、絵画、彫刻、ダンス、演技、運動などのために意識して取る姿勢を指すことが多いが、写真以外の表現的な姿勢にも使う。"
          },
          {
            "sense_id": "sense:007",
            "line": 469,
            "label": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ",
            "definition": "本当の感情・性格・立場とは別に、他人に特定の印象を与えるために作った態度や人物像。実際にはそう思っていないのに、知的、勇敢、無関心、親切などであるかのように振る舞うことを批判的に表す。"
          },
          {
            "sense_id": "sense:008",
            "line": 575,
            "label": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる",
            "definition": "難しい質問や問題によって、人を困らせて答えに窮させること。現代の一般英語では `puzzle`、`baffle`、`perplex` のほうが普通で、この `pose` は辞書に残る低頻度・硬い用法として理解するとよい。"
          }
        ],
        "collocations_examples": [
          {
            "example_id": "ex-0af8eada4460",
            "example": "He adopted a relaxed pose for the family photograph.",
            "translation": "彼は家族写真のためにくつろいだ姿勢を取った。"
          },
          {
            "example_id": "ex-061513b7ddbe",
            "example": "The artist posed the model in a seated position.",
            "translation": "その芸術家はモデルを座った姿勢に置いた。"
          },
          {
            "example_id": "ex-2533255b90b8",
            "example": "The riddle was a problem that posed even the most experienced solver.",
            "translation": "そのなぞなぞは、最も経験豊富な解答者さえ手こずらせる問題だった。"
          },
          {
            "example_id": "ex-ee36a8b07063",
            "example": "The audience quickly saw through the speaker's pose of certainty.",
            "translation": "聴衆はその話者の確信ありげな見せかけをすぐに見抜いた。"
          },
          {
            "example_id": "ex-31a9b86eeb07",
            "example": "The discovery poses the question of whether the species can survive in warmer seas.",
            "translation": "その発見は、その種がより温暖な海で生き残れるのかという問題を提起する。"
          },
          {
            "example_id": "ex-151abf88f292",
            "example": "She struck a confident pose before the interview began.",
            "translation": "彼女は面接が始まる前に自信ありげなポーズを取った。"
          },
          {
            "example_id": "ex-d90f1e8d5150",
            "example": "Officials assessed the risks posed by the overloaded electrical system.",
            "translation": "当局は過負荷状態の電気系統がもたらすリスクを評価した。"
          },
          {
            "example_id": "ex-f2bcb1c2bd8c",
            "example": "The dancer held the pose until the music stopped.",
            "translation": "そのダンサーは音楽が止まるまでそのポーズを保った。"
          },
          {
            "example_id": "ex-6c872ff49a8c",
            "example": "The moderator posed a question to the panel about the cost of reform.",
            "translation": "司会者は改革の費用についてパネリストたちに質問を投げかけた。"
          },
          {
            "example_id": "ex-34d31f13f4f1",
            "example": "The visitors posed beside the old locomotive.",
            "translation": "来場者たちは古い機関車の隣でポーズを取った。"
          },
          {
            "example_id": "ex-c403c3b74758",
            "example": "The award winner posed with her parents backstage.",
            "translation": "その受賞者は舞台裏で両親と一緒にポーズを取った。"
          },
          {
            "example_id": "ex-72a514afef4c",
            "example": "The two actors posed for a photograph after the ceremony.",
            "translation": "その2人の俳優は式典の後、写真撮影のためにポーズを取った。"
          },
          {
            "example_id": "ex-83f50b89d643",
            "example": "Her pose as an expert collapsed when she could not explain the basic terms.",
            "translation": "基本用語を説明できなかったため、彼女の専門家を装う態度は崩れた。"
          },
          {
            "example_id": "ex-51ebef88c469",
            "example": "The athlete found a dramatic pose for the camera.",
            "translation": "その選手はカメラに向けて劇的なポーズを決めた。"
          },
          {
            "example_id": "ex-69b55186b500",
            "example": "The teacher posed a problem for discussion before explaining the formula.",
            "translation": "その教師は公式を説明する前に、議論する問題を提示した。"
          },
          {
            "example_id": "ex-247dd65f3588",
            "example": "She was posing to impress the investors, but the presentation lacked evidence.",
            "translation": "彼女は投資家に好印象を与えようと気取っていたが、発表には根拠が欠けていた。"
          },
          {
            "example_id": "ex-d050804f14d7",
            "example": "Try a different pose so the light reaches your face.",
            "translation": "光が顔に当たるように、別のポーズを試してみて。"
          },
          {
            "example_id": "ex-696a832d81b6",
            "example": "The invasive plant poses a serious threat to native species.",
            "translation": "その外来植物は在来種に深刻な脅威をもたらしている。"
          },
          {
            "example_id": "ex-ad0ecec17dbf",
            "example": "The suspect was caught posing as a security guard.",
            "translation": "その容疑者は警備員を装っていたところを捕まった。"
          },
          {
            "example_id": "ex-f9dd43a4bb7c",
            "example": "The results pose a serious challenge to the assumption that demand is stable.",
            "translation": "その結果は、需要は安定しているという前提に重大な疑問を投げかける。"
          },
          {
            "example_id": "ex-74dee102cfda",
            "example": "He kept posing in a designer outfit instead of helping with the work.",
            "translation": "彼は仕事を手伝わず、高級な服を着て気取ってばかりいた。"
          },
          {
            "example_id": "ex-f72984ca318b",
            "example": "They were out posing in a rented sports car all afternoon.",
            "translation": "彼らは午後ずっと、借りたスポーツカーを見せびらかして外で気取っていた。"
          },
          {
            "example_id": "ex-88c870d8a0f1",
            "example": "Investigators posed as potential buyers to document the illegal sales.",
            "translation": "調査員たちは違法販売を記録するため、購入希望者を装った。"
          },
          {
            "example_id": "ex-c92fd6a1b903",
            "example": "Long-term exposure to the chemical may pose a risk to workers' health.",
            "translation": "その化学物質への長期的な曝露は、作業員の健康にリスクをもたらす可能性がある。"
          },
          {
            "example_id": "ex-1ac0898e6b26",
            "example": "Once the cameras were gone, she dropped the pose and admitted that she was worried.",
            "translation": "カメラがなくなると、彼女は取り繕うのをやめ、心配していたと認めた。"
          },
          {
            "example_id": "ex-7eb7b38e799a",
            "example": "The final chapter poses a difficult question about personal responsibility.",
            "translation": "最終章は、個人の責任について難しい問いを投げかけている。"
          },
          {
            "example_id": "ex-1074f88ab8b7",
            "example": "The caller posed as the director's assistant and requested confidential files.",
            "translation": "その電話の相手は部長の助手を装い、機密ファイルを要求した。"
          },
          {
            "example_id": "ex-bf001a180ab3",
            "example": "The steep terrain posed a major challenge to the rescue team.",
            "translation": "険しい地形は救助隊に大きな課題を突きつけた。"
          },
          {
            "example_id": "ex-9d60abc9e362",
            "example": "The instructor demonstrated a difficult yoga pose.",
            "translation": "インストラクターは難しいヨガのポーズを実演した。"
          },
          {
            "example_id": "ex-035d904faf22",
            "example": "He struck a pose of indifference, although the criticism clearly hurt him.",
            "translation": "その批判は明らかに彼を傷つけたが、彼は無関心を装った。"
          },
          {
            "example_id": "ex-de0b35dcec78",
            "example": "The damaged bridge could pose a danger to pedestrians.",
            "translation": "損傷した橋は歩行者に危険を及ぼすおそれがある。"
          },
          {
            "example_id": "ex-4ddb1203dc9a",
            "example": "The children laughed and posed for the camera.",
            "translation": "子どもたちは笑いながらカメラに向かってポーズを取った。"
          },
          {
            "example_id": "ex-57732c30fe30",
            "example": "The witness was completely posed by the examiner's final question.",
            "translation": "その証人は試験官の最後の質問にすっかり困惑した。"
          },
          {
            "example_id": "ex-e96a6b223b3d",
            "example": "The sudden loss of data posed a serious problem for the research team.",
            "translation": "突然のデータ消失は研究チームに深刻な問題をもたらした。"
          },
          {
            "example_id": "ex-102d81bd1689",
            "example": "Her pose of confidence disappeared when the questions became technical.",
            "translation": "質問が専門的になると、彼女の自信ありげな見せかけは消えた。"
          },
          {
            "example_id": "ex-191fa116ce7c",
            "example": "The man posed as a doctor to gain access to the restricted ward.",
            "translation": "その男は立入制限された病棟に入るため、医師を装った。"
          },
          {
            "example_id": "ex-edc717df1cd1",
            "example": "He posed as an expert on tax law and gave the client incorrect advice.",
            "translation": "彼は税法の専門家を装い、顧客に誤った助言をした。"
          },
          {
            "example_id": "ex-8916cf60559d",
            "example": "The photographer posed the family for a formal portrait.",
            "translation": "写真家は正式な家族写真のために、家族を配置した。"
          },
          {
            "example_id": "ex-97af90510b14",
            "example": "His concern for the workers was a mere pose.",
            "translation": "彼の労働者への心配は、単なる見せかけだった。"
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
      "input_body_sha256": "ecdf6518adf955d45f677a4e2c5e7d9356b4725cf87db77db64fbf1e69380614",
      "input_sections": {
        "etymology": [
          {
            "line": 20,
            "text": "＃語源"
          },
          {
            "line": 22,
            "text": "中心的な動詞 `pose` は中英語 `posen`、古フランス語 `poser`「置く、位置づける、提案する」を経て、後期ラテン語 `pausare`「止める、休ませる、休止する」に由来する。フランス語の `poser` が「置く」という意味を発達させる過程で、ラテン語 `ponere`「置く」とその過去分詞 `positus` との形の類似・意味上の連想も影響したと説明されるが、`pausare` と `ponere` は本来別語源である。  "
          },
          {
            "line": 23,
            "text": "英語では「特定の位置に置く」から「特定の姿勢を取る・取らせる」へ、さらに「質問や問題を目の前に提示する」「危険や問題を生じさせる」へ用法が広がった。名詞の `pose` はこの動詞から生じ、19世紀初頭には身体の姿勢を表す語として使われていた。  "
          },
          {
            "line": 24,
            "text": "「困惑させる」という別の動詞 `pose` は、古い `appose`／`oppose` の短縮・変形に関係する別系統で、写真や質問を「置く」という中心義から直接派生したものとして扱わない。`pause` は `pausare` を共有する同語源語で、`propose`、`compose`、`expose` などはフランス語の `poser` 系統を含むが、現代英語で `pose` に接頭辞を付けて作った単純な派生語ではない。  "
          }
        ],
        "word_formation": [
          {
            "line": 26,
            "text": "＃語形成"
          },
          {
            "line": 28,
            "text": "`poser` — 名詞「ポーズを取る人、気取り屋」。別系統の困惑義から「難問、手こずらせる問題」という意味も生じる。  "
          },
          {
            "line": 29,
            "text": "`poseur` — 名詞「気取り屋、見せかけの人物」。フランス語由来の語で、実際以上の知識・洗練・所属を装う人を批判的に指す。  "
          },
          {
            "line": 30,
            "text": "`posable/poseable` — 形容詞「ポーズを取らせられる、望む姿勢に置ける」。人形やフィギュアなど、関節を動かして姿勢を作れる物について使うことが多い。  "
          },
          {
            "line": 31,
            "text": "`posing` — 現在分詞・動名詞形で、「ポーズを取っていること」「気取って振る舞うこと」の両方を文脈に応じて表す。  "
          }
        ],
        "sense_structure": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 49,
            "text": "【日本語訳・定義】事物や状況が、誰か・何かにとって対処を要する危険、リスク、問題、困難などを生じさせること。主語が意図的に脅すとは限らず、客観的に「〜という危険をもたらす」「〜の障害となる」と述べる硬めの表現である。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 125,
            "text": "【日本語訳・定義】質問、問題、論点、仮説などを、他者が考えたり議論したりする対象として提示すること。単に発言するより、検討すべき論点を前に置く含みがあり、会議・論文・評論などで使われる。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 196,
            "text": "【日本語訳・定義】人や物を写真、絵画、彫刻、舞台上の構図などに適した姿勢・位置に置くこと。また、人がそのような姿勢を保って写真家や画家のためにポーズを取ること。自分がポーズを取る場合は自動詞、モデルなどに姿勢を取らせる場合は他動詞になる。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 272,
            "text": "【日本語訳・定義】人に良く見せたり、印象づけたりする目的で、自然ではない態度、服装、振る舞いを意識的に演じること。写真撮影のために姿勢を取る語義3と違い、ここでは「気取っている」という批判的な評価が含まれやすい。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 324,
            "text": "【日本語訳・定義】本当はそうではない人や立場であるかのように振る舞い、他人をだますこと。身分を隠して接近する場合や、資格・専門性を持つように見せる場合に使う。単なる遊びの演技にも使えるが、通常は欺きの含みがある。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 395,
            "text": "【日本語訳・定義】人が立つ・座る・体を構えるなどして保つ、特定の身体の姿勢。写真、絵画、彫刻、ダンス、演技、運動などのために意識して取る姿勢を指すことが多いが、写真以外の表現的な姿勢にも使う。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 471,
            "text": "【日本語訳・定義】本当の感情・性格・立場とは別に、他人に特定の印象を与えるために作った態度や人物像。実際にはそう思っていないのに、知的、勇敢、無関心、親切などであるかのように振る舞うことを批判的に表す。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 577,
            "text": "【日本語訳・定義】難しい質問や問題によって、人を困らせて答えに窮させること。現代の一般英語では `puzzle`、`baffle`、`perplex` のほうが普通で、この `pose` は辞書に残る低頻度・硬い用法として理解するとよい。  "
          }
        ],
        "frequency_register": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 51,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 53,
            "text": "【レジスター/領域】標準語。報道、行政、科学、医療、安全管理、ビジネスで特に多い。`threat`、`risk`、`danger` では害の可能性、`problem`、`challenge`、`obstacle` では対処の難しさに焦点が移る。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 127,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 129,
            "text": "【レジスター/領域】標準語・やや硬い表現。会議、研究、教育、評論、報道で広く使う。質問を普通に尋ねる日常会話では `ask`、論点を持ち出す場合は `raise` もよく使う。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 198,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 200,
            "text": "【レジスター/領域】標準語。写真、絵画、広告、ファッション、ダンス、日常の記念撮影で使う。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 274,
            "text": "【頻度】〈5/10〉  "
          },
          {
            "line": 276,
            "text": "【レジスター/領域】標準語・やや否定的。会話、評論、人物描写で使う。しばしば進行形 `be posing` で、目の前で気取って振る舞う様子を描写する。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 326,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 328,
            "text": "【レジスター/領域】標準語。詐欺、犯罪報道、潜入捜査、人物批判、オンライン上の身元偽装で使う。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 397,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 399,
            "text": "【レジスター/領域】標準語。日常会話、写真、芸術、ファッション、ダンス、ヨガ・フィットネスで使う。通常は可算名詞で、`a pose`、`several poses` のように数える。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 473,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 475,
            "text": "【レジスター/領域】標準語・批判的な人物描写。評論、文学、会話、政治・社会的な態度の分析で使う。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 579,
            "text": "【頻度】〈2/10〉  "
          },
          {
            "line": 581,
            "text": "【レジスター/領域】まれ・古風または文語的。古い文章、辞書の用例、硬い人物描写などで見られるが、学習者が自分で使う必要性は低い。語源的にも、語義1〜7の `pose` とは別系統である。  "
          }
        ],
        "usage_notes": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 89,
            "text": "【語法・注意】`pose` はこの用法では通常、主語に危険や問題を生じさせる事物・状況を置き、危険の受け手は `to`、問題の受け手は `for` で示す。`*pose someone a threat` とせず、`pose a threat to someone` とする。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 160,
            "text": "【語法・注意】この用法の `pose` は、質問や問題を検討の前に置く表現で、`ask` より形式的である。`raise a question` は疑問や論点を持ち出すこと、`propose` は計画・案を提案することに重点がある。`pose a problem` は語義1の「問題を引き起こす」と形が同じなので、`for discussion` や議論を行う主語があれば語義2、被害や障害を受ける対象があれば語義1と判断しやすい。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 236,
            "text": "【語法・注意】自分が姿勢を取るときは `She posed for the camera.` のように目的語を置かない。撮影者がモデルを配置するときは `The photographer posed her for the portrait.` のように人を目的語にする。`pose with` は「〜と一緒に写る」であり、必ずしも特別に気取った姿勢を意味しない。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 297,
            "text": "【語法・注意】この用法の `pose` は、単に写真のためにポーズを取ることではない。写真撮影の文脈で `pose for the camera` と言えば通常は中立的な語義3だが、`pose in an expensive car`、`be posing to impress` のように見せびらかしや人工的な態度が焦点になると語義4になる。`show off` は能力・所有物などを誇示すること、`pose` は態度や人物像を作って見せることに焦点がある。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 359,
            "text": "【語法・注意】`pose as` の `as` は省略できず、後ろには通常、人物・役割・組織などを表す名詞句を置く。`*pose to be a doctor` ではなく、`pose as a doctor` または `pretend to be a doctor` とする。`pretend to be` は冗談や子どものごっこにも使えるが、`pose as` は身元や資格を偽って人を欺く場面に結びつきやすい。`impersonate` は特定の人物や公的役割になりすます行為そのものに焦点があり、`pose as` はその立場を装って相手を欺く文脈を強く示す。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 435,
            "text": "【語法・注意】`pose` は通常 `a pose` と数え、`three different poses` のように複数形にできる。`posture` は普段の体の構えや健康上の姿勢、`position` は身体に限らない位置全般、`stance` は立ち方に加えて意見・立場も表す。したがって「姿勢が悪い」という一般的な身体状態には `bad posture` が自然で、撮影で一時的に取る姿勢には `a pose` が自然である。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 511,
            "text": "【語法・注意】この名詞の `pose` は、単なる意見や態度を中立的に表す `attitude` と異なり、人工的に作られた印象という含みを持つ。`affectation` は話し方や仕草などの不自然な気取り、`pretense` は事実・感情・身分などを偽る見せかけ全般を表す。身体の姿勢なら語義6であり、`a relaxed pose` は通常、批判的な「見せかけ」ではない。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 597,
            "text": "【語法・注意】この意味の `pose` は、写真の姿勢、質問の提起、危険の発生とは別の語義である。`The question posed him` のように人を直接目的語に取る形は現代では非常にまれで、通常は `The question puzzled him.` や `He was baffled by the question.` と言う。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 57,
            "text": "【コロケーション】"
          },
          {
            "line": 59,
            "text": "・`pose a threat to 〈人・動物・環境〉`  "
          },
          {
            "line": 60,
            "text": "用途: 人、動物、環境などに危害を及ぼす可能性があることを表す。  "
          },
          {
            "line": 61,
            "text": "例: The invasive plant poses a serious threat to native species.  "
          },
          {
            "line": 62,
            "text": "訳: その外来植物は在来種に深刻な脅威をもたらしている。  "
          },
          {
            "line": 64,
            "text": "・`pose a risk to 〈health/safety〉`  "
          },
          {
            "line": 65,
            "text": "用途: 健康や安全に悪い結果が生じる可能性を、客観的・説明的に述べる。  "
          },
          {
            "line": 66,
            "text": "例: Long-term exposure to the chemical may pose a risk to workers' health.  "
          },
          {
            "line": 67,
            "text": "訳: その化学物質への長期的な曝露は、作業員の健康にリスクをもたらす可能性がある。  "
          },
          {
            "line": 69,
            "text": "・`pose a danger to 〈人・集団〉`  "
          },
          {
            "line": 70,
            "text": "用途: 具体的な人や集団に危険が及ぶことを表す。  "
          },
          {
            "line": 71,
            "text": "例: The damaged bridge could pose a danger to pedestrians.  "
          },
          {
            "line": 72,
            "text": "訳: 損傷した橋は歩行者に危険を及ぼすおそれがある。  "
          },
          {
            "line": 74,
            "text": "・`pose a problem for 〈person/system〉`  "
          },
          {
            "line": 75,
            "text": "用途: 事物や状況が、誰かや制度に解決すべき問題を生じさせることを表す。  "
          },
          {
            "line": 76,
            "text": "例: The sudden loss of data posed a serious problem for the research team.  "
          },
          {
            "line": 77,
            "text": "訳: 突然のデータ消失は研究チームに深刻な問題をもたらした。  "
          },
          {
            "line": 79,
            "text": "・`pose a challenge to 〈team/plan〉`  "
          },
          {
            "line": 80,
            "text": "用途: 目標達成や作業の進行を難しくする課題を生じさせることを表す。  "
          },
          {
            "line": 81,
            "text": "例: The steep terrain posed a major challenge to the rescue team.  "
          },
          {
            "line": 82,
            "text": "訳: 険しい地形は救助隊に大きな課題を突きつけた。  "
          },
          {
            "line": 84,
            "text": "・`the threat/risk posed by 〈cause〉`  "
          },
          {
            "line": 85,
            "text": "用途: ある原因がもたらす危険や問題を、名詞句の中で説明する。  "
          },
          {
            "line": 86,
            "text": "例: Officials assessed the risks posed by the overloaded electrical system.  "
          },
          {
            "line": 87,
            "text": "訳: 当局は過負荷状態の電気系統がもたらすリスクを評価した。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 133,
            "text": "【コロケーション】"
          },
          {
            "line": 135,
            "text": "・`pose a question to 〈person/group〉`  "
          },
          {
            "line": 136,
            "text": "用途: 相手に、考える価値のある質問を正式に投げかけることを表す。  "
          },
          {
            "line": 137,
            "text": "例: The moderator posed a question to the panel about the cost of reform.  "
          },
          {
            "line": 138,
            "text": "訳: 司会者は改革の費用についてパネリストたちに質問を投げかけた。  "
          },
          {
            "line": 140,
            "text": "・`pose the question of whether 〈節〉`  "
          },
          {
            "line": 141,
            "text": "用途: 「〜かどうか」という論点を、検討すべき問題として提示する。  "
          },
          {
            "line": 142,
            "text": "例: The discovery poses the question of whether the species can survive in warmer seas.  "
          },
          {
            "line": 143,
            "text": "訳: その発見は、その種がより温暖な海で生き残れるのかという問題を提起する。  "
          },
          {
            "line": 145,
            "text": "・`pose a difficult question`  "
          },
          {
            "line": 146,
            "text": "用途: 答えや判断が容易でない質問を提起することを表す。  "
          },
          {
            "line": 147,
            "text": "例: The final chapter poses a difficult question about personal responsibility.  "
          },
          {
            "line": 148,
            "text": "訳: 最終章は、個人の責任について難しい問いを投げかけている。  "
          },
          {
            "line": 150,
            "text": "・`pose a problem for discussion`  "
          },
          {
            "line": 151,
            "text": "用途: 解決・検討すべき問題を議論の場に提示することを表す。  "
          },
          {
            "line": 152,
            "text": "例: The teacher posed a problem for discussion before explaining the formula.  "
          },
          {
            "line": 153,
            "text": "訳: その教師は公式を説明する前に、議論する問題を提示した。  "
          },
          {
            "line": 155,
            "text": "・`pose a challenge to 〈theory/assumption〉`  "
          },
          {
            "line": 156,
            "text": "用途: 新しい証拠や議論が、既存の理論・前提を再検討させる論点になることを表す。  "
          },
          {
            "line": 157,
            "text": "例: The results pose a serious challenge to the assumption that demand is stable.  "
          },
          {
            "line": 158,
            "text": "訳: その結果は、需要は安定しているという前提に重大な疑問を投げかける。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 204,
            "text": "【コロケーション】"
          },
          {
            "line": 206,
            "text": "・`pose for a photograph/portrait`  "
          },
          {
            "line": 207,
            "text": "用途: 写真や肖像画に写るため、一定の姿勢を保つことを表す。  "
          },
          {
            "line": 208,
            "text": "例: The two actors posed for a photograph after the ceremony.  "
          },
          {
            "line": 209,
            "text": "訳: その2人の俳優は式典の後、写真撮影のためにポーズを取った。  "
          },
          {
            "line": 211,
            "text": "・`pose for the camera`  "
          },
          {
            "line": 212,
            "text": "用途: カメラに向けて、撮影されるための姿勢を取ることを表す。  "
          },
          {
            "line": 213,
            "text": "例: The children laughed and posed for the camera.  "
          },
          {
            "line": 214,
            "text": "訳: 子どもたちは笑いながらカメラに向かってポーズを取った。  "
          },
          {
            "line": 216,
            "text": "・`pose with 〈person〉`  "
          },
          {
            "line": 217,
            "text": "用途: 他の人と一緒に写真に写る姿勢を取ることを表す。  "
          },
          {
            "line": 218,
            "text": "例: The award winner posed with her parents backstage.  "
          },
          {
            "line": 219,
            "text": "訳: その受賞者は舞台裏で両親と一緒にポーズを取った。  "
          },
          {
            "line": 221,
            "text": "・`pose beside/next to 〈object/person〉`  "
          },
          {
            "line": 222,
            "text": "用途: 特定の物や人の隣で写真に写ることを表す。  "
          },
          {
            "line": 223,
            "text": "例: The visitors posed beside the old locomotive.  "
          },
          {
            "line": 224,
            "text": "訳: 来場者たちは古い機関車の隣でポーズを取った。  "
          },
          {
            "line": 226,
            "text": "・`pose someone for 〈photograph/portrait〉`  "
          },
          {
            "line": 227,
            "text": "用途: 写真家や画家が、モデルの姿勢や位置を決めて撮影・制作することを表す。  "
          },
          {
            "line": 228,
            "text": "例: The photographer posed the family for a formal portrait.  "
          },
          {
            "line": 229,
            "text": "訳: 写真家は正式な家族写真のために、家族を配置した。  "
          },
          {
            "line": 231,
            "text": "・`pose a model in 〈position〉`  "
          },
          {
            "line": 232,
            "text": "用途: モデルを特定の身体の向きや姿勢に置くことを表す。  "
          },
          {
            "line": 233,
            "text": "例: The artist posed the model in a seated position.  "
          },
          {
            "line": 234,
            "text": "訳: その芸術家はモデルを座った姿勢に置いた。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 280,
            "text": "【コロケーション】"
          },
          {
            "line": 282,
            "text": "・`pose in a designer outfit`  "
          },
          {
            "line": 283,
            "text": "用途: 高価・目立つ服装を見せ、印象づけようとして気取ることを表す。  "
          },
          {
            "line": 284,
            "text": "例: He kept posing in a designer outfit instead of helping with the work.  "
          },
          {
            "line": 285,
            "text": "訳: 彼は仕事を手伝わず、高級な服を着て気取ってばかりいた。  "
          },
          {
            "line": 287,
            "text": "・`pose in 〈car/clothes〉`  "
          },
          {
            "line": 288,
            "text": "用途: 車や服などを見せびらかすように、外で気取って振る舞うことを表す。  "
          },
          {
            "line": 289,
            "text": "例: They were out posing in a rented sports car all afternoon.  "
          },
          {
            "line": 290,
            "text": "訳: 彼らは午後ずっと、借りたスポーツカーを見せびらかして外で気取っていた。  "
          },
          {
            "line": 292,
            "text": "・`pose to impress 〈people〉`  "
          },
          {
            "line": 293,
            "text": "用途: 他人に好印象や威圧感を与えようとして、わざと態度を作ることを表す。  "
          },
          {
            "line": 294,
            "text": "例: She was posing to impress the investors, but the presentation lacked evidence.  "
          },
          {
            "line": 295,
            "text": "訳: 彼女は投資家に好印象を与えようと気取っていたが、発表には根拠が欠けていた。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 332,
            "text": "【コロケーション】"
          },
          {
            "line": 334,
            "text": "・`pose as a doctor/police officer`  "
          },
          {
            "line": 335,
            "text": "用途: 医師や警察官ではない人が、その身分を偽って行動することを表す。  "
          },
          {
            "line": 336,
            "text": "例: The man posed as a doctor to gain access to the restricted ward.  "
          },
          {
            "line": 337,
            "text": "訳: その男は立入制限された病棟に入るため、医師を装った。  "
          },
          {
            "line": 339,
            "text": "・`pose as an expert`  "
          },
          {
            "line": 340,
            "text": "用途: 実際には十分な知識や資格がないのに、専門家のように振る舞うことを表す。  "
          },
          {
            "line": 341,
            "text": "例: He posed as an expert on tax law and gave the client incorrect advice.  "
          },
          {
            "line": 342,
            "text": "訳: 彼は税法の専門家を装い、顧客に誤った助言をした。  "
          },
          {
            "line": 344,
            "text": "・`pose as someone's assistant`  "
          },
          {
            "line": 345,
            "text": "用途: 他人の助手だと偽って、情報や場所へのアクセスを得ようとすることを表す。  "
          },
          {
            "line": 346,
            "text": "例: The caller posed as the director's assistant and requested confidential files.  "
          },
          {
            "line": 347,
            "text": "訳: その電話の相手は部長の助手を装い、機密ファイルを要求した。  "
          },
          {
            "line": 349,
            "text": "・`pose as a security guard`  "
          },
          {
            "line": 350,
            "text": "用途: 身分を偽っているところを発見・逮捕されることを表す。  "
          },
          {
            "line": 351,
            "text": "例: The suspect was caught posing as a security guard.  "
          },
          {
            "line": 352,
            "text": "訳: その容疑者は警備員を装っていたところを捕まった。  "
          },
          {
            "line": 354,
            "text": "・`pose as a potential buyer`  "
          },
          {
            "line": 355,
            "text": "用途: 実際には購入者ではない人が、購入希望者を装って接近することを表す。  "
          },
          {
            "line": 356,
            "text": "例: Investigators posed as potential buyers to document the illegal sales.  "
          },
          {
            "line": 357,
            "text": "訳: 調査員たちは違法販売を記録するため、購入希望者を装った。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 403,
            "text": "【コロケーション】"
          },
          {
            "line": 405,
            "text": "・`strike a pose`  "
          },
          {
            "line": 406,
            "text": "用途: 特定の印象を与える姿勢を、意識して素早く取ることを表す。比喩的に、態度を演出する意味にもなる。  "
          },
          {
            "line": 407,
            "text": "例: She struck a confident pose before the interview began.  "
          },
          {
            "line": 408,
            "text": "訳: 彼女は面接が始まる前に自信ありげなポーズを取った。  "
          },
          {
            "line": 410,
            "text": "・`hold a pose`  "
          },
          {
            "line": 411,
            "text": "用途: 写真、絵画、ダンス、運動などで、同じ姿勢を一定時間保つことを表す。  "
          },
          {
            "line": 412,
            "text": "例: The dancer held the pose until the music stopped.  "
          },
          {
            "line": 413,
            "text": "訳: そのダンサーは音楽が止まるまでそのポーズを保った。  "
          },
          {
            "line": 415,
            "text": "・`adopt a relaxed pose`  "
          },
          {
            "line": 416,
            "text": "用途: 体の力を抜いた、落ち着いた姿勢を取ることを表す。  "
          },
          {
            "line": 417,
            "text": "例: He adopted a relaxed pose for the family photograph.  "
          },
          {
            "line": 418,
            "text": "訳: 彼は家族写真のためにくつろいだ姿勢を取った。  "
          },
          {
            "line": 420,
            "text": "・`a pose for the camera`  "
          },
          {
            "line": 421,
            "text": "用途: カメラに写ることを目的とした姿勢を表す。  "
          },
          {
            "line": 422,
            "text": "例: The athlete found a dramatic pose for the camera.  "
          },
          {
            "line": 423,
            "text": "訳: その選手はカメラに向けて劇的なポーズを決めた。  "
          },
          {
            "line": 425,
            "text": "・`a yoga/dance pose`  "
          },
          {
            "line": 426,
            "text": "用途: ヨガやダンスで定められた身体の形・姿勢を表す。  "
          },
          {
            "line": 427,
            "text": "例: The instructor demonstrated a difficult yoga pose.  "
          },
          {
            "line": 428,
            "text": "訳: インストラクターは難しいヨガのポーズを実演した。  "
          },
          {
            "line": 430,
            "text": "・`change/try a pose`  "
          },
          {
            "line": 431,
            "text": "用途: 撮影や演技のために、取る姿勢を変えたり別の姿勢を試したりすることを表す。  "
          },
          {
            "line": 432,
            "text": "例: Try a different pose so the light reaches your face.  "
          },
          {
            "line": 433,
            "text": "訳: 光が顔に当たるように、別のポーズを試してみて。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 479,
            "text": "【コロケーション】"
          },
          {
            "line": 481,
            "text": "・`a mere pose`  "
          },
          {
            "line": 482,
            "text": "用途: 表面上の態度が本心ではなく、効果を狙った見せかけにすぎないことを表す。  "
          },
          {
            "line": 483,
            "text": "例: His concern for the workers was a mere pose.  "
          },
          {
            "line": 484,
            "text": "訳: 彼の労働者への心配は、単なる見せかけだった。  "
          },
          {
            "line": 486,
            "text": "・`a pose of confidence`  "
          },
          {
            "line": 487,
            "text": "用途: 本当の自信があるかどうかにかかわらず、自信があるように見せる態度を表す。  "
          },
          {
            "line": 488,
            "text": "例: Her pose of confidence disappeared when the questions became technical.  "
          },
          {
            "line": 489,
            "text": "訳: 質問が専門的になると、彼女の自信ありげな見せかけは消えた。  "
          },
          {
            "line": 491,
            "text": "・`strike a pose of indifference`  "
          },
          {
            "line": 492,
            "text": "用途: 無関心であるかのような態度を意識して作ることを表す。  "
          },
          {
            "line": 493,
            "text": "例: He struck a pose of indifference, although the criticism clearly hurt him.  "
          },
          {
            "line": 494,
            "text": "訳: その批判は明らかに彼を傷つけたが、彼は無関心を装った。  "
          },
          {
            "line": 496,
            "text": "・`a pose as an expert`  "
          },
          {
            "line": 497,
            "text": "用途: 専門家であるかのように見せる、実体を伴わない立場・態度を表す。  "
          },
          {
            "line": 498,
            "text": "例: Her pose as an expert collapsed when she could not explain the basic terms.  "
          },
          {
            "line": 499,
            "text": "訳: 基本用語を説明できなかったため、彼女の専門家を装う態度は崩れた。  "
          },
          {
            "line": 501,
            "text": "・`see through someone's pose`  "
          },
          {
            "line": 502,
            "text": "用途: 人が作っている態度の裏にある本心や実態を見抜くことを表す。  "
          },
          {
            "line": 503,
            "text": "例: The audience quickly saw through the speaker's pose of certainty.  "
          },
          {
            "line": 504,
            "text": "訳: 聴衆はその話者の確信ありげな見せかけをすぐに見抜いた。  "
          },
          {
            "line": 506,
            "text": "・`drop/abandon the pose`  "
          },
          {
            "line": 507,
            "text": "用途: 作っていた態度をやめ、本来の感情や態度を見せることを表す。  "
          },
          {
            "line": 508,
            "text": "例: Once the cameras were gone, she dropped the pose and admitted that she was worried.  "
          },
          {
            "line": 509,
            "text": "訳: カメラがなくなると、彼女は取り繕うのをやめ、心配していたと認めた。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 585,
            "text": "【コロケーション】"
          },
          {
            "line": 587,
            "text": "・`be completely posed by 〈question〉`  "
          },
          {
            "line": 588,
            "text": "用途: 難しい質問に答えられず、すっかり困惑していることを古風・硬く表す。  "
          },
          {
            "line": 589,
            "text": "例: The witness was completely posed by the examiner's final question.  "
          },
          {
            "line": 590,
            "text": "訳: その証人は試験官の最後の質問にすっかり困惑した。  "
          },
          {
            "line": 592,
            "text": "・`a problem that poses 〈person〉`  "
          },
          {
            "line": 593,
            "text": "用途: 人を手こずらせる問題を、低頻度の他動詞用法で表す。  "
          },
          {
            "line": 594,
            "text": "例: The riddle was a problem that posed even the most experienced solver.  "
          },
          {
            "line": 595,
            "text": "訳: そのなぞなぞは、最も経験豊富な解答者さえ手こずらせる問題だった。  "
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
      "input_body_sha256": "ecdf6518adf955d45f677a4e2c5e7d9356b4725cf87db77db64fbf1e69380614",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "米: /poʊz/｜英: /pəʊz/。どちらも1音節で、語末は無声音 /s/ ではなく有声音の /z/ である。米音は二重母音 /oʊ/、英音は二重母音 /əʊ/ で、違いは主に第1音節の母音にある。  "
          },
          {
            "line": 16,
            "text": "三人称単数・複数形の `poses` は米 /ˈpoʊzɪz/・英 /ˈpəʊzɪz/。語末の /z/ に続くため、複数・三単現の語尾は /ɪz/ となる。過去形・過去分詞 `posed` は米 /poʊzd/・英 /pəʊzd/ で、語尾に母音を加えず1音節で発音する。  "
          },
          {
            "line": 17,
            "text": "現在分詞 `posing` は米 /ˈpoʊzɪŋ/・英 /ˈpəʊzɪŋ/。`pose` の語末の e は書かれないが、語幹の /z/ は保たれる。動詞・名詞とも基本形は同じ1音節で、品詞による強勢移動はない。  "
          },
          {
            "line": 18,
            "text": "`pose` /poʊz/（ポーズ）と `pause` /pɔːz/（ポーズ、休止）は、米音でも母音が異なる別語である。  "
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
      "input_body_sha256": "ecdf6518adf955d45f677a4e2c5e7d9356b4725cf87db77db64fbf1e69380614",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "米: /poʊz/｜英: /pəʊz/。どちらも1音節で、語末は無声音 /s/ ではなく有声音の /z/ である。米音は二重母音 /oʊ/、英音は二重母音 /əʊ/ で、違いは主に第1音節の母音にある。  "
          },
          {
            "line": 16,
            "text": "三人称単数・複数形の `poses` は米 /ˈpoʊzɪz/・英 /ˈpəʊzɪz/。語末の /z/ に続くため、複数・三単現の語尾は /ɪz/ となる。過去形・過去分詞 `posed` は米 /poʊzd/・英 /pəʊzd/ で、語尾に母音を加えず1音節で発音する。  "
          },
          {
            "line": 17,
            "text": "現在分詞 `posing` は米 /ˈpoʊzɪŋ/・英 /ˈpəʊzɪŋ/。`pose` の語末の e は書かれないが、語幹の /z/ は保たれる。動詞・名詞とも基本形は同じ1音節で、品詞による強勢移動はない。  "
          },
          {
            "line": 18,
            "text": "`pose` /poʊz/（ポーズ）と `pause` /pɔːz/（ポーズ、休止）は、米音でも母音が異なる別語である。  "
          }
        ],
        "etymology": [
          {
            "line": 20,
            "text": "＃語源"
          },
          {
            "line": 22,
            "text": "中心的な動詞 `pose` は中英語 `posen`、古フランス語 `poser`「置く、位置づける、提案する」を経て、後期ラテン語 `pausare`「止める、休ませる、休止する」に由来する。フランス語の `poser` が「置く」という意味を発達させる過程で、ラテン語 `ponere`「置く」とその過去分詞 `positus` との形の類似・意味上の連想も影響したと説明されるが、`pausare` と `ponere` は本来別語源である。  "
          },
          {
            "line": 23,
            "text": "英語では「特定の位置に置く」から「特定の姿勢を取る・取らせる」へ、さらに「質問や問題を目の前に提示する」「危険や問題を生じさせる」へ用法が広がった。名詞の `pose` はこの動詞から生じ、19世紀初頭には身体の姿勢を表す語として使われていた。  "
          },
          {
            "line": 24,
            "text": "「困惑させる」という別の動詞 `pose` は、古い `appose`／`oppose` の短縮・変形に関係する別系統で、写真や質問を「置く」という中心義から直接派生したものとして扱わない。`pause` は `pausare` を共有する同語源語で、`propose`、`compose`、`expose` などはフランス語の `poser` 系統を含むが、現代英語で `pose` に接頭辞を付けて作った単純な派生語ではない。  "
          }
        ],
        "word_formation": [
          {
            "line": 26,
            "text": "＃語形成"
          },
          {
            "line": 28,
            "text": "`poser` — 名詞「ポーズを取る人、気取り屋」。別系統の困惑義から「難問、手こずらせる問題」という意味も生じる。  "
          },
          {
            "line": 29,
            "text": "`poseur` — 名詞「気取り屋、見せかけの人物」。フランス語由来の語で、実際以上の知識・洗練・所属を装う人を批判的に指す。  "
          },
          {
            "line": 30,
            "text": "`posable/poseable` — 形容詞「ポーズを取らせられる、望む姿勢に置ける」。人形やフィギュアなど、関節を動かして姿勢を作れる物について使うことが多い。  "
          },
          {
            "line": 31,
            "text": "`posing` — 現在分詞・動名詞形で、「ポーズを取っていること」「気取って振る舞うこと」の両方を文脈に応じて表す。  "
          }
        ],
        "core_image": [
          {
            "line": 33,
            "text": "＃コアイメージ"
          },
          {
            "line": 35,
            "text": "`pose` の中心義は、人・物・問い・危険などを、他者が見る・考える・対処する位置へ「置く」ことである。そこから、身体を特定の姿勢に置く用法、質問や問題を検討の前に置く用法、危険を対処すべきものとして生じさせる用法が分かれる。  "
          },
          {
            "line": 36,
            "text": "・危険や困難を対処すべき位置に置く → 「危険・問題を引き起こす」（語義1）  "
          },
          {
            "line": 37,
            "text": "・質問や問題を検討の前に置く → 「質問・問題を提起する」（語義2）  "
          },
          {
            "line": 38,
            "text": "・人や物を見せる姿勢に置く → 「ポーズを取らせる・取る」（語義3）  "
          },
          {
            "line": 39,
            "text": "・自分を人目を引く態度に置く → 「気取って振る舞う」（語義4）  "
          },
          {
            "line": 40,
            "text": "・自分を別人・別の立場として置く → 「〜を装う、なりすます」（語義5）  "
          },
          {
            "line": 41,
            "text": "・身体を置いた姿勢そのもの → 「姿勢、ポーズ」（語義6）  "
          },
          {
            "line": 42,
            "text": "・本心とは別の態度を見せるために置いた姿勢 → 「見せかけの態度」（語義7）  "
          },
          {
            "line": 43,
            "text": "語義8は、古い `appose`／`oppose` に関係する同綴異義の動詞で、語彙的意味がこの「置く」という共通核から導けないため、個別に参照する。  "
          }
        ],
        "sense_structure": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 49,
            "text": "【日本語訳・定義】事物や状況が、誰か・何かにとって対処を要する危険、リスク、問題、困難などを生じさせること。主語が意図的に脅すとは限らず、客観的に「〜という危険をもたらす」「〜の障害となる」と述べる硬めの表現である。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 125,
            "text": "【日本語訳・定義】質問、問題、論点、仮説などを、他者が考えたり議論したりする対象として提示すること。単に発言するより、検討すべき論点を前に置く含みがあり、会議・論文・評論などで使われる。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 196,
            "text": "【日本語訳・定義】人や物を写真、絵画、彫刻、舞台上の構図などに適した姿勢・位置に置くこと。また、人がそのような姿勢を保って写真家や画家のためにポーズを取ること。自分がポーズを取る場合は自動詞、モデルなどに姿勢を取らせる場合は他動詞になる。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 272,
            "text": "【日本語訳・定義】人に良く見せたり、印象づけたりする目的で、自然ではない態度、服装、振る舞いを意識的に演じること。写真撮影のために姿勢を取る語義3と違い、ここでは「気取っている」という批判的な評価が含まれやすい。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 324,
            "text": "【日本語訳・定義】本当はそうではない人や立場であるかのように振る舞い、他人をだますこと。身分を隠して接近する場合や、資格・専門性を持つように見せる場合に使う。単なる遊びの演技にも使えるが、通常は欺きの含みがある。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 395,
            "text": "【日本語訳・定義】人が立つ・座る・体を構えるなどして保つ、特定の身体の姿勢。写真、絵画、彫刻、ダンス、演技、運動などのために意識して取る姿勢を指すことが多いが、写真以外の表現的な姿勢にも使う。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 471,
            "text": "【日本語訳・定義】本当の感情・性格・立場とは別に、他人に特定の印象を与えるために作った態度や人物像。実際にはそう思っていないのに、知的、勇敢、無関心、親切などであるかのように振る舞うことを批判的に表す。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 577,
            "text": "【日本語訳・定義】難しい質問や問題によって、人を困らせて答えに窮させること。現代の一般英語では `puzzle`、`baffle`、`perplex` のほうが普通で、この `pose` は辞書に残る低頻度・硬い用法として理解するとよい。  "
          }
        ],
        "frequency_register": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 51,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 53,
            "text": "【レジスター/領域】標準語。報道、行政、科学、医療、安全管理、ビジネスで特に多い。`threat`、`risk`、`danger` では害の可能性、`problem`、`challenge`、`obstacle` では対処の難しさに焦点が移る。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 127,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 129,
            "text": "【レジスター/領域】標準語・やや硬い表現。会議、研究、教育、評論、報道で広く使う。質問を普通に尋ねる日常会話では `ask`、論点を持ち出す場合は `raise` もよく使う。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 198,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 200,
            "text": "【レジスター/領域】標準語。写真、絵画、広告、ファッション、ダンス、日常の記念撮影で使う。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 274,
            "text": "【頻度】〈5/10〉  "
          },
          {
            "line": 276,
            "text": "【レジスター/領域】標準語・やや否定的。会話、評論、人物描写で使う。しばしば進行形 `be posing` で、目の前で気取って振る舞う様子を描写する。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 326,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 328,
            "text": "【レジスター/領域】標準語。詐欺、犯罪報道、潜入捜査、人物批判、オンライン上の身元偽装で使う。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 397,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 399,
            "text": "【レジスター/領域】標準語。日常会話、写真、芸術、ファッション、ダンス、ヨガ・フィットネスで使う。通常は可算名詞で、`a pose`、`several poses` のように数える。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 473,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 475,
            "text": "【レジスター/領域】標準語・批判的な人物描写。評論、文学、会話、政治・社会的な態度の分析で使う。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 579,
            "text": "【頻度】〈2/10〉  "
          },
          {
            "line": 581,
            "text": "【レジスター/領域】まれ・古風または文語的。古い文章、辞書の用例、硬い人物描写などで見られるが、学習者が自分で使う必要性は低い。語源的にも、語義1〜7の `pose` とは別系統である。  "
          }
        ],
        "frames": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 55,
            "text": "【文法パターン】`〈事物・状況〉 pose a threat/risk/danger to 〈対象〉`＝〈対象〉に危険をもたらす／`〈事物・状況〉 pose a problem/challenge for 〈人・組織〉`＝〈人・組織〉に問題・課題を生じさせる／`pose a hazard/obstacle/barrier to 〈活動・進行〉`＝活動・進行の障害となる  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 131,
            "text": "【文法パターン】`pose a question to 〈person/group〉`＝〈人・集団〉に質問を提起する／`pose the question of whether 〈節〉`＝〜かどうかという問題を提起する／`pose a problem/issue for discussion`＝議論のために問題・論点を提示する／`pose a challenge to 〈theory/assumption〉`＝理論・前提に対する反論となる論点を提示する／`pose a dilemma for 〈decision-maker〉`＝意思決定者に難しい選択を突きつける  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 202,
            "text": "【文法パターン】`pose for 〈photographer/camera/portrait〉`＝写真家・カメラ・肖像画のためにポーズを取る／`pose with/next to/beside 〈person/object〉`＝人・物と一緒にポーズを取る／`pose in 〈position/place〉`＝特定の姿勢・場所でポーズを取る／`pose someone/something for 〈photograph/portrait〉`＝人・物を写真・肖像画のために配置する／`pose a model in 〈position〉`＝モデルを特定の姿勢に置く  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 278,
            "text": "【文法パターン】`pose in 〈clothes/setting〉`＝服装・場面を利用して気取る／`pose to impress 〈people〉`＝人を感心させようとして気取る  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 330,
            "text": "【文法パターン】`pose as 〈名詞〉`＝〜を装う、〜になりすます／`be posing as 〈名詞〉`＝〜を装っている／`a person posing as 〈role〉`＝〜を装う人  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 401,
            "text": "【文法パターン】`adopt/take/strike a pose`＝ポーズを取る／`hold a pose`＝ポーズを保つ／`in a 〈adjective〉 pose`＝〜な姿勢で／`a pose for the camera/portrait`＝カメラ・肖像画のためのポーズ／`change/try a pose`＝ポーズを変える・試す  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 477,
            "text": "【文法パターン】`a mere pose`＝単なる見せかけ／`a pose of 〈quality/emotion〉`＝〜を装う態度／`strike a pose/an attitude of 〈quality〉`＝〜の態度を演じる／`someone's pose as 〈role〉`＝〜を装う人の見せかけ／`see through/drop the pose`＝見せかけを見抜く・やめる  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 583,
            "text": "【文法パターン】`〈難問・問題〉 pose 〈人〉`＝難問が人を困惑させる  "
          }
        ],
        "collocations_examples": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 57,
            "text": "【コロケーション】"
          },
          {
            "line": 59,
            "text": "・`pose a threat to 〈人・動物・環境〉`  "
          },
          {
            "line": 60,
            "text": "用途: 人、動物、環境などに危害を及ぼす可能性があることを表す。  "
          },
          {
            "line": 61,
            "text": "例: The invasive plant poses a serious threat to native species.  "
          },
          {
            "line": 62,
            "text": "訳: その外来植物は在来種に深刻な脅威をもたらしている。  "
          },
          {
            "line": 64,
            "text": "・`pose a risk to 〈health/safety〉`  "
          },
          {
            "line": 65,
            "text": "用途: 健康や安全に悪い結果が生じる可能性を、客観的・説明的に述べる。  "
          },
          {
            "line": 66,
            "text": "例: Long-term exposure to the chemical may pose a risk to workers' health.  "
          },
          {
            "line": 67,
            "text": "訳: その化学物質への長期的な曝露は、作業員の健康にリスクをもたらす可能性がある。  "
          },
          {
            "line": 69,
            "text": "・`pose a danger to 〈人・集団〉`  "
          },
          {
            "line": 70,
            "text": "用途: 具体的な人や集団に危険が及ぶことを表す。  "
          },
          {
            "line": 71,
            "text": "例: The damaged bridge could pose a danger to pedestrians.  "
          },
          {
            "line": 72,
            "text": "訳: 損傷した橋は歩行者に危険を及ぼすおそれがある。  "
          },
          {
            "line": 74,
            "text": "・`pose a problem for 〈person/system〉`  "
          },
          {
            "line": 75,
            "text": "用途: 事物や状況が、誰かや制度に解決すべき問題を生じさせることを表す。  "
          },
          {
            "line": 76,
            "text": "例: The sudden loss of data posed a serious problem for the research team.  "
          },
          {
            "line": 77,
            "text": "訳: 突然のデータ消失は研究チームに深刻な問題をもたらした。  "
          },
          {
            "line": 79,
            "text": "・`pose a challenge to 〈team/plan〉`  "
          },
          {
            "line": 80,
            "text": "用途: 目標達成や作業の進行を難しくする課題を生じさせることを表す。  "
          },
          {
            "line": 81,
            "text": "例: The steep terrain posed a major challenge to the rescue team.  "
          },
          {
            "line": 82,
            "text": "訳: 険しい地形は救助隊に大きな課題を突きつけた。  "
          },
          {
            "line": 84,
            "text": "・`the threat/risk posed by 〈cause〉`  "
          },
          {
            "line": 85,
            "text": "用途: ある原因がもたらす危険や問題を、名詞句の中で説明する。  "
          },
          {
            "line": 86,
            "text": "例: Officials assessed the risks posed by the overloaded electrical system.  "
          },
          {
            "line": 87,
            "text": "訳: 当局は過負荷状態の電気系統がもたらすリスクを評価した。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 133,
            "text": "【コロケーション】"
          },
          {
            "line": 135,
            "text": "・`pose a question to 〈person/group〉`  "
          },
          {
            "line": 136,
            "text": "用途: 相手に、考える価値のある質問を正式に投げかけることを表す。  "
          },
          {
            "line": 137,
            "text": "例: The moderator posed a question to the panel about the cost of reform.  "
          },
          {
            "line": 138,
            "text": "訳: 司会者は改革の費用についてパネリストたちに質問を投げかけた。  "
          },
          {
            "line": 140,
            "text": "・`pose the question of whether 〈節〉`  "
          },
          {
            "line": 141,
            "text": "用途: 「〜かどうか」という論点を、検討すべき問題として提示する。  "
          },
          {
            "line": 142,
            "text": "例: The discovery poses the question of whether the species can survive in warmer seas.  "
          },
          {
            "line": 143,
            "text": "訳: その発見は、その種がより温暖な海で生き残れるのかという問題を提起する。  "
          },
          {
            "line": 145,
            "text": "・`pose a difficult question`  "
          },
          {
            "line": 146,
            "text": "用途: 答えや判断が容易でない質問を提起することを表す。  "
          },
          {
            "line": 147,
            "text": "例: The final chapter poses a difficult question about personal responsibility.  "
          },
          {
            "line": 148,
            "text": "訳: 最終章は、個人の責任について難しい問いを投げかけている。  "
          },
          {
            "line": 150,
            "text": "・`pose a problem for discussion`  "
          },
          {
            "line": 151,
            "text": "用途: 解決・検討すべき問題を議論の場に提示することを表す。  "
          },
          {
            "line": 152,
            "text": "例: The teacher posed a problem for discussion before explaining the formula.  "
          },
          {
            "line": 153,
            "text": "訳: その教師は公式を説明する前に、議論する問題を提示した。  "
          },
          {
            "line": 155,
            "text": "・`pose a challenge to 〈theory/assumption〉`  "
          },
          {
            "line": 156,
            "text": "用途: 新しい証拠や議論が、既存の理論・前提を再検討させる論点になることを表す。  "
          },
          {
            "line": 157,
            "text": "例: The results pose a serious challenge to the assumption that demand is stable.  "
          },
          {
            "line": 158,
            "text": "訳: その結果は、需要は安定しているという前提に重大な疑問を投げかける。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 204,
            "text": "【コロケーション】"
          },
          {
            "line": 206,
            "text": "・`pose for a photograph/portrait`  "
          },
          {
            "line": 207,
            "text": "用途: 写真や肖像画に写るため、一定の姿勢を保つことを表す。  "
          },
          {
            "line": 208,
            "text": "例: The two actors posed for a photograph after the ceremony.  "
          },
          {
            "line": 209,
            "text": "訳: その2人の俳優は式典の後、写真撮影のためにポーズを取った。  "
          },
          {
            "line": 211,
            "text": "・`pose for the camera`  "
          },
          {
            "line": 212,
            "text": "用途: カメラに向けて、撮影されるための姿勢を取ることを表す。  "
          },
          {
            "line": 213,
            "text": "例: The children laughed and posed for the camera.  "
          },
          {
            "line": 214,
            "text": "訳: 子どもたちは笑いながらカメラに向かってポーズを取った。  "
          },
          {
            "line": 216,
            "text": "・`pose with 〈person〉`  "
          },
          {
            "line": 217,
            "text": "用途: 他の人と一緒に写真に写る姿勢を取ることを表す。  "
          },
          {
            "line": 218,
            "text": "例: The award winner posed with her parents backstage.  "
          },
          {
            "line": 219,
            "text": "訳: その受賞者は舞台裏で両親と一緒にポーズを取った。  "
          },
          {
            "line": 221,
            "text": "・`pose beside/next to 〈object/person〉`  "
          },
          {
            "line": 222,
            "text": "用途: 特定の物や人の隣で写真に写ることを表す。  "
          },
          {
            "line": 223,
            "text": "例: The visitors posed beside the old locomotive.  "
          },
          {
            "line": 224,
            "text": "訳: 来場者たちは古い機関車の隣でポーズを取った。  "
          },
          {
            "line": 226,
            "text": "・`pose someone for 〈photograph/portrait〉`  "
          },
          {
            "line": 227,
            "text": "用途: 写真家や画家が、モデルの姿勢や位置を決めて撮影・制作することを表す。  "
          },
          {
            "line": 228,
            "text": "例: The photographer posed the family for a formal portrait.  "
          },
          {
            "line": 229,
            "text": "訳: 写真家は正式な家族写真のために、家族を配置した。  "
          },
          {
            "line": 231,
            "text": "・`pose a model in 〈position〉`  "
          },
          {
            "line": 232,
            "text": "用途: モデルを特定の身体の向きや姿勢に置くことを表す。  "
          },
          {
            "line": 233,
            "text": "例: The artist posed the model in a seated position.  "
          },
          {
            "line": 234,
            "text": "訳: その芸術家はモデルを座った姿勢に置いた。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 280,
            "text": "【コロケーション】"
          },
          {
            "line": 282,
            "text": "・`pose in a designer outfit`  "
          },
          {
            "line": 283,
            "text": "用途: 高価・目立つ服装を見せ、印象づけようとして気取ることを表す。  "
          },
          {
            "line": 284,
            "text": "例: He kept posing in a designer outfit instead of helping with the work.  "
          },
          {
            "line": 285,
            "text": "訳: 彼は仕事を手伝わず、高級な服を着て気取ってばかりいた。  "
          },
          {
            "line": 287,
            "text": "・`pose in 〈car/clothes〉`  "
          },
          {
            "line": 288,
            "text": "用途: 車や服などを見せびらかすように、外で気取って振る舞うことを表す。  "
          },
          {
            "line": 289,
            "text": "例: They were out posing in a rented sports car all afternoon.  "
          },
          {
            "line": 290,
            "text": "訳: 彼らは午後ずっと、借りたスポーツカーを見せびらかして外で気取っていた。  "
          },
          {
            "line": 292,
            "text": "・`pose to impress 〈people〉`  "
          },
          {
            "line": 293,
            "text": "用途: 他人に好印象や威圧感を与えようとして、わざと態度を作ることを表す。  "
          },
          {
            "line": 294,
            "text": "例: She was posing to impress the investors, but the presentation lacked evidence.  "
          },
          {
            "line": 295,
            "text": "訳: 彼女は投資家に好印象を与えようと気取っていたが、発表には根拠が欠けていた。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 332,
            "text": "【コロケーション】"
          },
          {
            "line": 334,
            "text": "・`pose as a doctor/police officer`  "
          },
          {
            "line": 335,
            "text": "用途: 医師や警察官ではない人が、その身分を偽って行動することを表す。  "
          },
          {
            "line": 336,
            "text": "例: The man posed as a doctor to gain access to the restricted ward.  "
          },
          {
            "line": 337,
            "text": "訳: その男は立入制限された病棟に入るため、医師を装った。  "
          },
          {
            "line": 339,
            "text": "・`pose as an expert`  "
          },
          {
            "line": 340,
            "text": "用途: 実際には十分な知識や資格がないのに、専門家のように振る舞うことを表す。  "
          },
          {
            "line": 341,
            "text": "例: He posed as an expert on tax law and gave the client incorrect advice.  "
          },
          {
            "line": 342,
            "text": "訳: 彼は税法の専門家を装い、顧客に誤った助言をした。  "
          },
          {
            "line": 344,
            "text": "・`pose as someone's assistant`  "
          },
          {
            "line": 345,
            "text": "用途: 他人の助手だと偽って、情報や場所へのアクセスを得ようとすることを表す。  "
          },
          {
            "line": 346,
            "text": "例: The caller posed as the director's assistant and requested confidential files.  "
          },
          {
            "line": 347,
            "text": "訳: その電話の相手は部長の助手を装い、機密ファイルを要求した。  "
          },
          {
            "line": 349,
            "text": "・`pose as a security guard`  "
          },
          {
            "line": 350,
            "text": "用途: 身分を偽っているところを発見・逮捕されることを表す。  "
          },
          {
            "line": 351,
            "text": "例: The suspect was caught posing as a security guard.  "
          },
          {
            "line": 352,
            "text": "訳: その容疑者は警備員を装っていたところを捕まった。  "
          },
          {
            "line": 354,
            "text": "・`pose as a potential buyer`  "
          },
          {
            "line": 355,
            "text": "用途: 実際には購入者ではない人が、購入希望者を装って接近することを表す。  "
          },
          {
            "line": 356,
            "text": "例: Investigators posed as potential buyers to document the illegal sales.  "
          },
          {
            "line": 357,
            "text": "訳: 調査員たちは違法販売を記録するため、購入希望者を装った。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 403,
            "text": "【コロケーション】"
          },
          {
            "line": 405,
            "text": "・`strike a pose`  "
          },
          {
            "line": 406,
            "text": "用途: 特定の印象を与える姿勢を、意識して素早く取ることを表す。比喩的に、態度を演出する意味にもなる。  "
          },
          {
            "line": 407,
            "text": "例: She struck a confident pose before the interview began.  "
          },
          {
            "line": 408,
            "text": "訳: 彼女は面接が始まる前に自信ありげなポーズを取った。  "
          },
          {
            "line": 410,
            "text": "・`hold a pose`  "
          },
          {
            "line": 411,
            "text": "用途: 写真、絵画、ダンス、運動などで、同じ姿勢を一定時間保つことを表す。  "
          },
          {
            "line": 412,
            "text": "例: The dancer held the pose until the music stopped.  "
          },
          {
            "line": 413,
            "text": "訳: そのダンサーは音楽が止まるまでそのポーズを保った。  "
          },
          {
            "line": 415,
            "text": "・`adopt a relaxed pose`  "
          },
          {
            "line": 416,
            "text": "用途: 体の力を抜いた、落ち着いた姿勢を取ることを表す。  "
          },
          {
            "line": 417,
            "text": "例: He adopted a relaxed pose for the family photograph.  "
          },
          {
            "line": 418,
            "text": "訳: 彼は家族写真のためにくつろいだ姿勢を取った。  "
          },
          {
            "line": 420,
            "text": "・`a pose for the camera`  "
          },
          {
            "line": 421,
            "text": "用途: カメラに写ることを目的とした姿勢を表す。  "
          },
          {
            "line": 422,
            "text": "例: The athlete found a dramatic pose for the camera.  "
          },
          {
            "line": 423,
            "text": "訳: その選手はカメラに向けて劇的なポーズを決めた。  "
          },
          {
            "line": 425,
            "text": "・`a yoga/dance pose`  "
          },
          {
            "line": 426,
            "text": "用途: ヨガやダンスで定められた身体の形・姿勢を表す。  "
          },
          {
            "line": 427,
            "text": "例: The instructor demonstrated a difficult yoga pose.  "
          },
          {
            "line": 428,
            "text": "訳: インストラクターは難しいヨガのポーズを実演した。  "
          },
          {
            "line": 430,
            "text": "・`change/try a pose`  "
          },
          {
            "line": 431,
            "text": "用途: 撮影や演技のために、取る姿勢を変えたり別の姿勢を試したりすることを表す。  "
          },
          {
            "line": 432,
            "text": "例: Try a different pose so the light reaches your face.  "
          },
          {
            "line": 433,
            "text": "訳: 光が顔に当たるように、別のポーズを試してみて。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 479,
            "text": "【コロケーション】"
          },
          {
            "line": 481,
            "text": "・`a mere pose`  "
          },
          {
            "line": 482,
            "text": "用途: 表面上の態度が本心ではなく、効果を狙った見せかけにすぎないことを表す。  "
          },
          {
            "line": 483,
            "text": "例: His concern for the workers was a mere pose.  "
          },
          {
            "line": 484,
            "text": "訳: 彼の労働者への心配は、単なる見せかけだった。  "
          },
          {
            "line": 486,
            "text": "・`a pose of confidence`  "
          },
          {
            "line": 487,
            "text": "用途: 本当の自信があるかどうかにかかわらず、自信があるように見せる態度を表す。  "
          },
          {
            "line": 488,
            "text": "例: Her pose of confidence disappeared when the questions became technical.  "
          },
          {
            "line": 489,
            "text": "訳: 質問が専門的になると、彼女の自信ありげな見せかけは消えた。  "
          },
          {
            "line": 491,
            "text": "・`strike a pose of indifference`  "
          },
          {
            "line": 492,
            "text": "用途: 無関心であるかのような態度を意識して作ることを表す。  "
          },
          {
            "line": 493,
            "text": "例: He struck a pose of indifference, although the criticism clearly hurt him.  "
          },
          {
            "line": 494,
            "text": "訳: その批判は明らかに彼を傷つけたが、彼は無関心を装った。  "
          },
          {
            "line": 496,
            "text": "・`a pose as an expert`  "
          },
          {
            "line": 497,
            "text": "用途: 専門家であるかのように見せる、実体を伴わない立場・態度を表す。  "
          },
          {
            "line": 498,
            "text": "例: Her pose as an expert collapsed when she could not explain the basic terms.  "
          },
          {
            "line": 499,
            "text": "訳: 基本用語を説明できなかったため、彼女の専門家を装う態度は崩れた。  "
          },
          {
            "line": 501,
            "text": "・`see through someone's pose`  "
          },
          {
            "line": 502,
            "text": "用途: 人が作っている態度の裏にある本心や実態を見抜くことを表す。  "
          },
          {
            "line": 503,
            "text": "例: The audience quickly saw through the speaker's pose of certainty.  "
          },
          {
            "line": 504,
            "text": "訳: 聴衆はその話者の確信ありげな見せかけをすぐに見抜いた。  "
          },
          {
            "line": 506,
            "text": "・`drop/abandon the pose`  "
          },
          {
            "line": 507,
            "text": "用途: 作っていた態度をやめ、本来の感情や態度を見せることを表す。  "
          },
          {
            "line": 508,
            "text": "例: Once the cameras were gone, she dropped the pose and admitted that she was worried.  "
          },
          {
            "line": 509,
            "text": "訳: カメラがなくなると、彼女は取り繕うのをやめ、心配していたと認めた。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 585,
            "text": "【コロケーション】"
          },
          {
            "line": 587,
            "text": "・`be completely posed by 〈question〉`  "
          },
          {
            "line": 588,
            "text": "用途: 難しい質問に答えられず、すっかり困惑していることを古風・硬く表す。  "
          },
          {
            "line": 589,
            "text": "例: The witness was completely posed by the examiner's final question.  "
          },
          {
            "line": 590,
            "text": "訳: その証人は試験官の最後の質問にすっかり困惑した。  "
          },
          {
            "line": 592,
            "text": "・`a problem that poses 〈person〉`  "
          },
          {
            "line": 593,
            "text": "用途: 人を手こずらせる問題を、低頻度の他動詞用法で表す。  "
          },
          {
            "line": 594,
            "text": "例: The riddle was a problem that posed even the most experienced solver.  "
          },
          {
            "line": 595,
            "text": "訳: そのなぞなぞは、最も経験豊富な解答者さえ手こずらせる問題だった。  "
          }
        ],
        "usage_notes": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 89,
            "text": "【語法・注意】`pose` はこの用法では通常、主語に危険や問題を生じさせる事物・状況を置き、危険の受け手は `to`、問題の受け手は `for` で示す。`*pose someone a threat` とせず、`pose a threat to someone` とする。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 160,
            "text": "【語法・注意】この用法の `pose` は、質問や問題を検討の前に置く表現で、`ask` より形式的である。`raise a question` は疑問や論点を持ち出すこと、`propose` は計画・案を提案することに重点がある。`pose a problem` は語義1の「問題を引き起こす」と形が同じなので、`for discussion` や議論を行う主語があれば語義2、被害や障害を受ける対象があれば語義1と判断しやすい。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 236,
            "text": "【語法・注意】自分が姿勢を取るときは `She posed for the camera.` のように目的語を置かない。撮影者がモデルを配置するときは `The photographer posed her for the portrait.` のように人を目的語にする。`pose with` は「〜と一緒に写る」であり、必ずしも特別に気取った姿勢を意味しない。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 297,
            "text": "【語法・注意】この用法の `pose` は、単に写真のためにポーズを取ることではない。写真撮影の文脈で `pose for the camera` と言えば通常は中立的な語義3だが、`pose in an expensive car`、`be posing to impress` のように見せびらかしや人工的な態度が焦点になると語義4になる。`show off` は能力・所有物などを誇示すること、`pose` は態度や人物像を作って見せることに焦点がある。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 359,
            "text": "【語法・注意】`pose as` の `as` は省略できず、後ろには通常、人物・役割・組織などを表す名詞句を置く。`*pose to be a doctor` ではなく、`pose as a doctor` または `pretend to be a doctor` とする。`pretend to be` は冗談や子どものごっこにも使えるが、`pose as` は身元や資格を偽って人を欺く場面に結びつきやすい。`impersonate` は特定の人物や公的役割になりすます行為そのものに焦点があり、`pose as` はその立場を装って相手を欺く文脈を強く示す。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 435,
            "text": "【語法・注意】`pose` は通常 `a pose` と数え、`three different poses` のように複数形にできる。`posture` は普段の体の構えや健康上の姿勢、`position` は身体に限らない位置全般、`stance` は立ち方に加えて意見・立場も表す。したがって「姿勢が悪い」という一般的な身体状態には `bad posture` が自然で、撮影で一時的に取る姿勢には `a pose` が自然である。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 511,
            "text": "【語法・注意】この名詞の `pose` は、単なる意見や態度を中立的に表す `attitude` と異なり、人工的に作られた印象という含みを持つ。`affectation` は話し方や仕草などの不自然な気取り、`pretense` は事実・感情・身分などを偽る見せかけ全般を表す。身体の姿勢なら語義6であり、`a relaxed pose` は通常、批判的な「見せかけ」ではない。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 597,
            "text": "【語法・注意】この意味の `pose` は、写真の姿勢、質問の提起、危険の発生とは別の語義である。`The question posed him` のように人を直接目的語に取る形は現代では非常にまれで、通常は `The question puzzled him.` や `He was baffled by the question.` と言う。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 47,
            "text": "1. 【動詞・他動詞】危険・問題・課題などを引き起こす、もたらす"
          },
          {
            "line": 93,
            "text": "【類義語】"
          },
          {
            "line": 95,
            "text": "・create  "
          },
          {
            "line": 96,
            "text": "定義: 何かを新たに生じさせる。  "
          },
          {
            "line": 97,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 98,
            "text": "違い: `create` は結果を生じさせること全般を表す広い語で、`pose` のように危険・問題を対処対象として提示する硬い含みはない。  "
          },
          {
            "line": 99,
            "text": "例: The change created additional work for the accounting team.  "
          },
          {
            "line": 100,
            "text": "訳: その変更は経理チームに追加の作業を生じさせた。  "
          },
          {
            "line": 102,
            "text": "・present  "
          },
          {
            "line": 103,
            "text": "定義: 問題、機会、危険などを人の前に現れさせる、または直面させる。  "
          },
          {
            "line": 104,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 105,
            "text": "違い: `present` は危険に限らず、状況や機会を提示する中立的な語である。`pose` は特に対処を要する問題・リスクとの結びつきが強い。  "
          },
          {
            "line": 106,
            "text": "例: The new evidence presents a difficulty for the proposed explanation.  "
          },
          {
            "line": 107,
            "text": "訳: 新しい証拠は、提案された説明に難点をもたらす。  "
          },
          {
            "line": 109,
            "text": "・constitute  "
          },
          {
            "line": 110,
            "text": "定義: 全体として、ある危険・問題・脅威に当たる。  "
          },
          {
            "line": 111,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 112,
            "text": "違い: `constitute` は「それ自体が〜である」という分類・評価に焦点があり、`pose` は誰かにとって危険や問題を生じさせる関係に焦点がある。  "
          },
          {
            "line": 113,
            "text": "例: The leak constitutes a serious violation of the safety rules.  "
          },
          {
            "line": 114,
            "text": "訳: その漏えいは安全規則への重大な違反に当たる。  "
          },
          {
            "line": 116,
            "text": "・threaten  "
          },
          {
            "line": 117,
            "text": "定義: 危害や不利益を及ぼすおそれがある、または脅す。  "
          },
          {
            "line": 118,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 119,
            "text": "違い: `threaten` は危険の切迫性や、場合によっては意図的な脅しを強く示す。`pose` は自然現象や制度上の問題にも使う客観的な表現である。  "
          },
          {
            "line": 120,
            "text": "例: Rising sea levels threaten coastal communities.  "
          },
          {
            "line": 121,
            "text": "訳: 海面上昇は沿岸地域社会を脅かしている。  "
          },
          {
            "line": 123,
            "text": "2. 【動詞・他動詞・やや硬い】質問・問題・仮説などを提起する、提示する"
          },
          {
            "line": 164,
            "text": "【類義語】"
          },
          {
            "line": 166,
            "text": "・ask  "
          },
          {
            "line": 167,
            "text": "定義: 答えや情報を求めて質問する。  "
          },
          {
            "line": 168,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 169,
            "text": "違い: `ask` は日常会話から正式な場面まで使える基本語で、`pose` よりも「相手から答えを求める行為」に焦点がある。  "
          },
          {
            "line": 170,
            "text": "例: I asked the manager whether the deadline could be extended.  "
          },
          {
            "line": 171,
            "text": "訳: 私は締め切りを延ばせるかどうかマネージャーに尋ねた。  "
          },
          {
            "line": 173,
            "text": "・raise  "
          },
          {
            "line": 174,
            "text": "定義: 問題、疑問、懸念などを話題として持ち出す。  "
          },
          {
            "line": 175,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 176,
            "text": "違い: `raise a question/issue` は論点を会議や議論に持ち込むことに重点があり、`pose` は問いを検討対象として組み立てて提示する含みがある。  "
          },
          {
            "line": 177,
            "text": "例: Several members raised concerns about the new procedure.  "
          },
          {
            "line": 178,
            "text": "訳: 何人かのメンバーが新しい手続きについて懸念を提起した。  "
          },
          {
            "line": 180,
            "text": "・put forward  "
          },
          {
            "line": 181,
            "text": "定義: 考え、提案、議論などを検討のために提示する。  "
          },
          {
            "line": 182,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 183,
            "text": "違い: `put forward` は質問に限らず、案や意見を明示的に提示する句動詞である。`pose` は問い・問題を前に置く表現として硬く響きやすい。  "
          },
          {
            "line": 184,
            "text": "例: The committee put forward three alternatives for reducing costs.  "
          },
          {
            "line": 185,
            "text": "訳: 委員会は費用を削減するための3つの代案を提示した。  "
          },
          {
            "line": 187,
            "text": "・propose  "
          },
          {
            "line": 188,
            "text": "定義: 計画、案、説明などを採用候補として提案する。  "
          },
          {
            "line": 189,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 190,
            "text": "違い: `propose` は実行・採用を期待する案を示すことが多い。`pose a question` は、答えや議論を求める問いを置く表現である。  "
          },
          {
            "line": 191,
            "text": "例: The engineer proposed a simpler design for the device.  "
          },
          {
            "line": 192,
            "text": "訳: その技術者は装置のより簡単な設計を提案した。  "
          },
          {
            "line": 194,
            "text": "3. 【動詞・他動詞／自動詞】（撮影・絵画のために）人・物を特定の位置に置く／自分がポーズを取る"
          },
          {
            "line": 240,
            "text": "【類義語】"
          },
          {
            "line": 242,
            "text": "・position  "
          },
          {
            "line": 243,
            "text": "定義: 人や物を特定の場所・位置に意図的に置く。  "
          },
          {
            "line": 244,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 245,
            "text": "違い: `position` は配置そのものに焦点があり、写真や芸術のために身体の姿勢を作る含みは `pose` ほど強くない。  "
          },
          {
            "line": 246,
            "text": "例: The nurse positioned the lamp beside the examination table.  "
          },
          {
            "line": 247,
            "text": "訳: 看護師は診察台のそばにランプを配置した。  "
          },
          {
            "line": 249,
            "text": "・arrange  "
          },
          {
            "line": 250,
            "text": "定義: 人や物を、見た目や目的に合うように整えて配置する。  "
          },
          {
            "line": 251,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 252,
            "text": "違い: `arrange` は複数の人・物の全体的な並べ方を表す。`pose` は特にモデルの身体の向きや姿勢を決める。  "
          },
          {
            "line": 253,
            "text": "例: The assistant arranged the flowers around the sculpture.  "
          },
          {
            "line": 254,
            "text": "訳: アシスタントは彫刻の周りに花を配置した。  "
          },
          {
            "line": 256,
            "text": "・model  "
          },
          {
            "line": 257,
            "text": "定義: 芸術家のために座ったり立ったりして、作品のモデルを務める。  "
          },
          {
            "line": 258,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 259,
            "text": "違い: `model` は描く側のためにポーズを保つ役割を表し、`pose` のように特定の姿勢を取る行為一般を表すわけではない。  "
          },
          {
            "line": 260,
            "text": "例: She modeled for a sculptor during the winter.  "
          },
          {
            "line": 261,
            "text": "訳: 彼女は冬の間、彫刻家のモデルを務めた。  "
          },
          {
            "line": 263,
            "text": "・sit/stand for 〈artist/photographer〉  "
          },
          {
            "line": 264,
            "text": "定義: 画家や写真家のために座ったり立ったりして姿勢を保つ。  "
          },
          {
            "line": 265,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 266,
            "text": "違い: `sit/stand for` は実際の姿勢とその持続を具体的に述べる句で、`pose` よりも動作の種類が限定される。  "
          },
          {
            "line": 267,
            "text": "例: The child stood for the painter for nearly an hour.  "
          },
          {
            "line": 268,
            "text": "訳: その子どもは1時間近く画家のために立っていた。  "
          },
          {
            "line": 270,
            "text": "4. 【動詞・自動詞・通例進行形・軽蔑的】人目を引くために気取った態度・格好をする"
          },
          {
            "line": 299,
            "text": "【類義語】"
          },
          {
            "line": 301,
            "text": "・posture  "
          },
          {
            "line": 302,
            "text": "定義: 特定の態度や立場を、しばしば実際以上に強く見せるように取る。  "
          },
          {
            "line": 303,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 304,
            "text": "違い: 動詞 `posture` は政治・交渉などで強硬な立場を演じる用法が目立つ。`pose` は服装、態度、人物像を気取って見せる一般的な含みが強い。  "
          },
          {
            "line": 305,
            "text": "例: The two sides postured during the negotiations but later reached an agreement.  "
          },
          {
            "line": 306,
            "text": "訳: 両陣営は交渉中は強硬姿勢を演じたが、後に合意に達した。  "
          },
          {
            "line": 308,
            "text": "・affect  "
          },
          {
            "line": 309,
            "text": "定義: 自然ではない話し方、態度、感情などを意図的に身につけて見せる。  "
          },
          {
            "line": 310,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 311,
            "text": "違い: `affect` は人工的な声・アクセント・態度そのものを作ることに焦点があり、`pose` より硬く、対象が限定されやすい。  "
          },
          {
            "line": 312,
            "text": "例: He affected a calm manner even though he was nervous.  "
          },
          {
            "line": 313,
            "text": "訳: 彼は緊張していたが、平静な態度を装った。  "
          },
          {
            "line": 315,
            "text": "・show off  "
          },
          {
            "line": 316,
            "text": "定義: 能力、所有物、外見などを目立つように示して自慢する。  "
          },
          {
            "line": 317,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 318,
            "text": "違い: `show off` は誇示する行為を直接表す口語である。`pose` は何かを見せるだけでなく、特定の人物像や態度を演出する点を強調する。  "
          },
          {
            "line": 319,
            "text": "例: The teenager was showing off his new motorcycle.  "
          },
          {
            "line": 320,
            "text": "訳: その10代の若者は新しいオートバイを見せびらかしていた。  "
          },
          {
            "line": 322,
            "text": "5. 【動詞・pose as + 名詞構文】（人・資格・立場など）を装う、〜になりすます"
          },
          {
            "line": 363,
            "text": "【類義語】"
          },
          {
            "line": 365,
            "text": "・pretend to be 〈someone/something〉  "
          },
          {
            "line": 366,
            "text": "定義: 本当はそうではない人・物であるふりをする。  "
          },
          {
            "line": 367,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 368,
            "text": "違い: `pretend to be` は遊び、冗談、想像、欺きのすべてに使える最も広い表現で、必ずしも実害のある偽装を示さない。  "
          },
          {
            "line": 369,
            "text": "例: The children pretended to be astronauts during the game.  "
          },
          {
            "line": 370,
            "text": "訳: 子どもたちは遊びの間、宇宙飛行士のふりをした。  "
          },
          {
            "line": 372,
            "text": "・impersonate 〈person/official〉  "
          },
          {
            "line": 373,
            "text": "定義: 特定の人物や公的役割の話し方・身分などをまねて本人のように振る舞う。  "
          },
          {
            "line": 374,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 375,
            "text": "違い: `impersonate` は本人の身元や役割の再現に焦点があり、詐欺・違法行為の文脈で使われやすい。`pose as` はより広く、専門家や購入者などの立場を装う場合にも使う。  "
          },
          {
            "line": 376,
            "text": "例: The caller was charged with impersonating a government official.  "
          },
          {
            "line": 377,
            "text": "訳: その電話の発信者は政府職員になりすましたとして起訴された。  "
          },
          {
            "line": 379,
            "text": "・pass oneself off as 〈someone/something〉  "
          },
          {
            "line": 380,
            "text": "定義: 本当はそうではないのに、他人にそうだと信じさせる。  "
          },
          {
            "line": 381,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 382,
            "text": "違い: `pass oneself off as` は相手に本物だと認めさせようとする欺きの含みが特に強い。`pose as` よりも「見破られずに通す」点に焦点がある。  "
          },
          {
            "line": 383,
            "text": "例: He passed himself off as a qualified electrician.  "
          },
          {
            "line": 384,
            "text": "訳: 彼は資格のある電気技師だと偽って通した。  "
          },
          {
            "line": 386,
            "text": "・masquerade as 〈someone/something〉  "
          },
          {
            "line": 387,
            "text": "定義: 別の人・物・立場を装う。  "
          },
          {
            "line": 388,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 389,
            "text": "違い: `masquerade as` は仮面をかぶるような明白な偽装や、実体を隠す比喩に使われ、`pose as` より文語的・劇的に響くことがある。  "
          },
          {
            "line": 390,
            "text": "例: The website masqueraded as an official public-service portal.  "
          },
          {
            "line": 391,
            "text": "訳: そのウェブサイトは公式の行政サービス窓口を装っていた。  "
          },
          {
            "line": 393,
            "text": "6. 【名詞・可算】（写真・絵画・演技などの）姿勢、ポーズ"
          },
          {
            "line": 439,
            "text": "【類義語】"
          },
          {
            "line": 441,
            "text": "・posture  "
          },
          {
            "line": 442,
            "text": "定義: 体の位置や構え、またはその人に特徴的な体の保ち方。  "
          },
          {
            "line": 443,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 444,
            "text": "違い: `posture` は習慣的な姿勢や身体の配列に焦点がある。`pose` は特定の場面で意識して取る一時的・表現的な姿勢に焦点がある。  "
          },
          {
            "line": 445,
            "text": "例: Good posture can reduce strain on the neck.  "
          },
          {
            "line": 446,
            "text": "訳: 良い姿勢は首への負担を減らせる。  "
          },
          {
            "line": 448,
            "text": "・stance  "
          },
          {
            "line": 449,
            "text": "定義: 立っているときの足や体の構え、または意見・立場。  "
          },
          {
            "line": 450,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 451,
            "text": "違い: 身体についての `stance` は安定性や構えを強調し、`pose` のような撮影・演出の含みは弱い。比喩的な意見の意味は `pose` より広く定着している。  "
          },
          {
            "line": 452,
            "text": "例: The boxer changed his stance before the next round.  "
          },
          {
            "line": 453,
            "text": "訳: そのボクサーは次のラウンドの前に構えを変えた。  "
          },
          {
            "line": 455,
            "text": "・position  "
          },
          {
            "line": 456,
            "text": "定義: 人や物が置かれている場所・向き・状態。  "
          },
          {
            "line": 457,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 458,
            "text": "違い: `position` は「どこにあるか」という中立的な位置を指す。`pose` は身体を見せるために取る姿勢や、その姿勢が作る印象を含みやすい。  "
          },
          {
            "line": 459,
            "text": "例: The camera records the exact position of each joint.  "
          },
          {
            "line": 460,
            "text": "訳: そのカメラは各関節の正確な位置を記録する。  "
          },
          {
            "line": 462,
            "text": "・attitude  "
          },
          {
            "line": 463,
            "text": "定義: 体の構え、または人・物事に対する心理的な態度。  "
          },
          {
            "line": 464,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 465,
            "text": "違い: 身体の意味の `attitude` はやや専門的・芸術的で、日常の写真の姿勢には `pose` が普通である。心理的な態度を表す場合は、`pose` と違って本心に反する見せかけを必ずしも含まない。  "
          },
          {
            "line": 466,
            "text": "例: The sculpture has an attitude of quiet movement.  "
          },
          {
            "line": 467,
            "text": "訳: その彫刻には静かな動きを感じさせる姿勢がある。  "
          },
          {
            "line": 469,
            "text": "7. 【名詞・可算・しばしば軽蔑的】見せかけの態度、気取ったふるまい、ポーズ"
          },
          {
            "line": 515,
            "text": "【類義語】"
          },
          {
            "line": 517,
            "text": "・affectation  "
          },
          {
            "line": 518,
            "text": "定義: 他人に良く見せようとして作る、不自然でわざとらしい話し方や態度。  "
          },
          {
            "line": 519,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 520,
            "text": "違い: `affectation` は特定の仕草、発音、言葉遣いなどの不自然さを指しやすい。`pose` はより広く、人物全体の役割や立場を演出することも表す。  "
          },
          {
            "line": 521,
            "text": "例: Her exaggerated accent was an affectation.  "
          },
          {
            "line": 522,
            "text": "訳: 彼女の大げさなアクセントは、わざとらしい気取りだった。  "
          },
          {
            "line": 524,
            "text": "・pretense  "
          },
          {
            "line": 525,
            "text": "定義: 本当ではないものを本当らしく見せること、またはその見せかけ。  "
          },
          {
            "line": 526,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 527,
            "text": "違い: `pretense` は事実、感情、身分などの偽装全般を表す。`pose` は特に人目を意識して作る態度・人物像に焦点がある。  "
          },
          {
            "line": 528,
            "text": "例: His pretense of being calm did not convince anyone.  "
          },
          {
            "line": 529,
            "text": "訳: 彼が冷静なふりをしても、誰も納得しなかった。  "
          },
          {
            "line": 531,
            "text": "・front  "
          },
          {
            "line": 532,
            "text": "定義: 本当の感情や弱さを隠すために外向きに見せる態度。  "
          },
          {
            "line": 533,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 534,
            "text": "違い: `front` は防御・隠蔽のための外面に焦点がある。`pose` は防御に限らず、印象を良くしたり優位に見せたりする演出にも使う。  "
          },
          {
            "line": 535,
            "text": "例: His cheerful manner was a front for his anxiety.  "
          },
          {
            "line": 536,
            "text": "訳: 彼の陽気な態度は不安を隠すための外面だった。  "
          },
          {
            "line": 538,
            "text": "・act  "
          },
          {
            "line": 539,
            "text": "定義: 本心とは異なる感情や人物を演じること。  "
          },
          {
            "line": 540,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 541,
            "text": "違い: `act` は演技一般を表す口語的な語で、舞台上の演技にも使える。`pose` は短い態度や見せかけを批判的に指しやすい。  "
          },
          {
            "line": 542,
            "text": "例: His apology sounded like an act rather than a sincere admission.  "
          },
          {
            "line": 543,
            "text": "訳: 彼の謝罪は、誠実な認め方というより演技のように聞こえた。  "
          },
          {
            "line": 545,
            "text": "・airs  "
          },
          {
            "line": 546,
            "text": "定義: 実際以上に洗練され、重要であるかのように振る舞う気取り。  "
          },
          {
            "line": 547,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 548,
            "text": "違い: `airs` は上品さや優越感を誇示する含みが強い複数形の表現である。`pose` は優越感に限らず、勇気・無関心・専門性など任意の態度を装える。  "
          },
          {
            "line": 549,
            "text": "例: She puts on airs whenever senior managers enter the room.  "
          },
          {
            "line": 550,
            "text": "訳: 彼女は上級管理職が部屋に入ると、いつも気取った態度を取る。  "
          },
          {
            "line": 552,
            "text": "【反意語】"
          },
          {
            "line": 554,
            "text": "・sincerity  "
          },
          {
            "line": 555,
            "text": "定義: 本心から出た感情や態度で、見せかけでないこと。  "
          },
          {
            "line": 556,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 557,
            "text": "違い: `sincerity` は、効果を狙って作った `pose` と反対に、言動が本心に基づくことを表す。  "
          },
          {
            "line": 558,
            "text": "例: The sincerity of her apology was clear from her actions.  "
          },
          {
            "line": 559,
            "text": "訳: 彼女の謝罪が誠実なものだということは、行動から明らかだった。  "
          },
          {
            "line": 561,
            "text": "・authenticity  "
          },
          {
            "line": 562,
            "text": "定義: 人の感情・態度・作品などが本物で、作為的でないこと。  "
          },
          {
            "line": 563,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 564,
            "text": "違い: `authenticity` は「本物らしさ・本来の自分らしさ」を強調し、`pose` の人工的に作った人物像と対立する。  "
          },
          {
            "line": 565,
            "text": "例: The singer's authenticity mattered more to the audience than her image.  "
          },
          {
            "line": 566,
            "text": "訳: その歌手の本物らしさは、イメージよりも聴衆にとって重要だった。  "
          },
          {
            "line": 568,
            "text": "・genuineness  "
          },
          {
            "line": 569,
            "text": "定義: 感情や態度が偽りなく、本心から出ていること。  "
          },
          {
            "line": 570,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 571,
            "text": "違い: `genuineness` は個々の感情・反応が本物であることを表し、他人に見せるために作られた `pose` と反対の性質である。  "
          },
          {
            "line": 572,
            "text": "例: The genuineness of his surprise was obvious.  "
          },
          {
            "line": 573,
            "text": "訳: 彼の驚きが本物であることは明らかだった。  "
          },
          {
            "line": 575,
            "text": "8. 【動詞・他動詞・まれ・古風】（人を）困惑させる、手こずらせる"
          },
          {
            "line": 599,
            "text": "【類義語】"
          },
          {
            "line": 601,
            "text": "・puzzle  "
          },
          {
            "line": 602,
            "text": "定義: 問題や状況が人を困惑させ、理解や解決を難しくする。  "
          },
          {
            "line": 603,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 604,
            "text": "違い: `puzzle` は現代英語で自然な一般語で、好奇心を刺激する軽い困惑にも、解けない問題にも使える。  "
          },
          {
            "line": 605,
            "text": "例: The unexpected result puzzled the researchers.  "
          },
          {
            "line": 606,
            "text": "訳: 予想外の結果は研究者たちを困惑させた。  "
          },
          {
            "line": 608,
            "text": "・baffle  "
          },
          {
            "line": 609,
            "text": "定義: 難しさや不可解さによって、完全に困らせる。  "
          },
          {
            "line": 610,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 611,
            "text": "違い: `baffle` は `puzzle` より困惑の程度が強く、答えや説明が見つからない含みがある。  "
          },
          {
            "line": 612,
            "text": "例: The strange pattern baffled the police.  "
          },
          {
            "line": 613,
            "text": "訳: その奇妙なパターンは警察を困惑させた。  "
          },
          {
            "line": 615,
            "text": "・perplex  "
          },
          {
            "line": 616,
            "text": "定義: 複雑な問題や矛盾によって、深く困惑させる。  "
          },
          {
            "line": 617,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 618,
            "text": "違い: `perplex` は `puzzle` より文語的で、考えを整理できない深い困惑を表しやすい。  "
          },
          {
            "line": 619,
            "text": "例: The contradictory instructions perplexed the new employees.  "
          },
          {
            "line": 620,
            "text": "訳: 矛盾した指示は新入社員たちを困惑させた。  "
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
