#!/usr/bin/env python3
"""Plan a Java deprecated, for-removal, and removed API audit."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass


DEFAULT_TARGET = "25"
SUPPORTED_TARGETS = {"11", "17", "21", "25", "26"}


@dataclass(frozen=True)
class AuditPlan:
    target: str
    artifact: str
    commands: tuple[str, ...]
    checks: tuple[str, ...]
    limitations: tuple[str, ...]
    official_docs: tuple[str, ...]


def normalize_version(value: str) -> str:
    value = value.strip()
    if value.startswith("1."):
        return value.split(".", 1)[1]
    return value


def docs(target: str) -> tuple[str, ...]:
    docs_version = target if target in SUPPORTED_TARGETS else DEFAULT_TARGET
    return (
        f"https://docs.oracle.com/en/java/javase/{docs_version}/docs/specs/man/jdeprscan.html",
        f"https://docs.oracle.com/en/java/javase/{docs_version}/docs/specs/man/jdeps.html",
        f"https://docs.oracle.com/en/java/javase/{docs_version}/migrate/removed-apis.html",
        f"https://docs.oracle.com/en/java/javase/{docs_version}/migrate/removed-tools-and-components.html",
        f"https://docs.oracle.com/en/java/javase/{docs_version}/docs/api/deprecated-list.html",
        f"https://www.oracle.com/java/technologies/javase/{docs_version}all-relnotes.html",
    )


def build_plan(target: str = DEFAULT_TARGET, artifact: str = "<path-to-jar-or-classes>") -> AuditPlan:
    target = normalize_version(target)
    if not target.isdigit():
        raise ValueError("target must be a Java major version, for example 17, 21, or 25")
    if target not in SUPPORTED_TARGETS:
        raise ValueError(f"target {target} is not in supported target set: {', '.join(sorted(SUPPORTED_TARGETS, key=int))}")

    commands = (
        f"jdeprscan --release {target} {artifact}",
        f"jdeprscan --release {target} --for-removal {artifact}",
        f"jdeprscan --release {target} -l --for-removal",
        f"jdeps --jdk-internals --multi-release {target} {artifact}",
    )
    checks = (
        "Build the project first so the scan points at compiled classes or packaged JARs.",
        "Run jdeprscan against the same compiled output that will be migrated, including application modules and important internal libraries.",
        "Treat for-removal findings as migration blockers unless the code path is dead and can be removed.",
        "Run jdeps for JDK internal API usage; replace internal APIs with supported Java SE or documented JDK APIs before upgrading.",
        "Read the target migration guide removed APIs page and release notes for behavior changes that static tools may not find.",
        "Scan third-party dependencies separately with their own release notes and compatibility matrices; jdeprscan reports Java SE deprecated APIs, not library-specific deprecations.",
    )
    limitations = (
        "jdeprscan analyzes class files and JARs; it does not analyze source-only code that has not been compiled.",
        "jdeprscan reports deprecated Java SE APIs and does not report third-party library deprecations.",
        "Static tools can miss reflective, service-loaded, generated, or configuration-driven API usage.",
        "jdeps flags dependencies such as JDK internal APIs, but replacement choices still require reading API docs and release notes.",
    )
    return AuditPlan(target=target, artifact=artifact, commands=commands, checks=checks, limitations=limitations, official_docs=docs(target))


def official_urls(target: str = DEFAULT_TARGET) -> tuple[str, ...]:
    return docs(normalize_version(target))


def render_text(plan: AuditPlan) -> str:
    lines = [f"Java {plan.target} deprecation and removal audit", f"Artifact: {plan.artifact}", "", "Commands:"]
    lines.extend(f"- `{command}`" for command in plan.commands)
    lines.extend(["", "Checks:"])
    lines.extend(f"{index}. {check}" for index, check in enumerate(plan.checks, start=1))
    lines.extend(["", "Limitations:"])
    lines.extend(f"- {limitation}" for limitation in plan.limitations)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in plan.official_docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=DEFAULT_TARGET, help="Target Java major version")
    parser.add_argument("--artifact", default="<path-to-jar-or-classes>", help="JAR, class file, or classes directory to scan")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    try:
        plan = build_plan(args.target, args.artifact)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(asdict(plan), indent=2) if args.json else render_text(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
