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
from . import etpatch as ET
from . import shared
from . import validatorshared as vs
from .boxvalidator import BoxValidator
from ._boxesmarkers import boxTypeMap

class JP2Validator:
    """JP2 validator class
    """

    # Reverse access of boxTypemap for quick lookup
    boxTagMap = {v: k for k, v in boxTypeMap.items()}

    def __init__(self, options, bType, boxContents,
                 startOffset=None, components=None):
        """Initialise a BoxValidator."""
        self.options = options
        self.format = self.options['validationFormat']
        self.verboseFlag = self.options['verboseFlag']
        self.nullxmlFlag = self.options['nullxmlFlag']
        self.packetmarkersFlag = self.options['packetmarkersFlag']
        self.characteristics = ET.Element("properties")
        self.tests = ET.Element("tests")
        self.warnings = ET.Element("warnings")
        self.boxType = "JP2"
        self.boxContents = boxContents
        self.startOffset = startOffset
        self.returnOffset = None
        self.isValid = None
        self.tilePartLength = None
        self.csiz = components
        self.bTypeString = bType

    def validate(self):
        """Generic validation function."""
        try:
            to_call = getattr(self, "validate_" + self.boxType)
            to_call()
        except AttributeError:
            # Don't think this should ever happen because all known boxes
            # are defined in boxTypeMap and anything not in boxTypeMap should
            # trigger "unknown" box validator function
            msg = "ignoring '" + self.boxType + \
                "' (validator function not yet implemented)"
            shared.printWarning(msg)

        return self

    def _isValid(self):
        for elt in self.tests.iter():
            if elt.text is False:
                # File didn't pass this test, so not valid
                return False
        return True

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

    def validate_JP2(self):
        """Top-level function for JP2 (and JPH) validation.

        1. Parses all top-level boxes in JP2 byte object, and calls separate validator
           function for each of these
        2. Checks for presence of all required top-level boxes
        3. Checks if JP2 header properties are consistent with corresponding properties
           in codestream header
        """
        # Marker tags/codes that identify all top level boxes as hexadecimal strings
        # (Correspond to "Box Type" values, see ISO/IEC 15444-1 Section I.4)
        tagSignatureBox = b'\x6a\x50\x20\x20'
        tagFileTypeBox = b'\x66\x74\x79\x70'
        tagJP2HeaderBox = b'\x6a\x70\x32\x68'
        tagIntellectualPropertyBox = b'\x6a\x70\x32\x69'
        tagContiguousCodestreamBox = b'\x6a\x70\x32\x63'

        # List for storing box type identifiers
        boxTypes = []

        noBytes = len(self.boxContents)
        byteStart = 0

        # Dummy value
        boxLengthValue = 10

        while byteStart < noBytes and boxLengthValue not in [0, -9999]:

            boxLengthValue, boxType, byteEnd, boxContents = vs.getBox(self,
                byteStart, noBytes)

            # Validate current top level box
            resultsBox = BoxValidator(
                self.options,
                boxType,
                boxContents).validate()
            testsBox = resultsBox.tests
            characteristicsBox = resultsBox.characteristics
            warningsBox = resultsBox.warnings

            byteStart = byteEnd

            # Add to list of box types
            boxTypes.append(boxType)

            # Add test results, characteristics and warnings
            # to their respective trees
            self.tests.appendIfNotEmpty(testsBox)
            self.characteristics.append(characteristicsBox)
            self.warnings.appendIfNotEmpty(warningsBox)

        # Do all required top level boxes exist (ISO/IEC 15444-1 Section I.4)?
        containsSignatureBox = tagSignatureBox in boxTypes
        containsFileTypeBox = tagFileTypeBox in boxTypes
        containsJP2HeaderBox = tagJP2HeaderBox in boxTypes
        containsContiguousCodestreamBox = tagContiguousCodestreamBox in boxTypes

        self.testFor("containsSignatureBox", containsSignatureBox)
        self.testFor("containsFileTypeBox", containsFileTypeBox)
        self.testFor("containsJP2HeaderBox", containsJP2HeaderBox)
        self.testFor(
            "containsContiguousCodestreamBox", containsContiguousCodestreamBox)

        # If iPR field in image header box equals 1, intellectual property box
        # must exist as well
        iPR = self.characteristics.findElementText(
            'jp2HeaderBox/imageHeaderBox/iPR')

        if iPR == 1:
            containsIntellectualPropertyBox = tagIntellectualPropertyBox in boxTypes
            self.testFor(
                "containsIntellectualPropertyBox",
                containsIntellectualPropertyBox)

        # Is the first box a Signature Box (ISO/IEC 15444-1 Section I.5.1)?
        try:
            firstBoxIsSignatureBox = boxTypes[0] == tagSignatureBox
        except Exception:
            firstBoxIsSignatureBox = False

        # Is the second box a File Type Box (ISO/IEC 15444-1 Section I.5.2)?
        try:
            secondBoxIsFileTypeBox = boxTypes[1] == tagFileTypeBox
        except Exception:
            secondBoxIsFileTypeBox = False

        # JP2 Header Box: after File Type box, before (first) contiguous codestream box
        # (ISO/IEC 15444-1 Section I.5.3)?
        try:
            positionJP2HeaderBox = boxTypes.index(tagJP2HeaderBox)
            positionFirstContiguousCodestreamBox = boxTypes.index(
                tagContiguousCodestreamBox)

            locationJP2HeaderBoxIsValid = bool(positionFirstContiguousCodestreamBox > positionJP2HeaderBox > 1)

        except Exception:
            locationJP2HeaderBoxIsValid = False

        self.testFor("firstBoxIsSignatureBox", firstBoxIsSignatureBox)
        self.testFor("secondBoxIsFileTypeBox", secondBoxIsFileTypeBox)
        self.testFor(
            "locationJP2HeaderBoxIsValid", locationJP2HeaderBoxIsValid)

        # Some boxes can have multiple instances, whereas for others only one
        # is allowed
        # --> Note: multiple Contiguous Codestream boxes are allowed, although conforming
        # readers only read first one. So maybe include a warning in case of multiple
        # codestreams?
        noMoreThanOneSignatureBox = boxTypes.count(tagSignatureBox) <= 1
        noMoreThanOneFileTypeBox = boxTypes.count(tagFileTypeBox) <= 1
        noMoreThanOneJP2HeaderBox = boxTypes.count(tagJP2HeaderBox) <= 1

        self.testFor("noMoreThanOneSignatureBox", noMoreThanOneSignatureBox)
        self.testFor("noMoreThanOneFileTypeBox", noMoreThanOneFileTypeBox)
        self.testFor("noMoreThanOneJP2HeaderBox", noMoreThanOneJP2HeaderBox)

        # Check if general image properties in Image Header Box are consistent with
        # corresponding values in codestream header.

        # JP2 image header and codestream SIZ header as element objects
        jp2ImageHeader = self.characteristics.find(
            'jp2HeaderBox/imageHeaderBox')
        sizHeader = self.characteristics.find('contiguousCodestreamBox/siz')

        # Only proceed with tests if the above really exist (if this is not the case
        # the preceding tests will have already identified this file as not
        # valid)

        # Note: do *NOT* use 'findtext' function to get values: if value equals 0
        # this returns an empty string, even though 'text' field really contains an
        # integer. Probably a bug in ET. Using 'find' + text property does work
        # as expected

        if jp2ImageHeader is not None and sizHeader is not None:

            # Height must be equal to ysiz -yOsiz

            height = jp2ImageHeader.findElementText('height')
            ysiz = sizHeader.findElementText('ysiz')
            yOsiz = sizHeader.findElementText('yOsiz')

            heightConsistentWithSIZ = height == (ysiz - yOsiz)
            self.testFor("heightConsistentWithSIZ", heightConsistentWithSIZ)

            # Width must be equal to xsiz - xOsiz
            width = jp2ImageHeader.findElementText('width')
            xsiz = sizHeader.findElementText('xsiz')
            xOsiz = sizHeader.findElementText('xOsiz')

            widthConsistentWithSIZ = width == (xsiz - xOsiz)
            self.testFor("widthConsistentWithSIZ", widthConsistentWithSIZ)

            # nC must be equal to csiz
            nC = jp2ImageHeader.findElementText('nC')
            csiz = sizHeader.findElementText('csiz')

            nCConsistentWithSIZ = nC == csiz
            self.testFor("nCConsistentWithSIZ", nCConsistentWithSIZ)

            # Bits per component: bPCSign must be equal to ssizSign,
            # and bPCDepth to ssizDepth
            #
            # There can be 2 situations here:
            #
            # 1. bPCSign and bPCDepth same for all components --> use values from image header
            # 2. bPCSign and bPCDepth vary across components --> use values from Bits Per
            # -- Components box
            #
            # Situation 1 is the most common one. Situation 2 can be identified by a value
            # of 255 of bPC in the image header, which corresponds to  bPCSign = 1
            # and bPCDepth = 128 (these are both derived from bPC, which is not included
            # as a reportable here!)
            #
            # TO DO: test situation 2 using images with BPC box (cannot find
            # any right now)

            bPCSign = jp2ImageHeader.findElementText('bPCSign')
            bPCDepth = jp2ImageHeader.findElementText('bPCDepth')

            if bPCSign == 1 and bPCDepth == 128:
                # Actual bPCSign / bPCDepth in Bits Per Components box
                # (situation 2 above)

                bpcBox = self.characteristics.find(
                    'jp2HeaderBox/bitsPerComponentBox')

                # All occurrences of bPCSign box to list. If bpcBox is 'noneType'
                # (e.g. due to some weird corruption of the file) this will result in
                # an empty list, so nothing really bad will happen ..
                try:
                    bPCSignValues = bpcBox.findAllText('bPCSign')
                except AttributeError:
                    bPCSignValues = []

                # All occurrences of bPCDepth to list
                try:
                    bPCDepthValues = bpcBox.findAllText('bPCDepth')
                except AttributeError:
                    bPCDepthValues = []

            else:
                # These are the actual values (situation 1 above)

                # Create list of bPCSign values (i.e. duplicate fixed
                # value for each component)
                bPCSignValues = []

                for _ in range(nC):
                    bPCSignValues.append(bPCSign)

                # Create list of bPCDepth values(i.e. duplicate fixed
                # value for each component)
                bPCDepthValues = []

                for _ in range(nC):
                    bPCDepthValues.append(bPCDepth)

            # All occurrences of ssizSign to list
            try:
                ssizSignValues = sizHeader.findAllText('ssizSign')
            except AttributeError:
                ssizSignValues = []

            # All occurrences of ssizDepth to list
            try:
                ssizDepthValues = sizHeader.findAllText('ssizDepth')
            except AttributeError:
                ssizDepthValues = []

            # bPCSignValues must be equal to ssizSignValues
            bPCSignConsistentWithSIZ = bPCSignValues == ssizSignValues
            self.testFor("bPCSignConsistentWithSIZ", bPCSignConsistentWithSIZ)

            # bPCDepthValues must be equal to ssizDepthValues
            bPCDepthConsistentWithSIZ = bPCDepthValues == ssizDepthValues
            self.testFor(
                "bPCDepthConsistentWithSIZ", bPCDepthConsistentWithSIZ)

            # Calculate compression ratio
            if self.format in ['jp2', 'jph']:
                compressionRatio = vs.calculateCompressionRatio(
                    noBytes, bPCDepthValues, height, width)
                compressionRatio = round(compressionRatio, 2)
                self.addCharacteristic("compressionRatio", compressionRatio)

        # Valid JP2 only if all tests returned True
        self.isValid = self._isValid()
