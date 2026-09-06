from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import process_improvement


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "targeted_correction_v1"
REVIEW_SCOPE = "changed_hunks_and_local_context"
FINAL_STATUSES = {"checked", "final"}
CORRECTION_ROOT = Path("audits/targeted_corrections")


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _git_show(repo_root: Path, ref: str, path: str) -> str:
    return _git(repo_root, "show", f"{ref}:{path}")


def _changed_paths(repo_root: Path, base: str, head: str) -> list[str]:
    return [
        line.strip()
        for line in _git(repo_root, "diff", "--name-only", base, head, "--").splitlines()
        if line.strip()
    ]


def _entry_diff(repo_root: Path, base: str, head: str, entry_path: str) -> str:
    return _git(repo_root, "diff", "--unified=3", base, head, "--", entry_path)


def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    closing = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if closing is None:
        return {}, text
    front: dict[str, str] = {}
    for line in lines[1:closing]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        front[key.strip()] = value.strip().strip('"').strip("'")
    return front, "\n".join(lines[closing + 1 :])


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _body_sha256(text: str) -> str:
    return _sha256(_split_front_matter(text)[1])


def _is_checked(front: dict[str, str]) -> bool:
    return front.get("status") in FINAL_STATUSES and front.get("checked", "").lower() == "true"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _record_path(entry_path: str, created_at: str) -> Path:
    slug = Path(entry_path).stem
    stamp = created_at.replace("-", "").replace(":", "").replace("Z", "Z")
    return CORRECTION_ROOT / slug / f"{stamp}.json"


