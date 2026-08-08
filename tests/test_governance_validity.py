from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from magikarp.config import (
    evidence_config,
    load_config,
    smoke_config,
    validate_config,
)
from magikarp.eligibility import manifest_hash
from magikarp.manifest import (
    build_manifest,
    load_manifest,
    validate_current_checkout,
    validate_frozen_manifest,
    write_manifest,
)
from magikarp.types import DiagnosticRecord, RevisionTrace, TrialRecord
from magikarp.validity import evaluate_validity


class ConfigurationTests(unittest.TestCase):
    def test_templates_freeze_agent_population_and_ridge_alpha(self) -> None:
        for config in (smoke_config(), evidence_config()):
            validate_config(config)
            self.assertEqual(
                config["agent_population"]["diagnostic_skill_levels"],
                [0.25, 0.55, 0.85],
            )
            self.assertEqual(
                config["agent_population"]["controllers"],
                ["rigid", "hyperplastic", "depth_aware", "evidence_heuristic"],
            )
            self.assertEqual(config["ridge"]["alpha"], 1.0)
            self.assertIn(config["ridge"]["alpha"], config["ridge"]["alphas"])
            self.assertTrue(config["thresholds"]["positive_require_ci_lower_bound"])
            self.assertEqual(
                config["generator_scope"],
                {
                    "implementation": "builtin_latent_context_v0.1",
                    "family_labels": "namespaced_buckets_single_generator",
                    "structurally_distinct_families": False,
                    "external_families": False,
                    "evidence_ready": False,
                },
            )
        self.assertEqual(smoke_config()["thresholds"]["positive_min_delta_mae"], 0.0)
        self.assertEqual(evidence_config()["thresholds"]["positive_min_delta_mae"], 0.005)

    def test_population_and_ridge_choices_cannot_drift(self) -> None:
        config = smoke_config()
        config["agent_population"]["diagnostic_skill_levels"][0] = 0.20
        with self.assertRaisesRegex(ValueError, "diagnostic_skill_levels"):
            validate_config(config)

        config = smoke_config()
        config["agent_population"]["controllers"].reverse()
        with self.assertRaisesRegex(ValueError, "controllers"):
            validate_config(config)

        config = smoke_config()
        config["ridge"]["alpha"] = 2.0
        with self.assertRaisesRegex(ValueError, "ridge.alpha"):
            validate_config(config)

        config = evidence_config()
        config["thresholds"]["positive_min_delta_mae"] = 0.0
        with self.assertRaisesRegex(ValueError, "positive_min_delta_mae"):
            validate_config(config)

        config = smoke_config()
        config["thresholds"]["positive_require_ci_lower_bound"] = False
        with self.assertRaisesRegex(ValueError, "positive_require_ci_lower_bound"):
            validate_config(config)

        config = evidence_config()
        config["generator_scope"]["evidence_ready"] = True
        with self.assertRaisesRegex(ValueError, "generator_scope"):
            validate_config(config)

    def test_load_config_validates_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            path.write_text(json.dumps(smoke_config()), encoding="utf-8")
            self.assertEqual(load_config(path), smoke_config())

            path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "root"):
                load_config(path)


