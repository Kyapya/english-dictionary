# Independent review handoff

Stage: `checker_recheck/round-9/example-attribution`

Review only this packet and its named specification. Do not inspect other round files, prior findings, or alignment keys. Save the raw response at the exact path requested in your task, with required reviewer metadata.

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
  "input_body_sha256": "4ab0d5d71a7c1f54616c6e43ea3bd1cf78edf3d0d530028f0398efd73951f200",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 36,
        "label": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "definition": "確証がない段階で、ある事柄が真実かもしれないと考えることを表す。人が犯罪・不正をした可能性への疑いもこの意味に含む。Oxfordは犯罪・不正の疑いでは可算・不可算の両用法を、命題の真偽については可算用法を記している。"
      },
      {
        "sense_id": "sense:002",
        "line": 89,
        "label": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "definition": "人や物事を十分に信用できず、疑いの目で見る態度を表す。ある事柄が真実かどうかについての見立てを表す語義1とは異なり、対象への不信や警戒に焦点を置く。"
      },
      {
        "sense_id": "sense:003",
        "line": 117,
        "label": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "definition": "ものがごく少量、またはかすかな兆候として感じられることを表す。通常 a suspicion of ... の形で使われる。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-d23afb316897",
        "example": "The unexplained gap in the records raised some suspicion among auditors that several invoices had been altered.",
        "translation": "記録の説明できない欠落から、複数の請求書が改ざんされていたのではないかという疑いが監査担当者の間に生じた。"
      },
      {
        "example_id": "ex-8c2dff4b567f",
        "example": "Residents regarded the sudden policy change with suspicion.",
        "translation": "住民たちは突然の方針変更を疑いの目で見た。"
      },
      {
        "example_id": "ex-a283f299e62c",
        "example": "The old tale had a suspicion of truth in it.",
        "translation": "その古い物語には、どこか真実味が感じられた。"
      },
      {
        "example_id": "ex-a300c62da701",
        "example": "The contractor remained under suspicion while investigators checked whether it had falsified invoices.",
        "translation": "請求書を改ざんしたかどうかを捜査員が調べる間、その請負業者は疑いをかけられたままだった。"
      },
      {
        "example_id": "ex-1fbe1b9ab0de",
        "example": "There was a suspicion of a smile in her reply.",
        "translation": "彼女の返事にはかすかな笑みが感じられた。"
      },
      {
        "example_id": "ex-1b58df9a85ca",
        "example": "The manager had a suspicion that the cashier had altered the sales records.",
        "translation": "その管理者は、レジ係が売上記録を改ざんしたのではないかと疑っていた。"
      },
      {
        "example_id": "ex-55d9cedf815d",
        "example": "Two people were arrested on suspicion of fraud after the investigation.",
        "translation": "捜査後、2人が詐欺の容疑で逮捕された。"
      },
      {
        "example_id": "ex-ddc458ae2d6b",
        "example": "I had a suspicion that the meeting had been canceled.",
        "translation": "会議は中止されたのではないかと私は疑っていた。"
      },
      {
        "example_id": "ex-733c6810992f",
        "example": "The abrupt policy reversal aroused residents' suspicions that officials had concealed the project's true cost.",
        "translation": "突然の方針転換を受けて、住民たちは当局が事業の本当の費用を隠していたのではないかと疑い始めた。"
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
  "source_artifact_sha256": "e90fd78ac088d2024598beed6ae0af6133d299beb74c373437b548466fce7266",
  "normalized_input_sha256": "5894525e9b527613e09eb766e02503fae2a05121001470ed473f5d117909de5f"
}
```
