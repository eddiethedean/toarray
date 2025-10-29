from array import array

import pytest

from toarray import analyze_array, select_array
from toarray.result import SelectionError


def test_select_policy_defaults_smallest():
    out = select_array([0, 1, 255])
    assert isinstance(out, array)
    assert out.typecode == "B"


def test_no_float_policy_returns_list_for_floats():
    out = select_array([1.0, 2.0], no_float=True)
    assert isinstance(out, list)


def test_analyze_array_metadata():
    res = analyze_array([1, 2, 3])
    assert res.count == 3
    assert res.min == 1.0 and res.max == 3.0
    assert res.typecode in {"b", "B", "h", "H", "i", "I", "q", "Q"}


def test_analyze_array_empty_and_non_numeric():
    empty = analyze_array([])
    assert empty.reason == "empty" and empty.count == 0
    nn = analyze_array(["x", 1])
    assert nn.reason == "non-numeric" and nn.typecode is None


def test_analyze_array_no_fitting_type_reason():
    # Floats disallowed -> select_array returns list -> reason 'no-fitting-type'
    res = analyze_array([1.0, 2.0], no_float=True)
    assert res.reason == "no-fitting-type"


def test_policy_balanced_and_wide():
    # 'balanced' starts with signed preference sequence
    out_bal = select_array([0, 1, 2], policy="balanced")
    assert isinstance(out_bal, array)
    assert out_bal.typecode in {"b", "B", "h", "H", "i", "I", "q", "Q"}

    # 'wide' favors wider ints first; still should be integer array
    out_wide = select_array([0, 1, 2], policy="wide")
    assert isinstance(out_wide, array)
    assert out_wide.typecode in {"i", "I", "q", "Q", "h", "H", "b", "B"}


def test_min_max_bounds_and_prefer_signed():
    # Constrain to 16-bit types only; prefer signed yields 'h' for negatives
    v = [-1, 0, 1]
    out = select_array(v, min_type="h", max_type="H", prefer_signed=True)
    assert isinstance(out, array) and out.typecode == "h"

    # Constrain to 32-bit unsigned only; forces 'I'
    out2 = select_array([65536, 70000], min_type="I", max_type="I")
    assert isinstance(out2, array) and out2.typecode == "I"


def test_no_float_strict_raises():
    with pytest.raises(SelectionError) as ei:
        select_array([1.0, 2.0], no_float=True, strict=True)
    assert ei.value.expected == "integers only"


def test_allow_float_downgrade_skip_float32():
    # Value exceeds float32: should choose 'd' when downgrade not allowed
    out = select_array([1e39, -1e39], allow_float_downgrade=False)
    assert isinstance(out, array) and out.typecode == "d"


def test_strict_with_empty_candidates_raises_selectionerror():
    # Create empty candidate space via inverted bounds
    with pytest.raises(SelectionError):
        select_array([1], min_type="d", max_type="b", strict=True)


def test_skip_f32_continue_path():
    # Default allow_float_downgrade=True, but skip 'f' due to range, then pick 'd'
    out = select_array([1e39])
    assert isinstance(out, array) and out.typecode == "d"


def test_strict_violating_index_inside_loop():
    with pytest.raises(SelectionError) as ei:
        select_array([1000], min_type="b", max_type="B", strict=True)
    assert isinstance(ei.value, SelectionError)


def test_end_fallback_returns_list_when_not_strict():
    out = select_array([1000], min_type="b", max_type="B", strict=False)
    assert isinstance(out, list)
