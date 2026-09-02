from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPROVEMENT_DIR = REPO_ROOT / "process_improvement"
RECORDS_DIR = IMPROVEMENT_DIR / "records"
ACTIVE_PATH = IMPROVEMENT_DIR / "ACTIVE.md"
RETIREMENT_PATH = IMPROVEMENT_DIR / "retirement_state.json"

SCHEMA_VERSION = "project_process_improvement_v1"
ID_PATTERN = re.compile(r"PI-[0-9]{4}")
STATUSES = {"candidate", "trial", "active", "retired"}
CATEGORIES = {"quality", "efficiency", "reliability", "maintainability"}
SEVERITIES = {"low", "medium", "high", "critical"}
PHASES = {
    "planning",
    "generation",
    "normal_review",
    "cold_review_handoff",
    "cold_resolution",
    "final_review",
    "audit_mutation",
    "validation",
    "publication",
    "all",
}
VALIDATION_RESULTS = {"not_started", "pending", "pass", "fail"}
ENFORCEMENT_MODES = {
    "coordinator_playbook",
    "canonical_spec",
    "script_or_ci",
    "mixed",
}
MAX_RECORD_BYTES = 16_384
RETIREMENT_SCHEMA_VERSION = "process_retirement_v1"
DEFAULT_RETIREMENT_INTERVAL_WORDS = 10
ESCAPED_DEFECT_LINK_REQUIRED_FROM = "2026-08-27"

REQUIRED_KEYS = {
    "schema_version",
    "id",
    "title",
    "status",
    "category",
    "severity",
    "scope",
    "problem_pattern",
    "generalized_insight",
    "action_rule",
    "applicability",
    "exceptions",
    "generalization_gate",
    "evidence",
    "validation",
    "enforcement",
    "created_at",
    "updated_at",
}
OPTIONAL_KEYS = {"escaped_defect_ids"}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def _load_records(repo_root: Path = REPO_ROOT) -> tuple[list[dict[str, Any]], list[str]]:
    records_dir = repo_root / "process_improvement" / "records"
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    if not records_dir.is_dir():
        return [], [f"process-improvement records directory not found: {records_dir}"]

    for path in sorted(records_dir.glob("PI-*.json")):
        if path.stat().st_size > MAX_RECORD_BYTES:
            errors.append(
                f"{path.relative_to(repo_root)}: record exceeds {MAX_RECORD_BYTES} bytes"
            )
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(repo_root)}: invalid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path.relative_to(repo_root)}: top level must be an object")
            continue
        record["_path"] = path
        records.append(record)
    return records, errors


def _validate_string_list(
    value: Any, *, label: str, allowed: set[str] | None = None
) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, list) or not value:
        return [f"{label} must be a non-empty list"]
    for index, item in enumerate(value):
        if not _nonempty_string(item):
            errors.append(f"{label}[{index}] must be a non-empty string")
        elif allowed is not None and item not in allowed:
            errors.append(f"{label}[{index}] has unsupported value {item!r}")
    if len(value) != len(set(value)):
        errors.append(f"{label} contains duplicates")
    return errors


