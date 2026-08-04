from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PromptContractTests(unittest.TestCase):
    def test_entry_v4_keeps_required_quality_gates(self) -> None:
        text = (REPO_ROOT / "prompts" / "entry_spec_v4.md").read_text(encoding="utf-8")
        required = (
            "prompts/entry_spec_v3.md",
            "生成前の必須構文マトリクス",
            "分詞形容詞の必須監査",
            "再帰形・代名詞位置・語順交替の必須監査",
            "品詞境界とブロック整合",
            "最小対立の必須化",
            "コアイメージと歴史的語義",
            "prompt_version` は `entry_spec_v4",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_check_v4_keeps_independent_audit_gates(self) -> None:
        text = (REPO_ROOT / "prompts" / "check_spec_v4.md").read_text(encoding="utf-8")
        required = (
            "旧本文の見出し、語義番号、語義名、コロケーション数をチェックの出発点にしない",
            "独立棚卸し台帳",
            "本文収録台帳",
            "必須の品詞・派生形監査",
            "必須の構文差監査",
            "最小対立監査",
            "コアイメージ監査",
            "v4チェック完了条件",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_agents_routes_generation_and_checking_through_v4(self) -> None:
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("prompts/entry_spec_v4.md", text)
        self.assertIn("prompts/check_spec_v4.md", text)
        self.assertIn("prompt_version: entry_spec_v4", text)

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
