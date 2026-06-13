#!/usr/bin/env python3
"""Generate official-doc-backed Java learning paths by level and goal."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class LearningStep:
    title: str
    outcome: str
    practice: str
    tags: tuple[str, ...]
    docs: tuple[str, ...]


@dataclass(frozen=True)
class LearningPath:
    level: str
    steps: tuple[LearningStep, ...]


LEVEL_ALIASES = {
    "beginner": "beginner",
    "new": "beginner",
    "junior": "beginner",
    "intermediate": "intermediate",
    "mid": "intermediate",
    "professional": "professional",
    "senior": "professional",
    "advanced": "professional",
}


def api_link(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/{path}"


def jls_link(section: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/{section}"


def paths(version: str = DEFAULT_VERSION) -> tuple[LearningPath, ...]:
    return (
        LearningPath(
            level="beginner",
            steps=(
                LearningStep(
                    title="Set up, compile, and run Java",
                    outcome="Understand the write, compile, run cycle and the roles of `javac` and `java`.",
                    practice="Create one `HelloWorld.java`, compile it, run it, then intentionally break it and read the compiler diagnostic.",
                    tags=("fundamentals", "tooling"),
                    docs=(
                        "https://dev.java/learn/getting-started/",
                        api_link("java.base/java/lang/String.html", version),
                        f"https://docs.oracle.com/en/java/javase/{version}/docs/specs/man/javac.html",
                    ),
                ),
                LearningStep(
                    title="Learn variables, control flow, methods, and arrays",
                    outcome="Read and write small single-file programs using core language constructs.",
                    practice="Write a small CLI program that validates input, loops over an array, and extracts repeated logic into methods.",
                    tags=("fundamentals", "syntax"),
                    docs=("https://dev.java/learn/language-basics/", jls_link("jls-14.html", version)),
                ),
                LearningStep(
                    title="Model behavior with classes and objects",
                    outcome="Understand fields, constructors, methods, access control, packages, and object identity.",
                    practice="Create a small domain class with validation, a useful `toString`, and package-private helper methods.",
                    tags=("oop", "api-design"),
                    docs=(
                        "https://dev.java/learn/classes-objects/",
                        jls_link("jls-8.html", version),
                        api_link("java.base/java/lang/Object.html", version),
                    ),
                ),
                LearningStep(
                    title="Handle errors intentionally",
                    outcome="Distinguish compile errors, checked exceptions, unchecked exceptions, and domain validation.",
                    practice="Read a file or parse input, then return a clear error message for invalid input.",
                    tags=("exceptions", "debugging"),
                    docs=(
                        "https://docs.oracle.com/javase/tutorial/essential/exceptions/",
                        jls_link("jls-11.html", version),
                    ),
                ),
            ),
        ),
        LearningPath(
            level="intermediate",
            steps=(
                LearningStep(
                    title="Choose collections deliberately",
                    outcome="Select List, Set, Map, Queue, and Deque implementations by behavior and complexity needs.",
                    practice="Refactor an array-based program to use collections and document why each collection was chosen.",
                    tags=("collections", "api-design"),
                    docs=(
                        "https://dev.java/learn/api/collections-framework/",
                        api_link("java.base/java/util/Collection.html", version),
                        api_link("java.base/java/util/Map.html", version),
                    ),
                ),
                LearningStep(
                    title="Use generics and Optional without hiding design problems",
                    outcome="Understand parameterized types, wildcards, type inference, and absence as an API concept.",
                    practice="Convert a raw-type API to generic types and replace one nullable return with an explicit absence model.",
                    tags=("generics", "api-design", "optional"),
                    docs=(
                        jls_link("jls-4.html", version),
                        jls_link("jls-18.html", version),
                        api_link("java.base/java/util/Optional.html", version),
                    ),
                ),
                LearningStep(
                    title="Process data with streams where they improve clarity",
                    outcome="Use map, filter, reduce, collectors, and primitive streams while recognizing stream misuse.",
                    practice="Implement the same aggregation with a loop and a stream; compare readability, allocation, and debugging.",
                    tags=("streams", "performance"),
                    docs=(
                        "https://dev.java/learn/api/streams/",
                        api_link("java.base/java/util/stream/package-summary.html", version),
                    ),
                ),
                LearningStep(
                    title="Understand modules, class paths, and build boundaries",
                    outcome="Diagnose missing symbols, package visibility, dependency scope, and modular access problems.",
                    practice="Create a tiny two-module or two-package example and intentionally misconfigure imports or dependencies.",
                    tags=("modules", "tooling", "debugging"),
                    docs=(
                        jls_link("jls-7.html", version),
                        api_link("java.base/module-summary.html", version),
                        f"https://docs.oracle.com/en/java/javase/{version}/docs/specs/man/javac.html",
                    ),
                ),
            ),
        ),
        LearningPath(
            level="professional",
            steps=(
                LearningStep(
                    title="Reason from the JLS and API contracts",
                    outcome="Resolve language and overload questions from specification rules instead of folklore.",
                    practice="Explain one confusing overload, initialization, or generic inference case using the exact JLS section.",
                    tags=("language", "spec", "api-design"),
                    docs=(
                        jls_link("index.html", version),
                        jls_link("jls-12.html", version),
                        jls_link("jls-15.html", version),
                    ),
                ),
                LearningStep(
                    title="Design and review concurrent code conservatively",
                    outcome="Apply happens-before, interruption, executor lifecycle, confinement, and safe publication rules.",
                    practice="Review a shared mutable component and write down its ownership, synchronization, and shutdown model.",
                    tags=("concurrency", "review", "performance"),
                    docs=(
                        jls_link("jls-17.html", version),
                        api_link("java.base/java/util/concurrent/package-summary.html", version),
                    ),
                ),
                LearningStep(
                    title="Modernize with compatibility discipline",
                    outcome="Use newer Java features while respecting source, target, runtime, library, and deployment constraints.",
                    practice="Plan a Java 11-to-LTS migration with build, CI, dependency, reflection, and runtime checks.",
                    tags=("modernization", "migration", "compatibility"),
                    docs=(
                        f"https://docs.oracle.com/en/java/javase/{version}/migrate/index.html",
                        "https://openjdk.org/jeps/0",
                        "https://www.oracle.com/java/technologies/javase/jdk-relnotes-index.html",
                    ),
                ),
                LearningStep(
                    title="Review security and operational failure modes",
                    outcome="Identify trust boundaries, resource exhaustion, disclosure risks, and security-provider assumptions.",
                    practice="Annotate a service entry point with trust boundaries, input validation, resource limits, and sensitive outputs.",
                    tags=("security", "review", "operations"),
                    docs=(
                        "https://www.oracle.com/java/technologies/javase/seccodeguide.html",
                        f"https://docs.oracle.com/en/java/javase/{version}/security/index.html",
                    ),
                ),
            ),
        ),
    )


def normalize_level(level: str) -> str:
    normalized = LEVEL_ALIASES.get(level.lower().strip())
    if not normalized:
        valid = ", ".join(sorted(LEVEL_ALIASES))
        raise ValueError(f"unknown level {level!r}; valid levels: {valid}")
    return normalized


def build_path(level: str, goal: str | None = None, version: str = DEFAULT_VERSION) -> LearningPath:
    normalized = normalize_level(level)
    by_level = {path.level: path for path in paths(version)}
    selected = by_level[normalized]
    if not goal:
        return selected

    goal_tokens = {token.strip().lower() for token in goal.replace(",", " ").split() if token.strip()}
    steps = tuple(step for step in selected.steps if goal_tokens.intersection(step.tags))
    if not steps:
        available = ", ".join(sorted({tag for step in selected.steps for tag in step.tags}))
        raise ValueError(f"goal {goal!r} did not match {normalized} topics; available tags: {available}")
    return LearningPath(level=selected.level, steps=steps)


def official_urls(path: LearningPath) -> tuple[str, ...]:
    urls: list[str] = []
    for step in path.steps:
        urls.extend(step.docs)
    return tuple(dict.fromkeys(urls))


def render_text(path: LearningPath) -> str:
    lines = [f"Java learning path: {path.level}"]
    for index, step in enumerate(path.steps, start=1):
        lines.extend(
            [
                "",
                f"{index}. {step.title}",
                f"   Outcome: {step.outcome}",
                f"   Practice: {step.practice}",
                f"   Tags: {', '.join(step.tags)}",
                f"   Docs: {', '.join(step.docs)}",
            ]
        )
    lines.extend(["", "Official docs:"])
    for url in official_urls(path):
        lines.append(f"- {url}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("level", nargs="?", default="beginner", help="beginner, intermediate, professional, or alias")
    parser.add_argument("--goal", help="Optional topic tag such as concurrency, streams, security, migration, debugging")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    try:
        path = build_path(args.level, args.goal, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(path)
        payload["official_docs"] = list(official_urls(path))
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
