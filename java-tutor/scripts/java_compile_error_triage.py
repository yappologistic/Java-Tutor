#!/usr/bin/env python3
"""Triage common javac diagnostics with official documentation links."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class CompileErrorInfo:
    key: str
    patterns: tuple[str, ...]
    summary: str
    first_checks: tuple[str, ...]
    docs: tuple[str, ...]


def javac_doc(version: str) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/specs/man/javac.html"


def jls_doc(section: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/{section}"


def diagnostics(version: str = DEFAULT_VERSION) -> tuple[CompileErrorInfo, ...]:
    return (
        CompileErrorInfo(
            key="cannot-find-symbol",
            patterns=("cannot find symbol", "cannot resolve symbol", "symbol:"),
            summary="The compiler cannot resolve a name in the current scope, imports, class path, source path, or module graph.",
            first_checks=(
                "Check spelling, case, package declaration, imports, and whether the referenced type/member is visible.",
                "Check build configuration: class path, module path, source path, generated sources, annotation processing, and dependency scope.",
                "Check source/release level when the symbol is from a newer Java API or language feature.",
            ),
            docs=(javac_doc(version), jls_doc("jls-6.html", version), jls_doc("jls-7.html", version)),
        ),
        CompileErrorInfo(
            key="package-does-not-exist",
            patterns=("package .* does not exist", "package does not exist"),
            summary="An imported or referenced package is not visible to javac from the configured source, class, or module path.",
            first_checks=(
                "Confirm the dependency is declared in the active Maven/Gradle/source-set configuration.",
                "Confirm the package name and artifact match; package names are not the same as Maven coordinates or module names.",
                "For modular builds, check module declarations, module path, and required modules.",
            ),
            docs=(javac_doc(version), jls_doc("jls-7.html", version)),
        ),
        CompileErrorInfo(
            key="incompatible-types",
            patterns=("incompatible types", "bad type in conditional expression", "possible lossy conversion"),
            summary="An expression cannot be converted to the target type required by assignment, invocation, return, cast, or another context.",
            first_checks=(
                "Identify the required target type and the actual expression type from the full diagnostic.",
                "Check generic type arguments, wildcard capture, primitive boxing/unboxing, narrowing conversions, and overload selection.",
                "Avoid adding casts until the API contract and intended type are clear.",
            ),
            docs=(jls_doc("jls-5.html", version), jls_doc("jls-15.html", version)),
        ),
        CompileErrorInfo(
            key="method-not-applicable",
            patterns=("method .* cannot be applied", "no suitable method found", "no applicable method"),
            summary="No accessible overload matches the supplied receiver, argument count, argument types, type parameters, or invocation context.",
            first_checks=(
                "Compare each argument type to the candidate method signatures shown by javac.",
                "Check varargs, autoboxing, generic inference, lambdas/method references, and static versus instance invocation.",
                "Check whether a newer overload exists only in a later Java SE API or dependency version.",
            ),
            docs=(jls_doc("jls-15.html#jls-15.12", version), jls_doc("jls-18.html", version), javac_doc(version)),
        ),
        CompileErrorInfo(
            key="non-static-reference",
            patterns=("non-static .* cannot be referenced from a static context", "non-static variable .* static context"),
            summary="Code in a static context tried to use an instance member without an instance.",
            first_checks=(
                "Check whether the code should run on an existing object, a newly constructed object, or a static utility.",
                "Do not make state static just to silence the compiler; first confirm the ownership and lifetime of that state.",
                "Check nested classes, lambdas, and main methods where static context is common.",
            ),
            docs=(jls_doc("jls-8.html", version), jls_doc("jls-15.html", version)),
        ),
        CompileErrorInfo(
            key="definite-assignment",
            patterns=("variable .* might not have been initialized", "variable .* might already have been assigned"),
            summary="A local variable or blank final field is not definitely assigned, or is definitely assigned more than allowed.",
            first_checks=(
                "Check every branch, loop, catch/finally path, and early return before the variable is read.",
                "Initialize near declaration only when that value is semantically valid.",
                "For blank final fields, check every constructor path and constructor chaining.",
            ),
            docs=(jls_doc("jls-16.html", version), jls_doc("jls-4.html#jls-4.12.4", version)),
        ),
        CompileErrorInfo(
            key="public-class-file-name",
            patterns=("class .* is public, should be declared in a file named", "interface .* is public, should be declared in a file named"),
            summary="A public top-level type must be declared in the matching compilation unit file.",
            first_checks=(
                "Rename the file to match the public top-level type, or rename/remove public from the type when appropriate.",
                "Check package layout and generated-source configuration before moving files.",
                "Keep one public top-level type per ordinary source file unless the language feature in use explicitly allows otherwise.",
            ),
            docs=(jls_doc("jls-7.html#jls-7.6", version), javac_doc(version)),
        ),
        CompileErrorInfo(
            key="release-source-target",
            patterns=("release version .* not supported", "invalid source release", "source release .* requires target release", "target release"),
            summary="The configured javac source, target, or release option is incompatible with the JDK running the compiler or with each other.",
            first_checks=(
                "Run `javac --version` and check the build toolchain JDK, not only `java --version`.",
                "Prefer `--release` or the build tool's release option when compiling against a Java SE platform version.",
                "Align Maven/Gradle toolchains, CI images, IDE JDKs, and container JDKs.",
            ),
            docs=(javac_doc(version), "https://docs.oracle.com/en/java/javase/25/migrate/index.html"),
        ),
    )


def diagnostic_index(version: str = DEFAULT_VERSION) -> dict[str, CompileErrorInfo]:
    return {item.key: item for item in diagnostics(version)}


def detect(query: str, version: str = DEFAULT_VERSION) -> CompileErrorInfo:
    lowered = query.lower()
    for item in diagnostics(version):
        for pattern in item.patterns:
            if re.search(pattern, lowered):
                return item
    available = ", ".join(item.key for item in diagnostics(version))
    raise ValueError(f"unsupported javac diagnostic; available diagnostic keys: {available}")


def select(key: str, version: str = DEFAULT_VERSION) -> CompileErrorInfo:
    item = diagnostic_index(version).get(key)
    if not item:
        available = ", ".join(item.key for item in diagnostics(version))
        raise ValueError(f"unknown diagnostic key {key!r}; available diagnostic keys: {available}")
    return item


def official_urls(items: Iterable[CompileErrorInfo]) -> tuple[str, ...]:
    urls: list[str] = []
    for item in items:
        urls.extend(item.docs)
    return tuple(dict.fromkeys(urls))


def render_text(item: CompileErrorInfo) -> str:
    checks = "\n".join(f"{index}. {check}" for index, check in enumerate(item.first_checks, start=1))
    docs = "\n".join(f"- {url}" for url in item.docs)
    return f"{item.key}\n\n{item.summary}\n\nFirst checks:\n{checks}\n\nOfficial docs:\n{docs}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="javac diagnostic text, or a known diagnostic key with --key")
    parser.add_argument("--key", action="store_true", help="Treat query as a diagnostic key")
    parser.add_argument("--list", action="store_true", help="List supported diagnostic keys")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        payload = [item.key for item in diagnostics(args.version)]
        print(json.dumps(payload, indent=2) if args.json else "\n".join(payload))
        return 0

    if not args.query:
        parser.error("query is required unless --list is used")

    try:
        item = select(args.query, args.version) if args.key else detect(args.query, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(item)
        payload["official_docs"] = list(item.docs)
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(item))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
