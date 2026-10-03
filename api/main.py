from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import random

app = FastAPI(title="Samyak Console API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/funnel")
def get_funnel():
    # Return aggregate money funnel metrics
    return {
        "treatment": {
            "at_risk": 1500000,
            "suppressed": 250000, # Wrongful chases / already paid blocked
            "feasible": 1250000,
            "acted": 950000,
            "recovered": 605500
        },
        "holdout": {
            "at_risk": 1500000,
            "suppressed": 0, # Naive chases everyone
            "feasible": 1500000,
            "acted": 1500000,
            "recovered": 561700
        }
    }

@app.get("/api/cases")
def list_cases():
    return [
        {"id": "CASE-7012", "event": "MANDATE_DEBIT_DUE", "status": "FEASIBLE", "amount": 12000},
        {"id": "CASE-7013", "event": "MANDATE_FAILURE", "status": "REFUSED", "amount": 450},
        {"id": "CASE-7014", "event": "INVOICE_OVERDUE", "status": "FEASIBLE", "amount": 55000}
    ]

@app.get("/api/cases/{case_id}")
def get_case(case_id: str):
    # This is the money shot for Screen 3
    # Return a rich decision record
    return {
        "id": case_id,
        "raw_event": {
            "event_type": "MANDATE_FAILURE",
            "subject_id": "SUBJ-9921",
            "amount": 450,
            "decline_code": "MAC-21",
            "issuer": "HDFC",
            "timestamp": "2026-10-03T09:12:44Z"
        },
        "diagnosis": {
            "root_cause": "CARDHOLDER_CANCELLED",
            "level": "L1", # L1 deterministic
            "confidence": 1.0,
            "description": "Deterministic table lookup on MAC-21"
        },
        "constraints": [
            {"id": "NPCI-ATT-01", "desc": "Max 3 attempts per cycle", "pass": True},
            {"id": "RBI-EM-03", "desc": "Post-debit confirmation sent", "pass": True},
            {"id": "MAC-21-BLOCK", "desc": "Terminal decline logic", "pass": False, "citation": "Network rules 4.1.2"}
        ],
        "plans_considered": [
            {"id": "P-1", "action": "RETRY_T+1", "ev": -15.0, "feasible": False},
            {"id": "P-2", "action": "DO_NOTHING", "ev": 0.0, "feasible": True}
        ],
        "chosen_plan": {
            "id": "P-2",
            "action": "DO_NOTHING",
            "timeline": ["2026-10-03T09:12:45Z - Decision made", "2026-10-03T09:12:45Z - Case closed, added to ledger"]
        },
        "dispatch": {
            "template_id": "N/A",
            "scrub_verdict": "BLOCKED" # Refusal prominent
        }
    }

@app.get("/api/sweep")
def get_sweep():
    # Try to load real sweep if exists, else return mock
    sweep_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'out', 'sweep.json')
    if os.path.exists(sweep_path):
        with open(sweep_path, 'r') as f:
            return json.load(f)
            
    # Mock fallback
    return [
        {
            "multipliers": {"INSUFFICIENT_FUNDS": 1.0, "TECHNICAL_DECLINE": 1.0, "INVOICE_OVERDUE": 1.0},
            "holdout_recovered": 100,
            "samyak_recovered": 130,
            "uplift": 0.30
        }
    ]
