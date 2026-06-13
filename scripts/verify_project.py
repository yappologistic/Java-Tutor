#!/usr/bin/env python3
"""Verify the Java Tutor skill project without local Codex-only tooling."""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "java-tutor"
REQUIRED_FILES = [
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "agents" / "openai.yaml",
    SKILL_DIR / "references" / "source-map.md",
    SKILL_DIR / "references" / "teaching-workflows.md",
    SKILL_DIR / "scripts" / "java_doc_link.py",
    SKILL_DIR / "scripts" / "java_exception_triage.py",
    SKILL_DIR / "scripts" / "java_migration_plan.py",
    SKILL_DIR / "scripts" / "java_project_info.py",
    SKILL_DIR / "scripts" / "java_topic_links.py",
    SKILL_DIR / "scripts" / "java_verify_commands.py",
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
    "https://docs.oracle.com/en/java/javase/25/migrate/index.html",
    "https://docs.oracle.com/javase/specs/jls/se25/html/index.html",
    "https://docs.oracle.com/javase/specs/jvms/se25/html/index.html",
    "https://www.oracle.com/java/technologies/javase/26all-relnotes.html",
    "https://www.oracle.com/java/technologies/javase/25all-relnotes.html",
    "https://openjdk.org/jeps/0",
    "https://dev.java/learn/",
    "https://docs.oracle.com/javase/tutorial/",
]
RELEASE_FACT_CHECKS = [
    {
        "name": "Oracle downloads latest release",
        "url": "https://www.oracle.com/java/technologies/downloads/",
        "required": ["JDK 26 is the latest release of the Java SE Platform"],
    },
    {
        "name": "Oracle downloads latest LTS",
        "url": "https://www.oracle.com/java/technologies/downloads/",
        "required": ["JDK 25 is the latest Long-Term Support (LTS) release of the Java SE Platform"],
    },
    {
        "name": "Oracle Java SE docs current versions",
        "url": "https://docs.oracle.com/en/java/javase/",
        "required": ["Current Java SE Versions", "JDK 26", "JDK 25", "JDK 21", "JDK 17", "JDK 11", "JDK 8"],
    },
    {
        "name": "Oracle JDK 26 release notes",
        "url": "https://www.oracle.com/java/technologies/javase/26all-relnotes.html",
        "required": ["JDK 26.0.1", "April 21, 2026", "JDK 26", "March 17, 2026"],
    },
]


def topic_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_topic_links
    finally:
        sys.path.pop(0)
    for topic in java_topic_links.TOPICS:
        yield from topic.links


def exception_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_exception_triage
    finally:
        sys.path.pop(0)
    for item in java_exception_triage.EXCEPTIONS:
        yield java_exception_triage.api_link(item.api_class, "25")


def run(command: list[str], *, timeout: int = 30) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, timeout=timeout, check=True)


def run_with_env(command: list[str], env: dict[str, str], *, timeout: int = 30) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, env=env, timeout=timeout, check=True)


def normalize_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())


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


def check_installers() -> None:
    with tempfile.TemporaryDirectory(prefix="java-tutor-verify-") as temp_dir:
        temp_home = Path(temp_dir) / "codex-home"
        skill_file = temp_home / "skills" / "java-tutor" / "SKILL.md"
        metadata_file = temp_home / "skills" / "java-tutor" / ".install-info"
        env = os.environ.copy()
        env["CODEX_HOME"] = str(temp_home)

        if os.name == "nt":
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            if not powershell:
                print("Skipping install.ps1 smoke test: PowerShell is not available")
                return
            run_with_env(
                [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\\install.ps1", "-Action", "Status"],
                env,
            )
            run_with_env([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\\install.ps1"], env)
            if not skill_file.is_file():
                raise AssertionError("install.ps1 did not install SKILL.md")
            if not metadata_file.is_file():
                raise AssertionError("install.ps1 did not write install metadata")
            run_with_env(
                [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\\install.ps1", "-Action", "Status"],
                env,
            )
            run_with_env(
                [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\\install.ps1", "-Action", "Update"],
                env,
            )
            if not skill_file.is_file():
                raise AssertionError("install.ps1 update removed SKILL.md")
            run_with_env(
                [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\\install.ps1", "-Action", "Uninstall"],
                env,
            )
            if skill_file.exists():
                raise AssertionError("install.ps1 uninstall left SKILL.md behind")
            return

        shell = shutil.which("bash") or shutil.which("sh")
        if not shell:
            print("Skipping install.sh smoke test: sh/bash is not available")
            return
        run_with_env([shell, "./install.sh", "status"], env)
        run_with_env([shell, "./install.sh"], env)
        if not skill_file.is_file():
            raise AssertionError("install.sh did not install SKILL.md")
        if not metadata_file.is_file():
            raise AssertionError("install.sh did not write install metadata")
        run_with_env([shell, "./install.sh", "status"], env)
        run_with_env([shell, "./install.sh", "update"], env)
        if not skill_file.is_file():
            raise AssertionError("install.sh update removed SKILL.md")
        run_with_env([shell, "./install.sh", "uninstall"], env)
        if skill_file.exists():
            raise AssertionError("install.sh uninstall left SKILL.md behind")


def run_tests() -> None:
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])


def check_official_links() -> None:
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "java-tutor-project-verifier/1.0")]
    for url in sorted(set([*OFFICIAL_URLS, *topic_urls(), *exception_urls()])):
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


def check_release_facts() -> None:
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "java-tutor-project-verifier/1.0")]
    for check in RELEASE_FACT_CHECKS:
        url = check["url"]
        print("+ FACT", check["name"], url)
        with opener.open(url, timeout=20) as response:
            content_type = response.headers.get_content_charset() or "utf-8"
            page = normalize_text(response.read().decode(content_type, errors="replace"))
        for required in check["required"]:
            if normalize_text(required) not in page:
                raise AssertionError(f"{check['name']} missing expected official text: {required!r}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-links", action="store_true", help="Check reachability of official Java source URLs")
    args = parser.parse_args(argv)

    check_required_files()
    check_skill_metadata()
    check_docs()
    check_shell_syntax()
    check_installers()
    run_tests()
    if args.check_links:
        check_official_links()
        check_release_facts()
    print("Project verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
