#!/usr/bin/env python3
"""Triage Java numeric precision, rounding, parsing, overflow, and equality issues."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class NumericIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def jls(chapter: str, anchor: str | None = None, version: str = DEFAULT_VERSION) -> str:
    suffix = f"#{anchor}" if anchor else ""
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/jls-{chapter}.html{suffix}"


def issues(version: str = DEFAULT_VERSION) -> tuple[NumericIssue, ...]:
    big_decimal = api("java/math/BigDecimal.html", version)
    big_integer = api("java/math/BigInteger.html", version)
    rounding_mode = api("java/math/RoundingMode.html", version)
    math_api = api("java/lang/Math.html", version)
    strict_math = api("java/lang/StrictMath.html", version)
    double_api = api("java/lang/Double.html", version)
    float_api = api("java/lang/Float.html", version)
    integer_api = api("java/lang/Integer.html", version)
    long_api = api("java/lang/Long.html", version)
    arithmetic_exception = api("java/lang/ArithmeticException.html", version)
    number_format_exception = api("java/lang/NumberFormatException.html", version)
    number_format = api("java/text/NumberFormat.html", version)
    decimal_format = api("java/text/DecimalFormat.html", version)
    locale = api("java/util/Locale.html", version)
    return (
        NumericIssue(
            key="floating-point",
            title="Floating-point precision, NaN, infinity, and binary decimal surprises",
            aliases=("double", "float", "precision", "nan", "infinity", "rounding error", "0.1"),
            first_checks=(
                "Identify whether the value is approximate measurement data or exact decimal/business data.",
                "Check for NaN, infinity, signed zero, and accumulated error across repeated operations.",
                "Capture expected tolerance, units, and whether comparisons use exact equality.",
            ),
            fixes_to_consider=(
                "Use double or float for approximate scientific or measurement values with explicit tolerances.",
                "Use BigDecimal for exact decimal quantities where the business contract requires it.",
                "Use Double.compare or domain tolerances instead of direct equality for approximate values.",
            ),
            pitfalls=(
                "Expecting binary floating point to represent decimal fractions exactly.",
                "Sorting or comparing values without deciding how NaN and signed zero should behave.",
                "Switching to BigDecimal without defining scale and rounding rules.",
            ),
            docs=(jls("4", "jls-4.2.3", version), double_api, float_api, math_api),
        ),
        NumericIssue(
            key="bigdecimal-money",
            title="BigDecimal scale, rounding, constructors, and money-style decimal values",
            aliases=("bigdecimal", "money", "currency", "scale", "setscale", "roundingmode"),
            first_checks=(
                "Identify required scale, rounding mode, currency/minor units, and serialization format.",
                "Check whether BigDecimal values are built from strings, integers, or binary floating-point values.",
                "Look for equals/compareTo mismatches caused by scale differences.",
            ),
            fixes_to_consider=(
                "Create BigDecimal from String or integer minor units when exact decimal input matters.",
                "Pass an explicit RoundingMode when division or scale changes can be inexact.",
                "Use compareTo for numeric equality when scale differences should not matter.",
            ),
            pitfalls=(
                "Calling new BigDecimal(double) for exact decimal input.",
                "Using equals when 1.0 and 1.00 should be treated as the same numeric value.",
                "Calling divide without a rounding mode for a non-terminating decimal expansion.",
            ),
            docs=(big_decimal, rounding_mode, arithmetic_exception),
        ),
        NumericIssue(
            key="overflow",
            title="Integer overflow, narrowing conversion, exact arithmetic, and BigInteger",
            aliases=("overflow", "underflow", "int overflow", "long overflow", "narrowing", "addexact"),
            first_checks=(
                "Identify operand types before promotion, conversion, multiplication, shifts, and assignment.",
                "Check whether overflow should wrap, throw, saturate, clamp, or use arbitrary precision.",
                "Look for intermediate overflow before a result is assigned to a wider type.",
            ),
            fixes_to_consider=(
                "Use Math.addExact, subtractExact, multiplyExact, or toIntExact when overflow should fail fast.",
                "Promote operands before arithmetic when a wider primitive result is required.",
                "Use BigInteger when values can exceed primitive ranges by design.",
            ),
            pitfalls=(
                "Assuming int arithmetic widens because the final variable is long.",
                "Forgetting that primitive integer overflow wraps without throwing.",
                "Missing narrowing conversions hidden in casts, compound assignments, or APIs.",
            ),
            docs=(jls("5", version=version), jls("15", "jls-15.17", version), math_api, big_integer),
        ),
        NumericIssue(
            key="division-rounding",
            title="Integer division, BigDecimal division, divide-by-zero, and rounding rules",
            aliases=("division", "integer division", "divide", "rounding", "round", "divide by zero"),
            first_checks=(
                "Identify operand types and whether the operation is integer, floating-point, or BigDecimal division.",
                "Check zero divisors, non-terminating decimal expansions, and required rounding policy.",
                "Verify whether truncation toward zero is intended for negative integer division.",
            ),
            fixes_to_consider=(
                "Cast or promote before division when a fractional primitive result is required.",
                "Pass scale and RoundingMode for BigDecimal division that may be inexact.",
                "Validate divisors and define behavior for zero explicitly.",
            ),
            pitfalls=(
                "Expecting int divided by int to produce a fractional result.",
                "Assuming BigDecimal.divide always succeeds without scale or rounding mode.",
                "Forgetting negative integer division truncates toward zero.",
            ),
            docs=(jls("15", "jls-15.17.2", version), big_decimal, rounding_mode, arithmetic_exception),
        ),
        NumericIssue(
            key="parse-format",
            title="Numeric parsing, NumberFormatException, locale, and decimal formatting",
            aliases=("parseint", "parselong", "numberformatexception", "numberformat", "decimalformat", "locale"),
            first_checks=(
                "Capture the exact input string, expected locale, radix, grouping separator, and decimal separator.",
                "Check whether the input is machine-formatted, user-facing localized text, or protocol data.",
                "Identify whether errors should reject input, default a value, or report validation details.",
            ),
            fixes_to_consider=(
                "Use Integer/Long parse methods for strict machine strings with explicit radix when needed.",
                "Use NumberFormat or DecimalFormat with an explicit Locale for localized user input/output.",
                "Keep presentation formatting separate from storage and protocol formats.",
            ),
            pitfalls=(
                "Parsing localized user text with non-localized parseInt or parseLong.",
                "Letting the default locale change numeric formatting across environments.",
                "Silently swallowing NumberFormatException and continuing with an unsafe default.",
            ),
            docs=(integer_api, long_api, number_format_exception, number_format, decimal_format, locale),
        ),
        NumericIssue(
            key="comparison-equality",
            title="Numeric equality, ordering, tolerance, BigDecimal scale, and NaN handling",
            aliases=("compare", "equals", "tolerance", "epsilon", "bigdecimal equals", "nan compare"),
            first_checks=(
                "Identify the numeric type and whether equality means exact representation or domain equivalence.",
                "Check whether tolerance comparisons are absolute, relative, unit-based, or business-rule based.",
                "Look for mixed numeric types in maps, sets, sorting, serialization, and tests.",
            ),
            fixes_to_consider=(
                "Use domain tolerances for approximate floating-point comparisons.",
                "Use BigDecimal.compareTo when numeric value equality should ignore scale.",
                "Use Double.compare or Float.compare for total ordering semantics required by sorting APIs.",
            ),
            pitfalls=(
                "Using one universal epsilon for values with very different magnitudes.",
                "Using BigDecimal.equals when scale-insensitive numeric comparison is required.",
                "Ignoring NaN and signed zero when defining ordering or equality for floating-point values.",
            ),
            docs=(double_api, float_api, big_decimal, jls("15", "jls-15.21.1", version)),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, NumericIssue]:
    index: dict[str, NumericIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> NumericIssue:
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
        raise ValueError(f"ambiguous numeric issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown numeric issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[NumericIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: NumericIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="Numeric issue key or alias")
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
