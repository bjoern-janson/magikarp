"""Leakage-resistant predictive analysis for MAGIKARP v0.1.

Adaptation episodes are first collapsed to one row per
``agent_id x generator_family x failure``.  Failure remains a separate stratum
because every generator family deliberately realizes every failure depth; that
crossing prevents generator identity from leaking the label.  The outer
prediction then excludes *both* every row from the test agent and every row
from the test generator family.  This prevents episode replication,
known-agent leakage, and known-generator leakage from masquerading as held-out
predictive gain.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
import math
from typing import Any

import numpy as np

from .types import TrialRecord


_AGGREGATE_NUMERIC_FIELDS = (
    "q",
    "a",
    "e",
    "sd",
    "recovery",
    "transfer",
    "retention",
    "preservation",
    "correction_cost",
)
_FEATURES_M0 = ("q", "a", "e")
_FEATURES_M1 = ("q", "a", "e", "sd")


def _field(record: object, name: str) -> Any:
    if isinstance(record, Mapping):
        try:
            return record[name]
        except KeyError as exc:
            raise ValueError(f"record is missing {name!r}") from exc
    try:
        return getattr(record, name)
    except AttributeError as exc:
        raise ValueError(f"record is missing {name!r}") from exc


def _finite_number(record: object, name: str) -> float:
    try:
        value = float(_field(record, name))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"record field {name!r} must be numeric") from exc
    if not math.isfinite(value):
        raise ValueError(f"record field {name!r} must be finite")
    return value


def _constant(group: Sequence[object], name: str) -> Any:
    values = [_field(record, name) for record in group]
    first = values[0]
    if any(value != first for value in values[1:]):
        raise ValueError(
            f"{name!r} varies within agent_id x generator_family x failure "
            "aggregation cell"
        )
    return first


def _optional_field(record: object, name: str, default: Any) -> Any:
    if isinstance(record, Mapping):
        return record.get(name, default)
    return getattr(record, name, default)


def _agent_group_id(record: object) -> str:
    """Return the independent matched-block ID, with legacy-safe fallback."""

    return str(_optional_field(record, "agent_group_id", _field(record, "agent_id")))


def aggregate_trials(records: Iterable[TrialRecord | Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Collapse episodes to agent-by-generator-by-failure analysis cells.

    ``q``, ``a``, ``e``, ``sd``, recovery, and all decomposed secondary
    outcomes are arithmetic means.  Identity, split, family, and seed labels
    must be invariant inside a cell.  Failure is part of the cell key because
    a valid generator family spans all three failure depths.
    """

    grouped: dict[tuple[str, str, str], list[object]] = defaultdict(list)
    for record in records:
        key = (
            str(_field(record, "agent_id")),
            str(_field(record, "generator_family")),
            str(_field(record, "failure")),
        )
        grouped[key].append(record)

    result: list[dict[str, Any]] = []
    for (agent_id, generator_family, failure), group in sorted(grouped.items()):
        row: dict[str, Any] = {
            "agent_id": agent_id,
            "agent_group_id": _agent_group_id(group[0]),
            "agent_family": str(_constant(group, "agent_family")),
            "seed": int(_constant(group, "seed")),
            "generator_family": generator_family,
            "structural_family_id": str(_constant(group, "structural_family_id")),
            "split": str(_constant(group, "split")),
            "failure": failure,
            "n_trials": len(group),
        }
        if any(_agent_group_id(record) != row["agent_group_id"] for record in group):
            raise ValueError(
                "agent_group_id varies within agent_id x generator_family x failure cell"
            )
        for name in _AGGREGATE_NUMERIC_FIELDS:
            row[name] = math.fsum(_finite_number(record, name) for record in group) / len(
                group
            )
        result.append(row)
    return result


def _validate_aggregated_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    cells: set[tuple[str, str, str]] = set()
    for source in rows:
        row = {
            "agent_id": str(_field(source, "agent_id")),
            "agent_group_id": _agent_group_id(source),
            "generator_family": str(_field(source, "generator_family")),
            "structural_family_id": str(_field(source, "structural_family_id")),
            "failure": str(_field(source, "failure")),
            **{name: _finite_number(source, name) for name in _FEATURES_M1},
            "recovery": _finite_number(source, "recovery"),
        }
        cell = (row["agent_id"], row["generator_family"], row["failure"])
        if cell in cells:
            raise ValueError(
                "prediction input must already contain one row per "
                "agent_id x generator_family x failure; call aggregate_trials first"
            )
        cells.add(cell)
        prepared.append(row)
    if not prepared:
        raise ValueError("at least one aggregated trial row is required")
    return prepared


