# Targeted adjudication: frequency-score sourcing

Return one independent `targeted_adjudication_v1` JSON record for issue
`TARGETED-FREQUENCY-SCORE-ROUND8`. Save it as
`frequency.targeted_adjudication.response.json` beside this request. Use your
own stable reviewer agent ID. Do not edit the article.

## Question

Does the current article's shared disclosure, together with `entry_spec_v5`,
resolve the seven evidence findings below that object to the absence of
dictionary-provided numeric frequency data? If not, state the specific change
or support needed for these current ratings.

## Current text and ratings

The article says: “この節の各語義・類義語の頻度スコアは、英語全体での遭遇頻度を
entry_spec_v5 の10段階基準に照らした編集上の定性的推定である。厳密なコーパス集計値や
辞書掲載の数値ではなく、地域・専門・古風な用法を過大評価しない目安として付けている。
類義語のスコアは、各項目の「定義」に示す意味に限る。”

The current 3 sense ratings are 8/10, 7/10, and 2/10. The current 4 synonym
ratings are doubt 8/10, distrust 8/10, hint 8/10, and trace 8/10. The article
does not claim these values are corpus measurements.

## Applicable specification

`prompts/entry_spec_v5.md` requires ratings for each sense and each synonym,
restricted to the meaning in the item's definition, on an absolute English-wide
scale. It says that when strict statistical support is unavailable, apply the
10-point rubric consistently and do not overrate regional or archaic senses.
The bands are 10 very high; 8–9 high; 6–7 medium; 4–5 low-to-medium; 2–3 low;
1 rare.

## Current evidence finding

The independent round-8 evidence pass reports seven blocking
`evidence_claim_mismatch` findings for the exact seven values listed above.
Its rationale for each is that the opened Oxford/Merriam-Webster suspicion
entries provide definitions, usage labels, examples, or a synonym relation, but
do not publish a numeric frequency measure or an 8/10, 7/10, or 2/10 scale.
The evidence pass does not allege that a value contradicts an observed numeric
source or that its placement in the rubric band is demonstrably wrong.

## Earlier targeted decision

An independent round-5 adjudication on a prior, 4-sense/5-synonym draft decided
`resolved_needs_change`: it found that lack of numeric dictionary data alone
was not a blocker under the same specification, but the then-current disclosure
covered only senses 1–2 and omitted senses 3–4 and all five synonym ratings.
The article has since been reduced to three senses/four synonyms and now has the
shared disclosure quoted above, which explicitly covers both categories and
labels the values as estimates. Reassess the present seven findings and current
disclosure rather than repeating the prior scope conclusion mechanically.

## Output contract

Return exactly one JSON object with schema `targeted_adjudication_v1`, fields
`issue_id`, `reviewer.agent_id`, `decision` (`resolved_correct`,
`resolved_needs_change`, or `insufficient_evidence`), `rationale`, and
`applicable_scope`. Keep the rationale specific to the current seven values and
the current note. Do not inspect or discuss any blind alignment record or key.
