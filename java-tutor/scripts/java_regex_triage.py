#!/usr/bin/env python3
"""Triage Java regular-expression issues with official Pattern and Matcher links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class RegexIssue:
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


def issues(version: str = DEFAULT_VERSION) -> tuple[RegexIssue, ...]:
    pattern = api("java/util/regex/Pattern.html", version)
    matcher = api("java/util/regex/Matcher.html", version)
    pattern_syntax = api("java/util/regex/Pattern.html#sum", version)
    pattern_syntax_exception = api("java/util/regex/PatternSyntaxException.html", version)
    string_api = api("java/lang/String.html", version)
    return (
        RegexIssue(
            key="java-string-escaping",
            title="Java string literal escaping versus regex escaping",
            aliases=("escape", "escaping", "backslash", "string literal", "double escape", "\\d"),
            first_checks=(
                "Identify whether the pattern is written as a Java source string, text block, external config, or user input.",
                "Separate Java literal escaping from regex metacharacter escaping before changing the pattern.",
                "Print or inspect the runtime pattern string when the source literal is hard to reason about.",
            ),
            fixes_to_consider=(
                "Double Java string backslashes for regex escapes in source strings, such as \"\\\\d\" for a digit class.",
                "Use Pattern.quote when user text should be treated literally.",
                "Use text blocks carefully; they reduce some Java escaping but do not remove regex escaping rules.",
            ),
            pitfalls=(
                "Fixing only the regex layer when the Java string literal is the actual source of the bug.",
                "Quoting a whole pattern when only one literal fragment should be quoted.",
                "Forgetting replacement strings have their own escape rules.",
            ),
            docs=(pattern, pattern_syntax, string_api),
        ),
        RegexIssue(
            key="matches-vs-find",
            title="Matcher.matches(), find(), lookingAt(), and String regex methods",
            aliases=("matches", "find", "lookingat", "string matches", "contains regex"),
            first_checks=(
                "Determine whether the expected behavior is full-string match, prefix match, or substring search.",
                "Check whether String.matches is recompiling the pattern in a loop.",
                "Inspect anchors such as ^, $, \\A, and \\z before changing matching APIs.",
            ),
            fixes_to_consider=(
                "Use matches for full-region matches and find for repeated or substring matches.",
                "Compile a reusable Pattern when the same regex runs many times.",
                "Use explicit anchors when full-input or line-boundary behavior must be visible in the pattern.",
            ),
            pitfalls=(
                "Expecting String.matches to behave like a contains check.",
                "Adding .* around a pattern instead of using find when substring search is intended.",
                "Ignoring matcher region or anchoring settings when reusing a Matcher.",
            ),
            docs=(matcher, pattern, string_api),
        ),
        RegexIssue(
            key="groups-captures",
            title="Capturing groups, named groups, backreferences, and group extraction",
            aliases=("group", "groups", "capture", "capturing", "named group", "backreference"),
            first_checks=(
                "Check whether the match actually succeeded before reading groups.",
                "List expected group numbers or names and compare them with every capturing parenthesis.",
                "Decide whether parentheses should capture, not capture, or only group alternation/quantifiers.",
            ),
            fixes_to_consider=(
                "Use non-capturing groups for structure that should not shift group numbers.",
                "Use named capturing groups when extraction code is hard to maintain by index.",
                "Handle optional groups that may return null after a successful match.",
            ),
            pitfalls=(
                "Reading groups before find or matches succeeds.",
                "Breaking extraction code by inserting a new capturing group near the front of the pattern.",
                "Confusing replacement backreferences with pattern backreferences.",
            ),
            docs=(matcher, pattern),
        ),
        RegexIssue(
            key="flags-unicode-lines",
            title="Regex flags, Unicode character classes, case handling, and line boundaries",
            aliases=("flags", "unicode", "case insensitive", "multiline", "dotall", "line boundary"),
            first_checks=(
                "Identify required case, locale-independent, Unicode, line-boundary, and dot-newline behavior.",
                "Check whether flags are passed to Pattern.compile or embedded in the pattern.",
                "Test inputs with non-ASCII letters, combining characters, and multiple lines when relevant.",
            ),
            fixes_to_consider=(
                "Use Pattern flags explicitly when behavior should not be hidden in a complex pattern.",
                "Enable Unicode-aware behavior only when it matches the data contract and performance needs.",
                "Distinguish MULTILINE anchor behavior from DOTALL dot behavior.",
            ),
            pitfalls=(
                "Assuming CASE_INSENSITIVE alone is always enough for Unicode text.",
                "Confusing MULTILINE with matching across newline characters.",
                "Using \\w, \\d, or \\b without checking the intended character-class semantics.",
            ),
            docs=(pattern, pattern_syntax),
        ),
        RegexIssue(
            key="replacement-quoting",
            title="Replacement strings, quoteReplacement, appendReplacement, and replaceAll",
            aliases=("replaceall", "replacement", "quote replacement", "dollar", "appendreplacement"),
            first_checks=(
                "Determine whether the replacement is a literal string or uses captured groups.",
                "Check for dollar signs and backslashes in replacement text supplied by users or config.",
                "Identify whether replacement happens once, globally, or through appendReplacement logic.",
            ),
            fixes_to_consider=(
                "Use Matcher.quoteReplacement for literal replacement text.",
                "Use replaceFirst or replaceAll according to the required replacement count.",
                "Use appendReplacement and appendTail when replacement needs per-match logic.",
            ),
            pitfalls=(
                "Quoting the regex pattern but forgetting to quote literal replacement text.",
                "Treating $ and backslash the same in patterns and replacement strings.",
                "Using String.replaceAll when String.replace would express a literal replacement.",
            ),
            docs=(matcher, string_api, pattern),
        ),
        RegexIssue(
            key="performance-backtracking",
            title="Regex performance, catastrophic backtracking, compilation, and input limits",
            aliases=("performance", "backtracking", "catastrophic", "regex slow", "redos", "compile pattern"),
            first_checks=(
                "Capture the pattern, input size, representative worst-case input, and time limit.",
                "Look for nested quantifiers, ambiguous alternation, and unbounded user-controlled input.",
                "Check whether patterns are compiled repeatedly in hot paths.",
            ),
            fixes_to_consider=(
                "Compile and reuse Pattern objects for hot repeated matches.",
                "Constrain input size and simplify ambiguous quantified subpatterns.",
                "Use possessive quantifiers or atomic groups only after confirming they preserve intended matches.",
            ),
            pitfalls=(
                "Benchmarking only successful small inputs when failures are the expensive case.",
                "Adding greediness changes without testing captured groups and alternatives.",
                "Accepting unbounded regex input or patterns across a trust boundary.",
            ),
            docs=(pattern, matcher, tutorial("essential/regex/")),
        ),
        RegexIssue(
            key="split-tokenization",
            title="String.split, Pattern.split, delimiters, limits, and empty trailing tokens",
            aliases=("split", "token", "delimiter", "trailing empty", "csv"),
            first_checks=(
                "Identify whether the delimiter is a regex or a literal string.",
                "Check the split limit argument and whether trailing empty strings must be preserved.",
                "Avoid regex split for formats with quoting or escaping rules such as CSV.",
            ),
            fixes_to_consider=(
                "Use Pattern.quote for literal delimiters passed to regex split APIs.",
                "Pass a negative limit when trailing empty tokens must be retained.",
                "Use a real parser for structured formats with quotes, escapes, or nested syntax.",
            ),
            pitfalls=(
                "Splitting on . or | without escaping because they are regex metacharacters.",
                "Losing trailing empty fields due to default split behavior.",
                "Using regex split for CSV and similar formats with grammar beyond a delimiter.",
            ),
            docs=(string_api, pattern),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, RegexIssue]:
    index: dict[str, RegexIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> RegexIssue:
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
        raise ValueError(f"ambiguous regex issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown regex issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[RegexIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: RegexIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="Regex issue key or alias")
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
