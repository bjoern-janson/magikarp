from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from magikarp.eligibility import (
    canonical_hash,
    comparison_record_hash,
    evaluate_evidence_eligibility,
    generator_provenance_hash,
    load_attestation,
    manifest_hash,
    seal_attestation,
    write_attestation,
)
from magikarp.manifest import MANIFEST_VERSION
from magikarp.config import evidence_config, smoke_config
from magikarp.runner import _is_evidence_bearing, _status


REPO_ROOT = Path(__file__).resolve().parents[1]


SCIENTIFIC_HASH_FIELDS = (
    "benchmark_contract_hash",
    "evidence_protocol_hash",
    "generator_source_hash",
    "generator_provenance_hash",
    "controller_source_hash",
    "analysis_source_hash",
    "config_hash",
    "design_freeze_hash",
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _refresh_manifest(manifest: dict[str, object]) -> dict[str, object]:
    """Re-seal a hypothetical manifest after an intentional test mutation."""

    provenance = manifest.get("generator_provenance")
    if isinstance(provenance, dict):
        provenance["comparison_record_hash"] = comparison_record_hash(provenance)
        provenance["generator_provenance_hash"] = generator_provenance_hash(
            provenance
        )
        for field in (
            "structural_family_id",
            "generator_family",
            "generator_version",
            "generator_source_hash",
            "generator_provenance_hash",
        ):
            manifest[field] = provenance[field]

    design = manifest.get("design_freeze")
    if isinstance(design, dict):
        manifest["design_freeze_hash"] = canonical_hash(design)

    scientific = manifest.get("scientific_hashes")
    if isinstance(scientific, dict):
        for field in SCIENTIFIC_HASH_FIELDS:
            scientific[field] = manifest[field]

    manifest["manifest_hash"] = manifest_hash(manifest)
    return manifest


def _hypothetical_l2_manifest() -> dict[str, object]:
    """Return a schema fixture, not a claim that an eligible generator exists."""

    provenance: dict[str, object] = {
        "structural_family_id": "hypothetical_independent_family_v1",
        "generator_family": "hypothetical.external.synthetic",
        "generator_version": "1.0.0",
        "generator_source_hash": _digest("generator-source"),
        "author_or_origin": "hypothetical-external-lab",
        "generator_created_at_utc": "2026-01-02T03:04:05Z",
        "derived_from": [],
        "shared_source_code": [],
        "shared_helper_functions": [],
        "shared_task_abstractions": ["public MAGIKARP-v0.1 contract"],
        "shared_latent_failure_ontology": ["parameter", "model", "interface"],
        "shared_parameterization": [],
        "shared_labeling_logic": [],
        "shared_revision_controller_assumptions": ["supplied revision depths"],
        "shared_evaluation_assumptions": [],
        "known_shared_dependencies": ["Python"],
        "benchmark_internal_access": {
            "public_contract": True,
            "implementation": False,
            "prior_manifests": False,
            "prior_outcomes": False,
            "failed_runs": False,
        },
        "independence_level": "L2",
        "independence_reviewer_id": "hypothetical-independent-reviewer",
        "independence_rationale": "Independently authored schema fixture.",
        "independence_limitations": ["unit-test fixture only"],
        "comparison_record_hash": "",
        "generator_provenance_hash": "",
    }
    design_freeze: dict[str, object] = {
        "seed_policy": {
            "policy": "fixed-before-outcomes",
            "registered_run_ids": ["hypothetical-l2-run-001"],
            "seeds": [11, 13],
        },
        "group_assignment_policy": {
            "independent_unit": "agent_group_id",
            "structural_family_field": "structural_family_id",
        },
        "primary_endpoints": {"primary": "held_out_recovery"},
        "validity_gate_definitions": {
            "required": ["A", "B", "C", "D", "E", "F"]
        },
        "exclusion_rules": {
            "predeclared": [],
            "missing_data": "invalidates the run",
        },
        "bootstrap_or_interval_procedure": {
            "unit": "structural_family_id",
            "confidence": 0.95,
            "replicates": 4000,
        },
        "stopping_rule": {
            "planned_runs": ["hypothetical-l2-run-001"],
            "rule": "one preregistered run",
        },
        "evidence_classification_rules": {
            "positive": "valid_positive",
            "null": "valid_negative",
            "invalid": "benchmark_invalid",
        },
    }
    manifest: dict[str, object] = {
        "manifest_version": MANIFEST_VERSION,
        "mode": "evidence",
        "frozen": True,
        "benchmark_version": "MAGIKARP-v0.1",
        "benchmark_contract_hash": _digest("benchmark-contract"),
        "evidence_protocol_version": "0.1",
        "evidence_protocol_hash": _digest("evidence-protocol"),
        "run_id": "hypothetical-l2-run-001",
        "config_hash": _digest("frozen-config"),
        "controller_version": "0.1.0",
        "controller_source_hash": _digest("controller-source"),
        "analysis_version": "0.1.0",
        "analysis_source_hash": _digest("analysis-source"),
        "generator_scope": {
            "implementation": "hypothetical_external_v1",
            "structurally_distinct_families": True,
            "external_families": True,
            "evidence_ready": True,
        },
        "independence_level": "L2",
        "generator_provenance": provenance,
        "design_freeze": design_freeze,
        "scientific_hashes": {},
    }
    return _refresh_manifest(manifest)


def _attestation_for(manifest: dict[str, object]) -> dict[str, object]:
    return seal_attestation(
        {
            "schema_version": 1,
            "manifest_hash": manifest["manifest_hash"],
            "benchmark_contract_hash": manifest["benchmark_contract_hash"],
            "evidence_protocol_hash": manifest["evidence_protocol_hash"],
            "generator_source_hash": manifest["generator_source_hash"],
            "generator_provenance_hash": manifest["generator_provenance_hash"],
            "controller_source_hash": manifest["controller_source_hash"],
            "analysis_source_hash": manifest["analysis_source_hash"],
            "config_hash": manifest["config_hash"],
            "run_id": manifest["run_id"],
            "independence_level": manifest["independence_level"],
            "evidence_ready": True,
            "attestor_id": "hypothetical-independent-attestor",
            "attestor_independence": "independent",
            "attested_at_utc": "2026-01-03T04:05:06Z",
            "record_locator": "urn:test:immutable:hypothetical-l2-run-001",
            "status": "independent_verified",
        }
    )


class EvidenceEligibilityBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = _hypothetical_l2_manifest()
        self.attestation = _attestation_for(self.manifest)

    def test_complete_hypothetical_l2_fixture_is_schema_eligible(self) -> None:
        decision = evaluate_evidence_eligibility(self.manifest, self.attestation)
        self.assertTrue(decision["eligible"])
        self.assertEqual(decision["reasons"], [])
        self.assertEqual(decision["independence_level"], "L2")

    def test_builtin_cannot_be_promoted_by_fully_resealed_metadata(self) -> None:
        attacks = {
            "implementation": lambda manifest: manifest["generator_scope"].update(  # type: ignore[union-attr]
                {"implementation": "builtin_latent_context_v0.1"}
            ),
            "structural-id": lambda manifest: manifest[
                "generator_provenance"
            ].update(  # type: ignore[union-attr]
                {"structural_family_id": "builtin_latent_context_v0.1"}
            ),
            "declared-derivative": lambda manifest: manifest[
                "generator_provenance"
            ].update(  # type: ignore[union-attr]
                {"derived_from": ["builtin_latent_context_v0.1"]}
            ),
        }
        for name, mutate in attacks.items():
            with self.subTest(name=name):
                attacked = copy.deepcopy(self.manifest)
                mutate(attacked)
                _refresh_manifest(attacked)
                decision = evaluate_evidence_eligibility(
                    attacked, _attestation_for(attacked)
                )
                self.assertFalse(decision["eligible"])
                self.assertIn("builtin_or_derivative_ineligible", decision["reasons"])

    def test_missing_manifest_provenance_or_attestation_fails_closed(self) -> None:
        missing_manifest = evaluate_evidence_eligibility(None, self.attestation)
        self.assertFalse(missing_manifest["eligible"])
        self.assertIn("manifest_missing", missing_manifest["reasons"])

        missing_provenance = copy.deepcopy(self.manifest)
        del missing_provenance["generator_provenance"]
        missing_provenance["manifest_hash"] = manifest_hash(missing_provenance)
        decision = evaluate_evidence_eligibility(
            missing_provenance, _attestation_for(missing_provenance)
        )
        self.assertFalse(decision["eligible"])
        self.assertIn("generator_provenance_incomplete", decision["reasons"])

        missing_attestation = evaluate_evidence_eligibility(self.manifest, None)
        self.assertFalse(missing_attestation["eligible"])
        self.assertIn("attestation_missing", missing_attestation["reasons"])

    def test_individually_missing_provenance_fields_fail_closed(self) -> None:
        for field in (
            "author_or_origin",
            "benchmark_internal_access",
            "independence_rationale",
            "shared_evaluation_assumptions",
        ):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.manifest)
                provenance = candidate["generator_provenance"]
                assert isinstance(provenance, dict)
                del provenance[field]
                candidate["manifest_hash"] = manifest_hash(candidate)
                decision = evaluate_evidence_eligibility(
                    candidate, _attestation_for(candidate)
                )
                self.assertFalse(decision["eligible"])
                self.assertIn(
                    "generator_provenance_incomplete", decision["reasons"]
                )

    def test_present_but_blank_null_or_wrong_type_provenance_fails_closed(self) -> None:
        attacks = {
            "blank-author": ("author_or_origin", ""),
            "blank-generator-version": ("generator_version", ""),
            "blank-reviewer": ("independence_reviewer_id", ""),
            "null-rationale": ("independence_rationale", None),
            "bad-created-time": ("generator_created_at_utc", "not-a-timestamp"),
            "wrong-type-access": ("benchmark_internal_access", "undisclosed"),
            "wrong-type-dependencies": ("known_shared_dependencies", None),
        }
        for name, (field, value) in attacks.items():
            with self.subTest(name=name):
                candidate = copy.deepcopy(self.manifest)
                provenance = candidate["generator_provenance"]
                assert isinstance(provenance, dict)
                provenance[field] = value
                _refresh_manifest(candidate)
                decision = evaluate_evidence_eligibility(
                    candidate, _attestation_for(candidate)
                )
                self.assertFalse(
                    decision["eligible"],
                    f"present-but-invalid provenance was accepted: {field}",
                )

    def test_l2_disclosure_with_prior_outcome_access_fails_closed(self) -> None:
        candidate = copy.deepcopy(self.manifest)
        provenance = candidate["generator_provenance"]
        assert isinstance(provenance, dict)
        access = provenance["benchmark_internal_access"]
        assert isinstance(access, dict)
        access["prior_outcomes"] = True
        _refresh_manifest(candidate)
        decision = evaluate_evidence_eligibility(
            candidate, _attestation_for(candidate)
        )
        self.assertFalse(decision["eligible"])

    def test_incomplete_benchmark_internal_access_disclosure_fails_closed(self) -> None:
        candidate = copy.deepcopy(self.manifest)
        provenance = candidate["generator_provenance"]
        assert isinstance(provenance, dict)
        provenance["benchmark_internal_access"] = {"public_contract": True}
        _refresh_manifest(candidate)
        decision = evaluate_evidence_eligibility(
            candidate, _attestation_for(candidate)
        )
        self.assertFalse(decision["eligible"])

    def test_disclosed_builtin_lineage_or_target_mechanism_fails_closed(self) -> None:
        attacks = {
            "object-lineage": (
                "derived_from",
                {"implementation": "builtin_latent_context_v0.1"},
            ),
            "shared-environment-source": (
                "shared_source_code",
                ["src/magikarp/environment.py"],
            ),
            "shared-outcome-helper": (
                "shared_helper_functions",
                ["magikarp.environment.evaluate_revision"],
            ),
            "shared-recovery-construction": (
                "shared_evaluation_assumptions",
                ["copied built-in evaluate_revision recovery construction"],
            ),
        }
        for name, (field, value) in attacks.items():
            with self.subTest(name=name):
                candidate = copy.deepcopy(self.manifest)
                provenance = candidate["generator_provenance"]
                assert isinstance(provenance, dict)
                provenance[field] = value
                _refresh_manifest(candidate)
                decision = evaluate_evidence_eligibility(
                    candidate, _attestation_for(candidate)
                )
                self.assertFalse(
                    decision["eligible"],
                    f"declared built-in mechanism sharing was accepted: {field}",
                )

    def test_present_but_invalid_frozen_design_fields_fail_closed(self) -> None:
        attacks = {
            "null": ("primary_endpoints", None),
            "scalar": ("primary_endpoints", 42),
            "empty-exclusions": ("exclusion_rules", {}),
        }
        for name, (field, value) in attacks.items():
            with self.subTest(name=name):
                candidate = copy.deepcopy(self.manifest)
                design = candidate["design_freeze"]
                assert isinstance(design, dict)
                design[field] = value
                _refresh_manifest(candidate)
                decision = evaluate_evidence_eligibility(
                    candidate, _attestation_for(candidate)
                )
                self.assertFalse(decision["eligible"])

    def test_run_id_must_be_in_seed_registry_and_stopping_plan(self) -> None:
        candidate = copy.deepcopy(self.manifest)
        candidate["run_id"] = "unplanned-post-hoc-run"
        _refresh_manifest(candidate)
        decision = evaluate_evidence_eligibility(
            candidate, _attestation_for(candidate)
        )
        self.assertFalse(decision["eligible"])

    def test_incomplete_or_non_independent_attestation_fails_closed(self) -> None:
        incomplete = dict(self.attestation)
        del incomplete["record_locator"]
        incomplete = seal_attestation(incomplete)
        decision = evaluate_evidence_eligibility(self.manifest, incomplete)
        self.assertFalse(decision["eligible"])
        self.assertIn("attestation_schema_incomplete", decision["reasons"])

        for field, value, reason in (
            ("status", "self_attested", "attestation_not_independent_verified"),
            ("attestor_independence", "same-team", "attestor_not_independent"),
            ("evidence_ready", False, "attestation_not_evidence_ready"),
            ("independence_level", "L1", "attested_independence_level_mismatch"),
        ):
            with self.subTest(field=field):
                statement = dict(self.attestation)
                statement[field] = value
                statement = seal_attestation(statement)
                decision = evaluate_evidence_eligibility(self.manifest, statement)
                self.assertFalse(decision["eligible"])
                self.assertIn(reason, decision["reasons"])

    def test_attestor_cannot_be_the_declared_generator_author(self) -> None:
        provenance = self.manifest["generator_provenance"]
        assert isinstance(provenance, dict)
        statement = dict(self.attestation)
        statement["attestor_id"] = provenance["author_or_origin"]
        statement = seal_attestation(statement)
        decision = evaluate_evidence_eligibility(self.manifest, statement)
        self.assertFalse(decision["eligible"])

    def test_incompatible_benchmark_protocol_and_schema_versions_fail_closed(self) -> None:
        wrong_manifest_version = copy.deepcopy(self.manifest)
        wrong_manifest_version["manifest_version"] = MANIFEST_VERSION + 1
        _refresh_manifest(wrong_manifest_version)
        decision = evaluate_evidence_eligibility(
            wrong_manifest_version, _attestation_for(wrong_manifest_version)
        )
        self.assertFalse(decision["eligible"])

        for field, value, reason in (
            ("benchmark_version", "MAGIKARP-v9", "benchmark_version_mismatch"),
            (
                "evidence_protocol_version",
                "9.0",
                "evidence_protocol_version_mismatch",
            ),
        ):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.manifest)
                candidate[field] = value
                _refresh_manifest(candidate)
                decision = evaluate_evidence_eligibility(
                    candidate, _attestation_for(candidate)
                )
                self.assertFalse(decision["eligible"])
                self.assertIn(reason, decision["reasons"])

        wrong_schema = dict(self.attestation)
        wrong_schema["schema_version"] = 2
        wrong_schema = seal_attestation(wrong_schema)
        decision = evaluate_evidence_eligibility(self.manifest, wrong_schema)
        self.assertFalse(decision["eligible"])
        self.assertIn("attestation_schema_version_mismatch", decision["reasons"])

        bool_schema = dict(self.attestation)
        bool_schema["schema_version"] = True
        bool_schema = seal_attestation(bool_schema)
        decision = evaluate_evidence_eligibility(self.manifest, bool_schema)
        self.assertFalse(decision["eligible"])
        self.assertIn("attestation_schema_version_mismatch", decision["reasons"])

    def test_changed_scientific_hashes_invalidate_prior_attestation(self) -> None:
        for field in SCIENTIFIC_HASH_FIELDS:
            with self.subTest(field=field):
                changed = copy.deepcopy(self.manifest)
                changed[field] = _digest(f"changed-{field}")
                scientific = changed["scientific_hashes"]
                assert isinstance(scientific, dict)
                scientific[field] = changed[field]
                changed["manifest_hash"] = manifest_hash(changed)
                decision = evaluate_evidence_eligibility(changed, self.attestation)
                self.assertFalse(decision["eligible"])
                self.assertIn("attestation_manifest_hash_mismatch", decision["reasons"])

    def test_internal_scientific_hash_divergence_fails_even_when_reattested(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["controller_source_hash"] = _digest("different-controller-source")
        # Deliberately leave scientific_hashes bound to the old source, then
        # re-seal both outer records.  Fresh self-hashes cannot conceal an
        # internally inconsistent scientific binding.
        changed["manifest_hash"] = manifest_hash(changed)
        decision = evaluate_evidence_eligibility(
            changed, _attestation_for(changed)
        )
        self.assertFalse(decision["eligible"])
        self.assertIn("controller_source_hash_mismatch", decision["reasons"])

    def test_changed_frozen_design_invalidates_prior_attestation(self) -> None:
        changed = copy.deepcopy(self.manifest)
        design = changed["design_freeze"]
        assert isinstance(design, dict)
        design["primary_endpoints"] = ["post-hoc replacement"]
        _refresh_manifest(changed)
        decision = evaluate_evidence_eligibility(changed, self.attestation)
        self.assertFalse(decision["eligible"])
        self.assertIn("attestation_manifest_hash_mismatch", decision["reasons"])

    def test_attestation_serialization_is_deterministic_and_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "a" / "attestation.json"
            second = root / "b" / "attestation.json"
            write_attestation(self.attestation, first)
            reversed_order = dict(reversed(tuple(self.attestation.items())))
            write_attestation(reversed_order, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(load_attestation(first), self.attestation)
            self.assertTrue(first.read_bytes().endswith(b"\n"))

        stale_hash = dict(self.attestation)
        stale_hash["attestation_hash"] = "0" * 64
        self.assertEqual(seal_attestation(stale_hash), self.attestation)

    def test_tampered_attestation_self_hash_is_not_authoritative(self) -> None:
        tampered = dict(self.attestation)
        tampered["attestor_id"] = "post-hoc-substitution"
        decision = evaluate_evidence_eligibility(self.manifest, tampered)
        self.assertFalse(decision["eligible"])
        self.assertIn("attestation_hash_mismatch", decision["reasons"])


class OutcomeAuthorityBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = evidence_config()
        # This is a pure classifier fixture; validate_config deliberately keeps
        # the executable built-in configuration ineligible.
        self.config["generator_scope"]["evidence_ready"] = True
        self.eligible = {"eligible": True}
        self.positive_analysis = {
            "delta_mae": 0.020,
            "confidence_interval": [0.010, 0.030],
            "per_failure": {
                "parameter": {"delta_mae": 0.030},
                "model": {"delta_mae": 0.020},
                "interface": {"delta_mae": 0.010},
            },
        }
        self.null_analysis = {
            "delta_mae": 0.004,
            "confidence_interval": [-0.010, 0.018],
            "per_failure": {
                "parameter": {"delta_mae": 0.020},
                "model": {"delta_mae": -0.010},
                "interface": {"delta_mae": 0.000},
            },
        }

    def test_failed_gate_cannot_become_empirical_positive(self) -> None:
        validity = {"all_passed": False}
        status = _status(
            self.config, validity, self.positive_analysis, self.eligible
        )
        self.assertEqual(status, "benchmark_invalid")
        self.assertFalse(
            _is_evidence_bearing(self.config, validity, status, self.eligible)
        )

    def test_valid_null_is_retained_as_evidence(self) -> None:
        validity = {"all_passed": True}
        status = _status(self.config, validity, self.null_analysis, self.eligible)
        self.assertEqual(status, "valid_negative")
        self.assertTrue(
            _is_evidence_bearing(self.config, validity, status, self.eligible)
        )

    def test_invalid_eligibility_is_distinct_from_valid_null(self) -> None:
        validity = {"all_passed": True}
        ineligible = {"eligible": False}
        status = _status(self.config, validity, self.null_analysis, ineligible)
        self.assertEqual(status, "benchmark_invalid")
        self.assertNotEqual(status, "valid_negative")
        self.assertFalse(
            _is_evidence_bearing(self.config, validity, status, ineligible)
        )

    def test_per_failure_heterogeneity_is_not_a_third_evidence_status(self) -> None:
        status = _status(
            self.config,
            {"all_passed": True},
            self.null_analysis,
            self.eligible,
        )
        self.assertEqual(status, "valid_negative")
        self.assertNotEqual(status, "valid_mixed")


class InstalledPackageBoundaryTests(unittest.TestCase):
    def test_wheel_smoke_remains_builtin_and_non_evidence_bearing(self) -> None:
        """Exercise the installed wheel outside the source checkout."""

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            built = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    "--no-deps",
                    "--no-build-isolation",
                    "--wheel-dir",
                    str(wheelhouse),
                    str(REPO_ROOT),
                ],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(
                built.returncode,
                0,
                f"wheel build failed:\nstdout={built.stdout}\nstderr={built.stderr}",
            )
            wheels = list(wheelhouse.glob("*.whl"))
            self.assertEqual(len(wheels), 1)

            installed = root / "installed"
            installed.mkdir()
            with zipfile.ZipFile(wheels[0]) as archive:
                archive.extractall(installed)

            config = smoke_config()
            config["sample_counts"].update(
                {
                    "agents_per_family": 2,
                    "baseline_cases": 1,
                    "standard_adaptation_cases": 1,
                    "diagnostic_cases_per_failure": 2,
                    "adaptation_cases_per_failure": 2,
                    "transfer_cases_per_failure": 2,
                }
            )
            config["bootstrap"]["replicates"] = 8
            config_path = root / "smoke.json"
            config_path.write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            output = root / "wheel-smoke"
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(installed)
            import_probe = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import pathlib, magikarp; "
                    "print(pathlib.Path(magikarp.__file__).resolve())",
                ],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(import_probe.returncode, 0, import_probe.stderr)
            imported_from = Path(import_probe.stdout.strip())
            self.assertTrue(imported_from.is_relative_to(installed.resolve()))

            executed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "magikarp",
                    "--repo-root",
                    str(root),
                    "smoke",
                    "--config",
                    str(config_path),
                    "--output",
                    str(output),
                ],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(
                executed.returncode,
                0,
                "installed-wheel smoke failed outside the checkout:\n"
                f"stdout={executed.stdout}\nstderr={executed.stderr}",
            )

            cli_summary = json.loads(executed.stdout)
            persisted = json.loads(
                (output / "summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(cli_summary["status"], "engineering_only")
            self.assertEqual(persisted["status"], "engineering_only")
            self.assertFalse(persisted["evidence_ready"])
            self.assertFalse(persisted["evidence_bearing"])

            trial_rows = [
                json.loads(line)
                for line in (output / "trial_records.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            self.assertTrue(trial_rows)
            self.assertEqual(
                {row["structural_family_id"] for row in trial_rows},
                {"builtin_latent_context_v0.1"},
            )


if __name__ == "__main__":
    unittest.main()
