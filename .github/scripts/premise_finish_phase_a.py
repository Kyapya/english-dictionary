from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "audits/workflow_runs/premise/20260829T223614Z-5cbb1e5c.json"
CYCLE = REPO / "audits/runs/p/premise/20260829T223614Z-5cbb1e5c"
ENTRY = REPO / "entries/p/premise.md"
MODEL = "auto"


def run(cmd: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, cwd=REPO, input=input_text, text=True, capture_output=True, timeout=900)
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
    text = messages[-1]
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    value = json.loads(text.strip())
    if not isinstance(value, dict):
        raise RuntimeError("review response must be one JSON object")
    return value, (models[-1] if models else MODEL)


def review(prompt: str) -> tuple[dict, str]:
    p = run([
        "copilot", "--no-ask-user", "--no-custom-instructions", "--model", MODEL,
        "--output-format", "json", "--deny-tool=shell", "--deny-tool=write",
        "--deny-tool=url", "--deny-tool=memory",
    ], input_text=prompt, check=False)
    if p.returncode:
        raise RuntimeError(f"Copilot reviewer failed ({p.returncode})")
    return parse_copilot(p.stdout)


def complete(stage: str, request_path: Path, defects: int) -> None:
    run([
        sys.executable, "scripts/run_word.py", "--complete-stage", str(RUN),
        "--stage", stage, "--input-bytes", str(request_path.stat().st_size),
        "--duration-seconds", "1", "--defects-detected", str(defects),
    ])


def do_handoff(stage: str, contract: str, defect_field: str) -> tuple[dict, str]:
    run([sys.executable, "scripts/run_word.py", "--resume", str(RUN)])
    req = CYCLE / "handoff" / f"{stage}.request.md"
    response = CYCLE / "handoff" / f"{stage}.response.json"
    last_error = ""
    for attempt in range(1, 3):
        value, model = review(req.read_text(encoding="utf-8") + contract + (f"\nPrevious machine rejection:\n{last_error}" if last_error else ""))
        response.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        ing = run([
            sys.executable, "scripts/run_word.py", "--resume", str(RUN),
            "--ingest-review", stage, "--declared-model", model,
            "--reviewer-agent-id", f"github-actions:{os.environ.get('GITHUB_RUN_ID','unknown')}:{stage}:attempt{attempt}",
        ], check=False)
        if ing.returncode == 0:
            saved = json.loads((CYCLE / f"{stage}.json").read_text(encoding="utf-8"))
            defects = len(saved.get(defect_field, [])) if isinstance(saved.get(defect_field), list) else 0
            complete(stage, req, defects)
            return saved, model
        last_error = (ing.stdout + ing.stderr)[-12000:]
    raise RuntimeError(f"{stage} review could not satisfy machine contract: {last_error}")


def main() -> int:
    cold_contract = r'''

MACHINE/LIVENESS CONTRACT (mandatory): Return JSON only. Include summary and findings. Each finding must have id, location, severity high|medium|low, description, reason, suggested_direction, scope_anchors. Every scope anchor must have id, exact_quote copied verbatim from the supplied entry body, and location_hint. For every finding, the `reason` MUST literally repeat at least one of its scope_anchors[].exact_quote strings verbatim. Make findings individually reasoned; do not reuse boilerplate. If there is no actual problem, return {"summary":"問題候補なし","findings":[]} rather than inventing a finding.
'''
    cold, _ = do_handoff("cold_review", cold_contract, "findings")

    blind_contract = r'''

MACHINE/LIVENESS CONTRACT (mandatory): Return exactly one final_blind_review_v2 JSON object, JSON only. Include provisional_decision, independent_candidates, article_findings. Every candidate must have a unique id, surface_form, frame, meaning, disposition included|excluded, rationale, and at least one semantic_assertion with unique id, statement, polarity must_hold|must_not_hold, scope. Candidate rationale MUST literally repeat at least one of that candidate's surface_form, frame, or meaning strings verbatim. Every article finding must have unique id, taxonomy_id, location object {section,line_start,line_end,exact_quote}, severity blocking|minor, rationale; the rationale MUST literally repeat location.exact_quote verbatim. Do not output article_target_ids, evidence_link_ids, resolution_ids. Use provisional_decision=reject only for an actual blocker candidate; otherwise pass. Do not invent problems just to avoid a zero-finding result.
'''
    blind, _ = do_handoff("final_blind", blind_contract, "article_findings")

    seal = CYCLE / "blind_seal.json"
    run([
        sys.executable, "scripts/generate_audit_manifest.py", "seal-blind",
        str(ENTRY), str(CYCLE / "final_blind.json"), "--output", str(seal),
    ])
    run([
        sys.executable, "scripts/run_word.py", "--complete-stage", str(RUN),
        "--stage", "blind_seal", "--input-bytes", str((CYCLE / "final_blind.json").stat().st_size),
        "--duration-seconds", "1",
    ])

    # Chronology invariant: final blind + seal must exist in an ancestor commit
    # before any final_review is created.
    run(["git", "add", str(RUN.relative_to(REPO)), str(CYCLE.relative_to(REPO))])
    run(["git", "commit", "-m", "audit(premise): seal cold and final blind reviews"])
    run(["git", "push", "origin", "HEAD:add/premise-v5-20260829"])
    print(json.dumps({
        "cold_findings": len(cold.get("findings", [])),
        "blind_findings": len(blind.get("article_findings", [])),
        "excluded_candidates": len([x for x in blind.get("independent_candidates", []) if isinstance(x, dict) and x.get("disposition") != "included"]),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
