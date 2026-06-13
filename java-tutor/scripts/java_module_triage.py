#!/usr/bin/env python3
"""Triage Java Platform Module System issues with official documentation links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"
JEP_261 = "https://openjdk.org/jeps/261"


@dataclass(frozen=True)
class ModuleIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    cautions: tuple[str, ...]
    docs: tuple[str, ...]


def doc(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/{path}"


def jls(section: str, version: str = DEFAULT_VERSION) -> str:
    chapter = section.split(".")[0]
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/jls-{chapter}.html#jls-{section}"


def issues(version: str = DEFAULT_VERSION) -> tuple[ModuleIssue, ...]:
    java_man = doc("docs/specs/man/java.html", version)
    javac_man = doc("docs/specs/man/javac.html", version)
    jar_man = doc("docs/specs/man/jar.html", version)
    jdeps_man = doc("docs/specs/man/jdeps.html", version)
    module_api = doc("docs/api/java.base/java/lang/Module.html", version)
    service_loader = doc("docs/api/java.base/java/util/ServiceLoader.html", version)
    return (
        ModuleIssue(
            key="module-descriptor",
            title="module-info.java descriptor design and compilation",
            aliases=("module-info", "module descriptor", "requires", "exports", "opens"),
            first_checks=(
                "Find the module-info.java file and the module name it declares.",
                "Check required modules, exported packages, opened packages, used services, and provided services.",
                "Compile with the same module path and source/release level used by the build.",
            ),
            fixes_to_consider=(
                "Add only the requires directives needed by compiled references.",
                "Export API packages; open packages only when reflective access is required.",
                "Keep module names stable and aligned with the artifact's intended public identity.",
            ),
            cautions=(
                "Do not export or open every package to silence one error; that defeats encapsulation.",
                "Changing a module name is a compatibility break for downstream module users.",
            ),
            docs=(jls("7.7", version), javac_man, JEP_261),
        ),
        ModuleIssue(
            key="module-path-class-path",
            title="Module path, class path, unnamed module, and automatic modules",
            aliases=("module path", "classpath", "class path", "unnamed module", "automatic module"),
            first_checks=(
                "Identify which dependencies are on the module path and which are on the class path.",
                "Check whether non-modular JARs become automatic modules or stay in the unnamed module.",
                "Capture the exact java/javac command or build tool configuration.",
            ),
            fixes_to_consider=(
                "Move modular dependencies to the module path when strong module boundaries are needed.",
                "Keep legacy class path dependencies on the class path when migration is incremental.",
                "Use jdeps to understand the module graph before changing packaging.",
            ),
            cautions=(
                "Automatic module names can be derived from JAR names and may not be stable API.",
                "Mixing class path and module path can hide readability assumptions during migration.",
            ),
            docs=(java_man, javac_man, jar_man, jdeps_man, JEP_261),
        ),
        ModuleIssue(
            key="readability",
            title="Module readability and requires failures",
            aliases=("reads", "readability", "requires transitive", "module not found", "does not read"),
            first_checks=(
                "Identify the source module, target module, and package containing the referenced type.",
                "Check whether the source module declares requires or requires transitive for the target module.",
                "Confirm the target module is observable on the module path or in the runtime image.",
            ),
            fixes_to_consider=(
                "Add requires for direct dependencies referenced by module source.",
                "Use requires transitive only when downstream modules need implied readability of an API dependency.",
                "Use --add-reads only as a narrow migration or diagnostic workaround.",
            ),
            cautions=(
                "requires transitive exposes dependency shape as part of your module API.",
                "Runtime --add-reads flags do not replace a clean module descriptor for library code.",
            ),
            docs=(jls("7.7.1", version), java_man, javac_man, module_api),
        ),
        ModuleIssue(
            key="exports-opens",
            title="Exports, opens, reflection, and encapsulation failures",
            aliases=("export", "exports", "open package", "opens", "reflection", "inaccessibleobjectexception", "add-opens", "add-exports"),
            first_checks=(
                "Determine whether the failure is compile-time access, runtime access, or deep reflection.",
                "Identify the package being accessed and the module attempting access.",
                "Check whether exports, qualified exports, opens, qualified opens, --add-exports, or --add-opens is being used.",
            ),
            fixes_to_consider=(
                "Export packages that are intended public API.",
                "Open packages only for frameworks or tooling that need deep reflection.",
                "Prefer upgrading reflection-heavy libraries before adding broad command-line opens.",
            ),
            cautions=(
                "Opening packages broadly can leak internals and hide unsupported access.",
                "Command-line access flags are deployment configuration, not a substitute for module design.",
            ),
            docs=(jls("7.7.2", version), java_man, JEP_261),
        ),
        ModuleIssue(
            key="split-packages",
            title="Split packages and duplicate packages across modules",
            aliases=("split package", "duplicate package", "package exists in another module"),
            first_checks=(
                "Find every JAR or module containing the package named in the diagnostic.",
                "Check whether generated sources, test fixtures, shaded JARs, or multi-release JAR entries duplicate the package.",
                "Inspect dependency mediation to see whether two versions of the same library are present.",
            ),
            fixes_to_consider=(
                "Refactor package ownership so one package belongs to one module.",
                "Remove duplicate dependency versions or exclude the unwanted artifact.",
                "Avoid using shading/relocation that creates duplicate exported packages on the module path.",
            ),
            cautions=(
                "Moving only one class may not fix resources, services, or generated package-info/module-info conflicts.",
                "A class path layout that worked before Java 9 may fail on the module path.",
            ),
            docs=(JEP_261, java_man, javac_man, jdeps_man),
        ),
        ModuleIssue(
            key="services",
            title="ServiceLoader, uses, and provides declarations",
            aliases=("service", "serviceloader", "uses", "provides", "provider"),
            first_checks=(
                "Identify the service interface, provider class, and module containing each.",
                "Check whether the consumer module declares uses and the provider module declares provides ... with ... .",
                "Confirm the provider module is resolved at run time.",
            ),
            fixes_to_consider=(
                "Add uses to modules that call ServiceLoader for a service.",
                "Add provides with the provider implementation in the provider module descriptor.",
                "Use --bind-services with jlink when building images that need service provider binding.",
            ),
            cautions=(
                "Class path META-INF/services behavior and module descriptor service declarations are related but not identical deployment shapes.",
                "Providers that are not resolved cannot be discovered by ServiceLoader.",
            ),
            docs=(jls("7.7.3", version), service_loader, doc("docs/specs/man/jlink.html", version)),
        ),
        ModuleIssue(
            key="jlink-runtime-image",
            title="jlink custom runtime image module graph",
            aliases=("jlink", "runtime image", "custom runtime", "missing module", "bind services"),
            first_checks=(
                "Use jdeps to identify required modules for the application and dependencies.",
                "Check --module-path, --add-modules, service binding, and launcher configuration.",
                "Verify the generated image on the same operating system and architecture it will be deployed to.",
            ),
            fixes_to_consider=(
                "Add missing root modules explicitly when they are not discovered from the main module.",
                "Use --bind-services only when the image should include service providers.",
                "Keep reproducible image inputs under build automation rather than manual command lines.",
            ),
            cautions=(
                "A custom image omits modules not in the resolved graph; reflective or service-loaded code can reveal missing modules later.",
                "Images are platform-specific and should be built for each target platform.",
            ),
            docs=(doc("docs/specs/man/jlink.html", version), jdeps_man, JEP_261),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, ModuleIssue]:
    index: dict[str, ModuleIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> ModuleIssue:
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
        raise ValueError(f"ambiguous module issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown module issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[ModuleIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: ModuleIssue) -> str:
    lines = [issue.title, f"Key: {issue.key}", "", "First checks:"]
    lines.extend(f"{index}. {check}" for index, check in enumerate(issue.first_checks, start=1))
    lines.extend(["", "Fixes to consider:"])
    lines.extend(f"- {item}" for item in issue.fixes_to_consider)
    lines.extend(["", "Cautions:"])
    lines.extend(f"- {item}" for item in issue.cautions)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in issue.docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue", nargs="?", help="Module issue key or alias")
    parser.add_argument("--list", action="store_true", help="List known module issue keys")
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
