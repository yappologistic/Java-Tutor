#!/usr/bin/env python3
"""Triage common Java security risk areas with official documentation links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"
SECURE_CODING = "https://www.oracle.com/java/technologies/javase/seccodeguide.html"


@dataclass(frozen=True)
class SecurityRisk:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    safer_defaults: tuple[str, ...]
    docs: tuple[str, ...]


def doc(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/{path}"


def risks(version: str = DEFAULT_VERSION) -> tuple[SecurityRisk, ...]:
    security_guide = doc("security/index.html", version)
    security_overview = doc("security/java-security-overview1.html", version)
    serialization_filtering = doc("core/serialization-filtering1.html", version)
    xml_constants = doc("docs/api/java.xml/javax/xml/XMLConstants.html", version)
    secure_random = doc("docs/api/java.base/java/security/SecureRandom.html", version)
    path_api = doc("docs/api/java.base/java/nio/file/Path.html", version)
    return (
        SecurityRisk(
            key="deserialization",
            title="Deserialization of untrusted data",
            aliases=("serialization", "deserialize", "objectinputstream", "readobject"),
            first_checks=(
                "Identify whether the input crosses a trust boundary before any object is instantiated.",
                "Look for ObjectInputStream, custom readObject methods, third-party serializers, and polymorphic type handling.",
                "Check whether serialization filters are configured and whether allowed classes are as narrow as possible.",
            ),
            safer_defaults=(
                "Avoid native Java deserialization for untrusted data when a simpler data format fits.",
                "Use allow-list based filtering and reject unexpected graph size, depth, references, and classes.",
                "Treat deserialization as code execution adjacent when reviewing exposed endpoints.",
            ),
            docs=(SECURE_CODING, serialization_filtering, security_guide),
        ),
        SecurityRisk(
            key="xml-parsing",
            title="XML parsing and entity expansion",
            aliases=("xml", "xxe", "entity expansion", "billion laughs", "xpath"),
            first_checks=(
                "Find XML parsers, transformers, validators, XPath, and SOAP/XML libraries that parse untrusted input.",
                "Check whether external entities, external schemas/stylesheets, and excessive expansion are disabled or bounded.",
                "Check whether FEATURE_SECURE_PROCESSING and parser-specific limits are set for the actual parser in use.",
            ),
            safer_defaults=(
                "Disable external entity resolution unless it is explicitly required and constrained.",
                "Set processing limits for size, depth, expansion, and time-consuming expressions.",
                "Validate input format and reject unexpected document structures early.",
            ),
            docs=(SECURE_CODING, xml_constants, security_guide),
        ),
        SecurityRisk(
            key="path-traversal",
            title="Path traversal and filesystem access",
            aliases=("path", "file", "directory traversal", "zip slip", "filesystem"),
            first_checks=(
                "Identify user-controlled path segments, archive entries, upload names, and temporary file names.",
                "Normalize and resolve paths against an intended base directory before access.",
                "Check symlink, race, archive extraction, overwrite, and permission boundary behavior.",
            ),
            safer_defaults=(
                "Do not concatenate filesystem paths with raw user input.",
                "Compare resolved paths to an allowed base directory before reading or writing.",
                "Generate server-side file names for uploads and temporary files.",
            ),
            docs=(SECURE_CODING, path_api, security_guide),
        ),
        SecurityRisk(
            key="secrets-logging",
            title="Secrets, logs, and diagnostic disclosure",
            aliases=("secret", "secrets", "logging", "logs", "password", "token"),
            first_checks=(
                "Search logs, exception messages, metrics, traces, and audit events for credentials or sensitive personal data.",
                "Check whether stack traces, SQL, request bodies, headers, environment variables, and system properties can leak.",
                "Confirm how production logs are retained, indexed, exported, and access-controlled.",
            ),
            safer_defaults=(
                "Redact secrets at the boundary and avoid passing raw credentials to generic logging helpers.",
                "Use structured error codes for users and keep sensitive diagnostic details in restricted channels.",
                "Treat heap dumps, thread dumps, and JFR recordings as potentially sensitive artifacts.",
            ),
            docs=(SECURE_CODING, security_overview, security_guide),
        ),
        SecurityRisk(
            key="crypto-random",
            title="Cryptography, randomness, and TLS assumptions",
            aliases=("crypto", "cryptography", "random", "securerandom", "tls", "ssl"),
            first_checks=(
                "Identify custom crypto, random token generation, password handling, TLS configuration, and provider assumptions.",
                "Check whether algorithms, key sizes, modes, padding, and protocols are current for the deployed JDK.",
                "Confirm secrets are generated with SecureRandom or a vetted high-level API, not Random or predictable seeds.",
            ),
            safer_defaults=(
                "Prefer high-level, reviewed libraries and platform TLS defaults unless there is a documented reason not to.",
                "Do not invent encryption formats, password hashing, or token schemes.",
                "Verify disabled algorithms and provider configuration on the target runtime.",
            ),
            docs=(security_guide, security_overview, secure_random, SECURE_CODING),
        ),
        SecurityRisk(
            key="resource-exhaustion",
            title="Resource exhaustion and denial of service",
            aliases=("dos", "denial of service", "resource", "regex", "zip bomb", "memory exhaustion"),
            first_checks=(
                "Identify untrusted inputs that control allocation sizes, recursion, archive expansion, regexes, images, XML, or loop bounds.",
                "Check whether expensive parsing, logging, decompression, and buffering have explicit limits.",
                "Check whether failures release files, sockets, locks, memory, and executor resources promptly.",
            ),
            safer_defaults=(
                "Set input size, decompressed size, time, depth, and count limits close to the boundary.",
                "Reject work that exceeds policy instead of relying on OutOfMemoryError or timeouts.",
                "Use try-with-resources and cancellation-aware code for expensive operations.",
            ),
            docs=(SECURE_CODING, security_guide, doc("docs/api/java.base/java/lang/AutoCloseable.html", version)),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.lower().replace("_", "-").split())


def risk_index(version: str = DEFAULT_VERSION) -> dict[str, SecurityRisk]:
    index: dict[str, SecurityRisk] = {}
    for risk in risks(version):
        index[normalize(risk.key)] = risk
        index[normalize(risk.title)] = risk
        for alias in risk.aliases:
            index[normalize(alias)] = risk
    return index


def find_risk(query: str, version: str = DEFAULT_VERSION) -> SecurityRisk:
    normalized = normalize(query)
    index = risk_index(version)
    if normalized in index:
        return index[normalized]
    matches = [risk for key, risk in index.items() if normalized in key or key in normalized]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if unique_matches:
        options = ", ".join(risk.key for risk in unique_matches)
        raise ValueError(f"ambiguous security risk {query!r}; choose one of: {options}")
    available = ", ".join(risk.key for risk in risks(version))
    raise ValueError(f"unknown security risk {query!r}; available risks: {available}")


def official_urls(selected: Iterable[SecurityRisk]) -> tuple[str, ...]:
    urls: list[str] = []
    for risk in selected:
        urls.extend(risk.docs)
    return tuple(dict.fromkeys(urls))


def render_text(risk: SecurityRisk) -> str:
    lines = [risk.title, f"Key: {risk.key}", "", "First checks:"]
    lines.extend(f"{index}. {check}" for index, check in enumerate(risk.first_checks, start=1))
    lines.extend(["", "Safer defaults:"])
    lines.extend(f"- {item}" for item in risk.safer_defaults)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in risk.docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("risk", nargs="?", help="Risk key or alias")
    parser.add_argument("--list", action="store_true", help="List known risk keys")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        keys = [risk.key for risk in risks(args.version)]
        print(json.dumps(keys, indent=2) if args.json else "\n".join(keys))
        return 0

    if not args.risk:
        parser.error("risk is required unless --list is used")

    try:
        risk = find_risk(args.risk, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(risk)
        payload["official_docs"] = list(risk.docs)
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(risk))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
