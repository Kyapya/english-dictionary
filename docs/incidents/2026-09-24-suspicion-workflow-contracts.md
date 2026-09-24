# Suspicion workflow contract repair — 2026-09-24

Baseline: main `92ae3e31877786b7b051038d83a8a447ed5153e4`.
Incident evidence: PR #179 (`words/suspicion-20260911`), head
`601cdf6a674089c89052f414f0a0d8f44a1c2c85`, run
`audits/runs/s/suspicion/20260911T033430Z-c12c3ef3`.

## Defects and executable regressions

- Inventory completion required downstream article comparison: separate the phase
  prerequisite while preserving final coverage and timestamp validation.
- Concise final-review notes contradicted an arbitrary 40-character liveness test:
  share the visible trace contract, accept concrete finding notes, reject empty or
  stock all-pass templates, retain independent raw-response/coverage requirements.
- The sense preamble was omitted from checker input: preserve it with frequency
  context; clarify editorial estimates without excusing false statistical claims.
- Checker findings without optional IDs caused final indexing failure: derive stable
  IDs in all final indexing views without rewriting original reviewer evidence.
- Coarse lexical edits invalidated six passes: recognize exact numeric frequency
  replacements separately. Any actual cache reuse still needs all hash and review
  checks; meaning, example, structure and unclassified edits retain conservative
  invalidation. Ignore only canonical line offsets in versioned new input hashes.
- A lost frame-review context forced stage 1 to be repeated: support sealed-stage1
  replay by a fresh independent stage-2 reviewer, retaining actual IDs, both raw
  responses, receipt bindings, original blind inference and the other six results.

These cases are covered by `tests/test_suspicion_workflow_regressions.py` alongside
the existing tests. No entry, queue, audit, export, or suspicion status is changed
by this infrastructure repair. It does not complete or certify PR #179. No speedup
factor or maximum generation time has yet been measured for the repaired workflow.
