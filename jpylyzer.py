#! /usr/bin/env python
#
#
#
# jpylyzer
# Requires: Python 2.7 OR Python 3.2 or better
#
# Copyright (C) 2011 Johan van der Knijff, Koninklijke Bibliotheek - National Library of the Netherlands
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
# ISSUES:
# 1. Using wildcards on the command line doesn't result in the expected
# behaviour under Linux! Workaround: wrap them in quotes, e.g:
#
#  jpylyzer.py *  -- only processes 1st encountered file!
#  jpylyzer.py "*" -- results in correct behaviour
#


import sys
import os
import time
import imp
import glob
import struct
import argparse
import warnings
import xml.etree.ElementTree as ET
from xml.dom import minidom


scriptPath,scriptName=os.path.split(sys.argv[0])

__version__= "14 December 2011"


def main_is_frozen():
	return (hasattr(sys, "frozen") or # new py2exe
			hasattr(sys, "importers") # old py2exe
			or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
	if main_is_frozen():
		return os.path.dirname(sys.executable)
	return os.path.dirname(sys.argv[0])

def printWarning(msg):
	msgString=("WARNING (%s):  %s\n") % (scriptName,msg)
	sys.stderr.write(msgString)

def readFileBytes(file):
	# Read file, return contents as a byte object

	# Open file
	f=open(file,"rb")

	# Put contents of file into a byte object.
	fileData=f.read()
	f.close()

	return(fileData)

def writeOutput(tree):
	# Write element tree with analysis results to stdout

	# Create pretty-printed version of tree
	treePrettified=prettify(tree)

	# Write to stdout
	sys.stdout.write(treePrettified)

def prettify(elem):
	# Return a pretty-printed XML string for the Element
	# Source: http://www.doughellmann.com/PyMOTW/xml/etree/ElementTree/create.html
	rough_string = ET.tostring(elem, 'ascii')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="  ")

def addElement(parent,tag,text):
	# Add child element to parent
	element=ET.SubElement(parent, tag)
	element.text=text

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


def generatePropertiesRemapTable():

	# Generates nested dictionary which is used to map 'raw' property values
	# (mostly integer values) to corresponding text descriptions

	# Master dictionary for mapping of text descriptions to enumerated values
	# Key: corresponds to parameter tag name
	# Value: sub-dictionary with mappings for all property values
	enumerationsMap={}

	# Sub-dictionaries for individual properties

	# Generic 0 = no, 1=yes mapping (used for various properties)
	yesNoMap={}
	yesNoMap[0]="no"
	yesNoMap[1]="yes"

	# Bits per component: sign (Image HeaderBox, Bits Per Component Box, SIZ header
	# in codestream)
	signMap={}
	signMap[0]="unsigned"
	signMap[1]="signed"

	# Compression type (Image Header Box)
	cMap={}
	cMap[7]="jpeg2000"

	# meth (Colour Specification Box)
	methMap={}
	methMap[1]="Enumerated"
	methMap[2]="Restricted ICC"
	methMap[3]="Any ICC"  # JPX only
	methMap[4]="Vendor Colour" # JPX only

	# enumCS (Colour Specification Box)
	enumCSMap={}
	enumCSMap[16]="sRGB"
	enumCSMap[17]="greyscale"
	enumCSMap[18]="sYCC"

	# Decoder capabilities, rsiz (Codestream, SIZ)
	rsizMap={}
	rsizMap[0]="ISO/IEC 15444-1" # Does this correspiond to Profile 2??
	rsizMap[1]="Profile 0"
	rsizMap[2]="Profile 1"

	# Progression order (Codestream, COD)
	orderMap={}
	orderMap[0]="LRCP"
	orderMap[1]="RLCP"
	orderMap[2]="RPCL"
	orderMap[3]="PCRL"
	orderMap[4]="CPRL"

	# Transformation type (Codestream, COD)
	transformationMap={}
	transformationMap[0]="9-7 irreversible"
	transformationMap[1]="5-3 reversible"

	# Add sub-dictionaries to master dictionary, using tag name as key
	enumerationsMap['unkC']=yesNoMap
	enumerationsMap['iPR']=yesNoMap
	enumerationsMap['precincts']=yesNoMap
	enumerationsMap['sop']=yesNoMap
	enumerationsMap['eph']=yesNoMap
	enumerationsMap['multipleComponentTransformation']=yesNoMap
	enumerationsMap['codingBypass']=yesNoMap
	enumerationsMap['resetOnBoundaries']=yesNoMap
	enumerationsMap['termOnEachPass']=yesNoMap
	enumerationsMap['vertCausalContext']=yesNoMap
	enumerationsMap['predTermination']=yesNoMap
	enumerationsMap['segmentationSymbols']=yesNoMap
	enumerationsMap['bPCSign']=signMap
	enumerationsMap['ssizSign']=signMap
	enumerationsMap['c']=cMap
	enumerationsMap['meth']=methMap
	enumerationsMap['enumCS']=enumCSMap
	enumerationsMap['order']=orderMap
	enumerationsMap['transformation']=transformationMap
	enumerationsMap['rsiz']=rsizMap

	return(enumerationsMap)

def elementTreeToPrintable(tree,remapTable):

	# Takes element tree object, and returns a modified version in which all
	# non-printable 'text' fields (which may contain numeric data or binary strings)
	# are replaced by printable strings
	#
	# Property values in original tree may be mapped to alternative (more user-friendly)
	# reportable values using a rempapTable, which is a nested dictionary.

	# Destination tree: copy of source
	treePrintable=tree

	for  elt in treePrintable.iter():

		# Text field of this element
		textIn=elt.text

		# Tag name
		tag=elt.tag

		# Step 1: replace property values by values defined in enumerationsMap,
		# if applicable

		try:
			# If tag is in enumerationsMap, replace property values
			parameterMap=remapTable[tag]

			try:
				# Map original property values to values in dictionary
				remappedValue=parameterMap[textIn]
			except KeyError:
				# If value doesn't match any key: use original value instead
				remappedValue=textIn

		except KeyError:
			# If tag doesn't match any key in enumerationsMap, use original value
			remappedValue=textIn

		# Step 2: convert all values to text strings

		if remappedValue != None:
			# Data type
			textType=type(remappedValue)

			# Convert text field, depending on type
			if textType == bytes:
				textOut=strToText(remappedValue)
			else:
				textOut=str(remappedValue)

			# Update output tree
			elt.text=textOut

	return(treePrintable)

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

def isValidJP2(tests):
	for  elt in tests.iter():

		if elt.text == False:
			# File didn't pass this test, so not valid
			return(False)
	return(True)

