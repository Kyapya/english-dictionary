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


# check_pass_frame_relation_v7

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

## 4. 反意語対立軸の2段階ブラインド検査

各語義ブロックの `【反意語】` 欄にある全アイテムを対象とする。同じ反意語が複数語義に現れる場合も語義ごとに独立して判定する。類義語・反意語欄内の例文は対象外であり、反意語欄が存在しないことは正常な完成状態なのでfindingを出さない。

### 4.1 段階1: ブラインド軸命名

段階1では `antonym_axis_blind_request_v1` だけを受け取る。各アイテムに開示されるのは、見出し語、当該語義の `【日本語訳・定義】` 全文、反意語の語、反意語の `定義:` 行だけである。`違い:` 行、`頻度:` 行、`例:` 行、`訳:` 行、類義語欄全体、コアイメージ、他語義の情報を参照してはならない。アイテムはrun別の不透明IDを持ち、shuffleされた順で提示される。

各アイテムについて次を記録する。

1. 二語が対立する意味軸を名詞一語で命名する。複合語は可とするが、「〜の度合い」などの説明句は不可とする。
2. 対立型を `補完 | 程度 | 方向 | 評価 | 状態` のいずれか一つに分類する。
3. 軸を命名できない場合は軸を `unnamable` とし、対立型を空値にして、理由を一文で述べる。

回答は `antonym_axis_blind_record_v1` として確定・保存する。調整役は、この記録の保存、request hash照合、全不透明IDの被覆を確認するまで段階2入力を作成・開示してはならない。

段階1では次のJSON形を返す。`input_body_sha256`、`blind_request_sha256`、`recorded_at`、`reviewer` は調整役が実際のrequestと保存時刻から封印するメタデータであり、判定者は `axes` の内容を作成する。

```json
{
  "schema_version": "antonym_axis_blind_record_v1",
  "pass_id": "frame-relation",
  "input_body_sha256": "stage 1 requestの値",
  "blind_request_sha256": "stage 1 request全体のsha256",
  "recorded_at": "aware ISO-8601 timestamp",
  "reviewer": {},
  "axes": [
    {
      "item_id": "ant-opaque-id",
      "axis": "名詞一語 | unnamable",
      "relation_type": "補完 | 程度 | 方向 | 評価 | 状態 | null",
      "reason": "unnamableの場合は必須の一文理由"
    }
  ]
}
```

### 4.2 段階2: 照合・裁定

段階1記録の封印後に限り、当該語義の全文（`違い:` 行と類義語欄を含む）を開示する。段階1で命名した軸と型を変更せず、次の基準で裁定する。担当taxonomyはすべて既存の `lexical_relation_mislabel` とする。

- **F1（unnamable）**: 段階1が `unnamable` なら `blocking`。
- **F2（軸の帰属不正）**: 命名された軸が当該語義の `【日本語訳・定義】` から導出できず、同語義の類義語欄の語との対立としてのみ成立する軸転移なら `blocking`。
- **F3（型の不正）**: 段階1の分類が5型のいずれにも実質的に収まらず、解決策・結果・原因・関連概念の対立なら `blocking`。
- **F4（違い行の自己否定）**: `違い:` 行が対立の不成立・限定を自認する記述（「〜まで意味しない」「〜とは限らない」「対立しない」等の趣旨）を含むなら `minor` 以上。段階1がpassでもF4単独でfindingを出す。

段階1で軸を命名でき、F2〜F4のいずれにも該当しなければ問題なしとする。各flagの `suggested_direction` は `削除 | 語法・注意への対照表現としての移動 | 対立軸修正` のいずれか一方向とする。

段階2の回答は `antonym_axis_adjudication_record_v1` として、各不透明IDの `flags`、根拠、修正方向、F4のseverity、既存v6ルールによるframe finding、必要な `unrouted_observations` を返す。F1は段階1記録から機械照合され、段階2で解除してはならない。

段階2では次のJSON形を返す。hash群と `reviewer` は調整役が実際のartifactから封印するメタデータである。問題なしのアイテムも `flags: []` として必ず一度だけ記録する。

```json
{
  "schema_version": "antonym_axis_adjudication_record_v1",
  "pass_id": "frame-relation",
  "input_body_sha256": "stage 2 requestの値",
  "stage2_request_sha256": "stage 2 request全体のsha256",
  "blind_record_sha256": "保存済みstage 1 record全体のsha256",
  "reviewer": {},
  "adjudications": [
    {
      "item_id": "ant-opaque-id",
      "flags": ["F1 | F2 | F3 | F4"],
      "rationale": "裁定理由",
      "suggested_direction": "削除 | 語法・注意への対照表現としての移動 | 対立軸修正",
      "f4_severity": "blocking | minor | null"
    }
  ],
  "frame_findings": [],
  "unrouted_observations": []
}
```

### 4.3 出力と時系列封印

