
def isctrl(c):
	# This doesn't work in Python 3!!
	#return (0 <= ord(c) <= 8) or (ord(c) == 12) or (14 <= ord(c) < 32)
	
	# Revert to previous method - ugly but it works!
	controlChars={b'\x00',b'\x01',b'\x02',b'\x03',b'\x04',b'\x05',b'\x06',b'\x07', \
		b'\x08',b'\x0b',b'\x0c',b'\x0e',b'\x0f',b'\x10',b'\x11',b'\x12',b'\x13',b'\x14', \
		b'\x15',b'\x16',b'\x17',b'\x18',b'\x19',b'\x1a',b'\x1b',b'\x1c',b'\x1d',b'\x1e', \
		b'\x1f'}
	
	return c in controlChars

def isctrlAlt(c):

	"""
	if type(c)=='str':
		byteValue=ord(c)
	else:
		byteValue=c
	
	"""
	
	byteValue=ord(c)
	
	print(byteValue,type(byteValue))
	return (0 <= byteValue <= 8) or (byteValue == 12) or (14 <= byteValue < 32)

def main():
	str=b'\x00\x63\x6c\x72'
	#str="jp123"
	#str=b'\x00'
	print(type(str))
	
	for c in str: print(c,isctrl(c))
	print("----")
	
	for c in str: print(c,isctrlAlt(c))
	
	#print(any(isctrl(c) for c in str))
	#print(isctrl(str))

if __name__ == "__main__":
	main()
