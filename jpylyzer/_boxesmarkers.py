#! /usr/bin/env python3

"""Marker tags/codes that identify all boxes, sub-boxes and marker segments
as hexadecimal strings.
"""

# Boxes, sub-boxes. These correspond to values in  Table I.4 (Defined boxes) of ISO/IEC 15444-1

boxTypeMap = {
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
    'icc': 'icc'
}

# Codestream marker segments. These correspond to values in  Table A.2
# (List of markers and marker segments) of ISO/IEC 15444-1

markerTypeMap = {
    b'\xff\x50': "cap",
    b'\xff\x51': "siz",
    b'\xff\x56': "prf",
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
    b'\xff\x59': "cpf",
    b'\xff\x60': "ppm",
    b'\xff\x61': "ppt",
    b'\xff\x63': "crg",
    b'\xff\x90': "tilePart",
    'startOfTile': 'sot'
}
