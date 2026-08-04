from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = REPO_ROOT / "queue" / "words.csv"


def _read_queue() -> list[dict[str, str]]:
    with QUEUE_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
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
