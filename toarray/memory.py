"""
Memory efficiency utilities for toarray.

These utilities help demonstrate and measure the memory savings
achieved by using array.array instead of lists.
"""

from __future__ import annotations

from array import array
from collections.abc import Iterable
from dataclasses import dataclass
from sys import getsizeof

from .iterable_to_array import get_array

__all__ = ["memory_report", "get_memory_footprint", "MemoryReport"]


@dataclass
class MemoryReport:
    """Memory usage report comparing list vs array."""

    list_bytes: int
    array_bytes: int
    savings_bytes: int
    savings_ratio: float
    typecode: str | None
    count: int

    def __str__(self) -> str:
        if self.typecode is None:
            return f"List: {self.list_bytes:,} bytes (no array conversion possible)"
        savings_pct = (1 - self.savings_ratio) * 100
        return (
            f"List: {self.list_bytes:,} bytes | "
            f"Array({self.typecode}): {self.array_bytes:,} bytes | "
            f"Savings: {self.savings_bytes:,} bytes ({savings_pct:.1f}%)"
        )


def get_memory_footprint(obj: array | list) -> int:
    """
    Get the memory footprint of an array or list in bytes.

    For arrays, this includes the array object overhead plus the data.
    For lists, this includes the list object overhead plus all items.

    Args:
        obj: An array.array or list to measure

    Returns:
        Estimated memory footprint in bytes
    """
    if isinstance(obj, array):
        # Array object overhead + data
        return getsizeof(obj) + obj.buffer_info()[1] * obj.itemsize
    elif isinstance(obj, list):
        # List object overhead + items
        base = getsizeof(obj)
        # Rough estimate: each item has pointer overhead
        # This is approximate; actual size depends on object types
        item_overhead = getsizeof(obj[0]) if obj else 0
        return base + sum(getsizeof(item) for item in obj)
    else:
        return getsizeof(obj)


def memory_report(
    iterable: Iterable,
    *,
    include_list: bool = True,
) -> MemoryReport:
    """
    Generate a memory usage report comparing list vs array representation.

    This function demonstrates the memory savings achieved by converting
    an iterable to the smallest fitting array.array type.

    Args:
        iterable: The iterable to analyze
        include_list: If True, measure list memory (may be expensive for large iterables)

    Returns:
        MemoryReport with memory usage comparison

    Example:
        >>> report = memory_report([0, 1, 2, ..., 255])
        >>> print(report)
        List: 6,144 bytes | Array(B): 256 bytes | Savings: 5,888 bytes (95.8%)
    """
    values = list(iterable)
    count = len(values)

    # Get optimized array
    arr = get_array(values)

    # Calculate array memory
    if isinstance(arr, array):
        array_bytes = get_memory_footprint(arr)
        typecode = arr.typecode
    else:
        # Fallback to list
        array_bytes = get_memory_footprint(arr) if arr else 0
        typecode = None

    # Calculate list memory (if requested)
    if include_list:
        list_bytes = get_memory_footprint(values)
    else:
        # Estimate: assume 24 bytes per integer in list (Python object overhead)
        # This is approximate but avoids materializing large lists
        list_bytes = count * 24 if count > 0 else 0

    savings_bytes = list_bytes - array_bytes if typecode else 0
    savings_ratio = array_bytes / list_bytes if list_bytes > 0 and typecode else 1.0

    return MemoryReport(
        list_bytes=list_bytes,
        array_bytes=array_bytes,
        savings_bytes=savings_bytes,
        savings_ratio=savings_ratio,
        typecode=typecode,
        count=count,
    )

