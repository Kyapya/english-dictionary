# targeted_adjudication_v1

具体的に記録された一つの未解決争点だけを、衝突した判断を出した担当とは別の
独立agent/contextで裁定する。全文レビューや同じpassの単純再実行ではない。

## 入力

- 一つの明確な質問
- 関係する本文抜粋
- 衝突または不確実な判断と各根拠
- 必要な既存source excerptまたはsource fact

無関係な記事全体、全監査履歴、生成文脈を入力しない。findingがゼロ、記事が長い、
多義語・専門語である、「念のため」だけを起動理由にしない。

## 出力

`targeted_adjudication_v1` JSONとして `issue_id`、独立性を示す `reviewer.agent_id`、
`decision` (`resolved_correct | resolved_needs_change | insufficient_evidence`)、
`rationale`、`applicable_scope` を返す。`insufficient_evidence` はPASSへ変換せず、
主張の限定・削除または明示的な追加調査が必要な未解決事項として停止する。
