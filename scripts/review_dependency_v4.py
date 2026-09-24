from __future__ import annotations

"""Content dependencies for compact reviews; historical seven-pass records stay immutable.

The document digest identifies the edition.  Area digests identify the meaning
and evidence actually inspected.  Neither a new timestamp nor a new full-body
hash is permission to rewrite a historical review receipt.
"""

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import content_audit
import workflow_revision

VERSION = "compact_review_v1"
AREAS = ("pronunciation", "etymology", "word_formation", "core_image", "usage_preamble")


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


def _sense_anchor(title: str) -> str:
    # Keep the label/meaning, not the ordinal. An editorial move must not
    # magically bind a different meaning to an old numerical target ID.
    return re.sub(r"^\s*\d+[.．、]?\s*", "", title).strip()


def _area(target: dict[str, Any]) -> str:
    title = str(target.get("sense") or "")
    if title:
        return "sense:" + digest(_sense_anchor(title))[:20]
    section = str(target.get("section") or "")
    for name, headings in (
        ("pronunciation", ("発音",)), ("etymology", ("語源",)),
        ("word_formation", ("語形成",)), ("core_image", ("コアイメージ",)),
    ):
        if any(heading in section for heading in headings):
            return name
    return "usage_preamble"


def _evidence_rows(inventory: dict[str, Any], targets: list[dict[str, Any]]) -> dict[str, Any]:
    gate = inventory.get("source_first_audit", {})
    if not isinstance(gate, dict):
        raise ValueError("source_first_audit is required")
    area_of_id = {str(target["id"]): _area(target) for target in targets}
    facts: dict[str, dict[str, Any]] = {}
    for source in gate.get("sources", []):
        if not isinstance(source, dict):
            continue
        for fact in source.get("facts", []):
            if isinstance(fact, dict) and fact.get("id"):
                facts[str(fact["id"])] = {
                    "id": fact["id"], "statement": fact.get("statement"),
                    "source_detail": fact.get("source_detail"),
                    "locator": source.get("locator"),
                    "source_type": source.get("source_type"),
                    "independence_group": source.get("independence_group"),
                }
    unions = {str(row["id"]): row for row in gate.get("source_union", [])
              if isinstance(row, dict) and row.get("id")}
    result: dict[str, list[Any]] = defaultdict(list)
    for claim in gate.get("claim_units", []):
        if not isinstance(claim, dict):
            continue
        linked = {area_of_id[str(target)] for target in claim.get("article_target_ids", [])
                  if str(target) in area_of_id}
        if not linked:
            # A dangling claim is never silently certified by a content key.
            result["unmatched_claims"].append(claim)
            continue
        fact_ids = {str(row.get("source_fact_id")) for row in claim.get("source_supports", [])
                    if isinstance(row, dict)}
        support = {
            "claim": {key: value for key, value in claim.items()
                      if key not in {"article_target_ids", "recorded_at", "line"}},
            "facts": [facts.get(fid, {"missing_fact": fid}) for fid in sorted(fact_ids)],
            "unions": [unions.get(str(uid), {"missing_union": uid})
                       for uid in claim.get("union_ids", [])],
        }
        for area in linked:
            result[area].append(support)
    return dict(result)


def snapshot(entry: Path, inventory: dict[str, Any], *, specification_sha256: str) -> dict[str, Any]:
    """Build semantic keys with stable duplicate discrimination and source content.

    Old ordinal target IDs are used only to resolve links within this snapshot.
    They are never themselves a reuse key. Unknown/ambiguous structures fail
    closed to a whole-content review.
    """
    text = entry.read_text(encoding="utf-8")
    targets = content_audit.extract_targets(entry)
    sections, unknown = workflow_revision._semantic_snapshot(text)
    topology = workflow_revision._sense_topology(sections)
    raw_areas: dict[str, list[Any]] = defaultdict(list)
    seen: dict[tuple[str, str, str], int] = defaultdict(int)
    for target in targets:
        area = _area(target)
        key = (area, str(target["kind"]), str(target["text_sha256"]))
        seen[key] += 1
        raw_areas[area].append({
            "stable_id": f"{area}:{target['kind']}:{target['text_sha256']}:{seen[key]}",
            "kind": target["kind"], "text": target["text"],
        })
    # Include content not extracted as a target. This catches changes to
    # explanatory prose and refuses to reuse an unknown heading by accident.
    for unit, lines in sections.items():
        for line in lines:
            owner, separator, value = line.partition("\0")
            if owner.startswith("@") and separator:
                area = "sense:" + digest(_sense_anchor(owner[1:]))[:20]
                normalized = value
            elif re.match(r"^\d+[.．、]?\s*【", line):
                area = "sense:" + digest(_sense_anchor(line))[:20]
                normalized = _sense_anchor(line)
            else:
                area = unit if unit in AREAS else "usage_preamble"
                normalized = line
            raw_areas[area].append({"unit": unit, "line": normalized})
    evidence = _evidence_rows(inventory, targets)
    topology_key = digest(topology)
    known_preamble = [line for line in unknown if line.startswith("【頻度表記】")]
    if known_preamble:
        raw_areas["usage_preamble"].extend({"unit": "frequency_legend", "line": line}
                                           for line in known_preamble)
    ambiguous = bool(set(unknown) - set(known_preamble) or evidence.get("unmatched_claims"))
    # A changed sense topology invalidates every area that relies on the map.
    area_keys = {area: digest({"version": VERSION, "spec": specification_sha256,
                               "content": rows, "evidence": evidence.get(area, []),
                               "topology": topology_key if area.startswith("sense:")
                               or area == "sense_content" else None})
                 for area, rows in raw_areas.items()}
    return {
        "workflow_contract_version": VERSION,
        "body_sha256": workflow_revision.body_sha256(text),
        "inventory_sha256": digest(inventory),
        "specification_sha256": specification_sha256,
        "topology_sha256": topology_key,
        "ambiguous": ambiguous,
        "areas": area_keys,
    }


def invalidated(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    if before.get("workflow_contract_version") != VERSION or after.get("workflow_contract_version") != VERSION:
        raise ValueError("compact workflow contract version mismatch")
    all_areas = set(before["areas"]) | set(after["areas"])
    broad = (before.get("ambiguous") or after.get("ambiguous") or
             before.get("topology_sha256") != after.get("topology_sha256"))
    changed = sorted(all_areas if broad else
                     (area for area in all_areas if before["areas"].get(area) != after["areas"].get(area)))
    return {"full_content_review": bool(broad), "invalidated_areas": changed,
            "reusable_areas": sorted(all_areas - set(changed)),
            "reason": "ambiguous_or_sense_topology" if broad else "content_dependency"}


def reuse_receipt(original: dict[str, Any], before: dict[str, Any],
                  after: dict[str, Any], area: str) -> dict[str, Any]:
    if area not in before["areas"] or before["areas"][area] != after["areas"].get(area):
        raise ValueError("review content dependency changed")
    if before.get("ambiguous") or after.get("ambiguous"):
        raise ValueError("ambiguous content requires renewed review")
    if not original.get("raw_response_sha256") or not original.get("raw_response_path"):
        raise ValueError("missing original raw review provenance")
    if original.get("area_keys", {}).get(area) != before["areas"][area]:
        raise ValueError("original review did not cover this content key")
    return {"schema_version": "compact_review_reuse_v1", "area": area,
            "original_raw_response_path": original["raw_response_path"],
            "original_raw_response_sha256": original["raw_response_sha256"],
            "original_body_sha256": before["body_sha256"],
            "current_body_sha256": after["body_sha256"],
            "unchanged_dependency_sha256": after["areas"][area]}
