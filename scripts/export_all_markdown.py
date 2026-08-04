from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = REPO_ROOT / "queue" / "words.csv"
OUTPUT_PATH = REPO_ROOT / "exports" / "dictionary_all.md"
INCLUDED_STATUSES = {"checked", "final"}


def _resolve_entry(file_value: str) -> Path:
    path = Path(file_value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _read_queue() -> list[dict[str, str]]:
    with QUEUE_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    if not QUEUE_PATH.is_file():
        print(f"ERROR: queue file not found: {QUEUE_PATH}")
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    included = 0
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as output:
        output.write("# Dictionary Export\n\n")
        for row in _read_queue():
            status = (row.get("status") or "").strip()
            if status not in INCLUDED_STATUSES:
                continue
            headword = row.get("headword") or "(unknown)"
            file_value = row.get("file") or ""
            path = _resolve_entry(file_value)
            if not path.is_file():
                print(f"WARNING: skipped missing file for {headword}: {file_value}")
                continue
            content = path.read_text(encoding="utf-8").strip()
            output.write(f"\n---\n\n# {headword}\n\n")
            output.write(content)
            output.write("\n")
            included += 1

    print(f"Wrote {OUTPUT_PATH} ({included} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
