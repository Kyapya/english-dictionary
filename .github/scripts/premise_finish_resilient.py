from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_passes  # noqa: E402
import review_liveness  # noqa: E402
import premise_finish_phase_a as phase  # noqa: E402


def _save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _secondary_cold(sec_dir: Path, base: str) -> dict:
    prompt_base = (REPO / "prompts/cold_review_prompt_v1.md").read_text(encoding="utf-8")
    prompt_base += "\n\nINPUT ENTRY BODY:\n" + phase.body_text()
    prompt_base += r'''

SECONDARY ZERO-FINDING CONFIRMATION. This is a fresh independent review. Do not assume the primary reviewer was correct. Return JSON only with summary and findings. Each finding must have id, location, severity high|medium|low, description, reason, suggested_direction, scope_anchors. Every scope anchor has id, exact_quote copied verbatim from the supplied entry, and location_hint. For each finding, reason must literally repeat at least one scope_anchors[].exact_quote. Findings must use item-specific reasoning. If there is no actual defect, return {"summary":"secondary review: no defect found","findings":[]}.
'''
    previous = ""
    for attempt in range(1, 4):
        prompt = prompt_base
        if previous:
            prompt += "\n\nPrevious machine validation errors. Correct these without weakening the independent review:\n" + previous
        value, model = phase.review(prompt)
        value["reviewer"] = phase.reviewer_meta(model, f"{base}:cold:attempt{attempt}")
        _save(sec_dir / f"cold_review.attempt{attempt}.json", value)
        errors = review_liveness.validate_reviewer(
            value.get("reviewer"), generation_model=phase.generation_model()
        )
        errors.extend(
            review_liveness.validate_finding_liveness(
                value, field="findings", label="secondary cold review findings"
            )
        )
        if not errors:
            return value
        previous = "; ".join(errors)
    raise RuntimeError("secondary cold review failed machine/liveness contract: " + previous)


def _secondary_attribution(sec_dir: Path, base: str) -> dict:
    request = phase.read_json(phase.CYCLE / "check_passes/example-attribution.request.json")
    _save(sec_dir / "example_attribution.request.json", request)
    prompt_base = r'''
You are a SECOND, fresh, independent blind example-attribution reviewer. Use ONLY the masked request below. Do not inspect the dictionary article, the primary review, any alignment key, or document ownership/order. Return one JSON object with keys summary, findings, blind_attribution_record. findings is [] if this independent classification reveals no attribution defect.

blind_attribution_record MUST contain an attributions array covering every opaque example_id exactly once. Each row MUST contain: example_id, classification (unique|ambiguous), candidate_sense_ids, discriminating_terms, rationale.

For a UNIQUE row:
- candidate_sense_ids has exactly one supplied sense_id.
- discriminating_terms has one or more short strings copied VERBATIM from that row's supplied English example or Japanese translation. Never invent or paraphrase these strings.
- rationale is item-specific and LITERALLY REPEATS at least one string from that same row's discriminating_terms (or the complete supplied English example).

For an AMBIGUOUS row:
- candidate_sense_ids has at least two supplied sense_ids.
- discriminating_terms MUST be [].
- rationale is item-specific and LITERALLY CONTAINS the complete supplied English example verbatim.

Across UNIQUE rows, choose genuinely item-specific evidence: the set of distinct discriminating_terms across the record must be larger than the number of supplied senses. Rationales must not be copy-pattern boilerplate after IDs are removed. Do not invent example IDs or sense IDs. Do not use withheld ownership/order. Return JSON only.

MASKED REQUEST:
'''
    previous = ""
    for attempt in range(1, 4):
        prompt = prompt_base + json.dumps(request, ensure_ascii=False, indent=2)
        if previous:
            prompt += "\n\nPrevious machine validation errors. Reclassify independently and correct only these contract defects:\n" + previous
        value, model = phase.review(prompt)
        record = value.get("blind_attribution_record")
        if not isinstance(record, dict):
            _save(sec_dir / f"example_attribution.attempt{attempt}.json", value)
            previous = "response lacks blind_attribution_record object"
            continue
        reviewer = phase.reviewer_meta(model, f"{base}:example-attribution:attempt{attempt}")
        record["schema_version"] = "example_attribution_blind_record_v1"
        record["pass_id"] = "example-attribution"
        record["input_body_sha256"] = str(request.get("input_body_sha256", ""))
        record["blind_request_sha256"] = phase.canonical_hash(request)
        record["recorded_at"] = datetime.now(timezone.utc).isoformat()
        record["reviewer"] = reviewer
        value["reviewer"] = reviewer
        value.setdefault("findings", [])
        value.setdefault("summary", "secondary independent example-attribution classification completed")
        _save(sec_dir / f"example_attribution.attempt{attempt}.json", value)
        errors = check_passes.validate_blind_attribution_record(
            record,
            request,
            generation_model=phase.generation_model(),
        )
        # validate_blind_attribution_record already invokes attribution liveness,
        # but keep the reviewer check explicit so the retry feedback is complete.
        errors.extend(
            review_liveness.validate_reviewer(
                reviewer, generation_model=phase.generation_model()
            )
        )
        if not errors:
            return value
        previous = "; ".join(dict.fromkeys(errors))
    raise RuntimeError("secondary attribution failed machine/liveness contract: " + previous)


def resilient_secondary(cold: dict) -> dict:
    if phase.primary_finding_count(cold=cold) != 0:
        return {}
    sec_dir = phase.CYCLE / "secondary_reviews_attempts"
    base = f"github-actions:{os.environ.get('GITHUB_RUN_ID', 'unknown')}:secondary"
    cold_value = _secondary_cold(sec_dir, base)
    attr_value = _secondary_attribution(sec_dir, base)
    secondary = {"cold_review": cold_value, "example_attribution": attr_value}
    _save(phase.CYCLE / "secondary_reviews.json", secondary)
    errors = review_liveness.zero_finding_run_errors(
        phase.read_json(phase.CYCLE / "pass_findings.json"),
        cold,
        {"article_findings": [], "independent_candidates": [{"disposition": "included"}]},
        secondary_reviews=secondary,
    )
    # The synthetic included candidate above only asks zero_finding_run_errors to
    # check reviewer-agent independence before final_blind exists. Full run
    # validation is repeated against the real final_blind before sealing.
    if errors:
        raise RuntimeError("secondary-agent independence check failed: " + "; ".join(errors))
    if cold_value.get("findings") or attr_value.get("findings"):
        raise RuntimeError("secondary zero-finding confirmation found a defect; revision cycle required")
    return secondary


def main() -> int:
    phase.run_secondary_zero_confirmations = resilient_secondary
    return phase.main()


if __name__ == "__main__":
    raise SystemExit(main())
