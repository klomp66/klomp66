########################################
# GMN_Code_CheckDigit
# Created: July 20, 2020 JvS
#
# Calculate the check digit of any 23 digit GMN Code
#########################################

# This is full 25 char test GMU
testGMU1 = '1987654Ad4X4bL5ttr2310c2K'
testGMU2 = '1987654Ad4X4bL5ttr2310c'

def _calculateGMNCheckDigits(gmnCode, checkDigitsIncluded=False):
    print("Calculating Check Digits for GMN Code %s, checkdigits included = %s" %(gmnCode, checkDigitsIncluded))
    # need to complete filling in TABLE_1 all the way from 0 through 81
    TABLE_1 = [["!", 0], \
               ['"', 1], \
               ["%", 2], \
               ["&", 3], \
               ["'", 4], \
               ["(", 5], \
               [")", 6], \
               ["*", 7], \
               ["+", 8], \
               [",", 9], \
               ["-", 10], \
               [".", 11], \
               ["/", 12], \
               ["0", 13], \
               ["1", 14], \
               ["2", 15], \
               ["3", 16], \
               ["4", 17], \
               ["5", 18], \
               ["6", 19], \
               ["7", 20], \
               ["8", 21], \
               ["9", 22], \
               [":", 23], \
               [";", 24], \
               ["<", 25], \
               ["=", 26], \
               [">", 27], \
               ["?", 28], \
               ["A", 29], \
               ["B", 30], \
               ["C", 31], \
               ["D", 32], \
               ["E", 33], \
               ["F", 34], \
               ["G", 35], \
               ["H", 36], \
               ["I", 37], \
               ["J", 38], \
               ["K", 39], \
               ["L", 40], \
               ["M", 41], \
               ["N", 42], \
               ["O", 43], \
               ["P", 44], \
               ["Q", 45], \
               ["R", 46], \
               ["S", 47], \
               ["T", 48], \
               ["U", 49], \
               ["V", 50], \
               ["W", 51], \
               ["X", 52], \
               ["Y", 53], \
               ["Z", 54], \
               ["_", 55], \
               ["a", 56], \
               ["b", 57], \
               ["c", 58], \
               ["d", 59], \
               ["e", 60], \
               ["f", 61], \
               ["g", 62], \
               ["h", 63], \
               ["i", 64], \
               ["j", 65], \
               ["k", 66], \
               ["l", 67], \
               ["m", 68], \
               ["n", 69], \
               ["o", 70], \
               ["p", 71], \
               ["q", 72], \
               ["r", 73], \
               ["s", 74], \
               ["t", 75], \
               ["u", 76], \
               ["v", 77], \
               ["w", 78], \
               ["x", 79], \
               ["y", 80], \
               ["z", 81]  \
               ]
    # Create a dictionary object ("Set") to hold the TABLE1 values for easy reference
    characterValues = {}

    for row in TABLE_1:
        characterValues[row[0]] = row[1]
        
    # Create a dictionary object to Assign Weights:
    weightVals = {}

    weightVals[-23] = 83
    weightVals[-22] = 79
    weightVals[-21] = 73
    weightVals[-20] = 71
    weightVals[-19] = 67
    weightVals[-18] = 61
    weightVals[-17] = 59
    weightVals[-16] = 53
    weightVals[-15] = 47
    weightVals[-14] = 43
    weightVals[-13] = 41
    weightVals[-12] = 37
    weightVals[-11] = 31
    weightVals[-10] = 29
    weightVals[-9] = 23
    weightVals[-8] = 19
    weightVals[-7] = 17
    weightVals[-6] = 13
    weightVals[-5] = 11
    weightVals[-4] = 7
    weightVals[-3] = 5
    weightVals[-2] = 3
    weightVals[-1] = 2

    if checkDigitsIncluded == False:
        gmnCodeLength = len(gmnCode)
        if gmnCodeLength >= 24:
            gmnCode = gmnCode[0:(len(gmnCode) - 2)]
            gmnCodeLength = len(gmnCode)
    
    if checkDigitsIncluded == True:
        gmnCode = gmnCode[0:(len(gmnCode) - 2)]
        gmnCodeLength = len(gmnCode)
        
    print("Length of the string %s is: %s" %(gmnCode, gmnCodeLength))
    
    # now we can just loop through the first 23 chars in string
    counter = 0
    sum = 0
    for charVal in gmnCode:
        counter += 1
        positionFromEnd = (counter - 1) - gmnCodeLength
        print("Working on character %s in %s, position from the end is %s" %(charVal, gmnCode, positionFromEnd))
        if counter == 24:
            break
        subtotal = (characterValues[charVal] * weightVals[positionFromEnd])
        print("Translated value for character %s is %s, and the weight is %s" %(charVal, characterValues[charVal], weightVals[positionFromEnd]))
        sum = sum + subtotal

    # sum is now the sum that you need to work with.
    SUM = sum
    print("Sum: %s" %(SUM))

    # Remainder is "MOD" (modulus) in Python is the % sign
    REMAINDER = SUM % 1021
    print("Remainder: %s" %(REMAINDER))

    # Integer value of REMAINDER / 32 is the first lookup for table 2
    CHKDIGIT1_INTEGER = int(REMAINDER / 32)
    print("First Check Digit lookup value: %s" %(CHKDIGIT1_INTEGER))

    # Not too sure about how the second one is structured, but giving this a try:
    # The only way I can see this working to get the values shown in the PDF calculation example,
    # is to use the value of REMAINDER as the check digit 2 lookup value.
    CHKDIGIT2_INTEGER = REMAINDER % 32
    print("Second Check Digit lookup value: %s" %(CHKDIGIT2_INTEGER))

    # Now we need TABLE_2 to look up the values to get the actual check digits...
    TABLE_2 = [["2", 0], \
         ["3", 1], \
         ["4", 2], \
         ["5", 3], \
         ["6", 4], \
         ["7", 5], \
         ["8", 6], \
         ["9", 7], \
         ["A", 8], \
         ["B", 9], \
         ["C", 10], \
         ["D", 11], \
         ["E", 12], \
         ["F", 13], \
         ["G", 14], \
         ["H", 15], \
         ["J", 16], \
         ["K", 17], \
         ["L", 18], \
         ["M", 19], \
         ["N", 20], \
         ["P", 21], \
         ["Q", 22], \
         ["R", 23], \
         ["S", 24], \
         ["T", 25], \
         ["U", 26], \
         ["V", 27], \
         ["W", 28], \
         ["X", 29], \
         ["Y", 30], \
         ["Z", 31] \
         ]
    
    assignedValues = {}


    for row1 in TABLE_2:
        assignedValues[row1[1]] = row1[0]
    checkDigits = [CHKDIGIT1_INTEGER, CHKDIGIT2_INTEGER]

    #Charset value for C1
    counter = 0
    for assignVal in checkDigits:
       C1 = (assignedValues[assignVal])
       counter += 1
       if counter == 1:
           break
    print("C1 = %s" %(C1))

    #Charset value for C2
    counter = 0
    for assignVal in checkDigits:
       counter += 1
       C2 = (assignedValues[assignVal])
    print("C2 = %s" %(C2))
    
    print('FINISH RUNNING GMN-CheckDigits-Calculation Rule')
    
    fullGMNCode = "%s%s%s" %(gmnCode, C1, C2)
    
    return fullGMNCode, C1, C2

try:
    BUDI_DI, chkDgt1, chkDgt2 = _calculateGMNCheckDigits(testGMU1)
    print("Full BUDI_DI1 number is: %s" %(BUDI_DI))
    BUDI_DI2, chkDgt1, chkDgt2 = _calculateGMNCheckDigits(testGMU1, True)
    print("Full BUDI_DI2 number is: %s" %(BUDI_DI2))
    BUDI_DI3, chkDgt1, chkDgt2 = _calculateGMNCheckDigits(testGMU2, False)
    print("Full BUDI_DI3 number is: %s" %(BUDI_DI3))
    
except:
    print("Oh Snap")
