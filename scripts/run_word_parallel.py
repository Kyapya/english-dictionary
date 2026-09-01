from __future__ import annotations

"""Parallel checker execution overlay for the v3 one-word orchestrator.

The v3 implementation remains intact in ``run_word_v3.py`` so existing workflow
manifests and CLI behavior stay compatible. The preserved stage plan continues to
mark cold/final reviewers as ``independent_llm``. This module overrides only checker
execution/handoff behavior:

* API mode runs the seven routed checker passes concurrently (max seven workers).
* handoff mode fans out one request per checker pass and mechanically fans in
  seven independently attributed responses.
* frame-relation keeps its masked stage 1 -> disclosed stage 2 dependency
  serial inside its own worker/agent.
"""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import run_word_v3 as _v3


for _name, _value in vars(_v3).items():
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


CHECKER_MAX_WORKERS = 7
PARALLEL_CHECKER_PROTOCOL_VERSION = "parallel_checker_v1"

_ORIGINAL_PREPARE_HANDOFF = _v3.prepare_handoff
_ORIGINAL_INGEST_HANDOFF_REVIEW = _v3.ingest_handoff_review
_ORIGINAL_EXECUTE_API_REVIEW_STAGE = _v3.execute_api_review_stage
_ORIGINAL_PREPARE_REVIEW_INPUTS = _v3.prepare_review_inputs


def _checker_cycle(
    manifest: dict[str, Any], *, repo_root: Path
) -> tuple[dict[str, Any], Path]:
    request = _v3.next_stage_request(manifest)
    if request is None or request.get("name") != "checker_passes":
        raise ValueError("next stage is not checker_passes")
    output_paths = [repo_root / str(value) for value in request["output_paths"]]
    return request, output_paths[-1].parent


def _parallel_checker_request_path(cycle_dir: Path, pass_id: str) -> Path:
    return cycle_dir / "handoff" / f"checker_passes.{pass_id}.request.md"


def _parallel_checker_response_path(cycle_dir: Path, pass_id: str) -> Path:
    return cycle_dir / "handoff" / f"checker_passes.{pass_id}.response.json"


def _parallel_frame_stage2_request_path(cycle_dir: Path) -> Path:
    return cycle_dir / "handoff" / "checker_passes.frame-relation.stage2.request.md"


def _parallel_frame_stage2_response_path(cycle_dir: Path) -> Path:
    return cycle_dir / "handoff" / "checker_passes.frame-relation.stage2.response.json"


def _checker_pass_ids(router: dict[str, Any]) -> list[str]:
    return [str(item["id"]) for item in router.get("passes", [])]


def _normalize_parallel_reviewer(
    value: Any,
    *,
    generation_model: str,
    label: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label}: reviewer must be an object")
    declared_model = str(value.get("declared_model", "")).strip()
    agent_id = str(value.get("agent_id", "")).strip()
    if not declared_model:
        raise ValueError(f"{label}: reviewer.declared_model is required")
    if not agent_id:
        raise ValueError(f"{label}: reviewer.agent_id is required")
    mode = value.get("mode", "handoff")
    if mode != "handoff":
        raise ValueError(f"{label}: reviewer.mode must be handoff")
    reviewer: dict[str, Any] = {
        "mode": "handoff",
        "declared_model": declared_model,
        "ingested_by": "human",
        "agent_id": agent_id,
    }
    if (
        _v3.review_liveness.normalize_text(declared_model)
        == _v3.review_liveness.normalize_text(generation_model)
    ):
        reviewer["same_model_as_generation"] = True
    errors = _v3.review_liveness.validate_reviewer(
        reviewer, generation_model=generation_model
    )
    if errors:
        raise ValueError(f"{label}: " + "; ".join(errors))
    return reviewer


