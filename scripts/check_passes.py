from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTER_PATH = REPO_ROOT / "prompts" / "check_router_v6.md"
TAXONOMY_PATH = REPO_ROOT / "audits" / "escaped_defect_taxonomy.json"
ROUTER_BEGIN = "<!-- CHECK_ROUTER_V6_JSON_BEGIN -->"
ROUTER_END = "<!-- CHECK_ROUTER_V6_JSON_END -->"
SENSE_PATTERN = re.compile(r"^\d+\.\s+【")
MAIN_HEADING_PATTERN = re.compile(r"^＃")


@dataclass(frozen=True)
class LocatedLine:
    number: int
    text: str


def _digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_router(path: Path = ROUTER_PATH) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if ROUTER_BEGIN not in text or ROUTER_END not in text:
        raise ValueError("check router is missing its machine-readable block")
    block = text.split(ROUTER_BEGIN, 1)[1].split(ROUTER_END, 1)[0]
    match = re.search(r"```json\s*(\{.*\})\s*```", block, re.DOTALL)
    if match is None:
        raise ValueError("check router JSON block is invalid")
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("check router must be a JSON object")
    return value


def load_taxonomy(path: Path = TAXONOMY_PATH) -> set[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(item["id"])
        for item in value.get("categories", [])
        if isinstance(item, dict) and item.get("id")
    }


