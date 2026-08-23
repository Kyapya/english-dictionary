# final_review_spec_v1

このファイルは、通常チェック側でもコールドレビュー側でもない第三者が、保存直前の辞書記事へ最終合否を出すための現行完全版最終審査仕様である。

最終審査担当は、このファイルを最初から最後まで読んでから審査する。記事の作成、通常チェック、本文修正、コールドレビューのいずれかを担当した実行は、同じ記事の最終審査担当になってはならない。最終審査担当は本文を変更せず、まず監査記録を見ない盲検審査を完了・固定し、その後に監査記録を開いて照合して `PASS` または `REJECT` を決定する。

## 三者分離

各記事では次の三者を別の実行にする。

1. `normal_checker`: ゼロベース棚卸し、通常チェック、根拠収集、本文修正、コールドレビュー候補の判定を行う。
2. `cold_reviewer`: 仕様があらかじめ想定していない問題候補を、既知の判断に誘導されず1回だけ探索する。
3. `final_adjudicator`: 修正後本文だけから独立棚卸しと問題探索を行い、その盲検出力を固定してから、外部化された監査結果、根拠台帳、コールドレビューと解決結果を照合し、最終合否だけを決定する。

`normal_checker`、`cold_reviewer`、`final_adjudicator` の `reviewer_id`、`execution.run_id`、`execution.context_id` はそれぞれ相互に異ならなければならない。役割名の変更や同じ会話内の役割切替で分離を代用しない。各実行は開始・終了時刻、本文ハッシュ、promptハッシュ、文脈モード、入力物一覧を記録する。

## 入力

盲検審査の開始時に最終審査担当へ渡すのは次の二つだけとする。

- front matterを含む修正後の最新版記事。
- `prompts/final_review_spec_v1.md`。

この段階では対応する監査ファイル、通常チェック結果、コールドレビュー結果、queue、logs、差分、既知の懸念を見せない。見出し語だけから `final_review.independent_candidates` のID、表層形、完全な統語フレーム、意味、収録・除外判断、理由を作り、記事全体の問題候補を `final_review.blind_review.article_findings` に記録し、暫定合否を出す。さらに各独立候補について、その候補が正しいなら本文全体で満たされるべき、または満たしてはならない原子的な意味関係を `semantic_assertions` として1件以上作る。`semantic_assertions` は候補の境界・作用方向・包含関係・除外関係・一般化可能範囲などを、後で本文へ機械的に照合できる粒度にする。盲検出力は次のコマンドで `output_sha256` に固定してから照合へ進む。

```bash
python scripts/content_audit.py seal-blind audits/a/apple.json
```

盲検原出力 `audits/runs/.../final_blind.json` にも、各候補の `semantic_assertions` を候補本体と同時に保存する。`seal-blind` は `blind_seal_v2` と `sealed_at` を記録し、assertion本体を含めてハッシュ化する。seal直後の監査JSONと盲検原出力を、監査記録を開く前に一度コミットする。その後の別コミットでのみ `reconciliation_started_at`、監査側target・根拠リンクID、照合結果、最終合否を追加する。同一コミットでsealと最終照合を完成させてはならず、照合開始後にassertionを追加・削除・変更してはならない。

照合開始後に次を追加で渡す。

- 対応する `audits/<entry相対パス>.json`。
- 根拠台帳が参照する資料へアクセスするための情報。

最終審査側候補の `article_target_ids` と `evidence_link_ids` は、盲検で固定した候補内容を変えずに、この照合段階で追加する。target IDや通常チェック側の根拠IDを盲検段階で推測してはならない。

監査ファイルには、記事本文から自動抽出された全監査対象と全関係監査、通常チェック側の全件判定、独立棚卸し候補、主張単位の根拠リンク、コールドレビューの全候補、その構造化された解決結果、最新版本文へ結び付いたsemantic constraintと盲検candidate assertionの照合結果が含まれていなければならない。生成時の長い思考過程や、完成候補を正当化するための会話上の説得は渡さない。

## 最終審査担当の禁止事項

