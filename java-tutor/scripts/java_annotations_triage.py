#!/usr/bin/env python3
"""Triage Java annotation retention, targets, reflection, and processors with official links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class AnnotationIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def base_api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def compiler_api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.compiler/{path}"


def jls(section: str, version: str = DEFAULT_VERSION) -> str:
    chapter = section.split(".")[0]
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/jls-{chapter}.html#jls-{section}"


def issues(version: str = DEFAULT_VERSION) -> tuple[AnnotationIssue, ...]:
    annotation = base_api("java/lang/annotation/Annotation.html", version)
    annotated_element = base_api("java/lang/reflect/AnnotatedElement.html", version)
    retention = base_api("java/lang/annotation/Retention.html", version)
    retention_policy = base_api("java/lang/annotation/RetentionPolicy.html", version)
    target = base_api("java/lang/annotation/Target.html", version)
    element_type = base_api("java/lang/annotation/ElementType.html", version)
    inherited = base_api("java/lang/annotation/Inherited.html", version)
    repeatable = base_api("java/lang/annotation/Repeatable.html", version)
    documented = base_api("java/lang/annotation/Documented.html", version)
    suppress_warnings = base_api("java/lang/SuppressWarnings.html", version)
    override = base_api("java/lang/Override.html", version)
    deprecated = base_api("java/lang/Deprecated.html", version)
    safe_varargs = base_api("java/lang/SafeVarargs.html", version)
    processor = compiler_api("javax/annotation/processing/Processor.html", version)
    abstract_processor = compiler_api("javax/annotation/processing/AbstractProcessor.html", version)
    round_environment = compiler_api("javax/annotation/processing/RoundEnvironment.html", version)
    processing_environment = compiler_api("javax/annotation/processing/ProcessingEnvironment.html", version)
    filer = compiler_api("javax/annotation/processing/Filer.html", version)
    messager = compiler_api("javax/annotation/processing/Messager.html", version)
    element = compiler_api("javax/lang/model/element/Element.html", version)
    return (
        AnnotationIssue(
            key="retention-target",
            title="Annotation retention, target, and runtime visibility",
            aliases=("retention", "target", "runtime annotation", "annotation not visible", "elementtype"),
            first_checks=(
                "Check the annotation type declaration for @Retention and @Target.",
                "Confirm whether the consumer expects source-time, class-file, or runtime reflection visibility.",
                "Verify that every use site is allowed by the declared ElementType targets.",
            ),
            fixes_to_consider=(
                "Use RetentionPolicy.RUNTIME only when runtime reflection must observe the annotation.",
                "Use RetentionPolicy.CLASS for class-file tooling that does not require runtime reflection.",
                "Declare the narrowest @Target set that matches the intended language elements.",
            ),
            pitfalls=(
                "Expecting SOURCE- or CLASS-retained annotations to appear through reflection.",
                "Forgetting @Target, which permits broad use rather than documenting intent.",
                "Using METHOD or FIELD targets when the intended use is TYPE_USE or PARAMETER.",
            ),
            docs=(annotation, retention, retention_policy, target, element_type, jls("9.6.4.2", version), jls("9.6.4.3", version)),
        ),
        AnnotationIssue(
            key="reflection-lookup",
            title="Reading annotations with reflection and AnnotatedElement semantics",
            aliases=("getannotation", "getannotations", "declared annotation", "reflection lookup", "annotatedelement"),
            first_checks=(
                "Identify whether the lookup needs directly present, indirectly present, present, or associated annotations.",
                "Check whether the query is on a Class, method, constructor, field, parameter, package, module, or type-use location.",
                "Confirm retention is RUNTIME before debugging reflection lookup code.",
            ),
            fixes_to_consider=(
                "Use getDeclaredAnnotation(s) when only directly declared annotations should count.",
                "Use getAnnotation(s) when inherited class annotations should be considered.",
                "Use getAnnotationsByType or getDeclaredAnnotationsByType for repeatable annotations.",
            ),
            pitfalls=(
                "Using getAnnotation and assuming it means directly declared on the element.",
                "Debugging reflection code before confirming the annotation has RetentionPolicy.RUNTIME.",
                "Expecting type-use annotations to appear from ordinary declaration-annotation queries.",
            ),
            docs=(annotated_element, annotation, retention_policy),
        ),
        AnnotationIssue(
            key="inherited-repeatable",
            title="@Inherited, @Repeatable, containers, and repeatable annotation lookup",
            aliases=("inherited", "repeatable", "repeatable annotation", "container annotation", "annotationsbytype"),
            first_checks=(
                "Check whether @Inherited is present and whether the query is on a class rather than a method, field, interface, or type use.",
                "Verify that a repeatable annotation declares a valid containing annotation type.",
                "Check whether reflection should return the container annotation, repeated annotations, or both.",
            ),
            fixes_to_consider=(
                "Use @Inherited only for class-level annotations where superclass inheritance is part of the contract.",
                "Use @Repeatable with a container annotation whose value element returns the repeated annotation array type.",
                "Prefer getAnnotationsByType when callers want the logical repeated annotation values.",
            ),
            pitfalls=(
                "Assuming @Inherited applies to interfaces, methods, fields, parameters, or type-use annotations.",
                "Forgetting that repeatable annotations are represented with a containing annotation in class files.",
                "Mixing direct container declarations with repeated annotations without testing reflection behavior.",
            ),
            docs=(inherited, repeatable, annotated_element, jls("9.6.3", version), jls("9.6.4.3", version)),
        ),
        AnnotationIssue(
            key="type-use",
            title="Type-use annotations, receiver annotations, and annotated type APIs",
            aliases=("type use", "type-use", "type annotation", "receiver annotation", "annotated type"),
            first_checks=(
                "Check whether the annotation target includes ElementType.TYPE_USE or ElementType.TYPE_PARAMETER.",
                "Identify the annotated type location: generic argument, array level, cast, receiver, throws type, or bound.",
                "Use reflection's annotated type APIs rather than declaration annotation APIs when reading type-use metadata.",
            ),
            fixes_to_consider=(
                "Add TYPE_USE only when the annotation semantically applies to uses of a type rather than just declarations.",
                "Use AnnotatedType and related reflection APIs for runtime-visible type-use annotations.",
                "Write tests for nested generic and array type-use locations because placement matters.",
            ),
            pitfalls=(
                "Expecting a declaration annotation API to find annotations written on a type use.",
                "Placing an annotation on the array type level different from the one a checker or framework reads.",
                "Using TYPE_USE as a broad escape hatch when a narrower declaration target would be clearer.",
            ),
            docs=(element_type, annotated_element, base_api("java/lang/reflect/AnnotatedType.html", version), jls("9.7.4", version)),
        ),
        AnnotationIssue(
            key="annotation-processing",
            title="Annotation processing rounds, generated files, diagnostics, and supported annotations",
            aliases=("processor", "annotation processor", "apt", "roundenvironment", "generated source", "filer"),
            first_checks=(
                "Identify whether the annotation is needed at compile time by a processor or at runtime by reflection.",
                "Check supported annotation types, supported source version, processing rounds, and whether processing is claimed.",
                "Inspect generated source/resource paths and diagnostics emitted through Filer and Messager.",
            ),
            fixes_to_consider=(
                "Use AbstractProcessor for conventional javac annotation processors unless a lower-level Processor implementation is required.",
                "Generate files through Filer and report source-positioned diagnostics through Messager.",
                "Make processors deterministic across rounds and handle the final processingOver round.",
            ),
            pitfalls=(
                "Expecting SOURCE-retained annotations to be visible at runtime just because a processor can read them.",
                "Generating the same file in more than one round.",
                "Claiming annotations too broadly and preventing other processors from seeing them.",
            ),
            docs=(processor, abstract_processor, round_environment, processing_environment, filer, messager, element),
        ),
        AnnotationIssue(
            key="predefined-annotations",
            title="Predefined annotations: @Override, @Deprecated, @SuppressWarnings, and @SafeVarargs",
            aliases=("override", "deprecated", "suppresswarnings", "safevarargs", "predefined annotation"),
            first_checks=(
                "Identify whether the annotation is enforced by the compiler, consumed by tools, or visible to runtime reflection.",
                "Check whether @SuppressWarnings and @SafeVarargs are scoped as narrowly as possible.",
                "For @Deprecated, verify whether forRemoval and since metadata should be supplied for migration clarity.",
            ),
            fixes_to_consider=(
                "Use @Override on methods intended to override or implement a supertype method.",
                "Use @SuppressWarnings only at the smallest declaration that contains the justified warning.",
                "Use @SafeVarargs only when the generic varargs method body is actually safe and the declaration is eligible.",
            ),
            pitfalls=(
                "Suppressing warnings broadly and hiding new compiler diagnostics.",
                "Using @SafeVarargs to silence a warning without auditing heap-pollution risk.",
                "Deprecating APIs without migration guidance or metadata useful to callers.",
            ),
            docs=(override, deprecated, suppress_warnings, safe_varargs, jls("9.6.4", version)),
        ),
        AnnotationIssue(
            key="annotation-elements",
            title="Annotation element types, default values, constants, and nested annotations",
            aliases=("annotation element", "default value", "annotation value", "constant expression", "nested annotation"),
            first_checks=(
                "Check that every annotation element return type is one of the annotation-supported types.",
                "Confirm default values are compile-time constants, enum constants, class literals, annotations, or arrays of supported values.",
                "Remember that annotation element values are part of source and binary contracts consumed by tools and frameworks.",
            ),
            fixes_to_consider=(
                "Use simple element types and defaults that keep common call sites readable.",
                "Use nested annotations or arrays only when the modeled metadata genuinely needs structure or multiplicity.",
                "Prefer adding optional elements with defaults when evolving public annotation APIs.",
            ),
            pitfalls=(
                "Trying to use arbitrary object instances, null, or non-constant values as annotation element values.",
                "Renaming annotation elements without considering source and binary compatibility.",
                "Using mutable semantics in annotation metadata; annotation element values are declarative metadata.",
            ),
            docs=(annotation, jls("9.6.1", version), jls("9.7.1", version)),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, AnnotationIssue]:
    index: dict[str, AnnotationIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> AnnotationIssue:
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
        raise ValueError(f"ambiguous annotation issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown annotation issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[AnnotationIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: AnnotationIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="Annotation issue key or alias")
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
