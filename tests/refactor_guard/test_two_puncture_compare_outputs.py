import pytest

from tools.regression.two_puncture_diff import compare_outputs


def _sample_file(mass2=0.5):
    return (
        "#File created on Wed Feb 18 00:00:00 2026\n"
        "bhmass1      = 0.5\n"
        f"bhmass2      = {mass2}\n"
        "bhpy1        = 0.1\n"
        "bhpy2        = -0.1\n"
        "data 2 2 2\n"
        "1.0\n"
        "2.0\n"
        "3.0\n"
    )


def _sample_stdout(adm=1.01501):
    return (
        "The two puncture masses are mp = 0.5 and mm = 0.5\n"
        "                   resulted Mp = 0.523119 and Mm = 0.523119\n"
        f"The total ADM mass is {adm}\n"
    )


def test_compare_outputs_success():
    compare_outputs(
        legacy_stdout=_sample_stdout(),
        legacy_file=_sample_file(),
        rust_stdout=_sample_stdout(),
        rust_file=_sample_file(),
        ansorg_rtol=1.0e-8,
        ansorg_atol=1.0e-10,
        stdout_rtol=1.0e-8,
        stdout_atol=1.0e-10,
        ignore_patterns=[r"^#File created on "],
    )


def test_compare_outputs_raises_on_named_value_mismatch():
    with pytest.raises(RuntimeError, match="named value compare failed"):
        compare_outputs(
            legacy_stdout=_sample_stdout(),
            legacy_file=_sample_file(mass2=0.5),
            rust_stdout=_sample_stdout(),
            rust_file=_sample_file(mass2=0.5),
            ansorg_rtol=1.0e-8,
            ansorg_atol=1.0e-10,
            stdout_rtol=1.0e-8,
            stdout_atol=1.0e-10,
            ignore_patterns=[r"^#File created on ", r"^bhpy2"],
        )


def test_compare_outputs_raises_on_stdout_metric_mismatch():
    with pytest.raises(RuntimeError, match="stdout metric compare failed"):
        compare_outputs(
            legacy_stdout=_sample_stdout(adm=1.01501),
            legacy_file=_sample_file(),
            rust_stdout=_sample_stdout(adm=1.11501),
            rust_file=_sample_file(),
            ansorg_rtol=1.0e-8,
            ansorg_atol=1.0e-10,
            stdout_rtol=1.0e-12,
            stdout_atol=1.0e-12,
            ignore_patterns=[r"^#File created on "],
        )
