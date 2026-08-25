# process-refactor-v1 E2E trial: distinct

- Date: 2026-08-25
- Workflow run: `audits/workflow_runs/distinct/20260825T131103Z-34ac3453.json`
- Cycle directory: `audits/runs/d/distinct/20260825T131103Z-34ac3453/`
- Selected queue word: `distinct` (new `pending` row selected from a previously requested but unqueued headword)
- Profile: standard
- Status: in progress

## Research and source-first cost

- Search queries: 12 / 12
- Candidate pages: 11 / 18
- Adopted sources: 6 / 6
- Atomic source facts: 19 / 48
- Research rounds: 2 / 2
- Coverage axes closed: 6 / 6

## Completed stage measurements

| stage | instruction bytes | input bytes | duration seconds | defects detected | revisions |
|---|---:|---:|---:|---:|---:|
| generation | 52,602 | 8 | 420 | 0 | 1 |
| mechanical_validator | 0 | 29,999 | 1 | 0 | 0 |
| checker_passes | 0 | 205,583 | 720 | 9 | 2 |

Checker input is the aggregate across six separately executed section-limited passes. Each pass loaded only its own v6 specification; no execution loaded all pass specifications together.

## Normal-review defects and resolutions

| owner pass | detected issue | resolution in latest entry |
|---|---|---|
| sense-structure | The independently attested botanical meaning “separate/free, not fused” was absent. | Added a fifth, domain-labelled botanical sense with frames, examples, usage boundary, and relations. |
| frame-relation | `independent`, `overlapping`, and `uncertain` were labelled as direct lexical relations although their opposition or synonymy was only contextual. | Removed all three relation blocks. |
| frame-relation | Two grammar frames were described without a representative collocation/example. | Removed the unrepresented frames rather than widening the entry. |
| frame-relation | One extracted-frame explanation overstated what a displayed pattern encoded. | Reworded the explanation to match the visible frame. |
| qualification | SQL `DISTINCT` was called a reserved word. | Narrowed the claim to the conventional term “keyword.” |
| evidence | Unnecessary comparisons with `distant` and `extinct` lacked a direct evidence link. | Removed the comparisons from the pronunciation section. |

After these corrections, `scripts/validate_entry.py` passes and all six v6 checker result files contain no unresolved finding. The source-first v2 pre-final gate also passes.

## Integration defect exposed by the trial

The initial checker bundle included an invented trailing newline in its body hash while final-manifest generation did not. This made an unchanged body appear stale across stages. `scripts/check_passes.py` now uses the same canonical body hashing as `scripts/generate_audit_manifest.py`, with a regression test in `tests/test_check_passes.py`.

## Remaining stages

- cold review (context-free)
- final blind review and seal (context-free)
- finding resolution and final reconciliation
- status update and export
- final CI validation
