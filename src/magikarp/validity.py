"""Machine-readable benchmark-validity gates for MAGIKARP v0.1."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import numpy as np

from .types import DiagnosticRecord, FailureDepth, TrialRecord


_FAILURES = ("parameter", "model", "interface")
_REQUIRED_FAMILIES = ("rigid", "hyperplastic", "depth_aware")


def _failure_name(value: Any) -> str | None:
    if isinstance(value, FailureDepth):
        return value.label
    if isinstance(value, int) and not isinstance(value, bool):
        return {0: "parameter", 1: "model", 2: "interface"}.get(value)
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace("-", "_")
    if normalized.startswith("failuredepth."):
        normalized = normalized.split(".", 1)[1]
    aliases = {
        "parameter": "parameter",
        "f_p": "parameter",
        "fp": "parameter",
        "p": "parameter",
        "model": "model",
        "f_m": "model",
        "fm": "model",
        "m": "model",
        "interface": "interface",
        "f_i": "interface",
        "fi": "interface",
        "i": "interface",
    }
    return aliases.get(normalized)


def _depth(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value in {0, 1, 2}:
        return value
    name = _failure_name(value)
    return {"parameter": 0, "model": 1, "interface": 2}.get(name) if name else None


def _finite(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _entry_success(entry: Any, threshold: float) -> bool:
    if isinstance(entry, Mapping):
        for key in ("solvable", "success", "passed"):
            if key in entry:
                return bool(entry[key])
        for key in ("recovery", "score", "performance"):
            if key in entry:
                value = _finite(entry[key])
                return value is not None and value >= threshold
        return False
    if isinstance(entry, bool):
        return entry
    value = _finite(entry)
    return value is not None and value >= threshold


def _matrix_rows(
    intervention_matrix: Mapping[Any, Any], success_threshold: float
) -> dict[str, dict[int, bool]]:
    rows: dict[str, dict[int, bool]] = {failure: {} for failure in _FAILURES}
    if not isinstance(intervention_matrix, Mapping):
        return rows
    for raw_failure, raw_row in intervention_matrix.items():
        failure = _failure_name(raw_failure)
        if failure is None:
            continue
        if isinstance(raw_row, Mapping):
            entries = raw_row.items()
        elif isinstance(raw_row, Sequence) and not isinstance(
            raw_row, (str, bytes, bytearray)
        ):
            entries = enumerate(raw_row)
        else:
            continue
        for raw_depth, entry in entries:
            depth = _depth(raw_depth)
            if depth is not None:
                rows[failure][depth] = _entry_success(entry, success_threshold)
    return rows


def _gate(
    name: str,
    passed: bool,
    details: dict[str, Any],
) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "details": details}


def _gate_a(
    rows: dict[str, dict[int, bool]], thresholds: Mapping[str, Any]
) -> dict[str, Any]:
    expected = thresholds["intervention_minima"]
    observed: dict[str, int | None] = {}
    success_by_depth: dict[str, dict[str, bool]] = {}
    for failure in _FAILURES:
        row = rows[failure]
        solvable = [depth for depth, success in row.items() if success]
        observed[failure] = min(solvable) if solvable else None
        success_by_depth[failure] = {
            str(depth): bool(row.get(depth, False)) for depth in range(3)
        }
    passed = all(observed[failure] == expected[failure] for failure in _FAILURES)
    return _gate(
        "failure-depth intervention minima",
        passed,
        {
            "expected_minima": dict(expected),
            "observed_minima": observed,
            "success_by_depth": success_by_depth,
        },
    )


def _gate_b(
    rows: dict[str, dict[int, bool]], interface_collision: bool
) -> dict[str, Any]:
    interface = rows["interface"]
    old_interface_unsolvable = not interface.get(0, False) and not interface.get(1, False)
    expansion_solvable = interface.get(2, False)
    passed = (
        interface_collision is True
        and old_interface_unsolvable
        and expansion_solvable
    )
    return _gate(
        "interface impossibility",
        passed,
        {
            "interface_collision": interface_collision is True,
            "parameter_or_model_revision_unsolvable": old_interface_unsolvable,
            "interface_expansion_solvable": expansion_solvable,
        },
    )


def _diagnostic_arrays(
    records: Sequence[DiagnosticRecord],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    labels: list[int] = []
    probabilities: list[tuple[float, float, float]] = []
    nuisance: list[tuple[float, float, float]] = []
    invalid = 0
    for record in records:
        failure = _failure_name(record.failure)
        if failure is None or len(record.q_sd) != 3 or len(record.nuisance) != 3:
            invalid += 1
            continue
        q = tuple(_finite(value) for value in record.q_sd)
        x = tuple(_finite(value) for value in record.nuisance)
        if any(value is None for value in q + x):
            invalid += 1
            continue
        q_values = tuple(float(value) for value in q if value is not None)
        x_values = tuple(float(value) for value in x if value is not None)
        if any(value < 0.0 or value > 1.0 for value in q_values):
            invalid += 1
            continue
        if not math.isclose(sum(q_values), 1.0, rel_tol=0.0, abs_tol=1e-6):
            invalid += 1
            continue
        labels.append(_FAILURES.index(failure))
        probabilities.append(q_values)  # type: ignore[arg-type]
        nuisance.append(x_values)  # type: ignore[arg-type]
    return (
        np.asarray(labels, dtype=int),
        np.asarray(probabilities, dtype=float),
        np.asarray(nuisance, dtype=float),
        invalid,
    )


def _gate_c(
    records: Sequence[DiagnosticRecord], thresholds: Mapping[str, Any]
) -> dict[str, Any]:
    labels, probabilities, _, invalid = _diagnostic_arrays(records)
    counts = {failure: int(np.sum(labels == index)) for index, failure in enumerate(_FAILURES)}
    if labels.size == 0:
        return _gate(
            "diagnostic identifiability",
            False,
            {"record_count": 0, "invalid_records": invalid, "class_counts": counts},
        )
    predictions = np.argmax(probabilities, axis=1)
    accuracy = float(np.mean(predictions == labels))
    recalls = {
        failure: (
            float(np.mean(predictions[labels == index] == index))
            if counts[failure]
            else None
        )
        for index, failure in enumerate(_FAILURES)
    }
    min_accuracy = float(thresholds["diagnostic_min_top1_accuracy"])
    min_recall = float(thresholds["diagnostic_min_class_recall"])
    passed = (
        invalid == 0
        and all(counts[failure] > 0 for failure in _FAILURES)
        and accuracy >= min_accuracy
        and all(value is not None and value >= min_recall for value in recalls.values())
    )
    return _gate(
        "diagnostic identifiability",
        passed,
        {
            "record_count": int(labels.size),
            "invalid_records": invalid,
            "class_counts": counts,
            "top1_accuracy": accuracy,
            "class_recall": recalls,
            "minimum_top1_accuracy": min_accuracy,
            "minimum_class_recall": min_recall,
        },
    )


def _leave_one_out_centroid_accuracy(features: np.ndarray, labels: np.ndarray) -> float:
    if features.shape[0] != labels.size or labels.size == 0:
        return float("nan")
    predictions: list[int] = []
    for held_out in range(labels.size):
        available = np.arange(labels.size) != held_out
        candidates: list[tuple[float, int]] = []
        for label in range(len(_FAILURES)):
            members = features[available & (labels == label)]
            if members.size == 0:
                continue
            centroid = np.mean(members, axis=0)
            distance = float(np.sum((features[held_out] - centroid) ** 2))
            candidates.append((distance, label))
        predictions.append(min(candidates)[1] if candidates else -1)
    return float(np.mean(np.asarray(predictions, dtype=int) == labels))


def _gate_d(
    records: Sequence[DiagnosticRecord], thresholds: Mapping[str, Any]
) -> dict[str, Any]:
    labels, _, nuisance, invalid = _diagnostic_arrays(records)
    counts = np.bincount(labels, minlength=len(_FAILURES)) if labels.size else np.zeros(3, dtype=int)
    enough = labels.size > 0 and bool(np.all(counts >= 2)) and invalid == 0
    if not enough:
        return _gate(
            "nuisance-only leakage audit",
            False,
            {
                "record_count": int(labels.size),
                "invalid_records": invalid,
                "class_counts": {
                    failure: int(counts[index]) for index, failure in enumerate(_FAILURES)
                },
                "reason": "at least two valid records per failure class are required",
            },
        )

    observed = _leave_one_out_centroid_accuracy(nuisance, labels)
    rng = np.random.default_rng(int(thresholds["nuisance_seed"]))
    permutation_scores = np.asarray(
        [
            _leave_one_out_centroid_accuracy(nuisance, rng.permutation(labels))
            for _ in range(int(thresholds["nuisance_permutations"]))
        ],
        dtype=float,
    )
    quantile = float(
        np.quantile(permutation_scores, float(thresholds["nuisance_permutation_quantile"]))
    )
    limit = max(
        float(thresholds["nuisance_max_accuracy"]),
        quantile + float(thresholds["nuisance_permutation_margin"]),
    )
    passed = math.isfinite(observed) and observed <= limit
    return _gate(
        "nuisance-only leakage audit",
        passed,
        {
            "record_count": int(labels.size),
            "invalid_records": invalid,
            "classifier": "leave_one_out_nearest_centroid",
            "observed_accuracy": observed,
            "permutation_mean_accuracy": float(np.mean(permutation_scores)),
            "permutation_quantile_accuracy": quantile,
            "allowed_accuracy": limit,
            "permutations": int(permutation_scores.size),
        },
    )


def _gate_e(
    records: Sequence[TrialRecord], thresholds: Mapping[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[float]] = defaultdict(list)
    invalid = 0
    for record in records:
        if record.agent_family not in _REQUIRED_FAMILIES:
            continue
        q = _finite(record.q)
        if q is None:
            invalid += 1
        else:
            grouped[record.agent_family].append(q)
    counts = {family: len(grouped[family]) for family in _REQUIRED_FAMILIES}
    means = {
        family: (float(np.mean(grouped[family])) if grouped[family] else None)
        for family in _REQUIRED_FAMILIES
    }
    minimum_count = int(thresholds["q_min_records_per_family"])
    complete = all(counts[family] >= minimum_count for family in _REQUIRED_FAMILIES)
    finite_means = [value for value in means.values() if value is not None]
    mean_gap = max(finite_means) - min(finite_means) if len(finite_means) == 3 else None
    maximum_gap = float(thresholds["q_max_family_mean_gap"])
    passed = invalid == 0 and complete and mean_gap is not None and mean_gap <= maximum_gap
    return _gate(
        "baseline competence overlap",
        passed,
        {
            "required_families": list(_REQUIRED_FAMILIES),
            "records_per_family": counts,
            "family_mean_Q": means,
            "invalid_records": invalid,
            "minimum_records_per_family": minimum_count,
            "maximum_family_mean_gap": maximum_gap,
            "observed_family_mean_gap": mean_gap,
        },
    )


def _gate_f(
    records: Sequence[TrialRecord], thresholds: Mapping[str, Any]
) -> dict[str, Any]:
    matched: dict[str, list[float]] = defaultdict(list)
    over: dict[str, list[float]] = defaultdict(list)
    invalid = 0
    deep_success = False
    success_threshold = float(thresholds["intervention_success_min"])
    for record in records:
        failure = _failure_name(record.failure)
        depth = _depth(record.d_revision)
        cost = _finite(record.correction_cost)
        recovery = _finite(record.recovery)
        if failure is None or depth is None or cost is None or recovery is None:
            invalid += 1
            continue
        sufficient = _FAILURES.index(failure)
        if depth == sufficient:
            matched[failure].append(cost)
        elif depth > sufficient:
            over[failure].append(cost)
        if failure == "interface" and depth == 2 and recovery >= success_threshold:
            deep_success = True

    excess_by_failure: dict[str, float] = {}
    for failure in _FAILURES:
        if matched[failure] and over[failure]:
            excess_by_failure[failure] = float(
                np.mean(over[failure]) - np.mean(matched[failure])
            )
    minimum_gap = float(thresholds["cost_asymmetry_min_gap"])
    minimum_observed = min(excess_by_failure.values()) if excess_by_failure else None
    passed = (
        invalid == 0
        and bool(excess_by_failure)
        and minimum_observed is not None
        and minimum_observed >= minimum_gap
        and deep_success
    )
    return _gate(
        "revision-cost asymmetry",
        passed,
        {
            "matched_counts": {failure: len(matched[failure]) for failure in _FAILURES},
            "over_revision_counts": {failure: len(over[failure]) for failure in _FAILURES},
            "over_revision_cost_excess_by_failure": excess_by_failure,
            "minimum_observed_cost_excess": minimum_observed,
            "required_cost_excess": minimum_gap,
            "sufficient_interface_revision_recovers": deep_success,
            "invalid_records": invalid,
        },
    )


def evaluate_validity(
    diagnostic_records: Iterable[DiagnosticRecord],
    trial_records: Iterable[TrialRecord],
    intervention_matrix: Mapping[Any, Any],
    interface_collision: bool,
    thresholds: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate the six frozen v0.1 benchmark-validity gates.

    The return value is JSON-compatible and deliberately separates gate
    outcomes from details so runners never need to infer validity from prose.
    """

    diagnostics = tuple(diagnostic_records)
    trials = tuple(trial_records)
    required = {
        "intervention_success_min",
        "intervention_minima",
        "diagnostic_min_top1_accuracy",
        "diagnostic_min_class_recall",
        "nuisance_max_accuracy",
        "nuisance_permutation_margin",
        "nuisance_permutation_quantile",
        "nuisance_permutations",
        "nuisance_seed",
        "q_max_family_mean_gap",
        "q_min_records_per_family",
        "cost_asymmetry_min_gap",
    }
    missing = sorted(required.difference(thresholds))
    if missing:
        raise ValueError(f"validity thresholds missing: {', '.join(missing)}")

    rows = _matrix_rows(
        intervention_matrix,
        float(thresholds["intervention_success_min"]),
    )
    gates = {
        "A": _gate_a(rows, thresholds),
        "B": _gate_b(rows, interface_collision),
        "C": _gate_c(diagnostics, thresholds),
        "D": _gate_d(diagnostics, thresholds),
        "E": _gate_e(trials, thresholds),
        "F": _gate_f(trials, thresholds),
    }
    return {
        "all_passed": all(gate["passed"] for gate in gates.values()),
        "gates": gates,
    }
