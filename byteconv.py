from curses.ascii import isctrl
import struct

# Convert bytestr of bOrder byteorder to format using formatCharacter
# Return -9999 if unpack raised an error
def __doConv__(bytestr, bOrder, formatCharacter):
	# Format string for unpack
	formatStr=bOrder+formatCharacter
	try:
		result=struct.unpack(formatStr,bytestr)[0]
	except:
		result=-9999
	return(result)

def strToULongLong(str):
	# Unpack 8 byte string to unsigned long long integer, assuming big-endian byte order.
	return __doConv__(str, ">", "Q")

def strToUInt(str):
	# Unpack 4 byte string to unsigned integer, assuming big-endian byte order.
	return __doConv__(str, ">", "I")

def strToUShortInt(str):
	# Unpack 2 byte string to unsigned short integer, assuming big-endian  byte order
	return __doConv__(str, ">", "H")

def strToUnsignedChar(str):
	# Unpack 1 byte string to unsigned character/integer, assuming big-endian  byte order.
	return __doConv__(str, ">", "B")

def strToSignedChar(str):
	# Unpack 1 byte string to signed character/integer, assuming big-endian byte order.
	return __doConv__(str, ">", "b")

def strToText(str):
	# Unpack byte string to text string, assuming big-endian
	# byte order.

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
	if any(isctrl(c) for c in str):
		# Return empty string
		result=""
	else:
		try:
			result=str.decode(encoding=enc,errors=errorMode)
		except:
			# We end up here if str is part of extended ASCII (or Latin) set (char 129-255)
			# Return empty string
			result=""

	return(result)
