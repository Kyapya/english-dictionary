from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from process_improvement import (  # noqa: E402
    _load_records,
    _validate_record,
    render_active,
    validate_registry,
)


class ProcessImprovementTests(unittest.TestCase):
    def setUp(self) -> None:
        records, errors = _load_records(REPO_ROOT)
        self.assertEqual(errors, [])
        self.base = copy.deepcopy(records[0])
        self.base.pop("_path", None)

    def _write_repo(self, records: list[dict]) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        records_dir = root / "process_improvement" / "records"
        records_dir.mkdir(parents=True)
        (root / "AGENTS.md").write_text("test", encoding="utf-8")
        (root / "audits").mkdir()
        (root / "audits" / "README.md").write_text("test", encoding="utf-8")
        (root / "scripts").mkdir()
        (root / "scripts" / "content_audit.py").write_text("test", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests" / "test_content_audit.py").write_text("test", encoding="utf-8")
        for record in records:
            path = records_dir / f"{record['id']}.json"
            path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        loaded, errors = _load_records(root)
        self.assertEqual(errors, [])
        (root / "process_improvement" / "ACTIVE.md").write_text(
            render_active(loaded), encoding="utf-8"
        )
        return root

    def test_repository_registry_and_generated_playbook_are_valid(self) -> None:
        self.assertEqual(validate_registry(REPO_ROOT), [])

    def test_standard_flow_loads_lessons_and_keeps_blind_roles_isolated(self) -> None:
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        workflow = (REPO_ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        for text in (agents, readme):
            self.assertIn("process_improvement/ACTIVE.md", text)
            self.assertIn("scripts/process_improvement.py", text)
            self.assertIn("コールドレビュー", text)
            self.assertIn("最終盲検", text)
        self.assertIn("単語固有", readme)
        self.assertIn("新しい知見なし", readme)
        orchestrator = (REPO_ROOT / "scripts" / "run_word.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("process_improvement/ACTIVE.md", orchestrator)
        self.assertIn("context_free_cold", orchestrator)
        self.assertIn("context_free_final_blind", orchestrator)
        self.assertIn('"process_improvement/**"', workflow)
        self.assertIn("scripts/process_improvement.py validate", workflow)

    def test_memo_like_record_without_generalization_basis_is_rejected(self) -> None:
        record = copy.deepcopy(self.base)
        record["generalization_gate"]["repeated_across_runs"] = False
        record["generalization_gate"]["high_impact_single_run"] = False
        record["_path"] = REPO_ROOT / "process_improvement" / "records" / "PI-0001.json"
        errors = _validate_record(record, REPO_ROOT)
        self.assertTrue(any("reject memo-like records" in error for error in errors))

    def test_repeated_problem_requires_two_distinct_sources(self) -> None:
        record = copy.deepcopy(self.base)
        record["evidence"] = [record["evidence"][0]]
        record["_path"] = REPO_ROOT / "process_improvement" / "records" / "PI-0001.json"
        errors = _validate_record(record, REPO_ROOT)
        self.assertTrue(any("two distinct evidence sources" in error for error in errors))

    def test_active_rule_requires_completed_validation(self) -> None:
        record = copy.deepcopy(self.base)
        record["validation"]["result"] = "pending"
        record["_path"] = REPO_ROOT / "process_improvement" / "records" / "PI-0001.json"
        errors = _validate_record(record, REPO_ROOT)
        self.assertTrue(any("active status requires" in error for error in errors))

    def test_candidates_and_rules_enforced_elsewhere_do_not_bloat_playbook(self) -> None:
        candidate = copy.deepcopy(self.base)
        candidate["id"] = "PI-0003"
        candidate["title"] = "候補規則"
        candidate["status"] = "candidate"
        candidate["action_rule"] = "候補段階では次回実行へ強制しない。"
        candidate["validation"]["result"] = "not_started"
        candidate["enforcement"]["surface_in_playbook"] = True
        candidate["enforcement"]["mode"] = "coordinator_playbook"
        rendered = render_active([self.base, candidate])
        self.assertNotIn("PI-0001", rendered)
        self.assertNotIn("PI-0003", rendered)

    def test_quality_rule_cannot_become_a_hidden_playbook_spec(self) -> None:
        record = copy.deepcopy(self.base)
        record["category"] = "quality"
        record["enforcement"] = {
            "mode": "coordinator_playbook",
            "surface_in_playbook": True,
            "refs": ["AGENTS.md"],
        }
        record["_path"] = REPO_ROOT / "process_improvement" / "records" / "PI-0001.json"
        errors = _validate_record(record, REPO_ROOT)
        self.assertTrue(any("hidden content spec" in error for error in errors))
        self.assertTrue(any("canonical spec/script" in error for error in errors))

    def test_duplicate_action_rules_are_rejected(self) -> None:
        other = copy.deepcopy(self.base)
        other["id"] = "PI-0003"
        other["title"] = "別名の重複規則"
        root = self._write_repo([self.base, other])
        errors = validate_registry(root)
        self.assertTrue(any("duplicate process-improvement action rule" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
