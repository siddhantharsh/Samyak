# SAMYAK — Product Requirements Document

**A pre-emptive, constraint-solved, proof-carrying revenue recovery control plane for India.**

Track: AI Revenue Recovery · Razorpay Hackathon
Version 1.0 · Status: Build-ready

---

## 0. The one-liner

> Most recovery systems ask *"what should we do?"*
> Samyak asks the three questions that actually determine whether money comes back:
> **What are we legally permitted to do? Will the rails even accept it right now? Is it worth more than it costs?**

*Samyak* (सम्यक्) means *right* or *proper* — as in *samyak-karmānta*, right action. The name is the thesis: in Indian payments, the right recovery action is a narrow intersection of legal, feasible, and profitable, and almost every system in production gets that intersection wrong.

**Elevator pitch (30 seconds):**
Indian revenue recovery is not an intelligence problem. It is a constraint problem. NPCI gives you four mandate attempts, not unlimited retries. RBI requires a pre-debit notification 24 hours ahead, which means your recovery decision is due *before* the payment fails. TRAI blocks any SMS that does not match a pre-registered template character-for-character, so an LLM cannot write the nudge. Visa fines you for retrying a hard decline even once. Samyak encodes all of it as machine-checkable constraints, uses an LLM only where the input is genuinely unstructured, solves for the best legal plan, executes it in a bounded sandbox, and emits a cryptographic proof for every action taken and every action refused.

---

## 1. The problem, with evidence

### 1.1 The scale

| Fact | Source |
|---|---|
| Merchant-side blended UPI success rates land at 92–96%; below 90% is a serious business problem | NPCI BD/TD statistics, Circular OC-149 |
| UPI Autopay failure rates run 8–15%, versus 2–3% for card mandates | Product analysis of UPI recurring flows |
| Businesses lose 62% of customers permanently after a single failed transaction | Razorpay multi-payment acceptance research |
| 216,221 delayed-payment applications involving ₹47,677 crore filed by micro and small enterprises on MSME Samadhaan through Dec 2024 | Ministry of MSME annual report 2024-25 |
| Nearly 60% of firms say failed payments are expensive to track and resolve | Razorpay PSR optimization research |
| Mobile cart abandonment in India projected at ~85% by 2026, driven by network latency in Tier 2/3 cities | Razorpay checkout research |

This is not a niche. It is one of the largest recurring value leaks in the Indian digital economy, and the losses are concentrated in businesses least equipped to engineer their way out.

### 1.2 The eight failure modes nobody builds for

These are the real ones. Each is verified, each has a rule or a published statistic behind it, and each is invisible to a naive "detect and nudge" agent.

**F1 — The retry budget is four, not infinite.**
From August 2025 NPCI allows a maximum of four attempts per UPI Autopay mandate cycle: one original execution plus three retries. After that the cycle is marked failed. A dunning system built on "retry every day for a week" burns the entire budget in 96 hours and then has nothing left.

**F2 — The recovery decision is due before the failure.**
The pre-debit notification must be sent 24 to 48 hours before the debit is initiated, and if the PDN fails the debit request fails too, since PDN is a prerequisite under NPCI operating guidelines. There is also a hard cutoff: PDN requests received at or after 23:50 for a next-day debit are rejected. **This inverts the entire problem.** The highest-leverage moment in recovery is not after the failure; it is 48 hours before, when you still get to choose the date, the amount and the rail.

**F3 — First-presentation failure can revoke the mandate entirely.**
Under NPCI guidelines, if the first presentation fails the registered mandate is automatically revoked. That is not a retry problem, it is a re-onboarding problem, and treating it as a retry wastes every subsequent action.

**F4 — Retrying at the wrong hour is a self-inflicted decline.**
NPCI peak hours (roughly 10:00–13:00) carry the highest transaction load, and new rules restrict automated payments during those windows; an EMI scheduled at 10:30 AM is now likely to hit a technical decline. Off-peak slots — before 10 AM, 1 PM to 5 PM, after 9:30 PM — succeed materially more often. Scheduling is a free recovery lever that costs nothing and is almost universally ignored.

**F5 — An LLM cannot legally write the recovery message.**
All commercial SMS in India requires three-layer DLT registration (entity, header, content template), and real-time template scrubbing at the network level blocks any message whose content does not match an approved template exactly. Since October 2024, every URL must be pre-whitelisted and every template variable pre-tagged. A generated "Hinglish personalised nudge" never reaches the handset. Every team in this track that demos LLM-written SMS is demoing something that cannot ship.

**F6 — Retrying a hard decline costs money immediately.**
Visa's Excessive Reattempts Rule charges per retry beyond the 15th attempt in 30 days, and retrying a Category 1 (never retry) decline triggers the fee immediately regardless of attempt count. Mastercard charges per retry after MAC 03 ("do not try again") from the first unauthorized attempt, and MAC 21 signals the cardholder cancelled the mandate, making further attempts both non-compliant and futile. Fees accrue whether or not the retry eventually succeeds — meaning naive systems pay penalties *on revenue they recover*.

**F7 — Chasing someone who already paid.**
Webhook loss, settlement lag, and reconciliation delay mean a meaningful share of "unpaid" records are paid. In B2B the Indian-specific version is worse: **TDS short-payment.** The buyer pays the invoice minus withholding tax, the AR ledger reads it as partially unpaid, and the system chases a customer who paid correctly. This is the most expensive failure in the whole category because it destroys the relationship *and* wastes the action budget.

**F8 — Contact rules are legal boundaries, not UX preferences.**
For any regulated-entity collections context, RBI directives permit contacting borrowers only between 8:00 AM and 7:00 PM; calls outside that window are treated as harassment, and the regulated entity carries liability even when an outsourced agent or bot made the call. RBI also expects lenders to respect *calamitous timing* — no contact during a family bereavement or medical emergency even inside legal hours. Layered on top: DPDP Act 2023 consent and data-residency obligations, DND/NCPR scrubbing, and clear AI self-identification as best practice on automated voice calls.

### 1.3 Why existing solutions do not cover this

