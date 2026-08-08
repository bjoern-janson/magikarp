# Codex Handoff — MAGIKARP v0.1

## Goal

Build the smallest benchmark capable of falsifying the claim:

> Pre-adaptation representation self-diagnosis adds held-out predictive information about later adaptation beyond current competence, ordinary error sensitivity, and standard adaptation metrics.

Do not implement the entire conceptual framework.

Before an evidence-bearing run, follow [`docs/V0_1_EXECUTION_PREFLIGHT.md`](docs/V0_1_EXECUTION_PREFLIGHT.md). It freezes the remaining execution choices, validity gates, revision-trace requirements, and result-status vocabulary without changing the v0.1 hypothesis.

## First implementation target

Create a synthetic task family with three controlled failure depths:

1. **Parameter failure** — existing variables and structure are sufficient; one local parameter/value becomes wrong.
2. **Model failure** — variables remain observable, but the causal/transition relationship becomes wrong.
3. **Interface failure** — a previously collapsed distinction becomes necessary; solving the task requires changing the representation or observation interface.

The experimenter must know ground-truth `F`.

## Suggested minimal agent families

Use deliberately simple agents before LLMs or large neural systems:

- **Rigid/local updater** — prefers parameter changes and under-escalates.
- **Hyperplastic updater** — escalates too readily to model/interface changes.
- **Depth-aware updater** — can select among parameter/model/interface revisions.
- Optional: matched random or heuristic controls.

The first result should come from a setting where the causal structure is transparent enough to debug.

## Experimental phases

### Phase A — Baseline
Train/evaluate agents until current competence `Q` is matched as closely as practical.

### Phase B — Diagnostic probes
Expose agents to controlled evidence of parameter/model/interface failures.

Do **not** permit unrestricted recovery.

Record a diagnostic distribution such as:

```text
P(parameter), P(model), P(interface)
```

Use these data to compute `SD`.

### Phase C — Held-out perturbation
Introduce new perturbations from held-out instances or preferably held-out failure families.

Now allow adaptation.

### Phase D — Outcome trajectory
Record:

- recovery,
- transfer,
- retention,
- preservation,
- revision cost.

Also preserve the complete revision trace so diagnostic quality, revision selection, and execution success remain separable.

## Required comparisons

Baseline predictor:

```text
M0: Y ~ Q + A + E
```

Expanded predictor:

```text
M1: Y ~ Q + A + E + SD
```

Evaluate out of sample.

Start with straightforward predictive models and cross-validation before information-theoretic estimation.

## Guardrails

- Diagnostic and adaptation tasks must be generated independently enough to prevent benchmark recognition.
- Keep raw diagnostic outputs.
- Keep raw adaptation trajectories.
- Separate measurement code from agent adaptation code.
- Record seeds and config hashes.
- Preserve negative results.
- Do not collapse outcomes into one score prematurely.
- Do not use future outcome information to tune the SD definition.
- Do not interpret a result until the execution-preflight validity gates pass.

## Minimal repo structure Codex can create

```text
src/magikarp/
  envs/
  agents/
  diagnostics/
  metrics/
  analysis/
tests/
configs/
scripts/
results/        # ignored except compact summaries
```

Prefer a simple Python stack unless another language offers a clear experimental advantage.

## Definition of done for first bench

A single command should:

1. generate deterministic train/diagnostic/held-out splits,
2. run all agent families,
3. compute `Q`, `E`, baseline adaptation measures, and pre-adaptation `SD`,
4. run held-out adaptation trials,
5. emit decomposed `Y_adapt`,
6. preserve revision traces and selected revision depth,
7. fit/evaluate `M0` and `M1`,
8. report held-out predictive delta with uncertainty,
9. save configs and raw-enough artifacts to reproduce the result,
10. emit the benchmark-validity gates and one explicit run status.

## What not to do yet

- Do not build a universal JT score.
- Do not implement the seven-sins analogy.
- Do not implement music taxonomy.
- Do not claim causation.
- Do not implement CARP as the first experimental manipulation.
- Do not optimize for a publishable benchmark before proving the signal exists.
- Do not introduce large models until the toy environment is understood.

## Next scientific decision

After the first result:

- If `M1 <= M0` out of sample: contract or redefine only if a specific measurement failure is demonstrated.
- If `M1 > M0` reproducibly: strengthen holdouts, test revision efficiency, then consider causal interventions.
