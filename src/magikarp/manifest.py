"""Deterministic run manifests for MAGIKARP v0.1."""

from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from .config import validate_config
from .eligibility import (
    BENCHMARK_VERSION,
    BUILTIN_IMPLEMENTATION,
    EVIDENCE_PROTOCOL_VERSION,
    canonical_hash,
    comparison_record_hash,
    generator_provenance_hash,
    manifest_hash,
)


MANIFEST_VERSION = 3
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_PACKAGE_PATH = Path("src/magikarp")
_AUTHORITY_PATHS = (
    "docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md",
    "docs/REVISION_CONTROLLER_CLARIFICATION.md",
    "docs/V0_1_EXECUTION_PREFLIGHT.md",
)
_BENCHMARK_CONTRACT_PATH = Path("docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md")
_EVIDENCE_PROTOCOL_PATH = Path("EVIDENCE-RUN-PROTOCOL-v0.1.md")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _source_inventory(package_root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(package_root.rglob("*")):
        relative = path.relative_to(package_root)
        if (
            not path.is_file()
            or "__pycache__" in relative.parts
            or path.suffix.lower() in {".pyc", ".pyo"}
        ):
            continue
        key = (_PACKAGE_PATH / relative).as_posix()
        files[key] = _file_digest(path)
    if not files:
        raise ValueError(f"executing package tree is empty: {package_root}")
    return files


def _git_toplevel(repo_root: Path) -> Path | None:
    try:
        output = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return Path(output).resolve() if output else None


def _repository_provenance(
    repo_root: Path, *, require_binding: bool
) -> dict[str, Any]:
    root = repo_root.resolve()
    executing_package = Path(__file__).resolve().parent
    expected_package = (root / _PACKAGE_PATH).resolve()
    top_level = _git_toplevel(root)
    repository_bound = top_level == root and executing_package == expected_package
    if require_binding and not repository_bound:
        raise ValueError(
            "evidence provenance requires the supplied repo root to be the Git "
            "top-level containing the executing package at src/magikarp"
        )

    authority_files: dict[str, str] = {}
    if repository_bound:
        for relative in _AUTHORITY_PATHS:
            path = root / relative
            if not path.is_file():
                raise ValueError(f"authoritative frozen document is missing: {relative}")
            authority_files[relative] = _file_digest(path)

    source_files = _source_inventory(executing_package)
    return {
        "repository_bound": repository_bound,
        "package_path": _PACKAGE_PATH.as_posix(),
        "source_files": source_files,
        "source_tree_hash": _digest(source_files),
        "authority_files": authority_files,
        "authority_tree_hash": _digest(authority_files),
    }


def _manifest_digest(manifest: dict[str, Any]) -> str:
    return manifest_hash(manifest)


def _git_state(repo_root: Path) -> tuple[str, bool]:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip().lower()
        dirty_output = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=normal"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return "unknown", True
    if not _SHA_RE.fullmatch(sha):
        return "unknown", True
    return sha, bool(dirty_output.strip())


def _split_hashes(config: dict[str, Any]) -> dict[str, str]:
    namespaces = config["split_namespaces"]
    seeds = config["seeds"]
    return {
        split: _digest({"namespace": namespace, "seeds": seeds[split]})
        for split, namespace in sorted(namespaces.items())
    }


def _component_hash(source_files: dict[str, str], *relative_paths: str) -> str:
    selected = {path: source_files[path] for path in relative_paths}
    return canonical_hash(selected)


def _builtin_generator_provenance(source_hash: str) -> dict[str, Any]:
    """Return the explicit L0 comparison record for the built-in generator."""

    record: dict[str, Any] = {
        "structural_family_id": BUILTIN_IMPLEMENTATION,
        "generator_family": "namespaced_buckets_single_generator",
        "generator_version": "0.1",
        "generator_source_hash": source_hash,
        "author_or_origin": "MAGIKARP repository built-in engineering generator",
        "generator_created_at_utc": "2026-08-08T00:00:00Z",
        "derived_from": [],
        "shared_source_code": ["src/magikarp/environment.py"],
        "shared_helper_functions": ["stable seeded latent-context construction"],
        "shared_task_abstractions": ["parameter", "model", "interface"],
        "shared_latent_failure_ontology": ["parameter", "model", "interface"],
        "shared_parameterization": ["signal prototypes", "outcome equations"],
        "shared_labeling_logic": ["experimenter-owned failure depth"],
        "shared_revision_controller_assumptions": ["supplied depth 0/1/2 actions"],
        "shared_evaluation_assumptions": ["built-in recovery and preservation functions"],
        "known_shared_dependencies": [
            "MAGIKARP benchmark types",
            "frozen failure ontology",
            "supplied revision action set",
        ],
        "benchmark_internal_access": {
            "public_contract": True,
            "implementation": True,
            "prior_manifests": True,
            "prior_outcomes": True,
            "failed_runs": True,
        },
        "independence_level": "L0",
        "independence_reviewer_id": "magikarp-maintainers",
        "independence_rationale": (
            "Built-in family labels are seed/index buckets over one mechanism and "
            "cannot establish structural independence."
        ),
        "independence_limitations": [
            "same source tree as the benchmark",
            "shared diagnostic and outcome-generating mechanism",
            "not independently authored or attested",
        ],
    }
    record["comparison_record_hash"] = comparison_record_hash(record)
    record["generator_provenance_hash"] = generator_provenance_hash(record)
    return record


def _design_freeze(config: dict[str, Any], run_id: str) -> dict[str, Any]:
    return {
        "seed_policy": {
            "registered_run_ids": [run_id],
            "seeds": config["seeds"],
            "derivation": "stable namespaced hash; all registered seeds included exactly once",
            "execution_order": "sorted frozen config order",
        },
        "group_assignment_policy": {
            "independent_agent_block": "agent_group_id = population-seed x replicate",
            "structural_family": "structural_family_id identifies the generating mechanism",
            "within_family_bucket": "generator_family is a seed/index bucket only",
            "outer_prediction": "hold out whole agent_group_id and generator_family groups",
        },
        "primary_endpoints": {
            "primary": "R_c: held-out recovery after a fixed adaptation budget",
            "reported": ["R_c", "T", "R", "P", "C"],
            "models": {
                "M0": ["intercept", "Q", "A", "E"],
                "M1": ["intercept", "Q", "A", "E", "SD"],
                "effect": "MAE(M0)-MAE(M1)",
            },
        },
        "validity_gate_definitions": {
            "thresholds": config["thresholds"],
            "order": "all required gates pass before primary prediction is evaluated",
        },
        "exclusion_rules": {
            "predeclared": [],
            "missing_data": "no silent exclusion; any missing required record invalidates the run",
            "post_outcome_changes": "forbidden under this manifest",
        },
        "bootstrap_or_interval_procedure": {
            "ridge": config["ridge"],
            "bootstrap": config["bootstrap"],
            "loss_difference": "paired M0 minus M1 absolute-error difference",
        },
        "stopping_rule": {
            "planned_runs": [run_id],
            "rule": "execute each registered run once and retain positive, null, invalid, and technical failures",
            "interim_outcome_inspection": False,
            "outcome_conditioned_seed_selection": False,
        },
        "evidence_classification_rules": {
            "valid_positive": "valid primary delta exceeds threshold and required interval lower bound",
            "valid_negative": "valid run not meeting the frozen primary positive rule",
            "benchmark_invalid": "any failed validity, provenance, compatibility, attestation, or freeze condition",
            "engineering_only": "deliberately ineligible infrastructure execution",
            "per_failure_heterogeneity": "secondary diagnostic only; never a top-level outcome",
        },
    }


def build_manifest(config: dict[str, Any], repo_root: str | Path) -> dict[str, Any]:
    """Build a deterministic pre-outcome manifest.

    An evidence manifest is marked frozen only when built from a clean Git
    commit.  Smoke manifests remain explicitly non-evidence-bearing.
    """

    validate_config(config)
    # The JSON round trip both copies the object and normalizes tuples or other
    # JSON-compatible containers before hashing and persistence.
    frozen_config = json.loads(_canonical_json(config))
    root = Path(repo_root).resolve()
    evidence_mode = frozen_config["mode"] == "evidence"
    provenance = _repository_provenance(root, require_binding=evidence_mode)
    git_sha, git_dirty = _git_state(root)
    authority_root = root if provenance["repository_bound"] else Path(__file__).resolve().parents[2]
    benchmark_contract_path = authority_root / _BENCHMARK_CONTRACT_PATH
    evidence_protocol_path = authority_root / _EVIDENCE_PROTOCOL_PATH
    authority_available = (
        benchmark_contract_path.is_file() and evidence_protocol_path.is_file()
    )
    if evidence_mode and not authority_available:
        raise ValueError("evidence mode requires the exact benchmark contract and protocol files")

    source_files = provenance["source_files"]
    generator_source_hash = _component_hash(
        source_files, "src/magikarp/environment.py"
    )
    controller_source_hash = _component_hash(
        source_files, "src/magikarp/agents.py"
    )
    analysis_source_hash = _component_hash(
        source_files,
        "src/magikarp/analysis.py",
        "src/magikarp/eligibility.py",
        "src/magikarp/metrics.py",
        "src/magikarp/runner.py",
        "src/magikarp/validity.py",
    )
    generator_provenance = _builtin_generator_provenance(generator_source_hash)
    run_id = str(frozen_config["run_id"])
    design_freeze = _design_freeze(frozen_config, run_id)
    config_hash = _digest(frozen_config)
    benchmark_contract_hash = (
        _file_digest(benchmark_contract_path) if authority_available else "0" * 64
    )
    evidence_protocol_hash = (
        _file_digest(evidence_protocol_path) if authority_available else "0" * 64
    )
    design_freeze_hash = _digest(design_freeze)
    scientific_hashes = {
        "benchmark_contract_hash": benchmark_contract_hash,
        "evidence_protocol_hash": evidence_protocol_hash,
        "generator_source_hash": generator_source_hash,
        "generator_provenance_hash": generator_provenance["generator_provenance_hash"],
        "controller_source_hash": controller_source_hash,
        "analysis_source_hash": analysis_source_hash,
        "config_hash": config_hash,
        "design_freeze_hash": design_freeze_hash,
    }
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "benchmark_contract_hash": benchmark_contract_hash,
        "evidence_protocol_version": EVIDENCE_PROTOCOL_VERSION,
        "evidence_protocol_hash": evidence_protocol_hash,
        "run_id": run_id,
        "mode": frozen_config["mode"],
        "frozen": bool(evidence_mode and not git_dirty and git_sha != "unknown"),
        "config": frozen_config,
        "config_hash": config_hash,
        "generator_scope": frozen_config["generator_scope"],
        "generator_provenance": generator_provenance,
        "structural_family_id": generator_provenance["structural_family_id"],
        "generator_family": generator_provenance["generator_family"],
        "generator_version": generator_provenance["generator_version"],
        "generator_source_hash": generator_source_hash,
        "generator_provenance_hash": generator_provenance["generator_provenance_hash"],
        "independence_level": generator_provenance["independence_level"],
        "controller_version": "0.1",
        "controller_source_hash": controller_source_hash,
        "analysis_version": "0.1",
        "analysis_source_hash": analysis_source_hash,
        "design_freeze": design_freeze,
        "design_freeze_hash": design_freeze_hash,
        "scientific_hashes": scientific_hashes,
        "eligibility_prerequisites": {
            "minimum_independence_level": "L2",
            "independent_attestation_required": True,
            "candidate_scope_declares_ready": bool(
                frozen_config["generator_scope"]["evidence_ready"]
            ),
            "built_in_generator_eligible": False,
        },
        "authority_binding": {
            "available": authority_available,
            "benchmark_contract_path": _BENCHMARK_CONTRACT_PATH.as_posix(),
            "evidence_protocol_path": _EVIDENCE_PROTOCOL_PATH.as_posix(),
        },
        "evidence_ready": False,
        "git": {
            "sha": git_sha,
            "dirty": git_dirty,
        },
        "runtime": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "numpy": np.__version__,
        },
        "provenance": provenance,
        "split_namespaces": dict(sorted(frozen_config["split_namespaces"].items())),
        "split_hashes": _split_hashes(frozen_config),
        "definitions": {
            "metrics": {
                "Q": "mean normalized clean pre-perturbation performance",
                "E": "mean pre-adaptation perturbation loss before unrestricted correction",
                "A": "fixed-budget recovery on a disjoint ordinary parameter-shift suite",
                "SD": "one minus normalized multiclass Brier loss over parameter/model/interface diagnosis",
            },
            "outcomes": {
                "primary": "R_c: held-out recovery after a fixed adaptation budget",
                "reported": ["R_c", "T", "R", "P", "C"],
            },
            "models": {
                "M0": ["intercept", "Q", "A", "E"],
                "M1": ["intercept", "Q", "A", "E", "SD"],
                "family": "linear_or_ridge_regression",
                "ridge": frozen_config["ridge"],
                "selection_metric": "held_out_mae",
                "delta": "MAE(M0)-MAE(M1)",
                "bootstrap": frozen_config["bootstrap"],
            },
        },
    }
    manifest["manifest_hash"] = _manifest_digest(manifest)
    return manifest


