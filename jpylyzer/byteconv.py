"""Various functions for converting and manipulating bytes objects."""
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

import struct
import binascii
import unicodedata


def _doConv(bytestr, bOrder, formatCharacter):
    """Convert bytestr object of bOrder byteorder.

    Formatted using formatCharacter.
    Returns -9999 if struct.unpack raises an error
    """
    # Format string for unpack
    formatStr = bOrder + formatCharacter
    try:
        result = struct.unpack(formatStr, bytestr)[0]
    except BaseException:
        result = -9999
    return result


def bytesToULongLong(bytestring):
    """Unpack 8 byte string to unsigned long long integer.

    Assuming big-endian byte order.
    """
    return _doConv(bytestring, ">", "Q")


def bytesToUInt(bytestring):
    """Unpack 4 byte string to unsigned integer.

    Assuming big-endian byte order.
    """
    return _doConv(bytestring, ">", "I")


def bytesToUShortInt(bytestring):
    """Unpack 2 byte string to unsigned short integer.

    Assuming big-endian byte order.
    """
    return _doConv(bytestring, ">", "H")


def bytesToUnsignedChar(bytestring):
    """Unpack 1 byte string to unsigned character/integer.

    Assuming big-endian byte order.
    """
    return _doConv(bytestring, ">", "B")


def bytesToSignedChar(bytestring):
    """Unpack 1 byte string to signed character/integer.

    Assuming big-endian byte order.
    """
    return _doConv(bytestring, ">", "b")


def bytesToInteger(bytestring):
    """Unpack byte string of any length to integer.

    Taken from:
    http://stackoverflow.com/questions/4358285/

    JvdK: what endianness is assumed here? Could go wrong on some systems?

    binascii.hexlify will be obsolete in python3 soon
    They will add a .tohex() method to bytes class
    Issue 3532 bugs.python.org
    """
    try:
        result = int(binascii.hexlify(bytestring), 16)
    except BaseException:
        result = -9999

    return result


def isctrl(c):
    """Return True if byte corresponds to device control character.

    (See also: http://www.w3schools.com/tags/ref_ascii.asp)
    """
    return ord(c) < 32 or ord(c) == 127


def bytesToHex(bytestring):
    """Return hexadecimal ascii representation of bytestring."""
    return binascii.hexlify(bytestring)


def containsControlCharacters(bytestring):
    """Return True if bytestring object contains control characters."""
    for i in range(len(bytestring)):
        if isctrl(bytestring[i:i + 1]):
            return True
    return False


def removeControlCharacters(string):
    """Remove control characters from string.

    Adapted from: http://stackoverflow.com/a/19016117/1209004
    """
    # Tab, newline and return are part of C0, but are allowed in XML
    allowedChars = [u'\t', u'\n', u'\r']
    return "".join(ch for ch in string if unicodedata.category(ch)[
                   0] != "C" or ch in allowedChars)


def removeNullTerminator(bytestring):
    """Remove null terminator from bytestring."""
    bytesOut = bytestring.rstrip(b'\x00')
    return bytesOut


def bytesToText(bytestring):
    """Unpack byte object to text string, assuming big-endian byte order."""
    # Set encoding and error mode
    enc = "utf-8"
    errorMode = "strict"

    try:
        # Decode to utf-8
        string = bytestring.decode(encoding=enc, errors=errorMode)

        # Remove control characters
        result = removeControlCharacters(string)

    except BaseException:
        # Return empty string if bytestring cannot be decoded
        result = ""

    return result
