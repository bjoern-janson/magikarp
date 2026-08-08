"""Deterministic synthetic environment for the MAGIKARP v0.1 benchmark.

The environment deliberately keeps the v0.1 boundary narrow: an interface
failure is repaired by a *supplied* interface-expansion action (revision depth
2).  Nothing in this module claims or tests open-ended representation
invention.

All pseudo-random values come from stable, named streams.  Reordering calls or
running under a Python process with a different hash seed therefore cannot
change a generated case or outcome.
"""

from __future__ import annotations

import hashlib
import math

import numpy as np

from .types import AgentSpec, DiagnosticEvidence, FailureDepth


# All v0.1 built-in buckets are parameterizations of one structural generator
# family.  Keeping this identifier fixed prevents split or bucket names from
# being mistaken for independently implemented structural families.
BUILTIN_STRUCTURAL_FAMILY_ID = "builtin_latent_context_v0.1"


# Rows are failure depths; columns are committed revision depths.  A value is
# the accuracy available to a perfect executor.  Deeper-than-necessary actions
# can still solve a failure, but carry disruption and correction costs in
# ``evaluate_revision``.
_INTERVENTION_ACCURACY: tuple[tuple[float, float, float], ...] = (
    (0.96, 0.95, 0.93),  # parameter: depth 0 is sufficient
    (0.36, 0.95, 0.93),  # model: depth 1 is the minimum sufficient action
    (0.24, 0.34, 0.94),  # interface: only supplied depth-2 expansion works
)

_REVISION_COSTS: tuple[float, float, float] = (1.0, 3.0, 7.0)


