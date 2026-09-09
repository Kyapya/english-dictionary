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
  "input_body_sha256": "7daa0d416ecef06000548e2f59c08bd4394750574e23f19e24855a4a6339257a",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "米・英: /ˈevɪdənt/。3音節で、第1音節に主強勢がある。第1音節の /ˈev/ に強勢を置き、第2音節の /ɪ/ は弱く、第3音節は /dənt/ と発音する。語尾の /t/ を落として「エビデン」のようにせず、最後を閉じる。派生副詞 evidently は /ˈevɪdəntli/、同語族の名詞 evidence は /ˈevɪdəns/ で、いずれも語頭側に強勢がある。  "
      }
    ],
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "中英語後期に、古フランス語またはラテン語 evidens・evident-「目や心に明らかな、明白な」から英語に入った。ラテン語の形は e-（ex-「外へ、十分に」の変形）と videre「見る」に関係し、もともと「外に現れて見える」という発想を含む。  "
      },
      {
        "line": 20,
        "text": "同じラテン語系統の evidence「証拠、証拠を示す」、evidently「明らかに、どうやら」、self-evident「自明な」と意味上・形態上つながる。  "
      }
    ],
    "word_formation": [
      {
        "line": 22,
        "text": "＃語形成"
      },
      {
        "line": 24,
        "text": "・evidently：副詞。「明らかに、見たところ」。文全体を修飾して「どうやら、伝えられるところでは」のように使うこともある。  "
      },
      {
        "line": 25,
        "text": "・self-evident：複合形容詞。「証明や説明を必要としないほど明らかな、自明の」。  "
      },
      {
        "line": 26,
        "text": "・evidence：名詞・動詞。evident と同じ語源系統に属し、名詞では「証拠」、動詞では「証拠を示す」を表す。現代英語で evident に単純に接尾辞を付けた派生語ではない。  "
      }
    ],
    "core_image": [],
    "sense_structure": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 32,
        "text": "【日本語訳・定義】見える特徴、行動、データ、状況などから、ある事実・状態・感情・評価を容易に認識または理解できることを表す。観察した人にとって明白だという意味であり、語そのものが論理的な証明や絶対的な確実性まで保証するわけではない。  "
      }
    ],
    "frequency_register": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 34,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 36,
        "text": "【レジスター/領域】標準語だが、会話中心の obvious や clear よりやや形式的。報告書、学術文、ニュース、ビジネスの説明で多く、感情や特徴が外から読み取れることにも使う。  "
      }
    ],
    "frames": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 38,
        "text": "【文法パターン】something + be・seem・become・remain evident＝事実・状態などが明らかである／it + be・become + evident + that 〈節〉＝～であることが明らかだ／something + be evident to someone＝〈人〉にとって明らかだ／it + be evident to someone + that 〈節〉＝〈人〉には～が明らかだ／it + be evident from 〈data・evidence・behavior〉 + that 〈節〉＝〈データ・証拠・行動〉から～が明らかだ／something + be evident in 〈expression・results・pattern〉＝感情・特徴などが〈表情・結果・パターン〉に表れている／make something・make it evident + that 〈節〉＝何かを明白にする・～であることを明らかにする／evident + 〈change・difference・sign・need〉＝明らかな〈変化・違い・兆候・必要性〉。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 40,
        "text": "【コロケーション】"
      },
      {
        "line": 42,
        "text": "・it is evident that 〈節〉  "
      },
      {
        "line": 43,
        "text": "用途: 状況や観察結果から、ある判断が明らかだと述べる基本構文。  "
      },
      {
        "line": 44,
        "text": "例: It is evident that the current plan cannot meet the deadline.  "
      },
      {
        "line": 45,
        "text": "訳: 現在の計画では期限に間に合わないことが明らかだ。  "
      },
      {
        "line": 47,
        "text": "・be evident to someone  "
      },
      {
        "line": 48,
        "text": "用途: 何が誰にとって明らかなのかを示す。  "
      },
      {
        "line": 49,
        "text": "例: The benefits of the new system were immediately evident to the staff.  "
      },
      {
        "line": 50,
        "text": "訳: 新しいシステムの利点は職員にはすぐに明らかになった。  "
      },
      {
        "line": 52,
        "text": "・be evident from 〈data・evidence・results〉 that 〈節〉  "
      },
      {
        "line": 53,
        "text": "用途: 明白だと判断する根拠や情報源を示す。  "
      },
      {
        "line": 54,
        "text": "例: It was evident from the audit results that several invoices had been duplicated.  "
      },
      {
        "line": 55,
        "text": "訳: 監査結果から、複数の請求書が重複していたことは明らかだった。  "
      },
      {
        "line": 57,
        "text": "・be evident in 〈expression・behavior・pattern〉  "
      },
      {
        "line": 58,
        "text": "用途: 感情や特徴が表情・行動・結果などに現れていることを表す。  "
      },
      {
        "line": 59,
        "text": "例: Her disappointment was evident in the way she avoided eye contact.  "
      },
      {
        "line": 60,
        "text": "訳: 彼女が目を合わせようとしなかったことに、失望がはっきり表れていた。  "
      },
      {
        "line": 62,
        "text": "・become evident  "
      },
      {
        "line": 63,
        "text": "用途: 時間の経過や追加情報によって、それまで不明だったことが明らかになることを表す。  "
      },
      {
        "line": 64,
        "text": "例: The scale of the damage became evident after the smoke cleared.  "
      },
      {
        "line": 65,
        "text": "訳: 煙が晴れた後、被害の規模が明らかになった。  "
      },
      {
        "line": 67,
        "text": "・make it evident that 〈節〉  "
      },
      {
        "line": 68,
        "text": "用途: 数値、言動、結果などによって、ある判断を明白にする。  "
      },
      {
        "line": 69,
        "text": "例: The revised figures made it evident that the original estimate was too optimistic.  "
      },
      {
        "line": 70,
        "text": "訳: 修正後の数値によって、当初の見積もりが楽観的すぎたことが明らかになった。  "
      },
      {
        "line": 72,
        "text": "・evident signs of 〈change・stress・recovery〉  "
      },
      {
        "line": 73,
        "text": "用途: 変化、ストレス、回復などが起きていると分かる兆候を表す。  "
      },
      {
        "line": 74,
        "text": "例: The patient showed evident signs of recovery after the treatment.  "
      },
      {
        "line": 75,
        "text": "訳: その患者には治療後、回復の明らかな兆候が見られた。  "
      },
      {
        "line": 77,
        "text": "・with evident 〈relief・pleasure・concern〉  "
      },
      {
        "line": 78,
        "text": "用途: 表情や声などに感情が明確に現れている様子を表す。  "
      },
      {
        "line": 79,
        "text": "例: She spoke with evident relief after the results were announced.  "
      },
      {
        "line": 80,
        "text": "訳: 結果が発表された後、彼女はほっとした様子をはっきり見せて話した。  "
      }
    ],
    "usage_notes": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 82,
        "text": "【語法・注意】`evident to someone` は「誰にとって明らかか」、`evident from something` は「何を根拠に明らかか」、`evident in something` は「どこに表れているか」を示す。`evident that ...` のように内容を続ける場合は、通常 `It is evident that ...` と形式主語 it を置く。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 30,
        "text": "1. 【形容詞・限定用法／叙述用法】明らかな、明白な、はっきり表れている"
      },
      {
        "line": 88,
        "text": "【類義語】"
      },
      {
        "line": 90,
        "text": "・obvious  "
      },
      {
        "line": 91,
        "text": "定義: 見たり考えたりすれば容易に分かる、明白な。  "
      },
      {
        "line": 92,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 93,
        "text": "違い: obvious は日常的で、証拠がなくても直観的に分かることに使える。evident は兆候や状況から判断できることをやや形式的に述べる。  "
      },
      {
        "line": 94,
        "text": "例: It was obvious from his expression that he was disappointed.  "
      },
      {
        "line": 95,
        "text": "訳: 彼の表情から、彼が失望しているのは明らかだった。  "
      },
      {
        "line": 97,
        "text": "・clear  "
      },
      {
        "line": 98,
        "text": "定義: 意味・事実・状況などが疑いなく理解できる、明確な。  "
      },
      {
        "line": 99,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 100,
        "text": "違い: clear は説明や指示を「分かりやすくする」意図にも使え、対象範囲が広い。evident は観察可能な兆候から明らかになることに焦点を置きやすい。  "
      },
      {
        "line": 101,
        "text": "例: The instructions were clear to everyone on the team.  "
      },
      {
        "line": 102,
        "text": "訳: その指示はチームの全員にとって明確だった。  "
      },
      {
        "line": 104,
        "text": "・apparent  "
      },
      {
        "line": 105,
        "text": "定義: 観察や状況から、そうだと見て取れる・思われる。  "
      },
      {
        "line": 106,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 107,
        "text": "違い: apparent は「そう見える」という含みから、実際には異なる可能性を残すことがある。evident は通常、利用可能な兆候から明らかだという判断をより直接に表す。  "
      },
      {
        "line": 108,
        "text": "例: It soon became apparent that the schedule was unrealistic.  "
      },
      {
        "line": 109,
        "text": "訳: その予定が現実的でないことは、まもなく明らかになった。  "
      },
      {
        "line": 111,
        "text": "・plain  "
      },
      {
        "line": 112,
        "text": "定義: 隠れたところがなく、見たり聞いたりすれば明らかな。  "
      },
      {
        "line": 113,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 114,
        "text": "違い: plain は `plain to see`、`make it plain` などで、率直に明示する感じも持つ。evident は感情や結果が兆候として現れる説明に向く。  "
      },
      {
        "line": 115,
        "text": "例: It was plain to see that the proposal needed more work.  "
      },
      {
        "line": 116,
        "text": "訳: その提案にさらに検討が必要なのは一目瞭然だった。  "
      },
      {
        "line": 118,
        "text": "・manifest  "
      },
      {
        "line": 119,
        "text": "定義: 性質・事実・感情などがはっきり外に現れている、明白な。  "
      },
      {
        "line": 120,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 121,
        "text": "違い: manifest は evident より硬く、文学・学術・形式的な文脈で、隠れたものが明確に現れたことを強調する。  "
      },
      {
        "line": 122,
        "text": "例: The report revealed a manifest lack of oversight.  "
      },
      {
        "line": 123,
        "text": "訳: その報告書は監督が明らかに欠けていたことを示した。  "
      },
      {
        "line": 125,
        "text": "・noticeable  "
      },
      {
        "line": 126,
        "text": "定義: 見たり感じたりして気づくことができる、目立つ。  "
      },
      {
        "line": 127,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 128,
        "text": "違い: noticeable は知覚上の目立ちやすさに焦点があり、そこから命題や判断が理解できることまでは含まない。evident は抽象的な事実や結論にも使える。  "
      },
      {
        "line": 129,
        "text": "例: There was a noticeable change in his attitude.  "
      },
      {
        "line": 130,
        "text": "訳: 彼の態度には目立った変化があった。  "
      },
      {
        "line": 132,
        "text": "【反意語】"
      },
      {
        "line": 134,
        "text": "・unclear  "
      },
      {
        "line": 135,
        "text": "定義: 意味・理由・状況などがはっきりせず、容易には理解できない。  "
      },
      {
        "line": 136,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 137,
        "text": "違い: evident の「情報や兆候から明らかである」という理解可能性の軸に対し、unclear は解釈や判断がまだ定まらない状態を表す。  "
      },
      {
        "line": 138,
        "text": "例: The reason for the sudden change remains unclear.  "
      },
      {
        "line": 139,
        "text": "訳: その突然の変化の理由は依然として不明だ。  "
      },
      {
        "line": 141,
        "text": "・obscure  "
      },
      {
        "line": 142,
        "text": "定義: 見えにくく、知られておらず、理解しにくい。  "
      },
      {
        "line": 143,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 144,
        "text": "違い: obscure は情報や特徴が隠れている・目立たないために認識しにくいことを強調し、evident の「前面に現れて分かる」と程度の軸で対照をなす。  "
      },
      {
        "line": 145,
        "text": "例: The connection between the two events was initially obscure.  "
      },
      {
        "line": 146,
        "text": "訳: その2つの出来事のつながりは、当初は分かりにくかった。  "
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
    "input_body_sha256": "7daa0d416ecef06000548e2f59c08bd4394750574e23f19e24855a4a6339257a",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "1d7ca9841a8fbec70cc511984246c0c3b31846a3c20f497d78147f596066ed3e",
    "source_first_artifact_sha256": "30b66db08f75dd69b45d2c04e3c7e49edce013c046dafbcd965f201c1691195c",
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
        "id": "S002",
        "locator": "https://www.oxfordlearnersdictionaries.com/definition/english/evident",
        "source_type": "learner_dictionary",
        "independence_group": "oxford_university_press",
        "facts": [
          {
            "id": "F004",
            "form": "evident",
            "kind": "pronunciation",
            "statement": "Oxford gives /ˈevɪdənt/ in both its British and American panels.",
            "source_detail": "The entry prints the IPA form above the definition in both regional panels."
          },
          {
            "id": "F008",
            "form": "evident",
            "kind": "etymology",
            "statement": "Evident entered English from Old French or Latin evidens, evident-, related to e-/ex- and videre ‘to see’.",
            "source_detail": "Oxford's word-origin note gives the late Middle English route and the Latin components."
          }
        ]
      },
      {
        "id": "S003",
        "locator": "https://www.merriam-webster.com/dictionary/evident",
        "source_type": "general_dictionary",
        "independence_group": "merriam_webster",
        "facts": [
          {
            "id": "F010",
            "form": "evident",
            "kind": "etymology",
            "statement": "The first known use of evident is in the 14th century and its history passes through Middle English, Anglo-French, and Latin.",
            "source_detail": "Merriam-Webster gives the first-known-use century and the Latin evidens etymology."
          }
        ]
      },
      {
        "id": "S004",
        "locator": "https://www.etymonline.com/word/evident",
        "source_type": "etymology_dictionary",
        "independence_group": "etymonline",
        "facts": [
          {
            "id": "F011",
            "form": "evident",
            "kind": "etymology",
            "statement": "Evident means plainly seen or perceived and goes through Old French to Latin evidentem, from ex and videre.",
            "source_detail": "Etymonline traces the late-fourteenth-century adjective and explains the Latin elements."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "U004",
        "source_fact_ids": [
          "F004"
        ],
        "canonical_statement": "The current learner-dictionary pronunciation is /ˈevɪdənt/.",
        "disposition": "included",
        "rationale": "The IPA and its stress explanation are stated in the pronunciation section."
      },
      {
        "id": "U005",
        "source_fact_ids": [
          "F008",
          "F010",
          "F011"
        ],
        "canonical_statement": "Evident has a late Middle English history connected through French and Latin to the idea of seeing clearly.",
        "disposition": "included",
        "rationale": "Multiple etymological references support the bounded origin explanation."
      }
    ],
    "claim_units": [
      {
        "id": "C004",
        "union_ids": [
          "U004"
        ],
        "subject_form": "evident",
        "claim_type": "pronunciation",
        "statement": "Evident is pronounced /ˈevɪdənt/ with first-syllable stress in the cited learner-dictionary representation.",
        "article_target_ids": [
          "pronunciation"
        ],
        "source_supports": [
          {
            "source_fact_id": "F004",
            "support_summary": "Oxford prints /ˈevɪdənt/ in both regional panels."
          }
        ]
      },
      {
        "id": "C005",
        "union_ids": [
          "U005"
        ],
        "subject_form": "evident",
        "claim_type": "etymology",
        "statement": "The word's history connects French and Latin forms with seeing and clear perception.",
        "article_target_ids": [
          "etymology"
        ],
        "source_supports": [
          {
            "source_fact_id": "F008",
            "support_summary": "Oxford gives the Old French or Latin route and videre connection."
          },
          {
            "source_fact_id": "F010",
            "support_summary": "Merriam-Webster supplies the Middle English, Anglo-French, and Latin history."
          },
          {
            "source_fact_id": "F011",
            "support_summary": "Etymonline gives evidentem from ex and videre and the plainly-seen sense."
          }
        ]
      }
    ]
  },
  "specification_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
  "source_artifact_sha256": "30b66db08f75dd69b45d2c04e3c7e49edce013c046dafbcd965f201c1691195c",
  "normalized_input_sha256": "7d4abeb19fce096f5eb933720db9a99adfb619630e2a15889357c18cb795c497"
}
```
