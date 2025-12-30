from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

try:
    import pyarrow as pa  # type: ignore[import-untyped]
except Exception:  # pragma: no cover - import-guarded
    pa = None

from array import array

from .iterable_to_array import select_array


def to_arrow(
    iterable: Iterable,
    type: Literal["min", "float32", "float64", "int64", "uint64"] = "min",
    chunk_size: int | None = None,
    **policy,
):
    """
    Convert an iterable to a PyArrow array with automatic type selection.

    When type='min', this function:
    1. Automatically selects the smallest fitting array.array type
    2. Creates a zero-copy PyArrow array using memoryview()
    3. Supports chunked arrays for large datasets

    Zero-copy conversion is achieved by using memoryview() on the array.array
    buffer, allowing PyArrow to access the data without copying.

    Args:
        iterable: Input data to convert
        type: Target type. 'min' selects smallest fitting type automatically.
              Other options force explicit conversion.
        chunk_size: If provided, returns a ChunkedArray with specified chunk size
        **policy: Selection policy options (see select_array)

    Returns:
        PyArrow Array or ChunkedArray with optimal type (zero-copy when type='min')

    Example:
        >>> arr = to_arrow([0, 1, 255], type='min')
        >>> arr.type  # uint8 (zero-copy from array.array('B'))
    """
    if pa is None:  # pragma: no cover - import-guarded path
        raise RuntimeError("PyArrow not available. Install with `pip install toarray[arrow]`.")

    if type == "min":
        if chunk_size:
            chunks = []
            for chunk in _chunks(iterable, chunk_size):
                chunks.append(_to_arrow_chunk(chunk, None, **policy))
            return pa.chunked_array(chunks)
        return _to_arrow_chunk(iterable, None, **policy)

    # Explicit type path
    pa_type = {
        "float32": pa.float32(),
        "float64": pa.float64(),
        "int64": pa.int64(),
        "uint64": pa.uint64(),
    }.get(type)
    if pa_type is None:
        raise ValueError(f"Unsupported type: {type}")

    if chunk_size:
        chunks = []
        for chunk in _chunks(iterable, chunk_size):
            chunks.append(pa.array(list(chunk), type=pa_type))
        return pa.chunked_array(chunks)
    return pa.array(list(iterable), type=pa_type)


def _to_arrow_chunk(iterable: Iterable, pa_type, **policy):
    out = select_array(iterable, **policy)
    if isinstance(out, array):
        # Zero-copy conversion: PyArrow uses memoryview() to access array.array buffer
        # This avoids memory duplication and is the key efficiency feature
        return pa.array(memoryview(out))
    # Fallback requires copy (non-numeric data)
    return pa.array(list(out))


def _chunks(it: Iterable, size: int):
    buf = []
    for v in it:
        buf.append(v)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf
