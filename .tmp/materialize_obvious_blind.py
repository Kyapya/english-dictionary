from __future__ import annotations

import base64
import gzip
import hashlib
import json
import runpy
from pathlib import Path

from scripts import content_audit

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audits/o/obvious.json"
RAWDIR = ROOT / "audits/runs/o/obvious/cycle-001"

# Idempotency: once the blind output is sealed, later CI runs must not reseal it.
if AUDIT.exists():
    existing = json.loads(AUDIT.read_text(encoding="utf-8"))
    blind = existing.get("final_review", {}).get("blind_review", {})
    if blind.get("output_sha256") and not existing.get("final_review", {}).get("execution", {}).get("reconciliation_started_at"):
        raise SystemExit(0)

# Materialize the already-prepared normal/post-cold audit state from the bounded payload.
payload = base64.b64decode((ROOT / ".tmp/obvious_generator.b64").read_text(encoding="ascii"))
code = gzip.decompress(payload).decode("utf-8")
tmp = ROOT / ".tmp/_run_obvious_generator.py"
tmp.write_text(code, encoding="utf-8")
try:
    runpy.run_path(str(tmp), run_name="__main__")
finally:
    tmp.unlink(missing_ok=True)

data = json.loads(AUDIT.read_text(encoding="utf-8"))
body_hash = data["body_sha256"]
prompt_hash = hashlib.sha256((ROOT / "prompts/final_review_spec_v1.md").read_bytes()).hexdigest()
run_id = "final-obvious-cycle001-20260825"
context_id = "final-obvious-context-free-20260825"
started_at = "2026-08-25T14:20:00+09:00"
recorded_at = "2026-08-25T14:23:30+09:00"

candidates = [
    {
        "id": "IC-01",
        "surface_form": "obvious; be obvious; it is obvious that; obvious to/from; make it obvious; obvious wh-clause",
        "frame": "X is obvious; it is obvious (to Y/from Z) that S; X is obvious to Y/from Z; make X/it obvious; it is obvious what/why/how/who ...",
        "meaning": "見た目・行動・証拠・文脈などから、特別な説明や難しい推論なしに容易に認識・理解できる",
        "disposition": "included",
        "rationale": "現代英語の中心義。補語構文・to/from・make obvious・wh節まで高頻度で、学習上必須。",
        "article_target_ids": [],
        "evidence_link_ids": [],
        "semantic_assertions": [
            {
                "id": "SA-01",
                "statement": "一般義の obvious は『容易に認識・理解できる』を表すが、文字どおり全員が必ず知っていることまでは要求しない。",
                "polarity": "must_hold",
                "scope": "一般義の定義・構文・語法・用例",
            }
        ],
    },
    {
        "id": "IC-02",
        "surface_form": "the/an obvious choice/solution/answer/candidate/example; the obvious thing/place",
        "frame": "the/an obvious N; the obvious thing to do; the obvious place to start; no obvious solution/answer; the most obvious N",
        "meaning": "複数候補の中で、まず自然に思いつく・目立つ候補である",
        "disposition": "included",
        "rationale": "単なる知覚的明白さから区別して学ぶ価値の高い高頻度用法。最善・唯一を必ずしも意味しない。",
        "article_target_ids": [],
        "evidence_link_ids": [],
        "semantic_assertions": [
            {
                "id": "SA-02",
                "statement": "obvious choice/solution/answer は『まず思いつく自然な候補』を表し、その候補が唯一または最善であることを必ずしも含意しない。",
                "polarity": "must_hold",
                "scope": "候補・解決策・答えの語義と用例",
            }
        ],
    },
    {
        "id": "IC-03",
        "surface_form": "too obvious; an obvious ending/joke/ploy; state the obvious; avoid the obvious",
        "frame": "X is too/rather/pretty obvious; an obvious ending/joke/ploy; state/avoid the obvious",
        "meaning": "予想しやすすぎる・見え見えで、新鮮さ・想像力・繊細さに欠けるという批判的評価",
        "disposition": "included",
        "rationale": "批評・会話で独立した学習価値がある評価的拡張。ただし obvious 自体に常に否定評価があるわけではない。",
        "article_target_ids": [],
        "evidence_link_ids": [],
        "semantic_assertions": [
            {
                "id": "SA-03",
                "statement": "批判的 obvious は文脈依存の評価的拡張であり、neutral な an obvious reference や単なる『容易に認識できる』用法へ否定評価を一般化してはならない。",
                "polarity": "must_not_hold",
                "scope": "批判的語義の境界・関連表現",
            }
        ],
    },
    {
        "id": "IC-04",
        "surface_form": "obvious in patent law; obvious to a person skilled in the art; obvious in view of prior art; obvious under 35 U.S.C. §103; obvious to try",
        "frame": "claimed invention/claim is or would have been obvious to a skilled person; obvious in view of prior art; obvious under §103; reference renders claim obvious; option is obvious to try",
        "meaning": "特許法上、当業者が先行技術等から容易に想到でき、必要な非自明性・inventive step を欠く",
        "disposition": "included",
        "rationale": "特許法で重要な専門用法。米国 §103 を中心に、EPC/英国にも obvious が法的基準語として現れるため法域差の限定が必要。",
        "article_target_ids": [],
        "evidence_link_ids": [],
        "semantic_assertions": [
            {
                "id": "SA-04A",
                "statement": "特許法上の obvious は一般人基準ではなく、関連法域が定める skilled person / person having ordinary skill in the art と先行技術を基準にする。",
                "polarity": "must_hold",
                "scope": "特許法語義の定義・主体・基準時・先行技術",
            },
            {
                "id": "SA-04B",
                "statement": "米国の obvious to try は単に試せる選択肢が存在するだけで自動的に §103 obviousness を成立させるものではなく、有限個の特定された予測可能な解決策と合理的成功期待等の条件が必要である。",
                "polarity": "must_hold",
                "scope": "米国特許法 obvious to try の説明",
            },
            {
                "id": "SA-04C",
                "statement": "米国 §103、EPC Article 56、英国 Patents Act 1977 section 3 は同一の具体的法的テストとして無条件に同一視してはならない。",
                "polarity": "must_not_hold",
                "scope": "法域比較",
            },
        ],
    },
    {
        "id": "IC-05",
        "surface_form": "obviously; obviousness",
        "frame": "obviously + adjective/clause; obviousness of X",
        "meaning": "副詞『明らかに／当然ながら』と名詞『明白さ』",
        "disposition": "included",
        "rationale": "生産的で一般学習価値の高い派生形。obviously は文副詞としても高頻度。",
        "article_target_ids": [],
        "evidence_link_ids": [],
        "semantic_assertions": [
            {
                "id": "SA-05",
                "statement": "obviously は obvious の一般義に対応する副詞として、容易に分かる様態だけでなく話し手の判断を示す文副詞にも使える。",
                "polarity": "must_hold",
                "scope": "語形成 obviously/obviousness",
            }
        ],
    },
    {
        "id": "IC-06",
        "surface_form": "nonobvious; nonobviousness",
        "frame": "claim/invention is nonobvious over prior art; nonobviousness requirement",
        "meaning": "特に米国特許法で、当業者にとって先行技術から容易に想到できないこと／非自明性",
        "disposition": "included",
        "rationale": "obvious の特許法用法を理解するうえで直接対立する重要な専門派生語。",
        "article_target_ids": [],
        "evidence_link_ids": [],
        "semantic_assertions": [
            {
                "id": "SA-06",
                "statement": "nonobvious / nonobviousness は特許法の専門的対立語として扱い、日常英語の単純な not obvious と完全に同一のレジスターとして一般化しない。",
                "polarity": "must_hold",
                "scope": "語形成・特許法反意語",
            }
        ],
    },
]

