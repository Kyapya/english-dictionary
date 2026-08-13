from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCHEMA_VERSION = "content_audit_v1"
COLD_REVIEW_PROMPT_VERSION = "cold_review_prompt_v1"
FINAL_STATUSES = {"checked", "final"}
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


def build_manifest(entry_path: Path, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    relative = entry_path.resolve().relative_to(repo_root.resolve()).as_posix()
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "entry_path": relative,
        "body_sha256": body_sha256(entry_path),
        "targets": extract_targets(entry_path),
        "evidence": [],
        "normal_review": {
            "role": "normal_checker",
            "reviewer_id": "",
            "reviewed_at": "",
            "completed": False,
            "independent_candidates": [],
            "target_results": [],
        },
        "cold_review": {
            "role": "cold_reviewer",
            "reviewer_id": "",
            "reviewed_at": "",
            "prompt_version": COLD_REVIEW_PROMPT_VERSION,
            "completed": False,
            "summary": "",
            "findings": [],
        },
        "resolutions": [],
        "final_review": {
            "role": "final_adjudicator",
            "reviewer_id": "",
            "reviewed_at": "",
            "completed": False,
            "body_sha256": "",
            "decision": "pending",
            "target_results": [],
            "candidate_results": [],
            "finding_results": [],
            "blockers": [],
        },
    }


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


def validate_manifest(
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
    if manifest.get("schema_version") != AUDIT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {AUDIT_SCHEMA_VERSION}")
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
        if front.get("status") not in FINAL_STATUSES:
            continue
        audit_path = audit_path_for_entry(entry_path, repo_root)
        for error in validate_manifest(entry_path, audit_path, repo_root):
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
    return _print_errors(validate_all_audited())


if __name__ == "__main__":
    raise SystemExit(main())
