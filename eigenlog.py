"""eigenlog.py: a mind you can run.
It keeps a map of the world, a log of reflections, a register of claims, and a
record of what did not fit the map. It cannot detect unknown unknowns: by
definition, they cannot be looked up. It records the symptoms of one: concepts
with no home, surprises, and a residual list that keeps growing.
"""
import copy                      # copy.deepcopy makes an independent copy
import sqlite3                   # SQL, built into Python
from datetime import date        # "from X import Y" takes one name from a library
import pandas as pd

# ---------------------------------------------------------------- the map ---
UNKNOWN = None            # exists, not yet known
NOT_APPLICABLE = "n/a"    # does not exist in this case
STATUSES = ("verified", "unverified", "contested")
COLUMNS = ["id", "when", "subject", "observation", "measure", "doubt", "struggle", "resolved"]

WORLD = {
    "body": {
        "human": ["organs", "emotions", "thoughts", "behaviours"],
        "brain": ["amygdala", "prefrontal cortex", "eyes", "neurons"],
    },
    "family": {
        "pa": UNKNOWN, "ma": UNKNOWN, "g-ma": UNKNOWN,
        "g-pa": UNKNOWN, "step-pa": NOT_APPLICABLE, "sis": UNKNOWN,
    },
    "universe": ["planets", "animals", "aliens", "stars"],
    "quant": ["maths", "ratio", "measured truth"],
    "qual": ["feel", "beauty", "texture", "touch"],
    "frameworks": ["subject", "variables", "parameters", "debatable inputs"],
    "culture": ["subconscious", "repeated stories", "ancient civilisation", "accumulated wisdom"],
    "electronics": ["functions", "surveillance", "tech", "binaries", "high systems"],
    "bias": ["value judgement", "positivism", "acceptance", "rights", "pre-existing catechism"],
    "art": ["words", "painting", "sports", "program"],
    "time": {"past": 1, "present": 0, "future": -1},
    "meaning": ["metaphor", "logic", "illogic", "interpreted truth", "phone: a universe portal in a universe"],
    "data": list(STATUSES),
    "love": {
        "feelings": ["strong feelings", "attraction", "obsession"],
        "conduct": ["care", "duty", "discipline", "big heart"],
        "what happens": ["hurt", "surprise", "delayed reciprocity"],
        "why": ["inclusive reasons"],
    },
    "grief": ["repeated reminiscence", "nostalgia", "missing for the individual", "wishful idealism of the person"],
    "betrayal": ["indirect sensitive information", "action < words", "egoism > altruism", "disrespect for time", "devaluation of the partner", "inequitable representation of reality"],
    "real experience": ["much unquantifiable data", "pronunciation", "self-behaving", "movement", "intersection of emotions with body"],
    "other": [],     # the residual: whatever fits nowhere yet
}

# The human side: one person, described by the map's own words.
HUMAN = {
    "gender": UNKNOWN,
    "value": "okay",                                              # good | okay | evil
    "quant": ["money", "critical thinking", "illusory useful tools"],
    "qual": ["looks", "mental state", "real experience"],
    "ethics": ["care", "deontology", "consequence"],              # lenses, not options
}

# Read as a sequence: a prior (bias), then what exists, then what arrives, then the response.
THOUGHTS = ["bias", "available data", "context", "receipt of data", "reaction"]

