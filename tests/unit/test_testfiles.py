#! /usr/bin/env python3
# -*- coding: utf-8 -*-
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
xsdFile = os.path.join(JPYLYZER_DIR, "xsd/jpylyzer-v-2-2.xsd")

# Directory with test files
testFilesDir = JPYLYZER_DIR.replace("jpylyzer", "jpylyzer-test-files/files")

# All files in test files dir
testFiles = glob.glob(os.path.join(testFilesDir, '*'))

# Dictionary with names of all test files and validity against JP2
validityLookupJP2 = {
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
"erdas-nullinput-uint8-rgb-null-2tileparts.jp2": "True",
"erdas-sandiego1m_null.jp2": "True",
"erdas-sandiego3i_5.2.jp2": "True",
"erdas-sandiego3i_5.5.jp2": "True"
}

# Dictionary with names of all test files and validity against codestream
validityLookupJ2C = {
"is_codestream.jp2": "True"
}

# Dictionary with names of all test files and validity against JPH
validityLookupJPH = {
"oht-ht.jph": "False",
"oj-ht-byte.jph": "True"
}

# Dictionary with names of all test files and validity against JHC
validityLookupJHC = {
"grok-ht.jhc": "True",
"htj2k_cpf_broadcast.jhc": "False",
"oht-ht.jhc": "True",
"oj-ht-byte_causal.jhc": "True",
"ojph-ht.jhc": "True"
}

## Excluded in above dict are:
#
# - 3 surrogate pair samples

config.INPUT_WRAPPER_FLAG = True

def test_groundtruth_complete():
    """
    Test if all files in validityLookup
    dictionaries really exist
    """
    for key in validityLookupJP2:
        thisFile = os.path.join(testFilesDir, key)
        assert os.path.isfile(thisFile)

    for key in validityLookupJ2C:
        thisFile = os.path.join(testFilesDir, key)
        assert os.path.isfile(thisFile)

    for key in validityLookupJPH:
        thisFile = os.path.join(testFilesDir, key)
        assert os.path.isfile(thisFile)

    for key in validityLookupJHC:
        thisFile = os.path.join(testFilesDir, key)
        assert os.path.isfile(thisFile)


@pytest.mark.parametrize('inJP2', testFiles)

def test_status_jp2(inJP2):
    """
    Tests for any internal errors based on statusInfo value
    using JP2 validation
    """
    outJpylyzer = checkOneFile(inJP2, 'jp2')
    assert outJpylyzer.findtext('./statusInfo/success') == "True"

@pytest.mark.parametrize('inJ2C', testFiles)

def test_status_j2c(inJ2C):
    """
    Tests for any internal errors based on statusInfo value
    using codestream validation
    """
    outJpylyzer = checkOneFile(inJ2C, 'j2c')
    assert outJpylyzer.findtext('./statusInfo/success') == "True"

@pytest.mark.parametrize('inJPH', testFiles)

def test_status_jph(inJPH):
    """
    Tests for any internal errors based on statusInfo value
    using codestream validation
    """
    outJpylyzer = checkOneFile(inJPH, 'jph')
    assert outJpylyzer.findtext('./statusInfo/success') == "True"

@pytest.mark.parametrize('inJHC', testFiles)

def test_status_jhc(inJHC):
    """
    Tests for any internal errors based on statusInfo value
    using codestream validation
    """
    outJpylyzer = checkOneFile(inJHC, 'jhc')
    assert outJpylyzer.findtext('./statusInfo/success') == "True"

@pytest.mark.parametrize('inJP2', testFiles)

def test_validation_outcome_jp2(inJP2):
    """
    Tests validation outcome against known validity (JP2)
    """
    fName = os.path.basename(inJP2)
    outJpylyzer = checkOneFile(inJP2, 'jp2')
    if fName in validityLookupJP2.keys():
        isValid = validityLookupJP2[fName]
        assert outJpylyzer.findtext('./isValid') == isValid

@pytest.mark.parametrize('inJ2C', testFiles)

def test_validation_outcome_j2c(inJ2C):
    """
    Tests validation outcome against known validity
    (codestream format)
    """
    fName = os.path.basename(inJ2C)
    outJpylyzer = checkOneFile(inJ2C, 'j2c')
    if fName in validityLookupJ2C.keys():
        isValid = validityLookupJ2C[fName]
        assert outJpylyzer.findtext('./isValid') == isValid

