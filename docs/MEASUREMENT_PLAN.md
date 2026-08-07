# Measurement Plan

## 1. Core measurement principle

Measure diagnosis first. Measure adaptation later.

`SD` is a prospective predictor, not a retrospective label for agents that adapted well.

## 2. SD construction

The diagnostic phase should yield outputs such as:

\[
p(F_p),p(F_m),p(F_i)
\]

Potential components:

### Depth accuracy
How often the highest-probability diagnosis matches ground-truth failure depth.

### Calibration
Whether assigned probabilities correspond to empirical correctness.

### Boundary sensitivity
Whether the system appropriately raises probability on representation-level failure when local explanations become inadequate.

Do not finalize a composite SD score after looking at adaptation outcomes.

A reasonable v0.1 strategy is to preregister one primary SD metric and report the components separately.

## 3. Raw error sensitivity E

Control for the simpler explanation that SD merely measures noticing error.

Possible E metrics:

- prediction-error magnitude,
- anomaly detection rate,
- surprise,
- confidence drop after failure,
- latency to acknowledge mismatch.

The benchmark's distinctive signal should survive reasonable controls for E.

## 4. Standard adaptation baseline A

Choose baselines appropriate to the toy environment.

Candidates:

- adaptation speed under ordinary parameter shifts,
- update count,
- learning-rate responsiveness,
- robustness to perturbation,
- calibration,
- continual-learning retention,
- training exposure,
- agent capacity/parameter count.

Do not add controls so indiscriminately that they deterministically encode SD itself. Controls should represent plausible existing alternatives.

## 5. Outcome vector

Keep:

\[
Y_{\text{adapt}}=(R_c,T,R,P,C)
\]

separate in raw results.

### Recovery R_c
How much target-task performance returns after adaptation.

### Transfer T
How well the learned correction applies to unseen related conditions.

### Retention R
Whether adaptation persists across delayed evaluation or intervening tasks.

### Preservation P
Whether unaffected prior capabilities/relationships remain intact.

### Cost C
The amount of unnecessary or expensive change required.

Possible C measures:

- update steps,
- revision depth,
- number of failed interventions before correct revision,
- data/compute budget,
- induced regressions,
- explicit environment revision costs.

## 6. Primary predictive comparison

Use a simple, auditable predictive pipeline first.

Example:

```text
M0: Y_primary ~ Q + A + E
M1: Y_primary ~ Q + A + E + SD
```

Evaluation:

- nested or carefully separated cross-validation,
- held-out failure families where feasible,
- report delta in predictive performance,
- bootstrap or repeated-seed uncertainty,
- include per-outcome secondary models.

Suitable metrics depend on Y:

- R² / MAE for continuous endpoints,
- log loss / AUROC for binary endpoints,
- ranking correlation if outcome is ordinal.

The scientific criterion is out-of-sample improvement, not coefficient significance.

## 7. Stronger generalization levels

Report performance across increasingly difficult holdouts:

1. random held-out instances,
2. held-out perturbation parameters,
3. held-out failure families,
4. held-out agent checkpoints,
5. held-out agent architectures,
6. later: held-out domains.

Do not claim broad transfer from level 1 alone.

## 8. Leakage audit

Before interpreting any result, check whether SD can be predicted from superficial benchmark artifacts:

- feature distributions,
- prompt/template wording,
- sequence length,
- failure label encodings,
- generator IDs,
- episode IDs,
- perturbation magnitude accidentally tied to failure class.

Train a nuisance classifier on these artifacts where useful.

If a trivial classifier can identify F without using the intended diagnostic evidence, redesign the generator.

## 9. Matched-capability analysis

A useful complementary analysis is to compare systems/checkpoints within a narrow Q band.

This tests whether SD separates future adaptation among currently similar performers.

Do not rely only on exact pair matching; the primary result should come from aggregate held-out prediction.

## 10. Correction-cost secondary endpoint

This may be especially discriminating.

Two agents can reach equal recovery:

\[
R_c(A)=R_c(B)
\]

while:

\[
C(A)\gg C(B)
\]

because one performs several wrongly targeted revisions before reaching the correct layer.

Test whether pre-adaptation SD predicts lower recovery cost even when endpoint recovery is comparable.

## 11. Negative-result handling

If M1 fails to outperform M0:

1. verify measurement reliability and leakage controls,
2. verify that F is identifiable from diagnostic evidence,
3. verify adequate variation in SD,
4. verify adequate power/sample size,
5. if those pass, contract the claim.

Do not redefine SD around the observed outcome.
