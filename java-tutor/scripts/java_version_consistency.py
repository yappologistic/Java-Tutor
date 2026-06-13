#!/usr/bin/env python3
"""Check Java version hints for conflicting source, target, toolchain, and runtime baselines."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import java_project_info


DEFAULT_VERSION = "25"
OFFICIAL_DOC_TEMPLATES = (
    "https://docs.oracle.com/en/java/javase/{version}/docs/specs/man/javac.html",
    "https://docs.oracle.com/en/java/javase/{version}/migrate/index.html",
    "https://docs.oracle.com/en/java/javase/",
)

COMPILE_HINT_TOKENS = (
    "compiler",
    "source",
    "target",
    "release",
    "gradle-java-version",
    "java.version",
)
RUNTIME_HINT_TOKENS = (
    "docker",
    "java-version-file",
    "sdkman",
    "java.home",
)


def parse_major(value: str) -> int | None:
    normalized = java_project_info.normalize_version(value)
    if re.fullmatch(r"\d+", normalized):
        return int(normalized)
    return None


def numeric_hints(info: dict[str, Any]) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    for hint in info["hints"]:
        major = parse_major(hint["value"])
        if major is None:
            continue
        hints.append({**hint, "major": major})
    return hints


def has_token(kind: str, tokens: Iterable[str]) -> bool:
    lowered = kind.lower()
    return any(token in lowered for token in tokens)


def classify_hints(hints: list[dict[str, Any]], tokens: Iterable[str]) -> list[dict[str, Any]]:
    return [hint for hint in hints if has_token(hint["kind"], tokens)]


def official_docs(version: str = DEFAULT_VERSION) -> tuple[str, ...]:
    return tuple(doc.format(version=version) for doc in OFFICIAL_DOC_TEMPLATES)


def build_issue(
    code: str,
    severity: str,
    summary: str,
    action: str,
    docs: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "summary": summary,
        "action": action,
        "official_docs": list(docs),
    }


def analyze(root: Path) -> dict[str, Any]:
    info = java_project_info.infer_project_info(root)
    hints = numeric_hints(info)
    versions = sorted({hint["major"] for hint in hints})
    compile_hints = classify_hints(hints, COMPILE_HINT_TOKENS)
    runtime_hints = classify_hints(hints, RUNTIME_HINT_TOKENS)
    doc_version = info.get("language_version") or info.get("recommended_version") or DEFAULT_VERSION
    docs = official_docs(str(doc_version))
    issues: list[dict[str, Any]] = []

    if not hints:
        issues.append(
            build_issue(
                "no-version-hints",
                "info",
                "No numeric Java version hints were found in common project files.",
                "Inspect build files, CI, containers, and local toolchains before making version-specific recommendations.",
                docs,
            )
        )
    elif len(versions) > 1:
        issues.append(
            build_issue(
                "mixed-version-hints",
                "warning",
                f"Multiple Java versions were detected: {', '.join(str(version) for version in versions)}.",
                "Confirm which value controls source compatibility, bytecode target, test runtime, production runtime, and local toolchain.",
                docs,
            )
        )

    compile_versions = sorted({hint["major"] for hint in compile_hints})
    runtime_versions = sorted({hint["major"] for hint in runtime_hints})
    if compile_versions and runtime_versions and max(runtime_versions) > min(compile_versions):
        issues.append(
            build_issue(
                "runtime-newer-than-compile-baseline",
                "info",
                f"Runtime/toolchain hints go up to Java {max(runtime_versions)}, while compile hints include Java {min(compile_versions)}.",
                "Do not recommend APIs newer than the compile release/source level unless the build baseline is intentionally raised.",
                docs,
            )
        )

    recommended = int(doc_version) if str(doc_version).isdigit() else None
    if recommended is not None and recommended <= 8:
        issues.append(
            build_issue(
                "legacy-baseline",
                "info",
                f"The highest detected Java baseline is {recommended}.",
                "Avoid Java 9+ APIs and language features unless the project is being migrated.",
                docs,
            )
        )

    return {
        "root": info["root"],
        "detected_versions": [str(version) for version in versions],
        "language_version": info.get("language_version"),
        "runtime_version": info.get("runtime_version"),
        "highest_detected_version": info.get("highest_detected_version"),
        "recommended_version": str(doc_version) if doc_version else None,
        "compile_hint_versions": [str(version) for version in compile_versions],
        "runtime_hint_versions": [str(version) for version in runtime_versions],
        "hints": info["hints"],
        "issues": issues,
        "official_docs": list(docs),
    }


def render_text(result: dict[str, Any]) -> str:
    lines = [
        "Java version consistency",
        f"Root: {result['root']}",
        f"Detected versions: {', '.join(result['detected_versions']) if result['detected_versions'] else 'none'}",
        f"Recommended version: {result['recommended_version'] or 'unknown'}",
    ]
    if result["hints"]:
        lines.append("")
        lines.append("Hints:")
        for hint in result["hints"]:
            lines.append(f"- {hint['kind']}: Java {hint['value']} ({hint['source']})")
    lines.append("")
    lines.append("Issues:")
    if result["issues"]:
        for issue in result["issues"]:
            lines.append(f"- [{issue['severity']}] {issue['code']}: {issue['summary']} {issue['action']}")
    else:
        lines.append("- No version consistency issues detected from common project files.")
    lines.append("")
    lines.append("Official docs:")
    for url in result["official_docs"]:
        lines.append(f"- {url}")
    return "\n".join(lines)


def official_urls() -> tuple[str, ...]:
    return official_docs(DEFAULT_VERSION)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Project root to inspect")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    result = analyze(Path(args.path))
    print(json.dumps(result, indent=2) if args.json else render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
