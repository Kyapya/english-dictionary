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
  "input_body_sha256": "4ab58d0a9b82ee8b0ade3bc81ddbd1b7a34b2d50961f3dbe201fd02a0f6e5ab8",
  "input_sections": {
    "sense_structure": [
      {
        "sense_id": "sense:001",
        "line": 46,
        "label": "1. 【可算名詞】委員会、調査委員会、行政委員会",
        "definition": "政府や公的機関などから、特定分野の調査、監督、規制、助言を行う正式な権限と責任を与えられた人々の組織を表す。固有の機関名では Commission と大文字で書くことがある。"
      },
      {
        "sense_id": "sense:002",
        "line": 108,
        "label": "2. 【可算・不可算名詞】歩合、販売手数料",
        "definition": "商品やサービスの販売、契約成立などの成果に応じて、販売員や代理人へ支払われる報酬。売上額の一定割合であることが多いが、必ず割合とは限らない。"
      },
      {
        "sense_id": "sense:003",
        "line": 170,
        "label": "3. 【可算・不可算名詞】取扱手数料、仲介手数料",
        "definition": "銀行、証券会社、仲介業者などが、両替、売買、送金その他の取引を処理する対価として顧客に請求する金額。取引額の一定割合の場合も定額の場合もある。"
      },
      {
        "sense_id": "sense:004",
        "line": 220,
        "label": "4. 【可算名詞】正式な依頼、発注、依頼作品",
        "definition": "芸術作品、建築、文章、調査などを特定の人・組織に作成・実施してもらう正式な依頼または発注。文脈によって、その依頼を受けて制作された作品や、請け負った仕事そのものも指す。"
      },
      {
        "sense_id": "sense:005",
        "line": 277,
        "label": "5. 【不可算名詞・形式的】犯罪・不正行為を行うこと",
        "definition": "犯罪、違反、不正行為などを実行することを表す形式的な名詞用法。通常、the commission of 〈crime/offence/act〉という固定的な形で使う。"
      },
      {
        "sense_id": "sense:006",
        "line": 315,
        "label": "6. 【可算名詞・軍事】士官任命、士官の地位・辞令",
        "definition": "軍で士官としての階級と権限を正式に与える任命、その地位、またはそれを証明する文書を表す。一般的な入隊や配属そのものではない。"
      },
      {
        "sense_id": "sense:007",
        "line": 353,
        "label": "7. 【慣用的名詞句】就役中・稼働中／使用不能・任務不能",
        "definition": "in commission は船舶・設備などが正式に就役中、または使用可能な状態にあることを表す。out of commission は就役していない、故障などで使用できない、または人が負傷・病気で一時的に活動できない状態を表す。"
      },
      {
        "sense_id": "sense:008",
        "line": 412,
        "label": "8. 【他動詞】～を正式に依頼する、発注する",
        "definition": "人や組織に、作品の制作、報告書・調査の作成、設計その他の専門的な仕事を正式に依頼し、実施するよう取り決める。依頼主を主語にし、人または成果物・仕事を目的語に取る。"
      },
      {
        "sense_id": "sense:009",
        "line": 481,
        "label": "9. 【他動詞・通常受動・軍事】～を士官に任命する",
        "definition": "軍で人を正式に士官として任官させ、階級と権限を与える。本人を主語にした受動形が特に多い。"
      },
      {
        "sense_id": "sense:010",
        "line": 519,
        "label": "10. 【他動詞】船舶・設備などを就役・稼働させる",
        "definition": "新しい船舶、機械、設備、システムなどについて、必要な試験・確認を経て正式に運用可能な状態へ移し、使用を開始する。船舶の正式な就役と、工学上の設備立ち上げの両方に使う。"
      }
    ],
    "collocations_examples": [
      {
        "example_id": "ex-9316b6186144",
        "example": "Agents earn commission on every policy they sell.",
        "translation": "代理店担当者は販売した保険契約ごとに歩合を得る。"
      },
      {
        "example_id": "ex-cb80e1af867d",
        "example": "The gallery pays its representatives a commission for each painting sold.",
        "translation": "その画廊は絵が売れるたびに販売担当者へ歩合を支払う。"
      },
      {
        "example_id": "ex-57cff05fb475",
        "example": "The officer resigned her commission and left the service.",
        "translation": "その士官は任官を辞し、軍を去った。"
      },
      {
        "example_id": "ex-a2cd837596b0",
        "example": "The navy commissioned the new vessel in a ceremony at the port.",
        "translation": "海軍は港での式典でその新造船を就役させた。"
      },
      {
        "example_id": "ex-70792408d168",
        "example": "Most sales staff receive a base salary and work partly on commission.",
        "translation": "営業担当者の多くは基本給を受け取り、一部は歩合制で働いている。"
      },
      {
        "example_id": "ex-2a1bb25e5f2f",
        "example": "An independent commission on election reform will publish its recommendations next month.",
        "translation": "選挙制度改革に関する独立委員会は来月、提言を公表する。"
      },
      {
        "example_id": "ex-fbbc6db195f4",
        "example": "The exchange service applies a commission of one percent.",
        "translation": "その両替サービスでは1パーセントの手数料がかかる。"
      },
      {
        "example_id": "ex-d99552bc9a56",
        "example": "Two elevators are out of commission while repairs are carried out.",
        "translation": "修理中のため、エレベーター2基が使用できない。"
      },
      {
        "example_id": "ex-2c4c63adf0b7",
        "example": "She takes commissions for custom illustrations through her website.",
        "translation": "彼女はウェブサイトを通じて特注イラストの制作依頼を受けている。"
      },
      {
        "example_id": "ex-eec4283acbd4",
        "example": "The artist accepted a private commission for a family portrait.",
        "translation": "その画家は家族肖像画の個人的な制作依頼を引き受けた。"
      },
      {
        "example_id": "ex-216f34257192",
        "example": "The museum commissioned a local artist to create a sculpture for the entrance.",
        "translation": "美術館は地元の芸術家に、入口用の彫刻を制作するよう依頼した。"
      },
      {
        "example_id": "ex-717b24cb2bd1",
        "example": "The research vessel remained in commission for more than thirty years.",
        "translation": "その調査船は30年以上にわたり就役していた。"
      },
      {
        "example_id": "ex-634a125107f2",
        "example": "After completing the academy, she received a commission as a second lieutenant.",
        "translation": "士官学校を修了後、彼女は少尉に任官した。"
      },
      {
        "example_id": "ex-c9562dbb197e",
        "example": "The composer completed a commission from the city orchestra.",
        "translation": "その作曲家は市のオーケストラから依頼された作品を完成させた。"
      },
      {
        "example_id": "ex-ca0b03c57d9f",
        "example": "Engineers will commission the new control system before the plant reopens.",
        "translation": "工場の再開前に、技術者が新しい制御システムを立ち上げて運用可能にする。"
      },
      {
        "example_id": "ex-14e5f1ccc168",
        "example": "A shoulder injury put him out of commission for the rest of the season.",
        "translation": "肩のけがにより、彼はシーズン残りを出場できなくなった。"
      },
      {
        "example_id": "ex-ad7b66b55de8",
        "example": "The orchestra commissioned a new symphony from the composer.",
        "translation": "そのオーケストラは作曲家に新しい交響曲を依頼した。"
      },
      {
        "example_id": "ex-1b712c228a52",
        "example": "The board commissioned an independent study of the project's environmental impact.",
        "translation": "取締役会はその事業の環境影響について独立調査を依頼した。"
      },
      {
        "example_id": "ex-841e486d1162",
        "example": "The turbine passed all commissioning tests before commercial operation began.",
        "translation": "そのタービンは商業運転開始前に、すべての試運転試験に合格した。"
      },
      {
        "example_id": "ex-7e61f368a4f1",
        "example": "The commission's report identified serious gaps in oversight.",
        "translation": "委員会の報告書は監督体制の重大な不備を指摘した。"
      },
      {
        "example_id": "ex-c4ed4c4f80da",
        "example": "The architect received a commission to design the new library.",
        "translation": "その建築家は新しい図書館を設計する依頼を受けた。"
      },
      {
        "example_id": "ex-a8fbf31eafe0",
        "example": "Newly commissioned officers attended the leadership course.",
        "translation": "新たに任官した士官たちは指揮官研修に参加した。"
      },
      {
        "example_id": "ex-47f5c8fb4a14",
        "example": "The navy plans to put the new patrol ship into commission next spring.",
        "translation": "海軍は来春、新しい巡視船を就役させる予定だ。"
      },
      {
        "example_id": "ex-a7ff4876b298",
        "example": "The buyer paid a commission to the broker who arranged the sale.",
        "translation": "買い手は売買を取りまとめた仲介業者に手数料を支払った。"
      },
      {
        "example_id": "ex-f34292adafa0",
        "example": "The exhibition features a film specially commissioned for the anniversary.",
        "translation": "その展覧会では記念日のために特別制作された映画を上映している。"
      },
      {
        "example_id": "ex-b945a6f5daf9",
        "example": "The evidence linked the weapon to the commission of the crime.",
        "translation": "その証拠により、凶器とその犯罪の実行が結び付けられた。"
      },
      {
        "example_id": "ex-346e0ec5599a",
        "example": "He was commissioned into the air force in 2022.",
        "translation": "彼は2022年に空軍士官に任官した。"
      },
      {
        "example_id": "ex-4a9e5e99fffc",
        "example": "Commission-based pay can create strong incentives to close deals quickly.",
        "translation": "歩合中心の報酬制度は、取引を早く成立させる強い動機を生むことがある。"
      },
      {
        "example_id": "ex-3564b877a182",
        "example": "The hospital's backup generator was commissioned into service last week.",
        "translation": "その病院の非常用発電機は先週、正式に運用開始となった。"
      },
      {
        "example_id": "ex-02f2d3aaca45",
        "example": "The broker charges a small commission on each trade.",
        "translation": "その証券会社は取引ごとに少額の手数料を請求する。"
      },
      {
        "example_id": "ex-eb329d830a0e",
        "example": "The survey was commissioned by the city council.",
        "translation": "その調査は市議会の依頼で実施された。"
      },
      {
        "example_id": "ex-e6c257129cef",
        "example": "The platform advertises commission-free trading in selected funds.",
        "translation": "そのプラットフォームは一部のファンドについて売買手数料無料をうたっている。"
      },
      {
        "example_id": "ex-839ebdf77cb1",
        "example": "No one was injured during the commission of the robbery.",
        "translation": "その強盗の実行中にけが人は出なかった。"
      },
      {
        "example_id": "ex-a48807917206",
        "example": "She receives a ten percent commission on all new contracts.",
        "translation": "彼女はすべての新規契約について10パーセントの歩合を受け取る。"
      },
      {
        "example_id": "ex-823382a720e2",
        "example": "Parliament called for a commission of inquiry into the security failures.",
        "translation": "議会はその安全保障上の失敗について調査委員会を設けるよう求めた。"
      },
      {
        "example_id": "ex-2e9b302f4655",
        "example": "He held a commission in the Royal Navy for twelve years.",
        "translation": "彼は12年間、英国海軍で士官の地位にあった。"
      },
      {
        "example_id": "ex-6cc3dd65ff92",
        "example": "She was commissioned as a lieutenant after completing officer training.",
        "translation": "彼女は士官訓練を修了後、中尉に任官した。"
      },
      {
        "example_id": "ex-75180a63b8f5",
        "example": "She served on the national commission on child welfare for six years.",
        "translation": "彼女は6年間、児童福祉に関する国家委員会の委員を務めた。"
      },
      {
        "example_id": "ex-9211ad69884b",
        "example": "He was accused of aiding others in the commission of the offence.",
        "translation": "彼は他者によるその違反の実行を助けたとして告発された。"
      },
      {
        "example_id": "ex-5d7b59f4e0de",
        "example": "The government set up an independent commission to investigate the disaster.",
        "translation": "政府はその災害を調査する独立委員会を設置した。"
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
  "source_artifact_sha256": "8518a3adc40ce4cbce1cb5cb38779fdae3e2432ff08a459a570ae20078ed7630",
  "normalized_input_sha256": "4e40b29b8a364cbbb65e8b6774938f4693d7ba638945ccf3074ea09e8b0e77af"
}
```
