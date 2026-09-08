#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p work
touch work/.gdignore
if [[ -n "${GODOT_BIN:-}" ]]; then
  godot_bin="$GODOT_BIN"
elif command -v godot >/dev/null 2>&1; then
  godot_bin=godot
elif [[ -x work/runtime/Godot_v4.5.1-stable_linux.x86_64 ]]; then
  godot_bin=work/runtime/Godot_v4.5.1-stable_linux.x86_64
else
  echo 'Godot 4.5.1 requis. Définir GODOT_BIN avec son chemin.' >&2
  exit 1
fi
exec "$godot_bin" --path . "$@"
