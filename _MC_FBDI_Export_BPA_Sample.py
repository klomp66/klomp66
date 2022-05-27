#######################################
# _MC_FBDI_Export_BPA_Sample
# Created April 29, 2022 JvS
# Edit rule to select Items and output to FBDI BPA format
# This export is configurable to:
#   include Column headings or not,
#   use Display Names or attribute technical names in the column headings
#   For testing purposes, print the column headings only
#   Specify the delimiter
#   Specify the character to wrap values in, if the delimiter is found in the data
########################################
#<<<IMPORTS>
import datetime
import random
import time
from java.io import File
from java.io import FileWriter
from java.io import BufferedWriter

runEditRuleWithName('_Custom_MDM_Functions')

# CONSTANTS DECLARATION
PROCEDURE_NAME = "FBDI_BPA_EXPORT"
ATTR_CONTRACT_NUMBER = "contractNumber"
ATTR_CONTRACT_LINE = "contractLine"
ATTR_NAME = "attrName"
CONTRACT = "Contract"
GLOBAL = "Global"
DEFAULT = "Default"
EDIT_RULE = "Edit Rule"

# Controls
PRINT_COLUMN_HEADER_ROW = True
TEST_HEADER_ONLY = False
USE_DISPLAY_NAME_AS_HEADER = True
DELIMITER = ","
DELIMITER_WRAP = '"'
DELIMITER_WRAP_ALWAYS_ON = False
IGNORE_ATTRIBUTE_INDEX_GAPS = True

# Configuration - Data Source
PERSPECTIVE_NAME = "Global Item Master"
ITEM_DATA_TYPE = "Global Item Master"
ONTOLOGY_NAME = "Global_Item_Master"

# Configuration - URC Specification for Attribute Selection and Sequencing
URCGroupName = URC_GROUP_NAME
FBDI_BPA_HEADER_URC = "FBDI_BPA_HEADER"
FBDI_BPA_LINES_URC = "FBDI_BPA_LINES"
FBDI_BPA_ATTRS_URC = "FBDI_BPA_ATTRS"

# Set up values for filenames
today = datetime.datetime.now()
CURRENT_YEAR = today.year
CURRENT_MONTH = _padAnyGTIN(today.month, 2)
CURRENT_DATE = _padAnyGTIN(today.day, 2)
CURRENT_HOUR = _padAnyGTIN(today.hour, 2)
CURRENT_MINUTE = _padAnyGTIN(today.minute, 2)
CURRENT_SECOND = _padAnyGTIN(today.second, 2)

# Output File Name Declaration
OUTPUT_FOLDER = BASE_OUTPUT_DIR  # From 'Health_Constants_And_Functions'
FBDI_HEADER_FILENAME = "%s_%s_%s%s%s at %s_%s.txt" %(FBDI_BPA_HEADER_URC, ENVIRONMENT, CURRENT_YEAR, CURRENT_MONTH, CURRENT_DATE, CURRENT_HOUR, CURRENT_MINUTE)
FBDI_LINES_FILENAME = "%s_%s_%s%s%s at %s_%s.txt" %(FBDI_BPA_LINES_URC, ENVIRONMENT, CURRENT_YEAR, CURRENT_MONTH, CURRENT_DATE, CURRENT_HOUR, CURRENT_MINUTE)
FBDI_ATTRS_FILENAME = "%s_%s_%s%s%s at %s_%s.txt" %(FBDI_BPA_ATTRS_URC, ENVIRONMENT, CURRENT_YEAR, CURRENT_MONTH, CURRENT_DATE, CURRENT_HOUR, CURRENT_MINUTE)

# Create and open the output files
FBDI_HEADER_FULLPATH_FILE = File(OUTPUT_FOLDER, FBDI_HEADER_FILENAME)
FBDI_LINES_FULLPATH_FILE = File(OUTPUT_FOLDER, FBDI_LINES_FILENAME)
FBDI_ATTRS_FULLPATH_FILE = File(OUTPUT_FOLDER, FBDI_ATTRS_FILENAME)

FBDI_HEADER_FILEWRITER = BufferedWriter(FileWriter(FBDI_HEADER_FULLPATH_FILE))
FBDI_LINES_FILEWRITER = BufferedWriter(FileWriter(FBDI_LINES_FULLPATH_FILE))
FBDI_ATTRS_FILEWRITER = BufferedWriter(FileWriter(FBDI_ATTRS_FULLPATH_FILE))

