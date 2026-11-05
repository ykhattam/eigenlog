# Claims in the post, with status

Verified means the check ran and passed (`python post_claims.py`). 
Unverified means untested. Contested means informed people disagree.

## Verified

The map has 18 categories and 109 words. Checked by: counted by flatten() (ran it).

The code rejects a misspelt term. Checked by: define('inclusive reason') raises ValueError (ran it).

The code accepts a well-formed but wrong definition. Checked by: define('measured truth', 'a feeling') is stored (ran it).

The code catches a word placed in two categories. Checked by: overlaps() after adding 'stars' to art (ran it).

Two minds do not share a map. Checked by: park() on one leaves the other unchanged (ran it).

A resolved doubt stays in the log as history. Checked by: entry keeps its doubt text and is marked resolved (ran it).

A claim marked verified must carry a test and a source. Checked by: claim('x', 'verified') raises ValueError (ran it).

No word in the map has a stray leading or trailing space. Checked by: every word from flatten() equals its stripped form (ran it).

The code does not model links between categories. Checked by: Mind has no links attribute (ran it).

No function in the code addresses why we exist. Checked by: the public methods are only the ones listed here (ran it).

The shipped demo log is invented, not a record of real days. Checked by: the demo says so in its comments (read the file).

## Unverified

Careful analysis cuts some errors, such as unclear words and inconsistent claims. Checked by: compare logged errors before and after using the habits (author).

Careful analysis does not cut wrong premises or missing data. Checked by: the code accepts a wrong definition, which shows one case, not the general rule (author).

Logic clarifies the frameworks we think in. Checked by: no test proposed (author).

Python and pandas practice with Claude made a good tool for reflection. Checked by: log real days for a month, then review (author).

Regular reflection helps make sense of an uncertain world. Checked by: self-report; no comparison made (author).

The map is meant to help me navigate. Checked by: an intention, not a result (author).

## Contested

Logic cannot supply values. Checked by: close to the is-ought gap; readings of Hume differ (author).

A definition plus its applicability is wisdom. Checked by: accounts of wisdom differ (author).

Writing, painting, sport, conversation and singing carry weight that logic does not. Checked by: depends on what 'weight' means (author).

The map includes value-laden words that are the author's own choices. Checked by: for example 'evil', 'egoism > altruism', 'obsession' (author).