def _stream_seed(seed: int, *parts: object) -> int:
    """Return a platform-stable 64-bit seed for a named random stream."""

    material = "\x1f".join((str(int(seed)), *(str(part) for part in parts)))
    digest = hashlib.blake2b(material.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little", signed=False)


def _rng(seed: int, *parts: object) -> np.random.Generator:
    return np.random.default_rng(_stream_seed(seed, *parts))


def _validate_namespace(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip().replace(" ", "-")


def generate_diagnostic_evidence(
    seed: int,
    split: str,
    cases_per_failure: int,
    generator_prefix: str,
) -> list[DiagnosticEvidence]:
    """Generate a balanced, identifiable diagnostic battery.

    ``signals`` are the only label-informative surface.  The nuisance vector
    and ordinary error magnitude are paired across the three failure depths,
    so their empirical distributions are exactly label-independent.  Case IDs
    and generator-family names omit failure labels and are assigned after a
    deterministic shuffle.
    """

    if isinstance(cases_per_failure, bool) or not isinstance(cases_per_failure, int):
        raise TypeError("cases_per_failure must be an integer")
    if cases_per_failure < 1:
        raise ValueError("cases_per_failure must be at least 1")

    split_name = _validate_namespace(split, "split")
    prefix = _validate_namespace(generator_prefix, "generator_prefix")
    family_count = min(4, cases_per_failure)

    # These prototypes describe admissible pre-adaptation evidence: localized
    # residuals, structural residuals, and observational collisions.  They are
    # not outcome observations and do not execute a correction.
    signal_prototypes: tuple[tuple[float, float, float], ...] = (
        (0.90, 0.28, 0.16),
        (0.30, 0.91, 0.22),
        (0.25, 0.37, 0.94),
    )

    provisional: list[DiagnosticEvidence] = []
    for case_index in range(cases_per_failure):
        # Reuse exactly the same nuisance tuple and error magnitude for one
        # case at every failure depth.  This is stronger than independence in
        # expectation and makes a nuisance-only leakage test meaningful even
        # for a small smoke battery.
        nuisance_rng = _rng(seed, prefix, split_name, "nuisance", case_index)
        nuisance = tuple(float(x) for x in nuisance_rng.uniform(-1.0, 1.0, size=3))
        error_magnitude = float(nuisance_rng.uniform(0.35, 0.85))
        family = f"{prefix}.{split_name}.latent-context-{case_index % family_count:02d}"

        for failure in FailureDepth:
            signal_rng = _rng(
                seed,
                prefix,
                split_name,
                "diagnostic-signal",
                case_index,
                failure.value,
            )
            noisy = np.asarray(signal_prototypes[failure.value]) + signal_rng.normal(
                loc=0.0, scale=0.055, size=3
            )
            signals = tuple(float(x) for x in np.clip(noisy, 0.02, 0.98))
            provisional.append(
                DiagnosticEvidence(
                    # Replaced after shuffling so neither the text nor a fixed
                    # modulo pattern exposes the failure class.
                    case_id="",
                    split=split_name,
                    generator_family=family,
                    structural_family_id=BUILTIN_STRUCTURAL_FAMILY_ID,
                    failure=failure,
                    signals=signals,
                    error_magnitude=error_magnitude,
                    nuisance=nuisance,
                )
            )

    order_rng = _rng(seed, prefix, split_name, "case-order")
    order = order_rng.permutation(len(provisional))
    width = max(4, len(str(len(provisional) - 1)))
    evidence: list[DiagnosticEvidence] = []
    for public_index, private_index in enumerate(order):
        item = provisional[int(private_index)]
        evidence.append(
            DiagnosticEvidence(
                case_id=f"{prefix}.{split_name}.case-{public_index:0{width}d}",
                split=item.split,
                generator_family=item.generator_family,
                structural_family_id=item.structural_family_id,
                failure=item.failure,
                signals=item.signals,
                error_magnitude=item.error_magnitude,
                nuisance=item.nuisance,
            )
        )
    return evidence


def oracle_accuracy(failure: FailureDepth | int | str, revision_depth: int) -> float:
    """Return oracle task accuracy for a failure/action pair.

    The minimum sufficient depths are 0, 1, and 2 for parameter, model, and
    interface failures respectively.  The interface action is supplied by the
    benchmark; the oracle does not invent an observation channel.
    """

    normalized_failure = _coerce_failure(failure)
    normalized_depth = _coerce_revision_depth(revision_depth)
    return _INTERVENTION_ACCURACY[normalized_failure.value][normalized_depth]


def intervention_matrix() -> dict[str, tuple[float, float, float]]:
    """Return the immutable oracle intervention table in JSON-friendly form."""

    return {
        failure.label: tuple(_INTERVENTION_ACCURACY[failure.value])
        for failure in FailureDepth
    }


def interface_collision_exists() -> bool:
    """Demonstrate the v0.1 impossibility under the old observation interface.

    Two latent states collide under the old one-dimensional observation while
    requiring different actions.  Revision depth 2 reveals the supplied
    second coordinate and resolves that collision.
    """

    latent_states = ((1, 0), (1, 1))

    def old_interface(state: tuple[int, int]) -> tuple[int]:
        return (state[0],)

    def required_action(state: tuple[int, int]) -> int:
        return state[1]

    first, second = latent_states
    return (
        old_interface(first) == old_interface(second)
        and required_action(first) != required_action(second)
    )


def evaluate_revision(
    spec: AgentSpec,
    evidence: DiagnosticEvidence,
    revision_depth: int,
) -> dict[str, float]:
    """Evaluate one committed revision without mutating the agent or evidence.

    Noise is small, deterministic, and outcome-specific.  It represents run
    variability without making results depend on evaluation order.
    """

    if not isinstance(spec, AgentSpec):
        raise TypeError("spec must be an AgentSpec")
    if not isinstance(evidence, DiagnosticEvidence):
        raise TypeError("evidence must be DiagnosticEvidence")

    depth = _coerce_revision_depth(revision_depth)
    sufficient_depth = evidence.failure.value
    under_revision = max(0, sufficient_depth - depth)
    over_revision = max(0, depth - sufficient_depth)

    oracle = oracle_accuracy(evidence.failure, depth)
    execution = float(np.clip(spec.execution_skill, 0.0, 1.0))
    execution_factor = 0.70 + 0.30 * execution

    def noise(name: str, scale: float) -> float:
        generator = _rng(
            spec.seed,
            spec.agent_id,
            evidence.case_id,
            evidence.generator_family,
            depth,
            "outcome",
            name,
        )
        return float(generator.normal(0.0, scale))

    recovery = _clip01(oracle * execution_factor + noise("recovery", 0.008))
    transfer = _clip01(
        0.88 * recovery
        + 0.09 * execution
        - 0.035 * under_revision
        - 0.015 * over_revision
        + noise("transfer", 0.008)
    )
    retention = _clip01(
        0.91 * recovery
        + 0.065 * execution
        - 0.012 * over_revision
        + noise("retention", 0.006)
    )

    # Shallow failed corrections tend to preserve the old behavior; excessive
    # restructuring damages it.  This keeps preservation distinct from
    # recovery and exposes hyperplastic over-revision.
    disruption = (0.008, 0.045, 0.12)[depth] + 0.035 * over_revision
    preservation = _clip01(
        float(np.clip(spec.baseline_q, 0.0, 1.0))
        - disruption
        + 0.008 * under_revision
        + noise("preservation", 0.005)
    )
    correction_cost = max(
        0.0,
        _REVISION_COSTS[depth]
        + 0.35 * under_revision
        + abs(noise("correction-cost", 0.025)),
    )

    return {
        "recovery": recovery,
        "transfer": transfer,
        "retention": retention,
        "preservation": preservation,
        "correction_cost": correction_cost,
    }


def _coerce_failure(value: FailureDepth | int | str) -> FailureDepth:
    if isinstance(value, FailureDepth):
        return value
    if isinstance(value, str):
        try:
            return FailureDepth[value.strip().upper()]
        except KeyError as exc:
            raise ValueError(f"unknown failure depth: {value!r}") from exc
    if isinstance(value, bool):
        raise ValueError(f"unknown failure depth: {value!r}")
    try:
        return FailureDepth(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unknown failure depth: {value!r}") from exc


def _coerce_revision_depth(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise TypeError("revision_depth must be an integer in {0, 1, 2}")
    depth = int(value)
    if depth not in (0, 1, 2):
        raise ValueError("revision_depth must be in {0, 1, 2}")
    return depth


def _clip01(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("outcome value must be finite")
    return float(min(1.0, max(0.0, value)))
