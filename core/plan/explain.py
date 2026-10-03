from typing import List

def explain_infeasibility(binding_constraints: List[str]) -> str:
    """
    Turns an infeasible result into a human-readable sentence.
    """
    explanations = {
        "NPCI-ATT-01": "mandate attempts exhausted (NPCI-ATT-01)",
        "NPCI-PDN-01": "unable to schedule 24h pre-debit notification (NPCI-PDN-01)",
        "NPCI-PDN-02": "PDN falls into the 23:50 cutoff blackout (NPCI-PDN-02)",
        "RBI-FPC-01": "contact falls outside permitted 08:00-19:00 window (RBI-FPC-01)",
        "SYSTEM-REQ-01": "no slots available for debit execution (SYSTEM-REQ-01)"
    }
    
    reasons = [explanations.get(c, c) for c in binding_constraints if c != "TEST-RESTR"]
    if not reasons:
        reasons = ["unresolvable constraints"]
        
    reason_str = ", ".join(reasons)
    return f"No legal action available before horizon: {reason_str}. Recommend manual outreach via the registered relationship manager."