def _validate_record(record: dict[str, Any], repo_root: Path) -> list[str]:
    path = record.get("_path")
    label = path.relative_to(repo_root).as_posix() if isinstance(path, Path) else "record"
    errors: list[str] = []
    keys = set(record) - {"_path"}
    missing = sorted(REQUIRED_KEYS - keys)
    extra = sorted(keys - REQUIRED_KEYS - OPTIONAL_KEYS)
    if missing:
        errors.append(f"{label}: missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{label}: unsupported keys: {', '.join(extra)}")
    if missing:
        return errors

    escaped_ids = record.get("escaped_defect_ids")
    created_at = str(record.get("created_at", ""))
    if created_at >= ESCAPED_DEFECT_LINK_REQUIRED_FROM and escaped_ids is None:
        errors.append(
            f"{label}: escaped_defect_ids is required for records created on or after "
            f"{ESCAPED_DEFECT_LINK_REQUIRED_FROM}"
        )
    if escaped_ids is not None:
        errors.extend(
            _validate_string_list(
                escaped_ids, label=f"{label}: escaped_defect_ids"
            )
        )
        registry_path = repo_root / "audits" / "escaped_defects.json"
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registered = {
                str(item.get("id"))
                for item in registry.get("defects", [])
                if isinstance(item, dict) and _nonempty_string(item.get("id"))
            }
        except (OSError, json.JSONDecodeError, AttributeError):
            errors.append(
                f"{label}: cannot load escaped-defect registry {registry_path}"
            )
        else:
            for defect_id in escaped_ids if isinstance(escaped_ids, list) else []:
                if isinstance(defect_id, str) and defect_id not in registered:
                    errors.append(
                        f"{label}: escaped_defect_ids contains unknown id {defect_id}"
                    )

    record_id = record["id"]
    if not _nonempty_string(record_id) or not ID_PATTERN.fullmatch(record_id):
        errors.append(f"{label}: id must match PI-0000")
    elif isinstance(path, Path) and path.stem != record_id:
        errors.append(f"{label}: filename must match id {record_id}")

    for key, limit in (
        ("title", 120),
        ("problem_pattern", 1200),
        ("generalized_insight", 1200),
        ("action_rule", 1200),
        ("exceptions", 800),
        ("created_at", 40),
        ("updated_at", 40),
    ):
        if not _nonempty_string(record[key]):
            errors.append(f"{label}: {key} must be a non-empty string")
        elif len(record[key]) > limit:
            errors.append(f"{label}: {key} exceeds {limit} characters")

    if record["schema_version"] != SCHEMA_VERSION:
        errors.append(f"{label}: unsupported schema_version")
    if record["status"] not in STATUSES:
        errors.append(f"{label}: unsupported status {record['status']!r}")
    if record["category"] not in CATEGORIES:
        errors.append(f"{label}: unsupported category {record['category']!r}")
    if record["severity"] not in SEVERITIES:
        errors.append(f"{label}: unsupported severity {record['severity']!r}")
    if record["scope"] != "cross_entry_workflow":
        errors.append(
            f"{label}: scope must be 'cross_entry_workflow'; entry-specific notes do not belong here"
        )
    errors.extend(
        _validate_string_list(
            record["applicability"], label=f"{label}: applicability", allowed=PHASES
        )
    )

    gate = record["generalization_gate"]
    if not isinstance(gate, dict):
        errors.append(f"{label}: generalization_gate must be an object")
    else:
        expected = {"repeated_across_runs", "high_impact_single_run", "rationale"}
        if set(gate) != expected:
            errors.append(f"{label}: generalization_gate keys must be {sorted(expected)}")
        repeated = gate.get("repeated_across_runs")
        high_impact = gate.get("high_impact_single_run")
        if not isinstance(repeated, bool) or not isinstance(high_impact, bool):
            errors.append(f"{label}: generalization gate flags must be booleans")
        elif not (repeated or high_impact):
            errors.append(
                f"{label}: reject memo-like records; require recurrence or one high-impact event"
            )
        if not _nonempty_string(gate.get("rationale")):
            errors.append(f"{label}: generalization_gate.rationale is required")
        if high_impact and record["severity"] not in {"high", "critical"}:
            errors.append(
                f"{label}: high_impact_single_run requires high or critical severity"
            )

    evidence = record["evidence"]
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{label}: evidence must contain at least one observed run or PR")
        evidence = []
    elif len(evidence) > 10:
        errors.append(f"{label}: evidence is capped at 10 items; summarize repeated evidence")
    evidence_sources: list[str] = []
    for index, item in enumerate(evidence):
        item_label = f"{label}: evidence[{index}]"
        if not isinstance(item, dict) or set(item) != {"source", "observation"}:
            errors.append(f"{item_label} must contain only source and observation")
            continue
        for key in ("source", "observation"):
            if not _nonempty_string(item[key]):
                errors.append(f"{item_label}.{key} must be a non-empty string")
            elif len(item[key]) > 800:
                errors.append(f"{item_label}.{key} exceeds 800 characters")
        if _nonempty_string(item.get("source")):
            evidence_sources.append(item["source"])
    if (
        isinstance(gate, dict)
        and gate.get("repeated_across_runs") is True
        and len(set(evidence_sources)) < 2
    ):
        errors.append(f"{label}: repeated_across_runs requires two distinct evidence sources")

    validation = record["validation"]
    if not isinstance(validation, dict):
        errors.append(f"{label}: validation must be an object")
    else:
        expected = {"hypothesis", "measures", "window_runs", "observed_runs", "result", "notes"}
        if set(validation) != expected:
            errors.append(f"{label}: validation keys must be {sorted(expected)}")
        if not _nonempty_string(validation.get("hypothesis")):
            errors.append(f"{label}: validation.hypothesis is required")
        errors.extend(
            _validate_string_list(
                validation.get("measures"), label=f"{label}: validation.measures"
            )
        )
        window = validation.get("window_runs")
        observed = validation.get("observed_runs")
        if not isinstance(window, int) or isinstance(window, bool) or window < 1:
            errors.append(f"{label}: validation.window_runs must be a positive integer")
        if not isinstance(observed, int) or isinstance(observed, bool) or observed < 0:
            errors.append(f"{label}: validation.observed_runs must be a non-negative integer")
        if (
            isinstance(window, int)
            and isinstance(observed, int)
            and observed > window
        ):
            errors.append(f"{label}: validation.observed_runs cannot exceed window_runs")
        result = validation.get("result")
        if result not in VALIDATION_RESULTS:
            errors.append(f"{label}: unsupported validation result {result!r}")
        if not isinstance(validation.get("notes"), str):
            errors.append(f"{label}: validation.notes must be a string")
        if record["status"] == "trial" and result != "pending":
            errors.append(f"{label}: trial status requires validation.result=pending")
        if record["status"] == "active" and result != "pass":
            errors.append(f"{label}: active status requires validation.result=pass")
        if record["status"] == "retired" and result not in {"pass", "fail"}:
            errors.append(f"{label}: retired status requires a completed validation result")

    enforcement = record["enforcement"]
    if not isinstance(enforcement, dict):
        errors.append(f"{label}: enforcement must be an object")
    else:
        expected = {"mode", "surface_in_playbook", "refs"}
        if set(enforcement) != expected:
            errors.append(f"{label}: enforcement keys must be {sorted(expected)}")
        mode = enforcement.get("mode")
        surface = enforcement.get("surface_in_playbook")
        refs = enforcement.get("refs")
        if mode not in ENFORCEMENT_MODES:
            errors.append(f"{label}: unsupported enforcement mode {mode!r}")
        if not isinstance(surface, bool):
            errors.append(f"{label}: enforcement.surface_in_playbook must be boolean")
        if surface and mode not in {"coordinator_playbook", "mixed"}:
            errors.append(
                f"{label}: only coordinator or mixed rules may surface in ACTIVE.md"
            )
        if not isinstance(refs, list):
            errors.append(f"{label}: enforcement.refs must be a list")
            refs = []
        if record["status"] == "active" and not refs:
            errors.append(f"{label}: active records require an enforceable spec/script/test ref")
        if record["category"] == "quality" and record["status"] in {"trial", "active"}:
            if surface:
                errors.append(
                    f"{label}: quality rules may not surface in ACTIVE.md as a hidden content spec"
                )
            if mode == "coordinator_playbook":
                errors.append(
                    f"{label}: trial or active quality rules require canonical spec/script enforcement"
                )
            local_refs = [
                ref
                for ref in refs
                if isinstance(ref, str) and "://" not in ref and not ref.startswith("github:")
            ]
            if not any(ref.startswith(("prompts/", "scripts/")) for ref in local_refs):
                errors.append(
                    f"{label}: trial or active quality rules require a prompts/ or scripts/ ref"
                )
            if record["status"] == "active" and not any(
                ref.startswith("tests/") for ref in local_refs
            ):
                errors.append(f"{label}: active quality rules require a tests/ ref")
        for index, ref in enumerate(refs):
            if not _nonempty_string(ref):
                errors.append(f"{label}: enforcement.refs[{index}] must be a string")
                continue
            if "://" not in ref and not ref.startswith("github:"):
                ref_path = repo_root / ref.split("#", 1)[0]
                if not ref_path.exists():
                    errors.append(
                        f"{label}: enforcement ref does not exist: {ref.split('#', 1)[0]}"
                    )

    return errors


