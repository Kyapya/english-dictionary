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
  "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
  "input_sections": {
    "pronunciation": [
      {
        "line": 13,
        "text": "＃発音記号"
      },
      {
        "line": 15,
        "text": "動詞は米・英: /kənˈfaɪn/。2音節で第2音節に主強勢があり、第1音節の母音は弱い /ə/ になる。低頻度の名詞は、米: /ˈkɑːnfaɪn/｜英: /ˈkɒnfaɪn/ で、第1音節に主強勢が移り、第1音節の母音にも米英差がある。動詞の三人称単数形 confines は /kənˈfaɪnz/、過去形・過去分詞 confined は /kənˈfaɪnd/、-ing形 confining は /kənˈfaɪnɪŋ/ と発音する。  "
      }
    ],
    "etymology": [
      {
        "line": 17,
        "text": "＃語源"
      },
      {
        "line": 19,
        "text": "動詞は中期フランス語 confiner「境を接する、限界内にとどめる」から英語に入り、さらにラテン語 confinis「境を接する」にさかのぼる。con-「共に」と finis「境界、終わり」が結び付いた語で、「境界の内側に置く」という意味の核が、現代の「範囲を限る」「閉じ込める」につながった。名詞はフランス語の複数形 confins「境界」などを経て英語に入った。finite「有限の」、final「最後の」もラテン語 finis と関係する。  "
      }
    ],
    "word_formation": [
      {
        "line": 21,
        "text": "＃語形成"
      },
      {
        "line": 23,
        "text": "・confinement（名詞）— 閉じ込めること、拘禁、行動範囲が限られた状態。文脈によって物理的拘束、病気による外出不能、限定された環境などを表す。  "
      },
      {
        "line": 24,
        "text": "・confined（形容詞）— 狭く囲まれた、限られた。単なる過去分詞としての受動用法と、confined space のような形容詞用法がある。  "
      },
      {
        "line": 25,
        "text": "・confining（形容詞）— 自由な動きや活動を妨げる、窮屈な。物理的な狭さだけでなく、服装・役割・生活環境などの制約にも使う。  "
      },
      {
        "line": 26,
        "text": "・unconfined（形容詞）— 閉じ込められていない、境界内に制限されていない。一般語としては limited や restricted ほど頻繁ではない。  "
      }
    ],
    "core_image": [
      {
        "line": 28,
        "text": "＃コアイメージ"
      },
      {
        "line": 30,
        "text": "人・物・活動・内容などを、ある境界の内側にとどめ、外へ出たり広がったりしないようにする。形容詞ではその結果の状態や窮屈さを、名詞では境界そのものを表す。  "
      },
      {
        "line": 32,
        "text": "・対象の範囲を一定の境界内にとどめる → 「～を…に限る、限定する」（語義1）  "
      },
      {
        "line": 33,
        "text": "・人や動物を一定の場所から出られなくする → 「閉じ込める、拘束する」（語義2）  "
      },
      {
        "line": 34,
        "text": "・病気やけがで生活場所を狭い範囲にとどめる → 「～を寝床・自宅などにとどめる」（語義3）  "
      },
      {
        "line": 35,
        "text": "・空間や区域が狭い境界内に収まった状態 → 「狭く囲まれた、限られた」（語義4）  "
      },
      {
        "line": 36,
        "text": "・内外を分けて範囲を画する境界 → 「境界、範囲、領域」（語義5）  "
      }
    ],
    "sense_structure": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 42,
        "text": "【日本語訳・定義】話題、活動、作業、影響、現象などが及ぶ範囲を、特定の対象・場所・期間・分野などの内側に限定する。対象がすでにその範囲に収まっていることを述べる受動形と、話し手が意識的に扱う範囲を絞る能動形・再帰形の両方がよく使われる。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 120,
        "text": "【日本語訳・定義】人や動物を、部屋、施設、囲い、刑務所などの外へ自由に出られないようにする。物理的な障壁、命令、拘禁などによる移動の制限を表し、本人の自由意思で滞在している場合には通常使わない。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 193,
        "text": "【日本語訳・定義】病気、けが、身体状態などが原因で、人がベッド、自宅、病室など限られた場所から動けない、または外出できない状態にする。原因を主語にする能動文も可能だが、本人を主語にした be confined to が特に多い。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 250,
        "text": "【日本語訳・定義】confined の形で、空間や区域が壁や境界に囲まれて狭い、または内部で動ける余地が少ないことを表す。単に面積が小さいだけでなく、閉鎖性や動きにくさを含みやすい。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 323,
        "text": "【日本語訳・定義】通常 confines の形で、場所・組織・分野などの外縁をなす境界、またはその境界に囲まれた内部の領域を表す。現代の一般的な文章では単数形 confine より複数形 confines が圧倒的に普通である。  "
      }
    ],
    "frequency_register": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 44,
        "text": "【頻度】〈8/10〉  "
      },
      {
        "line": 46,
        "text": "【レジスター/領域】一般語だが、日常会話より文章、ニュース、ビジネス、学術的説明でやや多い。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 122,
        "text": "【頻度】〈7/10〉  "
      },
      {
        "line": 124,
        "text": "【レジスター/領域】一般語。ニュース、法律・刑事、軍事、動物管理の文脈でよく使われる。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 195,
        "text": "【頻度】〈6/10〉  "
      },
      {
        "line": 197,
        "text": "【レジスター/領域】一般語・医療関連。病状や回復期間を述べるやや硬い表現。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 252,
        "text": "【頻度】〈6/10〉  "
      },
      {
        "line": 254,
        "text": "【レジスター/領域】一般語。confined space は日常的説明のほか、労働安全の専門用語としても使われる。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 325,
        "text": "【頻度】〈4/10〉  "
      },
      {
        "line": 327,
        "text": "【レジスター/領域】格式的・文学的。within/beyond/outside the confines of の形で、抽象的・物理的な範囲を述べる文章に使われる。  "
      }
    ],
    "frames": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 48,
        "text": "【文法パターン】confine something to 〈範囲・場所・期間・活動〉＝何かを～の範囲内に限る／confine oneself to 〈名詞・doing〉＝自分が扱う内容・行うことを～だけにする／be confined to 〈範囲・場所・集団〉＝～に限られている／confine 〈発言・検討・努力〉 to 〈対象〉＝発言・検討・努力の対象を～に絞る  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 126,
        "text": "【文法パターン】confine someone/something in 〈閉鎖場所〉＝人・動物を～の中に閉じ込める／confine someone/something to 〈場所〉＝人・動物を～から出られないようにする／be confined in 〈施設・部屋〉＝～に収容・拘束されている／be confined to quarters＝兵舎・自室待機を命じられている  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 199,
        "text": "【文法パターン】〈病気・けが・身体状態〉 confine someone to 〈bed/home/a room〉＝病気などが人を～から動けない状態にする／someone be confined to bed/home＝人が病気などで寝床・自宅から動けない／someone be confined to 〈場所〉 with/by 〈病気・けが〉＝病気・けがにより～にとどまっている  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 256,
        "text": "【文法パターン】a confined 〈space/area/place〉＝狭く囲まれた空間・区域／in confined 〈conditions/quarters〉＝狭く限られた環境で／feel confined＝閉じ込められたように感じる  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 329,
        "text": "【文法パターン】within the confines of 〈場所・制度・分野〉＝～の範囲内で／beyond the confines of 〈場所・制度・分野〉＝～の境界を越えて／outside the confines of 〈場所・制度・分野〉＝～の範囲外で／the narrow confines of 〈場所・枠組み〉＝～という狭い範囲  "
      }
    ],
    "collocations_examples": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 50,
        "text": "【コロケーション】"
      },
      {
        "line": 52,
        "text": "・confine the discussion to 〈話題〉  "
      },
      {
        "line": 53,
        "text": "用途: 議論で扱う範囲を特定の話題に限定する。  "
      },
      {
        "line": 54,
        "text": "例: Please confine the discussion to the issues on today's agenda.  "
      },
      {
        "line": 55,
        "text": "訳: 議論は本日の議題にある問題だけに絞ってください。  "
      },
      {
        "line": 57,
        "text": "・confine one's remarks to 〈対象〉  "
      },
      {
        "line": 58,
        "text": "用途: 発言する内容を特定の対象に限る。  "
      },
      {
        "line": 59,
        "text": "例: She confined her remarks to the financial risks of the proposal.  "
      },
      {
        "line": 60,
        "text": "訳: 彼女は発言をその提案の財務上のリスクに限定した。  "
      },
      {
        "line": 62,
        "text": "・confine oneself to 〈名詞・doing〉  "
      },
      {
        "line": 63,
        "text": "用途: 自分が扱う話題や行う活動を意識的に一つの範囲へ絞る。  "
      },
      {
        "line": 64,
        "text": "例: In this chapter, I will confine myself to examining the short-term effects.  "
      },
      {
        "line": 65,
        "text": "訳: この章では、短期的な影響の検討だけに対象を絞る。  "
      },
      {
        "line": 67,
        "text": "・be confined to 〈場所・集団〉  "
      },
      {
        "line": 68,
        "text": "用途: 問題、特徴、現象などが特定の場所や集団だけに見られることを表す。  "
      },
      {
        "line": 69,
        "text": "例: The shortage is not confined to rural areas.  "
      },
      {
        "line": 70,
        "text": "訳: その不足は農村部だけに限られた問題ではない。  "
      },
      {
        "line": 72,
        "text": "・confine 〈物質・作用〉 to 〈区域・装置〉  "
      },
      {
        "line": 73,
        "text": "用途: 物質、熱、火、プラズマなどが外へ広がらないよう一定の区域内に保つ。  "
      },
      {
        "line": 74,
        "text": "例: The magnetic field confines the plasma to the center of the chamber.  "
      },
      {
        "line": 75,
        "text": "訳: その磁場はプラズマを容器の中心部に閉じ込める。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 128,
        "text": "【コロケーション】"
      },
      {
        "line": 130,
        "text": "・confine someone in a cell  "
      },
      {
        "line": 131,
        "text": "用途: 人を独房などの閉鎖された空間から出られないようにする。  "
      },
      {
        "line": 132,
        "text": "例: The prisoner was confined in a windowless cell for several days.  "
      },
      {
        "line": 133,
        "text": "訳: その囚人は数日間、窓のない独房に拘禁された。  "
      },
      {
        "line": 135,
        "text": "・confine an animal to 〈囲い・ケージ〉  "
      },
      {
        "line": 136,
        "text": "用途: 動物が指定された囲いの外へ出ないようにする。  "
      },
      {
        "line": 137,
        "text": "例: The injured bird was temporarily confined to a large enclosure.  "
      },
      {
        "line": 138,
        "text": "訳: けがをした鳥は一時的に大きな囲いの中で保護された。  "
      },
      {
        "line": 140,
        "text": "・keep 〈人・動物〉 confined  "
      },
      {
        "line": 141,
        "text": "用途: 人や動物を外へ出られない状態に保つ。  "
      },
      {
        "line": 142,
        "text": "例: The order kept the soldiers confined to their barracks overnight.  "
      },
      {
        "line": 143,
        "text": "訳: その命令により兵士たちは一晩、兵舎から出られなかった。  "
      },
      {
        "line": 145,
        "text": "・be confined to quarters  "
      },
      {
        "line": 146,
        "text": "用途: 軍人などが処罰・命令により兵舎や指定場所から出ないよう命じられた状態を表す。  "
      },
      {
        "line": 147,
        "text": "例: He was confined to quarters for disobeying the order.  "
      },
      {
        "line": 148,
        "text": "訳: 彼は命令に従わなかったため、兵舎待機を命じられた。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 201,
        "text": "【コロケーション】"
      },
      {
        "line": 203,
        "text": "・be confined to bed  "
      },
      {
        "line": 204,
        "text": "用途: 病気やけがのため起きて普段どおり活動できず、寝床にとどまる。  "
      },
      {
        "line": 205,
        "text": "例: She was confined to bed for a week with a severe infection.  "
      },
      {
        "line": 206,
        "text": "訳: 彼女は重い感染症のため1週間、寝床から起きられなかった。  "
      },
      {
        "line": 208,
        "text": "・be confined to one's home  "
      },
      {
        "line": 209,
        "text": "用途: 健康上の理由などで外出できず、自宅にとどまる。  "
      },
      {
        "line": 210,
        "text": "例: After the operation, he was confined to his home for several days.  "
      },
      {
        "line": 211,
        "text": "訳: 手術後、彼は数日間、自宅から出られなかった。  "
      },
      {
        "line": 213,
        "text": "・〈病気・けが〉 confine someone to 〈場所〉  "
      },
      {
        "line": 214,
        "text": "用途: 病気やけがを原因として、人の行動範囲が特定の場所に限られることを表す。  "
      },
      {
        "line": 215,
        "text": "例: A knee injury confined her to the apartment for most of the winter.  "
      },
      {
        "line": 216,
        "text": "訳: 膝のけがのため、彼女は冬の大半をアパートから出られずに過ごした。  "
      },
      {
        "line": 218,
        "text": "・be temporarily confined to 〈場所〉  "
      },
      {
        "line": 219,
        "text": "用途: 限られた期間だけ、健康上の理由で一定の場所にとどまることを表す。  "
      },
      {
        "line": 220,
        "text": "例: He is temporarily confined to his room while he recovers.  "
      },
      {
        "line": 221,
        "text": "訳: 彼は回復するまで一時的に自室で過ごさなければならない。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 258,
        "text": "【コロケーション】"
      },
      {
        "line": 260,
        "text": "・a confined space  "
      },
      {
        "line": 261,
        "text": "用途: 壁や境界に囲まれ、動きや出入りが制限されやすい空間を表す。  "
      },
      {
        "line": 262,
        "text": "例: The machine should not be operated in a confined space without adequate ventilation.  "
      },
      {
        "line": 263,
        "text": "訳: その機械は、十分な換気のない閉鎖空間で作動させるべきではない。  "
      },
      {
        "line": 265,
        "text": "・in confined quarters  "
      },
      {
        "line": 266,
        "text": "用途: 人が動ける余地の少ない狭い居住・作業場所にいることを表す。  "
      },
      {
        "line": 267,
        "text": "例: The crew lived in confined quarters during the voyage.  "
      },
      {
        "line": 268,
        "text": "訳: 乗組員は航海中、狭い居住区で暮らした。  "
      },
      {
        "line": 270,
        "text": "・work in confined conditions  "
      },
      {
        "line": 271,
        "text": "用途: 動作や移動の余地が限られた環境で作業する。  "
      },
      {
        "line": 272,
        "text": "例: The technicians had to work in confined conditions beneath the stage.  "
      },
      {
        "line": 273,
        "text": "訳: 技術者たちは舞台の下の狭い環境で作業しなければならなかった。  "
      },
      {
        "line": 275,
        "text": "・feel confined in 〈場所〉  "
      },
      {
        "line": 276,
        "text": "用途: 場所が狭い、または自由に動けず、閉じ込められたように感じる。  "
      },
      {
        "line": 277,
        "text": "例: I felt confined in the tiny room after only a few hours.  "
      },
      {
        "line": 278,
        "text": "訳: その小さな部屋に数時間いただけで、私は閉じ込められたように感じた。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 331,
        "text": "【コロケーション】"
      },
      {
        "line": 333,
        "text": "・within the confines of 〈場所・制度〉  "
      },
      {
        "line": 334,
        "text": "用途: 物理的または制度的な境界の内側にあることを表す。  "
      },
      {
        "line": 335,
        "text": "例: The negotiations took place within the confines of the embassy.  "
      },
      {
        "line": 336,
        "text": "訳: 交渉は大使館の敷地内で行われた。  "
      },
      {
        "line": 338,
        "text": "・beyond the confines of 〈場所・分野〉  "
      },
      {
        "line": 339,
        "text": "用途: 場所や分野の既存の境界を越えて及ぶことを表す。  "
      },
      {
        "line": 340,
        "text": "例: Her influence extended far beyond the confines of the university.  "
      },
      {
        "line": 341,
        "text": "訳: 彼女の影響力は大学の枠をはるかに越えて広がった。  "
      },
      {
        "line": 343,
        "text": "・outside the confines of 〈制度・枠組み〉  "
      },
      {
        "line": 344,
        "text": "用途: 制度や枠組みが定める範囲の外側にあることを表す。  "
      },
      {
        "line": 345,
        "text": "例: The group continued its work outside the confines of the formal organization.  "
      },
      {
        "line": 346,
        "text": "訳: そのグループは正式な組織の枠外でも活動を続けた。  "
      },
      {
        "line": 348,
        "text": "・the narrow confines of 〈場所・枠組み〉  "
      },
      {
        "line": 349,
        "text": "用途: 物理的・抽象的な範囲が狭く、制約的であることを強調する。  "
      },
      {
        "line": 350,
        "text": "例: The story moves beyond the narrow confines of a family dispute.  "
      },
      {
        "line": 351,
        "text": "訳: その物語は家族間の争いという狭い枠を越えて展開する。  "
      }
    ],
    "usage_notes": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 77,
        "text": "【語法・注意】基本形は confine A to B であり、to の後ろには名詞または動名詞を置く。×confine A in doing B のように範囲を示す前置詞を機械的に in に替えない。場所の内部へ物理的に閉じ込める語義2では confine someone in a cell のように in も使う。confine oneself to は「自分を物理的に閉じ込める」ではなく、通常「話題・活動を自分で限定する」という再帰構文である。受動形 be confined to は、否定や mainly、largely などと結び付き、「～だけに限られる／限られない」を表しやすい。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 150,
        "text": "【語法・注意】この語義では能動形も可能だが、拘束される側を主語にした be confined in/to が多い。in は容器・部屋・施設の「内部」を、to は移動可能な「範囲」を示す。imprison は人を刑務所に入れる法的・物理的な拘禁に焦点があり、動物や一時的な行動制限には使いにくい。confine は刑罰に限らず、命令や安全上の理由による拘束にも使える。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 223,
        "text": "【語法・注意】be confined to a wheelchair は従来から見られる表現だが、車いすを人を閉じ込める物として否定的に描くため、不快・不適切と受け取られることがある。単に移動手段を述べるなら use a wheelchair または be a wheelchair user を用いる。be confined to bed は病気などで起きられない状態を表し、単にベッドで休む choose to stay in bed とは異なる。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 280,
        "text": "【語法・注意】confined space は一般には狭く囲まれた空間を表すが、労働安全上の専門用語では法域や制度ごとに定義・要件があるため、小さい部屋をすべて専門上の confined space と断定しない。be confined to 〈場所・範囲〉は動詞 confine の受動形で「～に限定・拘束されている」、a confined space は形容詞 confined が名詞を修飾して「狭く囲まれた空間」である。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 353,
        "text": "【語法・注意】名詞では動詞と強勢位置が異なる。現代英語では通常 the confines of ... の複数形で使い、単数の a confine はまれである。confines は「境界線」そのものと「境界に囲まれた領域」の両方を表し得るため、within the confines of the park は通常「公園の区域内」、beyond the confines of the law は比喩的に「法の枠を越えて」と理解する。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 40,
        "text": "1. 【他動詞】～を…に限る、限定する"
      },
      {
        "line": 79,
        "text": "【類義語】"
      },
      {
        "line": 81,
        "text": "・limit  "
      },
      {
        "line": 82,
        "text": "定義: 数量、範囲、程度、時間などに限度を設ける。  "
      },
      {
        "line": 83,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 84,
        "text": "違い: limit は最も広く中立的で、上限を設ける場合にも使う。confine は対象をある境界の内側にとどめ、外へ広げないイメージが強い。  "
      },
      {
        "line": 85,
        "text": "例: The policy limits each application to two pages.  "
      },
      {
        "line": 86,
        "text": "訳: その方針では各申請書を2ページまでに制限している。  "
      },
      {
        "line": 88,
        "text": "・restrict  "
      },
      {
        "line": 89,
        "text": "定義: 規則、条件、権限などによって範囲や自由を制限する。  "
      },
      {
        "line": 90,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 91,
        "text": "違い: restrict は許可・利用・行動への制約を広く表す。confine A to B は、AがBの外へ及ばないという境界を特に示す。  "
      },
      {
        "line": 92,
        "text": "例: Access is restricted to authorized staff.  "
      },
      {
        "line": 93,
        "text": "訳: 立ち入りは権限のある職員に制限されている。  "
      },
      {
        "line": 95,
        "text": "・circumscribe  "
      },
      {
        "line": 96,
        "text": "定義: 活動、権限、可能性などの範囲を狭く限定する。  "
      },
      {
        "line": 97,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 98,
        "text": "違い: circumscribe は非常に硬い語で、抽象的な権限・選択肢・行動範囲が制約される文脈に多い。confine の方が一般的で、具体的な場所にも使える。  "
      },
      {
        "line": 99,
        "text": "例: The constitution circumscribes the powers of the executive.  "
      },
      {
        "line": 100,
        "text": "訳: 憲法は行政府の権限の範囲を限定している。  "
      },
      {
        "line": 102,
        "text": "【反意語】"
      },
      {
        "line": 104,
        "text": "・broaden  "
      },
      {
        "line": 105,
        "text": "定義: 話題、活動、対象などの範囲を広げる。  "
      },
      {
        "line": 106,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 107,
        "text": "違い: 範囲を狭く限定する confine と、同じ範囲軸上で外側へ広げる方向の対立をなす。  "
      },
      {
        "line": 108,
        "text": "例: The committee broadened the inquiry to include safety concerns.  "
      },
      {
        "line": 109,
        "text": "訳: 委員会は安全上の懸念も含めるよう調査範囲を広げた。  "
      },
      {
        "line": 111,
        "text": "・extend  "
      },
      {
        "line": 112,
        "text": "定義: 対象となる範囲、期間、適用先などをさらに先まで広げる。  "
      },
      {
        "line": 113,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 114,
        "text": "違い: confine A to B がAの到達範囲をB内に止めるのに対し、extend A to B はAの到達範囲をBまで広げる。  "
      },
      {
        "line": 115,
        "text": "例: The program was extended to smaller communities.  "
      },
      {
        "line": 116,
        "text": "訳: その制度はより小さな地域にも拡大された。  "
      },
      {
        "line": 118,
        "text": "2. 【他動詞・通常受動】人・動物を閉じ込める、拘束する"
      },
      {
        "line": 152,
        "text": "【類義語】"
      },
      {
        "line": 154,
        "text": "・imprison  "
      },
      {
        "line": 155,
        "text": "定義: 人を刑務所などに入れて自由を奪う。  "
      },
      {
        "line": 156,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 157,
        "text": "違い: imprison は刑罰・政治的拘禁など人の収監を中心とする。confine は人以外の動物や、刑務所以外の限定された場所にも使える。  "
      },
      {
        "line": 158,
        "text": "例: The regime imprisoned several opposition leaders.  "
      },
      {
        "line": 159,
        "text": "訳: その政権は複数の反対派指導者を投獄した。  "
      },
      {
        "line": 161,
        "text": "・detain  "
      },
      {
        "line": 162,
        "text": "定義: 当局などが人を一定時間引き留め、立ち去れないようにする。  "
      },
      {
        "line": 163,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 164,
        "text": "違い: detain は一時的な身柄拘束や事情聴取のための留置に焦点がある。confine は場所の境界内に置かれる状態を強く示す。  "
      },
      {
        "line": 165,
        "text": "例: Police detained the suspect for questioning.  "
      },
      {
        "line": 166,
        "text": "訳: 警察は事情聴取のため容疑者を拘束した。  "
      },
      {
        "line": 168,
        "text": "・enclose  "
      },
      {
        "line": 169,
        "text": "定義: 物や場所の周囲を囲い、その内側に収める。  "
      },
      {
        "line": 170,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 171,
        "text": "違い: enclose は囲いを作ることに焦点があり、対象の自由を奪う含みは必須ではない。confine は外へ出られないという制限を前面に出す。  "
      },
      {
        "line": 172,
        "text": "例: A stone wall enclosed the garden.  "
      },
      {
        "line": 173,
        "text": "訳: 石垣が庭を取り囲んでいた。  "
      },
      {
        "line": 175,
        "text": "【反意語】"
      },
      {
        "line": 177,
        "text": "・release  "
      },
      {
        "line": 178,
        "text": "定義: 拘束・収容されている人や動物を自由にする。  "
      },
      {
        "line": 179,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 180,
        "text": "違い: 閉鎖場所内にとどめる confine に対し、そこから出ることを許す方向の対立をなす。  "
      },
      {
        "line": 181,
        "text": "例: The authorities released the detainees the next morning.  "
      },
      {
        "line": 182,
        "text": "訳: 当局は翌朝、被拘束者たちを解放した。  "
      },
      {
        "line": 184,
        "text": "・free  "
      },
      {
        "line": 185,
        "text": "定義: 束縛、監禁、拘束などから自由にする。  "
      },
      {
        "line": 186,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 187,
        "text": "違い: confine が移動の自由を奪うのに対し、free はその拘束自体を取り除く。release より広く、物理的・制度的・比喩的拘束に使える。  "
      },
      {
        "line": 188,
        "text": "例: The rescue team freed the animals from the locked shed.  "
      },
      {
        "line": 189,
        "text": "訳: 救助隊は鍵のかかった小屋から動物たちを解放した。  "
      },
      {
        "line": 191,
        "text": "3. 【他動詞・通常受動】～を寝床・自宅などにとどめる"
      },
      {
        "line": 225,
        "text": "【類義語】"
      },
      {
        "line": 227,
        "text": "・be bedridden  "
      },
      {
        "line": 228,
        "text": "定義: 病気、けが、高齢などで寝床から離れられない状態にある。  "
      },
      {
        "line": 229,
        "text": "頻度: 〈5/10〉  "
      },
      {
        "line": 230,
        "text": "違い: be bedridden は比較的長い・重い状態を表しやすい形容詞表現である。be confined to bed は一時的な病気にも使える。  "
      },
      {
        "line": 231,
        "text": "例: He was bedridden for months after the stroke.  "
      },
      {
        "line": 232,
        "text": "訳: 彼は脳卒中の後、何か月も寝たきりだった。  "
      },
      {
        "line": 234,
        "text": "・be housebound  "
      },
      {
        "line": 235,
        "text": "定義: 身体状態などのため自宅から外出することが難しい。  "
      },
      {
        "line": 236,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 237,
        "text": "違い: be housebound は自宅の外へ出にくい状態そのものを表す。be confined to one's home は原因によって行動範囲が自宅内に限られたことを描く。  "
      },
      {
        "line": 238,
        "text": "例: The service delivers meals to older people who are housebound.  "
      },
      {
        "line": 239,
        "text": "訳: そのサービスは外出困難な高齢者に食事を届ける。  "
      },
      {
        "line": 241,
        "text": "・be restricted to 〈場所・活動〉  "
      },
      {
        "line": 242,
        "text": "定義: 許可や身体状態などにより、場所・活動の範囲が限られている。  "
      },
      {
        "line": 243,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 244,
        "text": "違い: be restricted to は原因を問わない中立的な制限表現である。be confined to は移動できない、または外へ出られないという強い制約を示しやすい。  "
      },
      {
        "line": 245,
        "text": "例: During recovery, she was restricted to light indoor activities.  "
      },
      {
        "line": 246,
        "text": "訳: 回復中、彼女の活動は屋内での軽いものに限られた。  "
      },
      {
        "line": 248,
        "text": "4. 【形容詞】狭く囲まれた、限られた"
      },
      {
        "line": 282,
        "text": "【類義語】"
      },
      {
        "line": 284,
        "text": "・enclosed  "
      },
      {
        "line": 285,
        "text": "定義: 壁、柵、覆いなどによって周囲を囲まれた。  "
      },
      {
        "line": 286,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 287,
        "text": "違い: enclosed は囲いの存在を表すが、狭さや窮屈さは必須ではない。confined は空間や動きが限られる含みを持ちやすい。  "
      },
      {
        "line": 288,
        "text": "例: The garden is surrounded by an enclosed walkway.  "
      },
      {
        "line": 289,
        "text": "訳: その庭は屋根と壁のある通路に囲まれている。  "
      },
      {
        "line": 291,
        "text": "・cramped  "
      },
      {
        "line": 292,
        "text": "定義: 人や物に対して利用できる空間が足りず、窮屈な。  "
      },
      {
        "line": 293,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 294,
        "text": "違い: cramped は狭さによる不快さを直接強調する。confined は境界に囲まれ、動きが制限される構造に焦点がある。  "
      },
      {
        "line": 295,
        "text": "例: Four people shared a cramped cabin.  "
      },
      {
        "line": 296,
        "text": "訳: 4人が窮屈な船室を共有した。  "
      },
      {
        "line": 298,
        "text": "・restricted  "
      },
      {
        "line": 299,
        "text": "定義: 利用、移動、範囲などが制限された。  "
      },
      {
        "line": 300,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 301,
        "text": "違い: restricted は規則や条件による抽象的制限にも広く使う。confined は特に空間的な閉鎖性を示しやすい。  "
      },
      {
        "line": 302,
        "text": "例: The equipment operates in a restricted area.  "
      },
      {
        "line": 303,
        "text": "訳: その装置は立ち入り制限区域で稼働している。  "
      },
      {
        "line": 305,
        "text": "【反意語】"
      },
      {
        "line": 307,
        "text": "・spacious  "
      },
      {
        "line": 308,
        "text": "定義: 人や物がゆったり動ける十分な空間がある。  "
      },
      {
        "line": 309,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 310,
        "text": "違い: 動ける余地が少ない confined と、空間に十分な余裕がある spacious は広さ・窮屈さの軸で対立する。  "
      },
      {
        "line": 311,
        "text": "例: The new cabin is bright and spacious.  "
      },
      {
        "line": 312,
        "text": "訳: 新しい船室は明るく広々としている。  "
      },
      {
        "line": 314,
        "text": "・open  "
      },
      {
        "line": 315,
        "text": "定義: 閉鎖されず、周囲や上部が広く開けている。  "
      },
      {
        "line": 316,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 317,
        "text": "違い: 境界に囲まれた confined に対し、open は閉鎖性が少なく外へ開かれた状態を表す。文脈によっては広さではなく出入り可能性の対立になる。  "
      },
      {
        "line": 318,
        "text": "例: We moved the meeting to an open area outside.  "
      },
      {
        "line": 319,
        "text": "訳: 私たちは会議を屋外の開けた場所に移した。  "
      },
      {
        "line": 321,
        "text": "5. 【名詞・通常複数・格式／文学的】境界、範囲、領域"
      },
      {
        "line": 355,
        "text": "【類義語】"
      },
      {
        "line": 357,
        "text": "・bounds  "
      },
      {
        "line": 358,
        "text": "定義: 許容範囲、領域、行動などの境界・限界。  "
      },
      {
        "line": 359,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 360,
        "text": "違い: bounds も通常複数で、out of bounds など定着表現が多い。confines は境界に囲まれた内部の領域まで意識させやすく、より格式的である。  "
      },
      {
        "line": 361,
        "text": "例: The proposal falls outside the bounds of the agreement.  "
      },
      {
        "line": 362,
        "text": "訳: その提案は合意の範囲外である。  "
      },
      {
        "line": 364,
        "text": "・limits  "
      },
      {
        "line": 365,
        "text": "定義: 範囲、能力、権限などがそれ以上及ばない境界。  "
      },
      {
        "line": 366,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 367,
        "text": "違い: limits は最も一般的で、数量的な上限にも使える。confines は場所・制度・分野を囲む境界や領域を表す格式的な語である。  "
      },
      {
        "line": 368,
        "text": "例: The plan remains within the limits of the current budget.  "
      },
      {
        "line": 369,
        "text": "訳: その計画は現在の予算の範囲内に収まっている。  "
      },
      {
        "line": 371,
        "text": "・boundaries  "
      },
      {
        "line": 372,
        "text": "定義: 場所、分野、関係などを内外に分ける境界。  "
      },
      {
        "line": 373,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 374,
        "text": "違い: boundaries は境界線や区分そのものに焦点がある。confines はその線で囲まれた範囲を含めて指すことがある。  "
      },
      {
        "line": 375,
        "text": "例: The research crosses traditional disciplinary boundaries.  "
      },
      {
        "line": 376,
        "text": "訳: その研究は従来の学問分野の境界を越えている。  "
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
    "input_body_sha256": "262b2e492890cf2d4d7112ac806acf3d9a664cf3a5e3ed7beba313ba13c64ed2",
    "source_inventory_schema_version": "source_inventory_v2",
    "source_inventory_sha256": "72c27e5c9db49d348162a7f2c39d157a44d05eea7f85d91606bcc11a3371b3f1",
    "source_first_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
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
        "id": "S-001",
        "locator": "https://www.oxfordlearnersdictionaries.com/us/definition/english/confine",
        "source_type": "general_dictionary",
        "independence_group": "oxford_languages",
        "facts": [
          {
            "id": "F-001",
            "form": "confine",
            "kind": "lexical_sense",
            "statement": "to keep something inside the limits of an activity, subject, area, or other range",
            "source_detail": "Oxford sense 1 defines the range-limiting use and examples show work, discussion, and geographical distribution."
          },
          {
            "id": "F-002",
            "form": "confine A to B",
            "kind": "argument_structure",
            "statement": "the range-limiting verb uses be confined to, confine oneself to, and confine attention or remarks to a subject",
            "source_detail": "Oxford examples explicitly distinguish passive be confined to and reflexive confine yourself to doing something."
          },
          {
            "id": "F-003",
            "form": "confine",
            "kind": "lexical_sense",
            "statement": "to keep a person or animal in a small or closed space",
            "source_detail": "Oxford sense 2 gives passive confinement in a cage and confinement to barracks."
          },
          {
            "id": "F-004",
            "form": "be confined to bed",
            "kind": "usage_constraint",
            "statement": "be confined to bed expresses inability to leave because of illness, while confined to a wheelchair is often considered offensive and wheelchair user is preferred",
            "source_detail": "Oxford sense 3 supplies the bed example and an explicit disability-language usage note."
          },
          {
            "id": "F-005",
            "form": "confine",
            "kind": "pronunciation",
            "statement": "the verb is pronounced /kənˈfaɪn/ with stress on the second syllable",
            "source_detail": "Oxford's pronunciation entry gives the two-syllable verb pronunciation."
          }
        ]
      },
      {
        "id": "S-002",
        "locator": "https://www.merriam-webster.com/dictionary/confine",
        "source_type": "general_dictionary",
        "independence_group": "merriam_webster",
        "facts": [
          {
            "id": "F-006",
            "form": "confine",
            "kind": "lexical_sense",
            "statement": "the transitive verb can hold something within a location or keep it within limits",
            "source_detail": "Merriam-Webster separates holding within a location, imprisoning, and keeping within limits."
          },
          {
            "id": "F-007",
            "form": "confine",
            "kind": "lexical_sense",
            "statement": "the transitive verb can imprison a person or otherwise deprive the person of free movement",
            "source_detail": "Merriam-Webster lists imprison as a central transitive use."
          },
          {
            "id": "F-008",
            "form": "confines",
            "kind": "lexical_sense",
            "statement": "the noun is normally plural and denotes enclosing boundaries, restraints, or scope",
            "source_detail": "Merriam-Webster's noun entry marks confines plural and illustrates within and outside the confines of a place or authority."
          },
          {
            "id": "F-009",
            "form": "confined",
            "kind": "derived_form",
            "statement": "confined is the regular past tense and past participle of confine",
            "source_detail": "The Merriam-Webster inflection line lists confined."
          },
          {
            "id": "F-010",
            "form": "confining",
            "kind": "derived_form",
            "statement": "confining is the regular present participle of confine",
            "source_detail": "The Merriam-Webster inflection line lists confining."
          },
          {
            "id": "F-011",
            "form": "confine",
            "kind": "pronunciation",
            "statement": "the verb has final stress while the noun also has an initial-stress pronunciation",
            "source_detail": "Merriam-Webster gives verb kən-ˈfīn and noun ˈkän-ˌfīn, with a secondary noun variant."
          }
        ]
      },
      {
        "id": "S-003",
        "locator": "https://www.collinsdictionary.com/us/dictionary/english/confine",
        "source_type": "general_dictionary",
        "independence_group": "harpercollins",
        "facts": [
          {
            "id": "F-012",
            "form": "confine",
            "kind": "lexical_sense",
            "statement": "the verb means to keep within limits or to keep shut in and restrict free movement",
            "source_detail": "Collins lists the limiting and physical-confinement transitive senses with examples."
          },
          {
            "id": "F-013",
            "form": "confines",
            "kind": "lexical_sense",
            "statement": "the noun, often plural, means a limit, boundary, region, or territory",
            "source_detail": "Collins labels the noun often plural and gives boundary and territory meanings."
          },
          {
            "id": "F-014",
            "form": "confine",
            "kind": "pronunciation",
            "statement": "British verb /kənˈfaɪn/ contrasts with British noun /ˈkɒnfaɪn/, and American reference forms show the same stress contrast with /ɑ/ in the noun",
            "source_detail": "Collins provides separate verb and noun pronunciations in British and American sections."
          }
        ]
      },
      {
        "id": "S-004",
        "locator": "https://www.etymonline.com/word/confine",
        "source_type": "etymological_dictionary",
        "independence_group": "etymonline",
        "facts": [
          {
            "id": "F-015",
            "form": "confine",
            "kind": "etymology",
            "statement": "the verb entered from French confiner and ultimately relates to Latin confinis, built from com and finis for a shared boundary",
            "source_detail": "Etymonline traces the obsolete bordering sense and the later restrict-within-bounds sense through French and Medieval Latin."
          },
          {
            "id": "F-016",
            "form": "confinement",
            "kind": "derived_form",
            "statement": "confinement is a noun for the state or act of being confined",
            "source_detail": "Etymonline traces confinement from French confinement and records the restraint sense."
          },
          {
            "id": "F-017",
            "form": "unconfined",
            "kind": "derived_form",
            "statement": "unconfined means not confined or free from restraint or control",
            "source_detail": "Etymonline analyzes unconfined as un- plus the past participle of confine."
          }
        ]
      },
      {
        "id": "S-005",
        "locator": "https://www.merriam-webster.com/dictionary/confined",
        "source_type": "general_dictionary",
        "independence_group": "merriam_webster",
        "facts": [
          {
            "id": "F-018",
            "form": "confined",
            "kind": "derived_form",
            "statement": "the adjective confined can mean kept within bounds or very small, as in confined spaces and compartments",
            "source_detail": "Merriam-Webster has a separate adjective entry covering location, captivity, and very small spaces."
          }
        ]
      },
      {
        "id": "S-006",
        "locator": "https://www.osha.gov/confined-spaces",
        "source_type": "government_primary",
        "independence_group": "us_osha",
        "facts": [
          {
            "id": "F-019",
            "form": "confined space",
            "kind": "specialist_use",
            "statement": "under the cited U.S. OSHA framework a confined space has limited or restricted entry or exit and is not designed for continuous occupancy",
            "source_detail": "OSHA's overview states the occupational-safety criteria and distinguishes confined spaces from permit-required confined spaces."
          }
        ]
      }
    ],
    "source_union": [
      {
        "id": "U-001",
        "source_fact_ids": [
          "F-001",
          "F-006",
          "F-012"
        ],
        "canonical_statement": "Confine can limit a subject, activity, effect, or thing to a stated range.",
        "disposition": "included",
        "rationale": "This is the first major verb sense and is independently supported."
      },
      {
        "id": "U-002",
        "source_fact_ids": [
          "F-002"
        ],
        "canonical_statement": "The main limiting frames are confine A to B, be confined to B, and confine oneself to a noun or gerund.",
        "disposition": "included",
        "rationale": "The frames are high-value and difficult for learners to infer safely."
      },
      {
        "id": "U-003",
        "source_fact_ids": [
          "F-003",
          "F-007"
        ],
        "canonical_statement": "Confine can keep a person or animal from leaving a bounded place.",
        "disposition": "included",
        "rationale": "This physical detention sense differs from abstract scope restriction."
      },
      {
        "id": "U-004",
        "source_fact_ids": [
          "F-004"
        ],
        "canonical_statement": "Be confined to bed describes illness-related restriction, while confined to a wheelchair carries an often-offensive framing.",
        "disposition": "included",
        "rationale": "The construction and disability-language warning have direct learner value."
      },
      {
        "id": "U-005",
        "source_fact_ids": [
          "F-008",
          "F-013"
        ],
        "canonical_statement": "The usually plural noun confines denotes boundaries, restraints, scope, or the territory within boundaries.",
        "disposition": "included",
        "rationale": "The noun is lower-frequency but recurrent in fixed prepositional phrases."
      },
      {
        "id": "U-006",
        "source_fact_ids": [
          "F-005",
          "F-011",
          "F-014"
        ],
        "canonical_statement": "The verb has second-syllable stress; the noun commonly has first-syllable stress and a British-American vowel difference.",
        "disposition": "included",
        "rationale": "The heteronymic stress contrast is essential pronunciation information."
      },
      {
        "id": "U-007",
        "source_fact_ids": [
          "F-015"
        ],
        "canonical_statement": "Confine comes through French from a Latin boundary expression related to con- and finis.",
        "disposition": "included",
        "rationale": "The historical boundary sense directly explains the modern semantic connection."
      },
      {
        "id": "U-008",
        "source_fact_ids": [
          "F-009",
          "F-018"
        ],
        "canonical_statement": "Confined is both the regular past participle and a lexicalized adjective for bounded, captive, or very small conditions.",
        "disposition": "included",
        "rationale": "The adjective confined space is frequent and not adequately covered by an inflection note alone."
      },
      {
        "id": "U-009",
        "source_fact_ids": [
          "F-010"
        ],
        "canonical_statement": "Confining is the regular present participle of confine.",
        "disposition": "included",
        "rationale": "The inflection and spelling change are recorded in word formation and pronunciation."
      },
      {
        "id": "U-010",
        "source_fact_ids": [
          "F-016"
        ],
        "canonical_statement": "Confinement is the noun for the act or state of confining.",
        "disposition": "included",
        "rationale": "This is the principal noun derivative."
      },
      {
        "id": "U-011",
        "source_fact_ids": [
          "F-017"
        ],
        "canonical_statement": "Unconfined means not confined or free from restraint.",
        "disposition": "included",
        "rationale": "This is the transparent negative derivative included in word formation."
      },
      {
        "id": "U-012",
        "source_fact_ids": [
          "F-019"
        ],
        "canonical_statement": "Confined space has a defined occupational-safety use whose criteria go beyond merely being a small room.",
        "disposition": "included",
        "rationale": "The article warns learners not to infer the specialist classification from ordinary size alone."
      }
    ],
    "claim_units": [
      {
        "id": "C-001",
        "union_ids": [
          "U-001"
        ],
        "subject_form": "confine",
        "claim_type": "lexical_sense",
        "statement": "Confine means to limit a subject, activity, phenomenon, or thing to a stated scope.",
        "article_target_ids": [
          "definition:001",
          "collocation:001",
          "collocation:005"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-001",
            "support_summary": "Oxford defines the activity, subject, and area limiting use."
          },
          {
            "source_fact_id": "F-006",
            "support_summary": "Merriam-Webster distinguishes location and limit uses."
          },
          {
            "source_fact_id": "F-012",
            "support_summary": "Collins records keeping within limits and physical bounds."
          }
        ]
      },
      {
        "id": "C-002",
        "union_ids": [
          "U-002"
        ],
        "subject_form": "confine A to B",
        "claim_type": "frame",
        "statement": "Confine A to B, be confined to B, and confine oneself to a noun or gerund are central frames.",
        "article_target_ids": [
          "grammar_pattern:001",
          "collocation:002",
          "collocation:003",
          "collocation:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-002",
            "support_summary": "Oxford supplies passive, reflexive, and object-plus-to examples."
          }
        ]
      },
      {
        "id": "C-003",
        "union_ids": [
          "U-003"
        ],
        "subject_form": "confine",
        "claim_type": "lexical_sense",
        "statement": "Confine can keep a person or animal from leaving an enclosed place.",
        "article_target_ids": [
          "definition:002",
          "grammar_pattern:002",
          "collocation:006",
          "collocation:007"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-003",
            "support_summary": "Oxford defines keeping people or animals in a closed space."
          },
          {
            "source_fact_id": "F-007",
            "support_summary": "Merriam-Webster directly lists the imprisoning use."
          }
        ]
      },
      {
        "id": "C-004",
        "union_ids": [
          "U-004"
        ],
        "subject_form": "be confined to bed",
        "claim_type": "usage_constraint",
        "statement": "Be confined to bed is an illness construction; wheelchair wording can be offensive and should be replaced when only the mobility aid is meant.",
        "article_target_ids": [
          "definition:003",
          "collocation:010",
          "usage_note:003"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-004",
            "support_summary": "Oxford gives both the bed construction and the explicit wheelchair-language warning."
          }
        ]
      },
      {
        "id": "C-005",
        "union_ids": [
          "U-005"
        ],
        "subject_form": "confines",
        "claim_type": "lexical_sense",
        "statement": "The usually plural noun confines denotes boundaries, scope, or the area within boundaries.",
        "article_target_ids": [
          "definition:005",
          "grammar_pattern:005",
          "collocation:018",
          "collocation:019"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-008",
            "support_summary": "Merriam-Webster marks the noun plural and gives boundary and scope meanings."
          },
          {
            "source_fact_id": "F-013",
            "support_summary": "Collins marks the noun often plural and gives boundary and territory meanings."
          }
        ]
      },
      {
        "id": "C-006",
        "union_ids": [
          "U-006"
        ],
        "subject_form": "confine",
        "claim_type": "pronunciation",
        "statement": "The verb and noun differ in stress, and the initial-stress noun has a British-American first-vowel contrast.",
        "article_target_ids": [
          "pronunciation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-005",
            "support_summary": "Oxford gives final stress for the two-syllable verb."
          },
          {
            "source_fact_id": "F-011",
            "support_summary": "Merriam-Webster distinguishes common verb and noun stress patterns."
          },
          {
            "source_fact_id": "F-014",
            "support_summary": "Collins supplies British and American verb-noun pronunciations."
          }
        ]
      },
      {
        "id": "C-007",
        "union_ids": [
          "U-007"
        ],
        "subject_form": "confine",
        "claim_type": "etymology",
        "statement": "Confine entered through French and derives from a Latin expression for sharing a boundary.",
        "article_target_ids": [
          "etymology:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-015",
            "support_summary": "Etymonline traces French confiner to Medieval Latin and Latin boundary forms."
          }
        ]
      },
      {
        "id": "C-008",
        "union_ids": [
          "U-008"
        ],
        "subject_form": "confined",
        "claim_type": "derived_form",
        "statement": "Confined is a past participle and an adjective for bounded or very small spaces.",
        "article_target_ids": [
          "word_formation:002",
          "definition:004",
          "collocation:014"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-009",
            "support_summary": "Merriam-Webster lists confined as the regular past form."
          },
          {
            "source_fact_id": "F-018",
            "support_summary": "Merriam-Webster's adjective entry covers limited and very small spaces."
          }
        ]
      },
      {
        "id": "C-009",
        "union_ids": [
          "U-009"
        ],
        "subject_form": "confining",
        "claim_type": "derived_form",
        "statement": "Confining is the regular present participle of confine.",
        "article_target_ids": [
          "word_formation:003",
          "pronunciation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-010",
            "support_summary": "Merriam-Webster explicitly lists confining among the inflected forms."
          }
        ]
      },
      {
        "id": "C-010",
        "union_ids": [
          "U-010"
        ],
        "subject_form": "confinement",
        "claim_type": "derived_form",
        "statement": "Confinement names the act or state of being confined.",
        "article_target_ids": [
          "word_formation:001"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-016",
            "support_summary": "Etymonline records confinement as restraint or the state of being confined."
          }
        ]
      },
      {
        "id": "C-011",
        "union_ids": [
          "U-011"
        ],
        "subject_form": "unconfined",
        "claim_type": "derived_form",
        "statement": "Unconfined means free from confinement or restraint.",
        "article_target_ids": [
          "word_formation:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-017",
            "support_summary": "Etymonline defines unconfined as not confined or free from restraint."
          }
        ]
      },
      {
        "id": "C-012",
        "union_ids": [
          "U-012"
        ],
        "subject_form": "confined space",
        "claim_type": "specialist_use",
        "statement": "Occupational-safety definitions of confined space use specific criteria beyond ordinary smallness.",
        "article_target_ids": [
          "definition:004",
          "collocation:014",
          "usage_note:004"
        ],
        "source_supports": [
          {
            "source_fact_id": "F-019",
            "support_summary": "OSHA requires restricted entry or exit and no design for continuous occupancy under its framework."
          }
        ]
      }
    ]
  },
  "specification_sha256": "dc0826565109b0be96c5ef7c13943a01b0e42616fecff87ab25102e5cda4cb8d",
  "source_artifact_sha256": "bec7926f6a41b3d90a8f5c26196283257655aba3db53208c4879d4cdbe4de3ca",
  "normalized_input_sha256": "224d64d847afb0f11502cb6df73b967d11db50087ce99f2c1c4b3a85fcc65f99"
}
```
