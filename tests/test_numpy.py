import pytest

from toarray import to_numpy

np = pytest.importorskip("numpy")  # skip if numpy missing


def test_to_numpy_min_zeros_copylike():
    arr = to_numpy([0, 1, 2], dtype="min")
    assert arr.dtype.kind in {"i", "u"}
    assert arr.shape == (3,)


def test_to_numpy_explicit_float64():
    arr = to_numpy([0, 1, 2], dtype="float64")
    assert arr.dtype.name == "float64"


def test_to_numpy_min_object_list_for_non_numeric():
    arr = to_numpy(["x", "y"], dtype="min")
    assert arr.dtype == object
    assert arr.tolist() == ["x", "y"]


def test_to_numpy_unsupported_dtype_raises():
    with pytest.raises(ValueError):
        to_numpy([1, 2, 3], dtype="bogus")
