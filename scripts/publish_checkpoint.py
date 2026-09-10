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
from pathlib import Path


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE).strip()


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
    remote_rows = git(root, "ls-remote", "--heads", "origin", "refs/heads/" + branch).split()
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
    return {"branch": branch, "branch_exists": bool(remote_rows), "remote_base": remote_base, "local_head": git(root, "rev-parse", "HEAD"), "commits": commits}


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
    parser.add_argument("command", choices=("plan", "blob", "accept"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--sha")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--length", type=int, default=12000)
    args = parser.parse_args()
    if args.command == "plan":
        content = json.dumps(plan(args.root), ensure_ascii=True)
        print(json.dumps({"total": len(content), "chunk": content[args.offset:args.offset + args.length]}, ensure_ascii=False))
    elif args.command == "accept":
        print(json.dumps(accept(args.root, args.sha)))
    else:
        if not args.sha or len(args.sha) != 40 or any(c not in "0123456789abcdef" for c in args.sha):
            raise ValueError("blob SHA must be a full Git object ID")
        raw = subprocess.check_output(["git", "-C", str(args.root), "cat-file", "blob", args.sha])
        content = base64.b64encode(raw).decode()
        print(json.dumps({"total": len(content), "chunk": content[args.offset:args.offset + args.length]}))


if __name__ == "__main__":
    main()
