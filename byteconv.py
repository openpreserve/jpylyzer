import struct

# Convert bytestr of bOrder byteorder to format using formatCharacter
# Return -9999 if unpack raised an error
def _doConv(bytestr, bOrder, formatCharacter):
	# Format string for unpack
	formatStr=bOrder+formatCharacter
	try:
		result=struct.unpack(formatStr,bytestr)[0]
	except:
		result=-9999
	return(result)

def strToULongLong(str):
	# Unpack 8 byte string to unsigned long long integer, assuming big-endian byte order.
	return _doConv(str, ">", "Q")

def strToUInt(str):
	# Unpack 4 byte string to unsigned integer, assuming big-endian byte order.
	return _doConv(str, ">", "I")

def strToUShortInt(str):
	# Unpack 2 byte string to unsigned short integer, assuming big-endian  byte order
	return _doConv(str, ">", "H")

def strToUnsignedChar(str):
	# Unpack 1 byte string to unsigned character/integer, assuming big-endian  byte order.
	return _doConv(str, ">", "B")

def strToSignedChar(str):
	# Unpack 1 byte string to signed character/integer, assuming big-endian byte order.
	return _doConv(str, ">", "b")

def isctrl(c):
	# This doesn't work in Python 3! Behaviour varies depending on whether
	# c is part of text string or bytes string, and I've already wasted far
	# too much time on this! For now we'll fall back on the
	# old and ugly containsControlCharacters function below ...
	return (0 <= ord(c) <= 8) or (ord(c) == 12) or (14 <= ord(c) < 32)
	
def containsControlCharacters(str):
    # Returns True if str contains control characters

    controlChars={b'\x00',b'\x01',b'\x02',b'\x03',b'\x04',b'\x05',b'\x06',b'\x07', \
        b'\x08',b'\x0b',b'\x0c',b'\x0e',b'\x0f',b'\x10',b'\x11',b'\x12',b'\x13',b'\x14', \
        b'\x15',b'\x16',b'\x17',b'\x18',b'\x19',b'\x1a',b'\x1b',b'\x1c',b'\x1d',b'\x1e', \
        b'\x1f'}

    containsControlCharacters=False
    
    for c in controlChars:
        if c in str:
            containsControlCharacters=True
            
    return(containsControlCharacters)	

def strToText(str):
	# Unpack byte string to text string, assuming big-endian
	# byte order.
	
	# Would perhaps be better to call this function 'bytesToText'!

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
	
	if containsControlCharacters(str):
		# Return empty string
		result=""

	else:
		try:
			result=str.decode(encoding=enc,errors=errorMode)
			
		except:
			# Return empty string
			result="Rubbish"
			
	return(result)