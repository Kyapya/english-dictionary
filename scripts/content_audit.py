from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCHEMA_VERSION = "content_audit_v3"
PREVIOUS_AUDIT_SCHEMA_VERSION = "content_audit_v2"
LEGACY_AUDIT_SCHEMA_VERSION = "content_audit_v1"
COLD_REVIEW_PROMPT_VERSION = "cold_review_prompt_v1"
FINAL_STATUSES = {"checked", "final"}
AUDITED_STATUSES = {"needs_review", "review_ready", "checked", "final"}
INVALIDATION_REGISTRY = Path("audits/review_invalidations.json")
INVALIDATION_SCHEMA_VERSION = "review_invalidations_v1"
SENSE_PATTERN = re.compile(r"^\d+\.\s*【.+】")
HIGH_RISK_MARKERS = re.compile(
    r"必ず|常に|通常|原則|のみ|だけ|不可|できない|誤り|非文|"
    r"不自然|自然|高頻度|低頻度|古風|地域|米英|米:|英:|"
    r"法律|法的|医療|税務|保険|制度|限定|主に|語源|さかのぼ|"
    r"always|never|must|cannot|only",
    re.IGNORECASE,
)
EVIDENCE_REQUIRED_KINDS = {
    "pronunciation",
    "etymology",
    "word_formation",
    "sense_boundary",
    "definition",
    "frequency",
    "register",
    "grammar_pattern",
    "collocation",
    "usage_note",
    "core_image",
    "synonym",
    "antonym",
}
TWO_SOURCES_OR_PRIMARY_KINDS = {
    "sense_boundary",
    "frequency",
    "register",
    "synonym",
    "antonym",
}
PRIMARY_SOURCE_TYPES = {
    "primary_source",
    "official_primary",
    "corpus",
    "standard",
    "research_paper",
}
LEGACY_ESCAPED_DEFECT_CATEGORIES = (
    "compound_component_generalization",
    "argument_slot_role_mismatch",
    "regional_qualification",
    "technical_terminology_conventionality",
    "sense_boundary_overlap",
    "lexical_relation_mislabel",
    "example_translation_alignment",
    "absolute_scope_counterexample",
    "pronunciation_symbol_explanation",
    "evidence_claim_mismatch",
)
ESCAPED_DEFECT_CATEGORIES = LEGACY_ESCAPED_DEFECT_CATEGORIES + (
    "semantic_direction_reversal",
    "cross_section_internal_contradiction",
    "finding_scope_transfer_loss",
    "raw_adjudication_manifest_divergence",
)
INLINE_LABELS = {
    "【日本語訳・定義】": "definition",
    "【頻度】": "frequency",
    "【レジスター/領域】": "register",
    "【文法パターン】": "grammar_pattern",
    "【語法・注意】": "usage_note",
}
GROUP_SIZES = {
    "【コロケーション】": ("collocation", 4),
    "【類義語】": ("synonym", 6),
    "【反意語】": ("antonym", 6),
}


def _required_defect_categories(manifest: dict[str, Any]) -> tuple[str, ...]:
    gate = manifest.get("semantic_gate")
    if isinstance(gate, dict) and gate.get("version") == "semantic_resolution_v2":
        return ESCAPED_DEFECT_CATEGORIES
    return LEGACY_ESCAPED_DEFECT_CATEGORIES


def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            values: dict[str, str] = {}
            for line in lines[1:index]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    values[key.strip()] = value.strip().strip('"')
            return values, "\n".join(lines[index + 1 :])
    return {}, text


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def body_sha256(entry_path: Path) -> str:
    _, body = _split_front_matter(entry_path.read_text(encoding="utf-8"))
    return _digest(body)


def _entry_body(entry_path: Path) -> str:
    _, body = _split_front_matter(entry_path.read_text(encoding="utf-8"))
    return body


def audit_path_for_entry(entry_path: Path, repo_root: Path = REPO_ROOT) -> Path:
    relative = entry_path.resolve().relative_to(repo_root.resolve())
    if not relative.parts or relative.parts[0] != "entries":
        raise ValueError(f"entry must be under entries/: {entry_path}")
    return repo_root / "audits" / Path(*relative.parts[1:]).with_suffix(".json")


