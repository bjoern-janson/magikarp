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
- [`CODEX_HANDOFF.md`](CODEX_HANDOFF.md) — current routing file;
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
