# 2026-08-29 single-run retry loop incident

## Symptom

After the late-August workflow changes, a headword request could continue for hours without reaching a merged checked entry. The concrete `disorder` attempt produced many sibling remote branches, including `disorder-final-20260829-v5` and `disorder-final-20260829-v6`, instead of resuming one workflow run.

## Evidence

- PR #123 bounded repeated review-ingestion failures inside one run, but its own notes left one hole open: a newly created run resets the deadline and failure counter.
- `disorder-final-20260829-v5` ended at commit `717ef8e3e6c7e374b3e91977f79e53d7374b1298` (`workflow(disorder): initialize guarded run`).
- `disorder-final-20260829-v6` ended at commit `8a3cccd8f3b497b0de3a9e2ab51480f800291647` with the same initialization-only pattern.
- Remote branch discovery showed repeated `disorder-final-*` variants. This is incompatible with the intended resume model and allows every retry to receive a fresh elapsed-time budget.

## Root cause

The guard bounded retries only inside a single workflow manifest. Nothing at the new-run entrypoint checked whether another remote branch already held an unfinished manifest for the same headword. When an execution environment or conversation lost local state, an agent could create another branch and call the new-run path again. That bypassed the per-run retry ceiling by resetting `run_id`, `deadline_at`, heartbeat and review failure counters.

The review-independence and two-stage blind checks made the workflow more likely to encounter a recoverable interruption, but they were not themselves an infinite loop. The unbounded behavior came from cross-run respawning.

## Remediation

- Add `scripts/start_word.py` as the only supported entrypoint for a new headword run.
- Scan remote branches for same-headword workflow manifests before delegating to `run_word.py`.
- If a guarded run is `in_progress`, fail with `resume_required` and return the branch/run path.
- If the latest guarded run is `budget_exhausted`, require explicit `--restart-after-budget-exhausted`; never reset the budget automatically.
- Fail closed when remote run state cannot be verified.
- Keep the dictionary-content specification, reviewer independence, liveness checks, blind antonym-axis adjudication and existing per-run budgets unchanged.

This remediation intentionally fixes liveness without weakening content-quality gates.
