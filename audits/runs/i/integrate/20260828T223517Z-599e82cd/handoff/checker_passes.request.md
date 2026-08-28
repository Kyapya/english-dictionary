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
      "input_body_sha256": "f81f71e168187dbc968e77848fc623c5b7a1a06b513de11c30f7548088338629",
      "input_sections": {
        "definitions": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 51,
            "text": "【日本語訳・定義】別々に存在していた要素、機能、部門、制度などを組み合わせ、一つのまとまりとして働くようにする。同じ場所に集める、同じ一覧に載せるということではなく、組み合わせた後に全体として機能することまでを含意する。目的語は部品や路線のような具体物でも、方針、データ、部門のような抽象物でもよい。統合の結果として元の要素が識別できなくなることまでは必要としない。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 162,
            "text": "【日本語訳・定義】過去分詞 integrated が形容詞として定着した用法で、多くの部分や機能が結び付き、一つのまとまりとして働くようになっていることを表す。限定用法と叙述用法の両方で使い、程度は fully、highly、closely、tightly などの副詞で示す。an integrated circuit（集積回路）、an integrated approach（統合的な取り組み）のように、専門的な複合表現も作る。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 266,
            "text": "【日本語訳・定義】別々のシステム、機器、サービス、路線などが結び付いて、一つのまとまりとして働くようになる。主語は人ではなく、装置、ソフトウェア、制度などの物や仕組みである。目的語は取らず、結び付く相手は with、まとまって入る先は into で示す。ソフトウェアの説明では「他の製品と連携して動く」という意味でよく使う。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 342,
            "text": "【日本語訳・定義】新しく加わった人や、これまで別扱いされてきた集団を、既存の共同体、組織、学級の対等な構成員として受け入れ、実際に活動へ加われるようにする。主語は受け入れる側の人、機関、制度で、目的語は加わる側の人や集団である。ただし再帰代名詞を目的語にとる integrate oneself into では、加わる側の人が主語と目的語を兼ねる。在籍させるだけでなく、周囲との関係が成り立つところまでを含意する。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 446,
            "text": "【日本語訳・定義】新しく入った人が、集団や社会の一員として周囲と関係を築き、実際に活動へ加わるようになる。主語は加わる側の人や集団で、目的語は取らない。入っていく先は into、打ち解ける相手は with で示し、副詞を伴って程度や成否を述べることが多い。本人の側から見た変化を述べる点で、受け入れる側を主語にする語義4と役割が逆になる。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 538,
            "text": "【日本語訳・定義】学校、軍、公共施設、居住地区などで、人種を主とし、辞書によっては性別や出身国も挙げる属性を理由に人を分けていた制度をやめ、分けられていた人々が同じ場所や組織に対等な構成員として属せるようにする。またそうなる。米国で公民権運動期の学校の人種統合をめぐって定着した用法で、現在も歴史的記述や社会・法律の議論で使う。目的語は制度・施設であり、制度上の分離の撤廃を述べる点で、個々の人や集団を目的語にして受け入れを述べる語義4と区別する。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 616,
            "text": "【日本語訳・定義】学校、地区、施設などが、人種、宗派、性別などを理由とする分離をやめ、これまで分けられていた人々が同じ場に属している状態であることを表す。語義6の動詞用法に対応する形容詞用法である。米国では人種についての用法が中心で、公民権運動以後の社会、教育、歴史の記述に定着している。北アイルランドではカトリックとプロテスタントの児童をともに教える学校を指す。名詞の前に置く限定用法が中心で、修飾する対象は制度、施設、地域や人の集団であり、個人ではない。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 689,
            "text": "【日本語訳・定義】微積分で、関数や式の積分を求める。微分の逆の操作で、微小な部分を足し合わせて面積、体積、総量などの全体量を得ることに当たる。目的語には積分の対象となる関数や式が来る。積分する変数は with respect to で示し、over は積分する変数や領域を導く。積分区間の上下限は from … to … で示す。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 59,
            "text": "【コロケーション】"
          },
          {
            "line": 61,
            "text": "・integrate 〈new features〉 into 〈the existing platform〉  "
          },
          {
            "line": 62,
            "text": "用途: 新しい機能を既存の基盤へ組み込むことを表す、技術文脈の中心的な形。  "
          },
          {
            "line": 63,
            "text": "例: The team integrated two new payment methods into the existing checkout system.  "
          },
          {
            "line": 64,
            "text": "訳: チームは二つの新しい支払い方法を、既存の購入手続きの仕組みに組み込んだ。  "
          },
          {
            "line": 66,
            "text": "・integrate 〈the logistics network〉 with 〈a courier service〉  "
          },
          {
            "line": 67,
            "text": "用途: 対等な二つの仕組み・組織を結び付けて一体にする。  "
          },
          {
            "line": 68,
            "text": "例: The company integrated its logistics network with a regional courier service.  "
          },
          {
            "line": 69,
            "text": "訳: その会社は自社の物流網を地域の宅配業者と統合した。  "
          },
          {
            "line": 71,
            "text": "・fully integrate 〈the two departments〉  "
          },
          {
            "line": 72,
            "text": "用途: 統合の程度を副詞で示す。fully、closely、seamlessly、successfully がよく使われる。  "
          },
          {
            "line": 73,
            "text": "例: It took two years to fully integrate the two departments after the merger.  "
          },
          {
            "line": 74,
            "text": "訳: 合併後、二つの部門を完全に統合するのに2年かかった。  "
          },
          {
            "line": 76,
            "text": "・integrate 〈data〉 from 〈multiple sources〉  "
          },
          {
            "line": 77,
            "text": "用途: 出所の異なる情報を一つにまとめることを表す。  "
          },
          {
            "line": 78,
            "text": "例: The dashboard integrates data from multiple sources into a single view.  "
          },
          {
            "line": 79,
            "text": "訳: そのダッシュボードは複数の出所のデータを一つの画面にまとめている。  "
          },
          {
            "line": 81,
            "text": "・integrate 〈theory〉 and 〈practice〉  "
          },
          {
            "line": 82,
            "text": "用途: 二つの領域・観点を結び付けて一体として扱う、学術的な言い方。  "
          },
          {
            "line": 83,
            "text": "例: The course integrates theory and practice through weekly fieldwork.  "
          },
          {
            "line": 84,
            "text": "訳: その講座は毎週の実地調査を通じて理論と実践を結び付けている。  "
          },
          {
            "line": 86,
            "text": "・be integrated into 〈the curriculum〉  "
          },
          {
            "line": 87,
            "text": "用途: 受動態で、要素が制度・計画の一部として組み込まれている状態を表す。  "
          },
          {
            "line": 88,
            "text": "例: Digital skills are now integrated into the primary school curriculum.  "
          },
          {
            "line": 89,
            "text": "訳: デジタル技能は今では小学校の教育課程に組み込まれている。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 170,
            "text": "【コロケーション】"
          },
          {
            "line": 172,
            "text": "・an integrated 〈system/approach〉  "
          },
          {
            "line": 173,
            "text": "用途: 複数の要素が一体として働く仕組みややり方を表す、最も基本的な限定用法。  "
          },
          {
            "line": 174,
            "text": "例: The hospital has adopted an integrated approach to chronic pain.  "
          },
          {
            "line": 175,
            "text": "訳: その病院は慢性痛に対して統合的な取り組みを採用している。  "
          },
          {
            "line": 177,
            "text": "・an integrated circuit  "
          },
          {
            "line": 178,
            "text": "用途: 電子工学で、多数の素子を一つのチップにまとめた回路を指す固定した複合語。  "
          },
          {
            "line": 179,
            "text": "例: A modern phone contains billions of transistors on a single integrated circuit.  "
          },
          {
            "line": 180,
            "text": "訳: 現代の携帯電話は一つの集積回路の上に何十億個ものトランジスタを載せている。  "
          },
          {
            "line": 182,
            "text": "・fully integrated  "
          },
          {
            "line": 183,
            "text": "用途: 一体化の程度が完全であることを叙述用法で述べる。  "
          },
          {
            "line": 184,
            "text": "例: The two databases are now fully integrated.  "
          },
          {
            "line": 185,
            "text": "訳: その二つのデータベースは今では完全に統合されている。  "
          },
          {
            "line": 187,
            "text": "・a vertically integrated 〈company〉  "
          },
          {
            "line": 188,
            "text": "用途: 経営学で、原材料の調達から販売までを一社が一貫して担う体制を表す。  "
          },
          {
            "line": 189,
            "text": "例: The group is a vertically integrated producer that grows, roasts, and sells its own coffee.  "
          },
          {
            "line": 190,
            "text": "訳: そのグループは、自社でコーヒーを栽培し焙煎し販売する垂直統合型の生産者である。  "
          },
          {
            "line": 192,
            "text": "・closely integrated with 〈the rest of the network〉  "
          },
          {
            "line": 193,
            "text": "用途: 他の部分との結び付きの強さを叙述用法で述べる。  "
          },
          {
            "line": 194,
            "text": "例: The new terminal is closely integrated with the rest of the airport's rail network.  "
          },
          {
            "line": 195,
            "text": "訳: 新しいターミナルは空港の鉄道網の残りの部分と緊密につながっている。  "
          },
          {
            "line": 197,
            "text": "・an integrated 〈transport network〉  "
          },
          {
            "line": 198,
            "text": "用途: 交通や公共サービスで、複数の手段が一つの体系として使えることを表す。  "
          },
          {
            "line": 199,
            "text": "例: The city promised an integrated transport network with a single ticket for buses and trams.  "
          },
          {
            "line": 200,
            "text": "訳: 市はバスと路面電車を一枚の切符で使える統合交通網を約束した。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 274,
            "text": "【コロケーション】"
          },
          {
            "line": 276,
            "text": "・〈the app〉 integrates with 〈existing tools〉  "
          },
          {
            "line": 277,
            "text": "用途: ソフトウェアやサービスが他製品と連携することを表す、製品説明の定型。  "
          },
          {
            "line": 278,
            "text": "例: The scheduling app integrates with most email clients.  "
          },
          {
            "line": 279,
            "text": "訳: そのスケジュール管理アプリはほとんどのメールソフトと連携する。  "
          },
          {
            "line": 281,
            "text": "・integrate seamlessly with 〈the control software〉  "
          },
          {
            "line": 282,
            "text": "用途: 連携の滑らかさを副詞で強調する。seamlessly、smoothly、easily がよく使われる。  "
          },
          {
            "line": 283,
            "text": "例: The new sensors integrate seamlessly with the factory's existing control software.  "
          },
          {
            "line": 284,
            "text": "訳: 新しいセンサーは工場の既存の制御ソフトと滑らかに連携する。  "
          },
          {
            "line": 286,
            "text": "・〈the two networks〉 integrate into 〈a single system〉  "
          },
          {
            "line": 287,
            "text": "用途: 別々の仕組みが一つの体系へまとまることを表す。  "
          },
          {
            "line": 288,
            "text": "例: The regional rail and bus networks will integrate into a single ticketing system next year.  "
          },
          {
            "line": 289,
            "text": "訳: 地域の鉄道網とバス網は来年、一つの発券システムへまとまる。  "
          },
          {
            "line": 291,
            "text": "・〈the components〉 integrate well  "
          },
          {
            "line": 292,
            "text": "用途: 連携の良し悪しを副詞で評価する。  "
          },
          {
            "line": 293,
            "text": "例: The camera and the editing software integrate well, so files transfer without conversion.  "
          },
          {
            "line": 294,
            "text": "訳: そのカメラと編集ソフトはよく連携するので、ファイルは変換せずに移せる。  "
          },
          {
            "line": 296,
            "text": "・〈the module〉 does not integrate with 〈the older version〉  "
          },
          {
            "line": 297,
            "text": "用途: 連携できないことを否定形で述べる。  "
          },
          {
            "line": 298,
            "text": "例: The new module does not integrate with the older version of the database.  "
          },
          {
            "line": 299,
            "text": "訳: 新しいモジュールは旧版のデータベースとは連携しない。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 350,
            "text": "【コロケーション】"
          },
          {
            "line": 352,
            "text": "・integrate 〈immigrants〉 into 〈society〉  "
          },
          {
            "line": 353,
            "text": "用途: 行政や社会政策で、移民を社会の構成員として受け入れることを表す。  "
          },
          {
            "line": 354,
            "text": "例: The program is designed to integrate recent immigrants into the local labor market.  "
          },
          {
            "line": 355,
            "text": "訳: その事業は、最近来た移民を地域の労働市場へ受け入れることを目的としている。  "
          },
          {
            "line": 357,
            "text": "・integrate 〈children with disabilities〉 into 〈mainstream schools〉  "
          },
          {
            "line": 358,
            "text": "用途: 教育制度で、別枠にされてきた児童を通常の学級へ受け入れることを表す。  "
          },
          {
            "line": 359,
            "text": "例: The district has integrated most children with disabilities into mainstream classrooms.  "
          },
          {
            "line": 360,
            "text": "訳: その学区は障害のある児童の大半を通常学級へ受け入れてきた。  "
          },
          {
            "line": 362,
            "text": "・integrate 〈new employees〉 into 〈the team〉  "
          },
          {
            "line": 363,
            "text": "用途: 人事で、新しい社員を既存のチームの一員にすることを表す。  "
          },
          {
            "line": 364,
            "text": "例: A good mentor can integrate new employees into the team within weeks.  "
          },
          {
            "line": 365,
            "text": "訳: 優れた指導役がいれば、新入社員を数週間でチームの一員にできる。  "
          },
          {
            "line": 367,
            "text": "・integrate oneself into 〈a research group〉  "
          },
          {
            "line": 368,
            "text": "用途: 再帰代名詞を目的語にして、自分から集団に入っていくことを表す。  "
          },
          {
            "line": 369,
            "text": "例: She quickly integrated herself into the research group.  "
          },
          {
            "line": 370,
            "text": "訳: 彼女はすぐに研究グループに入り込んでいった。  "
          },
          {
            "line": 372,
            "text": "・fully integrate 〈refugees〉 into 〈the community〉  "
          },
          {
            "line": 373,
            "text": "用途: 受け入れの程度を副詞で示す。fully、successfully、properly が多い。  "
          },
          {
            "line": 374,
            "text": "例: It takes years to fully integrate refugees into a new community.  "
          },
          {
            "line": 375,
            "text": "訳: 難民を新しい共同体に完全に受け入れるには何年もかかる。  "
          },
          {
            "line": 377,
            "text": "・be integrated into 〈the workforce〉  "
          },
          {
            "line": 378,
            "text": "用途: 受動態で、集団が働く場に受け入れられている状態を表す。  "
          },
          {
            "line": 379,
            "text": "例: Older workers are not always well integrated into the digital workforce.  "
          },
          {
            "line": 380,
            "text": "訳: 高齢の労働者が、デジタル化した職場にいつもうまく受け入れられているとは限らない。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 454,
            "text": "【コロケーション】"
          },
          {
            "line": 456,
            "text": "・〈newcomers〉 integrate into 〈the local community〉  "
          },
          {
            "line": 457,
            "text": "用途: 移住者や転入者が地域の一員になっていくことを表す。  "
          },
          {
            "line": 458,
            "text": "例: Many of the families integrated into the local community within a year.  "
          },
          {
            "line": 459,
            "text": "訳: その家族の多くは1年以内に地域社会に溶け込んだ。  "
          },
          {
            "line": 461,
            "text": "・integrate quickly  "
          },
          {
            "line": 462,
            "text": "用途: 溶け込む速さを副詞で述べる。quickly、easily、slowly が多い。  "
          },
          {
            "line": 463,
            "text": "例: Children usually integrate more quickly than their parents.  "
          },
          {
            "line": 464,
            "text": "訳: 子どもは普通、親よりも早く溶け込む。  "
          },
          {
            "line": 466,
            "text": "・find it hard to integrate  "
          },
          {
            "line": 467,
            "text": "用途: 溶け込むことの難しさを述べる定型。  "
          },
          {
            "line": 468,
            "text": "例: He found it hard to integrate after moving to a new city.  "
          },
          {
            "line": 469,
            "text": "訳: 彼は新しい街に移ってから溶け込むのに苦労した。  "
          },
          {
            "line": 471,
            "text": "・integrate with 〈one's new colleagues〉  "
          },
          {
            "line": 472,
            "text": "用途: 職場で同僚と打ち解けることを表す。  "
          },
          {
            "line": 473,
            "text": "例: She has integrated well with her new colleagues.  "
          },
          {
            "line": 474,
            "text": "訳: 彼女は新しい同僚たちとうまく打ち解けている。  "
          },
          {
            "line": 476,
            "text": "・fail to integrate  "
          },
          {
            "line": 477,
            "text": "用途: 溶け込めないことを述べる、報道や報告書に多い形。  "
          },
          {
            "line": 478,
            "text": "例: The report warned that some young arrivals fail to integrate socially.  "
          },
          {
            "line": 479,
            "text": "訳: その報告書は、若い入国者の一部が社会的に溶け込めていないと警告した。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 546,
            "text": "【コロケーション】"
          },
          {
            "line": 548,
            "text": "・integrate 〈the public schools〉  "
          },
          {
            "line": 549,
            "text": "用途: 公立学校の人種隔離を撤廃することを表す、この語義の中心的な形。  "
          },
          {
            "line": 550,
            "text": "例: A federal court ordered the state to integrate its public schools.  "
          },
          {
            "line": 551,
            "text": "訳: 連邦裁判所は州に対し、公立学校の人種隔離を撤廃するよう命じた。  "
          },
          {
            "line": 553,
            "text": "・integrate 〈the armed forces〉  "
          },
          {
            "line": 554,
            "text": "用途: 軍隊の人種隔離撤廃について述べる、歴史的記述の定型。  "
          },
          {
            "line": 555,
            "text": "例: Truman's 1948 executive order committed the government to integrating the armed forces.  "
          },
          {
            "line": 556,
            "text": "訳: トルーマンの1948年の大統領令は、軍の人種隔離を撤廃することを政府の方針として定めた。  "
          },
          {
            "line": 558,
            "text": "・racially integrate 〈the suburbs〉  "
          },
          {
            "line": 559,
            "text": "用途: 居住地区の人種構成を統合することを表す。  "
          },
          {
            "line": 560,
            "text": "例: Housing policies in the 1970s tried to racially integrate the suburbs.  "
          },
          {
            "line": 561,
            "text": "訳: 1970年代の住宅政策は郊外の住宅地を人種的に統合しようとした。  "
          },
          {
            "line": 563,
            "text": "・〈the university〉 integrated  "
          },
          {
            "line": 564,
            "text": "用途: 施設や機関そのものを主語にして、人種統合されたことを述べる自動詞用法。  "
          },
          {
            "line": 565,
            "text": "例: The university integrated in 1962 after a federal court ruling.  "
          },
          {
            "line": 566,
            "text": "訳: その大学は連邦裁判所の判断を受けて1962年に人種統合された。  "
          },
          {
            "line": 568,
            "text": "・be integrated under 〈a desegregation order〉  "
          },
          {
            "line": 569,
            "text": "用途: 受動態で、命令に基づいて人種統合が行われたことを述べる。  "
          },
          {
            "line": 570,
            "text": "例: The district was integrated under a desegregation order that lasted thirty years.  "
          },
          {
            "line": 571,
            "text": "訳: その学区は30年続いた人種分離撤廃命令のもとで人種統合された。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 624,
            "text": "【コロケーション】"
          },
          {
            "line": 626,
            "text": "・an integrated 〈school〉  "
          },
          {
            "line": 627,
            "text": "用途: 人種統合された学校を指す、この語義の中心的な形。  "
          },
          {
            "line": 628,
            "text": "例: She was among the first students to attend an integrated school in the county.  "
          },
          {
            "line": 629,
            "text": "訳: 彼女はその郡で人種統合された学校に通った最初の生徒の一人だった。  "
          },
          {
            "line": 631,
            "text": "・an integrated 〈neighborhood〉  "
          },
          {
            "line": 632,
            "text": "用途: 人種による分離をやめ、複数の人種の住民がともに暮らす地区を指す。  "
          },
          {
            "line": 633,
            "text": "例: They deliberately chose an integrated neighborhood when they bought their house.  "
          },
          {
            "line": 634,
            "text": "訳: 彼らは家を買うとき、意識して人種統合された地区を選んだ。  "
          },
          {
            "line": 636,
            "text": "・racially integrated  "
          },
          {
            "line": 637,
            "text": "用途: racially を添えて、人種についての統合であることを明示する叙述用法。  "
          },
          {
            "line": 638,
            "text": "例: Only a small share of the city's public schools are racially integrated today.  "
          },
          {
            "line": 639,
            "text": "訳: 今日、その市の公立学校のうち人種統合されているのはごく一部にすぎない。  "
          },
          {
            "line": 641,
            "text": "・an integrated 〈lunch counter〉  "
          },
          {
            "line": 642,
            "text": "用途: 公民権運動期の施設について、人種を問わず利用できたことを述べる歴史的な言い方。  "
          },
          {
            "line": 643,
            "text": "例: The sit-ins of 1960 aimed to win integrated lunch counters across the South.  "
          },
          {
            "line": 644,
            "text": "訳: 1960年の座り込みは、南部全域で人種を問わず利用できる軽食カウンターを実現することを目指していた。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 697,
            "text": "【コロケーション】"
          },
          {
            "line": 699,
            "text": "・integrate 〈the function〉  "
          },
          {
            "line": 700,
            "text": "用途: 関数の積分を求める、この語義の基本形。  "
          },
          {
            "line": 701,
            "text": "例: To find the area under the curve, integrate the function between the two limits.  "
          },
          {
            "line": 702,
            "text": "訳: 曲線の下の面積を求めるには、その関数を二つの積分限界の間で積分する。  "
          },
          {
            "line": 704,
            "text": "・integrate 〈the expression〉 with respect to 〈x〉  "
          },
          {
            "line": 705,
            "text": "用途: 積分する変数を明示する定型。  "
          },
          {
            "line": 706,
            "text": "例: Integrate the expression with respect to x, treating y as a constant.  "
          },
          {
            "line": 707,
            "text": "訳: y を定数とみなして、その式を x について積分せよ。  "
          },
          {
            "line": 709,
            "text": "・integrate 〈the product〉 by parts  "
          },
          {
            "line": 710,
            "text": "用途: 部分積分という手法を指定する固定表現。  "
          },
          {
            "line": 711,
            "text": "例: You can integrate the product by parts to remove the logarithm.  "
          },
          {
            "line": 712,
            "text": "訳: その積は部分積分すれば対数を消すことができる。  "
          },
          {
            "line": 714,
            "text": "・integrate 〈the velocity〉 over 〈time〉  "
          },
          {
            "line": 715,
            "text": "用途: 物理量を積分して別の量を導くことを表す。  "
          },
          {
            "line": 716,
            "text": "例: Integrate the velocity over time to obtain the total displacement.  "
          },
          {
            "line": 717,
            "text": "訳: 速度を時間で積分すれば全変位が得られる。  "
          },
          {
            "line": 719,
            "text": "・integrate 〈the expression〉 numerically  "
          },
          {
            "line": 720,
            "text": "用途: 数値計算によって近似的に積分することを表す。  "
          },
          {
            "line": 721,
            "text": "例: The software integrates the expression numerically when no closed form exists.  "
          },
          {
            "line": 722,
            "text": "訳: 閉じた形の解が存在しない場合、そのソフトは式を数値的に積分する。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 93,
            "text": "【類義語】"
          },
          {
            "line": 95,
            "text": "・combine  "
          },
          {
            "line": 96,
            "text": "定義: 二つ以上のものを合わせて一つにする。  "
          },
          {
            "line": 97,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 98,
            "text": "違い: 合わせるという操作が中心で、合わせた後に一つの体系として機能するという含みは integrate ほど強くない。料理から抽象概念まで使える日常語である。  "
          },
          {
            "line": 99,
            "text": "例: She combined the two reports into a single document.  "
          },
          {
            "line": 100,
            "text": "訳: 彼女は二つの報告書を一つの文書にまとめた。  "
          },
          {
            "line": 102,
            "text": "・merge  "
          },
          {
            "line": 103,
            "text": "定義: 二つ以上のものを境目のない一つのものにする。  "
          },
          {
            "line": 104,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 105,
            "text": "違い: 元のものの区別がなくなる方向を強く含意する。integrate は各部分が識別できるまま連携する場合にも使えるが、merge は結果として一つの単位になる場合に使う。  "
          },
          {
            "line": 106,
            "text": "例: The company merged its two research divisions last spring.  "
          },
          {
            "line": 107,
            "text": "訳: その会社は昨春、二つの研究部門を合併させた。  "
          },
          {
            "line": 109,
            "text": "・incorporate  "
          },
          {
            "line": 110,
            "text": "定義: 既にある全体の中へ要素を取り入れて一部にする。  "
          },
          {
            "line": 111,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 112,
            "text": "違い: 取り入れる側と取り入れられる側の上下関係がはっきりし、要素を全体へ吸収する点に重点がある。integrate は対等な要素どうしを結び合わせる場合にも使える。  "
          },
          {
            "line": 113,
            "text": "例: The final draft incorporates the reviewers' comments.  "
          },
          {
            "line": 114,
            "text": "訳: 最終稿には査読者の意見が取り入れられている。  "
          },
          {
            "line": 116,
            "text": "・unify  "
          },
          {
            "line": 117,
            "text": "定義: 分かれていたものを一つにまとめ、統一の取れた状態にする。  "
          },
          {
            "line": 118,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 119,
            "text": "違い: 統一と一貫性という結果を強調し、国家、規格、理論など大きな対象に使うことが多い。機器や業務の連携には integrate のほうが自然である。  "
          },
          {
            "line": 120,
            "text": "例: The reform unified the country's three separate pension systems.  "
          },
          {
            "line": 121,
            "text": "訳: その改革は国内の三つの別々の年金制度を一本化した。  "
          },
          {
            "line": 123,
            "text": "・consolidate  "
          },
          {
            "line": 124,
            "text": "定義: 複数のものを一つにまとめて、より強く効率的な状態にする。  "
          },
          {
            "line": 125,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 126,
            "text": "違い: まとめることで無駄を省き強化するという目的と効果に重点があり、経営や財務の文脈に偏る。連携して働くようにするという含みは薄い。  "
          },
          {
            "line": 127,
            "text": "例: The group consolidated its five regional offices into two hubs.  "
          },
          {
            "line": 128,
            "text": "訳: そのグループは五つの地域拠点を二つの中核拠点にまとめた。  "
          },
          {
            "line": 130,
            "text": "・blend  "
          },
          {
            "line": 131,
            "text": "定義: 性質の異なるものを混ぜ合わせて調和した一つのものにする。  "
          },
          {
            "line": 132,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 133,
            "text": "違い: 混ざり合って区別がつかなくなることと、仕上がりの調和に重点があり、味、色、音、様式に使う。仕組みどうしを機能的に連携させるという意味では integrate を使うが、blended learning のように方式を組み合わせた複合語は作る。  "
          },
          {
            "line": 134,
            "text": "例: The design blends traditional materials with modern lines.  "
          },
          {
            "line": 135,
            "text": "訳: そのデザインは伝統的な素材と現代的な線を調和させている。  "
          },
          {
            "line": 137,
            "text": "【反意語】"
          },
          {
            "line": 139,
            "text": "・separate  "
          },
          {
            "line": 140,
            "text": "定義: 一つになっていたものを分けて別々にする。  "
          },
          {
            "line": 141,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 142,
            "text": "違い: 一つにするか別々にするかという操作の向きが正反対で、程度の差ではない。  "
          },
          {
            "line": 143,
            "text": "例: The company separated its consumer and enterprise divisions.  "
          },
          {
            "line": 144,
            "text": "訳: その会社は消費者向け部門と法人向け部門を分割した。  "
          },
          {
            "line": 146,
            "text": "・fragment  "
          },
          {
            "line": 147,
            "text": "定義: 全体をいくつもの小さな断片に分ける。  "
          },
          {
            "line": 148,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 149,
            "text": "違い: 一つの全体にするのと逆に、細かく分かれて全体性が失われる方向を表す。市場、業界、社会について使うことが多い。  "
          },
          {
            "line": 150,
            "text": "例: Streaming has fragmented the television audience.  "
          },
          {
            "line": 151,
            "text": "訳: 配信サービスはテレビの視聴者層を細分化した。  "
          },
          {
            "line": 153,
            "text": "・disintegrate  "
          },
          {
            "line": 154,
            "text": "定義: まとまりを失ってばらばらに崩れる。  "
          },
          {
            "line": 155,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 156,
            "text": "違い: 一体化とは逆の方向を表すが、意図的な分割ではなく、まとまりが失われて崩れるという結果に重点がある。  "
          },
          {
            "line": 157,
            "text": "例: Without funding, the network of clinics slowly disintegrated.  "
          },
          {
            "line": 158,
            "text": "訳: 資金がなく、その診療所網は次第に崩壊していった。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 204,
            "text": "【類義語】"
          },
          {
            "line": 206,
            "text": "・unified  "
          },
          {
            "line": 207,
            "text": "定義: 分かれていた部分が一つにまとめられ、統一が取れている。  "
          },
          {
            "line": 208,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 209,
            "text": "違い: 統一と一貫性という結果に重点があり、部分が連携して働くという含みは弱い。規格、指揮系統、理論に使う。  "
          },
          {
            "line": 210,
            "text": "例: The army now operates under a unified command.  "
          },
          {
            "line": 211,
            "text": "訳: その軍は現在、統一された指揮系統のもとで活動している。  "
          },
          {
            "line": 213,
            "text": "・combined  "
          },
          {
            "line": 214,
            "text": "定義: 二つ以上のものが合わさっている。  "
          },
          {
            "line": 215,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 216,
            "text": "違い: 合わさっているという事実だけを述べ、全体として機能するかどうかは述べない。合計を表す用法もある。  "
          },
          {
            "line": 217,
            "text": "例: The exhibition is the combined work of three photographers.  "
          },
          {
            "line": 218,
            "text": "訳: その展示は3人の写真家が力を合わせた作品である。  "
          },
          {
            "line": 220,
            "text": "・all-in-one  "
          },
          {
            "line": 221,
            "text": "定義: 複数の機能を一つの製品にまとめてある。  "
          },
          {
            "line": 222,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 223,
            "text": "違い: 製品の宣伝で使う口語的な複合語で、機能をまとめてあることに重点がある。制度や組織には使わない。  "
          },
          {
            "line": 224,
            "text": "例: The printer is an all-in-one device that also scans and copies.  "
          },
          {
            "line": 225,
            "text": "訳: そのプリンターは走査も複写もできる一体型の機器である。  "
          },
          {
            "line": 227,
            "text": "・seamless  "
          },
          {
            "line": 228,
            "text": "定義: 部分の切れ目が感じられないほど滑らかにつながっている。  "
          },
          {
            "line": 229,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 230,
            "text": "違い: 使う側から見て切れ目が意識されないことに重点があり、内部が実際に一体化しているかどうかは述べない。  "
          },
          {
            "line": 231,
            "text": "例: The app promises a seamless transfer between devices.  "
          },
          {
            "line": 232,
            "text": "訳: そのアプリは機器間の切れ目のない移行をうたっている。  "
          },
          {
            "line": 234,
            "text": "・coherent  "
          },
          {
            "line": 235,
            "text": "定義: 各部分が矛盾なく結び付いて筋が通っている。  "
          },
          {
            "line": 236,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 237,
            "text": "違い: 論理や方針の一貫性に重点があり、機器や組織が制度的に結合していることは表さない。  "
          },
          {
            "line": 238,
            "text": "例: The party still lacks a coherent economic policy.  "
          },
          {
            "line": 239,
            "text": "訳: その政党にはいまだに一貫した経済政策がない。  "
          },
          {
            "line": 241,
            "text": "【反意語】"
          },
          {
            "line": 243,
            "text": "・fragmented  "
          },
          {
            "line": 244,
            "text": "定義: 全体がばらばらの断片に分かれている。  "
          },
          {
            "line": 245,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 246,
            "text": "違い: 一つのまとまりとして働くのとは逆に、分かれて全体性を欠く状態を表す。  "
          },
          {
            "line": 247,
            "text": "例: The country's health system remains highly fragmented.  "
          },
          {
            "line": 248,
            "text": "訳: その国の医療制度は依然として非常に細分化されている。  "
          },
          {
            "line": 250,
            "text": "・disjointed  "
          },
          {
            "line": 251,
            "text": "定義: 部分どうしのつながりを欠いてばらばらである。  "
          },
          {
            "line": 252,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 253,
            "text": "違い: つながりの欠如を否定的に述べる語で、話、文章、動きに使う。  "
          },
          {
            "line": 254,
            "text": "例: His presentation was disjointed and hard to follow.  "
          },
          {
            "line": 255,
            "text": "訳: 彼の発表はまとまりがなく、ついていくのが難しかった。  "
          },
          {
            "line": 257,
            "text": "・standalone  "
          },
          {
            "line": 258,
            "text": "定義: 他と接続せずに単独で機能する。  "
          },
          {
            "line": 259,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 260,
            "text": "違い: 他と結び付いていない点で反対だが、欠陥ではなく単独で完結しているという中立的な評価を伴う。  "
          },
          {
            "line": 261,
            "text": "例: The software is sold as a standalone product as well as part of the suite.  "
          },
          {
            "line": 262,
            "text": "訳: そのソフトは製品群の一部としても単独製品としても販売されている。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 303,
            "text": "【類義語】"
          },
          {
            "line": 305,
            "text": "・interoperate  "
          },
          {
            "line": 306,
            "text": "定義: 系統の異なる機器やソフトが互いに情報をやり取りして動作する。  "
          },
          {
            "line": 307,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 308,
            "text": "違い: 技術規格の文脈に限られる専門語で、相互に動作できるという能力を述べる。一般の製品説明では integrate のほうがはるかに普通である。  "
          },
          {
            "line": 309,
            "text": "例: The two hospital systems can interoperate through a shared data standard.  "
          },
          {
            "line": 310,
            "text": "訳: その二つの病院システムは共通のデータ規格を通じて相互に動作できる。  "
          },
          {
            "line": 312,
            "text": "・sync  "
          },
          {
            "line": 313,
            "text": "定義: 二つの機器やサービスが情報をそろえて同じ状態になる。  "
          },
          {
            "line": 314,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 315,
            "text": "違い: 情報の内容をそろえる操作に限られ、機能全体が連携するという意味はない。口語的で sync with の形が多い。  "
          },
          {
            "line": 316,
            "text": "例: The fitness tracker syncs with your phone every few minutes.  "
          },
          {
            "line": 317,
            "text": "訳: その活動量計は数分ごとに携帯電話と同期する。  "
          },
          {
            "line": 319,
            "text": "・mesh  "
          },
          {
            "line": 320,
            "text": "定義: 二つ以上のものがかみ合ってうまく働く。  "
          },
          {
            "line": 321,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 322,
            "text": "違い: かみ合いのよさという比喩に重点があり、計画、意見、日程にも使う。機器の接続という技術的な意味は薄い。  "
          },
          {
            "line": 323,
            "text": "例: The two schedules mesh surprisingly well.  "
          },
          {
            "line": 324,
            "text": "訳: その二つの日程は驚くほどよくかみ合っている。  "
          },
          {
            "line": 326,
            "text": "・dovetail  "
          },
          {
            "line": 327,
            "text": "定義: 二つのものが無駄なくぴったり合わさって機能する。  "
          },
          {
            "line": 328,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 329,
            "text": "違い: ぴったり合うという形の比喩で、計画や日程の相性を述べることが多い。装置やソフトの接続には使いにくい。  "
          },
          {
            "line": 330,
            "text": "例: The two projects dovetail neatly, so the teams can share data.  "
          },
          {
            "line": 331,
            "text": "訳: その二つの計画はうまくかみ合うので、両チームはデータを共有できる。  "
          },
          {
            "line": 333,
            "text": "・merge  "
          },
          {
            "line": 334,
            "text": "定義: 別々のものが境目を失って一つになる。  "
          },
          {
            "line": 335,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 336,
            "text": "違い: 元の区別がなくなる方向を含意し、連携して働くという意味はない。道路、企業、ファイルについて使う。  "
          },
          {
            "line": 337,
            "text": "例: The two lanes merge just after the bridge.  "
          },
          {
            "line": 338,
            "text": "訳: その二車線は橋を過ぎたところで合流する。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 384,
            "text": "【類義語】"
          },
          {
            "line": 386,
            "text": "・assimilate  "
          },
          {
            "line": 387,
            "text": "定義: 少数派の集団に多数派の文化や習慣を取り入れさせ、区別がつかない状態にする。  "
          },
          {
            "line": 388,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 389,
            "text": "違い: 加わる側が元の特徴を失うことを含意しやすく、社会政策の議論では否定的に受け取られることがある。integrate は違いを保ったまま対等な構成員にするという含みで使える。  "
          },
          {
            "line": 390,
            "text": "例: The government was accused of trying to assimilate minority communities.  "
          },
          {
            "line": 391,
            "text": "訳: 政府は少数派の共同体を同化させようとしていると非難された。  "
          },
          {
            "line": 393,
            "text": "・include  "
          },
          {
            "line": 394,
            "text": "定義: 全体の一部として中に入れる、対象に数え入れる。  "
          },
          {
            "line": 395,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 396,
            "text": "違い: 対象として数え入れることが中心で、実際に関係が成り立つところまでは含意しない。教育政策では inclusion が integration と別の概念として使われる。  "
          },
          {
            "line": 397,
            "text": "例: The new policy includes part-time staff in the bonus scheme.  "
          },
          {
            "line": 398,
            "text": "訳: 新しい方針は非常勤職員を賞与制度の対象に含めている。  "
          },
          {
            "line": 400,
            "text": "・absorb  "
          },
          {
            "line": 401,
            "text": "定義: 大きな組織や集団が別の人や集団を取り込んで自分の一部にする。  "
          },
          {
            "line": 402,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 403,
            "text": "違い: 取り込む側の規模と主導性が強く、取り込まれた側の独自性は残らないという含みになる。対等な参加という含みはない。  "
          },
          {
            "line": 404,
            "text": "例: The larger union absorbed several smaller regional branches.  "
          },
          {
            "line": 405,
            "text": "訳: その大きな労働組合はいくつかの小さな地域支部を吸収した。  "
          },
          {
            "line": 407,
            "text": "・admit  "
          },
          {
            "line": 408,
            "text": "定義: 組織や施設への加入や入場を認める。  "
          },
          {
            "line": 409,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 410,
            "text": "違い: 加入の可否を認める手続きが中心で、加入後に関係が成り立つかどうかは述べない。  "
          },
          {
            "line": 411,
            "text": "例: The club finally admitted women as full members in 1998.  "
          },
          {
            "line": 412,
            "text": "訳: そのクラブは1998年にようやく女性を正会員として認めた。  "
          },
          {
            "line": 414,
            "text": "・mainstream  "
          },
          {
            "line": 415,
            "text": "定義: 特別な枠に置かれていた児童や利用者を通常の制度の中で扱う。  "
          },
          {
            "line": 416,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 417,
            "text": "違い: 教育や福祉の専門語で、通常の学級やサービスへ移すという制度上の措置を指す。社会全体への受け入れという広い意味はない。  "
          },
          {
            "line": 418,
            "text": "例: The school mainstreamed most of its special-education students.  "
          },
          {
            "line": 419,
            "text": "訳: その学校は特別支援教育の生徒の大半を通常学級へ移した。  "
          },
          {
            "line": 421,
            "text": "【反意語】"
          },
          {
            "line": 423,
            "text": "・segregate  "
          },
          {
            "line": 424,
            "text": "定義: 人種、性別、障害などを理由に人を別の場所や制度へ分けて置く。  "
          },
          {
            "line": 425,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 426,
            "text": "違い: 対等な構成員として受け入れるのとは逆に、意図的に分けて隔てる方向を表す。  "
          },
          {
            "line": 427,
            "text": "例: The old rules segregated students by ability from the age of eleven.  "
          },
          {
            "line": 428,
            "text": "訳: 古い規則は11歳から生徒を能力別に分けていた。  "
          },
          {
            "line": 430,
            "text": "・exclude  "
          },
          {
            "line": 431,
            "text": "定義: 対象から外して参加させない。  "
          },
          {
            "line": 432,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 433,
            "text": "違い: 受け入れの反対方向で、参加そのものを認めないことを表す。別に分けて置く segregate と違い、外に置く点に重点がある。  "
          },
          {
            "line": 434,
            "text": "例: The scheme excluded workers on short-term contracts.  "
          },
          {
            "line": 435,
            "text": "訳: その制度は短期契約の労働者を対象から外していた。  "
          },
          {
            "line": 437,
            "text": "・isolate  "
          },
          {
            "line": 438,
            "text": "定義: 人を周囲から切り離して孤立させる。  "
          },
          {
            "line": 439,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 440,
            "text": "違い: 集団の一員にするのと逆に、関係を断って一人にする方向を表す。制度上の分離ではなく関係の断絶に重点がある。  "
          },
          {
            "line": 441,
            "text": "例: Long night shifts isolated her from her colleagues.  "
          },
          {
            "line": 442,
            "text": "訳: 長く続く夜勤が彼女を同僚から孤立させた。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 483,
            "text": "【類義語】"
          },
          {
            "line": 485,
            "text": "・fit in  "
          },
          {
            "line": 486,
            "text": "定義: 周囲の人となじんで違和感なく過ごせるようになる。  "
          },
          {
            "line": 487,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 488,
            "text": "違い: 口語的で、周囲との相性や居心地に重点がある。制度や社会への参加という含みは薄い。  "
          },
          {
            "line": 489,
            "text": "例: It took him a while to fit in at his new school.  "
          },
          {
            "line": 490,
            "text": "訳: 彼は新しい学校になじむのに少し時間がかかった。  "
          },
          {
            "line": 492,
            "text": "・settle in  "
          },
          {
            "line": 493,
            "text": "定義: 新しい場所や仕事に慣れて落ち着く。  "
          },
          {
            "line": 494,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 495,
            "text": "違い: 環境に慣れることが中心で、集団の一員として受け入れられるかどうかは述べない。  "
          },
          {
            "line": 496,
            "text": "例: She soon settled in at her new office.  "
          },
          {
            "line": 497,
            "text": "訳: 彼女はすぐに新しい職場に慣れた。  "
          },
          {
            "line": 499,
            "text": "・assimilate  "
          },
          {
            "line": 500,
            "text": "定義: 少数派が多数派の文化や習慣を取り入れて区別がつかなくなる。  "
          },
          {
            "line": 501,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 502,
            "text": "違い: 元の文化的特徴を失う方向を含意する。integrate は違いを保ったまま参加するという含みで使える。  "
          },
          {
            "line": 503,
            "text": "例: Second-generation immigrants often assimilate more completely than their parents.  "
          },
          {
            "line": 504,
            "text": "訳: 移民の2世は親よりも完全に同化することが多い。  "
          },
          {
            "line": 506,
            "text": "・mix  "
          },
          {
            "line": 507,
            "text": "定義: 人と交わって付き合う。  "
          },
          {
            "line": 508,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 509,
            "text": "違い: 人と交際するという行為が中心で、集団の一員として定着することまでは含意しない。mix with の形で使う。  "
          },
          {
            "line": 510,
            "text": "例: He doesn't mix much with the other students.  "
          },
          {
            "line": 511,
            "text": "訳: 彼は他の学生とあまり交わらない。  "
          },
          {
            "line": 513,
            "text": "・blend in  "
          },
          {
            "line": 514,
            "text": "定義: 周囲と見分けがつかないほど目立たなくなる。  "
          },
          {
            "line": 515,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 516,
            "text": "違い: 目立たなくなることが中心で、関係を築いて参加することは含意しない。外見や振る舞いについて使う。  "
          },
          {
            "line": 517,
            "text": "例: He wore a suit so that he would blend in at the reception.  "
          },
          {
            "line": 518,
            "text": "訳: 彼は歓迎会で目立たないようにスーツを着た。  "
          },
          {
            "line": 520,
            "text": "【反意語】"
          },
          {
            "line": 522,
            "text": "・withdraw  "
          },
          {
            "line": 523,
            "text": "定義: 人との関わりを避けて集団から身を引く。  "
          },
          {
            "line": 524,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 525,
            "text": "違い: 一員になっていく方向とは逆に、関係から離れていく方向を表す。  "
          },
          {
            "line": 526,
            "text": "例: After the argument he withdrew from the group entirely.  "
          },
          {
            "line": 527,
            "text": "訳: 言い争いの後、彼は完全にそのグループから離れた。  "
          },
          {
            "line": 529,
            "text": "・keep to oneself  "
          },
          {
            "line": 530,
            "text": "定義: 他人と関わらずに一人で過ごす。  "
          },
          {
            "line": 531,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 532,
            "text": "違い: 集団に加わっていくのとは逆に、自分から関わりを持たない状態を表す。  "
          },
          {
            "line": 533,
            "text": "例: The new tenant keeps to himself and rarely speaks to the neighbors.  "
          },
          {
            "line": 534,
            "text": "訳: 新しい入居者は人と関わらず、近所の人ともめったに話さない。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 575,
            "text": "【類義語】"
          },
          {
            "line": 577,
            "text": "・desegregate  "
          },
          {
            "line": 578,
            "text": "定義: 法や規則による人種分離をやめさせる。  "
          },
          {
            "line": 579,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 580,
            "text": "違い: 分離を禁じるという制度上の措置に焦点があり、実際に複数の人種が同じ場にいる状態になったかどうかは述べない。  "
          },
          {
            "line": 581,
            "text": "例: The ruling required the city to desegregate its bus system.  "
          },
          {
            "line": 582,
            "text": "訳: その判決は市に対し、バス路線の人種分離をやめるよう求めた。  "
          },
          {
            "line": 584,
            "text": "・admit  "
          },
          {
            "line": 585,
            "text": "定義: これまで排除されていた人の入学や加入を認める。  "
          },
          {
            "line": 586,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 587,
            "text": "違い: 個々の加入を認める行為が中心で、制度全体の分離をやめるという意味はない。  "
          },
          {
            "line": 588,
            "text": "例: The college admitted its first Black students in 1955.  "
          },
          {
            "line": 589,
            "text": "訳: その大学は1955年に初めて黒人学生を受け入れた。  "
          },
          {
            "line": 591,
            "text": "・open  "
          },
          {
            "line": 592,
            "text": "定義: 一部の人にしか認められていなかった場や制度を、すべての人が利用できるようにする。  "
          },
          {
            "line": 593,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 594,
            "text": "違い: 利用資格を広げることが中心で、人種による分離の撤廃という限定はない。open A to B の形で使う。  "
          },
          {
            "line": 595,
            "text": "例: The 1964 law opened public accommodations to all citizens regardless of race.  "
          },
          {
            "line": 596,
            "text": "訳: 1964年の法律は、ホテルや飲食店など一般公衆に開かれた事業所を、人種にかかわらずすべての市民に開放した。  "
          },
          {
            "line": 598,
            "text": "【反意語】"
          },
          {
            "line": 600,
            "text": "・segregate  "
          },
          {
            "line": 601,
            "text": "定義: 人種などを理由に人を別の場所や制度へ分けて置く。  "
          },
          {
            "line": 602,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 603,
            "text": "違い: 人種統合とは正反対の方向で、同じ意味軸の上で分ける側を表す。  "
          },
          {
            "line": 604,
            "text": "例: State laws once segregated schools, buses, and parks.  "
          },
          {
            "line": 605,
            "text": "訳: 州法はかつて学校、バス、公園を人種別に分けていた。  "
          },
          {
            "line": 607,
            "text": "・resegregate  "
          },
          {
            "line": 608,
            "text": "定義: いったん人種統合された制度を再び人種別に分かれた状態にする。  "
          },
          {
            "line": 609,
            "text": "頻度: 〈2/10〉  "
          },
          {
            "line": 610,
            "text": "違い: 統合の後に元の分離状態へ戻る方向を表し、社会学や教育政策の議論で使う専門的な語である。  "
          },
          {
            "line": 611,
            "text": "例: Many districts quietly resegregated after the court orders ended.  "
          },
          {
            "line": 612,
            "text": "訳: 多くの学区は裁判所の命令が終わった後、静かに再び人種別に分かれていった。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 648,
            "text": "【類義語】"
          },
          {
            "line": 650,
            "text": "・desegregated  "
          },
          {
            "line": 651,
            "text": "定義: 法や規則による人種分離が撤廃された状態である。  "
          },
          {
            "line": 652,
            "text": "頻度: 〈2/10〉  "
          },
          {
            "line": 653,
            "text": "違い: 分離を禁じる措置が取られたことに焦点があり、実際に複数の人種が同じ場にいるかどうかは述べない。  "
          },
          {
            "line": 654,
            "text": "例: Legally desegregated schools can still be almost entirely single-race.  "
          },
          {
            "line": 655,
            "text": "訳: 法的に人種分離が撤廃された学校でも、実際にはほぼ単一の人種だけということがある。  "
          },
          {
            "line": 657,
            "text": "・mixed  "
          },
          {
            "line": 658,
            "text": "定義: 複数の種類の人が混ざっている。  "
          },
          {
            "line": 659,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 660,
            "text": "違い: 構成が混ざっているという事実を述べる一般語で、分離の撤廃という制度上の経緯は含意しない。  "
          },
          {
            "line": 661,
            "text": "例: The school serves a mixed community of long-term residents and new arrivals.  "
          },
          {
            "line": 662,
            "text": "訳: その学校は長年の住民と新しく来た人が混ざる地域に対応している。  "
          },
          {
            "line": 664,
            "text": "・multiracial  "
          },
          {
            "line": 665,
            "text": "定義: 複数の人種から成る。  "
          },
          {
            "line": 666,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 667,
            "text": "違い: 構成の事実を述べる語で、分離をやめた結果であるという含みはない。人にも集団にも使う。  "
          },
          {
            "line": 668,
            "text": "例: They grew up in a multiracial suburb outside Chicago.  "
          },
          {
            "line": 669,
            "text": "訳: 彼らはシカゴ郊外の多人種の住宅地で育った。  "
          },
          {
            "line": 671,
            "text": "【反意語】"
          },
          {
            "line": 673,
            "text": "・segregated  "
          },
          {
            "line": 674,
            "text": "定義: 人種などを理由に分けられている。  "
          },
          {
            "line": 675,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 676,
            "text": "違い: 人種統合された状態とは正反対で、同じ意味軸の上で分けられた側を表す。  "
          },
          {
            "line": 677,
            "text": "例: Photographs of segregated waiting rooms still appear in textbooks.  "
          },
          {
            "line": 678,
            "text": "訳: 人種別に分けられた待合室の写真は今でも教科書に載っている。  "
          },
          {
            "line": 680,
            "text": "・all-white  "
          },
          {
            "line": 681,
            "text": "定義: 構成員が白人だけである。  "
          },
          {
            "line": 682,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 683,
            "text": "違い: 統合された状態とは逆に、単一の人種だけで構成されていることを述べる。分離が制度によるものかどうかは述べない。  "
          },
          {
            "line": 684,
            "text": "例: The town's only high school remained all-white until 1965.  "
          },
          {
            "line": 685,
            "text": "訳: その町の唯一の高校は1965年まで白人だけの学校のままだった。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 726,
            "text": "【類義語】"
          },
          {
            "line": 728,
            "text": "・antidifferentiate  "
          },
          {
            "line": 729,
            "text": "定義: 微分の逆の操作として原始関数を求める。  "
          },
          {
            "line": 730,
            "text": "頻度: 〈1/10〉  "
          },
          {
            "line": 731,
            "text": "違い: 不定積分を求める操作だけを指す教育用の語で、定積分や数値積分には使わない。数学の文章でもまれである。  "
          },
          {
            "line": 732,
            "text": "例: Students learn to antidifferentiate simple polynomials before studying definite integrals.  "
          },
          {
            "line": 733,
            "text": "訳: 学生は定積分を学ぶ前に、簡単な多項式の原始関数を求めることを学ぶ。  "
          },
          {
            "line": 735,
            "text": "・evaluate the integral  "
          },
          {
            "line": 736,
            "text": "定義: 立てられた積分の値を計算して求める。  "
          },
          {
            "line": 737,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 738,
            "text": "違い: どちらも積分の計算を行うことを指すが、evaluate the integral は立式済みの積分の値を出す段階に限られる。integrate は関数から積分を作る操作そのものを含む。  "
          },
          {
            "line": 739,
            "text": "例: Evaluate the integral by substituting u for the exponent.  "
          },
          {
            "line": 740,
            "text": "訳: 指数部を u に置き換えて、その積分の値を求めよ。  "
          },
          {
            "line": 742,
            "text": "【反意語】"
          },
          {
            "line": 744,
            "text": "・differentiate  "
          },
          {
            "line": 745,
            "text": "定義: 微積分で、関数の導関数を求める。  "
          },
          {
            "line": 746,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 747,
            "text": "違い: 積分と微分は互いに逆の操作であり、同じ意味軸の上で正反対の方向を表す。  "
          },
          {
            "line": 748,
            "text": "例: Differentiate the position function to find the velocity.  "
          },
          {
            "line": 749,
            "text": "訳: 位置の関数を微分すれば速度が求まる。  "
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
      "input_body_sha256": "f81f71e168187dbc968e77848fc623c5b7a1a06b513de11c30f7548088338629",
      "input_sections": {
        "core_image": [
          {
            "line": 34,
            "text": "＃コアイメージ"
          },
          {
            "line": 36,
            "text": "現代英語の integrate は、別々に存在しているものを、隔たりや欠けのない一つの全体にすること、またそうなることを表す。対象が部品でも、社会の構成員でも、微小な量でも、「ばらばらのものを一つの全体にする」という同じ発想が働く。  "
          },
          {
            "line": 38,
            "text": "・別々の要素を一つの全体へまとめる働き → 「統合する、組み込む」（語義1）  "
          },
          {
            "line": 39,
            "text": "・要素が一つの全体へまとめられた状態 → 「統合された、一体型の」（語義2）  "
          },
          {
            "line": 40,
            "text": "・別々の要素が一つの全体へまとまる変化 → 「統合される、連携する」（語義3）  "
          },
          {
            "line": 41,
            "text": "・別々の人を集団という全体へ加える働き → 「溶け込ませる、一員にする」（語義4）  "
          },
          {
            "line": 42,
            "text": "・別々の人が集団という全体へ加わる変化 → 「溶け込む、一員になる」（語義5）  "
          },
          {
            "line": 43,
            "text": "・隔てられた集団を一つの全体へまとめる働きと変化 → 「人種統合する、人種隔離を撤廃する」（語義6）  "
          },
          {
            "line": 44,
            "text": "・隔てられた集団が一つの全体になった状態 → 「分離をやめて統合された」（語義7）  "
          },
          {
            "line": 45,
            "text": "・微小な部分を足し合わせて全体量を出す働き → 「積分する」（語義8）  "
          }
        ],
        "sense_structure": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 51,
            "text": "【日本語訳・定義】別々に存在していた要素、機能、部門、制度などを組み合わせ、一つのまとまりとして働くようにする。同じ場所に集める、同じ一覧に載せるということではなく、組み合わせた後に全体として機能することまでを含意する。目的語は部品や路線のような具体物でも、方針、データ、部門のような抽象物でもよい。統合の結果として元の要素が識別できなくなることまでは必要としない。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 162,
            "text": "【日本語訳・定義】過去分詞 integrated が形容詞として定着した用法で、多くの部分や機能が結び付き、一つのまとまりとして働くようになっていることを表す。限定用法と叙述用法の両方で使い、程度は fully、highly、closely、tightly などの副詞で示す。an integrated circuit（集積回路）、an integrated approach（統合的な取り組み）のように、専門的な複合表現も作る。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 266,
            "text": "【日本語訳・定義】別々のシステム、機器、サービス、路線などが結び付いて、一つのまとまりとして働くようになる。主語は人ではなく、装置、ソフトウェア、制度などの物や仕組みである。目的語は取らず、結び付く相手は with、まとまって入る先は into で示す。ソフトウェアの説明では「他の製品と連携して動く」という意味でよく使う。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 342,
            "text": "【日本語訳・定義】新しく加わった人や、これまで別扱いされてきた集団を、既存の共同体、組織、学級の対等な構成員として受け入れ、実際に活動へ加われるようにする。主語は受け入れる側の人、機関、制度で、目的語は加わる側の人や集団である。ただし再帰代名詞を目的語にとる integrate oneself into では、加わる側の人が主語と目的語を兼ねる。在籍させるだけでなく、周囲との関係が成り立つところまでを含意する。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 446,
            "text": "【日本語訳・定義】新しく入った人が、集団や社会の一員として周囲と関係を築き、実際に活動へ加わるようになる。主語は加わる側の人や集団で、目的語は取らない。入っていく先は into、打ち解ける相手は with で示し、副詞を伴って程度や成否を述べることが多い。本人の側から見た変化を述べる点で、受け入れる側を主語にする語義4と役割が逆になる。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 538,
            "text": "【日本語訳・定義】学校、軍、公共施設、居住地区などで、人種を主とし、辞書によっては性別や出身国も挙げる属性を理由に人を分けていた制度をやめ、分けられていた人々が同じ場所や組織に対等な構成員として属せるようにする。またそうなる。米国で公民権運動期の学校の人種統合をめぐって定着した用法で、現在も歴史的記述や社会・法律の議論で使う。目的語は制度・施設であり、制度上の分離の撤廃を述べる点で、個々の人や集団を目的語にして受け入れを述べる語義4と区別する。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 616,
            "text": "【日本語訳・定義】学校、地区、施設などが、人種、宗派、性別などを理由とする分離をやめ、これまで分けられていた人々が同じ場に属している状態であることを表す。語義6の動詞用法に対応する形容詞用法である。米国では人種についての用法が中心で、公民権運動以後の社会、教育、歴史の記述に定着している。北アイルランドではカトリックとプロテスタントの児童をともに教える学校を指す。名詞の前に置く限定用法が中心で、修飾する対象は制度、施設、地域や人の集団であり、個人ではない。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 689,
            "text": "【日本語訳・定義】微積分で、関数や式の積分を求める。微分の逆の操作で、微小な部分を足し合わせて面積、体積、総量などの全体量を得ることに当たる。目的語には積分の対象となる関数や式が来る。積分する変数は with respect to で示し、over は積分する変数や領域を導く。積分区間の上下限は from … to … で示す。  "
          }
        ],
        "usage_notes": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 91,
            "text": "【語法・注意】前置詞で含意が変わる。into は「既にある大きな全体の中へ入れる」、with は「対等なものどうしを結び合わせる」を表し、integrate the new office into the group（新拠点をグループの一部にする）と integrate the new office with the head office（新拠点と本社を結び付ける）は述べていることが違う。× integrate A to B は誤りで、○ integrate A into B または ○ integrate A with B とする。能動態の目的語の後ろでは into と with が中心である。include との違いにも注意する。The list includes three names.（一覧に載っている）は integrate では置き換えられない。integrate は組み込んだ後に全体として機能することまで述べる。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 202,
            "text": "【語法・注意】限定用法と叙述用法の両方で使える。叙述用法は無修飾でも普通で、程度を示すときは fully、closely、tightly などの副詞を使う。The system is very integrated. も皆無ではないが、程度を示す標準的な言い方としては選ばれにくい。動詞の受動態 The systems were integrated last year.（昨年統合された、語義1の行為）と、状態を述べる The systems are integrated.（統合されている、語義2）は形が近いので、時制と副詞で区別する。an integrated curriculum（教科どうしを結び付けた教育課程、語義2）と an integrated school（分離をやめて統合された学校、語義7）は同じ形でも中心意味が異なり、修飾される名詞と文脈で判断する。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 301,
            "text": "【語法・注意】この語義では目的語を取らない。The app integrates the calendar. は文としては正しいが、語義1の他動詞（カレンダーを組み込む）と読まれ、「連携する」という意味にはならない。連携する相手は with、まとまって入る先は into で示し、× integrate to とは言わない。他動詞の受動態 be integrated with と、この自動詞の integrate with は近い内容を表すが、受動態は統合した行為者の存在を前提にし、自動詞は仕組みどうしが働き合う状態そのものに焦点がある。主語が人の場合は語義5になる。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 382,
            "text": "【語法・注意】受け入れる側が主語、加わる側が目的語になる。加わる側を主語にして「溶け込む」と言うときは目的語を取らない語義5を使う。○ The manager integrated him into the team.（語義4）と ○ He integrated into the team.（語義5）は主語と目的語の役割が入れ替わる最小対立で、× He integrated in the team. とは言わない。integrate oneself into は自動詞の integrate into よりやや硬く、本人の意識的な努力を含意する。受動態は be integrated into が中心だが、Disabled students are integrated in regular classrooms. のように in を使う例も辞書に載る。assimilate との違いにも注意する。assimilate は加わる側が元の文化的特徴を失うことを含意しやすく、社会政策の議論では integrate と対比して使われる。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 481,
            "text": "【語法・注意】この語義では目的語を取らない。She integrated the team. は文としては正しいが、語義1の他動詞（チームを統合した）と読まれ、「チームに溶け込んだ」の意味にはならない。入っていく先は into が標準で、× integrate to とは言わない。in は語義4の受動態 be integrated in 〈場〉 に見られ、自動詞でも integrate in the labour market のような報告書的な用例があるが、into のほうが安全である。会話では fit in のほうがはるかに普通で、integrate は社会政策や職場の評価など、やや客観的に述べる文脈で使う。主語が装置や仕組みの場合は語義3になる。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 573,
            "text": "【語法・注意】典型的な目的語は学校、軍、地区などの制度や組織である。辞書は「分離をやめて対等な構成員として迎える」という定義も与えており、人を目的語にとる用法もあるが、その場合は語義4（一員として受け入れる）と重なる。人種分離の撤廃そのものを述べたいときは integrate the schools のように制度を目的語にすると意味がはっきりする。自動詞用法の The university integrated in 1962. の in は時を表す副詞句であり、語義5で扱った支配される前置詞ではない。語義1と語義3、語義4と語義5は、他動詞と自動詞で主語の役割が入れ替わるため別語義に分けているが、この語義では他動詞も自動詞も同じ制度を主語または目的語に取り、出来事が同じなので一つの語義にまとめている。desegregate との違いも重要である。desegregate は法や規則による分離をやめさせる制度上の措置に焦点があり、integrate は分けられていた人々が実際に同じ場に属する状態になることまでを含意する。このため公民権運動の議論では The schools were desegregated but never integrated. のように対比して使われる。この語義は主に米国の用法である。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 646,
            "text": "【語法・注意】この語義の integrated は制度、施設、地域や人の集団を修飾し、× an integrated student のように個人には使わない。個人について述べるときは語義5の自動詞を使い、○ a student who has integrated into the school とする。an integrated school（分離をやめて統合された学校、語義7）と an integrated curriculum（教科どうしを結び付けた教育課程、語義2）は形が同じでも中心意味が異なり、修飾される名詞と文脈で判断する。この語義が指す分離の種類は地域によって異なる。米国では人種を指し、北アイルランドでは宗派を指して、an integrated school はカトリックとプロテスタントの児童をともに教える学校になる。どちらの分離を指すかは文脈で決まるので、米国の記述をそのまま当てはめない。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 724,
            "text": "【語法・注意】数学の専門語で、一般義の「統合する」とは別に覚える。逆の操作は differentiate（微分する）、結果として得られる量は integral（積分）、操作全体は integration（積分法）である。integration は語義1から語義6までの名詞形と同じ形なので、分野と文脈で読み分ける。積分する変数は with respect to x のように示し、× integrate by x とは言わない。口頭の説明では integrate over the interval のように対象を言わずに済ませることもあるが、書き言葉では積分する関数や式を目的語として示すのが標準的である。  "
          }
        ],
        "word_formation": [
          {
            "line": 25,
            "text": "＃語形成"
          },
          {
            "line": 27,
            "text": "・integration：名詞。「統合、一体化、（米国の）人種統合、（数学の）積分」。動詞の各語義に対応し、economic integration、racial integration、numerical integration のように、修飾語と分野で指す内容が定まる。  "
          },
          {
            "line": 28,
            "text": "・integrated：過去分詞。動詞の完了形・受動態を作るほか、an integrated system のように形容詞として定着している（語義2・語義7）。  "
          },
          {
            "line": 29,
            "text": "・integrating：現在分詞・動名詞。integrating the two teams「両チームを統合すること、統合しながら」のように使う。  "
          },
          {
            "line": 30,
            "text": "・integrator：名詞。「統合するもの」。辞書は特に、数学の積分に相当する加算を行う装置・計算機部品を挙げる。system integrator／systems integrator（複数の製品を組み合わせて一つの仕組みに構築する事業者）という複合語でも使う。  "
          },
          {
            "line": 31,
            "text": "・integrative：形容詞。「統合的な」。integrative medicine「統合医療」のように、学術・専門的な複合語で使う。日常語ではない。  "
          },
          {
            "line": 32,
            "text": "・disintegrate：dis- を付けた動詞。「ばらばらに崩れる、崩壊する」。一般義の単純な否定ではなく、まとまりが失われて崩れるという結果に重点がある。  "
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
      "input_body_sha256": "f81f71e168187dbc968e77848fc623c5b7a1a06b513de11c30f7548088338629",
      "input_sections": {
        "antonym_items": [
          {
            "item_id": "ant-7fb31d874f5c",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】別々に存在していた要素、機能、部門、制度などを組み合わせ、一つのまとまりとして働くようにする。同じ場所に集める、同じ一覧に載せるということではなく、組み合わせた後に全体として機能することまでを含意する。目的語は部品や路線のような具体物でも、方針、データ、部門のような抽象物でもよい。統合の結果として元の要素が識別できなくなることまでは必要としない。",
            "antonym": "disintegrate",
            "antonym_definition": "定義: まとまりを失ってばらばらに崩れる。"
          },
          {
            "item_id": "ant-03319d94d559",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】過去分詞 integrated が形容詞として定着した用法で、多くの部分や機能が結び付き、一つのまとまりとして働くようになっていることを表す。限定用法と叙述用法の両方で使い、程度は fully、highly、closely、tightly などの副詞で示す。an integrated circuit（集積回路）、an integrated approach（統合的な取り組み）のように、専門的な複合表現も作る。",
            "antonym": "disjointed",
            "antonym_definition": "定義: 部分どうしのつながりを欠いてばらばらである。"
          },
          {
            "item_id": "ant-7ec45a9d3d9a",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】学校、地区、施設などが、人種、宗派、性別などを理由とする分離をやめ、これまで分けられていた人々が同じ場に属している状態であることを表す。語義6の動詞用法に対応する形容詞用法である。米国では人種についての用法が中心で、公民権運動以後の社会、教育、歴史の記述に定着している。北アイルランドではカトリックとプロテスタントの児童をともに教える学校を指す。名詞の前に置く限定用法が中心で、修飾する対象は制度、施設、地域や人の集団であり、個人ではない。",
            "antonym": "segregated",
            "antonym_definition": "定義: 人種などを理由に分けられている。"
          },
          {
            "item_id": "ant-b4ccc5771c69",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】新しく入った人が、集団や社会の一員として周囲と関係を築き、実際に活動へ加わるようになる。主語は加わる側の人や集団で、目的語は取らない。入っていく先は into、打ち解ける相手は with で示し、副詞を伴って程度や成否を述べることが多い。本人の側から見た変化を述べる点で、受け入れる側を主語にする語義4と役割が逆になる。",
            "antonym": "keep to oneself",
            "antonym_definition": "定義: 他人と関わらずに一人で過ごす。"
          },
          {
            "item_id": "ant-f9cf5d525a09",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】過去分詞 integrated が形容詞として定着した用法で、多くの部分や機能が結び付き、一つのまとまりとして働くようになっていることを表す。限定用法と叙述用法の両方で使い、程度は fully、highly、closely、tightly などの副詞で示す。an integrated circuit（集積回路）、an integrated approach（統合的な取り組み）のように、専門的な複合表現も作る。",
            "antonym": "fragmented",
            "antonym_definition": "定義: 全体がばらばらの断片に分かれている。"
          },
          {
            "item_id": "ant-d2ffd590cea3",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】新しく加わった人や、これまで別扱いされてきた集団を、既存の共同体、組織、学級の対等な構成員として受け入れ、実際に活動へ加われるようにする。主語は受け入れる側の人、機関、制度で、目的語は加わる側の人や集団である。ただし再帰代名詞を目的語にとる integrate oneself into では、加わる側の人が主語と目的語を兼ねる。在籍させるだけでなく、周囲との関係が成り立つところまでを含意する。",
            "antonym": "isolate",
            "antonym_definition": "定義: 人を周囲から切り離して孤立させる。"
          },
          {
            "item_id": "ant-a1f14e81fe41",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】別々に存在していた要素、機能、部門、制度などを組み合わせ、一つのまとまりとして働くようにする。同じ場所に集める、同じ一覧に載せるということではなく、組み合わせた後に全体として機能することまでを含意する。目的語は部品や路線のような具体物でも、方針、データ、部門のような抽象物でもよい。統合の結果として元の要素が識別できなくなることまでは必要としない。",
            "antonym": "fragment",
            "antonym_definition": "定義: 全体をいくつもの小さな断片に分ける。"
          },
          {
            "item_id": "ant-29bd1cd57814",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】別々に存在していた要素、機能、部門、制度などを組み合わせ、一つのまとまりとして働くようにする。同じ場所に集める、同じ一覧に載せるということではなく、組み合わせた後に全体として機能することまでを含意する。目的語は部品や路線のような具体物でも、方針、データ、部門のような抽象物でもよい。統合の結果として元の要素が識別できなくなることまでは必要としない。",
            "antonym": "separate",
            "antonym_definition": "定義: 一つになっていたものを分けて別々にする。"
          },
          {
            "item_id": "ant-b5e57e2e1316",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】学校、地区、施設などが、人種、宗派、性別などを理由とする分離をやめ、これまで分けられていた人々が同じ場に属している状態であることを表す。語義6の動詞用法に対応する形容詞用法である。米国では人種についての用法が中心で、公民権運動以後の社会、教育、歴史の記述に定着している。北アイルランドではカトリックとプロテスタントの児童をともに教える学校を指す。名詞の前に置く限定用法が中心で、修飾する対象は制度、施設、地域や人の集団であり、個人ではない。",
            "antonym": "all-white",
            "antonym_definition": "定義: 構成員が白人だけである。"
          },
          {
            "item_id": "ant-42197b362a77",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】学校、軍、公共施設、居住地区などで、人種を主とし、辞書によっては性別や出身国も挙げる属性を理由に人を分けていた制度をやめ、分けられていた人々が同じ場所や組織に対等な構成員として属せるようにする。またそうなる。米国で公民権運動期の学校の人種統合をめぐって定着した用法で、現在も歴史的記述や社会・法律の議論で使う。目的語は制度・施設であり、制度上の分離の撤廃を述べる点で、個々の人や集団を目的語にして受け入れを述べる語義4と区別する。",
            "antonym": "resegregate",
            "antonym_definition": "定義: いったん人種統合された制度を再び人種別に分かれた状態にする。"
          },
          {
            "item_id": "ant-260ca2a38daf",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】微積分で、関数や式の積分を求める。微分の逆の操作で、微小な部分を足し合わせて面積、体積、総量などの全体量を得ることに当たる。目的語には積分の対象となる関数や式が来る。積分する変数は with respect to で示し、over は積分する変数や領域を導く。積分区間の上下限は from … to … で示す。",
            "antonym": "differentiate",
            "antonym_definition": "定義: 微積分で、関数の導関数を求める。"
          },
          {
            "item_id": "ant-58da553a6d63",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】過去分詞 integrated が形容詞として定着した用法で、多くの部分や機能が結び付き、一つのまとまりとして働くようになっていることを表す。限定用法と叙述用法の両方で使い、程度は fully、highly、closely、tightly などの副詞で示す。an integrated circuit（集積回路）、an integrated approach（統合的な取り組み）のように、専門的な複合表現も作る。",
            "antonym": "standalone",
            "antonym_definition": "定義: 他と接続せずに単独で機能する。"
          },
          {
            "item_id": "ant-b6bffed1f411",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】新しく加わった人や、これまで別扱いされてきた集団を、既存の共同体、組織、学級の対等な構成員として受け入れ、実際に活動へ加われるようにする。主語は受け入れる側の人、機関、制度で、目的語は加わる側の人や集団である。ただし再帰代名詞を目的語にとる integrate oneself into では、加わる側の人が主語と目的語を兼ねる。在籍させるだけでなく、周囲との関係が成り立つところまでを含意する。",
            "antonym": "segregate",
            "antonym_definition": "定義: 人種、性別、障害などを理由に人を別の場所や制度へ分けて置く。"
          },
          {
            "item_id": "ant-4bc52afe6b1b",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】新しく加わった人や、これまで別扱いされてきた集団を、既存の共同体、組織、学級の対等な構成員として受け入れ、実際に活動へ加われるようにする。主語は受け入れる側の人、機関、制度で、目的語は加わる側の人や集団である。ただし再帰代名詞を目的語にとる integrate oneself into では、加わる側の人が主語と目的語を兼ねる。在籍させるだけでなく、周囲との関係が成り立つところまでを含意する。",
            "antonym": "exclude",
            "antonym_definition": "定義: 対象から外して参加させない。"
          },
          {
            "item_id": "ant-d14235cdf9ef",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】新しく入った人が、集団や社会の一員として周囲と関係を築き、実際に活動へ加わるようになる。主語は加わる側の人や集団で、目的語は取らない。入っていく先は into、打ち解ける相手は with で示し、副詞を伴って程度や成否を述べることが多い。本人の側から見た変化を述べる点で、受け入れる側を主語にする語義4と役割が逆になる。",
            "antonym": "withdraw",
            "antonym_definition": "定義: 人との関わりを避けて集団から身を引く。"
          },
          {
            "item_id": "ant-ea1fcb84a890",
            "headword": "integrate",
            "sense_definition": "【日本語訳・定義】学校、軍、公共施設、居住地区などで、人種を主とし、辞書によっては性別や出身国も挙げる属性を理由に人を分けていた制度をやめ、分けられていた人々が同じ場所や組織に対等な構成員として属せるようにする。またそうなる。米国で公民権運動期の学校の人種統合をめぐって定着した用法で、現在も歴史的記述や社会・法律の議論で使う。目的語は制度・施設であり、制度上の分離の撤廃を述べる点で、個々の人や集団を目的語にして受け入れを述べる語義4と区別する。",
            "antonym": "segregate",
            "antonym_definition": "定義: 人種などを理由に人を別の場所や制度へ分けて置く。"
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
      "input_body_sha256": "f81f71e168187dbc968e77848fc623c5b7a1a06b513de11c30f7548088338629",
      "input_sections": {
        "sense_structure": [
          {
            "sense_id": "sense:001",
            "line": 49,
            "label": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む",
            "definition": "別々に存在していた要素、機能、部門、制度などを組み合わせ、一つのまとまりとして働くようにする。同じ場所に集める、同じ一覧に載せるということではなく、組み合わせた後に全体として機能することまでを含意する。目的語は部品や路線のような具体物でも、方針、データ、部門のような抽象物でもよい。統合の結果として元の要素が識別できなくなることまでは必要としない。"
          },
          {
            "sense_id": "sense:002",
            "line": 160,
            "label": "2. 【分詞形容詞】統合された、一体型の",
            "definition": "過去分詞 integrated が形容詞として定着した用法で、多くの部分や機能が結び付き、一つのまとまりとして働くようになっていることを表す。限定用法と叙述用法の両方で使い、程度は fully、highly、closely、tightly などの副詞で示す。an integrated circuit（集積回路）、an integrated approach（統合的な取り組み）のように、専門的な複合表現も作る。"
          },
          {
            "sense_id": "sense:003",
            "line": 264,
            "label": "3. 【自動詞】（システム・要素が）統合される、連携する",
            "definition": "別々のシステム、機器、サービス、路線などが結び付いて、一つのまとまりとして働くようになる。主語は人ではなく、装置、ソフトウェア、制度などの物や仕組みである。目的語は取らず、結び付く相手は with、まとまって入る先は into で示す。ソフトウェアの説明では「他の製品と連携して動く」という意味でよく使う。"
          },
          {
            "sense_id": "sense:004",
            "line": 340,
            "label": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする",
            "definition": "新しく加わった人や、これまで別扱いされてきた集団を、既存の共同体、組織、学級の対等な構成員として受け入れ、実際に活動へ加われるようにする。主語は受け入れる側の人、機関、制度で、目的語は加わる側の人や集団である。ただし再帰代名詞を目的語にとる integrate oneself into では、加わる側の人が主語と目的語を兼ねる。在籍させるだけでなく、周囲との関係が成り立つところまでを含意する。"
          },
          {
            "sense_id": "sense:005",
            "line": 444,
            "label": "5. 【自動詞】（人が）溶け込む、一員になる",
            "definition": "新しく入った人が、集団や社会の一員として周囲と関係を築き、実際に活動へ加わるようになる。主語は加わる側の人や集団で、目的語は取らない。入っていく先は into、打ち解ける相手は with で示し、副詞を伴って程度や成否を述べることが多い。本人の側から見た変化を述べる点で、受け入れる側を主語にする語義4と役割が逆になる。"
          },
          {
            "sense_id": "sense:006",
            "line": 536,
            "label": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する",
            "definition": "学校、軍、公共施設、居住地区などで、人種を主とし、辞書によっては性別や出身国も挙げる属性を理由に人を分けていた制度をやめ、分けられていた人々が同じ場所や組織に対等な構成員として属せるようにする。またそうなる。米国で公民権運動期の学校の人種統合をめぐって定着した用法で、現在も歴史的記述や社会・法律の議論で使う。目的語は制度・施設であり、制度上の分離の撤廃を述べる点で、個々の人や集団を目的語にして受け入れを述べる語義4と区別する。"
          },
          {
            "sense_id": "sense:007",
            "line": 614,
            "label": "7. 【分詞形容詞・社会】分離をやめて統合された",
            "definition": "学校、地区、施設などが、人種、宗派、性別などを理由とする分離をやめ、これまで分けられていた人々が同じ場に属している状態であることを表す。語義6の動詞用法に対応する形容詞用法である。米国では人種についての用法が中心で、公民権運動以後の社会、教育、歴史の記述に定着している。北アイルランドではカトリックとプロテスタントの児童をともに教える学校を指す。名詞の前に置く限定用法が中心で、修飾する対象は制度、施設、地域や人の集団であり、個人ではない。"
          },
          {
            "sense_id": "sense:008",
            "line": 687,
            "label": "8. 【他動詞・数学】積分する",
            "definition": "微積分で、関数や式の積分を求める。微分の逆の操作で、微小な部分を足し合わせて面積、体積、総量などの全体量を得ることに当たる。目的語には積分の対象となる関数や式が来る。積分する変数は with respect to で示し、over は積分する変数や領域を導く。積分区間の上下限は from … to … で示す。"
          }
        ],
        "collocations_examples": [
          {
            "example_id": "ex-b4f1dfa2f1b1",
            "example": "Integrate the expression with respect to x, treating y as a constant.",
            "translation": "y を定数とみなして、その式を x について積分せよ。"
          },
          {
            "example_id": "ex-54d67989db1f",
            "example": "The new module does not integrate with the older version of the database.",
            "translation": "新しいモジュールは旧版のデータベースとは連携しない。"
          },
          {
            "example_id": "ex-200c5afe9936",
            "example": "Children usually integrate more quickly than their parents.",
            "translation": "子どもは普通、親よりも早く溶け込む。"
          },
          {
            "example_id": "ex-f059ea5b8646",
            "example": "A good mentor can integrate new employees into the team within weeks.",
            "translation": "優れた指導役がいれば、新入社員を数週間でチームの一員にできる。"
          },
          {
            "example_id": "ex-8629a4ed458e",
            "example": "A modern phone contains billions of transistors on a single integrated circuit.",
            "translation": "現代の携帯電話は一つの集積回路の上に何十億個ものトランジスタを載せている。"
          },
          {
            "example_id": "ex-502fd239fa6b",
            "example": "The company integrated its logistics network with a regional courier service.",
            "translation": "その会社は自社の物流網を地域の宅配業者と統合した。"
          },
          {
            "example_id": "ex-d496ddaabba2",
            "example": "It took two years to fully integrate the two departments after the merger.",
            "translation": "合併後、二つの部門を完全に統合するのに2年かかった。"
          },
          {
            "example_id": "ex-17d7dfe91256",
            "example": "Digital skills are now integrated into the primary school curriculum.",
            "translation": "デジタル技能は今では小学校の教育課程に組み込まれている。"
          },
          {
            "example_id": "ex-56fe06325457",
            "example": "She was among the first students to attend an integrated school in the county.",
            "translation": "彼女はその郡で人種統合された学校に通った最初の生徒の一人だった。"
          },
          {
            "example_id": "ex-fc8b49beeaf9",
            "example": "The district was integrated under a desegregation order that lasted thirty years.",
            "translation": "その学区は30年続いた人種分離撤廃命令のもとで人種統合された。"
          },
          {
            "example_id": "ex-63f942cdb2b0",
            "example": "The regional rail and bus networks will integrate into a single ticketing system next year.",
            "translation": "地域の鉄道網とバス網は来年、一つの発券システムへまとまる。"
          },
          {
            "example_id": "ex-0820332eb61e",
            "example": "The scheduling app integrates with most email clients.",
            "translation": "そのスケジュール管理アプリはほとんどのメールソフトと連携する。"
          },
          {
            "example_id": "ex-1aacf260f79c",
            "example": "The group is a vertically integrated producer that grows, roasts, and sells its own coffee.",
            "translation": "そのグループは、自社でコーヒーを栽培し焙煎し販売する垂直統合型の生産者である。"
          },
          {
            "example_id": "ex-fe02f3dd19c9",
            "example": "The new sensors integrate seamlessly with the factory's existing control software.",
            "translation": "新しいセンサーは工場の既存の制御ソフトと滑らかに連携する。"
          },
          {
            "example_id": "ex-09485662fba9",
            "example": "The sit-ins of 1960 aimed to win integrated lunch counters across the South.",
            "translation": "1960年の座り込みは、南部全域で人種を問わず利用できる軽食カウンターを実現することを目指していた。"
          },
          {
            "example_id": "ex-f854790b6d1d",
            "example": "The two databases are now fully integrated.",
            "translation": "その二つのデータベースは今では完全に統合されている。"
          },
          {
            "example_id": "ex-a6362157d326",
            "example": "A federal court ordered the state to integrate its public schools.",
            "translation": "連邦裁判所は州に対し、公立学校の人種隔離を撤廃するよう命じた。"
          },
          {
            "example_id": "ex-08d0602f37d1",
            "example": "They deliberately chose an integrated neighborhood when they bought their house.",
            "translation": "彼らは家を買うとき、意識して人種統合された地区を選んだ。"
          },
          {
            "example_id": "ex-ec0d92023eac",
            "example": "She has integrated well with her new colleagues.",
            "translation": "彼女は新しい同僚たちとうまく打ち解けている。"
          },
          {
            "example_id": "ex-63afda7994f1",
            "example": "Housing policies in the 1970s tried to racially integrate the suburbs.",
            "translation": "1970年代の住宅政策は郊外の住宅地を人種的に統合しようとした。"
          },
          {
            "example_id": "ex-94fb74fac0d9",
            "example": "The new terminal is closely integrated with the rest of the airport's rail network.",
            "translation": "新しいターミナルは空港の鉄道網の残りの部分と緊密につながっている。"
          },
          {
            "example_id": "ex-541b4b78f4a2",
            "example": "The district has integrated most children with disabilities into mainstream classrooms.",
            "translation": "その学区は障害のある児童の大半を通常学級へ受け入れてきた。"
          },
          {
            "example_id": "ex-4bcc787af403",
            "example": "Older workers are not always well integrated into the digital workforce.",
            "translation": "高齢の労働者が、デジタル化した職場にいつもうまく受け入れられているとは限らない。"
          },
          {
            "example_id": "ex-c49a16450781",
            "example": "The city promised an integrated transport network with a single ticket for buses and trams.",
            "translation": "市はバスと路面電車を一枚の切符で使える統合交通網を約束した。"
          },
          {
            "example_id": "ex-9132e6c71bf8",
            "example": "The dashboard integrates data from multiple sources into a single view.",
            "translation": "そのダッシュボードは複数の出所のデータを一つの画面にまとめている。"
          },
          {
            "example_id": "ex-f42ea7bff66b",
            "example": "The course integrates theory and practice through weekly fieldwork.",
            "translation": "その講座は毎週の実地調査を通じて理論と実践を結び付けている。"
          },
          {
            "example_id": "ex-8609ed819103",
            "example": "Only a small share of the city's public schools are racially integrated today.",
            "translation": "今日、その市の公立学校のうち人種統合されているのはごく一部にすぎない。"
          },
          {
            "example_id": "ex-e6db02aa1420",
            "example": "You can integrate the product by parts to remove the logarithm.",
            "translation": "その積は部分積分すれば対数を消すことができる。"
          },
          {
            "example_id": "ex-912169f785eb",
            "example": "The program is designed to integrate recent immigrants into the local labor market.",
            "translation": "その事業は、最近来た移民を地域の労働市場へ受け入れることを目的としている。"
          },
          {
            "example_id": "ex-3d2ba82d0952",
            "example": "The university integrated in 1962 after a federal court ruling.",
            "translation": "その大学は連邦裁判所の判断を受けて1962年に人種統合された。"
          },
          {
            "example_id": "ex-3db88dcf2308",
            "example": "The hospital has adopted an integrated approach to chronic pain.",
            "translation": "その病院は慢性痛に対して統合的な取り組みを採用している。"
          },
          {
            "example_id": "ex-b89db709ea62",
            "example": "The camera and the editing software integrate well, so files transfer without conversion.",
            "translation": "そのカメラと編集ソフトはよく連携するので、ファイルは変換せずに移せる。"
          },
          {
            "example_id": "ex-5549b3f501a9",
            "example": "The team integrated two new payment methods into the existing checkout system.",
            "translation": "チームは二つの新しい支払い方法を、既存の購入手続きの仕組みに組み込んだ。"
          },
          {
            "example_id": "ex-bb1fd7a315f1",
            "example": "To find the area under the curve, integrate the function between the two limits.",
            "translation": "曲線の下の面積を求めるには、その関数を二つの積分限界の間で積分する。"
          },
          {
            "example_id": "ex-93171c3294ef",
            "example": "He found it hard to integrate after moving to a new city.",
            "translation": "彼は新しい街に移ってから溶け込むのに苦労した。"
          },
          {
            "example_id": "ex-ce31d0c78703",
            "example": "She quickly integrated herself into the research group.",
            "translation": "彼女はすぐに研究グループに入り込んでいった。"
          },
          {
            "example_id": "ex-1e1da94f601e",
            "example": "It takes years to fully integrate refugees into a new community.",
            "translation": "難民を新しい共同体に完全に受け入れるには何年もかかる。"
          },
          {
            "example_id": "ex-5bd19e65d39e",
            "example": "The report warned that some young arrivals fail to integrate socially.",
            "translation": "その報告書は、若い入国者の一部が社会的に溶け込めていないと警告した。"
          },
          {
            "example_id": "ex-65ec4ef41de0",
            "example": "Truman's 1948 executive order committed the government to integrating the armed forces.",
            "translation": "トルーマンの1948年の大統領令は、軍の人種隔離を撤廃することを政府の方針として定めた。"
          },
          {
            "example_id": "ex-046c9da55592",
            "example": "Many of the families integrated into the local community within a year.",
            "translation": "その家族の多くは1年以内に地域社会に溶け込んだ。"
          },
          {
            "example_id": "ex-11d2cb4e3716",
            "example": "Integrate the velocity over time to obtain the total displacement.",
            "translation": "速度を時間で積分すれば全変位が得られる。"
          },
          {
            "example_id": "ex-fc73592260f4",
            "example": "The software integrates the expression numerically when no closed form exists.",
            "translation": "閉じた形の解が存在しない場合、そのソフトは式を数値的に積分する。"
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
      "input_body_sha256": "f81f71e168187dbc968e77848fc623c5b7a1a06b513de11c30f7548088338629",
      "input_sections": {
        "etymology": [
          {
            "line": 20,
            "text": "＃語源"
          },
          {
            "line": 22,
            "text": "ラテン語 integer「欠けのない、そろっている」に由来する。integer は in-「〜でない」と tangere「触れる」の語根から成り、「手を触れられていない、損なわれていない」が原義とされる。この形容詞から作られた動詞 integrare「元どおりの全体にする、修復する」の過去分詞 integratus が英語に入り、まず1400年代半ばに「完全な」を表す形容詞として、次いで1600年代前半に動詞として記録された。語源の中心は「一つのものが欠けていない」という状態であり、現代の中心義「別々のものを組み合わせて一つの全体にする」は、そこから対象を複数へ移して働きかけの意味を加えたものである。「全体・完全」という核は共通するが、同じ意味がそのまま残っているわけではない。  "
          },
          {
            "line": 23,
            "text": "学習価値のある同語源語には、integer「整数」、integral「不可欠な、積分」、integrity「誠実さ、完全性」、disintegrate「崩壊する」がある。いずれもラテン語 integer の「欠けがない」という核を共有するが、英語では意味が離れており、互いに置き換えることはできない。  "
          }
        ],
        "word_formation": [
          {
            "line": 25,
            "text": "＃語形成"
          },
          {
            "line": 27,
            "text": "・integration：名詞。「統合、一体化、（米国の）人種統合、（数学の）積分」。動詞の各語義に対応し、economic integration、racial integration、numerical integration のように、修飾語と分野で指す内容が定まる。  "
          },
          {
            "line": 28,
            "text": "・integrated：過去分詞。動詞の完了形・受動態を作るほか、an integrated system のように形容詞として定着している（語義2・語義7）。  "
          },
          {
            "line": 29,
            "text": "・integrating：現在分詞・動名詞。integrating the two teams「両チームを統合すること、統合しながら」のように使う。  "
          },
          {
            "line": 30,
            "text": "・integrator：名詞。「統合するもの」。辞書は特に、数学の積分に相当する加算を行う装置・計算機部品を挙げる。system integrator／systems integrator（複数の製品を組み合わせて一つの仕組みに構築する事業者）という複合語でも使う。  "
          },
          {
            "line": 31,
            "text": "・integrative：形容詞。「統合的な」。integrative medicine「統合医療」のように、学術・専門的な複合語で使う。日常語ではない。  "
          },
          {
            "line": 32,
            "text": "・disintegrate：dis- を付けた動詞。「ばらばらに崩れる、崩壊する」。一般義の単純な否定ではなく、まとまりが失われて崩れるという結果に重点がある。  "
          }
        ],
        "sense_structure": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 51,
            "text": "【日本語訳・定義】別々に存在していた要素、機能、部門、制度などを組み合わせ、一つのまとまりとして働くようにする。同じ場所に集める、同じ一覧に載せるということではなく、組み合わせた後に全体として機能することまでを含意する。目的語は部品や路線のような具体物でも、方針、データ、部門のような抽象物でもよい。統合の結果として元の要素が識別できなくなることまでは必要としない。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 162,
            "text": "【日本語訳・定義】過去分詞 integrated が形容詞として定着した用法で、多くの部分や機能が結び付き、一つのまとまりとして働くようになっていることを表す。限定用法と叙述用法の両方で使い、程度は fully、highly、closely、tightly などの副詞で示す。an integrated circuit（集積回路）、an integrated approach（統合的な取り組み）のように、専門的な複合表現も作る。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 266,
            "text": "【日本語訳・定義】別々のシステム、機器、サービス、路線などが結び付いて、一つのまとまりとして働くようになる。主語は人ではなく、装置、ソフトウェア、制度などの物や仕組みである。目的語は取らず、結び付く相手は with、まとまって入る先は into で示す。ソフトウェアの説明では「他の製品と連携して動く」という意味でよく使う。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 342,
            "text": "【日本語訳・定義】新しく加わった人や、これまで別扱いされてきた集団を、既存の共同体、組織、学級の対等な構成員として受け入れ、実際に活動へ加われるようにする。主語は受け入れる側の人、機関、制度で、目的語は加わる側の人や集団である。ただし再帰代名詞を目的語にとる integrate oneself into では、加わる側の人が主語と目的語を兼ねる。在籍させるだけでなく、周囲との関係が成り立つところまでを含意する。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 446,
            "text": "【日本語訳・定義】新しく入った人が、集団や社会の一員として周囲と関係を築き、実際に活動へ加わるようになる。主語は加わる側の人や集団で、目的語は取らない。入っていく先は into、打ち解ける相手は with で示し、副詞を伴って程度や成否を述べることが多い。本人の側から見た変化を述べる点で、受け入れる側を主語にする語義4と役割が逆になる。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 538,
            "text": "【日本語訳・定義】学校、軍、公共施設、居住地区などで、人種を主とし、辞書によっては性別や出身国も挙げる属性を理由に人を分けていた制度をやめ、分けられていた人々が同じ場所や組織に対等な構成員として属せるようにする。またそうなる。米国で公民権運動期の学校の人種統合をめぐって定着した用法で、現在も歴史的記述や社会・法律の議論で使う。目的語は制度・施設であり、制度上の分離の撤廃を述べる点で、個々の人や集団を目的語にして受け入れを述べる語義4と区別する。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 616,
            "text": "【日本語訳・定義】学校、地区、施設などが、人種、宗派、性別などを理由とする分離をやめ、これまで分けられていた人々が同じ場に属している状態であることを表す。語義6の動詞用法に対応する形容詞用法である。米国では人種についての用法が中心で、公民権運動以後の社会、教育、歴史の記述に定着している。北アイルランドではカトリックとプロテスタントの児童をともに教える学校を指す。名詞の前に置く限定用法が中心で、修飾する対象は制度、施設、地域や人の集団であり、個人ではない。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 689,
            "text": "【日本語訳・定義】微積分で、関数や式の積分を求める。微分の逆の操作で、微小な部分を足し合わせて面積、体積、総量などの全体量を得ることに当たる。目的語には積分の対象となる関数や式が来る。積分する変数は with respect to で示し、over は積分する変数や領域を導く。積分区間の上下限は from … to … で示す。  "
          }
        ],
        "frequency_register": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 53,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 55,
            "text": "【レジスター/領域】標準的な語で、ビジネス、技術、行政、教育、学術の説明文に多い。日常会話では put together や combine のほうが普通である。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 164,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 166,
            "text": "【レジスター/領域】技術、経営、行政、医療の文章に多い。日常会話で使うことは少ないが、製品名や制度名の一部として目にする機会は多い。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 268,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 270,
            "text": "【レジスター/領域】技術、製品説明、ビジネスの文章に多く、ソフトウェアやサービスの機能紹介でよく見られる。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 344,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 346,
            "text": "【レジスター/領域】行政、教育、人事、社会政策の文章に多い。移民政策、障害のある児童の就学、新入社員の受け入れを述べる、ややフォーマルな語である。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 448,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 450,
            "text": "【レジスター/領域】社会、教育、職場について述べるややフォーマルな語で、報道や人事の文章に多い。日常会話では fit in が普通である。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 540,
            "text": "【頻度】〈4/10〉  "
          },
          {
            "line": 542,
            "text": "【レジスター/領域】主に米国。歴史、法律、社会学、報道の文脈で使う。日常会話で現在の話題として使うことは少ない。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 618,
            "text": "【頻度】〈3/10〉  "
          },
          {
            "line": 620,
            "text": "【レジスター/領域】社会制度について述べる語で、歴史、教育政策、社会学、報道の文脈で使うことが多い。米国では人種、北アイルランドでは宗派の分離が話題になる。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 691,
            "text": "【頻度】〈3/10〉  "
          },
          {
            "line": 693,
            "text": "【レジスター/領域】数学、物理、工学の専門語。微積分を扱う教科書、論文、授業のほか、数値計算を行うソフトウェアの説明など、専門を前提とする技術文書でも使う。一般の文脈では使わない。  "
          }
        ],
        "usage_notes": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 91,
            "text": "【語法・注意】前置詞で含意が変わる。into は「既にある大きな全体の中へ入れる」、with は「対等なものどうしを結び合わせる」を表し、integrate the new office into the group（新拠点をグループの一部にする）と integrate the new office with the head office（新拠点と本社を結び付ける）は述べていることが違う。× integrate A to B は誤りで、○ integrate A into B または ○ integrate A with B とする。能動態の目的語の後ろでは into と with が中心である。include との違いにも注意する。The list includes three names.（一覧に載っている）は integrate では置き換えられない。integrate は組み込んだ後に全体として機能することまで述べる。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 202,
            "text": "【語法・注意】限定用法と叙述用法の両方で使える。叙述用法は無修飾でも普通で、程度を示すときは fully、closely、tightly などの副詞を使う。The system is very integrated. も皆無ではないが、程度を示す標準的な言い方としては選ばれにくい。動詞の受動態 The systems were integrated last year.（昨年統合された、語義1の行為）と、状態を述べる The systems are integrated.（統合されている、語義2）は形が近いので、時制と副詞で区別する。an integrated curriculum（教科どうしを結び付けた教育課程、語義2）と an integrated school（分離をやめて統合された学校、語義7）は同じ形でも中心意味が異なり、修飾される名詞と文脈で判断する。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 301,
            "text": "【語法・注意】この語義では目的語を取らない。The app integrates the calendar. は文としては正しいが、語義1の他動詞（カレンダーを組み込む）と読まれ、「連携する」という意味にはならない。連携する相手は with、まとまって入る先は into で示し、× integrate to とは言わない。他動詞の受動態 be integrated with と、この自動詞の integrate with は近い内容を表すが、受動態は統合した行為者の存在を前提にし、自動詞は仕組みどうしが働き合う状態そのものに焦点がある。主語が人の場合は語義5になる。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 382,
            "text": "【語法・注意】受け入れる側が主語、加わる側が目的語になる。加わる側を主語にして「溶け込む」と言うときは目的語を取らない語義5を使う。○ The manager integrated him into the team.（語義4）と ○ He integrated into the team.（語義5）は主語と目的語の役割が入れ替わる最小対立で、× He integrated in the team. とは言わない。integrate oneself into は自動詞の integrate into よりやや硬く、本人の意識的な努力を含意する。受動態は be integrated into が中心だが、Disabled students are integrated in regular classrooms. のように in を使う例も辞書に載る。assimilate との違いにも注意する。assimilate は加わる側が元の文化的特徴を失うことを含意しやすく、社会政策の議論では integrate と対比して使われる。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 481,
            "text": "【語法・注意】この語義では目的語を取らない。She integrated the team. は文としては正しいが、語義1の他動詞（チームを統合した）と読まれ、「チームに溶け込んだ」の意味にはならない。入っていく先は into が標準で、× integrate to とは言わない。in は語義4の受動態 be integrated in 〈場〉 に見られ、自動詞でも integrate in the labour market のような報告書的な用例があるが、into のほうが安全である。会話では fit in のほうがはるかに普通で、integrate は社会政策や職場の評価など、やや客観的に述べる文脈で使う。主語が装置や仕組みの場合は語義3になる。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 573,
            "text": "【語法・注意】典型的な目的語は学校、軍、地区などの制度や組織である。辞書は「分離をやめて対等な構成員として迎える」という定義も与えており、人を目的語にとる用法もあるが、その場合は語義4（一員として受け入れる）と重なる。人種分離の撤廃そのものを述べたいときは integrate the schools のように制度を目的語にすると意味がはっきりする。自動詞用法の The university integrated in 1962. の in は時を表す副詞句であり、語義5で扱った支配される前置詞ではない。語義1と語義3、語義4と語義5は、他動詞と自動詞で主語の役割が入れ替わるため別語義に分けているが、この語義では他動詞も自動詞も同じ制度を主語または目的語に取り、出来事が同じなので一つの語義にまとめている。desegregate との違いも重要である。desegregate は法や規則による分離をやめさせる制度上の措置に焦点があり、integrate は分けられていた人々が実際に同じ場に属する状態になることまでを含意する。このため公民権運動の議論では The schools were desegregated but never integrated. のように対比して使われる。この語義は主に米国の用法である。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 646,
            "text": "【語法・注意】この語義の integrated は制度、施設、地域や人の集団を修飾し、× an integrated student のように個人には使わない。個人について述べるときは語義5の自動詞を使い、○ a student who has integrated into the school とする。an integrated school（分離をやめて統合された学校、語義7）と an integrated curriculum（教科どうしを結び付けた教育課程、語義2）は形が同じでも中心意味が異なり、修飾される名詞と文脈で判断する。この語義が指す分離の種類は地域によって異なる。米国では人種を指し、北アイルランドでは宗派を指して、an integrated school はカトリックとプロテスタントの児童をともに教える学校になる。どちらの分離を指すかは文脈で決まるので、米国の記述をそのまま当てはめない。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 724,
            "text": "【語法・注意】数学の専門語で、一般義の「統合する」とは別に覚える。逆の操作は differentiate（微分する）、結果として得られる量は integral（積分）、操作全体は integration（積分法）である。integration は語義1から語義6までの名詞形と同じ形なので、分野と文脈で読み分ける。積分する変数は with respect to x のように示し、× integrate by x とは言わない。口頭の説明では integrate over the interval のように対象を言わずに済ませることもあるが、書き言葉では積分する関数や式を目的語として示すのが標準的である。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 59,
            "text": "【コロケーション】"
          },
          {
            "line": 61,
            "text": "・integrate 〈new features〉 into 〈the existing platform〉  "
          },
          {
            "line": 62,
            "text": "用途: 新しい機能を既存の基盤へ組み込むことを表す、技術文脈の中心的な形。  "
          },
          {
            "line": 63,
            "text": "例: The team integrated two new payment methods into the existing checkout system.  "
          },
          {
            "line": 64,
            "text": "訳: チームは二つの新しい支払い方法を、既存の購入手続きの仕組みに組み込んだ。  "
          },
          {
            "line": 66,
            "text": "・integrate 〈the logistics network〉 with 〈a courier service〉  "
          },
          {
            "line": 67,
            "text": "用途: 対等な二つの仕組み・組織を結び付けて一体にする。  "
          },
          {
            "line": 68,
            "text": "例: The company integrated its logistics network with a regional courier service.  "
          },
          {
            "line": 69,
            "text": "訳: その会社は自社の物流網を地域の宅配業者と統合した。  "
          },
          {
            "line": 71,
            "text": "・fully integrate 〈the two departments〉  "
          },
          {
            "line": 72,
            "text": "用途: 統合の程度を副詞で示す。fully、closely、seamlessly、successfully がよく使われる。  "
          },
          {
            "line": 73,
            "text": "例: It took two years to fully integrate the two departments after the merger.  "
          },
          {
            "line": 74,
            "text": "訳: 合併後、二つの部門を完全に統合するのに2年かかった。  "
          },
          {
            "line": 76,
            "text": "・integrate 〈data〉 from 〈multiple sources〉  "
          },
          {
            "line": 77,
            "text": "用途: 出所の異なる情報を一つにまとめることを表す。  "
          },
          {
            "line": 78,
            "text": "例: The dashboard integrates data from multiple sources into a single view.  "
          },
          {
            "line": 79,
            "text": "訳: そのダッシュボードは複数の出所のデータを一つの画面にまとめている。  "
          },
          {
            "line": 81,
            "text": "・integrate 〈theory〉 and 〈practice〉  "
          },
          {
            "line": 82,
            "text": "用途: 二つの領域・観点を結び付けて一体として扱う、学術的な言い方。  "
          },
          {
            "line": 83,
            "text": "例: The course integrates theory and practice through weekly fieldwork.  "
          },
          {
            "line": 84,
            "text": "訳: その講座は毎週の実地調査を通じて理論と実践を結び付けている。  "
          },
          {
            "line": 86,
            "text": "・be integrated into 〈the curriculum〉  "
          },
          {
            "line": 87,
            "text": "用途: 受動態で、要素が制度・計画の一部として組み込まれている状態を表す。  "
          },
          {
            "line": 88,
            "text": "例: Digital skills are now integrated into the primary school curriculum.  "
          },
          {
            "line": 89,
            "text": "訳: デジタル技能は今では小学校の教育課程に組み込まれている。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 170,
            "text": "【コロケーション】"
          },
          {
            "line": 172,
            "text": "・an integrated 〈system/approach〉  "
          },
          {
            "line": 173,
            "text": "用途: 複数の要素が一体として働く仕組みややり方を表す、最も基本的な限定用法。  "
          },
          {
            "line": 174,
            "text": "例: The hospital has adopted an integrated approach to chronic pain.  "
          },
          {
            "line": 175,
            "text": "訳: その病院は慢性痛に対して統合的な取り組みを採用している。  "
          },
          {
            "line": 177,
            "text": "・an integrated circuit  "
          },
          {
            "line": 178,
            "text": "用途: 電子工学で、多数の素子を一つのチップにまとめた回路を指す固定した複合語。  "
          },
          {
            "line": 179,
            "text": "例: A modern phone contains billions of transistors on a single integrated circuit.  "
          },
          {
            "line": 180,
            "text": "訳: 現代の携帯電話は一つの集積回路の上に何十億個ものトランジスタを載せている。  "
          },
          {
            "line": 182,
            "text": "・fully integrated  "
          },
          {
            "line": 183,
            "text": "用途: 一体化の程度が完全であることを叙述用法で述べる。  "
          },
          {
            "line": 184,
            "text": "例: The two databases are now fully integrated.  "
          },
          {
            "line": 185,
            "text": "訳: その二つのデータベースは今では完全に統合されている。  "
          },
          {
            "line": 187,
            "text": "・a vertically integrated 〈company〉  "
          },
          {
            "line": 188,
            "text": "用途: 経営学で、原材料の調達から販売までを一社が一貫して担う体制を表す。  "
          },
          {
            "line": 189,
            "text": "例: The group is a vertically integrated producer that grows, roasts, and sells its own coffee.  "
          },
          {
            "line": 190,
            "text": "訳: そのグループは、自社でコーヒーを栽培し焙煎し販売する垂直統合型の生産者である。  "
          },
          {
            "line": 192,
            "text": "・closely integrated with 〈the rest of the network〉  "
          },
          {
            "line": 193,
            "text": "用途: 他の部分との結び付きの強さを叙述用法で述べる。  "
          },
          {
            "line": 194,
            "text": "例: The new terminal is closely integrated with the rest of the airport's rail network.  "
          },
          {
            "line": 195,
            "text": "訳: 新しいターミナルは空港の鉄道網の残りの部分と緊密につながっている。  "
          },
          {
            "line": 197,
            "text": "・an integrated 〈transport network〉  "
          },
          {
            "line": 198,
            "text": "用途: 交通や公共サービスで、複数の手段が一つの体系として使えることを表す。  "
          },
          {
            "line": 199,
            "text": "例: The city promised an integrated transport network with a single ticket for buses and trams.  "
          },
          {
            "line": 200,
            "text": "訳: 市はバスと路面電車を一枚の切符で使える統合交通網を約束した。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 274,
            "text": "【コロケーション】"
          },
          {
            "line": 276,
            "text": "・〈the app〉 integrates with 〈existing tools〉  "
          },
          {
            "line": 277,
            "text": "用途: ソフトウェアやサービスが他製品と連携することを表す、製品説明の定型。  "
          },
          {
            "line": 278,
            "text": "例: The scheduling app integrates with most email clients.  "
          },
          {
            "line": 279,
            "text": "訳: そのスケジュール管理アプリはほとんどのメールソフトと連携する。  "
          },
          {
            "line": 281,
            "text": "・integrate seamlessly with 〈the control software〉  "
          },
          {
            "line": 282,
            "text": "用途: 連携の滑らかさを副詞で強調する。seamlessly、smoothly、easily がよく使われる。  "
          },
          {
            "line": 283,
            "text": "例: The new sensors integrate seamlessly with the factory's existing control software.  "
          },
          {
            "line": 284,
            "text": "訳: 新しいセンサーは工場の既存の制御ソフトと滑らかに連携する。  "
          },
          {
            "line": 286,
            "text": "・〈the two networks〉 integrate into 〈a single system〉  "
          },
          {
            "line": 287,
            "text": "用途: 別々の仕組みが一つの体系へまとまることを表す。  "
          },
          {
            "line": 288,
            "text": "例: The regional rail and bus networks will integrate into a single ticketing system next year.  "
          },
          {
            "line": 289,
            "text": "訳: 地域の鉄道網とバス網は来年、一つの発券システムへまとまる。  "
          },
          {
            "line": 291,
            "text": "・〈the components〉 integrate well  "
          },
          {
            "line": 292,
            "text": "用途: 連携の良し悪しを副詞で評価する。  "
          },
          {
            "line": 293,
            "text": "例: The camera and the editing software integrate well, so files transfer without conversion.  "
          },
          {
            "line": 294,
            "text": "訳: そのカメラと編集ソフトはよく連携するので、ファイルは変換せずに移せる。  "
          },
          {
            "line": 296,
            "text": "・〈the module〉 does not integrate with 〈the older version〉  "
          },
          {
            "line": 297,
            "text": "用途: 連携できないことを否定形で述べる。  "
          },
          {
            "line": 298,
            "text": "例: The new module does not integrate with the older version of the database.  "
          },
          {
            "line": 299,
            "text": "訳: 新しいモジュールは旧版のデータベースとは連携しない。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 350,
            "text": "【コロケーション】"
          },
          {
            "line": 352,
            "text": "・integrate 〈immigrants〉 into 〈society〉  "
          },
          {
            "line": 353,
            "text": "用途: 行政や社会政策で、移民を社会の構成員として受け入れることを表す。  "
          },
          {
            "line": 354,
            "text": "例: The program is designed to integrate recent immigrants into the local labor market.  "
          },
          {
            "line": 355,
            "text": "訳: その事業は、最近来た移民を地域の労働市場へ受け入れることを目的としている。  "
          },
          {
            "line": 357,
            "text": "・integrate 〈children with disabilities〉 into 〈mainstream schools〉  "
          },
          {
            "line": 358,
            "text": "用途: 教育制度で、別枠にされてきた児童を通常の学級へ受け入れることを表す。  "
          },
          {
            "line": 359,
            "text": "例: The district has integrated most children with disabilities into mainstream classrooms.  "
          },
          {
            "line": 360,
            "text": "訳: その学区は障害のある児童の大半を通常学級へ受け入れてきた。  "
          },
          {
            "line": 362,
            "text": "・integrate 〈new employees〉 into 〈the team〉  "
          },
          {
            "line": 363,
            "text": "用途: 人事で、新しい社員を既存のチームの一員にすることを表す。  "
          },
          {
            "line": 364,
            "text": "例: A good mentor can integrate new employees into the team within weeks.  "
          },
          {
            "line": 365,
            "text": "訳: 優れた指導役がいれば、新入社員を数週間でチームの一員にできる。  "
          },
          {
            "line": 367,
            "text": "・integrate oneself into 〈a research group〉  "
          },
          {
            "line": 368,
            "text": "用途: 再帰代名詞を目的語にして、自分から集団に入っていくことを表す。  "
          },
          {
            "line": 369,
            "text": "例: She quickly integrated herself into the research group.  "
          },
          {
            "line": 370,
            "text": "訳: 彼女はすぐに研究グループに入り込んでいった。  "
          },
          {
            "line": 372,
            "text": "・fully integrate 〈refugees〉 into 〈the community〉  "
          },
          {
            "line": 373,
            "text": "用途: 受け入れの程度を副詞で示す。fully、successfully、properly が多い。  "
          },
          {
            "line": 374,
            "text": "例: It takes years to fully integrate refugees into a new community.  "
          },
          {
            "line": 375,
            "text": "訳: 難民を新しい共同体に完全に受け入れるには何年もかかる。  "
          },
          {
            "line": 377,
            "text": "・be integrated into 〈the workforce〉  "
          },
          {
            "line": 378,
            "text": "用途: 受動態で、集団が働く場に受け入れられている状態を表す。  "
          },
          {
            "line": 379,
            "text": "例: Older workers are not always well integrated into the digital workforce.  "
          },
          {
            "line": 380,
            "text": "訳: 高齢の労働者が、デジタル化した職場にいつもうまく受け入れられているとは限らない。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 454,
            "text": "【コロケーション】"
          },
          {
            "line": 456,
            "text": "・〈newcomers〉 integrate into 〈the local community〉  "
          },
          {
            "line": 457,
            "text": "用途: 移住者や転入者が地域の一員になっていくことを表す。  "
          },
          {
            "line": 458,
            "text": "例: Many of the families integrated into the local community within a year.  "
          },
          {
            "line": 459,
            "text": "訳: その家族の多くは1年以内に地域社会に溶け込んだ。  "
          },
          {
            "line": 461,
            "text": "・integrate quickly  "
          },
          {
            "line": 462,
            "text": "用途: 溶け込む速さを副詞で述べる。quickly、easily、slowly が多い。  "
          },
          {
            "line": 463,
            "text": "例: Children usually integrate more quickly than their parents.  "
          },
          {
            "line": 464,
            "text": "訳: 子どもは普通、親よりも早く溶け込む。  "
          },
          {
            "line": 466,
            "text": "・find it hard to integrate  "
          },
          {
            "line": 467,
            "text": "用途: 溶け込むことの難しさを述べる定型。  "
          },
          {
            "line": 468,
            "text": "例: He found it hard to integrate after moving to a new city.  "
          },
          {
            "line": 469,
            "text": "訳: 彼は新しい街に移ってから溶け込むのに苦労した。  "
          },
          {
            "line": 471,
            "text": "・integrate with 〈one's new colleagues〉  "
          },
          {
            "line": 472,
            "text": "用途: 職場で同僚と打ち解けることを表す。  "
          },
          {
            "line": 473,
            "text": "例: She has integrated well with her new colleagues.  "
          },
          {
            "line": 474,
            "text": "訳: 彼女は新しい同僚たちとうまく打ち解けている。  "
          },
          {
            "line": 476,
            "text": "・fail to integrate  "
          },
          {
            "line": 477,
            "text": "用途: 溶け込めないことを述べる、報道や報告書に多い形。  "
          },
          {
            "line": 478,
            "text": "例: The report warned that some young arrivals fail to integrate socially.  "
          },
          {
            "line": 479,
            "text": "訳: その報告書は、若い入国者の一部が社会的に溶け込めていないと警告した。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 546,
            "text": "【コロケーション】"
          },
          {
            "line": 548,
            "text": "・integrate 〈the public schools〉  "
          },
          {
            "line": 549,
            "text": "用途: 公立学校の人種隔離を撤廃することを表す、この語義の中心的な形。  "
          },
          {
            "line": 550,
            "text": "例: A federal court ordered the state to integrate its public schools.  "
          },
          {
            "line": 551,
            "text": "訳: 連邦裁判所は州に対し、公立学校の人種隔離を撤廃するよう命じた。  "
          },
          {
            "line": 553,
            "text": "・integrate 〈the armed forces〉  "
          },
          {
            "line": 554,
            "text": "用途: 軍隊の人種隔離撤廃について述べる、歴史的記述の定型。  "
          },
          {
            "line": 555,
            "text": "例: Truman's 1948 executive order committed the government to integrating the armed forces.  "
          },
          {
            "line": 556,
            "text": "訳: トルーマンの1948年の大統領令は、軍の人種隔離を撤廃することを政府の方針として定めた。  "
          },
          {
            "line": 558,
            "text": "・racially integrate 〈the suburbs〉  "
          },
          {
            "line": 559,
            "text": "用途: 居住地区の人種構成を統合することを表す。  "
          },
          {
            "line": 560,
            "text": "例: Housing policies in the 1970s tried to racially integrate the suburbs.  "
          },
          {
            "line": 561,
            "text": "訳: 1970年代の住宅政策は郊外の住宅地を人種的に統合しようとした。  "
          },
          {
            "line": 563,
            "text": "・〈the university〉 integrated  "
          },
          {
            "line": 564,
            "text": "用途: 施設や機関そのものを主語にして、人種統合されたことを述べる自動詞用法。  "
          },
          {
            "line": 565,
            "text": "例: The university integrated in 1962 after a federal court ruling.  "
          },
          {
            "line": 566,
            "text": "訳: その大学は連邦裁判所の判断を受けて1962年に人種統合された。  "
          },
          {
            "line": 568,
            "text": "・be integrated under 〈a desegregation order〉  "
          },
          {
            "line": 569,
            "text": "用途: 受動態で、命令に基づいて人種統合が行われたことを述べる。  "
          },
          {
            "line": 570,
            "text": "例: The district was integrated under a desegregation order that lasted thirty years.  "
          },
          {
            "line": 571,
            "text": "訳: その学区は30年続いた人種分離撤廃命令のもとで人種統合された。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 624,
            "text": "【コロケーション】"
          },
          {
            "line": 626,
            "text": "・an integrated 〈school〉  "
          },
          {
            "line": 627,
            "text": "用途: 人種統合された学校を指す、この語義の中心的な形。  "
          },
          {
            "line": 628,
            "text": "例: She was among the first students to attend an integrated school in the county.  "
          },
          {
            "line": 629,
            "text": "訳: 彼女はその郡で人種統合された学校に通った最初の生徒の一人だった。  "
          },
          {
            "line": 631,
            "text": "・an integrated 〈neighborhood〉  "
          },
          {
            "line": 632,
            "text": "用途: 人種による分離をやめ、複数の人種の住民がともに暮らす地区を指す。  "
          },
          {
            "line": 633,
            "text": "例: They deliberately chose an integrated neighborhood when they bought their house.  "
          },
          {
            "line": 634,
            "text": "訳: 彼らは家を買うとき、意識して人種統合された地区を選んだ。  "
          },
          {
            "line": 636,
            "text": "・racially integrated  "
          },
          {
            "line": 637,
            "text": "用途: racially を添えて、人種についての統合であることを明示する叙述用法。  "
          },
          {
            "line": 638,
            "text": "例: Only a small share of the city's public schools are racially integrated today.  "
          },
          {
            "line": 639,
            "text": "訳: 今日、その市の公立学校のうち人種統合されているのはごく一部にすぎない。  "
          },
          {
            "line": 641,
            "text": "・an integrated 〈lunch counter〉  "
          },
          {
            "line": 642,
            "text": "用途: 公民権運動期の施設について、人種を問わず利用できたことを述べる歴史的な言い方。  "
          },
          {
            "line": 643,
            "text": "例: The sit-ins of 1960 aimed to win integrated lunch counters across the South.  "
          },
          {
            "line": 644,
            "text": "訳: 1960年の座り込みは、南部全域で人種を問わず利用できる軽食カウンターを実現することを目指していた。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 697,
            "text": "【コロケーション】"
          },
          {
            "line": 699,
            "text": "・integrate 〈the function〉  "
          },
          {
            "line": 700,
            "text": "用途: 関数の積分を求める、この語義の基本形。  "
          },
          {
            "line": 701,
            "text": "例: To find the area under the curve, integrate the function between the two limits.  "
          },
          {
            "line": 702,
            "text": "訳: 曲線の下の面積を求めるには、その関数を二つの積分限界の間で積分する。  "
          },
          {
            "line": 704,
            "text": "・integrate 〈the expression〉 with respect to 〈x〉  "
          },
          {
            "line": 705,
            "text": "用途: 積分する変数を明示する定型。  "
          },
          {
            "line": 706,
            "text": "例: Integrate the expression with respect to x, treating y as a constant.  "
          },
          {
            "line": 707,
            "text": "訳: y を定数とみなして、その式を x について積分せよ。  "
          },
          {
            "line": 709,
            "text": "・integrate 〈the product〉 by parts  "
          },
          {
            "line": 710,
            "text": "用途: 部分積分という手法を指定する固定表現。  "
          },
          {
            "line": 711,
            "text": "例: You can integrate the product by parts to remove the logarithm.  "
          },
          {
            "line": 712,
            "text": "訳: その積は部分積分すれば対数を消すことができる。  "
          },
          {
            "line": 714,
            "text": "・integrate 〈the velocity〉 over 〈time〉  "
          },
          {
            "line": 715,
            "text": "用途: 物理量を積分して別の量を導くことを表す。  "
          },
          {
            "line": 716,
            "text": "例: Integrate the velocity over time to obtain the total displacement.  "
          },
          {
            "line": 717,
            "text": "訳: 速度を時間で積分すれば全変位が得られる。  "
          },
          {
            "line": 719,
            "text": "・integrate 〈the expression〉 numerically  "
          },
          {
            "line": 720,
            "text": "用途: 数値計算によって近似的に積分することを表す。  "
          },
          {
            "line": 721,
            "text": "例: The software integrates the expression numerically when no closed form exists.  "
          },
          {
            "line": 722,
            "text": "訳: 閉じた形の解が存在しない場合、そのソフトは式を数値的に積分する。  "
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
      "input_body_sha256": "f81f71e168187dbc968e77848fc623c5b7a1a06b513de11c30f7548088338629",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "米: /ˈɪntəˌɡreɪt/｜英: /ˈɪntɪɡreɪt/。3音節の in-te-grate で、第1音節 /ˈɪn/ に主強勢がある。  "
          },
          {
            "line": 16,
            "text": "米英の記号の差は2か所である。第1に第2音節の母音で、米は /ə/、英は /ɪ/ と表記する。第2に第3音節で、米の記号には第二強勢 /ˌ/ があり、英の記号にはこれがない。第2音節の母音は米英どちらも弱化した短い母音で、辞書によって英音を /ə/ と表記することもある。第2の差も表記上の慣習によるところが大きく、第3音節の母音 /eɪ/ は米英とも十分な長さで発音される。  "
          },
          {
            "line": 17,
            "text": "過去形・過去分詞 integrated は、上の記号に規則的な -ed の /ɪd/ を加えた米 /ˈɪntəˌɡreɪtɪd/｜英 /ˈɪntɪɡreɪtɪd/ となり、4音節になる。辞書も integrated を4音節として扱う。母音の質と強勢の位置は動詞と変わらない。  "
          },
          {
            "line": 18,
            "text": "名詞 integration は英 /ˌɪntɪˈɡreɪʃən/ と記録され、主強勢が第3音節へ移って第1音節が第二強勢 /ˌ/ になる。米音では、動詞と同じく第2音節の母音が /ə/ になる。動詞と名詞で主強勢の位置が変わる点に注意する。  "
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
      "input_body_sha256": "f81f71e168187dbc968e77848fc623c5b7a1a06b513de11c30f7548088338629",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "米: /ˈɪntəˌɡreɪt/｜英: /ˈɪntɪɡreɪt/。3音節の in-te-grate で、第1音節 /ˈɪn/ に主強勢がある。  "
          },
          {
            "line": 16,
            "text": "米英の記号の差は2か所である。第1に第2音節の母音で、米は /ə/、英は /ɪ/ と表記する。第2に第3音節で、米の記号には第二強勢 /ˌ/ があり、英の記号にはこれがない。第2音節の母音は米英どちらも弱化した短い母音で、辞書によって英音を /ə/ と表記することもある。第2の差も表記上の慣習によるところが大きく、第3音節の母音 /eɪ/ は米英とも十分な長さで発音される。  "
          },
          {
            "line": 17,
            "text": "過去形・過去分詞 integrated は、上の記号に規則的な -ed の /ɪd/ を加えた米 /ˈɪntəˌɡreɪtɪd/｜英 /ˈɪntɪɡreɪtɪd/ となり、4音節になる。辞書も integrated を4音節として扱う。母音の質と強勢の位置は動詞と変わらない。  "
          },
          {
            "line": 18,
            "text": "名詞 integration は英 /ˌɪntɪˈɡreɪʃən/ と記録され、主強勢が第3音節へ移って第1音節が第二強勢 /ˌ/ になる。米音では、動詞と同じく第2音節の母音が /ə/ になる。動詞と名詞で主強勢の位置が変わる点に注意する。  "
          }
        ],
        "etymology": [
          {
            "line": 20,
            "text": "＃語源"
          },
          {
            "line": 22,
            "text": "ラテン語 integer「欠けのない、そろっている」に由来する。integer は in-「〜でない」と tangere「触れる」の語根から成り、「手を触れられていない、損なわれていない」が原義とされる。この形容詞から作られた動詞 integrare「元どおりの全体にする、修復する」の過去分詞 integratus が英語に入り、まず1400年代半ばに「完全な」を表す形容詞として、次いで1600年代前半に動詞として記録された。語源の中心は「一つのものが欠けていない」という状態であり、現代の中心義「別々のものを組み合わせて一つの全体にする」は、そこから対象を複数へ移して働きかけの意味を加えたものである。「全体・完全」という核は共通するが、同じ意味がそのまま残っているわけではない。  "
          },
          {
            "line": 23,
            "text": "学習価値のある同語源語には、integer「整数」、integral「不可欠な、積分」、integrity「誠実さ、完全性」、disintegrate「崩壊する」がある。いずれもラテン語 integer の「欠けがない」という核を共有するが、英語では意味が離れており、互いに置き換えることはできない。  "
          }
        ],
        "word_formation": [
          {
            "line": 25,
            "text": "＃語形成"
          },
          {
            "line": 27,
            "text": "・integration：名詞。「統合、一体化、（米国の）人種統合、（数学の）積分」。動詞の各語義に対応し、economic integration、racial integration、numerical integration のように、修飾語と分野で指す内容が定まる。  "
          },
          {
            "line": 28,
            "text": "・integrated：過去分詞。動詞の完了形・受動態を作るほか、an integrated system のように形容詞として定着している（語義2・語義7）。  "
          },
          {
            "line": 29,
            "text": "・integrating：現在分詞・動名詞。integrating the two teams「両チームを統合すること、統合しながら」のように使う。  "
          },
          {
            "line": 30,
            "text": "・integrator：名詞。「統合するもの」。辞書は特に、数学の積分に相当する加算を行う装置・計算機部品を挙げる。system integrator／systems integrator（複数の製品を組み合わせて一つの仕組みに構築する事業者）という複合語でも使う。  "
          },
          {
            "line": 31,
            "text": "・integrative：形容詞。「統合的な」。integrative medicine「統合医療」のように、学術・専門的な複合語で使う。日常語ではない。  "
          },
          {
            "line": 32,
            "text": "・disintegrate：dis- を付けた動詞。「ばらばらに崩れる、崩壊する」。一般義の単純な否定ではなく、まとまりが失われて崩れるという結果に重点がある。  "
          }
        ],
        "core_image": [
          {
            "line": 34,
            "text": "＃コアイメージ"
          },
          {
            "line": 36,
            "text": "現代英語の integrate は、別々に存在しているものを、隔たりや欠けのない一つの全体にすること、またそうなることを表す。対象が部品でも、社会の構成員でも、微小な量でも、「ばらばらのものを一つの全体にする」という同じ発想が働く。  "
          },
          {
            "line": 38,
            "text": "・別々の要素を一つの全体へまとめる働き → 「統合する、組み込む」（語義1）  "
          },
          {
            "line": 39,
            "text": "・要素が一つの全体へまとめられた状態 → 「統合された、一体型の」（語義2）  "
          },
          {
            "line": 40,
            "text": "・別々の要素が一つの全体へまとまる変化 → 「統合される、連携する」（語義3）  "
          },
          {
            "line": 41,
            "text": "・別々の人を集団という全体へ加える働き → 「溶け込ませる、一員にする」（語義4）  "
          },
          {
            "line": 42,
            "text": "・別々の人が集団という全体へ加わる変化 → 「溶け込む、一員になる」（語義5）  "
          },
          {
            "line": 43,
            "text": "・隔てられた集団を一つの全体へまとめる働きと変化 → 「人種統合する、人種隔離を撤廃する」（語義6）  "
          },
          {
            "line": 44,
            "text": "・隔てられた集団が一つの全体になった状態 → 「分離をやめて統合された」（語義7）  "
          },
          {
            "line": 45,
            "text": "・微小な部分を足し合わせて全体量を出す働き → 「積分する」（語義8）  "
          }
        ],
        "sense_structure": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 51,
            "text": "【日本語訳・定義】別々に存在していた要素、機能、部門、制度などを組み合わせ、一つのまとまりとして働くようにする。同じ場所に集める、同じ一覧に載せるということではなく、組み合わせた後に全体として機能することまでを含意する。目的語は部品や路線のような具体物でも、方針、データ、部門のような抽象物でもよい。統合の結果として元の要素が識別できなくなることまでは必要としない。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 162,
            "text": "【日本語訳・定義】過去分詞 integrated が形容詞として定着した用法で、多くの部分や機能が結び付き、一つのまとまりとして働くようになっていることを表す。限定用法と叙述用法の両方で使い、程度は fully、highly、closely、tightly などの副詞で示す。an integrated circuit（集積回路）、an integrated approach（統合的な取り組み）のように、専門的な複合表現も作る。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 266,
            "text": "【日本語訳・定義】別々のシステム、機器、サービス、路線などが結び付いて、一つのまとまりとして働くようになる。主語は人ではなく、装置、ソフトウェア、制度などの物や仕組みである。目的語は取らず、結び付く相手は with、まとまって入る先は into で示す。ソフトウェアの説明では「他の製品と連携して動く」という意味でよく使う。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 342,
            "text": "【日本語訳・定義】新しく加わった人や、これまで別扱いされてきた集団を、既存の共同体、組織、学級の対等な構成員として受け入れ、実際に活動へ加われるようにする。主語は受け入れる側の人、機関、制度で、目的語は加わる側の人や集団である。ただし再帰代名詞を目的語にとる integrate oneself into では、加わる側の人が主語と目的語を兼ねる。在籍させるだけでなく、周囲との関係が成り立つところまでを含意する。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 446,
            "text": "【日本語訳・定義】新しく入った人が、集団や社会の一員として周囲と関係を築き、実際に活動へ加わるようになる。主語は加わる側の人や集団で、目的語は取らない。入っていく先は into、打ち解ける相手は with で示し、副詞を伴って程度や成否を述べることが多い。本人の側から見た変化を述べる点で、受け入れる側を主語にする語義4と役割が逆になる。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 538,
            "text": "【日本語訳・定義】学校、軍、公共施設、居住地区などで、人種を主とし、辞書によっては性別や出身国も挙げる属性を理由に人を分けていた制度をやめ、分けられていた人々が同じ場所や組織に対等な構成員として属せるようにする。またそうなる。米国で公民権運動期の学校の人種統合をめぐって定着した用法で、現在も歴史的記述や社会・法律の議論で使う。目的語は制度・施設であり、制度上の分離の撤廃を述べる点で、個々の人や集団を目的語にして受け入れを述べる語義4と区別する。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 616,
            "text": "【日本語訳・定義】学校、地区、施設などが、人種、宗派、性別などを理由とする分離をやめ、これまで分けられていた人々が同じ場に属している状態であることを表す。語義6の動詞用法に対応する形容詞用法である。米国では人種についての用法が中心で、公民権運動以後の社会、教育、歴史の記述に定着している。北アイルランドではカトリックとプロテスタントの児童をともに教える学校を指す。名詞の前に置く限定用法が中心で、修飾する対象は制度、施設、地域や人の集団であり、個人ではない。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 689,
            "text": "【日本語訳・定義】微積分で、関数や式の積分を求める。微分の逆の操作で、微小な部分を足し合わせて面積、体積、総量などの全体量を得ることに当たる。目的語には積分の対象となる関数や式が来る。積分する変数は with respect to で示し、over は積分する変数や領域を導く。積分区間の上下限は from … to … で示す。  "
          }
        ],
        "frequency_register": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 53,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 55,
            "text": "【レジスター/領域】標準的な語で、ビジネス、技術、行政、教育、学術の説明文に多い。日常会話では put together や combine のほうが普通である。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 164,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 166,
            "text": "【レジスター/領域】技術、経営、行政、医療の文章に多い。日常会話で使うことは少ないが、製品名や制度名の一部として目にする機会は多い。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 268,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 270,
            "text": "【レジスター/領域】技術、製品説明、ビジネスの文章に多く、ソフトウェアやサービスの機能紹介でよく見られる。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 344,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 346,
            "text": "【レジスター/領域】行政、教育、人事、社会政策の文章に多い。移民政策、障害のある児童の就学、新入社員の受け入れを述べる、ややフォーマルな語である。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 448,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 450,
            "text": "【レジスター/領域】社会、教育、職場について述べるややフォーマルな語で、報道や人事の文章に多い。日常会話では fit in が普通である。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 540,
            "text": "【頻度】〈4/10〉  "
          },
          {
            "line": 542,
            "text": "【レジスター/領域】主に米国。歴史、法律、社会学、報道の文脈で使う。日常会話で現在の話題として使うことは少ない。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 618,
            "text": "【頻度】〈3/10〉  "
          },
          {
            "line": 620,
            "text": "【レジスター/領域】社会制度について述べる語で、歴史、教育政策、社会学、報道の文脈で使うことが多い。米国では人種、北アイルランドでは宗派の分離が話題になる。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 691,
            "text": "【頻度】〈3/10〉  "
          },
          {
            "line": 693,
            "text": "【レジスター/領域】数学、物理、工学の専門語。微積分を扱う教科書、論文、授業のほか、数値計算を行うソフトウェアの説明など、専門を前提とする技術文書でも使う。一般の文脈では使わない。  "
          }
        ],
        "frames": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 57,
            "text": "【文法パターン】integrate 〈要素〉＝要素を統合する／integrate 〈要素〉 into 〈全体〉＝要素を既存の全体の一部として組み込む／integrate 〈要素〉 with 〈対等の相手〉＝要素を対等の相手と結び合わせて一体にする／integrate 〈要素A〉 and 〈要素B〉＝二つの要素を組み合わせて一体にする／be integrated into 〈全体〉＝全体の一部として組み込まれている  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 168,
            "text": "【文法パターン】an integrated 〈system〉＝統合された仕組み（限定用法）／be fully integrated＝完全に一体化している（叙述用法）／be closely integrated with 〈another unit〉＝別の部門と緊密に結び付いている／a vertically integrated 〈company〉＝生産から販売までを一貫して行う会社  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 272,
            "text": "【文法パターン】〈an app〉 integrate with 〈another service〉＝アプリが別のサービスと連携して働く／〈two networks〉 integrate into 〈a single system〉＝二つの仕組みが一つの体系へまとまる  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 348,
            "text": "【文法パターン】integrate 〈newcomers〉 into 〈the community〉＝新しく来た人を共同体の一員にする／integrate 〈students〉 into 〈mainstream classes〉＝生徒を通常学級へ受け入れる／integrate oneself into 〈the team〉＝自分からチームに入っていく／be integrated into 〈the workforce〉＝働き手として受け入れられている  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 452,
            "text": "【文法パターン】〈newcomers〉 integrate into 〈the local community〉＝新しく来た人が地域の一員になる／〈a new member〉 integrate with 〈the rest of the team〉＝新しい一員が他の構成員と打ち解ける  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 544,
            "text": "【文法パターン】integrate 〈the public schools〉＝公立学校の人種隔離を撤廃する／〈the university〉 integrate＝大学が人種統合される／be integrated under 〈a court order〉＝裁判所の命令によって人種統合される  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 622,
            "text": "【文法パターン】an integrated 〈school〉＝人種統合された学校（限定用法）／be racially integrated＝人種的に統合されている（叙述用法）  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 695,
            "text": "【文法パターン】integrate 〈the function〉＝関数を積分する／integrate 〈the expression〉 with respect to 〈x〉＝式を x について積分する／integrate 〈the function〉 from 〈a〉 to 〈b〉＝関数を a から b まで積分する／integrate 〈the product〉 by parts＝積を部分積分する  "
          }
        ],
        "collocations_examples": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 59,
            "text": "【コロケーション】"
          },
          {
            "line": 61,
            "text": "・integrate 〈new features〉 into 〈the existing platform〉  "
          },
          {
            "line": 62,
            "text": "用途: 新しい機能を既存の基盤へ組み込むことを表す、技術文脈の中心的な形。  "
          },
          {
            "line": 63,
            "text": "例: The team integrated two new payment methods into the existing checkout system.  "
          },
          {
            "line": 64,
            "text": "訳: チームは二つの新しい支払い方法を、既存の購入手続きの仕組みに組み込んだ。  "
          },
          {
            "line": 66,
            "text": "・integrate 〈the logistics network〉 with 〈a courier service〉  "
          },
          {
            "line": 67,
            "text": "用途: 対等な二つの仕組み・組織を結び付けて一体にする。  "
          },
          {
            "line": 68,
            "text": "例: The company integrated its logistics network with a regional courier service.  "
          },
          {
            "line": 69,
            "text": "訳: その会社は自社の物流網を地域の宅配業者と統合した。  "
          },
          {
            "line": 71,
            "text": "・fully integrate 〈the two departments〉  "
          },
          {
            "line": 72,
            "text": "用途: 統合の程度を副詞で示す。fully、closely、seamlessly、successfully がよく使われる。  "
          },
          {
            "line": 73,
            "text": "例: It took two years to fully integrate the two departments after the merger.  "
          },
          {
            "line": 74,
            "text": "訳: 合併後、二つの部門を完全に統合するのに2年かかった。  "
          },
          {
            "line": 76,
            "text": "・integrate 〈data〉 from 〈multiple sources〉  "
          },
          {
            "line": 77,
            "text": "用途: 出所の異なる情報を一つにまとめることを表す。  "
          },
          {
            "line": 78,
            "text": "例: The dashboard integrates data from multiple sources into a single view.  "
          },
          {
            "line": 79,
            "text": "訳: そのダッシュボードは複数の出所のデータを一つの画面にまとめている。  "
          },
          {
            "line": 81,
            "text": "・integrate 〈theory〉 and 〈practice〉  "
          },
          {
            "line": 82,
            "text": "用途: 二つの領域・観点を結び付けて一体として扱う、学術的な言い方。  "
          },
          {
            "line": 83,
            "text": "例: The course integrates theory and practice through weekly fieldwork.  "
          },
          {
            "line": 84,
            "text": "訳: その講座は毎週の実地調査を通じて理論と実践を結び付けている。  "
          },
          {
            "line": 86,
            "text": "・be integrated into 〈the curriculum〉  "
          },
          {
            "line": 87,
            "text": "用途: 受動態で、要素が制度・計画の一部として組み込まれている状態を表す。  "
          },
          {
            "line": 88,
            "text": "例: Digital skills are now integrated into the primary school curriculum.  "
          },
          {
            "line": 89,
            "text": "訳: デジタル技能は今では小学校の教育課程に組み込まれている。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 170,
            "text": "【コロケーション】"
          },
          {
            "line": 172,
            "text": "・an integrated 〈system/approach〉  "
          },
          {
            "line": 173,
            "text": "用途: 複数の要素が一体として働く仕組みややり方を表す、最も基本的な限定用法。  "
          },
          {
            "line": 174,
            "text": "例: The hospital has adopted an integrated approach to chronic pain.  "
          },
          {
            "line": 175,
            "text": "訳: その病院は慢性痛に対して統合的な取り組みを採用している。  "
          },
          {
            "line": 177,
            "text": "・an integrated circuit  "
          },
          {
            "line": 178,
            "text": "用途: 電子工学で、多数の素子を一つのチップにまとめた回路を指す固定した複合語。  "
          },
          {
            "line": 179,
            "text": "例: A modern phone contains billions of transistors on a single integrated circuit.  "
          },
          {
            "line": 180,
            "text": "訳: 現代の携帯電話は一つの集積回路の上に何十億個ものトランジスタを載せている。  "
          },
          {
            "line": 182,
            "text": "・fully integrated  "
          },
          {
            "line": 183,
            "text": "用途: 一体化の程度が完全であることを叙述用法で述べる。  "
          },
          {
            "line": 184,
            "text": "例: The two databases are now fully integrated.  "
          },
          {
            "line": 185,
            "text": "訳: その二つのデータベースは今では完全に統合されている。  "
          },
          {
            "line": 187,
            "text": "・a vertically integrated 〈company〉  "
          },
          {
            "line": 188,
            "text": "用途: 経営学で、原材料の調達から販売までを一社が一貫して担う体制を表す。  "
          },
          {
            "line": 189,
            "text": "例: The group is a vertically integrated producer that grows, roasts, and sells its own coffee.  "
          },
          {
            "line": 190,
            "text": "訳: そのグループは、自社でコーヒーを栽培し焙煎し販売する垂直統合型の生産者である。  "
          },
          {
            "line": 192,
            "text": "・closely integrated with 〈the rest of the network〉  "
          },
          {
            "line": 193,
            "text": "用途: 他の部分との結び付きの強さを叙述用法で述べる。  "
          },
          {
            "line": 194,
            "text": "例: The new terminal is closely integrated with the rest of the airport's rail network.  "
          },
          {
            "line": 195,
            "text": "訳: 新しいターミナルは空港の鉄道網の残りの部分と緊密につながっている。  "
          },
          {
            "line": 197,
            "text": "・an integrated 〈transport network〉  "
          },
          {
            "line": 198,
            "text": "用途: 交通や公共サービスで、複数の手段が一つの体系として使えることを表す。  "
          },
          {
            "line": 199,
            "text": "例: The city promised an integrated transport network with a single ticket for buses and trams.  "
          },
          {
            "line": 200,
            "text": "訳: 市はバスと路面電車を一枚の切符で使える統合交通網を約束した。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 274,
            "text": "【コロケーション】"
          },
          {
            "line": 276,
            "text": "・〈the app〉 integrates with 〈existing tools〉  "
          },
          {
            "line": 277,
            "text": "用途: ソフトウェアやサービスが他製品と連携することを表す、製品説明の定型。  "
          },
          {
            "line": 278,
            "text": "例: The scheduling app integrates with most email clients.  "
          },
          {
            "line": 279,
            "text": "訳: そのスケジュール管理アプリはほとんどのメールソフトと連携する。  "
          },
          {
            "line": 281,
            "text": "・integrate seamlessly with 〈the control software〉  "
          },
          {
            "line": 282,
            "text": "用途: 連携の滑らかさを副詞で強調する。seamlessly、smoothly、easily がよく使われる。  "
          },
          {
            "line": 283,
            "text": "例: The new sensors integrate seamlessly with the factory's existing control software.  "
          },
          {
            "line": 284,
            "text": "訳: 新しいセンサーは工場の既存の制御ソフトと滑らかに連携する。  "
          },
          {
            "line": 286,
            "text": "・〈the two networks〉 integrate into 〈a single system〉  "
          },
          {
            "line": 287,
            "text": "用途: 別々の仕組みが一つの体系へまとまることを表す。  "
          },
          {
            "line": 288,
            "text": "例: The regional rail and bus networks will integrate into a single ticketing system next year.  "
          },
          {
            "line": 289,
            "text": "訳: 地域の鉄道網とバス網は来年、一つの発券システムへまとまる。  "
          },
          {
            "line": 291,
            "text": "・〈the components〉 integrate well  "
          },
          {
            "line": 292,
            "text": "用途: 連携の良し悪しを副詞で評価する。  "
          },
          {
            "line": 293,
            "text": "例: The camera and the editing software integrate well, so files transfer without conversion.  "
          },
          {
            "line": 294,
            "text": "訳: そのカメラと編集ソフトはよく連携するので、ファイルは変換せずに移せる。  "
          },
          {
            "line": 296,
            "text": "・〈the module〉 does not integrate with 〈the older version〉  "
          },
          {
            "line": 297,
            "text": "用途: 連携できないことを否定形で述べる。  "
          },
          {
            "line": 298,
            "text": "例: The new module does not integrate with the older version of the database.  "
          },
          {
            "line": 299,
            "text": "訳: 新しいモジュールは旧版のデータベースとは連携しない。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 350,
            "text": "【コロケーション】"
          },
          {
            "line": 352,
            "text": "・integrate 〈immigrants〉 into 〈society〉  "
          },
          {
            "line": 353,
            "text": "用途: 行政や社会政策で、移民を社会の構成員として受け入れることを表す。  "
          },
          {
            "line": 354,
            "text": "例: The program is designed to integrate recent immigrants into the local labor market.  "
          },
          {
            "line": 355,
            "text": "訳: その事業は、最近来た移民を地域の労働市場へ受け入れることを目的としている。  "
          },
          {
            "line": 357,
            "text": "・integrate 〈children with disabilities〉 into 〈mainstream schools〉  "
          },
          {
            "line": 358,
            "text": "用途: 教育制度で、別枠にされてきた児童を通常の学級へ受け入れることを表す。  "
          },
          {
            "line": 359,
            "text": "例: The district has integrated most children with disabilities into mainstream classrooms.  "
          },
          {
            "line": 360,
            "text": "訳: その学区は障害のある児童の大半を通常学級へ受け入れてきた。  "
          },
          {
            "line": 362,
            "text": "・integrate 〈new employees〉 into 〈the team〉  "
          },
          {
            "line": 363,
            "text": "用途: 人事で、新しい社員を既存のチームの一員にすることを表す。  "
          },
          {
            "line": 364,
            "text": "例: A good mentor can integrate new employees into the team within weeks.  "
          },
          {
            "line": 365,
            "text": "訳: 優れた指導役がいれば、新入社員を数週間でチームの一員にできる。  "
          },
          {
            "line": 367,
            "text": "・integrate oneself into 〈a research group〉  "
          },
          {
            "line": 368,
            "text": "用途: 再帰代名詞を目的語にして、自分から集団に入っていくことを表す。  "
          },
          {
            "line": 369,
            "text": "例: She quickly integrated herself into the research group.  "
          },
          {
            "line": 370,
            "text": "訳: 彼女はすぐに研究グループに入り込んでいった。  "
          },
          {
            "line": 372,
            "text": "・fully integrate 〈refugees〉 into 〈the community〉  "
          },
          {
            "line": 373,
            "text": "用途: 受け入れの程度を副詞で示す。fully、successfully、properly が多い。  "
          },
          {
            "line": 374,
            "text": "例: It takes years to fully integrate refugees into a new community.  "
          },
          {
            "line": 375,
            "text": "訳: 難民を新しい共同体に完全に受け入れるには何年もかかる。  "
          },
          {
            "line": 377,
            "text": "・be integrated into 〈the workforce〉  "
          },
          {
            "line": 378,
            "text": "用途: 受動態で、集団が働く場に受け入れられている状態を表す。  "
          },
          {
            "line": 379,
            "text": "例: Older workers are not always well integrated into the digital workforce.  "
          },
          {
            "line": 380,
            "text": "訳: 高齢の労働者が、デジタル化した職場にいつもうまく受け入れられているとは限らない。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 454,
            "text": "【コロケーション】"
          },
          {
            "line": 456,
            "text": "・〈newcomers〉 integrate into 〈the local community〉  "
          },
          {
            "line": 457,
            "text": "用途: 移住者や転入者が地域の一員になっていくことを表す。  "
          },
          {
            "line": 458,
            "text": "例: Many of the families integrated into the local community within a year.  "
          },
          {
            "line": 459,
            "text": "訳: その家族の多くは1年以内に地域社会に溶け込んだ。  "
          },
          {
            "line": 461,
            "text": "・integrate quickly  "
          },
          {
            "line": 462,
            "text": "用途: 溶け込む速さを副詞で述べる。quickly、easily、slowly が多い。  "
          },
          {
            "line": 463,
            "text": "例: Children usually integrate more quickly than their parents.  "
          },
          {
            "line": 464,
            "text": "訳: 子どもは普通、親よりも早く溶け込む。  "
          },
          {
            "line": 466,
            "text": "・find it hard to integrate  "
          },
          {
            "line": 467,
            "text": "用途: 溶け込むことの難しさを述べる定型。  "
          },
          {
            "line": 468,
            "text": "例: He found it hard to integrate after moving to a new city.  "
          },
          {
            "line": 469,
            "text": "訳: 彼は新しい街に移ってから溶け込むのに苦労した。  "
          },
          {
            "line": 471,
            "text": "・integrate with 〈one's new colleagues〉  "
          },
          {
            "line": 472,
            "text": "用途: 職場で同僚と打ち解けることを表す。  "
          },
          {
            "line": 473,
            "text": "例: She has integrated well with her new colleagues.  "
          },
          {
            "line": 474,
            "text": "訳: 彼女は新しい同僚たちとうまく打ち解けている。  "
          },
          {
            "line": 476,
            "text": "・fail to integrate  "
          },
          {
            "line": 477,
            "text": "用途: 溶け込めないことを述べる、報道や報告書に多い形。  "
          },
          {
            "line": 478,
            "text": "例: The report warned that some young arrivals fail to integrate socially.  "
          },
          {
            "line": 479,
            "text": "訳: その報告書は、若い入国者の一部が社会的に溶け込めていないと警告した。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 546,
            "text": "【コロケーション】"
          },
          {
            "line": 548,
            "text": "・integrate 〈the public schools〉  "
          },
          {
            "line": 549,
            "text": "用途: 公立学校の人種隔離を撤廃することを表す、この語義の中心的な形。  "
          },
          {
            "line": 550,
            "text": "例: A federal court ordered the state to integrate its public schools.  "
          },
          {
            "line": 551,
            "text": "訳: 連邦裁判所は州に対し、公立学校の人種隔離を撤廃するよう命じた。  "
          },
          {
            "line": 553,
            "text": "・integrate 〈the armed forces〉  "
          },
          {
            "line": 554,
            "text": "用途: 軍隊の人種隔離撤廃について述べる、歴史的記述の定型。  "
          },
          {
            "line": 555,
            "text": "例: Truman's 1948 executive order committed the government to integrating the armed forces.  "
          },
          {
            "line": 556,
            "text": "訳: トルーマンの1948年の大統領令は、軍の人種隔離を撤廃することを政府の方針として定めた。  "
          },
          {
            "line": 558,
            "text": "・racially integrate 〈the suburbs〉  "
          },
          {
            "line": 559,
            "text": "用途: 居住地区の人種構成を統合することを表す。  "
          },
          {
            "line": 560,
            "text": "例: Housing policies in the 1970s tried to racially integrate the suburbs.  "
          },
          {
            "line": 561,
            "text": "訳: 1970年代の住宅政策は郊外の住宅地を人種的に統合しようとした。  "
          },
          {
            "line": 563,
            "text": "・〈the university〉 integrated  "
          },
          {
            "line": 564,
            "text": "用途: 施設や機関そのものを主語にして、人種統合されたことを述べる自動詞用法。  "
          },
          {
            "line": 565,
            "text": "例: The university integrated in 1962 after a federal court ruling.  "
          },
          {
            "line": 566,
            "text": "訳: その大学は連邦裁判所の判断を受けて1962年に人種統合された。  "
          },
          {
            "line": 568,
            "text": "・be integrated under 〈a desegregation order〉  "
          },
          {
            "line": 569,
            "text": "用途: 受動態で、命令に基づいて人種統合が行われたことを述べる。  "
          },
          {
            "line": 570,
            "text": "例: The district was integrated under a desegregation order that lasted thirty years.  "
          },
          {
            "line": 571,
            "text": "訳: その学区は30年続いた人種分離撤廃命令のもとで人種統合された。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 624,
            "text": "【コロケーション】"
          },
          {
            "line": 626,
            "text": "・an integrated 〈school〉  "
          },
          {
            "line": 627,
            "text": "用途: 人種統合された学校を指す、この語義の中心的な形。  "
          },
          {
            "line": 628,
            "text": "例: She was among the first students to attend an integrated school in the county.  "
          },
          {
            "line": 629,
            "text": "訳: 彼女はその郡で人種統合された学校に通った最初の生徒の一人だった。  "
          },
          {
            "line": 631,
            "text": "・an integrated 〈neighborhood〉  "
          },
          {
            "line": 632,
            "text": "用途: 人種による分離をやめ、複数の人種の住民がともに暮らす地区を指す。  "
          },
          {
            "line": 633,
            "text": "例: They deliberately chose an integrated neighborhood when they bought their house.  "
          },
          {
            "line": 634,
            "text": "訳: 彼らは家を買うとき、意識して人種統合された地区を選んだ。  "
          },
          {
            "line": 636,
            "text": "・racially integrated  "
          },
          {
            "line": 637,
            "text": "用途: racially を添えて、人種についての統合であることを明示する叙述用法。  "
          },
          {
            "line": 638,
            "text": "例: Only a small share of the city's public schools are racially integrated today.  "
          },
          {
            "line": 639,
            "text": "訳: 今日、その市の公立学校のうち人種統合されているのはごく一部にすぎない。  "
          },
          {
            "line": 641,
            "text": "・an integrated 〈lunch counter〉  "
          },
          {
            "line": 642,
            "text": "用途: 公民権運動期の施設について、人種を問わず利用できたことを述べる歴史的な言い方。  "
          },
          {
            "line": 643,
            "text": "例: The sit-ins of 1960 aimed to win integrated lunch counters across the South.  "
          },
          {
            "line": 644,
            "text": "訳: 1960年の座り込みは、南部全域で人種を問わず利用できる軽食カウンターを実現することを目指していた。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 697,
            "text": "【コロケーション】"
          },
          {
            "line": 699,
            "text": "・integrate 〈the function〉  "
          },
          {
            "line": 700,
            "text": "用途: 関数の積分を求める、この語義の基本形。  "
          },
          {
            "line": 701,
            "text": "例: To find the area under the curve, integrate the function between the two limits.  "
          },
          {
            "line": 702,
            "text": "訳: 曲線の下の面積を求めるには、その関数を二つの積分限界の間で積分する。  "
          },
          {
            "line": 704,
            "text": "・integrate 〈the expression〉 with respect to 〈x〉  "
          },
          {
            "line": 705,
            "text": "用途: 積分する変数を明示する定型。  "
          },
          {
            "line": 706,
            "text": "例: Integrate the expression with respect to x, treating y as a constant.  "
          },
          {
            "line": 707,
            "text": "訳: y を定数とみなして、その式を x について積分せよ。  "
          },
          {
            "line": 709,
            "text": "・integrate 〈the product〉 by parts  "
          },
          {
            "line": 710,
            "text": "用途: 部分積分という手法を指定する固定表現。  "
          },
          {
            "line": 711,
            "text": "例: You can integrate the product by parts to remove the logarithm.  "
          },
          {
            "line": 712,
            "text": "訳: その積は部分積分すれば対数を消すことができる。  "
          },
          {
            "line": 714,
            "text": "・integrate 〈the velocity〉 over 〈time〉  "
          },
          {
            "line": 715,
            "text": "用途: 物理量を積分して別の量を導くことを表す。  "
          },
          {
            "line": 716,
            "text": "例: Integrate the velocity over time to obtain the total displacement.  "
          },
          {
            "line": 717,
            "text": "訳: 速度を時間で積分すれば全変位が得られる。  "
          },
          {
            "line": 719,
            "text": "・integrate 〈the expression〉 numerically  "
          },
          {
            "line": 720,
            "text": "用途: 数値計算によって近似的に積分することを表す。  "
          },
          {
            "line": 721,
            "text": "例: The software integrates the expression numerically when no closed form exists.  "
          },
          {
            "line": 722,
            "text": "訳: 閉じた形の解が存在しない場合、そのソフトは式を数値的に積分する。  "
          }
        ],
        "usage_notes": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 91,
            "text": "【語法・注意】前置詞で含意が変わる。into は「既にある大きな全体の中へ入れる」、with は「対等なものどうしを結び合わせる」を表し、integrate the new office into the group（新拠点をグループの一部にする）と integrate the new office with the head office（新拠点と本社を結び付ける）は述べていることが違う。× integrate A to B は誤りで、○ integrate A into B または ○ integrate A with B とする。能動態の目的語の後ろでは into と with が中心である。include との違いにも注意する。The list includes three names.（一覧に載っている）は integrate では置き換えられない。integrate は組み込んだ後に全体として機能することまで述べる。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 202,
            "text": "【語法・注意】限定用法と叙述用法の両方で使える。叙述用法は無修飾でも普通で、程度を示すときは fully、closely、tightly などの副詞を使う。The system is very integrated. も皆無ではないが、程度を示す標準的な言い方としては選ばれにくい。動詞の受動態 The systems were integrated last year.（昨年統合された、語義1の行為）と、状態を述べる The systems are integrated.（統合されている、語義2）は形が近いので、時制と副詞で区別する。an integrated curriculum（教科どうしを結び付けた教育課程、語義2）と an integrated school（分離をやめて統合された学校、語義7）は同じ形でも中心意味が異なり、修飾される名詞と文脈で判断する。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 301,
            "text": "【語法・注意】この語義では目的語を取らない。The app integrates the calendar. は文としては正しいが、語義1の他動詞（カレンダーを組み込む）と読まれ、「連携する」という意味にはならない。連携する相手は with、まとまって入る先は into で示し、× integrate to とは言わない。他動詞の受動態 be integrated with と、この自動詞の integrate with は近い内容を表すが、受動態は統合した行為者の存在を前提にし、自動詞は仕組みどうしが働き合う状態そのものに焦点がある。主語が人の場合は語義5になる。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 382,
            "text": "【語法・注意】受け入れる側が主語、加わる側が目的語になる。加わる側を主語にして「溶け込む」と言うときは目的語を取らない語義5を使う。○ The manager integrated him into the team.（語義4）と ○ He integrated into the team.（語義5）は主語と目的語の役割が入れ替わる最小対立で、× He integrated in the team. とは言わない。integrate oneself into は自動詞の integrate into よりやや硬く、本人の意識的な努力を含意する。受動態は be integrated into が中心だが、Disabled students are integrated in regular classrooms. のように in を使う例も辞書に載る。assimilate との違いにも注意する。assimilate は加わる側が元の文化的特徴を失うことを含意しやすく、社会政策の議論では integrate と対比して使われる。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 481,
            "text": "【語法・注意】この語義では目的語を取らない。She integrated the team. は文としては正しいが、語義1の他動詞（チームを統合した）と読まれ、「チームに溶け込んだ」の意味にはならない。入っていく先は into が標準で、× integrate to とは言わない。in は語義4の受動態 be integrated in 〈場〉 に見られ、自動詞でも integrate in the labour market のような報告書的な用例があるが、into のほうが安全である。会話では fit in のほうがはるかに普通で、integrate は社会政策や職場の評価など、やや客観的に述べる文脈で使う。主語が装置や仕組みの場合は語義3になる。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 573,
            "text": "【語法・注意】典型的な目的語は学校、軍、地区などの制度や組織である。辞書は「分離をやめて対等な構成員として迎える」という定義も与えており、人を目的語にとる用法もあるが、その場合は語義4（一員として受け入れる）と重なる。人種分離の撤廃そのものを述べたいときは integrate the schools のように制度を目的語にすると意味がはっきりする。自動詞用法の The university integrated in 1962. の in は時を表す副詞句であり、語義5で扱った支配される前置詞ではない。語義1と語義3、語義4と語義5は、他動詞と自動詞で主語の役割が入れ替わるため別語義に分けているが、この語義では他動詞も自動詞も同じ制度を主語または目的語に取り、出来事が同じなので一つの語義にまとめている。desegregate との違いも重要である。desegregate は法や規則による分離をやめさせる制度上の措置に焦点があり、integrate は分けられていた人々が実際に同じ場に属する状態になることまでを含意する。このため公民権運動の議論では The schools were desegregated but never integrated. のように対比して使われる。この語義は主に米国の用法である。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 646,
            "text": "【語法・注意】この語義の integrated は制度、施設、地域や人の集団を修飾し、× an integrated student のように個人には使わない。個人について述べるときは語義5の自動詞を使い、○ a student who has integrated into the school とする。an integrated school（分離をやめて統合された学校、語義7）と an integrated curriculum（教科どうしを結び付けた教育課程、語義2）は形が同じでも中心意味が異なり、修飾される名詞と文脈で判断する。この語義が指す分離の種類は地域によって異なる。米国では人種を指し、北アイルランドでは宗派を指して、an integrated school はカトリックとプロテスタントの児童をともに教える学校になる。どちらの分離を指すかは文脈で決まるので、米国の記述をそのまま当てはめない。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 724,
            "text": "【語法・注意】数学の専門語で、一般義の「統合する」とは別に覚える。逆の操作は differentiate（微分する）、結果として得られる量は integral（積分）、操作全体は integration（積分法）である。integration は語義1から語義6までの名詞形と同じ形なので、分野と文脈で読み分ける。積分する変数は with respect to x のように示し、× integrate by x とは言わない。口頭の説明では integrate over the interval のように対象を言わずに済ませることもあるが、書き言葉では積分する関数や式を目的語として示すのが標準的である。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 49,
            "text": "1. 【他動詞】（要素・機能・組織などを）統合する、組み込む"
          },
          {
            "line": 93,
            "text": "【類義語】"
          },
          {
            "line": 95,
            "text": "・combine  "
          },
          {
            "line": 96,
            "text": "定義: 二つ以上のものを合わせて一つにする。  "
          },
          {
            "line": 97,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 98,
            "text": "違い: 合わせるという操作が中心で、合わせた後に一つの体系として機能するという含みは integrate ほど強くない。料理から抽象概念まで使える日常語である。  "
          },
          {
            "line": 99,
            "text": "例: She combined the two reports into a single document.  "
          },
          {
            "line": 100,
            "text": "訳: 彼女は二つの報告書を一つの文書にまとめた。  "
          },
          {
            "line": 102,
            "text": "・merge  "
          },
          {
            "line": 103,
            "text": "定義: 二つ以上のものを境目のない一つのものにする。  "
          },
          {
            "line": 104,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 105,
            "text": "違い: 元のものの区別がなくなる方向を強く含意する。integrate は各部分が識別できるまま連携する場合にも使えるが、merge は結果として一つの単位になる場合に使う。  "
          },
          {
            "line": 106,
            "text": "例: The company merged its two research divisions last spring.  "
          },
          {
            "line": 107,
            "text": "訳: その会社は昨春、二つの研究部門を合併させた。  "
          },
          {
            "line": 109,
            "text": "・incorporate  "
          },
          {
            "line": 110,
            "text": "定義: 既にある全体の中へ要素を取り入れて一部にする。  "
          },
          {
            "line": 111,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 112,
            "text": "違い: 取り入れる側と取り入れられる側の上下関係がはっきりし、要素を全体へ吸収する点に重点がある。integrate は対等な要素どうしを結び合わせる場合にも使える。  "
          },
          {
            "line": 113,
            "text": "例: The final draft incorporates the reviewers' comments.  "
          },
          {
            "line": 114,
            "text": "訳: 最終稿には査読者の意見が取り入れられている。  "
          },
          {
            "line": 116,
            "text": "・unify  "
          },
          {
            "line": 117,
            "text": "定義: 分かれていたものを一つにまとめ、統一の取れた状態にする。  "
          },
          {
            "line": 118,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 119,
            "text": "違い: 統一と一貫性という結果を強調し、国家、規格、理論など大きな対象に使うことが多い。機器や業務の連携には integrate のほうが自然である。  "
          },
          {
            "line": 120,
            "text": "例: The reform unified the country's three separate pension systems.  "
          },
          {
            "line": 121,
            "text": "訳: その改革は国内の三つの別々の年金制度を一本化した。  "
          },
          {
            "line": 123,
            "text": "・consolidate  "
          },
          {
            "line": 124,
            "text": "定義: 複数のものを一つにまとめて、より強く効率的な状態にする。  "
          },
          {
            "line": 125,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 126,
            "text": "違い: まとめることで無駄を省き強化するという目的と効果に重点があり、経営や財務の文脈に偏る。連携して働くようにするという含みは薄い。  "
          },
          {
            "line": 127,
            "text": "例: The group consolidated its five regional offices into two hubs.  "
          },
          {
            "line": 128,
            "text": "訳: そのグループは五つの地域拠点を二つの中核拠点にまとめた。  "
          },
          {
            "line": 130,
            "text": "・blend  "
          },
          {
            "line": 131,
            "text": "定義: 性質の異なるものを混ぜ合わせて調和した一つのものにする。  "
          },
          {
            "line": 132,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 133,
            "text": "違い: 混ざり合って区別がつかなくなることと、仕上がりの調和に重点があり、味、色、音、様式に使う。仕組みどうしを機能的に連携させるという意味では integrate を使うが、blended learning のように方式を組み合わせた複合語は作る。  "
          },
          {
            "line": 134,
            "text": "例: The design blends traditional materials with modern lines.  "
          },
          {
            "line": 135,
            "text": "訳: そのデザインは伝統的な素材と現代的な線を調和させている。  "
          },
          {
            "line": 137,
            "text": "【反意語】"
          },
          {
            "line": 139,
            "text": "・separate  "
          },
          {
            "line": 140,
            "text": "定義: 一つになっていたものを分けて別々にする。  "
          },
          {
            "line": 141,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 142,
            "text": "違い: 一つにするか別々にするかという操作の向きが正反対で、程度の差ではない。  "
          },
          {
            "line": 143,
            "text": "例: The company separated its consumer and enterprise divisions.  "
          },
          {
            "line": 144,
            "text": "訳: その会社は消費者向け部門と法人向け部門を分割した。  "
          },
          {
            "line": 146,
            "text": "・fragment  "
          },
          {
            "line": 147,
            "text": "定義: 全体をいくつもの小さな断片に分ける。  "
          },
          {
            "line": 148,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 149,
            "text": "違い: 一つの全体にするのと逆に、細かく分かれて全体性が失われる方向を表す。市場、業界、社会について使うことが多い。  "
          },
          {
            "line": 150,
            "text": "例: Streaming has fragmented the television audience.  "
          },
          {
            "line": 151,
            "text": "訳: 配信サービスはテレビの視聴者層を細分化した。  "
          },
          {
            "line": 153,
            "text": "・disintegrate  "
          },
          {
            "line": 154,
            "text": "定義: まとまりを失ってばらばらに崩れる。  "
          },
          {
            "line": 155,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 156,
            "text": "違い: 一体化とは逆の方向を表すが、意図的な分割ではなく、まとまりが失われて崩れるという結果に重点がある。  "
          },
          {
            "line": 157,
            "text": "例: Without funding, the network of clinics slowly disintegrated.  "
          },
          {
            "line": 158,
            "text": "訳: 資金がなく、その診療所網は次第に崩壊していった。  "
          },
          {
            "line": 160,
            "text": "2. 【分詞形容詞】統合された、一体型の"
          },
          {
            "line": 204,
            "text": "【類義語】"
          },
          {
            "line": 206,
            "text": "・unified  "
          },
          {
            "line": 207,
            "text": "定義: 分かれていた部分が一つにまとめられ、統一が取れている。  "
          },
          {
            "line": 208,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 209,
            "text": "違い: 統一と一貫性という結果に重点があり、部分が連携して働くという含みは弱い。規格、指揮系統、理論に使う。  "
          },
          {
            "line": 210,
            "text": "例: The army now operates under a unified command.  "
          },
          {
            "line": 211,
            "text": "訳: その軍は現在、統一された指揮系統のもとで活動している。  "
          },
          {
            "line": 213,
            "text": "・combined  "
          },
          {
            "line": 214,
            "text": "定義: 二つ以上のものが合わさっている。  "
          },
          {
            "line": 215,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 216,
            "text": "違い: 合わさっているという事実だけを述べ、全体として機能するかどうかは述べない。合計を表す用法もある。  "
          },
          {
            "line": 217,
            "text": "例: The exhibition is the combined work of three photographers.  "
          },
          {
            "line": 218,
            "text": "訳: その展示は3人の写真家が力を合わせた作品である。  "
          },
          {
            "line": 220,
            "text": "・all-in-one  "
          },
          {
            "line": 221,
            "text": "定義: 複数の機能を一つの製品にまとめてある。  "
          },
          {
            "line": 222,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 223,
            "text": "違い: 製品の宣伝で使う口語的な複合語で、機能をまとめてあることに重点がある。制度や組織には使わない。  "
          },
          {
            "line": 224,
            "text": "例: The printer is an all-in-one device that also scans and copies.  "
          },
          {
            "line": 225,
            "text": "訳: そのプリンターは走査も複写もできる一体型の機器である。  "
          },
          {
            "line": 227,
            "text": "・seamless  "
          },
          {
            "line": 228,
            "text": "定義: 部分の切れ目が感じられないほど滑らかにつながっている。  "
          },
          {
            "line": 229,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 230,
            "text": "違い: 使う側から見て切れ目が意識されないことに重点があり、内部が実際に一体化しているかどうかは述べない。  "
          },
          {
            "line": 231,
            "text": "例: The app promises a seamless transfer between devices.  "
          },
          {
            "line": 232,
            "text": "訳: そのアプリは機器間の切れ目のない移行をうたっている。  "
          },
          {
            "line": 234,
            "text": "・coherent  "
          },
          {
            "line": 235,
            "text": "定義: 各部分が矛盾なく結び付いて筋が通っている。  "
          },
          {
            "line": 236,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 237,
            "text": "違い: 論理や方針の一貫性に重点があり、機器や組織が制度的に結合していることは表さない。  "
          },
          {
            "line": 238,
            "text": "例: The party still lacks a coherent economic policy.  "
          },
          {
            "line": 239,
            "text": "訳: その政党にはいまだに一貫した経済政策がない。  "
          },
          {
            "line": 241,
            "text": "【反意語】"
          },
          {
            "line": 243,
            "text": "・fragmented  "
          },
          {
            "line": 244,
            "text": "定義: 全体がばらばらの断片に分かれている。  "
          },
          {
            "line": 245,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 246,
            "text": "違い: 一つのまとまりとして働くのとは逆に、分かれて全体性を欠く状態を表す。  "
          },
          {
            "line": 247,
            "text": "例: The country's health system remains highly fragmented.  "
          },
          {
            "line": 248,
            "text": "訳: その国の医療制度は依然として非常に細分化されている。  "
          },
          {
            "line": 250,
            "text": "・disjointed  "
          },
          {
            "line": 251,
            "text": "定義: 部分どうしのつながりを欠いてばらばらである。  "
          },
          {
            "line": 252,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 253,
            "text": "違い: つながりの欠如を否定的に述べる語で、話、文章、動きに使う。  "
          },
          {
            "line": 254,
            "text": "例: His presentation was disjointed and hard to follow.  "
          },
          {
            "line": 255,
            "text": "訳: 彼の発表はまとまりがなく、ついていくのが難しかった。  "
          },
          {
            "line": 257,
            "text": "・standalone  "
          },
          {
            "line": 258,
            "text": "定義: 他と接続せずに単独で機能する。  "
          },
          {
            "line": 259,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 260,
            "text": "違い: 他と結び付いていない点で反対だが、欠陥ではなく単独で完結しているという中立的な評価を伴う。  "
          },
          {
            "line": 261,
            "text": "例: The software is sold as a standalone product as well as part of the suite.  "
          },
          {
            "line": 262,
            "text": "訳: そのソフトは製品群の一部としても単独製品としても販売されている。  "
          },
          {
            "line": 264,
            "text": "3. 【自動詞】（システム・要素が）統合される、連携する"
          },
          {
            "line": 303,
            "text": "【類義語】"
          },
          {
            "line": 305,
            "text": "・interoperate  "
          },
          {
            "line": 306,
            "text": "定義: 系統の異なる機器やソフトが互いに情報をやり取りして動作する。  "
          },
          {
            "line": 307,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 308,
            "text": "違い: 技術規格の文脈に限られる専門語で、相互に動作できるという能力を述べる。一般の製品説明では integrate のほうがはるかに普通である。  "
          },
          {
            "line": 309,
            "text": "例: The two hospital systems can interoperate through a shared data standard.  "
          },
          {
            "line": 310,
            "text": "訳: その二つの病院システムは共通のデータ規格を通じて相互に動作できる。  "
          },
          {
            "line": 312,
            "text": "・sync  "
          },
          {
            "line": 313,
            "text": "定義: 二つの機器やサービスが情報をそろえて同じ状態になる。  "
          },
          {
            "line": 314,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 315,
            "text": "違い: 情報の内容をそろえる操作に限られ、機能全体が連携するという意味はない。口語的で sync with の形が多い。  "
          },
          {
            "line": 316,
            "text": "例: The fitness tracker syncs with your phone every few minutes.  "
          },
          {
            "line": 317,
            "text": "訳: その活動量計は数分ごとに携帯電話と同期する。  "
          },
          {
            "line": 319,
            "text": "・mesh  "
          },
          {
            "line": 320,
            "text": "定義: 二つ以上のものがかみ合ってうまく働く。  "
          },
          {
            "line": 321,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 322,
            "text": "違い: かみ合いのよさという比喩に重点があり、計画、意見、日程にも使う。機器の接続という技術的な意味は薄い。  "
          },
          {
            "line": 323,
            "text": "例: The two schedules mesh surprisingly well.  "
          },
          {
            "line": 324,
            "text": "訳: その二つの日程は驚くほどよくかみ合っている。  "
          },
          {
            "line": 326,
            "text": "・dovetail  "
          },
          {
            "line": 327,
            "text": "定義: 二つのものが無駄なくぴったり合わさって機能する。  "
          },
          {
            "line": 328,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 329,
            "text": "違い: ぴったり合うという形の比喩で、計画や日程の相性を述べることが多い。装置やソフトの接続には使いにくい。  "
          },
          {
            "line": 330,
            "text": "例: The two projects dovetail neatly, so the teams can share data.  "
          },
          {
            "line": 331,
            "text": "訳: その二つの計画はうまくかみ合うので、両チームはデータを共有できる。  "
          },
          {
            "line": 333,
            "text": "・merge  "
          },
          {
            "line": 334,
            "text": "定義: 別々のものが境目を失って一つになる。  "
          },
          {
            "line": 335,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 336,
            "text": "違い: 元の区別がなくなる方向を含意し、連携して働くという意味はない。道路、企業、ファイルについて使う。  "
          },
          {
            "line": 337,
            "text": "例: The two lanes merge just after the bridge.  "
          },
          {
            "line": 338,
            "text": "訳: その二車線は橋を過ぎたところで合流する。  "
          },
          {
            "line": 340,
            "text": "4. 【他動詞】（人・集団を）溶け込ませる、一員にする"
          },
          {
            "line": 384,
            "text": "【類義語】"
          },
          {
            "line": 386,
            "text": "・assimilate  "
          },
          {
            "line": 387,
            "text": "定義: 少数派の集団に多数派の文化や習慣を取り入れさせ、区別がつかない状態にする。  "
          },
          {
            "line": 388,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 389,
            "text": "違い: 加わる側が元の特徴を失うことを含意しやすく、社会政策の議論では否定的に受け取られることがある。integrate は違いを保ったまま対等な構成員にするという含みで使える。  "
          },
          {
            "line": 390,
            "text": "例: The government was accused of trying to assimilate minority communities.  "
          },
          {
            "line": 391,
            "text": "訳: 政府は少数派の共同体を同化させようとしていると非難された。  "
          },
          {
            "line": 393,
            "text": "・include  "
          },
          {
            "line": 394,
            "text": "定義: 全体の一部として中に入れる、対象に数え入れる。  "
          },
          {
            "line": 395,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 396,
            "text": "違い: 対象として数え入れることが中心で、実際に関係が成り立つところまでは含意しない。教育政策では inclusion が integration と別の概念として使われる。  "
          },
          {
            "line": 397,
            "text": "例: The new policy includes part-time staff in the bonus scheme.  "
          },
          {
            "line": 398,
            "text": "訳: 新しい方針は非常勤職員を賞与制度の対象に含めている。  "
          },
          {
            "line": 400,
            "text": "・absorb  "
          },
          {
            "line": 401,
            "text": "定義: 大きな組織や集団が別の人や集団を取り込んで自分の一部にする。  "
          },
          {
            "line": 402,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 403,
            "text": "違い: 取り込む側の規模と主導性が強く、取り込まれた側の独自性は残らないという含みになる。対等な参加という含みはない。  "
          },
          {
            "line": 404,
            "text": "例: The larger union absorbed several smaller regional branches.  "
          },
          {
            "line": 405,
            "text": "訳: その大きな労働組合はいくつかの小さな地域支部を吸収した。  "
          },
          {
            "line": 407,
            "text": "・admit  "
          },
          {
            "line": 408,
            "text": "定義: 組織や施設への加入や入場を認める。  "
          },
          {
            "line": 409,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 410,
            "text": "違い: 加入の可否を認める手続きが中心で、加入後に関係が成り立つかどうかは述べない。  "
          },
          {
            "line": 411,
            "text": "例: The club finally admitted women as full members in 1998.  "
          },
          {
            "line": 412,
            "text": "訳: そのクラブは1998年にようやく女性を正会員として認めた。  "
          },
          {
            "line": 414,
            "text": "・mainstream  "
          },
          {
            "line": 415,
            "text": "定義: 特別な枠に置かれていた児童や利用者を通常の制度の中で扱う。  "
          },
          {
            "line": 416,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 417,
            "text": "違い: 教育や福祉の専門語で、通常の学級やサービスへ移すという制度上の措置を指す。社会全体への受け入れという広い意味はない。  "
          },
          {
            "line": 418,
            "text": "例: The school mainstreamed most of its special-education students.  "
          },
          {
            "line": 419,
            "text": "訳: その学校は特別支援教育の生徒の大半を通常学級へ移した。  "
          },
          {
            "line": 421,
            "text": "【反意語】"
          },
          {
            "line": 423,
            "text": "・segregate  "
          },
          {
            "line": 424,
            "text": "定義: 人種、性別、障害などを理由に人を別の場所や制度へ分けて置く。  "
          },
          {
            "line": 425,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 426,
            "text": "違い: 対等な構成員として受け入れるのとは逆に、意図的に分けて隔てる方向を表す。  "
          },
          {
            "line": 427,
            "text": "例: The old rules segregated students by ability from the age of eleven.  "
          },
          {
            "line": 428,
            "text": "訳: 古い規則は11歳から生徒を能力別に分けていた。  "
          },
          {
            "line": 430,
            "text": "・exclude  "
          },
          {
            "line": 431,
            "text": "定義: 対象から外して参加させない。  "
          },
          {
            "line": 432,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 433,
            "text": "違い: 受け入れの反対方向で、参加そのものを認めないことを表す。別に分けて置く segregate と違い、外に置く点に重点がある。  "
          },
          {
            "line": 434,
            "text": "例: The scheme excluded workers on short-term contracts.  "
          },
          {
            "line": 435,
            "text": "訳: その制度は短期契約の労働者を対象から外していた。  "
          },
          {
            "line": 437,
            "text": "・isolate  "
          },
          {
            "line": 438,
            "text": "定義: 人を周囲から切り離して孤立させる。  "
          },
          {
            "line": 439,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 440,
            "text": "違い: 集団の一員にするのと逆に、関係を断って一人にする方向を表す。制度上の分離ではなく関係の断絶に重点がある。  "
          },
          {
            "line": 441,
            "text": "例: Long night shifts isolated her from her colleagues.  "
          },
          {
            "line": 442,
            "text": "訳: 長く続く夜勤が彼女を同僚から孤立させた。  "
          },
          {
            "line": 444,
            "text": "5. 【自動詞】（人が）溶け込む、一員になる"
          },
          {
            "line": 483,
            "text": "【類義語】"
          },
          {
            "line": 485,
            "text": "・fit in  "
          },
          {
            "line": 486,
            "text": "定義: 周囲の人となじんで違和感なく過ごせるようになる。  "
          },
          {
            "line": 487,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 488,
            "text": "違い: 口語的で、周囲との相性や居心地に重点がある。制度や社会への参加という含みは薄い。  "
          },
          {
            "line": 489,
            "text": "例: It took him a while to fit in at his new school.  "
          },
          {
            "line": 490,
            "text": "訳: 彼は新しい学校になじむのに少し時間がかかった。  "
          },
          {
            "line": 492,
            "text": "・settle in  "
          },
          {
            "line": 493,
            "text": "定義: 新しい場所や仕事に慣れて落ち着く。  "
          },
          {
            "line": 494,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 495,
            "text": "違い: 環境に慣れることが中心で、集団の一員として受け入れられるかどうかは述べない。  "
          },
          {
            "line": 496,
            "text": "例: She soon settled in at her new office.  "
          },
          {
            "line": 497,
            "text": "訳: 彼女はすぐに新しい職場に慣れた。  "
          },
          {
            "line": 499,
            "text": "・assimilate  "
          },
          {
            "line": 500,
            "text": "定義: 少数派が多数派の文化や習慣を取り入れて区別がつかなくなる。  "
          },
          {
            "line": 501,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 502,
            "text": "違い: 元の文化的特徴を失う方向を含意する。integrate は違いを保ったまま参加するという含みで使える。  "
          },
          {
            "line": 503,
            "text": "例: Second-generation immigrants often assimilate more completely than their parents.  "
          },
          {
            "line": 504,
            "text": "訳: 移民の2世は親よりも完全に同化することが多い。  "
          },
          {
            "line": 506,
            "text": "・mix  "
          },
          {
            "line": 507,
            "text": "定義: 人と交わって付き合う。  "
          },
          {
            "line": 508,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 509,
            "text": "違い: 人と交際するという行為が中心で、集団の一員として定着することまでは含意しない。mix with の形で使う。  "
          },
          {
            "line": 510,
            "text": "例: He doesn't mix much with the other students.  "
          },
          {
            "line": 511,
            "text": "訳: 彼は他の学生とあまり交わらない。  "
          },
          {
            "line": 513,
            "text": "・blend in  "
          },
          {
            "line": 514,
            "text": "定義: 周囲と見分けがつかないほど目立たなくなる。  "
          },
          {
            "line": 515,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 516,
            "text": "違い: 目立たなくなることが中心で、関係を築いて参加することは含意しない。外見や振る舞いについて使う。  "
          },
          {
            "line": 517,
            "text": "例: He wore a suit so that he would blend in at the reception.  "
          },
          {
            "line": 518,
            "text": "訳: 彼は歓迎会で目立たないようにスーツを着た。  "
          },
          {
            "line": 520,
            "text": "【反意語】"
          },
          {
            "line": 522,
            "text": "・withdraw  "
          },
          {
            "line": 523,
            "text": "定義: 人との関わりを避けて集団から身を引く。  "
          },
          {
            "line": 524,
            "text": "頻度: 〈7/10〉  "
          },
          {
            "line": 525,
            "text": "違い: 一員になっていく方向とは逆に、関係から離れていく方向を表す。  "
          },
          {
            "line": 526,
            "text": "例: After the argument he withdrew from the group entirely.  "
          },
          {
            "line": 527,
            "text": "訳: 言い争いの後、彼は完全にそのグループから離れた。  "
          },
          {
            "line": 529,
            "text": "・keep to oneself  "
          },
          {
            "line": 530,
            "text": "定義: 他人と関わらずに一人で過ごす。  "
          },
          {
            "line": 531,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 532,
            "text": "違い: 集団に加わっていくのとは逆に、自分から関わりを持たない状態を表す。  "
          },
          {
            "line": 533,
            "text": "例: The new tenant keeps to himself and rarely speaks to the neighbors.  "
          },
          {
            "line": 534,
            "text": "訳: 新しい入居者は人と関わらず、近所の人ともめったに話さない。  "
          },
          {
            "line": 536,
            "text": "6. 【他動詞・自動詞・主に米国・社会】人種統合する、人種隔離を撤廃する"
          },
          {
            "line": 575,
            "text": "【類義語】"
          },
          {
            "line": 577,
            "text": "・desegregate  "
          },
          {
            "line": 578,
            "text": "定義: 法や規則による人種分離をやめさせる。  "
          },
          {
            "line": 579,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 580,
            "text": "違い: 分離を禁じるという制度上の措置に焦点があり、実際に複数の人種が同じ場にいる状態になったかどうかは述べない。  "
          },
          {
            "line": 581,
            "text": "例: The ruling required the city to desegregate its bus system.  "
          },
          {
            "line": 582,
            "text": "訳: その判決は市に対し、バス路線の人種分離をやめるよう求めた。  "
          },
          {
            "line": 584,
            "text": "・admit  "
          },
          {
            "line": 585,
            "text": "定義: これまで排除されていた人の入学や加入を認める。  "
          },
          {
            "line": 586,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 587,
            "text": "違い: 個々の加入を認める行為が中心で、制度全体の分離をやめるという意味はない。  "
          },
          {
            "line": 588,
            "text": "例: The college admitted its first Black students in 1955.  "
          },
          {
            "line": 589,
            "text": "訳: その大学は1955年に初めて黒人学生を受け入れた。  "
          },
          {
            "line": 591,
            "text": "・open  "
          },
          {
            "line": 592,
            "text": "定義: 一部の人にしか認められていなかった場や制度を、すべての人が利用できるようにする。  "
          },
          {
            "line": 593,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 594,
            "text": "違い: 利用資格を広げることが中心で、人種による分離の撤廃という限定はない。open A to B の形で使う。  "
          },
          {
            "line": 595,
            "text": "例: The 1964 law opened public accommodations to all citizens regardless of race.  "
          },
          {
            "line": 596,
            "text": "訳: 1964年の法律は、ホテルや飲食店など一般公衆に開かれた事業所を、人種にかかわらずすべての市民に開放した。  "
          },
          {
            "line": 598,
            "text": "【反意語】"
          },
          {
            "line": 600,
            "text": "・segregate  "
          },
          {
            "line": 601,
            "text": "定義: 人種などを理由に人を別の場所や制度へ分けて置く。  "
          },
          {
            "line": 602,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 603,
            "text": "違い: 人種統合とは正反対の方向で、同じ意味軸の上で分ける側を表す。  "
          },
          {
            "line": 604,
            "text": "例: State laws once segregated schools, buses, and parks.  "
          },
          {
            "line": 605,
            "text": "訳: 州法はかつて学校、バス、公園を人種別に分けていた。  "
          },
          {
            "line": 607,
            "text": "・resegregate  "
          },
          {
            "line": 608,
            "text": "定義: いったん人種統合された制度を再び人種別に分かれた状態にする。  "
          },
          {
            "line": 609,
            "text": "頻度: 〈2/10〉  "
          },
          {
            "line": 610,
            "text": "違い: 統合の後に元の分離状態へ戻る方向を表し、社会学や教育政策の議論で使う専門的な語である。  "
          },
          {
            "line": 611,
            "text": "例: Many districts quietly resegregated after the court orders ended.  "
          },
          {
            "line": 612,
            "text": "訳: 多くの学区は裁判所の命令が終わった後、静かに再び人種別に分かれていった。  "
          },
          {
            "line": 614,
            "text": "7. 【分詞形容詞・社会】分離をやめて統合された"
          },
          {
            "line": 648,
            "text": "【類義語】"
          },
          {
            "line": 650,
            "text": "・desegregated  "
          },
          {
            "line": 651,
            "text": "定義: 法や規則による人種分離が撤廃された状態である。  "
          },
          {
            "line": 652,
            "text": "頻度: 〈2/10〉  "
          },
          {
            "line": 653,
            "text": "違い: 分離を禁じる措置が取られたことに焦点があり、実際に複数の人種が同じ場にいるかどうかは述べない。  "
          },
          {
            "line": 654,
            "text": "例: Legally desegregated schools can still be almost entirely single-race.  "
          },
          {
            "line": 655,
            "text": "訳: 法的に人種分離が撤廃された学校でも、実際にはほぼ単一の人種だけということがある。  "
          },
          {
            "line": 657,
            "text": "・mixed  "
          },
          {
            "line": 658,
            "text": "定義: 複数の種類の人が混ざっている。  "
          },
          {
            "line": 659,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 660,
            "text": "違い: 構成が混ざっているという事実を述べる一般語で、分離の撤廃という制度上の経緯は含意しない。  "
          },
          {
            "line": 661,
            "text": "例: The school serves a mixed community of long-term residents and new arrivals.  "
          },
          {
            "line": 662,
            "text": "訳: その学校は長年の住民と新しく来た人が混ざる地域に対応している。  "
          },
          {
            "line": 664,
            "text": "・multiracial  "
          },
          {
            "line": 665,
            "text": "定義: 複数の人種から成る。  "
          },
          {
            "line": 666,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 667,
            "text": "違い: 構成の事実を述べる語で、分離をやめた結果であるという含みはない。人にも集団にも使う。  "
          },
          {
            "line": 668,
            "text": "例: They grew up in a multiracial suburb outside Chicago.  "
          },
          {
            "line": 669,
            "text": "訳: 彼らはシカゴ郊外の多人種の住宅地で育った。  "
          },
          {
            "line": 671,
            "text": "【反意語】"
          },
          {
            "line": 673,
            "text": "・segregated  "
          },
          {
            "line": 674,
            "text": "定義: 人種などを理由に分けられている。  "
          },
          {
            "line": 675,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 676,
            "text": "違い: 人種統合された状態とは正反対で、同じ意味軸の上で分けられた側を表す。  "
          },
          {
            "line": 677,
            "text": "例: Photographs of segregated waiting rooms still appear in textbooks.  "
          },
          {
            "line": 678,
            "text": "訳: 人種別に分けられた待合室の写真は今でも教科書に載っている。  "
          },
          {
            "line": 680,
            "text": "・all-white  "
          },
          {
            "line": 681,
            "text": "定義: 構成員が白人だけである。  "
          },
          {
            "line": 682,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 683,
            "text": "違い: 統合された状態とは逆に、単一の人種だけで構成されていることを述べる。分離が制度によるものかどうかは述べない。  "
          },
          {
            "line": 684,
            "text": "例: The town's only high school remained all-white until 1965.  "
          },
          {
            "line": 685,
            "text": "訳: その町の唯一の高校は1965年まで白人だけの学校のままだった。  "
          },
          {
            "line": 687,
            "text": "8. 【他動詞・数学】積分する"
          },
          {
            "line": 726,
            "text": "【類義語】"
          },
          {
            "line": 728,
            "text": "・antidifferentiate  "
          },
          {
            "line": 729,
            "text": "定義: 微分の逆の操作として原始関数を求める。  "
          },
          {
            "line": 730,
            "text": "頻度: 〈1/10〉  "
          },
          {
            "line": 731,
            "text": "違い: 不定積分を求める操作だけを指す教育用の語で、定積分や数値積分には使わない。数学の文章でもまれである。  "
          },
          {
            "line": 732,
            "text": "例: Students learn to antidifferentiate simple polynomials before studying definite integrals.  "
          },
          {
            "line": 733,
            "text": "訳: 学生は定積分を学ぶ前に、簡単な多項式の原始関数を求めることを学ぶ。  "
          },
          {
            "line": 735,
            "text": "・evaluate the integral  "
          },
          {
            "line": 736,
            "text": "定義: 立てられた積分の値を計算して求める。  "
          },
          {
            "line": 737,
            "text": "頻度: 〈3/10〉  "
          },
          {
            "line": 738,
            "text": "違い: どちらも積分の計算を行うことを指すが、evaluate the integral は立式済みの積分の値を出す段階に限られる。integrate は関数から積分を作る操作そのものを含む。  "
          },
          {
            "line": 739,
            "text": "例: Evaluate the integral by substituting u for the exponent.  "
          },
          {
            "line": 740,
            "text": "訳: 指数部を u に置き換えて、その積分の値を求めよ。  "
          },
          {
            "line": 742,
            "text": "【反意語】"
          },
          {
            "line": 744,
            "text": "・differentiate  "
          },
          {
            "line": 745,
            "text": "定義: 微積分で、関数の導関数を求める。  "
          },
          {
            "line": 746,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 747,
            "text": "違い: 積分と微分は互いに逆の操作であり、同じ意味軸の上で正反対の方向を表す。  "
          },
          {
            "line": 748,
            "text": "例: Differentiate the position function to find the velocity.  "
          },
          {
            "line": 749,
            "text": "訳: 位置の関数を微分すれば速度が求まる。  "
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