- 記事本文、queue、通常チェック結果、根拠台帳を自分で修正しない。
- 問題を発見した後、自分で直した版へ自分で `PASS` を出さない。
- 通常チェックの `pass`、コールドレビューの候補判定、資料名の記載を正しい前提として引き継がない。
- 項目数、監査件数、形式検証の成功を内容の正しさの代用にしない。
- 未判定項目、未確認資料、未解決候補を「軽微」として通過させない。
- 盲検出力を固定した後に、通常チェックの棚卸しへ合わせて独立棚卸し、問題候補、`semantic_assertions` を書き換えない。
- seal済み盲検状態の先行コミットを作らず、同一コミットで監査照合と最終合否まで記録しない。
- 以前のrevisionで修正済みという説明だけで、現在の本文でもfindingが解決済みだと扱わない。

## 全監査対象の個別判定

`scripts/content_audit.py build` が生成した `targets` を正本の監査対象一覧とする。最終審査担当は各targetを一つずつ確認し、`final_review.target_results` に同じIDで `pass` または `fail` を記録する。まとめて「全文確認済み」とだけ記録してはならない。

監査対象には、少なくとも次が含まれる。

- 語義見出しと語義境界。
- 日本語訳・定義。
- 頻度とレジスター。
- 文法パターンを区切った各完全フレーム。
- 各コロケーションのパターン、用途、例文、訳の組。
- 語法・注意。
- 発音記号と発音説明。
- 語源、語形成、コアイメージ。
- 各類義語・反意語の定義、頻度、差、例文、訳の組。

各targetの `notes` には、そのtargetで何を照合して合格または不合格としたかを書く。具体性は審査上の要件だが、文面の一致だけでは内容の未確認を証明できないため、検証スクリプトは同一・定型的な文面であることだけを理由に機械的に拒否しない。

## 関係監査の個別判定

単一箇所の正誤だけでは検出できない問題を、`scripts/content_audit.py build` が `relations` として自動生成する。通常チェックと最終審査は、絞り込まれて生成された全relationを同じIDで個別判定する。件数を増やすこと自体を網羅性と見なさない。

- 記事内の相互参照などが混同リスクを示す語義対の最小差、境界、重複、統合可能性。全語義対の直積は作らない。
- 語義見出しと詳細定義の整合。
- コロケーションの用途・英文・訳の意味関係。
- 定義と語法注意の整合。
- 定義と類義語・反意語欄の同義性、上下関係、対立軸の整合。
- 文法パターンと用例群の対応。
- コアイメージで語義番号が明示された枝と、当該語義の見出し・詳細定義・語法の対応。語義番号を限定しない総括文は、語義目録全体との整合を1件で確認する。
- 記事内の語法・定義・相互参照が混同リスクを具体的に示す語義対の境界。全語義ペアの直積は作らない。
- 記事全体から生じる学習者の誤った一般化。

relationが一つでも未判定または `fail` なら `PASS` にしない。

## 独立棚卸し候補の判定

監査ファイルを見る前に、最終審査担当自身が見出し語から語義・品詞・完全な統語フレームを棚卸しし、収録・除外の別を含めて `final_review.independent_candidates` に記録する。この棚卸しは通常チェック側の候補IDや分類を見て作ってはならない。

各候補には `semantic_assertions` を1件以上付ける。各assertionは `id`、`statement`、`polarity`、`scope` を持ち、`polarity` は `must_hold` または `must_not_hold` とする。たとえば除外候補なら「この意味を通常義として本文へ一般化しない」、専門義なら「AはBの一種であり同義語として無条件に置換しない」、作用関係なら「AがBに作用し逆向きに説明しない」のように、候補の正しさを本文へ適用したときの境界を原子的に外部化する。候補の意味説明を言い換えただけのassertionではなく、本文に反する記述があれば不合格にできる関係を書く。

盲検出力を固定して監査ファイルを開いた後、`normal_review.independent_candidates` と最終審査側の全候補を双方向に比較し、`final_review.inventory_comparison` に `match`、`normal_only`、`final_only`、`classification_conflict` のいずれかを記録する。両方の候補一覧を一件残らず照合し、差が記事の欠落または過剰収録を示す場合は `fail` とする。

そのうえで、`normal_review.independent_candidates` の全候補について、実在性、完全な統語フレーム、中心意味、頻度・学習価値、本文への収録または除外理由、根拠を確認する。本文にある項目だけでなく、通常チェック側が除外した候補も確認する。

