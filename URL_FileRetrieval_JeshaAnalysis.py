##########################################
# URL_FileRetrieval
# Created 3/22/2021 JvS
#
# Used to download a file at a specific URL
##########################################

import traceback
import logging
import re
import xml.etree.ElementTree as ET
import urllib.request
from datetime import datetime
from zipfile import ZipFile

VERSION = ["Full"]

# On to the download stuff...
timeStamp = datetime.now()

cYear = timeStamp.strftime("%Y")
cMonth = timeStamp.strftime("%m")
cDate = timeStamp.strftime("%d")
cDateFixed = "01"

# Modify the filename as needed to the first of the month
suffix = "%s%s%s" % (cYear, cMonth, cDateFixed)
# Modify the filename as needed to the current date
dailySuffix = "%s%s%s" % (cYear, cMonth, cDate)

# set up logging business
logFileName = 'C:\\Interfaces\\AccessGUDID\\AccessGUDID_Logger_%s.log' %(dailySuffix)

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
# LOG_FORMAT = "%(message)s"

logging.basicConfig(filename=logFileName, \
                    level=logging.DEBUG, \
                    format=LOG_FORMAT, \
                    filemode='a')  # filemode='w' will overwrite the log each time, 'a' will append
# Logger is in append mode, in case the monthly and daily jobs both run on same day, they will not overwrite each other.

writeLog = logging.getLogger()
writeLog.info("Starting Access GUDID %s download and processing." %(VERSION))

URL_SOURCE_DELIM = "https://accessgudid.nlm.nih.gov/release_files/download/AccessGUDID_Delimited_Full_Release_%s.zip" % (suffix)
URL_SOURCE_XML_FULL = "https://accessgudid.nlm.nih.gov/release_files/download/gudid_full_release_%s.zip" % (suffix)
URL_SOURCE_XML_DAILY = "https://accessgudid.nlm.nih.gov/release_files/download/gudid_daily_update_%s.zip" % (dailySuffix)

DEST_PATH = 'C:/Interfaces/AccessGUDID/Files/'
DEST_FILE_DELIM = 'GUDID_DATA_DELIM.zip'
DEST_FILE_XML_FULL = 'GUDID_DATA_XML_FULL_%s.zip' % (suffix)
DEST_FILE_XML_DAILY = 'GUDID_DATA_XML_DAILY_%s.zip' % (dailySuffix)

DELIMITER = "|"
writeLog.info("Import file delimiter will be: '%s'" %(DELIMITER))


