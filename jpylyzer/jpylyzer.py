#! /usr/bin/env python
#
"""Jpylyzer validator for JPEG 200 Part 1 (JP2) images

 Requires: Python 2.7 (older versions won't work) OR Python 3.2 or more recent
  (Python 3.0 and 3.1 won't work either!)

 Copyright (C) 2011 - 2017 Johan van der Knijff, Koninklijke Bibliotheek -
  National Library of the Netherlands

Contributors:
   Rene van der Ark, NL (refactoring of original code).
   Lars Buitinck, NL.
   Adam Retter, The National Archives, UK.
   Jaishree Davey, The National Archives, UK.
   Laura Damian, The National Archives, UK.
   Carl Wilson, Open Planets Foundation, UK.
   Stefan Weil, UB Mannheim, DE.
   Adam Fritzler, Planet Labs, USA.
"""

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

import sys
import mmap
import os
import time
import glob
import argparse
import codecs
import re
from xml.dom import minidom
import xml.etree.ElementTree as ETree
from six import u
from . import config as config
from . import etpatch as ET
from . import boxvalidator as bv
from . import shared as shared


scriptPath, scriptName = os.path.split(sys.argv[0])

# scriptName is empty when called from Java/Jython, so this needs a fix
if len(scriptName) == 0:
    scriptName = 'jpylyzer'

__version__ = "1.18.0b8"

# Create parser
parser = argparse.ArgumentParser(
    description="JP2 image validator and properties extractor")

# list of existing files to be analysed
existingFiles = []

# Name space and schema strings
nsString = 'http://openpreservation.org/ns/jpylyzer/'
xsiNsString = 'http://www.w3.org/2001/XMLSchema-instance'
locSchemaString = 'http://openpreservation.org/ns/jpylyzer/ \
http://jpylyzer.openpreservation.org/jpylyzer-v-1-1.xsd'


