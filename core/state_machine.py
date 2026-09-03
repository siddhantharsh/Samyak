from enum import Enum
from typing import Dict, Set

class State(str, Enum):
    DETECTED = "DETECTED"
    SUPPRESSED_RECONCILED = "SUPPRESSED_RECONCILED"
    DIAGNOSED = "DIAGNOSED"
    NO_LEGAL_ACTION = "NO_LEGAL_ACTION"
    HUMAN_ESCALATED = "HUMAN_ESCALATED"
    PLANNED = "PLANNED"
    PRE_EMPTED = "PRE_EMPTED"
    ACTION_DISPATCHED = "ACTION_DISPATCHED"
    AWAITING_OUTCOME = "AWAITING_OUTCOME"
    PROMISE_TO_PAY = "PROMISE_TO_PAY"
    DISPUTED = "DISPUTED"
    OPTED_OUT = "OPTED_OUT"
    DEFERRED = "DEFERRED"
    RECOVERED = "RECOVERED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    WRITTEN_OFF = "WRITTEN_OFF"

_TRANSITIONS: Dict[State, Set[State]] = {
    State.DETECTED: {State.SUPPRESSED_RECONCILED, State.DIAGNOSED},
    State.DIAGNOSED: {
        State.NO_LEGAL_ACTION, 
        State.PLANNED, 
        State.RECOVERED, 
        State.BUDGET_EXHAUSTED, 
        State.WRITTEN_OFF
    },
    State.NO_LEGAL_ACTION: {State.HUMAN_ESCALATED},
    State.PLANNED: {State.PRE_EMPTED, State.ACTION_DISPATCHED, State.DEFERRED},
    State.ACTION_DISPATCHED: {
        State.AWAITING_OUTCOME, 
        State.PROMISE_TO_PAY, 
        State.DISPUTED, 
        State.OPTED_OUT
    },
}

_TERMINAL_STATES: Set[State] = {
    State.SUPPRESSED_RECONCILED,
    State.HUMAN_ESCALATED,
    State.PRE_EMPTED,
    State.AWAITING_OUTCOME,
    State.PROMISE_TO_PAY,
    State.DISPUTED,
    State.OPTED_OUT,
    State.DEFERRED,
    State.RECOVERED,
    State.BUDGET_EXHAUSTED,
    State.WRITTEN_OFF
}

class IllegalTransitionError(Exception):
    pass

def allowed_transitions(state: State) -> Set[State]:
    return _TRANSITIONS.get(state, set())

def is_terminal(state: State) -> bool:
    return state in _TERMINAL_STATES

def transition(current: State, next_state: State) -> State:
    if next_state not in allowed_transitions(current):
        raise IllegalTransitionError(f"Cannot transition from {current} to {next_state}")
    return next_state
