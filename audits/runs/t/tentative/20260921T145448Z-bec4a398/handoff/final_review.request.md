# Independent review handoff

Stage: `final_review`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session. For runs using self_attested_handoff_v1, the raw response must include a top-level reviewer object with mode=handoff, the actual agent_id, and the actual declared_model. The ingester will reject identity supplied only after the response was created.

## Prompt

# final_review_spec_v3

最新版本文と固定済みレビューを照合し、最終合否を判断する。正常項目の合格理由を大量に作る時間を、本文・資料・修正箇所の実読へ戻す。品質基準、全件の判定、独立性、未解決事項を残さない条件は維持する。

## 照合

- `inventories` / `response_template` を対象IDの正本とする。欠落を空集合と推測しない。未判定は合格ではない。
- 事実、語法、発音、例文、訳が正しく、主要な品詞、語義、派生・転換、専門用法、完全な統語フレームが過不足なく扱われていることを確認する。語義境界、コアイメージ、定義、語法、コロケーション、語彙関係に矛盾がないこと。例文と訳の意味役割、作用方向、肯否、数量、時制・法、条件、修飾範囲、レジスターを確認する。
- 証拠の内容確認は evidence checker が本文・claim・外部資料を照合した結果を使う。合格理由の長さや findings が0件であることは正確さの根拠にしない。高リスク主張の反例・矛盾・適用範囲が未確認、資料にアクセスできない、主張と根拠が食い違う場合は `insufficient_evidence` として解決するまで合格にしない。
- すべてのfindingについて、採用修正が最新版へ反映され、不採用理由が資料と仕様に支えられ、修正の影響が再検査されているかを確認する。修正前の説明だけで解決扱いにしない。
- 固定済みblind candidateの各 `semantic_assertion` を最新版へ適用し、候補の境界・作用方向・包含/除外関係・一般化範囲に反する記述がないことを確認する。
- final reviewは全面レビューを繰り返す工程ではない。具体的な矛盾・未解決事項・修正確認に注力する。疑義のある外部資料は該当箇所を再確認する。hash、ID集合、時系列、seal、再検査・再利用条件は `scripts/run_word.py`、`scripts/workflow_revision.py`、`scripts/generate_audit_manifest.py` の検証を使い、説明文を作り直さない。

## 出力

`final_review_v3` JSONを返す。対象ID・判定・必要な束縛情報を記録する。

`response_template` の結果欄と `_output_metadata` を使う。同じ結果を `adjudication` 配下へ再掲したり、固定済み `independent_candidates` を応答へ複製したりしない。

- `target_results`、`relation_results`、`normal_candidate_results`、`blind_candidate_results`、`evidence_checks`、`source_inventory_results` は全IDを重複なく含み、各 `status` を `pass` または `fail` とする。
- 正常な `pass` の `notes` は省略する。本文の全文引用、対象ごとの「問題なし」の言い換え、合格理由の水増しは不要。判定を初期値のpassで一括補完してはならない。
- `fail` は `notes` に問題と必要な修正を短く記す。引用は問題の特定に必要な範囲だけにする。
- `finding_results` は各findingを一度だけ含め、`pass` でも最新版のどの修正または不採用根拠を確認したかを `notes` に短く残す。元のfinding・resolutionを全文再掲しない。
- `blind_candidate_results` は全 `assertion_ids` と `verified_body_sha256` を保持する。candidateのpassは列挙した全assertionの確認を意味する。一つでも未確認または不成立ならfailとする。assertionごとの合格理由表を別に作らない。
- `source_inventory_results` の `union_id` は `id` と一致させる。
- `checker_recheck_results` / `chronology_results` の説明表は作らない。機械検証の原記録を参照する。
- `decision` は `pass | reject`、`blockers` と全体の非blocking `notes` は配列とする。本文は変更しない。

## 合否

全対象がpass、未解決・hold・`insufficient_evidence`・未検査範囲・無効pass・判断衝突・未確認の修正影響が0件、blockerが0件の場合だけPASSとする。条件付き合格は使わない。

誤り、主要語義・構文の欠落や過剰収録、根拠との矛盾、必須内容の違反、未判定・未解決事項があればREJECTとする。blockerには対象ID、問題、必要な修正を記録し、修正・影響範囲の再検査・final blind再実行へ戻す。`REJECT` は審査失敗ではなく、問題を検出した正常な成果である。分類粒度や任意の表現改善だけを理由にrejectせず、非blocking noteとする。

v1/v2は旧runの検証・再現専用。保存済みraw出力は書き換えず、そのschemaの条件で検証する。


## Input packet

