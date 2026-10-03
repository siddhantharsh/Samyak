from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

class LeakType(str, Enum):
    PAYMENT_FAIL = "PAYMENT_FAIL"
    CHECKOUT_ABANDON = "CHECKOUT_ABANDON"
    MANDATE_DEBIT_DUE = "MANDATE_DEBIT_DUE"
    MANDATE_FAIL = "MANDATE_FAIL"
    INVOICE_OVERDUE = "INVOICE_OVERDUE"

class Rail(str, Enum):
    UPI_AUTOPAY = "UPI_AUTOPAY"
    CARD_MANDATE = "CARD_MANDATE"
    UPI_COLLECT = "UPI_COLLECT"
    NETBANKING = "NETBANKING"
    NEFT_RTGS = "NEFT_RTGS"
    NONE = "NONE"

class RawCodes(BaseModel):
    gateway_code: Optional[str] = None
    issuer_code: Optional[str] = None
    network_category: Optional[str] = None
    mac: Optional[str] = None
    npci_code: Optional[str] = None

class Context(BaseModel):
    mandate_id: Optional[str] = None
    invoice_id: Optional[str] = None
    cart_id: Optional[str] = None
    attempt_index: Optional[int] = None
    cycle_id: Optional[str] = None

class LeakEvent(BaseModel):
    id: str
    tenant_id: str
    leak_type: LeakType
    subject_ref: str
    amount: float
    currency: str
    due_at: datetime
    occurred_at: datetime
    rail: Rail
    raw_codes: RawCodes
    context: Context
    idempotency_key: str

class Subject(BaseModel):
    id: str
    contact_channels: List[str]
    language_pref: str
    consent_state: Dict[str, Any]
    dnd_status: str
    suppression_flags: List[str]
    is_udyam_supplier_relationship: bool
    contact_history: List[Dict[str, Any]]
    timezone: str

class Layer(str, Enum):
    L1_DETERMINISTIC = "L1_DETERMINISTIC"
    L2_INFERRED = "L2_INFERRED"
    UNRESOLVED = "UNRESOLVED"

class Diagnosis(BaseModel):
    root_cause: str
    layer: Layer
    confidence: float
    permitted_action_classes: Set[str]
    evidence: List[str]

class ConstraintSnapshot(BaseModel):
    register_version: str
    attempt_counters: Dict[str, int]
    consent_state: Dict[str, Any]
    window_state: Dict[str, Any]
    template_registry_version: str
    budget_remaining: float

class PlannedAction(BaseModel):
    kind: str
    scheduled_at: datetime
    channel: str
    template_id: Optional[str]
    variables: Dict[str, Any]
    precondition_step_ids: List[str]

class ActionPlan(BaseModel):
    steps: List[PlannedAction] = []
    feasible: bool
    binding_constraints: List[str] = []
    ev_net: Optional[Decimal] = None
    solver_stats: Optional[Dict[str, Any]] = None

class Arm(str, Enum):
    TREATMENT = "TREATMENT"
    HOLDOUT = "HOLDOUT"

class DecisionRecord(BaseModel):
    seq: int
    prev_hash: str
    hash: str
    event_id: str
    diagnosis: Diagnosis
    constraint_snapshot_digest: str
    considered_plans: List[ActionPlan]
    chosen_plan: Optional[ActionPlan]
    refusals: List[Tuple[str, str, str]]
    policy_version: str
    model_versions: Dict[str, str]
    prompt_hash: Optional[str]
    input_digest: str
    responsible_entity_id: str
    timestamp: datetime
    arm: Arm