def write_manifest(manifest: dict[str, Any], path: str | Path) -> None:
    """Atomically write a manifest as stable, human-readable JSON."""

    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a dictionary")
    try:
        payload = json.dumps(
            manifest,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        ) + "\n"
    except (TypeError, ValueError) as exc:
        raise ValueError(f"manifest must be finite and JSON-compatible: {exc}") from exc
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(target)


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Load a manifest without treating it as frozen evidence."""

    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load manifest {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("manifest root must be a JSON object")
    return value


def _validate_scientific_bindings(
    manifest: dict[str, Any], *, source_files: dict[str, str], authority_root: Path
) -> None:
    """Recompute every scientific hash available from the executing checkout."""

    if manifest.get("benchmark_version") != BENCHMARK_VERSION:
        raise ValueError(f"benchmark_version must equal {BENCHMARK_VERSION}")
    if manifest.get("evidence_protocol_version") != EVIDENCE_PROTOCOL_VERSION:
        raise ValueError(
            f"evidence_protocol_version must equal {EVIDENCE_PROTOCOL_VERSION}"
        )
    contract_path = authority_root / _BENCHMARK_CONTRACT_PATH
    protocol_path = authority_root / _EVIDENCE_PROTOCOL_PATH
    authority_available = contract_path.is_file() and protocol_path.is_file()
    if manifest.get("mode") == "evidence" and not authority_available:
        raise ValueError("evidence mode requires the exact benchmark contract and protocol files")
    authority_binding = manifest.get("authority_binding")
    if not isinstance(authority_binding, dict) or authority_binding.get("available") is not authority_available:
        raise ValueError("manifest authority availability does not match executing distribution")
    expected: dict[str, str] = {
        "benchmark_contract_hash": _file_digest(contract_path) if authority_available else "0" * 64,
        "evidence_protocol_hash": _file_digest(protocol_path) if authority_available else "0" * 64,
        "generator_source_hash": _component_hash(
            source_files, "src/magikarp/environment.py"
        ),
        "controller_source_hash": _component_hash(
            source_files, "src/magikarp/agents.py"
        ),
        "analysis_source_hash": _component_hash(
            source_files,
            "src/magikarp/analysis.py",
            "src/magikarp/eligibility.py",
            "src/magikarp/metrics.py",
            "src/magikarp/runner.py",
            "src/magikarp/validity.py",
        ),
    }
    generator_record = manifest.get("generator_provenance")
    if not isinstance(generator_record, dict):
        raise ValueError("manifest generator_provenance is missing")
    if generator_record.get("comparison_record_hash") != comparison_record_hash(
        generator_record
    ):
        raise ValueError("generator comparison record hash does not match disclosures")
    expected["generator_provenance_hash"] = generator_provenance_hash(generator_record)
    config = manifest.get("config")
    design = manifest.get("design_freeze")
    if not isinstance(config, dict) or not isinstance(design, dict):
        raise ValueError("manifest config or design_freeze is missing")
    expected["config_hash"] = _digest(config)
    expected["design_freeze_hash"] = _digest(design)
    scientific = manifest.get("scientific_hashes")
    if not isinstance(scientific, dict):
        raise ValueError("manifest scientific_hashes is missing")
    for field, value in expected.items():
        if manifest.get(field) != value or scientific.get(field) != value:
            raise ValueError(f"manifest {field} does not match executing scientific source")
    if generator_record.get("generator_source_hash") != expected["generator_source_hash"]:
        raise ValueError("generator provenance source hash does not match executing source")
    if generator_record.get("generator_provenance_hash") != expected["generator_provenance_hash"]:
        raise ValueError("generator provenance hash does not match disclosures")

    duplicate_fields = {
        "structural_family_id",
        "generator_family",
        "generator_version",
        "generator_source_hash",
        "generator_provenance_hash",
        "independence_level",
    }
    for field in duplicate_fields:
        if manifest.get(field) != generator_record.get(field):
            raise ValueError(f"manifest {field} does not match generator provenance")


def validate_frozen_manifest(manifest: dict[str, Any], config: dict[str, Any]) -> None:
    """Reject stale, mismatched, or unfrozen evidence manifests."""

    validate_config(config)
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a dictionary")
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        raise ValueError(f"manifest_version must equal {MANIFEST_VERSION}")
    manifest_hash = manifest.get("manifest_hash")
    if not isinstance(manifest_hash, str) or not _DIGEST_RE.fullmatch(manifest_hash):
        raise ValueError("manifest_hash must be one SHA-256 digest")
    if manifest_hash != _manifest_digest(manifest):
        raise ValueError("manifest content does not match manifest_hash")

    normalized_config = json.loads(_canonical_json(config))
    expected_hash = _digest(normalized_config)
    if manifest.get("mode") != normalized_config["mode"]:
        raise ValueError("manifest mode does not match config mode")
    if manifest.get("config_hash") != expected_hash:
        raise ValueError("manifest config hash does not match config")
    if manifest.get("config") != normalized_config:
        raise ValueError("manifest embedded config does not match config")
    if manifest.get("run_id") != normalized_config["run_id"]:
        raise ValueError("manifest run_id does not match config")
    if manifest.get("generator_scope") != normalized_config["generator_scope"]:
        raise ValueError("manifest generator scope does not match config")
    if manifest.get("split_namespaces") != dict(
        sorted(normalized_config["split_namespaces"].items())
    ):
        raise ValueError("manifest split namespaces do not match config")
    if manifest.get("split_hashes") != _split_hashes(normalized_config):
        raise ValueError("manifest split hashes do not match config")

    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("manifest executing provenance is missing")
    source_files = provenance.get("source_files")
    if not isinstance(source_files, dict):
        raise ValueError("manifest executing source inventory is missing")
    authority_root = Path(__file__).resolve().parents[2]
    _validate_scientific_bindings(
        manifest, source_files=source_files, authority_root=authority_root
    )

    git = manifest.get("git")
    if not isinstance(git, dict):
        raise ValueError("manifest git metadata is missing")
    if normalized_config["mode"] == "evidence":
        if manifest.get("frozen") is not True:
            raise ValueError("evidence manifest is not frozen")
        if git.get("dirty") is not False:
            raise ValueError("evidence manifest was built from a dirty worktree")
        sha = git.get("sha")
        if not isinstance(sha, str) or not _SHA_RE.fullmatch(sha):
            raise ValueError("evidence manifest must identify one full Git commit SHA")
        if not isinstance(provenance, dict) or provenance.get("repository_bound") is not True:
            raise ValueError("evidence manifest is not bound to the executing repository")


def validate_current_checkout(manifest: dict[str, Any], repo_root: str | Path) -> None:
    """Require evidence execution from the frozen commit with no tracked edits.

    Untracked files are allowed because the frozen manifest itself and the
    result directory are normally created after the clean pre-outcome check.
    Tracked implementation/config changes are never allowed after freezing.
    """

    git = manifest.get("git")
    if not isinstance(git, dict) or not isinstance(git.get("sha"), str):
        raise ValueError("manifest git metadata is missing")
    runtime = manifest.get("runtime")
    expected_runtime = {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "numpy": np.__version__,
    }
    if runtime != expected_runtime:
        raise ValueError(
            f"current runtime does not match frozen manifest: expected {runtime}, "
            f"got {expected_runtime}"
        )
    root = Path(repo_root).resolve()
    current_provenance = _repository_provenance(root, require_binding=True)
    if manifest.get("provenance") != current_provenance:
        raise ValueError(
            "executing source or authoritative frozen documents do not match the manifest"
        )
    _validate_scientific_bindings(
        manifest,
        source_files=current_provenance["source_files"],
        authority_root=root,
    )
    try:
        current_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip().lower()
        tracked_status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f"cannot verify evidence checkout: {exc}") from exc
    if current_sha != git["sha"]:
        raise ValueError("current Git commit does not match the frozen manifest")
    if tracked_status:
        raise ValueError("tracked files changed after the evidence manifest was frozen")
