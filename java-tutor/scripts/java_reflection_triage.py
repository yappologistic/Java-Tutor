#!/usr/bin/env python3
"""Triage Java reflection, annotations, proxies, method handles, and access issues."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class ReflectionIssue:
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


def issues(version: str = DEFAULT_VERSION) -> tuple[ReflectionIssue, ...]:
    class_api = api("java/lang/Class.html", version)
    member = api("java/lang/reflect/Member.html", version)
    method = api("java/lang/reflect/Method.html", version)
    constructor = api("java/lang/reflect/Constructor.html", version)
    field = api("java/lang/reflect/Field.html", version)
    accessible = api("java/lang/reflect/AccessibleObject.html", version)
    invocation_target = api("java/lang/reflect/InvocationTargetException.html", version)
    modifier = api("java/lang/reflect/Modifier.html", version)
    parameterized_type = api("java/lang/reflect/ParameterizedType.html", version)
    annotated_element = api("java/lang/reflect/AnnotatedElement.html", version)
    annotation = api("java/lang/annotation/Annotation.html", version)
    retention = api("java/lang/annotation/Retention.html", version)
    retention_policy = api("java/lang/annotation/RetentionPolicy.html", version)
    target = api("java/lang/annotation/Target.html", version)
    module = api("java/lang/Module.html", version)
    proxy = api("java/lang/reflect/Proxy.html", version)
    invocation_handler = api("java/lang/reflect/InvocationHandler.html", version)
    method_handles = api("java/lang/invoke/MethodHandles.html", version)
    method_handle = api("java/lang/invoke/MethodHandle.html", version)
    lookup = api("java/lang/invoke/MethodHandles.Lookup.html", version)
    record_component = api("java/lang/reflect/RecordComponent.html", version)
    record_api = api("java/lang/Record.html", version)
    return (
        ReflectionIssue(
            key="access-members",
            title="Reflective access, members, constructors, fields, and InvocationTargetException",
            aliases=("reflection", "method invoke", "field", "constructor", "setaccessible", "invocationtargetexception"),
            first_checks=(
                "Identify the reflected class, member, declaring package, module, visibility, and caller module.",
                "Check whether failure is lookup, accessibility, invocation target, type conversion, or class loading.",
                "Unwrap InvocationTargetException to inspect the exception thrown by the invoked method or constructor.",
            ),
            fixes_to_consider=(
                "Prefer public APIs over reflective access when the target is under your control.",
                "Use getDeclared* only when non-public members are intentionally part of the reflective contract.",
                "Handle reflective lookup failures separately from failures thrown by invoked code.",
            ),
            pitfalls=(
                "Treating InvocationTargetException as the root cause.",
                "Assuming setAccessible bypasses all module access checks.",
                "Relying on private members whose names or signatures can change without compatibility promises.",
            ),
            docs=(class_api, member, method, constructor, field, accessible, invocation_target),
        ),
        ReflectionIssue(
            key="annotations-retention",
            title="Annotation visibility, RetentionPolicy, Target, inheritance, and repeatable annotations",
            aliases=("annotation", "annotations", "retention", "runtime annotation", "target", "repeatable"),
            first_checks=(
                "Check the annotation RetentionPolicy and whether runtime reflection is expected to see it.",
                "Verify the Target meta-annotation matches the program element being annotated.",
                "Distinguish direct, inherited, repeatable, and type-use annotations before querying reflection APIs.",
            ),
            fixes_to_consider=(
                "Use RetentionPolicy.RUNTIME for annotations that runtime reflection must observe.",
                "Use the correct AnnotatedElement query for direct, inherited, or repeated annotation semantics.",
                "Add explicit tests around annotation discovery if frameworks depend on it.",
            ),
            pitfalls=(
                "Expecting CLASS-retained annotations to be visible through runtime reflection.",
                "Assuming @Inherited applies to methods, fields, interfaces, or type-use annotations.",
                "Reading only one annotation when a repeatable annotation container is involved.",
            ),
            docs=(annotation, annotated_element, retention, retention_policy, target, jls("9", "jls-9.6", version)),
        ),
        ReflectionIssue(
            key="modules-opens",
            title="JPMS reflective access, exports, opens, add-opens, and strong encapsulation",
            aliases=("module reflection", "inaccessibleobjectexception", "opens", "exports", "add-opens", "jpms reflection"),
            first_checks=(
                "Identify source module, target module, package, whether the package is exported or opened, and launch flags.",
                "Check whether the code needs compile-time access, reflective access, or deep reflection.",
                "Confirm whether the failure appears only on newer JDKs due to stronger encapsulation.",
            ),
            fixes_to_consider=(
                "Use module-info opens for packages intentionally accessed reflectively by frameworks.",
                "Use --add-opens only as an explicit migration or launch-time compatibility measure.",
                "Prefer public exported APIs for stable cross-module contracts.",
            ),
            pitfalls=(
                "Using exports when deep reflection requires opens.",
                "Adding broad opens to every package instead of scoping reflective access.",
                "Depending on JDK internals that are strongly encapsulated or unsupported.",
            ),
            docs=(module, accessible, jls("7", "jls-7.7.2", version), jls("7", "jls-7.7.3", version)),
        ),
        ReflectionIssue(
            key="generic-types",
            title="Generic type metadata, type erasure, ParameterizedType, and reflective signatures",
            aliases=("generic", "generics", "parameterizedtype", "type erasure", "generic type", "signature"),
            first_checks=(
                "Identify whether the needed information is available at runtime or erased by the language model.",
                "Inspect generic superclass, interfaces, fields, methods, and parameters rather than raw Class alone.",
                "Check whether framework proxies or synthetic bridge methods alter the reflected view.",
            ),
            fixes_to_consider=(
                "Use java.lang.reflect.Type APIs when generic signature metadata is present.",
                "Pass explicit Class or Type tokens when runtime type inference cannot recover erased information.",
                "Keep reflective generic handling defensive around wildcards, type variables, and raw types.",
            ),
            pitfalls=(
                "Expecting Class<List<String>> style runtime types to exist after erasure.",
                "Casting every Type to ParameterizedType without checking its actual subtype.",
                "Ignoring bridge methods when reflecting over generic overrides.",
            ),
            docs=(parameterized_type, class_api, method, jls("4", "jls-4.6", version)),
        ),
        ReflectionIssue(
            key="dynamic-proxy",
            title="Dynamic proxies, InvocationHandler, interface dispatch, equals/hashCode, and modules",
            aliases=("proxy", "dynamic proxy", "invocationhandler", "jdk proxy", "interface proxy"),
            first_checks=(
                "Verify every proxied type is an interface visible to the chosen class loader/module context.",
                "Check how equals, hashCode, toString, default methods, and checked exceptions are handled.",
                "Inspect the InvocationHandler path for target exceptions, recursion, and class loader leaks.",
            ),
            fixes_to_consider=(
                "Use Proxy only for interface-based dispatch and choose a class loader that can see all interfaces.",
                "Handle Object methods deliberately inside InvocationHandler.",
                "Unwrap and propagate target exceptions according to the proxied method contract.",
            ),
            pitfalls=(
                "Trying to proxy concrete classes with JDK dynamic proxies.",
                "Forgetting equals/hashCode/toString behavior and breaking map/set or logging behavior.",
                "Leaking application class loaders through cached proxy classes or handlers.",
            ),
            docs=(proxy, invocation_handler, method),
        ),
        ReflectionIssue(
            key="method-handles",
            title="MethodHandle lookup, access modes, invocation types, and reflection alternatives",
            aliases=("methodhandle", "method handles", "lookup", "invokeexact", "varhandle", "java.lang.invoke"),
            first_checks=(
                "Identify lookup class, access mode, target member type, method type, and caller module/package.",
                "Check whether invokeExact type signatures match exactly at compile-time call sites.",
                "Decide whether reflection, MethodHandle, VarHandle, or a direct lambda is the correct mechanism.",
            ),
            fixes_to_consider=(
                "Use MethodHandles.Lookup with the narrowest required access privileges.",
                "Prefer invokeExact when exact static type checking is valuable and signatures are stable.",
                "Use publicLookup or scoped lookups when crossing module or package boundaries.",
            ),
            pitfalls=(
                "Assuming MethodHandles automatically bypass reflection/module access rules.",
                "Confusing invoke and invokeExact conversion behavior.",
                "Using dynamic invocation where a direct method reference or interface is clearer.",
            ),
            docs=(method_handles, method_handle, lookup, module),
        ),
        ReflectionIssue(
            key="records-reflection",
            title="Record reflection, RecordComponent, canonical constructors, and component annotations",
            aliases=("record", "records", "recordcomponent", "record reflection", "canonical constructor"),
            first_checks=(
                "Check whether the class is a record and inspect record components rather than only fields.",
                "Identify component names, accessor methods, canonical constructor parameters, and annotations.",
                "Verify framework assumptions about no-arg constructors, mutable fields, and bean setters.",
            ),
            fixes_to_consider=(
                "Use Class.isRecord and getRecordComponents for record-aware reflection.",
                "Map record components to accessors and canonical constructor parameters explicitly.",
                "Adapt serializers or mappers to immutable record construction when necessary.",
            ),
            pitfalls=(
                "Treating record components as ordinary mutable bean properties.",
                "Reading fields only and missing component-level annotations.",
                "Expecting frameworks that require no-arg constructors or setters to work unchanged with records.",
            ),
            docs=(record_api, record_component, class_api, jls("8", "jls-8.10", version)),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, ReflectionIssue]:
    index: dict[str, ReflectionIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> ReflectionIssue:
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
        raise ValueError(f"ambiguous reflection issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown reflection issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[ReflectionIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: ReflectionIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="Reflection issue key or alias")
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
