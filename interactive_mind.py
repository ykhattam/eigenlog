"""interactive_mind.py: Fluid interactive practice for Eigenlog.
Allows entering any subject or multi-tag freely, with quant/qual scaling.
"""
from eigenlog import Mind

def main():
    m = Mind()
    print("--- Eigenlog Fluid Practice ---")
    print("Tip: Subjects, categories, and tags are now fully fluid. Express freely.\n")
    
    while True:
        subject = input("Subject / Domain (or 'quit'): ").strip()
        if not subject or subject.lower() == 'quit':
            break
            
        observation = input("Observation / Thought: ").strip()
        measure = input("Quant/Qual Measure or Scale (optional): ").strip() or None
        doubt = input("Any doubt or tension? (optional): ").strip() or None
        
        entry_id = m.reflect(subject=subject, observation=observation, measure=measure, doubt=doubt)
        print(f"-> Logged reflection #{entry_id} under [{subject}]\n")

    log = m.read()
    if not log.empty:
        print("\n--- Your Fluid Session Log ---")
        print(log[['when', 'subject', 'observation', 'measure', 'doubt']])

if __name__ == "__main__":
    main()
