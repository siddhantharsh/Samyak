# AGENTS.md — Samyak

Read this fully before every task. It overrides your defaults.

## What this is

Samyak is a **revenue recovery control plane** for Indian payments. It decides
whether a recovery action is *legal*, *feasible on the rails*, and *worth more
than it costs* — then proves it afterwards.

Full spec: `docs/SAMYAK_PRD.md`. Read the sections named in your task prompt.
Do not read the whole PRD and try to build everything at once.

## Hard invariants — never violate these, in any task

1. **The LLM never decides whether money moves.** All money and contact
   decisions are deterministic code plus the constraint solver. If you find
   yourself writing a prompt that asks a model "should we retry this?", stop:
   that belongs in `core/policy/`.

2. **The LLM never authors outbound customer text.** Indian TRAI DLT rules block
   any SMS whose content doesn't exactly match a pre-registered template. The
   model may *select* a template ID and *fill tagged variables*. It may not
   write, reword, improve, or "personalise" message bodies. If you generate
   message copy, you have broken the product's core claim.

3. **Never author, edit, invent, or "correct" a regulatory rule.**
   `data/constraints.yaml` is human-maintained ground truth. You may read it,
   load it, index it, and write code that evaluates it. You may not add rules,
   change thresholds, or fill gaps from your own knowledge. If a rule you need
   is missing, stop and tell the user which rule ID is missing.

4. **Never modify `sim/outcome_params.frozen.yaml`.** Those parameters were
   frozen before the policy engine existed. The honesty of the entire
   measurement framework depends on them not being tuned. If results look bad,
   that is a finding, not a bug. Report it; do not fix it by editing that file.

5. **Refusals are first-class output.** Every blocked action must be recorded
   in the audit ledger with the rule ID that blocked it. Silently dropping a
   case is a bug of the highest severity.

6. **Determinism.** Every random draw uses the seeded RNG in `core/rng.py`.
   No `random.random()`, no `datetime.now()` inside decision paths — time is
   injected. `make demo` must produce byte-identical output across runs.

7. **Idempotency.** Every executor and every ingestion path is keyed and safe
   to call twice. Duplicate webhooks are in the test suite.

## Scope discipline

- Build **only** what the current task prompt asks for. Do not scaffold ahead.
- If you think an adjacent piece is needed, say so and stop. Do not build it.
- No UI work until the task prompt explicitly says UI.
- No new dependencies without naming them and why in the implementation plan.

## Definition of done (every task)

A task is not complete until all of these hold:

- [ ] Tests for the new code pass (`make test`)
- [ ] `make demo` still runs end to end and is deterministic
- [ ] No new `TODO` or `pass  # stub` in code paths the task claimed to finish
- [ ] You have stated, in the walkthrough artifact, what you did **not** build
- [ ] Any assumption you made is listed explicitly, not buried in code

If you cannot satisfy these, say so plainly rather than declaring success.

## Repo layout

```
data/constraints.yaml         # ground truth rules — READ ONLY for you
data/templates.yaml           # DLT-registered message templates — READ ONLY
sim/outcome_params.frozen.yaml# frozen sim params — READ ONLY for you
core/
  entities.py                 # LeakEvent, Subject, Diagnosis, DecisionRecord...
  rng.py                      # seeded RNG, injected clock
  ingest/                     # normalisation, idempotency
  recon/                      # do-not-chase guard, TDS rule
  diagnose/                   # L1 deterministic resolver, L2 model fallback
  constraints/                # register loader + predicate evaluation
  plan/                       # CP-SAT solver, infeasibility reporting
  ev/                         # expected value ranking
  execute/                    # bounded executors + DLT scrub simulator
  audit/                      # hash-chained ledger, replay
  preempt/                    # T-48 engine
sim/                          # synthetic data generator, outcome model, sweep
console/                      # React UI — only touched in UI tasks
tests/redteam/                # the 15 adversarial cases
```

## Style

- Python 3.11, type hints on all public functions, `ruff` clean.
- Pure functions in decision paths. Side effects only in `execute/` and `audit/`.
- Errors are values in decision paths, not exceptions. A case that cannot be
  decided becomes `NO_LEGAL_ACTION`, never a crash.
- Comments explain *why* a rule exists, with its rule ID. Not what the code does.

## Communication

- In Planning Mode, your implementation plan must list: files touched, the
  interfaces you will define, what you are explicitly not doing, and the
  verification you will run. Wait for approval.
- Do not claim something works because it compiles. Run it.
