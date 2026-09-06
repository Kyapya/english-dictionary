# Independent review handoff — parallel checker fan-out

Stage: `checker_passes`

Protocol: `parallel_checker_v1`

Launch all seven request files below concurrently, one independent subagent per pass. Do not concatenate the seven checker specifications. Wait for all seven response files before ingestion. The coordinator performs only mechanical validation/fan-in; it must not synthesize missing checker responses.

Parallel execution does not pause the workflow guard: keep the normal heartbeat/checkpoint discipline while the subagents are running, and stop rather than silently restarting if the run budget is exhausted.

The `frame-relation` worker performs its blind stage 1 now; after fan-in the coordinator generates a stage-2 request that must go back to that same subagent. The other six passes do not rerun.

## Fan-out files

- `translation`: `checker_passes.translation.request.md` -> `checker_passes.translation.response.json`
- `sense-structure`: `checker_passes.sense-structure.request.md` -> `checker_passes.sense-structure.response.json`
- `frame-relation`: `checker_passes.frame-relation.request.md` -> `checker_passes.frame-relation.response.json`
- `example-attribution`: `checker_passes.example-attribution.request.md` -> `checker_passes.example-attribution.response.json`
- `qualification`: `checker_passes.qualification.request.md` -> `checker_passes.qualification.response.json`
- `pronunciation`: `checker_passes.pronunciation.request.md` -> `checker_passes.pronunciation.response.json`
- `evidence`: `checker_passes.evidence.request.md` -> `checker_passes.evidence.response.json`
