#####################################
# _ZZ_XML_FileHandler
# Attempt to see if I can make sense of XML files in Python
# Without help LOL
#####################################

import logging
import re
import xml.etree.ElementTree as ET

#runEditRuleWithName('_Custom_MDM_Functions')

#logFileName = 'C:\\Users\\PhotonUser\\My Files\\Temporary Files\\xmlHandling.log'
#xmlFileName = 'C:\\Users\\PhotonUser\\My Files\\Temporary Files\\udid_export_2020_05_11.xml'
#xmlFileName = 'C:\\Users\\PhotonUser\\My Files\\Temporary Files\\FULLDownload_Part1_Of_103_2020-06-01.xml'

logFileName = 'C:\\Users\\jeffv\\Desktop\\xmlHandling.log'
xmlFileName = 'C:\\Users\\jeffv\\Desktop\\udid_export_2020_05_11.xml'
#xmlFileName = 'C:\\Users\\jeffv\\Desktop\\FULLDownload_Part1_Of_103_2020-06-01.xml'


# LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
LOG_FORMAT = "%(message)s"

logging.basicConfig(filename=logFileName, \
                    level=logging.DEBUG, \
                    format=LOG_FORMAT, \
                    filemode='w')  # filemode='w' will overwrite the log each time

writeLog = logging.getLogger()
writeLog.info("Starting XML Handling")

writeLog.info("Writing to log file: %s" %(logFileName))
writeLog.info("Xml file to read is: %s" %(xmlFileName))

nsXPATH = ''
XPATH = ''

GUDID_ONTOLOGY_NAME = 'GUDID_Item'

orgId = getCurrentOrganisationId()
persName = 'GUDID_Item'

gudidAttrIds = getOntologyAttributeIds(GUDID_ONTOLOGY_NAME)
gudidAttrNames = getOntologyAttributeNames(GUDID_ONTOLOGY_NAME)

gudidUniqueAttrNames = ['primaryDINumber', 'labelerDUNSNumber', 'issuingAgency']
XMLUniqueTagMappings = ['deviceId', 'dunsNumber','deviceIdIssuingAgency']

nameSpace = ""

# Note I had to add a lower case 'r' ahead of the path string for some reason, otherwise I got parser error
# tree = ET.parse(r'C:\Users\jeffvs\GUDID_InitialLoad.xml')
#root = tree.root
#nameSpace = re.match(r'{.*}', root.tag).group(0)

def actualTag(tag):
    return tag[(len(nameSpace) - len(tag)):]

def fullTag(tag):
    return nameSpace + tag

def _getUniqueGUDIDAttrVals(xmlNode):
    # Node at this point is a child node and "device" has been identified.
    # the 'labelerDUNSNumber' is a child of this node, xpath './device/dunsNumber'
    # the primaryDINumber and issuing agency is down a few:
    # './device/identifiers/identifier/deviceId'
    # './device/identifiers/identifier/deviceIdIssuingAgency'
    attrVals = []

    xpathPrimaryDINo = "./%s/%s/%s" %(fullTag("identifiers"), fullTag("identifier"), fullTag("deviceId"))
    primaryDINo = xmlNode.find(xpathPrimaryDINo).text

    xpathDUNSNo = "./%s" %(fullTag("dunsNumber"))
    labelerDuns = xmlNode.find(xpathDUNSNo).text

    xpathIssuingAgency = "./%s/%s/%s" % (fullTag("identifiers"), fullTag("identifier"), fullTag("deviceIdIssuingAgency"))
    issuingAgency = xmlNode.find(xpathIssuingAgency).text

    writeLog.info('Unique Attribute Values found for prim.di and labeler duns and issAgncy:  %s, %s, %s' %(primaryDINo, labelerDuns, issuingAgency))

    attrVals.append(primaryDINo)
    attrVals.append(labelerDuns)
    attrVals.append(issuingAgency)

    return attrVals

def _getXPathText(xmlNode, tag, XPathList = []):
    # XPathList is a list of XPATHs, given as simple tags, need to be filled out and then text values retrieved.
    # This list starts from the calling point, not from the root.
    xpath = "./"

    if XPathList != []:
        for pathTag in XPathList:
            xpath = "%s/%s" %(xpath, fullTag(pathTag))

    xpath = "%s/%s" %(xpath, fullTag(tag))
    retVal = xmlNode.find(xpath).text

    if retVal in [None, "", "None", "Null"]:
        return None
    else:
        if retVal == "false":
            return "No"
        if retVal == "true":
            return "Yes"

        return retVal


def _createGUDIDNode(attrNames, attrVals):
    orgId = getCurrentOrganisationId()
    persName = "GUDID_Item"
    RQ_DATATYPE = "GUDID_Item"

    gudidNode = createNodes(orgId, persName, attrNames, [attrVals], RQ_DATATYPE)[0]

    return gudidNode


# execution begins here:
writeLog.info('Getting the tree iterparse thing now..')
tree = ET.iterparse(xmlFileName, events=("start", "end"))
context = iter(tree)
event, root = context.next()

nameSpace = re.match(r'{.*}', root.tag).group(0)

writeLog.info("nameSpace: %s" %(nameSpace))
writeLog.info("Root tag is: %s" %(actualTag(root.tag)))

for event, elem in context:
    if event == 'start':
        if actualTag(elem.tag) == 'device':
            writeLog.info("Device Found %s" %(actualTag(elem.tag)))
            recordPublishDate = elem.find(fullTag("devicePublishDate")).text
            writeLog.info("Record Publish Date: %s"%(recordPublishDate))
    if event == 'end':
        if actualTag(elem.tag) == 'device':
            root.clear()
    elem.clear()


    # Discard the element and clear memory for every element it runs into

root.clear()

