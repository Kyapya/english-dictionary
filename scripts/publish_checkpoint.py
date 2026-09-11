"""Publish local commits using a selected transport; connector I/O stays in Work.

The companion publish_checkpoint.js consumes this CLI through configured tools.
No connector credentials are extracted or copied into the shell.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import os
import re
import tempfile
import sys
from pathlib import Path


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True, encoding="utf-8", stderr=subprocess.PIPE, timeout=60).strip()


def mode(root: Path) -> str:
    result = subprocess.run(["git", "-C", str(root), "config", "--get", "dictionary.publishMode"], capture_output=True, text=True)
    return result.stdout.strip() or "git"


def select(root: Path, selected: str) -> str:
    if selected not in {"git", "connector"}:
        raise ValueError("publish mode must be git or connector")
    git(root, "config", "dictionary.publishMode", selected)
    return selected


def receipt_path(root: Path) -> Path:
    branch = git(root, "branch", "--show-current")
    if not branch:
        raise ValueError("publication requires a branch")
    directory = Path(git(root, "rev-parse", "--absolute-git-dir"))
    return directory / ("dictionary-publish-" + hashlib.sha256(branch.encode()).hexdigest() + ".json")


def receipt(root: Path) -> dict:
    path = receipt_path(root)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def publish(root: Path) -> bool:
    if mode(root) == "connector":
        return receipt(root).get("local_head") == git(root, "rev-parse", "HEAD")
    git(root, "push", "-u", "origin", "HEAD:" + git(root, "branch", "--show-current"))
    return True


def plan(root: Path, *, check_remote: bool = True, check_clean: bool = True) -> dict:
    if check_clean and git(root, "status", "--porcelain"):
        raise ValueError("commit the intended changes before publishing")
    previous = receipt(root)
    branch = git(root, "branch", "--show-current")
    if not branch:
        raise ValueError("publication requires a branch")
    base = previous.get("local_head") or git(root, "merge-base", "HEAD", "origin/main")
    remote_base = previous.get("remote_head", base)
    remote_rows = git(root, "ls-remote", "--heads", "origin", "refs/heads/" + branch).split() if check_remote else []
    if check_remote and remote_rows and remote_rows[0] != remote_base:
        raise ValueError("remote branch advanced; reconcile it or accept the already published checkpoint before retrying")
    git(root, "merge-base", "--is-ancestor", base, "HEAD")
    commits = []
    for sha in git(root, "rev-list", "--reverse", base + "..HEAD").splitlines():
        parents = git(root, "show", "-s", "--format=%P", sha).split()
        if parents != [commits[-1]["local_sha"] if commits else base]:
            raise ValueError("connector publication requires linear local commits")
        raw = subprocess.check_output(["git", "-C", str(root), "diff-tree", "--no-commit-id", "--raw", "--no-abbrev", "-r", "-z", parents[0], sha])
        parts = raw.split(b"\0")
        entries = []
        for index in range(0, len(parts) - 1, 2):
            old_mode, new_mode, old_sha, new_sha, status = parts[index].decode().split()
            path = parts[index + 1].decode()
            if new_mode not in {"000000", "100644", "100755", "120000"}:
                raise ValueError("unsupported tree mode: " + new_mode)
            entries.append({"path": path, "mode": old_mode.lstrip(":") if new_mode == "000000" else new_mode, "type": "blob", "sha": None if new_mode == "000000" else new_sha})
        commits.append({"local_sha": sha, "tree_sha": git(root, "rev-parse", sha + "^{tree}"), "base_tree_sha": git(root, "rev-parse", parents[0] + "^{tree}"), "message": git(root, "show", "-s", "--format=%B", sha), "entries": entries})
    return {"branch": branch, "branch_exists": bool(remote_rows), "local_base": base, "remote_base": remote_base, "local_head": git(root, "rev-parse", "HEAD"), "commits": commits}


def _atomic_json(path: Path, value: dict) -> None:
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".publication-")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _session_path(root: Path, plan_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{64}", plan_id):
        raise ValueError("invalid publication plan ID")
    return receipt_path(root).parent / ("dictionary-transfer-" + plan_id + ".json")


def _validate_before_upload(root: Path, value: dict) -> None:
    """Run the same changed-content gates before any connector write."""
    changed = {item["path"] for commit in value["commits"] for item in commit["entries"]}
    if not any(path.startswith(("entries/", "audits/", "queue/")) for path in changed):
        return
    commands = [("entry_workflow_guard.py", ["validate-changed", "--merge-ready"]),
                ("checker_subagent_gate.py", ["validate-changed"]),
                ("content_audit.py", ["validate-changed"]),
                ("semantic_resolution_gate.py", ["validate-changed"]),
                ("source_first_audit_gate.py", ["validate-changed"])]
    if any(path.startswith("audits/targeted_corrections/") for path in changed):
        commands = [("targeted_correction.py", ["validate-changed"])]
    for script, args in commands:
        path = root / "scripts" / script
        if not path.exists():
            raise ValueError("publication validation script missing: " + script)
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(path), *args,
             "--base", value["local_base"], "--head", value["local_head"]],
            cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        if result.returncode:
            raise ValueError(script + ": " + result.stdout + result.stderr)


def prepare(root: Path, repository: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be owner/name")
    remote = git(root, "remote", "get-url", "origin")
    allowed = {f"https://github.com/{repository}", f"https://github.com/{repository}.git",
               f"git@github.com:{repository}.git"}
    if remote not in allowed:
        raise ValueError("connector destination must match origin; do not switch transport after denial")
    # A retry reuses the snapshot even after a ref update whose response was lost.
    pointer = receipt_path(root).with_suffix(".transfer.json")
    if pointer.exists():
        previous = json.loads(pointer.read_text(encoding="utf-8"))
        state = session(root, previous["plan_id"], check_head=False)
        value = state["plan"]
        if (value["local_head"] == git(root, "rev-parse", "HEAD")
                and value["repository"] == repository
                and value["branch"] == git(root, "branch", "--show-current")):
            if git(root, "status", "--porcelain"):
                raise ValueError("worktree changed during publication")
            actual = git(root, "ls-remote", "--heads", "origin", "refs/heads/" + value["branch"]).split()
            expected = [value["remote_base"], *state["commits"].values()]
            if actual and actual[0] not in expected:
                raise ValueError("remote branch advanced; reconcile before retrying")
            return {"plan_id": previous["plan_id"], "resumed": True, "progress": state["progress"],
                    "branch_exists": bool(actual), "published_head": actual[0] if actual else None}
    value = plan(root)
    _validate_before_upload(root, value)
    value["repository"] = repository
    plan_id = hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
    state = {"plan": value, "blobs": [], "trees": [], "commits": {}, "progress": "prepared"}
    _atomic_json(_session_path(root, plan_id), state)
    _atomic_json(pointer, {"plan_id": plan_id})
    return {"plan_id": plan_id, "resumed": False, "progress": "prepared",
            "branch_exists": value["branch_exists"]}


def session(root: Path, plan_id: str, *, check_head: bool = True) -> dict:
    value = json.loads(_session_path(root, plan_id).read_text(encoding="utf-8"))
    if check_head and value["plan"]["local_head"] != git(root, "rev-parse", "HEAD"):
        raise ValueError("publication snapshot is stale")
    return value


def record_progress(root: Path, plan_id: str, kind: str, sha: str, local_sha: str | None) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", sha or ""):
        raise ValueError("progress requires a full SHA")
    state = session(root, plan_id)
    commits = state["plan"]["commits"]
    if kind == "blob":
        if sha not in {e["sha"] for c in commits for e in c["entries"]}:
            raise ValueError("blob outside publication plan")
        state["blobs"] = sorted(set(state["blobs"]) | {sha})
    elif kind == "tree":
        if sha not in {c["tree_sha"] for c in commits}:
            raise ValueError("tree outside publication plan")
        state["trees"] = sorted(set(state["trees"]) | {sha})
    elif kind == "commit":
        if local_sha not in {c["local_sha"] for c in commits}:
            raise ValueError("commit outside publication plan")
        state["commits"][local_sha] = sha
    else:
        raise ValueError("unknown progress kind")
    state["progress"] = kind + ":" + sha
    _atomic_json(_session_path(root, plan_id), state)
    return {"progress": state["progress"]}


def blob_page(root: Path, sha: str, offset: int, length: int, plan_id: str | None = None) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", sha or ""):
        raise ValueError("blob SHA must be a full Git object ID")
    if offset < 0 or length <= 0 or length > 12000:
        raise ValueError("invalid page bounds")
    if plan_id:
        state = session(root, plan_id)
        if sha not in {e["sha"] for c in state["plan"]["commits"] for e in c["entries"]}:
            raise ValueError("blob outside publication plan")
    cache = receipt_path(root).parent / ("dictionary-blob-" + sha + ".b64")
    if not cache.exists():
        raw = subprocess.check_output(["git", "-C", str(root), "cat-file", "blob", sha], timeout=60)
        if hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() != sha:
            raise ValueError("local blob hash mismatch")
        cache.write_bytes(base64.b64encode(raw))
    with cache.open("rb") as stream:
        stream.seek(offset)
        chunk = stream.read(length).decode("ascii")
    return {"total": cache.stat().st_size, "chunk": chunk}


def accept(root: Path, remote_head: str) -> dict:
    publication = plan(root, check_remote=False, check_clean=False)
    branch = publication["branch"]
    actual = git(root, "ls-remote", "--heads", "origin", "refs/heads/" + branch).split()
    if not actual or actual[0] != remote_head:
        raise ValueError("remote branch differs from publication receipt")
    git(root, "fetch", "origin", branch)
    chain = git(root, "rev-list", "--reverse", publication["remote_base"] + ".." + remote_head).splitlines()
    if len(chain) != len(publication["commits"]):
        raise ValueError("remote commit count differs from publication plan")
    parent = publication["remote_base"]
    for remote_sha, local in zip(chain, publication["commits"]):
        if git(root, "show", "-s", "--format=%P", remote_sha).split() != [parent]:
            raise ValueError("remote ancestry differs from publication plan")
        if git(root, "rev-parse", remote_sha + "^{tree}") != local["tree_sha"]:
            raise ValueError("remote content differs from local commit")
        parent = remote_sha
    if not chain and remote_head != publication["remote_base"]:
        raise ValueError("unexpected remote head")
    value = {"local_head": publication["local_head"], "remote_head": remote_head, "branch": branch}
    receipt_path(root).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "plan", "blob", "accept", "state", "progress"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--sha")
    parser.add_argument("--repository")
    parser.add_argument("--plan-id")
    parser.add_argument("--kind")
    parser.add_argument("--local-sha")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--length", type=int, default=12000)
    args = parser.parse_args()
    if args.offset < 0 or not 0 < args.length <= 12000:
        raise ValueError("invalid page bounds")
    if args.command == "prepare":
        print(json.dumps(prepare(args.root, args.repository)))
    elif args.command == "state":
        value = session(args.root, args.plan_id)
        print(json.dumps({key: value[key] for key in ("blobs", "trees", "commits", "progress")}))
    elif args.command == "progress":
        print(json.dumps(record_progress(args.root, args.plan_id, args.kind, args.sha, args.local_sha)))
    elif args.command == "plan":
        value = session(args.root, args.plan_id)["plan"] if args.plan_id else plan(args.root)
        content = json.dumps(value, ensure_ascii=True)
        print(json.dumps({"total": len(content), "chunk": content[args.offset:args.offset + args.length]}, ensure_ascii=False))
    elif args.command == "accept":
        print(json.dumps(accept(args.root, args.sha)))
    else:
        print(json.dumps(blob_page(args.root, args.sha, args.offset, args.length, args.plan_id)))


if __name__ == "__main__":
    main()