def getICCCharacteristics(profile):

	# Extracts characteristics (property-value pairs) of ICC profile
	# Note that although values are stored in  'text' property of sub-elements,
	# they may have a type other than 'text' (binary string, integers, lists)
	# This means that some post-processing (conversion to text) is needed to
	# write these property-value pairs to XML

	characteristics=ET.Element('icc')

	# Profile header properties (note: incomplete at this stage!)

	# Size in bytes
	profileSize=strToUInt(profile[0:4])
	addElement(characteristics,"profileSize",profileSize)

	# Preferred CMM type
	preferredCMMType=strToUInt(profile[4:8])
	addElement(characteristics,"preferredCMMType",preferredCMMType)

	# Profile version: major revision
	profileMajorRevision=strToUnsignedChar(profile[8:9])

	# Profile version: minor revision
	profileMinorRevisionByte=strToUnsignedChar(profile[9:10])

	# Minor revision: first 4 bits of profileMinorRevisionByte
	# (Shift bits 4 positions to right, logical shift not arithemetic shift!)
	profileMinorRevision=profileMinorRevisionByte >> 4

	# Bug fix revision: last 4 bits of profileMinorRevisionByte
	# (apply bit mask of 00001111 = 15)
	profileBugFixRevision=profileMinorRevisionByte & 15

	# Construct text string with profile version
	profileVersion="%s.%s.%s" % (profileMajorRevision, profileMinorRevision, profileBugFixRevision)
	addElement(characteristics,"profileVersion",profileVersion)

	# Bytes 10 and 11 are reserved an set to zero(ignored here)

	# Profile class (or device class) (binary string)
	profileClass=profile[12:16]
	addElement(characteristics,"profileClass",profileClass)

	# Colour space (binary string)
	colourSpace=profile[16:20]
	addElement(characteristics,"colourSpace",colourSpace)

	# Profile connection space (binary string)
	profileConnectionSpace=profile[20:24]
	addElement(characteristics,"profileConnectionSpace",profileConnectionSpace)

	# Date and time fields

	year=strToUShortInt(profile[24:26])
	month=strToUnsignedChar(profile[27:28])
	day=strToUnsignedChar(profile[29:30])
	hour=strToUnsignedChar(profile[31:32])
	minute=strToUnsignedChar(profile[33:34])
	second=strToUnsignedChar(profile[35:36])

	dateString="%d/%02d/%02d" % (year, month, day)
	timeString="%02d:%02d:%02d" % (hour, minute, second)
	dateTimeString="%s, %s" % (dateString, timeString)
	addElement(characteristics,"dateTimeString",dateTimeString)

	# Profile signature (binary string)
	profileSignature=profile[36:40]
	addElement(characteristics,"profileSignature",profileSignature)

	# Primary platform (binary string)
	primaryPlatform=profile[40:44]

	addElement(characteristics,"primaryPlatform",primaryPlatform)

	# To do: add remaining header fields; maybe include check on Profile ID
	# field (MD5 checksum) to test integrity of profile.

	# Parse tag table

	# Number of tags (tag count)
	tagCount=strToUInt(profile[128:132])

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
		tagSignature=profile[tagStart:tagStart+4]
		tagOffset=strToUInt(profile[tagStart+4:tagStart+8])
		tagSize=strToUInt(profile[tagStart+8:tagStart+12])

		addElement(characteristics,"tag",tagSignature)

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

		descTag=profile[descStartOffset:descStartOffset+descSize]

		# Note that description of this tag is missing from recent versions of
		# standard; following code based on older version:
		# ICC.1:2001-04 File Format for Color Profiles [REVISION of ICC.1:1998-09]

		# Length of description (including terminating null character)
		descriptionLength=strToUInt(descTag[8:12])

		# Description as binary string (excluding terminating null char)
		description=descTag[12:12+descriptionLength-1]

	except:
		description=""

	addElement(characteristics,"description",description)

	return(characteristics)


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
		b'\x6a\x70\x32\x63': "contiguousCodestreamBox"
	}

	# Reverse access of typemap for quick lookup
	boxTagMap = dict((v,k) for k,v in typeMap.iteritems())

	# Map for byte values to be tested against
	controlledByteMap = {
		"validSignature": b'\x0d\x0a\x87\x0a',
		"validBrandValue": b'\x6a\x70\x32\x20',
		"requiredInCompatibilityList": b'\x6a\x70\x32\x20'
	}

	# consts
	MAX_DIM = (2**32)-1

	def __init__(self, bType, boxContents):
		if bType in self.typeMap:
			self.boxType = self.typeMap[bType]
		else:
			self.boxType = 'unknownBox'
		self.characteristics = ET.Element(self.boxType)
		self.tests = ET.Element(self.boxType)
		self.boxContents = boxContents

	def validate(self):
		try:
			to_call = getattr(self, "validate_" + self.boxType)
		except AttributeError:
			warnings.warn("Method 'validate_" + self.boxType + "' not implemented")
		else:
			to_call()
		return (self.tests, self.characteristics)

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
			# Call functions for sub-boxes
			if boxType == self.boxTagMap['resolutionBox']:
				# Resolution box
				resultBox,characteristicsBox=validateResolutionBox(subBoxContents)
			else:
				# Unknown box (nothing to validate)
				resultBox,characteristicsBox=BoxValidator(boxType, subBoxContents).validate()

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
			resultSIZ, characteristicsSIZ=validateSIZ(segContents)

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
				resultCOD, characteristicsCOD=validateCOD(segContents)
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
				resultQCD, characteristicsQCD=validateQCD(segContents)
				# Add analysis results to test results tree
				self.tests.append(resultQCD)
				# Add extracted characteristics to characteristics tree
				self.characteristics.append(characteristicsQCD)
				offset=offsetNext
			elif marker == b'\xff\x64':
				# COM (codestream comment) marker segment
				# Validate QCD segment
				resultCOM, characteristicsCOM=validateCOM(segContents)
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
		self.testFor("heightIsValid", 1 <= height <= self.MAX_DIM)
		self.testFor("widthIsValid", 1 <= width <= self.MAX_DIM)
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
			iccCharacteristics=getICCCharacteristics(profile)
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
			iccCharacteristics = getICCCharacteristics(profile)
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
		addElement(tests,"boxLengthIsValid",boxLengthIsValid)

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

