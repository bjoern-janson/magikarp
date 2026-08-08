# MAGIKARP v0.1 — Project Freeze

**Freeze package date:** 2026-08-08  
**Snapshot base commit:** `57d3c526ee930a525f0dff39c162aa2c68863abb`  
**Scientific benchmark:** `MAGIKARP-v0.1`  
**Purpose:** preserve the exact research and engineering boundary reached before the first qualifying evidence source exists.

This file freezes project state. It does **not** amend the benchmark contract, create a new scientific version, or make any run evidence-bearing.

## 1. Frozen scientific state

The v0.1 question remains:

> **Does prospective failure-depth diagnosis add held-out predictive information about later recovery beyond present competence, ordinary error sensitivity, and the frozen standard-adaptation control?**

Primary comparison:

```text
M0: R_c ~ Q + A + E
M1: R_c ~ Q + A + E + SD
```

Load-bearing objects remain only:

- `Q` — present competence;
- `SD` — prospective failure-depth diagnosis measured before unrestricted adaptation;
- `F` — experimenter-controlled failure depth (`parameter`, `model`, `interface`);
- `Y_adapt` — decomposed held-out adaptation trajectory.

The primary claim is predictive, not causal.

## 2. Frozen claim boundary

A positive v0.1 result may support only the frozen predictive claim under the demonstrated task and independence scope.

It does **not** establish:

- causal efficacy of `SD`;
- representation invention;
- generation of an unsupplied missing distinction;
- Controlled Representational Escape;
- open-ended correctability;
- recursive improvement capacity;
- general intelligence.

The interface-expansion action in v0.1 is supplied by the benchmark. Selection among supplied revisions is not invention.

## 3. Current executable state

The repository contains a deterministic engineering loop with:

- oracle-validated parameter/model/interface failure depths;
- a label-free diagnostic API;
- crossed diagnostic skill and revision-controller behavior;
- prospective raw `q_SD` and frozen Brier-based `SD`;
- decomposed recovery, transfer, retention, preservation, and correction cost;
- complete revision traces;
- validity gates A-F;
- agent-block × generator-bucket held-out analysis;
- source-bound manifests;
- fail-closed evidence eligibility;
- separate attestation records;
- tests covering the major benchmark and evidence-boundary invariants.

The built-in generator is fixed at `L0`. Its `generator_family` labels are namespaced buckets over one generating mechanism, not structural families.

Therefore:

```text
built-in smoke -> engineering_only
built-in manifest run -> engineering_only
```

No built-in run may be relabeled as evidence by changing metadata or supplying an attestation.

## 4. Evidence state at freeze

At this freeze:

- qualifying `L2` generators: **none**;
- qualifying `L3` generators: **none**;
- evidence-bearing v0.1 runs: **none**;
- empirical positive claim: **none**;
- empirical negative claim: **none**.

The repository has an evidence-eligibility schema and validator, but the executable runner is intentionally still bound to the built-in generator. A genuine `L2`/`L3` source cannot yet be executed through the current CLI without a source/adapter change.

This is the exact implementation frontier, not an accidental omission.

## 5. Authority map

When documents differ in scope, use this map rather than treating every file as equally normative:

1. [`docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md`](docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md) — scientific question, load-bearing variables, claim scope, and primary comparison.
2. [`EVIDENCE-RUN-PROTOCOL-v0.1.md`](EVIDENCE-RUN-PROTOCOL-v0.1.md) — evidence eligibility, structural independence, provenance, attestation, freeze conditions, scientific versioning, and outcome authority.
3. [`docs/V0_1_EXECUTION_PREFLIGHT.md`](docs/V0_1_EXECUTION_PREFLIGHT.md) — operational metric definitions, validity gates, execution sequence, and result artifacts.
4. [`docs/REVISION_CONTROLLER_CLARIFICATION.md`](docs/REVISION_CONTROLLER_CLARIFICATION.md) — implementation-facing separation of diagnosis, revision selection, and outcome; it does not amend the primary hypothesis.
5. Implementation docs, handoffs, conceptual files, archived examples, and this freeze package — explanatory or operational guidance only.

If an older explanatory file conflicts with the frozen evidence protocol on evidence status or outcome authority, the evidence protocol governs that question.

## 6. Known limitations intentionally preserved

The following are known at freeze and are **not** reasons to keep polishing the built-in benchmark:

- the depth-aware supplied controller directly consumes `q_SD`, so a built-in positive can be manufactured by the supplied correction architecture;
- `M0` freezes `Q + A + E` and does not separately encode controller identity;
- built-in `generator_family` buckets are not structural holdouts;
- the default bootstrap unit can exercise bucket-level uncertainty but does not create structural independence;
- the current external-evidence path exists in schema/eligibility space, not yet as a runnable generator adapter;
- an independent source may introduce nuisance/leakage surfaces not present in the built-in generator and must be audited on its own terms.

These limitations constrain interpretation. They do not license outcome-driven changes to v0.1.

## 7. Engineering stopping point

Do not spend additional engineering budget making the built-in generator more realistic, more generic, or more publishable merely because the code can be improved.

The built-in implementation has one remaining job: remain a stable engineering reference and regression target.

The next scarce resource goes to **independent evidence provenance**.

## 8. Next authorized project transition

The next project sequence is:

```text
independent source
-> provenance review
-> minimum execution adapter
-> freeze manifest
-> independent attestation
-> one frozen evidence run
-> retain positive, null, or invalid result
```

The independent source comes **before** adapter generalization. Do not build a generic generator plugin framework in anticipation of unknown evidence sources.

Continue from [`CONTINUATION.md`](CONTINUATION.md).

## 9. Verification of the inherited engineering state

A team inheriting the repository should first reproduce the engineering reference:

```text
python -m pip install -e .
python -m unittest discover -s tests -v
magikarp smoke --output results/smoke
```

A healthy reference smoke run must remain non-evidence-bearing. Passing smoke gates validates the engineering loop, not the scientific hypothesis.

## 10. Freeze rule

Any future change that alters what is generated, measured, excluded, grouped, stopped, analyzed, or claimed must be evaluated under the scientific-versioning rules in `EVIDENCE-RUN-PROTOCOL-v0.1.md`.

Engineering changes may restore already-frozen semantics. Scientifically material changes require a new experimental version. Outcome-driven repair under the same v0.1 identity is forbidden.
