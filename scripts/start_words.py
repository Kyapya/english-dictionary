"""Durable multi-word intake; delegate content work to the existing one-word flow.

The control checkout owns queue/batches and queue/jobs. Workers use independent
local clones, never its index/config. No LLM calls, review decisions, retries of
exhausted runs, pushes, or merges are invented by this scheduler.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import signal
import sqlite3
import subprocess
import sys
import tempfile
import uuid

from slugify import slugify

ROOT = Path(__file__).resolve().parents[1]
VERSION = "word_batch_v1"
ACTIVE = {"preparing", "active"}


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected an object: {path}")
    return value


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".batch-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def parse_words(arguments: list[str], file: Path | None = None) -> list[str]:
    """Each CLI argument/line/comma-delimited item is one headword, not each space."""
    values = list(arguments)
    if file is not None:
        text = file.read_text(encoding="utf-8-sig")
        if file.suffix.lower() == ".json":
            decoded = json.loads(text)
            if not isinstance(decoded, list) or not all(isinstance(v, str) for v in decoded):
                raise ValueError("word JSON must be an array of strings")
            values.extend(decoded)
        else:
            values.append(text)
    words: dict[str, str] = {}
    for value in values:
        for item in re.split(r"[,、\r\n]+", value):
            item = " ".join(item.strip().split())
            if not item:
                continue
            if len(item) > 160 or not re.search(r"[A-Za-z]", item):
                raise ValueError(f"not an English headword: {item!r}")
            if re.search(r"[^A-Za-z0-9 '\u2018\u2019\u02bc\u2032`.-]", item):
                raise ValueError(f"unsupported characters in headword: {item!r}")
            key = slugify(item)
            # case/apostrophe variants share the same article path by project policy.
            words.setdefault(key, item)
    if not words:
        raise ValueError("supply at least one English word or quoted short phrase")
    return list(words.values())


class Queue:
    def __init__(self, root: Path):
        self.root = root.resolve()
        common = Path(git(self.root, "rev-parse", "--git-common-dir"))
        self.common = (self.root / common).resolve()
        self.control = self.common / "dictionary-batches"
        self.control.mkdir(parents=True, exist_ok=True)
        # A single control checkout must own a shared git repository's queue.
        owner = self.control / "owner.json"
        with self.lock():
            if owner.exists() and read(owner)["root"] != str(self.root):
                raise ValueError("use the original control checkout for this queue")
            if not owner.exists():
                write(owner, {"root": str(self.root)})

    @contextmanager
    def lock(self):
        # SQLite locking is process-safe and released on crash; no stale PID leases.
        connection = sqlite3.connect(self.control / "lock.sqlite3", timeout=30)
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield
            connection.commit()
        finally:
            connection.close()

    def job_path(self, slug: str) -> Path:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError("invalid job slug")
        return self.root / "queue" / "jobs" / f"{slug}.json"

    def jobs(self) -> list[dict]:
        result = []
        for path in sorted((self.root / "queue" / "jobs").glob("*.json")):
            value = read(path)
            if value.get("schema_version") != VERSION or value.get("slug") != path.stem:
                raise ValueError(f"invalid queue job: {path}")
            result.append(value)
        return sorted(result, key=lambda job: (job["queued_at"], job["job_id"]))

    def workspace(self, job: dict) -> Path:
        ident = job["job_id"]
        if not re.fullmatch(r"[0-9a-f]{32}", ident):
            raise ValueError("invalid job id")
        return self.control / "workers" / ident

    def enqueue(self, words: list[str], *, publish_mode: str = "connector",
                reviewer_mode: str = "handoff") -> dict:
        words = parse_words(words)
        if publish_mode not in {"git", "connector"} or reviewer_mode not in {"api", "handoff"}:
            raise ValueError("invalid execution mode")
        # Pin the published main, not the control branch containing queue records.
        # Resolve outside the queue lock; a slow remote must not hold the dispatcher.
        remote = git(self.root, "ls-remote", "--exit-code", "origin", "refs/heads/main").split()
        if len(remote) != 2 or remote[1] != "refs/heads/main" or not re.fullmatch(r"[0-9a-f]{40}", remote[0]):
            raise ValueError("cannot resolve the published main commit")
        base = remote[0]
        try:
            git(self.root, "cat-file", "-e", base + "^{commit}")
        except subprocess.CalledProcessError as exc:
            raise ValueError("published main is not available locally; fetch origin main before intake") from exc
        with self.lock():
            batch_id = uuid.uuid4().hex
            batch = {"schema_version": VERSION, "batch_id": batch_id,
                     "received_at": now(), "jobs": []}
            # Validate the complete request before writing any of its jobs.
            for word in words:
                existing = self.job_path(slugify(word))
                if existing.exists():
                    previous = read(existing)
                    if previous.get("schema_version") != VERSION:
                        raise ValueError(f"invalid queue job: {existing}")
                    if (previous.get("publish_mode"), previous.get("reviewer_mode")) != (publish_mode, reviewer_mode):
                        raise ValueError(f"{word}: existing job uses different modes; resume it explicitly")
            for word in words:
                slug = slugify(word)
                path = self.job_path(slug)
                if path.exists():
                    job = read(path)
                    if (job.get("publish_mode"), job.get("reviewer_mode")) != (publish_mode, reviewer_mode):
                        raise ValueError(f"{slug}: existing job uses different modes; resume it explicitly")
                else:
                    ident = uuid.uuid4().hex
                    job = {"schema_version": VERSION, "job_id": ident, "slug": slug,
                           "headword": word, "base_sha": base, "queued_at": now(),
                           "status": "queued", "branch": f"words/{slug}-{ident[:12]}",
                           "publish_mode": publish_mode, "reviewer_mode": reviewer_mode,
                           "run_path": None, "error": None}
                    write(path, job)
                batch["jobs"].append({"slug": slug, "job_id": job["job_id"]})
            write(self.root / "queue" / "batches" / f"{batch_id}.json", batch)
            return batch

    def _manifest(self, job: dict) -> tuple[Path, dict] | None:
        workspace = self.workspace(job)
        if not workspace.is_dir():
            return None
        if job.get("run_path"):
            relative = Path(job["run_path"])
            expected = Path("audits/workflow_runs") / job["slug"]
            if relative.parent != expected or relative.suffix != ".json":
                raise ValueError("run path is outside its word's workflow directory")
            paths = [workspace / relative]
        else:
            if "baseline_runs" not in job:
                return None
            baseline = set(job["baseline_runs"])
            paths = [p for p in (workspace / "audits/workflow_runs" / job["slug"]).glob("*.json")
                     if p.relative_to(workspace).as_posix() not in baseline]
        if not paths:
            return None
        if len(paths) != 1:
            raise ValueError("multiple new runs found; do not guess or reset their budgets")
        path = paths[0]
        manifest = read(path)
        if slugify(str(manifest.get("headword", ""))) != job["slug"]:
            raise ValueError("workflow headword differs from its assigned job")
        if manifest.get("branch") != job["branch"]:
            raise ValueError("workflow branch differs from its assigned job")
        if manifest.get("status") not in {"in_progress", "completed", "budget_exhausted"}:
            raise ValueError("unknown workflow status")
        return path, manifest

    def _refresh(self, job: dict) -> dict:
        if job["status"] == "queued":
            return job
        try:
            record = self._manifest(job)
            if record is None:
                # Never reinterpret an interrupted launch as a fresh queued job.
                return job
            path, manifest = record
            job["run_path"] = path.relative_to(self.workspace(job)).as_posix()
            job["workflow_status"] = manifest["status"]
            job["stage"] = manifest.get("stage")
            job["last_heartbeat_at"] = manifest.get("last_heartbeat_at")
            job["time_warnings"] = manifest.get("time_warnings", {})
            job["status"] = {"in_progress": "active", "completed": "completed",
                             "budget_exhausted": "blocked"}[manifest["status"]]
            job["error"] = manifest.get("stop_reason") or None
        except (OSError, ValueError, KeyError) as exc:
            job["status"] = "blocked"
            job["error"] = str(exc)
        write(self.job_path(job["slug"]), job)
        return job

    def snapshot(self) -> dict:
        with self.lock():
            jobs = [self._refresh(job) for job in self.jobs()]
            summaries = []
            for job in jobs:
                row = {key: job.get(key) for key in
                       ("slug", "headword", "job_id", "status", "branch", "run_path", "stage", "error",
                        "last_heartbeat_at", "time_warnings")}
                row["workspace"] = str(self.workspace(job)) if job["status"] != "queued" else None
                row["workspace_available"] = self.workspace(job).is_dir()
                row["assignment_path"] = str(self.workspace(job).parent / f"{job['job_id']}.request.md") if job.get("run_path") else None
                if job.get("run_path") and row["workspace_available"]:
                    row["resume_argv"] = [sys.executable, "scripts/run_word.py", "--resume", job["run_path"]]
                if job.get("blocked_runs"):
                    row["existing_runs"] = job["blocked_runs"]
                summaries.append(row)
            counts = {status: sum(row["status"] == status for row in summaries)
                      for status in ("queued", "preparing", "active", "blocked", "completed")}
            priority = {"active": 0, "preparing": 1, "blocked": 2, "queued": 3, "completed": 4}
            summaries.sort(key=lambda row: priority[row["status"]])
            return {"schema_version": VERSION, "counts": counts, "jobs": summaries[:100],
                    "omitted_jobs": max(0, len(summaries) - 100),
                    "execution": "handoff: run each word's existing workflow in its own workspace"}

    def _prepare(self, job: dict) -> None:
        workspace = self.workspace(job)
        if workspace.exists():
            raise ValueError("workspace already exists; recover the existing job, never overwrite it")
        workspace.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout",
                        str(self.root), str(workspace)], check=True, capture_output=True, text=True)
        git(workspace, "remote", "set-url", "origin", git(self.root, "remote", "get-url", "origin"))
        git(workspace, "checkout", "-b", job["branch"], job["base_sha"])
        for key in ("user.name", "user.email"):
            configured = subprocess.run(["git", "-C", str(self.root), "config", "--get", key],
                                        capture_output=True, text=True)
            if configured.returncode == 0:
                git(workspace, "config", key, configured.stdout.strip())
        for script in ("scripts/start_word.py", "scripts/run_word.py"):
            if not (workspace / script).is_file():
                raise ValueError(f"pinned base does not contain {script}")
        job["baseline_runs"] = [p.relative_to(workspace).as_posix() for p in
                                (workspace / "audits/workflow_runs" / job["slug"]).glob("*.json")]
        job["prepared_at"] = now()
        with self.lock():
            write(self.job_path(job["slug"]), job)
        command = [sys.executable, "scripts/start_word.py", job["headword"],
                   "--publish-mode", job["publish_mode"], "--reviewer-mode", job["reviewer_mode"]]
        log = self.control / f"{job['job_id']}.start.log"
        with log.open("w", encoding="utf-8") as stream:
            process = subprocess.Popen(command, cwd=workspace, stdout=stream, stderr=subprocess.STDOUT,
                                       text=True, start_new_session=(os.name == "posix"))
            try:
                code = process.wait(timeout=180)
            except BaseException:
                # start_word launches run_word: stop the entire process group on timeout.
                if os.name == "posix":
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    process.kill()
                process.wait()
                raise
        job["start_exit_code"] = code
        record = self._manifest(job)
        if record is None:
            output = log.read_text(encoding="utf-8")
            try:
                payload = json.loads(output)
            except ValueError:
                payload = {}
            job["blocked_runs"] = payload.get("runs", [])
            raise ValueError(payload.get("reason") or
                             f"start did not produce one run (exit {code}); see {log.name}")
        if code != 0:
            # A persisted run is authoritative even if the transport/start command failed.
            job["start_warning"] = f"start exit {code}; resume the persisted run, do not restart"
        self._write_handoff(job, record[0])

    def _write_handoff(self, job: dict, run: Path) -> None:
        workspace = self.workspace(job)
        relative = run.relative_to(workspace).as_posix()
        text = (f"# Word assignment: {job['headword']}\n\n"
                f"Work only in `{workspace}` on branch `{job['branch']}`.\n"
                f"Resume `{relative}`; do not create a fresh run or reset any budget.\n"
                "Read AGENTS.md here; follow the existing single-word orchestrator and its next_stage.\n"
                "Keep every content/review/independence/publication gate unchanged.\n"
                "Use this word only in the writer context; delegate reviews to independent contexts.\n"
                "Publish this workspace's checkpoints through the selected transport.\n"
                "Do not edit the control checkout, another word, or its queue files.\n"
                "A sibling's failure is not a reason to stop this word.\n"
                "Do not mark the batch complete or merge sibling branches yourself.\n\n"
                f"```sh\n{shlex.join([sys.executable, 'scripts/run_word.py', '--resume', relative])}\n```\n")
        (workspace.parent / f"{job['job_id']}.request.md").write_text(text, encoding="utf-8", newline="\n")

    def dispatch(self, max_active: int | None = None) -> dict:
        if max_active is not None and not 1 <= max_active <= 16:
            raise ValueError("max-active must be between 1 and 16")
        with self.lock():
            # Store one queue-wide cap; a second dispatcher cannot increase it silently.
            settings = self.control / "settings.json"
            configured = read(settings)["max_active"] if settings.exists() else 2
            if max_active is not None and settings.exists() and configured != max_active:
                raise ValueError("queue concurrency is already pinned; use --set-max-active explicitly")
            max_active = configured if max_active is None else max_active
            if not settings.exists():
                write(settings, {"max_active": max_active})
            jobs = [self._refresh(job) for job in self.jobs()]
            slots = max(0, max_active - sum(j["status"] in ACTIVE for j in jobs))
            selected = [j for j in jobs if j["status"] == "queued"][:slots]
            # Claim before slow clone/fetch/commit operations, leaving enqueue unblocked.
            for job in selected:
                job["status"] = "preparing"
                write(self.job_path(job["slug"]), job)
        # Initialization is deliberately serial: expensive *content work* is handed off
        # per word afterward. Starting shells is not evidence of parallel LLM execution.
        for job in selected:
            try:
                self._prepare(job)
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                job["status"] = "blocked"
                job["error"] = str(exc)
            with self.lock():
                self._refresh(job)
                write(self.job_path(job["slug"]), job)
        return self.snapshot()

    def configure(self, maximum: int) -> dict:
        if not 1 <= maximum <= 16:
            raise ValueError("max-active must be between 1 and 16")
        with self.lock():
            write(self.control / "settings.json", {"max_active": maximum})
        return self.snapshot()

    def recover(self, slug: str) -> dict:
        """Reattach a persisted run after an interrupted launcher, never restart it."""
        with self.lock():
            job = read(self.job_path(slug))
            record = self._manifest(job)
            if record is None:
                raise ValueError("no unambiguous persisted run; inspect start log/remote state before recovery")
            self._write_handoff(job, record[0])
            self._refresh(job)
        return self.snapshot()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("words", nargs="*")
    parser.add_argument("--words-file", type=Path)
    parser.add_argument("--enqueue-only", action="store_true")
    parser.add_argument("--dispatch", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--recover", metavar="SLUG")
    parser.add_argument("--max-active", type=int)
    parser.add_argument("--set-max-active", type=int)
    parser.add_argument("--publish-mode", choices=("git", "connector"), default="connector")
    parser.add_argument("--reviewer-mode", choices=("api", "handoff"), default="handoff")
    args = parser.parse_args(argv)
    try:
        has_words = bool(args.words or args.words_file)
        if args.set_max_active is not None and (has_words or args.dispatch or args.status or args.recover or args.enqueue_only):
            raise ValueError("set-max-active must be used on its own")
        if sum((args.status, bool(args.recover), args.enqueue_only)) > 1:
            raise ValueError("status, recover and enqueue-only are mutually exclusive")
        if (args.status or args.recover) and (has_words or args.dispatch):
            raise ValueError("status/recover cannot also enqueue or dispatch")
        if args.enqueue_only and args.dispatch:
            raise ValueError("enqueue-only cannot dispatch")
        words = parse_words(args.words, args.words_file) if has_words else None
        if words is None and args.set_max_active is None and not (args.status or args.recover or args.dispatch):
            raise ValueError("supply words, --dispatch, --status or --recover")
        queue = Queue(ROOT)
        batch = queue.enqueue(words, publish_mode=args.publish_mode,
                              reviewer_mode=args.reviewer_mode) if words else None
        if args.set_max_active is not None:
            result = queue.configure(args.set_max_active)
        elif args.recover:
            result = queue.recover(args.recover)
        elif args.status or args.enqueue_only:
            result = queue.snapshot()
        else:
            result = queue.dispatch(args.max_active)
        if batch:
            result["batch"] = {"batch_id": batch["batch_id"], "accepted_count": len(batch["jobs"]),
                               "path": f"queue/batches/{batch['batch_id']}.json"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "queue_error", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
