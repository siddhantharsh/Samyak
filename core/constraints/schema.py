from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

class CounterCapPredicate(BaseModel):
    kind: Literal["counter_cap"]
    counter: str
    cap: int
    also_min_gap_hours: Optional[int] = None
    condition: Optional[str] = None
    scope: Optional[Union[str, List[str]]] = None

class RequiresPreconditionPredicate(BaseModel):
    kind: Literal["requires_precondition"]
    precondition_action: Optional[str] = None
    lead_hours: Optional[int] = None
    exempt_when: Optional[str] = None
    appended_action: Optional[str] = None
    direction: Optional[str] = None
    prepended_element: Optional[str] = None

class BlackoutPredicate(BaseModel):
    kind: Literal["blackout"]
    start: str
    end: str
    condition: Optional[str] = None

class RequiresStatePredicate(BaseModel):
    kind: Literal["requires_state"]
    state_path: str
    required_value: Union[str, bool]

class ForbiddenWhenPredicate(BaseModel):
    kind: Literal["forbidden_when"]
    condition: str
    rewrite_to: Optional[str] = None
    terminal_state: Optional[str] = None

class TimeWindowPredicate(BaseModel):
    kind: Literal["time_window"]
    forbidden_start: Optional[str] = None
    forbidden_end: Optional[str] = None
    allowed_start: Optional[str] = None
    allowed_end: Optional[str] = None
    condition: Optional[str] = None
    context: Optional[str] = None

class ThresholdPredicate(BaseModel):
    kind: Literal["threshold"]
    field: str
    max: Optional[Union[int, float]] = None
    min: Optional[Union[int, float]] = None
    currency: Optional[str] = None
    condition: Optional[str] = None
    else_require_action: Optional[str] = None
    fallback_max_without_written_agreement: Optional[int] = None
    max_ratio_of: Optional[str] = None
    ratio: Optional[float] = None

class RequiresConsentPredicate(BaseModel):
    kind: Literal["requires_consent"]
    consent_field: str
    check_timing: Optional[str] = None
    must_be_current: Optional[bool] = None

class MinGapPredicate(BaseModel):
    kind: Literal["min_gap"]
    since: str
    min_hours: int

Predicate = Union[
    CounterCapPredicate,
    RequiresPreconditionPredicate,
    BlackoutPredicate,
    RequiresStatePredicate,
    ForbiddenWhenPredicate,
    TimeWindowPredicate,
    ThresholdPredicate,
    RequiresConsentPredicate,
    MinGapPredicate
]

class Rule(BaseModel):
    id: str
    title: str
    source: Optional[str] = None
    citation: Optional[str] = None
    severity: Literal["HARD", "SOFT"]
    penalty_cost: Optional[float] = None
    applies_to: List[str]
    predicate: Predicate = Field(discriminator="kind")
    note: Optional[str] = None
