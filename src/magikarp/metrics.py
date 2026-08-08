"""Prospective diagnostic metrics for MAGIKARP v0.1.

The frozen primary ``SD`` metric is the normalized negative multiclass Brier
loss.  Class-balanced skill, top-1 accuracy, per-class recall, and entropy are
reported as diagnostic robustness summaries; none of them replaces ``SD``.

All functions operate only on ``failure`` and the pre-adaptation ``q_sd``
distribution.  Adaptation outcomes are deliberately outside this module.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
import math
from typing import Any

from .types import FailureDepth


FAILURE_LABELS: tuple[str, str, str] = ("parameter", "model", "interface")
_LABEL_TO_INDEX = {label: index for index, label in enumerate(FAILURE_LABELS)}


def _field(record: object, name: str) -> Any:
    if isinstance(record, Mapping):
        try:
            return record[name]
        except KeyError as exc:
            raise ValueError(f"diagnostic record is missing {name!r}") from exc
    try:
        return getattr(record, name)
    except AttributeError as exc:
        raise ValueError(f"diagnostic record is missing {name!r}") from exc


def _failure_label(value: object) -> str:
    if isinstance(value, FailureDepth):
        return value.label
    label = str(value).lower()
    if label not in _LABEL_TO_INDEX:
        raise ValueError(
            f"unknown failure label {value!r}; expected one of {FAILURE_LABELS}"
        )
    return label


def _probabilities(value: object) -> tuple[float, float, float]:
    try:
        probabilities = tuple(float(item) for item in value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError("q_sd must be a sequence of three probabilities") from exc
    if len(probabilities) != len(FAILURE_LABELS):
        raise ValueError("q_sd must contain exactly three probabilities")
    if not all(math.isfinite(item) and item >= 0.0 for item in probabilities):
        raise ValueError("q_sd probabilities must be finite and non-negative")
    total = math.fsum(probabilities)
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-8):
        raise ValueError(f"q_sd probabilities must sum to 1 (got {total!r})")
    # Remove harmless floating-point drift so downstream metrics share one
    # exactly normalized representation.
    return tuple(item / total for item in probabilities)  # type: ignore[return-value]


def _examples(records: Iterable[object]) -> list[tuple[str, tuple[float, float, float]]]:
    examples = [
        (_failure_label(_field(record, "failure")), _probabilities(_field(record, "q_sd")))
        for record in records
    ]
    if not examples:
        raise ValueError("at least one diagnostic record is required")
    return examples


def _brier_loss(label: str, probabilities: Sequence[float]) -> float:
    target = _LABEL_TO_INDEX[label]
    return math.fsum(
        (probability - (1.0 if index == target else 0.0)) ** 2
        for index, probability in enumerate(probabilities)
    )


def normalized_brier_sd(records: Iterable[object]) -> float:
    """Return the frozen primary scalar ``SD`` in the inclusive range [0, 1].

    For ``N`` records this implements exactly

    ``1 - sum(||q_sd - one_hot(F)||^2) / (2 * N)``.

    Records may be dataclass instances (including ``DiagnosticRecord`` or
    ``TrialRecord``) or mappings with ``failure`` and ``q_sd`` fields.
    """

    examples = _examples(records)
    mean_loss = math.fsum(_brier_loss(label, q_sd) for label, q_sd in examples) / len(
        examples
    )
    return 1.0 - mean_loss / 2.0


def empirical_failure_prior(records: Iterable[object]) -> dict[str, float]:
    """Return the empirical diagnostic-label prior in canonical class order."""

    examples = _examples(records)
    counts = Counter(label for label, _ in examples)
    return {label: counts[label] / len(examples) for label in FAILURE_LABELS}


def _prior_vector(
    examples: Sequence[tuple[str, tuple[float, float, float]]],
    prior: Mapping[str, float] | Sequence[float] | None,
) -> tuple[float, float, float]:
    if prior is None:
        counts = Counter(label for label, _ in examples)
        values = tuple(counts[label] / len(examples) for label in FAILURE_LABELS)
    elif isinstance(prior, Mapping):
        missing = [label for label in FAILURE_LABELS if label not in prior]
        if missing:
            raise ValueError(f"prior is missing failure classes: {missing}")
        values = tuple(float(prior[label]) for label in FAILURE_LABELS)
    else:
        try:
            values = tuple(float(item) for item in prior)
        except (TypeError, ValueError) as exc:
            raise ValueError("prior must contain three probabilities") from exc

    if len(values) != len(FAILURE_LABELS):
        raise ValueError("prior must contain exactly three probabilities")
    if not all(math.isfinite(item) and item >= 0.0 for item in values):
        raise ValueError("prior probabilities must be finite and non-negative")
    total = math.fsum(values)
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-8):
        raise ValueError(f"prior probabilities must sum to 1 (got {total!r})")
    return tuple(item / total for item in values)  # type: ignore[return-value]


def _macro_class_brier_loss(
    examples: Sequence[tuple[str, tuple[float, float, float]]],
    *,
    constant_prediction: Sequence[float] | None = None,
) -> float:
    losses: dict[str, list[float]] = defaultdict(list)
    for label, probabilities in examples:
        prediction = constant_prediction if constant_prediction is not None else probabilities
        losses[label].append(_brier_loss(label, prediction))
    # Average within true class first, so class-frequency imbalance cannot make
    # the easiest or most common failure depth dominate this robustness metric.
    return math.fsum(
        math.fsum(class_losses) / len(class_losses) for class_losses in losses.values()
    ) / len(losses)


def class_balanced_brier_skill_score(
    records: Iterable[object],
    prior: Mapping[str, float] | Sequence[float] | None = None,
) -> float:
    """Return class-balanced Brier skill relative to a prior-only predictor.

    ``1`` is perfect, ``0`` matches the reference prior, and negative values
    are worse than that prior.  If ``prior`` is omitted, the empirical label
    prior is used.  Evidence-bearing runs should pass a prior frozen from
    training/diagnostic design data rather than estimating it on a held-out
    evaluation set.

    Classes absent from the supplied records are not fabricated: macro
    balancing is over the observed true classes, while the prediction vector
    always retains all three frozen failure depths.
    """

    examples = _examples(records)
    reference = _prior_vector(examples, prior)
    observed_loss = _macro_class_brier_loss(examples)
    reference_loss = _macro_class_brier_loss(examples, constant_prediction=reference)
    if reference_loss <= 0.0:
        if observed_loss <= 0.0:
            return 0.0
        raise ValueError("Brier skill is undefined for a zero-loss reference prior")
    return 1.0 - observed_loss / reference_loss


def diagnostic_summary(
    records: Iterable[object],
    prior: Mapping[str, float] | Sequence[float] | None = None,
) -> dict[str, Any]:
    """Return JSON-friendly primary and diagnostic robustness summaries.

    ``sd`` is the preregistered primary metric.  ``brier_skill_class_balanced``
    and the classification/entropy fields are explicitly secondary checks.
    Entropy is reported both in nats and normalized by ``log(3)``.
    """

    examples = _examples(records)
    reference = _prior_vector(examples, prior)
    correct = 0
    entropy_values: list[float] = []
    class_counts = Counter(label for label, _ in examples)
    class_correct = Counter()

    for label, probabilities in examples:
        prediction = FAILURE_LABELS[max(range(len(probabilities)), key=probabilities.__getitem__)]
        if prediction == label:
            correct += 1
            class_correct[label] += 1
        entropy_values.append(
            -math.fsum(value * math.log(value) for value in probabilities if value > 0.0)
        )

    observed_loss = _macro_class_brier_loss(examples)
    reference_loss = _macro_class_brier_loss(examples, constant_prediction=reference)
    if reference_loss <= 0.0:
        skill = 0.0 if observed_loss <= 0.0 else None
    else:
        skill = 1.0 - observed_loss / reference_loss

    mean_entropy = math.fsum(entropy_values) / len(entropy_values)
    return {
        "n_records": len(examples),
        "sd": 1.0
        - math.fsum(_brier_loss(label, q_sd) for label, q_sd in examples)
        / (2.0 * len(examples)),
        "top1_accuracy": correct / len(examples),
        "per_class": {
            label: {
                "n": class_counts[label],
                "recall": (
                    class_correct[label] / class_counts[label]
                    if class_counts[label]
                    else None
                ),
            }
            for label in FAILURE_LABELS
        },
        "mean_entropy_nats": mean_entropy,
        "mean_entropy_normalized": mean_entropy / math.log(len(FAILURE_LABELS)),
        "brier_skill_class_balanced": skill,
        "class_balanced_brier_loss": observed_loss,
        "reference_class_balanced_brier_loss": reference_loss,
        "reference_prior": {
            label: reference[index] for index, label in enumerate(FAILURE_LABELS)
        },
        "reference_prior_source": "empirical" if prior is None else "frozen",
    }


__all__ = [
    "FAILURE_LABELS",
    "class_balanced_brier_skill_score",
    "diagnostic_summary",
    "empirical_failure_prior",
    "normalized_brier_sd",
]
