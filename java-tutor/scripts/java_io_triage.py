#!/usr/bin/env python3
"""Triage Java I/O, NIO, charset, serialization, and socket issues with official links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class IoIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def tutorial(path: str) -> str:
    return f"https://docs.oracle.com/javase/tutorial/{path}"


def jls(section: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/{section}"


def issues(version: str = DEFAULT_VERSION) -> tuple[IoIssue, ...]:
    path_api = api("java/nio/file/Path.html", version)
    files_api = api("java/nio/file/Files.html", version)
    charset_api = api("java/nio/charset/Charset.html", version)
    standard_charsets = api("java/nio/charset/StandardCharsets.html", version)
    input_stream = api("java/io/InputStream.html", version)
    output_stream = api("java/io/OutputStream.html", version)
    reader = api("java/io/Reader.html", version)
    writer = api("java/io/Writer.html", version)
    autocloseable = api("java/lang/AutoCloseable.html", version)
    object_input_stream = api("java/io/ObjectInputStream.html", version)
    serialization_filtering = f"https://docs.oracle.com/en/java/javase/{version}/core/serialization-filtering1.html"
    socket = api("java/net/Socket.html", version)
    server_socket = api("java/net/ServerSocket.html", version)
    uri = api("java/net/URI.html", version)
    url = api("java/net/URL.html", version)
    return (
        IoIssue(
            key="paths-files",
            title="Path, Files, directories, and filesystem boundaries",
            aliases=("path", "files", "filesystem", "file path", "directory", "relative path", "path traversal"),
            first_checks=(
                "Capture the working directory, input path string, resolved path, and target operating system.",
                "Check whether the code expects a file, directory, symlink, temporary file, or classpath resource.",
                "Resolve user-controlled paths against an intended base before reading or writing.",
            ),
            fixes_to_consider=(
                "Use Path and Files APIs instead of string concatenation for filesystem paths.",
                "Normalize and resolve paths before enforcing directory boundaries.",
                "Use temporary-file APIs for generated names instead of hand-rolled paths.",
            ),
            pitfalls=(
                "Assuming path separators, case sensitivity, or symlink behavior are the same on every OS.",
                "Checking a path before use without considering races or symlink changes.",
                "Treating classpath resources and filesystem files as interchangeable.",
            ),
            docs=(path_api, files_api, tutorial("essential/io/path.html")),
        ),
        IoIssue(
            key="charset-text",
            title="Text I/O, charsets, bytes, and line endings",
            aliases=("charset", "encoding", "utf-8", "text file", "line ending", "mojibake"),
            first_checks=(
                "Identify the actual byte encoding at the boundary and the charset used by the Java code.",
                "Check whether APIs use an explicit charset or the platform default.",
                "Confirm whether line endings, BOMs, normalization, or locale-sensitive text processing matter.",
            ),
            fixes_to_consider=(
                "Pass StandardCharsets.UTF_8 or the required protocol/file charset explicitly.",
                "Separate byte-oriented APIs from character-oriented Reader/Writer APIs.",
                "Normalize line handling only when the file or protocol contract requires it.",
            ),
            pitfalls=(
                "Relying on the default charset when moving between developer machines, containers, and production hosts.",
                "Counting characters when a byte length is required by a file format or network protocol.",
                "Using String conversions for binary data.",
            ),
            docs=(charset_api, standard_charsets, reader, writer),
        ),
        IoIssue(
            key="streams-buffers",
            title="InputStream, OutputStream, buffering, and partial reads/writes",
            aliases=("inputstream", "outputstream", "buffer", "partial read", "binary io", "flush"),
            first_checks=(
                "Identify whether the API reads bytes, characters, objects, or structured records.",
                "Check loops for partial reads, end-of-stream handling, buffering, flushing, and close behavior.",
                "Confirm whether the data size is bounded before reading it all into memory.",
            ),
            fixes_to_consider=(
                "Loop until the expected byte count or end-of-stream is reached.",
                "Use buffered streams for many small reads or writes.",
                "Stream large data instead of loading the entire content into memory.",
            ),
            pitfalls=(
                "Assuming one read fills the whole buffer.",
                "Forgetting to flush buffered output before another process or protocol peer expects data.",
                "Closing wrapper streams without understanding ownership of the underlying stream.",
            ),
            docs=(input_stream, output_stream, api("java/io/BufferedInputStream.html", version), api("java/io/BufferedOutputStream.html", version)),
        ),
        IoIssue(
            key="resource-lifecycle",
            title="Resource lifecycle, try-with-resources, and suppressed exceptions",
            aliases=("close", "resource leak", "try with resources", "autocloseable", "suppressed exception"),
            first_checks=(
                "Identify every object that owns files, sockets, channels, streams, readers, writers, or other native resources.",
                "Check whether resources close on success, failure, cancellation, and early returns.",
                "Inspect suppressed exceptions when cleanup fails under a primary exception.",
            ),
            fixes_to_consider=(
                "Use try-with-resources for AutoCloseable resources with clear ownership.",
                "Keep resource scopes narrow and avoid returning objects whose owner has already been closed.",
                "Log or propagate suppressed exceptions when they matter for debugging.",
            ),
            pitfalls=(
                "Leaking streams in exception paths.",
                "Closing a resource too early and returning a lazy stream or reader backed by it.",
                "Ignoring suppressed exceptions that explain cleanup failures.",
            ),
            docs=(autocloseable, jls("jls-14.html#jls-14.20.3", version), files_api),
        ),
        IoIssue(
            key="serialization",
            title="Java object serialization and filtering",
            aliases=("serialization", "objectinputstream", "deserialize", "readobject", "serialversionuid"),
            first_checks=(
                "Identify whether serialized input crosses a trust boundary.",
                "Check ObjectInputStream usage, custom readObject methods, serialVersionUID, and class compatibility.",
                "Verify whether serialization filters constrain classes, graph size, depth, references, and bytes.",
            ),
            fixes_to_consider=(
                "Avoid native Java serialization for untrusted data when possible.",
                "Use allow-list based serialization filters for any deserialization boundary.",
                "Prefer explicit data formats for long-term storage or cross-service contracts.",
            ),
            pitfalls=(
                "Treating deserialization as passive data parsing.",
                "Assuming serialVersionUID compatibility proves semantic compatibility.",
                "Forgetting that object graphs can be large or maliciously shaped.",
            ),
            docs=(object_input_stream, serialization_filtering, "https://www.oracle.com/java/technologies/javase/seccodeguide.html"),
        ),
        IoIssue(
            key="socket-io",
            title="Socket I/O, timeouts, blocking, and network resource handling",
            aliases=("socket", "network", "timeout", "blocking io", "server socket", "connect timeout"),
            first_checks=(
                "Capture endpoint, protocol, timeout settings, thread model, and whether the failure is connect, read, write, or close.",
                "Check whether blocking calls can wait forever and whether cancellation closes or interrupts the right resource.",
                "Confirm character encoding and framing for text protocols over sockets.",
            ),
            fixes_to_consider=(
                "Set explicit connect and read timeouts that match the service-level behavior.",
                "Close sockets on cancellation or shutdown to unblock waiting operations.",
                "Define message framing clearly instead of relying on ad hoc line or buffer behavior.",
            ),
            pitfalls=(
                "Assuming write success means the peer processed the data.",
                "Using platform default charsets for network protocols.",
                "Creating unbounded thread-per-connection behavior without resource limits.",
            ),
            docs=(socket, server_socket, input_stream, output_stream),
        ),
        IoIssue(
            key="uri-url",
            title="URI, URL, file paths, and resource identifiers",
            aliases=("uri", "url", "file url", "classpath resource", "spaces in path"),
            first_checks=(
                "Determine whether the value is a filesystem path, URI, URL, classpath resource name, or user-facing string.",
                "Check escaping, normalization, authority, scheme, and platform path conversion rules.",
                "Avoid converting between URI, URL, and Path unless the target abstraction really matches.",
            ),
            fixes_to_consider=(
                "Use URI for identifiers and Path for local filesystem paths.",
                "Use class loader resource APIs for classpath resources.",
                "Handle spaces and non-ASCII characters through structured APIs instead of string replacements.",
            ),
            pitfalls=(
                "Treating URL as a cheap string wrapper when it can involve protocol semantics.",
                "Building URIs with string concatenation instead of constructors/builders appropriate to the source.",
                "Assuming every URI can become a local Path.",
            ),
            docs=(uri, url, path_api),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, IoIssue]:
    index: dict[str, IoIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> IoIssue:
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
        raise ValueError(f"ambiguous I/O issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown I/O issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[IoIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: IoIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="I/O issue key or alias")
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
