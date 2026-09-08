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
  "input_body_sha256": "341958940f8496856aeb8c0cfff9a4664b95d91d5ad66bc5a5a5e04c11689389",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 39,
        "label": "1. 【他動詞】構成する、（全体の一定割合を）占める",
        "definition": "一つまたは複数の人・物・部分・期間などが、一つの全体を形作る、またはその全体の一定割合・重要部分を占めることを表す。全体構成の能動構文では主語が構成要素、目的語がそれらによってできる全体である。一方、割合・部分量を示す構文では、目的語が割合・部分量となり、全体は of 句に現れる。意図的に組み立てる行為ではなく、部分と全体の関係を記述することが多い。"
      },
      {
        "sense_id": "sense:002",
        "line": 111,
        "label": "2. 【他動詞・連結的用法】～に当たる、～を意味する、～となる",
        "definition": "行為、状況、事実、結果などが、ある分類・評価・状態の定義や成立条件を満たし、そのものと見なせることを表す。目的語には crime、breach、threat、evidence、change、problem などが来る。法律用語だけではなく一般の評価にも使うが、何がその分類に当たるかをやや改まって判断する響きがある。"
      },
      {
        "sense_id": "sense:003",
        "line": 188,
        "label": "3. 【他動詞】（組織・委員会・政府などを）正式に設立する、組織する",
        "definition": "組織、委員会、裁判所、政府などを正式に形成・設置し、公式の組織体として成立させることを表す。制度や文脈によって所定の手続きや権限付与を伴うことはあるが、constitute という語だけで法的有効性や実際の活動可能性まで一律に保証するわけではない。"
      },
      {
        "sense_id": "sense:004",
        "line": 253,
        "label": "4. 【他動詞・公式・法律】（人を役職・地位に）正式に任命・指定する",
        "definition": "権限をもつ者・法律・公式文書などが、人を特定の役職・地位・役割に正式に任命・指定することを表す。任命の法的有効性、付与される権限、その立場で行動できる範囲は、該当する文書・制度・法域によって決まる。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-20739e4f6ab2",
        "example": "Sharing the data without permission would constitute a breach of the agreement.",
        "translation": "許可なくデータを共有すれば、その契約への違反に当たる。"
      },
      {
        "example_id": "ex-6580bc19b1b9",
        "example": "The charter identifies the treasurer as a legally constituted officer of the association.",
        "translation": "その憲章は、会計役を協会において法に基づき正式に任命された役職者として明記している。"
      },
      {
        "example_id": "ex-ce5a776418c8",
        "example": "Deliberately altering the records may constitute a criminal offence.",
        "translation": "記録を故意に改ざんすることは、刑事犯罪に当たる可能性がある。"
      },
      {
        "example_id": "ex-8e811b406263",
        "example": "Maintenance costs constitute a significant part of the annual budget.",
        "translation": "維持費は年間予算のかなりの部分を占める。"
      },
      {
        "example_id": "ex-3250194bfa48",
        "example": "Twelve jurors constitute the full jury in this court.",
        "translation": "この裁判所では、12人の陪審員が陪審全体を構成する。"
      },
      {
        "example_id": "ex-fd73f5de867d",
        "example": "The treaty provides for a tribunal to be constituted when a dispute arises.",
        "translation": "その条約は、紛争が生じた際に審判機関を設置することを定めている。"
      },
      {
        "example_id": "ex-924a4fd85622",
        "example": "Part-time employees constitute the majority of the evening staff.",
        "translation": "非常勤職員が夜間スタッフの過半数を占めている。"
      },
      {
        "example_id": "ex-68e8f9d29819",
        "example": "The charter constituted him treasurer of the association.",
        "translation": "その憲章によって、彼は協会の会計役に任命された。"
      },
      {
        "example_id": "ex-7022004a7a23",
        "example": "The guidelines explain what constitutes acceptable use of the system.",
        "translation": "その指針は、どのようなシステム利用が許容されるかを説明している。"
      },
      {
        "example_id": "ex-5b909f57236c",
        "example": "She was constituted guardian for the limited purpose stated in the order.",
        "translation": "彼女は、その命令に記された限定的な目的のための後見人に任命された。"
      },
      {
        "example_id": "ex-a5fd77ea3b57",
        "example": "The damaged bridge constitutes a serious risk to public safety.",
        "translation": "その損傷した橋は公共の安全に対する重大な危険となっている。"
      },
      {
        "example_id": "ex-4637d54ddbed",
        "example": "Online sales now constitute 35 percent of the company's revenue.",
        "translation": "オンライン販売は現在、その会社の売上高の35パーセントを占めている。"
      },
      {
        "example_id": "ex-01a49989788b",
        "example": "The commission was constituted under the new environmental law.",
        "translation": "その委員会は新しい環境法に基づいて設置された。"
      },
      {
        "example_id": "ex-c3399241dc9b",
        "example": "The revised policy constitutes a significant change in the company's approach.",
        "translation": "改訂された方針は、その会社の取り組み方の大きな変化に当たる。"
      },
      {
        "example_id": "ex-eae1a2d1edd9",
        "example": "The panel is constituted of experts from five different fields.",
        "translation": "その委員会は5つの異なる分野の専門家で構成されている。"
      },
      {
        "example_id": "ex-3cd3bc2622ea",
        "example": "A single anonymous message does not constitute proof of fraud.",
        "translation": "匿名のメッセージ一通だけでは、詐欺の証明にはならない。"
      },
      {
        "example_id": "ex-d9ef24b6a41d",
        "example": "Only a duly constituted board may approve the transaction.",
        "translation": "正式に構成された取締役会だけが、その取引を承認できる。"
      },
      {
        "example_id": "ex-4bc1c5dc0c02",
        "example": "The ministry constituted an independent panel to investigate the accident.",
        "translation": "同省は、その事故を調査する独立委員会を正式に設置した。"
      },
      {
        "example_id": "ex-3cfeeb6c7589",
        "example": "The parties agreed to constitute a transitional government.",
        "translation": "当事者らは暫定政府を発足させることで合意した。"
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
  "source_artifact_sha256": "f98ceb46d53d98a15da050b7cf90ea946c481b3b4bfa6a28e16261031574c94b",
  "normalized_input_sha256": "a7d45edb0d2551fe48842012dba24110606d72743c1dda2a8a055fe374c36c73"
}
```
