#!/usr/bin/env python3
"""Triage common Java concurrency symptoms with official documentation links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class ConcurrencyConcern:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    evidence: tuple[str, ...]
    safer_defaults: tuple[str, ...]
    docs: tuple[str, ...]


def doc(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/{path}"


def jls_memory_model(version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/jls-17.html"


def concerns(version: str = DEFAULT_VERSION) -> tuple[ConcurrencyConcern, ...]:
    thread_api = doc("docs/api/java.base/java/lang/Thread.html", version)
    interrupted = doc("docs/api/java.base/java/lang/InterruptedException.html", version)
    concurrent_pkg = doc("docs/api/java.base/java/util/concurrent/package-summary.html", version)
    executor = doc("docs/api/java.base/java/util/concurrent/ExecutorService.html", version)
    future = doc("docs/api/java.base/java/util/concurrent/Future.html", version)
    concurrent_hash_map = doc("docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html", version)
    atomic_pkg = doc("docs/api/java.base/java/util/concurrent/atomic/package-summary.html", version)
    locks_pkg = doc("docs/api/java.base/java/util/concurrent/locks/package-summary.html", version)
    virtual_threads = doc("core/virtual-threads.html", version)
    return (
        ConcurrencyConcern(
            key="data-race",
            title="Data races, stale reads, and unsafe publication",
            aliases=("race", "visibility", "stale read", "safe publication", "publication"),
            first_checks=(
                "Find shared mutable state accessed by more than one thread.",
                "Check whether every read/write is protected by the same lock, volatile, atomic class, final-field safe publication, or another happens-before edge.",
                "Look for escaping this references, mutable static state, unsafely published caches, and double-checked locking without volatile.",
            ),
            evidence=(
                "Small stress tests that run the suspected path repeatedly.",
                "Thread dumps showing concurrent access paths when locks are expected.",
                "Code paths proving object construction, publication, and later reads.",
            ),
            safer_defaults=(
                "Prefer immutability, confinement, and message passing before shared mutable state.",
                "Use java.util.concurrent abstractions instead of ad hoc wait/notify or unsynchronized flags.",
                "Document the synchronization policy next to the guarded state.",
            ),
            docs=(jls_memory_model(version), thread_api, concurrent_pkg),
        ),
        ConcurrencyConcern(
            key="deadlock",
            title="Deadlocks and lock-order problems",
            aliases=("lock", "blocked", "monitor", "thread dump", "lock order"),
            first_checks=(
                "Capture a thread dump while the application is stuck and inspect blocked threads and owned monitors.",
                "Identify nested locking and whether all code paths acquire locks in one global order.",
                "Check callbacks, logging, equals/hashCode, and external calls made while holding locks.",
            ),
            evidence=(
                "Thread dumps from jcmd, jstack, an IDE, or the service runtime.",
                "A lock graph that shows acquisition order for the involved monitors or locks.",
                "Timing or load conditions needed to reproduce the blocked state.",
            ),
            safer_defaults=(
                "Keep synchronized regions small and avoid calling unknown code while holding a lock.",
                "Use higher-level concurrent collections, queues, or executors when they fit the design.",
                "Prefer timed lock acquisition only when the timeout path is designed and tested.",
            ),
            docs=(thread_api, locks_pkg, concurrent_pkg),
        ),
        ConcurrencyConcern(
            key="interruption-cancellation",
            title="Interruption and cancellation handling",
            aliases=("interrupt", "interruptedexception", "cancel", "cancellation"),
            first_checks=(
                "Find catch blocks for InterruptedException and check whether they restore the interrupt status or stop work intentionally.",
                "Check loops, blocking calls, futures, and executor tasks for cancellation-aware exits.",
                "Confirm cleanup releases locks, files, sockets, and other resources when work is cancelled.",
            ),
            evidence=(
                "Stack traces or thread dumps showing where a task blocks.",
                "Logs showing cancellation requests and whether tasks actually exit.",
                "Tests that cancel work while it is blocked and while it is doing CPU work.",
            ),
            safer_defaults=(
                "Do not swallow InterruptedException silently.",
                "Propagate cancellation to child tasks and external resources when possible.",
                "Use try/finally or try-with-resources so cancellation does not leak resources.",
            ),
            docs=(interrupted, thread_api, future, executor),
        ),
        ConcurrencyConcern(
            key="executor-lifecycle",
            title="Executor, thread pool, and Future lifecycle",
            aliases=("executor", "thread pool", "shutdown", "future", "task leak"),
            first_checks=(
                "Identify who owns the executor and when it is shut down.",
                "Check whether submitted tasks can block forever, queue without bounds, or hide exceptions in Future results.",
                "Check whether shutdown, awaitTermination, cancellation, and rejection behavior are handled deliberately.",
            ),
            evidence=(
                "Thread dump counts and pool thread names before, during, and after the workload.",
                "Metrics for active threads, queued tasks, completed tasks, rejected tasks, and task latency.",
                "Tests that exercise normal completion, exception, timeout, cancellation, and service shutdown.",
            ),
            safer_defaults=(
                "Give executors clear ownership and close/shutdown them at the same lifecycle boundary.",
                "Bound queues or apply backpressure for untrusted or bursty workloads.",
                "Inspect Future results or use completion mechanisms that surface task failures.",
            ),
            docs=(executor, future, concurrent_pkg),
        ),
        ConcurrencyConcern(
            key="virtual-threads",
            title="Virtual thread suitability and migration checks",
            aliases=("loom", "virtual thread", "virtual threads", "pinning"),
            first_checks=(
                "Confirm the application is running on a Java version that supports virtual threads.",
                "Identify whether the workload is mostly blocking I/O rather than CPU-bound work.",
                "Check thread-local usage, synchronization, native calls, and carrier-thread pinning only with evidence from tools or runtime diagnostics.",
            ),
            evidence=(
                "JFR recordings, thread dumps, and throughput/latency before and after the change.",
                "Load tests that preserve the production concurrency shape.",
                "Runtime version and framework support notes for request handling, JDBC, and observability.",
            ),
            safer_defaults=(
                "Use virtual threads to simplify blocking-style concurrent code, not to speed up CPU-bound work.",
                "Keep resource limits explicit; virtual threads do not remove database, socket, file, or downstream capacity limits.",
                "Avoid pooling virtual threads; create them per task through the supported APIs.",
            ),
            docs=(virtual_threads, thread_api, concurrent_pkg),
        ),
        ConcurrencyConcern(
            key="concurrent-collections",
            title="Concurrent collections and compound actions",
            aliases=("concurrenthashmap", "copyonwrite", "queue", "blockingqueue", "collection"),
            first_checks=(
                "Identify whether the collection itself is thread-safe and whether the whole operation is compound.",
                "Replace check-then-act, get-then-put, and iterate-then-mutate races with atomic collection methods where available.",
                "Check iteration semantics, blocking behavior, memory growth, and mutability of stored values.",
            ),
            evidence=(
                "Tests that run the compound operation from many threads.",
                "Heap and queue-size observations for producers and consumers.",
                "Code review of invariants that span multiple collection operations or multiple collections.",
            ),
            safer_defaults=(
                "Use ConcurrentHashMap methods such as compute, merge, or putIfAbsent for map-local atomic updates.",
                "Use BlockingQueue or other purpose-built structures for producer-consumer coordination.",
                "Protect multi-collection invariants with a clear synchronization policy.",
            ),
            docs=(concurrent_hash_map, concurrent_pkg),
        ),
        ConcurrencyConcern(
            key="atomicity",
            title="Atomicity, counters, and volatile misconceptions",
            aliases=("atomic", "volatile", "counter", "lost update", "cas"),
            first_checks=(
                "Check whether the code needs visibility only or an atomic read-modify-write operation.",
                "Look for volatile counters, separate read/check/write steps, and non-atomic updates to shared state.",
                "Confirm invariants that involve more than one field are protected together.",
            ),
            evidence=(
                "Stress tests that compare expected and observed counts under contention.",
                "Code paths showing every mutation of the shared state.",
                "Contention and throughput metrics when choosing between atomic classes, locks, and redesign.",
            ),
            safer_defaults=(
                "Use AtomicInteger, AtomicLong, LongAdder, or locks for shared counters depending on semantics.",
                "Do not use volatile as a substitute for compound atomic updates.",
                "Prefer immutable snapshots when readers need consistent multi-field state.",
            ),
            docs=(atomic_pkg, jls_memory_model(version), concurrent_pkg),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.lower().replace("_", "-").split())


def concern_index(version: str = DEFAULT_VERSION) -> dict[str, ConcurrencyConcern]:
    index: dict[str, ConcurrencyConcern] = {}
    for concern in concerns(version):
        index[normalize(concern.key)] = concern
        index[normalize(concern.title)] = concern
        for alias in concern.aliases:
            index[normalize(alias)] = concern
    return index


def find_concern(query: str, version: str = DEFAULT_VERSION) -> ConcurrencyConcern:
    normalized = normalize(query)
    index = concern_index(version)
    if normalized in index:
        return index[normalized]
    matches = [concern for key, concern in index.items() if normalized in key or key in normalized]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if unique_matches:
        options = ", ".join(concern.key for concern in unique_matches)
        raise ValueError(f"ambiguous concurrency concern {query!r}; choose one of: {options}")
    available = ", ".join(concern.key for concern in concerns(version))
    raise ValueError(f"unknown concurrency concern {query!r}; available concerns: {available}")


def official_urls(selected: Iterable[ConcurrencyConcern]) -> tuple[str, ...]:
    urls: list[str] = []
    for concern in selected:
        urls.extend(concern.docs)
    return tuple(dict.fromkeys(urls))


def render_text(concern: ConcurrencyConcern) -> str:
    lines = [concern.title, f"Key: {concern.key}", "", "First checks:"]
    lines.extend(f"{index}. {check}" for index, check in enumerate(concern.first_checks, start=1))
    lines.extend(["", "Evidence to collect:"])
    lines.extend(f"- {item}" for item in concern.evidence)
    lines.extend(["", "Safer defaults:"])
    lines.extend(f"- {item}" for item in concern.safer_defaults)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in concern.docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("concern", nargs="?", help="Concurrency concern key or alias")
    parser.add_argument("--list", action="store_true", help="List known concern keys")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        keys = [concern.key for concern in concerns(args.version)]
        print(json.dumps(keys, indent=2) if args.json else "\n".join(keys))
        return 0

    if not args.concern:
        parser.error("concern is required unless --list is used")

    try:
        concern = find_concern(args.concern, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(concern)
        payload["official_docs"] = list(concern.docs)
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(concern))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