def validateResolutionBox(boxContents):
	# Superbox that specifies the capture and default display grid resolutions of
	# the image. (ISO/IEC 15444-1 Section I.5.3.7

	# Test results to elementtree element
	tests=ET.Element('resolutionBox')

	# Characteristics to elementtree element
	characteristics=ET.Element('resolutionBox')

	# Marker tags/codes that identify all sub-boxes as hexadecimal strings
	tagCaptureResolutionBox=b'\x72\x65\x73\x63'
	tagDisplayResolutionBox=b'\x72\x65\x73\x64'

	# List for storing box type identifiers
	subBoxTypes=[]

	noBytes=len(boxContents)
	byteStart = 0
	bytesTotal=0

	# Dummy value
	boxLengthValue=10

	while byteStart < noBytes and boxLengthValue != 0:

		boxLengthValue, boxType, byteEnd, subBoxContents = getBox(boxContents,byteStart, noBytes)

		# Call functions sub-boxes
		if boxType == tagCaptureResolutionBox:
			# Capture Resolution Box
			resultBox,characteristicsBox=validateCaptureResolutionBox(subBoxContents)
		elif boxType == tagDisplayResolutionBox:
			# Default Display Resolution Box
			resultBox,characteristicsBox=validateDisplayResolutionBox(subBoxContents)
		else:
			# Unknown box (nothing to validate)
			resultBox,characteristicsBox=BoxValidator(boxType, subBoxContents).validate()

		byteStart = byteEnd

		# Add to list of box types
		subBoxTypes.append(boxType)

		# Add analysis results to test results tree
		tests.append(resultBox)

		# Add extracted characteristics to characteristics tree
		characteristics.append(characteristicsBox)

	# This box contains either one Capture Resolution box, one Default Display
	# resolution box, or one of both

	if tagCaptureResolutionBox in subBoxTypes or tagDisplayResolutionBox in subBoxTypes:
		containsCaptureOrDisplayResolutionBox=True
	else:
		containsCaptureOrDisplayResolutionBox=False

	addElement(tests,"containsCaptureOrDisplayResolutionBox",containsCaptureOrDisplayResolutionBox)

	noMoreThanOneCaptureResolutionBox=subBoxTypes.count(tagCaptureResolutionBox) <= 1
	noMoreThanOneDisplayResolutionBox=subBoxTypes.count(tagDisplayResolutionBox) <= 1

	addElement(tests,"noMoreThanOneCaptureResolutionBox",noMoreThanOneCaptureResolutionBox)
	addElement(tests,"noMoreThanOneDisplayResolutionBox",noMoreThanOneDisplayResolutionBox)

	return(tests,characteristics)

# Validator functions for boxes in Resolution box

def validateCaptureResolutionBox(boxContents):

	# Capture  Resolution Box (ISO/IEC 15444-1 Section I.5.3.7.1)

	# Test results to elementtree element
	tests=ET.Element('captureResolutionBox')

	# Characteristics to elementtree element
	characteristics=ET.Element('captureResolutionBox')

	# Check box size, which should be 10 bytes
	boxLengthIsValid=len(boxContents) == 10
	addElement(tests,"boxLengthIsValid",boxLengthIsValid)

	# Vertical / horizontal grid resolution numerators and denominators:
	# all values within range 1-65535

	# Vertical grid resolution numerator (2 byte integer)
	vRcN=strToUShortInt(boxContents[0:2])
	addElement(characteristics,"vRcN",vRcN)
	vRcNIsValid=1 <= vRcN <= 65535
	addElement(tests,"vRcNIsValid",vRcNIsValid)

	# Vertical grid resolution denominator (2 byte integer)
	vRcD=strToUShortInt(boxContents[2:4])
	addElement(characteristics,"vRcD",vRcD)
	vRcDIsValid=1 <= vRcD <= 65535
	addElement(tests,"vRcDIsValid",vRcDIsValid)

	# Horizontal grid resolution numerator (2 byte integer)
	hRcN=strToUShortInt(boxContents[4:6])
	addElement(characteristics,"hRcN",hRcN)
	hRcNIsValid=1 <= hRcN <= 65535
	addElement(tests,"hRcNIsValid",hRcNIsValid)

	# Horizontal grid resolution denominator (2 byte integer)
	hRcD=strToUShortInt(boxContents[6:8])
	addElement(characteristics,"hRcD",hRcD)
	hRcDIsValid=1 <= hRcD <= 65535
	addElement(tests,"hRcDIsValid",hRcDIsValid)

	# Vertical / horizontal grid resolution exponents:
	# values within range -128-127

	# Vertical grid resolution exponent (1 byte signed integer)
	vRcE=strToSignedChar(boxContents[8:9])
	addElement(characteristics,"vRcE",vRcE)
	vRcEIsValid=-128 <= vRcE <= 127
	addElement(tests,"vRcEIsValid",vRcEIsValid)

	# Horizontal grid resolution exponent (1 byte signed integer)
	hRcE=strToSignedChar(boxContents[9:10])
	addElement(characteristics,"hRcE",hRcE)
	hRcEIsValid=-128 <= hRcE <= 127
	addElement(tests,"hRcEIsValid",hRcEIsValid)

	# Include vertical and horizontal resolution values in pixels per meter
	# and pixels per inch in output
	vRescInPixelsPerMeter=(vRcN/vRcD)*(10**(vRcE))
	addElement(characteristics,"vRescInPixelsPerMeter",round(vRescInPixelsPerMeter,2))

	hRescInPixelsPerMeter=(hRcN/hRcD)*(10**(hRcE))
	addElement(characteristics,"hRescInPixelsPerMeter",round(hRescInPixelsPerMeter,2))

	vRescInPixelsPerInch=vRescInPixelsPerMeter*25.4e-3
	addElement(characteristics,"vRescInPixelsPerInch",round(vRescInPixelsPerInch,2))

	hRescInPixelsPerInch=hRescInPixelsPerMeter*25.4e-3
	addElement(characteristics,"hRescInPixelsPerInch",round(hRescInPixelsPerInch,2))

	return(tests,characteristics)

