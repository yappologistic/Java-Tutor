#!/usr/bin/env python3
"""Choose official JDK tool manuals and first checks for Java tooling tasks."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class JdkTool:
    key: str
    title: str
    aliases: tuple[str, ...]
    use_when: tuple[str, ...]
    first_checks: tuple[str, ...]
    common_options: tuple[str, ...]
    docs: tuple[str, ...]


def man_page(tool: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/specs/man/{tool}.html"


def troubleshoot_page(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/troubleshoot/{path}"


def tools(version: str = DEFAULT_VERSION) -> tuple[JdkTool, ...]:
    return (
        JdkTool(
            key="java",
            title="Java application launcher",
            aliases=("launcher", "runtime", "main", "classpath", "module path", "jvm option"),
            use_when=(
                "Running a class, module, JAR, or source file.",
                "Diagnosing class path, module path, system property, JVM option, or startup behavior.",
            ),
            first_checks=(
                "Capture the exact command, working directory, Java version, and full error output.",
                "Identify whether the app is launched by class name, module name, executable JAR, or source file.",
                "Separate application arguments from JVM options and launcher options.",
            ),
            common_options=("-cp / -classpath", "--module-path", "--module", "-jar", "-Dname=value", "--enable-preview"),
            docs=(man_page("java", version),),
        ),
        JdkTool(
            key="javac",
            title="Java compiler",
            aliases=("compile", "compiler", "source", "target", "release", "annotation processor"),
            use_when=(
                "Compiling Java source files or diagnosing compiler diagnostics.",
                "Checking source/release/target compatibility, class paths, module paths, or annotation processing.",
            ),
            first_checks=(
                "Capture the exact diagnostic, source file, compiler command, and configured Java release.",
                "Check whether --release, --source, --target, class path, and module path align.",
                "Identify annotation processors and generated sources before treating missing symbols as source bugs.",
            ),
            common_options=("--release", "--source", "--target", "-classpath", "--module-path", "-processor", "-Xlint"),
            docs=(man_page("javac", version),),
        ),
        JdkTool(
            key="jar",
            title="JAR archive tool",
            aliases=("archive", "manifest", "executable jar", "multi-release jar", "mrjar"),
            use_when=(
                "Creating, inspecting, updating, or validating JAR files.",
                "Working with manifests, executable JARs, services, or multi-release JARs.",
            ),
            first_checks=(
                "Inspect the archive contents before changing packaging.",
                "Check the manifest for Main-Class, Class-Path, Multi-Release, and service metadata.",
                "Confirm whether the JAR is intended for class path, module path, or both.",
            ),
            common_options=("--create", "--file", "--manifest", "--main-class", "--describe-module", "--validate"),
            docs=(man_page("jar", version),),
        ),
        JdkTool(
            key="javadoc",
            title="Javadoc documentation generator",
            aliases=("api docs", "doclint", "documentation generator", "javadocs"),
            use_when=(
                "Generating API documentation from Java source.",
                "Diagnosing doclint, module/package documentation, links, or custom doclet behavior.",
            ),
            first_checks=(
                "Capture the exact javadoc command and failing source or package.",
                "Check source path, module source path, class path, and external link configuration.",
                "Distinguish source compilation errors from documentation comment or doclint issues.",
            ),
            common_options=("-d", "-sourcepath", "--module-source-path", "-classpath", "-link", "-Xdoclint"),
            docs=(man_page("javadoc", version),),
        ),
        JdkTool(
            key="jshell",
            title="JShell interactive Java shell",
            aliases=("repl", "scratch", "interactive shell", "snippet"),
            use_when=(
                "Trying small Java snippets interactively.",
                "Demonstrating API behavior without creating a full project.",
            ),
            first_checks=(
                "Confirm snippets do not rely on project-only dependencies unless class path/module path is configured.",
                "Keep examples short and copyable, especially for beginner learning.",
                "Use the same Java version as the target concept when testing version-gated features.",
            ),
            common_options=("--class-path", "--module-path", "--add-modules", "--enable-preview", "/help", "/vars"),
            docs=(man_page("jshell", version),),
        ),
        JdkTool(
            key="jdeps",
            title="Java dependency analysis tool",
            aliases=("dependency analysis", "internal api", "module deps", "jdeps"),
            use_when=(
                "Analyzing class, package, module, or JDK-internal API dependencies.",
                "Planning migrations where removed modules, strong encapsulation, or module boundaries matter.",
            ),
            first_checks=(
                "Run against compiled classes or JARs, not just source files.",
                "Include all relevant class path or module path dependencies.",
                "Use the output to identify dependency direction and JDK-internal API usage before refactoring.",
            ),
            common_options=("--class-path", "--module-path", "--multi-release", "--jdk-internals", "--print-module-deps"),
            docs=(man_page("jdeps", version),),
        ),
        JdkTool(
            key="jdeprscan",
            title="Java deprecated API scanner",
            aliases=("deprecated api", "for removal", "deprecation scan", "deprecated scanner"),
            use_when=(
                "Finding deprecated APIs, APIs marked for removal, or migration risks in compiled artifacts.",
                "Preparing an upgrade checklist before moving to a newer JDK.",
            ),
            first_checks=(
                "Run against compiled classes or JARs produced by the project.",
                "Set --release to the target JDK version being evaluated.",
                "Treat findings as review input; verify replacements in current API docs and migration guides.",
            ),
            common_options=("--release", "--for-removal", "--list", "--class-path"),
            docs=(man_page("jdeprscan", version),),
        ),
        JdkTool(
            key="jlink",
            title="Custom runtime image tool",
            aliases=("runtime image", "custom runtime", "modules image", "jlink"),
            use_when=(
                "Creating a custom Java runtime image from modules.",
                "Reducing deployment footprint for modular applications or known module graphs.",
            ),
            first_checks=(
                "Confirm the application and dependencies have a clear module graph.",
                "Use jdeps to identify required modules before building an image.",
                "Check service binding, launchers, compression, and platform-specific image assumptions.",
            ),
            common_options=("--module-path", "--add-modules", "--output", "--launcher", "--bind-services", "--compress"),
            docs=(man_page("jlink", version), man_page("jdeps", version)),
        ),
        JdkTool(
            key="jpackage",
            title="Java application packaging tool",
            aliases=("installer", "native package", "app image", "package app", "jpackage"),
            use_when=(
                "Packaging Java applications as platform-specific app images or installers.",
                "Choosing packaging options for Windows, Linux, or macOS distribution.",
            ),
            first_checks=(
                "Identify the target operating system and package type before choosing options.",
                "Confirm the app image or runtime image inputs and main class/module are correct.",
                "Account for signing, icons, file associations, install directories, and CI platform limits separately.",
            ),
            common_options=("--type", "--input", "--main-jar", "--main-class", "--module", "--runtime-image", "--app-version"),
            docs=(man_page("jpackage", version),),
        ),
        JdkTool(
            key="jcmd",
            title="JVM diagnostic command tool",
            aliases=("diagnostic command", "thread dump", "heap dump", "jcmd", "vm flags"),
            use_when=(
                "Collecting diagnostics from a running JVM process.",
                "Getting thread dumps, heap information, VM flags, JFR control, or native memory summaries.",
            ),
            first_checks=(
                "Identify the target PID and make sure permissions allow attaching to it.",
                "Prefer low-impact diagnostic commands first on production systems.",
                "Treat thread dumps, heap dumps, and recordings as sensitive artifacts.",
            ),
            common_options=("help", "Thread.print", "GC.heap_info", "VM.flags", "JFR.start", "JFR.dump"),
            docs=(man_page("jcmd", version),),
        ),
        JdkTool(
            key="jfr",
            title="JDK Flight Recorder tool",
            aliases=("flight recorder", "recording", "profile", "jfr"),
            use_when=(
                "Inspecting, printing, summarizing, or viewing JDK Flight Recorder files.",
                "Analyzing runtime performance, allocation, thread, GC, and event evidence.",
            ),
            first_checks=(
                "Record enough workload context to make the events meaningful.",
                "Keep recordings bounded in duration and size for production systems.",
                "Redact or protect recordings because they may contain sensitive runtime data.",
            ),
            common_options=("print", "summary", "view", "metadata", "assemble", "disassemble"),
            docs=(man_page("jfr", version), troubleshoot_page("troubleshoot-performance-issues-using-jfr.html", version)),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def tool_index(version: str = DEFAULT_VERSION) -> dict[str, JdkTool]:
    index: dict[str, JdkTool] = {}
    for tool in tools(version):
        index[normalize(tool.key)] = tool
        index[normalize(tool.title)] = tool
        for alias in tool.aliases:
            index[normalize(alias)] = tool
    return index


def find_tool(query: str, version: str = DEFAULT_VERSION) -> JdkTool:
    normalized = normalize(query)
    index = tool_index(version)
    if normalized in index:
        return index[normalized]
    matches = [tool for key, tool in index.items() if normalized in key or key in normalized]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if unique_matches:
        options = ", ".join(tool.key for tool in unique_matches)
        raise ValueError(f"ambiguous JDK tool {query!r}; choose one of: {options}")
    available = ", ".join(tool.key for tool in tools(version))
    raise ValueError(f"unknown JDK tool {query!r}; available tools: {available}")


def official_urls(selected: Iterable[JdkTool]) -> tuple[str, ...]:
    urls: list[str] = []
    for tool in selected:
        urls.extend(tool.docs)
    return tuple(dict.fromkeys(urls))


def render_text(tool: JdkTool) -> str:
    lines = [tool.title, f"Key: {tool.key}", "", "Use when:"]
    lines.extend(f"- {item}" for item in tool.use_when)
    lines.extend(["", "First checks:"])
    lines.extend(f"{index}. {check}" for index, check in enumerate(tool.first_checks, start=1))
    lines.extend(["", "Common options:"])
    lines.extend(f"- {option}" for option in tool.common_options)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in tool.docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", nargs="?", help="JDK tool key or alias")
    parser.add_argument("--list", action="store_true", help="List known JDK tool keys")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        keys = [tool.key for tool in tools(args.version)]
        print(json.dumps(keys, indent=2) if args.json else "\n".join(keys))
        return 0

    if not args.tool:
        parser.error("tool is required unless --list is used")

    try:
        tool = find_tool(args.tool, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(tool)
        payload["official_docs"] = list(tool.docs)
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(tool))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
