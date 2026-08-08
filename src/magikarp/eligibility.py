"""Fail-closed evidence eligibility and pre-outcome attestation helpers.

The validator proves deterministic schema and hash binding only.  It cannot
prove that an attestor is socially independent or that ``record_locator`` is
immutable; those facts require external governance under the evidence-run
protocol.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


ATTESTATION_SCHEMA_VERSION = 1
MANIFEST_SCHEMA_VERSION = 3
BENCHMARK_VERSION = "MAGIKARP-v0.1"
EVIDENCE_PROTOCOL_VERSION = "0.1"
BUILTIN_IMPLEMENTATION = "builtin_latent_context_v0.1"
ELIGIBLE_INDEPENDENCE_LEVELS = frozenset({"L2", "L3"})
ATTESTATION_STATUSES = frozenset(
    {
        "missing",
        "self_attested",
        "process_verified",
        "independent_verified",
        "rejected",
    }
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_PROVENANCE_FIELDS = frozenset(
    {
        "structural_family_id",
        "generator_family",
        "generator_version",
        "generator_source_hash",
        "author_or_origin",
        "generator_created_at_utc",
        "derived_from",
        "shared_source_code",
        "shared_helper_functions",
        "shared_task_abstractions",
        "shared_latent_failure_ontology",
        "shared_parameterization",
        "shared_labeling_logic",
        "shared_evaluation_assumptions",
        "shared_revision_controller_assumptions",
        "shared_evaluation_assumptions",
        "known_shared_dependencies",
        "benchmark_internal_access",
        "independence_level",
        "independence_reviewer_id",
        "independence_rationale",
        "independence_limitations",
        "comparison_record_hash",
        "generator_provenance_hash",
    }
)
_DESIGN_FREEZE_FIELDS = frozenset(
    {
        "seed_policy",
        "group_assignment_policy",
        "primary_endpoints",
        "validity_gate_definitions",
        "exclusion_rules",
        "bootstrap_or_interval_procedure",
        "stopping_rule",
        "evidence_classification_rules",
    }
)
_ATTESTATION_FIELDS = frozenset(
    {
        "schema_version",
        "manifest_hash",
        "benchmark_contract_hash",
        "evidence_protocol_hash",
        "generator_source_hash",
        "generator_provenance_hash",
        "controller_source_hash",
        "analysis_source_hash",
        "config_hash",
        "run_id",
        "independence_level",
        "evidence_ready",
        "attestor_id",
        "attestor_independence",
        "attested_at_utc",
        "record_locator",
        "status",
        "attestation_hash",
    }
)
_SCIENTIFIC_HASH_FIELDS = (
    "benchmark_contract_hash",
    "evidence_protocol_hash",
    "generator_source_hash",
    "generator_provenance_hash",
    "controller_source_hash",
    "analysis_source_hash",
    "config_hash",
    "design_freeze_hash",
)
_PROVENANCE_STRING_FIELDS = frozenset(
    {
        "structural_family_id",
        "generator_family",
        "generator_version",
        "generator_source_hash",
        "author_or_origin",
        "generator_created_at_utc",
        "independence_level",
        "independence_reviewer_id",
        "independence_rationale",
    }
)
_PROVENANCE_LIST_FIELDS = frozenset(
    {
        "derived_from",
        "shared_source_code",
        "shared_helper_functions",
        "shared_task_abstractions",
        "shared_latent_failure_ontology",
        "shared_parameterization",
        "shared_labeling_logic",
        "shared_revision_controller_assumptions",
        "shared_evaluation_assumptions",
        "known_shared_dependencies",
        "independence_limitations",
    }
)
_TARGET_MECHANISM_DISCLOSURES = frozenset(
    {
        "shared_source_code",
        "shared_helper_functions",
        "shared_parameterization",
        "shared_labeling_logic",
        "shared_evaluation_assumptions",
    }
)
_INTERNAL_ACCESS_FIELDS = frozenset(
    {"public_contract", "implementation", "prior_manifests", "prior_outcomes", "failed_runs"}
)


def canonical_hash(value: Any) -> str:
    """Return SHA-256 over canonical finite JSON."""

    payload = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def manifest_hash(manifest: Mapping[str, Any]) -> str:
    """Hash a manifest while excluding its self-hash field."""

    return canonical_hash({key: value for key, value in manifest.items() if key != "manifest_hash"})


def comparison_record_hash(provenance: Mapping[str, Any]) -> str:
    """Hash generator comparison disclosures, excluding both derived hashes."""

    return canonical_hash(
        {
            key: value
            for key, value in provenance.items()
            if key not in {"comparison_record_hash", "generator_provenance_hash"}
        }
    )


def generator_provenance_hash(provenance: Mapping[str, Any]) -> str:
    """Hash a comparison record including its comparison hash."""

    return canonical_hash(
        {key: value for key, value in provenance.items() if key != "generator_provenance_hash"}
    )


def attestation_hash(attestation: Mapping[str, Any]) -> str:
    """Hash an attestation while excluding its self-hash field."""

    return canonical_hash(
        {key: value for key, value in attestation.items() if key != "attestation_hash"}
    )


def seal_attestation(attestation: Mapping[str, Any]) -> dict[str, Any]:
    """Copy an attestation payload and add its deterministic self-hash."""

    sealed = json.loads(
        json.dumps(attestation, allow_nan=False, ensure_ascii=True, sort_keys=True)
    )
    if not isinstance(sealed, dict):
        raise ValueError("attestation must be a JSON object")
    sealed.pop("attestation_hash", None)
    sealed["attestation_hash"] = attestation_hash(sealed)
    return sealed


def write_attestation(attestation: Mapping[str, Any], path: str | Path) -> None:
    """Validate and atomically write a deterministic attestation JSON record."""

    sealed = dict(attestation)
    if set(sealed) != _ATTESTATION_FIELDS:
        raise ValueError("attestation fields do not match protocol schema")
    if sealed.get("attestation_hash") != attestation_hash(sealed):
        raise ValueError("attestation content does not match attestation_hash")
    payload = json.dumps(
        sealed, allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True
    ) + "\n"
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(target)


def load_attestation(path: str | Path) -> dict[str, Any]:
    """Load a separate attestation record without granting it authority."""

    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load attestation {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("attestation root must be a JSON object")
    return value


def _utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _contains_builtin_identity(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().casefold() == BUILTIN_IMPLEMENTATION.casefold()
    if isinstance(value, Mapping):
        return any(_contains_builtin_identity(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_builtin_identity(item) for item in value)
    return False


def _design_freeze_complete(design: Any) -> bool:
    if not isinstance(design, Mapping) or not _DESIGN_FREEZE_FIELDS.issubset(design):
        return False
    for field in _DESIGN_FREEZE_FIELDS:
        value = design[field]
        if not isinstance(value, Mapping) or not value:
            return False
    return True


def evaluate_evidence_eligibility(
    manifest: Mapping[str, Any] | None,
    attestation: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Derive pre-outcome evidence readiness from frozen, bound records.

    Every unknown, missing, inconsistent, or unverifiable value adds a stable
    reason code and leaves ``eligible`` false.  An otherwise convincing
    attestation can never promote the built-in generator or one of its declared
    derivatives.
    """

    reasons: list[str] = []
    checked_hashes: dict[str, bool] = {}
    candidate = dict(manifest) if isinstance(manifest, Mapping) else {}
    statement = dict(attestation) if isinstance(attestation, Mapping) else {}

    def reject(reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    if not candidate:
        reject("manifest_missing")
    if type(candidate.get("manifest_version")) is not int or candidate.get("manifest_version") != MANIFEST_SCHEMA_VERSION:
        reject("manifest_version_mismatch")
    if candidate.get("mode") != "evidence":
        reject("evidence_mode_required")
    if candidate.get("frozen") is not True:
        reject("manifest_not_frozen")
    actual_manifest_hash = candidate.get("manifest_hash")
    manifest_hash_ok = (
        isinstance(actual_manifest_hash, str)
        and bool(_DIGEST_RE.fullmatch(actual_manifest_hash))
        and actual_manifest_hash == manifest_hash(candidate)
    )
    checked_hashes["manifest_hash"] = manifest_hash_ok
    if not manifest_hash_ok:
        reject("manifest_hash_mismatch")
    if candidate.get("benchmark_version") != BENCHMARK_VERSION:
        reject("benchmark_version_mismatch")
    if candidate.get("evidence_protocol_version") != EVIDENCE_PROTOCOL_VERSION:
        reject("evidence_protocol_version_mismatch")
    if not _nonempty_string(candidate.get("run_id")):
        reject("run_id_missing")

    design = candidate.get("design_freeze")
    if not _design_freeze_complete(design):
        reject("design_freeze_incomplete")
        design_hash_ok = False
    else:
        design_hash_ok = candidate.get("design_freeze_hash") == canonical_hash(design)
    checked_hashes["design_freeze_hash"] = design_hash_ok
    if not design_hash_ok:
        reject("design_freeze_hash_mismatch")
    if isinstance(design, Mapping):
        run_id = candidate.get("run_id")
        seed_policy = design.get("seed_policy")
        stopping_rule = design.get("stopping_rule")
        registered = (
            seed_policy.get("registered_run_ids")
            if isinstance(seed_policy, Mapping)
            else None
        )
        planned = (
            stopping_rule.get("planned_runs")
            if isinstance(stopping_rule, Mapping)
            else None
        )
        if not isinstance(registered, list) or run_id not in registered:
            reject("run_id_not_registered")
        if not isinstance(planned, list) or run_id not in planned:
            reject("run_id_not_planned")

    provenance = candidate.get("generator_provenance")
    if not isinstance(provenance, Mapping) or not _PROVENANCE_FIELDS.issubset(provenance):
        reject("generator_provenance_incomplete")
        comparison_ok = False
        provenance_ok = False
    else:
        comparison_ok = provenance.get("comparison_record_hash") == comparison_record_hash(provenance)
        provenance_ok = provenance.get("generator_provenance_hash") == generator_provenance_hash(provenance)
    checked_hashes["comparison_record_hash"] = comparison_ok
    checked_hashes["generator_provenance_hash"] = provenance_ok
    if not comparison_ok:
        reject("comparison_record_hash_mismatch")
    if not provenance_ok:
        reject("generator_provenance_hash_mismatch")
    if isinstance(provenance, Mapping) and _PROVENANCE_FIELDS.issubset(provenance):
        invalid_provenance = False
        for field in _PROVENANCE_STRING_FIELDS:
            if not _nonempty_string(provenance.get(field)):
                invalid_provenance = True
        if not isinstance(provenance.get("generator_source_hash"), str) or not _DIGEST_RE.fullmatch(
            str(provenance.get("generator_source_hash"))
        ):
            invalid_provenance = True
        if not _utc_timestamp(provenance.get("generator_created_at_utc")):
            invalid_provenance = True
        for field in _PROVENANCE_LIST_FIELDS:
            if not isinstance(provenance.get(field), list):
                invalid_provenance = True
        access = provenance.get("benchmark_internal_access")
        if (
            not isinstance(access, Mapping)
            or not _INTERNAL_ACCESS_FIELDS.issubset(access)
        ):
            invalid_provenance = True
        elif any(type(value) is not bool for value in access.values()):
            invalid_provenance = True
        if invalid_provenance:
            reject("generator_provenance_invalid")
        if any(provenance.get(field) for field in _TARGET_MECHANISM_DISCLOSURES):
            reject("shared_target_mechanism_ineligible")
        if isinstance(access, Mapping) and any(
            access.get(field) is True
            for field in ("implementation", "prior_outcomes", "failed_runs")
        ):
            reject("benchmark_internal_access_ineligible")

    scope = candidate.get("generator_scope")
    scope_ready = isinstance(scope, Mapping) and scope.get("evidence_ready") is True
    if not scope_ready:
        reject("generator_scope_not_ready")
    if not isinstance(scope, Mapping) or scope.get("structurally_distinct_families") is not True:
        reject("structural_independence_not_declared")
    implementation = scope.get("implementation") if isinstance(scope, Mapping) else None
    structural_id = candidate.get("structural_family_id")
    derived_from = provenance.get("derived_from") if isinstance(provenance, Mapping) else None
    builtin_identity = (
        implementation == BUILTIN_IMPLEMENTATION
        or structural_id == BUILTIN_IMPLEMENTATION
        or (isinstance(provenance, Mapping) and provenance.get("structural_family_id") == BUILTIN_IMPLEMENTATION)
        or _contains_builtin_identity(derived_from)
    )
    if builtin_identity:
        reject("builtin_or_derivative_ineligible")

    independence_level = candidate.get("independence_level")
    if isinstance(provenance, Mapping) and provenance.get("independence_level") != independence_level:
        reject("independence_level_mismatch")
    if independence_level not in ELIGIBLE_INDEPENDENCE_LEVELS:
        reject("independence_level_below_L2")

    top_generator_fields = {
        "structural_family_id": "structural_family_id",
        "generator_family": "generator_family",
        "generator_version": "generator_version",
        "generator_source_hash": "generator_source_hash",
        "generator_provenance_hash": "generator_provenance_hash",
    }
    for top_key, provenance_key in top_generator_fields.items():
        if not isinstance(provenance, Mapping) or candidate.get(top_key) != provenance.get(provenance_key):
            reject(f"{top_key}_mismatch")

    scientific = candidate.get("scientific_hashes")
    if not isinstance(scientific, Mapping):
        reject("scientific_hashes_missing")
        scientific = {}
    for field in _SCIENTIFIC_HASH_FIELDS:
        value = candidate.get(field)
        valid_digest = (
            isinstance(value, str)
            and bool(_DIGEST_RE.fullmatch(value))
            and value != "0" * 64
        )
        bound = valid_digest and scientific.get(field) == value
        checked_hashes[field] = bool(bound)
        if not bound:
            reject(f"{field}_mismatch")

    attestation_status = statement.get("status", "missing") if statement else "missing"
    if not statement:
        reject("attestation_missing")
    else:
        if set(statement) != _ATTESTATION_FIELDS:
            reject("attestation_schema_incomplete")
        if type(statement.get("schema_version")) is not int or statement.get("schema_version") != ATTESTATION_SCHEMA_VERSION:
            reject("attestation_schema_version_mismatch")
        if attestation_status not in ATTESTATION_STATUSES:
            reject("attestation_status_unknown")
        elif attestation_status != "independent_verified":
            reject("attestation_not_independent_verified")
        if statement.get("attestor_independence") != "independent":
            reject("attestor_not_independent")
        if statement.get("evidence_ready") is not True:
            reject("attestation_not_evidence_ready")
        if not _nonempty_string(statement.get("attestor_id")):
            reject("attestor_id_missing")
        if (
            isinstance(provenance, Mapping)
            and _nonempty_string(statement.get("attestor_id"))
            and _nonempty_string(provenance.get("author_or_origin"))
            and str(statement["attestor_id"]).strip().casefold()
            == str(provenance["author_or_origin"]).strip().casefold()
        ):
            reject("attestor_matches_generator_author")
        if not _utc_timestamp(statement.get("attested_at_utc")):
            reject("attested_at_utc_invalid")
        if not _nonempty_string(statement.get("record_locator")):
            reject("record_locator_missing")
        statement_hash_ok = (
            isinstance(statement.get("attestation_hash"), str)
            and statement.get("attestation_hash") == attestation_hash(statement)
        )
        checked_hashes["attestation_hash"] = statement_hash_ok
        if not statement_hash_ok:
            reject("attestation_hash_mismatch")
        if statement.get("independence_level") != independence_level:
            reject("attested_independence_level_mismatch")
        bindings = {
            "manifest_hash": actual_manifest_hash,
            "benchmark_contract_hash": candidate.get("benchmark_contract_hash"),
            "evidence_protocol_hash": candidate.get("evidence_protocol_hash"),
            "generator_source_hash": candidate.get("generator_source_hash"),
            "generator_provenance_hash": candidate.get("generator_provenance_hash"),
            "controller_source_hash": candidate.get("controller_source_hash"),
            "analysis_source_hash": candidate.get("analysis_source_hash"),
            "config_hash": candidate.get("config_hash"),
            "run_id": candidate.get("run_id"),
        }
        for field, expected in bindings.items():
            if statement.get(field) != expected:
                reject(f"attestation_{field}_mismatch")

    return {
        "eligible": not reasons,
        "attestation_status": str(attestation_status),
        "independence_level": independence_level,
        "reasons": sorted(reasons),
        "checked_hashes": dict(sorted(checked_hashes.items())),
        "validator_scope": (
            "schema_and_hash_binding_only; external attestor identity, control "
            "independence, and locator immutability are not established by software"
        ),
    }
