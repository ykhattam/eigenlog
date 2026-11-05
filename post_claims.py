"""post_claims.py: every claim in the LinkedIn post, with an honest status.
A claim is "verified" only if the check beside it runs and passes. Run this file
to re-check them; it stops with an error if a verified claim stops being true.
It writes claims.md, which the README links to.
"""
from eigenlog import Mind, WORLD, flatten
import os

n_categories = len(WORLD)
n_words = len(set(flatten(WORLD)))
PUBLIC = {name for name in dir(Mind) if not name.startswith("_")}

def rejects_typo():
    try:
        Mind().define("inclusive reason", "x")
    except ValueError:
        return True
    return False

def accepts_wrong_definition():
    m = Mind()
    m.define("measured truth", "a feeling")
    return m.definitions["measured truth"] == "a feeling"

def catches_repeat():
    m = Mind()
    m.world["art"].append("stars")
    return "stars" in m.overlaps()

def minds_are_independent():
    a, b = Mind(), Mind()
    a.park("dreams")
    return b.world["other"] == [] and WORLD["other"] == []

def verified_needs_working():
    try:
        Mind().claim("x", "verified")
    except ValueError:
        return True
    return False

def no_stray_spaces():
    return all(w == w.strip() for w in flatten(WORLD))

def doubt_stays_as_history():
    m = Mind()
    i = m.reflect("x", "y", doubt="why?")
    m.resolve_doubt(i, "because")
    return m.entries[i]["doubt"] == "why?" and m.entries[i]["resolved"]

CLAIMS = [
    (f"The map has {n_categories} categories and {n_words} words.", "verified", "counted by flatten()", "ran it", lambda: n_categories > 0 and n_words > n_categories),
    ("The code rejects a misspelt term.", "verified", "define('inclusive reason') raises ValueError", "ran it", rejects_typo),
    ("The code accepts a well-formed but wrong definition.", "verified", "define('measured truth', 'a feeling') is stored", "ran it", accepts_wrong_definition),
    ("The code catches a word placed in two categories.", "verified", "overlaps() after adding 'stars' to art", "ran it", catches_repeat),
    ("Two minds do not share a map.", "verified", "park() on one leaves the other unchanged", "ran it", minds_are_independent),
    ("A resolved doubt stays in the log as history.", "verified", "entry keeps its doubt text and is marked resolved", "ran it", doubt_stays_as_history),
    ("A claim marked verified must carry a test and a source.", "verified", "claim('x', 'verified') raises ValueError", "ran it", verified_needs_working),
    ("No word in the map has a stray leading or trailing space.", "verified", "every word from flatten() equals its stripped form", "ran it", no_stray_spaces),
    ("The code does not model links between categories.", "verified", "Mind has no links attribute", "ran it", lambda: not hasattr(Mind(), "links")),
    ("No function in the code addresses why we exist.", "verified", "the public methods are only the ones listed here", "ran it", lambda: PUBLIC == {"reflect", "claim", "define", "resolve_doubt", "surprise", "read", "open_doubts", "change", "human", "known", "orphans", "overlaps", "park", "pressure", "query", "save"}),
    ("The shipped demo log is invented, not a record of real days.", "verified", "the demo says so in its comments", "read the file", lambda: "invented" in open(os.path.abspath(__file__).replace("post_claims.py", "eigenlog.py")).read()),
    ("Careful analysis cuts some errors, such as unclear words and inconsistent claims.", "unverified", "compare logged errors before and after using the habits", "author", None),
    ("Careful analysis does not cut wrong premises or missing data.", "unverified", "the code accepts a wrong definition, which shows one case, not the general rule", "author", None),
    ("Logic clarifies the frameworks we think in.", "unverified", "no test proposed", "author", None),
    ("Logic cannot supply values.", "contested", "close to the is-ought gap; readings of Hume differ", "author", None),
    ("A definition plus its applicability is wisdom.", "contested", "accounts of wisdom differ", "author", None),
    ("Writing, painting, sport, conversation and singing carry weight that logic does not.", "contested", "depends on what 'weight' means", "author", None),
    ("Python and pandas practice with Claude made a good tool for reflection.", "unverified", "log real days for a month, then review", "author", None),
    ("Regular reflection helps make sense of an uncertain world.", "unverified", "self-report; no comparison made", "author", None),
    ("The map is meant to help me navigate.", "unverified", "an intention, not a result", "author", None),
    ("The map includes value-laden words that are the author's own choices.", "contested", "for example 'evil', 'egoism > altruism', 'obsession'", "author", None),
]

if __name__ == "__main__":
    mind = Mind()
    for text, status, test, source, check in CLAIMS:
        if status == "verified":
            assert check is not None and check(), f"verified claim failed: {text}"
        mind.claim(text, status, test, source)
        
    order = ["verified", "unverified", "contested"]
    lines = ["# Claims in the post, with status", "",
             "Verified means the check ran and passed (`python post_claims.py`). ",
             "Unverified means untested. Contested means informed people disagree.", ""]
             
    for status in order:
        lines += [f"## {status.capitalize()}", ""]
        for c in mind.claims:
            if c["status"] == status:
                lines += [f"{c['text']} Checked by: {c['test']} ({c['source']}).", ""]
                
    with open("claims.md", "w") as f:
        f.write("\n".join(lines))
    counts = {s: sum(c["status"] == s for c in mind.claims) for s in order}
    print(counts)