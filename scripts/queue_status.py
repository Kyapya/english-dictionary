from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = REPO_ROOT / "queue" / "words.csv"
ESCAPED_DEFECTS_PATH = REPO_ROOT / "audits" / "escaped_defects.json"
ESCAPED_TAXONOMY_PATH = REPO_ROOT / "audits" / "escaped_defect_taxonomy.json"


def _read_queue() -> list[dict[str, str]]:
    with QUEUE_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_escaped_defects(
    value: object,
    taxonomy: object,
    *,
    runs_root: Path,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict) or value.get("schema_version") != "escaped_defects_v1":
        return ["escaped defects schema_version must be escaped_defects_v1"]
    defects = value.get("defects")
    if not isinstance(defects, list):
        return ["escaped defects registry must contain a defects list"]
    categories = taxonomy.get("categories") if isinstance(taxonomy, dict) else None
    if not isinstance(categories, list):
        return ["escaped defect taxonomy must contain categories"]
    expected: dict[str, set[str]] = {}
    for index, item in enumerate(categories):
        if not isinstance(item, dict) or not item.get("id"):
            errors.append(f"taxonomy categories[{index}].id is required")
            continue
        taxonomy_id = str(item["id"])
        stages = item.get("expected_detection_stages")
        if not isinstance(stages, list) or not stages or not all(
            isinstance(stage, str) and stage for stage in stages
        ):
            errors.append(
                f"taxonomy category {taxonomy_id}.expected_detection_stages "
                "must be a non-empty string list"
            )
            continue
        if taxonomy_id in expected:
            errors.append(f"taxonomy category id is duplicated: {taxonomy_id}")
        expected[taxonomy_id] = set(stages)
    seen: set[str] = set()
    for index, item in enumerate(defects):
        label = f"defects[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        for key in (
            "id",
            "headword",
            "taxonomy_id",
            "location",
            "detected_by",
            "expected_stage",
            "run_id",
        ):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"{label}.{key} is required")
        defect_id = str(item.get("id", ""))
        if defect_id in seen:
            errors.append(f"{label}.id is duplicated: {defect_id}")
        seen.add(defect_id)
        taxonomy_id = str(item.get("taxonomy_id", ""))
        stage = str(item.get("expected_stage", ""))
        if taxonomy_id not in expected:
            errors.append(f"{label}.taxonomy_id is unknown: {taxonomy_id}")
        elif stage not in expected[taxonomy_id]:
            errors.append(
                f"{label}.expected_stage {stage!r} is not registered for {taxonomy_id}"
            )
        if item.get("detected_by") != "external":
            errors.append(f"{label}.detected_by must be external")
        run_id = str(item.get("run_id", ""))
        if run_id and not any(path.is_dir() for path in runs_root.glob(f"*/*/{run_id}")):
            errors.append(f"{label}.run_id does not resolve to a preserved run")
    return errors


def escaped_defect_stage_counts(
    path: Path = ESCAPED_DEFECTS_PATH,
    taxonomy_path: Path = ESCAPED_TAXONOMY_PATH,
) -> Counter[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    errors = validate_escaped_defects(
        value, taxonomy, runs_root=path.parent / "runs"
    )
    if errors:
        raise ValueError("; ".join(errors))
    defects = value["defects"]
    return Counter(
        str(item.get("expected_stage") or "(blank)")
        for item in defects
        if isinstance(item, dict)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Show queue or escaped-defect status")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("escaped-by-stage")
    args = parser.parse_args(argv)
    if args.command == "escaped-by-stage":
        if not ESCAPED_DEFECTS_PATH.is_file():
            print(f"ERROR: escaped defects file not found: {ESCAPED_DEFECTS_PATH}")
            return 1
        try:
            counts = escaped_defect_stage_counts()
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"ERROR: {exc}")
            return 1
        print("Escaped defects by expected detection stage")
        for stage in sorted(counts):
            print(f"- {stage}: {counts[stage]}")
        return 0
    if not QUEUE_PATH.is_file():
        print(f"ERROR: queue file not found: {QUEUE_PATH}")
        return 1

    rows = _read_queue()
    counts = Counter((row.get("status") or "(blank)").strip() or "(blank)" for row in rows)
    prompt_counts = Counter(
        (row.get("prompt_version") or "(blank)").strip() or "(blank)" for row in rows
    )

    print("Status counts")
    if counts:
        for status in sorted(counts):
            print(f"- {status}: {counts[status]}")
    else:
        print("- (none): 0")

    print()
    print("Prompt version counts")
    if prompt_counts:
        for version in sorted(prompt_counts):
            print(f"- {version}: {prompt_counts[version]}")
    else:
        print("- (none): 0")

    pending_rows = [row for row in rows if (row.get("status") or "").strip() == "pending"]
    print()
    print("First pending entries")
    if not pending_rows:
        print("- none")
    for row in pending_rows[:10]:
        priority = row.get("priority") or ""
        headword = row.get("headword") or ""
        file_value = row.get("file") or ""
        print(f"- {priority}\t{headword}\t{file_value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
