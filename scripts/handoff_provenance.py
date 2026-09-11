"""Bind handoff decisions to preserved responses, without claiming identity attestation.

A digest proves byte integrity, not that a human or independent agent really ran.
The dispatcher must preserve the actual external response; never synthesize one.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PROTOCOL = "preserved_handoff_v1"
DECISIONS = {
    "decision", "provisional_decision", "findings", "article_findings",
    "independent_candidates", "target_results", "relation_results",
    "candidate_results", "finding_results", "evidence_checks",
    "source_inventory_results", "attributions",
    "axes", "adjudications", "frame_findings", "unrouted_observations",
    "input_body_sha256", "input_revision_id", "prompt_sha256",
}


def bind(path: Path, repo_root: Path) -> dict:
    relative = path.resolve().relative_to(repo_root.resolve()).as_posix()
    if not relative.startswith("audits/runs/"):
        raise ValueError("source response must be under audits/runs/")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    # Canonical response paths can be replaced on a later recheck. Preserve the
    # original bytes under a content-addressed path before recording a binding.
    preserved = path.parent / "source_responses" / (digest + ".json")
    preserved.parent.mkdir(parents=True, exist_ok=True)
    if preserved.exists():
        if preserved.read_bytes() != raw:
            raise ValueError("immutable response snapshot differs")
    else:
        with preserved.open("xb") as stream:
            stream.write(raw)
    return {
        "path": preserved.resolve().relative_to(repo_root.resolve()).as_posix(),
        "sha256": digest,
    }


def validate(output: dict, repo_root: Path, *, required: bool = False) -> list[str]:
    reviewer = output.get("reviewer", {})
    if not isinstance(reviewer, dict) or reviewer.get("mode") != "handoff":
        return []
    binding = reviewer.get("source_response")
    if binding is None and not required:
        return []
    if not isinstance(binding, dict):
        return ["handoff requires a preserved source_response; agent_id alone is not proof"]
    try:
        relative = binding["path"]
        if not isinstance(relative, str):
            raise ValueError("source response path must be a string")
        path = (repo_root / relative).resolve()
        if not isinstance(relative, str) or not relative.startswith("audits/runs/"):
            raise ValueError("source response must be under audits/runs/")
        path.relative_to(repo_root.resolve())
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != binding.get("sha256"):
            raise ValueError("source response digest mismatch")
        source = json.loads(raw)
        if not isinstance(source, dict):
            raise ValueError("source response must be an object")
        if reviewer.get("ingested_by") != "orchestrator" and required:
            raise ValueError("automated handoff ingestion must be labelled orchestrator")
        source_reviewer = source.get("reviewer", {})
        if source_reviewer and (
            not isinstance(source_reviewer, dict)
            or source_reviewer.get("agent_id") != reviewer.get("agent_id")
        ):
            raise ValueError("source response reviewer differs from ingested reviewer")
        fields = DECISIONS.intersection(source)
        if not fields and not any(key in source for key in ("antonym_axis_blind_record", "adjudications", "blind_attribution_record")):
            raise ValueError("source response has no review decisions")
        mismatches = sorted(key for key in fields if output.get(key) != source[key])
        if mismatches:
            raise ValueError("review decisions differ from preserved response: " + ", ".join(mismatches))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [str(exc)]
    return []


def validate_checker(output: dict, root: Path, *, required: bool = False) -> list[str]:
    if output.get("pass_id") == "example-attribution":
        records = [output.get("blind_attribution_record", {})]
    elif output.get("pass_id") == "frame-relation":
        records = [output.get("antonym_axis_blind_record", {}),
                   output.get("antonym_axis_adjudication_record", {})]
    else:
        records = [output]
    errors = []
    for record in records:
        if not record and required:
            errors.append("checker source record is missing")
        else:
            errors.extend(validate(record, root, required=required))
    return errors


def required_for_cycle(cycle: Path, root: Path) -> bool:
    path = root / "audits/workflow_runs" / cycle.parent.name / (cycle.name + ".json")
    if not path.exists():
        return False
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return manifest.get("orchestrator", {}).get("review_provenance_protocol") == PROTOCOL
