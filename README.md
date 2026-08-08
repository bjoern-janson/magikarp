# MAGIKARP

**MAGIKARP studies whether prospective sensitivity to representation limits contains independent predictive information about later adaptation when those limits are crossed.**

## Current state

MAGIKARP v0.1 is at an **engineering freeze**.

- conceptual stack: frozen;
- v0.1 predictive hypothesis: frozen;
- deterministic built-in benchmark: implemented;
- validity/provenance/attestation machinery: implemented;
- built-in generator: `L0`, engineering-only;
- qualifying `L2`/`L3` evidence sources: none;
- evidence-bearing v0.1 runs: none.

The next scientific step is **independent evidence acquisition**, not additional ontology or built-in benchmark polish.

### Start here

- [`PROJECT_FREEZE.md`](PROJECT_FREEZE.md) — exact scientific/engineering state preserved at the 2026-08-08 freeze.
- [`CONTINUATION.md`](CONTINUATION.md) — current handoff and next authorized project sequence.
- [`docs/PROJECT_STATE-v0.1.json`](docs/PROJECT_STATE-v0.1.json) — machine-readable snapshot.
- [`docs/INDEPENDENT_GENERATOR_BRIEF-v0.1.md`](docs/INDEPENDENT_GENERATOR_BRIEF-v0.1.md) — restricted handoff for a team intended to preserve a plausible `L2` generator-independence claim.

## From Correctable Lineage to NSS to MAGIKARP

### A one-page guide for new researchers

#### The shared question

The program studies a practical problem: **what should a system do when the way it currently represents the world stops being adequate?** A good system should not merely produce a correct answer today. It should preserve a justified path to becoming appropriately different tomorrow.

The work developed in three linked stages.

#### 1. Correctable Lineage — preserve what deserves to survive

Correctable Lineage began with governance. When a claim, model, or decision is reused, the system should retain its provenance, scope, dependencies, and conditions for reopening it. It separates:

- discovery from validation;
- attention from authority;
- a result being useful from a result being justified.

Its central concern is **correctability**: can a trusted structure be revised without losing the reasons it was trusted, and can a correction path remain independent rather than repeating the same hidden failure?

This is a conceptual and governance framework. It is not yet a demonstrated general-purpose intelligence theory.

#### 2. Negative-Space Search (NSS) — do not expand when the representation is already adequate

NSS turns one part of that concern into a concrete search policy. Given an observed signature, it checks whether available cases with that signature disagree in their trusted labels. If there is no observed collision, it does not launch expensive generic synthesis. If there is a collision, it expands the representation or search space.

The useful result is narrow: **collision-gated search can avoid unnecessary expansion while preserving repair on observed conflicts**. The NSS implementation is an engineering benchmark, not evidence for a unique “negative-space” capability. Its headline candidate-count saving is bookkeeping rather than a full executed-compute comparison, and “no observed collision” does not prove universal adequacy under noise, hidden context, or distribution shift.

NSS therefore supplies a disciplined trigger for representation repair; it does not decide truth or authority by itself.

#### 3. MAGIKARP — measure whether self-diagnosis predicts adaptation

MAGIKARP asks the next empirical question:

> **Before adaptation begins, does a system’s sensitivity to the limits of its own representation predict how well it adapts when those limits are crossed?**

The frozen v0.1 variables are deliberately small:

- **Q:** current competence;
- **SD:** pre-adaptation self-diagnosis of representation limits;
- **F:** controlled failure depth — parameter, model, or interface;
- **Y_adapt:** later held-out outcomes — recovery, transfer, retention, preservation, and correction cost.

The primary comparison is held-out prediction: does adding `SD` to ordinary competence and error measures improve prediction of `Y_adapt`? This is a predictive claim, not yet a causal claim. The benchmark also tests proportional revision: shallow failures should not trigger deep restructuring, while interface failures should not be treated as mere parameter errors.

#### Where the program is now

MAGIKARP has an executable deterministic synthetic loop, validity gates, leakage checks, label-free agent views, grouped held-out analysis, source-bound manifests, and fail-closed attestation/eligibility rules. The repository includes a regression test suite and CI around those engineering boundaries.

The built-in generator is explicitly **engineering-only**: its “families” are namespaced buckets from one generator, not independent structural or external families. No qualifying evidence-bearing generator is currently supplied.

So the current status is:

> **The measurement instrument is operational; the scientific wager remains open.**

#### Where it is heading

The next meaningful step is not more ontology. It is an independently frozen evidence run with structurally distinct or external generator families, independent pre-outcome attestation, preregistered analysis, and held-out tests that can produce positive, negative, or invalid results.

If `SD` adds no reliable predictive value, MAGIKARP should contract. If it does, later stages can test whether targeted interventions increase `SD` and whether the Controlled Adaptation Reasoning Protocol (CARP) improves adaptation.

**In one sentence:** Correctable Lineage governs what may be trusted and reopened; NSS controls when representation search should expand; MAGIKARP tests whether knowing a representation’s limits helps a system adapt.

## Frozen v0.1 question

> **Does prospective failure-depth diagnosis add held-out predictive information about later recovery beyond present competence, ordinary error sensitivity, and the frozen standard-adaptation control?**

Primary comparison:

\[
M_0:R_c\sim Q+A+E
\]

\[
M_1:R_c\sim Q+A+E+SD
\]

The primary claim is predictive, not causal.

## Minimal ontology budget

v0.1 requires only four load-bearing objects:

- **Q** — present competence before perturbation;
- **SD** — prospective pre-adaptation diagnosis of failure depth;
- **F** — experimenter-controlled failure depth;
- **Y_adapt** — later held-out adaptation trajectory.

Failure depth is frozen as:

