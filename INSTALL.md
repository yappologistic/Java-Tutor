# Installation

## One-Line Commands From GitHub

Install for the current user:

Windows:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; iwr https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; & $p
```

Linux/macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash
```

Update:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; iwr https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; & $p -Action Update
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash -s -- update
```

Status:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; iwr https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; & $p -Action Status
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash -s -- status
```

Uninstall:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; iwr https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; & $p -Action Uninstall
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash -s -- uninstall
```

Add `-Scope Global` on Windows or `--global` on macOS/Linux for global install/update/uninstall.

## Windows

Install for the current user:

```powershell
.\install.ps1
```

The script copies `java-tutor` to:

```text
$env:CODEX_HOME\skills\java-tutor
```

If `CODEX_HOME` is not set, it uses:

```text
$HOME\.codex\skills\java-tutor
```

Install globally for all users:

```powershell
.\install.ps1 -Scope Global
```

The global Windows target is:

```text
C:\ProgramData\Codex\skills\java-tutor
```

Set `CODEX_GLOBAL_HOME` to override the global Codex home before running the installer.

## macOS/Linux

Install for the current user:

```bash
./install.sh
```

The script copies `java-tutor` to `${CODEX_HOME:-$HOME/.codex}/skills/java-tutor`.

Install globally for all users:

```bash
sudo ./install.sh --global
```

The global Unix target is:

Linux:

```text
/usr/local/share/codex/skills/java-tutor
```

macOS:

```text
/Library/Application Support/Codex/skills/java-tutor
```

Set `CODEX_GLOBAL_HOME` to override the global Codex home before running the installer.

## Manual Install

Copy the `java-tutor` folder into a Codex skills directory, then restart Codex if needed.

## Update

Pull the latest repository changes and run:

```powershell
.\install.ps1 -Action Update
```

```bash
./install.sh update
```

The installer replaces the installed `java-tutor` folder.

## Uninstall

```powershell
.\install.ps1 -Action Uninstall
```

```bash
./install.sh uninstall
```

## Status

```powershell
.\install.ps1 -Action Status
```

```bash
./install.sh status
```

## Verify Installers and Skill Files

Run:

```powershell
python .\scripts\verify_project.py
```

This checks required skill files, metadata, documentation coverage, installer syntax, install/update/uninstall/status behavior in a temporary Codex home, and the Python tests. Run with `--check-links` to verify the official Java documentation URLs are reachable.
