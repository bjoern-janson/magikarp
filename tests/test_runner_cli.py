from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from magikarp.config import evidence_config, smoke_config
from magikarp.runner import _agent_population, _battery, _measure_q, _status, run_benchmark


REPO_ROOT = Path(__file__).resolve().parents[1]


def tiny_smoke_config() -> dict[str, object]:
    config = smoke_config()
    config["sample_counts"].update(
        {
            "agents_per_family": 2,
            "baseline_cases": 2,
            "standard_adaptation_cases": 2,
            "diagnostic_cases_per_failure": 2,
            "adaptation_cases_per_failure": 2,
            "transfer_cases_per_failure": 2,
        }
    )
    config["bootstrap"]["replicates"] = 20
    return config


class RunnerTests(unittest.TestCase):
    def test_primary_null_remains_negative_despite_secondary_heterogeneity(self) -> None:
        config = evidence_config()
        # Isolate the status classifier from the built-in generator's
        # fail-closed engineering scope.
        config["generator_scope"]["evidence_ready"] = True
        analysis = {
            "delta_mae": 0.0,
            "ci95": [-0.01, 0.01],
            "per_failure": {
                "parameter": {"delta_mae": 0.02},
                "model": {"delta_mae": -0.01},
                "interface": {"delta_mae": 0.0},
            },
        }
        self.assertEqual(
            _status(
                config,
                {"all_passed": True},
                analysis,
                {"eligible": True},
            ),
            "valid_negative",
        )

    def test_smoke_executes_full_loop_and_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first"
            second = Path(temporary) / "second"
            config = tiny_smoke_config()
            summary_a = run_benchmark(
                config, repo_root=REPO_ROOT, output_dir=first
            )
            summary_b = run_benchmark(
                config, repo_root=REPO_ROOT, output_dir=second
            )

            self.assertEqual(summary_a["status"], "engineering_only")
            self.assertFalse(summary_a["evidence_bearing"])
            self.assertFalse(summary_a["evidence_ready"])
            self.assertTrue(summary_a["validity"]["all_passed"])
            self.assertTrue(summary_a["analysis"]["evaluated"])
            self.assertEqual(summary_a["counts"]["independent_agent_groups"], 2)
            self.assertEqual(summary_a["analysis"], summary_b["analysis"])
            self.assertEqual(summary_a["counts"], summary_b["counts"])

            required = {
                "manifest.json",
                "evidence_eligibility.json",
                "diagnostic_records.jsonl",
                "trial_records.jsonl",
                "validity.json",
                "predictions.csv",
                "summary.json",
                "summary.md",
            }
            self.assertEqual(required, {path.name for path in first.iterdir()})
            persisted = json.loads((first / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(persisted["status"], "engineering_only")

    def test_invalid_gates_skip_primary_analysis(self) -> None:
        invalid = {"all_passed": False, "gates": {}}
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "invalid"
            with patch(
                "magikarp.runner.evaluate_validity", return_value=invalid
            ), patch("magikarp.runner.grouped_outer_prediction") as prediction:
                summary = run_benchmark(
                    tiny_smoke_config(),
                    repo_root=REPO_ROOT,
                    output_dir=output,
                )
            rendered = (output / "summary.md").read_text(encoding="utf-8")
        prediction.assert_not_called()
        self.assertEqual(summary["status"], "benchmark_invalid")
        self.assertFalse(summary["evidence_bearing"])
        self.assertFalse(summary["analysis"]["evaluated"])
        self.assertEqual(summary["analysis"]["reason"], "validity_gates_failed")
        self.assertIn("Not evaluated", rendered)
        self.assertNotIn("passed validity gates. It is predictive", rendered)

    def test_bootstrap_unit_and_confidence_are_operational(self) -> None:
        config = tiny_smoke_config()
        config["bootstrap"]["unit"] = "agent"
        config["bootstrap"]["confidence"] = 0.8
        with tempfile.TemporaryDirectory() as temporary:
            summary = run_benchmark(
                config,
                repo_root=REPO_ROOT,
                output_dir=Path(temporary) / "bootstrap",
            )
        self.assertEqual(summary["analysis"]["confidence_level"], 0.8)
        self.assertEqual(summary["analysis"]["bootstrap"]["unit"], "agent")
        self.assertNotIn("ci95", summary["analysis"])

    def test_frozen_namespaces_change_generated_data(self) -> None:
        original = tiny_smoke_config()
        changed = tiny_smoke_config()
        changed["split_namespaces"]["diagnostic"] = "alternate/diagnostic"
        first_cases = _battery(original, "diagnostic", 1)
        second_cases = _battery(changed, "diagnostic", 1)
        self.assertNotEqual(first_cases[0].case_id, second_cases[0].case_id)

        spec = _agent_population(original)[0]
        original_q = _measure_q(spec, original)
        changed["split_namespaces"]["baseline"] = "alternate/baseline"
        self.assertNotEqual(original_q, _measure_q(spec, changed))

    def test_evidence_mode_refuses_to_run_without_frozen_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "frozen manifest"):
                run_benchmark(
                    evidence_config(),
                    repo_root=REPO_ROOT,
                    output_dir=Path(temporary) / "evidence",
                )

    def test_nonempty_output_requires_explicit_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            output.mkdir()
            (output / "keep.txt").write_text("user data", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run_benchmark(
                    tiny_smoke_config(), repo_root=REPO_ROOT, output_dir=output
                )


if __name__ == "__main__":
    unittest.main()
