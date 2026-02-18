from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable

FLOAT_PATTERN = re.compile(r"[-+]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")


@dataclass
class CompareResult:
    ok: bool
    reason: str


def strip_ignored_lines(text: str, ignore_line_patterns: Iterable[str]) -> str:
    patterns = [re.compile(p) for p in ignore_line_patterns]
    out_lines: list[str] = []
    for line in text.splitlines():
        if any(p.search(line) for p in patterns):
            continue
        out_lines.append(line)
    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")


def extract_float_sequence(text: str) -> list[float]:
    return [float(x.group(0)) for x in FLOAT_PATTERN.finditer(text)]


def parse_key_value_numbers(text: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        try:
            out[key] = float(value)
        except ValueError:
            continue
    return out


def _is_close(a: float, b: float, rtol: float, atol: float) -> bool:
    return math.isclose(a, b, rel_tol=rtol, abs_tol=atol)


def compare_float_sequences(expected: list[float], actual: list[float], rtol: float, atol: float) -> CompareResult:
    if len(expected) != len(actual):
        return CompareResult(False, f"length mismatch: expected={len(expected)} actual={len(actual)}")

    for i, (e, a) in enumerate(zip(expected, actual)):
        if not _is_close(e, a, rtol, atol):
            return CompareResult(
                False,
                (
                    f"value mismatch at index {i}: expected={e:.16e} "
                    f"actual={a:.16e} abs_diff={abs(e - a):.3e}"
                ),
            )

    return CompareResult(True, "all values are within tolerance")


def compare_named_values(
    expected: dict[str, float], actual: dict[str, float], keys: Iterable[str], rtol: float, atol: float
) -> CompareResult:
    for key in keys:
        if key not in expected:
            return CompareResult(False, f"missing key in expected: {key}")
        if key not in actual:
            return CompareResult(False, f"missing key in actual: {key}")

        e = expected[key]
        a = actual[key]
        if not _is_close(e, a, rtol, atol):
            return CompareResult(
                False,
                (
                    f"named value mismatch for '{key}': expected={e:.16e} "
                    f"actual={a:.16e} abs_diff={abs(e - a):.3e}"
                ),
            )

    return CompareResult(True, "all named values are within tolerance")
