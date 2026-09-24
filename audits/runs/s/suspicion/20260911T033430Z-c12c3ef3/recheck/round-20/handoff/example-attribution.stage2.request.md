# Independent review handoff

Stage: `checker_passes/example-attribution-stage2`

The stage-1 blind record is saved and provenance-bound. Continue with the same reviewer id and context. Read only this packet and the supplied checker prompt. The alignment key and usage notes are now disclosed; do not revise the blind record. Compare each saved blind classification against the actual assigned sense and apply the prompt’s stage-2 rules. Save a separate response at `example-attribution.stage2.response.raw.json` containing schema_version `example_attribution_stage2_response_v1`, pass_id, input_body_sha256, stage1_request_sha256, blind_record_sha256, alignment_key_sha256, aligned_at (after stage1 recorded_at), top-level reviewer metadata (same id/model as stage1, ingested_by human), findings, and unrouted_observations. Each finding must use the prompt taxonomy/location/severity/rationale/suggested_direction contract.

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
  "schema_version": "example_attribution_stage2_request_v1",
  "pass_id": "example-attribution",
  "input_body_sha256": "22115ff16b934a7bee72be158df65dd1569ca9a64c670adb9cd408a03b504ebd",
  "stage1_request_sha256": "bee6ab024458432e99ce0e67c2095681c2ff0e5e7dc3f3de7445e9fa45b3a6d4",
  "blind_record_sha256": "0f2d1dbbd48a4adef7498b78c8f2c775c34ee1e39bea63b09016a3f2cc227d93",
  "alignment_key_sha256": "5f55414a53854fd0f2379f56db745fd5261f442fcd7f89c94c6ce3c080328373",
  "blind_attribution_record": {
    "schema_version": "example_attribution_blind_record_v1",
    "pass_id": "example-attribution",
    "input_body_sha256": "22115ff16b934a7bee72be158df65dd1569ca9a64c670adb9cd408a03b504ebd",
    "blind_request_sha256": "bee6ab024458432e99ce0e67c2095681c2ff0e5e7dc3f3de7445e9fa45b3a6d4",
    "recorded_at": "2026-09-24T13:17:41Z",
    "reviewer": {
      "mode": "handoff",
      "declared_model": "GPT-6",
      "ingested_by": "orchestrator",
      "agent_id": "agent-round20-example-attribution-20260924-7f84b2ae",
      "source_response": {
        "path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-20/responses/source_responses/a5ed70f03c3f8168827e70c64a89847ac56a9c98ff0487738c9e6561528897a5.json",
        "sha256": "a5ed70f03c3f8168827e70c64a89847ac56a9c98ff0487738c9e6561528897a5"
      }
    },
    "attributions": [
      {
        "example_id": "ex-060a5192124c",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "remained under suspicion",
          "until the records were checked"
        ],
        "rationale": "The exact cue \"remained under suspicion until the records were checked\" presents a person as a suspect pending evidence, which selects sense 1. Sense 2 could be general wariness toward a contractor, but this construction ties suspicion to checking records to resolve a possible allegation."
      },
      {
        "example_id": "ex-634a364d45b4",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:002"
        ],
        "discriminating_terms": [
          "viewed the sudden policy change with suspicion"
        ],
        "rationale": "The exact cue \"viewed the sudden policy change with suspicion\" describes a wary attitude toward the decision, selecting sense 2. Sense 1 would require the change to be suspected of a specific crime or dishonest act, and the sentence names none."
      },
      {
        "example_id": "ex-b9e6473dfcfd",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:004"
        ],
        "discriminating_terms": [
          "a suspicion of citrus",
          "made it taste fresher"
        ],
        "rationale": "The exact cue \"a suspicion of citrus\" is in a sauce-and-taste frame, and \"made it taste fresher\" confirms a faint flavor note, selecting sense 4. Sense 3 would be a tentative belief about a proposition; this sentence describes a sensory quality the sauce had."
      },
      {
        "example_id": "ex-7c75bf50b419",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:003"
        ],
        "discriminating_terms": [
          "had a sneaking suspicion that everyone already knew the answer"
        ],
        "rationale": "The exact cue \"had a sneaking suspicion that everyone already knew the answer\" presents an unconfirmed proposition about a state of knowledge, selecting sense 3. Sense 2 would express distrust of people or their reliability, which this sentence does not say."
      },
      {
        "example_id": "ex-1e6c5d63abbd",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:003"
        ],
        "discriminating_terms": [
          "have a suspicion that the meeting will finish earlier than planned"
        ],
        "rationale": "The exact cue \"have a suspicion that the meeting will finish earlier than planned\" presents a conjecture about a non-criminal future event, selecting sense 3. Sense 2 would concern mistrust of a person, source, or motive, none of which is expressed."
      },
      {
        "example_id": "ex-ff889969af92",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:004"
        ],
        "discriminating_terms": [
          "white with a suspicion of blue"
        ],
        "rationale": "The exact cue \"white with a suspicion of blue\" describes a barely perceptible tint in the walls’ appearance, selecting sense 4. Sense 3 would be a conjecture about a proposition, whereas this phrase directly describes a color quality."
      },
      {
        "example_id": "ex-82a69bbd2c42",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:002"
        ],
        "discriminating_terms": [
          "cast suspicion on the reliability of the company's explanation"
        ],
        "rationale": "The exact cue \"cast suspicion on the reliability of the company's explanation\" targets the explanation’s trustworthiness, selecting sense 2. Sense 1 would allege a particular crime or dishonest act; the sentence questions reliability without naming one."
      },
      {
        "example_id": "ex-5738efb14b08",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:004"
        ],
        "discriminating_terms": [
          "a suspicion of disappointment in his voice"
        ],
        "rationale": "The exact cue \"a suspicion of disappointment in his voice\" presents disappointment as a faint audible quality, selecting sense 4. Sense 3 could be a guess about his emotion, but the phrase describes a slight trace in the voice rather than a proposition someone entertains."
      },
      {
        "example_id": "ex-b23f76ce6acb",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:004"
        ],
        "discriminating_terms": [
          "A suspicion of a smile appeared at the corner of her mouth"
        ],
        "rationale": "The exact cue \"A suspicion of a smile appeared at the corner of her mouth\" describes a barely perceptible expression, selecting sense 4. Sense 3 would be a conjecture about whether she smiled; this sentence describes the faint smile itself."
      },
      {
        "example_id": "ex-05d22e8ff3bb",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "arrested on suspicion of fraud"
        ],
        "rationale": "The exact cue \"arrested on suspicion of fraud\" states the legal basis for arrest and names criminal wrongdoing, selecting sense 1. Sense 3 can express a tentative belief about a fact, but this frame is specifically an allegation of fraud."
      },
      {
        "example_id": "ex-75549b1c1e8d",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:003"
        ],
        "discriminating_terms": [
          "confirmed her suspicion that the battery was failing"
        ],
        "rationale": "The exact cue \"confirmed her suspicion that the battery was failing\" is a hypothesis about a non-criminal condition later verified by tests, selecting sense 3. Sense 2 would express mistrust of a person or source, which is absent here."
      },
      {
        "example_id": "ex-cce722f090e3",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "altered timestamp",
          "cast suspicion on the clerk who had access to the report"
        ],
        "rationale": "The exact cue \"altered timestamp cast suspicion on the clerk who had access to the report\" links the clerk to possible tampering, selecting sense 1. Sense 2 would be generalized distrust; the access-to-alteration relation makes this directed suspicion of wrongdoing."
      },
      {
        "example_id": "ex-21d3d765d8c6",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:002"
        ],
        "discriminating_terms": [
          "The new monitoring system was initially greeted with some suspicion"
        ],
        "rationale": "The exact cue \"The new monitoring system was initially greeted with some suspicion\" describes a wary reception, selecting sense 2. Sense 1 would require a suspected crime or dishonest act by the system or its makers, and none is stated."
      },
      {
        "example_id": "ex-0a6a90980f29",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:003"
        ],
        "discriminating_terms": [
          "a strong suspicion that the delay was caused by a technical problem"
        ],
        "rationale": "The exact cue \"a strong suspicion that the delay was caused by a technical problem\" is a conjecture about a non-criminal cause, selecting sense 3. Sense 2 would be mistrust of a source or motive, neither of which appears in this sentence."
      },
      {
        "example_id": "ex-98fddba364aa",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "unexplained transfer of client funds",
          "suspicion of fraud"
        ],
        "rationale": "The exact cue \"unexplained transfer of client funds aroused suspicion of fraud among the auditors\" explicitly names fraud as suspected wrongdoing, selecting sense 1. Sense 3 would concern a non-criminal factual conjecture and cannot account for the stated fraud allegation."
      },
      {
        "example_id": "ex-6ec1f647d3f8",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "came under suspicion",
          "when several invoices disappeared"
        ],
        "rationale": "The exact cue \"The employee came under suspicion when several invoices disappeared\" makes the employee a suspect in connection with a possible loss-related act, selecting sense 1. Sense 2 would only express general wariness and would not capture this event-linked suspicion."
      },
      {
        "example_id": "ex-4d931abbe0ce",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "confirmed the manager's suspicions that a guard had stolen the missing laptops"
        ],
        "rationale": "The exact cue \"confirmed the manager's suspicions that a guard had stolen the missing laptops\" explicitly attributes theft to the guard, selecting sense 1. Sense 3 is excluded because this is a suspicion of criminal conduct, not a non-criminal situation."
      }
    ]
  },
  "alignment_key": {
    "schema_version": "example_attribution_alignment_key_v1",
    "pass_id": "example-attribution",
    "input_body_sha256": "22115ff16b934a7bee72be158df65dd1569ca9a64c670adb9cd408a03b504ebd",
    "blind_request_sha256": "bee6ab024458432e99ce0e67c2095681c2ff0e5e7dc3f3de7445e9fa45b3a6d4",
    "shuffle_seed": "22115ff16b934a7bee72be158df65dd1569ca9a64c670adb9cd408a03b504ebd",
    "examples": [
      {
        "example_id": "ex-98fddba364aa",
        "assigned_sense_id": "sense:001",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 52,
          "line_end": 52,
          "exact_quote": "例: The unexplained transfer of client funds aroused suspicion of fraud among the auditors.  "
        },
        "source_example_id": "example:001"
      },
      {
        "example_id": "ex-05d22e8ff3bb",
        "assigned_sense_id": "sense:001",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 57,
          "line_end": 57,
          "exact_quote": "例: Two people were arrested on suspicion of fraud after the investigation.  "
        },
        "source_example_id": "example:002"
      },
      {
        "example_id": "ex-060a5192124c",
        "assigned_sense_id": "sense:001",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 62,
          "line_end": 62,
          "exact_quote": "例: The contractor remained under suspicion until the records were checked.  "
        },
        "source_example_id": "example:003"
      },
      {
        "example_id": "ex-6ec1f647d3f8",
        "assigned_sense_id": "sense:001",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 67,
          "line_end": 67,
          "exact_quote": "例: The employee came under suspicion when several invoices disappeared.  "
        },
        "source_example_id": "example:004"
      },
      {
        "example_id": "ex-cce722f090e3",
        "assigned_sense_id": "sense:001",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 72,
          "line_end": 72,
          "exact_quote": "例: The altered timestamp cast suspicion on the clerk who had access to the report.  "
        },
        "source_example_id": "example:005"
      },
      {
        "example_id": "ex-4d931abbe0ce",
        "assigned_sense_id": "sense:001",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 77,
          "line_end": 77,
          "exact_quote": "例: The security footage confirmed the manager's suspicions that a guard had stolen the missing laptops.  "
        },
        "source_example_id": "example:006"
      },
      {
        "example_id": "ex-634a364d45b4",
        "assigned_sense_id": "sense:002",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 105,
          "line_end": 105,
          "exact_quote": "例: Residents viewed the sudden policy change with suspicion.  "
        },
        "source_example_id": "example:007"
      },
      {
        "example_id": "ex-21d3d765d8c6",
        "assigned_sense_id": "sense:002",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 110,
          "line_end": 110,
          "exact_quote": "例: The new monitoring system was initially greeted with some suspicion.  "
        },
        "source_example_id": "example:008"
      },
      {
        "example_id": "ex-82a69bbd2c42",
        "assigned_sense_id": "sense:002",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 115,
          "line_end": 115,
          "exact_quote": "例: The discrepancy cast suspicion on the reliability of the company's explanation.  "
        },
        "source_example_id": "example:009"
      },
      {
        "example_id": "ex-1e6c5d63abbd",
        "assigned_sense_id": "sense:003",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 150,
          "line_end": 150,
          "exact_quote": "例: I have a suspicion that the meeting will finish earlier than planned.  "
        },
        "source_example_id": "example:010"
      },
      {
        "example_id": "ex-7c75bf50b419",
        "assigned_sense_id": "sense:003",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 155,
          "line_end": 155,
          "exact_quote": "例: She had a sneaking suspicion that everyone already knew the answer.  "
        },
        "source_example_id": "example:011"
      },
      {
        "example_id": "ex-0a6a90980f29",
        "assigned_sense_id": "sense:003",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 160,
          "line_end": 160,
          "exact_quote": "例: We had a strong suspicion that the delay was caused by a technical problem.  "
        },
        "source_example_id": "example:012"
      },
      {
        "example_id": "ex-75549b1c1e8d",
        "assigned_sense_id": "sense:003",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 165,
          "line_end": 165,
          "exact_quote": "例: The test results confirmed her suspicion that the battery was failing.  "
        },
        "source_example_id": "example:013"
      },
      {
        "example_id": "ex-ff889969af92",
        "assigned_sense_id": "sense:004",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 200,
          "line_end": 200,
          "exact_quote": "例: The walls were white with a suspicion of blue in the evening light.  "
        },
        "source_example_id": "example:014"
      },
      {
        "example_id": "ex-b9e6473dfcfd",
        "assigned_sense_id": "sense:004",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 205,
          "line_end": 205,
          "exact_quote": "例: The sauce had a suspicion of citrus that made it taste fresher.  "
        },
        "source_example_id": "example:015"
      },
      {
        "example_id": "ex-5738efb14b08",
        "assigned_sense_id": "sense:004",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 210,
          "line_end": 210,
          "exact_quote": "例: There was a suspicion of disappointment in his voice.  "
        },
        "source_example_id": "example:016"
      },
      {
        "example_id": "ex-b23f76ce6acb",
        "assigned_sense_id": "sense:004",
        "anchor": {
          "section": "collocations_examples",
          "line_start": 215,
          "line_end": 215,
          "exact_quote": "例: A suspicion of a smile appeared at the corner of her mouth.  "
        },
        "source_example_id": "example:017"
      }
    ],
    "sense_usage_notes": [
      {
        "sense_id": "sense:001",
        "line": 80,
        "text": "on suspicion of theft は「窃盗の疑いを理由に」という定型表現である。under suspicion は、Oxford の説明では不正をしたのではないかと疑われている状態を表す。accusation や allegation は類義語ではなく、誰かが不正をしたという主張・告発を指す関連語である。"
      },
      {
        "sense_id": "sense:002",
        "line": 118,
        "text": "with suspicion は「疑いの目で、信用せずに」という態度を表す。Oxford と American Heritage はこの語義を distrust / lack of confidence と説明する。Merriam-Webster は suspicion が真実性・現実性・公正さ・信頼性への信頼の薄さを強調すると説明し、mistrust は疑いに基づく信頼の欠如を強調するとしている。"
      },
      {
        "sense_id": "sense:003",
        "line": 168,
        "text": "この語義では内容は悪いことに限らず、I have a suspicion that she may surprise us with good news. のように中立・肯定的な内容についても「そうではないかという気」を表せる。本記事では、that節が特定の人の犯罪・不正行為を述べる用例を語義1に置き、語義3はそれ以外の事実・状況への推測に用いる。suspicion that ... の that は内容を導く接続詞で、suspicion of ... の of は名詞句を取る。a sneaking suspicion の sneaking はここでは「盗み歩く」という直訳ではなく、表立って確信してはいないが心の中にある感覚を表す。"
      },
      {
        "sense_id": "sense:004",
        "line": 218,
        "text": "この a suspicion of ... は「～を疑うこと」ではなく、「～がほんの少し存在すること」である。"
      }
    ]
  },
  "required_output_schema": "example_attribution_stage2_response_v1"
}
```
