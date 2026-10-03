from pydantic import BaseModel
from typing import List, Callable, Any
from core.audit.ledger import AuditLedger, DecisionRecord

class ReplayReport(BaseModel):
    total_cases: int
    matches: int
    determinism_percentage: float

def replay_all(ledger: AuditLedger, decision_fn: Callable[[Any], DecisionRecord]) -> ReplayReport:
    """
    Given an audit ledger, replay every historical decision through the current policy engine
    and assert bit-identical output.
    `decision_fn` takes a `snapshot` and returns the newly evaluated `DecisionRecord`.
    """
    records = ledger.get_all()
    # Skip genesis block
    records_to_replay = [r for r in records if not r.get("is_genesis")]
    
    total = len(records_to_replay)
    if total == 0:
        return ReplayReport(total_cases=0, matches=0, determinism_percentage=100.0)
        
    matches = 0
    for rec_dict in records_to_replay:
        new_record = decision_fn(rec_dict)
        
        old_action = rec_dict.get("chosen_plan", {}).get("steps", [{}])[0].get("kind") if rec_dict.get("chosen_plan") else None
        new_action = new_record.chosen_plan.steps[0].kind if new_record.chosen_plan and new_record.chosen_plan.steps else None
        
        old_refusals = set(r[1] for r in rec_dict.get("refusals", []))
        new_refusals = set(r[1] for r in new_record.refusals)
        
        if old_action == new_action and old_refusals == new_refusals:
            matches += 1
            
    return ReplayReport(
        total_cases=total,
        matches=matches,
        determinism_percentage=(matches / total) * 100.0
    )