def _ridge_predictions(
    train_features: np.ndarray,
    train_targets: np.ndarray,
    test_features: np.ndarray,
    *,
    alpha: float,
) -> np.ndarray:
    design = np.column_stack((np.ones(train_features.shape[0]), train_features))
    test_design = np.column_stack((np.ones(test_features.shape[0]), test_features))
    penalty = np.eye(design.shape[1], dtype=float) * alpha
    penalty[0, 0] = 0.0  # Never penalize the intercept.
    normal_matrix = design.T @ design + penalty
    right_hand_side = design.T @ train_targets
    try:
        coefficients = np.linalg.solve(normal_matrix, right_hand_side)
    except np.linalg.LinAlgError:
        coefficients = np.linalg.lstsq(normal_matrix, right_hand_side, rcond=None)[0]
    return np.asarray(test_design @ coefficients, dtype=float)


def _prediction_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    mae_m0 = math.fsum(float(row["abs_error_m0"]) for row in rows) / len(rows)
    mae_m1 = math.fsum(float(row["abs_error_m1"]) for row in rows) / len(rows)
    return {
        "mae_m0": mae_m0,
        "mae_m1": mae_m1,
        "delta_mae": mae_m0 - mae_m1,
        "n_rows": len(rows),
        "n_agents": len({str(row["agent_id"]) for row in rows}),
        "n_agent_groups": len({str(row["agent_group_id"]) for row in rows}),
        "n_generator_families": len(
            {str(row["generator_family"]) for row in rows}
        ),
        "n_structural_families": len(
            {str(row["structural_family_id"]) for row in rows}
        ),
    }


def paired_group_bootstrap(
    prediction_rows: Iterable[Mapping[str, Any]],
    *,
    unit: str = "generator_family",
    confidence: float = 0.95,
    n_bootstrap: int = 2_000,
    seed: int = 0,
) -> dict[str, Any]:
    """Bootstrap paired M0-minus-M1 losses at a frozen independent unit.

    ``unit`` may be ``generator_family``, ``agent`` (the independent matched
    block, not a crossed composite), or ``checkpoint`` (the composite
    ``agent_id`` in this synthetic v0.1).  Loss differences are first averaged
    within the selected unit.  Whole unit means are then sampled with
    replacement, retaining the paired predictions from both models.
    """

    try:
        validated_replicates = int(n_bootstrap)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("n_bootstrap must be a positive integer") from exc
    if (
        isinstance(n_bootstrap, bool)
        or validated_replicates != n_bootstrap
        or validated_replicates < 1
    ):
        raise ValueError("n_bootstrap must be a positive integer")
    n_bootstrap = validated_replicates
    try:
        confidence = float(confidence)
    except (TypeError, ValueError) as exc:
        raise ValueError("confidence must be strictly between 0 and 1") from exc
    if not math.isfinite(confidence) or not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be strictly between 0 and 1")
    group_fields = {
        "generator_family": "generator_family",
        "agent": "agent_group_id",
        "checkpoint": "agent_id",
    }
    if unit not in group_fields:
        raise ValueError(
            "bootstrap unit must be generator_family, agent, or checkpoint"
        )
    group_field = group_fields[unit]
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in prediction_rows:
        group = str(_field(row, group_field))
        difference = _finite_number(row, "abs_error_m0") - _finite_number(
            row, "abs_error_m1"
        )
        grouped[group].append(difference)
    if not grouped:
        raise ValueError("at least one prediction row is required")

    groups = sorted(grouped)
    group_deltas = np.asarray(
        [math.fsum(grouped[group]) / len(grouped[group]) for group in groups],
        dtype=float,
    )
    rng = np.random.default_rng(seed)
    sampled_indices = rng.integers(
        0, len(group_deltas), size=(n_bootstrap, len(group_deltas))
    )
    replicates = group_deltas[sampled_indices].mean(axis=1)
    tail = (1.0 - confidence) / 2.0
    low, high = np.quantile(replicates, [tail, 1.0 - tail])
    result = {
        "estimate": float(group_deltas.mean()),
        "confidence_interval": [float(low), float(high)],
        "confidence": confidence,
        "n_bootstrap": n_bootstrap,
        "seed": int(seed),
        "unit": unit,
        "group_field": group_field,
        "n_groups": len(groups),
    }
    if math.isclose(confidence, 0.95, rel_tol=0.0, abs_tol=1e-12):
        result["ci95"] = result["confidence_interval"]
    return result


def paired_generator_bootstrap(
    prediction_rows: Iterable[Mapping[str, Any]],
    *,
    n_bootstrap: int = 2_000,
    seed: int = 0,
) -> dict[str, Any]:
    """Backward-compatible 95% generator-family bootstrap wrapper."""

    result = paired_group_bootstrap(
        prediction_rows,
        unit="generator_family",
        confidence=0.95,
        n_bootstrap=n_bootstrap,
        seed=seed,
    )
    result["n_generator_families"] = result["n_groups"]
    return result


