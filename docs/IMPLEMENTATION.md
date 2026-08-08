# MAGIKARP v0.1 executable implementation

## Authority and scope

This implementation executes the frozen predictive v0.1 contract. It does not
amend that contract and does not implement the broader Deutschian target of
open-ended representation invention.

The interface-failure action is supplied by the benchmark. The implementation
tests prospective discrimination among parameter, model, and interface
failure, followed by controlled selection of one of those supplied revision
depths.

This implementation has one built-in synthetic generator. Its
`generator_family` labels are deterministic seed/index buckets within that
generator, not structurally distinct mechanisms and not external benchmark
families. Consequently the built-in execution path is fail-closed as
`engineering_only`, including when the manifest workflow is exercised.

## Operational loop

One run performs the following sequence:

1. Build distinct deterministic baseline, ordinary-adaptation, diagnostic,
   adaptation, and transfer seed/identifier namespaces over the same synthetic
   generator.
2. Generate a crossed population: three diagnostic-skill levels under rigid,
   hyperplastic, depth-aware, and evidence-heuristic controllers.
3. Measure `Q`, `E`, and `A` before held-out adaptation.
4. Emit raw prospective `q_SD` on the diagnostic battery and compute the
   frozen normalized Brier `SD`.
5. Diagnose separate namespaced adaptation cases, select one supplied
   revision depth, and retain the full revision trace.
6. Evaluate recovery on the adaptation case and transfer/retention on a
   disjoint transfer case.
7. Run validity gates A-F before interpreting the primary comparison.
8. Collapse episodes to agent × generator-family × failure rows.
9. Compare `M0: R_c ~ Q + A + E` with
   `M1: R_c ~ Q + A + E + SD` using two-way held-out prediction that excludes
   both the test agent ID and test generator-family bucket. This exercises the
   analysis machinery; it is not a structural-family generalization claim.
10. Write raw-enough records, predictions, validity output, and compact
    summaries.

## Synthetic intervention oracle

The finite environment freezes these minimum sufficient depths:

| Failure | Depth 0: parameter | Depth 1: model | Depth 2: interface | Minimum |
| --- | ---: | ---: | ---: | ---: |
| parameter | 0.96 | 0.95 | 0.93 | 0 |
| model | 0.36 | 0.95 | 0.93 | 1 |
| interface | 0.24 | 0.34 | 0.94 | 2 |

Deeper-than-necessary actions may recover but incur greater correction and
preservation costs. Interface impossibility is separately checked through an
observational collision under the old interface.

## Anti-confounding controls

- Diagnostic skill is crossed with every controller family.
- Controller-matched agents emit identical `q_SD` for the same diagnostic
  block; controller identity therefore does not determine `SD`.
- The evidence heuristic uses the same admissible evidence but ignores the
  emitted `q_SD`.
- Diagnostic functions do not read the experimenter-only failure label.
- Nuisance and error-magnitude distributions are exactly balanced across
  failure labels.
- Analysis aggregates episodes before prediction and excludes both held-out
  agent IDs and generator-family bucket IDs from training. Matched agent blocks
  and the single underlying synthetic generator remain shared dependencies.
- Raw Brier `SD` remains primary; class-balanced Brier skill is reported as a
  robustness diagnostic rather than substituted post hoc.

## Commands

Install and verify:

```text
python -m pip install -e .
python -m unittest discover -s tests -v
magikarp smoke --output results/smoke
```

A smoke run is `engineering_only` when all validity gates pass and
`benchmark_invalid` when any gate fails. It cannot produce evidence for or
against MAGIKARP.

Exercise the future evidence-run infrastructure:

```text
magikarp template --mode evidence --output configs/evidence-v0.1.json
magikarp freeze --config configs/evidence-v0.1.json --manifest manifests/evidence-v0.1.json
magikarp run --manifest manifests/evidence-v0.1.json --attestation attestations/evidence-v0.1.json --output results/evidence-v0.1
```

These commands exercise evidence-run infrastructure; with the built-in
single-generator scope they still produce an engineering-only result, with or
without an attestation. Review and commit the implementation and evidence
config before `freeze`. `freeze` requires the executing `src/magikarp` package
to reside in that repository, binds manifest v3 to the contract, evidence
protocol, generator provenance, controllers, analysis, design choices, source
tree, and runtime, and requires a clean commit. `run` requires the same commit,
runtime, source/doc hashes, and rejects tracked changes made after freezing.

Attestation is a separate pre-outcome JSON record bound to the frozen manifest
hash. Its deterministic schema/hash checks cannot prove attestor identity,
control independence, or locator immutability; an external party or process
must establish those facts. Missing, self, incomplete, or mismatched
attestation fails closed. The normative requirements are in
[`EVIDENCE-RUN-PROTOCOL-v0.1.md`](../EVIDENCE-RUN-PROTOCOL-v0.1.md).
`magikarp.eligibility.seal_attestation` and `write_attestation` canonicalize and
persist a reviewer-created record; calling them does not confer independence.

## Artifacts

Every successful run writes:

```text
manifest.json
evidence_eligibility.json
diagnostic_records.jsonl
trial_records.jsonl
validity.json
predictions.csv
summary.json
summary.md
```

A run supplied with an attestation also preserves `attestation.json`, even if
eligibility fails.

## Remaining evidence boundary

An executable loop is not an evidence-bearing result. The built-in family
labels are namespaced buckets over one generator, not structural holdouts. No
external benchmark cases, independent agent implementations, independently
attested manifest, or externally frozen adjudication has yet been supplied. A
later valid positive would remain predictive; it would not establish causation,
representation invention, recursive improvement capacity, or
`I proportional to C_improve`.
