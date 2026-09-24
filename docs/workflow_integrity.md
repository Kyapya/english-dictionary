# Review integrity and reliable publication

## Trust boundary

An agent ID, JSON schema, SHA-256, CI success, or zero findings alone does not
prove that an independent review actually happened. The dispatcher must preserve
the actual independent agent/provider response, without filling decisions from
templates or answer keys. Do not invent reviewer IDs, dates, findings, PASS rows,
or alternative wording merely to satisfy a liveness test. API credentials must
remain in their existing provider/connector boundary.

New runs declare `review_provenance_protocol: preserved_handoff_v1`. Handoff
ingestion preserves content-addressed copies of source responses, binds their
hashes, and compares substantive decisions with ingested outputs. Checker
attribution and both frame stages bind their own source records. Existing runs
without the new contract remain historical; they are not retroactively certified.
New changed runs cannot omit the protocol, or remove it on resume.

These checks detect missing, edited, or mismatched evidence, not a malicious
dispatcher fabricating both the response and its metadata. Independent execution
still requires actual separate review contexts. Preserve a transport/run receipt
where available; never describe local ingestion as proof of human review.
New runs also declare `review_response_protocol: self_attested_handoff_v1`.
The raw handoff response itself must contain its reviewer agent ID and model;
command-line metadata must match it. This prevents an anonymous response
template from being assigned a reviewer identity during ingestion. It remains a
self-declaration, so the dispatcher must still use a genuinely separate context.
Do not expose alignment keys, earlier findings, or expected answers to blind
reviewers. Final-blind and reconciliation retain the existing staged input rules.

Known defective evidence is registered in `audits/review_invalidations.json`.
Keep raw outputs and their historical claims; regenerate only the derived audit.
A registered invalidation cannot authorize checked/final status or publication,
even if the original final-review JSON says PASS. Status/queue metadata must
reflect needs_review. Content correction requires a separate authorized request.

## Start once, with a checked environment

Before creating a branch or run:

1. Run `python -X utf8 scripts/environment_preflight.py` using the installed
   interpreter explicitly if `python` is unavailable. Set `PYTHONUTF8=1` for
   child processes. Do not use a no-op fcntl shim; file_lock provides real locks
   on Windows and POSIX.
2. Use a short workspace, or enable `core.longpaths` locally on Windows. Preserve
   existing user changes. Check existing remote/control runs before starting.
3. Preserve the exact bytes of sealed evidence, including historical mixed EOLs.
   Existing Git attributes preserve raw artifacts; historical test archives
   explicitly disable autocrlf. New producers write UTF-8/LF. Never repair
   a hash mismatch by changing an expected hash without checking original bytes.
4. Choose authenticated Git or the connector before starting. Do not extract
   credentials, retry a known-unavailable transport, or change transport/branch
   to evade a permission refusal.

Use the shared start_words/start_word entrypoints and resume the same run.
Do not rebuild branches or resets to hide failed attempts. Do not regenerate the
whole dictionary export unless the requested publication actually needs it.

## Deterministic repair and resumption contracts

Source collection completion does not require article mapping that belongs to
comparison. Comparison and final publication still require complete union/claim
coverage and strictly ordered timestamps; partial invalid references are rejected.

Checker packets include the sense-section preamble in frequency context; qualification
also receives lexical relations so it can see each synonym/antonym score and sense. Editorial
ordinal frequency estimates are not corpus measurements. Unsupported factual claims,
regional/archaic overstatement, and invented statistics remain review defects.
New `check_pass_semantic_input_v2` hashes ignore only canonical located-line offsets;
text, order, semantic IDs, source bindings and specification hashes remain checked.
Historical markerless requests retain the original hash algorithm. For lexical
numeric-frequency-only revisions, the required plan narrows to qualification and
evidence, but no cache may be reused unless all existing reuse checks still pass.
This is not a promise that every such edit will require exactly two calls.

Missing checker finding IDs are derived deterministically in the indexing layer.
Never insert them into preserved reviewer responses. Concise final-review packets
include `review_trace_contract`: concrete finding notes count without a duplicate
40-character overall explanation; with no findings, retain one short concrete
overall observation. Boilerplate all-pass templates still fail. Notes, IDs and
hashes do not establish independent execution.

