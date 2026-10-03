# 公開までの整合性 (compact_review_v1)

`AGENTS.md` と `prompts/compact_review_contract_v1.json` が新規runの正本。
旧runの再現には [legacy_workflow_integrity.md](legacy_workflow_integrity.md) を使う。

- 本文全体のhashは版の識別に使う。レビューの再利用は内容area・関連する語義構造・
  対応する根拠本文のhashで決める。単なる記録時刻、行番号、保存先、試行回数で失効させない。
- A/Bは異なる実行コンテキストで、生成者とは別に判断する。原応答は不変のまま残す。
  呼出元がrequestとrawのhash・担当ID・時刻を受領記録へ付ける。
- 未確認領域、blocking、実質的な誤訳、根拠不明の主要主張をPASSにしない。
  minorを採用せず公開する場合は、本文への影響を説明して記録する。
- 本文修正後は `compact_workflow.py --resume` の現在版公開判定を確認する。
  無関係な領域の旧判断は原版への参照を保持して再利用し、旧rawの本文hashを改変しない。
- `--finalize` はentry・queue・audit・runを同じ本文版へ結ぶ。PRのCI、実際のマージ、
  Notion同期は別途確認する。CIだけを記事の品質の証明とは呼ばない。
- 旧runの移行は既存runのIDと失敗履歴を保持し、別のmigration overlayに旧版・新版・
  対象head・原レビューの対応を残す。不足した確認だけを追加する。

レビュー失敗や中断では同じrunを再開する。時間の経過だけで自動PASSにも停止にもせず、
繰り返し解決しない争点は限定裁定へ送る。
