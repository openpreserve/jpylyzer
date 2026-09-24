#! /usr/bin/env python3

from __future__ import division
import uuid
import math
from . import etpatch as ET
from . import byteconv as bc
from . import shared
from .validator import Validator
from .codestreamvalidator import CSValidator


class BoxValidator(Validator):
    """Validator class for all boxes in JP2 and JPH
    """

    def __init__(self, options, bType, boxContents,
                 startOffset=None, components=None):
        """Initialise a BoxValidator."""
        Validator.__init__(self, options, bType, boxContents,
                           startOffset=None, components=None)
        self.options = options
        self.format = self.options['validationFormat']
        self.verboseFlag = self.options['verboseFlag']
        self.nullxmlFlag = self.options['nullxmlFlag']
        self.packetmarkersFlag = self.options['packetmarkersFlag']
        if bType in self.boxTypeMap:
            self.boxType = self.boxTypeMap[bType]
        elif bType == "contiguousCodestreamBox":
            self.characteristics = ET.Element("properties")
            self.tests = ET.Element("tests")
            self.warnings = ET.Element("warnings")
            self.boxType = 'contiguousCodestreamBox'
        else:
            self.boxType = 'unknownBox'
            self.characteristics = ET.Element("properties")
            self.warnings = ET.Element("warnings")

        if bType not in ["JP2", "contiguousCodestreamBox"]:
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

    # Validator functions for JP2 and JPH boxes

    def validate_unknownBox(self):
        """Process 'unknown'box.

        Although jpylyzer doesn't know anything about this box, we can at least
        report the 4 characters from the Box Type field (TBox) here.
        """
        boxType = self.bTypeString

        # Add boxType string to output
        self.addCharacteristic("boxType", boxType)

        # Print warning message to screen
        msg = "ignoring unknown box '" + bc.bytesToText(boxType) + "'"
        self.addWarning(msg)
        shared.printWarning(msg)

    def validate_signatureBox(self):
        """Signature box (ISO/IEC 15444-1 Section I.5.2)."""
        # Check box size, which must be 4 bytes
        self.testFor("boxLengthIsValid", len(self.boxContents) == 4)

        # Signature *not* added to characteristics output, because it contains
        # non-printable characters)
        self.testFor(
            "signatureIsValid", self.boxContents[0:4] == b'\x0d\x0a\x87\x0a')

    def validate_fileTypeBox(self):
        """File type box (ISO/IEC 15444-1 Section I.5.2;
        ISO/IEC 15444-15 Section D.3)."""
        # Determine number of compatibility fields from box length
        numberOfCompatibilityFields = (len(self.boxContents) - 8) / 4

        # This should never produce a decimal number (would indicate missing
        # data)
        self.testFor("boxLengthIsValid", numberOfCompatibilityFields == int(
            numberOfCompatibilityFields))

        # Brand value
        br = self.boxContents[0:4]
        self.addCharacteristic("br", br)

        # Is brand value valid?
        if self.format == 'jp2':
            self.testFor("brandIsValid", br == b'\x6a\x70\x32\x20')
        elif self.format == 'jph':
            self.testFor("brandIsValid", br == b'\x6a\x70\x68\x20')

        # Minor version
        minV = bc.bytesToUInt(self.boxContents[4:8])
        self.addCharacteristic("minV", minV)

        # Value must be 0
        # Note that conforming readers should continue to process the file
        # even if this field contains some other value
        self.testFor("minorVersionIsValid", minV == 0)

        # Compatibility list (one or more 4-byte fields)
        # Create list object and store all entries as separate list elements
        cLList = []
        offset = 8

        for _ in range(int(numberOfCompatibilityFields)):
            cL = self.boxContents[offset:offset + 4]
            self.addCharacteristic("cL", cL)
            cLList.append(cL)
            offset += 4

        # Compatibility list must contain at least one field with mandatory value.
        # List is considered valid if this value is found.
        if self.format == 'jp2':
            self.testFor(
                "compatibilityListIsValid",
                b'\x6a\x70\x32\x20' in cLList)
        elif self.format == 'jph':
            self.testFor(
                "compatibilityListIsValid",
                b'\x6a\x70\x68\x20' in cLList)

    def validate_jp2HeaderBox(self):
        """JP2 header box (superbox) (ISO/IEC 15444-1 Section I.5.3;
        ISO/IEC 15444-15 Section D.2)."""
        # List for storing box type identifiers
        subBoxTypes = []
        noBytes = len(self.boxContents)
        byteStart = 0

        # Dummy value
        boxLengthValue = 10

        while byteStart < noBytes and boxLengthValue not in [0, -9999]:
            boxLengthValue, boxType, byteEnd, subBoxContents = self._getBox(byteStart,
                                                                            noBytes)

            # Validate sub-boxes
            resultsBox = BoxValidator(
                self.options,
                boxType,
                subBoxContents).validate()
            testsBox = resultsBox.tests
            characteristicsBox = resultsBox.characteristics
            warningsBox = resultsBox.warnings

            byteStart = byteEnd

            # Add to list of box types
            subBoxTypes.append(boxType)

            # Add test results, characteristics and warnings to their
            # respective trees
            self.tests.appendIfNotEmpty(testsBox)
            self.characteristics.append(characteristicsBox)
            self.warnings.appendIfNotEmpty(warningsBox)

        # Do all required header boxes exist?
        self.testFor("containsImageHeaderBox",
                     self.boxTagMap['imageHeaderBox'] in subBoxTypes)

        if self.format == 'jp2':
            self.testFor("containsColourSpecificationBox", self.boxTagMap[
                'colourSpecificationBox'] in subBoxTypes)
        elif self.format == 'jph':
            # In JPH, Colour Specification Box is only mandatory if unkC is
            # zero
            unkC = self.characteristics.findElementText('imageHeaderBox/unkC')
            if unkC == 0:
                self.testFor("containsColourSpecificationBox", self.boxTagMap[
                    'colourSpecificationBox'] in subBoxTypes)

            # If JPH does not contain a Colour Specification Box, no cTyp
            # values (from Channel definition box) shall be equal to 0
            if not self.boxTagMap['colourSpecificationBox'] in subBoxTypes:
                cTypes = self.characteristics.findAllText(
                    'channelDefinitionBox/cTyp')
                self.testFor("noZeroCTypesIfNoColourBox", 0 not in cTypes)

        # If bPCSign equals 1 and bPCDepth equals 128 (equivalent to bPC field being
        # 255), this box must contain a Bits Per Components box
        sign = self.characteristics.findElementText('imageHeaderBox/bPCSign')
        depth = self.characteristics.findElementText('imageHeaderBox/bPCDepth')

        if sign == 1 and depth == 128:
            self.testFor("containsBitsPerComponentBox", self.boxTagMap[
                'bitsPerComponentBox'] in subBoxTypes)

        # Is the first box an Image Header Box?
        try:
            firstJP2HeaderBoxIsImageHeaderBox = subBoxTypes[
                0] == self.boxTagMap['imageHeaderBox']
        except Exception:
            firstJP2HeaderBoxIsImageHeaderBox = False

        self.testFor(
            "firstJP2HeaderBoxIsImageHeaderBox",
            firstJP2HeaderBoxIsImageHeaderBox)

        # Some boxes can have multiple instances, whereas for others only one
        # is allowed
        self.testFor("noMoreThanOneImageHeaderBox", subBoxTypes.count(
            self.boxTagMap['imageHeaderBox']) <= 1)
        self.testFor("noMoreThanOneBitsPerComponentBox", subBoxTypes.count(
            self.boxTagMap['bitsPerComponentBox']) <= 1)
        self.testFor("noMoreThanOnePaletteBox", subBoxTypes.count(
            self.boxTagMap['paletteBox']) <= 1)
        self.testFor("noMoreThanOneComponentMappingBox", subBoxTypes.count(
            self.boxTagMap['componentMappingBox']) <= 1)
        self.testFor("noMoreThanOneChannelDefinitionBox", subBoxTypes.count(
            self.boxTagMap['channelDefinitionBox']) <= 1)
        self.testFor("noMoreThanOneResolutionBox", subBoxTypes.count(
            self.boxTagMap['resolutionBox']) <= 1)

        # In case of multiple colour specification boxes, they must appear contiguously
        # within the header box
        colourSpecificationBoxesAreContiguous = shared.listOccurrencesAreContiguous(
            subBoxTypes, self.boxTagMap['colourSpecificationBox'])
        self.testFor("colourSpecificationBoxesAreContiguous",
                     colourSpecificationBoxesAreContiguous)

        # If JP2 Header box contains a Palette Box, it must also contain a component
        # mapping box, and vice versa
        if ((self.boxTagMap['paletteBox'] in subBoxTypes and self.boxTagMap['componentMappingBox']
             not in subBoxTypes) or (self.boxTagMap['componentMappingBox'] in subBoxTypes and
                                     self.boxTagMap['paletteBox'] not in subBoxTypes)):
            paletteAndComponentMappingBoxesOnlyTogether = False
        else:
            paletteAndComponentMappingBoxesOnlyTogether = True

        self.testFor("paletteAndComponentMappingBoxesOnlyTogether",
                     paletteAndComponentMappingBoxesOnlyTogether)

    # Validator functions for boxes in JP2 Header superbox
    def validate_imageHeaderBox(self):
        """Image header box (ISO/IEC 15444-1 Section I.5.3.1).

        This is a fixed-length box that contains generic image info.
        """
        # Check box length (14 bytes, excluding box length/type fields)
        self.testFor("boxLengthIsValid", len(self.boxContents) == 14)

        # Image height and width (both as unsigned integers)
        height = bc.bytesToUInt(self.boxContents[0:4])
        self.addCharacteristic("height", height)
        width = bc.bytesToUInt(self.boxContents[4:8])
        self.addCharacteristic("width", width)

        # Height and width must be within range 1 - (2**32)-1
        self.testFor("heightIsValid", 1 <= height <= (2 ** 32) - 1)
        self.testFor("widthIsValid", 1 <= width <= (2 ** 32) - 1)

        # Number of components (unsigned short integer)
        nC = bc.bytesToUShortInt(self.boxContents[8:10])
        self.addCharacteristic("nC", nC)

        # Number of components must be in range 1 - 16384 (including limits)
        self.testFor("nCIsValid", 1 <= nC <= 16384)

        # Bits per component (unsigned character)
        bPC = bc.bytesToUnsignedChar(self.boxContents[10:11])

        # Most significant bit indicates whether components are signed (1)
        # or unsigned (0).
        bPCSign = bc.getBitValue(bPC, 1)
        self.addCharacteristic("bPCSign", bPCSign)

        # Remaining bits indicate (bit depth - 1). Extracted by applying bit mask of
        # 01111111 (=127)
        bPCDepth = (bPC & 127) + 1
        self.addCharacteristic("bPCDepth", bPCDepth)

        # Bits per component field is valid if:
        # 1. bPCDepth in range 1-38 (including limits)
        # 2. OR bPC equal 255 (indicating that components vary in bit depth)
        bPCDepthIsWithinAllowedRange = 1 <= bPCDepth <= 38
        bitDepthIsVariable = 1 <= bPC <= 255

        bPCIsValid = bool(bPCDepthIsWithinAllowedRange or bitDepthIsVariable)

        self.testFor("bPCIsValid", bPCIsValid)

        # Compression type (unsigned character)
        c = bc.bytesToUnsignedChar(self.boxContents[11:12])
        self.addCharacteristic("c", c)

        # Value must always be 7
        self.testFor("cIsValid", c == 7)

        # Colourspace unknown field (unsigned character)
        unkC = bc.bytesToUnsignedChar(self.boxContents[12:13])
        self.addCharacteristic("unkC", unkC)

        # Value must be 0 or 1
        self.testFor("unkCIsValid", 0 <= unkC <= 1)

        # Intellectual Property field (unsigned character)
        iPR = bc.bytesToUnsignedChar(self.boxContents[13:14])
        self.addCharacteristic("iPR", iPR)

        # Value must be 0 or 1
        self.testFor("iPRIsValid", 0 <= iPR <= 1)

    def validate_bitsPerComponentBox(self):
        """Validate Bits per component box (ISO/IEC 15444-1 Section I.5.3.2).

        Optional box that specifies bit depth of each component.
        """
        # Number of bPC field (each field is 1 byte)
        numberOfBPFields = len(self.boxContents)

        # Validate all entries
        for i in range(numberOfBPFields):

            # Bits per component (unsigned character)
            bPC = bc.bytesToUnsignedChar(self.boxContents[i:i + 1])

            # Most significant bit indicates whether components are signed (1)
            # or unsigned (0). Extracted by applying bit mask of 10000000
            # (=128)
            bPCSign = bc.getBitValue(bPC, 1)
            self.addCharacteristic("bPCSign", bPCSign)

            # Remaining bits indicate (bit depth - 1). Extracted by applying bit mask of
            # 01111111 (=127)
            bPCDepth = (bPC & 127) + 1
            self.addCharacteristic("bPCDepth", bPCDepth)

            # Bits per component field is valid if bPCDepth in range 1-38
            # (including limits)
            self.testFor("bPCIsValid", 1 <= bPCDepth <= 38)

    def validate_colourSpecificationBox(self):
        """Colour specification box (ISO/IEC 15444-1 Section I.5.3.3;
        ISO/IEC 15444-15 Section D.4).

        This box defines one method for interpreting colourspace of decompressed
        image data.
        """
        # Length of this box
        length = len(self.boxContents)

        # Specification method (unsigned character)
        meth = bc.bytesToUnsignedChar(self.boxContents[0:1])
        self.addCharacteristic("meth", meth)

        if self.format == 'jp2':
            # Value must be 1 (enumerated colourspace) or 2 (restricted ICC
            # profile)
            self.testFor("methIsValid", meth in [1, 2])

        elif self.format == 'jph':
            # JPH also allows 3 (Any ICC) and 5 (parameterized colourspace)
            self.testFor("methIsValid", meth in [1, 2, 3, 5])

        # Precedence (unsigned character)
        prec = bc.bytesToUnsignedChar(self.boxContents[1:2])
        self.addCharacteristic("prec", prec)

        # Value shall be 0 (but conforming readers should ignore it)
        self.testFor("precIsValid", prec == 0)

        # Colourspace approximation (unsigned character)
        approx = bc.bytesToUnsignedChar(self.boxContents[2:3])
        self.addCharacteristic("approx", approx)

        # Value shall be 0 (but conforming readers should ignore it)
        self.testFor("approxIsValid", approx == 0)

        # Colour space info: enumerated CS or embedded ICC profile,
        # depending on value of meth
        if meth == 1:
            # Enumerated colour space field (long integer)
            enumCS = bc.bytesToUInt(self.boxContents[3:length])
            self.addCharacteristic("enumCS", enumCS)

            # (Note: this will also trap any cases where enumCS is more/less than 4
            # bytes, as bc.bytesToUInt will return bogus negative value, which in turn is
            # handled by statement below)

            # Legal values: 16,17, 18
            self.testFor("enumCSIsValid", enumCS in [16, 17, 18])

        elif meth == 2:
            # Restricted ICC profile
            profile = self.boxContents[3:length]

            # Extract ICC profile properties as element object
            iccResults = BoxValidator(
                self.options,
                'icc',
                profile).validate()
            iccCharacteristics = iccResults.characteristics
            iccWarnings = iccResults.warnings
            self.characteristics.append(iccCharacteristics)
            self.warnings.appendIfNotEmpty(iccWarnings)

            # Profile size property must equal actual profile size
            profileSize = iccCharacteristics.findElementText('profileSize')
            self.testFor("iccSizeIsValid", profileSize == len(profile))

            # Profile class must be 'input' or 'display'
            profileClass = iccCharacteristics.findElementText('profileClass')
            self.testFor(
                "iccPermittedProfileClass", profileClass in [b'scnr', b'mntr'])

            # List of tag signatures may not contain "AToB0Tag", which indicates
            # an N-component LUT based profile, which is not allowed in JP2

            # Step 1: create list of all "tag" elements
            tagSignatureElements = iccCharacteristics.findall("tag")

            # Step 2: create list of all tag signatures and fill it
            tagSignatures = []

            for i in range(len(tagSignatureElements)):
                tagSignatures.append(tagSignatureElements[i].text)

            # Step 3: verify non-existence of "AToB0Tag"
            self.testFor("iccNoLUTBasedProfile", b'A2B0' not in tagSignatures)

        elif meth == 3:
            # ICC profile embedded using "Any ICC" method. Used in JPEG 2000 Part 2
            # (JPX) and Part 15 (JPH)
            profile = self.boxContents[3:length]

            # Extract ICC profile properties as element object
            # self.getICCCharacteristics(profile)
            iccResults = BoxValidator(
                self.options,
                'icc',
                profile).validate()
            iccCharacteristics = iccResults.characteristics
            iccWarnings = iccResults.warnings
            self.characteristics.append(iccCharacteristics)
            self.warnings.appendIfNotEmpty(iccWarnings)

        elif meth == 5:
            # Parameterized colourspace. Used in JPEG 2000 Part 15 (JPH)

            # ColourPrimaries value
            colPrims = bc.bytesToUShortInt(self.boxContents[3:5])
            self.addCharacteristic("colPrims", colPrims)

            if self.format == 'jph':
                # Value must be part of enumeration defined in
                # Rec. ITU-T H.273 | ISO/IEC 23001-8 (Table 2)
                self.testFor("colPrimsIsValid", colPrims in [1, 2, 4, 5,
                                                             6, 7, 8, 9,
                                                             10, 11, 12, 22])
            # TransferCharacteristics value
            transfC = bc.bytesToUShortInt(self.boxContents[5:7])
            self.addCharacteristic("transfC", transfC)

            if self.format == 'jph':
                # Value must be part of enumeration defined in
                # Rec. ITU-T H.273 | ISO/IEC 23001-8 (Table 3)
                self.testFor("transfCIsValid", transfC in [1, 2, 4, 5,
                                                           6, 7, 8, 9,
                                                           10, 11, 12, 13,
                                                           14, 15, 16, 17,
                                                           18])
            # MatrixCoefficients value
            matCoeffs = bc.bytesToUShortInt(self.boxContents[7:9])
            self.addCharacteristic("matCoeffs", matCoeffs)

            if self.format == 'jph':
                # Value must be part of enumeration defined in
                # Rec. ITU-T H.273 | ISO/IEC 23001-8 (Table 4)
                self.testFor("matCoeffsIsValid", matCoeffs in [0, 1, 2, 4,
                                                               5, 6, 7, 8,
                                                               9, 10, 11, 12,
                                                               13, 14])

            # VideoFullRange byte (currently only 1st bit is defined, remaining 7 bits
            # are reserved for future use)
            vidFRngByte = bc.bytesToUnsignedChar(self.boxContents[9:10])

            # VideoFullRangeFlag: first bit of vidFRngByte
            vidFRng = bc.getBitValue(vidFRngByte, 1)
            self.addCharacteristic("vidFRng", vidFRng)

    def validate_icc(self):
        """Extract characteristics (property-value pairs) of ICC profile.

        Note that although values are stored in  'text' property of sub-elements,
        they may have a type other than 'text' (binary string, integers, lists)
        This means that some post-processing (conversion to text) is needed to
        write these property-value pairs to XML
        """
        # Profile header properties (note: incomplete at this stage!)

        # Size in bytes
        profileSize = bc.bytesToUInt(self.boxContents[0:4])
        self.addCharacteristic("profileSize", profileSize)

        # Preferred CMM type
        preferredCMMType = self.boxContents[4:8]
        self.addCharacteristic("preferredCMMType", preferredCMMType)

        # Profile version: major revision
        profileMajorRevision = bc.bytesToUnsignedChar(self.boxContents[8:9])

        # Profile version: minor revision
        profileMinorRevisionByte = bc.bytesToUnsignedChar(
            self.boxContents[9:10])

        # Minor revision: first 4 bits of profileMinorRevisionByte
        # (Shift bits 4 positions to right, logical shift not arithmetic shift!)
        profileMinorRevision = profileMinorRevisionByte >> 4

        # Bug fix revision: last 4 bits of profileMinorRevisionByte
        # (apply bit mask of 00001111 = 15)
        profileBugFixRevision = profileMinorRevisionByte & 15

        # Construct text string with profile version
        profileVersion = "%s.%s.%s" % (
            profileMajorRevision, profileMinorRevision, profileBugFixRevision)
        self.addCharacteristic("profileVersion", profileVersion)

        # Bytes 10 and 11 are reserved an set to zero(ignored here)

        # Profile class (or device class)
        profileClass = self.boxContents[12:16]
        self.addCharacteristic("profileClass", profileClass)

        # Colour space
        colourSpace = self.boxContents[16:20]
        self.addCharacteristic("colourSpace", colourSpace)

        # Profile connection space
        profileConnectionSpace = self.boxContents[20:24]
        self.addCharacteristic(
            "profileConnectionSpace", profileConnectionSpace)

        # Date and time fields
        year = bc.bytesToUShortInt(self.boxContents[24:26])
        month = bc.bytesToUnsignedChar(self.boxContents[27:28])
        day = bc.bytesToUnsignedChar(self.boxContents[29:30])
        hour = bc.bytesToUnsignedChar(self.boxContents[31:32])
        minute = bc.bytesToUnsignedChar(self.boxContents[33:34])
        second = bc.bytesToUnsignedChar(self.boxContents[35:36])
        dateString = "%d/%02d/%02d" % (year, month, day)
        timeString = "%02d:%02d:%02d" % (hour, minute, second)
        dateTimeString = "%s, %s" % (dateString, timeString)
        self.addCharacteristic("dateTimeString", dateTimeString)

        # Profile signature
        profileSignature = self.boxContents[36:40]
        self.addCharacteristic("profileSignature", profileSignature)

        # Primary platform
        primaryPlatform = self.boxContents[40:44]
        self.addCharacteristic("primaryPlatform", primaryPlatform)

        # Profile flags (bytes 44-47; only first byte read here as remaining bytes
        # don't contain any meaningful information)
        profileFlags = bc.bytesToUnsignedChar(self.boxContents[44:45])

        # Embedded profile (0 if not embedded, 1 if embedded in file)
        embeddedProfile = bc.getBitValue(profileFlags, 1)
        self.addCharacteristic("embeddedProfile", embeddedProfile)

        # Profile cannot be used independently from embedded colour data
        # (1 if true, 0 if false)
        profileCannotBeUsedIndependently = bc.getBitValue(profileFlags, 2)
        self.addCharacteristic(
            "profileCannotBeUsedIndependently",
            profileCannotBeUsedIndependently)

        # Device manufacturer
        deviceManufacturer = self.boxContents[48:52]
        self.addCharacteristic("deviceManufacturer", deviceManufacturer)

        # Device model
        deviceModel = self.boxContents[52:56]
        self.addCharacteristic("deviceModel", deviceModel)

        # Device attributes (bytes 56-63; only first byte read here as remaining bytes
        # don't contain any meaningful information)
        deviceAttributes = bc.bytesToUnsignedChar(self.boxContents[56:57])

        # Transparency (1 = transparent; 0 = reflective)
        transparency = bc.getBitValue(deviceAttributes, 1)
        self.addCharacteristic("transparency", transparency)

        # Glossiness (1 = matte; 0 = glossy)
        glossiness = bc.getBitValue(deviceAttributes, 2)
        self.addCharacteristic("glossiness", glossiness)

        # Media polarity (1 = negative; 0 = positive)
        polarity = bc.getBitValue(deviceAttributes, 3)
        self.addCharacteristic("polarity", polarity)

        # Media colour (1 = black & white; 0 = colour)
        colour = bc.getBitValue(deviceAttributes, 4)
        self.addCharacteristic("colour", colour)

        # Rendering intent (bytes 64-67, only least-significant 2 bytes used)
        renderingIntent = bc.bytesToUShortInt(self.boxContents[66:68])
        self.addCharacteristic("renderingIntent", renderingIntent)

        # Profile connection space illuminants (X, Y, Z)
        connectionSpaceIlluminantX = round(
            bc.bytesToUInt(self.boxContents[68:72]) / 65536, 4)
        self.addCharacteristic(
            "connectionSpaceIlluminantX", connectionSpaceIlluminantX)

        connectionSpaceIlluminantY = round(
            bc.bytesToUInt(self.boxContents[72:76]) / 65536, 4)
        self.addCharacteristic(
            "connectionSpaceIlluminantY", connectionSpaceIlluminantY)

        connectionSpaceIlluminantZ = round(
            bc.bytesToUInt(self.boxContents[76:80]) / 65536, 4)
        self.addCharacteristic(
            "connectionSpaceIlluminantZ", connectionSpaceIlluminantZ)

        # Profile creator
        profileCreator = self.boxContents[80:84]
        self.addCharacteristic("profileCreator", profileCreator)

        # Profile ID (as hexadecimal string)
        profileID = bc.bytesToHex(self.boxContents[84:100])
        self.addCharacteristic("profileID", profileID)

        # Number of tags (tag count)
        tagCount = bc.bytesToUInt(self.boxContents[128:132])

        # Impose upper value on tagCount to avoid freezes in case of byte corrupted file
        # Value of 4096 taken from ExifTool (arbitrary, no limit imposed by ICC
        # spec)
        tagCount = min(tagCount, 4096)

        # List of tag signatures, offsets and sizes
        # All local to this function; all property exports through "characteristics"
        # element object!
        tagSignatures = []
        tagOffsets = []
        tagSizes = []

        # Offset of start of first tag
        tagStart = 132
        for i in range(tagCount):
            # Extract tag signature (as binary string) for each entry
            tagSignature = self.boxContents[tagStart:tagStart + 4]
            tagOffset = bc.bytesToUInt(
                self.boxContents[tagStart + 4:tagStart + 8])
            tagSize = bc.bytesToUInt(
                self.boxContents[tagStart + 8:tagStart + 12])
            self.addCharacteristic("tag", tagSignature)

            # Add to list
            tagSignatures.append(tagSignature)
            tagOffsets.append(tagOffset)
            tagSizes.append(tagSize)

            # Start offset of next tag
            tagStart += 12

        # Get profile description from profile description tag
        # The following code could go wrong in case tagSignatures doesn't
        # contain description fields (e.g. if profile is corrupted); try block
        # will capture any such errors.

        try:
            i = tagSignatures.index(b'desc')
            descStartOffset = tagOffsets[i]
            descSize = tagSizes[i]
            descTag = self.boxContents[
                descStartOffset:descStartOffset + descSize]

            # Note that description of this tag is missing from recent versions of
            # standard; following code based on older version:
            # ICC.1:2001-04 File Format for Color Profiles [REVISION of ICC.1:1998-09]
            # Length of description (including terminating null character)
            descriptionLength = bc.bytesToUInt(descTag[8:12])

            # Description as binary string (excluding terminating null char)
            description = descTag[12:12 + descriptionLength - 1]
        except Exception:
            description = ""
        self.addCharacteristic("description", description)

    def validate_paletteBox(self):
        """Palette box (ISO/IEC 15444-1 Section I.5.3.4).

        Optional box that specifies a palette
        """
        # Number of entries in the table (each field is 2 bytes)
        nE = bc.bytesToUShortInt(self.boxContents[0:2])
        self.addCharacteristic("nE", nE)

        # nE within range 1-1024
        self.testFor("nEIsValid", 1 <= nE <= 1024)

        # Number of palette columns
        nPC = bc.bytesToUnsignedChar(self.boxContents[2:3])
        self.addCharacteristic("nPC", nPC)

        # nPC within range 1-255
        self.testFor("nPCIsValid", 1 <= nPC <= 255)

        # Following parameters are repeated for each column
        for i in range(nPC):

            # Bit depth of values created by column i
            b = bc.bytesToUnsignedChar(self.boxContents[3 + i:4 + i])

            # Most significant bit indicates whether palette column is signed (1)
            # or unsigned (0). Extracted by applying bit mask of 10000000
            # (=128)
            bSign = bc.getBitValue(b, 1)
            self.addCharacteristic("bSign", bSign)

            # Remaining bits indicate (bit depth - 1). Extracted by applying bit mask of
            # 01111111 (=127)
            bDepth = (b & 127) + 1
            self.addCharacteristic("bDepth", bDepth)

            # Bits depth field is valid if bDepth in range 1-38 (including
            # limits)
            self.testFor("bDepthIsValid", 1 <= bDepth <= 38)

            # If bDepth is not a multiple of 8 bits add padding bits
            # E.g. if bDepth is 10, bDepthPadded will be 16 bits, and
            # C value will be stored in low 10 bits of 16-bit field
            bDepthPadded = math.ceil(bDepth / 8) * 8
            bytesPadded = int(bDepthPadded / 8)

            # Start offset of cP entries for this column
            offset = nPC + 3 + i * (nE * bytesPadded)

            for _ in range(nE):
                # Get bytes for this entry
                cPAsBytes = self.boxContents[offset:offset + bytesPadded]

                # Convert to integer (cP could be *any* length so we cannot rely
                # on struct.unpack!)
                cP = bc.bytesToInteger(cPAsBytes)
                self.addCharacteristic("cP", cP)

                offset += bytesPadded

    def validate_componentMappingBox(self):
        """Component mapping box (ISO/IEC 15444-1 Section I.5.3.5).

        This box defines how image channels are identified from actual
        components
        """
        # Determine number of channels from box length
        numberOfChannels = int(len(self.boxContents) / 4)

        offset = 0

        # Loop through box contents and validate fields
        for _ in range(numberOfChannels):

            # Component index
            cMP = bc.bytesToUShortInt(self.boxContents[offset:offset + 2])
            self.addCharacteristic("cMP", cMP)

            # Allowed range: 0 - 16384
            self.testFor("cMPIsValid", 0 <= cMP <= 16384)

            # Specifies how channel is generated from codestream component
            mTyp = bc.bytesToUnsignedChar(
                self.boxContents[offset + 2:offset + 3])
            self.addCharacteristic("mTyp", mTyp)

            # Allowed range: 0 - 1
            self.testFor("mTypIsValid", 0 <= mTyp <= 1)

            # Palette component index
            pCol = bc.bytesToUnsignedChar(
                self.boxContents[offset + 3:offset + 4])
            self.addCharacteristic("pCol", pCol)

            # If mTyp equals 0, pCol must be 0 as well
            if mTyp == 0:
                pColIsValid = pCol == 0
            else:
                pColIsValid = True

            self.testFor("pColIsValid", pColIsValid)

            offset += 4

    def validate_channelDefinitionBox(self):
        """Channel definition box (ISO/IEC 15444-1 Section I.5.3.6;
        ISO/IEC 15444-15 Section D.6).

        This box specifies the meaning of the samples in each channel in the
        image.
        """
        # Number of channel descriptions (short integer)
        n = bc.bytesToUShortInt(self.boxContents[0:2])
        self.addCharacteristic("n", n)

        # Allowed range: 1 - 65535
        self.testFor("nIsValid", 1 <= n <= 65535)

        # Each channel description is made up of three 2-byte fields, so check
        # if size of box contents matches n
        boxLengthIsValid = len(self.boxContents) - 2 == n * 6
        self.testFor("boxLengthIsValid", boxLengthIsValid)

        # This list is used to keep track of number of alpha
        # channels and their respective cAssoc values
        alphaChannels = []

        # Loop through box contents and validate fields
        offset = 2
        for _ in range(n):
            # Channel index
            cN = bc.bytesToUShortInt(self.boxContents[offset:offset + 2])
            self.addCharacteristic("cN", cN)

            # Allowed range: 0 - 65535
            self.testFor("cNIsValid", 0 <= cN <= 65535)

            # Channel type
            cTyp = bc.bytesToUShortInt(self.boxContents[offset + 2:offset + 4])
            self.addCharacteristic("cTyp", cTyp)

            if self.format == 'jp2':
                # Only values from Table I.16 are allowed
                self.testFor("cTypIsValid", cTyp in [0, 1, 2, 65535])
            elif self.format == 'jph':
                # JPH adds application-defined value
                self.testFor("cTypIsValid", cTyp in [0, 1, 2, 3, 65535])
            # Channel Association
            cAssoc = bc.bytesToUShortInt(
                self.boxContents[offset + 4:offset + 6])
            self.addCharacteristic("cAssoc", cAssoc)

            # Allowed range: 0 - 65535
            self.testFor("cAssocIsValid", 0 <= cTyp <= 65535)

            if cTyp in [1, 2]:
                alphaChannels.append([cTyp, cAssoc])

            offset += 6

        if self.format == 'jph':
            # At most one cTyp field shall be equal to 1 or 2
            self.testFor("noMoreThanOneAlphaChannel", len(alphaChannels) <= 1)

            # Corresponding cAssoc field shall be equal to 0
            for channel in alphaChannels:
                self.testFor("cAssocAlphaChannelIsZero", channel[1] == 0)

    def validate_resolutionBox(self):
        """Resolution box (superbox)(ISO/IEC 15444-1 Section I.5.3.7.

        Specifies the capture and/or default display grid resolutions of
        the image.
        """
        # Marker tags/codes that identify all sub-boxes as hexadecimal strings
        tagCaptureResolutionBox = b'\x72\x65\x73\x63'
        tagDisplayResolutionBox = b'\x72\x65\x73\x64'

        # List for storing box type identifiers
        subBoxTypes = []

        noBytes = len(self.boxContents)
        byteStart = 0

        # Dummy value
        boxLengthValue = 10

        while byteStart < noBytes and boxLengthValue not in [0, -9999]:

            boxLengthValue, boxType, byteEnd, subBoxContents = self._getBox(byteStart,
                                                                            noBytes)

            # validate sub boxes
            resultsBox = BoxValidator(
                self.options,
                boxType,
                subBoxContents).validate()
            testsBox = resultsBox.tests
            characteristicsBox = resultsBox.characteristics
            warningsBox = resultsBox.warnings

            byteStart = byteEnd

            # Add to list of box types
            subBoxTypes.append(boxType)

            # Add test results, characteristics and warnings
            # to their respective trees
            self.tests.appendIfNotEmpty(testsBox)
            self.characteristics.append(characteristicsBox)
            self.warnings.appendIfNotEmpty(warningsBox)

        # This box contains either one Capture Resolution box, one Default Display
        # resolution box, or one of both
        self.testFor("containsCaptureOrDisplayResolutionBox",
                     tagCaptureResolutionBox in subBoxTypes or
                     tagDisplayResolutionBox in subBoxTypes)
        self.testFor("noMoreThanOneCaptureResolutionBox",
                     subBoxTypes.count(tagCaptureResolutionBox) <= 1)
        self.testFor("noMoreThanOneDisplayResolutionBox",
                     subBoxTypes.count(tagDisplayResolutionBox) <= 1)

    # Validator functions for boxes in Resolution box

    def validate_captureResolutionBox(self):
        """Capture  Resolution Box (ISO/IEC 15444-1 Section I.5.3.7.1)."""
        # Check box size, which must be 10 bytes
        self.testFor("boxLengthIsValid", len(self.boxContents) == 10)

        # Vertical / horizontal grid resolution numerators and denominators:
        # all values within range 1-65535

        # Vertical grid resolution numerator (2 byte integer)
        vRcN = bc.bytesToUShortInt(self.boxContents[0:2])
        self.addCharacteristic("vRcN", vRcN)
        self.testFor("vRcNIsValid", 1 <= vRcN <= 65535)

        # Vertical grid resolution denominator (2 byte integer)
        vRcD = bc.bytesToUShortInt(self.boxContents[2:4])
        self.addCharacteristic("vRcD", vRcD)
        self.testFor("vRcDIsValid", 1 <= vRcD <= 65535)

        # Horizontal grid resolution numerator (2 byte integer)
        hRcN = bc.bytesToUShortInt(self.boxContents[4:6])
        self.addCharacteristic("hRcN", hRcN)
        self.testFor("hRcNIsValid", 1 <= hRcN <= 65535)

        # Horizontal grid resolution denominator (2 byte integer)
        hRcD = bc.bytesToUShortInt(self.boxContents[6:8])
        self.addCharacteristic("hRcD", hRcD)
        self.testFor("hRcDIsValid", 1 <= hRcD <= 65535)

        # Vertical / horizontal grid resolution exponents:
        # values within range -128-127

        # Vertical grid resolution exponent (1 byte signed integer)
        vRcE = bc.bytesToSignedChar(self.boxContents[8:9])
        self.addCharacteristic("vRcE", vRcE)
        self.testFor("vRcEIsValid", -128 <= vRcE <= 127)

        # Horizontal grid resolution exponent (1 byte signed integer)
        hRcE = bc.bytesToSignedChar(self.boxContents[9:10])
        self.addCharacteristic("hRcE", hRcE)
        self.testFor("hRcEIsValid", -128 <= hRcE <= 127)

        # Include vertical and horizontal resolution values in pixels per meter
        # and pixels per inch in output
        vRescInPixelsPerMeter = (vRcN / vRcD) * (10 ** (vRcE))
        self.addCharacteristic(
            "vRescInPixelsPerMeter", round(vRescInPixelsPerMeter, 2))

        hRescInPixelsPerMeter = (hRcN / hRcD) * (10 ** (hRcE))
        self.addCharacteristic(
            "hRescInPixelsPerMeter", round(hRescInPixelsPerMeter, 2))

        vRescInPixelsPerInch = vRescInPixelsPerMeter * 25.4e-3
        self.addCharacteristic(
            "vRescInPixelsPerInch", round(vRescInPixelsPerInch, 2))

        hRescInPixelsPerInch = hRescInPixelsPerMeter * 25.4e-3
        self.addCharacteristic(
            "hRescInPixelsPerInch", round(hRescInPixelsPerInch, 2))

    def validate_displayResolutionBox(self):
        """Default Display  Resolution Box (ISO/IEC 15444-1 Section I.5.3.7.2)."""
        # Check box size, which must be 10 bytes
        self.testFor("boxLengthIsValid", len(self.boxContents) == 10)

        # Vertical / horizontal grid resolution numerators and denominators:
        # all values within range 1-65535

        # Vertical grid resolution numerator (2 byte integer)
        vRdN = bc.bytesToUShortInt(self.boxContents[0:2])
        self.addCharacteristic("vRdN", vRdN)
        self.testFor("vRdNIsValid", 1 <= vRdN <= 65535)

        # Vertical grid resolution denominator (2 byte integer)
        vRdD = bc.bytesToUShortInt(self.boxContents[2:4])
        self.addCharacteristic("vRdD", vRdD)
        self.testFor("vRdDIsValid", 1 <= vRdD <= 65535)

        # Horizontal grid resolution numerator (2 byte integer)
        hRdN = bc.bytesToUShortInt(self.boxContents[4:6])
        self.addCharacteristic("hRdN", hRdN)
        self.testFor("hRdNIsValid", 1 <= hRdN <= 65535)

        # Horizontal grid resolution denominator (2 byte integer)
        hRdD = bc.bytesToUShortInt(self.boxContents[6:8])
        self.addCharacteristic("hRdD", hRdD)
        self.testFor("hRdDIsValid", 1 <= hRdD <= 65535)

        # Vertical / horizontal grid resolution exponents:
        # values within range -128-127

        # Vertical grid resolution exponent (1 byte signed integer)
        vRdE = bc.bytesToSignedChar(self.boxContents[8:9])
        self.addCharacteristic("vRdE", vRdE)
        self.testFor("vRdEIsValid", -128 <= vRdE <= 127)

        # Horizontal grid resolution exponent (1 byte signed integer)
        hRdE = bc.bytesToSignedChar(self.boxContents[9:10])
        self.addCharacteristic("hRdE", hRdE)
        self.testFor("hRdEIsValid", -128 <= hRdE <= 127)

        # Include vertical and horizontal resolution values in pixels per meter
        # and pixels per inch in output
        vResdInPixelsPerMeter = (vRdN / vRdD) * (10 ** (vRdE))
        self.addCharacteristic(
            "vResdInPixelsPerMeter", round(vResdInPixelsPerMeter, 2))

        hResdInPixelsPerMeter = (hRdN / hRdD) * (10 ** (hRdE))
        self.addCharacteristic(
            "hResdInPixelsPerMeter", round(hResdInPixelsPerMeter, 2))

        vResdInPixelsPerInch = vResdInPixelsPerMeter * 25.4e-3
        self.addCharacteristic(
            "vResdInPixelsPerInch", round(vResdInPixelsPerInch, 2))

        hResdInPixelsPerInch = hResdInPixelsPerMeter * 25.4e-3
        self.addCharacteristic(
            "hResdInPixelsPerInch", round(hResdInPixelsPerInch, 2))

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
        marker, _, segContents, offsetNext = self._getMarkerSegment(offset)

        # Marker must be start-of-codestream marker
        self.testFor("codestreamStartsWithSOCMarker", marker == b'\xff\x4f')
        offset = offsetNext

        # Read next marker segment. This must be the SIZ (image and tile
        # size) marker
        marker, _, segContents, offsetNext = self._getMarkerSegment(offset)
        foundSIZMarker = marker == b'\xff\x51'
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
                marker, _, segContents, offsetNext = self._getMarkerSegment(offset)

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
            self.testFor("ccocValuesConsecutive", shared.consecutive(ccocValuesMain))
            self.testFor("cqccValuesConsecutive", shared.consecutive(cqccValuesMain))

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

                compressionRatio = self._calculateCompressionRatio(length,
                                                                   ssizDepthValues,
                                                                   (ysiz - yOsiz),
                                                                   (xsiz - xOsiz))
                compressionRatio = round(compressionRatio, 2)
                self.addCharacteristic("compressionRatio", compressionRatio)

        # Valid codestream only if all tests returned True
        self.isValid = self._isValid()

    def validate_xmlBox(self):
        """XML Box (ISO/IEC 15444-1 Section I.7.1)."""
        data = self.boxContents

        # Data must be well-formed XML. Try to parse data to Element
        # instance.

        try:
            dataAsElement = ET.fromstring(data)

            # Add data to characteristics tree
            self.characteristics.append(dataAsElement)

            # If no exception was raised data contains well-formed XML
            containsWellformedXML = True
        except Exception:
            # If parse raised error this is not well-formed XML
            containsWellformedXML = False

            # Useful for extracting null-terminated XML (older Kakadu versions)
            if self.nullxmlFlag:
                try:
                    data = bc.removeNullTerminator(data)
                    dataAsElement = ET.fromstring(data)
                    self.characteristics.append(dataAsElement)
                except Exception:
                    pass

        self.testFor("containsWellformedXML", containsWellformedXML)

    def validate_uuidBox(self):
        """UUID Box (ISO/IEC 15444-1 Section I.7.2).

        For details on UUIDs see: http://tools.ietf.org/html/rfc4122.html

        Box contains 16-byte identifier, followed by block of data.
        Format of data is defined outside of the scope of JPEG 2000,
        so in most cases there's not much to validate here. Exception:
        if uuid = be7acfcb-97a9-42e8-9c71-999491e3afac this indicates
        presence of XMP metadata.
        """
        boxLength = len(self.boxContents)

        # Check box size, which must be greater than 16 bytes
        self.testFor("boxLengthIsValid", boxLength > 16)

        # First 16 bytes contain UUID, convert to string of hex digits
        # in standard form
        boxUUID = str(uuid.UUID(bytes=self.boxContents[0:16]))

        if boxUUID == "be7acfcb-97a9-42e8-9c71-999491e3afac":
            # XMP packet
            data = self.boxContents[16:boxLength]

            # Data must be well-formed XML. Try to parse data to Element
            # instance.

            try:
                dataAsElement = ET.fromstring(data)

                # Add data to characteristics tree
                self.characteristics.append(dataAsElement)

                # If no exception was raised data contains well-formed XML
                containsWellformedXML = True
            except BaseException:
                # If parse raised error this is not well-formed XML
                containsWellformedXML = False

                # Useful for extracting null-terminated XML (older Kakadu
                # versions)
                if self.nullxmlFlag:
                    try:
                        data = bc.removeNullTerminator(data)
                        dataAsElement = ET.fromstring(data)
                        self.characteristics.append(dataAsElement)
                    except BaseException:
                        pass

            self.testFor("containsWellformedXML", containsWellformedXML)
        else:
            # Only add to UUID to characteristics tree
            self.addCharacteristic("uuid", boxUUID)

    def validate_uuidInfoBox(self):
        """UUID Info box (superbox)(ISO/IEC 15444-1 Section I.7.3).

        Provides additional information on vendor-specific UUIDs.
        """
        # Marker tags/codes that identify sub-boxes as hexadecimal strings
        tagListBox = b'\x75\x6c\x73\x74'
        tagURLBox = b'\x75\x72\x6c\x20'

        # List for storing box type identifiers
        subBoxTypes = []

        noBytes = len(self.boxContents)
        byteStart = 0

        # Dummy value
        boxLengthValue = 10

        while byteStart < noBytes and boxLengthValue not in [0, -9999]:

            boxLengthValue, boxType, byteEnd, subBoxContents = self._getBox(byteStart,
                                                                            noBytes)

            # validate sub boxes
            resultsBox = BoxValidator(
                self.options,
                boxType,
                subBoxContents).validate()
            testsBox = resultsBox.tests
            characteristicsBox = resultsBox.characteristics
            warningsBox = resultsBox.warnings

            byteStart = byteEnd

            # Add to list of box types
            subBoxTypes.append(boxType)

            # Add test results, characteristics and warnings
            # to their respective trees
            self.tests.appendIfNotEmpty(testsBox)
            self.characteristics.append(characteristicsBox)
            self.warnings.appendIfNotEmpty(warningsBox)

        # This box contains one UUID List box and one Data Entry URL box
        self.testFor("containsOneListBox", subBoxTypes.count(tagListBox) == 1)
        self.testFor("containsOneURLBox", subBoxTypes.count(tagURLBox) == 1)

    def validate_uuidListBox(self):
        """UUID List box (ISO/IEC 15444-1 Section I.7.3.1).

        Contains a list of UUIDs.
        """
        # Number of UUIDs
        nU = bc.bytesToUShortInt(self.boxContents[0:2])
        self.addCharacteristic("nU", nU)

        # Each UUID is 16 byte string, so check if total box length is valid
        self.testFor("boxLengthIsValid", len(self.boxContents) == nU * 16 + 2)

        # Loop through all UUIDs
        offset = 2
        for _ in range(nU):
            boxUUID = str(
                uuid.UUID(bytes=self.boxContents[offset:offset + 16]))
            self.addCharacteristic("uuid", boxUUID)
            offset += 16

    def validate_urlBox(self):
        """Data Entry URL box (ISO/IEC 15444-1 Section I.7.3.2).

        Contains URL that can be used to obtain more information
        about UUIDs in UUID List box.
        """
        # Version number (1 byte unsigned integer)
        version = bc.bytesToUnsignedChar(self.boxContents[0:1])
        self.addCharacteristic("version", version)

        # Value of version shall be 0
        self.testFor("versionIsValid", version == 0)

        # Next item reserved to flag particular attributes of this box
        # (defined as 3-byte integer in standard, but since this is not
        # readily supported in Python we'll treat it as a bytes object)
        flag = self.boxContents[1:4]

        # All bytes must be 0
        self.testFor("flagIsValid", flag == b'\x00\x00\x00')

        # Location: this is the actual URL, encoded as a UTF-8 string
        loc = self.boxContents[4:len(self.boxContents)]

        # Last byte of loc must be null terminator
        self.testFor("locHasNullTerminator", loc.endswith(b'\x00'))

        # Remove null character as this cannot be represented as XML
        loc = bc.removeNullTerminator(loc)

        # Try decode to UTF-8
        try:
            loc.decode("utf-8", "strict")
            self.testFor("locIsUTF8", True)
        except UnicodeDecodeError:
            self.testFor("locIsUTF8", False)

        self.addCharacteristic("loc", loc)
