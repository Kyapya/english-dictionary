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