def _downloadAndUnzip(sourceURL, commonPath, destinationFileName):
    try:
        DEST_FNAME = '%s%s' % (commonPath, destinationFileName)

        writeLog.info("Please Wait - Downloading %s" % (sourceURL))
        urllib.request.urlretrieve(sourceURL, DEST_FNAME)
        writeLog.info("Download Complete.")

        writeLog.info("Unzipping....")
        with ZipFile(DEST_FNAME, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            # Iterate over the file names
            for fileName in listOfFileNames:
                # Confirm the file being extracted
                writeLog.info("Now Extracting file: %s" % (fileName))
                zipObj.extract(fileName, commonPath)

        writeLog.info("Unzip should now be complete")
        return listOfFileNames
    except:
        writelog.info("Problem with downloading SourceURL: %s" %(sourceURL))
        traceback.print_exc()
        return None


def _createReplicationKeyMap(keyMapFileName):
    # This map is used to compare the XML files, and only allow the XML records if the keys are found in this keyMap
    keyMap = {}

    try:
        writeLog.info("_createReplicationKeyMap called, starting...")
        lines = [line.strip() for line in open(keyMapFileName)]
        for line in lines:
            keyMap[line] = "True"

        return keyMap
    except:
        writeLog.info("Oh Snap - Error creating replication Keymap")
        traceback.print_exc()
        return None


def _removeUnwantedChar(string, badChar):
    # how long is this string
    strLen = len(string)

    # at what location is the bad char
    bcIndex = string.find(badChar)

    # if the bad char is found
    if bcIndex != -1:
        # Prefix is everything before the bad char
        Prefix = string[0:bcIndex - 1]

        # Suffix is everything after the bad char, remember index starts at 0 so the final index
        # is the length of the string -1
        Suffix = string[bcIndex + 1: strLen - 1]

        # reassemble without the bad Char
        newString = '%s%s' % (Prefix, Suffix)

        return newString

    return string


def _processListOfXMLFiles(xmlFileList, folderPath, loadFileName):
    def actualTag(tag):
        return tag[(len(nameSpace) - len(tag)):]

    def fullTag(tag):
        return nameSpace + tag
    
    def _BuildCompanyMap(companyNameMap, key):
                
        if companyNameMap.get(key, "Not Found") == "Not Found":
            counterValue = 1
        else:
            counterValue = companyNameMap[key] + 1
        
        companyNameMap[key] = counterValue
        writeLog.info("Key value is %s and counter = %s" %(key, counterValue))
        
        return companyNameMap

    def _getXPathText(xmlNode, tag, XPathList=[]):
        # XPathList is a list of XPATHs, given as simple tags, need to be filled out and then text values retrieved.
        # This list starts from the calling point, not from the root.
        xpath = "./"

        if XPathList != []:
            for pathTag in XPathList:
                xpath = "%s/%s" % (xpath, fullTag(pathTag))

        xpath = "%s/%s" % (xpath, fullTag(tag))

        try:
            retVal = xmlNode.find(xpath).text

            if retVal in [None, "", "None", "Null"]:
                return " "
            else:
                if retVal == "false":
                    return "No"
                if retVal == "true":
                    return "Yes"

                if '\n' in retVal:
                    retVal = retVal.replace('\n', ' ')
                if DELIMITER in retVal:
                    retVal = retVal.replace(DELIMITER, ':')

                return retVal
        except AttributeError:
            writeLog.info("Attribute Error on %s%s" % (XPathList, tag))
            return " "

    def _generateDelimLine(child, header=False):
        delimLine = ""
        # device attrs
        if header:
            delimLine = "publicVersionStatus%s" %(DELIMITER)
        else:
            publicVersionStatus = _getXPathText(child, "publicVersionStatus")
            delimLine = "%s%s" % (publicVersionStatus, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceRecordStatus%s" % (delimLine, DELIMITER)
        else:
            deviceRecordStatus = _getXPathText(child, "deviceRecordStatus")
            delimLine = "%s%s%s" % (delimLine, deviceRecordStatus, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%spublicVersionNumber%s" % (delimLine, DELIMITER)
        else:
            publicVersionNumber = _getXPathText(child, "publicVersionNumber")
            delimLine = "%s%s%s" % (delimLine, publicVersionNumber, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%spublicVersionDate%s" % (delimLine, DELIMITER)
        else:
            publicVersionDate = _getXPathText(child, "publicVersionDate")
            delimLine = "%s%s%s" % (delimLine, publicVersionDate, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdevicePublishDate%s" % (delimLine, DELIMITER)
        else:
            devicePublishDate = _getXPathText(child, "devicePublishDate")
            delimLine = "%s%s%s" % (delimLine, devicePublishDate, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceCommDistributionEndDate%s" % (delimLine, DELIMITER)
        else:
            deviceCommDistributionEndDate = _getXPathText(child, "deviceCommDistributionEndDate")
            delimLine = "%s%s%s" % (delimLine, deviceCommDistributionEndDate, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceCommDistributionStatus%s" % (delimLine, DELIMITER)
        else:
            deviceCommDistributionStatus = _getXPathText(child, "deviceCommDistributionStatus")
            delimLine = "%s%s%s" % (delimLine, deviceCommDistributionStatus, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sbrandName%s" % (delimLine, DELIMITER)
        else:
            brandName = _getXPathText(child, "brandName")
            delimLine = "%s%s%s" % (delimLine, brandName[:65], DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sversionModelNumber%s" % (delimLine, DELIMITER)
        else:
            versionModelNumber = _getXPathText(child, "versionModelNumber")
            delimLine = "%s%s%s" % (delimLine, versionModelNumber, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%scatalogNumber%s" % (delimLine, DELIMITER)
        else:
            catalogNumber = _getXPathText(child, "catalogNumber")
            delimLine = "%s%s%s" % (delimLine, catalogNumber, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdunsNumber%s" % (delimLine, DELIMITER)
        else:
            dunsNumber = _getXPathText(child, "dunsNumber")
            delimLine = "%s%s%s" % (delimLine, dunsNumber, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%scompanyName%s" % (delimLine, DELIMITER)
        else:
            companyName = _getXPathText(child, "companyName")
            delimLine = "%s%s%s" % (delimLine, companyName, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceCount%s" % (delimLine, DELIMITER)
        else:
            deviceCount = _getXPathText(child, "deviceCount")
            delimLine = "%s%s%s" % (delimLine, deviceCount, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceDescription%s" % (delimLine, DELIMITER)
        else:
            deviceDescription = _getXPathText(child, "deviceDescription")
            delimLine = "%s%s%s" % (delimLine, deviceDescription[:500], DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sDMExempt%s" % (delimLine, DELIMITER)
        else:
            DMExempt = _getXPathText(child, "DMExempt")
            delimLine = "%s%s%s" % (delimLine, DMExempt, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%spremarketExempt%s" % (delimLine, DELIMITER)
        else:
            premarketExempt = _getXPathText(child, "premarketExempt")
            delimLine = "%s%s%s" % (delimLine, premarketExempt, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceHCTP%s" % (delimLine, DELIMITER)
        else:
            deviceHCTP = _getXPathText(child, "deviceHCTP")
            delimLine = "%s%s%s" % (delimLine, deviceHCTP, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceKit%s" % (delimLine, DELIMITER)
        else:
            deviceKit = _getXPathText(child, "deviceKit")
            delimLine = "%s%s%s" % (delimLine, deviceKit, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceCombinationProduct%s" % (delimLine, DELIMITER)
        else:
            deviceCombinationProduct = _getXPathText(child, "deviceCombinationProduct")
            delimLine = "%s%s%s" % (delimLine, deviceCombinationProduct, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%ssingleUse%s" % (delimLine, DELIMITER)
        else:
            singleUse = _getXPathText(child, "singleUse")
            delimLine = "%s%s%s" % (delimLine, singleUse, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%slotBatch%s" % (delimLine, DELIMITER)
        else:
            lotBatch = _getXPathText(child, "lotBatch")
            delimLine = "%s%s%s" % (delimLine, lotBatch, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sserialNumber%s" % (delimLine, DELIMITER)
        else:
            serialNumber = _getXPathText(child, "serialNumber")
            delimLine = "%s%s%s" % (delimLine, serialNumber, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%smanufacturingDate%s" % (delimLine, DELIMITER)
        else:
            manufacturingDate = _getXPathText(child, "manufacturingDate")
            delimLine = "%s%s%s" % (delimLine, manufacturingDate, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sexpirationDate%s" % (delimLine, DELIMITER)
        else:
            expirationDate = _getXPathText(child, "expirationDate")
            delimLine = "%s%s%s" % (delimLine, expirationDate, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdonationIdNumber%s" % (delimLine, DELIMITER)
        else:
            donationIdNumber = _getXPathText(child, "donationIdNumber")
            delimLine = "%s%s%s" % (delimLine, donationIdNumber, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%slabeledContainsNRL%s" % (delimLine, DELIMITER)
        else:
            labeledContainsNRL = _getXPathText(child, "labeledContainsNRL")
            delimLine = "%s%s%s" % (delimLine, labeledContainsNRL, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%slabeledNoNRL%s" % (delimLine, DELIMITER)
        else:
            labeledNoNRL = _getXPathText(child, "labeledNoNRL")
            delimLine = "%s%s%s" % (delimLine, labeledNoNRL, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sMRISafetyStatus%s" % (delimLine, DELIMITER)
        else:
            MRISafetyStatus = _getXPathText(child, "MRISafetyStatus")
            delimLine = "%s%s%s" % (delimLine, MRISafetyStatus, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%srx%s" % (delimLine, DELIMITER)
        else:
            rx = _getXPathText(child, "rx")
            delimLine = "%s%s%s" % (delimLine, rx, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sotc%s" % (delimLine, DELIMITER)
        else:
            otc = _getXPathText(child, "otc")
            delimLine = "%s%s%s" % (delimLine, otc, DELIMITER)
        #        writeLog.info(delimLine)

        # identifiers ["identifiers","identifier"]
        xPathSegment = ["identifiers", "identifier"]
        if header:
            delimLine = "%sdeviceId%s" % (delimLine, DELIMITER)
        else:
            deviceId = _getXPathText(child, "deviceId", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, deviceId, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceIdType%s" % (delimLine, DELIMITER)
        else:
            deviceIdType = _getXPathText(child, "deviceIdType", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, deviceIdType, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sdeviceIdIssuingAgency%s" % (delimLine, DELIMITER)
        else:
            deviceIdIssuingAgency = _getXPathText(child, "deviceIdIssuingAgency", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, deviceIdIssuingAgency, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%scontainsDINumber%s" % (delimLine, DELIMITER)
        else:
            containsDINumber = _getXPathText(child, "containsDINumber", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, containsDINumber, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%spkgQuantity%s" % (delimLine, DELIMITER)
        else:
            pkgQuantity = _getXPathText(child, "pkgQuantity", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, pkgQuantity, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%spkgDiscontinueDate%s" % (delimLine, DELIMITER)
        else:
            pkgDiscontinueDate = _getXPathText(child, "pkgDiscontinueDate", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, pkgDiscontinueDate, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%spkgStatus%s" % (delimLine, DELIMITER)
        else:
            pkgStatus = _getXPathText(child, "pkgStatus", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, pkgStatus, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%spkgType%s" % (delimLine, DELIMITER)
        else:
            pkgType = _getXPathText(child, "pkgType", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, pkgType, DELIMITER)
        #        writeLog.info(delimLine)

        # Contacts ["contacts", "customerContact"]
        xPathSegment = ["contacts", "customerContact"]
        # phone = _getXPathText(child, "phone", xPathSegment)
        # phoneExtension = _getXPathText(child, "phoneExtension", xPathSegment)
        # email = _getXPathText(child, "email", xPathSegment)

        # GMDN Terms ["gmdnTerms", "gmdn"]
        xPathSegment = ["gmdnTerms", "gmdn"]
        if header:
            delimLine = "%sgmdnPTName%s" % (delimLine, DELIMITER)
        else:
            gmdnPTName = _getXPathText(child, "gmdnPTName", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, gmdnPTName, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%sgmdnPTDefinition%s" % (delimLine, DELIMITER)
        else:
            gmdnPTDefinition = _getXPathText(child, "gmdnPTDefinition", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, gmdnPTDefinition[:475], DELIMITER)
        #        writeLog.info(delimLine)

        # Product Codes ["productCodes", "fdaProductCode"]
        xPathSegment = ["productCodes", "fdaProductCode"]
        # productCode = _getXPathText(child, "productCode", xPathSegment)
        # productCodeName = _getXPathText(child, "productCodeName", xPathSegment)

        # Environmental Conditions ["environmentalConditions", "storageHandling"]
        xPathSegment = ["environmentalConditions", "storageHandling"]
        # storageHandlingType = _getXPathText(child, "storageHandlingType", xPathSegment)
        # storageHandlingHigh = _getXPathText(child, "storageHandlingHigh", xPathSegment)
        # storageHandlingHighValue = storageHandlingHigh.attrib.get("value", "Not Found")
        # storageHandlingHighUOM = storageHandlingHigh.attrib.get("unit", "Not Found")
        # storageHandlingLow = _getXPathText(child, "storageHandlingLow", xPathSegment)
        # storageHandlingLowValue = storageHandlingLow.attrib.get("value", "Not Found")
        # storageHandlingLowUOM = storageHandlingLow.attrib.get("unit", "Not Found")
        # storageHandlingSpecialConditionText = _getXPathText(child, "storageHandlingSpecialConditionText", xPathSegment)

        # Device Sizes ["deviceSizes", "deviceSize"]
        xPathSegment = ["deviceSizes", "deviceSize"]

        if header:
            delimLine = "%sLength%sLengthUOM%sWidth%sWidthUOM%sHeight%sHeightUOM%sDepth%sDepthUOM%ssizeText%s" % (delimLine, DELIMITER, DELIMITER, DELIMITER, DELIMITER, DELIMITER, DELIMITER, DELIMITER, DELIMITER, DELIMITER)
        else:
            length = ""
            lengthUOM = ""
            width = ""
            widthUOM = ""
            height = ""
            heightUOM = ""
            depth = ""
            depthUOM = ""
            sizeText = ""

            xpathFullSegment = "./%s/%s" % (fullTag("deviceSizes"), fullTag("deviceSize"))
            sizeNodeList = child.findall(xpathFullSegment)

            if sizeNodeList != None and len(sizeNodeList) > 0:
                for sizeNode in sizeNodeList:
                    sizeType = _getXPathText(sizeNode, "sizeType")
                    writeLog.info("sizeType should be found: %s" % (sizeType))
                    if sizeType in ["Length", "Width", "Height", "Depth"]:
                        sizeObj = sizeNode.find("./%s" % (fullTag("size")))
                        for key in sizeObj.attrib.keys():
                            writeLog.info("Attributes are:  Attribute Name (key): %s, Attribute Value (value): %s" % (key, sizeObj.attrib[key]))
                        sizeValue = sizeObj.attrib.get("value", "Not Found")
                        writeLog.info("size Value is: %s" % (sizeValue))
                        sizeUOM = sizeObj.attrib.get("unit", "Not Found")
                        writeLog.info("Size uoM is: %s" % (sizeUOM))

                        if sizeType == "Length":
                            length = sizeValue
                            lengthUOM = sizeUOM
                        elif sizeType == "Width":
                            width = sizeValue
                            widthUOM = sizeUOM
                        elif sizeType == "Height":
                            height = sizeValue
                            heightUOM = sizeUOM
                        elif sizeType == "Depth":
                            depth = sizeValue
                            depthUOM = sizeUOM
                        else:
                            pass

                    sizeText = _getXPathText(sizeNode, "sizeText")
            delimLine = "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s" % (delimLine, length, DELIMITER, lengthUOM, DELIMITER, width, DELIMITER, widthUOM, DELIMITER, height, DELIMITER, heightUOM, DELIMITER, depth, DELIMITER, depthUOM, DELIMITER, sizeText, DELIMITER)

        # Sterilization ["sterilization"]
        xPathSegment = ["sterilization"]
        if header:
            delimLine = "%sdeviceSterile%s" % (delimLine, DELIMITER)
        else:
            deviceSterile = _getXPathText(child, "deviceSterile", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, deviceSterile, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%ssterilizationPriorToUse%s" % (delimLine, DELIMITER)
        else:
            sterilizationPriorToUse = _getXPathText(child, "sterilizationPriorToUse", xPathSegment)
            delimLine = "%s%s%s" % (delimLine, sterilizationPriorToUse, DELIMITER)
        #        writeLog.info(delimLine)

        if header:
            delimLine = "%ssterilizationMethod%s" % (delimLine, DELIMITER)
        else:
            methodTypes = _getXPathText(child, "methodTypes", xPathSegment)
            if methodTypes not in [None, "", " ", "None", "Null"]:
                xPathSegment = ["sterilization", "methodTypes"]
                sterilizationMethod = _getXPathText(child, "sterilizationMethod", xPathSegment)
                delimLine = "%s%s%s" % (delimLine, sterilizationMethod, DELIMITER)
            #                writeLog.info(delimLine)
            else:
                delimLine = "%s%s" % (delimLine, DELIMITER)
        #                writeLog.info(delimLine)

        delimLine = "%s\n" % (delimLine)
        return delimLine

    try:
        writeLog.info("_processListOfXMLFiles called, starting...")
        writeFile = open(loadFileName, "wt", encoding="utf-8")
        #headerLine = _generateDelimLine("Nothing", True)
        #writeFile.write(headerLine)
        companyCountMap = {}
        companyAnalysisMap = {}

        for xmlFile in xmlFileList:
            writeLog.info("Processing xml file: %s" % (xmlFile))
            fileWithPath = "%s%s" % (DEST_PATH, xmlFile)
            tree = ET.parse(fileWithPath)
            root = tree.getroot()
            nameSpace = re.match(r'{.*}', root.tag).group(0)
            writeLog.info("nameSpace: %s" % (nameSpace))
            writeLog.info("Root tag is: %s" % (actualTag(root.tag)))

            tagsWithAttributes = {}

            for child in root:
                if child.attrib == {} or child.attrib == {'{http://www.w3.org/2001/XMLSchema-instance}nil': 'true'}:
                    # writeLog.info("./%s: %s" % (actualTag(child.tag), child.text))
                    pass
                else:
                    tagsWithAttributes[actualTag(child.tag)] = actualTag(child.tag)
                    # writeLog.info("./%s: %s - %s" % (actualTag(child.tag), child.text, child.attrib))

                    for key in child.attrib.keys():
                        # writeLog.info("Attributes are:  Attribute Name (key): %s, Attribute Value (value): %s" % (key, child.attrib[key]))
                        pass

                if actualTag(child.tag) == "device":

                    if (_getXPathText(child, "publicVersionStatus") in ["Delete"]) or (_getXPathText(child, "deviceRecordStatus") in ["Deactivated"]):
                        writeLog.info("Device Deactivated, skipping...")
                        continue

                    companyName = _getXPathText(child, 'companyName')
                    companyPhone = _getXPathText(child, 'phone', ["contacts", "customerContact"])
                    companyEmail = _getXPathText(child, 'email', ["contacts", "customerContact"])
                    brandName = _getXPathText(child, "brandName")

                    valueForBaseline = "%s%s%s%s%s" %(companyName, DELIMITER, companyPhone, DELIMITER, companyEmail)
                    valueForMap = "%s%s%s%s%s%s%s" %(companyName, DELIMITER, companyPhone, DELIMITER, companyEmail, DELIMITER, brandName)

                    companyCountMap = _BuildCompanyMap(companyCountMap, valueForBaseline)
                    companyAnalysisMap = _BuildCompanyMap(companyAnalysisMap, valueForMap)
                    

        writeFile.write("Company Name|Phone|Email|CountOfDeviceIds\n")
        for key, value in companyCountMap.items():
            outputLine = "%s%s%s\n" %(key, DELIMITER, value)
            writeFile.write(outputLine)

        writeFile.write("Company Name|Phone|Email|BrandName|CountOfDeviceIds\n")
        for key, value in companyAnalysisMap.items():
            outputLine = "%s%s%s\n" %(key, DELIMITER, value)
            writeFile.write(outputLine)

        return True
    except:
        writeLog.info("Oh Snap - XML File Processing barfed")
        # readFile.close()
        writeFile.close()
        traceback.print_exc()
        return False


try:
   #############
    # Here calculate the choices of source URLs, destination Paths, and Destination filenames
    #############

    LOAD_FILE_FULL = 'C:/Interfaces/AccessGUDID/Files/GUDID_Full_%s.txt' % (suffix)
    LOAD_FILE_DAILY = 'C:/Interfaces/AccessGUDID/Files/GUDID_Daily_%s.txt' % (dailySuffix)

    if "Daily" in VERSION:
        xmlDailyFileList = _downloadAndUnzip(URL_SOURCE_XML_DAILY, DEST_PATH, DEST_FILE_XML_DAILY)
        if xmlDailyFileList != None and len(xmlDailyFileList) > 0:
            bSuccess = _processListOfXMLFiles(xmlDailyFileList, DEST_PATH, LOAD_FILE_DAILY)

    if "Full" in VERSION:
        xmlFullFileList = _downloadAndUnzip(URL_SOURCE_XML_FULL, DEST_PATH, DEST_FILE_XML_FULL)

        if xmlFullFileList != None and len(xmlFullFileList) > 0:
            bSuccess = _processListOfXMLFiles(xmlFullFileList, DEST_PATH, LOAD_FILE_FULL)

    writeLog.info("Processing Complete for %s." %(VERSION))

except:
    writeLog.info("Oh Snap - Main Routine Failure")
    traceback.print_exc()

