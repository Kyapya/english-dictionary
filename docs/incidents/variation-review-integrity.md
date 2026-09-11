# variation review-evidence incident

Affected PR: https://github.com/Kyapya/english-dictionary/pull/166

Merged commit: `a2292f71b5e9984d22a2f8d5781f82a5a7431571`

Affected run: `audits/runs/v/variation/20260910T142432Z-faa7c659`

## Confirmed findings

- The task-local creation helper copied `assigned_sense_id` from the example
  alignment key into the allegedly blind classifications. It used the first
  four words of each example as a mechanically generated justification.
- It synthesized final PASS rows and reused normal inventory candidates for
  the purportedly independent inventory. Some real earlier agent reviews
  improved the draft, but do not authenticate these final raw records.
- Workflow completion is recorded before several raw review timestamps.
  These historical timestamps must not be rewritten into a plausible order.
- PR history was reconstructed to retain a sealed-blind ancestor, then squash
  merging removed that ancestry from main. PR CI passed, but the actual merged
  chronology check fails. The post-merge green run was Notion sync.
- Publication retries rebuilt branches/resent objects. Removing required audits
  caused a predictable missing-completed-workflow CI failure. The transport
  repeatedly read/encoded whole blobs for each page and lacked durable progress.
- Windows archive newline conversion caused sealed hash/specification mismatches;
  missing Python/fcntl and long paths were discovered after work had begun.
- An execution-environment approval rejection was incorrectly described as
  a GitHub safety review. User confirmation was not the primary missing input.

## Remediation boundary

The user requested workflow/integrity fixes without article-text correction.
The article body is preserved. Only checked/status metadata and its queue row
are demoted to needs_review/false. Original raw files and the workflow history
remain forensic evidence. The invalidation registry and derived audit make the
historical PASS unusable as publication authorization.

The task-local synthetic helper has been disabled at its entrypoint and retained
for forensics. It is not a supported repository workflow. Do not rebuild a
replacement PASS, backdate records, or request a blind reviewer to confirm the
known answer key. A future genuine review must retain its actual responses.

Known article issues remain open by user instruction: musical variations versus
separate works, the wording example's sense placement, etymological direction,
article-bearing construction templates, duplicate genetic-variation collocations,
and the stated scope of specialized senses. These are not marked corrected.

Implementation and operating procedure: [workflow integrity](../workflow_integrity.md).
Hash bindings and pattern detectors improve evidence integrity but are not
cryptographic attestation that an independent model actually executed.
