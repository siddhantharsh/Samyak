import json
import os
import tempfile
import filecmp
from sim.generate import generate_data

def test_generator_determinism():
    # Run twice and check identical files
    with tempfile.TemporaryDirectory() as td:
        orig_cwd = os.getcwd()
        os.chdir(td)
        try:
            generate_data(seed=42)
            os.rename("data/synthetic", "data/run1")
            
            generate_data(seed=42)
            os.rename("data/synthetic", "data/run2")
            
            assert filecmp.cmp("data/run1/subjects.json", "data/run2/subjects.json")
            assert filecmp.cmp("data/run1/events.json", "data/run2/events.json")
            assert filecmp.cmp("data/run1/landmine_index.json", "data/run2/landmine_index.json")
        finally:
            os.chdir(orig_cwd)

def test_generator_volumes_and_distribution():
    with open("data/synthetic/subjects.json", "r") as f:
        subjects = json.load(f)
    
    with open("data/synthetic/events.json", "r") as f:
        events = json.load(f)
        
    with open("data/synthetic/landmine_index.json", "r") as f:
        landmine_index = json.load(f)
        
    assert len(subjects) == 1200
    assert 3500 <= len(events) <= 3520 # 3514 due to landmines

    types_count = {}
    mac_count = {}
    for ev in events:
        ltype = ev["leak_type"]
        types_count[ltype] = types_count.get(ltype, 0) + 1
        
        if ltype == "MANDATE_FAIL":
            mac = ev["raw_codes"].get("mac")
            mac_count[mac] = mac_count.get(mac, 0) + 1

    # Base volumes (+ small additions from landmines)
    assert 1400 <= types_count["MANDATE_DEBIT_DUE"] <= 1410
    assert 900 <= types_count["MANDATE_FAIL"] <= 910
    assert 700 <= types_count["CHECKOUT_ABANDON"] <= 710
    assert 500 <= types_count["INVOICE_OVERDUE"] <= 510

    # MANDATE_FAIL distribution check (within 3% margin)
    mf_total = types_count["MANDATE_FAIL"]
    
    insufficient = mac_count.get("05", 0) / mf_total
    technical = mac_count.get("91", 0) / mf_total
    mandate = mac_count.get("14", 0) / mf_total
    expired = mac_count.get("54", 0) / mf_total
    cap_afa = mac_count.get("AFA", 0) / mf_total
    fraud = mac_count.get("59", 0) / mf_total

    assert abs(insufficient - 0.55) <= 0.03
    assert abs(technical - 0.15) <= 0.03
    assert abs(mandate - 0.10) <= 0.03
    assert abs(expired - 0.08) <= 0.03
    assert abs(cap_afa - 0.05) <= 0.03
    assert abs(fraud - 0.04) <= 0.03
    
def test_generator_landmines_exist():
    with open("data/synthetic/landmine_index.json", "r") as f:
        landmines = json.load(f)
        
    expected_landmines = {
        "duplicate_webhook",
        "payment_settles_before_dispatch",
        "opt_out_mid_sequence",
        "mandate_revoked_after_first_fail",
        "debit_in_peak_window",
        "pdn_at_2352",
        "afa_amount_raised",
        "mac_21_with_attempts",
        "tds_short_payment",
        "already_paid_hinglish",
        "reply_stop",
        "calamitous_timing",
        "udyam_41_days_old"
    }
    
    assert set(landmines.keys()) == expected_landmines
    assert len(landmines) == 13
