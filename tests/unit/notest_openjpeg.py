#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""
Tests on openjeg-data test corpus files.

Pre-condition:

Contents of openjpeg-data repo (https://github.com/uclouvain/openjpeg-data)
are present in sibling directory relative to jpylyzer dir, e.g.:

        |-- jpylyzer/
home/ --|      
        |--openjpeg-data/

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
testFilesDir = JPYLYZER_DIR.replace("jpylyzer", "openjpeg-data")
#testFilesDir = os.path.join(testFilesDir, "input/conformance")

# All files in test files directory tree. Includes many
# files in other (not JPEG 2000) formats but for the purpose
# of these tests that doesn't matter
testFiles = glob.glob(testFilesDir + "/**", recursive=True)
testFiles = [f for f in testFiles if os.path.isfile(f)]

config.INPUT_WRAPPER_FLAG = True

@pytest.mark.parametrize('input', testFiles)

def test_status_jp2(input):
    """
    Tests for any internal errors based on statusInfo value
    using JP2 validation
    """
    outJpylyzer = checkOneFile(input, 'jp2')
    assert outJpylyzer.findtext('./statusInfo/success') == "True"

@pytest.mark.parametrize('input', testFiles)

def test_status_j2c(input):
    """
    Tests for any internal errors based on statusInfo value
    using codestream validation
    """
    outJpylyzer = checkOneFile(input, 'j2c')
    assert outJpylyzer.findtext('./statusInfo/success') == "True"

def test_xml_is_valid_jp2(capsys):
    """
    Run checkfiles function on all files in test corpus and
    verify resulting XML output validates against XSD schema
    """
    config.VALIDATION_FORMAT = "jp2"
    checkFiles(False, True, testFiles)
    
    # Capture output from stdout
    captured = capsys.readouterr()
    xmlOut = captured.out
    # Parse XSD schema
    xmlschema_doc = etree.parse(xsdFile)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    # Parse XML
    xml_doc = etree.fromstring(xmlOut.encode())
    assert xmlschema.validate(xml_doc)

def test_xml_is_valid_j2c(capsys):
    """
    Run checkfiles function on all files in test corpus and
    verify resulting XML output validates against XSD schema
    """
    config.VALIDATION_FORMAT = "j2c"
    checkFiles(False, True, testFiles)
    
    # Capture output from stdout
    captured = capsys.readouterr()
    xmlOut = captured.out
    # Parse XSD schema
    xmlschema_doc = etree.parse(xsdFile)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    # Parse XML
    xml_doc = etree.fromstring(xmlOut.encode())
    assert xmlschema.validate(xml_doc)