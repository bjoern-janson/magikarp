from __future__ import annotations

import dataclasses
import unittest
from collections import Counter, defaultdict

from magikarp.agents import SyntheticAgent, generate_agent_specs
from magikarp.environment import (
    BUILTIN_STRUCTURAL_FAMILY_ID,
    evaluate_revision,
    generate_diagnostic_evidence,
    interface_collision_exists,
    intervention_matrix,
    oracle_accuracy,
)
from magikarp.types import AgentSpec, ControllerFamily, FailureDepth


class EnvironmentTests(unittest.TestCase):
    def test_evidence_is_balanced_deterministic_and_namespaced(self) -> None:
        first = generate_diagnostic_evidence(17, "diagnostic", 7, "battery-a")
        second = generate_diagnostic_evidence(17, "diagnostic", 7, "battery-a")
        changed = generate_diagnostic_evidence(18, "diagnostic", 7, "battery-a")

        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)
        self.assertEqual(len(first), 21)
        self.assertEqual(Counter(item.failure for item in first), {depth: 7 for depth in FailureDepth})
        self.assertEqual(len({item.case_id for item in first}), len(first))
        self.assertTrue(all("parameter" not in item.case_id for item in first))
        self.assertTrue(all("model" not in item.generator_family for item in first))
        self.assertTrue(all("interface" not in item.generator_family for item in first))
        self.assertTrue(all(item.split == "diagnostic" for item in first))
        self.assertEqual(
            {item.structural_family_id for item in first},
            {BUILTIN_STRUCTURAL_FAMILY_ID},
        )

        other_split = generate_diagnostic_evidence(17, "transfer", 7, "battery-b")
        self.assertEqual(
            {item.structural_family_id for item in first + other_split},
            {"builtin_latent_context_v0.1"},
        )
        self.assertEqual(
            first[0].agent_view().structural_family_id,
            first[0].structural_family_id,
        )

    def test_nuisance_and_error_distributions_are_exactly_label_independent(self) -> None:
        evidence = generate_diagnostic_evidence(23, "diagnostic", 8, "paired")
        nuisance_by_failure = defaultdict(list)
        errors_by_failure = defaultdict(list)
        for item in evidence:
            nuisance_by_failure[item.failure].append(item.nuisance)
            errors_by_failure[item.failure].append(item.error_magnitude)

        reference_nuisance = sorted(nuisance_by_failure[FailureDepth.PARAMETER])
        reference_errors = sorted(errors_by_failure[FailureDepth.PARAMETER])
        for failure in FailureDepth:
            self.assertEqual(sorted(nuisance_by_failure[failure]), reference_nuisance)
            self.assertEqual(sorted(errors_by_failure[failure]), reference_errors)

    def test_signals_make_failure_depth_identifiable_in_expectation(self) -> None:
        evidence = generate_diagnostic_evidence(31, "diagnostic", 30, "signals")
        correct = sum(max(range(3), key=lambda index: item.signals[index]) == item.failure.value for item in evidence)
        self.assertGreater(correct / len(evidence), 0.95)

    def test_interventions_have_the_required_minimum_sufficient_depths(self) -> None:
        threshold = 0.80
        expected_minima = {
            FailureDepth.PARAMETER: 0,
            FailureDepth.MODEL: 1,
            FailureDepth.INTERFACE: 2,
        }
        matrix = intervention_matrix()
        self.assertEqual(set(matrix), {"parameter", "model", "interface"})
        for failure, expected in expected_minima.items():
            sufficient = [depth for depth in range(3) if oracle_accuracy(failure, depth) >= threshold]
            self.assertEqual(min(sufficient), expected)

        self.assertTrue(interface_collision_exists())

    def test_revision_outcomes_are_deterministic_decomposed_and_costly(self) -> None:
        spec = generate_agent_specs(4, 1, [0.8])[0]
        cases = generate_diagnostic_evidence(5, "adaptation", 2, "heldout")
        interface_case = next(item for item in cases if item.failure is FailureDepth.INTERFACE)
        parameter_case = next(item for item in cases if item.failure is FailureDepth.PARAMETER)

        shallow = evaluate_revision(spec, interface_case, 0)
        deep = evaluate_revision(spec, interface_case, 2)
        self.assertEqual(deep, evaluate_revision(spec, interface_case, 2))
        self.assertEqual(
            set(deep),
            {"recovery", "transfer", "retention", "preservation", "correction_cost"},
        )
        self.assertGreater(deep["recovery"], shallow["recovery"])
        self.assertGreater(deep["correction_cost"], shallow["correction_cost"])
        self.assertTrue(all(0.0 <= deep[key] <= 1.0 for key in ("recovery", "transfer", "retention", "preservation")))

        parameter_shallow = evaluate_revision(spec, parameter_case, 0)
        parameter_deep = evaluate_revision(spec, parameter_case, 2)
        self.assertGreater(parameter_deep["correction_cost"], parameter_shallow["correction_cost"])
        self.assertLess(parameter_deep["preservation"], parameter_shallow["preservation"])


