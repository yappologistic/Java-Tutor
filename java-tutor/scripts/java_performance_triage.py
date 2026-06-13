#!/usr/bin/env python3
"""Triage common Java performance symptoms with official JDK tooling links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class PerformanceSymptom:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    evidence: tuple[str, ...]
    commands: tuple[str, ...]
    docs: tuple[str, ...]


def doc(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/{path}"


def symptoms(version: str = DEFAULT_VERSION) -> tuple[PerformanceSymptom, ...]:
    jcmd = doc("docs/specs/man/jcmd.html", version)
    jmap = doc("docs/specs/man/jmap.html", version)
    jfr_intro = "https://dev.java/learn/jvm/jfr/"
    diagnostic_tools = doc("troubleshoot/diagnostic-tools.html", version)
    performance_jfr = doc("troubleshoot/troubleshoot-performance-issues-using-jfr.html", version)
    memory_leaks = doc("troubleshoot/troubleshooting-memory-leaks.html", version)
    gc_tuning = doc("gctuning/introduction-garbage-collection-tuning.html", version)
    prepare = doc("troubleshoot/prepare-java-troubleshooting.html", version)
    return (
        PerformanceSymptom(
            key="high-cpu",
            title="High CPU or throughput regression",
            aliases=("cpu", "hot method", "slow", "throughput", "latency"),
            first_checks=(
                "Confirm whether the issue is CPU saturation, blocking, GC, I/O, or an external dependency before changing code.",
                "Capture a time-bounded profile during the bad interval, not after the system has recovered.",
                "Compare load, request mix, JVM version, flags, heap size, and deployment environment to the known-good baseline.",
            ),
            evidence=(
                "JFR recording covering the slow interval",
                "CPU, allocation, thread, and lock profiles",
                "Recent deployment/configuration changes",
            ),
            commands=(
                "jcmd <pid> JFR.start name=profile settings=profile duration=120s filename=profile.jfr",
                "jcmd <pid> Thread.print",
                "jcmd <pid> VM.command_line",
            ),
            docs=(jfr_intro, diagnostic_tools, performance_jfr, jcmd),
        ),
        PerformanceSymptom(
            key="gc-pauses",
            title="Garbage collection pauses or allocation pressure",
            aliases=("gc", "garbage collection", "pause", "allocation", "heap pressure"),
            first_checks=(
                "Separate allocation rate, live-set growth, heap sizing, collector choice, and application-level retention.",
                "Do not tune GC flags before collecting GC logs or JFR evidence for the workload.",
                "Check whether pauses correlate with traffic spikes, batch jobs, caches, finalization, or large object allocation.",
            ),
            evidence=(
                "GC logs or JFR GC events",
                "Heap occupancy before and after GC",
                "Allocation hot spots and object lifetime clues",
            ),
            commands=(
                "jcmd <pid> JFR.start name=gc settings=profile duration=300s filename=gc.jfr",
                "jcmd <pid> GC.heap_info",
                "jcmd <pid> VM.flags",
            ),
            docs=(performance_jfr, gc_tuning, diagnostic_tools, jcmd),
        ),
        PerformanceSymptom(
            key="memory-leak",
            title="Memory leak or unbounded heap growth",
            aliases=("memory", "leak", "oom", "outofmemory", "heap growth"),
            first_checks=(
                "Distinguish a true leak from a legitimate cache, workload growth, fragmentation, or delayed collection.",
                "Capture evidence before restart: heap histogram, heap dump if acceptable, and JFR with heap statistics when useful.",
                "Treat heap dumps as sensitive data because they can contain credentials and user data.",
            ),
            evidence=(
                "Heap histogram trend across time",
                "Heap dump from a representative bad state",
                "JFR heap statistics or object count growth",
            ),
            commands=(
                "jcmd <pid> GC.class_histogram",
                "jcmd <pid> GC.heap_dump filename=heap.hprof",
                "jmap -histo:live <pid>",
            ),
            docs=(memory_leaks, diagnostic_tools, jcmd, jmap),
        ),
        PerformanceSymptom(
            key="thread-contention",
            title="Thread contention, deadlock, or blocking",
            aliases=("thread", "threads", "deadlock", "lock", "blocked", "contention"),
            first_checks=(
                "Check whether threads are runnable, blocked on locks, parked, waiting on I/O, or waiting on external systems.",
                "Take multiple thread dumps several seconds apart so repeated stack states can be compared.",
                "Use JFR lock and thread events to connect contention with code paths and workload timing.",
            ),
            evidence=(
                "At least three thread dumps across the incident",
                "JFR lock, thread, and scheduling events",
                "Executor configuration and queue depth",
            ),
            commands=(
                "jcmd <pid> Thread.print",
                "jcmd <pid> JFR.start name=threads settings=profile duration=120s filename=threads.jfr",
                "jcmd <pid> VM.system_properties",
            ),
            docs=(diagnostic_tools, performance_jfr, jcmd),
        ),
        PerformanceSymptom(
            key="startup",
            title="Slow startup or warmup",
            aliases=("startup", "warmup", "cold start", "slow start"),
            first_checks=(
                "Measure startup phases separately: process launch, class loading, framework initialization, JIT warmup, and first request.",
                "Compare classpath/module path, container CPU limits, CDS usage, logging configuration, and dependency initialization.",
                "Avoid optimizing steady-state hot paths until startup evidence points there.",
            ),
            evidence=(
                "JFR recording from process start",
                "JVM command line and flags",
                "Class loading and initialization timing",
            ),
            commands=(
                "java -XX:StartFlightRecording=filename=startup.jfr,settings=profile,dumponexit=true ...",
                "jcmd <pid> VM.command_line",
                "jcmd <pid> VM.uptime",
            ),
            docs=(prepare, jfr_intro, diagnostic_tools, jcmd),
        ),
        PerformanceSymptom(
            key="io",
            title="File, socket, or external I/O bottleneck",
            aliases=("io", "i/o", "socket", "network", "file", "database"),
            first_checks=(
                "Confirm whether time is spent in Java code, kernel I/O, remote services, DNS, connection pools, or backpressure.",
                "Enable JFR file and socket events when I/O is suspected.",
                "Correlate application timing with service metrics and operating-system resource saturation.",
            ),
            evidence=(
                "JFR socket/file read and write events",
                "Timeout/error logs with timestamps",
                "Connection pool and downstream service metrics",
            ),
            commands=(
                "jcmd <pid> JFR.start name=io settings=profile duration=180s filename=io.jfr",
                "jcmd <pid> Thread.print",
            ),
            docs=(performance_jfr, diagnostic_tools, jcmd),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.lower().replace("_", "-").split())


def symptom_index(version: str = DEFAULT_VERSION) -> dict[str, PerformanceSymptom]:
    index: dict[str, PerformanceSymptom] = {}
    for symptom in symptoms(version):
        index[normalize(symptom.key)] = symptom
        index[normalize(symptom.title)] = symptom
        for alias in symptom.aliases:
            index[normalize(alias)] = symptom
    return index


def find_symptom(query: str, version: str = DEFAULT_VERSION) -> PerformanceSymptom:
    normalized = normalize(query)
    index = symptom_index(version)
    if normalized in index:
        return index[normalized]
    matches = [symptom for key, symptom in index.items() if normalized in key or key in normalized]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if unique_matches:
        options = ", ".join(symptom.key for symptom in unique_matches)
        raise ValueError(f"ambiguous symptom {query!r}; choose one of: {options}")
    available = ", ".join(symptom.key for symptom in symptoms(version))
    raise ValueError(f"unknown symptom {query!r}; available symptoms: {available}")


def official_urls(selected: Iterable[PerformanceSymptom]) -> tuple[str, ...]:
    urls: list[str] = []
    for symptom in selected:
        urls.extend(symptom.docs)
    return tuple(dict.fromkeys(urls))


def render_text(symptom: PerformanceSymptom) -> str:
    lines = [symptom.title, f"Key: {symptom.key}", "", "First checks:"]
    lines.extend(f"{index}. {check}" for index, check in enumerate(symptom.first_checks, start=1))
    lines.extend(["", "Evidence to collect:"])
    lines.extend(f"- {item}" for item in symptom.evidence)
    lines.extend(["", "Useful commands:"])
    lines.extend(f"- `{command}`" for command in symptom.commands)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in symptom.docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("symptom", nargs="?", help="Symptom key or alias")
    parser.add_argument("--list", action="store_true", help="List known symptom keys")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        keys = [symptom.key for symptom in symptoms(args.version)]
        print(json.dumps(keys, indent=2) if args.json else "\n".join(keys))
        return 0

    if not args.symptom:
        parser.error("symptom is required unless --list is used")

    try:
        symptom = find_symptom(args.symptom, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(symptom)
        payload["official_docs"] = list(symptom.docs)
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(symptom))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
