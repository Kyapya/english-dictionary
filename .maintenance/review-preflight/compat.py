"""Compatibility corrections verified against existing and evident regressions."""
from pathlib import Path
import subprocess


def replace(text, old, new):
    if text.count(old) != 1:
        raise SystemExit(f'expected one compatibility anchor ({text.count(old)}): {old[:100]}')
    return text.replace(old, new, 1)


def checked(path, sha):
    if subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip() != sha:
        raise SystemExit('unexpected compatibility source: ' + str(path))
    return path.read_text(encoding='utf-8')


path = Path('scripts/review_preflight.py')
s = checked(path, '7f7f095c23bda6934f77526c0ec7d669ddbbd1fe')
s = replace(s, 'for item in source["evidence_link_ids"]', 'for item in source.get("evidence_link_ids", [])')
path.write_text(s, encoding='utf-8')

path = Path('scripts/review_validation.py')
s = checked(path, 'e132279dd559406fe26f7b5e336cfe32e444b340')
s = replace(s, '        evidence = source.get("evidence_link_ids")', '''        # The v1 field is optional; explicit malformed values are still rejected.
        evidence = source.get("evidence_link_ids", [])''')
s = replace(s, 'evidence_link_ids must be an explicit list of unique non-empty IDs',
            'evidence_link_ids, when present, must be a list of unique non-empty IDs')
s = replace(s, '''            for rid, row in rows.items():
                collect(f"pass_outputs[{i}].findings.{rid}", lambda row=row, rid=rid: audit._validate_finding(row, rid))
''', '')
s = replace(s, '''    outputs = values.get("pass_findings", {}).get("pass_outputs")
''', '''    import check_passes
    router = check_passes.load_router(root / "prompts/check_router_v6.md")
    expected_passes = {row["id"] for row in router["passes"]}
    outputs = values.get("pass_findings", {}).get("pass_outputs")
''')
s = replace(s, '''        import check_passes
        router = check_passes.load_router(root / "prompts/check_router_v6.md")
        expected_passes = {row["id"] for row in router["passes"]}
''', '')
anchor = '    cold = collections.get("cold_review.findings")\n'
s = replace(s, anchor, '''    # Checker findings use the router's native taxonomy, not the article-finding
    # taxonomy. Reuse the same validator and provenance inputs as final audit.
    def optional(relative: str) -> dict | None:
        path = cycle / relative
        return load(path, relative) if path.is_file() else None

    attribution = optional("check_passes/example-attribution.request.json")
    attribution_key = optional("check_passes/example-attribution.alignment-key.json")
    antonym = optional("check_passes/frame-relation.request.json")
    antonym_stage2 = optional("check_passes/frame-relation.antonym-axis.stage2.request.json")
    antonym_key = optional("check_passes/frame-relation.antonym-axis.alignment-key.json")
    provenance = not audit._is_historical_cycle(cycle) or any(
        isinstance(values.get(name, {}).get("reviewer"), dict)
        for name in ("cold_review", "final_blind")
    ) or any(isinstance(row, dict) and isinstance(row.get("reviewer"), dict)
             for row in (outputs if isinstance(outputs, list) else []))
    generation_model = audit._entry_front_matter(entry).get("model")
    for i, output in enumerate(outputs if isinstance(outputs, list) else []):
        if not isinstance(output, dict) or output.get("pass_id") not in expected_passes:
            continue
        pid = output["pass_id"]
        request = optional("check_passes/" + pid + ".request.json")
        if pid == "frame-relation" and antonym_stage2 is not None:
            request = antonym_stage2
        collect(f"pass_outputs[{i}]", lambda output=output, request=request: check_passes.validate_pass_output(
            output, router, entry_path=entry, repo_root=root,
            example_request=attribution, alignment_key=attribution_key,
            antonym_request=antonym, antonym_stage2_request=antonym_stage2,
            antonym_alignment_key=antonym_key, request_payload=request,
            check_liveness=False, generation_model=generation_model,
            require_reviewer=provenance,
            require_antonym_axis=("antonym_axis_blind_record" in output
                                  or any(value is not None for value in (antonym, antonym_stage2, antonym_key))),
        ))
''' + anchor)
s = replace(s, '''            for pid, expected in request_hashes.items():
''', '''            original_ids = {p.name.removesuffix(".request.json")
                            for p in (cycle / "check_passes").glob("*.request.json")
                            if p.name.removesuffix(".request.json") in expected_passes}
            for pid in sorted(set(request_hashes) | original_ids):
                expected = request_hashes.get(pid)
''')
path.write_text(s, encoding='utf-8')

# This old test specified the behavior deliberately changed by priority 1:
# one dry-run rejection used to charge one actual ingestion failure. The new
# expectation preserves its original unchanged-replay assertion as well.
path = Path('tests/test_workflow_preflight.py')
s = checked(path, 'ae9e7c2520f8a45ddf4f6b610564c97cd8f595c3')
s = replace(s, '''        self.assertEqual(result["review_ingest_failures"]["count"], 1)
''', '''        self.assertNotIn("review_ingest_failures", result)
        self.assertEqual(result["review_preflight_failures"]["count"], 1)
''')
path.write_text(s, encoding='utf-8')

path = Path('tests/test_review_preflight_recovery.py')
s = checked(path, '93e00a0dc379d42778c31351a300690c8456da6a')
anchor = '    def test_template_keeps_every_decision_unjudged(self):\n'
s = replace(s, anchor, '''    def test_missing_original_snapshot_binding_is_reported(self):
        snapshot_path = self.cycle / "check_passes/input_snapshot.json"
        snapshot = read(snapshot_path)
        removed = next(iter(snapshot["request_hashes"]))
        del snapshot["request_hashes"][removed]
        write(snapshot_path, snapshot)
        report = self.report()
        self.assertFalse(report["valid"])
        self.assertTrue(any(e["code"] == "immutable_request_changed"
                            and e["path"] == removed + ".request.json" for e in report["errors"]))

    def test_explicit_bad_evidence_ids_are_not_treated_as_optional(self):
        source = read(self.cycle / "source_inventory.json")
        source["evidence_link_ids"] = None
        write(self.cycle / "source_inventory.json", source)
        report = self.report()
        self.assertFalse(report["valid"])
        self.assertTrue(any(e["code"] == "evidence_ids" for e in report["errors"]))

''' + anchor)
path.write_text(s, encoding='utf-8')
print('Applied native schema compatibility and regression updates.')
