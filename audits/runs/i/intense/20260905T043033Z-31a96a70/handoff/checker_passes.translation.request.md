# Independent checker handoff

Stage: `checker_passes/translation`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.translation.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_translation_v6

## 目的

英文・訳文・定義における意味の保存と方向を検査する。自然な意訳は認めるが、見出し語の構文差・含意・作用関係を誤学習させる変化は認めない。

## 担当タクソノミー分類

- `example_translation_alignment`
- `semantic_direction_reversal`

## 検査ルール

- 各例文と訳について、述語、主語・目的語・補語、行為者・経験者・対象・結果の意味役割を対応させる。
- 肯定・否定、比較基準、程度、数量、時制、相、法、条件、因果、目的を保存する。
- 修飾範囲、焦点、対比、情報構造、明示内容と文脈推論の境界、レジスターと話者評価を保存する。
- コロケーションのpattern・用途・英文・訳が同じ語義、品詞、完全フレームを表すか確認する。英文が別語義でも成立するだけでは合格にしない。
- 作用する側／される側、上位／下位、原因／結果、全体／部分、評価主体／評価対象を逆転させない。
- 日本語訳が自然でも、英文にない必然性・意図・結果・専門的効果を追加していればfindingとする。
- 同じ例文を異なる構文や語義の証明に使い回していないか確認する。
- 問題が1箇所に見える場合も、同じ訳語・関係が入力section内の別箇所で再発していないか確認する。

## 入力として受け取るセクション

- `definitions`
- `collocations_examples`
- `lexical_relations`

