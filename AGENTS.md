# AGENTS.md

This repository is preparing **MAGIKARP v0.1**, a deliberately minimal benchmark. Coding agents should optimize for experimental discriminability, not theoretical expansion.

Before any evidence-bearing run, follow [`docs/V0_1_EXECUTION_PREFLIGHT.md`](docs/V0_1_EXECUTION_PREFLIGHT.md). Smoke runs may debug implementation, but no result should be interpreted until the preflight validity gates pass and the run manifest is frozen.

## Non-negotiable scope

The load-bearing v0.1 objects are only:

- `Q`: present competence.
- `SD`: pre-adaptation representation self-diagnosis.
- `F`: experimenter-controlled failure depth.
- `Y_adapt`: held-out adaptation outcomes.

Do **not** make escape topology, authority capture, provenance, transformation topology, Gyarados failure, or CARP required implementation objects unless a concrete benchmark need forces them in.

The post-freeze revision-controller clarification may require recording `q_SD`, revision traces, and selected revision depth, but these are implementation/analysis surfaces rather than new load-bearing v0.1 ontology.

## Primary hypothesis

Adding pre-adaptation `SD` should improve held-out prediction of later adaptation outcomes beyond strong baselines:

- present competence,
- ordinary error sensitivity,
- standard adaptation metrics.

Primary comparison:

- `M0: Y ~ Q + A + E`
- `M1: Y ~ Q + A + E + SD`

The primary success criterion is reproducible out-of-sample predictive gain.

## Predictor/outcome firewall

`SD` must be computed before unrestricted adaptation and without access to outcome information.

Diagnostic probes and held-out adaptation tasks must not leak via:

- shared templates,
- near-duplicate instances,
- generator fingerprints,
- hidden labels,
- memorized failure signatures,
- adaptation trajectories used during SD scoring.

## Failure classes

Ground truth:

- `parameter`
- `model`
- `interface`

The benchmark should make the correct revision depth identifiable by construction.

## Outcome handling

Keep the adaptation vector decomposed:

- recovery,
- transfer,
- retention,
- preservation,
- correction/revision cost.

Do not invent a universal scalar MAGIKARP score in v0.1.

## Engineering priorities

1. Deterministic seeds and reproducible dataset generation.
2. Explicit train/diagnostic/adaptation/transfer splits.
3. Strong assertions against leakage.
4. Small synthetic environments with known ground-truth failure type.
5. Baselines that can fail in both directions:
   - rigid/shallow updater,
   - hyperplastic/deep updater,
   - sensible adaptive baseline.
6. Machine-readable run artifacts.
7. Tests for all benchmark invariants before large experiments.
8. Frozen evidence-run manifest and explicit run status.

## Scientific discipline

- Prediction is not causation.
- A positive correlation is not enough.
- In-sample improvement is not enough.
- A significant coefficient is not enough.
- If SD adds no held-out predictive value, report the negative result.
- Do not rescue a null result by expanding definitions.
- Avoid explanation after the fact unless it produces a new discriminating test.
- A failed benchmark-validity gate means `benchmark_invalid`, not evidence against MAGIKARP.

## CARP

CARP is a candidate intervention, not the definition of MAGIKARP success. Do not bake CARP compliance into labels or scoring.

## Preferred first milestone

A tiny end-to-end benchmark where:

1. two or more agent classes achieve similar baseline `Q`,
2. diagnostic probes yield distinct `SD`,
3. held-out failures are introduced,
4. `SD` is tested prospectively against later adaptation trajectories,
5. a no-SD baseline model is compared against an SD-augmented model,
6. diagnostic output, revision choice, and adaptation outcome remain separately recorded,
7. benchmark-validity gates are machine-readable,
8. all results are reproducible from a single command.
