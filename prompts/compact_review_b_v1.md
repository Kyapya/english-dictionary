# Independent source review B — compact_review_v1

Open the primary external source locators in the supplied evidence packet. Compare
the article, claim units, definitions, example usage and scope directly to those
sources, rather than repeating the author's inventory summary. Look for missing
major senses and unsupported generalizations. Distinguish contradiction, source
not accessible, and genuine uncertainty. Two independent principal dictionaries
are the baseline; targeted extra research is driven by an unresolved important
claim. Do not delete useful checked evidence merely to meet a source count.

Return JSON with `schema_version`, `checked_areas`, `unchecked_areas`, `findings`.
Each finding has `area`, `severity`, `impact`, `evidence`, `action`. Source
inaccessibility or unsupported major content is blocking until resolved or
properly limited. Do not produce a normal-reasons table or copy a hash into the
response.
