#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from tools.regression.numdiff import (
    compare_float_sequences,
    compare_named_values,
    extract_float_sequence,
    parse_key_value_numbers,
    strip_ignored_lines,
)

STDOUT_RESULT_PATTERN = re.compile(
    r"resulted Mp =\s*([-+0-9.eE]+)\s*and Mm =\s*([-+0-9.eE]+)"
)
STDOUT_ADM_PATTERN = re.compile(r"The total ADM mass is\s*([-+0-9.eE]+)")


def build_input_text(params: dict[str, float]) -> str:
    ordered_keys = [
        "mm",
        "mp",
        "b",
        "P_plusx",
        "P_plusy",
        "P_plusz",
        "P_minusx",
        "P_minusy",
        "P_minusz",
        "S_plusx",
        "S_plusy",
        "S_plusz",
        "S_minusx",
        "S_minusy",
        "S_minusz",
        "Mp",
        "Mm",
        "admtol",
        "Newtontol",
        "nA",
        "nB",
        "nphi",
        "Newtonmaxit",
    ]

    lines = []
    for key in ordered_keys:
        if key not in params:
            raise KeyError(f"missing key in params: {key}")
        lines.append(f"ABE::{key} = {params[key]}")
    return "\n".join(lines) + "\n"


def parse_stdout_metrics(stdout_text: str) -> dict[str, float]:
    out: dict[str, float] = {}

    m = STDOUT_RESULT_PATTERN.search(stdout_text)
    if m:
        out["resulted_Mp"] = float(m.group(1))
        out["resulted_Mm"] = float(m.group(2))

    m = STDOUT_ADM_PATTERN.search(stdout_text)
    if m:
        out["total_ADM_mass"] = float(m.group(1))

    return out


