# Java Tutor Codex Skill

`java-tutor` is a Codex skill for learning, debugging, reviewing, modernizing, and explaining Java with official documentation links.

The skill is designed for beginners through senior Java developers. It routes answers to the right official source: Oracle Java SE API docs, the Java Language Specification, the Java Virtual Machine Specification, OpenJDK JEPs, Oracle release notes, dev.java, and Oracle Java Tutorials.

## What It Does

- Explains Java concepts interactively at the user's level.
- Fixes Java compile errors, runtime exceptions, test failures, and build issues.
- Reviews Java code for correctness, compatibility, concurrency, resources, and maintainability.
- Helps migrate and modernize Java projects while respecting the configured source/target version.
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

Optionally check official Java source URLs:

```powershell
python .\scripts\verify_project.py --check-links
```

Run the lower-level validation and script tests:

```powershell
python C:\Users\LENOVO\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\java-tutor
python -m unittest discover -s tests
```

## Source Freshness

The bundled source map was checked against official Java documentation on 2026-06-13. The skill instructs Codex to browse official sources for any answer involving latest releases, support status, security updates, licensing, or preview/incubator status.