def grouped_outer_prediction(
    rows: Iterable[Mapping[str, Any]],
    *,
    ridge_alpha: float = 1.0,
    bootstrap_unit: str = "generator_family",
    bootstrap_confidence: float = 0.95,
    n_bootstrap: int = 2_000,
    seed: int = 0,
) -> dict[str, Any]:
    """Compare M0 and M1 under two-way leave-group-out prediction.

    Input must be the output of :func:`aggregate_trials`.  For every test cell
    ``(independent agent block, generator)``, training excludes the union of
    that block's rows and that generator family's rows across all composites
    and failures. Shared features receive exactly the same training-only
    centering/scaling in both ridge models:

    ``M0: recovery ~ q + a + e``
    ``M1: recovery ~ q + a + e + sd``

    The result contains per-cell predictions plus MAE summaries and a paired
    generator-family bootstrap interval for ``MAE(M0) - MAE(M1)``.
    """

    try:
        ridge_alpha = float(ridge_alpha)
    except (TypeError, ValueError) as exc:
        raise ValueError("ridge_alpha must be a non-negative finite number") from exc
    if not math.isfinite(ridge_alpha) or ridge_alpha < 0.0:
        raise ValueError("ridge_alpha must be a non-negative finite number")

    prepared = _validate_aggregated_rows(rows)
    agent_groups = {row["agent_group_id"] for row in prepared}
    generators = {row["generator_family"] for row in prepared}
    if len(agent_groups) < 2 or len(generators) < 2:
        raise ValueError(
            "two-way outer prediction requires at least two independent agent "
            "groups and two generator families"
        )

    all_features = np.asarray(
        [[row[name] for name in _FEATURES_M1] for row in prepared], dtype=float
    )
    all_targets = np.asarray([row["recovery"] for row in prepared], dtype=float)
    predictions_by_index: list[dict[str, Any] | None] = [None] * len(prepared)
    outer_folds: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(prepared):
        outer_folds[(row["agent_group_id"], row["generator_family"])].append(index)

    # All cells in one block x generator fold share a training partition. Fit
    # once per partition, then predict every composite/failure cell in a batch.
    # This makes the frozen evidence template operationally tractable without
    # changing a single held-out prediction.
    for (test_agent_group, test_generator), test_indices in sorted(outer_folds.items()):
        train_indices = [
            index
            for index, candidate in enumerate(prepared)
            if candidate["agent_group_id"] != test_agent_group
            and candidate["generator_family"] != test_generator
        ]
        if not train_indices:
            raise ValueError(
                "a two-way outer fold has no training rows; provide a denser "
                "agent x generator design"
            )

        train_raw = all_features[train_indices]
        test_raw = all_features[test_indices]
        means = train_raw.mean(axis=0)
        scales = train_raw.std(axis=0)
        scales = np.where(scales > np.finfo(float).eps, scales, 1.0)
        train_scaled = (train_raw - means) / scales
        test_scaled = (test_raw - means) / scales
        train_targets = all_targets[train_indices]

        pred_m0 = _ridge_predictions(
            train_scaled[:, : len(_FEATURES_M0)],
            train_targets,
            test_scaled[:, : len(_FEATURES_M0)],
            alpha=ridge_alpha,
        )
        pred_m1 = _ridge_predictions(
            train_scaled,
            train_targets,
            test_scaled,
            alpha=ridge_alpha,
        )
        for offset, test_index in enumerate(test_indices):
            test_row = prepared[test_index]
            y_true = float(all_targets[test_index])
            prediction_m0 = float(pred_m0[offset])
            prediction_m1 = float(pred_m1[offset])
            predictions_by_index[test_index] = {
                "agent_id": test_row["agent_id"],
                "agent_group_id": test_row["agent_group_id"],
                "generator_family": test_row["generator_family"],
                "structural_family_id": test_row["structural_family_id"],
                "failure": test_row["failure"],
                "y_true": y_true,
                "pred_m0": prediction_m0,
                "pred_m1": prediction_m1,
                "abs_error_m0": abs(y_true - prediction_m0),
                "abs_error_m1": abs(y_true - prediction_m1),
                "train_rows": len(train_indices),
            }

    if any(row is None for row in predictions_by_index):
        raise RuntimeError("outer prediction failed to populate every held-out row")
    predictions = [row for row in predictions_by_index if row is not None]

    summary = _prediction_summary(predictions)
    per_failure: dict[str, dict[str, Any]] = {}
    for failure in sorted({row["failure"] for row in predictions}):
        per_failure[failure] = _prediction_summary(
            [row for row in predictions if row["failure"] == failure]
        )
    bootstrap = paired_group_bootstrap(
        predictions,
        unit=bootstrap_unit,
        confidence=bootstrap_confidence,
        n_bootstrap=n_bootstrap,
        seed=seed,
    )
    summary.update(
        {
            "evaluated": True,
            "confidence_interval": bootstrap["confidence_interval"],
            "confidence_level": bootstrap["confidence"],
            "per_failure": per_failure,
            "bootstrap": bootstrap,
            "ridge_alpha": ridge_alpha,
            "outer_scheme": "leave-one-independent-agent-block-and-generator-family-out",
        }
    )
    if "ci95" in bootstrap:
        summary["ci95"] = bootstrap["ci95"]
    return {"predictions": predictions, "summary": summary}


__all__ = [
    "aggregate_trials",
    "grouped_outer_prediction",
    "paired_group_bootstrap",
    "paired_generator_bootstrap",
]