def render_active(records: list[dict[str, Any]]) -> str:
    surfaced = [
        record
        for record in records
        if record.get("status") in {"trial", "active"}
        and record.get("enforcement", {}).get("surface_in_playbook") is True
    ]
    surfaced.sort(key=lambda record: (record["status"] != "trial", record["id"]))
    lines = [
        "# Active project-process lessons",
        "",
        "<!-- Generated by scripts/process_improvement.py; do not edit directly. -->",
        "",
        "このファイルは、単語をまたいで再利用する運用知見のうち、現在の調整役が適用する規則だけを示す。",
        "記事内容の第二仕様として使わず、コールドレビュー担当と最終盲検担当には渡さない。",
        "内容品質の恒久ルールは、正式な生成・チェック・最終審査仕様または機械検証へ反映したものだけを有効とする。",
        "",
    ]
    if not surfaced:
        lines.extend(("現在、調整役が別途適用する規則はありません。", ""))
    for record in surfaced:
        status_label = "試行中" if record["status"] == "trial" else "有効"
        lines.extend(
            (
                f"## {record['id']} {record['title']}（{status_label}）",
                "",
                f"- 適用工程: {', '.join(record['applicability'])}",
                f"- 規則: {record['action_rule']}",
                f"- 例外・非対象: {record['exceptions']}",
                f"- 効果確認: {record['validation']['hypothesis']}",
                "",
            )
        )
    return "\n".join(lines)


