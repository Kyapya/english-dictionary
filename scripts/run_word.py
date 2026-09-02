from __future__ import annotations

"""Compatibility entrypoint for the parallel checker orchestrator.

The stable v3 implementation is retained in ``run_word_v3.py`` and the checker
parallelization lives in ``run_word_parallel.py``. This thin module preserves
legacy source-contract markers and dynamic monkey-patch behavior used by the
regression suite while routing runtime hooks to the parallel implementation.

Checker passes use parallel subagents: one isolated subagent/context per pass.
The same model may be reused by multiple subagents; handoff independence is
proved by distinct ``reviewer.agent_id`` values, not by distinct model names.
Legacy aggregate checker handoff ingestion is deliberately rejected so a run
cannot bypass the seven-subagent fan-out/fan-in contract.

Preserved contracts: independent_llm, process_improvement/ACTIVE.md,
context_free_cold, context_free_final_blind, confirm_remote_checkpoint,
heartbeat_manifest, entry_workflow_guard, source_inventory_complete.
"""

from pathlib import Path
from typing import Any

import run_word_parallel as _parallel


for _name, _value in vars(_parallel).items():
    if _name not in {
        "__name__",
        "__file__",
        "__package__",
        "__loader__",
        "__spec__",
        "__builtins__",
        "__cached__",
    }:
        globals()[_name] = _value


CHECKER_SUBAGENT_PROTOCOL_VERSION = "parallel_subagents_v2"

# Keep the original implementations before installing dispatchers.
_prepare_handoff_impl = _parallel.prepare_handoff
_ingest_handoff_review_impl = _parallel.ingest_handoff_review
_execute_api_review_stage_impl = _parallel.execute_api_review_stage
_execute_checker_bundle_api_impl = _parallel._execute_checker_bundle_api
_plan_payload_impl = _parallel.plan_payload


def _subagent_plan_payload(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _plan_payload_impl(*args, **kwargs)
    checker_passes = value.get("checker_passes")
    value["checker_execution_protocol"] = CHECKER_SUBAGENT_PROTOCOL_VERSION
    value["checker_subagent_count"] = (
        len(checker_passes) if isinstance(checker_passes, list) else 0
    )
    return value


def _rewrite_checker_handoff_terminology(index_path: Path) -> None:
    """Use the user-facing term subagent without changing stable JSON field names."""

    candidates = {index_path}
    if index_path.parent.is_dir():
        candidates.update(index_path.parent.glob("checker_passes*.request.md"))
    replacements = (
        ("independent agent/session", "independent subagent/session"),
        ("one independent agent per pass", "one independent subagent per pass"),
        ("reuse one agent for multiple passes", "reuse one subagent for multiple passes"),
        ("Keep this exact agent available", "Keep this exact subagent available"),
        ("the same agent reviewer.agent_id", "the same subagent reviewer.agent_id"),
        ("go back to that same agent", "go back to that same subagent"),
        ("while the agents are running", "while the subagents are running"),
        ("seven parallel handoff agents", "seven parallel handoff subagents"),
    )
    for path in candidates:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        revised = text
        for old, new in replacements:
            revised = revised.replace(old, new)
        if revised != text:
            path.write_text(revised, encoding="utf-8")


def _strict_prepare_handoff(*args: Any, **kwargs: Any) -> Any:
    path = _prepare_handoff_impl(*args, **kwargs)
    if isinstance(path, Path):
        _rewrite_checker_handoff_terminology(path)
    return path


def _strict_checker_handoff_ready(
    manifest: dict[str, Any], *, repo_root: Path
) -> None:
    request = _parallel._v3.next_stage_request(manifest)
    if request is None or request.get("name") != "checker_passes":
        return
    if request.get("reviewer_mode") != "handoff":
        return

    _, cycle_dir = _parallel._checker_cycle(manifest, repo_root=repo_root)
    check_dir = cycle_dir / "check_passes"
    checkpoint = check_dir / "checker_passes.stage1.json"

    if checkpoint.is_file():
        stage2_response = _parallel._parallel_frame_stage2_response_path(cycle_dir)
        if not stage2_response.is_file():
            raise ValueError(
                "checker subagent handoff requires the canonical frame-relation "
                "stage-2 response from the same subagent; legacy aggregate stage-2 "
                "handoff is not accepted"
            )
        return

    entry = repo_root / str(manifest["entry_path"])
    front, _ = _parallel._v3.validate_entry._split_front_matter(
        entry.read_text(encoding="utf-8")
    )
    generation_model = _parallel._v3.validate_entry._front_matter_values(
        front or []
    ).get("model", "")
    router = _parallel._v3.check_passes.load_router(repo_root / DEFAULT_CHECK_SPEC)
    pass_ids = _parallel._checker_pass_ids(router)
    responses = _parallel._load_parallel_checker_responses(
        cycle_dir,
        pass_ids,
        generation_model=generation_model,
    )
    if responses is None:
        raise ValueError(
            "checker handoff requires one response from each parallel subagent; "
            "legacy aggregate checker handoff is not accepted"
        )


def _strict_ingest_handoff_review(*args: Any, **kwargs: Any) -> Any:
    manifest = args[0] if args else kwargs.get("manifest")
    stage = kwargs.get("stage")
    repo_root = kwargs.get("repo_root", REPO_ROOT)
    if isinstance(manifest, dict) and stage == "checker_passes":
        _strict_checker_handoff_ready(manifest, repo_root=repo_root)
    return _ingest_handoff_review_impl(*args, **kwargs)


def _dispatch_prepare_handoff(*args: Any, **kwargs: Any) -> Any:
    return globals()["prepare_handoff"](*args, **kwargs)


def _dispatch_ingest_handoff_review(*args: Any, **kwargs: Any) -> Any:
    return globals()["ingest_handoff_review"](*args, **kwargs)


def _dispatch_execute_api_review_stage(*args: Any, **kwargs: Any) -> Any:
    return globals()["execute_api_review_stage"](*args, **kwargs)


def _dispatch_execute_checker_bundle_api(*args: Any, **kwargs: Any) -> Any:
    return globals()["_execute_checker_bundle_api"](*args, **kwargs)


def _dispatch_plan_payload(*args: Any, **kwargs: Any) -> Any:
    return globals()["plan_payload"](*args, **kwargs)


# Public hooks. Internal cross-module calls use dispatchers so unittest.mock
# patches against ``run_word.<hook>`` continue to work.
prepare_handoff = _strict_prepare_handoff
ingest_handoff_review = _strict_ingest_handoff_review
execute_api_review_stage = _execute_api_review_stage_impl
_execute_checker_bundle_api = _execute_checker_bundle_api_impl
plan_payload = _subagent_plan_payload

_parallel.prepare_handoff = _dispatch_prepare_handoff
_parallel.ingest_handoff_review = _dispatch_ingest_handoff_review
_parallel.execute_api_review_stage = _dispatch_execute_api_review_stage
_parallel._execute_checker_bundle_api = _dispatch_execute_checker_bundle_api
_parallel.plan_payload = _dispatch_plan_payload
_parallel._v3.prepare_handoff = _dispatch_prepare_handoff
_parallel._v3.ingest_handoff_review = _dispatch_ingest_handoff_review
_parallel._v3.execute_api_review_stage = _dispatch_execute_api_review_stage
_parallel._v3.plan_payload = _dispatch_plan_payload


if __name__ == "__main__":
    raise SystemExit(_parallel._v3.main())
