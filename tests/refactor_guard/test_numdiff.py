import pytest

from tools.regression.numdiff import (
    compare_float_sequences,
    compare_named_values,
    extract_float_sequence,
    parse_key_value_numbers,
    strip_ignored_lines,
)


def test_strip_ignored_lines_single_pattern():
    text = "#time line\na=1\nb=2\n"
    cleaned = strip_ignored_lines(text, [r"^#"])
    assert cleaned == "a=1\nb=2\n"


def test_strip_ignored_lines_multiple_patterns():
    text = "skip this\nkeep=1\nremove me\n"
    cleaned = strip_ignored_lines(text, [r"^skip", r"remove"])
    assert cleaned == "keep=1\n"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("a=1", [1.0]),
        ("x=-3.5 y=+2.1", [-3.5, 2.1]),
        ("1e-2 2E+3", [1.0e-2, 2.0e3]),
        ("no number", []),
        (".5 -.25 +4.", [0.5, -0.25, 4.0]),
    ],
)
def test_extract_float_sequence(text, expected):
    assert extract_float_sequence(text) == expected


def test_parse_key_value_numbers_ignores_non_numeric():
    text = "a = 1\nb = hello\nc=2.5\n"
    parsed = parse_key_value_numbers(text)
    assert parsed == {"a": 1.0, "c": 2.5}


def test_compare_float_sequences_equal():
    result = compare_float_sequences([1.0, 2.0], [1.0, 2.0], rtol=0.0, atol=0.0)
    assert result.ok


def test_compare_float_sequences_length_mismatch():
    result = compare_float_sequences([1.0], [1.0, 2.0], rtol=1.0e-9, atol=1.0e-12)
    assert not result.ok
    assert "length mismatch" in result.reason


def test_compare_float_sequences_value_mismatch():
    result = compare_float_sequences([1.0, 2.0], [1.0, 2.1], rtol=1.0e-9, atol=1.0e-12)
    assert not result.ok
    assert "index 1" in result.reason


def test_compare_float_sequences_with_tolerance():
    result = compare_float_sequences([1.0], [1.0 + 1.0e-9], rtol=1.0e-8, atol=0.0)
    assert result.ok


def test_compare_named_values_equal():
    result = compare_named_values(
        {"a": 1.0, "b": 2.0},
        {"a": 1.0, "b": 2.0},
        keys=["a", "b"],
        rtol=0.0,
        atol=0.0,
    )
    assert result.ok


def test_compare_named_values_missing_key_in_expected():
    result = compare_named_values({"a": 1.0}, {"a": 1.0, "b": 2.0}, keys=["b"], rtol=1.0e-8, atol=1.0e-12)
    assert not result.ok
    assert "missing key in expected" in result.reason


def test_compare_named_values_missing_key_in_actual():
    result = compare_named_values({"a": 1.0}, {}, keys=["a"], rtol=1.0e-8, atol=1.0e-12)
    assert not result.ok
    assert "missing key in actual" in result.reason


def test_compare_named_values_value_mismatch():
    result = compare_named_values({"a": 1.0}, {"a": 1.1}, keys=["a"], rtol=1.0e-8, atol=1.0e-12)
    assert not result.ok
    assert "named value mismatch" in result.reason


def test_compare_named_values_with_tolerance():
    result = compare_named_values(
        {"a": 1.0},
        {"a": 1.0 + 1.0e-9},
        keys=["a"],
        rtol=1.0e-8,
        atol=0.0,
    )
    assert result.ok