最終frame-relation pass出力にはfindingと併せて、段階1の `antonym_axis_blind_record` を改変せず埋め込み、段階2の `aligned_at` と `unrouted_observations` を記録する。`aligned_at` は段階1の `recorded_at` より後でなければならない。不透明ID、shuffle、alignment key、stage 1 request hash、保存済みrecord hashの照合はexample-attributionの既存機構と同じ方式を使い、`audits/BLIND_SEAL_CHRONOLOGY_REQUIRED` に従って段階1保存前の段階2開示をprocess欠陥として失敗させる。所要時間の長短は合否に使わない。


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
      "input_body_sha256": "c00b2207548c03e5eb31796c9607af43eb3c089dae2f9a8b96dc2bda9464a00e",
      "input_sections": {
        "definitions": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】ほとんど希望がなく、状況を変えるためなら危険や結果を十分に考えず何でもしようとする心理状態。人・集団について使うと「絶望した」「追い詰められた」「必死の」という意味になり、文脈によっては無謀さや暴力性を含むが、必ずしも暴力的とは限らない。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 116,
            "text": "【日本語訳・定義】他の方法が失敗した後、または成功の見込みがほとんどない状況で行われる行動・試み。危険を伴うことがあるが、語の必須条件は「追い詰められた状況での最後の努力」であり、結果が実際に失敗することまでは含まない。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 190,
            "text": "【日本語訳・定義】人が何かを極度に必要としたり、強く欲しがったりしている状態。desperate for 〈名詞〉 と desperate to do の形を取り、対象は仕事・金・助けのような切実な必要から、愛情・注目・コーヒーのような強い欲求まで広い。この用法だけでは、実際に希望を失ったり危険な行動を取ったりしているとは限らない。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 264,
            "text": "【日本語訳・定義】状況、病状、経済状態、不足などが非常に悪く、改善の望みが薄い、または緊急の対処を要する状態。人の心理状態ではなく、対象となる状況そのものの深刻さを評価する。desperate need は「極度の必要・不足」、desperate shortage は「深刻な不足」を表す。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 53,
            "text": "【コロケーション】"
          },
          {
            "line": 55,
            "text": "・be/feel desperate  "
          },
          {
            "line": 56,
            "text": "用途: 人が希望を失い、追い詰められた心理状態にあることを表す。  "
          },
          {
            "line": 57,
            "text": "例: After three days without news, the family felt desperate.  "
          },
          {
            "line": 58,
            "text": "訳: 3日間知らせがなく、家族は絶望的な気持ちになった。  "
          },
          {
            "line": 60,
            "text": "・grow increasingly desperate  "
          },
          {
            "line": 61,
            "text": "用途: 時間の経過とともに、絶望や切迫感が強まることを表す。  "
          },
          {
            "line": 62,
            "text": "例: The trapped hikers grew increasingly desperate as night fell.  "
          },
          {
            "line": 63,
            "text": "訳: 閉じ込められたハイカーたちは、夜になるにつれてますます切迫した。  "
          },
          {
            "line": 65,
            "text": "・a desperate man/ woman/ family  "
          },
          {
            "line": 66,
            "text": "用途: 希望や余裕を失い、極端な行動に出かねない人や家族を描写する。  "
          },
          {
            "line": 67,
            "text": "例: The police were looking for a desperate man who had lost everything.  "
          },
          {
            "line": 68,
            "text": "訳: 警察は、すべてを失って追い詰められた男を捜していた。  "
          },
          {
            "line": 70,
            "text": "・a desperate cry/plea for help  "
          },
          {
            "line": 71,
            "text": "用途: 絶望や切迫感を示す助けの叫び・懇願を表す。  "
          },
          {
            "line": 72,
            "text": "例: We heard a desperate cry for help from the riverbank.  "
          },
          {
            "line": 73,
            "text": "訳: 私たちは川岸からの必死の助けを求める叫び声を聞いた。  "
          },
          {
            "line": 75,
            "text": "・desperate with anxiety/grief  "
          },
          {
            "line": 76,
            "text": "用途: 強い不安や悲嘆で平静を失いかけている状態を表す。  "
          },
          {
            "line": 77,
            "text": "例: Desperate with anxiety, she called every hospital in the city.  "
          },
          {
            "line": 78,
            "text": "訳: 彼女は不安で取り乱し、市内の病院すべてに電話をかけた。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 124,
            "text": "【コロケーション】"
          },
          {
            "line": 126,
            "text": "・a desperate attempt to do  "
          },
          {
            "line": 127,
            "text": "用途: 成功の望みが薄くても、最後に何かをしようとする試みを表す。  "
          },
          {
            "line": 128,
            "text": "例: She made a desperate attempt to reach the child before the door closed.  "
          },
          {
            "line": 129,
            "text": "訳: 彼女は扉が閉まる前にその子に届こうと必死に試みた。  "
          },
          {
            "line": 131,
            "text": "・make a desperate bid for 〈自由・勝利・主導権〉  "
          },
          {
            "line": 132,
            "text": "用途: 重要な目標を得るための最後の、しばしば危険な努力を表す。  "
          },
          {
            "line": 133,
            "text": "例: The team made a desperate bid for victory in the final minute.  "
          },
          {
            "line": 134,
            "text": "訳: そのチームは最後の1分に勝利を懸けた必死の攻勢に出た。  "
          },
          {
            "line": 136,
            "text": "・take desperate measures  "
          },
          {
            "line": 137,
            "text": "用途: 通常の方法では解決できない問題に対して、非常手段を取ることを表す。  "
          },
          {
            "line": 138,
            "text": "例: The company took desperate measures to avoid bankruptcy.  "
          },
          {
            "line": 139,
            "text": "訳: その会社は破産を避けるために非常手段を取った。  "
          },
          {
            "line": 141,
            "text": "・a desperate struggle/battle to do  "
          },
          {
            "line": 142,
            "text": "用途: 勝ち目が薄くても、目的のために力を尽くす闘いを表す。  "
          },
          {
            "line": 143,
            "text": "例: The doctors began a desperate battle to save his life.  "
          },
          {
            "line": 144,
            "text": "訳: 医師たちは彼の命を救うための必死の闘いを始めた。  "
          },
          {
            "line": 146,
            "text": "・a desperate search for 〈人・解決策〉  "
          },
          {
            "line": 147,
            "text": "用途: 時間や可能性が限られた中で、最後まで行う切迫した捜索を表す。  "
          },
          {
            "line": 148,
            "text": "例: Volunteers organized a desperate search for the missing child.  "
          },
          {
            "line": 149,
            "text": "訳: ボランティアは行方不明の子どもを必死に捜す活動を組織した。  "
          },
          {
            "line": 151,
            "text": "・a desperate plea/appeal for 〈助け・平静〉  "
          },
          {
            "line": 152,
            "text": "用途: ほかに頼る手段がないような切迫した懇願・訴えを表す。  "
          },
          {
            "line": 153,
            "text": "例: The prisoner made a desperate plea for medical treatment.  "
          },
          {
            "line": 154,
            "text": "訳: その収監者は医療措置を求めて必死に懇願した。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 198,
            "text": "【コロケーション】"
          },
          {
            "line": 200,
            "text": "・be desperate for help  "
          },
          {
            "line": 201,
            "text": "用途: 助けを極度に必要としていることを表す。  "
          },
          {
            "line": 202,
            "text": "例: The villagers are desperate for help after the flood.  "
          },
          {
            "line": 203,
            "text": "訳: その村人たちは洪水の後、助けを切実に必要としている。  "
          },
          {
            "line": 205,
            "text": "・be desperate for a job  "
          },
          {
            "line": 206,
            "text": "用途: 仕事を非常に必要としている、または何としても得たいと思っていることを表す。  "
          },
          {
            "line": 207,
            "text": "例: He was desperate for a job after months of unemployment.  "
          },
          {
            "line": 208,
            "text": "訳: 彼は何か月も失業した後、仕事を切実に求めていた。  "
          },
          {
            "line": 210,
            "text": "・be desperate for money/attention  "
          },
          {
            "line": 211,
            "text": "用途: 金銭や他人からの注目を極度に必要・欲求していることを表す。  "
          },
          {
            "line": 212,
            "text": "例: The young performer seemed desperate for attention.  "
          },
          {
            "line": 213,
            "text": "訳: その若い出演者は注目を必死に求めているようだった。  "
          },
          {
            "line": 215,
            "text": "・be desperate to do  "
          },
          {
            "line": 216,
            "text": "用途: 何かをどうしてもしたい、または何としても実現したいという強い欲求を表す。  "
          },
          {
            "line": 217,
            "text": "例: She was desperate to find a way home before dark.  "
          },
          {
            "line": 218,
            "text": "訳: 彼女は暗くなる前に帰る方法をどうしても見つけたかった。  "
          },
          {
            "line": 220,
            "text": "・be desperate for someone to do  "
          },
          {
            "line": 221,
            "text": "用途: 他人に特定の行動をどうしてもしてほしいと望むことを表す。  "
          },
          {
            "line": 222,
            "text": "例: The parents were desperate for their son to come home safely.  "
          },
          {
            "line": 223,
            "text": "訳: その両親は息子に無事帰ってきてほしいと切に願っていた。  "
          },
          {
            "line": 225,
            "text": "・be desperate for a coffee  "
          },
          {
            "line": 226,
            "text": "用途: 危機的な必要ではなく、日常的なものを「とても欲しい」とくだけて言う。  "
          },
          {
            "line": 227,
            "text": "例: I’m desperate for a coffee after that early meeting.  "
          },
          {
            "line": 228,
            "text": "訳: あの早朝の会議の後で、コーヒーがすごく飲みたい。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 272,
            "text": "【コロケーション】"
          },
          {
            "line": 274,
            "text": "・a desperate situation  "
          },
          {
            "line": 275,
            "text": "用途: 事態が非常に悪く、危険または絶望的に近いことを表す。  "
          },
          {
            "line": 276,
            "text": "例: The aid workers were trying to evacuate people from a desperate situation.  "
          },
          {
            "line": 277,
            "text": "訳: 救援隊員たちは、非常に危険な状況から人々を避難させようとしていた。  "
          },
          {
            "line": 279,
            "text": "・be in desperate need of 〈物・支援〉  "
          },
          {
            "line": 280,
            "text": "用途: 物・支援・対策が極度に不足し、緊急に必要であることを表す。  "
          },
          {
            "line": 281,
            "text": "例: The hospital is in desperate need of blood supplies.  "
          },
          {
            "line": 282,
            "text": "訳: その病院は血液の供給を極度に必要としている。  "
          },
          {
            "line": 284,
            "text": "・a desperate shortage of 〈物〉  "
          },
          {
            "line": 285,
            "text": "用途: 物資や資源が極端に不足していることを表す。  "
          },
          {
            "line": 286,
            "text": "例: The region is facing a desperate shortage of clean water.  "
          },
          {
            "line": 287,
            "text": "訳: その地域は清潔な水の深刻な不足に直面している。  "
          },
          {
            "line": 289,
            "text": "・be in desperate straits  "
          },
          {
            "line": 290,
            "text": "用途: 経済・生活・組織などが非常に困窮した状況にあることを表す。  "
          },
          {
            "line": 291,
            "text": "例: Many small farms are in desperate straits after the prolonged drought.  "
          },
          {
            "line": 292,
            "text": "訳: 長引く干ばつの後、多くの小規模農家が非常に困窮している。  "
          },
          {
            "line": 294,
            "text": "・desperate poverty  "
          },
          {
            "line": 295,
            "text": "用途: 貧困が極度で、生活を維持することが非常に難しい状態を表す。  "
          },
          {
            "line": 296,
            "text": "例: The report describes families living in desperate poverty.  "
          },
          {
            "line": 297,
            "text": "訳: その報告書は極度の貧困の中で暮らす家族について述べている。  "
          },
          {
            "line": 299,
            "text": "・a desperate illness/crisis  "
          },
          {
            "line": 300,
            "text": "用途: 病状や危機が非常に重く、改善や解決の見込みが薄いことを表す。  "
          },
          {
            "line": 301,
            "text": "例: The patient was in a desperate condition when the ambulance arrived.  "
          },
          {
            "line": 302,
            "text": "訳: 救急車が到着したとき、患者の状態は非常に深刻だった。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 82,
            "text": "【類義語】"
          },
          {
            "line": 84,
            "text": "・despairing  "
          },
          {
            "line": 85,
            "text": "定義: 希望を失い、絶望を感じたり示したりしている。  "
          },
          {
            "line": 86,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 87,
            "text": "違い: despairing は内面的な絶望の表出に焦点があり、desperate のように危険を顧みない行動まで必ず含むわけではない。  "
          },
          {
            "line": 88,
            "text": "例: He gave me a despairing look when the plan failed.  "
          },
          {
            "line": 89,
            "text": "訳: 計画が失敗すると、彼は私に絶望したような顔を向けた。  "
          },
          {
            "line": 91,
            "text": "・hopeless  "
          },
          {
            "line": 92,
            "text": "定義: 希望や成功の見込みがない、またはそう感じている。  "
          },
          {
            "line": 93,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 94,
            "text": "違い: hopeless は望みのなさや諦めに焦点があり、desperate はその状態から生じる必死の行動・切迫感を強く示す。  "
          },
          {
            "line": 95,
            "text": "例: The rescue team refused to call the search hopeless.  "
          },
          {
            "line": 96,
            "text": "訳: 救助隊は捜索を見込みがないとは認めようとしなかった。  "
          },
          {
            "line": 98,
            "text": "・frantic  "
          },
          {
            "line": 99,
            "text": "定義: 恐怖・不安・急ぎで取り乱し、落ち着いて行動できない。  "
          },
          {
            "line": 100,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 101,
            "text": "違い: frantic は動揺や慌ただしさに焦点があり、desperate は希望のなさや極端な必要をより強く含む。  "
          },
          {
            "line": 102,
            "text": "例: Frantic parents searched the crowded station for their child.  "
          },
          {
            "line": 103,
            "text": "訳: 取り乱した両親は、混雑した駅で子どもを捜した。  "
          },
          {
            "line": 105,
            "text": "【反意語】"
          },
          {
            "line": 107,
            "text": "・hopeful  "
          },
          {
            "line": 108,
            "text": "定義: よい結果や成功の可能性を信じ、希望を持っている。  "
          },
          {
            "line": 109,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 110,
            "text": "違い: hopeful は希望が残っている状態、desperate は希望がほとんどなく追い詰められた状態を表す。両者は心理状態の軸で対立する。  "
          },
          {
            "line": 111,
            "text": "例: The family remained hopeful despite the long wait.  "
          },
          {
            "line": 112,
            "text": "訳: 長く待たされても、その家族は希望を失わなかった。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 158,
            "text": "【類義語】"
          },
          {
            "line": 160,
            "text": "・last-ditch  "
          },
          {
            "line": 161,
            "text": "定義: ほかの手段が尽きた段階で行う、最後の。  "
          },
          {
            "line": 162,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 163,
            "text": "違い: last-ditch は最後の機会という順序に焦点があり、desperate は行為者の切迫感や成功の見込みの薄さをより強く示す。  "
          },
          {
            "line": 164,
            "text": "例: The board approved a last-ditch plan to save the project.  "
          },
          {
            "line": 165,
            "text": "訳: 取締役会はプロジェクトを救うための最後の計画を承認した。  "
          },
          {
            "line": 167,
            "text": "・frantic  "
          },
          {
            "line": 168,
            "text": "定義: 急ぎや不安で取り乱した、必死の。  "
          },
          {
            "line": 169,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 170,
            "text": "違い: frantic は行動の慌ただしさ・混乱を表し、desperate は追い詰められた状況と望みの薄さに焦点がある。  "
          },
          {
            "line": 171,
            "text": "例: They launched a frantic search before the storm arrived.  "
          },
          {
            "line": 172,
            "text": "訳: 彼らは嵐が来る前に大急ぎで捜索を始めた。  "
          },
          {
            "line": 174,
            "text": "・drastic  "
          },
          {
            "line": 175,
            "text": "定義: 問題を変えるために、通常より極端で大きな影響を及ぼす。  "
          },
          {
            "line": 176,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 177,
            "text": "違い: drastic は措置の強さ・規模を表すが、desperate のように希望のなさや切迫した動機を必ずしも含まない。  "
          },
          {
            "line": 178,
            "text": "例: The hospital introduced drastic changes to reduce infections.  "
          },
          {
            "line": 179,
            "text": "訳: その病院は感染を減らすために抜本的な変更を導入した。  "
          },
          {
            "line": 181,
            "text": "・do-or-die  "
          },
          {
            "line": 182,
            "text": "定義: 成功しなければ重大な結果になる、絶対に成功させなければならない。  "
          },
          {
            "line": 183,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 184,
            "text": "違い: do-or-die は成功か失敗かの重大な二択を強調し、desperate は試みの切迫感や成功の見込みの薄さを表す。  "
          },
          {
            "line": 185,
            "text": "例: This is a do-or-die match for the team.  "
          },
          {
            "line": 186,
            "text": "訳: これはそのチームにとって絶対に負けられない試合だ。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 232,
            "text": "【類義語】"
          },
          {
            "line": 234,
            "text": "・in dire need of 〈物・支援〉  "
          },
          {
            "line": 235,
            "text": "定義: 物や支援を非常に深刻な状態で必要としている。  "
          },
          {
            "line": 236,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 237,
            "text": "違い: in dire need of は客観的な不足・困窮を強調し、desperate for は人の強い欲求・切望にも、くだけた欲しさにも使える。  "
          },
          {
            "line": 238,
            "text": "例: The clinic is in dire need of more nurses.  "
          },
          {
            "line": 239,
            "text": "訳: その診療所は看護師をもっと必要とする深刻な状況にある。  "
          },
          {
            "line": 241,
            "text": "・eager for 〈機会・知らせ〉  "
          },
          {
            "line": 242,
            "text": "定義: 何かを熱心に、楽しみにしながら強く望んでいる。  "
          },
          {
            "line": 243,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 244,
            "text": "違い: eager は期待や前向きな熱意を含みやすく、desperate のような困窮・焦り・追い詰められた感じは必須ではない。  "
          },
          {
            "line": 245,
            "text": "例: The students were eager for the results of the competition.  "
          },
          {
            "line": 246,
            "text": "訳: 学生たちは競技会の結果を心待ちにしていた。  "
          },
          {
            "line": 248,
            "text": "・longing for 〈人・場所・経験〉  "
          },
          {
            "line": 249,
            "text": "定義: 人・場所・過去の経験などを強く恋しく思い、切望している。  "
          },
          {
            "line": 250,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 251,
            "text": "違い: longing for は持続的で感情的なあこがれ・恋しさに焦点があり、desperate for は必要の切迫や欲求の極端な強さを広く表す。  "
          },
          {
            "line": 252,
            "text": "例: She felt a deep longing for her childhood home.  "
          },
          {
            "line": 253,
            "text": "訳: 彼女は子どもの頃の家を深く恋しく思った。  "
          },
          {
            "line": 255,
            "text": "・dying for 〈物・行動〉  "
          },
          {
            "line": 256,
            "text": "定義: くだけて、何かを非常に欲しい・したいと思っている。  "
          },
          {
            "line": 257,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 258,
            "text": "違い: dying for は強調的な口語表現で、文字どおり死ぬ危険や絶望を通常は含まない。desperate for は口語から報道まで使えるが、より切迫した響きが出やすい。  "
          },
          {
            "line": 259,
            "text": "例: I’m dying for a hot shower after the hike.  "
          },
          {
            "line": 260,
            "text": "訳: ハイキングの後で、熱いシャワーを浴びたくてたまらない。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 306,
            "text": "【類義語】"
          },
          {
            "line": 308,
            "text": "・dire  "
          },
          {
            "line": 309,
            "text": "定義: 状況が非常に深刻で、緊急の対処や救済を必要とする。  "
          },
          {
            "line": 310,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 311,
            "text": "違い: dire は状況の深刻さを硬く客観的に述べやすく、desperate はそこに絶望感・切迫感・極端さが加わる。  "
          },
          {
            "line": 312,
            "text": "例: The country is facing a dire shortage of food.  "
          },
          {
            "line": 313,
            "text": "訳: その国は食料の深刻な不足に直面している。  "
          },
          {
            "line": 315,
            "text": "・grave  "
          },
          {
            "line": 316,
            "text": "定義: 危険・結果・責任などが非常に重大で、軽視できない。  "
          },
          {
            "line": 317,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 318,
            "text": "違い: grave は重大さ・深刻さを改まって示し、desperate のように改善の望みの薄さや切迫した努力まで含むとは限らない。  "
          },
          {
            "line": 319,
            "text": "例: The accident raised grave concerns about safety.  "
          },
          {
            "line": 320,
            "text": "訳: その事故は安全性について重大な懸念を生じさせた。  "
          },
          {
            "line": 322,
            "text": "・critical  "
          },
          {
            "line": 323,
            "text": "定義: 状況が危機的で、直ちに判断・対応しなければならない。  "
          },
          {
            "line": 324,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 325,
            "text": "違い: critical は危機の段階や緊急性に焦点があり、desperate は極度の悪さや望みの薄さをより強く感じさせる。  "
          },
          {
            "line": 326,
            "text": "例: The patient remains in critical condition.  "
          },
          {
            "line": 327,
            "text": "訳: その患者は依然として危篤状態にある。  "
          },
          {
            "line": 329,
            "text": "・severe  "
          },
          {
            "line": 330,
            "text": "定義: 程度が非常に強く、苦痛・損害・不足などが大きい。  "
          },
          {
            "line": 331,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 332,
            "text": "違い: severe は強度の大きさを広く表す客観的な語で、desperate のような追い詰められた評価やほとんど望みのない感じは必須ではない。  "
          },
          {
            "line": 333,
            "text": "例: The area suffered severe water shortages.  "
          },
          {
            "line": 334,
            "text": "訳: その地域は深刻な水不足に苦しんだ。  "
          },
          {
            "line": 336,
            "text": "【反意語】"
          },
          {
            "line": 338,
            "text": "・promising  "
          },
          {
            "line": 339,
            "text": "定義: よい結果や改善の見込みがあり、将来に希望を持たせる。  "
          },
          {
            "line": 340,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 341,
            "text": "違い: promising は状況の明るい見込みを示し、desperate は状況が非常に悪く改善の望みが薄いことを示す。状況評価の軸で対立する。  "
          },
          {
            "line": 342,
            "text": "例: The latest figures give a more promising picture of the economy.  "
          },
          {
            "line": 343,
            "text": "訳: 最新の数字は経済についてより明るい見通しを示している。  "
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
      "input_body_sha256": "c00b2207548c03e5eb31796c9607af43eb3c089dae2f9a8b96dc2bda9464a00e",
      "input_sections": {
        "core_image": [
          {
            "line": 30,
            "text": "＃コアイメージ"
          },
          {
            "line": 32,
            "text": "desperate の中心には、「希望や余裕がほとんどなく、事態を変えるために限界まで切迫している」という感覚がある。人の状態では絶望が無謀さや必死さにつながり、行動では最後の手段になり、必要・欲求では強さが極限に達し、状況では深刻さや危険として現れる。  "
          },
          {
            "line": 34,
            "text": "・絶望して余裕がない → 「絶望して必死の、危険を顧みない」（語義1）  "
          },
          {
            "line": 35,
            "text": "・望みが薄くても最後に試みる → 「必死の、最後の手段の」（語義2）  "
          },
          {
            "line": 36,
            "text": "・必要・欲求が極度に強い → 「～を非常に必要とする、切望する」（語義3）  "
          },
          {
            "line": 37,
            "text": "・状況や不足が限界的に悪い → 「非常に深刻な、危険な、極度の」（語義4）  "
          },
          {
            "line": 39,
            "text": "語義1は人・集団の心理状態、語義2はその状態から出る行動や試み、語義3は対象への強い必要・欲求、語義4は状況や状態そのものの深刻さに焦点がある。特に desperate for 〈名詞〉は「その人が強く必要・欲求を感じる」、in desperate need of 〈名詞〉は「状況が極度に不足している」という違いに注意する。  "
          }
        ],
        "sense_structure": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】ほとんど希望がなく、状況を変えるためなら危険や結果を十分に考えず何でもしようとする心理状態。人・集団について使うと「絶望した」「追い詰められた」「必死の」という意味になり、文脈によっては無謀さや暴力性を含むが、必ずしも暴力的とは限らない。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 116,
            "text": "【日本語訳・定義】他の方法が失敗した後、または成功の見込みがほとんどない状況で行われる行動・試み。危険を伴うことがあるが、語の必須条件は「追い詰められた状況での最後の努力」であり、結果が実際に失敗することまでは含まない。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 190,
            "text": "【日本語訳・定義】人が何かを極度に必要としたり、強く欲しがったりしている状態。desperate for 〈名詞〉 と desperate to do の形を取り、対象は仕事・金・助けのような切実な必要から、愛情・注目・コーヒーのような強い欲求まで広い。この用法だけでは、実際に希望を失ったり危険な行動を取ったりしているとは限らない。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 264,
            "text": "【日本語訳・定義】状況、病状、経済状態、不足などが非常に悪く、改善の望みが薄い、または緊急の対処を要する状態。人の心理状態ではなく、対象となる状況そのものの深刻さを評価する。desperate need は「極度の必要・不足」、desperate shortage は「深刻な不足」を表す。  "
          }
        ],
        "usage_notes": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 80,
            "text": "【語法・注意】この語義の desperate は単なる「熱心な」「決意の固い」ではなく、希望のなさや追い詰められた余裕のなさを含む。be desperate to do は「～したくてたまらない／～することを切望している」という語義3になりやすく、後続の to不定詞だけで語義1の「絶望している」と決めつけない。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 156,
            "text": "【語法・注意】desperate attempt は「必死の試み」であって、必ずしも無謀・違法という意味ではない。last-ditch attempt は「最後の手段」という時間的・戦略的な面を強調し、desperate attempt はそこに切迫感や成功の望みの薄さが加わる。take desperate measures も、手段が必ず非倫理的・暴力的だと決めつけない。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 230,
            "text": "【語法・注意】名詞を続けるときは desperate for 〈名詞〉、動作を続けるときは desperate to do であり、×desperate doing や ×desperate for do とはしない。be desperate to do は「～したくてたまらない」で、必ずしも「絶望して無謀なことをする」ではない。want、need より強く、文脈によっては焦りや感情的な弱さまで伝える。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 304,
            "text": "【語法・注意】in desperate need of 〈名詞〉は、状況や不足が深刻であることに焦点を置く。一方、be desperate for 〈名詞〉は、主語である人・組織が対象を強く必要・欲求していることに焦点を置く。たとえば The hospital is in desperate need of blood は病院の不足を、The patient is desperate for help は患者の切実な求めを表す。desperate は「必ず完全に絶望的」と断定する語ではなく、深刻さ・危険さ・緊急性を強く評価する語としても使う。  "
          }
        ],
        "word_formation": [
          {
            "line": 23,
            "text": "＃語形成"
          },
          {
            "line": 25,
            "text": "・desperately：desperate の副詞。「絶望的・必死の状態で」のほか、desperately need/want のように「非常に、切実に」の意味でも使う。  "
          },
          {
            "line": 26,
            "text": "・desperation：名詞。「絶望、やけ、切迫した状態」または、その状態から出る必死の行動。  "
          },
          {
            "line": 27,
            "text": "・desperateness：名詞。「絶望的・切迫した状態」。desperation より使用頻度が低く、説明的・硬めに響く。  "
          },
          {
            "line": 28,
            "text": "・desperado：絶望や無謀さと結び付いた「無法者、凶悪犯」を表す名詞。desperate の通常の名詞形ではなく、別に語彙化した語である。  "
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
      "schema_version": "antonym_axis_blind_request_v1",
      "pass_id": "frame-relation",
      "taxonomy_ids": [
        "argument_slot_role_mismatch",
        "lexical_relation_mislabel"
      ],
      "specification": "prompts/check_pass_frame_relation_v7.md",
      "input_body_sha256": "c00b2207548c03e5eb31796c9607af43eb3c089dae2f9a8b96dc2bda9464a00e",
      "input_sections": {
        "antonym_items": [
          {
            "item_id": "ant-c52aadd72499",
            "headword": "desperate",
            "sense_definition": "【日本語訳・定義】状況、病状、経済状態、不足などが非常に悪く、改善の望みが薄い、または緊急の対処を要する状態。人の心理状態ではなく、対象となる状況そのものの深刻さを評価する。desperate need は「極度の必要・不足」、desperate shortage は「深刻な不足」を表す。",
            "antonym": "promising",
            "antonym_definition": "定義: よい結果や改善の見込みがあり、将来に希望を持たせる。"
          },
          {
            "item_id": "ant-4e7b502379ab",
            "headword": "desperate",
            "sense_definition": "【日本語訳・定義】ほとんど希望がなく、状況を変えるためなら危険や結果を十分に考えず何でもしようとする心理状態。人・集団について使うと「絶望した」「追い詰められた」「必死の」という意味になり、文脈によっては無謀さや暴力性を含むが、必ずしも暴力的とは限らない。",
            "antonym": "hopeful",
            "antonym_definition": "定義: よい結果や成功の可能性を信じ、希望を持っている。"
          }
        ]
      },
      "blind_protocol": {
        "stage": 1,
        "withheld_fields": [
          "difference_line",
          "frequency_line",
          "example_line",
          "translation_line",
          "synonym_section",
          "core_image",
          "other_senses",
          "document_order"
        ],
        "questions": [
          "name_axis_as_one_noun",
          "classify_as_補完_程度_方向_評価_状態",
          "record_unnamable_with_one_sentence_reason"
        ],
        "required_output_schema": "antonym_axis_blind_record_v1"
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
      "input_body_sha256": "c00b2207548c03e5eb31796c9607af43eb3c089dae2f9a8b96dc2bda9464a00e",
      "input_sections": {
        "sense_structure": [
          {
            "sense_id": "sense:001",
            "line": 43,
            "label": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない",
            "definition": "ほとんど希望がなく、状況を変えるためなら危険や結果を十分に考えず何でもしようとする心理状態。人・集団について使うと「絶望した」「追い詰められた」「必死の」という意味になり、文脈によっては無謀さや暴力性を含むが、必ずしも暴力的とは限らない。"
          },
          {
            "sense_id": "sense:002",
            "line": 114,
            "label": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の",
            "definition": "他の方法が失敗した後、または成功の見込みがほとんどない状況で行われる行動・試み。危険を伴うことがあるが、語の必須条件は「追い詰められた状況での最後の努力」であり、結果が実際に失敗することまでは含まない。"
          },
          {
            "sense_id": "sense:003",
            "line": 188,
            "label": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している",
            "definition": "人が何かを極度に必要としたり、強く欲しがったりしている状態。desperate for 〈名詞〉 と desperate to do の形を取り、対象は仕事・金・助けのような切実な必要から、愛情・注目・コーヒーのような強い欲求まで広い。この用法だけでは、実際に希望を失ったり危険な行動を取ったりしているとは限らない。"
          },
          {
            "sense_id": "sense:004",
            "line": 262,
            "label": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の",
            "definition": "状況、病状、経済状態、不足などが非常に悪く、改善の望みが薄い、または緊急の対処を要する状態。人の心理状態ではなく、対象となる状況そのものの深刻さを評価する。desperate need は「極度の必要・不足」、desperate shortage は「深刻な不足」を表す。"
          }
        ],
        "collocations_examples": [
          {
            "example_id": "ex-37d057ab67a3",
            "example": "The company took desperate measures to avoid bankruptcy.",
            "translation": "その会社は破産を避けるために非常手段を取った。"
          },
          {
            "example_id": "ex-2bebca4d3416",
            "example": "The villagers are desperate for help after the flood.",
            "translation": "その村人たちは洪水の後、助けを切実に必要としている。"
          },
          {
            "example_id": "ex-09b1b472de18",
            "example": "Many small farms are in desperate straits after the prolonged drought.",
            "translation": "長引く干ばつの後、多くの小規模農家が非常に困窮している。"
          },
          {
            "example_id": "ex-2b4048fceda1",
            "example": "The parents were desperate for their son to come home safely.",
            "translation": "その両親は息子に無事帰ってきてほしいと切に願っていた。"
          },
          {
            "example_id": "ex-423ccf919216",
            "example": "The doctors began a desperate battle to save his life.",
            "translation": "医師たちは彼の命を救うための必死の闘いを始めた。"
          },
          {
            "example_id": "ex-5ab925453dfc",
            "example": "She was desperate to find a way home before dark.",
            "translation": "彼女は暗くなる前に帰る方法をどうしても見つけたかった。"
          },
          {
            "example_id": "ex-4b90d1e3fdfe",
            "example": "Desperate with anxiety, she called every hospital in the city.",
            "translation": "彼女は不安で取り乱し、市内の病院すべてに電話をかけた。"
          },
          {
            "example_id": "ex-6f9f7ad3d52a",
            "example": "The region is facing a desperate shortage of clean water.",
            "translation": "その地域は清潔な水の深刻な不足に直面している。"
          },
          {
            "example_id": "ex-a2ffbda604ae",
            "example": "He was desperate for a job after months of unemployment.",
            "translation": "彼は何か月も失業した後、仕事を切実に求めていた。"
          },
          {
            "example_id": "ex-b54f7c1b29fd",
            "example": "She made a desperate attempt to reach the child before the door closed.",
            "translation": "彼女は扉が閉まる前にその子に届こうと必死に試みた。"
          },
          {
            "example_id": "ex-50c03426e5ad",
            "example": "We heard a desperate cry for help from the riverbank.",
            "translation": "私たちは川岸からの必死の助けを求める叫び声を聞いた。"
          },
          {
            "example_id": "ex-2f738c2261bb",
            "example": "The trapped hikers grew increasingly desperate as night fell.",
            "translation": "閉じ込められたハイカーたちは、夜になるにつれてますます切迫した。"
          },
          {
            "example_id": "ex-50988792e638",
            "example": "The aid workers were trying to evacuate people from a desperate situation.",
            "translation": "救援隊員たちは、非常に危険な状況から人々を避難させようとしていた。"
          },
          {
            "example_id": "ex-73e5453fdb1b",
            "example": "The police were looking for a desperate man who had lost everything.",
            "translation": "警察は、すべてを失って追い詰められた男を捜していた。"
          },
          {
            "example_id": "ex-43e15b8ac1f6",
            "example": "The prisoner made a desperate plea for medical treatment.",
            "translation": "その収監者は医療措置を求めて必死に懇願した。"
          },
          {
            "example_id": "ex-f47fe96f6194",
            "example": "The report describes families living in desperate poverty.",
            "translation": "その報告書は極度の貧困の中で暮らす家族について述べている。"
          },
          {
            "example_id": "ex-af7332920171",
            "example": "I’m desperate for a coffee after that early meeting.",
            "translation": "あの早朝の会議の後で、コーヒーがすごく飲みたい。"
          },
          {
            "example_id": "ex-d03375fe01f1",
            "example": "The team made a desperate bid for victory in the final minute.",
            "translation": "そのチームは最後の1分に勝利を懸けた必死の攻勢に出た。"
          },
          {
            "example_id": "ex-70f341671955",
            "example": "The patient was in a desperate condition when the ambulance arrived.",
            "translation": "救急車が到着したとき、患者の状態は非常に深刻だった。"
          },
          {
            "example_id": "ex-06867b0211c5",
            "example": "The hospital is in desperate need of blood supplies.",
            "translation": "その病院は血液の供給を極度に必要としている。"
          },
          {
            "example_id": "ex-6b6ff41db9c1",
            "example": "Volunteers organized a desperate search for the missing child.",
            "translation": "ボランティアは行方不明の子どもを必死に捜す活動を組織した。"
          },
          {
            "example_id": "ex-0756a6ae7003",
            "example": "The young performer seemed desperate for attention.",
            "translation": "その若い出演者は注目を必死に求めているようだった。"
          },
          {
            "example_id": "ex-efdcca9bd0a2",
            "example": "After three days without news, the family felt desperate.",
            "translation": "3日間知らせがなく、家族は絶望的な気持ちになった。"
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
      "input_body_sha256": "c00b2207548c03e5eb31796c9607af43eb3c089dae2f9a8b96dc2bda9464a00e",
      "input_sections": {
        "etymology": [
          {
            "line": 17,
            "text": "＃語源"
          },
          {
            "line": 19,
            "text": "中英語 desperat が古フランス語を経て、ラテン語 desperatus「希望を失った、絶望した」にさかのぼる。これは動詞 desperare「絶望する、望みがないとあきらめる」の過去分詞で、de- と sperare「望む、希望する」から成る。まず「絶望している」という人の状態を表し、そこから、絶望に動かされた無謀な行動、成功の望みが薄い試み、状況の深刻さ、極度の必要・欲求へ意味が広がった。  "
          },
          {
            "line": 21,
            "text": "despair「絶望する／絶望」、desperately「必死に、非常に」、desperation「絶望、やけ、切迫した状態」は同じ語源に連なる。語源上の「希望がない」という核は現代の全用法を文字どおりに規定するものではなく、desperate for a coffee のようなくだけた強い欲求では、必ずしも実際の絶望や危険を意味しない。  "
          }
        ],
        "word_formation": [
          {
            "line": 23,
            "text": "＃語形成"
          },
          {
            "line": 25,
            "text": "・desperately：desperate の副詞。「絶望的・必死の状態で」のほか、desperately need/want のように「非常に、切実に」の意味でも使う。  "
          },
          {
            "line": 26,
            "text": "・desperation：名詞。「絶望、やけ、切迫した状態」または、その状態から出る必死の行動。  "
          },
          {
            "line": 27,
            "text": "・desperateness：名詞。「絶望的・切迫した状態」。desperation より使用頻度が低く、説明的・硬めに響く。  "
          },
          {
            "line": 28,
            "text": "・desperado：絶望や無謀さと結び付いた「無法者、凶悪犯」を表す名詞。desperate の通常の名詞形ではなく、別に語彙化した語である。  "
          }
        ],
        "sense_structure": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】ほとんど希望がなく、状況を変えるためなら危険や結果を十分に考えず何でもしようとする心理状態。人・集団について使うと「絶望した」「追い詰められた」「必死の」という意味になり、文脈によっては無謀さや暴力性を含むが、必ずしも暴力的とは限らない。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 116,
            "text": "【日本語訳・定義】他の方法が失敗した後、または成功の見込みがほとんどない状況で行われる行動・試み。危険を伴うことがあるが、語の必須条件は「追い詰められた状況での最後の努力」であり、結果が実際に失敗することまでは含まない。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 190,
            "text": "【日本語訳・定義】人が何かを極度に必要としたり、強く欲しがったりしている状態。desperate for 〈名詞〉 と desperate to do の形を取り、対象は仕事・金・助けのような切実な必要から、愛情・注目・コーヒーのような強い欲求まで広い。この用法だけでは、実際に希望を失ったり危険な行動を取ったりしているとは限らない。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 264,
            "text": "【日本語訳・定義】状況、病状、経済状態、不足などが非常に悪く、改善の望みが薄い、または緊急の対処を要する状態。人の心理状態ではなく、対象となる状況そのものの深刻さを評価する。desperate need は「極度の必要・不足」、desperate shortage は「深刻な不足」を表す。  "
          }
        ],
        "frequency_register": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 47,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 49,
            "text": "【レジスター/領域】標準的な一般語。感情描写、報道、物語、災害・救助、社会問題で広く使う。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 118,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 120,
            "text": "【レジスター/領域】標準的な一般語。報道、政治、競技、救助、交渉、ビジネス、物語で広く使う。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 192,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 194,
            "text": "【レジスター/領域】標準的な一般語。求人、支援要請、感情描写で広く使う。desperate for a coffee のような「とても欲しい」という用法はくだけた会話で特に自然である。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 266,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 268,
            "text": "【レジスター/領域】標準的な一般語。報道、社会問題、医療、経済、災害、政策で広く使う。  "
          }
        ],
        "usage_notes": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 80,
            "text": "【語法・注意】この語義の desperate は単なる「熱心な」「決意の固い」ではなく、希望のなさや追い詰められた余裕のなさを含む。be desperate to do は「～したくてたまらない／～することを切望している」という語義3になりやすく、後続の to不定詞だけで語義1の「絶望している」と決めつけない。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 156,
            "text": "【語法・注意】desperate attempt は「必死の試み」であって、必ずしも無謀・違法という意味ではない。last-ditch attempt は「最後の手段」という時間的・戦略的な面を強調し、desperate attempt はそこに切迫感や成功の望みの薄さが加わる。take desperate measures も、手段が必ず非倫理的・暴力的だと決めつけない。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 230,
            "text": "【語法・注意】名詞を続けるときは desperate for 〈名詞〉、動作を続けるときは desperate to do であり、×desperate doing や ×desperate for do とはしない。be desperate to do は「～したくてたまらない」で、必ずしも「絶望して無謀なことをする」ではない。want、need より強く、文脈によっては焦りや感情的な弱さまで伝える。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 304,
            "text": "【語法・注意】in desperate need of 〈名詞〉は、状況や不足が深刻であることに焦点を置く。一方、be desperate for 〈名詞〉は、主語である人・組織が対象を強く必要・欲求していることに焦点を置く。たとえば The hospital is in desperate need of blood は病院の不足を、The patient is desperate for help は患者の切実な求めを表す。desperate は「必ず完全に絶望的」と断定する語ではなく、深刻さ・危険さ・緊急性を強く評価する語としても使う。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 53,
            "text": "【コロケーション】"
          },
          {
            "line": 55,
            "text": "・be/feel desperate  "
          },
          {
            "line": 56,
            "text": "用途: 人が希望を失い、追い詰められた心理状態にあることを表す。  "
          },
          {
            "line": 57,
            "text": "例: After three days without news, the family felt desperate.  "
          },
          {
            "line": 58,
            "text": "訳: 3日間知らせがなく、家族は絶望的な気持ちになった。  "
          },
          {
            "line": 60,
            "text": "・grow increasingly desperate  "
          },
          {
            "line": 61,
            "text": "用途: 時間の経過とともに、絶望や切迫感が強まることを表す。  "
          },
          {
            "line": 62,
            "text": "例: The trapped hikers grew increasingly desperate as night fell.  "
          },
          {
            "line": 63,
            "text": "訳: 閉じ込められたハイカーたちは、夜になるにつれてますます切迫した。  "
          },
          {
            "line": 65,
            "text": "・a desperate man/ woman/ family  "
          },
          {
            "line": 66,
            "text": "用途: 希望や余裕を失い、極端な行動に出かねない人や家族を描写する。  "
          },
          {
            "line": 67,
            "text": "例: The police were looking for a desperate man who had lost everything.  "
          },
          {
            "line": 68,
            "text": "訳: 警察は、すべてを失って追い詰められた男を捜していた。  "
          },
          {
            "line": 70,
            "text": "・a desperate cry/plea for help  "
          },
          {
            "line": 71,
            "text": "用途: 絶望や切迫感を示す助けの叫び・懇願を表す。  "
          },
          {
            "line": 72,
            "text": "例: We heard a desperate cry for help from the riverbank.  "
          },
          {
            "line": 73,
            "text": "訳: 私たちは川岸からの必死の助けを求める叫び声を聞いた。  "
          },
          {
            "line": 75,
            "text": "・desperate with anxiety/grief  "
          },
          {
            "line": 76,
            "text": "用途: 強い不安や悲嘆で平静を失いかけている状態を表す。  "
          },
          {
            "line": 77,
            "text": "例: Desperate with anxiety, she called every hospital in the city.  "
          },
          {
            "line": 78,
            "text": "訳: 彼女は不安で取り乱し、市内の病院すべてに電話をかけた。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 124,
            "text": "【コロケーション】"
          },
          {
            "line": 126,
            "text": "・a desperate attempt to do  "
          },
          {
            "line": 127,
            "text": "用途: 成功の望みが薄くても、最後に何かをしようとする試みを表す。  "
          },
          {
            "line": 128,
            "text": "例: She made a desperate attempt to reach the child before the door closed.  "
          },
          {
            "line": 129,
            "text": "訳: 彼女は扉が閉まる前にその子に届こうと必死に試みた。  "
          },
          {
            "line": 131,
            "text": "・make a desperate bid for 〈自由・勝利・主導権〉  "
          },
          {
            "line": 132,
            "text": "用途: 重要な目標を得るための最後の、しばしば危険な努力を表す。  "
          },
          {
            "line": 133,
            "text": "例: The team made a desperate bid for victory in the final minute.  "
          },
          {
            "line": 134,
            "text": "訳: そのチームは最後の1分に勝利を懸けた必死の攻勢に出た。  "
          },
          {
            "line": 136,
            "text": "・take desperate measures  "
          },
          {
            "line": 137,
            "text": "用途: 通常の方法では解決できない問題に対して、非常手段を取ることを表す。  "
          },
          {
            "line": 138,
            "text": "例: The company took desperate measures to avoid bankruptcy.  "
          },
          {
            "line": 139,
            "text": "訳: その会社は破産を避けるために非常手段を取った。  "
          },
          {
            "line": 141,
            "text": "・a desperate struggle/battle to do  "
          },
          {
            "line": 142,
            "text": "用途: 勝ち目が薄くても、目的のために力を尽くす闘いを表す。  "
          },
          {
            "line": 143,
            "text": "例: The doctors began a desperate battle to save his life.  "
          },
          {
            "line": 144,
            "text": "訳: 医師たちは彼の命を救うための必死の闘いを始めた。  "
          },
          {
            "line": 146,
            "text": "・a desperate search for 〈人・解決策〉  "
          },
          {
            "line": 147,
            "text": "用途: 時間や可能性が限られた中で、最後まで行う切迫した捜索を表す。  "
          },
          {
            "line": 148,
            "text": "例: Volunteers organized a desperate search for the missing child.  "
          },
          {
            "line": 149,
            "text": "訳: ボランティアは行方不明の子どもを必死に捜す活動を組織した。  "
          },
          {
            "line": 151,
            "text": "・a desperate plea/appeal for 〈助け・平静〉  "
          },
          {
            "line": 152,
            "text": "用途: ほかに頼る手段がないような切迫した懇願・訴えを表す。  "
          },
          {
            "line": 153,
            "text": "例: The prisoner made a desperate plea for medical treatment.  "
          },
          {
            "line": 154,
            "text": "訳: その収監者は医療措置を求めて必死に懇願した。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 198,
            "text": "【コロケーション】"
          },
          {
            "line": 200,
            "text": "・be desperate for help  "
          },
          {
            "line": 201,
            "text": "用途: 助けを極度に必要としていることを表す。  "
          },
          {
            "line": 202,
            "text": "例: The villagers are desperate for help after the flood.  "
          },
          {
            "line": 203,
            "text": "訳: その村人たちは洪水の後、助けを切実に必要としている。  "
          },
          {
            "line": 205,
            "text": "・be desperate for a job  "
          },
          {
            "line": 206,
            "text": "用途: 仕事を非常に必要としている、または何としても得たいと思っていることを表す。  "
          },
          {
            "line": 207,
            "text": "例: He was desperate for a job after months of unemployment.  "
          },
          {
            "line": 208,
            "text": "訳: 彼は何か月も失業した後、仕事を切実に求めていた。  "
          },
          {
            "line": 210,
            "text": "・be desperate for money/attention  "
          },
          {
            "line": 211,
            "text": "用途: 金銭や他人からの注目を極度に必要・欲求していることを表す。  "
          },
          {
            "line": 212,
            "text": "例: The young performer seemed desperate for attention.  "
          },
          {
            "line": 213,
            "text": "訳: その若い出演者は注目を必死に求めているようだった。  "
          },
          {
            "line": 215,
            "text": "・be desperate to do  "
          },
          {
            "line": 216,
            "text": "用途: 何かをどうしてもしたい、または何としても実現したいという強い欲求を表す。  "
          },
          {
            "line": 217,
            "text": "例: She was desperate to find a way home before dark.  "
          },
          {
            "line": 218,
            "text": "訳: 彼女は暗くなる前に帰る方法をどうしても見つけたかった。  "
          },
          {
            "line": 220,
            "text": "・be desperate for someone to do  "
          },
          {
            "line": 221,
            "text": "用途: 他人に特定の行動をどうしてもしてほしいと望むことを表す。  "
          },
          {
            "line": 222,
            "text": "例: The parents were desperate for their son to come home safely.  "
          },
          {
            "line": 223,
            "text": "訳: その両親は息子に無事帰ってきてほしいと切に願っていた。  "
          },
          {
            "line": 225,
            "text": "・be desperate for a coffee  "
          },
          {
            "line": 226,
            "text": "用途: 危機的な必要ではなく、日常的なものを「とても欲しい」とくだけて言う。  "
          },
          {
            "line": 227,
            "text": "例: I’m desperate for a coffee after that early meeting.  "
          },
          {
            "line": 228,
            "text": "訳: あの早朝の会議の後で、コーヒーがすごく飲みたい。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 272,
            "text": "【コロケーション】"
          },
          {
            "line": 274,
            "text": "・a desperate situation  "
          },
          {
            "line": 275,
            "text": "用途: 事態が非常に悪く、危険または絶望的に近いことを表す。  "
          },
          {
            "line": 276,
            "text": "例: The aid workers were trying to evacuate people from a desperate situation.  "
          },
          {
            "line": 277,
            "text": "訳: 救援隊員たちは、非常に危険な状況から人々を避難させようとしていた。  "
          },
          {
            "line": 279,
            "text": "・be in desperate need of 〈物・支援〉  "
          },
          {
            "line": 280,
            "text": "用途: 物・支援・対策が極度に不足し、緊急に必要であることを表す。  "
          },
          {
            "line": 281,
            "text": "例: The hospital is in desperate need of blood supplies.  "
          },
          {
            "line": 282,
            "text": "訳: その病院は血液の供給を極度に必要としている。  "
          },
          {
            "line": 284,
            "text": "・a desperate shortage of 〈物〉  "
          },
          {
            "line": 285,
            "text": "用途: 物資や資源が極端に不足していることを表す。  "
          },
          {
            "line": 286,
            "text": "例: The region is facing a desperate shortage of clean water.  "
          },
          {
            "line": 287,
            "text": "訳: その地域は清潔な水の深刻な不足に直面している。  "
          },
          {
            "line": 289,
            "text": "・be in desperate straits  "
          },
          {
            "line": 290,
            "text": "用途: 経済・生活・組織などが非常に困窮した状況にあることを表す。  "
          },
          {
            "line": 291,
            "text": "例: Many small farms are in desperate straits after the prolonged drought.  "
          },
          {
            "line": 292,
            "text": "訳: 長引く干ばつの後、多くの小規模農家が非常に困窮している。  "
          },
          {
            "line": 294,
            "text": "・desperate poverty  "
          },
          {
            "line": 295,
            "text": "用途: 貧困が極度で、生活を維持することが非常に難しい状態を表す。  "
          },
          {
            "line": 296,
            "text": "例: The report describes families living in desperate poverty.  "
          },
          {
            "line": 297,
            "text": "訳: その報告書は極度の貧困の中で暮らす家族について述べている。  "
          },
          {
            "line": 299,
            "text": "・a desperate illness/crisis  "
          },
          {
            "line": 300,
            "text": "用途: 病状や危機が非常に重く、改善や解決の見込みが薄いことを表す。  "
          },
          {
            "line": 301,
            "text": "例: The patient was in a desperate condition when the ambulance arrived.  "
          },
          {
            "line": 302,
            "text": "訳: 救急車が到着したとき、患者の状態は非常に深刻だった。  "
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
      "input_body_sha256": "c00b2207548c03e5eb31796c9607af43eb3c089dae2f9a8b96dc2bda9464a00e",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "米: /ˈdɛspərət/｜英: /ˈdespərət/。いずれも3音節で、第1音節に主強勢がある。米音では第1音節を /dɛs/、英音では /des/ と示す辞書がある。米英とも /ˈdespərət/ や /ˈdɛspərɪt/ に近い別表記が見られるが、語末の -ate はここでは /ət/ で、「エイト」とは読まない。第2音節の /pər/ は米音では r を伴う /pɚ/、英音では /pə/ に近い。desperately は /ˈdespərətli/、desperation は /ˌdespəˈreɪʃən/ で、名詞では強勢位置が変わる。  "
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
      "input_body_sha256": "c00b2207548c03e5eb31796c9607af43eb3c089dae2f9a8b96dc2bda9464a00e",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "米: /ˈdɛspərət/｜英: /ˈdespərət/。いずれも3音節で、第1音節に主強勢がある。米音では第1音節を /dɛs/、英音では /des/ と示す辞書がある。米英とも /ˈdespərət/ や /ˈdɛspərɪt/ に近い別表記が見られるが、語末の -ate はここでは /ət/ で、「エイト」とは読まない。第2音節の /pər/ は米音では r を伴う /pɚ/、英音では /pə/ に近い。desperately は /ˈdespərətli/、desperation は /ˌdespəˈreɪʃən/ で、名詞では強勢位置が変わる。  "
          }
        ],
        "etymology": [
          {
            "line": 17,
            "text": "＃語源"
          },
          {
            "line": 19,
            "text": "中英語 desperat が古フランス語を経て、ラテン語 desperatus「希望を失った、絶望した」にさかのぼる。これは動詞 desperare「絶望する、望みがないとあきらめる」の過去分詞で、de- と sperare「望む、希望する」から成る。まず「絶望している」という人の状態を表し、そこから、絶望に動かされた無謀な行動、成功の望みが薄い試み、状況の深刻さ、極度の必要・欲求へ意味が広がった。  "
          },
          {
            "line": 21,
            "text": "despair「絶望する／絶望」、desperately「必死に、非常に」、desperation「絶望、やけ、切迫した状態」は同じ語源に連なる。語源上の「希望がない」という核は現代の全用法を文字どおりに規定するものではなく、desperate for a coffee のようなくだけた強い欲求では、必ずしも実際の絶望や危険を意味しない。  "
          }
        ],
        "word_formation": [
          {
            "line": 23,
            "text": "＃語形成"
          },
          {
            "line": 25,
            "text": "・desperately：desperate の副詞。「絶望的・必死の状態で」のほか、desperately need/want のように「非常に、切実に」の意味でも使う。  "
          },
          {
            "line": 26,
            "text": "・desperation：名詞。「絶望、やけ、切迫した状態」または、その状態から出る必死の行動。  "
          },
          {
            "line": 27,
            "text": "・desperateness：名詞。「絶望的・切迫した状態」。desperation より使用頻度が低く、説明的・硬めに響く。  "
          },
          {
            "line": 28,
            "text": "・desperado：絶望や無謀さと結び付いた「無法者、凶悪犯」を表す名詞。desperate の通常の名詞形ではなく、別に語彙化した語である。  "
          }
        ],
        "core_image": [
          {
            "line": 30,
            "text": "＃コアイメージ"
          },
          {
            "line": 32,
            "text": "desperate の中心には、「希望や余裕がほとんどなく、事態を変えるために限界まで切迫している」という感覚がある。人の状態では絶望が無謀さや必死さにつながり、行動では最後の手段になり、必要・欲求では強さが極限に達し、状況では深刻さや危険として現れる。  "
          },
          {
            "line": 34,
            "text": "・絶望して余裕がない → 「絶望して必死の、危険を顧みない」（語義1）  "
          },
          {
            "line": 35,
            "text": "・望みが薄くても最後に試みる → 「必死の、最後の手段の」（語義2）  "
          },
          {
            "line": 36,
            "text": "・必要・欲求が極度に強い → 「～を非常に必要とする、切望する」（語義3）  "
          },
          {
            "line": 37,
            "text": "・状況や不足が限界的に悪い → 「非常に深刻な、危険な、極度の」（語義4）  "
          },
          {
            "line": 39,
            "text": "語義1は人・集団の心理状態、語義2はその状態から出る行動や試み、語義3は対象への強い必要・欲求、語義4は状況や状態そのものの深刻さに焦点がある。特に desperate for 〈名詞〉は「その人が強く必要・欲求を感じる」、in desperate need of 〈名詞〉は「状況が極度に不足している」という違いに注意する。  "
          }
        ],
        "sense_structure": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】ほとんど希望がなく、状況を変えるためなら危険や結果を十分に考えず何でもしようとする心理状態。人・集団について使うと「絶望した」「追い詰められた」「必死の」という意味になり、文脈によっては無謀さや暴力性を含むが、必ずしも暴力的とは限らない。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 116,
            "text": "【日本語訳・定義】他の方法が失敗した後、または成功の見込みがほとんどない状況で行われる行動・試み。危険を伴うことがあるが、語の必須条件は「追い詰められた状況での最後の努力」であり、結果が実際に失敗することまでは含まない。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 190,
            "text": "【日本語訳・定義】人が何かを極度に必要としたり、強く欲しがったりしている状態。desperate for 〈名詞〉 と desperate to do の形を取り、対象は仕事・金・助けのような切実な必要から、愛情・注目・コーヒーのような強い欲求まで広い。この用法だけでは、実際に希望を失ったり危険な行動を取ったりしているとは限らない。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 264,
            "text": "【日本語訳・定義】状況、病状、経済状態、不足などが非常に悪く、改善の望みが薄い、または緊急の対処を要する状態。人の心理状態ではなく、対象となる状況そのものの深刻さを評価する。desperate need は「極度の必要・不足」、desperate shortage は「深刻な不足」を表す。  "
          }
        ],
        "frequency_register": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 47,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 49,
            "text": "【レジスター/領域】標準的な一般語。感情描写、報道、物語、災害・救助、社会問題で広く使う。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 118,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 120,
            "text": "【レジスター/領域】標準的な一般語。報道、政治、競技、救助、交渉、ビジネス、物語で広く使う。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 192,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 194,
            "text": "【レジスター/領域】標準的な一般語。求人、支援要請、感情描写で広く使う。desperate for a coffee のような「とても欲しい」という用法はくだけた会話で特に自然である。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 266,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 268,
            "text": "【レジスター/領域】標準的な一般語。報道、社会問題、医療、経済、災害、政策で広く使う。  "
          }
        ],
        "frames": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 51,
            "text": "【文法パターン】be/feel/look/get/grow/become desperate＝絶望する・追い詰められた状態になる／be desperate about 〈事〉＝〈事〉に絶望・困り果てている／desperate with 〈感情・苦痛〉＝〈感情・苦痛〉で取り乱している／a desperate 〈人・集団〉＝絶望して必死の〈人・集団〉  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 122,
            "text": "【文法パターン】make a desperate attempt/bid/effort to do＝～するために必死の試み・努力をする／take desperate measures＝非常手段を取る／a desperate struggle/battle/search for 〈目的〉＝〈目的〉のための必死の闘い・捜索／a desperate plea/appeal for 〈援助・行動〉＝切迫した懇願・訴え  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 196,
            "text": "【文法パターン】be/feel desperate for 〈物・支援・機会〉＝～を非常に必要とする・切望する／be desperate to do＝どうしても～したい／be desperate for someone to do＝人にどうしても～してほしい／look desperate for 〈物・承認〉＝～を必死に求めているように見える  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 270,
            "text": "【文法パターン】be in a desperate situation/condition/state＝非常に深刻な状況・状態にある／face a desperate shortage of 〈物〉＝〈物〉の深刻な不足に直面する／be in desperate need of 〈物・支援〉＝〈物・支援〉を極度に必要とする状況にある／be in desperate straits＝非常に困窮した状況にある／a desperate illness/crisis＝深刻な病気・危機  "
          }
        ],
        "collocations_examples": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 53,
            "text": "【コロケーション】"
          },
          {
            "line": 55,
            "text": "・be/feel desperate  "
          },
          {
            "line": 56,
            "text": "用途: 人が希望を失い、追い詰められた心理状態にあることを表す。  "
          },
          {
            "line": 57,
            "text": "例: After three days without news, the family felt desperate.  "
          },
          {
            "line": 58,
            "text": "訳: 3日間知らせがなく、家族は絶望的な気持ちになった。  "
          },
          {
            "line": 60,
            "text": "・grow increasingly desperate  "
          },
          {
            "line": 61,
            "text": "用途: 時間の経過とともに、絶望や切迫感が強まることを表す。  "
          },
          {
            "line": 62,
            "text": "例: The trapped hikers grew increasingly desperate as night fell.  "
          },
          {
            "line": 63,
            "text": "訳: 閉じ込められたハイカーたちは、夜になるにつれてますます切迫した。  "
          },
          {
            "line": 65,
            "text": "・a desperate man/ woman/ family  "
          },
          {
            "line": 66,
            "text": "用途: 希望や余裕を失い、極端な行動に出かねない人や家族を描写する。  "
          },
          {
            "line": 67,
            "text": "例: The police were looking for a desperate man who had lost everything.  "
          },
          {
            "line": 68,
            "text": "訳: 警察は、すべてを失って追い詰められた男を捜していた。  "
          },
          {
            "line": 70,
            "text": "・a desperate cry/plea for help  "
          },
          {
            "line": 71,
            "text": "用途: 絶望や切迫感を示す助けの叫び・懇願を表す。  "
          },
          {
            "line": 72,
            "text": "例: We heard a desperate cry for help from the riverbank.  "
          },
          {
            "line": 73,
            "text": "訳: 私たちは川岸からの必死の助けを求める叫び声を聞いた。  "
          },
          {
            "line": 75,
            "text": "・desperate with anxiety/grief  "
          },
          {
            "line": 76,
            "text": "用途: 強い不安や悲嘆で平静を失いかけている状態を表す。  "
          },
          {
            "line": 77,
            "text": "例: Desperate with anxiety, she called every hospital in the city.  "
          },
          {
            "line": 78,
            "text": "訳: 彼女は不安で取り乱し、市内の病院すべてに電話をかけた。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 124,
            "text": "【コロケーション】"
          },
          {
            "line": 126,
            "text": "・a desperate attempt to do  "
          },
          {
            "line": 127,
            "text": "用途: 成功の望みが薄くても、最後に何かをしようとする試みを表す。  "
          },
          {
            "line": 128,
            "text": "例: She made a desperate attempt to reach the child before the door closed.  "
          },
          {
            "line": 129,
            "text": "訳: 彼女は扉が閉まる前にその子に届こうと必死に試みた。  "
          },
          {
            "line": 131,
            "text": "・make a desperate bid for 〈自由・勝利・主導権〉  "
          },
          {
            "line": 132,
            "text": "用途: 重要な目標を得るための最後の、しばしば危険な努力を表す。  "
          },
          {
            "line": 133,
            "text": "例: The team made a desperate bid for victory in the final minute.  "
          },
          {
            "line": 134,
            "text": "訳: そのチームは最後の1分に勝利を懸けた必死の攻勢に出た。  "
          },
          {
            "line": 136,
            "text": "・take desperate measures  "
          },
          {
            "line": 137,
            "text": "用途: 通常の方法では解決できない問題に対して、非常手段を取ることを表す。  "
          },
          {
            "line": 138,
            "text": "例: The company took desperate measures to avoid bankruptcy.  "
          },
          {
            "line": 139,
            "text": "訳: その会社は破産を避けるために非常手段を取った。  "
          },
          {
            "line": 141,
            "text": "・a desperate struggle/battle to do  "
          },
          {
            "line": 142,
            "text": "用途: 勝ち目が薄くても、目的のために力を尽くす闘いを表す。  "
          },
          {
            "line": 143,
            "text": "例: The doctors began a desperate battle to save his life.  "
          },
          {
            "line": 144,
            "text": "訳: 医師たちは彼の命を救うための必死の闘いを始めた。  "
          },
          {
            "line": 146,
            "text": "・a desperate search for 〈人・解決策〉  "
          },
          {
            "line": 147,
            "text": "用途: 時間や可能性が限られた中で、最後まで行う切迫した捜索を表す。  "
          },
          {
            "line": 148,
            "text": "例: Volunteers organized a desperate search for the missing child.  "
          },
          {
            "line": 149,
            "text": "訳: ボランティアは行方不明の子どもを必死に捜す活動を組織した。  "
          },
          {
            "line": 151,
            "text": "・a desperate plea/appeal for 〈助け・平静〉  "
          },
          {
            "line": 152,
            "text": "用途: ほかに頼る手段がないような切迫した懇願・訴えを表す。  "
          },
          {
            "line": 153,
            "text": "例: The prisoner made a desperate plea for medical treatment.  "
          },
          {
            "line": 154,
            "text": "訳: その収監者は医療措置を求めて必死に懇願した。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 198,
            "text": "【コロケーション】"
          },
          {
            "line": 200,
            "text": "・be desperate for help  "
          },
          {
            "line": 201,
            "text": "用途: 助けを極度に必要としていることを表す。  "
          },
          {
            "line": 202,
            "text": "例: The villagers are desperate for help after the flood.  "
          },
          {
            "line": 203,
            "text": "訳: その村人たちは洪水の後、助けを切実に必要としている。  "
          },
          {
            "line": 205,
            "text": "・be desperate for a job  "
          },
          {
            "line": 206,
            "text": "用途: 仕事を非常に必要としている、または何としても得たいと思っていることを表す。  "
          },
          {
            "line": 207,
            "text": "例: He was desperate for a job after months of unemployment.  "
          },
          {
            "line": 208,
            "text": "訳: 彼は何か月も失業した後、仕事を切実に求めていた。  "
          },
          {
            "line": 210,
            "text": "・be desperate for money/attention  "
          },
          {
            "line": 211,
            "text": "用途: 金銭や他人からの注目を極度に必要・欲求していることを表す。  "
          },
          {
            "line": 212,
            "text": "例: The young performer seemed desperate for attention.  "
          },
          {
            "line": 213,
            "text": "訳: その若い出演者は注目を必死に求めているようだった。  "
          },
          {
            "line": 215,
            "text": "・be desperate to do  "
          },
          {
            "line": 216,
            "text": "用途: 何かをどうしてもしたい、または何としても実現したいという強い欲求を表す。  "
          },
          {
            "line": 217,
            "text": "例: She was desperate to find a way home before dark.  "
          },
          {
            "line": 218,
            "text": "訳: 彼女は暗くなる前に帰る方法をどうしても見つけたかった。  "
          },
          {
            "line": 220,
            "text": "・be desperate for someone to do  "
          },
          {
            "line": 221,
            "text": "用途: 他人に特定の行動をどうしてもしてほしいと望むことを表す。  "
          },
          {
            "line": 222,
            "text": "例: The parents were desperate for their son to come home safely.  "
          },
          {
            "line": 223,
            "text": "訳: その両親は息子に無事帰ってきてほしいと切に願っていた。  "
          },
          {
            "line": 225,
            "text": "・be desperate for a coffee  "
          },
          {
            "line": 226,
            "text": "用途: 危機的な必要ではなく、日常的なものを「とても欲しい」とくだけて言う。  "
          },
          {
            "line": 227,
            "text": "例: I’m desperate for a coffee after that early meeting.  "
          },
          {
            "line": 228,
            "text": "訳: あの早朝の会議の後で、コーヒーがすごく飲みたい。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 272,
            "text": "【コロケーション】"
          },
          {
            "line": 274,
            "text": "・a desperate situation  "
          },
          {
            "line": 275,
            "text": "用途: 事態が非常に悪く、危険または絶望的に近いことを表す。  "
          },
          {
            "line": 276,
            "text": "例: The aid workers were trying to evacuate people from a desperate situation.  "
          },
          {
            "line": 277,
            "text": "訳: 救援隊員たちは、非常に危険な状況から人々を避難させようとしていた。  "
          },
          {
            "line": 279,
            "text": "・be in desperate need of 〈物・支援〉  "
          },
          {
            "line": 280,
            "text": "用途: 物・支援・対策が極度に不足し、緊急に必要であることを表す。  "
          },
          {
            "line": 281,
            "text": "例: The hospital is in desperate need of blood supplies.  "
          },
          {
            "line": 282,
            "text": "訳: その病院は血液の供給を極度に必要としている。  "
          },
          {
            "line": 284,
            "text": "・a desperate shortage of 〈物〉  "
          },
          {
            "line": 285,
            "text": "用途: 物資や資源が極端に不足していることを表す。  "
          },
          {
            "line": 286,
            "text": "例: The region is facing a desperate shortage of clean water.  "
          },
          {
            "line": 287,
            "text": "訳: その地域は清潔な水の深刻な不足に直面している。  "
          },
          {
            "line": 289,
            "text": "・be in desperate straits  "
          },
          {
            "line": 290,
            "text": "用途: 経済・生活・組織などが非常に困窮した状況にあることを表す。  "
          },
          {
            "line": 291,
            "text": "例: Many small farms are in desperate straits after the prolonged drought.  "
          },
          {
            "line": 292,
            "text": "訳: 長引く干ばつの後、多くの小規模農家が非常に困窮している。  "
          },
          {
            "line": 294,
            "text": "・desperate poverty  "
          },
          {
            "line": 295,
            "text": "用途: 貧困が極度で、生活を維持することが非常に難しい状態を表す。  "
          },
          {
            "line": 296,
            "text": "例: The report describes families living in desperate poverty.  "
          },
          {
            "line": 297,
            "text": "訳: その報告書は極度の貧困の中で暮らす家族について述べている。  "
          },
          {
            "line": 299,
            "text": "・a desperate illness/crisis  "
          },
          {
            "line": 300,
            "text": "用途: 病状や危機が非常に重く、改善や解決の見込みが薄いことを表す。  "
          },
          {
            "line": 301,
            "text": "例: The patient was in a desperate condition when the ambulance arrived.  "
          },
          {
            "line": 302,
            "text": "訳: 救急車が到着したとき、患者の状態は非常に深刻だった。  "
          }
        ],
        "usage_notes": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 80,
            "text": "【語法・注意】この語義の desperate は単なる「熱心な」「決意の固い」ではなく、希望のなさや追い詰められた余裕のなさを含む。be desperate to do は「～したくてたまらない／～することを切望している」という語義3になりやすく、後続の to不定詞だけで語義1の「絶望している」と決めつけない。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 156,
            "text": "【語法・注意】desperate attempt は「必死の試み」であって、必ずしも無謀・違法という意味ではない。last-ditch attempt は「最後の手段」という時間的・戦略的な面を強調し、desperate attempt はそこに切迫感や成功の望みの薄さが加わる。take desperate measures も、手段が必ず非倫理的・暴力的だと決めつけない。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 230,
            "text": "【語法・注意】名詞を続けるときは desperate for 〈名詞〉、動作を続けるときは desperate to do であり、×desperate doing や ×desperate for do とはしない。be desperate to do は「～したくてたまらない」で、必ずしも「絶望して無謀なことをする」ではない。want、need より強く、文脈によっては焦りや感情的な弱さまで伝える。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 304,
            "text": "【語法・注意】in desperate need of 〈名詞〉は、状況や不足が深刻であることに焦点を置く。一方、be desperate for 〈名詞〉は、主語である人・組織が対象を強く必要・欲求していることに焦点を置く。たとえば The hospital is in desperate need of blood は病院の不足を、The patient is desperate for help は患者の切実な求めを表す。desperate は「必ず完全に絶望的」と断定する語ではなく、深刻さ・危険さ・緊急性を強く評価する語としても使う。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 43,
            "text": "1. 【形容詞・叙述用法中心／限定用法も可】絶望して必死の、危険を顧みない"
          },
          {
            "line": 82,
            "text": "【類義語】"
          },
          {
            "line": 84,
            "text": "・despairing  "
          },
          {
            "line": 85,
            "text": "定義: 希望を失い、絶望を感じたり示したりしている。  "
          },
          {
            "line": 86,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 87,
            "text": "違い: despairing は内面的な絶望の表出に焦点があり、desperate のように危険を顧みない行動まで必ず含むわけではない。  "
          },
          {
            "line": 88,
            "text": "例: He gave me a despairing look when the plan failed.  "
          },
          {
            "line": 89,
            "text": "訳: 計画が失敗すると、彼は私に絶望したような顔を向けた。  "
          },
          {
            "line": 91,
            "text": "・hopeless  "
          },
          {
            "line": 92,
            "text": "定義: 希望や成功の見込みがない、またはそう感じている。  "
          },
          {
            "line": 93,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 94,
            "text": "違い: hopeless は望みのなさや諦めに焦点があり、desperate はその状態から生じる必死の行動・切迫感を強く示す。  "
          },
          {
            "line": 95,
            "text": "例: The rescue team refused to call the search hopeless.  "
          },
          {
            "line": 96,
            "text": "訳: 救助隊は捜索を見込みがないとは認めようとしなかった。  "
          },
          {
            "line": 98,
            "text": "・frantic  "
          },
          {
            "line": 99,
            "text": "定義: 恐怖・不安・急ぎで取り乱し、落ち着いて行動できない。  "
          },
          {
            "line": 100,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 101,
            "text": "違い: frantic は動揺や慌ただしさに焦点があり、desperate は希望のなさや極端な必要をより強く含む。  "
          },
          {
            "line": 102,
            "text": "例: Frantic parents searched the crowded station for their child.  "
          },
          {
            "line": 103,
            "text": "訳: 取り乱した両親は、混雑した駅で子どもを捜した。  "
          },
          {
            "line": 105,
            "text": "【反意語】"
          },
          {
            "line": 107,
            "text": "・hopeful  "
          },
          {
            "line": 108,
            "text": "定義: よい結果や成功の可能性を信じ、希望を持っている。  "
          },
          {
            "line": 109,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 110,
            "text": "違い: hopeful は希望が残っている状態、desperate は希望がほとんどなく追い詰められた状態を表す。両者は心理状態の軸で対立する。  "
          },
          {
            "line": 111,
            "text": "例: The family remained hopeful despite the long wait.  "
          },
          {
            "line": 112,
            "text": "訳: 長く待たされても、その家族は希望を失わなかった。  "
          },
          {
            "line": 114,
            "text": "2. 【形容詞・通常限定用法】（行動・試みが）最後の手段の、成功の望みが薄い、必死の"
          },
          {
            "line": 158,
            "text": "【類義語】"
          },
          {
            "line": 160,
            "text": "・last-ditch  "
          },
          {
            "line": 161,
            "text": "定義: ほかの手段が尽きた段階で行う、最後の。  "
          },
          {
            "line": 162,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 163,
            "text": "違い: last-ditch は最後の機会という順序に焦点があり、desperate は行為者の切迫感や成功の見込みの薄さをより強く示す。  "
          },
          {
            "line": 164,
            "text": "例: The board approved a last-ditch plan to save the project.  "
          },
          {
            "line": 165,
            "text": "訳: 取締役会はプロジェクトを救うための最後の計画を承認した。  "
          },
          {
            "line": 167,
            "text": "・frantic  "
          },
          {
            "line": 168,
            "text": "定義: 急ぎや不安で取り乱した、必死の。  "
          },
          {
            "line": 169,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 170,
            "text": "違い: frantic は行動の慌ただしさ・混乱を表し、desperate は追い詰められた状況と望みの薄さに焦点がある。  "
          },
          {
            "line": 171,
            "text": "例: They launched a frantic search before the storm arrived.  "
          },
          {
            "line": 172,
            "text": "訳: 彼らは嵐が来る前に大急ぎで捜索を始めた。  "
          },
          {
            "line": 174,
            "text": "・drastic  "
          },
          {
            "line": 175,
            "text": "定義: 問題を変えるために、通常より極端で大きな影響を及ぼす。  "
          },
          {
            "line": 176,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 177,
            "text": "違い: drastic は措置の強さ・規模を表すが、desperate のように希望のなさや切迫した動機を必ずしも含まない。  "
          },
          {
            "line": 178,
            "text": "例: The hospital introduced drastic changes to reduce infections.  "
          },
          {
            "line": 179,
            "text": "訳: その病院は感染を減らすために抜本的な変更を導入した。  "
          },
          {
            "line": 181,
            "text": "・do-or-die  "
          },
          {
            "line": 182,
            "text": "定義: 成功しなければ重大な結果になる、絶対に成功させなければならない。  "
          },
          {
            "line": 183,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 184,
            "text": "違い: do-or-die は成功か失敗かの重大な二択を強調し、desperate は試みの切迫感や成功の見込みの薄さを表す。  "
          },
          {
            "line": 185,
            "text": "例: This is a do-or-die match for the team.  "
          },
          {
            "line": 186,
            "text": "訳: これはそのチームにとって絶対に負けられない試合だ。  "
          },
          {
            "line": 188,
            "text": "3. 【形容詞・叙述用法中心】～を非常に必要としている、～を切望している"
          },
          {
            "line": 232,
            "text": "【類義語】"
          },
          {
            "line": 234,
            "text": "・in dire need of 〈物・支援〉  "
          },
          {
            "line": 235,
            "text": "定義: 物や支援を非常に深刻な状態で必要としている。  "
          },
          {
            "line": 236,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 237,
            "text": "違い: in dire need of は客観的な不足・困窮を強調し、desperate for は人の強い欲求・切望にも、くだけた欲しさにも使える。  "
          },
          {
            "line": 238,
            "text": "例: The clinic is in dire need of more nurses.  "
          },
          {
            "line": 239,
            "text": "訳: その診療所は看護師をもっと必要とする深刻な状況にある。  "
          },
          {
            "line": 241,
            "text": "・eager for 〈機会・知らせ〉  "
          },
          {
            "line": 242,
            "text": "定義: 何かを熱心に、楽しみにしながら強く望んでいる。  "
          },
          {
            "line": 243,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 244,
            "text": "違い: eager は期待や前向きな熱意を含みやすく、desperate のような困窮・焦り・追い詰められた感じは必須ではない。  "
          },
          {
            "line": 245,
            "text": "例: The students were eager for the results of the competition.  "
          },
          {
            "line": 246,
            "text": "訳: 学生たちは競技会の結果を心待ちにしていた。  "
          },
          {
            "line": 248,
            "text": "・longing for 〈人・場所・経験〉  "
          },
          {
            "line": 249,
            "text": "定義: 人・場所・過去の経験などを強く恋しく思い、切望している。  "
          },
          {
            "line": 250,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 251,
            "text": "違い: longing for は持続的で感情的なあこがれ・恋しさに焦点があり、desperate for は必要の切迫や欲求の極端な強さを広く表す。  "
          },
          {
            "line": 252,
            "text": "例: She felt a deep longing for her childhood home.  "
          },
          {
            "line": 253,
            "text": "訳: 彼女は子どもの頃の家を深く恋しく思った。  "
          },
          {
            "line": 255,
            "text": "・dying for 〈物・行動〉  "
          },
          {
            "line": 256,
            "text": "定義: くだけて、何かを非常に欲しい・したいと思っている。  "
          },
          {
            "line": 257,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 258,
            "text": "違い: dying for は強調的な口語表現で、文字どおり死ぬ危険や絶望を通常は含まない。desperate for は口語から報道まで使えるが、より切迫した響きが出やすい。  "
          },
          {
            "line": 259,
            "text": "例: I’m dying for a hot shower after the hike.  "
          },
          {
            "line": 260,
            "text": "訳: ハイキングの後で、熱いシャワーを浴びたくてたまらない。  "
          },
          {
            "line": 262,
            "text": "4. 【形容詞・限定用法中心／叙述用法も可】（状況・状態が）非常に深刻な、危険な、極度の"
          },
          {
            "line": 306,
            "text": "【類義語】"
          },
          {
            "line": 308,
            "text": "・dire  "
          },
          {
            "line": 309,
            "text": "定義: 状況が非常に深刻で、緊急の対処や救済を必要とする。  "
          },
          {
            "line": 310,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 311,
            "text": "違い: dire は状況の深刻さを硬く客観的に述べやすく、desperate はそこに絶望感・切迫感・極端さが加わる。  "
          },
          {
            "line": 312,
            "text": "例: The country is facing a dire shortage of food.  "
          },
          {
            "line": 313,
            "text": "訳: その国は食料の深刻な不足に直面している。  "
          },
          {
            "line": 315,
            "text": "・grave  "
          },
          {
            "line": 316,
            "text": "定義: 危険・結果・責任などが非常に重大で、軽視できない。  "
          },
          {
            "line": 317,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 318,
            "text": "違い: grave は重大さ・深刻さを改まって示し、desperate のように改善の望みの薄さや切迫した努力まで含むとは限らない。  "
          },
          {
            "line": 319,
            "text": "例: The accident raised grave concerns about safety.  "
          },
          {
            "line": 320,
            "text": "訳: その事故は安全性について重大な懸念を生じさせた。  "
          },
          {
            "line": 322,
            "text": "・critical  "
          },
          {
            "line": 323,
            "text": "定義: 状況が危機的で、直ちに判断・対応しなければならない。  "
          },
          {
            "line": 324,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 325,
            "text": "違い: critical は危機の段階や緊急性に焦点があり、desperate は極度の悪さや望みの薄さをより強く感じさせる。  "
          },
          {
            "line": 326,
            "text": "例: The patient remains in critical condition.  "
          },
          {
            "line": 327,
            "text": "訳: その患者は依然として危篤状態にある。  "
          },
          {
            "line": 329,
            "text": "・severe  "
          },
          {
            "line": 330,
            "text": "定義: 程度が非常に強く、苦痛・損害・不足などが大きい。  "
          },
          {
            "line": 331,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 332,
            "text": "違い: severe は強度の大きさを広く表す客観的な語で、desperate のような追い詰められた評価やほとんど望みのない感じは必須ではない。  "
          },
          {
            "line": 333,
            "text": "例: The area suffered severe water shortages.  "
          },
          {
            "line": 334,
            "text": "訳: その地域は深刻な水不足に苦しんだ。  "
          },
          {
            "line": 336,
            "text": "【反意語】"
          },
          {
            "line": 338,
            "text": "・promising  "
          },
          {
            "line": 339,
            "text": "定義: よい結果や改善の見込みがあり、将来に希望を持たせる。  "
          },
          {
            "line": 340,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 341,
            "text": "違い: promising は状況の明るい見込みを示し、desperate は状況が非常に悪く改善の望みが薄いことを示す。状況評価の軸で対立する。  "
          },
          {
            "line": 342,
            "text": "例: The latest figures give a more promising picture of the economy.  "
          },
          {
            "line": 343,
            "text": "訳: 最新の数字は経済についてより明るい見通しを示している。  "
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
