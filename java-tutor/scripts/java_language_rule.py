#!/usr/bin/env python3
"""Route Java language-rule questions to precise JLS documentation."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class LanguageRule:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    common_pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def jls(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/{path}"


def api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def language_guide(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/language/{path}"


def rules(version: str = DEFAULT_VERSION) -> tuple[LanguageRule, ...]:
    return (
        LanguageRule(
            key="overload-resolution",
            title="Method invocation and overload resolution",
            aliases=("overload", "overloading", "method invocation", "ambiguous method", "varargs"),
            first_checks=(
                "Identify the compile-time target type, argument expressions, and candidate methods.",
                "Separate strict invocation, loose invocation, and variable-arity phases before choosing a most-specific method.",
                "Check whether boxing, widening, varargs, generics, or lambdas changed applicability.",
            ),
            common_pitfalls=(
                "Assuming the runtime class chooses overloaded methods; overload resolution is a compile-time process.",
                "Forgetting that null can make unrelated reference overloads ambiguous.",
                "Confusing overriding dispatch with overload selection.",
            ),
            docs=(jls("jls-15.html#jls-15.12", version), jls("jls-15.html#jls-15.12.2", version)),
        ),
        LanguageRule(
            key="generic-inference",
            title="Generic method invocation and type inference",
            aliases=("generics", "type inference", "diamond", "inference variable", "generic method"),
            first_checks=(
                "Identify explicit type arguments, target type, parameter types, and argument expressions.",
                "Check whether inference uses assignment, invocation, or cast context.",
                "Inspect bounds, wildcards, captures, and overload resolution together instead of in isolation.",
            ),
            common_pitfalls=(
                "Expecting inference to use information that is unavailable in the current context.",
                "Treating List<Subtype> as a subtype of List<Supertype> instead of using wildcards where needed.",
                "Changing overload selection accidentally by adding a generic overload.",
            ),
            docs=(jls("jls-18.html", version), jls("jls-4.html#jls-4.5", version), jls("jls-5.html#jls-5.1.10", version)),
        ),
        LanguageRule(
            key="erasure-bridge-methods",
            title="Type erasure, reifiability, and bridge methods",
            aliases=("erasure", "bridge method", "raw type", "heap pollution", "reifiable"),
            first_checks=(
                "Check whether the code relies on generic type information at runtime.",
                "Identify raw types, unchecked conversions, generic arrays, and non-reifiable varargs.",
                "Inspect overridden generic methods for erasure clashes or compiler-generated bridge methods.",
            ),
            common_pitfalls=(
                "Using instanceof or class literals as if parameterized type arguments exist at runtime.",
                "Ignoring unchecked warnings that can become ClassCastException later.",
                "Mistaking bridge methods in stack traces or reflection output for source methods.",
            ),
            docs=(jls("jls-4.html#jls-4.6", version), jls("jls-4.html#jls-4.7", version), jls("jls-8.html#jls-8.4.8.3", version)),
        ),
        LanguageRule(
            key="overriding-hiding",
            title="Overriding, hiding, and dynamic dispatch",
            aliases=("override", "overriding", "hiding", "dynamic dispatch", "static method"),
            first_checks=(
                "Determine whether the member is an instance method, static method, field, private method, or constructor.",
                "Check signatures, return-type substitutability, access modifiers, throws clauses, and final/static/private constraints.",
                "Separate field hiding and static method hiding from instance method overriding.",
            ),
            common_pitfalls=(
                "Expecting fields or static methods to dispatch polymorphically.",
                "Changing access, return types, or checked exceptions in a way that prevents overriding.",
                "Forgetting that private methods are not inherited for overriding purposes.",
            ),
            docs=(jls("jls-8.html#jls-8.4.8", version), jls("jls-8.html#jls-8.3", version), jls("jls-15.html#jls-15.12.4.4", version)),
        ),
        LanguageRule(
            key="initialization-order",
            title="Class, interface, field, and instance initialization",
            aliases=("initialization", "static init", "class initialization", "initializer", "constructor order"),
            first_checks=(
                "Identify whether the question is about loading, linking, class initialization, instance creation, or constructor execution.",
                "Trace superclass initialization before subclass initialization.",
                "Check textual order of field initializers and initializer blocks within each class.",
            ),
            common_pitfalls=(
                "Calling overridable methods from constructors before subclass state is initialized.",
                "Reading fields before their initializer has executed.",
                "Confusing class initialization triggers with object construction steps.",
            ),
            docs=(jls("jls-12.html#jls-12.4", version), jls("jls-12.html#jls-12.5", version), jls("jls-8.html#jls-8.8.7", version)),
        ),
        LanguageRule(
            key="try-with-resources",
            title="Try-with-resources, closing, and suppressed exceptions",
            aliases=("try with resources", "autocloseable", "suppressed exception", "close order", "resource"),
            first_checks=(
                "Identify every resource variable and whether it implements AutoCloseable.",
                "Check resource closing order and whether close failures are suppressed under a primary exception.",
                "Inspect catch/finally logic for behavior that hides or replaces the original failure.",
            ),
            common_pitfalls=(
                "Assuming resources close in declaration order; they close in reverse order.",
                "Losing suppressed exceptions when wrapping or logging exceptions manually.",
                "Using a resource after the try-with-resources statement has closed it.",
            ),
            docs=(jls("jls-14.html#jls-14.20.3", version), api("java/lang/AutoCloseable.html", version)),
        ),
        LanguageRule(
            key="lambda-capture",
            title="Lambda bodies, target typing, and captured locals",
            aliases=("lambda", "effectively final", "capture", "functional interface", "method reference"),
            first_checks=(
                "Identify the target functional interface and its single abstract method.",
                "Check whether captured local variables are final or effectively final.",
                "Resolve overloads that use lambdas only after considering target typing and functional interface compatibility.",
            ),
            common_pitfalls=(
                "Trying to mutate a captured local variable from inside a lambda.",
                "Expecting a lambda to have a standalone type without a target type.",
                "Creating ambiguous overloads with different functional interfaces.",
            ),
            docs=(jls("jls-15.html#jls-15.27", version), jls("jls-9.html#jls-9.8", version), jls("jls-15.html#jls-15.13", version)),
        ),
        LanguageRule(
            key="records",
            title="Record classes, components, and constructors",
            aliases=("record", "record class", "canonical constructor", "compact constructor"),
            first_checks=(
                "Identify record components and the automatically declared members.",
                "Check whether the constructor is canonical, compact, or non-canonical.",
                "Confirm invariants are enforced without assigning directly to final component fields in a compact constructor.",
            ),
            common_pitfalls=(
                "Treating records as mutable data classes instead of shallowly immutable carriers.",
                "Forgetting that component values can reference mutable objects.",
                "Breaking API expectations by overriding generated members inconsistently.",
            ),
            docs=(jls("jls-8.html#jls-8.10", version), language_guide("records.html", version), "https://openjdk.org/jeps/395"),
        ),
        LanguageRule(
            key="pattern-variables",
            title="Pattern variables, scope, and switch patterns",
            aliases=("pattern variable", "instanceof pattern", "pattern matching", "switch pattern", "flow scoping"),
            first_checks=(
                "Identify which pattern introduces the variable and where the pattern has definitely matched.",
                "Check boolean operators, negation, loops, and switch labels for flow-sensitive scope.",
                "For switch, check dominance, exhaustiveness, null handling, and guards.",
            ),
            common_pitfalls=(
                "Using a pattern variable outside the region where the compiler knows the match succeeded.",
                "Ordering switch labels so an earlier pattern dominates a later one.",
                "Forgetting that preview-era pattern behavior may differ from final Java SE behavior.",
            ),
            docs=(jls("jls-6.html#jls-6.3", version), jls("jls-14.html#jls-14.30", version), jls("jls-14.html#jls-14.11", version)),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def rule_index(version: str = DEFAULT_VERSION) -> dict[str, LanguageRule]:
    index: dict[str, LanguageRule] = {}
    for rule in rules(version):
        index[normalize(rule.key)] = rule
        index[normalize(rule.title)] = rule
        for alias in rule.aliases:
            index[normalize(alias)] = rule
    return index


def find_rule(query: str, version: str = DEFAULT_VERSION) -> LanguageRule:
    normalized = normalize(query)
    index = rule_index(version)
    if normalized in index:
        return index[normalized]
    matches = [rule for key, rule in index.items() if normalized in key or key in normalized]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if unique_matches:
        options = ", ".join(rule.key for rule in unique_matches)
        raise ValueError(f"ambiguous language rule {query!r}; choose one of: {options}")
    available = ", ".join(rule.key for rule in rules(version))
    raise ValueError(f"unknown language rule {query!r}; available rules: {available}")


def official_urls(selected: Iterable[LanguageRule]) -> tuple[str, ...]:
    urls: list[str] = []
    for rule in selected:
        urls.extend(rule.docs)
    return tuple(dict.fromkeys(urls))


def render_text(rule: LanguageRule) -> str:
    lines = [rule.title, f"Key: {rule.key}", "", "First checks:"]
    lines.extend(f"{index}. {check}" for index, check in enumerate(rule.first_checks, start=1))
    lines.extend(["", "Common pitfalls:"])
    lines.extend(f"- {pitfall}" for pitfall in rule.common_pitfalls)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in rule.docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rule", nargs="?", help="Language rule key or alias")
    parser.add_argument("--list", action="store_true", help="List known rule keys")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java Language Specification version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        keys = [rule.key for rule in rules(args.version)]
        print(json.dumps(keys, indent=2) if args.json else "\n".join(keys))
        return 0

    if not args.rule:
        parser.error("rule is required unless --list is used")

    try:
        rule = find_rule(args.rule, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(rule)
        payload["official_docs"] = list(rule.docs)
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(rule))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
