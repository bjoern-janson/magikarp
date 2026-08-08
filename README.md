# MAGIKARP

**MAGIKARP studies whether sensitivity to the limits of a system's own representation contains independent predictive information about future adaptation when those limits are crossed.**

This repository is frozen at the point where the conceptual work yields a minimal empirical wager. The next progress should come from benchmark results, implementation pressure, or failed predictions—not additional ontology.

## Research stack

### Representational Governance
**Problem class:** How do representations acquire, retain, relinquish, and revise authority under changing conditions?

### MAGIKARP
**Measurement target:** Does a system preserve justified routes for changing its representations, and specifically can pre-adaptation representation self-diagnosis predict later adaptive trajectory?

### CARP
**Candidate operational discipline:** A controlled adaptation reasoning protocol that may improve the measured property. CARP is not the definition of success and must itself be tested.

## Frozen v0.1 empirical question

> **Does pre-adaptation sensitivity to representation limits predict held-out adaptation outcomes beyond current competence, ordinary error sensitivity, and standard adaptation metrics?**

The primary claim is predictive, not causal.

\[
SD_{\text{diagnostic}} \rightarrow \text{incremental held-out prediction of }Y_{\text{adapt}}
\]

The stronger causal statement is explicitly deferred to a later intervention stage.

The executable currently included here is an **engineering instrument**, not a
scientifically ready evidence source. Its `generator_family` values are
namespaced seed/index buckets produced by one synthetic latent-context
generator. They are useful for testing aggregation and holdout machinery, but
they are not structurally distinct or external failure families.

## Minimal ontology budget

v0.1 should require only four load-bearing objects:

- **Q** — present competence before perturbation.
- **SD** — diagnostic representation self-diagnosis, measured before unrestricted adaptation.
- **F** — experimenter-controlled ground-truth failure depth: parameter, model, or interface.
- **Y_adapt** — later held-out adaptation trajectory.

A useful decomposed outcome vector is:

\[
Y_{\text{adapt}}=(R_c,T,R,P,C)
\]

where:

- **R_c** — recovery,
- **T** — transfer,
- **R** — retention,
- **P** — preservation of still-valid structure,
- **C** — unnecessary correction/revision cost.

Do not create a single universal `MAGIKARP_score` in v0.1.

## Epistemic ladder

Keep these claims separate:

\[
\text{existence} \neq \text{prediction} \neq \text{causation} \neq \text{intervention efficacy}
\]

The staged research ladder is:

1. **v0.1:** Does SD add held-out predictive information?
2. **v0.2:** Does SD predict efficient and targeted revision?
3. **v0.3:** Does an intervention that raises SD improve adaptation?
4. **v0.4:** Does CARP reliably produce such an intervention effect?

## Primary statistical comparison

Baseline model:

\[
M_0: Y \sim Q + A + E
\]

Expanded model:

\[
M_1: Y \sim Q + A + E + SD
\]

where **A** denotes strong standard adaptation baselines and **E** denotes ordinary/raw error sensitivity.

The primary success criterion is **reproducible out-of-sample predictive gain** from adding SD—not an in-sample correlation, a significant coefficient, or a cherry-picked pair of systems.

The null is explicit:

\[
H_0: SD \text{ adds no reliable held-out predictive value beyond existing measures.}
\]

If the null survives strong testing, MAGIKARP contracts rather than expanding definitions.

## Failure-depth discrimination

The first benchmark should use controlled failures:

\[
F \in \{F_p,F_m,F_i\}
\]

- **F_p — parameter failure:** the representation is adequate; a local value/parameter is wrong.
- **F_m — model failure:** the representation exposes the relevant variables, but the relationship/mechanism among them is wrong.
- **F_i — interface failure:** the representation itself collapses a distinction required for success.

The target is not maximum change. It is proportional revision:

\[
\text{revision depth} \approx \text{failure depth}
\]

Two symmetric pathologies should fail:

- **rigidity / under-revision:** deep failure receives a shallow patch;
- **hyperplasticity / over-revision:** local failure triggers unnecessary restructuring.

A post-freeze clarification separates the diagnostic output, the revision depth actually selected, and the eventual adaptation outcome so these failure transitions are not collapsed into one variable.

## Temporal and data firewall

The benchmark must enforce:

\[
\text{diagnostic probes} \rightarrow SD \rightarrow \text{held-out perturbations} \rightarrow Y_{\text{adapt}}
\]

No information from the later adaptation phase may leak into the construction of SD. Diagnostic and adaptation datasets should also avoid leakage through shared templates, near-duplicate latent structures, hidden labels, or generator artifacts.

Prefer stronger generalization tests over random-instance splits:

1. held-out failure instances,
2. held-out failure families,
3. later: held-out architectures/checkpoints/domains.

## Gyarados failure — secondary hypothesis

Keep this as a memorable adversarial hypothesis, not as a load-bearing v0.1 construct:

