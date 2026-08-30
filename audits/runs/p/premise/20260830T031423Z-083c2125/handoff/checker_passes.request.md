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
      "input_body_sha256": "1853b935aa8af00051a2dc94003c0f331997f6110d9b6181471417254083d528",
      "input_sections": {
        "definitions": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】議論、推論、判断、計画、行動などを進める際に、真である、またはひとまず受け入れるものとして置かれる考え・命題・仮定。その前提自体が実際に正しいことを `premise` という語が保証するわけではなく、`false premise`「誤った前提」のようにも使える。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 115,
            "text": "【日本語訳・定義】映画、小説、ドラマ、ゲーム、企画などを成立させる基本的な状況・設定・中心アイデア。作品によっては主要な筋立て・ストーリーラインの核まで指し、細かな出来事の並びをすべて指す `plot` より「作品を一文程度で要約できる土台」に焦点がある。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 167,
            "text": "【日本語訳・定義】論証・推論において、結論を導くための出発点として置かれる命題。三段論法では `major premise`「大前提」、`minor premise`「小前提」のように呼ぶ。一般語義1と連続しているが、ここでは論証の構成要素としてより厳密に用いる。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 219,
            "text": "【日本語訳・定義】人・会社・組織などが所有・占有・使用する土地、建物、建物の一部、およびそれに付随する敷地。会社・店舗・学校・病院・工場などの場所に特によく使うが、住宅や賃貸物件などにも使える。現代英語ではこの意味を通常 `premises` という複数形で表し、単数 `a premise` を「一つの建物・敷地」の意味では普通使わない。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 283,
            "text": "【日本語訳・定義】理論、議論、計画、判断などを、ある考え・仮定が真または受け入れられるものとして土台にして組み立てる。現代英語では、とくに受動態 `be premised on/upon ...`「～を前提としている、～に基づいている」が重要である。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 338,
            "text": "【日本語訳・定義】議論や推論を始める前に、ある命題・考えを前提として提示したり、真であるものとして仮に置いたりする。語義5の `premise A on B` では A が前提に基づいて組み立てられる対象だが、この語義では目的語・that節の内容そのものが「前提として置かれる内容」になる。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 53,
            "text": "【コロケーション】"
          },
          {
            "line": 55,
            "text": "・`the premise that ...`  "
          },
          {
            "line": 56,
            "text": "用途: 内容を that節で明示して「～という前提」を表す。  "
          },
          {
            "line": 57,
            "text": "例: The proposal rests on the premise that demand will continue to grow.  "
          },
          {
            "line": 58,
            "text": "訳: その提案は、需要が今後も伸び続けるという前提に立っている。  "
          },
          {
            "line": 60,
            "text": "・`on the premise that ...`  "
          },
          {
            "line": 61,
            "text": "用途: 判断・行動を何らかの仮定に基づいて行うことを示す。  "
          },
          {
            "line": 62,
            "text": "例: We planned the schedule on the premise that the parts would arrive by Friday.  "
          },
          {
            "line": 63,
            "text": "訳: 私たちは、部品が金曜日までに届くという前提で日程を組んだ。  "
          },
          {
            "line": 65,
            "text": "・`start from the premise that ...`  "
          },
          {
            "line": 66,
            "text": "用途: 議論や分析の出発点となる考えを示す。  "
          },
          {
            "line": 67,
            "text": "例: The report starts from the premise that access to data should be limited by purpose.  "
          },
          {
            "line": 68,
            "text": "訳: その報告書は、データへのアクセスは目的に応じて制限されるべきだという前提から出発している。  "
          },
          {
            "line": 70,
            "text": "・`an underlying premise`  "
          },
          {
            "line": 71,
            "text": "用途: 明示されていなくても、議論や制度の根底で支えている前提を指す。  "
          },
          {
            "line": 72,
            "text": "例: An underlying premise of the policy is that most users will follow the rules voluntarily.  "
          },
          {
            "line": 73,
            "text": "訳: その方針の根底にある前提の一つは、大半の利用者が自発的に規則を守るということである。  "
          },
          {
            "line": 75,
            "text": "・`a false/flawed premise`  "
          },
          {
            "line": 76,
            "text": "用途: 結論以前に、出発点となる仮定そのものに誤りや欠陥があることを示す。  "
          },
          {
            "line": 77,
            "text": "例: A convincing argument can still fail if it begins with a false premise.  "
          },
          {
            "line": 78,
            "text": "訳: 説得力のある議論でも、誤った前提から始まれば成り立たないことがある。  "
          },
          {
            "line": 80,
            "text": "・`question/challenge the premise`  "
          },
          {
            "line": 81,
            "text": "用途: 相手の結論ではなく、その結論を支える出発点そのものを疑う。  "
          },
          {
            "line": 82,
            "text": "例: Before discussing the cost, we should challenge the premise that the change is necessary.  "
          },
          {
            "line": 83,
            "text": "訳: 費用を議論する前に、その変更が必要だという前提自体を検討し直すべきだ。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 123,
            "text": "【コロケーション】"
          },
          {
            "line": 125,
            "text": "・`the premise of the film/show/book`  "
          },
          {
            "line": 126,
            "text": "用途: 作品の基本設定や中心アイデアを述べる。  "
          },
          {
            "line": 127,
            "text": "例: The premise of the film is simple: nobody in the town can tell a lie.  "
          },
          {
            "line": 128,
            "text": "訳: その映画の基本設定は単純で、町の誰も嘘をつけないというものだ。  "
          },
          {
            "line": 130,
            "text": "・`an intriguing premise`  "
          },
          {
            "line": 131,
            "text": "用途: 読者・視聴者の興味を引く基本設定を評価する。  "
          },
          {
            "line": 132,
            "text": "例: The novel has an intriguing premise, even though the middle chapters move slowly.  "
          },
          {
            "line": 133,
            "text": "訳: 中盤の展開は遅いものの、その小説には興味を引く基本設定がある。  "
          },
          {
            "line": 135,
            "text": "・`build a story around a premise`  "
          },
          {
            "line": 136,
            "text": "用途: 一つの中心設定を核として物語を展開する。  "
          },
          {
            "line": 137,
            "text": "例: The writers built the series around the premise that memories could be traded.  "
          },
          {
            "line": 138,
            "text": "訳: 脚本家たちは、記憶を売買できるという設定を中心にシリーズを構成した。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 175,
            "text": "【コロケーション】"
          },
          {
            "line": 177,
            "text": "・`major premise`  "
          },
          {
            "line": 178,
            "text": "用途: 伝統的なカテゴリー三段論法で、結論の述語となる major term（大項）を含む前提を指す。「より一般的な内容だから大前提」と定義されるわけではない。  "
          },
          {
            "line": 179,
            "text": "例: In “All metals conduct electricity; copper is a metal; therefore copper conducts electricity,” the first statement is the major premise because it contains the predicate term of the conclusion.  "
          },
          {
            "line": 180,
            "text": "訳: 「すべての金属は電気を通す。銅は金属である。したがって銅は電気を通す」という三段論法では、最初の命題が結論の述語となる大項を含むため大前提である。  "
          },
          {
            "line": 182,
            "text": "・`minor premise`  "
          },
          {
            "line": 183,
            "text": "用途: 伝統的なカテゴリー三段論法で、結論の主語となる minor term（小項）を含む前提を指す。「個別的な内容だから小前提」と定義されるわけではない。  "
          },
          {
            "line": 184,
            "text": "例: In the same syllogism, “Copper is a metal” is the minor premise because it contains the subject term of the conclusion.  "
          },
          {
            "line": 185,
            "text": "訳: 同じ三段論法では、「銅は金属である」が結論の主語となる小項を含むため小前提である。  "
          },
          {
            "line": 187,
            "text": "・`premises and conclusion`  "
          },
          {
            "line": 188,
            "text": "用途: 論証を、根拠として置かれる命題群と、そこから導かれる結論に分けて捉える。  "
          },
          {
            "line": 189,
            "text": "例: To evaluate the argument, separate its premises from its conclusion.  "
          },
          {
            "line": 190,
            "text": "訳: その論証を評価するには、前提群と結論を分けて考えなさい。  "
          },
          {
            "line": 192,
            "text": "・`infer a conclusion from the premises`  "
          },
          {
            "line": 193,
            "text": "用途: 与えられた前提から推論によって結論を導く。  "
          },
          {
            "line": 194,
            "text": "例: The conclusion cannot be inferred from the premises without an additional assumption.  "
          },
          {
            "line": 195,
            "text": "訳: 追加の仮定がなければ、その前提群からその結論を導くことはできない。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 227,
            "text": "【コロケーション】"
          },
          {
            "line": 229,
            "text": "・`on the premises`  "
          },
          {
            "line": 230,
            "text": "用途: 建物・敷地の内側で行われることを表す。`premises` に所有格を付けず、特定の構内なら `the` を使うことが多い。  "
          },
          {
            "line": 231,
            "text": "例: Smoking is not permitted anywhere on the premises.  "
          },
          {
            "line": 232,
            "text": "訳: この敷地内では、どこであっても喫煙は認められていない。  "
          },
          {
            "line": 234,
            "text": "・`off the premises`  "
          },
          {
            "line": 235,
            "text": "用途: 建物・敷地の外へ出た場所、または外で行うことを表す。  "
          },
          {
            "line": 236,
            "text": "例: Confidential documents must not be taken off the premises without permission.  "
          },
          {
            "line": 237,
            "text": "訳: 機密文書を許可なく構外へ持ち出してはならない。  "
          },
          {
            "line": 239,
            "text": "・`leave/vacate the premises`  "
          },
          {
            "line": 240,
            "text": "用途: 人が構内を離れる、または占有者が建物・敷地から退去することを表す。`vacate` はより形式的。  "
          },
          {
            "line": 241,
            "text": "例: Visitors must leave the premises by 9 p.m.  "
          },
          {
            "line": 242,
            "text": "訳: 来訪者は午後9時までに構内から退出しなければならない。  "
          },
          {
            "line": 244,
            "text": "・`business/commercial premises`  "
          },
          {
            "line": 245,
            "text": "用途: 事業に使用される建物・敷地をまとめて表す。  "
          },
          {
            "line": 246,
            "text": "例: The company moved to larger business premises near the station.  "
          },
          {
            "line": 247,
            "text": "訳: その会社は駅の近くの、より広い事業用施設へ移転した。  "
          },
          {
            "line": 249,
            "text": "・`the premises are ...`  "
          },
          {
            "line": 250,
            "text": "用途: `premises` を複数扱いして状態を述べる。  "
          },
          {
            "line": 251,
            "text": "例: The premises are protected by security cameras at all times.  "
          },
          {
            "line": 252,
            "text": "訳: その施設は常時、防犯カメラで監視されている。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 291,
            "text": "【コロケーション】"
          },
          {
            "line": 293,
            "text": "・`be premised on the assumption that ...`  "
          },
          {
            "line": 294,
            "text": "用途: 理論・計画などの根底にある仮定を明示する。  "
          },
          {
            "line": 295,
            "text": "例: The forecast is premised on the assumption that interest rates will remain unchanged.  "
          },
          {
            "line": 296,
            "text": "訳: その予測は、金利が据え置かれるという仮定を前提にしている。  "
          },
          {
            "line": 298,
            "text": "・`be premised on the idea that ...`  "
          },
          {
            "line": 299,
            "text": "用途: 制度・主張などが、ある考えを出発点として構成されていることを表す。  "
          },
          {
            "line": 300,
            "text": "例: The program is premised on the idea that early support can prevent larger problems later.  "
          },
          {
            "line": 301,
            "text": "訳: そのプログラムは、早期支援によって後の大きな問題を防げるという考えに基づいている。  "
          },
          {
            "line": 303,
            "text": "・`premise an argument on/upon ...`  "
          },
          {
            "line": 304,
            "text": "用途: 議論を特定の前提に基づかせる。能動態は受動態より形式的で、頻度も低い。  "
          },
          {
            "line": 305,
            "text": "例: The author premises the argument on a distinction between legal ownership and practical control.  "
          },
          {
            "line": 306,
            "text": "訳: 著者は、法的所有と実質的支配の区別を前提としてその議論を組み立てている。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 346,
            "text": "【コロケーション】"
          },
          {
            "line": 348,
            "text": "・`premise that ...`  "
          },
          {
            "line": 349,
            "text": "用途: 後続の議論のため、that節の内容そのものを前提として置く。  "
          },
          {
            "line": 350,
            "text": "例: The author premises that each participant has access to the same information.  "
          },
          {
            "line": 351,
            "text": "訳: 著者は、各参加者が同じ情報にアクセスできることを前提として置いている。  "
          },
          {
            "line": 353,
            "text": "・`let us premise that ...`  "
          },
          {
            "line": 354,
            "text": "用途: 論証の冒頭で、検討のための前提を明示的に設定する。現代ではかなり硬い。  "
          },
          {
            "line": 355,
            "text": "例: Let us premise that the two measurements were taken under identical conditions.  "
          },
          {
            "line": 356,
            "text": "訳: 2回の測定は同一条件で行われたと前提としておこう。  "
          },
          {
            "line": 358,
            "text": "・`premise a proposition`  "
          },
          {
            "line": 359,
            "text": "用途: 命題そのものを、後の推論に先立つ前提として提示する。  "
          },
          {
            "line": 360,
            "text": "例: The author premises a proposition about human motivation before turning to the main argument.  "
          },
          {
            "line": 361,
            "text": "訳: 著者は本論に入る前に、人間の動機に関する命題を前提として提示している。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 90,
            "text": "【類義語】"
          },
          {
            "line": 92,
            "text": "・assumption  "
          },
          {
            "line": 93,
            "text": "定義: 証明・確認されていないが、ひとまず真として受け入れる考え。  "
          },
          {
            "line": 94,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 95,
            "text": "違い: `assumption` は日常的な思い込みや計画上の仮定にも広く使える。`premise` は、その考えを土台に議論・推論・判断を組み立てる関係をより強く示す。  "
          },
          {
            "line": 96,
            "text": "例: Our cost estimate is based on the assumption that fuel prices will remain stable.  "
          },
          {
            "line": 97,
            "text": "訳: 私たちの費用見積もりは、燃料価格が安定したままだという仮定に基づいている。  "
          },
          {
            "line": 99,
            "text": "・presupposition  "
          },
          {
            "line": 100,
            "text": "定義: 発言・理論・考えの背後ですでに成り立つものとして想定されている前提。  "
          },
          {
            "line": 101,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 102,
            "text": "違い: `premise` が明示的な論証の土台にも使えるのに対し、`presupposition` は暗黙に先取りされている前提という含みが強く、言語学・哲学でも使われる。  "
          },
          {
            "line": 103,
            "text": "例: The question contains the presupposition that someone made the decision deliberately.  "
          },
          {
            "line": 104,
            "text": "訳: その質問には、誰かが意図的にその決定をしたという前提が含まれている。  "
          },
          {
            "line": 106,
            "text": "・basis  "
          },
          {
            "line": 107,
            "text": "定義: 判断・主張・制度などを支える根拠・基礎。  "
          },
          {
            "line": 108,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 109,
            "text": "違い: `basis` は事実、証拠、原則、計算方法など幅広い「基礎」を表せる。`premise` は特に、真として置く考え・命題を指す。  "
          },
          {
            "line": 110,
            "text": "例: There is no factual basis for the claim.  "
          },
          {
            "line": 111,
            "text": "訳: その主張には事実上の根拠がない。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 142,
            "text": "【類義語】"
          },
          {
            "line": 144,
            "text": "・concept  "
          },
          {
            "line": 145,
            "text": "定義: 作品・企画・製品などの中心となる発想・概念。  "
          },
          {
            "line": 146,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 147,
            "text": "違い: `concept` は視覚的・商品的・抽象的なアイデアにも広く使える。`premise` は「この条件・状況を出発点にすると何が起こるか」という物語的な設定に向きやすい。  "
          },
          {
            "line": 148,
            "text": "例: The design concept combines a library with a community workspace.  "
          },
          {
            "line": 149,
            "text": "訳: その設計コンセプトは、図書館と地域の共同作業空間を組み合わせている。  "
          },
          {
            "line": 151,
            "text": "・setup  "
          },
          {
            "line": 152,
            "text": "定義: 物語の冒頭で人物・状況・対立関係を整える設定・導入。  "
          },
          {
            "line": 153,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 154,
            "text": "違い: `setup` は物語が動き出すための具体的な初期配置に焦点がある。`premise` は作品全体を支える中心アイデアまで含み得る。  "
          },
          {
            "line": 155,
            "text": "例: The opening scene establishes the setup for the mystery.  "
          },
          {
            "line": 156,
            "text": "訳: 冒頭の場面で、そのミステリーの初期設定が示される。  "
          },
          {
            "line": 158,
            "text": "・plot  "
          },
          {
            "line": 159,
            "text": "定義: 物語で起きる出来事の筋、展開。  "
          },
          {
            "line": 160,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 161,
            "text": "違い: `plot` は出来事の連鎖そのもの。`premise` はその連鎖を生み出す基本条件・着想である。  "
          },
          {
            "line": 162,
            "text": "例: The plot becomes more complicated after the second episode.  "
          },
          {
            "line": 163,
            "text": "訳: 物語の筋は第2話以降さらに複雑になる。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 201,
            "text": "【類義語】"
          },
          {
            "line": 203,
            "text": "・proposition  "
          },
          {
            "line": 204,
            "text": "定義: 真か偽かを問いうる内容を持つ命題。  "
          },
          {
            "line": 205,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 206,
            "text": "違い: `proposition` は命題そのものの種類を表し、結論にもなり得る。`premise` は論証の中で、その命題が結論を支える役割に置かれていることを表す。  "
          },
          {
            "line": 207,
            "text": "例: The proposition is false, but it can still be used to illustrate the form of the argument.  "
          },
          {
            "line": 208,
            "text": "訳: その命題は偽だが、論証の形式を示すためには使える。  "
          },
          {
            "line": 210,
            "text": "・assumption  "
          },
          {
            "line": 211,
            "text": "定義: 推論のために真として置く仮定。  "
          },
          {
            "line": 212,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 213,
            "text": "違い: `assumption` は明示されない補助的な仮定にも使える。`premise` は論証の構成要素として提示された命題を指しやすい。  "
          },
          {
            "line": 214,
            "text": "例: The proof depends on an unstated assumption about continuity.  "
          },
          {
            "line": 215,
            "text": "訳: その証明は、連続性についての明示されていない仮定に依存している。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 258,
            "text": "【類義語】"
          },
          {
            "line": 260,
            "text": "・property  "
          },
          {
            "line": 261,
            "text": "定義: 所有される土地・建物、不動産。  "
          },
          {
            "line": 262,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 263,
            "text": "違い: `property` は所有物・不動産としての法的・経済的な対象に焦点があり、個人住宅にも広く使える。`premises` は所有者が誰かより、その場所が占有・使用される物理的な建物・敷地として捉えられることが多い。  "
          },
          {
            "line": 264,
            "text": "例: The company owns several properties in the city.  "
          },
          {
            "line": 265,
            "text": "訳: その会社は市内に複数の不動産を所有している。  "
          },
          {
            "line": 267,
            "text": "・site  "
          },
          {
            "line": 268,
            "text": "定義: 建物・活動・工事などが置かれている、または行われる場所・敷地。  "
          },
          {
            "line": 269,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 270,
            "text": "違い: `site` は場所そのものに焦点があり、建物がまだない土地にも使える。`premises` は既に占有・使用されている建物・敷地をまとめて指しやすい。  "
          },
          {
            "line": 271,
            "text": "例: Construction will begin on the new site next month.  "
          },
          {
            "line": 272,
            "text": "訳: 新しい敷地では来月、建設工事が始まる。  "
          },
          {
            "line": 274,
            "text": "・facility  "
          },
          {
            "line": 275,
            "text": "定義: 特定の目的のために設けられた建物・設備。  "
          },
          {
            "line": 276,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 277,
            "text": "違い: `facility` は機能・設備に焦点があり、研究施設・製造施設など用途を強調する。`premises` は用途の詳細より、物理的な構内全体を指す。  "
          },
          {
            "line": 278,
            "text": "例: The laboratory operates a testing facility outside the city.  "
          },
          {
            "line": 279,
            "text": "訳: その研究所は市外で試験施設を運営している。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 313,
            "text": "【類義語】"
          },
          {
            "line": 315,
            "text": "・base  "
          },
          {
            "line": 316,
            "text": "定義: 考え・行動・判断などを、特定の根拠・情報・原則に基づかせる。  "
          },
          {
            "line": 317,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 318,
            "text": "違い: `base A on B` は証拠・データ・経験などにも非常に広く使える。`premise A on B` は B が「前提として置かれる考え・仮定」である場合に特に適し、より形式的。  "
          },
          {
            "line": 319,
            "text": "例: The decision was based on updated safety data.  "
          },
          {
            "line": 320,
            "text": "訳: その決定は最新の安全データに基づいていた。  "
          },
          {
            "line": 322,
            "text": "・found  "
          },
          {
            "line": 323,
            "text": "定義: 理論・制度・主張などを、ある原理・根拠の上に築く。  "
          },
          {
            "line": 324,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 325,
            "text": "違い: `be founded on ...` は基礎となる原理・価値・事実にも使え、`premised on` より「築かれている」という比喩が強い。  "
          },
          {
            "line": 326,
            "text": "例: The organization was founded on the principle of equal access.  "
          },
          {
            "line": 327,
            "text": "訳: その組織は、平等なアクセスという原則に基づいて設立された。  "
          },
          {
            "line": 329,
            "text": "・predicate  "
          },
          {
            "line": 330,
            "text": "定義: 主張・判断などを、ある条件・事実・前提に依存させる。  "
          },
          {
            "line": 331,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 332,
            "text": "違い: `predicate A on B` は非常に形式的で、法律・学術で見られる。`premise A on B` と近いが、`premise` は「前提命題を置く」という語源・論証とのつながりがより直接的である。  "
          },
          {
            "line": 333,
            "text": "例: The claim is predicated on evidence that has since been disputed.  "
          },
          {
            "line": 334,
            "text": "訳: その主張は、その後争われるようになった証拠を前提としている。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 367,
            "text": "【類義語】"
          },
          {
            "line": 369,
            "text": "・assume  "
          },
          {
            "line": 370,
            "text": "定義: 証明せずに、ある内容をひとまず真として受け入れる。  "
          },
          {
            "line": 371,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 372,
            "text": "違い: `assume` は日常・学術のどちらでも広く使え、`premise` よりはるかに一般的。`premise` は論証の前提として明示的に置くという硬い響きがある。  "
          },
          {
            "line": 373,
            "text": "例: Assume that the two samples are independent.  "
          },
          {
            "line": 374,
            "text": "訳: 2つの標本は独立していると仮定しなさい。  "
          },
          {
            "line": 376,
            "text": "・posit  "
          },
          {
            "line": 377,
            "text": "定義: 議論・理論のために、命題や仮説を明示的に提示する。  "
          },
          {
            "line": 378,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 379,
            "text": "違い: `posit` は学術・哲学で比較的自然に使える一方、この語義の `premise` はさらにまれで古風・形式的に感じられることがある。  "
          },
          {
            "line": 380,
            "text": "例: The model posits that agents act on incomplete information.  "
          },
          {
            "line": 381,
            "text": "訳: そのモデルは、行為者は不完全な情報に基づいて行動すると仮定している。  "
          },
          {
            "line": 383,
            "text": "・postulate  "
          },
          {
            "line": 384,
            "text": "定義: 理論や推論の出発点として、命題・原理を仮定する。  "
          },
          {
            "line": 385,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 386,
            "text": "違い: `postulate` は科学・数学・哲学で「理論上の仮定として置く」ことを明確に表せる。`premise` は同じ方向を表せるが、動詞としては使用範囲が狭い。  "
          },
          {
            "line": 387,
            "text": "例: The theory postulates the existence of an unobserved mechanism.  "
          },
          {
            "line": 388,
            "text": "訳: その理論は、観測されていない機構の存在を仮定している。  "
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
      "input_body_sha256": "1853b935aa8af00051a2dc94003c0f331997f6110d9b6181471417254083d528",
      "input_sections": {
        "core_image": [
          {
            "line": 31,
            "text": "＃コアイメージ"
          },
          {
            "line": 33,
            "text": "`premise` の中心は、「後に続く結論・判断・構成を支えるものを、先に置いて土台にする」である。議論では命題を先に置き、判断では仮定を土台にし、作品では物語を成立させる基本設定を置く。動詞では、その土台の上に理論や主張を組み立てることを表す。  "
          },
          {
            "line": 34,
            "text": "・議論・判断の土台として置く考え → 「前提、仮定」（語義1）  "
          },
          {
            "line": 35,
            "text": "・作品を成立させる土台の設定・筋立ての核 → 「基本設定、中心的な着想」（語義2）  "
          },
          {
            "line": 36,
            "text": "・論理学で結論を導くために置く命題 → 「前提命題」（語義3）  "
          },
          {
            "line": 37,
            "text": "・理論・主張などをある考えの上に置く → 「～を…に基づかせる」（語義5）  "
          },
          {
            "line": 38,
            "text": "・命題や考え自体を前提として先に置く → 「～を前提として述べる・仮定する」（語義6）  "
          },
          {
            "line": 39,
            "text": "`premises`「建物・敷地」（語義4）は歴史的には同じ語から発達したが、現代話者にとって上のコアイメージから直接推測しにくい定着義なので、別に覚える。  "
          }
        ],
        "sense_structure": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】議論、推論、判断、計画、行動などを進める際に、真である、またはひとまず受け入れるものとして置かれる考え・命題・仮定。その前提自体が実際に正しいことを `premise` という語が保証するわけではなく、`false premise`「誤った前提」のようにも使える。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 115,
            "text": "【日本語訳・定義】映画、小説、ドラマ、ゲーム、企画などを成立させる基本的な状況・設定・中心アイデア。作品によっては主要な筋立て・ストーリーラインの核まで指し、細かな出来事の並びをすべて指す `plot` より「作品を一文程度で要約できる土台」に焦点がある。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 167,
            "text": "【日本語訳・定義】論証・推論において、結論を導くための出発点として置かれる命題。三段論法では `major premise`「大前提」、`minor premise`「小前提」のように呼ぶ。一般語義1と連続しているが、ここでは論証の構成要素としてより厳密に用いる。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 219,
            "text": "【日本語訳・定義】人・会社・組織などが所有・占有・使用する土地、建物、建物の一部、およびそれに付随する敷地。会社・店舗・学校・病院・工場などの場所に特によく使うが、住宅や賃貸物件などにも使える。現代英語ではこの意味を通常 `premises` という複数形で表し、単数 `a premise` を「一つの建物・敷地」の意味では普通使わない。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 283,
            "text": "【日本語訳・定義】理論、議論、計画、判断などを、ある考え・仮定が真または受け入れられるものとして土台にして組み立てる。現代英語では、とくに受動態 `be premised on/upon ...`「～を前提としている、～に基づいている」が重要である。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 338,
            "text": "【日本語訳・定義】議論や推論を始める前に、ある命題・考えを前提として提示したり、真であるものとして仮に置いたりする。語義5の `premise A on B` では A が前提に基づいて組み立てられる対象だが、この語義では目的語・that節の内容そのものが「前提として置かれる内容」になる。  "
          }
        ],
        "usage_notes": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 85,
            "text": "【語法・注意】`premise` は「結論を支える土台」に焦点があり、単に未確認の予想を表す `assumption` より論証・判断との結びつきが強い。`on the premise that ...` と `on the assumption that ...` は重なるが、前者は議論・方針の明示的な根拠という響きがやや強い。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 140,
            "text": "【語法・注意】この語義の `premise` と `plot` は重なることがあるが、通常は焦点が異なる。`premise` は物語を生む基本状況・中心アイデア、または主要な筋立ての核を要約するのに向き、`plot` は出来事がどのような順序・因果で展開するかという具体的な筋書きに焦点がある。`concept` はさらに広く、作品以外の発想や概念にも使える。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 197,
            "text": "【語法・注意】論理学では、「前提が真であること」と「推論が妥当であること」を混同しない。妥当な論証は、前提が真なら結論が偽にならない形を持つことを問題にするのであり、`valid premise` を単純に「真の前提」の意味で使うより、`true premise` と `valid argument/inference` を区別するほうが正確である。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 254,
            "text": "【語法・注意】この意味の `premises` は見た目が複数形で、標準的には複数動詞を取る。`These premises are ...`、`the premises have ...` のように考える。単数の建物や物件を指したい場合も、通常は `a premise` ではなく `a building`、`a property`、`a site` などを使う。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 308,
            "text": "【語法・注意】動詞の中心構文は `premise A on/upon B` で、A が「組み立てられる理論・主張・行動」、B が「その土台となる前提」である。方向を逆にしない。受動態では `A is premised on B` となり、学習者にとって最も遭遇しやすい形である。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 363,
            "text": "【語法・注意】この語義は現代英語では低頻度で、学習上は語義5の `be premised on/upon ...` のほうを優先する。`premise that P` では P 自体を前提として置くのに対し、`A is premised on P` では A が P を土台として組み立てられている。項の方向が異なるので混同しない。  "
          }
        ],
        "word_formation": [
          {
            "line": 24,
            "text": "＃語形成"
          },
          {
            "line": 26,
            "text": "・premises：`premise` の通常の複数形。また、複数形の形に固定して「（事業所などの）建物・敷地」を表す。後者でも文法上は複数扱いが基本で、`the premises are ...` のように使う。  "
          },
          {
            "line": 27,
            "text": "・premised：動詞 *premise* の過去形・過去分詞。とくに `be premised on/upon ...`「～を前提としている、～に基づいている」で頻出する。  "
          },
          {
            "line": 28,
            "text": "・premising：動詞 *premise* の現在分詞・動名詞。一般語としての頻度は高くなく、論証や形式的な説明で現れる。  "
          },
          {
            "line": 29,
            "text": "・premiss：主にイギリス英語で見られる異綴り。とくに論理学の「前提命題」で用いられることがあるが、`premise` のほうが広く通用する。  "
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
      "input_body_sha256": "1853b935aa8af00051a2dc94003c0f331997f6110d9b6181471417254083d528",
      "input_sections": {
        "antonym_items": []
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
      "input_body_sha256": "1853b935aa8af00051a2dc94003c0f331997f6110d9b6181471417254083d528",
      "input_sections": {
        "sense_structure": [
          {
            "sense_id": "sense:001",
            "line": 43,
            "label": "1. 【名詞・可算】前提、仮定、議論・判断の出発点",
            "definition": "議論、推論、判断、計画、行動などを進める際に、真である、またはひとまず受け入れるものとして置かれる考え・命題・仮定。その前提自体が実際に正しいことを `premise` という語が保証するわけではなく、`false premise`「誤った前提」のようにも使える。"
          },
          {
            "sense_id": "sense:002",
            "line": 113,
            "label": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想",
            "definition": "映画、小説、ドラマ、ゲーム、企画などを成立させる基本的な状況・設定・中心アイデア。作品によっては主要な筋立て・ストーリーラインの核まで指し、細かな出来事の並びをすべて指す `plot` より「作品を一文程度で要約できる土台」に焦点がある。"
          },
          {
            "sense_id": "sense:003",
            "line": 165,
            "label": "3. 【名詞・可算・論理学】前提命題、推論の前提",
            "definition": "論証・推論において、結論を導くための出発点として置かれる命題。三段論法では `major premise`「大前提」、`minor premise`「小前提」のように呼ぶ。一般語義1と連続しているが、ここでは論証の構成要素としてより厳密に用いる。"
          },
          {
            "sense_id": "sense:004",
            "line": 217,
            "label": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）",
            "definition": "人・会社・組織などが所有・占有・使用する土地、建物、建物の一部、およびそれに付随する敷地。会社・店舗・学校・病院・工場などの場所に特によく使うが、住宅や賃貸物件などにも使える。現代英語ではこの意味を通常 `premises` という複数形で表し、単数 `a premise` を「一つの建物・敷地」の意味では普通使わない。"
          },
          {
            "sense_id": "sense:005",
            "line": 281,
            "label": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる",
            "definition": "理論、議論、計画、判断などを、ある考え・仮定が真または受け入れられるものとして土台にして組み立てる。現代英語では、とくに受動態 `be premised on/upon ...`「～を前提としている、～に基づいている」が重要である。"
          },
          {
            "sense_id": "sense:006",
            "line": 336,
            "label": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する",
            "definition": "議論や推論を始める前に、ある命題・考えを前提として提示したり、真であるものとして仮に置いたりする。語義5の `premise A on B` では A が前提に基づいて組み立てられる対象だが、この語義では目的語・that節の内容そのものが「前提として置かれる内容」になる。"
          }
        ],
        "collocations_examples": [
          {
            "example_id": "ex-c868d17ca028",
            "example": "The premise of the film is simple: nobody in the town can tell a lie.",
            "translation": "その映画の基本設定は単純で、町の誰も嘘をつけないというものだ。"
          },
          {
            "example_id": "ex-92be1a0b2a54",
            "example": "The author premises the argument on a distinction between legal ownership and practical control.",
            "translation": "著者は、法的所有と実質的支配の区別を前提としてその議論を組み立てている。"
          },
          {
            "example_id": "ex-5b3aa43593b4",
            "example": "The company moved to larger business premises near the station.",
            "translation": "その会社は駅の近くの、より広い事業用施設へ移転した。"
          },
          {
            "example_id": "ex-8664d9b0b5fb",
            "example": "The author premises a proposition about human motivation before turning to the main argument.",
            "translation": "著者は本論に入る前に、人間の動機に関する命題を前提として提示している。"
          },
          {
            "example_id": "ex-42ea2168be2d",
            "example": "In “All metals conduct electricity; copper is a metal; therefore copper conducts electricity,” the first statement is the major premise because it contains the predicate term of the conclusion.",
            "translation": "「すべての金属は電気を通す。銅は金属である。したがって銅は電気を通す」という三段論法では、最初の命題が結論の述語となる大項を含むため大前提である。"
          },
          {
            "example_id": "ex-a8c8ebaafeed",
            "example": "Smoking is not permitted anywhere on the premises.",
            "translation": "この敷地内では、どこであっても喫煙は認められていない。"
          },
          {
            "example_id": "ex-5351a9ca37e7",
            "example": "The forecast is premised on the assumption that interest rates will remain unchanged.",
            "translation": "その予測は、金利が据え置かれるという仮定を前提にしている。"
          },
          {
            "example_id": "ex-f6332a3258f6",
            "example": "To evaluate the argument, separate its premises from its conclusion.",
            "translation": "その論証を評価するには、前提群と結論を分けて考えなさい。"
          },
          {
            "example_id": "ex-9a2d16f3c747",
            "example": "The proposal rests on the premise that demand will continue to grow.",
            "translation": "その提案は、需要が今後も伸び続けるという前提に立っている。"
          },
          {
            "example_id": "ex-cf443fc21baa",
            "example": "Visitors must leave the premises by 9 p.m.",
            "translation": "来訪者は午後9時までに構内から退出しなければならない。"
          },
          {
            "example_id": "ex-b9c53956ba0a",
            "example": "An underlying premise of the policy is that most users will follow the rules voluntarily.",
            "translation": "その方針の根底にある前提の一つは、大半の利用者が自発的に規則を守るということである。"
          },
          {
            "example_id": "ex-dcc4043eb0ad",
            "example": "Before discussing the cost, we should challenge the premise that the change is necessary.",
            "translation": "費用を議論する前に、その変更が必要だという前提自体を検討し直すべきだ。"
          },
          {
            "example_id": "ex-b40774d14087",
            "example": "The program is premised on the idea that early support can prevent larger problems later.",
            "translation": "そのプログラムは、早期支援によって後の大きな問題を防げるという考えに基づいている。"
          },
          {
            "example_id": "ex-5856e63c43bb",
            "example": "Let us premise that the two measurements were taken under identical conditions.",
            "translation": "2回の測定は同一条件で行われたと前提としておこう。"
          },
          {
            "example_id": "ex-dc48b2fcfb25",
            "example": "A convincing argument can still fail if it begins with a false premise.",
            "translation": "説得力のある議論でも、誤った前提から始まれば成り立たないことがある。"
          },
          {
            "example_id": "ex-b57086d73e3b",
            "example": "In the same syllogism, “Copper is a metal” is the minor premise because it contains the subject term of the conclusion.",
            "translation": "同じ三段論法では、「銅は金属である」が結論の主語となる小項を含むため小前提である。"
          },
          {
            "example_id": "ex-d67387564b98",
            "example": "The writers built the series around the premise that memories could be traded.",
            "translation": "脚本家たちは、記憶を売買できるという設定を中心にシリーズを構成した。"
          },
          {
            "example_id": "ex-45cb42865390",
            "example": "The conclusion cannot be inferred from the premises without an additional assumption.",
            "translation": "追加の仮定がなければ、その前提群からその結論を導くことはできない。"
          },
          {
            "example_id": "ex-0aa16317b245",
            "example": "Confidential documents must not be taken off the premises without permission.",
            "translation": "機密文書を許可なく構外へ持ち出してはならない。"
          },
          {
            "example_id": "ex-f92944e569e3",
            "example": "The premises are protected by security cameras at all times.",
            "translation": "その施設は常時、防犯カメラで監視されている。"
          },
          {
            "example_id": "ex-7a82c406999a",
            "example": "The report starts from the premise that access to data should be limited by purpose.",
            "translation": "その報告書は、データへのアクセスは目的に応じて制限されるべきだという前提から出発している。"
          },
          {
            "example_id": "ex-c4fa080c837f",
            "example": "The author premises that each participant has access to the same information.",
            "translation": "著者は、各参加者が同じ情報にアクセスできることを前提として置いている。"
          },
          {
            "example_id": "ex-212458e2130a",
            "example": "The novel has an intriguing premise, even though the middle chapters move slowly.",
            "translation": "中盤の展開は遅いものの、その小説には興味を引く基本設定がある。"
          },
          {
            "example_id": "ex-48dba812059b",
            "example": "We planned the schedule on the premise that the parts would arrive by Friday.",
            "translation": "私たちは、部品が金曜日までに届くという前提で日程を組んだ。"
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
      "input_body_sha256": "1853b935aa8af00051a2dc94003c0f331997f6110d9b6181471417254083d528",
      "input_sections": {
        "etymology": [
          {
            "line": 19,
            "text": "＃語源"
          },
          {
            "line": 21,
            "text": "中英語の *premise* は、古フランス語を経て中世ラテン語 *praemissa (propositio)*「前に置かれた命題」にさかのぼる。*praemissa* はラテン語 *praemittere*「前に送る、先に述べる」に由来し、*prae-*「前に」＋ *mittere*「送る」から成る。論証で結論より先に置かれる命題という発想が、現在の「推論・議論の前提」につながった。  "
          },
          {
            "line": 22,
            "text": "`premises` の「建物・敷地」という意味は、単に「前提が複数ある」ことから生じたのではない。法律文書で先に述べられた事項や、譲渡文書で記載された対象を *premises* と呼んだ歴史を経て、そこに記載された土地・建物そのものを指すようになった。現代ではこの不動産義は複数形 `premises` として定着しているため、語源上のつながりより用法を独立して覚えるほうが実用的である。  "
          }
        ],
        "word_formation": [
          {
            "line": 24,
            "text": "＃語形成"
          },
          {
            "line": 26,
            "text": "・premises：`premise` の通常の複数形。また、複数形の形に固定して「（事業所などの）建物・敷地」を表す。後者でも文法上は複数扱いが基本で、`the premises are ...` のように使う。  "
          },
          {
            "line": 27,
            "text": "・premised：動詞 *premise* の過去形・過去分詞。とくに `be premised on/upon ...`「～を前提としている、～に基づいている」で頻出する。  "
          },
          {
            "line": 28,
            "text": "・premising：動詞 *premise* の現在分詞・動名詞。一般語としての頻度は高くなく、論証や形式的な説明で現れる。  "
          },
          {
            "line": 29,
            "text": "・premiss：主にイギリス英語で見られる異綴り。とくに論理学の「前提命題」で用いられることがあるが、`premise` のほうが広く通用する。  "
          }
        ],
        "sense_structure": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】議論、推論、判断、計画、行動などを進める際に、真である、またはひとまず受け入れるものとして置かれる考え・命題・仮定。その前提自体が実際に正しいことを `premise` という語が保証するわけではなく、`false premise`「誤った前提」のようにも使える。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 115,
            "text": "【日本語訳・定義】映画、小説、ドラマ、ゲーム、企画などを成立させる基本的な状況・設定・中心アイデア。作品によっては主要な筋立て・ストーリーラインの核まで指し、細かな出来事の並びをすべて指す `plot` より「作品を一文程度で要約できる土台」に焦点がある。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 167,
            "text": "【日本語訳・定義】論証・推論において、結論を導くための出発点として置かれる命題。三段論法では `major premise`「大前提」、`minor premise`「小前提」のように呼ぶ。一般語義1と連続しているが、ここでは論証の構成要素としてより厳密に用いる。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 219,
            "text": "【日本語訳・定義】人・会社・組織などが所有・占有・使用する土地、建物、建物の一部、およびそれに付随する敷地。会社・店舗・学校・病院・工場などの場所に特によく使うが、住宅や賃貸物件などにも使える。現代英語ではこの意味を通常 `premises` という複数形で表し、単数 `a premise` を「一つの建物・敷地」の意味では普通使わない。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 283,
            "text": "【日本語訳・定義】理論、議論、計画、判断などを、ある考え・仮定が真または受け入れられるものとして土台にして組み立てる。現代英語では、とくに受動態 `be premised on/upon ...`「～を前提としている、～に基づいている」が重要である。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 338,
            "text": "【日本語訳・定義】議論や推論を始める前に、ある命題・考えを前提として提示したり、真であるものとして仮に置いたりする。語義5の `premise A on B` では A が前提に基づいて組み立てられる対象だが、この語義では目的語・that節の内容そのものが「前提として置かれる内容」になる。  "
          }
        ],
        "frequency_register": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 47,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 49,
            "text": "【レジスター/領域】標準～やや形式的。議論、ビジネス、学術、政策、分析、日常の説明で広く使う。日常会話では `assumption` のほうが軽く自然な場面も多い。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 117,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 119,
            "text": "【レジスター/領域】標準語。映画・小説・テレビ番組・ゲームの紹介や批評、企画説明でよく使う。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 169,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 171,
            "text": "【レジスター/領域】論理学、哲学、批判的思考、議論分析。専門用語として標準的。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 221,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 223,
            "text": "【レジスター/領域】標準～やや形式的。規則、契約、警告表示、警備、保険、不動産、事業運営、住宅・賃貸関係でよく使う。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 285,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 287,
            "text": "【レジスター/領域】形式的。学術、政策、法律、ビジネス分析、評論で使う。日常会話では `base ... on ...` のほうが一般的。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 340,
            "text": "【頻度】〈3/10〉  "
          },
          {
            "line": 342,
            "text": "【レジスター/領域】非常に形式的で低頻度。論証、哲学、古風・硬い説明文で見られる。現代の一般文では `assume`、`posit`、`postulate` などのほうが普通。  "
          }
        ],
        "usage_notes": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 85,
            "text": "【語法・注意】`premise` は「結論を支える土台」に焦点があり、単に未確認の予想を表す `assumption` より論証・判断との結びつきが強い。`on the premise that ...` と `on the assumption that ...` は重なるが、前者は議論・方針の明示的な根拠という響きがやや強い。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 140,
            "text": "【語法・注意】この語義の `premise` と `plot` は重なることがあるが、通常は焦点が異なる。`premise` は物語を生む基本状況・中心アイデア、または主要な筋立ての核を要約するのに向き、`plot` は出来事がどのような順序・因果で展開するかという具体的な筋書きに焦点がある。`concept` はさらに広く、作品以外の発想や概念にも使える。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 197,
            "text": "【語法・注意】論理学では、「前提が真であること」と「推論が妥当であること」を混同しない。妥当な論証は、前提が真なら結論が偽にならない形を持つことを問題にするのであり、`valid premise` を単純に「真の前提」の意味で使うより、`true premise` と `valid argument/inference` を区別するほうが正確である。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 254,
            "text": "【語法・注意】この意味の `premises` は見た目が複数形で、標準的には複数動詞を取る。`These premises are ...`、`the premises have ...` のように考える。単数の建物や物件を指したい場合も、通常は `a premise` ではなく `a building`、`a property`、`a site` などを使う。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 308,
            "text": "【語法・注意】動詞の中心構文は `premise A on/upon B` で、A が「組み立てられる理論・主張・行動」、B が「その土台となる前提」である。方向を逆にしない。受動態では `A is premised on B` となり、学習者にとって最も遭遇しやすい形である。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 363,
            "text": "【語法・注意】この語義は現代英語では低頻度で、学習上は語義5の `be premised on/upon ...` のほうを優先する。`premise that P` では P 自体を前提として置くのに対し、`A is premised on P` では A が P を土台として組み立てられている。項の方向が異なるので混同しない。  "
          }
        ],
        "collocations_examples": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 53,
            "text": "【コロケーション】"
          },
          {
            "line": 55,
            "text": "・`the premise that ...`  "
          },
          {
            "line": 56,
            "text": "用途: 内容を that節で明示して「～という前提」を表す。  "
          },
          {
            "line": 57,
            "text": "例: The proposal rests on the premise that demand will continue to grow.  "
          },
          {
            "line": 58,
            "text": "訳: その提案は、需要が今後も伸び続けるという前提に立っている。  "
          },
          {
            "line": 60,
            "text": "・`on the premise that ...`  "
          },
          {
            "line": 61,
            "text": "用途: 判断・行動を何らかの仮定に基づいて行うことを示す。  "
          },
          {
            "line": 62,
            "text": "例: We planned the schedule on the premise that the parts would arrive by Friday.  "
          },
          {
            "line": 63,
            "text": "訳: 私たちは、部品が金曜日までに届くという前提で日程を組んだ。  "
          },
          {
            "line": 65,
            "text": "・`start from the premise that ...`  "
          },
          {
            "line": 66,
            "text": "用途: 議論や分析の出発点となる考えを示す。  "
          },
          {
            "line": 67,
            "text": "例: The report starts from the premise that access to data should be limited by purpose.  "
          },
          {
            "line": 68,
            "text": "訳: その報告書は、データへのアクセスは目的に応じて制限されるべきだという前提から出発している。  "
          },
          {
            "line": 70,
            "text": "・`an underlying premise`  "
          },
          {
            "line": 71,
            "text": "用途: 明示されていなくても、議論や制度の根底で支えている前提を指す。  "
          },
          {
            "line": 72,
            "text": "例: An underlying premise of the policy is that most users will follow the rules voluntarily.  "
          },
          {
            "line": 73,
            "text": "訳: その方針の根底にある前提の一つは、大半の利用者が自発的に規則を守るということである。  "
          },
          {
            "line": 75,
            "text": "・`a false/flawed premise`  "
          },
          {
            "line": 76,
            "text": "用途: 結論以前に、出発点となる仮定そのものに誤りや欠陥があることを示す。  "
          },
          {
            "line": 77,
            "text": "例: A convincing argument can still fail if it begins with a false premise.  "
          },
          {
            "line": 78,
            "text": "訳: 説得力のある議論でも、誤った前提から始まれば成り立たないことがある。  "
          },
          {
            "line": 80,
            "text": "・`question/challenge the premise`  "
          },
          {
            "line": 81,
            "text": "用途: 相手の結論ではなく、その結論を支える出発点そのものを疑う。  "
          },
          {
            "line": 82,
            "text": "例: Before discussing the cost, we should challenge the premise that the change is necessary.  "
          },
          {
            "line": 83,
            "text": "訳: 費用を議論する前に、その変更が必要だという前提自体を検討し直すべきだ。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 123,
            "text": "【コロケーション】"
          },
          {
            "line": 125,
            "text": "・`the premise of the film/show/book`  "
          },
          {
            "line": 126,
            "text": "用途: 作品の基本設定や中心アイデアを述べる。  "
          },
          {
            "line": 127,
            "text": "例: The premise of the film is simple: nobody in the town can tell a lie.  "
          },
          {
            "line": 128,
            "text": "訳: その映画の基本設定は単純で、町の誰も嘘をつけないというものだ。  "
          },
          {
            "line": 130,
            "text": "・`an intriguing premise`  "
          },
          {
            "line": 131,
            "text": "用途: 読者・視聴者の興味を引く基本設定を評価する。  "
          },
          {
            "line": 132,
            "text": "例: The novel has an intriguing premise, even though the middle chapters move slowly.  "
          },
          {
            "line": 133,
            "text": "訳: 中盤の展開は遅いものの、その小説には興味を引く基本設定がある。  "
          },
          {
            "line": 135,
            "text": "・`build a story around a premise`  "
          },
          {
            "line": 136,
            "text": "用途: 一つの中心設定を核として物語を展開する。  "
          },
          {
            "line": 137,
            "text": "例: The writers built the series around the premise that memories could be traded.  "
          },
          {
            "line": 138,
            "text": "訳: 脚本家たちは、記憶を売買できるという設定を中心にシリーズを構成した。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 175,
            "text": "【コロケーション】"
          },
          {
            "line": 177,
            "text": "・`major premise`  "
          },
          {
            "line": 178,
            "text": "用途: 伝統的なカテゴリー三段論法で、結論の述語となる major term（大項）を含む前提を指す。「より一般的な内容だから大前提」と定義されるわけではない。  "
          },
          {
            "line": 179,
            "text": "例: In “All metals conduct electricity; copper is a metal; therefore copper conducts electricity,” the first statement is the major premise because it contains the predicate term of the conclusion.  "
          },
          {
            "line": 180,
            "text": "訳: 「すべての金属は電気を通す。銅は金属である。したがって銅は電気を通す」という三段論法では、最初の命題が結論の述語となる大項を含むため大前提である。  "
          },
          {
            "line": 182,
            "text": "・`minor premise`  "
          },
          {
            "line": 183,
            "text": "用途: 伝統的なカテゴリー三段論法で、結論の主語となる minor term（小項）を含む前提を指す。「個別的な内容だから小前提」と定義されるわけではない。  "
          },
          {
            "line": 184,
            "text": "例: In the same syllogism, “Copper is a metal” is the minor premise because it contains the subject term of the conclusion.  "
          },
          {
            "line": 185,
            "text": "訳: 同じ三段論法では、「銅は金属である」が結論の主語となる小項を含むため小前提である。  "
          },
          {
            "line": 187,
            "text": "・`premises and conclusion`  "
          },
          {
            "line": 188,
            "text": "用途: 論証を、根拠として置かれる命題群と、そこから導かれる結論に分けて捉える。  "
          },
          {
            "line": 189,
            "text": "例: To evaluate the argument, separate its premises from its conclusion.  "
          },
          {
            "line": 190,
            "text": "訳: その論証を評価するには、前提群と結論を分けて考えなさい。  "
          },
          {
            "line": 192,
            "text": "・`infer a conclusion from the premises`  "
          },
          {
            "line": 193,
            "text": "用途: 与えられた前提から推論によって結論を導く。  "
          },
          {
            "line": 194,
            "text": "例: The conclusion cannot be inferred from the premises without an additional assumption.  "
          },
          {
            "line": 195,
            "text": "訳: 追加の仮定がなければ、その前提群からその結論を導くことはできない。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 227,
            "text": "【コロケーション】"
          },
          {
            "line": 229,
            "text": "・`on the premises`  "
          },
          {
            "line": 230,
            "text": "用途: 建物・敷地の内側で行われることを表す。`premises` に所有格を付けず、特定の構内なら `the` を使うことが多い。  "
          },
          {
            "line": 231,
            "text": "例: Smoking is not permitted anywhere on the premises.  "
          },
          {
            "line": 232,
            "text": "訳: この敷地内では、どこであっても喫煙は認められていない。  "
          },
          {
            "line": 234,
            "text": "・`off the premises`  "
          },
          {
            "line": 235,
            "text": "用途: 建物・敷地の外へ出た場所、または外で行うことを表す。  "
          },
          {
            "line": 236,
            "text": "例: Confidential documents must not be taken off the premises without permission.  "
          },
          {
            "line": 237,
            "text": "訳: 機密文書を許可なく構外へ持ち出してはならない。  "
          },
          {
            "line": 239,
            "text": "・`leave/vacate the premises`  "
          },
          {
            "line": 240,
            "text": "用途: 人が構内を離れる、または占有者が建物・敷地から退去することを表す。`vacate` はより形式的。  "
          },
          {
            "line": 241,
            "text": "例: Visitors must leave the premises by 9 p.m.  "
          },
          {
            "line": 242,
            "text": "訳: 来訪者は午後9時までに構内から退出しなければならない。  "
          },
          {
            "line": 244,
            "text": "・`business/commercial premises`  "
          },
          {
            "line": 245,
            "text": "用途: 事業に使用される建物・敷地をまとめて表す。  "
          },
          {
            "line": 246,
            "text": "例: The company moved to larger business premises near the station.  "
          },
          {
            "line": 247,
            "text": "訳: その会社は駅の近くの、より広い事業用施設へ移転した。  "
          },
          {
            "line": 249,
            "text": "・`the premises are ...`  "
          },
          {
            "line": 250,
            "text": "用途: `premises` を複数扱いして状態を述べる。  "
          },
          {
            "line": 251,
            "text": "例: The premises are protected by security cameras at all times.  "
          },
          {
            "line": 252,
            "text": "訳: その施設は常時、防犯カメラで監視されている。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 291,
            "text": "【コロケーション】"
          },
          {
            "line": 293,
            "text": "・`be premised on the assumption that ...`  "
          },
          {
            "line": 294,
            "text": "用途: 理論・計画などの根底にある仮定を明示する。  "
          },
          {
            "line": 295,
            "text": "例: The forecast is premised on the assumption that interest rates will remain unchanged.  "
          },
          {
            "line": 296,
            "text": "訳: その予測は、金利が据え置かれるという仮定を前提にしている。  "
          },
          {
            "line": 298,
            "text": "・`be premised on the idea that ...`  "
          },
          {
            "line": 299,
            "text": "用途: 制度・主張などが、ある考えを出発点として構成されていることを表す。  "
          },
          {
            "line": 300,
            "text": "例: The program is premised on the idea that early support can prevent larger problems later.  "
          },
          {
            "line": 301,
            "text": "訳: そのプログラムは、早期支援によって後の大きな問題を防げるという考えに基づいている。  "
          },
          {
            "line": 303,
            "text": "・`premise an argument on/upon ...`  "
          },
          {
            "line": 304,
            "text": "用途: 議論を特定の前提に基づかせる。能動態は受動態より形式的で、頻度も低い。  "
          },
          {
            "line": 305,
            "text": "例: The author premises the argument on a distinction between legal ownership and practical control.  "
          },
          {
            "line": 306,
            "text": "訳: 著者は、法的所有と実質的支配の区別を前提としてその議論を組み立てている。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 346,
            "text": "【コロケーション】"
          },
          {
            "line": 348,
            "text": "・`premise that ...`  "
          },
          {
            "line": 349,
            "text": "用途: 後続の議論のため、that節の内容そのものを前提として置く。  "
          },
          {
            "line": 350,
            "text": "例: The author premises that each participant has access to the same information.  "
          },
          {
            "line": 351,
            "text": "訳: 著者は、各参加者が同じ情報にアクセスできることを前提として置いている。  "
          },
          {
            "line": 353,
            "text": "・`let us premise that ...`  "
          },
          {
            "line": 354,
            "text": "用途: 論証の冒頭で、検討のための前提を明示的に設定する。現代ではかなり硬い。  "
          },
          {
            "line": 355,
            "text": "例: Let us premise that the two measurements were taken under identical conditions.  "
          },
          {
            "line": 356,
            "text": "訳: 2回の測定は同一条件で行われたと前提としておこう。  "
          },
          {
            "line": 358,
            "text": "・`premise a proposition`  "
          },
          {
            "line": 359,
            "text": "用途: 命題そのものを、後の推論に先立つ前提として提示する。  "
          },
          {
            "line": 360,
            "text": "例: The author premises a proposition about human motivation before turning to the main argument.  "
          },
          {
            "line": 361,
            "text": "訳: 著者は本論に入る前に、人間の動機に関する命題を前提として提示している。  "
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
      "input_body_sha256": "1853b935aa8af00051a2dc94003c0f331997f6110d9b6181471417254083d528",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "名詞は米・英: /ˈpremɪs/。2音節の PREM-iss で、第1音節に主強勢がある。語末の `-ise` を /aɪz/ と読む語ではなく、名詞では /ɪs/ で終わる。  "
          },
          {
            "line": 16,
            "text": "動詞は米・英で /prɪˈmaɪz/ と /ˈpremɪs/ の両方が辞書に載る。/prɪˈmaɪz/ では第2音節に強勢があり、語末は /aɪz/、/ˈpremɪs/ では名詞と同じ発音になる。とくに `be premised on/upon ...` を聞くときは、話者によってこの二つがあり得る。  "
          },
          {
            "line": 17,
            "text": "複数形 premises は /ˈpremɪsɪz/。建物・敷地を表す `premises` も同じ発音で、綴りは複数形と同一である。動詞の過去形・過去分詞 premised、-ing形 premising は、採用する動詞発音に応じて発音も変わる。  "
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
      "input_body_sha256": "1853b935aa8af00051a2dc94003c0f331997f6110d9b6181471417254083d528",
      "input_sections": {
        "pronunciation": [
          {
            "line": 13,
            "text": "＃発音記号"
          },
          {
            "line": 15,
            "text": "名詞は米・英: /ˈpremɪs/。2音節の PREM-iss で、第1音節に主強勢がある。語末の `-ise` を /aɪz/ と読む語ではなく、名詞では /ɪs/ で終わる。  "
          },
          {
            "line": 16,
            "text": "動詞は米・英で /prɪˈmaɪz/ と /ˈpremɪs/ の両方が辞書に載る。/prɪˈmaɪz/ では第2音節に強勢があり、語末は /aɪz/、/ˈpremɪs/ では名詞と同じ発音になる。とくに `be premised on/upon ...` を聞くときは、話者によってこの二つがあり得る。  "
          },
          {
            "line": 17,
            "text": "複数形 premises は /ˈpremɪsɪz/。建物・敷地を表す `premises` も同じ発音で、綴りは複数形と同一である。動詞の過去形・過去分詞 premised、-ing形 premising は、採用する動詞発音に応じて発音も変わる。  "
          }
        ],
        "etymology": [
          {
            "line": 19,
            "text": "＃語源"
          },
          {
            "line": 21,
            "text": "中英語の *premise* は、古フランス語を経て中世ラテン語 *praemissa (propositio)*「前に置かれた命題」にさかのぼる。*praemissa* はラテン語 *praemittere*「前に送る、先に述べる」に由来し、*prae-*「前に」＋ *mittere*「送る」から成る。論証で結論より先に置かれる命題という発想が、現在の「推論・議論の前提」につながった。  "
          },
          {
            "line": 22,
            "text": "`premises` の「建物・敷地」という意味は、単に「前提が複数ある」ことから生じたのではない。法律文書で先に述べられた事項や、譲渡文書で記載された対象を *premises* と呼んだ歴史を経て、そこに記載された土地・建物そのものを指すようになった。現代ではこの不動産義は複数形 `premises` として定着しているため、語源上のつながりより用法を独立して覚えるほうが実用的である。  "
          }
        ],
        "word_formation": [
          {
            "line": 24,
            "text": "＃語形成"
          },
          {
            "line": 26,
            "text": "・premises：`premise` の通常の複数形。また、複数形の形に固定して「（事業所などの）建物・敷地」を表す。後者でも文法上は複数扱いが基本で、`the premises are ...` のように使う。  "
          },
          {
            "line": 27,
            "text": "・premised：動詞 *premise* の過去形・過去分詞。とくに `be premised on/upon ...`「～を前提としている、～に基づいている」で頻出する。  "
          },
          {
            "line": 28,
            "text": "・premising：動詞 *premise* の現在分詞・動名詞。一般語としての頻度は高くなく、論証や形式的な説明で現れる。  "
          },
          {
            "line": 29,
            "text": "・premiss：主にイギリス英語で見られる異綴り。とくに論理学の「前提命題」で用いられることがあるが、`premise` のほうが広く通用する。  "
          }
        ],
        "core_image": [
          {
            "line": 31,
            "text": "＃コアイメージ"
          },
          {
            "line": 33,
            "text": "`premise` の中心は、「後に続く結論・判断・構成を支えるものを、先に置いて土台にする」である。議論では命題を先に置き、判断では仮定を土台にし、作品では物語を成立させる基本設定を置く。動詞では、その土台の上に理論や主張を組み立てることを表す。  "
          },
          {
            "line": 34,
            "text": "・議論・判断の土台として置く考え → 「前提、仮定」（語義1）  "
          },
          {
            "line": 35,
            "text": "・作品を成立させる土台の設定・筋立ての核 → 「基本設定、中心的な着想」（語義2）  "
          },
          {
            "line": 36,
            "text": "・論理学で結論を導くために置く命題 → 「前提命題」（語義3）  "
          },
          {
            "line": 37,
            "text": "・理論・主張などをある考えの上に置く → 「～を…に基づかせる」（語義5）  "
          },
          {
            "line": 38,
            "text": "・命題や考え自体を前提として先に置く → 「～を前提として述べる・仮定する」（語義6）  "
          },
          {
            "line": 39,
            "text": "`premises`「建物・敷地」（語義4）は歴史的には同じ語から発達したが、現代話者にとって上のコアイメージから直接推測しにくい定着義なので、別に覚える。  "
          }
        ],
        "sense_structure": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 45,
            "text": "【日本語訳・定義】議論、推論、判断、計画、行動などを進める際に、真である、またはひとまず受け入れるものとして置かれる考え・命題・仮定。その前提自体が実際に正しいことを `premise` という語が保証するわけではなく、`false premise`「誤った前提」のようにも使える。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 115,
            "text": "【日本語訳・定義】映画、小説、ドラマ、ゲーム、企画などを成立させる基本的な状況・設定・中心アイデア。作品によっては主要な筋立て・ストーリーラインの核まで指し、細かな出来事の並びをすべて指す `plot` より「作品を一文程度で要約できる土台」に焦点がある。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 167,
            "text": "【日本語訳・定義】論証・推論において、結論を導くための出発点として置かれる命題。三段論法では `major premise`「大前提」、`minor premise`「小前提」のように呼ぶ。一般語義1と連続しているが、ここでは論証の構成要素としてより厳密に用いる。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 219,
            "text": "【日本語訳・定義】人・会社・組織などが所有・占有・使用する土地、建物、建物の一部、およびそれに付随する敷地。会社・店舗・学校・病院・工場などの場所に特によく使うが、住宅や賃貸物件などにも使える。現代英語ではこの意味を通常 `premises` という複数形で表し、単数 `a premise` を「一つの建物・敷地」の意味では普通使わない。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 283,
            "text": "【日本語訳・定義】理論、議論、計画、判断などを、ある考え・仮定が真または受け入れられるものとして土台にして組み立てる。現代英語では、とくに受動態 `be premised on/upon ...`「～を前提としている、～に基づいている」が重要である。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 338,
            "text": "【日本語訳・定義】議論や推論を始める前に、ある命題・考えを前提として提示したり、真であるものとして仮に置いたりする。語義5の `premise A on B` では A が前提に基づいて組み立てられる対象だが、この語義では目的語・that節の内容そのものが「前提として置かれる内容」になる。  "
          }
        ],
        "frequency_register": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 47,
            "text": "【頻度】〈9/10〉  "
          },
          {
            "line": 49,
            "text": "【レジスター/領域】標準～やや形式的。議論、ビジネス、学術、政策、分析、日常の説明で広く使う。日常会話では `assumption` のほうが軽く自然な場面も多い。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 117,
            "text": "【頻度】〈7/10〉  "
          },
          {
            "line": 119,
            "text": "【レジスター/領域】標準語。映画・小説・テレビ番組・ゲームの紹介や批評、企画説明でよく使う。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 169,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 171,
            "text": "【レジスター/領域】論理学、哲学、批判的思考、議論分析。専門用語として標準的。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 221,
            "text": "【頻度】〈8/10〉  "
          },
          {
            "line": 223,
            "text": "【レジスター/領域】標準～やや形式的。規則、契約、警告表示、警備、保険、不動産、事業運営、住宅・賃貸関係でよく使う。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 285,
            "text": "【頻度】〈6/10〉  "
          },
          {
            "line": 287,
            "text": "【レジスター/領域】形式的。学術、政策、法律、ビジネス分析、評論で使う。日常会話では `base ... on ...` のほうが一般的。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 340,
            "text": "【頻度】〈3/10〉  "
          },
          {
            "line": 342,
            "text": "【レジスター/領域】非常に形式的で低頻度。論証、哲学、古風・硬い説明文で見られる。現代の一般文では `assume`、`posit`、`postulate` などのほうが普通。  "
          }
        ],
        "frames": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 51,
            "text": "【文法パターン】`the premise that ...`＝～という前提／`on the premise that ...`＝～という前提で／`start/work/proceed from the premise that ...`＝～を前提として始める・進める／`base 〈議論・計画〉 on the premise that ...`＝議論・計画を～という前提に置く／`question/challenge/reject a premise`＝前提を疑う・異議を唱える・退ける／`a false/flawed/basic/underlying premise`＝誤った・欠陥のある・基本的な・根底の前提  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 121,
            "text": "【文法パターン】`the premise of 〈作品・企画〉`＝作品・企画の基本設定／`a simple/interesting/intriguing premise`＝単純な・興味深い・魅力的な設定／`the premise is that ...`＝基本設定は～である／`build a story around a premise`＝ある設定を中心に物語を作る  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 173,
            "text": "【文法パターン】`a premise of an argument`＝論証の前提命題／`major/minor premise`＝大前提・小前提／`premises and conclusion`＝前提群と結論／`derive/infer a conclusion from premises`＝前提から結論を導く／`the premises are true`＝前提群が真である  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 225,
            "text": "【文法パターン】`on the premises`＝その構内・敷地内で／`off the premises`＝構外・敷地外で／`enter/leave/vacate the premises`＝構内に入る・出る・退去する／`business/commercial/industrial premises`＝事業用・商業用・工業用施設／`the premises are ...`＝その建物・敷地は～である  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 289,
            "text": "【文法パターン】`premise 〈理論・主張・計画〉 on/upon 〈考え・仮定〉`＝理論などを考え・仮定に基づかせる／`〈理論・主張・計画〉 be premised on/upon 〈考え・仮定〉`＝理論などが考え・仮定を前提としている  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 344,
            "text": "【文法パターン】`premise that ...`＝～だと前提として述べる・仮定する／`premise 〈命題・考え〉`＝命題・考えを前提として置く／`let us premise that ...`＝～だと前提としておこう  "
          }
        ],
        "collocations_examples": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 53,
            "text": "【コロケーション】"
          },
          {
            "line": 55,
            "text": "・`the premise that ...`  "
          },
          {
            "line": 56,
            "text": "用途: 内容を that節で明示して「～という前提」を表す。  "
          },
          {
            "line": 57,
            "text": "例: The proposal rests on the premise that demand will continue to grow.  "
          },
          {
            "line": 58,
            "text": "訳: その提案は、需要が今後も伸び続けるという前提に立っている。  "
          },
          {
            "line": 60,
            "text": "・`on the premise that ...`  "
          },
          {
            "line": 61,
            "text": "用途: 判断・行動を何らかの仮定に基づいて行うことを示す。  "
          },
          {
            "line": 62,
            "text": "例: We planned the schedule on the premise that the parts would arrive by Friday.  "
          },
          {
            "line": 63,
            "text": "訳: 私たちは、部品が金曜日までに届くという前提で日程を組んだ。  "
          },
          {
            "line": 65,
            "text": "・`start from the premise that ...`  "
          },
          {
            "line": 66,
            "text": "用途: 議論や分析の出発点となる考えを示す。  "
          },
          {
            "line": 67,
            "text": "例: The report starts from the premise that access to data should be limited by purpose.  "
          },
          {
            "line": 68,
            "text": "訳: その報告書は、データへのアクセスは目的に応じて制限されるべきだという前提から出発している。  "
          },
          {
            "line": 70,
            "text": "・`an underlying premise`  "
          },
          {
            "line": 71,
            "text": "用途: 明示されていなくても、議論や制度の根底で支えている前提を指す。  "
          },
          {
            "line": 72,
            "text": "例: An underlying premise of the policy is that most users will follow the rules voluntarily.  "
          },
          {
            "line": 73,
            "text": "訳: その方針の根底にある前提の一つは、大半の利用者が自発的に規則を守るということである。  "
          },
          {
            "line": 75,
            "text": "・`a false/flawed premise`  "
          },
          {
            "line": 76,
            "text": "用途: 結論以前に、出発点となる仮定そのものに誤りや欠陥があることを示す。  "
          },
          {
            "line": 77,
            "text": "例: A convincing argument can still fail if it begins with a false premise.  "
          },
          {
            "line": 78,
            "text": "訳: 説得力のある議論でも、誤った前提から始まれば成り立たないことがある。  "
          },
          {
            "line": 80,
            "text": "・`question/challenge the premise`  "
          },
          {
            "line": 81,
            "text": "用途: 相手の結論ではなく、その結論を支える出発点そのものを疑う。  "
          },
          {
            "line": 82,
            "text": "例: Before discussing the cost, we should challenge the premise that the change is necessary.  "
          },
          {
            "line": 83,
            "text": "訳: 費用を議論する前に、その変更が必要だという前提自体を検討し直すべきだ。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 123,
            "text": "【コロケーション】"
          },
          {
            "line": 125,
            "text": "・`the premise of the film/show/book`  "
          },
          {
            "line": 126,
            "text": "用途: 作品の基本設定や中心アイデアを述べる。  "
          },
          {
            "line": 127,
            "text": "例: The premise of the film is simple: nobody in the town can tell a lie.  "
          },
          {
            "line": 128,
            "text": "訳: その映画の基本設定は単純で、町の誰も嘘をつけないというものだ。  "
          },
          {
            "line": 130,
            "text": "・`an intriguing premise`  "
          },
          {
            "line": 131,
            "text": "用途: 読者・視聴者の興味を引く基本設定を評価する。  "
          },
          {
            "line": 132,
            "text": "例: The novel has an intriguing premise, even though the middle chapters move slowly.  "
          },
          {
            "line": 133,
            "text": "訳: 中盤の展開は遅いものの、その小説には興味を引く基本設定がある。  "
          },
          {
            "line": 135,
            "text": "・`build a story around a premise`  "
          },
          {
            "line": 136,
            "text": "用途: 一つの中心設定を核として物語を展開する。  "
          },
          {
            "line": 137,
            "text": "例: The writers built the series around the premise that memories could be traded.  "
          },
          {
            "line": 138,
            "text": "訳: 脚本家たちは、記憶を売買できるという設定を中心にシリーズを構成した。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 175,
            "text": "【コロケーション】"
          },
          {
            "line": 177,
            "text": "・`major premise`  "
          },
          {
            "line": 178,
            "text": "用途: 伝統的なカテゴリー三段論法で、結論の述語となる major term（大項）を含む前提を指す。「より一般的な内容だから大前提」と定義されるわけではない。  "
          },
          {
            "line": 179,
            "text": "例: In “All metals conduct electricity; copper is a metal; therefore copper conducts electricity,” the first statement is the major premise because it contains the predicate term of the conclusion.  "
          },
          {
            "line": 180,
            "text": "訳: 「すべての金属は電気を通す。銅は金属である。したがって銅は電気を通す」という三段論法では、最初の命題が結論の述語となる大項を含むため大前提である。  "
          },
          {
            "line": 182,
            "text": "・`minor premise`  "
          },
          {
            "line": 183,
            "text": "用途: 伝統的なカテゴリー三段論法で、結論の主語となる minor term（小項）を含む前提を指す。「個別的な内容だから小前提」と定義されるわけではない。  "
          },
          {
            "line": 184,
            "text": "例: In the same syllogism, “Copper is a metal” is the minor premise because it contains the subject term of the conclusion.  "
          },
          {
            "line": 185,
            "text": "訳: 同じ三段論法では、「銅は金属である」が結論の主語となる小項を含むため小前提である。  "
          },
          {
            "line": 187,
            "text": "・`premises and conclusion`  "
          },
          {
            "line": 188,
            "text": "用途: 論証を、根拠として置かれる命題群と、そこから導かれる結論に分けて捉える。  "
          },
          {
            "line": 189,
            "text": "例: To evaluate the argument, separate its premises from its conclusion.  "
          },
          {
            "line": 190,
            "text": "訳: その論証を評価するには、前提群と結論を分けて考えなさい。  "
          },
          {
            "line": 192,
            "text": "・`infer a conclusion from the premises`  "
          },
          {
            "line": 193,
            "text": "用途: 与えられた前提から推論によって結論を導く。  "
          },
          {
            "line": 194,
            "text": "例: The conclusion cannot be inferred from the premises without an additional assumption.  "
          },
          {
            "line": 195,
            "text": "訳: 追加の仮定がなければ、その前提群からその結論を導くことはできない。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 227,
            "text": "【コロケーション】"
          },
          {
            "line": 229,
            "text": "・`on the premises`  "
          },
          {
            "line": 230,
            "text": "用途: 建物・敷地の内側で行われることを表す。`premises` に所有格を付けず、特定の構内なら `the` を使うことが多い。  "
          },
          {
            "line": 231,
            "text": "例: Smoking is not permitted anywhere on the premises.  "
          },
          {
            "line": 232,
            "text": "訳: この敷地内では、どこであっても喫煙は認められていない。  "
          },
          {
            "line": 234,
            "text": "・`off the premises`  "
          },
          {
            "line": 235,
            "text": "用途: 建物・敷地の外へ出た場所、または外で行うことを表す。  "
          },
          {
            "line": 236,
            "text": "例: Confidential documents must not be taken off the premises without permission.  "
          },
          {
            "line": 237,
            "text": "訳: 機密文書を許可なく構外へ持ち出してはならない。  "
          },
          {
            "line": 239,
            "text": "・`leave/vacate the premises`  "
          },
          {
            "line": 240,
            "text": "用途: 人が構内を離れる、または占有者が建物・敷地から退去することを表す。`vacate` はより形式的。  "
          },
          {
            "line": 241,
            "text": "例: Visitors must leave the premises by 9 p.m.  "
          },
          {
            "line": 242,
            "text": "訳: 来訪者は午後9時までに構内から退出しなければならない。  "
          },
          {
            "line": 244,
            "text": "・`business/commercial premises`  "
          },
          {
            "line": 245,
            "text": "用途: 事業に使用される建物・敷地をまとめて表す。  "
          },
          {
            "line": 246,
            "text": "例: The company moved to larger business premises near the station.  "
          },
          {
            "line": 247,
            "text": "訳: その会社は駅の近くの、より広い事業用施設へ移転した。  "
          },
          {
            "line": 249,
            "text": "・`the premises are ...`  "
          },
          {
            "line": 250,
            "text": "用途: `premises` を複数扱いして状態を述べる。  "
          },
          {
            "line": 251,
            "text": "例: The premises are protected by security cameras at all times.  "
          },
          {
            "line": 252,
            "text": "訳: その施設は常時、防犯カメラで監視されている。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 291,
            "text": "【コロケーション】"
          },
          {
            "line": 293,
            "text": "・`be premised on the assumption that ...`  "
          },
          {
            "line": 294,
            "text": "用途: 理論・計画などの根底にある仮定を明示する。  "
          },
          {
            "line": 295,
            "text": "例: The forecast is premised on the assumption that interest rates will remain unchanged.  "
          },
          {
            "line": 296,
            "text": "訳: その予測は、金利が据え置かれるという仮定を前提にしている。  "
          },
          {
            "line": 298,
            "text": "・`be premised on the idea that ...`  "
          },
          {
            "line": 299,
            "text": "用途: 制度・主張などが、ある考えを出発点として構成されていることを表す。  "
          },
          {
            "line": 300,
            "text": "例: The program is premised on the idea that early support can prevent larger problems later.  "
          },
          {
            "line": 301,
            "text": "訳: そのプログラムは、早期支援によって後の大きな問題を防げるという考えに基づいている。  "
          },
          {
            "line": 303,
            "text": "・`premise an argument on/upon ...`  "
          },
          {
            "line": 304,
            "text": "用途: 議論を特定の前提に基づかせる。能動態は受動態より形式的で、頻度も低い。  "
          },
          {
            "line": 305,
            "text": "例: The author premises the argument on a distinction between legal ownership and practical control.  "
          },
          {
            "line": 306,
            "text": "訳: 著者は、法的所有と実質的支配の区別を前提としてその議論を組み立てている。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 346,
            "text": "【コロケーション】"
          },
          {
            "line": 348,
            "text": "・`premise that ...`  "
          },
          {
            "line": 349,
            "text": "用途: 後続の議論のため、that節の内容そのものを前提として置く。  "
          },
          {
            "line": 350,
            "text": "例: The author premises that each participant has access to the same information.  "
          },
          {
            "line": 351,
            "text": "訳: 著者は、各参加者が同じ情報にアクセスできることを前提として置いている。  "
          },
          {
            "line": 353,
            "text": "・`let us premise that ...`  "
          },
          {
            "line": 354,
            "text": "用途: 論証の冒頭で、検討のための前提を明示的に設定する。現代ではかなり硬い。  "
          },
          {
            "line": 355,
            "text": "例: Let us premise that the two measurements were taken under identical conditions.  "
          },
          {
            "line": 356,
            "text": "訳: 2回の測定は同一条件で行われたと前提としておこう。  "
          },
          {
            "line": 358,
            "text": "・`premise a proposition`  "
          },
          {
            "line": 359,
            "text": "用途: 命題そのものを、後の推論に先立つ前提として提示する。  "
          },
          {
            "line": 360,
            "text": "例: The author premises a proposition about human motivation before turning to the main argument.  "
          },
          {
            "line": 361,
            "text": "訳: 著者は本論に入る前に、人間の動機に関する命題を前提として提示している。  "
          }
        ],
        "usage_notes": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 85,
            "text": "【語法・注意】`premise` は「結論を支える土台」に焦点があり、単に未確認の予想を表す `assumption` より論証・判断との結びつきが強い。`on the premise that ...` と `on the assumption that ...` は重なるが、前者は議論・方針の明示的な根拠という響きがやや強い。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 140,
            "text": "【語法・注意】この語義の `premise` と `plot` は重なることがあるが、通常は焦点が異なる。`premise` は物語を生む基本状況・中心アイデア、または主要な筋立ての核を要約するのに向き、`plot` は出来事がどのような順序・因果で展開するかという具体的な筋書きに焦点がある。`concept` はさらに広く、作品以外の発想や概念にも使える。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 197,
            "text": "【語法・注意】論理学では、「前提が真であること」と「推論が妥当であること」を混同しない。妥当な論証は、前提が真なら結論が偽にならない形を持つことを問題にするのであり、`valid premise` を単純に「真の前提」の意味で使うより、`true premise` と `valid argument/inference` を区別するほうが正確である。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 254,
            "text": "【語法・注意】この意味の `premises` は見た目が複数形で、標準的には複数動詞を取る。`These premises are ...`、`the premises have ...` のように考える。単数の建物や物件を指したい場合も、通常は `a premise` ではなく `a building`、`a property`、`a site` などを使う。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 308,
            "text": "【語法・注意】動詞の中心構文は `premise A on/upon B` で、A が「組み立てられる理論・主張・行動」、B が「その土台となる前提」である。方向を逆にしない。受動態では `A is premised on B` となり、学習者にとって最も遭遇しやすい形である。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 363,
            "text": "【語法・注意】この語義は現代英語では低頻度で、学習上は語義5の `be premised on/upon ...` のほうを優先する。`premise that P` では P 自体を前提として置くのに対し、`A is premised on P` では A が P を土台として組み立てられている。項の方向が異なるので混同しない。  "
          }
        ],
        "lexical_relations": [
          {
            "line": 43,
            "text": "1. 【名詞・可算】前提、仮定、議論・判断の出発点"
          },
          {
            "line": 90,
            "text": "【類義語】"
          },
          {
            "line": 92,
            "text": "・assumption  "
          },
          {
            "line": 93,
            "text": "定義: 証明・確認されていないが、ひとまず真として受け入れる考え。  "
          },
          {
            "line": 94,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 95,
            "text": "違い: `assumption` は日常的な思い込みや計画上の仮定にも広く使える。`premise` は、その考えを土台に議論・推論・判断を組み立てる関係をより強く示す。  "
          },
          {
            "line": 96,
            "text": "例: Our cost estimate is based on the assumption that fuel prices will remain stable.  "
          },
          {
            "line": 97,
            "text": "訳: 私たちの費用見積もりは、燃料価格が安定したままだという仮定に基づいている。  "
          },
          {
            "line": 99,
            "text": "・presupposition  "
          },
          {
            "line": 100,
            "text": "定義: 発言・理論・考えの背後ですでに成り立つものとして想定されている前提。  "
          },
          {
            "line": 101,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 102,
            "text": "違い: `premise` が明示的な論証の土台にも使えるのに対し、`presupposition` は暗黙に先取りされている前提という含みが強く、言語学・哲学でも使われる。  "
          },
          {
            "line": 103,
            "text": "例: The question contains the presupposition that someone made the decision deliberately.  "
          },
          {
            "line": 104,
            "text": "訳: その質問には、誰かが意図的にその決定をしたという前提が含まれている。  "
          },
          {
            "line": 106,
            "text": "・basis  "
          },
          {
            "line": 107,
            "text": "定義: 判断・主張・制度などを支える根拠・基礎。  "
          },
          {
            "line": 108,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 109,
            "text": "違い: `basis` は事実、証拠、原則、計算方法など幅広い「基礎」を表せる。`premise` は特に、真として置く考え・命題を指す。  "
          },
          {
            "line": 110,
            "text": "例: There is no factual basis for the claim.  "
          },
          {
            "line": 111,
            "text": "訳: その主張には事実上の根拠がない。  "
          },
          {
            "line": 113,
            "text": "2. 【名詞・可算】（物語・映画・企画などの）基本設定、中心的な着想"
          },
          {
            "line": 142,
            "text": "【類義語】"
          },
          {
            "line": 144,
            "text": "・concept  "
          },
          {
            "line": 145,
            "text": "定義: 作品・企画・製品などの中心となる発想・概念。  "
          },
          {
            "line": 146,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 147,
            "text": "違い: `concept` は視覚的・商品的・抽象的なアイデアにも広く使える。`premise` は「この条件・状況を出発点にすると何が起こるか」という物語的な設定に向きやすい。  "
          },
          {
            "line": 148,
            "text": "例: The design concept combines a library with a community workspace.  "
          },
          {
            "line": 149,
            "text": "訳: その設計コンセプトは、図書館と地域の共同作業空間を組み合わせている。  "
          },
          {
            "line": 151,
            "text": "・setup  "
          },
          {
            "line": 152,
            "text": "定義: 物語の冒頭で人物・状況・対立関係を整える設定・導入。  "
          },
          {
            "line": 153,
            "text": "頻度: 〈8/10〉  "
          },
          {
            "line": 154,
            "text": "違い: `setup` は物語が動き出すための具体的な初期配置に焦点がある。`premise` は作品全体を支える中心アイデアまで含み得る。  "
          },
          {
            "line": 155,
            "text": "例: The opening scene establishes the setup for the mystery.  "
          },
          {
            "line": 156,
            "text": "訳: 冒頭の場面で、そのミステリーの初期設定が示される。  "
          },
          {
            "line": 158,
            "text": "・plot  "
          },
          {
            "line": 159,
            "text": "定義: 物語で起きる出来事の筋、展開。  "
          },
          {
            "line": 160,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 161,
            "text": "違い: `plot` は出来事の連鎖そのもの。`premise` はその連鎖を生み出す基本条件・着想である。  "
          },
          {
            "line": 162,
            "text": "例: The plot becomes more complicated after the second episode.  "
          },
          {
            "line": 163,
            "text": "訳: 物語の筋は第2話以降さらに複雑になる。  "
          },
          {
            "line": 165,
            "text": "3. 【名詞・可算・論理学】前提命題、推論の前提"
          },
          {
            "line": 201,
            "text": "【類義語】"
          },
          {
            "line": 203,
            "text": "・proposition  "
          },
          {
            "line": 204,
            "text": "定義: 真か偽かを問いうる内容を持つ命題。  "
          },
          {
            "line": 205,
            "text": "頻度: 〈6/10〉  "
          },
          {
            "line": 206,
            "text": "違い: `proposition` は命題そのものの種類を表し、結論にもなり得る。`premise` は論証の中で、その命題が結論を支える役割に置かれていることを表す。  "
          },
          {
            "line": 207,
            "text": "例: The proposition is false, but it can still be used to illustrate the form of the argument.  "
          },
          {
            "line": 208,
            "text": "訳: その命題は偽だが、論証の形式を示すためには使える。  "
          },
          {
            "line": 210,
            "text": "・assumption  "
          },
          {
            "line": 211,
            "text": "定義: 推論のために真として置く仮定。  "
          },
          {
            "line": 212,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 213,
            "text": "違い: `assumption` は明示されない補助的な仮定にも使える。`premise` は論証の構成要素として提示された命題を指しやすい。  "
          },
          {
            "line": 214,
            "text": "例: The proof depends on an unstated assumption about continuity.  "
          },
          {
            "line": 215,
            "text": "訳: その証明は、連続性についての明示されていない仮定に依存している。  "
          },
          {
            "line": 217,
            "text": "4. 【名詞・複数形】建物・敷地、構内（特に事業所・施設など）"
          },
          {
            "line": 258,
            "text": "【類義語】"
          },
          {
            "line": 260,
            "text": "・property  "
          },
          {
            "line": 261,
            "text": "定義: 所有される土地・建物、不動産。  "
          },
          {
            "line": 262,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 263,
            "text": "違い: `property` は所有物・不動産としての法的・経済的な対象に焦点があり、個人住宅にも広く使える。`premises` は所有者が誰かより、その場所が占有・使用される物理的な建物・敷地として捉えられることが多い。  "
          },
          {
            "line": 264,
            "text": "例: The company owns several properties in the city.  "
          },
          {
            "line": 265,
            "text": "訳: その会社は市内に複数の不動産を所有している。  "
          },
          {
            "line": 267,
            "text": "・site  "
          },
          {
            "line": 268,
            "text": "定義: 建物・活動・工事などが置かれている、または行われる場所・敷地。  "
          },
          {
            "line": 269,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 270,
            "text": "違い: `site` は場所そのものに焦点があり、建物がまだない土地にも使える。`premises` は既に占有・使用されている建物・敷地をまとめて指しやすい。  "
          },
          {
            "line": 271,
            "text": "例: Construction will begin on the new site next month.  "
          },
          {
            "line": 272,
            "text": "訳: 新しい敷地では来月、建設工事が始まる。  "
          },
          {
            "line": 274,
            "text": "・facility  "
          },
          {
            "line": 275,
            "text": "定義: 特定の目的のために設けられた建物・設備。  "
          },
          {
            "line": 276,
            "text": "頻度: 〈9/10〉  "
          },
          {
            "line": 277,
            "text": "違い: `facility` は機能・設備に焦点があり、研究施設・製造施設など用途を強調する。`premises` は用途の詳細より、物理的な構内全体を指す。  "
          },
          {
            "line": 278,
            "text": "例: The laboratory operates a testing facility outside the city.  "
          },
          {
            "line": 279,
            "text": "訳: その研究所は市外で試験施設を運営している。  "
          },
          {
            "line": 281,
            "text": "5. 【他動詞・形式的】〈理論・主張・行動など〉を～という前提に置く、～に基づかせる"
          },
          {
            "line": 313,
            "text": "【類義語】"
          },
          {
            "line": 315,
            "text": "・base  "
          },
          {
            "line": 316,
            "text": "定義: 考え・行動・判断などを、特定の根拠・情報・原則に基づかせる。  "
          },
          {
            "line": 317,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 318,
            "text": "違い: `base A on B` は証拠・データ・経験などにも非常に広く使える。`premise A on B` は B が「前提として置かれる考え・仮定」である場合に特に適し、より形式的。  "
          },
          {
            "line": 319,
            "text": "例: The decision was based on updated safety data.  "
          },
          {
            "line": 320,
            "text": "訳: その決定は最新の安全データに基づいていた。  "
          },
          {
            "line": 322,
            "text": "・found  "
          },
          {
            "line": 323,
            "text": "定義: 理論・制度・主張などを、ある原理・根拠の上に築く。  "
          },
          {
            "line": 324,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 325,
            "text": "違い: `be founded on ...` は基礎となる原理・価値・事実にも使え、`premised on` より「築かれている」という比喩が強い。  "
          },
          {
            "line": 326,
            "text": "例: The organization was founded on the principle of equal access.  "
          },
          {
            "line": 327,
            "text": "訳: その組織は、平等なアクセスという原則に基づいて設立された。  "
          },
          {
            "line": 329,
            "text": "・predicate  "
          },
          {
            "line": 330,
            "text": "定義: 主張・判断などを、ある条件・事実・前提に依存させる。  "
          },
          {
            "line": 331,
            "text": "頻度: 〈4/10〉  "
          },
          {
            "line": 332,
            "text": "違い: `predicate A on B` は非常に形式的で、法律・学術で見られる。`premise A on B` と近いが、`premise` は「前提命題を置く」という語源・論証とのつながりがより直接的である。  "
          },
          {
            "line": 333,
            "text": "例: The claim is predicated on evidence that has since been disputed.  "
          },
          {
            "line": 334,
            "text": "訳: その主張は、その後争われるようになった証拠を前提としている。  "
          },
          {
            "line": 336,
            "text": "6. 【他動詞・形式的・まれ】〈命題・考え〉を前提として置く、～だと前提として述べる・仮定する"
          },
          {
            "line": 367,
            "text": "【類義語】"
          },
          {
            "line": 369,
            "text": "・assume  "
          },
          {
            "line": 370,
            "text": "定義: 証明せずに、ある内容をひとまず真として受け入れる。  "
          },
          {
            "line": 371,
            "text": "頻度: 〈10/10〉  "
          },
          {
            "line": 372,
            "text": "違い: `assume` は日常・学術のどちらでも広く使え、`premise` よりはるかに一般的。`premise` は論証の前提として明示的に置くという硬い響きがある。  "
          },
          {
            "line": 373,
            "text": "例: Assume that the two samples are independent.  "
          },
          {
            "line": 374,
            "text": "訳: 2つの標本は独立していると仮定しなさい。  "
          },
          {
            "line": 376,
            "text": "・posit  "
          },
          {
            "line": 377,
            "text": "定義: 議論・理論のために、命題や仮説を明示的に提示する。  "
          },
          {
            "line": 378,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 379,
            "text": "違い: `posit` は学術・哲学で比較的自然に使える一方、この語義の `premise` はさらにまれで古風・形式的に感じられることがある。  "
          },
          {
            "line": 380,
            "text": "例: The model posits that agents act on incomplete information.  "
          },
          {
            "line": 381,
            "text": "訳: そのモデルは、行為者は不完全な情報に基づいて行動すると仮定している。  "
          },
          {
            "line": 383,
            "text": "・postulate  "
          },
          {
            "line": 384,
            "text": "定義: 理論や推論の出発点として、命題・原理を仮定する。  "
          },
          {
            "line": 385,
            "text": "頻度: 〈5/10〉  "
          },
          {
            "line": 386,
            "text": "違い: `postulate` は科学・数学・哲学で「理論上の仮定として置く」ことを明確に表せる。`premise` は同じ方向を表せるが、動詞としては使用範囲が狭い。  "
          },
          {
            "line": 387,
            "text": "例: The theory postulates the existence of an unobserved mechanism.  "
          },
          {
            "line": 388,
            "text": "訳: その理論は、観測されていない機構の存在を仮定している。  "
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
