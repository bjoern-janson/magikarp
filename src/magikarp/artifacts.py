"""Artifact writers for independently recomputable benchmark runs."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np


def _json_default(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=_json_default) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: Iterable[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            if is_dataclass(row):
                row = asdict(row)
            handle.write(json.dumps(row, sort_keys=True, default=_json_default) + "\n")


def write_csv(path: Path, rows: list[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(value, sort_keys=True, default=_json_default)
                    if isinstance(value, (dict, list, tuple))
                    else value
                    for key, value in row.items()
                }
            )


def render_summary(summary: Mapping[str, Any]) -> str:
    analysis = summary.get("analysis", {})
    validity = summary.get("validity", {})
    counts = summary.get("counts", {})
    confidence = analysis.get("confidence_level")
    interval = analysis.get("confidence_interval", analysis.get("ci95", "n/a"))
    interval_label = (
        f"{100.0 * float(confidence):g}% paired interval"
        if isinstance(confidence, (int, float))
        else "Paired interval"
    )
    lines = [
        "# MAGIKARP v0.1 run summary",
        "",
        f"- Run ID: `{summary.get('run_id', 'unknown')}`",
        f"- Run timestamp: `{summary.get('run_timestamp_utc', 'unknown')}`",
        f"- Status: `{summary.get('status', 'unknown')}`",
        f"- Evidence intended: `{str(summary.get('evidence_intended', False)).lower()}`",
        f"- Evidence ready: `{str(summary.get('evidence_ready', False)).lower()}`",
        f"- Evidence-bearing: `{str(summary.get('evidence_bearing', False)).lower()}`",
        f"- Attestation status: `{summary.get('attestation_status', 'missing')}`",
        f"- Independence level: `{summary.get('independence_level', 'unknown')}`",
        f"- Validity gates passed: `{str(validity.get('all_passed', False)).lower()}`",
        f"- Composite agents: `{analysis.get('n_agents', counts.get('agents', 0))}`",
        f"- Independent agent groups: `{analysis.get('n_agent_groups', counts.get('independent_agent_groups', 0))}`",
        f"- Generator families: `{analysis.get('n_generator_families', 0)}`",
        "",
        "## Frozen primary comparison",
        "",
    ]
    if analysis.get("evaluated", True):
        lines.extend(
            [
                "`M0: R_c ~ Q + A + E`",
                "",
                "`M1: R_c ~ Q + A + E + SD`",
                "",
                f"- MAE(M0): `{analysis.get('mae_m0', 'n/a')}`",
                f"- MAE(M1): `{analysis.get('mae_m1', 'n/a')}`",
                f"- Delta MAE: `{analysis.get('delta_mae', 'n/a')}`",
                f"- {interval_label}: `{interval}`",
            ]
        )
    else:
        reason = analysis.get("reason", "prerequisite_failed")
        lines.append(f"Not evaluated: `{reason}` before the primary comparison.")
    lines.extend(["", "## Interpretation boundary", ""])

    if summary.get("evidence_bearing") and validity.get("all_passed"):
        lines.append(
            "This status is interpreted only under the frozen manifest and passed validity gates. "
            "It is predictive, not causal."
        )
    elif (
        summary.get("evidence_intended")
        and summary.get("generator_scope", {}).get("implementation")
        == "builtin_latent_context_v0.1"
    ):
        lines.append(
            "The built-in single-generator scope is engineering-only. Its family labels are "
            "namespaced buckets, not structurally independent evidence families."
        )
    elif summary.get("evidence_intended"):
        lines.append(
            "This evidence-intended run failed a readiness or validity condition and is not "
            "evidence for or against the MAGIKARP hypothesis."
        )
    else:
        lines.append(
            "This is an engineering run. It exercises the operational loop and is not evidence "
            "for or against the MAGIKARP hypothesis."
        )
    claim_boundary = summary.get("claim_boundary")
    if isinstance(claim_boundary, str) and claim_boundary.strip():
        lines.extend(["", f"Claim boundary: {claim_boundary}"])
    eligibility = summary.get("evidence_eligibility", {})
    reasons = eligibility.get("reasons", []) if isinstance(eligibility, Mapping) else []
    if reasons:
        lines.extend(
            [
                "",
                "Eligibility failures: " + ", ".join(f"`{reason}`" for reason in reasons),
            ]
        )
    lines.append("")
    return "\n".join(lines)


def write_run_artifacts(
    output_dir: Path,
    *,
    manifest: Mapping[str, Any],
    diagnostic_records: Iterable[Any],
    trial_records: Iterable[Any],
    validity: Mapping[str, Any],
    predictions: list[Mapping[str, Any]],
    summary: Mapping[str, Any],
    attestation: Mapping[str, Any] | None = None,
    eligibility: Mapping[str, Any] | None = None,
) -> None:
    """Write the required preflight artifacts plus raw diagnostics."""

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "manifest.json", manifest)
    if attestation is not None:
        write_json(output_dir / "attestation.json", attestation)
    write_json(output_dir / "evidence_eligibility.json", eligibility or {})
    write_jsonl(output_dir / "diagnostic_records.jsonl", diagnostic_records)
    write_jsonl(output_dir / "trial_records.jsonl", trial_records)
    write_json(output_dir / "validity.json", validity)
    write_csv(output_dir / "predictions.csv", predictions)
    write_json(output_dir / "summary.json", summary)
    (output_dir / "summary.md").write_text(render_summary(summary), encoding="utf-8")