def generatePropertiesRemapTable():
    """Generates nested dictionary which is used to map 'raw' property values
    (mostly integer values) to corresponding text descriptions
    """

    # Master dictionary for mapping of text descriptions to enumerated values
    # Key: corresponds to parameter tag name
    # Value: sub-dictionary with mappings for all property values
    enumerationsMap = {}

    # Sub-dictionaries for individual properties

    # Generic 0 = no, 1=yes mapping (used for various properties)
    yesNoMap = {}
    yesNoMap[0] = "no"
    yesNoMap[1] = "yes"

    # Bits per component: sign (Image HeaderBox, Bits Per Component Box, SIZ header
    # in codestream)
    signMap = {}
    signMap[0] = "unsigned"
    signMap[1] = "signed"

    # Compression type (Image Header Box)
    cMap = {}
    cMap[7] = "jpeg2000"

    # meth (Colour Specification Box)
    methMap = {}
    methMap[1] = "Enumerated"
    methMap[2] = "Restricted ICC"
    methMap[3] = "Any ICC"  # JPX only
    methMap[4] = "Vendor Colour"  # JPX only

    # enumCS (Colour Specification Box)
    enumCSMap = {}
    enumCSMap[16] = "sRGB"
    enumCSMap[17] = "greyscale"
    enumCSMap[18] = "sYCC"

    # Profile Class (ICC)
    profileClassMap = {}
    profileClassMap[b'scnr'] = "Input Device Profile"
    profileClassMap[b'mntr'] = "Display Device Profile"
    profileClassMap[b'prtr'] = "Output Device Profile"
    profileClassMap[b'link'] = "DeviceLink Profile"
    profileClassMap[b'spac'] = "ColorSpace Conversion Profile"
    profileClassMap[b'abst'] = "Abstract Profile"
    profileClassMap[b'nmcl'] = "Named Colour Profile"

    # Primary Platform (ICC)
    primaryPlatformMap = {}
    primaryPlatformMap[b'APPL'] = "Apple Computer, Inc."
    primaryPlatformMap[b'MSFT'] = "Microsoft Corporation"
    primaryPlatformMap[b'SGI'] = "Silicon Graphics, Inc."
    primaryPlatformMap[b'SUNW'] = "Sun Microsystems, Inc."

    # Transparency (ICC)
    transparencyMap = {}
    transparencyMap[0] = "Reflective"
    transparencyMap[1] = "Transparent"

    # Glossiness (ICC)
    glossinessMap = {}
    glossinessMap[0] = "Glossy"
    glossinessMap[1] = "Matte"

    # Polarity (ICC)
    polarityMap = {}
    polarityMap[0] = "Positive"
    polarityMap[1] = "Negative"

    # Colour (ICC)
    colourMap = {}
    colourMap[0] = "Colour"
    colourMap[1] = "Black and white"

    # Rendering intent (ICC)
    renderingIntentMap = {}
    renderingIntentMap[0] = "Perceptual"
    renderingIntentMap[1] = "Media-Relative Colorimetric"
    renderingIntentMap[2] = "Saturation"
    renderingIntentMap[3] = "ICC-Absolute Colorimetric"

    # mTyp (Component Mapping box)
    mTypMap = {}
    mTypMap[0] = "direct use"
    mTypMap[1] = "palette mapping"

    # Channel type (Channel Definition Box)
    cTypMap = {}
    cTypMap[0] = "colour"
    cTypMap[1] = "opacity"
    cTypMap[2] = "premultiplied opacity"
    cTypMap[65535] = "not specified"

    # Channel association (Channel Definition Box)
    cAssocMap = {}
    cAssocMap[0] = "all colours"
    cAssocMap[65535] = "no colours"

    # Decoder capabilities, rsiz (Codestream, SIZ)
    rsizMap = {}
    rsizMap[0] = "ISO/IEC 15444-1"  # Does this correspiond to Profile 2??
    rsizMap[1] = "Profile 0"
    rsizMap[2] = "Profile 1"

    # Progression order (Codestream, COD)
    orderMap = {}
    orderMap[0] = "LRCP"
    orderMap[1] = "RLCP"
    orderMap[2] = "RPCL"
    orderMap[3] = "PCRL"
    orderMap[4] = "CPRL"

    # Transformation type (Codestream, COD)
    transformationMap = {}
    transformationMap[0] = "9-7 irreversible"
    transformationMap[1] = "5-3 reversible"

    # Quantization style (Codestream, QCD)
    qStyleMap = {}
    qStyleMap[0] = "no quantization"
    qStyleMap[1] = "scalar derived"
    qStyleMap[2] = "scalar expounded"

    # Registration value (Codestream, COM)
    registrationMap = {}
    registrationMap[0] = "binary"
    registrationMap[1] = "ISO/IEC 8859-15 (Latin)"

    # Add sub-dictionaries to master dictionary, using tag name as key
    enumerationsMap['unkC'] = yesNoMap
    enumerationsMap['iPR'] = yesNoMap
    enumerationsMap['profileClass'] = profileClassMap
    enumerationsMap['primaryPlatform'] = primaryPlatformMap
    enumerationsMap['embeddedProfile'] = yesNoMap
    enumerationsMap['profileCannotBeUsedIndependently'] = yesNoMap
    enumerationsMap['transparency'] = transparencyMap
    enumerationsMap['glossiness'] = glossinessMap
    enumerationsMap['polarity'] = polarityMap
    enumerationsMap['colour'] = colourMap
    enumerationsMap['renderingIntent'] = renderingIntentMap
    enumerationsMap['bSign'] = signMap
    enumerationsMap['mTyp'] = mTypMap
    enumerationsMap['precincts'] = yesNoMap
    enumerationsMap['sop'] = yesNoMap
    enumerationsMap['eph'] = yesNoMap
    enumerationsMap['multipleComponentTransformation'] = yesNoMap
    enumerationsMap['codingBypass'] = yesNoMap
    enumerationsMap['resetOnBoundaries'] = yesNoMap
    enumerationsMap['termOnEachPass'] = yesNoMap
    enumerationsMap['vertCausalContext'] = yesNoMap
    enumerationsMap['predTermination'] = yesNoMap
    enumerationsMap['segmentationSymbols'] = yesNoMap
    enumerationsMap['bPCSign'] = signMap
    enumerationsMap['ssizSign'] = signMap
    enumerationsMap['c'] = cMap
    enumerationsMap['meth'] = methMap
    enumerationsMap['enumCS'] = enumCSMap
    enumerationsMap['cTyp'] = cTypMap
    enumerationsMap['cAssoc'] = cAssocMap
    enumerationsMap['order'] = orderMap
    enumerationsMap['transformation'] = transformationMap
    enumerationsMap['rsiz'] = rsizMap
    enumerationsMap['qStyle'] = qStyleMap
    enumerationsMap['rcom'] = registrationMap

    return enumerationsMap


