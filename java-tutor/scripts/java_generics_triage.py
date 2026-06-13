#!/usr/bin/env python3
"""Triage Java generics, wildcards, erasure, and type-inference issues with official links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class GenericsIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def jls(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/{path}"


def api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def issues(version: str = DEFAULT_VERSION) -> tuple[GenericsIssue, ...]:
    collections_api = api("java/util/Collections.html", version)
    class_api = api("java/lang/Class.html", version)
    safe_varargs = api("java/lang/SafeVarargs.html", version)
    comparable = api("java/lang/Comparable.html", version)
    comparator = api("java/util/Comparator.html", version)
    list_api = api("java/util/List.html", version)
    collection_api = api("java/util/Collection.html", version)
    optional_api = api("java/util/Optional.html", version)
    return (
        GenericsIssue(
            key="invariance-wildcards",
            title="Generic type invariance, wildcard bounds, and PECS API design",
            aliases=("wildcard", "wildcards", "extends super", "pecs", "list subtype", "covariance"),
            first_checks=(
                "Identify the element type relationship separately from the generic container type relationship.",
                "Check whether the API only reads values, only writes values, or both reads and writes the same element type.",
                "Look for List<Subtype> being passed where List<Supertype> is required; generic types are invariant unless wildcard bounds are used.",
            ),
            fixes_to_consider=(
                "Use ? extends T when the caller provides a producer that the method only reads from.",
                "Use ? super T when the caller provides a consumer that the method writes T values into.",
                "Use an exact type parameter when the method must both read and write values with the same precise type relationship.",
            ),
            pitfalls=(
                "Adding ? extends T and then expecting to add arbitrary T values to that collection.",
                "Using raw types to bypass invariance instead of designing the API with bounded wildcards.",
                "Assuming arrays and generic collections follow the same variance and runtime-checking rules.",
            ),
            docs=(jls("jls-4.html#jls-4.5", version), jls("jls-4.html#jls-4.10.2", version), collection_api, list_api),
        ),
        GenericsIssue(
            key="type-inference",
            title="Generic method type inference, target typing, and overload interaction",
            aliases=("inference", "type inference", "cannot infer type", "diamond", "generic method", "target type"),
            first_checks=(
                "Identify explicit type arguments, target type, parameter types, argument expressions, lambdas, and method references.",
                "Check whether the inference context is assignment, invocation, or cast context.",
                "Inspect overload resolution and inference together; adding an overload can change which constraints are considered.",
            ),
            fixes_to_consider=(
                "Provide an explicit target type or explicit type witness only when it clarifies an otherwise under-constrained call.",
                "Split complex chained expressions so the compiler has an intermediate target type.",
                "Prefer clearer generic method signatures over forcing callers to use casts.",
            ),
            pitfalls=(
                "Expecting inference to use runtime values or later statements outside the expression context.",
                "Using null, empty collections, or lambdas in overloaded calls without enough type information.",
                "Fixing inference with unchecked casts that only move the failure to runtime.",
            ),
            docs=(jls("jls-18.html", version), jls("jls-15.html#jls-15.12.2", version), jls("jls-5.html", version)),
        ),
        GenericsIssue(
            key="erasure-reifiability",
            title="Type erasure, reifiable types, instanceof, class literals, and reflection limits",
            aliases=("erasure", "reifiable", "instanceof list string", "class literal", "generic reflection"),
            first_checks=(
                "Check whether the code expects parameterized type arguments to be available at runtime.",
                "Identify class literals, instanceof tests, casts, reflective Class objects, and generic signature metadata separately.",
                "Look for logic that uses Class<T> safely versus logic that tries to inspect erased type arguments.",
            ),
            fixes_to_consider=(
                "Pass an explicit Class<T>, type token, parser, or factory when runtime type information is required.",
                "Use instanceof with a reifiable type, then validate contained elements separately when necessary.",
                "Treat reflection generic metadata as declaration metadata, not proof that runtime values have already been validated.",
            ),
            pitfalls=(
                "Writing instanceof List<String>, which is not valid because List<String> is non-reifiable.",
                "Assuming List<String>.class exists; class literals require reifiable types.",
                "Treating a successful raw cast as evidence that every element has the desired generic type.",
            ),
            docs=(jls("jls-4.html#jls-4.6", version), jls("jls-4.html#jls-4.7", version), jls("jls-15.html#jls-15.20.2", version), class_api),
        ),
        GenericsIssue(
            key="raw-unchecked",
            title="Raw types, unchecked conversions, and heap pollution",
            aliases=("raw type", "unchecked", "unchecked cast", "heap pollution", "rawtypes", "classcastexception later"),
            first_checks=(
                "Find the first raw type, unchecked assignment, unchecked method invocation, or unchecked cast in the data path.",
                "Check whether a warning was introduced at a legacy boundary, reflection boundary, varargs boundary, or collection mutation.",
                "Trace where the polluted value is later read with an implicit compiler-inserted cast.",
            ),
            fixes_to_consider=(
                "Parameterize raw declarations and APIs where source compatibility permits it.",
                "Isolate unavoidable unchecked casts at a narrow boundary and validate inputs before suppressing warnings.",
                "Use @SuppressWarnings(\"unchecked\") only on the smallest declaration that contains a justified unchecked operation.",
            ),
            pitfalls=(
                "Suppressing unchecked warnings broadly and losing the location of the real type-safety break.",
                "Mixing raw and parameterized views of the same mutable collection.",
                "Assuming an unchecked cast checks all future elements; it normally checks only the erased runtime type.",
            ),
            docs=(jls("jls-4.html#jls-4.8", version), jls("jls-5.html#jls-5.1.9", version), jls("jls-4.html#jls-4.12.2", version)),
        ),
        GenericsIssue(
            key="generic-arrays-varargs",
            title="Generic arrays, non-reifiable varargs, and @SafeVarargs",
            aliases=("generic array", "varargs", "safevarargs", "possible heap pollution", "cannot create generic array"),
            first_checks=(
                "Identify whether the element type is reifiable and whether an array creation, varargs parameter, or array store is involved.",
                "Check whether the varargs method writes to the varargs array or exposes it to untrusted code.",
                "Confirm whether @SafeVarargs is legal for the method and whether the method body is actually safe.",
            ),
            fixes_to_consider=(
                "Prefer collections or caller-provided array factories when the element type is non-reifiable.",
                "Use @SafeVarargs only for final, static, private, or otherwise eligible methods that do not perform unsafe operations.",
                "Avoid writing into or leaking the varargs array for generic varargs methods.",
            ),
            pitfalls=(
                "Creating new T[] directly; type variables are generally non-reifiable.",
                "Annotating a method with @SafeVarargs without auditing the method body.",
                "Allowing array covariance and erased generic element types to combine into delayed ClassCastException failures.",
            ),
            docs=(jls("jls-10.html#jls-10.5", version), jls("jls-15.html#jls-15.10", version), jls("jls-8.html#jls-8.4.1", version), safe_varargs),
        ),
        GenericsIssue(
            key="bounds-intersections",
            title="Type parameter bounds, recursive bounds, and intersection types",
            aliases=("bounds", "bounded type", "intersection type", "recursive bound", "comparable t"),
            first_checks=(
                "List every declared type parameter, its upper bounds, and where each bound is required by the implementation.",
                "Check bound order: at most one class bound appears first, followed by interface bounds.",
                "For recursive bounds such as T extends Comparable<T>, verify the intended self-type relationship and caller ergonomics.",
            ),
            fixes_to_consider=(
                "Use bounds only for operations the generic implementation actually performs.",
                "Use intersection bounds when the implementation requires multiple capabilities from the same value.",
                "Prefer Comparator parameters when natural ordering bounds make the API too restrictive.",
            ),
            pitfalls=(
                "Adding overly strong bounds that reject valid caller types.",
                "Using raw Comparable instead of Comparable<? super T> or a Comparator when sorting values.",
                "Confusing type parameter bounds with runtime checks; bounds constrain compile-time type checking.",
            ),
            docs=(jls("jls-4.html#jls-4.4", version), jls("jls-4.html#jls-4.9", version), comparable, comparator),
        ),
        GenericsIssue(
            key="bridge-erasure-clash",
            title="Bridge methods, erasure clashes, overriding, and stack-trace surprises",
            aliases=("bridge method", "name clash", "same erasure", "erasure clash", "override generic", "synthetic bridge"),
            first_checks=(
                "Compare source signatures and erased signatures for overridden, overloaded, and inherited methods.",
                "Check whether covariant returns or generic specialization require a compiler-generated bridge method.",
                "Inspect stack traces or reflection output for synthetic bridge methods before assuming duplicate source methods exist.",
            ),
            fixes_to_consider=(
                "Rename or redesign overloads whose erased signatures collide.",
                "Keep overriding signatures source-compatible with the generic supertype contract.",
                "When using reflection, filter or handle synthetic and bridge methods deliberately.",
            ),
            pitfalls=(
                "Declaring overloads that differ only in type arguments and erase to the same signature.",
                "Mistaking bridge methods for hand-written methods during debugging or instrumentation.",
                "Breaking binary compatibility by changing erased method signatures in public APIs.",
            ),
            docs=(jls("jls-4.html#jls-4.6", version), jls("jls-8.html#jls-8.4.8.3", version), jls("jls-13.html", version)),
        ),
        GenericsIssue(
            key="api-design",
            title="Generic API design, type parameters versus wildcards, and fluent APIs",
            aliases=("generic api", "api design", "fluent generic", "self type", "bounded wildcard api"),
            first_checks=(
                "Decide whether the type relationship belongs on the method, the class, or the call-site wildcard.",
                "Check whether callers need inference-friendly APIs, fluent chaining, subclass return types, or heterogeneous values.",
                "Identify where the API should expose variance and where implementation details should remain exact.",
            ),
            fixes_to_consider=(
                "Use method type parameters for relationships among arguments and return values in a single call.",
                "Use class type parameters when the object carries the type relationship across multiple operations.",
                "Use wildcards at API boundaries and capture helper methods internally when that keeps caller code simple.",
            ),
            pitfalls=(
                "Adding unused type parameters that make signatures look more flexible without improving type safety.",
                "Returning overly specific implementation types instead of stable generic interfaces.",
                "Using Optional, collections, or fluent builders with generic signatures that make simple calls require explicit casts.",
            ),
            docs=(jls("jls-8.html#jls-8.1.2", version), jls("jls-8.html#jls-8.4.4", version), collections_api, optional_api),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, GenericsIssue]:
    index: dict[str, GenericsIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> GenericsIssue:
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
        raise ValueError(f"ambiguous generics issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown generics issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[GenericsIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: GenericsIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="Generics issue key or alias")
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
