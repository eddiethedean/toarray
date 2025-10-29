from array import array

from toarray import stream_array


def test_stream_basic_chunks():
    data = list(range(10))
    chunks = list(stream_array(data, chunk_size=3))
    # First chunk defines type
    assert isinstance(chunks[0], array)
    assert chunks[0].typecode in {"B", "b", "H", "h", "I", "i"}
    # All chunks yielded
    assert sum(len(list(c)) for c in chunks) == 10


def test_stream_widen_on_violation():
    # First chunk fits 'B'; second chunk contains -1 which violates 'B'
    data = [0, 1, 2] + [-1, 0, 1]
    chunks = list(stream_array(data, chunk_size=3))
    assert isinstance(chunks[0], array) and chunks[0].typecode == "B"
    # Violation yields list for that chunk
    assert isinstance(chunks[1], list)


def test_stream_empty_iterable():
    # Should iterate to nothing
    assert list(stream_array([], chunk_size=5)) == []


def test_stream_code_none_path_non_numeric():
    chunks = list(stream_array(["a", "b", 1], chunk_size=1))
    # With chunk_size=1, we exercise the in-loop branch (yield inside loop)
    assert all(isinstance(c, list) for c in chunks)


def test_stream_code_none_tail_flush():
    # First chunk non-numeric with size 3, then one leftover triggers tail flush branch
    chunks = list(stream_array(["a", "b", "c", "d"], chunk_size=3))
    assert isinstance(chunks[0], list)
    assert isinstance(chunks[1], list)
