from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PromptContractTests(unittest.TestCase):
    def test_entry_v5_complete_spec_keeps_all_quality_gates(self) -> None:
        text = (REPO_ROOT / "prompts" / "entry_spec_v5.md").read_text(encoding="utf-8")
        required = (
            "生成前の必須構文マトリクス",
            "分詞形容詞の必須監査",
            "再帰形・代名詞位置・語順交替の必須監査",
            "品詞境界とブロック整合",
            "最小対立の必須化",
            "コアイメージと歴史的語義",
            "語義棚卸しと構文棚卸しを別々",
            "行末に半角スペースをちょうど2個",
            "コロケーションエントリは次の4行固定",
            "類義語・反意語の各エントリは次の6行固定",
            "prompt_version: entry_spec_v5",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_check_v5_complete_spec_keeps_all_independent_audit_gates(self) -> None:
        text = (REPO_ROOT / "prompts" / "check_spec_v5.md").read_text(encoding="utf-8")
        required = (
            "旧本文の見出し、語義番号、語義名、コロケーション数をチェックの出発点にしない",
            "独立棚卸し台帳",
            "本文収録台帳",
            "必須の品詞・派生形監査",
            "必須の構文差監査",
            "最小対立監査",
            "コアイメージ監査",
            "v5書式監査",
            "チェック後の必須コールドレビュー・判定修正・条件付き再検査",
            "front matterを除いた通常チェック後の最新版本文",
            "文脈を継承しない独立実行",
            "語義の分け方・境界・重複",
            "学習者が説明から誤った一般化",
            "採用修正がある場合の全文再検査",
            "チェック完了条件",
            "prompt_version: entry_spec_v5",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_v5_preserves_source_quality_and_exact_format_contract(self) -> None:
        entry = (REPO_ROOT / "prompts" / "entry_spec_v5.md").read_text(encoding="utf-8")
        check = (REPO_ROOT / "prompts" / "check_spec_v5.md").read_text(encoding="utf-8")
        notion = (REPO_ROOT / "prompts" / "notion_spec_v1.md").read_text(encoding="utf-8")
        for marker in (
            "現行完全版生成仕様",
            "行末に半角スペースをちょうど2個",
            "各コロケーションエントリは次の4行固定",
            "類義語・反意語の各エントリは次の6行固定",
            "生成前の必須構文マトリクス",
            "prompt_version: entry_spec_v5",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, entry)
        self.assertIn("二段階の独立チェック", check)
        self.assertIn("1エントリを1つのNotionテキストブロック", notion)
        self.assertIn("同一rich_textブロック内のネイティブ改行", notion)

    def test_single_cold_review_flow_is_required_before_checked(self) -> None:
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        check = (REPO_ROOT / "prompts" / "check_spec_v5.md").read_text(
            encoding="utf-8"
        )
        entry = (REPO_ROOT / "prompts" / "entry_spec_v5.md").read_text(
            encoding="utf-8"
        )
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        review_prompt = (
            "英単語解説として問題がないか、記事全体を横断して"
            "内容上の問題を前提なしで指摘してください。各文の正誤だけでなく、"
            "語義の分け方・境界・重複と、学習者が説明から"
            "誤った一般化をしないかも確認してください。"
        )
        old_review_prompt = (
            "英単語解説として問題がないか、"
            "内容上の問題を前提なしで指摘してください。"
        )

        for text in (agents, check, entry, readme):
            self.assertIn("コールドレビュー", text)
            self.assertIn("1回", text)
            self.assertIn("全文再検査", text)
            self.assertIn("採用が1件以上", text)
            self.assertIn("採用が0件", text)
            self.assertIn("最終状態", text)

        for text in (agents, check, readme):
            self.assertIn("採用", text)
            self.assertIn("不採用", text)
            self.assertIn("保留", text)
            self.assertIn(review_prompt, text)
            self.assertNotIn(old_review_prompt, text)
            self.assertIn("語義", text)
            self.assertIn("誤った一般化", text)

        self.assertIn("文脈を継承しない独立実行を1回", check)
        self.assertIn("本文中の語義名、語義番号、語義境界", check)
        self.assertIn("front matterを除いた通常チェック後の最新版本文", check)
        self.assertIn("`保留`が0件", check)
        self.assertIn("コールドレビューが未実施", agents)
        self.assertIn("生成仕様、チェック仕様、過去の指摘", readme)
        self.assertIn(
            "通常チェックが完了し、主要項目の収録先と品詞整合を"
            "説明できる場合も、この時点では",
            entry,
        )
        self.assertIn(
            "問題候補はあるが採用0件なら"
            "「コールドレビューの採用0件につき全文再検査省略」",
            check,
        )
        for text in (agents, check, entry, readme):
            self.assertNotIn("2回のコールドレビュー", text)
            self.assertNotIn("相互に結果を見せない", text)
            self.assertNotIn("第1レビュー", text)
            self.assertNotIn("第2レビュー", text)
            self.assertNotIn("採用が0件でも", text)
        self.assertNotIn(
            "内容監査まで完了し、主要項目の収録先と品詞整合を"
            "説明できる場合だけ `status: checked`",
            entry,
        )
    def test_current_specs_are_standalone(self) -> None:
        current_files = (
            REPO_ROOT / "prompts" / "entry_spec_v5.md",
            REPO_ROOT / "prompts" / "check_spec_v5.md",
            REPO_ROOT / "AGENTS.md",
        )
        legacy_paths = tuple(
            f"prompts/{kind}_spec_v{version}.md"
            for kind in ("entry", "check")
            for version in range(1, 5)
        )
        for path in current_files:
            text = path.read_text(encoding="utf-8")
            for legacy_path in legacy_paths:
                with self.subTest(path=path.name, legacy_path=legacy_path):
                    self.assertNotIn(legacy_path, text)

    def test_agents_routes_generation_and_checking_through_complete_v5(self) -> None:
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("prompts/entry_spec_v5.md", text)
        self.assertIn("prompts/check_spec_v5.md", text)
        self.assertIn("prompts/notion_spec_v1.md", text)
        self.assertIn("prompt_version: entry_spec_v5", text)
        self.assertNotIn("v3・v4・v5", text)

    def test_github_flow_uses_codex_not_an_api_generator(self) -> None:
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        validate_workflow = (
            REPO_ROOT / ".github" / "workflows" / "validate.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("生成主体は、ユーザーから依頼を受けて", agents)
        self.assertIn("OpenAI APIキーは不要", readme)
        self.assertIn("pull_request:", validate_workflow)
        self.assertIn("scripts/validate_repository.py", validate_workflow)
        self.assertFalse(
            (REPO_ROOT / ".github" / "workflows" / "generate-entry.yml").exists()
        )
        self.assertFalse((REPO_ROOT / "scripts" / "generate_entry.py").exists())


if __name__ == "__main__":
    unittest.main()
