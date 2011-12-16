import struct
import warnings
import xml.etree.ElementTree as ET

def findElementText(element,match):

	# Replacement for ET's 'findtext' function, which has a bug
	# that will return empty string if text field contains integer with
	# value of zero (0)
	#
	# If there is no match, return None

	elt=element.find(match)

	if elt != None:
		result=elt.text
	else:
		result=None

	return(result)

def strToULongLong(str):
	# Unpack  8 byte string to unsigned long long integer, assuming big-endian
	# byte order. Return -9999 if unpack raised an error
	# (e.g. due to zero-length input string)

	# Set byte order to big-endian
	bOrder=">"

	# Format character for unsigned long long integer
	formatCharacter="Q"

	# Format string for unpack
	formatStr=bOrder+formatCharacter

	try:
		result=struct.unpack(formatStr,str)[0]
	except:
		result=-9999

	return(result)

def strToUInt(str):
	# Unpack  4 byte string to unsigned integer, assuming big-endian
	# byte order. Return -9999 if unpack raised an error
	# (e.g. due to zero-length input string)

	# Set byte order to big-endian
	bOrder=">"

	# Format character for unsigned integer
	formatCharacter="I"

	# Format string for unpack
	formatStr=bOrder+formatCharacter

	try:
		result=struct.unpack(formatStr,str)[0]
	except:
		result=-9999

	return(result)

def strToUShortInt(str):
	# Unpack 2 byte string to unsigned short integer, assuming big-endian
	# byte order. Return -9999 if unpack raised an error
	# (e.g. due to zero-length input string)

	# Set byte order to big-endian
	bOrder=">"

	# Format character for unsigned short integer
	formatCharacter="H"

	# Format string for unpack
	formatStr=bOrder+formatCharacter

	try:
		result=struct.unpack(formatStr,str)[0]
	except:
		result=-9999

	return(result)

def strToUnsignedChar(str):
	# Unpack 1 byte string to unsigned character/integer, assuming big-endian
	# byte order. Return -9999 if unpack raised an error
	# (e.g. due to zero-length input string)

	# Set byte order to big-endian
	bOrder=">"

	# Format character for unsigned short integer
	formatCharacter="B"

	# Format string for unpack
	formatStr=bOrder+formatCharacter

	try:
		result=struct.unpack(formatStr,str)[0]
	except:
		result=-9999

	return(result)

def strToSignedChar(str):
	# Unpack 1 byte string to signed character/integer, assuming big-endian
	# byte order. Return -9999 if unpack raised an error
	# (e.g. due to zero-length input string)

	# Set byte order to big-endian
	bOrder=">"

	# Format character for signed short integer
	formatCharacter="b"

	# Format string for unpack
	formatStr=bOrder+formatCharacter

	try:
		result=struct.unpack(formatStr,str)[0]
	except:
		result=-9999

	return(result)

def strToText(str):
	# Unpack byte string to text string, assuming big-endian
	# byte order.

	# Using ASCII may be too restrictive for representing some codestream comments,
	# which use ISO/IES 8859-15 (Latin)
	# However using ASCII here at least keeps the detection of control characters relatively
	# simple. Maybe extend this later to UTF-8
	#
	# Possible improvement: include detection of char 129-255 in control character check
	# (using regular expressions). In that case try / except block can be dropped
	# Already spent way too much time on this now so do this later ...

	# Set encoding
	enc="ascii"

	# Set error mode
	errorMode="strict"

	# Check if string contain control characters, which are not allowed in XML
	# (Note: entities are no problem, as minidom will deal with those by itself)
	if containsControlCharacters(str)==True:
		# Return empty string
		result=""
	else:
		try:
			result=str.decode(encoding=enc,errors=errorMode)
		except:
			# We end up here if str is part of extended ASCII (or Latin) set (char 129-255)
			# Return empty string
			result=""

	return(result)

def containsControlCharacters(str):
	# Returns True if str contains control characters
	# Maybe rewrite using reg expressions

	controlChars={b'\x00',b'\x01',b'\x02',b'\x03',b'\x04',b'\x05',b'\x06',b'\x07', \
		b'\x08',b'\x0b',b'\x0c',b'\x0e',b'\x0f',b'\x10',b'\x11',b'\x12',b'\x13',b'\x14', \
		b'\x15',b'\x16',b'\x17',b'\x18',b'\x19',b'\x1a',b'\x1b',b'\x1c',b'\x1d',b'\x1e', \
		b'\x1f'}

	containsControlCharacters=False

	for c in controlChars:
		if c in str:
			containsControlCharacters=True

	return(containsControlCharacters)

def findAllText(element,match):

	# Searches element and returns list that contains 'Text' attribute
	# of all matching sub-elements. Returns empty list if element
	# does not exist

	try:
		tmp=element.findall(match)
	except:
		tmp=[]
	result=[]
	for i in range(len(tmp)):
		result.append(tmp[i].text)

	return(result)

def getBitValue(n, p):

	# get the bitvalue of denary (base 10) number n at the equivalent binary
	# position p (binary count starts at position 1 from the left)
	# Only works if n can be expressed as 8 bits !!!

	# Word length in bits
	wordLength=8

	# Shift = word length - p
	shift=wordLength-p

	return (n >> shift) & 1



def indexMultiMatch(list, value):
	# Search list for occurrences of 'value', and return list
	# of matching index positions in souurce list

	matchIndices=[]
	numberOfElements=len(list)

	for i in range(numberOfElements):

		if list[i]==value:
			matchIndices.append(i)

	return(matchIndices)

def listContainsConsecutiveNumbers(list):
	# Takes list and returns True if items are consecutive numbers,
	# and False otherwise

	containsConsecutiveNumbers=True

	numberOfElements=len(list)

	try:
		for i in range(1,numberOfElements):
			if list[i] - list[i-1] != 1:
				containsConsecutiveNumbers=False
	except:
		containsConsecutiveNumbers=False

	return(containsConsecutiveNumbers)

def listOccurrencesAreContiguous(list,value):
	# Returns True if occurrences of 'value' in list are contiguous, and
	# "False otherwise"

	# Create list with index values of all occurrences of 'value'
	indexValues=indexMultiMatch(list,value)

	# If index values are a sequence of consecutive numbers this means that
	# all occurrences of 'value' are contiguous
	occurrencesAreContiguous=listContainsConsecutiveNumbers(indexValues)

	return(occurrencesAreContiguous)

