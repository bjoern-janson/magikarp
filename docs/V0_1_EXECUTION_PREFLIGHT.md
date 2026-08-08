# MAGIKARP v0.1 — Execution Preflight

**Status:** post-freeze execution governance for the frozen v0.1 hypothesis.  
**Authority:** implementation and result-interpretation rules only; this document does not expand the conceptual ontology or change the primary research claim. Evidence eligibility and top-level outcome authority are governed by [`../EVIDENCE-RUN-PROTOCOL-v0.1.md`](../EVIDENCE-RUN-PROTOCOL-v0.1.md).

## Purpose

The v0.1 conceptual contract is already frozen. Before an evidence-bearing run, the implementation must also freeze the remaining operational choices that could otherwise be tuned after seeing outcomes.

The rule is:

> **Freeze the measurement and validity surface before inspecting the result.**

A smoke test may be used to debug code and benchmark invariants. A smoke test is not evidence for or against MAGIKARP.

---

## 1. Empirical chain to preserve

The implementation must keep these objects separate:

\[
F
\rightarrow
q_{SD}(F\mid E_{\mathrm{diag}})
\rightarrow
D_{\mathrm{revision}}
\rightarrow
Y_{\mathrm{adapt}}.
\]

- \(F\): experimenter-controlled ground-truth failure depth.
- \(q_{SD}\): prospective diagnostic distribution produced before unrestricted adaptation.
- \(D_{\mathrm{revision}}\): revision depth actually selected during adaptation.
- \(Y_{\mathrm{adapt}}\): later held-out adaptation trajectory.

Do not infer diagnosis from the revision selected, and do not infer either from eventual recovery.

---

## 2. Frozen failure-depth vocabulary

For v0.1:

\[
F\in\{F_p,F_m,F_i\}
\]

with the ordered intervention depths:

```text
0 = parameter
1 = model
2 = interface
```

The generator must establish by construction that:

- `F_p` is solvable by parameter revision while the model and interface remain adequate;
- `F_m` is not solvable by parameter-only revision but is solvable by changing the model relationship while keeping the interface fixed;
- `F_i` is not solvable over the old interface and requires the benchmark-defined interface-expansion action.

If these intervention claims cannot be demonstrated by oracle or exhaustive checks, the benchmark is invalid and no MAGIKARP result may be interpreted.

---

## 3. Diagnostic output and primary SD metric

Agents should emit the raw diagnostic distribution:

\[
q_{SD}=(q(F_p),q(F_m),q(F_i)).
\]

Preserve the raw probabilities for every diagnostic episode.

For the first v0.1 evidence-bearing run, use **normalized negative multiclass Brier loss** as the primary scalar `SD` measure:

\[
SD
=
1-
\frac{1}{2N}
\sum_{n=1}^{N}
\sum_{k\in\{p,m,i\}}
\left(q_{nk}-\mathbf 1[F_n=k]\right)^2.
\]

Higher is better; perfect diagnosis gives `SD = 1`.

Report separately, but do not substitute post hoc for the primary metric:

- top-1 failure-depth accuracy;
- per-class recall, especially interface-failure recall;
- calibration / reliability summaries;
- diagnostic entropy.

No adaptation outcome may be used to redefine or tune `SD`.

---

## 4. Baseline variables

The evidence-bearing implementation must emit explicit scalar versions of the controls used in the primary comparison.

### Q — present competence

`Q` is mean normalized performance on a clean pre-perturbation evaluation set, measured before diagnostic or adaptation perturbations.

### E — ordinary error sensitivity

`E` is mean task loss or prediction-error magnitude on the pre-adaptation perturbation probes **before any unrestricted corrective action**.

Its purpose is to control the simpler explanation that `SD` merely measures how strongly the system notices error.

### A — standard adaptation ability

For the first benchmark, `A` is recovery on a separate ordinary parameter-shift calibration suite under the same fixed adaptation budget used by the main task where practical.

This calibration suite must be disjoint from the diagnostic and held-out adaptation generators.

If the implementation uses a different operationalization of `Q`, `E`, or `A` because the task makes these definitions impossible, the replacement must be recorded in the run manifest **before** the evidence-bearing run.

---

## 5. Adaptation outcomes

Always retain the decomposed vector:

