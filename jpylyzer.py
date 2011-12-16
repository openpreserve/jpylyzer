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
import xml.etree.ElementTree as ET
from xml.dom import minidom
from boxvalidator import BoxValidator

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

		heightConsistentWithSIZ = height == (ysiz-yOsiz)
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


