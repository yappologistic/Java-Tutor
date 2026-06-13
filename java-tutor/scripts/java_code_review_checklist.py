#!/usr/bin/env python3
"""Generate an official-doc-backed Java code review checklist."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class ReviewItem:
    check: str
    why: str
    docs: tuple[str, ...]


@dataclass(frozen=True)
class ReviewArea:
    key: str
    title: str
    items: tuple[ReviewItem, ...]


def api_link(api_path: str, version: str) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/{api_path}"


def jls_link(section: str, version: str) -> str:
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/{section}"


def java_doc(path: str, version: str) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/{path}"


def areas(version: str = DEFAULT_VERSION) -> tuple[ReviewArea, ...]:
    collection_docs = api_link("java.base/java/util/Collection.html", version)
    optional_docs = api_link("java.base/java/util/Optional.html", version)
    autocloseable_docs = api_link("java.base/java/lang/AutoCloseable.html", version)
    concurrent_docs = api_link("java.base/java/util/concurrent/package-summary.html", version)
    objects_docs = api_link("java.base/java/util/Objects.html", version)
    return (
        ReviewArea(
            key="correctness",
            title="Correctness and API Contracts",
            items=(
                ReviewItem(
                    check="Check equality, ordering, and hash-code contracts for collections, maps, records, and sorted structures.",
                    why="Broken contracts can make lookups, deduplication, sorting, and caches behave incorrectly.",
                    docs=(api_link("java.base/java/lang/Object.html", version), collection_docs),
                ),
                ReviewItem(
                    check="Check boundary conditions around empty input, absent values, indexes, numeric ranges, and exceptional paths.",
                    why="Most production bugs hide outside the happy path; API contracts usually define these edge cases explicitly.",
                    docs=(optional_docs, jls_link("jls-11.html", version)),
                ),
                ReviewItem(
                    check="Check nullability at API boundaries and prefer explicit validation or domain absence over accidental null flow.",
                    why="Failing near the source of bad input makes defects easier to diagnose and reduces later NullPointerException risk.",
                    docs=(objects_docs, optional_docs),
                ),
            ),
        ),
        ReviewArea(
            key="resources",
            title="Resource Management",
            items=(
                ReviewItem(
                    check="Check every closeable resource, stream, file handle, socket, and lock for deterministic release on success and failure.",
                    why="Resource leaks can exhaust file descriptors, memory, threads, database connections, or locks.",
                    docs=(autocloseable_docs, "https://www.oracle.com/java/technologies/javase/seccodeguide.html"),
                ),
                ReviewItem(
                    check="Prefer try-with-resources for AutoCloseable values and keep resource ownership clear across method boundaries.",
                    why="try-with-resources makes release behavior visible and preserves suppressed exceptions.",
                    docs=(autocloseable_docs, jls_link("jls-14.html#jls-14.20.3", version)),
                ),
            ),
        ),
        ReviewArea(
            key="concurrency",
            title="Concurrency and Memory Model",
            items=(
                ReviewItem(
                    check="Check shared mutable state for a clear happens-before relationship, safe publication, or confinement.",
                    why="Data races can produce stale reads, lost updates, and behavior that is legal but surprising under the Java Memory Model.",
                    docs=(jls_link("jls-17.html", version), concurrent_docs),
                ),
                ReviewItem(
                    check="Check blocking calls, synchronized regions, locks, executors, and futures for deadlocks, starvation, and cancellation behavior.",
                    why="Concurrency bugs often appear only under load, cancellation, interruption, or shutdown.",
                    docs=(concurrent_docs,),
                ),
                ReviewItem(
                    check="Check collection mutation during iteration and use concurrent collections only when their consistency guarantees fit the design.",
                    why="Fail-fast iterators are diagnostic aids; they are not synchronization or correctness mechanisms.",
                    docs=(collection_docs, concurrent_docs),
                ),
            ),
        ),
        ReviewArea(
            key="security",
            title="Security and Trust Boundaries",
            items=(
                ReviewItem(
                    check="Identify trust boundaries and validate, normalize, or reject data before using it for paths, commands, parsing, reflection, SQL, XML, or serialization.",
                    why="Secure Java code still depends on disciplined input handling around untrusted data.",
                    docs=(
                        "https://www.oracle.com/java/technologies/javase/seccodeguide.html",
                        java_doc("security/index.html", version),
                    ),
                ),
                ReviewItem(
                    check="Check secret handling, logging, exception messages, temporary files, and serialization for accidental disclosure.",
                    why="Confidential data often leaks through diagnostics and secondary storage rather than the primary business path.",
                    docs=("https://www.oracle.com/java/technologies/javase/seccodeguide.html",),
                ),
                ReviewItem(
                    check="Check dependency, provider, crypto, TLS, and permissions assumptions against the deployed JDK and runtime environment.",
                    why="Security behavior can depend on JDK version, provider configuration, disabled algorithms, and deployment policy.",
                    docs=(
                        java_doc("security/java-security-overview1.html", version),
                        java_doc("security/index.html", version),
                    ),
                ),
            ),
        ),
        ReviewArea(
            key="compatibility",
            title="Compatibility and Maintainability",
            items=(
                ReviewItem(
                    check="Check source, target, and runtime Java versions before recommending newer APIs, language features, or library upgrades.",
                    why="A correct patch can still break builds or deployments when it exceeds the configured Java baseline.",
                    docs=(
                        java_doc("migrate/index.html", version),
                        "https://docs.oracle.com/en/java/javase/",
                    ),
                ),
                ReviewItem(
                    check="Check public API changes for binary/source compatibility, serialization shape, checked exceptions, and behavioral contract changes.",
                    why="Library users depend on more than signatures; compatibility includes documented behavior and runtime linkage.",
                    docs=(jls_link("jls-13.html", version),),
                ),
            ),
        ),
    )


ALIASES = {
    "correctness": "correctness",
    "api": "correctness",
    "null": "correctness",
    "resources": "resources",
    "resource": "resources",
    "io": "resources",
    "concurrency": "concurrency",
    "threads": "concurrency",
    "threading": "concurrency",
    "security": "security",
    "secure": "security",
    "compat": "compatibility",
    "compatibility": "compatibility",
    "migration": "compatibility",
    "versions": "compatibility",
}


def select_areas(focuses: Iterable[str] | None = None, version: str = DEFAULT_VERSION) -> tuple[ReviewArea, ...]:
    all_areas = areas(version)
    by_key = {area.key: area for area in all_areas}
    if not focuses:
        return all_areas

    selected: list[ReviewArea] = []
    unknown: list[str] = []
    for focus in focuses:
        key = ALIASES.get(focus.lower().strip())
        if not key:
            unknown.append(focus)
            continue
        area = by_key[key]
        if area not in selected:
            selected.append(area)
    if unknown:
        valid = ", ".join(sorted(ALIASES))
        raise ValueError(f"unknown focus area(s): {', '.join(unknown)}; valid focuses: {valid}")
    return tuple(selected)


def official_urls(selected: Iterable[ReviewArea]) -> tuple[str, ...]:
    urls: list[str] = []
    for area in selected:
        for item in area.items:
            urls.extend(item.docs)
    return tuple(dict.fromkeys(urls))


def checklist_payload(focuses: Iterable[str] | None = None, version: str = DEFAULT_VERSION) -> dict[str, object]:
    selected = select_areas(focuses, version)
    return {
        "version": version,
        "areas": [
            {
                "key": area.key,
                "title": area.title,
                "items": [asdict(item) for item in area.items],
            }
            for area in selected
        ],
        "official_docs": list(official_urls(selected)),
    }


def render_text(focuses: Iterable[str] | None = None, version: str = DEFAULT_VERSION) -> str:
    selected = select_areas(focuses, version)
    lines = [f"Java code review checklist (Java SE {version})"]
    for area in selected:
        lines.extend(["", f"## {area.title}"])
        for index, item in enumerate(area.items, start=1):
            lines.append(f"{index}. {item.check}")
            lines.append(f"   Why: {item.why}")
            lines.append(f"   Docs: {', '.join(item.docs)}")
    lines.extend(["", "Official docs:"])
    for url in official_urls(selected):
        lines.append(f"- {url}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("focus", nargs="*", help="Optional focus areas: correctness, resources, concurrency, security, compatibility")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    try:
        output = checklist_payload(args.focus, args.version) if args.json else render_text(args.focus, args.version)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(output, indent=2) if args.json else output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
