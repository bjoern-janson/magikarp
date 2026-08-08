# MAGIKARP Evidence-Run Protocol v0.1

**Status:** frozen and normative for evidence-bearing MAGIKARP v0.1 runs.  
**Protocol identifier:** `0.1`  
**Benchmark identifier:** `MAGIKARP-v0.1`

This protocol governs evidence eligibility and provenance. It does not amend
the frozen benchmark contract, its supplied correction architecture, its
metrics, or its claim. `MUST`, `MUST NOT`, `SHOULD`, and `MAY` are normative.

The frozen scientific question remains:

> **Does prospective failure-depth diagnosis predict held-out recovery under
> the frozen supplied correction architecture?**

Selection among supplied revisions is not representation invention.

## 1. Evidence states and fail-closed rule

`evidence_ready` is a pre-run eligibility decision. `evidence_bearing` is a
post-run classification. Neither is a user assertion; both MUST be derived
from the manifest, independent attestation, current hashes, run conditions,
and validity result.

Only protocol compliance can authorize `evidence_ready=true`; only a valid
completed run can then produce `evidence_bearing=true`.

An execution is evidence-bearing only when all of the following are true:

1. benchmark and protocol versions are compatible;
2. every required manifest and provenance field is present and hash-valid;
3. generator independence is `L2` or `L3` under Section 2;
4. a separate pre-outcome attestation has status `independent_verified`,
   `attestor_independence="independent"`, and exact matching hashes;
5. the frozen seed, grouping, endpoint, exclusion, stopping, analysis, and
   classification rules were followed;
6. every required validity gate passes; and
7. the final status is `valid_positive` or `valid_negative`.

In compact form:

```text
evidence_bearing =
  evidence_intended
  AND evidence_ready
  AND independent_attestation_valid
  AND frozen_conditions_obeyed
  AND validity.all_passed
  AND status IN {valid_positive, valid_negative}
```

Unknown, missing, inconsistent, or unverifiable information MUST resolve to
`evidence_ready=false` and `evidence_bearing=false`. The built-in
`builtin_latent_context_v0.1` generator and derivatives remain `L0`,
`engineering_only`, and non-evidence-bearing regardless of metadata.

If a run was intended and attested as evidence-ready but violates a required
condition or gate, it is `benchmark_invalid`. A deliberately ineligible
infrastructure run is `engineering_only`. A valid null is `valid_negative`,
not invalid.

## 2. Structural independence

The governing distinctions are `surface difference != structural independence`
and `reproducibility != independence`. Different seeds, files,
numerical parameters, surface distributions, names, wrappers, or mechanical
rewrites do not create a new structural family. Reproducibility is not
independence.

A generator family is structurally distinct only when it is not derived from,
and does not share, the mechanism capable of manufacturing the target
relationship between prospective diagnosis and later recovery. Review MUST
compare the concrete construction of diagnostic evidence, failure instances,
labels, sufficient revisions, outcome/recovery functions, and evaluation—not
only source layout or output statistics.

Sharing the public v0.1 failure ontology and supplied action set is expected
and does not alone collapse independence. Sharing concrete signal prototypes,
target-generating equations, label construction, recovery logic, or a helper
that jointly determines diagnosis and outcome does.

### Graded independence

| Level | Operational meaning | Maximum authority |
| --- | --- | --- |
| `L0` | Built-in generator; seed/parameter/surface variant; wrapper, port, or mechanical derivative; or provenance too weak to judge. | Engineering and debugging only. `evidence_ready=false`. |
| `L1` | Internally authored and demonstrably different mechanism, but authors had access to benchmark implementation/results or remain under the same target-design process. | Measurement development and internal robustness only. `evidence_ready=false`. |
| `L2` | Independently authored synthetic family. Authors may know the public contract but did not derive from the built-in generator, inspect outcome-bearing runs, or reuse the target-manufacturing mechanism. Independently attested. | Bounded synthetic evidence for the frozen v0.1 predictive claim. |
| `L3` | External or naturally sourced family with independent origin and adjudication, mapped to v0.1 without outcome-driven redesign. Independently attested. | Cross-source predictive evidence within the demonstrated task scope. |

