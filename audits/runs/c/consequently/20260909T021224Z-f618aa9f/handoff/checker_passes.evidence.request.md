# Independent checker handoff

Stage: `checker_passes/evidence`

Run this request in its own independent subagent/session. The seven checker pass requests are designed to run concurrently; do not concatenate them into one prompt or reuse one subagent for multiple passes.

Save exactly one JSON response as `checker_passes.evidence.response.json`. The top-level JSON must include the routed `pass_id` and a `reviewer` object with `mode: "handoff"`, the actual `declared_model`, `ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass must use a different agent_id.
## Prompt

# check_pass_evidence_v6

## 目的

主張単位の根拠リンクが、対象主張を直接支持するかだけを検査する。source-first工程との二重チェックを避けるため、このパスは資料探索計画、source inventoryのcoverage、fact収集をやり直さない。

## 担当タクソノミー分類

- `evidence_claim_mismatch`

## 検査ルール

- source-first工程が固定したsource・fact・claim unit・対象sectionを入力として受け、claimと引用位置または忠実な要約の対応を確認する。
- 入力は `evidence_context_v1` とし、対象claimに関係するsource、fact、source union、claim unit、`source_supports` だけを含む。`source_inventory_sha256`、`source_first_artifact_sha256`、本文hashの一致を機械検証済みでなければ開始しない。
- source-first artifactが欠落、未完了、schema不正、参照切れ、本文hash不一致の場合はfail closedとし、再探索やfact追加で補わない。
- 資料名や検索結果見出しが存在するだけで合格にせず、locator、該当箇所、支持内容、当該語義・構文への適用範囲を確認する。
- 別義、別品詞、別法域、別地域、別時代の記述を現在の対象主張へ流用しない。
- 高リスク主張に `two_sources_or_primary` が指定される場合、同一引用元を別IDにした重複を独立2資料として数えない。一次資料1件を使う場合は当該主張へ直接適用できることを確認する。
- 発音、語源、語義境界、文法制約、完全フレーム、例文の自然さ、絶対表現、地域差、頻度、専門説明、類義語・反意語差のevidence linkを個別に確認する。
- 断定的主張では支持例だけでなく、source-first記録にある反例・矛盾探索の方法と結果が主張範囲に対応するか確認する。
- 資料が食い違う場合、本文が差を反映して範囲を限定しているかを確認する。根拠から決められない内容をpassにしない。
- このパスはclaimの辞書学的正しさを他パスの代わりに再判定せず、「提示された根拠がそのclaimを支えるか」に限定する。

## 入力として受け取るセクション

- `pronunciation`
- `etymology`
- `word_formation`
- `core_image`
- `sense_structure`
- `frequency_register`
- `frames`
- `collocations_examples`
- `usage_notes`
- `lexical_relations`
- source-first工程が生成したsource inventory、fact、claim unit、evidence link
- API modeとhandoff modeはいずれも `scripts/check_passes.py` が生成した同一の正規化requestを使う。

## findingの出力スキーマ

```json
{
  "taxonomy_id": "evidence_claim_mismatch",
  "location": {
    "section": "router section selector",
    "line_start": 1,
    "line_end": 1,
    "exact_quote": "根拠対象となる本文主張"
  },
  "severity": "blocking | minor",
  "rationale": "source locator・支持内容・適用範囲の不一致",
  "evidence_link_ids": ["問題のある既存link ID"],
  "suggested_direction": "主張限定、根拠差替え、holdの方向"
}
```

根拠が主張を支持しない状態は原則 `blocking` とする。


## Input packet

```json
{
  "schema_version": "check_pass_request_v6",
  "pass_id": "evidence",
  "taxonomy_ids": [
    "evidence_claim_mismatch"
  ],
  "specification": "prompts/check_pass_evidence_v6.md",
  "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米: /ˈkɑːn.sə.kwənt.li/｜英: /ˈkɒn.sɪ.kwənt.li/。いずれも4音節で、第1音節に主強勢がある。米語は第1音節が /ɑː/、英語は /ɒ/ で、さらに米語では第2音節が /ə/、英語では /ɪ/ となる。`quent` の母音はいずれも弱く /ə/ と発音する。  "
      }
    ],
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "形容詞 `consequent` に副詞語尾 `-ly` が付いた語である。`consequent` はラテン語 *consequi*「あとに従う、続いて起こる」にさかのぼり、`con-`「ともに」と *sequi*「従う」に関係する。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・`consequence`：名詞。「結果、影響」。特に複数形 `consequences` は好ましくない結果を指しやすい。  "
      },
      {
        "line": 24,
        "text": "・`consequent`：形容詞。ある出来事の結果として続くことを表す、ややフォーマルな語。  "
      },
      {
        "line": 25,
        "text": "・`consequential`：形容詞。「重要な、重大な」。`consequently` と違い、因果関係をつなぐ副詞ではない。  "
      }
    ],
    "core_image": [],
    "sense_structure": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 31,
        "text": "【日本語訳・定義】前に述べた事実・状況・判断を理由として、後に述べる結果が続くことを示す。単に出来事が後の時点で起こることではなく、前件から後件が結果として導かれることを表す。`so` よりフォーマルで、報告、説明、論証などで使われやすい。  "
      }
    ],
    "frequency_register": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 33,
        "text": "【頻度】〈6/10〉  "
      },
      {
        "line": 35,
        "text": "【レジスター/領域】ややフォーマル。学術文、報告書、ニュース、論理的な説明でよく用いられる。  "
      }
    ],
    "frames": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 37,
        "text": "【文法パターン】`〈原因となる文〉. Consequently, 〈結果の文〉`＝その結果、…／`〈原因となる文〉; consequently, 〈結果の文〉`＝…、したがって…／`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する。文頭で使うときは通常後ろにコンマを置き、二つの独立した節をコンマだけでつなぐ `…, consequently, …` は避ける。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 39,
        "text": "【コロケーション】"
      },
      {
        "line": 41,
        "text": "・`Consequently, 〈結果の文〉`  "
      },
      {
        "line": 42,
        "text": "用途: 直前に述べた原因・根拠を受けて、文全体の結論や結果を明示する。  "
      },
      {
        "line": 43,
        "text": "例: The train service was suspended. Consequently, many employees worked from home.  "
      },
      {
        "line": 44,
        "text": "訳: 列車の運行が停止された。その結果、多くの従業員が在宅勤務をした。  "
      },
      {
        "line": 46,
        "text": "・`〈原因となる文〉; consequently, 〈結果の文〉`  "
      },
      {
        "line": 47,
        "text": "用途: 密接な因果関係にある二つの独立節を、セミコロンでつなぐフォーマルな書き方である。  "
      },
      {
        "line": 48,
        "text": "例: The evidence was incomplete; consequently, the committee postponed its decision.  "
      },
      {
        "line": 49,
        "text": "訳: 証拠が不十分だったため、委員会は決定を延期した。  "
      },
      {
        "line": 51,
        "text": "・`〈主語〉 + consequently + 〈動詞句〉`  "
      },
      {
        "line": 52,
        "text": "用途: 結果を表す副詞として、主語の後、主要動詞の前に置く。  "
      },
      {
        "line": 53,
        "text": "例: Demand fell sharply, and the company consequently reduced production.  "
      },
      {
        "line": 54,
        "text": "訳: 需要が急減したため、その会社は結果として生産を減らした。  "
      },
      {
        "line": 56,
        "text": "・`be consequently + 〈過去分詞・形容詞〉`  "
      },
      {
        "line": 57,
        "text": "用途: 原因の結果として生じた状態や判断を、`be` の後で説明する。  "
      },
      {
        "line": 58,
        "text": "例: The deadline was missed, and the application was consequently rejected.  "
      },
      {
        "line": 59,
        "text": "訳: 締切に間に合わなかったため、その申請は結果として却下された。  "
      },
      {
        "line": 61,
        "text": "・`and consequently + 〈動詞句〉`  "
      },
      {
        "line": 62,
        "text": "用途: 一つの節の中で、前の節・句に示された事情の帰結として後続の行為や状態を示す。  "
      },
      {
        "line": 63,
        "text": "例: The region receives little rainfall and consequently faces frequent water shortages.  "
      },
      {
        "line": 64,
        "text": "訳: その地域は降雨量が少なく、その結果しばしば水不足に直面する。  "
      }
    ],
    "usage_notes": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 66,
        "text": "【語法・注意】`consequently` が示すのは因果関係であり、単なる時間順ではない。後に起きただけなら `subsequently`、次の手順を示すなら `then` を使う。`Because the road was closed, we took a detour.` のように原因を従属節で述べる形と違い、`consequently` は原因から帰結を示す副詞である。`The road was closed; consequently, we took a detour.` のようにピリオドまたはセミコロンで二つの独立節をつなぐのは代表的な書き方だが、`the application was consequently rejected` のように文中でも使える。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 29,
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "line": 68,
        "text": "【類義語】"
      },
      {
        "line": 70,
        "text": "・therefore  "
      },
      {
        "line": 71,
        "text": "定義: 前に述べた事実・理由から、論理的な結論や結果が導かれることを示す。  "
      },
      {
        "line": 72,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 73,
        "text": "違い: `therefore` は論証の結論を明示する響きが特に強い。`consequently` は出来事・状況から実際に続く結果を示すときにも自然である。  "
      },
      {
        "line": 74,
        "text": "例: The data are incomplete; therefore, no firm conclusion can be drawn.  "
      },
      {
        "line": 75,
        "text": "訳: データが不完全なので、確かな結論は導けない。  "
      },
      {
        "line": 77,
        "text": "・as a result  "
      },
      {
        "line": 78,
        "text": "定義: 前の出来事や状況の結果として、後の出来事が起こることを示す句。  "
      },
      {
        "line": 79,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 80,
        "text": "違い: `as a result` は日常的で分かりやすく、会話から文章まで広く使える。`consequently` は一語でよりフォーマルに因果関係をつなぐ。  "
      },
      {
        "line": 81,
        "text": "例: The supplier delayed delivery. As a result, the launch was postponed.  "
      },
      {
        "line": 82,
        "text": "訳: 供給業者が納品を遅らせた。その結果、発売は延期された。  "
      },
      {
        "line": 84,
        "text": "・thus  "
      },
      {
        "line": 85,
        "text": "定義: 前の内容を受けて、結果や論理的帰結を示す。  "
      },
      {
        "line": 86,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 87,
        "text": "違い: `thus` は書き言葉でより硬く、論文・技術文書では「このように」の意味も持つ。`consequently` はここでいう「その結果」の意味に限られる。  "
      },
      {
        "line": 88,
        "text": "例: The sample was contaminated and thus could not be analyzed.  "
      },
      {
        "line": 89,
        "text": "訳: 試料が汚染されていたため、したがって分析できなかった。  "
      },
      {
        "line": 91,
        "text": "・accordingly  "
      },
      {
        "line": 92,
        "text": "定義: ある事情・情報に応じて、またはその結果として行動・処置がなされることを示す。  "
      },
      {
        "line": 93,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 94,
        "text": "違い: `accordingly` は「事情に応じて」の意味で意図的な対応を表すことがある。`consequently` は、対応の意図がなくても因果の結果を示せる。  "
      },
      {
        "line": 95,
        "text": "例: The weather forecast changed, so the organizers adjusted the schedule accordingly.  "
      },
      {
        "line": 96,
        "text": "訳: 天気予報が変わったので、主催者はそれに応じて日程を調整した。  "
      },
      {
        "line": 98,
        "text": "・hence  "
      },
      {
        "line": 99,
        "text": "定義: 前に述べた理由・事実から結論または結果が生じることを示す。  "
      },
      {
        "line": 100,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 101,
        "text": "違い: 因果を示す `hence` は `consequently` より文語的で、簡潔な論証や固定表現に多い。また `hence` には「今から〜後」の時間表現など別の用法もある。  "
      },
      {
        "line": 102,
        "text": "例: The files were encrypted; hence, only authorized staff could read them.  "
      },
      {
        "line": 103,
        "text": "訳: ファイルは暗号化されていた。したがって、閲覧できたのは権限を持つ職員だけだった。  "
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
  },
  "evidence_context": {
    "schema_version": "evidence_context_v1",
    "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "cf92c5a0a56d2309a638e3b9c00e588d276280bd9878aa36a1d9fa5f72b21143",
    "source_first_artifact_sha256": "bcea85e6857e24d95179eec8199560c6b551bb2889d5dae928b29cda43626824",
    "relevant_sections": [
      "collocations_examples",
      "core_image",
      "etymology",
      "frames",
      "frequency_register",
      "lexical_relations",
      "pronunciation",
      "sense_structure",
      "usage_notes",
      "word_formation"
    ],
    "sources": [
      {
        "id": "S001",
        "locator": "https://dictionary.cambridge.org/dictionary/english/consequently",
        "source_type": "learner_dictionary",
        "independence_group": "cambridge_university_press",
        "facts": [
          {
            "id": "F002",
            "form": "consequently",
            "kind": "pronunciation",
            "statement": "Cambridge gives UK /ˈkɒn.sɪ.kwənt.li/ and US /ˈkɑːn.sə.kwənt.li/.",
            "source_detail": "The pronunciation entry displays the two regional IPA forms."
          }
        ]
      },
      {
        "id": "S002",
        "locator": "https://www.oxfordlearnersdictionaries.com/definition/english/consequently",
        "source_type": "learner_dictionary",
        "independence_group": "oxford_university_press",
        "facts": [
          {
            "id": "F004",
            "form": "consequently",
            "kind": "pronunciation",
            "statement": "Oxford gives British /ˈkɒnsɪkwəntli/ and American /ˈkɑːnsɪkwentli/.",
            "source_detail": "The entry prints separate British and North American IPA forms."
          }
        ]
      },
      {
        "id": "S004",
        "locator": "https://www.etymonline.com/word/consequent",
        "source_type": "etymology_dictionary",
        "independence_group": "etymonline",
        "facts": [
          {
            "id": "F007",
            "form": "consequently",
            "kind": "etymology",
            "statement": "Consequently is related to consequent, from Latin consequi ‘to follow after’, formed from com- and sequi ‘to follow’.",
            "source_detail": "The consequent entry gives the Latin formation and explicitly lists Consequently as related."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "U002",
        "source_fact_ids": [
          "F002",
          "F004"
        ],
        "canonical_statement": "The word has distinct British and American vowel realizations in the first two syllables.",
        "disposition": "included",
        "rationale": "The regional IPA is stated in the pronunciation section."
      },
      {
        "id": "U004",
        "source_fact_ids": [
          "F007"
        ],
        "canonical_statement": "The word derives through consequent from the Latin follow-after verb consequi.",
        "disposition": "included",
        "rationale": "This supports the compact etymology."
      }
    ],
    "claim_units": [
      {
        "id": "C002",
        "union_ids": [
          "U002"
        ],
        "subject_form": "consequently",
        "claim_type": "pronunciation",
        "statement": "British and American pronunciation differ in the first and second syllable vowels.",
        "article_target_ids": [
          "pronunciation"
        ],
        "source_supports": [
          {
            "source_fact_id": "F002",
            "support_summary": "Cambridge supplies separate UK and US IPA forms."
          },
          {
            "source_fact_id": "F004",
            "support_summary": "Oxford independently supplies British and American IPA."
          }
        ]
      },
      {
        "id": "C004",
        "union_ids": [
          "U004"
        ],
        "subject_form": "consequently",
        "claim_type": "etymology",
        "statement": "Its history is tied to the idea of following after.",
        "article_target_ids": [
          "etymology"
        ],
        "source_supports": [
          {
            "source_fact_id": "F007",
            "support_summary": "Etymonline traces consequent to Latin consequi ‘follow after’."
          }
        ]
      }
    ]
  },
  "specification_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
  "source_artifact_sha256": "bcea85e6857e24d95179eec8199560c6b551bb2889d5dae928b29cda43626824",
  "normalized_input_sha256": "b06ac61a3353dce82188c48253cf7a439a5c821694d26f7569c993a5ea283d14"
}
```