# Configuration - ICAS values
INTERFACE_ID = "577_FBDI_INTERFACE"
BATCH_ID = _padAnyGTIN(random.randint(0, 999999), 6)

# Configuration - FBDI Values
FBDI_DOCUMENT_TYPE = "BLANKET"

# Mappings from mapping file
conversionMap = {}
conversionMap["DOCUMENT_NUM"] = [ATTR_NAME, ATTR_CONTRACT_NUMBER, CONTRACT]
conversionMap["DOCUMENT_TYPE_CODE"] = ["default", "BLANKET"]
conversionMap["PRC_BU_NAME"] = ["default", "MAYO_SHARED_SERVICES_BU"]
conversionMap["LINE_NUM"] = [ATTR_NAME, ATTR_CONTRACT_LINE, CONTRACT]
conversionMap["ITEM"] = [ATTR_NAME, "lawsonItemCode", GLOBAL]
conversionMap["MANUFACTURER_PART_NUM"] = [ATTR_NAME, "manufacturerItemNumber", GLOBAL]
conversionMap["UNSPSC"] = [EDIT_RULE, "_MC_FBDI_Rule_UNSPSC"]

# Retrieve the list of sequences and technical attribute names to be printed out from the URC
FBDI_Header_Map = cmf_getURCList(URCGroupName, FBDI_BPA_HEADER_URC)
FBDI_Lines_Map = cmf_getURCList(URCGroupName, FBDI_BPA_LINES_URC)
FBDI_Attrs_Map = cmf_getURCList(URCGroupName, FBDI_BPA_ATTRS_URC)

def getDisplayNameOfAttribute(ontologyName, attributeListMap):
    ### Get the display name map of nominated attributes, i.e. attributeName: displayName
    attributeNames = getOntologyAttributeNames(ontologyName)
    attributeDescriptions = getOntologyAttributeDisplayNames(ontologyName)
    displayNameMap = {}
    for key in attributeListMap.keys():
        attributeName = attributeListMap[key]

        for i in range(len(attributeNames)):
            name = attributeNames[i]
            if (name == attributeName):
                displayName = attributeDescriptions[i]
                if displayName == None or displayName == '':
                    displayName = name
                displayNameMap[attributeName] = displayName.replace("<html>", "")
                cmf_print("Display Name for Attribute %s is %s" %(attributeName, displayNameMap[attributeName]))
                break

    return displayNameMap

# Get the display names of the attributes
FBDI_HeaderDisplayNamesMap = getDisplayNameOfAttribute(ONTOLOGY_NAME, FBDI_Header_Map)
FBDI_LinesDisplayNamesMap = getDisplayNameOfAttribute(ONTOLOGY_NAME, FBDI_Lines_Map)
FBDI_AttrsDisplayNamesMap = getDisplayNameOfAttribute(ONTOLOGY_NAME, FBDI_Attrs_Map)

headerCache = {}
lineCache = {}
attrCache = {}

def _getHighestKeyValueOfAttributeListMap(attrListMap):
    highValue = 0

    for key in attrListMap.keys():
        if int(key) > highValue:
            highValue = int(key)

    return highValue

FBDI_HEADER_HIGHEST_ATTRIBUTE_INDEX = _getHighestKeyValueOfAttributeListMap(FBDI_Header_Map)
FBDI_LINES_HIGHEST_ATTRIBUTE_INDEX = _getHighestKeyValueOfAttributeListMap(FBDI_Lines_Map)
FBDI_ATTRS_HIGHEST_ATTRIBUTE_INDEX = _getHighestKeyValueOfAttributeListMap(FBDI_Attrs_Map)

def _getPackagingString(nodeId):
    retVal = ""
    netContentUOMAttrName = "netContent UOM"
    netContentAttrName = "netContent"

    suffixList = ["0", "1", "2", "3", "4"]

    for suffix in suffixList:

        if suffix in ["1", "2", "3", "4"]:
            netContentUOMAttrName = "netContent UOM_Alt%s" % (suffix)
            netContentAttrName = "netContent_Alt%s" % (suffix)

        uom = getAttributeValue(nodeId, netContentUOMAttrName)
        conversion = getAttributeValue(nodeId, netContentAttrName)

        if uom not in [None, ""] or conversion not in [None, ""]:
            if retVal == "":
                retVal = "%s/%s" % (uom, conversion)
            else:
                retVal = "%s/%s/%s" %(retVal, uom, conversion)

    cmf_printDebug("PACKAGING_STRING calculated as: %s " %(retVal))
    return retVal

