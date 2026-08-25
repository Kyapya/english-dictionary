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

## 本文改稿

新規cycleでは `revision-00N.md` を生成しない。本文の各改稿は `scripts/run_word.py` が記事だけの個別Git commitとして記録し、Git commitを改稿履歴の正本にする。旧 `content_audit_v3` 用の `build`、`start-cycle`、`add-revision` CLIは退役済みである。

## 判定仕様

- 内容パス: `prompts/check_router_v6.md` と `prompts/check_pass_*_v6.md`
- final blind: `prompts/final_blind_prompt_v2.md`
- 最終合否: `prompts/final_review_spec_v2.md`
- raw→manifest・seal・網羅性: `scripts/generate_audit_manifest.py`
- 旧v1〜v3互換検証: `scripts/content_audit.py`、`scripts/semantic_resolution_gate.py`

既存監査の形式や過去ファイルを一括変換・移動・削除しない。次の新規runからv4を使用する。
