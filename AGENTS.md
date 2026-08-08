# AGENTS.md

MAGIKARP v0.1 is at an **engineering freeze**. Coding agents should preserve the frozen scientific contract and optimize for experimental discriminability, not theoretical expansion.

## Start here

Before making project changes, read:

1. [`PROJECT_FREEZE.md`](PROJECT_FREEZE.md)
2. [`CONTINUATION.md`](CONTINUATION.md)
3. [`docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md`](docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md)
4. [`EVIDENCE-RUN-PROTOCOL-v0.1.md`](EVIDENCE-RUN-PROTOCOL-v0.1.md)
5. [`docs/V0_1_EXECUTION_PREFLIGHT.md`](docs/V0_1_EXECUTION_PREFLIGHT.md)

The completed first-implementation Codex brief is preserved at [`archive/CODEX_HANDOFF_INITIAL.md`](archive/CODEX_HANDOFF_INITIAL.md) for historical context only.

## Current project boundary

The built-in deterministic loop under `src/magikarp` is an engineering reference. It is fixed at `L0`, and no metadata, wrapper, seed variation, or attestation can make it evidence-bearing.

The next scientific step is **not** more built-in benchmark polish. It is a genuinely independent `L2` or `L3` evidence source.

Do not build a generic external-generator framework before a real independent source exists. Once a source is frozen, implement only the minimum adapter required to execute it without changing the frozen scientific meaning.

## Non-negotiable v0.1 scope

The load-bearing objects remain only:

- `Q` — present competence;
- `SD` — prospective pre-adaptation failure-depth diagnosis;
- `F` — experimenter-controlled failure depth;
- `Y_adapt` — decomposed held-out adaptation outcomes.

Primary comparison:

```text
M0: R_c ~ Q + A + E
M1: R_c ~ Q + A + E + SD
```

The claim is predictive, not causal.

Do **not** make representation invention, CRE, escape topology, authority capture, transformation topology, Gyarados failure, CARP, or recursive improvement required v0.1 implementation objects.

Selection among the supplied parameter/model/interface revision classes is not representation invention.

## Empirical separation to preserve

Keep these objects distinct in code and artifacts:

```text
F -> q_SD -> D_revision -> Y_adapt
```

Do not infer diagnosis from revision choice. Do not infer diagnosis or revision choice from recovery.

`SD` must be computed before unrestricted adaptation and without later outcome information.

Keep recovery, transfer, retention, preservation, and correction cost decomposed. Do not create a universal MAGIKARP score.

## Evidence discipline

- Prediction is not causation.
- Reproducibility is not structural independence.
- Generator buckets are not structural families.
- A valid null is retained evidence.
- A failed validity/provenance/freeze condition is `benchmark_invalid`, not a negative result.
- Per-failure heterogeneity is secondary; it is not a third top-level evidence status.
- Do not rescue a null by changing definitions, endpoints, seeds, exclusions, or stopping rules after outcome inspection.

Before an evidence-bearing run, follow the exact evidence protocol, freeze the manifest, and obtain a separate independent pre-outcome attestation.

## Independent-source firewall

If a separate team is intended to author an `L2` generator, direct them to [`docs/INDEPENDENT_GENERATOR_BRIEF-v0.1.md`](docs/INDEPENDENT_GENERATOR_BRIEF-v0.1.md) rather than the implementation.

Do not unnecessarily expose generator authors to:

- `src/magikarp/`;
- built-in signal prototypes;
- built-in outcome equations;
- tests encoding those mechanisms;
- prior evidence outcomes or failed evidence runs.

If access has occurred, disclose it rather than overstating independence.

## Validation after implementation changes

Run:

```text
python -m unittest discover -s tests -v
magikarp smoke --output results/smoke --overwrite
```

A healthy smoke run remains `engineering_only`. Passing gates validates the engineering loop, not the scientific hypothesis.

If a change alters what is generated, measured, excluded, grouped, stopped, analyzed, or claimed, apply the scientific-versioning rule in `EVIDENCE-RUN-PROTOCOL-v0.1.md` rather than silently preserving the v0.1 identity.
