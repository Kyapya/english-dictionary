from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import entry_workflow_guard as guard
import check_passes
import content_audit
import process_improvement
import review_liveness
import review_call
import validate_entry
from slugify import slugify


REPO_ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR_VERSION = "run_word_v3"
DEFAULT_CHECK_SPEC = "prompts/check_router_v6.md"
DEFAULT_FINAL_SPEC = "prompts/final_review_spec_v2.md"
DEFAULT_FINAL_BLIND_SPEC = "prompts/final_blind_prompt_v2.md"
COST_SCHEMA_VERSION = "workflow_cost_v1"
WORKFLOW_CONTRACT_VERSION = "workflow_improvement_v1"


@dataclass(frozen=True)
class StagePlan:
    name: str
    executor: str
    specification_files: tuple[str, ...]
    input_scope: tuple[str, ...]
    output_paths: tuple[str, ...]
    guard_checkpoints: tuple[str, ...] = ()
    context_mode: str = "coordinator"
    reviewer_mode: str | None = None
    input_packet_path: str | None = None

    def to_dict(self, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
        value = asdict(self)
        value["specification_files"] = list(self.specification_files)
        value["input_scope"] = list(self.input_scope)
        value["output_paths"] = list(self.output_paths)
        value["guard_checkpoints"] = list(self.guard_checkpoints)
        value["instruction_bytes"] = (
            sum(
                (repo_root / item).stat().st_size
                for item in self.specification_files
                if (repo_root / item).is_file()
            )
            if "llm" in self.executor
            else 0
        )
        return value


def entry_path_for(headword: str) -> str:
    resolved = slugify(headword)
    if not resolved:
        raise ValueError("headword must produce a non-empty slug")
    return f"entries/{resolved[0]}/{resolved}.md"


def _artifact_root(headword: str) -> str:
    resolved = slugify(headword)
    return f"audits/runs/{resolved[0]}/{resolved}/{{run_id}}"


def _review_input_packet_path(root: str, stage: str, reviewer_mode: str) -> str:
    if reviewer_mode == "handoff":
        return f"{root}/handoff/{stage}.request.md"
    if stage == "checker_passes":
        return f"{root}/check_passes/"
    return f"{root}/{stage}.request.json"


def build_plan(
    headword: str,
    *,
    check_spec: str = DEFAULT_CHECK_SPEC,
    final_spec: str = DEFAULT_FINAL_SPEC,
    reviewer_mode: str = "api",
) -> tuple[StagePlan, ...]:
    entry = entry_path_for(headword)
    resolved = slugify(headword)
    root = _artifact_root(headword)
    audit = f"audits/{resolved[0]}/{resolved}.json"
    run = f"audits/workflow_runs/{resolved}/{{run_id}}.json"
    return (
        StagePlan(
            "guard_start",
            "orchestrator",
            ("scripts/entry_workflow_guard.py",),
            ("headword", "queue row", "git branch", "base SHA"),
            (run,),
            ("preflight", "preflight_pushed"),
        ),
        StagePlan(
            "generation",
            "llm",
            ("prompts/entry_spec_v5.md", "process_improvement/ACTIVE.md"),
            ("headword", "entry specification", "active process rules"),
            (entry, f"{root}/generation.json"),
            ("draft_saved",),
        ),
        StagePlan(
            "mechanical_validator",
            "python",
            ("scripts/validate_entry.py",),
            ("entry including front matter",),
            (f"{root}/validator.json",),
        ),
        StagePlan(
            "checker_passes",
            "router",
            (check_spec,),
            (
                "router-selected entry sections",
                "frame-relation antonym-axis masked stage 1 before full-sense adjudication",
                "example-attribution masked stage 1 before ownership alignment",
                "source inventory for evidence pass",
                "machine validator findings",
            ),
            (
                f"{root}/source_inventory.json",
                f"{root}/check_passes/",
                f"{root}/pass_findings.json",
            ),
            ("source_inventory_complete", "normal_review_complete"),
            "fresh_normal_context",
            reviewer_mode,
            _review_input_packet_path(root, "checker_passes", reviewer_mode),
        ),
        StagePlan(
            "cold_review",
            "independent_llm",
            ("prompts/cold_review_prompt_v1.md",),
            ("entry body without front matter",),
            (f"{root}/cold_review.json",),
            ("cold_review_complete",),
            "context_free_cold",
            reviewer_mode,
            _review_input_packet_path(root, "cold_review", reviewer_mode),
        ),
        StagePlan(
            "pre_blind_resolution",
            "llm",
            ("prompts/pre_blind_resolution_v1.md",),
            (
                "fixed draft",
                "checker findings",
                "cold-review findings",
                "source inventory",
            ),
            (
                f"{root}/pre_blind_resolution.json",
                f"{root}/pre_blind_revision.json",
            ),
            (),
            "pre_blind_resolution_context",
        ),
        StagePlan(
            "checker_recheck",
            "router",
            ("scripts/workflow_revision.py", check_spec),
            (
                "pre-blind before/after bodies",
                "initial checker requests and valid outputs",
                "unchanged source-first artifact",
            ),
            (f"{root}/checker_recheck_manifest.json",),
            (),
            "deterministic_impact_scope",
            reviewer_mode,
            _review_input_packet_path(root, "checker_passes", reviewer_mode),
        ),
        StagePlan(
            "final_blind",
            "independent_llm",
            (DEFAULT_FINAL_BLIND_SPEC,),
            ("post-pre-blind-resolution entry body only",),
            (f"{root}/final_blind.json",),
            (),
            "context_free_final_blind",
            reviewer_mode,
            _review_input_packet_path(root, "final_blind", reviewer_mode),
        ),
        StagePlan(
            "blind_seal",
            "python",
            ("scripts/generate_audit_manifest.py",),
            ("final blind raw JSON", "entry body hash"),
            (f"{root}/blind_seal.json",),
            ("blind_seal_complete",),
        ),
        StagePlan(
            "post_blind_resolution",
            "llm",
            ("prompts/post_blind_resolution_v1.md",),
            (
                "latest entry body",
                "sealed final-blind findings only",
                "source inventory",
            ),
            (
                f"{root}/post_blind_resolution.json",
                f"{root}/post_blind_verification.json",
                f"{root}/resolutions.json",
            ),
            (),
            "post_blind_resolution_context",
        ),
        StagePlan(
            "final_review",
            "independent_llm",
            (final_spec,),
            (
                "latest entry body",
                "sealed final-blind output",
                "pre- and post-blind resolution records",
                "checker recheck/reuse manifest",
                "targeted adjudications for concrete unresolved issues",
            ),
            (f"{root}/final_review.json", audit),
            ("final_review_complete",),
            "final_reconciliation_context",
            reviewer_mode,
            _review_input_packet_path(root, "final_review", reviewer_mode),
        ),
        StagePlan(
            "status_update",
            "python",
            ("scripts/run_word.py",),
            ("final decision", "entry front matter", "queue row"),
            (entry, "queue/words.csv", f"{root}/status_update.json"),
        ),
        StagePlan(
            "export",
            "python",
            ("scripts/export_all_markdown.py", "scripts/export_index.py"),
            ("checked/final entries", "queue"),
            ("exports/dictionary_all.md", "exports/dictionary_index.csv"),
            ("completed",),
        ),
    )


def plan_payload(
    headword: str,
    repo_root: Path = REPO_ROOT,
    *,
    reviewer_mode: str = "api",
) -> dict[str, Any]:
    stages = [
        stage.to_dict(repo_root)
        for stage in build_plan(headword, reviewer_mode=reviewer_mode)
    ]
    encoded = json.dumps(stages, ensure_ascii=False, sort_keys=True).encode("utf-8")
    pass_plans: list[dict[str, Any]] = []
    router_path = repo_root / DEFAULT_CHECK_SPEC
    if router_path.is_file():
        router = check_passes.load_router(router_path)
        for item in router.get("passes", []):
            specification = str(item["specification"])
            specification_path = repo_root / specification
            pass_plan = {
                "id": item["id"],
                "specification": specification,
                "taxonomy_ids": list(item["taxonomy_ids"]),
                "input_sections": list(item["sections"]),
                "output_path": (
                    f"{_artifact_root(headword)}/check_passes/"
                    f"{item['id']}.json"
                ),
                "instruction_bytes": (
                    specification_path.stat().st_size
                    if specification_path.is_file()
                    else 0
                ),
                "reviewer_mode": reviewer_mode,
                "input_packet_path": (
                    f"{_artifact_root(headword)}/check_passes/"
                    f"{item['id']}.request.json"
                ),
            }
            if item["id"] == "example-attribution":
                pass_plan.update(
                    {
                        "stage1_output_path": (
                            f"{_artifact_root(headword)}/check_passes/"
                            "example-attribution.blind-record.json"
                        ),
                        "alignment_key_path": (
                            f"{_artifact_root(headword)}/check_passes/"
                            "example-attribution.alignment-key.json"
                        ),
                    }
                )
            if item["id"] == "frame-relation":
                pass_plan.update(
                    {
                        "stage1_output_path": (
                            f"{_artifact_root(headword)}/check_passes/"
                            "frame-relation.antonym-axis.blind-record.json"
                        ),
                        "stage2_request_path": (
                            f"{_artifact_root(headword)}/check_passes/"
                            "frame-relation.antonym-axis.stage2.request.json"
                        ),
                        "stage2_output_path": (
                            f"{_artifact_root(headword)}/check_passes/"
                            "frame-relation.antonym-axis.adjudication-record.json"
                        ),
                        "alignment_key_path": (
                            f"{_artifact_root(headword)}/check_passes/"
                            "frame-relation.antonym-axis.alignment-key.json"
                        ),
                    }
                )
            pass_plans.append(pass_plan)
    return {
        "workflow_contract_version": WORKFLOW_CONTRACT_VERSION,
        "orchestrator_version": ORCHESTRATOR_VERSION,
        "headword": headword,
        "entry_path": entry_path_for(headword),
        "plan_sha256": hashlib.sha256(encoded).hexdigest(),
        "stages": stages,
        "checker_passes": pass_plans,
        "reviewer_mode": reviewer_mode,
    }


def initialize_cost_metrics(
    plan: dict[str, Any], *, repo_root: Path = REPO_ROOT
) -> dict[str, Any]:
    if (repo_root / "process_improvement" / "retirement_state.json").is_file():
        retirement_errors = process_improvement.validate_retirement_state(repo_root)
        if retirement_errors:
            raise ValueError("; ".join(retirement_errors))
    records, errors = process_improvement._load_records(repo_root)
    if errors and (repo_root / "process_improvement" / "records").exists():
        raise ValueError("; ".join(errors))
    if errors:
        records = []
    process_rules = []
    for record in records:
        if record.get("status") not in {"trial", "active"}:
            continue
        rule_bytes = len(str(record.get("action_rule", "")).encode("utf-8"))
        process_rules.append(
            {
                "id": str(record["id"]),
                "status": str(record["status"]),
                "instruction_bytes": rule_bytes,
                "input_bytes": 0,
                "duration_seconds": 0.0,
                "defects_detected": 0,
                "completed": False,
            }
        )
    stages = []
    for item in plan["stages"]:
        stages.append(
            {
                "id": item["name"],
                "instruction_bytes": item["instruction_bytes"],
                "input_bytes": 0,
                "duration_seconds": 0.0,
                "defects_detected": 0,
                "revision_count": 0,
                "completed": item["name"] == "guard_start",
            }
        )
    checker_passes = [
        {
            "id": item["id"],
            "instruction_bytes": item["instruction_bytes"],
            "input_bytes": 0,
            "duration_seconds": 0.0,
            "defects_detected": 0,
            "completed": False,
        }
        for item in plan["checker_passes"]
    ]
    return {
        "schema_version": COST_SCHEMA_VERSION,
        "total_cycles": 1,
        "total_revisions": 0,
        "total_duration_seconds": 0.0,
        "completed_at": "",
        "stages": stages,
        "checker_passes": checker_passes,
        "process_rules": process_rules,
    }


def initialize_orchestrator_state(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "next_stage_index": 1,
        "completed_stages": ["guard_start"],
        "stage_outputs": {},
    }


def _cost_row(metrics: dict[str, Any], collection: str, item_id: str) -> dict[str, Any]:
    items = metrics.get(collection)
    if not isinstance(items, list):
        raise ValueError(f"metrics.{collection} must be a list")
    matches = [item for item in items if isinstance(item, dict) and item.get("id") == item_id]
    if len(matches) != 1:
        raise ValueError(f"metrics.{collection} has no unique row for {item_id}")
    return matches[0]


def record_cost(
    manifest: dict[str, Any],
    *,
    collection: str,
    item_id: str,
    input_bytes: int,
    duration_seconds: float,
    defects_detected: int = 0,
    revision_count: int = 0,
) -> None:
    metrics = manifest.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("workflow manifest has no cost metrics")
    if collection not in {"stages", "checker_passes", "process_rules"}:
        raise ValueError("unknown cost collection")
    if (
        not isinstance(input_bytes, int)
        or isinstance(input_bytes, bool)
        or input_bytes < 0
    ):
        raise ValueError("input_bytes must be a non-negative integer")
    if not isinstance(duration_seconds, (int, float)) or duration_seconds < 0:
        raise ValueError("duration_seconds must be non-negative")
    if (
        not isinstance(defects_detected, int)
        or isinstance(defects_detected, bool)
        or defects_detected < 0
    ):
        raise ValueError("defects_detected must be a non-negative integer")
    if (
        not isinstance(revision_count, int)
        or isinstance(revision_count, bool)
        or revision_count < 0
    ):
        raise ValueError("revision_count must be a non-negative integer")
    row = _cost_row(metrics, collection, item_id)
    if row.get("completed") is True:
        raise ValueError(f"cost row is already completed: {collection}.{item_id}")
    row["input_bytes"] = input_bytes
    row["duration_seconds"] = float(duration_seconds)
    row["defects_detected"] = defects_detected
    row["completed"] = True
    if collection == "stages":
        row["revision_count"] = revision_count
        metrics["total_revisions"] = sum(
            int(item.get("revision_count", 0))
            for item in metrics["stages"]
            if isinstance(item, dict)
        )


def begin_additional_cycle(manifest: dict[str, Any]) -> None:
    metrics = manifest.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("workflow manifest has no cost metrics")
    metrics["total_cycles"] = int(metrics.get("total_cycles", 0)) + 1


def finalize_cost_metrics(
    manifest: dict[str, Any], *, now: datetime | None = None
) -> None:
    metrics = manifest.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("workflow manifest has no cost metrics")
    completed = now or datetime.now(timezone.utc)
    started = datetime.fromisoformat(str(manifest["started_at"]).replace("Z", "+00:00"))
    metrics["completed_at"] = guard._format_time(completed)
    metrics["total_duration_seconds"] = max(
        0.0, (completed - started).total_seconds()
    )


def next_stage_request(manifest: dict[str, Any]) -> dict[str, Any] | None:
    orchestrator = manifest.get("orchestrator")
    state = manifest.get("orchestrator_state")
    if not isinstance(orchestrator, dict) or not isinstance(state, dict):
        raise ValueError("workflow manifest has no orchestrator state")
    stages = orchestrator.get("stages")
    index = state.get("next_stage_index")
    if not isinstance(stages, list) or not isinstance(index, int):
        raise ValueError("orchestrator stage state is invalid")
    if index >= len(stages):
        return None
    stage = dict(stages[index])
    run_id = str(manifest["run_id"])
    stage["output_paths"] = [
        str(path).replace("{run_id}", run_id) for path in stage["output_paths"]
    ]
    if stage.get("input_packet_path"):
        stage["input_packet_path"] = str(stage["input_packet_path"]).replace(
            "{run_id}", run_id
        )
    return stage


REVIEW_STAGES = {"checker_passes", "cold_review", "final_blind", "final_review"}


def _entry_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :])
    return text


