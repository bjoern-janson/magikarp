# MAGIKARP v0.1 — Continuation Handoff

Start here if you are taking over the project after the 2026-08-08 engineering freeze.

The project does **not** need more theory or more built-in benchmark polish before the next gate. The immediate objective is to obtain a genuinely independent evidence source for the already-frozen v0.1 question.

## 1. Current objective

Do not ask whether the built-in synthetic loop can manufacture a positive signal. It can, and it is intentionally barred from scientific authority.

The next question is:

> **Does the frozen prospective diagnostic measure add held-out predictive information when failure/recovery structure comes from a source that did not inherit the built-in target-manufacturing mechanism?**

The next deliverable is therefore a qualifying `L2` or `L3` generator/source plus its provenance record and independent attestation path.

## 2. Read order for an integration team

An integration team may inspect the full repository. Read in this order:

1. [`PROJECT_FREEZE.md`](PROJECT_FREEZE.md)
2. [`docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md`](docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md)
3. [`EVIDENCE-RUN-PROTOCOL-v0.1.md`](EVIDENCE-RUN-PROTOCOL-v0.1.md)
4. [`docs/V0_1_EXECUTION_PREFLIGHT.md`](docs/V0_1_EXECUTION_PREFLIGHT.md)
5. [`docs/REVISION_CONTROLLER_CLARIFICATION.md`](docs/REVISION_CONTROLLER_CLARIFICATION.md)
6. [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md)
7. `src/magikarp/`
8. `tests/`

Treat `CODEX_HANDOFF.md` as historical implementation context. The first synthetic implementation target described there is complete.

## 3. Read boundary for an independent generator team

A team intended to qualify at `L2` should **not** begin by reading the implementation.

Use [`docs/INDEPENDENT_GENERATOR_BRIEF-v0.1.md`](docs/INDEPENDENT_GENERATOR_BRIEF-v0.1.md) as the handoff surface.

To preserve the strongest plausible independence claim, generator authors should not inspect:

- `src/magikarp/`;
- tests encoding the built-in mechanism;
- built-in generator equations or signal prototypes;
- prior outcome-bearing runs;
- failed evidence runs;
- internal target-tuning history.

Public knowledge of the frozen benchmark ontology and supplied action classes is allowed; copying the built-in signal/recovery mechanism is not.

If this boundary has already been crossed, disclose it. Do not launder an `L1` source into `L2` through naming or review language.

## 4. Required independent-source properties

A candidate source must provide enough structure to instantiate the frozen failure-depth distinction:

- parameter failure — the existing representation/model class remains sufficient and a local revision can recover;
- model failure — represented variables remain sufficient but a deeper relationship/model revision is required;
- interface failure — the old interface is insufficient and the benchmark-supplied interface-expansion class is required.

The source must allow these minimum sufficient depths to be established by construction, oracle, exhaustive adjudication, or another preregistered independent method.

The source must also expose pre-adaptation evidence from which failure depth is identifiable in expectation without leaking experimenter labels or later outcomes.

It does **not** need to implement representation invention. v0.1 supplies the revision classes.

## 5. Provenance before integration

Before an integration team modifies MAGIKARP to execute the candidate source, freeze a generator provenance record covering at least:

- structural family identity and version;
- source hash or immutable source locator;
- author/origin and creation time;
- derivation lineage;
- shared code and helper functions;
- shared task abstractions;
- shared latent failure ontology;
- shared parameterization/signal construction;
- shared labeling logic;
- shared revision-controller assumptions;
- shared evaluation/outcome assumptions;
- known dependencies;
- access to benchmark implementation, prior manifests, prior outcomes, and failed runs;
- proposed independence level and limitations.

Use the exact requirements in `EVIDENCE-RUN-PROTOCOL-v0.1.md`; do not substitute this summary for the protocol.

## 6. Only then build the minimum adapter

