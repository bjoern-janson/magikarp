"""Frozen configuration templates for the MAGIKARP v0.1 benchmark.

The templates deliberately keep every evidence-bearing numerical choice in
JSON.  Callers may extend the dictionaries with task-specific, JSON-compatible
fields, but the governance fields validated here may not be omitted.
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Any


CONFIG_VERSION = 2
_MODES = frozenset({"smoke", "evidence"})
_SPLITS = (
    "baseline",
    "standard_adaptation",
    "diagnostic",
    "adaptation",
    "transfer",
)
_COUNTS = (
    "agents_per_family",
    "baseline_cases",
    "standard_adaptation_cases",
    "diagnostic_cases_per_failure",
    "adaptation_cases_per_failure",
    "transfer_cases_per_failure",
)
_DIAGNOSTIC_SKILL_LEVELS = (0.25, 0.55, 0.85)
_CONTROLLERS = (
    "rigid",
    "hyperplastic",
    "depth_aware",
    "evidence_heuristic",
)
_GENERATOR_SCOPE = {
    "implementation": "builtin_latent_context_v0.1",
    "family_labels": "namespaced_buckets_single_generator",
    "structurally_distinct_families": False,
    "external_families": False,
    "evidence_ready": False,
}


def _template(mode: str) -> dict[str, Any]:
    evidence = mode == "evidence"
    return {
        "config_version": CONFIG_VERSION,
        "mode": mode,
        "run_id": (
            "magikarp-v0.1-evidence-001" if evidence else "magikarp-v0.1-smoke"
        ),
        "split_namespaces": {
            "baseline": "magikarp-v0.1/baseline",
            "standard_adaptation": "magikarp-v0.1/standard-adaptation",
            "diagnostic": "magikarp-v0.1/diagnostic",
            "adaptation": "magikarp-v0.1/held-out-adaptation",
            "transfer": "magikarp-v0.1/transfer-retention",
        },
        "seeds": {
            "agents": [1103, 2203, 3301] if evidence else [1103],
            "baseline": [4001, 4003, 4007] if evidence else [4001],
            "standard_adaptation": [5003, 5009, 5011] if evidence else [5003],
            "diagnostic": [6007, 6011, 6029] if evidence else [6007],
            "adaptation": [7001, 7013, 7019] if evidence else [7001],
            "transfer": [8009, 8011, 8017] if evidence else [8009],
        },
        "sample_counts": {
            "agents_per_family": 12 if evidence else 2,
            "baseline_cases": 60 if evidence else 9,
            "standard_adaptation_cases": 60 if evidence else 9,
            "diagnostic_cases_per_failure": 40 if evidence else 3,
            "adaptation_cases_per_failure": 40 if evidence else 3,
            "transfer_cases_per_failure": 24 if evidence else 3,
        },
        "agent_population": {
            "diagnostic_skill_levels": list(_DIAGNOSTIC_SKILL_LEVELS),
            "controllers": list(_CONTROLLERS),
        },
        "generator_scope": dict(_GENERATOR_SCOPE),
        "thresholds": {
            "intervention_success_min": 0.80,
            "intervention_minima": {
                "parameter": 0,
                "model": 1,
                "interface": 2,
            },
            "diagnostic_min_top1_accuracy": 0.60,
            "diagnostic_min_class_recall": 0.50,
            "nuisance_max_accuracy": 0.55,
            "nuisance_permutation_margin": 0.05,
            "nuisance_permutation_quantile": 0.95,
            "nuisance_permutations": 1000 if evidence else 64,
            "nuisance_seed": 9011,
            "q_max_family_mean_gap": 0.10,
            "q_min_records_per_family": 3 if evidence else 1,
            "cost_asymmetry_min_gap": 0.25,
            "positive_min_delta_mae": 0.005 if evidence else 0.0,
            "positive_require_ci_lower_bound": True,
        },
        "ridge": {
            "alpha": 1.0,
            "alphas": [0.0, 0.01, 0.1, 1.0, 10.0],
            "folds": 5 if evidence else 3,
            "selection_metric": "mae",
        },
        "bootstrap": {
            "replicates": 4000 if evidence else 200,
            "confidence": 0.95,
            "seed": 10007,
            "unit": "generator_family",
        },
    }


def smoke_config() -> dict[str, Any]:
    """Return an independent, validated smoke-run configuration."""

    config = _template("smoke")
    validate_config(config)
    return copy.deepcopy(config)


def evidence_config() -> dict[str, Any]:
    """Return the evidence-run template to freeze in a run manifest."""

    config = _template("evidence")
    validate_config(config)
    return copy.deepcopy(config)


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a UTF-8 JSON configuration file."""

    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load config {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("configuration root must be a JSON object")
    validate_config(value)
    return value


def _require_mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _number(value: Any, path: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{path} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{path} must be finite")
    if minimum is not None and result < minimum:
        raise ValueError(f"{path} must be >= {minimum}")
    return result


def _integer(value: Any, path: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path} must be an integer")
    if value < minimum:
        raise ValueError(f"{path} must be >= {minimum}")
    return value


def _probability(value: Any, path: str) -> float:
    result = _number(value, path)
    if not 0.0 <= result <= 1.0:
        raise ValueError(f"{path} must be between 0 and 1")
    return result


def validate_config(config: dict[str, Any]) -> None:
    """Validate the frozen governance portion of a configuration.

    Extra JSON-compatible fields are allowed so the environment implementation
    can add task-specific choices without weakening these checks.
    """

    if not isinstance(config, dict):
        raise ValueError("config must be a dictionary")
    if config.get("config_version") != CONFIG_VERSION:
        raise ValueError(f"config_version must equal {CONFIG_VERSION}")
    mode = config.get("mode")
    if mode not in _MODES:
        raise ValueError(f"mode must be one of {sorted(_MODES)}")
    run_id = config.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be a non-empty string")

    namespaces = _require_mapping(config, "split_namespaces")
    for split in _SPLITS:
        namespace = namespaces.get(split)
        if not isinstance(namespace, str) or not namespace.strip():
            raise ValueError(f"split_namespaces.{split} must be a non-empty string")
    if len(set(namespaces[split] for split in _SPLITS)) != len(_SPLITS):
        raise ValueError("split namespaces must be distinct")

    seeds = _require_mapping(config, "seeds")
    for name in ("agents", *_SPLITS):
        values = seeds.get(name)
        if not isinstance(values, list) or not values:
            raise ValueError(f"seeds.{name} must be a non-empty array")
        checked = [_integer(value, f"seeds.{name}[]") for value in values]
        if len(set(checked)) != len(checked):
            raise ValueError(f"seeds.{name} must not contain duplicates")

    counts = _require_mapping(config, "sample_counts")
    for name in _COUNTS:
        _integer(counts.get(name), f"sample_counts.{name}", minimum=1)

    population = _require_mapping(config, "agent_population")
    skill_levels = population.get("diagnostic_skill_levels")
    if not isinstance(skill_levels, list):
        raise ValueError("agent_population.diagnostic_skill_levels must be an array")
    checked_levels = tuple(
        _probability(value, "agent_population.diagnostic_skill_levels[]")
        for value in skill_levels
    )
    if checked_levels != _DIAGNOSTIC_SKILL_LEVELS:
        raise ValueError(
            "agent_population.diagnostic_skill_levels must equal "
            f"{list(_DIAGNOSTIC_SKILL_LEVELS)}"
        )
    controllers = population.get("controllers")
    if controllers != list(_CONTROLLERS):
        raise ValueError(
            f"agent_population.controllers must equal {list(_CONTROLLERS)}"
        )

    generator_scope = _require_mapping(config, "generator_scope")
    if generator_scope != _GENERATOR_SCOPE:
        raise ValueError(
            "generator_scope must identify the built-in, single-generator "
            f"engineering scope exactly: {_GENERATOR_SCOPE}"
        )

    thresholds = _require_mapping(config, "thresholds")
    _probability(thresholds.get("intervention_success_min"), "thresholds.intervention_success_min")
    minima = _require_mapping(thresholds, "intervention_minima")
    expected_minima = {"parameter": 0, "model": 1, "interface": 2}
    if minima != expected_minima:
        raise ValueError(f"thresholds.intervention_minima must equal {expected_minima}")
    _probability(
        thresholds.get("diagnostic_min_top1_accuracy"),
        "thresholds.diagnostic_min_top1_accuracy",
    )
    _probability(
        thresholds.get("diagnostic_min_class_recall"),
        "thresholds.diagnostic_min_class_recall",
    )
    _probability(thresholds.get("nuisance_max_accuracy"), "thresholds.nuisance_max_accuracy")
    _number(
        thresholds.get("nuisance_permutation_margin"),
        "thresholds.nuisance_permutation_margin",
        minimum=0.0,
    )
    _probability(
        thresholds.get("nuisance_permutation_quantile"),
        "thresholds.nuisance_permutation_quantile",
    )
    _integer(thresholds.get("nuisance_permutations"), "thresholds.nuisance_permutations", minimum=1)
    _integer(thresholds.get("nuisance_seed"), "thresholds.nuisance_seed")
    _number(
        thresholds.get("q_max_family_mean_gap"),
        "thresholds.q_max_family_mean_gap",
        minimum=0.0,
    )
    _integer(
        thresholds.get("q_min_records_per_family"),
        "thresholds.q_min_records_per_family",
        minimum=1,
    )
    _number(
        thresholds.get("cost_asymmetry_min_gap"),
        "thresholds.cost_asymmetry_min_gap",
        minimum=0.0,
    )
    minimum_delta = _number(
        thresholds.get("positive_min_delta_mae"),
        "thresholds.positive_min_delta_mae",
        minimum=0.0,
    )
    expected_delta = 0.005 if mode == "evidence" else 0.0
    if minimum_delta != expected_delta:
        raise ValueError(
            f"thresholds.positive_min_delta_mae must equal {expected_delta} in {mode} mode"
        )
    if thresholds.get("positive_require_ci_lower_bound") is not True:
        raise ValueError("thresholds.positive_require_ci_lower_bound must be true")

    ridge = _require_mapping(config, "ridge")
    alpha = _number(ridge.get("alpha"), "ridge.alpha", minimum=0.0)
    alphas = ridge.get("alphas")
    if not isinstance(alphas, list) or not alphas:
        raise ValueError("ridge.alphas must be a non-empty array")
    checked_alphas = [_number(value, "ridge.alphas[]", minimum=0.0) for value in alphas]
    if len(set(checked_alphas)) != len(checked_alphas):
        raise ValueError("ridge.alphas must not contain duplicates")
    if alpha not in checked_alphas:
        raise ValueError("ridge.alpha must be one of ridge.alphas")
    _integer(ridge.get("folds"), "ridge.folds", minimum=2)
    if ridge.get("selection_metric") != "mae":
        raise ValueError("ridge.selection_metric must be 'mae'")

    bootstrap = _require_mapping(config, "bootstrap")
    replicates = _integer(bootstrap.get("replicates"), "bootstrap.replicates", minimum=1)
    if mode == "evidence" and replicates < 2000:
        raise ValueError("evidence bootstrap.replicates must be at least 2000")
    confidence = _probability(bootstrap.get("confidence"), "bootstrap.confidence")
    if not 0.5 < confidence < 1.0:
        raise ValueError("bootstrap.confidence must be strictly between 0.5 and 1")
    _integer(bootstrap.get("seed"), "bootstrap.seed")
    if bootstrap.get("unit") not in {"generator_family", "agent", "checkpoint"}:
        raise ValueError("bootstrap.unit must be generator_family, agent, or checkpoint")

    try:
        json.dumps(config, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"config must be finite and JSON-compatible: {exc}") from exc
