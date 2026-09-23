"""Read-only environment checks to run before creating a dictionary workflow."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def inspect(root: Path) -> dict:
    errors, warnings = [], []
    if sys.version_info < (3, 12):
        errors.append("Python 3.12+ required; select an installed interpreter explicitly")
    if not shutil.which("git"):
        errors.append("Git is unavailable")
    else:
        result = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                                capture_output=True, text=True, encoding="utf-8", timeout=30)
        if result.returncode:
            errors.append("Git cannot inspect this workspace: " + result.stderr.strip())
        elif result.stdout:
            warnings.append("Worktree has changes; isolate/preserve them before starting a word run")
        shallow = subprocess.run(["git", "-C", str(root), "rev-parse", "--is-shallow-repository"],
                                 capture_output=True, text=True, timeout=30)
        if shallow.stdout.strip() == "true":
            warnings.append("Shallow history: fetch required ancestors before chronology/fixture tests")
    if not shutil.which("node"):
        warnings.append("Node unavailable: connector adapter regression tests cannot run")
    if not sys.flags.utf8_mode:
        warnings.append("Use python -X utf8, or PYTHONUTF8=1, including child processes")
    if os.name == "nt" and len(str(root)) > 80:
        warnings.append("Long Windows workspace path: use a short worktree or enable core.longpaths locally")
    return {"python": sys.executable, "platform": sys.platform, "errors": errors, "warnings": warnings,
            "authorization": "No write credential checks, uploads, provider calls, or transport changes performed"}


if __name__ == "__main__":
    report = inspect(Path(__file__).resolve().parents[1])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(bool(report["errors"]))
