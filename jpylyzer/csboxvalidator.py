"""Validator class for all boxes in JP2 and JPH"""
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import division
import uuid
import math
from . import etpatch as ET
from . import byteconv as bc
from . import shared
from .codestreamvalidator import CSValidator

class CSBoxValidator:
    """Marker tags/codes that identify all boxes and sub-boxes as hexadecimal strings.
    These correspond to values in  Table I.4 (Defined boxes) of ISO/IEC 15444-1
    """

    def __init__(self, options, bType, boxContents,
                 startOffset=None, components=None):
        """Initialise a CSBoxValidator."""
        self.options = options
        self.format = self.options['validationFormat']
        self.verboseFlag = self.options['verboseFlag']
        self.nullxmlFlag = self.options['nullxmlFlag']
        self.packetmarkersFlag = self.options['packetmarkersFlag']
        self.characteristics = ET.Element("properties")
        self.tests = ET.Element("tests")
        self.warnings = ET.Element("warnings")
        self.boxType = 'contiguousCodestreamBox'

        self.boxContents = boxContents
        self.startOffset = startOffset
        self.returnOffset = None
        self.isValid = None
        self.tilePartLength = None
        self.csiz = components
        self.bTypeString = bType

    def validate(self):
        """Generic box validation function."""
        try:
            to_call = getattr(self, "validate_" + self.boxType)
        except AttributeError:
            # Don't think this should ever happen because all known boxes
            # are defined in typeMap and anything not in typeMap should
            # trigger "unknown" box validator function
            msg = "ignoring '" + self.boxType + \
                "' (validator function not yet implemented)"
            shared.printWarning(msg)
        else:
            to_call()

        return self

    def _isValid(self):
        for elt in self.tests.iter():
            if elt.text is False:
                # File didn't pass this test, so not valid
                return False
        return True

    def _getMarkerSegment(self, offset):
        """Read marker segment that starts at offset.

        Return marker, size, contents and start offset of next marker.
        """
        # First 2 bytes: 16 bit marker
        marker = self.boxContents[offset:offset + 2]

        # Check if this is a delimiting marker segment
        if marker in [b'\xff\x4f', b'\xff\x93', b'\xff\xd9', b'\xff\x92']:
            # Zero-length markers: SOC, SOD, EOC, EPH
            length = 0
        else:
            # Not a delimiting marker, so remainder contains some data
            length = bc.bytesToUShortInt(
                self.boxContents[offset + 2:offset + 4])

        # Contents of marker segment (excluding marker) to binary string
        contents = self.boxContents[offset + 2:offset + 2 + length]

        if length == -9999:
            # If length couldn't be determined because of decode error,
            # return bogus value for offsetNext (calling function should
            # handle this further!)
            offsetNext = -9999

        else:
            # Offset value start of next marker segment
            offsetNext = offset + length + 2

        return (marker, length, contents, offsetNext)

    def _getBox(self, byteStart, noBytes):
        """Parse JP2 box and return information on its size, type and contents."""
        # Box length (4 byte unsigned integer)
        boxLengthValue = bc.bytesToUInt(
            self.boxContents[byteStart:byteStart + 4])

        # Box type
        boxType = self.boxContents[byteStart + 4:byteStart + 8]

        # Start byte of box contents
        contentsStartOffset = 8

        # Read extended box length if box length value equals 1
        # In that case contentsStartOffset must also be 16 (not 8!)
        # (See ISO/IEC 15444-1 Section I.4)
        if boxLengthValue == 1:
            boxLengthValue = bc.bytesToULongLong(
                self.boxContents[byteStart + 8:byteStart + 16])
            contentsStartOffset = 16

        # For the very last box in a file boxLengthValue may equal 0, so we need
        # to calculate actual value
        if boxLengthValue == 0:
            boxLengthValue = noBytes - byteStart

        # End byte for current box
        byteEnd = byteStart + boxLengthValue

        # Contents of this box as a byte object (i.e. 'DBox' in ISO/IEC 15444-1
        # Section I.4)
        boxContents = self.boxContents[byteStart + contentsStartOffset:byteEnd]

        return (boxLengthValue, boxType, byteEnd, boxContents)

    def testFor(self, testType, testResult):
        """Add testResult node to tests element tree."""
        if not self.verboseFlag:
            # Non-verbose output: only add results of tests that failed
            if testResult is False:
                self.tests.appendChildTagWithText(testType, testResult)

        else:
            # Verbose output, add results of all tests
            self.tests.appendChildTagWithText(testType, testResult)

    def addCharacteristic(self, characteristic, charValue):
        """Add characteristic node to characteristics element tree."""
        self.characteristics.appendChildTagWithText(characteristic, charValue)

    def addWarning(self, msg):
        """Add warning node to warnings element tree."""
        self.warnings.appendChildTagWithText("warning", msg)


    def _calculateCompressionRatio(
            self, noBytes, bPCDepthValues, height, width):
        """Compute compression ratio.

        - noBytes: size of compressed image in bytes
        - bPCDepthValues: list with bits per component for each component
        - height, width: image height, width
        """
        # Total bits per pixel
        bitsPerPixel = 0

        for i in range(len(bPCDepthValues)):
            bitsPerPixel += bPCDepthValues[i]

        # Convert to bytes per pixel
        bytesPerPixel = bitsPerPixel / 8

        # Uncompressed image size
        sizeUncompressed = bytesPerPixel * height * width

        # Compression ratio
        if noBytes != 0:
            compressionRatio = sizeUncompressed / noBytes
        else:
            # Obviously something going wrong here ...
            compressionRatio = -9999

        return compressionRatio

    def validate_contiguousCodestreamBox(self):
        """Validate Contiguous codestream box (ISO/IEC 15444-1 Section I.5.4)."""
        # Codestream length
        length = len(self.boxContents)

        # Keep track of byte offsets
        offset = 0

        # Number of PLM and PPM markers
        plmCount = 0
        ppmCount = 0

        # Read first marker segment. This must be the start-of-codestream
        # marker
        marker, _, segContents, offsetNext = self._getMarkerSegment(
            offset)

        # Marker must be start-of-codestream marker
        self.testFor("codestreamStartsWithSOCMarker", marker == b'\xff\x4f')
        offset = offsetNext

        # Read next marker segment. This must be the SIZ (image and tile
        # size) marker
        marker, _, segContents, offsetNext = self._getMarkerSegment(
            offset)
        foundSIZMarker = (marker == b'\xff\x51')
        self.testFor("foundSIZMarker", foundSIZMarker)

        if foundSIZMarker:
            # Validate SIZ segment
            resultsSIZ = CSValidator(
                self.options,
                marker,
                segContents).validate()
            testsSIZ = resultsSIZ.tests
            characteristicsSIZ = resultsSIZ.characteristics
            warningsSIZ = resultsSIZ.warnings

            self.tests.appendIfNotEmpty(testsSIZ)
            self.characteristics.append(characteristicsSIZ)
            self.warnings.appendIfNotEmpty(warningsSIZ)
            # Get csiz value, which is needed later on by the COC validation
            # function
            csiz = characteristicsSIZ.findElementText('csiz')

            offset = offsetNext

            # Loop through remaining marker segments in main header; first SOT (start of
            # tile-part marker) indicates end of main header.

            # Initial values for marker found flags
            foundPRFMarker = False
            foundCPFMarker = False
            foundCAPMarker = False
            foundCODMarker = False
            foundQCDMarker = False

            while marker != b'\xff\x90' and offsetNext != -9999:
                marker, _, segContents, offsetNext = self._getMarkerSegment(
                    offset)

                if marker == b'\xff\x52':
                    # COD (coding style default) marker segment
                    # COD is required
                    foundCODMarker = True
                    # Validate COD segment
                    resultsCOD = CSValidator(
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
                    resultsCOC = CSValidator(
                        self.options,
                        marker,
                        segContents,
                        components=csiz).validate()
                    testsCOC = resultsCOC.tests
                    characteristicsCOC = resultsCOC.characteristics
                    warningsCOC = resultsCOC.warnings
                    self.tests.appendIfNotEmpty(testsCOC)
                    self.characteristics.append(characteristicsCOC)
                    self.warnings.appendIfNotEmpty(warningsCOC)
                    offset = offsetNext

                elif marker == b'\xff\x5c':
                    # QCD (quantization default) marker segment
                    # QCD is required
                    foundQCDMarker = True
                    # Validate QCD segment
                    resultsQCD = CSValidator(
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
                    resultsQCC = CSValidator(
                        self.options,
                        marker,
                        segContents,
                        components=csiz).validate()
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
                    resultsRGN = CSValidator(
                        self.options,
                        marker,
                        segContents,
                        components=csiz).validate()
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
                    resultsPOC = CSValidator(
                        self.options,
                        marker,
                        segContents,
                        components=csiz).validate()
                    testsPOC = resultsPOC.tests
                    characteristicsPOC = resultsPOC.characteristics
                    warningsPOC = resultsPOC.warnings
                    self.tests.appendIfNotEmpty(testsPOC)
                    self.characteristics.append(characteristicsPOC)
                    self.warnings.appendIfNotEmpty(warningsPOC)
                    offset = offsetNext

                elif marker == b'\xff\x63':
                    # CRG (component registration) marker segment
                    # Validate CRG segment
                    resultsCRG = CSValidator(
                        self.options,
                        marker,
                        segContents,
                        components=csiz).validate()
                    testsCRG = resultsCRG.tests
                    characteristicsCRG = resultsCRG.characteristics
                    warningsCRG = resultsCRG.warnings
                    self.tests.appendIfNotEmpty(testsCRG)
                    self.characteristics.append(characteristicsCRG)
                    self.warnings.appendIfNotEmpty(warningsCRG)
                    offset = offsetNext

                elif marker == b'\xff\x64':
                    # COM (codestream comment) marker segment
                    # Validate COM segment
                    resultsCOM = CSValidator(
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

                elif marker == b'\xff\x50':
                    # CAP marker
                    foundCAPMarker = True
                    resultsCAP = CSValidator(
                        self.options,
                        marker,
                        segContents).validate()
                    testsCAP = resultsCAP.tests
                    characteristicsCAP = resultsCAP.characteristics
                    warningsCAP = resultsCAP.warnings
                    self.tests.appendIfNotEmpty(testsCAP)
                    self.characteristics.append(characteristicsCAP)
                    self.warnings.appendIfNotEmpty(warningsCAP)
                    offset = offsetNext

                elif marker == b'\xff\x56':
                    # PRF marker
                    foundPRFMarker = True
                    resultsPRF = CSValidator(
                        self.options,
                        marker,
                        segContents).validate()
                    testsPRF = resultsPRF.tests
                    characteristicsPRF = resultsPRF.characteristics
                    warningsPRF = resultsPRF.warnings
                    self.tests.appendIfNotEmpty(testsPRF)
                    self.characteristics.append(characteristicsPRF)
                    self.warnings.appendIfNotEmpty(warningsPRF)
                    offset = offsetNext

                elif marker == b'\xff\x59':
                    # CPF marker
                    foundCPFMarker = True
                    resultsCPF = CSValidator(
                        self.options,
                        marker,
                        segContents).validate()
                    testsCPF = resultsCPF.tests
                    characteristicsCPF = resultsCPF.characteristics
                    warningsCPF = resultsCPF.warnings
                    self.tests.appendIfNotEmpty(testsCPF)
                    self.characteristics.append(characteristicsCPF)
                    self.warnings.appendIfNotEmpty(warningsCPF)
                    offset = offsetNext

                elif marker == b'\xff\x90':
                    # Start of tile (SOT) marker segment; don't update offset as this
                    # will get us of out of this loop (for functional
                    # readability):
                    pass

                elif marker == b'\xff\x55':
                    # TLM marker
                    resultsTLM = CSValidator(
                        self.options,
                        marker,
                        segContents).validate()
                    testsTLM = resultsTLM.tests
                    characteristicsTLM = resultsTLM.characteristics
                    warningsTLM = resultsTLM.warnings
                    self.tests.appendIfNotEmpty(testsTLM)
                    self.characteristics.append(characteristicsTLM)
                    self.warnings.appendIfNotEmpty(warningsTLM)
                    offset = offsetNext

                elif marker == b'\xff\x57':
                    # PLM marker
                    plmCount += 1
                    resultsPLM = CSValidator(
                        self.options,
                        marker,
                        segContents).validate()
                    testsPLM = resultsPLM.tests
                    characteristicsPLM = resultsPLM.characteristics
                    warningsPLM = resultsPLM.warnings
                    self.tests.appendIfNotEmpty(testsPLM)
                    if self.packetmarkersFlag:
                        self.characteristics.append(characteristicsPLM)
                    self.warnings.appendIfNotEmpty(warningsPLM)
                    offset = offsetNext

                elif marker == b'\xff\x60':
                    # PPM marker
                    ppmCount += 1
                    resultsPPM = CSValidator(
                        self.options,
                        marker,
                        segContents).validate()
                    testsPPM = resultsPPM.tests
                    characteristicsPPM = resultsPPM.characteristics
                    warningsPPM = resultsPPM.warnings
                    self.tests.appendIfNotEmpty(testsPPM)
                    if self.packetmarkersFlag:
                        self.characteristics.append(characteristicsPPM)
                    self.warnings.appendIfNotEmpty(warningsPPM)
                    offset = offsetNext

                else:
                    # Any other marker segment: ignore and move on to next one
                    # Note that this should result in validation error as all
                    # marker segments are covered above!!
                    offset = offsetNext

            # Add ppmCount and plmCount value to characteristics
            self.addCharacteristic("ppmCount", ppmCount)
            self.addCharacteristic("plmCount", plmCount)

            # Add foundCODMarker / foundQCDMarker outcome to tests
            self.testFor("foundCODMarker", foundCODMarker)
            self.testFor("foundQCDMarker", foundQCDMarker)

            # Test for presence of CAP marker if rsiz indicates capabilities that
            # are defined there
            rsiz = self.characteristics.findElementText(
                'siz/rsiz')
            # Two most significant bits of rsiz indicate CAP marker use
            if (rsiz >> 14) & 15 == 1:
                self.testFor("foundCAPMarker", foundCAPMarker)

            # Remainder of codestream is a sequence of tile parts, followed by one
            # end-of-codestream marker

            # Expected number of tiles (as calculated from info in SIZ marker)
            numberOfTilesExpected = self.characteristics.findElementText(
                'siz/numberOfTiles')

            # If we did not get the number of tiles, assume it is zero
            if not numberOfTilesExpected:
                numberOfTilesExpected = 0

            # Impose upper limit on numberOfTilesExpected to avoid misbehaviour
            # in case of corrupted files. Value of 65535 equals upper value imposed by Kakadu
            # (can't find this  anywhere the standard though)
            numberOfTilesExpected = min(numberOfTilesExpected, 65535)

            # Create list with one entry for each tile
            tileIndices = []

            # Dictionary that contains expected number of tile parts for each
            # tile
            tilePartsPerTileExpected = {}

            # Dictionary that contains found number of tile parts for each tile
            tilePartsPerTileFound = {}

            # Create entry for each tile part and initialise value at 0
            for i in range(numberOfTilesExpected):
                tilePartsPerTileFound[i] = 0

            # Create sub-elements to store tile-part characteristics, tests and warnings
            tilePartCharacteristics = ET.Element('tileParts')
            tilePartTests = ET.Element('tileParts')
            tilePartWarnings = ET.Element('tileParts')

            while marker == b'\xff\x90':
                marker = self.boxContents[offset:offset + 2]

                if marker == b'\xff\x90':
                    resultsTilePart = CSValidator(
                        self.options,
                        marker,
                        self.boxContents,
                        startOffset=offset,
                        components=csiz).validate()
                    testsTilePart = resultsTilePart.tests
                    characteristicsTilePart = resultsTilePart.characteristics
                    warningsTilePart = resultsTilePart.warnings
                    offsetNext = resultsTilePart.returnOffset
                    tilePartTests.appendIfNotEmpty(testsTilePart)
                    tilePartCharacteristics.append(characteristicsTilePart)
                    tilePartWarnings.appendIfNotEmpty(warningsTilePart)
                    tileIndex = characteristicsTilePart.findElementText(
                        'sot/isot')
                    tilePartsOfTile = characteristicsTilePart.findElementText(
                        'sot/tnsot')
                    # Add tileIndex to tileIndices, if it doesn't exist already
                    if tileIndex not in tileIndices:
                        tileIndices.append(tileIndex)
                    # Expected number of tile-parts for each tile to dictionary
                    if tilePartsOfTile != 0:
                        tilePartsPerTileExpected[tileIndex] = tilePartsOfTile

                    # Increase found number of tile-parts for this tile by 1
                    try:
                        tilePartsPerTileFound[
                            tileIndex] = tilePartsPerTileFound[tileIndex] + 1
                    except KeyError:
                        # Get the f**k out of here if tileIndex is not in
                        # tilePartsPerTileFound (e.g. because the isot field is
                        # damaged)
                        break
                    if offsetNext != offset:
                        offset = offsetNext
                    else:
                        # offsetNext same as offset: this happens if image only contains
                        # one single tile-part (psot=0), in which case we break out of
                        # this loop
                        break

            # Length of tileIndices must equal numberOfTilesExpected
            self.testFor("foundExpectedNumberOfTiles", len(
                tileIndices) == numberOfTilesExpected)

            # Found numbers of tile	parts per tile must match expected
            if tilePartsPerTileExpected:
                self.testFor("foundExpectedNumberOfTileParts",
                            tilePartsPerTileExpected == tilePartsPerTileFound)

            # Add tile-part tests, characteristics and warnings to tree
            self.tests.appendIfNotEmpty(tilePartTests)
            self.characteristics.append(tilePartCharacteristics)
            self.warnings.appendIfNotEmpty(tilePartWarnings)

            # Test if all ccoc values at main header level are unique
            # (A.6.2 - no more than one COC per any given component)
            ccocElementsMain = self.characteristics.findall('coc/ccoc')
            # List with all ccoc values
            ccocValuesMain = []
            for elt in ccocElementsMain:
                ccocValuesMain.append(elt.text)

            if ccocValuesMain:
                self.testFor(
                    "maxOneCcocPerComponentMain", len(
                        set(ccocValuesMain)) == len(ccocValuesMain))

            # Test if all cqcc values at main header level are unique
            # (A.6.5 - no more than one QCC per any given component)
            cqccElementsMain = self.characteristics.findall('qcc/cqcc')
            # List with all cqcc values
            cqccValuesMain = []
            for elt in cqccElementsMain:
                cqccValuesMain.append(elt.text)
            if cqccValuesMain:
                self.testFor(
                    "maxOneCqccPerComponentMain", len(
                        set(cqccValuesMain)) == len(cqccValuesMain))

            # Test if ccoc and cqcc values are consecutive numbers
            self.testFor("ccocValuesConsecutive", all(n-i==ccocValuesMain[0] for i,n in enumerate(ccocValuesMain)))
            self.testFor("cqccValuesConsecutive", all(n-i==cqccValuesMain[0] for i,n in enumerate(cqccValuesMain)))

            # Consistency tests on TLM marker segments
            if len(self.characteristics.findall('tlm')) > 0:
                # Test if sum of tpCount values from TLM marker segments
                # corresponds to actual number of tile parts

                # Tile part count from jpylyzer parsing
                tpCount = len(self.characteristics.findall('tileParts/tilePart'))

                # Tile part count from TLM
                tpCountTlm = 0
                tpCountElements = self.characteristics.findall('tlm/tpCount')
                for i in range(len(tpCountElements)):
                    tpCountTlm += tpCountElements[i].text

                self.testFor("tilePartsTLMConsistencyCheck", tpCountTlm == tpCount)

                # Test if tile part lengths defined by ptlm values in TLM marker segments
                # correspond to psot values in SOT marker segments
                ptlmElements = self.characteristics.findall('tlm/ptlm')
                psotElements = self.characteristics.findall('tileParts/tilePart/sot/psot')

                # Lists of all ptlm and psot values
                ptlms = []
                for i in range(len(ptlmElements)):
                    ptlms.append(ptlmElements[i].text)
                psots = []
                for i in range(len(psotElements)):
                    psots.append(psotElements[i].text)

                self.testFor("tilePartLengthsConsistencyCheck", ptlms == psots)

            # Last 2 bytes must be end-of-codestream marker
            self.testFor("foundEOCMarker",
                         self.boxContents[length - 2:length] == b'\xff\xd9')

            if self.format in ['j2c', 'jhc'] and foundSIZMarker:

                # Calculate compression ratio
                ssizDepthValues = characteristicsSIZ.findAllText('ssizDepth')
                ysiz = characteristicsSIZ.findElementText('ysiz')
                yOsiz = characteristicsSIZ.findElementText('xOsiz')
                xsiz = characteristicsSIZ.findElementText('xsiz')
                xOsiz = characteristicsSIZ.findElementText('xOsiz')

                compressionRatio = self._calculateCompressionRatio(
                    length, ssizDepthValues, (ysiz - yOsiz), (xsiz - xOsiz))
                compressionRatio = round(compressionRatio, 2)
                self.addCharacteristic("compressionRatio", compressionRatio)

        # Valid codestream only if all tests returned True
        self.isValid = self._isValid()
