#!/usr/bin/env python3
"""Return official documentation links for common Java topics."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Topic:
    key: str
    title: str
    status: str
    minimum_version: str
    links: tuple[str, ...]
    aliases: tuple[str, ...] = ()


TOPICS: tuple[Topic, ...] = (
    Topic(
        key="records",
        title="Records",
        status="Final language feature",
        minimum_version="16",
        links=(
            "https://openjdk.org/jeps/395",
            "https://docs.oracle.com/en/java/javase/{version}/language/records.html",
            "https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/java/lang/Record.html",
        ),
        aliases=("record", "data carrier", "data class"),
    ),
    Topic(
        key="sealed-classes",
        title="Sealed classes and interfaces",
        status="Final language feature",
        minimum_version="17",
        links=(
            "https://openjdk.org/jeps/409",
            "https://docs.oracle.com/en/java/javase/{version}/language/sealed-classes-and-interfaces.html",
        ),
        aliases=("sealed", "permits", "sealed interfaces"),
    ),
    Topic(
        key="virtual-threads",
        title="Virtual threads",
        status="Final platform feature",
        minimum_version="21",
        links=(
            "https://openjdk.org/jeps/444",
            "https://docs.oracle.com/en/java/javase/{version}/core/virtual-threads.html",
            "https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/java/lang/Thread.html",
        ),
        aliases=("virtual thread", "loom", "lightweight threads"),
    ),
    Topic(
        key="sequenced-collections",
        title="Sequenced collections",
        status="Final API",
        minimum_version="21",
        links=(
            "https://openjdk.org/jeps/431",
            "https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/java/util/SequencedCollection.html",
            "https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/java/util/SequencedSet.html",
            "https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/java/util/SequencedMap.html",
        ),
        aliases=("sequenced collection", "sequenced set", "sequenced map", "reversed collection"),
    ),
    Topic(
        key="pattern-switch",
        title="Pattern matching for switch",
        status="Final language feature",
        minimum_version="21",
        links=(
            "https://openjdk.org/jeps/441",
            "https://docs.oracle.com/en/java/javase/{version}/language/pattern-matching-switch.html",
        ),
        aliases=("switch patterns", "pattern matching switch", "type patterns switch"),
    ),
    Topic(
        key="switch-expressions",
        title="Switch expressions",
        status="Final language feature",
        minimum_version="14",
        links=(
            "https://openjdk.org/jeps/361",
            "https://docs.oracle.com/en/java/javase/{version}/language/switch-expressions-and-statements.html",
        ),
        aliases=("switch expression", "yield"),
    ),
    Topic(
        key="text-blocks",
        title="Text blocks",
        status="Final language feature",
        minimum_version="15",
        links=(
            "https://openjdk.org/jeps/378",
            "https://docs.oracle.com/en/java/javase/{version}/text-blocks/index.html",
        ),
        aliases=("text block", "multiline strings", "multi-line strings"),
    ),
    Topic(
        key="streams",
        title="Streams",
        status="Final API",
        minimum_version="8",
        links=(
            "https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/java/util/stream/package-summary.html",
            "https://docs.oracle.com/javase/tutorial/collections/streams/",
        ),
        aliases=("stream", "stream api", "java streams"),
    ),
    Topic(
        key="optional",
        title="Optional",
        status="Final API",
        minimum_version="8",
        links=(
            "https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/java/util/Optional.html",
        ),
        aliases=("java optional", "nullable", "null optional"),
    ),
    Topic(
        key="modules",
        title="Java Platform Module System",
        status="Final platform feature",
        minimum_version="9",
        links=(
            "https://openjdk.org/jeps/261",
            "https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/module-summary.html",
            "https://docs.oracle.com/en/java/javase/{version}/docs/specs/man/java.html",
        ),
        aliases=("jpms", "module system", "jigsaw"),
    ),
)


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def topic_index() -> dict[str, Topic]:
    index: dict[str, Topic] = {}
    for topic in TOPICS:
        index[normalize(topic.key)] = topic
        index[normalize(topic.title)] = topic
        for alias in topic.aliases:
            index[normalize(alias)] = topic
    return index


def find_topic(query: str) -> Topic:
    normalized = normalize(query)
    index = topic_index()
    if normalized in index:
        return index[normalized]
    matches = [topic for key, topic in index.items() if normalized in key or key in normalized]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if unique_matches:
        options = ", ".join(topic.key for topic in unique_matches)
        raise ValueError(f"ambiguous topic {query!r}; choose one of: {options}")
    available = ", ".join(topic.key for topic in TOPICS)
    raise ValueError(f"unknown topic {query!r}; available topics: {available}")


def links_for(topic: Topic, version: str) -> tuple[str, ...]:
    links = tuple(link.format(version=version) for link in topic.links)
    if version != "8":
        return links
    return tuple(link.replace("https://docs.oracle.com/en/java/javase/8/docs/api/java.base/", "https://docs.oracle.com/javase/8/docs/api/") for link in links)


def payload_for(topic: Topic, version: str) -> dict[str, object]:
    payload = asdict(topic)
    payload["version"] = version
    payload["links"] = list(links_for(topic, version))
    return payload


def render_text(topic: Topic, version: str = "25") -> str:
    links = "\n".join(f"- {link}" for link in links_for(topic, version))
    return (
        f"{topic.title}\n"
        f"Key: {topic.key}\n"
        f"Status: {topic.status}\n"
        f"Minimum Java version: {topic.minimum_version}\n"
        f"Documentation version: {version}\n"
        f"Official docs:\n{links}"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic", nargs="?", help="Topic key or alias")
    parser.add_argument("--list", action="store_true", help="List known topic keys")
    parser.add_argument("--version", default="25", help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        keys = [topic.key for topic in TOPICS]
        print(json.dumps(keys) if args.json else "\n".join(keys))
        return 0

    if not args.topic:
        parser.error("topic is required unless --list is used")

    try:
        topic = find_topic(args.topic)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(payload_for(topic, args.version), indent=2) if args.json else render_text(topic, args.version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
