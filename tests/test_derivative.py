import numpy as np
import pytest

import derivative


METHODS = [
    "3-points 2-orders",
    "5-points 4-orders",
    "7-points 6-orders",
]


def scalar_stencil_value(f, x, h, method):
    if method == "3-points 2-orders":
        return (f(x + h) + f(x - h)) / (2.0 * h)
    if method == "5-points 4-orders":
        return (f(x - 2.0 * h) - 8.0 * f(x - h) + 8.0 * f(x + h) - f(x + 2.0 * h)) / (
            12.0 * h
        )
    if method == "7-points 6-orders":
        return (
            -f(x - 3.0 * h)
            + 9.0 * f(x - 2.0 * h)
            - 45.0 * f(x - h)
            + 45.0 * f(x + h)
            - 9.0 * f(x + 2.0 * h)
            + f(x + 3.0 * h)
        ) / (60.0 * h)
    raise ValueError("unsupported method in test helper")


def multivalue_stencil_value(f, x, h, method):
    f0 = f(x)
    out = np.zeros(len(f0))

    for i in range(len(f0)):
        if method == "3-points 2-orders":
            fx1 = f(x - h)
            fx3 = f(x + h)
            out[i] = (fx3[i] + fx1[i]) / (2.0 * h)
        elif method == "5-points 4-orders":
            fx1 = f(x - 2.0 * h)
            fx2 = f(x - h)
            fx4 = f(x + h)
            fx5 = f(x + 2.0 * h)
            out[i] = (fx1[i] - 8.0 * fx2[i] + 8.0 * fx4[i] - fx5[i]) / (12.0 * h)
        elif method == "7-points 6-orders":
            fx1 = f(x - 3.0 * h)
            fx2 = f(x - 2.0 * h)
            fx3 = f(x - h)
            fx5 = f(x + h)
            fx6 = f(x + 2.0 * h)
            fx7 = f(x + 3.0 * h)
            out[i] = (
                -fx1[i]
                - 9.0 * fx2[i]
                - 45.0 * fx3[i]
                + 45.0 * fx5[i]
                - 9.0 * fx6[i]
                + fx7[i]
            ) / (60.0 * h)
        else:
            raise ValueError("unsupported method in test helper")

    return out


def test_first_order_derivative_matches_current_implementation():
    f = lambda x: x**4 - 2.0 * x + 3.0
    x = 0.35
    h = 1.0e-3

    for method in METHODS:
        expected = scalar_stencil_value(f, x, h, method)
        result = derivative.first_order_derivative(f, x, h, method)
        assert result == pytest.approx(expected, rel=1e-12, abs=1e-12)


def test_first_order_derivative_invalid_method_raises_unboundlocalerror():
    with pytest.raises(UnboundLocalError):
        derivative.first_order_derivative(lambda x: x, 1.0, 0.1, "invalid")


def test_first_order_derivative_multivalue_all_methods(capsys):
    def f(x):
        return (x**2 + 1.0, np.sin(x), 3.0 * x - 2.0)

    x = 0.7
    h = 2.0e-3

    for method in METHODS:
        expected = multivalue_stencil_value(f, x, h, method)
        result = derivative.first_order_derivative_multivalue(f, x, h, method)
        assert np.allclose(result, expected, rtol=1e-12, atol=1e-12)

    printed = capsys.readouterr().out
    assert "(" in printed
    assert ")" in printed


def test_first_order_derivative_multivalue_invalid_method_returns_zeros():
    def f(x):
        return [x, x + 1.0, x**2]

    result = derivative.first_order_derivative_multivalue(f, 1.2, 0.1, "invalid")
    assert np.array_equal(result, np.zeros(3))
