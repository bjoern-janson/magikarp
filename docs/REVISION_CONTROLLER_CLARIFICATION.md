# Revision-Controller Clarification

**Status:** post-freeze clarification for implementation and interpretation.  
**Authority:** does not amend the frozen MAGIKARP v0.1 primary hypothesis, load-bearing variable set, or statistical comparison.

## Purpose

The full research lineage suggests a useful decomposition that is only implicit in the frozen v0.1 materials:

> Failure diagnosis, revision selection, and adaptation outcome are distinct empirical objects.

MAGIKARP should therefore avoid treating a successful diagnosis as equivalent to a selected revision, or a selected revision as equivalent to successful adaptation.

The implementation-facing chain is:

\[
\boxed{
F
\rightarrow
q_{SD}(F\mid E_{\mathrm{diag}})
\rightarrow
D_{\mathrm{revision}}
\rightarrow
Y_{\mathrm{adapt}}
}
\]

where:

- \(F\) is the experimenter-controlled true failure depth;
- \(E_{\mathrm{diag}}\) is diagnostic evidence available before unrestricted adaptation;
- \(q_{SD}(F\mid E_{\mathrm{diag}})\) is the system's prospective diagnostic distribution over failure depth;
- \(D_{\mathrm{revision}}\) is the revision depth actually selected during adaptation;
- \(Y_{\mathrm{adapt}}\) is the later held-out adaptation trajectory.

Each arrow is a separate empirical question.

## Diagnostic output versus SD

For continuity, the project retains the symbol `SD`, but `SD` should not simultaneously mean the raw diagnostic output, its accuracy, and a latent self-model.

A system may emit:

\[
q_{SD}(F\mid E_{\mathrm{diag}})
=
\big(q(F_p),q(F_m),q(F_i)\big).
\]

`SD` is then a preregistered measure of the quality of that prospective diagnostic signal, for example through failure-depth discrimination, calibration, or another fixed proper scoring rule.

Operationally, `SD` means sensitivity to the limits of the current representation. It does not require anthropomorphic self-understanding.

## Three separable failure transitions

### 1. Diagnostic failure

The true failure depth is not recovered reliably from the diagnostic evidence:

\[
q_{SD}(F)\not\approx F.
\]

Example: the benchmark contains an interface failure, but the system assigns most probability to parameter failure.

This is a failure to localize what kind of thing is wrong.

### 2. Revision-governance failure

The system diagnoses the failure depth adequately but selects an inappropriate intervention depth:

\[
q_{SD}(F)\approx F,
\qquad
D_{\mathrm{revision}}\not\approx D_{\mathrm{sufficient}}(F).
\]

Example: the system correctly identifies an interface failure but continues parameter tuning, or identifies a parameter failure but unnecessarily restructures the interface.

Diagnosis therefore does not imply authorization or execution.

### 3. Execution/adaptation failure

The system selects an appropriate revision class but fails to implement it successfully:

\[
D_{\mathrm{revision}}\approx D_{\mathrm{sufficient}}(F),
\qquad
Y_{\mathrm{adapt}}\text{ remains poor}.
\]

This separates inability to execute a warranted change from inability to diagnose or select it.

## Revision-depth calibration

The target is not maximum plasticity and not minimum change in isolation. It is **minimum sufficient revision**:

\[
\boxed{
D_{\mathrm{revision}}
\approx
D_{\mathrm{sufficient}}(F)
}
\]

where the sufficient revision is the least costly revision that restores held-out reliability while preserving still-valid structure, respecting scope, and avoiding unnecessary escalation.

This gives two symmetric failure modes:

- **under-revision:** \(D_{\mathrm{revision}}<D_{\mathrm{sufficient}}(F)\);
- **over-revision:** \(D_{\mathrm{revision}}>D_{\mathrm{sufficient}}(F)\).

The existing agent families should therefore be treated as a load-bearing adversarial comparison:

| System | Expected characteristic failure |
| --- | --- |
| Rigid / local updater | under-revision on deep failures |
| Hyperplastic updater | over-revision on shallow failures |
| Depth-aware updater | revision depth tracks the sufficient failure-specific intervention |

A benchmark that rewards only deep-failure recovery could mistakenly favor indiscriminate restructuring. Shallow-failure controls are necessary to discriminate selective adaptation from hyperplasticity.

## Relationship to the frozen v0.1 hypothesis

This clarification does **not** replace the primary prospective test:

\[
M_0:Y_{\mathrm{adapt}}\sim Q+A+E
\]

versus:

\[
M_1:Y_{\mathrm{adapt}}\sim Q+A+E+SD.
\]

The primary question remains whether pre-adaptation diagnostic sensitivity adds reproducible held-out predictive information beyond present competence, ordinary error sensitivity, and strong adaptation baselines.

The revision trace is a secondary mechanistic analysis. A useful diagnostic quantity is:

\[
E_D=d(D_{\mathrm{revision}},D_{\mathrm{sufficient}}(F)).
\]

Secondary questions include whether:

\[
SD\uparrow\Rightarrow E_D\downarrow
\]

and whether lower revision-depth error predicts lower correction cost, stronger preservation, and better transfer.

These associations must not be promoted into causal claims without intervention.

## Causal boundary

The v0.1 sequence remains:

\[
\text{diagnostic probes}
\rightarrow
SD
\rightarrow
\text{held-out perturbation}
\rightarrow
D_{\mathrm{revision}}
\rightarrow
Y_{\mathrm{adapt}}.
\]

A predictive result does not establish:

\[
SD\rightarrow Y_{\mathrm{adapt}}
\]

causally.

A later stage would need to test:

\[
do(SD\uparrow)
\overset{?}{\longrightarrow}
Y_{\mathrm{adapt}}\uparrow.
\]

Only after such a result should a candidate procedure such as CARP be tested as a mechanism for increasing the relevant diagnostic property.

## Compression

The implementation-level question is:

> **Before changing, can a system discriminate what kind of thing is wrong, select the minimum sufficient revision depth, and then successfully execute that revision?**

For MAGIKARP v0.1, only the first part is promoted to the primary predictive construct. The remaining transitions are recorded separately so that benchmark failures can be localized rather than collapsed into a single adaptation score.
