"""interactive_mind.py: Fluid interactive practice for Eigenlog.
Allows entering any subject or multi-tag freely, with optional local Qwen AI critique.
"""
import sys
import os
import json
import sqlite3
from datetime import date
from pydantic import BaseModel, Field, ValidationError
from eigenlog import Mind, WORLD_REFERENCES
from ai_critic import critique, check_server, Dialogue

CONFIG_FILE = ".eigenlog_config"
DB_FILE = "eigenlog.db"

class LogEntry(BaseModel):
    id: int
    when: str
    subject: str = Field(..., min_length=1)
    observation: str = Field(..., min_length=1)
    measure: str | None = None
    doubt: str | None = None
    struggle: str | None = None
    resolved: int = 0


class PersistentMind(Mind):
    def __init__(self, db_path=DB_FILE):
        super().__init__()
        self.db_path = db_path
        self._init_db()
        self.load_from_db()

    def _init_db(self):
        con = sqlite3.connect(self.db_path)
        con.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                when_date TEXT NOT NULL,
                subject TEXT NOT NULL,
                observation TEXT NOT NULL,
                measure TEXT,
                doubt TEXT,
                struggle TEXT,
                resolved INTEGER DEFAULT 0
            )
        """)
        con.commit()
        con.close()
        try:
            os.chmod(self.db_path, 0o600)
        except OSError:
            pass
        self._migrate_csv()

    def _migrate_csv(self):
        """One-time import of a legacy log.csv if the DB has no rows yet."""
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.csv")
        if not os.path.exists(csv_path):
            return
        con = sqlite3.connect(self.db_path)
        existing = con.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        if existing:
            con.close()
            return
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            n = 0
            for _, row in df.iterrows():
                try:
                    entry = LogEntry(
                        id=int(row.get("id", n)),
                        when=str(row.get("when", "")),
                        subject=str(row.get("subject", "general")),
                        observation=str(row.get("observation", "")),
                        measure=None if pd.isna(row.get("measure")) else str(row.get("measure")),
                        doubt=None if pd.isna(row.get("doubt")) else str(row.get("doubt")),
                        struggle=None if pd.isna(row.get("struggle")) else str(row.get("struggle")),
                        resolved=int(bool(row.get("resolved", 0))),
                    )
                except (ValidationError, ValueError, TypeError):
                    continue
                con.execute(
                    "INSERT OR REPLACE INTO entries (id, when_date, subject, observation, measure, doubt, struggle, resolved) VALUES (?,?,?,?,?,?,?,?)",
                    (entry.id, entry.when, entry.subject, entry.observation, entry.measure, entry.doubt, entry.struggle, entry.resolved),
                )
                n += 1
            con.commit()
            con.close()
            if n:
                os.rename(csv_path, csv_path + ".migrated")
                print(f"[migration: imported {n} entries from log.csv into eigenlog.db; log.csv renamed to log.csv.migrated]")
        except Exception as e:
            con.close()
            print(f"[migration skipped: {e}]")

    def load_from_db(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT id, when_date, subject, observation, measure, doubt, struggle, resolved FROM entries ORDER BY id ASC")
        rows = cur.fetchall()
        con.close()
        
        self.entries = []
        for r in rows:
            try:
                entry_data = {
                    "id": r[0],
                    "when": r[1],
                    "subject": r[2],
                    "observation": r[3],
                    "measure": r[4],
                    "doubt": r[5],
                    "struggle": r[6],
                    "resolved": r[7]
                }
                validated = LogEntry(**entry_data)
                self.entries.append(validated.model_dump())
            except ValidationError as e:
                print(f"[Schema Validation Error on row {r[0]}: {e}]")

    def save_entry_to_db(self, entry):
        validated = LogEntry(**entry)
        con = sqlite3.connect(self.db_path)
        con.execute("""
            INSERT OR REPLACE INTO entries (id, when_date, subject, observation, measure, doubt, struggle, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (validated.id, validated.when, validated.subject, validated.observation, validated.measure, validated.doubt, validated.struggle, validated.resolved))
        con.commit()
        con.close()
        try:
            os.chmod(self.db_path, 0o600)
        except OSError:
            pass

    def reflect(self, subject, observation, measure=None, doubt=None, struggle=None, when=None):
        entry_id = super().reflect(subject, observation, measure, doubt, struggle, when)
        self.save_entry_to_db(self.entries[-1])
        return entry_id

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"mode": "1", "heat_level": 2}

def save_config(mode, heat_level):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"mode": mode, "heat_level": heat_level}, f)
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        pass

def main():
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print("\n-> Session ended.")
        return

