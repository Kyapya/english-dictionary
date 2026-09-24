"""Resume stage 2 from sealed evidence, never by impersonating a lost reviewer.

These receipts bind inputs and explain a context replacement; they do not prove
independent execution. The dispatcher must actually start a fresh review context.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

PROTOCOL = "sealed_stage1_replay_v1"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def _identity(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def replay_template(blind_record: dict, request_sha256: str) -> dict:
    return {
        "protocol": PROTOCOL,
        "previous_agent_id": blind_record.get("reviewer", {}).get("agent_id"),
        "blind_record_sha256": digest(blind_record),
        "stage2_request_sha256": request_sha256,
        "reason": None,
    }


def validate_replay(response: dict, blind_record: dict, request_sha256: str, *,
                    other_agent_ids: Iterable[str] = (),
                    repo_root: Path | None = None) -> list[str]:
    """Permit a genuine replacement only with a self-declared, bound receipt.

    The same handoff agent/model remains valid without a receipt. API reviews
    retain their existing isolated-call contract (this helper is handoff-only).
    """
    old = blind_record.get("reviewer", {})
    new = response.get("reviewer", {})
    if not isinstance(old, dict) or not isinstance(new, dict):
        return ["stage1 replay requires reviewer metadata for both stages"]
    receipt = response.get("stage1_replay")
    if new.get("mode") != "handoff":
        return [] if receipt is None else ["stage1 replay requires handoff reviewers"]
    old_id, new_id = _identity(old.get("agent_id")), _identity(new.get("agent_id"))
    old_model, new_model = _identity(old.get("declared_model")), _identity(new.get("declared_model"))
    if not all((old_id, new_id, old_model, new_model)):
        return ["stage1 replay requires both actual agent IDs and declared models"]
    if old_id == new_id and old_model == new_model and receipt is None:
        return []
    errors = []
    if old_id == new_id:
        errors.append("a replacement must use its own agent ID, not impersonate stage 1")
    others = {_identity(value) for value in other_agent_ids}
    if old_id in others or new_id in others:
        errors.append("both frame stages must be independent of the other checker passes")
    if not isinstance(receipt, dict):
        return [*errors, "replacement stage 2 requires a stage1_replay receipt"]
    expected = replay_template(blind_record, request_sha256)
    for key, value in expected.items():
        if key != "reason" and receipt.get(key) != value:
            errors.append(f"stage1_replay.{key} mismatch")
    if not isinstance(receipt.get("reason"), str) or not receipt["reason"].strip():
        errors.append("stage1_replay.reason must explain why the previous context is unavailable")
    if old.get("mode") != "handoff":
        errors.append("stage1 replay requires a preserved handoff stage 1")
    if repo_root is not None:
        import handoff_provenance
        errors.extend(handoff_provenance.validate(blind_record, repo_root, required=True))
    return errors
