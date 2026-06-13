#!/usr/bin/env python3
"""Triage Java class loading, resources, class path, module path, and services issues."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class ClassLoadingIssue:
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


def jvms(chapter: str, anchor: str | None = None, version: str = DEFAULT_VERSION) -> str:
    suffix = f"#{anchor}" if anchor else ""
    return f"https://docs.oracle.com/javase/specs/jvms/se{version}/html/jvms-{chapter}.html{suffix}"


def issues(version: str = DEFAULT_VERSION) -> tuple[ClassLoadingIssue, ...]:
    class_loader = api("java/lang/ClassLoader.html", version)
    class_api = api("java/lang/Class.html", version)
    thread = api("java/lang/Thread.html", version)
    module = api("java/lang/Module.html", version)
    module_layer = api("java/lang/ModuleLayer.html", version)
    module_finder = api("java/lang/module/ModuleFinder.html", version)
    service_loader = api("java/util/ServiceLoader.html", version)
    url = api("java/net/URL.html", version)
    url_class_loader = api("java/net/URLClassLoader.html", version)
    jar_file = api("java/util/jar/JarFile.html", version)
    security_exception = api("java/lang/SecurityException.html", version)
    return (
        ClassLoadingIssue(
            key="not-found",
            title="ClassNotFoundException, NoClassDefFoundError, linkage timing, and missing dependencies",
            aliases=("classnotfoundexception", "noclassdeffounderror", "class not found", "missing class", "dependency missing"),
            first_checks=(
                "Capture the full exception, including caused-by chain and the exact binary class name.",
                "Identify whether failure occurs during explicit loading, resolution, initialization, or later linkage.",
                "Inspect runtime class path/module path, packaged artifacts, shaded jars, and optional dependencies.",
            ),
            fixes_to_consider=(
                "Add the missing runtime dependency to the same launch mode used in production.",
                "Check packaging rules so classes present at compile time are also present at runtime.",
                "Separate class loading failure from class initialization failure before changing dependencies.",
            ),
            pitfalls=(
                "Assuming compile success proves runtime class availability.",
                "Treating NoClassDefFoundError as always meaning the named class file is absent.",
                "Ignoring earlier initialization errors that poison later class use.",
            ),
            docs=(class_loader, class_api, jls("12", "jls-12.2", version), jvms("5", "jvms-5.3", version)),
        ),
        ClassLoadingIssue(
            key="resources",
            title="Classpath resources, ClassLoader resources, leading slashes, and URL handling",
            aliases=("resource", "resources", "getresource", "classpath resource", "leading slash", "resource stream"),
            first_checks=(
                "Determine whether the target is a classpath resource, module resource, filesystem path, or URL.",
                "Check resource name spelling, case sensitivity, package-relative versus absolute lookup, and packaging.",
                "Verify whether the code expects a URL, stream, directory listing, or local filesystem path.",
            ),
            fixes_to_consider=(
                "Use Class.getResource for class-relative or absolute resource names.",
                "Use ClassLoader.getResource with names that do not start with a leading slash.",
                "Treat resource URLs as opaque unless the protocol is known to be a local file.",
            ),
            pitfalls=(
                "Converting a jar resource URL to a File path.",
                "Using filesystem APIs for resources packaged inside jars or runtime images.",
                "Forgetting resource name case can matter after moving from Windows to Linux containers.",
            ),
            docs=(class_api, class_loader, url),
        ),
        ClassLoadingIssue(
            key="context-loader",
            title="Thread context ClassLoader, frameworks, plugins, and service discovery",
            aliases=("context classloader", "tccl", "thread context", "plugin", "service discovery"),
            first_checks=(
                "Inspect the current thread context ClassLoader at the failing framework or plugin boundary.",
                "Identify which loader defines the API types and which loader defines implementation classes.",
                "Check executor threads, virtual threads, app servers, build tools, and plugin systems for loader changes.",
            ),
            fixes_to_consider=(
                "Pass an explicit ClassLoader where APIs support it instead of relying on ambient context.",
                "Set and restore the thread context ClassLoader around narrow framework calls when required.",
                "Keep API types in a parent/shared loader and implementation details in child/plugin loaders.",
            ),
            pitfalls=(
                "Leaking plugin ClassLoaders through thread locals, cached services, or long-lived executors.",
                "Assuming every thread inherits the context loader expected by the application framework.",
                "Loading the same API type through multiple loaders and breaking casts.",
            ),
            docs=(thread, class_loader, service_loader),
        ),
        ClassLoadingIssue(
            key="modules-layers",
            title="Module path, ModuleLayer, readability, exports, opens, and split packages",
            aliases=("module layer", "modulepath", "module path", "readability", "split package", "modulefinder"),
            first_checks=(
                "Identify whether the app runs on class path, module path, a custom layer, or a mixed launch.",
                "Inspect module descriptors, resolved modules, readability edges, exports, opens, and split packages.",
                "Check whether the same package or module appears in more than one artifact or layer unexpectedly.",
            ),
            fixes_to_consider=(
                "Use module descriptors to declare required modules and services deliberately.",
                "Keep packages unique across modules to avoid split-package failures.",
                "Use custom ModuleLayer only when plugin isolation or dynamic module resolution is truly needed.",
            ),
            pitfalls=(
                "Putting modular and non-modular assumptions into the same launch command.",
                "Using exports when reflective frameworks need opens.",
                "Debugging only class path behavior when production launches on the module path.",
            ),
            docs=(module, module_layer, module_finder, jls("7", "jls-7.7", version)),
        ),
        ClassLoadingIssue(
            key="services",
            title="ServiceLoader providers, META-INF/services, provides/uses, and class loader selection",
            aliases=("serviceloader", "service loader", "provider", "meta-inf/services", "provides", "uses"),
            first_checks=(
                "Identify provider configuration mechanism: META-INF/services on class path or provides/uses in modules.",
                "Check provider class visibility, public no-arg constructor or provider method rules, and loader choice.",
                "Capture ServiceConfigurationError messages and every provider resource discovered.",
            ),
            fixes_to_consider=(
                "Put provider configuration in the artifact that contains the provider implementation.",
                "Use ServiceLoader.load with an explicit ClassLoader when context loader discovery is wrong.",
                "Declare uses and provides in module descriptors for modular service discovery.",
            ),
            pitfalls=(
                "Forgetting to merge META-INF/services files when shading jars.",
                "Loading service API and provider classes through incompatible loaders.",
                "Assuming providers are instantiated before ServiceLoader iteration begins.",
            ),
            docs=(service_loader, class_loader, module),
        ),
        ClassLoadingIssue(
            key="jar-url-loader",
            title="JARs, URLClassLoader, close behavior, nested jars, and dynamic loading",
            aliases=("jar", "urlclassloader", "dynamic loading", "nested jar", "close classloader"),
            first_checks=(
                "Inspect exact URLs, jar contents, manifest assumptions, nested-jar layout, and loader close lifecycle.",
                "Check whether loaded classes or resources remain referenced after a plugin should unload.",
                "Verify whether dynamic loading is compatible with the deployment format and module settings.",
            ),
            fixes_to_consider=(
                "Use URLClassLoader only when URL-based dynamic loading is the intended design.",
                "Close URLClassLoader when its resources should be released.",
                "Avoid assuming nested jars are ordinary class path entries unless the launcher supports them.",
            ),
            pitfalls=(
                "Expecting URLClassLoader to understand every application packaging format.",
                "Keeping static caches or threads that prevent class loader unloading.",
                "Modifying jar files while a loader still has open handles on them.",
            ),
            docs=(url_class_loader, jar_file, class_loader),
        ),
        ClassLoadingIssue(
            key="identity-casts",
            title="Class identity, casts, duplicate classes, and loader constraints",
            aliases=("classcastexception", "duplicate class", "same class", "loader identity", "cast"),
            first_checks=(
                "Print the class name and defining ClassLoader for both sides of the cast or API boundary.",
                "Look for duplicate jars, shaded classes, parent/child loader inversions, and plugin API duplication.",
                "Check whether serialization, reflection, or service loading crosses incompatible loader boundaries.",
            ),
            fixes_to_consider=(
                "Place shared API classes in one parent/shared loader.",
                "Remove duplicate copies of the same binary class from child/plugin artifacts.",
                "Design plugin boundaries around stable parent-loaded interfaces or data transfer objects.",
            ),
            pitfalls=(
                "Assuming equal binary names imply the same runtime type.",
                "Shading API classes that must be shared between host and plugin.",
                "Hiding loader identity in logs and losing the key diagnostic clue.",
            ),
            docs=(class_api, class_loader, jvms("5", "jvms-5.3", version)),
        ),
        ClassLoadingIssue(
            key="security-permissions",
            title="Class loading security checks, package definition, sealing, and permissions",
            aliases=("security", "permission", "defineclass", "package sealing", "sealed package"),
            first_checks=(
                "Capture SecurityException details, package name, code source, class loader, and jar manifest data.",
                "Check package sealing, duplicate packages across jars, and custom ClassLoader definePackage behavior.",
                "Identify whether legacy SecurityManager behavior or custom loader checks are involved.",
            ),
            fixes_to_consider=(
                "Keep sealed package classes in the same code source as required by the manifest contract.",
                "Avoid custom class loaders unless isolation, transformation, or dynamic loading requires them.",
                "Handle legacy SecurityManager-related behavior explicitly for older deployments.",
            ),
            pitfalls=(
                "Mixing classes from a sealed package across multiple jars.",
                "Ignoring code source and package metadata when defining classes dynamically.",
                "Assuming class loading security behavior is identical across old and modern JDKs.",
            ),
            docs=(class_loader, security_exception, url_class_loader),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, ClassLoadingIssue]:
    index: dict[str, ClassLoadingIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> ClassLoadingIssue:
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
        raise ValueError(f"ambiguous class loading issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown class loading issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[ClassLoadingIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: ClassLoadingIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="Class loading issue key or alias")
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