def validateDisplayResolutionBox(boxContents):

	# Default Display  Resolution Box (ISO/IEC 15444-1 Section I.5.3.7.2)

	# Test results to elementtree element
	tests=ET.Element('displayResolutionBox')

	# Characteristics to elementtree element
	characteristics=ET.Element('displayResolutionBox')

	# Check box size, which should be 10 bytes
	boxLengthIsValid=len(boxContents) == 10
	addElement(tests,"boxLengthIsValid",boxLengthIsValid)

	# Vertical / horizontal grid resolution numerators and denominators:
	# all values within range 1-65535

	# Vertical grid resolution numerator (2 byte integer)
	vRdN=strToUShortInt(boxContents[0:2])
	addElement(characteristics,"vRdN",vRdN)
	vRdNIsValid=1 <= vRdN <= 65535
	addElement(tests,"vRdNIsValid",vRdNIsValid)

	# Vertical grid resolution denominator (2 byte integer)
	vRdD=strToUShortInt(boxContents[2:4])
	addElement(characteristics,"vRdD",vRdD)
	vRdDIsValid=1 <= vRdD <= 65535
	addElement(tests,"vRdDIsValid",vRdDIsValid)

	# Horizontal grid resolution numerator (2 byte integer)
	hRdN=strToUShortInt(boxContents[4:6])
	addElement(characteristics,"hRdN",hRdN)
	hRdNIsValid=1 <= hRdN <= 65535
	addElement(tests,"hRdNIsValid",hRdNIsValid)

	# Horizontal grid resolution denominator (2 byte integer)
	hRdD=strToUShortInt(boxContents[6:8])
	addElement(characteristics,"hRdD",hRdD)
	hRdDIsValid=1 <= hRdD <= 65535
	addElement(tests,"hRdDIsValid",hRdDIsValid)

	# Vertical / horizontal grid resolution exponents:
	# values within range -128-127

	# Vertical grid resolution exponent (1 byte signed integer)
	vRdE=strToSignedChar(boxContents[8:9])
	addElement(characteristics,"vRdE",vRdE)
	vRdEIsValid=-128 <= vRdE <= 127
	addElement(tests,"vRdEIsValid",vRdEIsValid)

	# Horizontal grid resolution exponent (1 byte signed integer)
	hRdE=strToSignedChar(boxContents[9:10])
	addElement(characteristics,"hRdE",hRdE)
	hRdEIsValid=-128 <= hRdE <= 127
	addElement(tests,"hRdEIsValid",hRdEIsValid)

	# Include vertical and horizontal resolution values in pixels per meter
	# and pixels per inch in output
	vResdInPixelsPerMeter=(vRdN/vRdD)*(10**(vRdE))
	addElement(characteristics,"vResdInPixelsPerMeter",round(vResdInPixelsPerMeter,2))

	hResdInPixelsPerMeter=(hRdN/hRdD)*(10**(hRdE))
	addElement(characteristics,"hResdInPixelsPerMeter",round(hResdInPixelsPerMeter,2))

	vResdInPixelsPerInch=vResdInPixelsPerMeter*25.4e-3
	addElement(characteristics,"vResdInPixelsPerInch",round(vResdInPixelsPerInch,2))

	hResdInPixelsPerInch=hResdInPixelsPerMeter*25.4e-3
	addElement(characteristics,"hResdInPixelsPerInch",round(hResdInPixelsPerInch,2))

	return(tests,characteristics)

# Validator functions for boxes in UUID Info superbox

def validateUUIDListBox(boxContents):

	# Test results to elementtree element
	tests=ET.Element('uuidListBox')

	# Characteristics to elementtree element
	characteristics=ET.Element('uuidListBox')

	return(tests,characteristics)

def validateURLBox(boxContents):

	# Test results to elementtree element
	tests=ET.Element('urlBox')

	# Characteristics to elementtree element
	characteristics=ET.Element('urlBox')

	return(tests,characteristics)

# Validator functions for codestream elements

def validateSIZ(data):

	# Analyse SIZ segment of codestream header and validate it
	# (ISO/IEC 15444-1 Section A.5.1)

	# Test results to elementtree element
	tests=ET.Element('siz')

	# Characteristics to elementtree element
	characteristics=ET.Element('siz')

	# Length of main image header
	lsiz=strToUShortInt(data[0:2])
	addElement(characteristics,"lsiz",lsiz)

	# lsiz should be within range 41-49190
	lsizIsValid=41 <= lsiz <= 49190
	addElement(tests,"lsizIsValid",lsizIsValid)

	# Decoder capabilities
	rsiz=strToUShortInt(data[2:4])
	addElement(characteristics,"rsiz",rsiz)

	# rsiz should be either 0, 1 or 2
	rsizIsValid=rsiz in [0,1,2]
	addElement(tests,"rsizIsValid",rsizIsValid)

	# Width of reference grid
	xsiz=strToUInt(data[4:8])
	addElement(characteristics,"xsiz",xsiz)

	# xsiz should be within range 1 - (2**32)-1
	xsizIsValid=1 <= xsiz <= (2**32)-1
	addElement(tests,"xsizIsValid",xsizIsValid)

	# Heigth of reference grid
	ysiz=strToUInt(data[8:12])
	addElement(characteristics,"ysiz",ysiz)

	# ysiz should be within range 1 - (2**32)-1
	ysizIsValid=1 <= ysiz <= (2**32)-1
	addElement(tests,"ysizIsValid",ysizIsValid)

	# Horizontal offset from origin of reference grid to left of image area
	xOsiz=strToUInt(data[12:16])
	addElement(characteristics,"xOsiz",xOsiz)

	# xOsiz should be within range 0 - (2**32)-2
	xOsizIsValid=0 <= xOsiz <= (2**32)-2
	addElement(tests,"xOsizIsValid",xOsizIsValid)

	# Vertical offset from origin of reference grid to top of image area
	yOsiz=strToUInt(data[16:20])
	addElement(characteristics,"yOsiz",yOsiz)

	# yOsiz should be within range 0 - (2**32)-2
	yOsizIsValid=0 <= yOsiz <= (2**32)-2
	addElement(tests,"yOsizIsValid",yOsizIsValid)

	# Width of one reference tile with respect to the reference grid
	xTsiz=strToUInt(data[20:24])
	addElement(characteristics,"xTsiz",xTsiz)

	# xTsiz should be within range 1 - (2**32)- 1
	xTsizIsValid=1 <= xTsiz <= (2**32)-1
	addElement(tests,"xTsizIsValid",xTsizIsValid)

	# Height of one reference tile with respect to the reference grid
	yTsiz=strToUInt(data[24:28])
	addElement(characteristics,"yTsiz",yTsiz)

	# yTsiz should be within range 1 - (2**32)- 1
	yTsizIsValid=1 <= yTsiz <= (2**32)-1
	addElement(tests,"yTsizIsValid",yTsizIsValid)

	# Horizontal offset from origin of reference grid to left side of first tile
	xTOsiz=strToUInt(data[28:32])
	addElement(characteristics,"xTOsiz",xTOsiz)

	# xTOsiz should be within range 0 - (2**32)-2
	xTOsizIsValid=0 <= xTOsiz <= (2**32)-2
	addElement(tests,"xTOsizIsValid",xTOsizIsValid)

	# Vertical offset from origin of reference grid to top side of first tile
	yTOsiz=strToUInt(data[32:36])
	addElement(characteristics,"yTOsiz",yTOsiz)

	# yTOsiz should be within range 0 - (2**32)-2
	yTOsizIsValid=0 <= yTOsiz <= (2**32)-2
	addElement(tests,"yTOsizIsValid",yTOsizIsValid)

	# Number of components
	csiz=strToUShortInt(data[36:38])
	addElement(characteristics,"csiz",csiz)

	# Number of components should be in range 1 - 16384 (including limits)
	csizIsValid=1 <= csiz <= 16384
	addElement(tests,"csizIsValid",csizIsValid)

	# Check if codestream header size is consistent with csiz
	lsizConsistentWithCsiz=lsiz == 38+(3*csiz)
	addElement(tests,"lsizConsistentWithCsiz",lsizConsistentWithCsiz)

	# Precision, depth horizontal/verical separation repeated for each component

	# NOTE: for clarity maybe assign each component its own element (with properties
	# as sub elements)

	offset=38

	for i in range(csiz):

		# ssiz (=bits per component)
		ssiz=strToUnsignedChar(data[offset:offset+1])

		# Most significant bit indicates whether components are signed (1)
		# or unsigned (0). Extracted by applying bit mask of 10000000 (=128)
		ssizSign=getBitValue(ssiz, 1)
		addElement(characteristics,"ssizSign",ssizSign)

		# Remaining bits indicate (bit depth - 1). Extracted by applying bit mask of
		# 01111111 (=127)
		ssizDepth=(ssiz & 127) + 1
		addElement(characteristics,"ssizDepth",ssizDepth)

		# ssiz field is valid if ssizDepth in range 1-38
		ssizIsValid=1 <= ssizDepth <= 38
		addElement(tests,"ssizIsValid",ssizIsValid)

		# Horizontal separation of sample of this component with respect
		# to reference grid
		xRsiz=strToUnsignedChar(data[offset+1:offset+2])
		addElement(characteristics,"xRsiz",xRsiz)

		# xRSiz valid if range 1-255
		xRsizIsValid=1 <= xRsiz <= 255
		addElement(tests,"xRsizIsValid",xRsizIsValid)

		# Vertical separation of sample of this component with respect
		# to reference grid
		yRsiz=strToUnsignedChar(data[offset+2:offset+3])
		addElement(characteristics,"yRsiz",yRsiz)

		# yRSiz valid if range 1-255
		yRsizIsValid=1 <= yRsiz <= 255
		addElement(tests,"yRsizIsValid",yRsizIsValid)

		offset += 3

	return(tests,characteristics)

