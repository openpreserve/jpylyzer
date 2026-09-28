#! /usr/bin/env python3

from __future__ import division
import uuid
import math
from . import etpatch as ET
from . import byteconv as bc
from . import shared
from .validator import Validator
from .codestream import CSValidator
from .icc import IccValidator

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
        else:
            self.boxType = 'unknownBox'

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
        colourSpecificationBoxesAreContiguous = self._listOccurrencesAreContiguous(
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
            iccResults = IccValidator(self.options, 'icc', profile).validate()
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
            iccResults = IccValidator(self.options, 'icc', profile).validate()
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

        # Validate codestream
        resultsCodestream = CSValidator(self.options, "codestream", self.boxContents).validate()
        self.tests = resultsCodestream.tests
        self.characteristics = resultsCodestream.characteristics
        self.warnings = resultsCodestream.warnings

        ## Update root element tags
        self.tests.tag = self.boxType
        self.characteristics.tag = self.boxType
        self.warnings.tag = self.boxType

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
