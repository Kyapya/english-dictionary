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
  "input_body_sha256": "3a1ecd39179a54df37a738e19b1b01cfb3f4fc1ccfad52e3eed9dcbf378473a7",
  "input_sections": {
    "definitions": [
      {
        "line": 42,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 44,
        "text": "【日本語訳・定義】感情、感覚、痛み、暑さ、色、関心、圧力などの程度・強度が非常に高いこと。intense pleasure「非常に強い喜び」のように、好ましい対象にも使う。  "
      },
      {
        "line": 111,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 113,
        "text": "【日本語訳・定義】活動・競争・議論・訓練などが高い強度で行われ、活動量・速度・忙しさ・負荷が大きいこと。強い努力や緊張を伴う場合もあるが、それらは必須ではない。短期集中を伴う場合にも使うが、短期間であることは必須ではない。  "
      },
      {
        "line": 160,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 162,
        "text": "【日本語訳・定義】人については強い感情や態度を持つ、またはそうした印象を与えること、視線や表情については集中・鋭さ・強い感情が感じられること、関係については情緒的な結びつきや相互作用が強いことを表す。関係は緊張・衝突・不安定さを伴う場合もある。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 42,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 54,
        "text": "【コロケーション】"
      },
      {
        "line": 56,
        "text": "・intense pain  "
      },
      {
        "line": 57,
        "text": "用途: 身体的な痛みが非常に強いことを表す。  "
      },
      {
        "line": 58,
        "text": "例: He felt intense pain in his lower back.  "
      },
      {
        "line": 59,
        "text": "訳: 彼は腰の下部に激しい痛みを感じた。  "
      },
      {
        "line": 61,
        "text": "・intense heat  "
      },
      {
        "line": 62,
        "text": "用途: 暑さや熱が非常に強いことを表す。  "
      },
      {
        "line": 63,
        "text": "例: The intense heat made it dangerous to work outside.  "
      },
      {
        "line": 64,
        "text": "訳: 強烈な暑さのため、屋外で働くのは危険だった。  "
      },
      {
        "line": 66,
        "text": "・intense pressure  "
      },
      {
        "line": 67,
        "text": "用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  "
      },
      {
        "line": 68,
        "text": "例: The new manager is under intense pressure to improve the results.  "
      },
      {
        "line": 69,
        "text": "訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  "
      },
      {
        "line": 71,
        "text": "・intense interest  "
      },
      {
        "line": 72,
        "text": "用途: ある対象に向けられる関心が非常に強いことを表す。  "
      },
      {
        "line": 73,
        "text": "例: The discovery attracted intense interest from researchers around the world.  "
      },
      {
        "line": 74,
        "text": "訳: その発見は世界中の研究者から強い関心を集めた。  "
      },
      {
        "line": 76,
        "text": "・intense anger  "
      },
      {
        "line": 77,
        "text": "用途: 怒りの感情が非常に強いことを表す。  "
      },
      {
        "line": 78,
        "text": "例: The decision provoked intense anger among local residents.  "
      },
      {
        "line": 79,
        "text": "訳: その決定は地元住民の激しい怒りを引き起こした。  "
      },
      {
        "line": 81,
        "text": "・intense blue  "
      },
      {
        "line": 82,
        "text": "用途: 色の鮮やかさや彩度が際立ち、強い印象を与えることを表す。  "
      },
      {
        "line": 83,
        "text": "例: The intense blue of the lake stood out against the white snow.  "
      },
      {
        "line": 84,
        "text": "訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  "
      },
      {
        "line": 111,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 123,
        "text": "【コロケーション】"
      },
      {
        "line": 125,
        "text": "・intense competition  "
      },
      {
        "line": 126,
        "text": "用途: 競争の強度や激しさが非常に高いことを表す。  "
      },
      {
        "line": 127,
        "text": "例: There is intense competition for places at the top universities.  "
      },
      {
        "line": 128,
        "text": "訳: 一流大学の枠をめぐって激しい競争がある。  "
      },
      {
        "line": 130,
        "text": "・intense activity  "
      },
      {
        "line": 131,
        "text": "用途: 活動の強度・活動量・速度・忙しさ・負荷が非常に高いことを表す。  "
      },
      {
        "line": 132,
        "text": "例: The airport experienced a period of intense activity before the holiday.  "
      },
      {
        "line": 133,
        "text": "訳: その空港では休暇前に活動が非常に活発な時期があった。  "
      },
      {
        "line": 160,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 172,
        "text": "【コロケーション】"
      },
      {
        "line": 174,
        "text": "・an intense look  "
      },
      {
        "line": 175,
        "text": "用途: 強い感情や集中を帯びた視線・表情を表す。  "
      },
      {
        "line": 176,
        "text": "例: She gave him an intense look when he mentioned the accusation.  "
      },
      {
        "line": 177,
        "text": "訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  "
      },
      {
        "line": 179,
        "text": "・an intense person  "
      },
      {
        "line": 180,
        "text": "用途: 感情や態度が強く、存在感や圧のある人を表す。肯定・否定の評価は文脈で変わる。  "
      },
      {
        "line": 181,
        "text": "例: He is an intense person who takes every project very seriously.  "
      },
      {
        "line": 182,
        "text": "訳: 彼はどのプロジェクトにも非常に真剣に取り組む、強い存在感のある人だ。  "
      },
      {
        "line": 184,
        "text": "・an intense relationship  "
      },
      {
        "line": 185,
        "text": "用途: 感情的な結びつきや相互作用が非常に強い関係を表す。必ずしも良好・安定とは限らない。  "
      },
      {
        "line": 186,
        "text": "例: Their intense relationship left little room for emotional distance.  "
      },
      {
        "line": 187,
        "text": "訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 42,
        "text": "1. 【形容詞・限定／叙述】強烈な、非常に強い"
      },
      {
        "line": 88,
        "text": "【類義語】"
      },
      {
        "line": 90,
        "text": "・strong  "
      },
      {
        "line": 91,
        "text": "定義: intense と同じく、力・程度・感情などが大きいことを表す基本語。  "
      },
      {
        "line": 92,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 93,
        "text": "違い: strong は幅広い強さを表し、intense は感覚・感情などの強度が非常に高いことに焦点を置く。  "
      },
      {
        "line": 94,
        "text": "例: intense pain  "
      },
      {
        "line": 95,
        "text": "訳: 強い痛み。  "
      },
      {
        "line": 97,
        "text": "・extreme  "
      },
      {
        "line": 98,
        "text": "定義: 通常の範囲や限界から大きく外れた状態を表す関連語。  "
      },
      {
        "line": 99,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 100,
        "text": "違い: extreme は通常の範囲や限界からの逸脱に焦点があり、intense は体感や感情の強さにも使う。  "
      },
      {
        "line": 101,
        "text": "例: intense heat  "
      },
      {
        "line": 102,
        "text": "訳: 強烈な暑さ。  "
      },
      {
        "line": 104,
        "text": "・powerful  "
      },
      {
        "line": 105,
        "text": "定義: 物理的・心理的な力や他者への影響が大きいことを表す関連語。  "
      },
      {
        "line": 106,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 107,
        "text": "違い: powerful は作用する力や影響力に焦点があり、intense は経験される強度や圧にも使う。  "
      },
      {
        "line": 108,
        "text": "例: intense interest  "
      },
      {
        "line": 109,
        "text": "訳: 強い関心。  "
      },
      {
        "line": 111,
        "text": "2. 【形容詞・限定／叙述】激しい、活動量の多い"
      },
      {
        "line": 137,
        "text": "【類義語】"
      },
      {
        "line": 139,
        "text": "・fierce  "
      },
      {
        "line": 140,
        "text": "定義: 競争・対立・攻撃性などの激しさが非常に強いことを表す関連語。  "
      },
      {
        "line": 141,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 142,
        "text": "違い: fierce は攻撃性や対立を含みやすく、intense は敵意のない活動の強さにも使える。  "
      },
      {
        "line": 143,
        "text": "例: intense competition  "
      },
      {
        "line": 144,
        "text": "訳: 激しい競争。  "
      },
      {
        "line": 146,
        "text": "・intensive  "
      },
      {
        "line": 147,
        "text": "定義: 活動・訓練などを集中して行うことを表す関連語。  "
      },
      {
        "line": 148,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 149,
        "text": "違い: intensive は集中度・密度・徹底性を、intense は高い強度・活動量・速度・負荷を前面に出す。期間・範囲限定は intensive に伴う傾向だが必須ではない。  "
      },
      {
        "line": 150,
        "text": "例: intensive training  "
      },
      {
        "line": 151,
        "text": "訳: 集中的な訓練。  "
      },
      {
        "line": 153,
        "text": "・concentrated  "
      },
      {
        "line": 154,
        "text": "定義: 活動・注意・資源などが一箇所や短期間に集められた状態を表す関連語。  "
      },
      {
        "line": 155,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 156,
        "text": "違い: concentrated は集中配置や密度に焦点があり、intense は活動そのものの強度・活動量・速度・負荷に焦点を置く。  "
      },
      {
        "line": 157,
        "text": "例: concentrated training  "
      },
      {
        "line": 158,
        "text": "訳: 集中的な訓練。  "
      },
      {
        "line": 160,
        "text": "3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた"
      },
      {
        "line": 191,
        "text": "【類義語】"
      },
      {
        "line": 193,
        "text": "・passionate  "
      },
      {
        "line": 194,
        "text": "定義: intense と同じく強い感情や関与を表すが、熱意や情熱を前面に出す関連語。  "
      },
      {
        "line": 195,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 196,
        "text": "違い: passionate は熱意・情熱や積極的な関与を含みやすく、intense は肯定・否定を問わず感情や態度の強さを表す。  "
      },
      {
        "line": 197,
        "text": "例: a passionate advocate  "
      },
      {
        "line": 198,
        "text": "訳: 熱心な擁護者。  "
      },
      {
        "line": 200,
        "text": "・deep  "
      },
      {
        "line": 201,
        "text": "定義: 感情・関係・結びつきなどの深さを表す関連語。  "
      },
      {
        "line": 202,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 203,
        "text": "違い: deep は内面の深さや持続する結びつきに焦点があり、intense はその場の強い感情や張り詰めた印象にも使う。  "
      },
      {
        "line": 204,
        "text": "例: a deep emotional bond  "
      },
      {
        "line": 205,
        "text": "訳: 深い感情的な結びつき。  "
      },
      {
        "line": 207,
        "text": "・fervent  "
      },
      {
        "line": 208,
        "text": "定義: 支持・願い・感情などの熱烈さを表す関連語。  "
      },
      {
        "line": 209,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 210,
        "text": "違い: fervent は熱意や支持の強さを肯定的に表しやすく、intense は人・視線・関係の張り詰めた印象など、より広い対象に使う。  "
      },
      {
        "line": 211,
        "text": "例: fervent support  "
      },
      {
        "line": 212,
        "text": "訳: 熱烈な支持。  "
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