def validate_router(
    router: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    taxonomy_ids: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    if router.get("schema_version") != "check_router_v6":
        errors.append("router schema_version must be check_router_v6")
    taxonomy = taxonomy_ids if taxonomy_ids is not None else load_taxonomy(
        repo_root / "audits" / "escaped_defect_taxonomy.json"
    )
    excluded = router.get("excluded_process_categories")
    expected_excluded = {
        "finding_scope_transfer_loss",
        "raw_adjudication_manifest_divergence",
    }
    if not isinstance(excluded, list) or set(excluded) != expected_excluded:
        errors.append("router must exclude exactly the two process-defect categories")
        excluded = []
    passes = router.get("passes")
    if not isinstance(passes, list) or not passes:
        return [*errors, "router passes must be a non-empty list"]
    seen_passes: set[str] = set()
    owners: dict[str, str] = {}
    for item in passes:
        if not isinstance(item, dict):
            errors.append("router pass must be an object")
            continue
        pass_id = str(item.get("id", ""))
        if not pass_id or pass_id in seen_passes:
            errors.append(f"router pass id is missing or duplicated: {pass_id}")
        seen_passes.add(pass_id)
        specification = item.get("specification")
        if not isinstance(specification, str) or not (
            repo_root / specification
        ).is_file():
            errors.append(f"{pass_id}: specification file is missing")
        elif (repo_root / specification).stat().st_size > 15_000:
            errors.append(f"{pass_id}: specification exceeds 15000 bytes")
        sections = item.get("sections")
        if not isinstance(sections, list) or not sections:
            errors.append(f"{pass_id}: sections must be a non-empty list")
        category_ids = item.get("taxonomy_ids")
        if not isinstance(category_ids, list) or not category_ids:
            errors.append(f"{pass_id}: taxonomy_ids must be a non-empty list")
            continue
        for category in category_ids:
            if category in owners:
                errors.append(
                    f"taxonomy category {category} belongs to both "
                    f"{owners[category]} and {pass_id}"
                )
            owners[str(category)] = pass_id
    content_categories = taxonomy - set(excluded)
    routed = set(owners)
    for category in sorted(content_categories - routed):
        errors.append(f"unrouted content taxonomy category: {category}")
    for category in sorted(routed - content_categories):
        errors.append(f"non-content or unknown category routed to a pass: {category}")
    return errors


def _split_front_matter(text: str) -> tuple[int, list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return 0, lines
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return index + 1, lines[index + 1 :]
    return 0, lines


def _main_sections(
    body_start: int, lines: list[str]
) -> dict[str, list[LocatedLine]]:
    mapping = {
        "＃発音記号": "pronunciation",
        "＃語源": "etymology",
        "＃語形成": "word_formation",
        "＃コアイメージ": "core_image",
        "＃意味・用法・関連表現": "senses",
        "＃意味や関連情報の出力（日本語訳）": "senses",
    }
    sections: dict[str, list[LocatedLine]] = {
        name: [] for name in mapping.values()
    }
    active: str | None = None
    for offset, raw in enumerate(lines):
        stripped = raw.strip()
        if MAIN_HEADING_PATTERN.match(stripped):
            active = mapping.get(stripped)
        if active:
            sections[active].append(LocatedLine(body_start + offset + 1, raw))
    return sections


def _sense_blocks(lines: list[LocatedLine]) -> list[list[LocatedLine]]:
    blocks: list[list[LocatedLine]] = []
    current: list[LocatedLine] = []
    for line in lines:
        if SENSE_PATTERN.match(line.text.strip()):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _select_label_lines(
    blocks: list[list[LocatedLine]],
    labels: tuple[str, ...],
    *,
    grouped_size: int | None = None,
) -> list[LocatedLine]:
    selected: list[LocatedLine] = []
    for block in blocks:
        if not block:
            continue
        selected.append(block[0])
        index = 1
        while index < len(block):
            stripped = block[index].text.strip()
            if any(stripped.startswith(label) for label in labels):
                selected.append(block[index])
                if grouped_size is not None:
                    count = 0
                    cursor = index + 1
                    while cursor < len(block):
                        candidate = block[cursor]
                        candidate_text = candidate.text.strip()
                        if (
                            SENSE_PATTERN.match(candidate_text)
                            or candidate_text.startswith("【")
                        ):
                            break
                        if candidate_text:
                            selected.append(candidate)
                            count += 1
                        if count and count % grouped_size == 0:
                            # Continue: the section can contain multiple fixed blocks.
                            pass
                        cursor += 1
                    index = cursor
                    continue
            index += 1
    return selected


def extract_sections(text: str) -> dict[str, list[dict[str, Any]]]:
    body_start, body_lines = _split_front_matter(text)
    main = _main_sections(body_start, body_lines)
    blocks = _sense_blocks(main.get("senses", []))
    result: dict[str, list[LocatedLine]] = {
        "pronunciation": main.get("pronunciation", []),
        "etymology": main.get("etymology", []),
        "word_formation": main.get("word_formation", []),
        "core_image": main.get("core_image", []),
        "sense_structure": _select_label_lines(
            blocks, ("【日本語訳・定義】",)
        ),
        "definitions": _select_label_lines(
            blocks, ("【日本語訳・定義】",)
        ),
        "frequency_register": _select_label_lines(
            blocks, ("【頻度】", "【レジスター/領域】")
        ),
        "frames": _select_label_lines(blocks, ("【文法パターン】",)),
        "collocations_examples": _select_label_lines(
            blocks, ("【コロケーション】",), grouped_size=4
        ),
        "usage_notes": _select_label_lines(blocks, ("【語法・注意】",)),
        "lexical_relations": _select_label_lines(
            blocks, ("【類義語】", "【反意語】"), grouped_size=6
        ),
    }
    return {
        key: [
            {"line": item.number, "text": item.text}
            for item in value
            if item.text.strip()
        ]
        for key, value in result.items()
    }


def build_bundles(
    entry_path: Path,
    *,
    repo_root: Path = REPO_ROOT,
    router_path: Path | None = None,
) -> list[dict[str, Any]]:
    resolved = entry_path.resolve()
    raw = resolved.read_bytes()
    text = raw.decode("utf-8")
    _, body_lines = _split_front_matter(text)
    # Keep this canonicalization identical to generate_audit_manifest.body_sha256:
    # front matter is removed and split lines are rejoined without inventing a
    # trailing newline.  A stage-specific hash would make an unchanged body look
    # stale when checker output is handed to final manifest generation.
    body_bytes = "\n".join(body_lines).encode("utf-8")
    sections = extract_sections(text)
    router = load_router(router_path or (repo_root / "prompts" / "check_router_v6.md"))
    errors = validate_router(router, repo_root=repo_root)
    if errors:
        raise ValueError("; ".join(errors))
    bundles: list[dict[str, Any]] = []
    for check_pass in router["passes"]:
        selected = {
            section: sections.get(section, [])
            for section in check_pass["sections"]
        }
        bundles.append(
            {
                "schema_version": "check_pass_request_v6",
                "pass_id": check_pass["id"],
                "taxonomy_ids": list(check_pass["taxonomy_ids"]),
                "specification": check_pass["specification"],
                "input_body_sha256": _digest_bytes(body_bytes),
                "input_sections": selected,
                "finding_schema": router["finding_schema"],
            }
        )
    return bundles


def validate_pass_output(
    output: dict[str, Any], router: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    by_id = {
        item["id"]: item
        for item in router.get("passes", [])
        if isinstance(item, dict) and item.get("id")
    }
    pass_id = output.get("pass_id")
    if pass_id not in by_id:
        return [f"unknown pass_id: {pass_id}"]
    allowed = set(by_id[pass_id]["taxonomy_ids"])
    findings = output.get("findings")
    if not isinstance(findings, list):
        return ["findings must be a list"]
    for index, finding in enumerate(findings):
        label = f"findings[{index}]"
        if not isinstance(finding, dict):
            errors.append(f"{label} must be an object")
            continue
        required = {"taxonomy_id", "location", "severity", "rationale"}
        missing = required - set(finding)
        if missing:
            errors.append(f"{label} missing fields: {sorted(missing)}")
        if finding.get("taxonomy_id") not in allowed:
            errors.append(
                f"{label}.taxonomy_id is not owned by pass {pass_id}"
            )
        if finding.get("severity") not in {"blocking", "minor"}:
            errors.append(f"{label}.severity is invalid")
        location = finding.get("location")
        if not isinstance(location, dict):
            errors.append(f"{label}.location must be an object")
        else:
            for key in ("section", "line_start", "line_end", "exact_quote"):
                if location.get(key) in (None, ""):
                    errors.append(f"{label}.location.{key} is required")
    return errors


def write_bundles(
    bundles: list[dict[str, Any]], output_dir: Path
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for bundle in bundles:
        path = output_dir / f"{bundle['pass_id']}.request.json"
        path.write_text(
            json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def replay_regression_cases(
    cases_path: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> list[dict[str, Any]]:
    """Replay known defect locations against the v6 routing boundary.

    This is intentionally a structural regression: it verifies that a defect type
    which was found under v5 is still owned by one pass, and that the corrected
    location remains visible in that pass's section-limited input.  It does not
    pretend to re-create the original semantic adjudication with string matching.
    """
    payload = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("regression fixture must contain a non-empty cases list")
    router = load_router(repo_root / "prompts" / "check_router_v6.md")
    owners = {
        taxonomy_id: item["id"]
        for item in router["passes"]
        for taxonomy_id in item["taxonomy_ids"]
    }
    bundle_cache: dict[str, dict[str, dict[str, Any]]] = {}
    results: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("regression case must be an object")
        case_id = str(case.get("id", ""))
        word = str(case.get("word", ""))
        taxonomy_id = str(case.get("taxonomy_id", ""))
        quote = str(case.get("quote_fragment", ""))
        if not case_id or case_id in seen_ids:
            raise ValueError(f"regression case id is missing or duplicated: {case_id}")
        seen_ids.add(case_id)
        if taxonomy_id not in owners:
            raise ValueError(f"{case_id}: taxonomy category is not routed: {taxonomy_id}")
        entry_path = repo_root / "entries" / word[0].lower() / f"{word}.md"
        if not entry_path.is_file():
            raise ValueError(f"{case_id}: entry is missing: {entry_path}")
        if word not in bundle_cache:
            bundle_cache[word] = {
                item["pass_id"]: item
                for item in build_bundles(entry_path, repo_root=repo_root)
            }
        pass_id = owners[taxonomy_id]
        bundle = bundle_cache[word][pass_id]
        matches = [
            (section, line)
            for section, lines in bundle["input_sections"].items()
            for line in lines
            if quote in line["text"]
        ]
        if not matches:
            raise ValueError(
                f"{case_id}: known defect location is not visible to {pass_id}: {quote}"
            )
        section, line = matches[0]
        replay_output = {
            "pass_id": pass_id,
            "findings": [
                {
                    "taxonomy_id": taxonomy_id,
                    "location": {
                        "section": section,
                        "line_start": line["line"],
                        "line_end": line["line"],
                        "exact_quote": line["text"],
                    },
                    "severity": "blocking",
                    "rationale": "v5で確認済みの欠陥種をv6入力境界で再現",
                }
            ],
        }
        validation_errors = validate_pass_output(replay_output, router)
        if validation_errors:
            raise ValueError(f"{case_id}: " + "; ".join(validation_errors))
        results.append(
            {
                "id": case_id,
                "word": word,
                "taxonomy_id": taxonomy_id,
                "owner_pass": pass_id,
                "visible_section": section,
                "line": line["line"],
                "status": "PASS",
            }
        )
    return results


def render_regression_log(
    results: list[dict[str, Any]], cases_path: Path
) -> str:
    words = sorted({str(item["word"]) for item in results})
    lines = [
        "# v6 checker-pass regression trial (2026-08-25)",
        "",
        "- 対象: " + ", ".join(words),
        f"- ケース定義: `{cases_path.as_posix()}`",
        "- 方法: v5監査で確認済みの欠陥種について、現在の修正版本文に残る対応位置が、担当v6パスのsection限定入力に含まれ、finding schemaを通過することを再生検証した。",
        "- 注意: 文字列一致で辞書学的判断を代替するものではなく、既知の検査観点が分割時に脱落していないことを確認する構造回帰である。",
        "",
        "| case | word | taxonomy | owner pass | visible section | line | result |",
        "|---|---|---|---|---|---:|---|",
    ]
    for item in results:
        lines.append(
            "| {id} | {word} | `{taxonomy_id}` | `{owner_pass}` | "
            "`{visible_section}` | {line} | {status} |".format(**item)
        )
    lines.extend(
        [
            "",
            f"結果: {len(results)}/{len(results)} PASS。既知欠陥種の担当パス不明・入力範囲外・schema不適合は0件。",
            "",
        ]
    )
    return "\n".join(lines)


def _print_errors(errors: list[str]) -> int:
    if not errors:
        print("Check-pass validation passed.")
        return 0
    print("Check-pass validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Route v6 checker passes")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-router")
    bundle = sub.add_parser("bundle")
    bundle.add_argument("entry", type=Path)
    bundle.add_argument("--output-dir", required=True, type=Path)
    validate = sub.add_parser("validate-output")
    validate.add_argument("output", type=Path)
    regression = sub.add_parser("regression")
    regression.add_argument("cases", type=Path)
    regression.add_argument("--output", type=Path)
    args = parser.parse_args()
    router = load_router()
    if args.command == "validate-router":
        return _print_errors(validate_router(router))
    if args.command == "bundle":
        paths = write_bundles(build_bundles(args.entry), args.output_dir)
        for path in paths:
            print(path)
        return 0
    if args.command == "regression":
        results = replay_regression_cases(args.cases)
        log = render_regression_log(results, args.cases)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(log, encoding="utf-8")
            print(args.output)
        else:
            print(log, end="")
        return 0
    output = json.loads(args.output.read_text(encoding="utf-8"))
    return _print_errors(validate_pass_output(output, router))


if __name__ == "__main__":
    raise SystemExit(main())
