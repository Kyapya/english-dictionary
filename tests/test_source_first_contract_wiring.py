from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SourceFirstContractWiringTests(unittest.TestCase):
    def test_active_process_rule_references_contract(self) -> None:
        active = (ROOT / "process_improvement" / "ACTIVE.md").read_text(encoding="utf-8")
        self.assertIn("prompts/source_first_audit_v1.md", active)
        self.assertIn("source-first inventory", active)
        self.assertIn("claim-centric", active)
        self.assertIn("source union直接照合", active)

    def test_contract_contains_all_four_hardening_requirements(self) -> None:
        spec = (ROOT / "prompts" / "source_first_audit_v1.md").read_text(encoding="utf-8")
        self.assertIn("source-first 語義・用法棚卸し", spec)
        self.assertIn("派生語・関連形の原子化", spec)
        self.assertIn("claim-centric 根拠台帳", spec)
        self.assertIn("最終審査での直接source比較", spec)

    def test_ci_runs_source_first_gate_for_changed_audits(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        self.assertIn("source_first_audit_gate.py validate-changed", workflow)


if __name__ == "__main__":
    unittest.main()