def flatten(node):
    """Yield every key and every text value inside a nested structure."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from flatten(value)      # the function calls itself: recursion
    elif isinstance(node, list):
        for item in node:
            yield from flatten(item)
    elif isinstance(node, str):
        yield node

# --------------------------------------------------------------- the mind ---
# class defines a new kind of thing. Mind() builds one. Each Mind keeps its own
# lists, so a personal mind and a work mind never bleed into each other.
class Mind:
    """One mind: a map, a log, a claims register and a record of what did not fit."""
    
    def __init__(self, world=None):
        # deepcopy: edits to this mind's map never change WORLD itself.
        self.world = copy.deepcopy(WORLD if world is None else world)
        self.entries, self.claims = [], []
        self.surprises, self.misses = [], []
        self.definitions = {}      # term -> what I mean by it

    # --- writing -----------------------------------------------------------
    def reflect(self, subject, observation, measure=None, doubt=None, struggle=None, when=None):
        """Log one entry and return its id."""
        entry = {
            "id": len(self.entries),
            "when": when or date.today().isoformat(),   # a or b: a if truthy
            "subject": subject, "observation": observation,
            "measure": measure, "doubt": doubt, "struggle": struggle,
            "resolved": False,
        }
        self.entries.append(entry)
        return entry["id"]

    def claim(self, text, status="unverified", test=None, source=None, from_entry=None):
        """Register a claim with an honest status."""
        if status not in STATUSES:
            raise ValueError(f"status must be one of {STATUSES}")
        self.claims.append({"text": text, "status": status, "test": test, "source": source, "from_entry": from_entry})

    def define(self, term, meaning, from_entry=None):
        """Fix what a word means, once. A definition is a choice, not a claim:
        it cannot be true or false, only clear or unclear."""
        if term not in self.known():
            raise ValueError(f"{term!r} is not in the map")
        self.definitions[term] = meaning
        if from_entry is not None:
            entry = self.entries[from_entry]
            if entry["doubt"] is None or entry["resolved"]:
                raise ValueError("that entry has no open doubt")
            entry["resolved"] = True

    def resolve_doubt(self, entry_id, resolution, status="unverified", test=None, source=None):
        """Turn a doubt into a claim. The doubt stays in the log as history."""
        entry = self.entries[entry_id]
        if entry["doubt"] is None:
            raise ValueError("that entry has no doubt")
        if entry["resolved"]:
            raise ValueError("that doubt is already resolved")
        entry["resolved"] = True
        self.claim(resolution, status, test, source, from_entry=entry_id)

    def surprise(self, subject, expected, actual):
        """Log a gap between what you expected and what happened."""
        if expected != actual:
            self.surprises.append({"subject": subject, "expected": expected, "actual": actual})

    # --- reading -----------------------------------------------------------
    def read(self, subject=None):
        """The log as a table, or only one subject's rows."""
        log = pd.DataFrame(self.entries, columns=COLUMNS)
        log["when"] = pd.to_datetime(log["when"])
        return log if subject is None else log[log["subject"] == subject]

    def open_doubts(self):
        """Entries with a doubt that has not been resolved."""
        log = self.read()
        return log[log["doubt"].notna() & ~log["resolved"].astype(bool)]

    def change(self, subject):
        """Step-to-step change in a subject's measure. Tests 'state or relief?'"""
        log = self.read(subject).sort_values("when")
        return pd.to_numeric(log["measure"]).diff()

    def human(self):
        """The human side as a one-row table."""
        return pd.DataFrame([HUMAN])

    # --- the map's own checks ----------------------------------------------
    def known(self):
        return set(flatten(self.world))   # a set holds each word once

    def orphans(self, concepts):
        """Concepts with no place in the map. Misses are remembered."""
        missing = [c for c in concepts if c not in self.known()]
        self.misses.extend(m for m in missing if m not in self.misses)
        return missing

    def overlaps(self):
        """Words in more than one top-level category (this ignores HUMAN)."""
        seen = {}
        for category, content in self.world.items():
            for word in set(flatten(content)):
                seen.setdefault(word, []).append(category)
        return {w: c for w, c in seen.items() if len(c) > 1}

    def park(self, concept):
        """Put a concept in the residual list until a category exists for it."""
        if concept not in self.known():
            self.world["other"].append(concept)

    def pressure(self):
        """Symptoms that the map is under strain. Not a detector of unknown unknowns."""
        n = len(self.entries)
        return {
            "unplaced concepts seen": len(self.misses),
            "parked in other": len(self.world["other"]),
            "surprise rate": len(self.surprises) / n if n else None,
        }

    # --- the bridge to the other languages ---------------------------------
    def query(self, sql):
        """Ask the log a question in SQL. Quote "when": it is a reserved word."""
        con = sqlite3.connect(":memory:")
        self.read().to_sql("log", con, index=False)
        return pd.read_sql(sql, con)

    def save(self, path="log.csv"):
        """Write the log to CSV, for the shell, Excel and git."""
        out = self.read()
        out["resolved"] = out["resolved"].astype(int)   # 0 or 1, so SQL and Excel read it plainly
        out.to_csv(path, index=False)

