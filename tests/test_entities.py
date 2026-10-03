from datetime import datetime, timezone
from decimal import Decimal
import pytest
from pydantic import ValidationError
from core.entities import (
    LeakEvent,
    Subject,
    Diagnosis,
    ConstraintSnapshot,
    PlannedAction,
    ActionPlan,
    DecisionRecord,
    LeakType,
    Rail,
    RawCodes,
    Context,
    Layer,
    Arm,
)

def test_entities_instantiation():
    now = datetime.now(timezone.utc)
    
    subject = Subject(
        id="sub_123",
        contact_channels=["SMS_SEND"],
        language_pref="en",
        consent_state={},
        dnd_status="UNREGISTERED",
        suppression_flags=[],
        is_udyam_supplier_relationship=False,
        contact_history=[],
        timezone="Asia/Kolkata",
    )
    
    leak = LeakEvent(
        id="leak_123",
        tenant_id="tenant_1",
        leak_type=LeakType.PAYMENT_FAIL,
        subject_ref="sub_123",
        amount=100.0,
        currency="INR",
        due_at=now,
        occurred_at=now,
        rail=Rail.UPI_AUTOPAY,
        raw_codes=RawCodes(),
        context=Context(),
        idempotency_key="idemp_1",
    )
    
    diagnosis = Diagnosis(
        root_cause="INSUFFICIENT_FUNDS",
        layer=Layer.L1_DETERMINISTIC,
        confidence=1.0,
        permitted_action_classes={"RETRY"},
        evidence=["bank_code_51"],
    )
    
    snapshot = ConstraintSnapshot(
        register_version="v1",
        attempt_counters={"SMS_SEND": 1},
        consent_state={"communication_consent": True},
        window_state={},
        template_registry_version="v1",
        budget_remaining=50.0,
    )
    
    action = PlannedAction(
        kind="SMS_SEND",
        scheduled_at=now,
        channel="SMS",
        template_id="tpl_123",
        variables={"name": "test"},
        precondition_step_ids=[],
    )
    
    plan = ActionPlan(
        steps=[action],
        feasible=True,
        binding_constraints=["TIME_WINDOW"],
        ev_net=Decimal("10.5"),
        solver_stats={"time_ms": 15},
    )
    
    record = DecisionRecord(
        seq=1,
        prev_hash="0000",
        hash="1111",
        event_id="leak_123",
        diagnosis=diagnosis,
        constraint_snapshot_digest="digest_abc",
        considered_plans=[plan],
        chosen_plan=plan,
        refusals=[("SMS_SEND", "NET-VISA-01", "rule matched")],
        policy_version="1.0",
        model_versions={"L2": "v2"},
        prompt_hash=None,
        input_digest="digest_in",
        responsible_entity_id="entity_1",
        timestamp=now,
        arm=Arm.TREATMENT,
    )
    
    assert leak.id == "leak_123"
    assert subject.id == "sub_123"
    assert diagnosis.layer == Layer.L1_DETERMINISTIC
    assert snapshot.register_version == "v1"
    assert action.kind == "SMS_SEND"
    assert plan.steps[0].kind == "SMS_SEND"
    assert record.arm == Arm.TREATMENT


def test_entities_invalid_leak_type():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError) as exc:
        LeakEvent(
            id="leak_404",
            tenant_id="tenant_1",
            leak_type="INVALID_LEAK_TYPE", # Invalid enum value
            subject_ref="sub_123",
            amount=100.0,
            currency="INR",
            due_at=now,
            occurred_at=now,
            rail=Rail.UPI_AUTOPAY,
            raw_codes=RawCodes(),
            context=Context(),
            idempotency_key="idemp_1",
        )
    assert "Input should be 'PAYMENT_FAIL', 'CHECKOUT_ABANDON'" in str(exc.value)


def test_entities_missing_required_fields():
    with pytest.raises(ValidationError) as exc:
        Subject(
            id="sub_missing",
            # Omitting contact_channels and other required fields
        )
    err_str = str(exc.value)
    assert "contact_channels" in err_str
    assert "language_pref" in err_str
    assert "consent_state" in err_str


def test_entities_diagnosis_layer_enum():
    with pytest.raises(ValidationError) as exc:
        Diagnosis(
            root_cause="UNKNOWN",
            layer="L3_MAGIC", # Invalid layer
            confidence=0.5,
            permitted_action_classes=set(),
            evidence=[]
        )
    assert "Input should be 'L1_DETERMINISTIC', 'L2_INFERRED' or 'UNRESOLVED'" in str(exc.value)