def _review_invalidations(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    path = repo_root / INVALIDATION_REGISTRY
    if not path.is_file():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(value, dict) or value.get("schema_version") != INVALIDATION_SCHEMA_VERSION:
        return []
    records = value.get("invalidations")
    return [item for item in records if isinstance(item, dict)] if isinstance(records, list) else []


def _matching_invalidation(
    entry_path: Path,
    body_hash: str,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any] | None:
    relative = entry_path.resolve().relative_to(repo_root.resolve()).as_posix()
    for record in _review_invalidations(repo_root):
        if (
            record.get("entry_path") == relative
            and record.get("body_sha256") == body_hash
            and record.get("status") == "invalidated"
        ):
            return record
    return None


def validate_invalidation_registry(repo_root: Path = REPO_ROOT) -> list[str]:
    path = repo_root / INVALIDATION_REGISTRY
    if not path.is_file():
        return []
    errors: list[str] = []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read {INVALIDATION_REGISTRY}: {exc}"]
    if not isinstance(value, dict):
        return [f"{INVALIDATION_REGISTRY} must be a JSON object"]
    if value.get("schema_version") != INVALIDATION_SCHEMA_VERSION:
        errors.append(
            f"{INVALIDATION_REGISTRY}.schema_version must be {INVALIDATION_SCHEMA_VERSION}"
        )
    records = value.get("invalidations")
    if not isinstance(records, list):
        return errors + [f"{INVALIDATION_REGISTRY}.invalidations must be a list"]
    seen: set[tuple[str, str]] = set()
    for index, record in enumerate(records):
        label = f"{INVALIDATION_REGISTRY}.invalidations[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        for key in ("entry_path", "body_sha256", "invalidated_at", "reason"):
            if not _nonempty(record.get(key)):
                errors.append(f"{label}.{key} is required")
        record_status = record.get("status")
        if record_status not in {"invalidated", "superseded"}:
            errors.append(f"{label}.status must be invalidated or superseded")
        _sha256_value(record.get("body_sha256"), f"{label}.body_sha256", errors)
        _timestamp(record.get("invalidated_at"), f"{label}.invalidated_at", errors)
        categories = record.get("defect_categories")
        if not isinstance(categories, list) or not categories:
            errors.append(f"{label}.defect_categories must be a non-empty list")
        else:
            unknown = sorted(set(categories) - set(ESCAPED_DEFECT_CATEGORIES))
            if unknown:
                errors.append(f"{label} contains unknown defect categories: {', '.join(unknown)}")
        entry_value = str(record.get("entry_path", ""))
        key = (entry_value, str(record.get("body_sha256", "")))
        if key in seen:
            errors.append(f"{label} duplicates an existing entry/body invalidation")
        seen.add(key)
        entry = repo_root / entry_value
        if not entry.is_file():
            errors.append(f"{label}.entry_path does not exist")
            continue
        actual_hash = body_sha256(entry)
        if record_status == "invalidated":
            if actual_hash != record.get("body_sha256"):
                errors.append(
                    f"{label}.body_sha256 no longer matches the current entry body; "
                    "mark the record superseded and bind its replacement body"
                )
            front, _ = _split_front_matter(entry.read_text(encoding="utf-8"))
            if front.get("status") != "needs_review" or front.get("checked") != "false":
                errors.append(
                    f"{label} requires entry status needs_review and checked false"
                )
        elif record_status == "superseded":
            for key_name in ("superseded_at", "superseded_by_body_sha256"):
                if not _nonempty(record.get(key_name)):
                    errors.append(f"{label}.{key_name} is required")
            _timestamp(record.get("superseded_at"), f"{label}.superseded_at", errors)
            _sha256_value(
                record.get("superseded_by_body_sha256"),
                f"{label}.superseded_by_body_sha256",
                errors,
            )
            if record.get("superseded_by_body_sha256") == record.get("body_sha256"):
                errors.append(
                    f"{label}.superseded_by_body_sha256 must differ from body_sha256"
                )
    return errors


def _is_structure_line(text: str) -> bool:
    return (
        text.startswith("＃")
        or SENSE_PATTERN.match(text) is not None
        or text in GROUP_SIZES
        or any(text.startswith(label) for label in INLINE_LABELS)
    )


def extract_targets(entry_path: Path) -> list[dict[str, Any]]:
    _, body = _split_front_matter(entry_path.read_text(encoding="utf-8"))
    lines = body.splitlines()
    targets: list[dict[str, Any]] = []
    counters: dict[str, int] = {}
    section = ""
    sense = ""

    def add(kind: str, start: int, end: int, text: str) -> None:
        counters[kind] = counters.get(kind, 0) + 1
        requires_evidence = (
            kind in EVIDENCE_REQUIRED_KINDS
            or HIGH_RISK_MARKERS.search(text) is not None
        )
        location = f"line:{start + 1}" if start == end else f"lines:{start + 1}-{end + 1}"
        targets.append(
            {
                "id": f"{kind}:{counters[kind]:03d}",
                "kind": kind,
                "location": location,
                "section": section,
                "sense": sense,
                "text_sha256": _digest(text),
                "requires_evidence": requires_evidence,
                "evidence_policy": (
                    "two_sources_or_primary"
                    if kind in TWO_SOURCES_OR_PRIMARY_KINDS
                    or HIGH_RISK_MARKERS.search(text) is not None
                    else "one_source"
                ),
                "text": text,
            }
        )

    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("＃"):
            section = stripped
            sense = ""
            index += 1
            continue
        if SENSE_PATTERN.match(stripped):
            sense = stripped
            add("sense_boundary", index, index, stripped)
            index += 1
            continue
        if stripped in GROUP_SIZES:
            kind, block_size = GROUP_SIZES[stripped]
            content: list[tuple[int, str]] = []
            cursor = index + 1
            while cursor < len(lines):
                candidate = lines[cursor].strip()
                if candidate and _is_structure_line(candidate):
                    break
                if candidate:
                    content.append((cursor, candidate))
                cursor += 1
            for offset in range(0, len(content), block_size):
                block = content[offset : offset + block_size]
                if block:
                    add(
                        kind,
                        block[0][0],
                        block[-1][0],
                        "\n".join(text for _, text in block),
                    )
            index = cursor
            continue

        matched_label = next(
            (label for label in INLINE_LABELS if stripped.startswith(label)), None
        )
        if matched_label is not None:
            kind = INLINE_LABELS[matched_label]
            content = stripped[len(matched_label) :].strip()
            if kind == "grammar_pattern":
                parts = [part.strip() for part in content.split("／") if part.strip()]
                for part in parts or [content]:
                    add(kind, index, index, part)
            else:
                add(kind, index, index, content or stripped)
            index += 1
            continue

        if section == "＃発音記号":
            kind = "pronunciation"
        elif section == "＃語源":
            kind = "etymology"
        elif section == "＃語形成":
            kind = "word_formation"
        elif section == "＃コアイメージ":
            kind = "core_image"
        elif section == "＃意味・用法・関連表現" and sense:
            kind = "usage_note"
        else:
            kind = "narrative"
        add(kind, index, index, stripped)
        index += 1

    return targets


def _extract_relations_v2(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Preserve the v2 relation inventory for unchanged legacy manifests."""
    import itertools

    relations: list[dict[str, Any]] = []
    counters: dict[str, int] = {}

    def add(kind: str, target_ids: list[str], description: str) -> None:
        counters[kind] = counters.get(kind, 0) + 1
        canonical = json.dumps(
            {"kind": kind, "target_ids": target_ids, "description": description},
            ensure_ascii=False,
            sort_keys=True,
        )
        relations.append(
            {
                "id": f"{kind}:{counters[kind]:03d}",
                "kind": kind,
                "target_ids": target_ids,
                "description": description,
                "text_sha256": _digest(canonical),
                "requires_evidence": True,
            }
        )

    senses = [target for target in targets if target["kind"] == "sense_boundary"]
    sense_by_text = {target["text"]: target for target in senses}
    for left, right in itertools.combinations(senses, 2):
        add(
            "sense_pair",
            [left["id"], right["id"]],
            "両語義の最小差、境界、重複、統合可能性を比較し、対象種類や使用分野だけに依存しない独立差を確認する。",
        )
    for target in targets:
        if target["kind"] == "sense_boundary" or not target.get("sense"):
            continue
        boundary = sense_by_text.get(target["sense"])
        if boundary is not None:
            add(
                "sense_membership",
                [boundary["id"], target["id"]],
                "対象記述が所属語義の定義・品詞・意味範囲に実際に属し、別語義へ移すべき内容ではないことを確認する。",
            )
    _append_shared_relations(
        relations, counters, targets, senses, add, legacy=True, enhanced=False
    )
    return relations


def _sense_number(target: dict[str, Any]) -> str:
    match = re.match(r"^(\d+)\.", str(target.get("text", "")))
    return match.group(1) if match else ""


def _referenced_sense_numbers(text: str) -> set[str]:
    return set(re.findall(r"語義\s*([0-9]+)", text))


def _sense_risk_pairs(
    targets: list[dict[str, Any]], senses: list[dict[str, Any]]
) -> list[tuple[dict[str, Any], dict[str, Any], list[str]]]:
    """Select only article-signalled overlap risks; never enumerate every pair."""
    by_number = {_sense_number(sense): sense for sense in senses}
    reasons: dict[tuple[str, str], set[str]] = {}
    for target in targets:
        owner = by_number.get(_sense_number({"text": target.get("sense", "")}))
        if owner is None:
            continue
        owner_number = _sense_number(owner)
        for referenced in _referenced_sense_numbers(str(target.get("text", ""))):
            other = by_number.get(referenced)
            if other is None or other["id"] == owner["id"]:
                continue
            pair = tuple(sorted((owner["id"], other["id"])))
            reasons.setdefault(pair, set()).add(
                f"{target['id']} explicitly contrasts sense {owner_number} with sense {referenced}"
            )
    indexed = {sense["id"]: sense for sense in senses}
    return [
        (indexed[left], indexed[right], sorted(pair_reasons))
        for (left, right), pair_reasons in sorted(reasons.items())
    ]


def _append_shared_relations(
    relations: list[dict[str, Any]],
    counters: dict[str, int],
    targets: list[dict[str, Any]],
    senses: list[dict[str, Any]],
    add: Any,
    *,
    legacy: bool,
    enhanced: bool,
) -> None:
    """Append non-cartesian relation families shared by v2 and v3."""
    for target in targets:
        if target["kind"] == "collocation":
            add(
                "example_translation",
                [target["id"]],
                "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
            )
    for sense in senses:
        members = [target for target in targets if target.get("sense") == sense["text"]]
        definitions = [target for target in members if target["kind"] == "definition"]
        usage_notes = [target for target in members if target["kind"] == "usage_note"]
        lexical_relations = [
            target for target in members if target["kind"] in {"synonym", "antonym"}
        ]
        grammar_patterns = [
            target for target in members if target["kind"] == "grammar_pattern"
        ]
        collocations = [target for target in members if target["kind"] == "collocation"]
        for definition in definitions:
            if enhanced:
                add(
                    "sense_definition_consistency",
                    [sense["id"], definition["id"]],
                    "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
                )
            for usage_note in usage_notes:
                add(
                    "definition_usage_consistency",
                    [sense["id"], definition["id"], usage_note["id"]],
                    "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
                )
            if lexical_relations and enhanced:
                add(
                    "definition_lexical_relation_consistency",
                    [sense["id"], definition["id"]]
                    + [target["id"] for target in lexical_relations],
                    "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
                )
        for grammar_pattern in grammar_patterns:
            add(
                "pattern_example_coverage",
                [grammar_pattern["id"]]
                + [collocation["id"] for collocation in collocations],
                "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
            )
    core_images = [target for target in targets if target["kind"] == "core_image"]
    sense_by_number = {_sense_number(sense): sense for sense in senses}
    for core_image in core_images:
        referenced = sorted(
            _referenced_sense_numbers(core_image["text"]), key=lambda value: int(value)
        )
        mapped = [sense_by_number[number] for number in referenced if number in sense_by_number]
        if legacy:
            mapped = senses
        if mapped:
            for sense in mapped:
                members = [
                    target
                    for target in targets
                    if target.get("sense") == sense["text"]
                    and target["kind"] in {"definition", "usage_note"}
                ] if enhanced else []
                add(
                    "core_sense_mapping",
                    [core_image["id"], sense["id"]]
                    + [target["id"] for target in members],
                    (
                        "コアイメージの説明が対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。"
                        if legacy
                        else "コアイメージの説明が明示された対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。"
                    ),
                )
        elif senses:
            add(
                "core_inventory_consistency",
                [core_image["id"]] + [sense["id"] for sense in senses],
                "語義番号を限定しない総括的なコアイメージが、記事の語義目録全体を不当に一般化していないことを確認する。",
            )
    if senses:
        high_level_targets = [
            target
            for target in targets
            if target["kind"]
            in {"core_image", "sense_boundary", "definition", "usage_note"}
        ] if enhanced else senses
        add(
            "article_learning_risk",
            [target["id"] for target in high_level_targets],
            "記事全体の語義構成、対比、訳語、限定表現から学習者が誤った一般化をしないことを横断確認する。",
        )


def extract_relations(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build deterministic article-level and cross-target audit relationships."""
    relations: list[dict[str, Any]] = []
    counters: dict[str, int] = {}

    def add(kind: str, target_ids: list[str], description: str) -> None:
        counters[kind] = counters.get(kind, 0) + 1
        canonical = json.dumps(
            {"kind": kind, "target_ids": target_ids, "description": description},
            ensure_ascii=False,
            sort_keys=True,
        )
        relations.append(
            {
                "id": f"{kind}:{counters[kind]:03d}",
                "kind": kind,
                "target_ids": target_ids,
                "description": description,
                "text_sha256": _digest(canonical),
                "requires_evidence": True,
                "evidence_policy": (
                    "two_sources_or_primary"
                    if kind
                    in {
                        "risk_sense_pair",
                        "core_sense_mapping",
                        "core_inventory_consistency",
                        "article_learning_risk",
                    }
                    else "one_source"
                ),
            }
        )

    senses = [target for target in targets if target["kind"] == "sense_boundary"]
    for left, right, reasons in _sense_risk_pairs(targets, senses):
        add(
            "risk_sense_pair",
            [left["id"], right["id"]],
            "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: "
            + "; ".join(reasons),
        )
    _append_shared_relations(
        relations, counters, targets, senses, add, legacy=False, enhanced=True
    )
    return relations


def _extract_relations_v3_legacy(
    targets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Preserve the original v3 inventory for unchanged pre-gate manifests."""
    relations: list[dict[str, Any]] = []
    counters: dict[str, int] = {}

    def add(kind: str, target_ids: list[str], description: str) -> None:
        counters[kind] = counters.get(kind, 0) + 1
        canonical = json.dumps(
            {"kind": kind, "target_ids": target_ids, "description": description},
            ensure_ascii=False,
            sort_keys=True,
        )
        relations.append(
            {
                "id": f"{kind}:{counters[kind]:03d}",
                "kind": kind,
                "target_ids": target_ids,
                "description": description,
                "text_sha256": _digest(canonical),
                "requires_evidence": True,
                "evidence_policy": (
                    "two_sources_or_primary"
                    if kind
                    in {
                        "risk_sense_pair",
                        "core_sense_mapping",
                        "core_inventory_consistency",
                        "article_learning_risk",
                    }
                    else "one_source"
                ),
            }
        )

    senses = [target for target in targets if target["kind"] == "sense_boundary"]
    for left, right, reasons in _sense_risk_pairs(targets, senses):
        add(
            "risk_sense_pair",
            [left["id"], right["id"]],
            "記事内の明示的な相互参照が示す混同リスクについて、語義の最小差、境界、重複を確認する。根拠: "
            + "; ".join(reasons),
        )
    _append_shared_relations(
        relations, counters, targets, senses, add, legacy=False, enhanced=False
    )
    return relations


def _empty_execution() -> dict[str, Any]:
    return {
        "run_id": "",
        "context_id": "",
        "started_at": "",
        "completed_at": "",
        "input_body_sha256": "",
        "prompt_sha256": "",
        "context_mode": "",
        "input_artifacts": [],
    }


def build_manifest(entry_path: Path, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    relative = entry_path.resolve().relative_to(repo_root.resolve()).as_posix()
    relative_entry = Path(relative)
    revision_path = (
        Path("audits/runs")
        / Path(*relative_entry.parts[1:]).with_suffix("")
        / "cycle-001"
        / "revision-001.md"
    )
    targets = extract_targets(entry_path)
    current_body_hash = body_sha256(entry_path)
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "entry_path": relative,
        "body_sha256": current_body_hash,
        "review_history": [],
        "current_cycle": {
            "cycle_id": "cycle-001",
            "parent_cycle_id": None,
            "started_at": "",
            "change_reason": "",
            "body_revisions": [
                {
                    "revision_id": "revision-001",
                    "body_sha256": current_body_hash,
                    "snapshot_path": revision_path.as_posix(),
                    "created_at": "",
                    "reason": "initial audited body",
                }
            ],
            "raw_outputs": {
                "normal_review": {},
                "cold_review": {},
                "final_blind": {},
                "final_review": {},
            },
            "escaped_defects": [],
            "regression_checks": [
                {"category": category, "status": "pending", "notes": ""}
                for category in ESCAPED_DEFECT_CATEGORIES
            ],
        },
        "targets": targets,
        "relations": extract_relations(targets),
        "evidence": [],
        "evidence_links": [],
        "normal_review": {
            "role": "normal_checker",
            "reviewer_id": "",
            "reviewed_at": "",
            "completed": False,
            "execution": _empty_execution(),
            "independent_candidates": [],
            "target_results": [],
            "relation_results": [],
        },
        "cold_review": {
            "role": "cold_reviewer",
            "reviewer_id": "",
            "reviewed_at": "",
            "prompt_version": COLD_REVIEW_PROMPT_VERSION,
            "completed": False,
            "execution": _empty_execution(),
            "summary": "",
            "findings": [],
        },
        "resolutions": [],
        "semantic_gate": {
            "version": "semantic_resolution_v2",
            "body_sha256": current_body_hash,
            "constraints": [],
            "final_inventory_checks": [],
        },
        "final_review": {
            "role": "final_adjudicator",
            "reviewer_id": "",
            "reviewed_at": "",
            "completed": False,
            "execution": {
                **_empty_execution(),
                "reconciliation_started_at": "",
                "reconciliation_input_artifacts": [],
            },
            "body_sha256": "",
            "decision": "pending",
            "blind_review": {
                "completed": False,
                "recorded_at": "",
                "body_sha256": "",
                "audit_visible": False,
                "provisional_decision": "pending",
                "article_findings": [],
                "output_sha256": "",
            },
            "independent_candidates": [],
            "inventory_comparison": [],
            "blind_finding_results": [],
            "target_results": [],
            "relation_results": [],
            "candidate_results": [],
            "finding_results": [],
            "evidence_checks": [],
            "blockers": [],
        },
    }


def blind_review_sha256(final_review: dict[str, Any]) -> str:
    blind = final_review.get("blind_review")
    if not isinstance(blind, dict):
        blind = {}
    candidates = final_review.get("independent_candidates")
    sealed_candidates: list[dict[str, Any]] = []
    if isinstance(candidates, list):
        for candidate in candidates:
            if isinstance(candidate, dict):
                sealed_candidates.append(
                    {
                        key: candidate.get(key)
                        for key in (
                            "id",
                            "surface_form",
                            "frame",
                            "meaning",
                            "disposition",
                            "rationale",
                        )
                    }
                )
    payload = {
        "body_sha256": blind.get("body_sha256"),
        "provisional_decision": blind.get("provisional_decision"),
        # Target/evidence IDs are reconciliation data and are intentionally excluded.
        "independent_candidates": sealed_candidates,
        "article_findings": blind.get("article_findings"),
    }
    return _digest(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _index_by_id(items: Any, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not _nonempty(item.get("id")):
            errors.append(f"{label} contains an item without a non-empty id")
            continue
        item_id = item["id"]
        if item_id in indexed:
            errors.append(f"{label} has duplicate id: {item_id}")
        indexed[item_id] = item
    return indexed


def _validate_legacy_manifest(
    entry_path: Path,
    audit_path: Path,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    errors: list[str] = []
    if not audit_path.is_file():
        try:
            display_path = audit_path.relative_to(repo_root)
        except ValueError:
            display_path = audit_path
        return [f"audit manifest not found: {display_path}"]
    try:
        manifest = json.loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read audit manifest {audit_path}: {exc}"]
    if not isinstance(manifest, dict):
        return [f"audit manifest must be a JSON object: {audit_path}"]

    expected_relative = entry_path.resolve().relative_to(repo_root.resolve()).as_posix()
    if manifest.get("schema_version") != LEGACY_AUDIT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {LEGACY_AUDIT_SCHEMA_VERSION}")
    if manifest.get("entry_path") != expected_relative:
        errors.append(f"entry_path must be {expected_relative}")
    expected_body_hash = body_sha256(entry_path)
    if manifest.get("body_sha256") != expected_body_hash:
        errors.append("audit body_sha256 does not match the current entry body")

    expected_targets = {item["id"]: item for item in extract_targets(entry_path)}
    actual_targets = _index_by_id(manifest.get("targets"), "targets", errors)
    if set(actual_targets) != set(expected_targets):
        missing = sorted(set(expected_targets) - set(actual_targets))
        extra = sorted(set(actual_targets) - set(expected_targets))
        if missing:
            errors.append("targets are missing generated ids: " + ", ".join(missing))
        if extra:
            errors.append("targets contain stale ids: " + ", ".join(extra))
    for target_id in sorted(set(actual_targets) & set(expected_targets)):
        actual = actual_targets[target_id]
        expected = expected_targets[target_id]
        for key in (
            "kind",
            "location",
            "section",
            "sense",
            "text_sha256",
            "requires_evidence",
            "text",
        ):
            if actual.get(key) != expected.get(key):
                errors.append(f"target {target_id} has stale or invalid {key}")

    evidence = _index_by_id(manifest.get("evidence"), "evidence", errors)
    for evidence_id, item in evidence.items():
        for key in ("source_type", "citation", "locator", "supports", "checked_at"):
            if not _nonempty(item.get(key)):
                errors.append(f"evidence {evidence_id} requires non-empty {key}")

    normal = manifest.get("normal_review")
    cold = manifest.get("cold_review")
    final = manifest.get("final_review")
    for label, review, role in (
        ("normal_review", normal, "normal_checker"),
        ("cold_review", cold, "cold_reviewer"),
        ("final_review", final, "final_adjudicator"),
    ):
        if not isinstance(review, dict):
            errors.append(f"{label} must be an object")
            continue
        if review.get("role") != role:
            errors.append(f"{label}.role must be {role}")
        if not _nonempty(review.get("reviewer_id")):
            errors.append(f"{label}.reviewer_id is required")
        if not _nonempty(review.get("reviewed_at")):
            errors.append(f"{label}.reviewed_at is required")
        if review.get("completed") is not True:
            errors.append(f"{label}.completed must be true")

    reviewer_ids = [
        review.get("reviewer_id")
        for review in (normal, cold, final)
        if isinstance(review, dict) and _nonempty(review.get("reviewer_id"))
    ]
    if len(reviewer_ids) == 3 and len(set(reviewer_ids)) != 3:
        errors.append("normal, cold, and final reviewer_id values must be distinct")

    def check_evidence_refs(refs: Any, label: str, required: bool) -> None:
        if not isinstance(refs, list):
            errors.append(f"{label}.evidence_ids must be a list")
            return
        if required and not refs:
            errors.append(f"{label} requires at least one evidence id")
        for evidence_id in refs:
            if evidence_id not in evidence:
                errors.append(f"{label} references unknown evidence id: {evidence_id}")

    normal_candidates: dict[str, dict[str, Any]] = {}
    if isinstance(normal, dict):
        normal_results = _index_by_id(
            normal.get("target_results"), "normal_review.target_results", errors
        )
        if set(normal_results) != set(expected_targets):
            missing = sorted(set(expected_targets) - set(normal_results))
            extra = sorted(set(normal_results) - set(expected_targets))
            if missing:
                errors.append("normal review is missing targets: " + ", ".join(missing))
            if extra:
                errors.append("normal review contains unknown targets: " + ", ".join(extra))
        for target_id, result in normal_results.items():
            if result.get("status") != "pass":
                errors.append(f"normal target {target_id} must have status pass")
            if not _nonempty(result.get("notes")):
                errors.append(f"normal target {target_id} requires concrete notes")
            target = expected_targets.get(target_id)
            check_evidence_refs(
                result.get("evidence_ids"),
                f"normal target {target_id}",
                bool(target and target["requires_evidence"]),
            )

        normal_candidates = _index_by_id(
            normal.get("independent_candidates"),
            "normal_review.independent_candidates",
            errors,
        )
        if not normal_candidates:
            errors.append("normal review requires an externalized independent inventory")
        for candidate_id, candidate in normal_candidates.items():
            for key in ("surface_form", "frame", "meaning", "rationale"):
                if not _nonempty(candidate.get(key)):
                    errors.append(f"candidate {candidate_id} requires non-empty {key}")
            if candidate.get("disposition") not in {"included", "excluded"}:
                errors.append(f"candidate {candidate_id} has invalid disposition")
            article_target_ids = candidate.get("article_target_ids")
            if not isinstance(article_target_ids, list):
                errors.append(f"candidate {candidate_id}.article_target_ids must be a list")
            else:
                if candidate.get("disposition") == "included" and not article_target_ids:
                    errors.append(f"included candidate {candidate_id} needs article_target_ids")
                for target_id in article_target_ids:
                    if target_id not in expected_targets:
                        errors.append(
                            f"candidate {candidate_id} references unknown target: {target_id}"
                        )
            check_evidence_refs(
                candidate.get("evidence_ids"), f"candidate {candidate_id}", True
            )

    cold_findings: dict[str, dict[str, Any]] = {}
    if isinstance(cold, dict):
        if cold.get("prompt_version") != COLD_REVIEW_PROMPT_VERSION:
            errors.append(
                f"cold_review.prompt_version must be {COLD_REVIEW_PROMPT_VERSION}"
            )
        if not _nonempty(cold.get("summary")):
            errors.append("cold_review.summary is required")
        cold_findings = _index_by_id(cold.get("findings"), "cold_review.findings", errors)
        if not cold_findings and "問題候補なし" not in str(cold.get("summary", "")):
            errors.append("cold review with no findings must state 問題候補なし")
        for finding_id, finding in cold_findings.items():
            for key in ("location", "description", "reason", "suggested_direction"):
                if not _nonempty(finding.get(key)):
                    errors.append(f"cold finding {finding_id} requires non-empty {key}")
            check_evidence_refs(
                finding.get("evidence_ids"), f"cold finding {finding_id}", False
            )

    resolutions = _index_by_id(manifest.get("resolutions"), "resolutions", errors)
    if set(resolutions) != set(cold_findings):
        missing = sorted(set(cold_findings) - set(resolutions))
        extra = sorted(set(resolutions) - set(cold_findings))
        if missing:
            errors.append("resolutions are missing findings: " + ", ".join(missing))
        if extra:
            errors.append("resolutions contain unknown findings: " + ", ".join(extra))
    for finding_id, resolution in resolutions.items():
        if resolution.get("status") not in {"adopted", "rejected", "hold"}:
            errors.append(f"resolution {finding_id} has invalid status")
        if not _nonempty(resolution.get("rationale")):
            errors.append(f"resolution {finding_id} requires a rationale")
        check_evidence_refs(
            resolution.get("evidence_ids"), f"resolution {finding_id}", False
        )

    if isinstance(final, dict):
        if final.get("body_sha256") != expected_body_hash:
            errors.append("final_review.body_sha256 does not match the current entry body")
        if final.get("decision") != "pass":
            errors.append("final_review.decision must be pass")
        blockers = final.get("blockers")
        if not isinstance(blockers, list) or blockers:
            errors.append("final_review.blockers must be an empty list for a passed entry")

        final_results = _index_by_id(
            final.get("target_results"), "final_review.target_results", errors
        )
        if set(final_results) != set(expected_targets):
            missing = sorted(set(expected_targets) - set(final_results))
            extra = sorted(set(final_results) - set(expected_targets))
            if missing:
                errors.append("final review is missing targets: " + ", ".join(missing))
            if extra:
                errors.append("final review contains unknown targets: " + ", ".join(extra))
        for target_id, result in final_results.items():
            if result.get("status") != "pass":
                errors.append(f"final target {target_id} must have status pass")
            if not _nonempty(result.get("notes")):
                errors.append(f"final target {target_id} requires concrete notes")
            target = expected_targets.get(target_id)
            if target and target["requires_evidence"] and result.get("evidence_checked") is not True:
                errors.append(f"final target {target_id} must verify its evidence")

        candidate_results = _index_by_id(
            final.get("candidate_results"), "final_review.candidate_results", errors
        )
        if set(candidate_results) != set(normal_candidates):
            missing = sorted(set(normal_candidates) - set(candidate_results))
            extra = sorted(set(candidate_results) - set(normal_candidates))
            if missing:
                errors.append("final review is missing candidates: " + ", ".join(missing))
            if extra:
                errors.append("final review contains unknown candidates: " + ", ".join(extra))
        for candidate_id, result in candidate_results.items():
            if result.get("status") != "pass":
                errors.append(f"final candidate {candidate_id} must have status pass")
            if result.get("evidence_checked") is not True:
                errors.append(f"final candidate {candidate_id} must verify its evidence")
            if not _nonempty(result.get("notes")):
                errors.append(f"final candidate {candidate_id} requires concrete notes")

        finding_results = _index_by_id(
            final.get("finding_results"), "final_review.finding_results", errors
        )
        if set(finding_results) != set(cold_findings):
            missing = sorted(set(cold_findings) - set(finding_results))
            extra = sorted(set(finding_results) - set(cold_findings))
            if missing:
                errors.append("final review is missing findings: " + ", ".join(missing))
            if extra:
                errors.append("final review contains unknown findings: " + ", ".join(extra))
        for finding_id, result in finding_results.items():
            if result.get("status") != "pass":
                errors.append(f"final finding {finding_id} must have status pass")
            if not _nonempty(result.get("notes")):
                errors.append(f"final finding {finding_id} requires concrete notes")

    if any(item.get("status") == "hold" for item in resolutions.values()):
        errors.append("an audit with a hold resolution cannot pass final review")
    return errors


def _timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not _nonempty(value):
        errors.append(f"{label} is required")
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            errors.append(f"{label} must include a timezone")
            return None
        return parsed
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp")
        return None


def _sha256_value(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        errors.append(f"{label} must be a lowercase SHA-256 digest")


def _is_primary_source(source_type: Any) -> bool:
    normalized = str(source_type).strip().lower()
    return normalized in PRIMARY_SOURCE_TYPES


def _safe_repo_file(path_value: Any, repo_root: Path, prefix: str) -> Path | None:
    if not _nonempty(path_value):
        return None
    relative = Path(str(path_value))
    if relative.is_absolute() or ".." in relative.parts:
        return None
    candidate = (repo_root / relative).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return None
    if not relative.as_posix().startswith(prefix):
        return None
    return candidate


def _validate_v3_cycle(
    manifest: dict[str, Any],
    repo_root: Path,
    expected_body_hash: str,
    errors: list[str],
) -> set[str]:
    history = manifest.get("review_history")
    if not isinstance(history, list):
        errors.append("review_history must be a list")
        history = []
    seen_history_cycles: set[str] = set()
    for index, record in enumerate(history):
        label = f"review_history[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        for key in ("cycle_id", "body_sha256", "snapshot_path", "snapshot_sha256", "archived_at"):
            if not _nonempty(record.get(key)):
                errors.append(f"{label}.{key} is required")
        cycle_id = str(record.get("cycle_id", ""))
        if cycle_id in seen_history_cycles:
            errors.append(f"review_history has duplicate cycle_id: {cycle_id}")
        seen_history_cycles.add(cycle_id)
        _sha256_value(record.get("body_sha256"), f"{label}.body_sha256", errors)
        _sha256_value(record.get("snapshot_sha256"), f"{label}.snapshot_sha256", errors)
        _timestamp(record.get("archived_at"), f"{label}.archived_at", errors)
        snapshot = _safe_repo_file(record.get("snapshot_path"), repo_root, "audits/history/")
        if snapshot is None:
            errors.append(f"{label}.snapshot_path must be a safe path under audits/history/")
        elif not snapshot.is_file():
            errors.append(f"{label}.snapshot_path does not exist")
        else:
            actual = hashlib.sha256(snapshot.read_bytes()).hexdigest()
            if actual != record.get("snapshot_sha256"):
                errors.append(f"{label}.snapshot_sha256 does not match the archived bytes")
            else:
                try:
                    archived_manifest = json.loads(snapshot.read_text(encoding="utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    errors.append(f"{label}.snapshot_path is not valid JSON")
                else:
                    if (
                        isinstance(archived_manifest, dict)
                        and archived_manifest.get("schema_version") == AUDIT_SCHEMA_VERSION
                    ):
                        _validate_v3_raw_outputs(archived_manifest, repo_root, errors)

    cycle = manifest.get("current_cycle")
    if not isinstance(cycle, dict):
        errors.append("current_cycle must be an object")
        return {expected_body_hash}
    for key in ("cycle_id", "started_at", "change_reason"):
        if not _nonempty(cycle.get(key)):
            errors.append(f"current_cycle.{key} is required")
    if cycle.get("cycle_id") in seen_history_cycles:
        errors.append("current_cycle.cycle_id must not repeat a historical cycle_id")
    expected_parent = history[-1].get("cycle_id") if history and isinstance(history[-1], dict) else None
    if cycle.get("parent_cycle_id") != expected_parent:
        errors.append("current_cycle.parent_cycle_id must identify the latest historical cycle")
    _timestamp(cycle.get("started_at"), "current_cycle.started_at", errors)

    revisions = cycle.get("body_revisions")
    allowed_hashes: set[str] = set()
    if not isinstance(revisions, list) or not revisions:
        errors.append("current_cycle.body_revisions must be a non-empty list")
        revisions = []
    revision_ids: set[str] = set()
    for index, revision in enumerate(revisions):
        label = f"current_cycle.body_revisions[{index}]"
        if not isinstance(revision, dict):
            errors.append(f"{label} must be an object")
            continue
        for key in (
            "revision_id",
            "body_sha256",
            "snapshot_path",
            "created_at",
            "reason",
        ):
            if not _nonempty(revision.get(key)):
                errors.append(f"{label}.{key} is required")
        revision_id = str(revision.get("revision_id", ""))
        if revision_id in revision_ids:
            errors.append(f"current_cycle.body_revisions has duplicate revision_id: {revision_id}")
        revision_ids.add(revision_id)
        _sha256_value(revision.get("body_sha256"), f"{label}.body_sha256", errors)
        if _nonempty(revision.get("body_sha256")):
            allowed_hashes.add(str(revision["body_sha256"]))
        revision_snapshot = _safe_repo_file(
            revision.get("snapshot_path"), repo_root, "audits/runs/"
        )
        if revision_snapshot is None:
            errors.append(f"{label}.snapshot_path must be a safe path under audits/runs/")
        elif not revision_snapshot.is_file():
            errors.append(f"{label}.snapshot_path does not exist")
        else:
            try:
                snapshot_text = revision_snapshot.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(f"{label}.snapshot_path must be UTF-8 text")
            else:
                if _digest(snapshot_text) != revision.get("body_sha256"):
                    errors.append(f"{label}.snapshot_path does not match body_sha256")
        _timestamp(revision.get("created_at"), f"{label}.created_at", errors)
    if revisions and isinstance(revisions[-1], dict) and revisions[-1].get("body_sha256") != expected_body_hash:
        errors.append("the latest body revision must match the current entry body")

    escaped = cycle.get("escaped_defects")
    if not isinstance(escaped, list):
        errors.append("current_cycle.escaped_defects must be a list")
    else:
        for index, defect in enumerate(escaped):
            label = f"current_cycle.escaped_defects[{index}]"
            if not isinstance(defect, dict):
                errors.append(f"{label} must be an object")
                continue
            if defect.get("category") not in ESCAPED_DEFECT_CATEGORIES:
                errors.append(f"{label}.category is not in the escaped-defect taxonomy")
            for key in ("id", "detected_after_stage", "description", "prevention"):
                if not _nonempty(defect.get(key)):
                    errors.append(f"{label}.{key} is required")
            if not isinstance(defect.get("target_ids"), list):
                errors.append(f"{label}.target_ids must be a list")

    raw_checks = cycle.get("regression_checks")
    if not isinstance(raw_checks, list):
        errors.append("current_cycle.regression_checks must be a list")
        raw_checks = []
    checks = _index_by_id(
        [
            {"id": item.get("category"), **item}
            if isinstance(item, dict)
            else item
            for item in raw_checks
        ],
        "current_cycle.regression_checks",
        errors,
    )
    required_categories = set(_required_defect_categories(manifest))
    if set(checks) != required_categories:
        errors.append("current_cycle.regression_checks must cover every taxonomy category exactly once")
    for category, check in checks.items():
        if check.get("status") not in {"pending", "pass", "not_applicable"}:
            errors.append(f"regression check {category} has invalid status")
        if check.get("status") != "pending" and not _nonempty(check.get("notes")):
            errors.append(f"regression check {category} requires notes")
    return allowed_hashes or {expected_body_hash}


def _validate_v3_raw_outputs(
    manifest: dict[str, Any], repo_root: Path, errors: list[str]
) -> None:
    gate = manifest.get("semantic_gate")
    require_structured_raw = (
        isinstance(gate, dict)
        and gate.get("version") == "semantic_resolution_v2"
    )
    cycle = manifest.get("current_cycle")
    if not isinstance(cycle, dict):
        return
    raw_outputs = cycle.get("raw_outputs")
    if not isinstance(raw_outputs, dict):
        errors.append("current_cycle.raw_outputs must be an object")
        return
    normal = manifest.get("normal_review")
    cold = manifest.get("cold_review")
    final = manifest.get("final_review")
    required: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    if isinstance(normal, dict) and normal.get("completed") is True:
        execution = normal.get("execution")
        required["normal_review"] = (
            normal,
            execution if isinstance(execution, dict) else {},
        )
    if isinstance(cold, dict) and cold.get("completed") is True:
        execution = cold.get("execution")
        required["cold_review"] = (
            cold,
            execution if isinstance(execution, dict) else {},
        )
    if (
        isinstance(final, dict)
        and final.get("completed") is True
        and final.get("decision") in {"pass", "reject"}
    ):
        execution = final.get("execution")
        final_execution = execution if isinstance(execution, dict) else {}
        required["final_blind"] = (final, final_execution)
        required["final_review"] = (final, final_execution)

    seen_paths: set[str] = set()
    for stage, (review, execution) in required.items():
        reference = raw_outputs.get(stage)
        label = f"current_cycle.raw_outputs.{stage}"
        if not isinstance(reference, dict) or not reference:
            errors.append(f"{label} is required for a completed stage")
            continue
        for key in (
            "path",
            "sha256",
            "input_body_sha256",
            "prompt_sha256",
            "run_id",
            "context_id",
        ):
            if not _nonempty(reference.get(key)):
                errors.append(f"{label}.{key} is required")
        _sha256_value(reference.get("sha256"), f"{label}.sha256", errors)
        for key in ("input_body_sha256", "prompt_sha256", "run_id", "context_id"):
            if reference.get(key) != execution.get(key):
                errors.append(f"{label}.{key} must match the stage execution")
        path_value = str(reference.get("path", ""))
        if path_value in seen_paths:
            errors.append("each review stage must reference a distinct raw output file")
        seen_paths.add(path_value)
        raw_path = _safe_repo_file(path_value, repo_root, "audits/runs/")
        if raw_path is None:
            errors.append(f"{label}.path must be a safe path under audits/runs/")
        elif not raw_path.is_file():
            errors.append(f"{label}.path does not exist")
        else:
            raw_bytes = raw_path.read_bytes()
            actual = hashlib.sha256(raw_bytes).hexdigest()
            if actual != reference.get("sha256"):
                errors.append(f"{label}.sha256 does not match the raw output bytes")
            if require_structured_raw:
                try:
                    raw_value = json.loads(raw_bytes.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    errors.append(f"{label}.path must contain a JSON object")
                else:
                    if not isinstance(raw_value, dict):
                        errors.append(f"{label}.path must contain a JSON object")
                    elif raw_value.get("stage") != stage:
                        errors.append(f"{label}.stage must be {stage}")
        if stage == "final_blind":
            blind = review.get("blind_review", {})
            if reference.get("sealed_output_sha256") != blind.get("output_sha256"):
                errors.append(
                    "current_cycle.raw_outputs.final_blind.sealed_output_sha256 "
                    "must match the sealed blind review"
                )


def _validate_v2_manifest(
    entry_path: Path,
    audit_path: Path,
    repo_root: Path,
) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read audit manifest {audit_path}: {exc}"]
    if not isinstance(manifest, dict):
        return [f"audit manifest must be a JSON object: {audit_path}"]

    expected_relative = entry_path.resolve().relative_to(repo_root.resolve()).as_posix()
    front, _ = _split_front_matter(entry_path.read_text(encoding="utf-8"))
    entry_status = front.get("status", "")
    entry_checked = front.get("checked", "").lower() == "true"
    expected_body_hash = body_sha256(entry_path)
    invalidation = _matching_invalidation(entry_path, expected_body_hash, repo_root)
    schema_version = manifest.get("schema_version")
    is_v3 = schema_version == AUDIT_SCHEMA_VERSION
    semantic_gate = manifest.get("semantic_gate")
    is_semantic_v2 = (
        isinstance(semantic_gate, dict)
        and semantic_gate.get("version") == "semantic_resolution_v2"
    )
    allowed_body_hashes = (
        _validate_v3_cycle(manifest, repo_root, expected_body_hash, errors)
        if is_v3
        else {expected_body_hash}
    )

    if schema_version not in {PREVIOUS_AUDIT_SCHEMA_VERSION, AUDIT_SCHEMA_VERSION}:
        errors.append(
            f"schema_version must be {PREVIOUS_AUDIT_SCHEMA_VERSION} or {AUDIT_SCHEMA_VERSION}"
        )
    if manifest.get("entry_path") != expected_relative:
        errors.append(f"entry_path must be {expected_relative}")
    if manifest.get("body_sha256") != expected_body_hash:
        errors.append("audit body_sha256 does not match the current entry body")

    expected_targets = {item["id"]: item for item in extract_targets(entry_path)}
    actual_targets = _index_by_id(manifest.get("targets"), "targets", errors)
    if set(actual_targets) != set(expected_targets):
        missing = sorted(set(expected_targets) - set(actual_targets))
        extra = sorted(set(actual_targets) - set(expected_targets))
        if missing:
            errors.append("targets are missing generated ids: " + ", ".join(missing))
        if extra:
            errors.append("targets contain stale ids: " + ", ".join(extra))
    for target_id in sorted(set(actual_targets) & set(expected_targets)):
        target_keys = (
            "kind",
            "location",
            "section",
            "sense",
            "text_sha256",
            "requires_evidence",
        ) + (("evidence_policy",) if is_v3 else ()) + ("text",)
        for key in target_keys:
            if actual_targets[target_id].get(key) != expected_targets[target_id].get(key):
                errors.append(f"target {target_id} has stale or invalid {key}")

    relation_builder = (
        extract_relations
        if is_semantic_v2
        else (_extract_relations_v3_legacy if is_v3 else _extract_relations_v2)
    )
    expected_relations = {
        item["id"]: item for item in relation_builder(list(expected_targets.values()))
    }
    actual_relations = _index_by_id(manifest.get("relations"), "relations", errors)
    if set(actual_relations) != set(expected_relations):
        missing = sorted(set(expected_relations) - set(actual_relations))
        extra = sorted(set(actual_relations) - set(expected_relations))
        if missing:
            errors.append("relations are missing generated ids: " + ", ".join(missing))
        if extra:
            errors.append("relations contain stale ids: " + ", ".join(extra))
    for relation_id in sorted(set(actual_relations) & set(expected_relations)):
        relation_keys = (
            "kind",
            "target_ids",
            "description",
            "text_sha256",
            "requires_evidence",
        ) + (("evidence_policy",) if is_v3 else ())
        for key in relation_keys:
            if actual_relations[relation_id].get(key) != expected_relations[relation_id].get(key):
                errors.append(f"relation {relation_id} has stale or invalid {key}")

    evidence = _index_by_id(manifest.get("evidence"), "evidence", errors)
    for evidence_id, item in evidence.items():
        for key in ("source_type", "citation", "locator", "supports", "checked_at"):
            if not _nonempty(item.get(key)):
                errors.append(f"evidence {evidence_id} requires non-empty {key}")

    evidence_links = _index_by_id(
        manifest.get("evidence_links"), "evidence_links", errors
    )
    for link_id, link in evidence_links.items():
        if link.get("subject_type") not in {
            "target",
            "relation",
            "normal_candidate",
            "final_candidate",
            "finding",
            "resolution",
            "inventory_comparison",
            "blind_finding",
        }:
            errors.append(f"evidence link {link_id} has invalid subject_type")
        for key in ("subject_id", "evidence_id", "claim", "locator", "supports"):
            if not _nonempty(link.get(key)):
                errors.append(f"evidence link {link_id} requires non-empty {key}")
        if link.get("evidence_id") not in evidence:
            errors.append(
                f"evidence link {link_id} references unknown evidence id: "
                f"{link.get('evidence_id')}"
            )
        if link.get("support_type") not in {
            "direct",
            "inference",
            "counterexample",
            "context",
        }:
            errors.append(f"evidence link {link_id} has invalid support_type")
        if link.get("counterexample_checked") not in {True, False}:
            errors.append(f"evidence link {link_id}.counterexample_checked must be boolean")
        if not _nonempty(link.get("counterexample_result")):
            errors.append(f"evidence link {link_id} requires counterexample_result")
        if is_v3:
            if link.get("locator_kind") not in {
                "sense_number",
                "section",
                "example",
                "paragraph",
                "line",
                "spec_clause",
                "corpus_query",
            }:
                errors.append(f"evidence link {link_id} has invalid locator_kind")
            for key in ("source_detail", "applicability", "counterexample_method"):
                if not _nonempty(link.get(key)):
                    errors.append(f"evidence link {link_id} requires non-empty {key}")
            if is_semantic_v2 and not _nonempty(link.get("source_excerpt_or_summary")):
                errors.append(
                    f"evidence link {link_id} requires non-empty source_excerpt_or_summary"
                )

    def check_link_refs(
        refs: Any,
        label: str,
        required: bool,
        subject_type: str | None = None,
        subject_id: str | None = None,
    ) -> None:
        if not isinstance(refs, list):
            errors.append(f"{label}.evidence_link_ids must be a list")
            return
        if required and not refs:
            errors.append(f"{label} requires at least one evidence link id")
        for link_id in refs:
            link = evidence_links.get(link_id)
            if link is None:
                errors.append(f"{label} references unknown evidence link id: {link_id}")
                continue
            if subject_type is not None and link.get("subject_type") != subject_type:
                errors.append(f"{label} references evidence link for another subject type")
            if subject_id is not None and link.get("subject_id") != subject_id:
                errors.append(f"{label} references evidence link for another subject id")

    def check_evidence_policy(refs: Any, subject: dict[str, Any] | None, label: str) -> None:
        if not is_v3 or not isinstance(subject, dict):
            return
        if not isinstance(refs, list):
            return
        direct_evidence_ids = {
            evidence_links[link_id].get("evidence_id")
            for link_id in refs
            if link_id in evidence_links
            and evidence_links[link_id].get("support_type") == "direct"
        }
        if is_semantic_v2 and subject.get("requires_evidence") and not direct_evidence_ids:
            errors.append(f"{label} requires at least one directly supporting evidence link")
        if subject.get("evidence_policy") != "two_sources_or_primary":
            return
        has_primary = any(
            _is_primary_source(evidence[evidence_id].get("source_type"))
            for evidence_id in direct_evidence_ids
            if evidence_id in evidence
        )
        independent_citations = {
            " ".join(str(evidence[evidence_id].get("citation", "")).lower().split())
            for evidence_id in direct_evidence_ids
            if evidence_id in evidence
        }
        if len(independent_citations) < 2 and not has_primary:
            errors.append(f"{label} requires two independent sources or one primary source")

    def validate_execution(
        review: dict[str, Any],
        label: str,
        context_mode: str,
        input_artifacts: set[str],
    ) -> dict[str, Any]:
        execution = review.get("execution")
        if not isinstance(execution, dict):
            errors.append(f"{label}.execution must be an object")
            return {}
        for key in (
            "run_id",
            "context_id",
            "started_at",
            "completed_at",
            "input_body_sha256",
            "prompt_sha256",
            "context_mode",
        ):
            if not _nonempty(execution.get(key)):
                errors.append(f"{label}.execution.{key} is required")
        if review.get("reviewer_id") != execution.get("run_id"):
            errors.append(f"{label}.reviewer_id must equal execution.run_id")
        if execution.get("input_body_sha256") not in allowed_body_hashes:
            errors.append(f"{label}.execution.input_body_sha256 is stale")
        _sha256_value(
            execution.get("prompt_sha256"),
            f"{label}.execution.prompt_sha256",
            errors,
        )
        if execution.get("context_mode") != context_mode:
            errors.append(f"{label}.execution.context_mode must be {context_mode}")
        artifacts = execution.get("input_artifacts")
        if not isinstance(artifacts, list) or set(artifacts) != input_artifacts:
            errors.append(
                f"{label}.execution.input_artifacts must be exactly "
                + ", ".join(sorted(input_artifacts))
            )
        started = _timestamp(execution.get("started_at"), f"{label}.execution.started_at", errors)
        completed = _timestamp(
            execution.get("completed_at"), f"{label}.execution.completed_at", errors
        )
        if started is not None and completed is not None and completed < started:
            errors.append(f"{label}.execution.completed_at precedes started_at")
        return execution

    normal = manifest.get("normal_review")
    cold = manifest.get("cold_review")
    final = manifest.get("final_review")
    for label, review, role in (
        ("normal_review", normal, "normal_checker"),
        ("cold_review", cold, "cold_reviewer"),
        ("final_review", final, "final_adjudicator"),
    ):
        if not isinstance(review, dict):
            errors.append(f"{label} must be an object")
            continue
        if review.get("role") != role:
            errors.append(f"{label}.role must be {role}")

    normal_execution: dict[str, Any] = {}
    cold_execution: dict[str, Any] = {}
    final_execution: dict[str, Any] = {}
    if isinstance(normal, dict):
        if normal.get("completed") is not True:
            errors.append("normal_review.completed must be true")
        if not _nonempty(normal.get("reviewed_at")):
            errors.append("normal_review.reviewed_at is required")
        normal_execution = validate_execution(
            normal,
            "normal_review",
            "isolated",
            {"entry_body", "check_spec"},
        )
    if isinstance(cold, dict):
        if cold.get("completed") is not True:
            errors.append("cold_review.completed must be true")
        if not _nonempty(cold.get("reviewed_at")):
            errors.append("cold_review.reviewed_at is required")
        cold_execution = validate_execution(
            cold,
            "cold_review",
            "context_free",
            {"entry_body", "cold_review_prompt"},
        )

    decision = final.get("decision") if isinstance(final, dict) else None
    if decision not in {"pending", "pass", "reject"}:
        errors.append("final_review.decision must be pending, pass, or reject")
    if isinstance(final, dict) and decision != "pending":
        if final.get("completed") is not True:
            errors.append("final_review.completed must be true after adjudication")
        if not _nonempty(final.get("reviewed_at")):
            errors.append("final_review.reviewed_at is required after adjudication")
        final_execution = validate_execution(
            final,
            "final_review",
            "context_free",
            {"entry_body", "final_review_spec"},
        )
        reconciliation_artifacts = final_execution.get("reconciliation_input_artifacts")
        required_reconciliation = {
            "entry_body",
            "final_review_spec",
            "audit_manifest",
            "evidence_sources",
        }
        if not isinstance(reconciliation_artifacts, list) or set(
            reconciliation_artifacts
        ) != required_reconciliation:
            errors.append(
                "final_review.execution.reconciliation_input_artifacts must include "
                "only entry_body, final_review_spec, audit_manifest, and evidence_sources"
            )
        _timestamp(
            final_execution.get("reconciliation_started_at"),
            "final_review.execution.reconciliation_started_at",
            errors,
        )

    run_ids = [
        execution.get("run_id")
        for execution in (normal_execution, cold_execution, final_execution)
        if _nonempty(execution.get("run_id"))
    ]
    context_ids = [
        execution.get("context_id")
        for execution in (normal_execution, cold_execution, final_execution)
        if _nonempty(execution.get("context_id"))
    ]
    if len(run_ids) == 3 and len(set(run_ids)) != 3:
        errors.append("normal, cold, and final execution.run_id values must be distinct")
    if len(context_ids) == 3 and len(set(context_ids)) != 3:
        errors.append("normal, cold, and final execution.context_id values must be distinct")

    normal_candidates: dict[str, dict[str, Any]] = {}
    if isinstance(normal, dict):
        normal_results = _index_by_id(
            normal.get("target_results"), "normal_review.target_results", errors
        )
        if set(normal_results) != set(expected_targets):
            errors.append("normal review must decide every generated target exactly once")
        for target_id, result in normal_results.items():
            if result.get("status") != "pass":
                errors.append(f"normal target {target_id} must have status pass")
            if not _nonempty(result.get("notes")):
                errors.append(f"normal target {target_id} requires notes")
            target = expected_targets.get(target_id)
            check_link_refs(
                result.get("evidence_link_ids"),
                f"normal target {target_id}",
                bool(target and target["requires_evidence"]),
                "target",
                target_id,
            )
            check_evidence_policy(
                result.get("evidence_link_ids"), target, f"normal target {target_id}"
            )

        normal_relation_results = _index_by_id(
            normal.get("relation_results"), "normal_review.relation_results", errors
        )
        if set(normal_relation_results) != set(expected_relations):
            errors.append("normal review must decide every generated relation exactly once")
        for relation_id, result in normal_relation_results.items():
            if result.get("status") != "pass":
                errors.append(f"normal relation {relation_id} must have status pass")
            if not _nonempty(result.get("notes")):
                errors.append(f"normal relation {relation_id} requires notes")
            check_link_refs(
                result.get("evidence_link_ids"),
                f"normal relation {relation_id}",
                True,
                "relation",
                relation_id,
            )
            check_evidence_policy(
                result.get("evidence_link_ids"),
                expected_relations.get(relation_id),
                f"normal relation {relation_id}",
            )

        normal_candidates = _index_by_id(
            normal.get("independent_candidates"),
            "normal_review.independent_candidates",
            errors,
        )
        if not normal_candidates:
            errors.append("normal review requires an externalized independent inventory")
        for candidate_id, candidate in normal_candidates.items():
            for key in ("surface_form", "frame", "meaning", "rationale"):
                if not _nonempty(candidate.get(key)):
                    errors.append(f"normal candidate {candidate_id} requires non-empty {key}")
            if candidate.get("disposition") not in {"included", "excluded"}:
                errors.append(f"normal candidate {candidate_id} has invalid disposition")
            article_target_ids = candidate.get("article_target_ids")
            if not isinstance(article_target_ids, list):
                errors.append(f"normal candidate {candidate_id}.article_target_ids must be a list")
            else:
                if candidate.get("disposition") == "included" and not article_target_ids:
                    errors.append(f"included normal candidate {candidate_id} needs article_target_ids")
                for target_id in article_target_ids:
                    if target_id not in expected_targets:
                        errors.append(
                            f"normal candidate {candidate_id} references unknown target: {target_id}"
                        )
            check_link_refs(
                candidate.get("evidence_link_ids"),
                f"normal candidate {candidate_id}",
                True,
                "normal_candidate",
                candidate_id,
            )

    cold_findings: dict[str, dict[str, Any]] = {}
    if isinstance(cold, dict):
        if cold.get("prompt_version") != COLD_REVIEW_PROMPT_VERSION:
            errors.append(
                f"cold_review.prompt_version must be {COLD_REVIEW_PROMPT_VERSION}"
            )
        if not _nonempty(cold.get("summary")):
            errors.append("cold_review.summary is required")
        cold_findings = _index_by_id(cold.get("findings"), "cold_review.findings", errors)
        if not cold_findings and "問題候補なし" not in str(cold.get("summary", "")):
            errors.append("cold review with no findings must state 問題候補なし")
        for finding_id, finding in cold_findings.items():
            for key in ("location", "description", "reason", "suggested_direction"):
                if not _nonempty(finding.get(key)):
                    errors.append(f"cold finding {finding_id} requires non-empty {key}")
            if is_semantic_v2:
                anchors = _index_by_id(
                    finding.get("scope_anchors"),
                    f"cold finding {finding_id}.scope_anchors",
                    errors,
                )
                if not anchors:
                    errors.append(
                        f"cold finding {finding_id} requires at least one scope anchor"
                    )
                for anchor_id, anchor in anchors.items():
                    for key in ("exact_quote", "location_hint"):
                        if not _nonempty(anchor.get(key)):
                            errors.append(
                                f"cold finding {finding_id} anchor {anchor_id} requires {key}"
                            )
            check_link_refs(
                finding.get("evidence_link_ids"),
                f"cold finding {finding_id}",
                False,
                "finding",
                finding_id,
            )

    resolutions = _index_by_id(manifest.get("resolutions"), "resolutions", errors)
    if set(resolutions) != set(cold_findings):
        errors.append("resolutions must cover every cold finding exactly once")
    for finding_id, resolution in resolutions.items():
        status = resolution.get("status")
        if status not in {"adopted", "rejected", "hold"}:
            errors.append(f"resolution {finding_id} has invalid status")
        if not isinstance(resolution.get("problem_confirmed"), bool):
            errors.append(f"resolution {finding_id}.problem_confirmed must be boolean")
        for key in ("rationale", "remaining_risk"):
            if not _nonempty(resolution.get(key)):
                errors.append(f"resolution {finding_id} requires non-empty {key}")
        for key in (
            "required_changes",
            "affected_target_ids",
            "affected_relation_ids",
            "implemented_changes",
        ):
            value = resolution.get(key)
            if not isinstance(value, list):
                errors.append(f"resolution {finding_id}.{key} must be a list")
            elif key in {"required_changes", "implemented_changes"} and any(
                not _nonempty(item) for item in value
            ):
                errors.append(f"resolution {finding_id}.{key} must contain text items")
        for target_id in resolution.get("affected_target_ids", []):
            if target_id not in expected_targets:
                errors.append(f"resolution {finding_id} references unknown target {target_id}")
        for relation_id in resolution.get("affected_relation_ids", []):
            if relation_id not in expected_relations:
                errors.append(f"resolution {finding_id} references unknown relation {relation_id}")
        if is_semantic_v2:
            finding = cold_findings.get(finding_id, {})
            anchors = _index_by_id(
                finding.get("scope_anchors"),
                f"cold finding {finding_id}.scope_anchors",
                errors,
            )
            anchor_results = _index_by_id(
                resolution.get("scope_anchor_results"),
                f"resolution {finding_id}.scope_anchor_results",
                errors,
            )
            if set(anchor_results) != set(anchors):
                errors.append(
                    f"resolution {finding_id} must resolve every cold-finding scope anchor exactly once"
                )
            for anchor_id, result in anchor_results.items():
                if result.get("status") not in {
                    "corrected",
                    "removed",
                    "unchanged_valid",
                    "not_applicable",
                }:
                    errors.append(
                        f"resolution {finding_id} anchor {anchor_id} has invalid status"
                    )
                if not _nonempty(result.get("notes")):
                    errors.append(
                        f"resolution {finding_id} anchor {anchor_id} requires notes"
                    )
                anchor_targets = result.get("affected_target_ids")
                anchor_queries = result.get("article_queries")
                if not isinstance(anchor_targets, list) or not isinstance(anchor_queries, list):
                    errors.append(
                        f"resolution {finding_id} anchor {anchor_id} target/query fields must be lists"
                    )
                    continue
                for target_id in anchor_targets:
                    if target_id not in expected_targets:
                        errors.append(
                            f"resolution {finding_id} anchor {anchor_id} references unknown target {target_id}"
                        )
                if resolution.get("problem_confirmed") is True and not (
                    anchor_targets or anchor_queries
                ):
                    errors.append(
                        f"confirmed resolution {finding_id} anchor {anchor_id} must map a target or article query"
                    )
        if status == "adopted":
            if resolution.get("problem_confirmed") is not True:
                errors.append(f"adopted resolution {finding_id} must confirm the problem")
            if not resolution.get("required_changes"):
                errors.append(f"adopted resolution {finding_id} requires required_changes")
            if not resolution.get("implemented_changes"):
                errors.append(f"adopted resolution {finding_id} requires implemented_changes")
        if status == "rejected" and resolution.get("problem_confirmed") is not False:
            errors.append(f"rejected resolution {finding_id} cannot confirm the problem")
        check_link_refs(
            resolution.get("evidence_link_ids"),
            f"resolution {finding_id}",
            True,
            "resolution",
            finding_id,
        )

    final_candidates: dict[str, dict[str, Any]] = {}
    blind_findings: dict[str, dict[str, Any]] = {}
    inventory_comparisons: dict[str, dict[str, Any]] = {}
    final_failure = False
    if isinstance(final, dict) and decision != "pending":
        if final.get("body_sha256") != expected_body_hash:
            errors.append("final_review.body_sha256 does not match the current entry body")
        blind = final.get("blind_review")
        if not isinstance(blind, dict):
            errors.append("final_review.blind_review must be an object")
            blind = {}
        if blind.get("completed") is not True:
            errors.append("final_review.blind_review.completed must be true")
        if blind.get("body_sha256") != expected_body_hash:
            errors.append("final blind review body_sha256 is stale")
        if blind.get("audit_visible") is not False:
            errors.append("final blind review must record audit_visible as false")
        if blind.get("provisional_decision") not in {"pass", "reject"}:
            errors.append("final blind review provisional_decision must be pass or reject")
        blind_recorded = _timestamp(
            blind.get("recorded_at"), "final_review.blind_review.recorded_at", errors
        )
        final_started = _timestamp(
            final_execution.get("started_at"),
            "final_review.execution.started_at",
            errors,
        )
        final_completed = _timestamp(
            final_execution.get("completed_at"),
            "final_review.execution.completed_at",
            errors,
        )
        reconciliation_started = _timestamp(
            final_execution.get("reconciliation_started_at"),
            "final_review.execution.reconciliation_started_at",
            errors,
        )
        if (
            final_started is not None
            and blind_recorded is not None
            and blind_recorded < final_started
        ):
            errors.append("final blind review was recorded before final execution started")
        if (
            blind_recorded is not None
            and reconciliation_started is not None
            and reconciliation_started < blind_recorded
        ):
            errors.append("final reconciliation started before blind review was recorded")
        if (
            reconciliation_started is not None
            and final_completed is not None
            and final_completed < reconciliation_started
        ):
            errors.append("final review completed before reconciliation started")

        final_candidates = _index_by_id(
            final.get("independent_candidates"),
            "final_review.independent_candidates",
            errors,
        )
        if not final_candidates:
            errors.append("final blind review requires an independent inventory")
        for candidate_id, candidate in final_candidates.items():
            for key in ("surface_form", "frame", "meaning", "rationale"):
                if not _nonempty(candidate.get(key)):
                    errors.append(f"final candidate {candidate_id} requires non-empty {key}")
            if candidate.get("disposition") not in {"included", "excluded"}:
                errors.append(f"final candidate {candidate_id} has invalid disposition")
            article_target_ids = candidate.get("article_target_ids")
            if not isinstance(article_target_ids, list):
                errors.append(f"final candidate {candidate_id}.article_target_ids must be a list")
            else:
                if candidate.get("disposition") == "included" and not article_target_ids:
                    errors.append(
                        f"included final candidate {candidate_id} needs article_target_ids"
                    )
                for target_id in article_target_ids:
                    if target_id not in expected_targets:
                        errors.append(
                            f"final candidate {candidate_id} references unknown target: {target_id}"
                        )
            check_link_refs(
                candidate.get("evidence_link_ids"),
                f"final candidate {candidate_id}",
                True,
                "final_candidate",
                candidate_id,
            )

        blind_findings = _index_by_id(
            blind.get("article_findings"),
            "final_review.blind_review.article_findings",
            errors,
        )
        for finding_id, finding in blind_findings.items():
            for key in ("location", "description", "reason"):
                if not _nonempty(finding.get(key)):
                    errors.append(f"blind finding {finding_id} requires non-empty {key}")
        if blind.get("output_sha256") != blind_review_sha256(final):
            errors.append("final blind review output_sha256 does not seal its blind output")

        inventory_comparisons = _index_by_id(
            final.get("inventory_comparison"),
            "final_review.inventory_comparison",
            errors,
        )
        covered_normal: set[str] = set()
        covered_final: set[str] = set()
        for comparison_id, comparison in inventory_comparisons.items():
            if comparison.get("comparison") not in {
                "match",
                "normal_only",
                "final_only",
                "classification_conflict",
            }:
                errors.append(f"inventory comparison {comparison_id} has invalid comparison")
            if comparison.get("status") not in {"pass", "fail"}:
                errors.append(f"inventory comparison {comparison_id} has invalid status")
            if comparison.get("status") == "fail":
                final_failure = True
            if not _nonempty(comparison.get("rationale")):
                errors.append(f"inventory comparison {comparison_id} requires rationale")
            normal_ids = comparison.get("normal_candidate_ids")
            final_ids = comparison.get("final_candidate_ids")
            if not isinstance(normal_ids, list) or not isinstance(final_ids, list):
                errors.append(
                    f"inventory comparison {comparison_id} candidate id fields must be lists"
                )
                continue
            for candidate_id in normal_ids:
                if candidate_id not in normal_candidates:
                    errors.append(
                        f"inventory comparison {comparison_id} has unknown normal candidate"
                    )
                covered_normal.add(candidate_id)
            for candidate_id in final_ids:
                if candidate_id not in final_candidates:
                    errors.append(
                        f"inventory comparison {comparison_id} has unknown final candidate"
                    )
                covered_final.add(candidate_id)
            check_link_refs(
                comparison.get("evidence_link_ids"),
                f"inventory comparison {comparison_id}",
                True,
                "inventory_comparison",
                comparison_id,
            )
        if covered_normal != set(normal_candidates):
            errors.append("inventory comparison does not cover every normal candidate")
        if covered_final != set(final_candidates):
            errors.append("inventory comparison does not cover every final candidate")

        final_results = _index_by_id(
            final.get("target_results"), "final_review.target_results", errors
        )
        if set(final_results) != set(expected_targets):
            errors.append("final review must decide every generated target exactly once")
        for target_id, result in final_results.items():
            if result.get("status") not in {"pass", "fail"}:
                errors.append(f"final target {target_id} has invalid status")
            if result.get("status") == "fail":
                final_failure = True
            if not _nonempty(result.get("notes")):
                errors.append(f"final target {target_id} requires notes")
            target = expected_targets.get(target_id)
            check_link_refs(
                result.get("evidence_link_ids_checked"),
                f"final target {target_id}",
                bool(target and target["requires_evidence"]),
                "target",
                target_id,
            )
            check_evidence_policy(
                result.get("evidence_link_ids_checked"),
                target,
                f"final target {target_id}",
            )

        final_relation_results = _index_by_id(
            final.get("relation_results"), "final_review.relation_results", errors
        )
        if set(final_relation_results) != set(expected_relations):
            errors.append("final review must decide every generated relation exactly once")
        for relation_id, result in final_relation_results.items():
            if result.get("status") not in {"pass", "fail"}:
                errors.append(f"final relation {relation_id} has invalid status")
            if result.get("status") == "fail":
                final_failure = True
            if not _nonempty(result.get("notes")):
                errors.append(f"final relation {relation_id} requires notes")
            check_link_refs(
                result.get("evidence_link_ids_checked"),
                f"final relation {relation_id}",
                True,
                "relation",
                relation_id,
            )
            check_evidence_policy(
                result.get("evidence_link_ids_checked"),
                expected_relations.get(relation_id),
                f"final relation {relation_id}",
            )

        candidate_results = _index_by_id(
            final.get("candidate_results"), "final_review.candidate_results", errors
        )
        if set(candidate_results) != set(normal_candidates):
            errors.append("final review must decide every normal candidate exactly once")
        for candidate_id, result in candidate_results.items():
            if result.get("status") not in {"pass", "fail"}:
                errors.append(f"final candidate result {candidate_id} has invalid status")
            if result.get("status") == "fail":
                final_failure = True
            if not _nonempty(result.get("notes")):
                errors.append(f"final candidate result {candidate_id} requires notes")
            check_link_refs(
                result.get("evidence_link_ids_checked"),
                f"final candidate result {candidate_id}",
                True,
                "normal_candidate",
                candidate_id,
            )

        blind_finding_results = _index_by_id(
            final.get("blind_finding_results"),
            "final_review.blind_finding_results",
            errors,
        )
        if set(blind_finding_results) != set(blind_findings):
            errors.append("final review must reconcile every blind finding exactly once")
        for finding_id, result in blind_finding_results.items():
            if result.get("status") not in {"pass", "fail"}:
                errors.append(f"blind finding result {finding_id} has invalid status")
            if result.get("status") == "fail":
                final_failure = True
            if not _nonempty(result.get("notes")):
                errors.append(f"blind finding result {finding_id} requires notes")
            check_link_refs(
                result.get("evidence_link_ids_checked"),
                f"blind finding result {finding_id}",
                True,
                "blind_finding",
                finding_id,
            )

        finding_results = _index_by_id(
            final.get("finding_results"), "final_review.finding_results", errors
        )
        if set(finding_results) != set(cold_findings):
            errors.append("final review must decide every cold finding exactly once")
        for finding_id, result in finding_results.items():
            if result.get("finding_validity") not in {"valid", "invalid", "partial"}:
                errors.append(f"final finding {finding_id} has invalid finding_validity")
            if result.get("resolution_status") not in {"resolved", "unresolved"}:
                errors.append(f"final finding {finding_id} has invalid resolution_status")
            if result.get("status") not in {"pass", "fail"}:
                errors.append(f"final finding {finding_id} has invalid status")
            verified_changes = result.get("verified_changes")
            if not isinstance(verified_changes, list) or any(
                not _nonempty(item) for item in verified_changes
            ):
                errors.append(f"final finding {finding_id}.verified_changes must be a text list")
            if not isinstance(result.get("unresolved_problem"), str):
                errors.append(f"final finding {finding_id}.unresolved_problem must be text")
            if result.get("resolution_status") == "unresolved" or result.get("status") == "fail":
                final_failure = True
            if not _nonempty(result.get("notes")):
                errors.append(f"final finding {finding_id} requires notes")
            check_link_refs(
                result.get("evidence_link_ids_checked"),
                f"final finding {finding_id}",
                True,
            )

        if is_semantic_v2:
            required_final_links: set[str] = set()
            for collection in (
                final_results,
                final_relation_results,
                candidate_results,
                blind_finding_results,
                finding_results,
            ):
                for result in collection.values():
                    refs = result.get("evidence_link_ids_checked")
                    if isinstance(refs, list):
                        required_final_links.update(
                            str(value) for value in refs if _nonempty(value)
                        )
            for collection in (final_candidates, inventory_comparisons):
                for item in collection.values():
                    refs = item.get("evidence_link_ids")
                    if isinstance(refs, list):
                        required_final_links.update(
                            str(value) for value in refs if _nonempty(value)
                        )
            evidence_checks = _index_by_id(
                final.get("evidence_checks"),
                "final_review.evidence_checks",
                errors,
            )
            if set(evidence_checks) != required_final_links:
                missing = sorted(required_final_links - set(evidence_checks))
                extra = sorted(set(evidence_checks) - required_final_links)
                if missing:
                    errors.append(
                        "final evidence checks are missing evidence links: "
                        + ", ".join(missing)
                    )
                if extra:
                    errors.append(
                        "final evidence checks contain unused evidence links: "
                        + ", ".join(extra)
                    )
            for link_id, check in evidence_checks.items():
                if link_id not in evidence_links:
                    errors.append(
                        f"final evidence check {link_id} references an unknown evidence link"
                    )
                if check.get("status") not in {"pass", "fail"}:
                    errors.append(
                        f"final evidence check {link_id}.status must be pass or fail"
                    )
                for key in (
                    "claim_supported",
                    "locator_verified",
                    "applicability_confirmed",
                ):
                    if not isinstance(check.get(key), bool):
                        errors.append(
                            f"final evidence check {link_id}.{key} must be boolean"
                        )
                if check.get("contradiction_status") not in {
                    "no_contradiction",
                    "resolved",
                    "contradiction_found",
                }:
                    errors.append(
                        f"final evidence check {link_id} has invalid contradiction_status"
                    )
                if not _nonempty(check.get("notes")):
                    errors.append(f"final evidence check {link_id} requires notes")
                if decision == "pass" and (
                    check.get("status") != "pass"
                    or check.get("claim_supported") is not True
                    or check.get("locator_verified") is not True
                    or check.get("applicability_confirmed") is not True
                    or check.get("contradiction_status") == "contradiction_found"
                ):
                    final_failure = True

    blockers = final.get("blockers") if isinstance(final, dict) else None
    if not isinstance(blockers, list):
        errors.append("final_review.blockers must be a list")
        blockers = []
    for blocker in blockers:
        if not isinstance(blocker, dict):
            errors.append("final_review.blockers must contain objects")
            continue
        for key in ("id", "subject_id", "problem", "required_change"):
            if not _nonempty(blocker.get(key)):
                errors.append(f"final blocker requires non-empty {key}")

    if decision == "pending":
        if isinstance(final, dict) and final.get("completed") is not False:
            errors.append("pending final review must have completed false")
        has_hold = any(item.get("status") == "hold" for item in resolutions.values())
        if entry_checked or entry_status not in {"review_ready", "needs_review"}:
            errors.append(
                "pending final review is valid only for review_ready or needs_review, "
                "with checked false"
            )
        if entry_status == "needs_review" and not has_hold:
            errors.append("pending needs_review audit requires a hold resolution")
        if entry_status == "review_ready" and has_hold:
            errors.append("review_ready audit cannot retain a hold resolution")
        if blockers:
            errors.append("pending final review cannot have blockers")
    elif decision == "pass":
        if blockers:
            errors.append("passed final review must have no blockers")
        if final_failure:
            errors.append("passed final review contains a failed or unresolved result")
        if any(item.get("status") == "hold" for item in resolutions.values()):
            errors.append("passed final review cannot contain a hold resolution")
        if invalidation is not None:
            if entry_status != "needs_review" or entry_checked:
                errors.append(
                    "an invalidated passed review requires needs_review/checked false"
                )
        elif entry_status not in {"review_ready", "checked", "final"}:
            errors.append("passed final review has an invalid entry status")
        if entry_status in FINAL_STATUSES and not entry_checked:
            errors.append("checked/final entry with passed review must have checked true")
    elif decision == "reject":
        if not blockers:
            errors.append("rejected final review requires at least one blocker")
        if not final_failure and not (
            isinstance(final, dict)
            and isinstance(final.get("blind_review"), dict)
            and final["blind_review"].get("provisional_decision") == "reject"
        ):
            errors.append("rejected final review must record a failed or unresolved result")
        if entry_status != "needs_review" or entry_checked:
            errors.append("rejected final review requires needs_review/checked false")

    if is_v3 and decision in {"pass", "reject"}:
        cycle = manifest.get("current_cycle", {})
        checks = cycle.get("regression_checks", []) if isinstance(cycle, dict) else []
        if any(
            not isinstance(check, dict)
            or check.get("status") not in {"pass", "not_applicable"}
            for check in checks
        ):
            errors.append(
                "completed v3 audit requires every escaped-defect regression check "
                "to be pass or not_applicable"
            )
        _validate_v3_raw_outputs(manifest, repo_root, errors)
    elif is_v3:
        _validate_v3_raw_outputs(manifest, repo_root, errors)

    valid_subjects = {
        "target": set(expected_targets),
        "relation": set(expected_relations),
        "normal_candidate": set(normal_candidates),
        "final_candidate": set(final_candidates),
        "finding": set(cold_findings),
        "resolution": set(resolutions),
        "inventory_comparison": set(inventory_comparisons),
        "blind_finding": set(blind_findings),
    }
    for link_id, link in evidence_links.items():
        subject_type = link.get("subject_type")
        subject_id = link.get("subject_id")
        if subject_type in valid_subjects and subject_id not in valid_subjects[subject_type]:
            errors.append(f"evidence link {link_id} references unknown subject id")
    return errors


def validate_manifest(
    entry_path: Path,
    audit_path: Path,
    repo_root: Path = REPO_ROOT,
    *,
    require_current: bool = False,
) -> list[str]:
    if not audit_path.is_file():
        try:
            display_path = audit_path.relative_to(repo_root)
        except ValueError:
            display_path = audit_path
        return [f"audit manifest not found: {display_path}"]
    try:
        manifest = json.loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read audit manifest {audit_path}: {exc}"]
    if not isinstance(manifest, dict):
        return [f"audit manifest must be a JSON object: {audit_path}"]
    schema_version = manifest.get("schema_version")
    if schema_version == LEGACY_AUDIT_SCHEMA_VERSION:
        if require_current:
            return [
                f"changed audited content must use schema_version {AUDIT_SCHEMA_VERSION}"
            ]
        return _validate_legacy_manifest(entry_path, audit_path, repo_root)
    if schema_version == PREVIOUS_AUDIT_SCHEMA_VERSION:
        if require_current:
            return [
                f"changed audited content must use schema_version {AUDIT_SCHEMA_VERSION}"
            ]
        return _validate_v2_manifest(entry_path, audit_path, repo_root)
    if schema_version != AUDIT_SCHEMA_VERSION:
        return [f"schema_version must be {AUDIT_SCHEMA_VERSION}"]
    return _validate_v2_manifest(entry_path, audit_path, repo_root)


def _git_changed_paths(base: str, head: str, repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", base, head],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _git_file_at(ref: str, relative: str, repo_root: Path) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{relative}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    return result.stdout if result.returncode == 0 else None


def _body_sha256_text(text: str) -> str:
    _, body = _split_front_matter(text)
    return _digest(body)


def _entry_path_for_audit_relative(path: str) -> str | None:
    if not path.startswith("audits/") or not path.endswith(".json"):
        return None
    relative = Path(path).relative_to("audits")
    if len(relative.parts) != 2:
        return None
    return (Path("entries") / relative.with_suffix(".md")).as_posix()


def _entry_path_for_audit_artifact(path: str) -> str | None:
    parts = Path(path).parts
    if len(parts) >= 6 and parts[:2] == ("audits", "runs"):
        return (Path("entries") / parts[2] / f"{parts[3]}.md").as_posix()
    if len(parts) >= 5 and parts[:2] == ("audits", "history"):
        return (Path("entries") / parts[2] / f"{parts[3]}.md").as_posix()
    return None


def _completed_manifest(manifest: dict[str, Any]) -> bool:
    final = manifest.get("final_review")
    return (
        isinstance(final, dict)
        and final.get("completed") is True
        and final.get("decision") in {"pass", "reject"}
    )


def _validate_append_only_transition(
    relative: str,
    entry_path: Path,
    audit_path: Path,
    base: str,
    repo_root: Path,
) -> list[str]:
    errors: list[str] = []
    audit_relative = audit_path.relative_to(repo_root).as_posix()
    base_audit_bytes = _git_file_at(base, audit_relative, repo_root)
    base_entry_bytes = _git_file_at(base, relative, repo_root)
    if base_audit_bytes is None:
        return errors
    try:
        base_manifest = json.loads(base_audit_bytes.decode("utf-8"))
        head_manifest = json.loads(audit_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, OSError):
        return errors
    if not isinstance(base_manifest, dict) or not isinstance(head_manifest, dict):
        return errors
    body_changed = (
        base_entry_bytes is not None
        and _body_sha256_text(base_entry_bytes.decode("utf-8"))
        != body_sha256(entry_path)
    )
    try:
        head_audit_bytes = audit_path.read_bytes()
    except OSError:
        head_audit_bytes = b""
    audit_changed = head_audit_bytes != base_audit_bytes
    must_append = body_changed or (_completed_manifest(base_manifest) and audit_changed)
    head_history = head_manifest.get("review_history")
    if not isinstance(head_history, list):
        head_history = []
    base_history = base_manifest.get("review_history", [])
    if not isinstance(base_history, list):
        base_history = []
    if head_history[: len(base_history)] != base_history:
        errors.append("review_history must preserve the base revision as an immutable prefix")
    if not must_append:
        base_cycle = base_manifest.get("current_cycle")
        head_cycle = head_manifest.get("current_cycle")
        if (
            isinstance(base_cycle, dict)
            and isinstance(head_cycle, dict)
            and base_cycle.get("cycle_id") != head_cycle.get("cycle_id")
        ):
            errors.append("an incomplete audit must continue in its existing current_cycle")
        return errors
    if head_manifest.get("schema_version") != AUDIT_SCHEMA_VERSION:
        errors.append(f"a revised or previously completed audit must use {AUDIT_SCHEMA_VERSION}")
        return errors
    snapshot_sha = hashlib.sha256(base_audit_bytes).hexdigest()
    new_records = head_history[len(base_history) :]
    matching = [
        record
        for record in new_records
        if isinstance(record, dict)
        and record.get("snapshot_sha256") == snapshot_sha
        and record.get("body_sha256") == base_manifest.get("body_sha256")
    ]
    if not matching:
        errors.append(
            "body changes and completed-audit revisions must append an exact snapshot "
            "of the base audit"
        )
    base_cycle = base_manifest.get("current_cycle")
    head_cycle = head_manifest.get("current_cycle")
    if isinstance(base_cycle, dict) and isinstance(head_cycle, dict):
        if base_cycle.get("cycle_id") == head_cycle.get("cycle_id"):
            errors.append("a revised completed audit must start a new cycle_id")
    return errors


def validate_changed(base: str, head: str, repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    changed = _git_changed_paths(base, head, repo_root)
    if INVALIDATION_REGISTRY.as_posix() in changed:
        errors.extend(validate_invalidation_registry(repo_root))
    entry_paths = {
        path for path in changed if path.startswith("entries/") and path.endswith(".md")
    }
    audit_sources: dict[str, list[Path]] = {}
    for path in changed:
        candidate_entry = _entry_path_for_audit_relative(path)
        if candidate_entry is None:
            candidate_entry = _entry_path_for_audit_artifact(path)
        if candidate_entry is not None:
            entry_paths.add(candidate_entry)
            audit_sources.setdefault(candidate_entry, []).append(repo_root / path)

    for relative in sorted(entry_paths):
        entry_path = repo_root / relative
        if not entry_path.is_file():
            if any(path.is_file() for path in audit_sources.get(relative, [])):
                errors.append(f"changed audit has no entry: {relative}")
            continue
        front, _ = _split_front_matter(entry_path.read_text(encoding="utf-8"))
        status = front.get("status")
        audit_path = audit_path_for_entry(entry_path, repo_root)
        if status not in AUDITED_STATUSES:
            continue
        if status == "needs_review" and not audit_path.is_file():
            continue
        for error in validate_manifest(
            entry_path, audit_path, repo_root, require_current=True
        ):
            errors.append(f"{relative}: {error}")
        if audit_path.is_file():
            for error in _validate_append_only_transition(
                relative, entry_path, audit_path, base, repo_root
            ):
                errors.append(f"{relative}: {error}")
    return errors


def validate_all_audited(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = validate_invalidation_registry(repo_root)
    audits_dir = repo_root / "audits"
    if not audits_dir.is_dir():
        return []
    for audit_path in sorted(audits_dir.rglob("*.json")):
        relative = audit_path.relative_to(audits_dir).with_suffix(".md")
        if len(relative.parts) != 2:
            continue
        entry_path = repo_root / "entries" / relative
        if not entry_path.is_file():
            errors.append(f"audit has no entry: {audit_path.relative_to(repo_root)}")
            continue
        for error in validate_manifest(entry_path, audit_path, repo_root):
            errors.append(f"{entry_path.relative_to(repo_root)}: {error}")
    return errors


def validate_sync(entry_paths: list[Path], repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    for entry_path in entry_paths:
        resolved = entry_path.resolve()
        try:
            relative = resolved.relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            errors.append(f"sync entry must be under the repository: {entry_path}")
            continue
        if not resolved.is_file() or not relative.startswith("entries/") or not relative.endswith(".md"):
            errors.append(f"invalid sync entry: {relative}")
            continue
        front, _ = _split_front_matter(resolved.read_text(encoding="utf-8"))
        if front.get("status") not in FINAL_STATUSES:
            continue
        audit_path = audit_path_for_entry(resolved, repo_root)
        for error in validate_manifest(resolved, audit_path, repo_root):
            errors.append(f"{relative}: {error}")
    return errors


def _write_latest_revision_snapshot(
    manifest: dict[str, Any], entry_path: Path, repo_root: Path
) -> None:
    cycle = manifest["current_cycle"]
    revision = cycle["body_revisions"][-1]
    snapshot = _safe_repo_file(revision["snapshot_path"], repo_root, "audits/runs/")
    if snapshot is None:
        raise ValueError("generated revision snapshot path is not safe")
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text(_entry_body(entry_path), encoding="utf-8")


def start_review_cycle(
    entry_path: Path,
    audit_path: Path,
    reason: str,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    if not audit_path.is_file():
        return ["cannot start a new cycle without an existing audit manifest"]
    old_bytes = audit_path.read_bytes()
    try:
        old = json.loads(old_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"cannot read existing audit manifest: {exc}"]
    if not isinstance(old, dict):
        return ["existing audit manifest must be a JSON object"]
    history = old.get("review_history", [])
    if not isinstance(history, list):
        return ["existing review_history must be a list"]
    old_cycle = old.get("current_cycle")
    if isinstance(old_cycle, dict) and _nonempty(old_cycle.get("cycle_id")):
        archived_cycle_id = str(old_cycle["cycle_id"])
    else:
        archived_cycle_id = "legacy-" + str(old.get("body_sha256", ""))[:12]
    relative_entry = entry_path.resolve().relative_to(repo_root.resolve())
    snapshot_relative = (
        Path("audits/history")
        / Path(*relative_entry.parts[1:]).with_suffix("")
        / f"{archived_cycle_id}.json"
    )
    snapshot_path = repo_root / snapshot_relative
    if snapshot_path.exists() and snapshot_path.read_bytes() != old_bytes:
        return [f"archive snapshot already exists with different bytes: {snapshot_relative}"]
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_bytes(old_bytes)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    record = {
        "cycle_id": archived_cycle_id,
        "body_sha256": old.get("body_sha256"),
        "snapshot_path": snapshot_relative.as_posix(),
        "snapshot_sha256": hashlib.sha256(old_bytes).hexdigest(),
        "archived_at": now,
    }
    new = build_manifest(entry_path, repo_root)
    new["review_history"] = [*history, record]
    cycle = new["current_cycle"]
    cycle["cycle_id"] = f"cycle-{len(history) + 2:03d}"
    cycle["parent_cycle_id"] = archived_cycle_id
    cycle["started_at"] = now
    cycle["change_reason"] = reason
    cycle["body_revisions"][0]["created_at"] = now
    new_revision_path = (
        Path("audits/runs")
        / Path(*relative_entry.parts[1:]).with_suffix("")
        / cycle["cycle_id"]
        / "revision-001.md"
    )
    cycle["body_revisions"][0]["snapshot_path"] = new_revision_path.as_posix()
    _write_latest_revision_snapshot(new, entry_path, repo_root)
    audit_path.write_text(
        json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return []


def add_body_revision(
    entry_path: Path,
    audit_path: Path,
    reason: str,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    if not audit_path.is_file():
        return ["cannot add a body revision without an existing audit manifest"]
    try:
        manifest = json.loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read existing audit manifest: {exc}"]
    if not isinstance(manifest, dict) or manifest.get("schema_version") != AUDIT_SCHEMA_VERSION:
        return [f"body revisions require schema_version {AUDIT_SCHEMA_VERSION}"]
    if _completed_manifest(manifest):
        return ["completed audits require start-cycle, not add-revision"]
    cycle = manifest.get("current_cycle")
    if not isinstance(cycle, dict) or not _nonempty(cycle.get("cycle_id")):
        return ["current_cycle with a cycle_id is required"]
    revisions = cycle.get("body_revisions")
    if not isinstance(revisions, list) or not revisions:
        return ["current_cycle.body_revisions must be a non-empty list"]
    current_hash = body_sha256(entry_path)
    latest = revisions[-1]
    if isinstance(latest, dict) and latest.get("body_sha256") == current_hash:
        return ["the current entry body is already the latest recorded revision"]
    revision_id = f"revision-{len(revisions) + 1:03d}"
    relative_entry = entry_path.resolve().relative_to(repo_root.resolve())
    snapshot_relative = (
        Path("audits/runs")
        / Path(*relative_entry.parts[1:]).with_suffix("")
        / str(cycle["cycle_id"])
        / f"{revision_id}.md"
    )
    revisions.append(
        {
            "revision_id": revision_id,
            "body_sha256": current_hash,
            "snapshot_path": snapshot_relative.as_posix(),
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "reason": reason,
        }
    )
    targets = extract_targets(entry_path)
    manifest["body_sha256"] = current_hash
    manifest["targets"] = targets
    manifest["relations"] = extract_relations(targets)
    _write_latest_revision_snapshot(manifest, entry_path, repo_root)
    audit_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return []


def seal_blind_review(audit_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read audit manifest {audit_path}: {exc}"]
    if not isinstance(manifest, dict) or manifest.get("schema_version") != AUDIT_SCHEMA_VERSION:
        return [f"blind review sealing requires schema_version {AUDIT_SCHEMA_VERSION}"]
    final = manifest.get("final_review")
    if not isinstance(final, dict):
        return ["final_review must be an object"]
    blind = final.get("blind_review")
    if not isinstance(blind, dict):
        return ["final_review.blind_review must be an object"]
    if blind.get("completed") is not True:
        errors.append("blind review must be completed before sealing")
    if blind.get("audit_visible") is not False:
        errors.append("blind review must record audit_visible as false before sealing")
    if blind.get("provisional_decision") not in {"pass", "reject"}:
        errors.append("blind review provisional_decision must be pass or reject")
    candidates = final.get("independent_candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append("blind review requires an independent inventory before sealing")
    if not isinstance(blind.get("article_findings"), list):
        errors.append("blind review article_findings must be a list")
    if errors:
        return errors
    blind["output_sha256"] = blind_review_sha256(final)
    audit_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return []


def _print_errors(errors: list[str]) -> int:
    if errors:
        print("Content audit validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Content audit validation passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and validate content audit manifests.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build")
    build.add_argument("entry", type=Path)
    build.add_argument("--output", type=Path)

    validate = subparsers.add_parser("validate")
    validate.add_argument("entry", type=Path)
    validate.add_argument("--audit", type=Path)

    changed = subparsers.add_parser("validate-changed")
    changed.add_argument("--base", required=True)
    changed.add_argument("--head", required=True)

    seal = subparsers.add_parser("seal-blind")
    seal.add_argument("audit", type=Path)

    start_cycle = subparsers.add_parser("start-cycle")
    start_cycle.add_argument("entry", type=Path)
    start_cycle.add_argument("--audit", type=Path)
    start_cycle.add_argument("--reason", required=True)

    add_revision = subparsers.add_parser("add-revision")
    add_revision.add_argument("entry", type=Path)
    add_revision.add_argument("--audit", type=Path)
    add_revision.add_argument("--reason", required=True)

    sync = subparsers.add_parser("validate-sync")
    sync.add_argument("entries", nargs="+", type=Path)

    subparsers.add_parser("validate-audited")
    args = parser.parse_args()

    if args.command == "build":
        entry_path = args.entry.resolve()
        output = args.output or audit_path_for_entry(entry_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        manifest = build_manifest(entry_path)
        _write_latest_revision_snapshot(manifest, entry_path, REPO_ROOT)
        output.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        try:
            display_path = output.relative_to(REPO_ROOT)
        except ValueError:
            display_path = output
        print(display_path)
        return 0
    if args.command == "validate":
        entry_path = args.entry.resolve()
        audit_path = args.audit or audit_path_for_entry(entry_path)
        return _print_errors(validate_manifest(entry_path, audit_path))
    if args.command == "validate-changed":
        return _print_errors(validate_changed(args.base, args.head))
    if args.command == "seal-blind":
        audit_path = args.audit.resolve()
        errors = seal_blind_review(audit_path)
        if errors:
            return _print_errors(errors)
        try:
            display_path = audit_path.relative_to(REPO_ROOT)
        except ValueError:
            display_path = audit_path
        print(f"Sealed blind review: {display_path}")
        return 0
    if args.command == "start-cycle":
        entry_path = args.entry.resolve()
        audit_path = args.audit.resolve() if args.audit else audit_path_for_entry(entry_path)
        return _print_errors(
            start_review_cycle(entry_path, audit_path, args.reason, REPO_ROOT)
        )
    if args.command == "add-revision":
        entry_path = args.entry.resolve()
        audit_path = args.audit.resolve() if args.audit else audit_path_for_entry(entry_path)
        return _print_errors(
            add_body_revision(entry_path, audit_path, args.reason, REPO_ROOT)
        )
    if args.command == "validate-sync":
        return _print_errors(validate_sync(args.entries, REPO_ROOT))
    return _print_errors(validate_all_audited())


if __name__ == "__main__":
    raise SystemExit(main())
