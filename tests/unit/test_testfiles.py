# pylint: disable=missing-docstring
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
"modified_date_out_of_range.jp2": "True"
}

## Excluded in above dict are:
#
# bitwiser-icc-corrupted-tagcount*.jp2: all True
# bitwiser-resolutionbox*.jp2: all False
# bitwiser-headerbox*.jp2: all False
# bitwiser-codestreamheader*.jp2: all False
#

def fileIsValid(testFile):
    VALIDATION_FORMAT = 'jp2'
    xmlElement = checkOneFile(testFile, VALIDATION_FORMAT)
    return xmlElement.findtext('./isValid')

def test_validity():
    for fileName, isValid in testFiles.items():
        testFile = os.path.join(testFilesDir, fileName)
        print(testFile)
        isValidJpylyzer = fileIsValid(testFile)
        assert isValidJpylyzer == isValid


