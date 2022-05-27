########################################
# GTIN_CheckDigit
# Created: July 20, 2020 JvS
#
# Calculate the check digit of any length GTIN
#########################################

testGtin1 = '00613994187451'
testGtin2 = '29310640000713'

def calcGTINCheckDigit(gtin):
	print("GTIN Length:", len(gtin))
	digit = []
	# Append each digit to a list
	for n in range(len(gtin) - 1):
		digit.append(gtin[n])

	sum = 0

	# Now cycle through the digits and do the math
	for n in range(len(gtin) - 1):
		# If the length is an odd number...
		if len(gtin) % 2 == 1:
			if (n % 2) == 0:
				sum += int(digit[n])
			else:
				sum += (3 * int(digit[n]))
		else:
			# the length is an even number, bump the multiplier forwards
			if (n % 2) == 0:
				sum += (3 * int(digit[n]))
			else:
				sum += int(digit[n])

	checkDigit = 10 - (sum % 10)
	print("Check Digit should be:", checkDigit)
	return checkDigit


nCD1 = calcGTINCheckDigit(testGtin1)
print(testGtin1[-1:])
if int(testGtin1[-1:]) == nCD1:
	print("Correct Check Digit")
else:
	print("Incorrect check digit, should be:", nCD1)

nCD2 = calcGTINCheckDigit(testGtin2)
print(testGtin2[-1:])
if int(testGtin2[-1:]) == nCD2:
	print("Correct Check Digit")
else:
	print("Incorrect check digit, should be:", nCD2)
