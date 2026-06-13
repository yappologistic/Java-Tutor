#!/usr/bin/env python3
"""Triage common Java exceptions with official API documentation links."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class ExceptionInfo:
    name: str
    api_class: str
    summary: str
    first_checks: tuple[str, ...]


EXCEPTIONS: tuple[ExceptionInfo, ...] = (
    ExceptionInfo(
        name="NullPointerException",
        api_class="java.lang.NullPointerException",
        summary="Code tried to use `null` where an object reference was required.",
        first_checks=(
            "Find the exact expression on the throwing line, not just the line number.",
            "Check chained calls, autounboxing, array access, and values returned by maps or repositories.",
            "Prefer fixing the source of unexpected null; use guards or Optional only when absence is valid.",
        ),
    ),
    ExceptionInfo(
        name="IndexOutOfBoundsException",
        api_class="java.lang.IndexOutOfBoundsException",
        summary="An index was outside the valid range for a list, string, array-like object, or buffer.",
        first_checks=(
            "Compare the failing index to the collection/string size at the same moment.",
            "Check off-by-one loops using `<=` instead of `<`.",
            "Check whether filtering, concurrent mutation, or empty input changed the expected size.",
        ),
    ),
    ExceptionInfo(
        name="ClassCastException",
        api_class="java.lang.ClassCastException",
        summary="Code tried to cast an object to a type it is not an instance of.",
        first_checks=(
            "Log or inspect the runtime class of the value being cast.",
            "Remove raw types and unchecked casts; use generics at API boundaries.",
            "Check class-loader boundaries when the class names look identical.",
        ),
    ),
    ExceptionInfo(
        name="IllegalArgumentException",
        api_class="java.lang.IllegalArgumentException",
        summary="A method received an argument value it rejects.",
        first_checks=(
            "Read the throwing method's API contract for valid ranges, formats, and nullability.",
            "Validate caller input before the call when bad values are expected.",
            "Keep the exception if the caller violated a programming contract.",
        ),
    ),
    ExceptionInfo(
        name="IllegalStateException",
        api_class="java.lang.IllegalStateException",
        summary="A method was called when the receiver was not in the right state.",
        first_checks=(
            "Check lifecycle ordering: opened/closed, started/stopped, initialized/uninitialized.",
            "Look for reused streams, iterators, builders, or resources after terminal/close operations.",
            "Check concurrent access that can change state between validation and use.",
        ),
    ),
    ExceptionInfo(
        name="ConcurrentModificationException",
        api_class="java.util.ConcurrentModificationException",
        summary="A collection detected structural modification during iteration.",
        first_checks=(
            "Do not add/remove through the collection while iterating except through the iterator's own methods.",
            "Use `removeIf`, collect changes then apply them, or use a concurrent collection when appropriate.",
            "Do not rely on this exception for correctness; fail-fast behavior is best-effort.",
        ),
    ),
    ExceptionInfo(
        name="NoSuchElementException",
        api_class="java.util.NoSuchElementException",
        summary="Code requested an element that is not present.",
        first_checks=(
            "Check `Iterator.next()`, `Scanner.next*()`, or `Optional.get()` calls before availability is proven.",
            "Use `hasNext`, `findFirst().orElse...`, or `orElseThrow` with a domain-specific message.",
            "Check empty input and filtering predicates.",
        ),
    ),
    ExceptionInfo(
        name="NumberFormatException",
        api_class="java.lang.NumberFormatException",
        summary="Text could not be parsed as a numeric value.",
        first_checks=(
            "Inspect the exact input string, including whitespace, separators, locale-specific characters, and empty values.",
            "Use the parser that matches the expected numeric type and radix.",
            "Validate external input and report a useful domain error rather than leaking parser details.",
        ),
    ),
)


def api_link(api_class: str, version: str) -> str:
    module = "java.base"
    path = api_class.replace(".", "/")
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/{module}/{path}.html"


def exception_index() -> dict[str, ExceptionInfo]:
    index: dict[str, ExceptionInfo] = {}
    for item in EXCEPTIONS:
        index[item.name.lower()] = item
        index[item.api_class.lower()] = item
    return index


def extract_exception_name(text: str) -> str:
    match = re.search(r"((?:[a-zA-Z_$][\w$]*\.)*[A-Z][\w$]*(?:Exception|Error))", text)
    if not match:
        raise ValueError("could not find a Java exception class name")
    return match.group(1).split(".")[-1]


def triage(query: str) -> ExceptionInfo:
    name = extract_exception_name(query)
    index = exception_index()
    item = index.get(name.lower())
    if not item:
        available = ", ".join(item.name for item in EXCEPTIONS)
        raise ValueError(f"unsupported exception {name!r}; available exceptions: {available}")
    return item


def render_text(item: ExceptionInfo, version: str) -> str:
    checks = "\n".join(f"{index}. {check}" for index, check in enumerate(item.first_checks, start=1))
    return (
        f"{item.name}\n\n"
        f"{item.summary}\n\n"
        f"First checks:\n{checks}\n\n"
        f"Official docs:\n- {api_link(item.api_class, version)}"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Exception class name or stack trace text")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE API version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    try:
        item = triage(args.query)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(item)
        payload["official_docs"] = [api_link(item.api_class, args.version)]
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(item, args.version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