No level supports causal efficacy, representation invention, or general
intelligence claims. Uncertainty about independence lowers the assigned level.

### Required generator comparison record

`generator_provenance` MUST disclose, for the candidate and every comparison
family:

- `structural_family_id`, `generator_family`, `generator_version`,
  `generator_source_hash`, `author_or_origin`, `generator_created_at_utc`, and
  `derived_from` lineage;
- `shared_source_code` and `shared_helper_functions`;
- `shared_task_abstractions` and `shared_latent_failure_ontology`;
- `shared_parameterization` and shared signal construction;
- `shared_labeling_logic`;
- `shared_revision_controller_assumptions`;
- `shared_evaluation_assumptions`, including outcome construction;
- all `known_shared_dependencies`;
- `benchmark_internal_access`, including access to implementation, prior
  manifests, outcomes, or failed runs;
- the assigned `independence_level`, reviewer rationale, unresolved
  `independence_limitations`, and comparison-record hash; reviewer identity
  and rationale are `independence_reviewer_id` and
  `independence_rationale`, and the comparison hash is
  `comparison_record_hash`.

Evidence rows MUST carry `structural_family_id` separately from
`generator_family`. The latter may be a seed/index bucket and MUST NOT be
silently promoted to a structural family.

## 3. Required manifest and run records

The pre-outcome manifest MUST be deterministic and contain the following
evidential fields. Hashes are SHA-256 over raw file bytes or canonical JSON, as
appropriate.

| Block | Required fields |
| --- | --- |
| Identity | `benchmark_version`, `benchmark_contract_hash`, `evidence_protocol_version`, `evidence_protocol_hash`, `manifest_version`, `manifest_hash`, `run_id` |
| Scientific hashes | `scientific_hashes` containing contract, protocol, generator source/provenance, controller, analysis, config, and `design_freeze_hash` values |
| Generator | `generator_scope`, `generator_provenance`, `structural_family_id`, `generator_family`, `generator_version`, `generator_source_hash`, `generator_provenance_hash`, `independence_level`, author/origin, derivation, shared dependencies, internal access, and limitations |
| Controller and analysis | `controller_version`, `controller_source_hash`, `analysis_version`, `analysis_source_hash` |
| Frozen design | `design_freeze.seed_policy`, `group_assignment_policy`, `primary_endpoints`, `validity_gate_definitions`, `exclusion_rules`, `bootstrap_or_interval_procedure`, `stopping_rule`, and `evidence_classification_rules` |
| Existing execution identity | `config`, `config_hash`, Git SHA/clean state, executing source inventory/hash, authoritative-document hashes, split namespaces/hashes, Python/NumPy versions |
| Eligibility | intended independence level and machine-readable readiness prerequisites; readiness remains false until a valid external attestation is supplied |

`group_assignment_policy` MUST distinguish independent `agent_group_id` blocks,
structural families, and within-family `generator_family` buckets. The analysis
record MUST retain its actual outer scheme and bootstrap fields, including
`unit`, `group_field`, `n_groups`, `confidence`, `n_bootstrap`, and `seed`.

The immutable result envelope MUST add `run_timestamp_utc`, actual run status,
`evidence_intended`, derived `evidence_ready`, derived `evidence_bearing`,
effective `attestation_status`, validity output, deviations, and links to all
attempted run IDs. The pre-outcome manifest MUST NOT be edited to add these
post-start observations.

## 4. Independent attestation

Attestation is a separate pre-run JSON record, supplied to execution as
`--attestation`; it is not a mutable field inside the frozen manifest. The
record MUST contain exactly identified values for:

