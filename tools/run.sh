#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
required_version="$(<tools/godot-version.txt)"
if [[ -n "${GODOT_BIN:-}" ]]; then
  godot_bin="$GODOT_BIN"
elif [[ -n "${GODOT_EXE:-}" ]]; then
  godot_bin="$GODOT_EXE"
elif command -v godot >/dev/null 2>&1; then
  godot_bin=godot
elif [[ -x "work/runtime/Godot_v${required_version}-stable_linux.x86_64" ]]; then
  godot_bin="work/runtime/Godot_v${required_version}-stable_linux.x86_64"
elif [[ -x "work/runtime/Godot_v${required_version}-stable_win64_console.exe" ]]; then
  godot_bin="work/runtime/Godot_v${required_version}-stable_win64_console.exe"
else
  echo "Godot $required_version stable requis. Définir GODOT_BIN ou GODOT_EXE avec son chemin." >&2
  exit 1
fi

# GODOT_EXE may come from Windows; command arguments themselves are not translated by WSL.
if [[ "$godot_bin" =~ ^[A-Za-z]:[\\/] || "$godot_bin" == \\\\* ]]; then
  command -v wslpath >/dev/null || { echo 'wslpath requis pour ce chemin Windows.' >&2; exit 1; }
  godot_bin="$(wslpath -u "$godot_bin")"
fi
godot_bin="$(command -v "$godot_bin")" || { echo 'Binaire Godot introuvable ou non exécutable.' >&2; exit 1; }
if [[ "$godot_bin" != /* ]]; then godot_bin="$PWD/$godot_bin"; fi
engine_version="$("$godot_bin" --headless --version)"
engine_version="${engine_version//$'\r'/}"
if [[ "$engine_version" != "$required_version.stable."* || "$engine_version" == *$'\n'* ]]; then
  echo "Version refusée : $engine_version ; attendu : $required_version.stable.*" >&2
  exit 1
fi

# Resolve once in test.sh so its isolation matches the engine actually selected.
if [[ "${1:-}" == --print-engine ]]; then
  printf '%s\n' "$godot_bin"
  exit 0
fi
project_path="$PWD"
if [[ "${godot_bin,,}" == *.exe ]]; then
  command -v wslpath >/dev/null || { echo 'wslpath requis pour lancer Godot Windows depuis Bash.' >&2; exit 1; }
  project_path="$(wslpath -w "$project_path")"
fi
mkdir -p work
touch work/.gdignore
exec "$godot_bin" --path "$project_path" "$@"