各候補を `final_review.candidate_results` に同じIDで記録する。収録候補に有効な本文targetへの対応がない、除外候補の理由や根拠が不足している、主要候補自体が棚卸しから欠落していると判明した場合は `REJECT` とする。

さらに最終審査側の全独立候補について、盲検で固定した全`semantic_assertions`を現在の本文へ実際に適用し、`semantic_gate.final_inventory_checks` を候補と1対1で作る。各checkにはcandidate ID、全assertion ID、現在の本文ハッシュ、実際に確認したtarget・relation・記事内query、queryごとの一致件数と一致target ID、`pass`/`fail`、具体的notesを記録する。`included` 候補では照合段階で対応付けた全 `article_target_ids` と、それらを含む全生成relationを再確認する。`excluded` 候補でも対応targetがないことだけを根拠にせず、その境界を侵食しうる定義、コアイメージ、語法、相互参照、例文をtarget・relationまたは明示的な全文queryで確認する。盲検棚卸しで正しい除外理由を書いていても、本文に逆の一般化が残っていれば `fail` とする。

## 根拠台帳の検証

`targets` で `requires_evidence: true` の項目、生成された全relation、両者の独立棚卸し候補、findingとresolution、棚卸し比較には主張単位の `evidence_links` が必要である。各リンクには対象種別・対象ID、検証する主張、資料ID、位置種別、資料内の具体的位置、その箇所の短い引用または忠実な要約、どのように支持するか、当該語義・構文への適用範囲、支持種別、反例確認の方法と結果を記録する。最終審査担当は、単に資料名があることではなく、資料の該当箇所が実際に対象主張を支えることを確認し、各結果の `evidence_link_ids_checked` に確認済みリンクIDを記録する。

最終審査で使用した全根拠リンクについて `final_review.evidence_checks` を1件ずつ作る。IDはevidence link IDと一致させ、`status`、`claim_supported`、`locator_verified`、`applicability_confirmed`、`contradiction_status`、具体的notesを記録する。`PASS` では、全checkがpassで、主張・locator・適用範囲が確認済みであり、未解決の矛盾がないことを必須とする。同じcitationを別のevidence IDへ複製して独立した2資料として数えてはならない。

`evidence_policy: two_sources_or_primary` の高リスク対象は、独立した2資料または当該主張へ直接適用できる一次資料がなければ `pass` にしない。特に地域差、専門・制度用法、語義境界、頻度、類義語・反意語、絶対表現では、一般的な辞書名や検索見出しだけで根拠要件を満たしたと扱わない。

少なくとも次の主張は高リスクとして扱う。

- 発音、弱形、強勢、音節、米英差・地域差。
- 語源、成立年代、意味変化、語形成。
- 語義境界、文法制約、完全な統語フレーム。
- コロケーション、例文の自然さ、語法上の制約、コアイメージによる語義対応。
- 「必ず」「常に」「通常」「のみ」「できない」など、適用範囲を限定する主張。
- 頻度、古風性、専門性、口語・文語などのレジスター。
- 法律、保険、税務、医療、資格制度などの専門説明。
- 類義語・反意語との中心的な差。

検索結果の見出し、資料名だけ、別義を扱う用例は根拠としない。資料が食い違う場合は、適用範囲を限定できるかを確認し、確定できなければ `REJECT` とする。断定的な主張では、支持例だけでなく反例・打ち消し例がないかも確認する。

## 例文と訳の汎用監査

各例文と訳について、単語の一対一置換だけでなく、次の意味関係が保存されているか確認する。

- 述語とその主語・目的語・補語。
- 行為者、経験者、対象、結果などの意味役割。
- 肯定・否定、比較基準、程度、数量。
- 時制、相、法、条件、因果、目的。
- 修飾範囲、焦点、対比、情報構造。
- 原文で明示された内容と、文脈から推論されるだけの内容の境界。
- レジスターと話者評価。

原文と訳でこれらの向き、範囲、強さが変わる場合は、自然な意訳であっても説明目的を損なわないかを判定する。見出し語の構文差や含意を誤って学習させる訳は `fail` とする。

## コールドレビュー候補と解決結果の検証

