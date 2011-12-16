import byteconv as bc
import unittest


class ByteConvTest(unittest.TestCase):
	def test_strToULongLong(self):
		self.assertEqual(bc.strToULongLong(b'\x0e\x0f\x10\x11\x0e\x0f\x10\x10'), 1013046106618007568)
	def test_strToULongLong_fail(self):
		self.assertEqual(bc.strToULongLong(b'\x0e\x0f\x10\x11\x0e\x0f\x10'), -9999)

	def test_strToUInt(self):
		self.assertEqual(bc.strToUInt(b'\x0e\x0f\x10\x11'), 235868177)
	def test_strToUInt_fail(self):
		self.assertEqual(bc.strToUInt(b'\x0e\x0f\x10\x11\x0e\x0f\x10'), -9999)

	def test_strToUShortInt(self):
		self.assertEqual(bc.strToUShortInt(b'\x0e\x0f'), 3599)
	def test_strToUShortInt_fail(self):
		self.assertEqual(bc.strToUShortInt(b'\x0e\x0f\x0e'), -9999)

	# strToUnsignedChar
	def test_strToUnsignedChar(self):
		self.assertEqual(bc.strToUnsignedChar(b'\x0e'), 14)
	def test_strToUnsignedChar_fail(self):
		self.assertEqual(bc.strToUnsignedChar(b'\x0e\x0f\x0e'), -9999)

	# strToSignedChar
	def test_strToSignedChar(self):
		self.assertEqual(bc.strToSignedChar(b'\x0e'), 14)
	def test_strToSignedChar_fail(self):
		self.assertEqual(bc.strToSignedChar(b'\x0e\x0f\x0e'), -9999)

	# strToText
	def test_strToText(self):
		self.assertEqual(bc.strToText(b'\x44\x41\x44\x44\x59'), "DADDY")
	def test_strToText_fail(self):
		self.assertEqual(bc.strToText(b'\x0e\x0f\x10\x11\x0e\x0f\x10\x10'), "")

if __name__ == '__main__':
	unittest.main()
