#!/usr/bin/env bash
set -euo pipefail

script_path="${BASH_SOURCE[0]:-}"
if [[ -n "$script_path" && -f "$script_path" ]]; then
  repo_root="$(cd "$(dirname "$script_path")" && pwd)"
else
  repo_root=""
fi
source_dir="${repo_root:+$repo_root/java-tutor}"
repo_url="${JAVA_TUTOR_ARCHIVE_URL:-https://github.com/yappologistic/Java-Tutor/archive/refs/heads/main.tar.gz}"
scope="user"
action="install"
temp_root=""
source_kind="local"
tmp_target=""
backup_target=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    install|update|uninstall|status)
      action="$1"
      ;;
    --user)
      scope="user"
      ;;
    --global)
      scope="global"
      ;;
    *)
      echo "Usage: $0 [install|update|uninstall|status] [--user|--global]" >&2
      exit 2
      ;;
  esac
  shift
done

if [[ "$scope" == "global" ]]; then
  if [[ -n "${CODEX_GLOBAL_HOME:-}" ]]; then
    codex_home="$CODEX_GLOBAL_HOME"
  else
    case "$(uname -s)" in
      Darwin)
        codex_home="/Library/Application Support/Codex"
        ;;
      Linux)
        codex_home="/usr/local/share/codex"
        ;;
      *)
        codex_home="/usr/local/share/codex"
        ;;
    esac
  fi
else
  codex_home="${CODEX_HOME:-$HOME/.codex}"
fi
skills_dir="$codex_home/skills"
target="$skills_dir/java-tutor"

if [[ "$action" == "status" ]]; then
  if [[ -f "$target/SKILL.md" ]]; then
    echo "java-tutor ($scope scope) is installed at $target"
    if [[ -f "$target/.install-info" ]]; then
      installed_at="$(awk -F= '$1 == "installedAtUtc" { sub($1 FS, ""); print; exit }' "$target/.install-info")"
      installed_from="$(awk -F= '$1 == "source" { sub($1 FS, ""); print; exit }' "$target/.install-info")"
      echo "Installed at: ${installed_at:-unknown}"
      echo "Installed from: ${installed_from:-unknown}"
    fi
  else
    echo "java-tutor ($scope scope) is not installed at $target"
  fi
  exit 0
fi

if [[ "$action" == "uninstall" ]]; then
  if [[ -d "$target" ]]; then
    rm -rf "$target"
    echo "Uninstalled java-tutor ($scope scope) from $target"
  else
    echo "java-tutor ($scope scope) is not installed at $target"
  fi
  exit 0
fi

cleanup() {
  if [[ -n "$temp_root" && -d "$temp_root" ]]; then
    rm -rf "$temp_root"
  fi
  if [[ -n "$tmp_target" && -d "$tmp_target" ]]; then
    rm -rf "$tmp_target"
  fi
}
trap cleanup EXIT

if [[ -z "$source_dir" || ! -d "$source_dir" ]]; then
  source_kind="archive"
  temp_root="$(mktemp -d)"
  archive="$temp_root/java-tutor.tar.gz"
  if [[ -f "$repo_url" ]]; then
    cp "$repo_url" "$archive"
  elif command -v curl >/dev/null 2>&1; then
    curl -fsSL "$repo_url" -o "$archive"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$archive" "$repo_url"
  else
    echo "Cannot download repo archive: curl or wget is required" >&2
    exit 1
  fi
  tar -xzf "$archive" -C "$temp_root"
  source_dir="$temp_root/Java-Tutor-main/java-tutor"
fi

if [[ ! -d "$source_dir" ]]; then
  echo "Cannot find skill folder: $source_dir" >&2
  exit 1
fi

mkdir -p "$skills_dir"
case "$target" in
  "$skills_dir"/java-tutor) ;;
  *)
    echo "Refusing to modify unexpected install target: $target" >&2
    exit 1
    ;;
esac

tmp_target="$(mktemp -d "$skills_dir/.java-tutor.tmp.XXXXXX")"
rmdir "$tmp_target"
cp -R "$source_dir" "$tmp_target"
if [[ ! -f "$tmp_target/SKILL.md" ]]; then
  echo "Install payload is missing SKILL.md" >&2
  exit 1
fi

license_source=""
if [[ -n "$repo_root" && -f "$repo_root/LICENSE" ]]; then
  license_source="$repo_root/LICENSE"
elif [[ "$source_kind" == "archive" && -f "$temp_root/Java-Tutor-main/LICENSE" ]]; then
  license_source="$temp_root/Java-Tutor-main/LICENSE"
fi
if [[ -n "$license_source" ]]; then
  cp "$license_source" "$tmp_target/LICENSE"
fi

if [[ "$source_kind" == "archive" ]]; then
  install_source="$repo_url"
else
  install_source="$source_dir"
fi
{
  echo "skill=java-tutor"
  echo "scope=$scope"
  echo "installedAtUtc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "source=$install_source"
} > "$tmp_target/.install-info"
find "$tmp_target" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$tmp_target" -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

if [[ -d "$target" ]]; then
  backup_target="$skills_dir/.java-tutor.backup.$$"
  rm -rf "$backup_target"
  mv "$target" "$backup_target"
fi

if ! mv "$tmp_target" "$target"; then
  if [[ -n "$backup_target" && -d "$backup_target" ]]; then
    mv "$backup_target" "$target"
  fi
  echo "Failed to replace installed java-tutor skill" >&2
  exit 1
fi
tmp_target=""
if [[ -n "$backup_target" && -d "$backup_target" ]]; then
  rm -rf "$backup_target"
fi

echo "$action completed for java-tutor ($scope scope) at $target"
