# Round 13 frame-relation serial recovery

Attempt 1 was rejected because its raw stage-1 response carried an incorrect request digest. The raw response and dependent stage-2 artifacts are preserved under `attempt-1-unaccepted/` and excluded. Six independent round-12 passes remain valid. Attempt 2 uses a fresh reviewer for both blind stages.

- Canonical stage-1 request: `frame-relation.request.md` (`frame-relation.request.json`)
- Attempt 1 disposition: `frame-relation.stage1.correction-required.json`
- Attempt 1 archived response and dependent artifacts: `attempt-1-unaccepted/`
- Attempt 2 plan: `attempt-2-plan.json`
