# Round 13 frame-relation serial recovery

The canonical stage-1 request is connector-published and bound to candidate body `e0cdcd7c…`. Attempt 1 failed its request binding and remains quarantined under `attempt-1-unaccepted/`. Attempt 2 produced a valid, published stage-1 response, but its reviewer was unavailable for stage 2; its response and checkpoint are preserved under `attempt-2-valid-stage1-no-stage2/` and excluded from the final pass.

Attempt 3 stage 1 was accepted and connector-published before the alignment key or stage-2 request was created. Both stages use reviewer `/root/round13_frame_recovery` (`GPT-6`). The stage-2 packet now awaits connector publication.

- Canonical request: `frame-relation.request.md` (`frame-relation.request.json`)
- Attempt 1: `attempt-1-unaccepted/`
- Attempt 2: `attempt-2-valid-stage1-no-stage2/`
- Attempt 3 plan: `attempt-3-plan.json`
- Attempt 3 stage 1: `frame-relation.stage1.response.json`
- Attempt 3 alignment key: `frame-relation.antonym-axis.alignment-key.json`
- Attempt 3 stage-2 packet: `frame-relation.stage2.request.md` (`frame-relation.stage2.request.json`)
