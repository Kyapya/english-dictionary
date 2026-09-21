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
  "input_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f",
  "input_sections": {
    "definitions": [
      {
        "line": 37,
        "text": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない"
      },
      {
        "line": 39,
        "text": "【日本語訳・定義】計画、日程、合意、結論、説明、提案、識別などが、現時点では候補として置かれているものの、検討・交渉・確認が終わっておらず、後で変更または撤回される可能性があることを表す。単に「一時的」という期間の短さではなく、内容の確定性がまだ低いことに焦点がある。  "
      },
      {
        "line": 144,
        "text": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な"
      },
      {
        "line": 146,
        "text": "【日本語訳・定義】人の行動、声、表情、返答、提案などが、確信や自信を十分に示さず、様子をうかがいながら慎重に行われることを表す。単に静か・弱いという意味ではなく、失敗や拒否を恐れている、またはまだ慣れていないような不確かさが表れやすい。  "
      },
      {
        "line": 251,
        "text": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目"
      },
      {
        "line": 253,
        "text": "【日本語訳・定義】予約、契約、日程、出演枠などについて、正式な確定や契約が済む前に、仮のものとして記録・扱われる項目を表す。一般会話で広く使う名詞ではなく、複数形 tentatives を含む業務上・事務上の文脈で見られる低頻度用法である。  "
      }
    ],
    "collocations_examples": [
      {
        "line": 37,
        "text": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない"
      },
      {
        "line": 47,
        "text": "【コロケーション】"
      },
      {
        "line": 49,
        "text": "・tentative plans for 〈event/activity〉  "
      },
      {
        "line": 50,
        "text": "用途: 予定はあるが、内容や日時がまだ変わる可能性があることを表す。  "
      },
      {
        "line": 51,
        "text": "例: We have tentative plans for a short trip in October.  "
      },
      {
        "line": 52,
        "text": "訳: 私たちは10月に短い旅行をする仮の予定がある。  "
      },
      {
        "line": 54,
        "text": "・a tentative date for 〈event〉  "
      },
      {
        "line": 55,
        "text": "用途: 会議・発売・開始などの日付を候補として置く。  "
      },
      {
        "line": 56,
        "text": "例: The organizers set a tentative date for the conference in early May.  "
      },
      {
        "line": 57,
        "text": "訳: 主催者は会議の開催日を5月初旬の仮の日付として設定した。  "
      },
      {
        "line": 59,
        "text": "・a tentative schedule  "
      },
      {
        "line": 60,
        "text": "用途: 今後の調整で変更され得る予定表を指す。  "
      },
      {
        "line": 61,
        "text": "例: The airline released a tentative schedule for the new route.  "
      },
      {
        "line": 62,
        "text": "訳: その航空会社は新路線の暫定的な運航予定を公表した。  "
      },
      {
        "line": 64,
        "text": "・a tentative agreement/deal  "
      },
      {
        "line": 65,
        "text": "用途: 当事者が大筋で合意したが、最終承認や正式契約がまだ済んでいない状態を表す。  "
      },
      {
        "line": 66,
        "text": "例: The two sides reached a tentative agreement after three days of talks.  "
      },
      {
        "line": 67,
        "text": "訳: 両者は3日間の協議の後、暫定合意に達した。  "
      },
      {
        "line": 69,
        "text": "・tentative conclusions/findings  "
      },
      {
        "line": 70,
        "text": "用途: 調査や分析の途中で得られ、追加の確認で修正され得る結論・結果を表す。  "
      },
      {
        "line": 71,
        "text": "例: The researchers presented their tentative findings at the workshop.  "
      },
      {
        "line": 72,
        "text": "訳: 研究者たちはワークショップで予備的な研究結果を発表した。  "
      },
      {
        "line": 74,
        "text": "・a tentative explanation for 〈phenomenon/problem〉  "
      },
      {
        "line": 75,
        "text": "用途: 現象や問題を説明する仮説を、確定的な説明としてではなく提示する。  "
      },
      {
        "line": 76,
        "text": "例: The team offered a tentative explanation for the sudden drop in demand.  "
      },
      {
        "line": 77,
        "text": "訳: チームは需要が急減したことについて暫定的な説明を示した。  "
      },
      {
        "line": 79,
        "text": "・a tentative identification of 〈person/object〉  "
      },
      {
        "line": 80,
        "text": "用途: 証拠が十分でなく、現段階での仮の同定であることを示す。  "
      },
      {
        "line": 81,
        "text": "例: The police made a tentative identification of the vehicle from the video.  "
      },
      {
        "line": 82,
        "text": "訳: 警察は映像からその車両を暫定的に特定した。  "
      },
      {
        "line": 84,
        "text": "・tentatively approve/accept/identify something  "
      },
      {
        "line": 85,
        "text": "用途: 承認・受諾・特定を行うが、最終確認や条件の充足を残していることを表す。  "
      },
      {
        "line": 86,
        "text": "例: The board tentatively approved the budget pending a legal review.  "
      },
      {
        "line": 87,
        "text": "訳: 取締役会は法務審査を条件として、その予算を暫定承認した。  "
      },
      {
        "line": 144,
        "text": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な"
      },
      {
        "line": 154,
        "text": "【コロケーション】"
      },
      {
        "line": 156,
        "text": "・a tentative smile  "
      },
      {
        "line": 157,
        "text": "用途: 相手の反応をうかがうような、確信のない笑顔を表す。  "
      },
      {
        "line": 158,
        "text": "例: She gave him a tentative smile before entering the unfamiliar room.  "
      },
      {
        "line": 159,
        "text": "訳: 彼女は見慣れない部屋に入る前、彼にためらいがちな笑顔を向けた。  "
      },
      {
        "line": 161,
        "text": "・a tentative answer/reply  "
      },
      {
        "line": 162,
        "text": "用途: 答えを断定せず、自信がないまま返すことを表す。  "
      },
      {
        "line": 163,
        "text": "例: He gave a tentative answer because he had not checked the figures.  "
      },
      {
        "line": 164,
        "text": "訳: 彼は数字を確認していなかったので、自信のない返答をした。  "
      },
      {
        "line": 166,
        "text": "・a tentative voice/tone  "
      },
      {
        "line": 167,
        "text": "用途: 声や口調にためらい・不確かさが表れていることを表す。  "
      },
      {
        "line": 168,
        "text": "例: “Perhaps we should wait,” she said in a tentative voice.  "
      },
      {
        "line": 169,
        "text": "訳: 「待ったほうがよいかもしれません」と、彼女はためらいがちな声で言った。  "
      },
      {
        "line": 171,
        "text": "・a tentative knock on 〈door〉  "
      },
      {
        "line": 172,
        "text": "用途: 在室や反応を確かめるように、強く決め込まずノックすることを表す。  "
      },
      {
        "line": 173,
        "text": "例: There was a tentative knock on the office door.  "
      },
      {
        "line": 174,
        "text": "訳: オフィスのドアをおそるおそるノックする音がした。  "
      },
      {
        "line": 176,
        "text": "・take tentative steps towards 〈goal/change〉  "
      },
      {
        "line": 177,
        "text": "用途: 目標や変化に向けて、確信はないが最初の行動を始めることを表す。  "
      },
      {
        "line": 178,
        "text": "例: The company is taking tentative steps toward reducing its use of plastic.  "
      },
      {
        "line": 179,
        "text": "訳: その会社はプラスチックの使用を減らすための最初の一歩を慎重に踏み出している。  "
      },
      {
        "line": 181,
        "text": "・make a tentative attempt to do something  "
      },
      {
        "line": 182,
        "text": "用途: 成功の確信はないが、試しに行動を起こすことを表す。  "
      },
      {
        "line": 183,
        "text": "例: The child made a tentative attempt to join the other players.  "
      },
      {
        "line": 184,
        "text": "訳: その子どもは、ほかの遊び仲間に加わろうとおそるおそる試みた。  "
      },
      {
        "line": 186,
        "text": "・be tentative about 〈doing something〉  "
      },
      {
        "line": 187,
        "text": "用途: 何かをすることに自信がなく、決めかねている状態を表す。  "
      },
      {
        "line": 188,
        "text": "例: She was tentative about speaking up in front of the whole team.  "
      },
      {
        "line": 189,
        "text": "訳: 彼女はチーム全員の前で発言することをためらっていた。  "
      },
      {
        "line": 191,
        "text": "・tentatively suggest/ask something  "
      },
      {
        "line": 192,
        "text": "用途: 相手の反応を見ながら、強く主張せずに提案・質問することを表す。  "
      },
      {
        "line": 193,
        "text": "例: He tentatively suggested moving the meeting to Friday.  "
      },
      {
        "line": 194,
        "text": "訳: 彼は会議を金曜日に移してはどうかと、ためらいがちに提案した。  "
      },
      {
        "line": 251,
        "text": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目"
      },
      {
        "line": 261,
        "text": "【コロケーション】"
      },
      {
        "line": 263,
        "text": "・list the dates as tentatives  "
      },
      {
        "line": 264,
        "text": "用途: 契約や正式確認が済んでいない日程を仮の枠として記録する。  "
      },
      {
        "line": 265,
        "text": "例: The theater listed the autumn dates as tentatives while it waited for the contracts.  "
      },
      {
        "line": 266,
        "text": "訳: その劇場は契約を待つ間、秋の日程を暫定枠として記録した。  "
      },
      {
        "line": 268,
        "text": "・hold a date as a tentative  "
      },
      {
        "line": 269,
        "text": "用途: 日程を正式決定前の仮押さえとして扱う。  "
      },
      {
        "line": 270,
        "text": "例: The producer asked us to hold the date as a tentative until Friday.  "
      },
      {
        "line": 271,
        "text": "訳: プロデューサーは、金曜日まではその日を仮押さえとしておくよう私たちに頼んだ。  "
      }
    ],
    "lexical_relations": [
      {
        "line": 37,
        "text": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない"
      },
      {
        "line": 91,
        "text": "【類義語】"
      },
      {
        "line": 93,
        "text": "・provisional  "
      },
      {
        "line": 94,
        "text": "定義: 正式なものが決まるまで、暫定的に使われる。  "
      },
      {
        "line": 95,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 96,
        "text": "違い: provisional は正式な決定・制度・地位の代替として置かれることを強調し、tentative は内容がまだ固まっておらず変更され得ることを広く示す。  "
      },
      {
        "line": 97,
        "text": "例: The committee issued a provisional approval while the documents were being checked.  "
      },
      {
        "line": 98,
        "text": "訳: 委員会は書類を確認している間、暫定承認を出した。  "
      },
      {
        "line": 100,
        "text": "・preliminary  "
      },
      {
        "line": 101,
        "text": "定義: 本格的な検討や最終段階の前に行われる、初期段階の。  "
      },
      {
        "line": 102,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 103,
        "text": "違い: preliminary は時期・段階が早いことに焦点があり、tentative はその結論や計画がまだ確定していないことに焦点がある。  "
      },
      {
        "line": 104,
        "text": "例: The report contains preliminary results from the first experiment.  "
      },
      {
        "line": 105,
        "text": "訳: その報告書には最初の実験の予備結果が含まれている。  "
      },
      {
        "line": 107,
        "text": "・conditional  "
      },
      {
        "line": 108,
        "text": "定義: 特定の条件が満たされる場合にだけ成立する。  "
      },
      {
        "line": 109,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 110,
        "text": "違い: conditional は変更の理由となる条件を明示する語で、tentative は条件を示さなくても、現段階で確定していないことを表せる。  "
      },
      {
        "line": 111,
        "text": "例: The offer is conditional on approval from the lender.  "
      },
      {
        "line": 112,
        "text": "訳: その申し出は貸し手の承認を条件としている。  "
      },
      {
        "line": 114,
        "text": "・unconfirmed  "
      },
      {
        "line": 115,
        "text": "定義: 正式な確認や裏付けがまだ得られていない。  "
      },
      {
        "line": 116,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 117,
        "text": "違い: unconfirmed は情報の確認状態に焦点があり、tentative は情報だけでなく計画・合意・結論を仮置きする場合にも使う。  "
      },
      {
        "line": 118,
        "text": "例: The report was based on an unconfirmed account of the incident.  "
      },
      {
        "line": 119,
        "text": "訳: その報告書は、その出来事についてまだ確認されていない説明に基づいていた。  "
      },
      {
        "line": 121,
        "text": "【反意語】"
      },
      {
        "line": 123,
        "text": "・definite  "
      },
      {
        "line": 124,
        "text": "定義: 内容や予定が明確に決まっていて、曖昧さが少ない。  "
      },
      {
        "line": 125,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 126,
        "text": "違い: definite は tentative の「未確定」に対する直接的な反対側を示す。  "
      },
      {
        "line": 127,
        "text": "例: We need a definite answer before we book the venue.  "
      },
      {
        "line": 128,
        "text": "訳: 会場を予約する前に、確定した返事が必要だ。  "
      },
      {
        "line": 130,
        "text": "・confirmed  "
      },
      {
        "line": 131,
        "text": "定義: 確認や承認によって、正しいもの・正式なものとして確定している。  "
      },
      {
        "line": 132,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 133,
        "text": "違い: confirmed は確認手続きが済んだことに焦点があり、tentative はその手続きの前段階を示す。  "
      },
      {
        "line": 134,
        "text": "例: The confirmed departure time is shown on your ticket.  "
      },
      {
        "line": 135,
        "text": "訳: 確定した出発時刻はチケットに表示されている。  "
      },
      {
        "line": 137,
        "text": "・final  "
      },
      {
        "line": 138,
        "text": "定義: それ以上の変更・検討を予定しない最終的な。  "
      },
      {
        "line": 139,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 140,
        "text": "違い: final は変更を終えた段階、tentative は変更の余地を残した段階を表す。  "
      },
      {
        "line": 141,
        "text": "例: The final schedule will be sent to all participants tomorrow.  "
      },
      {
        "line": 142,
        "text": "訳: 最終日程は明日、参加者全員に送られる。  "
      },
      {
        "line": 144,
        "text": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な"
      },
      {
        "line": 198,
        "text": "【類義語】"
      },
      {
        "line": 200,
        "text": "・hesitant  "
      },
      {
        "line": 201,
        "text": "定義: 決めたり行動したりすることをためらっている。  "
      },
      {
        "line": 202,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 203,
        "text": "違い: hesitant は意思決定や行動を進められないためらいを直接示し、tentative は声・表情・動作が自信なさそうに現れる様子まで表せる。  "
      },
      {
        "line": 204,
        "text": "例: She was hesitant to raise the issue during the meeting.  "
      },
      {
        "line": 205,
        "text": "訳: 彼女は会議中にその問題を持ち出すのをためらった。  "
      },
      {
        "line": 207,
        "text": "・uncertain  "
      },
      {
        "line": 208,
        "text": "定義: 自分の判断・答え・行動に確信がない。  "
      },
      {
        "line": 209,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 210,
        "text": "違い: uncertain は認識や判断の不確かさを広く表し、tentative はその不確かさが行動・発言・表情に現れていることを描きやすい。  "
      },
      {
        "line": 211,
        "text": "例: He sounded uncertain when asked about the cause.  "
      },
      {
        "line": 212,
        "text": "訳: 原因を尋ねられたとき、彼は自信がなさそうに聞こえた。  "
      },
      {
        "line": 214,
        "text": "・cautious  "
      },
      {
        "line": 215,
        "text": "定義: 危険・損失・誤りを避けるために用心深い。  "
      },
      {
        "line": 216,
        "text": "頻度: 〈9/10〉  "
      },
      {
        "line": 217,
        "text": "違い: cautious はリスク管理の意識を含むが、tentative は必ずしも危険を評価しているとは限らず、自信のなさや慣れていない感じを示す。  "
      },
      {
        "line": 218,
        "text": "例: The manager took a cautious approach to the unfamiliar market.  "
      },
      {
        "line": 219,
        "text": "訳: その管理者は未知の市場に慎重な姿勢で臨んだ。  "
      },
      {
        "line": 221,
        "text": "・faltering  "
      },
      {
        "line": 222,
        "text": "定義: 力強さや流暢さを欠き、途中で弱まったりつまずいたりする。  "
      },
      {
        "line": 223,
        "text": "頻度: 〈6/10〉  "
      },
      {
        "line": 224,
        "text": "違い: faltering は声・歩み・進行が不安定で途切れがちな結果に焦点があり、tentative は最初から確信を持てず慎重に行う態度に焦点がある。  "
      },
      {
        "line": 225,
        "text": "例: His faltering voice revealed how nervous he was.  "
      },
      {
        "line": 226,
        "text": "訳: 彼の途切れがちな声から、彼がどれほど緊張していたかが分かった。  "
      },
      {
        "line": 228,
        "text": "【反意語】"
      },
      {
        "line": 230,
        "text": "・confident  "
      },
      {
        "line": 231,
        "text": "定義: 自分の能力・判断・発言に確信を持っている。  "
      },
      {
        "line": 232,
        "text": "頻度: 〈10/10〉  "
      },
      {
        "line": 233,
        "text": "違い: confident は tentative の「自信のない態度」に対する直接的な反対を表す。  "
      },
      {
        "line": 234,
        "text": "例: She gave a confident answer to the difficult question.  "
      },
      {
        "line": 235,
        "text": "訳: 彼女はその難しい質問に自信を持って答えた。  "
      },
      {
        "line": 237,
        "text": "・assured  "
      },
      {
        "line": 238,
        "text": "定義: 落ち着きと自信があり、確実そうに見える。  "
      },
      {
        "line": 239,
        "text": "頻度: 〈7/10〉  "
      },
      {
        "line": 240,
        "text": "違い: assured は態度・話し方・演技などに表れる落ち着いた自信を強調し、confident より改まった響きがある。  "
      },
      {
        "line": 241,
        "text": "例: The speaker adopted an assured tone from the beginning.  "
      },
      {
        "line": 242,
        "text": "訳: その話し手は最初から自信に満ちた口調を取った。  "
      },
      {
        "line": 244,
        "text": "・decisive  "
      },
      {
        "line": 245,
        "text": "定義: 迷わず判断し、行動をはっきり決める。  "
      },
      {
        "line": 246,
        "text": "頻度: 〈8/10〉  "
      },
      {
        "line": 247,
        "text": "違い: decisive は決断や行動の速さ・明確さに焦点があり、tentative は決めかねながら慎重に進めることを表す。  "
      },
      {
        "line": 248,
        "text": "例: The director took decisive action when the system failed.  "
      },
      {
        "line": 249,
        "text": "訳: システムが停止したとき、部長は断固たる行動を取った。  "
      },
      {
        "line": 251,
        "text": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目"
      },
      {
        "line": 275,
        "text": "【類義語】"
      },
      {
        "line": 277,
        "text": "・provisional item  "
      },
      {
        "line": 278,
        "text": "定義: 正式決定まで仮のものとして記録・管理される項目。  "
      },
      {
        "line": 279,
        "text": "頻度: 〈3/10〉  "
      },
      {
        "line": 280,
        "text": "違い: provisional item は意味を明示する説明的な句で、名詞 tentative の業務上の用法を平易に言い換える。tentative より自然に伝わりやすいが、特定業界の固定用語とは限らない。  "
      },
      {
        "line": 281,
        "text": "例: The spreadsheet marks each provisional item in gray until the contract is signed.  "
      },
      {
        "line": 282,
        "text": "訳: その表計算シートでは、契約が締結されるまで各暫定項目を灰色で示している。  "
      },
      {
        "line": 284,
        "text": "・pending booking  "
      },
      {
        "line": 285,
        "text": "定義: 確定や支払いなどを待っている仮予約。  "
      },
      {
        "line": 286,
        "text": "頻度: 〈4/10〉  "
      },
      {
        "line": 287,
        "text": "違い: pending booking は予約に意味を限定し、保留中であることを直接示す。tentative は予約以外の日程・契約項目にも使える。  "
      },
      {
        "line": 288,
        "text": "例: We kept the pending booking separate from the confirmed reservations.  "
      },
      {
        "line": 289,
        "text": "訳: 私たちは保留中の仮予約を、確定済みの予約とは別にしておいた。  "
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
  "specification_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
  "source_artifact_sha256": "73787b3811419d4af99b6764bcacbf9685ac18522d5e2b856009599ce8e20810",
  "normalized_input_sha256": "511f539e04aa2239073b6874dfc8c8e086dc0fb000259d89b0b66fffcc3273ef"
}
```