- **Gateway-native smart retries** (including Razorpay's own) optimise retry timing well, but they operate on one rail and do not reason across checkout, subscription and receivables, and they do not carry a compliance proof per action.
- **Dunning SaaS** (Churnbuster, Gravy, Easy Subscription class products) is built on US/EU card assumptions. Nothing in that stack knows about PDN windows, NPCI attempt caps, DLT template scrubbing, or Section 43B(h).
- **AR/collections tools** chase invoices but do not know payments-rail state, and cannot tell a TDS short-payment from a default.
- **Generic LLM agents** produce text, which is the one thing Indian regulation will not let you freely produce.

**The gap Samyak fills:** nobody has built the *decision layer* that sits above all rails and below all channels, encodes Indian constraints as first-class objects, and can prove what it did and why.

---

## 2. Positioning and thesis

### 2.1 What Samyak is

A **recovery control plane**. It does not move money and it does not own the customer relationship. It ingests leak events from any source, decides the single best legal action, dispatches it through existing bounded executors, and produces an auditable record.

### 2.2 Three innovations, in priority order

**I1 — T-48 pre-emption: recovery starts before the failure.**
Because F2 forces a decision 24–48 hours ahead of every mandate debit, Samyak treats that window as the primary intervention surface. Before the debit, it predicts failure risk from mandate history, issuer health, amount-versus-cap headroom and calendar position, then chooses the debit date, the rail and the pre-notification content. A payment that never fails needs no recovery. **This reframe alone differentiates the submission**: everyone else in this track is building a system that reacts; Samyak is the only one that acts on the causal upstream.

**I2 — A feasibility solver, not a rules chain.**
Recovery in India is a constrained scheduling problem: pick a sequence of actions over the next N days subject to attempt caps, notification lead times, quiet hours, blackout windows, template availability, consent state and cost budget, maximising expected net recovery. Samyak models this as a CP-SAT problem (OR-Tools) and *proves* a plan feasible before executing any of it. When no legal plan exists it says so explicitly and routes to human escalation instead of thrashing.
Slogan for the demo: **the model proposes, the solver disposes.**

**I3 — Proof-carrying actions.**
Every dispatched action carries a signed certificate listing the rule IDs it satisfied, the constraint snapshot, the model and policy versions, the prompt hash and the input digest, chained by hash to the previous decision. A "Regulator Mode" view answers, for any contact ever made, the question *"why were you allowed to do this, at this time, to this person?"* in one click, and replays the decision deterministically from the log.

### 2.3 The measurement stance (read this before writing any metric)

Outcomes in a hackathon are simulated. Pretending otherwise destroys credibility. Samyak therefore reports **three tiers of metric**, ordered by how real they are:

- **Tier 1 — Real regardless of simulation (headline).**
  `compliance_violations = 0`. Avoidable-waste rate. Prohibited-action attempts blocked. Do-not-chase suppressions. These are properties of the decision logic, not of the outcome model, and they are true no matter what the world does.
- **Tier 2 — Structurally real.** Constraint satisfaction rate, plan feasibility rate, infeasible-case escalation rate, decision latency, replay determinism (100% of decisions reproduce bit-identically from the log).
- **Tier 3 — Simulated, reported honestly as a band.** Net recovery uplift versus holdout, presented as a **range across a sensitivity sweep** of the outcome model's parameters, with the parameters frozen before the policy engine was written and stated in the README.

The README line that wins this: *"Our uplift number is simulated and we show it as a band. Our violation number is not simulated and it is zero."*

---

## 3. Users

| Persona | Context | What they need from Samyak |
|---|---|---|
| **Rhea, Growth/Billing lead at a D2C subscription brand** | 40k subscribers on UPI Autopay, 11% monthly debit failure, no in-house payments engineer | Automatic pre-emption and legal retry sequencing without her writing rule code; a number she can take to her CFO |
| **Vikram, Finance controller at a ₹200 Cr manufacturing firm** | 900 open invoices, 60+ day DSO, chases by email and phone | Stop chasing paid invoices; separate TDS short-payments from real defaults; know which invoices cross the Section 43B(h) line and when |
| **Ananya, Risk & Compliance at a fintech/NBFC** | Carries liability for every automated contact made by any vendor | Evidence. Time-window enforcement, consent state, per-action proof, and a kill switch |
| **Karthik, Payments platform engineer (the Razorpay judge's proxy)** | Cares whether this is real | Correct decline-code semantics, correct NPCI/RBI constraint modelling, idempotency, replayability |

---

## 4. Scope

### 4.1 In scope (v1, hackathon deliverable)

1. Unified leak-event ingestion across four leak types with a shared state machine.
2. Reconciliation guard (do-not-chase, including TDS short-payment detection).
3. Two-layer diagnosis: deterministic code/MAC resolver plus LLM fallback for unlabelled or ambiguous cases.
4. T-48 pre-emption engine for mandate debits.
5. Constraint register with ~30 machine-checkable rules across NPCI, RBI, card networks, TRAI and internal policy.
6. CP-SAT feasibility solver producing an executable action plan.
7. Expected-value ranking with a live "do nothing" arm.
8. Bounded action executors: mandate re-present, template-selected SMS/WhatsApp, checkout recovery link, AR escalation ladder, human handoff.
9. Inbound intent parser: customer replies, remittance advice, promise-to-pay extraction.
10. Proof-carrying hash-chained audit ledger with deterministic replay and Regulator Mode.
11. Treatment/holdout assignment with sensitivity-swept uplift reporting.
12. Red-team suite of 14 adversarial scenarios with a pass table.
13. Operator console: funnel, case detail with decision trace, constraint inspector, audit view.

### 4.2 Explicitly out of scope

- Moving real money or touching real customer data. Everything runs on a synthetic corpus and simulated rails.
- Actual DLT registration, real SMS/WhatsApp dispatch, real voice calls. Executors are sandboxed and log intent plus the scrub verdict.
- Credit scoring, collections litigation, legal notices.
- Multi-tenant auth, billing, RBAC beyond a single demo operator.
- Being a payment gateway. Samyak sits above the gateway.

### 4.3 Non-goals (state these out loud; they are credibility)

- **We do not use an LLM to author outbound messages.** Regulation forbids it. We use it to *select and fill* registered templates.
- **We do not claim causal proof of revenue uplift.** We claim a bounded simulated estimate and a real compliance guarantee.
- **We do not replace Razorpay's smart retries.** We decide whether a retry is legal and worth it, then hand execution to the rail.

---

## 5. The Constraint Register (the moat)

Every rule below is implemented as a first-class object with an ID, a predicate, a severity, a source citation and a test case. This register *is* the product's defensibility. Put it in the README verbatim.

### 5.1 Rail constraints (NPCI / UPI Autopay)

| ID | Rule | Effect on planning |
|---|---|---|
| `NPCI-ATT-01` | Max 4 attempts per mandate cycle (1 execution + 3 retries), stricter from Aug 2025 | Hard cap in solver; attempts become a scarce resource to allocate |
| `NPCI-PDN-01` | PDN required 24–48h before every debit | Every debit action needs a paired notify action ≥24h earlier |
| `NPCI-PDN-02` | PDN requests at/after 23:50 rejected for T+1 debits | Blackout on late-night scheduling of next-day debits |
| `NPCI-PDN-03` | If PDN fails, the debit fails | Notify success is a precondition edge in the plan graph |
| `NPCI-MND-01` | First-presentation failure auto-revokes the mandate | Branch to re-onboarding, not retry |
| `NPCI-PEAK-01` | Automated debits during ~10:00–13:00 peak load face elevated technical decline | Soft constraint with heavy cost penalty; prefer off-peak slots |
| `NPCI-MIT-01` | MIT autopay permitted up to ₹50,000; above requires customer-initiated payment | Above threshold, "retry" is not an available action |
| `NPCI-FAST-01` | FASTag/NCMC auto-replenishment exempt from 24h PDN | Category-conditional relaxation |

### 5.2 Regulatory constraints (RBI)

| ID | Rule | Effect |
|---|---|---|
| `RBI-EM-01` | E-Mandate Framework 2026 (21 Apr 2026): recurring debits up to ₹15,000 without per-cycle AFA | Above threshold, plan must include re-auth, not retry |
| `RBI-EM-02` | ₹1 lakh no-AFA ceiling for insurance premium, mutual fund subscription, credit card bill only | Category-aware threshold lookup |
| `RBI-EM-03` | Mandatory post-debit confirmation after every successful collection | Auto-appended action, not optional |
| `RBI-EM-04` | Customer may opt out of an individual debit or withdraw the mandate at any time | Opt-out is a terminal state, checked immediately before every dispatch |
| `RBI-FPC-01` | Recovery contact permitted only 08:00–19:00 | Hard time window on all contact actions in regulated context |
| `RBI-FPC-02` | No third-party contact (family, employer, neighbours) | Contact graph restricted to debtor and guarantor |
| `RBI-FPC-03` | Calamitous-timing suppression — no contact during bereavement/medical emergency | Manual and signal-triggered suppression flag |
| `RBI-FPC-04` | Liability rests with the regulated entity regardless of agent or bot | Every action attributed to a responsible entity ID in the log |

### 5.3 Card network constraints

| ID | Rule | Effect |
|---|---|---|
| `NET-VISA-01` | Category 1 (never retry) → retry triggers fee immediately | Retry action removed from action set |
| `NET-VISA-02` | Cap 15 reattempts / 30 days for Category 2 & 3 | Rolling-window counter per card+merchant |
| `NET-VISA-03` | No decline category code present → default to not retrying | Conservative default on ambiguity |
| `NET-MC-01` | MAC 01 → route to payment-update flow, do not retry | Action rewrite, not suppression |
| `NET-MC-02` | MAC 02 → retry permitted, ≤1/day, ≤10 per 30 days | Spacing constraint |
| `NET-MC-03` | MAC 03 → do not retry; penalty from the first attempt | Hard block |
| `NET-MC-04` | MAC 21 → mandate cancelled by cardholder; further attempts non-compliant and futile | Terminal state |
| `NET-SOFT-01` | Soft declines: no sooner than 24h after decline, ≤1/day | Minimum inter-attempt gap |

### 5.4 Communication constraints (TRAI / DPDP)

| ID | Rule | Effect |
|---|---|---|
| `TRAI-DLT-01` | Content must match a registered template exactly; network scrubbing blocks mismatches | LLM selects template ID and fills tagged variables only; a scrub simulator validates before dispatch |
| `TRAI-DLT-02` | All URLs pre-whitelisted, all variables pre-tagged (since Oct 2024) | Link registry; unregistered URL = blocked action |
| `TRAI-DLT-03` | Header category suffix -P/-S/-T/-G assigned by carrier | Message category determines which templates are reachable |
| `TRAI-DND-01` | DND/NCPR scrubbing for promotional traffic | Consent-class check before channel selection |
| `DPDP-01` | Consent basis documented and current per data principal | Consent ledger lookup is a precondition |
| `DPDP-02` | Data minimisation; PII redaction before third-party model calls | PII vault + tokenisation at the LLM boundary |
| `DPDP-03` | Data residency in India | Deployment constraint, documented |
| `AI-DISC-01` | Clear AI self-identification at the start of automated voice contact | Prepended to any voice script |

### 5.5 Receivables constraints (MSMED / Income Tax)

| ID | Rule | Effect |
|---|---|---|
| `MSME-43BH-01` | Payment to a Udyam-registered micro/small enterprise must occur within 45 days (15 without written agreement) or the buyer loses the income-tax deduction for that year | Creates a **factual, non-coercive escalation lever with a hard date** |
| `MSME-16-01` | MSMED Sec 16: compound interest at 3× RBI bank rate on delayed payment; Sec 23 makes that interest non-deductible | Quantifiable cost-of-delay figure to state in the reminder |
| `MSME-TDS-01` | Buyer-side TDS withholding produces systematic short-payment against invoice value | Reconciliation rule: `invoice − expected_TDS ≈ received` ⇒ NOT a default |

**Why `MSME-43BH-01` is the hidden gem of this track:** it turns a receivables chaser from a pest into a *service*. A reminder that says "this invoice crosses the Section 43B(h) 45-day line on 14 October, after which your firm loses the deduction on ₹X and accrues non-deductible interest at ~3× the RBI bank rate" is not a nag. It is information the buyer's own finance team urgently wants, it is factually true, it is entirely non-coercive, and it is materially more effective than any tone of voice an LLM could generate. No other submission will have this.

---

## 6. Architecture

### 6.1 Component map

```
                        ┌─────────────────────────────┐
  payment / checkout ──▶│  Ingestion & Normalisation  │
  subscription / AR     │  → canonical LeakEvent      │
  webhooks              └──────────────┬──────────────┘
                                       ▼
                        ┌─────────────────────────────┐
                        │  Reconciliation Guard       │  ← ledger, TDS rule
                        │  "are they actually owing?" │
                        └──────────────┬──────────────┘
                          suppress ◀───┤
                                       ▼
                        ┌─────────────────────────────┐
                        │  Diagnosis Resolver         │
                        │  L1 deterministic (code/MAC)│
                        │  L2 LLM fallback + confidence│
                        └──────────────┬──────────────┘
                                       ▼
                        ┌─────────────────────────────┐
                        │  T-48 Pre-emption Engine    │  ← issuer health, calendar
                        │  (mandate cycles only)      │
                        └──────────────┬──────────────┘
                                       ▼
      Constraint    ──▶  ┌─────────────────────────────┐
      Register           │  Plan Solver (CP-SAT)       │
      Consent Ledger ──▶ │  feasible action sequences  │
      Attempt Counters ─▶│  over next N days           │
                        └──────────────┬──────────────┘
                          infeasible ◀─┤ → human escalation w/ reason
                                       ▼
                        ┌─────────────────────────────┐
                        │  EV Ranker (incl. do-nothing)│
                        └──────────────┬──────────────┘
                                       ▼
                        ┌─────────────────────────────┐
                        │  Bounded Executors          │
                        │  represent · template-msg   │
                        │  · link · escalate · handoff│
                        └──────────────┬──────────────┘
                                       ▼
                        ┌─────────────────────────────┐
                        │  Proof-Carrying Audit Ledger│ ← hash chain, replay
                        └──────────────┬──────────────┘
                                       ▼
                        ┌─────────────────────────────┐
                        │  Outcome Sim + Measurement  │
                        │  treatment / holdout / sweep│
                        └─────────────────────────────┘
                                       ▲
                        ┌──────────────┴──────────────┐
                        │  Inbound Intent Parser      │ ← replies, remittance
                        └─────────────────────────────┘
```

### 6.2 Core entities

```python
LeakEvent:
  id, tenant_id, leak_type: {PAYMENT_FAIL, CHECKOUT_ABANDON,
                             MANDATE_DEBIT_DUE, MANDATE_FAIL, INVOICE_OVERDUE}
  subject_ref            # customer or buyer entity
  amount, currency, due_at, occurred_at
  rail: {UPI_AUTOPAY, CARD_MANDATE, UPI_COLLECT, NETBANKING, NEFT_RTGS, NONE}
  raw_codes: {gateway_code, issuer_code, network_category, mac, npci_code}
  context: {mandate_id, invoice_id, cart_id, attempt_index, cycle_id}
  idempotency_key

Subject:                       # customer or B2B buyer
  id, contact_channels[], language_pref, consent_state,
  dnd_status, suppression_flags[], is_udyam_supplier_relationship,
  contact_history[], timezone

Diagnosis:
  root_cause: enum(~24 causes)
  layer: {L1_DETERMINISTIC, L2_INFERRED}
  confidence: float
  permitted_action_classes: set
  evidence: [rule_ids | model_rationale_hash]

ConstraintSnapshot:            # frozen at decision time — critical for replay
  register_version, attempt_counters, consent_state,
  window_state, template_registry_version, budget_remaining

ActionPlan:
  steps: [PlannedAction(kind, scheduled_at, channel, template_id,
                        variables, precondition_step_ids)]
  feasible: bool
  binding_constraints: [rule_id]
  ev_net: decimal
  solver_stats

DecisionRecord:                # the audit atom
  seq, prev_hash, hash
  event_id, diagnosis, constraint_snapshot_digest,
  considered_plans[], chosen_plan, refusals: [(action, rule_id, reason)],
  policy_version, model_versions, prompt_hash, input_digest,
  responsible_entity_id, timestamp, arm: {TREATMENT, HOLDOUT}
```

### 6.3 The unified leak state machine

```
DETECTED
  ├─▶ SUPPRESSED_RECONCILED     (already paid / TDS short-pay / duplicate)
  └─▶ DIAGNOSED
        ├─▶ NO_LEGAL_ACTION      → HUMAN_ESCALATED   (solver infeasible)
        ├─▶ PLANNED
        │     ├─▶ PRE_EMPTED     (T-48 reschedule/notify; mandate path)
        │     ├─▶ ACTION_DISPATCHED
        │     │     ├─▶ AWAITING_OUTCOME
        │     │     ├─▶ PROMISE_TO_PAY   (inbound intent; re-plan around date)
        │     │     ├─▶ DISPUTED         (inbound "already paid" → recon loop)
        │     │     └─▶ OPTED_OUT        (terminal, permanent)
        │     └─▶ DEFERRED       (window/blackout; re-enter at legal time)
        ├─▶ RECOVERED            (terminal)
        ├─▶ BUDGET_EXHAUSTED     (attempt cap hit; terminal for cycle)
        └─▶ WRITTEN_OFF          (terminal)
```

Four leak types, one machine. Adapters differ only in which action classes and constraints are in play. This is the abstraction claim, and the demo must show it holding across all four.

---

## 7. Subsystem specifications

### 7.1 Ingestion & normalisation

Consumes webhook-shaped events (Razorpay-style payloads for `payment.failed`, `subscription.charged`, `subscription.pending`, plus invoice and cart feeds). Normalises to `LeakEvent`.

- **Idempotency:** dedupe key = `(tenant, source_event_id)`. Duplicate webhooks are a real production failure and are in the red-team suite.
- **Ordering:** events carry a monotonic cycle/attempt index; out-of-order delivery must not double-count attempts.
- **Code normalisation:** a mapping layer that unifies gateway codes, ISO 8583 issuer response codes, Mastercard MACs, Visa decline category codes and NPCI/UPI codes into one namespace, preserving the original.

### 7.2 Reconciliation guard — *do not chase people who paid you*

Runs **before** anything else. Suppression outcomes:

| Check | Logic | Outcome |
|---|---|---|
| Settled-but-unwebhooked | Ledger shows a settled payment matching amount+ref within window | `SUPPRESSED_RECONCILED` |
| Duplicate event | Idempotency key already seen | Drop |
| Partial payment | Received < invoice, remainder above TDS tolerance | Re-scope to residual amount |
| **TDS short-payment** | `\|invoice − received − expected_TDS(section, rate)\| ≤ ₹1 tolerance` where the rate is inferred from the buyer's declared section (194C/194J/194H etc.) | `SUPPRESSED_RECONCILED` + flag "TDS withheld, request Form 16A" |
| Credit note applied | Open credit note matches residual | Suppress |

**Metric it produces:** *do-not-chase suppressions*, a Tier-1 real number. If this fires even a handful of times in the demo batch, it is the most persuasive slide you have, because every finance person in the room has been on the wrong end of it.

### 7.3 Diagnosis resolver (two layers)

**Layer 1 — deterministic (target: ~85% of events).**
A lookup from `(network, code, mac/category)` to `(root_cause, permitted_action_classes)`. This is a table, not a model, and it is *correct by construction*. Root causes include: insufficient funds, issuer technical decline, expired card, closed account, suspected fraud, mandate revoked, mandate not found, amount exceeds mandate cap, AFA required (above threshold), PDN missing/late, velocity/limit exceeded, peak-window technical decline, checkout session timeout, app-switch abandonment, buyer dispute, TDS withholding, awaiting GRN/acceptance, invoice dispute, deliberate delay.

**Layer 2 — LLM inference (the ~15% where it earns its keep).**
Triggered when: no MAC/category present (common with smaller Indian issuers), the code is non-standard, or the signal is free text. Inputs: issuer identity, historical decline pattern for that issuer/bank, subject payment history, amount, time of day, rail. Output: a root-cause distribution with calibrated confidence.
**Hard rule:** confidence below threshold routes to the conservative branch, which is always the more restrictive action set. Under-confidence must never expand what is permitted. The console shows the layer badge (L1 green / L2 amber) on every case so a judge can see the boundary is deliberate.

**Why this is right:** the networks already publish the retry instruction, so inferring it with retrieval would be theatre. The genuine uncertainty is where the instruction is *absent*, and that is exactly where the model runs.

### 7.4 T-48 pre-emption engine (headline feature)

Applies to `MANDATE_DEBIT_DUE` events, generated on a schedule 72 hours before each due debit.

**Inputs:** mandate history (last N cycle outcomes), issuer/bank health (NPCI publishes per-bank monthly technical-decline and uptime statistics — a real, public, citable signal), amount vs mandate cap headroom, calendar position (salary-cycle proximity, month-end clustering), and the subject's historical successful-debit hours.

**Outputs — a pre-emption plan:**
1. **Slot selection.** Choose a debit time outside the ~10:00–13:00 peak band (`NPCI-PEAK-01`), preferring the subject's historically successful window.
2. **Date selection.** Shift within the permitted mandate date rule toward salary-cycle proximity where the cause history is insufficient-funds.
3. **PDN scheduling.** Emit the notify action ≥24h ahead, respecting the 23:50 cutoff (`NPCI-PDN-02`), and treat PDN success as a precondition for the debit step (`NPCI-PDN-03`).
4. **Rail arbitration.** If the amount now exceeds the mandate cap or the AFA threshold (`RBI-EM-01/02`, `NPCI-MIT-01`), do not schedule a debit at all — schedule a re-authorisation flow.
5. **Top-up nudge.** For high insufficient-funds risk, select a registered *service*-category template reminding the customer of the upcoming debit and amount, dispatched inside contact hours.

**The demo line:** *"This debit hasn't failed yet. It's scheduled for 10:40 AM tomorrow on a bank with elevated peak-hour declines, for a customer whose last two failures were both insufficient funds three days before payday. We moved it to 9:15 PM on the 2nd and sent the PDN with a top-up reminder. That's a recovery we made before there was anything to recover."*

Nobody else in the track will show this.

### 7.5 Plan solver (CP-SAT)

**Decision variables:** for each candidate action *a* in the action set and each discrete time slot *t* over a 14-day horizon, a boolean `x[a,t]`.

**Hard constraints (from the register):**
- `Σ x[retry, t] ≤ attempts_remaining` (`NPCI-ATT-01`, `NET-VISA-02`, `NET-MC-02`)
- `x[debit,t] ⇒ ∃ x[pdn,t'] with t−t' ∈ [24h, 48h]` (`NPCI-PDN-01`)
- `x[pdn,t] = 0` for t in the 23:50 cutoff band with T+1 debit (`NPCI-PDN-02`)
- `x[contact,t] = 0` outside 08:00–19:00 (`RBI-FPC-01`) and outside 09:00–21:00 for promotional class
- `x[retry,*] = 0` when diagnosis ∈ {hard decline, MAC 03, MAC 21, Category 1} (`NET-VISA-01`, `NET-MC-03/04`)
- inter-attempt spacing ≥ 24h (`NET-SOFT-01`, `NET-MC-02`)
- `x[sms,t] ⇒ template_available(category, language)` (`TRAI-DLT-01`)
- consent and opt-out preconditions (`RBI-EM-04`, `DPDP-01`)
- contact-frequency cap per rolling window (internal anti-fatigue policy)
- total action cost ≤ budget

**Soft constraints (penalised):** peak-window debits, contact fatigue, weekend contact, channel-preference mismatch.

**Objective:** maximise `Σ EV(a,t)` per §7.6.

**Infeasibility is a first-class output.** When no plan exists, the solver returns the *binding constraint set*, and the case becomes `NO_LEGAL_ACTION → HUMAN_ESCALATED` with a human-readable reason: *"No legal action available before 12 Oct: mandate attempts exhausted (NPCI-ATT-01), card retry prohibited (NET-MC-03), customer opted out of SMS (DPDP-01). Recommend manual outreach via the registered relationship manager."*

That refusal screen is worth more to a fintech judge than any success screen.

### 7.6 Expected-value ranking

```
EV(a,t) =  P(success | root_cause, attempt_index, slot, rail, issuer_health) × amount_recoverable
         − direct_cost(a)                    # gateway fee, SMS cost, agent minutes
         − P(penalty | a, code_category) × penalty_amount   # Visa/MC excessive-attempt fees
         − fatigue_cost(contact_count, days_since_last)
         − churn_risk_cost(a, subject_tenure)
```

A **do-nothing arm** (`EV = 0`) is always in the candidate set. Cases where the agent's best action is no action get their own counter on the dashboard, labelled *restraint*. This is a genuinely differentiated metric: it demonstrates the system is optimising net value, not activity.

For receivables, `amount_recoverable` includes the `MSME-16-01` interest exposure where applicable, which is why the 43B(h) reminder ranks so highly — its EV is high *and* its cost and annoyance are near zero.

### 7.7 Bounded executors

Each executor is deterministic, idempotent, sandboxed, and refuses any action lacking a valid plan certificate.

| Executor | Bound |
|---|---|
| `mandate.represent` | Requires attempts_remaining > 0, valid PDN in window, mandate active |
| `message.send` | Requires `template_id` from the registry + all tagged variables present; runs the **DLT scrub simulator** (exact-match check against the registered body, URL whitelist check) and hard-fails on mismatch |
| `link.issue` | Card-update / re-auth / checkout-recovery link, signed and expiring |
| `ar.escalate` | Escalation ladder: reminder → statement of account → 43B(h) notice → relationship-manager handoff. Never skips a rung |
| `human.handoff` | Emits a case packet with the full decision trace |
| `voice.script` | (Stretch) Generates a script that begins with AI self-identification (`AI-DISC-01`), enforces the 08:00–19:00 window, and blocks third-party disclosure by construction |

**The scrub simulator is a demo moment.** Show an LLM-authored "improved" message getting rejected by the scrubber, then the template-selected version passing. Ten seconds, enormous credibility.

### 7.8 Inbound intent parser (where the LLM genuinely belongs)

Inputs: SMS/WhatsApp replies, AR email threads, remittance advices, payment-note free text.

Outputs (structured, typed):
- `OPT_OUT` → permanent suppression, terminal, no further contact ever
- `PROMISE_TO_PAY(date, amount, confidence)` → creates a PTP object; solver re-plans around it and suppresses contact until date+1
- `ALREADY_PAID(reference?)` → routes to the reconciliation guard, suppresses contact pending resolution
- `DISPUTE(reason)` → routes to human, blocks automated chasing
- `TDS_WITHHELD(section, amount)` → reconciliation rule
- `HARDSHIP` → contact-frequency reduction and empathy routing
- `CHANNEL_SWITCH(preferred)`

**PII handling:** text is tokenised through a PII vault before any model call (`DPDP-02`), and the vault mapping never leaves the boundary. Show this in the architecture slide.

### 7.9 Proof-carrying audit ledger

Every decision appends a `DecisionRecord` with `hash = H(prev_hash ‖ canonical_json(record))`. The ledger stores refusals with equal weight to actions — *what we chose not to do and which rule stopped us* is the compliance story.

**Regulator Mode.** Pick any contact ever made and get:
- the exact constraint snapshot at decision time
- the rule IDs satisfied, each linking to its source citation
- the alternatives considered and why they lost
- policy version, model versions, prompt hash
- a **replay** button that re-executes the decision from the frozen snapshot and asserts bit-identical output

**Replay determinism is a Tier-2 metric and must be 100%.** Publish it.

**Kill switch.** A global halt that drains in-flight actions and marks the reason. Fintech judges look for this reflexively.

### 7.10 Measurement framework

- **Assignment.** Subjects assigned to `TREATMENT` / `HOLDOUT` at ingestion, deterministically hashed on subject ID so assignment is stable and replayable. Holdout receives statutory-only communications (post-debit confirmations under `RBI-EM-03` still go out — a nice detail showing the holdout is legally correct, not just switched off).
- **Outcome model.** A separate module with parameters frozen and version-pinned *before* the policy engine was written, documented in the README. It converts `(root_cause, action, slot, attempt_index, subject_profile)` into a payment probability, with base rates anchored to published figures where they exist (UPI Autopay 8–15% failure, card mandate 2–3%, retry-recovery bands).
- **Sensitivity sweep.** Run the whole batch across a grid of outcome-model parameters (±40% on each key rate). Report uplift as a **band**: *"net recovery uplift +X% to +Y% across the sweep; the sign is stable across all N parameter settings."* Stability of sign is a far stronger claim than a single tuned point, and it is honest.
- **Exception report.** Cases where nothing worked, itemised by binding constraint. Publishing your failures is what separates a submission from a pitch.

---

## 8. Where AI is used, and where it deliberately is not

| Function | Approach | Justification |
|---|---|---|
| Decline-code → root cause (labelled) | Deterministic table | The network already publishes the instruction; inference here would be theatre and would introduce error |
| Decline-code → root cause (unlabelled) | LLM with calibrated confidence | Genuine uncertainty; smaller issuers omit MACs |
| Failure prediction at T-48 | Gradient-boosted model on mandate/issuer/calendar features | Tabular, structured, needs calibration not language |
| Slot & date optimisation | CP-SAT solver | Hard constraints require proof, not probability |
| Should-we-act decision | Deterministic policy + EV arithmetic | Money actions must be auditable and hallucination-immune |
| Outbound message content | Template selection + variable fill (LLM chooses the template & language variant) | `TRAI-DLT-01` makes free generation illegal |
| Inbound reply understanding | LLM structured extraction | Genuinely unstructured natural language |
| Remittance advice / TDS parsing | LLM + arithmetic verification | Free-text with a checkable numeric invariant |
| Case summary for human handoff | LLM | Summarisation, no authority over action |
| Operator Q&A ("why did we skip case 4412?") | LLM over the audit ledger, read-only | Explanation, not decision |

**The line to say out loud in the demo:** *"The LLM never decides whether money moves and never writes a word that goes to a customer. It reads, it classifies, it explains. Everything with legal or financial consequence is deterministic and provable."*

That single sentence is what makes a payments engineer trust the build.

---

## 9. Synthetic data specification

Target: **1,200 subjects, ~3,500 events**, Indian-realistic.

**Subject generation:** name/phone/language distribution weighted to real Indian usage (Hindi, English, Tamil, Telugu, Marathi, Bengali, Kannada); consent state; DND status; tenure; historical successful-debit hours; salary-day inference for a subset.

**Merchants:** 6 archetypes — D2C subscription box, OTT, EdTech, SaaS, NBFC EMI, B2B manufacturer — each with different category thresholds (`RBI-EM-02`), rails and ticket sizes.

**Issuers:** ~14 synthetic banks with per-bank technical-decline rates and peak-hour degradation curves, modelled on the shape of NPCI's published per-bank TD/uptime statistics.

**Event mix:**
| Leak type | Volume | Notes |
|---|---|---|
| Mandate debit due (T-48 candidates) | 1,400 | The pre-emption surface |
| Mandate/subscription failure | 900 | Code distribution weighted realistically: ~55% insufficient funds, ~15% technical, ~10% mandate issues, ~8% expired/closed, ~5% cap/AFA, ~4% fraud-suspected, ~3% other |
| Checkout abandonment | 700 | With UPI app-switch timeouts overrepresented per Tier-2/3 latency reality |
| Invoice overdue (B2B) | 500 | Including 60 TDS short-payments, 25 disputes, 40 Udyam-supplier relationships nearing the 45-day line |

**Deliberate landmines seeded in the data** (these are the demo):
duplicate webhooks · payment settling between decision and dispatch · opt-out arriving mid-sequence · mandate revoked after first-presentation failure · debit scheduled inside peak window · PDN attempted at 23:52 · amount raised above the ₹15,000 AFA threshold mid-cycle · MAC 21 on a card with 9 attempts remaining · TDS short-payment on a large invoice · reply "bhai paisa bhej diya kal" (already-paid claim in Hinglish) · reply "STOP" · a subject flagged for calamitous timing · an invoice to a Udyam micro-enterprise 41 days old.

Each landmine maps to a red-team case (§12).

---

## 10. Success metrics

### Tier 1 — real (headline these)
| Metric | Target |
|---|---|
| Compliance violations across the batch | **0** |
| Prohibited actions blocked (attempted by a naive baseline, blocked by Samyak) | Report absolute count |
| Do-not-chase suppressions | Report count and ₹ value of avoided wrongful chases |
| Avoidable network-penalty exposure avoided (₹) | Report vs baseline |
| Restraint rate (cases where do-nothing won) | Report |

### Tier 2 — structural
Plan feasibility rate · infeasible-case escalation rate (must be 100% of infeasible cases, never silently dropped) · replay determinism (100%) · p95 decision latency (<400ms excluding LLM, <2.5s with) · L1 deterministic coverage (~85%).

### Tier 3 — simulated, reported as a band
Net recovery uplift vs holdout across the sensitivity sweep · sign stability across the grid · recovery by root cause · pre-emption effect (failures prevented at T-48 vs baseline schedule).

### The comparison table that wins the demo

Run three policies over the identical batch:

| | Naive dunning (baseline) | Rules-only | **Samyak** |
|---|---|---|---|
| Gross recovered (sim) | — | — | — |
| Network penalties incurred | high | some | **0** |
| Compliance violations | many | some | **0** |
| Wrongful chases (already paid) | many | some | **0** |
| **Net recovered after cost** | — | — | **highest** |

Showing that the naive baseline recovers *more gross and less net* is the single most memorable slide you can put in front of a payments judge.

---

## 11. Operator console (what judges actually look at)

**Screen 1 — Money funnel.** ₹ at risk → ₹ suppressed as not-actually-owed → ₹ with a feasible legal plan → ₹ acted on → ₹ recovered (band). Holdout bar beside treatment bar.

**Screen 2 — Live case stream.** Rows animate as events flow. Colour-coded by outcome, with refusals visually prominent rather than hidden. A judge should be able to see refusals happening without being told.

**Screen 3 — Case detail (the money shot).** For one case: raw event → diagnosis with L1/L2 badge → constraint inspector showing every rule evaluated with pass/fail and its citation → the solver's considered plans with EVs → the chosen plan on a timeline → dispatched artifact with template ID and scrub verdict.

**Screen 4 — Regulator Mode.** Search any contact. Get the proof, the chain hash, and a replay button.

**Screen 5 — Policy comparison.** The three-policy table above, with the sensitivity slider live so a judge can drag the outcome-model parameters and watch the uplift band move while the violation count stays pinned at zero. **That interaction is the wow moment** — it makes the honesty of the measurement into a feature rather than a caveat.

---

## 12. Red-team suite (ship this as a passing test table)

| # | Scenario | Required behaviour |
|---|---|---|
| 1 | Duplicate webhook for same failure | Dedupe; attempt counter increments once |
| 2 | Payment settles between decision and dispatch | Pre-dispatch recheck suppresses the action |
| 3 | Opt-out arrives mid-sequence | All queued actions cancelled; terminal state; no further contact |
| 4 | Hard decline (Visa Category 1) | Zero retries; route to update flow |
| 5 | MAC 03 returned | Zero retries; penalty avoided; logged with rule ID |
| 6 | MAC 21 (cardholder cancelled) | Terminal; re-onboarding path, not retry |
| 7 | 4th mandate attempt requested | Blocked at `NPCI-ATT-01`; cycle marked exhausted |
| 8 | PDN attempted at 23:52 for T+1 debit | Rejected; debit rescheduled to T+2 with valid PDN |
| 9 | First presentation fails | Mandate treated as revoked; re-onboarding branch |
| 10 | Amount raised above ₹15,000 mid-cycle | Debit not scheduled; AFA re-auth flow issued |
| 11 | Contact attempted at 19:40 | Deferred to 08:00 next day, logged as deferral not failure |
| 12 | LLM-drafted "better" SMS submitted | Scrub simulator rejects; registered template substituted |
| 13 | TDS short-payment on ₹18L invoice | Suppressed as reconciled; Form 16A request issued, not a chase |
| 14 | Hinglish reply "paisa bhej diya" | Parsed as ALREADY_PAID; contact suppressed; recon loop opened |
| 15 | Calamitous-timing flag set | All contact suppressed regardless of legal hours |

Put the passing table in the README. Fifteen green rows is more persuasive than any prose.

---

## 13. Build plan (48 hours, with cut lines)

**Rule: nothing on the P1 list may be started before every P0 item is green.**

| Block | Hours | Deliverable | Priority |
|---|---|---|---|
| B1 | 0–4 | Repo, entities, event bus, state machine skeleton, synthetic generator v1 (subjects + mandate/failure events) | P0 |
| B2 | 4–9 | Constraint register as data (all ~30 rules with IDs, predicates, citations) + unit tests per rule | P0 — *this is the moat; do it early and do it properly* |
| B3 | 9–13 | L1 deterministic diagnosis resolver + code normalisation across networks | P0 |
| B4 | 13–18 | CP-SAT solver: variables, hard constraints, infeasibility reporting | P0 |
| B5 | 18–21 | EV ranker + do-nothing arm; bounded executors with the DLT scrub simulator | P0 |
| B6 | 21–25 | Reconciliation guard incl. TDS rule; audit ledger with hash chain + replay | P0 |
| B7 | 25–29 | Outcome simulator (params frozen & committed first), treatment/holdout, sensitivity sweep runner | P0 |
| B8 | 29–34 | Console screens 1, 3, 5 (funnel, case detail, policy comparison) | P0 |
| B9 | 34–37 | T-48 pre-emption engine + issuer health model | **P1 — highest-value P1; protect this** |
| B10 | 37–40 | L2 LLM diagnosis fallback + inbound intent parser | P1 |
| B11 | 40–43 | Checkout + receivables adapters (proving the abstraction), 43B(h) escalation ladder | P1 |
| B12 | 43–45 | Red-team suite green; Regulator Mode screen | P1 |
| B13 | 45–48 | README, demo video, sensitivity numbers frozen, submit with buffer | P0 |

**Cut lines, in the order you cut them:** voice scripts → screens 2 & 4 → checkout adapter → L2 LLM fallback (fall back to conservative default, which is correct behaviour anyway) → receivables adapter.
**Never cut:** the constraint register, the solver, the audit chain, the zero-violation metric, the honest measurement framing.

---

## 14. Tech stack (aligned to how Razorpay actually builds)

Razorpay runs Go services on Kubernetes with Kafka event pipelines, PostgreSQL, and CDC/outbox patterns for consistency across a monolith-to-microservices migration. Mirroring that shape signals you understand the environment.

| Layer | Choice | Note |
|---|---|---|
| Event bus | Kafka (Redpanda locally) | Matches Razorpay's event-driven backbone; topics per leak type |
| Core services | Go for ingestion/executors; Python for solver, ML, LLM | Go where throughput and idempotency matter, Python where the maths lives |
| Consistency | Outbox pattern + CDC | The exact pattern their platform team uses; call it out in the README |
| Store | PostgreSQL (events, ledger, register), Redis (counters, windows, idempotency) | Rolling attempt windows fit Redis naturally |
| Solver | OR-Tools CP-SAT | |
| Prediction | LightGBM / XGBoost with isotonic calibration | Calibration matters because EV depends on probability being honest |
| LLM | Claude via API, structured output, PII-tokenised inputs | |
| Console | React + Tailwind + Recharts | |
| Packaging | Docker Compose, single `make demo` | Judges must be able to run it |
| Determinism | Seeded RNG everywhere; frozen params committed with a git tag | Replay determinism depends on this |

---

## 15. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Solver over-engineering eats the clock | B4 timeboxed to 5h; fallback is a topological rules chain with the identical register — the register is what matters, the solver is the elegance |
| Judges dismiss simulated outcomes | Tier-1 metrics are real and lead the pitch; sensitivity band replaces point estimate; state the limitation before they do |
| Too many features, none finished | Hard cut lines in §13; P0 alone is a complete, coherent submission |
| Constraint claims challenged on accuracy | Every rule carries a source citation in the register; being asked "where did you get NPCI-ATT-01?" and answering instantly is a win, not a risk |
| "Isn't this just Razorpay's smart retries?" | Prepared answer: smart retries optimise *when* on one rail; Samyak decides *whether it is legal, feasible and worth it* across four leak types, and proves it. We hand execution to their retry engine |
| Demo breaks live | Pre-recorded 90s video plus a deterministic seeded run; `make demo` reproduces identical numbers every time |

---

## 16. Roadmap beyond the hackathon (include this — it signals product thinking)

- **v1.1** Constrained contextual bandit over action arms, exploring only inside the feasible set the solver returns. Safe exploration is a genuinely publishable idea.
- **v1.2** Constraint register as a versioned, subscribable feed. When RBI issues a circular, every deployment updates and re-plans. This is the actual business.
- **v1.3** Real DLT template registry integration with automated template-gap detection ("you have no approved Tamil service template for mandate failure — here is the draft to register").
- **v1.4** TReDS hand-off for accepted receivables that fail recovery, converting an unrecoverable chase into liquidity.
- **v2.0** Cross-merchant issuer-health federation: aggregate anonymised decline patterns to predict bank degradation before NPCI publishes monthly stats.

---

## 17. The 90-second demo script

> **0:00** "Every team in this track built something that reacts to a failed payment. We built something that stops it from failing, and can prove every decision it made was legal."
>
> **0:10** *Screen 3, case 1.* "This debit hasn't failed yet. Due tomorrow 10:40 AM — inside NPCI's peak window on a bank with elevated technical declines, for a customer whose last two failures were insufficient funds, three days before payday. We moved it to 9:15 PM on the 2nd, sent the pre-debit notification 26 hours ahead, and issued a top-up reminder. Recovery before there was anything to recover."
>
> **0:30** *Case 2.* "Hard decline, Mastercard MAC 03. A naive dunner retries this and pays a network penalty on the first attempt. We refuse, and route to a card-update link." *Constraint inspector flashes NET-MC-03.*
>
> **0:40** *Case 3.* "₹18 lakh invoice, flagged overdue. It isn't. The buyer withheld TDS under 194C. We suppressed the chase and requested Form 16A instead. That's a customer relationship we didn't destroy."
>
> **0:50** *Case 4.* "An LLM wrote a better message. TRAI's scrubber blocks it, because in India you cannot send text that doesn't match a registered template. So our model picks the template and fills the tagged variables." *Rejected, then accepted.*
>
> **1:05** *Screen 5.* "Three policies, same batch. Naive dunning recovers more gross and less net, with 47 compliance violations. We recover less gross, zero violations, and more money."
>
> **1:15** *Drag the sensitivity slider.* "Our uplift is simulated, so we show it as a band across a parameter sweep. Watch the band move. Watch the violation count. It stays at zero, because that number isn't simulated — it's a property of the decision logic."
>
> **1:25** *Regulator Mode.* "Every action carries a proof. Rule IDs, constraint snapshot, model versions, hash-chained. Click replay: the decision reproduces bit-for-bit."
>
> **1:30** "Samyak. Right action on every rupee at risk."

---

## Appendix A — Naming

**Samyak** (सम्यक्) — "right, proper, correct." From *samyak-karmānta*, right action. Neutral across Indian languages, non-coercive, and it states the thesis.

Deliberately avoid names in the *vasooli / recovery-goon* register. RBI has been actively tightening rules on coercive recovery conduct, and a compliance-forward product undermines itself in one word if it sounds like a collections enforcer. English subtitle for the README: **"the recovery control plane."**

## Appendix B — README structure (judges skim; engineer this)

1. One-paragraph thesis
2. **The constraint table** — put it above the fold; it is the strongest single artifact
3. The three innovations with one screenshot each
4. **The honest-measurement paragraph**, stated plainly: what is simulated, what is not, why the violation count is the number that matters
5. Red-team pass table (15 rows, all green)
6. Architecture diagram
7. `make demo` — deterministic, reproducible
8. What we would build next
9. Every rule ID linked to its source

## Appendix C — Anticipated judge questions

| Question | Answer |
|---|---|
| "Isn't the uplift number just your simulator?" | Yes, and we say so. It is reported as a band across a parameter sweep with the sign stable throughout. The headline metric is the violation count, which is a property of our logic, not our simulator. |
| "Why not RAG the decline codes?" | Because the networks already publish the instruction in the response — Visa decline category codes and Mastercard MACs. Retrieval there would add error to a solved mapping. We use the model where the instruction is absent, which is common with smaller Indian issuers. |
| "Why a solver and not if-statements?" | Because the constraints interact. PDN lead time couples to the debit slot, which couples to the peak-window penalty, which couples to the attempt budget, which couples to the AFA threshold. A rules chain gives you an answer; a solver gives you a *proof*, and tells you when no legal answer exists. |
| "Razorpay already has smart retries." | Yes, and we would call them. Smart retries answer *when to retry on this rail*. We answer *whether any action is legal, feasible, and worth more than it costs, across four leak types* — and we can prove it afterwards. |
| "What breaks first at scale?" | The solver, at ~14-day horizons with large action sets. Mitigation is horizon truncation and warm-starting from the previous plan; the register and executors scale horizontally on Kafka partitions keyed by subject. |
