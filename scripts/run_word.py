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
from slugify import slugify


REPO_ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR_VERSION = "run_word_v1"
DEFAULT_CHECK_SPEC = "prompts/check_router_v6.md"
DEFAULT_FINAL_SPEC = "prompts/final_review_spec_v1.md"


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
            (f"{root}/check_passes/", f"{root}/pass_findings.json"),
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
            (final_spec,),
            ("latest entry only",),
            (f"{root}/final_blind.json",),
            (),
            "context_free_final_blind",
        ),
        StagePlan(
            "blind_seal",
            "python",
            ("scripts/content_audit.py", "scripts/semantic_resolution_gate.py"),
            ("final blind raw JSON", "entry body hash"),
            (f"{root}/blind_seal.json",),
            ("blind_seal_complete",),
        ),
        StagePlan(
            "final_review",
            "independent_llm",
            (final_spec,),
            (
                "latest entry including front matter",
                "sealed final-blind output",
                "all checker and cold findings",
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
    next_index = guard.STAGES.index(manifest["stage"]) + 1
    next_guard = (
        guard.STAGES[next_index] if next_index < len(guard.STAGES) else None
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "stage": manifest["stage"],
                "next_guard_checkpoint": next_guard,
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
        "--profile", choices=sorted(guard.PROFILES), default="standard"
    )
    parser.add_argument("--reason", default="")
    return parser


def main() -> int:
    args = build_parser().parse_args()
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