\[
F\in\{F_p,F_m,F_i\}
\]

- `F_p` — parameter failure;
- `F_m` — model failure;
- `F_i` — interface failure.

Keep outcomes decomposed:

\[
Y_{adapt}=(R_c,T,R,P,C)
\]

- `R_c` — recovery;
- `T` — transfer;
- `R` — retention;
- `P` — preservation;
- `C` — correction/revision cost.

Do not create a universal MAGIKARP score in v0.1.

## Empirical separation

The implementation preserves:

\[
F
\rightarrow
q_{SD}
\rightarrow
D_{revision}
\rightarrow
Y_{adapt}
\]

Diagnosis, revision selection, and eventual recovery are separate empirical objects.

The benchmark-defined interface-expansion action is supplied. v0.1 does **not** test representation invention.

## Executable engineering loop

The repository contains a deterministic synthetic implementation with:

- oracle-validated parameter/model/interface minimum sufficient depths;
- an explicit old-interface collision for interface failure;
- label-free diagnostic agent inputs;
- crossed diagnostic skill and revision-controller behavior;
- rigid, hyperplastic, depth-aware, and matched evidence-heuristic controllers;
- frozen Brier-based `SD` plus secondary diagnostic summaries;
- decomposed outcomes and revision traces;
- validity gates A-F;
- agent-block × generator-bucket held-out `M0`/`M1` analysis;
- source-bound manifests;
- structural-family provenance fields;
- separate independent-attestation records;
- fail-closed evidence eligibility;
- regression tests for the benchmark and evidence boundary.

Quick start:

```text
python -m pip install -e .
python -m unittest discover -s tests -v
magikarp smoke --output results/smoke
```

A healthy smoke run returns `engineering_only`. A failed benchmark-validity gate returns `benchmark_invalid` and suppresses the primary comparison.

Passing the smoke run is evidence that the engineering loop executes, **not** evidence for or against the MAGIKARP hypothesis.

## Evidence boundary

The built-in generator is `builtin_latent_context_v0.1` at independence level `L0`.

Its `generator_family` labels are deterministic seed/index buckets over one mechanism. Therefore:

\[
\text{different buckets}\neq\text{structural independence}
\]

and:

\[
\text{reproducibility}\neq\text{independence}.
\]

No metadata, wrapper, seed change, or attestation can promote the built-in generator into an evidence-bearing source.

A scientifically interpretable run requires a qualifying `L2` or `L3` source, frozen provenance, a source-specific execution path, an independent pre-outcome attestation, passed validity gates, and adherence to the frozen run design.

The current runner is intentionally still bound to the built-in generator. The external evidence schema exists, but a real independent source must exist **before** the minimum execution adapter is built.

## Result authority

Top-level run states are:

- `engineering_only` — deliberately ineligible infrastructure run;
- `benchmark_invalid` — validity/provenance/freeze/attestation condition failed;
- `valid_negative` — valid evidence run that does not satisfy the frozen positive rule;
- `valid_positive` — valid evidence run that satisfies the frozen positive rule.

A valid null is retained evidence. Per-failure heterogeneity is secondary and does not create a fifth top-level status.

A positive v0.1 result supports only the bounded predictive claim. It does not establish causation, representation invention, Controlled Representational Escape, open-ended correctability, recursive improvement, or general intelligence.

## Authority map

Use the documents below according to scope:

1. [`docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md`](docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md) — frozen scientific question, variables, primary test, and claim scope.
2. [`EVIDENCE-RUN-PROTOCOL-v0.1.md`](EVIDENCE-RUN-PROTOCOL-v0.1.md) — normative evidence eligibility, structural independence, provenance, attestation, versioning, and outcome authority.
3. [`docs/V0_1_EXECUTION_PREFLIGHT.md`](docs/V0_1_EXECUTION_PREFLIGHT.md) — operational metrics, validity gates, run sequence, and artifacts.
4. [`docs/REVISION_CONTROLLER_CLARIFICATION.md`](docs/REVISION_CONTROLLER_CLARIFICATION.md) — separation of diagnosis, revision selection, and execution without amending the primary hypothesis.
5. [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) — current executable design and boundary.

Supporting context:

- [`docs/MEASUREMENT_PLAN.md`](docs/MEASUREMENT_PLAN.md)
- [`docs/BENCHMARK_DESIGN.md`](docs/BENCHMARK_DESIGN.md)
- [`docs/REPRESENTATIONAL_GOVERNANCE.md`](docs/REPRESENTATIONAL_GOVERNANCE.md)
- [`docs/CARP.md`](docs/CARP.md)
- [`docs/CONCEPTUAL_LINEAGE.md`](docs/CONCEPTUAL_LINEAGE.md)
- [`docs/CONCEPTUAL_RESERVE.md`](docs/CONCEPTUAL_RESERVE.md)
- [`docs/GLOSSARY.md`](docs/GLOSSARY.md)

Coding-agent guidance:

- [`AGENTS.md`](AGENTS.md)
- [`archive/CODEX_HANDOFF_INITIAL.md`](archive/CODEX_HANDOFF_INITIAL.md) — completed initial implementation brief.

Archived application/assessment context is non-evidential.

## Continuation

The next sequence is intentionally narrow:

```text
independent source
-> provenance review
-> minimum source-specific adapter
-> frozen manifest
-> independent attestation
-> one frozen evidence run
-> retain positive, null, or invalid result
```

Do not build a generic plugin framework before the independent source exists. Do not change the scientific contract merely to make integration convenient. If the source requires a scientifically material change, version the experiment rather than silently preserving the v0.1 identity.

See [`CONTINUATION.md`](CONTINUATION.md) for the full handoff.

🐟
