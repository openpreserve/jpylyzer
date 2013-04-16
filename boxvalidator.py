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
import config
import etpatch as ET
import byteconv as bc
from shared import listOccurrencesAreContiguous
from shared import printWarning

class BoxValidator:
	# Marker tags/codes that identify all sub-boxes as hexadecimal strings
	#(Correspond to "Box Type" values, see ISO/IEC 15444-1 Section I.4)
	typeMap = {
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
		b'\xff\x51': "siz",
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
		b'\xff\x60': "ppm",
		b'\xff\x61': "ppt",
		b'\xff\x63': "crg",
		b'\xff\x90': "tilePart",
		'icc': 'icc',
		'startOfTile': 'sot'
	}
	
	# Reverse access of typemap for quick lookup
	boxTagMap = {v:k for k, v in typeMap.items()}

	def __init__(self, bType, boxContents, startOffset = None):
		if bType in self.typeMap:
			self.boxType = self.typeMap[bType]
		elif bType == "JP2":
			self.characteristics = ET.Element("properties")
			self.tests = ET.Element("tests")
			self.boxType = "JP2"
		else:
			self.boxType = 'unknownBox'

		if self.boxType != "JP2":
			self.characteristics = ET.Element(self.boxType)
			self.tests = ET.Element(self.boxType)

		self.boxContents = boxContents
		self.startOffset = startOffset
		self.returnOffset = None
		self.isValid = None
		self.bTypeString = bType

	def validate(self):
		try:
			to_call = getattr(self, "validate_" + self.boxType)
		except AttributeError:
			printWarning("ignoring '" + self.boxType + "' (validator function not yet implemented)" )

		else:
			to_call()

		if self.isValid is not None:
			return (self.isValid, self.tests, self.characteristics)
		elif self.returnOffset is None:
			return (self.tests, self.characteristics)
		else:
			return (self.tests, self.characteristics, self.returnOffset)

	def _isValid(self):
		for elt in self.tests.iter():
			if elt.text == False:
				# File didn't pass this test, so not valid
				return(False)
		return(True)

	
	def _getBox(self, byteStart, noBytes):
		# Parse JP2 box and return information on its
		# size, type and contents
		
		# Box length (4 byte unsigned integer)
		boxLengthValue = bc.bytesToUInt(self.boxContents[byteStart:byteStart+4])
		
		# Box type
		boxType = self.boxContents[byteStart+4:byteStart+8]
		
		# Start byte of box contents
		contentsStartOffset = 8
		
		# Read extended box length if box length value equals 1
		# In that case contentsStartOffset should also be 16 (not 8!)
		# (See ISO/IEC 15444-1 Section I.4)
		if boxLengthValue == 1:
			boxLengthValue = bc.bytesToULongLong(self.boxContents[byteStart+8:byteStart+16])
			contentsStartOffset = 16
		
		# For the very last box in a file boxLengthValue may equal 0, so we need
		# to calculate actual value
		if boxLengthValue == 0:
			boxLengthValue = noBytes-byteStart
		
		# End byte for current box
		byteEnd = byteStart + boxLengthValue
		
		# Contents of this box as a byte object (i.e. 'DBox' in ISO/IEC 15444-1 Section I.4)
		boxContents = self.boxContents[byteStart+contentsStartOffset:byteEnd]
		
		return (boxLengthValue, boxType, byteEnd, boxContents)

	
	def _getMarkerSegment(self,offset):
		# Read marker segment that starts at offset and return marker, size,
		# contents and start offset of next marker
		
		# First 2 bytes: 16 bit marker
		marker = self.boxContents[offset:offset+2]
		
		# Check if this is a delimiting marker segment
		if marker in [b'\xff\x4f',b'\xff\x93',b'\xff\xd9',b'\xff\x92']:
			# Zero-length markers: SOC, SOD, EOC, EPH
			length=0
		else:
			# Not a delimiting marker, so remainder contains some data
			length=bc.bytesToUShortInt(self.boxContents[offset+2:offset+4])
			
		# Contents of marker segment (excluding marker) to binary string
		contents=self.boxContents[offset+2:offset + 2 +length]
			
		if length== -9999:
			# If length couldn't be determined because of decode error,
			# return bogus value for offsetNext (calling function should
			# handle this further!)
			offsetNext=-9999
					
		else:
			# Offset value start of next marker segment
			offsetNext=offset+length+2
		
		return(marker,length,contents,offsetNext)

	def _calculateCompressionRatio(self, noBytes,bPCDepthValues,height,width):
		# Computes compression ratio
		# noBytes: size of compressed image in bytes
		# bPCDepthValues: list with bits per component for each component
		# height, width: image height, width
		
		# Total bits per pixel
		bitsPerPixel = 0
		
		for i in range(len(bPCDepthValues)):
			bitsPerPixel += bPCDepthValues[i]
		
		# Convert to bytes per pixel
		bytesPerPixel = bitsPerPixel/8
		
		# Uncompressed image size
		sizeUncompressed = bytesPerPixel*height*width
		
		# Compression ratio
		if noBytes != 0:
			compressionRatio = sizeUncompressed / noBytes
		else:
			# Obviously something going wrong here ...
			compressionRatio = -9999
		
		return(compressionRatio) 

	def _getBitValue(self, n, p):
		# Get the bit value of denary (base 10) number n at the equivalent binary
		# position p (binary count starts at position 1 from the left)
		# Only works if n can be expressed as 8 bits !!!
		
		# Word length in bits
		wordLength=8
		
		# Shift = word length - p
		shift=wordLength-p
		
		return (n >> shift) & 1

	def testFor(self, testType, testResult):
		# Add testResult node to tests element tree
		
		#print(config.outputVerboseFlag)
		
		if config.outputVerboseFlag == False:
			# Non-verbose output: only add results of tests that failed 
			if testResult==False:
				self.tests.appendChildTagWithText(testType, testResult)
		
		else:
			# Verbose output, add results of all tests
			self.tests.appendChildTagWithText(testType, testResult)
		

	def addCharacteristic(self, characteristic, charValue):
		# Add characteristic node to characteristics element tree
		
		self.characteristics.appendChildTagWithText(characteristic, charValue)

	# Validator functions for boxes
	
	def validate_unknownBox(self):

		# Although jpylyzer doesn't "know" anything about this box, we
		# can at least report the 4 characters from the Box Type field
		# (TBox) here
		
		boxType=self.bTypeString
		
		# If boxType contains any device control characters (e.g. because of
		# file corruption), replace them  with printable character
		if bc.containsControlCharacters(boxType):
			boxType=bc.replaceControlCharacters(boxType)
		
		# Decode to string with Latin encoding
		# Elementtree will deal with any non-ASCII characters by replacing
		# them with numeric entity references
		boxType=boxType.decode("iso-8859-15","strict")
		
		# Add (cleaned up) boxType string to output
		self.addCharacteristic( "boxType", boxType)
		
		# Print warning message to screen		
		printWarning("ignoring unknown box")

	def validate_signatureBox(self):
		# Signature box (ISO/IEC 15444-1 Section I.5.2)
				
		# Check box size, which should be 4 bytes
		self.testFor("boxLengthIsValid", len(self.boxContents) == 4)
		
		# Signature *not* added to characteristics output, because it contains non-printable characters)
		self.testFor("signatureIsValid", self.boxContents[0:4] == b'\x0d\x0a\x87\x0a')

	def validate_fileTypeBox(self):
		# File type box (ISO/IEC 15444-1 Section I.5.2)
		
		# Determine number of compatibility fields from box length
		numberOfCompatibilityFields=(len(self.boxContents)-8)/4
		
		# This should never produce a decimal number (would indicate missing data)
		self.testFor("boxLengthIsValid", numberOfCompatibilityFields == int(numberOfCompatibilityFields))

		# Brand value
		br = self.boxContents[0:4]
		self.addCharacteristic( "br", br)

		# Is brand value valid?
		self.testFor("brandIsValid", br == b'\x6a\x70\x32\x20')

		# Minor version
		minV = bc.bytesToUInt(self.boxContents[4:8])
		self.addCharacteristic("minV", minV)

		# Value should be 0
		# Note that conforming readers should continue to process the file
		# even if this field contains siome other value
		self.testFor("minorVersionIsValid", minV == 0)

		# Compatibility list (one or more 4-byte fields)
		# Create list object and store all entries as separate list elements
		cLList = []
		offset = 8
		
		for i in range(int(numberOfCompatibilityFields)):
				cL = self.boxContents[offset:offset+4]
				self.addCharacteristic("cL", cL)
				cLList.append(cL)
				offset += 4

		# Compatibility list should contain at least one field with mandatory value.
		# List is considered valid if this value is found.
		self.testFor("compatibilityListIsValid", b'\x6a\x70\x32\x20' in cLList)
	
	def validate_jp2HeaderBox(self):
		# JP2 header box (superbox) (ISO/IEC 15444-1 Section I.5.3)
		
		# List for storing box type identifiers
		subBoxTypes = []
		noBytes = len(self.boxContents)
		byteStart = 0
		bytesTotal = 0

		# Dummy value
		boxLengthValue = 10
		while byteStart < noBytes and boxLengthValue != 0:
			boxLengthValue, boxType, byteEnd, subBoxContents = self._getBox(byteStart, noBytes)

			# Validate sub-boxes
			resultBox, characteristicsBox = BoxValidator(boxType, subBoxContents).validate()

			byteStart = byteEnd

			# Add to list of box types
			subBoxTypes.append(boxType)

			# Add analysis results to test results tree
			self.tests.appendIfNotEmpty(resultBox)

			# Add extracted characteristics to characteristics tree
			self.characteristics.append(characteristicsBox)

		# Do all required header boxes exist?
		self.testFor("containsImageHeaderBox", self.boxTagMap['imageHeaderBox'] in subBoxTypes)
		self.testFor("containsColourSpecificationBox", self.boxTagMap['colourSpecificationBox'] in subBoxTypes)

		# If bPCSign equals 1 and bPCDepth equals 128 (equivalent to bPC field being
		# 255), this box should contain a Bits Per Components box
		sign = self.characteristics.findElementText('imageHeaderBox/bPCSign')
		depth = self.characteristics.findElementText('imageHeaderBox/bPCDepth')

		if sign == 1 and depth == 128:
			self.testFor("containsBitsPerComponentBox", self.boxTagMap['bitsPerComponentBox'] in subBoxTypes)

		# Is the first box an Image Header Box?
		try:
			firstJP2HeaderBoxIsImageHeaderBox=subBoxTypes[0] == self.boxTagMap['imageHeaderBox']
		except:
			firstJP2HeaderBoxIsImageHeaderBox=False

		self.testFor("firstJP2HeaderBoxIsImageHeaderBox",firstJP2HeaderBoxIsImageHeaderBox)

		# Some boxes can have multiple instances, whereas for others only one
		# is allowed
		self.testFor("noMoreThanOneImageHeaderBox",  subBoxTypes.count(self.boxTagMap['imageHeaderBox']) <= 1)
		self.testFor("noMoreThanOneBitsPerComponentBox", subBoxTypes.count(self.boxTagMap['bitsPerComponentBox']) <= 1)
		self.testFor("noMoreThanOnePaletteBox", subBoxTypes.count(self.boxTagMap['paletteBox']) <= 1)
		self.testFor("noMoreThanOneComponentMappingBox", subBoxTypes.count(self.boxTagMap['componentMappingBox']) <= 1)
		self.testFor("noMoreThanOneChannelDefinitionBox", subBoxTypes.count(self.boxTagMap['channelDefinitionBox']) <= 1)
		self.testFor("noMoreThanOneResolutionBox", subBoxTypes.count(self.boxTagMap['resolutionBox']) <= 1)

		# In case of multiple colour specification boxes, they should appear contiguously
		# within the header box
		colourSpecificationBoxesAreContiguous=listOccurrencesAreContiguous(subBoxTypes, self.boxTagMap['colourSpecificationBox'])
		self.testFor("colourSpecificationBoxesAreContiguous",colourSpecificationBoxesAreContiguous)

		# If JP2 Header box contains a Palette Box, it should also contain a component
		# mapping box, and vice versa
		if (self.boxTagMap['paletteBox'] in subBoxTypes and self.boxTagMap['componentMappingBox'] not in subBoxTypes) \
		or (self.boxTagMap['componentMappingBox'] in subBoxTypes and self.boxTagMap['paletteBox'] not in subBoxTypes):
			paletteAndComponentMappingBoxesOnlyTogether=False
		else:
			paletteAndComponentMappingBoxesOnlyTogether=True

		self.testFor("paletteAndComponentMappingBoxesOnlyTogether",paletteAndComponentMappingBoxesOnlyTogether)


	# Validator functions for boxes in JP2 Header superbox
	
	def validate_imageHeaderBox(self):
		# Image header box (ISO/IEC 15444-1 Section I.5.3.1)	
		# This is a fixed-length box that contains generic image info.

		# Check box length (14 bytes, excluding box length/type fields)
		self.testFor("boxLengthIsValid", len(self.boxContents) == 14)

		# Image height and width (both as unsigned integers)
		height = bc.bytesToUInt(self.boxContents[0:4])
		self.addCharacteristic("height", height)
		width = bc.bytesToUInt(self.boxContents[4:8])
		self.addCharacteristic("width", width)

		# Height and width should be within range 1 - (2**32)-1
		self.testFor("heightIsValid", 1 <= height <= (2**32)-1)
		self.testFor("widthIsValid", 1 <= width <= (2**32)-1)
	
		# Number of components (unsigned short integer)
		nC = bc.bytesToUShortInt(self.boxContents[8:10])
		self.addCharacteristic("nC", nC)
	
		# Number of components should be in range 1 - 16384 (including limits)
		self.testFor("nCIsValid", 1 <= nC <= 16384)

		# Bits per component (unsigned character)
		bPC = bc.bytesToUnsignedChar(self.boxContents[10:11])
	
		# Most significant bit indicates whether components are signed (1)
		# or unsigned (0).
		bPCSign = self._getBitValue(bPC, 1)
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

		if bPCDepthIsWithinAllowedRange == True or bitDepthIsVariable == True:
			bPCIsValid=True
		else:
			bPCIsValid=False

		self.testFor("bPCIsValid",bPCIsValid)
		
		# Compression type (unsigned character)
		c = bc.bytesToUnsignedChar(self.boxContents[11:12])
		self.addCharacteristic("c", c)
		
		# Value should always be 7
		self.testFor("cIsValid", c == 7)
		
		# Colourspace unknown field (unsigned character)
		unkC = bc.bytesToUnsignedChar(self.boxContents[12:13])
		self.addCharacteristic("unkC", unkC)
		
		# Value should be 0 or 1
		self.testFor("unkCIsValid", 0 <= unkC <= 1)
		
		# Intellectual Property field (unsigned character)
		iPR = bc.bytesToUnsignedChar(self.boxContents[13:14])
		self.addCharacteristic("iPR",iPR)
		
		# Value should be 0 or 1
		self.testFor("iPRIsValid", 0 <= iPR <= 1)


	def validate_bitsPerComponentBox(self):
		# bits per component box (ISO/IEC 15444-1 Section I.5.3.2)
		# Optional box that specifies bit depth of each component
		
		# Number of bPC field (each field is 1 byte)
		numberOfBPFields = len(self.boxContents)

		# Validate all entries
		for i in range(numberOfBPFields):

			# Bits per component (unsigned character)
			bPC = bc.bytesToUnsignedChar(self.boxContents[i:i+1])

			# Most significant bit indicates whether components are signed (1)
			# or unsigned (0). Extracted by applying bit mask of 10000000 (=128)
			bPCSign = self._getBitValue(bPC, 1)
			self.addCharacteristic("bPCSign",bPCSign)

			# Remaining bits indicate (bit depth - 1). Extracted by applying bit mask of
			# 01111111 (=127)
			bPCDepth=(bPC & 127) + 1
			self.addCharacteristic("bPCDepth",bPCDepth)

			# Bits per component field is valid if bPCDepth in range 1-38 (including limits)
			self.testFor("bPCIsValid", 1 <= bPCDepth <= 38)


	def validate_colourSpecificationBox(self):
		# Colour specification box (ISO/IEC 15444-1 Section I.5.3.3)
		# This box defines one method for interpreting colourspace of decompressed
		# image data
		
		# Length of this box
		length = len(self.boxContents)

		# Specification method (unsigned character)
		meth = bc.bytesToUnsignedChar(self.boxContents[0:1])
		self.addCharacteristic("meth",meth)

		# Value should be 1 (enumerated colourspace) or 2 (restricted ICC profile)
		self.testFor("methIsValid", 1 <= meth <= 2)

		# Precedence (unsigned character)
		prec = bc.bytesToUnsignedChar(self.boxContents[1:2])
		self.addCharacteristic("prec",prec)

		# Value shall be 0 (but conforming readers should ignore it)
		self.testFor("precIsValid", prec == 0)

		# Colourspace approximation (unsigned character)
		approx = bc.bytesToUnsignedChar(self.boxContents[2:3])
		self.addCharacteristic("approx",approx)

		# Value shall be 0 (but conforming readers should ignore it)
		self.testFor("approxIsValid",approx == 0)

		# Colour space info: enumerated CS or embedded ICC profile,
		# depending on value of meth
		if meth == 1:
			# Enumerated colour space field (long integer)
			enumCS = bc.bytesToUInt(self.boxContents[3:length])
			self.addCharacteristic("enumCS",enumCS)

			# (Note: this will also trap any cases where enumCS is more/less than 4
			# bytes, as bc.bytesToUInt will return bogus negative value, which in turn is
			# handled by statement below)

			# Legal values: 16,17, 18
			self.testFor("enumCSIsValid", enumCS in [16,17,18])

		elif meth == 2:
			# Restricted ICC profile
			profile = self.boxContents[3:length]

			# Extract ICC profile properties as element object
			tests, iccCharacteristics = BoxValidator('icc', profile).validate() #self.getICCCharacteristics(profile)
			self.characteristics.append(iccCharacteristics)

			# Profile size property should equal actual profile size
			profileSize = iccCharacteristics.findElementText('profileSize')
			self.testFor("iccSizeIsValid", profileSize == len(profile))

			# Profile class must be 'input' or 'display'
			profileClass = iccCharacteristics.findElementText('profileClass')
			self.testFor("iccPermittedProfileClass", profileClass in [b'scnr',b'mntr'])

			# List of tag signatures may not contain "AToB0Tag", which indicates
			# an N-component LUT based profile, which is not allowed in JP2

			# Step 1: create list of all "tag" elements
			tagSignatureElements = iccCharacteristics.findall("tag")

			# Step 2: create list of all tag signatures and fill it
			tagSignatures=[]

			for i in range(len(tagSignatureElements)):
				tagSignatures.append(tagSignatureElements[i].text)

			# Step 3: verify non-existence of "AToB0Tag"
			self.testFor("iccNoLUTBasedProfile", b'A2B0' not in tagSignatures)

		elif meth == 3:
			# ICC profile embedded using "Any ICC" method. Belongs to Part 2 of the
			# standard (JPX), so if we get here by definition this is not valid JP2!
			profile = self.boxContents[3:length]

			# Extract ICC profile properties as element object
			tests, iccCharacteristics = BoxValidator('icc', profile).validate() #self.getICCCharacteristics(profile)
			self.characteristics.append(iccCharacteristics)

	def validate_icc(self):
		# Extracts characteristics (property-value pairs) of ICC profile
		# Note that although values are stored in  'text' property of sub-elements,
		# they may have a type other than 'text' (binary string, integers, lists)
		# This means that some post-processing (conversion to text) is needed to
		# write these property-value pairs to XML

		# Profile header properties (note: incomplete at this stage!)
		
		# Size in bytes
		profileSize=bc.bytesToUInt(self.boxContents[0:4])
		self.addCharacteristic("profileSize",profileSize)
		
		# Preferred CMM type
		preferredCMMType=self.boxContents[4:8]
		self.addCharacteristic("preferredCMMType",preferredCMMType)
		
		# Profile version: major revision
		profileMajorRevision=bc.bytesToUnsignedChar(self.boxContents[8:9])
		
		# Profile version: minor revision
		profileMinorRevisionByte=bc.bytesToUnsignedChar(self.boxContents[9:10])
		
		# Minor revision: first 4 bits of profileMinorRevisionByte
		# (Shift bits 4 positions to right, logical shift not arithemetic shift!)
		profileMinorRevision=profileMinorRevisionByte >> 4
		
		# Bug fix revision: last 4 bits of profileMinorRevisionByte
		# (apply bit mask of 00001111 = 15)
		profileBugFixRevision=profileMinorRevisionByte & 15
		
		# Construct text string with profile version
		profileVersion="%s.%s.%s" % (profileMajorRevision, profileMinorRevision, profileBugFixRevision)
		self.addCharacteristic("profileVersion",profileVersion)
		
		# Bytes 10 and 11 are reserved an set to zero(ignored here)
		
		# Profile class (or device class)
		profileClass=self.boxContents[12:16]
		self.addCharacteristic("profileClass",profileClass)
		
		# Colour space
		colourSpace=self.boxContents[16:20]
		self.addCharacteristic("colourSpace",colourSpace)
		
		# Profile connection space 
		profileConnectionSpace=self.boxContents[20:24]
		self.addCharacteristic("profileConnectionSpace",profileConnectionSpace)
		
		# Date and time fields
		year=bc.bytesToUShortInt(self.boxContents[24:26])
		month=bc.bytesToUnsignedChar(self.boxContents[27:28])
		day=bc.bytesToUnsignedChar(self.boxContents[29:30])
		hour=bc.bytesToUnsignedChar(self.boxContents[31:32])
		minute=bc.bytesToUnsignedChar(self.boxContents[33:34])
		second=bc.bytesToUnsignedChar(self.boxContents[35:36])
		dateString="%d/%02d/%02d" % (year, month, day)
		timeString="%02d:%02d:%02d" % (hour, minute, second)
		dateTimeString="%s, %s" % (dateString, timeString)
		self.addCharacteristic("dateTimeString",dateTimeString)
		
		# Profile signature
		profileSignature=self.boxContents[36:40]
		self.addCharacteristic("profileSignature",profileSignature)
		
		# Primary platform
		primaryPlatform=self.boxContents[40:44]
		self.addCharacteristic("primaryPlatform",primaryPlatform)
		
		# Profile flags (bytes 44-47; only first byte read here as remaing bytes
		# don't contain any meaningful information)
		profileFlags=bc.bytesToUnsignedChar(self.boxContents[44:45])
				
		# Embedded profile (0 if not embedded, 1 if embedded in file)
		embeddedProfile=self._getBitValue(profileFlags,1)
		self.addCharacteristic("embeddedProfile",embeddedProfile)
		
		# Profile cannot be used independently from embedded colour data
		# (1 if true, 0 if false)
		profileCannotBeUsedIndependently=self._getBitValue(profileFlags,2)
		self.addCharacteristic("profileCannotBeUsedIndependently",profileCannotBeUsedIndependently)
		
		# Device manufacturer
		deviceManufacturer=self.boxContents[48:52]
		self.addCharacteristic("deviceManufacturer",deviceManufacturer)
		
		# Device model
		deviceModel=self.boxContents[52:56]
		self.addCharacteristic("deviceModel",deviceModel)
		
		# Device attributes (bytes 56-63; only first byte read here as remaing bytes
		# don't contain any meaningful information)
		deviceAttributes=bc.bytesToUnsignedChar(self.boxContents[56:57])
		
		# Transparency (1 = transparent; 0 = reflective)
		transparency=self._getBitValue(deviceAttributes,1)
		self.addCharacteristic("transparency",transparency)
		
		# Glossiness (1 = matte; 0 = glossy)
		glossiness=self._getBitValue(deviceAttributes,2)
		self.addCharacteristic("glossiness",glossiness)
		
		# Media polarity (1 = negative; 0 = positive)
		polarity=self._getBitValue(deviceAttributes,3)
		self.addCharacteristic("polarity",polarity)
		
		# Media colour (1 = black & white; 0 = colour)
		colour=self._getBitValue(deviceAttributes,4)
		self.addCharacteristic("colour",colour)
		
		# Rendering intent (bytes 64-67, only least-significant 2 bytes used)
		renderingIntent=bc.bytesToUShortInt(self.boxContents[66:68])
		self.addCharacteristic("renderingIntent",renderingIntent)
		
		# Profile connection space illuminants (X, Y, Z)
		connectionSpaceIlluminantX=round(bc.bytesToUInt(self.boxContents[68:72])/65536,4)
		self.addCharacteristic("connectionSpaceIlluminantX",connectionSpaceIlluminantX)
		
		connectionSpaceIlluminantY=round(bc.bytesToUInt(self.boxContents[72:76])/65536,4)
		self.addCharacteristic("connectionSpaceIlluminantY",connectionSpaceIlluminantY)
		
		connectionSpaceIlluminantZ=round(bc.bytesToUInt(self.boxContents[76:80])/65536,4)
		self.addCharacteristic("connectionSpaceIlluminantZ",connectionSpaceIlluminantZ)
		
		# Profile creator
		profileCreator=self.boxContents[80:84]
		self.addCharacteristic("profileCreator",profileCreator)
		
		# Profile ID (as hexadecimal string)
		profileID=bc.bytesToHex(self.boxContents[84:100])
		self.addCharacteristic("profileID",profileID)
				
		# Number of tags (tag count)
		tagCount=bc.bytesToUInt(self.boxContents[128:132])
		
		## TEST
		print("tagCount (icc): " +str(tagCount))
		## TEST
		
		# List of tag signatures, offsets and sizes
		# All local to this function; all property exports through "characteristics"
		# element object!
		tagSignatures=[]
		tagOffsets=[]
		tagSizes=[]
		
		# Offset of start of first tag
		tagStart=132
		for i in range(tagCount):
			# Extract tag signature (as binary string) for each entry
			tagSignature=self.boxContents[tagStart:tagStart+4]
			tagOffset=bc.bytesToUInt(self.boxContents[tagStart+4:tagStart+8])
			tagSize=bc.bytesToUInt(self.boxContents[tagStart+8:tagStart+12])
			self.addCharacteristic("tag",tagSignature)
			
			# Add to list
			tagSignatures.append(tagSignature)
			tagOffsets.append(tagOffset)
			tagSizes.append(tagSize)
			
			# Start offset of next tag
			tagStart +=12
		
		# Get profile description from profile description tag
		# The following code could go wrong in case tagSignatures doesn't
		# contain description fields (e.g. if profile is corrupted); try block
		# will capture any such errors.
		
		try:
			i = tagSignatures.index(b'desc')
			descStartOffset=tagOffsets[i]
			descSize=tagSizes[i]
			descTag=self.boxContents[descStartOffset:descStartOffset+descSize]
		
			# Note that description of this tag is missing from recent versions of
			# standard; following code based on older version:
			# ICC.1:2001-04 File Format for Color Profiles [REVISION of ICC.1:1998-09]
			# Length of description (including terminating null character)
			descriptionLength=bc.bytesToUInt(descTag[8:12])
		
			# Description as binary string (excluding terminating null char)
			description=descTag[12:12+descriptionLength-1]
		except:
			description=""
		self.addCharacteristic("description",description)
		
	def validate_paletteBox(self):
		# Palette box (ISO/IEC 15444-1 Section I.5.3.4)
		# Optional box that specifies a palette
		
		# Number of entries in the table (each field is 2 bytes)
		nE = bc.bytesToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("nE",nE)
		
		# nE within range 1-1024
		self.testFor("nEIsValid", 1 <= nE <= 1024)
		
		# Number of palette columns
		nPC=bc.bytesToUnsignedChar(self.boxContents[2:3])
		self.addCharacteristic("nPC",nPC)
		
		# nPC within range 1-255
		self.testFor("nPCIsValid", 1 <= nPC <= 255)
		
		# Following parameters are repeated for each column
		for i in range(nPC):

			# Bit depth of values created by column i
			b = bc.bytesToUnsignedChar(self.boxContents[3+i:4+i])
			
			# Most significant bit indicates whether palette column is signed (1)
			# or unsigned (0). Extracted by applying bit mask of 10000000 (=128)
			bSign = self._getBitValue(b, 1)
			self.addCharacteristic("bSign",bSign)

			# Remaining bits indicate (bit depth - 1). Extracted by applying bit mask of
			# 01111111 (=127)
			bDepth=(b & 127) + 1
			self.addCharacteristic("bDepth",bDepth)

			# Bits depth field is valid if bDepth in range 1-38 (including limits)
			self.testFor("bDepthIsValid", 1 <= bDepth <= 38)
			
			# If bDepth is not a multiple of 8 bits add padding bits
			# E.g. if bDepth is 10, bDepthPadded will be 16 bits, and
			# C value will be stored in low 10 bits of 16-bit field
			bDepthPadded=math.ceil(bDepth/8)*8
			bytesPadded=int(bDepthPadded/8)
			
			# Start offset of cP entries for this column
			offset=nPC+3+i*(nE*bytesPadded)
			
			for j in range(nE):
				# Get bytes for this entry
				cPAsBytes=self.boxContents[offset:offset+bytesPadded]
				
				# Convert to integer (cP could be *any* length so we cannot rely
				# on struct.unpack!)
				cP=bc.bytesToInteger(cPAsBytes)
				self.addCharacteristic("cP",cP)
				
				offset += bytesPadded

	def validate_componentMappingBox(self):
		# Component mapping box (ISO/IEC 15444-1 Section I.5.3.5)
		# This box defines how image channels are identified from actual components
		
		# Determine number of channels from box length
		numberOfChannels=int(len(self.boxContents)/4)
		
		offset=0

		# Loop through box contents and validate fields
		for i in range(numberOfChannels):
			
			# Component index
			cMP=bc.bytesToUShortInt(self.boxContents[offset:offset+2])
			self.addCharacteristic("cMP",cMP)

			# Allowed range: 0 - 16384
			self.testFor("cMPIsValid", 0 <= cMP <= 16384)

			# Specifies how channel is generated from codestream component
			mTyp = bc.bytesToUnsignedChar(self.boxContents[offset+2:offset+3])
			self.addCharacteristic("mTyp",mTyp)

			# Allowed range: 0 - 1
			self.testFor("mTypIsValid", 0 <= mTyp <= 1)

			# Palette component index
			pCol = bc.bytesToUnsignedChar(self.boxContents[offset+3:offset+4])
			self.addCharacteristic("pCol",pCol)

			# If mTyp equals 0, pCol should be 0 as well
			if mTyp ==0:
				pColIsValid = pCol ==0
			else:
				pColIsValid=True
			
			self.testFor("pColIsValid", pColIsValid)

			offset += 4			


	def validate_channelDefinitionBox(self):
		# Channel definition box (ISO/IEC 15444-1 Section I.5.3.6)
		# This box specifies the meaning of the samples in each channel in the image

		# Number of channel descriptions (short integer)
		n = bc.bytesToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("n",n)

		# Allowed range: 1 - 65535
		self.testFor("nIsValid", 1 <= n <= 65535)

		# Each channel description is made up of three 2-byte fields, so check
		# if size of box contents matches n
		boxLengthIsValid = len(self.boxContents) - 2 == n * 6
		self.testFor("boxLengthIsValid",boxLengthIsValid)

		# Loop through box contents and validate fields
		offset = 2
		for i in range(n):
			# Channel index
			cN=bc.bytesToUShortInt(self.boxContents[offset:offset+2])
			self.addCharacteristic("cN",cN)

			# Allowed range: 0 - 65535
			self.testFor("cNIsValid", 0 <= cN <= 65535)

			# Channel type
			cTyp = bc.bytesToUShortInt(self.boxContents[offset+2:offset+4])
			self.addCharacteristic("cTyp",cTyp)

			# Allowed range: 0 - 65535
			self.testFor("cTypIsValid", 0 <= cTyp <= 65535)

			# Channel Association
			cAssoc = bc.bytesToUShortInt(self.boxContents[offset+4:offset+6])
			self.addCharacteristic("cAssoc",cAssoc)

			# Allowed range: 0 - 65535
			self.testFor("cAssocIsValid", 0 <= cTyp <= 65535)

			offset += 6

	def validate_resolutionBox(self):
		# Resolution box (superbox)(ISO/IEC 15444-1 Section I.5.3.7
		# Specifies the capture and/or default display grid resolutions of
		# the image.

		# Marker tags/codes that identify all sub-boxes as hexadecimal strings
		tagCaptureResolutionBox=b'\x72\x65\x73\x63'
		tagDisplayResolutionBox=b'\x72\x65\x73\x64'

		# List for storing box type identifiers
		subBoxTypes=[]

		noBytes = len(self.boxContents)
		byteStart = 0
		bytesTotal = 0

		# Dummy value
		boxLengthValue = 10

		while byteStart < noBytes and boxLengthValue != 0:

			boxLengthValue, boxType, byteEnd, subBoxContents = self._getBox(byteStart, noBytes)

			# validate sub boxes
			resultBox, characteristicsBox = BoxValidator(boxType, subBoxContents).validate()

			byteStart = byteEnd

			# Add to list of box types
			subBoxTypes.append(boxType)

			# Add analysis results to test results tree
			self.tests.appendIfNotEmpty(resultBox)

			# Add extracted characteristics to characteristics tree
			self.characteristics.append(characteristicsBox)

		# This box contains either one Capture Resolution box, one Default Display
		# resolution box, or one of both
		self.testFor("containsCaptureOrDisplayResolutionBox", tagCaptureResolutionBox in subBoxTypes or tagDisplayResolutionBox in subBoxTypes)
		self.testFor("noMoreThanOneCaptureResolutionBox", subBoxTypes.count(tagCaptureResolutionBox) <= 1)
		self.testFor("noMoreThanOneDisplayResolutionBox", subBoxTypes.count(tagDisplayResolutionBox) <= 1)


	# Validator functions for boxes in Resolution box
	
	def validate_captureResolutionBox(self):
		# Capture  Resolution Box (ISO/IEC 15444-1 Section I.5.3.7.1)

		# Check box size, which should be 10 bytes
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
		vRescInPixelsPerMeter = (vRcN/vRcD) * (10**(vRcE))
		self.addCharacteristic("vRescInPixelsPerMeter", round(vRescInPixelsPerMeter,2))

		hRescInPixelsPerMeter = (hRcN/hRcD) * (10**(hRcE))
		self.addCharacteristic("hRescInPixelsPerMeter", round(hRescInPixelsPerMeter,2))

		vRescInPixelsPerInch = vRescInPixelsPerMeter * 25.4e-3
		self.addCharacteristic("vRescInPixelsPerInch", round(vRescInPixelsPerInch,2))

		hRescInPixelsPerInch = hRescInPixelsPerMeter * 25.4e-3
		self.addCharacteristic("hRescInPixelsPerInch", round(hRescInPixelsPerInch,2))

	def validate_displayResolutionBox(self):
		# Default Display  Resolution Box (ISO/IEC 15444-1 Section I.5.3.7.2)

		# Check box size, which should be 10 bytes
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
		self.addCharacteristic("hRdD",hRdD)
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
		vResdInPixelsPerMeter = (vRdN/vRdD) * (10**(vRdE))
		self.addCharacteristic("vResdInPixelsPerMeter", round(vResdInPixelsPerMeter,2))

		hResdInPixelsPerMeter = (hRdN/hRdD) * (10**(hRdE))
		self.addCharacteristic("hResdInPixelsPerMeter", round(hResdInPixelsPerMeter,2))

		vResdInPixelsPerInch = vResdInPixelsPerMeter * 25.4e-3
		self.addCharacteristic("vResdInPixelsPerInch", round(vResdInPixelsPerInch,2))

		hResdInPixelsPerInch = hResdInPixelsPerMeter * 25.4e-3
		self.addCharacteristic("hResdInPixelsPerInch", round(hResdInPixelsPerInch,2))

	def validate_contiguousCodestreamBox(self):
		# Contiguous codestream box (ISO/IEC 15444-1 Section I.5.4)
		
		# Codestream length
		length = len(self.boxContents)

		# Keep track of byte offsets
		offset = 0

		# Read first marker segment. This should be the start-of-codestream marker
		marker,segLength,segContents,offsetNext=self._getMarkerSegment(offset)

		# Marker should be start-of-codestream marker
		self.testFor("codestreamStartsWithSOCMarker", marker == b'\xff\x4f')
		offset = offsetNext

		# Read next marker segment. This should be the SIZ (image and tile size) marker
		marker,segLength,segContents,offsetNext=self._getMarkerSegment(offset)
		foundSIZMarker = (marker == b'\xff\x51')
		self.testFor("foundSIZMarker", foundSIZMarker)
		
		if foundSIZMarker:
			# Validate SIZ segment
			resultSIZ, characteristicsSIZ = BoxValidator(marker, segContents).validate() # validateSIZ(segContents)

			# Add analysis results to test results tree
			#self.tests.appendIfNotEmpty(resultSIZ)
			
			self.tests.appendIfNotEmpty(resultSIZ)
			
			# Add extracted characteristics to characteristics tree
			self.characteristics.append(characteristicsSIZ)

		offset = offsetNext

		# Loop through remaining marker segments in main header; first SOT (start of
		# tile-part marker) indicates end of main header. For now only validate
		# COD and QCD segments (which are both required) and extract contents of
		# COM segments. Any other marker segments are ignored.

		# Initial values for foundCODMarker and foundQCDMarker
		foundCODMarker=False
		foundQCDMarker=False

		while marker != b'\xff\x90' and offsetNext !=-9999:
			marker,segLength,segContents,offsetNext=self._getMarkerSegment(offset)
			
			## TEST
			print("Starting validation of " + str(marker))
			## TEST
			
			if marker == b'\xff\x52':
				# COD (coding style default) marker segment
				# COD is required
				foundCODMarker=True

				# Validate COD segment
				resultCOD, characteristicsCOD = BoxValidator(marker, segContents).validate() 
				# Add analysis results to test results tree
				self.tests.appendIfNotEmpty(resultCOD)
				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsCOD)
				offset = offsetNext
			elif marker == b'\xff\x5c':
				# QCD (quantization default) marker segment
				# QCD is required
				foundQCDMarker=True
				# Validate QCD segment
				resultQCD, characteristicsQCD = BoxValidator(marker, segContents).validate()
				# Add analysis results to test results tree
				self.tests.appendIfNotEmpty(resultQCD)
				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsQCD)
				offset=offsetNext
			elif marker == b'\xff\x64':
				# COM (codestream comment) marker segment
				# Validate QCD segment
				resultCOM, characteristicsCOM = BoxValidator(marker, segContents).validate() 
				# Add analysis results to test results tree
				self.tests.appendIfNotEmpty(resultCOM)
				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsCOM)
				offset = offsetNext
			elif marker==b'\xff\x90':
				# Start of tile (SOT) marker segment; don't update offset as this
				# will get us of out of this loop (for functional readability):
				offset = offset
				
			elif marker in[b'\xff\x53',b'\xff\x5d',b'\xff\x5e', \
					b'\xff\x5f',b'\xff\x55',b'\xff\x57',b'\xff\x60',b'\xff\x63']:
				# COC, QCC, RGN, POC, TLM, PLM ,PPM, CRG marker: ignore and
				# move on to next one
				# Bugfix 1.5.2: COC marker was previously missing (changed x52 to x53!)
				
				resultOther,characteristicsOther= BoxValidator(marker, segContents).validate()
				# Add analysis results to test results tree
				self.tests.appendIfNotEmpty(resultOther)
				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsOther)
				offset=offsetNext
			else:
				# Any other marker segment: ignore and move on to next one
				# Note that this should result in validation error as all
				# marker segments are covered above!!
				offset=offsetNext
		## TEST
		print("End of loop")
		## TEST

		# Add foundCODMarker / foundQCDMarker outcome to tests
		self.testFor("foundCODMarker",foundCODMarker)
		self.testFor("foundQCDMarker",foundQCDMarker)

		# Check if quantization parameters are consistent with levels (section A.6.4, eq A-4)
		# Note: this check may be performed at tile-part level as well (not included now)
		if foundCODMarker:
			lqcd = self.characteristics.findElementText('qcd/lqcd')
			qStyle = self.characteristics.findElementText('qcd/qStyle')
			levels = self.characteristics.findElementText('cod/levels')

		# Expected lqcd as a function of qStyle and levels
		if qStyle == 0:
			lqcdExpected = 4 + 3*levels
		elif qStyle == 1:
			lqcdExpected = 5
		elif qStyle == 2:
			lqcdExpected= 5 + 6*levels
		else:
			# Dummy value in case of non-legal value of qStyle
			lqcdExpected = -9999

		# lqcd should equal expected value
		self.testFor("quantizationConsistentWithLevels", lqcd == lqcdExpected)

		# Remainder of codestream is a sequence of tile parts, followed by one
		# end-of-codestream marker
				
		# Expected number of tiles (as calculated from info in SIZ marker)
		numberOfTilesExpected=self.characteristics.findElementText('siz/numberOfTiles')
		
		## TEST
		print("numberOfTilesExpected: " +str(numberOfTilesExpected))
		
		numberOfTilesExpected=min(numberOfTilesExpected,1000)
		
		## TEST
		
		# Create list with one entry for each tile
		tileIndices=[]
		
		# Dictionary that contains expected number of tile parts for each tile
		tilePartsPerTileExpected={}
		
		# Dictionary that contains found number of tile parts for each tile
		tilePartsPerTileFound={}
		
		# Create entry for each tile part and initialise value at 0
		for i in range(numberOfTilesExpected):
			tilePartsPerTileFound[i]=0
	
		# Create sub-elements to store tile-part characteristics and tests
		tilePartCharacteristics=ET.Element('tileParts')
		tilePartTests=ET.Element('tileParts')
		
		## TEST
		print("Entering tile-parts loop ..")
		## TEST

		while marker == b'\xff\x90':
			marker = self.boxContents[offset:offset+2]
			
			##TEST
			print("Offset: " + str(offset))
			##TEST

			if marker == b'\xff\x90':
				resultTilePart, characteristicsTilePart,offsetNext = BoxValidator(marker, self.boxContents, offset).validate()
				# Add analysis results to test results tree
				tilePartTests.appendIfNotEmpty(resultTilePart)
				
				# Add extracted characteristics to characteristics tree
				tilePartCharacteristics.append(characteristicsTilePart)
								
				tileIndex=characteristicsTilePart.findElementText('sot/isot')
				tilePartIndex=characteristicsTilePart.findElementText('sor/tpsot')
				tilePartsOfTile=characteristicsTilePart.findElementText('sot/tnsot')
				
				# Add tileIndex to tileIndices, if it doesn't exist already
				if tileIndex not in tileIndices:
					tileIndices.append(tileIndex)
							
				# Expected number of tile-parts for each tile to dictionary
				if tilePartsOfTile != 0:				
					tilePartsPerTileExpected[tileIndex]=tilePartsOfTile
				
				# Increase found number of tile-parts for this tile by 1 
				tilePartsPerTileFound[tileIndex]=tilePartsPerTileFound[tileIndex] +1

				if offsetNext != offset:
					offset = offsetNext
				else:
					# offsetNext same as offset: this happens if image only contains
					# one single tile-part (psot=0), in which case we break out of
					# this loop
					break

		# Length of tileIndices should equal numberOfTilesExpected
		self.testFor("foundExpectedNumberOfTiles", len(tileIndices) == numberOfTilesExpected)
				
		# Found numbers of tile	parts per tile should match expected	
		self.testFor("foundExpectedNumberOfTileParts", len(set(tilePartsPerTileExpected.items()) - set(tilePartsPerTileFound.items())) == 0)

		# Add tile-part characteristics and tests to characteristics / tests
		self.characteristics.append(tilePartCharacteristics)
		self.tests.appendIfNotEmpty(tilePartTests)

		# Last 2 bytes should be end-of-codestream marker
		self.testFor("foundEOCMarker", self.boxContents[length-2:length] == b'\xff\xd9')
		
	# Validator functions for codestream elements
	
	def validate_siz(self):
		# Image and tile size (SIZ) header fields (ISO/IEC 15444-1 Section A.5.1)

		# Length of main image header
		lsiz = bc.bytesToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lsiz", lsiz)

		# lsiz should be within range 41-49190
		self.testFor("lsizIsValid", 41 <= lsiz <= 49190)

		# Decoder capabilities
		rsiz = bc.bytesToUShortInt(self.boxContents[2:4])
		self.addCharacteristic("rsiz", rsiz)

		# rsiz should be either 0, 1 or 2
		self.testFor("rsizIsValid", rsiz in [0,1,2])

		# Width of reference grid
		xsiz = bc.bytesToUInt(self.boxContents[4:8])
		self.addCharacteristic("xsiz", xsiz)

		# xsiz should be within range 1 - (2**32)-1
		self.testFor("xsizIsValid", 1 <= xsiz <= (2**32)-1)

		# Heigth of reference grid
		ysiz = bc.bytesToUInt(self.boxContents[8:12])
		self.addCharacteristic("ysiz", ysiz)

		# ysiz should be within range 1 - (2**32)-1
		self.testFor("ysizIsValid", 1 <= ysiz <= (2**32)-1)

		# Horizontal offset from origin of reference grid to left of image area
		xOsiz = bc.bytesToUInt(self.boxContents[12:16])
		self.addCharacteristic("xOsiz", xOsiz)

		# xOsiz should be within range 0 - (2**32)-2
		self.testFor("xOsizIsValid", 0 <= xOsiz <= (2**32)-2)

		# Vertical offset from origin of reference grid to top of image area
		yOsiz = bc.bytesToUInt(self.boxContents[16:20])
		self.addCharacteristic("yOsiz", yOsiz)

		# yOsiz should be within range 0 - (2**32)-2
		self.testFor("yOsizIsValid", 0 <= yOsiz <= (2**32)-2)

		# Width of one reference tile with respect to the reference grid
		xTsiz = bc.bytesToUInt(self.boxContents[20:24])
		self.addCharacteristic("xTsiz", xTsiz)

		# xTsiz should be within range 1 - (2**32)- 1
		self.testFor("xTsizIsValid", 1 <= xTsiz <= (2**32)-1)

		# Height of one reference tile with respect to the reference grid
		yTsiz = bc.bytesToUInt(self.boxContents[24:28])
		self.addCharacteristic("yTsiz", yTsiz)

		# yTsiz should be within range 1 - (2**32)- 1
		self.testFor("yTsizIsValid", 1 <= yTsiz <= (2**32)-1)

		# Horizontal offset from origin of reference grid to left side of first tile
		xTOsiz = bc.bytesToUInt(self.boxContents[28:32])
		self.addCharacteristic("xTOsiz", xTOsiz)

		# xTOsiz should be within range 0 - (2**32)-2
		self.testFor("xTOsizIsValid", 0 <= xTOsiz <= (2**32)-2)

		# Vertical offset from origin of reference grid to top side of first tile
		yTOsiz = bc.bytesToUInt(self.boxContents[32:36])
		self.addCharacteristic("yTOsiz", yTOsiz)

		# yTOsiz should be within range 0 - (2**32)-2
		self.testFor("yTOsizIsValid", 0 <= yTOsiz <= (2**32)-2)
		
		# Number of tiles		
		if xTsiz != 0 and yTsiz != 0:
			# If block to prevent zero-division (which should not happen
			# for valid files)
			numberOfTilesX=math.ceil((xsiz-xOsiz)/xTsiz)
			numberOfTilesY=math.ceil((ysiz-yOsiz)/yTsiz)
			numberOfTiles=int(numberOfTilesX*numberOfTilesY)
		else:
			# Bogus value
			numberOfTiles=0
			
		self.addCharacteristic("numberOfTiles", numberOfTiles)

		# Number of components
		csiz = bc.bytesToUShortInt(self.boxContents[36:38])
		self.addCharacteristic("csiz", csiz)

		# Number of components should be in range 1 - 16384 (including limits)
		self.testFor("csizIsValid", 1 <= csiz <= 16384)

		# Check if codestream header size is consistent with csiz
		self.testFor("lsizConsistentWithCsiz", lsiz == 38 + (3*csiz))

		# Precision, depth horizontal/verical separation repeated for each component

		offset = 38

		for i in range(csiz):
			# ssiz (=bits per component)
			ssiz = bc.bytesToUnsignedChar(self.boxContents[offset:offset+1])

			# Most significant bit indicates whether components are signed (1)
			# or unsigned (0). Extracted by applying bit mask of 10000000 (=128)
			ssizSign = self._getBitValue(ssiz, 1)
			self.addCharacteristic("ssizSign", ssizSign)

			# Remaining bits indicate (bit depth - 1). Extracted by applying bit mask of
			# 01111111 (=127)
			ssizDepth = (ssiz & 127) + 1
			self.addCharacteristic("ssizDepth", ssizDepth)

			# ssiz field is valid if ssizDepth in range 1-38
			self.testFor("ssizIsValid", 1 <= ssizDepth <= 38)

			# Horizontal separation of sample of this component with respect
			# to reference grid
			xRsiz = bc.bytesToUnsignedChar(self.boxContents[offset+1:offset+2])
			self.addCharacteristic("xRsiz", xRsiz)

			# xRSiz valid if range 1-255
			self.testFor("xRsizIsValid", 1 <= xRsiz <= 255)

			# Vertical separation of sample of this component with respect
			# to reference grid
			yRsiz = bc.bytesToUnsignedChar(self.boxContents[offset+2:offset+3])
			self.addCharacteristic("yRsiz", yRsiz)

			# yRSiz valid if range 1-255
			self.testFor("yRsizIsValid", 1 <= yRsiz <= 255)

			offset += 3


	def validate_cod(self):
		# Coding style default (COD) header fields (ISO/IEC 15444-1 Section A.6.1)

		# Length of COD marker
		lcod=bc.bytesToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lcod",lcod)

		# lcod should be in range 12-45
		lcodIsValid=12 <= lcod  <= 45
		self.testFor("lcodIsValid",lcodIsValid)

		# Coding style
		scod=bc.bytesToUnsignedChar(self.boxContents[2:3])

		# scod contains 3 coding style parameters that follow from  its 3 least
		# significant bits

		# Last bit: 0 in case of default precincts (ppx/ppy=15), 1 in case precincts
		# are defined in sPcod parameter
		precincts=self._getBitValue(scod,8)
		self.addCharacteristic("precincts",precincts)

		# 7th bit: 0: no start of packet marker segments; 1: start of packet marker
		# segments may be used
		sop=self._getBitValue(scod,7)
		self.addCharacteristic("sop",sop)

		# 6th bit: 0: no end of packet marker segments; 1: end of packet marker
		# segments shall be used
		eph=self._getBitValue(scod, 6)
		self.addCharacteristic("eph",eph)

		# Coding parameters that are independent of components (grouped as sGCod)
		# in standard)

		sGcod=self.boxContents[3:7]

		# Progression order
		order=bc.bytesToUnsignedChar(sGcod[0:1])
		self.addCharacteristic("order",order)

		# Allowed values: 0 (LRCP), 1 (RLCP), 2 (RPCL), 3 (PCRL), 4(CPRL)
		orderIsValid=order in [0,1,2,3,4]
		self.testFor("orderIsValid",orderIsValid)

		# Number of layers
		layers=bc.bytesToUShortInt(sGcod[1:3])
		self.addCharacteristic("layers",layers)

		# layers should be in range 1-65535
		layersIsValid=1 <= layers  <= 65535
		self.testFor("layersIsValid",layersIsValid)

		# Multiple component transformation
		multipleComponentTransformation=bc.bytesToUnsignedChar(sGcod[3:4])
		self.addCharacteristic("multipleComponentTransformation",multipleComponentTransformation)

		# Value should be 0 (no transformation) or 1 (transformation on components
		# 0,1 and 2)
		multipleComponentTransformationIsValid=multipleComponentTransformation in [0,1]
		self.testFor("multipleComponentTransformationIsValid",multipleComponentTransformationIsValid)

		# Coding parameters that are component-specific (grouped as sPCod)
		# in standard)

		# Number of decomposition levels
		levels=bc.bytesToUnsignedChar(self.boxContents[7:8])
		self.addCharacteristic("levels",levels)

		# levels should be within range 0-32
		levelsIsValid=0 <= levels  <= 32
		self.testFor("levelsIsValid",levelsIsValid)

		# Check lcod is consistent with levels and precincts (eq A-2 )
		if precincts ==0:
			lcodExpected=12
		else:
			lcodExpected=13 + levels

		lcodConsistentWithLevelsPrecincts=lcod == lcodExpected
		self.testFor("lcodConsistentWithLevelsPrecincts",lcodConsistentWithLevelsPrecincts)

		# Code block width exponent (stored as offsets, add 2 to get actual value)
		codeBlockWidthExponent=bc.bytesToUnsignedChar(self.boxContents[8:9]) + 2
		self.addCharacteristic("codeBlockWidth",2**codeBlockWidthExponent)

		# Value within range 2-10
		codeBlockWidthExponentIsValid=2 <= codeBlockWidthExponent <= 10
		self.testFor("codeBlockWidthExponentIsValid",codeBlockWidthExponentIsValid)

		# Code block height exponent (stored as offsets, add 2 to get actual value)
		codeBlockHeightExponent=bc.bytesToUnsignedChar(self.boxContents[9:10]) + 2
		self.addCharacteristic("codeBlockHeight",2**codeBlockHeightExponent)

		# Value within range 2-10
		codeBlockHeightExponentIsValid=2 <= codeBlockHeightExponent <= 10
		self.testFor("codeBlockHeightExponentIsValid",codeBlockHeightExponentIsValid)

		# Sum of width + height exponents shouldn't exceed 12
		sumHeightWidthExponentIsValid=codeBlockWidthExponent+codeBlockHeightExponent <= 12
		self.testFor("sumHeightWidthExponentIsValid",sumHeightWidthExponentIsValid)

		# Code block style, contains 6 boolean switches
		codeBlockStyle=bc.bytesToUnsignedChar(self.boxContents[10:11])

		# Bit 8: selective arithmetic coding bypass
		codingBypass=self._getBitValue(codeBlockStyle,8)
		self.addCharacteristic("codingBypass",codingBypass)

		# Bit 7: reset of context probabilities on coding pass boundaries
		resetOnBoundaries=self._getBitValue(codeBlockStyle,7)
		self.addCharacteristic("resetOnBoundaries",resetOnBoundaries)

		# Bit 6: termination on each coding pass
		termOnEachPass=self._getBitValue(codeBlockStyle,6)
		self.addCharacteristic("termOnEachPass",termOnEachPass)

		# Bit 5: vertically causal context
		vertCausalContext=self._getBitValue(codeBlockStyle,5)
		self.addCharacteristic("vertCausalContext",vertCausalContext)

		# Bit 4: predictable termination
		predTermination=self._getBitValue(codeBlockStyle,4)
		self.addCharacteristic("predTermination",predTermination)

		# Bit 3: segmentation symbols are used
		segmentationSymbols=self._getBitValue(codeBlockStyle,3)
		self.addCharacteristic("segmentationSymbols",segmentationSymbols)

		# Wavelet transformation: 9-7 irreversible (0) or 5-3 reversible (1)
		transformation=bc.bytesToUnsignedChar(self.boxContents[11:12])
		self.addCharacteristic("transformation",transformation)

		transformationIsValid=transformation in [0,1]
		self.testFor("transformationIsValid",transformationIsValid)

		if precincts ==1:

			# Precinct size for each resolution level (=decomposition levels +1)
			# Order: low to high (lowest first)

			offset=12

			for i in range(levels+1):
				# Precinct byte
				precinctByte=bc.bytesToUnsignedChar(self.boxContents[offset:offset+1])

				# Precinct width exponent: least significant 4 bytes (apply bit mask)
				ppx=precinctByte & 15
				precinctSizeX=2**ppx
				self.addCharacteristic("precinctSizeX",precinctSizeX)

				# Precinct size of 1 (exponent 0) only allowed for lowest resolution level
				if i !=0:
					precinctSizeXIsValid=precinctSizeX >= 2
				else:
					precinctSizeXIsValid=True

				self.testFor("precinctSizeXIsValid",precinctSizeXIsValid)

				# Precinct height exponent: most significant 4 bytes (shift 4
				# to right and apply bit mask)
				ppy=(precinctByte >>4) & 15
				precinctSizeY=2**ppy
				self.addCharacteristic("precinctSizeY",precinctSizeY)

				# Precinct size of 1 (exponent 0) only allowed for lowest resolution level
				if i !=0:
					precinctSizeYIsValid=precinctSizeY >= 2
				else:
					precinctSizeYIsValid=True

				self.testFor("precinctSizeYIsValid",precinctSizeYIsValid)
				offset+=1


	def validate_qcd(self):
		# Quantization default  (QCD) header fields (ISO/IEC 15444-1 Section A.6.4)

		# Length of QCD marker
		lqcd=bc.bytesToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lqcd",lqcd)

		# lqcd should be in range 4-197
		lqcdIsValid=4 <= lqcd  <= 197
		self.testFor("lqcdIsValid",lqcdIsValid)

		# Note: lqcd should also be consistent with no. decomp.levels and sqcd!

		# Quantization style for all components
		sqcd=bc.bytesToUnsignedChar(self.boxContents[2:3])

		# sqcd contains 2 quantization parameters: style + no of guard bits

		# Style: least significant 5 bytes (apply bit mask)
		qStyle=sqcd & 31
		self.addCharacteristic("qStyle",qStyle)

		# Allowed values: 0 (no quantization), 1 (scalar derived), 2 (scalar expounded)
		qStyleIsValid=qStyle in [0,1,2]
		self.testFor("qStyleIsValid",qStyleIsValid)

		# Number of guard bits (3 most significant bits, shift + bit mask)
		guardBits=(sqcd >>5) &7
		self.addCharacteristic("guardBits",guardBits)

		# No. of decomposition levels --> cross-check with info from COD!!
		if qStyle==0:
			levels=int((lqcd-4)/3)
		elif qStyle==2:
			levels=int((lqcd-5)/6)

		offset=3

		if qStyle==0:
			for i in range(levels):
				spqcd=bc.bytesToUnsignedChar(self.boxContents[offset:offset+1])

				# 5 most significant bits -> exponent epsilon in Eq E-5
				epsilon=(spqcd >>3) &31
				self.addCharacteristic("epsilon",epsilon)

				offset +=1

		elif qStyle==2:
			for i in range(levels):
				spqcd=bc.bytesToUShortInt(self.boxContents[offset:offset+2])

				# 11 least significant bits: mu in Eq E-3
				mu=spqcd & 2047
				self.addCharacteristic("mu",mu)

				# 5 most significant bits: exponent epsilon in Eq E-3
				epsilon=(spqcd >> 11) & 31
				self.addCharacteristic("epsilon",epsilon)

				offset +=2

		else:
			spqcd=bc.bytesToUShortInt(self.boxContents[offset:offset+2])
			# 11 least significant bits: mu in Eq E-3
			mu=spqcd & 2047
			self.addCharacteristic("mu",mu)

			# 5 most significant bits: exponent epsilon in Eq E-3
			epsilon=(spqcd >> 11) & 31
			self.addCharacteristic("epsilon",epsilon)

		# Possible enhancement here: instead of reporting coefficients, report result
		# of corresponding equations (need Annex E from standard for that)


	def validate_com(self):
		# Codestream comment (COM) (ISO/IEC 15444-1 Section A.9.2)

		# Length of COM marker
		lcom=bc.bytesToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lcom",lcom)

		# lcom should be in range 5-65535
		lcomIsValid=5 <= lcom  <= 65535
		self.testFor("lcomIsValid",lcomIsValid)

		# Registration value of marker segment
		rcom=bc.bytesToUShortInt(self.boxContents[2:4])
		self.addCharacteristic("rcom",rcom)

		# rcom should be either 0 (binary values) or 1 (ISO/IEC 8859-15 (Latin) values)
		rcomIsValid=0 <= rcom  <= 1
		self.testFor("rcomIsValid",rcomIsValid)

		# Contents (multiples of Ccom)
		comment=self.boxContents[4:lcom]
		
		# If comment contains any device control characters (e.g. because of
		# file corruption), replace them  with printable character
		if bc.containsControlCharacters(comment):
			comment=bc.replaceControlCharacters(comment)
		
		# Decode to string with Latin encoding
		# Elementtree will deal with any non-ASCII characters by replacing
		# them with numeric entity references
		comment=comment.decode("iso-8859-15","strict")
									
		# Only add comment to characteristics if text (may contain binary data if rcom is 0!)
		if rcom == 1:
			self.addCharacteristic("comment",comment)

	def validate_sot(self):
		# Start of tile-part (SOT) marker segment (ISO/IEC 15444-1 Section A.4.2)

		# Note that unlike other marker validation functions this one returns a
		# third result, which is the total tile-part length (psot)!

		# Length of SOT marker
		lsot=bc.bytesToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lsot",lsot)

		# lsot should be 10
		lsotIsValid=lsot  == 10
		self.testFor("lsotIsValid",lsotIsValid)

		# Tile index
		isot=bc.bytesToUShortInt(self.boxContents[2:4])
		self.addCharacteristic("isot",isot)
		
		# Tile index should be in range 0-65534
		isotIsValid=0 <= isot <= 65534
		self.testFor("isotIsValid",isotIsValid)

		# Length of tile part (including this SOT)
		psot=bc.bytesToUInt(self.boxContents[4:8])
		self.addCharacteristic("psot",psot)

		# psot equals 0 (for last tile part) or greater than 14 (so range 1-13 is illegal)
		psotIsValid=not(1 <= psot <= 13)
		self.testFor("psotIsValid",psotIsValid)

		# Tile part index
		tpsot=bc.bytesToUnsignedChar(self.boxContents[8:9])
		self.addCharacteristic("tpsot",tpsot)

		# Should be in range 0-254
		tpsotIsValid=0 <= tpsot <= 254
		self.testFor("tpsotIsValid",tpsotIsValid)

		# Number of tile-parts of a tile in the codestream
		# Value of 0 indicates that number of tile-parts of tile in the codestream
		# is not defined in this header; otherwise value in range 1-255
		tnsot=bc.bytesToUnsignedChar(self.boxContents[9:10])
		self.addCharacteristic("tnsot",tnsot)
		self.returnOffset = psot
	
	# The following validator functions cover those marker segments that
	# are not yet supported, however including them has the effect that their
	# presence at least reported in jpylyzer's output.
	# Together these cover *all* the marker segments defined in ISO/IEC 15444-1,
	# apart from the SOP/EPH markers (not sure if I even *want* to see those reported
	# because there will be either lots of them or none at all!).
	
	def validate_coc(self):
		# Empty function
		pass
	
	def validate_rgn(self):
		# Empty function
		pass
	
	def validate_qcc(self):
		# Empty function
		pass
	
	def validate_poc(self):
		# Empty function
		pass
	
	def validate_tlm(self):
		# Empty function
		pass
	
	def validate_plm(self):
		# Empty function
		pass
	
	def validate_plt(self):
		# Empty function
		pass
	
	def validate_ppm(self):
		# Empty function
		pass
	
	def validate_ppt(self):
		# Empty function
		pass

	def validate_crg(self):
		# Empty function
		pass

	def validate_tilePart(self):
		# Analyse tile part that starts at offsetStart and perform cursory validation
		# Precondition: offsetStart points to SOT marker
		#
		# Limitations:
		# - COD, COC, QCD, QCC and RGN are markers only allowed in first tile-part
		#   of a tile; there is currently no check on this (may be added later)

		offset = self.startOffset
		
		# Read first marker segment, which is a  start of tile (SOT) marker segment
		marker,segLength,segContents,offsetNext=self._getMarkerSegment(offset)

		# Validate start of tile (SOT) marker segment
		# tilePartLength is value of psot, which is the total length of this tile
		# including the SOT marker. Note that psot may be 0 for last tile!
		resultSOT, characteristicsSOT, tilePartLength = BoxValidator('startOfTile', segContents).validate()
		
		# Add analysis results to test results tree
		self.tests.appendIfNotEmpty(resultSOT)

		# Add extracted characteristics to characteristics tree
		self.characteristics.append(characteristicsSOT)

		offset=offsetNext

		# Last marker in every tile-part should be a start of data marker
		foundSODMarker=False

		# Loop through remaining tile part marker segments; extract properties of
		# and validate COD, QCD and COM marker segments. Also test for presence of
		# SOD marker
		# NOTE 1: limited testing so far because of unavailability of test images with these
		# markers at tile-part level!!
		# NOTE 2: check for offsetNext !=-9999 was included after encountering image with corruption
		# that resulted in nonsensical lsot values, ultimatelty leading to an infinite loop. Shouldn't happen
		# anymore (although this may not be the most elegant way of handling this)

		while marker != b'\xff\x93' and offsetNext !=-9999:
			marker,segLength,segContents,offsetNext=self._getMarkerSegment(offset)
									
			if marker==b'\xff\x52':
				# COD (coding style default) marker segment
				
				# Validate COD segment
				resultCOD, characteristicsCOD = BoxValidator(marker, segContents).validate() 

				# Add analysis results to test results tree
				self.tests.appendIfNotEmpty(resultCOD)

				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsCOD)

				offset=offsetNext

			elif marker==b'\xff\x5c':
				# QCD (quantization default) marker segment
				
				# Validate QCD segment
				resultQCD, characteristicsQCD = BoxValidator(marker, segContents).validate()

				# Add analysis results to test results tree
				self.tests.appendIfNotEmpty(resultQCD)

				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsQCD)

				offset=offsetNext

			elif marker==b'\xff\x64':
				# COM (codestream comment) marker segment

				# Validate COM segment
				resultCOM, characteristicsCOM = BoxValidator(marker, segContents).validate()

				# Add analysis results to test results tree
				self.tests.appendIfNotEmpty(resultCOM)

				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsCOM)

				offset=offsetNext
					
			elif marker in[b'\xff\x53',b'\xff\x5d',b'\xff\x5e', \
					b'\xff\x5f',b'\xff\x61',b'\xff\x58']:
				# COC, QCC, RGN, POC, PPT or PLT marker: ignore and
				# move on to next one
				# Bugfix 1.5.2: COC marker was previously missing (changed x52 to x53!)
				
				resultOther,characteristicsOther= BoxValidator(marker, segContents).validate()
				# Add analysis results to test results tree
				self.tests.appendIfNotEmpty(resultOther)
				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsOther)
				offset=offsetNext

			else:
				# Unknown marker segment: ignore and move on to next one
				# NOTE: validation should also be a test for specific marker segments that are
				# not allowed here!!
				offset=offsetNext
			
				
		# Last marker segment should be start-of-data (SOD) marker
		self.testFor("foundSODMarker",marker == b'\xff\x93')
		
		# Bugfix 1.5.2: previous versions mistakenly assumed SOD at self.startOffset + 12!
		# Goes wrong if til part contains any optional markers. Fixed now!
					
		# Position of first byte in next tile
		offsetNextTilePart = self.startOffset + tilePartLength
				
		# Check if offsetNextTile really points to start of new tile or otherwise
		# EOC (useful for detecting within-codestream byte corruption)
		if tilePartLength != 0:
			# This will skip this test if tilePartLength equals 0, but that doesn't
			# matter since check for EOC is included elsewhere
			markerNextTilePart=self.boxContents[offsetNextTilePart:offsetNextTilePart+2]
			foundNextTilePartOrEOC=markerNextTilePart in [b'\xff\x90',b'\xff\xd9']
			self.testFor("foundNextTilePartOrEOC",foundNextTilePartOrEOC)

		self.returnOffset = offsetNextTilePart

	def validate_xmlBox(self):
		# XML Box (ISO/IEC 15444-1 Section I.7.1)
		
		data=self.boxContents
		
		# Data should be well-formed XML. Try to parse data to Element instance.
		
		try:
			dataAsElement= ET.fromstring(data)
			
			# Add data to characteristics tree
			self.characteristics.append(dataAsElement)
			
			# If no exception was raised data contains well-formed XML
			containsWellformedXML=True
		except:
			# If parse raised error this is not well-formed XML
			containsWellformedXML=False
		
		self.testFor("containsWellformedXML",containsWellformedXML)
	
	def validate_uuidBox(self):
		# UUID Box (ISO/IEC 15444-1 Section I.7.2)
		# For details on UUIDs see: http://tools.ietf.org/html/rfc4122.html
			
		# Box contains 16-byte identifier, followed by block of data.
		# Format of data is defined outside of the scope of JPEG 2000,
		# so in most cases there's not much to validate here. Exception:
		# if uuid = be7acfcb-97a9-42e8-9c71-999491e3afac this indicates
		# presence of XMP metadata
		
		boxLength=len(self.boxContents)
		
		# Check box size, which should be greater than 16 bytes
		self.testFor("boxLengthIsValid", boxLength > 16)
						
		# First 16 bytes contain UUID, convert to string of hex digits
		# in standard form
		id=str(uuid.UUID(bytes=self.boxContents[0:16]))
		
		if id=="be7acfcb-97a9-42e8-9c71-999491e3afac":
			# XMP packet
			data=self.boxContents[16:boxLength]
			
			# Data should be well-formed XML. Try to parse data to Element instance.
		
			try:
				dataAsElement= ET.fromstring(data)
			
				# Add data to characteristics tree
				self.characteristics.append(dataAsElement)
			
				# If no exception was raised data contains well-formed XML
				containsWellformedXML=True
			except:
				# If parse raised error this is not well-formed XML
				containsWellformedXML=False
		
			self.testFor("containsWellformedXML",containsWellformedXML)
		else:
			# Only add to UUID to characteristics tree	
			self.addCharacteristic("uuid",id)

	def validate_uuidInfoBox(self):
		# UUID Info box (superbox)(ISO/IEC 15444-1 Section I.7.3)
		# Provides additional information on vendor-specific UUIDs
		
		# NOTE: Untested at this stage due to lack of suitable test files!!!

		# Marker tags/codes that identify sub-boxes as hexadecimal strings
		tagListBox=b'\x75\x6c\x73\x74'
		tagURLBox=b'\x75\x72\x6c\x20'

		# List for storing box type identifiers
		subBoxTypes=[]

		noBytes = len(self.boxContents)
		byteStart = 0
		bytesTotal = 0

		# Dummy value
		boxLengthValue = 10

		while byteStart < noBytes and boxLengthValue != 0:

			boxLengthValue, boxType, byteEnd, subBoxContents = self._getBox(byteStart, noBytes)

			# validate sub boxes
			resultBox, characteristicsBox = BoxValidator(boxType, subBoxContents).validate()

			byteStart = byteEnd

			# Add to list of box types
			subBoxTypes.append(boxType)

			# Add analysis results to test results tree
			self.tests.appendIfNotEmpty(resultBox)

			# Add extracted characteristics to characteristics tree
			self.characteristics.append(characteristicsBox)

		# This box contains one UUID List box and one Data Entry URL box
		self.testFor("containsOneListBox", subBoxTypes.count(tagListBox) == 1)
		self.testFor("containsOneURLBox", subBoxTypes.count(tagURLBox) == 1)

	def validate_uuidListBox(self):
		# UUID List box (ISO/IEC 15444-1 Section I.7.3.1)
		# Contains a list of UUIDs
		
		# NOTE: Untested at this stage due to lack of suitable test files!!!
		
		# Number of UUIDs
		nU=bc.bytesToUShortInt(self.boxContents[0:2])
		self.addCharacteristic( "nU", nU)
		
		# Each UUID is 16 byte string, so check if total box length is valid
		self.testFor("boxLengthIsValid", len(self.boxContents) == nU*16 + 2)

		# Loop through all UUIDs				
		offset = 2
		for i in range(nU):
			id=str(uuid.UUID(bytes=self.boxContents[offset:offset+16]))
			self.addCharacteristic("uuid",id)
			offset+=16

	def validate_urlBox(self):
		# Data Entry URL box (ISO/IEC 15444-1 Section I.7.3.2)
		# Contains URL that can be used to obtain more information
		# about UUIDs in UUID List box
		
		# Version number (1 byte unsigned integer)
		version=bc.bytesToUnsignedChar(self.boxContents[0:1])
		self.addCharacteristic( "version", version)
		
		# Value of version shall be 0
		self.testFor("versionIsValid", version == 0)
		
		# Next item reserved to flag particular attributes of this box
		# (defined as 3-byte integer in standard, but since this is not
		# readily supported in Python we'll treat it as a bytes object)
		flag=self.boxContents[1:4]
		
		# All bytes should be 0
		self.testFor("flagIsValid", flag == b'\x00\x00\x00')
		
		# Location: this is the actual URL, encoded as a UTF-8 string
		loc=self.boxContents[4:len(self.boxContents)]
		
		# Loc is null terminated string, remove null character as this
		# cannot be represented as XML
		loc=loc.rstrip(b'\x00')
		
		# If loc contains any device control characters (e.g. because of
		# file corruption), replace them  with printable character
		if bc.containsControlCharacters(loc):
			loc=bc.replaceControlCharacters(loc)
		
		# Decode as UTF-8 
		try:
			loc=loc.decode("utf-8","strict")
			self.testFor("locIsUTF8", True)
		except UnicodeDecodeError:
			loc=""
			self.testFor("locIsUTF8", False)
		
		self.addCharacteristic( "loc", loc)

	def validate_JP2(self):
		# Top-level function for JP2 validation:
		#
		# 1. Parses all top-level boxes in JP2 byte object, and calls separate validator
		#	function for each of these
		# 2. Checks for presence of all required top-level boxes
		# 3. Checks if JP2 header properties are consistent with corresponding properties
		#	in codestream header

		# Marker tags/codes that identify all top level boxes as hexadecimal strings
		#(Correspond to "Box Type" values, see ISO/IEC 15444-1 Section I.4)
		tagSignatureBox=b'\x6a\x50\x20\x20'
		tagFileTypeBox=b'\x66\x74\x79\x70'
		tagJP2HeaderBox=b'\x6a\x70\x32\x68'
		tagContiguousCodestreamBox=b'\x6a\x70\x32\x63'

		# List for storing box type identifiers
		boxTypes=[]

		noBytes=len(self.boxContents)
		byteStart = 0
		bytesTotal=0

		# Dummy value
		boxLengthValue=10

		while byteStart < noBytes and boxLengthValue != 0:

			boxLengthValue, boxType, byteEnd, boxContents = self._getBox(byteStart, noBytes)
			
			## TEST
			print("Starting validation of " + boxType)
			## TEST

			# Validate current top level box
			resultBox,characteristicsBox = BoxValidator(boxType, boxContents).validate()

			byteStart = byteEnd

			# Add to list of box types
			boxTypes.append(boxType)

			# Add analysis results to test results tree
			self.tests.appendIfNotEmpty(resultBox)

			# Add extracted characteristics to characteristics tree
			self.characteristics.append(characteristicsBox)

		# Do all required top level boxes exist (ISO/IEC 15444-1 Section I.4)?
		containsSignatureBox=tagSignatureBox in  boxTypes
		containsFileTypeBox=tagFileTypeBox in  boxTypes
		containsJP2HeaderBox=tagJP2HeaderBox in  boxTypes
		containsContiguousCodestreamBox=tagContiguousCodestreamBox in  boxTypes

		self.testFor("containsSignatureBox",containsSignatureBox)
		self.testFor("containsFileTypeBox",containsFileTypeBox)
		self.testFor("containsJP2HeaderBox",containsJP2HeaderBox)
		self.testFor("containsContiguousCodestreamBox",containsContiguousCodestreamBox)

		# If iPR field in image header box equals 1, intellectual property box
		# should exist as well
		iPR = self.characteristics.findElementText('jp2HeaderBox/imageHeaderBox/iPR')

		if iPR == 1:
			containsIntellectualPropertyBox=tagIntellectualPropertyBox in  boxTypes
			self.testFor("containsIntellectualPropertyBox",containsIntellectualPropertyBox)

		# Is the first box a Signature Box (ISO/IEC 15444-1 Section I.5.1)?
		try:
			firstBoxIsSignatureBox=boxTypes[0] == tagSignatureBox
		except:
			firstBoxIsSignatureBox=False

		# Is the second box a File Type Box (ISO/IEC 15444-1 Section I.5.2)?
		try:
			secondBoxIsFileTypeBox=boxTypes[1] == tagFileTypeBox
		except:
			secondBoxIsFileTypeBox=False

		# JP2 Header Box: after File Type box, before (first) contiguous codestream box
		#(ISO/IEC 15444-1 Section I.5.3)?
		try:
			positionJP2HeaderBox=boxTypes.index(tagJP2HeaderBox)
			positionFirstContiguousCodestreamBox=boxTypes.index(tagContiguousCodestreamBox)

			if positionFirstContiguousCodestreamBox> positionJP2HeaderBox > 1:
				locationJP2HeaderBoxIsValid=True
			else:
				locationJP2HeaderBoxIsValid=False
		except:
			locationJP2HeaderBoxIsValid=False

		self.testFor("firstBoxIsSignatureBox",firstBoxIsSignatureBox)
		self.testFor("secondBoxIsFileTypeBox",secondBoxIsFileTypeBox)
		self.testFor("locationJP2HeaderBoxIsValid",locationJP2HeaderBoxIsValid)

		# Some boxes can have multiple instances, whereas for others only one
		# is allowed
		# --> Note: multiple Contiguous Codestream boxes are allowed, although conforming
		# readers only read first one. So maybe include a warning in case of multiple
		# codestreams?
		noMoreThanOneSignatureBox=boxTypes.count(tagSignatureBox) <= 1
		noMoreThanOneFileTypeBox=boxTypes.count(tagFileTypeBox) <= 1
		noMoreThanOneJP2HeaderBox=boxTypes.count(tagJP2HeaderBox) <= 1

		self.testFor("noMoreThanOneSignatureBox",noMoreThanOneSignatureBox)
		self.testFor("noMoreThanOneFileTypeBox",noMoreThanOneFileTypeBox)
		self.testFor("noMoreThanOneJP2HeaderBox",noMoreThanOneJP2HeaderBox)

		# Check if general image properties in Image Header Box are consistent with
		# corresponding values in codestream header.

		# JP2 image header and codestream SIZ header as element objects
		jp2ImageHeader=self.characteristics.find('jp2HeaderBox/imageHeaderBox')
		sizHeader=self.characteristics.find('contiguousCodestreamBox/siz')

		# Only proceed with tests if the above really exist (if this is not the case
		# the preceding tests will have already identified this file as not valid)

		# Note: do *NOT* use 'findtext' function to get values: if value equals 0
		# this returns an empty string, even though 'text' field really contains an
		# integer. Probably a bug in ET. Using 'find' + text property does work
		# as expected

		if jp2ImageHeader != None and sizHeader != None:

			# Height should be equal to ysiz -yOsiz

			height=jp2ImageHeader.findElementText('height')
			ysiz=sizHeader.findElementText('ysiz')
			yOsiz=sizHeader.findElementText('yOsiz')

			heightConsistentWithSIZ = height == (ysiz-yOsiz)
			self.testFor("heightConsistentWithSIZ", heightConsistentWithSIZ)

			# Width should be equal to xsiz - xOsiz
			width=jp2ImageHeader.findElementText('width')
			xsiz=sizHeader.findElementText('xsiz')
			xOsiz=sizHeader.findElementText('xOsiz')

			widthConsistentWithSIZ=width == (xsiz-xOsiz)
			self.testFor("widthConsistentWithSIZ", widthConsistentWithSIZ)

			# nC should be equal to csiz
			nC=jp2ImageHeader.findElementText('nC')
			csiz=sizHeader.findElementText('csiz')

			nCConsistentWithSIZ=nC == csiz
			self.testFor("nCConsistentWithSIZ", nCConsistentWithSIZ)

			# Bits per component: bPCSign should be equal to ssizSign,
			# and bPCDepth to ssizDepth
			#
			# There can be 2 situations here:
			#
			# 1. bPCSign and bPCDepth same for all components --> use values from image header
			# 2. bPCSign and bPCDepth vary across components --> use values from Bits Per
			#	Components box
			#
			# Situation 1 is the most common one. Situation 2 can be identified by a value
			# of 255 of bPC in the image header, which corresponds to  bPCSign = 1
			# and bPCDepth = 128 (these are both derived from bPC, which is not included
			# as a reportable here!)
			#
			# TO DO: test situation 2 using images with BPC box (cannot find any right now)

			bPCSign=jp2ImageHeader.findElementText('bPCSign')
			bPCDepth=jp2ImageHeader.findElementText('bPCDepth')

			if bPCSign == 1 and bPCDepth == 128:
				# Actual bPCSign / bPCDepth in Bits Per Components box
				# (situation 2 above)

				bpcBox=self.characteristics.find('jp2HeaderBox/bitsPerComponentBox')

				# All occurrences of bPCSign box to list. If bpcBox is 'noneType'
				# (e.g. due to some weird corruption of the file) this will result in
				# an empty list, so nothing really bad will happen ..
				bPCSignValues=bpcBox.findAllText('bPCSign')

				# All occurrences of bPCDepth to list
				bPCDepthValues=bpcBox.findAllText('bPCDepth')

			else:
				# These are the actual values (situation 1 above)

				# Create list of bPCSign values (i.e. duplicate fixed
				# value for each component)
				bPCSignValues=[]

				for i in range(nC):
					bPCSignValues.append(bPCSign)

				# Create list of bPCDepth values(i.e. duplicate fixed
				# value for each component)
				bPCDepthValues=[]

				for i in range(nC):
					bPCDepthValues.append(bPCDepth)

			# All occurrences of ssizSign to list
			ssizSignValues=sizHeader.findAllText('ssizSign')

			# All occurrences of ssizDepth to list
			ssizDepthValues=sizHeader.findAllText('ssizDepth')

			# bPCSignValues should be equal to ssizSignValues
			bPCSignConsistentWithSIZ=bPCSignValues == ssizSignValues
			self.testFor("bPCSignConsistentWithSIZ", bPCSignConsistentWithSIZ)

			# bPCDepthValues should be equal to ssizDepthValues
			bPCDepthConsistentWithSIZ=bPCDepthValues == ssizDepthValues
			self.testFor("bPCDepthConsistentWithSIZ", bPCDepthConsistentWithSIZ)

			# Calculate compression ratio of this image
			compressionRatio=self._calculateCompressionRatio(noBytes,bPCDepthValues,height,width)
			compressionRatio=round(compressionRatio,2)
			self.addCharacteristic("compressionRatio",compressionRatio)

		# Valid JP2 only if all tests returned True
		self.isValid = self._isValid()
