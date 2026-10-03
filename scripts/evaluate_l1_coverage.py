import json
from core.entities import LeakEvent, Layer
from core.diagnose.resolver_l1 import resolve_l1

def run():
    print("Evaluating L1 Deterministic Resolver Coverage...")
    with open("data/synthetic/events.json") as f:
        events_data = json.load(f)
        
    events = [LeakEvent(**d) for d in events_data]
    
    l1_resolved = 0
    unresolved = 0
    
    for ev in events:
        diag = resolve_l1(ev)
        if diag.layer == Layer.L1_DETERMINISTIC:
            l1_resolved += 1
        elif diag.layer == Layer.UNRESOLVED:
            unresolved += 1
            
    total = len(events)
    coverage = (l1_resolved / total) * 100 if total > 0 else 0.0
    
    print("=" * 40)
    print(f"L1 DIAGNOSIS COVERAGE")
    print(f"Total Events Processed : {total}")
    print(f"L1 Resolved            : {l1_resolved}")
    print(f"Unresolved (to L2)     : {unresolved}")
    print(f"Coverage Percentage    : {coverage:.2f}%")
    print("=" * 40)
    
if __name__ == "__main__":
    run()
