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
  "input_body_sha256": "82f343438dd0057f0cc4edd16ece26ba75380521e8c02dfb806b6da7eb43d3f8",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 38,
        "label": "1. 【名詞・可算／不可算】容疑、犯罪・不正をしたのではないかという疑い",
        "definition": "人が犯罪、不正、不誠実な行為などをした可能性があると、十分な証明がない段階で考えること、またはその疑いを向けられている状態を表す。個々の疑いを数えるときは可算、疑いという状態・雰囲気をまとめて述べるときは不可算で使われる。"
      },
      {
        "sense_id": "sense:002",
        "line": 105,
        "label": "2. 【名詞・不可算中心】不信、警戒を伴う疑念",
        "definition": "人、組織、動機、考えなどをそのまま信用せず、「裏に何か問題・意図があるかもしれない」と疑って見る態度を表す。語義1のように特定の犯罪・不正行為を想定する必要はなく、広い意味での mistrust / distrust に近い。"
      },
      {
        "sense_id": "sense:003",
        "line": 176,
        "label": "3. 【名詞・可算】～ではないかという気、確証のない推測",
        "definition": "ある事実・状況が本当なのではないかと感じることを表す。ここでは犯罪・不正や相手への不信に限らず、証明はないが「たぶんそうだ」という予感・推測を指す。通常は個々の考えとして可算で、a suspicion that ... の形が非常に重要である。"
      },
      {
        "sense_id": "sense:004",
        "line": 243,
        "label": "4. 【名詞・単数／やや文語的】ほんの少し、かすかな気配",
        "definition": "色、味、匂い、感情、表情などが、はっきり大量に存在するのではなく「あるかないか分かる程度」にわずかに感じられることを表す。通常 a suspicion of ... の形で用いられる比喩的な用法である。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-8a4ef0999ecc",
        "example": "A detailed explanation dispelled our suspicion that the figures had been altered.",
        "translation": "詳しい説明によって、数値が改変されたのではないかという私たちの疑いは解消された。"
      },
      {
        "example_id": "ex-48102953e7b8",
        "example": "The contractor remained under suspicion until the records were checked.",
        "translation": "記録が確認されるまで、その請負業者には疑いがかけられたままだった。"
      },
      {
        "example_id": "ex-e51e4756d1e5",
        "example": "Two people were arrested on suspicion of fraud after the investigation.",
        "translation": "捜査後、2人が詐欺の容疑で逮捕された。"
      },
      {
        "example_id": "ex-36e9e4e6be44",
        "example": "The unexplained changes led to deep suspicion among investors.",
        "translation": "説明のない変更によって、投資家の間に強い不信が生じた。"
      },
      {
        "example_id": "ex-e0b61cb2de26",
        "example": "The security footage confirmed the manager's suspicions.",
        "translation": "防犯映像によって、管理者が抱いていた疑いが裏付けられた。"
      },
      {
        "example_id": "ex-601c8d708c80",
        "example": "Residents viewed the sudden policy change with suspicion.",
        "translation": "住民たちは突然の方針変更を疑いの目で見た。"
      },
      {
        "example_id": "ex-87c743df3053",
        "example": "We had a growing suspicion that the delay was caused by a technical problem.",
        "translation": "その遅延は技術的な問題によるのではないかという疑いが、私たちの中で強まっていった。"
      },
      {
        "example_id": "ex-16b22318fdc1",
        "example": "The walls were white with a suspicion of blue in the evening light.",
        "translation": "その壁は白かったが、夕方の光の中ではほんのり青みを帯びていた。"
      },
      {
        "example_id": "ex-3e259e33cb5c",
        "example": "She answered with a suspicion of a smile.",
        "translation": "彼女はほんのかすかな笑みを浮かべて答えた。"
      },
      {
        "example_id": "ex-f7355f9c6e4c",
        "example": "The new monitoring system was initially met with suspicion by employees.",
        "translation": "新しい監視システムは当初、従業員から疑いをもって受け止められた。"
      },
      {
        "example_id": "ex-90ed8fe19623",
        "example": "The employee came under suspicion when several invoices disappeared.",
        "translation": "複数の請求書がなくなったことで、その従業員が疑われるようになった。"
      },
      {
        "example_id": "ex-63ea3296b2ad",
        "example": "The unexplained transfer of funds aroused suspicion among the auditors.",
        "translation": "説明のつかない資金移動が監査担当者たちの疑いを招いた。"
      },
      {
        "example_id": "ex-dd90b4f98b60",
        "example": "He could not shake the nagging suspicion that he had forgotten something important.",
        "translation": "彼は何か大事なことを忘れたのではないかという消えない疑いを振り払えなかった。"
      },
      {
        "example_id": "ex-54111ea2191e",
        "example": "The test results confirmed her suspicion that the battery was failing.",
        "translation": "検査結果によって、バッテリーが劣化しているのではないかという彼女の推測が裏付けられた。"
      },
      {
        "example_id": "ex-e51165591ac7",
        "example": "She had a sneaking suspicion that everyone already knew the answer.",
        "translation": "彼女は、皆すでに答えを知っているのではないかとひそかに感じていた。"
      },
      {
        "example_id": "ex-a27d5b59244b",
        "example": "There was a suspicion of disappointment in his voice.",
        "translation": "彼の声にはかすかな失望がにじんでいた。"
      },
      {
        "example_id": "ex-dc9c7db7c4fb",
        "example": "The altered timestamp cast suspicion on the authenticity of the document.",
        "translation": "変更された時刻表示によって、その文書の真正性に疑いが向けられた。"
      },
      {
        "example_id": "ex-a9a32168cb59",
        "example": "The lack of transparency caused widespread suspicion about the process.",
        "translation": "透明性の欠如によって、その手続きに対する不信が広く生じた。"
      },
      {
        "example_id": "ex-f39ea7392ec3",
        "example": "I have a suspicion that the meeting will finish earlier than planned.",
        "translation": "その会議は予定より早く終わるのではないかという気がしている。"
      },
      {
        "example_id": "ex-f8f613237eae",
        "example": "The sauce had a suspicion of citrus that made it taste fresher.",
        "translation": "そのソースにはほんのり柑橘の風味があり、より爽やかに感じられた。"
      },
      {
        "example_id": "ex-660dfd458c56",
        "example": "Years of secrecy created a lasting suspicion of the agency.",
        "translation": "長年の秘密主義によって、その機関に対する根強い不信が生まれた。"
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
  "source_artifact_sha256": "358a6ef905363f010a31dece02f1dd57e94ea0fad57f759488d3898360d8fc54",
  "normalized_input_sha256": "3e856f8009c44f80857cd14972520eda2d6e5258986c459df70d55ab6368f1af"
}
```