def validateCOD(data):

	# Analyse coding style default header fields (COD) and validate
	# (ISO/IEC 15444-1 Section A.6.1)

	# Test results to elementtree element
	tests=ET.Element('cod')

	# Characteristics to elementtree element
	characteristics=ET.Element('cod')

	# Length of COD marker
	lcod=strToUShortInt(data[0:2])
	addElement(characteristics,"lcod",lcod)

	# lcod should be in range 12-45
	lcodIsValid=12 <= lcod  <= 45
	addElement(tests,"lcodIsValid",lcodIsValid)

	# Coding style
	scod=strToUnsignedChar(data[2:3])

	# scod contains 3 coding style parameters that follow from  its 3 least
	# significant bits

	# Last bit: 0 in case of default precincts (ppx/ppy=15), 1 in case precincts
	# are defined in sPcod parameter
	precincts=getBitValue(scod,8)
	addElement(characteristics,"precincts",precincts)

	# 7th bit: 0: no start of packet marker segments; 1: start of packet marker
	# segments may be used
	sop=getBitValue(scod,7)
	addElement(characteristics,"sop",sop)

	# 6th bit: 0: no end of packet marker segments; 1: end of packet marker
	# segments shall be used
	eph=getBitValue(scod, 6)
	addElement(characteristics,"eph",eph)

	# Coding parameters that are independent of components (grouped as sGCod)
	# in standard)

	sGcod=data[3:7]

	# Progression order
	order=strToUnsignedChar(sGcod[0:1])
	addElement(characteristics,"order",order)

	# Allowed values: 0 (LRCP), 1 (RLCP), 2 (RPCL), 3 (PCRL), 4(CPRL)
	orderIsValid=order in [0,1,2,3,4]
	addElement(tests,"orderIsValid",orderIsValid)

	# Number of layers
	layers=strToUShortInt(sGcod[1:3])
	addElement(characteristics,"layers",layers)

	# layers should be in range 1-65535
	layersIsValid=1 <= layers  <= 65535
	addElement(tests,"layersIsValid",layersIsValid)

	# Multiple component transformation
	multipleComponentTransformation=strToUnsignedChar(sGcod[3:4])
	addElement(characteristics,"multipleComponentTransformation",multipleComponentTransformation)

	# Value should be 0 (no transformation) or 1 (transformation on components
	# 0,1 and 2)
	multipleComponentTransformationIsValid=multipleComponentTransformation in [0,1]
	addElement(tests,"multipleComponentTransformationIsValid",multipleComponentTransformationIsValid)

	# Coding parameters that are component-specific (grouped as sPCod)
	# in standard)

	# Number of decomposition levels
	levels=strToUnsignedChar(data[7:8])
	addElement(characteristics,"levels",levels)

	# levels should be within range 0-32
	levelsIsValid=0 <= levels  <= 32
	addElement(tests,"levelsIsValid",levelsIsValid)

	# Check lcod is consistent with levels and precincts (eq A-2 )
	if precincts ==0:
		lcodExpected=12
	else:
		lcodExpected=13 + levels

	lcodConsistentWithLevelsPrecincts=lcod == lcodExpected
	addElement(tests,"lcodConsistentWithLevelsPrecincts",lcodConsistentWithLevelsPrecincts)

	# Code block width exponent (stored as offsets, add 2 to get actual value)
	codeBlockWidthExponent=strToUnsignedChar(data[8:9]) + 2
	addElement(characteristics,"codeBlockWidth",2**codeBlockWidthExponent)

	# Value within range 2-10
	codeBlockWidthExponentIsValid=2 <= codeBlockWidthExponent <= 10
	addElement(tests,"codeBlockWidthExponentIsValid",codeBlockWidthExponentIsValid)

	# Code block height exponent (stored as offsets, add 2 to get actual value)
	codeBlockHeightExponent=strToUnsignedChar(data[9:10]) + 2
	addElement(characteristics,"codeBlockHeight",2**codeBlockHeightExponent)

	# Value within range 2-10
	codeBlockHeightExponentIsValid=2 <= codeBlockHeightExponent <= 10
	addElement(tests,"codeBlockHeightExponentIsValid",codeBlockHeightExponentIsValid)

	# Sum of width + height exponents shouldn't exceed 12
	sumHeightWidthExponentIsValid=codeBlockWidthExponent+codeBlockHeightExponent <= 12
	addElement(tests,"sumHeightWidthExponentIsValid",sumHeightWidthExponentIsValid)

	# Code block style, contains 6 boolean switches
	codeBlockStyle=strToUnsignedChar(data[10:11])

	# Bit 8: selective arithmetic coding bypass
	codingBypass=getBitValue(codeBlockStyle,8)
	addElement(characteristics,"codingBypass",codingBypass)

	# Bit 7: reset of context probabilities on coding pass boundaries
	resetOnBoundaries=getBitValue(codeBlockStyle,7)
	addElement(characteristics,"resetOnBoundaries",resetOnBoundaries)

	# Bit 6: termination on each coding pass
	termOnEachPass=getBitValue(codeBlockStyle,6)
	addElement(characteristics,"termOnEachPass",termOnEachPass)

	# Bit 5: vertically causal context
	vertCausalContext=getBitValue(codeBlockStyle,5)
	addElement(characteristics,"vertCausalContext",vertCausalContext)

	# Bit 4: predictable termination
	predTermination=getBitValue(codeBlockStyle,4)
	addElement(characteristics,"predTermination",predTermination)

	# Bit 3: segmentation symbols are used
	segmentationSymbols=getBitValue(codeBlockStyle,3)
	addElement(characteristics,"segmentationSymbols",segmentationSymbols)

	# Wavelet transformation: 9-7 irreversible (0) or 5-3 reversible (1)
	transformation=strToUnsignedChar(data[11:12])
	addElement(characteristics,"transformation",transformation)

	transformationIsValid=transformation in [0,1]
	addElement(tests,"transformationIsValid",transformationIsValid)

	if precincts ==1:

		# Precinct size for each resolution level (=decomposition levels +1)
		# Order: low to high (lowest first)

		offset=12

		for i in range(levels+1):
			# Precinct byte
			precinctByte=strToUnsignedChar(data[offset:offset+1])

			# Precinct width exponent: least significant 4 bytes (apply bit mask)
			ppx=precinctByte & 15
			precinctSizeX=2**ppx
			addElement(characteristics,"precinctSizeX",precinctSizeX)

			# Precinct size of 1 (exponent 0) only allowed for lowest resolution level
			if i !=0:
				precinctSizeXIsValid=precinctSizeX >= 2
			else:
				precinctSizeXIsValid=True

			addElement(tests,"precinctSizeXIsValid",precinctSizeXIsValid)

			# Precinct height exponent: most significant 4 bytes (shift 4
			# to right and apply bit mask)
			ppy=(precinctByte >>4) & 15
			precinctSizeY=2**ppy
			addElement(characteristics,"precinctSizeY",precinctSizeY)

			# Precinct size of 1 (exponent 0) only allowed for lowest resolution level
			if i !=0:
				precinctSizeYIsValid=precinctSizeY >= 2
			else:
				precinctSizeYIsValid=True

			addElement(tests,"precinctSizeYIsValid",precinctSizeYIsValid)

			offset+=1

	return(tests,characteristics)

