#!/usr/bin/env python3
"""Triage Java subprocess, ProcessBuilder, environment, and stream issues."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class ProcessIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def issues(version: str = DEFAULT_VERSION) -> tuple[ProcessIssue, ...]:
    process_builder = api("java/lang/ProcessBuilder.html", version)
    process = api("java/lang/Process.html", version)
    process_handle = api("java/lang/ProcessHandle.html", version)
    runtime = api("java/lang/Runtime.html", version)
    input_stream = api("java/io/InputStream.html", version)
    output_stream = api("java/io/OutputStream.html", version)
    reader = api("java/io/Reader.html", version)
    standard_charsets = api("java/nio/charset/StandardCharsets.html", version)
    path = api("java/nio/file/Path.html", version)
    file = api("java/io/File.html", version)
    duration = api("java/time/Duration.html", version)
    time_unit = api("java/util/concurrent/TimeUnit.html", version)
    system = api("java/lang/System.html", version)
    security_manager = api("java/lang/SecurityManager.html", version)
    return (
        ProcessIssue(
            key="command-arguments",
            title="ProcessBuilder command lists, shell quoting, arguments, and portability",
            aliases=("processbuilder", "command", "arguments", "shell", "quote", "runtime exec"),
            first_checks=(
                "Capture the exact command list passed to ProcessBuilder, not only the displayed command string.",
                "Determine whether shell features such as pipes, redirects, globbing, or variables are required.",
                "Check operating system, executable lookup path, file extensions, and argument boundaries.",
            ),
            fixes_to_consider=(
                "Pass executable and arguments as separate list elements when shell parsing is not required.",
                "Invoke an explicit shell only when shell syntax is intentionally part of the contract.",
                "Use absolute executable paths or controlled PATH values for reproducible launches.",
            ),
            pitfalls=(
                "Putting a whole shell command in one ProcessBuilder argument and expecting Java to split it.",
                "Using platform-specific shell syntax without guarding Windows, Linux, and macOS differences.",
                "Logging a joined command string and mistaking it for the actual argument vector.",
            ),
            docs=(process_builder, runtime),
        ),
        ProcessIssue(
            key="working-directory",
            title="Working directory, relative paths, executable lookup, and filesystem context",
            aliases=("working directory", "cwd", "directory", "relative path", "executable not found"),
            first_checks=(
                "Inspect ProcessBuilder.directory, current Java process directory, and every relative path argument.",
                "Check whether the child process expects resources relative to its working directory.",
                "Confirm path syntax and case-sensitivity on the target operating system.",
            ),
            fixes_to_consider=(
                "Set ProcessBuilder.directory explicitly when child behavior depends on a working directory.",
                "Pass absolute paths for files whose location should not depend on launch context.",
                "Use Path APIs to build cross-platform paths before passing them to the child process.",
            ),
            pitfalls=(
                "Assuming a service, IDE, test runner, and terminal start with the same working directory.",
                "Relying on current directory for executable lookup instead of a known PATH or absolute path.",
                "Concatenating path strings with hard-coded separators.",
            ),
            docs=(process_builder, path, file),
        ),
        ProcessIssue(
            key="environment",
            title="Environment variables, inheritance, PATH, locale, and secret handling",
            aliases=("environment", "env", "path variable", "locale", "secret", "process environment"),
            first_checks=(
                "Inspect the environment map supplied to ProcessBuilder before the process starts.",
                "Check PATH, locale, proxy, credential, and tool-specific variables required by the child process.",
                "Identify secrets that must not be logged, inherited, or exposed through diagnostics.",
            ),
            fixes_to_consider=(
                "Set only the child environment variables that are part of the launch contract.",
                "Prefer explicit executable paths over relying on PATH where reproducibility matters.",
                "Redact environment-derived secrets in logs, errors, and test output.",
            ),
            pitfalls=(
                "Mutating the environment after start and expecting it to affect a running child process.",
                "Leaking parent process secrets into untrusted subprocesses.",
                "Assuming environment variable names and case behave identically across every OS.",
            ),
            docs=(process_builder, system),
        ),
        ProcessIssue(
            key="stdio-deadlock",
            title="stdout, stderr, stdin, pipe buffering, inheritIO, and process hangs",
            aliases=("stdout", "stderr", "stdin", "deadlock", "hang", "pipe", "inheritio"),
            first_checks=(
                "Check whether stdout and stderr are consumed concurrently before waiting for process exit.",
                "Identify whether the child expects stdin input or waits for EOF.",
                "Capture output size and whether redirectErrorStream, redirects, or inheritIO are configured.",
            ),
            fixes_to_consider=(
                "Drain stdout and stderr or redirect them before calling waitFor on verbose processes.",
                "Close the process output stream when no more stdin data will be sent.",
                "Use redirectErrorStream or separate consumers according to whether stderr must remain distinct.",
            ),
            pitfalls=(
                "Calling waitFor while the child blocks writing to a full pipe.",
                "Ignoring stderr and losing the real failure message.",
                "Leaving stdin open so the child waits forever for more input.",
            ),
            docs=(process, process_builder, input_stream, output_stream),
        ),
        ProcessIssue(
            key="exit-timeout",
            title="Exit codes, waitFor, timeout handling, interruption, and process cleanup",
            aliases=("exit code", "waitfor", "timeout", "destroy", "destroyforcibly", "interruptedexception"),
            first_checks=(
                "Capture exit code, timeout, cancellation path, and whether child descendants must also stop.",
                "Check how InterruptedException is handled while waiting for a child process.",
                "Inspect whether destroy or destroyForcibly is appropriate for the platform and child process.",
            ),
            fixes_to_consider=(
                "Use waitFor with a timeout when process duration must be bounded.",
                "Restore interrupt status or propagate interruption after cleanup decisions.",
                "Use ProcessHandle when descendant process tracking is required.",
            ),
            pitfalls=(
                "Treating every nonzero exit code as the same failure without preserving output and command context.",
                "Swallowing interruption and leaving calling code unable to cancel correctly.",
                "Assuming killing the parent process always kills every child it spawned.",
            ),
            docs=(process, process_handle, duration, time_unit),
        ),
        ProcessIssue(
            key="text-encoding",
            title="Process output text decoding, charsets, lines, and binary output",
            aliases=("encoding", "charset", "utf-8", "output text", "mojibake", "binary output"),
            first_checks=(
                "Identify whether process output is bytes, text, structured data, or mixed stdout/stderr diagnostics.",
                "Check the charset contract of the child process, locale, and platform default charset.",
                "Decide whether line-oriented reading is safe for the output format and size.",
            ),
            fixes_to_consider=(
                "Decode bytes with an explicit charset such as UTF-8 when the child process contract guarantees it.",
                "Keep binary output as bytes instead of routing it through Reader or String APIs.",
                "Stream large output rather than accumulating unbounded strings in memory.",
            ),
            pitfalls=(
                "Using the platform default charset for tool output that has a documented encoding.",
                "Treating binary output as text and corrupting it through character decoding.",
                "Blocking on line reads when the child does not emit line terminators.",
            ),
            docs=(input_stream, reader, standard_charsets),
        ),
        ProcessIssue(
            key="security-boundary",
            title="Subprocess security boundaries, untrusted input, injection, and least privilege",
            aliases=("security", "injection", "untrusted", "command injection", "least privilege"),
            first_checks=(
                "Identify every untrusted value that influences executable path, arguments, environment, or working directory.",
                "Check whether invoking a shell expands the attack surface through metacharacters and redirection.",
                "Inspect filesystem permissions, inherited credentials, environment secrets, and output disclosure paths.",
            ),
            fixes_to_consider=(
                "Avoid shell invocation for untrusted values; pass arguments as a structured command list.",
                "Allow-list executable names, modes, and file locations instead of validating arbitrary commands.",
                "Run subprocesses with the least privileges and environment needed for the task.",
            ),
            pitfalls=(
                "Assuming ProcessBuilder prevents command injection when an explicit shell is still invoked.",
                "Logging commands or environment variables that contain secrets.",
                "Executing attacker-controlled files from writable directories.",
            ),
            docs=(process_builder, runtime, security_manager),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, ProcessIssue]:
    index: dict[str, ProcessIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> ProcessIssue:
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
        raise ValueError(f"ambiguous process issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown process issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[ProcessIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: ProcessIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="Process issue key or alias")
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