\[
Q(R) \uparrow \quad \land \quad SD(R) \downarrow
\]

A system can become increasingly successful inside its current validity region while becoming worse at detecting when that region has ended.

The v0.1 benchmark should first establish whether SD is measurable and independently predictive. Only then should optimization-induced loss of SD become a primary target.

## Executable v0.1 loop

The repository now contains a deterministic synthetic implementation of the
frozen v0.1 contract. It includes:

- oracle-validated parameter, model, and interface failure depths;
- crossed diagnostic skill and revision-controller behavior;
- distinct diagnostic, adaptation, and transfer seed/identifier namespaces
  over one synthetic generator;
- prospective `q_SD`, decomposed outcomes, and complete revision traces;
- machine-readable validity gates A-F;
- agent × generator-family × failure aggregation;
- two-way identifier-level held-out `M0`/`M1` prediction;
- source-bound manifest v3, structural-family provenance, independent
  attestation, and fail-closed eligibility infrastructure.

Quick start:

```text
python -m pip install -e .
python -m unittest discover -s tests -v
magikarp smoke --output results/smoke
```

A smoke run with passing validity gates returns `engineering_only`; a failed
gate returns `benchmark_invalid`. Passing proves that the operational loop and
benchmark invariants execute, not evidence for or against the v0.1 hypothesis.

The built-in generator also remains `engineering_only` when exercised through
the manifest `freeze`/`run` workflow. A scientifically interpretable evidence
run requires structurally distinct or external generator families and an
independent pre-outcome manifest attestation; neither is supplied here yet.

See [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) for the environment,
analysis unit, anti-confounding controls, artifacts, and frozen evidence-run
workflow.

## Repository map

- [`EVIDENCE-RUN-PROTOCOL-v0.1.md`](EVIDENCE-RUN-PROTOCOL-v0.1.md) — normative provenance, independence, freeze, attestation, and outcome-authority requirements for evidence-bearing v0.1 runs.
- [`docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md`](docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md) — frozen preregisterable benchmark contract.
- [`docs/BENCHMARK_DESIGN.md`](docs/BENCHMARK_DESIGN.md) — concrete minimal synthetic benchmark design.
- [`docs/MEASUREMENT_PLAN.md`](docs/MEASUREMENT_PLAN.md) — predictor/outcome separation, baselines, evaluation, and leakage controls.
- [`docs/REVISION_CONTROLLER_CLARIFICATION.md`](docs/REVISION_CONTROLLER_CLARIFICATION.md) — post-freeze clarification separating diagnosis, revision selection, and execution without amending the v0.1 hypothesis.
- [`docs/V0_1_EXECUTION_PREFLIGHT.md`](docs/V0_1_EXECUTION_PREFLIGHT.md) — pre-outcome execution freeze: operational metrics, validity gates, run manifest, artifact schema, and result-status rules.
- [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) — executable environment, agents, analysis, validity gates, CLI, and evidence boundary.
- [`docs/REPRESENTATIONAL_GOVERNANCE.md`](docs/REPRESENTATIONAL_GOVERNANCE.md) — public-facing umbrella problem.
- [`docs/CARP.md`](docs/CARP.md) — frozen Controlled Adaptation Reasoning Protocol and its role.
- [`docs/CONCEPTUAL_LINEAGE.md`](docs/CONCEPTUAL_LINEAGE.md) — how the research narrowed to the current wager.
- [`docs/CONCEPTUAL_RESERVE.md`](docs/CONCEPTUAL_RESERVE.md) — non-load-bearing concepts retained for explanation only.
- [`docs/GLOSSARY.md`](docs/GLOSSARY.md) — stable terminology.
- [`CODEX_HANDOFF.md`](CODEX_HANDOFF.md) — implementation brief for the first benchmark.
- [`AGENTS.md`](AGENTS.md) — repo-level instructions for coding agents.
- [`archive/APPLICATION_LENSES.md`](archive/APPLICATION_LENSES.md) — seven-sins and music-taxonomy lenses, retained as illustrative applications rather than evidence.
- [`archive/EXTERNAL_ASSESSMENT_NOTES.md`](archive/EXTERNAL_ASSESSMENT_NOTES.md) — informal external assessment supplied during development; not scientific evidence.

## Current status

**Conceptual stack: frozen.**  
**v0.1 hypothesis: frozen.**  
**Execution preflight: frozen before evidence-bearing implementation.**  
**Implementation: executable deterministic synthetic loop.**

**Engineering smoke: operational; never evidence-bearing.**

**Built-in generator: infrastructure-only; its family labels are not structural holdouts.**

**Evidence protocol and eligibility infrastructure: ready.**

**Qualifying evidence-bearing generators: none.**

The next meaningful scientific output should be an independently frozen,
valid evidence run—not another expansion of the ontology.

🐟
