# Round 11 independent checker handoff

Run all seven pass requests concurrently with one independent reviewer per pass. Keep the frame-relation stage-1 agent for its stage-2 follow-up. Do not inspect or reveal any alignment key before the stage-1 checkpoint is committed and connector-published.

- `translation`: `translation.request.md` → `translation.response.json`
- `sense-structure`: `sense-structure.request.md` → `sense-structure.response.json`
- `frame-relation`: `frame-relation.request.md` → `frame-relation.stage1.response.json`
- `example-attribution`: `example-attribution.request.md` → `example-attribution.blind-record.json`
- `qualification`: `qualification.request.md` → `qualification.response.json`
- `pronunciation`: `pronunciation.request.md` → `pronunciation.response.json`
- `evidence`: `evidence.request.md` → `evidence.response.json`