def validate_registry(repo_root: Path = REPO_ROOT) -> list[str]:
    records, errors = _load_records(repo_root)
    for record in records:
        errors.extend(_validate_record(record, repo_root))

    ids = [record.get("id") for record in records if _nonempty_string(record.get("id"))]
    for record_id, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate process-improvement id: {record_id}")

    titles = [_normalized(record["title"]) for record in records if _nonempty_string(record.get("title"))]
    for title, count in Counter(titles).items():
        if count > 1:
            errors.append(f"duplicate process-improvement title: {title}")

    rules = [_normalized(record["action_rule"]) for record in records if _nonempty_string(record.get("action_rule"))]
    for rule, count in Counter(rules).items():
        if count > 1:
            errors.append(f"duplicate process-improvement action rule: {rule[:80]}")

    expected_active = render_active(records)
    active_path = repo_root / "process_improvement" / "ACTIVE.md"
    if not active_path.is_file():
        errors.append(f"active process-improvement playbook not found: {active_path}")
    elif active_path.read_text(encoding="utf-8") != expected_active:
        errors.append(
            "process_improvement/ACTIVE.md is stale; run "
            "python scripts/process_improvement.py render"
        )
    errors.extend(validate_retirement_state(repo_root))
    return errors


def _active_retirement_units(repo_root: Path) -> dict[str, dict[str, str]]:
    records, errors = _load_records(repo_root)
    if errors:
        raise ValueError("; ".join(errors))
    units: dict[str, dict[str, str]] = {}
    for record in records:
        if record.get("status") == "active":
            unit_id = f"rule:{record['id']}"
            units[unit_id] = {
                "id": unit_id,
                "kind": "operating_rule",
                "source": f"process_improvement/records/{record['id']}.json",
            }
    import check_passes

    router = check_passes.load_router(repo_root / "prompts" / "check_router_v6.md")
    for item in router.get("passes", []):
        unit_id = f"check_pass:{item['id']}"
        units[unit_id] = {
            "id": unit_id,
            "kind": "checker_pass",
            "source": str(item["specification"]),
        }
    return units


