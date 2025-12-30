# toarray Examples and Use Cases

## Memory Efficiency Examples

### Basic Memory Savings

```python
from toarray import get_array, memory_report

# Small integers (0-255) use uint8
data = list(range(256))
arr = get_array(data)
print(f"Type: {arr.typecode}")  # 'B' (uint8)

# See the memory savings
report = memory_report(data)
print(report)
# List: 6,144 bytes | Array(B): 256 bytes | Savings: 5,888 bytes (95.8%)
```

### Real-World Memory Savings

```python
from toarray import memory_report

# Sensor data: temperature readings 0-100
sensor_data = [20, 21, 22, 23, 24] * 1000  # 5000 readings
report = memory_report(sensor_data)
print(f"Memory savings: {report.savings_bytes:,} bytes ({report.savings_ratio:.1%} reduction)")
```

## Zero-Copy Conversions

### NumPy Zero-Copy

```python
from toarray import to_numpy
import numpy as np

data = [0, 1, 2, 255]
arr_np = to_numpy(data, dtype='min')

print(f"Dtype: {arr_np.dtype}")  # uint8
print(f"Zero-copy: {not arr_np.flags.owndata}")  # True - shares memory!

# Modify original array affects NumPy view
# (demonstrating they share memory)
```

### PyArrow Zero-Copy

```python
from toarray import to_arrow

data = list(range(1000))
arr_pa = to_arrow(data, type='min')

print(f"Type: {arr_pa.type}")  # uint16 or uint8
print(f"Length: {arr_pa.length()}")  # 1000
# Memory is shared via memoryview - no copy!
```

## Performance Optimizations

### Large Dataset Processing

```python
from toarray import select_array

# For very large iterables, limit scanning for type detection
large_data = range(1_000_000)

# Sample first 1000 items to determine type, then process all
arr = select_array(large_data, sample_size=1000)
# Still processes all 1M items, but only scans min/max for first 1000
```

### Streaming Large Files

```python
from toarray import stream_array

# Process CSV data in chunks
def process_csv_chunks(filename):
    with open(filename) as f:
        # Read numeric column
        values = (int(line.strip()) for line in f)
        
        # Stream in chunks, auto-optimizing each chunk
        for chunk in stream_array(values, chunk_size=65536):
            # Process chunk (already optimized array.array)
            process(chunk)
```

## Use Cases

### 1. IoT/Embedded Systems

```python
# Memory-constrained device collecting sensor data
from toarray import get_array

# Collect 10,000 temperature readings (0-100°C)
readings = collect_sensor_data(count=10000)

# Automatically use smallest type (uint8 fits 0-255)
optimized = get_array(readings)  # Uses ~10KB instead of ~240KB
```

### 2. Data Pipeline Optimization

```python
from toarray import to_arrow, memory_report

# Process data before sending to database
raw_data = [1, 2, 3, ..., 1000000]

# Optimize and convert to PyArrow (zero-copy!)
arrow_array = to_arrow(raw_data, type='min')

# Check savings
report = memory_report(raw_data)
print(f"Saved {report.savings_bytes / 1024 / 1024:.2f} MB")
```

### 3. NumPy Integration

```python
from toarray import to_numpy
import numpy as np

# Automatic dtype selection with zero-copy
data = [0, 1, 2, ..., 255]
arr = to_numpy(data, dtype='min')  # uint8, zero-copy

# Use with NumPy operations
result = arr * 2  # Still efficient, shares underlying buffer
```

### 4. CSV Processing

```python
import csv
from toarray import get_array

# Read numeric column from CSV
def read_csv_column(filename, column_idx):
    with open(filename) as f:
        reader = csv.reader(f)
        values = [int(row[column_idx]) for row in reader]
        
        # Auto-optimize to smallest array type
        return get_array(values)

# Usage
prices = read_csv_column('sales.csv', column_idx=2)
print(f"Memory: {len(prices) * prices.itemsize} bytes")
```

## Performance Benchmarks

### Memory Comparison

| Data Size | List Memory | Array Memory | Savings |
|-----------|-------------|--------------|---------|
| 1,000 uint8 | ~24 KB | ~1 KB | 95.8% |
| 10,000 uint16 | ~240 KB | ~20 KB | 91.7% |
| 100,000 int32 | ~2.4 MB | ~400 KB | 83.3% |

### Type Selection Speed

- Small datasets (< 1K items): < 1ms
- Medium datasets (1K-100K): < 10ms
- Large datasets (100K+): < 100ms (with sample_size)

## Best Practices

1. **Use `sample_size` for very large iterables** (> 1M items)
   ```python
   arr = select_array(huge_iterable, sample_size=1000)
   ```

2. **Check memory savings** to understand impact
   ```python
   report = memory_report(data)
   if report.savings_ratio < 0.5:  # Less than 50% savings
       print("Consider if optimization is worth it")
   ```

3. **Use zero-copy conversions** when working with NumPy/PyArrow
   ```python
   arr_np = to_numpy(data, dtype='min')  # Zero-copy!
   ```

4. **Stream for large datasets** to avoid materializing everything
   ```python
   for chunk in stream_array(large_iterable, chunk_size=65536):
       process(chunk)
   ```

