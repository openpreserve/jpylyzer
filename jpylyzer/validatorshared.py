"""Shared functions for Jpylyzer validator classes."""
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

from . import byteconv as bc

def getBox(validator, byteStart, noBytes):
    """Parse JP2 box and return information on its size, type and contents."""
    # Box length (4 byte unsigned integer)
    boxLengthValue = bc.bytesToUInt(
        validator.boxContents[byteStart:byteStart + 4])

    # Box type
    boxType = validator.boxContents[byteStart + 4:byteStart + 8]

    # Start byte of box contents
    contentsStartOffset = 8

    # Read extended box length if box length value equals 1
    # In that case contentsStartOffset must also be 16 (not 8!)
    # (See ISO/IEC 15444-1 Section I.4)
    if boxLengthValue == 1:
        boxLengthValue = bc.bytesToULongLong(
            validator.boxContents[byteStart + 8:byteStart + 16])
        contentsStartOffset = 16

    # For the very last box in a file boxLengthValue may equal 0, so we need
    # to calculate actual value
    if boxLengthValue == 0:
        boxLengthValue = noBytes - byteStart

    # End byte for current box
    byteEnd = byteStart + boxLengthValue

    # Contents of this box as a byte object (i.e. 'DBox' in ISO/IEC 15444-1
    # Section I.4)
    boxContents = validator.boxContents[byteStart + contentsStartOffset:byteEnd]

    return (boxLengthValue, boxType, byteEnd, boxContents)


def getMarkerSegment(validator, offset):
    """Read marker segment that starts at offset.

    Return marker, size, contents and start offset of next marker.
    """
    # First 2 bytes: 16 bit marker
    marker = validator.boxContents[offset:offset + 2]

    # Check if this is a delimiting marker segment
    if marker in [b'\xff\x4f', b'\xff\x93', b'\xff\xd9', b'\xff\x92']:
        # Zero-length markers: SOC, SOD, EOC, EPH
        length = 0
    else:
        # Not a delimiting marker, so remainder contains some data
        length = bc.bytesToUShortInt(
            validator.boxContents[offset + 2:offset + 4])

    # Contents of marker segment (excluding marker) to binary string
    contents = validator.boxContents[offset + 2:offset + 2 + length]

    if length == -9999:
        # If length couldn't be determined because of decode error,
        # return bogus value for offsetNext (calling function should
        # handle this further!)
        offsetNext = -9999

    else:
        # Offset value start of next marker segment
        offsetNext = offset + length + 2

    return (marker, length, contents, offsetNext)

def calculateCompressionRatio(noBytes, bPCDepthValues, height, width):
    """Compute compression ratio.

    - noBytes: size of compressed image in bytes
    - bPCDepthValues: list with bits per component for each component
    - height, width: image height, width
    """
    # Total bits per pixel
    bitsPerPixel = 0

    for i in range(len(bPCDepthValues)):
        bitsPerPixel += bPCDepthValues[i]

    # Convert to bytes per pixel
    bytesPerPixel = bitsPerPixel / 8

    # Uncompressed image size
    sizeUncompressed = bytesPerPixel * height * width

    # Compression ratio
    if noBytes != 0:
        compressionRatio = sizeUncompressed / noBytes
    else:
        # Obviously something going wrong here ...
        compressionRatio = -9999

    return compressionRatio

