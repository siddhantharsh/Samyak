import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from core.rng import seeded_rng
from core.entities import (
    LeakType, Rail, Subject, LeakEvent, RawCodes, Context
)

# Constants
SUBJECT_COUNT = 1200
EVENTS_DUE = 1400
EVENTS_FAIL = 900
EVENTS_ABANDON = 700
EVENTS_INVOICE = 500

LANGUAGES = ["en", "hi", "ta", "te", "mr", "bn", "kn"]
LANG_WEIGHTS = [30, 40, 10, 5, 5, 5, 5]

DND_STATUSES = ["UNREGISTERED", "PROMOTIONAL_BLOCKED", "ALL_BLOCKED"]
DND_WEIGHTS = [60, 30, 10]

def generate_data(seed: int = 42):
    rng = seeded_rng(seed)
    base_time = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    
    # 1. Generate Merchants (6 archetypes)
    merchants = [
        {"id": "merch_d2c", "type": "D2C_SUBSCRIPTION", "avg_ticket": 1200},
        {"id": "merch_ott", "type": "OTT", "avg_ticket": 399},
        {"id": "merch_edtech", "type": "EDTECH", "avg_ticket": 8000},
        {"id": "merch_saas", "type": "SAAS", "avg_ticket": 25000},
        {"id": "merch_nbfc", "type": "NBFC_EMI", "avg_ticket": 12000},
        {"id": "merch_b2b", "type": "B2B_MFG", "avg_ticket": 150000},
    ]

    # 2. Generate Issuers (14 banks)
    issuers = [{"id": f"bank_{i:02d}", "td_rate": rng.uniform(0.01, 0.05)} for i in range(1, 15)]

    # 3. Generate Subjects (1200)
    subjects = []
    for i in range(SUBJECT_COUNT):
        is_udyam = rng.random() < 0.1
        lang = rng.choices(LANGUAGES, weights=LANG_WEIGHTS)[0]
        dnd = rng.choices(DND_STATUSES, weights=DND_WEIGHTS)[0]
        
        # Landmine 12: calamitous_timing
        suppression_flags = []
        if i == 42:
            suppression_flags = ["CALAMITOUS_TIMING"]
            
        subject = Subject(
            id=f"sub_{i:04d}",
            contact_channels=["SMS", "WHATSAPP", "EMAIL"],
            language_pref=lang,
            consent_state={"communication_consent": True},
            dnd_status=dnd,
            suppression_flags=suppression_flags,
            is_udyam_supplier_relationship=is_udyam,
            contact_history=[],
            timezone="Asia/Kolkata"
        )
        subjects.append(subject)

    # 4. Generate Events
    events = []
    landmine_index = {}
    
    def emit_event(ev: LeakEvent, landmine_id: str = None):
        ev_dict = ev.model_dump()
        ev_dict["due_at"] = ev_dict["due_at"].isoformat()
        ev_dict["occurred_at"] = ev_dict["occurred_at"].isoformat()
        if landmine_id:
            ev_dict["landmine_id"] = landmine_id
            landmine_index.setdefault(landmine_id, []).append(ev.id)
        events.append(ev_dict)

    ev_id_counter = 1
    def next_ev_id():
        nonlocal ev_id_counter
        val = f"evt_{ev_id_counter:05d}"
        ev_id_counter += 1
        return val

    # Generate MANDATE_DEBIT_DUE (1400)
    for _ in range(EVENTS_DUE):
        sub = rng.choice(subjects)
        merch = rng.choice(merchants)
        ev_id = next_ev_id()
        
        amount = merch["avg_ticket"] * rng.uniform(0.8, 1.2)
        occurred_at = base_time - timedelta(hours=rng.randint(1, 100))
        due_at = occurred_at + timedelta(hours=72)
        
        ev = LeakEvent(
            id=ev_id,
            tenant_id="tenant_default",
            leak_type=LeakType.MANDATE_DEBIT_DUE,
            subject_ref=sub.id,
            amount=round(amount, 2),
            currency="INR",
            due_at=due_at,
            occurred_at=occurred_at,
            rail=Rail.UPI_AUTOPAY,
            raw_codes=RawCodes(),
            context=Context(mandate_id=f"mnd_{ev_id}", attempt_index=1, cycle_id=f"cycle_{ev_id}"),
            idempotency_key=f"idemp_{ev_id}"
        )
        emit_event(ev)

    # Pre-generate exact MAC distribution for MANDATE_FAIL
    mac_distribution = (
        ["05"] * int(EVENTS_FAIL * 0.55) +
        ["91"] * int(EVENTS_FAIL * 0.15) +
        ["14"] * int(EVENTS_FAIL * 0.10) +
        ["54"] * int(EVENTS_FAIL * 0.08) +
        ["AFA"] * int(EVENTS_FAIL * 0.05) +
        ["59"] * int(EVENTS_FAIL * 0.04) +
        ["OTHER"] * int(EVENTS_FAIL * 0.03)
    )
    # Pad if rounding left us short
    mac_distribution += ["05"] * (EVENTS_FAIL - len(mac_distribution))
    rng.shuffle(mac_distribution)

    # Generate MANDATE_FAIL (900)
    for i in range(EVENTS_FAIL):
        sub = rng.choice(subjects)
        ev_id = next_ev_id()
        mac = mac_distribution[i]
        
        ev = LeakEvent(
            id=ev_id,
            tenant_id="tenant_default",
            leak_type=LeakType.MANDATE_FAIL,
            subject_ref=sub.id,
            amount=1000.0,
            currency="INR",
            due_at=base_time,
            occurred_at=base_time,
            rail=Rail.CARD_MANDATE,
            raw_codes=RawCodes(mac=mac),
            context=Context(mandate_id=f"mnd_{ev_id}", attempt_index=1),
            idempotency_key=f"idemp_{ev_id}"
        )
        emit_event(ev)

    # Generate CHECKOUT_ABANDON (700)
    for _ in range(EVENTS_ABANDON):
        sub = rng.choice(subjects)
        ev_id = next_ev_id()
        ev = LeakEvent(
            id=ev_id,
            tenant_id="tenant_default",
            leak_type=LeakType.CHECKOUT_ABANDON,
            subject_ref=sub.id,
            amount=500.0,
            currency="INR",
            due_at=base_time,
            occurred_at=base_time,
            rail=Rail.UPI_COLLECT,
            raw_codes=RawCodes(network_category="TIMEOUT"), # App switch timeout
            context=Context(cart_id=f"cart_{ev_id}"),
            idempotency_key=f"idemp_{ev_id}"
        )
        emit_event(ev)

    # Generate INVOICE_OVERDUE (500)
    for _ in range(EVENTS_INVOICE):
        sub = rng.choice(subjects)
        ev_id = next_ev_id()
        ev = LeakEvent(
            id=ev_id,
            tenant_id="tenant_default",
            leak_type=LeakType.INVOICE_OVERDUE,
            subject_ref=sub.id,
            amount=10000.0,
            currency="INR",
            due_at=base_time - timedelta(days=10),
            occurred_at=base_time,
            rail=Rail.NEFT_RTGS,
            raw_codes=RawCodes(),
            context=Context(invoice_id=f"inv_{ev_id}"),
            idempotency_key=f"idemp_{ev_id}"
        )
        emit_event(ev)

    # Now inject exactly 13 landmines (replacing some existing events or just adding them)
    # 1. duplicate_webhook
    ev_dup1 = events[0].copy()
    ev_dup1["id"] = next_ev_id()
    ev_dup1["landmine_id"] = "duplicate_webhook"
    
    ev_dup2 = ev_dup1.copy()
    ev_dup2["id"] = next_ev_id()
    # Identical idempotency_key creates the duplicate condition
    
    events.append(ev_dup1)
    events.append(ev_dup2)
    landmine_index.setdefault("duplicate_webhook", []).extend([ev_dup1["id"], ev_dup2["id"]])

    def add_landmine(leak_type, landmine_id, amount=1000.0, due_at=None, raw_codes=None, context=None, rail=Rail.UPI_AUTOPAY, subject_ref=None):
        sub_id = subject_ref or rng.choice(subjects).id
        ev_id = next_ev_id()
        ev = LeakEvent(
            id=ev_id,
            tenant_id="tenant_default",
            leak_type=leak_type,
            subject_ref=sub_id,
            amount=amount,
            currency="INR",
            due_at=due_at or base_time,
            occurred_at=base_time,
            rail=rail,
            raw_codes=RawCodes(**(raw_codes or {})),
            context=Context(**(context or {})),
            idempotency_key=f"idemp_{ev_id}"
        )
        emit_event(ev, landmine_id)

    # 2. payment_settles_before_dispatch
    add_landmine(LeakType.MANDATE_FAIL, "payment_settles_before_dispatch")
    
    # 3. opt_out_mid_sequence
    add_landmine(LeakType.CHECKOUT_ABANDON, "opt_out_mid_sequence")
    
    # 4. mandate_revoked_after_first_fail
    add_landmine(LeakType.MANDATE_FAIL, "mandate_revoked_after_first_fail", raw_codes={"npci_code": "REVOKED"}, context={"attempt_index": 1})
    
    # 5. debit_in_peak_window
    peak_time = base_time.replace(hour=11, minute=30)
    add_landmine(LeakType.MANDATE_DEBIT_DUE, "debit_in_peak_window", due_at=peak_time)
    
    # 6. pdn_at_2352
    add_landmine(LeakType.MANDATE_DEBIT_DUE, "pdn_at_2352")
    
    # 7. afa_amount_raised
    add_landmine(LeakType.MANDATE_DEBIT_DUE, "afa_amount_raised", amount=16000.0)
    
    # 8. mac_21_with_attempts
    add_landmine(LeakType.MANDATE_FAIL, "mac_21_with_attempts", rail=Rail.CARD_MANDATE, raw_codes={"mac": "21"}, context={"attempt_index": 1}) # 9 remaining? (15 max, if we are at attempt 1, there are plenty remaining)
    
    # 9. tds_short_payment
    add_landmine(LeakType.INVOICE_OVERDUE, "tds_short_payment", amount=100000.0) # We will detect the short payment logically later, but the event is flagged here.
    
    # 10. already_paid_hinglish
    add_landmine(LeakType.INVOICE_OVERDUE, "already_paid_hinglish")
    
    # 11. reply_stop
    add_landmine(LeakType.MANDATE_FAIL, "reply_stop")
    
    # 12. calamitous_timing
    # Find the subject with calamitous_timing
    calamitous_sub = next(s for s in subjects if "CALAMITOUS_TIMING" in s.suppression_flags)
    add_landmine(LeakType.MANDATE_FAIL, "calamitous_timing", subject_ref=calamitous_sub.id)
    
    # 13. udyam_41_days_old
    udyam_sub = next(s for s in subjects if s.is_udyam_supplier_relationship)
    due_41_days_ago = base_time - timedelta(days=41)
    add_landmine(LeakType.INVOICE_OVERDUE, "udyam_41_days_old", subject_ref=udyam_sub.id, due_at=due_41_days_ago)

    # Write out data
    os.makedirs("data/synthetic", exist_ok=True)
    with open("data/synthetic/subjects.json", "w") as f:
        json.dump([s.model_dump() for s in subjects], f, indent=2)
        
    with open("data/synthetic/events.json", "w") as f:
        json.dump(events, f, indent=2)
        
    with open("data/synthetic/landmine_index.json", "w") as f:
        json.dump(landmine_index, f, indent=2)
        
    print(f"Generated {len(subjects)} subjects and {len(events)} events (including 13 landmines).")

if __name__ == "__main__":
    generate_data()
