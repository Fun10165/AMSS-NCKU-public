#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEGACY_BIN="${LEGACY_TWOPUNCTURE_BIN:-${ROOT_DIR}/AMSS_NCKU_source/TwoPunctureABE}"
RUST_BIN="${RUST_TWOPUNCTURE_BIN:-}"
CASE_GLOB="${CASE_GLOB:-${ROOT_DIR}/tests/refactor_guard/cases/*.json}"
REQUIRE_RUST_DIFF="${REQUIRE_RUST_DIFF:-0}"

if [[ ! -x "${LEGACY_BIN}" ]]; then
  echo "legacy binary not found or not executable: ${LEGACY_BIN}"
  echo "Try running: ./scripts/test_native.sh"
  exit 1
fi

echo "[1/4] Python regression unit tests"
python -m pytest tests/test_derivative.py tests/test_derivative_xiaoqu.py

echo "[2/4] Refactor-guard framework tests"
python -m pytest tests/refactor_guard

echo "[3/4] Legacy baseline run (TwoPuncture cases)"
shopt -s nullglob
case_files=( ${CASE_GLOB} )
shopt -u nullglob
if [[ ${#case_files[@]} -eq 0 ]]; then
  echo "no case files found for CASE_GLOB=${CASE_GLOB}"
  exit 1
fi

for case_json in "${case_files[@]}"; do
  echo "running case: ${case_json}"
  diff_args=(
    --legacy-bin "${LEGACY_BIN}"
    --case-json "${case_json}"
  )
  if [[ -n "${RUST_BIN}" ]]; then
    diff_args+=(--rust-bin "${RUST_BIN}")
  fi
  if [[ "${REQUIRE_RUST_DIFF}" == "1" ]]; then
    diff_args+=(--require-rust)
  fi
  python -m tools.regression.two_puncture_diff "${diff_args[@]}"
done

echo "[4/4] Done"
if [[ -z "${RUST_BIN}" ]]; then
  echo "RUST_TWOPUNCTURE_BIN is not set, so only legacy baseline was validated."
  echo "Set RUST_TWOPUNCTURE_BIN to enable legacy-vs-rust differential checks."
else
  echo "Legacy-vs-rust differential checks passed."
fi
