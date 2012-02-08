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
import etpatch as ET
from boxvalidator import BoxValidator
from byteconv import strToText

scriptPath, scriptName = os.path.split(sys.argv[0])

__version__= "8 February 2012"


def main_is_frozen():
	return (hasattr(sys, "frozen") or # new py2exe
			hasattr(sys, "importers") # old py2exe
			or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
	if main_is_frozen():
		return os.path.dirname(sys.executable)
	return os.path.dirname(sys.argv[0])

# Read file, return contents as a byte object
def readFileBytes(file):
	# Open file
	f = open(file,"rb")
	# Put contents of file into a byte object.
	fileData=f.read()
	f.close()
	return(fileData)


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



def checkFiles(images):
	if len(images) == 0:
		warnings.warn("no images to check!")

	for image in images:
		thisFile = image

		isFile = os.path.isfile(thisFile)

		if isFile:
			# Read and analyse one file
			fileData = readFileBytes(thisFile)
			isValidJP2, tests, characteristics = BoxValidator("JP2", fileData).validate() #validateJP2(fileData)

			# Generate property values remap table
			remapTable = generatePropertiesRemapTable()

			# Create printable version of tests and characteristics tree
			tests.makeHumanReadable()
			characteristics.makeHumanReadable(remapTable)

			# Create output elementtree object
			root=ET.Element('jpylyzer')

			# Create elements for storing tool and file meta info
			toolInfo=ET.Element('toolInfo')
			fileInfo=ET.Element('fileInfo')

			# Produce some general tool and file meta info
			toolInfo.appendChildTagWithText("toolName", scriptName)
			toolInfo.appendChildTagWithText("toolVersion", __version__)
			fileInfo.appendChildTagWithText("fileName", thisFile)
			fileInfo.appendChildTagWithText("filePath", os.path.abspath(thisFile))
			fileInfo.appendChildTagWithText("fileSizeInBytes", str(os.path.getsize(thisFile)))
			fileInfo.appendChildTagWithText("fileLastModified", time.ctime(os.path.getmtime(thisFile)))

			# Append to root
			root.append(toolInfo)
			root.append(fileInfo)

			# Add validation outcome
			root.appendChildTagWithText("isValidJP2", str(isValidJP2))

			# Append test results and characteristics to root
			root.append(tests)
			root.append(characteristics)

			# Write output
			sys.stdout.write(root.toxml())

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
