# Independent content review A — compact_review_v1

Read the current article without the author's self assessment, prior findings, or
expected conclusions. Inspect every requested area for the coverage in
`compact_review_contract_v1.json`: sense boundaries and important constructions,
example ownership and Japanese translations, direction of use, lexical relation
axes, region/register, pronunciation, etymology. Check missing major uses across
the whole article. For an ambiguous example or antonym, compare candidate senses
before assigning it; do not require an antonym when none is natural.

Return JSON with `schema_version`, `checked_areas`, `unchecked_areas`, `findings`.
Each finding has `area`, `severity`, `impact`, `evidence`, `action`. Never invent a
pass reason for each normal item. Mark an area unchecked when you cannot judge it.
A substantive mistranslation is blocking even when the suggested fix is small.
Use `uncertainty` when the answer needs evidence; do not silently pass it.