```text
schema_version
manifest_hash
benchmark_contract_hash
evidence_protocol_hash
generator_source_hash
generator_provenance_hash
controller_source_hash
analysis_source_hash
config_hash
run_id
independence_level
evidence_ready
attestor_id
attestor_independence
attested_at_utc
record_locator
status
attestation_hash
```

`attestation_hash` is the deterministic hash of the record excluding that
field. The attestor MUST independently recompute the referenced hashes, review
the provenance comparison, confirm version compatibility and eligibility, and
place the signed record or its hash in an append-only or otherwise immutable
location before outcome inspection.

Allowed status values are `missing`, `self_attested`, `process_verified`,
`independent_verified`, and `rejected`. Only `independent_verified` with
`attestor_independence="independent"`, `evidence_ready=true`, and level `L2`
or `L3` can authorize an evidence run. A bot or reviewer under the same
write/control authority may provide process integrity but not independent
attestation. Self-attestation is never sufficient. If an independent attestor
is unavailable, stop with `evidence_ready=false`.

Machine validation proves only schema completeness and hash binding. It does
not prove that `attestor_id` is truthful, that the attestor is outside the
author's control, or that `record_locator` is immutable. An external
party/process MUST confirm those facts; without that confirmation the run is
ineligible regardless of a syntactically valid record. This mechanism is an
audit anchor, not a substitute for independence.

## 5. Pre-outcome freeze boundary and run sequence

Before any evidence-bearing outcome is inspected, freeze and attest:

- benchmark contract and this protocol;
- generator source, provenance, structural-family assignment, and version;
- controller and diagnostic definitions;
- `Q`, `E`, `A`, `SD`, primary endpoint, and all reported outcomes;
- validity gates and thresholds;
- exclusion and missing-data rules;
- independent-group and structural-family assignments;
- seeds or seed-generation rule, run count, execution order, and stopping rule;
- model/preprocessing, primary comparison, effect threshold, bootstrap unit,
  confidence level, replicate count, and evidence-classification rules;
- analysis code, runtime/dependency versions, and artifact schema.

The sequence is:

1. register every planned `run_id` and seed under one frozen design;
2. build and hash the deterministic manifest;
3. obtain and publish the independent attestation;
4. verify manifest, attestation, executing source, runtime, and clean checkout;
5. execute once without inspecting interim outcomes or selecting seeds;
6. evaluate validity before the primary analysis;
7. classify and retain every planned run, including null and invalid runs; and
8. publish the result envelope and hashes without rewriting prior artifacts.

Any unplanned seed, early stopping, omitted run, post-hoc exclusion, or hash
mismatch invalidates confirmatory status unless already covered by a frozen
rule. Exploratory reanalysis MUST use a new manifest and be labeled as such.

## 6. Outcome authority

### Valid positive

A `valid_positive` result may support only the frozen predictive claim, and
only at the demonstrated independence level. Per-failure heterogeneity is a
secondary diagnostic under the frozen overall positive/null classification;
it is not a third top-level outcome and cannot replace the primary result.

Neither may be described as evidence for representation invention,
`G_rep`, Controlled Representational Escape, `FC_open`, creativity, universal
explanatory intelligence, recursive improvement of `C_improve`, or generation
of an unsupplied missing distinction. The supplied interface-expansion action
is a hard claim boundary.

### Valid null

A `valid_negative` result is a retained scientific evidence object. It MUST NOT
be dropped, hidden, replaced by selected seeds, or tuned away. It does not by
itself identify whether diagnosis is uninformative, the operationalization is
weak, controllers dominate, the taxonomy fails to transfer across generator
families, or another variable is needed.
Those are hypotheses for a separately frozen experiment.

### Invalid

Failed validity, provenance, independence, attestation, compatibility, or
frozen-run conditions authorize no empirical claim. Primary analysis MUST be
suppressed (`analysis.evaluated=false`) or, if retained for debugging, visibly
quarantined as non-evidence. An invalid run can never receive an empirical
positive or negative status.

