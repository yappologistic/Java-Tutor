#!/usr/bin/env python3
"""Infer Java version hints from common project files."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


VERSION_PATTERNS = [
    r"sourceCompatibility\s*=\s*['\"]?([0-9][0-9.]*)",
    r"targetCompatibility\s*=\s*['\"]?([0-9][0-9.]*)",
    r"JavaVersion\.VERSION_([0-9_]+)",
    r"languageVersion\s*=\s*JavaLanguageVersion\.of\((\d+)\)",
    r"--release\s+(\d+)",
]
JAVA_TAG_PATTERNS = [
    r"(?:java|jdk|jre|openjdk|temurin|zulu|corretto|graalvm)[^\s:.-]*[-_:]?(\d{1,2})",
    r"(\d{1,2})(?:-jdk|-jre)",
]
COMPILE_HINT_TOKENS = (
    "compiler",
    "source",
    "target",
    "release",
    "gradle-java-version",
    "java.version",
)
RUNTIME_HINT_TOKENS = (
    "docker",
    "java-version-file",
    "sdkman",
    "java.home",
)
PROJECT_FILENAMES = {
    ".java-version",
    ".sdkmanrc",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "gradle.properties",
    "Dockerfile",
}
SKIP_DIR_NAMES = {
    ".git",
    ".gradle",
    ".idea",
    ".mvn",
    "build",
    "dist",
    "node_modules",
    "out",
    "target",
}


def normalize_version(value: str) -> str:
    value = value.strip().strip('"').strip("'").replace("_", ".")
    if value.startswith("1."):
        return value.split(".", 1)[1]
    java_distribution_match = re.search(r"(?:java|jdk|jre|openjdk|temurin|zulu|corretto|graalvm)[^\d]*(\d{1,2})", value)
    if java_distribution_match:
        return java_distribution_match.group(1)
    leading_version_match = re.match(r"(\d{1,2})(?:[._-]|$)", value)
    if leading_version_match:
        return leading_version_match.group(1)
    return value


def add_hint(hints: list[dict[str, str]], source: Path, kind: str, value: str) -> None:
    hints.append({"source": str(source), "kind": kind, "value": normalize_version(value)})


def discover_project_dirs(root: Path) -> list[Path]:
    discovered: list[Path] = []
    seen: set[Path] = set()
    for current, dir_names, file_names in os.walk(root):
        dir_names[:] = [name for name in dir_names if name not in SKIP_DIR_NAMES]
        current_path = Path(current)
        names = set(file_names)
        has_project_file = bool(PROJECT_FILENAMES & names) or any(name.startswith("Dockerfile.") for name in names)
        if has_project_file and current_path not in seen:
            discovered.append(current_path)
            seen.add(current_path)
    if root not in seen:
        discovered.insert(0, root)
    return discovered


def parse_java_version_file(root: Path, hints: list[dict[str, str]]) -> None:
    for name in [".java-version", ".sdkmanrc"]:
        path = root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if name == ".java-version":
            first = text.strip().splitlines()[0] if text.strip() else ""
            if first:
                add_hint(hints, path, "java-version-file", first)
        else:
            match = re.search(r"java\s*=\s*([^\s]+)", text)
            if match:
                add_hint(hints, path, "sdkman-java", match.group(1))


def parse_maven(root: Path, hints: list[dict[str, str]]) -> None:
    path = root / "pom.xml"
    if not path.is_file():
        return
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        return
    xml_root = tree.getroot()
    namespace = ""
    if xml_root.tag.startswith("{"):
        namespace = xml_root.tag.split("}", 1)[0] + "}"

    properties = xml_root.find(f"{namespace}properties")
    property_values: dict[str, str] = {}
    if properties is not None:
        for child in properties:
            key = child.tag.split("}", 1)[-1]
            value = (child.text or "").strip()
            if value:
                property_values[key] = value
            if key in {
                "java.version",
                "maven.compiler.release",
                "maven.compiler.source",
                "maven.compiler.target",
            } and value:
                add_hint(hints, path, key, value)

    for plugin in xml_root.findall(f".//{namespace}plugin"):
        artifact = plugin.findtext(f"{namespace}artifactId", default="")
        if artifact != "maven-compiler-plugin":
            continue
        config = plugin.find(f"{namespace}configuration")
        if config is None:
            continue
        for key in ["release", "source", "target"]:
            value = config.findtext(f"{namespace}{key}", default="").strip()
            if value:
                property_match = re.fullmatch(r"\$\{([^}]+)\}", value)
                if property_match and property_match.group(1) in property_values:
                    value = property_values[property_match.group(1)]
                add_hint(hints, path, f"maven-compiler-plugin.{key}", value)


def parse_gradle(root: Path, hints: list[dict[str, str]]) -> None:
    for name in ["build.gradle", "build.gradle.kts", "gradle.properties"]:
        path = root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if name == "gradle.properties":
            for key in ["java.version", "org.gradle.java.home"]:
                match = re.search(rf"^{re.escape(key)}\s*=\s*(.+)$", text, flags=re.MULTILINE)
                if match:
                    add_hint(hints, path, key, match.group(1))
            continue
        for pattern in VERSION_PATTERNS:
            for match in re.finditer(pattern, text):
                add_hint(hints, path, "gradle-java-version", match.group(1))


def parse_dockerfile(root: Path, hints: list[dict[str, str]]) -> None:
    for path in [root / "Dockerfile", *root.glob("Dockerfile.*")]:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"^\s*FROM\s+(?:--platform=\S+\s+)?(\S+)", text, flags=re.IGNORECASE | re.MULTILINE):
            image_ref = match.group(1).split("@", 1)[0]
            for pattern in JAVA_TAG_PATTERNS:
                tag_match = re.search(pattern, image_ref, flags=re.IGNORECASE)
                if tag_match:
                    add_hint(hints, path, "docker-base-image", tag_match.group(1))
                    break


def numeric_hint_versions(hints: list[dict[str, str]], tokens: tuple[str, ...] | None = None) -> list[int]:
    versions: list[int] = []
    for hint in hints:
        if tokens and not any(token in hint["kind"].lower() for token in tokens):
            continue
        if re.fullmatch(r"\d+", hint["value"]):
            versions.append(int(hint["value"]))
    return sorted(set(versions))


def infer_project_info(root: Path) -> dict[str, Any]:
    root = root.resolve()
    hints: list[dict[str, str]] = []
    for project_dir in discover_project_dirs(root):
        parse_java_version_file(project_dir, hints)
        parse_maven(project_dir, hints)
        parse_gradle(project_dir, hints)
        parse_dockerfile(project_dir, hints)
    numeric_versions = numeric_hint_versions(hints)
    compile_versions = numeric_hint_versions(hints, COMPILE_HINT_TOKENS)
    runtime_versions = numeric_hint_versions(hints, RUNTIME_HINT_TOKENS)
    language_version = str(min(compile_versions)) if compile_versions else (str(max(numeric_versions)) if numeric_versions else None)
    runtime_version = str(max(runtime_versions)) if runtime_versions else None
    return {
        "root": str(root),
        "detected_versions": [str(version) for version in numeric_versions],
        "language_version": language_version,
        "runtime_version": runtime_version,
        "highest_detected_version": str(max(numeric_versions)) if numeric_versions else None,
        "recommended_version": language_version,
        "hints": hints,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Project root to inspect")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args(argv)

    info = infer_project_info(Path(args.path))
    print(json.dumps(info, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
