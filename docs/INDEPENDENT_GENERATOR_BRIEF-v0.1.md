# MAGIKARP v0.1 — Independent Generator Brief

**Audience:** a team authoring a candidate `L2` synthetic generator without reading MAGIKARP implementation internals.

This brief is intentionally narrower than the full repository. Its purpose is to preserve generator independence while still giving an external team enough information to construct a source compatible with the frozen v0.1 scientific question.

Do not use this document to claim `L2` automatically. Independence is established by provenance, access history, structural comparison, and separate review under `EVIDENCE-RUN-PROTOCOL-v0.1.md`.

## 1. Frozen question

MAGIKARP v0.1 asks whether a **prospective pre-adaptation diagnosis of failure depth** contains held-out predictive information about later recovery beyond frozen baseline controls.

The failure-depth vocabulary is:

```text
0 = parameter
1 = model
2 = interface
```

The benchmark does not ask the system to invent an unsupplied representation. It selects among supplied revision classes.

## 2. Required source semantics

Your source should independently construct tasks in which the minimum sufficient correction depth is knowable.

### Parameter failure

The current represented variables and model form remain adequate. A local parameter/value revision is sufficient.

### Model failure

The relevant variables remain represented, but a local parameter change is insufficient. A relationship/model-structure revision is sufficient while the observation interface remains adequate.

### Interface failure

The existing observation/representation interface collapses a distinction required for correct behavior. Parameter and model revision over the old interface are insufficient. A supplied interface-expansion class makes recovery possible.

The source must support an independent method for establishing these minimum sufficient depths before outcome interpretation.

## 3. Diagnostic phase

Before unrestricted adaptation, provide evidence that makes the failure-depth class identifiable **in expectation**.

The evidence must not expose:

- an experimenter-owned failure label;
- a deterministic class token;
- later recovery/outcome information;
- revision choices made after the diagnostic phase.

The diagnostic representation does not need to resemble the built-in generator and should not be reverse-engineered from it.

## 4. Adaptation phase

Use held-out cases distinct from the diagnostic cases.

Allow the system to choose among the frozen supplied revision depths. Record the chosen depth and later outcomes separately from the earlier diagnosis.

The source should make unnecessary deeper revision costly or disruptive enough that always choosing the deepest action is distinguishable from targeted correction.

## 5. Required outcome surfaces

The integration layer must eventually be able to derive or record:

- recovery;
- transfer;
- retention;
- preservation of still-valid behavior;
- correction/revision cost.

Do not collapse these into a single universal score.

## 6. Independence constraints

To preserve a plausible `L2` claim, generator authors should avoid access to:

- `src/magikarp/`;
- built-in generator equations;
- built-in diagnostic signal prototypes;
- built-in recovery/outcome functions;
- tests encoding those mechanisms;
- prior evidence outcomes or failed evidence runs.

Knowing the public failure ontology and that v0.1 uses supplied depth-0/1/2 revision classes is allowed and expected.

If you have already inspected implementation internals, disclose that access. The source may still be useful, but its maximum evidence authority may be lower.

## 7. Provenance deliverable

Before integration, deliver a structured provenance record describing:

- generator/source name and version;
- immutable source hash or locator;
- author/origin;
- creation timestamp;
- derivation history;
- source code shared with MAGIKARP, if any;
- helper functions shared with MAGIKARP, if any;
- shared task abstractions;
- shared latent failure ontology;
- shared parameterization or signal construction;
- shared labeling logic;
- shared revision-controller assumptions;
- shared evaluation/outcome assumptions;
- known dependencies;
- access to the public contract;
- access to MAGIKARP implementation;
- access to prior manifests;
- access to prior outcomes;
- access to failed runs;
- known independence limitations.

Do not self-assign authority by declaration. An independent reviewer will compare this record against the frozen protocol.

## 8. What to hand to the integration team

Provide, before any MAGIKARP outcome is inspected:

1. immutable generator/source version;
2. generator source hash;
3. documentation of the three minimum sufficient correction depths;
4. diagnostic/adaptation/transfer split policy;
5. seed or case-generation policy;
6. nuisance/leakage surfaces that should be audited;
7. provenance record;
8. a deterministic or otherwise preregisterable execution interface;
9. any known limitations.

Do not tune the generator after seeing whether MAGIKARP's `M1` beats `M0`.

## 9. What the integration team may do

After your source is frozen, a separate integration team may build the smallest adapter needed to map your source into the frozen MAGIKARP measurement and artifact surfaces.

That adapter must be reviewed for target leakage. In particular, it must not encode the true failure class into the diagnostic observation under a convenient intermediate representation.

If integration requires changing the scientific meaning of `Q`, `E`, `A`, `SD`, the failure classes, the primary endpoint, or the primary comparison, the project must apply the scientific-versioning rule rather than silently calling the result v0.1.

## 10. Evidence authority

Even a fully qualifying generator does not make a run evidence-bearing by itself.

The final run also requires:

- frozen scientific/source/config hashes;
- a valid manifest;
- a separate independent pre-outcome attestation;
- all required validity gates;
- exact adherence to the preregistered run conditions.

A valid positive supports only the bounded predictive v0.1 claim. A valid null is retained. An invalid run supports neither a positive nor a negative empirical claim.
