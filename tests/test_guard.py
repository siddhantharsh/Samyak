import pytest
from datetime import datetime
from core.entities import LeakEvent, LeakType, Rail, RawCodes, Context
from core.recon.guard import check_event, LedgerState

def create_event(
    id="evt_1",
    amount=100.0,
    subject_ref="sub_1",
    invoice_id=None,
    idempotency_key="idk_1"
):
    ctx = Context()
    if invoice_id:
        ctx.invoice_id = invoice_id

    return LeakEvent(
        id=id,
        tenant_id="t1",
        leak_type=LeakType.INVOICE_OVERDUE,
        subject_ref=subject_ref,
        amount=amount,
        currency="INR",
        due_at=datetime.utcnow(),
        occurred_at=datetime.utcnow(),
        rail=Rail.NEFT_RTGS,
        raw_codes=RawCodes(),
        context=ctx,
        idempotency_key=idempotency_key,
    )

def test_settled_but_unwebhooked():
    ev = create_event(amount=100.0, subject_ref="sub_1")
    state = LedgerState(
        seen_idempotency_keys=set(),
        settled_payments=[{"subject_ref": "sub_1", "amount": 100.0, "date": datetime.utcnow()}],
        received_amounts={},
        credit_notes={},
        subject_tds_section={}
    )
    res = check_event(ev, state)
    assert res.action == "SUPPRESSED_RECONCILED"
    assert res.check_name == "Settled-but-unwebhooked"

def test_duplicate_event():
    ev = create_event(idempotency_key="idk_dup")
    state = LedgerState(
        seen_idempotency_keys={"idk_dup"},
        settled_payments=[],
        received_amounts={},
        credit_notes={},
        subject_tds_section={}
    )
    res = check_event(ev, state)
    assert res.action == "DROP"
    assert res.check_name == "Duplicate event"

def test_partial_payment():
    ev = create_event(amount=1000.0, invoice_id="inv_1")
    state = LedgerState(
        seen_idempotency_keys=set(),
        settled_payments=[],
        received_amounts={"inv_1": 400.0},
        credit_notes={},
        subject_tds_section={"sub_1": "194C"} # 2% tds
    )
    res = check_event(ev, state)
    assert res.action == "RE_SCOPED"
    assert res.check_name == "Partial payment"
    assert res.residual_amount == 600.0

def test_tds_short_payment():
    ev = create_event(amount=100000.0, invoice_id="inv_2")
    # expected TDS at 2% for 194C is 2000
    # if received is 98000, remainder is exactly TDS
    state = LedgerState(
        seen_idempotency_keys=set(),
        settled_payments=[],
        received_amounts={"inv_2": 98000.0},
        credit_notes={},
        subject_tds_section={"sub_1": "194C"}
    )
    res = check_event(ev, state)
    assert res.action == "SUPPRESSED_RECONCILED"
    assert res.check_name == "TDS short-payment"

def test_credit_note_applied():
    ev = create_event(amount=500.0, invoice_id="inv_3")
    state = LedgerState(
        seen_idempotency_keys=set(),
        settled_payments=[],
        received_amounts={"inv_3": 0.0}, # No partial payment
        credit_notes={"inv_3": 500.0},
        subject_tds_section={}
    )
    res = check_event(ev, state)
    assert res.action == "SUPPRESSED_RECONCILED"
    assert res.check_name == "Credit note applied"

def test_landmines():
    import json
    import os
    
    if not os.path.exists("data/synthetic/events.json"):
        return
        
    with open("data/synthetic/events.json") as f:
        events_data = json.load(f)
    with open("data/synthetic/landmine_index.json") as f:
        lm_index = json.load(f)
        
    events = [LeakEvent(**d) for d in events_data]
    events_by_id = {e.id: e for e in events}
    
    # 1. Duplicate webhook
    dup_ids = lm_index.get("duplicate_webhook", [])
    if dup_ids and len(dup_ids) >= 2:
        ev1 = events_by_id[dup_ids[0]]
        ev2 = events_by_id[dup_ids[1]]
        
        state = LedgerState(
            seen_idempotency_keys=set(),
            settled_payments=[],
            received_amounts={},
            credit_notes={},
            subject_tds_section={}
        )
        # First process
        res1 = check_event(ev1, state)
        assert res1.action == "PASSED"
        state.seen_idempotency_keys.add(ev1.idempotency_key)
        
        # Second process (the duplicate)
        res2 = check_event(ev2, state)
        assert res2.action == "DROP"
        assert res2.check_name == "Duplicate event"

    # 2. TDS short payment
    tds_ids = lm_index.get("tds_short_payment", [])
    if tds_ids:
        ev_tds = events_by_id[tds_ids[0]]
        # Mock ledger state so this is a TDS short payment
        invoice_id = ev_tds.context.invoice_id
        if not invoice_id:
            invoice_id = "inv_tds_lm"
            ev_tds.context.invoice_id = invoice_id
        
        rate = 0.02 # 194C
        expected_tds = ev_tds.amount * rate
        received = ev_tds.amount - expected_tds
        
        state = LedgerState(
            seen_idempotency_keys=set(),
            settled_payments=[],
            received_amounts={invoice_id: received},
            credit_notes={},
            subject_tds_section={ev_tds.subject_ref: "194C"}
        )
        res_tds = check_event(ev_tds, state)
        assert res_tds.action == "SUPPRESSED_RECONCILED"
        assert res_tds.check_name == "TDS short-payment"
