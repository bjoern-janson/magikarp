"""Shared, JSON-friendly benchmark types.

The types preserve the preflight's empirical boundaries:

    failure -> prospective diagnosis -> revision selection -> outcome

Diagnosis is never inferred from revision choice or recovery.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import IntEnum, StrEnum
from typing import Any


class FailureDepth(IntEnum):
    """Experimenter-controlled minimum sufficient intervention depth."""

    PARAMETER = 0
    MODEL = 1
    INTERFACE = 2

    @property
    def label(self) -> str:
        return self.name.lower()


class ControllerFamily(StrEnum):
    """Revision policies crossed with diagnostic quality."""

    RIGID = "rigid"
    HYPERPLASTIC = "hyperplastic"
    DEPTH_AWARE = "depth_aware"
    EVIDENCE_HEURISTIC = "evidence_heuristic"


@dataclass(frozen=True)
class DiagnosticObservation:
    """Label-free pre-adaptation evidence exposed to an agent."""

    case_id: str
    split: str
    generator_family: str
    structural_family_id: str
    signals: tuple[float, float, float]
    error_magnitude: float
    nuisance: tuple[float, float, float]


@dataclass(frozen=True)
class DiagnosticEvidence:
    """Evaluator-owned evidence including experimenter-only ground truth."""

    case_id: str
    split: str
    generator_family: str
    structural_family_id: str
    failure: FailureDepth
    signals: tuple[float, float, float]
    error_magnitude: float
    nuisance: tuple[float, float, float]

    def agent_view(self) -> DiagnosticObservation:
        """Return the only evidence representation agent APIs may accept."""

        return DiagnosticObservation(
            case_id=self.case_id,
            split=self.split,
            generator_family=self.generator_family,
            structural_family_id=self.structural_family_id,
            signals=self.signals,
            error_magnitude=self.error_magnitude,
            nuisance=self.nuisance,
        )


@dataclass(frozen=True)
class AgentSpec:
    """One crossed condition within an independently sampled agent group."""

    agent_id: str
    agent_group_id: str
    controller_family: ControllerFamily
    diagnostic_skill: float
    execution_skill: float
    baseline_q: float
    standard_adaptation: float
    seed: int


@dataclass(frozen=True)
class DiagnosticRecord:
    agent_id: str
    controller_family: str
    case_id: str
    generator_family: str
    structural_family_id: str
    failure: str
    q_sd: tuple[float, float, float]
    error_magnitude: float
    nuisance: tuple[float, float, float]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RevisionTrace:
    first_depth: int
    maximum_depth: int
    attempts: tuple[int, ...]
    cost: float
    recovery_followed: bool


@dataclass(frozen=True)
class TrialRecord:
    """One adaptation trial with its independent agent-group identity."""

    agent_id: str
    agent_group_id: str
    agent_family: str
    seed: int
    generator_family: str
    structural_family_id: str
    split: str
    failure: str
    q_sd: tuple[float, float, float]
    sd: float
    q: float
    e: float
    a: float
    revision_trace: RevisionTrace
    d_revision: int
    recovery: float
    transfer: float
    retention: float
    preservation: float
    correction_cost: float
    adaptation_case_id: str | None = None
    transfer_case_id: str | None = None
    transfer_generator_family: str | None = None

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["revision_trace"] = asdict(self.revision_trace)
        return data
