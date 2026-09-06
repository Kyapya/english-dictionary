# Independent checker handoff

Stage: `checker_passes/example-attribution`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.example-attribution.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_example_attribution_v6

## 目的

見出し語の各例文が、所属する語義ブロックへ意味的に帰属するかを、所属情報を参照しない先行判定（ブラインド再分類）で検査する。

## 担当タクソノミー分類

- `example_sense_attribution_mismatch`

## 検査ルール

- 検査は必ず次の2段階の順で行い、段階1の判定を段階2より先に確定・記録する。
- 段階1（ブラインド帰属判定）: `sense_structure` から語義番号、見出しの品詞・意味領域ラベル、訳語、定義の一覧を作る。次に `collocations_examples` の各例文（見出し語を含む例文のみ。類義語・反意語欄の例文は対象外）について、所属ブロック、コロケーション見出し、用途行を参照せず、例文と訳だけから最も自然な帰属語義を判定する。次点候補の有無と、判別根拠となった例文内の語句を記録する。
- 段階1では所属語義を含まない `example_attribution_blind_request_v1` だけを受け取り、判定を `example_attribution_blind_record_v1` として保存する。調整役はこの記録が保存されるまで所属キーを渡さない。
- `unique` 判定は、例文中で**見出し語そのものが担う意味関係、項構造、構文フレーム、結果状態、方向性**から他の有力候補語義を排除できる場合に限る。`doctor`、`project`、`variable`、`assignment`、`owner` など、単に話題分野・登場人物・対象領域を示す周辺語だけを根拠に `unique` としてはならない。
- `discriminating_terms` は、見出し語の意味選択に直接効く語句を記録する。可能なら見出し語に結び付く目的語・補語・前置詞句・小辞・結果表現・意味役割を用いる。単なる分野語・人物名詞・背景語は、それ自体が競合語義を意味的に排除することを説明できない限り判別語としない。
- `unique` の `rationale` では、最有力語義だけを説明して終えてはならない。少なくとも1つのもっともらしい競合語義を明示し、**同じ例文中の見出し語の使われ方**がなぜ競合語義では成立しないかを比較して述べる。
- 競合語義を排除する材料が話題分野などの周辺語しかない場合、または見出し語自体の意味関係から一意化できない場合は `ambiguous` とし、自然に成立する候補語義をすべて `candidate_sense_ids` に残す。表面的なトピック推定で曖昧性を消してはならない。
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


## Input packet

