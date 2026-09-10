# Text storage and audit hashes

New generated Markdown and JSON use UTF-8 without a BOM and LF line endings.
Production text writers explicitly set `encoding="utf-8", newline="\n"`;
binary writers keep their existing UTF-8 serialization. This fixes the bytes
before hashing, not after an audit has been sealed. Text readers must also use
explicit UTF-8 rather than the host's default encoding.

`.gitattributes` checks out specifications in `prompts/` as LF on every OS, so
specification hashes computed from disk match their Git blobs. Existing clones
may still have CRLF files from an earlier checkout: use a fresh checkout/worktree
for new runs after this change. Changing attributes alone does not rewrite files
already present on disk. Do not refresh inputs of an in-progress or sealed run
merely to change their line endings.

Audit, entry, process-improvement, queue, backup, and historical fixture paths
use `-text`: Git stores and checks out their exact bytes, including old CRLF or
mixed-EOL artifacts. New files in these paths still use LF because their writers
set it explicitly. `.editorconfig` supplies UTF-8/LF defaults for new edits without
adding a final newline or stripping trailing whitespace from hash-bound content.

Do not run repository-wide `git add --renormalize`, rewrite historical evidence,
or update old hashes to accommodate a checkout conversion. Existing byte hashes,
JSON canonical hashes, and frozen-input checks retain their current semantics.
