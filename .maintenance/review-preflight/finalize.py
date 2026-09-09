"""Final exact-source-checked boundary fixes; removed before the PR is merged."""
from pathlib import Path
import subprocess


def checked(path, sha):
    if subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip() != sha:
        raise SystemExit('unexpected finalization source: ' + str(path))
    return path.read_text(encoding='utf-8')


def replace(text, old, new):
    if text.count(old) != 1:
        raise SystemExit(f'expected one finalization anchor ({text.count(old)}): {old[:120]}')
    return text.replace(old, new, 1)


path = Path('scripts/review_validation.py')
s = checked(path, '7310f66f87e7995695c97ecbd1483e9c9977f13c')
s = replace(s, 'if row.get("disposition") not in {"adopted", "rejected"}:',
            'if row.get("disposition") not in ("adopted", "rejected"):')
s = replace(s, '''        if not isinstance(output, dict) or output.get("pass_id") not in expected_passes:
''', '''        if (not isinstance(output, dict) or not isinstance(output.get("pass_id"), str)
                or output["pass_id"] not in expected_passes):
''')
path.write_text(s, encoding='utf-8')

path = Path('scripts/run_word_v3.py')
s = checked(path, 'ff4c537c6450ea0debd891756be5beed5edfece5')
s = replace(s, '''        guard.clear_review_ingest_failures(manifest)
    next_request = next_stage_request(manifest)
''', '''        guard.clear_review_ingest_failures(manifest)
        review_recovery.resolve_validation_failure(manifest, stage=str(stage_name))
        manifest.pop("last_rejected_review", None)
        guard._write(resolved, manifest)
    next_request = next_stage_request(manifest)
''')
path.write_text(s, encoding='utf-8')

path = Path('tests/test_review_preflight_recovery.py')
s = checked(path, '3a3003abbbf2e94827926098551645561639b56f')
s = replace(s, 'import sys\n', 'import sys\nimport subprocess\nimport tarfile\n')
s = replace(s, '''        shutil.copytree(ROOT / "prompts", self.root / "prompts")
        original = sorted(p for p in (ROOT / "audits/runs/e/evident").iterdir()
                          if p.is_dir() and (p / "final_review.json").is_file())[-1]
        self.cycle = self.root / original.relative_to(ROOT)
        shutil.copytree(original, self.cycle)
        self.entry = self.root / "entries/e/evident.md"
        self.entry.parent.mkdir(parents=True)
        shutil.copy2(ROOT / "entries/e/evident.md", self.entry)
''', '''        # Freeze the incident bundle; future dictionary edits must not silently
        # change these regression inputs or create new dependencies on current text.
        data = subprocess.check_output([
            "git", "-C", str(ROOT), "archive",
            "ced03833849db093d0a9581dd7be7277d9f32869",
            "prompts", "entries/e/evident.md", "audits/runs/e/evident",
        ])
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            archive.extractall(self.root, filter="data")
        self.cycle = sorted(p for p in (self.root / "audits/runs/e/evident").iterdir()
                            if p.is_dir() and (p / "final_review.json").is_file())[-1]
        self.entry = self.root / "entries/e/evident.md"
''')
anchor = '    def test_template_keeps_every_decision_unjudged(self):\n'
s = replace(s, anchor, '''    def test_malformed_enum_and_pass_id_do_not_abort_aggregate_report(self):
        normal_path = self.cycle / "pass_findings.json"
        normal = read(normal_path)
        normal["pass_outputs"][0]["pass_id"] = []
        write(normal_path, normal)
        resolution_path = self.cycle / "resolutions.json"
        resolutions = read(resolution_path)
        resolutions["resolutions"][0]["disposition"] = []
        write(resolution_path, resolutions)
        source_path = self.cycle / "source_inventory.json"
        source = read(source_path)
        source["input_body_sha256"] = "stale"
        write(source_path, source)
        report = self.report()
        self.assertFalse(report["valid"])
        self.assertTrue(any(e["path"] == "pass_outputs[0].pass_id" for e in report["errors"]))
        self.assertTrue(any(e["code"] == "resolution_disposition" for e in report["errors"]))
        self.assertTrue(any(e["path"] == "source_inventory.input_body_sha256" for e in report["errors"]))

''' + anchor)
anchor = '    def test_validation_rehearsal_does_not_write_into_real_run(self):\n'
s = replace(s, anchor, '''    def test_corrected_api_call_resolves_correction_and_retains_history(self):
        error = review_validation.PreflightError({"valid": False, "errors": [{"message": "stale source"}], "blocked_checks": []})
        with mock.patch.object(runner, "execute_api_review_stage", side_effect=error):
            self.assertEqual(runner._resume(self.path, call_review=True), 1)
        with mock.patch.object(runner, "execute_api_review_stage", return_value=[self.cycle / "final_review.json"]) as call:
            self.assertEqual(runner._resume(self.path, call_review=True), 0)
        call.assert_called_once()
        saved = read(self.path)
        self.assertEqual(saved["review_correction"]["status"], "resolved")
        self.assertEqual(saved["review_preflight_failures"]["count"], 1)
        self.assertEqual(saved["run_id"], self.manifest["run_id"])
        self.assertEqual(saved["started_at"], self.manifest["started_at"])
        self.assertNotIn("review_ingest_failures", saved)

''' + anchor)
path.write_text(s, encoding='utf-8')
print('Applied final boundary checks and fixed incident regression inputs.')
