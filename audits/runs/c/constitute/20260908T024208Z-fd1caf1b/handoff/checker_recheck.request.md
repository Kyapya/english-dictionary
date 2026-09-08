# Independent checker recheck handoff — parallel fan-out

Stage: `checker_recheck`

Deterministic blind seed: `20260908T024208Z-fd1caf1b:checker_recheck`

Launch the seven requests concurrently with one independent subagent per pass. Do not concatenate specifications. The frame-relation pass requires its same-subagent stage 2 after the seven stage-1 responses are fanned in.

## Fan-out files

- `translation`: `checker_recheck.translation.request.md` -> `../recheck/translation.response.json`
- `sense-structure`: `checker_recheck.sense-structure.request.md` -> `../recheck/sense-structure.response.json`
- `frame-relation`: `checker_recheck.frame-relation.request.md` -> `../recheck/frame-relation.response.json`
- `example-attribution`: `checker_recheck.example-attribution.request.md` -> `../recheck/example-attribution.response.json`
- `qualification`: `checker_recheck.qualification.request.md` -> `../recheck/qualification.response.json`
- `pronunciation`: `checker_recheck.pronunciation.request.md` -> `../recheck/pronunciation.response.json`
- `evidence`: `checker_recheck.evidence.request.md` -> `../recheck/evidence.response.json`
