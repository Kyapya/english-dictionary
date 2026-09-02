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
  "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 30,
        "label": "1. 【名詞・不可算】公衆の注目、報道上の露出",
        "definition": "人・企業・作品・出来事などが、新聞、テレビなどのメディアを通じて世間から受ける注目や報道上の露出。好意的とは限らず、good/bad/negative/unwanted publicity のように評価を添えられる。"
      },
      {
        "sense_id": "sense:002",
        "line": 101,
        "label": "2. 【名詞・不可算】宣伝活動、広報",
        "definition": "人、商品、作品、行事、主張などに世間の関心を集めるために行う広報・宣伝活動。広告に限らず、情報提供などの広報手段を含み得る。ここでは世間の注目を集める側の活動・手段に焦点を置く。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-89fae701bfc6",
        "example": "The restaurant responded quickly to the negative publicity surrounding the safety complaint.",
        "translation": "そのレストランは、安全性に関する苦情をめぐる否定的な報道にすぐ対応した。"
      },
      {
        "example_id": "ex-b3cd135cea73",
        "example": "The company staged a publicity stunt by projecting its logo onto the river bridge.",
        "translation": "その会社は川に架かる橋へロゴを投影する話題作りの仕掛けを行った。"
      },
      {
        "example_id": "ex-51c288100a2c",
        "example": "The organizers arranged advance publicity for the festival several months before it opened.",
        "translation": "主催者は祭りの開幕数か月前から事前広報を手配した。"
      },
      {
        "example_id": "ex-d9402edd47c2",
        "example": "The press office prepared publicity material for the product launch.",
        "translation": "広報室は製品発売のための宣伝資料を用意した。"
      },
      {
        "example_id": "ex-24c2620e3b89",
        "example": "The museum launched a publicity campaign for its new exhibition.",
        "translation": "その博物館は新しい展覧会の広報キャンペーンを始めた。"
      },
      {
        "example_id": "ex-93e5ac564ed0",
        "example": "The charity gained widespread publicity after the athlete supported its campaign.",
        "translation": "その慈善団体は、その選手がキャンペーンを支持した後、広く世間の注目を浴びた。"
      },
      {
        "example_id": "ex-b96ab1d45bb5",
        "example": "The scandal gave the company bad publicity.",
        "translation": "その不祥事は会社に否定的な世間の注目をもたらした。"
      },
      {
        "example_id": "ex-ee610cdc723c",
        "example": "The novelist shuns publicity and rarely gives interviews.",
        "translation": "その小説家は世間の注目を避け、めったにインタビューに応じない。"
      },
      {
        "example_id": "ex-67f583463d68",
        "example": "The discovery received widespread publicity in the national press.",
        "translation": "その発見は全国紙で広く報道された。"
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
