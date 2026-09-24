#! /usr/bin/env python3

from . import byteconv as bc
from . import shared


class Validator:
    """Generic validator class
    """

    def __init__(self, options, bType, boxContents,
                 startOffset=None, components=None):
        """Initialise a Validator."""

        self.options = None
        self.verboseFlag = None
        self.boxType = None
        self.boxContents = None
        self.characteristics = None
        self.tests = None
        self.warnings = None
        # The following two dictionaries map the hexadecimal strings that identify boxes and and marker
        # segments to corresponding hexadecimal strings

        # Boxes, sub-boxes. These correspond to values in  Table I.4 (Defined boxes) of ISO/IEC 15444-1

        self.boxTypeMap = {
            b'\x6a\x70\x32\x69': "intellectualPropertyBox",
            b'\x78\x6d\x6c\x20': "xmlBox",
            b'\x75\x75\x69\x64': "uuidBox",
            b'\x75\x69\x6e\x66': "uuidInfoBox",
            b'\x6a\x50\x20\x20': "signatureBox",
            b'\x66\x74\x79\x70': "fileTypeBox",
            b'\x6a\x70\x32\x68': "jp2HeaderBox",
            b'\x69\x68\x64\x72': "imageHeaderBox",
            b'\x62\x70\x63\x63': "bitsPerComponentBox",
            b'\x63\x6f\x6c\x72': "colourSpecificationBox",
            b'\x70\x63\x6c\x72': "paletteBox",
            b'\x63\x6d\x61\x70': "componentMappingBox",
            b'\x63\x64\x65\x66': "channelDefinitionBox",
            b'\x72\x65\x73\x20': "resolutionBox",
            b'\x6a\x70\x32\x63': "contiguousCodestreamBox",
            b'\x72\x65\x73\x63': "captureResolutionBox",
            b'\x72\x65\x73\x64': "displayResolutionBox",
            b'\x75\x6c\x73\x74': "uuidListBox",
            b'\x75\x72\x6c\x20': "urlBox",
            'icc': 'icc'
        }

        # Codestream marker segments. These correspond to values in  Table A.2
        # (List of markers and marker segments) of ISO/IEC 15444-1

        self.markerTypeMap = {
            b'\xff\x50': "cap",
            b'\xff\x51': "siz",
            b'\xff\x56': "prf",
            b'\xff\x52': "cod",
            b'\xff\x5c': "qcd",
            b'\xff\x64': "com",
            b'\xff\x53': "coc",
            b'\xff\x5e': "rgn",
            b'\xff\x5d': "qcc",
            b'\xff\x5f': "poc",
            b'\xff\x55': "tlm",
            b'\xff\x57': "plm",
            b'\xff\x58': "plt",
            b'\xff\x59': "cpf",
            b'\xff\x60': "ppm",
            b'\xff\x61': "ppt",
            b'\xff\x63': "crg",
            b'\xff\x90': "tilePart",
            'startOfTile': 'sot'
        }

        # Reverse access of boxTypemap and .markerTypeMap for quick lookup
        self.boxTagMap = {v: k for k, v in self.boxTypeMap.items()}
        self.markerTagMap = {v: k for k, v in self.markerTypeMap.items()}

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

    def _parse_ipl(self, lpl, offset):
        """Parse Iplt/Iplm parameters into a comma separated string of (hex) values.

        The logic here is basically:
        Each iplt/iplm is a collection of 7 bits, where the MSB signifies the following 7 bits
        are to be prepended to the following 7 LSB bits.
        Eg: boxContents = [0C,9F,62,7C] becomes [0C,FE2,7C], as
        9F  = 10011111
        62  =        01100010
        FE2 = 000111111100010
        See table A.36 for more details.

        - lpl: lplt/lplm parameter.
        - offset: the offset (from marker code) to iplt/iplm parameter.
            For iplt this will be 3 (sizeof(lplt) + sizeof(zplt)),
            for iplm this will be 4 sizeof(lplm) + sizeof(zplm) + sizeof(nplm)
        """
        iplt = ''
        i = offset
        while i < lpl and i < len(
                self.boxContents):  # Don't over-read on bad lplt/lplm
            ipl_i_len = 1  # number of bytes making up the current ipl(t|m)_i
            while bc.bytesToUnsignedChar(
                    self.boxContents[i + ipl_i_len - 1:i + ipl_i_len]) & 0x80:
                ipl_i_len += 1

            # Join all the segments together
            iplt_i = bc.bytesToUnsignedChar(self.boxContents[i:i + 1])
            for ipl_index in range(1, ipl_i_len):
                iplt_i = (iplt_i & 0x7F) << 7
                iplt_i |= bc.bytesToUnsignedChar(
                    self.boxContents[i + ipl_index:i + ipl_index + 1])

            i += ipl_i_len
            iplt += ('{:0' + str(2 * ipl_i_len) + 'X},').format(iplt_i)
        return iplt[:-1]

    def _consecutive(self, lst):
        """Return True if items in lst are consecutive numbers."""
        for i in range(1, len(lst)):
            if lst[i] - lst[i - 1] != 1:
                return False
        return True

    def _listOccurrencesAreContiguous(self, lst, value):
        """Return True if all occurrences of value in lst are at contiguous positions."""
        indices_of_value = [i for i in range(len(lst)) if lst[i] == value]
        return self._consecutive(indices_of_value)
