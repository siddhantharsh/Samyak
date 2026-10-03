import json
import os
from datetime import datetime
from core.entities import LeakEvent
from core.recon.guard import check_event, LedgerState, load_tds_rates

def run():
    print("Loading corpus...")
    with open("data/synthetic/events.json") as f:
        events_data = json.load(f)
    with open("data/synthetic/landmine_index.json") as f:
        lm_index = json.load(f)

    events = [LeakEvent(**d) for d in events_data]
    events_by_id = {e.id: e for e in events}
    
    tds_rates = load_tds_rates()

    # Build a mock ledger state that activates the landmines and a random subset of events
    state = LedgerState(
        seen_idempotency_keys=set(),
        settled_payments=[],
        received_amounts={},
        credit_notes={},
        subject_tds_section={}
    )

    # 1. Payment settles before dispatch
    settle_ids = lm_index.get("payment_settles_before_dispatch", [])
    for ev_id in settle_ids:
        ev = events_by_id[ev_id]
        state.settled_payments.append({
            "subject_ref": ev.subject_ref,
            "amount": ev.amount,
            "date": datetime.utcnow()
        })

    # 2. TDS short payment
    tds_ids = lm_index.get("tds_short_payment", [])
    for ev_id in tds_ids:
        ev = events_by_id[ev_id]
        invoice_id = getattr(ev.context, "invoice_id", None)
        if not invoice_id:
            invoice_id = f"inv_{ev.id}"
            ev.context.invoice_id = invoice_id
        rate = tds_rates.get("194C", 0.02)
        expected_tds = ev.amount * rate
        state.received_amounts[invoice_id] = ev.amount - expected_tds
        state.subject_tds_section[ev.subject_ref] = "194C"

    # Also make every 100th invoice event a partial payment
    # and every 150th a credit note
    for i, ev in enumerate(events):
        if ev.leak_type == "INVOICE_OVERDUE" and getattr(ev.context, "invoice_id", None):
            inv_id = ev.context.invoice_id
            if i % 100 == 0:
                # Partial payment
                state.received_amounts[inv_id] = ev.amount * 0.5
            elif i % 150 == 0:
                # Credit note
                state.credit_notes[inv_id] = ev.amount
                state.received_amounts[inv_id] = 0.0

    print("Running guard...")
    suppressed_count = 0
    suppressed_value = 0.0
    rescoped_count = 0

    for ev in events:
        res = check_event(ev, state)
        
        # Keep track of idempotency to catch duplicates natively
        if res.action == "PASSED" or res.action == "RE_SCOPED":
            state.seen_idempotency_keys.add(ev.idempotency_key)
            
        if res.action in ("SUPPRESSED_RECONCILED", "DROP"):
            suppressed_count += 1
            suppressed_value += ev.amount
            # print(f"Suppressed: {ev.id} - {res.check_name} ({res.explanation})")
        elif res.action == "RE_SCOPED":
            rescoped_count += 1
            # Rescoping effectively suppresses the difference
            suppressed_value += (ev.amount - res.residual_amount)
            # print(f"Re-scoped: {ev.id} - new amount {res.residual_amount}")

    print("=" * 40)
    print(f"GUARD RESULTS")
    print(f"Total Events Processed : {len(events)}")
    print(f"Suppressed Events      : {suppressed_count}")
    print(f"Re-scoped Events       : {rescoped_count}")
    print(f"Total ₹ Value Saved    : ₹{suppressed_value:,.2f}")
    print("=" * 40)

if __name__ == "__main__":
    run()
