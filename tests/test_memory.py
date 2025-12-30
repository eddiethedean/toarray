from array import array

from toarray import get_memory_footprint, memory_report


def test_memory_footprint_array():
    arr = array("B", [0, 1, 2, 255])
    size = get_memory_footprint(arr)
    assert size > 0
    # Should be roughly: array overhead + 4 bytes (4 * uint8)
    assert size < 100  # Reasonable upper bound


def test_memory_footprint_list():
    lst = [0, 1, 2, 255]
    size = get_memory_footprint(lst)
    assert size > 0
    # Lists have more overhead per item
    assert size > get_memory_footprint(array("B", lst))


def test_memory_report_numeric():
    data = list(range(256))  # 0-255 fits in uint8
    report = memory_report(data)

    assert report.count == 256
    assert report.typecode == "B"
    assert report.list_bytes > report.array_bytes
    assert report.savings_bytes > 0
    assert report.savings_ratio < 1.0  # Array should be smaller


def test_memory_report_non_numeric():
    data = ["a", "b", "c"]
    report = memory_report(data)

    assert report.count == 3
    assert report.typecode is None  # Can't convert to array
    assert report.array_bytes >= 0


def test_memory_report_empty():
    report = memory_report([])
    assert report.count == 0
    assert report.list_bytes >= 0
    assert report.array_bytes >= 0


def test_memory_report_string_representation():
    data = list(range(10))
    report = memory_report(data)
    str_repr = str(report)
    assert "bytes" in str_repr.lower()
    assert report.typecode in str_repr or "no array" in str_repr.lower()


def test_memory_report_without_list():
    # Test that include_list=False works
    data = list(range(100))
    report = memory_report(data, include_list=False)
    assert report.count == 100
    # Should still work, just estimates list size
    assert report.list_bytes > 0

