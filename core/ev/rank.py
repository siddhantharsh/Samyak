import yaml
from typing import List, Tuple, Optional
from decimal import Decimal

_OUTCOME_PARAMS = None
_ACTION_COSTS = None

def get_outcome_params():
    global _OUTCOME_PARAMS
    if _OUTCOME_PARAMS is None:
        try:
            with open("sim/outcome_params.frozen.yaml", "r") as f:
                _OUTCOME_PARAMS = yaml.safe_load(f) or {}
        except FileNotFoundError:
            _OUTCOME_PARAMS = {}
    return _OUTCOME_PARAMS

def get_action_costs():
    global _ACTION_COSTS
    if _ACTION_COSTS is None:
        try:
            with open("data/action_costs.yaml", "r") as f:
                _ACTION_COSTS = yaml.safe_load(f) or {}
        except FileNotFoundError:
            _ACTION_COSTS = {}
    return _ACTION_COSTS

def calculate_ev(action: str, root_cause: str, attempt_index: int, amount: float) -> Decimal:
    if action == "DO_NOTHING":
        return Decimal('0.00')
        
    outcomes = get_outcome_params()
    costs = get_action_costs()
    
    # P(success)
    p_succ = outcomes.get("base_success_prob", {}).get(root_cause, 0.10)
    
    # Decay
    decays = outcomes.get("attempt_decay", [1.0])
    decay = decays[attempt_index] if attempt_index < len(decays) else decays[-1]
    p_succ *= decay
    
    # Direct Cost
    direct_cost = costs.get("costs", {}).get(action, 0.0)
    
    # Penalty Risk
    p_penalty = outcomes.get("penalty_prob", {}).get(root_cause, 0.01)
    penalty_amt = costs.get("penalties", {}).get("EXCESSIVE_RETRY", 25.00)
    
    # Simplified EV calculation (fatigue_cost and churn_risk_cost are 0 for now as per minimal baseline)
    expected_value = (p_succ * amount) - direct_cost - (p_penalty * penalty_amt)
    return Decimal(expected_value).quantize(Decimal('0.01'))

def rank_actions(candidates: List[str], root_cause: str, attempt_index: int, amount: float) -> List[Tuple[str, Decimal]]:
    """
    Ranks the available candidate actions by their Expected Value.
    Always includes DO_NOTHING.
    """
    if "DO_NOTHING" not in candidates:
        candidates.append("DO_NOTHING")
        
    scored = []
    for action in candidates:
        ev = calculate_ev(action, root_cause, attempt_index, amount)
        scored.append((action, ev))
        
    # Sort by EV descending
    return sorted(scored, key=lambda x: x[1], reverse=True)