```json
{
  "stage": "final_review",
  "entry_body": "\n＃発音記号\n\n米・英: /ˈtentətɪv/。3音節で、第1音節の /ˈten/ に主強勢がある。第2音節は弱い /tə/、語末は /tɪv/ と発音する。tentatively は /ˈtentətɪvli/、tentativeness は /ˈtentətɪvnəs/ のように、派生語でも第1音節の強勢を保つ。  \n\n＃語源\n\n16世紀後半に使われ始めた語で、中世ラテン語 tentativus「試みる性質の、試験的な、暫定的な」から来た。これはラテン語 tentare／temptare「触れて確かめる、試す、試みる」に由来する。「まず試してみる段階」という意味から、まだ十分に固まっていない「暫定的な」と、試みる人の「自信のない、ためらいがちな」へ意味が広がった。attempt、tempt、tentatively、tentativeness は同じラテン語の語族に関係するが、tentative の単純な活用形ではない。  \n\n＃語形成\n\n・tentatively：副詞。「暫定的に、仮に」または「ためらいがちに、自信なさそうに」。修飾する内容によって2つの形容詞義に対応する。  \n・tentativeness：名詞。「暫定性、未確定性」または「ためらい、自信のなさ」。通常は不可算名詞で、性質や態度を表す。  \n・tentative：名詞転用。「暫定的なもの、仮の項目」。まれで、予約・契約・日程などが確定する前の業務上の項目を指すことがある。  \n・attempt／tempt：同じラテン語 tentare／temptare にさかのぼる関連語。attempt は「試み」、tempt は現代英語で主に「誘惑する」を表し、tentative の派生語ではない。  \n\n＃コアイメージ\n\ntentative の共通核は、「まだ確定させず、試しに触れている段階」である。計画や判断なら後で変更され得る「暫定性」、行動や表情なら確信を持たず慎重に踏み出す「ためらい」として現れる。  \n・内容を試しに置き、後で変えられる状態 → 「暫定的な、仮の」（語義1）  \n・行動を試しに行い、確信を持てない様子 → 「ためらいがちな、自信のない」（語義2）  \n・確定前の項目を業務上の仮登録として扱う → 「暫定案、仮の項目」（語義3）  \n\n＃意味・用法・関連表現\n\n1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない\n\n【日本語訳・定義】計画、日程、合意、結論、説明、提案、識別などが、現時点では候補として置かれているものの、検討・交渉・確認が終わっておらず、後で変更または撤回される可能性があることを表す。単に「一時的」という期間の短さではなく、内容の確定性がまだ低いことに焦点がある。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準語で、会話・報道・ビジネス・学術・交渉まで広く使う。特に plan、date、schedule、arrangement、agreement、conclusion、explanation、identification など、後から確認や調整が入り得る名詞と結びつく。  \n\n【文法パターン】a tentative 〈plan/date/schedule/arrangement/agreement〉＝暫定的な〈計画・日付・予定・取り決め・合意〉／tentative conclusions/findings＝予備的な結論・調査結果／a tentative explanation/identification＝暫定的な説明・仮の同定／make/reach/announce a tentative decision＝暫定的な決定をする・出す／be tentative about 〈the date/details〉＝〈日付・詳細〉がまだ確定していない／tentative plans to do＝～する暫定的な計画／tentatively agree/approve/identify＝暫定的に合意する・承認する・特定する。  \n\n【コロケーション】\n\n・tentative plans for 〈event/activity〉  \n用途: 予定はあるが、内容や日時がまだ変わる可能性があることを表す。  \n例: We have tentative plans for a short trip in October.  \n訳: 私たちは10月に短い旅行をする仮の予定がある。  \n\n・a tentative date for 〈event〉  \n用途: 会議・発売・開始などの日付を候補として置く。  \n例: The organizers set a tentative date for the conference in early May.  \n訳: 主催者は会議の開催日を5月初旬の仮の日付として設定した。  \n\n・a tentative schedule  \n用途: 今後の調整で変更され得る予定表を指す。  \n例: The airline released a tentative schedule for the new route.  \n訳: その航空会社は新路線の暫定的な運航予定を公表した。  \n\n・a tentative agreement/deal  \n用途: 当事者が大筋で合意したが、最終承認や正式契約がまだ済んでいない状態を表す。  \n例: The two sides reached a tentative agreement after three days of talks.  \n訳: 両者は3日間の協議の後、暫定合意に達した。  \n\n・tentative conclusions/findings  \n用途: 調査や分析の途中で得られ、追加の確認で修正され得る結論・結果を表す。  \n例: The researchers presented their tentative findings at the workshop.  \n訳: 研究者たちはワークショップで予備的な研究結果を発表した。  \n\n・a tentative explanation for 〈phenomenon/problem〉  \n用途: 現象や問題を説明する仮説を、確定的な説明としてではなく提示する。  \n例: The team offered a tentative explanation for the sudden drop in demand.  \n訳: チームは需要が急減したことについて暫定的な説明を示した。  \n\n・a tentative identification of 〈person/object〉  \n用途: 証拠が十分でなく、現段階での仮の同定であることを示す。  \n例: The police made a tentative identification of the vehicle from the video.  \n訳: 警察は映像からその車両を暫定的に特定した。  \n\n・tentatively approve/accept/identify something  \n用途: 承認・受諾・特定を行うが、最終確認や条件の充足を残していることを表す。  \n例: The board tentatively approved the budget pending a legal review.  \n訳: 取締役会は法務審査を条件として、その予算を暫定承認した。  \n\n【語法・注意】tentative は「その場しのぎの」「短期間の」と同義ではない。`a tentative date` は期間が短い日付ではなく、まだ変更され得る候補日である。`a tentative agreement` も正式な契約・最終合意とは限らず、`final`、`confirmed`、`settled` などで確定段階を示す。`uncertain` は結果や真偽が不確かなことを広く表すのに対し、tentative は計画・判断などをいったん置いているが確定させていないことに焦点がある。`preliminary` は作業・調査の初期段階であること、`provisional` は正式なものに代わる仮の状態であることを強調しやすい。  \n\n【類義語】\n\n・provisional  \n定義: 正式なものが決まるまで、暫定的に使われる。  \n頻度: 〈7/10〉  \n違い: provisional は正式な決定・制度・地位の代替として置かれることを強調し、tentative は内容がまだ固まっておらず変更され得ることを広く示す。  \n例: The committee issued a provisional approval while the documents were being checked.  \n訳: 委員会は書類を確認している間、暫定承認を出した。  \n\n・preliminary  \n定義: 本格的な検討や最終段階の前に行われる、初期段階の。  \n頻度: 〈8/10〉  \n違い: preliminary は時期・段階が早いことに焦点があり、tentative はその結論や計画がまだ確定していないことに焦点がある。  \n例: The report contains preliminary results from the first experiment.  \n訳: その報告書には最初の実験の予備結果が含まれている。  \n\n・conditional  \n定義: 特定の条件が満たされる場合にだけ成立する。  \n頻度: 〈8/10〉  \n違い: conditional は変更の理由となる条件を明示する語で、tentative は条件を示さなくても、現段階で確定していないことを表せる。  \n例: The offer is conditional on approval from the lender.  \n訳: その申し出は貸し手の承認を条件としている。  \n\n・unconfirmed  \n定義: 正式な確認や裏付けがまだ得られていない。  \n頻度: 〈7/10〉  \n違い: unconfirmed は情報の確認状態に焦点があり、tentative は情報だけでなく計画・合意・結論を仮置きする場合にも使う。  \n例: The report was based on an unconfirmed account of the incident.  \n訳: その報告書は、その出来事についてまだ確認されていない説明に基づいていた。  \n\n【反意語】\n\n・definite  \n定義: 内容や予定が明確に決まっていて、曖昧さが少ない。  \n頻度: 〈9/10〉  \n違い: definite は tentative の「未確定」に対する直接的な反対側を示す。  \n例: We need a definite answer before we book the venue.  \n訳: 会場を予約する前に、確定した返事が必要だ。  \n\n・confirmed  \n定義: 確認や承認によって、正しいもの・正式なものとして確定している。  \n頻度: 〈9/10〉  \n違い: confirmed は確認手続きが済んだことに焦点があり、tentative はその手続きの前段階を示す。  \n例: The confirmed departure time is shown on your ticket.  \n訳: 確定した出発時刻はチケットに表示されている。  \n\n・final  \n定義: それ以上の変更・検討を予定しない最終的な。  \n頻度: 〈10/10〉  \n違い: final は変更を終えた段階、tentative は変更の余地を残した段階を表す。  \n例: The final schedule will be sent to all participants tomorrow.  \n訳: 最終日程は明日、参加者全員に送られる。  \n\n2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な\n\n【日本語訳・定義】人の行動、声、表情、返答、提案などが、確信や自信を十分に示さず、様子をうかがいながら慎重に行われることを表す。単に静か・弱いという意味ではなく、失敗や拒否を恐れている、またはまだ慣れていないような不確かさが表れやすい。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】標準語で、会話・描写・物語・心理描写・対人場面に広く使う。smile、voice、answer、reply、greeting、knock、step、attempt、gesture など、意志や動作の現れ方を表す語と結びつく。  \n\n【文法パターン】a tentative 〈smile/voice/answer/reply〉＝ためらいがちな〈笑顔・声・返答〉／take tentative steps＝おそるおそる歩み出す・初めの一歩を踏み出す／make a tentative attempt/gesture＝慎重な試み・身振りをする／be tentative about 〈doing something〉＝～することにためらいがある／sound/look/seem tentative＝声・様子が自信なさそうに聞こえる・見える／tentatively ask/suggest/reply＝ためらいながら尋ねる・提案する・返答する。  \n\n【コロケーション】\n\n・a tentative smile  \n用途: 相手の反応をうかがうような、確信のない笑顔を表す。  \n例: She gave him a tentative smile before entering the unfamiliar room.  \n訳: 彼女は見慣れない部屋に入る前、彼にためらいがちな笑顔を向けた。  \n\n・a tentative answer/reply  \n用途: 答えを断定せず、自信がないまま返すことを表す。  \n例: He gave a tentative answer because he had not checked the figures.  \n訳: 彼は数字を確認していなかったので、自信のない返答をした。  \n\n・a tentative voice/tone  \n用途: 声や口調にためらい・不確かさが表れていることを表す。  \n例: “Perhaps we should wait,” she said in a tentative voice.  \n訳: 「待ったほうがよいかもしれません」と、彼女はためらいがちな声で言った。  \n\n・a tentative knock on 〈door〉  \n用途: 在室や反応を確かめるように、強く決め込まずノックすることを表す。  \n例: There was a tentative knock on the office door.  \n訳: オフィスのドアをおそるおそるノックする音がした。  \n\n・take tentative steps towards 〈goal/change〉  \n用途: 目標や変化に向けて、確信はないが最初の行動を始めることを表す。  \n例: The company is taking tentative steps toward reducing its use of plastic.  \n訳: その会社はプラスチックの使用を減らすための最初の一歩を慎重に踏み出している。  \n\n・make a tentative attempt to do something  \n用途: 成功の確信はないが、試しに行動を起こすことを表す。  \n例: The child made a tentative attempt to join the other players.  \n訳: その子どもは、ほかの遊び仲間に加わろうとおそるおそる試みた。  \n\n・be tentative about 〈doing something〉  \n用途: 何かをすることに自信がなく、決めかねている状態を表す。  \n例: She was tentative about speaking up in front of the whole team.  \n訳: 彼女はチーム全員の前で発言することをためらっていた。  \n\n・tentatively suggest/ask something  \n用途: 相手の反応を見ながら、強く主張せずに提案・質問することを表す。  \n例: He tentatively suggested moving the meeting to Friday.  \n訳: 彼は会議を金曜日に移してはどうかと、ためらいがちに提案した。  \n\n【語法・注意】この意味の tentative は、計画が未確定という語義1と異なり、行為者の態度や動作の仕方を描写する。`a tentative smile` は「仮の笑顔」ではなく、相手の反応を確かめるような笑顔である。`hesitant` は決断・発言・行動をためらうことを直接表す最も近い語、`cautious` は危険や失敗を避けるための用心深さを表し、必ずしも自信のなさを含まない。`tentative steps` は文字どおり歩く場合も、計画・改革への初期行動を比喩的に表す場合もある。  \n\n【類義語】\n\n・hesitant  \n定義: 決めたり行動したりすることをためらっている。  \n頻度: 〈9/10〉  \n違い: hesitant は意思決定や行動を進められないためらいを直接示し、tentative は声・表情・動作が自信なさそうに現れる様子まで表せる。  \n例: She was hesitant to raise the issue during the meeting.  \n訳: 彼女は会議中にその問題を持ち出すのをためらった。  \n\n・uncertain  \n定義: 自分の判断・答え・行動に確信がない。  \n頻度: 〈9/10〉  \n違い: uncertain は認識や判断の不確かさを広く表し、tentative はその不確かさが行動・発言・表情に現れていることを描きやすい。  \n例: He sounded uncertain when asked about the cause.  \n訳: 原因を尋ねられたとき、彼は自信がなさそうに聞こえた。  \n\n・cautious  \n定義: 危険・損失・誤りを避けるために用心深い。  \n頻度: 〈9/10〉  \n違い: cautious はリスク管理の意識を含むが、tentative は必ずしも危険を評価しているとは限らず、自信のなさや慣れていない感じを示す。  \n例: The manager took a cautious approach to the unfamiliar market.  \n訳: その管理者は未知の市場に慎重な姿勢で臨んだ。  \n\n・faltering  \n定義: 力強さや流暢さを欠き、途中で弱まったりつまずいたりする。  \n頻度: 〈6/10〉  \n違い: faltering は声・歩み・進行が不安定で途切れがちな結果に焦点があり、tentative は最初から確信を持てず慎重に行う態度に焦点がある。  \n例: His faltering voice revealed how nervous he was.  \n訳: 彼の途切れがちな声から、彼がどれほど緊張していたかが分かった。  \n\n【反意語】\n\n・confident  \n定義: 自分の能力・判断・発言に確信を持っている。  \n頻度: 〈10/10〉  \n違い: confident は tentative の「自信のない態度」に対する直接的な反対を表す。  \n例: She gave a confident answer to the difficult question.  \n訳: 彼女はその難しい質問に自信を持って答えた。  \n\n・assured  \n定義: 落ち着きと自信があり、確実そうに見える。  \n頻度: 〈7/10〉  \n違い: assured は態度・話し方・演技などに表れる落ち着いた自信を強調し、confident より改まった響きがある。  \n例: The speaker adopted an assured tone from the beginning.  \n訳: その話し手は最初から自信に満ちた口調を取った。  \n\n・decisive  \n定義: 迷わず判断し、行動をはっきり決める。  \n頻度: 〈8/10〉  \n違い: decisive は決断や行動の速さ・明確さに焦点があり、tentative は決めかねながら慎重に進めることを表す。  \n例: The director took decisive action when the system failed.  \n訳: システムが停止したとき、部長は断固たる行動を取った。  \n\n3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目\n\n【日本語訳・定義】予約、契約、日程、出演枠などについて、正式な確定や契約が済む前に、仮のものとして記録・扱われる項目を表す。一般会話で広く使う名詞ではなく、複数形 tentatives を含む業務上・事務上の文脈で見られる低頻度用法である。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】低頻度。イベント予約、放送・興行、契約管理など、仮押さえや契約待ちの項目を区別する実務的な文脈に限られやすい。通常は a tentative booking、a tentative date、a tentative arrangement のように形容詞として言うほうが自然である。  \n\n【文法パターン】a tentative＝1件の暫定項目／tentatives＝複数の暫定項目／list/hold/book dates as tentatives＝日程を暫定項目として一覧化・仮押さえする。  \n\n【コロケーション】\n\n・list the dates as tentatives  \n用途: 契約や正式確認が済んでいない日程を仮の枠として記録する。  \n例: The theater listed the autumn dates as tentatives while it waited for the contracts.  \n訳: その劇場は契約を待つ間、秋の日程を暫定枠として記録した。  \n\n・hold a date as a tentative  \n用途: 日程を正式決定前の仮押さえとして扱う。  \n例: The producer asked us to hold the date as a tentative until Friday.  \n訳: プロデューサーは、金曜日まではその日を仮押さえとしておくよう私たちに頼んだ。  \n\n【語法・注意】この名詞用法は一般的な「仮のもの」の言い換えとして自由に使う語ではない。通常の文章では `a tentative plan`、`a tentative booking` のように形容詞用法を選ぶ。名詞の tentative が必要かどうかは業界の慣行によって異なり、読者に伝わりにくい場合は provisional item、pending booking など具体的な表現で言い換える。  \n\n【類義語】\n\n・provisional item  \n定義: 正式決定まで仮のものとして記録・管理される項目。  \n頻度: 〈3/10〉  \n違い: provisional item は意味を明示する説明的な句で、名詞 tentative の業務上の用法を平易に言い換える。tentative より自然に伝わりやすいが、特定業界の固定用語とは限らない。  \n例: The spreadsheet marks each provisional item in gray until the contract is signed.  \n訳: その表計算シートでは、契約が締結されるまで各暫定項目を灰色で示している。  \n\n・pending booking  \n定義: 確定や支払いなどを待っている仮予約。  \n頻度: 〈4/10〉  \n違い: pending booking は予約に意味を限定し、保留中であることを直接示す。tentative は予約以外の日程・契約項目にも使える。  \n例: We kept the pending booking separate from the confirmed reservations.  \n訳: 私たちは保留中の仮予約を、確定済みの予約とは別にしておいた。  ",
  "_output_metadata": {
    "schema_version": "final_review_v3",
    "stage": "final_review",
    "run_id": "blind-tentative-20260921T145448Z-bec4a398",
    "context_id": "blind-tentative-context-20260921T145448Z-bec4a398",
    "input_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f",
    "prompt_sha256": "7fee3a9d388e6557c2d8a66702e890b2398ca20228e61072acc81eedafcfac9d",
    "input_artifacts": [
      "entry_body",
      "sealed_final_blind",
      "pre_blind_resolution",
      "post_blind_resolution",
      "checker_recheck_manifest",
      "targeted_adjudications",
      "final_review_spec"
    ]
  },
  "review_context": {
    "checker_summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency.",
    "cold_review_summary": "問題候補なし。本文全体を文脈なしで確認し、語義の境界、用法、例文、訳、品詞表示、学習者が行い得る一般化を点検したが、具体的に指摘すべき内容上の問題は見当たらない。",
    "final_blind_decision": "pass",
    "blind_seal": {
      "schema_version": "blind_seal_v3",
      "stage": "blind_seal",
      "entry_path": "entries/t/tentative.md",
      "body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f",
      "final_blind_path": "audits/runs/t/tentative/20260921T145448Z-bec4a398/final_blind.json",
      "final_blind_sha256": "1570cec673e640a8658f10b544ebc3b20d622a74f57ced594549a9f7be7d156b",
      "blind_output_sha256": "2907d509d508763f3624cb333175bd545f9622d6328929d6cd410c03d05df45b",
      "sealed_at": "2026-09-22T00:43:55.007801+09:00"
    },
    "checker_recheck": {
      "current_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f",
      "full_recheck": false,
      "invalidated_passes": [],
      "pass_results": [
        {
          "pass_id": "evidence",
          "mode": "reused",
          "spec_sha256": "f0de393d4d064190e23916b2e8bfda25b2b83fd29e14cf52395c894b8539d7e9",
          "normalized_input_sha256": "6f860cd5ea14b699afc3a83f2623149552686fb85516975642e85ff807dd5281",
          "source_artifact_sha256": "f84b1ebfd7802053fbc9fa711329bde0991dbd742d9be98f3f516baa3ff2b11f",
          "output_sha256": "aaac5e80275d75aecafba750d30b0baf67d6ee2b66051b1d43bf1c3376c322fa",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reuse_validated": true,
          "reviewer_agent_id": "tentative-checker-evidence-1",
          "output_path": "audits/runs/t/tentative/20260921T145448Z-bec4a398/check_passes/evidence.json",
          "reuse_proof_path": null,
          "validated_on_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
        },
        {
          "pass_id": "example-attribution",
          "mode": "reused",
          "spec_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
          "normalized_input_sha256": "d717d446d31d139801bd8b7ef3f4ed6ab77b20173081a062aa5eb19538c637c9",
          "source_artifact_sha256": "f84b1ebfd7802053fbc9fa711329bde0991dbd742d9be98f3f516baa3ff2b11f",
          "output_sha256": "201ff4e881ea3d89f75645461e1b71980014f3379fb923adce6bb41194d9d287",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reuse_validated": true,
          "reviewer_agent_id": "tentative-checker-example-attribution-1",
          "output_path": "audits/runs/t/tentative/20260921T145448Z-bec4a398/check_passes/example-attribution.json",
          "reuse_proof_path": null,
          "validated_on_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
        },
        {
          "pass_id": "frame-relation",
          "mode": "reused",
          "spec_sha256": "3598ca81a5784639c6b43a0806d0981a985bf4174f424c744aad1dde787bfcef",
          "normalized_input_sha256": "3589ea747175fadabb8cc558be4d7a10159414d4ff12c77bc9551d0da0d582dd",
          "source_artifact_sha256": "f84b1ebfd7802053fbc9fa711329bde0991dbd742d9be98f3f516baa3ff2b11f",
          "output_sha256": "db6d4f247c58e4a6a887c71e82cc40f124b63e8880d38e257241aaa8efe458a8",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reuse_validated": true,
          "reviewer_agent_id": "tentative-checker-frame-relation-1",
          "output_path": "audits/runs/t/tentative/20260921T145448Z-bec4a398/pass_findings.json",
          "reuse_proof_path": null,
          "validated_on_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
        },
        {
          "pass_id": "pronunciation",
          "mode": "reused",
          "spec_sha256": "7e3e94267ac9f917c901c12580b91e570b5989df7adfbf2a39b833478c766d8a",
          "normalized_input_sha256": "6d407560b2fbdde28b6f65e28008e47b694b13f0cfcd7816fa591af7ac554c6a",
          "source_artifact_sha256": "f84b1ebfd7802053fbc9fa711329bde0991dbd742d9be98f3f516baa3ff2b11f",
          "output_sha256": "95b8d6524b63a012d819b16fe37d4424a92d8ce4e632e14833542aad397c06cd",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reuse_validated": true,
          "reviewer_agent_id": "tentative-checker-pronunciation-1",
          "output_path": "audits/runs/t/tentative/20260921T145448Z-bec4a398/check_passes/pronunciation.json",
          "reuse_proof_path": null,
          "validated_on_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
        },
        {
          "pass_id": "qualification",
          "mode": "reused",
          "spec_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
          "normalized_input_sha256": "7a5370235aef5b90d2926ef11e836a3b49897a6a1f463dfacb2ee22e5e8dbc79",
          "source_artifact_sha256": "f84b1ebfd7802053fbc9fa711329bde0991dbd742d9be98f3f516baa3ff2b11f",
          "output_sha256": "cae3b87ebd744f702c3ee61659507c9b26350fbdb3d2468795df3491a891173b",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reuse_validated": true,
          "reviewer_agent_id": "tentative-checker-qualification-1",
          "output_path": "audits/runs/t/tentative/20260921T145448Z-bec4a398/check_passes/qualification.json",
          "reuse_proof_path": null,
          "validated_on_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
        },
        {
          "pass_id": "sense-structure",
          "mode": "reused",
          "spec_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
          "normalized_input_sha256": "ec7bcaa5880075e3b72892444d0c6fae5c18fefa9b9f13c3eeb4a39354a7123e",
          "source_artifact_sha256": "f84b1ebfd7802053fbc9fa711329bde0991dbd742d9be98f3f516baa3ff2b11f",
          "output_sha256": "97b0e5125433748219855dacc2be22ae57cc32ca2ade51cda88129e046efb668",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reuse_validated": true,
          "reviewer_agent_id": "tentative-checker-sense-structure-1",
          "output_path": "audits/runs/t/tentative/20260921T145448Z-bec4a398/check_passes/sense-structure.json",
          "reuse_proof_path": null,
          "validated_on_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
        },
        {
          "pass_id": "translation",
          "mode": "reused",
          "spec_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
          "normalized_input_sha256": "511f539e04aa2239073b6874dfc8c8e086dc0fb000259d89b0b66fffcc3273ef",
          "source_artifact_sha256": "f84b1ebfd7802053fbc9fa711329bde0991dbd742d9be98f3f516baa3ff2b11f",
          "output_sha256": "6263f7020641e55554a72bc908bdee913a6fb02ade57f225189046eb40ca2c83",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reuse_validated": true,
          "reviewer_agent_id": "tentative-checker-translation-1",
          "output_path": "audits/runs/t/tentative/20260921T145448Z-bec4a398/check_passes/translation.json",
          "reuse_proof_path": null,
          "validated_on_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
        }
      ]
    },
    "post_blind_verification": {
      "schema_version": "post_blind_verification_v1",
      "verified_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f",
      "checker_recheck_completed": true,
      "final_blind_repeated": false,
      "final_blind_sha256": "1570cec673e640a8658f10b544ebc3b20d622a74f57ced594549a9f7be7d156b",
      "attempt_number": 1
    },
    "resolutions": [
      {
        "id": "finding_example_sense_attribution_tentative_knock",
        "finding_id": "finding_example_sense_attribution_tentative_knock",
        "status": "resolved",
        "disposition": "rejected",
        "resolved_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f",
        "rationale": "The quoted example \"例: There was a tentative knock on the office door.  \" describes a cautious knocking action and is correctly placed under the hesitant-manner adjective sense. The checker attribution record, rather than the article, assigned it to the rare noun sense, so no article movement is warranted."
      }
    ]
  },
  "inventories": {
    "target_results": [
      {
        "id": "pronunciation:001",
        "kind": "pronunciation",
        "location": "line:4",
        "section": "＃発音記号",
        "sense": "",
        "text": "米・英: /ˈtentətɪv/。3音節で、第1音節の /ˈten/ に主強勢がある。第2音節は弱い /tə/、語末は /tɪv/ と発音する。tentatively は /ˈtentətɪvli/、tentativeness は /ˈtentətɪvnəs/ のように、派生語でも第1音節の強勢を保つ。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text": "16世紀後半に使われ始めた語で、中世ラテン語 tentativus「試みる性質の、試験的な、暫定的な」から来た。これはラテン語 tentare／temptare「触れて確かめる、試す、試みる」に由来する。「まず試してみる段階」という意味から、まだ十分に固まっていない「暫定的な」と、試みる人の「自信のない、ためらいがちな」へ意味が広がった。attempt、tempt、tentatively、tentativeness は同じラテン語の語族に関係するが、tentative の単純な活用形ではない。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text": "・tentatively：副詞。「暫定的に、仮に」または「ためらいがちに、自信なさそうに」。修飾する内容によって2つの形容詞義に対応する。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text": "・tentativeness：名詞。「暫定性、未確定性」または「ためらい、自信のなさ」。通常は不可算名詞で、性質や態度を表す。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text": "・tentative：名詞転用。「暫定的なもの、仮の項目」。まれで、予約・契約・日程などが確定する前の業務上の項目を指すことがある。"
      },
      {
        "id": "word_formation:004",
        "kind": "word_formation",
        "location": "line:15",
        "section": "＃語形成",
        "sense": "",
        "text": "・attempt／tempt：同じラテン語 tentare／temptare にさかのぼる関連語。attempt は「試み」、tempt は現代英語で主に「誘惑する」を表し、tentative の派生語ではない。"
      },
      {
        "id": "core_image:001",
        "kind": "core_image",
        "location": "line:19",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "tentative の共通核は、「まだ確定させず、試しに触れている段階」である。計画や判断なら後で変更され得る「暫定性」、行動や表情なら確信を持たず慎重に踏み出す「ためらい」として現れる。"
      },
      {
        "id": "core_image:002",
        "kind": "core_image",
        "location": "line:20",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "・内容を試しに置き、後で変えられる状態 → 「暫定的な、仮の」（語義1）"
      },
      {
        "id": "core_image:003",
        "kind": "core_image",
        "location": "line:21",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "・行動を試しに行い、確信を持てない様子 → 「ためらいがちな、自信のない」（語義2）"
      },
      {
        "id": "core_image:004",
        "kind": "core_image",
        "location": "line:22",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "・確定前の項目を業務上の仮登録として扱う → 「暫定案、仮の項目」（語義3）"
      },
      {
        "id": "sense_boundary:001",
        "kind": "sense_boundary",
        "location": "line:26",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:28",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "計画、日程、合意、結論、説明、提案、識別などが、現時点では候補として置かれているものの、検討・交渉・確認が終わっておらず、後で変更または撤回される可能性があることを表す。単に「一時的」という期間の短さではなく、内容の確定性がまだ低いことに焦点がある。"
      },
      {
        "id": "frequency:001",
        "kind": "frequency",
        "location": "line:30",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "〈9/10〉"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:32",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "標準語で、会話・報道・ビジネス・学術・交渉まで広く使う。特に plan、date、schedule、arrangement、agreement、conclusion、explanation、identification など、後から確認や調整が入り得る名詞と結びつく。"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "a tentative 〈plan/date/schedule/arrangement/agreement〉＝暫定的な〈計画・日付・予定・取り決め・合意〉"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "tentative conclusions/findings＝予備的な結論・調査結果"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "a tentative explanation/identification＝暫定的な説明・仮の同定"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "make/reach/announce a tentative decision＝暫定的な決定をする・出す"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "be tentative about 〈the date/details〉＝〈日付・詳細〉がまだ確定していない"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "tentative plans to do＝～する暫定的な計画"
      },
      {
        "id": "grammar_pattern:007",
        "kind": "grammar_pattern",
        "location": "line:34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "tentatively agree/approve/identify＝暫定的に合意する・承認する・特定する。"
      },
      {
        "id": "collocation:001",
        "kind": "collocation",
        "location": "lines:38-41",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・tentative plans for 〈event/activity〉\n用途: 予定はあるが、内容や日時がまだ変わる可能性があることを表す。\n例: We have tentative plans for a short trip in October.\n訳: 私たちは10月に短い旅行をする仮の予定がある。"
      },
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:43-46",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・a tentative date for 〈event〉\n用途: 会議・発売・開始などの日付を候補として置く。\n例: The organizers set a tentative date for the conference in early May.\n訳: 主催者は会議の開催日を5月初旬の仮の日付として設定した。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:48-51",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・a tentative schedule\n用途: 今後の調整で変更され得る予定表を指す。\n例: The airline released a tentative schedule for the new route.\n訳: その航空会社は新路線の暫定的な運航予定を公表した。"
      },
      {
        "id": "collocation:004",
        "kind": "collocation",
        "location": "lines:53-56",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・a tentative agreement/deal\n用途: 当事者が大筋で合意したが、最終承認や正式契約がまだ済んでいない状態を表す。\n例: The two sides reached a tentative agreement after three days of talks.\n訳: 両者は3日間の協議の後、暫定合意に達した。"
      },
      {
        "id": "collocation:005",
        "kind": "collocation",
        "location": "lines:58-61",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・tentative conclusions/findings\n用途: 調査や分析の途中で得られ、追加の確認で修正され得る結論・結果を表す。\n例: The researchers presented their tentative findings at the workshop.\n訳: 研究者たちはワークショップで予備的な研究結果を発表した。"
      },
      {
        "id": "collocation:006",
        "kind": "collocation",
        "location": "lines:63-66",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・a tentative explanation for 〈phenomenon/problem〉\n用途: 現象や問題を説明する仮説を、確定的な説明としてではなく提示する。\n例: The team offered a tentative explanation for the sudden drop in demand.\n訳: チームは需要が急減したことについて暫定的な説明を示した。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:68-71",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・a tentative identification of 〈person/object〉\n用途: 証拠が十分でなく、現段階での仮の同定であることを示す。\n例: The police made a tentative identification of the vehicle from the video.\n訳: 警察は映像からその車両を暫定的に特定した。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:73-76",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・tentatively approve/accept/identify something\n用途: 承認・受諾・特定を行うが、最終確認や条件の充足を残していることを表す。\n例: The board tentatively approved the budget pending a legal review.\n訳: 取締役会は法務審査を条件として、その予算を暫定承認した。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:78",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "tentative は「その場しのぎの」「短期間の」と同義ではない。`a tentative date` は期間が短い日付ではなく、まだ変更され得る候補日である。`a tentative agreement` も正式な契約・最終合意とは限らず、`final`、`confirmed`、`settled` などで確定段階を示す。`uncertain` は結果や真偽が不確かなことを広く表すのに対し、tentative は計画・判断などをいったん置いているが確定させていないことに焦点がある。`preliminary` は作業・調査の初期段階であること、`provisional` は正式なものに代わる仮の状態であることを強調しやすい。"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:82-87",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・provisional\n定義: 正式なものが決まるまで、暫定的に使われる。\n頻度: 〈7/10〉\n違い: provisional は正式な決定・制度・地位の代替として置かれることを強調し、tentative は内容がまだ固まっておらず変更され得ることを広く示す。\n例: The committee issued a provisional approval while the documents were being checked.\n訳: 委員会は書類を確認している間、暫定承認を出した。"
      },
      {
        "id": "synonym:002",
        "kind": "synonym",
        "location": "lines:89-94",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・preliminary\n定義: 本格的な検討や最終段階の前に行われる、初期段階の。\n頻度: 〈8/10〉\n違い: preliminary は時期・段階が早いことに焦点があり、tentative はその結論や計画がまだ確定していないことに焦点がある。\n例: The report contains preliminary results from the first experiment.\n訳: その報告書には最初の実験の予備結果が含まれている。"
      },
      {
        "id": "synonym:003",
        "kind": "synonym",
        "location": "lines:96-101",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・conditional\n定義: 特定の条件が満たされる場合にだけ成立する。\n頻度: 〈8/10〉\n違い: conditional は変更の理由となる条件を明示する語で、tentative は条件を示さなくても、現段階で確定していないことを表せる。\n例: The offer is conditional on approval from the lender.\n訳: その申し出は貸し手の承認を条件としている。"
      },
      {
        "id": "synonym:004",
        "kind": "synonym",
        "location": "lines:103-108",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・unconfirmed\n定義: 正式な確認や裏付けがまだ得られていない。\n頻度: 〈7/10〉\n違い: unconfirmed は情報の確認状態に焦点があり、tentative は情報だけでなく計画・合意・結論を仮置きする場合にも使う。\n例: The report was based on an unconfirmed account of the incident.\n訳: その報告書は、その出来事についてまだ確認されていない説明に基づいていた。"
      },
      {
        "id": "antonym:001",
        "kind": "antonym",
        "location": "lines:112-117",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・definite\n定義: 内容や予定が明確に決まっていて、曖昧さが少ない。\n頻度: 〈9/10〉\n違い: definite は tentative の「未確定」に対する直接的な反対側を示す。\n例: We need a definite answer before we book the venue.\n訳: 会場を予約する前に、確定した返事が必要だ。"
      },
      {
        "id": "antonym:002",
        "kind": "antonym",
        "location": "lines:119-124",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・confirmed\n定義: 確認や承認によって、正しいもの・正式なものとして確定している。\n頻度: 〈9/10〉\n違い: confirmed は確認手続きが済んだことに焦点があり、tentative はその手続きの前段階を示す。\n例: The confirmed departure time is shown on your ticket.\n訳: 確定した出発時刻はチケットに表示されている。"
      },
      {
        "id": "antonym:003",
        "kind": "antonym",
        "location": "lines:126-131",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】暫定的な、仮の、まだ確定していない",
        "text": "・final\n定義: それ以上の変更・検討を予定しない最終的な。\n頻度: 〈10/10〉\n違い: final は変更を終えた段階、tentative は変更の余地を残した段階を表す。\n例: The final schedule will be sent to all participants tomorrow.\n訳: 最終日程は明日、参加者全員に送られる。"
      },
      {
        "id": "sense_boundary:002",
        "kind": "sense_boundary",
        "location": "line:133",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:135",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "人の行動、声、表情、返答、提案などが、確信や自信を十分に示さず、様子をうかがいながら慎重に行われることを表す。単に静か・弱いという意味ではなく、失敗や拒否を恐れている、またはまだ慣れていないような不確かさが表れやすい。"
      },
      {
        "id": "frequency:002",
        "kind": "frequency",
        "location": "line:137",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "〈8/10〉"
      },
      {
        "id": "register:002",
        "kind": "register",
        "location": "line:139",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "標準語で、会話・描写・物語・心理描写・対人場面に広く使う。smile、voice、answer、reply、greeting、knock、step、attempt、gesture など、意志や動作の現れ方を表す語と結びつく。"
      },
      {
        "id": "grammar_pattern:008",
        "kind": "grammar_pattern",
        "location": "line:141",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "a tentative 〈smile/voice/answer/reply〉＝ためらいがちな〈笑顔・声・返答〉"
      },
      {
        "id": "grammar_pattern:009",
        "kind": "grammar_pattern",
        "location": "line:141",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "take tentative steps＝おそるおそる歩み出す・初めの一歩を踏み出す"
      },
      {
        "id": "grammar_pattern:010",
        "kind": "grammar_pattern",
        "location": "line:141",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "make a tentative attempt/gesture＝慎重な試み・身振りをする"
      },
      {
        "id": "grammar_pattern:011",
        "kind": "grammar_pattern",
        "location": "line:141",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "be tentative about 〈doing something〉＝～することにためらいがある"
      },
      {
        "id": "grammar_pattern:012",
        "kind": "grammar_pattern",
        "location": "line:141",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "sound/look/seem tentative＝声・様子が自信なさそうに聞こえる・見える"
      },
      {
        "id": "grammar_pattern:013",
        "kind": "grammar_pattern",
        "location": "line:141",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "tentatively ask/suggest/reply＝ためらいながら尋ねる・提案する・返答する。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:145-148",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・a tentative smile\n用途: 相手の反応をうかがうような、確信のない笑顔を表す。\n例: She gave him a tentative smile before entering the unfamiliar room.\n訳: 彼女は見慣れない部屋に入る前、彼にためらいがちな笑顔を向けた。"
      },
      {
        "id": "collocation:010",
        "kind": "collocation",
        "location": "lines:150-153",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・a tentative answer/reply\n用途: 答えを断定せず、自信がないまま返すことを表す。\n例: He gave a tentative answer because he had not checked the figures.\n訳: 彼は数字を確認していなかったので、自信のない返答をした。"
      },
      {
        "id": "collocation:011",
        "kind": "collocation",
        "location": "lines:155-158",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・a tentative voice/tone\n用途: 声や口調にためらい・不確かさが表れていることを表す。\n例: “Perhaps we should wait,” she said in a tentative voice.\n訳: 「待ったほうがよいかもしれません」と、彼女はためらいがちな声で言った。"
      },
      {
        "id": "collocation:012",
        "kind": "collocation",
        "location": "lines:160-163",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・a tentative knock on 〈door〉\n用途: 在室や反応を確かめるように、強く決め込まずノックすることを表す。\n例: There was a tentative knock on the office door.\n訳: オフィスのドアをおそるおそるノックする音がした。"
      },
      {
        "id": "collocation:013",
        "kind": "collocation",
        "location": "lines:165-168",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・take tentative steps towards 〈goal/change〉\n用途: 目標や変化に向けて、確信はないが最初の行動を始めることを表す。\n例: The company is taking tentative steps toward reducing its use of plastic.\n訳: その会社はプラスチックの使用を減らすための最初の一歩を慎重に踏み出している。"
      },
      {
        "id": "collocation:014",
        "kind": "collocation",
        "location": "lines:170-173",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・make a tentative attempt to do something\n用途: 成功の確信はないが、試しに行動を起こすことを表す。\n例: The child made a tentative attempt to join the other players.\n訳: その子どもは、ほかの遊び仲間に加わろうとおそるおそる試みた。"
      },
      {
        "id": "collocation:015",
        "kind": "collocation",
        "location": "lines:175-178",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・be tentative about 〈doing something〉\n用途: 何かをすることに自信がなく、決めかねている状態を表す。\n例: She was tentative about speaking up in front of the whole team.\n訳: 彼女はチーム全員の前で発言することをためらっていた。"
      },
      {
        "id": "collocation:016",
        "kind": "collocation",
        "location": "lines:180-183",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・tentatively suggest/ask something\n用途: 相手の反応を見ながら、強く主張せずに提案・質問することを表す。\n例: He tentatively suggested moving the meeting to Friday.\n訳: 彼は会議を金曜日に移してはどうかと、ためらいがちに提案した。"
      },
      {
        "id": "usage_note:002",
        "kind": "usage_note",
        "location": "line:185",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "この意味の tentative は、計画が未確定という語義1と異なり、行為者の態度や動作の仕方を描写する。`a tentative smile` は「仮の笑顔」ではなく、相手の反応を確かめるような笑顔である。`hesitant` は決断・発言・行動をためらうことを直接表す最も近い語、`cautious` は危険や失敗を避けるための用心深さを表し、必ずしも自信のなさを含まない。`tentative steps` は文字どおり歩く場合も、計画・改革への初期行動を比喩的に表す場合もある。"
      },
      {
        "id": "synonym:005",
        "kind": "synonym",
        "location": "lines:189-194",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・hesitant\n定義: 決めたり行動したりすることをためらっている。\n頻度: 〈9/10〉\n違い: hesitant は意思決定や行動を進められないためらいを直接示し、tentative は声・表情・動作が自信なさそうに現れる様子まで表せる。\n例: She was hesitant to raise the issue during the meeting.\n訳: 彼女は会議中にその問題を持ち出すのをためらった。"
      },
      {
        "id": "synonym:006",
        "kind": "synonym",
        "location": "lines:196-201",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・uncertain\n定義: 自分の判断・答え・行動に確信がない。\n頻度: 〈9/10〉\n違い: uncertain は認識や判断の不確かさを広く表し、tentative はその不確かさが行動・発言・表情に現れていることを描きやすい。\n例: He sounded uncertain when asked about the cause.\n訳: 原因を尋ねられたとき、彼は自信がなさそうに聞こえた。"
      },
      {
        "id": "synonym:007",
        "kind": "synonym",
        "location": "lines:203-208",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・cautious\n定義: 危険・損失・誤りを避けるために用心深い。\n頻度: 〈9/10〉\n違い: cautious はリスク管理の意識を含むが、tentative は必ずしも危険を評価しているとは限らず、自信のなさや慣れていない感じを示す。\n例: The manager took a cautious approach to the unfamiliar market.\n訳: その管理者は未知の市場に慎重な姿勢で臨んだ。"
      },
      {
        "id": "synonym:008",
        "kind": "synonym",
        "location": "lines:210-215",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・faltering\n定義: 力強さや流暢さを欠き、途中で弱まったりつまずいたりする。\n頻度: 〈6/10〉\n違い: faltering は声・歩み・進行が不安定で途切れがちな結果に焦点があり、tentative は最初から確信を持てず慎重に行う態度に焦点がある。\n例: His faltering voice revealed how nervous he was.\n訳: 彼の途切れがちな声から、彼がどれほど緊張していたかが分かった。"
      },
      {
        "id": "antonym:004",
        "kind": "antonym",
        "location": "lines:219-224",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・confident\n定義: 自分の能力・判断・発言に確信を持っている。\n頻度: 〈10/10〉\n違い: confident は tentative の「自信のない態度」に対する直接的な反対を表す。\n例: She gave a confident answer to the difficult question.\n訳: 彼女はその難しい質問に自信を持って答えた。"
      },
      {
        "id": "antonym:005",
        "kind": "antonym",
        "location": "lines:226-231",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・assured\n定義: 落ち着きと自信があり、確実そうに見える。\n頻度: 〈7/10〉\n違い: assured は態度・話し方・演技などに表れる落ち着いた自信を強調し、confident より改まった響きがある。\n例: The speaker adopted an assured tone from the beginning.\n訳: その話し手は最初から自信に満ちた口調を取った。"
      },
      {
        "id": "antonym:006",
        "kind": "antonym",
        "location": "lines:233-238",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】ためらいがちな、自信のない、慎重な",
        "text": "・decisive\n定義: 迷わず判断し、行動をはっきり決める。\n頻度: 〈8/10〉\n違い: decisive は決断や行動の速さ・明確さに焦点があり、tentative は決めかねながら慎重に進めることを表す。\n例: The director took decisive action when the system failed.\n訳: システムが停止したとき、部長は断固たる行動を取った。"
      },
      {
        "id": "sense_boundary:003",
        "kind": "sense_boundary",
        "location": "line:240",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目"
      },
      {
        "id": "definition:003",
        "kind": "definition",
        "location": "line:242",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "予約、契約、日程、出演枠などについて、正式な確定や契約が済む前に、仮のものとして記録・扱われる項目を表す。一般会話で広く使う名詞ではなく、複数形 tentatives を含む業務上・事務上の文脈で見られる低頻度用法である。"
      },
      {
        "id": "frequency:003",
        "kind": "frequency",
        "location": "line:244",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "〈2/10〉"
      },
      {
        "id": "register:003",
        "kind": "register",
        "location": "line:246",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "低頻度。イベント予約、放送・興行、契約管理など、仮押さえや契約待ちの項目を区別する実務的な文脈に限られやすい。通常は a tentative booking、a tentative date、a tentative arrangement のように形容詞として言うほうが自然である。"
      },
      {
        "id": "grammar_pattern:014",
        "kind": "grammar_pattern",
        "location": "line:248",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "a tentative＝1件の暫定項目"
      },
      {
        "id": "grammar_pattern:015",
        "kind": "grammar_pattern",
        "location": "line:248",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "tentatives＝複数の暫定項目"
      },
      {
        "id": "grammar_pattern:016",
        "kind": "grammar_pattern",
        "location": "line:248",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "list/hold/book dates as tentatives＝日程を暫定項目として一覧化・仮押さえする。"
      },
      {
        "id": "collocation:017",
        "kind": "collocation",
        "location": "lines:252-255",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "・list the dates as tentatives\n用途: 契約や正式確認が済んでいない日程を仮の枠として記録する。\n例: The theater listed the autumn dates as tentatives while it waited for the contracts.\n訳: その劇場は契約を待つ間、秋の日程を暫定枠として記録した。"
      },
      {
        "id": "collocation:018",
        "kind": "collocation",
        "location": "lines:257-260",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "・hold a date as a tentative\n用途: 日程を正式決定前の仮押さえとして扱う。\n例: The producer asked us to hold the date as a tentative until Friday.\n訳: プロデューサーは、金曜日まではその日を仮押さえとしておくよう私たちに頼んだ。"
      },
      {
        "id": "usage_note:003",
        "kind": "usage_note",
        "location": "line:262",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "この名詞用法は一般的な「仮のもの」の言い換えとして自由に使う語ではない。通常の文章では `a tentative plan`、`a tentative booking` のように形容詞用法を選ぶ。名詞の tentative が必要かどうかは業界の慣行によって異なり、読者に伝わりにくい場合は provisional item、pending booking など具体的な表現で言い換える。"
      },
      {
        "id": "synonym:009",
        "kind": "synonym",
        "location": "lines:266-271",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "・provisional item\n定義: 正式決定まで仮のものとして記録・管理される項目。\n頻度: 〈3/10〉\n違い: provisional item は意味を明示する説明的な句で、名詞 tentative の業務上の用法を平易に言い換える。tentative より自然に伝わりやすいが、特定業界の固定用語とは限らない。\n例: The spreadsheet marks each provisional item in gray until the contract is signed.\n訳: その表計算シートでは、契約が締結されるまで各暫定項目を灰色で示している。"
      },
      {
        "id": "synonym:010",
        "kind": "synonym",
        "location": "lines:273-278",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・可算／まれ・業務用語】暫定案、仮の項目",
        "text": "・pending booking\n定義: 確定や支払いなどを待っている仮予約。\n頻度: 〈4/10〉\n違い: pending booking は予約に意味を限定し、保留中であることを直接示す。tentative は予約以外の日程・契約項目にも使える。\n例: We kept the pending booking separate from the confirmed reservations.\n訳: 私たちは保留中の仮予約を、確定済みの予約とは別にしておいた。"
      }
    ],
    "relation_results": [
      {
        "id": "risk_sense_pair:001",
        "kind": "risk_sense_pair",
        "target_ids": [
          "sense_boundary:001",
          "sense_boundary:002"
        ],
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: usage_note:002 explicitly contrasts sense 2 with sense 1"
      },
      {
        "id": "example_translation:001",
        "kind": "example_translation",
        "target_ids": [
          "collocation:001"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:002",
        "kind": "example_translation",
        "target_ids": [
          "collocation:002"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:003",
        "kind": "example_translation",
        "target_ids": [
          "collocation:003"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:004",
        "kind": "example_translation",
        "target_ids": [
          "collocation:004"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:005",
        "kind": "example_translation",
        "target_ids": [
          "collocation:005"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:006",
        "kind": "example_translation",
        "target_ids": [
          "collocation:006"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:007",
        "kind": "example_translation",
        "target_ids": [
          "collocation:007"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:008",
        "kind": "example_translation",
        "target_ids": [
          "collocation:008"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:009",
        "kind": "example_translation",
        "target_ids": [
          "collocation:009"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:010",
        "kind": "example_translation",
        "target_ids": [
          "collocation:010"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:011",
        "kind": "example_translation",
        "target_ids": [
          "collocation:011"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:012",
        "kind": "example_translation",
        "target_ids": [
          "collocation:012"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:013",
        "kind": "example_translation",
        "target_ids": [
          "collocation:013"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:014",
        "kind": "example_translation",
        "target_ids": [
          "collocation:014"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:015",
        "kind": "example_translation",
        "target_ids": [
          "collocation:015"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:016",
        "kind": "example_translation",
        "target_ids": [
          "collocation:016"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:017",
        "kind": "example_translation",
        "target_ids": [
          "collocation:017"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:018",
        "kind": "example_translation",
        "target_ids": [
          "collocation:018"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "sense_definition_consistency:001",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。"
      },
      {
        "id": "definition_usage_consistency:001",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "usage_note:001"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。"
      },
      {
        "id": "definition_lexical_relation_consistency:001",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "synonym:001",
          "synonym:002",
          "synonym:003",
          "synonym:004",
          "antonym:001",
          "antonym:002",
          "antonym:003"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。"
      },
      {
        "id": "pattern_example_coverage:001",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:001",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007",
          "collocation:008"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:002",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:002",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007",
          "collocation:008"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:003",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:003",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007",
          "collocation:008"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:004",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:004",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007",
          "collocation:008"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:005",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:005",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007",
          "collocation:008"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:006",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:006",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007",
          "collocation:008"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:007",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:007",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007",
          "collocation:008"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "sense_definition_consistency:002",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。"
      },
      {
        "id": "definition_usage_consistency:002",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "usage_note:002"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。"
      },
      {
        "id": "definition_lexical_relation_consistency:002",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "synonym:005",
          "synonym:006",
          "synonym:007",
          "synonym:008",
          "antonym:004",
          "antonym:005",
          "antonym:006"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。"
      },
      {
        "id": "pattern_example_coverage:008",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:008",
          "collocation:009",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:009",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:009",
          "collocation:009",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:010",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:010",
          "collocation:009",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:011",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:011",
          "collocation:009",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:012",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:012",
          "collocation:009",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:013",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:013",
          "collocation:009",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013",
          "collocation:014",
          "collocation:015",
          "collocation:016"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "sense_definition_consistency:003",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。"
      },
      {
        "id": "definition_usage_consistency:003",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003",
          "usage_note:003"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。"
      },
      {
        "id": "definition_lexical_relation_consistency:003",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:003",
          "definition:003",
          "synonym:009",
          "synonym:010"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。"
      },
      {
        "id": "pattern_example_coverage:014",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:014",
          "collocation:017",
          "collocation:018"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:015",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:015",
          "collocation:017",
          "collocation:018"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:016",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:016",
          "collocation:017",
          "collocation:018"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "core_inventory_consistency:001",
        "kind": "core_inventory_consistency",
        "target_ids": [
          "core_image:001",
          "sense_boundary:001",
          "sense_boundary:002",
          "sense_boundary:003"
        ],
        "description": "語義番号を限定しない総括的なコアイメージが、記事の語義目録全体を不当に一般化していないことを確認する。"
      },
      {
        "id": "core_sense_mapping:001",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:002",
          "sense_boundary:001",
          "definition:001",
          "usage_note:001"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。"
      },
      {
        "id": "core_sense_mapping:002",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:003",
          "sense_boundary:002",
          "definition:002",
          "usage_note:002"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。"
      },
      {
        "id": "core_sense_mapping:003",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:004",
          "sense_boundary:003",
          "definition:003",
          "usage_note:003"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。"
      },
      {
        "id": "article_learning_risk:001",
        "kind": "article_learning_risk",
        "target_ids": [
          "core_image:001",
          "core_image:002",
          "core_image:003",
          "core_image:004",
          "sense_boundary:001",
          "definition:001",
          "usage_note:001",
          "sense_boundary:002",
          "definition:002",
          "usage_note:002",
          "sense_boundary:003",
          "definition:003",
          "usage_note:003"
        ],
        "description": "記事全体の語義構成、対比、訳語、限定表現から学習者が誤った一般化をしないことを横断確認する。"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "candidate_provisional_adjective",
        "surface_form": "tentative",
        "frame": "adjective: tentative plan/date/schedule/agreement/conclusion/explanation/identification; be tentative about details; tentatively agree, approve, or identify",
        "meaning": "not yet fixed or confirmed and liable to change",
        "disposition": "included",
        "rationale": "The frame adjective: tentative plan/date/schedule/agreement/conclusion/explanation/identification; be tentative about details; tentatively agree, approve, or identify consistently expresses the meaning not yet fixed or confirmed and liable to change, while the article distinguishes this status from mere short duration.",
        "semantic_assertions": [
          {
            "id": "assert_provisional_status",
            "statement": "The adjective must describe a plan, judgment, arrangement, or identification that is currently proposed or accepted provisionally and may still be changed or withdrawn.",
            "polarity": "must_hold",
            "scope": "provisional adjective uses"
          },
          {
            "id": "assert_not_short_duration",
            "statement": "The adjective must not be generalized to mean merely temporary or short-lived when the content is already settled.",
            "polarity": "must_not_hold",
            "scope": "provisional adjective uses"
          }
        ]
      },
      {
        "id": "candidate_hesitant_adjective",
        "surface_form": "tentative",
        "frame": "adjective: tentative smile/voice/answer/reply; take tentative steps; make a tentative attempt/gesture; sound, look, or seem tentative; tentatively ask, suggest, or reply",
        "meaning": "lacking confidence or certainty and expressed or performed cautiously",
        "disposition": "included",
        "rationale": "The frame adjective: tentative smile/voice/answer/reply; take tentative steps; make a tentative attempt/gesture; sound, look, or seem tentative; tentatively ask, suggest, or reply identifies the meaning lacking confidence or certainty and expressed or performed cautiously, including both interpersonal manner and cautious first action.",
        "semantic_assertions": [
          {
            "id": "assert_cautious_manner",
            "statement": "This adjective must characterize the manner or presentation of an action, voice, expression, or response as hesitant or not fully confident.",
            "polarity": "must_hold",
            "scope": "hesitant adjective uses"
          },
          {
            "id": "assert_not_silence",
            "statement": "This adjective must not be reduced to simply quiet, weak, or cautious because of external danger without an accompanying lack of confidence or hesitation.",
            "polarity": "must_not_hold",
            "scope": "hesitant adjective uses"
          }
        ]
      },
      {
        "id": "candidate_rare_noun",
        "surface_form": "tentative",
        "frame": "rare count noun: a tentative; tentatives; list, hold, or book dates as tentatives in business contexts",
        "meaning": "a provisional item or arrangement awaiting confirmation",
        "disposition": "included",
        "rationale": "The frame rare count noun: a tentative; tentatives; list, hold, or book dates as tentatives in business contexts supports the meaning a provisional item or arrangement awaiting confirmation and is explicitly limited to low-frequency practical usage rather than presented as a freely interchangeable everyday noun.",
        "semantic_assertions": [
          {
            "id": "assert_noun_provisional_item",
            "statement": "The noun must refer to a recorded or held provisional item, such as a date or booking, that awaits confirmation or contract completion.",
            "polarity": "must_hold",
            "scope": "rare noun use"
          },
          {
            "id": "assert_noun_restricted",
            "statement": "The noun must not be generalized as the ordinary noun counterpart for every adjective use of tentative.",
            "polarity": "must_not_hold",
            "scope": "rare noun use"
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "finding_example_sense_attribution_tentative_knock",
        "taxonomy_id": "example_sense_attribution_mismatch",
        "severity": "blocking",
        "location": {
          "section": "collocations_examples",
          "line_start": 173,
          "line_end": 173,
          "exact_quote": "例: There was a tentative knock on the office door.  "
        },
        "rationale": "段階1の最も自然な帰属はsense:003だが、実際の所属はsense:002である。",
        "suggested_direction": "語義ブロック間の移動"
      }
    ],
    "evidence_checks": [
      {
        "id": "EVID-001"
      },
      {
        "id": "EVID-002"
      },
      {
        "id": "EVID-003"
      },
      {
        "id": "EVID-004"
      },
      {
        "id": "EVID-005"
      },
      {
        "id": "EVID-006"
      },
      {
        "id": "EVID-007"
      },
      {
        "id": "EVID-008"
      }
    ],
    "source_inventory_results": [
      {
        "id": "U-001",
        "source_fact_ids": [
          "F-001",
          "F-007",
          "F-011"
        ],
        "canonical_statement": "The common adjective sense describes a plan, idea, result, or other content that is not settled and may change.",
        "disposition": "included",
        "rationale": "Three independent general dictionaries converge on the provisional or not-fully-developed sense used as sense 1."
      },
      {
        "id": "U-002",
        "source_fact_ids": [
          "F-002",
          "F-008",
          "F-012"
        ],
        "canonical_statement": "The adjective can describe a person, action, response, or manner that is hesitant, uncertain, or not confident.",
        "disposition": "included",
        "rationale": "Oxford, Cambridge, and Merriam-Webster independently provide the hesitation/uncertainty sense used as sense 2."
      },
      {
        "id": "U-003",
        "source_fact_ids": [
          "F-013"
        ],
        "canonical_statement": "Tentative has a rare noun use for something uncertain or subject to change, with plural tentatives.",
        "disposition": "integrated",
        "rationale": "The Merriam-Webster noun entry is retained as a clearly qualified, low-frequency sense rather than generalized to ordinary conversation."
      },
      {
        "id": "U-004",
        "source_fact_ids": [
          "F-003",
          "F-009"
        ],
        "canonical_statement": "The headword is pronounced /ˈtentətɪv/.",
        "disposition": "included",
        "rationale": "Oxford and Cambridge agree on the learner-facing pronunciation."
      },
      {
        "id": "U-005",
        "source_fact_ids": [
          "F-004",
          "F-017"
        ],
        "canonical_statement": "Tentative is connected historically with Medieval Latin tentativus and Latin tentare, with an older trial or testing notion.",
        "disposition": "included",
        "rationale": "Oxford and Etymonline provide convergent etymological support; the article states the relationship without claiming a direct modern derivation."
      },
      {
        "id": "U-006",
        "source_fact_ids": [
          "F-015",
          "F-018"
        ],
        "canonical_statement": "Tentatively is the adverb corresponding to provisional and hesitant uses of tentative.",
        "disposition": "integrated",
        "rationale": "Oxford's adverb entry and Etymonline's related-form record support the derived-word note."
      },
      {
        "id": "U-007",
        "source_fact_ids": [
          "F-016"
        ],
        "canonical_statement": "Tentativeness is a noun related to the quality of being tentative.",
        "disposition": "integrated",
        "rationale": "The derived form is included as a compact learner-facing word-formation note."
      },
      {
        "id": "U-008",
        "source_fact_ids": [
          "F-010"
        ],
        "canonical_statement": "The adjective is used with plans, ideas, suggestions, and actions, with the exact sense determined by whether the content is unsettled or the manner is hesitant.",
        "disposition": "integrated",
        "rationale": "The Cambridge learner entry supplies the frame inventory that the article organizes across senses 1 and 2."
      },
      {
        "id": "U-009",
        "source_fact_ids": [
          "F-014"
        ],
        "canonical_statement": "Merriam-Webster records separate first-known-use dates for the adjective and noun.",
        "disposition": "excluded",
        "rationale": "The dates are useful audit facts but are not needed for the learner-facing article and are not asserted in its text."
      }
    ]
  },
  "response_template": {
    "decision": null,
    "blockers": [],
    "notes": [],
    "target_results": [
      {
        "id": "pronunciation:001",
        "status": null,
        "target_id": "pronunciation:001"
      },
      {
        "id": "etymology:001",
        "status": null,
        "target_id": "etymology:001"
      },
      {
        "id": "word_formation:001",
        "status": null,
        "target_id": "word_formation:001"
      },
      {
        "id": "word_formation:002",
        "status": null,
        "target_id": "word_formation:002"
      },
      {
        "id": "word_formation:003",
        "status": null,
        "target_id": "word_formation:003"
      },
      {
        "id": "word_formation:004",
        "status": null,
        "target_id": "word_formation:004"
      },
      {
        "id": "core_image:001",
        "status": null,
        "target_id": "core_image:001"
      },
      {
        "id": "core_image:002",
        "status": null,
        "target_id": "core_image:002"
      },
      {
        "id": "core_image:003",
        "status": null,
        "target_id": "core_image:003"
      },
      {
        "id": "core_image:004",
        "status": null,
        "target_id": "core_image:004"
      },
      {
        "id": "sense_boundary:001",
        "status": null,
        "target_id": "sense_boundary:001"
      },
      {
        "id": "definition:001",
        "status": null,
        "target_id": "definition:001"
      },
      {
        "id": "frequency:001",
        "status": null,
        "target_id": "frequency:001"
      },
      {
        "id": "register:001",
        "status": null,
        "target_id": "register:001"
      },
      {
        "id": "grammar_pattern:001",
        "status": null,
        "target_id": "grammar_pattern:001"
      },
      {
        "id": "grammar_pattern:002",
        "status": null,
        "target_id": "grammar_pattern:002"
      },
      {
        "id": "grammar_pattern:003",
        "status": null,
        "target_id": "grammar_pattern:003"
      },
      {
        "id": "grammar_pattern:004",
        "status": null,
        "target_id": "grammar_pattern:004"
      },
      {
        "id": "grammar_pattern:005",
        "status": null,
        "target_id": "grammar_pattern:005"
      },
      {
        "id": "grammar_pattern:006",
        "status": null,
        "target_id": "grammar_pattern:006"
      },
      {
        "id": "grammar_pattern:007",
        "status": null,
        "target_id": "grammar_pattern:007"
      },
      {
        "id": "collocation:001",
        "status": null,
        "target_id": "collocation:001"
      },
      {
        "id": "collocation:002",
        "status": null,
        "target_id": "collocation:002"
      },
      {
        "id": "collocation:003",
        "status": null,
        "target_id": "collocation:003"
      },
      {
        "id": "collocation:004",
        "status": null,
        "target_id": "collocation:004"
      },
      {
        "id": "collocation:005",
        "status": null,
        "target_id": "collocation:005"
      },
      {
        "id": "collocation:006",
        "status": null,
        "target_id": "collocation:006"
      },
      {
        "id": "collocation:007",
        "status": null,
        "target_id": "collocation:007"
      },
      {
        "id": "collocation:008",
        "status": null,
        "target_id": "collocation:008"
      },
      {
        "id": "usage_note:001",
        "status": null,
        "target_id": "usage_note:001"
      },
      {
        "id": "synonym:001",
        "status": null,
        "target_id": "synonym:001"
      },
      {
        "id": "synonym:002",
        "status": null,
        "target_id": "synonym:002"
      },
      {
        "id": "synonym:003",
        "status": null,
        "target_id": "synonym:003"
      },
      {
        "id": "synonym:004",
        "status": null,
        "target_id": "synonym:004"
      },
      {
        "id": "antonym:001",
        "status": null,
        "target_id": "antonym:001"
      },
      {
        "id": "antonym:002",
        "status": null,
        "target_id": "antonym:002"
      },
      {
        "id": "antonym:003",
        "status": null,
        "target_id": "antonym:003"
      },
      {
        "id": "sense_boundary:002",
        "status": null,
        "target_id": "sense_boundary:002"
      },
      {
        "id": "definition:002",
        "status": null,
        "target_id": "definition:002"
      },
      {
        "id": "frequency:002",
        "status": null,
        "target_id": "frequency:002"
      },
      {
        "id": "register:002",
        "status": null,
        "target_id": "register:002"
      },
      {
        "id": "grammar_pattern:008",
        "status": null,
        "target_id": "grammar_pattern:008"
      },
      {
        "id": "grammar_pattern:009",
        "status": null,
        "target_id": "grammar_pattern:009"
      },
      {
        "id": "grammar_pattern:010",
        "status": null,
        "target_id": "grammar_pattern:010"
      },
      {
        "id": "grammar_pattern:011",
        "status": null,
        "target_id": "grammar_pattern:011"
      },
      {
        "id": "grammar_pattern:012",
        "status": null,
        "target_id": "grammar_pattern:012"
      },
      {
        "id": "grammar_pattern:013",
        "status": null,
        "target_id": "grammar_pattern:013"
      },
      {
        "id": "collocation:009",
        "status": null,
        "target_id": "collocation:009"
      },
      {
        "id": "collocation:010",
        "status": null,
        "target_id": "collocation:010"
      },
      {
        "id": "collocation:011",
        "status": null,
        "target_id": "collocation:011"
      },
      {
        "id": "collocation:012",
        "status": null,
        "target_id": "collocation:012"
      },
      {
        "id": "collocation:013",
        "status": null,
        "target_id": "collocation:013"
      },
      {
        "id": "collocation:014",
        "status": null,
        "target_id": "collocation:014"
      },
      {
        "id": "collocation:015",
        "status": null,
        "target_id": "collocation:015"
      },
      {
        "id": "collocation:016",
        "status": null,
        "target_id": "collocation:016"
      },
      {
        "id": "usage_note:002",
        "status": null,
        "target_id": "usage_note:002"
      },
      {
        "id": "synonym:005",
        "status": null,
        "target_id": "synonym:005"
      },
      {
        "id": "synonym:006",
        "status": null,
        "target_id": "synonym:006"
      },
      {
        "id": "synonym:007",
        "status": null,
        "target_id": "synonym:007"
      },
      {
        "id": "synonym:008",
        "status": null,
        "target_id": "synonym:008"
      },
      {
        "id": "antonym:004",
        "status": null,
        "target_id": "antonym:004"
      },
      {
        "id": "antonym:005",
        "status": null,
        "target_id": "antonym:005"
      },
      {
        "id": "antonym:006",
        "status": null,
        "target_id": "antonym:006"
      },
      {
        "id": "sense_boundary:003",
        "status": null,
        "target_id": "sense_boundary:003"
      },
      {
        "id": "definition:003",
        "status": null,
        "target_id": "definition:003"
      },
      {
        "id": "frequency:003",
        "status": null,
        "target_id": "frequency:003"
      },
      {
        "id": "register:003",
        "status": null,
        "target_id": "register:003"
      },
      {
        "id": "grammar_pattern:014",
        "status": null,
        "target_id": "grammar_pattern:014"
      },
      {
        "id": "grammar_pattern:015",
        "status": null,
        "target_id": "grammar_pattern:015"
      },
      {
        "id": "grammar_pattern:016",
        "status": null,
        "target_id": "grammar_pattern:016"
      },
      {
        "id": "collocation:017",
        "status": null,
        "target_id": "collocation:017"
      },
      {
        "id": "collocation:018",
        "status": null,
        "target_id": "collocation:018"
      },
      {
        "id": "usage_note:003",
        "status": null,
        "target_id": "usage_note:003"
      },
      {
        "id": "synonym:009",
        "status": null,
        "target_id": "synonym:009"
      },
      {
        "id": "synonym:010",
        "status": null,
        "target_id": "synonym:010"
      }
    ],
    "relation_results": [
      {
        "id": "risk_sense_pair:001",
        "status": null,
        "relation_id": "risk_sense_pair:001"
      },
      {
        "id": "example_translation:001",
        "status": null,
        "relation_id": "example_translation:001"
      },
      {
        "id": "example_translation:002",
        "status": null,
        "relation_id": "example_translation:002"
      },
      {
        "id": "example_translation:003",
        "status": null,
        "relation_id": "example_translation:003"
      },
      {
        "id": "example_translation:004",
        "status": null,
        "relation_id": "example_translation:004"
      },
      {
        "id": "example_translation:005",
        "status": null,
        "relation_id": "example_translation:005"
      },
      {
        "id": "example_translation:006",
        "status": null,
        "relation_id": "example_translation:006"
      },
      {
        "id": "example_translation:007",
        "status": null,
        "relation_id": "example_translation:007"
      },
      {
        "id": "example_translation:008",
        "status": null,
        "relation_id": "example_translation:008"
      },
      {
        "id": "example_translation:009",
        "status": null,
        "relation_id": "example_translation:009"
      },
      {
        "id": "example_translation:010",
        "status": null,
        "relation_id": "example_translation:010"
      },
      {
        "id": "example_translation:011",
        "status": null,
        "relation_id": "example_translation:011"
      },
      {
        "id": "example_translation:012",
        "status": null,
        "relation_id": "example_translation:012"
      },
      {
        "id": "example_translation:013",
        "status": null,
        "relation_id": "example_translation:013"
      },
      {
        "id": "example_translation:014",
        "status": null,
        "relation_id": "example_translation:014"
      },
      {
        "id": "example_translation:015",
        "status": null,
        "relation_id": "example_translation:015"
      },
      {
        "id": "example_translation:016",
        "status": null,
        "relation_id": "example_translation:016"
      },
      {
        "id": "example_translation:017",
        "status": null,
        "relation_id": "example_translation:017"
      },
      {
        "id": "example_translation:018",
        "status": null,
        "relation_id": "example_translation:018"
      },
      {
        "id": "sense_definition_consistency:001",
        "status": null,
        "relation_id": "sense_definition_consistency:001"
      },
      {
        "id": "definition_usage_consistency:001",
        "status": null,
        "relation_id": "definition_usage_consistency:001"
      },
      {
        "id": "definition_lexical_relation_consistency:001",
        "status": null,
        "relation_id": "definition_lexical_relation_consistency:001"
      },
      {
        "id": "pattern_example_coverage:001",
        "status": null,
        "relation_id": "pattern_example_coverage:001"
      },
      {
        "id": "pattern_example_coverage:002",
        "status": null,
        "relation_id": "pattern_example_coverage:002"
      },
      {
        "id": "pattern_example_coverage:003",
        "status": null,
        "relation_id": "pattern_example_coverage:003"
      },
      {
        "id": "pattern_example_coverage:004",
        "status": null,
        "relation_id": "pattern_example_coverage:004"
      },
      {
        "id": "pattern_example_coverage:005",
        "status": null,
        "relation_id": "pattern_example_coverage:005"
      },
      {
        "id": "pattern_example_coverage:006",
        "status": null,
        "relation_id": "pattern_example_coverage:006"
      },
      {
        "id": "pattern_example_coverage:007",
        "status": null,
        "relation_id": "pattern_example_coverage:007"
      },
      {
        "id": "sense_definition_consistency:002",
        "status": null,
        "relation_id": "sense_definition_consistency:002"
      },
      {
        "id": "definition_usage_consistency:002",
        "status": null,
        "relation_id": "definition_usage_consistency:002"
      },
      {
        "id": "definition_lexical_relation_consistency:002",
        "status": null,
        "relation_id": "definition_lexical_relation_consistency:002"
      },
      {
        "id": "pattern_example_coverage:008",
        "status": null,
        "relation_id": "pattern_example_coverage:008"
      },
      {
        "id": "pattern_example_coverage:009",
        "status": null,
        "relation_id": "pattern_example_coverage:009"
      },
      {
        "id": "pattern_example_coverage:010",
        "status": null,
        "relation_id": "pattern_example_coverage:010"
      },
      {
        "id": "pattern_example_coverage:011",
        "status": null,
        "relation_id": "pattern_example_coverage:011"
      },
      {
        "id": "pattern_example_coverage:012",
        "status": null,
        "relation_id": "pattern_example_coverage:012"
      },
      {
        "id": "pattern_example_coverage:013",
        "status": null,
        "relation_id": "pattern_example_coverage:013"
      },
      {
        "id": "sense_definition_consistency:003",
        "status": null,
        "relation_id": "sense_definition_consistency:003"
      },
      {
        "id": "definition_usage_consistency:003",
        "status": null,
        "relation_id": "definition_usage_consistency:003"
      },
      {
        "id": "definition_lexical_relation_consistency:003",
        "status": null,
        "relation_id": "definition_lexical_relation_consistency:003"
      },
      {
        "id": "pattern_example_coverage:014",
        "status": null,
        "relation_id": "pattern_example_coverage:014"
      },
      {
        "id": "pattern_example_coverage:015",
        "status": null,
        "relation_id": "pattern_example_coverage:015"
      },
      {
        "id": "pattern_example_coverage:016",
        "status": null,
        "relation_id": "pattern_example_coverage:016"
      },
      {
        "id": "core_inventory_consistency:001",
        "status": null,
        "relation_id": "core_inventory_consistency:001"
      },
      {
        "id": "core_sense_mapping:001",
        "status": null,
        "relation_id": "core_sense_mapping:001"
      },
      {
        "id": "core_sense_mapping:002",
        "status": null,
        "relation_id": "core_sense_mapping:002"
      },
      {
        "id": "core_sense_mapping:003",
        "status": null,
        "relation_id": "core_sense_mapping:003"
      },
      {
        "id": "article_learning_risk:001",
        "status": null,
        "relation_id": "article_learning_risk:001"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "candidate_provisional_adjective",
        "status": null,
        "assertion_ids": [
          "assert_provisional_status",
          "assert_not_short_duration"
        ],
        "verified_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
      },
      {
        "id": "candidate_hesitant_adjective",
        "status": null,
        "assertion_ids": [
          "assert_cautious_manner",
          "assert_not_silence"
        ],
        "verified_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
      },
      {
        "id": "candidate_rare_noun",
        "status": null,
        "assertion_ids": [
          "assert_noun_provisional_item",
          "assert_noun_restricted"
        ],
        "verified_body_sha256": "0776dad38e204651edaf002adb4634b2bdf5ffb371b9d38c3ab1f33440a3c35f"
      }
    ],
    "finding_results": [
      {
        "id": "finding_example_sense_attribution_tentative_knock",
        "status": null,
        "notes": ""
      }
    ],
    "evidence_checks": [
      {
        "id": "EVID-001",
        "status": null
      },
      {
        "id": "EVID-002",
        "status": null
      },
      {
        "id": "EVID-003",
        "status": null
      },
      {
        "id": "EVID-004",
        "status": null
      },
      {
        "id": "EVID-005",
        "status": null
      },
      {
        "id": "EVID-006",
        "status": null
      },
      {
        "id": "EVID-007",
        "status": null
      },
      {
        "id": "EVID-008",
        "status": null
      }
    ],
    "source_inventory_results": [
      {
        "id": "U-001",
        "status": null,
        "union_id": "U-001"
      },
      {
        "id": "U-002",
        "status": null,
        "union_id": "U-002"
      },
      {
        "id": "U-003",
        "status": null,
        "union_id": "U-003"
      },
      {
        "id": "U-004",
        "status": null,
        "union_id": "U-004"
      },
      {
        "id": "U-005",
        "status": null,
        "union_id": "U-005"
      },
      {
        "id": "U-006",
        "status": null,
        "union_id": "U-006"
      },
      {
        "id": "U-007",
        "status": null,
        "union_id": "U-007"
      },
      {
        "id": "U-008",
        "status": null,
        "union_id": "U-008"
      },
      {
        "id": "U-009",
        "status": null,
        "union_id": "U-009"
      }
    ],
    "input_revision_id": "9fc50b17c025edfc6d87c2b255bc5749359eac4e7188d78c353d3b990439dc62"
  },
  "input_bindings": {
    "pass_findings.json": "122347cb1521bfc0e8667b4d551a416fcb13298bbb2995153617db7b3849d3d9",
    "cold_review.json": "e47bebca999a79f8cc8fc777ee6af541e89059a99b9d02d0d5d1b233c870ade7",
    "final_blind.json": "1570cec673e640a8658f10b544ebc3b20d622a74f57ced594549a9f7be7d156b",
    "blind_seal.json": "3c163330797c2e2b323897b51af55026e30a3a5db976a77be67ddabe3627865c",
    "pre_blind_resolution.json": "20555f671e7fe03548174f5b9c96282fa9fdc0b309ec9ca61f8d65765d0f223c",
    "pre_blind_revision.json": "ed6a129302c610501b4c8a392963f76f109875b22969f170aa66e8727ff643bc",
    "checker_recheck_manifest.json": "7d092c8d5cde7cd5c9adbe41bcd2f01dfcd4e880693e72e197c9bbdad3365e9f",
    "post_blind_resolution.json": "922ff2eb415b8dc0a1639276dc40702f8ae18f58857e66f2b446af9bc06e74cb",
    "post_blind_verification.json": "2c559c8b926ce2f6f621feef887602f14dbf763546733fc4f4e94d365f65ffa0",
    "targeted_adjudications.json": "af5af9b139e61078d584a712c70a3ce285f0407cc7fa63836b8195db9ea9f3b6",
    "source_inventory.json": "e2a268a99569d1c41d9891149792af0e7909cabb89d37849a3090646eb221902",
    "resolutions.json": "60cf3b7a4be948421acf6e8e38f1d9901355445e8ce77033f459ff69a63ab70a",
    "check_passes/checker_passes.stage1.json": "2659f9791076a50c85f5717fee78707685c3852f28d2ec2059be0bb606c333ef",
    "check_passes/evidence.json": "1c279365858ac42db25a949eb65168524b2557d104fc2a14744100630872f191",
    "check_passes/evidence.request.json": "46101fcc356a53b094e604325123379a63ba17bb03b7ffd4a0ff323a931a5a74",
    "check_passes/example-attribution.alignment-key.json": "a8c22b8e8c2ea44f597718f6ce552348f6c1969484546a7a9e1e4d918fa5be58",
    "check_passes/example-attribution.blind-record.json": "6491edc6dbeee2e992598b9589d62ae7e7d9f313e184585d69b6c06ba01216bb",
    "check_passes/example-attribution.json": "b5776e96a6b79c436f25e4cb5d7a97b6c28287e70fe986a18d672c530f2dd928",
    "check_passes/example-attribution.request.json": "58da3d83e7b1f28b9a6cad7b6ab0fbd34e6bb4f6c3c9457c8cba56ce967709aa",
    "check_passes/frame-relation.antonym-axis.adjudication-record.json": "86c5c4191a9bf563be0bbb24532c61d2602a756cd3607508762b779b972734b9",
    "check_passes/frame-relation.antonym-axis.alignment-key.json": "9dd133a52e0c4a1b1ccc3f77e7c29da568a83b72cb98ece54f4ab8c0e1c99fbb",
    "check_passes/frame-relation.antonym-axis.blind-record.json": "10f6b58822bb970645ce4ae20d1480f178804340731633a73a818733782844e2",
    "check_passes/frame-relation.antonym-axis.stage2.request.json": "eef58de620e26ce8db233d18d8bb185c047f819847f2b714b49b278a2678553a",
    "check_passes/frame-relation.request.json": "97b038df6e9fa9c803a3877f5a9fe4f188468c7867b08dd646275905b57e1e4a",
    "check_passes/input_snapshot.json": "e5067be8fd9e5e93286eaf107abbf87a270b450ac555a36d23a1cf790114ee0b",
    "check_passes/pronunciation.json": "3db2db8e7d19fd5d586a7c7efb8c0fc5677f3d95f1a8dbe2a13172f4bfc07d45",
    "check_passes/pronunciation.request.json": "982c9de3f93f8d6fc69d4eddde81d2a9a56a55edde07eda329ba96bbec999842",
    "check_passes/qualification.json": "d6e72030a1e79588861ae7b3c992a1f7033a95f3015ff7988ce3170080e56258",
    "check_passes/qualification.request.json": "75f16da8a7b68b6908a70509b83d27fe89a2b903f1d5c93605679a11401bfb7d",
    "check_passes/sense-structure.json": "588a0b1b04fb13b7ef64c8b280fba0d461d6b9da025063ccb9eea797a34f3150",
    "check_passes/sense-structure.request.json": "e7779904c25953297e28dd677dbfeef15afb90974a6dc200b763806b6b813aa9",
    "check_passes/translation.json": "9b06429d6d3e749fcefa0d847a2f34e697aa1d5d00531ecab4e11ff88f716e6e",
    "check_passes/translation.request.json": "63a92633ce11f5ae0b3f4dfd86bd3efb2ca6ff3d64f8265aa784db97d4d3005d"
  },
  "contract_version": "review_preflight_v1",
  "input_revision_id": "9fc50b17c025edfc6d87c2b255bc5749359eac4e7188d78c353d3b990439dc62"
}
```
