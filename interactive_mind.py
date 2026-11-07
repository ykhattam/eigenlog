"""interactive_mind.py: Fluid interactive practice for Eigenlog.
Allows entering any subject or multi-tag freely, with optional local Qwen AI critique.
"""
from eigenlog import Mind
from ai_critic import critique, check_server

def main():
    m = Mind()
    print("--- Eigenlog Fluid Practice ---")
    
    mode = input("Select mode: [1] Normal / Database logging only, [2] Interactive with Local LLM critique [1/2]: ").strip()
    use_ai = (mode == '2')
    
    if use_ai:
        if check_server():
            print("-> Local LLM critic enabled.\n")
        else:
            print("-> Warning: Local LLM server not active at http://127.0.0.1:8080. Falling back to normal mode.\n")
            use_ai = False
    else:
        print("-> Running in normal database/log mode.\n")

    print(f"Known world references for inspiration: {list(m.world.keys())}\n")
    
    while True:
        subject = input("Subject / Domain (or 'quit'): ").strip()
        if not subject or subject.lower() == 'quit':
            break
            
        observation = input("Observation / Thought: ").strip()
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