def _getAllRelatedContractNodes(nodeId):
    retList = []
    match = False
    upstreamMasterId = None
    orgId = getCurrentOrganisationId()

    relNameMaster = "CONSOLIDATED_IMPORT_ITEM_TO_GLOBAL_ITEM_MASTER"
    consolMasterRelNodeList = getRelatedNodes(nodeId, relNameMaster, orgId)
    # there should be one!
    if consolMasterRelNodeList != None:
        upstreamMasterId = consolMasterRelNodeList[0]
        cmf_print("Consolidated MASTER record key is: %s" % (getAttributeValue(upstreamMasterId, "UniqueCompositeKey")))

    if upstreamMasterId != None:
        # Next to find all relationships called "Master"
        masterRelName = "Master"
        relIdList = getExistingRelationships(upstreamMasterId, masterRelName)

        if _listChecksOut(relIdList, "Source Records"):
            relNodeList = getRelatedNodes(upstreamMasterId, masterRelName, orgId)
            cmf_print("Master record has %s related nodes with relationship type 'MASTER'" % (len(relNodeList)))

            for relNodeId in relNodeList:
                match = False
                if ("Mayo_C" in getAttributeValue(relNodeId, "UniqueCompositeKey")) and (getAttributeValue(relNodeId, "Contracted") == True) and (getAttributeValue(relNodeId, "ITEM_TYPE") == "Special"):
                    if (getAttributeValue(relNodeId, "contractNumber") == getAttributeValue(nodeId, "contractNumber")) and (getAttributeValue(relNodeId, "contractLine") == getAttributeValue(nodeId, "contractLine")):
                        match = True
                        retList.append(relNodeId)
                    else:
                        retList.append(relNodeId)
    return retList


def printColumnHeaders(highestIndex, attributeListMap, displayNamesMap, fileWriter, URCParentName):
    ### Prints the column headings line
    string = ""
    displayName = ""
    for i in range(highestIndex + 1):
        cmf_printDebug("Index: %s" %(i))
        # convert to a string
        index = str(i)
        # pad it to 3 char
        newIndex = _padAnyGTIN(index, 3)

        if attributeListMap.get(newIndex, "Not Found") == "Not Found":
            if IGNORE_ATTRIBUTE_INDEX_GAPS:
                cmf_print("ERROR:  Reference Code List %s does not contain a code of %s" %(URCParentName, newIndex))
                continue
            else:
                cmf_print("ERROR:  Reference Code List %s does not contain a code of %s, adding placeholder" % (URCParentName, newIndex))
                displayName = "placeHolder"
        else:
            attrName = attributeListMap[newIndex]
            if displayNamesMap.get(attrName, "Not Found") == "Not Found":
                cmf_print("ERROR: Could not retrieve the display name for attribute: %s, using attribute tech name instead" %(attrName))
                displayName = attrName
            else:
                if USE_DISPLAY_NAME_AS_HEADER:
                    displayName = displayNamesMap[attrName]
                else:
                    displayName = attrName

        if DELIMITER in displayName or DELIMITER_WRAP_ALWAYS_ON:
            displayName = '%s%s%s' % (DELIMITER_WRAP, displayName, DELIMITER_WRAP)

        string = "%s%s%s" % (string, displayName, DELIMITER)

    string = "%sEND\n" %(string)
    fileWriter.write(string)
    return True