front matter、生成過程、通常チェックの過去判断、ACTIVE.mdは受け取らない。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "example_translation_alignment | semantic_direction_reversal",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "本文からの改変していない引用"
  },
  "severity": "blocking | minor",
  "rationale": "何がどの方向・範囲・強さで不一致か",
  "evidence_link_ids": [],
  "suggested_direction": "意味を変えずに直す方向"
}
```

`taxonomy_id`、位置、severity、根拠を必須とする。事実・語法・例文/訳の正誤に関わるものは `blocking`、事実関係を変えない局所的な日本語調整だけを `minor` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "translation",
  "taxonomy_ids": [
    "example_translation_alignment",
    "semantic_direction_reversal"
  ],
  "specification": "prompts/check_pass_translation_v6.md",
  "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
  "input_sections": {
    "definitions": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、色、関心、圧力などの程度・強度が非常に高いこと。intense pleasure「非常に強い喜び」のように、好ましい対象にも使う。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 111,
        "text": "【日本語訳・定義】活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 158,
        "text": "【日本語訳・定義】人・視線・表情・関係などについて、強い感情や意見が表れる、強く感じられる、または強い感情的な結びつきがあること。人・表情の表出、人物への評価、関係の情緒的な強さを区別する。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 52,
        "text": "【コロケーション】"
      },
      {
        "line": 54,
        "text": "・intense pain  "
      },
      {
        "line": 55,
        "text": "用途: 身体的な痛みが非常に強いことを表す。  "
      },
      {
        "line": 56,
        "text": "例: He felt intense pain in his lower back.  "
      },
      {
        "line": 57,
        "text": "訳: 彼は腰の下部に激しい痛みを感じた。  "
      },
      {
        "line": 59,
        "text": "・intense heat  "
      },
      {
        "line": 60,
        "text": "用途: 暑さや熱が非常に強いことを表す。  "
      },
      {
        "line": 61,
        "text": "例: The intense heat made it dangerous to work outside.  "
      },
      {
        "line": 62,
        "text": "訳: 強烈な暑さのため、屋外で働くのは危険だった。  "
      },
      {
        "line": 64,
        "text": "・intense pressure  "
      },
      {
        "line": 65,
        "text": "用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  "
      },
      {
        "line": 66,
        "text": "例: The new manager is under intense pressure to improve the results.  "
      },
      {
        "line": 67,
        "text": "訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  "
      },
      {
        "line": 69,
        "text": "・intense interest  "
      },
      {
        "line": 70,
        "text": "用途: ある対象に向けられる関心が非常に強いことを表す。  "
      },
      {
        "line": 71,
        "text": "例: The discovery attracted intense interest from researchers around the world.  "
      },
      {
        "line": 72,
        "text": "訳: その発見は世界中の研究者から強い関心を集めた。  "
      },
      {
        "line": 74,
        "text": "・intense anger  "
      },
      {
        "line": 75,
        "text": "用途: 怒りの感情が非常に強いことを表す。  "
      },
      {
        "line": 76,
        "text": "例: The decision provoked intense anger among local residents.  "
      },
      {
        "line": 77,
        "text": "訳: その決定は地元住民の激しい怒りを引き起こした。  "
      },
      {
        "line": 79,
        "text": "・intense blue  "
      },
      {
        "line": 80,
        "text": "用途: 色の強さや濃さが際立ち、強い印象を与えることを表す。  "
      },
      {
        "line": 81,
        "text": "例: The intense blue of the lake stood out against the white snow.  "
      },
      {
        "line": 82,
        "text": "訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 119,
        "text": "【コロケーション】"
      },
      {
        "line": 121,
        "text": "・intense competition  "
      },
      {
        "line": 122,
        "text": "用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。  "
      },
      {
        "line": 123,
        "text": "例: There is intense competition for places at the top universities.  "
      },
      {
        "line": 124,
        "text": "訳: 一流大学の枠をめぐって激しい競争がある。  "
      },
      {
        "line": 126,
        "text": "・intense activity  "
      },
      {
        "line": 127,
        "text": "用途: 活動の強度・エネルギー・負荷が非常に高いことを表す。  "
      },
      {
        "line": 128,
        "text": "例: The airport experienced a period of intense activity before the holiday.  "
      },
      {
        "line": 129,
        "text": "訳: その空港では休暇前に活動が非常に活発な時期があった。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 166,
        "text": "【コロケーション】"
      },
      {
        "line": 168,
        "text": "・an intense look  "
      },
      {
        "line": 169,
        "text": "用途: 強い感情や集中を帯びた視線・表情を表す。  "
      },
      {
        "line": 170,
        "text": "例: She gave him an intense look when he mentioned the accusation.  "
      },
      {
        "line": 171,
        "text": "訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  "
      },
      {
        "line": 173,
        "text": "・an intense person  "
      },
      {
        "line": 174,
        "text": "用途: 感情や態度が強く、存在感や圧のある人を表す。肯定・否定の評価は文脈で変わる。  "
      },
      {
        "line": 175,
        "text": "例: He is an intense person who takes every project very seriously.  "
      },
      {
        "line": 176,
        "text": "訳: 彼はどのプロジェクトにも非常に真剣に取り組む、強い存在感のある人だ。  "
      },
      {
        "line": 178,
        "text": "・an intense relationship  "
      },
      {
        "line": 179,
        "text": "用途: 感情的な結びつきや相互作用が非常に強い関係を表す。  "
      },
      {
        "line": 180,
        "text": "例: Their intense relationship left little room for emotional distance.  "
      },
      {
        "line": 181,
        "text": "訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 40,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 86,
        "text": "【類義語】"
      },
      {
        "line": 88,
        "text": "・strong  "
      },
      {
        "line": 89,
        "text": "定義: intense と比較される、幅広い「強い」を表す関連語。  "
      },
      {
        "line": 90,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 91,
        "text": "違い: strong は幅広い強さを表し、intense は感覚・感情などの強度が非常に高いことに焦点を置く。  "
      },
      {
        "line": 92,
        "text": "例: intense pain  "
      },
      {
        "line": 93,
        "text": "訳: 強い痛み。  "
      },
      {
        "line": 95,
        "text": "・extreme  "
      },
      {
        "line": 96,
        "text": "定義: intense と比較される、通常の範囲からの逸脱に焦点を置く関連語。  "
      },
      {
        "line": 97,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 98,
        "text": "違い: extreme は通常の範囲や限界からの逸脱に焦点があり、intense は体感や感情の強さにも使う。  "
      },
      {
        "line": 99,
        "text": "例: intense heat  "
      },
      {
        "line": 100,
        "text": "訳: 強烈な暑さ。  "
      },
      {
        "line": 102,
        "text": "・powerful  "
      },
      {
        "line": 103,
        "text": "定義: intense と比較される、作用する力や影響に焦点を置く関連語。  "
      },
      {
        "line": 104,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 105,
        "text": "違い: powerful は作用する力や影響力に焦点があり、intense は経験される強度や圧にも使う。  "
      },
      {
        "line": 106,
        "text": "例: intense interest  "
      },
      {
        "line": 107,
        "text": "訳: 強い関心。  "
      },
      {
        "line": 109,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 133,
        "text": "【類義語】"
      },
      {
        "line": 135,
        "text": "・fierce  "
      },
      {
        "line": 136,
        "text": "定義: intense と比較される、競争・対立の激しさに焦点を置く関連語。  "
      },
      {
        "line": 137,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 138,
        "text": "違い: fierce は攻撃性や対立を含みやすく、intense は敵意のない活動の強さにも使える。  "
      },
      {
        "line": 139,
        "text": "例: intense competition  "
      },
      {
        "line": 140,
        "text": "訳: 激しい競争。  "
      },
      {
        "line": 142,
        "text": "・vigorous  "
      },
      {
        "line": 143,
        "text": "定義: intense と比較される、活力や積極的なエネルギーに焦点を置く関連語。  "
      },
      {
        "line": 144,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 145,
        "text": "違い: vigorous は活力や積極的なエネルギーに焦点があり、intense は活動の緊張や負荷も表す。  "
      },
      {
        "line": 146,
        "text": "例: intense activity  "
      },
      {
        "line": 147,
        "text": "訳: 激しい活動。  "
      },
      {
        "line": 149,
        "text": "・strenuous  "
      },
      {
        "line": 150,
        "text": "定義: intense と比較される、大きな努力を要する行為に焦点を置く関連語。  "
      },
      {
        "line": 151,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 152,
        "text": "違い: strenuous は行為がきつく多大な努力を要することに焦点があり、intense は活動の緊張感や負荷も表す。  "
      },
      {
        "line": 153,
        "text": "例: intense training  "
      },
      {
        "line": 154,
        "text": "訳: 激しい訓練。  "
      },
      {
        "line": 156,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 185,
        "text": "【類義語】"
      },
      {
        "line": 187,
        "text": "・serious  "
      },
      {
        "line": 188,
        "text": "定義: intense と比較される、真剣さや重要性に焦点を置く関連語。  "
      },
      {
        "line": 189,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 190,
        "text": "違い: serious は真面目さや重要性に焦点があり、intense は強い感情や張り詰めた印象も表す。  "
      },
      {
        "line": 191,
        "text": "例: an intense person  "
      },
      {
        "line": 192,
        "text": "訳: 感情や態度の強い人。  "
      },
      {
        "line": 194,
        "text": "・passionate  "
      },
      {
        "line": 195,
        "text": "定義: intense と比較される、熱意や強い関与に焦点を置く関連語。  "
      },
      {
        "line": 196,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 197,
        "text": "違い: passionate は熱意や強い関与を表し、intense より肯定的な評価になりやすい。  "
      },
      {
        "line": 198,
        "text": "例: an intense look  "
      },
      {
        "line": 199,
        "text": "訳: 強い視線。  "
      },
      {
        "line": 201,
        "text": "・earnest  "
      },
      {
        "line": 202,
        "text": "定義: intense と比較される、誠実さや真摯さに焦点を置く関連語。  "
      },
      {
        "line": 203,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 204,
        "text": "違い: earnest は誠実さや真摯さに焦点があり、intense は感情の強さや対人的な圧も表す。  "
      },
      {
        "line": 205,
        "text": "例: an intense relationship  "
      },
      {
        "line": 206,
        "text": "訳: 感情的な結びつきの強い関係。  "
      }
    ]
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
  }
}
```
