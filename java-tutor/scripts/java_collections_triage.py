#!/usr/bin/env python3
"""Triage Java collections, streams, Optional, and equality issues with official links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class CollectionsIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def jls(section: str, version: str = DEFAULT_VERSION) -> str:
    chapter = section.split(".")[0]
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/jls-{chapter}.html#jls-{section}"


def issues(version: str = DEFAULT_VERSION) -> tuple[CollectionsIssue, ...]:
    collection = api("java/util/Collection.html", version)
    list_api = api("java/util/List.html", version)
    set_api = api("java/util/Set.html", version)
    map_api = api("java/util/Map.html", version)
    collections_api = api("java/util/Collections.html", version)
    objects_api = api("java/util/Objects.html", version)
    optional_api = api("java/util/Optional.html", version)
    stream_api = api("java/util/stream/package-summary.html", version)
    concurrent_mod = api("java/util/ConcurrentModificationException.html", version)
    comparable = api("java/lang/Comparable.html", version)
    comparator = api("java/util/Comparator.html", version)
    return (
        CollectionsIssue(
            key="collection-choice",
            title="Choosing List, Set, Map, Queue, or specialized collection types",
            aliases=("choose collection", "list vs set", "map vs list", "queue", "deque", "collection type"),
            first_checks=(
                "Identify whether callers need ordering, uniqueness, key lookup, duplicates, random access, FIFO/LIFO behavior, or concurrency.",
                "Check expected size, mutation frequency, lookup frequency, iteration order requirements, and null handling.",
                "Confirm whether the API should expose an interface type or a concrete implementation detail.",
            ),
            fixes_to_consider=(
                "Use List for ordered positional data, Set for uniqueness, Map for key-based lookup, and Queue/Deque for work ordering.",
                "Return interfaces from APIs unless a concrete behavior is part of the contract.",
                "Document iteration order when callers can observe it.",
            ),
            pitfalls=(
                "Choosing a HashSet or HashMap when stable iteration order is a requirement.",
                "Using a List for repeated membership checks when a Set would express intent and improve lookup behavior.",
                "Exposing mutable collections directly from domain objects or public APIs.",
            ),
            docs=(collection, list_api, set_api, map_api),
        ),
        CollectionsIssue(
            key="equals-hashcode",
            title="equals, hashCode, and hash-based collection behavior",
            aliases=("equals", "hashcode", "hash map key", "hashset duplicate", "contains not working"),
            first_checks=(
                "Check whether objects used as HashMap keys or HashSet elements implement equals and hashCode consistently.",
                "Confirm key fields do not mutate while the object is stored in a hash-based collection.",
                "Compare record, value-object, identity, and entity semantics before changing equality.",
            ),
            fixes_to_consider=(
                "Implement equals and hashCode from the same stable fields.",
                "Prefer immutable keys for hash-based collections.",
                "Use records when shallow immutable data-carrier semantics match the design and the Java version supports them.",
            ),
            pitfalls=(
                "Overriding equals without overriding hashCode.",
                "Mutating a key after insertion, making lookup fail even though the object is still present.",
                "Using arrays as value components without considering array identity equality.",
            ),
            docs=(api("java/lang/Object.html", version), objects_api, map_api, set_api, jls("8.10.3", version)),
        ),
        CollectionsIssue(
            key="ordering-comparison",
            title="Comparable, Comparator, sorting, and ordering contracts",
            aliases=("sort", "sorting", "comparable", "comparator", "compareto", "comparison method violates"),
            first_checks=(
                "Identify whether natural ordering or a contextual Comparator should define the order.",
                "Check comparator transitivity, antisymmetry, null handling, and consistency with equals when required.",
                "Confirm whether sorting must be stable and whether the input collection supports mutation.",
            ),
            fixes_to_consider=(
                "Use Comparator factory methods and composition for readable ordering rules.",
                "Keep compareTo consistent with equals when values are used in sorted sets or maps unless documented otherwise.",
                "Use defensive null handling explicitly instead of accidental NullPointerException behavior.",
            ),
            pitfalls=(
                "Subtracting integers in a comparator and overflowing.",
                "Returning inconsistent comparison results for equal inputs.",
                "Using TreeSet or TreeMap with a comparator that treats distinct values as equal.",
            ),
            docs=(comparable, comparator, collections_api, jls("15.21.1", version)),
        ),
        CollectionsIssue(
            key="concurrent-modification",
            title="ConcurrentModificationException and safe iteration/mutation",
            aliases=("concurrentmodificationexception", "modify while iterating", "fail-fast", "iterator remove"),
            first_checks=(
                "Identify which collection is being iterated and which code path mutates it.",
                "Check whether mutation happens through the iterator, collection API, stream pipeline, callback, or another thread.",
                "Confirm whether the collection's iterator is fail-fast, weakly consistent, snapshot-based, or synchronized externally.",
            ),
            fixes_to_consider=(
                "Use Iterator.remove when removing the current element during iteration and the iterator supports it.",
                "Collect changes separately, then apply them after iteration.",
                "Use concurrent collections or explicit synchronization when multiple threads mutate shared collections.",
            ),
            pitfalls=(
                "Assuming ConcurrentModificationException always means multiple threads are involved.",
                "Mutating a collection from inside a stream pipeline operating on the same collection.",
                "Relying on fail-fast behavior for correctness instead of fixing the mutation pattern.",
            ),
            docs=(concurrent_mod, collection, api("java/util/Iterator.html", version), api("java/util/concurrent/package-summary.html", version)),
        ),
        CollectionsIssue(
            key="map-updates",
            title="Map updates, compute/merge, nulls, and default methods",
            aliases=("computeifabsent", "compute", "merge", "putifabsent", "map update", "cache map"),
            first_checks=(
                "Check whether the update must be atomic with respect to other updates.",
                "Identify how null keys, null values, missing mappings, and mapping-function exceptions should behave.",
                "Confirm whether the map implementation permits nulls and whether it is concurrent.",
            ),
            fixes_to_consider=(
                "Use computeIfAbsent, compute, merge, or putIfAbsent to express common update patterns.",
                "Use ConcurrentHashMap when map-local atomic updates must be thread-safe.",
                "Keep mapping functions side-effect-light and avoid recursive updates to the same map.",
            ),
            pitfalls=(
                "Writing check-then-put code that races under concurrency.",
                "Assuming all Map implementations permit null keys or null values.",
                "Doing expensive or externally visible work inside mapping functions without considering retries or exceptions.",
            ),
            docs=(map_api, api("java/util/concurrent/ConcurrentHashMap.html", version)),
        ),
        CollectionsIssue(
            key="optional-usage",
            title="Optional usage, null boundaries, and API design",
            aliases=("optional", "nullable", "orElse", "orElseGet", "null optional"),
            first_checks=(
                "Identify whether Optional is used as a return type, field, parameter, collection element, or local pipeline helper.",
                "Check whether null can cross the API boundary and where it should be converted.",
                "Inspect eager versus lazy fallback behavior in orElse and orElseGet.",
            ),
            fixes_to_consider=(
                "Use Optional primarily to model possibly absent return values.",
                "Convert nullable inputs at the boundary and keep internal code consistent.",
                "Use orElseGet when fallback construction is expensive or has side effects.",
            ),
            pitfalls=(
                "Calling get without checking presence or using an appropriate fallback.",
                "Returning null from a method whose declared return type is Optional.",
                "Using Optional fields or parameters without a clear framework/API reason.",
            ),
            docs=(optional_api, api("java/util/NoSuchElementException.html", version)),
        ),
        CollectionsIssue(
            key="stream-pipeline",
            title="Stream pipelines, side effects, laziness, and parallel streams",
            aliases=("stream", "streams", "parallel stream", "side effects", "collect", "lazy"),
            first_checks=(
                "Identify the stream source, intermediate operations, terminal operation, and whether the pipeline is sequential or parallel.",
                "Check for side effects, shared mutable state, encounter-order assumptions, and short-circuiting behavior.",
                "Confirm whether the source can be reused; streams are single-use pipelines.",
            ),
            fixes_to_consider=(
                "Prefer side-effect-free intermediate operations and explicit collectors.",
                "Use parallel streams only when the workload, source splitting, and thread-safety assumptions justify it.",
                "Replace clever streams with loops when mutation, exceptions, or debugging clarity dominate.",
            ),
            pitfalls=(
                "Forgetting that intermediate operations are lazy until a terminal operation runs.",
                "Mutating the source collection during stream traversal.",
                "Assuming parallel streams speed up blocking or small workloads.",
            ),
            docs=(stream_api, collection, api("java/util/stream/Collectors.html", version)),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, CollectionsIssue]:
    index: dict[str, CollectionsIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> CollectionsIssue:
    normalized = normalize(query)
    index = issue_index(version)
    if normalized in index:
        return index[normalized]
    matches = [issue for key, issue in index.items() if normalized in key or key in normalized]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if unique_matches:
        options = ", ".join(issue.key for issue in unique_matches)
        raise ValueError(f"ambiguous collections issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown collections issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[CollectionsIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: CollectionsIssue) -> str:
    lines = [issue.title, f"Key: {issue.key}", "", "First checks:"]
    lines.extend(f"{index}. {check}" for index, check in enumerate(issue.first_checks, start=1))
    lines.extend(["", "Fixes to consider:"])
    lines.extend(f"- {item}" for item in issue.fixes_to_consider)
    lines.extend(["", "Pitfalls:"])
    lines.extend(f"- {item}" for item in issue.pitfalls)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in issue.docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue", nargs="?", help="Collections issue key or alias")
    parser.add_argument("--list", action="store_true", help="List known issue keys")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        keys = [issue.key for issue in issues(args.version)]
        print(json.dumps(keys, indent=2) if args.json else "\n".join(keys))
        return 0

    if not args.issue:
        parser.error("issue is required unless --list is used")

    try:
        issue = find_issue(args.issue, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(issue)
        payload["official_docs"] = list(issue.docs)
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(issue))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
