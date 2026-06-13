# Installation

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

```text
/usr/local/share/codex/skills/java-tutor
```

Set `CODEX_GLOBAL_HOME` to override the global Codex home before running the installer.

## Manual Install

Copy the `java-tutor` folder into a Codex skills directory, then restart Codex if needed.

## Update

Pull the latest repository changes and run the installer again. The installer replaces the installed `java-tutor` folder.
