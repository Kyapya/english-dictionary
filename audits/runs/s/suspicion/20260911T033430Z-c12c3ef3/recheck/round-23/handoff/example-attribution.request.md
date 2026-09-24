# Independent checker handoff

Stage: `checker_passes/example-attribution`

Use a fresh independent reviewer session. Do not inspect prior-round findings or other checker outputs. Save one raw response in the corresponding `responses/` file with the exact `pass_id` and reviewer identity required by the prompt. Do not edit or replace earlier raw files.

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


## Exact input packet

```json
{
  "schema_version": "example_attribution_blind_request_v1",
  "pass_id": "example-attribution",
  "taxonomy_ids": [
    "example_sense_attribution_mismatch"
  ],
  "specification": "prompts/check_pass_example_attribution_v6.md",
  "input_body_sha256": "b34f7da3691330b05a3a8a1aaf894599ec4d16d118e331f84a1dc41bcfca5677",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 38,
        "label": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "definition": "人が犯罪、不正、不誠実な行為をしたとして疑いの対象になること、またはその人の行為に不正の容疑を向けることを表す。焦点は、ある命題の真偽を予想すること自体より、特定の人がその行為をしたとして疑われている点にある。that節を伴う例もあるが、節の話題だけで語義を決めず、人への容疑を表す場合は語義1に置く。複数の個別の疑いを述べる suspicions は可算、疑いという状態を表す suspicion は不可算で使われる。on suspicion of ... のように特定の容疑でも無冠詞となる定型表現があるため、可算・不可算は意味だけで一律には決まらない。"
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
        "definition": "十分な証拠がなくても、ある命題や状況が真かもしれないと考える、話者の暫定的な推測・予感を表す。焦点は命題の真偽にあり、特定の人を犯罪・不正の容疑者として扱うこと自体ではない。that節の話題だけで語義を決めず、節全体についての推測は語義3、特定の人へ行為の容疑を向ける用法は語義1に置く。この用法では個々の考えを表す可算形が典型。可算・不可算は意味だけで一律に決まらず、構文にも左右される。"
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
        "example_id": "ex-b05441354faa",
        "example": "I have a suspicion that the meeting will finish earlier than planned.",
        "translation": "その会議は予定より早く終わるのではないかという気がしている。"
      },
      {
        "example_id": "ex-7109decd0751",
        "example": "The altered timestamp cast suspicion on the clerk who had access to the report.",
        "translation": "変更された時刻表示によって、報告書にアクセスできた事務員に疑いが向けられた。"
      },
      {
        "example_id": "ex-07975d37945b",
        "example": "A suspicion of a smile appeared at the corner of her mouth.",
        "translation": "彼女の口元に、かすかな笑みが浮かんだ。"
      },
      {
        "example_id": "ex-f7a4533cef3c",
        "example": "The new monitoring system was initially greeted with some suspicion.",
        "translation": "新しい監視システムは当初、多少の疑いをもって受け止められた。"
      },
      {
        "example_id": "ex-3e2a729590ee",
        "example": "Among the auditors, the unexplained transfer of client funds aroused suspicion that the treasurer had committed fraud.",
        "translation": "監査担当者の間では、顧客資金の使途不明な移動により、会計係が詐欺を行ったのではないかという疑いが生じた。"
      },
      {
        "example_id": "ex-6673d64fd465",
        "example": "We had a strong suspicion that the delay was caused by a technical problem.",
        "translation": "私たちは、その遅延は技術的な問題によるのではないかという強い疑いを抱いていた。"
      },
      {
        "example_id": "ex-711c9be0fe2d",
        "example": "Two people were arrested on suspicion of fraud after the investigation.",
        "translation": "捜査後、2人が詐欺の容疑で逮捕された。"
      },
      {
        "example_id": "ex-b36a63140789",
        "example": "The sauce had a suspicion of citrus that made it taste fresher.",
        "translation": "そのソースにはほんのり柑橘の風味があり、より爽やかに感じられた。"
      },
      {
        "example_id": "ex-703df1820255",
        "example": "The employee came under suspicion when several invoices disappeared.",
        "translation": "複数の請求書がなくなったことで、その従業員が疑われるようになった。"
      },
      {
        "example_id": "ex-38ece9c9bad6",
        "example": "The test results confirmed her suspicion that the battery was failing.",
        "translation": "検査結果によって、バッテリーが劣化しているのではないかという彼女の推測が裏付けられた。"
      },
      {
        "example_id": "ex-66342a6a5835",
        "example": "There was a suspicion of disappointment in his voice.",
        "translation": "彼の声にはかすかな失望がにじんでいた。"
      },
      {
        "example_id": "ex-3b391b190f2d",
        "example": "The contractor remained under suspicion until the records were checked.",
        "translation": "記録が確認されるまで、その請負業者には疑いがかけられたままだった。"
      },
      {
        "example_id": "ex-58250159cf7a",
        "example": "The security footage confirmed the manager's suspicions that a guard had stolen the missing laptops.",
        "translation": "防犯映像によって、警備員がなくなったノートパソコンを盗んだという管理者の疑いが裏付けられた。"
      },
      {
        "example_id": "ex-42cf1597e55a",
        "example": "The discrepancy cast suspicion on the reliability of the company's explanation.",
        "translation": "その食い違いによって、その会社の説明の信頼性に疑いが向けられた。"
      },
      {
        "example_id": "ex-68c0aa431b5b",
        "example": "She had a sneaking suspicion that everyone already knew the answer.",
        "translation": "彼女は、皆すでに答えを知っているのではないかとひそかに感じていた。"
      },
      {
        "example_id": "ex-733171bde527",
        "example": "Residents viewed the sudden policy change with suspicion.",
        "translation": "住民たちは突然の方針変更を疑いの目で見た。"
      },
      {
        "example_id": "ex-13fd09516339",
        "example": "The walls were white with a suspicion of blue in the evening light.",
        "translation": "その壁は白かったが、夕方の光の中ではほんのり青みを帯びていた。"
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
  "source_artifact_sha256": "f583eaabf925bd9587585be43d243b3ff6dbb0b2fd483ecbd1d89a0fce16aee2",
  "normalization_version": "check_pass_semantic_input_v2",
  "normalized_input_sha256": "023f9b59641783195187fe5c3b830220be5ad3c728586ee4f5eb15ac95a0defb"
}
```