@pytest.mark.parametrize('inJPH', testFiles)

def test_validation_outcome_jp2(inJPH):
    """
    Tests validation outcome against known validity (JPH)
    """
    fName = os.path.basename(inJPH)
    outJpylyzer = checkOneFile(inJPH, 'jph')
    if fName in validityLookupJPH.keys():
        isValid = validityLookupJPH[fName]
        assert outJpylyzer.findtext('./isValid') == isValid

@pytest.mark.parametrize('inJHC', testFiles)
def test_validation_outcome_jp2(inJHC):
    """
    Tests validation outcome against known validity (JHC)
    """
    fName = os.path.basename(inJHC)
    outJpylyzer = checkOneFile(inJHC, 'jhc')
    if fName in validityLookupJHC.keys():
        isValid = validityLookupJHC[fName]
        assert outJpylyzer.findtext('./isValid') == isValid

def test_xml_is_valid_jp2(capsys):
    """
    Run checkfiles function on all files in test corpus and
    verify resulting XML output validates against XSD schema
    """
    config.VALIDATION_FORMAT = "jp2"
    checkFiles(config.INPUT_RECURSIVE_FLAG, testFiles)

    # Capture output from stdout
    captured = capsys.readouterr()
    xmlOut = captured.out
    # Parse XSD schema
    xmlschema_doc = etree.parse(xsdFile)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    # Parse XML
    xml_doc = etree.fromstring(xmlOut.encode())
    assert xmlschema.validate(xml_doc)

def test_xml_mix_1(capsys):
    """
    Check if output validates for reporting MIX 1 output
    """
    config.VALIDATION_FORMAT = "jp2"
    config.MIX_FLAG = 1
    checkFiles(config.INPUT_RECURSIVE_FLAG, testFiles)

    # Capture output from stdout
    captured = capsys.readouterr()
    xmlOut = captured.out
    # Parse XSD schema
    xmlschema_doc = etree.parse(xsdFile)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    # Parse XML
    xml_doc = etree.fromstring(xmlOut.encode())
    assert xmlschema.validate(xml_doc)

def test_xml_mix_2(capsys):
    """
    Check if output validates for reporting MIX 2 output
    """
    config.VALIDATION_FORMAT = "jp2"
    config.MIX_FLAG = 2
    checkFiles(config.INPUT_RECURSIVE_FLAG, testFiles)

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
    config.MIX_FLAG = 0
    checkFiles(config.INPUT_RECURSIVE_FLAG, testFiles)

    # Capture output from stdout
    captured = capsys.readouterr()
    xmlOut = captured.out
    # Parse XSD schema
    xmlschema_doc = etree.parse(xsdFile)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    # Parse XML
    xml_doc = etree.fromstring(xmlOut.encode())
    assert xmlschema.validate(xml_doc)

def test_xml_is_valid_jph(capsys):
    """
    Run checkfiles function on all files in test corpus and
    verify resulting XML output validates against XSD schema
    """
    config.VALIDATION_FORMAT = "jph"
    config.MIX_FLAG = 0
    checkFiles(config.INPUT_RECURSIVE_FLAG, testFiles)

    # Capture output from stdout
    captured = capsys.readouterr()
    xmlOut = captured.out
    # Parse XSD schema
    xmlschema_doc = etree.parse(xsdFile)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    # Parse XML
    xml_doc = etree.fromstring(xmlOut.encode())
    assert xmlschema.validate(xml_doc)

def test_xml_is_valid_jhc(capsys):
    """
    Run checkfiles function on all files in test corpus and
    verify resulting XML output validates against XSD schema
    """
    config.VALIDATION_FORMAT = "jhc"
    config.MIX_FLAG = 0
    checkFiles(config.INPUT_RECURSIVE_FLAG, testFiles)

    # Capture output from stdout
    captured = capsys.readouterr()
    xmlOut = captured.out
    # Parse XSD schema
    xmlschema_doc = etree.parse(xsdFile)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    # Parse XML
    xml_doc = etree.fromstring(xmlOut.encode())
    assert xmlschema.validate(xml_doc)