def _printDataLine(highestIndex, contractNumber, nodeId, attributeListMap, URCParentName, fileWriter, contractToGlobalMap):
    ### Writes the data line from the node Id to the output file
    string = ""

    if contractToGlobalMap.get(nodeId, "Not Found") == "Not Found":
        cmf_print("ERROR: Contract Node: %s doesn't seem to have a related Global Node, cannot produce data line" %(getAttributeValue(nodeId, UNIQUE_KEY_ATTR_NAME)))
        return False
    else:
        globalNodeId = contractToGlobalMap[nodeId]
        cmf_printDebug("Contract Node: %s has a related Global Node %s, continuing" % (getAttributeValue(nodeId, UNIQUE_KEY_ATTR_NAME), getAttributeValue(globalNodeId, UNIQUE_KEY_ATTR_NAME)))

    for i in range(highestIndex + 1):
        # convert to a string
        index = str(i)
        # pad it to 3 char
        newIndex = _padAnyGTIN(index, 3)

        # initialize value
        value = ""

        # Check for index gaps, and ignore if it's ok to count in the list by 5's or whatever increment.
        if attributeListMap.get(newIndex, "Not Found") == "Not Found":
            if IGNORE_ATTRIBUTE_INDEX_GAPS:
                cmf_printDebug("ERROR:  Reference Code List %s does not contain a code of %s, ignoring..." % (URCParentName, newIndex))
            else:
                cmf_printDebug("ERROR:  Reference Code List %s does not contain a code of %s, adding a null in place" % (URCParentName, newIndex))
                value = ""
                string = "%s%s%s" % (string, value, DELIMITER)
        else:
            attrName = attributeListMap[newIndex]

            # Handle the metadata first
            if attrName == "INTERFACE_HEADER_KEY":
                if headerCache.get(contractNumber, "Not Found") != "Not Found":
                    value = headerCache[contractNumber]
            if attrName == "INTERFACE_LINE_KEY":
                contractNum = getAttributeValue(nodeId, ATTR_CONTRACT_NUMBER)
                contractLine = getAttributeValue(nodeId, ATTR_CONTRACT_LINE)
                contractCombo = "%s: %s" % (contractNum, contractLine)
                if lineCache.get(contractCombo, "Not Found") != "Not Found":
                    value = lineCache[contractCombo]
            if attrName == "INTERFACE_ATTRIBUTE_KEY":
                contractNum = getAttributeValue(nodeId, ATTR_CONTRACT_NUMBER)
                contractLine = getAttributeValue(nodeId, ATTR_CONTRACT_LINE)
                contractCombo = "%s: %s" % (contractNum, contractLine)
                if attrCache.get(contractCombo, "Not Found") != "Not Found":
                    value = attrCache[contractCombo]

            if attrName == "ACTION" and "HEADER" in URCParentName:
                value = "UPDATE"
            if attrName == "ACTION" and "LINES" in URCParentName:
                value = "SYNC"

            if attrName == "PACKAGING_STRING":
                value = _getPackagingString(globalNodeId)

            # Finally, handle the conversionMap assignments
            if value == "":
                if conversionMap.get(attrName, "Not Found") != "Not Found":
                    instructionType = conversionMap[attrName][0]
                    instructionValue = conversionMap[attrName][1]
                    instructionSource = ""

                    if instructionType == DEFAULT:
                        value = instructionValue

                    if instructionType == ATTR_NAME:
                        instructionSource = conversionMap[attrName][2]

                        if instructionSource == CONTRACT:
                            value = getAttributeValue(nodeId, instructionValue)
                        if instructionSource == GLOBAL:
                            value = getAttributeValue(globalNodeId, instructionValue)

                    if instructionType == EDIT_RULE:
                        instructionSource = conversionMap[attrName][1]
                        runEditRuleWithName(instructionSource)

            if value == None:
                value = ""  # Otherwise it outputs "None" which isn't typically desired

            value = "%s" %(value)
            # Check to see if the delimiter is contained within the data, and wrap the value in the wrap character
            if DELIMITER in value or DELIMITER_WRAP_ALWAYS_ON:
                value = '%s%s%s' %(DELIMITER_WRAP, value, DELIMITER_WRAP)

            string = "%s%s%s" % (string, value, DELIMITER)
    string = "%sEND\n" % (string)
    fileWriter.write(string)

    return True


