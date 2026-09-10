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
  "input_body_sha256": "dce1e8375f2e9709647eb4c0fd89fa016895cec32363a81b3950d8cdb28a2078",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 40,
        "label": "1. 【形容詞・人・判断】分別のある、道理にかなった、現実的な",
        "definition": "感情だけで決めず、理由・経験・実際の条件を考えて、適切で無理のない判断や行動をすることを表す。人にも、考え・助言・計画・解決策などにも使い、話し手が妥当だと評価する含みがある。"
      },
      {
        "sense_id": "sense:002",
        "line": 161,
        "label": "2. 【形容詞・衣類・靴】実用的な、実用本位の",
        "definition": "衣服・靴・かばんなどが、流行や見た目よりも、歩きやすさ・丈夫さ・防寒性などの実用性を重視して作られたり選ばれたりしていることを表す。必ずしも醜い、古い、または質が低いという意味ではない。"
      },
      {
        "sense_id": "sense:003",
        "line": 230,
        "label": "3. 【形容詞・形式的】感じ取れる、明確に分かる、かなりの",
        "definition": "差・変化・増減・量などが、感覚や判断によって認識できる程度にはっきりしていることを表す。現代の一般会話での「分別のある」という意味より形式的で、sensible difference や sensible increase のように、無視できない程度を述べる。"
      },
      {
        "sense_id": "sense:004",
        "line": 310,
        "label": "4. 【形容詞・形式的／古風】（刺激などを）感じ取れる、知覚できる",
        "definition": "痛み・熱・光などの外部刺激を、感覚器官や身体で受け取る能力があることを表す。現代の一般英語では sensitive to が普通で、sensible to は古風・形式的または専門的に響く。"
      },
      {
        "sense_id": "sense:005",
        "line": 371,
        "label": "5. 【形容詞・形式的／文学的・sensible of】～を意識している、～を深く感じている",
        "definition": "事実・危険・義務・誤り・親切などを心で認識し、強く意識していることを表す。通常 sensible of 〈名詞〉の形で使い、現代の会話では aware of、conscious of、grateful for などが自然なことが多い。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-06fbbbeac7c3",
        "example": "The software update made a sensible difference to the loading time.",
        "translation": "ソフトウェアの更新によって、読み込み時間に明らかな違いが出た。"
      },
      {
        "example_id": "ex-ce1033cabc3a",
        "example": "I am deeply sensible of your kindness during this difficult time.",
        "translation": "この困難な時期にあなたが親切にしてくださったことを深く感じています。"
      },
      {
        "example_id": "ex-c73d0a672e66",
        "example": "Please be sensible about how much equipment you bring.",
        "translation": "どれだけ機材を持ってくるかは、現実的に考えてください。"
      },
      {
        "example_id": "ex-e98481f4000e",
        "example": "We need a sensible approach to reducing unnecessary costs.",
        "translation": "不要な費用を減らすには、現実的な取り組み方が必要だ。"
      },
      {
        "example_id": "ex-f1d531f2ab27",
        "example": "It is sensible to keep a copy of the receipt.",
        "translation": "領収書の写しを保管しておくのが賢明だ。"
      },
      {
        "example_id": "ex-25b3cb874623",
        "example": "Her sensible advice helped me avoid a costly mistake.",
        "translation": "彼女の現実的な助言のおかげで、私は高くつく間違いを避けられた。"
      },
      {
        "example_id": "ex-525efed7dbf5",
        "example": "There has been a sensible change in the patient's condition.",
        "translation": "患者の状態には、はっきり分かる変化があった。"
      },
      {
        "example_id": "ex-d7bdb6329e6c",
        "example": "The injured area remained sensible to pain after the procedure.",
        "translation": "処置後も、負傷した部位は痛みを感じ取る状態だった。"
      },
      {
        "example_id": "ex-538037f4c7f6",
        "example": "Taking the earlier train was a sensible decision.",
        "translation": "早い方の電車に乗ったのは妥当な判断だった。"
      },
      {
        "example_id": "ex-097205d56b28",
        "example": "She was sensible of the fact that her decision affected the whole team.",
        "translation": "彼女は、自分の決定がチーム全体に影響するという事実を意識していた。"
      },
      {
        "example_id": "ex-756df75d4de7",
        "example": "Wear sensible shoes because the tour involves a lot of walking.",
        "translation": "たくさん歩くツアーなので、歩きやすい靴を履いてください。"
      },
      {
        "example_id": "ex-bce154207b58",
        "example": "It would be sensible for you to check the figures again.",
        "translation": "あなたがもう一度数字を確認するのが賢明だろう。"
      },
      {
        "example_id": "ex-4bf709203bc3",
        "example": "The instrument is sensible to heat from a nearby flame.",
        "translation": "その器具は近くの炎から出る熱を感知できる。"
      },
      {
        "example_id": "ex-cc2725a340f4",
        "example": "The material is sensible to light and should be stored in the dark.",
        "translation": "その素材は光を感知する性質があるので、暗所で保管すべきだ。"
      },
      {
        "example_id": "ex-7ea70512c2a1",
        "example": "The guide recommends sensible footwear for the uneven ground.",
        "translation": "ガイドは、でこぼこした地面には実用的な履物を勧めている。"
      },
      {
        "example_id": "ex-3ebf34ad4f4d",
        "example": "The volunteers were keenly sensible of the risks involved.",
        "translation": "ボランティアたちは、そこに伴う危険を強く意識していた。"
      },
      {
        "example_id": "ex-9ff99954fb7f",
        "example": "The sensible thing to do is wait until the weather improves.",
        "translation": "天候が回復するまで待つのが妥当な行動だ。"
      },
      {
        "example_id": "ex-767566a3d76d",
        "example": "He was sensible enough to ask for help before the problem grew.",
        "translation": "彼は問題が大きくなる前に助けを求めるだけの分別があった。"
      },
      {
        "example_id": "ex-42f8f43956f8",
        "example": "Pack sensible clothing for the cold and wet conditions.",
        "translation": "寒くて雨の多い状況に合う実用的な服を荷造りしてください。"
      },
      {
        "example_id": "ex-edb8f6f2b228",
        "example": "The new process produced a sensible reduction in waste.",
        "translation": "新しい工程によって、廃棄物が明らかに減少した。"
      },
      {
        "example_id": "ex-23d0968ce45d",
        "example": "The policy led to a sensible increase in public access.",
        "translation": "その政策によって、一般の利用可能性がはっきり増した。"
      },
      {
        "example_id": "ex-baefd0b2b304",
        "example": "He soon became sensible of his error and apologized.",
        "translation": "彼はすぐに自分の誤りに気づき、謝罪した。"
      },
      {
        "example_id": "ex-9970ff247279",
        "example": "I bought a sensible coat rather than a delicate fashion jacket.",
        "translation": "繊細なファッションジャケットではなく、実用的なコートを買った。"
      },
      {
        "example_id": "ex-2cf3b522d5a4",
        "example": "Choose sensible clothing for the long flight.",
        "translation": "長時間のフライトには実用的な服を選んでください。"
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
  "source_artifact_sha256": "0035642740b1174f92eb8173dfb0455de3648f65c58090795bb3e13932a0c417",
  "normalized_input_sha256": "bc83a7d0363f67dba987d96aa366208c26c87576fe1ee5b1a7b8e688666908a5"
}
```
