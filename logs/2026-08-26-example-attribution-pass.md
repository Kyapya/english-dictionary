# 2026-08-26 例文語義帰属検査パス改修

## 対象

- 改修A: `entry_spec_v5` と `check_spec_v5` に全語義共通の例文判別可能性ルールを追加。
- 改修B: `example_sense_attribution_mismatch` と `example-attribution` checker passを追加。
- 既存エントリ本文、queue、既存監査結果は変更していない。

## 実装記録

- stage 1では語義一覧と例文・訳だけを含む `example_attribution_blind_request_v1` を生成する。所属語義、コロケーション見出し、用途行、語法注記は含めない。
- stage 1判定を `example_attribution_blind_record_v1` として保存し、そのhashと時刻を検証する。
- stage 1保存後に限り、所属語義と語法注記を含む `example_attribution_alignment_key_v1` をstage 2へ渡す。
- stage 2は誤帰属・判別語のない曖昧例文を `blocking` findingへ変換し、正常例文にはfindingを出さない。
- 新規content auditには新taxonomyを必須化する一方、導入前の監査manifestは明示的contract markerの有無で互換性を維持し、遡及再チェックを要求しない。
- `prompts/migration_table_v5_to_v6.md` は現行仕様の対応表ではなく、`backups/2026-08-25-process-refactor` の固定投影であるため変更していない。

## 合成fixture実効性確認

- fixture: `tests/fixtures/example_attribution_polysemous.md`
- 同じ `veln 〈人〉` フレームを物理的追跡、案件継続、求愛の3語義へ配置した。
- 誤帰属 `example:004` と曖昧 `example:001` に `example_sense_attribution_mismatch` / `blocking` が出た。
- 一意な正常例 `example:002`、`example:003`、`example:005` にはfindingが出なかった。
- stage 2時刻がstage 1記録以前の場合に検証が失敗する回帰テストを追加した。

## 検証結果

- `python scripts/validate_repository.py`: PASS
- `python scripts/check_passes.py validate-router`: PASS
- `python -m unittest discover -s tests -p 'test_*.py'`: 182 tests PASS
- `python scripts/process_improvement.py validate`: PASS
- `python scripts/check_passes.py validate-blind-record ...`: PASS
- `python scripts/check_passes.py reconcile-example-attribution ...`: 誤帰属・曖昧の2 findingsを生成
- `python scripts/check_passes.py validate-output ... --entry ...`: PASS

## 逸脱・未解決事項

- 依頼書の列挙外だが、正本taxonomy、オーケストレータ、instruction budget記録、README/AGENTSのpass数、生成監査validator、関連テストを整合のため更新した。
- 未解決事項なし。