def _processRetrievedRecords(nodeBatch, contractToGlobalMap):
    ### writes the data records out to the file, in the sequence determined by the URC sequencing.

    global headerCounter
    global lineCounter

    # First, ensure the Contract records as well as Global records are loaded, speed things up
    cmf_printDebug("NodeBatch has %s records" %(len(nodeBatch)))

    loadList = []
    for nodeId in nodeBatch:
        if contractToGlobalMap.get(nodeId, "Not Found") != "Not Found":
            loadList.append(contractToGlobalMap[nodeId])

    cmf_printDebug("Extra Node List to load into memory has %s records" %(len(loadList)))
    cmf_printDebug("NodeBatch has %s records" %(len(nodeBatch)))
    ensureDataNodesLoaded(loadList)

    for nodeId in nodeBatch:
        contractNum = getAttributeValue(nodeId, ATTR_CONTRACT_NUMBER)
        contractLine = getAttributeValue(nodeId, ATTR_CONTRACT_LINE)
        contractCombo = "%s: %s" %(contractNum, contractLine)

        if headerCache.get(contractNum, "Not Found") == "Not Found":
            headerCounter += 1
            interfaceKey = "%s%s" %(INTERFACE_ID, headerCounter)
            headerCache[contractNum] = interfaceKey
            _printDataLine(FBDI_HEADER_HIGHEST_ATTRIBUTE_INDEX, contractNum, nodeId, FBDI_Header_Map, FBDI_BPA_HEADER_URC, FBDI_HEADER_FILEWRITER, contractToGlobalMap)

        if lineCache.get(contractCombo, "Not Found") == "Not Found":
            lineCounter += 1
            lineKey = "line%s" %(lineCounter)
            attrKey = "attribute%s" %(lineCounter)
            lineCache[contractCombo] = lineKey
            attrCache[contractCombo] = attrKey
            _printDataLine(FBDI_LINES_HIGHEST_ATTRIBUTE_INDEX, contractNum, nodeId, FBDI_Lines_Map, FBDI_BPA_LINES_URC, FBDI_LINES_FILEWRITER, contractToGlobalMap)
            _printDataLine(FBDI_ATTRS_HIGHEST_ATTRIBUTE_INDEX, contractNum, nodeId, FBDI_Attrs_Map, FBDI_BPA_ATTRS_URC, FBDI_ATTRS_FILEWRITER, contractToGlobalMap)

        # Finish the global record status
        if contractToGlobalMap.get(nodeId, "Not Found") != "Not Found":
            setAttributeValue(contractToGlobalMap[nodeId], "updateStatus", "Unchanged")

    return headerCounter, lineCounter #<<whatever>>

def _getRecordsToBeProcessed():
    ### This forms the data selection to be used for processing
    orgId = getCurrentOrganisationId()
    persId = getOrgPerspectiveByName(PERSPECTIVE_NAME, orgId)
    dataTypeId = getDataNodeTypeIdByName(ITEM_DATA_TYPE)

    contractToGlobalMap = {}
    contractNodeIds = []

    attrIds = []
    attrOperators = []
    attrValues = []

    # Selection criteria
    attrIds.append(getAttributeId("updateStatus"))
    attrOperators.append(nodeLibrary.OPER_NE)
    attrValues.append('No Change')

    #<<<REPEAT AS NEEDED>>>

    nodeList = searchForNodes(dataTypeId, attrIds, None, attrValues, attrOperators, [persId], orgId)

    cmf_printDebug("%s searchForNodes in data type: %s returned %s records." % (PROCEDURE_NAME, ITEM_DATA_TYPE, len(nodeList)))

    contractNodes = []

    if _listChecksOut(nodeList, "Changed Global Contracts"):
        # Retrieve the contract records from Consolidated View for each Global Node and map it to the node mapping
        # The node mapping of contract to Global items is necessary, since the output will contain values from both Global record and Contract record

        for globalNodeId in nodeList:
            contractNodeIds = _getAllRelatedContractNodes(globalNodeId)

            if _listChecksOut(contractNodeIds, "Contract Records"):
                for contractNodeId in contractNodeIds:
                    contractNodes.append(contractNodeId)
                    contractToGlobalMap[contractNodeId] = globalNodeId

    return contractNodes, contractToGlobalMap


