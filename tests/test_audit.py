import os
import tempfile
import json
import pytest
import datetime
from core.entities import DecisionRecord, Diagnosis, Layer, Arm, ActionPlan, PlannedAction
from core.audit.ledger import AuditLedger, canonical_json
from core.audit.replay import replay_all
from core.audit.killswitch import engage_killswitch, is_killswitch_engaged, get_killswitch_reason, reset_killswitch

def create_dummy_record(i: int, action_kind="mandate.represent", refusals=None) -> DecisionRecord:
    diag = Diagnosis(root_cause="INSUFFICIENT_FUNDS", layer=Layer.L1_DETERMINISTIC, confidence=1.0, permitted_action_classes=set(), evidence=[])
    
    if action_kind:
        action = ActionPlan(feasible=True, steps=[PlannedAction(kind=action_kind, scheduled_at=datetime.datetime.now(), channel="UPI", template_id=None, variables={}, precondition_step_ids=[])])
    else:
        action = None
        
    return DecisionRecord(
        seq=i,
        prev_hash="",
        hash="",
        event_id=f"case_{i}",
        diagnosis=diag,
        constraint_snapshot_digest=f"snap_{i%5}",
        considered_plans=[],
        chosen_plan=action,
        refusals=refusals or [],
        policy_version="1.0",
        model_versions={},
        prompt_hash=None,
        input_digest="input1",
        responsible_entity_id="system",
        timestamp=datetime.datetime.now(),
        arm=Arm.TREATMENT
    )

@pytest.fixture
def temp_ledger():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        filepath = f.name
    ledger = AuditLedger(filepath=filepath)
    yield ledger
    if os.path.exists(filepath):
        os.remove(filepath)

# 1-3. Canonical JSON Edge Cases
@pytest.mark.parametrize("input_data,expected_substr", [
    ({"b": 2, "a": 1}, '{"a":1,"b":2}'),
    ({"nested": {"z": 1.1234567, "y": 2}}, '{"nested":{"y":2,"z":1.123457}}'), # Tests float rounding and nesting
    ([1.0000001, {"x": 2}], '[1.0,{"x":2}]'),
])
def test_canonical_json_edge_cases(input_data, expected_substr):
    assert canonical_json(input_data) == expected_substr

# 4-8. Killswitch State Transitions
@pytest.mark.parametrize("initial_state,engage_msg,expected_bool,expected_reason", [
    (False, "Test reason 1", True, "Test reason 1"),
    (False, "Another reason", True, "Another reason"),
    (True, "Override reason", True, "Override reason"),
    (False, "", True, ""),
    (True, None, True, None),
])
def test_killswitch_state_transitions(initial_state, engage_msg, expected_bool, expected_reason):
    reset_killswitch()
    if initial_state:
        engage_killswitch("Initial")
    engage_killswitch(engage_msg)
    assert is_killswitch_engaged() == expected_bool
    assert get_killswitch_reason() == (expected_reason or "")

# 9-10. Ledger Genesis Behavior
def test_ledger_genesis_behavior(temp_ledger):
    records = temp_ledger.get_all()
    assert len(records) == 1
    assert records[0]["is_genesis"] is True
    assert records[0]["hash"] == "0" * 64

def test_ledger_genesis_reopen(temp_ledger):
    # Test that reopening the ledger doesn't create another genesis
    ledger2 = AuditLedger(filepath=temp_ledger.filepath)
    assert len(ledger2.get_all()) == 1

# 11-15. Ledger Append and Retrieve
@pytest.mark.parametrize("num_records", [1, 2, 5, 10, 50])
def test_ledger_append_and_retrieve(temp_ledger, num_records):
    for i in range(num_records):
        temp_ledger.append(create_dummy_record(i))
    
    records = temp_ledger.get_all()
    assert len(records) == num_records + 1 # +1 for genesis
    for i in range(1, num_records + 1):
        assert records[i]["seq"] == i
        assert "hash" in records[i]
        assert "prev_hash" in records[i]

# 16-25. Ledger Verify Chain Valid
@pytest.mark.parametrize("num_records", [0, 1, 2, 3, 5, 8, 13, 21, 34, 55])
def test_ledger_verify_chain_valid(temp_ledger, num_records):
    for i in range(num_records):
        temp_ledger.append(create_dummy_record(i))
    assert temp_ledger.verify_chain() is True

