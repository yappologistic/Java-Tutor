#!/usr/bin/env python3
"""Verify the Java Tutor skill project without local Codex-only tooling."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "java-tutor"
REQUIRED_FILES = [
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "agents" / "openai.yaml",
    SKILL_DIR / "references" / "source-map.md",
    SKILL_DIR / "references" / "teaching-workflows.md",
    SKILL_DIR / "scripts" / "java_doc_link.py",
    SKILL_DIR / "scripts" / "java_project_info.py",
    ROOT / "README.md",
    ROOT / "INSTALL.md",
    ROOT / "install.ps1",
    ROOT / "install.sh",
    ROOT / ".gitattributes",
    ROOT / ".gitignore",
]
OFFICIAL_URLS = [
    "https://docs.oracle.com/en/java/javase/",
    "https://www.oracle.com/java/technologies/downloads/",
    "https://docs.oracle.com/en/java/javase/26/",
    "https://docs.oracle.com/en/java/javase/25/docs/api/",
    "https://docs.oracle.com/javase/specs/jls/se25/html/index.html",
    "https://docs.oracle.com/javase/specs/jvms/se25/html/index.html",
    "https://www.oracle.com/java/technologies/javase/26all-relnotes.html",
    "https://www.oracle.com/java/technologies/javase/25all-relnotes.html",
    "https://openjdk.org/jeps/0",
    "https://dev.java/learn/",
    "https://docs.oracle.com/javase/tutorial/",
]


def run(command: list[str], *, timeout: int = 30) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, timeout=timeout, check=True)


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        raise AssertionError("Missing required files:\n" + "\n".join(str(path) for path in missing))


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        raise AssertionError("SKILL.md must start with YAML frontmatter")

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            raise AssertionError(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def check_skill_metadata() -> None:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    fields = parse_frontmatter(text)
    if fields.get("name") != "java-tutor":
        raise AssertionError("SKILL.md frontmatter name must be java-tutor")
    description = fields.get("description", "")
    if len(description) < 120:
        raise AssertionError("SKILL.md description is too short for reliable triggering")
    for token in ["Java", "debug", "official", "JLS", "JEP"]:
        if token not in description:
            raise AssertionError(f"SKILL.md description should mention {token!r}")
    if "TODO" in text:
        raise AssertionError("SKILL.md still contains TODO text")

    agent_yaml = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if "Use $java-tutor" not in agent_yaml:
        raise AssertionError("agents/openai.yaml default_prompt must mention $java-tutor")


def check_docs() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    install = (ROOT / "INSTALL.md").read_text(encoding="utf-8")
    combined = readme + "\n" + install
    for phrase in [
        "One-line install",
        "One-line update",
        "One-line uninstall",
        "Windows",
        "Linux",
        "macOS",
        "CODEX_GLOBAL_HOME",
    ]:
        if phrase not in combined:
            raise AssertionError(f"Documentation should mention {phrase!r}")


def check_shell_syntax() -> None:
    shell = os.environ.get("SHELLCHECK_SH", "sh")
    try:
        run([shell, "-n", "./install.sh"])
    except FileNotFoundError:
        print("Skipping install.sh syntax check: sh is not available")


def run_tests() -> None:
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])


def check_official_links() -> None:
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "java-tutor-project-verifier/1.0")]
    for url in OFFICIAL_URLS:
        print("+ HEAD", url)
        request = urllib.request.Request(url, method="HEAD")
        try:
            with opener.open(request, timeout=20) as response:
                status = response.status
        except urllib.error.HTTPError as exc:
            if exc.code in {403, 405}:
                request = urllib.request.Request(url, method="GET")
                with opener.open(request, timeout=20) as response:
                    status = response.status
            else:
                raise
        if status >= 400:
            raise AssertionError(f"{url} returned HTTP {status}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-links", action="store_true", help="Check reachability of official Java source URLs")
    args = parser.parse_args(argv)

    check_required_files()
    check_skill_metadata()
    check_docs()
    check_shell_syntax()
    run_tests()
    if args.check_links:
        check_official_links()
    print("Project verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
