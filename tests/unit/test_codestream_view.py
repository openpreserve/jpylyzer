#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""The contiguous codestream box is validated in place, not copied."""

import os
import tracemalloc

from jpylyzer.jpylyzer import checkOneFile

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
BALLOON = os.path.join(SCRIPT_DIR, "..", "..", "example_files", "balloon.jp2")


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


def test_repeated_validation_releases_the_memory_map():
    """No view of the codestream survives validation; a surviving view would
    make closing the memory map raise BufferError (reported as a failure)."""
    for _ in range(3):
        result = checkOneFile(BALLOON, "jp2", True, True)
        assert result.findtext("statusInfo/success") == "True"
