#! /usr/bin/env python3
"""
Validation of ICC profiles
"""

from __future__ import division
from . import etpatch as ET
from . import byteconv as bc
from .validator import Validator


class IccValidator(Validator):
    """Validator class for ICC profiles
       Currently this class is only used to report ICC profile properties,
       without any actual validation (which is out of Jpylyzer's scope)
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
        self.boxType = "icc"

        self.characteristics = ET.Element(self.boxType)
        self.tests = ET.Element(self.boxType)
        self.warnings = ET.Element(self.boxType)

        self.boxContents = boxContents
        self.bTypeString = bType

    # Validator function for ICC profiles

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
        profileVersion = "%s.%s.%s" % (profileMajorRevision,
                                       profileMinorRevision,
                                       profileBugFixRevision)
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
