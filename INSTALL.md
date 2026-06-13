# Installation

## One-Line Commands From GitHub

One-line install for the current user. By default these commands track `main`, so they install the latest repository state.

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; powershell -NoProfile -ExecutionPolicy Bypass -File $p
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash
```

One-line update:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; powershell -NoProfile -ExecutionPolicy Bypass -File $p -Action Update
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash -s -- update
```

Status:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; powershell -NoProfile -ExecutionPolicy Bypass -File $p -Action Status
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash -s -- status
```

One-line uninstall:

```powershell
$p="$env:TEMP\java-tutor-install.ps1"; Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.ps1 -OutFile $p; powershell -NoProfile -ExecutionPolicy Bypass -File $p -Action Uninstall
```

```bash
curl -fsSL https://raw.githubusercontent.com/yappologistic/Java-Tutor/main/install.sh | bash -s -- uninstall
```

Add `-Scope Global` on Windows or `--global` on macOS/Linux for global install/update/uninstall.

Pinned release install after a tag exists:

```powershell
$tag="v1.0.0"; $p="$env:TEMP\java-tutor-install.ps1"; Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/yappologistic/Java-Tutor/$tag/install.ps1" -OutFile $p; powershell -NoProfile -ExecutionPolicy Bypass -File $p -Ref $tag
```

```bash
tag=v1.0.0; curl -fsSL "https://raw.githubusercontent.com/yappologistic/Java-Tutor/$tag/install.sh" | bash -s -- --ref "$tag"
```

Use `JAVA_TUTOR_REF` instead of `--ref`/`-Ref` in automation if environment variables fit your install tooling better.

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
bash ./install.sh
```

The script copies `java-tutor` to `${CODEX_HOME:-$HOME/.codex}/skills/java-tutor`.

Install globally for all users:

```bash
sudo bash ./install.sh --global
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
bash ./install.sh update
```

The installer replaces the installed `java-tutor` folder.

## Uninstall

```powershell
.\install.ps1 -Action Uninstall
```

```bash
bash ./install.sh uninstall
```

## Status

```powershell
.\install.ps1 -Action Status
```

```bash
bash ./install.sh status
```

Status reports the install path and, for installs made with the current installer, the install timestamp and source.

## Verify Installers and Skill Files

Run:

```powershell
python .\scripts\verify_project.py
```

This checks required skill files, metadata, documentation coverage, installer syntax, install/update/uninstall/status behavior in a temporary Codex home, and the Python tests. Run with `--check-links` to verify the official Java documentation URLs are reachable.
