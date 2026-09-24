# Independent checker handoff

Pass: `example-attribution`

Review only the exact input packet included below and the specified checker prompt. Use an independent context. Do not consult earlier review outputs, resolutions, or final-blind findings. Return a single JSON object with the requested pass result. Set `reviewer.mode` to `handoff`, `reviewer.declared_model` to the actual model name available to you (do not guess), `reviewer.ingested_by` to `human`, and `reviewer.agent_id` to your actual unique agent path. Do not reuse an agent_id from another pass.

## Checker prompt

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


This is stage 1 of example-attribution. Return only the blind attribution record; do not ask to see or infer the withheld alignment key.

## Input packet

```json
{
  "schema_version": "example_attribution_blind_request_v1",
  "pass_id": "example-attribution",
  "taxonomy_ids": [
    "example_sense_attribution_mismatch"
  ],
  "specification": "prompts/check_pass_example_attribution_v6.md",
  "input_body_sha256": "8508fef1bf79309ca9c904c1a5b901698298454c0b9cddf6fe1227383f20bc7c",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 38,
        "label": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "definition": "人が犯罪、不正、不誠実な行為などをした可能性があると、十分な証明がない段階で考えること、またはその疑いを向けられている状態を表す。複数の個別の疑いを述べる suspicions は可算、疑いという状態を表す suspicion は不可算で使われる。on suspicion of ... のように特定の容疑でも無冠詞となる定型表現があるため、可算・不可算は意味だけで一律には決まらない。"
      },
      {
        "sense_id": "sense:002",
        "line": 91,
        "label": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "definition": "人、組織、動機、考えなどの真実性や信頼性を確信できず、すぐには信用しない態度を表す。相手や情報の裏に問題や意図があるのではないかという警戒を伴うこともある。語義1のように特定の犯罪・不正行為を想定する必要はなく、広い意味での mistrust / distrust に近い。"
      },
      {
        "sense_id": "sense:003",
        "line": 136,
        "label": "3. 【名詞・可算中心】～ではないかという気、確証のない推測",
        "definition": "特定の人が犯罪・不正をしたという疑いではなく、犯罪・不正を前提としない事実や状況が本当なのではないかと、確証のないまま感じることを表す。人物への容疑や一般的な不信ではなく、「そうではないか」という推測・予感に焦点がある。この意味では a suspicion that ... のように個々の考えを表す可算形が典型。可算・不可算は意味だけで一律に決まらず、構文にも左右される。"
      },
      {
        "sense_id": "sense:004",
        "line": 186,
        "label": "4. 【名詞・単数／formal（やや改まった）】ほんの少し、かすかな気配",
        "definition": "色、味、匂い、感情、表情などが、はっきり大量に存在するのではなく「あるかないか分かる程度」にわずかに感じられることを表す。通常 a suspicion of ... の形で用いられる比喩的な用法である。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-6f35064482c6",
        "example": "The sauce had a suspicion of citrus that made it taste fresher.",
        "translation": "そのソースにはほんのり柑橘の風味があり、より爽やかに感じられた。"
      },
      {
        "example_id": "ex-89201c7f223c",
        "example": "We had a strong suspicion that the delay was caused by a technical problem.",
        "translation": "私たちは、その遅延は技術的な問題によるのではないかという強い疑いを抱いていた。"
      },
      {
        "example_id": "ex-0575f444d17a",
        "example": "She had a sneaking suspicion that everyone already knew the answer.",
        "translation": "彼女は、皆すでに答えを知っているのではないかとひそかに感じていた。"
      },
      {
        "example_id": "ex-287d7b4cb87d",
        "example": "A suspicion of a smile appeared at the corner of her mouth.",
        "translation": "彼女の口元に、かすかな笑みが浮かんだ。"
      },
      {
        "example_id": "ex-da324141aa40",
        "example": "The test results confirmed her suspicion that the battery was failing.",
        "translation": "検査結果によって、バッテリーが劣化しているのではないかという彼女の推測が裏付けられた。"
      },
      {
        "example_id": "ex-69e69cb7082e",
        "example": "Two people were arrested on suspicion of fraud after the investigation.",
        "translation": "捜査後、2人が詐欺の容疑で逮捕された。"
      },
      {
        "example_id": "ex-e142028a3c83",
        "example": "Residents viewed the sudden policy change with suspicion.",
        "translation": "住民たちは突然の方針変更を疑いの目で見た。"
      },
      {
        "example_id": "ex-be2866e94e86",
        "example": "The security footage confirmed the manager's suspicions that a guard had taken the missing laptops.",
        "translation": "防犯映像によって、警備員がなくなったノートパソコンを持ち去ったという管理者の疑いが裏付けられた。"
      },
      {
        "example_id": "ex-2b84f168669b",
        "example": "There was a suspicion of disappointment in his voice.",
        "translation": "彼の声にはかすかな失望がにじんでいた。"
      },
      {
        "example_id": "ex-1bc8afbd46f2",
        "example": "The altered timestamp cast suspicion on the clerk who had access to the report.",
        "translation": "変更された時刻表示によって、報告書にアクセスできた事務員に疑いが向けられた。"
      },
      {
        "example_id": "ex-5b3fe8fb8945",
        "example": "The walls were white with a suspicion of blue in the evening light.",
        "translation": "その壁は白かったが、夕方の光の中ではほんのり青みを帯びていた。"
      },
      {
        "example_id": "ex-1966a015e076",
        "example": "The new monitoring system was initially greeted with some suspicion.",
        "translation": "新しい監視システムは当初、多少の疑いをもって受け止められた。"
      },
      {
        "example_id": "ex-197dd39d5d04",
        "example": "The unexplained transfer of client funds aroused suspicion of fraud among the auditors.",
        "translation": "顧客資金の説明のない移動が、監査担当者たちに詐欺の疑いを抱かせた。"
      },
      {
        "example_id": "ex-20740c3da421",
        "example": "The contractor remained under suspicion until the records were checked.",
        "translation": "記録が確認されるまで、その請負業者には疑いがかけられたままだった。"
      },
      {
        "example_id": "ex-5c88577a2ca8",
        "example": "The discrepancy cast suspicion on the reliability of the company's explanation.",
        "translation": "その食い違いによって、その会社の説明の信頼性に疑いが向けられた。"
      },
      {
        "example_id": "ex-411c135d337e",
        "example": "I have a suspicion that the meeting will finish earlier than planned.",
        "translation": "その会議は予定より早く終わるのではないかという気がしている。"
      },
      {
        "example_id": "ex-9442f8acf285",
        "example": "The employee came under suspicion when several invoices disappeared.",
        "translation": "複数の請求書がなくなったことで、その従業員が疑われるようになった。"
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
  },
  "specification_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
  "source_artifact_sha256": "dc02fc70b5f11b78e5105b0158a8a845a6314d562d748f4e571433de0e727341",
  "normalization_version": "check_pass_semantic_input_v2",
  "normalized_input_sha256": "71792d154d670339c40ffc77843b163ffb98294c615de64803fe49b1f5d0146c"
}
```
