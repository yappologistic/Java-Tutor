#!/usr/bin/env python3
"""Triage Java String, Unicode, locale, formatting, and text-resource issues with official links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class TextIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def jls(section: str, version: str = DEFAULT_VERSION) -> str:
    chapter = section.split(".")[0]
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/jls-{chapter}.html#jls-{section}"


def guide(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/{path}"


def issues(version: str = DEFAULT_VERSION) -> tuple[TextIssue, ...]:
    string = api("java/lang/String.html", version)
    string_builder = api("java/lang/StringBuilder.html", version)
    char_sequence = api("java/lang/CharSequence.html", version)
    character = api("java/lang/Character.html", version)
    locale = api("java/util/Locale.html", version)
    formatter = api("java/util/Formatter.html", version)
    resource_bundle = api("java/util/ResourceBundle.html", version)
    properties = api("java/util/Properties.html", version)
    normalizer = api("java/text/Normalizer.html", version)
    collator = api("java/text/Collator.html", version)
    break_iterator = api("java/text/BreakIterator.html", version)
    message_format = api("java/text/MessageFormat.html", version)
    number_format = api("java/text/NumberFormat.html", version)
    date_format = api("java/text/DateFormat.html", version)
    pattern_syntax = api("java/util/regex/Pattern.html", version)
    charset = api("java/nio/charset/Charset.html", version)
    standard_charsets = api("java/nio/charset/StandardCharsets.html", version)
    return (
        TextIssue(
            key="string-comparison",
            title="String equality, ordering, contains checks, and regex confusion",
            aliases=("string equals", "equalsignorecase", "compareto", "contains", "matches", "string comparison"),
            first_checks=(
                "Identify whether the comparison needs exact equality, case-insensitive equality, lexicographic ordering, locale-sensitive ordering, substring search, or regex matching.",
                "Check for == on String values; that compares references, not character content.",
                "Check whether String.matches was used when literal contains, startsWith, endsWith, or Pattern/Matcher.find semantics were intended.",
            ),
            fixes_to_consider=(
                "Use equals for exact content equality and compareTo only for natural lexicographic ordering.",
                "Use Collator for user-facing locale-sensitive sorting or comparison.",
                "Use Pattern and Matcher deliberately when the input is a regular expression rather than literal text.",
            ),
            pitfalls=(
                "Using == and passing tests accidentally because of string interning.",
                "Using compareTo result values as if only -1, 0, or 1 are possible.",
                "Treating String.matches as a substring search; it attempts to match the whole input against a regex.",
            ),
            docs=(string, collator, pattern_syntax, jls("15.21.3", version)),
        ),
        TextIssue(
            key="unicode-codepoints",
            title="Unicode code units, code points, supplementary characters, and text boundaries",
            aliases=("unicode", "code point", "surrogate", "emoji", "char length", "grapheme"),
            first_checks=(
                "Check whether the code operates on UTF-16 char values, Unicode code points, or user-perceived characters.",
                "Look for indexing, substring, length, reverse, truncate, or validation logic that can split surrogate pairs.",
                "For word, sentence, or character boundaries, identify whether locale-sensitive BreakIterator behavior is required.",
            ),
            fixes_to_consider=(
                "Use String codePoint* methods when logic must handle supplementary Unicode characters.",
                "Use Character APIs for code point classification and conversion.",
                "Use BreakIterator when user-facing text boundaries matter more than raw code unit offsets.",
            ),
            pitfalls=(
                "Assuming String.length counts user-visible characters.",
                "Reversing or truncating strings by char index and corrupting supplementary characters.",
                "Treating Unicode normalization, collation, and case mapping as the same problem.",
            ),
            docs=(string, character, char_sequence, break_iterator),
        ),
        TextIssue(
            key="locale-case",
            title="Locale-sensitive case mapping and case-insensitive matching",
            aliases=("tolowercase", "touppercase", "turkish i", "locale case", "case insensitive"),
            first_checks=(
                "Identify whether case mapping is for machine identifiers, protocol values, or user-facing natural language text.",
                "Check calls to toLowerCase or toUpperCase without an explicit Locale.",
                "For comparisons, check whether locale-sensitive collation or locale-independent case folding is intended.",
            ),
            fixes_to_consider=(
                "Use Locale.ROOT for locale-independent identifiers, keys, protocol tokens, and normalized internal values.",
                "Use the user's Locale when presenting or transforming natural-language text.",
                "Use Collator for user-facing case/accent-sensitive comparison requirements.",
            ),
            pitfalls=(
                "Letting the default locale change machine identifiers unexpectedly.",
                "Assuming equalsIgnoreCase handles every user-facing linguistic comparison correctly.",
                "Lowercasing before storage without documenting whether the mapping is locale-independent.",
            ),
            docs=(string, locale, collator),
        ),
        TextIssue(
            key="formatting-interpolation",
            title="String formatting, MessageFormat, Formatter, and text templates",
            aliases=("format", "formatted", "messageformat", "printf", "interpolation", "placeholder"),
            first_checks=(
                "Identify whether formatting is for developer logs, user-facing localized text, numbers, dates, or protocol output.",
                "Check whether Formatter-style placeholders or MessageFormat-style placeholders are being used.",
                "Inspect the Locale used for number and date rendering when output is user-facing or machine-parsed.",
            ),
            fixes_to_consider=(
                "Use String.format, formatted, or Formatter for Formatter-style developer or protocol formatting.",
                "Use MessageFormat and ResourceBundle for localized user-facing messages.",
                "Use NumberFormat and DateFormat or java.time formatters when locale-specific values are involved.",
            ),
            pitfalls=(
                "Mixing MessageFormat syntax with Formatter syntax.",
                "Using default-locale formatting for machine-readable files or wire formats.",
                "Concatenating localized messages instead of formatting a whole localized message pattern.",
            ),
            docs=(string, formatter, message_format, number_format, date_format, locale),
        ),
        TextIssue(
            key="text-blocks",
            title="Text blocks, incidental whitespace, escape processing, and source literals",
            aliases=("text block", "text blocks", "triple quote", "multiline string", "incidental whitespace"),
            first_checks=(
                "Check the project's Java source level; text blocks are available only in Java versions that support them.",
                "Inspect indentation, trailing newline expectations, escape sequences, and whether stripIndent or translateEscapes is involved.",
                "Confirm whether the literal is human-readable source text, JSON/SQL/XML, or an exact byte-level fixture.",
            ),
            fixes_to_consider=(
                "Use text blocks for readable multi-line source literals when incidental whitespace rules match the desired value.",
                "Use escapes or explicit concatenation when exact leading/trailing whitespace is critical.",
                "Add assertions for exact expected string values when whitespace is semantically significant.",
            ),
            pitfalls=(
                "Forgetting the implicit newline before the closing delimiter position affects the resulting value.",
                "Assuming source indentation is always preserved exactly.",
                "Using text blocks without checking the configured source or release level.",
            ),
            docs=(guide("text-blocks/index.html", version), string, jls("3.10.6", version)),
        ),
        TextIssue(
            key="builder-concat",
            title="String concatenation, StringBuilder, mutability, and repeated assembly",
            aliases=("stringbuilder", "string builder", "concat", "concatenation", "append", "mutable string"),
            first_checks=(
                "Identify whether concatenation happens once, inside a loop, across threads, or inside logging/formatting code.",
                "Check whether mutability, capacity growth, or accidental sharing of a builder affects correctness.",
                "Verify that null handling in concatenation or append calls matches the intended output.",
            ),
            fixes_to_consider=(
                "Use ordinary + concatenation for simple readable expressions.",
                "Use StringBuilder when assembling many pieces imperatively in one thread.",
                "Use formatters or joiners when separators, localization, or structured formatting dominate.",
            ),
            pitfalls=(
                "Prematurely replacing readable + expressions without evidence of a bottleneck.",
                "Sharing StringBuilder across threads without synchronization.",
                "Forgetting that append(null) appends the string \"null\" rather than failing.",
            ),
            docs=(string, string_builder, jls("15.18.1", version)),
        ),
        TextIssue(
            key="normalization-collation",
            title="Unicode normalization, collation, accents, and canonical equivalence",
            aliases=("normalization", "normalize", "collation", "accent", "canonical equivalence", "nfc"),
            first_checks=(
                "Determine whether the problem is binary equality, canonical equivalence, user-facing sort order, or search behavior.",
                "Check whether inputs can arrive in different Unicode normalization forms.",
                "Identify locale and strength requirements before comparing or sorting user-facing text.",
            ),
            fixes_to_consider=(
                "Use Normalizer when canonical composition/decomposition matters.",
                "Use Collator for locale-sensitive ordering and comparison.",
                "Normalize at defined boundaries and document which normalization form is stored or compared.",
            ),
            pitfalls=(
                "Assuming visually similar strings have identical code point sequences.",
                "Using binary String equality for user-facing search or sort behavior.",
                "Normalizing without considering security, identifiers, or compatibility-form side effects.",
            ),
            docs=(normalizer, collator, string, locale),
        ),
        TextIssue(
            key="resources-i18n",
            title="ResourceBundle, properties, localization, and missing resource behavior",
            aliases=("resourcebundle", "i18n", "localization", "properties", "missing resource", "translations"),
            first_checks=(
                "Identify the base name, class loader/module context, requested Locale, fallback chain, and resource format.",
                "Check whether missing keys, default locale fallback, or encoding assumptions explain the behavior.",
                "Verify that message patterns and arguments are localized together rather than concatenated piecemeal.",
            ),
            fixes_to_consider=(
                "Use ResourceBundle for locale-specific resources and keep keys stable.",
                "Use MessageFormat for parameterized localized messages.",
                "Use Properties or ResourceBundle control/custom providers deliberately when the storage format differs from standard bundles.",
            ),
            pitfalls=(
                "Testing only the default locale and missing fallback or missing-key behavior.",
                "Concatenating translated fragments in a way that breaks grammar in other languages.",
                "Confusing properties file behavior with ResourceBundle locale fallback rules.",
            ),
            docs=(resource_bundle, properties, message_format, locale),
        ),
        TextIssue(
            key="charset-boundary",
            title="Text-to-byte boundaries, charsets, and accidental platform defaults",
            aliases=("charset", "encoding", "utf-8", "default charset", "mojibake", "bytes string"),
            first_checks=(
                "Identify every boundary where text becomes bytes or bytes become text: files, sockets, process output, HTTP, databases, or archives.",
                "Check whether code uses the platform default charset implicitly.",
                "Confirm the external protocol or file format's required charset before changing conversion code.",
            ),
            fixes_to_consider=(
                "Use StandardCharsets.UTF_8 or the protocol-specified Charset explicitly.",
                "Keep text processing and byte processing separate until the boundary is clear.",
                "Add tests with non-ASCII text so encoding mistakes are observable.",
            ),
            pitfalls=(
                "Assuming a String has an encoding; encodings matter when converting between chars and bytes.",
                "Using the platform default charset in code that must behave the same across machines.",
                "Fixing mojibake by reinterpreting corrupted text instead of correcting the original boundary.",
            ),
            docs=(charset, standard_charsets, string),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, TextIssue]:
    index: dict[str, TextIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> TextIssue:
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
        raise ValueError(f"ambiguous text issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown text issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[TextIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: TextIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="Text issue key or alias")
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
