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
  "entry_body": "\n＃発音記号\n\n米: /ˈdefənət/｜英: /ˈdefɪnət/。3音節で、第1音節に主強勢がある。米語では第2音節の母音を弱い /ə/、英語では /ɪ/ と示すことが多い。語末は /nət/ で、綴りの -ite を /eɪt/ と読まない。definitely は米 /ˈdefənətli/・英 /ˈdefɪnətli/ のように発音し、語尾の -ly が加わる。  \n\n＃語源\n\ndefinite は16世紀初頭の英語で「固定された、確かな」の意味で使われ、ラテン語 dēfīnītus「境界を定められた、限定された、確定した」から来た。これは dēfīnīre「限界を定める、決定する、説明する」の過去分詞で、de-「完全に」と finis「境界、終わり」に分けて考えられる。18世紀初頭には文法用語として「限定する」の意味でも使われた。define、finite、definition、definitive、indefinite は同じ語源の語族に属する。  \n\n＃語形成\n\n・definitely：副詞。「確実に、間違いなく、はっきりと」。話者の確信を表す文副詞としても、動詞・形容詞を強める副詞としても使う。  \n・definiteness：名詞。「明確さ、確定性、定性」。文法では名詞句の指示対象が特定可能である性質を表す。  \n・indefinite：接頭辞 in-「否定」を伴う関連形。「不確定な、漠然とした、定のない」。definite の単純な反意語になる用法と、文法用語としての用法がある。  \n・definitive：同じラテン語幹系統の形容詞。「決定的な、最終的な」。definite よりも最終判断・決着の含みが強く、単なる語尾違いとして置き換えない。  \n・define / definition：同じ語源にさかのぼる動詞・名詞。「境界を定める」「定義」。definite の直接の活用形ではないが、「曖昧さを境界づける」という意味のつながりがある。  \n\n＃コアイメージ\n\ndefinite の共通核は、「境界・同一性・判断を曖昧さから切り出し、はっきり固定する」ことである。何を固定するかによって、決定、観察上の明瞭さ、範囲や内容の限定、文法上の指示対象、植物の数や成長の上限へ広がる。  \n・判断や予定を曖昧さから切り出して固定する → 「確定した、決まった」（語義1）  \n・特徴や変化を観察上はっきり切り出す → 「明らかな、はっきりした」（語義2）  \n・範囲や内容を境界づけて固定する → 「具体的な、特定の」（語義3）  \n・指示対象を文脈上特定可能なものとして切り出す → 「定の、特定できる」（語義4）  \n・数や成長の上限を固定する → 「有限の、定数の」（語義5）  \n  \n＃意味・用法・関連表現\n\n1. 【形容詞・限定用法／叙述用法】確定した、決まった\n\n【日本語訳・定義】答え、決定、計画、日付、合意、意図などが、曖昧な候補や一時的な案ではなく、内容として定まり、変更される可能性が低いことを表す。必ずしも今後絶対に変更できないという意味ではなく、現時点で決定・約束・判断が明確になっていることに焦点がある。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準語で、会話・ビジネス・報道・公式文書まで広く使う。計画や合意の確定性を述べるときに多く、日常会話では sure が話者の確信、definite が決定や内容の確定を表しやすい。ここでの頻度の数値はこの辞書内の学習上の相対目安で、10は日常・一般文書で頻出、1は限定的な専門用法を表す。特定領域内のコーパス頻度や厳密な語義間順位ではない。  \n\n【文法パターン】a definite answer/decision/plan/date/deadline＝確定した答え・決定・計画・日付・期限／a definite agreement/offer/commitment＝明確に成立した合意・正式な申し出・確約／have no definite plans/ideas＝決まった計画・具体的な考えがない／anything definite＝何か確定したこと・情報／nothing definite＝何も確定したことはない／be definite about something＝ある事柄について態度・内容を明確にする／a definite yes/no＝はっきりした賛成／拒否。  \n\n【コロケーション】\n\n・a definite answer  \n用途: 予想や曖昧な返事ではなく、決定した答えを求める。  \n例: We need a definite answer by Friday, not another tentative suggestion.  \n訳: 私たちは金曜日までに、また別の仮案ではなく確定した答えを必要としている。  \n\n・a definite date for 〈event〉  \n用途: 行事・開始・発売などの日付が決まっていることを表す。  \n例: The organizers have not announced a definite date for the launch.  \n訳: 主催者は発売の確定した日付をまだ発表していない。  \n\n・no definite plans  \n用途: 将来の予定がまだ決まっていないことを表す。  \n例: I have no definite plans for the weekend yet.  \n訳: 私は週末の具体的な予定をまだ決めていない。  \n\n・anything definite about something  \n用途: ある事柄について確定した情報があるかを尋ねる。  \n例: Do you know anything definite about when the train will leave?  \n訳: 列車がいつ出るかについて、何か確定した情報を知っていますか。  \n\n・a definite yes/no  \n用途: ためらいや条件付きではない、明確な肯定・拒否を表す。  \n例: Her reply was a definite no, so we stopped asking.  \n訳: 彼女の返事は明確な拒否だったので、私たちは尋ねるのをやめた。  \n\n・be definite about 〈decision/position〉  \n用途: 決定や立場を曖昧にせず、はっきり示す。  \n例: Please be definite about your position before the meeting begins.  \n訳: 会議が始まる前に、自分の立場を明確にしてください。  \n\n・a definite commitment to do  \n用途: ある行動を実行するという明確な確約を表す。  \n例: The grant requires a definite commitment to complete the project.  \n訳: その助成金には、プロジェクトを完了するという明確な確約が必要だ。  \n\n・a definite agreement  \n用途: 条件や内容が定まり、当事者間で成立した合意を表す。  \n例: No definite agreement had been reached by the end of the meeting.  \n訳: 会議の終了時までに、確定した合意は成立していなかった。  \n\n【語法・注意】certain は「真実だと確信している」「起こる可能性が高い」という話者の認識にも使えるが、definite は答え・計画・日付などの内容が決まっていることを強調しやすい。final は「それ以上変更しない最終段階」、firm は意思・態度の強さに焦点があるため、definite と完全には交換できない。`I have no definite plans.` は「将来の予定が一切ない」ではなく「決まった予定はない」という意味である。definite と definitely、definite と definitive を品詞や意味を考えずに置き換えない。綴りは definite であり、definate ではない。  \n\n【類義語】\n\n・certain  \n定義: 疑いがなく、確かだと判断される。  \n頻度: 〈10/10〉  \n違い: certain は事実・未来・話者の確信を広く表す。definite は答えや予定が決定済みで曖昧でないことを表しやすい。  \n例: I am certain that she will accept the offer.  \n訳: 彼女がその申し出を受けると私は確信している。  \n\n・settled  \n定義: 議論や検討の後に、決定・合意されている。  \n頻度: 〈8/10〉  \n違い: settled は未決の状態が終わったことに焦点があり、definite は決まった内容が明確であることに焦点がある。  \n例: The venue for the conference is now settled.  \n訳: 会議の会場は今や決まっている。  \n\n・firm  \n定義: 意思・約束・態度が強く、簡単には変わらない。  \n頻度: 〈9/10〉  \n違い: firm は人の決意や約束の強さを示し、definite は決定内容や情報の確定性を示す。  \n例: She made a firm promise to return the money.  \n訳: 彼女はそのお金を返すと固く約束した。  \n\n・fixed  \n定義: 位置・日時・数量などが変更されないように定められている。  \n頻度: 〈10/10〉  \n違い: fixed は変更不能・変更予定なしという状態を強く示し、definite は曖昧さが解消されていることを広く示す。  \n例: The shop has fixed opening hours.  \n訳: その店には固定された営業時間がある。  \n\n【反意語】\n\n・uncertain  \n定義: 確実でなく、結果や内容がまだ分からない。  \n頻度: 〈9/10〉  \n違い: uncertain は確定性の反対で、definite が決定・情報の明確さを示すのに対し、見通しや判断が定まらない。  \n例: The outcome remains uncertain.  \n訳: 結果は依然として不確かだ。  \n\n・tentative  \n定義: 仮のもので、後で変更される可能性がある。  \n頻度: 〈8/10〉  \n違い: tentative は計画・合意などが試案段階であることを示し、definite はそこから確定した段階を示す。  \n例: We made a tentative booking for next month.  \n訳: 私たちは来月について仮予約をした。  \n\n・undecided  \n定義: 選択・判断・決定がまだ行われていない。  \n頻度: 〈8/10〉  \n違い: undecided は決める主体や問題が未決定であること、definite は答えや立場が決まっていることを表す。  \n例: The committee is still undecided about the proposal.  \n訳: 委員会はその提案についてまだ決めていない。  \n\n・indefinite  \n定義: 明確な範囲・期間・内容が定まっていない。  \n頻度: 〈7/10〉  \n違い: indefinite は期間・数量・指示対象などの境界が不明確であることを表し、definite は境界が定まっていることを表す。  \n例: The project was postponed for an indefinite period.  \n訳: そのプロジェクトは無期限に延期された。  \n\n2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした\n\n【日本語訳・定義】変化、差、効果、兆候、利点などが、観察や比較によって実際に認められるほど明瞭・顕著であることを表す。必ずしも論理的に証明済み、絶対に疑いがないという意味ではなく、話し手が変化や特徴をはっきり認識しているという評価を含むことがある。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】標準語で、会話・報道・評価・ビジネス文書まで使える。clear や obvious よりやや説明的・形式的で、improvement、difference、effect、sign など、観察できる変化や結果を修飾することが多い。  \n\n【文法パターン】a definite improvement/change/difference＝明らかな改善・変化・違い／a definite sign/indication of something＝～の明らかな兆候・指標／have a definite effect/impact on something＝ある物事に明確な効果・影響を及ぼす／a definite advantage/disadvantage＝明確な利点・不利／a definite possibility＝現実味のある可能性／see/feel a definite difference＝はっきり違いを感じる。  \n\n【コロケーション】\n\n・a definite improvement  \n用途: 状態や成績が実際に良くなったと認められることを表す。  \n例: The new treatment produced a definite improvement in her symptoms.  \n訳: 新しい治療によって、彼女の症状には明らかな改善が見られた。  \n\n・a definite difference between 〈A〉 and 〈B〉  \n用途: 二つの対象の違いがはっきり認められることを表す。  \n例: There is a definite difference between the two versions of the report.  \n訳: その報告書の二つの版には明らかな違いがある。  \n\n・a definite sign of something  \n用途: ある状態や出来事を示す、見分けやすい兆候を表す。  \n例: A sudden drop in demand is a definite sign of weakening consumer confidence.  \n訳: 需要の急減は、消費者信頼感が弱まっている明らかな兆候だ。  \n\n・have a definite effect on something  \n用途: 行為・条件・政策などが、結果に明確な影響を与えることを表す。  \n例: Sleep has a definite effect on how well people remember new information.  \n訳: 睡眠は、人が新しい情報をどれだけよく覚えるかに明確な影響を及ぼす。  \n\n・a definite advantage  \n用途: 他と比べて認めやすい具体的な利点を強調する。  \n例: The shorter route offers a definite advantage during the winter.  \n訳: その短い経路は冬の間、明確な利点をもたらす。  \n\n・a definite possibility  \n用途: 単なる空想ではなく、現実に起こり得る可能性を表す。  \n例: A delay is a definite possibility if the storm continues.  \n訳: 嵐が続けば、遅延は十分に現実的な可能性だ。  \n\n・see a definite change in something  \n用途: 状態や傾向の変化を観察してはっきり認める。  \n例: We can see a definite change in customer behavior after the price increase.  \n訳: 値上げ後、顧客の行動に明らかな変化が見られる。  \n\n・with a definite sense of 〈emotion〉  \n用途: 特定の感情を明確に抱いていることを表す。  \n例: He left the room with a definite sense of relief.  \n訳: 彼は明確な安堵感を抱いて部屋を出た。  \n\n【語法・注意】この用法の definite は「証明された」と同義ではない。`a definite improvement` は改善がはっきり認められるという意味で、科学的な因果関係が完全に証明されたという意味ではない。`a definite possibility` は「確実に起こること」ではなく「現実味のある可能性」である。obvious は文脈や話者にとって明白と評価されること、clear は混乱や曖昧さがないこと、noticeable は知覚上目立つことを強調し、definite は変化・差・効果などを明確なものとして認めることに焦点がある。  \n\n【類義語】\n\n・clear  \n定義: 意味・事実・視界などに混乱や曖昧さがない。  \n頻度: 〈10/10〉  \n違い: clear は理解可能性や障害のなさを広く表す。definite は変化・差・効果などが明確に認められることを強調しやすい。  \n例: The instructions are clear and easy to follow.  \n訳: その指示は明確で、従いやすい。  \n\n・obvious  \n定義: 見たり考えたりすれば、すぐに分かる。  \n頻度: 〈10/10〉  \n違い: obvious は認識の容易さを強く示す。definite は明らかさを示すが、必ずしも誰にとっても自明とは限らない。  \n例: It was obvious that the machine had stopped working.  \n訳: その機械が動かなくなったことは明らかだった。  \n\n・noticeable  \n定義: 見たり感じたりして気づくことができる。  \n頻度: 〈8/10〉  \n違い: noticeable は知覚上の目立ちやすさに焦点がある。definite は目立つだけでなく、差や効果を明確なものとして評価する。  \n例: There was a noticeable drop in temperature overnight.  \n訳: 一晩で気温が目に見えて下がった。  \n\n・distinct  \n定義: ほかのものと区別できるほど特徴がはっきりしている。  \n頻度: 〈9/10〉  \n違い: distinct は境界や識別可能性を強調する。definite は結果・変化・効果が明確に認められることにも使う。  \n例: The two methods produce distinct results.  \n訳: その二つの方法は明確に異なる結果を生む。  \n\n・marked  \n定義: 程度や差が目立つほど顕著である。  \n頻度: 〈7/10〉  \n違い: marked は変化・差・改善の大きさを強く示し、definite はそこまで大きくなくても、存在が明確であることを表せる。  \n例: The report shows a marked reduction in waste.  \n訳: その報告書は廃棄物の顕著な削減を示している。  \n\n【反意語】\n\n・unclear  \n定義: 意味・原因・結果などがはっきりしない。  \n頻度: 〈9/10〉  \n違い: unclear は理解や判断の明瞭さの反対で、definite は観察・評価の対象が明らかであることを示す。  \n例: The cause of the failure is still unclear.  \n訳: 故障の原因はまだはっきりしない。  \n\n・indistinct  \n定義: 輪郭・音・違いなどがぼんやりして区別しにくい。  \n頻度: 〈6/10〉  \n違い: indistinct は知覚上の境界が弱いことを表し、definite は特徴や差が明瞭に取り出せることを表す。  \n例: The distant hills were indistinct in the fog.  \n訳: 遠くの丘は霧の中でぼんやりしていた。  \n\n・imperceptible  \n定義: 感覚や観察ではほとんど気づけない。  \n頻度: 〈5/10〉  \n違い: imperceptible は変化や差が知覚できないほど小さいことを示し、definite は明確に認められることを示す。  \n例: The change in pressure was almost imperceptible.  \n訳: 圧力の変化はほとんど知覚できなかった。  \n\n3. 【形容詞・限定用法】具体的な、特定の\n\n【日本語訳・定義】数量、期間、範囲、時点、形、情報などに明確な境界や内容があり、漠然としたものではないことを表す。特定の対象を指す場合でも、文脈上その対象を識別できるという文法上の意味とは異なり、ここでは内容・範囲・条件が具体的に定まっていることに焦点がある。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】標準語。契約・行政・学術・技術文書では形式的な用法が現れ、数学では `definite integral` などの専門連語で使われる。specific は選び出された個別性、exact は数値や内容の厳密な一致、definite は範囲や条件が定まっていることを強調しやすい。  \n\n【文法パターン】a definite amount/number/quantity/period＝具体的な量・数・期間／at a definite time/stage＝特定の時点・段階で／within definite limits＝明確な範囲内で／definite information/details＝具体的な情報・詳細／a definite shape/form＝はっきり定まった形・形式／a definite integral＝定積分。  \n  \n【コロケーション】\n\n・a definite amount of 〈money/material〉  \n用途: 金額や物質の量が一定の範囲・数量として定まっていることを表す。  \n例: The machine requires a definite amount of oil to operate safely.  \n訳: その機械を安全に稼働させるには、一定量の油が必要だ。  \n\n・a definite number of 〈people/items〉  \n用途: 人数や個数が曖昧でなく、決まった数であることを表す。  \n例: Only a definite number of students can join the laboratory tour.  \n訳: 研究室見学には決まった人数の学生だけが参加できる。  \n\n・for a definite period  \n用途: 期間の終点または長さがあらかじめ定められていることを表す。  \n例: The equipment may be rented for a definite period of six months.  \n訳: その設備は6か月という定められた期間、借りることができる。  \n\n・within definite limits  \n用途: 許容範囲や境界を明確に限定する。  \n例: The temperature must remain within definite limits during transport.  \n訳: 輸送中、温度は明確に定められた範囲内に保たなければならない。  \n\n・definite information about 〈topic〉  \n用途: 内容が具体的で明確な情報を表し、文脈によっては確かな情報を含意する。  \n例: We need definite information about the delivery schedule before placing the order.  \n訳: 注文を出す前に、納入予定について具体的な情報が必要だ。  \n\n・a definite shape/form  \n用途: 輪郭や形式が一定で、別の形と区別できることを表す。  \n例: The crystals grow into a definite shape under controlled conditions.  \n訳: その結晶は、管理された条件下で一定の形に成長する。  \n\n・a definite integral  \n用途: 数学で、積分区間の上下端が指定された定積分を指す。  \n例: The area under the curve can be calculated with a definite integral.  \n訳: 曲線の下の面積は定積分で計算できる。  \n\n【語法・注意】`a definite amount` は「量が決まっている」ことを示すが、必ずしも聞き手がその数値を知っているとは限らない。`specific` は「その特定のもの」という選択に、`exact` は誤差のない数値・内容に焦点がある。`definite information` は具体的で明確な情報（文脈によっては確かな情報）、`definite plans` は決定済みの予定というように、名詞によって「具体的」と「確定した」のどちらが前面に出るかが変わる。`definite integral` は「確実な積分」ではなく、積分区間が定まった数学用語である。  \n\n【類義語】\n\n・specific  \n定義: ほかのものではなく、特定の対象・内容に関する。  \n頻度: 〈10/10〉  \n違い: specific は個別の対象を選び出すことを強調し、definite は数量・範囲・条件などが明確に定まっていることを強調する。  \n例: Please give me a specific example.  \n訳: 具体的な例を一つ挙げてください。  \n\n・precise  \n定義: 細部や数値が正確で、曖昧さがない。  \n頻度: 〈9/10〉  \n違い: precise は細かい正確さを要求する。definite は必ずしも数値の厳密さを求めず、境界や内容が決まっていることを示す。  \n例: The report provides precise measurements.  \n訳: その報告書は正確な測定値を示している。  \n\n・specified  \n定義: 条件・文書・規則などで明示的に指定されている。  \n頻度: 〈8/10〉  \n違い: specified は誰かが明示して指定したことに焦点があり、definite は指定の有無にかかわらず内容が定まっていることを表せる。  \n例: The work must be completed within the specified time.  \n訳: 作業は指定された時間内に完了しなければならない。  \n\n・determinate  \n定義: 限界・終点・結果が決まっている。  \n頻度: 〈5/10〉  \n違い: determinate は形式的・専門的で、数学・科学・哲学などで境界や結果の決定性を述べる。definite は一般語としてより広く使う。  \n例: The process has a determinate end point.  \n訳: その過程には明確に定まった終点がある。  \n\n・fixed  \n定義: 位置・数量・時期などが動かないように定められている。  \n頻度: 〈10/10〉  \n違い: fixed は変更されない状態を強く示し、definite は具体的に境界づけられた情報や範囲にも使う。  \n例: The fee is fixed for the entire contract period.  \n訳: 料金は契約期間全体を通じて固定されている。  \n\n【反意語】\n\n・indefinite  \n定義: 範囲・期間・数量・内容などが決まっていない。  \n頻度: 〈7/10〉  \n違い: indefinite は定まった境界がないことを直接表し、definite は範囲や条件が具体化されていることを表す。  \n例: The meeting was postponed for an indefinite period.  \n訳: 会議は無期限に延期された。  \n\n・unspecified  \n定義: 必要な内容や条件が明示されていない。  \n頻度: 〈7/10〉  \n違い: unspecified は情報が指定されていないことに焦点があり、definite は情報の境界や内容が明らかであることを表す。  \n例: The shipment was delayed for unspecified reasons.  \n訳: その発送は理由が明示されないまま遅れた。  \n\n・vague  \n定義: 表現・考え・範囲などがぼんやりして具体性に欠ける。  \n頻度: 〈9/10〉  \n違い: vague は内容の輪郭が弱いことを表し、definite は内容を具体的に切り出せることを表す。  \n例: His answer was too vague to be useful.  \n訳: 彼の答えは曖昧すぎて役に立たなかった。  \n\n・unlimited  \n定義: 数量・範囲・期間などに上限がない。  \n頻度: 〈8/10〉  \n違い: unlimited は上限の不存在を示し、definite は上限や範囲が定められていることを示す。ただし、definite が必ず有限量を意味するわけではない。  \n例: The plan offers unlimited data usage.  \n訳: そのプランはデータ通信を無制限で提供する。  \n  \n4. 【形容詞・文法用語】定の、特定できる\n\n【日本語訳・定義】文法で、名詞句の指示対象が、既出、状況上の唯一性、修飾語、共有知識などによって聞き手・読み手に特定可能であることを表す。英語では the が definite article「定冠詞」であり、対象が必ず世界に一つしかないこと、単数であること、以前に必ず言及されたことだけを意味するわけではない。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】文法・言語学の用語。英語学習では the と a/an、無冠詞の使い分けを説明するときに頻出する。definite は「特定の」という一般語義にも近いが、文法では指示対象を同定できるという性質を指す。  \n\n【文法パターン】the definite article＝定冠詞 the／a definite noun phrase＝定名詞句／definite reference to 〈person/thing〉＝〈人・物〉を特定して指す定の指示／a definite description of 〈person/thing〉＝〈人・物〉を同定する確定記述／a definite referent＝特定可能な指示対象／a noun phrase is definite＝名詞句が定である。  \n\n【コロケーション】\n\n・the definite article  \n用途: 英語の the のように、聞き手・読み手が指示対象を特定できることを示す冠詞を指す。  \n例: In English, the is the definite article used before singular and plural noun phrases.  \n訳: 英語では the が、単数・複数の名詞句の前に使われる定冠詞である。  \n\n・a definite noun phrase  \n用途: 指示対象が文脈から特定可能な名詞句を指す。  \n例: In “the book on the desk,” the whole phrase is a definite noun phrase.  \n訳: 「机の上のその本」では、句全体が定名詞句である。  \n\n・definite reference to 〈person/thing〉  \n用途: 名詞句が、文脈上どの人物・物を指すか特定できる定の指示を表す。  \n例: In “the company’s earlier report,” the noun phrase has a definite reference in this context.  \n訳: 「その会社の以前の報告書」では、この文脈で名詞句の指示対象が特定できる。  \n\n・a definite description of 〈person/thing〉  \n用途: 固有名を使わず、記述によって指示対象を同定する表現を指す。  \n例: “The first person to arrive” is a definite description in this context.  \n訳: この文脈では、「最初に到着した人」は確定記述である。  \n\n・a definite referent  \n用途: 名詞句が指し示す、文脈上特定可能な対象を指す。  \n例: The plural noun phrase can still have a definite referent.  \n訳: 複数名詞句でも、指示対象を特定できる場合がある。  \n\n・definite and indefinite articles  \n用途: the と a/an のように、指示対象の特定可能性が異なる冠詞を対比する。  \n例: The lesson contrasts definite and indefinite articles in everyday sentences.  \n訳: その授業では、日常文における定冠詞と不定冠詞を対比している。  \n\n【語法・注意】文法上の definite は「前に一度出た名詞」に限られない。`the door` はその場に一つしかないドアを指せるし、`the book on the desk` は修飾語によってどの本か分かるため定になる。単数か複数か、可算か不可算かも決定条件ではなく、`the books`、`the water` も定になり得る。specific は「特定のものを意図している」という意味で、`a specific book` のように不定冠詞と共存できるが、specific だから文法上 definite になるわけではない。英語の the には、種類全体を述べる `The tiger is endangered.` のような総称的用法もあるため、definite と「唯一の個体」を機械的に同一視しない。  \n\n【類義語】\n\n・identified  \n定義: どの人物・物を指すかが分かっている、または特定されている。  \n頻度: 〈9/10〉  \n違い: identified は対象が同定されている状態を平易に述べる。definite は名詞句の文法的な指示性を表す用語である。  \n例: The identified object was removed from the scene.  \n訳: 特定された物体は現場から取り除かれた。  \n\n・determinate  \n定義: 境界・値・指示対象などが決まっている。  \n頻度: 〈5/10〉  \n違い: determinate は形式的・専門的で、definite は英語の冠詞や名詞句の性質を説明する標準用語である。  \n例: The expression has a determinate meaning in this context.  \n訳: その表現はこの文脈では明確に定まった意味を持つ。  \n\n・specific  \n定義: 一般的なものではなく、特定の人物・物・内容に関する。  \n頻度: 〈10/10〉  \n違い: specific は個別性を表す一般語で、文法上の definite と重なることはあるが、`a specific book` のように不定名詞句にも使える。  \n例: She was looking for a specific file.  \n訳: 彼女は特定のファイルを探していた。  \n\n【反意語】\n\n・indefinite  \n定義: 名詞句の指示対象が特定できない、または特定の一つとして提示されない。  \n頻度: 〈7/10〉  \n違い: 文法上の indefinite は definite の直接の反対で、英語の a/an や、文脈によっては無冠詞の名詞句に関係する。  \n例: “A book” is indefinite because the listener does not know which book is meant.  \n訳: 「ある本」は、どの本を指すか聞き手に分からないため不定である。  \n\n・unidentified  \n定義: どの人物・物であるかが特定されていない。  \n頻度: 〈8/10〉  \n違い: unidentified は現実の対象を同定できない状態を示し、definite は文法上の名詞句が対象を特定可能に提示する状態を示す。  \n例: An unidentified caller left a message.  \n訳: 身元不明の発信者がメッセージを残した。  \n\n・generic  \n定義: 個別の一つではなく、種類全体や一般的な概念に関する。  \n頻度: 〈7/10〉  \n違い: generic は指示の範囲が一般化されていることを表す。definite と対照できるが、英語では definite article が総称的に使われる場合もあるため、完全な形の反意語ではない。  \n例: “Dogs are social animals” has a generic reference.  \n訳: 「犬は社会的な動物だ」は総称的な指示を持つ。  \n\n5. 【形容詞・植物学】有限の、定数の\n\n【日本語訳・定義】植物学で、花器官の数が一定で、通常は20未満で花弁数の倍数になること、または花序の主軸が花で終わり成長に限りがあることを表す専門用法である。一般語の「確実な」ではなく、数や成長が定まっているという意味で、definite inflorescence は determinate／cymose inflorescence に当たる。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】植物学に限られる低頻度の専門語。一般の文章では通常この意味で解釈せず、専門文献で floral organs、stamens、inflorescence などと共に現れる。  \n\n【文法パターン】definite stamens＝数が一定の雄しべ／a definite inflorescence＝主軸が花で終わる有限花序／definite growth＝成長が一定の段階で止まる定限成長。  \n\n【コロケーション】\n\n・definite stamens  \n用途: 花弁数との関係で数が一定の雄しべを指す。  \n例: The species has definite stamens, usually in a fixed multiple of the number of petals.  \n訳: その種には、通常、花弁数の決まった倍数になる定数の雄しべがある。  \n\n・a definite inflorescence  \n用途: 主軸が花で終わり、伸長に限りがある有限花序を指す。  \n例: The plant develops a definite inflorescence in which the main axis ends in a flower.  \n訳: その植物は、主軸が花で終わる有限花序を形成する。  \n\n・definite growth  \n用途: 植物体や器官の成長が一定の段階で止まる定限成長を表す。  \n例: Definite growth is common in some compact flowering plants.  \n訳: 定限成長は、一部の小型の開花植物でよく見られる。  \n\n【語法・注意】この用法は一般英語の definite answer や definite plan とは別の専門的な意味である。`definite inflorescence` は花序の成長様式を指し、単に「明確な花序」という意味ではない。植物学では `indefinite` や `indeterminate` が、数や主軸の成長に固定された終点がない対照表現として使われる。  \n\n【類義語】\n\n・determinate  \n定義: 植物の成長・花序・器官の数などが一定の限界で決まる。  \n頻度: 〈4/10〉  \n違い: determinate はこの植物学上の意味でより一般的な専門語で、definite は同じ特徴を別の語彙で表す。  \n例: The plant produces a determinate inflorescence.  \n訳: その植物は有限花序を形成する。  \n\n・fixed-number  \n定義: 数が一定に定められている。  \n頻度: 〈2/10〉  \n違い: fixed-number は説明的な表現で、definite stamens の特徴を言い換えるが、単独の標準用語としての使用は限定的である。  \n例: The flower has a fixed number of stamens.  \n訳: その花には一定数の雄しべがある。  \n\n【反意語】\n\n・indefinite  \n定義: 数が一定でない、または花序の成長に固定された終点がない。  \n頻度: 〈3/10〉  \n違い: indefinite は definite stamens や definite inflorescence の反対側にある植物学用語で、器官数や成長の上限が定まらないことを示す。  \n例: An indefinite inflorescence can continue producing flowers along its main axis.  \n訳: 無限花序は主軸に沿って花を作り続けることがある。  \n\n・indeterminate  \n定義: 成長や結果の終点があらかじめ固定されていない。  \n頻度: 〈5/10〉  \n違い: indeterminate は植物学で definite／determinate と対立し、主軸の成長が花で終わらないことなどを表す。  \n例: The species shows indeterminate rather than definite growth.  \n訳: その種は定限成長ではなく不定成長を示す。  ",
  "_output_metadata": {
    "schema_version": "final_review_v3",
    "stage": "final_review",
    "run_id": "blind-definite-20260919T135234Z-e94458a7",
    "context_id": "blind-definite-context-20260919T135234Z-e94458a7",
    "input_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
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
    "cold_review_summary": "本文を文脈なしで確認し、意味方向または語義境界に関わる局所的な修正候補を3件記録した。",
    "final_blind_decision": "pass",
    "blind_seal": {
      "schema_version": "blind_seal_v3",
      "stage": "blind_seal",
      "entry_path": "entries/d/definite.md",
      "body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
      "final_blind_path": "audits/runs/d/definite/20260919T135234Z-e94458a7/final_blind.json",
      "final_blind_sha256": "1d53fa8d0d62d18949a74d88f95c43a795c520e4620a65332c6f313ee190f517",
      "blind_output_sha256": "511c884a02110cd107a7f38919daa54b5586f6edcabdd9a9a0762cb6a8600e4a",
      "sealed_at": "2026-09-19T11:21:46.782952-04:00"
    },
    "checker_recheck": {
      "current_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
      "full_recheck": false,
      "invalidated_passes": [
        "evidence",
        "example-attribution",
        "frame-relation",
        "qualification",
        "translation"
      ],
      "pass_results": [
        {
          "pass_id": "translation",
          "mode": "rechecked",
          "validated_on_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
          "spec_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
          "normalized_input_sha256": "329fdab657cc20828c6b8c2fa99228ae6fe7a872816c1017e426682b669bf20b",
          "source_artifact_sha256": "eccbe24290b5fd13c7cd6815dfb65ccbbce89ee27dafca3ceed75c616a98d2d4",
          "output_sha256": "2b528fc48d5cbd38750c5af7e2c9d65f3128bcbace85ee4da7e6ccce474599a2",
          "response_path": "audits/runs/d/definite/20260919T135234Z-e94458a7/handoff/recheck/round1/translation.response.json",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true
        },
        {
          "pass_id": "sense-structure",
          "mode": "reused",
          "validated_on_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
          "spec_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
          "normalized_input_sha256": "a65c5d4f6076d8c2d12e74c840faf6e3f20e6c0a99bb9b80039060d7b3caf3aa",
          "source_artifact_sha256": "eccbe24290b5fd13c7cd6815dfb65ccbbce89ee27dafca3ceed75c616a98d2d4",
          "output_sha256": "7f2c710503ce47883441745a67c38f372841c718a91ddf696159f5d7db416ed5",
          "source_output_path": "audits/runs/d/definite/20260919T135234Z-e94458a7/check_passes/sense-structure.json",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reuse_validated": true
        },
        {
          "pass_id": "frame-relation",
          "mode": "rechecked",
          "validated_on_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
          "spec_sha256": "3598ca81a5784639c6b43a0806d0981a985bf4174f424c744aad1dde787bfcef",
          "normalized_input_sha256": "6786528bda43609c2e45bf419faf2637fc91d4f2e6fa822740bd3182ac7cf959",
          "source_artifact_sha256": "eccbe24290b5fd13c7cd6815dfb65ccbbce89ee27dafca3ceed75c616a98d2d4",
          "output_sha256": "4b28e60a3cfc2b00a075d8a79a4dbe42a06c2af47f09b0245fe4fa3a2c66a40f",
          "response_path": "audits/runs/d/definite/20260919T135234Z-e94458a7/handoff/recheck/round1/frame-relation.response.json",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true
        },
        {
          "pass_id": "example-attribution",
          "mode": "rechecked",
          "validated_on_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
          "spec_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
          "normalized_input_sha256": "66f724a13ede61ff1dbecf6ee22998ef512eb1e8737297f24b4164f776abca48",
          "source_artifact_sha256": "eccbe24290b5fd13c7cd6815dfb65ccbbce89ee27dafca3ceed75c616a98d2d4",
          "output_sha256": "ce33c6de5a6825ef3110dc94c2c1edcabc47bc601cbf2f6be98317847accbd89",
          "response_path": "audits/runs/d/definite/20260919T135234Z-e94458a7/handoff/recheck/round1/example-attribution.response.json",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true
        },
        {
          "pass_id": "qualification",
          "mode": "rechecked",
          "validated_on_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
          "spec_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
          "normalized_input_sha256": "ec576ba700cf9f26e9d302c9ebb98f7e2886285b9f2f2025c0c5b912e741d294",
          "source_artifact_sha256": "eccbe24290b5fd13c7cd6815dfb65ccbbce89ee27dafca3ceed75c616a98d2d4",
          "output_sha256": "f40fe67b877baec9621b448c951d30fe705810b6dd23cc8075dc68d2d3085067",
          "response_path": "audits/runs/d/definite/20260919T135234Z-e94458a7/handoff/recheck/round1/qualification.response.json",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true
        },
        {
          "pass_id": "pronunciation",
          "mode": "reused",
          "validated_on_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
          "spec_sha256": "7e3e94267ac9f917c901c12580b91e570b5989df7adfbf2a39b833478c766d8a",
          "normalized_input_sha256": "0f1ba081f77f97a08089e7f9f659106c1be4049bd60c0e59ecd717f51815bb95",
          "source_artifact_sha256": "eccbe24290b5fd13c7cd6815dfb65ccbbce89ee27dafca3ceed75c616a98d2d4",
          "output_sha256": "a45aaa57215966e5792087af435bfdf8a3c7c02f49ad62c321daa0f7338ad617",
          "source_output_path": "audits/runs/d/definite/20260919T135234Z-e94458a7/check_passes/pronunciation.json",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reuse_validated": true
        },
        {
          "pass_id": "evidence",
          "mode": "rechecked",
          "validated_on_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
          "spec_sha256": "f0de393d4d064190e23916b2e8bfda25b2b83fd29e14cf52395c894b8539d7e9",
          "normalized_input_sha256": "ff50c1ad51ed13a1c969aa821eb3dcbea058e459514ab587ff543db3f14f1d07",
          "source_artifact_sha256": "eccbe24290b5fd13c7cd6815dfb65ccbbce89ee27dafca3ceed75c616a98d2d4",
          "output_sha256": "da7410ff369066e228a2df3eafc3161afd92e663275026b33133100d024b6aa4",
          "response_path": "audits/runs/d/definite/20260919T135234Z-e94458a7/handoff/recheck/round1/evidence.response.json",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true
        }
      ]
    },
    "post_blind_verification": {
      "schema_version": "post_blind_verification_v1",
      "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf",
      "recorded_at": "2026-09-19T15:22:00Z",
      "checker_recheck_completed": true,
      "checker_recheck_manifest_sha256": "450723147cbed4a50139b83155f7d46d407d21deed8fa74b10ad7765ed7fc25d",
      "final_blind_repeated": true,
      "final_blind_sha256": "1d53fa8d0d62d18949a74d88f95c43a795c520e4620a65332c6f313ee190f517",
      "final_blind_recorded_at": "2026-09-19T15:21:17.293417+00:00",
      "attempt_number": 1,
      "status": "complete"
    },
    "resolutions": [
      {
        "id": "CR-definite-001",
        "finding_id": "CR-definite-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "肯定・否定の対応と否定範囲が伝わるよう anything definite と nothing definite を別々の自然な日本語フレームへ改めた。",
        "resolved_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "CR-definite-002",
        "finding_id": "CR-definite-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "a definite number of の中心義である「決まった人数」を保ち、上限という含意に狭めない訳へ改めた。",
        "resolved_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "CR-definite-003",
        "finding_id": "CR-definite-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "文法用語として、名詞句の指示対象が文脈上特定可能になる definite reference の例文へ差し替えた。",
        "resolved_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
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
        "text": "米: /ˈdefənət/｜英: /ˈdefɪnət/。3音節で、第1音節に主強勢がある。米語では第2音節の母音を弱い /ə/、英語では /ɪ/ と示すことが多い。語末は /nət/ で、綴りの -ite を /eɪt/ と読まない。definitely は米 /ˈdefənətli/・英 /ˈdefɪnətli/ のように発音し、語尾の -ly が加わる。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text": "definite は16世紀初頭の英語で「固定された、確かな」の意味で使われ、ラテン語 dēfīnītus「境界を定められた、限定された、確定した」から来た。これは dēfīnīre「限界を定める、決定する、説明する」の過去分詞で、de-「完全に」と finis「境界、終わり」に分けて考えられる。18世紀初頭には文法用語として「限定する」の意味でも使われた。define、finite、definition、definitive、indefinite は同じ語源の語族に属する。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text": "・definitely：副詞。「確実に、間違いなく、はっきりと」。話者の確信を表す文副詞としても、動詞・形容詞を強める副詞としても使う。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text": "・definiteness：名詞。「明確さ、確定性、定性」。文法では名詞句の指示対象が特定可能である性質を表す。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text": "・indefinite：接頭辞 in-「否定」を伴う関連形。「不確定な、漠然とした、定のない」。definite の単純な反意語になる用法と、文法用語としての用法がある。"
      },
      {
        "id": "word_formation:004",
        "kind": "word_formation",
        "location": "line:15",
        "section": "＃語形成",
        "sense": "",
        "text": "・definitive：同じラテン語幹系統の形容詞。「決定的な、最終的な」。definite よりも最終判断・決着の含みが強く、単なる語尾違いとして置き換えない。"
      },
      {
        "id": "word_formation:005",
        "kind": "word_formation",
        "location": "line:16",
        "section": "＃語形成",
        "sense": "",
        "text": "・define / definition：同じ語源にさかのぼる動詞・名詞。「境界を定める」「定義」。definite の直接の活用形ではないが、「曖昧さを境界づける」という意味のつながりがある。"
      },
      {
        "id": "core_image:001",
        "kind": "core_image",
        "location": "line:20",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "definite の共通核は、「境界・同一性・判断を曖昧さから切り出し、はっきり固定する」ことである。何を固定するかによって、決定、観察上の明瞭さ、範囲や内容の限定、文法上の指示対象、植物の数や成長の上限へ広がる。"
      },
      {
        "id": "core_image:002",
        "kind": "core_image",
        "location": "line:21",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "・判断や予定を曖昧さから切り出して固定する → 「確定した、決まった」（語義1）"
      },
      {
        "id": "core_image:003",
        "kind": "core_image",
        "location": "line:22",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "・特徴や変化を観察上はっきり切り出す → 「明らかな、はっきりした」（語義2）"
      },
      {
        "id": "core_image:004",
        "kind": "core_image",
        "location": "line:23",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "・範囲や内容を境界づけて固定する → 「具体的な、特定の」（語義3）"
      },
      {
        "id": "core_image:005",
        "kind": "core_image",
        "location": "line:24",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "・指示対象を文脈上特定可能なものとして切り出す → 「定の、特定できる」（語義4）"
      },
      {
        "id": "core_image:006",
        "kind": "core_image",
        "location": "line:25",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "・数や成長の上限を固定する → 「有限の、定数の」（語義5）"
      },
      {
        "id": "sense_boundary:001",
        "kind": "sense_boundary",
        "location": "line:29",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "1. 【形容詞・限定用法／叙述用法】確定した、決まった"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:31",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "答え、決定、計画、日付、合意、意図などが、曖昧な候補や一時的な案ではなく、内容として定まり、変更される可能性が低いことを表す。必ずしも今後絶対に変更できないという意味ではなく、現時点で決定・約束・判断が明確になっていることに焦点がある。"
      },
      {
        "id": "frequency:001",
        "kind": "frequency",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "〈9/10〉"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:35",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "標準語で、会話・ビジネス・報道・公式文書まで広く使う。計画や合意の確定性を述べるときに多く、日常会話では sure が話者の確信、definite が決定や内容の確定を表しやすい。ここでの頻度の数値はこの辞書内の学習上の相対目安で、10は日常・一般文書で頻出、1は限定的な専門用法を表す。特定領域内のコーパス頻度や厳密な語義間順位ではない。"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:37",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "a definite answer/decision/plan/date/deadline＝確定した答え・決定・計画・日付・期限"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:37",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "a definite agreement/offer/commitment＝明確に成立した合意・正式な申し出・確約"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:37",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "have no definite plans/ideas＝決まった計画・具体的な考えがない"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:37",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "anything definite＝何か確定したこと・情報"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:37",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "nothing definite＝何も確定したことはない"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:37",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "be definite about something＝ある事柄について態度・内容を明確にする"
      },
      {
        "id": "grammar_pattern:007",
        "kind": "grammar_pattern",
        "location": "line:37",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "a definite yes/no＝はっきりした賛成"
      },
      {
        "id": "grammar_pattern:008",
        "kind": "grammar_pattern",
        "location": "line:37",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "拒否。"
      },
      {
        "id": "collocation:001",
        "kind": "collocation",
        "location": "lines:41-44",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・a definite answer\n用途: 予想や曖昧な返事ではなく、決定した答えを求める。\n例: We need a definite answer by Friday, not another tentative suggestion.\n訳: 私たちは金曜日までに、また別の仮案ではなく確定した答えを必要としている。"
      },
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:46-49",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・a definite date for 〈event〉\n用途: 行事・開始・発売などの日付が決まっていることを表す。\n例: The organizers have not announced a definite date for the launch.\n訳: 主催者は発売の確定した日付をまだ発表していない。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:51-54",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・no definite plans\n用途: 将来の予定がまだ決まっていないことを表す。\n例: I have no definite plans for the weekend yet.\n訳: 私は週末の具体的な予定をまだ決めていない。"
      },
      {
        "id": "collocation:004",
        "kind": "collocation",
        "location": "lines:56-59",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・anything definite about something\n用途: ある事柄について確定した情報があるかを尋ねる。\n例: Do you know anything definite about when the train will leave?\n訳: 列車がいつ出るかについて、何か確定した情報を知っていますか。"
      },
      {
        "id": "collocation:005",
        "kind": "collocation",
        "location": "lines:61-64",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・a definite yes/no\n用途: ためらいや条件付きではない、明確な肯定・拒否を表す。\n例: Her reply was a definite no, so we stopped asking.\n訳: 彼女の返事は明確な拒否だったので、私たちは尋ねるのをやめた。"
      },
      {
        "id": "collocation:006",
        "kind": "collocation",
        "location": "lines:66-69",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・be definite about 〈decision/position〉\n用途: 決定や立場を曖昧にせず、はっきり示す。\n例: Please be definite about your position before the meeting begins.\n訳: 会議が始まる前に、自分の立場を明確にしてください。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:71-74",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・a definite commitment to do\n用途: ある行動を実行するという明確な確約を表す。\n例: The grant requires a definite commitment to complete the project.\n訳: その助成金には、プロジェクトを完了するという明確な確約が必要だ。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:76-79",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・a definite agreement\n用途: 条件や内容が定まり、当事者間で成立した合意を表す。\n例: No definite agreement had been reached by the end of the meeting.\n訳: 会議の終了時までに、確定した合意は成立していなかった。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:81",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "certain は「真実だと確信している」「起こる可能性が高い」という話者の認識にも使えるが、definite は答え・計画・日付などの内容が決まっていることを強調しやすい。final は「それ以上変更しない最終段階」、firm は意思・態度の強さに焦点があるため、definite と完全には交換できない。`I have no definite plans.` は「将来の予定が一切ない」ではなく「決まった予定はない」という意味である。definite と definitely、definite と definitive を品詞や意味を考えずに置き換えない。綴りは definite であり、definate ではない。"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:85-90",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・certain\n定義: 疑いがなく、確かだと判断される。\n頻度: 〈10/10〉\n違い: certain は事実・未来・話者の確信を広く表す。definite は答えや予定が決定済みで曖昧でないことを表しやすい。\n例: I am certain that she will accept the offer.\n訳: 彼女がその申し出を受けると私は確信している。"
      },
      {
        "id": "synonym:002",
        "kind": "synonym",
        "location": "lines:92-97",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・settled\n定義: 議論や検討の後に、決定・合意されている。\n頻度: 〈8/10〉\n違い: settled は未決の状態が終わったことに焦点があり、definite は決まった内容が明確であることに焦点がある。\n例: The venue for the conference is now settled.\n訳: 会議の会場は今や決まっている。"
      },
      {
        "id": "synonym:003",
        "kind": "synonym",
        "location": "lines:99-104",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・firm\n定義: 意思・約束・態度が強く、簡単には変わらない。\n頻度: 〈9/10〉\n違い: firm は人の決意や約束の強さを示し、definite は決定内容や情報の確定性を示す。\n例: She made a firm promise to return the money.\n訳: 彼女はそのお金を返すと固く約束した。"
      },
      {
        "id": "synonym:004",
        "kind": "synonym",
        "location": "lines:106-111",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・fixed\n定義: 位置・日時・数量などが変更されないように定められている。\n頻度: 〈10/10〉\n違い: fixed は変更不能・変更予定なしという状態を強く示し、definite は曖昧さが解消されていることを広く示す。\n例: The shop has fixed opening hours.\n訳: その店には固定された営業時間がある。"
      },
      {
        "id": "antonym:001",
        "kind": "antonym",
        "location": "lines:115-120",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・uncertain\n定義: 確実でなく、結果や内容がまだ分からない。\n頻度: 〈9/10〉\n違い: uncertain は確定性の反対で、definite が決定・情報の明確さを示すのに対し、見通しや判断が定まらない。\n例: The outcome remains uncertain.\n訳: 結果は依然として不確かだ。"
      },
      {
        "id": "antonym:002",
        "kind": "antonym",
        "location": "lines:122-127",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・tentative\n定義: 仮のもので、後で変更される可能性がある。\n頻度: 〈8/10〉\n違い: tentative は計画・合意などが試案段階であることを示し、definite はそこから確定した段階を示す。\n例: We made a tentative booking for next month.\n訳: 私たちは来月について仮予約をした。"
      },
      {
        "id": "antonym:003",
        "kind": "antonym",
        "location": "lines:129-134",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・undecided\n定義: 選択・判断・決定がまだ行われていない。\n頻度: 〈8/10〉\n違い: undecided は決める主体や問題が未決定であること、definite は答えや立場が決まっていることを表す。\n例: The committee is still undecided about the proposal.\n訳: 委員会はその提案についてまだ決めていない。"
      },
      {
        "id": "antonym:004",
        "kind": "antonym",
        "location": "lines:136-141",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法】確定した、決まった",
        "text": "・indefinite\n定義: 明確な範囲・期間・内容が定まっていない。\n頻度: 〈7/10〉\n違い: indefinite は期間・数量・指示対象などの境界が不明確であることを表し、definite は境界が定まっていることを表す。\n例: The project was postponed for an indefinite period.\n訳: そのプロジェクトは無期限に延期された。"
      },
      {
        "id": "sense_boundary:002",
        "kind": "sense_boundary",
        "location": "line:143",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:145",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "変化、差、効果、兆候、利点などが、観察や比較によって実際に認められるほど明瞭・顕著であることを表す。必ずしも論理的に証明済み、絶対に疑いがないという意味ではなく、話し手が変化や特徴をはっきり認識しているという評価を含むことがある。"
      },
      {
        "id": "frequency:002",
        "kind": "frequency",
        "location": "line:147",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "〈8/10〉"
      },
      {
        "id": "register:002",
        "kind": "register",
        "location": "line:149",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "標準語で、会話・報道・評価・ビジネス文書まで使える。clear や obvious よりやや説明的・形式的で、improvement、difference、effect、sign など、観察できる変化や結果を修飾することが多い。"
      },
      {
        "id": "grammar_pattern:009",
        "kind": "grammar_pattern",
        "location": "line:151",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "a definite improvement/change/difference＝明らかな改善・変化・違い"
      },
      {
        "id": "grammar_pattern:010",
        "kind": "grammar_pattern",
        "location": "line:151",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "a definite sign/indication of something＝～の明らかな兆候・指標"
      },
      {
        "id": "grammar_pattern:011",
        "kind": "grammar_pattern",
        "location": "line:151",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "have a definite effect/impact on something＝ある物事に明確な効果・影響を及ぼす"
      },
      {
        "id": "grammar_pattern:012",
        "kind": "grammar_pattern",
        "location": "line:151",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "a definite advantage/disadvantage＝明確な利点・不利"
      },
      {
        "id": "grammar_pattern:013",
        "kind": "grammar_pattern",
        "location": "line:151",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "a definite possibility＝現実味のある可能性"
      },
      {
        "id": "grammar_pattern:014",
        "kind": "grammar_pattern",
        "location": "line:151",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "see/feel a definite difference＝はっきり違いを感じる。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:155-158",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・a definite improvement\n用途: 状態や成績が実際に良くなったと認められることを表す。\n例: The new treatment produced a definite improvement in her symptoms.\n訳: 新しい治療によって、彼女の症状には明らかな改善が見られた。"
      },
      {
        "id": "collocation:010",
        "kind": "collocation",
        "location": "lines:160-163",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・a definite difference between 〈A〉 and 〈B〉\n用途: 二つの対象の違いがはっきり認められることを表す。\n例: There is a definite difference between the two versions of the report.\n訳: その報告書の二つの版には明らかな違いがある。"
      },
      {
        "id": "collocation:011",
        "kind": "collocation",
        "location": "lines:165-168",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・a definite sign of something\n用途: ある状態や出来事を示す、見分けやすい兆候を表す。\n例: A sudden drop in demand is a definite sign of weakening consumer confidence.\n訳: 需要の急減は、消費者信頼感が弱まっている明らかな兆候だ。"
      },
      {
        "id": "collocation:012",
        "kind": "collocation",
        "location": "lines:170-173",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・have a definite effect on something\n用途: 行為・条件・政策などが、結果に明確な影響を与えることを表す。\n例: Sleep has a definite effect on how well people remember new information.\n訳: 睡眠は、人が新しい情報をどれだけよく覚えるかに明確な影響を及ぼす。"
      },
      {
        "id": "collocation:013",
        "kind": "collocation",
        "location": "lines:175-178",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・a definite advantage\n用途: 他と比べて認めやすい具体的な利点を強調する。\n例: The shorter route offers a definite advantage during the winter.\n訳: その短い経路は冬の間、明確な利点をもたらす。"
      },
      {
        "id": "collocation:014",
        "kind": "collocation",
        "location": "lines:180-183",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・a definite possibility\n用途: 単なる空想ではなく、現実に起こり得る可能性を表す。\n例: A delay is a definite possibility if the storm continues.\n訳: 嵐が続けば、遅延は十分に現実的な可能性だ。"
      },
      {
        "id": "collocation:015",
        "kind": "collocation",
        "location": "lines:185-188",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・see a definite change in something\n用途: 状態や傾向の変化を観察してはっきり認める。\n例: We can see a definite change in customer behavior after the price increase.\n訳: 値上げ後、顧客の行動に明らかな変化が見られる。"
      },
      {
        "id": "collocation:016",
        "kind": "collocation",
        "location": "lines:190-193",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・with a definite sense of 〈emotion〉\n用途: 特定の感情を明確に抱いていることを表す。\n例: He left the room with a definite sense of relief.\n訳: 彼は明確な安堵感を抱いて部屋を出た。"
      },
      {
        "id": "usage_note:002",
        "kind": "usage_note",
        "location": "line:195",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "この用法の definite は「証明された」と同義ではない。`a definite improvement` は改善がはっきり認められるという意味で、科学的な因果関係が完全に証明されたという意味ではない。`a definite possibility` は「確実に起こること」ではなく「現実味のある可能性」である。obvious は文脈や話者にとって明白と評価されること、clear は混乱や曖昧さがないこと、noticeable は知覚上目立つことを強調し、definite は変化・差・効果などを明確なものとして認めることに焦点がある。"
      },
      {
        "id": "synonym:005",
        "kind": "synonym",
        "location": "lines:199-204",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・clear\n定義: 意味・事実・視界などに混乱や曖昧さがない。\n頻度: 〈10/10〉\n違い: clear は理解可能性や障害のなさを広く表す。definite は変化・差・効果などが明確に認められることを強調しやすい。\n例: The instructions are clear and easy to follow.\n訳: その指示は明確で、従いやすい。"
      },
      {
        "id": "synonym:006",
        "kind": "synonym",
        "location": "lines:206-211",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・obvious\n定義: 見たり考えたりすれば、すぐに分かる。\n頻度: 〈10/10〉\n違い: obvious は認識の容易さを強く示す。definite は明らかさを示すが、必ずしも誰にとっても自明とは限らない。\n例: It was obvious that the machine had stopped working.\n訳: その機械が動かなくなったことは明らかだった。"
      },
      {
        "id": "synonym:007",
        "kind": "synonym",
        "location": "lines:213-218",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・noticeable\n定義: 見たり感じたりして気づくことができる。\n頻度: 〈8/10〉\n違い: noticeable は知覚上の目立ちやすさに焦点がある。definite は目立つだけでなく、差や効果を明確なものとして評価する。\n例: There was a noticeable drop in temperature overnight.\n訳: 一晩で気温が目に見えて下がった。"
      },
      {
        "id": "synonym:008",
        "kind": "synonym",
        "location": "lines:220-225",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・distinct\n定義: ほかのものと区別できるほど特徴がはっきりしている。\n頻度: 〈9/10〉\n違い: distinct は境界や識別可能性を強調する。definite は結果・変化・効果が明確に認められることにも使う。\n例: The two methods produce distinct results.\n訳: その二つの方法は明確に異なる結果を生む。"
      },
      {
        "id": "synonym:009",
        "kind": "synonym",
        "location": "lines:227-232",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・marked\n定義: 程度や差が目立つほど顕著である。\n頻度: 〈7/10〉\n違い: marked は変化・差・改善の大きさを強く示し、definite はそこまで大きくなくても、存在が明確であることを表せる。\n例: The report shows a marked reduction in waste.\n訳: その報告書は廃棄物の顕著な削減を示している。"
      },
      {
        "id": "antonym:005",
        "kind": "antonym",
        "location": "lines:236-241",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・unclear\n定義: 意味・原因・結果などがはっきりしない。\n頻度: 〈9/10〉\n違い: unclear は理解や判断の明瞭さの反対で、definite は観察・評価の対象が明らかであることを示す。\n例: The cause of the failure is still unclear.\n訳: 故障の原因はまだはっきりしない。"
      },
      {
        "id": "antonym:006",
        "kind": "antonym",
        "location": "lines:243-248",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・indistinct\n定義: 輪郭・音・違いなどがぼんやりして区別しにくい。\n頻度: 〈6/10〉\n違い: indistinct は知覚上の境界が弱いことを表し、definite は特徴や差が明瞭に取り出せることを表す。\n例: The distant hills were indistinct in the fog.\n訳: 遠くの丘は霧の中でぼんやりしていた。"
      },
      {
        "id": "antonym:007",
        "kind": "antonym",
        "location": "lines:250-255",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・限定用法／叙述用法】明らかな、はっきりした",
        "text": "・imperceptible\n定義: 感覚や観察ではほとんど気づけない。\n頻度: 〈5/10〉\n違い: imperceptible は変化や差が知覚できないほど小さいことを示し、definite は明確に認められることを示す。\n例: The change in pressure was almost imperceptible.\n訳: 圧力の変化はほとんど知覚できなかった。"
      },
      {
        "id": "sense_boundary:003",
        "kind": "sense_boundary",
        "location": "line:257",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "3. 【形容詞・限定用法】具体的な、特定の"
      },
      {
        "id": "definition:003",
        "kind": "definition",
        "location": "line:259",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "数量、期間、範囲、時点、形、情報などに明確な境界や内容があり、漠然としたものではないことを表す。特定の対象を指す場合でも、文脈上その対象を識別できるという文法上の意味とは異なり、ここでは内容・範囲・条件が具体的に定まっていることに焦点がある。"
      },
      {
        "id": "frequency:003",
        "kind": "frequency",
        "location": "line:261",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "〈7/10〉"
      },
      {
        "id": "register:003",
        "kind": "register",
        "location": "line:263",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "標準語。契約・行政・学術・技術文書では形式的な用法が現れ、数学では `definite integral` などの専門連語で使われる。specific は選び出された個別性、exact は数値や内容の厳密な一致、definite は範囲や条件が定まっていることを強調しやすい。"
      },
      {
        "id": "grammar_pattern:015",
        "kind": "grammar_pattern",
        "location": "line:265",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "a definite amount/number/quantity/period＝具体的な量・数・期間"
      },
      {
        "id": "grammar_pattern:016",
        "kind": "grammar_pattern",
        "location": "line:265",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "at a definite time/stage＝特定の時点・段階で"
      },
      {
        "id": "grammar_pattern:017",
        "kind": "grammar_pattern",
        "location": "line:265",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "within definite limits＝明確な範囲内で"
      },
      {
        "id": "grammar_pattern:018",
        "kind": "grammar_pattern",
        "location": "line:265",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "definite information/details＝具体的な情報・詳細"
      },
      {
        "id": "grammar_pattern:019",
        "kind": "grammar_pattern",
        "location": "line:265",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "a definite shape/form＝はっきり定まった形・形式"
      },
      {
        "id": "grammar_pattern:020",
        "kind": "grammar_pattern",
        "location": "line:265",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "a definite integral＝定積分。"
      },
      {
        "id": "collocation:017",
        "kind": "collocation",
        "location": "lines:269-272",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・a definite amount of 〈money/material〉\n用途: 金額や物質の量が一定の範囲・数量として定まっていることを表す。\n例: The machine requires a definite amount of oil to operate safely.\n訳: その機械を安全に稼働させるには、一定量の油が必要だ。"
      },
      {
        "id": "collocation:018",
        "kind": "collocation",
        "location": "lines:274-277",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・a definite number of 〈people/items〉\n用途: 人数や個数が曖昧でなく、決まった数であることを表す。\n例: Only a definite number of students can join the laboratory tour.\n訳: 研究室見学には決まった人数の学生だけが参加できる。"
      },
      {
        "id": "collocation:019",
        "kind": "collocation",
        "location": "lines:279-282",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・for a definite period\n用途: 期間の終点または長さがあらかじめ定められていることを表す。\n例: The equipment may be rented for a definite period of six months.\n訳: その設備は6か月という定められた期間、借りることができる。"
      },
      {
        "id": "collocation:020",
        "kind": "collocation",
        "location": "lines:284-287",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・within definite limits\n用途: 許容範囲や境界を明確に限定する。\n例: The temperature must remain within definite limits during transport.\n訳: 輸送中、温度は明確に定められた範囲内に保たなければならない。"
      },
      {
        "id": "collocation:021",
        "kind": "collocation",
        "location": "lines:289-292",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・definite information about 〈topic〉\n用途: 内容が具体的で明確な情報を表し、文脈によっては確かな情報を含意する。\n例: We need definite information about the delivery schedule before placing the order.\n訳: 注文を出す前に、納入予定について具体的な情報が必要だ。"
      },
      {
        "id": "collocation:022",
        "kind": "collocation",
        "location": "lines:294-297",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・a definite shape/form\n用途: 輪郭や形式が一定で、別の形と区別できることを表す。\n例: The crystals grow into a definite shape under controlled conditions.\n訳: その結晶は、管理された条件下で一定の形に成長する。"
      },
      {
        "id": "collocation:023",
        "kind": "collocation",
        "location": "lines:299-302",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・a definite integral\n用途: 数学で、積分区間の上下端が指定された定積分を指す。\n例: The area under the curve can be calculated with a definite integral.\n訳: 曲線の下の面積は定積分で計算できる。"
      },
      {
        "id": "usage_note:003",
        "kind": "usage_note",
        "location": "line:304",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "`a definite amount` は「量が決まっている」ことを示すが、必ずしも聞き手がその数値を知っているとは限らない。`specific` は「その特定のもの」という選択に、`exact` は誤差のない数値・内容に焦点がある。`definite information` は具体的で明確な情報（文脈によっては確かな情報）、`definite plans` は決定済みの予定というように、名詞によって「具体的」と「確定した」のどちらが前面に出るかが変わる。`definite integral` は「確実な積分」ではなく、積分区間が定まった数学用語である。"
      },
      {
        "id": "synonym:010",
        "kind": "synonym",
        "location": "lines:308-313",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・specific\n定義: ほかのものではなく、特定の対象・内容に関する。\n頻度: 〈10/10〉\n違い: specific は個別の対象を選び出すことを強調し、definite は数量・範囲・条件などが明確に定まっていることを強調する。\n例: Please give me a specific example.\n訳: 具体的な例を一つ挙げてください。"
      },
      {
        "id": "synonym:011",
        "kind": "synonym",
        "location": "lines:315-320",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・precise\n定義: 細部や数値が正確で、曖昧さがない。\n頻度: 〈9/10〉\n違い: precise は細かい正確さを要求する。definite は必ずしも数値の厳密さを求めず、境界や内容が決まっていることを示す。\n例: The report provides precise measurements.\n訳: その報告書は正確な測定値を示している。"
      },
      {
        "id": "synonym:012",
        "kind": "synonym",
        "location": "lines:322-327",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・specified\n定義: 条件・文書・規則などで明示的に指定されている。\n頻度: 〈8/10〉\n違い: specified は誰かが明示して指定したことに焦点があり、definite は指定の有無にかかわらず内容が定まっていることを表せる。\n例: The work must be completed within the specified time.\n訳: 作業は指定された時間内に完了しなければならない。"
      },
      {
        "id": "synonym:013",
        "kind": "synonym",
        "location": "lines:329-334",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・determinate\n定義: 限界・終点・結果が決まっている。\n頻度: 〈5/10〉\n違い: determinate は形式的・専門的で、数学・科学・哲学などで境界や結果の決定性を述べる。definite は一般語としてより広く使う。\n例: The process has a determinate end point.\n訳: その過程には明確に定まった終点がある。"
      },
      {
        "id": "synonym:014",
        "kind": "synonym",
        "location": "lines:336-341",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・fixed\n定義: 位置・数量・時期などが動かないように定められている。\n頻度: 〈10/10〉\n違い: fixed は変更されない状態を強く示し、definite は具体的に境界づけられた情報や範囲にも使う。\n例: The fee is fixed for the entire contract period.\n訳: 料金は契約期間全体を通じて固定されている。"
      },
      {
        "id": "antonym:008",
        "kind": "antonym",
        "location": "lines:345-350",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・indefinite\n定義: 範囲・期間・数量・内容などが決まっていない。\n頻度: 〈7/10〉\n違い: indefinite は定まった境界がないことを直接表し、definite は範囲や条件が具体化されていることを表す。\n例: The meeting was postponed for an indefinite period.\n訳: 会議は無期限に延期された。"
      },
      {
        "id": "antonym:009",
        "kind": "antonym",
        "location": "lines:352-357",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・unspecified\n定義: 必要な内容や条件が明示されていない。\n頻度: 〈7/10〉\n違い: unspecified は情報が指定されていないことに焦点があり、definite は情報の境界や内容が明らかであることを表す。\n例: The shipment was delayed for unspecified reasons.\n訳: その発送は理由が明示されないまま遅れた。"
      },
      {
        "id": "antonym:010",
        "kind": "antonym",
        "location": "lines:359-364",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・vague\n定義: 表現・考え・範囲などがぼんやりして具体性に欠ける。\n頻度: 〈9/10〉\n違い: vague は内容の輪郭が弱いことを表し、definite は内容を具体的に切り出せることを表す。\n例: His answer was too vague to be useful.\n訳: 彼の答えは曖昧すぎて役に立たなかった。"
      },
      {
        "id": "antonym:011",
        "kind": "antonym",
        "location": "lines:366-371",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【形容詞・限定用法】具体的な、特定の",
        "text": "・unlimited\n定義: 数量・範囲・期間などに上限がない。\n頻度: 〈8/10〉\n違い: unlimited は上限の不存在を示し、definite は上限や範囲が定められていることを示す。ただし、definite が必ず有限量を意味するわけではない。\n例: The plan offers unlimited data usage.\n訳: そのプランはデータ通信を無制限で提供する。"
      },
      {
        "id": "sense_boundary:004",
        "kind": "sense_boundary",
        "location": "line:373",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "4. 【形容詞・文法用語】定の、特定できる"
      },
      {
        "id": "definition:004",
        "kind": "definition",
        "location": "line:375",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "文法で、名詞句の指示対象が、既出、状況上の唯一性、修飾語、共有知識などによって聞き手・読み手に特定可能であることを表す。英語では the が definite article「定冠詞」であり、対象が必ず世界に一つしかないこと、単数であること、以前に必ず言及されたことだけを意味するわけではない。"
      },
      {
        "id": "frequency:004",
        "kind": "frequency",
        "location": "line:377",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "〈7/10〉"
      },
      {
        "id": "register:004",
        "kind": "register",
        "location": "line:379",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "文法・言語学の用語。英語学習では the と a/an、無冠詞の使い分けを説明するときに頻出する。definite は「特定の」という一般語義にも近いが、文法では指示対象を同定できるという性質を指す。"
      },
      {
        "id": "grammar_pattern:021",
        "kind": "grammar_pattern",
        "location": "line:381",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "the definite article＝定冠詞 the"
      },
      {
        "id": "grammar_pattern:022",
        "kind": "grammar_pattern",
        "location": "line:381",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "a definite noun phrase＝定名詞句"
      },
      {
        "id": "grammar_pattern:023",
        "kind": "grammar_pattern",
        "location": "line:381",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "definite reference to 〈person/thing〉＝〈人・物〉を特定して指す定の指示"
      },
      {
        "id": "grammar_pattern:024",
        "kind": "grammar_pattern",
        "location": "line:381",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "a definite description of 〈person/thing〉＝〈人・物〉を同定する確定記述"
      },
      {
        "id": "grammar_pattern:025",
        "kind": "grammar_pattern",
        "location": "line:381",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "a definite referent＝特定可能な指示対象"
      },
      {
        "id": "grammar_pattern:026",
        "kind": "grammar_pattern",
        "location": "line:381",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "a noun phrase is definite＝名詞句が定である。"
      },
      {
        "id": "collocation:024",
        "kind": "collocation",
        "location": "lines:385-388",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・the definite article\n用途: 英語の the のように、聞き手・読み手が指示対象を特定できることを示す冠詞を指す。\n例: In English, the is the definite article used before singular and plural noun phrases.\n訳: 英語では the が、単数・複数の名詞句の前に使われる定冠詞である。"
      },
      {
        "id": "collocation:025",
        "kind": "collocation",
        "location": "lines:390-393",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・a definite noun phrase\n用途: 指示対象が文脈から特定可能な名詞句を指す。\n例: In “the book on the desk,” the whole phrase is a definite noun phrase.\n訳: 「机の上のその本」では、句全体が定名詞句である。"
      },
      {
        "id": "collocation:026",
        "kind": "collocation",
        "location": "lines:395-398",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・definite reference to 〈person/thing〉\n用途: 名詞句が、文脈上どの人物・物を指すか特定できる定の指示を表す。\n例: In “the company’s earlier report,” the noun phrase has a definite reference in this context.\n訳: 「その会社の以前の報告書」では、この文脈で名詞句の指示対象が特定できる。"
      },
      {
        "id": "collocation:027",
        "kind": "collocation",
        "location": "lines:400-403",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・a definite description of 〈person/thing〉\n用途: 固有名を使わず、記述によって指示対象を同定する表現を指す。\n例: “The first person to arrive” is a definite description in this context.\n訳: この文脈では、「最初に到着した人」は確定記述である。"
      },
      {
        "id": "collocation:028",
        "kind": "collocation",
        "location": "lines:405-408",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・a definite referent\n用途: 名詞句が指し示す、文脈上特定可能な対象を指す。\n例: The plural noun phrase can still have a definite referent.\n訳: 複数名詞句でも、指示対象を特定できる場合がある。"
      },
      {
        "id": "collocation:029",
        "kind": "collocation",
        "location": "lines:410-413",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・definite and indefinite articles\n用途: the と a/an のように、指示対象の特定可能性が異なる冠詞を対比する。\n例: The lesson contrasts definite and indefinite articles in everyday sentences.\n訳: その授業では、日常文における定冠詞と不定冠詞を対比している。"
      },
      {
        "id": "usage_note:004",
        "kind": "usage_note",
        "location": "line:415",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "文法上の definite は「前に一度出た名詞」に限られない。`the door` はその場に一つしかないドアを指せるし、`the book on the desk` は修飾語によってどの本か分かるため定になる。単数か複数か、可算か不可算かも決定条件ではなく、`the books`、`the water` も定になり得る。specific は「特定のものを意図している」という意味で、`a specific book` のように不定冠詞と共存できるが、specific だから文法上 definite になるわけではない。英語の the には、種類全体を述べる `The tiger is endangered.` のような総称的用法もあるため、definite と「唯一の個体」を機械的に同一視しない。"
      },
      {
        "id": "synonym:015",
        "kind": "synonym",
        "location": "lines:419-424",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・identified\n定義: どの人物・物を指すかが分かっている、または特定されている。\n頻度: 〈9/10〉\n違い: identified は対象が同定されている状態を平易に述べる。definite は名詞句の文法的な指示性を表す用語である。\n例: The identified object was removed from the scene.\n訳: 特定された物体は現場から取り除かれた。"
      },
      {
        "id": "synonym:016",
        "kind": "synonym",
        "location": "lines:426-431",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・determinate\n定義: 境界・値・指示対象などが決まっている。\n頻度: 〈5/10〉\n違い: determinate は形式的・専門的で、definite は英語の冠詞や名詞句の性質を説明する標準用語である。\n例: The expression has a determinate meaning in this context.\n訳: その表現はこの文脈では明確に定まった意味を持つ。"
      },
      {
        "id": "synonym:017",
        "kind": "synonym",
        "location": "lines:433-438",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・specific\n定義: 一般的なものではなく、特定の人物・物・内容に関する。\n頻度: 〈10/10〉\n違い: specific は個別性を表す一般語で、文法上の definite と重なることはあるが、`a specific book` のように不定名詞句にも使える。\n例: She was looking for a specific file.\n訳: 彼女は特定のファイルを探していた。"
      },
      {
        "id": "antonym:012",
        "kind": "antonym",
        "location": "lines:442-447",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・indefinite\n定義: 名詞句の指示対象が特定できない、または特定の一つとして提示されない。\n頻度: 〈7/10〉\n違い: 文法上の indefinite は definite の直接の反対で、英語の a/an や、文脈によっては無冠詞の名詞句に関係する。\n例: “A book” is indefinite because the listener does not know which book is meant.\n訳: 「ある本」は、どの本を指すか聞き手に分からないため不定である。"
      },
      {
        "id": "antonym:013",
        "kind": "antonym",
        "location": "lines:449-454",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・unidentified\n定義: どの人物・物であるかが特定されていない。\n頻度: 〈8/10〉\n違い: unidentified は現実の対象を同定できない状態を示し、definite は文法上の名詞句が対象を特定可能に提示する状態を示す。\n例: An unidentified caller left a message.\n訳: 身元不明の発信者がメッセージを残した。"
      },
      {
        "id": "antonym:014",
        "kind": "antonym",
        "location": "lines:456-461",
        "section": "＃意味・用法・関連表現",
        "sense": "4. 【形容詞・文法用語】定の、特定できる",
        "text": "・generic\n定義: 個別の一つではなく、種類全体や一般的な概念に関する。\n頻度: 〈7/10〉\n違い: generic は指示の範囲が一般化されていることを表す。definite と対照できるが、英語では definite article が総称的に使われる場合もあるため、完全な形の反意語ではない。\n例: “Dogs are social animals” has a generic reference.\n訳: 「犬は社会的な動物だ」は総称的な指示を持つ。"
      },
      {
        "id": "sense_boundary:005",
        "kind": "sense_boundary",
        "location": "line:463",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "5. 【形容詞・植物学】有限の、定数の"
      },
      {
        "id": "definition:005",
        "kind": "definition",
        "location": "line:465",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "植物学で、花器官の数が一定で、通常は20未満で花弁数の倍数になること、または花序の主軸が花で終わり成長に限りがあることを表す専門用法である。一般語の「確実な」ではなく、数や成長が定まっているという意味で、definite inflorescence は determinate／cymose inflorescence に当たる。"
      },
      {
        "id": "frequency:005",
        "kind": "frequency",
        "location": "line:467",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "〈2/10〉"
      },
      {
        "id": "register:005",
        "kind": "register",
        "location": "line:469",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "植物学に限られる低頻度の専門語。一般の文章では通常この意味で解釈せず、専門文献で floral organs、stamens、inflorescence などと共に現れる。"
      },
      {
        "id": "grammar_pattern:027",
        "kind": "grammar_pattern",
        "location": "line:471",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "definite stamens＝数が一定の雄しべ"
      },
      {
        "id": "grammar_pattern:028",
        "kind": "grammar_pattern",
        "location": "line:471",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "a definite inflorescence＝主軸が花で終わる有限花序"
      },
      {
        "id": "grammar_pattern:029",
        "kind": "grammar_pattern",
        "location": "line:471",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "definite growth＝成長が一定の段階で止まる定限成長。"
      },
      {
        "id": "collocation:030",
        "kind": "collocation",
        "location": "lines:475-478",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "・definite stamens\n用途: 花弁数との関係で数が一定の雄しべを指す。\n例: The species has definite stamens, usually in a fixed multiple of the number of petals.\n訳: その種には、通常、花弁数の決まった倍数になる定数の雄しべがある。"
      },
      {
        "id": "collocation:031",
        "kind": "collocation",
        "location": "lines:480-483",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "・a definite inflorescence\n用途: 主軸が花で終わり、伸長に限りがある有限花序を指す。\n例: The plant develops a definite inflorescence in which the main axis ends in a flower.\n訳: その植物は、主軸が花で終わる有限花序を形成する。"
      },
      {
        "id": "collocation:032",
        "kind": "collocation",
        "location": "lines:485-488",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "・definite growth\n用途: 植物体や器官の成長が一定の段階で止まる定限成長を表す。\n例: Definite growth is common in some compact flowering plants.\n訳: 定限成長は、一部の小型の開花植物でよく見られる。"
      },
      {
        "id": "usage_note:005",
        "kind": "usage_note",
        "location": "line:490",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "この用法は一般英語の definite answer や definite plan とは別の専門的な意味である。`definite inflorescence` は花序の成長様式を指し、単に「明確な花序」という意味ではない。植物学では `indefinite` や `indeterminate` が、数や主軸の成長に固定された終点がない対照表現として使われる。"
      },
      {
        "id": "synonym:018",
        "kind": "synonym",
        "location": "lines:494-499",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "・determinate\n定義: 植物の成長・花序・器官の数などが一定の限界で決まる。\n頻度: 〈4/10〉\n違い: determinate はこの植物学上の意味でより一般的な専門語で、definite は同じ特徴を別の語彙で表す。\n例: The plant produces a determinate inflorescence.\n訳: その植物は有限花序を形成する。"
      },
      {
        "id": "synonym:019",
        "kind": "synonym",
        "location": "lines:501-506",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "・fixed-number\n定義: 数が一定に定められている。\n頻度: 〈2/10〉\n違い: fixed-number は説明的な表現で、definite stamens の特徴を言い換えるが、単独の標準用語としての使用は限定的である。\n例: The flower has a fixed number of stamens.\n訳: その花には一定数の雄しべがある。"
      },
      {
        "id": "antonym:015",
        "kind": "antonym",
        "location": "lines:510-515",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "・indefinite\n定義: 数が一定でない、または花序の成長に固定された終点がない。\n頻度: 〈3/10〉\n違い: indefinite は definite stamens や definite inflorescence の反対側にある植物学用語で、器官数や成長の上限が定まらないことを示す。\n例: An indefinite inflorescence can continue producing flowers along its main axis.\n訳: 無限花序は主軸に沿って花を作り続けることがある。"
      },
      {
        "id": "antonym:016",
        "kind": "antonym",
        "location": "lines:517-522",
        "section": "＃意味・用法・関連表現",
        "sense": "5. 【形容詞・植物学】有限の、定数の",
        "text": "・indeterminate\n定義: 成長や結果の終点があらかじめ固定されていない。\n頻度: 〈5/10〉\n違い: indeterminate は植物学で definite／determinate と対立し、主軸の成長が花で終わらないことなどを表す。\n例: The species shows indeterminate rather than definite growth.\n訳: その種は定限成長ではなく不定成長を示す。"
      }
    ],
    "relation_results": [
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
        "id": "example_translation:019",
        "kind": "example_translation",
        "target_ids": [
          "collocation:019"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:020",
        "kind": "example_translation",
        "target_ids": [
          "collocation:020"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:021",
        "kind": "example_translation",
        "target_ids": [
          "collocation:021"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:022",
        "kind": "example_translation",
        "target_ids": [
          "collocation:022"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:023",
        "kind": "example_translation",
        "target_ids": [
          "collocation:023"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:024",
        "kind": "example_translation",
        "target_ids": [
          "collocation:024"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:025",
        "kind": "example_translation",
        "target_ids": [
          "collocation:025"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:026",
        "kind": "example_translation",
        "target_ids": [
          "collocation:026"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:027",
        "kind": "example_translation",
        "target_ids": [
          "collocation:027"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:028",
        "kind": "example_translation",
        "target_ids": [
          "collocation:028"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:029",
        "kind": "example_translation",
        "target_ids": [
          "collocation:029"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:030",
        "kind": "example_translation",
        "target_ids": [
          "collocation:030"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:031",
        "kind": "example_translation",
        "target_ids": [
          "collocation:031"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。"
      },
      {
        "id": "example_translation:032",
        "kind": "example_translation",
        "target_ids": [
          "collocation:032"
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
          "antonym:003",
          "antonym:004"
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
        "id": "pattern_example_coverage:008",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:008",
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
          "synonym:009",
          "antonym:005",
          "antonym:006",
          "antonym:007"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。"
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
        "id": "pattern_example_coverage:014",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:014",
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
          "synonym:010",
          "synonym:011",
          "synonym:012",
          "synonym:013",
          "synonym:014",
          "antonym:008",
          "antonym:009",
          "antonym:010",
          "antonym:011"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。"
      },
      {
        "id": "pattern_example_coverage:015",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:015",
          "collocation:017",
          "collocation:018",
          "collocation:019",
          "collocation:020",
          "collocation:021",
          "collocation:022",
          "collocation:023"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:016",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:016",
          "collocation:017",
          "collocation:018",
          "collocation:019",
          "collocation:020",
          "collocation:021",
          "collocation:022",
          "collocation:023"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:017",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:017",
          "collocation:017",
          "collocation:018",
          "collocation:019",
          "collocation:020",
          "collocation:021",
          "collocation:022",
          "collocation:023"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:018",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:018",
          "collocation:017",
          "collocation:018",
          "collocation:019",
          "collocation:020",
          "collocation:021",
          "collocation:022",
          "collocation:023"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:019",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:019",
          "collocation:017",
          "collocation:018",
          "collocation:019",
          "collocation:020",
          "collocation:021",
          "collocation:022",
          "collocation:023"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:020",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:020",
          "collocation:017",
          "collocation:018",
          "collocation:019",
          "collocation:020",
          "collocation:021",
          "collocation:022",
          "collocation:023"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "sense_definition_consistency:004",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。"
      },
      {
        "id": "definition_usage_consistency:004",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004",
          "usage_note:004"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。"
      },
      {
        "id": "definition_lexical_relation_consistency:004",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:004",
          "definition:004",
          "synonym:015",
          "synonym:016",
          "synonym:017",
          "antonym:012",
          "antonym:013",
          "antonym:014"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。"
      },
      {
        "id": "pattern_example_coverage:021",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:021",
          "collocation:024",
          "collocation:025",
          "collocation:026",
          "collocation:027",
          "collocation:028",
          "collocation:029"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:022",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:022",
          "collocation:024",
          "collocation:025",
          "collocation:026",
          "collocation:027",
          "collocation:028",
          "collocation:029"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:023",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:023",
          "collocation:024",
          "collocation:025",
          "collocation:026",
          "collocation:027",
          "collocation:028",
          "collocation:029"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:024",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:024",
          "collocation:024",
          "collocation:025",
          "collocation:026",
          "collocation:027",
          "collocation:028",
          "collocation:029"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:025",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:025",
          "collocation:024",
          "collocation:025",
          "collocation:026",
          "collocation:027",
          "collocation:028",
          "collocation:029"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:026",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:026",
          "collocation:024",
          "collocation:025",
          "collocation:026",
          "collocation:027",
          "collocation:028",
          "collocation:029"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "sense_definition_consistency:005",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:005",
          "definition:005"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。"
      },
      {
        "id": "definition_usage_consistency:005",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:005",
          "definition:005",
          "usage_note:005"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。"
      },
      {
        "id": "definition_lexical_relation_consistency:005",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:005",
          "definition:005",
          "synonym:018",
          "synonym:019",
          "antonym:015",
          "antonym:016"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。"
      },
      {
        "id": "pattern_example_coverage:027",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:027",
          "collocation:030",
          "collocation:031",
          "collocation:032"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:028",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:028",
          "collocation:030",
          "collocation:031",
          "collocation:032"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:029",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:029",
          "collocation:030",
          "collocation:031",
          "collocation:032"
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
          "sense_boundary:003",
          "sense_boundary:004",
          "sense_boundary:005"
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
        "id": "core_sense_mapping:004",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:005",
          "sense_boundary:004",
          "definition:004",
          "usage_note:004"
        ],
        "description": "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。"
      },
      {
        "id": "core_sense_mapping:005",
        "kind": "core_sense_mapping",
        "target_ids": [
          "core_image:006",
          "sense_boundary:005",
          "definition:005",
          "usage_note:005"
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
          "core_image:005",
          "core_image:006",
          "sense_boundary:001",
          "definition:001",
          "usage_note:001",
          "sense_boundary:002",
          "definition:002",
          "usage_note:002",
          "sense_boundary:003",
          "definition:003",
          "usage_note:003",
          "sense_boundary:004",
          "definition:004",
          "usage_note:004",
          "sense_boundary:005",
          "definition:005",
          "usage_note:005"
        ],
        "description": "記事全体の語義構成、対比、訳語、限定表現から学習者が誤った一般化をしないことを横断確認する。"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "IC-definite-001",
        "surface_form": "definite",
        "frame": "a definite answer/decision/plan/date/agreement; be definite about 〈decision/position〉",
        "meaning": "答え・決定・計画・日付・合意などが確定している",
        "disposition": "included",
        "rationale": "surface_form definite の frame a definite answer/decision/plan/date/agreement は、meaning 答え・決定・計画・日付・合意などが確定しているという決定・内容の確定を表す。",
        "semantic_assertions": [
          {
            "id": "IC-definite-001-SA-001",
            "statement": "決定・計画・日付・合意の内容が現時点で定まり、仮案や未決定状態ではない。",
            "polarity": "must_hold",
            "scope": "sense 1 certainty and settlement"
          },
          {
            "id": "IC-definite-001-SA-002",
            "statement": "definite は今後絶対に変更不能であることを必須条件にしない。",
            "polarity": "must_not_hold",
            "scope": "sense 1 changeability boundary"
          }
        ]
      },
      {
        "id": "IC-definite-002",
        "surface_form": "definite",
        "frame": "a definite improvement/change/difference/effect/sign/advantage/possibility",
        "meaning": "変化・差・効果・兆候・利点などが明らかに認められる",
        "disposition": "included",
        "rationale": "surface_form definite の frame a definite improvement/change/difference/effect/sign/advantage/possibility は、meaning 変化・差・効果・兆候・利点などが明らかに認められるという観察・評価の用法を表す。",
        "semantic_assertions": [
          {
            "id": "IC-definite-002-SA-001",
            "statement": "対象の変化・差・効果・兆候などが観察や比較で明瞭に認められる。",
            "polarity": "must_hold",
            "scope": "sense 2 observable clarity"
          },
          {
            "id": "IC-definite-002-SA-002",
            "statement": "科学的因果関係の完全な証明や、可能性の確実な実現を意味しない。",
            "polarity": "must_not_hold",
            "scope": "sense 2 evidence and possibility boundary"
          }
        ]
      },
      {
        "id": "IC-definite-003",
        "surface_form": "definite",
        "frame": "a definite amount/number/period; within definite limits; definite information; a definite shape/form; a definite integral",
        "meaning": "数量・期間・範囲・内容・形などが具体的に定まっている",
        "disposition": "included",
        "rationale": "surface_form definite の frame a definite amount/number/period; within definite limits; definite information; a definite shape/form; a definite integral は、meaning 数量・期間・範囲・内容・形などが具体的に定まっているという限定・境界の用法を表す。",
        "semantic_assertions": [
          {
            "id": "IC-definite-003-SA-001",
            "statement": "対象の数量・期間・範囲・内容・形または積分区間に明確な境界や指定がある。",
            "polarity": "must_hold",
            "scope": "sense 3 specificity and limits"
          },
          {
            "id": "IC-definite-003-SA-002",
            "statement": "この用法を文法上の定性、または常に聞き手が数値を知っていることへ一般化しない。",
            "polarity": "must_not_hold",
            "scope": "sense 3 grammar and knowability boundary"
          }
        ]
      },
      {
        "id": "IC-definite-004",
        "surface_form": "definite",
        "frame": "the definite article; a definite noun phrase; definite reference; a definite description; a definite referent",
        "meaning": "文法上、名詞句の指示対象が特定可能である",
        "disposition": "included",
        "rationale": "surface_form definite の frame the definite article; a definite noun phrase; definite reference; a definite description; a definite referent は、meaning 文法上、名詞句の指示対象が特定可能であるという定性の用法を表す。",
        "semantic_assertions": [
          {
            "id": "IC-definite-004-SA-001",
            "statement": "既出・状況上の唯一性・修飾語・共有知識などにより指示対象が同定可能である。",
            "polarity": "must_hold",
            "scope": "sense 4 grammatical definiteness"
          },
          {
            "id": "IC-definite-004-SA-002",
            "statement": "definite を単数、唯一の世界内個体、または必ず先行言及済みであることと同一視しない。",
            "polarity": "must_not_hold",
            "scope": "sense 4 definiteness boundary"
          }
        ]
      },
      {
        "id": "IC-definite-005",
        "surface_form": "definite",
        "frame": "definite stamens; a definite inflorescence; definite growth",
        "meaning": "植物学で器官数や成長の終点が定まった有限・定限の",
        "disposition": "included",
        "rationale": "surface_form definite の frame definite stamens; a definite inflorescence; definite growth は、meaning 植物学で器官数や成長の終点が定まった有限・定限のという専門用法を表す。",
        "semantic_assertions": [
          {
            "id": "IC-definite-005-SA-001",
            "statement": "花器官の数または花序・成長の終点が固定される専門的特徴を指す。",
            "polarity": "must_hold",
            "scope": "sense 5 botanical usage"
          },
          {
            "id": "IC-definite-005-SA-002",
            "statement": "植物学の definite を一般英語の「明らかな」や「確実な」として解釈しない。",
            "polarity": "must_not_hold",
            "scope": "sense 5 register boundary"
          }
        ]
      },
      {
        "id": "IC-definite-006",
        "surface_form": "definitely",
        "frame": "sentence adverb; definitely + verb/adjective",
        "meaning": "確実に、間違いなく、はっきりと",
        "disposition": "included",
        "rationale": "surface_form definitely の frame sentence adverb; definitely + verb/adjective は、meaning 確実に、間違いなく、はっきりとという語形成上の関連副詞を表す。",
        "semantic_assertions": [
          {
            "id": "IC-definite-006-SA-001",
            "statement": "definitely は definite の形容詞活用形ではなく、確信を表す副詞として扱われる。",
            "polarity": "must_hold",
            "scope": "word formation definitely"
          }
        ]
      },
      {
        "id": "IC-definite-007",
        "surface_form": "definiteness",
        "frame": "noun; grammatical definiteness of a noun phrase",
        "meaning": "明確さ・確定性・文法上の定性",
        "disposition": "included",
        "rationale": "surface_form definiteness の frame noun; grammatical definiteness of a noun phrase は、meaning 明確さ・確定性・文法上の定性という語形成上の関連名詞を表す。",
        "semantic_assertions": [
          {
            "id": "IC-definite-007-SA-001",
            "statement": "definiteness は名詞句の指示対象が特定可能である性質を含む。",
            "polarity": "must_hold",
            "scope": "word formation definiteness"
          }
        ]
      },
      {
        "id": "IC-definite-008",
        "surface_form": "indefinite",
        "frame": "related adjective; indefinite period/quantity/reference",
        "meaning": "不確定な、境界や指示対象が定まらない",
        "disposition": "included",
        "rationale": "surface_form indefinite の frame related adjective; indefinite period/quantity/reference は、meaning 不確定な、境界や指示対象が定まらないという反対側の関連形を本文が明示的に扱う。",
        "semantic_assertions": [
          {
            "id": "IC-definite-008-SA-001",
            "statement": "indefinite は用法に応じて未確定・境界不明確・文法上の不定を表し、単一の一般的反意だけに固定されない。",
            "polarity": "must_hold",
            "scope": "word formation and lexical relation indefinite"
          }
        ]
      },
      {
        "id": "IC-definite-009",
        "surface_form": "definitive",
        "frame": "related adjective; definitive decision/judgment",
        "meaning": "決定的な、最終的な",
        "disposition": "included",
        "rationale": "surface_form definitive の frame related adjective; definitive decision/judgment は、meaning 決定的な、最終的なという definite より最終判断の含みが強い関連形を本文が区別して扱う。",
        "semantic_assertions": [
          {
            "id": "IC-definite-009-SA-001",
            "statement": "definitive は definite と完全な語尾違いの交換可能形ではなく、最終判断・決着の含みが強い。",
            "polarity": "must_hold",
            "scope": "word formation definitive"
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "CR-definite-001",
        "severity": "medium",
        "location": "語義1の【文法パターン】",
        "suggested_direction": "「anything definite＝何か確定したこと・情報」「nothing definite＝何も確定したことはない」のように、肯定・否定を分けて訳す。"
      },
      {
        "id": "CR-definite-002",
        "severity": "medium",
        "location": "語義3の a definite number of コロケーション",
        "suggested_direction": "訳を「研究室見学には決まった人数の学生だけが参加できる」などにし、上限を強調する場合は文脈由来の含意として注記する。"
      },
      {
        "id": "CR-definite-003",
        "severity": "medium",
        "location": "語義4の definite reference to コロケーション",
        "suggested_direction": "文法語義の例を definite reference の指示性を実際に示す文に差し替えるか、このコロケーションを一般語義側へ移して「明確な言及」と説明する。"
      }
    ],
    "evidence_checks": [
      {
        "id": "ev-definite-pronunciation"
      },
      {
        "id": "ev-definite-etymology"
      },
      {
        "id": "ev-definite-senses"
      },
      {
        "id": "ev-definite-grammar"
      },
      {
        "id": "ev-definite-botany"
      },
      {
        "id": "ev-definite-calculus"
      }
    ],
    "source_inventory_results": [
      {
        "id": "u-ca-certainty",
        "source_fact_ids": [
          "CA-01"
        ],
        "canonical_statement": "Fixed or settled status is a core general adjective sense.",
        "disposition": "integrated",
        "rationale": "Mapped to the first sense and its examples, usage note, and relations."
      },
      {
        "id": "u-ca-clarity",
        "source_fact_ids": [
          "CA-02"
        ],
        "canonical_statement": "Clear and obvious status is a distinct general adjective sense.",
        "disposition": "integrated",
        "rationale": "Mapped to the second sense and its examples, usage note, and relations."
      },
      {
        "id": "u-ca-pronunciation",
        "source_fact_ids": [
          "CA-03"
        ],
        "canonical_statement": "The headword has regional pronunciation variants with first-syllable stress.",
        "disposition": "integrated",
        "rationale": "Mapped to the pronunciation target."
      },
      {
        "id": "u-ca-usage",
        "source_fact_ids": [
          "CA-04"
        ],
        "canonical_statement": "The general learner examples align with the article's high-frequency constructional coverage.",
        "disposition": "integrated",
        "rationale": "Mapped to the general-use senses and their construction targets."
      },
      {
        "id": "u-mw-ambiguous",
        "source_fact_ids": [
          "MW-01"
        ],
        "canonical_statement": "Definite can signal absence of ambiguity, doubt, or uncertainty.",
        "disposition": "integrated",
        "rationale": "Mapped to settled and clear general senses."
      },
      {
        "id": "u-mw-limits",
        "source_fact_ids": [
          "MW-02"
        ],
        "canonical_statement": "Definite can mark distinct or certain limits and extent.",
        "disposition": "integrated",
        "rationale": "Mapped to the specific-limits sense."
      },
      {
        "id": "u-mw-grammar",
        "source_fact_ids": [
          "MW-03"
        ],
        "canonical_statement": "The grammatical sense identifies or particularizes reference.",
        "disposition": "integrated",
        "rationale": "Mapped to the grammar sense."
      },
      {
        "id": "u-mw-botany",
        "source_fact_ids": [
          "MW-04"
        ],
        "canonical_statement": "Botanical definite has a technical finite or determinate meaning.",
        "disposition": "integrated",
        "rationale": "Mapped to the botanical sense."
      },
      {
        "id": "u-mw-definitely",
        "source_fact_ids": [
          "MW-05"
        ],
        "canonical_statement": "The adverbial derivative preserves the certainty or definiteness relation.",
        "disposition": "integrated",
        "rationale": "Mapped to word formation and core-image targets."
      },
      {
        "id": "u-mw-definiteness",
        "source_fact_ids": [
          "MW-06"
        ],
        "canonical_statement": "The noun names the abstract quality corresponding to definite.",
        "disposition": "integrated",
        "rationale": "Mapped to word formation and core-image targets."
      },
      {
        "id": "u-mw-definitive",
        "source_fact_ids": [
          "MW-07"
        ],
        "canonical_statement": "A related finality word should not replace definite in every context.",
        "disposition": "integrated",
        "rationale": "Mapped to word formation and core-image targets."
      },
      {
        "id": "u-bc-reference",
        "source_fact_ids": [
          "BC-01",
          "BC-02"
        ],
        "canonical_statement": "The definite article selects a referent recoverable by speaker and listener.",
        "disposition": "integrated",
        "rationale": "Mapped to the grammar sense."
      },
      {
        "id": "u-bc-groups",
        "source_fact_ids": [
          "BC-03",
          "BC-04"
        ],
        "canonical_statement": "Definite-article interpretation depends on reference and construction, not number alone.",
        "disposition": "integrated",
        "rationale": "Mapped to the grammar sense and usage targets."
      },
      {
        "id": "u-ox-article",
        "source_fact_ids": [
          "OX-01",
          "OX-02",
          "OX-03"
        ],
        "canonical_statement": "The learner grammar reference confirms the article's terminology and referential function.",
        "disposition": "integrated",
        "rationale": "Mapped to the grammar sense."
      },
      {
        "id": "u-etym-history",
        "source_fact_ids": [
          "ET-01",
          "ET-02",
          "ET-03"
        ],
        "canonical_statement": "Historical senses connect certainty, limits, and grammatical definiteness.",
        "disposition": "integrated",
        "rationale": "Mapped to etymology, word formation, and core-image targets."
      },
      {
        "id": "u-etym-family",
        "source_fact_ids": [
          "ET-04"
        ],
        "canonical_statement": "The boundary-and-limiting word family explains the article's related-word notes.",
        "disposition": "integrated",
        "rationale": "Mapped to word formation and core-image targets."
      },
      {
        "id": "u-ka-bounds",
        "source_fact_ids": [
          "KA-01",
          "KA-02"
        ],
        "canonical_statement": "Mathematical definiteness is expressed by explicit lower and upper limits.",
        "disposition": "integrated",
        "rationale": "Mapped to the mathematical part of the specific-limits sense."
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
        "id": "word_formation:005",
        "status": null,
        "target_id": "word_formation:005"
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
        "id": "core_image:005",
        "status": null,
        "target_id": "core_image:005"
      },
      {
        "id": "core_image:006",
        "status": null,
        "target_id": "core_image:006"
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
        "id": "grammar_pattern:008",
        "status": null,
        "target_id": "grammar_pattern:008"
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
        "id": "antonym:004",
        "status": null,
        "target_id": "antonym:004"
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
        "id": "grammar_pattern:014",
        "status": null,
        "target_id": "grammar_pattern:014"
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
        "id": "synonym:009",
        "status": null,
        "target_id": "synonym:009"
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
        "id": "antonym:007",
        "status": null,
        "target_id": "antonym:007"
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
        "id": "grammar_pattern:017",
        "status": null,
        "target_id": "grammar_pattern:017"
      },
      {
        "id": "grammar_pattern:018",
        "status": null,
        "target_id": "grammar_pattern:018"
      },
      {
        "id": "grammar_pattern:019",
        "status": null,
        "target_id": "grammar_pattern:019"
      },
      {
        "id": "grammar_pattern:020",
        "status": null,
        "target_id": "grammar_pattern:020"
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
        "id": "collocation:019",
        "status": null,
        "target_id": "collocation:019"
      },
      {
        "id": "collocation:020",
        "status": null,
        "target_id": "collocation:020"
      },
      {
        "id": "collocation:021",
        "status": null,
        "target_id": "collocation:021"
      },
      {
        "id": "collocation:022",
        "status": null,
        "target_id": "collocation:022"
      },
      {
        "id": "collocation:023",
        "status": null,
        "target_id": "collocation:023"
      },
      {
        "id": "usage_note:003",
        "status": null,
        "target_id": "usage_note:003"
      },
      {
        "id": "synonym:010",
        "status": null,
        "target_id": "synonym:010"
      },
      {
        "id": "synonym:011",
        "status": null,
        "target_id": "synonym:011"
      },
      {
        "id": "synonym:012",
        "status": null,
        "target_id": "synonym:012"
      },
      {
        "id": "synonym:013",
        "status": null,
        "target_id": "synonym:013"
      },
      {
        "id": "synonym:014",
        "status": null,
        "target_id": "synonym:014"
      },
      {
        "id": "antonym:008",
        "status": null,
        "target_id": "antonym:008"
      },
      {
        "id": "antonym:009",
        "status": null,
        "target_id": "antonym:009"
      },
      {
        "id": "antonym:010",
        "status": null,
        "target_id": "antonym:010"
      },
      {
        "id": "antonym:011",
        "status": null,
        "target_id": "antonym:011"
      },
      {
        "id": "sense_boundary:004",
        "status": null,
        "target_id": "sense_boundary:004"
      },
      {
        "id": "definition:004",
        "status": null,
        "target_id": "definition:004"
      },
      {
        "id": "frequency:004",
        "status": null,
        "target_id": "frequency:004"
      },
      {
        "id": "register:004",
        "status": null,
        "target_id": "register:004"
      },
      {
        "id": "grammar_pattern:021",
        "status": null,
        "target_id": "grammar_pattern:021"
      },
      {
        "id": "grammar_pattern:022",
        "status": null,
        "target_id": "grammar_pattern:022"
      },
      {
        "id": "grammar_pattern:023",
        "status": null,
        "target_id": "grammar_pattern:023"
      },
      {
        "id": "grammar_pattern:024",
        "status": null,
        "target_id": "grammar_pattern:024"
      },
      {
        "id": "grammar_pattern:025",
        "status": null,
        "target_id": "grammar_pattern:025"
      },
      {
        "id": "grammar_pattern:026",
        "status": null,
        "target_id": "grammar_pattern:026"
      },
      {
        "id": "collocation:024",
        "status": null,
        "target_id": "collocation:024"
      },
      {
        "id": "collocation:025",
        "status": null,
        "target_id": "collocation:025"
      },
      {
        "id": "collocation:026",
        "status": null,
        "target_id": "collocation:026"
      },
      {
        "id": "collocation:027",
        "status": null,
        "target_id": "collocation:027"
      },
      {
        "id": "collocation:028",
        "status": null,
        "target_id": "collocation:028"
      },
      {
        "id": "collocation:029",
        "status": null,
        "target_id": "collocation:029"
      },
      {
        "id": "usage_note:004",
        "status": null,
        "target_id": "usage_note:004"
      },
      {
        "id": "synonym:015",
        "status": null,
        "target_id": "synonym:015"
      },
      {
        "id": "synonym:016",
        "status": null,
        "target_id": "synonym:016"
      },
      {
        "id": "synonym:017",
        "status": null,
        "target_id": "synonym:017"
      },
      {
        "id": "antonym:012",
        "status": null,
        "target_id": "antonym:012"
      },
      {
        "id": "antonym:013",
        "status": null,
        "target_id": "antonym:013"
      },
      {
        "id": "antonym:014",
        "status": null,
        "target_id": "antonym:014"
      },
      {
        "id": "sense_boundary:005",
        "status": null,
        "target_id": "sense_boundary:005"
      },
      {
        "id": "definition:005",
        "status": null,
        "target_id": "definition:005"
      },
      {
        "id": "frequency:005",
        "status": null,
        "target_id": "frequency:005"
      },
      {
        "id": "register:005",
        "status": null,
        "target_id": "register:005"
      },
      {
        "id": "grammar_pattern:027",
        "status": null,
        "target_id": "grammar_pattern:027"
      },
      {
        "id": "grammar_pattern:028",
        "status": null,
        "target_id": "grammar_pattern:028"
      },
      {
        "id": "grammar_pattern:029",
        "status": null,
        "target_id": "grammar_pattern:029"
      },
      {
        "id": "collocation:030",
        "status": null,
        "target_id": "collocation:030"
      },
      {
        "id": "collocation:031",
        "status": null,
        "target_id": "collocation:031"
      },
      {
        "id": "collocation:032",
        "status": null,
        "target_id": "collocation:032"
      },
      {
        "id": "usage_note:005",
        "status": null,
        "target_id": "usage_note:005"
      },
      {
        "id": "synonym:018",
        "status": null,
        "target_id": "synonym:018"
      },
      {
        "id": "synonym:019",
        "status": null,
        "target_id": "synonym:019"
      },
      {
        "id": "antonym:015",
        "status": null,
        "target_id": "antonym:015"
      },
      {
        "id": "antonym:016",
        "status": null,
        "target_id": "antonym:016"
      }
    ],
    "relation_results": [
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
        "id": "example_translation:019",
        "status": null,
        "relation_id": "example_translation:019"
      },
      {
        "id": "example_translation:020",
        "status": null,
        "relation_id": "example_translation:020"
      },
      {
        "id": "example_translation:021",
        "status": null,
        "relation_id": "example_translation:021"
      },
      {
        "id": "example_translation:022",
        "status": null,
        "relation_id": "example_translation:022"
      },
      {
        "id": "example_translation:023",
        "status": null,
        "relation_id": "example_translation:023"
      },
      {
        "id": "example_translation:024",
        "status": null,
        "relation_id": "example_translation:024"
      },
      {
        "id": "example_translation:025",
        "status": null,
        "relation_id": "example_translation:025"
      },
      {
        "id": "example_translation:026",
        "status": null,
        "relation_id": "example_translation:026"
      },
      {
        "id": "example_translation:027",
        "status": null,
        "relation_id": "example_translation:027"
      },
      {
        "id": "example_translation:028",
        "status": null,
        "relation_id": "example_translation:028"
      },
      {
        "id": "example_translation:029",
        "status": null,
        "relation_id": "example_translation:029"
      },
      {
        "id": "example_translation:030",
        "status": null,
        "relation_id": "example_translation:030"
      },
      {
        "id": "example_translation:031",
        "status": null,
        "relation_id": "example_translation:031"
      },
      {
        "id": "example_translation:032",
        "status": null,
        "relation_id": "example_translation:032"
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
        "id": "pattern_example_coverage:008",
        "status": null,
        "relation_id": "pattern_example_coverage:008"
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
        "id": "pattern_example_coverage:014",
        "status": null,
        "relation_id": "pattern_example_coverage:014"
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
        "id": "pattern_example_coverage:017",
        "status": null,
        "relation_id": "pattern_example_coverage:017"
      },
      {
        "id": "pattern_example_coverage:018",
        "status": null,
        "relation_id": "pattern_example_coverage:018"
      },
      {
        "id": "pattern_example_coverage:019",
        "status": null,
        "relation_id": "pattern_example_coverage:019"
      },
      {
        "id": "pattern_example_coverage:020",
        "status": null,
        "relation_id": "pattern_example_coverage:020"
      },
      {
        "id": "sense_definition_consistency:004",
        "status": null,
        "relation_id": "sense_definition_consistency:004"
      },
      {
        "id": "definition_usage_consistency:004",
        "status": null,
        "relation_id": "definition_usage_consistency:004"
      },
      {
        "id": "definition_lexical_relation_consistency:004",
        "status": null,
        "relation_id": "definition_lexical_relation_consistency:004"
      },
      {
        "id": "pattern_example_coverage:021",
        "status": null,
        "relation_id": "pattern_example_coverage:021"
      },
      {
        "id": "pattern_example_coverage:022",
        "status": null,
        "relation_id": "pattern_example_coverage:022"
      },
      {
        "id": "pattern_example_coverage:023",
        "status": null,
        "relation_id": "pattern_example_coverage:023"
      },
      {
        "id": "pattern_example_coverage:024",
        "status": null,
        "relation_id": "pattern_example_coverage:024"
      },
      {
        "id": "pattern_example_coverage:025",
        "status": null,
        "relation_id": "pattern_example_coverage:025"
      },
      {
        "id": "pattern_example_coverage:026",
        "status": null,
        "relation_id": "pattern_example_coverage:026"
      },
      {
        "id": "sense_definition_consistency:005",
        "status": null,
        "relation_id": "sense_definition_consistency:005"
      },
      {
        "id": "definition_usage_consistency:005",
        "status": null,
        "relation_id": "definition_usage_consistency:005"
      },
      {
        "id": "definition_lexical_relation_consistency:005",
        "status": null,
        "relation_id": "definition_lexical_relation_consistency:005"
      },
      {
        "id": "pattern_example_coverage:027",
        "status": null,
        "relation_id": "pattern_example_coverage:027"
      },
      {
        "id": "pattern_example_coverage:028",
        "status": null,
        "relation_id": "pattern_example_coverage:028"
      },
      {
        "id": "pattern_example_coverage:029",
        "status": null,
        "relation_id": "pattern_example_coverage:029"
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
        "id": "core_sense_mapping:004",
        "status": null,
        "relation_id": "core_sense_mapping:004"
      },
      {
        "id": "core_sense_mapping:005",
        "status": null,
        "relation_id": "core_sense_mapping:005"
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
        "id": "IC-definite-001",
        "status": null,
        "assertion_ids": [
          "IC-definite-001-SA-001",
          "IC-definite-001-SA-002"
        ],
        "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "IC-definite-002",
        "status": null,
        "assertion_ids": [
          "IC-definite-002-SA-001",
          "IC-definite-002-SA-002"
        ],
        "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "IC-definite-003",
        "status": null,
        "assertion_ids": [
          "IC-definite-003-SA-001",
          "IC-definite-003-SA-002"
        ],
        "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "IC-definite-004",
        "status": null,
        "assertion_ids": [
          "IC-definite-004-SA-001",
          "IC-definite-004-SA-002"
        ],
        "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "IC-definite-005",
        "status": null,
        "assertion_ids": [
          "IC-definite-005-SA-001",
          "IC-definite-005-SA-002"
        ],
        "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "IC-definite-006",
        "status": null,
        "assertion_ids": [
          "IC-definite-006-SA-001"
        ],
        "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "IC-definite-007",
        "status": null,
        "assertion_ids": [
          "IC-definite-007-SA-001"
        ],
        "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "IC-definite-008",
        "status": null,
        "assertion_ids": [
          "IC-definite-008-SA-001"
        ],
        "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      },
      {
        "id": "IC-definite-009",
        "status": null,
        "assertion_ids": [
          "IC-definite-009-SA-001"
        ],
        "verified_body_sha256": "fcb08ac47dc55a7ef50022fe8615ddb12b921fe50d617dd4577843cb068b99bf"
      }
    ],
    "finding_results": [
      {
        "id": "CR-definite-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "CR-definite-002",
        "status": null,
        "notes": ""
      },
      {
        "id": "CR-definite-003",
        "status": null,
        "notes": ""
      }
    ],
    "evidence_checks": [
      {
        "id": "ev-definite-pronunciation",
        "status": null
      },
      {
        "id": "ev-definite-etymology",
        "status": null
      },
      {
        "id": "ev-definite-senses",
        "status": null
      },
      {
        "id": "ev-definite-grammar",
        "status": null
      },
      {
        "id": "ev-definite-botany",
        "status": null
      },
      {
        "id": "ev-definite-calculus",
        "status": null
      }
    ],
    "source_inventory_results": [
      {
        "id": "u-ca-certainty",
        "status": null,
        "union_id": "u-ca-certainty"
      },
      {
        "id": "u-ca-clarity",
        "status": null,
        "union_id": "u-ca-clarity"
      },
      {
        "id": "u-ca-pronunciation",
        "status": null,
        "union_id": "u-ca-pronunciation"
      },
      {
        "id": "u-ca-usage",
        "status": null,
        "union_id": "u-ca-usage"
      },
      {
        "id": "u-mw-ambiguous",
        "status": null,
        "union_id": "u-mw-ambiguous"
      },
      {
        "id": "u-mw-limits",
        "status": null,
        "union_id": "u-mw-limits"
      },
      {
        "id": "u-mw-grammar",
        "status": null,
        "union_id": "u-mw-grammar"
      },
      {
        "id": "u-mw-botany",
        "status": null,
        "union_id": "u-mw-botany"
      },
      {
        "id": "u-mw-definitely",
        "status": null,
        "union_id": "u-mw-definitely"
      },
      {
        "id": "u-mw-definiteness",
        "status": null,
        "union_id": "u-mw-definiteness"
      },
      {
        "id": "u-mw-definitive",
        "status": null,
        "union_id": "u-mw-definitive"
      },
      {
        "id": "u-bc-reference",
        "status": null,
        "union_id": "u-bc-reference"
      },
      {
        "id": "u-bc-groups",
        "status": null,
        "union_id": "u-bc-groups"
      },
      {
        "id": "u-ox-article",
        "status": null,
        "union_id": "u-ox-article"
      },
      {
        "id": "u-etym-history",
        "status": null,
        "union_id": "u-etym-history"
      },
      {
        "id": "u-etym-family",
        "status": null,
        "union_id": "u-etym-family"
      },
      {
        "id": "u-ka-bounds",
        "status": null,
        "union_id": "u-ka-bounds"
      }
    ],
    "input_revision_id": "d8f943d9e0354e1c8aab61894637118803b6325893c5f6289a8188bf9922d895"
  },
  "input_bindings": {
    "pass_findings.json": "1e826ad965af4b9c41e334b74d0695090ee0b634debc2f630433898b8f72e447",
    "cold_review.json": "f34adbe8b00ed9b6318f0bc686bd6cd94d2aff6d93a02276f26862c348992b7e",
    "final_blind.json": "1d53fa8d0d62d18949a74d88f95c43a795c520e4620a65332c6f313ee190f517",
    "blind_seal.json": "2a1ae54ab9598745aeda30db1902cfec84883610cf1b0afb6b26e94838f8bd9a",
    "pre_blind_resolution.json": "8ab148d3af5c237c6ff458b4cfdefca18a17ffbd6ff62d09fbc8ed413f8173fd",
    "pre_blind_revision.json": "6b6ea89c9f350bfc167f47c774155908da9044aa654a4017efd04b718b5b124f",
    "checker_recheck_manifest.json": "78b4288e3e6883572f76b401a801e07a50a5f38fc9f2e44101313f4d2a2535c9",
    "post_blind_resolution.json": "e33350b45aa997f1dc39f36b82a9aabb8d3aa5e71c1dc788ca8a78d1a149472a",
    "post_blind_verification.json": "d3f6f0c30927267fc5f4e7d8d2dd7f5b4d7a662a6a7c76100885a99430fc8c84",
    "targeted_adjudications.json": "af5af9b139e61078d584a712c70a3ce285f0407cc7fa63836b8195db9ea9f3b6",
    "source_inventory.json": "1c8540154c4ee3458d231b2e221e5d2e27f46b392fe90c236daf0fea71ee4163",
    "resolutions.json": "a5563454a78361d13645641b3cb30e52953daf7a0af814372e2d38e48eb50524",
    "check_passes/checker_passes.stage1.json": "fd66a0bfb49eccb36724576dfe58e31cd1d52e22d226b402b4fd64626c1e03bc",
    "check_passes/evidence.json": "7a341309121f9854eb121086e52012f5471789e945f9dfd221746219cc6629aa",
    "check_passes/evidence.request.json": "78a9bac203097e87c0adcf8d4fc74e8a9219fd630a4c28c32761a8171e943f8e",
    "check_passes/example-attribution.alignment-key.json": "3d67272b123c12ce6490f93a1789edccfce285d4378d964f08c87c36be42dbf7",
    "check_passes/example-attribution.blind-record.json": "f4399f0b06d3f73d36c2668462b27b60262374b0b2a4abee88f20fd2bcd9551f",
    "check_passes/example-attribution.json": "52512ef4ed0420f84badbb79ef965a404f2c92288ad35ccf005e4fb1113f2da1",
    "check_passes/example-attribution.request.json": "91b7400312cb6ca1f45d90fe0601de0aa308c38916ca09017658b1f27202b24c",
    "check_passes/frame-relation.antonym-axis.adjudication-record.json": "eabbb56d53bd0b9f871ab41c07d1dd41030ea7246bd19787282e8a11b6401567",
    "check_passes/frame-relation.antonym-axis.alignment-key.json": "ce21de0a57d02f63d67c8c4a817ed20e333d441801158057ad9824511e26044d",
    "check_passes/frame-relation.antonym-axis.blind-record.json": "1475a35fcceb6280575c4b79b8e4c010bf27708d41861fc363bbfc57e65dbbfe",
    "check_passes/frame-relation.antonym-axis.stage2.request.json": "f8557ec9c473681be81ae8bb59bd4a70bac89e652db0d22cd09f41b6dd12a110",
    "check_passes/frame-relation.request.json": "79c1b5a928729d4849c7e709262d848221772471f347f3130242953177eeb4a0",
    "check_passes/input_snapshot.json": "ad9552068547d56a9443ed89c6ed14916af849944a29e6ae737989745a9ee393",
    "check_passes/pronunciation.json": "a45aaa57215966e5792087af435bfdf8a3c7c02f49ad62c321daa0f7338ad617",
    "check_passes/pronunciation.request.json": "b9bff05686a98c678586e7389c2ebf40e91463c58580ebf5e6f7958c9a946a85",
    "check_passes/qualification.json": "a1995ee66452cd51d671d45098011075584ac3bd1c874acdb3951ccfb9f947a9",
    "check_passes/qualification.request.json": "11ca6be3f2adeb55ed1d59462c68799e6ba7259fd02eae17f7b308646f7c69b9",
    "check_passes/sense-structure.json": "7f2c710503ce47883441745a67c38f372841c718a91ddf696159f5d7db416ed5",
    "check_passes/sense-structure.request.json": "38720d4d3b4d24d5deeafc4ae782a5505dd433aa521fc5e9dc65202fd0e8d47e",
    "check_passes/translation.json": "f39686636d1daa7752f8bf8b603d9fc3cb8085fa11a5fc974b43d4b51fc86c1b",
    "check_passes/translation.request.json": "c666931d13fd8b591a51ce87923c271ec25c95b375c6b70c1a43ae6ccc59c51b"
  },
  "contract_version": "review_preflight_v1",
  "input_revision_id": "d8f943d9e0354e1c8aab61894637118803b6325893c5f6289a8188bf9922d895"
}
```
