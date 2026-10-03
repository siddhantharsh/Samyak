from datetime import datetime, timedelta, timezone
from typing import List, Optional
from ortools.sat.python import cp_model
from core.entities import ActionPlan, PlannedAction

def _slot_to_dt(slot: int) -> datetime:
    # Anchor at midnight UTC
    anchor = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return anchor + timedelta(minutes=30 * slot)

def solve_plan(
    attempts_remaining: int = 4,
    horizon_days: int = 14,
    require_debit: bool = True,
    restrict_to_slot: Optional[int] = None,
    enforce_fpc: bool = True
) -> ActionPlan:
    """
    CP-SAT solver generating an ActionPlan over a 14-day horizon.
    """
    model = cp_model.CpModel()
    
    slots_per_day = 48
    num_slots = horizon_days * slots_per_day
    
    actions = ['debit', 'pdn', 'sms']
    x = {}
    for a in actions:
        for t in range(num_slots):
            x[(a, t)] = model.NewBoolVar(f'x_{a}_{t}')
            
    assumption_map = {}
    assumption_vars = []
    
    def add_assumption(rule_id: str):
        b = model.NewBoolVar(f'assume_{rule_id}')
        assumption_map[b.Index()] = rule_id
        assumption_vars.append(b)
        return b

    # SYSTEM-REQ-01: We must schedule at least one debit to have a viable recovery plan
    if require_debit:
        b_req = add_assumption('SYSTEM-REQ-01')
        model.Add(sum(x['debit', t] for t in range(num_slots)) >= 1).OnlyEnforceIf(b_req)

    # 1. NPCI-ATT-01: Max attempts
    b_att = add_assumption('NPCI-ATT-01')
    model.Add(sum(x['debit', t] for t in range(num_slots)) <= attempts_remaining).OnlyEnforceIf(b_att)

    # 2. NPCI-PDN-01: PDN 24-48h before debit
    # For every slot t, if x['debit', t] == 1, then sum(x['pdn', t']) >= 1 for t' in [t-96, t-48]
    b_pdn1 = add_assumption('NPCI-PDN-01')
    for t in range(num_slots):
        end_t = t - 48
        start_t = t - 96
        
        if end_t < 0:
            model.Add(x['debit', t] == 0).OnlyEnforceIf(b_pdn1)
        else:
            start_t = max(0, start_t)
            valid_pdns = [x['pdn', tp] for tp in range(start_t, end_t + 1)]
            model.Add(sum(valid_pdns) >= 1).OnlyEnforceIf([b_pdn1, x['debit', t]])
            
    # 3. NPCI-PDN-02: No PDN in 23:50 cutoff (slot 47 in each day)
    b_pdn2 = add_assumption('NPCI-PDN-02')
    for t in range(num_slots):
        if t % 48 == 47:
            model.Add(x['pdn', t] == 0).OnlyEnforceIf(b_pdn2)
            
    # 4. RBI-FPC-01: Contact hours 08:00 - 19:00 (slots 16 to 37)
    if enforce_fpc:
        b_fpc = add_assumption('RBI-FPC-01')
        for t in range(num_slots):
            slot_in_day = t % 48
            if not (16 <= slot_in_day < 38):
                model.Add(x['sms', t] == 0).OnlyEnforceIf(b_fpc)
                model.Add(x['pdn', t] == 0).OnlyEnforceIf(b_fpc)

    # Test overrides
    if restrict_to_slot is not None:
        b_restr = add_assumption('TEST-RESTR')
        model.Add(x['debit', restrict_to_slot] == 1).OnlyEnforceIf(b_restr)
        # Prevent any other debits to tightly constrain the test
        model.Add(sum(x['debit', t] for t in range(num_slots)) == 1).OnlyEnforceIf(b_restr)

    # Objective: Maximize early debits
    model.Maximize(
        sum(x['debit', t] * 1000 - (t * x['debit', t]) for t in range(num_slots))
    )
    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 0.5
    
    model.AddAssumptions(assumption_vars)
    
    status = solver.Solve(model)
    
    if status == cp_model.INFEASIBLE:
        conflicts = solver.SufficientAssumptionsForInfeasibility()
        binding = [assumption_map[b] for b in conflicts]
        return ActionPlan(feasible=False, binding_constraints=binding)
        
    elif status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        steps = []
        for t in range(num_slots):
            for a in actions:
                if solver.Value(x[(a, t)]):
                    steps.append(PlannedAction(
                        kind=a,
                        scheduled_at=_slot_to_dt(t),
                        channel="SYSTEM" if a == 'debit' else "SMS",
                        template_id=None,
                        variables={},
                        precondition_step_ids=[]
                    ))
        return ActionPlan(feasible=True, steps=steps)
        
    else:
        return ActionPlan(feasible=False, binding_constraints=["SOLVER_TIMEOUT"])