def build_record(
    *,
    entry_path: str,
    base_text: str,
    head_text: str,
    diff_text: str,
    user_request: str,
    reviewer: str,
    review_notes: str = "",
    pi_processing: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    base_front, _ = _split_front_matter(base_text)
    head_front, _ = _split_front_matter(head_text)
    if not _is_checked(base_front):
        raise ValueError("targeted correction requires a checked/final base entry")
    if not _is_checked(head_front):
        raise ValueError("targeted correction must keep the entry checked/final")
    if base_front.get("status") != head_front.get("status"):
        raise ValueError("targeted correction must not change final status")
    if not diff_text.strip():
        raise ValueError("targeted correction requires a non-empty entry diff")
    if not user_request.strip():
        raise ValueError("user_request is required")
    if not reviewer.strip():
        raise ValueError("reviewer is required")
    return {
        "schema_version": SCHEMA_VERSION,
        "entry_path": entry_path,
        "created_at": created_at or _timestamp(),
        "base_body_sha256": _body_sha256(base_text),
        "head_body_sha256": _body_sha256(head_text),
        "diff_sha256": _sha256(diff_text),
        "user_request": user_request.strip(),
        "review": {
            "scope": REVIEW_SCOPE,
            "reviewer": reviewer.strip(),
            "verdict": "pass",
            "notes": review_notes.strip(),
        },
        "pi_processing": pi_processing
        or {
            "status": "pending",
            "reason": "no coordinator learning_delta was supplied",
        },
    }


def validate_record(
    record: dict[str, Any],
    *,
    entry_path: str,
    base_text: str,
    head_text: str,
    diff_text: str,
) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if record.get("entry_path") != entry_path:
        errors.append("entry_path must match the changed entry")
    if not isinstance(record.get("created_at"), str) or not record["created_at"].strip():
        errors.append("created_at is required")
    if not isinstance(record.get("user_request"), str) or not record["user_request"].strip():
        errors.append("user_request is required")

    base_front, _ = _split_front_matter(base_text)
    head_front, _ = _split_front_matter(head_text)
    if not _is_checked(base_front):
        errors.append("base entry must already be checked/final")
    if not _is_checked(head_front):
        errors.append("head entry must remain checked/final")
    if base_front.get("status") != head_front.get("status"):
        errors.append("targeted correction must not change final status")

    expected_hashes = {
        "base_body_sha256": _body_sha256(base_text),
        "head_body_sha256": _body_sha256(head_text),
        "diff_sha256": _sha256(diff_text),
    }
    for key, expected in expected_hashes.items():
        if record.get(key) != expected:
            errors.append(f"{key} does not match the reviewed correction")

    review = record.get("review")
    if not isinstance(review, dict):
        errors.append("review must be an object")
    else:
        if review.get("scope") != REVIEW_SCOPE:
            errors.append(f"review.scope must be {REVIEW_SCOPE}")
        if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
            errors.append("review.reviewer is required")
        if review.get("verdict") != "pass":
            errors.append("review.verdict must be pass")
        if not isinstance(review.get("notes", ""), str):
            errors.append("review.notes must be a string")
    pi_processing = record.get("pi_processing")
    if not isinstance(pi_processing, dict):
        errors.append("pi_processing must be an object")
    elif pi_processing.get("status") not in process_improvement.PI_PROCESSING_STATUSES:
        errors.append("pi_processing.status is invalid")
    return errors


def validate_changed(base: str, head: str, repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    changed = _changed_paths(repo_root, base, head)
    entries = [path for path in changed if path.startswith("entries/") and path.endswith(".md")]
    records = [
        path
        for path in changed
        if path.startswith(f"{CORRECTION_ROOT.as_posix()}/") and path.endswith(".json")
    ]

    if len(entries) != 1:
        errors.append("targeted correction requires exactly one changed entry")
    if len(records) != 1:
        errors.append("targeted correction requires exactly one changed correction record")
    if errors:
        return errors

    entry_path = entries[0]
    record_path = records[0]
    allowed = {entry_path, record_path}
    try:
        base_text = _git_show(repo_root, base, entry_path)
    except subprocess.CalledProcessError:
        return ["targeted correction requires the entry to exist in the base revision"]
    try:
        head_text = _git_show(repo_root, head, entry_path)
        raw_record = _git_show(repo_root, head, record_path)
        record = json.loads(raw_record)
    except subprocess.CalledProcessError as exc:
        return [f"cannot read targeted correction content: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"correction record is not valid JSON: {exc}"]
    if not isinstance(record, dict):
        return ["correction record must be a JSON object"]

    pi_changed = {
        path for path in changed if path.startswith("process_improvement/")
    }
    pi_processing = record.get("pi_processing")
    pi_allowed: set[str] = set()
    if pi_changed and not isinstance(pi_processing, dict):
        errors.append("process-improvement changes require bound pi_processing data")
    elif pi_changed:
        status = pi_processing.get("status")
        event_id = str(pi_processing.get("event_id", ""))
        if status not in {"processed", "no_applicable"} or not event_id:
            errors.append(
                "process-improvement changes require a processed/no_applicable event receipt"
            )
        else:
            safe_event = re.sub(r"[^A-Za-z0-9_.-]+", "-", event_id)
            receipt_path = f"process_improvement/receipts/{safe_event}.json"
            pi_allowed.add(receipt_path)
            try:
                receipt = json.loads(_git_show(repo_root, head, receipt_path))
            except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
                errors.append(f"cannot read bound PI receipt: {exc}")
                receipt = {}
            for item in receipt.get("applied", []) if isinstance(receipt, dict) else []:
                if not isinstance(item, dict):
                    continue
                knowledge_id = str(item.get("knowledge_id", ""))
                version = item.get("version")
                action = item.get("action")
                if action in {"create", "revise"}:
                    pi_allowed.add(
                        f"process_improvement/records/{knowledge_id}.json"
                    )
                if action == "revise" and isinstance(version, int):
                    pi_allowed.add(
                        f"process_improvement/history/{knowledge_id}.v{version - 1}.json"
                    )
            for path in pi_changed:
                if not path.startswith("process_improvement/observations/"):
                    continue
                try:
                    observation = json.loads(_git_show(repo_root, head, path))
                except (subprocess.CalledProcessError, json.JSONDecodeError):
                    continue
                if isinstance(observation, dict) and observation.get("event_id") == event_id:
                    pi_allowed.add(path)
            pi_allowed.update(
                {
                    "process_improvement/index.json",
                    "process_improvement/ACTIVE.md",
                }
            )
            unexpected_pi = sorted(pi_changed - pi_allowed)
            if unexpected_pi:
                errors.append(
                    "targeted correction contains PI changes not bound to its receipt: "
                    + ", ".join(unexpected_pi)
                )
            registry_errors = process_improvement.validate_registry(repo_root)
            errors.extend(
                f"process-improvement registry: {error}"
                for error in registry_errors
            )
    extras = sorted(set(changed) - allowed - pi_changed)
    if extras:
        errors.append(
            "targeted correction PR may only change the entry, its correction record, "
            "and receipt-bound PI files: "
            + ", ".join(extras)
        )

    diff_text = _entry_diff(repo_root, base, head, entry_path)
    if not diff_text.strip():
        return ["targeted correction entry diff is empty"]
    errors.extend(
        validate_record(
            record,
            entry_path=entry_path,
            base_text=base_text,
            head_text=head_text,
            diff_text=diff_text,
        )
    )
    return errors


def command_record(args: argparse.Namespace) -> int:
    repo_root = REPO_ROOT
    entry = Path(args.entry)
    if entry.is_absolute():
        try:
            entry = entry.resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise ValueError("entry must be inside the repository") from exc
    entry_path = entry.as_posix()
    current_path = repo_root / entry
    if not current_path.is_file():
        raise ValueError(f"entry does not exist: {entry_path}")

    base_text = _git_show(repo_root, args.base, entry_path)
    head_text = current_path.read_text(encoding="utf-8")
    diff_text = _git(repo_root, "diff", "--unified=3", args.base, "--", entry_path)
    created_at = _timestamp()
    output = repo_root / _record_path(entry_path, created_at)
    pi_result: dict[str, Any] = {
        "status": "pending",
        "reason": "no coordinator learning_delta was supplied",
    }
    if args.learning_delta:
        try:
            container = json.loads(args.learning_delta.read_text(encoding="utf-8"))
            delta = (
                container.get("learning_delta")
                if isinstance(container, dict)
                else None
            )
            if not isinstance(delta, dict):
                delta = container if isinstance(container, dict) else None
            if not isinstance(delta, dict):
                raise ValueError("learning delta must be a JSON object")
            source = {
                "event_id": (
                    f"targeted:{Path(entry_path).stem}:"
                    f"{_sha256(diff_text)[:12]}"
                ),
                "knowledge_epoch": process_improvement.current_epoch(repo_root),
                "origin_kind": "targeted_correction",
                "source_ref": output.relative_to(repo_root).as_posix(),
                "observed_at": created_at,
                "content_sha256": _sha256(diff_text),
            }
            receipt = process_improvement.ingest_learning_delta(
                source, delta, repo_root=repo_root
            )
            pi_result = {
                "status": receipt.get("status", "save_error"),
                "event_id": receipt.get("event_id"),
            }
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            pi_result = {"status": "save_error", "reason": str(exc)}
    record = build_record(
        entry_path=entry_path,
        base_text=base_text,
        head_text=head_text,
        diff_text=diff_text,
        user_request=args.request,
        reviewer=args.reviewer,
        review_notes=args.review_notes,
        pi_processing=pi_result,
        created_at=created_at,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output.relative_to(repo_root).as_posix())
    return 0


def command_validate_changed(args: argparse.Namespace) -> int:
    errors = validate_changed(args.base, args.head)
    if errors:
        for error in errors:
            print(f"FAIL targeted-correction: {error}", file=sys.stderr)
        return 1
    print("PASS targeted-correction")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record and validate user-requested targeted corrections")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record")
    record.add_argument("--entry", required=True)
    record.add_argument("--base", required=True)
    record.add_argument("--request", required=True)
    record.add_argument("--reviewer", required=True)
    record.add_argument("--review-notes", default="")
    record.add_argument("--learning-delta", type=Path)
    record.set_defaults(func=command_record)

    changed = sub.add_parser("validate-changed")
    changed.add_argument("--base", required=True)
    changed.add_argument("--head", required=True)
    changed.set_defaults(func=command_validate_changed)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL targeted-correction: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