def fileToMemoryMap(filename):
    """Read contents of filename to memory map object"""

    # Open filename
    f = open(filename, "rb")

    # Call to mmap is different on Linux and Windows, so we need to know
    # the current platform
    platform = config.PLATFORM

    try:
        if platform == "win32":
            # Parameters for Windows may need further fine-tuning ...
            fileData = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        else:
            # This works for Linux (and Cygwin on Windows). Not too sure
            # about other platforms like Mac OS though
            fileData = mmap.mmap(f.fileno(), 0, mmap.MAP_SHARED, mmap.PROT_READ)
    except ValueError:
        # mmap fails on empty files.
        fileData = ""

    f.close()
    return fileData


def checkOneFile(path):
    """Process one file and return analysis result as element object"""

    # Create output elementtree object

    if config.inputRecursiveFlag or config.inputWrapperFlag:
        # Name space already declared in results element, so no need to do it
        # here
        root = ET.Element('jpylyzer')
    else:
        root = ET.Element(
            'jpylyzer', {'xmlns': nsString,
                         'xmlns:xsi': xsiNsString,
                         'xsi:schemaLocation': locSchemaString})

    # Create elements for storing tool, file and status meta info
    toolInfo = ET.Element('toolInfo')
    fileInfo = ET.Element('fileInfo')
    statusInfo = ET.Element('statusInfo')

    # File name and path
    fileName = os.path.basename(path)
    filePath = os.path.abspath(path)

    # If file name / path contain any surrogate pairs, remove them to
    # avoid problems when writing to XML
    fileNameCleaned = stripSurrogatePairs(fileName)
    filePathCleaned = stripSurrogatePairs(filePath)

    # Produce some general tool and file meta info
    toolInfo.appendChildTagWithText("toolName", scriptName)
    toolInfo.appendChildTagWithText("toolVersion", __version__)
    fileInfo.appendChildTagWithText("fileName", fileNameCleaned)
    fileInfo.appendChildTagWithText("filePath", filePathCleaned)
    fileInfo.appendChildTagWithText(
        "fileSizeInBytes", str(os.path.getsize(path)))
    try:
        lastModifiedDate = time.ctime(os.path.getmtime(path))
    except ValueError:
        # Dates earlier than 1 Jan 1970 can raise ValueError on Windows
        # Workaround: replace by lowest possible value (typically 1 Jan 1970)
        lastModifiedDate = time.ctime(0)
    fileInfo.appendChildTagWithText(
        "fileLastModified", lastModifiedDate)

    # Initialise success flag
    success = True

    try:
        # Contents of file to memory map object
        fileData = fileToMemoryMap(path)
        isValidJP2, tests, characteristics = bv.BoxValidator("JP2", fileData).validate()

        if fileData != "":
            fileData.close()

        # Generate property values remap table
        remapTable = generatePropertiesRemapTable()

        # Create printable version of tests and characteristics tree
        tests.makeHumanReadable()
        characteristics.makeHumanReadable(remapTable)
    except Exception as ex:
        isValidJP2 = False
        success = False
        exceptionType = type(ex)

        if exceptionType == MemoryError:
            failureMessage = "memory error (file size too large)"
        elif exceptionType == IOError:
            failureMessage = "I/O error (cannot open file)"
        elif exceptionType == RuntimeError:
            failureMessage = "runtime error (please report to developers)"
        else:
            failureMessage = "unknown error (please report to developers)"

        shared.printWarning(failureMessage)
        tests = ET.Element("tests")
        characteristics = ET.Element('properties')

    # Add status info
    statusInfo.appendChildTagWithText("success", str(success))
    if not success:
        statusInfo.appendChildTagWithText("failureMessage", failureMessage)

    # Append all results to root
    root.append(toolInfo)
    root.append(fileInfo)
    root.append(statusInfo)
    root.appendChildTagWithText("isValidJP2", str(isValidJP2))
    root.append(tests)
    root.append(characteristics)

    return root


