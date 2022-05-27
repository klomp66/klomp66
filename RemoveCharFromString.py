##########################################
# RemoveCharFromString
# Removes unwanted characters from a string
###########################################


def _removeUnwantedChar(string, badChar):
	# how long is this string
	strLen = len(string)

	# at what location is the bad char
	bcIndex = string.find(badChar)

	# if the bad char is found
	if bcIndex != -1:
		# Prefix is everything before the bad char
		Prefix = string[0:bcIndex-1]

		# Suffix is everything after the bad char, remember index starts at 0 so the final index
		# is the length of the string -1
		Suffix = string[bcIndex+1 : strLen-1]

		# reassemble without the bad Char
		newString = '%s%s' %(Prefix, Suffix)

		return newString

	return string