def _load_parallel_checker_responses(
    cycle_dir: Path,
    pass_ids: list[str],
    *,
    generation_model: str,
) -> dict[str, dict[str, Any]] | None:
    paths = {
        pass_id: _parallel_checker_response_path(cycle_dir, pass_id)
        for pass_id in pass_ids
    }
    existing = {pass_id for pass_id, path in paths.items() if path.is_file()}
    if not existing:
        return None
    missing = [pass_id for pass_id in pass_ids if pass_id not in existing]
    if missing:
        raise ValueError(
            "parallel checker handoff is incomplete; missing responses: "
            + ", ".join(missing)
        )

    loaded: dict[str, dict[str, Any]] = {}
    claimed_ids: set[str] = set()
    agent_ids: set[str] = set()
    for expected_pass_id in pass_ids:
        value = json.loads(paths[expected_pass_id].read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(
                f"parallel checker response {expected_pass_id} must be a JSON object"
            )
        claimed = str(value.get("pass_id", "")).strip()
        if claimed != expected_pass_id:
            raise ValueError(
                "parallel checker response pass_id mismatch: "
                f"expected {expected_pass_id}, got {claimed or '<missing>'}"
            )
        if claimed in claimed_ids:
            raise ValueError(f"duplicate checker pass_id in handoff responses: {claimed}")
        claimed_ids.add(claimed)

        reviewer = _normalize_parallel_reviewer(
            value.get("reviewer"),
            generation_model=generation_model,
            label=f"checker {expected_pass_id}",
        )
        normalized_agent_id = _v3.review_liveness.normalize_text(reviewer["agent_id"])
        if normalized_agent_id in agent_ids:
            raise ValueError(
                "parallel checker handoff requires a unique reviewer.agent_id "
                f"for every pass; duplicate: {reviewer['agent_id']}"
            )
        agent_ids.add(normalized_agent_id)
        value["reviewer"] = reviewer
        loaded[expected_pass_id] = value

    if len(claimed_ids) != len(pass_ids):
        raise ValueError("parallel checker handoff must cover every routed pass exactly once")
    return loaded


def _parallel_checker_handoff_body(
    *,
    pass_id: str,
    prompt_text: str,
    packet: dict[str, Any],
    response_name: str,
) -> str:
    frame_note = ""
    if pass_id == "frame-relation":
        frame_note = (
            "\nThis is frame-relation stage 1 only. Keep this exact agent available. "
            "After the coordinator fans in all seven stage-1 responses, the same agent "
            "reviewer.agent_id and declared_model must execute the generated "
            "frame-relation stage-2 request before this pass is complete.\n"
        )
    return (
        "# Independent checker handoff\n\n"
        f"Stage: `checker_passes/{pass_id}`\n\n"
        "Run this request in its own independent agent/session. The seven checker "
        "pass requests are designed to run concurrently; do not concatenate them "
        "into one prompt or reuse one agent for multiple passes.\n\n"
        f"Save exactly one JSON response as `{response_name}`. The top-level JSON "
        "must include the routed `pass_id` and a `reviewer` object with "
        '`mode: "handoff"`, the actual `declared_model`, '
        '`ingested_by: "human"`, and a non-empty `agent_id`. Each checker pass '
        "must use a different agent_id."
        + frame_note
        + "\n## Prompt\n\n"
        + prompt_text
        + "\n\n## Input packet\n\n```json\n"
        + json.dumps(packet, ensure_ascii=False, indent=2)
        + "\n```\n"
    )


def prepare_handoff(
    manifest: dict[str, Any], *, repo_root: Path = REPO_ROOT
) -> Path:
    request = _v3.next_stage_request(manifest)
    if request is None or request.get("name") not in REVIEW_STAGES:
        raise ValueError("next stage is not a review handoff stage")
    if request.get("reviewer_mode") != "handoff":
        raise ValueError("review handoff is only available in handoff mode")
    if request.get("name") != "checker_passes":
        return _ORIGINAL_PREPARE_HANDOFF(manifest, repo_root=repo_root)

    _, cycle_dir = _checker_cycle(manifest, repo_root=repo_root)
    check_dir = cycle_dir / "check_passes"
    checkpoint = check_dir / "checker_passes.stage1.json"
    handoff_dir = cycle_dir / "handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    if checkpoint.is_file():
        stage2_request_path = check_dir / "frame-relation.antonym-axis.stage2.request.json"
        if not stage2_request_path.is_file():
            raise ValueError(
                "process defect: checker stage 1 checkpoint has no stage 2 request"
            )
        packet = json.loads(stage2_request_path.read_text(encoding="utf-8"))
        prompt_text = (
            repo_root / "prompts" / "check_pass_frame_relation_v7.md"
        ).read_text(encoding="utf-8")
        checkpoint_value = json.loads(checkpoint.read_text(encoding="utf-8"))
        frame_reviewer = (
            checkpoint_value.get("checker_reviewers", {}).get("frame-relation", {})
            if isinstance(checkpoint_value, dict)
            else {}
        )
        expected_agent = (
            str(frame_reviewer.get("agent_id", "")).strip()
            if isinstance(frame_reviewer, dict)
            else ""
        )
        expected_model = (
            str(frame_reviewer.get("declared_model", "")).strip()
            if isinstance(frame_reviewer, dict)
            else ""
        )
        provenance = ""
        if expected_agent:
            provenance = (
                "\nThis stage must be executed by the same frame-relation agent "
                f"from stage 1: reviewer.agent_id=`{expected_agent}`"
                + (f", declared_model=`{expected_model}`." if expected_model else ".")
                + "\n"
            )
        body = (
            "# Independent review handoff\n\n"
            "Stage: `checker_passes/frame-relation-antonym-axis-stage2`\n\n"
            "This is the only serial dependency inside the parallel checker fan-out. "
            "Do not rerun the other six checker passes."
            + provenance
            + "\nSave one `antonym_axis_adjudication_record_v1` JSON object as "
            "`checker_passes.frame-relation.stage2.response.json`. Include the "
            "same top-level handoff `reviewer` metadata used by the frame-relation "
            "stage-1 response.\n\n"
            "## Prompt\n\n"
            + prompt_text
            + "\n\n## Input packet\n\n```json\n"
            + json.dumps(packet, ensure_ascii=False, indent=2)
            + "\n```\n"
        )
        parallel_path = _parallel_frame_stage2_request_path(cycle_dir)
        parallel_path.write_text(body, encoding="utf-8")
        legacy_path = handoff_dir / "checker_passes.stage2.request.md"
        legacy_path.write_text(body, encoding="utf-8")
        return legacy_path

    _, packet = _ORIGINAL_PREPARE_REVIEW_INPUTS(manifest, repo_root=repo_root)
    bundles = packet.get("requests")
    if not isinstance(bundles, list) or not bundles:
        raise ValueError("checker review packet has no routed requests")

    rows: list[str] = []
    seen: set[str] = set()
    for bundle in bundles:
        if not isinstance(bundle, dict):
            raise ValueError("checker request bundle must be an object")
        pass_id = str(bundle.get("pass_id", "")).strip()
        if not pass_id or pass_id in seen:
            raise ValueError("checker request bundles contain duplicate or missing pass_id")
        seen.add(pass_id)
        specification = str(bundle.get("specification", "")).strip()
        prompt_path = repo_root / specification
        if not prompt_path.is_file():
            raise ValueError(f"checker prompt is missing: {specification}")
        request_path = _parallel_checker_request_path(cycle_dir, pass_id)
        response_name = f"checker_passes.{pass_id}.response.json"
        request_path.write_text(
            _parallel_checker_handoff_body(
                pass_id=pass_id,
                prompt_text=prompt_path.read_text(encoding="utf-8"),
                packet=bundle,
                response_name=response_name,
            ),
            encoding="utf-8",
        )
        rows.append(f"- `{pass_id}`: `{request_path.name}` -> `{response_name}`")

    index_path = repo_root / str(request["input_packet_path"])
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        "# Independent review handoff — parallel checker fan-out\n\n"
        "Stage: `checker_passes`\n\n"
        f"Protocol: `{PARALLEL_CHECKER_PROTOCOL_VERSION}`\n\n"
        "Launch all seven request files below concurrently, one independent agent "
        "per pass. Do not concatenate the seven checker specifications. Wait for "
        "all seven response files before ingestion. The coordinator performs only "
        "mechanical validation/fan-in; it must not synthesize missing checker "
        "responses.\n\n"
        "Parallel execution does not pause the workflow guard: keep the normal "
        "heartbeat/checkpoint discipline while the agents are running, and stop "
        "rather than silently restarting if the run budget is exhausted.\n\n"
        "The `frame-relation` worker performs its blind stage 1 now; after fan-in "
        "the coordinator generates a stage-2 request that must go back to that "
        "same agent. The other six passes do not rerun.\n\n"
        "## Fan-out files\n\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )
    return index_path


def _process_parallel_stage1(
    manifest: dict[str, Any],
    *,
    cycle_dir: Path,
    repo_root: Path,
    responses: dict[str, dict[str, Any]],
) -> Path:
    entry = repo_root / str(manifest["entry_path"])
    front, _ = _v3.validate_entry._split_front_matter(entry.read_text(encoding="utf-8"))
    generation_model = _v3.validate_entry._front_matter_values(front or []).get("model", "")
    check_dir = cycle_dir / "check_passes"
    router = _v3.check_passes.load_router(repo_root / DEFAULT_CHECK_SPEC)
    pass_ids = _checker_pass_ids(router)
    alignment = json.loads(
        (check_dir / "example-attribution.alignment-key.json").read_text(encoding="utf-8")
    )
    antonym_alignment = json.loads(
        (check_dir / "frame-relation.antonym-axis.alignment-key.json").read_text(encoding="utf-8")
    )
    outputs: list[dict[str, Any]] = []
    reviewers: dict[str, dict[str, Any]] = {}
    frame_bundle: dict[str, Any] | None = None
    frame_blind_path = check_dir / "frame-relation.antonym-axis.blind-record.json"

    for pass_id in pass_ids:
        bundle_path = check_dir / f"{pass_id}.request.json"
        if not bundle_path.is_file():
            raise ValueError(f"checker request is missing: {bundle_path}")
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        response = dict(responses[pass_id])
        reviewer = dict(response["reviewer"])
        reviewers[pass_id] = reviewer

        if pass_id == "frame-relation":
            frame_bundle = bundle
            blind_record = _v3.check_passes.bind_antonym_axis_blind_record(response, bundle)
            blind_record["reviewer"] = reviewer
            blind_errors = _v3.check_passes.validate_antonym_axis_blind_record(
                blind_record,
                bundle,
                generation_model=generation_model,
            )
            if blind_errors:
                raise ValueError("frame-relation stage 1: " + "; ".join(blind_errors))
            frame_blind_path.write_text(
                json.dumps(blind_record, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            outputs.append(
                {
                    "pass_id": pass_id,
                    "reviewer": reviewer,
                    "findings": [],
                    "antonym_axis_blind_record": blind_record,
                }
            )
            continue

        if pass_id == "example-attribution":
            blind_path = check_dir / "example-attribution.blind-record.json"
            blind_path.write_text(
                json.dumps(response, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            output = _v3.check_passes.reconcile_example_attribution(
                bundle,
                response,
                alignment,
                aligned_at=datetime.now(timezone.utc).isoformat(),
            )
            output["reviewer"] = reviewer
        else:
            output = response

        errors = _v3.check_passes.validate_pass_output(
            output,
            router,
            entry_path=entry,
            repo_root=repo_root,
            example_request=bundle if pass_id == "example-attribution" else None,
            request_payload=bundle,
            alignment_key=alignment if pass_id == "example-attribution" else None,
            generation_model=generation_model,
        )
        if errors:
            raise ValueError(f"pass output {pass_id}: " + "; ".join(errors))
        (check_dir / f"{pass_id}.json").write_text(
            json.dumps(output, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        outputs.append(output)

    if frame_bundle is None:
        raise ValueError("parallel checker responses contain no frame-relation pass")
    stage2_request = _v3.check_passes.materialize_antonym_axis_stage2_request(
        entry,
        frame_bundle,
        frame_blind_path,
        antonym_alignment,
        repo_root=repo_root,
    )
    stage2_request_path = check_dir / "frame-relation.antonym-axis.stage2.request.json"
    stage2_request_path.write_text(
        json.dumps(stage2_request, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    checkpoint = {
        **_v3._normal_review_metadata(manifest, entry, repo_root=repo_root),
        "pass_outputs": outputs,
        "checker_reviewers": reviewers,
        "independent_candidates": [],
        "summary": (
            "Independent checker stage 1 completed by seven parallel handoff agents; "
            "frame-relation stage 2 remains pending."
        ),
    }
    checkpoint_path = check_dir / "checker_passes.stage1.json"
    checkpoint_path.write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return prepare_handoff(manifest, repo_root=repo_root)


def _process_parallel_stage2(
    manifest: dict[str, Any],
    *,
    cycle_dir: Path,
    repo_root: Path,
    response_path: Path,
) -> Path:
    checkpoint_path = cycle_dir / "check_passes" / "checker_passes.stage1.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    reviewers = checkpoint.get("checker_reviewers")
    if not isinstance(reviewers, dict) or not isinstance(reviewers.get("frame-relation"), dict):
        raise ValueError(
            "parallel frame-relation stage 2 requires a parallel stage-1 checkpoint"
        )
    expected_reviewer = reviewers["frame-relation"]

    entry = repo_root / str(manifest["entry_path"])
    front, _ = _v3.validate_entry._split_front_matter(entry.read_text(encoding="utf-8"))
    generation_model = _v3.validate_entry._front_matter_values(front or []).get("model", "")
    value = json.loads(response_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("frame-relation stage-2 response must be a JSON object")
    if str(value.get("pass_id", "")).strip() != "frame-relation":
        raise ValueError("frame-relation stage-2 response has the wrong pass_id")
    reviewer = _normalize_parallel_reviewer(
        value.get("reviewer"),
        generation_model=generation_model,
        label="frame-relation stage 2",
    )
    if (
        _v3.review_liveness.normalize_text(reviewer["agent_id"])
        != _v3.review_liveness.normalize_text(expected_reviewer.get("agent_id"))
    ):
        raise ValueError(
            "frame-relation stage 2 must use the same reviewer.agent_id as stage 1"
        )
    if (
        _v3.review_liveness.normalize_text(reviewer["declared_model"])
        != _v3.review_liveness.normalize_text(expected_reviewer.get("declared_model"))
    ):
        raise ValueError(
            "frame-relation stage 2 must use the same declared_model as stage 1"
        )
    value["reviewer"] = reviewer

    check_dir = cycle_dir / "check_passes"
    router = _v3.check_passes.load_router(repo_root / DEFAULT_CHECK_SPEC)
    antonym_request = json.loads(
        (check_dir / "frame-relation.request.json").read_text(encoding="utf-8")
    )
    antonym_alignment = json.loads(
        (check_dir / "frame-relation.antonym-axis.alignment-key.json").read_text(encoding="utf-8")
    )
    blind_record = json.loads(
        (check_dir / "frame-relation.antonym-axis.blind-record.json").read_text(encoding="utf-8")
    )
    stage2_request = json.loads(
        (check_dir / "frame-relation.antonym-axis.stage2.request.json").read_text(encoding="utf-8")
    )
    adjudication = _v3.check_passes.bind_antonym_axis_adjudication_record(
        value, stage2_request, blind_record
    )
    adjudication["reviewer"] = reviewer
    adjudication_path = check_dir / "frame-relation.antonym-axis.adjudication-record.json"
    adjudication_path.write_text(
        json.dumps(adjudication, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    output = _v3.check_passes.reconcile_antonym_axis(
        antonym_request,
        blind_record,
        stage2_request,
        adjudication,
        antonym_alignment,
        aligned_at=datetime.now(timezone.utc).isoformat(),
        generation_model=generation_model,
    )
    output["reviewer"] = reviewer
    errors = _v3.check_passes.validate_pass_output(
        output,
        router,
        entry_path=entry,
        repo_root=repo_root,
        antonym_request=antonym_request,
        antonym_stage2_request=stage2_request,
        antonym_alignment_key=antonym_alignment,
        request_payload=stage2_request,
        generation_model=generation_model,
    )
    if errors:
        raise ValueError("pass output frame-relation: " + "; ".join(errors))

    outputs = checkpoint.get("pass_outputs")
    if not isinstance(outputs, list):
        raise ValueError("checker stage 1 checkpoint has no pass_outputs")
    for index, candidate in enumerate(outputs):
        if isinstance(candidate, dict) and candidate.get("pass_id") == "frame-relation":
            outputs[index] = output
            break
    else:
        raise ValueError("checker stage 1 checkpoint has no frame-relation output")

    reviewers["frame-relation"] = reviewer
    checkpoint["pass_outputs"] = outputs
    checkpoint["checker_reviewers"] = reviewers
    checkpoint["summary"] = (
        "Independent checker passes completed by parallel handoff; "
        "frame-relation preserved its serial blind/adjudication dependency."
    )
    target = cycle_dir / "pass_findings.json"
    target.write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def ingest_handoff_review(
    manifest: dict[str, Any],
    *,
    stage: str,
    declared_model: str,
    reviewer_agent_id: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> Path:
    if stage != "checker_passes":
        return _ORIGINAL_INGEST_HANDOFF_REVIEW(
            manifest,
            stage=stage,
            declared_model=declared_model,
            reviewer_agent_id=reviewer_agent_id,
            repo_root=repo_root,
        )

    request, cycle_dir = _checker_cycle(manifest, repo_root=repo_root)
    if request.get("reviewer_mode") != "handoff":
        raise ValueError("review ingestion requires a handoff review stage")
    check_dir = cycle_dir / "check_passes"
    checkpoint = check_dir / "checker_passes.stage1.json"

    if checkpoint.is_file():
        parallel_stage2 = _parallel_frame_stage2_response_path(cycle_dir)
        if parallel_stage2.is_file():
            return _process_parallel_stage2(
                manifest,
                cycle_dir=cycle_dir,
                repo_root=repo_root,
                response_path=parallel_stage2,
            )
        return _ORIGINAL_INGEST_HANDOFF_REVIEW(
            manifest,
            stage=stage,
            declared_model=declared_model,
            reviewer_agent_id=reviewer_agent_id,
            repo_root=repo_root,
        )

    entry = repo_root / str(manifest["entry_path"])
    front, _ = _v3.validate_entry._split_front_matter(entry.read_text(encoding="utf-8"))
    generation_model = _v3.validate_entry._front_matter_values(front or []).get("model", "")
    router = _v3.check_passes.load_router(repo_root / DEFAULT_CHECK_SPEC)
    pass_ids = _checker_pass_ids(router)
    responses = _load_parallel_checker_responses(
        cycle_dir,
        pass_ids,
        generation_model=generation_model,
    )
    if responses is None:
        return _ORIGINAL_INGEST_HANDOFF_REVIEW(
            manifest,
            stage=stage,
            declared_model=declared_model,
            reviewer_agent_id=reviewer_agent_id,
            repo_root=repo_root,
        )
    return _process_parallel_stage1(
        manifest,
        cycle_dir=cycle_dir,
        repo_root=repo_root,
        responses=responses,
    )


def _execute_checker_bundle_api(
    bundle: dict[str, Any],
    *,
    router: dict[str, Any],
    entry: Path,
    repo_root: Path,
    cycle_dir: Path,
    check_dir: Path,
    alignment: dict[str, Any],
    antonym_alignment: dict[str, Any],
    provider: str,
    model: str,
    api_key: str,
    endpoint: str | None,
    generation_model: str,
) -> tuple[dict[str, Any], list[Path]]:
    pass_id = str(bundle["pass_id"])
    request_path = check_dir / f"{pass_id}.request.json"
    prompt_path = repo_root / str(bundle["specification"])
    final_path = check_dir / f"{pass_id}.json"
    created: list[Path] = []

    if pass_id == "frame-relation":
        blind_record_path = check_dir / "frame-relation.antonym-axis.blind-record.json"
        blind_record = _v3.review_call.execute_review(
            stage="checker-frame-relation-antonym-axis-stage1",
            request_path=request_path,
            prompt_path=prompt_path,
            cycle_dir=cycle_dir,
            output_path=blind_record_path,
            provider=provider,
            model=model,
            api_key=api_key,
            endpoint=endpoint,
            generation_model=generation_model,
        )
        blind_record = _v3.check_passes.bind_antonym_axis_blind_record(
            blind_record, bundle
        )
        blind_record_path.write_text(
            json.dumps(blind_record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        blind_errors = _v3.check_passes.validate_antonym_axis_blind_record(
            blind_record,
            bundle,
            generation_model=generation_model,
        )
        if blind_errors:
            raise ValueError(
                "API pass output frame-relation stage 1: " + "; ".join(blind_errors)
            )
        stage2_request = _v3.check_passes.materialize_antonym_axis_stage2_request(
            entry,
            bundle,
            blind_record_path,
            antonym_alignment,
            repo_root=repo_root,
        )
        stage2_request_path = check_dir / "frame-relation.antonym-axis.stage2.request.json"
        stage2_request_path.write_text(
            json.dumps(stage2_request, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        adjudication_path = check_dir / "frame-relation.antonym-axis.adjudication-record.json"
        adjudication = _v3.review_call.execute_review(
            stage="checker-frame-relation-antonym-axis-stage2",
            request_path=stage2_request_path,
            prompt_path=prompt_path,
            cycle_dir=cycle_dir,
            output_path=adjudication_path,
            provider=provider,
            model=model,
            api_key=api_key,
            endpoint=endpoint,
            generation_model=generation_model,
        )
        adjudication = _v3.check_passes.bind_antonym_axis_adjudication_record(
            adjudication, stage2_request, blind_record
        )
        adjudication_path.write_text(
            json.dumps(adjudication, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        output = _v3.check_passes.reconcile_antonym_axis(
            bundle,
            blind_record,
            stage2_request,
            adjudication,
            antonym_alignment,
            aligned_at=datetime.now(timezone.utc).isoformat(),
            generation_model=generation_model,
        )
        final_path.write_text(
            json.dumps(output, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        errors = _v3.check_passes.validate_pass_output(
            output,
            router,
            entry_path=entry,
            repo_root=repo_root,
            antonym_request=bundle,
            antonym_stage2_request=stage2_request,
            antonym_alignment_key=antonym_alignment,
            request_payload=stage2_request,
            generation_model=generation_model,
        )
        if errors:
            raise ValueError("API pass output frame-relation: " + "; ".join(errors))
        return output, [blind_record_path, adjudication_path, final_path]

    model_output_path = (
        check_dir / "example-attribution.blind-record.json"
        if pass_id == "example-attribution"
        else final_path
    )
    model_output = _v3.review_call.execute_review(
        stage=f"checker-{pass_id}",
        request_path=request_path,
        prompt_path=prompt_path,
        cycle_dir=cycle_dir,
        output_path=model_output_path,
        provider=provider,
        model=model,
        api_key=api_key,
        endpoint=endpoint,
        generation_model=generation_model,
    )
    if pass_id == "example-attribution":
        output = _v3.check_passes.reconcile_example_attribution(
            bundle,
            model_output,
            alignment,
            aligned_at=datetime.now(timezone.utc).isoformat(),
        )
        final_path.write_text(
            json.dumps(output, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        created.append(model_output_path)
    else:
        output = model_output
    errors = _v3.check_passes.validate_pass_output(
        output,
        router,
        entry_path=entry,
        repo_root=repo_root,
        example_request=bundle if pass_id == "example-attribution" else None,
        request_payload=bundle,
        alignment_key=alignment if pass_id == "example-attribution" else None,
        generation_model=generation_model,
    )
    if errors:
        raise ValueError(f"API pass output {pass_id}: " + "; ".join(errors))
    created.append(final_path)
    return output, created


def execute_api_review_stage(
    manifest: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    endpoint: str | None = None,
) -> list[Path]:
    request = _v3.next_stage_request(manifest)
    if request is None or request.get("name") not in REVIEW_STAGES:
        raise ValueError("next stage is not an API review stage")
    if request.get("reviewer_mode") != "api":
        raise ValueError("API review execution requires reviewer mode api")
    if request.get("name") != "checker_passes":
        return _ORIGINAL_EXECUTE_API_REVIEW_STAGE(
            manifest,
            repo_root=repo_root,
            provider=provider,
            model=model,
            api_key=api_key,
            endpoint=endpoint,
        )

    resolved_provider = (
        provider or os.environ.get("DICT_REVIEW_PROVIDER", "openai")
    ).strip().lower()
    resolved_model = (model or os.environ.get("DICT_REVIEW_MODEL", "")).strip()
    resolved_key = (api_key or os.environ.get("DICT_REVIEW_API_KEY", "")).strip()
    resolved_endpoint = (
        endpoint
        if endpoint is not None
        else os.environ.get("DICT_REVIEW_ENDPOINT", "").strip() or None
    )
    if resolved_provider not in _v3.review_call.SUPPORTED_PROVIDERS:
        raise ValueError(
            "DICT_REVIEW_PROVIDER must be one of "
            f"{sorted(_v3.review_call.SUPPORTED_PROVIDERS)}"
        )
    if not resolved_model or not resolved_key:
        raise ValueError(
            "API review requires DICT_REVIEW_MODEL and DICT_REVIEW_API_KEY"
        )

    entry = repo_root / str(manifest["entry_path"])
    front, _ = _v3.validate_entry._split_front_matter(entry.read_text(encoding="utf-8"))
    generation_model = _v3.validate_entry._front_matter_values(front or []).get("model", "")
    output_paths = [repo_root / str(value) for value in request["output_paths"]]
    cycle_dir = output_paths[-1].parent
    _, packet = _ORIGINAL_PREPARE_REVIEW_INPUTS(manifest, repo_root=repo_root)
    bundles = packet.get("requests")
    if not isinstance(bundles, list) or not bundles:
        raise ValueError("checker review packet has no routed requests")
    if len(bundles) > CHECKER_MAX_WORKERS:
        raise ValueError(
            f"checker router produced {len(bundles)} passes; "
            f"parallel executor limit is {CHECKER_MAX_WORKERS}"
        )

    check_dir = cycle_dir / "check_passes"
    router = _v3.check_passes.load_router(repo_root / DEFAULT_CHECK_SPEC)
    alignment = json.loads(
        (check_dir / "example-attribution.alignment-key.json").read_text(encoding="utf-8")
    )
    antonym_alignment = json.loads(
        (check_dir / "frame-relation.antonym-axis.alignment-key.json").read_text(encoding="utf-8")
    )

    with ThreadPoolExecutor(
        max_workers=min(CHECKER_MAX_WORKERS, len(bundles)),
        thread_name_prefix="checker-pass",
    ) as executor:
        futures = [
            executor.submit(
                _execute_checker_bundle_api,
                bundle,
                router=router,
                entry=entry,
                repo_root=repo_root,
                cycle_dir=cycle_dir,
                check_dir=check_dir,
                alignment=alignment,
                antonym_alignment=antonym_alignment,
                provider=resolved_provider,
                model=resolved_model,
                api_key=resolved_key,
                endpoint=resolved_endpoint,
                generation_model=generation_model,
            )
            for bundle in bundles
        ]
        results = [future.result() for future in futures]

    pass_outputs = [output for output, _ in results]
    created = [path for _, paths in results for path in paths]
    if [str(item.get("pass_id")) for item in pass_outputs] != [
        str(bundle.get("pass_id")) for bundle in bundles
    ]:
        raise ValueError("parallel checker executor returned pass outputs out of contract")

    normal_review = {
        **_v3._normal_review_metadata(manifest, entry, repo_root=repo_root),
        "pass_outputs": pass_outputs,
        "independent_candidates": [],
        "summary": (
            "Independent checker passes completed through the review API "
            "with parallel pass execution."
        ),
    }
    pass_findings_path = cycle_dir / "pass_findings.json"
    pass_findings_path.write_text(
        json.dumps(normal_review, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return [*created, pass_findings_path]


_v3.prepare_handoff = prepare_handoff
_v3.ingest_handoff_review = ingest_handoff_review
_v3.execute_api_review_stage = execute_api_review_stage

globals()["prepare_handoff"] = prepare_handoff
globals()["ingest_handoff_review"] = ingest_handoff_review
globals()["execute_api_review_stage"] = execute_api_review_stage


if __name__ == "__main__":
    raise SystemExit(_v3.main())