A lost frame-review context is not a reason to discard valid stage 1. The generated
stage-2 handoff includes a `sealed_stage1_replay_v1` receipt template. A genuinely
fresh independent reviewer uses its own agent ID/model and records the old agent
ID, sealed blind-record hash, immutable stage-2 request hash and replacement reason
in its raw response. The ingester verifies both preserved original responses and
their bindings; it never changes the stage-1 record or impersonates its author.
A replacement cannot be one of the other six checker contexts. The original
same-agent/model path remains compatible. Missing provenance is not certified by
inventing a receipt. Existing dispatch packets and raw records are not rewritten.

Workflow repair belongs in a separate infrastructure PR, not a word-generation
patch. Add executable regressions, keep old audit evidence untouched, and run the
normal validation matrix. The suspicion incident regressions are in
`tests/test_suspicion_workflow_regressions.py`; timings must be measured on future
real runs, not inferred from passing unit tests.

## Publish the complete checkpoint

Commit the intended entry, derived audit, raw evidence, completed workflow record,
and queue update together as required by the workflow. Do not omit mandatory
audit files to make a smaller request. Sealed blind evidence must be committed
before reconciliation; retain that sequence.

`publish_checkpoint.js` takes `(tools, root, repository, options)`, where
`options.python` is an existing interpreter path and `options.notify` receives
progress objects. It verifies that the destination matches origin and runs local
changed-content gates before the first upload. Shell quoting supports Windows
and POSIX without passing credentials.

The immutable transfer plan is paged from a local snapshot. Blob bytes are read
from Git and base64-encoded once, then paged from cache. Verified blobs, trees,
and commits are recorded after each success and reused on a later invocation.
The final receipt is accepted only after verifying remote ancestry and trees.
Progress contains paths/stages/counts, not article bytes. Keep one publisher
per branch; simultaneous invocations are not supported.

The connector adapter resolves branch and default-branch heads through the
GitHub connector and passes them into the local planner. The local planner must
not use `git ls-remote` or `git fetch` in connector mode. It compares the remote
base tree with the local base tree before creating a new branch and accepts a
receipt only when every planned local commit has a recorded connector commit.

Publication validation has two modes. `checkpoint` validates the workflow guard
state needed for an in-progress checkpoint. `merge-ready` runs the complete
content, checker, semantic, and source gates. `auto` selects checkpoint mode when
a changed workflow manifest is still in progress and merge-ready otherwise.
This allows sealed intermediate evidence to be published without pretending the
unfinished run already satisfies final publication gates.

If a completed run is found to contain synthetic final-review evidence, use
`repair_final_review_evidence.py` only when the article body and all sealed
pre-final inputs are unchanged. It rehearses normal ingestion in isolation,
archives the old request/response/output bytes, ingests a fresh independently
self-attested response, regenerates the derived audit, and records the repair.
It must never rewrite blind evidence or carry old PASS rows into the replacement.

Stage completion records a measured wall duration from
`orchestrator_state.stage_started_at` when no measured duration is supplied.
Do not enter `0` or `1` as a placeholder. Explicit durations are labelled
`reported`; automatic durations are labelled `measured_wall`, so performance
analysis can distinguish the measurement source.

On refusal, stop and report whether it was an execution-environment approval,
connector authorization, branch protection, or a transport error. Do not
attribute every refusal to GitHub. Do not automatically retry a denied write.
On an ordinary transport failure, inspect saved progress and remote state before
resuming. A changed HEAD creates a new snapshot; an advanced remote requires
reconciliation. Never force-update the ref.

Local transfer caches live in the Git directory, not tracked outputs; they can
contain the same data as the local repository and must be protected accordingly.

## Merge and verify the actual result

Run `python -X utf8 scripts/merge_preflight.py --base BASE --head HEAD --method merge`
against the exact PR head. It checks content and review-history requirements.
Changes containing blind/reconciliation outputs must use a merge commit, not
squash or rebase. Do not change protection settings to make a merge possible.
If only squash is permitted, stop and report the conflict.

After merging, verify the actual resulting commit, not only the PR check badge.
The validation workflow now runs on main pushes and checks changed review
chronology; Notion sync also checks that chronology before import. A successful
Notion-sync job means synchronization succeeded, not that independent review or
all content checks passed. Check validation and sync separately.

PR and push checks validate the changed review path. Manual workflow_dispatch
retains the existing full-history audit scan. At the incident baseline, that
scan already fails for nine other historical entries; do not hide those errors,
regenerate evidence to silence them, or confuse them with this change's tests.

Historical invalidated runs stay invalidated. A metadata-only demotion is not a
new successful reconciliation and does not require manufacturing a seal ancestor.
Existing published copies may require a separate authorized status update;
do not claim they changed merely because a local registry changed.
