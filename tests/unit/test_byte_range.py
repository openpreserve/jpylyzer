#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""The contiguous codestream box is read in place through ByteRange, not copied."""

import itertools
import mmap
import os
import tracemalloc

import pytest

from jpylyzer.jpylyzer import checkOneFile
from jpylyzer.validator import ByteRange

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
BALLOON = os.path.join(SCRIPT_DIR, "..", "..", "example_files", "balloon.jp2")

DATA = bytes(range(256)) * 4
BOUNDS = [-9999, -300, -1, 0, 1, 7, 255, 1023, 1024, 1025, 5000, None]


@pytest.mark.parametrize("start,stop", [(0, len(DATA)), (8, 1000), (100, 50),
                                        (8, -9991), (2000, 3000), (1000, 2 ** 64)])
def test_slices_match_bytes_slicing(start, stop):
    """Every slice of a ByteRange equals the same slice of the copied bytes,
    including the negative and out-of-range bounds that corrupt box lengths
    produce (e.g. the -9999 sentinel)."""
    expected = DATA[start:stop]
    window = ByteRange(DATA, start, stop)
    assert len(window) == len(expected)
    for low, high in itertools.product(BOUNDS, BOUNDS):
        assert window[low:high] == expected[low:high], (start, stop, low, high)


def test_index_matches_bytes_indexing():
    window = ByteRange(DATA, 10, 20)
    assert [window[i] for i in range(-10, 10)] == [DATA[10:20][i] for i in range(-10, 10)]
    with pytest.raises(IndexError):
        window[10]
    with pytest.raises(IndexError):
        ByteRange(DATA, 5, 5)[0]


def test_extended_slices_are_rejected():
    with pytest.raises(ValueError):
        ByteRange(DATA, 0, 10)[::2]


def test_slices_of_a_memory_map_leave_it_closable():
    with open(BALLOON, "rb") as f:
        fileData = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    marker = ByteRange(fileData, 2929, len(fileData))[0:2]
    assert marker == b'\xff\x4f'
    fileData.close()


def test_codestream_is_not_copied_into_memory():
    """Peak Python allocation stays well below the file size: copying the
    codestream box out of the memory map costs about the whole file."""
    size = os.path.getsize(BALLOON)
    checkOneFile(BALLOON)
    tracemalloc.start()
    try:
        result = checkOneFile(BALLOON)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert result.findtext("isValid") == "True"
    assert peak < size / 2
