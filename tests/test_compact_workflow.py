from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import compact_workflow as flow
from tests.test_content_audit import ENTRY_TEXT


class CompactWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "prompts").mkdir()
        shutil.copy2(ROOT / "prompts/compact_review_contract_v1.json",
                     self.root / "prompts/compact_review_contract_v1.json")
        self.entry = self.root / "entries/s/sample.md"
        self.entry.parent.mkdir(parents=True)
        self.entry.write_text(ENTRY_TEXT, encoding="utf-8")
        self.inventory = self.root / "source_inventory.json"
        self.inventory.write_text(json.dumps({"source_first_audit": {
            "sources": [
                {"source_type": "learner_dictionary", "locator": "https://example.com/one", "independence_group": "one", "facts": []},
                {"source_type": "general_dictionary", "locator": "https://example.com/two", "independence_group": "two", "facts": []}],
            "source_union": [], "claim_units": []}}), encoding="utf-8")
        self.manifest = {"workflow_contract_version": flow.VERSION, "run_id": "run-1",
                         "entry_path": "entries/s/sample.md", "inventory_path": "source_inventory.json",
                         "review_receipts": [], "resolutions": [], "migration": None}
        self.run = self.root / "audits/workflow_runs/sample/run-1.json"
        flow._save(self.run, self.manifest)

    def test_two_independent_reviews_are_required_and_stale_body_blocks(self):
        areas = list(flow.current(self.manifest, self.root)["areas"])
        for role in ("A", "B"):
            request = flow.prepare(self.manifest, self.run, role, root=self.root)
            raw = request.parent / f"{role}.response.raw.json"
            flow._save(raw, {"schema_version": "compact_review_response_v1",
                             "checked_areas": areas, "unchecked_areas": [], "findings": []})
            flow.ingest(self.manifest, self.run, role, request, raw,
                        execution_id=f"agent-{role}", model="review-model", root=self.root)
            if role == "A":
                self.assertEqual(flow.status(self.manifest, root=self.root)["publish_gate"], "blocked")
        self.assertEqual(flow.status(self.manifest, root=self.root)["publish_gate"], "pass")
        self.entry.write_text(ENTRY_TEXT.replace("私たちはその材料の試料を調べた。", "私たちは材料の試料を調べた。"), encoding="utf-8")
        status = flow.status(self.manifest, root=self.root)
        self.assertEqual(status["publish_gate"], "blocked")
        self.assertTrue(status["uncovered"]["A"])
        self.assertNotIn("pronunciation", status["uncovered"]["A"])

    def test_missing_scope_and_raw_tampering_fail_closed(self):
        request = flow.prepare(self.manifest, self.run, "A", root=self.root)
        raw = request.parent / "A.response.raw.json"
        flow._save(raw, {"schema_version": "compact_review_response_v1",
                         "checked_areas": [], "unchecked_areas": [], "findings": []})
        with self.assertRaisesRegex(ValueError, "scope"):
            flow.ingest(self.manifest, self.run, "A", request, raw,
                        execution_id="agent-A", model="model", root=self.root)
        flow._save(raw, {"schema_version": "compact_review_response_v1",
                         "checked_areas": list(flow.current(self.manifest, self.root)["areas"]),
                         "unchecked_areas": [], "issues": []})
        receipt = flow.ingest(self.manifest, self.run, "A", request, raw,
                              execution_id="agent-A", model="model", root=self.root)
        self.assertEqual(receipt["normalizations"], ["issues->findings"])
        raw.write_text(raw.read_text() + " ", encoding="utf-8")
        self.assertTrue(flow.status(self.manifest, root=self.root)["uncovered"]["A"])


if __name__ == "__main__":
    unittest.main()
