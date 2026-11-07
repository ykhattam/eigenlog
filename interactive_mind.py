"""interactive_mind.py: Fluid interactive practice for Eigenlog.
Allows entering any subject or multi-tag freely, with optional local Qwen AI critique.
"""
from eigenlog import Mind
from ai_critic import critique, check_server

def main():
    m = Mind()
    print("--- Eigenlog Fluid Practice with Local AI ---")
    
    use_ai = False
    if check_server():
        choice = input("Local Qwen LLM server detected on port 8080. Enable AI critique? [y/N]: ").strip().lower()
        if choice == 'y':
            use_ai = True
            print("-> Local Qwen AI critic enabled.\n")
        else:
            print("-> Continuing without AI critique.\n")
    else:
        print("-> Local LLM server not active at http://127.0.0.1:8080. Running standard mode.\n")

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
            print("\n[Asking Qwen Coder for critique...]")
            feedback = critique(observation, subject)
            print(f"Qwen: {feedback}\n")
        else:
            print()

    log = m.read()
    if not log.empty:
        print("\n--- Your Fluid Session Log ---")
        print(log[['when', 'subject', 'observation', 'measure', 'doubt']])

if __name__ == "__main__":
    main()
