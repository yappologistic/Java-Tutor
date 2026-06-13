#!/usr/bin/env python3
"""Check whether a curated Java feature is available for a target Java version."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict
from typing import Any

import java_topic_links


def parse_major(version: str) -> int:
    value = version.strip().lower().replace("_", ".")
    if value.startswith("1."):
        value = value[2:]
    distribution_match = re.search(r"(?:java|jdk|jre|openjdk|temurin|zulu|corretto|graalvm)[^\d]*(\d{1,2})", value)
    if distribution_match:
        return int(distribution_match.group(1))
    digits = ""
    for char in value:
        if char.isdigit():
            digits += char
        else:
            break
    if not digits:
        raise ValueError(f"could not parse Java version {version!r}")
    return int(digits)


def compatibility(topic_query: str, target_version: str) -> dict[str, Any]:
    topic = java_topic_links.find_topic(topic_query)
    target = parse_major(target_version)
    minimum = parse_major(topic.minimum_version)
    available = target >= minimum
    docs_version = str(target if available else minimum)
    return {
        "topic": asdict(topic),
        "target_version": str(target),
        "minimum_version": str(minimum),
        "documentation_version": docs_version,
        "available": available,
        "recommendation": recommendation(topic, target, minimum, available),
        "official_docs": list(java_topic_links.links_for(topic, docs_version)),
    }


def recommendation(topic: java_topic_links.Topic, target: int, minimum: int, available: bool) -> str:
    if available:
        return (
            f"{topic.title} is available for Java {target}. "
            f"Still verify the project source/release setting and runtime JDK before using it."
        )
    return (
        f"{topic.title} requires Java {minimum} or newer, but the target is Java {target}. "
        f"Use an older-compatible alternative or plan a version upgrade first; linked API docs use Java {minimum}."
    )


def render_text(result: dict[str, Any]) -> str:
    topic = result["topic"]
    links = "\n".join(f"- {link}" for link in result["official_docs"])
    status = "Available" if result["available"] else "Not available"
    return (
        f"{topic['title']}\n"
        f"Status: {topic['status']}\n"
        f"Target Java version: {result['target_version']}\n"
        f"Minimum Java version: {result['minimum_version']}\n"
        f"Documentation version: {result['documentation_version']}\n"
        f"Compatibility: {status}\n"
        f"Recommendation: {result['recommendation']}\n"
        f"Official docs:\n{links}"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic", help="Feature/topic key or alias, such as records, virtual-threads, streams")
    parser.add_argument("--version", required=True, help="Target Java version, such as 8, 17, 21, or 25")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    try:
        result = compatibility(args.topic, args.version)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2) if args.json else render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
