# Samyak: The Recovery Control Plane

Every team in this track built something that reacts to a failed payment. We built a revenue recovery control plane for Indian payments that decides whether a recovery action is *legal*, *feasible on the rails*, and *worth more than it costs* — then proves it afterwards.

## Ground-Truth Regulatory Constraints

Samyak encodes India's complex payments and collections regulatory framework as hard constraints in a constraint satisfaction problem.

| Rule ID | Title | Source |
|---|---|---|
| [NPCI-ATT-01](#npci-att-01) | Max 4 attempts per mandate cycle | NPCI UPI Autopay retry rules |
| [NPCI-PDN-01](#npci-pdn-01) | Pre-debit notification required 24-48h before every debit | NPCI UPI Autopay operating guidelines; RBI E-Mandate Framework 2026 |
| [NPCI-PDN-02](#npci-pdn-02) | PDN requests at or after 23:50 rejected for T+1 debits | NPCI UPI Autopay PDN cutoff |
| [NPCI-PDN-03](#npci-pdn-03) | If PDN fails, the debit fails | NPCI operating guidelines |
| [NPCI-MND-01](#npci-mnd-01) | First-presentation failure auto-revokes the mandate | NPCI guidelines on mandate registration |
| [NPCI-PEAK-01](#npci-peak-01) | Automated debits during ~10:00-13:00 face elevated tech decline | NPCI peak-load restrictions |
| [NPCI-MIT-01](#npci-mit-01) | MIT autopay permitted up to Rs 50,000; above requires CIT | NPCI UPI Autopay MIT threshold |
| [RBI-EM-01](#rbi-em-01) | Recurring debits up to Rs 15,000 without per-cycle AFA | RBI Digital Payments E-Mandate Framework, 2026 |
| [RBI-EM-02](#rbi-em-02) | Rs 1 lakh no-AFA ceiling for insurance, mutual funds, cc bills | RBI Digital Payments E-Mandate Framework, 2026 |
| [RBI-EM-03](#rbi-em-03) | Mandatory post-debit confirmation after every successful collection | RBI Digital Payments E-Mandate Framework, 2026 |
| [RBI-EM-04](#rbi-em-04) | Customer may opt out of an individual debit or withdraw mandate | RBI Digital Payments E-Mandate Framework, 2026 |
| [RBI-FPC-01](#rbi-fpc-01) | Recovery contact permitted only 08:00-19:00 | RBI Fair Practices Code |
| [RBI-FPC-02](#rbi-fpc-02) | No third-party contact (family, employer, neighbours) | RBI Fair Practices Code |
| [RBI-FPC-03](#rbi-fpc-03) | Calamitous-timing suppression | RBI expectation of empathy |
| [RBI-FPC-04](#rbi-fpc-04) | Liability rests with RE regardless of agent or bot | RBI instructions on outsourcing |
| [NET-VISA-01](#net-visa-01) | Visa Category 1 (never retry) — fee triggers on first reattempt | Visa Excessive Reattempts Rule |
| [NET-VISA-02](#net-visa-02) | Cap 15 reattempts per 30 days for Visa Category 2 and 3 | Visa Excessive Reattempts Rule |
| [NET-VISA-03](#net-visa-03) | No decline category code present — default to not retrying | Visa default position |
| [NET-MC-01](#net-mc-01) | MAC 01 — route to payment-update flow, do not retry | Mastercard Merchant Advice Codes |
| [NET-MC-02](#net-mc-02) | MAC 02 — retry permitted, max 1/day, max 10 per 30 days | Mastercard Excessive Attempts |
| [NET-MC-03](#net-mc-03) | MAC 03 — do not retry; penalty from the first attempt | Mastercard Excessive Attempts |
| [NET-MC-04](#net-mc-04) | MAC 21 — cardholder cancelled; terminal | Mastercard Merchant Advice Codes |
| [NET-SOFT-01](#net-soft-01) | Soft declines — no sooner than 24h after decline, max 1/day | Visa/Mastercard soft decline guidance |
| [TRAI-TIME-01](#trai-time-01) | Promotional communication permitted only 09:00-21:00 | TCCCPR 2018 |
| [TRAI-DLT-01](#trai-dlt-01) | Content must match a registered template exactly | TCCCPR 2018 |
| [TRAI-DLT-02](#trai-dlt-02) | All URLs pre-whitelisted, all variables pre-tagged | TRAI CTA whitelisting |
| [TRAI-DLT-03](#trai-dlt-03) | Header category suffix -P/-S/-T/-G assigned by carrier | TRAI header suffix rule |
| [TRAI-DND-01](#trai-dnd-01) | DND / NCPR scrubbing for promotional traffic | TCCCPR 2018 |
| [DPDP-01](#dpdp-01) | Consent basis documented and current per data principal | Digital Personal Data Protection Act, 2023 |
| [DPDP-02](#dpdp-02) | Data minimisation; PII redaction before third-party model calls | DPDP Act 2023 |
| [AI-DISC-01](#ai-disc-01) | AI self-identification at the start of automated voice contact | RBI conduct rules |
| [MSME-43BH-01](#msme-43bh-01)| Payment to Udyam-registered enterprise within 45 days | Section 43B(h), Income Tax Act |
| [MSME-16-01](#msme-16-01) | Compound interest at 3x RBI bank rate on delayed payment | MSMED Act 2006 |
| [MSME-TDS-01](#msme-tds-01) | Buyer-side TDS withholding produces systematic short-payment | Income Tax Act TDS provisions |
| [POL-FATIGUE-01](#pol-fatigue-01)| Max 3 contacts per subject per rolling 7 days | Internal policy |
| [POL-OPTOUT-01](#pol-optout-01)| Opt-out is permanent and terminal | Internal policy |
| [POL-BUDGET-01](#pol-budget-01)| Action cost per case must not exceed 8% of recoverable amount | Internal policy |

---

## Three Key Innovations

1. **Deterministic Constraint Solving (CP-SAT):**
   Instead of hardcoding brittle `if/else` logic, Samyak schedules a 14-day recovery plan using an OR-Tools CP-SAT solver. The constraints naturally interact—for example, a PDN lead time couples to the debit slot, which couples to the peak-window penalty. A rules chain gives an answer, but our solver provides a mathematically optimal, compliant proof of schedule.

2. **T-48 Preemption Engine:**
   We flip the problem: acting 72h before a failure occurs. By monitoring NPCI peak loads, issuer health models, and calendar limits, the system schedules debits preemptively out of technical decline windows, avoiding penalties before they hit.

3. **Cryptographically Chained Audit Ledger:**
   Every blocked action is recorded with the exact rule ID that blocked it. A ledger logs `hash = sha256(prev_hash || canonical_json(record))`. The system supports 100% replay determinism to prove exactly why we chose to pursue, or suppress, a recovery.

---

## Honest Measurement Framework

In Samyak's outcome reports, **our monetary uplift (gross recovery and net yield) is strictly simulated**, mathematically modelled based on randomized issuer technical decline profiles and payment baseline probabilities. To reflect reality, we report this as an uplift *band* across a parameter sweep rather than a single point estimate.

However, **our zero compliance violations and zero network penalties are not simulated**. The violation count stays pinned at 0 because it is a deterministic property of the system's hardcoded constraint logic. This is the core thesis of our measurement: the honesty of our measurement is a feature.

---

## Red-Team Compliance Matrix

Samyak guarantees regulatory compliance through an adversarial test suite proving its handling of Indian payment landmines. 

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

---

## Architecture

* **Event Bus:** Simulates a Kafka (Redpanda) pipeline where events are published across 4 leak types.
* **Core Services:** Python architecture combining deterministic execution with LightGBM calibrated EV predictions.
* **Consistency Model:** Utilizes the outbox pattern and CDC design (mimicking Razorpay's monolith-to-microservices migration).
* **Storage Layer:** Uses JSON ledgers and YAML constraint registries representing PostgreSQL and Redis backends.
* **Solver:** OR-Tools CP-SAT solving.
* **Console:** React + Tailwind + Recharts frontend visualizing the deterministic outputs via a FastAPI layer.

---

## Reproducible Demo

The demo runs completely deterministically (seeded RNG), ensuring identical execution traces across every run.

```bash
make install
make test
python scripts/generate_redteam_report.py
make demo
```
*Note: `make demo` reproduces the Policy Comparison grid numbers byte-for-byte.*

---

## Roadmap

* **v1.1** Constrained contextual bandit over action arms, exploring only inside the feasible set the solver returns.
* **v1.2** Constraint register as a versioned, subscribable feed for auto-updating deployments when RBI issues circulars.
* **v1.3** Real DLT template registry integration with automated template-gap detection.
* **v1.4** TReDS hand-off for accepted receivables that fail recovery.
* **v2.0** Cross-merchant issuer-health federation to predict bank degradation.

---

<br />
<small>Built for the Razorpay Hackathon.</small>
