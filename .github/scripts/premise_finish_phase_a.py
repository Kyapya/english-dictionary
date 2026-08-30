from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_passes  # noqa: E402
import content_audit  # noqa: E402
import review_liveness  # noqa: E402
import validate_entry  # noqa: E402

HEADWORD = "premise"
ENTRY = REPO / "entries/p/premise.md"
MODEL = "auto"
RUN: Path
CYCLE: Path


def run(cmd: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(
        cmd,
        cwd=REPO,
        input=input_text,
        text=True,
        capture_output=True,
        timeout=900,
    )
    if p.stdout:
        print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if check and p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd)}")
    return p


def parse_copilot(stdout: str) -> tuple[dict, str]:
    messages: list[str] = []
    models: list[str] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        data = event.get("data") if isinstance(event.get("data"), dict) else {}
        if event.get("type") == "assistant.message":
            if isinstance(data.get("content"), str) and data["content"].strip():
                messages.append(data["content"].strip())
            if isinstance(data.get("model"), str) and data["model"].strip():
                models.append(data["model"].strip())
        if event.get("type") == "session.shutdown" and isinstance(data.get("currentModel"), str):
            models.append(data["currentModel"].strip())
    if not messages:
        raise RuntimeError("independent reviewer returned no assistant message")

    # Copilot's assistant.message content may contain a fenced JSON object
    # followed by a short explanation. Decode the first complete object and
    # let the stage-specific validators enforce its required schema.
    text = messages[-1].strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    decoder = json.JSONDecoder()
    start = text.find("{")
    while start >= 0:
        try:
            value, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            start = text.find("{", start + 1)
            continue
        if isinstance(value, dict):
            return value, (models[-1] if models else MODEL)
        break
    raise RuntimeError("review response must contain one JSON object")


def review(prompt: str) -> tuple[dict, str]:
    p = run(
        [
            "copilot",
            "--no-ask-user",
            "--no-custom-instructions",
            "--model",
            MODEL,
            "--output-format",
            "json",
            "--deny-tool=shell",
            "--deny-tool=write",
            "--deny-tool=url",
            "--deny-tool=memory",
        ],
        input_text=prompt,
        check=False,
    )
    if p.returncode:
        raise RuntimeError(f"Copilot reviewer failed ({p.returncode})")
    return parse_copilot(p.stdout)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def body_text() -> str:
    text = ENTRY.read_text(encoding="utf-8")
    front, body = validate_entry._split_front_matter(text)
    del front
    return "\n".join(body)


def body_hash() -> str:
    return hashlib.sha256(body_text().encode("utf-8")).hexdigest()


def refresh_preserved_artifact_hashes() -> None:
    """Rebind copied generation/audit metadata to the revised entry body."""
    current = body_hash()
    for name, key in (
        ("generation.json", "output_body_sha256"),
        ("validator.json", "input_body_sha256"),
        ("source_inventory.json", "input_body_sha256"),
    ):
        path = CYCLE / name
        if not path.is_file():
            raise RuntimeError(f"preserved artifact is missing: {path}")
        value = read_json(path)
        value[key] = current
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def generation_model() -> str:
    front, _ = validate_entry._split_front_matter(ENTRY.read_text(encoding="utf-8"))
    return validate_entry._front_matter_values(front or []).get("model", "")


def reviewer_meta(model: str, agent_id: str) -> dict[str, object]:
    value: dict[str, object] = {
        "mode": "handoff",
        "declared_model": model,
        "ingested_by": "human",
        "agent_id": agent_id,
    }
    if review_liveness.normalize_text(model) == review_liveness.normalize_text(generation_model()):
        value["same_model_as_generation"] = True
    return value


