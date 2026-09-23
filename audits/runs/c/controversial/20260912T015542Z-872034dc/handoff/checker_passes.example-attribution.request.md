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
  "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 30,
        "label": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "definition": "政策・決定・主張・作品・発言・人物などが、社会全体または特定の集団の中で、強い意見の対立、批判、反対を引き起こしていることを表す。事実として真偽が決まっていないことを必ずしも含まず、悪い、違法、意図的に挑発的だという意味でもない。"
      },
      {
        "sense_id": "sense:002",
        "line": 156,
        "label": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "definition": "人が性格や態度の傾向として、議論を好んだり、既存の立場に反論して対立を生みやすかったりすることを表す。辞書に記載される低頻度の語義で、現代の controversial person は通常、語義1の「論争の的となっている人物」と解釈される。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-ac1f37066679",
        "example": "It remains controversial whether the policy reduced inequality.",
        "translation": "その政策が格差を縮小したかどうかは、今も議論が分かれている。"
      },
      {
        "example_id": "ex-4b69ba5d4c7d",
        "example": "Her controversial manner turned minor technical disagreements into public arguments.",
        "translation": "彼女の対立を生みやすい態度は、ささいな技術上の意見の違いまで公の論争に変えた。"
      },
      {
        "example_id": "ex-521917da671b",
        "example": "The city council postponed a highly controversial proposal.",
        "translation": "市議会は非常に物議を醸している提案を延期した。"
      },
      {
        "example_id": "ex-1ae410060fc9",
        "example": "The advertising campaign is controversial in some circles but popular with younger viewers.",
        "translation": "その広告キャンペーンは一部では物議を醸しているが、若い視聴者には人気がある。"
      },
      {
        "example_id": "ex-e9c0f853bc9b",
        "example": "The committee made a controversial decision to cancel the exhibition.",
        "translation": "委員会は展示会を中止するという物議を醸す決定を下した。"
      },
      {
        "example_id": "ex-4cbe0301a48f",
        "example": "The renovation plan became controversial after residents learned the full cost.",
        "translation": "住民が総費用を知った後、その改修計画は物議を醸すようになった。"
      },
      {
        "example_id": "ex-685e754c92c7",
        "example": "He was controversial by temperament, challenging even minor points in every debate.",
        "translation": "彼は性向として論争的で、どの討論でもささいな点にまで反論した。"
      },
      {
        "example_id": "ex-2b864bd448fb",
        "example": "The speaker was controversial in debate because he deliberately attacked each established position.",
        "translation": "その話者は確立した立場を一つ一つ意図的に攻撃したため、討論では論争的だった。"
      },
      {
        "example_id": "ex-e74721a3133b",
        "example": "The historian remains a controversial figure in the region.",
        "translation": "その歴史家はその地域で今も評価が大きく分かれる人物だ。"
      },
      {
        "example_id": "ex-069c7db5553b",
        "example": "The minister's controversial remark drew criticism from both parties.",
        "translation": "大臣の物議を醸す発言は両党から批判を招いた。"
      },
      {
        "example_id": "ex-7b75c5c09c71",
        "example": "The use of facial-recognition technology remains a controversial issue.",
        "translation": "顔認証技術の利用は依然として論争を呼ぶ問題だ。"
      },
      {
        "example_id": "ex-ee135a966740",
        "example": "The columnist has a controversial temperament and treats every meeting as a public debate.",
        "translation": "そのコラムニストは論争を好む気質で、どの会議も公開討論のように扱う。"
      },
      {
        "example_id": "ex-7927fe1bf63d",
        "example": "The interpretation is controversial among constitutional scholars.",
        "translation": "その解釈は憲法学者の間で議論が分かれている。"
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
  "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
  "normalized_input_sha256": "f5f6bd4a1b6efa01656892e3463b05da349bd90c954729744a277833d3869ad2"
}
```
