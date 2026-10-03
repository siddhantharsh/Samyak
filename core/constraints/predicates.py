from typing import Tuple, Dict, Any
from core.entities import ConstraintSnapshot, PlannedAction
from core.constraints.schema import Predicate

def evaluate_predicate(predicate: Predicate, snapshot: ConstraintSnapshot, action: PlannedAction) -> Tuple[bool, str]:
    context = {**snapshot.model_dump(), **action.variables}

    if predicate.kind == "counter_cap":
        count = snapshot.attempt_counters.get(predicate.counter, 0)
        if predicate.condition and not _eval_condition(predicate.condition, context):
            return True, "Condition not met"
        if count >= predicate.cap:
            return False, f"Cap {predicate.cap} reached for {predicate.counter}"
        return True, "Passed"

    elif predicate.kind == "requires_precondition":
        if predicate.precondition_action:
            if predicate.precondition_action not in action.precondition_step_ids:
                if predicate.exempt_when and _eval_condition(predicate.exempt_when, context):
                    return True, "Exempted"
                return False, f"Requires {predicate.precondition_action}"
        if predicate.appended_action:
            if not action.variables.get("_has_appended"):
                return False, f"Requires {predicate.appended_action}"
        if predicate.prepended_element:
            if predicate.prepended_element not in action.variables.get("elements", []):
                return False, f"Requires {predicate.prepended_element}"
        return True, "Passed"

    elif predicate.kind == "blackout":
        if predicate.condition and not _eval_condition(predicate.condition, context):
            return True, "Condition not met"
        if action.variables.get("_is_blackout"):
            return False, "In blackout"
        return True, "Passed"

    elif predicate.kind == "requires_state":
        parts = predicate.state_path.split('.')
        val = context
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                val = None

        if predicate.required_value == "NOT_NULL":
            if val is None:
                return False, f"State {predicate.state_path} is null"
        elif isinstance(predicate.required_value, str) and predicate.required_value.startswith("IN ["):
            inner = predicate.required_value[4:-1]
            allowed = [x.strip() for x in inner.split(',')]
            if val not in allowed:
                return False, f"State {val} not in {allowed}"
        else:
            if val != predicate.required_value:
                return False, f"State {val} != {predicate.required_value}"
        return True, "Passed"

    elif predicate.kind == "forbidden_when":
        if predicate.condition:
            if _eval_condition(predicate.condition, context):
                return False, f"Forbidden by {predicate.condition}"
        return True, "Passed"

    elif predicate.kind == "time_window":
        if predicate.condition and not _eval_condition(predicate.condition, context):
            return True, "Condition not met"
        if action.variables.get("_out_of_time_window"):
            return False, "Outside time window"
        return True, "Passed"

    elif predicate.kind == "threshold":
        if predicate.condition and not _eval_condition(predicate.condition, context):
            return True, "Condition not met"
        val = context.get(predicate.field)
        if val is None:
            return True, "Passed"
        if predicate.max is not None and val > predicate.max:
            return False, f"Exceeds max {predicate.max}"
        if predicate.min is not None and val < predicate.min:
            return False, f"Below min {predicate.min}"
        
        if predicate.max_ratio_of and predicate.ratio is not None:
            base_val = context.get(predicate.max_ratio_of, 1.0)
            if val > base_val * predicate.ratio:
                return False, f"Exceeds max ratio {predicate.ratio}"
                
        return True, "Passed"

    elif predicate.kind == "requires_consent":
        if snapshot.consent_state.get(predicate.consent_field) is not True:
            return False, "Consent not granted"
        return True, "Passed"

    elif predicate.kind == "min_gap":
        if action.variables.get("_gap_too_small"):
            return False, "Gap too small"
        return True, "Passed"

    return True, "Passed"

def _eval_condition(cond: str, context: Dict[str, Any]) -> bool:
    class AttrDict(dict):
        def __getattr__(self, key):
            return self.get(key)
            
    def to_attr(d):
        if isinstance(d, dict):
            return AttrDict({k: to_attr(v) for k, v in d.items()})
        elif isinstance(d, list):
            return [to_attr(x) for x in d]
        return d
    
    safe_locals = to_attr(context)
    constants = {
        "INSURANCE": "INSURANCE",
        "MUTUAL_FUND": "MUTUAL_FUND",
        "CREDIT_CARD_BILL": "CREDIT_CARD_BILL",
        "REGISTERED": "REGISTERED",
        "PROMOTIONAL": "PROMOTIONAL",
        "SERVICE": "SERVICE",
        "TRANSACTIONAL": "TRANSACTIONAL",
        "GOVERNMENT": "GOVERNMENT",
        "debtor": "debtor",
        "guarantor": "guarantor",
        "co_borrower": "co_borrower",
        "T+1": "T+1",
        "CALAMITOUS_TIMING": "CALAMITOUS_TIMING",
        "null": None,
        "abs": abs,
        "true": True,
        "false": False
    }
    safe_locals.update(constants)
    
    cond = cond.replace(" and ", " and ")
    cond = cond.replace("T+1", "'T+1'")
    cond = cond.replace("subject.suppression_flags contains CALAMITOUS_TIMING", "CALAMITOUS_TIMING in subject.suppression_flags")
    
    try:
        return eval(cond, {"__builtins__": {}}, safe_locals)
    except Exception:
        return False
