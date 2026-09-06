# Independent review handoff

Stage: `final_review`

The response must be one JSON object matching `final_review_v2`. Run this in a separate model session; do not use the generation session.

## Current input binding

- entry body SHA-256: `22f45936b17d73702e084f80c1c2bf69e594dca053207f1eefe5670a1ba60310`
- sealed final-blind output SHA-256: `5a4c3ad9f425440282bd96469d553a1c75470469bdb30047e9c817273f88ec18`
- run/context: `blind-intense-20260905T152653Z-81cda47a-final` / `blind-intense-context-20260905T152653Z-81cda47a-final`
- targets: 42
- relations: 27
- normal candidates: 0
- blind candidates: 10
- findings: F001-F004
- evidence links: EVID-001-EVID-010
- source unions: U-001-U-009

Evaluate every target, relation, candidate, finding, evidence link, and source union. PASS only when every item passes and blockers is empty. Do not edit the entry.