def run():
    m = PersistentMind()
    
    # Handle Frictionless Micro-Log CLI Arguments (eigenlog -q / quick)
    if len(sys.argv) > 1 and sys.argv[1] in ("-q", "--quick", "quick"):
        if len(sys.argv) < 3:
            print("Error: Please provide a quick observation text, e.g. python interactive_mind.py -q 'tired'")
            sys.exit(1)
        observation = " ".join(sys.argv[2:])
        entry_id = m.reflect(subject="general", observation=observation)
        print(f"-> Frictionless Micro-Log recorded: #{entry_id} under [general]. Saved to eigenlog.db.")
        sys.exit(0)

    print("--- Eigenlog Fluid Practice ---")
    
    cfg = load_config()
    
    # Ask for Heat Dial level (with saved default representation)
    heat_input = input(f"Select AI Heat Dial:\n  [0] Cold Mode + Grammar/Logic Review\n  [1] Mirror / Supportive\n  [2] Dialectic / Questioning\n  [3] Forensic / Adversarial\nSelect [0/1/2/3] (Press Enter for saved default {cfg['heat_level']}): ").strip()
    heat_level = int(heat_input) if heat_input in ('0', '1', '2', '3') else cfg['heat_level']
    
    # Ask for mode (with saved default representation)
    mode_input = input(f"Select mode:\n  [1] Normal / Database logging only\n  [2] Interactive with Local LLM critique\n  [3] Pure Cold Mode (No AI)\nSelect [1/2/3] (Press Enter for saved default {cfg['mode']}): ").strip()
    mode = mode_input if mode_input in ('1', '2', '3') else cfg['mode']
    
    save_config(mode, heat_level)
    
    use_ai = (mode == '2') or (heat_level == 0)
    
    if mode == '3' and heat_level != 0:
        print("-> Pure Cold Mode active. Solitary, unassisted introspection enabled.\n")
        use_ai = False
    elif heat_level == 0:
        if check_server():
            print("-> Gentle grammar & logic checker enabled (Cold Mode + Review).\n")
            use_ai = True
        else:
            print("-> Warning: Local LLM server not active. Proceeding pure cold.\n")
            use_ai = False
    elif use_ai:
        if check_server():
            print("-> Local LLM critic enabled.\n")
        else:
            print("-> Warning: Local LLM server not active at http://127.0.0.1:8080. Falling back to normal mode.\n")
            use_ai = False
    else:
        print("-> Running in normal database/log mode.\n")

    # Display Macro-Categories & References
    print("=== Reference Ontology Taxonomy ===")
    for macro, micros in WORLD_REFERENCES.items():
        print(f"  {macro:<25}: {', '.join(micros)}")
    print("====================================\n")
    
    while True:
        subject = input("Subject / Domain (or 'quit' to exit): ").strip()
        if not subject or subject.lower() in ('quit', 'q'):
            break
            
        # Check for previous entry to surface Delta & progression
        last_entry = m.get_last_entry(subject)
        if last_entry:
            print(f"\n[Last time on [{subject}]] ({last_entry['when']}):")
            print(f"  Observation: \"{last_entry['observation']}\"")
            if last_entry.get('measure'):
                print(f"  Measure    : {last_entry['measure']}")
            if last_entry.get('doubt'):
                print(f"  Doubt      : {last_entry['doubt']}")
            print("-" * 40)
            delta = input("How has your understanding evolved since then? (optional evolution/delta): ").strip()
            if delta:
                observation_prefix = f"[Delta from {last_entry['when']}: {delta}] "
            else:
                observation_prefix = ""
        else:
            observation_prefix = ""

        observation_input = input("Observation / Thought: ").strip()
        if not observation_input:
            print("Observation cannot be empty.")
            continue
            
        epistemic_tag = input("Epistemic Tag: [1] Hypothesis (Default), [2] Subjective Truth [1/2]: ").strip()
        tag_str = "Subjective Truth" if epistemic_tag == '2' else "Hypothesis"

        observation = f"{observation_prefix}[{tag_str}] {observation_input}"
        measure = input("Quant/Qual Measure or Scale (optional): ").strip() or None
        doubt = input("Any doubt or tension? (optional): ").strip() or None
        
        entry_id = m.reflect(subject=subject, observation=observation, measure=measure, doubt=doubt)
        print(f"-> Logged reflection #{entry_id} under [{subject}]")
        
        if use_ai:
            label = "grammar & coherence review" if heat_level == 0 else "critical dialectic feedback"
            print(f"\n[Asking Local LLM for {label}...]")
            feedback = critique(observation, subject, world_keys=m.world.keys(), heat_level=heat_level, epistemic_tag=tag_str)
            print(f"Local LLM: {feedback}")
            dialogue = Dialogue(subject, heat_level=heat_level, epistemic_tag=tag_str, world_keys=m.world.keys())
            
            # Interactive feedback & control options
            while True:
                choice = input("Feedback options: [y] Useful, [n] Unuseful, [r] Repeat critique, [rating 1-5] Give score, [q] Quit loop, [Enter to continue]: ").strip().lower()
                if not choice:
                    print("-> Continuing.\n")
                    break
                elif choice in ('q', 'quit'):
                    print("-> Exiting feedback loop.\n")
                    break
                elif choice == 'y':
                    print("-> Telemetry recorded: Useful.\n")
                    break
                elif choice == 'n':
                    print("-> Telemetry recorded: Unhelpful.\n")
                    break
                elif choice == 'r':
                    print("\n[Re-generating critique...]")
                    feedback = critique(observation, subject, world_keys=m.world.keys(), heat_level=heat_level, epistemic_tag=tag_str)
                    print(f"Local LLM: {feedback}\n")
                elif choice.isdigit() and 1 <= int(choice) <= 5:
                    print(f"-> Telemetry recorded: Rating {choice}/5.\n")
                    break
                else:
                    # Treat input as a direct dialogue/reply
                    print("[Thinking...]")
                    reply, warning = dialogue.send(choice)
                    if warning:
                        print(warning)
                    feedback = reply
                    print(f"Local LLM: {feedback}")
        else:
            print()

    log = m.read()
    if not log.empty:
        print("\n--- Your Fluid Session Log ---")
        print(log[['when', 'subject', 'observation', 'measure', 'doubt']])

if __name__ == "__main__":
    main()
