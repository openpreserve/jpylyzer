"""Patch for 'findtext' bug in ElementTree
TODO:
1) Find out whether these patches are necessary
2) learn how to write and test patches properly
"""
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

import xml.etree.ElementTree as ET
from . import byteconv as bc
from . import config


def tostring(elem, enc, meth):
    """Return string representation of Element object with user-defined encoding and method"""
    return ET.tostring(elem, enc, meth)


def fromstring(text):
    """Convert string to Element object"""
    return ET.fromstring(text)


def SubElement(parent, tag):
    """Return sub-element from parent element"""
    return ET.SubElement(parent, tag)


class Element(ET.Element):
    """Element class"""

    def findElementText(self, match):
        """Replacement for ET's 'findtext' function, which has a bug
        that will return empty string if text field contains integer with
        value of zero (0); If there is no match, return None
        """
        elt = self.find(match)
        if elt is not None:
            return elt.text
        return None

    def findAllText(self, match):
        """Searches element and returns list that contains 'Text' attribute
        of all matching sub-elements. Returns empty list if element
        does not exist
        """

        try:
            return [result.text for result in self.findall(match)]
        except:
            return []

    def appendChildTagWithText(self, tag, text):
        """Append childnode with text"""

        el = ET.SubElement(self, tag)
        el.text = text

    def appendIfNotEmpty(self, subelement):
        """Append sub-element, but only if subelement is not empty"""

        if len(subelement) != 0:
            self.append(subelement)

    def makeHumanReadable(self, remapTable=None):
        """Takes element object, and returns a modified version in which all
        non-printable 'text' fields (which may contain numeric data or binary strings)
        are replaced by printable strings

        Property values in original tree may be mapped to alternative (more user-friendly)
        reportable values using a remapTable, which is a nested dictionary.
        """
        remapTable = remapTable or {}
        for elt in self.iter():
            # Text field of this element
            textIn = elt.text

            # Tag name
            tag = elt.tag

            # Step 1: replace property values by values defined in enumerationsMap,
            # if applicable
            try:
                # If tag is in enumerationsMap, replace property values
                parameterMap = remapTable[tag]
                try:
                    # Map original property values to values in dictionary
                    remappedValue = parameterMap[textIn]
                except KeyError:
                    # If value doesn't match any key: use original value
                    # instead
                    remappedValue = textIn
            except KeyError:
                # If tag doesn't match any key in enumerationsMap, use original
                # value
                remappedValue = textIn

            # Step 2: convert all values to text strings.

            # First set up list of all numeric data types,
            # which is dependent on the Python version used

            if config.PYTHON_VERSION.startswith(config.PYTHON_2):
                # Python 2.x
                numericTypes = [int, long, float, bool]
                # Long type is deprecated in Python 3.x!
            else:
                numericTypes = [int, float, bool]

            # Convert

            if remappedValue is not None:
                # Data type
                textType = type(remappedValue)

                # Convert text field, depending on type
                if textType == bytes:
                    textOut = bc.bytesToText(remappedValue)
                elif textType in numericTypes:
                    textOut = str(remappedValue)
                else:
                    textOut = bc.removeControlCharacters(remappedValue)

                # Update output tree
                elt.text = textOut

    def toxml(self, indent="  "):
        """Convert Element object to XML"""
        return ET.tostring(self, 'UTF-8', 'xml')
