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
