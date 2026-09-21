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
  "input_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 37,
        "label": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "definition": "計画、日程、合意、結論、説明、提案、識別などが、現時点では候補として置かれているものの、検討・交渉・確認が終わっておらず、後で変更または撤回される可能性があることを表す。単に「一時的」という期間の短さではなく、内容の確定性がまだ低いことに焦点がある。"
      },
      {
        "sense_id": "sense:002",
        "line": 144,
        "label": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "definition": "人の行動、声、表情、返答、提案などが、確信や自信を十分に示さず、様子をうかがいながら慎重に行われることを表す。単に静か・弱いという意味ではなく、失敗や拒否を恐れている、またはまだ慣れていないような不確かさが表れやすい。"
      },
      {
        "sense_id": "sense:003",
        "line": 251,
        "label": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "definition": "予約、契約、日程、出演枠などについて、正式な確定や契約が済む前に、仮のものとして記録・扱われる項目を表す。一般会話で広く使う名詞ではなく、複数形 tentatives を含む業務上・事務上の文脈で見られる低頻度用法である。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-3b4bb931b25e",
        "example": "There was a tentative knock on the office door.",
        "translation": "オフィスのドアをおそるおそるノックする音がした。"
      },
      {
        "example_id": "ex-7e90749261ad",
        "example": "The researchers presented their tentative findings at the workshop.",
        "translation": "研究者たちはワークショップで予備的な研究結果を発表した。"
      },
      {
        "example_id": "ex-b3211f3bcce5",
        "example": "She gave him a tentative smile before entering the unfamiliar room.",
        "translation": "彼女は見慣れない部屋に入る前、彼にためらいがちな笑顔を向けた。"
      },
      {
        "example_id": "ex-a9e1d65b98f2",
        "example": "The team offered a tentative explanation for the sudden drop in demand.",
        "translation": "チームは需要が急減したことについて暫定的な説明を示した。"
      },
      {
        "example_id": "ex-af604d5c1046",
        "example": "We have tentative plans for a short trip in October.",
        "translation": "私たちは10月に短い旅行をする仮の予定がある。"
      },
      {
        "example_id": "ex-47a3a5c7ee5c",
        "example": "The police made a tentative identification of the vehicle from the video.",
        "translation": "警察は映像からその車両を暫定的に特定した。"
      },
      {
        "example_id": "ex-9c3b3eaf3b37",
        "example": "The board tentatively approved the budget pending a legal review.",
        "translation": "取締役会は法務審査を条件として、その予算を暫定承認した。"
      },
      {
        "example_id": "ex-e515d547c5c6",
        "example": "She was tentative about speaking up in front of the whole team.",
        "translation": "彼女はチーム全員の前で発言することをためらっていた。"
      },
      {
        "example_id": "ex-dbcc08011cf0",
        "example": "The two sides reached a tentative agreement after three days of talks.",
        "translation": "両者は3日間の協議の後、暫定合意に達した。"
      },
      {
        "example_id": "ex-ae33ff16f90f",
        "example": "The child made a tentative attempt to join the other players.",
        "translation": "その子どもは、ほかの遊び仲間に加わろうとおそるおそる試みた。"
      },
      {
        "example_id": "ex-e9a00234528b",
        "example": "He tentatively suggested moving the meeting to Friday.",
        "translation": "彼は会議を金曜日に移してはどうかと、ためらいがちに提案した。"
      },
      {
        "example_id": "ex-cb6904de54b9",
        "example": "The company is taking tentative steps toward reducing its use of plastic.",
        "translation": "その会社はプラスチックの使用を減らすための最初の一歩を慎重に踏み出している。"
      },
      {
        "example_id": "ex-4233f7693f43",
        "example": "The producer asked us to hold the date as a tentative until Friday.",
        "translation": "プロデューサーは、金曜日まではその日を仮押さえとしておくよう私たちに頼んだ。"
      },
      {
        "example_id": "ex-a7928cfa4821",
        "example": "“Perhaps we should wait,” she said in a tentative voice.",
        "translation": "「待ったほうがよいかもしれません」と、彼女はためらいがちな声で言った。"
      },
      {
        "example_id": "ex-5f892f9d48e2",
        "example": "The theater listed the autumn dates as tentatives while it waited for the contracts.",
        "translation": "その劇場は契約を待つ間、秋の日程を暫定枠として記録した。"
      },
      {
        "example_id": "ex-493b3c8c5339",
        "example": "The airline released a tentative schedule for the new route.",
        "translation": "その航空会社は新路線の暫定的な運航予定を公表した。"
      },
      {
        "example_id": "ex-f5aa80685af9",
        "example": "The organizers set a tentative date for the conference in early May.",
        "translation": "主催者は会議の開催日を5月初旬の仮の日付として設定した。"
      },
      {
        "example_id": "ex-d31f9a9748a9",
        "example": "He gave a tentative answer because he had not checked the figures.",
        "translation": "彼は数字を確認していなかったので、自信のない返答をした。"
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
  "source_artifact_sha256": "73787b3811419d4af99b6764bcacbf9685ac18522d5e2b856009599ce8e20810",
  "normalized_input_sha256": "d717d446d31d139801bd8b7ef3f4ed6ab77b20173081a062aa5eb19538c637c9"
}
```
