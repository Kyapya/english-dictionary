from __future__ import annotations

import json
import subprocess
import sys
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

    def test_pre_refactor_specs_are_preserved_unchanged(self) -> None:
        backup = REPO_ROOT / "backups" / "2026-08-25-process-refactor" / "prompts"
        for name in ("entry_spec_v5.md", "check_spec_v5.md", "final_review_spec_v1.md"):
            with self.subTest(name=name):
                self.assertEqual(
                    (REPO_ROOT / "prompts" / name).read_bytes(),
                    (backup / name).read_bytes(),
                )

    def test_v6_checker_prompts_are_small_and_taxonomy_focused(self) -> None:
        router = (REPO_ROOT / "prompts" / "check_router_v6.md").read_text(
            encoding="utf-8"
        )
        self.assertLess(len(router.encode("utf-8")), 8_000)
        self.assertIn("finding_scope_transfer_loss", router)
        self.assertIn("raw_adjudication_manifest_divergence", router)
        for path in sorted((REPO_ROOT / "prompts").glob("check_pass_*_v6.md")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertLess(len(text.encode("utf-8")), 15_000)
                self.assertIn("## 担当タクソノミー分類", text)
                self.assertIn("## 入力として受け取るセクション", text)
                self.assertIn("## findingの出力スキーマ", text)
                self.assertNotIn("行末に半角スペースをちょうど2個", text)

    def test_three_party_inputs_are_separated_by_the_orchestrator(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run_word.py", "--dry-run", "obvious"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        stages = {item["name"]: item for item in json.loads(completed.stdout)["stages"]}
        self.assertEqual(stages["cold_review"]["input_scope"], ["entry body without front matter"])
        self.assertEqual(stages["final_blind"]["input_scope"], ["latest entry body only"])
        self.assertEqual(
            stages["final_review"]["input_scope"],
            [
                "latest entry body",
                "sealed final-blind output",
                "all checker and cold findings",
                "finding resolution records",
            ],
        )
        self.assertEqual(stages["cold_review"]["context_mode"], "context_free_cold")
        self.assertEqual(stages["final_blind"]["context_mode"], "context_free_final_blind")
        self.assertEqual(
            stages["final_review"]["context_mode"], "final_reconciliation_context"
        )
        for stage in (stages["cold_review"], stages["final_blind"]):
            self.assertNotIn("ACTIVE.md", json.dumps(stage))
            self.assertNotIn("findings", json.dumps(stage))

    def test_final_v2_preserves_the_semantic_pass_fail_boundary(self) -> None:
        text = (REPO_ROOT / "prompts" / "final_review_spec_v2.md").read_text(
            encoding="utf-8"
        )
        self.assertLess(len(text.encode("utf-8")), 8_000)
        for marker in (
            "事実、語法、発音、例文、訳",
            "主要な品詞、語義、派生・転換、専門用法、完全な統語フレーム",
            "語義境界、コアイメージ、定義、語法、コロケーション、語彙関係",
            "反例・矛盾・適用範囲",
            "すべてのfinding",
            "semantic_assertion",
            "条件付き合格は使わない",
            "非blocking note",
            "`REJECT` は審査失敗ではなく",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertIn("scripts/generate_audit_manifest.py", text)
        self.assertNotIn("entry_workflow_guard.py start", text)
        self.assertNotIn("start-cycle", text)
        self.assertNotIn("add-revision", text)

    def test_final_blind_prompt_has_no_reconciliation_identifiers(self) -> None:
        text = (REPO_ROOT / "prompts" / "final_blind_prompt_v2.md").read_text(
            encoding="utf-8"
        )
        self.assertLess(len(text.encode("utf-8")), 5_000)
        self.assertIn("semantic_assertions", text)
        self.assertIn("article_findings", text)
        self.assertIn("ACTIVE.md", text)
        self.assertIn("渡さない", text)
        self.assertIn("本文側target ID", text)

    def test_agents_is_a_small_router_for_the_orchestrator(self) -> None:
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertLess(len(text.encode("utf-8")), 6_000)
        for marker in (
            "python scripts/run_word.py --dry-run <headword>",
            "prompts/entry_spec_v5.md",
            "prompts/check_router_v6.md",
            "prompts/check_pass_*_v6.md",
            "prompts/final_blind_prompt_v2.md",
            "prompts/final_review_spec_v2.md",
            "prompts/notion_spec_v1.md",
        ):
            self.assertIn(marker, text)
        for removed_procedure in (
            "record-research",
            "confirm-remote",
            "最大2回",
            "Pull Requestの機械検証が成功したら",
        ):
            self.assertNotIn(removed_procedure, text)

    def test_readme_routes_instead_of_repeating_the_old_process_specs(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("OpenAI APIキーは不要", text)
        self.assertIn("scripts/run_word.py --dry-run", text)
        self.assertIn("content_audit_v4", text)
        self.assertIn("scripts/generate_audit_manifest.py", text)
        self.assertNotIn("prompts/check_spec_v5.md だけを全文", text)
        self.assertNotIn("scripts/content_audit.py start-cycle", text)

    def test_github_flow_uses_codex_not_an_api_generator(self) -> None:
        validate_workflow = (
            REPO_ROOT / ".github" / "workflows" / "validate.yml"
        ).read_text(encoding="utf-8")
        notion_workflow = (
            REPO_ROOT / ".github" / "workflows" / "sync-notion.yml"
        ).read_text(encoding="utf-8")
        orchestrator = (REPO_ROOT / "scripts" / "run_word.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("openai", orchestrator.lower())
        self.assertIn("independent_llm", orchestrator)
        self.assertIn("pull_request:", validate_workflow)
        self.assertIn("scripts/validate_repository.py", validate_workflow)
        self.assertIn("scripts/content_audit.py validate-changed", validate_workflow)
        self.assertIn("scripts/content_audit.py validate-sync", notion_workflow)
        self.assertFalse((REPO_ROOT / "scripts" / "generate_entry.py").exists())


if __name__ == "__main__":
    unittest.main()
