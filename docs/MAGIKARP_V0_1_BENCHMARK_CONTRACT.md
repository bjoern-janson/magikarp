# MAGIKARP v0.1 — Frozen Benchmark Contract

## 1. Status

This document is the frozen empirical contract for the first MAGIKARP benchmark.

Changes should be driven by:

- a demonstrated identifiability problem,
- implementation impossibility,
- data leakage,
- a failed prediction that localizes a flaw in the contract,
- or an explicit preregistration amendment recorded before inspecting the affected outcome.

Conceptual elegance alone is not a sufficient reason to alter the contract.

## 2. Research question

> **Does sensitivity to the limits of a system's own representation contain independent predictive information about future adaptation when those limits are crossed?**

Operationally:

> After controlling for present competence, ordinary error sensitivity, and strong standard adaptation metrics, does a pre-adaptation representation self-diagnosis measure improve held-out prediction of later adaptive trajectory?

## 3. Claim scope

v0.1 tests **prospective prediction**.

It does not establish:

- that SD causes adaptation,
- that SD is a universal construct,
- that CARP improves SD,
- that representational governance is a complete theory,
- that the result transfers to humans, institutions, or deployed AI systems.

Epistemic ladder:

\[
\text{existence} \neq \text{prediction} \neq \text{causation} \neq \text{intervention efficacy}
\]

## 4. Load-bearing variables

### Q — present competence

A baseline measure of performance before the representation-invalidating perturbation.

### SD — diagnostic representation self-diagnosis

A pre-adaptation predictor measuring whether the system can discriminate the likely depth of a failure.

A candidate diagnostic output is a probability distribution:

\[
p(F_p),p(F_m),p(F_i)
\]

SD may eventually include:

- failure-depth discrimination,
- calibration,
- boundary sensitivity.

The scoring rule should be fixed before adaptation outcomes are used.

### F — experimenter-controlled failure depth

\[
F \in \{F_p,F_m,F_i\}
\]

- `F_p`: parameter failure.
- `F_m`: model failure.
- `F_i`: interface failure.

F is ground truth from benchmark construction, not a latent label inferred post hoc.

### Y_adapt — held-out adaptive trajectory

Keep outcomes decomposed:

\[
Y_{\text{adapt}}=(R_c,T,R,P,C)
\]

- `R_c`: recovery.
- `T`: transfer.
- `R`: retention.
- `P`: preservation of unaffected valid structure.
- `C`: unnecessary revision/correction cost.

A preregistered primary endpoint may be selected, but the vector must remain reportable.

## 5. Failure-depth criterion

The benchmark should make an appropriate intervention depth identifiable.

Target principle:

\[
\text{revision depth} \approx \text{failure depth}
\]

Under-revision example:

\[
F_i \rightarrow \widehat{F_p}
\]

Over-revision example:

\[
F_p \rightarrow \widehat{F_i}
\]

The benchmark should reward neither rigidity nor indiscriminate plasticity.

## 6. Temporal firewall

The required sequence is:

\[
\text{diagnostic probes} \rightarrow SD \rightarrow \text{held-out perturbations} \rightarrow Y_{\text{adapt}}
\]

No later adaptation outcome may be used to construct, tune, or relabel SD.

## 7. Data firewall

Temporal ordering is insufficient if the diagnostic and adaptation phases reveal the same benchmark signature.

Prevent leakage through:

- identical templates,
- near-duplicate latent structures,
- deterministic generator artifacts,
- hidden failure-type tokens,
- repeated lexical/feature signatures,
- shared examples,
- adaptation outcomes used indirectly during SD tuning.

Prefer holdouts in increasing strength:

1. held-out instances,
2. held-out failure families,
3. held-out environment generators,
4. later: held-out architectures/checkpoints/domains.

## 8. Baseline controls

At minimum control for:

- `Q`: current competence,
- `E`: ordinary/raw error sensitivity,
- `A`: standard adaptation-relevant measures.

Possible A candidates depend on implementation but may include:

- adaptation speed,
- robustness,
- uncertainty/calibration,
- continual-learning metrics,
- learning rate or update count,
- training exposure,
- model size/compute where relevant.

The benchmark should use the strongest practical baselines available in the chosen toy domain.

## 9. Primary statistical test

Baseline:

\[
M_0:Y\sim Q+A+E
\]

Expanded:

\[
M_1:Y\sim Q+A+E+SD
\]

Primary criterion:

> Does M1 yield reproducible held-out predictive improvement over M0?

Do not substitute:

- in-sample fit,
- raw correlation,
- coefficient significance,
- a single favorable seed,
- a hand-selected agent pair.

Use repeated held-out evaluation with uncertainty estimates.

## 10. Primary hypotheses

### H1

\[
SD_{\text{diagnostic}}
\text{ adds reproducible held-out predictive information about }Y_{\text{adapt}}
\text{ beyond }Q,A,E.
\]

### H0

\[
SD
\text{ adds no reproducible held-out predictive value beyond }Q,A,E.
\]

If H0 survives strong evaluation, the MAGIKARP claim contracts.

## 11. Secondary analyses

Allowed but not primary:

- whether SD predicts correction cost,
- whether SD predicts preservation,
- whether failure-depth accuracy predicts number of unnecessary revision stages,
- whether SD predicts transfer better than endpoint recovery,
- whether current performance and SD diverge during optimization.

Do not promote secondary results to primary after inspection without labeling them exploratory.

## 12. Strong positive pattern

A particularly informative pattern would be:

\[
Q_A\approx Q_B
\]

and comparable baseline adaptation/error measures, while:

\[
SD_A>SD_B
\]

measured before unrestricted adaptation, followed by superior held-out adaptation for A.

Stronger still: SD predicts adaptation across held-out failure families or across multiple agent architectures/checkpoints.

## 13. Failure condition

The distinctive v0.1 claim weakens substantially if:

\[
M_1 \not> M_0
\]

out of sample after reasonable measurement quality, sample size, and controls.

The response to a null should be claim contraction unless an independently demonstrated measurement or identifiability failure justifies revision.

## 14. Explicit non-goals

v0.1 does not need to measure or implement:

- full transformation topology,
- escape topology,
- authority capture,
- governance capture,
- provenance laundering,
- the seven deadly sins analogy,
- music taxonomy,
- CARP intervention,
- Gyarados failure as a primary endpoint,
- a universal JT scalar.

These remain explanatory reserve.
