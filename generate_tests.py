import yaml
from jinja2 import Template

with open("data/constraints.yaml") as f:
    data = yaml.safe_load(f)

rules = data.get("rules", [])

test_template = """
def test_{{ safe_id }}():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "{{ rule_id }}"), None)
    assert rule is not None, "Rule {{ rule_id }} not found"

    # passing case
    snapshot = ConstraintSnapshot(
        register_version="1",
        attempt_counters={},
        consent_state={"communication_consent": True, "explicit_mandate_creation": True, "mandate_active": True},
        window_state={},
        template_registry_version="1",
        budget_remaining=100.0
    )
    action = PlannedAction(
        kind=rule.applies_to[0] if rule.applies_to else "TEST",
        scheduled_at=datetime.utcnow(),
        channel="TEST",
        template_id=None,
        variables={
            "amount": 10,
            "days_since_acceptance": 10,
            "days_overdue": 5,
            "cumulative_action_cost": 5,
            "amount_recoverable": 100,
            "invoice_amount": 100,
            "received_amount": 80,
            "expected_tds": 0,
            "subject": {"dnd_status": "UNREGISTERED", "opted_out": False, "is_udyam_supplier_relationship": False, "suppression_flags": []},
            "decline": {"mac": "00", "network_category": "00", "npci_code": "00", "visa_category": 0},
            "merchant": {"category": "RETAIL"},
            "message": {"category": "TRANSACTIONAL", "scrub_verdict": "PASS", "urls_whitelisted": True},
            "mandate": {"status": "ACTIVE", "first_presentation_failed": False},
            "pdn": {"status": "SUCCESS"},
            "debit_date": "T+2",
            "recipient": "debtor",
            "action": {"responsible_entity_id": "valid_entity"},
            "llm_input": {"pii_tokenised": True},
            "elements": ["AI_DISCLOSURE"],
            "_has_appended": True
        },
        precondition_step_ids=[getattr(rule.predicate, "precondition_action", "")] if getattr(rule.predicate, "precondition_action", None) else []
    )
    passed, reason = evaluate_predicate(rule.predicate, snapshot, action)
    assert passed is True, f"Failed passing case for {{ rule_id }}: {reason}"

    # failing case
    snapshot2 = ConstraintSnapshot(
        register_version="1",
        attempt_counters={getattr(rule.predicate, "counter", ""): 999} if getattr(rule.predicate, "counter", None) else {},
        consent_state={"communication_consent": False, "explicit_mandate_creation": False, "mandate_active": False},
        window_state={},
        template_registry_version="1",
        budget_remaining=100.0
    )
    action2 = PlannedAction(
        kind=rule.applies_to[0] if rule.applies_to else "TEST",
        scheduled_at=datetime.utcnow(),
        channel="TEST",
        template_id=None,
        variables={
            "amount": 9999999,
            "days_since_acceptance": 999,
            "days_overdue": 0,
            "cumulative_action_cost": 999,
            "amount_recoverable": 10,
            "invoice_amount": 100,
            "received_amount": 100,
            "expected_tds": 0,
            "subject": {"dnd_status": "REGISTERED", "opted_out": True, "is_udyam_supplier_relationship": True, "suppression_flags": ["CALAMITOUS_TIMING"]},
            "decline": {"mac": "03" if "{{ rule_id }}" == "NET-MC-03" else "21" if "{{ rule_id }}" == "NET-MC-04" else "02", "network_category": "1" if "{{ rule_id }}" == "NET-VISA-01" else "3" if "{{ rule_id }}" == "NET-VISA-03" else "00", "npci_code": "U16" if "{{ rule_id }}" == "NPCI-MND-01" else "00", "visa_category": 1 if "{{ rule_id }}" == "NET-VISA-01" else None if "{{ rule_id }}" == "NET-VISA-03" else 0},
            "merchant": {"category": "LENDING"},
            "message": {"category": "UNKNOWN", "scrub_verdict": "FAIL", "urls_whitelisted": False},
            "mandate": {"status": "INACTIVE", "first_presentation_failed": True},
            "pdn": {"status": "FAIL"},
            "debit_date": "T+1",
            "recipient": "employer",
            "action": {"responsible_entity_id": None},
            "llm_input": {"pii_tokenised": False},
            "elements": [],
            "_is_blackout": True,
            "_out_of_time_window": True,
            "_gap_too_small": True,
            "_has_appended": False
        },
        precondition_step_ids=[]
    )
    
    if rule.id == "RBI-EM-01":
        action2.variables["merchant"] = {"category": "RETAIL"}
    elif rule.id == "RBI-EM-02":
        action2.variables["merchant"] = {"category": "INSURANCE"}
    if rule.id == "NET-MC-01":
        action2.variables["decline"]["mac"] = "01"
    if rule.id == "TRAI-TIME-01":
        action2.variables["message"]["category"] = "PROMOTIONAL"
    if rule.id == "TRAI-DND-01":
        action2.variables["message"]["category"] = "PROMOTIONAL"
    if rule.id == "RBI-FPC-03":
        action2.variables["action"] = {"channel": "VOICE_CALL", "responsible_entity_id": None}
        action2.variables["contact_channel"] = "VOICE_CALL"
        action2.variables["subject"]["contact_channels"] = ["SMS_SEND"]
    if rule.id == "NET-VISA-03":
        action2.variables["decline"]["mac"] = None

    passed, reason = evaluate_predicate(rule.predicate, snapshot2, action2)
    assert passed is False, f"Failed failing case for {{ rule_id }}"
"""

header = """import pytest
from datetime import datetime
from decimal import Decimal
from core.constraints.register import Register
from core.entities import ConstraintSnapshot, PlannedAction
from core.constraints.predicates import evaluate_predicate

"""

with open("tests/test_constraints.py", "w") as out:
    out.write(header)
    for r in rules:
        safe_id = r["id"].replace("-", "_")
        out.write(Template(test_template).render(rule_id=r["id"], safe_id=safe_id))

print("Generated tests/test_constraints.py")
