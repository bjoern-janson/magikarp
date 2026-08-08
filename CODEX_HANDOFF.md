# Codex Handoff — Current Entry Point

The original MAGIKARP v0.1 implementation handoff has been completed and is preserved at [`archive/CODEX_HANDOFF_INITIAL.md`](archive/CODEX_HANDOFF_INITIAL.md).

Do **not** treat the old first-benchmark build brief as the current task.

## Current project state

Start with:

1. [`PROJECT_FREEZE.md`](PROJECT_FREEZE.md)
2. [`CONTINUATION.md`](CONTINUATION.md)
3. [`EVIDENCE-RUN-PROTOCOL-v0.1.md`](EVIDENCE-RUN-PROTOCOL-v0.1.md)

The built-in deterministic benchmark is an engineering reference only. It is fixed at `L0` and cannot produce scientific evidence.

## Current task boundary

The next scientific step is to obtain a genuinely independent `L2` or `L3` evidence source.

Do not:

- expand the conceptual framework;
- polish or generalize the built-in generator without a concrete evidence-source need;
- implement representation invention or CRE in v0.1;
- build a generic generator plugin system in anticipation of unknown sources;
- tune the frozen benchmark around observed outcomes.

Once an independent source is frozen, implement only the minimum source-specific execution adapter required to preserve the existing v0.1 measurement, validity, provenance, and claim boundaries.

Independent generator authors should use [`docs/INDEPENDENT_GENERATOR_BRIEF-v0.1.md`](docs/INDEPENDENT_GENERATOR_BRIEF-v0.1.md) without inspecting implementation internals if they are intended to preserve a plausible `L2` independence claim.
