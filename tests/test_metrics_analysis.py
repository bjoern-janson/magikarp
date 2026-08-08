from __future__ import annotations

import math
import unittest

from magikarp.analysis import (
    aggregate_trials,
    grouped_outer_prediction,
    paired_generator_bootstrap,
)
from magikarp.metrics import (
    class_balanced_brier_skill_score,
    diagnostic_summary,
    normalized_brier_sd,
)
from magikarp.types import RevisionTrace, TrialRecord


def trial(
    *,
    agent_id: str,
    generator_family: str,
    failure: str,
    recovery: float,
    q: float = 0.5,
    a: float = 0.5,
    e: float = 0.5,
    sd: float = 0.5,
    seed: int = 1,
    agent_group_id: str | None = None,
) -> TrialRecord:
    return TrialRecord(
        agent_id=agent_id,
        agent_group_id=agent_group_id or agent_id,
        agent_family="test",
        seed=seed,
        generator_family=generator_family,
        structural_family_id="fixture-structural-family",
        split="adaptation",
        failure=failure,
        q_sd=(1 / 3, 1 / 3, 1 / 3),
        sd=sd,
        q=q,
        e=e,
        a=a,
        revision_trace=RevisionTrace(
            first_depth=0,
            maximum_depth=0,
            attempts=(0,),
            cost=0.1,
            recovery_followed=True,
        ),
        d_revision=0,
        recovery=recovery,
        transfer=recovery - 0.01,
        retention=recovery - 0.02,
        preservation=0.9,
        correction_cost=0.1,
    )


class DiagnosticMetricTests(unittest.TestCase):
    def test_normalized_brier_sd_has_frozen_endpoints(self) -> None:
        perfect = [
            {"failure": "parameter", "q_sd": (1.0, 0.0, 0.0)},
            {"failure": "model", "q_sd": (0.0, 1.0, 0.0)},
            {"failure": "interface", "q_sd": (0.0, 0.0, 1.0)},
        ]
        maximally_wrong = [
            {"failure": "parameter", "q_sd": (0.0, 1.0, 0.0)},
            {"failure": "model", "q_sd": (0.0, 0.0, 1.0)},
            {"failure": "interface", "q_sd": (1.0, 0.0, 0.0)},
        ]
        self.assertEqual(normalized_brier_sd(perfect), 1.0)
        self.assertEqual(normalized_brier_sd(maximally_wrong), 0.0)

    def test_class_balanced_skill_exposes_high_raw_prior_score(self) -> None:
        records = [
            {"failure": "parameter", "q_sd": (0.9, 0.05, 0.05)}
            for _ in range(18)
        ] + [
            {"failure": "model", "q_sd": (0.9, 0.05, 0.05)},
            {"failure": "interface", "q_sd": (0.9, 0.05, 0.05)},
        ]
        self.assertGreater(normalized_brier_sd(records), 0.9)
        self.assertAlmostEqual(class_balanced_brier_skill_score(records), 0.0)

    def test_summary_reports_secondary_diagnostics(self) -> None:
        records = [
            {"failure": "parameter", "q_sd": (0.8, 0.1, 0.1)},
            {"failure": "model", "q_sd": (0.2, 0.7, 0.1)},
            {"failure": "interface", "q_sd": (0.6, 0.2, 0.2)},
        ]
        summary = diagnostic_summary(records, prior=(1 / 3, 1 / 3, 1 / 3))
        self.assertAlmostEqual(summary["top1_accuracy"], 2 / 3)
        self.assertEqual(summary["per_class"]["interface"]["recall"], 0.0)
        self.assertEqual(summary["reference_prior_source"], "frozen")
        self.assertGreaterEqual(summary["mean_entropy_normalized"], 0.0)
        self.assertLessEqual(summary["mean_entropy_normalized"], 1.0)

    def test_invalid_distribution_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "sum to 1"):
            normalized_brier_sd(
                [{"failure": "parameter", "q_sd": (0.8, 0.8, 0.0)}]
            )


