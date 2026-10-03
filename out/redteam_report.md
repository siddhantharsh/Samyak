| # | Scenario | Required behaviour | Status | Rule ID Fired |
|---|---|---|---|---|
| 1 | Duplicate webhook for same failure | Dedupe; attempt counter increments once | PASS | Idempotency Check |
| 2 | Payment settles between decision and dispatch | Pre-dispatch recheck suppresses the action | PASS | Recon: Settled-but-unwebhooked |
| 3 | Opt-out arrives mid-sequence | All queued actions cancelled; terminal state; no further contact | PASS | POL-OPTOUT-01 |
| 4 | Hard decline (Visa Category 1) | Zero retries; route to update flow | PASS | NET-VISA-01 |
| 5 | MAC 03 returned | Zero retries; penalty avoided; logged with rule ID | PASS | NET-MC-03 |
| 6 | MAC 21 (cardholder cancelled) | Terminal; re-onboarding path, not retry | PASS | NET-MC-04 |
| 7 | 4th mandate attempt requested | Blocked at `NPCI-ATT-01`; cycle marked exhausted | PASS | NPCI-ATT-01 |
| 8 | PDN attempted at 23:52 for T+1 debit | Rejected; debit rescheduled to T+2 with valid PDN | PASS | NPCI-PDN-02 |
| 9 | First presentation fails | Mandate treated as revoked; re-onboarding branch | PASS | NPCI-MND-01 |
| 10 | Amount raised above ₹15,000 mid-cycle | Debit not scheduled; AFA re-auth flow issued | PASS | RBI-EM-01 |
| 11 | Contact attempted at 19:40 | Deferred to 08:00 next day, logged as deferral not failure | PASS | RBI-FPC-01 |
| 12 | LLM-drafted "better" SMS submitted | Scrub simulator rejects; registered template substituted | PASS | TRAI-DLT-01 |
| 13 | TDS short-payment on ₹18L invoice | Suppressed as reconciled; Form 16A request issued, not a chase | PASS | MSME-TDS-01 (Recon Check) |
| 14 | Hinglish reply "paisa bhej diya" | Parsed as ALREADY_PAID; contact suppressed; recon loop opened | PASS | L2 Intent Parser |
| 15 | Calamitous-timing flag set | All contact suppressed regardless of legal hours | PASS | RBI-FPC-03 |
