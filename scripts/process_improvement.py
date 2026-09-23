from __future__ import annotations

"""Process-improvement knowledge registry, selection, and observation ledger.

The v2 registry deliberately keeps semantic adoption with the existing workflow
coordinator. This module validates the coordinator's structured decision,
selects applicable active knowledge, records immutable delivery/result facts, and
never promotes or retires knowledge from counters alone.
"""

import argparse
import contextlib
import datetime as dt
from file_lock import exclusive_lock
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPROVEMENT_DIR = REPO_ROOT / "process_improvement"
RECORDS_DIR = IMPROVEMENT_DIR / "records"
HISTORY_DIR = IMPROVEMENT_DIR / "history"
OBSERVATIONS_DIR = IMPROVEMENT_DIR / "observations"
RECEIPTS_DIR = IMPROVEMENT_DIR / "receipts"
EPOCH_PATH = IMPROVEMENT_DIR / "epoch.json"
INDEX_PATH = IMPROVEMENT_DIR / "index.json"
ACTIVE_PATH = IMPROVEMENT_DIR / "ACTIVE.md"

EPOCH_SCHEMA_VERSION = "process_improvement_epoch_v2"
RECORD_SCHEMA_VERSION = "process_improvement_knowledge_v2"
INDEX_SCHEMA_VERSION = "process_improvement_index_v2"
SNAPSHOT_SCHEMA_VERSION = "process_improvement_input_v2"
DELTA_SCHEMA_VERSION = "process_improvement_learning_delta_v2"
RECEIPT_SCHEMA_VERSION = "process_improvement_receipt_v2"
OBSERVATION_SCHEMA_VERSION = "process_improvement_observation_v2"

ID_PATTERN = re.compile(r"PI2-[A-F0-9]{12}")
SHA256_PATTERN = re.compile(r"[a-f0-9]{64}")
STATUSES = {"candidate", "active", "integrated", "retired"}
CATEGORIES = {"quality", "efficiency", "reliability", "maintainability"}
RECIPIENTS = {"generator", "coordinator"}
PHASES = {
    "planning",
    "generation",
    "revision",
    "pre_blind_resolution",
    "post_blind_resolution",
    "targeted_correction",
    "recovery",
    "publication",
    "all",
}
VALIDATION_DECISIONS = {"pending", "accepted"}
OUTCOMES = {
    "delivered",
    "action_confirmed",
    "no_opportunity",
    "recurred",
    "no_recurrence_observed",
    "burden",
    "unknown",
    "supporting_evidence",
}
PI_PROCESSING_STATUSES = {"processed", "no_applicable", "pending", "save_error"}
DEFAULT_MAX_ITEMS = 8
DEFAULT_MAX_BYTES = 8_192
MAX_RECORD_BYTES = 24_576
MAX_EVIDENCE_ITEMS = 20
GENERIC_ACTIONS = {
    "注意する",
    "正確に書く",
    "よく確認する",
    "be careful",
    "check carefully",
}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top level must be an object")
    return value


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_write(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )


@contextlib.contextmanager
def _registry_lock(repo_root: Path) -> Iterator[None]:
    lock_path = repo_root / "process_improvement" / ".registry.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_lock(lock_path):
        yield