class PredictiveAnalysisTests(unittest.TestCase):
    def test_aggregation_prevents_episode_pseudoreplication(self) -> None:
        records = [
            trial(agent_id="a0", generator_family="g0", failure="parameter", recovery=0.2),
            trial(agent_id="a0", generator_family="g0", failure="parameter", recovery=0.6),
            trial(agent_id="a0", generator_family="g1", failure="model", recovery=0.8),
        ]
        rows = aggregate_trials(records)
        self.assertEqual(len(rows), 2)
        first = next(row for row in rows if row["generator_family"] == "g0")
        self.assertEqual(first["n_trials"], 2)
        self.assertAlmostEqual(first["recovery"], 0.4)
        self.assertAlmostEqual(first["transfer"], 0.39)

    def test_failure_is_a_separate_stratum_within_generator(self) -> None:
        records = [
            trial(agent_id="a0", generator_family="g0", failure="parameter", recovery=0.2),
            trial(agent_id="a0", generator_family="g0", failure="model", recovery=0.6),
        ]
        rows = aggregate_trials(records)
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["failure"] for row in rows}, {"parameter", "model"})

    def test_two_way_outer_prediction_favors_informative_sd(self) -> None:
        rows = []
        failures = ("parameter", "model", "interface")
        for agent_index in range(6):
            sd = 0.1 + 0.15 * agent_index
            for generator_index in range(6):
                e = generator_index / 10
                rows.append(
                    {
                        "agent_id": f"a{agent_index}",
                        "structural_family_id": "fixture-structural-family",
                        "generator_family": f"g{generator_index}",
                        "failure": failures[generator_index % len(failures)],
                        "q": 0.5,
                        "a": 0.5,
                        "e": e,
                        "sd": sd,
                        "recovery": 0.05 + 0.8 * sd + 0.1 * e,
                    }
                )

        result = grouped_outer_prediction(
            rows, ridge_alpha=0.01, n_bootstrap=250, seed=71
        )
        self.assertEqual(len(result["predictions"]), 36)
        self.assertGreater(result["summary"]["delta_mae"], 0.0)
        self.assertEqual(result["summary"]["n_agents"], 6)
        self.assertEqual(result["summary"]["n_generator_families"], 6)
        self.assertEqual(set(result["summary"]["per_failure"]), set(failures))
        # Each fold excludes 1/6 of agents and 1/6 of families: 5 x 5 cells.
        self.assertTrue(
            all(row["train_rows"] == 25 for row in result["predictions"])
        )
        self.assertEqual(
            result,
            grouped_outer_prediction(
                rows, ridge_alpha=0.01, n_bootstrap=250, seed=71
            ),
        )

    def test_outer_prediction_excludes_entire_shared_agent_block(self) -> None:
        rows = []
        for group_index in range(3):
            for sibling_index in range(2):
                for generator_index in range(3):
                    rows.append(
                        {
                            "agent_id": f"a{group_index}-{sibling_index}",
                            "agent_group_id": f"block-{group_index}",
                            "structural_family_id": "fixture-structural-family",
                            "generator_family": f"g{generator_index}",
                            "failure": ("parameter", "model", "interface")[
                                generator_index
                            ],
                            "q": 0.5,
                            "a": 0.5,
                            "e": generator_index / 10,
                            "sd": 0.2 + 0.2 * group_index,
                            "recovery": 0.3 + 0.1 * sibling_index,
                        }
                    )
        result = grouped_outer_prediction(rows, n_bootstrap=20, seed=2)
        self.assertEqual(result["summary"]["n_agents"], 6)
        self.assertEqual(result["summary"]["n_agent_groups"], 3)
        # A fold holds out two sibling composites and one generator. Training
        # therefore contains 2 remaining blocks x 2 siblings x 2 generators.
        self.assertTrue(
            all(row["train_rows"] == 8 for row in result["predictions"])
        )

    def test_bootstrap_honors_frozen_unit_and_confidence(self) -> None:
        predictions = [
            {
                "agent_id": "a0",
                "agent_group_id": "block-0",
                "generator_family": "g0",
                "abs_error_m0": 0.5,
                "abs_error_m1": 0.1,
            },
            {
                "agent_id": "a1",
                "agent_group_id": "block-1",
                "generator_family": "g0",
                "abs_error_m0": 0.1,
                "abs_error_m1": 0.2,
            },
        ]
        from magikarp.analysis import paired_group_bootstrap

        summary = paired_group_bootstrap(
            predictions,
            unit="agent",
            confidence=0.8,
            n_bootstrap=100,
            seed=4,
        )
        self.assertEqual(summary["unit"], "agent")
        self.assertEqual(summary["group_field"], "agent_group_id")
        self.assertEqual(summary["confidence"], 0.8)
        self.assertNotIn("ci95", summary)

    def test_paired_bootstrap_uses_generator_means(self) -> None:
        predictions = [
            {"generator_family": "g0", "abs_error_m0": 0.5, "abs_error_m1": 0.1},
            {"generator_family": "g0", "abs_error_m0": 0.4, "abs_error_m1": 0.2},
            {"generator_family": "g1", "abs_error_m0": 0.1, "abs_error_m1": 0.2},
            {"generator_family": "g1", "abs_error_m0": 0.2, "abs_error_m1": 0.3},
        ]
        first = paired_generator_bootstrap(predictions, n_bootstrap=100, seed=9)
        second = paired_generator_bootstrap(predictions, n_bootstrap=100, seed=9)
        self.assertEqual(first, second)
        self.assertTrue(math.isclose(first["estimate"], 0.1, abs_tol=1e-12))
        self.assertEqual(first["unit"], "generator_family")


if __name__ == "__main__":
    unittest.main()