def checkNullArgs(args):
    """This method checks if the input arguments list and exits program if
    invalid or no input argument is supplied.
    """

    if len(args) == 0:

        print('')
        parser.print_help()
        sys.exit(config.ERR_CODE_NO_IMAGES)


def checkNoInput(files):
    """Check if input arguments list results in any existing input files at all
    (and exits if not)
    """

    if len(files) == 0:
        shared.printWarning("no images to check!")
        sys.exit(config.ERR_CODE_NO_IMAGES)


def printHelpAndExit():
    """Print help message and exit"""
    print('')
    parser.print_help()
    sys.exit()


def stripSurrogatePairs(ustring):

    """Removes surrogate pairs from a Unicode string"""

    # This works for Python 3.x, but not for 2.x!
    # Source: http://stackoverflow.com/q/19649463/1209004

    if config.PYTHON_VERSION.startswith(config.PYTHON_3):
        try:
            ustring.encode('utf-8')
        except UnicodeEncodeError:
            # Strip away surrogate pairs
            tmp = ustring.encode('utf-8', 'replace')
            ustring = tmp.decode('utf-8', 'ignore')

    # In Python 2.x we need to use regex
    # Source: http://stackoverflow.com/a/18674109/1209004

    if config.PYTHON_VERSION.startswith(config.PYTHON_2):
        # Generate regex for surrogate pair detection

        lone = re.compile(
            u(r"""(?x)            # verbose expression (allows comments)
            (                    # begin group
            [\ud800-\udbff]      #   match leading surrogate
            (?![\udc00-\udfff])  #   but only if not followed by trailing surrogate
            )                    # end group
            |                    #  OR
            (                    # begin group
            (?<![\ud800-\udbff]) #   if not preceded by leading surrogate
            [\udc00-\udfff]      #   match trailing surrogate
            )                   # end group
            """))

        # Remove surrogates (i.e. replace by empty string)
        tmp = lone.sub(r'', ustring).encode('utf-8')
        ustring = tmp.decode('utf-8')

    return ustring


def getFiles(searchpattern):
    """Append paths of all files that match search pattern to existingFiles"""
    results = glob.glob(searchpattern)
    for f in results:
        if os.path.isfile(f):
            existingFiles.append(f)


def getFilesWithPatternFromTree(rootDir, pattern):
    """Recurse into directory tree and return list of all files
    NOTE: directory names are disabled here!!
    """
    for dirname, dirnames, filenames in os.walk(rootDir):
        # Suppress directory names
        for subdirname in dirnames:
            thisDirectory = os.path.join(dirname, subdirname)
            # find files matching the pattern in current path
            searchpattern = os.path.join(thisDirectory, pattern)
            getFiles(searchpattern)


def getFilesFromTree(rootDir):
    """Recurse into directory tree and return list of all files
    NOTE: directory names are disabled here!!
    """

    for dirname, dirnames, filenames in os.walk(rootDir):
        # Suppress directory names
        for subdirname in dirnames:
            thisDirectory = os.path.join(dirname, subdirname)

        for filename in filenames:
            thisFile = os.path.join(dirname, filename)
            existingFiles.append(thisFile)