\[
Y_{\mathrm{adapt}}=(R_c,T,R,P,C).
\]

For the first v0.1 evidence-bearing run, use **held-out recovery `R_c` after a fixed adaptation budget** as the primary prediction endpoint.

Report all of the following regardless of the primary result:

- `R_c`: recovery;
- `T`: transfer;
- `R`: retention;
- `P`: preservation of still-valid behavior;
- `C`: correction / revision cost.

The fixed adaptation budget matters: a system should not obtain unlimited attempts until every strategy eventually recovers.

Do not create a universal MAGIKARP score.

---

## 6. Revision trace and depth calibration

Record the complete revision trace for every held-out adaptation episode.

At minimum record:

- first committed revision depth;
- maximum revision depth reached;
- number and order of attempted revision classes;
- explicit revision cost;
- whether recovery followed the selected revision.

For the secondary mechanistic analysis, define:

\[
D_{\mathrm{revision}}
=
\text{first committed revision depth}
\]

and, because the correct intervention depth is fixed by construction in v0.1:

\[
E_D
=
\left|
D_{\mathrm{revision}}-D_{\mathrm{sufficient}}(F)
\right|.
\]

Interpret:

- `D_revision < D_sufficient(F)` as under-revision;
- `D_revision > D_sufficient(F)` as over-revision.

This analysis is secondary. It must not replace the frozen primary predictive comparison after results are observed.

---

## 7. Load-bearing agent controls

The first benchmark must include all three behavioral regimes:

1. **Rigid / local updater** — preferentially makes shallow revisions and should expose under-revision on deep failures.
2. **Hyperplastic updater** — escalates readily and should expose over-revision on shallow failures.
3. **Depth-aware updater** — uses diagnostic evidence to select among parameter, model, and interface revision.

A benchmark that includes only deep failures may accidentally reward hyperplasticity. A benchmark that includes only shallow failures may accidentally reward rigidity.

An optional matched heuristic can adapt by fixed thresholds without emitting an explicit `SD`; use it when practical to test whether the predictive signal is reducible to generic responsiveness.

---

## 8. Data and temporal firewalls

Use distinct generator namespaces / seeds for:

```text
baseline competence
standard-adaptation calibration
diagnostic probes
held-out adaptation
transfer / retention
```

For an evidence-bearing v0.1 result, the held-out adaptation set should contain structurally disjoint perturbation families, not merely new random instances, whenever the generator supports such a split.

If only instance-level holdout is implemented initially, label the run **engineering-only** and do not claim failure-family transfer.

No adaptation outcome may influence:

- the diagnostic generator;
- `SD` scoring;
- feature selection for `SD`;
- failure labels;
- baseline definitions;
- split construction.

---

## 9. Benchmark-validity gates

All validity gates must pass before evaluating the primary hypothesis.

### Gate A — failure-depth intervention validity

Demonstrate the intervention claims in Section 2 with oracle or exhaustive checks.

### Gate B — interface impossibility

For `F_i`, verify an observational collision or equivalent impossibility under the old interface. Parameter/model optimization over that interface must not solve the held-out distinction.

### Gate C — diagnostic identifiability

The diagnostic phase must contain enough admissible information to distinguish failure depth in expectation. Do not require inference from information the diagnostic interface removes.

### Gate D — leakage audit

Attempt to predict `F` from nuisance-only information such as generator ID, episode ID, template, sequence length, feature scale, or other surface artifacts.

If nuisance-only prediction materially exceeds an appropriate label-permutation baseline, redesign the generator before interpreting MAGIKARP results.

### Gate E — baseline competence overlap

Agent families should have comparable `Q` where practical. If substantial mismatch remains, preserve it, control for `Q`, and report the overlap rather than hiding it through selective sampling.

### Gate F — revision-cost asymmetry

Confirm that unnecessary deep revision carries measurable cost, while sufficient deep revision remains possible. Otherwise hyperplastic and targeted adaptation are not discriminable.

A failed validity gate produces a **benchmark-invalid** result, not evidence for or against MAGIKARP.

---

## 10. Primary predictive analysis

Keep the frozen comparison:

```text
M0: R_c ~ Q + A + E
M1: R_c ~ Q + A + E + SD
```