# rule begins here
try:
    BATCH_SIZE = 60
    PAUSE_TIME = 0
    headerCounter = 0
    lineCounter = 0

    startTime = Date().getTime()
    nodeIds, contractToGlobalMap = _getRecordsToBeProcessed()
    cmf_printDebug("Returned %s nodeIds and contract map contains %s entries" %(len(nodeIds), len(contractToGlobalMap)))
    numRecs = len(nodeIds)
    nodeBatches = chunks(nodeIds, BATCH_SIZE)
    batchCounter = 0

    if PRINT_COLUMN_HEADER_ROW:
        printColumnHeaders(FBDI_HEADER_HIGHEST_ATTRIBUTE_INDEX, FBDI_Header_Map, FBDI_HeaderDisplayNamesMap, FBDI_HEADER_FILEWRITER, FBDI_BPA_HEADER_URC)
        printColumnHeaders(FBDI_LINES_HIGHEST_ATTRIBUTE_INDEX, FBDI_Lines_Map, FBDI_LinesDisplayNamesMap, FBDI_LINES_FILEWRITER, FBDI_BPA_LINES_URC)
        printColumnHeaders(FBDI_ATTRS_HIGHEST_ATTRIBUTE_INDEX, FBDI_Attrs_Map, FBDI_AttrsDisplayNamesMap, FBDI_ATTRS_FILEWRITER, FBDI_BPA_ATTRS_URC)

    if not TEST_HEADER_ONLY:
        for nodeBatch in nodeBatches:
            batchTimer = Date().getTime()
            ensureDataNodesLoaded(nodeBatch)
            cmf_printDebug("Now Processing Batch %s of total %s batches.." %(batchCounter, len(nodeBatches)))
            batchCounter += 1
            _processRetrievedRecords(nodeBatch, contractToGlobalMap)

            workingTimer = Date().getTime()
            batchTime = float((workingTimer - batchTimer) / 1000)
            if batchTime < .1:
                batchTime = .1
            batchRate = round(float(BATCH_SIZE / batchTime), 2)
            if batchRate < .1:
                batchRate = .1
            totalTime = float((workingTimer - startTime) / 1000)
            if totalTime < .1:
                totalTime = .1
            totalRate = round(float((BATCH_SIZE * batchCounter) / totalTime), 2)
            if totalRate < .1:
                totalRate = .1
            recsToGo = numRecs - (BATCH_SIZE * batchCounter)
            secondsLeftAvg = int(recsToGo / totalRate)
            secondsLeftBatch = int(recsToGo / batchRate)
            cmf_print("%s STATS:  Batch rate: %s/s. Avg rate: %s/s. Remaining: %s. ETC Batch: %s, ETC Avg: %s" % (PROCEDURE_NAME, batchRate, totalRate, recsToGo, secondsLeftBatch, secondsLeftAvg))

            if batchCounter % BATCH_SIZE == 0 and PAUSE_TIME != 0:
                cmf_print("%s STATS: Batch %s complete out of %s total, pausing for %s seconds for system to catch up" %(PROCEDURE_NAME, batchCounter, len(nodeBatches), PAUSE_TIME))
                time.sleep(PAUSE_TIME)

    jobTime = float((Date().getTime() - startTime) / 1000)
    cmf_print("%s STATS:  TOTAL TIME taken for job: %s seconds" %(PROCEDURE_NAME, jobTime))
    cmf_print("%s Complete" %(PROCEDURE_NAME))
except:
    cmf_print('PROBLEM running %s' %(PROCEDURE_NAME))
    FBDI_HEADER_FILEWRITER.close()
    FBDI_LINES_FILEWRITER.close()
    FBDI_ATTRS_FILEWRITER.close()
    FBDI_Header_Map.clear()
    FBDI_Lines_Map.clear()
    FBDI_Attrs_Map.clear()
    FBDI_HeaderDisplayNamesMap.clear()
    FBDI_LinesDisplayNamesMap.clear()
    FBDI_AttrsDisplayNamesMap.clear()
    traceback.print_exc()
    pass

finally:
    if FBDI_HEADER_FILEWRITER != None:
        FBDI_HEADER_FILEWRITER.close()
    if FBDI_LINES_FILEWRITER != None:
        FBDI_LINES_FILEWRITER.close()
    if FBDI_ATTRS_FILEWRITER != None:
        FBDI_ATTRS_FILEWRITER.close()

    FBDI_Header_Map.clear()
    FBDI_Lines_Map.clear()
    FBDI_Attrs_Map.clear()
    FBDI_HeaderDisplayNamesMap.clear()
    FBDI_LinesDisplayNamesMap.clear()
    FBDI_AttrsDisplayNamesMap.clear()