def _review_output_metadata(
    stage: str,
    manifest: dict[str, Any],
    entry: Path,
    specification_files: list[str],
    *,
    repo_root: Path,
) -> dict[str, Any]:
    run_id = str(manifest["run_id"])
    slug = entry.stem
    identity = "blind" if stage in {"final_blind", "final_review"} else "cold"
    schema_versions = {
        "cold_review": "cold_review_v1",
        "final_blind": "final_blind_v2",
        "final_review": "final_review_v2",
    }
    input_artifacts = {
        "cold_review": ["entry_body", "cold_review_prompt"],
        "final_blind": ["entry_body", "final_blind_prompt"],
        "final_review": [
            "entry_body",
            "sealed_final_blind",
            "pre_blind_resolution",
            "post_blind_resolution",
            "checker_recheck_manifest",
            "targeted_adjudications",
            "final_review_spec",
        ],
    }
    prompt_bytes = b"\n\n".join(
        (repo_root / path).read_bytes() for path in specification_files
    )
    metadata: dict[str, Any] = {
        "schema_version": schema_versions[stage],
        "stage": stage,
        "run_id": f"{identity}-{slug}-{run_id}",
        "context_id": f"{identity}-{slug}-context-{run_id}",
        "input_body_sha256": hashlib.sha256(
            _entry_body(entry).encode("utf-8")
        ).hexdigest(),
        "prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
        "input_artifacts": input_artifacts[stage],
    }
    if stage in {"cold_review", "final_blind"}:
        metadata["audit_visible"] = False
    return metadata


