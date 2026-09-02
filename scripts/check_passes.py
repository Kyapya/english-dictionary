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
ANTONYM_AXIS_TYPES = {"補完", "程度", "方向", "評価", "状態"}
ANTONYM_AXIS_FLAGS = {"F1", "F2", "F3", "F4"}
ANTONYM_DIRECTIONS = {
    "削除",
    "語法・注意への対照表現としての移動",
    "対立軸修正",
}


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
        specification_match = re.search(
            r"\s+\(`specification:\s+([^`]+)`\)$", cells[2]
        )
        section_cell = (
            cells[2][: specification_match.start()].strip()
            if specification_match is not None
            else cells[2]
        )
        rows.append(
            {
                "id": cells[0],
                "specification": (
                    specification_match.group(1).strip()
                    if specification_match is not None
                    else None
                ),
                "taxonomy_ids": [
                    value.strip() for value in cells[1].split(",") if value.strip()
                ],
                "sections": [
                    value.strip() for value in section_cell.split(",") if value.strip()
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
        table_core = [
            {
                "id": item["id"],
                "taxonomy_ids": item["taxonomy_ids"],
                "sections": item["sections"],
            }
            for item in table_rows
        ]
        json_rows = [
            {
                "id": item.get("id"),
                "taxonomy_ids": item.get("taxonomy_ids"),
                "sections": item.get("sections"),
            }
            for item in passes
            if isinstance(item, dict)
        ]
        if table_core != json_rows:
            errors.append("router pass table and machine-readable JSON must match exactly")
        table_frame = next(
            (item for item in table_rows if item["id"] == "frame-relation"), None
        )
        json_frame = next(
            (
                item
                for item in passes
                if isinstance(item, dict) and item.get("id") == "frame-relation"
            ),
            None,
        )
        if (
            table_frame is None
            or json_frame is None
            or table_frame.get("specification") != json_frame.get("specification")
        ):
            errors.append(
                "frame-relation specification must match in table and JSON"
            )
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


def _front_matter_headword(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for raw in lines[1:]:
        if raw.strip() == "---":
            break
        if raw.startswith("headword:"):
            return raw.split(":", 1)[1].strip().strip("'\"")
    return ""


def _clean_relation_term(value: str) -> str:
    return value.strip().removeprefix("・").strip().strip("`")


def _antonym_axis_material(text: str) -> dict[str, Any]:
    """Extract public blind items and coordinator-private stage 2 material."""
    body_start, body_lines = _split_front_matter(text)
    main = _main_sections(body_start, body_lines)
    blocks = _sense_blocks(main.get("senses", []))
    items: list[dict[str, Any]] = []
    senses: list[dict[str, Any]] = []
    for sense_index, block in enumerate(blocks, start=1):
        definition_line = next(
            (
                line
                for line in block[1:]
                if line.text.strip().startswith("【日本語訳・定義】")
            ),
            None,
        )
        if definition_line is None:
            continue
        senses.append(
            {
                "sense_id": f"sense:{sense_index:03d}",
                "full_sense": [
                    {"line": line.number, "text": line.text}
                    for line in block
                    if line.text.strip()
                ],
            }
        )
        in_antonyms = False
        current: list[LocatedLine] = []

        def flush_item() -> None:
            nonlocal current
            if not current:
                return
            term_line = current[0]
            definition = next(
                (
                    line
                    for line in current[1:]
                    if line.text.strip().startswith("定義:")
                ),
                None,
            )
            if definition is not None:
                difference = next(
                    (
                        line
                        for line in current[1:]
                        if line.text.strip().startswith("違い:")
                    ),
                    None,
                )
                items.append(
                    {
                        "source_item_id": f"antonym:{len(items) + 1:03d}",
                        "sense_id": f"sense:{sense_index:03d}",
                        "headword": _front_matter_headword(text),
                        "sense_definition": definition_line.text.strip(),
                        "antonym": _clean_relation_term(term_line.text),
                        "antonym_definition": definition.text.strip(),
                        "anchor": {
                            "section": "lexical_relations",
                            "line_start": term_line.number,
                            "line_end": term_line.number,
                            "exact_quote": term_line.text,
                        },
                        "difference_anchor": (
                            {
                                "section": "lexical_relations",
                                "line_start": difference.number,
                                "line_end": difference.number,
                                "exact_quote": difference.text,
                            }
                            if difference is not None
                            else None
                        ),
                    }
                )
            current = []

        for line in block[1:]:
            stripped = line.text.strip()
            if stripped == "【反意語】":
                flush_item()
                in_antonyms = True
                continue
            if stripped.startswith("【"):
                if in_antonyms:
                    flush_item()
                in_antonyms = False
                continue
            if not in_antonyms or not stripped:
                continue
            if stripped.startswith("・"):
                flush_item()
            current.append(line)
        flush_item()
    item_sense_ids = {str(item["sense_id"]) for item in items}
    return {
        "headword": _front_matter_headword(text),
        "items": items,
        "senses": [
            sense for sense in senses if str(sense["sense_id"]) in item_sense_ids
        ],
    }


def _antonym_opaque_ids(
    material: dict[str, Any], blind_seed: str
) -> dict[str, str]:
    return {
        str(item["source_item_id"]): "ant-"
        + hashlib.sha256(
            f"{blind_seed}\0{item['source_item_id']}".encode("utf-8")
        ).hexdigest()[:12]
        for item in material["items"]
    }


def _antonym_axis_blind_request(
    text: str,
    body_bytes: bytes,
    check_pass: dict[str, Any],
    finding_schema: dict[str, Any],
    *,
    blind_seed: str,
) -> dict[str, Any]:
    material = _antonym_axis_material(text)
    opaque_ids = _antonym_opaque_ids(material, blind_seed)
    items = [
        {
            "item_id": opaque_ids[str(item["source_item_id"])],
            "headword": item["headword"],
            "sense_definition": item["sense_definition"],
            "antonym": item["antonym"],
            "antonym_definition": item["antonym_definition"],
        }
        for item in material["items"]
    ]
    random.Random(blind_seed).shuffle(items)
    return {
        "schema_version": "antonym_axis_blind_request_v1",
        "pass_id": check_pass["id"],
        "taxonomy_ids": list(check_pass["taxonomy_ids"]),
        "specification": check_pass["specification"],
        "input_body_sha256": _digest_bytes(body_bytes),
        "input_sections": {"antonym_items": items},
        "blind_protocol": {
            "stage": 1,
            "withheld_fields": [
                "difference_line",
                "frequency_line",
                "example_line",
                "translation_line",
                "synonym_section",
                "core_image",
                "other_senses",
                "document_order",
            ],
            "questions": [
                "name_axis_as_one_noun",
                "classify_as_補完_程度_方向_評価_状態",
                "record_unnamable_with_one_sentence_reason",
            ],
            "required_output_schema": "antonym_axis_blind_record_v1",
        },
        "finding_schema": finding_schema,
    }


def build_antonym_axis_alignment_key(
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
        item for item in router["passes"] if item["id"] == "frame-relation"
    )
    effective_seed = blind_seed or _digest_bytes(body_bytes)
    request = _antonym_axis_blind_request(
        text,
        body_bytes,
        check_pass,
        router["finding_schema"],
        blind_seed=effective_seed,
    )
    material = _antonym_axis_material(text)
    opaque_ids = _antonym_opaque_ids(material, effective_seed)
    return {
        "schema_version": "antonym_axis_alignment_key_v1",
        "pass_id": "frame-relation",
        "input_body_sha256": _digest_bytes(body_bytes),
        "blind_request_sha256": _digest_json(request),
        "shuffle_seed": effective_seed,
        "items": [
            {
                **item,
                "item_id": opaque_ids[str(item["source_item_id"])],
            }
            for item in material["items"]
        ],
        "senses": material["senses"],
    }


def validate_antonym_axis_blind_record(
    record: Any,
    request: dict[str, Any] | None = None,
    *,
    generation_model: str | None = None,
    require_reviewer: bool = True,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["antonym_axis_blind_record must be an object"]
    if record.get("schema_version") != "antonym_axis_blind_record_v1":
        errors.append(
            "antonym_axis_blind_record.schema_version must be "
            "antonym_axis_blind_record_v1"
        )
    if record.get("pass_id") != "frame-relation":
        errors.append("antonym_axis_blind_record.pass_id must be frame-relation")
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
        errors.append(
            "antonym_axis_blind_record.recorded_at must be an aware ISO timestamp"
        )
    body_hash = record.get("input_body_sha256")
    if not isinstance(body_hash, str) or re.fullmatch(r"[0-9a-f]{64}", body_hash) is None:
        errors.append("antonym_axis_blind_record.input_body_sha256 must be a sha256")
    request_hash = record.get("blind_request_sha256")
    if not isinstance(request_hash, str) or re.fullmatch(r"[0-9a-f]{64}", request_hash) is None:
        errors.append("antonym_axis_blind_record.blind_request_sha256 must be a sha256")
    known_items: set[str] | None = None
    if request is not None:
        if request.get("schema_version") != "antonym_axis_blind_request_v1":
            errors.append("stage 1 request must use antonym_axis_blind_request_v1")
        if body_hash != request.get("input_body_sha256"):
            errors.append("antonym axis body hash does not match its stage 1 request")
        if request_hash != _digest_json(request):
            errors.append("antonym axis request hash does not match stage 1 input")
        sections = request.get("input_sections", {})
        known_items = {
            str(item.get("item_id"))
            for item in sections.get("antonym_items", [])
            if isinstance(item, dict) and item.get("item_id")
        }
    axes = record.get("axes")
    if not isinstance(axes, list):
        return [*errors, "antonym_axis_blind_record.axes must be a list"]
    seen: set[str] = set()
    for index, item in enumerate(axes):
        label = f"antonym_axis_blind_record.axes[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        item_id = str(item.get("item_id", ""))
        if not item_id or item_id in seen:
            errors.append(f"{label}.item_id is missing or duplicated")
        seen.add(item_id)
        axis = item.get("axis")
        if not isinstance(axis, str) or not axis.strip():
            errors.append(f"{label}.axis must be a non-empty string")
            continue
        relation_type = item.get("relation_type")
        reason = item.get("reason")
        if axis == "unnamable":
            if relation_type not in {None, ""}:
                errors.append(f"{label}.relation_type must be empty for unnamable")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{label}.reason is required for unnamable")
        elif relation_type not in ANTONYM_AXIS_TYPES:
            errors.append(
                f"{label}.relation_type must be one of {sorted(ANTONYM_AXIS_TYPES)}"
            )
    if known_items is not None and seen != known_items:
        missing = sorted(known_items - seen)
        extra = sorted(seen - known_items)
        if missing:
            errors.append("antonym axis record is missing items: " + ", ".join(missing))
        if extra:
            errors.append("antonym axis record has unknown items: " + ", ".join(extra))
    return errors


def bind_antonym_axis_blind_record(
    record: dict[str, Any],
    request: dict[str, Any],
    *,
    recorded_at: str | None = None,
) -> dict[str, Any]:
    """Bind reviewer-authored axes to the exact stage 1 artifact at save time."""
    bound = dict(record)
    bound["schema_version"] = "antonym_axis_blind_record_v1"
    bound["pass_id"] = "frame-relation"
    bound["input_body_sha256"] = request.get("input_body_sha256")
    bound["blind_request_sha256"] = _digest_json(request)
    bound["recorded_at"] = (
        recorded_at
        or str(record.get("recorded_at") or "")
        or datetime.now(timezone.utc).isoformat()
    )
    return bound


def materialize_antonym_axis_stage2_request(
    entry_path: Path,
    blind_request: dict[str, Any],
    blind_record_path: Path,
    alignment_key: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    require_reviewer: bool = True,
) -> dict[str, Any]:
    """Create stage 2 input only after the exact stage 1 record is persisted."""
    if not blind_record_path.is_file():
        raise ValueError(
            "process defect: stage 2 disclosure requires a saved stage 1 record"
        )
    blind_record = json.loads(blind_record_path.read_text(encoding="utf-8"))
    record_errors = validate_antonym_axis_blind_record(
        blind_record, blind_request, require_reviewer=require_reviewer
    )
    if record_errors:
        raise ValueError("; ".join(record_errors))
    if alignment_key.get("schema_version") != "antonym_axis_alignment_key_v1":
        raise ValueError("antonym axis alignment key schema_version is invalid")
    if alignment_key.get("input_body_sha256") != blind_request.get(
        "input_body_sha256"
    ):
        raise ValueError("antonym axis alignment key body hash mismatch")
    if alignment_key.get("blind_request_sha256") != _digest_json(blind_request):
        raise ValueError("antonym axis alignment key does not bind stage 1 request")
    raw = entry_path.resolve().read_bytes()
    text = raw.decode("utf-8")
    _, body_lines = _split_front_matter(text)
    body_bytes = "\n".join(body_lines).encode("utf-8")
    if _digest_bytes(body_bytes) != blind_request.get("input_body_sha256"):
        raise ValueError("entry body changed after antonym axis stage 1")
    router = load_router(repo_root / "prompts" / "check_router_v6.md")
    check_pass = next(
        item for item in router["passes"] if item["id"] == "frame-relation"
    )
    sections = extract_sections(text)
    axes = {
        str(item["item_id"]): item for item in blind_record.get("axes", [])
    }
    aligned_items = []
    for item in alignment_key.get("items", []):
        item_id = str(item["item_id"])
        aligned_items.append(
            {
                "item_id": item_id,
                "stage1_axis": axes[item_id],
                "sense_id": item["sense_id"],
                "anchor": item["anchor"],
                "difference_anchor": item.get("difference_anchor"),
            }
        )
    return {
        "schema_version": "antonym_axis_adjudication_request_v1",
        "pass_id": "frame-relation",
        "taxonomy_ids": list(check_pass["taxonomy_ids"]),
        "specification": check_pass["specification"],
        "input_body_sha256": _digest_bytes(body_bytes),
        "blind_request_sha256": _digest_json(blind_request),
        "blind_record_sha256": _digest_json(blind_record),
        "input_sections": {
            **{
                section: sections.get(section, [])
                for section in check_pass["sections"]
            },
            "antonym_axis_items": aligned_items,
            "antonym_axis_senses": alignment_key.get("senses", []),
        },
        "blind_protocol": {
            "stage": 2,
            "stage1_record_saved": True,
            "chronology_marker": "audits/BLIND_SEAL_CHRONOLOGY_REQUIRED",
            "required_output_schema": "antonym_axis_adjudication_record_v1",
        },
        "finding_schema": router["finding_schema"],
    }


def validate_antonym_axis_adjudication_record(
    record: Any,
    stage2_request: dict[str, Any],
    blind_record: dict[str, Any],
    *,
    generation_model: str | None = None,
    require_reviewer: bool = True,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["antonym_axis_adjudication_record must be an object"]
    if record.get("schema_version") != "antonym_axis_adjudication_record_v1":
        errors.append(
            "antonym_axis_adjudication_record.schema_version must be "
            "antonym_axis_adjudication_record_v1"
        )
    if record.get("pass_id") != "frame-relation":
        errors.append("antonym_axis_adjudication_record.pass_id must be frame-relation")
    if require_reviewer or record.get("reviewer") is not None:
        errors.extend(
            review_liveness.validate_reviewer(
                record.get("reviewer"), generation_model=generation_model
            )
        )
        errors.extend(
            review_liveness.validate_api_request_binding(
                record.get("reviewer"), stage2_request
            )
        )
    if record.get("input_body_sha256") != stage2_request.get("input_body_sha256"):
        errors.append("antonym axis adjudication body hash mismatch")
    if record.get("stage2_request_sha256") != _digest_json(stage2_request):
        errors.append("antonym axis adjudication request hash mismatch")
    if record.get("blind_record_sha256") != _digest_json(blind_record):
        errors.append("antonym axis adjudication does not bind the sealed blind record")
    request_items = stage2_request.get("input_sections", {}).get(
        "antonym_axis_items", []
    )
    known_items = {
        str(item.get("item_id"))
        for item in request_items
        if isinstance(item, dict) and item.get("item_id")
    }
    axes = {
        str(item.get("item_id")): item
        for item in blind_record.get("axes", [])
        if isinstance(item, dict)
    }
    adjudications = record.get("adjudications")
    if not isinstance(adjudications, list):
        return [*errors, "antonym_axis_adjudication_record.adjudications must be a list"]
    seen: set[str] = set()
    for index, item in enumerate(adjudications):
        label = f"antonym_axis_adjudication_record.adjudications[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        item_id = str(item.get("item_id", ""))
        if not item_id or item_id in seen:
            errors.append(f"{label}.item_id is missing or duplicated")
        seen.add(item_id)
        flags = item.get("flags")
        if not isinstance(flags, list) or any(flag not in ANTONYM_AXIS_FLAGS for flag in flags):
            errors.append(f"{label}.flags must contain only F1, F2, F3, F4")
            flags = []
        elif len(flags) != len(set(flags)):
            errors.append(f"{label}.flags contains duplicates")
        is_unnamable = axes.get(item_id, {}).get("axis") == "unnamable"
        if is_unnamable != ("F1" in flags):
            errors.append(f"{label}.flags must include F1 exactly for unnamable")
        rationale = item.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"{label}.rationale is required")
        if flags:
            if item.get("suggested_direction") not in ANTONYM_DIRECTIONS:
                errors.append(f"{label}.suggested_direction is invalid")
        if "F4" in flags:
            if item.get("f4_severity") not in {"blocking", "minor"}:
                errors.append(f"{label}.f4_severity must be blocking or minor")
        elif item.get("f4_severity") not in {None, ""}:
            errors.append(f"{label}.f4_severity is only valid with F4")
    if seen != known_items:
        missing = sorted(known_items - seen)
        extra = sorted(seen - known_items)
        if missing:
            errors.append("antonym axis adjudication is missing items: " + ", ".join(missing))
        if extra:
            errors.append("antonym axis adjudication has unknown items: " + ", ".join(extra))
    if not isinstance(record.get("frame_findings"), list):
        errors.append("antonym_axis_adjudication_record.frame_findings must be a list")
    if not isinstance(record.get("unrouted_observations"), list):
        errors.append(
            "antonym_axis_adjudication_record.unrouted_observations must be a list"
        )
    return errors


def bind_antonym_axis_adjudication_record(
    record: dict[str, Any],
    stage2_request: dict[str, Any],
    blind_record: dict[str, Any],
) -> dict[str, Any]:
    """Bind stage 2 judgments to the disclosed request and sealed stage 1 record."""
    bound = dict(record)
    bound["schema_version"] = "antonym_axis_adjudication_record_v1"
    bound["pass_id"] = "frame-relation"
    bound["input_body_sha256"] = stage2_request.get("input_body_sha256")
    bound["stage2_request_sha256"] = _digest_json(stage2_request)
    bound["blind_record_sha256"] = _digest_json(blind_record)
    return bound


def reconcile_antonym_axis(
    blind_request: dict[str, Any],
    blind_record: dict[str, Any],
    stage2_request: dict[str, Any],
    adjudication_record: dict[str, Any],
    alignment_key: dict[str, Any],
    *,
    aligned_at: str,
    generation_model: str | None = None,
    require_reviewer: bool = True,
) -> dict[str, Any]:
    errors = validate_antonym_axis_blind_record(
        blind_record,
        blind_request,
        generation_model=generation_model,
        require_reviewer=require_reviewer,
    )
    errors.extend(
        validate_antonym_axis_adjudication_record(
            adjudication_record,
            stage2_request,
            blind_record,
            generation_model=generation_model,
            require_reviewer=require_reviewer,
        )
    )
    recorded = _parse_timestamp(blind_record.get("recorded_at"))
    aligned = _parse_timestamp(aligned_at)
    if aligned is None:
        errors.append("aligned_at must be an aware ISO timestamp")
    elif recorded is not None and aligned <= recorded:
        errors.append("aligned_at must be later than the antonym axis blind record")
    if alignment_key.get("schema_version") != "antonym_axis_alignment_key_v1":
        errors.append("antonym axis alignment key schema_version is invalid")
    if alignment_key.get("blind_request_sha256") != _digest_json(blind_request):
        errors.append("antonym axis alignment key does not bind stage 1 request")
    if stage2_request.get("blind_record_sha256") != _digest_json(blind_record):
        errors.append("stage 2 request does not bind the sealed blind record")
    if errors:
        raise ValueError("; ".join(errors))

    anchors = {
        str(item["item_id"]): item for item in alignment_key.get("items", [])
    }
    axis_findings: list[dict[str, Any]] = []
    severity_by_flag = {"F1": "blocking", "F2": "blocking", "F3": "blocking"}
    for adjudication in adjudication_record["adjudications"]:
        item_id = str(adjudication["item_id"])
        owner = anchors[item_id]
        for flag in adjudication["flags"]:
            location = (
                owner.get("difference_anchor") or owner["anchor"]
                if flag == "F4"
                else owner["anchor"]
            )
            axis_findings.append(
                {
                    "taxonomy_id": "lexical_relation_mislabel",
                    "location": dict(location),
                    "severity": (
                        adjudication["f4_severity"]
                        if flag == "F4"
                        else severity_by_flag[flag]
                    ),
                    "rationale": f"{flag}: {adjudication['rationale']}",
                    "evidence_link_ids": [],
                    "suggested_direction": adjudication["suggested_direction"],
                }
            )
    return {
        "pass_id": "frame-relation",
        "reviewer": adjudication_record.get("reviewer"),
        "antonym_axis_blind_record": blind_record,
        "antonym_axis_adjudication_record": adjudication_record,
        "aligned_at": aligned_at,
        "findings": [
            *adjudication_record.get("frame_findings", []),
            *axis_findings,
        ],
        "unrouted_observations": adjudication_record.get(
            "unrouted_observations", []
        ),
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
        if check_pass["id"] == "frame-relation":
            bundles.append(
                _antonym_axis_blind_request(
                    text,
                    body_bytes,
                    check_pass,
                    router["finding_schema"],
                    blind_seed=effective_seed,
                )
            )
            continue
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
    antonym_request: dict[str, Any] | None = None,
    antonym_stage2_request: dict[str, Any] | None = None,
    antonym_alignment_key: dict[str, Any] | None = None,
    request_payload: dict[str, Any] | None = None,
    alignment_key: dict[str, Any] | None = None,
    check_liveness: bool = True,
    generation_model: str | None = None,
    require_reviewer: bool = True,
    require_antonym_axis: bool = True,
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
                output.get("reviewer"),
                antonym_stage2_request or request_payload or example_request,
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
    if pass_id == "frame-relation" and require_antonym_axis:
        blind_record = output.get("antonym_axis_blind_record")
        adjudication_record = output.get("antonym_axis_adjudication_record")
        if antonym_request is None:
            errors.append("frame-relation stage 1 request is required")
        if antonym_stage2_request is None:
            errors.append("frame-relation stage 2 request is required")
        if antonym_alignment_key is None:
            errors.append("frame-relation antonym alignment key is required")
        if antonym_request is not None:
            errors.extend(
                validate_antonym_axis_blind_record(
                    blind_record,
                    antonym_request,
                    generation_model=generation_model,
                    require_reviewer=require_reviewer,
                )
            )
        if (
            antonym_stage2_request is not None
            and isinstance(blind_record, dict)
        ):
            errors.extend(
                validate_antonym_axis_adjudication_record(
                    adjudication_record,
                    antonym_stage2_request,
                    blind_record,
                    generation_model=generation_model,
                    require_reviewer=require_reviewer,
                )
            )
        recorded = _parse_timestamp(
            blind_record.get("recorded_at")
            if isinstance(blind_record, dict)
            else None
        )
        aligned = _parse_timestamp(output.get("aligned_at"))
        if aligned is None:
            errors.append("aligned_at must be an aware ISO timestamp")
        elif recorded is not None and aligned <= recorded:
            errors.append("aligned_at must be later than antonym axis blind record")
        if (
            antonym_request is not None
            and antonym_stage2_request is not None
            and antonym_alignment_key is not None
            and isinstance(blind_record, dict)
            and isinstance(adjudication_record, dict)
        ):
            try:
                expected = reconcile_antonym_axis(
                    antonym_request,
                    blind_record,
                    antonym_stage2_request,
                    adjudication_record,
                    antonym_alignment_key,
                    aligned_at=str(output.get("aligned_at", "")),
                    generation_model=generation_model,
                    require_reviewer=require_reviewer,
                )
            except ValueError as exc:
                errors.append(str(exc))
            else:
                if output.get("findings") != expected["findings"]:
                    errors.append(
                        "frame-relation findings diverge from sealed axis adjudication"
                    )
                if output.get("unrouted_observations") != expected[
                    "unrouted_observations"
                ]:
                    errors.append(
                        "frame-relation unrouted_observations were modified"
                    )
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
        if pass_id == "frame-relation":
            full_sections = extract_sections(entry_path.read_text(encoding="utf-8"))
            frame_spec = next(
                item for item in router["passes"] if item["id"] == pass_id
            )
            bundle = {
                "input_sections": {
                    section: full_sections.get(section, [])
                    for section in frame_spec["sections"]
                }
            }
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
        validation_errors = validate_pass_output(
            replay_output, router, require_antonym_axis=False
        )
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
    validate.add_argument("--antonym-request", type=Path)
    validate.add_argument("--antonym-stage2-request", type=Path)
    validate.add_argument("--antonym-alignment-key", type=Path)
    blind = sub.add_parser("validate-blind-record")
    blind.add_argument("entry", type=Path)
    blind.add_argument("record", type=Path)
    reconcile = sub.add_parser("reconcile-example-attribution")
    reconcile.add_argument("entry", type=Path)
    reconcile.add_argument("record", type=Path)
    reconcile.add_argument("--output", required=True, type=Path)
    reconcile.add_argument("--aligned-at")
    axis_stage2 = sub.add_parser("materialize-antonym-axis-stage2")
    axis_stage2.add_argument("entry", type=Path)
    axis_stage2.add_argument("blind_request", type=Path)
    axis_stage2.add_argument("blind_record", type=Path)
    axis_stage2.add_argument("alignment_key", type=Path)
    axis_stage2.add_argument("--output", required=True, type=Path)
    axis_reconcile = sub.add_parser("reconcile-antonym-axis")
    axis_reconcile.add_argument("blind_request", type=Path)
    axis_reconcile.add_argument("blind_record", type=Path)
    axis_reconcile.add_argument("stage2_request", type=Path)
    axis_reconcile.add_argument("adjudication_record", type=Path)
    axis_reconcile.add_argument("alignment_key", type=Path)
    axis_reconcile.add_argument("--output", required=True, type=Path)
    axis_reconcile.add_argument("--aligned-at")
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
        antonym_alignment_path = (
            args.output_dir / "frame-relation.antonym-axis.alignment-key.json"
        )
        antonym_alignment_path.write_text(
            json.dumps(
                build_antonym_axis_alignment_key(
                    args.entry, blind_seed=args.seed
                ),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        paths.append(antonym_alignment_path)
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
    if args.command == "materialize-antonym-axis-stage2":
        request = json.loads(args.blind_request.read_text(encoding="utf-8"))
        alignment = json.loads(args.alignment_key.read_text(encoding="utf-8"))
        output = materialize_antonym_axis_stage2_request(
            args.entry,
            request,
            args.blind_record,
            alignment,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(output, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(args.output)
        return 0
    if args.command == "reconcile-antonym-axis":
        blind_request = json.loads(
            args.blind_request.read_text(encoding="utf-8")
        )
        blind_record = json.loads(
            args.blind_record.read_text(encoding="utf-8")
        )
        stage2_request = json.loads(
            args.stage2_request.read_text(encoding="utf-8")
        )
        adjudication_record = json.loads(
            args.adjudication_record.read_text(encoding="utf-8")
        )
        alignment = json.loads(args.alignment_key.read_text(encoding="utf-8"))
        output = reconcile_antonym_axis(
            blind_request,
            blind_record,
            stage2_request,
            adjudication_record,
            alignment,
            aligned_at=args.aligned_at or datetime.now(timezone.utc).isoformat(),
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
    antonym_request = (
        json.loads(args.antonym_request.read_text(encoding="utf-8"))
        if args.antonym_request
        else None
    )
    antonym_stage2_request = (
        json.loads(args.antonym_stage2_request.read_text(encoding="utf-8"))
        if args.antonym_stage2_request
        else None
    )
    antonym_alignment_key = (
        json.loads(args.antonym_alignment_key.read_text(encoding="utf-8"))
        if args.antonym_alignment_key
        else None
    )
    return _print_errors(
        validate_pass_output(
            output,
            router,
            entry_path=args.entry,
            antonym_request=antonym_request,
            antonym_stage2_request=antonym_stage2_request,
            antonym_alignment_key=antonym_alignment_key,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
