# Round 13 frame-relation serial recovery

Attempt 1 was rejected because its raw stage-1 response carried an incorrect request digest. The raw response and dependent stage-2 artifacts are preserved under `attempt-1-unaccepted/` and excluded. Six independent round-12 passes remain valid. Attempt 2 uses a fresh reviewer for both blind stages.

- Canonical stage-1 request: `frame-relation.request.md` (`frame-relation.request.json`)
- Attempt 1 disposition: `frame-relation.stage1.correction-required.json`
- Attempt 1 archived response and dependent artifacts: `attempt-1-unaccepted/`
- Attempt 2 plan: `attempt-2-plan.json`

Attempt 2 stage-1 response received and validated: `/root/frame14_retry` / `GPT-6`, request digest `8846e60a4bd98aef02fddd11ee833adb9713472d96f19a6ea8486dafc68cefd1`, response SHA-256 `74d2be21ea19776cb626a6c3693ab9e76d2f2ebe094853629ce23851041202cb`. It is in `checker_passes.stage1.json`; stage 2 remains withheld until this exact checkpoint is connector-published.
