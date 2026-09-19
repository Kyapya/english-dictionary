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
  "input_body_sha256": "6bf439cde2a5a009f8e4e4d27f7041f7af5c66dd15e9e51aaf59bfb705b46752",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 40,
        "label": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "definition": "答え、決定、計画、日付、合意、意図などが、曖昧な候補や一時的な案ではなく、内容として定まり、変更される可能性が低いことを表す。必ずしも今後絶対に変更できないという意味ではなく、現時点で決定・約束・判断が明確になっていることに焦点がある。"
      },
      {
        "sense_id": "sense:002",
        "line": 154,
        "label": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "definition": "変化、差、効果、兆候、利点などが、観察や比較によって実際に認められるほど明瞭・顕著であることを表す。必ずしも論理的に証明済み、絶対に疑いがないという意味ではなく、話し手が変化や特徴をはっきり認識しているという評価を含むことがある。"
      },
      {
        "sense_id": "sense:003",
        "line": 268,
        "label": "3. 【形容詞・限定用法】具体的な、特定の",
        "definition": "数量、期間、範囲、時点、形、情報などに明確な境界や内容があり、漠然としたものではないことを表す。特定の対象を指す場合でも、文脈上その対象を識別できるという文法上の意味とは異なり、ここでは内容・範囲・条件が具体的に定まっていることに焦点がある。"
      },
      {
        "sense_id": "sense:004",
        "line": 384,
        "label": "4. 【形容詞・文法用語】定の、特定できる",
        "definition": "文法で、名詞句の指示対象が、既出、状況上の唯一性、修飾語、共有知識などによって聞き手・読み手に特定可能であることを表す。英語では the が definite article「定冠詞」であり、対象が必ず世界に一つしかないこと、単数であること、以前に必ず言及されたことだけを意味するわけではない。"
      },
      {
        "sense_id": "sense:005",
        "line": 474,
        "label": "5. 【形容詞・植物学】有限の、定数の",
        "definition": "植物学で、花器官の数が一定で、通常は20未満で花弁数の倍数になること、または花序の主軸が花で終わり成長に限りがあることを表す専門用法である。一般語の「確実な」ではなく、数や成長が定まっているという意味で、definite inflorescence は determinate／cymose inflorescence に当たる。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-d644a79b4b50",
        "example": "Sleep has a definite effect on how well people remember new information.",
        "translation": "睡眠は、人が新しい情報をどれだけよく覚えるかに明確な影響を及ぼす。"
      },
      {
        "example_id": "ex-54354c2cfdf7",
        "example": "Do you know anything definite about when the train will leave?",
        "translation": "列車がいつ出るかについて、何か確定した情報を知っていますか。"
      },
      {
        "example_id": "ex-6c9f83869c1a",
        "example": "Please be definite about your position before the meeting begins.",
        "translation": "会議が始まる前に、自分の立場を明確にしてください。"
      },
      {
        "example_id": "ex-f79c1f44a25b",
        "example": "The species has definite stamens, usually in a fixed multiple of the number of petals.",
        "translation": "その種には、通常、花弁数の決まった倍数になる定数の雄しべがある。"
      },
      {
        "example_id": "ex-988fa8138f86",
        "example": "The area under the curve can be calculated with a definite integral.",
        "translation": "曲線の下の面積は定積分で計算できる。"
      },
      {
        "example_id": "ex-fe878351926f",
        "example": "There is a definite difference between the two versions of the report.",
        "translation": "その報告書の二つの版には明らかな違いがある。"
      },
      {
        "example_id": "ex-e74c8604e503",
        "example": "The machine requires a definite amount of oil to operate safely.",
        "translation": "その機械を安全に稼働させるには、一定量の油が必要だ。"
      },
      {
        "example_id": "ex-c19c393fc1ac",
        "example": "“The first person to arrive” is a definite description in this context.",
        "translation": "この文脈では、「最初に到着した人」は確定記述である。"
      },
      {
        "example_id": "ex-7ce341ec068a",
        "example": "The plant develops a definite inflorescence in which the main axis ends in a flower.",
        "translation": "その植物は、主軸が花で終わる有限花序を形成する。"
      },
      {
        "example_id": "ex-cbad99f14b3f",
        "example": "In English, the is the definite article used before singular and plural noun phrases.",
        "translation": "英語では the が、単数・複数の名詞句の前に使われる定冠詞である。"
      },
      {
        "example_id": "ex-710a72469623",
        "example": "We need definite information about the delivery schedule before placing the order.",
        "translation": "注文を出す前に、納入予定について具体的な情報が必要だ。"
      },
      {
        "example_id": "ex-cf17f361e524",
        "example": "We can see a definite change in customer behavior after the price increase.",
        "translation": "値上げ後、顧客の行動に明らかな変化が見られる。"
      },
      {
        "example_id": "ex-03de5fdb663a",
        "example": "The grant requires a definite commitment to complete the project.",
        "translation": "その助成金には、プロジェクトを完了するという明確な確約が必要だ。"
      },
      {
        "example_id": "ex-3f4a42fc3e7a",
        "example": "Her reply was a definite no, so we stopped asking.",
        "translation": "彼女の返事は明確な拒否だったので、私たちは尋ねるのをやめた。"
      },
      {
        "example_id": "ex-3baa53008352",
        "example": "The temperature must remain within definite limits during transport.",
        "translation": "輸送中、温度は明確に定められた範囲内に保たなければならない。"
      },
      {
        "example_id": "ex-d1a66af154f2",
        "example": "The lesson contrasts definite and indefinite articles in everyday sentences.",
        "translation": "その授業では、日常文における定冠詞と不定冠詞を対比している。"
      },
      {
        "example_id": "ex-e6bd75fc7b86",
        "example": "Only a definite number of students can join the laboratory tour.",
        "translation": "研究室見学に参加できる学生数には上限が決まっている。"
      },
      {
        "example_id": "ex-4963082548f4",
        "example": "A sudden drop in demand is a definite sign of weakening consumer confidence.",
        "translation": "需要の急減は、消費者信頼感が弱まっている明らかな兆候だ。"
      },
      {
        "example_id": "ex-7aca181fbedf",
        "example": "The plural noun phrase can still have a definite referent.",
        "translation": "複数名詞句でも、指示対象を特定できる場合がある。"
      },
      {
        "example_id": "ex-0ef42f0d5853",
        "example": "The organizers have not announced a definite date for the launch.",
        "translation": "主催者は発売の確定した日付をまだ発表していない。"
      },
      {
        "example_id": "ex-ac62dadef1df",
        "example": "Definite growth is common in some compact flowering plants.",
        "translation": "定限成長は、一部の小型の開花植物でよく見られる。"
      },
      {
        "example_id": "ex-7a5bec55a6f8",
        "example": "The new treatment produced a definite improvement in her symptoms.",
        "translation": "新しい治療によって、彼女の症状には明らかな改善が見られた。"
      },
      {
        "example_id": "ex-9f826d0b597c",
        "example": "A delay is a definite possibility if the storm continues.",
        "translation": "嵐が続けば、遅延は十分に現実的な可能性だ。"
      },
      {
        "example_id": "ex-632a1aa80843",
        "example": "No definite agreement had been reached by the end of the meeting.",
        "translation": "会議の終了時までに、確定した合意は成立していなかった。"
      },
      {
        "example_id": "ex-80295151595e",
        "example": "The shorter route offers a definite advantage during the winter.",
        "translation": "その短い経路は冬の間、明確な利点をもたらす。"
      },
      {
        "example_id": "ex-913e366b7fe9",
        "example": "In “the book on the desk,” the whole phrase is a definite noun phrase.",
        "translation": "「机の上のその本」では、句全体が定名詞句である。"
      },
      {
        "example_id": "ex-e1ea66e065bb",
        "example": "We need a definite answer by Friday, not another tentative suggestion.",
        "translation": "私たちは金曜日までに、また別の仮案ではなく確定した答えを必要としている。"
      },
      {
        "example_id": "ex-4201b3530588",
        "example": "The crystals grow into a definite shape under controlled conditions.",
        "translation": "その結晶は、管理された条件下で一定の形に成長する。"
      },
      {
        "example_id": "ex-c07571476815",
        "example": "I have no definite plans for the weekend yet.",
        "translation": "私は週末の具体的な予定をまだ決めていない。"
      },
      {
        "example_id": "ex-408664ca911b",
        "example": "He left the room with a definite sense of relief.",
        "translation": "彼は明らかに安堵した様子で部屋を出た。"
      },
      {
        "example_id": "ex-6f6b80a13c65",
        "example": "The article makes a definite reference to the company’s earlier report.",
        "translation": "その記事は会社の以前の報告書を明確に指し示している。"
      },
      {
        "example_id": "ex-f9e1062fff34",
        "example": "The equipment may be rented for a definite period of six months.",
        "translation": "その設備は6か月という定められた期間、借りることができる。"
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
  "source_artifact_sha256": "6c4a9cb96ef979d6caee6685612f8a3af1eadb335e8d0d86ec675b47df5e2d67",
  "normalized_input_sha256": "7e4b4f3f98cbf8d0b55825ed257ad2b593a9a84f982e9eeef30c5dc3bf6bd87a"
}
```