def validateQCD(data):

	# Analyse quantization default header fields (QCD) and validate
	# (ISO/IEC 15444-1 Section A.6.4)

	# Test results to elementtree element
	tests=ET.Element('qcd')

	# Characteristics to elementtree element
	characteristics=ET.Element('qcd')

	# Length of QCD marker
	lqcd=strToUShortInt(data[0:2])
	addElement(characteristics,"lqcd",lqcd)

	# lqcd should be in range 4-197
	lqcdIsValid=4 <= lqcd  <= 197
	addElement(tests,"lqcdIsValid",lqcdIsValid)

	# Note: lqcd should also be consistent with no. decomp.levels and sqcd!

	# Quantization style for all components
	sqcd=strToUnsignedChar(data[2:3])

	# sqcd contains 2 quantization parameters: style + no of guard bits

	# Style: least significant 5 bytes (apply bit mask)
	qStyle=sqcd & 31
	addElement(characteristics,"qStyle",qStyle)

	# Allowed values: 0 (no quantization), 1 (scalar derived), 2 (scalar expounded)
	qStyleIsValid=qStyle in [0,1,2]
	addElement(tests,"qStyleIsValid",qStyleIsValid)

	# Number of guard bits (3 most significant bits, shift + bit mask)
	guardBits=(sqcd >>5) &7
	addElement(characteristics,"guardBits",guardBits)

	# No. of decomposition levels --> cross-check with info from COD!!
	if qStyle==0:
		levels=int((lqcd-4)/3)
	elif qStyle==2:
		levels=int((lqcd-5)/6)

	offset=3

	if qStyle==0:
		for i in range(levels):
			spqcd=strToUnsignedChar(data[offset:offset+1])

			# 5 most significant bits -> exponent epsilon in Eq E-5
			epsilon=(spqcd >>3) &31
			addElement(characteristics,"epsilon",epsilon)

			offset +=1

	elif qStyle==2:
		for i in range(levels):
			spqcd=strToUShortInt(data[offset:offset+2])

			# 11 least significant bits: mu in Eq E-3
			mu=spqcd & 2047
			addElement(characteristics,"mu",mu)

			# 5 most significant bits: exponent epsilon in Eq E-3
			epsilon=(spqcd >> 11) & 31
			addElement(characteristics,"epsilon",epsilon)

			offset +=2

	else:
		spqcd=strToUShortInt(data[offset:offset+2])
		# 11 least significant bits: mu in Eq E-3
		mu=spqcd & 2047
		addElement(characteristics,"mu",mu)

		# 5 most significant bits: exponent epsilon in Eq E-3
		epsilon=(spqcd >> 11) & 31
		addElement(characteristics,"epsilon",epsilon)

	# Possible enhancement here: instead of reporting coefficients, report result
	# of corresponding equations (need Annex E from standard for that)

	return(tests,characteristics)