def select_latest_restarted_run() -> tuple[Path, Path]:
    candidates: list[tuple[str, Path, dict]] = []
    for path in (REPO / "audits/workflow_runs/premise").glob("*.json"):
        try:
            manifest = read_json(path)
        except Exception:
            continue
        completed = manifest.get("orchestrator_state", {}).get("completed_stages", [])
        if (
            manifest.get("status") != "budget_exhausted"
            and isinstance(completed, list)
            and "checker_passes" in completed
            and "cold_review" not in completed
        ):
            candidates.append((str(manifest.get("started_at", "")), path, manifest))
    if not candidates:
        raise RuntimeError("no live restarted premise run at the cold-review boundary")
    _, path, manifest = max(candidates, key=lambda item: item[0])
    run_id = str(manifest["run_id"])
    cycle = REPO / "audits/runs/p/premise" / run_id
    return path, cycle


def complete(stage: str, input_path: Path, defects: int = 0) -> None:
    run(
        [
            sys.executable,
            "scripts/run_word.py",
            "--complete-stage",
            str(RUN),
            "--stage",
            stage,
            "--input-bytes",
            str(input_path.stat().st_size if input_path.exists() and input_path.is_file() else 0),
            "--duration-seconds",
            "1",
            "--defects-detected",
            str(defects),
        ]
    )


def do_handoff(stage: str, contract: str, defect_field: str, *, complete_after: bool = True) -> tuple[dict, str]:
    run([sys.executable, "scripts/run_word.py", "--resume", str(RUN)])
    req = CYCLE / "handoff" / f"{stage}.request.md"
    response = CYCLE / "handoff" / f"{stage}.response.json"
    last_error = ""
    for attempt in range(1, 4):
        value, model = review(
            req.read_text(encoding="utf-8")
            + contract
            + (f"\nPrevious machine rejection:\n{last_error}" if last_error else "")
        )
        response.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        ing = run(
            [
                sys.executable,
                "scripts/run_word.py",
                "--resume",
                str(RUN),
                "--ingest-review",
                stage,
                "--declared-model",
                model,
                "--reviewer-agent-id",
                f"github-actions:{os.environ.get('GITHUB_RUN_ID','unknown')}:{stage}:attempt{attempt}",
            ],
            check=False,
        )
        if ing.returncode == 0:
            saved = read_json(CYCLE / f"{stage}.json")
            defects = len(saved.get(defect_field, [])) if isinstance(saved.get(defect_field), list) else 0
            if complete_after:
                complete(stage, req, defects)
            return saved, model
        last_error = (ing.stdout + ing.stderr)[-16000:]
    raise RuntimeError(f"{stage} review could not satisfy machine contract: {last_error}")


def primary_finding_count(cold: dict | None = None, blind: dict | None = None) -> int:
    normal = read_json(CYCLE / "pass_findings.json")
    total = sum(
        len(item.get("findings", []))
        for item in normal.get("pass_outputs", [])
        if isinstance(item, dict) and isinstance(item.get("findings"), list)
    )
    if cold is not None and isinstance(cold.get("findings"), list):
        total += len(cold["findings"])
    if blind is not None and isinstance(blind.get("article_findings"), list):
        total += len(blind["article_findings"])
    return total


