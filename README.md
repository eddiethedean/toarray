# toarray

Small Python package for converting iterables to the smallest fitting `array.array` type.

## Status

- Supports Python 3.9–3.13
- License: MIT

## Description

`toarray.get_array(iterable)` inspects the values and returns the smallest suitable
`array.array` when possible, otherwise it returns a plain `list`.

**Key Features:**
- 🎯 **Automatic type selection** - Finds the smallest fitting array type
- 💾 **Memory efficient** - Up to 24x memory savings vs Python lists
- ⚡ **Zero-copy interop** - Seamless conversion to NumPy/PyArrow without copying data
- 📊 **Memory reporting** - See exactly how much memory you're saving

## Where toarray Fits: Lists vs NumPy vs toarray

**Python Lists** (`list`)
- ✅ Flexible: any data type, dynamic size
- ✅ Simple: built-in, no dependencies
- ❌ Memory heavy: ~24 bytes per integer
- ❌ Slower: Python object overhead
- **Use when**: Small datasets, mixed types, simplicity matters

**NumPy Arrays** (`numpy.ndarray`)
- ✅ Fast: optimized C operations
- ✅ Rich ecosystem: thousands of functions
- ✅ Multi-dimensional: matrices, tensors
- ❌ Requires dependency: `numpy` package
- ❌ Manual dtype selection: you choose the type
- ❌ Less memory-efficient: often defaults to int64/float64
- **Use when**: Scientific computing, need NumPy operations, large-scale data analysis

**toarray** (`array.array` with auto-optimization)
- ✅ **Automatic optimization**: picks smallest type for you
- ✅ **Memory efficient**: 4-24x smaller than lists
- ✅ **Zero-copy interop**: seamless NumPy/PyArrow conversion
- ✅ **No dependencies**: uses stdlib `array.array`
- ✅ **Lightweight**: perfect for constrained environments
- ❌ Limited operations: use NumPy for advanced math
- ❌ One-dimensional: no matrices/tensors
- **Use when**: 
  - Memory-constrained environments (IoT, embedded)
  - Data pipelines needing efficient storage
  - Automatic dtype selection for NumPy/PyArrow
  - When you want list-like simplicity with array efficiency

### Quick Comparison

| Feature | `list` | `toarray` | `numpy.ndarray` |
|---------|--------|-----------|-----------------|
| Memory (1000 ints) | ~24 KB | ~1-4 KB | ~8 KB (int64) |
| Dependencies | None | None | numpy |
| Auto type selection | ❌ | ✅ | ❌ |
| Zero-copy to NumPy | ❌ | ✅ | N/A |
| Mathematical operations | ❌ | ❌ | ✅ |
| Multi-dimensional | ❌ | ❌ | ✅ |
| Best for | Small/mixed data | Memory optimization | Scientific computing |

### When to Use Each

```python
# Use list: Small, mixed-type data
data = ["name", 42, True]  # list is perfect

# Use toarray: Memory-constrained, automatic optimization
sensor_data = [20, 21, 22, ...]  # 10,000 readings
optimized = get_array(sensor_data)  # Auto uint8, 10KB vs 240KB

# Use NumPy: Scientific computing, operations needed
import numpy as np
arr = np.array([1, 2, 3])  # When you need np.mean(), np.dot(), etc.

# Use toarray → NumPy: Best of both worlds
from toarray import to_numpy
arr = to_numpy([0, 1, 255], dtype='min')  # Auto uint8, zero-copy!
# Now use NumPy operations on optimized array
```

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
from toarray import memory_report, get_memory_footprint

# Basic conversion - automatic type selection
get_array([0, 1, 255]).typecode  # 'B' (uint8)
get_array([-1, 0, 1]).typecode   # 'b' (int8)
get_array([1e-3, 2.5]).typecode  # 'f' (float32)
get_array(["a", "b"])          # ['a', 'b'] (non-numeric)
get_array([])                    # [] (empty)

# Memory efficiency reporting
report = memory_report([0, 1, 2, ..., 255])
print(report)
# List: 6,144 bytes | Array(B): 256 bytes | Savings: 5,888 bytes (95.8%)

# Performance optimization for large datasets
large_data = range(1_000_000)
arr = select_array(large_data, sample_size=1000)  # Fast type detection
```

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

# Zero-copy conversions to NumPy/PyArrow
# NumPy (pip install toarray[numpy])
from toarray import to_numpy
arr_np = to_numpy([0,1,2], dtype='min')     # dtype: uint8 (zero-copy!)
arr_np.flags.owndata  # False - shares memory with array.array
# Now use NumPy operations: arr_np.mean(), arr_np.sum(), etc.

# PyArrow (pip install toarray[arrow])
from toarray import to_arrow
arr_pa = to_arrow([0,1,2], type='min')                # pa.array([0, 1, 2], type=uint8) (zero-copy!)
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

### Performance Features

- **Early-exit optimization**: Stops scanning once bounds are known
- **Sampling mode**: Use `sample_size` parameter to limit type detection scanning
- **Zero-copy interop**: NumPy and PyArrow conversions share memory buffers

### Notes

- Non‑numeric input returns a `list` (text is not coerced to `array('u')`).
- Integer preference order: `B`, `b`, `H`, `h`, `I`, `i`, `Q`, `q`.
- Float preference order: `f` then `d` (subject to range and policy).

## Examples

See [EXAMPLES.md](EXAMPLES.md) for comprehensive examples including:
- Memory efficiency demonstrations
- Zero-copy conversion patterns
- Large dataset processing
- Real-world use cases (IoT, data pipelines, CSV processing)

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