# process-refactor-v1 E2E trial: distinct

- Date: 2026-08-25
- Workflow run: `audits/workflow_runs/distinct/20260825T131103Z-34ac3453.json`
- Cycle directory: `audits/runs/d/distinct/20260825T131103Z-34ac3453/`
- Selected queue word: `distinct` (new `pending` row selected from a previously requested but unqueued headword)
- Profile: standard
- Status: completed (`checked`, final decision `pass`)

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
| cold_review | 1,419 | 32,748 | 150 | 1 | 0 |
| final_blind | 1,735 | 32,748 | 240 | 0 | 0 |
| blind_seal | 0 | 18,785 | 1 | 0 | 0 |
| finding_resolution | 1,492 | 79,756 | 60 | 0 | 0 |
| final_review | 3,065 | 81,827 | 420 | 0 | 0 |
| status_update | 0 | 4,710 | 15 | 0 | 0 |
| export | 0 | 14,508 | 5 | 0 | 0 |

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

The context-free cold reviewer returned one low-severity observation about `distinct` and `identical` being compatible when different identity criteria are used. Resolution rejected it as an applicable defect because the entry's antonym comparison is explicitly scoped to sameness in the relevant qualitative or classificatory respects; token nonidentity versus qualitative identity changes the comparison axis. The sealed final-blind reviewer independently found no blocker, and the same final run accepted this resolution after checking all 114 targets, 66 relations, 31 blind assertions, 13 evidence links, and 13 source unions.

## Integration defect exposed by the trial

The initial checker bundle included an invented trailing newline in its body hash while final-manifest generation did not. This made an unchanged body appear stale across stages. `scripts/check_passes.py` now uses the same canonical body hashing as `scripts/generate_audit_manifest.py`, with a regression test in `tests/test_check_passes.py`.

The trial also exposed a raw-schema mismatch: the cold prompt intentionally emits open-ended `high/medium/low` findings with quote-anchored `scope_anchors`, while the new manifest generator initially forced the taxonomy schema used by checker/final-blind findings. The generator now validates and preserves the native cold schema separately, with a non-empty-finding regression test.

## Final result

- Workflow duration: 2,819.65 seconds (46 minutes 59.65 seconds), within the 60-minute standard deadline.
- Total cycles: 1
- Total revisions: 3
- Final decision: `pass`
- Entry/queue status: `checked`, `checked: true`
- Revision markdown snapshots generated: 0
- Canonical audit: `audits/d/distinct.json`, generated from raw JSON only
- Export completed: `exports/dictionary_all.md`, `exports/dictionary_index.csv`
