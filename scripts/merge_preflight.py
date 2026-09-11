"""Check review history before a merge, and recheck the actual merged commit.

This tool never merges, changes repository settings, or weakens protection rules.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def validate(base: str, head: str, method: str, root: Path) -> list[str]:
    from content_audit import validate_changed
    errors = []
    names = subprocess.check_output(
        ["git", "diff", "--name-only", base, head], cwd=root, text=True, encoding="utf-8"
    ).splitlines()
    reviewed = [p for p in names if p.startswith("audits/runs/")
                and p.endswith(("/final_blind.json", "/blind_seal.json", "/final_review.json"))]
    if reviewed and method != "merge":
        errors.append("review chronology requires merge commits; squash/rebase cannot preserve the verified ancestry")
    errors.extend(validate_changed(base, head, root))
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--method", choices=("merge", "squash", "rebase"), default="merge")
    args = parser.parse_args()
    errors = validate(args.base, args.head, args.method, Path(__file__).resolve().parents[1])
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))
