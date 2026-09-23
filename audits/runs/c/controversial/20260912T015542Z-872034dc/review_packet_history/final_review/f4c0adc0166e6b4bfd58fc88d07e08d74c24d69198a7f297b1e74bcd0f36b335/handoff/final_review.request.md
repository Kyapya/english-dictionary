# Independent review handoff

Stage: `final_review`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session.

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
  "entry_body": "\n＃発音記号\n\n米: /ˌkɑːntrəˈvɝːʃəl/｜英: /ˌkɒntrəˈvɜːʃəl/。米英とも4音節で、第3音節の /vɝː/・/vɜː/ に主強勢がある。第1音節の /ˌkɑːn/・/ˌkɒn/ には副次強勢を示す。米語では /ˌkɑːntrəˈvɝːsiəl/ に近い5音節寄りの発音も聞かれるが、通常の学習上は /ˈvɝːʃəl/・/ˈvɜːʃəl/ の部分を基準にする。  \n\n＃語源\n\n16世紀後半に使われ始めた語で、後期ラテン語 controversialis「論争に関する」から来た。controversia「論争」は controversus「反対方向に向けられた、争われた」に関係し、contra-/contro-「反対に」と versus「向けられた、転じた」（vertere「向きを変える」の過去分詞）に分けて考えられる。初出年代は資料により1580年代、1583年、1575–85年など差があるため、特定の年として暗記しない。  \n\n＃語形成\n\n・controversy：名詞。「論争、論争点、物議」。controversial と同じ語族の中心語で、public controversy のように使う。  \n・controversially：副詞。「物議を醸す形で、論争を呼ぶことに」。文全体や発言・判断の仕方を修飾する。  \n・controversialist：名詞。「論争家、論争に加わる人」。人の性向または論争上の立場を指す硬めの語。  \n・controvert：動詞。「反論する、論駁する」。controversial と意味は近いが、現代英語では controversial の直接の活用形ではなく、別の動詞として扱う。  \n\n＃意味・用法・関連表現\n\n1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す\n\n【日本語訳・定義】政策・決定・主張・作品・発言・人物などが、社会全体または特定の集団の中で、強い意見の対立、批判、反対を引き起こしていることを表す。事実として真偽が決まっていないことを必ずしも含まず、悪い、違法、意図的に挑発的だという意味でもない。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準語で、会話・ニュース・政治・文化・学術・ビジネスの文章まで広く使う。controversial は「多くの人が反対している」と同じではなく、賛成・反対の議論が強く起きている状態を指す。  \n\n【文法パターン】be/become/remain/prove controversial＝論争を呼ぶ・論争の的であり続ける・結果的に物議を醸す／a controversial 〈issue・decision・policy・claim・statement・figure・book・film〉＝論争を呼ぶ〈問題・決定・政策・主張・発言・人物・本・映画〉／highly/widely controversial＝非常に／広く物議を醸す／controversial among/within 〈group〉＝〈集団〉の間で論争を呼ぶ／controversial in some circles＝一部の界隈では物議を醸す／it remains controversial whether ...＝…かどうかは依然として議論が分かれる／be controversial enough to do＝～するほど物議を醸す／too controversial to do＝物議を醸しすぎて～できない。  \n\n【コロケーション】\n\n・a controversial issue  \n用途: 社会的に賛否が対立している問題を指す。  \n例: The use of facial-recognition technology remains a controversial issue.  \n訳: 顔認証技術の利用は依然として論争を呼ぶ問題だ。  \n\n・a controversial decision  \n用途: 決定の妥当性や影響をめぐって強い反対・批判が出ていることを表す。  \n例: The committee made a controversial decision to cancel the exhibition.  \n訳: 委員会は展示会を中止するという物議を醸す決定を下した。  \n\n・a controversial figure  \n用途: 功績と批判の両方があり、評価が大きく割れている人物を指す。  \n例: The historian remains a controversial figure in the region.  \n訳: その歴史家はその地域で今も評価が大きく分かれる人物だ。  \n\n・a highly controversial proposal  \n用途: 提案に対して非常に強い賛否や反発が起きていることを強調する。  \n例: The city council postponed a highly controversial proposal.  \n訳: 市議会は非常に物議を醸している提案を延期した。  \n\n・controversial among 〈group〉  \n用途: どの集団の中で意見が割れているかを限定する。  \n例: The interpretation is controversial among constitutional scholars.  \n訳: その解釈は憲法学者の間で議論が分かれている。  \n\n・controversial in some circles  \n用途: 社会全体ではなく、特定の界隈で物議を醸していることを示す。  \n例: The advertising campaign is controversial in some circles but popular with younger viewers.  \n訳: その広告キャンペーンは一部では物議を醸しているが、若い視聴者には人気がある。  \n\n・it remains controversial whether ...  \n用途: 判断が現在も決着していないことを述べる。  \n例: It remains controversial whether the policy reduced inequality.  \n訳: その政策が格差を縮小したかどうかは、今も議論が分かれている。  \n\n・a controversial remark  \n用途: 発言が批判や反発を招く内容だったことを表す。  \n例: The minister's controversial remark drew criticism from both parties.  \n訳: 大臣の物議を醸す発言は両党から批判を招いた。  \n\n・become controversial after ...  \n用途: 当初は普通だった対象が、後から知られた事実や変化によって論争の的になることを表す。  \n例: The renovation plan became controversial after residents learned the full cost.  \n訳: 住民が総費用を知った後、その改修計画は物議を醸すようになった。  \n\n【語法・注意】対象を主語にした be controversial は「その対象が論争の的だ」という意味で、必ずしも対象自身が議論を仕掛けるわけではない。人物についても通常は「評価が割れている人物」の意味であり、「論争を好む人」という性向を言いたいときは語義2を確認する。highly は対立の強さ、widely は論争が広い範囲に及ぶことを示す。controversial を「間違った」「受け入れられない」と自動的に訳さず、何が誰の間で争われているかを among/within 句や文脈で補う。  \n\n【類義語】\n\n・contentious  \n定義: 議論や対立を引き起こしやすい、争点になっている。  \n頻度: 〈8/10〉  \n違い: contentious は問題・決定が争いを生みやすい性質や、当事者間の対立の強さに焦点があり、controversial より対立的に響くことがある。  \n例: The contentious issue delayed the negotiations for weeks.  \n訳: その対立を招く争点のために、交渉は何週間も遅れた。  \n\n・disputed  \n定義: 真偽・権利・解釈などが争われている、意見が一致していない。  \n頻度: 〈8/10〉  \n違い: disputed は「正しいか、誰のものかなどが争われている」という未確定性を強調し、controversial のような広い世論上の物議まで必ずしも含まない。  \n例: The map shows the disputed border in a different color.  \n訳: その地図は争われている国境を別の色で示している。  \n\n・debatable  \n定義: 議論の余地があり、結論を一つに決めにくい。  \n頻度: 〈7/10〉  \n違い: debatable は主張や判断の妥当性を論じられることに焦点があり、controversial より感情的な反発や大きな社会的対立を含まない場合が多い。  \n例: Whether the change improved efficiency is debatable.  \n訳: その変更が効率を高めたかどうかは議論の余地がある。  \n\n・polarizing  \n定義: 人々を賛成側と反対側へ大きく分断する。  \n頻度: 〈7/10〉  \n違い: polarizing は意見の対立を二極化させる効果を強調する。controversial は意見が割れていても、二つの陣営に明確に分かれるとは限らない。  \n例: The candidate's polarizing speech dominated the news cycle.  \n訳: その候補者の社会を二極化させる演説が報道を席巻した。  \n\n・provocative  \n定義: 強い反応や議論を意図的または効果として引き起こす、挑発的な。  \n頻度: 〈8/10〉  \n違い: provocative は発言者・作者が反応を誘う性質や意図に焦点がある。controversial は実際に物議が生じている状態を表し、意図を必要としない。  \n例: The artist is known for provocative questions about public memory.  \n訳: その芸術家は公共の記憶について挑発的な問いを投げかけることで知られている。  \n\n・divisive  \n定義: 人々や集団の間に深い対立を生じさせる、分断を招く。  \n頻度: 〈7/10〉  \n違い: divisive は社会的な分断や関係悪化という結果を強く示す。controversial は分断に至らず、単に議論や批判を招く場合にも使える。  \n例: The divisive reform split the professional association.  \n訳: その分断を招く改革は専門職団体を二分した。  \n\n・polemical  \n定義: 論争を仕掛ける、または論争的な主張を展開する。  \n頻度: 〈4/10〉  \n違い: polemical は文章・議論・論者の攻撃的な論争スタイルに寄りやすく、controversial より硬く、意図的な論争性を含みやすい。  \n例: The book adopts a polemical tone toward established theories.  \n訳: その本は確立した理論に対して論争的な調子を取っている。  \n\n【反意語】\n\n・uncontroversial  \n定義: 意見の強い対立や広い反発を招かない、異論の少ない。  \n頻度: 〈6/10〉  \n違い: controversial の直接的な反対語で、問題・判断・人物などについて大きな論争が起きていない状態を表す。  \n例: The committee reached an uncontroversial agreement on the timetable.  \n訳: 委員会は日程について異論の少ない合意に達した。  \n\n・noncontroversial  \n定義: 論争的でない、特に意見の対立を起こさない。  \n頻度: 〈5/10〉  \n違い: noncontroversial も直接的な反対語だが、uncontroversial より説明的・形式的に見えることがある。  \n例: The report limits itself to noncontroversial background facts.  \n訳: その報告書は論争のない背景事実に内容を限定している。  \n\n2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な\n\n【日本語訳・定義】人が性格や態度の傾向として、議論を好んだり、既存の立場に反論して対立を生みやすかったりすることを表す。辞書に記載される低頻度の語義で、現代の controversial person は通常、語義1の「論争の的となっている人物」と解釈される。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】まれで、辞書的・形式的・文学的な説明に現れやすい。現代の一般的な文章で人の性向を表すなら argumentative、disputatious、polemical の方が意味を明確にしやすい。  \n\n【文法パターン】a controversial temperament＝論争を好む気質／a controversial manner＝対立を生みやすい態度／be controversial by temperament＝性向として論争的である／be controversial in debate＝議論で意図的に反論を重ねる。  \n\n【コロケーション】\n\n・a controversial temperament  \n用途: 人が性格的に議論や対立を好むことを、まれな形容詞用法で表す。  \n例: The columnist has a controversial temperament and treats every meeting as a public debate.  \n訳: そのコラムニストは論争を好む気質で、どの会議も公開討論のように扱う。  \n\n・a controversial manner  \n用途: 人が対立を招きやすい仕方で話したり振る舞ったりすることを表す。  \n例: Her controversial manner turned minor technical disagreements into public arguments.  \n訳: 彼女の対立を生みやすい態度は、ささいな技術上の意見の違いまで公の論争に変えた。  \n\n・be controversial by temperament  \n用途: 物議を醸す個別の行動ではなく、もともとの性向が論争的だと述べるまれな構文。  \n例: He was controversial by temperament, challenging even minor points in every debate.  \n訳: 彼は性向として論争的で、どの討論でもささいな点にまで反論した。  \n\n・be controversial in debate  \n用途: 議論の最中に、立場そのものよりも反論を重ねる性向が目立つことを表す。  \n例: The speaker was controversial in debate because he deliberately attacked each established position.  \n訳: その話者は確立した立場を一つ一つ意図的に攻撃したため、討論では論争的だった。  \n\n【語法・注意】この語義では controversial が人の性向を直接表すが、現代の「論争の的となる人物」という普通の解釈と形が同じなので、文脈で区別する必要がある。a controversial politician は通常語義1であり、気質を明示する temperament、manner、by temperament などがあって初めて語義2に近づく。意見が割れているだけなら語義1、本人が反論・対立を好むことまで言うなら語義2である。  \n\n【類義語】\n\n・disputatious  \n定義: 議論や口論を好む、論争好きな。  \n頻度: 〈4/10〉  \n違い: disputatious は人の性向そのものを表す明確な語で、controversial のまれな語義より自然に「口論好き」の意味を示す。  \n例: His disputatious nature made routine committee work exhausting.  \n訳: 彼の論争好きな性質のため、通常の委員会業務は疲れるものになった。  \n\n・argumentative  \n定義: すぐに反論する、議論好きな、口論を招く。  \n頻度: 〈7/10〉  \n違い: argumentative は日常的で、人が何にでも反論する傾向を表す。controversial より口論・反論の行動が前面に出る。  \n例: The child became argumentative whenever the rules were explained.  \n訳: その子は規則を説明されるといつも反論するようになった。  \n\n・polemical  \n定義: 論争を仕掛ける、攻撃的に論争する。  \n頻度: 〈4/10〉  \n違い: polemical は論者・文章・議論の意図的で攻撃的な論争性に焦点があり、controversial より文語的である。  \n例: The polemical writer challenged every compromise proposed by the panel.  \n訳: その論争的な筆者は、委員会が提案した妥協案すべてに異議を唱えた。  \n\n・contentious  \n定義: 対立的で、争いを引き起こしやすい。  \n頻度: 〈8/10〉  \n違い: contentious は人の態度にも使えるが、敵対的・喧嘩腰の含みが出やすい。controversial の語義2は、必ずしも敵意や攻撃性まで含まない。  \n例: The manager's contentious style made open discussion difficult.  \n訳: その管理職の対立的なスタイルは、率直な話し合いを難しくした。  ",
  "_output_metadata": {
    "schema_version": "final_review_v3",
    "stage": "final_review",
    "run_id": "blind-controversial-20260912T015542Z-872034dc",
    "context_id": "blind-controversial-context-20260912T015542Z-872034dc",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "prompt_sha256": "7fee3a9d388e6557c2d8a66702e890b2398ca20228e61072acc81eedafcfac9d",
    "input_artifacts": [
      "entry_body",
      "sealed_final_blind",
      "pre_blind_resolution",
      "post_blind_resolution",
      "checker_recheck_manifest",
      "targeted_adjudications",
      "final_review_spec"
    ],
    "blind_output_sha256": "455ef8e05e5ee529d434bfbbbe0cce1d335089c102a325e4bfcaa02ab80bef58"
  },
  "pass_findings": {
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-controversial-20260912T015542Z-872034dc",
    "context_id": "normal-controversial-context-20260912T015542Z-872034dc",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "prompt_sha256": "0b485ac494ff9f114a9061bbc7d789803f05ee6d79b908885efae2da2b0cebf5",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-09-12T02:26:39.106604+00:00",
    "pass_outputs": [
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "translation",
        "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "codex-gpt-5",
          "ingested_by": "orchestrator",
          "agent_id": "controversial-checker-translation-20260912T015542Z-872034dc",
          "same_model_as_generation": true,
          "source_response": {
            "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/ba96d2ae3e21d4fc24462e91c6f3d2b7bd2f65e16e95c2943805452d9d352436.json",
            "sha256": "ba96d2ae3e21d4fc24462e91c6f3d2b7bd2f65e16e95c2943805452d9d352436"
          }
        }
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "sense-structure",
        "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "codex-gpt-5",
          "ingested_by": "orchestrator",
          "agent_id": "controversial-checker-sense-structure-20260912T015542Z-872034dc",
          "same_model_as_generation": true,
          "source_response": {
            "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/a8ddf8126a94a8670e8c02512ae557a48a61a1b8d9e903a06615ada9486af0fc.json",
            "sha256": "a8ddf8126a94a8670e8c02512ae557a48a61a1b8d9e903a06615ada9486af0fc"
          }
        }
      },
      {
        "pass_id": "frame-relation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "codex-gpt-5",
          "ingested_by": "orchestrator",
          "agent_id": "controversial-checker-frame-axis-20260912T015542Z-872034dc",
          "same_model_as_generation": true,
          "source_response": {
            "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/f6939539550b34ba6e5fdf95c99988b984f8c507aa7a7d497ce9ad94c930c22e.json",
            "sha256": "f6939539550b34ba6e5fdf95c99988b984f8c507aa7a7d497ce9ad94c930c22e"
          }
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
          "blind_request_sha256": "a8571c606a5b65fde1bda9ca43c3af9db0eda2c0023b6c6059b42b9173c7c8c6",
          "recorded_at": "2026-09-12T02:20:00Z",
          "axes": [
            {
              "item_id": "ant-9155f1ca66db",
              "axis": "状態",
              "relation_type": "状態",
              "reason": "The adjective contrasts a state of being publicly disputed with a state in which that dispute is absent."
            },
            {
              "item_id": "ant-5e1d39a9d098",
              "axis": "状態",
              "relation_type": "状態",
              "reason": "The negative adjective describes the corresponding noncontroversial state rather than a higher or lower degree of controversy."
            }
          ],
          "reviewer": {
            "mode": "handoff",
            "declared_model": "codex-gpt-5",
            "ingested_by": "orchestrator",
            "agent_id": "controversial-checker-frame-axis-20260912T015542Z-872034dc",
            "same_model_as_generation": true,
            "source_response": {
              "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/21356adf71480e433f79a4d820763e3b11bb2990e51dff13121d59cd4c817b09.json",
              "sha256": "21356adf71480e433f79a4d820763e3b11bb2990e51dff13121d59cd4c817b09"
            }
          }
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
          "stage2_request_sha256": "cf431694b21a1251afc6c6af3861a823d11ea212edfef57559836461893e0030",
          "blind_record_sha256": "7982b752e545a329ab06e389ce7d9dd69d2ed38b682e987daeb43d186eebedce",
          "adjudications": [
            {
              "item_id": "ant-9155f1ca66db",
              "flags": [],
              "rationale": "The state axis is appropriate: uncontroversial is the direct absence-of-dispute counterpart for controversial in this sense, and the article's difference line is accurate.",
              "suggested_direction": null
            },
            {
              "item_id": "ant-5e1d39a9d098",
              "flags": [],
              "rationale": "The state axis is appropriate: noncontroversial names the same absence of public dispute, with a more formal or explanatory register, so no relation correction is needed.",
              "suggested_direction": null
            }
          ],
          "frame_findings": [],
          "unrouted_observations": [],
          "reviewer": {
            "mode": "handoff",
            "declared_model": "codex-gpt-5",
            "ingested_by": "orchestrator",
            "agent_id": "controversial-checker-frame-axis-20260912T015542Z-872034dc",
            "same_model_as_generation": true,
            "source_response": {
              "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/f6939539550b34ba6e5fdf95c99988b984f8c507aa7a7d497ce9ad94c930c22e.json",
              "sha256": "f6939539550b34ba6e5fdf95c99988b984f8c507aa7a7d497ce9ad94c930c22e"
            }
          }
        },
        "aligned_at": "2026-09-12T02:27:45.032647+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "codex-gpt-5",
          "ingested_by": "orchestrator",
          "agent_id": "controversial-checker-example-attribution-20260912T015542Z-872034dc",
          "same_model_as_generation": true,
          "source_response": {
            "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/fb876f521ed92c9e0bc5a6a453f31e1cc6a84582669bc0a2af1d98f49d6b136a.json",
            "sha256": "fb876f521ed92c9e0bc5a6a453f31e1cc6a84582669bc0a2af1d98f49d6b136a"
          }
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "stage": 1,
          "pass_id": "example-attribution",
          "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
          "blind_request_sha256": "4df720e3fec5307bd134bfcf73471fda85cea13c9f7d32fb458aa3dd67981f81",
          "recorded_at": "2026-09-12T02:20:10Z",
          "attributions": [
            {
              "example_id": "ex-ac1f37066679",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "policy"
              ],
              "rationale": "The term policy identifies a public decision or program being evaluated for disagreement, which fits sense:001."
            },
            {
              "example_id": "ex-4b69ba5d4c7d",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "manner"
              ],
              "rationale": "The term manner makes the adjective describe a person's habitual way of behaving, supporting the rare sense:002."
            },
            {
              "example_id": "ex-521917da671b",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "proposal"
              ],
              "rationale": "The term proposal identifies an object of public approval or opposition, supporting sense:001."
            },
            {
              "example_id": "ex-1ae410060fc9",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "advertising"
              ],
              "rationale": "The term advertising frames the campaign as a public work receiving mixed reactions, supporting sense:001."
            },
            {
              "example_id": "ex-e9c0f853bc9b",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "decision"
              ],
              "rationale": "The term decision names an institutional choice that can attract criticism, supporting sense:001."
            },
            {
              "example_id": "ex-4cbe0301a48f",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "renovation"
              ],
              "rationale": "The term renovation identifies a plan whose cost creates public disagreement, supporting sense:001."
            },
            {
              "example_id": "ex-685e754c92c7",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "temperament"
              ],
              "rationale": "The term temperament explicitly presents controversy as a stable personal disposition, supporting sense:002."
            },
            {
              "example_id": "ex-2b864bd448fb",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "deliberately"
              ],
              "rationale": "The term deliberately signals a person's repeated choice to attack established positions, supporting sense:002."
            },
            {
              "example_id": "ex-e74721a3133b",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "historian"
              ],
              "rationale": "The term historian identifies a public figure whose reputation is disputed, supporting sense:001."
            },
            {
              "example_id": "ex-069c7db5553b",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "remark"
              ],
              "rationale": "The term remark identifies a public utterance that draws criticism, supporting sense:001."
            },
            {
              "example_id": "ex-7b75c5c09c71",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "technology"
              ],
              "rationale": "The term technology identifies the public issue under debate, supporting sense:001."
            },
            {
              "example_id": "ex-ee135a966740",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "columnist"
              ],
              "rationale": "The term columnist identifies the person whose temperament is being described, supporting sense:002."
            },
            {
              "example_id": "ex-7927fe1bf63d",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "interpretation"
              ],
              "rationale": "The term interpretation identifies a claim evaluated by a professional group, supporting sense:001."
            }
          ],
          "reviewer": {
            "mode": "handoff",
            "declared_model": "codex-gpt-5",
            "ingested_by": "orchestrator",
            "agent_id": "controversial-checker-example-attribution-20260912T015542Z-872034dc",
            "same_model_as_generation": true,
            "source_response": {
              "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/fb876f521ed92c9e0bc5a6a453f31e1cc6a84582669bc0a2af1d98f49d6b136a.json",
              "sha256": "fb876f521ed92c9e0bc5a6a453f31e1cc6a84582669bc0a2af1d98f49d6b136a"
            }
          }
        },
        "aligned_at": "2026-09-12T02:26:39.102177+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "qualification",
        "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "codex-gpt-5",
          "ingested_by": "orchestrator",
          "agent_id": "controversial-checker-qualification-20260912T015542Z-872034dc",
          "same_model_as_generation": true,
          "source_response": {
            "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/fbcb1449b3d895a67e99fc1270c8b79bef830b9bbd9c807b243da196ebac691c.json",
            "sha256": "fbcb1449b3d895a67e99fc1270c8b79bef830b9bbd9c807b243da196ebac691c"
          }
        }
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "pronunciation",
        "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "codex-gpt-5",
          "ingested_by": "orchestrator",
          "agent_id": "controversial-checker-pronunciation-20260912T015542Z-872034dc",
          "same_model_as_generation": true,
          "source_response": {
            "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/031bf4b4d4b08c815925e63e7857f3a3a2d8a6e8d5d2f6210126eced2e9b5022.json",
            "sha256": "031bf4b4d4b08c815925e63e7857f3a3a2d8a6e8d5d2f6210126eced2e9b5022"
          }
        }
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "evidence",
        "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
        "findings": [],
        "reviewer": {
          "mode": "handoff",
          "declared_model": "codex-gpt-5",
          "ingested_by": "orchestrator",
          "agent_id": "controversial-checker-evidence-20260912T015542Z-872034dc",
          "same_model_as_generation": true,
          "source_response": {
            "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/7b6ff8c46059041de5928048f3170b3749efd363400fbce112834545441a032b.json",
            "sha256": "7b6ff8c46059041de5928048f3170b3749efd363400fbce112834545441a032b"
          }
        }
      }
    ],
    "checker_reviewers": {
      "translation": {
        "mode": "handoff",
        "declared_model": "codex-gpt-5",
        "ingested_by": "orchestrator",
        "agent_id": "controversial-checker-translation-20260912T015542Z-872034dc",
        "same_model_as_generation": true,
        "source_response": {
          "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/ba96d2ae3e21d4fc24462e91c6f3d2b7bd2f65e16e95c2943805452d9d352436.json",
          "sha256": "ba96d2ae3e21d4fc24462e91c6f3d2b7bd2f65e16e95c2943805452d9d352436"
        }
      },
      "sense-structure": {
        "mode": "handoff",
        "declared_model": "codex-gpt-5",
        "ingested_by": "orchestrator",
        "agent_id": "controversial-checker-sense-structure-20260912T015542Z-872034dc",
        "same_model_as_generation": true,
        "source_response": {
          "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/a8ddf8126a94a8670e8c02512ae557a48a61a1b8d9e903a06615ada9486af0fc.json",
          "sha256": "a8ddf8126a94a8670e8c02512ae557a48a61a1b8d9e903a06615ada9486af0fc"
        }
      },
      "frame-relation": {
        "mode": "handoff",
        "declared_model": "codex-gpt-5",
        "ingested_by": "orchestrator",
        "agent_id": "controversial-checker-frame-axis-20260912T015542Z-872034dc",
        "same_model_as_generation": true,
        "source_response": {
          "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/f6939539550b34ba6e5fdf95c99988b984f8c507aa7a7d497ce9ad94c930c22e.json",
          "sha256": "f6939539550b34ba6e5fdf95c99988b984f8c507aa7a7d497ce9ad94c930c22e"
        }
      },
      "example-attribution": {
        "mode": "handoff",
        "declared_model": "codex-gpt-5",
        "ingested_by": "orchestrator",
        "agent_id": "controversial-checker-example-attribution-20260912T015542Z-872034dc",
        "same_model_as_generation": true,
        "source_response": {
          "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/fb876f521ed92c9e0bc5a6a453f31e1cc6a84582669bc0a2af1d98f49d6b136a.json",
          "sha256": "fb876f521ed92c9e0bc5a6a453f31e1cc6a84582669bc0a2af1d98f49d6b136a"
        }
      },
      "qualification": {
        "mode": "handoff",
        "declared_model": "codex-gpt-5",
        "ingested_by": "orchestrator",
        "agent_id": "controversial-checker-qualification-20260912T015542Z-872034dc",
        "same_model_as_generation": true,
        "source_response": {
          "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/fbcb1449b3d895a67e99fc1270c8b79bef830b9bbd9c807b243da196ebac691c.json",
          "sha256": "fbcb1449b3d895a67e99fc1270c8b79bef830b9bbd9c807b243da196ebac691c"
        }
      },
      "pronunciation": {
        "mode": "handoff",
        "declared_model": "codex-gpt-5",
        "ingested_by": "orchestrator",
        "agent_id": "controversial-checker-pronunciation-20260912T015542Z-872034dc",
        "same_model_as_generation": true,
        "source_response": {
          "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/031bf4b4d4b08c815925e63e7857f3a3a2d8a6e8d5d2f6210126eced2e9b5022.json",
          "sha256": "031bf4b4d4b08c815925e63e7857f3a3a2d8a6e8d5d2f6210126eced2e9b5022"
        }
      },
      "evidence": {
        "mode": "handoff",
        "declared_model": "codex-gpt-5",
        "ingested_by": "orchestrator",
        "agent_id": "controversial-checker-evidence-20260912T015542Z-872034dc",
        "same_model_as_generation": true,
        "source_response": {
          "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/7b6ff8c46059041de5928048f3170b3749efd363400fbce112834545441a032b.json",
          "sha256": "7b6ff8c46059041de5928048f3170b3749efd363400fbce112834545441a032b"
        }
      }
    },
    "independent_candidates": [],
    "summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency."
  },
  "cold_review": {
    "summary": "問題候補なし。本文の語義区分、発音説明、語源、文型、例文、訳、レジスター表示を前提なしで横断確認したが、学習者に誤った一般化を促す重大な問題は見当たらない。",
    "findings": [],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "codex-gpt-5",
      "ingested_by": "orchestrator",
      "agent_id": "controversial-cold-20260912T015542Z-872034dc",
      "source_response": {
        "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/f244c66cce79567090f0bf682ace522cc2f7145badf4d298bf33469f3e75605f.json",
        "sha256": "f244c66cce79567090f0bf682ace522cc2f7145badf4d298bf33469f3e75605f"
      },
      "same_model_as_generation": true
    },
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-controversial-20260912T015542Z-872034dc",
    "context_id": "cold-controversial-context-20260912T015542Z-872034dc",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "prompt_sha256": "25c298d1a4305746147791bd442cd725a92737c8f0802b992ea88e5c6ff76a5d",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-12T02:34:36.348334+00:00"
  },
  "final_blind": {
    "provisional_decision": "pass",
    "independent_candidates": [
      {
        "id": "IC-FB-001",
        "surface_form": "controversial",
        "frame": "a controversial issue/decision/figure/remark",
        "meaning": "論争を呼ぶ、賛否が分かれる、物議を醸す",
        "disposition": "included",
        "rationale": "The frame a controversial issue/decision/figure/remark supports the meaning 論争を呼ぶ、賛否が分かれる、物議を醸す because the adjective describes a subject that attracts strong public disagreement.",
        "semantic_assertions": [
          {
            "id": "IC-FB-001-SA-001",
            "statement": "The adjective applies to an issue, decision, figure, or remark that provokes substantial disagreement or criticism.",
            "polarity": "must_hold",
            "scope": "ordinary public-controversy use"
          },
          {
            "id": "IC-FB-001-SA-002",
            "statement": "The ordinary adjective does not by itself entail that the subject is false, illegal, bad, or deliberately provocative.",
            "polarity": "must_not_hold",
            "scope": "ordinary public-controversy boundary"
          }
        ]
      },
      {
        "id": "IC-FB-002",
        "surface_form": "controversial",
        "frame": "controversial among/within a group; controversial in some circles",
        "meaning": "特定の集団の中で論争を呼ぶ",
        "disposition": "included",
        "rationale": "The frame controversial among/within a group; controversial in some circles supports the meaning 特定の集団の中で論争を呼ぶ by restricting where the disagreement is reported.",
        "semantic_assertions": [
          {
            "id": "IC-FB-002-SA-001",
            "statement": "An among, within, or in-some-circles phrase can limit the community in which the controversy exists.",
            "polarity": "must_hold",
            "scope": "scoped controversy"
          }
        ]
      },
      {
        "id": "IC-FB-003",
        "surface_form": "controversial",
        "frame": "become/remain/prove controversial; highly or widely controversial",
        "meaning": "論争状態になる、論争状態が続く、論争の広がりや強さが大きい",
        "disposition": "included",
        "rationale": "The frame become/remain/prove controversial; highly or widely controversial shows that controversial can describe a changing or continuing state, with modifiers for intensity or reach.",
        "semantic_assertions": [
          {
            "id": "IC-FB-003-SA-001",
            "statement": "Become, remain, and prove can present controversy as a state that begins, continues, or becomes evident.",
            "polarity": "must_hold",
            "scope": "copular and resultative frames"
          },
          {
            "id": "IC-FB-003-SA-002",
            "statement": "Highly and widely distinguish strength of opposition from the breadth of the group involved.",
            "polarity": "must_hold",
            "scope": "degree and scope modifiers"
          }
        ]
      },
      {
        "id": "IC-FB-004",
        "surface_form": "controversial",
        "frame": "a controversial temperament/manner; be controversial by temperament",
        "meaning": "論争を好む、論争を引き起こしがちな、論争的な",
        "disposition": "included",
        "rationale": "The frame a controversial temperament/manner; be controversial by temperament supports the meaning 論争を好む、論争を引き起こしがちな、論争的な as a rare dispositional reading about a person's habitual conduct.",
        "semantic_assertions": [
          {
            "id": "IC-FB-004-SA-001",
            "statement": "A temperament, manner, or by-temperament frame can shift the adjective from public evaluation of a person to a rare description of disputatious disposition.",
            "polarity": "must_hold",
            "scope": "rare dispositional use"
          },
          {
            "id": "IC-FB-004-SA-002",
            "statement": "A controversial person in ordinary current usage must not automatically be interpreted as someone who enjoys arguing.",
            "polarity": "must_not_hold",
            "scope": "person-reading boundary"
          }
        ]
      },
      {
        "id": "IC-FB-005",
        "surface_form": "controversially",
        "frame": "controversially modify a claim, decision, or clause",
        "meaning": "物議を醸す形で、論争を呼ぶ形で",
        "disposition": "included",
        "rationale": "The frame controversially modify a claim, decision, or clause supports the meaning 物議を醸す形で、論争を呼ぶ形で as the adverbial form describing how an assertion or action is presented.",
        "semantic_assertions": [
          {
            "id": "IC-FB-005-SA-001",
            "statement": "Controversially is an adverbial derivative and does not create a new adjective sense of controversial.",
            "polarity": "must_hold",
            "scope": "adverbial derivation"
          }
        ]
      },
      {
        "id": "IC-FB-006",
        "surface_form": "controversy",
        "frame": "public controversy / a controversy over a policy",
        "meaning": "論争、論争点、物議",
        "disposition": "included",
        "rationale": "The frame public controversy / a controversy over a policy supports the meaning 論争、論争点、物議 as the noun naming the dispute associated with controversial subjects.",
        "semantic_assertions": [
          {
            "id": "IC-FB-006-SA-001",
            "statement": "Controversy is a related noun naming a dispute or contentious public issue, not an inflected form of the adjective.",
            "polarity": "must_hold",
            "scope": "noun derivation"
          }
        ]
      },
      {
        "id": "IC-FB-007",
        "surface_form": "controversialist",
        "frame": "a controversialist in a debate",
        "meaning": "論争家、論争に加わる人",
        "disposition": "included",
        "rationale": "The frame a controversialist in a debate supports the meaning 論争家、論争に加わる人 as a formal related noun for a participant or advocate in controversy.",
        "semantic_assertions": [
          {
            "id": "IC-FB-007-SA-001",
            "statement": "Controversialist refers to a person associated with controversy and remains a separate noun from controversial.",
            "polarity": "must_hold",
            "scope": "person-denoting derivation"
          }
        ]
      },
      {
        "id": "IC-FB-008",
        "surface_form": "controvert",
        "frame": "to controvert a claim",
        "meaning": "反論する、論駁する",
        "disposition": "included",
        "rationale": "The frame to controvert a claim supports the meaning 反論する、論駁する as a related verb for directly challenging a proposition, while remaining lexically separate from controversial.",
        "semantic_assertions": [
          {
            "id": "IC-FB-008-SA-001",
            "statement": "Controvert is a separate verb meaning to dispute or refute a claim and is not a direct inflection of controversial.",
            "polarity": "must_hold",
            "scope": "verb-family boundary"
          }
        ]
      }
    ],
    "article_findings": [],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "codex-gpt-5",
      "ingested_by": "orchestrator",
      "agent_id": "controversial-final-blind-20260912T015542Z-872034dc",
      "source_response": {
        "path": "audits/runs/c/controversial/20260912T015542Z-872034dc/handoff/source_responses/d34fa36f480a3aeb2a96bf7a26c70e523932d8e0a4316fde922b324dcb26518c.json",
        "sha256": "d34fa36f480a3aeb2a96bf7a26c70e523932d8e0a4316fde922b324dcb26518c"
      },
      "same_model_as_generation": true
    },
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-controversial-20260912T015542Z-872034dc",
    "context_id": "blind-controversial-context-20260912T015542Z-872034dc",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "prompt_sha256": "3a481b4b5b1236ff386e148bcacc574570b305e79f5e155e9afcd34091f7785c",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-12T02:42:23.112674+00:00"
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/c/controversial.md",
    "body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "final_blind_path": "audits/runs/c/controversial/20260912T015542Z-872034dc/final_blind.json",
    "final_blind_sha256": "54147ac24b193f8737e95401ce71bd6f90120569095a7d44b145b6461ca77270",
    "blind_output_sha256": "455ef8e05e5ee529d434bfbbbe0cce1d335089c102a325e4bfcaa02ab80bef58",
    "sealed_at": "2026-09-12T10:42:33.336305+08:00"
  },
  "pre_blind_resolution": {
    "schema_version": "pre_blind_resolution_v1",
    "stage": "pre_blind_resolution",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "output_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "recorded_at": "2026-09-12T02:35:00Z",
    "resolutions": [],
    "learning_delta": {
      "schema_version": "process_improvement_learning_delta_v2",
      "reviewed": true,
      "items": []
    }
  },
  "pre_blind_revision": {
    "schema_version": "pre_blind_revision_v1",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "output_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "recorded_at": "2026-09-12T02:35:00Z",
    "changed_units": [],
    "invalidated_passes": [],
    "full_recheck": false
  },
  "checker_recheck_manifest": {
    "schema_version": "checker_recheck_manifest_v1",
    "current_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "revision_plan_sha256": "91669fb9a7b1cb3889ec30a9417c332bc864f9772e19446509dfe3f15978ebcc",
    "full_recheck": false,
    "invalidated_passes": [],
    "pass_results": [
      {
        "pass_id": "translation",
        "mode": "reused",
        "spec_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
        "normalized_input_sha256": "7b8bedb6417de84814f037c78f8c3fcfff1eef494565178e617ea7389c2fb7e8",
        "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
        "output_sha256": "ae47cd35ad7c067ae6005f4a4e71f0da0c2a06c2e4a4e637b5a0febf56892dc9",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reviewer_agent_id": "controversial-checker-translation-20260912T015542Z-872034dc",
        "output_path": "audits/runs/c/controversial/20260912T015542Z-872034dc/check_passes/translation.json",
        "validated_on_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "pass_id": "sense-structure",
        "mode": "reused",
        "spec_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
        "normalized_input_sha256": "ab0cd927622ac8b16615d9a6c156bd064a1138c9631add75fe3ffc00d9fec4c8",
        "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
        "output_sha256": "64cd2734637de8d1cb463a4888c55c96577dbb1970e4c9eb350896883df79156",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reviewer_agent_id": "controversial-checker-sense-structure-20260912T015542Z-872034dc",
        "output_path": "audits/runs/c/controversial/20260912T015542Z-872034dc/check_passes/sense-structure.json",
        "validated_on_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "pass_id": "frame-relation",
        "mode": "reused",
        "spec_sha256": "3598ca81a5784639c6b43a0806d0981a985bf4174f424c744aad1dde787bfcef",
        "normalized_input_sha256": "bb4fe1274aaba4cc9e5b3872a3a0e1121c6ab3f1f9d0e49df3438f21391a662c",
        "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
        "output_sha256": "3aa8c5d1de38bc5a3b8b1e3067c9e9c63a7ff78f54d58689703e54e96bebfecc",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reviewer_agent_id": "controversial-checker-frame-axis-20260912T015542Z-872034dc",
        "output_path": "audits/runs/c/controversial/20260912T015542Z-872034dc/check_passes/frame-relation.json",
        "validated_on_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "pass_id": "example-attribution",
        "mode": "reused",
        "spec_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
        "normalized_input_sha256": "f5f6bd4a1b6efa01656892e3463b05da349bd90c954729744a277833d3869ad2",
        "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
        "output_sha256": "f1ab6fa09c3e8060aced20144f020ec5edf4ab320df7ac5c2e16d2065269f5fe",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reviewer_agent_id": "controversial-checker-example-attribution-20260912T015542Z-872034dc",
        "output_path": "audits/runs/c/controversial/20260912T015542Z-872034dc/check_passes/example-attribution.json",
        "validated_on_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "pass_id": "qualification",
        "mode": "reused",
        "spec_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
        "normalized_input_sha256": "200997e23daa89657501501c13eaf7f268a7c8cbbb588a048a45fcbac2aa4aef",
        "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
        "output_sha256": "5108dd56e531af87f3610dc730ff99a9959748949404d5f85ff8940238334ed8",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reviewer_agent_id": "controversial-checker-qualification-20260912T015542Z-872034dc",
        "output_path": "audits/runs/c/controversial/20260912T015542Z-872034dc/check_passes/qualification.json",
        "validated_on_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "pass_id": "pronunciation",
        "mode": "reused",
        "spec_sha256": "7e3e94267ac9f917c901c12580b91e570b5989df7adfbf2a39b833478c766d8a",
        "normalized_input_sha256": "94c600de9f95f2fd465326129f540bab3cbb412ebac26373d2b4c2c816b5fe0f",
        "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
        "output_sha256": "1919099463c23146e08f08daf21673e2bad987bbb94b155b1168c7f8900afa6d",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reviewer_agent_id": "controversial-checker-pronunciation-20260912T015542Z-872034dc",
        "output_path": "audits/runs/c/controversial/20260912T015542Z-872034dc/check_passes/pronunciation.json",
        "validated_on_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "pass_id": "evidence",
        "mode": "reused",
        "spec_sha256": "f0de393d4d064190e23916b2e8bfda25b2b83fd29e14cf52395c894b8539d7e9",
        "normalized_input_sha256": "ecd65aba1b08fb830c82963545b431ea3abafbcdeaecd8b5a0edaa0febbebba3",
        "source_artifact_sha256": "77ed6903c70ca9ccab05a50f54ae8740a0cbc1b14859eb360871347314edd2d8",
        "output_sha256": "b20f6d56ac534b33f745ec85ba5be30ec6a6a180b0f50ecc80163a2cbc870ed4",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "reuse_validated": true,
        "reviewer_agent_id": "controversial-checker-evidence-20260912T015542Z-872034dc",
        "output_path": "audits/runs/c/controversial/20260912T015542Z-872034dc/check_passes/evidence.json",
        "validated_on_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      }
    ]
  },
  "post_blind_resolution": {
    "schema_version": "post_blind_resolution_v1",
    "recorded_at": "2026-09-12T02:43:31.789462Z",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "output_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "resolutions": [],
    "rationale": "The latest independent final-blind inventory found no article findings, so the sealed body is retained without further revision.",
    "learning_delta": {
      "schema_version": "process_improvement_learning_delta_v2",
      "reviewed": true,
      "items": []
    }
  },
  "post_blind_verification": {
    "schema_version": "post_blind_verification_v1",
    "verified_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "recorded_at": "2026-09-12T02:43:31.789462Z",
    "checker_recheck_completed": true,
    "checker_recheck_manifest_sha256": "475420f02b21c3b18e9cb1dc895a9726290b3accfd32b94c0b63beefe540713c",
    "final_blind_repeated": false,
    "final_blind_sha256": "54147ac24b193f8737e95401ce71bd6f90120569095a7d44b145b6461ca77270",
    "attempt_number": 1,
    "status": "complete"
  },
  "targeted_adjudications": {
    "schema_version": "targeted_adjudications_v1",
    "requests": [],
    "adjudications": []
  },
  "source_inventory": {
    "schema_version": "source_inventory_v2",
    "stage": "source_inventory",
    "headword": "controversial",
    "run_id": "source-controversial-20260912T015542Z-872034dc",
    "context_id": "source-controversial-context-20260912T015542Z-872034dc",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "prompt_sha256": "0377df9f9e2eeeed2d38f6a7072f675fc4eea38e948ed672004f96bc2d88f783",
    "input_artifacts": [
      "headword",
      "source_first_spec"
    ],
    "recorded_at": "2026-09-12T02:18:00Z",
    "evidence_link_ids": [],
    "source_first_audit": {
      "version": "source_first_audit_v2",
      "profile": "standard",
      "profile_reason": "bounded source-first inventory for controversial",
      "limits": {
        "max_sources": 6,
        "max_facts": 48,
        "max_research_rounds": 2,
        "max_post_cold_rechecks": null,
        "max_final_attempts": 2
      },
      "usage": {
        "sources_used": 4,
        "facts_used": 18,
        "research_rounds_used": 1,
        "post_cold_rechecks_used": 0,
        "final_attempts_used": 0
      },
      "research_status": "complete",
      "stop_reason": "coverage_axes_closed",
      "open_questions": [],
      "inventory_completed_before_article_comparison": true,
      "inventory_completed_at": "2026-09-12T02:18:00Z",
      "article_comparison_started_at": "2026-09-12T02:18:30Z",
      "coverage_axes": [
        {
          "axis": "lexical_senses",
          "status": "covered",
          "source_fact_ids": [
            "F001",
            "F003",
            "F008",
            "F013"
          ],
          "notes": "Independent dictionaries attest the common public-disagreement sense and the rare disputatious-personality sense."
        },
        {
          "axis": "part_of_speech_and_frames",
          "status": "covered",
          "source_fact_ids": [
            "F002",
            "F009",
            "F014"
          ],
          "notes": "The sources attest attributive and predicative adjective patterns, degree modification, and group-limiting complements."
        },
        {
          "axis": "derived_and_related_forms",
          "status": "covered",
          "source_fact_ids": [
            "F012"
          ],
          "notes": "The general dictionary lists the related adverb, noun, and verb forms used in the formation section."
        },
        {
          "axis": "specialist_and_legal_uses",
          "status": "not_applicable",
          "source_fact_ids": [],
          "notes": "The consulted current dictionaries do not establish a separate legal or specialist lexical sense for controversial."
        },
        {
          "axis": "register_region_and_frequency",
          "status": "covered",
          "source_fact_ids": [
            "F004",
            "F015"
          ],
          "notes": "Learner-dictionary level labels and dictionary usage descriptions support the common standard register and the rare personality sense."
        },
        {
          "axis": "pronunciation_and_etymology",
          "status": "covered",
          "source_fact_ids": [
            "F005",
            "F006",
            "F010",
            "F016",
            "F017",
            "F018"
          ],
          "notes": "Learner and general dictionaries provide current pronunciation and the etymology references provide the late-sixteenth-century history."
        }
      ],
      "sources": [
        {
          "id": "S001",
          "title": "Oxford Learner's Dictionaries — controversial",
          "locator": "https://www.oxfordlearnersdictionaries.com/definition/english/controversial",
          "source_type": "learner_dictionary",
          "source_role": "general_lexicon",
          "independence_group": "oxford_university_press",
          "facts": [
            {
              "id": "F001",
              "form": "controversial",
              "kind": "lexical_sense",
              "statement": "Controversial describes something that causes a lot of angry public discussion and disagreement.",
              "source_detail": "Oxford gives the main adjective sense for topics, plans, and people that provoke public disagreement."
            },
            {
              "id": "F002",
              "form": "controversial",
              "kind": "grammar_frame",
              "statement": "Controversial is used before issue, plan, figure, and similar nouns and can be modified by highly.",
              "source_detail": "Oxford examples include a highly controversial topic, a controversial plan, and controversial figures."
            },
            {
              "id": "F003",
              "form": "controversial",
              "kind": "lexical_sense",
              "statement": "A controversial person or figure is one whose public reputation or views provoke disagreement.",
              "source_detail": "Oxford includes controversial figures among its examples for the adjective."
            },
            {
              "id": "F004",
              "form": "controversial",
              "kind": "register_frequency",
              "statement": "Controversial is a common learner-level adjective, listed at Oxford 5000 level B2.",
              "source_detail": "Oxford labels the headword B2 in its learner vocabulary information."
            },
            {
              "id": "F005",
              "form": "controversial",
              "kind": "pronunciation",
              "statement": "Oxford gives British /ˌkɒntrəˈvɜːʃl/ and American /ˌkɑːntrəˈvɜːrʃl/ pronunciations.",
              "source_detail": "The Oxford entry displays separate British and American pronunciation transcriptions."
            },
            {
              "id": "F006",
              "form": "controversial",
              "kind": "etymology",
              "statement": "Controversial comes from late Latin controversialis and is related to controversia and controversus.",
              "source_detail": "Oxford's word-origin note traces the adjective to late Latin forms associated with controversy."
            }
          ]
        },
        {
          "id": "S002",
          "title": "Merriam-Webster — controversial",
          "locator": "https://www.merriam-webster.com/dictionary/controversial",
          "source_type": "general_dictionary",
          "source_role": "general_lexicon",
          "independence_group": "merriam_webster",
          "facts": [
            {
              "id": "F007",
              "form": "controversial",
              "kind": "lexical_sense",
              "statement": "Controversial means relating to or arousing controversy.",
              "source_detail": "Merriam-Webster gives of, relating to, or arousing controversy as its first adjective definition."
            },
            {
              "id": "F008",
              "form": "controversial",
              "kind": "lexical_sense",
              "statement": "Controversial can also mean given to controversy or disputatious when describing a person or temperament.",
              "source_detail": "Merriam-Webster lists a second adjective sense meaning given to controversy and gives a controversial temperament example."
            },
            {
              "id": "F009",
              "form": "controversial",
              "kind": "grammar_frame",
              "statement": "Controversial commonly modifies policy, film, and similar nouns in attributive adjective phrases.",
              "source_detail": "Merriam-Webster illustrates the adjective with a controversial policy and a controversial film."
            },
            {
              "id": "F010",
              "form": "controversial",
              "kind": "pronunciation",
              "statement": "American pronunciation includes a main /ˌkän-trə-ˈvər-shəl/ form and a variant with a more syllabic final sequence.",
              "source_detail": "Merriam-Webster displays the US pronunciation and the -ˈvər-sē-əl variant."
            },
            {
              "id": "F011",
              "form": "controversial",
              "kind": "etymology",
              "statement": "Merriam-Webster records controversial as first known from 1583.",
              "source_detail": "The dictionary's first-known-use field gives 1583 for the adjective."
            },
            {
              "id": "F012",
              "form": "controversially",
              "kind": "derived_form",
              "statement": "Controversially is the related adverb, and controversialist and controversialism are related noun forms; controvert is a related verb.",
              "source_detail": "Merriam-Webster's related-word information lists the adverb, noun forms, and the related verb controvert."
            }
          ]
        },
        {
          "id": "S003",
          "title": "Collins English Dictionary — controversial",
          "locator": "https://www.collinsdictionary.com/dictionary/english/controversial",
          "source_type": "general_dictionary",
          "source_role": "general_lexicon",
          "independence_group": "harpercollins",
          "facts": [
            {
              "id": "F013",
              "form": "controversial",
              "kind": "lexical_sense",
              "statement": "Controversial describes a person or thing that is the subject of intense public argument, disagreement, or disapproval, and it can rarely mean disputatious.",
              "source_detail": "Collins gives the public-argument sense and labels the disputatious personality sense rare in its American entry."
            },
            {
              "id": "F014",
              "form": "controversial",
              "kind": "grammar_frame",
              "statement": "Controversial forms common phrases with deal, decision, figure, film, issue, plan, proposal, remark, ruling, statement, theory, and view.",
              "source_detail": "Collins lists these noun collocations and degree modifiers such as highly, widely, and potentially."
            },
            {
              "id": "F015",
              "form": "controversial",
              "kind": "register_frequency",
              "statement": "Controversial is a B2 adjective, while its disputatious-personality use is rare.",
              "source_detail": "Collins labels the general headword B2 and marks the second American sense rare."
            },
            {
              "id": "F016",
              "form": "controversial",
              "kind": "pronunciation_etymology",
              "statement": "Collins gives American variants with both /-vɜrʃəl/ and /-vɜrsiəl/ and dates the origin to 1575–85.",
              "source_detail": "The Collins entry displays the pronunciation variants and the 1575–85 origin range."
            }
          ]
        },
        {
          "id": "S004",
          "title": "Online Etymology Dictionary — controversial",
          "locator": "https://www.etymonline.com/word/controversial",
          "source_type": "etymology_dictionary",
          "source_role": "etymology_reference",
          "independence_group": "etymonline",
          "facts": [
            {
              "id": "F017",
              "form": "controversial",
              "kind": "etymology",
              "statement": "Controversial is recorded in the 1580s in the sense of debatable or disputed, from late Latin controversialis.",
              "source_detail": "Etymonline dates the early adjective use to the 1580s and gives the late Latin source."
            },
            {
              "id": "F018",
              "form": "controversial",
              "kind": "etymology",
              "statement": "The Latin form is related to controversus, literally turned against, from contra and versus, the past participle of vertere.",
              "source_detail": "Etymonline explains the Latin components and the underlying sense of being turned against."
            }
          ]
        }
      ],
      "source_union": [
        {
          "id": "U001",
          "source_fact_ids": [
            "F001",
            "F002",
            "F003",
            "F007",
            "F009",
            "F013",
            "F014"
          ],
          "canonical_statement": "Controversial commonly describes an issue, decision, claim, work, remark, or person that arouses strong public or group disagreement.",
          "disposition": "included",
          "rationale": "This is the high-frequency main adjective sense and is the first numbered sense."
        },
        {
          "id": "U002",
          "source_fact_ids": [
            "F008",
            "F013",
            "F015"
          ],
          "canonical_statement": "Controversial can rarely describe a person or temperament inclined to controversy or disputation.",
          "disposition": "included",
          "rationale": "The rare personality sense is retained because independent dictionaries record it and it prevents a person-use ambiguity."
        },
        {
          "id": "U003",
          "source_fact_ids": [
            "F005",
            "F010",
            "F016"
          ],
          "canonical_statement": "Controversial has a four-syllable pronunciation with main stress on the third syllable and a US variant with a more syllabic ending.",
          "disposition": "included",
          "rationale": "The pronunciation section records the mainstream British/American forms and qualifies the US variant."
        },
        {
          "id": "U004",
          "source_fact_ids": [
            "F006",
            "F011",
            "F016",
            "F017",
            "F018"
          ],
          "canonical_statement": "Controversial is a late-sixteenth-century adjective from late Latin controversialis, related to controversia and controversus.",
          "disposition": "included",
          "rationale": "The etymology section states the shared late-sixteenth-century range and avoids treating conflicting first-use dates as exact."
        },
        {
          "id": "U005",
          "source_fact_ids": [
            "F012"
          ],
          "canonical_statement": "Controversially, controversialist, controversialism, and controvert are related forms, with different parts of speech and frequency.",
          "disposition": "integrated",
          "rationale": "The formation section records useful related forms without presenting the adverb or nouns as additional senses of the headword."
        },
        {
          "id": "U006",
          "source_fact_ids": [
            "F004",
            "F015"
          ],
          "canonical_statement": "The public-disagreement adjective is a common B2-level word, while the personality sense is rare.",
          "disposition": "integrated",
          "rationale": "The two frequency/register labels are attached to their respective numbered senses."
        }
      ],
      "claim_units": [
        {
          "id": "C001",
          "union_ids": [
            "U001"
          ],
          "subject_form": "controversial",
          "claim_type": "definition",
          "statement": "The common sense describes topics, decisions, claims, works, remarks, and people that provoke strong disagreement or criticism.",
          "article_target_ids": [
            "sense_boundary:001",
            "definition:001",
            "frequency:001",
            "register:001",
            "grammar_pattern:001",
            "grammar_pattern:002",
            "grammar_pattern:003",
            "grammar_pattern:004",
            "grammar_pattern:005",
            "grammar_pattern:006",
            "grammar_pattern:007",
            "grammar_pattern:008",
            "grammar_pattern:009",
            "collocation:001",
            "collocation:002",
            "collocation:003",
            "collocation:004",
            "collocation:005",
            "collocation:006",
            "collocation:007",
            "collocation:008",
            "collocation:009",
            "usage_note:001",
            "synonym:001",
            "synonym:002",
            "synonym:003",
            "synonym:004",
            "synonym:005",
            "synonym:006",
            "synonym:007",
            "antonym:001",
            "antonym:002"
          ],
          "source_supports": [
            {
              "source_fact_id": "F001",
              "support_summary": "Oxford directly defines the public discussion and disagreement sense."
            },
            {
              "source_fact_id": "F002",
              "support_summary": "Oxford supplies the main noun combinations and degree modifier."
            },
            {
              "source_fact_id": "F003",
              "support_summary": "Oxford attests the use for controversial figures."
            },
            {
              "source_fact_id": "F007",
              "support_summary": "Merriam-Webster defines the adjective through arousing controversy."
            },
            {
              "source_fact_id": "F009",
              "support_summary": "Merriam-Webster illustrates the attributive policy and film frames."
            },
            {
              "source_fact_id": "F013",
              "support_summary": "Collins defines intense public argument and disapproval."
            },
            {
              "source_fact_id": "F014",
              "support_summary": "Collins records the article's common noun collocations."
            }
          ]
        },
        {
          "id": "C002",
          "union_ids": [
            "U002"
          ],
          "subject_form": "controversial",
          "claim_type": "definition",
          "statement": "The rare personality sense describes a person inclined to controversy or disputation rather than merely a person who is being publicly debated.",
          "article_target_ids": [
            "sense_boundary:002",
            "definition:002",
            "frequency:002",
            "register:002",
            "grammar_pattern:010",
            "grammar_pattern:011",
            "grammar_pattern:012",
            "grammar_pattern:013",
            "collocation:010",
            "collocation:011",
            "collocation:012",
            "collocation:013",
            "usage_note:002",
            "synonym:008",
            "synonym:009",
            "synonym:010",
            "synonym:011"
          ],
          "source_supports": [
            {
              "source_fact_id": "F008",
              "support_summary": "Merriam-Webster explicitly gives the disputatious personality sense."
            },
            {
              "source_fact_id": "F013",
              "support_summary": "Collins records the rare disputatious use in its American entry."
            },
            {
              "source_fact_id": "F015",
              "support_summary": "Collins marks the personality use rare and contrasts it with the common sense."
            }
          ]
        },
        {
          "id": "C003",
          "union_ids": [
            "U003"
          ],
          "subject_form": "controversial",
          "claim_type": "pronunciation",
          "statement": "The word normally has four syllables and main stress on the third, with a US variant that may realize the ending as an extra syllable.",
          "article_target_ids": [
            "pronunciation:001"
          ],
          "source_supports": [
            {
              "source_fact_id": "F005",
              "support_summary": "Oxford supplies the main British and American transcriptions."
            },
            {
              "source_fact_id": "F010",
              "support_summary": "Merriam-Webster records the American ending variant."
            },
            {
              "source_fact_id": "F016",
              "support_summary": "Collins independently displays the American pronunciation variants."
            }
          ]
        },
        {
          "id": "C004",
          "union_ids": [
            "U004"
          ],
          "subject_form": "controversial",
          "claim_type": "etymology",
          "statement": "The adjective belongs to a late-sixteenth-century Latin-derived controversy word family involving the idea of being turned against.",
          "article_target_ids": [
            "etymology:001"
          ],
          "source_supports": [
            {
              "source_fact_id": "F006",
              "support_summary": "Oxford traces the adjective to late Latin controversialis."
            },
            {
              "source_fact_id": "F011",
              "support_summary": "Merriam-Webster's 1583 first-use date supports the late-sixteenth-century range."
            },
            {
              "source_fact_id": "F016",
              "support_summary": "Collins gives a 1575–85 origin range rather than a modern date."
            },
            {
              "source_fact_id": "F017",
              "support_summary": "Etymonline gives the 1580s debatable or disputed use."
            },
            {
              "source_fact_id": "F018",
              "support_summary": "Etymonline explains controversus, contra, versus, and vertere."
            }
          ]
        },
        {
          "id": "C005",
          "union_ids": [
            "U005"
          ],
          "subject_form": "controversially",
          "claim_type": "word_formation",
          "statement": "The article distinguishes the related adverb, noun forms, and verb rather than treating them as inflections of the adjective.",
          "article_target_ids": [
            "word_formation:001",
            "word_formation:002",
            "word_formation:003",
            "word_formation:004"
          ],
          "source_supports": [
            {
              "source_fact_id": "F012",
              "support_summary": "Merriam-Webster lists the related adverb, nouns, and verb forms."
            }
          ]
        },
        {
          "id": "C006",
          "union_ids": [
            "U006"
          ],
          "subject_form": "controversial",
          "claim_type": "register_frequency",
          "statement": "The public-disagreement use is standard and common, whereas the disputatious-personality use is rare and dictionary-oriented.",
          "article_target_ids": [
            "register:001",
            "frequency:001",
            "register:002",
            "frequency:002"
          ],
          "source_supports": [
            {
              "source_fact_id": "F004",
              "support_summary": "Oxford labels the headword B2 in its learner vocabulary."
            },
            {
              "source_fact_id": "F015",
              "support_summary": "Collins labels the personality use rare and the general word B2."
            }
          ]
        }
      ]
    }
  },
  "resolutions": {
    "schema_version": "resolutions_v1",
    "stage": "resolutions",
    "run_id": "resolution-controversial-20260912T015542Z-872034dc",
    "context_id": "resolution-controversial-context-20260912T015542Z-872034dc",
    "input_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5",
    "prompt_sha256": "7dfcaa0a828a334dbb84d1d31ed97312d0a9661a7aca70a7815a9f88b31ea2f1",
    "input_artifacts": [
      "entry_body",
      "all_findings"
    ],
    "recorded_at": "2026-09-12T02:43:31.789462Z",
    "resolutions": [],
    "learning_delta": {
      "schema_version": "process_improvement_learning_delta_v2",
      "reviewed": true,
      "items": []
    }
  },
  "inventories": {
    "target_results": [
      {
        "id": "pronunciation:001",
        "kind": "pronunciation",
        "location": "line:4",
        "section": "＃発音記号",
        "sense": "",
        "text_sha256": "8a744f0a9a73caae3c7cba7f57b44ebf31177e264541b358aeacee80fe786709",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "米: /ˌkɑːntrəˈvɝːʃəl/｜英: /ˌkɒntrəˈvɜːʃəl/。米英とも4音節で、第3音節の /vɝː/・/vɜː/ に主強勢がある。第1音節の /ˌkɑːn/・/ˌkɒn/ には副次強勢を示す。米語では /ˌkɑːntrəˈvɝːsiəl/ に近い5音節寄りの発音も聞かれるが、通常の学習上は /ˈvɝːʃəl/・/ˈvɜːʃəl/ の部分を基準にする。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text_sha256": "9b40b877bd6485ba93fc1fc28627f013c8e6774cfab9314c3ca3fe3550fd87cc",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "16世紀後半に使われ始めた語で、後期ラテン語 controversialis「論争に関する」から来た。controversia「論争」は controversus「反対方向に向けられた、争われた」に関係し、contra-/contro-「反対に」と versus「向けられた、転じた」（vertere「向きを変える」の過去分詞）に分けて考えられる。初出年代は資料により1580年代、1583年、1575–85年など差があるため、特定の年として暗記しない。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "a40a3226b8413844f17f848c9bd0bf0dac4f1d7f2e779cf8165a9f0d62b15dbd",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controversy：名詞。「論争、論争点、物議」。controversial と同じ語族の中心語で、public controversy のように使う。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "bc38d22c77884d6d33d09b70f32a205c6cac646f541ad1b99df31258ae4490b4",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controversially：副詞。「物議を醸す形で、論争を呼ぶことに」。文全体や発言・判断の仕方を修飾する。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "f28c35178557e13d6e059bfd37a1b34b47e6f699ca131beaef5a7ff9800f2c8a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controversialist：名詞。「論争家、論争に加わる人」。人の性向または論争上の立場を指す硬めの語。"
      },
      {
        "id": "word_formation:004",
        "kind": "word_formation",
        "location": "line:15",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "63a3786a8446f66430eae1305a6ba0cbff1f1384e06009944b235aa17ee42bef",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controvert：動詞。「反論する、論駁する」。controversial と意味は近いが、現代英語では controversial の直接の活用形ではなく、別の動詞として扱う。"
      },
      {
        "id": "sense_boundary:001",
        "kind": "sense_boundary",
        "location": "line:19",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "501ce539724a3eee9ac6f4d3f97daf880eda292c4dd3e7459f438790f321c0cf",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:21",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "fdc630c604154dac805bfe0439bb985fc93a221cde5a898946d3042d09372602",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "政策・決定・主張・作品・発言・人物などが、社会全体または特定の集団の中で、強い意見の対立、批判、反対を引き起こしていることを表す。事実として真偽が決まっていないことを必ずしも含まず、悪い、違法、意図的に挑発的だという意味でもない。"
      },
      {
        "id": "frequency:001",
        "kind": "frequency",
        "location": "line:23",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "7a626327bdf4a8ce1246cb04f8b9692c985873b0ba478e5ff432ffa1425edf1f",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈9/10〉"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:25",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "eb99c9474ded18a839c17444991b8e0dea996743edf0f996576ea67763c96fdf",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "標準語で、会話・ニュース・政治・文化・学術・ビジネスの文章まで広く使う。controversial は「多くの人が反対している」と同じではなく、賛成・反対の議論が強く起きている状態を指す。"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "8a51d40f92625fcfafe41905bb27b9d1de5f7b70fb0495b3c7b6f31acc2cc17d",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be/become/remain/prove controversial＝論争を呼ぶ・論争の的であり続ける・結果的に物議を醸す"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "276c6f4f505b6102cfa84e7d0cb5ed731f88ecebea08cae80a8c47508bef6593",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a controversial 〈issue・decision・policy・claim・statement・figure・book・film〉＝論争を呼ぶ〈問題・決定・政策・主張・発言・人物・本・映画〉"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "da5072e01c9e8e2435d969a406e4d108050e1c37aaa4ce1ba0a53d3b8aca48d9",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "highly/widely controversial＝非常に"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "e2efca3f936245704e0507fb913ac5b7e6461f1985b26aa93ade4cb1827c2721",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "広く物議を醸す"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "edbf232ada067dccfe65e56ee3cefd9d40f621f959657ab4a37fc26feaba37b4",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "controversial among/within 〈group〉＝〈集団〉の間で論争を呼ぶ"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "492a29aa7ef25560526c39136abdf43756f123f3d3a8f07c2d1cd091dbb75c4e",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "controversial in some circles＝一部の界隈では物議を醸す"
      },
      {
        "id": "grammar_pattern:007",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "5c4a65521e254079b19ba3196062d544693be779ebc6e55d6a9b87437b07ffcb",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "it remains controversial whether ...＝…かどうかは依然として議論が分かれる"
      },
      {
        "id": "grammar_pattern:008",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "d371617ffde65f279d7a9ac2ae3fe0f3d6408632728beb391ed69689fd6bc874",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be controversial enough to do＝～するほど物議を醸す"
      },
      {
        "id": "grammar_pattern:009",
        "kind": "grammar_pattern",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "75abef7f6f54394460211bd59fe154d0875b89148b652bc7e938027968fca17e",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "too controversial to do＝物議を醸しすぎて～できない。"
      },
      {
        "id": "collocation:001",
        "kind": "collocation",
        "location": "lines:31-34",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "a1cf7e37111868c2b2ceb8062836245b42728da67c9604c1406a652c351ace41",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial issue\n用途: 社会的に賛否が対立している問題を指す。\n例: The use of facial-recognition technology remains a controversial issue.\n訳: 顔認証技術の利用は依然として論争を呼ぶ問題だ。"
      },
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:36-39",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "5c29a8ee132fd1f2fa43bd53716d627a2f25e2b2c77e09a4dce491c4e69ce15c",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial decision\n用途: 決定の妥当性や影響をめぐって強い反対・批判が出ていることを表す。\n例: The committee made a controversial decision to cancel the exhibition.\n訳: 委員会は展示会を中止するという物議を醸す決定を下した。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:41-44",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "3c8e43292594fc4b0129a235261fa862aeee5c2d5468e1bb76415ce4e5485ced",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・a controversial figure\n用途: 功績と批判の両方があり、評価が大きく割れている人物を指す。\n例: The historian remains a controversial figure in the region.\n訳: その歴史家はその地域で今も評価が大きく分かれる人物だ。"
      },
      {
        "id": "collocation:004",
        "kind": "collocation",
        "location": "lines:46-49",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "4238292008a5a709b2008927a9ffe05020a77f0eff07e6b7cf09fdb268e173ca",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・a highly controversial proposal\n用途: 提案に対して非常に強い賛否や反発が起きていることを強調する。\n例: The city council postponed a highly controversial proposal.\n訳: 市議会は非常に物議を醸している提案を延期した。"
      },
      {
        "id": "collocation:005",
        "kind": "collocation",
        "location": "lines:51-54",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "9973ab472a7126616140cd7dd1b7c9f234dddce2da842225751b9b101a6c86d6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・controversial among 〈group〉\n用途: どの集団の中で意見が割れているかを限定する。\n例: The interpretation is controversial among constitutional scholars.\n訳: その解釈は憲法学者の間で議論が分かれている。"
      },
      {
        "id": "collocation:006",
        "kind": "collocation",
        "location": "lines:56-59",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "69b91f7b093ed158b555cab7c64af17a6135f83153e572b31f7a804175a6b820",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・controversial in some circles\n用途: 社会全体ではなく、特定の界隈で物議を醸していることを示す。\n例: The advertising campaign is controversial in some circles but popular with younger viewers.\n訳: その広告キャンペーンは一部では物議を醸しているが、若い視聴者には人気がある。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:61-64",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "0e9c13970cd75209bfa2920cc1ddc24396f9675ad135af3c1f002d6addec9e3c",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・it remains controversial whether ...\n用途: 判断が現在も決着していないことを述べる。\n例: It remains controversial whether the policy reduced inequality.\n訳: その政策が格差を縮小したかどうかは、今も議論が分かれている。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:66-69",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "610fab7f6f88573761280e28fd6a7ac7b3f1ba28c245dd4153ac9144e10a980a",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial remark\n用途: 発言が批判や反発を招く内容だったことを表す。\n例: The minister's controversial remark drew criticism from both parties.\n訳: 大臣の物議を醸す発言は両党から批判を招いた。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:71-74",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "7014ac2f2844b254010faeb64f5e68a2cecdf848f6b9e8c9f849aac6b2a9889f",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・become controversial after ...\n用途: 当初は普通だった対象が、後から知られた事実や変化によって論争の的になることを表す。\n例: The renovation plan became controversial after residents learned the full cost.\n訳: 住民が総費用を知った後、その改修計画は物議を醸すようになった。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:76",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "4dd4d08d23cf463a59deea5d40e9fc26ebf739903676028c62a93463def83ff5",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "対象を主語にした be controversial は「その対象が論争の的だ」という意味で、必ずしも対象自身が議論を仕掛けるわけではない。人物についても通常は「評価が割れている人物」の意味であり、「論争を好む人」という性向を言いたいときは語義2を確認する。highly は対立の強さ、widely は論争が広い範囲に及ぶことを示す。controversial を「間違った」「受け入れられない」と自動的に訳さず、何が誰の間で争われているかを among/within 句や文脈で補う。"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:80-85",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "87442f983bf74a4c43c64588d7d05f3a145e60ddca2bf9e5ab119efddc4baa7f",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・contentious\n定義: 議論や対立を引き起こしやすい、争点になっている。\n頻度: 〈8/10〉\n違い: contentious は問題・決定が争いを生みやすい性質や、当事者間の対立の強さに焦点があり、controversial より対立的に響くことがある。\n例: The contentious issue delayed the negotiations for weeks.\n訳: その対立を招く争点のために、交渉は何週間も遅れた。"
      },
      {
        "id": "synonym:002",
        "kind": "synonym",
        "location": "lines:87-92",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "132313664d478c67ad7e01dc628f32735551e1c147c062495f394d8bd89c4d38",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・disputed\n定義: 真偽・権利・解釈などが争われている、意見が一致していない。\n頻度: 〈8/10〉\n違い: disputed は「正しいか、誰のものかなどが争われている」という未確定性を強調し、controversial のような広い世論上の物議まで必ずしも含まない。\n例: The map shows the disputed border in a different color.\n訳: その地図は争われている国境を別の色で示している。"
      },
      {
        "id": "synonym:003",
        "kind": "synonym",
        "location": "lines:94-99",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "6b9984c16d8519f7340048bf653a65230f1d408d8433289918c5fb9d1ab1394a",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・debatable\n定義: 議論の余地があり、結論を一つに決めにくい。\n頻度: 〈7/10〉\n違い: debatable は主張や判断の妥当性を論じられることに焦点があり、controversial より感情的な反発や大きな社会的対立を含まない場合が多い。\n例: Whether the change improved efficiency is debatable.\n訳: その変更が効率を高めたかどうかは議論の余地がある。"
      },
      {
        "id": "synonym:004",
        "kind": "synonym",
        "location": "lines:101-106",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "174810d420e5fb3e877bed9e9139904a03c59021233ea7b517ccf9b945df7117",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・polarizing\n定義: 人々を賛成側と反対側へ大きく分断する。\n頻度: 〈7/10〉\n違い: polarizing は意見の対立を二極化させる効果を強調する。controversial は意見が割れていても、二つの陣営に明確に分かれるとは限らない。\n例: The candidate's polarizing speech dominated the news cycle.\n訳: その候補者の社会を二極化させる演説が報道を席巻した。"
      },
      {
        "id": "synonym:005",
        "kind": "synonym",
        "location": "lines:108-113",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "56a8a933ec528fe3d64eb649a8ab62677c79d3e8cace1c7b821f3786d5f7e015",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・provocative\n定義: 強い反応や議論を意図的または効果として引き起こす、挑発的な。\n頻度: 〈8/10〉\n違い: provocative は発言者・作者が反応を誘う性質や意図に焦点がある。controversial は実際に物議が生じている状態を表し、意図を必要としない。\n例: The artist is known for provocative questions about public memory.\n訳: その芸術家は公共の記憶について挑発的な問いを投げかけることで知られている。"
      },
      {
        "id": "synonym:006",
        "kind": "synonym",
        "location": "lines:115-120",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "65c05ce6b632c80f8e62c5eaa90fad64a1da01cb8fb02fad3c2f10fd57a910c1",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・divisive\n定義: 人々や集団の間に深い対立を生じさせる、分断を招く。\n頻度: 〈7/10〉\n違い: divisive は社会的な分断や関係悪化という結果を強く示す。controversial は分断に至らず、単に議論や批判を招く場合にも使える。\n例: The divisive reform split the professional association.\n訳: その分断を招く改革は専門職団体を二分した。"
      },
      {
        "id": "synonym:007",
        "kind": "synonym",
        "location": "lines:122-127",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "9b0fa9ed047159a53753a1f4900cf4bf290a17e2018b217fd05844b787195ab8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・polemical\n定義: 論争を仕掛ける、または論争的な主張を展開する。\n頻度: 〈4/10〉\n違い: polemical は文章・議論・論者の攻撃的な論争スタイルに寄りやすく、controversial より硬く、意図的な論争性を含みやすい。\n例: The book adopts a polemical tone toward established theories.\n訳: その本は確立した理論に対して論争的な調子を取っている。"
      },
      {
        "id": "antonym:001",
        "kind": "antonym",
        "location": "lines:131-136",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "87dedb582ccc998aeb8fea5e1248a7836b34e946df644efa4ad1b6aac7d12722",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・uncontroversial\n定義: 意見の強い対立や広い反発を招かない、異論の少ない。\n頻度: 〈6/10〉\n違い: controversial の直接的な反対語で、問題・判断・人物などについて大きな論争が起きていない状態を表す。\n例: The committee reached an uncontroversial agreement on the timetable.\n訳: 委員会は日程について異論の少ない合意に達した。"
      },
      {
        "id": "antonym:002",
        "kind": "antonym",
        "location": "lines:138-143",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【形容詞・限定用法／叙述用法・対象／人】論争を呼ぶ、賛否が分かれる、物議を醸す",
        "text_sha256": "61614c1bd67cf88cbefb9bb099d8d71bafbe5a36af0bc81279d8f1a0a4d55e34",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・noncontroversial\n定義: 論争的でない、特に意見の対立を起こさない。\n頻度: 〈5/10〉\n違い: noncontroversial も直接的な反対語だが、uncontroversial より説明的・形式的に見えることがある。\n例: The report limits itself to noncontroversial background facts.\n訳: その報告書は論争のない背景事実に内容を限定している。"
      },
      {
        "id": "sense_boundary:002",
        "kind": "sense_boundary",
        "location": "line:145",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "a2ad2cdcca50d3ca0d81c7c0981ed66a04e6458b4fee8b299252e2ba13d50e33",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:147",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "770698baef047f7a431f943f1f5aa8a0d1ac9c177ec62befb1c3cee1aa6987f6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "人が性格や態度の傾向として、議論を好んだり、既存の立場に反論して対立を生みやすかったりすることを表す。辞書に記載される低頻度の語義で、現代の controversial person は通常、語義1の「論争の的となっている人物」と解釈される。"
      },
      {
        "id": "frequency:002",
        "kind": "frequency",
        "location": "line:149",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "c9f89b3d40a42341908558a5512ad7d34bbc108cc33b512e22b76f6557469962",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈2/10〉"
      },
      {
        "id": "register:002",
        "kind": "register",
        "location": "line:151",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "ce266854a5a47558255071f27ac8b508e804061e9f0bc1bf99360f1d888d49b6",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "まれで、辞書的・形式的・文学的な説明に現れやすい。現代の一般的な文章で人の性向を表すなら argumentative、disputatious、polemical の方が意味を明確にしやすい。"
      },
      {
        "id": "grammar_pattern:010",
        "kind": "grammar_pattern",
        "location": "line:153",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "a0e370216502c56615885a7143b5e30f6346ce59b6af135f64050fc27a1b2028",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a controversial temperament＝論争を好む気質"
      },
      {
        "id": "grammar_pattern:011",
        "kind": "grammar_pattern",
        "location": "line:153",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "261e65c9c3ca09635197820a48ecbe1373901bb2e76e3b45576875ee9201e7b9",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "a controversial manner＝対立を生みやすい態度"
      },
      {
        "id": "grammar_pattern:012",
        "kind": "grammar_pattern",
        "location": "line:153",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "a841a89d53235b8e250142f42a691b54d2bc5b4a5830473bd317828b4dae532b",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be controversial by temperament＝性向として論争的である"
      },
      {
        "id": "grammar_pattern:013",
        "kind": "grammar_pattern",
        "location": "line:153",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "a0e4ad926223cf663c042c5563c8ad786f154b0dc148414ad93be779f2ebd5e3",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "be controversial in debate＝議論で意図的に反論を重ねる。"
      },
      {
        "id": "collocation:010",
        "kind": "collocation",
        "location": "lines:157-160",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "77ed9fdcc083671a735320ce03da9f962ebf436864ffad3e0a2a0c3bf89819fe",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial temperament\n用途: 人が性格的に議論や対立を好むことを、まれな形容詞用法で表す。\n例: The columnist has a controversial temperament and treats every meeting as a public debate.\n訳: そのコラムニストは論争を好む気質で、どの会議も公開討論のように扱う。"
      },
      {
        "id": "collocation:011",
        "kind": "collocation",
        "location": "lines:162-165",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "2c7a42caa5eae2b816a17a8c7ea4ca01a68f2f8f6eca8419b42edf51228b2886",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・a controversial manner\n用途: 人が対立を招きやすい仕方で話したり振る舞ったりすることを表す。\n例: Her controversial manner turned minor technical disagreements into public arguments.\n訳: 彼女の対立を生みやすい態度は、ささいな技術上の意見の違いまで公の論争に変えた。"
      },
      {
        "id": "collocation:012",
        "kind": "collocation",
        "location": "lines:167-170",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "2e168246a3d9798d04b358a4294df8642e81dea4a9b5589cc087bdb46d674220",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・be controversial by temperament\n用途: 物議を醸す個別の行動ではなく、もともとの性向が論争的だと述べるまれな構文。\n例: He was controversial by temperament, challenging even minor points in every debate.\n訳: 彼は性向として論争的で、どの討論でもささいな点にまで反論した。"
      },
      {
        "id": "collocation:013",
        "kind": "collocation",
        "location": "lines:172-175",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "507e3cda12e4b53134e308202185049db0203646a40d4c87792b0f2f7010989e",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・be controversial in debate\n用途: 議論の最中に、立場そのものよりも反論を重ねる性向が目立つことを表す。\n例: The speaker was controversial in debate because he deliberately attacked each established position.\n訳: その話者は確立した立場を一つ一つ意図的に攻撃したため、討論では論争的だった。"
      },
      {
        "id": "usage_note:002",
        "kind": "usage_note",
        "location": "line:177",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "4ead97ad6308fc47606922e75e40762463eb9dcb76d5394fcba8dae379f8aa48",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "この語義では controversial が人の性向を直接表すが、現代の「論争の的となる人物」という普通の解釈と形が同じなので、文脈で区別する必要がある。a controversial politician は通常語義1であり、気質を明示する temperament、manner、by temperament などがあって初めて語義2に近づく。意見が割れているだけなら語義1、本人が反論・対立を好むことまで言うなら語義2である。"
      },
      {
        "id": "synonym:008",
        "kind": "synonym",
        "location": "lines:181-186",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "b5e82e464da36ae0828c0fff036552e8dc5d321c5b4508544d63787a6913b8c4",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・disputatious\n定義: 議論や口論を好む、論争好きな。\n頻度: 〈4/10〉\n違い: disputatious は人の性向そのものを表す明確な語で、controversial のまれな語義より自然に「口論好き」の意味を示す。\n例: His disputatious nature made routine committee work exhausting.\n訳: 彼の論争好きな性質のため、通常の委員会業務は疲れるものになった。"
      },
      {
        "id": "synonym:009",
        "kind": "synonym",
        "location": "lines:188-193",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "966bb2cde06675ce8015e7894df5957201267acdd9ec9e2eed5ef04a4b109302",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・argumentative\n定義: すぐに反論する、議論好きな、口論を招く。\n頻度: 〈7/10〉\n違い: argumentative は日常的で、人が何にでも反論する傾向を表す。controversial より口論・反論の行動が前面に出る。\n例: The child became argumentative whenever the rules were explained.\n訳: その子は規則を説明されるといつも反論するようになった。"
      },
      {
        "id": "synonym:010",
        "kind": "synonym",
        "location": "lines:195-200",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "b04a2150c53378acd552d2cd52980e92a33508399c1e55ccd60f90235c4cdd49",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・polemical\n定義: 論争を仕掛ける、攻撃的に論争する。\n頻度: 〈4/10〉\n違い: polemical は論者・文章・議論の意図的で攻撃的な論争性に焦点があり、controversial より文語的である。\n例: The polemical writer challenged every compromise proposed by the panel.\n訳: その論争的な筆者は、委員会が提案した妥協案すべてに異議を唱えた。"
      },
      {
        "id": "synonym:011",
        "kind": "synonym",
        "location": "lines:202-207",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【形容詞・人の性向・まれ】論争を好む、論争を引き起こしがちな、論争的な",
        "text_sha256": "33e73aee9b4ecfebd7fe4e08c1ed635f02a6a9f6662c92d036390bf152b8cd24",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・contentious\n定義: 対立的で、争いを引き起こしやすい。\n頻度: 〈8/10〉\n違い: contentious は人の態度にも使えるが、敵対的・喧嘩腰の含みが出やすい。controversial の語義2は、必ずしも敵意や攻撃性まで含まない。\n例: The manager's contentious style made open discussion difficult.\n訳: その管理職の対立的なスタイルは、率直な話し合いを難しくした。"
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
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: definition:002 explicitly contrasts sense 2 with sense 1; usage_note:001 explicitly contrasts sense 1 with sense 2; usage_note:002 explicitly contrasts sense 2 with sense 1",
        "text_sha256": "6c5a751912b3ff4f5d6888ec95eb73acbaf08654d6d7d6c320f8f19266c789d7",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      },
      {
        "id": "example_translation:001",
        "kind": "example_translation",
        "target_ids": [
          "collocation:001"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "26750269ee9dd5b51b69765498e65b4a87effedbbc0238eb29e302fcc51b1271",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:002",
        "kind": "example_translation",
        "target_ids": [
          "collocation:002"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "0fddd7231b615b1468c1bb23515fe6ee82ffdf770efff68aeac4dbb2df355152",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:003",
        "kind": "example_translation",
        "target_ids": [
          "collocation:003"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "ae6f03bfc90aa62807a5306af7169ced4893be7f3fe0c7eef691a27f2c6671be",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:004",
        "kind": "example_translation",
        "target_ids": [
          "collocation:004"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "b7bd8e4f64f2b5b4416c868f399db21d336bb2525a56cb9582dc575f8de0f7d3",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:005",
        "kind": "example_translation",
        "target_ids": [
          "collocation:005"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "2c3d879214f4eaf61bfe50841656663a25b4c418dce8fa21d84fb2637c575cf5",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:006",
        "kind": "example_translation",
        "target_ids": [
          "collocation:006"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "e6b70b6f529d0afd20caa1af0a66c20b2b508c59841b4f32f3ef20f4e775bf02",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:007",
        "kind": "example_translation",
        "target_ids": [
          "collocation:007"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "70ef911dd4616153972b44f7c6764b22f0d4c69c0f3128250f4e79719f5c37d9",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:008",
        "kind": "example_translation",
        "target_ids": [
          "collocation:008"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "5f2bc65b94c6a305d15a4a7799b1b5f405b78d66c43ed082ddae23034fa9d638",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:009",
        "kind": "example_translation",
        "target_ids": [
          "collocation:009"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "0b4b10a1fbf88bacd5150465ea4b231fc56e5e27736eef3449c9f50b98a6fe2e",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:010",
        "kind": "example_translation",
        "target_ids": [
          "collocation:010"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "58d14b97f4826f5fe10d2313973b4228da01f3317e3edc280fd457b43980af45",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:011",
        "kind": "example_translation",
        "target_ids": [
          "collocation:011"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "43b8fe04035e437529cb24a74677df60f7d66c4b2f25c8fee27238aa8f1a3675",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:012",
        "kind": "example_translation",
        "target_ids": [
          "collocation:012"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "509ba966ede82e1b103e8461e7092b2e5bcccba6e77731ba860850397c816a49",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:013",
        "kind": "example_translation",
        "target_ids": [
          "collocation:013"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "fff01262eb1dccb4fd32f0e2eb32aeb8abdc2ff0ef1c5bdcca2d9ce346ebd89d",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:001",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "a610295e5ff2f26df8c51c3804bd7d2fb7fd9bef0c6ea2226069e2ad051c2267",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:001",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "usage_note:001"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "fce9e9eb0b0e86ca9ca46179914e226d1702b8d93d1ac7cbe7296a1d33593011",
        "requires_evidence": true,
        "evidence_policy": "one_source"
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
          "synonym:005",
          "synonym:006",
          "synonym:007",
          "antonym:001",
          "antonym:002"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "8f736878ab0e9d199a8f894c89dbcbcc1394f9f4de4b4f48c89857e55868516e",
        "requires_evidence": true,
        "evidence_policy": "one_source"
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
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "89fc1b5e2d428e6fefd729018624e729e7e2b57f56d9581ebda3d064eb774113",
        "requires_evidence": true,
        "evidence_policy": "one_source"
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
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "2c47accf1ce6061c7483ee2f8f562bc4060b150b2b44eb71be08e88d03810f82",
        "requires_evidence": true,
        "evidence_policy": "one_source"
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
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "427a533105d1a80c9e7e9711ec761b7978f5f6b6ed253cf7657cd6f2e67c12f7",
        "requires_evidence": true,
        "evidence_policy": "one_source"
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
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "13c83d69d0fa89c485a0b340ac8cb8a50c78a14336fb1627bf49ab14d85d69d6",
        "requires_evidence": true,
        "evidence_policy": "one_source"
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
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "e49df7ae40a62796a41ec543a71c2a2abc0254cf5760f0e83f5b7ad12a5bc6d2",
        "requires_evidence": true,
        "evidence_policy": "one_source"
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
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "e5ff50c89df53a63eb6ecdd47f71dc7b7eb7634e50e5700f6839ea45e01cdaca",
        "requires_evidence": true,
        "evidence_policy": "one_source"
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
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "0fb4cb145a88d1d92f6f047acc26fed46a318f6095d0c99feb6d4a09df98c599",
        "requires_evidence": true,
        "evidence_policy": "one_source"
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
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "7f17fd1c436fa33927fdfbc47e9fc59cf04a74432528d64a3ef5eddf1f5d5ac7",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:009",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:009",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005",
          "collocation:006",
          "collocation:007",
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "197fe21c96c4d15e24e75dd4b9d22c3b1ede7864b8ada5b6bce9a2bba308b5f1",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:002",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "e254f29d0b4af1400fd7482afff3595556e4dd05869cb4266669e3b16e6c794a",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:002",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "usage_note:002"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "295f3faddf88fe94a54769f3154c01213f59a8ec5ddd08a484c4323874f639ed",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:002",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:002",
          "definition:002",
          "synonym:008",
          "synonym:009",
          "synonym:010",
          "synonym:011"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "bf898ab52dd9a0950e5938b74a67684853de2b3e230affe865459e51b8ed58db",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:010",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:010",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "db8aa8072b2f128bf0aee3de3394b3621752e60cd37b6f6a2559a758200d9b44",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:011",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:011",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "b17d48393ef30e2663edcc650c45e05de2b723b1d53af7a34f1adb09935e8607",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:012",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:012",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "88486c0f9a9c70bb32fa427b49ca1c732f0fd6f93422782c11317472f8ac7d03",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:013",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:013",
          "collocation:010",
          "collocation:011",
          "collocation:012",
          "collocation:013"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "e2d9e0e038070e98383cef068aa1133931119dc5990660fb2c4cb1ecb57b6b15",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "article_learning_risk:001",
        "kind": "article_learning_risk",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "usage_note:001",
          "sense_boundary:002",
          "definition:002",
          "usage_note:002"
        ],
        "description": "記事全体の語義構成、対比、訳語、限定表現から学習者が誤った一般化をしないことを横断確認する。",
        "text_sha256": "6975269d452c09226391c7d49aaf1487a45f00877b03422ff13a701e98d52110",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "IC-FB-001",
        "surface_form": "controversial",
        "frame": "a controversial issue/decision/figure/remark",
        "meaning": "論争を呼ぶ、賛否が分かれる、物議を醸す",
        "disposition": "included",
        "rationale": "The frame a controversial issue/decision/figure/remark supports the meaning 論争を呼ぶ、賛否が分かれる、物議を醸す because the adjective describes a subject that attracts strong public disagreement.",
        "semantic_assertions": [
          {
            "id": "IC-FB-001-SA-001",
            "statement": "The adjective applies to an issue, decision, figure, or remark that provokes substantial disagreement or criticism.",
            "polarity": "must_hold",
            "scope": "ordinary public-controversy use"
          },
          {
            "id": "IC-FB-001-SA-002",
            "statement": "The ordinary adjective does not by itself entail that the subject is false, illegal, bad, or deliberately provocative.",
            "polarity": "must_not_hold",
            "scope": "ordinary public-controversy boundary"
          }
        ]
      },
      {
        "id": "IC-FB-002",
        "surface_form": "controversial",
        "frame": "controversial among/within a group; controversial in some circles",
        "meaning": "特定の集団の中で論争を呼ぶ",
        "disposition": "included",
        "rationale": "The frame controversial among/within a group; controversial in some circles supports the meaning 特定の集団の中で論争を呼ぶ by restricting where the disagreement is reported.",
        "semantic_assertions": [
          {
            "id": "IC-FB-002-SA-001",
            "statement": "An among, within, or in-some-circles phrase can limit the community in which the controversy exists.",
            "polarity": "must_hold",
            "scope": "scoped controversy"
          }
        ]
      },
      {
        "id": "IC-FB-003",
        "surface_form": "controversial",
        "frame": "become/remain/prove controversial; highly or widely controversial",
        "meaning": "論争状態になる、論争状態が続く、論争の広がりや強さが大きい",
        "disposition": "included",
        "rationale": "The frame become/remain/prove controversial; highly or widely controversial shows that controversial can describe a changing or continuing state, with modifiers for intensity or reach.",
        "semantic_assertions": [
          {
            "id": "IC-FB-003-SA-001",
            "statement": "Become, remain, and prove can present controversy as a state that begins, continues, or becomes evident.",
            "polarity": "must_hold",
            "scope": "copular and resultative frames"
          },
          {
            "id": "IC-FB-003-SA-002",
            "statement": "Highly and widely distinguish strength of opposition from the breadth of the group involved.",
            "polarity": "must_hold",
            "scope": "degree and scope modifiers"
          }
        ]
      },
      {
        "id": "IC-FB-004",
        "surface_form": "controversial",
        "frame": "a controversial temperament/manner; be controversial by temperament",
        "meaning": "論争を好む、論争を引き起こしがちな、論争的な",
        "disposition": "included",
        "rationale": "The frame a controversial temperament/manner; be controversial by temperament supports the meaning 論争を好む、論争を引き起こしがちな、論争的な as a rare dispositional reading about a person's habitual conduct.",
        "semantic_assertions": [
          {
            "id": "IC-FB-004-SA-001",
            "statement": "A temperament, manner, or by-temperament frame can shift the adjective from public evaluation of a person to a rare description of disputatious disposition.",
            "polarity": "must_hold",
            "scope": "rare dispositional use"
          },
          {
            "id": "IC-FB-004-SA-002",
            "statement": "A controversial person in ordinary current usage must not automatically be interpreted as someone who enjoys arguing.",
            "polarity": "must_not_hold",
            "scope": "person-reading boundary"
          }
        ]
      },
      {
        "id": "IC-FB-005",
        "surface_form": "controversially",
        "frame": "controversially modify a claim, decision, or clause",
        "meaning": "物議を醸す形で、論争を呼ぶ形で",
        "disposition": "included",
        "rationale": "The frame controversially modify a claim, decision, or clause supports the meaning 物議を醸す形で、論争を呼ぶ形で as the adverbial form describing how an assertion or action is presented.",
        "semantic_assertions": [
          {
            "id": "IC-FB-005-SA-001",
            "statement": "Controversially is an adverbial derivative and does not create a new adjective sense of controversial.",
            "polarity": "must_hold",
            "scope": "adverbial derivation"
          }
        ]
      },
      {
        "id": "IC-FB-006",
        "surface_form": "controversy",
        "frame": "public controversy / a controversy over a policy",
        "meaning": "論争、論争点、物議",
        "disposition": "included",
        "rationale": "The frame public controversy / a controversy over a policy supports the meaning 論争、論争点、物議 as the noun naming the dispute associated with controversial subjects.",
        "semantic_assertions": [
          {
            "id": "IC-FB-006-SA-001",
            "statement": "Controversy is a related noun naming a dispute or contentious public issue, not an inflected form of the adjective.",
            "polarity": "must_hold",
            "scope": "noun derivation"
          }
        ]
      },
      {
        "id": "IC-FB-007",
        "surface_form": "controversialist",
        "frame": "a controversialist in a debate",
        "meaning": "論争家、論争に加わる人",
        "disposition": "included",
        "rationale": "The frame a controversialist in a debate supports the meaning 論争家、論争に加わる人 as a formal related noun for a participant or advocate in controversy.",
        "semantic_assertions": [
          {
            "id": "IC-FB-007-SA-001",
            "statement": "Controversialist refers to a person associated with controversy and remains a separate noun from controversial.",
            "polarity": "must_hold",
            "scope": "person-denoting derivation"
          }
        ]
      },
      {
        "id": "IC-FB-008",
        "surface_form": "controvert",
        "frame": "to controvert a claim",
        "meaning": "反論する、論駁する",
        "disposition": "included",
        "rationale": "The frame to controvert a claim supports the meaning 反論する、論駁する as a related verb for directly challenging a proposition, while remaining lexically separate from controversial.",
        "semantic_assertions": [
          {
            "id": "IC-FB-008-SA-001",
            "statement": "Controvert is a separate verb meaning to dispute or refute a claim and is not a direct inflection of controversial.",
            "polarity": "must_hold",
            "scope": "verb-family boundary"
          }
        ]
      }
    ],
    "finding_results": [],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U001",
        "source_fact_ids": [
          "F001",
          "F002",
          "F003",
          "F007",
          "F009",
          "F013",
          "F014"
        ],
        "canonical_statement": "Controversial commonly describes an issue, decision, claim, work, remark, or person that arouses strong public or group disagreement.",
        "disposition": "included",
        "rationale": "This is the high-frequency main adjective sense and is the first numbered sense."
      },
      {
        "id": "U002",
        "source_fact_ids": [
          "F008",
          "F013",
          "F015"
        ],
        "canonical_statement": "Controversial can rarely describe a person or temperament inclined to controversy or disputation.",
        "disposition": "included",
        "rationale": "The rare personality sense is retained because independent dictionaries record it and it prevents a person-use ambiguity."
      },
      {
        "id": "U003",
        "source_fact_ids": [
          "F005",
          "F010",
          "F016"
        ],
        "canonical_statement": "Controversial has a four-syllable pronunciation with main stress on the third syllable and a US variant with a more syllabic ending.",
        "disposition": "included",
        "rationale": "The pronunciation section records the mainstream British/American forms and qualifies the US variant."
      },
      {
        "id": "U004",
        "source_fact_ids": [
          "F006",
          "F011",
          "F016",
          "F017",
          "F018"
        ],
        "canonical_statement": "Controversial is a late-sixteenth-century adjective from late Latin controversialis, related to controversia and controversus.",
        "disposition": "included",
        "rationale": "The etymology section states the shared late-sixteenth-century range and avoids treating conflicting first-use dates as exact."
      },
      {
        "id": "U005",
        "source_fact_ids": [
          "F012"
        ],
        "canonical_statement": "Controversially, controversialist, controversialism, and controvert are related forms, with different parts of speech and frequency.",
        "disposition": "integrated",
        "rationale": "The formation section records useful related forms without presenting the adverb or nouns as additional senses of the headword."
      },
      {
        "id": "U006",
        "source_fact_ids": [
          "F004",
          "F015"
        ],
        "canonical_statement": "The public-disagreement adjective is a common B2-level word, while the personality sense is rare.",
        "disposition": "integrated",
        "rationale": "The two frequency/register labels are attached to their respective numbered senses."
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
        "id": "grammar_pattern:009",
        "status": null,
        "target_id": "grammar_pattern:009"
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
        "id": "collocation:009",
        "status": null,
        "target_id": "collocation:009"
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
        "id": "usage_note:002",
        "status": null,
        "target_id": "usage_note:002"
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
        "id": "synonym:010",
        "status": null,
        "target_id": "synonym:010"
      },
      {
        "id": "synonym:011",
        "status": null,
        "target_id": "synonym:011"
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
        "id": "pattern_example_coverage:009",
        "status": null,
        "relation_id": "pattern_example_coverage:009"
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
        "id": "article_learning_risk:001",
        "status": null,
        "relation_id": "article_learning_risk:001"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "IC-FB-001",
        "status": null,
        "assertion_ids": [
          "IC-FB-001-SA-001",
          "IC-FB-001-SA-002"
        ],
        "verified_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "id": "IC-FB-002",
        "status": null,
        "assertion_ids": [
          "IC-FB-002-SA-001"
        ],
        "verified_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "id": "IC-FB-003",
        "status": null,
        "assertion_ids": [
          "IC-FB-003-SA-001",
          "IC-FB-003-SA-002"
        ],
        "verified_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "id": "IC-FB-004",
        "status": null,
        "assertion_ids": [
          "IC-FB-004-SA-001",
          "IC-FB-004-SA-002"
        ],
        "verified_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "id": "IC-FB-005",
        "status": null,
        "assertion_ids": [
          "IC-FB-005-SA-001"
        ],
        "verified_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "id": "IC-FB-006",
        "status": null,
        "assertion_ids": [
          "IC-FB-006-SA-001"
        ],
        "verified_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "id": "IC-FB-007",
        "status": null,
        "assertion_ids": [
          "IC-FB-007-SA-001"
        ],
        "verified_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      },
      {
        "id": "IC-FB-008",
        "status": null,
        "assertion_ids": [
          "IC-FB-008-SA-001"
        ],
        "verified_body_sha256": "81a1d26c2b696bfd6afeee63cc863b8e3f8bcfbe0e9dd5fde1a124523d5379c5"
      }
    ],
    "finding_results": [],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U001",
        "status": null,
        "union_id": "U001"
      },
      {
        "id": "U002",
        "status": null,
        "union_id": "U002"
      },
      {
        "id": "U003",
        "status": null,
        "union_id": "U003"
      },
      {
        "id": "U004",
        "status": null,
        "union_id": "U004"
      },
      {
        "id": "U005",
        "status": null,
        "union_id": "U005"
      },
      {
        "id": "U006",
        "status": null,
        "union_id": "U006"
      }
    ],
    "input_revision_id": "57f7d106a93e336397261df4a2b2b9d564e5ab8162e207bce1b73d89545fb523"
  },
  "input_bindings": {
    "pass_findings.json": "5ab8621a0700b24bfed41cf9b0483dc934c48fee2dc2c04766139c12406d462e",
    "cold_review.json": "41d6e149b6197dad85ded0b0d6f691c2117bb0c8c5080212712b8cbff2364d6b",
    "final_blind.json": "54147ac24b193f8737e95401ce71bd6f90120569095a7d44b145b6461ca77270",
    "blind_seal.json": "2947cfda4ff9402e65ccad59931b8e4b6ea90ea4a6c3c8708ec813bbfddec62c",
    "pre_blind_resolution.json": "8750244c23ec6734a565ec09ef7870420a63590cdfc8f558cca5aacf5f50fb24",
    "pre_blind_revision.json": "1c9b5ea127b73527828b1910a3f704d58c4fbc6710eaeee59ed701007d48e1e3",
    "checker_recheck_manifest.json": "475420f02b21c3b18e9cb1dc895a9726290b3accfd32b94c0b63beefe540713c",
    "post_blind_resolution.json": "124823aaf85025868122d9233954180d1c801c47188a454efacc611400cff7d5",
    "post_blind_verification.json": "25b5523cbc201283b75c30aceceeb862d3fbb72a8edce7c77c7f7bcdc07c9f86",
    "targeted_adjudications.json": "af5af9b139e61078d584a712c70a3ce285f0407cc7fa63836b8195db9ea9f3b6",
    "source_inventory.json": "734557db9b02bd9276bf385175905aa54a6cf019d39be7e89ae65c879ad25fa2",
    "resolutions.json": "4b20b362c2c2cb4bad9781d9f2378c543b697dd8f41b694169d08ad1f7006776",
    "check_passes/checker_passes.stage1.json": "da8638cde022d5eed7dea32ab90548abcdaa0525513e26fbdf8c29901446abfa",
    "check_passes/evidence.json": "fa187120ec34820771c92a88ec88032d1a7e5bbd96a38918b13f2ff6281c73fd",
    "check_passes/evidence.request.json": "6071e0720d1feb831905e2c57009472d990d065300975bdfc283555010f92d4c",
    "check_passes/example-attribution.alignment-key.json": "618e2c10e056f5030e602dcc9aecdc85fb598bb76abd3739cd4c9dd1fb8b2e42",
    "check_passes/example-attribution.blind-record.json": "6271ea7a58ee322df684a89a3de4dc47c769fda23b431e1bcebab5806c249d1a",
    "check_passes/example-attribution.json": "0b3c25de4fc21ea1e587596b9fec7ee341e249e559734b04f40f424c5b06a969",
    "check_passes/example-attribution.request.json": "88297e8a6389307b78319531611ba39da2acc045aaf2185a5c2ea0a2bff7f7bb",
    "check_passes/frame-relation.antonym-axis.adjudication-record.json": "b8612d433851d1b76a979ad152aab5fdabcc3c73f024f386bb1dc9ed970c8458",
    "check_passes/frame-relation.antonym-axis.alignment-key.json": "9834ee27689e2eba9f84b8b93c0df59271e4244ba6bc1dd921c64c0be308c3f9",
    "check_passes/frame-relation.antonym-axis.blind-record.json": "e723c3b9708b015f47f2e2426e2c62daa8249d4d59a1baf244b4296a9449f67b",
    "check_passes/frame-relation.antonym-axis.stage2.request.json": "ccf9388474a06229f100cecc6df2b9bf293a019be8c3823b4bf1eec4bc5bc5f0",
    "check_passes/frame-relation.request.json": "a07e387f4b7f5815e6c3bef696773432d8b5152172b0af8216459d2ee15719cd",
    "check_passes/input_snapshot.json": "a9fea74e02531c285610a58f88720790d753258998a865fe085ab23923abf7f0",
    "check_passes/pronunciation.json": "f97e1a08ce5c8548dfae6613988252fe9d47609071ff210099d9b3b311aec346",
    "check_passes/pronunciation.request.json": "d05738e4f530b6e511cf98612cfe059240cd98c951a2478844cf7880677e9a0d",
    "check_passes/qualification.json": "ea13a2a0070008c7218ba586ca5574a343b4718d7984c1a7db45e684b85a20fc",
    "check_passes/qualification.request.json": "849cf064777f9614f8e04df488571fb6e5295a3ca4acd336da0a200ae7326084",
    "check_passes/sense-structure.json": "0c21b8957b267eba735288c47fcfdaf3c94578263e94aa3a2116e0e029184afd",
    "check_passes/sense-structure.request.json": "900b6f724170730a64500048800cd99e908f45e6428ecfa0e2462ca70d50054a",
    "check_passes/translation.json": "db45329c42582bdcbe90b4e6c551a95d2b3cbd7f313abe93f464ad322b1fbb0b",
    "check_passes/translation.request.json": "5335b53a4d9eec7a577bdb3ce135ea1456cc6e13e444ab94d501459fd8389167"
  },
  "contract_version": "review_preflight_v1",
  "input_revision_id": "57f7d106a93e336397261df4a2b2b9d564e5ab8162e207bce1b73d89545fb523"
}
```
