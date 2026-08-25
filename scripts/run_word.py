from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import entry_workflow_guard as guard
import check_passes
import process_improvement
from slugify import slugify


REPO_ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR_VERSION = "run_word_v3"
DEFAULT_CHECK_SPEC = "prompts/check_router_v6.md"
DEFAULT_FINAL_SPEC = "prompts/final_review_spec_v2.md"
DEFAULT_FINAL_BLIND_SPEC = "prompts/final_blind_prompt_v2.md"
COST_SCHEMA_VERSION = "workflow_cost_v1"


@dataclass(frozen=True)
class StagePlan:
    name: str
    executor: str
    specification_files: tuple[str, ...]
    input_scope: tuple[str, ...]
    output_paths: tuple[str, ...]
    guard_checkpoints: tuple[str, ...] = ()
    context_mode: str = "coordinator"

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


def build_plan(
    headword: str,
    *,
    check_spec: str = DEFAULT_CHECK_SPEC,
    final_spec: str = DEFAULT_FINAL_SPEC,
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
        ),
        StagePlan(
            "cold_review",
            "independent_llm",
            ("prompts/cold_review_prompt_v1.md",),
            ("entry body without front matter",),
            (f"{root}/cold_review.json",),
            ("cold_review_complete",),
            "context_free_cold",
        ),
        StagePlan(
            "final_blind",
            "independent_llm",
            (DEFAULT_FINAL_BLIND_SPEC,),
            ("latest entry body only",),
            (f"{root}/final_blind.json",),
            (),
            "context_free_final_blind",
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
            "finding_resolution",
            "llm",
            ("prompts/finding_resolution_v6.md",),
            (
                "latest entry body",
                "all checker and cold findings",
                "sealed final-blind findings",
                "source inventory",
            ),
            (f"{root}/resolutions.json",),
            (),
            "normal_resolution_context",
        ),
        StagePlan(
            "final_review",
            "independent_llm",
            (final_spec,),
            (
                "latest entry body",
                "sealed final-blind output",
                "all checker, cold, and sealed final-blind findings",
                "finding resolution records",
            ),
            (f"{root}/final_review.json", audit),
            ("final_review_complete",),
            "final_reconciliation_context",
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


def plan_payload(headword: str, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    stages = [stage.to_dict(repo_root) for stage in build_plan(headword)]
    encoded = json.dumps(stages, ensure_ascii=False, sort_keys=True).encode("utf-8")
    pass_plans: list[dict[str, Any]] = []
    router_path = repo_root / DEFAULT_CHECK_SPEC
    if router_path.is_file():
        router = check_passes.load_router(router_path)
        for item in router.get("passes", []):
            specification = str(item["specification"])
            specification_path = repo_root / specification
            pass_plans.append(
                {
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
                }
            )
    return {
        "orchestrator_version": ORCHESTRATOR_VERSION,
        "headword": headword,
        "entry_path": entry_path_for(headword),
        "plan_sha256": hashlib.sha256(encoded).hexdigest(),
        "stages": stages,
        "checker_passes": pass_plans,
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
    return stage


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
    manifest["orchestrator"] = plan_payload(headword, repo_root)
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


def _resume(path: Path) -> int:
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
    next_request = next_stage_request(manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "stage": manifest["stage"],
                "next_stage": next_request,
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
        if args.headword or args.resume or args.dry_run or args.record_revision:
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
        if args.headword or args.resume or args.dry_run:
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
        return _resume(args.resume)
    if not args.headword:
        raise SystemExit("headword is required")
    if args.dry_run:
        print(json.dumps(plan_payload(args.headword), ensure_ascii=False, indent=2))
        return 0
    path = start_workflow(
        args.headword,
        profile=args.profile,
        reason=args.reason,
    )
    print(path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
