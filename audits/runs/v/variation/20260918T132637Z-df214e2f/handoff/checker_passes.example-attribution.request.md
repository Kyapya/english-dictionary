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
  "input_body_sha256": "e3caa8e1af96d10a7116b59750a969badff2bddfcee77986301493d751e824b9",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 45,
        "label": "1. 【名詞・不可算／可算】変化、変動、ばらつき",
        "definition": "量・水準・品質・状態などが一定ではなく変わること、またはその変化の幅・ばらつきを表す。変動・ばらつきを総体として述べる場合は不可算が多く、個々の変化・差・型を数える場合は可算になることが多い。個々の対象間の差や専門分野の変異を主に述べる場合は、語義3などの用法になる。"
      },
      {
        "sense_id": "sense:002",
        "line": 131,
        "label": "2. 【名詞・可算】基準から少し変えたもの、変形、別形",
        "definition": "同じ基本的な考え方・型・方法を保ちながら、内容や構成の一部を変えたものを表す。元と無関係な別物ではなく、「元のものを少し変えた版」という含みがある。`a variation on ...` は「…を土台にした変形・アレンジ」として特に重要である。音楽の主題に基づく専門的な用法は語義4、契約条件の正式な変更は語義6で扱う。"
      },
      {
        "sense_id": "sense:003",
        "line": 198,
        "label": "3. 【名詞・不可算／可算・生物学・遺伝学・医学】集団内の個体差、変異",
        "definition": "同じ種に属する個体や集団の内部・集団間に見られる、遺伝的・構造的・機能的な差を表す。生物の同種・同群の特徴が一様でないことに焦点を置く専門用法である。"
      },
      {
        "sense_id": "sense:004",
        "line": 274,
        "label": "4. 【名詞・可算・音楽】変奏；（複数・作品全体）変奏曲",
        "definition": "主題や旋律を反復し、旋律・和声・リズム・調性などに変化や装飾を加えた短い音楽作品、またはその一つの展開を表す。単数の `a variation` は通常、一連の変奏のうちの一つの変奏を指し、`variations` 全体や作品全体を指す場合に「変奏曲」とする。"
      },
      {
        "sense_id": "sense:005",
        "line": 322,
        "label": "5. 【名詞・可算・バレエ】ソロ演目、独舞",
        "definition": "クラシック・バレエで、踊り手が一人で踊る独舞・ソロ番号、または作品内のソロ部分を表す。音楽の変奏曲ではなく、舞踊作品上の演目名である。"
      },
      {
        "sense_id": "sense:006",
        "line": 365,
        "label": "6. 【名詞・可算／不可算・契約・法務】契約変更、契約変更事項",
        "definition": "契約締結後に、作業範囲・仕様・数量・価格・納期などの契約条件を変更すること、またはその変更内容を表す。契約書や適用法に定められた手続が問題となる専門用法で、合意・承認・記録を伴うことも多いが、必要な要件は契約・法域によって異なる。"
      },
      {
        "sense_id": "sense:007",
        "line": 403,
        "label": "7. 【名詞句・不可算・航海・地球科学・測量】magnetic variation＝磁気偏角",
        "definition": "複合表現 `magnetic variation` は、地球上のある地点で真北と磁北がなす水平角、またはその方位差を表す。地域や時期によって異なるため、航海・測量・方位の補正で考慮される。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-770ca952997f",
        "example": "He chose a variation from The Sleeping Beauty for the audition.",
        "translation": "彼はオーディションに『眠れる森の美女』のソロ演目を選んだ。"
      },
      {
        "example_id": "ex-755f618699d9",
        "example": "The students rehearsed a variation from the ballet before class.",
        "translation": "生徒たちは授業の前に、そのバレエ作品のソロ演目を練習した。"
      },
      {
        "example_id": "ex-49e09a36c4ae",
        "example": "The researchers compared genetic variation between populations living in different environments.",
        "translation": "研究者たちは、異なる環境に住む集団間の遺伝的変異を比較した。"
      },
      {
        "example_id": "ex-84e25b623627",
        "example": "The concert opened with a set of variations on a folk melody.",
        "translation": "その演奏会は民謡の旋律による変奏曲集で幕を開けた。"
      },
      {
        "example_id": "ex-5d633c938954",
        "example": "There is considerable variation in the time needed to complete the task.",
        "translation": "その作業を終えるのに必要な時間にはかなりのばらつきがある。"
      },
      {
        "example_id": "ex-d13f06f0bef3",
        "example": "Navigators must account for magnetic variation when plotting a course.",
        "translation": "航海者は航路を設定する際に磁気偏角を考慮しなければならない。"
      },
      {
        "example_id": "ex-17450ba09728",
        "example": "The editor created a slight variation on the original instructions by revising the wording.",
        "translation": "その編集者は文言を改め、元の説明書を少し変えた別版を作成した。"
      },
      {
        "example_id": "ex-4d5f8ddc089f",
        "example": "The novel is a clever variation on a familiar coming-of-age story.",
        "translation": "その小説は、よく知られた成長物語を巧みに変形した作品だ。"
      },
      {
        "example_id": "ex-0f2946e92a43",
        "example": "The store adjusts its stock for seasonal variation in demand.",
        "translation": "その店は需要の季節変動に合わせて在庫を調整する。"
      },
      {
        "example_id": "ex-0d6e4e25fe72",
        "example": "She is preparing a classical ballet variation for the competition.",
        "translation": "彼女はコンクールに向けてクラシック・バレエのソロ演目を準備している。"
      },
      {
        "example_id": "ex-571e24dbc8a5",
        "example": "The pianist chose a demanding theme and variations for the recital.",
        "translation": "そのピアニストはリサイタルに、難度の高い主題と変奏曲を選んだ。"
      },
      {
        "example_id": "ex-8d1277092bc5",
        "example": "Genetic variation within a species can affect its response to disease.",
        "translation": "種内の遺伝的変異は、病気への反応に影響することがある。"
      },
      {
        "example_id": "ex-10d46c567564",
        "example": "The study found substantial genetic variation among individuals in their response to the vaccine.",
        "translation": "その研究では、ワクチンへの反応に個体間の大きな遺伝的差が見つかった。"
      },
      {
        "example_id": "ex-f846a9be81c3",
        "example": "The team tested a variation on the original method.",
        "translation": "そのチームは元の方法を土台にした変形版を試した。"
      },
      {
        "example_id": "ex-1ffbf764a2a6",
        "example": "The study found wide variation between schools in the use of digital devices.",
        "translation": "その研究では、デジタル機器の使用について学校間に大きな差が見つかった。"
      },
      {
        "example_id": "ex-c51ae9ac1cd4",
        "example": "The survey found considerable variation according to age and region.",
        "translation": "その調査では、年齢と地域によってかなりの差が見つかった。"
      },
      {
        "example_id": "ex-6b6bb5188598",
        "example": "The plant samples show genetic variation in leaf shape and size within a species.",
        "translation": "その種の植物試料では、葉の形と大きさに遺伝的変異が見られる。"
      },
      {
        "example_id": "ex-d37651a5b546",
        "example": "The study measured genetic variation within a population in wing length over several generations.",
        "translation": "その研究は、数世代にわたる集団内の翼長における遺伝的変異を測定した。"
      },
      {
        "example_id": "ex-3a34f4d1c4ca",
        "example": "She played the final variation with remarkable clarity.",
        "translation": "彼女は最後の変奏を見事な明瞭さで演奏した。"
      },
      {
        "example_id": "ex-171de090e30a",
        "example": "This soup is a lighter variation on a traditional winter dish.",
        "translation": "このスープは伝統的な冬の料理をより軽めにしたアレンジだ。"
      },
      {
        "example_id": "ex-3735aa95af6d",
        "example": "Genetic variation in drug response should be considered when interpreting the results.",
        "translation": "結果を解釈する際は、薬物反応における遺伝的変異を考慮すべきだ。"
      },
      {
        "example_id": "ex-60f6e83c02b9",
        "example": "This version is a useful variation on the original design.",
        "translation": "この版は元の設計を土台にした有用なアレンジだ。"
      },
      {
        "example_id": "ex-a53f15416d79",
        "example": "The program included variations on a theme by Mozart.",
        "translation": "そのプログラムにはモーツァルトの主題による変奏曲が含まれていた。"
      },
      {
        "example_id": "ex-b7caf3b721ff",
        "example": "The contract includes a variation clause covering changes to the scope of work.",
        "translation": "その契約には作業範囲の変更を対象とする契約変更条項が含まれている。"
      },
      {
        "example_id": "ex-5dcd3c212d45",
        "example": "The forecast takes seasonal variation into account.",
        "translation": "その予測は季節変動を考慮に入れている。"
      },
      {
        "example_id": "ex-e9f1d5281254",
        "example": "The revised procedure shows only slight variation from the standard procedure in its timing.",
        "translation": "改訂された手順は、実施時間の点で標準手順からわずかに異なる。"
      },
      {
        "example_id": "ex-f6008df82cbd",
        "example": "Many theories on punishment are variations on a theme.",
        "translation": "刑罰についての多くの理論は、同じ主題を変形した展開である。"
      },
      {
        "example_id": "ex-80aa8ade2945",
        "example": "The engineer issued a variation order for the additional work.",
        "translation": "請負業者は追加工事について変更指示書を提出した。"
      },
      {
        "example_id": "ex-649ba093736a",
        "example": "The pianist performed a variation on the melody with subtle rhythmic changes.",
        "translation": "そのピアニストは、リズムを微妙に変えたその旋律の一つの変奏を演奏した。"
      },
      {
        "example_id": "ex-55962cb7190e",
        "example": "The parties signed a variation to the contract extending the delivery date.",
        "translation": "当事者は納期を延長する契約変更書に署名した。"
      },
      {
        "example_id": "ex-50e98977f38f",
        "example": "The graph shows the variation of temperature with altitude.",
        "translation": "そのグラフは高度に伴う温度の変化を示している。"
      },
      {
        "example_id": "ex-bd74363fa0ec",
        "example": "The two paint samples showed only slight variation in color.",
        "translation": "その2つの塗料見本には色のわずかな違いしか見られなかった。"
      },
      {
        "example_id": "ex-6d8dd931984e",
        "example": "The dancer performed her variation with controlled, precise movements.",
        "translation": "そのダンサーは抑制の効いた正確な動きでソロ演目を踊った。"
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
  "source_artifact_sha256": "3360995ffadddf9cf97c35ab26f6175e7704cfb8dd9a995a98542495174b9ca3",
  "normalized_input_sha256": "a1528dd2feb90918800d1cc13fb7f0bbca6bdbe712a62568548a90349eea56e9"
}
```
