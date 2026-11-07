"""interactive_mind.py: Fluid interactive practice for Eigenlog.
Allows entering any subject or multi-tag freely, with optional local Qwen AI critique.
"""
import sys
from eigenlog import Mind, WORLD_REFERENCES
from ai_critic import critique, check_server

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
    
    mode = input("Select mode:\n  [1] Normal / Database logging only\n  [2] Interactive with Local LLM critique\n  [3] Cold Mode (No AI critique for deep independent thinking)\nSelect [1/2/3]: ").strip()
    use_ai = (mode == '2')
    
    if mode == '3':
        print("-> Cold Mode active. Solitary, unassisted introspection enabled.\n")
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
            
        observation = f"{observation_prefix}{observation_input}"
        measure = input("Quant/Qual Measure or Scale (optional): ").strip() or None
        doubt = input("Any doubt or tension? (optional): ").strip() or None
        
        entry_id = m.reflect(subject=subject, observation=observation, measure=measure, doubt=doubt)
        print(f"-> Logged reflection #{entry_id} under [{subject}]")
        
        if use_ai:
            print("\n[Asking Local LLM for critical dialectic feedback...]")
            feedback = critique(observation, subject, world_keys=m.world.keys())
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
                        "model": LOCAL_MODEL_NAME,
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
