# English Dictionary project router

英単語・短い英語フレーズを1記事1 Markdownで管理する。内容基準は
`prompts/entry_spec_v5.md`、工程・入力分離・checkpoint・budget・statusは
`scripts/run_word.py` と参照スクリプトが正本である。

## オーケストレータ

```bash
python scripts/run_word.py --dry-run <headword>
python scripts/start_word.py <headword>
python scripts/run_word.py --resume <audits/workflow_runs/...json>
```

同一見出し語の未完了runは新規作成せず、オーケストレータの出力どおりに再開する。
checker、example-attribution、cold review、final blind、final reviewは生成担当と
独立した `scripts/review_call.py` または handoff の出力だけを受け付ける。

### 局所修整

`checked` / `final` の具体的な修整は `prompts/targeted_correction_review_v1.md`
と `scripts/targeted_correction.py` の局所経路を使う。全面改稿は通常工程で行う。

### checker_passes: 7並列 + frame-relationのみ2往復

7パスを一つに連結せず独立実行する。APIは最大7 worker、`frame-relation`だけ同一worker
内で `antonym_axis_blind_record` のstage 1→2を直列化する。handoffは7個のrequestを
同時に1パス1独立agentへ渡し、応答の正しい `pass_id`・一意な `reviewer.agent_id` を
要求する。欠落・ID不一致・重複はfan-inで拒否する。

7応答を `checker_passes.stage1.json` に保存し、frame-relationだけ第2往復へ進める。
`checker_passes.stage2.request.md` と並列名のrequestを作り、stage 1と同じagent/model
のresponseを受け付ける（旧v3の `checker_passes.stage2.response.json` も可）。この
2往復中の取り込み失敗3回は `budget_exhausted` とし、並列中もheartbeat・budgetを進める。

## ファイル・status

記事は `entries/{slugの先頭1文字}/{slug}.md`、run成果物は `audits/workflow_runs/` と
`audits/runs/` に置く。statusは `pending`、`draft`、`format_error`、`needs_review`、
`review_ready`、`checked`、`final`、`skip` を使う。

## 正本

| 用途 | 正本 |
|---|---|
| 記事内容 | `prompts/entry_spec_v5.md` |
| 通常チェック | `prompts/check_router_v6.md`、`prompts/check_pass_frame_relation_v7.md`、`prompts/check_pass_*_v6.md` |
| コールドレビュー | `prompts/cold_review_prompt_v1.md` |
| 最終盲検 | `prompts/final_blind_prompt_v2.md` |
| finding解決・最終合否 | `prompts/finding_resolution_v6.md`、`prompts/final_review_spec_v2.md` |
| 局所修整 | `prompts/targeted_correction_review_v1.md`、`scripts/targeted_correction.py` |
| source-first・semantic gate | `prompts/source_first_audit_v2.md`、`prompts/semantic_resolution_gate_v1.md` |
| 工程・形式・整合 | `scripts/run_word.py`、`scripts/entry_workflow_guard.py`、`scripts/validate_entry.py`、`scripts/validate_repository.py` |
| Notion・改善 | `prompts/notion_spec_v1.md`、`process_improvement/ACTIVE.md`、`scripts/process_improvement.py` |

旧工程文書は `backups/2026-08-25-process-refactor/`、規範移設表は
`prompts/migration_table_v5_to_v6.md` を参照する。