def calculateCompressionRatio(noBytes,bPCDepthValues,height,width):

	# Computes compression ratio
	# noBytes: size of compressed image in bytes
	# bPCDepthValues: list with bits per component for each component
	# height, width: image height, width

	# Total bits per pixel

	bitsPerPixel=0

	for i in range(len(bPCDepthValues)):
		bitsPerPixel += bPCDepthValues[i]

	bytesPerPixel=bitsPerPixel/8
	# Uncompressed image size
	sizeUncompressed=bytesPerPixel*height*width

	# Compression ratio
	if noBytes !=0:
		compressionRatio=sizeUncompressed/noBytes
	else:
		# Obviously something going wrong here ...
		compressionRatio=-9999

	return(compressionRatio)


def getBox(bytesData, byteStart, noBytes):

	# Parse JP2 box and return information on its
	# size, type and contents

	# Box headers

	# Box length (4 byte unsigned integer)
	boxLengthValue=strToUInt(bytesData[byteStart:byteStart+4])

	# Box type
	boxType=bytesData[byteStart+4:byteStart+8]

	# Start byte of box contents
	contentsStartOffset=8

	# Read extended box length if box length value equals 1
	# In that case contentsStartOffset should also be 16 (not 8!)
	# (See ISO/IEC 15444-1 Section I.4)
	if boxLengthValue == 1:
		boxLengthValue=strToULongLong(bytesData[byteStart+8:byteStart+16])

		contentsStartOffset=16

	# For the very last box in a file boxLengthValue may equal 0, so we need
	# to calculate actual value
	if boxLengthValue == 0:
		boxLengthValue=noBytes-byteStart

	# End byte for current box
	byteEnd=byteStart + boxLengthValue

	# Contents of this box as a byte object (i.e. 'DBox' in ISO/IEC 15444-1 Section I.4)
	boxContents=bytesData[byteStart+contentsStartOffset:byteEnd]

	return(boxLengthValue,boxType,byteEnd,boxContents)

def getMarkerSegment(data,offset):
	# Read marker segment that starts at offset and return marker, size,
	# contents and start offset of next marker
	# First 2 bytes: 16 bit marker
	marker = data[offset:offset+2]
	# Check if this is a delimiting marker segment
	if marker in [b'\xff\x4f',b'\xff\x93',b'\xff\xd9',b'\xff\x92']:
		# Zero-length markers: SOC, SOD, EOC, EPH
		length=0
	else:
		# Not a delimiting marker, so remainder contains some data
		length=strToUShortInt(data[offset+2:offset+4])
	# Contents of marker segment (excluding marker) to binary string
	contents=data[offset+2:offset + 2 +length]
	# Offset value start of next marker segment
	offsetNext=offset+length+2
	return(marker,length,contents,offsetNext)

def addElement(parent,tag,text):
	# Add child element to parent
	element=ET.SubElement(parent, tag)
	element.text=text



def validateTilePart(data,offsetStart):

	# Analyse tile part that starts at offsetStart and perform cursory validation
	# Precondition: offsetStart points to SOT marker
	#
	# Limitations:
	# - COD, COC, QCD, QCC and RGN are markers only allowed in first tile-part
	#   of a tile; there is currently no check on this (may be added later)

	# Test results to elementtree element
	tests=ET.Element('tilePart')

	# Characteristics to elementtree element
	characteristics=ET.Element('tilePart')

	offset=offsetStart

	# Read first marker segment, which is a  start of tile (SOT) marker segment
	marker,segLength,segContents,offsetNext=getMarkerSegment(data,offset)

	# Validate start of tile (SOT) marker segment
	# tilePartLength is value of psot, which is the total length of this tile
	# including the SOT marker. Note that psot may be 0 for last tile!
	resultSOT, characteristicsSOT, tilePartLength = BoxValidator('startOfTile', segContents).validate() #validateSOT(segContents)

	# Add analysis results to test results tree
	tests.append(resultSOT)

	# Add extracted characteristics to characteristics tree
	characteristics.append(characteristicsSOT)

	offset=offsetNext

	# Last marker in every tile-part should be a start of data marker
	foundSODMarker=False

	# Loop through remaining tile part marker segments; extract properties of
	# and validate COD, QCD and COM marker segments. Also test for presence of
	# SOD marker
	# NOTE: not tested yet because of unavailability of test images with these
	# markers at tile-part level!!

	while marker != b'\xff\x93':
		marker,segLength,segContents,offsetNext=getMarkerSegment(data,offset)

		if marker==b'\xff\x52':
			# COD (coding style default) marker segment

			# COD is required
			foundCODMarker=True

			# Validate COD segment
			resultCOD, characteristicsCOD = BoxValidator(marker, segContents).validate() # validateCOD(segContents)

			# Add analysis results to test results tree
			tests.append(resultCOD)

			# Add extracted characteristics to characteristics tree
			characteristics.append(characteristicsCOD)

			offset=offsetNext

		elif marker==b'\xff\x5c':
			# QCD (quantization default) marker segment

			# QCD is required
			foundQCDMarker=True

			# Validate QCD segment
			resultQCD, characteristicsQCD = BoxValidator(marker, segContents).validate() #validateQCD(segContents)

			# Add analysis results to test results tree
			tests.append(resultQCD)

			# Add extracted characteristics to characteristics tree
			characteristics.append(characteristicsQCD)

			offset=offsetNext

		elif marker==b'\xff\x64':
			# COM (codestream comment) marker segment

			# Validate QCD segment
			resultCOM, characteristicsCOM = BoxValidator(marker, segContents).validate() #b'\xff\x64'validateCOM(segContents)

			# Add analysis results to test results tree
			tests.append(resultCOM)

			# Add extracted characteristics to characteristics tree
			characteristics.append(characteristicsCOM)

			offset=offsetNext

		elif marker==b'\xff\x93':
			# SOT (start of data) marker segment: last tile-part marker
			foundSODMarker=True
			addElement(tests,"foundSODMarker",foundSODMarker)

		else:
			# Any other marker segment: ignore and move on to next one
			offset=offsetNext


	# Position of first byte in next tile
	offsetNextTilePart=offsetStart + tilePartLength

	# Check if offsetNextTile really points to start of new tile or otherwise
	# EOC (useful for detecting within-codestream byte corruption)
	if tilePartLength != 0:
		# This will skip this test if tilePartLength equals 0, but that doesn't
		# matter since check for EOC is included elsewhere
		markerNextTilePart=data[offsetNextTilePart:offsetNextTilePart+2]
		foundNextTilePartOrEOC=markerNextTilePart in [b'\xff\x90',b'\xff\xd9']
		addElement(tests,"foundNextTilePartOrEOC",foundNextTilePartOrEOC)

	return(tests,characteristics,offsetNextTilePart)



