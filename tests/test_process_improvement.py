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
    initial_retirement_state,
    render_active,
    retirement_review,
    validate_retirement_state,
    validate_registry,
)


class ProcessImprovementTests(unittest.TestCase):
    def setUp(self) -> None:
        records, errors = _load_records(REPO_ROOT)
        self.assertEqual(errors, [])
        self.base = copy.deepcopy(records[0])
        self.base.pop("_path", None)
        self.base["status"] = "active"
        self.base["validation"]["result"] = "pass"
        self.base["validation"]["observed_runs"] = self.base["validation"][
            "window_runs"
        ]

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
        (root / "prompts").mkdir()
        (root / "prompts" / "check_router_v6.md").write_bytes(
            (REPO_ROOT / "prompts" / "check_router_v6.md").read_bytes()
        )
        for record in records:
            path = records_dir / f"{record['id']}.json"
            path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        loaded, errors = _load_records(root)
        self.assertEqual(errors, [])
        (root / "process_improvement" / "ACTIVE.md").write_text(
            render_active(loaded), encoding="utf-8"
        )
        (root / "process_improvement" / "retirement_state.json").write_text(
            json.dumps(initial_retirement_state(root), ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
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

    def test_new_record_requires_registered_escaped_defect_ids(self) -> None:
        record = copy.deepcopy(self.base)
        record["created_at"] = "2026-08-27"
        record["updated_at"] = "2026-08-27"
        record["_path"] = REPO_ROOT / "process_improvement" / "records" / "PI-0001.json"
        errors = _validate_record(record, REPO_ROOT)
        self.assertTrue(any("escaped_defect_ids is required" in error for error in errors))

        record["escaped_defect_ids"] = ["not-registered"]
        errors = _validate_record(record, REPO_ROOT)
        self.assertTrue(any("unknown id not-registered" in error for error in errors))

        record["escaped_defect_ids"] = ["yield-D1"]
        errors = _validate_record(record, REPO_ROOT)
        self.assertFalse(any("escaped_defect" in error for error in errors))

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

    def _write_completed_cost_runs(self, root: Path, count: int) -> None:
        runs = root / "audits" / "workflow_runs"
        pass_ids = (
            "translation",
            "sense-structure",
            "frame-relation",
            "example-attribution",
            "qualification",
            "pronunciation",
            "evidence",
        )
        for index in range(count):
            path = runs / f"word-{index:02d}" / "run.json"
            path.parent.mkdir(parents=True)
            value = {
                "status": "completed",
                "entry_path": f"entries/w/word-{index:02d}.md",
                "metrics": {
                    "schema_version": "workflow_cost_v1",
                    "completed_at": f"2026-08-25T10:{index:02d}:00Z",
                    "checker_passes": [
                        {
                            "id": pass_id,
                            "instruction_bytes": 100,
                            "input_bytes": 900,
                            "duration_seconds": 2.0,
                            "defects_detected": 0 if pass_id == "translation" else 1,
                            "completed": True,
                        }
                        for pass_id in pass_ids
                    ],
                    "process_rules": [
                        {
                            "id": self.base["id"],
                            "instruction_bytes": 100,
                            "input_bytes": 0,
                            "duration_seconds": 1.0,
                            "defects_detected": 0,
                            "completed": True,
                        }
                    ],
                },
            }
            path.write_text(json.dumps(value), encoding="utf-8")

    def test_retirement_review_waits_for_ten_completed_words(self) -> None:
        root = self._write_repo([self.base])
        self._write_completed_cost_runs(root, 9)
        self.assertEqual(retirement_review(root, reviewed_at="2026-08-25"), [])
        state = json.loads(
            (root / "process_improvement" / "retirement_state.json").read_text()
        )
        self.assertTrue(all(unit["status"] == "active" for unit in state["units"]))

    def test_zero_yield_rule_and_pass_transition_to_retired_after_ten_words(self) -> None:
        root = self._write_repo([self.base])
        self._write_completed_cost_runs(root, 10)
        results = retirement_review(root, reviewed_at="2026-08-25")
        by_id = {item["id"]: item for item in results}
        self.assertEqual(by_id["check_pass:translation"]["decision"], "retire")
        self.assertEqual(by_id["check_pass:evidence"]["decision"], "retain")
        self.assertEqual(by_id[f"rule:{self.base['id']}"]["decision"], "retire")
        retired_record = json.loads(
            (
                root
                / "process_improvement"
                / "records"
                / f"{self.base['id']}.json"
            ).read_text()
        )
        self.assertEqual(retired_record["status"], "retired")
        self.assertEqual(retired_record["validation"]["result"], "fail")
        errors = validate_retirement_state(root)
        self.assertTrue(any("reassign its taxonomy" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