def load_epoch(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    value = _json(repo_root / "process_improvement" / "epoch.json")
    if value.get("schema_version") != EPOCH_SCHEMA_VERSION:
        raise ValueError(f"epoch.schema_version must be {EPOCH_SCHEMA_VERSION}")
    if not _nonempty_string(value.get("knowledge_epoch")):
        raise ValueError("epoch.knowledge_epoch is required")
    return value


def current_epoch(repo_root: Path = REPO_ROOT) -> str:
    return str(load_epoch(repo_root)["knowledge_epoch"])


def _load_records(repo_root: Path = REPO_ROOT) -> tuple[list[dict[str, Any]], list[str]]:
    """Load only the current v2 registry; legacy records are never a fallback."""

    records_dir = repo_root / "process_improvement" / "records"
    if not records_dir.is_dir():
        return [], [f"process-improvement records directory not found: {records_dir}"]
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted(records_dir.glob("PI2-*.json")):
        if path.stat().st_size > MAX_RECORD_BYTES:
            errors.append(f"{_relative(path, repo_root)}: record exceeds {MAX_RECORD_BYTES} bytes")
            continue
        try:
            record = _json(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        record["_path"] = path
        records.append(record)
    return records, errors


def _validate_string_list(
    value: Any,
    *,
    label: str,
    allowed: set[str] | None = None,
    allow_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "a list" if allow_empty else "a non-empty list"
        return [f"{label} must be {qualifier}"]
    errors: list[str] = []
    for index, item in enumerate(value):
        if not _nonempty_string(item):
            errors.append(f"{label}[{index}] must be a non-empty string")
        elif allowed is not None and item not in allowed:
            errors.append(f"{label}[{index}] has unsupported value {item!r}")
    if len(value) != len(set(value)):
        errors.append(f"{label} contains duplicates")
    return errors


def _section_text(text: str, scope: str) -> str:
    if scope == "file":
        return text
    if not scope.startswith("section:"):
        raise ValueError("dependency scope must be file or section:<Markdown heading>")
    heading = scope.split(":", 1)[1].strip()
    if not heading:
        raise ValueError("dependency section heading is empty")
    lines = text.splitlines(keepends=True)
    start: int | None = None
    level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        if start is None and match.group(2) == heading:
            start = index
            level = len(match.group(1))
            continue
        if start is not None and len(match.group(1)) <= level:
            return "".join(lines[start:index])
    if start is None:
        raise ValueError(f"dependency section not found: {heading}")
    return "".join(lines[start:])


def dependency_sha256(repo_root: Path, path: str, scope: str = "file") -> str:
    target = repo_root / path
    if not target.is_file():
        raise ValueError(f"dependency path does not exist: {path}")
    return _sha256_text(_section_text(target.read_text(encoding="utf-8"), scope))


def dependency_status(
    record: dict[str, Any], repo_root: Path = REPO_ROOT
) -> tuple[bool, list[str]]:
    validation = record.get("validation")
    dependencies = (
        validation.get("specification_context", [])
        if isinstance(validation, dict)
        else []
    )
    reasons: list[str] = []
    for item in dependencies if isinstance(dependencies, list) else []:
        if not isinstance(item, dict):
            reasons.append("malformed specification dependency")
            continue
        path = str(item.get("path", ""))
        scope = str(item.get("scope", "file"))
        expected = str(item.get("sha256", ""))
        try:
            actual = dependency_sha256(repo_root, path, scope)
        except ValueError as exc:
            reasons.append(str(exc))
            continue
        if actual != expected:
            reasons.append(f"dependency changed: {path} ({scope})")
    return not reasons, reasons


def _validate_record(record: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    path = record.get("_path")
    label = _relative(path, repo_root) if isinstance(path, Path) else "record"
    required = {
        "schema_version",
        "knowledge_epoch",
        "id",
        "version",
        "title",
        "status",
        "category",
        "priority",
        "problem",
        "delivery",
        "evidence",
        "validation",
        "created_at",
        "updated_at",
    }
    optional = {"escaped_defect_ids", "integration", "lifecycle"}
    keys = set(record) - {"_path"}
    errors: list[str] = []
    missing = sorted(required - keys)
    extra = sorted(keys - required - optional)
    if missing:
        errors.append(f"{label}: missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{label}: unsupported keys: {', '.join(extra)}")
    if missing:
        return errors

    if record.get("schema_version") != RECORD_SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {RECORD_SCHEMA_VERSION}")
    try:
        epoch = current_epoch(repo_root)
    except ValueError as exc:
        errors.append(str(exc))
        epoch = ""
    if record.get("knowledge_epoch") != epoch:
        errors.append(f"{label}: record does not belong to current knowledge_epoch")
    record_id = record.get("id")
    if not _nonempty_string(record_id) or not ID_PATTERN.fullmatch(str(record_id)):
        errors.append(f"{label}: id must match PI2-<12 uppercase hex digits>")
    elif isinstance(path, Path) and path.stem != record_id:
        errors.append(f"{label}: filename must match id {record_id}")
    version = record.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        errors.append(f"{label}: version must be a positive integer")
    for key, limit in (("title", 140), ("created_at", 40), ("updated_at", 40)):
        if not _nonempty_string(record.get(key)):
            errors.append(f"{label}: {key} must be a non-empty string")
        elif len(str(record[key])) > limit:
            errors.append(f"{label}: {key} exceeds {limit} characters")
    if record.get("status") not in STATUSES:
        errors.append(f"{label}: unsupported status {record.get('status')!r}")
    if record.get("category") not in CATEGORIES:
        errors.append(f"{label}: unsupported category {record.get('category')!r}")
    priority = record.get("priority")
    if not isinstance(priority, int) or isinstance(priority, bool) or not 0 <= priority <= 100:
        errors.append(f"{label}: priority must be an integer from 0 to 100")

    problem = record.get("problem")
    problem_keys = {
        "observed",
        "action",
        "reusable_because",
        "conditions",
        "exclusions",
        "uncertainties",
    }
    if not isinstance(problem, dict) or set(problem) != problem_keys:
        errors.append(f"{label}: problem keys must be {sorted(problem_keys)}")
    else:
        for key, limit in (
            ("observed", 1600),
            ("action", 1600),
            ("reusable_because", 1200),
            ("exclusions", 1200),
            ("uncertainties", 1200),
        ):
            if not _nonempty_string(problem.get(key)):
                errors.append(f"{label}: problem.{key} must be a non-empty string")
            elif len(str(problem[key])) > limit:
                errors.append(f"{label}: problem.{key} exceeds {limit} characters")
        action = _normalized(str(problem.get("action", "")))
        if action in GENERIC_ACTIONS or len(action) < 12:
            errors.append(f"{label}: problem.action must state a concrete reusable action")
        if len(str(problem.get("reusable_because", "")).strip()) < 12:
            errors.append(f"{label}: problem.reusable_because is too vague")
        conditions = problem.get("conditions")
        if not isinstance(conditions, dict) or set(conditions) != {
            "required_tags",
            "excluded_tags",
        }:
            errors.append(
                f"{label}: problem.conditions must contain required_tags and excluded_tags"
            )
        else:
            errors.extend(
                _validate_string_list(
                    conditions.get("required_tags"),
                    label=f"{label}: problem.conditions.required_tags",
                    allow_empty=True,
                )
            )
            errors.extend(
                _validate_string_list(
                    conditions.get("excluded_tags"),
                    label=f"{label}: problem.conditions.excluded_tags",
                    allow_empty=True,
                )
            )
            required_tags = conditions.get("required_tags", [])
            if required_tags and all(str(tag).startswith("headword:") for tag in required_tags):
                errors.append(f"{label}: headword-specific conditions are not reusable knowledge")

    delivery = record.get("delivery")
    if not isinstance(delivery, dict) or set(delivery) != {"recipients", "phases"}:
        errors.append(f"{label}: delivery must contain recipients and phases")
    else:
        errors.extend(
            _validate_string_list(
                delivery.get("recipients"),
                label=f"{label}: delivery.recipients",
                allowed=RECIPIENTS,
            )
        )
        errors.extend(
            _validate_string_list(
                delivery.get("phases"),
                label=f"{label}: delivery.phases",
                allowed=PHASES,
            )
        )

    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{label}: evidence must contain an observed new-epoch event")
        evidence = []
    elif len(evidence) > MAX_EVIDENCE_ITEMS:
        errors.append(f"{label}: evidence exceeds {MAX_EVIDENCE_ITEMS} items")
    for index, item in enumerate(evidence):
        item_label = f"{label}: evidence[{index}]"
        required_evidence = {
            "event_id",
            "knowledge_epoch",
            "source_ref",
            "content_sha256",
            "observation",
        }
        if not isinstance(item, dict) or set(item) != required_evidence:
            errors.append(f"{item_label} keys must be {sorted(required_evidence)}")
            continue
        for key in ("event_id", "source_ref", "observation"):
            if not _nonempty_string(item.get(key)):
                errors.append(f"{item_label}.{key} is required")
        if item.get("knowledge_epoch") != epoch:
            errors.append(f"{item_label}.knowledge_epoch is not the current epoch")
        if not SHA256_PATTERN.fullmatch(str(item.get("content_sha256", ""))):
            errors.append(f"{item_label}.content_sha256 must be SHA-256")

    validation = record.get("validation")
    if not isinstance(validation, dict) or set(validation) != {
        "decision",
        "rationale",
        "evidence_refs",
        "specification_context",
    }:
        errors.append(
            f"{label}: validation must contain decision, rationale, evidence_refs, and specification_context"
        )
    else:
        decision = validation.get("decision")
        if decision not in VALIDATION_DECISIONS:
            errors.append(f"{label}: unsupported validation decision {decision!r}")
        if not _nonempty_string(validation.get("rationale")):
            errors.append(f"{label}: validation.rationale is required")
        errors.extend(
            _validate_string_list(
                validation.get("evidence_refs"),
                label=f"{label}: validation.evidence_refs",
                allow_empty=record.get("status") == "candidate",
            )
        )
        dependencies = validation.get("specification_context")
        if not isinstance(dependencies, list):
            errors.append(f"{label}: validation.specification_context must be a list")
            dependencies = []
        for index, item in enumerate(dependencies):
            dep_label = f"{label}: validation.specification_context[{index}]"
            if not isinstance(item, dict) or set(item) != {"path", "scope", "sha256"}:
                errors.append(f"{dep_label} must contain path, scope, and sha256")
                continue
            if not _nonempty_string(item.get("path")):
                errors.append(f"{dep_label}.path is required")
            if not _nonempty_string(item.get("scope")):
                errors.append(f"{dep_label}.scope is required")
            if not SHA256_PATTERN.fullmatch(str(item.get("sha256", ""))):
                errors.append(f"{dep_label}.sha256 must be SHA-256")
        if record.get("status") == "active":
            if decision != "accepted" or not validation.get("evidence_refs"):
                errors.append(
                    f"{label}: active knowledge requires an accepted coordinator decision and evidence"
                )
            if not dependencies:
                errors.append(f"{label}: active knowledge requires specification dependencies")

    escaped = record.get("escaped_defect_ids")
    if escaped is not None:
        errors.extend(
            _validate_string_list(
                escaped,
                label=f"{label}: escaped_defect_ids",
                allow_empty=True,
            )
        )
    if record.get("status") == "integrated":
        integration = record.get("integration")
        if not isinstance(integration, dict) or set(integration) != {
            "refs",
            "verification_refs",
            "reason",
        }:
            errors.append(f"{label}: integrated knowledge requires integration evidence")
        else:
            errors.extend(_validate_string_list(integration.get("refs"), label=f"{label}: integration.refs"))
            errors.extend(
                _validate_string_list(
                    integration.get("verification_refs"),
                    label=f"{label}: integration.verification_refs",
                )
            )
            if not _nonempty_string(integration.get("reason")):
                errors.append(f"{label}: integration.reason is required")
    if record.get("status") == "retired":
        lifecycle = record.get("lifecycle")
        if not isinstance(lifecycle, dict) or set(lifecycle) != {"reason", "evidence_refs"}:
            errors.append(f"{label}: retired knowledge requires a reason and evidence")
        else:
            if not _nonempty_string(lifecycle.get("reason")):
                errors.append(f"{label}: lifecycle.reason is required")
            errors.extend(
                _validate_string_list(
                    lifecycle.get("evidence_refs"), label=f"{label}: lifecycle.evidence_refs"
                )
            )
    return errors


def _record_without_path(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "_path"}


def render_index(records: list[dict[str, Any]], epoch: str) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: str(item.get("id", ""))):
        problem = record.get("problem", {})
        delivery = record.get("delivery", {})
        rows.append(
            {
                "id": record.get("id"),
                "version": record.get("version"),
                "title": record.get("title"),
                "status": record.get("status"),
                "category": record.get("category"),
                "priority": record.get("priority"),
                "recipients": delivery.get("recipients", []),
                "phases": delivery.get("phases", []),
                "required_tags": problem.get("conditions", {}).get("required_tags", []),
                "excluded_tags": problem.get("conditions", {}).get("excluded_tags", []),
                "record_sha256": _sha256_bytes(
                    _canonical_bytes(_record_without_path(record))
                ),
            }
        )
    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "knowledge_epoch": epoch,
        "records": rows,
    }


def _validate_index_row(row: dict[str, Any]) -> list[str]:
    required = {
        "id",
        "version",
        "title",
        "status",
        "category",
        "priority",
        "recipients",
        "phases",
        "required_tags",
        "excluded_tags",
        "record_sha256",
    }
    if set(row) != required:
        return [f"index row keys must be {sorted(required)}"]
    errors: list[str] = []
    if not ID_PATTERN.fullmatch(str(row.get("id", ""))):
        errors.append("index row id is invalid")
    if (
        not isinstance(row.get("version"), int)
        or isinstance(row.get("version"), bool)
        or row["version"] < 1
    ):
        errors.append("index row version is invalid")
    if not _nonempty_string(row.get("title")):
        errors.append("index row title is invalid")
    if row.get("status") not in STATUSES:
        errors.append("index row status is invalid")
    if row.get("category") not in CATEGORIES:
        errors.append("index row category is invalid")
    if (
        not isinstance(row.get("priority"), int)
        or isinstance(row.get("priority"), bool)
        or not 0 <= row["priority"] <= 100
    ):
        errors.append("index row priority is invalid")
    for key, allowed in (
        ("recipients", RECIPIENTS),
        ("phases", PHASES),
        ("required_tags", None),
        ("excluded_tags", None),
    ):
        errors.extend(
            _validate_string_list(
                row.get(key),
                label=f"index row {key}",
                allowed=allowed,
                allow_empty=key in {"required_tags", "excluded_tags"},
            )
        )
    if not SHA256_PATTERN.fullmatch(str(row.get("record_sha256", ""))):
        errors.append("index row record_sha256 is invalid")
    return errors


def render_active(records: list[dict[str, Any]], epoch: str | None = None) -> str:
    epoch = epoch or next(
        (
            str(record.get("knowledge_epoch"))
            for record in records
            if record.get("knowledge_epoch")
        ),
        "unknown",
    )
    active = [record for record in records if record.get("status") == "active"]
    lines = [
        "# Process-improvement v2 compatibility view",
        "",
        "<!-- Generated by scripts/process_improvement.py; do not edit directly. -->",
        "",
        f"Knowledge epoch: `{epoch}`",
        "",
        "この一覧は互換用の派生表示であり、生成入力の正本ではありません。実行時は対象条件に合う知見だけをrun内の入力スナップショットへ固定します。",
        "cold review、通常checker、final blindには渡しません。",
        "",
    ]
    if not active:
        lines.extend(("現在、使用可能な知見はありません。", ""))
    else:
        for record in sorted(
            active, key=lambda item: (-int(item["priority"]), item["id"])
        ):
            lines.extend(
                (
                    f"- `{record['id']}` v{record['version']}: {record['title']}",
                    f"  - 届け先: {', '.join(record['delivery']['recipients'])}",
                    f"  - 工程: {', '.join(record['delivery']['phases'])}",
                    "",
                )
            )
    return "\n".join(lines)


def _render(repo_root: Path = REPO_ROOT) -> None:
    records, errors = _load_records(repo_root)
    if errors:
        raise ValueError("; ".join(errors))
    epoch = current_epoch(repo_root)
    record_errors = [
        error
        for record in records
        for error in _validate_record(record, repo_root)
    ]
    if record_errors:
        raise ValueError("; ".join(record_errors))
    _atomic_json(
        repo_root / "process_improvement" / "index.json",
        render_index(records, epoch),
    )
    _atomic_write(
        repo_root / "process_improvement" / "ACTIVE.md",
        render_active(records, epoch).encode("utf-8"),
    )


def _validate_epoch(repo_root: Path) -> list[str]:
    try:
        epoch = load_epoch(repo_root)
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    migration = epoch.get("migration")
    expected = {
        "pre_migration_sha",
        "migrated_at",
        "legacy_paths",
        "legacy_ids",
        "reason",
    }
    if not isinstance(migration, dict) or set(migration) != expected:
        return [f"epoch.migration keys must be {sorted(expected)}"]
    if not re.fullmatch(
        r"[a-f0-9]{40}", str(migration.get("pre_migration_sha", ""))
    ):
        errors.append("epoch.migration.pre_migration_sha must be a full commit SHA")
    for key in ("migrated_at", "reason"):
        if not _nonempty_string(migration.get(key)):
            errors.append(f"epoch.migration.{key} is required")
    for key in ("legacy_paths", "legacy_ids"):
        errors.extend(
            _validate_string_list(migration.get(key), label=f"epoch.migration.{key}")
        )
    return errors


def _load_observations(
    repo_root: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    root = repo_root / "process_improvement" / "observations"
    if not root.is_dir():
        return [], [f"observation directory not found: {root}"]
    values: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted(root.glob("*.json")):
        try:
            value = _json(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        value["_path"] = path
        values.append(value)
    return values, errors


def _validate_observation(value: dict[str, Any], repo_root: Path) -> list[str]:
    path = value.get("_path")
    label = _relative(path, repo_root) if isinstance(path, Path) else "observation"
    required = {
        "schema_version",
        "knowledge_epoch",
        "observation_id",
        "knowledge_id",
        "knowledge_version",
        "event_id",
        "outcome",
        "source_ref",
        "observation",
        "recorded_at",
        "metrics",
    }
    keys = set(value) - {"_path"}
    errors: list[str] = []
    if keys != required:
        return [f"{label}: observation keys must be {sorted(required)}"]
    if value.get("schema_version") != OBSERVATION_SCHEMA_VERSION:
        errors.append(f"{label}: invalid schema_version")
    if value.get("knowledge_epoch") != current_epoch(repo_root):
        errors.append(f"{label}: observation is from another knowledge_epoch")
    if value.get("outcome") not in OUTCOMES:
        errors.append(f"{label}: unsupported outcome {value.get('outcome')!r}")
    if not ID_PATTERN.fullmatch(str(value.get("knowledge_id", ""))):
        errors.append(f"{label}: invalid knowledge_id")
    if (
        not isinstance(value.get("knowledge_version"), int)
        or value["knowledge_version"] < 1
    ):
        errors.append(f"{label}: invalid knowledge_version")
    for key in (
        "observation_id",
        "event_id",
        "source_ref",
        "observation",
        "recorded_at",
    ):
        if not _nonempty_string(value.get(key)):
            errors.append(f"{label}: {key} is required")
    metrics = value.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != {
        "input_bytes",
        "duration_seconds",
        "revision_count",
    }:
        errors.append(f"{label}: metrics must distinguish null from measured zero")
    else:
        for key in ("input_bytes", "duration_seconds", "revision_count"):
            metric = metrics.get(key)
            if metric is not None and (
                not isinstance(metric, (int, float))
                or isinstance(metric, bool)
                or metric < 0
            ):
                errors.append(f"{label}: metrics.{key} must be null or non-negative")
    return errors


def _validate_workflow_snapshots(
    repo_root: Path, known_versions: set[tuple[str, int]]
) -> list[str]:
    errors: list[str] = []
    runs_root = repo_root / "audits" / "workflow_runs"
    if not runs_root.is_dir():
        return errors
    epoch = current_epoch(repo_root)
    for manifest_path in sorted(runs_root.glob("*/*.json")):
        try:
            manifest = _json(manifest_path)
        except ValueError:
            # Other audit validators own malformed historical manifests.
            continue
        context = manifest.get("process_improvement")
        if not isinstance(context, dict) or context.get("schema_version") != "workflow_process_improvement_v2":
            continue
        if context.get("knowledge_epoch") != epoch:
            # A future epoch reset must not retroactively invalidate old runs.
            continue
        label = _relative(manifest_path, repo_root)
        for key in ("snapshots", "processing", "pending_events", "selection_errors"):
            expected_type = list if key != "processing" else dict
            if not isinstance(context.get(key), expected_type):
                errors.append(f"{label}: process_improvement.{key} has invalid type")
        snapshots = context.get("snapshots", [])
        if not isinstance(snapshots, list):
            continue
        seen_stages: set[str] = set()
        for index, snapshot in enumerate(snapshots):
            snapshot_label = f"{label}: process_improvement.snapshots[{index}]"
            if not isinstance(snapshot, dict):
                errors.append(f"{snapshot_label} must be an object")
                continue
            stage = str(snapshot.get("stage", ""))
            if stage in seen_stages:
                errors.append(f"{snapshot_label}: duplicate stage {stage}")
            seen_stages.add(stage)
            if snapshot.get("recipient") not in RECIPIENTS:
                errors.append(f"{snapshot_label}: invalid recipient")
            path_value = str(snapshot.get("snapshot_path", ""))
            path = repo_root / path_value
            companion = path.with_suffix(".json")
            if not path.is_file() or not companion.is_file():
                errors.append(f"{snapshot_label}: committed snapshot files are missing")
                continue
            content = path.read_bytes()
            if len(content) != snapshot.get("input_bytes"):
                errors.append(f"{snapshot_label}: input_bytes does not match actual input")
            if _sha256_bytes(content) != snapshot.get("input_sha256"):
                errors.append(f"{snapshot_label}: input_sha256 does not match actual input")
            try:
                companion_value = _json(companion)
            except ValueError as exc:
                errors.append(str(exc))
            else:
                comparable = {key: value for key, value in snapshot.items() if key != "stage"}
                if companion_value != comparable:
                    errors.append(f"{snapshot_label}: JSON companion differs from manifest snapshot")
            for item in snapshot.get("selected", []):
                if not isinstance(item, dict):
                    errors.append(f"{snapshot_label}: selected item must be an object")
                    continue
                target = (str(item.get("id", "")), int(item.get("version", 0)))
                if target not in known_versions:
                    errors.append(
                        f"{snapshot_label}: selected missing knowledge version {target[0]} v{target[1]}"
                    )
        processing = context.get("processing", {})
        if isinstance(processing, dict):
            for stage, result in processing.items():
                if not isinstance(result, dict) or result.get("status") not in PI_PROCESSING_STATUSES:
                    errors.append(f"{label}: invalid PI processing status for {stage}")
            completed_stages = manifest.get("orchestrator_state", {}).get(
                "completed_stages", []
            )
            if isinstance(completed_stages, list):
                for stage in (
                    "generation",
                    "pre_blind_resolution",
                    "post_blind_resolution",
                ):
                    if stage in completed_stages and stage not in processing:
                        errors.append(
                            f"{label}: completed {stage} has no PI processing result"
                        )
        orchestrator = manifest.get("orchestrator", {})
        if isinstance(orchestrator, dict):
            for stage in orchestrator.get("stages", []):
                if not isinstance(stage, dict):
                    continue
                name = stage.get("name")
                if name in {"checker_passes", "cold_review", "final_blind"} and stage.get(
                    "process_improvement_input_path"
                ):
                    errors.append(f"{label}: independent review stage {name} received PI input")
    return errors


def validate_registry(repo_root: Path = REPO_ROOT) -> list[str]:
    errors = _validate_epoch(repo_root)
    for directory in ("records", "history", "observations", "receipts"):
        if not (repo_root / "process_improvement" / directory).is_dir():
            errors.append(f"process_improvement/{directory} is required")
    records, load_errors = _load_records(repo_root)
    errors.extend(load_errors)
    records_root = repo_root / "process_improvement" / "records"
    if records_root.is_dir():
        for path in records_root.glob("*.json"):
            if not ID_PATTERN.fullmatch(path.stem):
                errors.append(
                    f"legacy or unsupported record must not remain in the current registry: {_relative(path, repo_root)}"
                )
    if (repo_root / "process_improvement" / "retirement_state.json").exists():
        errors.append(
            "legacy retirement_state.json must not control v2 knowledge or checker passes"
        )
    for record in records:
        errors.extend(_validate_record(record, repo_root))
    known_versions = {
        (str(record.get("id")), int(record.get("version", 0)))
        for record in records
        if isinstance(record.get("version"), int)
    }
    history_root = repo_root / "process_improvement" / "history"
    if history_root.is_dir():
        for path in sorted(history_root.glob("PI2-*.v*.json")):
            try:
                historical = _json(path)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            record_id = str(historical.get("id", ""))
            version = historical.get("version")
            expected_name = (
                f"{record_id}.v{version}.json"
                if isinstance(version, int)
                else ""
            )
            if path.name != expected_name:
                errors.append(
                    f"{_relative(path, repo_root)}: history filename does not match its ID/version"
                )
            errors.extend(_validate_record(historical, repo_root))
            if isinstance(version, int):
                known_versions.add((record_id, version))
    ids = [str(record.get("id")) for record in records]
    for record_id, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate process-improvement id: {record_id}")
    normalized_titles = [
        _normalized(str(record.get("title", "")))
        for record in records
        if _nonempty_string(record.get("title"))
    ]
    for value, count in Counter(normalized_titles).items():
        if count > 1:
            errors.append(f"duplicate process-improvement title: {value[:80]}")
    actions = [
        _normalized(str(record.get("problem", {}).get("action", "")))
        for record in records
        if isinstance(record.get("problem"), dict)
    ]
    for value, count in Counter(actions).items():
        if value and count > 1:
            errors.append(f"duplicate process-improvement action: {value[:80]}")

    if not errors:
        epoch = current_epoch(repo_root)
        expected_index = render_index(records, epoch)
        try:
            actual_index = _json(
                repo_root / "process_improvement" / "index.json"
            )
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if actual_index != expected_index:
                errors.append("process_improvement/index.json is stale; run render")
        active_path = repo_root / "process_improvement" / "ACTIVE.md"
        if (
            not active_path.is_file()
            or active_path.read_text(encoding="utf-8")
            != render_active(records, epoch)
        ):
            errors.append("process_improvement/ACTIVE.md is stale; run render")

    observations, observation_errors = _load_observations(repo_root)
    errors.extend(observation_errors)
    seen_observations: set[str] = set()
    for value in observations:
        errors.extend(_validate_observation(value, repo_root))
        observation_id = str(value.get("observation_id", ""))
        if observation_id in seen_observations:
            errors.append(
                f"duplicate process-improvement observation: {observation_id}"
            )
        seen_observations.add(observation_id)
        target = (
            str(value.get("knowledge_id", "")),
            int(value.get("knowledge_version", 0)),
        )
        if target not in known_versions:
            errors.append(
                f"observation {observation_id} references missing knowledge version {target[0]} v{target[1]}"
            )
    receipts_root = repo_root / "process_improvement" / "receipts"
    if receipts_root.is_dir():
        for path in sorted(receipts_root.glob("*.json")):
            try:
                receipt = _json(path)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
                errors.append(f"{_relative(path, repo_root)}: invalid receipt schema")
            if receipt.get("knowledge_epoch") != current_epoch(repo_root):
                errors.append(
                    f"{_relative(path, repo_root)}: receipt is from another epoch"
                )
            if receipt.get("status") not in {"processed", "no_applicable"}:
                errors.append(f"{_relative(path, repo_root)}: invalid receipt status")
            if not SHA256_PATTERN.fullmatch(str(receipt.get("payload_sha256", ""))):
                errors.append(f"{_relative(path, repo_root)}: invalid receipt payload hash")
    errors.extend(_validate_workflow_snapshots(repo_root, known_versions))
    return errors


def _new_id(source: dict[str, Any], record: dict[str, Any]) -> str:
    seed = {
        "event_id": source["event_id"],
        "title": _normalized(str(record.get("title", ""))),
        "action": _normalized(str(record.get("problem", {}).get("action", ""))),
    }
    return "PI2-" + _sha256_bytes(_canonical_bytes(seed))[:12].upper()


def _source_evidence(source: dict[str, Any], observation: str) -> dict[str, Any]:
    return {
        "event_id": source["event_id"],
        "knowledge_epoch": source["knowledge_epoch"],
        "source_ref": source["source_ref"],
        "content_sha256": source["content_sha256"],
        "observation": observation,
    }


def _validate_source(source: dict[str, Any], repo_root: Path) -> None:
    required = {
        "event_id",
        "knowledge_epoch",
        "origin_kind",
        "source_ref",
        "observed_at",
        "content_sha256",
    }
    if set(source) != required:
        raise ValueError(f"source keys must be {sorted(required)}")
    if source.get("knowledge_epoch") != current_epoch(repo_root):
        raise ValueError("old or unknown event epoch cannot create current knowledge")
    for key in ("event_id", "origin_kind", "source_ref", "observed_at"):
        if not _nonempty_string(source.get(key)):
            raise ValueError(f"source.{key} is required")
    if not SHA256_PATTERN.fullmatch(str(source.get("content_sha256", ""))):
        raise ValueError("source.content_sha256 must be SHA-256")


def _normalize_submission(
    submission: dict[str, Any], source: dict[str, Any]
) -> dict[str, Any]:
    record = dict(submission)
    record["schema_version"] = RECORD_SCHEMA_VERSION
    record["knowledge_epoch"] = source["knowledge_epoch"]
    record["id"] = str(record.get("id") or _new_id(source, record))
    record["version"] = int(record.get("version", 1))
    record["created_at"] = str(record.get("created_at") or source["observed_at"])
    record["updated_at"] = str(record.get("updated_at") or source["observed_at"])
    observation = str(record.pop("evidence_observation", "")).strip()
    if not observation:
        raise ValueError("create.record.evidence_observation is required")
    record["evidence"] = [_source_evidence(source, observation)]
    return record


def _write_new_record(record: dict[str, Any], repo_root: Path) -> str:
    record_id = str(record["id"])
    path = repo_root / "process_improvement" / "records" / f"{record_id}.json"
    comparable = _record_without_path(record)
    if path.exists():
        if _json(path) == comparable:
            return record_id
        raise ValueError(f"knowledge ID collision: {record_id}")
    record["_path"] = path
    errors = _validate_record(record, repo_root)
    record.pop("_path", None)
    if errors:
        raise ValueError("; ".join(errors))
    _atomic_json(path, record)
    return record_id


def _revise_record(
    item: dict[str, Any], source: dict[str, Any], repo_root: Path
) -> tuple[str, int]:
    record_id = str(item.get("knowledge_id", ""))
    expected_version = item.get("expected_version")
    path = repo_root / "process_improvement" / "records" / f"{record_id}.json"
    if not path.is_file():
        raise ValueError(f"cannot revise missing knowledge: {record_id}")
    current = _json(path)
    if current.get("version") != expected_version:
        raise ValueError(
            f"concurrent knowledge update detected for {record_id}: expected "
            f"v{expected_version}, found v{current.get('version')}"
        )
    replacement = item.get("record")
    if not isinstance(replacement, dict):
        raise ValueError("revise.record must be an object")
    revised = dict(replacement)
    revised.update(
        {
            "schema_version": RECORD_SCHEMA_VERSION,
            "knowledge_epoch": source["knowledge_epoch"],
            "id": record_id,
            "version": int(expected_version) + 1,
            "created_at": current["created_at"],
            "updated_at": source["observed_at"],
        }
    )
    observation = str(revised.pop("evidence_observation", "")).strip()
    if not observation:
        raise ValueError("revise.record.evidence_observation is required")
    revised["evidence"] = [
        *current.get("evidence", []),
        _source_evidence(source, observation),
    ]
    revised["_path"] = path
    errors = _validate_record(revised, repo_root)
    revised.pop("_path", None)
    if errors:
        raise ValueError("; ".join(errors))
    history = (
        repo_root
        / "process_improvement"
        / "history"
        / f"{record_id}.v{expected_version}.json"
    )
    if history.exists() and _json(history) != current:
        raise ValueError(f"history collision for {record_id} v{expected_version}")
    if not history.exists():
        _atomic_json(history, current)
    _atomic_json(path, revised)
    return record_id, int(revised["version"])


def _observation_value(
    *,
    observation_id: str,
    source: dict[str, Any],
    knowledge_id: str,
    knowledge_version: int,
    outcome: str,
    observation: str,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_metrics = metrics or {}
    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "knowledge_epoch": source["knowledge_epoch"],
        "observation_id": observation_id,
        "knowledge_id": knowledge_id,
        "knowledge_version": knowledge_version,
        "event_id": source["event_id"],
        "outcome": outcome,
        "source_ref": source["source_ref"],
        "observation": observation,
        "recorded_at": source["observed_at"],
        "metrics": {
            "input_bytes": raw_metrics.get("input_bytes"),
            "duration_seconds": raw_metrics.get("duration_seconds"),
            "revision_count": raw_metrics.get("revision_count"),
        },
    }


def _write_observation(value: dict[str, Any], repo_root: Path) -> str:
    observation_id = str(value["observation_id"])
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", observation_id)
    path = repo_root / "process_improvement" / "observations" / f"{safe}.json"
    if path.exists():
        if _json(path) == value:
            return observation_id
        raise ValueError(f"observation ID collision: {observation_id}")
    value["_path"] = path
    errors = _validate_observation(value, repo_root)
    value.pop("_path", None)
    if errors:
        raise ValueError("; ".join(errors))
    _atomic_json(path, value)
    return observation_id


def _knowledge_version_exists(
    knowledge_id: str, version: int, repo_root: Path
) -> bool:
    current = (
        repo_root
        / "process_improvement"
        / "records"
        / f"{knowledge_id}.json"
    )
    if current.is_file() and _json(current).get("version") == version:
        return True
    historical = (
        repo_root
        / "process_improvement"
        / "history"
        / f"{knowledge_id}.v{version}.json"
    )
    return historical.is_file() and _json(historical).get("version") == version


def ingest_learning_delta(
    source: dict[str, Any],
    delta: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Idempotently apply a coordinator-reviewed delta and return its receipt."""

    _validate_source(source, repo_root)
    if delta.get("schema_version") != DELTA_SCHEMA_VERSION:
        raise ValueError(
            f"learning_delta.schema_version must be {DELTA_SCHEMA_VERSION}"
        )
    if delta.get("reviewed") is not True:
        return {
            "status": "pending",
            "event_id": source["event_id"],
            "reason": "coordinator review is absent or incomplete",
        }
    items = delta.get("items")
    if not isinstance(items, list):
        raise ValueError("learning_delta.items must be a list")
    payload_hash = _sha256_bytes(
        _canonical_bytes({"source": source, "delta": delta})
    )
    receipt_path = (
        repo_root
        / "process_improvement"
        / "receipts"
        / f"{re.sub(r'[^A-Za-z0-9_.-]+', '-', str(source['event_id']))}.json"
    )
    with _registry_lock(repo_root):
        if receipt_path.exists():
            receipt = _json(receipt_path)
            if receipt.get("payload_sha256") != payload_hash:
                raise ValueError(
                    f"event ID collision with different payload: {source['event_id']}"
                )
            return receipt
        if not items:
            receipt = {
                "schema_version": RECEIPT_SCHEMA_VERSION,
                "knowledge_epoch": source["knowledge_epoch"],
                "event_id": source["event_id"],
                "payload_sha256": payload_hash,
                "status": "no_applicable",
                "applied": [],
                "recorded_at": source["observed_at"],
            }
            _atomic_json(receipt_path, receipt)
            return receipt

        applied: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(
                    f"learning_delta.items[{index}] must be an object"
                )
            action = item.get("action")
            if action == "create":
                submission = item.get("record")
                if not isinstance(submission, dict):
                    raise ValueError(
                        f"learning_delta.items[{index}].record must be an object"
                    )
                record = _normalize_submission(submission, source)
                record_id = _write_new_record(record, repo_root)
                applied.append(
                    {"action": "create", "knowledge_id": record_id, "version": 1}
                )
            elif action == "revise":
                record_id, version = _revise_record(item, source, repo_root)
                applied.append(
                    {
                        "action": "revise",
                        "knowledge_id": record_id,
                        "version": version,
                    }
                )
            elif action == "observe":
                record_id = str(item.get("knowledge_id", ""))
                version = item.get("knowledge_version")
                outcome = str(item.get("outcome", ""))
                if not ID_PATTERN.fullmatch(record_id):
                    raise ValueError(
                        f"learning_delta.items[{index}] has invalid knowledge_id"
                    )
                if not isinstance(version, int) or version < 1:
                    raise ValueError(
                        f"learning_delta.items[{index}] has invalid knowledge_version"
                    )
                if not _knowledge_version_exists(record_id, version, repo_root):
                    raise ValueError(
                        f"learning_delta.items[{index}] references missing "
                        f"knowledge version {record_id} v{version}"
                    )
                if outcome not in OUTCOMES - {"delivered"}:
                    raise ValueError(
                        f"learning_delta.items[{index}] has invalid outcome"
                    )
                observation = str(item.get("observation", "")).strip()
                if not observation:
                    raise ValueError(
                        f"learning_delta.items[{index}].observation is required"
                    )
                observation_id = (
                    f"{source['event_id']}:{index}:{record_id}:v{version}"
                )
                value = _observation_value(
                    observation_id=observation_id,
                    source=source,
                    knowledge_id=record_id,
                    knowledge_version=version,
                    outcome=outcome,
                    observation=observation,
                    metrics=(
                        item.get("metrics")
                        if isinstance(item.get("metrics"), dict)
                        else None
                    ),
                )
                _write_observation(value, repo_root)
                applied.append(
                    {
                        "action": "observe",
                        "knowledge_id": record_id,
                        "version": version,
                        "outcome": outcome,
                    }
                )
            else:
                raise ValueError(
                    f"learning_delta.items[{index}] has unsupported action {action!r}"
                )
        _render(repo_root)
        receipt = {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "knowledge_epoch": source["knowledge_epoch"],
            "event_id": source["event_id"],
            "payload_sha256": payload_hash,
            "status": "processed",
            "applied": applied,
            "recorded_at": source["observed_at"],
        }
        _atomic_json(receipt_path, receipt)
        return receipt


def _compact_item(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record["id"],
        "version": record["version"],
        "category": record["category"],
        "action": record["problem"]["action"],
        "conditions": record["problem"]["conditions"],
        "exclusions": record["problem"]["exclusions"],
    }


def _snapshot_markdown(
    *, epoch: str, recipient: str, phase: str, items: list[dict[str, Any]]
) -> str:
    lines = [
        "# Selected process-improvement knowledge",
        "",
        f"- knowledge_epoch: `{epoch}`",
        f"- recipient: `{recipient}`",
        f"- phase: `{phase}`",
        "",
        "現行の正式仕様と今回の明示指示が常に優先されます。この入力はレビュー基準や公開条件を変更しません。",
        "",
    ]
    if not items:
        lines.extend(("今回の条件に適用できる知見はありません。", ""))
    for item in items:
        excluded_tags = item["conditions"]["excluded_tags"]
        lines.extend(
            (
                f"## {item['id']} v{item['version']}",
                "",
                "- 適用条件: "
                + (", ".join(item["conditions"]["required_tags"]) or "追加条件なし"),
                "- 除外特徴: "
                + (", ".join(excluded_tags) or "追加の除外特徴なし"),
                f"- 実行すること: {item['action']}",
                f"- 適用しない条件: {item['exclusions']}",
                "",
            )
        )
    return "\n".join(lines)


def select_knowledge(
    *,
    recipient: str,
    phase: str,
    features: set[str] | None = None,
    max_items: int = DEFAULT_MAX_ITEMS,
    max_bytes: int = DEFAULT_MAX_BYTES,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    if recipient not in RECIPIENTS:
        raise ValueError(f"recipient must be one of {sorted(RECIPIENTS)}")
    if phase not in PHASES - {"all"}:
        raise ValueError(f"phase must be one of {sorted(PHASES - {'all'})}")
    if (
        not isinstance(max_items, int)
        or isinstance(max_items, bool)
        or max_items < 0
        or not isinstance(max_bytes, int)
        or isinstance(max_bytes, bool)
        or max_bytes < 1
    ):
        raise ValueError(
            "max_items must be a non-negative integer and max_bytes a positive integer"
        )
    epoch = current_epoch(repo_root)
    minimum_bytes = len(
        _snapshot_markdown(
            epoch=epoch, recipient=recipient, phase=phase, items=[]
        ).encode("utf-8")
    )
    if max_bytes < minimum_bytes:
        raise ValueError(
            f"max_bytes must be at least the empty input size ({minimum_bytes})"
        )
    selected_features = set(features or set())
    index = _json(repo_root / "process_improvement" / "index.json")
    if index.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise ValueError("process-improvement index schema is invalid")
    if index.get("knowledge_epoch") != current_epoch(repo_root):
        raise ValueError("process-improvement index belongs to another epoch")
    index_rows = index.get("records")
    if not isinstance(index_rows, list):
        raise ValueError("process-improvement index records must be a list")
    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    eligible: list[dict[str, Any]] = []
    for row in index_rows:
        if not isinstance(row, dict):
            raise ValueError("process-improvement index row must be an object")
        row_errors = _validate_index_row(row)
        if row_errors:
            raise ValueError("; ".join(row_errors))
        record_id = str(row.get("id", ""))
        status = row.get("status")
        if status != "active":
            skipped.append({"id": record_id, "reason": f"status:{status}"})
            continue
        if recipient not in row.get("recipients", []):
            skipped.append({"id": record_id, "reason": "recipient_mismatch"})
            continue
        phases = row.get("phases", [])
        if phase not in phases and "all" not in phases:
            skipped.append({"id": record_id, "reason": "phase_mismatch"})
            continue
        required = set(row.get("required_tags", []))
        excluded = set(row.get("excluded_tags", []))
        if not required.issubset(selected_features):
            skipped.append(
                {"id": record_id, "reason": "condition_unknown_or_mismatch"}
            )
            continue
        if excluded & selected_features:
            skipped.append({"id": record_id, "reason": "excluded_condition"})
            continue
        path = repo_root / "process_improvement" / "records" / f"{record_id}.json"
        try:
            record = _json(path)
        except ValueError as exc:
            skipped.append(
                {"id": record_id, "reason": "invalid", "details": [str(exc)]}
            )
            continue
        if _sha256_bytes(_canonical_bytes(record)) != row.get("record_sha256"):
            skipped.append(
                {
                    "id": record_id,
                    "reason": "invalid",
                    "details": ["record differs from the selected index revision"],
                }
            )
            continue
        record["_path"] = path
        record_errors = _validate_record(record, repo_root)
        if record_errors:
            skipped.append(
                {
                    "id": record.get("id"),
                    "reason": "invalid",
                    "details": record_errors,
                }
            )
            continue
        valid_dependency, reasons = dependency_status(record, repo_root)
        if not valid_dependency:
            skipped.append(
                {
                    "id": record["id"],
                    "reason": "needs_recheck",
                    "details": reasons,
                }
            )
            continue
        eligible.append(record)
    eligible.sort(
        key=lambda item: (-int(item["priority"]), item["id"], int(item["version"]))
    )
    for record in eligible:
        if len(selected) >= max_items:
            skipped.append({"id": record["id"], "reason": "item_limit"})
            continue
        candidate = [*selected, _compact_item(record)]
        candidate_bytes = len(
            _snapshot_markdown(
                epoch=epoch,
                recipient=recipient,
                phase=phase,
                items=candidate,
            ).encode("utf-8")
        )
        if candidate_bytes > max_bytes:
            skipped.append({"id": record["id"], "reason": "byte_limit"})
            continue
        selected = candidate
    rendered = _snapshot_markdown(
        epoch=epoch, recipient=recipient, phase=phase, items=selected
    )
    return {
        "knowledge_epoch": epoch,
        "recipient": recipient,
        "phase": phase,
        "features": sorted(selected_features),
        "limits": {"max_items": max_items, "max_bytes": max_bytes},
        "selected": selected,
        "skipped": skipped,
        "input_text": rendered,
        "input_bytes": len(rendered.encode("utf-8")),
        "input_sha256": _sha256_text(rendered),
    }


def create_input_snapshot(
    *,
    run_id: str,
    recipient: str,
    phase: str,
    output_path: Path,
    features: set[str] | None = None,
    max_items: int = DEFAULT_MAX_ITEMS,
    max_bytes: int = DEFAULT_MAX_BYTES,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    started = time.perf_counter()
    selection = select_knowledge(
        recipient=recipient,
        phase=phase,
        features=features,
        max_items=max_items,
        max_bytes=max_bytes,
        repo_root=repo_root,
    )
    markdown_path = output_path
    json_path = output_path.with_suffix(".json")
    input_text = str(selection.pop("input_text"))
    _atomic_write(markdown_path, input_text.encode("utf-8"))
    snapshot = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        **selection,
        "run_id": run_id,
        "created_at": _now(),
        "snapshot_path": _relative(markdown_path, repo_root),
        "machine_duration_seconds": round(time.perf_counter() - started, 6),
        "additional_llm_calls": 0,
    }
    _atomic_json(json_path, snapshot)
    return snapshot


def record_snapshot_delivery(
    snapshot: dict[str, Any], *, repo_root: Path = REPO_ROOT
) -> list[str]:
    """Record that a frozen snapshot reached its intended stage input.

    Snapshot construction and actual delivery are separate facts. This lets a
    coordinator refresh a not-yet-used snapshot without counting both versions.
    """

    source = {
        "event_id": (
            f"delivery:{snapshot['run_id']}:{snapshot['recipient']}:"
            f"{snapshot['phase']}:{snapshot['input_sha256'][:12]}"
        ),
        "knowledge_epoch": snapshot["knowledge_epoch"],
        "origin_kind": "workflow_delivery",
        "source_ref": snapshot["snapshot_path"],
        "observed_at": snapshot["created_at"],
        "content_sha256": snapshot["input_sha256"],
    }
    recorded: list[str] = []
    with _registry_lock(repo_root):
        for index, item in enumerate(snapshot["selected"]):
            knowledge_id = str(item["id"])
            knowledge_version = int(item["version"])
            if not _knowledge_version_exists(
                knowledge_id, knowledge_version, repo_root
            ):
                raise ValueError(
                    "snapshot references missing knowledge version "
                    f"{knowledge_id} v{knowledge_version}"
                )
            observation = _observation_value(
                observation_id=(
                    f"{source['event_id']}:{index}:{item['id']}:v{item['version']}"
                ),
                source=source,
                knowledge_id=knowledge_id,
                knowledge_version=knowledge_version,
                outcome="delivered",
                observation=(
                    "Included in the actual "
                    f"{snapshot['recipient']}/{snapshot['phase']} input snapshot."
                ),
                metrics={"input_bytes": snapshot["input_bytes"]},
            )
            recorded.append(_write_observation(observation, repo_root))
    return recorded


def aggregate_observations(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    observations, errors = _load_observations(repo_root)
    if errors:
        raise ValueError("; ".join(errors))
    aggregate: dict[tuple[str, int], Counter[str]] = defaultdict(Counter)
    measured: dict[tuple[str, int], dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for value in observations:
        key = (
            str(value.get("knowledge_id")),
            int(value.get("knowledge_version", 0)),
        )
        aggregate[key][str(value.get("outcome"))] += 1
        metrics = value.get("metrics", {})
        if isinstance(metrics, dict):
            for metric, raw in metrics.items():
                if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                    measured[key][metric].append(float(raw))
    rows = []
    for key in sorted(aggregate):
        rows.append(
            {
                "knowledge_id": key[0],
                "knowledge_version": key[1],
                "outcomes": dict(sorted(aggregate[key].items())),
                "measurements": {
                    name: {"count": len(values), "sum": sum(values)}
                    for name, values in sorted(measured[key].items())
                },
            }
        )
    return {"knowledge_epoch": current_epoch(repo_root), "by_version": rows}


def reconfirm_record(
    *,
    record_id: str,
    expected_version: int,
    evidence_ref: str,
    rationale: str,
    repo_root: Path = REPO_ROOT,
    observed_at: str | None = None,
) -> dict[str, Any]:
    if not evidence_ref.strip() or not rationale.strip():
        raise ValueError(
            "reconfirmation requires evidence_ref and rationale; hash-only refresh is forbidden"
        )
    path = repo_root / "process_improvement" / "records" / f"{record_id}.json"
    record = _json(path)
    if record.get("version") != expected_version:
        raise ValueError(
            "reconfirmation expected_version does not match current record"
        )
    revised = dict(record)
    revised["validation"] = dict(record["validation"])
    dependencies = []
    for item in record["validation"]["specification_context"]:
        dependencies.append(
            {
                "path": item["path"],
                "scope": item["scope"],
                "sha256": dependency_sha256(
                    repo_root, item["path"], item["scope"]
                ),
            }
        )
    revised["validation"]["specification_context"] = dependencies
    revised["validation"]["rationale"] = rationale.strip()
    revised["validation"]["evidence_refs"] = [
        *record["validation"]["evidence_refs"],
        evidence_ref.strip(),
    ]
    revised["evidence_observation"] = (
        "Coordinator rechecked the action against the changed dependency."
    )
    source_time = observed_at or _now()
    source = {
        "event_id": f"reconfirm:{record_id}:v{expected_version + 1}",
        "knowledge_epoch": current_epoch(repo_root),
        "origin_kind": "reconfirmation",
        "source_ref": evidence_ref.strip(),
        "observed_at": source_time,
        "content_sha256": _sha256_text(rationale.strip()),
    }
    delta = {
        "schema_version": DELTA_SCHEMA_VERSION,
        "reviewed": True,
        "items": [
            {
                "action": "revise",
                "knowledge_id": record_id,
                "expected_version": expected_version,
                "record": revised,
            }
        ],
    }
    return ingest_learning_delta(source, delta, repo_root=repo_root)


def migrate_v2(
    *,
    knowledge_epoch: str,
    pre_migration_sha: str,
    migrated_at: str,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Perform the explicit one-time reset; the same migration is a safe no-op."""

    if not re.fullmatch(r"[a-f0-9]{40}", pre_migration_sha):
        raise ValueError("pre_migration_sha must be a full commit SHA")
    improvement = repo_root / "process_improvement"
    records_dir = improvement / "records"
    epoch_path = improvement / "epoch.json"
    with _registry_lock(repo_root):
        for directory in (
            records_dir,
            improvement / "history",
            improvement / "observations",
            improvement / "receipts",
        ):
            directory.mkdir(parents=True, exist_ok=True)
        if epoch_path.exists():
            existing = load_epoch(repo_root)
            if existing.get("knowledge_epoch") != knowledge_epoch:
                raise ValueError(
                    "a different process-improvement knowledge epoch already exists"
                )
            # Finish a possibly interrupted migration without touching current
            # PI2 records accumulated after the epoch was established.
            for path in records_dir.glob("*.json"):
                if not ID_PATTERN.fullmatch(path.stem):
                    path.unlink()
            retirement = improvement / "retirement_state.json"
            if retirement.exists():
                retirement.unlink()
            _render(repo_root)
            return {"status": "no_op", "knowledge_epoch": knowledge_epoch}

        legacy_record_paths = sorted(records_dir.glob("*.json"))
        legacy_paths = [_relative(path, repo_root) for path in legacy_record_paths]
        legacy_ids = [path.stem for path in legacy_record_paths]
        for name in ("ACTIVE.md", "retirement_state.json", "index.json"):
            path = improvement / name
            if path.exists():
                legacy_paths.append(_relative(path, repo_root))
        metadata = {
            "schema_version": EPOCH_SCHEMA_VERSION,
            "knowledge_epoch": knowledge_epoch,
            "migration": {
                "pre_migration_sha": pre_migration_sha,
                "migrated_at": migrated_at,
                "legacy_paths": legacy_paths
                or ["process_improvement/records (empty)"],
                "legacy_ids": legacy_ids or ["none"],
                "reason": (
                    "Reset obsolete pre-v2 knowledge; retain history only through Git commits."
                ),
            },
        }
        # Persist the complete deletion plan first. If interruption follows,
        # rerunning this same migration completes cleanup while preserving PI2.
        _atomic_json(epoch_path, metadata)
        for path in legacy_record_paths:
            path.unlink()
        for name in ("ACTIVE.md", "retirement_state.json", "index.json"):
            path = improvement / name
            if path.exists():
                path.unlink()
        _render(repo_root)
        return {
            "status": "migrated",
            "knowledge_epoch": knowledge_epoch,
            "removed": legacy_paths,
        }


def _summary(repo_root: Path, *, as_json: bool = False) -> None:
    records, errors = _load_records(repo_root)
    if errors:
        raise ValueError("; ".join(errors))
    status_counts = Counter(
        str(record.get("status", "invalid")) for record in records
    )
    stale = []
    for record in records:
        valid, reasons = dependency_status(record, repo_root)
        if not valid:
            stale.append(
                {
                    "id": record["id"],
                    "version": record["version"],
                    "reasons": reasons,
                }
            )
    receipts = list(
        (repo_root / "process_improvement" / "receipts").glob("*.json")
    )
    receipt_counts = Counter(_json(path).get("status", "invalid") for path in receipts)
    payload = {
        "knowledge_epoch": current_epoch(repo_root),
        "records": {
            status: status_counts.get(status, 0) for status in sorted(STATUSES)
        },
        "processing": dict(sorted(receipt_counts.items())),
        "needs_recheck": stale,
        "observations": aggregate_observations(repo_root)["by_version"],
    }
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"Knowledge epoch: {payload['knowledge_epoch']}")
    print(
        "Records: "
        + ", ".join(
            f"{key}={value}" for key, value in payload["records"].items()
        )
    )
    print(
        "Processing: "
        + (
            ", ".join(
                f"{key}={value}" for key, value in payload["processing"].items()
            )
            or "none"
        )
    )
    print(f"Needs recheck: {len(stale)}")


def _cli_source(path: Path, repo_root: Path) -> dict[str, Any]:
    value = _json(path)
    if "source" in value and isinstance(value["source"], dict):
        return value["source"]
    relative = _relative(path, repo_root)
    content = path.read_bytes()
    return {
        "event_id": f"file:{relative}:{_sha256_bytes(content)[:12]}",
        "knowledge_epoch": current_epoch(repo_root),
        "origin_kind": "file",
        "source_ref": relative,
        "observed_at": _now(),
        "content_sha256": _sha256_bytes(content),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage process-improvement v2 knowledge"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("render")
    summary = sub.add_parser("summary")
    summary.add_argument("--json", action="store_true")
    select = sub.add_parser("select")
    select.add_argument(
        "--recipient", required=True, choices=sorted(RECIPIENTS)
    )
    select.add_argument(
        "--phase", required=True, choices=sorted(PHASES - {"all"})
    )
    select.add_argument("--run-id", required=True)
    select.add_argument("--feature", action="append", default=[])
    select.add_argument("--output", type=Path, required=True)
    select.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS)
    select.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    ingest = sub.add_parser("ingest")
    ingest.add_argument("--source", type=Path, required=True)
    ingest.add_argument("--delta", type=Path, required=True)
    reconfirm = sub.add_parser("reconfirm")
    reconfirm.add_argument("--record-id", required=True)
    reconfirm.add_argument("--expected-version", type=int, required=True)
    reconfirm.add_argument("--evidence-ref", required=True)
    reconfirm.add_argument("--rationale", required=True)
    migrate = sub.add_parser("migrate-v2")
    migrate.add_argument("--knowledge-epoch", required=True)
    migrate.add_argument("--pre-migration-sha", required=True)
    migrate.add_argument("--migrated-at", default="")
    sub.add_parser("retirement-review")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate":
            errors = validate_registry()
            if errors:
                print("Process-improvement validation failed:", file=sys.stderr)
                for error in errors:
                    print(f"- {error}", file=sys.stderr)
                return 1
            print("Process-improvement v2 validation passed.")
        elif args.command == "render":
            with _registry_lock(REPO_ROOT):
                _render(REPO_ROOT)
            print("Rendered process_improvement/index.json and ACTIVE.md")
        elif args.command == "summary":
            _summary(REPO_ROOT, as_json=args.json)
        elif args.command == "select":
            snapshot = create_input_snapshot(
                run_id=args.run_id,
                recipient=args.recipient,
                phase=args.phase,
                output_path=args.output,
                features=set(args.feature),
                max_items=args.max_items,
                max_bytes=args.max_bytes,
            )
            print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        elif args.command == "ingest":
            source = _cli_source(args.source, REPO_ROOT)
            delta_container = _json(args.delta)
            delta = delta_container.get("learning_delta", delta_container)
            if not isinstance(delta, dict):
                raise ValueError("delta must be a JSON object")
            print(
                json.dumps(
                    ingest_learning_delta(source, delta),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "reconfirm":
            print(
                json.dumps(
                    reconfirm_record(
                        record_id=args.record_id,
                        expected_version=args.expected_version,
                        evidence_ref=args.evidence_ref,
                        rationale=args.rationale,
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "migrate-v2":
            print(
                json.dumps(
                    migrate_v2(
                        knowledge_epoch=args.knowledge_epoch,
                        pre_migration_sha=args.pre_migration_sha,
                        migrated_at=args.migrated_at or _now(),
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(
                "retirement-review was removed in process-improvement v2; "
                "no knowledge or checker state was changed.",
                file=sys.stderr,
            )
            return 2
    except (OSError, ValueError) as exc:
        print(f"FAIL process-improvement: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