def findFiles(recurse, paths):
    """Find all files that match a wildcard expression and add their paths to existingFiles"""

    WILDCARD = "*"

    # process the list of input paths
    for root in paths:

        if config.PYTHON_VERSION.startswith(config.PYTHON_2):
            # Convert root to UTF-8 (only needed for Python 2.x)
            root = unicode(root, 'utf-8')

        # WILDCARD IN PATH OR FILENAME
        # In Linux wilcard expansion done by bash so, add file to list
        if os.path.isfile(root):
            existingFiles.append(root)
        # Windows (& Linux with backslash prefix) does not expand wildcard '*'
        # Find files in the input path and add to list
        elif WILDCARD in root:
            # get the absolute path if not given
            if not os.path.isabs(root):
                root = os.path.abspath(root)

            # Expand wildcard in the input path. Returns a list of files,
            # folders
            filesList = glob.glob(root)

            # If the input path is a directory, then glob expands it to full
            # name
            if len(filesList) == 1 and os.path.isdir(filesList[0]):
                # set root to the expanded directory path
                root = filesList[0]

            # get files from directory

            # If the input path returned files list, add files to List

            if len(filesList) == 1 and os.path.isfile(filesList[0]):
                existingFiles.append(filesList[0])

            if len(filesList) > 1:
                for f in filesList:
                    if os.path.isfile(f):
                        existingFiles.append(f)

        elif not os.path.isdir(root) and not os.path.isfile(root):
            # One or more (but not all) paths do no exist - print a warning
            msg = root + " does not exist"
            shared.printWarning(msg)

        # RECURSION and WILDCARD IN RECURSION
        # Check if recurse in the input path
        if recurse:
            # get absolute input path if not given
            if not os.path.isabs(root):
                root = os.path.abspath(root)

            if WILDCARD in root:
                pathAndFilePattern = os.path.split(root)
                path = pathAndFilePattern[0]
                filePattern = pathAndFilePattern[1]
                filenameAndExtension = os.path.splitext(filePattern)
                # input path contains wildcard
                if WILDCARD in path:
                    filepath = glob.glob(path)
                    # if filepath is a folder, get files in current directory
                    if len(filepath) == 1:
                        getFilesWithPatternFromTree(filepath[0], filePattern)
                    # if filepath is a list of files/folder
                    # get all files in the tree matching the file pattern
                    if len(filepath) > 1:
                        for f in filepath:
                            if os.path.isdir(f):
                                getFilesWithPatternFromTree(f, filePattern)
                # file name or extension contains wildcard
                elif WILDCARD in filePattern:
                    getFilesWithPatternFromTree(path, filePattern)
                elif WILDCARD in filenameAndExtension:
                    filenameAndExtension = os.path.splitext(filePattern)
                    extension = WILDCARD + filenameAndExtension[1]
                    getFilesWithPatternFromTree(path, extension)
            # get files in the current folder and sub dirs w/o wildcard in path
            elif os.path.isdir(root):
                getFilesFromTree(root)


def writeElement(elt, codec):
    """Writes element as XML to stdout using defined codec"""

    # Element to string
    if config.PYTHON_VERSION.startswith(config.PYTHON_2):
        xmlOut = ET.tostring(elt, 'UTF-8', 'xml')
    if config.PYTHON_VERSION.startswith(config.PYTHON_3):
        xmlOut = ET.tostring(elt, 'unicode', 'xml')

    if not config.noPrettyXMLFlag:
        # Make xml pretty
        xmlPretty = minidom.parseString(xmlOut).toprettyxml('    ')

        # Steps to get rid of xml declaration:
        # String to list
        xmlAsList = xmlPretty.split("\n")
        # Remove first item (xml declaration)
        del xmlAsList[0]
        # Convert back to string
        xmlOut = "\n".join(xmlAsList)

        # Write output
        codec.write(xmlOut)
    else:
        # Python2.x does automatic conversion between byte and string types,
        # hence, binary data can be output using sys.stdout
        if config.PYTHON_VERSION.startswith(config.PYTHON_2):
            ETree.ElementTree(elt).write(codec, xml_declaration=False)
        # Python3.x recognizes bytes and str as different types and encoded
        # Unicode is represented as binary data. The underlying sys.stdout.buffer
        # is used to write binary data
        if config.PYTHON_VERSION.startswith(config.PYTHON_3):
            codec.write(xmlOut)


