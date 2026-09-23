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
  "entry_body": "\n＃発音記号\n\n米: Oxford の米語IPAは /səˈspɪʃn/。Merriam-Webster は sus·pi·cion と3音節に区切り、第2音節に主強勢を示す。両辞書で表記形式が異なる。  \n\n＃語源\n\nsuspicion は中英語を経て、アングロフランス語・古フランス語からラテン語系の形へさかのぼる。辞書によってラテン語形は suspicio、suspectio、suspectio(n-) と記され、中継経路の説明にも差がある。Merriam-Webster は suspicere「疑う」に由来すると説明している。  \n\n＃語形成\n\n・suspicious：形容詞。「疑っている、不信に思っている」、または人に疑いを起こさせる「疑わしい」。  \n・suspiciously：副詞形。  \n・suspiciousness：名詞形。  \n・suspicion（動詞）は他動詞で「～を疑う」。Merriam-Webster では chiefly dialectal とされるため、以下の主要な学習語義には採録しない。  \n\n＃コアイメージ\n\n学習上は「確証のない段階で、ある事柄が真実かもしれないと考える」という見立てを中心にする。人の犯罪・不正を疑う用法はその具体例であり、suspicion that ... の節には別の出来事や状態も続く。人や物事を信用できず疑いの目で見る用法は、対象への不信・警戒という態度に焦点を置く。a suspicion of a smile / truth は「ごく少量・かすかな兆し」を表す形式的な比喩用法。この整理は学習上の目安で、全用法が一つの語源的意味を共有するという主張ではない。  \n\n＃意味・用法・関連表現\n\nこの節の各語義・類義語の頻度スコアは、英語全体での遭遇頻度を entry_spec_v5 の10段階基準に照らした編集上の定性的推定である。厳密なコーパス集計値や辞書掲載の数値ではなく、地域・専門・古風な用法を過大評価しない目安として付けている。類義語のスコアは、各項目の「定義」に示す意味に限る。  \n\n1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い\n\n【日本語訳・定義】確証がない段階で、ある事柄が真実かもしれないと考えることを表す。人が犯罪・不正をした可能性への疑いもこの意味に含む。Oxfordは犯罪・不正の疑いでは可算・不可算の両用法を、命題の真偽については可算用法を記している。  \n\n【頻度】〈8/10〉  \n\n【レジスター/領域】標準語。犯罪・不正の可能性から、会議の中止など出来事や状態の真偽まで、確証のない考えを述べる。  \n\n【文法パターン】suspicion that 〈clause〉＝～ではないかという疑い／have a suspicion that 〈clause〉＝～ではないかという疑いを抱く／arouse 〈person〉's suspicions that 〈clause〉＝〈人〉に～ではないかという疑いを起こさせる／raise some suspicion＝疑いを招く／on suspicion of 〈offence〉＝〈犯罪〉の容疑で／be under suspicion＝疑いをかけられている。  \n\n【コロケーション】\n\n・on suspicion of 〈crime〉  \n用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕・拘束したことを述べる。  \n例: Two people were arrested on suspicion of fraud after the investigation.  \n訳: 捜査後、2人が詐欺の容疑で逮捕された。  \n\n・be under suspicion  \n用途: 人が不正や犯罪をしたのではないかと疑われている状態を表す。  \n例: The contractor remained under suspicion while investigators checked whether it had falsified invoices.  \n訳: 請求書を改ざんしたかどうかを捜査員が調べる間、その請負業者は疑いをかけられたままだった。  \n\n・a suspicion that 〈clause〉  \n用途: 確証がない段階で、節の内容が事実かもしれないという見立てを表す。  \n例: The manager had a suspicion that the cashier had altered the sales records.  \n訳: その管理者は、レジ係が売上記録を改ざんしたのではないかと疑っていた。  \n\n・have a suspicion that 〈clause〉  \n用途: 出来事や状態が実際に起きた、または成り立つのではないかという考えを抱く。  \n例: I had a suspicion that the meeting had been canceled.  \n訳: 会議は中止されたのではないかと私は疑っていた。  \n\n・arouse someone's suspicions  \n用途: ある出来事を受け、〈人〉が節の内容を真実かもしれないと疑うきっかけになる。  \n例: The abrupt policy reversal aroused residents' suspicions that officials had concealed the project's true cost.  \n訳: 突然の方針転換を受けて、住民たちは当局が事業の本当の費用を隠していたのではないかと疑い始めた。  \n\n・raise some suspicion  \n用途: ある発言や出来事が疑いを招くことを表す。  \n例: The unexplained delay raised some suspicion.  \n訳: 説明のつかない遅れが、多少の疑いを招いた。  \n\n【語法・注意】on suspicion of theft は「窃盗で有罪になった」ではなく、「窃盗をした疑いを理由に」という意味である。under suspicion も罪が確定した状態を表さない。Merriam-Webster の法律辞典は suspicion を通常、信念に至らない精神状態として説明し、reasonable suspicion の項目に関連づけている。ここでは特定の法域の法的基準を述べない。  \n\n【類義語】\n\n・doubt  \n定義: ある事柄の真偽について確信が持てない状態。  \n頻度: 〈8/10〉  \n違い: doubt は真偽の不確かさを広く表し、suspicion はある事柄が真実かもしれないという見立ても表す。  \n例: There was some doubt about whether the meeting had been canceled.  \n訳: 会議が中止されたかどうかについて、多少の疑問があった。  \n\n2. 【名詞・可算／不可算】不信、警戒を伴う疑念\n\n【日本語訳・定義】人や物事を十分に信用できず、疑いの目で見る態度を表す。ある事柄が真実かどうかについての見立てを表す語義1とは異なり、対象への不信や警戒に焦点を置く。  \n\n【頻度】〈7/10〉  \n\n【レジスター/領域】標準語。人や物事、説明などを信用できず、疑いの目で見る態度を述べる。  \n\n【文法パターン】regard 〈person/thing〉 with suspicion＝〈人・物事〉を疑いの目で見る。  \n\n【コロケーション】\n\n・regard 〈person/thing〉 with suspicion  \n用途: 人や物事をすぐには信用せず、疑いの目で見ることを表す。  \n例: Residents regarded the sudden policy change with suspicion.  \n訳: 住民たちは突然の方針変更を疑いの目で見た。  \n\n【語法・注意】with suspicion は、対象を信頼できるか疑って見る態度を表す。  \n\n【類義語】\n\n・distrust  \n定義: 人や物事を信頼できない気持ち。  \n頻度: 〈8/10〉  \n違い: distrust は信頼できない気持ちを直接表し、with suspicion は人や物事を疑いの目で見る態度を表す。Oxford Advanced American Dictionary は suspicion の第3語義を「人や物事を信頼できない気持ち」と説明し、両者の意味の重なりを示す。  \n例: Residents regarded the proposal with distrust.  \n訳: 住民たちはその提案を信用しなかった。  \n\n3. 【名詞・単数／形式的】ごく少量、かすかな兆し\n\n【日本語訳・定義】ものがごく少量、またはかすかな兆候として感じられることを表す。通常 a suspicion of ... の形で使われる。  \n\n【頻度】〈2/10〉  \n\n【レジスター/領域】単数形で用いる形式的な用法。  \n\n【文法パターン】a suspicion of 〈a smile〉＝笑みがかすかに感じられること／a suspicion of 〈truth〉＝真実味がかすかに感じられること。  \n\n【コロケーション】\n\n・a suspicion of a smile  \n用途: はっきり表れるほどではない、かすかな兆しを描写する。  \n例: There was a suspicion of a smile in her reply.  \n訳: 彼女の返事にはかすかな笑みが感じられた。  \n\n・a suspicion of truth  \n用途: 話や印象に真実味がかすかに感じられることを表す。  \n例: The old tale had a suspicion of truth in it.  \n訳: その古い物語には、どこか真実味が感じられた。  \n\n【語法・注意】この a suspicion of ... は「～を疑うこと」ではなく、「～がごく少量、または兆候としてわずかに感じられること」である。  \n\n【類義語】\n\n・hint  \n定義: Oxfordがこのごく少量・かすかな兆しの語義で挙げる類義語。  \n頻度: 〈8/10〉  \n違い: Oxfordはhintをこの語義の類義語として挙げ、suspicionの用法をformalと記している。  \n例: The tea has a hint of mint.  \n訳: そのお茶にはほのかなミントの風味がある。  \n\n・trace  \n定義: ごくわずかな量や痕跡を表す語。Merriam-Websterは本語義の類義語として挙げている。  \n頻度: 〈8/10〉  \n違い: Merriam-Websterはsuspicionの本語義をbarely detectable amount or traceと説明し、Oxfordはこの用法をformalとしている。  \n例: There was only a trace of smoke in the air.  \n訳: 空気中には煙がほんのわずかに漂っていた。  ",
  "_output_metadata": {
    "schema_version": "final_review_v3",
    "stage": "final_review",
    "run_id": "blind-suspicion-20260911T033430Z-c12c3ef3",
    "context_id": "blind-suspicion-context-20260911T033430Z-c12c3ef3",
    "input_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426",
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
    "cold_review_summary": "問題候補4件。語源のラテン語形と語源分解、語義3の可算性、類義語 allegation の定義に修正候補があります。",
    "final_blind_decision": "pass",
    "blind_seal": {
      "schema_version": "blind_seal_v3",
      "stage": "blind_seal",
      "entry_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-13/final-blind-input/suspicion.md",
      "body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426",
      "final_blind_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/final_blind.json",
      "final_blind_sha256": "3b46694c88288392c04b42633c7521334d590a6bd086272d8deeafca02944596",
      "blind_output_sha256": "a58762b9171b13a836e25df65019386c31219cfe51a830e2c6c6532b01d61421",
      "sealed_at": "2026-09-23T09:25:58.075956-07:00"
    },
    "checker_recheck": {
      "current_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426",
      "full_recheck": true,
      "invalidated_passes": [
        "evidence",
        "example-attribution",
        "frame-relation",
        "pronunciation",
        "qualification",
        "sense-structure",
        "translation"
      ],
      "pass_results": [
        {
          "pass_id": "translation",
          "mode": "rechecked",
          "spec_sha256": "d09d822f58ea8bcff9aa2890f988ad7aca9a9d3a773b5f9da5427f783ae25bb3",
          "normalized_input_sha256": "97c729dc40110cdabaee4b8d0ca21ddb368f8addd165a5e0c5f64676bbbe762d",
          "source_artifact_sha256": "cff7da1f22ae25fe071b48da51af07d50df1d6d825a6330a6abac5cdfc52420c",
          "output_sha256": "804c26272e886aa2e5cb563f0abd4ac0012be48218bf4a9f76758ccda8fad269",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reviewer_agent_id": "/root/r12_translation",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-6",
            "ingested_by": "human",
            "agent_id": "/root/r12_translation"
          },
          "request_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/translation.request.json",
          "request_sha256": "b2c2544e0a78751e7be529b06cdeb282beeea211a85e14102d9e73cc0f8681f5",
          "output_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/translation.response.normalized.json",
          "validated_on_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
        },
        {
          "pass_id": "sense-structure",
          "mode": "rechecked",
          "spec_sha256": "a815b90fbc456e2bc194220ee0f3bfa164790bbb6e1f2f740144ac62bb03b87c",
          "normalized_input_sha256": "559d0209d6e62e6364dcb06479792ece9d5a793ab4924f2a885019d1186e6572",
          "source_artifact_sha256": "cff7da1f22ae25fe071b48da51af07d50df1d6d825a6330a6abac5cdfc52420c",
          "output_sha256": "3051cef1e80880423ce42d6c5668d033da8462bd8ce5ce79b73fa4c9c83897e0",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reviewer_agent_id": "/root/r12_sense_structure",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-6",
            "ingested_by": "human",
            "agent_id": "/root/r12_sense_structure"
          },
          "request_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/sense-structure.request.json",
          "request_sha256": "f530969e598b82ed4eb7dad8bcc71d3de4a9fa03401c6da99d8e44999002a6da",
          "output_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/sense-structure.response.normalized.json",
          "validated_on_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
        },
        {
          "pass_id": "frame-relation",
          "mode": "rechecked",
          "spec_sha256": "3598ca81a5784639c6b43a0806d0981a985bf4174f424c744aad1dde787bfcef",
          "normalized_input_sha256": "fcf76b799739b4390b77c92dbad61f4974f578b0fcdeab80f7383cde7c0644c0",
          "source_artifact_sha256": "cff7da1f22ae25fe071b48da51af07d50df1d6d825a6330a6abac5cdfc52420c",
          "output_sha256": "0048125f04e7bfaaa4a33e8c0e98d9eb76a2afdf60a0ab6e1856f8206b0b391b",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reviewer_agent_id": "/root/round13_frame_recovery",
          "reviewer": {
            "mode": "handoff",
            "agent_id": "/root/round13_frame_recovery",
            "declared_model": "GPT-6",
            "ingested_by": "human"
          },
          "request_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-13/frame-relation.request.json",
          "request_sha256": "8846e60a4bd98aef02fddd11ee833adb9713472d96f19a6ea8486dafc68cefd1",
          "output_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-13/frame-relation.output.json",
          "validated_on_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
        },
        {
          "pass_id": "example-attribution",
          "mode": "rechecked",
          "spec_sha256": "e0bbb032bc0c50bf9bef5ff8f7854188287e635c58e599479891e11e3343a017",
          "normalized_input_sha256": "f4ac58d3edc658e61455477c2f21c66ad1caa179f51bac847cd6761f33f56c9a",
          "source_artifact_sha256": "cff7da1f22ae25fe071b48da51af07d50df1d6d825a6330a6abac5cdfc52420c",
          "output_sha256": "28474b4705229e2e606e45984823189e9994186465f3d791c6888f737901efc3",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reviewer_agent_id": "/root/r12_example_attribution",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-6",
            "ingested_by": "human",
            "agent_id": "/root/r12_example_attribution"
          },
          "request_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/example-attribution.request.json",
          "request_sha256": "84891627b935735d32bbcc11155738e4e16880161da345404db329ae8729de98",
          "output_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/example-attribution.output.json",
          "validated_on_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
        },
        {
          "pass_id": "qualification",
          "mode": "rechecked",
          "spec_sha256": "1cf8a434bbe1213c0ef739f4c47ffb41014ab2cd5156d297471af6df85ae40a2",
          "normalized_input_sha256": "716956ff765cc58410adf7650e858d8a58fcda13ba6c02b05f2f1b7f1d008fe4",
          "source_artifact_sha256": "cff7da1f22ae25fe071b48da51af07d50df1d6d825a6330a6abac5cdfc52420c",
          "output_sha256": "cfb2c9b8fa445311d5b84d76ebfeaa9ed2b1866d9add5daf0c7084e700030a24",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reviewer_agent_id": "/root/r12_qualification",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-6",
            "ingested_by": "human",
            "agent_id": "/root/r12_qualification"
          },
          "request_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/qualification.request.json",
          "request_sha256": "7552352d5dec534d653e1452aa2f8e80bdcce0f3584a289fc4c2bed2187c1452",
          "output_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/qualification.response.normalized.json",
          "validated_on_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
        },
        {
          "pass_id": "pronunciation",
          "mode": "rechecked",
          "spec_sha256": "7e3e94267ac9f917c901c12580b91e570b5989df7adfbf2a39b833478c766d8a",
          "normalized_input_sha256": "0ef29c95e58d9d9a542caa03a61c36787c136056342ebef9a19c6a14c52c2a5e",
          "source_artifact_sha256": "cff7da1f22ae25fe071b48da51af07d50df1d6d825a6330a6abac5cdfc52420c",
          "output_sha256": "122a1301b22a7c5d44dd8907488eebee4782213062384345f1952d6fe9e0a87f",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reviewer_agent_id": "/root/r12_pronunciation",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-6",
            "ingested_by": "human",
            "agent_id": "/root/r12_pronunciation"
          },
          "request_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/pronunciation.request.json",
          "request_sha256": "0372741f6509643b2705cbeae23662847c08ad9b56d01851996a6df6ab9a3917",
          "output_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/pronunciation.response.normalized.json",
          "validated_on_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
        },
        {
          "pass_id": "evidence",
          "mode": "rechecked",
          "spec_sha256": "f0de393d4d064190e23916b2e8bfda25b2b83fd29e14cf52395c894b8539d7e9",
          "normalized_input_sha256": "f6169088c913e6e68f647d2917932fa5dc4dad6642faf31c835e22c086aeb0ef",
          "source_artifact_sha256": "cff7da1f22ae25fe071b48da51af07d50df1d6d825a6330a6abac5cdfc52420c",
          "output_sha256": "d204080c8d138facbabe706b73f0aa4515011b39f43b4726c0644267f82fc6cd",
          "schema_valid": true,
          "reviewer_independent": true,
          "request_binding_valid": true,
          "reviewer_agent_id": "/root/r12_evidence",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-6",
            "ingested_by": "human",
            "agent_id": "/root/r12_evidence"
          },
          "request_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/evidence.request.json",
          "request_sha256": "03af35fb01ddcf8d223c433166501e0f4310576830e2cfab87b437e51c5fb3d6",
          "output_path": "audits/runs/s/suspicion/20260911T033430Z-c12c3ef3/recheck/round-12/evidence.response.normalized.json",
          "validated_on_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
        }
      ]
    },
    "post_blind_verification": {
      "schema_version": "post_blind_verification_v1",
      "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426",
      "verified_at": "2026-09-23T16:31:46.390608+00:00",
      "checker_recheck_completed": true,
      "checker_recheck_manifest_sha256": "0663c2ccba935c7c036bf60e469eecd0673fb94f95bcb63f39329a9357a7adf6",
      "final_blind_repeated": false,
      "final_blind_sha256": "3b46694c88288392c04b42633c7521334d590a6bd086272d8deeafca02944596",
      "final_blind_attempt": 1,
      "adopted_post_blind_findings": 0
    },
    "resolutions": [
      {
        "id": "CHK-sense-structure-85e67bdbf80f0e5b",
        "finding_id": "CHK-sense-structure-85e67bdbf80f0e5b",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "コアイメージを確証のない見立てを中心にした学習上の目安として改め、少量・兆しの語義を併記し、全用法が共通の語源的意味を持つとの主張ではないことを明記した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-frame-relation-f20791f0cfdbd2ce",
        "finding_id": "CHK-frame-relation-f20791f0cfdbd2ce",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "cast suspicion on の対象枠と文書の真正性を扱う例を削除し、残したthat節・容疑・raise some suspicionの枠に整理した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-frame-relation-f487dc58051550c5",
        "finding_id": "CHK-frame-relation-f487dc58051550c5",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "対象枠を person/thing とし、方針変更など物事を対象とする本文例が含まれるよう記述を改めた。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-frame-relation-61011dbd10a9eca3",
        "finding_id": "CHK-frame-relation-61011dbd10a9eca3",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "accusation は疑いそのものと異なるため、語義1の類義語欄から削除した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-frame-relation-c6cc8ed5c1faed74",
        "finding_id": "CHK-frame-relation-c6cc8ed5c1faed74",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "allegation は公に提示する主張であり疑いそのものではないため、類義語欄から削除した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-example-attribution-9a7ced3d899cef25",
        "finding_id": "CHK-example-attribution-9a7ced3d899cef25",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "曖昧な資金移動の例を外し、犯罪名を明示する on suspicion of fraud の例に置き換えた。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-example-attribution-4b73cc547d6ec54a",
        "finding_id": "CHK-example-attribution-4b73cc547d6ec54a",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "文書の真正性を対象にするcast suspicion onの例を削除し、犯罪・不正への疑いと分かる例に整理した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-example-attribution-4e805feccd4e0426",
        "finding_id": "CHK-example-attribution-4e805feccd4e0426",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "対象が曖昧なmanager’s suspicionsの例を外し、売上記録の改ざんを疑うthat節の例に置き換えた。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-example-attribution-02488c6d692d08e3",
        "finding_id": "CHK-example-attribution-02488c6d692d08e3",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "agencyへのsuspicion例を削除し、出典で確認できる人・物事を疑いの目で見る態度の例に絞った。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-example-attribution-ef69a9c2d1737319",
        "finding_id": "CHK-example-attribution-ef69a9c2d1737319",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "語義1と語義2の両方に読めるdeep suspicionの例を削除した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-example-attribution-3c70c60e3ba74cda",
        "finding_id": "CHK-example-attribution-3c70c60e3ba74cda",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "語義2と少量・兆しの語義のどちらにも読めるprocess例を削除し、原因を述べるraise some suspicionの例に整理した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-example-attribution-85f2d8aab19a336e",
        "finding_id": "CHK-example-attribution-85f2d8aab19a336e",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "複数の語義に取れるdispelled suspicionの例を削除し、犯罪・不正の疑いまたは命題内容が明示された例に整理した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-evidence-f26152139b13f089",
        "finding_id": "CHK-evidence-f26152139b13f089",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "発音の記述をOxfordの米語IPAとMerriam-Websterの音節区切り・強勢情報に限定し、未確認のCambridge比較を削除した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-evidence-1cb0e731e8d76698",
        "finding_id": "CHK-evidence-1cb0e731e8d76698",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "語源を出典別に確認できる歴史的形と経路の差に限定し、未確認の語素分解と現代語への意味継承の断定を削除した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-evidence-7bf51b857c089ddc",
        "finding_id": "CHK-evidence-7bf51b857c089ddc",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "語形成欄を出典で確認できるsuspiciousの用法と派生語の品詞に絞り、未確認だったsuspectの詳しい語義や副詞の意味・頻度の主張を削除した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-evidence-1d48282c2269ad9b",
        "finding_id": "CHK-evidence-1d48282c2269ad9b",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "広い使用域や句の相対頻度を断定する文を削り、頻度スコアを編集上の定性的推定と明記して、容疑表現と確証前の境界を区別した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-evidence-c694e2ed8a394b1d",
        "finding_id": "CHK-evidence-c694e2ed8a394b1d",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "根拠のないsuspicion of + person/group/ideaの枠とagency例を削除し、確認できるwith suspicionの態度構文を残した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-evidence-1c2014f25502d6e7",
        "finding_id": "CHK-evidence-1c2014f25502d6e7",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "頻度スコアが編集上の推定であると明記し、distrustの定義と語義差を出典が支える範囲に狭めた。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-evidence-74f1211675818881",
        "finding_id": "CHK-evidence-74f1211675818881",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "根拠のないmistrustとの比較と類義語項目を削除した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-evidence-4f7613fe6f400031",
        "finding_id": "CHK-evidence-4f7613fe6f400031",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "未確認のwith a suspicion of smile/irony構文を削除し、辞書で確認できるa suspicion of a smile / truthの形に改めた。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CHK-evidence-6e65bce7c7568c72",
        "finding_id": "CHK-evidence-6e65bce7c7568c72",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "動詞用法の注記を語形成欄へ移してchiefly dialectalと出典ラベルに合わせ、確認できない標準用法との比較を削除した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CR-1",
        "finding_id": "CR-1",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "ラテン語形を一つに断定せず、記録済み辞書の異表記を出典別に記載した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CR-2",
        "finding_id": "CR-2",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "「ひそかに」の語義、sub-/specereの語素分解、現代語の意味へ直結させる説明を削除した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CR-3",
        "finding_id": "CR-3",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "命題の真偽を扱う用法を独立語義として過分割せず、可算・不可算の説明を出典ごとの範囲に限定した。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "CR-4",
        "finding_id": "CR-4",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "allegationを類義語として扱う項目を削除し、公的・私的範囲の未確認な主張を残さなかった。",
        "resolved_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
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
        "text": "米: Oxford の米語IPAは /səˈspɪʃn/。Merriam-Webster は sus·pi·cion と3音節に区切り、第2音節に主強勢を示す。両辞書で表記形式が異なる。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text": "suspicion は中英語を経て、アングロフランス語・古フランス語からラテン語系の形へさかのぼる。辞書によってラテン語形は suspicio、suspectio、suspectio(n-) と記され、中継経路の説明にも差がある。Merriam-Webster は suspicere「疑う」に由来すると説明している。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text": "・suspicious：形容詞。「疑っている、不信に思っている」、または人に疑いを起こさせる「疑わしい」。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text": "・suspiciously：副詞形。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text": "・suspiciousness：名詞形。"
      },
      {
        "id": "word_formation:004",
        "kind": "word_formation",
        "location": "line:15",
        "section": "＃語形成",
        "sense": "",
        "text": "・suspicion（動詞）は他動詞で「～を疑う」。Merriam-Webster では chiefly dialectal とされるため、以下の主要な学習語義には採録しない。"
      },
      {
        "id": "core_image:001",
        "kind": "core_image",
        "location": "line:19",
        "section": "＃コアイメージ",
        "sense": "",
        "text": "学習上は「確証のない段階で、ある事柄が真実かもしれないと考える」という見立てを中心にする。人の犯罪・不正を疑う用法はその具体例であり、suspicion that ... の節には別の出来事や状態も続く。人や物事を信用できず疑いの目で見る用法は、対象への不信・警戒という態度に焦点を置く。a suspicion of a smile / truth は「ごく少量・かすかな兆し」を表す形式的な比喩用法。この整理は学習上の目安で、全用法が一つの語源的意味を共有するという主張ではない。"
      },
      {
        "id": "narrative:001",
        "kind": "narrative",
        "location": "line:23",
        "section": "＃意味・用法・関連表現",
        "sense": "",
        "text": "この節の各語義・類義語の頻度スコアは、英語全体での遭遇頻度を entry_spec_v5 の10段階基準に照らした編集上の定性的推定である。厳密なコーパス集計値や辞書掲載の数値ではなく、地域・専門・古風な用法を過大評価しない目安として付けている。類義語のスコアは、各項目の「定義」に示す意味に限る。"
      },
      {
        "id": "sense_boundary:001",
        "kind": "sense_boundary",
        "location": "line:25",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:27",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "確証がない段階で、ある事柄が真実かもしれないと考えることを表す。人が犯罪・不正をした可能性への疑いもこの意味に含む。Oxfordは犯罪・不正の疑いでは可算・不可算の両用法を、命題の真偽については可算用法を記している。"
      },
      {
        "id": "frequency:001",
        "kind": "frequency",
        "location": "line:29",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "〈8/10〉"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:31",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "標準語。犯罪・不正の可能性から、会議の中止など出来事や状態の真偽まで、確証のない考えを述べる。"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "suspicion that 〈clause〉＝～ではないかという疑い"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "have a suspicion that 〈clause〉＝～ではないかという疑いを抱く"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "arouse 〈person〉's suspicions that 〈clause〉＝〈人〉に～ではないかという疑いを起こさせる"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "raise some suspicion＝疑いを招く"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "on suspicion of 〈offence〉＝〈犯罪〉の容疑で"
      },
      {
        "id": "grammar_pattern:006",
        "kind": "grammar_pattern",
        "location": "line:33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "be under suspicion＝疑いをかけられている。"
      },
      {
        "id": "collocation:001",
        "kind": "collocation",
        "location": "lines:37-40",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "・on suspicion of 〈crime〉\n用途: 警察などが、ある犯罪を行った疑いを理由に人を逮捕・拘束したことを述べる。\n例: Two people were arrested on suspicion of fraud after the investigation.\n訳: 捜査後、2人が詐欺の容疑で逮捕された。"
      },
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:42-45",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "・be under suspicion\n用途: 人が不正や犯罪をしたのではないかと疑われている状態を表す。\n例: The contractor remained under suspicion while investigators checked whether it had falsified invoices.\n訳: 請求書を改ざんしたかどうかを捜査員が調べる間、その請負業者は疑いをかけられたままだった。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:47-50",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "・a suspicion that 〈clause〉\n用途: 確証がない段階で、節の内容が事実かもしれないという見立てを表す。\n例: The manager had a suspicion that the cashier had altered the sales records.\n訳: その管理者は、レジ係が売上記録を改ざんしたのではないかと疑っていた。"
      },
      {
        "id": "collocation:004",
        "kind": "collocation",
        "location": "lines:52-55",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "・have a suspicion that 〈clause〉\n用途: 出来事や状態が実際に起きた、または成り立つのではないかという考えを抱く。\n例: I had a suspicion that the meeting had been canceled.\n訳: 会議は中止されたのではないかと私は疑っていた。"
      },
      {
        "id": "collocation:005",
        "kind": "collocation",
        "location": "lines:57-60",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "・arouse someone's suspicions\n用途: ある出来事を受け、〈人〉が節の内容を真実かもしれないと疑うきっかけになる。\n例: The abrupt policy reversal aroused residents' suspicions that officials had concealed the project's true cost.\n訳: 突然の方針転換を受けて、住民たちは当局が事業の本当の費用を隠していたのではないかと疑い始めた。"
      },
      {
        "id": "collocation:006",
        "kind": "collocation",
        "location": "lines:62-65",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "・raise some suspicion\n用途: ある発言や出来事が疑いを招くことを表す。\n例: The unexplained delay raised some suspicion.\n訳: 説明のつかない遅れが、多少の疑いを招いた。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:67",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "on suspicion of theft は「窃盗で有罪になった」ではなく、「窃盗をした疑いを理由に」という意味である。under suspicion も罪が確定した状態を表さない。Merriam-Webster の法律辞典は suspicion を通常、信念に至らない精神状態として説明し、reasonable suspicion の項目に関連づけている。ここでは特定の法域の法的基準を述べない。"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:71-76",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【名詞・可算／不可算】疑い、推測：ある事柄が真実かもしれないと考えること。特に犯罪・不正への疑い",
        "text": "・doubt\n定義: ある事柄の真偽について確信が持てない状態。\n頻度: 〈8/10〉\n違い: doubt は真偽の不確かさを広く表し、suspicion はある事柄が真実かもしれないという見立ても表す。\n例: There was some doubt about whether the meeting had been canceled.\n訳: 会議が中止されたかどうかについて、多少の疑問があった。"
      },
      {
        "id": "sense_boundary:002",
        "kind": "sense_boundary",
        "location": "line:78",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念"
      },
      {
        "id": "definition:002",
        "kind": "definition",
        "location": "line:80",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text": "人や物事を十分に信用できず、疑いの目で見る態度を表す。ある事柄が真実かどうかについての見立てを表す語義1とは異なり、対象への不信や警戒に焦点を置く。"
      },
      {
        "id": "frequency:002",
        "kind": "frequency",
        "location": "line:82",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text": "〈7/10〉"
      },
      {
        "id": "register:002",
        "kind": "register",
        "location": "line:84",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text": "標準語。人や物事、説明などを信用できず、疑いの目で見る態度を述べる。"
      },
      {
        "id": "grammar_pattern:007",
        "kind": "grammar_pattern",
        "location": "line:86",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text": "regard 〈person/thing〉 with suspicion＝〈人・物事〉を疑いの目で見る。"
      },
      {
        "id": "collocation:007",
        "kind": "collocation",
        "location": "lines:90-93",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text": "・regard 〈person/thing〉 with suspicion\n用途: 人や物事をすぐには信用せず、疑いの目で見ることを表す。\n例: Residents regarded the sudden policy change with suspicion.\n訳: 住民たちは突然の方針変更を疑いの目で見た。"
      },
      {
        "id": "usage_note:002",
        "kind": "usage_note",
        "location": "line:95",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text": "with suspicion は、対象を信頼できるか疑って見る態度を表す。"
      },
      {
        "id": "synonym:002",
        "kind": "synonym",
        "location": "lines:99-104",
        "section": "＃意味・用法・関連表現",
        "sense": "2. 【名詞・可算／不可算】不信、警戒を伴う疑念",
        "text": "・distrust\n定義: 人や物事を信頼できない気持ち。\n頻度: 〈8/10〉\n違い: distrust は信頼できない気持ちを直接表し、with suspicion は人や物事を疑いの目で見る態度を表す。Oxford Advanced American Dictionary は suspicion の第3語義を「人や物事を信頼できない気持ち」と説明し、両者の意味の重なりを示す。\n例: Residents regarded the proposal with distrust.\n訳: 住民たちはその提案を信用しなかった。"
      },
      {
        "id": "sense_boundary:003",
        "kind": "sense_boundary",
        "location": "line:106",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し"
      },
      {
        "id": "definition:003",
        "kind": "definition",
        "location": "line:108",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "ものがごく少量、またはかすかな兆候として感じられることを表す。通常 a suspicion of ... の形で使われる。"
      },
      {
        "id": "frequency:003",
        "kind": "frequency",
        "location": "line:110",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "〈2/10〉"
      },
      {
        "id": "register:003",
        "kind": "register",
        "location": "line:112",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "単数形で用いる形式的な用法。"
      },
      {
        "id": "grammar_pattern:008",
        "kind": "grammar_pattern",
        "location": "line:114",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "a suspicion of 〈a smile〉＝笑みがかすかに感じられること"
      },
      {
        "id": "grammar_pattern:009",
        "kind": "grammar_pattern",
        "location": "line:114",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "a suspicion of 〈truth〉＝真実味がかすかに感じられること。"
      },
      {
        "id": "collocation:008",
        "kind": "collocation",
        "location": "lines:118-121",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "・a suspicion of a smile\n用途: はっきり表れるほどではない、かすかな兆しを描写する。\n例: There was a suspicion of a smile in her reply.\n訳: 彼女の返事にはかすかな笑みが感じられた。"
      },
      {
        "id": "collocation:009",
        "kind": "collocation",
        "location": "lines:123-126",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "・a suspicion of truth\n用途: 話や印象に真実味がかすかに感じられることを表す。\n例: The old tale had a suspicion of truth in it.\n訳: その古い物語には、どこか真実味が感じられた。"
      },
      {
        "id": "usage_note:003",
        "kind": "usage_note",
        "location": "line:128",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "この a suspicion of ... は「～を疑うこと」ではなく、「～がごく少量、または兆候としてわずかに感じられること」である。"
      },
      {
        "id": "synonym:003",
        "kind": "synonym",
        "location": "lines:132-137",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "・hint\n定義: Oxfordがこのごく少量・かすかな兆しの語義で挙げる類義語。\n頻度: 〈8/10〉\n違い: Oxfordはhintをこの語義の類義語として挙げ、suspicionの用法をformalと記している。\n例: The tea has a hint of mint.\n訳: そのお茶にはほのかなミントの風味がある。"
      },
      {
        "id": "synonym:004",
        "kind": "synonym",
        "location": "lines:139-144",
        "section": "＃意味・用法・関連表現",
        "sense": "3. 【名詞・単数／形式的】ごく少量、かすかな兆し",
        "text": "・trace\n定義: ごくわずかな量や痕跡を表す語。Merriam-Websterは本語義の類義語として挙げている。\n頻度: 〈8/10〉\n違い: Merriam-Websterはsuspicionの本語義をbarely detectable amount or traceと説明し、Oxfordはこの用法をformalとしている。\n例: There was only a trace of smoke in the air.\n訳: 空気中には煙がほんのわずかに漂っていた。"
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
        "description": "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: definition:002 explicitly contrasts sense 2 with sense 1"
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
          "synonym:001"
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
          "collocation:006"
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
          "collocation:006"
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
          "collocation:006"
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
          "collocation:006"
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
          "collocation:006"
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
          "collocation:006"
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
          "synonym:002"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。"
      },
      {
        "id": "pattern_example_coverage:007",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:007",
          "collocation:007"
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
          "synonym:003",
          "synonym:004"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。"
      },
      {
        "id": "pattern_example_coverage:008",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:008",
          "collocation:008",
          "collocation:009"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。"
      },
      {
        "id": "pattern_example_coverage:009",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:009",
          "collocation:008",
          "collocation:009"
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
        "id": "article_learning_risk:001",
        "kind": "article_learning_risk",
        "target_ids": [
          "core_image:001",
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
        "id": "noun_clause_belief",
        "surface_form": "suspicion",
        "frame": "suspicion that 〈clause〉; have a suspicion that 〈clause〉; a suspicion that 〈clause〉; arouse 〈person〉's suspicions that 〈clause〉",
        "meaning": "ある命題・出来事・状態が真実かもしれないという、確証に至らない見立て。犯罪・不正の可能性も、節の内容として表せる。",
        "disposition": "included",
        "rationale": "「suspicion that 〈clause〉; have a suspicion that 〈clause〉; a suspicion that 〈clause〉; arouse 〈person〉's suspicions that 〈clause〉」は、節の内容そのものを疑われる命題として示す。節の真偽を確定せず、その可能性を考える語義として本文に含まれている。",
        "semantic_assertions": [
          {
            "id": "noun_clause_belief_a1",
            "statement": "このフレームのthat節は、疑いの対象となる命題・出来事・状態の内容を示す。",
            "polarity": "must_hold",
            "scope": "that節を伴う名詞用法"
          },
          {
            "id": "noun_clause_belief_a2",
            "statement": "この疑いを抱くこと自体は、節の内容が事実であるとの確定を含意しない。",
            "polarity": "must_hold",
            "scope": "that節を伴う名詞用法"
          }
        ]
      },
      {
        "id": "noun_criminal_suspicion",
        "surface_form": "suspicion",
        "frame": "suspicion of 〈offence〉; on suspicion of 〈offence〉; be under suspicion",
        "meaning": "人が犯罪・不正をした可能性への疑い。容疑を理由とする取扱いや、疑いをかけられた状態を表す。",
        "disposition": "included",
        "rationale": "「on suspicion of 〈offence〉; be under suspicion」は、ある人が犯罪・不正を行った可能性に関する疑いを表す。本文は逮捕・拘束の理由と有罪確定を区別しており、この人を主体とする疑いのフレームを含めている。",
        "semantic_assertions": [
          {
            "id": "noun_criminal_suspicion_a1",
            "statement": "offence句は、人がその犯罪・不正を行った可能性を疑う内容または理由を示す。",
            "polarity": "must_hold",
            "scope": "犯罪・不正についての名詞用法"
          },
          {
            "id": "noun_criminal_suspicion_a2",
            "statement": "on suspicion of、またはunder suspicionの用法だけでは、有罪や不正の事実は確定しない。",
            "polarity": "must_hold",
            "scope": "on suspicion of / under suspicion"
          }
        ]
      },
      {
        "id": "noun_raises_suspicion",
        "surface_form": "suspicion",
        "frame": "raise some suspicion",
        "meaning": "出来事や発言が疑いを招くこと。疑いの対象となる命題は文面に明示されないことがある。",
        "disposition": "included",
        "rationale": "「raise some suspicion」は、出来事が疑いを招くという原因・結果のフレームで、疑われる人物や命題を必ずしも表面に出さない。本文では説明のつかない遅れが疑いを招く例として採録されている。",
        "semantic_assertions": [
          {
            "id": "noun_raises_suspicion_a1",
            "statement": "raise some suspicionでは、主語となる出来事・発言は疑いを生じさせる契機であり、必ずしも疑われる対象そのものではない。",
            "polarity": "must_hold",
            "scope": "raise some suspicion"
          },
          {
            "id": "noun_raises_suspicion_a2",
            "statement": "疑いが生じても、その契機となった出来事が不正または虚偽であると確定するわけではない。",
            "polarity": "must_hold",
            "scope": "raise some suspicion"
          }
        ]
      },
      {
        "id": "noun_distrustful_attitude",
        "surface_form": "suspicion",
        "frame": "regard 〈person/thing〉 with suspicion",
        "meaning": "人や物事を信用できず、疑いの目で見る態度。特定の命題が真実かもしれないという見立てより、対象への不信・警戒に焦点がある。",
        "disposition": "included",
        "rationale": "「regard 〈person/thing〉 with suspicion」は対象を疑いの目で見る態度を表し、対象についてのthat節の命題を疑うフレームとは意味役割が異なる。本文はこの態度を独立した語義として採録している。",
        "semantic_assertions": [
          {
            "id": "noun_distrustful_attitude_a1",
            "statement": "with suspicionの対象は、人・物事・説明など、信用できるかどうかを評価される対象である。",
            "polarity": "must_hold",
            "scope": "regard X with suspicion"
          },
          {
            "id": "noun_distrustful_attitude_a2",
            "statement": "この態度の記述は、対象についての特定の疑惑や命題が事実だという確信を必須としない。",
            "polarity": "must_hold",
            "scope": "regard X with suspicion"
          }
        ]
      },
      {
        "id": "noun_faint_amount_or_sign",
        "surface_form": "suspicion",
        "frame": "a suspicion of 〈a smile〉; a suspicion of 〈truth〉",
        "meaning": "通常単数のa suspicion of ...で、ごく少量またはかすかな兆しを表す形式的・比喩的用法。",
        "disposition": "included",
        "rationale": "「a suspicion of 〈a smile〉; a suspicion of 〈truth〉」は、疑うという心的行為ではなく、笑みや真実味がわずかに感じられることを表す。本文はこの意味を別語義として説明している。",
        "semantic_assertions": [
          {
            "id": "noun_faint_amount_or_sign_a1",
            "statement": "a suspicion of XはXのごく少量またはかすかな兆候を表す。",
            "polarity": "must_hold",
            "scope": "a suspicion of X"
          },
          {
            "id": "noun_faint_amount_or_sign_a2",
            "statement": "このフレームのsuspicionは、Xを真実かもしれないと疑う心的行為を意味しない。",
            "polarity": "must_not_hold",
            "scope": "a suspicion of X"
          }
        ]
      },
      {
        "id": "adjective_feeling_suspicious",
        "surface_form": "suspicious",
        "frame": "疑っている、不信に思っている",
        "meaning": "疑いを抱いている、または不信に思っている状態を表す形容詞。",
        "disposition": "included",
        "rationale": "「疑っている、不信に思っている」は、疑いを感じる主体側の形容詞用法として本文の語形成欄に含まれている。",
        "semantic_assertions": [
          {
            "id": "adjective_feeling_suspicious_a1",
            "statement": "この形容詞用法では、疑い・不信を抱く主体の状態を表す。",
            "polarity": "must_hold",
            "scope": "suspiciousの主体側用法"
          }
        ]
      },
      {
        "id": "adjective_causing_suspicion",
        "surface_form": "suspicious",
        "frame": "人に疑いを起こさせる「疑わしい」",
        "meaning": "疑いを生じさせる人や物事を表す形容詞。",
        "disposition": "included",
        "rationale": "「人に疑いを起こさせる「疑わしい」」は、疑いを抱く側ではなく、それを引き起こす対象側の形容詞用法であり、本文の語形成欄に含まれている。",
        "semantic_assertions": [
          {
            "id": "adjective_causing_suspicion_a1",
            "statement": "この形容詞用法は、疑いを感じる主体ではなく疑いを引き起こす対象の性質を表す。",
            "polarity": "must_hold",
            "scope": "suspiciousの対象側用法"
          }
        ]
      },
      {
        "id": "adverb_derivative",
        "surface_form": "suspiciously",
        "frame": "suspiciously",
        "meaning": "suspiciousの副詞形。",
        "disposition": "included",
        "rationale": "「suspiciously」は本文で副詞形として明記されている派生形である。",
        "semantic_assertions": [
          {
            "id": "adverb_derivative_a1",
            "statement": "suspiciouslyはsuspiciousに対応する副詞形である。",
            "polarity": "must_hold",
            "scope": "語形成"
          }
        ]
      },
      {
        "id": "abstract_noun_derivative",
        "surface_form": "suspiciousness",
        "frame": "suspiciousness",
        "meaning": "suspiciousの名詞形。",
        "disposition": "included",
        "rationale": "「suspiciousness」は本文で名詞形として明記されている派生形である。",
        "semantic_assertions": [
          {
            "id": "abstract_noun_derivative_a1",
            "statement": "suspiciousnessはsuspiciousに対応する名詞形である。",
            "polarity": "must_hold",
            "scope": "語形成"
          }
        ]
      },
      {
        "id": "dialectal_verb_excluded",
        "surface_form": "suspicion",
        "frame": "suspicion（動詞）",
        "meaning": "～を疑うという他動詞用法。本文ではchiefly dialectalと記して主要な学習語義から除外している。",
        "disposition": "excluded",
        "rationale": "「suspicion（動詞）」は名詞の主要語義ではなく、本文自身が方言的な他動詞用法として主要な学習語義から外している。",
        "semantic_assertions": [
          {
            "id": "dialectal_verb_excluded_a1",
            "statement": "この方言的な他動詞用法は、標準的な主要学習語義の一覧に含めない。",
            "polarity": "must_not_hold",
            "scope": "主要な学習語義"
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "CHK-sense-structure-85e67bdbf80f0e5b",
        "taxonomy_id": "cross_section_internal_contradiction",
        "severity": "minor",
        "location": {
          "section": "core_image",
          "line_start": 30,
          "line_end": 30,
          "exact_quote": "suspicion の共通核は、「まだ確証はないが、表面に見えていることの背後に別の事実・意図・問題があるのではないかと感じる」ことである。  "
        },
        "rationale": "この共通核は、語義1〜3の犯罪・不信・推測には合うが、語義4（line 34）の「ほんの少し、かすかな気配」には、表面の背後に別の事実を推測することが必須ではない。コアイメージの核が語義4の意味範囲を狭く捉えている。",
        "suggested_direction": "共通核を、不確かな推測だけでなく何かの存在をわずかに感じ取る用法も含む表現に広げる。"
      },
      {
        "id": "CHK-frame-relation-f20791f0cfdbd2ce",
        "taxonomy_id": "argument_slot_role_mismatch",
        "severity": "minor",
        "location": {
          "section": "frames",
          "line_start": 46,
          "line_end": 46,
          "exact_quote": "cast suspicion on 〈person/action〉＝〈人・行為〉に疑いを向ける"
        },
        "rationale": "語義1の例文「The altered timestamp cast suspicion on the authenticity of the document.」（72行目）は疑いの対象が文書の真正性という性質・主張であり、〈person/action〉の対象枠から外れる。対象を property/claim まで明示する必要がある。",
        "suggested_direction": "完全フレーム化：対象枠に〈claim/property〉を加える"
      },
      {
        "id": "CHK-frame-relation-f487dc58051550c5",
        "taxonomy_id": "argument_slot_role_mismatch",
        "severity": "minor",
        "location": {
          "section": "frames",
          "line_start": 113,
          "line_end": 113,
          "exact_quote": "regard/view/treat 〈person/claim〉 with suspicion＝〈人・主張〉を疑いの目で見る"
        },
        "rationale": "語義2の例文「Residents viewed the sudden policy change with suspicion.」（119行目）は対象が人または主張ではなく方針変更・決定である。〈proposal/action/decision〉などの対象枠を示す必要がある。",
        "suggested_direction": "完全フレーム化：対象枠に〈proposal/action/decision〉を加える"
      },
      {
        "id": "CHK-frame-relation-61011dbd10a9eca3",
        "taxonomy_id": "lexical_relation_mislabel",
        "severity": "minor",
        "location": {
          "section": "lexical_relations",
          "line_start": 84,
          "line_end": 84,
          "exact_quote": "・accusation"
        },
        "rationale": "accusation は不正をしたという非難・告発そのもの、suspicion は証明前に抱く疑いであり、同義語というより関連する発話・行為である。違い行も明示的な主張と内的な疑いを区別しているため、類義語欄から削除するのが適切。",
        "suggested_direction": "削除"
      },
      {
        "id": "CHK-frame-relation-c6cc8ed5c1faed74",
        "taxonomy_id": "lexical_relation_mislabel",
        "severity": "minor",
        "location": {
          "section": "lexical_relations",
          "line_start": 91,
          "line_end": 91,
          "exact_quote": "・allegation"
        },
        "rationale": "allegation は証明前に公に提示された不正についての主張で、suspicion の内的な疑いとは意味役割が異なる関連語である。違い行も提示された主張と発言されていない疑いを区別しているため、類義語欄から削除するのが適切。",
        "suggested_direction": "削除"
      },
      {
        "id": "CHK-example-attribution-9a7ced3d899cef25",
        "taxonomy_id": "example_sense_attribution_mismatch",
        "severity": "blocking",
        "location": {
          "section": "collocations_examples",
          "line_start": 52,
          "line_end": 52,
          "exact_quote": "例: The unexplained transfer of funds aroused suspicion among the auditors.  "
        },
        "rationale": "段階1でsense:001, sense:002が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
        "suggested_direction": "判別語の追加"
      },
      {
        "id": "CHK-example-attribution-4b73cc547d6ec54a",
        "taxonomy_id": "example_sense_attribution_mismatch",
        "severity": "blocking",
        "location": {
          "section": "collocations_examples",
          "line_start": 72,
          "line_end": 72,
          "exact_quote": "例: The altered timestamp cast suspicion on the authenticity of the document.  "
        },
        "rationale": "段階1でsense:002, sense:003が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
        "suggested_direction": "判別語の追加"
      },
      {
        "id": "CHK-example-attribution-4e805feccd4e0426",
        "taxonomy_id": "example_sense_attribution_mismatch",
        "severity": "blocking",
        "location": {
          "section": "collocations_examples",
          "line_start": 77,
          "line_end": 77,
          "exact_quote": "例: The security footage confirmed the manager's suspicions.  "
        },
        "rationale": "段階1でsense:001, sense:003が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
        "suggested_direction": "判別語の追加"
      },
      {
        "id": "CHK-example-attribution-02488c6d692d08e3",
        "taxonomy_id": "example_sense_attribution_mismatch",
        "severity": "blocking",
        "location": {
          "section": "collocations_examples",
          "line_start": 129,
          "line_end": 129,
          "exact_quote": "例: Years of secrecy created a lasting suspicion of the agency.  "
        },
        "rationale": "段階1でsense:001, sense:002が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
        "suggested_direction": "判別語の追加"
      },
      {
        "id": "CHK-example-attribution-ef69a9c2d1737319",
        "taxonomy_id": "example_sense_attribution_mismatch",
        "severity": "blocking",
        "location": {
          "section": "collocations_examples",
          "line_start": 134,
          "line_end": 134,
          "exact_quote": "例: The unexplained changes led to deep suspicion among investors.  "
        },
        "rationale": "段階1でsense:001, sense:002が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
        "suggested_direction": "判別語の追加"
      },
      {
        "id": "CHK-example-attribution-3c70c60e3ba74cda",
        "taxonomy_id": "example_sense_attribution_mismatch",
        "severity": "blocking",
        "location": {
          "section": "collocations_examples",
          "line_start": 139,
          "line_end": 139,
          "exact_quote": "例: The lack of transparency caused widespread suspicion about the process.  "
        },
        "rationale": "段階1でsense:002, sense:003が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
        "suggested_direction": "判別語の追加"
      },
      {
        "id": "CHK-example-attribution-85f2d8aab19a336e",
        "taxonomy_id": "example_sense_attribution_mismatch",
        "severity": "blocking",
        "location": {
          "section": "collocations_examples",
          "line_start": 215,
          "line_end": 215,
          "exact_quote": "例: A detailed explanation dispelled our suspicion that the figures had been altered.  "
        },
        "rationale": "段階1でsense:001, sense:003が同程度に自然と判定され、例文内に帰属を一意にする判別語がない。",
        "suggested_direction": "判別語の追加"
      },
      {
        "id": "CHK-evidence-f26152139b13f089",
        "taxonomy_id": "evidence_claim_mismatch",
        "severity": "blocking",
        "location": {
          "section": "pronunciation",
          "line_start": 15,
          "line_end": 15,
          "exact_quote": "米: /səˈspɪʃən/｜英: /səˈspɪʃən/。3音節で、第2音節に主強勢がある。Oxford 系の辞書では語末を /ʃn/ と圧縮して表記することもあるが、Cambridge 系の /ʃ.ən/ と大きく異なる発音を示すものではない。語頭の su- は強く /suː/ と読まず、弱い /sə/ になる。"
        },
        "rationale": "insufficient_evidence: Oxford（https://www.oxfordlearnersdictionaries.com/definition/english/suspicion）supports /səˈspɪʃn/ in its UK and US fields, and Merriam-Webster (https://www.merriam-webster.com/dictionary/suspicion) marks second-syllable stress. Neither locator verifies the Cambridge /ʃ.ən/ form or the claim that the difference is insignificant; no Cambridge locator is included in the evidence context.",
        "suggested_direction": "Add a Cambridge locator and verify the comparison, or remove the Cambridge comparison."
      },
      {
        "id": "CHK-evidence-1cb0e731e8d76698",
        "taxonomy_id": "evidence_claim_mismatch",
        "severity": "blocking",
        "location": {
          "section": "etymology",
          "line_start": 19,
          "line_end": 19,
          "exact_quote": "suspicion は中英語・アングロフランス語／古フランス語を経て、ラテン語 suspīciō / suspectionem「疑い、不信」にさかのぼる。さらに suspicere「ひそかに見る、疑って見る、疑う」と関係し、sub-「下から・ひそかに」と specere「見る」に結び付く語族である。現代語の意味では、目の前の証拠だけでは確定できないものを「何かあるのではないか」と見る感覚が中心に残っている。suspect、suspicious も同じ語族に属する。"
        },
        "rationale": "The cited etymology facts support the route through Middle English, French forms, and Latin suspicere. However, Etymonline's locator (https://www.etymonline.com/word/suspicion), in its linked suspect entry, describes sub as “up to” and specere as “to look at”; it does not support the article's gloss “下から・ひそかに” for sub-. The linked origin facts also do not establish that the stated modern semantic image “remains” as the word's central meaning. The target extends beyond the linked etymological facts.",
        "suggested_direction": "Limit the etymology to the sourced historical route and component glosses, or add direct support and mark the modern semantic continuity as an interpretation."
      },
      {
        "id": "CHK-evidence-7bf51b857c089ddc",
        "taxonomy_id": "evidence_claim_mismatch",
        "severity": "blocking",
        "location": {
          "section": "word_formation",
          "line_start": 23,
          "line_end": 25,
          "exact_quote": "・suspect：動詞では「～ではないかと疑う、〈人〉を犯人・不正の当事者ではないかと疑う」、名詞では「容疑者」、形容詞では「疑わしい、怪しい」。suspicion はその「疑い・疑念」を名詞として表す。\n・suspicious：形容詞。「疑っている、怪しいと思っている」または「疑わしい、怪しい」。人の心理と、対象の性質の両方を表せる。\n・suspiciously：副詞。「疑わしそうに、怪しいほど」。行動の見え方にも、程度が不自然に高いことにも使う。"
        },
        "rationale": "Oxford's linked word-family fact (oxf_family; https://www.oxfordlearnersdictionaries.com/definition/english/suspicion) lists the forms and parts of speech. It does not support the target's definitions of suspect, the two meanings of suspicious, or the manner and unusually-high-degree uses of suspiciously. The family-list fact directly supports membership, not these semantic claims.",
        "suggested_direction": "Add direct dictionary evidence for the stated senses and uses, or limit this section to the word-family forms and parts of speech."
      },
      {
        "id": "CHK-evidence-1d48282c2269ad9b",
        "taxonomy_id": "evidence_claim_mismatch",
        "severity": "blocking",
        "location": {
          "section": "frequency_register",
          "line_start": 44,
          "line_end": 44,
          "exact_quote": "【レジスター/領域】標準語。日常会話、報道、警察・司法関連の記事で広く使う。on suspicion of ...、under suspicion は報道や法執行の文脈で特に多い。ここでいう suspicion は有罪が立証されたことを意味しない。頻度の数値はこの辞書内の学習上の相対目安である。"
        },
        "rationale": "The linked Merriam-Webster legal fact (mw_legal; https://www.merriam-webster.com/dictionary/suspicion) supports the no-proof/short-of-belief boundary, not standardness, broad everyday and news distribution, or the claim that these phrases are especially common. Oxford and the Merseyside Police release (https://www.merseyside.police.uk/news/merseyside/news/2026/june-2026/man-arrested-on-suspicion-of-breach-of-the-peace-on-county-road/) provide examples of the phrases, but not their relative frequency or distribution. The linked evidence supports only part of this target.",
        "suggested_direction": "Limit the target to the no-proof boundary and documented examples, or add evidence appropriate to the register and frequency claims."
      },
      {
        "id": "CHK-evidence-c694e2ed8a394b1d",
        "taxonomy_id": "evidence_claim_mismatch",
        "severity": "blocking",
        "location": {
          "section": "frames",
          "line_start": 113,
          "line_end": 113,
          "exact_quote": "suspicion of 〈person/group/idea〉＝〈人・集団・考え〉への不信"
        },
        "rationale": "The linked facts for claim_distrust define the distrust sense and give examples such as viewing something with suspicion (Oxford and Merriam-Webster) or looking with suspicion on claims (American Heritage). They do not directly verify the distinct suspicion of + person/group/idea frame. The same unsupported frame is repeated in collocation:009 with the agency example at lines 127–129.",
        "suggested_direction": "Add a source example for suspicion of + person/group/idea in the distrust sense, or remove or qualify the frame and example."
      },
      {
        "id": "CHK-evidence-1c2014f25502d6e7",
        "taxonomy_id": "evidence_claim_mismatch",
        "severity": "blocking",
        "location": {
          "section": "lexical_relations",
          "line_start": 148,
          "line_end": 149,
          "exact_quote": "頻度: 〈8/10〉\n違い: distrust は信用の欠如そのものを直接表し、suspicion はその背後に隠れた問題・意図があるのではないかという推測を帯びやすい。"
        },
        "rationale": "The linked facts define suspicion as distrust or lack of confidence, but do not support the 8/10 frequency rating or this contrast. Merriam-Webster's linked comparison (mw_contrast; https://www.merriam-webster.com/dictionary/suspicion) says suspicion stresses lack of faith in truth, reality, fairness, or reliability, while mistrust implies doubt based on suspicion; it does not establish the target's stated distinction between distrust and suspicion.",
        "suggested_direction": "Remove or identify the frequency scale as editorial, and add direct comparative evidence for the stated distinction or narrow the wording to source-supported definitions."
      },
      {
        "id": "CHK-evidence-74f1211675818881",
        "taxonomy_id": "evidence_claim_mismatch",
        "severity": "blocking",
        "location": {
          "section": "lexical_relations",
          "line_start": 155,
          "line_end": 156,
          "exact_quote": "頻度: 〈7/10〉\n違い: mistrust は distrust に近い一般的な不信。suspicion はより「何か怪しい」という感覚を含みやすい。"
        },
        "rationale": "The linked sources do not support the 7/10 frequency rating. Merriam-Webster's linked comparison (mw_contrast; https://www.merriam-webster.com/dictionary/suspicion) says mistrust implies genuine doubt based upon suspicion, whereas the target presents mistrust as general distrust and shifts the distinguishing implication to suspicion. Oxford and American Heritage support the broad distrust sense but not this comparative claim.",
        "suggested_direction": "Remove or identify the frequency scale as editorial, and align the comparison with direct source evidence or qualify it."
      },
      {
        "id": "CHK-evidence-4f7613fe6f400031",
        "taxonomy_id": "evidence_claim_mismatch",
        "severity": "blocking",
        "location": {
          "section": "frames",
          "line_start": 251,
          "line_end": 251,
          "exact_quote": "with a suspicion of 〈smile/irony〉＝かすかな〈笑み・皮肉〉を帯びて。"
        },
        "rationale": "Oxford's linked fact (oxf_trace; https://www.oxfordlearnersdictionaries.com/definition/english/suspicion) gives “in the suspicion of a smile,” not the target's with + a suspicion of frame; the linked Merriam-Webster and American Heritage facts establish the small-amount sense but do not supply that frame or an irony example. The same with-construction appears in collocation:021's example at lines 270–272, so the source-to-frame link does not directly support those targets.",
        "suggested_direction": "Use the documented “suspicion of a smile” construction, or add a source that directly supports the with-construction and irony use."
      },
      {
        "id": "CHK-evidence-6e65bce7c7568c72",
        "taxonomy_id": "evidence_claim_mismatch",
        "severity": "blocking",
        "location": {
          "section": "usage_notes",
          "line_start": 275,
          "line_end": 275,
          "exact_quote": "一部の辞書には suspicion を動詞「疑う」として扱う非標準・方言的な用法も載るが、現代の標準英語では通常 suspect を使うため、本記事では主要語義として立てない。"
        },
        "rationale": "The linked facts mw_verb, ahd_verb, and ety_verb support that some dictionaries record a marginal verb meaning “suspect.” But usage_note:004 is tagged to sense 4, the small-amount use, so linking the separate verb claim to this sense-specific target creates a semantic mismatch. The linked facts also do not directly establish the frequency claim that modern standard English usually uses suspect.",
        "suggested_direction": "Move the verb note to a lemma-level or word-formation note, and support or qualify the standard-usage statement."
      },
      {
        "id": "CR-1",
        "severity": "medium",
        "location": "語源のラテン語形",
        "suggested_direction": "対格形を示す意図なら suspīciō / suspīciōnem とし、必要に応じて主格形・対格形であることを明記してください。"
      },
      {
        "id": "CR-2",
        "severity": "medium",
        "location": "語源の構成要素の説明",
        "suggested_direction": "sub- は「下から」などに限って説明し、suspicere は「下から見上げる」から「疑う」へ展開した語として記述するなど、「ひそかに」を語源的成分として扱わないでください。"
      },
      {
        "id": "CR-3",
        "severity": "low",
        "location": "語義3の可算性",
        "suggested_direction": "語義3の見出しを「可算・不可算」とし、a suspicion that ... と growing/widespread suspicion that ... のような用例で違いを示してください。"
      },
      {
        "id": "CR-4",
        "severity": "medium",
        "location": "語義1の類義語 allegation の定義",
        "suggested_direction": "「公に」を外し、誰かが不正・違法行為をしたという未証明の申し立て・主張として定義してください。"
      }
    ],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U-GUILT",
        "source_fact_ids": [
          "F-OUP-1",
          "F-MW-1"
        ],
        "canonical_statement": "Suspicion can denote a countable or uncountable belief that someone did something wrong without proof.",
        "disposition": "included",
        "rationale": "The article retains the evidence-limited wrongdoing sense; it no longer claims a separate state-of-being-suspected meaning."
      },
      {
        "id": "U-DISTRUST",
        "source_fact_ids": [
          "F-OUP-3"
        ],
        "canonical_statement": "The Oxford Advanced American Dictionary’s third sense of suspicion describes a feeling that a person or thing cannot be trusted.",
        "disposition": "included",
        "rationale": "The article uses Oxford’s direct definition; Merriam-Webster examples remain assigned to the separate frame union."
      },
      {
        "id": "U-UNCERTAIN-BELIEF",
        "source_fact_ids": [
          "F-OUP-2"
        ],
        "canonical_statement": "Oxford records a countable belief or suspicion that a proposition is true despite lack of proof.",
        "disposition": "included",
        "rationale": "The article uses the directly accessible Oxford meaning only. Cambridge’s search-result record and Merriam-Webster’s broader doubt definition are not treated as direct support for this sense."
      },
      {
        "id": "U-SMALL-AMOUNT",
        "source_fact_ids": [
          "F-OUP-4",
          "F-MW-3"
        ],
        "canonical_statement": "A singular suspicion can denote a very small amount or faint sign of something.",
        "disposition": "included",
        "rationale": "Oxford and Merriam-Webster directly support the retained small-amount use and its examples."
      },
      {
        "id": "U-FRAMES",
        "source_fact_ids": [
          "F-OUP-6",
          "F-MW-4"
        ],
        "canonical_statement": "Oxford records suspicion that + clause, on suspicion of + offence, and under suspicion; Merriam-Webster examples separately attest arouse someone’s suspicions, raise some suspicion, suspicion that + clause, and with suspicion.",
        "disposition": "integrated",
        "rationale": "The article retains separately attested patterns and distinguishes the number and frame in arouse someone’s suspicions from raise some suspicion. It omits unsupported bare suspicion of crime/wrongdoing and confirm suspicions that combinations."
      },
      {
        "id": "U-PRONUNCIATION",
        "source_fact_ids": [
          "F-OUP-5",
          "F-MW-5"
        ],
        "canonical_statement": "Oxford gives the North American IPA /səˈspɪʃn/; Merriam-Webster separately shows spelling syllabification and a pronunciation respelling with primary stress on the second syllable.",
        "disposition": "included",
        "rationale": "The article distinguishes Oxford’s IPA from Merriam-Webster’s spelling division and stress-marked pronunciation respelling; it makes no regional or phonetic equivalence claim."
      },
      {
        "id": "U-ETYMOLOGY",
        "source_fact_ids": [
          "F-MW-6",
          "F-ETY-1"
        ],
        "canonical_statement": "Dictionary accounts trace suspicion through Middle English and French to Latin forms related to suspicere, with source-specific forms and routes.",
        "disposition": "included",
        "rationale": "The article reports the source-specific route and removes the unsupported suspect-family claim."
      },
      {
        "id": "U-SUSPICIOUS",
        "source_fact_ids": [
          "F-MW-9"
        ],
        "canonical_statement": "Suspicious is a related adjective that can describe a person disposed to distrust and something that arouses suspicion.",
        "disposition": "integrated",
        "rationale": "The article includes the related adjective and distinguishes psychological from property uses."
      },
      {
        "id": "U-SUSPICIOUSLY",
        "source_fact_ids": [
          "F-MW-10"
        ],
        "canonical_statement": "Suspiciously is listed as an adverb related to suspicious.",
        "disposition": "integrated",
        "rationale": "The article includes suspiciously as a related form."
      },
      {
        "id": "U-SUSPICIOUSNESS",
        "source_fact_ids": [
          "F-MW-11"
        ],
        "canonical_statement": "Suspiciousness is listed as a noun related to suspicious.",
        "disposition": "integrated",
        "rationale": "The article includes suspiciousness as a related form."
      },
      {
        "id": "U-DIALECT-VERB",
        "source_fact_ids": [
          "F-MW-8",
          "F-MW-12"
        ],
        "canonical_statement": "Merriam-Webster records a chiefly dialectal transitive verb suspicion meaning suspect.",
        "disposition": "integrated",
        "rationale": "The article mentions this uncommon verb separately and does not present it as a main standard noun sense."
      },
      {
        "id": "U-LEGAL-USE",
        "source_fact_ids": [
          "F-MW-7"
        ],
        "canonical_statement": "The legal dictionary entry describes suspicion as a mental state generally short of belief and cross-references reasonable suspicion.",
        "disposition": "integrated",
        "rationale": "The article limits its legal note to the general meaning and the phrase on suspicion of; it does not explain a jurisdiction-specific reasonable-suspicion test."
      },
      {
        "id": "U-CEFR-LABELS",
        "source_fact_ids": [
          "F-CAM-6"
        ],
        "canonical_statement": "Cambridge labels its feeling sense B2 and its belief-in-guilt sense C1.",
        "disposition": "excluded",
        "rationale": "The Cambridge locator was inaccessible during direct review, and the article does not make CEFR-level claims."
      },
      {
        "id": "U-CAM-GUILT",
        "source_fact_ids": [
          "F-CAM-2"
        ],
        "canonical_statement": "A Cambridge search result reports a countable or uncountable belief that someone committed a crime or did something wrong.",
        "disposition": "excluded",
        "rationale": "The Cambridge entry locator returned 403 during direct review; this fact is preserved as an unverified search-result record and is not used to support the article."
      },
      {
        "id": "U-CAM-DISTRUST",
        "source_fact_ids": [
          "F-CAM-3"
        ],
        "canonical_statement": "A Cambridge search result reports a doubt or lack-of-trust sense with examples about a group’s politics.",
        "disposition": "excluded",
        "rationale": "The Cambridge entry locator returned 403 during direct review; the article relies on accessible Oxford, Merriam-Webster, and American Heritage evidence instead."
      },
      {
        "id": "U-CAM-SMALL-AMOUNT",
        "source_fact_ids": [
          "F-CAM-4"
        ],
        "canonical_statement": "A Cambridge search result reports a singular small-amount use illustrated by a slight smile.",
        "disposition": "excluded",
        "rationale": "The Cambridge entry locator returned 403 during direct review; the article’s small-amount sense and smile frame rely on accessible Oxford, Merriam-Webster, and American Heritage facts."
      },
      {
        "id": "U-CAM-PRONUNCIATION",
        "source_fact_ids": [
          "F-CAM-5"
        ],
        "canonical_statement": "A Cambridge search result reports UK and US IPA as /səˈspɪʃ.ən/.",
        "disposition": "excluded",
        "rationale": "The Cambridge entry locator returned 403 during direct review; no Cambridge IPA or regional comparison is used in the article."
      },
      {
        "id": "U-AHD-UNVERIFIED",
        "source_fact_ids": [
          "F-AHD-1",
          "F-AHD-2",
          "F-AHD-3",
          "F-AHD-4",
          "F-AHD-5"
        ],
        "canonical_statement": "American Heritage search-result facts cover suspected wrongdoing, being suspected, distrust, a small amount, and an etymology route.",
        "disposition": "excluded",
        "rationale": "The American Heritage locator could not be opened during direct review. These search-result facts are preserved in the inventory but are not used to support article claims."
      },
      {
        "id": "U-ETYMOLOGY-DETAIL-EXCLUDED",
        "source_fact_ids": [
          "F-ETY-2"
        ],
        "canonical_statement": "The etymology source adds a literal historical gloss for the Latin verb and a note about an early meaning of suspicion.",
        "disposition": "excluded",
        "rationale": "The article limits its etymology to the historical route and source-specific Latin forms; this additional semantic-history detail is not needed for that claim."
      },
      {
        "id": "U-CAM-UNCERTAIN-BELIEF",
        "source_fact_ids": [
          "F-CAM-1"
        ],
        "canonical_statement": "A Cambridge search result reports a countable belief that something may be true and a that-clause pattern.",
        "disposition": "excluded",
        "rationale": "The entry locator could not be accessed; this search-result fact is retained for audit traceability but does not support the article."
      },
      {
        "id": "U-MW-UNCERTAINTY",
        "source_fact_ids": [
          "F-MW-2"
        ],
        "canonical_statement": "Merriam-Webster records a broader state of mental uneasiness, uncertainty, or doubt.",
        "disposition": "integrated",
        "rationale": "This broader dictionary use informs the article’s comparison with doubt; it is not presented as a separate additional numbered sense."
      },
      {
        "id": "U-FREQUENCY-RUBRIC",
        "source_fact_ids": [
          "F-ENTRY-SPEC-FREQUENCY"
        ],
        "canonical_statement": "The entry-spec requires learner-facing editorial frequency ratings under a ten-point English-wide encounter rubric and explicitly allows estimates without strict statistical basis.",
        "disposition": "integrated",
        "rationale": "The article explicitly labels its values as editorial qualitative estimates, not corpus counts or dictionary-published numbers; the local specification is the primary source for the required rating method."
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
        "id": "narrative:001",
        "status": null,
        "target_id": "narrative:001"
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
        "id": "grammar_pattern:007",
        "status": null,
        "target_id": "grammar_pattern:007"
      },
      {
        "id": "collocation:007",
        "status": null,
        "target_id": "collocation:007"
      },
      {
        "id": "usage_note:002",
        "status": null,
        "target_id": "usage_note:002"
      },
      {
        "id": "synonym:002",
        "status": null,
        "target_id": "synonym:002"
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
        "id": "usage_note:003",
        "status": null,
        "target_id": "usage_note:003"
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
        "id": "pattern_example_coverage:007",
        "status": null,
        "relation_id": "pattern_example_coverage:007"
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
        "id": "core_inventory_consistency:001",
        "status": null,
        "relation_id": "core_inventory_consistency:001"
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
        "id": "noun_clause_belief",
        "status": null,
        "assertion_ids": [
          "noun_clause_belief_a1",
          "noun_clause_belief_a2"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "noun_criminal_suspicion",
        "status": null,
        "assertion_ids": [
          "noun_criminal_suspicion_a1",
          "noun_criminal_suspicion_a2"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "noun_raises_suspicion",
        "status": null,
        "assertion_ids": [
          "noun_raises_suspicion_a1",
          "noun_raises_suspicion_a2"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "noun_distrustful_attitude",
        "status": null,
        "assertion_ids": [
          "noun_distrustful_attitude_a1",
          "noun_distrustful_attitude_a2"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "noun_faint_amount_or_sign",
        "status": null,
        "assertion_ids": [
          "noun_faint_amount_or_sign_a1",
          "noun_faint_amount_or_sign_a2"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "adjective_feeling_suspicious",
        "status": null,
        "assertion_ids": [
          "adjective_feeling_suspicious_a1"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "adjective_causing_suspicion",
        "status": null,
        "assertion_ids": [
          "adjective_causing_suspicion_a1"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "adverb_derivative",
        "status": null,
        "assertion_ids": [
          "adverb_derivative_a1"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "abstract_noun_derivative",
        "status": null,
        "assertion_ids": [
          "abstract_noun_derivative_a1"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      },
      {
        "id": "dialectal_verb_excluded",
        "status": null,
        "assertion_ids": [
          "dialectal_verb_excluded_a1"
        ],
        "verified_body_sha256": "e0cdcd7c12ed6c212b99cc5c3f6aaa8025f839a1b1fb392bd5a98b62744f8426"
      }
    ],
    "finding_results": [
      {
        "id": "CHK-sense-structure-85e67bdbf80f0e5b",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-frame-relation-f20791f0cfdbd2ce",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-frame-relation-f487dc58051550c5",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-frame-relation-61011dbd10a9eca3",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-frame-relation-c6cc8ed5c1faed74",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-example-attribution-9a7ced3d899cef25",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-example-attribution-4b73cc547d6ec54a",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-example-attribution-4e805feccd4e0426",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-example-attribution-02488c6d692d08e3",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-example-attribution-ef69a9c2d1737319",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-example-attribution-3c70c60e3ba74cda",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-example-attribution-85f2d8aab19a336e",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-evidence-f26152139b13f089",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-evidence-1cb0e731e8d76698",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-evidence-7bf51b857c089ddc",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-evidence-1d48282c2269ad9b",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-evidence-c694e2ed8a394b1d",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-evidence-1c2014f25502d6e7",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-evidence-74f1211675818881",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-evidence-4f7613fe6f400031",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHK-evidence-6e65bce7c7568c72",
        "status": null,
        "notes": ""
      },
      {
        "id": "CR-1",
        "status": null,
        "notes": ""
      },
      {
        "id": "CR-2",
        "status": null,
        "notes": ""
      },
      {
        "id": "CR-3",
        "status": null,
        "notes": ""
      },
      {
        "id": "CR-4",
        "status": null,
        "notes": ""
      }
    ],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U-GUILT",
        "status": null,
        "union_id": "U-GUILT"
      },
      {
        "id": "U-DISTRUST",
        "status": null,
        "union_id": "U-DISTRUST"
      },
      {
        "id": "U-UNCERTAIN-BELIEF",
        "status": null,
        "union_id": "U-UNCERTAIN-BELIEF"
      },
      {
        "id": "U-SMALL-AMOUNT",
        "status": null,
        "union_id": "U-SMALL-AMOUNT"
      },
      {
        "id": "U-FRAMES",
        "status": null,
        "union_id": "U-FRAMES"
      },
      {
        "id": "U-PRONUNCIATION",
        "status": null,
        "union_id": "U-PRONUNCIATION"
      },
      {
        "id": "U-ETYMOLOGY",
        "status": null,
        "union_id": "U-ETYMOLOGY"
      },
      {
        "id": "U-SUSPICIOUS",
        "status": null,
        "union_id": "U-SUSPICIOUS"
      },
      {
        "id": "U-SUSPICIOUSLY",
        "status": null,
        "union_id": "U-SUSPICIOUSLY"
      },
      {
        "id": "U-SUSPICIOUSNESS",
        "status": null,
        "union_id": "U-SUSPICIOUSNESS"
      },
      {
        "id": "U-DIALECT-VERB",
        "status": null,
        "union_id": "U-DIALECT-VERB"
      },
      {
        "id": "U-LEGAL-USE",
        "status": null,
        "union_id": "U-LEGAL-USE"
      },
      {
        "id": "U-CEFR-LABELS",
        "status": null,
        "union_id": "U-CEFR-LABELS"
      },
      {
        "id": "U-CAM-GUILT",
        "status": null,
        "union_id": "U-CAM-GUILT"
      },
      {
        "id": "U-CAM-DISTRUST",
        "status": null,
        "union_id": "U-CAM-DISTRUST"
      },
      {
        "id": "U-CAM-SMALL-AMOUNT",
        "status": null,
        "union_id": "U-CAM-SMALL-AMOUNT"
      },
      {
        "id": "U-CAM-PRONUNCIATION",
        "status": null,
        "union_id": "U-CAM-PRONUNCIATION"
      },
      {
        "id": "U-AHD-UNVERIFIED",
        "status": null,
        "union_id": "U-AHD-UNVERIFIED"
      },
      {
        "id": "U-ETYMOLOGY-DETAIL-EXCLUDED",
        "status": null,
        "union_id": "U-ETYMOLOGY-DETAIL-EXCLUDED"
      },
      {
        "id": "U-CAM-UNCERTAIN-BELIEF",
        "status": null,
        "union_id": "U-CAM-UNCERTAIN-BELIEF"
      },
      {
        "id": "U-MW-UNCERTAINTY",
        "status": null,
        "union_id": "U-MW-UNCERTAINTY"
      },
      {
        "id": "U-FREQUENCY-RUBRIC",
        "status": null,
        "union_id": "U-FREQUENCY-RUBRIC"
      }
    ],
    "input_revision_id": "ce3dc8726d193de3df3fb075d35b9df8e59eb34be982b889837d27ff573dad8a"
  },
  "input_bindings": {
    "pass_findings.json": "ecd14d53e8402752c3afc8b1cbc6ab6f6dd01df0bd9aaaee54579e504a58531e",
    "cold_review.json": "64ea255b604cf711d465197361bcdbefbf8736e0cdcf7db50c2c104e4ed6ed14",
    "final_blind.json": "3b46694c88288392c04b42633c7521334d590a6bd086272d8deeafca02944596",
    "blind_seal.json": "a658e500d64af8ee2543a2afab4187824d77a81f2f30e5f471c879f2d9067a67",
    "pre_blind_resolution.json": "a8ebdd8cc233adf1c0b25bc53c20b4df23baa2dde0f2ab5e8dc1af00ac6030b1",
    "pre_blind_revision.json": "e4dc9d1af168802fda37bd253bda537b9c046ce3cae13b8029c3fe169ec1cfa8",
    "checker_recheck_manifest.json": "0663c2ccba935c7c036bf60e469eecd0673fb94f95bcb63f39329a9357a7adf6",
    "post_blind_resolution.json": "baaadef2f7f0ed1020fc62bb1c483edb1785f6a216778481a8fba5bc2e7ff9df",
    "post_blind_verification.json": "90f1d69c84ad7faedada4e46217de34d7be7d02a463729ebc1abf94d4d94a5aa",
    "targeted_adjudications.json": "ac46c0335504044b98274fd2fcb3beecc6863a5d4bbcacf787a0215932de3a8a",
    "source_inventory.json": "2f7c6b1efe170c2126f769a00d3814d927ce01a787d0dcac057d7268614f23c5",
    "resolutions.json": "f8ce481910f365022372644a253936af6393b53903d97693b2320a43b3ab72bc",
    "check_passes/checker_passes.stage1.json": "55901904b65cbe7599103d7902595371e5387a3a69188feeb5c0493ef3203f74",
    "check_passes/evidence.json": "ec659506e93f4af391142c0855620b1cbcf60b4788ab35396e9b445588920c9a",
    "check_passes/evidence.request.json": "16d8eee947b9f7feae8104b3b2eda41611543119c7360270560ec4b4e04c4361",
    "check_passes/example-attribution.alignment-key.json": "2c96a57dbd00c3bfde229de6797dce11d093dc8ccb2a67fa1597d6f7f866ce95",
    "check_passes/example-attribution.blind-record.json": "f302f519dda3131fe925545e43cb72f5cf38b20bd5afaf7df54702816b49aad1",
    "check_passes/example-attribution.json": "79cc77f138aa019455e4c41cffa269e440d449baae3d52a8e945812981931b50",
    "check_passes/example-attribution.request.json": "82025ee8eaf472eb092f361e02bfab3c3639bf54d35345303e27f32b761f23c1",
    "check_passes/frame-relation.antonym-axis.adjudication-record.json": "878e893861cf1a746a1fba6457b78934e1c4bf9ab28db10c0112ad23a6718ddf",
    "check_passes/frame-relation.antonym-axis.alignment-key.json": "c84c317736784af4ef0075a6246362268ba4d041cf466ee537ce9328a7a0d8b8",
    "check_passes/frame-relation.antonym-axis.blind-record.json": "0f347fd956df749aec2250d119571548f75bb9b3e313db7cd3f25920ddcde94a",
    "check_passes/frame-relation.antonym-axis.stage2.request.json": "068cc048c6c878085a7caaa981772d79188786140102737d75893b58cf1df8e1",
    "check_passes/frame-relation.request.json": "f31b98cfa90dfe94f7b601adb5ac1b912228498ddece53787bdc06ba421eca37",
    "check_passes/input_snapshot.json": "d9450a6a7408ed4ae30c9155742c26f8c8ff9ebe17c9af49d84055e8711b1a40",
    "check_passes/pronunciation.json": "3c4e590e6efb0dfd2c28592f46337f789f4d2c5b46493ad9be8fbd4eaeda4422",
    "check_passes/pronunciation.request.json": "e7f2fc06d8577a4e8544edbb365afd248f78b835d694a84d078246960083b9cf",
    "check_passes/qualification.json": "54f34dc1e4a9160d57352d4843f4112628f190669663cc77ac725ac7fbe0c289",
    "check_passes/qualification.request.json": "0b0171f1dd87d75d1ec37fbaf69db08bb7c3ec987d95b60aedba837db35ab790",
    "check_passes/sense-structure.json": "6a7868a3fa67ffef87e936bab9745f63805fbcb3832eb7894825e8ad4f9aff32",
    "check_passes/sense-structure.request.json": "6dca94d133f9e671300a6e077481e2334db4e129e74b63d4479cea0d765cb4a5",
    "check_passes/translation.json": "db04d980790d756553aa00d7d5e172dc64cf522aca247d71c0e54a9ed887823f",
    "check_passes/translation.request.json": "6d27a4dc43e58689df38a173f5d810cd67fcd5c374628e6a579211e5667feef0",
    "recheck/evidence.request.json": "d8eeedeba007fe6fe35199393f5fd8837fbc619c49ea7ca82220dacde935a4e5",
    "recheck/evidence.response.json": "184a98e8fa6698c62813666ad8cc4835b98f625c464b4d853119f6ce806b7dc8",
    "recheck/example-attribution.corrected.response.json": "754e4ef6fd80f2ce5d0831592e5d79966010e860f65f07ca6cfe919004c59cff",
    "recheck/example-attribution.output.json": "9b0bf8a70ccc14dad712743eddfeefd35a095eb13cea7d318edb1dffd0dbaeea",
    "recheck/example-attribution.request.json": "a41611fddd117217908f1c5cfc683e6afdae4b414e6a5d3d30796667f8942305",
    "recheck/example-attribution.response.json": "12e190b1fbba6f8ba3c3ccf65775042aed5dffa4ff5316323a1bffa14a86ba90",
    "recheck/frame-relation.corrected.response.json": "71eadf944703f44a7d2e53c0b60df45b804f66fa99006e5bb25e1d57a1fc1494",
    "recheck/frame-relation.output.json": "5ff07854b978b6ed691c0554bbac9f85d4a9ad8f4772601e28f9b4256cdd2cef",
    "recheck/frame-relation.request.json": "16d804f4af076ea324554364d2a2019895155af18ed574748fc42b408adf8019",
    "recheck/frame-relation.response.json": "a533e7ddd1d25a8144b8349c6cc7f12c63ba122f7292afcac40d718cb2ddb1c7",
    "recheck/frame-relation.stage2.request.json": "8783da790a726c8baa736b70e4194c5ac56a66eb3ab0d56289544c6a56fe41c4",
    "recheck/frame-relation.stage2.response.json": "c9adf7ab392fbe93a008535c48ee06bf6594c734e68bd524ce302c43b47238af",
    "recheck/pronunciation.request.json": "b2250e4b081d65965b8992a799d2cd0bd5751f6b1e50f561227bb7bacb7ab225",
    "recheck/pronunciation.response.json": "194a4c5f14d07c8c4c24ef919e45e252208b810844e88a6fd7d4bf8890bf7033",
    "recheck/qualification.request.json": "7983ee3e1c8e933a29afcaaf4bfc72386f6ff520a49cabfae7b4acff4536b1ba",
    "recheck/qualification.response.json": "1cfd13c2bb7a96ce1f3ad6b5a6489ae41b1b9e26525f1ad3bc79ff32253ba72c",
    "recheck/resolution-history.json": "59f60b11a7af111d28c9ae102882b11aec923e77109505d04f75991a85436850",
    "recheck/sense-boundary-targeted.request.json": "b2970fe8ae0581647b4f466e9853ff14e564049b931a6e0822821f311949b51c",
    "recheck/sense-boundary-targeted.response.json": "69a3c1cebd70a7e227cd31cbbc52b58afa9524e63c7a9d2de0d2959a09aaf523",
    "recheck/sense-structure.request.json": "873c8af69155cb654fb045d1b1b9bc5fae0584660cd2fc6d90fab4f786b315fb",
    "recheck/sense-structure.response.json": "faac2895724fff83cd267f31db45e5c9e1848125434a44b424f67c6672739e98",
    "recheck/translation.request.json": "ef5c968ceaf63f67eb033cbf0f727ea5d8e2c562bfd246d41e9df4bb97586bff",
    "recheck/translation.response.json": "0b7645defcef2ea2a058c07c39fb94bc32be6317de3bf13aba2b12eacf70ea6e"
  },
  "contract_version": "review_preflight_v1",
  "input_revision_id": "ce3dc8726d193de3df3fb075d35b9df8e59eb34be982b889837d27ff573dad8a"
}
```
