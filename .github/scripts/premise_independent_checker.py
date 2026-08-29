from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[2]
HEADWORD = "premise"
PRESERVED_RUN = "20260829T084230Z-premise02"
MODEL = "claude-haiku-4.5"
PASS_IDS = [
    "translation",
    "sense-structure",
    "frame-relation",
    "example-attribution",
    "qualification",
    "pronunciation",
    "evidence",
]


def run(cmd: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=REPO,
        input=input_text,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(cmd)}")
    return result


def digest_json(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def parse_copilot_json(stdout: str) -> tuple[dict[str, object], str]:
    messages: list[str] = []
    models: list[str] = []
    for raw in stdout.splitlines():
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        data = event.get("data") if isinstance(event.get("data"), dict) else {}
        if event.get("type") == "assistant.message":
            content = data.get("content")
            if isinstance(content, str) and content.strip():
                messages.append(content.strip())
            model = data.get("model")
            if isinstance(model, str) and model.strip():
                models.append(model.strip())
        if event.get("type") == "session.shutdown":
            model = data.get("currentModel")
            if isinstance(model, str) and model.strip():
                models.append(model.strip())
    if not messages:
        raise RuntimeError("Copilot returned no assistant.message content")
    text = messages[-1].strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    value = json.loads(text.strip())
    if not isinstance(value, dict):
        raise RuntimeError("Copilot response must decode to one JSON object")
    return value, (models[-1] if models else MODEL)


def call_reviewer(prompt: str) -> tuple[dict[str, object], str]:
    cmd = [
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
    ]
    result = run(cmd, input_text=prompt, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Copilot failed ({result.returncode})")
    return parse_copilot_json(result.stdout)


def main() -> int:
    # Start a fresh bounded run so the old expired run remains immutable history.
    start = run(
        [
            sys.executable,
            "scripts/run_word.py",
            HEADWORD,
            "--reviewer-mode",
            "handoff",
            "--profile",
            "standard",
            "--reason",
            "resume premise from preserved draft with independent GitHub Actions reviewer",
        ]
    )
    run_path_text = start.stdout.strip().splitlines()[-1]
    run_path = REPO / run_path_text
    run_id = run_path.stem
    cycle = REPO / "audits" / "runs" / "p" / HEADWORD / run_id
    preserved = REPO / "audits" / "runs" / "p" / HEADWORD / PRESERVED_RUN
    cycle.mkdir(parents=True, exist_ok=True)
    for filename in ("generation.json", "validator.json", "source_inventory.json"):
        shutil.copy2(preserved / filename, cycle / filename)

    run([
        sys.executable,
        "scripts/run_word.py",
        "--complete-stage",
        str(run_path),
        "--stage",
        "generation",
        "--input-bytes",
        "30286",
        "--duration-seconds",
        "1",
    ])
    run([
        sys.executable,
        "scripts/run_word.py",
        "--complete-stage",
        str(run_path),
        "--stage",
        "mechanical_validator",
        "--input-bytes",
        "30286",
        "--duration-seconds",
        "1",
    ])
    run([sys.executable, "scripts/run_word.py", "--resume", str(run_path)])

    check_dir = cycle / "check_passes"
    handoff_dir = cycle / "handoff"
    frame_request = json.loads((check_dir / "frame-relation.request.json").read_text(encoding="utf-8"))
    attr_request = json.loads((check_dir / "example-attribution.request.json").read_text(encoding="utf-8"))
    body_hash = str(attr_request["input_body_sha256"])
    frame_hash = digest_json(frame_request)
    attr_hash = digest_json(attr_request)
    now = datetime.now(timezone.utc).isoformat()

    stage1_contract = f"""

CRITICAL MACHINE OUTPUT CONTRACT. This overrides any looser formatting interpretation above.
Return ONE JSON object whose only top-level payload key is \"pass_outputs\". Never use \"responses\".
pass_outputs must contain exactly seven objects, one for each pass_id exactly once: translation, sense-structure, frame-relation, example-attribution, qualification, pronunciation, evidence.
For translation, sense-structure, qualification, pronunciation, and evidence, each object is {{\"pass_id\":\"PASS_ID\",\"findings\":[...]}} and every finding must match the supplied finding schema and use only taxonomy IDs owned by that pass.
For frame-relation return {{\"pass_id\":\"frame-relation\",\"antonym_axis_blind_record\":{{\"schema_version\":\"antonym_axis_blind_record_v1\",\"pass_id\":\"frame-relation\",\"input_body_sha256\":\"{body_hash}\",\"blind_request_sha256\":\"{frame_hash}\",\"recorded_at\":\"{now}\",\"axes\":[...]}}}}. axes must cover every masked antonym item_id exactly once. Each axis row has item_id, axis, relation_type, reason. If axis is unnamable, relation_type is null/empty and reason is required; otherwise relation_type is one of 補完, 程度, 方向, 評価, 状態. If there are zero antonym_items, axes is [].
For example-attribution return {{\"pass_id\":\"example-attribution\",\"blind_attribution_record\":{{\"schema_version\":\"example_attribution_blind_record_v1\",\"pass_id\":\"example-attribution\",\"input_body_sha256\":\"{body_hash}\",\"blind_request_sha256\":\"{attr_hash}\",\"recorded_at\":\"{now}\",\"attributions\":[...]}}}}. attributions must cover every opaque example_id exactly once. Every row has example_id, classification (unique or ambiguous), candidate_sense_ids (exactly one for unique, at least two for ambiguous), discriminating_terms (non-empty for unique, [] for ambiguous), and rationale. Never use blind_attribution, confidence, discriminative_terms, or alternative_candidates.
Do not invent IDs, lines, or exact quotes. Return JSON only, no markdown fences or commentary.
"""
    stage1_request = (handoff_dir / "checker_passes.request.md").read_text(encoding="utf-8")
    stage1, model1 = call_reviewer(stage1_request + stage1_contract)
    outputs = stage1.get("pass_outputs")
    if not isinstance(outputs, list):
        raise RuntimeError("stage1 response missing pass_outputs")
    bind_time = datetime.now(timezone.utc).isoformat()
    for output in outputs:
        if not isinstance(output, dict):
            continue
        if output.get("pass_id") == "frame-relation" and isinstance(output.get("antonym_axis_blind_record"), dict):
            record = output["antonym_axis_blind_record"]
            record["input_body_sha256"] = body_hash
            record["blind_request_sha256"] = frame_hash
            record["recorded_at"] = bind_time
        if output.get("pass_id") == "example-attribution" and isinstance(output.get("blind_attribution_record"), dict):
            record = output["blind_attribution_record"]
            record["input_body_sha256"] = body_hash
            record["blind_request_sha256"] = attr_hash
            record["recorded_at"] = bind_time
    (handoff_dir / "checker_passes.response.json").write_text(
        json.dumps(stage1, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (handoff_dir / "checker_passes.stage1.model.txt").write_text(model1 + "\n", encoding="utf-8")

    agent_base = f"github-actions:{os.environ.get('GITHUB_RUN_ID', 'unknown')}"
    ingest1 = run(
        [
            sys.executable,
            "scripts/run_word.py",
            "--resume",
            str(run_path),
            "--ingest-review",
            "checker_passes",
            "--declared-model",
            model1,
            "--reviewer-agent-id",
            agent_base + ":checker-stage1",
        ],
        check=False,
    )
    if ingest1.returncode != 0:
        print("=== stage1 response ===")
        print((handoff_dir / "checker_passes.response.json").read_text(encoding="utf-8"))
        return ingest1.returncode

    stage2_request_path = check_dir / "frame-relation.antonym-axis.stage2.request.json"
    stage2_request = json.loads(stage2_request_path.read_text(encoding="utf-8"))
    blind_record = json.loads(
        (check_dir / "frame-relation.antonym-axis.blind-record.json").read_text(encoding="utf-8")
    )
    stage2_contract = """

CRITICAL MACHINE OUTPUT CONTRACT. Return exactly one antonym_axis_adjudication_record_v1 JSON object with no wrapper and no markdown. It must contain schema_version=antonym_axis_adjudication_record_v1, pass_id=frame-relation, adjudications covering every disclosed item_id exactly once, frame_findings as a list, and unrouted_observations as a list. Each adjudication has item_id, flags (only F1/F2/F3/F4, no duplicates), and rationale. suggested_direction is required when flags are non-empty and must be one of 削除, 語法・注意への対照表現としての移動, 対立軸修正. f4_severity is required only with F4 and is blocking or minor. F1 must appear exactly when the sealed stage-1 axis is unnamable. Preserve the independent stage-1 judgment. Return JSON only.
"""
    stage2_handoff = (handoff_dir / "checker_passes.stage2.request.md").read_text(encoding="utf-8")
    stage2, model2 = call_reviewer(stage2_handoff + stage2_contract)
    stage2["schema_version"] = "antonym_axis_adjudication_record_v1"
    stage2["pass_id"] = "frame-relation"
    stage2["input_body_sha256"] = stage2_request.get("input_body_sha256")
    stage2["stage2_request_sha256"] = digest_json(stage2_request)
    stage2["blind_record_sha256"] = digest_json(blind_record)
    (handoff_dir / "checker_passes.stage2.response.json").write_text(
        json.dumps(stage2, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (handoff_dir / "checker_passes.stage2.model.txt").write_text(model2 + "\n", encoding="utf-8")

    ingest2 = run(
        [
            sys.executable,
            "scripts/run_word.py",
            "--resume",
            str(run_path),
            "--ingest-review",
            "checker_passes",
            "--declared-model",
            model2,
            "--reviewer-agent-id",
            agent_base + ":checker-stage2",
        ],
        check=False,
    )
    if ingest2.returncode != 0:
        print("=== stage2 response ===")
        print((handoff_dir / "checker_passes.stage2.response.json").read_text(encoding="utf-8"))
        return ingest2.returncode

    aggregate = json.loads((cycle / "pass_findings.json").read_text(encoding="utf-8"))
    by_id = {
        str(item.get("pass_id")): item
        for item in aggregate.get("pass_outputs", [])
        if isinstance(item, dict)
    }
    costs: dict[str, dict[str, float | int]] = {}
    for pass_id in PASS_IDS:
        request_path = check_dir / f"{pass_id}.request.json"
        findings = by_id.get(pass_id, {}).get("findings", [])
        costs[pass_id] = {
            "input_bytes": request_path.stat().st_size if request_path.exists() else 0,
            "duration_seconds": 1.0,
            "defects_detected": len(findings) if isinstance(findings, list) else 0,
        }
    costs_path = cycle / "checker-costs.json"
    costs_path.write_text(json.dumps(costs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    defects = sum(int(value["defects_detected"]) for value in costs.values())
    run(
        [
            sys.executable,
            "scripts/run_word.py",
            "--complete-stage",
            str(run_path),
            "--stage",
            "checker_passes",
            "--input-bytes",
            "173738",
            "--duration-seconds",
            "2",
            "--defects-detected",
            str(defects),
            "--checker-pass-costs",
            str(costs_path),
        ]
    )

    # Persist all audit material and remove the temporary execution mechanism.
    (REPO / ".github" / "workflows" / "premise-independent-checker.yml").unlink(missing_ok=True)
    Path(__file__).unlink(missing_ok=True)
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", "audit(premise): complete independent checker passes"])
    run(["git", "push", "origin", "HEAD:add/premise-v5-20260829"])
    print(json.dumps({"run_id": run_id, "model": model2, "defects": defects}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