# ------------------------------------------------------------- demonstration ---
if __name__ == "__main__":
    mind = Mind()
    
    # A claim is "verified" only because the check beside it ran and passed.
    assert pd.DataFrame({"a": ["x", None]})["a"].isna().tolist() == [False, True]
    mind.claim("isna() flags None in a text column", "verified", test="pd.DataFrame({'a': ['x', None]})['a'].isna()", source="ran it")
    
    assert mind.orphans(["stars", "dreams"]) == ["dreams"]
    mind.claim("orphans() returns concepts missing from the map", "verified", test="mind.orphans(['stars', 'dreams'])", source="ran it")
    
    assert mind.overlaps() == {}
    
    # a stray space after a word, often from pasting, would make it unfindable
    assert all(w == w.strip() for w in flatten(WORLD))
    assert set(mind.world["data"]) == set(STATUSES)
    
    # Claims I hold, with honest statuses.
    mind.claim("relaxed is a state, not a relief", "unverified", test="mind.change(...) on heavy days that end relaxed")
    mind.claim("obsession belongs inside love, not beside it", "contested")
    mind.claim("culture holds an individual layer and collective ones", "contested")
    mind.claim("betrayal is scoped to a partner while love is not", "contested")
    
    # A doubt, then its resolution: confusion becomes a position.
    truth = mind.reflect("truth", "kept under quant as measured, under meaning as interpreted", 5, "which test decides which kind a claim is?")
    mind.resolve_doubt(truth, "truth is both measured and interpreted", "contested")
    
    # Two words whose meaning was unclear, now defined in the author's own words.
    a = mind.reflect("love", "inclusive reasons: meaning unclear", None, "what did I mean by it?")
    mind.define("inclusive reasons", "multiple reasons acting accordingly together", from_entry=a)
    
    b = mind.reflect("real experience", "self-behaving: meaning unclear", None, "behaving how, towards whom?")
    mind.define("self-behaving", "the personality that exists not in quantity", from_entry=b)
    mind.claim("inclusive reasons sits under love's 'why' group", "unverified")
    
    assert len(mind.definitions) == 2
    
    # Three invented example days, to test the state-or-relief idea. Replace with real ones.
    mind.reflect("example mood", "heavy day", 7, when="2026-11-02")
    mind.reflect("example mood", "lighter", 5, when="2026-11-03")
    mind.reflect("example mood", "heavy, long, relaxed at the end", 4, "state or relief?", when="2026-11-04")
    
    assert mind.change("example mood").dropna().tolist() == [-2.0, -1.0]
    
    # A concept the map cannot hold, then a surprise.
    mind.orphans(["dreams"])
    mind.park("dreams")
    mind.surprise("example commute", expected="on time", actual="late")
    
    print(mind.human().T, "\n")
    print(mind.open_doubts()[["id", "subject", "doubt"]], "\n")
    print(mind.definitions, "\n")
    print(pd.DataFrame(mind.claims).groupby("status").size(), "\n")
    print(mind.query('SELECT subject, AVG(measure) AS average FROM log WHERE measure IS NOT NULL GROUP BY subject'), "\n")
    print(mind.pressure())