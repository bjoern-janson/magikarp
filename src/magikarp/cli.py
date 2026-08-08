"""Command-line interface for reproducible MAGIKARP runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .config import evidence_config, load_config, smoke_config, validate_config
from .eligibility import load_attestation
from .manifest import build_manifest, load_manifest, write_manifest
from .runner import run_benchmark


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="magikarp",
        description=(
            "Run the controlled MAGIKARP v0.1 synthetic benchmark infrastructure. "
            "The built-in generator is engineering-only."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="repository root used for Git provenance (default: current directory)",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    smoke = subcommands.add_parser(
        "smoke", help="run the full loop with engineering-only settings"
    )
    smoke.add_argument("--config", type=Path, help="optional smoke JSON config")
    smoke.add_argument("--output", type=Path, default=Path("results/smoke"))
    smoke.add_argument("--overwrite", action="store_true")

    template = subcommands.add_parser("template", help="write a config template")
    template.add_argument("--mode", choices=("smoke", "evidence"), required=True)
    template.add_argument("--output", type=Path, required=True)
    template.add_argument("--overwrite", action="store_true")

    freeze = subcommands.add_parser(
        "freeze",
        help=(
            "freeze a pre-outcome infrastructure manifest from a clean, "
            "source-bound commit"
        ),
        description=(
            "Freeze a source-bound infrastructure manifest. Record its emitted "
            "hash independently before inspecting outcomes."
        ),
    )
    freeze.add_argument("--config", type=Path, required=True)
    freeze.add_argument("--manifest", type=Path, required=True)
    freeze.add_argument("--overwrite", action="store_true")

    run = subcommands.add_parser(
        "run",
        help=(
            "exercise a frozen manifest; the built-in single-generator scope "
            "remains engineering-only"
        ),
        description=(
            "Exercise a frozen manifest. The built-in family labels are buckets "
            "over one synthetic generator, so this remains engineering-only."
        ),
    )
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument(
        "--attestation",
        type=Path,
        help=(
            "separate pre-outcome independent-attestation JSON; omission remains "
            "ineligible and can never authorize evidence"
        ),
    )
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--overwrite", action="store_true")
    return parser


def _write_template(mode: str, path: Path, *, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing config: {path}")
    config = smoke_config() if mode == "smoke" else evidence_config()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _print_result(summary: dict[str, object], output: Path) -> None:
    analysis = summary["analysis"]
    assert isinstance(analysis, dict)
    interval = analysis.get("confidence_interval", analysis.get("ci95"))
    payload = {
        "status": summary["status"],
        "output": str(output.resolve()),
        "evidence_bearing": summary.get("evidence_bearing", False),
        "evidence_ready": summary.get("evidence_ready", False),
        "attestation_status": summary.get("attestation_status", "missing"),
        "independence_level": summary.get("independence_level"),
        "generator_scope": summary.get("generator_scope", {}),
        "validity_passed": summary["validity"]["all_passed"],  # type: ignore[index]
        "analysis_evaluated": analysis.get("evaluated", True),
        "delta_mae": analysis.get("delta_mae"),
        "confidence_interval": interval,
        "confidence_level": analysis.get("confidence_level"),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        repo_root = args.repo_root.resolve()
        if args.command == "template":
            _write_template(args.mode, args.output, overwrite=args.overwrite)
            print(args.output.resolve())
            return 0

        if args.command == "smoke":
            config = load_config(args.config) if args.config else smoke_config()
            if config["mode"] != "smoke":
                raise ValueError("smoke command requires a smoke-mode config")
            summary = run_benchmark(
                config,
                repo_root=repo_root,
                output_dir=args.output,
                overwrite=args.overwrite,
            )
            _print_result(summary, args.output)
            return 0

        if args.command == "freeze":
            config = load_config(args.config)
            if config["mode"] != "evidence":
                raise ValueError("freeze command requires an evidence-mode config")
            if args.manifest.exists() and not args.overwrite:
                raise FileExistsError(
                    f"refusing to overwrite existing manifest: {args.manifest}"
                )
            manifest = build_manifest(config, repo_root)
            if manifest["frozen"] is not True:
                raise RuntimeError(
                    "evidence manifest cannot be frozen: commit the implementation "
                    "and start from a clean worktree"
                )
            write_manifest(manifest, args.manifest)
            print(
                json.dumps(
                    {
                        "manifest": str(args.manifest.resolve()),
                        "manifest_hash": manifest["manifest_hash"],
                        "generator_scope": manifest["generator_scope"],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        if args.command == "run":
            manifest = load_manifest(args.manifest)
            attestation = (
                load_attestation(args.attestation) if args.attestation else None
            )
            config = manifest.get("config")
            if not isinstance(config, dict):
                raise ValueError("manifest does not embed a benchmark config")
            validate_config(config)
            if config["mode"] != "evidence":
                raise ValueError("run command requires an evidence-mode manifest")
            summary = run_benchmark(
                config,
                repo_root=repo_root,
                output_dir=args.output,
                manifest=manifest,
                attestation=attestation,
                overwrite=args.overwrite,
            )
            _print_result(summary, args.output)
            return 0
        parser.error(f"unsupported command: {args.command}")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"magikarp: error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
