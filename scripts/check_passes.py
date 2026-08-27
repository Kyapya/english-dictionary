from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import review_liveness


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


def _digest_json(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return _digest_bytes(encoded)


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


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


def _router_table_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_table = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped == "## パス対応表":
            in_table = True
            continue
        if in_table and stripped.startswith("## "):
            break
        if not in_table or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 3 or cells[0] in {"pass", "---"}:
            continue
        rows.append(
            {
                "id": cells[0],
                "taxonomy_ids": [
                    value.strip() for value in cells[1].split(",") if value.strip()
                ],
                "sections": [
                    value.strip() for value in cells[2].split(",") if value.strip()
                ],
            }
        )
    return rows


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
    router_path = repo_root / "prompts" / "check_router_v6.md"
    if router_path.is_file():
        table_rows = _router_table_rows(router_path)
        json_rows = [
            {
                "id": item.get("id"),
                "taxonomy_ids": item.get("taxonomy_ids"),
                "sections": item.get("sections"),
            }
            for item in passes
            if isinstance(item, dict)
        ]
        if table_rows != json_rows:
            errors.append("router pass table and machine-readable JSON must match exactly")
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


def _example_attribution_material(text: str) -> dict[str, list[dict[str, Any]]]:
    """Extract sense inventory plus example-only and private ownership views.

    The public example view deliberately excludes the owning block, collocation
    heading, and usage line.  The private ownership view is emitted separately
    so a coordinator can persist stage 1 before making stage 2 available.
    """
    body_start, body_lines = _split_front_matter(text)
    main = _main_sections(body_start, body_lines)
    blocks = _sense_blocks(main.get("senses", []))
    senses: list[dict[str, Any]] = []
    examples: list[dict[str, Any]] = []
    ownership: list[dict[str, Any]] = []
    usage_notes: list[dict[str, Any]] = []
    example_index = 0
    for sense_index, block in enumerate(blocks, start=1):
        if not block:
            continue
        sense_id = f"sense:{sense_index:03d}"
        definition = ""
        for line in block[1:]:
            stripped = line.text.strip()
            if stripped.startswith("【日本語訳・定義】"):
                definition = stripped.removeprefix("【日本語訳・定義】").strip()
                break
        senses.append(
            {
                "sense_id": sense_id,
                "line": block[0].number,
                "label": block[0].text.strip(),
                "definition": definition,
            }
        )
        for line in block[1:]:
            stripped = line.text.strip()
            if stripped.startswith("【語法・注意】"):
                usage_notes.append(
                    {
                        "sense_id": sense_id,
                        "line": line.number,
                        "text": stripped.removeprefix("【語法・注意】").strip(),
                    }
                )

        in_collocations = False
        group: list[LocatedLine] = []

        def flush_group() -> None:
            nonlocal example_index, group
            if not group:
                return
            example_line = next(
                (item for item in group if item.text.strip().startswith("例:")),
                None,
            )
            translation_line = next(
                (item for item in group if item.text.strip().startswith("訳:")),
                None,
            )
            if example_line is not None:
                example_index += 1
                example_id = f"example:{example_index:03d}"
                example_text = example_line.text.strip().removeprefix("例:").strip()
                translation = (
                    translation_line.text.strip().removeprefix("訳:").strip()
                    if translation_line is not None
                    else ""
                )
                examples.append(
                    {
                        "example_id": example_id,
                        "line": example_line.number,
                        "example": example_text,
                        "translation": translation,
                    }
                )
                ownership.append(
                    {
                        "example_id": example_id,
                        "assigned_sense_id": sense_id,
                        "anchor": {
                            "section": "collocations_examples",
                            "line_start": example_line.number,
                            "line_end": example_line.number,
                            "exact_quote": example_line.text,
                        },
                    }
                )
            group = []

        for line in block[1:]:
            stripped = line.text.strip()
            if stripped == "【コロケーション】":
                flush_group()
                in_collocations = True
                continue
            if stripped.startswith("【"):
                if in_collocations:
                    flush_group()
                in_collocations = False
                continue
            if not in_collocations or not stripped:
                continue
            if stripped.startswith("・") and group:
                flush_group()
            group.append(line)
        flush_group()
    return {
        "senses": senses,
        "examples": examples,
        "ownership": ownership,
        "usage_notes": usage_notes,
    }


def _example_attribution_request(
    text: str,
    body_bytes: bytes,
    check_pass: dict[str, Any],
    finding_schema: dict[str, Any],
    *,
    blind_seed: str,
) -> dict[str, Any]:
    material = _example_attribution_material(text)
    opaque_ids = {
        str(item["example_id"]): "ex-"
        + hashlib.sha256(
            f"{blind_seed}\0{item['example_id']}".encode("utf-8")
        ).hexdigest()[:12]
        for item in material["examples"]
    }
    examples = []
    for item in material["examples"]:
        public = {key: value for key, value in item.items() if key != "line"}
        public["translation"] = re.sub(
            r"[（(][^）)]*(?:語義|用法|意味)[^）)]*[）)]",
            "",
            str(public.get("translation", "")),
        ).strip()
        public["example_id"] = opaque_ids[str(item["example_id"])]
        examples.append(public)
    random.Random(blind_seed).shuffle(examples)
    return {
        "schema_version": "example_attribution_blind_request_v1",
        "pass_id": check_pass["id"],
        "taxonomy_ids": list(check_pass["taxonomy_ids"]),
        "specification": check_pass["specification"],
        "input_body_sha256": _digest_bytes(body_bytes),
        "input_sections": {
            "sense_structure": material["senses"],
            "collocations_examples": examples,
        },
        "blind_protocol": {
            "stage": 1,
            "withheld_fields": [
                "assigned_sense_id",
                "collocation_heading",
                "usage_line",
                "example_group_boundary",
                "document_order",
            ],
            "required_output_schema": "example_attribution_blind_record_v1",
        },
        "finding_schema": finding_schema,
    }


def build_example_attribution_alignment_key(
    entry_path: Path,
    *,
    repo_root: Path = REPO_ROOT,
    router_path: Path | None = None,
    blind_seed: str | None = None,
) -> dict[str, Any]:
    raw = entry_path.resolve().read_bytes()
    text = raw.decode("utf-8")
    _, body_lines = _split_front_matter(text)
    body_bytes = "\n".join(body_lines).encode("utf-8")
    router = load_router(router_path or (repo_root / "prompts" / "check_router_v6.md"))
    check_pass = next(
        item for item in router["passes"] if item["id"] == "example-attribution"
    )
    effective_seed = blind_seed or _digest_bytes(body_bytes)
    request = _example_attribution_request(
        text,
        body_bytes,
        check_pass,
        router["finding_schema"],
        blind_seed=effective_seed,
    )
    material = _example_attribution_material(text)
    opaque_ids = {
        str(item["example_id"]): "ex-"
        + hashlib.sha256(
            f"{effective_seed}\0{item['example_id']}".encode("utf-8")
        ).hexdigest()[:12]
        for item in material["examples"]
    }
    return {
        "schema_version": "example_attribution_alignment_key_v1",
        "pass_id": "example-attribution",
        "input_body_sha256": _digest_bytes(body_bytes),
        "blind_request_sha256": _digest_json(request),
        "shuffle_seed": effective_seed,
        "examples": [
            {
                **item,
                "source_example_id": item["example_id"],
                "example_id": opaque_ids[str(item["example_id"])],
            }
            for item in material["ownership"]
        ],
        "sense_usage_notes": material["usage_notes"],
    }


def build_legacy_example_attribution_artifacts(
    entry_path: Path,
    router: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Reconstruct pre-2026-08-27 artifacts only for immutable audit validation."""
    text = entry_path.resolve().read_text(encoding="utf-8")
    _, body_lines = _split_front_matter(text)
    body_bytes = "\n".join(body_lines).encode("utf-8")
    check_pass = next(
        item for item in router["passes"] if item["id"] == "example-attribution"
    )
    material = _example_attribution_material(text)
    request = {
        "schema_version": "example_attribution_blind_request_v1",
        "pass_id": check_pass["id"],
        "taxonomy_ids": list(check_pass["taxonomy_ids"]),
        "specification": check_pass["specification"],
        "input_body_sha256": _digest_bytes(body_bytes),
        "input_sections": {
            "sense_structure": material["senses"],
            "collocations_examples": material["examples"],
        },
        "blind_protocol": {
            "stage": 1,
            "withheld_fields": [
                "assigned_sense_id",
                "collocation_heading",
                "usage_line",
            ],
            "required_output_schema": "example_attribution_blind_record_v1",
        },
        "finding_schema": router["finding_schema"],
    }
    alignment = {
        "schema_version": "example_attribution_alignment_key_v1",
        "pass_id": "example-attribution",
        "input_body_sha256": _digest_bytes(body_bytes),
        "blind_request_sha256": _digest_json(request),
        "examples": material["ownership"],
        "sense_usage_notes": material["usage_notes"],
    }
    return request, alignment


def build_bundles(
    entry_path: Path,
    *,
    repo_root: Path = REPO_ROOT,
    router_path: Path | None = None,
    blind_seed: str | None = None,
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
    effective_seed = blind_seed or _digest_bytes(body_bytes)
    sections = extract_sections(text)
    router = load_router(router_path or (repo_root / "prompts" / "check_router_v6.md"))
    errors = validate_router(router, repo_root=repo_root)
    if errors:
        raise ValueError("; ".join(errors))
    bundles: list[dict[str, Any]] = []
    for check_pass in router["passes"]:
        if check_pass["id"] == "example-attribution":
            bundles.append(
                _example_attribution_request(
                    text,
                    body_bytes,
                    check_pass,
                    router["finding_schema"],
                    blind_seed=effective_seed,
                )
            )
            continue
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


def validate_blind_attribution_record(
    record: Any,
    request: dict[str, Any] | None = None,
    *,
    check_liveness: bool = True,
    generation_model: str | None = None,
    require_reviewer: bool = True,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["blind_attribution_record must be an object"]
    if record.get("schema_version") != "example_attribution_blind_record_v1":
        errors.append(
            "blind_attribution_record.schema_version must be "
            "example_attribution_blind_record_v1"
        )
    if record.get("pass_id") != "example-attribution":
        errors.append("blind_attribution_record.pass_id must be example-attribution")
    if require_reviewer or record.get("reviewer") is not None:
        errors.extend(
            review_liveness.validate_reviewer(
                record.get("reviewer"), generation_model=generation_model
            )
        )
        errors.extend(
            review_liveness.validate_api_request_binding(record.get("reviewer"), request)
        )
    recorded_at = _parse_timestamp(record.get("recorded_at"))
    if recorded_at is None:
        errors.append("blind_attribution_record.recorded_at must be an aware ISO timestamp")
    body_hash = record.get("input_body_sha256")
    if not isinstance(body_hash, str) or re.fullmatch(r"[0-9a-f]{64}", body_hash) is None:
        errors.append("blind_attribution_record.input_body_sha256 must be a sha256")
    request_hash = record.get("blind_request_sha256")
    if not isinstance(request_hash, str) or re.fullmatch(r"[0-9a-f]{64}", request_hash) is None:
        errors.append("blind_attribution_record.blind_request_sha256 must be a sha256")

    known_examples: set[str] | None = None
    known_senses: set[str] | None = None
    if request is not None:
        if body_hash != request.get("input_body_sha256"):
            errors.append("blind attribution body hash does not match its stage 1 request")
        if request_hash != _digest_json(request):
            errors.append("blind attribution request hash does not match stage 1 input")
        sections = request.get("input_sections", {})
        known_examples = {
            str(item.get("example_id"))
            for item in sections.get("collocations_examples", [])
            if isinstance(item, dict) and item.get("example_id")
        }
        known_senses = {
            str(item.get("sense_id"))
            for item in sections.get("sense_structure", [])
            if isinstance(item, dict) and item.get("sense_id")
        }

    attributions = record.get("attributions")
    if not isinstance(attributions, list):
        return [*errors, "blind_attribution_record.attributions must be a list"]
    seen: set[str] = set()
    for index, item in enumerate(attributions):
        label = f"blind_attribution_record.attributions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        example_id = str(item.get("example_id", ""))
        if not example_id or example_id in seen:
            errors.append(f"{label}.example_id is missing or duplicated")
        seen.add(example_id)
        classification = item.get("classification")
        if classification not in {"unique", "ambiguous"}:
            errors.append(f"{label}.classification must be unique or ambiguous")
        candidates = item.get("candidate_sense_ids")
        if not isinstance(candidates, list) or not all(
            isinstance(value, str) and value for value in candidates
        ):
            errors.append(f"{label}.candidate_sense_ids must be a non-empty string list")
            candidates = []
        elif len(candidates) != len(set(candidates)):
            errors.append(f"{label}.candidate_sense_ids contains duplicates")
        if classification == "unique" and len(candidates) != 1:
            errors.append(f"{label} unique classification requires exactly one candidate")
        if classification == "ambiguous" and len(candidates) < 2:
            errors.append(f"{label} ambiguous classification requires at least two candidates")
        terms = item.get("discriminating_terms")
        if not isinstance(terms, list) or not all(
            isinstance(value, str) and value for value in terms
        ):
            errors.append(f"{label}.discriminating_terms must be a string list")
            terms = []
        if classification == "unique" and not terms:
            errors.append(f"{label} unique classification requires discriminating terms")
        if classification == "ambiguous" and terms:
            errors.append(f"{label} ambiguous classification must not invent discriminating terms")
        if not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
            errors.append(f"{label}.rationale is required")
        if known_senses is not None:
            unknown = sorted(set(candidates) - known_senses)
            if unknown:
                errors.append(f"{label} references unknown senses: {', '.join(unknown)}")
    if known_examples is not None and seen != known_examples:
        missing = sorted(known_examples - seen)
        extra = sorted(seen - known_examples)
        if missing:
            errors.append("blind attribution record is missing examples: " + ", ".join(missing))
        if extra:
            errors.append("blind attribution record has unknown examples: " + ", ".join(extra))
    if request is not None and check_liveness:
        errors.extend(review_liveness.validate_attribution_liveness(record, request))
    return errors


def _attribution_findings(
    record: dict[str, Any], alignment_key: dict[str, Any]
) -> list[dict[str, Any]]:
    by_example = {
        str(item["example_id"]): item for item in record.get("attributions", [])
    }
    findings: list[dict[str, Any]] = []
    for owner in alignment_key.get("examples", []):
        example_id = str(owner["example_id"])
        attribution = by_example[example_id]
        candidates = list(attribution["candidate_sense_ids"])
        assigned = str(owner["assigned_sense_id"])
        if attribution["classification"] == "ambiguous":
            rationale = (
                f"段階1で{', '.join(candidates)}が同程度に自然と判定され、"
                "例文内に帰属を一意にする判別語がない。"
            )
            direction = "判別語の追加"
        elif candidates[0] != assigned:
            rationale = (
                f"段階1の最も自然な帰属は{candidates[0]}だが、"
                f"実際の所属は{assigned}である。"
            )
            direction = "語義ブロック間の移動"
        else:
            continue
        findings.append(
            {
                "taxonomy_id": "example_sense_attribution_mismatch",
                "location": dict(owner["anchor"]),
                "severity": "blocking",
                "rationale": rationale,
                "evidence_link_ids": [],
                "suggested_direction": direction,
            }
        )
    return findings


def reconcile_example_attribution(
    request: dict[str, Any],
    record: dict[str, Any],
    alignment_key: dict[str, Any],
    *,
    aligned_at: str,
) -> dict[str, Any]:
    errors = validate_blind_attribution_record(record, request)
    if alignment_key.get("schema_version") != "example_attribution_alignment_key_v1":
        errors.append(
            "alignment key schema_version must be example_attribution_alignment_key_v1"
        )
    for key in ("input_body_sha256", "blind_request_sha256"):
        expected = (
            request.get("input_body_sha256")
            if key == "input_body_sha256"
            else _digest_json(request)
        )
        if alignment_key.get(key) != expected:
            errors.append(f"alignment key {key} does not match stage 1 request")
    recorded = _parse_timestamp(record.get("recorded_at"))
    aligned = _parse_timestamp(aligned_at)
    if aligned is None:
        errors.append("aligned_at must be an aware ISO timestamp")
    elif recorded is not None and aligned <= recorded:
        errors.append("aligned_at must be later than the blind attribution record")
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "pass_id": "example-attribution",
        "reviewer": record.get("reviewer"),
        "blind_attribution_record": record,
        "aligned_at": aligned_at,
        "findings": _attribution_findings(record, alignment_key),
        "unrouted_observations": [],
    }


def validate_pass_output(
    output: dict[str, Any],
    router: dict[str, Any],
    *,
    entry_path: Path | None = None,
    repo_root: Path = REPO_ROOT,
    example_request: dict[str, Any] | None = None,
    request_payload: dict[str, Any] | None = None,
    alignment_key: dict[str, Any] | None = None,
    check_liveness: bool = True,
    generation_model: str | None = None,
    require_reviewer: bool = True,
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
    if require_reviewer or output.get("reviewer") is not None:
        errors.extend(
            review_liveness.validate_reviewer(
                output.get("reviewer"), generation_model=generation_model
            )
        )
        errors.extend(
            review_liveness.validate_api_request_binding(
                output.get("reviewer"), request_payload or example_request
            )
        )
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
        if finding.get("taxonomy_id") == "example_sense_attribution_mismatch":
            if finding.get("severity") != "blocking":
                errors.append(f"{label}.severity must be blocking for example attribution")
            if finding.get("suggested_direction") not in {
                "例文置換",
                "語義ブロック間の移動",
                "判別語の追加",
            }:
                errors.append(f"{label}.suggested_direction is invalid")
    if pass_id == "example-attribution":
        request: dict[str, Any] | None = example_request
        resolved_alignment: dict[str, Any] | None = alignment_key
        if entry_path is not None and request is None:
            text = entry_path.resolve().read_text(encoding="utf-8")
            _, body_lines = _split_front_matter(text)
            request = _example_attribution_request(
                text,
                "\n".join(body_lines).encode("utf-8"),
                by_id["example-attribution"],
                router["finding_schema"],
                blind_seed=_digest_bytes("\n".join(body_lines).encode("utf-8")),
            )
            resolved_alignment = build_example_attribution_alignment_key(
                entry_path, repo_root=repo_root
            )
        record = output.get("blind_attribution_record")
        errors.extend(
            validate_blind_attribution_record(
                record,
                request,
                check_liveness=False,
                generation_model=generation_model,
                require_reviewer=require_reviewer,
            )
        )
        if check_liveness and request is not None and isinstance(record, dict):
            errors.extend(
                review_liveness.validate_attribution_liveness(
                    record, request, alignment_key=resolved_alignment
                )
            )
        recorded = _parse_timestamp(
            record.get("recorded_at") if isinstance(record, dict) else None
        )
        aligned = _parse_timestamp(output.get("aligned_at"))
        if aligned is None:
            errors.append("aligned_at must be an aware ISO timestamp")
        elif recorded is not None and aligned <= recorded:
            errors.append("aligned_at must be later than blind attribution record")
        if request is not None and resolved_alignment is not None and isinstance(record, dict):
            if resolved_alignment.get("blind_request_sha256") != _digest_json(request):
                errors.append("alignment key does not bind the current stage 1 request")
            expected = _attribution_findings(record, resolved_alignment)
            actual_anchors = {
                (
                    item.get("location", {}).get("line_start"),
                    item.get("location", {}).get("exact_quote"),
                )
                for item in findings
                if item.get("taxonomy_id") == "example_sense_attribution_mismatch"
                and isinstance(item.get("location"), dict)
            }
            for item in expected:
                anchor = (
                    item["location"]["line_start"],
                    item["location"]["exact_quote"],
                )
                if anchor not in actual_anchors:
                    errors.append(
                        "example attribution output is missing required blocking finding "
                        f"at line {anchor[0]}"
                    )
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
            "reviewer": {
                "mode": "handoff",
                "declared_model": "regression-fixture-reviewer",
                "ingested_by": "human",
            },
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
    bundle.add_argument("--seed")
    validate = sub.add_parser("validate-output")
    validate.add_argument("output", type=Path)
    validate.add_argument("--entry", type=Path)
    blind = sub.add_parser("validate-blind-record")
    blind.add_argument("entry", type=Path)
    blind.add_argument("record", type=Path)
    reconcile = sub.add_parser("reconcile-example-attribution")
    reconcile.add_argument("entry", type=Path)
    reconcile.add_argument("record", type=Path)
    reconcile.add_argument("--output", required=True, type=Path)
    reconcile.add_argument("--aligned-at")
    regression = sub.add_parser("regression")
    regression.add_argument("cases", type=Path)
    regression.add_argument("--output", type=Path)
    args = parser.parse_args()
    router = load_router()
    if args.command == "validate-router":
        return _print_errors(validate_router(router))
    if args.command == "bundle":
        paths = write_bundles(
            build_bundles(args.entry, blind_seed=args.seed), args.output_dir
        )
        alignment_path = args.output_dir / "example-attribution.alignment-key.json"
        alignment_path.write_text(
            json.dumps(
                build_example_attribution_alignment_key(
                    args.entry, blind_seed=args.seed
                ),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        paths.append(alignment_path)
        for path in paths:
            print(path)
        return 0
    if args.command == "validate-blind-record":
        request = next(
            item
            for item in build_bundles(args.entry)
            if item["pass_id"] == "example-attribution"
        )
        record = json.loads(args.record.read_text(encoding="utf-8"))
        return _print_errors(validate_blind_attribution_record(record, request))
    if args.command == "reconcile-example-attribution":
        request = next(
            item
            for item in build_bundles(args.entry)
            if item["pass_id"] == "example-attribution"
        )
        record = json.loads(args.record.read_text(encoding="utf-8"))
        aligned_at = args.aligned_at or datetime.now(timezone.utc).isoformat()
        output = reconcile_example_attribution(
            request,
            record,
            build_example_attribution_alignment_key(args.entry),
            aligned_at=aligned_at,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(output, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(args.output)
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
    return _print_errors(
        validate_pass_output(output, router, entry_path=args.entry)
    )


if __name__ == "__main__":
    raise SystemExit(main())
