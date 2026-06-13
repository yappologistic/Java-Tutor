#!/usr/bin/env python3
"""Suggest Java project verification commands without running them."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any


def command_string(parts: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(parts)
    return shlex.join(parts)


def command_item(scope: str, argv: list[str], reason: str) -> dict[str, Any]:
    return {"scope": scope, "argv": argv, "command": command_string(argv), "reason": reason}


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def gradle_executable(root: Path) -> str:
    if os.name == "nt" and (root / "gradlew.bat").is_file():
        return ".\\gradlew.bat"
    if (root / "gradlew").is_file():
        return "./gradlew"
    return "gradle"


def maven_executable(root: Path) -> str:
    if os.name == "nt" and (root / "mvnw.cmd").is_file():
        return ".\\mvnw.cmd"
    if (root / "mvnw").is_file():
        return "./mvnw"
    return "mvn"


def has_gradle(root: Path) -> bool:
    return any((root / name).is_file() for name in ["build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"])


def has_maven(root: Path) -> bool:
    return (root / "pom.xml").is_file()


def looks_like_test(path: Path) -> bool:
    name = path.stem
    return name.endswith("Test") or name.endswith("Tests") or name.startswith("Test")


def class_name_from_path(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return path.stem
    match = re.search(r"^\s*package\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*;", text, flags=re.MULTILINE)
    return f"{match.group(1)}.{path.stem}" if match else path.stem


def fallback_java_files(root: Path) -> list[Path]:
    ignored_dirs = {"build", "target", "out", ".gradle", ".git"}
    files = [
        path
        for path in root.rglob("*.java")
        if not any(part in ignored_dirs for part in path.relative_to(root).parts[:-1])
    ]
    return sorted(files)


def suggest_commands(root: Path, changed_file: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    changed_path = (root / changed_file).resolve() if changed_file else None
    if changed_path and not is_relative_to(changed_path, root):
        changed_path = None
    commands: list[dict[str, Any]] = []

    if has_maven(root):
        mvn = maven_executable(root)
        if changed_path and changed_path.suffix == ".java" and looks_like_test(changed_path):
            commands.append(command_item("narrow", [mvn, f"-Dtest={class_name_from_path(changed_path)}", "test"], "Run the changed Maven test class only."))
        commands.extend(
            [
                command_item("compile", [mvn, "test-compile"], "Compile production and test sources."),
                command_item("broad", [mvn, "test"], "Run the Maven test suite."),
            ]
        )
    elif has_gradle(root):
        gradle = gradle_executable(root)
        if changed_path and changed_path.suffix == ".java" and looks_like_test(changed_path):
            commands.append(command_item("narrow", [gradle, "test", "--tests", class_name_from_path(changed_path)], "Run the changed Gradle test class only."))
        commands.extend(
            [
                command_item("compile", [gradle, "compileJava", "compileTestJava"], "Compile Gradle production and test sources."),
                command_item("broad", [gradle, "test"], "Run the Gradle test suite."),
            ]
        )
    else:
        java_files = fallback_java_files(root)
        if changed_path and changed_path.suffix == ".java":
            commands.append(command_item("single-file", ["javac", str(changed_path)], "Compile the changed Java file directly."))
        elif java_files:
            commands.append(command_item("single-file", ["javac", str(java_files[0])], "Compile a top-level Java file directly."))

    return {
        "root": str(root),
        "changed_file": str(changed_path) if changed_path else None,
        "commands": commands,
    }


def render_text(result: dict[str, Any]) -> str:
    if not result["commands"]:
        return "No Java verification commands detected. Inspect the project build files manually."
    lines = ["Suggested verification commands:"]
    for item in result["commands"]:
        lines.append(f"- [{item['scope']}] `{item['command']}` - {item['reason']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Project root to inspect")
    parser.add_argument("--changed-file", help="Optional changed Java file for targeted verification")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    result = suggest_commands(Path(args.path), args.changed_file)
    print(json.dumps(result, indent=2) if args.json else render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
