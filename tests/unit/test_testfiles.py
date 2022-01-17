#! /usr/bin/env python3
# pylint: disable=missing-docstring
"""
Tests on jpylyzer test corpus files
TODO:
- Automatically fetch test files from Github
- Get rid of testFilesDir (is there some standard location
  for tests?)
- Perhaps read dictionary of tests files from CSV file (to be
  added to test-files repo)
- Look for better way to handle same test on different files
  (tracing back failed tests to respective files now relies on print
  statement, there must be better ways to do this?)
- Add tests for specific features/oddities (but see previous point)
"""

import sys
import os
from xml.dom.minidom import Element
from xml.etree.ElementTree import ElementTree
import pytest

from jpylyzer.jpylyzer import checkOneFile
import jpylyzer.config as config

testFilesDir = "/home/johan/jpylyzer-test-files/"

# Dictionary with names of all test files and validity
testFiles = {
"reference.jp2": "True",
"signature_corrupted.jp2": "False",
"invalid_character_in_xml.jp2": "False",
"invalid_character_in_codestream_comment.jp2": "False",
"null_character_in_codestream_comment.jp2": "False",
"missing_null_terminator_in_urlbox.jp2": "False",
"last_byte_missing.jp2": "False",
"truncated_at_byte_5000.jp2": "False",
"data_missing_in_last_tilepart.jp2": "False",
"meth_is_2_no_icc.jp2": "False",
"height_image_header_damaged.jp2": "False",
"triggerUnboundLocalError.jp2": "False",
"modified_date_out_of_range.jp2": "True",
"ランダム日本語テキスト.jp2": "True",
"隨機中國文字.jp2": "True",
"is_codestream.jp2": "False",
"is_jpx.jp2": "False",
"is_jpm.jp2": "False",
"is_jpeg.jp2": "False",
"jpx_disguised_as_jp2.jp2": "False",
"kakadu61.jp2": "True",
"kakadu71.jp2": "True",
"aware.jp2": "True",
"openJPEG15.jp2": "True",
"graphicsMagick.jp2": "True",
"oj-illegal-rcom-value.jp2": "False",
"oj-tnsot-0.jp2": "True",
"oj-ytsiz-not-valid-1.jp2": "False",
"oj-ytsiz-not-valid-2.jp2": "False",
"oj-xtsiz-not-valid-1.jp2": "False",
"oj-issue363-4740.jp2": "False",
"oj-poc-main-header.jp2": "True",
"oj-rgn-main-header-1.jp2": "True",
"oj-rgn-tilepart-header-1.jp2": "True",
"oj-plm-main-header.jp2": "False",
"oj-ppm-main-header-1.jp2": "False",
"oj-ppm-main-header-2.jp2": "False",
"oj-ppm-main-header-3.jp2": "False",
"oj-ppt-tilepart-header.jp2": "False",
"tika-tlm-main-header.jp2": "True",
"tika-crg-main-header.jp2": "True",
"null_terminated_content_in_xml_box.jp2": "False",
"palettedImage.jp2": "True",
"sentinel.jp2": "True",
"bitwiser-codestreamheader-corrupted-xsiz-10918.jp2": "False",
"bitwiser-codestreamheader-corrupted-xsiz-10928.jp2": "False",
"bitwiser-codestreamheader-corrupted-xsiz-10937.jp2": "False",
"bitwiser-codestreamheader-corrupted-xsiz-10946.jp2": "False",
"bitwiser-codestreamheader-corrupted-xsiz-10955.jp2": "False",
"bitwiser-codestreamheader-corrupted-ysiz-11208.jp2": "False",
"bitwiser-codestreamheader-corrupted-ysiz-11218.jp2": "False",
"bitwiser-codestreamheader-corrupted-ysiz-11227.jp2": "False",
"bitwiser-codestreamheader-corrupted-ysiz-11238.jp2": "False",
"bitwiser-codestreamheader-corrupted-ysiz-11252.jp2": "False",
"bitwiser-headerbox-corrupted-boxlength-22181.jp2": "False",
"bitwiser-icc-corrupted-tagcount-1911.jp2": "True",
"bitwiser-icc-corrupted-tagcount-1920.jp2": "True",
"bitwiser-icc-corrupted-tagcount-1937.jp2": "True",
"bitwiser-icc-corrupted-tagcount-1951.jp2": "True",
"bitwiser-icc-corrupted-tagcount-1961.jp2": "True",
"bitwiser-icc-corrupted-tagcount-1971.jp2": "True",
"bitwiser-icc-corrupted-tagcount-1984.jp2": "True",
"bitwiser-icc-corrupted-tagcount-1999.jp2": "True",
"bitwiser-icc-corrupted-tagcount-2011.jp2": "True",
"bitwiser-icc-corrupted-tagcount-2021.jp2": "True",
"bitwiser-resolutionbox-corrupted-boxlength-8127.jp2": "False",
"bitwiser-resolutionbox-corrupted-boxlength-8154.jp2": "False",
"bitwiser-resolutionbox-corrupted-boxlength-8730.jp2": "False",
"oj-tileindex-error-1.jp2": "False",
"oj-tileindex-error-2.jp2": "False",
"oj-tileindex-error-3.jp2": "False",
"oj-tileindex-error-4.jp2": "False",
"oj-tileindex-error-5.jp2": "False"
}

## Excluded in above dict are:
#
# - 3 surrogate pair samples: needs separate test

def test_validity():
    """
    Tests validation outcome of all test files against known validity
    """
    for fileName, isValid in testFiles.items():
        testFile = os.path.join(testFilesDir, fileName)
        print(testFile)
        outJpylyzer = checkOneFile(testFile, 'jp2')
        assert outJpylyzer.findtext('./statusInfo/success') == "True"
        assert outJpylyzer.findtext('./isValid') == isValid

def test_surrogatepairs():
    """
    Test handling of files with surrogate pairs in file name
    """
    pass

def test_emptyfile():
    """
    Test handling of empty files
    """
    testFile = os.path.join(testFilesDir, "empty.jp2")
    print(testFile)
    outJpylyzer = checkOneFile(testFile, 'jp2')
    assert outJpylyzer.findtext('./statusInfo/success') == "True"