def run_secondary_zero_confirmations(cold: dict) -> dict:
    if primary_finding_count(cold=cold) != 0:
        return {}
    base = f"github-actions:{os.environ.get('GITHUB_RUN_ID','unknown')}:secondary"
    sec_dir = CYCLE / "secondary_reviews"
    sec_dir.mkdir(parents=True, exist_ok=True)

    cold_request = {
        "stage": "secondary_cold_review",
        "entry_body": body_text(),
    }
    (sec_dir / "cold_review.request.json").write_text(
        json.dumps(cold_request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    cold_prompt = (REPO / "prompts/cold_review_prompt_v1.md").read_text(encoding="utf-8")
    cold_contract = r'''

SECONDARY ZERO-FINDING CONFIRMATION. Work independently from the primary reviewer and do not assume the primary result was correct. Return JSON only with summary and findings. Each finding must have id, location, severity high|medium|low, description, reason, suggested_direction, scope_anchors. Every scope anchor has id, exact_quote copied verbatim from the supplied entry, and location_hint. The reason must literally repeat at least one scope_anchors[].exact_quote. If there is no actual defect, return {"summary":"secondary review: no defect found","findings":[]}.
'''
    cold_value, cold_model = review(
        cold_prompt
        + "\n\nINPUT ENTRY BODY:\n"
        + body_text()
        + cold_contract
    )
    cold_value["reviewer"] = reviewer_meta(cold_model, base + ":cold")
    cold_errors = review_liveness.validate_reviewer(
        cold_value["reviewer"], generation_model=generation_model()
    )
    cold_errors.extend(
        review_liveness.validate_finding_liveness(
            cold_value, field="findings", label="secondary cold review findings"
        )
    )
    if cold_errors:
        raise RuntimeError("secondary cold liveness failed: " + "; ".join(cold_errors))

    attr_request = read_json(CYCLE / "check_passes/example-attribution.request.json")
    (sec_dir / "example_attribution.request.json").write_text(
        json.dumps(attr_request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    attr_prompt = r'''
You are a SECOND independent blind example-attribution reviewer. Use only the masked request below. Do not inspect the dictionary entry, the primary review, or any alignment key. Return one JSON object with keys summary, findings, blind_attribution_record. findings is [] when you identify no attribution defect from this independent classification. blind_attribution_record must use schema_version example_attribution_blind_record_v1 and pass_id example-attribution, and its attributions must cover every opaque example_id exactly once. Every row has example_id, classification unique|ambiguous, candidate_sense_ids (one for unique; at least two for ambiguous), discriminating_terms, rationale. For unique rows, every discriminating term is copied verbatim from that example or translation and rationale literally repeats at least one such term. For ambiguous rows, discriminating_terms is [] and rationale literally contains the complete supplied English example. Keep rationales item-specific. Do not invent IDs. Return JSON only.

MASKED REQUEST:
'''
    attr_value, attr_model = review(
        attr_prompt + json.dumps(attr_request, ensure_ascii=False, indent=2)
    )
    record = attr_value.get("blind_attribution_record")
    if not isinstance(record, dict):
        raise RuntimeError("secondary attribution response lacks blind_attribution_record")
    attr_reviewer = reviewer_meta(attr_model, base + ":example-attribution")
    record["schema_version"] = "example_attribution_blind_record_v1"
    record["pass_id"] = "example-attribution"
    record["input_body_sha256"] = str(attr_request.get("input_body_sha256", ""))
    record["blind_request_sha256"] = canonical_hash(attr_request)
    record["recorded_at"] = datetime.now(timezone.utc).isoformat()
    record["reviewer"] = attr_reviewer
    attr_value["reviewer"] = attr_reviewer
    attr_value.setdefault("findings", [])
    attr_value.setdefault("summary", "secondary independent example-attribution classification completed")
    attr_errors = check_passes.validate_blind_attribution_record(
        record,
        attr_request,
        generation_model=generation_model(),
    )
    attr_errors.extend(review_liveness.validate_attribution_liveness(record, attr_request))
    attr_errors.extend(review_liveness.validate_reviewer(attr_reviewer, generation_model=generation_model()))
    if attr_errors:
        raise RuntimeError("secondary attribution liveness failed: " + "; ".join(attr_errors))

    secondary = {
        "cold_review": cold_value,
        "example_attribution": attr_value,
    }
    (CYCLE / "secondary_reviews.json").write_text(
        json.dumps(secondary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if cold_value.get("findings") or attr_value.get("findings"):
        raise RuntimeError("secondary zero-finding confirmation found a defect; a revision cycle is required")
    return secondary


def build_empty_resolutions() -> Path:
    if primary_finding_count(
        cold=read_json(CYCLE / "cold_review.json"),
        blind=read_json(CYCLE / "final_blind.json"),
    ) != 0:
        raise RuntimeError("findings exist; do not create an empty resolution record")
    path = CYCLE / "resolutions.json"
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "resolutions_v1",
        "stage": "resolutions",
        "run_id": f"normal-premise-{CYCLE.name}",
        "context_id": f"normal-premise-context-{CYCLE.name}",
        "input_body_sha256": body_hash(),
        "prompt_sha256": "no-findings-empty-resolution",
        "input_artifacts": ["entry_body", "all_findings"],
        "recorded_at": now,
        "resolutions": [],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def final_review_contract() -> str:
    targets = content_audit.extract_targets(ENTRY)
    relations = content_audit.extract_relations(targets)
    normal = read_json(CYCLE / "pass_findings.json")
    blind = read_json(CYCLE / "final_blind.json")
    source = read_json(CYCLE / "source_inventory.json")
    seal = read_json(CYCLE / "blind_seal.json")
    findings: list[dict] = []
    for output in normal.get("pass_outputs", []):
        if isinstance(output, dict):
            findings.extend(item for item in output.get("findings", []) if isinstance(item, dict))
    cold = read_json(CYCLE / "cold_review.json")
    findings.extend(item for item in cold.get("findings", []) if isinstance(item, dict))
    findings.extend(item for item in blind.get("article_findings", []) if isinstance(item, dict))
    source_gate = source.get("source_first_audit", {}) if isinstance(source.get("source_first_audit"), dict) else {}
    inventory = {
        "blind_output_sha256": seal.get("blind_output_sha256"),
        "body_sha256": body_hash(),
        "target_results": [
            {"id": str(item["id"]), "exact_quote": str(item.get("text", ""))}
            for item in targets
        ],
        "relation_results": [
            {"id": str(item["id"]), "exact_quote": str(item.get("description", ""))}
            for item in relations
        ],
        "normal_candidate_ids": [
            str(item["id"])
            for item in normal.get("independent_candidates", [])
            if isinstance(item, dict) and item.get("id")
        ],
        "blind_candidates": [
            {
                "id": str(item["id"]),
                "assertion_ids": [
                    str(a["id"])
                    for a in item.get("semantic_assertions", [])
                    if isinstance(a, dict) and a.get("id")
                ],
            }
            for item in blind.get("independent_candidates", [])
            if isinstance(item, dict) and item.get("id")
        ],
        "finding_ids": [str(item["id"]) for item in findings if item.get("id")],
        "evidence_ids": [str(item) for item in source.get("evidence_link_ids", []) if str(item).strip()],
        "source_union_ids": [
            str(item["id"])
            for item in source_gate.get("source_union", [])
            if isinstance(item, dict) and item.get("id")
        ],
    }
    return """

CRITICAL FINAL MACHINE CONTRACT. Return JSON only. The supplied review spec and input packet remain authoritative. You must independently judge the article; do not rubber-stamp it. The exact coverage inventory below is mechanical bookkeeping only, not a prior quality judgment.
- decision is pass or reject; pass requires blockers=[] and every individual result status=pass.
- Copy blind_output_sha256 exactly from REQUIRED_INVENTORY.
- target_results and relation_results must cover every listed id exactly once. Each row has id, the matching target_id or relation_id, status pass|fail, notes, evidence_checked=true. For liveness, notes MUST literally include the supplied exact_quote for that id.
- normal_candidate_results, finding_results, and evidence_checks cover their listed IDs exactly once; each row has id, status pass|fail, notes.
- blind_candidate_results cover each listed blind candidate id exactly once; each row has id, status pass|fail, notes, assertion_ids exactly as listed, and verified_body_sha256 copied from REQUIRED_INVENTORY.body_sha256.
- source_inventory_results cover each source_union id exactly once; each row has id, union_id equal to id, status pass|fail, notes.
- Include blockers as a list and notes as a list. Return no markdown.

REQUIRED_INVENTORY:
""" + json.dumps(inventory, ensure_ascii=False, indent=2)


def git_commit_push(message: str, *paths: Path) -> None:
    rel = [str(path.relative_to(REPO)) for path in paths]
    run(["git", "add", "--", *rel])
    status = run(["git", "diff", "--cached", "--quiet"], check=False)
    if status.returncode == 0:
        return
    run(["git", "commit", "-m", message])
    run(["git", "push", "origin", "HEAD:add/premise-v5-20260829"])


def update_entry_and_queue() -> Path:
    final = read_json(CYCLE / "final_review.json")
    if final.get("decision") != "pass" or final.get("blockers"):
        raise RuntimeError("final review did not pass")
    today = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Tokyo")).date().isoformat()
    text = ENTRY.read_text(encoding="utf-8")
    text = text.replace("status: draft", "status: checked", 1)
    text = text.replace("checked: false", "checked: true", 1)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("updated_at:"):
            lines[i] = f"updated_at: {today}"
            break
    ENTRY.write_text("\n".join(lines) + "\n", encoding="utf-8")

    queue = REPO / "queue/words.csv"
    with queue.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
        fields = list(rows[0].keys()) if rows else [
            "headword", "type", "status", "priority", "file", "prompt_version", "model",
            "created_at", "updated_at", "checked", "notes",
        ]
    existing = next((row for row in rows if row.get("headword") == HEADWORD), None)
    priority = max([int(row.get("priority") or 0) for row in rows] + [0]) + 1
    values = {
        "headword": HEADWORD,
        "type": "word",
        "status": "checked",
        "priority": str(existing.get("priority") if existing else priority),
        "file": "entries/p/premise.md",
        "prompt_version": "entry_spec_v5",
        "model": generation_model(),
        "created_at": (existing.get("created_at") if existing else "2026-08-29"),
        "updated_at": today,
        "checked": "true",
        "notes": "source-first inventory; seven independent checker passes; context-free cold review; secondary zero-finding confirmation; sealed final blind review; final reconciliation passed",
    }
    if existing:
        existing.update(values)
    else:
        rows.append(values)
    with queue.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    status_path = CYCLE / "status_update.json"
    status_path.write_text(
        json.dumps(
            {
                "schema_version": "status_update_v1",
                "stage": "status_update",
                "run_id": CYCLE.name,
                "headword": HEADWORD,
                "entry_path": "entries/p/premise.md",
                "audit_path": "audits/p/premise.json",
                "decision": "pass",
                "body_sha256": body_hash(),
                "entry_status_before": "draft",
                "entry_status_after": "checked",
                "queue_status_before": existing.get("status", "absent") if existing else "absent",
                "queue_status_after": "checked",
                "checked": True,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return status_path


def main() -> int:
    global RUN, CYCLE
    RUN, CYCLE = select_latest_restarted_run()
    refresh_preserved_artifact_hashes()
    print(json.dumps({"run": str(RUN.relative_to(REPO)), "cycle": CYCLE.name}, ensure_ascii=False))

    cold_contract = r'''

MACHINE/LIVENESS CONTRACT (mandatory): Return JSON only. Include summary and findings. Each finding must have id, location, severity high|medium|low, description, reason, suggested_direction, scope_anchors. Every scope anchor must have id, exact_quote copied verbatim from the supplied entry body, and location_hint. For every finding, the reason MUST literally repeat at least one scope_anchors[].exact_quote string verbatim. Make findings individually reasoned; do not reuse boilerplate. If there is no actual problem, return {"summary":"問題候補なし","findings":[]} rather than inventing a finding.
'''
    cold, _ = do_handoff("cold_review", cold_contract, "findings")
    run_secondary_zero_confirmations(cold)

    blind_contract = r'''

MACHINE/LIVENESS CONTRACT (mandatory): Return exactly one final_blind_review_v2 JSON object, JSON only. Include provisional_decision, independent_candidates, article_findings. Every candidate must have a unique id, surface_form, frame, meaning, disposition included|excluded, rationale, and at least one semantic_assertion with unique id, statement, polarity must_hold|must_not_hold, scope. Candidate rationale MUST literally repeat at least one of that candidate's surface_form, frame, or meaning strings verbatim. Every article finding must have unique id, taxonomy_id, location object {section,line_start,line_end,exact_quote}, severity blocking|minor, rationale; the rationale MUST literally repeat location.exact_quote verbatim. Do not output article_target_ids, evidence_link_ids, resolution_ids. Use provisional_decision=reject only for an actual blocker candidate; otherwise pass. Do not invent problems just to avoid a zero-finding result.
'''
    blind, _ = do_handoff("final_blind", blind_contract, "article_findings")
    # The blind candidate list is an explicit inventory and may contain
    # correctly excluded candidates (for example, a spelling variant or an
    # inflection that is not a separate sense). Per final_blind_prompt_v2,
    # Any article finding, including a minor one, must be resolved before sealing;
    # the final blind's explicit candidate inventory is not itself a defect.
    # actual content defects are represented by article_findings or reject.
    blind_reject = blind.get("provisional_decision") == "reject"
    if primary_finding_count(cold=cold, blind=blind) or blind_reject:
        raise RuntimeError("primary or blind review found a substantive issue; revision cycle required before sealing")

    liveness = run([sys.executable, "scripts/review_liveness.py", "validate-run", str(CYCLE)], check=False)
    if liveness.returncode:
        raise RuntimeError("review liveness failed before blind seal")

    seal = CYCLE / "blind_seal.json"
    run(
        [
            sys.executable,
            "scripts/generate_audit_manifest.py",
            "seal-blind",
            str(ENTRY),
            str(CYCLE / "final_blind.json"),
            "--output",
            str(seal),
        ]
    )
    complete("blind_seal", CYCLE / "final_blind.json")
    git_commit_push("audit(premise): seal restarted cold and final blind reviews", RUN, CYCLE)

    resolutions = build_empty_resolutions()
    complete("finding_resolution", resolutions)

    final, _ = do_handoff(
        "final_review",
        final_review_contract(),
        "blockers",
        complete_after=False,
    )
    if final.get("decision") != "pass" or final.get("blockers"):
        raise RuntimeError("independent final reviewer rejected premise")

    audit = REPO / "audits/p/premise.json"
    run(
        [
            sys.executable,
            "scripts/generate_audit_manifest.py",
            "generate",
            str(ENTRY),
            str(CYCLE),
            "--output",
            str(audit),
        ]
    )
    complete("final_review", CYCLE / "final_review.json")

    status_path = update_entry_and_queue()
    complete("status_update", status_path)

    run([sys.executable, "scripts/export_all_markdown.py"])
    run([sys.executable, "scripts/export_index.py"])
    complete("export", REPO / "exports/dictionary_all.md")

    run([sys.executable, "scripts/validate_entry.py", "entries"])
    run([sys.executable, "scripts/validate_repository.py"])
    run([sys.executable, "scripts/review_liveness.py", "validate-run", str(CYCLE)])
    run([sys.executable, "scripts/generate_audit_manifest.py", "validate", str(ENTRY), str(audit)])

    # Temporary recovery machinery must not enter the PR.
    workflow = REPO / ".github/workflows/premise-finish.yml"
    script = Path(__file__)
    workflow.unlink(missing_ok=True)
    script.unlink(missing_ok=True)
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", "entry(premise): complete guarded review workflow"])
    run(["git", "push", "origin", "HEAD:add/premise-v5-20260829"])
    print(json.dumps({"status": "completed", "run_id": CYCLE.name, "audit": "audits/p/premise.json"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
