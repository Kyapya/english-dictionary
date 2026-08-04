from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_HEADINGS = [
    "＃発音記号",
    "＃語源",
    "＃語形成",
    "＃意味や関連情報の出力（日本語訳）",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _split_front_matter(text: str) -> tuple[list[str] | None, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], "\n".join(lines[index + 1 :])
    return None, text


def _has_key(front_matter: list[str], key: str) -> bool:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$")
    return any(pattern.match(line) for line in front_matter)


def _next_nonempty(lines: list[str], start: int, count: int) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped:
            found.append((index, stripped))
        if len(found) == count:
            break
    return found


def _check_headings(lines: list[str]) -> list[str]:
    errors: list[str] = []
    positions: list[int] = []
    for heading in REQUIRED_HEADINGS:
        matches = [index for index, line in enumerate(lines) if line.strip() == heading]
        if not matches:
            errors.append(f"missing required heading: {heading}")
            continue
        positions.append(matches[0])

    if len(positions) == len(REQUIRED_HEADINGS) and positions != sorted(positions):
        expected = " -> ".join(REQUIRED_HEADINGS)
        errors.append(f"heading order is wrong; expected {expected}")
    return errors


def _check_example_translation_balance(lines: list[str]) -> list[str]:
    example_count = sum(1 for line in lines if line.strip().startswith("例:"))
    translation_count = sum(1 for line in lines if line.strip().startswith("訳:"))
    if max(example_count, translation_count) == 0:
        return []
    if abs(example_count - translation_count) > 1:
        return [
            "example/translation count looks unbalanced: "
            f"例:={example_count}, 訳:={translation_count}"
        ]
    return []


def _check_collocation_blocks(lines: list[str]) -> list[str]:
    errors: list[str] = []
    for index, line in enumerate(lines):
        if not line.strip().startswith("【コロケーション】"):
            continue
        block = _next_nonempty(lines, index + 1, 4)
        if len(block) < 4:
            errors.append(f"line {index + 1}: collocation block has fewer than 4 non-empty lines")
            continue
        block_lines = [text for _, text in block]
        if not block_lines[0].startswith("・"):
            errors.append(f"line {block[0][0] + 1}: collocation pattern should start with ・")
        if block_lines[1].startswith(("・", "例:", "訳:")):
            errors.append(f"line {block[1][0] + 1}: collocation usage memo is missing or misplaced")
        if not block_lines[2].startswith("例:"):
            errors.append(f"line {block[2][0] + 1}: collocation third line should start with 例:")
        if not block_lines[3].startswith("訳:"):
            errors.append(f"line {block[3][0] + 1}: collocation fourth line should start with 訳:")
    return errors


def _check_relation_blocks(lines: list[str], marker: str) -> list[str]:
    errors: list[str] = []
    expected = [
        ("・", "entry term"),
        ("定義:", "definition"),
        ("頻度:", "frequency"),
        ("違い:", "difference"),
        ("例:", "example"),
        ("訳:", "translation"),
    ]
    for index, line in enumerate(lines):
        if not line.strip().startswith(marker):
            continue
        block = _next_nonempty(lines, index + 1, 6)
        if len(block) < 6:
            errors.append(f"line {index + 1}: {marker} block has fewer than 6 non-empty lines")
            continue
        for (line_index, text), (prefix, label) in zip(block, expected):
            if not text.startswith(prefix):
                errors.append(
                    f"line {line_index + 1}: {marker} {label} line should start with {prefix}"
                )
    return errors


def validate_text(text: str) -> list[str]:
    errors: list[str] = []
    front_matter, body = _split_front_matter(text)
    if front_matter is None:
        errors.append("missing YAML front matter delimited by ---")
    else:
        for key in ("headword", "status"):
            if not _has_key(front_matter, key):
                errors.append(f"front matter is missing {key}:")

    lines = body.splitlines()
    errors.extend(_check_headings(lines))
    errors.extend(_check_example_translation_balance(lines))
    errors.extend(_check_collocation_blocks(lines))
    errors.extend(_check_relation_blocks(lines, "【類義語】"))
    errors.extend(_check_relation_blocks(lines, "【反意語】"))
    return errors


def validate_file(path: Path) -> list[str]:
    return validate_text(_read_text(path))


def _resolve_target(raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return REPO_ROOT / path


def _collect_markdown_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(path for path in target.rglob("*.md") if path.is_file())
    raise FileNotFoundError(target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate dictionary entry Markdown format.")
    parser.add_argument(
        "target",
        nargs="?",
        default="entries",
        help="Markdown file or directory to validate. Defaults to entries/.",
    )
    args = parser.parse_args(argv)

    target = _resolve_target(args.target)
    try:
        files = _collect_markdown_files(target)
    except FileNotFoundError:
        print(f"ERROR: target not found: {target}", file=sys.stderr)
        return 1

    if not files:
        print(f"No Markdown files found under {target}")
        return 0

    failed = False
    for path in files:
        errors = validate_file(path)
        label = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        if errors:
            failed = True
            print(f"ERROR {label}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK {label}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
