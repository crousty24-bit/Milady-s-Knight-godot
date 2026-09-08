#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p work/test-results
./tools/run.sh --headless --editor --import --quit > work/test-results/import.log 2>&1
if rg -n 'SCRIPT ERROR|ERROR:' work/test-results/import.log; then exit 1; fi
for suite in movement physics integration routes backtracking; do
  timeout 90 ./tools/run.sh --headless --fixed-fps 60 --script "res://tests/$suite.gd" > "work/test-results/$suite.log" 2>&1 || {
    cat "work/test-results/$suite.log"
    exit 1
  }
  cat "work/test-results/$suite.log"
  if rg -n '^FAIL |SCRIPT ERROR|ERROR:|leaked' "work/test-results/$suite.log"; then exit 1; fi
done
