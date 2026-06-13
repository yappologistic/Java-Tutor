#!/usr/bin/env python3
"""Triage Java HTTP Client, URI, request/response, timeout, TLS, and WebSocket issues."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class HttpIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def http_api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.net.http/{path}"


def base_api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def issues(version: str = DEFAULT_VERSION) -> tuple[HttpIssue, ...]:
    http_client = http_api("java/net/http/HttpClient.html", version)
    http_request = http_api("java/net/http/HttpRequest.html", version)
    body_publishers = http_api("java/net/http/HttpRequest.BodyPublishers.html", version)
    http_response = http_api("java/net/http/HttpResponse.html", version)
    body_handlers = http_api("java/net/http/HttpResponse.BodyHandlers.html", version)
    body_subscribers = http_api("java/net/http/HttpResponse.BodySubscribers.html", version)
    web_socket = http_api("java/net/http/WebSocket.html", version)
    http_timeout = http_api("java/net/http/HttpTimeoutException.html", version)
    uri = base_api("java/net/URI.html", version)
    authenticator = base_api("java/net/Authenticator.html", version)
    proxy_selector = base_api("java/net/ProxySelector.html", version)
    ssl_context = base_api("javax/net/ssl/SSLContext.html", version)
    ssl_parameters = base_api("javax/net/ssl/SSLParameters.html", version)
    completable_future = base_api("java/util/concurrent/CompletableFuture.html", version)
    duration = base_api("java/time/Duration.html", version)
    executor = base_api("java/util/concurrent/Executor.html", version)
    charset = base_api("java/nio/charset/Charset.html", version)
    standard_charsets = base_api("java/nio/charset/StandardCharsets.html", version)
    input_stream = base_api("java/io/InputStream.html", version)
    return (
        HttpIssue(
            key="request-uri-headers",
            title="HttpRequest URI, method, headers, restricted headers, and request construction",
            aliases=("httprequest", "uri", "headers", "method", "restricted header", "request builder"),
            first_checks=(
                "Capture the exact URI, method, headers, body publisher, and Java version.",
                "Check URI encoding, scheme, host, path, query, and whether user input is inserted structurally.",
                "Verify whether the header is managed by the HTTP client or should be application-controlled.",
            ),
            fixes_to_consider=(
                "Build URI values with structured APIs before passing them to HttpRequest.",
                "Set only application-level headers and let the client manage protocol-level details.",
                "Create a new immutable HttpRequest for each distinct request contract.",
            ),
            pitfalls=(
                "String-concatenating query parameters without encoding boundaries.",
                "Expecting every wire header to be settable through the Java API.",
                "Reusing a request builder across unrelated requests and leaking headers or methods.",
            ),
            docs=(http_request, uri),
        ),
        HttpIssue(
            key="body-publishers",
            title="Request BodyPublishers, content length, streaming, repeatability, and charsets",
            aliases=("bodypublisher", "body publishers", "post body", "upload", "streaming upload", "charset"),
            first_checks=(
                "Identify body source, size, charset, content type, repeatability, and whether redirects/retries occur.",
                "Check whether the body publisher is one-shot, file-backed, byte-array backed, or streaming.",
                "Verify that text bodies use the charset promised by Content-Type.",
            ),
            fixes_to_consider=(
                "Use String, byte array, file, input stream, or custom publishers according to body lifetime and size.",
                "Set Content-Type explicitly when server parsing depends on media type and charset.",
                "Avoid buffering large uploads in memory unless bounded and intentional.",
            ),
            pitfalls=(
                "Treating a streaming body as reusable after redirect or retry behavior.",
                "Sending text with one charset while declaring another.",
                "Forgetting that chunking/content length behavior can matter to some servers.",
            ),
            docs=(body_publishers, http_request, charset, standard_charsets),
        ),
        HttpIssue(
            key="response-handlers",
            title="Response BodyHandlers, BodySubscribers, status codes, memory, and streaming",
            aliases=("bodyhandler", "body handlers", "response body", "status code", "download", "streaming response"),
            first_checks=(
                "Capture status code, headers, body handler, expected body size, and whether errors include bodies.",
                "Check whether the handler buffers all data, streams it, writes a file, or discards it.",
                "Decide whether non-2xx status codes should still read, log, or parse the response body.",
            ),
            fixes_to_consider=(
                "Choose BodyHandlers based on memory limits and ownership of the response body.",
                "Check statusCode before treating the body as successful application data.",
                "Stream large downloads to files or subscribers instead of accumulating strings.",
            ),
            pitfalls=(
                "Assuming send throws for HTTP 4xx or 5xx status codes.",
                "Reading large responses into memory through ofString or ofByteArray.",
                "Ignoring error response bodies that contain useful diagnostics.",
            ),
            docs=(http_response, body_handlers, body_subscribers),
        ),
        HttpIssue(
            key="async-futures",
            title="sendAsync, CompletableFuture, executor behavior, cancellation, and exception flow",
            aliases=("sendasync", "async", "completablefuture", "future", "executor", "cancel"),
            first_checks=(
                "Capture the future chain, executor configuration, cancellation path, and exception handling.",
                "Check whether blocking work runs inside completion stages and starves the executor.",
                "Inspect CompletionException causes rather than only top-level future failures.",
            ),
            fixes_to_consider=(
                "Compose asynchronous stages explicitly and unwrap causes for diagnostics.",
                "Use a suitable executor when default behavior does not fit workload isolation needs.",
                "Propagate cancellation and timeouts deliberately through dependent stages.",
            ),
            pitfalls=(
                "Calling join deep inside request code and accidentally making async code synchronous.",
                "Losing exceptions in unobserved CompletableFutures.",
                "Doing CPU-heavy or blocking work on an executor intended for HTTP progress.",
            ),
            docs=(http_client, completable_future, executor),
        ),
        HttpIssue(
            key="timeouts-redirects",
            title="Connect timeouts, request timeouts, redirects, retries, and interrupted waits",
            aliases=("timeout", "redirect", "retry", "connect timeout", "httptimeoutexception", "interrupted"),
            first_checks=(
                "Identify connect timeout, per-request timeout, redirect policy, retry policy, and observed phase.",
                "Capture whether the failure is DNS, TCP connect, TLS handshake, request body upload, or response wait.",
                "Check whether synchronous waits handle InterruptedException correctly.",
            ),
            fixes_to_consider=(
                "Set both client connect timeout and request timeout when service contracts require bounds.",
                "Choose redirect policy deliberately and preserve security expectations across redirects.",
                "Retry only idempotent or explicitly safe requests after classifying the failure.",
            ),
            pitfalls=(
                "Assuming one timeout covers DNS, connect, TLS, upload, and response body processing uniformly.",
                "Retrying POST requests with non-repeatable bodies or side effects.",
                "Following redirects that change authority or scheme without validating the trust boundary.",
            ),
            docs=(http_client, http_request, http_timeout, duration),
        ),
        HttpIssue(
            key="proxy-tls-auth",
            title="Proxy, TLS, SSLContext, SSLParameters, Authenticator, and certificate issues",
            aliases=("proxy", "tls", "ssl", "certificate", "authenticator", "mtls", "hostname verification"),
            first_checks=(
                "Capture proxy settings, TLS version, certificate chain, trust store, client certs, and target host.",
                "Check whether authentication is proxy auth, server auth, application auth, or mutual TLS.",
                "Inspect SSL handshake exceptions, hostname mismatch, and environment-specific trust configuration.",
            ),
            fixes_to_consider=(
                "Configure ProxySelector, Authenticator, SSLContext, and SSLParameters at the HttpClient boundary.",
                "Prefer trust store fixes over disabling certificate or hostname validation.",
                "Separate transport authentication from application Authorization headers.",
            ),
            pitfalls=(
                "Disabling TLS validation to work around a trust-store problem.",
                "Confusing proxy authentication with origin-server authentication.",
                "Assuming local developer trust stores match production containers.",
            ),
            docs=(http_client, proxy_selector, authenticator, ssl_context, ssl_parameters),
        ),
        HttpIssue(
            key="http2-version",
            title="HTTP protocol version, HTTP/2 negotiation, connection reuse, and flow control symptoms",
            aliases=("http2", "http/2", "version", "connection reuse", "flow control", "multiplexing"),
            first_checks=(
                "Capture requested client version, actual response version, TLS/ALPN setup, and server support.",
                "Check whether symptoms are protocol negotiation, stream reset, connection pooling, or body consumption.",
                "Inspect whether large or unconsumed bodies affect reuse and later requests.",
            ),
            fixes_to_consider=(
                "Set desired HttpClient version when protocol preference matters.",
                "Always consume or discard response bodies according to the chosen handler semantics.",
                "Use server/client diagnostics to distinguish application failures from protocol negotiation issues.",
            ),
            pitfalls=(
                "Assuming requesting HTTP/2 guarantees the final response uses HTTP/2.",
                "Leaving response bodies unconsumed and then blaming connection reuse.",
                "Treating multiplexed HTTP/2 behavior like one-socket-per-request HTTP/1.1 behavior.",
            ),
            docs=(http_client, http_response, input_stream),
        ),
        HttpIssue(
            key="websocket",
            title="HttpClient WebSocket, Listener backpressure, text/binary messages, and close handling",
            aliases=("websocket", "web socket", "listener", "backpressure", "ping", "close"),
            first_checks=(
                "Capture WebSocket URI, listener callbacks, requested demand, close status, and error callbacks.",
                "Check whether the listener requests more messages after processing callbacks.",
                "Identify text/binary message boundaries, partial messages, pings, pongs, and close frames.",
            ),
            fixes_to_consider=(
                "Use WebSocket.Listener demand methods deliberately to control message flow.",
                "Handle onError and onClose paths separately from normal message callbacks.",
                "Preserve text/binary boundaries and partial-message completion semantics.",
            ),
            pitfalls=(
                "Forgetting to request more messages and making the socket appear idle.",
                "Treating partial messages as complete application messages.",
                "Ignoring close codes and losing protocol-level diagnostics.",
            ),
            docs=(web_socket, http_client, uri),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, HttpIssue]:
    index: dict[str, HttpIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> HttpIssue:
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
        raise ValueError(f"ambiguous HTTP issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown HTTP issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[HttpIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: HttpIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="HTTP client issue key or alias")
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
