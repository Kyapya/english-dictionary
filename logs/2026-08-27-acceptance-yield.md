# Yield review-independence acceptance (2026-08-27)

## Status

BLOCKED — the one-time mode-I review could not be executed because this environment provides neither `DICT_REVIEW_API_KEY` nor `DICT_REVIEW_MODEL`.

## Completed prerequisites

- Acceptance fixture: `tests/fixtures/acceptance/yield_defective.md`
- Expected D1–D8 mapping: `tests/fixtures/acceptance/yield_defective_expected.json`
- Executable entrypoint: `python scripts/run_word.py yield --acceptance`
- Mechanical B5 result: D3 and D4 detected; an additional `yield place to` heading/frame mismatch was also detected.
- Old run invalidation: `20260826T131200Z-yield02` produces B1, B2, B3, and B4 invalidation reasons.
- Publication state: `entries/y/yield.md` and its queue row were demoted to `needs_review / checked: false` because B1–B3 require correction; the derived audit records the liveness invalidation while preserving the old raw files.

## Not claimed

No external reviewer model was called, so D1–D2 and D5–D8 have not been scored by the acceptance procedure and the acceptance result is not PASS. The criteria were not lowered and handoff mode was not substituted for the required mode-I run.

Because acceptance is blocked, the defective article body was not corrected and was not returned to `checked`.
