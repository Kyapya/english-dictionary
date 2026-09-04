from __future__ import annotations

"""Mechanical provenance gate for parallel checker subagents.

This gate adds no LLM review work. It only verifies that workflow runs created
under the parallel-subagent protocol actually preserve the seven-pass contract.
Model reuse is allowed; handoff subagents must have distinct ``reviewer.agent_id``
values so independent contexts cannot be represented as one reused subagent.
"""

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = REPO_ROOT / "audits" / "workflow_runs"
PROTOCOL_VERSION = "parallel_subagents_v2"


def _normalize(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _load_object(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}: cannot read JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: JSON root must be an object")
        return None
    return value


def _checker_output_path(
    manifest: dict[str, Any], *, repo_root: Path
) -> Path | None:
    orchestrator = manifest.get("orchestrator")
    if not isinstance(orchestrator, dict):
        return None
    run_id = str(manifest.get("run_id", "")).strip()
    for stage in orchestrator.get("stages", []):
        if not isinstance(stage, dict) or stage.get("name") != "checker_passes":
            continue
        for raw in stage.get("output_paths", []):
            text = str(raw)
            if text.endswith("/pass_findings.json"):
                return repo_root / text.replace("{run_id}", run_id)
    return None


def validate_manifest_subagents(
    manifest: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    merge_ready: bool = False,
) -> list[str]:
    errors: list[str] = []
    orchestrator = manifest.get("orchestrator")
    if not isinstance(orchestrator, dict):
        return errors
    if orchestrator.get("checker_execution_protocol") != PROTOCOL_VERSION:
        return errors

    # The provenance contract is a merge-time check for completed handoff
    # runs.  Abandoned or budget-exhausted runs are retained as history and
    # are validated by the changed-run workflow guard when they are edited;
    # they must not block an unrelated completed run in repository-wide CI.
    if merge_ready and manifest.get("status") != "completed":
        return errors

    label = str(manifest.get("run_id", "<unknown-run>"))
    expected = [
        str(item.get("id", "")).strip()
        for item in orchestrator.get("checker_passes", [])
        if isinstance(item, dict)
    ]
    if not expected or any(not value for value in expected):
        errors.append(f"{label}: subagent protocol requires routed checker pass ids")
        return errors
    if len(expected) != len(set(expected)):
        errors.append(f"{label}: routed checker pass ids must be unique")

    declared_count = orchestrator.get("checker_subagent_count")
    if declared_count != len(expected):
        errors.append(
            f"{label}: checker_subagent_count must equal routed pass count {len(expected)}"
        )

    target = _checker_output_path(manifest, repo_root=repo_root)
    if target is None:
        errors.append(f"{label}: checker pass_findings.json path is missing from plan")
        return errors
    if not target.is_file():
        errors.append(f"{label}: checker output is missing: {target.relative_to(repo_root)}")
        return errors

    aggregate = _load_object(target, f"{label}: checker output", errors)
    if aggregate is None:
        return errors
    outputs = aggregate.get("pass_outputs")
    if not isinstance(outputs, list):
        errors.append(f"{label}: checker output pass_outputs must be a list")
        return errors

    actual = [
        str(item.get("pass_id", "")).strip()
        for item in outputs
        if isinstance(item, dict)
    ]
    if len(actual) != len(outputs) or actual != expected:
        errors.append(
            f"{label}: checker outputs must cover routed passes exactly once and in plan order"
        )
        return errors

    reviewer_mode = str(orchestrator.get("reviewer_mode", "")).strip()
    if reviewer_mode != "handoff":
        # API mode already executes one isolated request per worker. The handoff
        # provenance rule below applies where external subagent identity is recorded.
        return errors

    agent_ids: set[str] = set()
    for index, item in enumerate(outputs):
        assert isinstance(item, dict)
        pass_id = expected[index]
        reviewer = item.get("reviewer")
        if not isinstance(reviewer, dict):
            errors.append(f"{label}: {pass_id} reviewer metadata is required")
            continue
        if reviewer.get("mode") != "handoff":
            errors.append(f"{label}: {pass_id} reviewer.mode must be handoff")
        declared_model = str(reviewer.get("declared_model", "")).strip()
        if not declared_model:
            errors.append(f"{label}: {pass_id} reviewer.declared_model is required")
        agent_id = str(reviewer.get("agent_id", "")).strip()
        if not agent_id:
            errors.append(f"{label}: {pass_id} reviewer.agent_id is required")
            continue
        normalized = _normalize(agent_id)
        if normalized in agent_ids:
            errors.append(
                f"{label}: checker subagents must use unique reviewer.agent_id values; "
                f"duplicate {agent_id!r}"
            )
        agent_ids.add(normalized)

    reviewers = aggregate.get("checker_reviewers")
    if reviewers is not None:
        if not isinstance(reviewers, dict):
            errors.append(f"{label}: checker_reviewers must be an object when present")
        else:
            for item in outputs:
                if not isinstance(item, dict):
                    continue
                pass_id = str(item.get("pass_id", ""))
                recorded = reviewers.get(pass_id)
                output_reviewer = item.get("reviewer")
                if not isinstance(recorded, dict) or not isinstance(output_reviewer, dict):
                    errors.append(f"{label}: checker_reviewers.{pass_id} is missing")
                    continue
                if _normalize(recorded.get("agent_id")) != _normalize(
                    output_reviewer.get("agent_id")
                ):
                    errors.append(
                        f"{label}: checker_reviewers.{pass_id}.agent_id must match pass output"
                    )
                if _normalize(recorded.get("declared_model")) != _normalize(
                    output_reviewer.get("declared_model")
                ):
                    errors.append(
                        f"{label}: checker_reviewers.{pass_id}.declared_model must match pass output"
                    )
    return errors


def validate_all(
    *, repo_root: Path = REPO_ROOT, merge_ready: bool = False
) -> list[str]:
    errors: list[str] = []
    runs_root = repo_root / "audits" / "workflow_runs"
    if not runs_root.exists():
        return errors
    for path in sorted(runs_root.rglob("*.json")):
        manifest = _load_object(path, str(path.relative_to(repo_root)), errors)
        if manifest is None:
            continue
        errors.extend(
            validate_manifest_subagents(
                manifest,
                repo_root=repo_root,
                merge_ready=merge_ready,
            )
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--merge-ready", action="store_true")
    args = parser.parse_args(argv)

    errors = validate_all(merge_ready=args.merge_ready)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("checker subagent provenance: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