## 7. Corrections and scientific versioning

An engineering correction restores the already-frozen semantics: packaging,
logging, serialization, deterministic seeding, manifest writing, a
non-semantic test-harness defect, or a mathematically incorrect implementation
of the frozen statistic. The defective run remains preserved and invalid; the
affected component version, hashes, manifest, and attestation MUST change
before rerun.

A scientifically material change alters what is generated, measured,
excluded, grouped, stopped, analyzed, or claimed. This includes changes to SD,
failure categories, task distributions, generator mechanisms, controller
semantics, endpoints, validity thresholds, exclusions, seed/group allocation,
or interpretation. A post-outcome material change requires a new
benchmark/protocol experiment version; it cannot retain confirmatory v0.1
identity.

When classification is ambiguous, treat the change as scientifically
material. Never repair v0.1 toward a desired result under the same version.

## 8. Adversarial closure table

| # | Attack | Required closure | Fail-closed result |
| ---: | --- | --- | --- |
| 1 | Built-in becomes eligible through a metadata trick. | Eligibility is derived from verified source/provenance hashes and ancestry; the built-in and derivatives are fixed at `L0`. A claimed flag cannot override identity. | `engineering_only`; both evidence flags false. |
| 2 | Shared target-manufacturing mechanism passes as structurally distinct. | Mandatory mechanism comparison covers signals, labels, failures, recovery logic, shared helpers, derivation, and internal access; unresolved sharing lowers the level below `L2`. | Not evidence-ready. |
| 3 | Endpoint changes after outcomes without versioning. | Endpoint and classification rules are inside the attested `design_freeze_hash`; any change breaks manifest/attestation hashes. | Prior run invalid; new version required. |
| 4 | Failed validity gate yields a positive-looking artifact. | Validity precedes primary analysis; failed gates suppress/quarantine analysis and cannot map to `valid_positive` or `valid_negative`. | `benchmark_invalid`, non-evidence-bearing. |
| 5 | Null run is silently excluded. | All planned run IDs are preregistered in an append-only attempt ledger; every completion, null, invalidity, and technical failure is retained. Missing runs make the batch incomplete. | No aggregate evidence claim until reconciled. |
| 6 | Seed selection becomes outcome tuning. | Seed policy, count, order, and stopping rule are attested pre-outcome; all planned seeds are included exactly once. | Deviation invalidates confirmatory status. |
| 7 | Post-hoc exclusions alter the claim. | Exclusion rules are frozen and every exclusion records its rule and reason. New exclusions require an exploratory label and new version/manifest. | Original confirmatory claim invalid. |
| 8 | Self-attestation masquerades as independent. | Attestation is a separate record with disclosed identity/control relationship. Machine checks bind fields and hashes but cannot establish identity, control independence, or locator immutability; an external party/process must confirm them. | Self/process verification remains non-evidence-ready. |
| 9 | Positive is described as representation invention. | Outcome authority and the supplied-revision boundary are protocol-hashed and repeated in result artifacts. Such language is a protocol violation, not an allowed interpretation. | Claim must be withdrawn/corrected; evidence scope remains v0.1 predictive only. |
| 10 | Material task change is called a bug fix under the same version. | Change classification examines task, measurement, grouping, analysis, and claim effects; ambiguity is resolved conservatively and scientific hashes expose changes. | New benchmark/protocol experiment version required. |

## 9. Current qualification and stopping rule

No current generator qualifies. The built-in generator has namespaced buckets
over one synthetic mechanism, no `structural_family_id` independence, and
`evidence_ready=false`; it remains useful engineering infrastructure.

Once this protocol, fail-closed eligibility, provenance/attestation checks, and
boundary tests are in place, stop engineering v0.1. The next research action is
to obtain a genuinely `L2` or `L3` evidence source—not to relabel or wrap the
built-in generator, tune toward a positive result, or implement later
representation-invention research.
