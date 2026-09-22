
"""Marker tags/codes that identify all boxes and sub-boxes as hexadecimal strings.
These correspond to values in  Table I.4 (Defined boxes) of ISO/IEC 15444-1
"""
typeMap = {
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