Use the same preprocessing and model family for both conditions.

Default v0.1 model family: ordinary linear regression or ridge regression with any regularization selected using training data only. Do not give `M1` additional tuning budget beyond the `SD` feature.

Primary prediction metric:

```text
MAE on held-out adaptation units
```

Define improvement as:

\[
\Delta_{MAE}
=
MAE(M_0)-MAE(M_1).
\]

Positive values favor the `SD`-augmented model.

Estimate uncertainty with a **paired bootstrap over the highest independent held-out unit available** (prefer perturbation family / generator family over individual episodes). Use at least 2,000 bootstrap replicates for the final summary.

A positive v0.1 result requires the preregistered held-out estimate to favor `M1`; report the 95% bootstrap interval and do not replace a null with a favorable secondary endpoint.

If the effect appears only in one failure class, report it as class-specific rather than a general MAGIKARP result.

---

## 11. Run sequence

### Stage 1 — smoke run

Purpose: code/debugging only.

Recommended scale: a small number of seeds sufficient to exercise every failure class and agent regime.

Allowed changes after a smoke run:

- bug fixes;
- generator repairs required by failed validity gates;
- implementation changes needed to realize the already-frozen definitions.

Not allowed:

- choosing a new primary endpoint because the original looks weak;
- redefining `SD` around observed adaptation outcomes;
- removing an unfavorable agent class or failure family without a documented validity reason.

### Stage 2 — freeze manifest

Before the first evidence-bearing run, commit a machine-readable manifest containing:

- git commit SHA;
- Python / dependency versions;
- generator version and config hash;
- all random seeds or seed-generation rule;
- sample counts;
- split identifiers / hashes;
- `Q`, `E`, `A`, and `SD` definitions;
- primary and secondary outcome definitions;
- model family and preprocessing;
- uncertainty procedure;
- validity-gate **definitions and thresholds**;
- any deviations from this preflight and their pre-outcome rationale.

Validity-gate **outcomes** are post-execution observations and must be written to the immutable result artifacts rather than inserted into the pre-outcome manifest.

### Stage 3 — evidence-bearing run

Run once under the frozen manifest, preserving raw-enough artifacts for independent recomputation.

If rerun because of a software defect, preserve the defective result and document why it is invalid rather than silently replacing it.

---

## 12. Required result artifacts

The implementation should emit at least:

```text
results/<run_id>/manifest.json
results/<run_id>/trial_records.jsonl
results/<run_id>/validity.json
results/<run_id>/predictions.csv
results/<run_id>/summary.json
results/<run_id>/summary.md
```

Each trial record should preserve enough information to reconstruct:

```text
agent_id / agent_family
seed / generator_family / split
F
q_SD
SD
Q
E
A
revision_trace
D_revision
R_c
T
R
P
C
```

Compact frozen summaries may later be committed even if raw local outputs remain ignored.

---

## 13. Result status vocabulary

Every run should receive exactly one top-level status:

- `engineering_only` — implementation/smoke run, not evidence-bearing;
- `benchmark_invalid` — one or more validity, provenance, attestation, compatibility, or frozen-run conditions failed;
- `valid_negative` — valid evidence run that does not meet the frozen positive rule;
- `valid_positive` — valid evidence run that meets the frozen positive rule.

A null is not an implementation failure. Material failure-class or preregistered subgroup heterogeneity is reported as a **secondary diagnostic** under the frozen overall positive/null classification; it does not create or replace a top-level evidence status.

---

## 14. Tomorrow-morning definition of ready

Before large execution begins, verify:

- [ ] all three failure depths are implemented and oracle-validated;
- [ ] rigid, hyperplastic, and depth-aware agents run end to end;
- [ ] `q_SD` is emitted before unrestricted adaptation;
- [ ] `SD` is computed only from diagnostic data;
- [ ] `Q`, `E`, and `A` are emitted independently of the held-out outcome;
- [ ] full revision traces are saved;
- [ ] `Y_adapt` remains decomposed;
- [ ] generator/split leakage tests exist;
- [ ] one command runs the complete benchmark;
- [ ] a manifest is frozen before the first evidence-bearing result;
- [ ] negative and invalid results have explicit storage paths.

If those conditions hold, the repository is ready to learn something rather than merely produce a number.