def _normal_review_metadata(
    manifest: dict[str, Any], entry: Path, *, repo_root: Path
) -> dict[str, Any]:
    run_id = str(manifest["run_id"])
    slug = entry.stem
    return {
        "schema_version": "normal_review_v2",
        "stage": "normal_review",
        "run_id": f"normal-{slug}-{run_id}",
        "context_id": f"normal-{slug}-context-{run_id}",
        "input_body_sha256": hashlib.sha256(
            _entry_body(entry).encode("utf-8")
        ).hexdigest(),
        "prompt_sha256": hashlib.sha256(
            (repo_root / DEFAULT_CHECK_SPEC).read_bytes()
        ).hexdigest(),
        "input_artifacts": ["router_selected_sections", "checker_pass_specs"],
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


def prepare_review_inputs(
    manifest: dict[str, Any], *, repo_root: Path = REPO_ROOT
) -> tuple[list[Path], dict[str, Any]]:
    """Materialize the immutable JSON packets used by API or handoff review."""
    request = next_stage_request(manifest)
    if request is None or request.get("name") not in REVIEW_STAGES:
        raise ValueError("next stage is not a review stage")
    stage = str(request["name"])
    entry = repo_root / str(manifest["entry_path"])
    if not entry.is_file():
        raise ValueError(f"entry is missing: {entry}")
    output_paths = [repo_root / str(value) for value in request["output_paths"]]
    cycle_dir = (
        output_paths[-1].parent
        if stage == "checker_passes"
        else output_paths[0].parent
    )
    if stage == "checker_passes":
        check_dir = cycle_dir / "check_passes"
        source_inventory_path = cycle_dir / "source_inventory.json"
        source_inventory: dict[str, Any] | None = None
        if source_inventory_path.is_file():
            source_inventory = json.loads(
                source_inventory_path.read_text(encoding="utf-8")
            )
        guarded_new_run = manifest.get("status") in {
            "in_progress",
            "completed",
            "budget_exhausted",
        } and manifest.get("orchestrator", {}).get(
            "workflow_contract_version"
        ) == WORKFLOW_CONTRACT_VERSION
        if guarded_new_run and source_inventory is None:
            raise ValueError(
                "source-first artifact is required before checker requests are built"
            )
        bundles = check_passes.build_bundles(
            entry,
            repo_root=repo_root,
            blind_seed=str(manifest["run_id"]),
            source_inventory=source_inventory,
            require_evidence_context=guarded_new_run,
        )
        paths = check_passes.write_bundles(bundles, check_dir)
        alignment = check_passes.build_example_attribution_alignment_key(
            entry, repo_root=repo_root, blind_seed=str(manifest["run_id"])
        )
        alignment_path = check_dir / "example-attribution.alignment-key.json"
        alignment_path.write_text(
            json.dumps(alignment, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        antonym_alignment = check_passes.build_antonym_axis_alignment_key(
            entry, repo_root=repo_root, blind_seed=str(manifest["run_id"])
        )
        antonym_alignment_path = (
            check_dir / "frame-relation.antonym-axis.alignment-key.json"
        )
        antonym_alignment_path.write_text(
            json.dumps(antonym_alignment, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return [
            *paths,
            alignment_path,
            antonym_alignment_path,
        ], {"stage": stage, "requests": bundles}

    packet: dict[str, Any] = {
        "stage": stage,
        "entry_body": _entry_body(entry),
        "_output_metadata": _review_output_metadata(
            stage,
            manifest,
            entry,
            list(request.get("specification_files", [])),
            repo_root=repo_root,
        ),
    }
    if stage == "final_review":
        for name in (
            "pass_findings.json",
            "cold_review.json",
            "final_blind.json",
            "blind_seal.json",
            "pre_blind_resolution.json",
            "pre_blind_revision.json",
            "checker_recheck_manifest.json",
            "post_blind_resolution.json",
            "post_blind_verification.json",
            "targeted_adjudications.json",
        ):
            path = cycle_dir / name
            if path.is_file():
                packet[name.removesuffix(".json")] = json.loads(
                    path.read_text(encoding="utf-8")
                )
        seal = packet.get("blind_seal")
        if isinstance(seal, dict) and seal.get("blind_output_sha256"):
            packet["_output_metadata"]["blind_output_sha256"] = seal[
                "blind_output_sha256"
            ]
    packet_path = cycle_dir / f"{stage}.request.json"
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return [packet_path], packet


def prepare_handoff(
    manifest: dict[str, Any], *, repo_root: Path = REPO_ROOT
) -> Path:
    request = next_stage_request(manifest)
    if request is None or request.get("name") not in REVIEW_STAGES:
        raise ValueError("next stage is not a review handoff stage")
    if request.get("reviewer_mode") != "handoff":
        raise ValueError("review handoff is only available in handoff mode")
    stage = str(request["name"])
    output_paths = [repo_root / str(value) for value in request["output_paths"]]
    cycle_dir = (
        output_paths[-1].parent
        if stage == "checker_passes"
        else output_paths[0].parent
    )
    if stage == "checker_passes":
        checkpoint = cycle_dir / "check_passes" / "checker_passes.stage1.json"
        stage2_request_path = (
            cycle_dir
            / "check_passes"
            / "frame-relation.antonym-axis.stage2.request.json"
        )
        if checkpoint.is_file():
            if not stage2_request_path.is_file():
                raise ValueError(
                    "process defect: checker stage 1 checkpoint has no stage 2 request"
                )
            packet = json.loads(stage2_request_path.read_text(encoding="utf-8"))
            prompt_text = (
                repo_root / "prompts" / "check_pass_frame_relation_v7.md"
            ).read_text(encoding="utf-8")
            handoff_path = (
                cycle_dir / "handoff" / "checker_passes.stage2.request.md"
            )
            handoff_path.parent.mkdir(parents=True, exist_ok=True)
            handoff_path.write_text(
                "# Independent review handoff\n\n"
                "Stage: `checker_passes/frame-relation-antonym-axis-stage2`\n\n"
                "The response must be one `antonym_axis_adjudication_record_v1` "
                "JSON object and must be saved as "
                "`checker_passes.stage2.response.json`.\n\n"
                "## Prompt\n\n"
                f"{prompt_text}\n\n"
                "## Input packet\n\n```json\n"
                + json.dumps(packet, ensure_ascii=False, indent=2)
                + "\n```\n",
                encoding="utf-8",
            )
            return handoff_path
    _, packet = prepare_review_inputs(manifest, repo_root=repo_root)
    if stage == "checker_passes":
        prompt_text = "\n\n".join(
            (repo_root / str(item["specification"])).read_text(encoding="utf-8")
            for item in manifest["orchestrator"].get("checker_passes", [])
        )
    else:
        prompt_text = "\n\n".join(
            (repo_root / value).read_text(encoding="utf-8")
            for value in request.get("specification_files", [])
        )
    handoff_path = repo_root / str(request["input_packet_path"])
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(
        "# Independent review handoff\n\n"
        f"Stage: `{stage}`\n\n"
        "The response must be one JSON object matching the supplied review schema. "
        "Create it in a separate model session; do not use the generation session.\n\n"
        "## Prompt\n\n"
        f"{prompt_text}\n\n"
        "## Input packet\n\n```json\n"
        + json.dumps(packet, ensure_ascii=False, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )
    return handoff_path


def ingest_handoff_review(
    manifest: dict[str, Any],
    *,
    stage: str,
    declared_model: str,
    reviewer_agent_id: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> Path:
    request = next_stage_request(manifest)
    if request is None or request.get("name") != stage:
        raise ValueError(f"next stage is not {stage}")
    if stage not in REVIEW_STAGES or request.get("reviewer_mode") != "handoff":
        raise ValueError("review ingestion requires a handoff review stage")
    if not declared_model.strip():
        raise ValueError("handoff ingestion requires the independently used model name")
    output_paths = [repo_root / str(value) for value in request["output_paths"]]
    cycle_dir = output_paths[-1].parent if stage == "checker_passes" else output_paths[0].parent
    checker_checkpoint = (
        cycle_dir / "check_passes" / "checker_passes.stage1.json"
        if stage == "checker_passes"
        else None
    )
    checker_stage2 = bool(
        checker_checkpoint is not None and checker_checkpoint.is_file()
    )
    response_path = (
        cycle_dir / "handoff" / "checker_passes.stage2.response.json"
        if checker_stage2
        else cycle_dir / "handoff" / f"{stage}.response.json"
    )
    if not response_path.is_file():
        raise ValueError(f"handoff response is missing: {response_path}")
    value = json.loads(response_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("handoff response must be a JSON object")
    agent_id = (reviewer_agent_id or "").strip()
    reviewer = {
        "mode": "handoff",
        "declared_model": declared_model.strip(),
        "ingested_by": "human",
    }
    if agent_id:
        reviewer["agent_id"] = agent_id
    entry = repo_root / str(manifest["entry_path"])
    front, _ = validate_entry._split_front_matter(entry.read_text(encoding="utf-8"))
    generation_model = validate_entry._front_matter_values(front or []).get("model", "")
    same_model = review_liveness.normalize_text(declared_model) == review_liveness.normalize_text(
        generation_model
    )
    if same_model:
        if not agent_id:
            raise ValueError(
                "same-model handoff review requires reviewer_agent_id to prove independent-agent provenance"
            )
        reviewer["same_model_as_generation"] = True
    value["reviewer"] = reviewer
    liveness_errors: list[str] = []
    if stage == "checker_passes":
        router = check_passes.load_router(repo_root / DEFAULT_CHECK_SPEC)
        check_dir = cycle_dir / "check_passes"
        attr_request = json.loads(
            (check_dir / "example-attribution.request.json").read_text(encoding="utf-8")
        )
        alignment = json.loads(
            (check_dir / "example-attribution.alignment-key.json").read_text(encoding="utf-8")
        )
        antonym_request = json.loads(
            (check_dir / "frame-relation.request.json").read_text(encoding="utf-8")
        )
        antonym_alignment = json.loads(
            (
                check_dir / "frame-relation.antonym-axis.alignment-key.json"
            ).read_text(encoding="utf-8")
        )
        blind_record_path = (
            check_dir / "frame-relation.antonym-axis.blind-record.json"
        )
        stage2_request_path = (
            check_dir / "frame-relation.antonym-axis.stage2.request.json"
        )
        if not checker_stage2:
            value.update(_normal_review_metadata(manifest, entry, repo_root=repo_root))
            value.setdefault("independent_candidates", [])
            value.setdefault(
                "summary", "Independent checker stage 1 ingested by handoff."
            )
            outputs = value.get("pass_outputs")
            if not isinstance(outputs, list):
                raise ValueError("checker handoff response requires pass_outputs")
            expected_passes = {item["id"] for item in router["passes"]}
            actual_passes = {
                str(item.get("pass_id"))
                for item in outputs
                if isinstance(item, dict)
            }
            if actual_passes != expected_passes or len(outputs) != len(expected_passes):
                raise ValueError("checker handoff must cover every routed pass exactly once")
            for index, output in enumerate(outputs):
                if not isinstance(output, dict):
                    raise ValueError("checker pass output must be an object")
                output["reviewer"] = reviewer
                pass_id = output.get("pass_id")
                if pass_id == "frame-relation":
                    blind_record = output.get("antonym_axis_blind_record")
                    if not isinstance(blind_record, dict):
                        raise ValueError(
                            "frame-relation handoff stage 1 requires "
                            "antonym_axis_blind_record"
                        )
                    blind_record["reviewer"] = reviewer
                    blind_record = check_passes.bind_antonym_axis_blind_record(
                        blind_record, antonym_request
                    )
                    output["antonym_axis_blind_record"] = blind_record
                    blind_errors = check_passes.validate_antonym_axis_blind_record(
                        blind_record,
                        antonym_request,
                        generation_model=generation_model,
                    )
                    if blind_errors:
                        raise ValueError(
                            "frame-relation stage 1: " + "; ".join(blind_errors)
                        )
                    blind_record_path.write_text(
                        json.dumps(blind_record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    continue
                record = output.get("blind_attribution_record")
                if isinstance(record, dict):
                    record["reviewer"] = reviewer
                if pass_id == "example-attribution":
                    if not isinstance(record, dict):
                        raise ValueError(
                            "example-attribution handoff requires blind_attribution_record"
                        )
                    output = check_passes.reconcile_example_attribution(
                        attr_request,
                        record,
                        alignment,
                        aligned_at=datetime.now(timezone.utc).isoformat(),
                    )
                    outputs[index] = output
                errors = check_passes.validate_pass_output(
                    output,
                    router,
                    entry_path=entry,
                    repo_root=repo_root,
                    example_request=attr_request,
                    alignment_key=alignment,
                    generation_model=generation_model,
                )
                if errors:
                    raise ValueError(
                        f"pass output {pass_id}: " + "; ".join(errors)
                    )
            stage2_request = check_passes.materialize_antonym_axis_stage2_request(
                entry,
                antonym_request,
                blind_record_path,
                antonym_alignment,
                repo_root=repo_root,
            )
            stage2_request_path.write_text(
                json.dumps(stage2_request, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            assert checker_checkpoint is not None
            checker_checkpoint.write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return prepare_handoff(manifest, repo_root=repo_root)

        assert checker_checkpoint is not None
        checkpoint = json.loads(checker_checkpoint.read_text(encoding="utf-8"))
        outputs = checkpoint.get("pass_outputs")
        if not isinstance(outputs, list):
            raise ValueError("checker stage 1 checkpoint has no pass_outputs")
        blind_record = json.loads(blind_record_path.read_text(encoding="utf-8"))
        stage2_request = json.loads(stage2_request_path.read_text(encoding="utf-8"))
        value["reviewer"] = reviewer
        value = check_passes.bind_antonym_axis_adjudication_record(
            value, stage2_request, blind_record
        )
        adjudication_path = (
            check_dir / "frame-relation.antonym-axis.adjudication-record.json"
        )
        output = check_passes.reconcile_antonym_axis(
            antonym_request,
            blind_record,
            stage2_request,
            value,
            antonym_alignment,
            aligned_at=datetime.now(timezone.utc).isoformat(),
            generation_model=generation_model,
        )
        adjudication_path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        for index, candidate in enumerate(outputs):
            if isinstance(candidate, dict) and candidate.get("pass_id") == "frame-relation":
                outputs[index] = output
                break
        else:
            raise ValueError("checker stage 1 checkpoint has no frame-relation output")
        errors = check_passes.validate_pass_output(
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
        value = checkpoint
        value["pass_outputs"] = outputs
        value["reviewer"] = reviewer
        value["summary"] = "Independent checker passes completed by two-stage handoff."
        target = output_paths[-1]
    else:
        request_packet_path = cycle_dir / f"{stage}.request.json"
        if not request_packet_path.is_file():
            raise ValueError(f"review request is missing: {request_packet_path}")
        request_packet = json.loads(
            request_packet_path.read_text(encoding="utf-8")
        )
        metadata = request_packet.get("_output_metadata")
        if not isinstance(metadata, dict):
            raise ValueError("review request has no output metadata")
        value.update(metadata)
        value["recorded_at"] = datetime.now(timezone.utc).isoformat()
        value["reviewer"] = reviewer
        errors = review_liveness.validate_reviewer(
            value.get("reviewer"), generation_model=generation_model
        )
        if stage == "cold_review":
            liveness_errors.extend(
                review_liveness.validate_finding_liveness(
                    value, field="findings", label="cold review findings"
                )
            )
        elif stage == "final_blind":
            liveness_errors.extend(
                review_liveness.validate_finding_liveness(
                    value, field="article_findings", label="final blind findings"
                )
            )
            liveness_errors.extend(
                review_liveness.validate_candidate_liveness(
                    value, label="final blind candidates"
                )
            )
        elif stage == "final_review":
            targets = content_audit.extract_targets(entry)
            relations = content_audit.extract_relations(targets)
            liveness_errors.extend(
                review_liveness.validate_final_review_liveness(
                    value,
                    target_quotes={
                        str(item["id"]): str(item.get("text", ""))
                        for item in targets
                    },
                    relation_quotes={
                        str(item["id"]): str(item.get("description", ""))
                        for item in relations
                    },
                )
            )
        if errors or liveness_errors:
            raise ValueError("; ".join([*errors, *liveness_errors]))
        target = output_paths[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return target


def execute_api_review_stage(
    manifest: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    endpoint: str | None = None,
) -> list[Path]:
    """Call, validate, and mechanically assemble the next API review stage."""
    request = next_stage_request(manifest)
    if request is None or request.get("name") not in REVIEW_STAGES:
        raise ValueError("next stage is not an API review stage")
    if request.get("reviewer_mode") != "api":
        raise ValueError("API review execution requires reviewer mode api")

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
    if resolved_provider not in review_call.SUPPORTED_PROVIDERS:
        raise ValueError(
            "DICT_REVIEW_PROVIDER must be one of "
            f"{sorted(review_call.SUPPORTED_PROVIDERS)}"
        )
    if not resolved_model or not resolved_key:
        raise ValueError(
            "API review requires DICT_REVIEW_MODEL and DICT_REVIEW_API_KEY"
        )

    stage = str(request["name"])
    entry = repo_root / str(manifest["entry_path"])
    front, _ = validate_entry._split_front_matter(entry.read_text(encoding="utf-8"))
    generation_model = validate_entry._front_matter_values(front or []).get(
        "model", ""
    )
    output_paths = [repo_root / str(value) for value in request["output_paths"]]
    cycle_dir = (
        output_paths[-1].parent
        if stage == "checker_passes"
        else output_paths[0].parent
    )
    _, packet = prepare_review_inputs(manifest, repo_root=repo_root)

    if stage == "checker_passes":
        check_dir = cycle_dir / "check_passes"
        router = check_passes.load_router(repo_root / DEFAULT_CHECK_SPEC)
        alignment_path = check_dir / "example-attribution.alignment-key.json"
        alignment = json.loads(alignment_path.read_text(encoding="utf-8"))
        antonym_alignment_path = (
            check_dir / "frame-relation.antonym-axis.alignment-key.json"
        )
        antonym_alignment = json.loads(
            antonym_alignment_path.read_text(encoding="utf-8")
        )
        pass_outputs: list[dict[str, Any]] = []
        created: list[Path] = []
        for bundle in packet["requests"]:
            pass_id = str(bundle["pass_id"])
            request_path = check_dir / f"{pass_id}.request.json"
            prompt_path = repo_root / str(bundle["specification"])
            final_path = check_dir / f"{pass_id}.json"
            if pass_id == "frame-relation":
                blind_record_path = (
                    check_dir / "frame-relation.antonym-axis.blind-record.json"
                )
                blind_record = review_call.execute_review(
                    stage="checker-frame-relation-antonym-axis-stage1",
                    request_path=request_path,
                    prompt_path=prompt_path,
                    cycle_dir=cycle_dir,
                    output_path=blind_record_path,
                    provider=resolved_provider,
                    model=resolved_model,
                    api_key=resolved_key,
                    endpoint=resolved_endpoint,
                    generation_model=generation_model,
                )
                blind_record = check_passes.bind_antonym_axis_blind_record(
                    blind_record, bundle
                )
                blind_record_path.write_text(
                    json.dumps(blind_record, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                blind_errors = check_passes.validate_antonym_axis_blind_record(
                    blind_record,
                    bundle,
                    generation_model=generation_model,
                )
                if blind_errors:
                    raise ValueError(
                        "API pass output frame-relation stage 1: "
                        + "; ".join(blind_errors)
                    )
                stage2_request = check_passes.materialize_antonym_axis_stage2_request(
                    entry,
                    bundle,
                    blind_record_path,
                    antonym_alignment,
                    repo_root=repo_root,
                )
                stage2_request_path = (
                    check_dir / "frame-relation.antonym-axis.stage2.request.json"
                )
                stage2_request_path.write_text(
                    json.dumps(stage2_request, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                adjudication_path = (
                    check_dir
                    / "frame-relation.antonym-axis.adjudication-record.json"
                )
                adjudication = review_call.execute_review(
                    stage="checker-frame-relation-antonym-axis-stage2",
                    request_path=stage2_request_path,
                    prompt_path=prompt_path,
                    cycle_dir=cycle_dir,
                    output_path=adjudication_path,
                    provider=resolved_provider,
                    model=resolved_model,
                    api_key=resolved_key,
                    endpoint=resolved_endpoint,
                    generation_model=generation_model,
                )
                adjudication = check_passes.bind_antonym_axis_adjudication_record(
                    adjudication, stage2_request, blind_record
                )
                adjudication_path.write_text(
                    json.dumps(adjudication, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                output = check_passes.reconcile_antonym_axis(
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
                errors = check_passes.validate_pass_output(
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
                    raise ValueError(
                        "API pass output frame-relation: " + "; ".join(errors)
                    )
                pass_outputs.append(output)
                created.extend(
                    [blind_record_path, adjudication_path, final_path]
                )
                continue
            model_output_path = (
                check_dir / "example-attribution.blind-record.json"
                if pass_id == "example-attribution"
                else final_path
            )
            model_output = review_call.execute_review(
                stage=f"checker-{pass_id}",
                request_path=request_path,
                prompt_path=prompt_path,
                cycle_dir=cycle_dir,
                output_path=model_output_path,
                provider=resolved_provider,
                model=resolved_model,
                api_key=resolved_key,
                endpoint=resolved_endpoint,
                generation_model=generation_model,
            )
            if pass_id == "example-attribution":
                output = check_passes.reconcile_example_attribution(
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
            errors = check_passes.validate_pass_output(
                output,
                router,
                entry_path=entry,
                repo_root=repo_root,
                example_request=(
                    bundle if pass_id == "example-attribution" else None
                ),
                request_payload=bundle,
                alignment_key=(
                    alignment if pass_id == "example-attribution" else None
                ),
                generation_model=generation_model,
            )
            if errors:
                raise ValueError(f"API pass output {pass_id}: " + "; ".join(errors))
            pass_outputs.append(output)
            created.append(final_path)

        normal_review = {
            **_normal_review_metadata(manifest, entry, repo_root=repo_root),
            "pass_outputs": pass_outputs,
            "independent_candidates": [],
            "summary": "Independent checker passes completed through the review API.",
        }
        pass_findings_path = cycle_dir / "pass_findings.json"
        pass_findings_path.write_text(
            json.dumps(normal_review, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return [*created, pass_findings_path]

    request_path = cycle_dir / f"{stage}.request.json"
    prompt_files = list(request.get("specification_files", []))
    if len(prompt_files) != 1:
        raise ValueError(f"API review stage {stage} requires exactly one prompt")
    output = review_call.execute_review(
        stage=stage,
        request_path=request_path,
        prompt_path=repo_root / str(prompt_files[0]),
        cycle_dir=cycle_dir,
        output_path=output_paths[0],
        provider=resolved_provider,
        model=resolved_model,
        api_key=resolved_key,
        endpoint=resolved_endpoint,
        generation_model=generation_model,
    )
    errors = review_liveness.validate_reviewer(
        output.get("reviewer"), generation_model=generation_model
    )
    errors.extend(
        review_liveness.validate_api_request_binding(
            output.get("reviewer"), packet
        )
    )
    if stage == "cold_review":
        errors.extend(
            review_liveness.validate_finding_liveness(
                output, field="findings", label="cold review findings"
            )
        )
    elif stage == "final_blind":
        errors.extend(
            review_liveness.validate_finding_liveness(
                output, field="article_findings", label="final blind findings"
            )
        )
        errors.extend(
            review_liveness.validate_candidate_liveness(
                output, label="final blind candidates"
            )
        )
    else:
        targets = content_audit.extract_targets(entry)
        relations = content_audit.extract_relations(targets)
        errors.extend(
            review_liveness.validate_final_review_liveness(
                output,
                target_quotes={
                    str(item["id"]): str(item.get("text", ""))
                    for item in targets
                },
                relation_quotes={
                    str(item["id"]): str(item.get("description", ""))
                    for item in relations
                },
            )
        )
    if errors:
        raise ValueError(f"API review output {stage}: " + "; ".join(errors))
    return [output_paths[0]]


def match_acceptance_defects(
    expected: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    frame_errors: list[str],
) -> list[dict[str, Any]]:
    """Apply the fixed §5 acceptance mapping without relaxing stage ownership."""
    results: list[dict[str, Any]] = []
    for defect in expected:
        defect_id = str(defect["id"])
        taxonomy_id = str(defect["taxonomy_id"])
        quotes = [
            str(defect["exact_quote"]),
            *map(str, defect.get("additional_exact_quotes", [])),
        ]
        if defect_id in {"D3", "D4"}:
            detected_quotes = [
                quote for quote in quotes if any(quote in error for error in frame_errors)
            ]
            results.append(
                {
                    "id": defect_id,
                    "detected": len(detected_quotes) == len(quotes),
                    "stages": (
                        ["mechanical:B5"]
                        if len(detected_quotes) == len(quotes)
                        else []
                    ),
                }
            )
            continue

        quote_matches: dict[str, list[dict[str, Any]]] = {}
        for quote in quotes:
            matches = [
                finding
                for finding in findings
                if finding.get("taxonomy_id") == taxonomy_id
                and quote in str(finding.get("location", {}).get("exact_quote", ""))
            ]
            if defect_id in {"D1", "D2"}:
                matches = [
                    finding
                    for finding in matches
                    if finding.get("stage") == "check_pass:example-attribution"
                    and finding.get("severity") == "blocking"
                ]
            quote_matches[quote] = matches
        matched = [item for values in quote_matches.values() for item in values]
        results.append(
            {
                "id": defect_id,
                "detected": all(quote_matches.values()),
                "stages": sorted({str(item["stage"]) for item in matched}),
            }
        )
    return results


def run_yield_acceptance(*, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    provider = os.environ.get("DICT_REVIEW_PROVIDER", "openai").strip().lower()
    model = os.environ.get("DICT_REVIEW_MODEL", "").strip()
    api_key = os.environ.get("DICT_REVIEW_API_KEY", "").strip()
    endpoint = os.environ.get("DICT_REVIEW_ENDPOINT", "").strip() or None
    if not model or not api_key:
        raise ValueError(
            "yield acceptance requires DICT_REVIEW_MODEL and DICT_REVIEW_API_KEY"
        )
    fixture = repo_root / "tests" / "fixtures" / "acceptance" / "yield_defective.md"
    expected_path = (
        repo_root
        / "tests"
        / "fixtures"
        / "acceptance"
        / "yield_defective_expected.json"
    )
    if not fixture.is_file() or not expected_path.is_file():
        raise ValueError("yield acceptance fixtures are missing")
    front, body = validate_entry._split_front_matter(
        fixture.read_text(encoding="utf-8")
    )
    generation_model = validate_entry._front_matter_values(front or []).get("model", "")
    if review_liveness.normalize_text(model) == review_liveness.normalize_text(
        generation_model
    ):
        raise ValueError("acceptance reviewer model must differ from generation model")

    run_id = datetime.now(timezone.utc).strftime("acceptance-%Y%m%dT%H%M%SZ")
    cycle_dir = repo_root / "audits" / "runs" / "y" / "yield" / run_id
    check_dir = cycle_dir / "check_passes"
    bundles = check_passes.build_bundles(
        fixture, repo_root=repo_root, blind_seed=run_id
    )
    check_passes.write_bundles(bundles, check_dir)
    alignment = check_passes.build_example_attribution_alignment_key(
        fixture, repo_root=repo_root, blind_seed=run_id
    )
    alignment_path = check_dir / "example-attribution.alignment-key.json"
    alignment_path.write_text(
        json.dumps(alignment, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    antonym_alignment = check_passes.build_antonym_axis_alignment_key(
        fixture, repo_root=repo_root, blind_seed=run_id
    )
    (
        check_dir / "frame-relation.antonym-axis.alignment-key.json"
    ).write_text(
        json.dumps(antonym_alignment, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    router = check_passes.load_router(repo_root / DEFAULT_CHECK_SPEC)
    pass_outputs: list[dict[str, Any]] = []
    for bundle in bundles:
        pass_id = str(bundle["pass_id"])
        request_path = check_dir / f"{pass_id}.request.json"
        prompt_path = repo_root / str(bundle["specification"])
        if pass_id == "frame-relation":
            blind_record_path = (
                check_dir / "frame-relation.antonym-axis.blind-record.json"
            )
            blind_record = review_call.execute_review(
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
            blind_record = check_passes.bind_antonym_axis_blind_record(
                blind_record, bundle
            )
            blind_record_path.write_text(
                json.dumps(blind_record, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            stage2_request = check_passes.materialize_antonym_axis_stage2_request(
                fixture,
                bundle,
                blind_record_path,
                antonym_alignment,
                repo_root=repo_root,
            )
            stage2_request_path = (
                check_dir / "frame-relation.antonym-axis.stage2.request.json"
            )
            stage2_request_path.write_text(
                json.dumps(stage2_request, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            adjudication = review_call.execute_review(
                stage="checker-frame-relation-antonym-axis-stage2",
                request_path=stage2_request_path,
                prompt_path=prompt_path,
                cycle_dir=cycle_dir,
                output_path=(
                    check_dir
                    / "frame-relation.antonym-axis.adjudication-record.json"
                ),
                provider=provider,
                model=model,
                api_key=api_key,
                endpoint=endpoint,
                generation_model=generation_model,
            )
            adjudication = check_passes.bind_antonym_axis_adjudication_record(
                adjudication, stage2_request, blind_record
            )
            (
                check_dir
                / "frame-relation.antonym-axis.adjudication-record.json"
            ).write_text(
                json.dumps(adjudication, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            output = check_passes.reconcile_antonym_axis(
                bundle,
                blind_record,
                stage2_request,
                adjudication,
                antonym_alignment,
                aligned_at=datetime.now(timezone.utc).isoformat(),
                generation_model=generation_model,
            )
            errors = check_passes.validate_pass_output(
                output,
                router,
                entry_path=fixture,
                repo_root=repo_root,
                antonym_request=bundle,
                antonym_stage2_request=stage2_request,
                antonym_alignment_key=antonym_alignment,
                request_payload=stage2_request,
                generation_model=generation_model,
            )
            if errors:
                raise ValueError(f"acceptance {pass_id}: " + "; ".join(errors))
            pass_outputs.append(output)
            continue
        raw_output = review_call.execute_review(
            stage=f"checker-{pass_id}",
            request_path=request_path,
            prompt_path=prompt_path,
            cycle_dir=cycle_dir,
            output_path=check_dir / f"{pass_id}.response.json",
            provider=provider,
            model=model,
            api_key=api_key,
            endpoint=endpoint,
            generation_model=generation_model,
        )
        if pass_id == "example-attribution":
            output = check_passes.reconcile_example_attribution(
                bundle,
                raw_output,
                alignment,
                aligned_at=datetime.now(timezone.utc).isoformat(),
            )
        else:
            output = raw_output
        errors = check_passes.validate_pass_output(
            output,
            router,
            entry_path=fixture,
            repo_root=repo_root,
            example_request=bundle if pass_id == "example-attribution" else None,
            request_payload=bundle,
            alignment_key=alignment if pass_id == "example-attribution" else None,
            generation_model=generation_model,
        )
        if errors:
            raise ValueError(f"acceptance {pass_id}: " + "; ".join(errors))
        pass_outputs.append(output)

    body_text = "\n".join(body.splitlines())
    stage_outputs: dict[str, dict[str, Any]] = {}
    for stage, prompt_name in (
        ("cold_review", "prompts/cold_review_prompt_v1.md"),
        ("final_blind", DEFAULT_FINAL_BLIND_SPEC),
    ):
        request_path = cycle_dir / f"{stage}.request.json"
        request_path.write_text(
            json.dumps(
                {"stage": stage, "entry_body": body_text},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        stage_outputs[stage] = review_call.execute_review(
            stage=stage,
            request_path=request_path,
            prompt_path=repo_root / prompt_name,
            cycle_dir=cycle_dir,
            output_path=cycle_dir / f"{stage}.json",
            provider=provider,
            model=model,
            api_key=api_key,
            endpoint=endpoint,
            generation_model=generation_model,
        )

    (cycle_dir / "pass_findings.json").write_text(
        json.dumps({"pass_outputs": pass_outputs}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    liveness_errors: list[str] = []
    attribution_output = next(
        item for item in pass_outputs if item.get("pass_id") == "example-attribution"
    )
    attribution_request = next(
        item for item in bundles if item.get("pass_id") == "example-attribution"
    )
    liveness_errors.extend(
        review_liveness.validate_attribution_liveness(
            attribution_output.get("blind_attribution_record"),
            attribution_request,
            alignment_key=alignment,
        )
    )
    liveness_errors.extend(
        review_liveness.validate_finding_liveness(
            stage_outputs["cold_review"],
            field="findings",
            label="cold review findings",
        )
    )
    liveness_errors.extend(
        review_liveness.validate_finding_liveness(
            stage_outputs["final_blind"],
            field="article_findings",
            label="final blind findings",
        )
    )
    liveness_errors.extend(
        review_liveness.validate_candidate_liveness(
            stage_outputs["final_blind"], label="final blind candidates"
        )
    )
    liveness_errors.extend(
        review_liveness.zero_finding_run_errors(
            {"pass_outputs": pass_outputs},
            stage_outputs["cold_review"],
            stage_outputs["final_blind"],
        )
    )
    invalidated_by = review_liveness.invalidation_ids(liveness_errors)

    all_findings = [
        {**finding, "stage": f"check_pass:{output['pass_id']}"}
        for output in pass_outputs
        for finding in output.get("findings", [])
    ]
    all_findings.extend(
        {**finding, "stage": "cold_review"}
        for finding in stage_outputs["cold_review"].get("findings", [])
    )
    all_findings.extend(
        {**finding, "stage": "final_blind"}
        for finding in stage_outputs["final_blind"].get("article_findings", [])
    )
    frame_errors, _ = validate_entry.grammar_frame_diagnostics(
        body.splitlines(), "yield"
    )
    expected = json.loads(expected_path.read_text(encoding="utf-8"))["defects"]
    results = match_acceptance_defects(expected, all_findings, frame_errors)
    by_id = {item["id"]: item for item in results}
    mandatory = all(by_id[item]["detected"] for item in ("D1", "D2", "D3", "D4"))
    technical = sum(by_id[item]["detected"] for item in ("D5", "D6", "D7", "D8"))
    report = {
        "run_id": run_id,
        "review_provider": provider,
        "review_model": model,
        "generation_model": generation_model,
        "results": results,
        "technical_detected": technical,
        "invalidated_by": invalidated_by,
        "review_liveness_errors": liveness_errors,
        "passed": mandatory and technical >= 2 and not invalidated_by,
    }
    log_path = repo_root / "logs" / "2026-08-27-acceptance-yield.md"
    log_path.write_text(
        "# Yield review-independence acceptance\n\n"
        f"- Run: `{run_id}`\n"
        f"- Review model: `{model}`\n"
        f"- Generation model: `{generation_model}`\n"
        f"- Result: {'PASS' if report['passed'] else 'FAIL'}\n\n"
        "```json\n"
        + json.dumps(report, ensure_ascii=False, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )
    return report


def complete_orchestrated_stage(
    manifest: dict[str, Any],
    *,
    stage: str,
    input_bytes: int,
    duration_seconds: float,
    defects_detected: int = 0,
    revision_count: int = 0,
    output_paths: list[str] | None = None,
    checker_pass_costs: dict[str, dict[str, Any]] | None = None,
    process_rule_defects: dict[str, int] | None = None,
    now: datetime | None = None,
    repo_root: Path = REPO_ROOT,
    verify_outputs: bool = True,
) -> None:
    request = next_stage_request(manifest)
    if request is None:
        raise ValueError("orchestrator has no remaining stage")
    if request["name"] != stage:
        raise ValueError(f"next orchestrator stage must be {request['name']}")
    expected_outputs = list(request["output_paths"])
    recorded_outputs = list(output_paths or expected_outputs)
    if recorded_outputs != expected_outputs:
        raise ValueError("stage outputs must exactly match the orchestrator plan")
    if verify_outputs:
        missing = [
            path
            for path in expected_outputs
            if not (repo_root / path.rstrip("/")).exists()
        ]
        if missing:
            raise ValueError(
                "stage outputs do not exist: " + ", ".join(missing)
            )
    record_cost(
        manifest,
        collection="stages",
        item_id=stage,
        input_bytes=input_bytes,
        duration_seconds=duration_seconds,
        defects_detected=defects_detected,
        revision_count=revision_count,
    )
    if stage == "generation":
        for row in manifest["metrics"]["process_rules"]:
            if row.get("completed") is True:
                continue
            record_cost(
                manifest,
                collection="process_rules",
                item_id=str(row["id"]),
                input_bytes=0,
                duration_seconds=duration_seconds,
                defects_detected=int((process_rule_defects or {}).get(str(row["id"]), 0)),
            )
    if stage == "checker_passes":
        provided = checker_pass_costs or {}
        expected = {
            str(row["id"]) for row in manifest["metrics"]["checker_passes"]
        }
        if set(provided) != expected:
            raise ValueError(
                "checker_pass_costs must cover every routed pass exactly once"
            )
        for pass_id in sorted(expected):
            cost = provided[pass_id]
            record_cost(
                manifest,
                collection="checker_passes",
                item_id=pass_id,
                input_bytes=int(cost.get("input_bytes", 0)),
                duration_seconds=float(cost.get("duration_seconds", 0.0)),
                defects_detected=int(cost.get("defects_detected", 0)),
            )
    current = now or datetime.now(timezone.utc)
    for checkpoint in request.get("guard_checkpoints", []):
        ok = guard.advance_stage(
            manifest,
            stage=str(checkpoint),
            notes=f"orchestrator completed {stage}",
            now=current,
        )
        if not ok:
            raise RuntimeError(manifest.get("stop_reason", "workflow guard stopped"))
    state = manifest["orchestrator_state"]
    state["completed_stages"].append(stage)
    state["next_stage_index"] = int(state["next_stage_index"]) + 1
    state["stage_outputs"][stage] = expected_outputs
    if stage == "export":
        finalize_cost_metrics(manifest, now=current)


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _current_branch(repo_root: Path) -> str:
    branch = _git(repo_root, "branch", "--show-current")
    if not branch or branch in {"main", "master"}:
        raise ValueError("run_word requires a dedicated non-main branch")
    return branch


def _base_sha(repo_root: Path) -> str:
    try:
        return _git(repo_root, "merge-base", "HEAD", "origin/main")
    except subprocess.CalledProcessError:
        return _git(repo_root, "rev-parse", "HEAD")


def create_guard_manifest(
    headword: str,
    *,
    repo_root: Path = REPO_ROOT,
    branch: str,
    base_sha: str,
    profile: str = "standard",
    reason: str = "",
    run_id: str | None = None,
    now: datetime | None = None,
    reviewer_mode: str = "api",
) -> tuple[Path, dict[str, Any]]:
    manifest = guard.new_manifest(
        headword=headword,
        entry_path=entry_path_for(headword),
        branch=branch,
        base_sha=base_sha,
        profile=profile,
        profile_reason=reason,
        run_id=run_id,
        now=now,
    )
    manifest["orchestrator"] = plan_payload(
        headword, repo_root, reviewer_mode=reviewer_mode
    )
    manifest["metrics"] = initialize_cost_metrics(
        manifest["orchestrator"], repo_root=repo_root
    )
    manifest["orchestrator_state"] = initialize_orchestrator_state(
        manifest["orchestrator"]
    )
    path = (
        repo_root
        / "audits"
        / "workflow_runs"
        / slugify(headword)
        / f"{manifest['run_id']}.json"
    )
    if path.exists():
        raise ValueError(f"workflow run already exists: {path}")
    guard._write(path, manifest)
    return path, manifest


def heartbeat_manifest(
    manifest: dict[str, Any], *, now: datetime | None = None
) -> bool:
    current = now or datetime.now(timezone.utc)
    ok = guard.enforce_budget(manifest, now=current)
    if ok:
        manifest["last_heartbeat_at"] = guard._format_time(current)
    return ok


def _commit_and_push(repo_root: Path, paths: Iterable[Path], message: str) -> str:
    relative = [
        path.resolve().relative_to(repo_root.resolve()).as_posix() for path in paths
    ]
    _git(repo_root, "add", "--", *relative)
    _git(repo_root, "commit", "-m", message)
    sha = _git(repo_root, "rev-parse", "HEAD")
    branch = _current_branch(repo_root)
    _git(repo_root, "push", "-u", "origin", f"HEAD:{branch}")
    return sha


def record_entry_revision(
    entry_path: Path,
    reason: str,
    *,
    repo_root: Path = REPO_ROOT,
    push: bool = True,
) -> str:
    resolved = entry_path.resolve()
    try:
        relative = resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("entry revision must be inside the repository") from exc
    if not relative.startswith("entries/") or not relative.endswith(".md"):
        raise ValueError("entry revision must target entries/**/*.md")
    if not resolved.is_file():
        raise ValueError(f"entry revision does not exist: {relative}")
    if not reason.strip():
        raise ValueError("entry revision requires a non-empty reason")
    status = _git(repo_root, "status", "--short", "--", relative)
    if not status.strip():
        raise ValueError(f"entry has no uncommitted revision: {relative}")
    _git(repo_root, "add", "--", relative)
    staged = {
        line.strip()
        for line in _git(repo_root, "diff", "--cached", "--name-only").splitlines()
        if line.strip()
    }
    if staged != {relative}:
        _git(repo_root, "restore", "--staged", "--", relative)
        raise ValueError(
            "revision commit must contain exactly one entry; clear other staged files first"
        )
    slug = resolved.stem
    _git(repo_root, "commit", "-m", f"entry({slug}): {reason.strip()}")
    sha = _git(repo_root, "rev-parse", "HEAD")
    if push:
        branch = _current_branch(repo_root)
        _git(repo_root, "push", "-u", "origin", f"HEAD:{branch}")
    return sha


def start_workflow(
    headword: str,
    *,
    repo_root: Path = REPO_ROOT,
    profile: str = "standard",
    reason: str = "",
    reviewer_mode: str = "api",
) -> Path:
    branch = _current_branch(repo_root)
    base = _base_sha(repo_root)
    run_path, manifest = create_guard_manifest(
        headword,
        repo_root=repo_root,
        branch=branch,
        base_sha=base,
        profile=profile,
        reason=reason,
        reviewer_mode=reviewer_mode,
    )
    start_sha = _commit_and_push(
        repo_root,
        (run_path,),
        f"workflow({slugify(headword)}): initialize guarded run",
    )
    if not guard.confirm_remote_checkpoint(
        manifest,
        manifest_path=run_path,
        commit_sha=start_sha,
        repo_root=repo_root,
    ):
        guard._write(run_path, manifest)
        raise RuntimeError(manifest.get("stop_reason", "workflow guard stopped"))
    guard._write(run_path, manifest)
    _commit_and_push(
        repo_root,
        (run_path,),
        f"workflow({slugify(headword)}): confirm remote checkpoint",
    )
    return run_path


def _report_review_failure(
    manifest: dict[str, Any],
    run_path: Path,
    *,
    stage: str,
    error: BaseException,
) -> int:
    """Charge a failed review ingestion to the guard instead of retrying blind.

    Without this the orchestrator raised, the guard was never consulted for the
    failed attempt, and an agent could re-prepare and re-ingest the same broken
    handoff response indefinitely.
    """
    running = guard.record_review_ingest_failure(
        manifest, stage=stage, error=str(error)
    )
    guard._write(run_path, manifest)
    payload = {
        "status": manifest["status"],
        "stage": manifest["stage"],
        "review_stage": stage,
        "error": str(error),
        "ingest_failure_count": manifest.get("review_ingest_failures", {}).get("count"),
    }
    if not running:
        payload["reason"] = manifest.get("stop_reason", "")
        payload["open_questions"] = manifest.get("open_questions", [])
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 2 if not running else 1


def _resume(
    path: Path,
    *,
    ingest_review: str | None = None,
    declared_model: str = "",
    reviewer_agent_id: str = "",
    call_review: bool = False,
) -> int:
    resolved = path.resolve()
    manifest = guard._read(resolved)
    ok = heartbeat_manifest(manifest)
    guard._write(resolved, manifest)
    if not ok:
        print(
            json.dumps(
                {"status": "stopped", "reason": manifest["stop_reason"]},
                ensure_ascii=False,
            )
        )
        return 2
    ingested_path: Path | None = None
    api_review_paths: list[Path] = []
    if ingest_review:
        try:
            ingested_path = ingest_handoff_review(
                manifest,
                stage=ingest_review,
                declared_model=declared_model,
                reviewer_agent_id=reviewer_agent_id or None,
            )
        except Exception as exc:  # the guard owns every failed ingestion
            return _report_review_failure(
                manifest, resolved, stage=ingest_review, error=exc
            )
        guard.clear_review_ingest_failures(manifest)
        guard._write(resolved, manifest)
    elif call_review:
        stage_name = (next_stage_request(manifest) or {}).get("name", "review")
        try:
            api_review_paths = execute_api_review_stage(manifest)
        except Exception as exc:  # the guard owns every failed review call
            return _report_review_failure(
                manifest, resolved, stage=str(stage_name), error=exc
            )
        guard.clear_review_ingest_failures(manifest)
    next_request = next_stage_request(manifest)
    handoff_path: Path | None = None
    review_request_paths: list[Path] = []
    if (
        next_request is not None
        and next_request.get("name") in REVIEW_STAGES
        and not ingest_review
        and not call_review
    ):
        if next_request.get("reviewer_mode") == "handoff":
            handoff_path = prepare_handoff(manifest)
        else:
            review_request_paths, _ = prepare_review_inputs(manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "stage": manifest["stage"],
                "next_stage": next_request,
                "handoff_request": (
                    handoff_path.relative_to(REPO_ROOT).as_posix()
                    if handoff_path is not None
                    else None
                ),
                "review_requests": [
                    path.relative_to(REPO_ROOT).as_posix()
                    for path in review_request_paths
                ],
                "api_review_outputs": [
                    path.relative_to(REPO_ROOT).as_posix()
                    for path in api_review_paths
                ],
                "ingested_review": (
                    ingested_path.relative_to(REPO_ROOT).as_posix()
                    if ingested_path is not None
                    else None
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Orchestrate one dictionary headword")
    parser.add_argument("headword", nargs="?")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", type=Path)
    parser.add_argument(
        "--reviewer-mode", choices=("api", "handoff"), default="api"
    )
    parser.add_argument("--ingest-review", choices=sorted(REVIEW_STAGES))
    parser.add_argument("--call-review", action="store_true")
    parser.add_argument("--declared-model", default="")
    parser.add_argument("--reviewer-agent-id", default="")
    parser.add_argument("--acceptance", action="store_true")
    parser.add_argument("--complete-stage", type=Path)
    parser.add_argument("--stage")
    parser.add_argument("--input-bytes", type=int, default=0)
    parser.add_argument("--duration-seconds", type=float, default=0.0)
    parser.add_argument("--defects-detected", type=int, default=0)
    parser.add_argument("--revision-count", type=int, default=0)
    parser.add_argument("--checker-pass-costs", type=Path)
    parser.add_argument("--record-revision", type=Path)
    parser.add_argument(
        "--profile", choices=sorted(guard.PROFILES), default="standard"
    )
    parser.add_argument("--reason", default="")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.complete_stage:
        if (
            args.headword
            or args.resume
            or args.dry_run
            or args.record_revision
            or args.call_review
        ):
            raise SystemExit(
                "--complete-stage cannot be combined with another workflow selector"
            )
        if not args.stage:
            raise SystemExit("--complete-stage requires --stage")
        resolved = args.complete_stage.resolve()
        manifest = guard._read(resolved)
        pass_costs = None
        if args.checker_pass_costs:
            pass_costs = json.loads(
                args.checker_pass_costs.read_text(encoding="utf-8")
            )
            if not isinstance(pass_costs, dict):
                raise SystemExit("--checker-pass-costs must contain a JSON object")
        complete_orchestrated_stage(
            manifest,
            stage=args.stage,
            input_bytes=args.input_bytes,
            duration_seconds=args.duration_seconds,
            defects_detected=args.defects_detected,
            revision_count=args.revision_count,
            checker_pass_costs=pass_costs,
            repo_root=REPO_ROOT,
        )
        guard._write(resolved, manifest)
        print(json.dumps(next_stage_request(manifest), ensure_ascii=False, indent=2))
        return 0
    if args.record_revision:
        if args.headword or args.resume or args.dry_run or args.call_review:
            raise SystemExit(
                "--record-revision cannot be combined with headword, --resume, or --dry-run"
            )
        print(record_entry_revision(args.record_revision, args.reason))
        return 0
    if args.resume:
        if args.headword or args.dry_run:
            raise SystemExit(
                "--resume cannot be combined with headword or --dry-run"
            )
        if args.ingest_review and args.call_review:
            raise SystemExit("--ingest-review and --call-review are mutually exclusive")
        if args.call_review and (args.declared_model or args.reviewer_agent_id):
            raise SystemExit(
                "--declared-model and --reviewer-agent-id are only used with --ingest-review"
            )
        if args.reviewer_agent_id and not args.ingest_review:
            raise SystemExit("--reviewer-agent-id requires --ingest-review")
        return _resume(
            args.resume,
            ingest_review=args.ingest_review,
            declared_model=args.declared_model,
            reviewer_agent_id=args.reviewer_agent_id,
            call_review=args.call_review,
        )
    if not args.headword:
        raise SystemExit("headword is required")
    if (
        args.call_review
        or args.ingest_review
        or args.declared_model
        or args.reviewer_agent_id
    ):
        raise SystemExit(
            "--call-review, --ingest-review, --declared-model, and --reviewer-agent-id require --resume"
        )
    if args.dry_run:
        print(
            json.dumps(
                plan_payload(
                    args.headword, reviewer_mode=args.reviewer_mode
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.acceptance:
        if args.headword != "yield":
            raise SystemExit("--acceptance is currently scoped to yield")
        if args.reviewer_mode != "api":
            raise SystemExit("yield acceptance requires reviewer mode api")
        try:
            report = run_yield_acceptance()
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["passed"] else 1
    path = start_workflow(
        args.headword,
        profile=args.profile,
        reason=args.reason,
        reviewer_mode=args.reviewer_mode,
    )
    print(path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
