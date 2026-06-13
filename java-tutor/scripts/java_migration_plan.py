#!/usr/bin/env python3
"""Generate an official-doc-backed Java migration checklist."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass


SUPPORTED_TARGETS = {"11", "17", "21", "25", "26"}


@dataclass(frozen=True)
class MigrationPlan:
    source: str
    target: str
    official_docs: tuple[str, ...]
    checks: tuple[str, ...]


BASE_CHECKS = (
    "Record the current runtime vendor/version with `java --version` and the build compiler target.",
    "Run the full test suite on the current JDK before changing source/target compatibility.",
    "Upgrade build plugins, test libraries, bytecode tools, annotation processors, and CI images before changing application code.",
    "Compile with the target JDK and treat new warnings/errors as migration findings.",
    "Review removed, deprecated, and behavior-changing APIs in the target JDK release notes.",
)


def normalize_version(value: str) -> str:
    value = value.strip()
    if value.startswith("1."):
        return value.split(".", 1)[1]
    return value


def official_docs(target: str) -> tuple[str, ...]:
    return (
        f"https://docs.oracle.com/en/java/javase/{target}/migrate/index.html",
        f"https://www.oracle.com/java/technologies/javase/{target}all-relnotes.html",
        f"https://docs.oracle.com/en/java/javase/{target}/docs/api/",
    )


def migration_checks(source: str, target: str) -> tuple[str, ...]:
    source_i = int(source)
    target_i = int(target)
    checks: list[str] = list(BASE_CHECKS)

    if source_i <= 8 < target_i:
        checks.extend(
            [
                "Audit dependencies on Java EE and CORBA modules removed after JDK 8; add explicit external dependencies where needed.",
                "Check illegal reflective access and strong encapsulation issues introduced by the module system.",
                "Replace uses of removed tools such as `javah`; use `javac -h` for JNI headers.",
            ]
        )
    if source_i <= 11 < target_i:
        checks.extend(
            [
                "Check for dependencies that still assume Java 8/11 bytecode or old class-file parsing libraries.",
                "Review TLS, certificate, and security-provider changes in each target release note.",
            ]
        )
    if source_i <= 17 < target_i:
        checks.extend(
            [
                "Verify framework and container support for Java 21+ before adopting virtual threads or newer language features.",
                "Prefer `--release` or toolchains over only setting source/target compatibility.",
            ]
        )
    if target_i >= 21:
        checks.extend(
            [
                "Evaluate virtual threads only for blocking I/O workloads; keep CPU-bound work on bounded executors or structured parallelism.",
                "Review pattern matching, records, sealed classes, and switch changes against the project's configured language level.",
            ]
        )
    if target_i >= 25:
        checks.extend(
            [
                f"Use the JDK {target} migration guide and release notes for target-specific migration checks.",
                "Mark preview/incubator APIs clearly and avoid relying on them in production without explicit approval.",
            ]
        )
    if target_i == 26:
        checks.append("Treat JDK 26 as a feature release, not the current LTS; confirm support policy before production rollout.")

    checks.append("After migration, run tests on the target JDK in CI and keep the previous production JDK available for rollback.")
    return tuple(dict.fromkeys(checks))


def build_plan(source: str, target: str) -> MigrationPlan:
    source = normalize_version(source)
    target = normalize_version(target)
    if not source.isdigit() or not target.isdigit():
        raise ValueError("source and target must be Java major versions, for example 8, 17, 21, or 25")
    if int(source) >= int(target):
        raise ValueError("target version must be greater than source version")
    if target not in SUPPORTED_TARGETS:
        raise ValueError(f"target {target} is not in supported target set: {', '.join(sorted(SUPPORTED_TARGETS, key=int))}")
    return MigrationPlan(source=source, target=target, official_docs=official_docs(target), checks=migration_checks(source, target))


def render_text(plan: MigrationPlan) -> str:
    checks = "\n".join(f"{index}. {check}" for index, check in enumerate(plan.checks, start=1))
    docs = "\n".join(f"- {link}" for link in plan.official_docs)
    return (
        f"Java {plan.source} to Java {plan.target} migration checklist\n\n"
        f"{checks}\n\n"
        f"Official docs:\n{docs}"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Current Java major version")
    parser.add_argument("target", help="Target Java major version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    try:
        plan = build_plan(args.source, args.target)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(asdict(plan), indent=2) if args.json else render_text(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
