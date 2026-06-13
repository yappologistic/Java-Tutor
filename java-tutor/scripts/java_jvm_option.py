#!/usr/bin/env python3
"""Triage JVM launcher options with official Java documentation links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class JvmOptionArea:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    option_families: tuple[str, ...]
    cautions: tuple[str, ...]
    docs: tuple[str, ...]


def doc(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/{path}"


def areas(version: str = DEFAULT_VERSION) -> tuple[JvmOptionArea, ...]:
    java_man = doc("docs/specs/man/java.html", version)
    gctuning = doc("gctuning/introduction-garbage-collection-tuning.html", version)
    diagnostics = doc("troubleshoot/diagnostic-tools.html", version)
    jfr = doc("troubleshoot/troubleshoot-performance-issues-using-jfr.html", version)
    virtual_threads = doc("core/virtual-threads.html", version)
    return (
        JvmOptionArea(
            key="heap-sizing",
            title="Heap sizing and memory limits",
            aliases=("heap", "xmx", "xms", "memory", "outofmemory", "container memory"),
            first_checks=(
                "Capture the exact launch command, Java version, container limits, and observed memory failure.",
                "Check whether the process is limited by heap, metaspace, native memory, direct buffers, or the operating system.",
                "Compare Xms/Xmx and percentage-based heap sizing with the workload and deployment limits.",
            ),
            option_families=("-Xms", "-Xmx", "-XX:InitialRAMPercentage", "-XX:MaxRAMPercentage", "-XX:MaxMetaspaceSize"),
            cautions=(
                "Do not increase heap size before identifying which memory pool or native allocation is exhausted.",
                "Leave headroom for metaspace, thread stacks, code cache, direct buffers, JFR, and native libraries.",
                "Container memory limits can make host-level memory assumptions wrong.",
            ),
            docs=(java_man, gctuning, diagnostics),
        ),
        JvmOptionArea(
            key="gc-selection",
            title="Garbage collector selection and tuning",
            aliases=("gc", "garbage collector", "g1", "zgc", "shenandoah", "parallelgc", "low latency"),
            first_checks=(
                "Identify the current collector, heap size, latency goals, throughput goals, and allocation rate.",
                "Collect GC logs or JFR evidence before changing collectors or pause targets.",
                "Check whether the application is latency-sensitive, throughput-oriented, memory-constrained, or startup-sensitive.",
            ),
            option_families=("-XX:+UseG1GC", "-XX:+UseZGC", "-XX:+UseParallelGC", "-XX:MaxGCPauseMillis", "-Xlog:gc*"),
            cautions=(
                "Changing collectors can improve one workload and regress another; measure under representative load.",
                "Pause-time goals are goals, not hard guarantees.",
                "Tuning too many GC flags can make future JDK upgrades harder.",
            ),
            docs=(java_man, gctuning, jfr),
        ),
        JvmOptionArea(
            key="gc-logging",
            title="GC, safepoint, and unified JVM logging",
            aliases=("xlog", "gc log", "gc logging", "safepoint", "unified logging"),
            first_checks=(
                "Capture existing logging flags and the Java version because legacy GC logging flags differ from unified logging.",
                "Choose tags and levels that answer the question without producing excessive production log volume.",
                "Preserve timestamps, uptime, rotation, and file names so logs are useful after collection.",
            ),
            option_families=("-Xlog:gc", "-Xlog:gc*", "-Xlog:safepoint", "-Xlog:os+container", "-Xlog:help"),
            cautions=(
                "Verbose logging can create large files quickly under allocation-heavy workloads.",
                "GC logs are evidence; do not treat a single pause without workload context as the root cause.",
                "Protect logs when command lines, paths, hostnames, or environment details are sensitive.",
            ),
            docs=(java_man, gctuning, diagnostics),
        ),
        JvmOptionArea(
            key="preview-features",
            title="Preview feature enablement",
            aliases=("preview", "enable-preview", "preview feature", "source preview"),
            first_checks=(
                "Confirm whether the feature is preview, incubator, final, or removed in the target Java version.",
                "Use --enable-preview consistently at compile time, test time, and run time.",
                "Check source/release settings in Maven, Gradle, IDE, and CI before changing code.",
            ),
            option_families=("--enable-preview", "--source", "--release"),
            cautions=(
                "Do not present preview behavior as stable Java SE behavior.",
                "Preview source or bytecode may not compile or run on a later Java release without changes.",
                "Libraries should avoid exposing preview-dependent public APIs unless the project accepts that risk.",
            ),
            docs=(java_man, "https://openjdk.org/jeps/12"),
        ),
        JvmOptionArea(
            key="module-access",
            title="Module access, encapsulation, and illegal reflection flags",
            aliases=("add-opens", "add-exports", "illegal access", "reflection", "encapsulation", "jpms"),
            first_checks=(
                "Identify the exact reflective access or module readability failure.",
                "Prefer upgrading libraries or using supported APIs before adding broad opens or exports.",
                "If a flag is necessary, scope it to the narrowest module/package and target module.",
            ),
            option_families=("--add-opens", "--add-exports", "--add-reads", "--module-path", "--add-modules"),
            cautions=(
                "Broad module-opening flags can hide dependency or library compatibility problems.",
                "Internal JDK APIs are unsupported and can change or disappear between releases.",
                "Runtime flags do not fix compile-time module design issues by themselves.",
            ),
            docs=(java_man, "https://openjdk.org/jeps/261", doc("migrate/index.html", version)),
        ),
        JvmOptionArea(
            key="assertions-properties",
            title="Assertions, system properties, and environment-sensitive defaults",
            aliases=("assert", "assertions", "ea", "system property", "-d", "-D", "file.encoding", "timezone"),
            first_checks=(
                "Separate JVM system properties from application arguments and environment variables.",
                "Check whether assertions are enabled for the intended classes or packages.",
                "Record locale, charset, time zone, and user.dir when behavior changes by environment.",
            ),
            option_families=("-ea", "-enableassertions", "-da", "-Dname=value", "-showversion"),
            cautions=(
                "Assertions can be disabled in production, so do not rely on them for required validation.",
                "Global system properties can affect libraries far from the code under investigation.",
                "Changing charset, locale, or time zone flags can mask portability bugs.",
            ),
            docs=(java_man, doc("docs/api/java.base/java/lang/System.html", version)),
        ),
        JvmOptionArea(
            key="diagnostics",
            title="Runtime diagnostics, crash output, and observability flags",
            aliases=("diagnostic", "jfr", "heap dump", "thread dump", "crash", "hs_err", "jcmd"),
            first_checks=(
                "Prefer evidence-gathering flags that answer the immediate question with limited overhead.",
                "Choose JFR, heap dumps, thread dumps, native memory tracking, or crash logs based on the symptom.",
                "Plan storage, retention, and access controls for generated diagnostic artifacts.",
            ),
            option_families=("-XX:StartFlightRecording", "-XX:FlightRecorderOptions", "-XX:+HeapDumpOnOutOfMemoryError", "-XX:ErrorFile", "-XX:NativeMemoryTracking"),
            cautions=(
                "Diagnostic artifacts may contain secrets, personal data, SQL, request data, paths, and command lines.",
                "Some diagnostic flags add overhead; validate impact before enabling them broadly.",
                "Heap dumps can be very large and should be handled as sensitive production data.",
            ),
            docs=(java_man, diagnostics, jfr),
        ),
        JvmOptionArea(
            key="virtual-thread-diagnostics",
            title="Virtual thread diagnostics and runtime behavior",
            aliases=("virtual thread flag", "loom flag", "pinning", "jdk.tracePinnedThreads", "virtual thread diagnostics"),
            first_checks=(
                "Confirm the Java version supports virtual threads and the workload is blocking-I/O oriented.",
                "Use thread dumps, JFR, and targeted diagnostics before changing synchronization or resource limits.",
                "Check whether the issue is carrier pinning, downstream capacity, thread-local use, or ordinary blocking.",
            ),
            option_families=("-Djdk.tracePinnedThreads", "-Djdk.virtualThreadScheduler.parallelism", "jcmd Thread.print", "JFR virtual-thread events"),
            cautions=(
                "Virtual threads do not remove database, socket, file, or downstream service limits.",
                "Scheduler properties are implementation-specific tuning levers; avoid depending on them casually.",
                "Treat pinning diagnostics as evidence to investigate, not as proof that every synchronized block is wrong.",
            ),
            docs=(virtual_threads, java_man, jfr),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def area_index(version: str = DEFAULT_VERSION) -> dict[str, JvmOptionArea]:
    index: dict[str, JvmOptionArea] = {}
    for area in areas(version):
        index[normalize(area.key)] = area
        index[normalize(area.title)] = area
        for alias in area.aliases:
            index[normalize(alias)] = area
    return index


def find_area(query: str, version: str = DEFAULT_VERSION) -> JvmOptionArea:
    normalized = normalize(query)
    index = area_index(version)
    if normalized in index:
        return index[normalized]
    matches = [area for key, area in index.items() if normalized in key or key in normalized]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if unique_matches:
        options = ", ".join(area.key for area in unique_matches)
        raise ValueError(f"ambiguous JVM option area {query!r}; choose one of: {options}")
    available = ", ".join(area.key for area in areas(version))
    raise ValueError(f"unknown JVM option area {query!r}; available areas: {available}")


def official_urls(selected: Iterable[JvmOptionArea]) -> tuple[str, ...]:
    urls: list[str] = []
    for area in selected:
        urls.extend(area.docs)
    return tuple(dict.fromkeys(urls))


def render_text(area: JvmOptionArea) -> str:
    lines = [area.title, f"Key: {area.key}", "", "First checks:"]
    lines.extend(f"{index}. {check}" for index, check in enumerate(area.first_checks, start=1))
    lines.extend(["", "Option families:"])
    lines.extend(f"- {option}" for option in area.option_families)
    lines.extend(["", "Cautions:"])
    lines.extend(f"- {caution}" for caution in area.cautions)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in area.docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("area", nargs="?", help="JVM option area key or alias")
    parser.add_argument("--list", action="store_true", help="List known JVM option areas")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        keys = [area.key for area in areas(args.version)]
        print(json.dumps(keys, indent=2) if args.json else "\n".join(keys))
        return 0

    if not args.area:
        parser.error("area is required unless --list is used")

    try:
        area = find_area(args.area, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(area)
        payload["official_docs"] = list(area.docs)
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(area))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
