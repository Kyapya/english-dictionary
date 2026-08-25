from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "instruction_budget_measurement_v1"
DEFAULT_OUTPUT = (
    REPO_ROOT / "process_improvement" / "records" / "process-refactor-v1.json"
)
BACKUP = REPO_ROOT / "backups" / "2026-08-25-process-refactor"


def _bytes(paths: list[str], repo_root: Path) -> int:
    return sum((repo_root / path).stat().st_size for path in paths)


def measurement(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    before_files = [
        "backups/2026-08-25-process-refactor/AGENTS.md",
        "backups/2026-08-25-process-refactor/prompts/entry_spec_v5.md",
        "backups/2026-08-25-process-refactor/prompts/check_spec_v5.md",
        "backups/2026-08-25-process-refactor/prompts/final_review_spec_v1.md",
    ]
    pass_files = [
        path.relative_to(repo_root).as_posix()
        for path in sorted((repo_root / "prompts").glob("check_pass_*_v6.md"))
    ]
    after_files = [
        "AGENTS.md",
        "prompts/entry_spec_v5.md",
        "process_improvement/ACTIVE.md",
        "prompts/check_router_v6.md",
        *pass_files,
        "prompts/cold_review_prompt_v1.md",
        "prompts/final_blind_prompt_v2.md",
        "prompts/finding_resolution_v6.md",
        "prompts/final_review_spec_v2.md",
    ]
    bundles = [
        {
            "execution": "coordinator_router",
            "files": ["AGENTS.md"],
        },
        {
            "execution": "generation",
            "files": [
                "prompts/entry_spec_v5.md",
                "process_improvement/ACTIVE.md",
            ],
        },
        {
            "execution": "checker_router",
            "files": ["prompts/check_router_v6.md"],
        },
        *[
            {
                "execution": f"check_pass:{Path(path).stem}",
                "files": [path],
            }
            for path in pass_files
        ],
        {
            "execution": "cold_review",
            "files": ["prompts/cold_review_prompt_v1.md"],
        },
        {
            "execution": "final_blind",
            "files": ["prompts/final_blind_prompt_v2.md"],
        },
        {
            "execution": "finding_resolution",
            "files": ["prompts/finding_resolution_v6.md"],
        },
        {
            "execution": "final_review",
            "files": ["prompts/final_review_spec_v2.md"],
        },
    ]
    for bundle in bundles:
        bundle["instruction_bytes"] = _bytes(bundle["files"], repo_root)
    before_total = _bytes(before_files, repo_root)
    after_total = _bytes(after_files, repo_root)
    max_after = max(int(bundle["instruction_bytes"]) for bundle in bundles)
    return {
        "schema_version": SCHEMA_VERSION,
        "record_id": "process-refactor-v1",
        "measured_at": "2026-08-25",
        "method": (
            "各構成で1語の処理に必読となる指示ファイルをbytesで合計し、"
            "v6は実行境界ごとのbundleも同じファイル実体から計測する。"
        ),
        "before": {
            "files": before_files,
            "required_instruction_bytes_per_word": before_total,
            "max_instruction_bytes_in_one_execution": before_total,
        },
        "after": {
            "files": after_files,
            "required_instruction_bytes_per_word": after_total,
            "max_instruction_bytes_in_one_execution": max_after,
            "execution_bundles": bundles,
        },
        "effect": {
            "bytes_reduced_per_word": before_total - after_total,
            "percent_reduced_per_word": round(
                (before_total - after_total) / before_total * 100, 2
            ),
            "max_execution_bytes_reduced": before_total - max_after,
            "max_execution_percent_reduced": round(
                (before_total - max_after) / before_total * 100, 2
            ),
        },
    }


def validate_record(path: Path, repo_root: Path = REPO_ROOT) -> list[str]:
    try:
        actual = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read instruction-budget record: {exc}"]
    expected = measurement(repo_root)
    if actual != expected:
        return [
            "instruction-budget record is stale; run "
            "python scripts/measure_instruction_budget.py render"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure process-refactor instruction bytes")
    parser.add_argument("command", choices=("render", "validate", "show"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.command == "render":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(measurement(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(args.output.relative_to(REPO_ROOT))
        return 0
    if args.command == "show":
        print(json.dumps(measurement(), ensure_ascii=False, indent=2))
        return 0
    errors = validate_record(args.output)
    if not errors:
        print("Instruction-budget measurement passed.")
        return 0
    for error in errors:
        print(error, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
