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
  "input_body_sha256": "a1ba2a3e8f2a29df70219a3e1669883e2e9020b77884a88290a797075c286f76",
  "stage1_request_sha256": "65a828708808900e466cccaaa1838a7187e639430f9d12efc6a54c833285e7b1",
  "blind_record_sha256": "7b3d94a76f36d42773aa300f6caddf238aa512b5dca5c055082e78c82479d354",
  "alignment_key_sha256": "a43fdcbb2d64f3f6ed33c330d3518c9c8649f5c19fa13a7f3d0f846d110e0e71",
  "blind_attribution_record": {
    "schema_version": "example_attribution_blind_record_v1",
    "pass_id": "example-attribution",
    "input_body_sha256": "a1ba2a3e8f2a29df70219a3e1669883e2e9020b77884a88290a797075c286f76",
    "blind_request_sha256": "65a828708808900e466cccaaa1838a7187e639430f9d12efc6a54c833285e7b1",
    "recorded_at": "2026-09-24T13:32:45.838Z",
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-6",
      "ingested_by": "orchestrator",
      "agent_id": "s21-example-attribution-independent-01",
      "source_response": {
        "path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-21/responses/source_responses/e11e81a68b2a9d3bf96bf8a91666411de6bb44c7beef1a094d5b81f30c9b7d53.json",
        "sha256": "e11e81a68b2a9d3bf96bf8a91666411de6bb44c7beef1a094d5b81f30c9b7d53"
      }
    },
    "attributions": [
      {
        "example_id": "ex-1f9874709c17",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "were arrested on suspicion of fraud"
        ],
        "rationale": "The exact cue “were arrested on suspicion of fraud” frames the arrested people as suspected of committing that offense, which is sense 1. Sense 3 could describe a belief that fraud occurred, but it does not account for the person-directed ground for arrest expressed by this construction."
      },
      {
        "example_id": "ex-c86e69a4d8d2",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "cast suspicion on the clerk",
          "who had access to the report"
        ],
        "rationale": "The exact cue “cast suspicion on the clerk” makes the clerk the person implicated by the altered timestamp; the access clause further connects that person to the possible act. Sense 2 could mean broad distrust of the clerk, but this construction in context points to the clerk's possible responsibility for wrongdoing, rather than a general wary attitude."
      },
      {
        "example_id": "ex-fca175961862",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "a guard had stolen the missing laptops",
          "confirmed the manager's suspicions"
        ],
        "rationale": "The exact cue “a guard had stolen the missing laptops” attributes a concrete crime to a particular person, making this sense 1. Sense 3 can describe a tentative proposition, but this clause specifically treats the guard as the person suspected of committing the theft."
      },
      {
        "example_id": "ex-848d43640b65",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:003"
        ],
        "discriminating_terms": [
          "that the delay was caused by a technical problem"
        ],
        "rationale": "The exact cue “that the delay was caused by a technical problem” supplies a causal proposition the speakers tentatively believe, which is sense 3. Sense 2 would be a general attitude of mistrust toward a person or source; the sentence instead states a belief about what caused the delay."
      },
      {
        "example_id": "ex-063398bcff6c",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:003"
        ],
        "discriminating_terms": [
          "that everyone already knew the answer"
        ],
        "rationale": "The exact cue “that everyone already knew the answer” supplies the content of a hunch, which is sense 3. Sense 2 would express distrust toward someone, but “everyone” is part of the proposition being guessed about, not the target of a wary attitude."
      },
      {
        "example_id": "ex-64aaff02f09c",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:004"
        ],
        "discriminating_terms": [
          "a suspicion of disappointment in his voice"
        ],
        "rationale": "The exact cue “a suspicion of disappointment in his voice” describes a faintly detectable emotional quality, which is sense 4. Sense 3 would be a belief that disappointment exists, but this phrase describes what the voice conveys rather than anyone's belief."
      },
      {
        "example_id": "ex-d62d25c12777",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:002"
        ],
        "discriminating_terms": [
          "greeted with some suspicion"
        ],
        "rationale": "The exact cue “greeted with some suspicion” describes a guarded reception of the system, which is sense 2. Sense 3 would require a tentative proposition about what is true; this phrase gives an attitude toward the system instead."
      },
      {
        "example_id": "ex-e71e631abd89",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "came under suspicion",
          "when several invoices disappeared"
        ],
        "rationale": "The exact cue “came under suspicion” places the employee among the possible responsible parties after invoices disappear, which is sense 1. Sense 2 could express general distrust of the employee, but this event-linked construction frames possible responsibility for an act, not broad mistrust."
      },
      {
        "example_id": "ex-a5bf2c6ace9f",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:003"
        ],
        "discriminating_terms": [
          "that the battery was failing"
        ],
        "rationale": "The exact cue “that the battery was failing” is a proposition about the battery's condition, making this sense 3. Sense 1 would concern a person suspected of wrongdoing, but no person is accused of an act here."
      },
      {
        "example_id": "ex-bf2f306bc58d",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:002"
        ],
        "discriminating_terms": [
          "cast suspicion on the reliability of the company's explanation"
        ],
        "rationale": "The exact cue “cast suspicion on the reliability of the company's explanation” targets the trustworthiness of information, which is sense 2. Sense 1 would accuse a person of an offense; the sentence instead questions the explanation's reliability."
      },
      {
        "example_id": "ex-7c7d21b50785",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:004"
        ],
        "discriminating_terms": [
          "white with a suspicion of blue"
        ],
        "rationale": "The exact cue “white with a suspicion of blue” describes a slight color quality in the walls, which is sense 4. Sense 3 would be a tentative belief that the walls are blue, but this is an appearance description, not a belief."
      },
      {
        "example_id": "ex-f9b4953df54e",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:004"
        ],
        "discriminating_terms": [
          "a suspicion of a smile appeared",
          "at the corner of her mouth"
        ],
        "rationale": "The exact cue “a suspicion of a smile appeared” describes a barely visible expression, which is sense 4. Sense 3 would be a hunch held by someone, whereas “appeared” and the stated location at the mouth describe a visible trace."
      },
      {
        "example_id": "ex-5fb863dfe3e9",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:004"
        ],
        "discriminating_terms": [
          "a suspicion of citrus",
          "made it taste fresher"
        ],
        "rationale": "The exact cue “a suspicion of citrus” names a faint flavor in the sauce, which is sense 4; the following taste effect confirms that the phrase describes flavor. Sense 3 would be someone's uncertain belief that citrus is present, but no belief is expressed."
      },
      {
        "example_id": "ex-09a185870588",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:002"
        ],
        "discriminating_terms": [
          "viewed the sudden policy change with suspicion"
        ],
        "rationale": "The exact cue “viewed the sudden policy change with suspicion” attributes a wary attitude toward the policy, which is sense 2. Sense 3 would express a tentative proposition, but no proposition is stated; the phrase describes how residents regard the change."
      },
      {
        "example_id": "ex-8b28e344e8d8",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:003"
        ],
        "discriminating_terms": [
          "that the meeting will finish earlier than planned"
        ],
        "rationale": "The exact cue “that the meeting will finish earlier than planned” states a prediction the speaker thinks may be true, which is sense 3. Sense 2 would be mistrust toward a person, source, or idea; this complement is instead a future-event proposition."
      },
      {
        "example_id": "ex-a101437f6a9a",
        "classification": "unique",
        "candidate_sense_ids": [
          "sense:001"
        ],
        "discriminating_terms": [
          "remained under suspicion until the records were checked"
        ],
        "rationale": "The exact cue “remained under suspicion until the records were checked” presents the contractor as a possible responsible party pending an evidence check, which is sense 1. Sense 2 could mean ongoing distrust of the contractor, but the under-suspicion construction and evidence-based resolution indicate suspicion of specific wrongdoing."
      },
      {
        "example_id": "ex-a73e1268df05",
        "classification": "ambiguous",
        "candidate_sense_ids": [
          "sense:001",
          "sense:003"
        ],
        "discriminating_terms": [],
        "rationale": "The exact sentence “The unexplained transfer of client funds aroused suspicion of fraud among the auditors.” supports two readings: sense 1, if the auditors suspect an unspecified person committed fraud, and sense 3, if they infer that the unexplained transfer itself was fraudulent. The sentence does not name a suspected perpetrator, so it does not resolve whether the suspicion is a person-directed accusation or a tentative proposition."
      }
    ]
  },
  "alignment_key": {
    "schema_version": "example_attribution_alignment_key_v1",
    "pass_id": "example-attribution",
    "input_body_sha256": "a1ba2a3e8f2a29df70219a3e1669883e2e9020b77884a88290a797075c286f76",
    "blind_request_sha256": "65a828708808900e466cccaaa1838a7187e639430f9d12efc6a54c833285e7b1",
    "shuffle_seed": "a1ba2a3e8f2a29df70219a3e1669883e2e9020b77884a88290a797075c286f76",
    "examples": [
      {
        "example_id": "ex-a73e1268df05",
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
        "example_id": "ex-1f9874709c17",
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
        "example_id": "ex-a101437f6a9a",
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
        "example_id": "ex-e71e631abd89",
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
        "example_id": "ex-c86e69a4d8d2",
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
        "example_id": "ex-fca175961862",
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
        "example_id": "ex-09a185870588",
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
        "example_id": "ex-d62d25c12777",
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
        "example_id": "ex-bf2f306bc58d",
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
        "example_id": "ex-8b28e344e8d8",
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
        "example_id": "ex-063398bcff6c",
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
        "example_id": "ex-848d43640b65",
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
        "example_id": "ex-a5bf2c6ace9f",
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
        "example_id": "ex-7c7d21b50785",
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
        "example_id": "ex-5fb863dfe3e9",
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
        "example_id": "ex-64aaff02f09c",
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
        "example_id": "ex-f9b4953df54e",
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
        "text": "on suspicion of theft は「窃盗の疑いを理由に」という定型表現である。under suspicion は、Oxford の説明では不正をしたのではないかと疑われている状態を表す。that節の形だけでなく意味上の焦点を見る。話者が節全体の真偽を暫定的に推測する用法は語義3、人に不正行為の容疑を向ける用法は語義1に置く。accusation や allegation は類義語ではなく、誰かが不正をしたという主張・告発を指す関連語である。"
      },
      {
        "sense_id": "sense:002",
        "line": 118,
        "text": "with suspicion は「疑いの目で、信用せずに」という態度を表す。Oxford と American Heritage はこの語義を distrust / lack of confidence と説明する。Merriam-Webster は suspicion が真実性・現実性・公正さ・信頼性への信頼の薄さを強調すると説明し、mistrust は疑いに基づく信頼の欠如を強調するとしている。"
      },
      {
        "sense_id": "sense:003",
        "line": 168,
        "text": "この語義では内容は悪いことに限らず、I have a suspicion that she may surprise us with good news. のように中立・肯定的な内容についても「そうではないかという気」を表せる。that節の内容が犯罪・不正かどうかだけで語義を分けない。節全体を真偽未確定の命題として推し量る用法は語義3、特定の人に犯罪・不正の容疑を向ける用法は語義1として説明する。suspicion that ... の that は内容を導く接続詞で、suspicion of ... の of は名詞句を取る。a sneaking suspicion の sneaking はここでは「盗み歩く」という直訳ではなく、表立って確信してはいないが心の中にある感覚を表す。"
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
