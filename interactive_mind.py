"""interactive_mind.py: Fluid interactive practice for Eigenlog.
Allows entering any subject or multi-tag freely, with optional local Qwen AI critique.
"""
import sys
import os
import json
from eigenlog import Mind, WORLD_REFERENCES
from ai_critic import critique, check_server

CONFIG_FILE = ".eigenlog_config"

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
    m = Mind()
    
    # Handle Frictionless Micro-Log CLI Arguments (eigenlog -q / quick)
    if len(sys.argv) > 1 and sys.argv[1] in ("-q", "--quick", "quick"):
        if len(sys.argv) < 3:
            print("Error: Please provide a quick observation text, e.g. python interactive_mind.py -q 'tired'")
            sys.exit(1)
        observation = " ".join(sys.argv[2:])
        entry_id = m.reflect(subject="general", observation=observation)
        m.save()
        print(f"-> Frictionless Micro-Log recorded: #{entry_id} under [general]. Saved successfully.")
        sys.exit(0)

    print("--- Eigenlog Fluid Practice ---")
    
    cfg = load_config()
    
    # Ask for Heat Dial level (with saved default representation)
    heat_input = input(f"Select AI Heat Dial:\n  [1] Mirror / Supportive\n  [2] Dialectic / Questioning\n  [3] Forensic / Adversarial\nSelect [1/2/3] (Press Enter for saved default {cfg['heat_level']}): ").strip()
    heat_level = int(heat_input) if heat_input in ('1', '2', '3') else cfg['heat_level']
    
    # Ask for mode (with saved default representation)
    mode_input = input(f"Select mode:\n  [1] Normal / Database logging only\n  [2] Interactive with Local LLM critique\n  [3] Cold Mode (No AI critique for deep independent thinking)\nSelect [1/2/3] (Press Enter for saved default {cfg['mode']}): ").strip()
    mode = mode_input if mode_input in ('1', '2', '3') else cfg['mode']
    
    save_config(mode, heat_level)
    
    use_ai = (mode == '2')
    
    if mode == '3':
        print("-> Cold Mode active. Solitary, unassisted introspection enabled.")
        print("-> Tip: Even without AI critique, you can run a local grammar & logical coherence check.")
        check_grammar = input("Would you like a grammar and consistency check (via local LLM without adversarial challenge)? [y/N]: ").strip().lower()
        use_ai = (check_grammar == 'y')
        if use_ai:
            if check_server():
                print("-> Gentle grammar & logic checker enabled.\n")
                heat_level = 0
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
            print("\n[Asking Local LLM for critical dialectic feedback...]")
            feedback = critique(observation, subject, world_keys=m.world.keys(), heat_level=heat_level, epistemic_tag=tag_str)
            print(f"Local LLM: {feedback}")
            
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
                    feedback = critique(observation, subject, world_keys=m.world.keys())
                    print(f"Local LLM: {feedback}\n")
                elif choice.isdigit() and 1 <= int(choice) <= 5:
                    print(f"-> Telemetry recorded: Rating {choice}/5.\n")
                    break
                else:
                    # Treat input as a direct dialogue/reply
                    print("[Thinking...]")
                    dialogue_prompt = f"Previous observation: {observation}\nCritique: {feedback}\nUser response: {choice}\n\nProvide a brief, challenging follow-up question or perspective (1 sentence):"
                    
                    import os
                    import requests
                    LMS_URL = os.getenv("LMS_URL", "http://127.0.0.1:8080/v1/chat/completions")
                    LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "qwen2.5-coder")
                    payload = {
                        "model": "/home/khattam/.local/share/oubliette/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
                        "messages": [
                            {"role": "system", "content": "You are a rigorous dialectical opponent maintaining conversational epistemic friction."},
                            {"role": "user", "content": dialogue_prompt}
                        ],
                        "temperature": 0.6,
                        "max_tokens": 60
                    }
                    try:
                        r = requests.post(LMS_URL, json=payload, timeout=60)
                        if r.status_code == 200:
                            feedback = r.json()["choices"][0]["message"]["content"].strip()
                            print(f"Local LLM: {feedback}")
                        else:
                            print("[LLM Error]")
                    except Exception as e:
                        print(f"[Error: {e}]")
        else:
            print()

    log = m.read()
    if not log.empty:
        print("\n--- Your Fluid Session Log ---")
        print(log[['when', 'subject', 'observation', 'measure', 'doubt']])

if __name__ == "__main__":
    main()
