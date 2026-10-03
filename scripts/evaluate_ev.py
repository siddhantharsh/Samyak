import sys
import os
import json

# Add the project root to sys.path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.entities import LeakEvent
from core.diagnose.resolver_l1 import resolve_l1
from core.ev.rank import rank_actions

def run():
    print("Evaluating EV over Synthetic Corpus...")
    try:
        with open("data/synthetic/events.json") as f:
            events = json.load(f)
    except FileNotFoundError:
        print("data/synthetic/events.json not found! Please run 'make data' first.")
        return
        
    restraint_count = 0
    total = 0
    
    for ev_dict in events:
        ev = LeakEvent(**ev_dict)
        diag = resolve_l1(ev)
        
        # Consider a standard set of candidate actions for the ranking
        candidates = ["mandate.represent", "message.send", "human.handoff"]
        
        attempt = ev.context.attempt_index if ev.context.attempt_index else 0
        
        ranked = rank_actions(candidates, diag.root_cause, attempt, ev.amount)
        best_action, best_ev = ranked[0]
        
        if best_action == "DO_NOTHING":
            restraint_count += 1
            
        total += 1
        
    print("=" * 40)
    print("EV RANKING RESULTS")
    print(f"Total Cases     : {total}")
    print(f"Restraint Count : {restraint_count}")
    print("=" * 40)

if __name__ == "__main__":
    run()
