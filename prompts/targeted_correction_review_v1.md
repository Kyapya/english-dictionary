# Targeted correction review v1

## Purpose

This review is only for a user-requested, localized correction to an entry that was already `checked` or `final` before the correction. It is intentionally not a normal review, cold review, final blind review, or final review.

The goal is to verify the requested correction and make sure the changed text does not create an obvious local contradiction. Untouched parts of the entry are out of scope.

## Inputs

Review only:

1. the user's correction request;
2. the unified diff for the changed entry;
3. the smallest surrounding context needed to understand each changed hunk.

Do not request or re-read the entire entry merely to look for unrelated defects. Do not restart source-first research for unchanged claims. If a changed claim itself needs factual verification, verify that claim only.

## Checks

For every changed hunk, confirm all of the following:

- the requested correction was actually applied;
- the replacement is factually and linguistically sound;
- examples, translations, labels, and explanations changed in that hunk agree with each other;
- the change does not create an obvious contradiction with immediately adjacent text;
- no unrelated rewrite was introduced in the same hunk.

If the user requested several specific corrections in one entry, all of those changed hunks may be reviewed in this single targeted pass.

## Stop rule

Return `pass` once every requested correction passes the checks above. Do not escalate to checker passes, cold review, final blind, final review, finding resolution, or a fresh full-entry audit merely because the entry changed.

Use the standard workflow instead when the request is a broad rewrite, a full re-evaluation, a large sense reorganization, or when the base entry was not already `checked`/`final`.

## Record contract

A passing targeted review is recorded under `audits/targeted_corrections/<slug>/` with:

- `schema_version: targeted_correction_v1`
- the changed `entry_path`
- hashes binding the base body, corrected body, and reviewed diff
- the user's requested correction scope
- `review.scope: changed_hunks_and_local_context`
- a non-empty `review.reviewer`
- `review.verdict: pass`

The record is an audit receipt for the scoped check; it is not evidence that untouched entry content was re-reviewed.
