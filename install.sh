#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_dir="$repo_root/java-tutor"
scope="user"

if [[ "${1:-}" == "--global" ]]; then
  scope="global"
elif [[ "${1:-}" != "" && "${1:-}" != "--user" ]]; then
  echo "Usage: $0 [--user|--global]" >&2
  exit 2
fi

if [[ ! -d "$source_dir" ]]; then
  echo "Cannot find skill folder: $source_dir" >&2
  exit 1
fi

if [[ "$scope" == "global" ]]; then
  codex_home="${CODEX_GLOBAL_HOME:-/usr/local/share/codex}"
else
  codex_home="${CODEX_HOME:-$HOME/.codex}"
fi
skills_dir="$codex_home/skills"
target="$skills_dir/java-tutor"

mkdir -p "$skills_dir"
rm -rf "$target"
cp -R "$source_dir" "$target"
find "$target" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$target" -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

echo "Installed java-tutor ($scope scope) to $target"
