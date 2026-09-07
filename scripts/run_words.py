"""Durable one-or-many-word intake around the unchanged guarded word workflow.

This is a coordinator, not an LLM provider. Preparation reserves isolated Git
worktrees without starting deadlines. Work launches independent word tasks only
after their reservation has been published through the selected transport.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterator
import unicodedata
import uuid

from slugify import slugify

ROOT = Path(__file__).resolve().parents[1]
VERSION = "word_batch_v1"
BATCHES = Path("queue/batches")
CLAIMS = Path("queue/word_claims")
CONFIG = Path("queue/batch_config.json")
ACTIVE = {"preparing", "prepared", "starting", "in_progress", "inspection_required"}
STATES = ACTIVE | {"queued", "linked", "existing", "blocked", "external", "review_complete", "merged"}
ID = re.compile(r"[a-z0-9][a-z0-9-]{0,95}\Z")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, check=check)


def common_dir(root: Path) -> Path:
    path = Path(git(root, "rev-parse", "--git-common-dir").stdout.strip())
    return path.resolve() if path.is_absolute() else (root / path).resolve()


@contextmanager
def lock(root: Path, name: str = "coordinator") -> Iterator[None]:
    if git(root, "branch", "--show-current").stdout.strip().startswith("batch-word/"):
        raise ValueError("use the coordinator checkout for intake/dispatch, not a word worktree")
    directory = common_dir(root) / "dictionary-batch-locks"
    directory.mkdir(exist_ok=True)
    with (directory / (name + ".lock")).open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("another coordinator/worker owns this operation; do not start a duplicate") from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def canonical(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().casefold()
    for apostrophe in "\u2018\u2019\u02bc\u2032`":
        value = value.replace(apostrophe, "'")
    return " ".join(value.split())


def words_from(values: list[str], words_file: Path | None = None) -> list[dict[str, str]]:
    raw = list(values)
    if words_file:
        text = words_file.read_text(encoding="utf-8-sig")
        if words_file.suffix.lower() == ".json":
            extra = json.loads(text)
            if not isinstance(extra, list) or not all(isinstance(v, str) for v in extra):
                raise ValueError("word JSON must be an array of strings")
            raw.extend(extra)
        else:
            raw.append(text)
    result: dict[str, dict[str, str]] = {}
    for group in raw:
        for item in re.split(r"[,;\n\r、，；]+", group):
            word = canonical(item)
            if not word:
                continue
            if len(word) > 100 or not re.fullmatch(r"[a-z][a-z0-9 .'\-]*", word):
                raise ValueError(f"not an English headword/short phrase: {item!r}")
            slug = slugify(word)
            if slug in result and result[slug]["headword"] != word:
                raise ValueError(f"different headwords share slug {slug!r}; resolve before intake")
            result.setdefault(slug, {"headword": word, "slug": slug})
    if not result:
        raise ValueError("at least one headword is required")
    return list(result.values())


def batch_path(root: Path, batch_id: str) -> Path:
    if not ID.fullmatch(batch_id):
        raise ValueError("invalid batch ID")
    return root / BATCHES / (batch_id + ".json")


def load_batch(root: Path, batch_id: str) -> dict[str, Any]:
    value = read_json(batch_path(root, batch_id))
    if value.get("schema_version") != VERSION or value.get("batch_id") != batch_id:
        raise ValueError("invalid batch schema or identity")
    if not isinstance(value.get("jobs"), list) or not value["jobs"]:
        raise ValueError("batch jobs must be a nonempty array")
    if value.get("reviewer_mode") not in {"api", "handoff"} or value.get("publish_mode") not in {"git", "connector"}:
        raise ValueError("invalid batch execution mode")
    if not re.fullmatch(r"[0-9a-f]{40}", str(value.get("base_sha", ""))):
        raise ValueError("batch base must be a pinned commit")
    seen: set[str] = set()
    for job in value["jobs"]:
        if not isinstance(job, dict) or job.get("state") not in STATES:
            raise ValueError("invalid word job")
        normalized = words_from([job.get("headword", "")])
        if len(normalized) != 1 or normalized[0]["slug"] != job.get("slug"):
            raise ValueError("job headword/slug mismatch")
        if job["slug"] in seen or not ID.fullmatch(str(job.get("job_id", ""))):
            raise ValueError("duplicate slug or invalid job ID")
        seen.add(job["slug"])
        if job.get("branch") != "batch-word/" + job["slug"]:
            raise ValueError("job branch mismatch")
        if job.get("run_path"):
            relative_run(job["run_path"], job["slug"])
    return value


def batches(root: Path) -> list[dict[str, Any]]:
    return [load_batch(root, path.stem) for path in sorted((root / BATCHES).glob("*.json"))]


def capacity(root: Path) -> int:
    config = read_json(root / CONFIG)
    value = config.get("max_active_words")
    if config.get("schema_version") != VERSION or type(value) is not int or value < 1:
        raise ValueError("batch_config requires a positive integer max_active_words")
    return value


def entry_path(slug: str) -> Path:
    return Path("entries") / slug[0] / (slug + ".md")


def is_checked(root: Path, slug: str, ref: str | None = None) -> bool:
    if ref:
        result = git(root, "show", ref + ":" + entry_path(slug).as_posix(), check=False)
        if result.returncode:
            return False
        text = result.stdout
    else:
        path = root / entry_path(slug)
        if not path.exists():
            return False
        text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    return len(parts) == 3 and not parts[0].strip() and bool(
        re.search(r"^checked:\s*true\s*$", parts[1], re.M)
    )


def enqueue(root: Path, words: list[dict[str, str]], *, batch_id: str | None = None,
            reviewer_mode: str = "handoff", publish_mode: str = "connector") -> dict[str, Any]:
    batch_id = batch_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S").lower() + "-" + uuid.uuid4().hex[:8]
    path = batch_path(root, batch_id)
    if reviewer_mode not in {"handoff", "api"} or publish_mode not in {"connector", "git"}:
        raise ValueError("invalid execution mode")
    with lock(root):
        all_batches = batches(root)
        if path.exists():
            previous = load_batch(root, batch_id)
            original = [{"headword": j["headword"], "slug": j["slug"]} for j in previous["jobs"]]
            if original != words or previous["reviewer_mode"] != reviewer_mode or previous["publish_mode"] != publish_mode:
                raise ValueError("batch ID already belongs to a different request")
            return previous
        owners: dict[str, tuple[dict, dict]] = {}
        for batch in all_batches:
            for job in batch["jobs"]:
                if job["state"] != "linked":
                    owners[job["slug"]] = (batch, job)
        # Validate the entire request before writing anything.
        for word in words:
            if word["slug"] in owners and owners[word["slug"]][1]["headword"] != word["headword"]:
                raise ValueError(f"headword collision with existing job: {word['slug']}")
        value: dict[str, Any] = {
            "schema_version": VERSION, "batch_id": batch_id, "created_at": now(),
            "base_sha": git(root, "rev-parse", "origin/main^{commit}").stdout.strip(),
            "coordinator_branch": git(root, "branch", "--show-current").stdout.strip(),
            "reviewer_mode": reviewer_mode, "publish_mode": publish_mode, "jobs": [],
        }
        for word in words:
            job: dict[str, Any] = dict(word, job_id=uuid.uuid4().hex, state="queued",
                                       branch="batch-word/" + word["slug"], run_path=None)
            if word["slug"] in owners:
                owner, original = owners[word["slug"]]
                job.update(state="linked", owner_batch=owner["batch_id"], job_id=original["job_id"])
            elif is_checked(root, word["slug"], "origin/main"):
                job["state"] = "existing"
            value["jobs"].append(job)
        write_json(path, value)
        return value


def workspace(root: Path, job: dict[str, Any]) -> Path:
    if not ID.fullmatch(str(job["job_id"])):
        raise ValueError("invalid job ID")
    return common_dir(root) / "dictionary-word-worktrees" / job["job_id"]


def relative_run(value: str, slug: str) -> Path:
    path = Path(value)
    prefix = Path("audits/workflow_runs") / slug
    if path.is_absolute() or ".." in path.parts or not path.is_relative_to(prefix) or path.suffix != ".json":
        raise ValueError("run path is outside the word's workflow directory")
    return path


def own_run(root: Path, job: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    work = workspace(root, job)
    if not work.is_dir():
        return None
    found = []
    for path in (work / "audits/workflow_runs" / job["slug"]).rglob("*.json"):
        manifest = read_json(path)
        if manifest.get("branch") == job["branch"] and slugify(str(manifest.get("headword", ""))) == job["slug"]:
            found.append((path.relative_to(work).as_posix(), manifest))
    if len(found) > 1:
        raise ValueError("multiple runs on one reserved branch; inspect without restarting")
    return found[0] if found else None


def remote_claim(root: Path, job: dict[str, Any]) -> dict[str, Any] | None:
    branch = job["branch"]
    rows = git(root, "ls-remote", "--heads", "origin", "refs/heads/" + branch).stdout.split()
    if not rows:
        return None
    git(root, "fetch", "origin", "refs/heads/" + branch + ":refs/remotes/origin/" + branch)
    result = git(root, "show", "origin/" + branch + ":" + (CLAIMS / (job["slug"] + ".json")).as_posix(), check=False)
    if result.returncode:
        raise ValueError("reserved remote branch exists without a valid claim; do not overwrite")
    value = json.loads(result.stdout)
    if not isinstance(value, dict) or value.get("slug") != job["slug"] or value.get("headword") != job["headword"]:
        raise ValueError("remote word reservation mismatch")
    return value


def prepare_one(root: Path, batch: dict[str, Any], job: dict[str, Any]) -> None:
    claim = remote_claim(root, job)
    if claim and claim.get("job_id") != job["job_id"]:
        job.update(state="external", owner_batch=claim.get("batch_id"),
                   reason="remote reservation belongs to another request; resume its owner, never duplicate")
        return
    work = workspace(root, job)
    if work.exists():
        local_claim = read_json(work / CLAIMS / (job["slug"] + ".json"))
        if local_claim.get("job_id") != job["job_id"]:
            raise ValueError("workspace reservation mismatch")
    else:
        work.parent.mkdir(parents=True, exist_ok=True)
        base = "origin/" + job["branch"] if claim else batch["base_sha"]
        exists = git(root, "show-ref", "--verify", "--quiet", "refs/heads/" + job["branch"], check=False).returncode == 0
        if exists:
            # Never reset an existing branch, even if its worktree was lost.
            git(root, "worktree", "add", "--lock", str(work), job["branch"])
            local_claim = read_json(work / CLAIMS / (job["slug"] + ".json"))
            if local_claim.get("job_id") != job["job_id"]:
                raise ValueError("existing local branch belongs to another request")
        else:
            git(root, "worktree", "add", "--lock", "-b", job["branch"], str(work), base)
            if not claim:
                marker = CLAIMS / (job["slug"] + ".json")
                write_json(work / marker, {"schema_version": VERSION, "batch_id": batch["batch_id"],
                                          "job_id": job["job_id"], "headword": job["headword"],
                                          "coordinator_branch": batch.get("coordinator_branch"),
                                          "slug": job["slug"], "reserved_at": now()})
                git(work, "add", "--", marker.as_posix())
                git(work, "commit", "-m", f"queue({job['slug']}): reserve independent word job")
    # An interrupted initial commit may leave only the intended marker staged.
    marker = (CLAIMS / (job["slug"] + ".json")).as_posix()
    if git(work, "cat-file", "-e", "HEAD:" + marker, check=False).returncode:
        staged = git(work, "diff", "--cached", "--name-only").stdout.splitlines()
        if any(path != marker for path in staged):
            raise ValueError("unrelated staged files prevent reservation recovery")
        git(work, "add", "--", marker)
        git(work, "commit", "-m", f"queue({job['slug']}): recover word reservation")
    job.update(state="prepared", reason="publish the reservation, then start this word when a worker is available")


def prepare(root: Path, batch_id: str) -> dict[str, Any]:
    # Refresh only for skip/dedup detection. Each request's specification base
    # remains pinned; coordinator-only commits never enter word branches.
    git(root, "fetch", "origin", "refs/heads/main:refs/remotes/origin/main")
    with lock(root):
        batch = load_batch(root, batch_id)
        occupied = sum(job["state"] in ACTIVE for b in batches(root) for job in b["jobs"])
        available = max(0, capacity(root) - occupied)
        for job in batch["jobs"]:
            if available == 0:
                break
            if job["state"] != "queued":
                continue
            if is_checked(root, job["slug"], "origin/main"):
                job.update(state="existing", reason="checked entry already present on origin/main")
                write_json(batch_path(root, batch_id), batch)
                continue
            # Persist before touching Git so a crash cannot cause a second start.
            job["state"] = "preparing"
            write_json(batch_path(root, batch_id), batch)
            try:
                prepare_one(root, batch, job)
            except (ValueError, OSError, subprocess.SubprocessError) as exc:
                job.update(state="blocked", reason=str(exc))
            if job["state"] in ACTIVE:
                available -= 1
            write_json(batch_path(root, batch_id), batch)
        return batch


def job_in(batch: dict[str, Any], slug: str) -> dict[str, Any]:
    for job in batch["jobs"]:
        if job["slug"] == slug:
            return job
    raise ValueError("word is not in this batch")


def record_run(root: Path, job: dict[str, Any]) -> bool:
    found = own_run(root, job)
    if not found:
        return False
    run_path, manifest = found
    if manifest.get("status") == "completed" and manifest.get("stage") == "completed":
        state = "review_complete"
    elif manifest.get("status") == "budget_exhausted":
        state = "blocked"
    elif manifest.get("status") == "in_progress":
        state = "in_progress"
    else:
        raise ValueError("unrecognized workflow status; do not infer completion")
    job.update(state=state, run_path=run_path, stage=manifest.get("stage"),
               reason=manifest.get("stop_reason", ""))
    return True


def start(root: Path, batch_id: str, slug: str) -> dict[str, Any]:
    # Per-word lock is separate from the short coordinator transaction so new
    # intake remains possible while the guarded starter scans/publishes.
    with lock(root, "word-" + slug):
        with lock(root):
            batch = load_batch(root, batch_id)
            job = job_in(batch, slug)
            if job["state"] not in {"prepared", "starting", "in_progress", "inspection_required"}:
                raise ValueError("job is not startable; queued/blocked/linked jobs cannot bypass dispatch")
            if record_run(root, job):
                write_json(batch_path(root, batch_id), batch)
                return job
            if job["state"] in {"starting", "inspection_required", "in_progress"}:
                raise ValueError("prior start has no recoverable manifest; inspect explicitly, never restart automatically")
            claim = remote_claim(root, job)
            if not claim:
                return dict(job, action="reservation_publication_pending")
            if claim.get("job_id") != job["job_id"]:
                job.update(state="external", reason="reservation lost; do not launch a duplicate")
                write_json(batch_path(root, batch_id), batch)
                return job
            job.update(state="starting", start_attempted_at=now())
            write_json(batch_path(root, batch_id), batch)
            work = workspace(root, job)
        result: subprocess.CompletedProcess[str] | None = None
        failure = ""
        try:
            result = subprocess.run(
                [sys.executable, str(work / "scripts/start_word.py"), job["headword"],
                 "--publish-mode", batch["publish_mode"], "--reviewer-mode", batch["reviewer_mode"]],
                cwd=work, capture_output=True, text=True, timeout=180,
            )
            failure = result.stderr.strip() if result.returncode else ""
        except (OSError, subprocess.SubprocessError) as exc:
            failure = str(exc)
        with lock(root):
            # Reload rather than overwrite intake/status updates made meanwhile.
            batch = load_batch(root, batch_id)
            job = job_in(batch, slug)
            try:
                found = record_run(root, job)
            except (ValueError, OSError) as exc:
                found, failure = False, str(exc)
            if not found:
                job.update(state="inspection_required", reason=failure or "starter returned no workflow manifest")
                if result is not None:
                    try:
                        report = json.loads(result.stdout)
                    except json.JSONDecodeError:
                        report = {}
                    if isinstance(report, dict) and report.get("status") in {
                        "resume_required", "restart_confirmation_required", "remote_run_scan_failed"
                    }:
                        job.update(state="blocked", reason=report["status"], guard_report=report)
            if failure:
                job["last_error"] = failure
            write_json(batch_path(root, batch_id), batch)
            return job


def refresh(root: Path, batch_id: str, *, fetch: bool = False) -> dict[str, Any]:
    """Reconcile saved results; never heartbeat, clear failures, or start work."""
    if fetch:
        git(root, "fetch", "origin", "refs/heads/main:refs/remotes/origin/main")
    with lock(root):
        batch = load_batch(root, batch_id)
        for job in batch["jobs"]:
            if job["state"] in {"queued", "linked", "external", "existing", "merged"}:
                continue
            try:
                if not record_run(root, job) and job["state"] == "preparing":
                    job.update(state="inspection_required", reason="interrupted preparation; inspect Git before recovery")
                if fetch and job["state"] == "review_complete":
                    main_run = git(root, "show", "origin/main:" + job["run_path"], check=False)
                    if main_run.returncode == 0:
                        merged = json.loads(main_run.stdout)
                        local = own_run(root, job)[1]
                        if merged.get("run_id") == local.get("run_id") and merged.get("status") == "completed" and merged.get("stage") == "completed":
                            job.update(state="merged", reason="completed run verified on origin/main")
            except (ValueError, OSError) as exc:
                job.update(state="inspection_required", reason=str(exc))
        write_json(batch_path(root, batch_id), batch)
        return batch


def recover(root: Path, batch_id: str, slug: str) -> dict[str, Any]:
    """Explicitly recover preparation only, never reset an attempted workflow."""
    with lock(root):
        batch = load_batch(root, batch_id)
        job = job_in(batch, slug)
        if record_run(root, job):
            write_json(batch_path(root, batch_id), batch)
            return job
        missing_workspace = not workspace(root, job).exists()
        remote_scan_only = job.get("guard_report", {}).get("status") == "remote_run_scan_failed"
        if job.get("start_attempted_at") and not missing_workspace and not remote_scan_only:
            raise ValueError("an attempted start cannot be reset by preparation recovery")
        if job.get("guard_report") and not remote_scan_only:
            raise ValueError("follow the original workflow guard; do not reset its run")
        if job["state"] not in ACTIVE | {"blocked"}:
            raise ValueError("only preparation or missing-workspace recovery is supported")
        if sum(j["state"] in ACTIVE for b in batches(root) for j in b["jobs"]) - int(job["state"] in ACTIVE) >= capacity(root):
            raise ValueError("no free word slot")
        prepare_one(root, batch, job)
        if not record_run(root, job) and job.get("start_attempted_at") and not remote_scan_only:
            job.update(state="inspection_required", reason="attempted start has no published manifest; inspect, never restart")
        if remote_scan_only:
            job.pop("guard_report", None)
            job.pop("start_attempted_at", None)
        write_json(batch_path(root, batch_id), batch)
        return job


def report(root: Path, batch: dict[str, Any]) -> dict[str, Any]:
    jobs = []
    counts: dict[str, int] = {}
    for original in batch["jobs"]:
        job = dict(original)
        if job["state"] == "linked":
            source = job_in(load_batch(root, job["owner_batch"]), job["slug"])
            job["owner_state"] = source["state"]
        if job["state"] in ACTIVE | {"blocked", "review_complete"}:
            job["workdir"] = str(workspace(root, job))
            if job.get("run_path"):
                job["resume_argv"] = ["python", "scripts/run_word.py", "--resume", job["run_path"]]
            elif job["state"] == "prepared":
                job["action"] = "publish reservation with scripts/publish_checkpoint.js in workdir; then start"
                job["start_argv"] = ["python", "scripts/run_words.py", "start", batch["batch_id"], job["slug"]]
        state = job.get("owner_state", job["state"])
        counts[state] = counts.get(state, 0) + 1
        jobs.append(job)
    return {"schema_version": VERSION, "batch_id": batch["batch_id"],
            "batch_path": (BATCHES / (batch["batch_id"] + ".json")).as_posix(),
            "max_active_words": capacity(root), "state_counts": counts, "jobs": jobs,
            "note": "Queue/prepare do not generate content. Independent word workers use the existing workflow. No automatic LLM launcher or background service is implied."}


def validate(root: Path) -> dict[str, Any]:
    capacity(root)
    owners: dict[str, str] = {}
    all_batches = batches(root)
    for batch in all_batches:
        for job in batch["jobs"]:
            if job["state"] == "linked":
                owner = job_in(load_batch(root, job["owner_batch"]), job["slug"])
                if owner["state"] == "linked" or owner["job_id"] != job["job_id"] or owner["headword"] != job["headword"]:
                    raise ValueError("invalid cross-batch job link")
            else:
                if job["slug"] in owners:
                    raise ValueError("multiple local job owners for one headword")
                owners[job["slug"]] = batch["batch_id"]
    return {"valid": True, "batches": len(all_batches), "unique_words": len(owners)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    intake = sub.add_parser("enqueue", help="one or many headwords; no run/deadline starts")
    intake.add_argument("headwords", nargs="*")
    intake.add_argument("--file", type=Path)
    intake.add_argument("--batch-id")
    intake.add_argument("--reviewer-mode", choices=("api", "handoff"), default="handoff")
    intake.add_argument("--publish-mode", choices=("connector", "git"), default="connector")
    for name in ("prepare", "status", "refresh", "start", "recover"):
        command = sub.add_parser(name)
        command.add_argument("batch_id")
        if name == "refresh":
            command.add_argument("--fetch", action="store_true")
        if name in {"start", "recover"}:
            command.add_argument("slug")
    sub.add_parser("validate")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "enqueue":
            value = report(root, enqueue(root, words_from(args.headwords, args.file), batch_id=args.batch_id,
                                         reviewer_mode=args.reviewer_mode, publish_mode=args.publish_mode))
        elif args.command == "validate":
            value = validate(root)
        elif args.command in {"start", "recover"}:
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
                raise ValueError("invalid slug")
            (start if args.command == "start" else recover)(root, args.batch_id, args.slug)
            value = report(root, load_batch(root, args.batch_id))
        else:
            function = {"prepare": prepare, "status": load_batch, "refresh": refresh}[args.command]
            result = function(root, args.batch_id, fetch=args.fetch) if args.command == "refresh" else function(root, args.batch_id)
            value = report(root, result)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "batch_operation_blocked", "reason": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
