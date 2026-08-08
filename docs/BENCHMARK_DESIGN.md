# Minimal Synthetic Benchmark Design

This document proposes a concrete v0.1 environment while preserving the frozen empirical claim.

## Design objective

Create situations where three failure depths are known by construction and where different adaptation depths have visibly different costs.

The environment should be simple enough that the experimenter can prove which failure depth is correct.

## Candidate environment: latent-context decision task

Each episode contains observable features and a required action.

Start with a representation under which all training examples are solvable.

At test time, introduce one of three controlled changes.

### Parameter failure

The represented variables and model form remain sufficient, but a local mapping/value changes.

Example:

- reward weight for an already represented feature changes,
- transition probability changes while state variables remain adequate.

Correct response: update a parameter or local estimate.

Unnecessary model/interface restructuring should incur cost.

### Model failure

All necessary variables are observable, but the assumed relationship among them changes.

Example:

- outcome was additive in two features during training,
- held-out phase makes the interaction multiplicative or conditional.

Correct response: revise model structure/relationship.

Parameter-only adaptation should exhibit systematic residual error.

### Interface failure

Two states previously equivalent under the observation interface become behaviorally distinct.

Training:

\[
O(s_a)=O(s_b)
\]

while both require the same action.

Perturbation:

\[
L(s_a)\neq L(s_b)
\]

The environment must provide an independent consequence/error channel sufficient to diagnose that the existing representation is inadequate. Do not require impossible inference from information that the interface literally removes.

Correct response: request/add/reveal a new feature, sensor, partition, or representation dimension.

Parameter/model tuning over the old interface cannot solve the task.

## Important identifiability rule

Interface diagnosis is not interface invention.

v0.1 should test whether the system can recognize that the current representation is insufficient and take a benchmark-defined interface-expansion action.

Do not require free-form invention of a missing sensor in the first benchmark.

## Agent families

### Local updater

- can tune parameters efficiently,
- can revise model only reluctantly,
- cannot or rarely escalates to interface change.

Expected weakness: under-revision on deep failures.

### Hyperplastic updater

- readily escalates to deeper revisions after errors,
- can solve interface failures,
- pays large unnecessary cost on parameter failures.

Expected weakness: over-revision.

### Depth-aware updater

- uses diagnostics to choose parameter/model/interface revision,
- incurs costs for unnecessary depth.

Expected strength: higher failure-depth discrimination and lower correction cost.

### Optional matched heuristic baseline

A policy that adapts by fixed thresholds without an explicit SD output.

Useful to test whether SD adds information beyond generic responsiveness.

## Diagnostic phase

Before unrestricted adaptation:

1. expose a short probe sequence,
2. provide observations, predictions, consequences, and allowed diagnostic signals,
3. prevent the agent from performing its full corrective action,
4. ask for a distribution over failure depths,
5. compute SD from held-out diagnostic probes.

The probe should contain enough information to identify failure depth in expectation.

## Adaptation phase

Use a different held-out perturbation.

Allow the agent to:

- update parameters,
- revise model structure,
- request/activate interface expansion.

Charge explicit costs:

\[
c_p < c_m < c_i
\]

unless an alternative cost structure is justified.

The point is not that deeper revisions are always worse; it is that unnecessary deep changes should be more disruptive than necessary local changes.

## Outcome vector

Track at least:

### Recovery
Post-adaptation task performance.

### Transfer
Performance on structurally related but unseen examples.

### Retention
Whether the correction survives later episodes or delayed evaluation.

### Preservation
Performance on examples whose previous solution remains valid.

### Correction cost
Could include:

- number of update steps,
- total revision cost,
- unnecessary depth escalation,
- data required,
- compute steps,
- regressions introduced.

## Data splits

Use separate seeds/generators for:

- baseline training,
- SD diagnostic probes,
- held-out adaptation,
- transfer.

Prefer holding out entire parameter ranges or rule families, not only individual samples.

## First falsification test

Fit predictive models across many runs/agents/checkpoints:

```text
M0: Y ~ Q + A + E
M1: Y ~ Q + A + E + SD
```

If M1 does not improve held-out prediction, report the negative result.

## Later extensions, not v0.1 requirements

- hidden common-mode correction channels,
- changing observation operators,
- multi-agent critics,
- optimization trajectories for Gyarados failure,
- LLM agents,
- open-ended interface invention.
