"""Shared functions for jpylyzer sub-modules."""
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

# Various shared functions

import sys
from . import byteconv as bc


def printWarning(msg):
    """Print warning to stderr."""
    msgString = ("User warning: " + msg + "\n")
    sys.stderr.write(msgString)


def errorExit(msg):
    """Print error message to stderr and exit."""
    msgString = ("Error: " + msg + "\n")
    sys.stderr.write(msgString)
    sys.exit()


def consecutive(lst):
    """Return True if items in lst are consecutive numbers."""
    for i in range(1, len(lst)):
        if lst[i] - lst[i - 1] != 1:
            return False
    return True


def listOccurrencesAreContiguous(lst, value):
    """Return True if all occurrences of value in lst are at contiguous positions."""
    indices_of_value = [i for i in range(len(lst)) if lst[i] == value]
    return consecutive(indices_of_value)


def _getBox(validatorInstance, byteStart, noBytes):
    """Parse JP2 box and return information on its size, type and contents."""
    # Box length (4 byte unsigned integer)
    boxLengthValue = bc.bytesToUInt(
        validatorInstance.boxContents[byteStart:byteStart + 4])

    # Box type
    boxType = validatorInstance.boxContents[byteStart + 4:byteStart + 8]

    # Start byte of box contents
    contentsStartOffset = 8

    # Read extended box length if box length value equals 1
    # In that case contentsStartOffset must also be 16 (not 8!)
    # (See ISO/IEC 15444-1 Section I.4)
    if boxLengthValue == 1:
        boxLengthValue = bc.bytesToULongLong(
            validatorInstance.boxContents[byteStart + 8:byteStart + 16])
        contentsStartOffset = 16

    # For the very last box in a file boxLengthValue may equal 0, so we need
    # to calculate actual value
    if boxLengthValue == 0:
        boxLengthValue = noBytes - byteStart

    # End byte for current box
    byteEnd = byteStart + boxLengthValue

    # Contents of this box as a byte object (i.e. 'DBox' in ISO/IEC 15444-1
    # Section I.4)
    boxContents = validatorInstance.boxContents[byteStart + contentsStartOffset:byteEnd]

    return (boxLengthValue, boxType, byteEnd, boxContents)
