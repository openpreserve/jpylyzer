#! /usr/bin/env python3
# pylint: disable=missing-docstring
"""
Tests on jpylyzer test corpus files.

Pre-condition:

Contents of jpylyzer-test-files repo (https://github.com/openpreserve/jpylyzer-test-files)
are present in sibling directory relative to jpylyzer dir, e.g.:

        |-- jpylyzer/
home/ --|      
        |--jpylyzer-test-files/

TODO:
- Automatically fetch test files from Github
- Perhaps read dictionary of tests files from CSV file (to be
  added to test-files repo)
- Add tests for specific features/oddities (but see previous point)
"""

import os
import glob
import pytest
from lxml import etree

from jpylyzer import config
from jpylyzer.jpylyzer import checkOneFile
from jpylyzer.jpylyzer import checkFiles

# Directory that contains this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Root dir of jpylyzer repo
JPYLYZER_DIR = os.path.split(os.path.split(SCRIPT_DIR)[0])[0]

# XSD file (path resolved from SCRIPT_DIR)
xsdFile = os.path.join(JPYLYZER_DIR, "xsd/jpylyzer-v-2-1.xsd")

# Directory with test files
testFilesDir = "/home/johan/openjpeg-data/input/conformance"

# All files in test files dir
testFiles = glob.glob(testFilesDir + "/**", recursive=True)
testFiles = [f for f in testFiles if os.path.isfile(f)]

@pytest.mark.parametrize('input', testFiles)

def test_xml_onefile(input):
    config.INPUT_WRAPPER_FLAG = True
    config.VALIDATION_FORMAT = "jp2"
    filesIn = [input]
    checkFiles(False, True, filesIn)