def initial_retirement_state(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    units = _active_retirement_units(repo_root)
    return {
        "schema_version": RETIREMENT_SCHEMA_VERSION,
        "review_interval_words": DEFAULT_RETIREMENT_INTERVAL_WORDS,
        "completed_words_seen": 0,
        "units": [
            {
                **units[unit_id],
                "status": "active",
                "last_reviewed_completed_words": 0,
                "last_window": None,
            }
            for unit_id in sorted(units)
        ],
    }


def _load_retirement_state(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    path = repo_root / "process_improvement" / "retirement_state.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read retirement state: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("retirement state must be a JSON object")
    return value


def validate_retirement_state(repo_root: Path = REPO_ROOT) -> list[str]:
    path = repo_root / "process_improvement" / "retirement_state.json"
    if not path.is_file():
        return ["process_improvement/retirement_state.json is required"]
    try:
        state = _load_retirement_state(repo_root)
        active_units = _active_retirement_units(repo_root)
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    if state.get("schema_version") != RETIREMENT_SCHEMA_VERSION:
        errors.append(f"retirement schema_version must be {RETIREMENT_SCHEMA_VERSION}")
    if state.get("review_interval_words") != DEFAULT_RETIREMENT_INTERVAL_WORDS:
        errors.append(
            f"retirement review_interval_words must be {DEFAULT_RETIREMENT_INTERVAL_WORDS}"
        )
    seen = state.get("completed_words_seen")
    if not isinstance(seen, int) or isinstance(seen, bool) or seen < 0:
        errors.append("retirement completed_words_seen must be non-negative")
    rows = state.get("units")
    if not isinstance(rows, list):
        return [*errors, "retirement units must be a list"]
    indexed: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not _nonempty_string(row.get("id")):
            errors.append(f"retirement units[{index}].id is required")
            continue
        unit_id = str(row["id"])
        if unit_id in indexed:
            errors.append(f"retirement units contains duplicate id {unit_id}")
            continue
        indexed[unit_id] = row
        if row.get("kind") not in {"operating_rule", "checker_pass"}:
            errors.append(f"retirement unit {unit_id}.kind is invalid")
        if row.get("status") not in {"active", "retired"}:
            errors.append(f"retirement unit {unit_id}.status is invalid")
        if not _nonempty_string(row.get("source")):
            errors.append(f"retirement unit {unit_id}.source is required")
        last = row.get("last_reviewed_completed_words")
        if not isinstance(last, int) or isinstance(last, bool) or last < 0:
            errors.append(
                f"retirement unit {unit_id}.last_reviewed_completed_words is invalid"
            )
    for unit_id, definition in active_units.items():
        row = indexed.get(unit_id)
        if row is None:
            errors.append(f"retirement state is missing active unit {unit_id}")
        elif row.get("source") != definition["source"]:
            errors.append(f"retirement unit {unit_id}.source is stale")
        elif row.get("status") == "retired" and row.get("kind") == "checker_pass":
            errors.append(
                f"retired checker pass {unit_id} remains in the active router; "
                "reassign its taxonomy before the next run"
            )
    for unit_id, row in indexed.items():
        if (
            row.get("kind") == "operating_rule"
            and row.get("status") == "active"
            and unit_id not in active_units
        ):
            errors.append(
                f"retirement unit {unit_id} is active but its PI record is not active"
            )
    return errors


def _completed_metric_runs(repo_root: Path) -> list[dict[str, Any]]:
    runs_root = repo_root / "audits" / "workflow_runs"
    latest_by_entry: dict[str, dict[str, Any]] = {}
    if not runs_root.is_dir():
        return []
    for path in sorted(runs_root.glob("*/*.json")):
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (
            not isinstance(manifest, dict)
            or manifest.get("status") != "completed"
            or not isinstance(manifest.get("metrics"), dict)
            or manifest["metrics"].get("schema_version") != "workflow_cost_v1"
        ):
            continue
        entry = str(manifest.get("entry_path", ""))
        completed_at = str(manifest["metrics"].get("completed_at", ""))
        current = latest_by_entry.get(entry)
        if current is None or completed_at > str(
            current.get("metrics", {}).get("completed_at", "")
        ):
            latest_by_entry[entry] = manifest
    return sorted(
        latest_by_entry.values(),
        key=lambda item: str(item.get("metrics", {}).get("completed_at", "")),
    )


def _unit_cost(run: dict[str, Any], unit: dict[str, Any]) -> tuple[int, int, float]:
    metrics = run.get("metrics", {})
    collection = (
        "checker_passes" if unit.get("kind") == "checker_pass" else "process_rules"
    )
    raw_id = str(unit["id"]).split(":", 1)[1]
    for row in metrics.get(collection, []):
        if isinstance(row, dict) and row.get("id") == raw_id and row.get("completed") is True:
            cost_bytes = int(row.get("instruction_bytes", 0)) + int(
                row.get("input_bytes", 0)
            )
            return (
                int(row.get("defects_detected", 0)),
                cost_bytes,
                float(row.get("duration_seconds", 0.0)),
            )
    return 0, 0, 0.0


def _retire_rule_record(unit_id: str, repo_root: Path, reviewed_runs: int) -> None:
    record_id = unit_id.split(":", 1)[1]
    path = repo_root / "process_improvement" / "records" / f"{record_id}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["status"] = "retired"
    validation = record["validation"]
    validation["observed_runs"] = min(
        int(validation["window_runs"]), max(int(validation["observed_runs"]), reviewed_runs)
    )
    validation["result"] = "fail"
    validation["notes"] = (
        f"10語ROI退役審査で検出欠陥0件。{reviewed_runs}語のwindow後に退役。"
    )
    record["updated_at"] = dt.date.today().isoformat()
    path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def retirement_review(
    repo_root: Path = REPO_ROOT, *, reviewed_at: str | None = None
) -> list[dict[str, Any]]:
    state = _load_retirement_state(repo_root)
    interval = int(state["review_interval_words"])
    runs = _completed_metric_runs(repo_root)
    total = len(runs)
    results: list[dict[str, Any]] = []
    for unit in state["units"]:
        if not isinstance(unit, dict) or unit.get("status") != "active":
            continue
        last = int(unit.get("last_reviewed_completed_words", 0))
        while total - last >= interval and unit.get("status") == "active":
            window = runs[last : last + interval]
            costs = [_unit_cost(run, unit) for run in window]
            defects = sum(item[0] for item in costs)
            cost_bytes = sum(item[1] for item in costs)
            duration = sum(item[2] for item in costs)
            decision = "retain" if defects > 0 else "retire"
            last += interval
            window_result = {
                "from_completed_word": last - interval + 1,
                "to_completed_word": last,
                "defects_detected": defects,
                "cost_bytes": cost_bytes,
                "duration_seconds": duration,
                "defects_per_kib": round(defects / (cost_bytes / 1024), 8)
                if cost_bytes
                else 0.0,
                "defects_per_second": round(defects / duration, 8)
                if duration
                else 0.0,
                "decision": decision,
                "reviewed_at": reviewed_at
                or dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            }
            unit["last_window"] = window_result
            unit["last_reviewed_completed_words"] = last
            if decision == "retire":
                unit["status"] = "retired"
                if unit.get("kind") == "operating_rule":
                    _retire_rule_record(str(unit["id"]), repo_root, interval)
            results.append({"id": unit["id"], **window_result})
    state["completed_words_seen"] = total
    path = repo_root / "process_improvement" / "retirement_state.json"
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _render(repo_root)
    return results


def _render(repo_root: Path) -> None:
    records, errors = _load_records(repo_root)
    if errors:
        raise ValueError("\n".join(errors))
    record_errors: list[str] = []
    for record in records:
        record_errors.extend(_validate_record(record, repo_root))
    if record_errors:
        raise ValueError("\n".join(record_errors))
    active_path = repo_root / "process_improvement" / "ACTIVE.md"
    active_path.write_text(render_active(records), encoding="utf-8")


def _summary(repo_root: Path) -> None:
    records, errors = _load_records(repo_root)
    if errors:
        raise ValueError("\n".join(errors))
    counts = Counter(record.get("status", "invalid") for record in records)
    print(
        "Project improvement knowledge: "
        + ", ".join(f"{status}={counts.get(status, 0)}" for status in sorted(STATUSES))
    )
    surfaced = [
        record
        for record in records
        if record.get("status") in {"trial", "active"}
        and record.get("enforcement", {}).get("surface_in_playbook") is True
    ]
    for record in sorted(surfaced, key=lambda item: item["id"]):
        print(f"- {record['id']} [{record['status']}]: {record['action_rule']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage cross-entry project improvement knowledge")
    parser.add_argument(
        "command", choices=("validate", "render", "summary", "retirement-review")
    )
    args = parser.parse_args()
    try:
        if args.command == "validate":
            errors = validate_registry()
            if errors:
                print("Project improvement validation failed:", file=sys.stderr)
                for error in errors:
                    print(f"- {error}", file=sys.stderr)
                return 1
            print("Project improvement validation passed.")
        elif args.command == "render":
            _render(REPO_ROOT)
            print(f"Rendered {ACTIVE_PATH.relative_to(REPO_ROOT)}")
        elif args.command == "summary":
            _summary(REPO_ROOT)
        else:
            results = retirement_review(REPO_ROOT)
            if not results:
                print(
                    f"Retirement review pending until each {DEFAULT_RETIREMENT_INTERVAL_WORDS}-word window closes."
                )
            else:
                print(json.dumps(results, ensure_ascii=False, indent=2))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
