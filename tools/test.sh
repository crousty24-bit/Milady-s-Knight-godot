#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for dependency in rg timeout mktemp; do
  command -v "$dependency" >/dev/null || { echo "Dépendance requise : $dependency" >&2; exit 1; }
done
mkdir -p work/test-results
results_dir="$(mktemp -d "$PWD/work/test-results/run-XXXXXXXX")"
printf 'Logs : %s\n' "$results_dir"
export GODOT_BIN
GODOT_BIN="$(timeout --kill-after=5 30 ./tools/run.sh --print-engine)"
printf '%s\n' "$GODOT_BIN" > "$results_dir/engine.txt"

# Separate user data before the editor import as well as before the test drivers.
if [[ "${GODOT_BIN,,}" == *.exe ]]; then
  command -v wslpath >/dev/null || { echo 'Dépendance requise pour Windows : wslpath' >&2; exit 1; }
  powershell_bin="$(command -v powershell.exe || true)"
  if [[ -z "$powershell_bin" ]]; then
    powershell_bin=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
  fi
  [[ -x "$powershell_bin" ]] || { echo 'PowerShell Windows introuvable ; ajouter powershell.exe au PATH.' >&2; exit 1; }
  windows_temp="$(timeout --kill-after=5 30 "$powershell_bin" -NoProfile -NonInteractive -Command '$godotTemp = [IO.Path]::GetTempPath(); $godotDrive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($godotTemp)); if ($godotDrive.DriveFormat -ne "NTFS") { throw "Le profil de tests Windows doit etre sur NTFS." }; $godotTemp')"
  windows_temp="${windows_temp//$'\r'/}"
  test_profile="$(mktemp -d "$(wslpath -u "$windows_temp")/milady-tests.XXXXXXXX")"
  export APPDATA="$test_profile/appdata" LOCALAPPDATA="$test_profile/localappdata"
  export MILADY_TEST_USER_ROOT="$APPDATA"
  # Replace only these entries; preserve every unrelated WSLENV variable and flag.
  IFS=: read -r -a shared_variables <<< "${WSLENV:-}"
  WSLENV=''
  for entry in "${shared_variables[@]}"; do
    case "${entry%%/*}" in APPDATA|LOCALAPPDATA|MILADY_TEST_USER_ROOT|'') continue ;; esac
    WSLENV="${WSLENV:+$WSLENV:}$entry"
  done
  export WSLENV="${WSLENV:+$WSLENV:}APPDATA/pw:LOCALAPPDATA/pw:MILADY_TEST_USER_ROOT/pw"
  mkdir -p "$APPDATA" "$LOCALAPPDATA"
else
  test_profile="$(mktemp -d "$results_dir/profile-XXXXXXXX")"
  export XDG_DATA_HOME="$test_profile/data" XDG_CONFIG_HOME="$test_profile/config" XDG_CACHE_HOME="$test_profile/cache"
  export MILADY_TEST_USER_ROOT="$XDG_DATA_HOME"
  mkdir -p "$XDG_DATA_HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"
fi
printf 'Profil isolé : %s\n' "$test_profile"
printf '%s\n' "$test_profile" > "$results_dir/profile.txt"
cleanup() {
  local status=$?
  if [[ $status -eq 0 ]]; then
    rm -rf -- "$test_profile"
  else
    printf 'Profil conservé après échec : %s\n' "$test_profile" >&2
  fi
}
trap cleanup EXIT

run_check() {
  local label="$1" seconds="$2" status=0
  shift 2
  timeout --kill-after=5 "$seconds" ./tools/run.sh "$@" > "$results_dir/$label.log" 2>&1 || status=$?
  cat "$results_dir/$label.log"
  if [[ $status -ne 0 ]]; then
    echo "Échec $label (code $status)." >&2
    return "$status"
  fi
  if rg -n '^FAIL |SCRIPT ERROR|ERROR:|leaked' "$results_dir/$label.log"; then return 1; fi
  if [[ "$label" != import ]] && ! rg -q '^RESULT [1-9][0-9]* .*; 0 failures\r?$' "$results_dir/$label.log"; then
    echo "Fin de vérification absente ou invalide : $label." >&2
    return 1
  fi
}

run_check import 180 --headless --editor --import --quit
run_check user-data-path 30 --headless --script res://tests/user_data_path.gd
for suite in movement physics mobility combat platform boundaries keyboard integration bonus routes backtracking damage_profiles damage_protection spikes_void death_transition audio progression_v2 menus longbow rewards dialogue_panel resurrection_player n1_cinematics n1_flow chest_economy standard_weapons reward_transactions run019_enemies run019_traps run019_exploration run019_integration run020_campaign run020_routes run021_tuning run021_audio run021_chase run021_elite_navigation run021_flight run021_wall_jump; do
  suite_timeout=90
  if [[ "$suite" == standard_weapons || "$suite" == run020_campaign || "$suite" == run020_routes || "$suite" == run021_elite_navigation ]]; then suite_timeout=180; fi
  if [[ "$suite" == run019_exploration || "$suite" == run019_integration || "$suite" == run020_campaign || "$suite" == run021_audio ]]; then
    run_check "$suite" "$suite_timeout" --headless --script "res://tests/$suite.gd"
  else
    run_check "$suite" "$suite_timeout" --headless --fixed-fps 60 --script "res://tests/$suite.gd"
  fi
done
# Exercise the upper variant too. In edited N2 both variants use the upper
# causeway and tunnel; the default retains the lower vault. N3/N4 test both forks.
run_check run020-routes-upper 180 --headless --fixed-fps 60 --script res://tests/run020_routes.gd -- upper
# Cold closure uses the real clock so gameplay and audio shutdown share the same timing.
run_check n1-cold-prepare 90 --headless --script res://tests/n1_cold_session.gd -- prepare
run_check n1-cold-reopen 90 --headless --script res://tests/n1_cold_session.gd -- reopen
run_check equipment-cold-open 90 --headless --script res://tests/equipment_cold_session.gd -- open
run_check equipment-cold-accept 90 --headless --script res://tests/equipment_cold_session.gd -- accept
run_check equipment-cold-finish 90 --headless --script res://tests/equipment_cold_session.gd -- finish
run_check run019-cold-prepare 90 --headless --script res://tests/run019_cold_session.gd -- prepare
run_check run019-cold-reopen 90 --headless --script res://tests/run019_cold_session.gd -- reopen
run_check run019-cold-reset 90 --headless --script res://tests/run019_cold_session.gd -- reset
run_check run020-cold-prepare 90 --headless --script res://tests/run020_cold_session.gd -- prepare
run_check run020-cold-reopen 90 --headless --script res://tests/run020_cold_session.gd -- reopen
run_check run020-cold-reset 90 --headless --script res://tests/run020_cold_session.gd -- reset
printf '40 suites et onze sessions à froid terminées ; isolation user:// vérifiée. Logs : %s\n' "$results_dir"
