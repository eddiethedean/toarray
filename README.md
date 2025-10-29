# toarray

Small Python package for converting iterables to the smallest fitting `array.array` type.

## Status

- Supports Python 3.9–3.13
- License: MIT

## Description

`toarray.get_array(iterable)` inspects the values and returns the smallest suitable
`array.array` when possible, otherwise it returns a plain `list`.

Rules of thumb:
- Non-numeric values → returns `list`
- Integers → prefers `B`, `b`, `H`, `h`, `I`, `i`, `Q`, `q` (in that order)
- Floats → tries `f` then `d`
- Empty iterables → returns `[]`

Note: Unicode arrays (`array('u')`) are deprecated/removed in modern Python and are not used.

## Install

```bash
pip install toarray
# optional extras
pip install toarray[numpy]
pip install toarray[arrow]
```

## Usage

```python
from toarray import get_array, select_array, analyze_array, stream_array

get_array([0, 1, 255]).typecode  # 'B'
get_array([-1, 0, 1]).typecode   # 'b'
get_array([1e-3, 2.5]).typecode  # 'f'
get_array(["a", "b"])          # ['a', 'b']
get_array([])                    # []

# Policy-based selection (control bounds and strategy)
arr = select_array(
    [0, 1, 256],
    policy='smallest',      # 'smallest' | 'balanced' | 'wide'
    prefer_signed=False,
    min_type=None,          # e.g. 'h', 'i', 'q', 'f', 'd'
    max_type=None,
)

# Metadata
info = analyze_array([1, 2, 3])
info.typecode, info.min, info.max     # ('B', 1.0, 3.0)

# Streaming
for chunk in stream_array(range(1000), chunk_size=256):
    pass

# Optional extras
# NumPy (pip install toarray[numpy])
from toarray import to_numpy
arr_np = to_numpy([0,1,2], dtype='min')     # dtype: uint8
arr_np_exp = to_numpy([0,1,2], dtype='float64')  # dtype: float64

# PyArrow (pip install toarray[arrow])
from toarray import to_arrow
arr_pa = to_arrow([0,1,2], type='min')                # pa.array([0, 1, 2], type=uint8)
arr_pa_chunked = to_arrow(range(10), type='float64', chunk_size=4)  # pa.ChunkedArray
```

### Selection policies and strict mode

- Policies adjust the candidate order searched for a fit:
  - `smallest`: smallest footprint first (default)
  - `balanced`: mildly prefers signed widths early
  - `wide`: wider integer types first
- Bounds: `min_type`/`max_type` let you constrain the search (e.g., up to `i` only).
- Floats: `allow_float_downgrade=False` skips `f` when magnitudes exceed float32.
- `no_float=True` forces integers only; with `strict=True` this raises on floats.

### Notes

- Non‑numeric input returns a `list` (text is not coerced to `array('u')`).
- Integer preference order: `B`, `b`, `H`, `h`, `I`, `i`, `Q`, `q`.
- Float preference order: `f` then `d` (subject to range and policy).

## Development

This project uses `pytest`, `ruff`, and `black`.

```bash
pip install -e .[dev]
ruff check .
black --check .
pytest
```

## Authors

Odos Matthews — odosmatthews@gmail.com

## License

MIT — see `LICENSE.md` for details