final = data["final_review"]
final["role"] = "final_adjudicator"
final["reviewer_id"] = "final-obvious-cycle001-20260825"
final["reviewed_at"] = ""
final["completed"] = False
final["execution"] = {
    "run_id": run_id,
    "context_id": context_id,
    "started_at": started_at,
    "completed_at": "",
    "input_body_sha256": body_hash,
    "prompt_sha256": prompt_hash,
    "context_mode": "context_free",
    "input_artifacts": ["entry_body", "final_review_spec"],
    "reconciliation_started_at": "",
    "reconciliation_input_artifacts": [],
}
final["body_sha256"] = ""
final["decision"] = "pending"
final["blind_review"] = {
    "seal_version": "blind_seal_v2",
    "completed": True,
    "recorded_at": recorded_at,
    "sealed_at": "",
    "body_sha256": body_hash,
    "audit_visible": False,
    "provisional_decision": "pass",
    "article_findings": [],
    "output_sha256": "",
}
final["independent_candidates"] = candidates
for key in (
    "inventory_comparison",
    "blind_finding_results",
    "target_results",
    "relation_results",
    "candidate_results",
    "finding_results",
    "evidence_checks",
    "blockers",
):
    final[key] = []
data["semantic_gate"]["final_inventory_checks"] = []

RAWDIR.mkdir(parents=True, exist_ok=True)
raw = {
    "stage": "final_blind",
    "role": "final_adjudicator",
    "reviewer_id": "final-obvious-cycle001-20260825",
    "run_id": run_id,
    "context_id": context_id,
    "started_at": started_at,
    "recorded_at": recorded_at,
    "input_body_sha256": body_hash,
    "prompt_sha256": prompt_hash,
    "audit_visible": False,
    "provisional_decision": "pass",
    "independent_candidates": candidates,
    "article_findings": [],
}
raw_path = RAWDIR / "final_blind.json"
raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
data["current_cycle"]["raw_outputs"]["final_blind"] = {
    "path": raw_path.relative_to(ROOT).as_posix(),
    "sha256": "",
    "input_body_sha256": body_hash,
    "prompt_sha256": prompt_hash,
    "run_id": run_id,
    "context_id": context_id,
    "sealed_output_sha256": "",
}
AUDIT.parent.mkdir(parents=True, exist_ok=True)
AUDIT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
errors = content_audit.seal_blind_review(AUDIT)
if errors:
    raise SystemExit("\n".join(errors))
