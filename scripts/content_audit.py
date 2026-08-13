from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCHEMA_VERSION = "content_audit_v2"
LEGACY_AUDIT_SCHEMA_VERSION = "content_audit_v1"
COLD_REVIEW_PROMPT_VERSION = "cold_review_prompt_v1"
FINAL_STATUSES = {"checked", "final"}
AUDITED_STATUSES = {"needs_review", "review_ready", "checked", "final"}
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


def audit_path_for_entry(entry_path: Path, repo_root: Path = REPO_ROOT) -> Path:
    relative = entry_path.resolve().relative_to(repo_root.resolve())
    if not relative.parts or relative.parts[0] != "entries":
        raise ValueError(f"entry must be under entries/: {entry_path}")
    return repo_root / "audits" / Path(*relative.parts[1:]).with_suffix(".json")


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
        if boundary is None:
            continue
        add(
            "sense_membership",
            [boundary["id"], target["id"]],
            "対象記述が所属語義の定義・品詞・意味範囲に実際に属し、別語義へ移すべき内容ではないことを確認する。",
        )

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
        grammar_patterns = [
            target for target in members if target["kind"] == "grammar_pattern"
        ]
        collocations = [target for target in members if target["kind"] == "collocation"]
        for definition in definitions:
            for usage_note in usage_notes:
                add(
                    "definition_usage_consistency",
                    [sense["id"], definition["id"], usage_note["id"]],
                    "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
                )
        for grammar_pattern in grammar_patterns:
            add(
                "pattern_example_coverage",
                [grammar_pattern["id"]]
                + [collocation["id"] for collocation in collocations],
                "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
            )

    core_images = [target for target in targets if target["kind"] == "core_image"]
    for core_image in core_images:
        for sense in senses:
            add(
                "core_sense_mapping",
                [core_image["id"], sense["id"]],
                "コアイメージの説明が対象語義を過度に単純化せず、歴史的説明と現代の語義説明を混同していないことを確認する。",
            )

    if senses:
        add(
            "article_learning_risk",
            [sense["id"] for sense in senses],
            "記事全体の語義構成、対比、訳語、限定表現から学習者が誤った一般化をしないことを横断確認する。",
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
    targets = extract_targets(entry_path)
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "entry_path": relative,
        "body_sha256": body_sha256(entry_path),
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

    if manifest.get("schema_version") != AUDIT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {AUDIT_SCHEMA_VERSION}")
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
        for key in (
            "kind",
            "location",
            "section",
            "sense",
            "text_sha256",
            "requires_evidence",
            "text",
        ):
            if actual_targets[target_id].get(key) != expected_targets[target_id].get(key):
                errors.append(f"target {target_id} has stale or invalid {key}")

    expected_relations = {
        item["id"]: item for item in extract_relations(list(expected_targets.values()))
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
        for key in (
            "kind",
            "target_ids",
            "description",
            "text_sha256",
            "requires_evidence",
        ):
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
        if execution.get("input_body_sha256") != expected_body_hash:
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
        if entry_status not in {"review_ready", "checked", "final"}:
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


def validate_changed(base: str, head: str, repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    changed = _git_changed_paths(base, head, repo_root)
    entry_paths = {
        path for path in changed if path.startswith("entries/") and path.endswith(".md")
    }
    audit_sources: dict[str, list[Path]] = {}
    for path in changed:
        if path.startswith("audits/") and path.endswith(".json"):
            relative = Path(path).relative_to("audits").with_suffix(".md")
            candidate_entry = (Path("entries") / relative).as_posix()
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
    return errors


def validate_all_audited(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    audits_dir = repo_root / "audits"
    if not audits_dir.is_dir():
        return []
    for audit_path in sorted(audits_dir.rglob("*.json")):
        relative = audit_path.relative_to(audits_dir).with_suffix(".md")
        entry_path = repo_root / "entries" / relative
        if not entry_path.is_file():
            errors.append(f"audit has no entry: {audit_path.relative_to(repo_root)}")
            continue
        for error in validate_manifest(entry_path, audit_path, repo_root):
            errors.append(f"{entry_path.relative_to(repo_root)}: {error}")
    return errors


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

    subparsers.add_parser("validate-audited")
    args = parser.parse_args()

    if args.command == "build":
        entry_path = args.entry.resolve()
        output = args.output or audit_path_for_entry(entry_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(build_manifest(entry_path), ensure_ascii=False, indent=2) + "\n",
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
    return _print_errors(validate_all_audited())


if __name__ == "__main__":
    raise SystemExit(main())
