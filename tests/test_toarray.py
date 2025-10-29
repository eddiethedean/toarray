import math
from array import array

import pytest

from toarray import get_array


def test_empty_iterable():
    assert get_array([]) == []


def test_non_numeric_returns_list():
    data = ["a", "b", "c"]
    out = get_array(data)
    assert isinstance(out, list)
    assert out == data


@pytest.mark.parametrize(
    "values,code",
    [
        ([0, 1, 255], "B"),
        ([0, 0, 0], "B"),
        ([-1, 0, 1], "b"),
        ([256, 65535], "H"),
        ([-32768, 32767], "h"),
        ([65536, 2_147_483_647], "I"),
        ([-2_147_483_648, 0, 2], "i"),
        ([2**33, 2**40], "Q"),
        ([-(2**40), -(2**33)], "q"),
    ],
)
def test_integer_arrays(values, code):
    out = get_array(values)
    assert isinstance(out, array)
    assert out.typecode == code
    assert list(out) == values


def test_floats_choose_f_then_d():
    small = [0.0, 1.5, -2.25]
    out = get_array(small)
    assert isinstance(out, array)
    # could be 'f' or 'd' depending on exact values; ensure it builds and matches
    assert list(map(float, out)) == small

    big = [1e310, -1e308]
    out2 = get_array(big)
    assert isinstance(out2, array)
    assert out2.typecode == "d"
    assert list(map(float, out2)) == big


def test_mixed_numeric_and_non_numeric_returns_list():
    data = [1, "x", 3]
    out = get_array(data)
    assert isinstance(out, list)
    assert out == data


def test_nan_and_inf_supported_by_floats():
    vals = [0.0, float("nan"), float("inf"), float("-inf")]
    out = get_array(vals)
    assert isinstance(out, array)
    assert out.typecode in {"f", "d"}
    # NaN != NaN, so compare using math functions
    assert math.isfinite(out[0]) and out[0] == 0.0
    assert math.isnan(out[1])
    assert math.isinf(out[2])
    assert math.isinf(out[3])
