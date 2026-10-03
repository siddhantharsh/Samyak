import pytest
from datetime import datetime
from decimal import Decimal
from core.constraints.register import Register
from core.entities import ConstraintSnapshot, PlannedAction
from core.constraints.predicates import evaluate_predicate


def test_NPCI_ATT_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NPCI-ATT-01"), None)
    assert rule is not None, "Rule NPCI-ATT-01 not found"

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
    assert passed is True, f"Failed passing case for NPCI-ATT-01: {reason}"

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
            "decline": {"mac": "03" if "NPCI-ATT-01" == "NET-MC-03" else "21" if "NPCI-ATT-01" == "NET-MC-04" else "02", "network_category": "1" if "NPCI-ATT-01" == "NET-VISA-01" else "3" if "NPCI-ATT-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "NPCI-ATT-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "NPCI-ATT-01" == "NET-VISA-01" else None if "NPCI-ATT-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NPCI-ATT-01"
def test_NPCI_PDN_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NPCI-PDN-01"), None)
    assert rule is not None, "Rule NPCI-PDN-01 not found"

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
    assert passed is True, f"Failed passing case for NPCI-PDN-01: {reason}"

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
            "decline": {"mac": "03" if "NPCI-PDN-01" == "NET-MC-03" else "21" if "NPCI-PDN-01" == "NET-MC-04" else "02", "network_category": "1" if "NPCI-PDN-01" == "NET-VISA-01" else "3" if "NPCI-PDN-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "NPCI-PDN-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "NPCI-PDN-01" == "NET-VISA-01" else None if "NPCI-PDN-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NPCI-PDN-01"
def test_NPCI_PDN_02():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NPCI-PDN-02"), None)
    assert rule is not None, "Rule NPCI-PDN-02 not found"

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
    assert passed is True, f"Failed passing case for NPCI-PDN-02: {reason}"

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
            "decline": {"mac": "03" if "NPCI-PDN-02" == "NET-MC-03" else "21" if "NPCI-PDN-02" == "NET-MC-04" else "02", "network_category": "1" if "NPCI-PDN-02" == "NET-VISA-01" else "3" if "NPCI-PDN-02" == "NET-VISA-03" else "00", "npci_code": "U16" if "NPCI-PDN-02" == "NPCI-MND-01" else "00", "visa_category": 1 if "NPCI-PDN-02" == "NET-VISA-01" else None if "NPCI-PDN-02" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NPCI-PDN-02"
def test_NPCI_PDN_03():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NPCI-PDN-03"), None)
    assert rule is not None, "Rule NPCI-PDN-03 not found"

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
    assert passed is True, f"Failed passing case for NPCI-PDN-03: {reason}"

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
            "decline": {"mac": "03" if "NPCI-PDN-03" == "NET-MC-03" else "21" if "NPCI-PDN-03" == "NET-MC-04" else "02", "network_category": "1" if "NPCI-PDN-03" == "NET-VISA-01" else "3" if "NPCI-PDN-03" == "NET-VISA-03" else "00", "npci_code": "U16" if "NPCI-PDN-03" == "NPCI-MND-01" else "00", "visa_category": 1 if "NPCI-PDN-03" == "NET-VISA-01" else None if "NPCI-PDN-03" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NPCI-PDN-03"
def test_NPCI_MND_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NPCI-MND-01"), None)
    assert rule is not None, "Rule NPCI-MND-01 not found"

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
    assert passed is True, f"Failed passing case for NPCI-MND-01: {reason}"

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
            "decline": {"mac": "03" if "NPCI-MND-01" == "NET-MC-03" else "21" if "NPCI-MND-01" == "NET-MC-04" else "02", "network_category": "1" if "NPCI-MND-01" == "NET-VISA-01" else "3" if "NPCI-MND-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "NPCI-MND-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "NPCI-MND-01" == "NET-VISA-01" else None if "NPCI-MND-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NPCI-MND-01"
def test_NPCI_PEAK_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NPCI-PEAK-01"), None)
    assert rule is not None, "Rule NPCI-PEAK-01 not found"

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
    assert passed is True, f"Failed passing case for NPCI-PEAK-01: {reason}"

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
            "decline": {"mac": "03" if "NPCI-PEAK-01" == "NET-MC-03" else "21" if "NPCI-PEAK-01" == "NET-MC-04" else "02", "network_category": "1" if "NPCI-PEAK-01" == "NET-VISA-01" else "3" if "NPCI-PEAK-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "NPCI-PEAK-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "NPCI-PEAK-01" == "NET-VISA-01" else None if "NPCI-PEAK-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NPCI-PEAK-01"
def test_NPCI_MIT_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NPCI-MIT-01"), None)
    assert rule is not None, "Rule NPCI-MIT-01 not found"

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
    assert passed is True, f"Failed passing case for NPCI-MIT-01: {reason}"

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
            "decline": {"mac": "03" if "NPCI-MIT-01" == "NET-MC-03" else "21" if "NPCI-MIT-01" == "NET-MC-04" else "02", "network_category": "1" if "NPCI-MIT-01" == "NET-VISA-01" else "3" if "NPCI-MIT-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "NPCI-MIT-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "NPCI-MIT-01" == "NET-VISA-01" else None if "NPCI-MIT-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NPCI-MIT-01"
def test_RBI_EM_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "RBI-EM-01"), None)
    assert rule is not None, "Rule RBI-EM-01 not found"

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
    assert passed is True, f"Failed passing case for RBI-EM-01: {reason}"

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
            "decline": {"mac": "03" if "RBI-EM-01" == "NET-MC-03" else "21" if "RBI-EM-01" == "NET-MC-04" else "02", "network_category": "1" if "RBI-EM-01" == "NET-VISA-01" else "3" if "RBI-EM-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "RBI-EM-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "RBI-EM-01" == "NET-VISA-01" else None if "RBI-EM-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for RBI-EM-01"
def test_RBI_EM_02():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "RBI-EM-02"), None)
    assert rule is not None, "Rule RBI-EM-02 not found"

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
    assert passed is True, f"Failed passing case for RBI-EM-02: {reason}"

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
            "decline": {"mac": "03" if "RBI-EM-02" == "NET-MC-03" else "21" if "RBI-EM-02" == "NET-MC-04" else "02", "network_category": "1" if "RBI-EM-02" == "NET-VISA-01" else "3" if "RBI-EM-02" == "NET-VISA-03" else "00", "npci_code": "U16" if "RBI-EM-02" == "NPCI-MND-01" else "00", "visa_category": 1 if "RBI-EM-02" == "NET-VISA-01" else None if "RBI-EM-02" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for RBI-EM-02"
def test_RBI_EM_03():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "RBI-EM-03"), None)
    assert rule is not None, "Rule RBI-EM-03 not found"

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
    assert passed is True, f"Failed passing case for RBI-EM-03: {reason}"

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
            "decline": {"mac": "03" if "RBI-EM-03" == "NET-MC-03" else "21" if "RBI-EM-03" == "NET-MC-04" else "02", "network_category": "1" if "RBI-EM-03" == "NET-VISA-01" else "3" if "RBI-EM-03" == "NET-VISA-03" else "00", "npci_code": "U16" if "RBI-EM-03" == "NPCI-MND-01" else "00", "visa_category": 1 if "RBI-EM-03" == "NET-VISA-01" else None if "RBI-EM-03" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for RBI-EM-03"
def test_RBI_EM_04():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "RBI-EM-04"), None)
    assert rule is not None, "Rule RBI-EM-04 not found"

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
    assert passed is True, f"Failed passing case for RBI-EM-04: {reason}"

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
            "decline": {"mac": "03" if "RBI-EM-04" == "NET-MC-03" else "21" if "RBI-EM-04" == "NET-MC-04" else "02", "network_category": "1" if "RBI-EM-04" == "NET-VISA-01" else "3" if "RBI-EM-04" == "NET-VISA-03" else "00", "npci_code": "U16" if "RBI-EM-04" == "NPCI-MND-01" else "00", "visa_category": 1 if "RBI-EM-04" == "NET-VISA-01" else None if "RBI-EM-04" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for RBI-EM-04"
def test_RBI_FPC_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "RBI-FPC-01"), None)
    assert rule is not None, "Rule RBI-FPC-01 not found"

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
    assert passed is True, f"Failed passing case for RBI-FPC-01: {reason}"

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
            "decline": {"mac": "03" if "RBI-FPC-01" == "NET-MC-03" else "21" if "RBI-FPC-01" == "NET-MC-04" else "02", "network_category": "1" if "RBI-FPC-01" == "NET-VISA-01" else "3" if "RBI-FPC-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "RBI-FPC-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "RBI-FPC-01" == "NET-VISA-01" else None if "RBI-FPC-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for RBI-FPC-01"
def test_RBI_FPC_02():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "RBI-FPC-02"), None)
    assert rule is not None, "Rule RBI-FPC-02 not found"

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
    assert passed is True, f"Failed passing case for RBI-FPC-02: {reason}"

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
            "decline": {"mac": "03" if "RBI-FPC-02" == "NET-MC-03" else "21" if "RBI-FPC-02" == "NET-MC-04" else "02", "network_category": "1" if "RBI-FPC-02" == "NET-VISA-01" else "3" if "RBI-FPC-02" == "NET-VISA-03" else "00", "npci_code": "U16" if "RBI-FPC-02" == "NPCI-MND-01" else "00", "visa_category": 1 if "RBI-FPC-02" == "NET-VISA-01" else None if "RBI-FPC-02" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for RBI-FPC-02"
def test_RBI_FPC_03():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "RBI-FPC-03"), None)
    assert rule is not None, "Rule RBI-FPC-03 not found"

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
    assert passed is True, f"Failed passing case for RBI-FPC-03: {reason}"

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
            "decline": {"mac": "03" if "RBI-FPC-03" == "NET-MC-03" else "21" if "RBI-FPC-03" == "NET-MC-04" else "02", "network_category": "1" if "RBI-FPC-03" == "NET-VISA-01" else "3" if "RBI-FPC-03" == "NET-VISA-03" else "00", "npci_code": "U16" if "RBI-FPC-03" == "NPCI-MND-01" else "00", "visa_category": 1 if "RBI-FPC-03" == "NET-VISA-01" else None if "RBI-FPC-03" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for RBI-FPC-03"
def test_RBI_FPC_04():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "RBI-FPC-04"), None)
    assert rule is not None, "Rule RBI-FPC-04 not found"

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
    assert passed is True, f"Failed passing case for RBI-FPC-04: {reason}"

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
            "decline": {"mac": "03" if "RBI-FPC-04" == "NET-MC-03" else "21" if "RBI-FPC-04" == "NET-MC-04" else "02", "network_category": "1" if "RBI-FPC-04" == "NET-VISA-01" else "3" if "RBI-FPC-04" == "NET-VISA-03" else "00", "npci_code": "U16" if "RBI-FPC-04" == "NPCI-MND-01" else "00", "visa_category": 1 if "RBI-FPC-04" == "NET-VISA-01" else None if "RBI-FPC-04" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for RBI-FPC-04"
def test_NET_VISA_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NET-VISA-01"), None)
    assert rule is not None, "Rule NET-VISA-01 not found"

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
    assert passed is True, f"Failed passing case for NET-VISA-01: {reason}"

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
            "decline": {"mac": "03" if "NET-VISA-01" == "NET-MC-03" else "21" if "NET-VISA-01" == "NET-MC-04" else "02", "network_category": "1" if "NET-VISA-01" == "NET-VISA-01" else "3" if "NET-VISA-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "NET-VISA-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "NET-VISA-01" == "NET-VISA-01" else None if "NET-VISA-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NET-VISA-01"
def test_NET_VISA_02():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NET-VISA-02"), None)
    assert rule is not None, "Rule NET-VISA-02 not found"

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
    assert passed is True, f"Failed passing case for NET-VISA-02: {reason}"

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
            "decline": {"mac": "03" if "NET-VISA-02" == "NET-MC-03" else "21" if "NET-VISA-02" == "NET-MC-04" else "02", "network_category": "1" if "NET-VISA-02" == "NET-VISA-01" else "3" if "NET-VISA-02" == "NET-VISA-03" else "00", "npci_code": "U16" if "NET-VISA-02" == "NPCI-MND-01" else "00", "visa_category": 1 if "NET-VISA-02" == "NET-VISA-01" else None if "NET-VISA-02" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NET-VISA-02"
def test_NET_VISA_03():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NET-VISA-03"), None)
    assert rule is not None, "Rule NET-VISA-03 not found"

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
    assert passed is True, f"Failed passing case for NET-VISA-03: {reason}"

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
            "decline": {"mac": "03" if "NET-VISA-03" == "NET-MC-03" else "21" if "NET-VISA-03" == "NET-MC-04" else "02", "network_category": "1" if "NET-VISA-03" == "NET-VISA-01" else "3" if "NET-VISA-03" == "NET-VISA-03" else "00", "npci_code": "U16" if "NET-VISA-03" == "NPCI-MND-01" else "00", "visa_category": 1 if "NET-VISA-03" == "NET-VISA-01" else None if "NET-VISA-03" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NET-VISA-03"
def test_NET_MC_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NET-MC-01"), None)
    assert rule is not None, "Rule NET-MC-01 not found"

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
    assert passed is True, f"Failed passing case for NET-MC-01: {reason}"

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
            "decline": {"mac": "03" if "NET-MC-01" == "NET-MC-03" else "21" if "NET-MC-01" == "NET-MC-04" else "02", "network_category": "1" if "NET-MC-01" == "NET-VISA-01" else "3" if "NET-MC-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "NET-MC-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "NET-MC-01" == "NET-VISA-01" else None if "NET-MC-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NET-MC-01"
def test_NET_MC_02():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NET-MC-02"), None)
    assert rule is not None, "Rule NET-MC-02 not found"

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
    assert passed is True, f"Failed passing case for NET-MC-02: {reason}"

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
            "decline": {"mac": "03" if "NET-MC-02" == "NET-MC-03" else "21" if "NET-MC-02" == "NET-MC-04" else "02", "network_category": "1" if "NET-MC-02" == "NET-VISA-01" else "3" if "NET-MC-02" == "NET-VISA-03" else "00", "npci_code": "U16" if "NET-MC-02" == "NPCI-MND-01" else "00", "visa_category": 1 if "NET-MC-02" == "NET-VISA-01" else None if "NET-MC-02" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NET-MC-02"
def test_NET_MC_03():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NET-MC-03"), None)
    assert rule is not None, "Rule NET-MC-03 not found"

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
    assert passed is True, f"Failed passing case for NET-MC-03: {reason}"

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
            "decline": {"mac": "03" if "NET-MC-03" == "NET-MC-03" else "21" if "NET-MC-03" == "NET-MC-04" else "02", "network_category": "1" if "NET-MC-03" == "NET-VISA-01" else "3" if "NET-MC-03" == "NET-VISA-03" else "00", "npci_code": "U16" if "NET-MC-03" == "NPCI-MND-01" else "00", "visa_category": 1 if "NET-MC-03" == "NET-VISA-01" else None if "NET-MC-03" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NET-MC-03"
def test_NET_MC_04():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NET-MC-04"), None)
    assert rule is not None, "Rule NET-MC-04 not found"

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
    assert passed is True, f"Failed passing case for NET-MC-04: {reason}"

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
            "decline": {"mac": "03" if "NET-MC-04" == "NET-MC-03" else "21" if "NET-MC-04" == "NET-MC-04" else "02", "network_category": "1" if "NET-MC-04" == "NET-VISA-01" else "3" if "NET-MC-04" == "NET-VISA-03" else "00", "npci_code": "U16" if "NET-MC-04" == "NPCI-MND-01" else "00", "visa_category": 1 if "NET-MC-04" == "NET-VISA-01" else None if "NET-MC-04" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NET-MC-04"
def test_NET_SOFT_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "NET-SOFT-01"), None)
    assert rule is not None, "Rule NET-SOFT-01 not found"

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
    assert passed is True, f"Failed passing case for NET-SOFT-01: {reason}"

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
            "decline": {"mac": "03" if "NET-SOFT-01" == "NET-MC-03" else "21" if "NET-SOFT-01" == "NET-MC-04" else "02", "network_category": "1" if "NET-SOFT-01" == "NET-VISA-01" else "3" if "NET-SOFT-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "NET-SOFT-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "NET-SOFT-01" == "NET-VISA-01" else None if "NET-SOFT-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for NET-SOFT-01"
def test_TRAI_TIME_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "TRAI-TIME-01"), None)
    assert rule is not None, "Rule TRAI-TIME-01 not found"

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
    assert passed is True, f"Failed passing case for TRAI-TIME-01: {reason}"

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
            "decline": {"mac": "03" if "TRAI-TIME-01" == "NET-MC-03" else "21" if "TRAI-TIME-01" == "NET-MC-04" else "02", "network_category": "1" if "TRAI-TIME-01" == "NET-VISA-01" else "3" if "TRAI-TIME-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "TRAI-TIME-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "TRAI-TIME-01" == "NET-VISA-01" else None if "TRAI-TIME-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for TRAI-TIME-01"
def test_TRAI_DLT_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "TRAI-DLT-01"), None)
    assert rule is not None, "Rule TRAI-DLT-01 not found"

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
    assert passed is True, f"Failed passing case for TRAI-DLT-01: {reason}"

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
            "decline": {"mac": "03" if "TRAI-DLT-01" == "NET-MC-03" else "21" if "TRAI-DLT-01" == "NET-MC-04" else "02", "network_category": "1" if "TRAI-DLT-01" == "NET-VISA-01" else "3" if "TRAI-DLT-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "TRAI-DLT-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "TRAI-DLT-01" == "NET-VISA-01" else None if "TRAI-DLT-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for TRAI-DLT-01"
def test_TRAI_DLT_02():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "TRAI-DLT-02"), None)
    assert rule is not None, "Rule TRAI-DLT-02 not found"

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
    assert passed is True, f"Failed passing case for TRAI-DLT-02: {reason}"

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
            "decline": {"mac": "03" if "TRAI-DLT-02" == "NET-MC-03" else "21" if "TRAI-DLT-02" == "NET-MC-04" else "02", "network_category": "1" if "TRAI-DLT-02" == "NET-VISA-01" else "3" if "TRAI-DLT-02" == "NET-VISA-03" else "00", "npci_code": "U16" if "TRAI-DLT-02" == "NPCI-MND-01" else "00", "visa_category": 1 if "TRAI-DLT-02" == "NET-VISA-01" else None if "TRAI-DLT-02" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for TRAI-DLT-02"
def test_TRAI_DLT_03():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "TRAI-DLT-03"), None)
    assert rule is not None, "Rule TRAI-DLT-03 not found"

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
    assert passed is True, f"Failed passing case for TRAI-DLT-03: {reason}"

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
            "decline": {"mac": "03" if "TRAI-DLT-03" == "NET-MC-03" else "21" if "TRAI-DLT-03" == "NET-MC-04" else "02", "network_category": "1" if "TRAI-DLT-03" == "NET-VISA-01" else "3" if "TRAI-DLT-03" == "NET-VISA-03" else "00", "npci_code": "U16" if "TRAI-DLT-03" == "NPCI-MND-01" else "00", "visa_category": 1 if "TRAI-DLT-03" == "NET-VISA-01" else None if "TRAI-DLT-03" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for TRAI-DLT-03"
def test_TRAI_DND_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "TRAI-DND-01"), None)
    assert rule is not None, "Rule TRAI-DND-01 not found"

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
    assert passed is True, f"Failed passing case for TRAI-DND-01: {reason}"

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
            "decline": {"mac": "03" if "TRAI-DND-01" == "NET-MC-03" else "21" if "TRAI-DND-01" == "NET-MC-04" else "02", "network_category": "1" if "TRAI-DND-01" == "NET-VISA-01" else "3" if "TRAI-DND-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "TRAI-DND-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "TRAI-DND-01" == "NET-VISA-01" else None if "TRAI-DND-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for TRAI-DND-01"
def test_DPDP_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "DPDP-01"), None)
    assert rule is not None, "Rule DPDP-01 not found"

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
    assert passed is True, f"Failed passing case for DPDP-01: {reason}"

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
            "decline": {"mac": "03" if "DPDP-01" == "NET-MC-03" else "21" if "DPDP-01" == "NET-MC-04" else "02", "network_category": "1" if "DPDP-01" == "NET-VISA-01" else "3" if "DPDP-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "DPDP-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "DPDP-01" == "NET-VISA-01" else None if "DPDP-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for DPDP-01"
def test_DPDP_02():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "DPDP-02"), None)
    assert rule is not None, "Rule DPDP-02 not found"

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
    assert passed is True, f"Failed passing case for DPDP-02: {reason}"

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
            "decline": {"mac": "03" if "DPDP-02" == "NET-MC-03" else "21" if "DPDP-02" == "NET-MC-04" else "02", "network_category": "1" if "DPDP-02" == "NET-VISA-01" else "3" if "DPDP-02" == "NET-VISA-03" else "00", "npci_code": "U16" if "DPDP-02" == "NPCI-MND-01" else "00", "visa_category": 1 if "DPDP-02" == "NET-VISA-01" else None if "DPDP-02" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for DPDP-02"
def test_AI_DISC_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "AI-DISC-01"), None)
    assert rule is not None, "Rule AI-DISC-01 not found"

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
    assert passed is True, f"Failed passing case for AI-DISC-01: {reason}"

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
            "decline": {"mac": "03" if "AI-DISC-01" == "NET-MC-03" else "21" if "AI-DISC-01" == "NET-MC-04" else "02", "network_category": "1" if "AI-DISC-01" == "NET-VISA-01" else "3" if "AI-DISC-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "AI-DISC-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "AI-DISC-01" == "NET-VISA-01" else None if "AI-DISC-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for AI-DISC-01"
def test_MSME_43BH_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "MSME-43BH-01"), None)
    assert rule is not None, "Rule MSME-43BH-01 not found"

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
    assert passed is True, f"Failed passing case for MSME-43BH-01: {reason}"

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
            "decline": {"mac": "03" if "MSME-43BH-01" == "NET-MC-03" else "21" if "MSME-43BH-01" == "NET-MC-04" else "02", "network_category": "1" if "MSME-43BH-01" == "NET-VISA-01" else "3" if "MSME-43BH-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "MSME-43BH-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "MSME-43BH-01" == "NET-VISA-01" else None if "MSME-43BH-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for MSME-43BH-01"
def test_MSME_16_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "MSME-16-01"), None)
    assert rule is not None, "Rule MSME-16-01 not found"

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
    assert passed is True, f"Failed passing case for MSME-16-01: {reason}"

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
            "decline": {"mac": "03" if "MSME-16-01" == "NET-MC-03" else "21" if "MSME-16-01" == "NET-MC-04" else "02", "network_category": "1" if "MSME-16-01" == "NET-VISA-01" else "3" if "MSME-16-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "MSME-16-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "MSME-16-01" == "NET-VISA-01" else None if "MSME-16-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for MSME-16-01"
def test_MSME_TDS_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "MSME-TDS-01"), None)
    assert rule is not None, "Rule MSME-TDS-01 not found"

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
    assert passed is True, f"Failed passing case for MSME-TDS-01: {reason}"

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
            "decline": {"mac": "03" if "MSME-TDS-01" == "NET-MC-03" else "21" if "MSME-TDS-01" == "NET-MC-04" else "02", "network_category": "1" if "MSME-TDS-01" == "NET-VISA-01" else "3" if "MSME-TDS-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "MSME-TDS-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "MSME-TDS-01" == "NET-VISA-01" else None if "MSME-TDS-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for MSME-TDS-01"
def test_POL_FATIGUE_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "POL-FATIGUE-01"), None)
    assert rule is not None, "Rule POL-FATIGUE-01 not found"

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
    assert passed is True, f"Failed passing case for POL-FATIGUE-01: {reason}"

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
            "decline": {"mac": "03" if "POL-FATIGUE-01" == "NET-MC-03" else "21" if "POL-FATIGUE-01" == "NET-MC-04" else "02", "network_category": "1" if "POL-FATIGUE-01" == "NET-VISA-01" else "3" if "POL-FATIGUE-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "POL-FATIGUE-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "POL-FATIGUE-01" == "NET-VISA-01" else None if "POL-FATIGUE-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for POL-FATIGUE-01"
def test_POL_OPTOUT_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "POL-OPTOUT-01"), None)
    assert rule is not None, "Rule POL-OPTOUT-01 not found"

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
    assert passed is True, f"Failed passing case for POL-OPTOUT-01: {reason}"

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
            "decline": {"mac": "03" if "POL-OPTOUT-01" == "NET-MC-03" else "21" if "POL-OPTOUT-01" == "NET-MC-04" else "02", "network_category": "1" if "POL-OPTOUT-01" == "NET-VISA-01" else "3" if "POL-OPTOUT-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "POL-OPTOUT-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "POL-OPTOUT-01" == "NET-VISA-01" else None if "POL-OPTOUT-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for POL-OPTOUT-01"
def test_POL_BUDGET_01():
    reg = Register("data/constraints.yaml")
    rule = next((r for r in reg.rules if r.id == "POL-BUDGET-01"), None)
    assert rule is not None, "Rule POL-BUDGET-01 not found"

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
    assert passed is True, f"Failed passing case for POL-BUDGET-01: {reason}"

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
            "decline": {"mac": "03" if "POL-BUDGET-01" == "NET-MC-03" else "21" if "POL-BUDGET-01" == "NET-MC-04" else "02", "network_category": "1" if "POL-BUDGET-01" == "NET-VISA-01" else "3" if "POL-BUDGET-01" == "NET-VISA-03" else "00", "npci_code": "U16" if "POL-BUDGET-01" == "NPCI-MND-01" else "00", "visa_category": 1 if "POL-BUDGET-01" == "NET-VISA-01" else None if "POL-BUDGET-01" == "NET-VISA-03" else 0},
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
    assert passed is False, f"Failed failing case for POL-BUDGET-01"