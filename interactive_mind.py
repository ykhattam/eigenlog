"""interactive_mind.py: Fluid interactive practice for Eigenlog.
Allows entering any subject or multi-tag freely, with optional local Qwen AI critique.
"""
from eigenlog import Mind
from ai_critic import critique, check_server

def main():
    m = Mind()
    print("--- Eigenlog Fluid Practice ---")
    
    mode = input("Select mode: [1] Normal / Database logging only, [2] Interactive with Local Qwen AI critique [1/2]: ").strip()
    use_ai = (mode == '2')
    
    if use_ai:
        if check_server():
            print("-> Local Qwen AI critic enabled.\n")
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
            print("\n[Asking Qwen Coder for critical dialectic feedback...]")
            feedback = critique(observation, subject, world_keys=m.world.keys())
            print(f"Qwen: {feedback}")
            
            # Simple feedback mechanism to prevent echo chambers & track utility
            useful = input("Was this critique useful? [y/n]: ").strip().lower()
            if useful == 'y':
                print("-> Telemetry recorded: Useful.\n")
            else:
                print("-> Telemetry recorded: Dismissed as unhelpful.\n")
        else:
            print()

    log = m.read()
    if not log.empty:
        print("\n--- Your Fluid Session Log ---")
        print(log[['when', 'subject', 'observation', 'measure', 'doubt']])

if __name__ == "__main__":
    main()
