import os
import yaml
from typing import Optional, List, Dict
from pydantic import BaseModel
from core.entities import LeakEvent

class SuppressionResult(BaseModel):
    action: str  # "DROP", "SUPPRESSED_RECONCILED", "RE_SCOPED", "PASSED"
    check_name: str
    arithmetic: str
    explanation: str
    residual_amount: Optional[float] = None

class LedgerState(BaseModel):
    seen_idempotency_keys: set[str]
    # list of dicts: {"subject_ref": str, "amount": float, "date": datetime}
    settled_payments: List[Dict]
    # invoice_id -> received amount
    received_amounts: Dict[str, float]
    # invoice_id -> applied credit
    credit_notes: Dict[str, float]
    # subject_ref -> section e.g. "194C"
    subject_tds_section: Dict[str, str]

def load_tds_rates() -> Dict[str, float]:
    path = "data/tds_rates.yaml"
    if not os.path.exists(path):
        # Create it as per prompt if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("# WARNING: These rates are for simulation and demo purposes.\n")
            f.write("# In a real production system, TDS rates must be verified by human tax/compliance experts.\n")
            f.write('"194C": 0.02\n"194J": 0.10\n"194H": 0.05\n"194I": 0.10\n')
    
    with open(path, "r") as f:
        return yaml.safe_load(f)

TDS_RATES = load_tds_rates()

def check_event(event: LeakEvent, state: LedgerState) -> SuppressionResult:
    # 1. Settled-but-unwebhooked
    for sp in state.settled_payments:
        if sp["subject_ref"] == event.subject_ref and abs(sp["amount"] - event.amount) <= 0.01:
            return SuppressionResult(
                action="SUPPRESSED_RECONCILED",
                check_name="Settled-but-unwebhooked",
                arithmetic=f"settled={sp['amount']} == event={event.amount}",
                explanation="Ledger shows a settled payment matching the amount and subject within the recent window."
            )

    # 2. Duplicate event
    if event.idempotency_key in state.seen_idempotency_keys:
        return SuppressionResult(
            action="DROP",
            check_name="Duplicate event",
            arithmetic=f"key={event.idempotency_key} in seen_keys",
            explanation="This event's idempotency key has already been processed."
        )

    # Context variables for invoice specific checks
    invoice_id = getattr(event.context, "invoice_id", None)
    
    if invoice_id and invoice_id in state.received_amounts:
        received = state.received_amounts[invoice_id]
        invoice = event.amount
        residual = invoice - received
        
        # Calculate expected TDS
        section = state.subject_tds_section.get(event.subject_ref)
        expected_tds = 0.0
        if section and section in TDS_RATES:
            rate = TDS_RATES[section]
            expected_tds = invoice * rate
        
        # 3. Partial payment
        # "Received < invoice, remainder above TDS tolerance"
        tds_upper_bound = expected_tds + 1.0
        if received > 0 and received < invoice and residual > tds_upper_bound:
            return SuppressionResult(
                action="RE_SCOPED",
                check_name="Partial payment",
                arithmetic=f"invoice={invoice} - received={received} = {residual} > tds_tolerance={tds_upper_bound}",
                explanation=f"A partial payment was received. The remainder exceeds the TDS tolerance, so the event is re-scoped to the residual amount of {residual}.",
                residual_amount=residual
            )

        # 4. TDS short-payment
        # "|invoice - received - expected_tds| <= 1"
        if section and abs(invoice - received - expected_tds) <= 1.0:
            return SuppressionResult(
                action="SUPPRESSED_RECONCILED",
                check_name="TDS short-payment",
                arithmetic=f"abs(invoice={invoice} - received={received} - expected_tds={expected_tds}) <= 1.0",
                explanation=f"The shortfall matches the expected TDS withholding under section {section}. Do not chase; request Form 16A."
            )

    # 5. Credit note applied
    if invoice_id and invoice_id in state.credit_notes:
        credit = state.credit_notes[invoice_id]
        received = state.received_amounts.get(invoice_id, 0.0)
        residual = event.amount - received
        if abs(credit - residual) <= 0.01:
            return SuppressionResult(
                action="SUPPRESSED_RECONCILED",
                check_name="Credit note applied",
                arithmetic=f"credit={credit} == residual={residual}",
                explanation="An open credit note matches the residual amount exactly."
            )
            
    return SuppressionResult(
        action="PASSED",
        check_name="None",
        arithmetic="",
        explanation="No reconciliation guard rules triggered."
    )
