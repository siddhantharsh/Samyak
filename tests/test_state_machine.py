import pytest
from core.state_machine import (
    State,
    allowed_transitions,
    is_terminal,
    transition,
    IllegalTransitionError
)

def test_every_legal_transition():
    # DETECTED
    assert transition(State.DETECTED, State.SUPPRESSED_RECONCILED) == State.SUPPRESSED_RECONCILED
    assert transition(State.DETECTED, State.DIAGNOSED) == State.DIAGNOSED
    
    # DIAGNOSED
    assert transition(State.DIAGNOSED, State.NO_LEGAL_ACTION) == State.NO_LEGAL_ACTION
    assert transition(State.DIAGNOSED, State.PLANNED) == State.PLANNED
    assert transition(State.DIAGNOSED, State.RECOVERED) == State.RECOVERED
    assert transition(State.DIAGNOSED, State.BUDGET_EXHAUSTED) == State.BUDGET_EXHAUSTED
    assert transition(State.DIAGNOSED, State.WRITTEN_OFF) == State.WRITTEN_OFF
    
    # NO_LEGAL_ACTION
    assert transition(State.NO_LEGAL_ACTION, State.HUMAN_ESCALATED) == State.HUMAN_ESCALATED
    
    # PLANNED
    assert transition(State.PLANNED, State.PRE_EMPTED) == State.PRE_EMPTED
    assert transition(State.PLANNED, State.ACTION_DISPATCHED) == State.ACTION_DISPATCHED
    assert transition(State.PLANNED, State.DEFERRED) == State.DEFERRED
    
    # ACTION_DISPATCHED
    assert transition(State.ACTION_DISPATCHED, State.AWAITING_OUTCOME) == State.AWAITING_OUTCOME
    assert transition(State.ACTION_DISPATCHED, State.PROMISE_TO_PAY) == State.PROMISE_TO_PAY
    assert transition(State.ACTION_DISPATCHED, State.DISPUTED) == State.DISPUTED
    assert transition(State.ACTION_DISPATCHED, State.OPTED_OUT) == State.OPTED_OUT

def test_illegal_transitions():
    with pytest.raises(IllegalTransitionError):
        transition(State.DETECTED, State.HUMAN_ESCALATED)
    
    with pytest.raises(IllegalTransitionError):
        transition(State.OPTED_OUT, State.DETECTED)
        
    with pytest.raises(IllegalTransitionError):
        transition(State.PLANNED, State.SUPPRESSED_RECONCILED)

def test_terminal_states_and_reachability():
    # OPTED_OUT is terminal and reachable from ACTION_DISPATCHED
    assert is_terminal(State.OPTED_OUT)
    assert State.OPTED_OUT in allowed_transitions(State.ACTION_DISPATCHED)

    # SUPPRESSED_RECONCILED is terminal and reachable from DETECTED
    assert is_terminal(State.SUPPRESSED_RECONCILED)
    assert State.SUPPRESSED_RECONCILED in allowed_transitions(State.DETECTED)