The current runner is intentionally welded to the built-in generator. Once a real independent source exists, introduce the smallest seam required to execute that source while preserving the frozen scientific interfaces.

Preferred rule:

```text
independent source first
minimum adapter second
```

Avoid:

```text
generic plugin framework first
source forced into framework later
```

The adapter must not silently manufacture the relationship under test. In particular, audit whether the mapping into diagnostic observations encodes the failure label or reproduces the built-in three-signal prototype under another name.

Any source-specific nuisance surfaces must be added to the leakage audit before evidence interpretation.

## 7. Adapter acceptance criteria

Before a candidate adapter can support an evidence run, verify:

- the generator is not a built-in derivative;
- structural-family identity is distinct from within-family buckets;
- diagnostic inputs are label-free;
- diagnostic and adaptation phases remain temporally and materially separated;
- all three minimum sufficient revision depths are independently established;
- interface failure is impossible under the old interface according to the frozen criterion;
- nuisance-only leakage is audited for the new source's actual surfaces;
- `Q`, `E`, `A`, and `SD` remain frozen and prospective;
- `Y_adapt` remains decomposed;
- controller, analysis, and source hashes are bound in the manifest;
- the bootstrap/held-out unit reflects the highest actual independence level available;
- no outcome was inspected while choosing seeds, exclusions, endpoints, or stopping rules.

If satisfying the source requires changing a scientific definition rather than an execution seam, stop and apply the versioning rule instead of silently preserving the `v0.1` label.

## 8. Attestation

A qualifying evidence run requires a separate pre-outcome attestation with exact hash bindings and `independent_verified` status.

Software can verify schema and hash consistency. It cannot establish social/control independence or immutable publication of the attestation record. Those facts require an external party or process.

Self-attestation and same-control process attestation do not qualify.

## 9. Evidence run sequence

For one evidence-intended run:

```text
1. freeze candidate generator/source
2. finalize provenance comparison
3. commit the minimum adapter and frozen config
4. register planned run IDs and seeds
5. build the deterministic manifest
6. independently recompute/review hashes
7. publish the independent attestation before outcomes
8. execute once
9. run validity gates before primary analysis
10. classify as valid_positive, valid_negative, or benchmark_invalid
11. retain every attempted run
```

A valid null stays. An invalid run licenses no empirical claim. A software defect does not authorize silent replacement of the failed artifact.

## 10. What not to do next

Do not:

- expand the conceptual ontology;
- add CRE or representation invention to v0.1;
- tune the built-in generator toward a desired effect;
- create new primary outcomes after seeing results;
- replace the Brier-based primary `SD` because another metric looks better;
- promote per-failure heterogeneity into a new top-level result class;
- treat generator buckets as structural independence;
- treat reproducibility as independence;
- write a generic external-source framework before a real source exists;
- describe a positive as causal or as evidence for open-ended representation invention.

## 11. Decision tree after the first qualifying run

### `valid_positive`

Retain the frozen bounded predictive claim. Then consider replication across another independent family before causal intervention work.

### `valid_negative`

Retain the null as evidence. Do not tune it away. Candidate explanations—weak diagnostic construct, controller dominance, taxonomy transfer failure, insufficient source diversity, or another variable—require a separately frozen follow-up experiment.

### `benchmark_invalid`

Make no empirical MAGIKARP claim. Localize the failed validity/provenance/execution condition. Engineering repair may restore frozen semantics; scientifically material repair requires a new experimental version.

## 12. Handoff completion criterion

A successor team has successfully inherited the project when it can state all of the following without ambiguity:

- what v0.1 tests;
- what it does not test;
- why the built-in generator is non-evidence-bearing;
- what would qualify an independent source;
- why the current runner cannot yet execute that source unchanged;
- what the minimum adapter is allowed to change;
- what is frozen before outcomes;
- what positive, null, and invalid runs authorize;
- which changes require a new scientific version.

If those answers are stable, continue with evidence acquisition rather than theory expansion.
