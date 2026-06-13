# Java Tutor Codex Skill

`java-tutor` is a Codex skill for learning, debugging, reviewing, modernizing, and explaining Java with official documentation links.

The skill is designed for beginners through senior Java developers. It routes answers to the right official source: Oracle Java SE API docs, the Java Language Specification, the Java Virtual Machine Specification, OpenJDK JEPs, Oracle release notes, dev.java, and Oracle Java Tutorials.

## What It Does

- Explains Java concepts interactively at the user's level.
- Builds official-doc-backed learning paths with `java-tutor/scripts/java_learning_path.py`.
- Fixes Java compile errors, runtime exceptions, test failures, and build issues.
- Checks Java feature compatibility with `java-tutor/scripts/java_feature_compat.py`.
- Routes JDK tool questions to official manuals with `java-tutor/scripts/java_jdk_tool.py`.
- Triage JVM launcher flags with `java-tutor/scripts/java_jvm_option.py`.
- Triage Java class loading, classpath/module-path, resource lookup, ServiceLoader, and duplicate-class issues with `java-tutor/scripts/java_classloading_triage.py`.
- Routes language-rule questions to exact JLS sections with `java-tutor/scripts/java_language_rule.py`.
- Triage collections, Optional, and stream issues with `java-tutor/scripts/java_collections_triage.py`.
- Triage common `javac` diagnostics with `java-tutor/scripts/java_compile_error_triage.py`.
- Triage Java generics, wildcards, type inference, erasure, raw types, heap pollution, and bridge methods with `java-tutor/scripts/java_generics_triage.py`.
- Triage Java I/O, NIO, charset, serialization, and socket issues with `java-tutor/scripts/java_io_triage.py`.
- Triage Java HTTP Client request, response, async, timeout, TLS/proxy/auth, HTTP/2, and WebSocket issues with `java-tutor/scripts/java_http_triage.py`.
- Triage JDBC connection, SQL parameter, transaction, result set, exception, and date/time mapping issues with `java-tutor/scripts/java_jdbc_triage.py`.
- Triage Java concurrency symptoms with `java-tutor/scripts/java_concurrency_triage.py`.
- Triage Java date/time, time-zone, formatting, and legacy Date/Calendar issues with `java-tutor/scripts/java_datetime_triage.py`.
- Triage Java numeric precision, rounding, overflow, parsing, and equality issues with `java-tutor/scripts/java_numeric_triage.py`.
- Triage Java regex escaping, matching, grouping, replacement, performance, and split issues with `java-tutor/scripts/java_regex_triage.py`.
- Triage Java reflection, annotations, proxies, method handles, generic metadata, and record reflection with `java-tutor/scripts/java_reflection_triage.py`.
- Triage Java subprocess, `ProcessBuilder`, environment, pipe, timeout, decoding, and command-security issues with `java-tutor/scripts/java_process_triage.py`.
- Reviews Java code for correctness, compatibility, concurrency, resources, and maintainability.
- Generates official-doc-backed review checklists with `java-tutor/scripts/java_code_review_checklist.py`.
- Triage Java performance symptoms with `java-tutor/scripts/java_performance_triage.py`.
- Triage Java security risk areas with `java-tutor/scripts/java_security_triage.py`.
- Helps migrate and modernize Java projects while respecting the configured source/target version.
- Triage Java module system issues with `java-tutor/scripts/java_module_triage.py`.
- Plans deprecated, for-removal, removed, and internal API audits with `java-tutor/scripts/java_deprecation_audit.py`.
- Checks conflicting Java source, target, toolchain, and runtime hints with `java-tutor/scripts/java_version_consistency.py`.
- Ends substantial answers with direct official documentation links.

## Install

One-line install from GitHub for the current user on Windows:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; iwr https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; & $p
```

One-line install from GitHub for the current user on Linux and macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash
```

One-line update:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; iwr https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; & $p -Action Update
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash -s -- update
```

One-line status:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; iwr https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; & $p -Action Status
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash -s -- status
```

One-line uninstall:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; iwr https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; & $p -Action Uninstall
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash -s -- uninstall
```

Install for the current user:

```powershell
.\install.ps1
```

On macOS/Linux:

```bash
./install.sh
```

Update after pulling new changes:

```powershell
.\install.ps1 -Action Update
```

```bash
./install.sh update
```

Uninstall:

```powershell
.\install.ps1 -Action Uninstall
```

```bash
./install.sh uninstall
```

Status:

```powershell
.\install.ps1 -Action Status
```

```bash
./install.sh status
```

Status reports the install path and, for installs made with the current installer, the install timestamp and source.

Install globally for all users on the machine:

```powershell
.\install.ps1 -Scope Global
```

Linux:

```bash
sudo ./install.sh --global
```

macOS:

```bash
sudo ./install.sh --global
```

The global location defaults to `C:\ProgramData\Codex\skills\java-tutor` on Windows, `/usr/local/share/codex/skills/java-tutor` on Linux, and `/Library/Application Support/Codex/skills/java-tutor` on macOS. Set `CODEX_GLOBAL_HOME` before running the installer if your Codex setup uses a different global skill directory.

Or copy the `java-tutor` folder into a Codex skills directory:

```text
C:\Users\<you>\.codex\skills\java-tutor
```

Linux/macOS user installs default to:

```text
~/.codex/skills/java-tutor
```

Restart Codex after installation if the skill does not appear immediately.

## Usage

Example prompts:

```text
Use $java-tutor to explain Java records and link to the official docs.
Use $java-tutor to fix this NullPointerException.
Use $java-tutor to review this Java service for concurrency bugs.
Use $java-tutor to help migrate this project from Java 11 to Java 25.
```

## Verify

Run the project verifier:

```powershell
python .\scripts\verify_project.py
```

The verifier checks required skill files, metadata, documentation coverage, installer syntax, install/update/uninstall/status behavior in a temporary Codex home, and the Python tests.

Optionally check official Java source URLs:

```powershell
python .\scripts\verify_project.py --check-links
```

`--check-links` also checks Oracle page content for the current latest release, current LTS, current documentation versions, and JDK 26 release-note dates.

Run the lower-level validation and script tests:

```powershell
python C:\Users\LENOVO\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\java-tutor
python -m unittest discover -s tests
```

## Source Freshness

The bundled source map was checked against official Java documentation on 2026-06-13. The skill instructs Codex to browse official sources for any answer involving latest releases, support status, security updates, licensing, or preview/incubator status.

## License

This project is fully open source under the MIT License. See `LICENSE`.