class AgentTests(unittest.TestCase):
    def test_population_is_fully_crossed_and_block_matched(self) -> None:
        levels = [0.15, 0.55, 0.95]
        specs = generate_agent_specs(101, 3, levels)
        self.assertEqual(len(specs), 3 * len(levels) * len(ControllerFamily))
        self.assertEqual(len({spec.agent_id for spec in specs}), len(specs))

        counts = Counter((spec.diagnostic_skill, spec.controller_family) for spec in specs)
        for level in levels:
            for family in ControllerFamily:
                self.assertEqual(counts[(level, family)], 3)

        for replicate in range(3):
            block = [spec for spec in specs if f"r{replicate:03d}" in spec.agent_id]
            self.assertEqual(len({spec.execution_skill for spec in block}), 1)
            self.assertEqual(len({spec.baseline_q for spec in block}), 1)
            self.assertEqual(len({spec.standard_adaptation for spec in block}), 1)

        self.assertEqual(specs, generate_agent_specs(101, 3, levels))
        other_seed_ids = {spec.agent_id for spec in generate_agent_specs(102, 3, levels)}
        self.assertTrue({spec.agent_id for spec in specs}.isdisjoint(other_seed_ids))

        evidence = generate_diagnostic_evidence(77, "diagnostic", 1, "crossed")[0]
        observation = evidence.agent_view()
        matched = [
            SyntheticAgent(spec).diagnose(observation)
            for spec in specs
            if "r000-s00" in spec.agent_id
        ]
        self.assertEqual(len(set(matched)), 1)

        for replicate in range(3):
            block = [spec for spec in specs if f"r{replicate:03d}" in spec.agent_id]
            self.assertEqual(len({spec.agent_group_id for spec in block}), 1)
        self.assertEqual(len({spec.agent_group_id for spec in specs}), 3)

    def test_diagnosis_is_probabilistic_deterministic_and_label_blind(self) -> None:
        evidence = generate_diagnostic_evidence(7, "diagnostic", 1, "blind")[0]
        observation = evidence.agent_view()
        spec = generate_agent_specs(8, 1, [0.8])[0]
        agent = SyntheticAgent(spec)
        q_sd = agent.diagnose(observation)

        relabelled = dataclasses.replace(
            evidence,
            failure=FailureDepth((evidence.failure.value + 1) % 3),
        )
        renamed = dataclasses.replace(
            observation,
            case_id="deliberately-different-case-id",
            generator_family="deliberately-different-family",
        )
        self.assertFalse(hasattr(observation, "failure"))
        with self.assertRaisesRegex(TypeError, "label-free"):
            agent.diagnose(evidence)  # type: ignore[arg-type]
        self.assertEqual(q_sd, agent.diagnose(observation))
        self.assertEqual(q_sd, agent.diagnose(relabelled.agent_view()))
        self.assertEqual(q_sd, agent.diagnose(renamed))
        self.assertAlmostEqual(sum(q_sd), 1.0)
        self.assertTrue(all(0.0 <= probability <= 1.0 for probability in q_sd))

    def test_higher_skill_improves_prospective_diagnosis(self) -> None:
        evidence = generate_diagnostic_evidence(19, "diagnostic", 25, "skill")
        specs = generate_agent_specs(20, 1, [0.05, 0.95])
        low = SyntheticAgent(next(spec for spec in specs if spec.diagnostic_skill == 0.05 and spec.controller_family is ControllerFamily.RIGID))
        high = SyntheticAgent(next(spec for spec in specs if spec.diagnostic_skill == 0.95 and spec.controller_family is ControllerFamily.RIGID))

        def mean_true_probability(agent: SyntheticAgent) -> float:
            return sum(
                agent.diagnose(item.agent_view())[item.failure.value]
                for item in evidence
            ) / len(evidence)

        self.assertGreater(mean_true_probability(high), mean_true_probability(low) + 0.25)

    def test_controllers_are_separable_from_diagnostic_quality(self) -> None:
        evidence = next(
            item
            for item in generate_diagnostic_evidence(6, "adaptation", 3, "controllers")
            if item.failure is FailureDepth.MODEL
        )
        observation = evidence.agent_view()
        specs = generate_agent_specs(3, 1, [0.7])
        by_family = {spec.controller_family: SyntheticAgent(spec) for spec in specs}
        arbitrary_q = (0.05, 0.90, 0.05)

        with self.assertRaisesRegex(TypeError, "label-free"):
            by_family[ControllerFamily.RIGID].choose_revision(  # type: ignore[arg-type]
                evidence, arbitrary_q
            )
        self.assertEqual(
            by_family[ControllerFamily.RIGID].choose_revision(
                observation, arbitrary_q
            ),
            0,
        )
        self.assertEqual(
            by_family[ControllerFamily.HYPERPLASTIC].choose_revision(
                observation, arbitrary_q
            ),
            2,
        )
        self.assertEqual(
            by_family[ControllerFamily.DEPTH_AWARE].choose_revision(
                observation, arbitrary_q
            ),
            1,
        )

        heuristic = by_family[ControllerFamily.EVIDENCE_HEURISTIC]
        self.assertEqual(
            heuristic.choose_revision(observation, (0.98, 0.01, 0.01)),
            heuristic.choose_revision(observation, (0.01, 0.01, 0.98)),
        )


if __name__ == "__main__":
    unittest.main()