# 26-35. Ledger Tamper Detection Mutations
@pytest.mark.parametrize("target_record_idx,field_to_tamper,tampered_val", [
    (1, "seq", 999),
    (1, "event_id", "hacked_event"),
    (2, "prev_hash", "deadbeef"),
    (2, "timestamp", "2099-01-01T00:00:00Z"),
    (1, "chosen_plan", {"feasible": False, "steps": [], "binding_constraints": []}),
    (3, "refusals", [["hacked_action", "hacked_rule", "reason"]]),
    (1, "input_digest", "tampered_digest"),
    (3, "responsible_entity_id", "hacker"),
    (2, "policy_version", "2.0-malicious"),
    (1, "arm", "HOLDOUT"),
])
def test_ledger_tamper_detection_mutations(temp_ledger, target_record_idx, field_to_tamper, tampered_val):
    # Setup 4 records
    for i in range(4):
        temp_ledger.append(create_dummy_record(i))
        
    assert temp_ledger.verify_chain() is True
    
    # Mutate directly in file
    with open(temp_ledger.filepath, 'r') as f:
        lines = f.readlines()
        
    data = json.loads(lines[target_record_idx])
    data[field_to_tamper] = tampered_val
    lines[target_record_idx] = json.dumps(data) + "\n"
    
    with open(temp_ledger.filepath, 'w') as f:
        f.writelines(lines)
        
    assert temp_ledger.verify_chain() is False

# 36-50. Replay Determinism Reports
def mock_deterministic_decision_engine(rec_dict: dict) -> DecisionRecord:
    # A perfectly deterministic engine that just replicates the original action/refusal exactly as it was.
    diag = Diagnosis(root_cause="INSUFFICIENT_FUNDS", layer=Layer.L1_DETERMINISTIC, confidence=1.0, permitted_action_classes=set(), evidence=[])
    
    old_action = rec_dict.get("chosen_plan")
    if old_action:
        action = ActionPlan(feasible=True, steps=[PlannedAction(kind=old_action["steps"][0]["kind"], scheduled_at=datetime.datetime.now(), channel="UPI", template_id=None, variables={}, precondition_step_ids=[])])
        refusals = []
    else:
        action = None
        refusals = [(r[0], r[1], r[2]) for r in rec_dict.get("refusals", [])]
        
    return DecisionRecord(
        seq=rec_dict["seq"],
        prev_hash=rec_dict["prev_hash"],
        hash=rec_dict["hash"],
        event_id=rec_dict["event_id"],
        diagnosis=diag,
        constraint_snapshot_digest=rec_dict["constraint_snapshot_digest"],
        considered_plans=[],
        chosen_plan=action,
        refusals=refusals,
        policy_version="1.0",
        model_versions={},
        prompt_hash=None,
        input_digest="input1",
        responsible_entity_id="system",
        timestamp=datetime.datetime.now(),
        arm=Arm.TREATMENT
    )

def mock_flaky_decision_engine(rec_dict: dict) -> DecisionRecord:
    # Changes action on odd sequences to cause mismatches
    seq = rec_dict.get("seq", 0)
    rec = mock_deterministic_decision_engine(rec_dict)
    if seq % 2 != 0:
        if rec.chosen_plan:
            rec.chosen_plan.steps[0].kind = "DIFFERENT_ACTION"
        else:
            rec.refusals.append(("NEW", "DIFFERENT_RULE", "NEW_REASON"))
    return rec

@pytest.mark.parametrize("num_records,engine_type", [
    (10, "deterministic"),
    (20, "deterministic"),
    (50, "deterministic"),
    (100, "deterministic"),
    (200, "deterministic"),
    (10, "flaky"),
    (20, "flaky"),
    (50, "flaky"),
    (1, "deterministic"),
    (1, "flaky"),
    (2, "flaky"),
    (3, "flaky"),
    (0, "deterministic"),
    (0, "flaky"),
    (15, "deterministic")
])
def test_replay_determinism_reports(temp_ledger, num_records, engine_type):
    # Setup records
    for i in range(num_records):
        temp_ledger.append(create_dummy_record(i, action_kind="mandate.represent" if i%3==0 else None, refusals=[] if i%3==0 else [("DO_NOTHING", "RULE", "Y")]))
        
    engine = mock_deterministic_decision_engine if engine_type == "deterministic" else mock_flaky_decision_engine
    
    report = replay_all(temp_ledger, engine)
    
    assert report.total_cases == num_records
    if num_records > 0:
        if engine_type == "deterministic":
            assert report.matches == num_records
            assert report.determinism_percentage == 100.0
        else:
            expected_matches = sum(1 for i in range(1, num_records + 1) if i % 2 == 0)
            assert report.matches == expected_matches
            assert abs(report.determinism_percentage - (expected_matches / num_records * 100.0)) < 0.01
