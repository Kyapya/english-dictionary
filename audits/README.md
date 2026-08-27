# 内容監査ファイル

`audits/` はレビュー原出力と、そこから機械生成した最終判定を保存する。記事と同じ相対パスの `audits/<initial>/<slug>.json` は新規runでは `content_audit_v4` とし、手で編集しない。既存のv1〜v3監査、`audits/history/`、過去のrevision snapshotは参照資産としてそのまま残す。

## v4の正本

新規cycleの正本は `audits/runs/<initial>/<slug>/<cycle-id>/` にある別々のraw JSONとGit履歴である。

- `source_inventory.json`
- `pass_findings.json`
- `cold_review.json`
- `resolutions.json`
- `final_blind.json`
- `blind_seal.json`
- `final_review.json`

`scripts/generate_audit_manifest.py` はraw JSONのhash、全finding、finding→resolution対応、最終decisionだけをroot manifestへ投影する。root manifestにrawにない判定を追加すると再生成比較で失敗する。`finding_scope_transfer_loss` は全finding IDとresolution IDの集合一致、`raw_adjudication_manifest_divergence` はmanifestの完全再生成比較により防止する。

```bash
python scripts/generate_audit_manifest.py seal-blind \
  entries/a/apple.md \
  audits/runs/a/apple/cycle-001/final_blind.json \
  --output audits/runs/a/apple/cycle-001/blind_seal.json

python scripts/generate_audit_manifest.py generate \
  entries/a/apple.md \
  audits/runs/a/apple/cycle-001 \
  --output audits/a/apple.json

python scripts/generate_audit_manifest.py validate \
  entries/a/apple.md audits/a/apple.json
```

blind入力の独立性、三者のrun/context分離、各段の入力artifact、本文hash、全target/relation/candidate/finding/evidence/source-union結果、未解決0件、blockerとdecisionの整合はgeneratorとCIが検証する。blind sealと `final_blind.json` は `final_review.json` が存在する前の先行commitに固定されなければならない。

## レビュー実体・liveness

新規レビュー出力には `reviewer.mode`（`api` または `handoff`）とモード固有の出所情報が必須である。APIの生応答は `raw/<stage>.response.json` に残し、`request_sha256` は保存した入力packet、`response_id` は生応答IDと一致しなければならない。handoffは別モデル・別セッションの応答だけを取り込む。

`scripts/review_liveness.py` は次を検査する。閾値は同スクリプト先頭の定数に集約し、rationale / notes の個別性は対象IDを除去した正規化文字列の種類数÷件数が `0.60` 以上でなければならない。

- `B1_term_not_in_example`: 判別語が対象例文または訳に実在しない。
- `B2_rationale_not_distinct`: rationale / notes が対象ごとに十分異ならない。
- `B2_rationale_not_grounded`: exact quote・判別語・候補固有表現のいずれにも接地していない。
- `B3_attribution_copy_pattern`: 判別語の種類数が語義数以下で、語義ラベル転写の兆候がある。
- `B4_zero_finding_single_review`: ゼロfinding runを異なる第2モデルのcold reviewとexample-attributionが再確認していない。

無効化されたrawは削除しない。派生manifestには `invalidated_by` と `review_liveness_errors` を残す。B1〜B3を含む場合は `needs_review / checked: false`、B4だけの場合は第2レビュー待ちの `review_ready / checked: false` で停止する。異なる第2モデルで再確認したゼロfinding runだけが `checked` へ進める。

外部レビューで判明した欠陥は `audits/escaped_defects.json` に記録し、`python scripts/queue_status.py escaped-by-stage` で本来の検出段別に集計する。taxonomy側の `expected_detection_stages` を段の所有関係の正本とする。この集計から作る新しい工程改善recordは、対応するIDを `escaped_defect_ids` に列挙する。

## 本文改稿

新規cycleでは `revision-00N.md` を生成しない。本文の各改稿は `scripts/run_word.py` が記事だけの個別Git commitとして記録し、Git commitを改稿履歴の正本にする。旧 `content_audit_v3` 用の `build`、`start-cycle`、`add-revision` CLIは退役済みである。

## 判定仕様

- 内容パス: `prompts/check_router_v6.md` と `prompts/check_pass_*_v6.md`
- final blind: `prompts/final_blind_prompt_v2.md`
- 最終合否: `prompts/final_review_spec_v2.md`
- raw→manifest・seal・網羅性: `scripts/generate_audit_manifest.py`
- 旧v1〜v3互換検証: `scripts/content_audit.py`、`scripts/semantic_resolution_gate.py`

既存監査の形式や過去ファイルを一括変換・移動・削除しない。次の新規runからv4を使用する。
