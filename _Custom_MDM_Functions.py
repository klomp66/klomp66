###################################
# Custom-MDM-Functions
# Created by: Jeff Ursino
# Updated/cleaned up for MC by: Jeff vS
# Date: June 2, 2020
# Description:
# Common utility functions used for this client implementation
#
# Modification log:
# 04/02/16 Jeff U: Created this file
# 08/02/16 Jeff U: Update to use composite attributes and process UDI attributes
# 18/02/16 Jeff U: INNOV-115 added code to clean up SAP_MASTER and delete related dynamic records before re-importing
# 18/02/16 Amit: INNOV-115 Following Jeff's enhancement, added code to also delete related ATWRT_TEXT records before re-importing
# 19/02/16 Jeff U: INNOV-115 Removed adding error to SAP_MASTER for missing attributes
# 25/02/16 Amit: INNOV-81 Added functions to support population of ATWRT_TEXT values in SAP_MASTER
# June 2, 2020 JvS: Set up for Mayo Clinic
###################################

import sys, traceback
sys.add_package('com.innovit.util')
sys.add_package('com.innovit.id')
sys.add_package('com.innovit.iice.extension.connector.gdsn.report')
sys.add_package('com.innovit.ice.report')

from java.util import List
from java.util import ArrayList
from java.util import Date
from java.util import Calendar
from java.io import File
from java.lang import System
from com.innovit.id import ObjId
from com.innovit.ice.common import AttributeFactory
from java.util import HashMap
from java.util import Map
from com.innovit.util import ObjectTuple
from com.innovit.util import IOUtils
from com.innovit.id import ObjId
from com.innovit.ice.common.search import SearchConstants
from com.innovit.iice.extension.connector.gdsn.report import GS1EventTypes
from com.innovit.ice.report import EventTypeProperties
from com.innovit.ice.report import SummaryEventTypes

runEditRuleWithName('Health_Constants_and_Functions')

# Constants to control printing of debug lines.
cmc_PRINT_ON = True
cmc_DEBUG_ON = False

cmc_PRIMARY_ORG_CODE = 'MC_GLOBAL'

ORG_ID = getCurrentOrganisationId()
ORG_CODE = getOrganisationAttributeValue(ORG_ID, "Organisation Code")
ORG_NAME = getOrganisationAttributeValue(ORG_ID, "Organisation Name")

validationOntologyName = 'Consolidated_Import_Item'
validationAttrNameList = getOntologyAttributeNames(validationOntologyName)

def cmf_getAttrsToIgnore():

    ignoreAttrNames = IGNORE_ATTR_NAMES

    ignoreAttrIds = []

    for attrName in ignoreAttrNames:
        ignoreAttrIds.append(getAttributeId(attrName))

    return ignoreAttrIds, ignoreAttrNames


def cmf_setValidationStatus(nodeId):

    cmf_printDebug("Setting the validation Status now")
    validationPassed = True

    for attrName in validationAttrNameList:
        cmf_printDebug("Checking attribute %s for errors" %(attrName))
        if isAttributeInError(nodeId, attrName):
            cmf_printDebug("attribute %s is in error, validation fails" %(attrName))
            validationPassed = False
            break

    cmf_print("Validation status is %s" %(validationPassed))

    if not validationPassed:
        setAttributeValue(nodeId, 'validationStatus', 'Validated - Failed')
    else:
        setAttributeValue(nodeId, 'validationStatus', 'Validated - Passed')
        _removeGreenBoxes(nodeId, 'Consolidated_Import_Item')
    setAttributeValue(nodeId, "Merged", False)
    return True


# Central print function, used to print errors/warnings
def cmf_print(message):
    if (cmc_PRINT_ON):
        # print cmf_removeNonASCII(message)
        printMessage = "%s: %s" %(ORG_CODE, message)
        System.out.println(printMessage)

# Central print function, used to print debug
def cmf_printDebug(message, params=None):
    # set to False to turn off debug messages
    if (cmc_DEBUG_ON):
        if (params not in [None, ''] and len(params) > 0):
            cmf_print("Unsupported 'params' argument in cmf_printDebug for message: %s" % (message))
            # todo construct the print statement using the 'message' %(params)
        # print "DEBUG: %s" %(cmf_removeNonASCII(message))
        debugMsg = "DEBUG %s: %s" % (ORG_CODE, message)
        System.out.println(debugMsg)

