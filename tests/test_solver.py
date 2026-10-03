import pytest
import itertools
from datetime import timedelta
from core.plan.solver import solve_plan
from core.plan.explain import explain_infeasibility

# 1-15: Basic Parameter Variations
PARAM_CASES = [
    # (attempts, require_debit, enforce_fpc, expected_feasible, expected_binding)
    (0, True, True, False, ["NPCI-ATT-01"]),
    (0, True, False, False, ["NPCI-ATT-01"]),
    (0, False, True, True, []),
    (0, False, False, True, []),
    (1, True, True, True, []),
    (1, True, False, True, []),
    (1, False, True, True, []),
    (1, False, False, True, []),
    (4, True, True, True, []),
    (4, True, False, True, []),
    (4, False, True, True, []),
    (4, False, False, True, []),
    (10, True, True, True, []),
    (10, True, False, True, []),
    (10, False, True, True, []),
]

@pytest.mark.parametrize("attempts, req_deb, fpc, exp_feas, exp_bind", PARAM_CASES)
def test_solver_parameters(attempts, req_deb, fpc, exp_feas, exp_bind):
    plan = solve_plan(
        attempts_remaining=attempts,
        require_debit=req_deb,
        enforce_fpc=fpc
    )
    assert plan.feasible == exp_feas
    if not exp_feas:
        # CP-SAT might return a superset/subset of constraints that conflict.
        # We assert that the primary expected constraint is in the binding set.
        for b in exp_bind:
            assert b in plan.binding_constraints

# 16-35: Boundary Slots for PDN Coupling
# We test forcing a debit at slot `t` with enforce_fpc=False so only PDN constraints apply.
# For t < 48, it must fail because 24h lead time needs t-48 >= 0.
SLOT_CASES = [
    (0, False), (10, False), (20, False), (30, False), (40, False),
    (45, False), (46, False), (47, False), # All < 48 are infeasible
    (48, True), (49, True), (95, True), (96, True), # >= 48 are feasible
    (200, True), (300, True), (400, True), (500, True),
    (600, True), (650, True), (670, True), (671, True)
]

@pytest.mark.parametrize("slot, exp_feas", SLOT_CASES)
def test_solver_slot_boundaries(slot, exp_feas):
    plan = solve_plan(
        attempts_remaining=4,
        require_debit=True,
        enforce_fpc=False, # Disable FPC to focus on pure PDN math
        restrict_to_slot=slot
    )
    assert plan.feasible == exp_feas
    if not exp_feas:
        # If it fails strictly due to slot < 48, it's because PDN-01 is violated.
        assert "NPCI-PDN-01" in plan.binding_constraints

# 36-50: Explain Infeasibility Combinations
# Let's pick 15 combinations of binding constraints to test the explainer.
ALL_CONSTRAINTS = [
    "NPCI-ATT-01", "NPCI-PDN-01", "NPCI-PDN-02", "RBI-FPC-01", "SYSTEM-REQ-01"
]
# Generate some combinations
EXPLAIN_CASES = [
    (["NPCI-ATT-01"], ["mandate attempts exhausted (NPCI-ATT-01)"]),
    (["NPCI-PDN-01"], ["unable to schedule 24h pre-debit notification (NPCI-PDN-01)"]),
    (["NPCI-PDN-02"], ["PDN falls into the 23:50 cutoff blackout (NPCI-PDN-02)"]),
    (["RBI-FPC-01"], ["contact falls outside permitted 08:00-19:00 window (RBI-FPC-01)"]),
    (["SYSTEM-REQ-01"], ["no slots available for debit execution (SYSTEM-REQ-01)"]),
    (["NPCI-ATT-01", "NPCI-PDN-01"], ["mandate attempts exhausted", "unable to schedule 24h pre-debit notification"]),
    (["NPCI-PDN-01", "RBI-FPC-01"], ["unable to schedule 24h pre-debit notification", "contact falls outside permitted"]),
    (["NPCI-ATT-01", "SYSTEM-REQ-01"], ["mandate attempts exhausted", "no slots available for debit execution"]),
    (["NPCI-PDN-02", "RBI-FPC-01"], ["23:50 cutoff blackout", "contact falls outside permitted"]),
    (["NPCI-ATT-01", "NPCI-PDN-01", "RBI-FPC-01"], ["mandate attempts exhausted", "unable to schedule 24h pre-debit notification", "contact falls outside permitted"]),
    ([], ["unresolvable constraints"]),
    (["UNKNOWN-RULE"], ["UNKNOWN-RULE"]), # Fallback mapping test
    (["NPCI-ATT-01", "UNKNOWN-RULE"], ["mandate attempts exhausted", "UNKNOWN-RULE"]),
    (ALL_CONSTRAINTS, ["mandate attempts exhausted", "unable to schedule 24h pre-debit", "23:50 cutoff blackout", "contact falls outside permitted", "no slots available for debit execution"]),
    (["TEST-RESTR", "NPCI-ATT-01"], ["mandate attempts exhausted"]), # TEST-RESTR is explicitly filtered out in the explainer
]

@pytest.mark.parametrize("binding, expected_snippets", EXPLAIN_CASES)
def test_explain_infeasibility_combinations(binding, expected_snippets):
    text = explain_infeasibility(binding)
    assert "No legal action available before horizon:" in text
    for snippet in expected_snippets:
        assert snippet in text
