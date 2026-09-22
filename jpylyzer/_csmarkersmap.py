"""Marker tags/codes that identify all markers and marker segments as hexadecimal strings.
These correspond to values in  Table A.2 (List of markers and marker segments) of ISO/IEC 15444-1
"""

typeMap = {
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
