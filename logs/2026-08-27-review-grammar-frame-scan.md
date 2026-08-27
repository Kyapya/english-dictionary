# Grammar-frame consistency scan (2026-08-27)

## Scope

Applied `validate_entry.grammar_frame_diagnostics` to every `entry_spec_v5` article whose status is `checked` or `final`.

## Result

- Articles scanned: all checked/final v5 entries in `entries/`
- Articles with findings: 1
- Findings: 5
- Manually confirmed false positives: 0

All five findings are in `entries/y/yield.md`:

1. Sense 4 is intransitive-only but contains `yield oneself to ...`.
2. Sense 5 is intransitive-only but contains `yield the right of way to ...`.
3. Sense 5 is intransitive-only but contains `yield precedence to ...`.
4. Sense 5 is intransitive-only but contains `yield the floor to ...`.
5. Sense 7 is intransitive-only but contains `yield place to ...`.

Items 1–4 cover requested defects D3 and D4. Item 5 is an additional instance of the same heading/frame contradiction. The first scan also flagged passive `cast` frames and infinitival `deserve to ...` complements; those were confirmed as heuristic false positives and the classifier was narrowed before this final measurement.

Legacy entries created before the enforcement date are measured but not retroactively blocked by the format CLI. The same diagnostics are blocking for entries created on or after 2026-08-27, regardless of current status, so a new workflow cannot pass through the inconsistency before gaining checked status.