class BoxValidator:
	# Marker tags/codes that identify all sub-boxes as hexadecimal strings
	#(Correspond to "Box Type" values, see ISO/IEC 15444-1 Section I.4)
	typeMap = {
		b'\x6a\x70\x32\x69': "intellectualPropertyBox",
		b'\x78\x6d\x6c\x20': "xmlBox",
		b'\x75\x75\x69\x64': "UUIDBox",
		b'\x75\x69\x6e\x66': "UUIDInfoBox",
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
		b'\xff\x51': "siz",
		b'\xff\x52': "cod",
		b'\xff\x5c': "qcd",
		b'\xff\x64': "com",
		'icc': 'icc',
		'startOfTile': 'sot'
	}

	# Reverse access of typemap for quick lookup
	boxTagMap = dict((v,k) for k,v in typeMap.iteritems())

	# Map for byte values to be tested against
	controlledByteMap = {
		"validSignature": b'\x0d\x0a\x87\x0a',
		"validBrandValue": b'\x6a\x70\x32\x20',
		"requiredInCompatibilityList": b'\x6a\x70\x32\x20'
	}

	def __init__(self, bType, boxContents):
		if bType in self.typeMap:
			self.boxType = self.typeMap[bType]
		else:
			self.boxType = 'unknownBox'
		self.characteristics = ET.Element(self.boxType)
		self.tests = ET.Element(self.boxType)
		self.boxContents = boxContents
		self.returnOffset = None

	def validate(self):
		try:
			to_call = getattr(self, "validate_" + self.boxType)
		except AttributeError:
			warnings.warn("Method 'validate_" + self.boxType + "' not implemented")
		else:
			to_call()
		if self.returnOffset is None:
			return (self.tests, self.characteristics)
		else:
			return (self.tests, self.characteristics, self.returnOffset)

	# Add an element of value to element tree
	def addElement(self, parent,tag,text):
		element = ET.SubElement(parent, tag)
		element.text = text

	# Add testresult node to tests element tree
	def testFor(self, testType, testResult):
		self.addElement(self.tests, testType, testResult)

	# Add characteristic node to characteristics element tree
	def addCharacteristic(self, characteristic, charValue):
		self.addElement(self.characteristics, characteristic, charValue)

	# Validations for boxes
	def validate_unknownBox(self):
		warnings.warn("No validation for unknown box")

	def validate_signatureBox(self):
		# Check box size, which should be 4 bytes
		self.testFor("boxLengthIsValid", len(self.boxContents) == 4)
		# Signature (*not* added to characteristics output, because it contains non-printable characters)
		self.testFor("signatureIsValid", self.boxContents[0:4] == self.controlledByteMap['validSignature'])

	def validate_fileTypeBox(self):
		# Determine number of compatibility fields from box length
		numberOfCompatibilityFields=(len(self.boxContents)-8)/4
		# This should never produce a decimal number (would indicate missing data)
		self.testFor("boxLengthIsValid", numberOfCompatibilityFields == int(numberOfCompatibilityFields))

		# This box contains (ISO/IEC 15444-1 Section I.5.2):
		# 1. Brand (4 bytes)
		br = self.boxContents[0:4]
		self.addCharacteristic( "br", br)

	# Is brand value valid?
		self.testFor("brandIsValid", br == self.controlledByteMap['validBrandValue'])

		# 2. Minor version (4 bytes)
		minV = strToUInt(self.boxContents[4:8])
		self.addCharacteristic("minV", minV)

		# Value should be 0
		# Note that conforming readers should continue to process the file
		# even if this field contains siome other value
		self.testFor("minorVersionIsValid", minV == 0)

		# 3. Compatibility list (one or more 4-byte fields)
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
		self.testFor("compatibilityListIsValid", self.controlledByteMap['requiredInCompatibilityList'] in cLList)


	# This is a superbox (ISO/IEC 15444-1 Section I.5.3)
	def validate_jp2HeaderBox(self):
		# List for storing box type identifiers
		subBoxTypes = []
		noBytes = len(self.boxContents)
		byteStart = 0
		bytesTotal = 0

		# Dummy value
		boxLengthValue = 10
		while byteStart < noBytes and boxLengthValue != 0:
			boxLengthValue, boxType, byteEnd, subBoxContents = getBox(self.boxContents,byteStart, noBytes)

			# Validate sub-boxes
			resultBox, characteristicsBox = BoxValidator(boxType, subBoxContents).validate()

			byteStart = byteEnd

			# Add to list of box types
			subBoxTypes.append(boxType)

			# Add analysis results to test results tree
			self.tests.append(resultBox)

			# Add extracted characteristics to characteristics tree
			self.characteristics.append(characteristicsBox)

		# Do all required header boxes exist?
		self.testFor("containsImageHeaderBox", self.boxTagMap['imageHeaderBox'] in subBoxTypes)
		self.testFor("containsColourSpecificationBox", self.boxTagMap['colourSpecificationBox'] in subBoxTypes)

		# If bPCSign equals 1 and bPCDepth equals 128 (equivalent to bPC field being
		# 255), this box should contain a Bits Per Components box
		sign = findElementText(self.characteristics,'imageHeaderBox/bPCSign')
		depth = findElementText(self.characteristics,'imageHeaderBox/bPCDepth')

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


	def validate_contiguousCodestreamBox(self):
		# Codestream length
		length = len(self.boxContents)

		# Keep track of byte offsets
		offset = 0

		# Read first marker segment. This should be the start-of-codestream marker
		marker,segLength,segContents,offsetNext=getMarkerSegment(self.boxContents,offset)

		# Marker should be start-of-codestream marker
		self.testFor("codestreamStartsWithSOCMarker", marker == b'\xff\x4f')
		offset = offsetNext

		# Read next marker segment. This should be the SIZ (image and tile size) marker
		marker,segLength,segContents,offsetNext=getMarkerSegment(self.boxContents,offset)
		foundSIZMarker = (marker == b'\xff\x51')
		self.testFor("foundSIZMarker", foundSIZMarker)

		if foundSIZMarker:
			# Validate SIZ segment
			resultSIZ, characteristicsSIZ = BoxValidator(marker, segContents).validate() # validateSIZ(segContents)

			# Add analysis results to test results tree
			self.tests.append(resultSIZ)

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

		while marker != b'\xff\x90':
			marker,segLength,segContents,offsetNext=getMarkerSegment(self.boxContents,offset)

			if marker == b'\xff\x52':
				# COD (coding style default) marker segment
				# COD is required
				foundCODMarker=True

				# Validate COD segment
				resultCOD, characteristicsCOD = BoxValidator(marker, segContents).validate() #validateCOD(segContents)
				# Add analysis results to test results tree
				self.tests.append(resultCOD)
				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsCOD)
				offset = offsetNext
			elif marker == b'\xff\x5c':
				# QCD (quantization default) marker segment
				# QCD is required
				foundQCDMarker=True
				# Validate QCD segment
				resultQCD, characteristicsQCD = BoxValidator(marker, segContents).validate()# validateQCD(segContents)
				# Add analysis results to test results tree
				self.tests.append(resultQCD)
				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsQCD)
				offset=offsetNext
			elif marker == b'\xff\x64':
				# COM (codestream comment) marker segment
				# Validate QCD segment
				resultCOM, characteristicsCOM = BoxValidator(marker, segContents).validate() #validateCOM(segContents)
				# Add analysis results to test results tree
				self.tests.append(resultCOM)
				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsCOM)
				offset = offsetNext
			elif marker==b'\xff\x90':
				# Start of tile (SOT) marker segment; don't update offset as this
				# will get of out of this loop (for functional readability):
				offset = offset
			else:
				# Any other marker segment: ignore and move on to next one
				offset=offsetNext

		# Add foundCODMarker / foundQCDMarker outcome to tests
		self.testFor("foundCODMarker",foundCODMarker)
		self.testFor("foundQCDMarker",foundQCDMarker)

		# Check if quantization parameters are consistent with levels (section A.6.4, eq A-4)
		# Note: this check may be performed at tile-part level as well (not included now)
		if foundCODMarker:
			lqcd = findElementText(self.characteristics,'qcd/lqcd')
			qStyle = findElementText(self.characteristics,'qcd/qStyle')
			levels = findElementText(self.characteristics,'cod/levels')

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

		# Create sub-elements to store tile-part characteristics and tests
		tilePartCharacteristics=ET.Element('tileParts')
		tilePartTests=ET.Element('tileParts')

		while marker == b'\xff\x90':
			marker = self.boxContents[offset:offset+2]

			if marker == b'\xff\x90':
				resultTilePart, characteristicsTilePart,offsetNext = validateTilePart(self.boxContents,offset)
				# Add analysis results to test results tree
				tilePartTests.append(resultTilePart)

				# Add extracted characteristics to characteristics tree
				tilePartCharacteristics.append(characteristicsTilePart)

				if offsetNext != offset:
					offset = offsetNext

		# Add tile-part characteristics and tests to characteristics / tests
		self.characteristics.append(tilePartCharacteristics)
		self.tests.append(tilePartTests)

		# Last 2 bytes should be end-of-codestream marker
		self.testFor("foundEOCMarker", self.boxContents[length-2:length] == b'\xff\xd9')


	# Validator functions for boxes in JP2 Header superbox
	def validate_imageHeaderBox(self):
	# This is a fixed-length box that contains generic image info.
	# (ISO/IEC 15444-1 Section I.5.3.1)
	# IMPORTANT: many of these parameters are redundant with header info
	# in codestream, so there should be a consistency check between these two!

	# Check box length (14 bytes, excluding box length/type fields)
		self.testFor("boxLengthIsValid", len(self.boxContents) == 14)

	# Image height and width (both as unsigned integers)
		height = strToUInt(self.boxContents[0:4])
		self.addCharacteristic("height", height)
		width = strToUInt(self.boxContents[4:8])
		self.addCharacteristic("width", width)

	# Height and width should be within range 1 - (2**32)-1
		self.testFor("heightIsValid", 1 <= height <= (2**32)-1)
		self.testFor("widthIsValid", 1 <= width <= (2**32)-1)
		# Number of components (unsigned short integer)
		nC = strToUShortInt(self.boxContents[8:10])
		self.addCharacteristic("nC", nC)
	# Number of components should be in range 1 - 16384 (including limits)
		self.testFor("nCIsValid", 1 <= nC <= 16384)

		# Bits per component (unsigned character)
		bPC = strToUnsignedChar(self.boxContents[10:11])
	# Most significant bit indicates whether components are signed (1)
	# or unsigned (0).
		bPCSign = getBitValue(bPC, 1)
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
		c = strToUnsignedChar(self.boxContents[11:12])
		self.addCharacteristic("c", c)
		# Value should always be 7
		self.testFor("cIsValid", c == 7)
	# Colourspace unknown field (unsigned character)
		unkC = strToUnsignedChar(self.boxContents[12:13])
		self.addCharacteristic("unkC", unkC)
	# Value should be 0 or 1
		self.testFor("unkCIsValid", 0 <= unkC <= 1)
	# Intellectual Property field (unsigned character)
		iPR = strToUnsignedChar(self.boxContents[13:14])
		self.addCharacteristic("iPR",iPR)
	# Value should be 0 or 1
		self.testFor("iPRIsValid", 0 <= iPR <= 1)


	def validate_bitsPerComponentBox(self):
		# Optional box that specifies bit depth of each component
		# (ISO/IEC 15444-1 Section I.5.3.2)

		# Number of bPC field (each field is 1 byte)
		numberOfBPFields = len(self.boxContents)

		# Validate all entries
		for i in range(numberOfBPFields):

			# Bits per component (unsigned character)
			bPC = strToUnsignedChar(self.boxContents[i:i+1])

			# Most significant bit indicates whether components are signed (1)
			# or unsigned (0). Extracted by applying bit mask of 10000000 (=128)
			bPCSign = getBitValue(bPC, 1)
			self.addCharacteristic("bPCSign",bPCSign)

			# Remaining bits indicate (bit depth - 1). Extracted by applying bit mask of
			# 01111111 (=127)
			bPCDepth=(bPC & 127) + 1
			self.addCharacteristic("bPCDepth",bPCDepth)

			# Bits per component field is valid if bPCDepth in range 1-38 (including limits)
			self.testFor("bPCIsValid", 1 <= bPCDepth <= 38)


	def validate_colourSpecificationBox(self):
		# This box defines one method for interpreting colourspace of decompressed
		# image data
		# (ISO/IEC 15444-1 Section I.5.3.3)

		# Length of this box
		length = len(self.boxContents)

		# Specification method (unsigned character)
		meth = strToUnsignedChar(self.boxContents[0:1])
		self.addCharacteristic("meth",meth)

		# Value should be 1 (enumerated colourspace) or 2 (restricted ICC profile)
		self.testFor("methIsValid", 1 <= meth <= 2)

	# Precedence (unsigned character)
		prec = strToUnsignedChar(self.boxContents[1:2])
		self.addCharacteristic("prec",prec)

	# Value shall be 0 (but conforming readers should ignore it)
		self.testFor("precIsValid", prec == 0)

	# Colourspace approximation (unsigned character)
		approx = strToUnsignedChar(self.boxContents[2:3])
		self.addCharacteristic("approx",approx)

	# Value shall be 0 (but conforming readers should ignore it)
		self.testFor("approxIsValid",approx == 0)

		# Colour space info: enumerated CS or embedded ICC profile,
		# depending on value of meth
		if meth == 1:
			# Enumerated colour space field (long integer)
			enumCS = strToUInt(self.boxContents[3:length])
			self.addCharacteristic("enumCS",enumCS)

			# (Note: this will also trap any cases where enumCS is more/less than 4
			# bytes, as strToUInt will return bogus negative value, which in turn is
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
			profileSize = findElementText(iccCharacteristics,'profileSize')
			self.testFor("iccSizeIsValid", profileSize == len(profile))

			# Profile class must be 'input' or 'display'
			profileClass = findElementText(iccCharacteristics,'profileClass')
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
			self.testFor("iccNoLUTBasedProfile", b'AToB0Tag' not in tagSignatures)

		elif meth == 3:
			# ICC profile embedded using "Any ICC" method. Belongs to Part 2 of the
			# standard (JPX), so if we get here by definition this is not valid JP2!
			profile = self.boxContents[3:length]

			# Extract ICC profile properties as element object
			tests, iccCharacteristics = BoxValidator('icc', profile).validate() #self.getICCCharacteristics(profile)
			self.characteristics.append(iccCharacteristics)


	def validate_channelDefinitionBox(self):
		# This box specifies the meaning of the samples in each channel in the image
		# (ISO/IEC 15444-1 Section I.5.3.6)
		# NOT TESTED YET BECAUSE OF UNAVAILABILITY OF SUITABLE TEST DATA!!

		# Number of channel descriptions (short integer)
		n = strToShortInt(self.boxContents[0:2])
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
			cN=strToShortInt(self.boxContents[offset:offset+2])
			self.addCharacteristic("cN",cN)

			# Allowed range: 0 - 65535
			self.testFor("cNIsValid", 0 <= cN <= 65535)

			# Channel type
			cTyp = strToShortInt(self.boxContents[offset+2:offset+4])
			self.addCharacteristic("cTyp",cTyp)

			# Allowed range: 0 - 65535
			self.testFor("cTypIsValid", 0 <= cTyp <= 65535)

			# Channel Association
			cAssoc = strToShortInt(self.boxContents[offset+4:offset+6])
			self.addCharacteristic("cAssoc",cAssoc)

			# Allowed range: 0 - 65535
			self.testFor("cAssocIsValid", 0 <= cTyp <= 65535)

			offset += 6

	def validate_resolutionBox(self):
		# Superbox that specifies the capture and default display grid resolutions of
		# the image. (ISO/IEC 15444-1 Section I.5.3.7

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

			boxLengthValue, boxType, byteEnd, subBoxContents = getBox(self.boxContents, byteStart, noBytes)

			# validate sub boxes
			resultBox, characteristicsBox = BoxValidator(boxType, subBoxContents).validate()

			byteStart = byteEnd

			# Add to list of box types
			subBoxTypes.append(boxType)

			# Add analysis results to test results tree
			self.tests.append(resultBox)

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
		vRcN = strToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("vRcN", vRcN)
		self.testFor("vRcNIsValid", 1 <= vRcN <= 65535)

		# Vertical grid resolution denominator (2 byte integer)
		vRcD = strToUShortInt(self.boxContents[2:4])
		self.addCharacteristic("vRcD", vRcD)
		self.testFor("vRcDIsValid", 1 <= vRcD <= 65535)

		# Horizontal grid resolution numerator (2 byte integer)
		hRcN = strToUShortInt(self.boxContents[4:6])
		self.addCharacteristic("hRcN", hRcN)
		self.testFor("hRcNIsValid", 1 <= hRcN <= 65535)

		# Horizontal grid resolution denominator (2 byte integer)
		hRcD = strToUShortInt(self.boxContents[6:8])
		self.addCharacteristic("hRcD", hRcD)
		self.testFor("hRcDIsValid", 1 <= hRcD <= 65535)

		# Vertical / horizontal grid resolution exponents:
		# values within range -128-127

		# Vertical grid resolution exponent (1 byte signed integer)
		vRcE = strToSignedChar(self.boxContents[8:9])
		self.addCharacteristic("vRcE", vRcE)
		self.testFor("vRcEIsValid", -128 <= vRcE <= 127)

		# Horizontal grid resolution exponent (1 byte signed integer)
		hRcE = strToSignedChar(self.boxContents[9:10])
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
		vRdN = strToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("vRdN", vRdN)
		self.testFor("vRdNIsValid", 1 <= vRdN <= 65535)

		# Vertical grid resolution denominator (2 byte integer)
		vRdD = strToUShortInt(self.boxContents[2:4])
		self.addCharacteristic("vRdD", vRdD)
		self.testFor("vRdDIsValid", 1 <= vRdD <= 65535)

		# Horizontal grid resolution numerator (2 byte integer)
		hRdN = strToUShortInt(self.boxContents[4:6])
		self.addCharacteristic("hRdN", hRdN)
		self.testFor("hRdNIsValid", 1 <= hRdN <= 65535)

		# Horizontal grid resolution denominator (2 byte integer)
		hRdD = strToUShortInt(self.boxContents[6:8])
		self.addCharacteristic("hRdD",hRdD)
		self.testFor("hRdDIsValid", 1 <= hRdD <= 65535)

		# Vertical / horizontal grid resolution exponents:
		# values within range -128-127

		# Vertical grid resolution exponent (1 byte signed integer)
		vRdE = strToSignedChar(self.boxContents[8:9])
		self.addCharacteristic("vRdE", vRdE)
		self.testFor("vRdEIsValid", -128 <= vRdE <= 127)

		# Horizontal grid resolution exponent (1 byte signed integer)
		hRdE = strToSignedChar(self.boxContents[9:10])
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


	# Validator functions for codestream elements
	def validate_siz(self):
		# Analyse SIZ segment of codestream header and validate it
		# (ISO/IEC 15444-1 Section A.5.1)

		# Length of main image header
		lsiz = strToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lsiz", lsiz)

		# lsiz should be within range 41-49190
		self.testFor("lsizIsValid", 41 <= lsiz <= 49190)

		# Decoder capabilities
		rsiz = strToUShortInt(self.boxContents[2:4])
		self.addCharacteristic("rsiz", rsiz)

		# rsiz should be either 0, 1 or 2
		self.testFor("rsizIsValid", rsiz in [0,1,2])

		# Width of reference grid
		xsiz = strToUInt(self.boxContents[4:8])
		self.addCharacteristic("xsiz", xsiz)

		# xsiz should be within range 1 - (2**32)-1
		self.testFor("xsizIsValid", 1 <= xsiz <= (2**32)-1)

		# Heigth of reference grid
		ysiz = strToUInt(self.boxContents[8:12])
		self.addCharacteristic("ysiz", ysiz)

		# ysiz should be within range 1 - (2**32)-1
		self.testFor("ysizIsValid", 1 <= ysiz <= (2**32)-1)

		# Horizontal offset from origin of reference grid to left of image area
		xOsiz = strToUInt(self.boxContents[12:16])
		self.addCharacteristic("xOsiz", xOsiz)

		# xOsiz should be within range 0 - (2**32)-2
		self.testFor("xOsizIsValid", 0 <= xOsiz <= (2**32)-2)

		# Vertical offset from origin of reference grid to top of image area
		yOsiz = strToUInt(self.boxContents[16:20])
		self.addCharacteristic("yOsiz", yOsiz)

		# yOsiz should be within range 0 - (2**32)-2
		self.testFor("yOsizIsValid", 0 <= yOsiz <= (2**32)-2)

		# Width of one reference tile with respect to the reference grid
		xTsiz = strToUInt(self.boxContents[20:24])
		self.addCharacteristic("xTsiz", xTsiz)

		# xTsiz should be within range 1 - (2**32)- 1
		self.testFor("xTsizIsValid", 1 <= xTsiz <= (2**32)-1)

		# Height of one reference tile with respect to the reference grid
		yTsiz = strToUInt(self.boxContents[24:28])
		self.addCharacteristic("yTsiz", yTsiz)

		# yTsiz should be within range 1 - (2**32)- 1
		self.testFor("yTsizIsValid", 1 <= yTsiz <= (2**32)-1)

		# Horizontal offset from origin of reference grid to left side of first tile
		xTOsiz = strToUInt(self.boxContents[28:32])
		self.addCharacteristic("xTOsiz", xTOsiz)

		# xTOsiz should be within range 0 - (2**32)-2
		self.testFor("xTOsizIsValid", 0 <= xTOsiz <= (2**32)-2)

		# Vertical offset from origin of reference grid to top side of first tile
		yTOsiz = strToUInt(self.boxContents[32:36])
		self.addCharacteristic("yTOsiz", yTOsiz)

		# yTOsiz should be within range 0 - (2**32)-2
		self.testFor("yTOsizIsValid", 0 <= yTOsiz <= (2**32)-2)

		# Number of components
		csiz = strToUShortInt(self.boxContents[36:38])
		self.addCharacteristic("csiz", csiz)

		# Number of components should be in range 1 - 16384 (including limits)
		self.testFor("csizIsValid", 1 <= csiz <= 16384)

		# Check if codestream header size is consistent with csiz
		self.testFor("lsizConsistentWithCsiz", lsiz == 38 + (3*csiz))

		# Precision, depth horizontal/verical separation repeated for each component

		# NOTE: for clarity maybe assign each component its own element (with properties
		# as sub elements)
		offset = 38

		for i in range(csiz):
			# ssiz (=bits per component)
			ssiz = strToUnsignedChar(self.boxContents[offset:offset+1])

			# Most significant bit indicates whether components are signed (1)
			# or unsigned (0). Extracted by applying bit mask of 10000000 (=128)
			ssizSign = getBitValue(ssiz, 1)
			self.addCharacteristic("ssizSign", ssizSign)

			# Remaining bits indicate (bit depth - 1). Extracted by applying bit mask of
			# 01111111 (=127)
			ssizDepth = (ssiz & 127) + 1
			self.addCharacteristic("ssizDepth", ssizDepth)

			# ssiz field is valid if ssizDepth in range 1-38
			self.testFor("ssizIsValid", 1 <= ssizDepth <= 38)

			# Horizontal separation of sample of this component with respect
			# to reference grid
			xRsiz = strToUnsignedChar(self.boxContents[offset+1:offset+2])
			self.addCharacteristic("xRsiz", xRsiz)

			# xRSiz valid if range 1-255
			self.testFor("xRsizIsValid", 1 <= xRsiz <= 255)

			# Vertical separation of sample of this component with respect
			# to reference grid
			yRsiz = strToUnsignedChar(self.boxContents[offset+2:offset+3])
			self.addCharacteristic("yRsiz", yRsiz)

			# yRSiz valid if range 1-255
			self.testFor("yRsizIsValid", 1 <= yRsiz <= 255)

			offset += 3


	def validate_cod(self):
		# Analyse coding style default header fields (COD) and validate
		# (ISO/IEC 15444-1 Section A.6.1)

		# Length of COD marker
		lcod=strToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lcod",lcod)

		# lcod should be in range 12-45
		lcodIsValid=12 <= lcod  <= 45
		self.testFor("lcodIsValid",lcodIsValid)

		# Coding style
		scod=strToUnsignedChar(self.boxContents[2:3])

		# scod contains 3 coding style parameters that follow from  its 3 least
		# significant bits

		# Last bit: 0 in case of default precincts (ppx/ppy=15), 1 in case precincts
		# are defined in sPcod parameter
		precincts=getBitValue(scod,8)
		self.addCharacteristic("precincts",precincts)

		# 7th bit: 0: no start of packet marker segments; 1: start of packet marker
		# segments may be used
		sop=getBitValue(scod,7)
		self.addCharacteristic("sop",sop)

		# 6th bit: 0: no end of packet marker segments; 1: end of packet marker
		# segments shall be used
		eph=getBitValue(scod, 6)
		self.addCharacteristic("eph",eph)

		# Coding parameters that are independent of components (grouped as sGCod)
		# in standard)

		sGcod=self.boxContents[3:7]

		# Progression order
		order=strToUnsignedChar(sGcod[0:1])
		self.addCharacteristic("order",order)

		# Allowed values: 0 (LRCP), 1 (RLCP), 2 (RPCL), 3 (PCRL), 4(CPRL)
		orderIsValid=order in [0,1,2,3,4]
		self.testFor("orderIsValid",orderIsValid)

		# Number of layers
		layers=strToUShortInt(sGcod[1:3])
		self.addCharacteristic("layers",layers)

		# layers should be in range 1-65535
		layersIsValid=1 <= layers  <= 65535
		self.testFor("layersIsValid",layersIsValid)

		# Multiple component transformation
		multipleComponentTransformation=strToUnsignedChar(sGcod[3:4])
		self.addCharacteristic("multipleComponentTransformation",multipleComponentTransformation)

		# Value should be 0 (no transformation) or 1 (transformation on components
		# 0,1 and 2)
		multipleComponentTransformationIsValid=multipleComponentTransformation in [0,1]
		self.testFor("multipleComponentTransformationIsValid",multipleComponentTransformationIsValid)

		# Coding parameters that are component-specific (grouped as sPCod)
		# in standard)

		# Number of decomposition levels
		levels=strToUnsignedChar(self.boxContents[7:8])
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
		codeBlockWidthExponent=strToUnsignedChar(self.boxContents[8:9]) + 2
		self.addCharacteristic("codeBlockWidth",2**codeBlockWidthExponent)

		# Value within range 2-10
		codeBlockWidthExponentIsValid=2 <= codeBlockWidthExponent <= 10
		self.testFor("codeBlockWidthExponentIsValid",codeBlockWidthExponentIsValid)

		# Code block height exponent (stored as offsets, add 2 to get actual value)
		codeBlockHeightExponent=strToUnsignedChar(self.boxContents[9:10]) + 2
		self.addCharacteristic("codeBlockHeight",2**codeBlockHeightExponent)

		# Value within range 2-10
		codeBlockHeightExponentIsValid=2 <= codeBlockHeightExponent <= 10
		self.testFor("codeBlockHeightExponentIsValid",codeBlockHeightExponentIsValid)

		# Sum of width + height exponents shouldn't exceed 12
		sumHeightWidthExponentIsValid=codeBlockWidthExponent+codeBlockHeightExponent <= 12
		self.testFor("sumHeightWidthExponentIsValid",sumHeightWidthExponentIsValid)

		# Code block style, contains 6 boolean switches
		codeBlockStyle=strToUnsignedChar(self.boxContents[10:11])

		# Bit 8: selective arithmetic coding bypass
		codingBypass=getBitValue(codeBlockStyle,8)
		self.addCharacteristic("codingBypass",codingBypass)

		# Bit 7: reset of context probabilities on coding pass boundaries
		resetOnBoundaries=getBitValue(codeBlockStyle,7)
		self.addCharacteristic("resetOnBoundaries",resetOnBoundaries)

		# Bit 6: termination on each coding pass
		termOnEachPass=getBitValue(codeBlockStyle,6)
		self.addCharacteristic("termOnEachPass",termOnEachPass)

		# Bit 5: vertically causal context
		vertCausalContext=getBitValue(codeBlockStyle,5)
		self.addCharacteristic("vertCausalContext",vertCausalContext)

		# Bit 4: predictable termination
		predTermination=getBitValue(codeBlockStyle,4)
		self.addCharacteristic("predTermination",predTermination)

		# Bit 3: segmentation symbols are used
		segmentationSymbols=getBitValue(codeBlockStyle,3)
		self.addCharacteristic("segmentationSymbols",segmentationSymbols)

		# Wavelet transformation: 9-7 irreversible (0) or 5-3 reversible (1)
		transformation=strToUnsignedChar(self.boxContents[11:12])
		self.addCharacteristic("transformation",transformation)

		transformationIsValid=transformation in [0,1]
		self.testFor("transformationIsValid",transformationIsValid)

		if precincts ==1:

			# Precinct size for each resolution level (=decomposition levels +1)
			# Order: low to high (lowest first)

			offset=12

			for i in range(levels+1):
				# Precinct byte
				precinctByte=strToUnsignedChar(self.boxContents[offset:offset+1])

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
		# Analyse quantization default header fields (QCD) and validate
		# (ISO/IEC 15444-1 Section A.6.4)

		# Length of QCD marker
		lqcd=strToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lqcd",lqcd)

		# lqcd should be in range 4-197
		lqcdIsValid=4 <= lqcd  <= 197
		self.testFor("lqcdIsValid",lqcdIsValid)

		# Note: lqcd should also be consistent with no. decomp.levels and sqcd!

		# Quantization style for all components
		sqcd=strToUnsignedChar(self.boxContents[2:3])

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
				spqcd=strToUnsignedChar(self.boxContents[offset:offset+1])

				# 5 most significant bits -> exponent epsilon in Eq E-5
				epsilon=(spqcd >>3) &31
				self.addCharacteristic("epsilon",epsilon)

				offset +=1

		elif qStyle==2:
			for i in range(levels):
				spqcd=strToUShortInt(self.boxContents[offset:offset+2])

				# 11 least significant bits: mu in Eq E-3
				mu=spqcd & 2047
				self.addCharacteristic("mu",mu)

				# 5 most significant bits: exponent epsilon in Eq E-3
				epsilon=(spqcd >> 11) & 31
				self.addCharacteristic("epsilon",epsilon)

				offset +=2

		else:
			spqcd=strToUShortInt(self.boxContents[offset:offset+2])
			# 11 least significant bits: mu in Eq E-3
			mu=spqcd & 2047
			self.addCharacteristic("mu",mu)

			# 5 most significant bits: exponent epsilon in Eq E-3
			epsilon=(spqcd >> 11) & 31
			self.addCharacteristic("epsilon",epsilon)

		# Possible enhancement here: instead of reporting coefficients, report result
		# of corresponding equations (need Annex E from standard for that)


	def validate_com(self):
		# Analyse codestream comment (COM) and validate
		# (ISO/IEC 15444-1 Section A.6.4)

		# Length of COM marker
		lcom=strToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lcom",lcom)

		# lcom should be in range 5-65535
		lcomIsValid=5 <= lcom  <= 65535
		self.testFor("lcomIsValid",lcomIsValid)

		# Registration value of marker segment
		rcom=strToUShortInt(self.boxContents[2:4])
		self.addCharacteristic("rcom",rcom)

		# rcom should be either 0 (binary values) or 1 (ISO/IEC 8859-15 (Latin) values)
		rcomIsValid=0 <= rcom  <= 1
		self.testFor("rcomIsValid",rcomIsValid)

		# Contents (multiples of Ccom)
		comment=self.boxContents[4:lcom]

		# Only add comment to characteristics if text (may contain binary data if rcom is 0!)
		if rcom == 1:
			self.addCharacteristic("comment",comment)


	# TODO refactor as validator
	def validate_icc(self):
		# Extracts characteristics (property-value pairs) of ICC profile
		# Note that although values are stored in  'text' property of sub-elements,
		# they may have a type other than 'text' (binary string, integers, lists)
		# This means that some post-processing (conversion to text) is needed to
		# write these property-value pairs to XML

		# Profile header properties (note: incomplete at this stage!)
		# Size in bytes
		profileSize=strToUInt(self.boxContents[0:4])
		self.addCharacteristic("profileSize",profileSize)
		# Preferred CMM type
		preferredCMMType=strToUInt(self.boxContents[4:8])
		self.addCharacteristic("preferredCMMType",preferredCMMType)
		# Profile version: major revision
		profileMajorRevision=strToUnsignedChar(self.boxContents[8:9])
		# Profile version: minor revision
		profileMinorRevisionByte=strToUnsignedChar(self.boxContents[9:10])
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
		# Profile class (or device class) (binary string)
		profileClass=self.boxContents[12:16]
		self.addCharacteristic("profileClass",profileClass)
		# Colour space (binary string)
		colourSpace=self.boxContents[16:20]
		self.addCharacteristic("colourSpace",colourSpace)
		# Profile connection space (binary string)
		profileConnectionSpace=self.boxContents[20:24]
		self.addCharacteristic("profileConnectionSpace",profileConnectionSpace)
		# Date and time fields
		year=strToUShortInt(self.boxContents[24:26])
		month=strToUnsignedChar(self.boxContents[27:28])
		day=strToUnsignedChar(self.boxContents[29:30])
		hour=strToUnsignedChar(self.boxContents[31:32])
		minute=strToUnsignedChar(self.boxContents[33:34])
		second=strToUnsignedChar(self.boxContents[35:36])
		dateString="%d/%02d/%02d" % (year, month, day)
		timeString="%02d:%02d:%02d" % (hour, minute, second)
		dateTimeString="%s, %s" % (dateString, timeString)
		self.addCharacteristic("dateTimeString",dateTimeString)
		# Profile signature (binary string)
		profileSignature=self.boxContents[36:40]
		self.addCharacteristic("profileSignature",profileSignature)
		# Primary platform (binary string)
		primaryPlatform=self.boxContents[40:44]
		self.addCharacteristic("primaryPlatform",primaryPlatform)
		# To do: add remaining header fields; maybe include check on Profile ID
		# field (MD5 checksum) to test integrity of profile.
		# Parse tag table
		# Number of tags (tag count)
		tagCount=strToUInt(self.boxContents[128:132])
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
			tagOffset=strToUInt(self.boxContents[tagStart+4:tagStart+8])
			tagSize=strToUInt(self.boxContents[tagStart+8:tagStart+12])
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
			descriptionLength=strToUInt(descTag[8:12])
			# Description as binary string (excluding terminating null char)
			description=descTag[12:12+descriptionLength-1]
		except:
			description=""
		self.addCharacteristic("description",description)

	def validate_sot(self):
		# Analyse start of tile-part (SOT) marker segment and validate
		# (ISO/IEC 15444-1 Section A.4.2)

		# Note that unlike other marker validation functions this one returns a
		# third result, which is the total tile-part length (psot)!

		# Length of SOT marker
		lsot=strToUShortInt(self.boxContents[0:2])
		self.addCharacteristic("lsot",lsot)

		# lcom should be 10
		lsotIsValid=lsot  == 10
		self.testFor("lsotIsValid",lsotIsValid)

		# Tile index
		isot=strToUShortInt(self.boxContents[2:4])
		self.addCharacteristic("isot",isot)

		# Tile index should be in range 0-65534
		isotIsValid=0 <= isot <= 65534
		self.testFor("isotIsValid",isotIsValid)

		# Length of tile part (including this SOT)
		psot=strToUInt(self.boxContents[4:8])
		self.addCharacteristic("psot",psot)

		# psot equals 0 (for last tile part) or greater than 14 (so range 1-13 is illegal)
		psotIsValid=not(1 <= psot <= 13)
		self.testFor("psotIsValid",psotIsValid)

		# Tile part index
		tpsot=strToUnsignedChar(self.boxContents[8:9])
		self.addCharacteristic("tpsot",tpsot)

		# Should be in range 0-254
		tpsotIsValid=0 <= tpsot <= 254
		self.testFor("tpsotIsValid",tpsotIsValid)

		# Number of tile-parts of a tile in the codestream
		# Value of 0 indicates that number of tile-parts of tile in the codestream
		# is not defined in this header; otherwise value in range 1-255
		tnsot=strToUnsignedChar(self.boxContents[9:10])
		self.addCharacteristic("tnsot",tnsot)
		self.returnOffset = psot
