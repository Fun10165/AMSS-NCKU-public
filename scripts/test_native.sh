#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/native-tests"

mkdir -p "${BUILD_DIR}"

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required tool: $1"
    echo "Tip: enter the provided Nix environment first: nix develop"
    exit 127
  fi
}

require_tool g++
require_tool gfortran
require_tool make

echo "[1/3] Running C++ native tests (AMSS_NCKU_source/*.C)"
g++ -std=gnu++14 -Wno-deprecated -Dnewc -O2 -I"${ROOT_DIR}/AMSS_NCKU_source" \
  "${ROOT_DIR}/tests/native/test_ahf_utils.cpp" \
  "${ROOT_DIR}/AMSS_NCKU_source/round.C" \
  "${ROOT_DIR}/AMSS_NCKU_source/norm.C" \
  "${ROOT_DIR}/AMSS_NCKU_source/fuzzy.C" \
  -o "${BUILD_DIR}/test_ahf_utils"
"${BUILD_DIR}/test_ahf_utils"

echo "[2/3] Running Fortran native tests (AMSS_NCKU_source/*.f90)"
gfortran -cpp -O2 -c "${ROOT_DIR}/AMSS_NCKU_source/FFT.f90" -o "${BUILD_DIR}/FFT.o"
gfortran -O2 \
  "${ROOT_DIR}/tests/native/test_fft_roundtrip.f90" \
  "${BUILD_DIR}/FFT.o" \
  -o "${BUILD_DIR}/test_fft_roundtrip"
"${BUILD_DIR}/test_fft_roundtrip"

echo "[3/3] Running CPU-only makefile smoke build (C/C++ linkage)"
make -C "${ROOT_DIR}/AMSS_NCKU_source" clean >/dev/null
make -C "${ROOT_DIR}/AMSS_NCKU_source" TwoPunctureABE \
  CXX=g++ \
  CLINKER=g++ \
  filein="" \
  CXXAPPFLAGS="-std=gnu++14 -O2 -Wno-deprecated -Dfortran3 -Dnewc" \
  LDLIBS="-lm" >/dev/null

test -x "${ROOT_DIR}/AMSS_NCKU_source/TwoPunctureABE"

echo "Native C/C++/Fortran tests passed."
