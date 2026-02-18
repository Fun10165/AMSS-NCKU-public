import numpy as np
import pytest

import derivative_xiaoqu


METHODS = [
    "3-points 2-orders",
    "5-points 4-orders",
    "7-points 6-orders",
    "9-points 8-orders",
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
    if method == "9-points 8-orders":
        return (
            3.0 * f(x - 4.0 * h)
            - 32.0 * f(x - 3.0 * h)
            + 168.0 * f(x - 2.0 * h)
            - 672.0 * f(x - h)
            + 672.0 * f(x + h)
            - 168.0 * f(x + 2.0 * h)
            + 32.0 * f(x + 3.0 * h)
            - 3.0 * f(x + 4.0 * h)
        ) / (840.0 * h)
    raise ValueError("unsupported method in test helper")


def series_stencil_value(series, i, dt, method):
    if method == "3-points 2-orders":
        return (series[i + 1] + series[i - 1]) / (2.0 * dt)
    if method == "5-points 4-orders":
        return (series[i - 2] - 8.0 * series[i - 1] + 8.0 * series[i + 1] - series[i + 2]) / (
            12.0 * dt
        )
    if method == "7-points 6-orders":
        return (
            -series[i - 3]
            + 9.0 * series[i - 2]
            - 45.0 * series[i - 1]
            + 45.0 * series[i + 1]
            - 9.0 * series[i + 2]
            + series[i + 3]
        ) / (60.0 * dt)
    if method == "9-points 8-orders":
        return (
            3.0 * series[i - 4]
            - 32.0 * series[i - 3]
            + 168.0 * series[i - 2]
            - 672.0 * series[i - 1]
            + 672.0 * series[i + 1]
            - 168.0 * series[i + 2]
            + 32.0 * series[i + 3]
            - 3.0 * series[i + 4]
        ) / (840.0 * dt)
    raise ValueError("unsupported method in test helper")


def test_first_order_derivative_matches_current_implementation():
    f = lambda x: x**3 + 2.0 * x - 1.0
    x = -0.2
    h = 1.0e-3

    for method in METHODS:
        expected = scalar_stencil_value(f, x, h, method)
        result = derivative_xiaoqu.first_order_derivative(f, x, h, method)
        assert result == pytest.approx(expected, rel=1e-12, abs=1e-12)


def test_first_order_derivative_invalid_method_raises_unboundlocalerror():
    with pytest.raises(UnboundLocalError):
        derivative_xiaoqu.first_order_derivative(lambda x: x, 0.0, 0.1, "invalid")


def test_first_order_derivative_at_t0_all_methods():
    t = np.linspace(-1.0, 1.0, 41)
    series = np.sin(t) + t**2
    i = 20
    dt = t[1] - t[0]

    for method in METHODS:
        expected = series_stencil_value(series, i, dt, method)
        result = derivative_xiaoqu.first_order_derivative_at_t0(series, t, i, method)
        assert result == pytest.approx(expected, rel=1e-12, abs=1e-12)


def test_first_order_derivative_at_t0_invalid_method_raises_unboundlocalerror():
    t = np.linspace(0.0, 1.0, 21)
    series = t**2
    with pytest.raises(UnboundLocalError):
        derivative_xiaoqu.first_order_derivative_at_t0(series, t, 10, "invalid")