def checkFiles(recurse, wrap, paths):
    """This method checks the input argument path(s) for existing files and
    analyses them
    """

    # Find existing files in the given input path(s)
    findFiles(recurse, paths)

    # If there are no valid input files then exit program
    checkNoInput(existingFiles)

    # Set encoding of the terminal to UTF-8
    if config.PYTHON_VERSION.startswith(config.PYTHON_2):
        out = codecs.getwriter(config.UTF8_ENCODING)(sys.stdout)
    elif config.PYTHON_VERSION.startswith(config.PYTHON_3):
        out = codecs.getwriter(config.UTF8_ENCODING)(sys.stdout.buffer)

    # Wrap the xml output in <results> element, if wrapper flag is true
    if wrap or recurse:
        xmlHead = "<?xml version='1.0' encoding='UTF-8'?>\n"
        xmlHead += "<results xmlns=\"" + nsString + "\" "
        xmlHead += "xmlns:xsi=\"" + xsiNsString + "\" "
        xmlHead += "xsi:schemaLocation=\"" + locSchemaString + "\">\n"
    else:
        xmlHead = "<?xml version='1.0' encoding='UTF-8'?>\n"
    out.write(xmlHead)

    # Process the input files
    for path in existingFiles:

        # Analyse file
        xmlElement = checkOneFile(path)

        # Write output to stdout
        writeElement(xmlElement, out)

    # Close </results> element if wrapper flag is true
    if wrap or recurse:
        out.write("</results>\n")


def parseCommandLine():
    """Parse command line arguments"""

    # Add arguments
    parser.add_argument('--verbose',
                        action="store_true",
                        dest="outputVerboseFlag",
                        default=False,
                        help="report test results in verbose format")

    parser.add_argument('--recurse', '-r',
                        action="store_true",
                        dest="inputRecursiveFlag",
                        default=False,
                        help="when analysing a directory, recurse into subdirectories \
                                (implies --wrapper)")
    parser.add_argument('--wrapper',
                        '-w', action="store_true",
                        dest="inputWrapperFlag",
                        default=False,
                        help="wrap output for individual image(s) in 'results' XML element")
    parser.add_argument('--nullxml',
                        action="store_true",
                        dest="extractNullTerminatedXMLFlag",
                        default=False,
                        help="extract null-terminated XML content from XML and UUID boxes \
                                (doesn't affect validation)")
    parser.add_argument('--nopretty',
                        action="store_true",
                        dest="noPrettyXMLFlag",
                        default=False,
                        help="suppress pretty-printing of XML output")
    parser.add_argument('jp2In',
                        action="store",
                        type=str,
                        nargs='+',
                        help="input JP2 image(s), may be one or more (whitespace-separated) path \
                                expressions; prefix wildcard (*) with backslash (\\) in Linux")
    parser.add_argument('--version', '-v',
                        action='version',
                        version=__version__)

    # Parse arguments
    args = parser.parse_args()

    return args


def main():
    """Main command line application"""
       
    # Get input from command line
    args = parseCommandLine()

    # Input images
    jp2In = args.jp2In

    # Print help message and exit if jp2In is empty
    if len(jp2In) == 0:
        printHelpAndExit()

    # Makes user-specified flags available to any module that imports 'config.py'
    # (here: 'boxvalidator.py')
    config.outputVerboseFlag = args.outputVerboseFlag
    config.extractNullTerminatedXMLFlag = args.extractNullTerminatedXMLFlag
    config.inputRecursiveFlag = args.inputRecursiveFlag
    config.inputWrapperFlag = args.inputWrapperFlag
    config.extractNullTerminatedXMLFlag = args.extractNullTerminatedXMLFlag
    config.noPrettyXMLFlag = args.noPrettyXMLFlag

    # Check files
    checkFiles(args.inputRecursiveFlag, args.inputWrapperFlag, jp2In)
    # checkFiles(False, args.inputWrapperFlag, jp2In)

if __name__ == "__main__":
    main()
