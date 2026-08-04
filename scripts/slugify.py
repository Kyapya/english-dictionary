from __future__ import annotations

import argparse
import re
import unicodedata


APOSTROPHES = "'\u2018\u2019\u02bc\u2032`"


def slugify(headword: str) -> str:
    """Convert a headword into a filesystem-friendly slug."""
    value = unicodedata.normalize("NFKD", headword.strip().lower())
    for mark in APOSTROPHES:
        value = value.replace(mark, "")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "entry"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a slug from an English headword.")
    parser.add_argument("headword", help="English word or short phrase")
    args = parser.parse_args()
    print(slugify(args.headword))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