def cmf_createUniqueMasterKey(cPrefix):
    dummyValue = int(getNextAutoIncrementValue('PIM_ID_Counter'))
    firstDigit = "1"
    remainingDigits = str(dummyValue)
    secondPart = _padAnyGTIN(remainingDigits, 9)
    uniqueKey = "%s_%s%s" % (cPrefix, firstDigit, secondPart)
    cmf_printDebug("New Unique Key created: %s" % (uniqueKey))
    return uniqueKey

def cmf_createUniqueKey(cPrefix):
    dummyValue = Date().getTime()
    uniqueKey = "%s_%s" % (cPrefix, dummyValue)
    cmf_printDebug("New Unique Key created: %s" % (uniqueKey))
    return uniqueKey

def chunks(my_list, n):
    # Cameron's gonna love this
    return [my_list[i * n:(i + 1) * n] for i in range((len(my_list) + n - 1) // n)]

def _padAnyGTIN(stringVal, numChar):
    strLen = len(str(stringVal))
    ndiff = numChar - strLen
    newStringVal = ""

    if ndiff <= 0:
        return stringVal
    else:
        for x in range(0, ndiff):
            newStringVal = "0" + str(stringVal)
            stringVal = newStringVal

    return newStringVal

def cmf_parsePrefixToFirstDelim(textString, delim):
    if textString not in [None, ""]:
        for i in range(0, len(textString)):
            if textString[i] == delim:
                return textString[0:i]
    return textString

def cmf_parseBetweenTwoDelim(textString, delim1, delim2):
    if textString not in [None, ""]:
        for i in range(0, len(textString)):
            if textString[i] == delim1:
                firstPos = i+1
                for j in range(firstPos, len(textString)):
                    if textString[j] == delim2:
                        lastPos = j
                        return textString[firstPos:lastPos]
    return textString

def cmf_CalcGTINCheckDigit(gtin):
    cmf_printDebug("GTIN Length: %s" %(len(gtin)))
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

    if checkDigit == 10:
        checkDigit = 0

    cmf_printDebug("Check Digit should be %s" %(checkDigit))
    return checkDigit

def isComposite(attrName):
    if(getAttributeType(attrName) == 9989): #Composite attribute
        return True
    return False

def isGrouped(attrName):
    if(getAttributeType(attrName) == 9991): #Grouped attribute
        return True
    return False

def getChildAttributeNames(parentAttributeName):
    from com.innovit.id import ObjId
    from com.innovit.ice.common import AttributeFactory
    attributeManager = AttributeFactory.getInstance()
    parentAttributeId = getAttributeId(parentAttributeName)
    childAttributeObjIds = attributeManager.getChildAttrIdsByParent(ObjId(parentAttributeId))
    childAttributeNames = []
    for childAttributeObjId in childAttributeObjIds:
        childAttributeFullName = getAttributeName(childAttributeObjId.getPkAttribute())
        childAttributeNames.append(childAttributeFullName[-1])
    return childAttributeNames

def _cmf_copyCompositeMultiValues(nodeId1, attrNameGroup, nodeId2, force=False):
    # Assumption and must be asserted that nodeId2 contains the same attrNameGroup
    # the "Force" option will copy even if the "get" values are non existent.  Otherwise, there must be at least one value in order to copy and record success
    success = False
    if isGrouped(attrNameGroup) or isComposite(attrNameGroup):
        cmf_printDebug("Attribute Name: %s is grouped or composite, proceeding" % (attrNameGroup))
        childNames = getChildAttributeNames(attrNameGroup)
        attrNameList = []

        for childAttrName in childNames:
            attrNameSub = []
            attrNameSub.append(attrNameGroup)
            attrNameSub.append(childAttrName)
            attrNameList.append(attrNameSub)

        for attrName in attrNameList:
            attrValueList = []
            attrValueList = getAttributeMultiValues(nodeId1, attrName)
            if force == True:
                setAttributeMultiValues(nodeId2, attrName, attrValueList)
                success = True
            else:
                #This could stand to be cleaned up a bit, to check each value in the list for [None, ""]
                if attrValueList != None and len(attrValueList) >= 1:
                    for i in range(len(attrValueList)):
                        setAttributeValueByIndex(nodeId2, attrName, attrValueList[i], i)
                    success = True
                else:
                    cmf_printDebug("The values in the source composite record are empty, nothing copied.")

    else:
        cmf_print("Retrieving Composite MultiValues failure, attribute %s is not composite or grouped attribute" % (attrNameGroup))

    return success

def _greenBoxANode(nodeId, ontologyName, ignoreAttrNameList=None, processName='gs1'):
    if ignoreAttrNameList is None:
        ignoreAttrNameList = []

    attrNameList = [] # getOntologyAttributeNames(ontologyName)
    attrIdList = getOntologyAttributeIds(ontologyName)
    changesFound = False
    attrUpdateState = ""
    recordUpdateStatus = getUpdateState(nodeId, processName)

    for attrId in attrIdList:
        attrName = getAttributeName(attrId)[0]
        cmf_printDebug("Green Box check on attribute name: %s" %(attrName))
        childAttrNameList = []
        bIsComposite = isComposite(attrName)
        bIsGrouped = isGrouped(attrName)
        attributeId = getAttributeId(attrName)
        bIsMultiValue = isAttributeMultiValue(attributeId)
        bIsCombo = False
        if bIsComposite or bIsGrouped:
            bIsCombo = True

        if not bIsMultiValue:
            if not bIsCombo:
                if attrName not in ignoreAttrNameList:
                    cmf_printDebug('Checking update state of attribute: %s' % (attrName))
                    attrUpdateState = getAttributeUpdateState(nodeId, processName, attrName)
                    cmf_printDebug("attrUpdateState  is: %s" % (attrUpdateState))
                    if attrUpdateState == "C":  # Changed
                        changesFound = True
                        message = "Attribute %s has changed to %s" % (attrName, getAttributeValue(nodeId, attrName))
                        addInfoMessage(nodeId, attrName, message, 0)
                    elif attrUpdateState == "A":
                        changesFound = True
                        message = "Attribute is new"
                        addInfoMessage(nodeId, attrName, message, 0)
            else:
                cmf_printDebug('Checking update state of attribute: %s' % (attrName))
                childAttrNameList = getChildAttributeNames(attrName)
                for index in range(len(childAttrNameList)):
                    attrNameFull = [attrName, childAttrNameList[index]]
                    if attrNameFull not in ignoreAttrNameList:
                        attrUpdateState = getAttributeUpdateState(nodeId, processName, attrNameFull)
                        cmf_printDebug("attrUpdateState  is: %s" % (attrUpdateState))
                        if attrUpdateState == "C":  # Changed
                            changesFound = True
                            message = "Attribute %s has changed to %s" % (attrName, getAttributeValue(nodeId, attrNameFull))
                            addInfoMessage(nodeId, attrNameFull, message, 0)
                        elif attrUpdateState == "A":
                            changesFound = True
                            message = "Attribute is new"
                            addInfoMessage(nodeId, attrNameFull, message, 0)

    resetAttributesUpdateState(nodeId, processName, attrIdList)
    resetUpdateState(nodeId, processName)
    return recordUpdateStatus


def _removeGreenBoxes(nodeId, ontologyName):

    attrNameList = getOntologyAttributeNames(ontologyName)

    for attrName in attrNameList:
        messages = getInfoMessages(nodeId, attrName, 0)

        if messages != None and len(messages) > 0:
            for message in messages:
                removeInfoMessage(nodeId, attrName, message, 0)

    return None

def _createReplicationKeyCache(keyMapFileName, gtinOnly = True):
    # This map is used to compare the XML files, and only allow the XML records if the keys are found in this keyCache
    keyCache = {}

    try:
        cmf_print("_createReplicationKeyCache called, starting...")
        lines = [line.strip() for line in open(keyMapFileName)]
        for line in lines:
            if not gtinOnly:
                lineList = line.split("`")
                keyCache[lineList[0]] = int(lineList[1])
            else:
                if "|" in line:
                    pass
                else:
                    # the GTIN is separated from the nodeId containing that GTIN by a comma, add the nodeId to the map value
                    # NOTE the nodeId (value) needs to be converted to "int" before it works on the other end.
                    lineList = line.split("`")
                    if lineList != None and len(lineList) >= 1:
                        keyCache[lineList[0]] = int(lineList[1])

        return keyCache
    except:
        cmf_print("Oh Snap - Error creating replication KeyCache")
        traceback.print_exc()
        return None

def _listChecksOut(listOfStuff, listName=None):
    if listOfStuff != None and len(listOfStuff) >= 1:
        cmf_printDebug("List Name: %s checked contains %s items" %(listName, len(listOfStuff)))
        return True
    else:
        cmf_printDebug("List Name: %s checked contains no items" %(listName))
        return False

#
# Checks the status of the nominated attributes to see if they have been changed.
# Returns true if any of the attributes have been changed, false if they are all 'N'
# for no change
#
def isItemChanged(itemId, attrNames, processId):
    # print "-- isItemChanged START --"
    ignoreAttrNames = IGNORE_ATTR_NAMES

    changed = false
    for attrName in attrNames:
        # print "Attribute %s state = %s"%(getAttributeName(attrName), getAttributeUpdateState(itemId, processId, attrName))
        if attrName not in ignoreAttrNames:
            if (getAttributeUpdateState(itemId, processId, attrName) in ['A', 'C', 'D']):
                changed = true
                break

    # print "-- isItemChanged END changed = %s --"%(changed)

    return changed

def cmf_getChangedAttrNamesMap(nodeId, attrNames, processId, attrNamesToIgnore = None):
    # this will check the list of attributes for any changes.  If the attribute is changed
    # then add the attribute name to the map, otherwise add text, "No Change"
    # Use a map object for faster processing
    attrNamesChanged = {}
    attrNameStatus = {}

    if attrNamesToIgnore == None:
        for attrName in attrNames:
            attrStatus = getAttributeUpdateState(nodeId, processId, attrName)
            if (attrStatus in ['A', 'C', 'D']):
                attrNamesChanged[attrName] = attrName
                attrNameStatus[attrName] = attrStatus
    else:
        for attrName in attrNames:
            if attrName not in attrNamesToIgnore:
                attrStatus = getAttributeUpdateState(nodeId, processId, attrName)
                if (attrStatus in ['A', 'C', 'D']):
                    attrNamesChanged[attrName] = attrName
                    attrNameStatus[attrName] = attrStatus

    return attrNamesChanged, attrNameStatus

def _approveNode(nodeId, bPass, cValue="Approved"):
    if bPass:
        setAttributeValue(nodeId, ['Approval Status', 'approvalStatus'], cValue)
        setAttributeValue(nodeId, ['Approval Status', 'approvalUser'], getUserName(getCurrentUserId()))
        setAttributeValue(nodeId, ['Approval Status', 'approvalDate'], Date().getTime())
        setAttributeValue(nodeId, ['Approval Status', 'approvalReason'], None)
    else:
        setAttributeValue(nodeId, ['Approval Status', 'approvalStatus'], 'Not Approved')

# Get node id of organisation code
def cmf_getOrganisationId(orgCode):
    orgIds = searchForOrgs([getAttributeId("Organisation Code")], None, [orgCode], [nodeLibrary.OPER_EQUALS], 0, True)
    if (orgIds == None) or (len(orgIds) == 0):
        return None
    cmf_printDebug('Org Id List = %s' %(orgIds))
    return orgIds[0]

def validatePerspective(cPerspectiveName):
    currentPersId= getCurrentPerspectiveId()
    persId = getOrgPerspectiveByName(cPerspectiveName, getCurrentOrganisationId())
    if(currentPersId != persId):
        return false
    return true

def _cmf_clearMultiValueComposite(compositeAttrNameArr, nodeId):
    count = getAttributeMultiValueCount(nodeId, compositeAttrNameArr)
    cmf_printDebug("Clearing %s values from %s" % (count, compositeAttrNameArr))
    index = 0
    while index < count:
        setChildAttributeValueByIndex(nodeId, compositeAttrNameArr, None, index)
        index = index + 1


def _cmf_deleteRelationships(nodeId, nodeTypeName):
    relTypeNames = getRelationshipTypes([nodeTypeName])
    for relNameId in relTypeNames:
        relName = findOrganisationRelationshipType(relNameId)
        cmf_printDebug("Removing relationships of type %s" % (relName))
        relNameStr = relName.getSrcToDestName()  # server side only
        # relNameStr = relName.getSrcToDestRelName() # client side only
        relIds = getExistingRelationships(nodeId, relNameStr)
        removeExistingRelationships(relIds)


def _cmf_deleteNode(nodeId, dataTypeName):
    categoryId = -1
    forceDelete = True
    persId = getOrgPerspectiveByName(SAP_PERS_NAME, getCurrentOrganisationId())
    cmf_printDebug("Not deleting %s node with: cat=%s, forceDelete=%s, persId=%s & dataTypeId=%s - delete manually" % (dataTypeName, categoryId, forceDelete, persId, getDataNodeTypeIdByName(dataTypeName)))
    deleteItems(persId, categoryId, [nodeId], forceDelete, getDataNodeTypeIdByName(dataTypeName))

def getAllOntologyAttributeNames(ontologyName):
    attrIdList = getOntologyAttributeIds(ontologyName)
    attrNameList = []
    lastAttrName = ''

    for attrId in attrIdList:
        attrName = getAttributeName(attrId)[0]
        if attrName == lastAttrName:
            continue
        else:
            lastAttrName = attrName
            bIsCombo = False
            bIsComposite = isComposite(attrName)
            bIsGrouped = isGrouped(attrName)
            if bIsComposite or bIsGrouped:
                bIsCombo = True

            if not bIsCombo:
                attrNameList.append(attrName)
            else:
                childAttrNameList = getChildAttributeNames(attrName)
                for index in range(len(childAttrNameList)):
                    attrNameFull = [attrName, childAttrNameList[index]]
                    attrNameList.append(attrNameFull)

    return attrNameList

#
# Copies the details of a node to the given view based on the conversion template to define the fields to be copied
#
def copyNodeToView(nodeId, conversionTemplateName, copyToPersName, uniqueAttrNames, uniqueAttrValues, dataTypeName, orgId, templateOrgId):
    cmf_printDebug('Org ID: %s' % (orgId))
    cmf_printDebug('nodeId: %s' % (nodeId))

    # create the initial node with the uniqueness fields
    copyToNodeId = createNodes(orgId, copyToPersName, uniqueAttrNames, [uniqueAttrValues], dataTypeName)[0]

    cmf_printDebug('Conversion Template Name: %s' % (conversionTemplateName))

    # copy over the other attribute values defined in the template
    copiedAttrIds = runConversion(conversionTemplateName, nodeId, copyToNodeId, templateOrgId)
    cmf_printDebug('Copied Attribute IDs: %s' % (copiedAttrIds))
    cmf_printDebug('Completed conversion template from supplier: %s GTIN: %s to Consolidated record GTIN: %s' %(getAttributeValue(nodeId, 'supplierId'), getAttributeValue(nodeId, 'globalTradeItemNumber'), getAttributeValue(copyToNodeId, 'globalTradeItemNumber')))

    if copiedAttrIds == None:
        cmf_print('Houston we have a problem, workflow node is corrupted.')
        return False
    else:
        for copiedAttrId in copiedAttrIds:
            attrName = getAttributeName(copiedAttrId)
            # cmf_print('Attribute Name: %s' %(attrName))
            if (isAttributeInError(copyToNodeId, attrName)):
                cmf_print("In Error %s" % (attrName[len(attrName) - 1]))

    return copyToNodeId

def cmf_getURCList(URCGroupName, URCParentName):
    subListMap = {}
    urcIds = []

    matchingUrcIds = findUrcs(URCGroupName, URCParentName)
    cmf_printDebug('Found URC for group:  %s and Parent: %s:  ID: %s' %(URCGroupName, URCParentName, matchingUrcIds))

    urcIds = findChildUrcs(matchingUrcIds[0])
    cmf_printDebug('List of URC Ids has %s entries' %(len(urcIds)))

    # get the names and descriptions for the urc's
    childNames = getUrcNames(urcIds)
    childDescs = getUrcDescriptions(urcIds)

    # convert to a list of tuples
    for i in range(len(urcIds)):
        subListMap[childNames[i]] = childDescs[i]

    cmf_printDebug(subListMap)
    return subListMap

def _getPicklistFromURC(URCGroupName, URCParentName, sortByKeys=True, keysOnly=False):
    attrLOV = []
    URCMap = cmf_getURCList(URCGroupName, URCParentName)

    for key in URCMap.keys():
        # Append the descriptions for lookups
        if keysOnly:
            lookupValue = '%s' % (key)
        else:
            if sortByKeys:
                lookupValue = '%s (%s)' % (key, URCMap[key])
            else:
                lookupValue = '%s (%s)' % (URCMap[key], key)
        attrLOV.append(lookupValue)

    attrLOV.sort()
    return attrLOV

def _translateFromURC(nodeId, attrName, URCGroupName, URCParentName):
    valueToTranslate = getAttributeValue(nodeId, attrName)

    if valueToTranslate != None:
        URCMap = cmf_getURCList(URCGroupName, URCParentName)
        if URCMap.get(valueToTranslate, "Not Found") == "Not Found":
            return valueToTranslate
        else:
            return URCMap[valueToTranslate]
    return valueToTranslate

def _translateAndAssignFromURC(nodeId, attrName, URCGroupName, URCParentName):
    valueToTranslate = getAttributeValue(nodeId, attrName)

    if valueToTranslate != None:
        URCMap = cmf_getURCList(URCGroupName, URCParentName)
        if URCMap.get(valueToTranslate, "Not Found") == "Not Found":
            return False
        else:
            setAttributeValue(nodeId, attrName, URCMap[valueToTranslate])
            return True
    return False

def _getGDSNPackagingHierarchy(nodeId, primaryDIAttrName="globalTradeItemNumber", nextLowerLevelDIAttrName="tradeItemIdentificationOfNextLowerLevelTradeItem"):

    packa
    success = False


    return nodeList