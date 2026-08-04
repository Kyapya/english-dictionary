from __future__ import annotations

import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = REPO_ROOT / "queue" / "words.csv"
ENTRIES_DIR = REPO_ROOT / "entries"
REQUIRED_QUEUE_COLUMNS = {
    "headword",
    "type",
    "status",
    "priority",
    "file",
    "prompt_version",
    "model",
    "created_at",
    "updated_at",
    "checked",
    "notes",
}
STATUSES_REQUIRING_FILES = {
    "draft",
    "format_error",
    "needs_review",
    "checked",
    "final",
}

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from validate_entry import _front_matter_values, _split_front_matter  # noqa: E402


def _entry_front_matter(path: Path) -> dict[str, str]:
    front_matter, _ = _split_front_matter(path.read_text(encoding="utf-8"))
    if front_matter is None:
        return {}
    return _front_matter_values(front_matter)


def validate_repository(repo_root: Path = REPO_ROOT) -> list[str]:
    queue_path = repo_root / "queue" / "words.csv"
    entries_dir = repo_root / "entries"
    errors: list[str] = []
    if not queue_path.is_file():
        return [f"queue file not found: {queue_path}"]

    with queue_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        rows = list(reader)

    missing_columns = sorted(REQUIRED_QUEUE_COLUMNS - fieldnames)
    if missing_columns:
        errors.append(f"queue is missing columns: {', '.join(missing_columns)}")

    seen_headwords: dict[str, int] = {}
    seen_files: dict[str, int] = {}
    queued_files: set[str] = set()

    for line_number, row in enumerate(rows, start=2):
        headword = (row.get("headword") or "").strip()
        status = (row.get("status") or "").strip()
        file_value = (row.get("file") or "").strip().replace("\\", "/")
        checked = (row.get("checked") or "").strip().lower()

        if not headword:
            errors.append(f"queue line {line_number}: blank headword")
        headword_key = headword.casefold()
        if headword_key in seen_headwords:
            errors.append(
                f"queue line {line_number}: duplicate headword {headword!r}; "
                f"first seen on line {seen_headwords[headword_key]}"
            )
        else:
            seen_headwords[headword_key] = line_number

        if status in {"checked", "final"} and checked != "true":
            errors.append(
                f"queue line {line_number}: status {status} requires checked=true"
            )

        if not file_value:
            if status in STATUSES_REQUIRING_FILES:
                errors.append(
                    f"queue line {line_number}: status {status} requires a file path"
                )
            continue

        if file_value in seen_files:
            errors.append(
                f"queue line {line_number}: duplicate file {file_value!r}; "
                f"first seen on line {seen_files[file_value]}"
            )
        else:
            seen_files[file_value] = line_number
        queued_files.add(file_value)

        relative_path = Path(file_value)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            errors.append(f"queue line {line_number}: unsafe file path {file_value!r}")
            continue
        if not file_value.startswith("entries/") or relative_path.suffix.lower() != ".md":
            errors.append(
                f"queue line {line_number}: file must be an entries/*.md path: {file_value!r}"
            )
            continue

        entry_path = repo_root / relative_path
        if not entry_path.is_file():
            if status in STATUSES_REQUIRING_FILES:
                errors.append(
                    f"queue line {line_number}: entry file not found: {file_value}"
                )
            continue

        front = _entry_front_matter(entry_path)
        comparisons = {
            "headword": headword,
            "status": status,
            "prompt_version": (row.get("prompt_version") or "").strip(),
            "checked": checked,
        }
        for key, expected in comparisons.items():
            actual = (front.get(key) or "").strip().lower() if key == "checked" else (front.get(key) or "").strip()
            if actual != expected:
                errors.append(
                    f"queue line {line_number}: {file_value} front matter {key}={actual!r} "
                    f"does not match queue value {expected!r}"
                )

    if entries_dir.is_dir():
        for entry_path in sorted(entries_dir.rglob("*.md")):
            relative = entry_path.relative_to(repo_root).as_posix()
            if relative not in queued_files:
                errors.append(f"entry is not listed in queue: {relative}")

    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        print("Repository consistency validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Repository consistency validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

