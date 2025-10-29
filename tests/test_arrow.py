import pytest

from toarray import to_arrow

pa = pytest.importorskip("pyarrow")  # skip if pyarrow missing


def test_to_arrow_min():
    arr = to_arrow([0, 1, 2], type="min")
    assert isinstance(arr, pa.Array)
    assert arr.to_pylist() == [0, 1, 2]


def test_to_arrow_chunked():
    arr = to_arrow(range(10), type="min", chunk_size=4)
    assert isinstance(arr, pa.ChunkedArray)
    assert arr.length() == 10


def test_to_arrow_explicit_float64_and_error():
    arr = to_arrow([0, 1, 2], type="float64")
    assert isinstance(arr, pa.Array)
    assert arr.type == pa.float64()
    with pytest.raises(ValueError):
        to_arrow([1, 2, 3], type="bogus")


def test_to_arrow_explicit_chunked_path():
    out = to_arrow(range(7), type="float64", chunk_size=3)
    assert isinstance(out, pa.ChunkedArray)
    assert out.length() == 7


def test_to_arrow_chunk_from_list_branch():
    # Non-numeric forces list path inside _to_arrow_chunk
    arr = to_arrow(["x", "y"], type="min")
    assert isinstance(arr, pa.Array)
    assert arr.to_pylist() == ["x", "y"]