def run_case(binary: Path, input_text: str, run_root: Path) -> tuple[str, str]:
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "TwoPunctureinput.par").write_text(input_text, encoding="utf-8")

    proc = subprocess.run(
        [str(binary)],
        cwd=run_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    if proc.returncode != 0:
        raise RuntimeError(f"command failed with code {proc.returncode}\n{proc.stdout}")

    out_file = run_root / "Ansorg.psid"
    if not out_file.exists():
        raise RuntimeError(f"expected output file not found: {out_file}")

    return proc.stdout, out_file.read_text(encoding="utf-8", errors="strict")


def compare_outputs(
    legacy_stdout: str,
    legacy_file: str,
    rust_stdout: str,
    rust_file: str,
    ansorg_rtol: float,
    ansorg_atol: float,
    stdout_rtol: float,
    stdout_atol: float,
    ignore_patterns: list[str],
) -> None:
    legacy_clean = strip_ignored_lines(legacy_file, ignore_patterns)
    rust_clean = strip_ignored_lines(rust_file, ignore_patterns)

    legacy_seq = extract_float_sequence(legacy_clean)
    rust_seq = extract_float_sequence(rust_clean)

    seq_result = compare_float_sequences(legacy_seq, rust_seq, rtol=ansorg_rtol, atol=ansorg_atol)
    if not seq_result.ok:
        raise RuntimeError(f"Ansorg.psid numeric sequence compare failed: {seq_result.reason}")

    legacy_named = parse_key_value_numbers(legacy_clean)
    rust_named = parse_key_value_numbers(rust_clean)
    check_keys = [
        "bhmass1",
        "bhmass2",
        "bhpy1",
        "bhpy2",
    ]
    named_result = compare_named_values(
        legacy_named,
        rust_named,
        keys=check_keys,
        rtol=ansorg_rtol,
        atol=ansorg_atol,
    )
    if not named_result.ok:
        raise RuntimeError(f"Ansorg.psid named value compare failed: {named_result.reason}")

    legacy_metrics = parse_stdout_metrics(legacy_stdout)
    rust_metrics = parse_stdout_metrics(rust_stdout)
    stdout_result = compare_named_values(
        legacy_metrics,
        rust_metrics,
        keys=["resulted_Mp", "resulted_Mm", "total_ADM_mass"],
        rtol=stdout_rtol,
        atol=stdout_atol,
    )
    if not stdout_result.ok:
        raise RuntimeError(f"stdout metric compare failed: {stdout_result.reason}")


def main() -> int:
    parser = argparse.ArgumentParser(description="TwoPuncture differential test: legacy vs Rust")
    parser.add_argument("--legacy-bin", required=True)
    parser.add_argument("--rust-bin", default="")
    parser.add_argument("--case-json", required=True)
    parser.add_argument("--work-root", default="build/refactor-guard/two-puncture")
    parser.add_argument("--require-rust", action="store_true")
    args = parser.parse_args()

    legacy_bin = Path(args.legacy_bin).resolve()
    rust_bin = Path(args.rust_bin).resolve() if args.rust_bin else None

    if not legacy_bin.exists():
        raise FileNotFoundError(f"legacy binary not found: {legacy_bin}")

    if rust_bin is not None and not rust_bin.exists():
        raise FileNotFoundError(f"rust binary not found: {rust_bin}")

    case_cfg = json.loads(Path(args.case_json).read_text(encoding="utf-8"))
    params = case_cfg["params"]
    ansorg_rtol = float(case_cfg["tolerance"]["ansorg_rtol"])
    ansorg_atol = float(case_cfg["tolerance"]["ansorg_atol"])
    stdout_rtol = float(case_cfg["tolerance"]["stdout_rtol"])
    stdout_atol = float(case_cfg["tolerance"]["stdout_atol"])
    ignore_patterns = case_cfg.get("ignore_line_patterns", [r"^#File created on "])

    work_root = Path(args.work_root).resolve()
    work_root.mkdir(parents=True, exist_ok=True)
    case_name = case_cfg.get("name", "two_puncture_case")

    input_text = build_input_text(params)

    with tempfile.TemporaryDirectory(prefix=f"{case_name}_", dir=work_root) as tmp:
        tmp_path = Path(tmp)
        legacy_dir = tmp_path / "legacy"
        legacy_stdout, legacy_file = run_case(legacy_bin, input_text, legacy_dir)

        (tmp_path / "legacy.stdout.log").write_text(legacy_stdout, encoding="utf-8")
        (tmp_path / "legacy.Ansorg.psid").write_text(legacy_file, encoding="utf-8")

        if rust_bin is None:
            if args.require_rust:
                raise RuntimeError("Rust binary is required but not provided")
            print("[refactor-guard] legacy run completed.")
            print("[refactor-guard] set --rust-bin (or RUST_TWOPUNCTURE_BIN) to enable differential checks.")
            keep_dir = work_root / f"{case_name}-latest-legacy"
            if keep_dir.exists():
                shutil.rmtree(keep_dir)
            keep_dir.mkdir(parents=True, exist_ok=True)
            (keep_dir / "TwoPunctureinput.par").write_text(input_text, encoding="utf-8")
            (keep_dir / "legacy.stdout.log").write_text(legacy_stdout, encoding="utf-8")
            (keep_dir / "legacy.Ansorg.psid").write_text(legacy_file, encoding="utf-8")
            return 0

        rust_dir = tmp_path / "rust"
        rust_stdout, rust_file = run_case(rust_bin, input_text, rust_dir)

        compare_outputs(
            legacy_stdout=legacy_stdout,
            legacy_file=legacy_file,
            rust_stdout=rust_stdout,
            rust_file=rust_file,
            ansorg_rtol=ansorg_rtol,
            ansorg_atol=ansorg_atol,
            stdout_rtol=stdout_rtol,
            stdout_atol=stdout_atol,
            ignore_patterns=ignore_patterns,
        )

        print("[refactor-guard] TwoPuncture legacy-vs-rust diff passed.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
