#!/usr/bin/env python3
"""Generate likely official Java documentation links."""

from __future__ import annotations

import argparse
import sys


DEFAULT_VERSION = "25"

MODULE_PREFIXES = {
    "java.applet.": "java.desktop",
    "java.awt.datatransfer.": "java.datatransfer",
    "java.awt.": "java.desktop",
    "java.beans.": "java.desktop",
    "java.datatransfer.": "java.datatransfer",
    "java.desktop.": "java.desktop",
    "java.instrument.": "java.instrument",
    "java.logging.": "java.logging",
    "java.management.": "java.management",
    "java.naming.": "java.naming",
    "java.net.http.": "java.net.http",
    "java.prefs.": "java.prefs",
    "java.rmi.": "java.rmi",
    "java.scripting.": "java.scripting",
    "java.security.jgss.": "java.security.jgss",
    "java.sql.": "java.sql",
    "java.transaction.xa.": "java.transaction.xa",
    "java.xml.crypto.": "java.xml.crypto",
    "java.xml.": "java.xml",
    "java.": "java.base",
    "javax.annotation.processing.": "java.compiler",
    "javax.lang.model.": "java.compiler",
    "javax.crypto.": "java.base",
    "javax.net.": "java.base",
    "javax.security.auth.kerberos.": "java.security.jgss",
    "javax.security.": "java.base",
    "javax.sql.": "java.sql",
    "javax.xml.": "java.xml",
    "org.w3c.dom.": "java.xml",
    "org.xml.sax.": "java.xml",
}


def infer_module(symbol: str) -> str:
    for prefix, module in sorted(MODULE_PREFIXES.items(), key=lambda item: len(item[0]), reverse=True):
        if symbol.startswith(prefix):
            return module
    return "java.base"


def api_path(class_name: str) -> str:
    parts = class_name.split(".")
    package_parts: list[str] = []
    class_parts: list[str] = []
    for part in parts:
        if class_parts or (part and part[0].isupper()):
            class_parts.append(part)
        else:
            package_parts.append(part)
    if not class_parts:
        return class_name.replace(".", "/")
    return "/".join([*package_parts, ".".join(class_parts)])


def api_link(symbol: str, version: str) -> str:
    cleaned = symbol.strip()
    if cleaned.endswith(".*"):
        package = cleaned[:-2].replace(".", "/")
        module = infer_module(cleaned[:-2])
        return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/{module}/{package}/package-summary.html"

    class_name, separator, member = cleaned.partition("#")
    module = infer_module(class_name)
    path = api_path(class_name)
    link = f"https://docs.oracle.com/en/java/javase/{version}/docs/api/{module}/{path}.html"
    if separator:
        link += f"#{member}"
    return link


def jls_link(section: str, version: str) -> str:
    chapter = section.split(".")[0]
    return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/jls-{chapter}.html#jls-{section}"


def jvms_link(section: str, version: str) -> str:
    chapter = section.split(".")[0]
    return f"https://docs.oracle.com/javase/specs/jvms/se{version}/html/jvms-{chapter}.html#jvms-{section}"


def build_link(kind: str, target: str | None, version: str) -> str:
    if kind == "api":
        if not target:
            raise ValueError("api requires a class, package.*, or package symbol")
        return api_link(target, version)
    if kind == "jls":
        if not target:
            return f"https://docs.oracle.com/javase/specs/jls/se{version}/html/index.html"
        return jls_link(target, version)
    if kind == "jvms":
        if not target:
            return f"https://docs.oracle.com/javase/specs/jvms/se{version}/html/index.html"
        return jvms_link(target, version)
    if kind == "jep":
        if not target:
            return "https://openjdk.org/jeps/0"
        return f"https://openjdk.org/jeps/{target}"
    if kind == "release-notes":
        return f"https://www.oracle.com/java/technologies/javase/{version}all-relnotes.html"
    if kind == "docs":
        return f"https://docs.oracle.com/en/java/javase/{version}/"
    if kind == "tutorial":
        return "https://docs.oracle.com/javase/tutorial/"
    if kind == "learn":
        return "https://dev.java/learn/"
    if kind == "downloads":
        return "https://www.oracle.com/java/technologies/downloads/"
    raise ValueError(f"unknown kind: {kind}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "kind",
        choices=["api", "jls", "jvms", "jep", "release-notes", "docs", "tutorial", "learn", "downloads"],
    )
    parser.add_argument("target", nargs="?")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE version, for example 25 or 21")
    args = parser.parse_args(argv)

    try:
        print(build_link(args.kind, args.target, args.version))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
