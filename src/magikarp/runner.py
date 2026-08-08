"""End-to-end execution of the frozen MAGIKARP v0.1 operational loop."""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from .agents import SyntheticAgent, generate_agent_specs
from .analysis import aggregate_trials, grouped_outer_prediction
from .artifacts import write_run_artifacts
from .config import validate_config
from .environment import (
    evaluate_revision,
    generate_diagnostic_evidence,
    interface_collision_exists,
    intervention_matrix,
)
from .eligibility import evaluate_evidence_eligibility
from .manifest import (
    build_manifest,
    validate_current_checkout,
    validate_frozen_manifest,
)
from .metrics import diagnostic_summary, normalized_brier_sd
from .types import (
    AgentSpec,
    DiagnosticEvidence,
    DiagnosticRecord,
    FailureDepth,
    RevisionTrace,
    TrialRecord,
)
from .validity import evaluate_validity


def _stable_seed(seed: int, *parts: object) -> int:
    material = "\x1f".join((str(seed), *(str(part) for part in parts)))
    digest = hashlib.blake2b(material.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little", signed=False)


def _clip01(value: float) -> float:
    return float(min(1.0, max(0.0, value)))


def _battery(
    config: Mapping[str, Any],
    split: str,
    cases_per_failure: int,
) -> list[DiagnosticEvidence]:
    evidence: list[DiagnosticEvidence] = []
    namespace = str(config["split_namespaces"][split])
    for seed in config["seeds"][split]:
        prefix = f"{namespace}/seed-{seed}"
        evidence.extend(
            generate_diagnostic_evidence(
                int(seed),
                split,
                int(cases_per_failure),
                prefix,
            )
        )
    case_ids = [record.case_id for record in evidence]
    if len(case_ids) != len(set(case_ids)):
        raise RuntimeError(f"{split} generator produced duplicate case IDs")
    return evidence


def _agent_population(config: Mapping[str, Any]) -> list[AgentSpec]:
    population = config.get("agent_population", {})
    levels = population.get("diagnostic_skill_levels", [0.25, 0.55, 0.85])
    replicates = int(config["sample_counts"]["agents_per_family"])
    specs: list[AgentSpec] = []
    for seed in config["seeds"]["agents"]:
        specs.extend(generate_agent_specs(int(seed), replicates, levels))
    ids = [spec.agent_id for spec in specs]
    if len(ids) != len(set(ids)):
        raise RuntimeError("agent generator produced duplicate agent IDs")
    return specs


def _measure_q(spec: AgentSpec, config: Mapping[str, Any]) -> float:
    """Measure clean pre-perturbation competence on the baseline namespace."""

    measurements: list[float] = []
    count = int(config["sample_counts"]["baseline_cases"])
    baseline_namespace = str(config["split_namespaces"]["baseline"])
    for seed in config["seeds"]["baseline"]:
        rng = np.random.default_rng(
            _stable_seed(int(seed), spec.agent_id, baseline_namespace)
        )
        measurements.extend(
            _clip01(spec.baseline_q + float(value))
            for value in rng.normal(0.0, 0.006, size=count)
        )
    return float(math.fsum(measurements) / len(measurements))


def _measure_a(
    spec: AgentSpec,
    calibration: Iterable[DiagnosticEvidence],
) -> float:
    """Measure ordinary parameter-shift recovery on a disjoint suite."""

    values = [
        evaluate_revision(spec, evidence, 0)["recovery"]
        for evidence in calibration
        if evidence.failure is FailureDepth.PARAMETER
    ]
    if not values:
        raise RuntimeError("standard-adaptation battery has no parameter failures")
    return float(math.fsum(values) / len(values))


def _measure_e(spec: AgentSpec, evidence: Iterable[DiagnosticEvidence]) -> float:
    """Measure pre-correction error magnitude without reading outcomes."""

    # Current competence affects the magnitude of pre-correction task loss,
    # while the evidence generator fixes the perturbation itself.  This is
    # deliberately separate from diagnostic class discrimination.
    scale = 1.05 - 0.15 * float(spec.baseline_q)
    values = [_clip01(item.error_magnitude * scale) for item in evidence]
    return float(math.fsum(values) / len(values))


def _diagnose(
    agent: SyntheticAgent,
    evidence: Iterable[DiagnosticEvidence],
) -> list[DiagnosticRecord]:
    records: list[DiagnosticRecord] = []
    for item in evidence:
        observation = item.agent_view()
        records.append(
            DiagnosticRecord(
                agent_id=agent.spec.agent_id,
                controller_family=agent.spec.controller_family.value,
                case_id=item.case_id,
                generator_family=item.generator_family,
                structural_family_id=item.structural_family_id,
                failure=item.failure.label,
                q_sd=agent.diagnose(observation),
                error_magnitude=item.error_magnitude,
                nuisance=item.nuisance,
            )
        )
    return records


def _index_by_failure(
    evidence: Iterable[DiagnosticEvidence],
) -> dict[FailureDepth, list[DiagnosticEvidence]]:
    indexed: dict[FailureDepth, list[DiagnosticEvidence]] = defaultdict(list)
    for item in evidence:
        indexed[item.failure].append(item)
    return indexed


def _run_trials(
    agent: SyntheticAgent,
    adaptation: list[DiagnosticEvidence],
    transfer: list[DiagnosticEvidence],
    *,
    sd: float,
    q: float,
    e: float,
    a: float,
    recovery_threshold: float,
) -> list[TrialRecord]:
    transfer_by_failure = _index_by_failure(transfer)
    offsets: dict[FailureDepth, int] = defaultdict(int)
    trials: list[TrialRecord] = []

    for item in adaptation:
        candidates = transfer_by_failure[item.failure]
        if not candidates:
            raise RuntimeError(f"transfer battery has no {item.failure.label} cases")
        transfer_item = candidates[offsets[item.failure] % len(candidates)]
        offsets[item.failure] += 1

        observation = item.agent_view()
        q_sd = agent.diagnose(observation)
        revision_depth = agent.choose_revision(observation, q_sd)
        primary = evaluate_revision(agent.spec, item, revision_depth)
        transferred = evaluate_revision(agent.spec, transfer_item, revision_depth)
        recovery_followed = primary["recovery"] >= recovery_threshold
        trace = RevisionTrace(
            first_depth=revision_depth,
            maximum_depth=revision_depth,
            attempts=(revision_depth,),
            cost=primary["correction_cost"],
            recovery_followed=recovery_followed,
        )
        trials.append(
            TrialRecord(
                agent_id=agent.spec.agent_id,
                agent_group_id=agent.spec.agent_group_id,
                agent_family=agent.spec.controller_family.value,
                seed=int(agent.spec.seed),
                generator_family=item.generator_family,
                structural_family_id=item.structural_family_id,
                split=item.split,
                failure=item.failure.label,
                q_sd=q_sd,
                sd=sd,
                q=q,
                e=e,
                a=a,
                revision_trace=trace,
                d_revision=revision_depth,
                recovery=primary["recovery"],
                transfer=transferred["recovery"],
                retention=transferred["retention"],
                preservation=primary["preservation"],
                correction_cost=primary["correction_cost"],
                adaptation_case_id=item.case_id,
                transfer_case_id=transfer_item.case_id,
                transfer_generator_family=transfer_item.generator_family,
            )
        )
    return trials


def _status(
    config: Mapping[str, Any],
    validity: Mapping[str, Any],
    analysis: Mapping[str, Any],
    eligibility: Mapping[str, Any] | None = None,
) -> str:
    candidate_ready = bool(
        config.get("generator_scope", {}).get("evidence_ready", False)
    )
    if not validity["all_passed"]:
        return "benchmark_invalid"
    if config["mode"] == "smoke" or not candidate_ready:
        return "engineering_only"
    if not isinstance(eligibility, Mapping) or eligibility.get("eligible") is not True:
        return "benchmark_invalid"

    thresholds = config["thresholds"]
    minimum = float(thresholds.get("positive_min_delta_mae", 0.0))
    require_ci = bool(thresholds.get("positive_require_ci_lower_bound", True))
    delta = float(analysis["delta_mae"])
    interval = analysis.get("confidence_interval", analysis.get("ci95"))
    if not isinstance(interval, (list, tuple)) or len(interval) != 2:
        raise ValueError("evaluated analysis is missing its confidence interval")
    lower = float(interval[0])
    favorable = delta > minimum and (not require_ci or lower > minimum)
    if favorable:
        return "valid_positive"
    return "valid_negative"


def _is_evidence_bearing(
    config: Mapping[str, Any],
    validity: Mapping[str, Any],
    status: str,
    eligibility: Mapping[str, Any],
) -> bool:
    """Return the post-run evidence decision, retaining valid null results."""

    return bool(
        config.get("mode") == "evidence"
        and eligibility.get("eligible") is True
        and validity.get("all_passed") is True
        and status in {"valid_positive", "valid_negative"}
    )


def run_benchmark(
    config: dict[str, Any],
    *,
    repo_root: str | Path,
    output_dir: str | Path,
    manifest: dict[str, Any] | None = None,
    attestation: Mapping[str, Any] | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Execute one complete benchmark and write all required artifacts.

    A valid smoke run remains ``engineering_only``; a failed validity gate is
    reported as ``benchmark_invalid``. Evidence mode refuses to run without a
    separately built, frozen manifest that matches the supplied configuration.
    """

    validate_config(config)
    repo = Path(repo_root).resolve()
    output = Path(output_dir).resolve()
    if output.exists() and any(output.iterdir()) and not overwrite:
        raise FileExistsError(f"output directory is not empty: {output}")
    if config["mode"] == "evidence":
        if manifest is None:
            raise ValueError("evidence mode requires a frozen manifest")
        validate_frozen_manifest(manifest, config)
        validate_current_checkout(manifest, repo)
        run_manifest = manifest
    else:
        run_manifest = build_manifest(config, repo)
    eligibility = evaluate_evidence_eligibility(run_manifest, attestation)

    counts = config["sample_counts"]
    diagnostic_evidence = _battery(
        config, "diagnostic", int(counts["diagnostic_cases_per_failure"])
    )
    adaptation_evidence = _battery(
        config, "adaptation", int(counts["adaptation_cases_per_failure"])
    )
    transfer_evidence = _battery(
        config, "transfer", int(counts["transfer_cases_per_failure"])
    )
    calibration_evidence = _battery(
        config,
        "standard_adaptation",
        int(counts["standard_adaptation_cases"]),
    )
    agents = _agent_population(config)

    diagnostic_records: list[DiagnosticRecord] = []
    trial_records: list[TrialRecord] = []
    per_agent_diagnostics: dict[str, dict[str, Any]] = {}
    recovery_threshold = float(config["thresholds"]["intervention_success_min"])

    for spec in agents:
        agent = SyntheticAgent(spec)
        agent_diagnostics = _diagnose(agent, diagnostic_evidence)
        diagnostic_records.extend(agent_diagnostics)
        diag_summary = diagnostic_summary(agent_diagnostics, prior=(1 / 3, 1 / 3, 1 / 3))
        per_agent_diagnostics[spec.agent_id] = diag_summary
        sd = normalized_brier_sd(agent_diagnostics)
        q = _measure_q(spec, config)
        a = _measure_a(spec, calibration_evidence)
        e = _measure_e(spec, diagnostic_evidence)
        trial_records.extend(
            _run_trials(
                agent,
                adaptation_evidence,
                transfer_evidence,
                sd=sd,
                q=q,
                e=e,
                a=a,
                recovery_threshold=recovery_threshold,
            )
        )

    validity = evaluate_validity(
        diagnostic_records,
        trial_records,
        intervention_matrix(),
        interface_collision_exists(),
        config["thresholds"],
    )
    candidate_evidence_ready = bool(
        config["mode"] == "evidence"
        and config["generator_scope"].get("evidence_ready", False)
    )
    analysis_allowed = bool(
        validity["all_passed"]
        and (not candidate_evidence_ready or eligibility["eligible"])
    )
    if analysis_allowed:
        aggregated = aggregate_trials(trial_records)
        prediction = grouped_outer_prediction(
            aggregated,
            ridge_alpha=float(config["ridge"].get("alpha", 1.0)),
            bootstrap_unit=str(config["bootstrap"]["unit"]),
            bootstrap_confidence=float(config["bootstrap"]["confidence"]),
            n_bootstrap=int(config["bootstrap"]["replicates"]),
            seed=int(config["bootstrap"]["seed"]),
        )
        analysis_summary = prediction["summary"]
        predictions = prediction["predictions"]
    else:
        # Fail closed: an invalid benchmark does not get to inspect or publish
        # the preregistered M0/M1 hypothesis comparison.
        aggregated = []
        predictions = []
        analysis_summary = {
            "evaluated": False,
            "reason": (
                "validity_gates_failed"
                if not validity["all_passed"]
                else "evidence_eligibility_failed"
            ),
        }
    status = _status(config, validity, analysis_summary, eligibility)
    generator_scope = dict(config["generator_scope"])
    evidence_ready = bool(eligibility["eligible"])
    evidence_bearing = _is_evidence_bearing(
        config, validity, status, eligibility
    )
    run_id = str(run_manifest["run_id"])
    summary = {
        "run_id": run_id,
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "evidence_intended": config["mode"] == "evidence",
        "evidence_ready": evidence_ready,
        "evidence_bearing": evidence_bearing,
        "generator_scope": generator_scope,
        "evidence_eligibility": eligibility,
        "attestation_status": eligibility["attestation_status"],
        "independence_level": eligibility["independence_level"],
        "validity": validity,
        "analysis": analysis_summary,
        "diagnostics": {
            "overall": diagnostic_summary(
                diagnostic_records, prior=(1 / 3, 1 / 3, 1 / 3)
            ),
            "per_agent": per_agent_diagnostics,
        },
        "counts": {
            "agents": len(agents),
            "independent_agent_groups": len(
                {spec.agent_group_id for spec in agents}
            ),
            "diagnostic_records": len(diagnostic_records),
            "trial_records": len(trial_records),
            "aggregated_prediction_rows": len(aggregated),
        },
        "deviations": list(eligibility["reasons"]),
        "attempted_run_ids": [run_id],
        "claim_boundary": (
            "Evidence authority is limited to whether prospective failure-depth diagnosis "
            "predicts held-out recovery under the frozen supplied correction architecture. "
            "Selection among supplied revisions is not representation invention. This result "
            "does not support causal efficacy, G_rep, Controlled Representational Escape, "
            "FC_open, creativity or universal intelligence, or recursive improvement of "
            "C_improve."
        ),
    }
    write_run_artifacts(
        output,
        manifest=run_manifest,
        diagnostic_records=diagnostic_records,
        trial_records=trial_records,
        validity=validity,
        predictions=predictions,
        summary=summary,
        attestation=attestation,
        eligibility=eligibility,
    )
    return summary
