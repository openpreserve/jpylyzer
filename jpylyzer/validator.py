#! /usr/bin/env python3

from . import byteconv as bc
from . import shared


class Validator:
    """Generic validator class
    """

    def __init__(self, options):
        """Initialise a Validator."""
        self.options = options
        self.verboseFlag = self.options['verboseFlag']
        self.boxType = None
        self.boxContents = None
        self.characteristics = None
        self.tests = None
        self.warnings = None

    def validate(self):
        """Generic validation function."""
        try:
            to_call = getattr(self, "validate_" + self.boxType)
            to_call()
        except AttributeError:
            # Don't think this should ever happen because all known boxes
            # are defined in boxTypeMap and anything not in boxTypeMap should
            # trigger "unknown" box validator function
            ## TEST
            raise
            ## TEST
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
