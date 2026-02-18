import json
from glob import glob
from pathlib import Path

import pytest

from tools.regression.two_puncture_diff import (
    build_input_text,
    parse_stdout_metrics,
)


def test_build_input_text_contains_required_lines():
    params = {
        "mm": 0.5,
        "mp": 0.5,
        "b": 3.0,
        "P_plusx": 0.0,
        "P_plusy": 0.1,
        "P_plusz": 0.0,
        "P_minusx": 0.0,
        "P_minusy": -0.1,
        "P_minusz": 0.0,
        "S_plusx": 0.0,
        "S_plusy": 0.0,
        "S_plusz": 0.0,
        "S_minusx": 0.0,
        "S_minusy": 0.0,
        "S_minusz": 0.0,
        "Mp": 1.0,
        "Mm": 1.0,
        "admtol": 1.0e-8,
        "Newtontol": 1.0e-8,
        "nA": 12,
        "nB": 12,
        "nphi": 8,
        "Newtonmaxit": 5,
    }
    text = build_input_text(params)
    assert "ABE::mm = 0.5" in text
    assert "ABE::nphi = 8" in text
    assert text.count("ABE::") == 23


def test_build_input_text_missing_key_raises_keyerror():
    with pytest.raises(KeyError):
        build_input_text({"mm": 0.5})


def test_parse_stdout_metrics_extracts_values():
    stdout = """
The two puncture masses are mp = 0.5 and mm = 0.5
                   resulted Mp = 0.523119 and Mm = 0.523119
The total ADM mass is 1.01501
"""
    parsed = parse_stdout_metrics(stdout)
    assert parsed["resulted_Mp"] == pytest.approx(0.523119)
    assert parsed["resulted_Mm"] == pytest.approx(0.523119)
    assert parsed["total_ADM_mass"] == pytest.approx(1.01501)


def test_parse_stdout_metrics_empty_when_no_match():
    parsed = parse_stdout_metrics("no metrics here")
    assert parsed == {}


def test_case_json_has_required_sections():
    case_paths = sorted(glob("tests/refactor_guard/cases/*.json"))
    assert len(case_paths) >= 5

    seen_names = set()
    required_param_keys = {
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
    }
    required_tol_keys = {"ansorg_rtol", "ansorg_atol", "stdout_rtol", "stdout_atol"}

    for case in case_paths:
        cfg = json.loads(Path(case).read_text(encoding="utf-8"))
        assert "name" in cfg
        assert cfg["name"] not in seen_names
        seen_names.add(cfg["name"])

        assert "params" in cfg
        assert required_param_keys.issubset(set(cfg["params"].keys()))

        assert "tolerance" in cfg
        assert required_tol_keys.issubset(set(cfg["tolerance"].keys()))

        assert "ignore_line_patterns" in cfg
        assert isinstance(cfg["ignore_line_patterns"], list)
        assert cfg["params"]["nA"] >= 8
        assert cfg["params"]["nB"] >= 8
