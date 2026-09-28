#! /usr/bin/env python3
"""
Validation of one tile part of a JPEG 2000 codestream
"""

from __future__ import division
from . import etpatch as ET
from .validator import Validator
from .csmarkers import CSMarkerValidator


class TilePartValidator(Validator):
    """Validator class for JPEG 2000 tile part
    Note that the 'boxType' variable actually represents
    marker types in the context of this class
    """

    def __init__(self, options, bType, boxContents,
                 startOffset=None, components=None):
        """Initialise a CSMarkerValidator."""
        Validator.__init__(self, options, bType, boxContents,
                           startOffset=None, components=None)
        self.options = options
        self.format = self.options['validationFormat']
        self.verboseFlag = self.options['verboseFlag']
        self.nullxmlFlag = self.options['nullxmlFlag']
        self.packetmarkersFlag = self.options['packetmarkersFlag']
        self.boxType = "tilePart"

        self.characteristics = ET.Element(self.boxType)
        self.tests = ET.Element(self.boxType)
        self.warnings = ET.Element(self.boxType)
        self.boxContents = boxContents
        self.startOffset = startOffset
        self.returnOffset = None
        self.isValid = None
        self.tilePartLength = None
        self.csiz = components
        self.bTypeString = bType

    # Validator function for tile-part

    def validate_tilePart(self):
        """Analyse tile part that starts at offsetStart and perform cursory validation.

        Precondition: offsetStart points to SOT marker
        """
        offset = self.startOffset

        # Number of PLT and PPT markers
        pltCount = 0
        pptCount = 0

        # Read first marker segment, which is a  start of tile (SOT) marker
        # segment
        marker, _, segContents, offsetNext = self._getMarkerSegment(offset)

        # Validate start of tile (SOT) marker segment
        # tilePartLength is value of psot, which is the total length of this tile
        # including the SOT marker. Note that psot may be 0 for last tile!
        resultsSOT = CSMarkerValidator(
            self.options,
            'startOfTile',
            segContents).validate()
        testsSOT = resultsSOT.tests
        characteristicsSOT = resultsSOT.characteristics
        warningsSOT = resultsSOT.warnings
        tilePartLength = resultsSOT.tilePartLength

        self.tests.appendIfNotEmpty(testsSOT)
        self.characteristics.append(characteristicsSOT)
        self.warnings.appendIfNotEmpty(warningsSOT)

        offset = offsetNext

        # Loop through remaining tile part marker segments; extract properties of
        # and validate COD, QCD and COM marker segments. Also test for presence of
        # SOD marker
        # NOTE 1: limited testing so far because of unavailability of test images with these
        # markers at tile-part level!!
        # NOTE 2: check for offsetNext !=-9999 was included after encountering image with
        # corruption that resulted in nonsensical lsot values, ultimatelty leading to an infinite
        # loop. Shouldn't happen anymore (although this may not be the most elegant way of handling
        # this)

        while marker != b'\xff\x93' and offsetNext != -9999:
            marker, _, segContents, offsetNext = self._getMarkerSegment(offset)

            if marker == b'\xff\x52':
                # COD (coding style default) marker segment
                # Validate COD segment
                resultsCOD = CSMarkerValidator(
                    self.options,
                    marker,
                    segContents).validate()
                testsCOD = resultsCOD.tests
                characteristicsCOD = resultsCOD.characteristics
                warningsCOD = resultsCOD.warnings
                self.tests.appendIfNotEmpty(testsCOD)
                self.characteristics.append(characteristicsCOD)
                self.warnings.appendIfNotEmpty(warningsCOD)
                offset = offsetNext

            elif marker == b'\xff\x53':
                # COC (coding style component) marker segment
                # COC is optional
                # Validate COC segment
                resultsCOC = CSMarkerValidator(
                    self.options,
                    marker,
                    segContents,
                    components=self.csiz).validate()
                testsCOC = resultsCOC.tests
                characteristicsCOC = resultsCOC.characteristics
                warningsCOC = resultsCOC.warnings
                self.tests.appendIfNotEmpty(testsCOC)
                self.characteristics.append(characteristicsCOC)
                self.warnings.appendIfNotEmpty(warningsCOC)
                offset = offsetNext

            elif marker == b'\xff\x5c':
                # QCD (quantization default) marker segment
                # Validate QCD segment
                resultsQCD = CSMarkerValidator(
                    self.options,
                    marker,
                    segContents).validate()
                testsQCD = resultsQCD.tests
                characteristicsQCD = resultsQCD.characteristics
                warningsQCD = resultsQCD.warnings
                self.tests.appendIfNotEmpty(testsQCD)
                self.characteristics.append(characteristicsQCD)
                self.warnings.appendIfNotEmpty(warningsQCD)
                offset = offsetNext

            elif marker == b'\xff\x5d':
                # QCC (quantization component) marker segment
                # QCC is optional
                # Validate QCC segment
                resultsQCC = CSMarkerValidator(
                    self.options,
                    marker,
                    segContents,
                    components=self.csiz).validate()
                testsQCC = resultsQCC.tests
                characteristicsQCC = resultsQCC.characteristics
                warningsQCC = resultsQCC.warnings
                self.tests.appendIfNotEmpty(testsQCC)
                self.characteristics.append(characteristicsQCC)
                self.warnings.appendIfNotEmpty(warningsQCC)
                offset = offsetNext

            elif marker == b'\xff\x5e':
                # RGN (region of interest) marker segment
                # RGN is optional
                # Validate RGN segment
                resultsRGN = CSMarkerValidator(
                    self.options,
                    marker,
                    segContents,
                    components=self.csiz).validate()
                testsRGN = resultsRGN.tests
                characteristicsRGN = resultsRGN.characteristics
                warningsRGN = resultsRGN.warnings
                self.tests.appendIfNotEmpty(testsRGN)
                self.characteristics.append(characteristicsRGN)
                self.warnings.appendIfNotEmpty(warningsRGN)
                offset = offsetNext

            elif marker == b'\xff\x5f':
                # POC (progression order change) marker segment
                # POC is optional
                # Validate QCC segment
                resultsPOC = CSMarkerValidator(
                    self.options,
                    marker,
                    segContents,
                    components=self.csiz).validate()
                testsPOC = resultsPOC.tests
                characteristicsPOC = resultsPOC.characteristics
                warningsPOC = resultsPOC.warnings
                self.tests.appendIfNotEmpty(testsPOC)
                self.characteristics.append(characteristicsPOC)
                self.warnings.appendIfNotEmpty(warningsPOC)
                offset = offsetNext

            elif marker == b'\xff\x64':
                # COM (codestream comment) marker segment
                # Validate COM segment
                resultsCOM = CSMarkerValidator(
                    self.options,
                    marker,
                    segContents).validate()
                testsCOM = resultsCOM.tests
                characteristicsCOM = resultsCOM.characteristics
                warningsCOM = resultsCOM.warnings
                self.tests.appendIfNotEmpty(testsCOM)
                self.characteristics.append(characteristicsCOM)
                self.warnings.appendIfNotEmpty(warningsCOM)
                offset = offsetNext

            elif marker == b'\xff\x58':
                # PLT marker
                pltCount += 1
                resultsPLT = CSMarkerValidator(
                    self.options,
                    marker,
                    segContents).validate()
                testsPLT = resultsPLT.tests
                characteristicsPLT = resultsPLT.characteristics
                warningsPLT = resultsPLT.warnings
                self.tests.appendIfNotEmpty(testsPLT)
                if self.packetmarkersFlag:
                    self.characteristics.append(characteristicsPLT)
                self.warnings.appendIfNotEmpty(warningsPLT)
                offset = offsetNext

            elif marker == b'\xff\x61':
                # PPT marker
                pptCount += 1
                resultsPPT = CSMarkerValidator(
                    self.options,
                    marker,
                    segContents).validate()
                testsPPT = resultsPPT.tests
                characteristicsPPT = resultsPPT.characteristics
                warningsPPT = resultsPPT.warnings
                self.tests.appendIfNotEmpty(testsPPT)
                if self.packetmarkersFlag:
                    self.characteristics.append(characteristicsPPT)
                self.warnings.appendIfNotEmpty(warningsPPT)
                offset = offsetNext

            else:
                # Unknown marker segment: ignore and move on to next one
                # NOTE: validation should also be a test for specific marker segments that are
                # not allowed here!!
                offset = offsetNext

        # Last marker segment must be start-of-data (SOD) marker
        self.testFor("foundSODMarker", marker == b'\xff\x93')

        # Add pltCount and ppptCount value to characteristics
        self.addCharacteristic("pltCount", pltCount)
        self.addCharacteristic("pptCount", pptCount)

        # COD, COC, QCD, QCC and RGN markers are only allowed in the
        # first tile-part of any tile (TPsot = 0)
        tpsot = self.characteristics.findElementText('sot/tpsot')
        if self.characteristics.findall('cod'):
            self.testFor("CODAllowed", tpsot == 0)
        if self.characteristics.findall('coc'):
            self.testFor("COCAllowed", tpsot == 0)
        if self.characteristics.findall('qcd'):
            self.testFor("QCDAllowed", tpsot == 0)
        if self.characteristics.findall('qcc'):
            self.testFor("QCCAllowed", tpsot == 0)
        if self.characteristics.findall('rgn'):
            self.testFor("RGNAllowed", tpsot == 0)

        # Test if all ccoc values (if present) within this tile part are unique
        # (A.6.2 - no more than one COC per any given component)
        ccocElementsTP = self.characteristics.findall('coc/ccoc')
        # List with all ccoc values
        ccocValuesTP = []
        for elt in ccocElementsTP:
            ccocValuesTP.append(elt.text)

        if ccocValuesTP:
            self.testFor(
                "maxOneCcocPerComponentTP", len(
                    set(ccocValuesTP)) == len(ccocValuesTP))

        # Test if all cqcc values (if present) within this tile part are unique
        # (A.6.5 - no more than one QCC per any given component)
        cqccElementsTP = self.characteristics.findall('qcc/cqcc')
        # List with all cqcc values
        cqccValuesTP = []
        for elt in cqccElementsTP:
            cqccValuesTP.append(elt.text)
        if cqccValuesTP:
            self.testFor(
                "maxOneCqccPerComponentTP", len(
                    set(cqccValuesTP)) == len(cqccValuesTP))

        # Test if ccoc and cqcc values are consecutive numbers
        self.testFor("ccocValuesConsecutive", self._consecutive(ccocValuesTP))
        self.testFor("cqccValuesConsecutive", self._consecutive(cqccValuesTP))

        # Position of first byte in next tile
        offsetNextTilePart = self.startOffset + tilePartLength

        # Check if offsetNextTile really points to start of new tile or otherwise
        # EOC (useful for detecting within-codestream byte corruption)
        if tilePartLength != 0:
            # This will skip this test if tilePartLength equals 0, but that doesn't
            # matter since check for EOC is included elsewhere
            markerNextTilePart = self.boxContents[
                offsetNextTilePart:offsetNextTilePart + 2]
            foundNextTilePartOrEOC = markerNextTilePart in [
                b'\xff\x90', b'\xff\xd9']
            self.testFor("foundNextTilePartOrEOC", foundNextTilePartOrEOC)

        self.returnOffset = offsetNextTilePart
