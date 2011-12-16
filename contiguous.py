# Search list for occurrences of 'value', and return list
# of matching index positions in souurce list
def __allIndexesOf__(list, value):
	matchIndices = []
	numberOfElements= len(list)

	for i in range(numberOfElements):
		if list[i]==value:
			matchIndices.append(i)

	return matchIndices

# Takes list and returns True if items are consecutive numbers,
# and False otherwise
def listContainsConsecutiveNumbers(list):
	containsConsecutiveNumbers = True
	numberOfElements = len(list)
	try:
		for i in range(1,numberOfElements):
			if list[i] - list[i-1] != 1:
				containsConsecutiveNumbers=False
	except:
		containsConsecutiveNumbers=False
	return containsConsecutiveNumbers

# Returns True if occurrences of 'value' in list are contiguous, and
# "False otherwise"
def listOccurrencesAreContiguous(list,value):   
	# Create list with index values of all occurrences of 'value'
	indexValues = __allIndexesOf__(list,value)
	# If index values are a sequence of consecutive numbers this means that
	# all occurrences of 'value' are contiguous
	return listContainsConsecutiveNumbers(indexValues)

