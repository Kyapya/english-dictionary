from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SourceFirstContractWiringTests(unittest.TestCase):
    def test_active_process_rule_references_contract(self) -> None:
        active = (ROOT / "process_improvement" / "ACTIVE.md").read_text(encoding="utf-8")
        self.assertIn("prompts/source_first_audit_v2.md", active)
        self.assertIn("外部資料から先に候補", active)
        self.assertIn("claim-centric", active)
        self.assertIn("source union直接照合", active)
        self.assertIn("最大2回", active)

    def test_contract_contains_all_four_hardening_requirements(self) -> None:
        spec = (ROOT / "prompts" / "source_first_audit_v2.md").read_text(encoding="utf-8")
        self.assertIn("本文の分類を見る前", spec)
        self.assertIn("原子的fact", spec)
        self.assertIn("claim unit", spec)
        self.assertIn("全unionを直接確認", spec)

    def test_contract_is_bounded_and_has_safe_stop(self) -> None:
        spec = (ROOT / "prompts" / "source_first_audit_v2.md").read_text(encoding="utf-8")
        self.assertIn("standard | 6 | 48 | 2", spec)
        self.assertIn("extended | 8 | 80 | 3", spec)
        self.assertIn("budget_exhausted", spec)
        self.assertIn("同じ依頼内で新cycleを自動開始しない", spec)

    def test_prompts_remove_unbounded_retry_language(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        check = (ROOT / "prompts" / "check_spec_v5.md").read_text(encoding="utf-8")
        final = (ROOT / "prompts" / "final_review_spec_v1.md").read_text(encoding="utf-8")
        self.assertNotIn("問題がなくなるまで繰り返す", agents)
        self.assertNotIn("問題がなくなるまで繰り返す", check)
        self.assertIn("最大2回", final)
        self.assertIn("安全停止", final)

    def test_ci_runs_source_first_gate_for_changed_audits(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        self.assertIn("source_first_audit_gate.py validate-changed", workflow)

    def test_runtime_guard_is_wired_before_research_and_into_ci(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        orchestrator = (ROOT / "scripts" / "run_word.py").read_text(encoding="utf-8")
        entry = (ROOT / "prompts" / "entry_spec_v5.md").read_text(encoding="utf-8")
        check = (ROOT / "prompts" / "check_spec_v5.md").read_text(encoding="utf-8")
        final = (ROOT / "prompts" / "final_review_spec_v1.md").read_text(encoding="utf-8")
        source = (ROOT / "prompts" / "source_first_audit_v2.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/run_word.py", agents)
        self.assertNotIn("confirm-remote", agents)
        self.assertIn("confirm_remote_checkpoint", orchestrator)
        self.assertIn("heartbeat_manifest", orchestrator)
        self.assertIn("draft保存20分", entry)
        self.assertIn("entry_workflow_guard", check)
        self.assertIn("entry_workflow_guard", final)
        self.assertIn("record-research", source)
        self.assertIn("entry_workflow_guard.py validate-changed", workflow)


if __name__ == "__main__":
    unittest.main()
