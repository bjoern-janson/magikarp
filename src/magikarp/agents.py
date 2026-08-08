"""Crossed synthetic diagnostic and revision-controller agents."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable, Sequence

import numpy as np

from .types import AgentSpec, ControllerFamily, DiagnosticObservation


def _stable_uint64(seed: int, *parts: object) -> int:
    material = "\x1f".join((str(int(seed)), *(str(part) for part in parts)))
    digest = hashlib.blake2b(material.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little", signed=False)


def _stable_unit(seed: int, *parts: object) -> float:
    # The high 53 bits map exactly onto the mantissa of a Python float.
    value = _stable_uint64(seed, *parts) >> 11
    return value / float(1 << 53)


def generate_agent_specs(
    seed: int,
    replicates: int,
    diagnostic_skill_levels: Iterable[float],
) -> list[AgentSpec]:
    """Create a fully crossed diagnostic-skill x controller population.

    Baseline competence, ordinary parameter-shift adaptation, and execution
    ability are matched within each replicate block.  Diagnostic skill is
    therefore not a disguised controller-family or general-competence label.
    """

    if isinstance(replicates, bool) or not isinstance(replicates, int):
        raise TypeError("replicates must be an integer")
    if replicates < 1:
        raise ValueError("replicates must be at least 1")

    levels = tuple(float(level) for level in diagnostic_skill_levels)
    if not levels:
        raise ValueError("diagnostic_skill_levels must not be empty")
    if any(not math.isfinite(level) or not 0.0 <= level <= 1.0 for level in levels):
        raise ValueError("diagnostic skill levels must be finite values in [0, 1]")
    if len(set(levels)) != len(levels):
        raise ValueError("diagnostic skill levels must be unique")

    specs: list[AgentSpec] = []
    # Keep the population seed visible for collision-free joins and artifact
    # audits.  ``n`` avoids an extra separator for the unusual negative seed.
    population_token = str(int(seed)).replace("-", "n")
    for replicate in range(replicates):
        agent_group_id = f"group-a{population_token}-r{replicate:03d}"
        # Matched block variables vary across genuinely independent synthetic
        # agents, not across controller/diagnosis conditions within a block.
        execution_skill = 0.78 + 0.16 * _stable_unit(seed, "execution", replicate)
        baseline_q = 0.80 + 0.08 * _stable_unit(seed, "baseline-q", replicate)
        standard_adaptation = 0.74 + 0.14 * _stable_unit(
            seed, "standard-adaptation", replicate
        )

        for level_index, diagnostic_skill in enumerate(levels):
            for controller in ControllerFamily:
                agent_seed = _stable_uint64(
                    seed,
                    "agent",
                    replicate,
                    level_index,
                    controller.value,
                )
                specs.append(
                    AgentSpec(
                        agent_id=(
                            f"agent-a{population_token}-r{replicate:03d}-"
                            f"s{level_index:02d}-"
                            f"{controller.value}"
                        ),
                        agent_group_id=agent_group_id,
                        controller_family=controller,
                        diagnostic_skill=diagnostic_skill,
                        execution_skill=execution_skill,
                        baseline_q=baseline_q,
                        standard_adaptation=standard_adaptation,
                        seed=agent_seed,
                    )
                )
    return specs


class SyntheticAgent:
    """A prospective diagnostic module paired with a revision controller."""

    def __init__(self, spec: AgentSpec):
        if not isinstance(spec, AgentSpec):
            raise TypeError("spec must be an AgentSpec")
        self.spec = spec

    def diagnose(self, evidence: DiagnosticObservation) -> tuple[float, float, float]:
        """Emit probabilities using pre-adaptation signals only.

        In particular, this method never reads ``evidence.failure``.  The
        diagnostic skill parameter controls how strongly the output trusts the
        admissible evidence rather than a uniform prior.
        """

        if not isinstance(evidence, DiagnosticObservation):
            raise TypeError("evidence must be a label-free DiagnosticObservation")

        signals = np.asarray(evidence.signals, dtype=float)
        if signals.shape != (3,) or not np.all(np.isfinite(signals)):
            raise ValueError("diagnostic signals must contain three finite values")

        # A small, agent-specific calibration offset supplies within-level
        # variation while preserving the requested crossed skill condition.
        # Strip only the controller suffix so the same replicate/skill
        # diagnostic module emits exactly the same q_SD when crossed with each
        # controller family.
        diagnostic_block_id = self.spec.agent_id.rsplit("-", 1)[0]
        calibration_offset = 0.04 * (
            2.0
            * _stable_unit(0, "diagnostic-calibration", diagnostic_block_id)
            - 1.0
        )
        effective_skill = float(
            np.clip(self.spec.diagnostic_skill + calibration_offset, 0.0, 1.0)
        )

        centered = signals - float(np.mean(signals))

        # At low skill, a deterministic case-specific idiosyncratic reading
        # can outrank the real evidence; merely mixing with a uniform prior
        # would reduce confidence without ever changing top-1 diagnosis.  This
        # construction gives the crossed population genuine discrimination
        # errors while keeping every input pre-adaptation and label-blind.  The
        # noise stream uses the explicitly label-balanced nuisance tuple, not
        # case IDs or generator-family names.
        idiosyncratic = np.asarray(
            [
                2.0
                * _stable_unit(
                    0,
                    "diagnostic-reading",
                    diagnostic_block_id,
                    evidence.nuisance,
                    index,
                )
                - 1.0
                for index in range(3)
            ],
            dtype=float,
        )
        logits = (
            effective_skill * 6.0 * centered
            + (1.0 - effective_skill) * 1.5 * idiosyncratic
        )
        logits -= float(np.max(logits))
        probabilities = np.exp(logits)
        probabilities /= float(np.sum(probabilities))
        return tuple(float(value) for value in probabilities)

    def choose_revision(
        self,
        evidence: DiagnosticObservation,
        q_sd: Sequence[float],
    ) -> int:
        """Choose one supplied revision depth according to controller family."""

        if not isinstance(evidence, DiagnosticObservation):
            raise TypeError("evidence must be a label-free DiagnosticObservation")
        probabilities = np.asarray(q_sd, dtype=float)
        if (
            probabilities.shape != (3,)
            or not np.all(np.isfinite(probabilities))
            or np.any(probabilities < 0.0)
            or not np.isclose(float(np.sum(probabilities)), 1.0, atol=1e-8)
        ):
            raise ValueError("q_sd must be a length-three probability distribution")

        family = self.spec.controller_family
        if family is ControllerFamily.RIGID:
            return 0
        if family is ControllerFamily.HYPERPLASTIC:
            return 2
        if family is ControllerFamily.DEPTH_AWARE:
            return int(np.argmax(probabilities))
        if family is ControllerFamily.EVIDENCE_HEURISTIC:
            # This matched policy ignores q_SD and uses fixed, preregisterable
            # thresholds on the raw admissible evidence.  It is not evidence
            # of representation invention and cannot request an unsupplied
            # action.
            parameter_signal, model_signal, interface_signal = evidence.signals
            if interface_signal >= 0.70 and interface_signal >= model_signal:
                return 2
            if model_signal >= 0.70 and model_signal >= parameter_signal:
                return 1
            return 0
        raise ValueError(f"unsupported controller family: {family!r}")