```json
{
  "schema_version": "example_attribution_blind_request_v1",
  "pass_id": "example-attribution",
  "taxonomy_ids": [
    "example_sense_attribution_mismatch"
  ],
  "specification": "prompts/check_pass_example_attribution_v6.md",
  "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 40,
        "label": "1. 【他動詞】～を…に限る、限定する",
        "definition": "話題、活動、作業、影響、現象などが及ぶ範囲を、特定の対象・場所・期間・分野などの内側に限定する。対象がすでにその範囲に収まっていることを述べる受動形と、話し手が意識的に扱う範囲を絞る能動形・再帰形の両方がよく使われる。"
      },
      {
        "sense_id": "sense:002",
        "line": 118,
        "label": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する",
        "definition": "人や動物を、部屋、施設、囲い、刑務所などの外へ自由に出られないようにする。物理的な障壁、命令、拘禁などによる移動の制限を表し、本人の自由意思で滞在している場合には通常使わない。"
      },
      {
        "sense_id": "sense:003",
        "line": 191,
        "label": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる",
        "definition": "病気、けが、身体状態などが原因で、人がベッド、自宅、病室など限られた場所から動けない、または外出できない状態にする。原因を主語にする能動文も可能だが、本人を主語にした be confined to が特に多い。"
      },
      {
        "sense_id": "sense:004",
        "line": 248,
        "label": "4. 【形容詞】狭く囲まれた、限られた",
        "definition": "confined の形で、空間や区域が壁や境界に囲まれて狭い、または内部で動ける余地が少ないことを表す。単に面積が小さいだけでなく、閉鎖性や動きにくさを含みやすい。"
      },
      {
        "sense_id": "sense:005",
        "line": 321,
        "label": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域",
        "definition": "通常 confines の形で、場所・組織・分野などの外縁をなす境界、またはその境界に囲まれた内部の領域を表す。現代の一般的な文章では単数形 confine より複数形 confines が圧倒的に普通である。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-ab9dc4cef69c",
        "example": "Her influence extended far beyond the confines of the university.",
        "translation": "彼女の影響力は大学の枠をはるかに越えて広がった。"
      },
      {
        "example_id": "ex-48d231fdefb7",
        "example": "The negotiations took place within the confines of the embassy.",
        "translation": "交渉は大使館の敷地内で行われた。"
      },
      {
        "example_id": "ex-f6323709feaa",
        "example": "The magnetic field confines the plasma to the center of the chamber.",
        "translation": "その磁場はプラズマを容器の中心部に閉じ込める。"
      },
      {
        "example_id": "ex-19fbcd0bb31e",
        "example": "The technicians had to work in confined conditions beneath the stage.",
        "translation": "技術者たちは舞台の下の狭い環境で作業しなければならなかった。"
      },
      {
        "example_id": "ex-9d35134efbf3",
        "example": "The group continued its work outside the confines of the formal organization.",
        "translation": "そのグループは正式な組織の枠外でも活動を続けた。"
      },
      {
        "example_id": "ex-20027313c181",
        "example": "He is temporarily confined to his room while he recovers.",
        "translation": "彼は回復するまで一時的に自室で過ごさなければならない。"
      },
      {
        "example_id": "ex-2b8d20bee0ac",
        "example": "A knee injury confined her to the apartment for most of the winter.",
        "translation": "膝のけがのため、彼女は冬の大半をアパートから出られずに過ごした。"
      },
      {
        "example_id": "ex-9577d742cfe7",
        "example": "He was confined to quarters for disobeying the order.",
        "translation": "彼は命令に従わなかったため、兵舎待機を命じられた。"
      },
      {
        "example_id": "ex-d5a6da675b13",
        "example": "The prisoner was confined in a windowless cell for several days.",
        "translation": "その囚人は数日間、窓のない独房に拘禁された。"
      },
      {
        "example_id": "ex-afda08153c24",
        "example": "I felt confined in the tiny room after only a few hours.",
        "translation": "その小さな部屋に数時間いただけで、私は閉じ込められたように感じた。"
      },
      {
        "example_id": "ex-f36507fc3020",
        "example": "The story moves beyond the narrow confines of a family dispute.",
        "translation": "その物語は家族間の争いという狭い枠を越えて展開する。"
      },
      {
        "example_id": "ex-50ac6b0a7623",
        "example": "Please confine the discussion to the issues on today's agenda.",
        "translation": "議論は本日の議題にある問題だけに絞ってください。"
      },
      {
        "example_id": "ex-32e4c7c37db5",
        "example": "The machine should not be operated in a confined space without adequate ventilation.",
        "translation": "その機械は、十分な換気のない閉鎖空間で作動させるべきではない。"
      },
      {
        "example_id": "ex-2132e30d65f2",
        "example": "After the operation, he was confined to his home for several days.",
        "translation": "手術後、彼は数日間、自宅から出られなかった。"
      },
      {
        "example_id": "ex-cb86d2ef723d",
        "example": "The order kept the soldiers confined to their barracks overnight.",
        "translation": "その命令により兵士たちは一晩、兵舎から出られなかった。"
      },
      {
        "example_id": "ex-cead63c39f1a",
        "example": "In this chapter, I will confine myself to examining the short-term effects.",
        "translation": "この章では、短期的な影響の検討だけに対象を絞る。"
      },
      {
        "example_id": "ex-d7b45d249ca7",
        "example": "She confined her remarks to the financial risks of the proposal.",
        "translation": "彼女は発言をその提案の財務上のリスクに限定した。"
      },
      {
        "example_id": "ex-2ee60453400b",
        "example": "She was confined to bed for a week with a severe infection.",
        "translation": "彼女は重い感染症のため1週間、寝床から起きられなかった。"
      },
      {
        "example_id": "ex-4c6a8b45a115",
        "example": "The crew lived in confined quarters during the voyage.",
        "translation": "乗組員は航海中、狭い居住区で暮らした。"
      },
      {
        "example_id": "ex-ed31d79c879d",
        "example": "The shortage is not confined to rural areas.",
        "translation": "その不足は農村部だけに限られた問題ではない。"
      },
      {
        "example_id": "ex-04a757c12fe1",
        "example": "The injured bird was temporarily confined to a large enclosure.",
        "translation": "けがをした鳥は一時的に大きな囲いの中で保護された。"
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
}
```