def validateCOM(data):

	# Analyse codestream comment (COM) and validate
	# (ISO/IEC 15444-1 Section A.6.4)

	# Test results to elementtree element
	tests=ET.Element('com')

	# Characteristics to elementtree element
	characteristics=ET.Element('com')

	# Length of COM marker
	lcom=strToUShortInt(data[0:2])
	addElement(characteristics,"lcom",lcom)

	# lcom should be in range 5-65535
	lcomIsValid=5 <= lcom  <= 65535
	addElement(tests,"lcomIsValid",lcomIsValid)

	# Registration value of marker segment
	rcom=strToUShortInt(data[2:4])
	addElement(characteristics,"rcom",rcom)

	# rcom should be either 0 (binary values) or 1 (ISO/IEC 8859-15 (Latin) values)
	rcomIsValid=0 <= rcom  <= 1
	addElement(tests,"rcomIsValid",rcomIsValid)

	# Contents (multiples of Ccom)
	comment=data[4:lcom]

	# Only add comment to characteristics if text (may contain binary data if rcom is 0!)
	if rcom == 1:

		addElement(characteristics,"comment",comment)

	return(tests,characteristics)

def validateSOT(data):

	# Analyse start of tile-part (SOT) marker segment and validate
	# (ISO/IEC 15444-1 Section A.4.2)

	# Note that unlike other marker validation functions this one returns a
	# third result, which is the total tile-part length (psot)!

	# Test results to elementtree element
	tests=ET.Element('sot')

	# Characteristics to elementtree element
	characteristics=ET.Element('sot')

	# Length of SOT marker
	lsot=strToUShortInt(data[0:2])
	addElement(characteristics,"lsot",lsot)

	# lcom should be 10
	lsotIsValid=lsot  == 10
	addElement(tests,"lsotIsValid",lsotIsValid)

	# Tile index
	isot=strToUShortInt(data[2:4])
	addElement(characteristics,"isot",isot)

	# Tile index should be in range 0-65534
	isotIsValid=0 <= isot <= 65534
	addElement(tests,"isotIsValid",isotIsValid)

	# Length of tile part (including this SOT)
	psot=strToUInt(data[4:8])
	addElement(characteristics,"psot",psot)

	# psot equals 0 (for last tile part) or greater than 14 (so range 1-13 is illegal)
	psotIsValid=not(1 <= psot <= 13)
	addElement(tests,"psotIsValid",psotIsValid)

	# Tile part index
	tpsot=strToUnsignedChar(data[8:9])
	addElement(characteristics,"tpsot",tpsot)

	# Should be in range 0-254
	tpsotIsValid=0 <= tpsot <= 254
	addElement(tests,"tpsotIsValid",tpsotIsValid)

	# Number of tile-parts of a tile in the codestream
	# Value of 0 indicates that number of tile-parts of tile in the codestream
	# is not defined in this header; otherwise value in range 1-255
	tnsot=strToUnsignedChar(data[9:10])
	addElement(characteristics,"tnsot",tnsot)

	return(tests,characteristics,psot)


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
	resultSOT, characteristicsSOT, tilePartLength=validateSOT(segContents)

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
			resultCOD, characteristicsCOD=validateCOD(segContents)

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
			resultQCD, characteristicsQCD=validateQCD(segContents)

			# Add analysis results to test results tree
			tests.append(resultQCD)

			# Add extracted characteristics to characteristics tree
			characteristics.append(characteristicsQCD)

			offset=offsetNext

		elif marker==b'\xff\x64':
			# COM (codestream comment) marker segment

			# Validate QCD segment
			resultCOM, characteristicsCOM=validateCOM(segContents)

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

def getMarkerSegment(data,offset):

	# Read marker segment that starts at offset and return marker, size,
	# contents and start offset of next marker

	# First 2 bytes: 16 bit marker
	marker=data[offset:offset+2]

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

