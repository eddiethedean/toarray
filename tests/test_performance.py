from array import array

import pytest

from toarray import select_array


def test_sample_size_limits_scanning():
    """Test that sample_size limits min/max scanning but still processes all items."""
    # Create a large iterable
    large_data = list(range(1000))

    # With sample_size, should still work correctly
    result = select_array(large_data, sample_size=100)
    assert isinstance(result, array)
    assert result.typecode in {"B", "b", "H", "h", "I", "i", "q", "Q"}
    assert len(result) == 1000  # All items processed


def test_sample_size_small_sample():
    """Test sample_size with small sample."""
    data = [0, 1, 2, 255]
    result = select_array(data, sample_size=2)
    assert isinstance(result, array)
    # Should still detect correct type from sample
    assert result.typecode in {"B", "b", "H", "h", "I", "i", "q", "Q"}


def test_early_exit_large_integers():
    """Test that early-exit works for large integers."""
    # Values that require 64-bit
    large_data = [2**40, 2**41, 2**42]

    result = select_array(large_data)
    assert isinstance(result, array)
    # Should be Q (uint64) or q (int64)
    assert result.typecode in {"Q", "q"}


def test_sample_size_none_uses_all():
    """Test that sample_size=None scans all items."""
    data = list(range(100))
    result1 = select_array(data, sample_size=None)
    result2 = select_array(data, sample_size=1000)  # Larger than data

    assert result1.typecode == result2.typecode
    assert list(result1) == list(result2)


def test_sample_size_with_non_numeric():
    """Test sample_size behavior with non-numeric data."""
    data = [1, 2, 3, "x", 4, 5]
    result = select_array(data, sample_size=2)
    # Should return list due to non-numeric
    assert isinstance(result, list)
    assert result == data

