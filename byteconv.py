import struct
import binascii

# Convert byte object of bOrder byteorder to format using formatCharacter
# Return -9999 if unpack raised an error
def _doConv(bytestr, bOrder, formatCharacter):
	# Format string for unpack
	formatStr=bOrder+formatCharacter
	try:
		result=struct.unpack(formatStr,bytestr)[0]
	except:
		result=-9999
	return(result)

def bytesToULongLong(bytes):
	# Unpack 8 byte string to unsigned long long integer, assuming big-endian byte order.
	return _doConv(bytes, ">", "Q")

def bytesToUInt(bytes):
	# Unpack 4 byte string to unsigned integer, assuming big-endian byte order.
	return _doConv(bytes, ">", "I")

def bytesToUShortInt(bytes):
	# Unpack 2 byte string to unsigned short integer, assuming big-endian  byte order
	return _doConv(bytes, ">", "H")

def bytesToUnsignedChar(bytes):
	# Unpack 1 byte string to unsigned character/integer, assuming big-endian  byte order.
	return _doConv(bytes, ">", "B")

def bytesToSignedChar(bytes):
	# Unpack 1 byte string to signed character/integer, assuming big-endian byte order.
	return _doConv(bytes, ">", "b")

def isctrl(c):
	# Returns True if byte corresponds to device control character
	# (See also: http://www.w3schools.com/tags/ref_ascii.asp)
	return (ord(c) < 32 or ord(c)==127)
	#return (0 <= ord(c) <= 8) or (ord(c) == 12) or (14 <= ord(c) < 32)
	
def bytesToHex(bytes):
	# Return hexadecimal ascii representation of bytes
	return binascii.hexlify(bytes)

def containsControlCharacters(bytes):
	# Returns True if bytes object contains control characters

	for i in range(len(bytes)):
		if isctrl(bytes[i:i+1]):
			return(True)
	return(False)	

def replaceControlCharacters(bytes):
	# Replace all occurrences of device control characters with
	# replaceByte

	# Set replacement byte for device control characters (*must* be a bytes
	# object, if not this won't work under Python 3!)
	replaceByte=b'*'
	
	# Output bytes object
	bytesOut=b''
	
	for i in range(len(bytes)):
		
		byteIn=bytes[i:i+1]
		
		if isctrl(byteIn):
			bytesOut=bytesOut + replaceByte
		else:
			bytesOut=bytesOut+byteIn

	return(bytesOut)

def bytesToText(bytes):
	# Unpack byte object to text string, assuming big-endian
	# byte order.
	
	# Set encoding
	enc="ascii"

	# Set error mode
	errorMode="strict"
	
	# Check if bytes object contains bytes that correspond to device control characters,
	# which are not allowed in XML
	
	if containsControlCharacters(bytes):
		# Return empty string
		result=""
		
	else:
		try:
			result=bytes.decode(encoding=enc,errors=errorMode)
			
		except:
			# Return empty string
			result=""
			
	return(result)