def validateJP2(jp2Data):
	# Top-level function for JP2 validation:
	#
	# 1. Parses all top-level boxes in JP2 byte object, and calls separate validator
	#	function for each of these
	# 2. Checks for presence of all required top-level boxes
	# 3. Checks if JP2 header properties are consistent with corresponding properties
	#	in codestream header

	# Initialise elementtree object that will hold all test results for this image
	tests=ET.Element('tests')

	# Initialise elementtree object that will hold all characteristics (property-value
	# pairs) for this image
	characteristics=ET.Element('properties')

	# Marker tags/codes that identify all top level boxes as hexadecimal strings
	#(Correspond to "Box Type" values, see ISO/IEC 15444-1 Section I.4)
	tagSignatureBox=b'\x6a\x50\x20\x20'
	tagFileTypeBox=b'\x66\x74\x79\x70'
	tagJP2HeaderBox=b'\x6a\x70\x32\x68'
	tagContiguousCodestreamBox=b'\x6a\x70\x32\x63'

	# List for storing box type identifiers
	boxTypes=[]

	noBytes=len(jp2Data)
	byteStart = 0
	bytesTotal=0

	# Dummy value
	boxLengthValue=10

	while byteStart < noBytes and boxLengthValue != 0:

		boxLengthValue, boxType, byteEnd, boxContents = getBox(jp2Data,byteStart, noBytes)

		# Validate current top level box
		resultBox,characteristicsBox = BoxValidator(boxType, boxContents).validate()

		byteStart = byteEnd

		# Add to list of box types
		boxTypes.append(boxType)

		# Add analysis results to test results tree
		tests.append(resultBox)

		# Add extracted characteristics to characteristics tree
		characteristics.append(characteristicsBox)

	# Do all required top level boxes exist (ISO/IEC 15444-1 Section I.4)?
	containsSignatureBox=tagSignatureBox in  boxTypes
	containsFileTypeBox=tagFileTypeBox in  boxTypes
	containsJP2HeaderBox=tagJP2HeaderBox in  boxTypes
	containsContiguousCodestreamBox=tagContiguousCodestreamBox in  boxTypes

	addElement(tests,"containsSignatureBox",containsSignatureBox)
	addElement(tests,"containsFileTypeBox",containsFileTypeBox)
	addElement(tests,"containsJP2HeaderBox",containsJP2HeaderBox)
	addElement(tests,"containsContiguousCodestreamBox",containsContiguousCodestreamBox)

	# If iPR field in image header box equals 1, intellectual property box
	# should exist as well
	iPR=findElementText(characteristics,'jp2HeaderBox/imageHeaderBox/iPR')

	if iPR == 1:
		containsIntellectualPropertyBox=tagIntellectualPropertyBox in  boxTypes
		addElement(tests,"containsIntellectualPropertyBox",containsIntellectualPropertyBox)

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

	addElement(tests,"firstBoxIsSignatureBox",firstBoxIsSignatureBox)
	addElement(tests,"secondBoxIsFileTypeBox",secondBoxIsFileTypeBox)
	addElement(tests,"locationJP2HeaderBoxIsValid",locationJP2HeaderBoxIsValid)

	# Some boxes can have multiple instances, whereas for others only one
	# is allowed
	# --> Note: multiple Contiguous Codestream boxes are allowed, although conforming
	# readers only read first one. So maybe include a warning in case of multiple
	# codestreams?
	noMoreThanOneSignatureBox=boxTypes.count(tagSignatureBox) <= 1
	noMoreThanOneFileTypeBox=boxTypes.count(tagFileTypeBox) <= 1
	noMoreThanOneJP2HeaderBox=boxTypes.count(tagJP2HeaderBox) <= 1

	addElement(tests,"noMoreThanOneSignatureBox",noMoreThanOneSignatureBox)
	addElement(tests,"noMoreThanOneFileTypeBox",noMoreThanOneFileTypeBox)
	addElement(tests,"noMoreThanOneJP2HeaderBox",noMoreThanOneJP2HeaderBox)

	# Check if general image properties in Image Header Box are consistent with
	# corresponding values in codestream header.

	# JP2 image header and codestream SIZ header as element objects
	jp2ImageHeader=characteristics.find('jp2HeaderBox/imageHeaderBox')
	sizHeader=characteristics.find('contiguousCodestreamBox/siz')

	# Only proceed with tests if the above really exist (if this is not the case
	# the preceding tests will have already identified this file as not valid)

	# Note: do *NOT* use 'findtext' function to get values: if value equals 0
	# this returns an empty string, even though 'text' field really contains an
	# integer. Probably a bug in ET. Using 'find' + text property does work
	# as expected

	if jp2ImageHeader != None and sizHeader != None:

		# Height should be equal to ysiz -yOsiz

		height=findElementText(jp2ImageHeader,'height')
		ysiz=findElementText(sizHeader,'ysiz')
		yOsiz=findElementText(sizHeader,'yOsiz')

		heightConsistentWithSIZ=height == (ysiz-yOsiz)
		addElement(tests,"heightConsistentWithSIZ", heightConsistentWithSIZ)

		# Width should be equal to xsiz - xOsiz
		width=findElementText(jp2ImageHeader,'width')
		xsiz=findElementText(sizHeader,'xsiz')
		xOsiz=findElementText(sizHeader,'xOsiz')

		widthConsistentWithSIZ=width == (xsiz-xOsiz)
		addElement(tests,"widthConsistentWithSIZ", widthConsistentWithSIZ)

		# nC should be equal to csiz
		nC=findElementText(jp2ImageHeader,'nC')
		csiz=findElementText(sizHeader,'csiz')

		nCConsistentWithSIZ=nC == csiz
		addElement(tests,"nCConsistentWithSIZ", nCConsistentWithSIZ)

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

		bPCSign=findElementText(jp2ImageHeader, 'bPCSign')
		bPCDepth=findElementText(jp2ImageHeader,'bPCDepth')

		if bPCSign == 1 and bPCDepth == 128:
			# Actual bPCSign / bPCDepth in Bits Per Components box
			# (situation 2 above)

			bpcBox=characteristics.find('jp2HeaderBox/bitsPerComponentBox')

			# All occurrences of bPCSign box to list. If bpcBox is 'noneType'
			# (e.g. due to some weird corruption of the file) this will result in
			# an empty list, so nothing really bad will happen ..
			bPCSignValues=findAllText(bpcBox,'bPCSign')

			# All occurrences of bPCDepth to list
			bPCDepthValues=findAllText(bpcBox,'bPCDepth')

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
		ssizSignValues=findAllText(sizHeader,'ssizSign')

		# All occurrences of ssizDepth to list
		ssizDepthValues=findAllText(sizHeader,'ssizDepth')

		# bPCSignValues should be equal to ssizSignValues
		bPCSignConsistentWithSIZ=bPCSignValues == ssizSignValues
		addElement(tests,"bPCSignConsistentWithSIZ", bPCSignConsistentWithSIZ)

		# bPCDepthValues should be equal to ssizDepthValues
		bPCDepthConsistentWithSIZ=bPCDepthValues == ssizDepthValues
		addElement(tests,"bPCDepthConsistentWithSIZ", bPCDepthConsistentWithSIZ)

		# Calculate compression ratio of this image
		compressionRatio=calculateCompressionRatio(noBytes,bPCDepthValues,height,width)
		compressionRatio=round(compressionRatio,2)
		addElement(characteristics,"compressionRatio",compressionRatio)

	# Valid JP2 only if all tests returned True
	isValid=isValidJP2(tests)

	return(isValid,tests,characteristics)

def checkFiles(images):
	if len(images) == 0:
		printWarning("no images to check!")

	for image in images:
		thisFile = image

		isFile = os.path.isfile(thisFile)

		if isFile:
			# Read and analyse one file
			fileData = readFileBytes(thisFile)
			isValidJP2, tests, characteristics = validateJP2(fileData)

			# Generate property values remap table
			remapTable = generatePropertiesRemapTable()

			# Create printable version of tests and characteristics tree
			testsPrintable = elementTreeToPrintable(tests,{})
			characteristicsPrintable = elementTreeToPrintable(characteristics,remapTable)

			# Create output elementtree object
			root=ET.Element('jpylyzer')

			# Create elements for storing tool and file meta info
			toolInfo=ET.Element('toolInfo')
			fileInfo=ET.Element('fileInfo')

			# Produce some general tool and file meta info
			addElement(toolInfo,"toolName",scriptName)
			addElement(toolInfo,"toolVersion",__version__)
			addElement(fileInfo,"fileName",thisFile)
			addElement(fileInfo,"filePath",os.path.abspath(thisFile))
			addElement(fileInfo,"fileSizeInBytes",str(os.path.getsize(thisFile)))
			addElement(fileInfo,"fileLastModified",time.ctime(os.path.getmtime(thisFile)))

			# Append to root
			root.append(toolInfo)
			root.append(fileInfo)

			# Add validation outcome
			addElement(root,"isValidJP2",str(isValidJP2))

			# Append test results and characteristics to root
			root.append(testsPrintable)
			root.append(characteristicsPrintable)

			# Write output
			writeOutput(root)


def parseCommandLine():
	# Create parser
	parser = argparse.ArgumentParser(description="JP2 image validator and properties extractor",version=__version__)

	# Add arguments
	parser.add_argument('jp2In', action="store", help="input JP2 image(s)")

	# Parse arguments
	args=parser.parse_args()

	return(args)

def main():
	# Get input from command line
	args=parseCommandLine()
	jp2In=args.jp2In

	# Input images as file list
	imagesIn=glob.glob(jp2In)

	# Check file
	checkFiles(imagesIn)

if __name__ == "__main__":
	main()