class ManifestTests(unittest.TestCase):
    def test_manifest_is_deterministic_and_round_trips(self) -> None:
        config = smoke_config()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = build_manifest(config, root)
            second = build_manifest(config, root)
            self.assertEqual(first, second)
            self.assertEqual(first["config"]["agent_population"], config["agent_population"])
            self.assertEqual(first["definitions"]["models"]["ridge"]["alpha"], 1.0)
            self.assertRegex(first["manifest_hash"], r"^[0-9a-f]{64}$")
            self.assertRegex(
                first["provenance"]["source_tree_hash"], r"^[0-9a-f]{64}$"
            )

            path = root / "manifest.json"
            write_manifest(first, path)
            self.assertEqual(load_manifest(path), first)
            validate_frozen_manifest(load_manifest(path), config)

    def test_evidence_manifest_rejects_unfrozen_and_mismatched_config(self) -> None:
        config = evidence_config()
        manifest = build_manifest(config, Path(__file__).resolve().parents[1])

        unfrozen = copy.deepcopy(manifest)
        unfrozen["frozen"] = False
        unfrozen["git"]["dirty"] = True
        unfrozen["manifest_hash"] = manifest_hash(unfrozen)
        with self.assertRaisesRegex(ValueError, "not frozen"):
            validate_frozen_manifest(unfrozen, config)

        changed = copy.deepcopy(config)
        changed["sample_counts"]["agents_per_family"] += 1
        with self.assertRaisesRegex(ValueError, "config hash"):
            validate_frozen_manifest(manifest, changed)

    def test_evidence_manifest_rejects_an_unrelated_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "executing package"):
                build_manifest(evidence_config(), temporary)

    def test_manifest_hash_detects_definition_tampering(self) -> None:
        manifest = build_manifest(smoke_config(), Path(__file__).resolve().parents[1])
        manifest["definitions"]["models"]["M0"] = ["post_outcome_rewrite"]
        with self.assertRaisesRegex(ValueError, "manifest_hash"):
            validate_frozen_manifest(manifest, smoke_config())

    def test_current_checkout_must_match_frozen_commit(self) -> None:
        manifest = build_manifest(smoke_config(), Path(__file__).resolve().parents[1])
        manifest["git"]["sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate_current_checkout(manifest, Path(__file__).resolve().parents[1])

    def test_current_runtime_must_match_frozen_manifest(self) -> None:
        manifest = build_manifest(smoke_config(), Path(__file__).resolve().parents[1])
        manifest["runtime"]["numpy"] = "0.0.invalid"
        with self.assertRaisesRegex(ValueError, "runtime does not match"):
            validate_current_checkout(manifest, Path(__file__).resolve().parents[1])

    def test_current_source_and_authority_must_match_manifest(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = build_manifest(smoke_config(), root)
        self.assertEqual(
            set(manifest["provenance"]["authority_files"]),
            {
                "docs/MAGIKARP_V0_1_BENCHMARK_CONTRACT.md",
                "docs/REVISION_CONTROLLER_CLARIFICATION.md",
                "docs/V0_1_EXECUTION_PREFLIGHT.md",
            },
        )
        manifest["provenance"]["source_tree_hash"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "executing source"):
            validate_current_checkout(manifest, root)


def _diagnostic_records() -> list[DiagnosticRecord]:
    records: list[DiagnosticRecord] = []
    for failure_index, failure in enumerate(("parameter", "model", "interface")):
        for replicate in range(2):
            q_sd = [0.05, 0.05, 0.05]
            q_sd[failure_index] = 0.90
            records.append(
                DiagnosticRecord(
                    agent_id=f"agent-{failure_index}-{replicate}",
                    controller_family="depth_aware",
                    case_id=f"case-{failure_index}-{replicate}",
                    generator_family="balanced-test",
                    structural_family_id="fixture-structural-family",
                    failure=failure,
                    q_sd=tuple(q_sd),
                    error_magnitude=1.0,
                    nuisance=(0.0, 0.0, 0.0),
                )
            )
    return records


def _trial(
    family: str,
    failure: str,
    depth: int,
    cost: float,
    recovery: float,
    q: float,
) -> TrialRecord:
    trace = RevisionTrace(
        first_depth=depth,
        maximum_depth=depth,
        attempts=(depth,),
        cost=cost,
        recovery_followed=True,
    )
    return TrialRecord(
        agent_id=f"{family}-{failure}-{depth}",
        agent_group_id=f"group-{family}",
        agent_family=family,
        seed=1,
        generator_family="balanced-test",
        structural_family_id="fixture-structural-family",
        split="adaptation",
        failure=failure,
        q_sd=(0.8, 0.1, 0.1),
        sd=0.8,
        q=q,
        e=0.5,
        a=0.5,
        revision_trace=trace,
        d_revision=depth,
        recovery=recovery,
        transfer=0.7,
        retention=0.7,
        preservation=0.7,
        correction_cost=cost,
    )


class ValidityTests(unittest.TestCase):
    def test_all_six_gates_pass_with_sequence_intervention_rows(self) -> None:
        config = smoke_config()
        trials = [
            _trial("rigid", "parameter", 0, 1.0, 0.9, 0.80),
            _trial("hyperplastic", "parameter", 2, 3.0, 0.9, 0.82),
            _trial("depth_aware", "interface", 2, 2.0, 0.9, 0.79),
        ]
        result = evaluate_validity(
            _diagnostic_records(),
            trials,
            {
                "parameter": (1.0, 1.0, 1.0),
                "model": (0.0, 1.0, 1.0),
                "interface": (0.0, 0.0, 1.0),
            },
            True,
            config["thresholds"],
        )
        self.assertTrue(result["all_passed"])
        self.assertEqual(set(result["gates"]), set("ABCDEF"))
        self.assertTrue(all(gate["passed"] for gate in result["gates"].values()))

    def test_live_interface_collision_failure_is_machine_readable(self) -> None:
        config = smoke_config()
        result = evaluate_validity(
            _diagnostic_records(),
            [
                _trial("rigid", "parameter", 0, 1.0, 0.9, 0.80),
                _trial("hyperplastic", "parameter", 2, 3.0, 0.9, 0.82),
                _trial("depth_aware", "interface", 2, 2.0, 0.9, 0.79),
            ],
            {
                "parameter": {0: True, 1: True, 2: True},
                "model": {0: False, 1: True, 2: True},
                "interface": {0: False, 1: False, 2: True},
            },
            False,
            config["thresholds"],
        )
        self.assertFalse(result["all_passed"])
        self.assertFalse(result["gates"]["B"]["passed"])
        self.assertFalse(result["gates"]["B"]["details"]["interface_collision"])


if __name__ == "__main__":
    unittest.main()
