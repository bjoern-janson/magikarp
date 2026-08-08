# Controlled Representational Escape (CRE)

## Introductory guide

> **Status:** future research context only. CRE is **not** part of the frozen MAGIKARP v0.1 benchmark contract, implementation target, or evidence claim. Nothing in this document may be used to reinterpret a MAGIKARP v0.1 result.

## The problem

A system can fail even when its current model is being used correctly, because the representation itself may not contain the distinction required for correction.

The hard case is not merely:

```text
How should the current model be adjusted?
```

It is:

```text
When is the current representation no longer sufficient,
what alternatives should be considered,
and when has any successor earned authority?
```

CRE is the proposed governance problem for that transition.

## Core idea

CRE separates three events that are often collapsed:

1. **leaving** — evidence warrants treating some part of the current representation as insufficient;
2. **generating** — candidate distinctions or successor representations are introduced;
3. **adopting** — a particular candidate earns scoped operational authority after discrimination.

The central invariant is:

> **Evidence can authorize departure without authorizing destination.**

A failure of the current representation therefore does not validate whichever replacement is generated next.

## Scoped departure

Evidence should only revise the scope it can identify.

```text
local residual
!=
global model rejection
```

If evidence challenges only a region, variable, relation, or use-case, departure authority is limited to that scope.

A system should preserve unaffected structure unless stronger evidence warrants broader revision.

## Candidate generation is not authority

Generating a new representation expands the possibility space. It does not expand the authority space.

```text
candidate generated
!=
candidate validated
```

A useful candidate should ideally make a discriminating commitment: what new distinction it introduces, what observation or intervention could separate it from alternatives, what it predicts, and what result would reduce support for it.

Novelty alone earns no authority.

## The unresolved state

CRE requires an explicit state in which:

```text
current representation: insufficient
successor representation: unresolved
```

This is not automatically a failure state.

It may be the correct result when evidence is strong enough to leave the old representation but not strong enough to adopt a new one.

Without this state, a system is forced toward one of two errors:

- retain an inadequate representation;
- invent a replacement and treat invention as knowledge.

The ability to remain unresolved is therefore load-bearing.

## Minimal transition

The intended transition is:

```text
scoped challenge
-> scoped departure
-> unresolved
-> candidate generation
-> discrimination
-> scoped adoption
-> validation
-> inheritance
-> reopening when new evidence warrants it
```

No transition silently grants the authority belonging to a later transition.

## Adoption is scoped and reopenable

A successor that succeeds under one tested scope earns authority only for that scope unless independent evidence supports broader reach.

Validation is also not permanent immunity.

```text
retained
!=
irreversible
```

Previously accepted representations remain reopenable when new evidence exposes a relevant failure.

## What CRE is not

CRE is not:

- generic creativity;
- unrestricted hypothesis generation;
- automatic ontology expansion after surprise;
- proof that every failure is representational;
- permission to replace a model whenever a more interesting one appears;
- evidence that a generated representation is true;
- part of MAGIKARP v0.1.

The difficult capability is governed transition between representational authorities, not generation by itself.

## Relationship to MAGIKARP

MAGIKARP v0.1 asks a deliberately earlier and narrower empirical question:

> **Does prospective failure-depth diagnosis add held-out predictive information about later recovery under supplied correction actions?**

Its correction classes are supplied. Selecting the supplied interface-level action is therefore not evidence of representation invention or CRE.

The research sequence is intentionally separated:

```text
MAGIKARP
-> diagnose whether correction depth carries prospective information

CRE
-> govern departure from an inadequate representation and successor adoption

Post-CRE
-> improve the machinery that performs that governance
```

A positive MAGIKARP result would not establish CRE. A null MAGIKARP result would also not by itself falsify the broader CRE problem; it would constrain the particular diagnostic relation MAGIKARP tests.

## What a future CRE benchmark must distinguish

A valid CRE benchmark must make it impossible to pass merely by always escalating, always refusing, or selecting a supplied hidden answer.

At minimum it should distinguish:

- cases repairable within the current representation;
- cases where the current representation is insufficient;
- candidate generation from candidate selection;
- departure authority from adoption authority;
- correct unresolved states from indecision;
- local success from transfer to a structurally different future failure;
- targeted improvement from destructive over-revision.

A useful acceptance question is:

> **Could a system pass without ever learning when representation change is warranted?**

If yes, the benchmark is not testing CRE.

## Three governing statements

> **An apparent edge may be a limit of resolution.**

> **Evidence can authorize departure without authorizing destination.**

> **When neither the old nor a new representation has sufficient authority, unresolved is the valid state.**

Together they impose a symmetric discipline:

```text
never make the current interface final;
never make its successor self-authorizing.
```

## Current status

CRE is a frozen future research target, not an implemented or validated MAGIKARP capability.

The immediate MAGIKARP priority remains unchanged:

```text
independent evidence source
-> provenance review
-> minimum source-specific adapter
-> frozen manifest
-> independent pre-outcome attestation
-> qualifying v0.1 evidence run
```

Do not expand MAGIKARP v0.1 to implement CRE before that empirical sequence is completed.
