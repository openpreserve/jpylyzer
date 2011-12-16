import xml.etree.ElementTree as ET

def tostring(elem, enc):
	return ET.tostring(elem, enc)

def SubElement(parent, tag):
	return ET.SubElement(parent, tag)

class Element(ET.Element):

	pass
	# Replacement for ET's 'findtext' function, which has a bug
	# that will return empty string if text field contains integer with
	# value of zero (0); If there is no match, return None
	def findElementText(self, match):
		elt = self.find(match)
		if elt is not None:
			return elt.text
		else:
			return None

	# Searches element and returns list that contains 'Text' attribute
	# of all matching sub-elements. Returns empty list if element
	# does not exist
	def findAllText(self, match):
		try:
			return [result.text for result in self.findall(match)]
		except:
			return []