コールドレビューの全findingと、通常チェック側による全resolutionを確認する。各findingの全`scope_anchors`が原出力から改変されず、resolutionの`scope_anchor_results`へ1対1で引き継がれていることを先に確認する。resolutionには `problem_confirmed`、理由、必要な変更、影響target・relation、実施した変更、残存リスク、根拠リンクを記録する。問題が確認されたresolutionは、さらに1件以上のsemantic constraint IDと `resolved_on_body_sha256` を持たなければならない。semantic constraintは自由文の修正メモではなく、そのfindingから得た正しい意味関係を `must_hold` / `must_not_hold` の原子的制約として表し、全scope anchor ID、影響target・relationまたは記事内query、現在の本文で最後に再確認した `verified_on_body_sha256`、確認notesを持つ。

最終審査はfindingの妥当性とresolutionの完了性を分け、`finding_validity`、`resolution_status`、実際に確認した変更、未解決問題を `final_review.finding_results` に同じIDで記録する。問題確認済みfindingには、現在の本文ハッシュを `verified_body_sha256`、再確認した全constraint IDを `verified_invariant_ids`、全scope anchorから引き継いだtarget、当該targetを含む全生成relation、全queryを `blast_radius_target_ids`、`blast_radius_relation_ids`、`blast_radius_queries_checked` として記録する。さらに `blast_radius_query_results` に各queryの一致件数と一致target IDを保存する。

採用修正が最新版へ反映されているか、不採用理由が資料と仕様に支えられているか、保留が残っていないかを確認する。特に「revision-003で修正した」のような過去revisionの説明だけでは解決済みとしない。現在の `body_sha256` と `resolved_on_body_sha256`、constraintの `verified_on_body_sha256`、final findingの `verified_body_sha256` がすべて一致し、元findingのaffected target/relationとconstraintで指定されたblast radiusを最新版全文で再確認した場合だけ `resolved` / `pass` とする。

コールドレビューの候補が0件の場合も、`summary` に「問題候補なし」があり、独立条件を満たした実行であることを確認する。コールドレビューの候補が少ないことや0件であることを、記事内容の合格根拠にはしない。

## semantic resolution hard gate

最終合否の直前に次を実行し、終了コード0でなければ `PASS` にしない。

```bash
python scripts/semantic_resolution_gate.py validate-entries entries/a/apple.md
```

この検証は少なくとも次を機械的に拒否する。

- 現在本文と異なるハッシュに結び付いた古いconstraint、resolution、finding確認、inventory check。
- 問題確認済みコールドfindingに対応するsemantic constraintがない状態。
- resolutionが宣言したconstraintを最終findingが全件再確認していない状態。
- findingのscope anchor、affected targetに接続するrelation、queryの一部をblast radius確認から落とした状態。
- queryの一致件数・一致target IDが最新版の機械的再計算と異なる状態。
- 最終候補の `semantic_assertions` が盲検原出力に存在せず、監査開封後に後付けされた状態。
- 最終盲検candidateと `semantic_gate.final_inventory_checks` が1対1で対応していない状態。
- `included` 候補の本文対応targetを全件再確認していない状態。
- `included` 候補の対応targetに接続するrelationを全件再確認していない状態。
- 最終審査で使用した根拠リンクの主張支持・locator・適用範囲・矛盾確認が欠ける状態。
- 最終照合の原出力が件数集計だけで、監査マニフェストの全個別判定と一致しない状態。
- 最終decisionが `pass` なのにcandidate assertionの本文照合が `fail` の状態。

機械検証は意味内容そのものを代わりに判断するものではない。最終審査担当が一度作った正しい意味判断を、最新版本文に適用した証跡なしに捨てたり、古い本文への確認を使い回したりできないようにするためのハードゲートである。

## 履歴・原出力・回帰確認

`content_audit_v3` の `review_history`、`current_cycle.body_revisions`、`current_cycle.raw_outputs` を確認する。各body revisionは本文スナップショットの実体とハッシュが一致しなければならない。通常、コールド、最終盲検、最終照合の各原出力は別のJSONファイルで保存され、SHA-256、run ID、context ID、入力本文・promptハッシュが各executionと一致しなければならない。加えて、通常の全target・relation・候補、コールドの全finding・scope anchor、最終盲検の全候補・finding、最終照合の全個別判定・evidence check・inventory check・blocker・decisionを監査マニフェストと完全一致させる。件数だけを記録した原出力から個別PASSを後付けしてはならない。コールドレビュー原出力は同一cycleにつき1件だけとする。

完了済み監査後の本文修正または再審査では、旧監査原文が `audits/history/` に不変のまま追記され、新しいcycle IDで審査されていることを確認する。過去の本文ハッシュや判定を現在値へ書き換えて履歴を整合させてはならない。

`audits/escaped_defect_taxonomy.json` の全分類について `regression_checks` が `pass` または理由付き `not_applicable` であり、レビュー後に判明した不備があれば語固有ではない分類、影響target、再発防止策が `escaped_defects` に記録されていることを確認する。

## 本文ハッシュと再審査

最終審査はfront matterを除く本文のSHA-256へ結び付ける。`final_review.body_sha256` が現在の本文と一致しない場合、過去の判定は無効である。

semantic resolutionも同じ本文ハッシュへ結び付ける。本文を再修正してハッシュが変わった場合、コールドレビュー自体を原則やり直す必要はないが、全semantic constraint、問題確認済みresolution、final finding result、全final inventory checkを新しい本文へ再照合するまでstaleとする。

`REJECT` 後の本文修正は通常チェック側が行う。最終審査は初回と修正後再審査を合わせて同一依頼内で最大2回とし、各回の前に `scripts/source_first_audit_gate.py record-attempt <entry> --stage final` を実行する。2回目のREJECTでは同じ依頼内で新cycleや追加審査を開始せず、blockerを保持した `needs_review`、checked falseとして安全停止する。コールドレビューは原則1回のままとするが、主要品詞・語義構成を全面的に作り直す必要が判明した場合は安全停止し、次の明示的な依頼で新cycleとしてコールドレビューから開始する。

## bounded source-first直接照合

新規・変更監査は `prompts/source_first_audit_v2.md` に従う。盲検棚卸しとsealまではsource-first監査を見ない。seal後、`source_union`、各unionのfact、対応するclaim unit、直接対応targetを確認し、機械生成済みの `final_review.source_inventory_results` にunionごとのstatusと具体的notesだけを記録する。fact ID・target ID一覧を最終結果へ再転記しない。通常候補と最終候補が一致していても、source union直接照合の代用にしない。

## 合否

次のすべてを満たす場合だけ `PASS` とする。

1. 三者の実行・文脈識別子が異なり、実行履歴と入力物が記録されている。
2. 本文ハッシュが一致する。
3. 監査記録を見ない盲検審査と独立棚卸しが先に完了・固定され、全独立候補の `semantic_assertions` も盲検原出力に固定されている。
4. 通常チェックと最終審査の棚卸しを双方向に全件比較している。
5. 自動抽出された全targetと全relationに最終判定があり、すべて `pass` である。
6. 通常チェック側の独立棚卸しの全候補に最終判定があり、すべて `pass` である。
7. 盲検審査の全問題候補とコールドレビューの全findingを照合し、問題確認済みfindingはsemantic constraintと最新版本文ハッシュ付きblast-radius確認を含めてすべて解決済みである。
8. 最終盲検の全独立候補について、全`semantic_assertions`を最新版本文へ照合した `semantic_gate.final_inventory_checks` があり、すべて `pass` である。
9. 必須対象の主張単位の根拠リンクを実際に確認している。
10. 使用した全根拠リンクの `final_review.evidence_checks` がpassで、主張支持・locator・適用範囲・矛盾探索を確認している。
11. 四段階の原出力と監査マニフェストの全個別結果が完全一致している。
12. `hold` と未解決事項がない。
13. `blockers` が空である。
14. `python scripts/semantic_resolution_gate.py validate-entries <entry>` が終了コード0である。

一つでも満たさない場合は `REJECT` とし、`blockers` に対象ID、問題、必要な修正を記録する。条件付き合格は使用しない。`REJECT` は監査失敗や途中状態ではなく、最終審査が完了して問題を正しく検出した正常な成果である。監査ファイルを保持し、記事をstatus `needs_review`、checked `false` にして修正工程へ戻す。

`PASS` 後、調整役は判定内容を変更せず、front matterとqueueをstatus `checked`、checked `true` へ機械的に同期する。通常チェック側が自ら合格を宣言してこの状態変更を行ってはならない。最終状態で全形式検証、repository検証、単体テスト、content audit検証、semantic resolution hard gateを実行し、すべて成功した場合だけ確定する。

【現行完全版最終審査仕様終わり】
