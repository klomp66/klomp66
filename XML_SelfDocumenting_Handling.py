#####################################
# _ZZ_XML_FileHandler
# Attempt to see if I can make sense of XML files in Python
# Without help LOL
#####################################

import logging
import re
import xml.etree.ElementTree as ET

logFileName = 'C:\\Interfaces\\AccessGUDID\\AccessGUDID_Documenter.log'
xmlFileName = 'C:\\Interfaces\\AccessGUDID\\Files\\FULLDownload_Part1_Of_115_2021-03-01.xml'
#logFileName = 'C:\\Users\\PhotonUser\\My Files\\Temporary Files\\xmlHandling.log'
#xmlFileName = 'C:\\Users\\PhotonUser\\My Files\\Temporary Files\\udid_export_2020_05_11.xml'

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

# Note I had to add a lower case 'r' ahead of the path string for some reason, otherwise I got parser error
# tree = ET.parse(r'C:\Users\jeffvs\GUDID_InitialLoad.xml')
tree = ET.parse(xmlFileName)

root = tree.getroot()

nameSpace = re.match(r'{.*}', root.tag).group(0)

def actualTag(tag):
    return tag[(len(nameSpace) - len(tag)):]

def fullTag(tag):
    return nameSpace + tag


writeLog.info("nameSpace = %s" % (nameSpace))
writeLog.info("root.tag: %s" % (root.tag))
writeLog.info("root.attrib: %s" % (root.attrib))
writeLog.info("Actual root tag = %s" % (actualTag(root.tag)))
writeLog.info("Full tag for Jeff: %s" % (fullTag("Jeff")))

tagsWithAttributes = {}

for child in root:
    if child.attrib == {} or child.attrib == {'{http://www.w3.org/2001/XMLSchema-instance}nil': 'true'}:
        writeLog.info("./%s: %s" % (actualTag(child.tag), child.text))
    else:
        tagsWithAttributes[actualTag(child.tag)] = actualTag(child.tag)
        writeLog.info("./%s: %s - %s" % (actualTag(child.tag), child.text, child.attrib))

        for key in child.attrib.keys():
            writeLog.info("Attributes are:  Attribute Name (key): %s, Attribute Value (value): %s" % (key, child.attrib[key]))

    if len(child) >= 1:
        writeLog.info("This item %s has %s children" %(actualTag(child.tag), len(child)))

    for grandchild in child:
        if grandchild.attrib == {} or grandchild.attrib == {'{http://www.w3.org/2001/XMLSchema-instance}nil': 'true'}:
            writeLog.info("./%s/%s: %s" % (actualTag(child.tag), actualTag(grandchild.tag), grandchild.text))
        else:
            tagsWithAttributes[actualTag(grandchild.tag)] = actualTag(grandchild.tag)
            writeLog.info("./%s/%s: %s - %s" % (actualTag(child.tag), actualTag(grandchild.tag), grandchild.text, grandchild.attrib))

            for key in grandchild.attrib.keys():
                writeLog.info("Attributes are:  Attribute Name (key): %s, Attribute Value (value): %s" % (key, grandchild.attrib[key]))

        if len(grandchild) >= 1:
            writeLog.info("This item %s has %s children" % (actualTag(grandchild.tag), len(grandchild)))

        for greatgrandchild in grandchild:
            if greatgrandchild.attrib == {} or greatgrandchild.attrib == {'{http://www.w3.org/2001/XMLSchema-instance}nil': 'true'}:
                writeLog.info("./%s/%s/%s: %s" % (actualTag(child.tag), actualTag(grandchild.tag), actualTag(greatgrandchild.tag), greatgrandchild.text))
            else:
                tagsWithAttributes[actualTag(greatgrandchild.tag)] = actualTag(greatgrandchild.tag)
                writeLog.info("./%s/%s/%s: %s - %s" % (actualTag(child.tag), actualTag(grandchild.tag), actualTag(greatgrandchild.tag), greatgrandchild.text, greatgrandchild.attrib))

                for key in greatgrandchild.attrib.keys():
                    writeLog.info("Attributes are:  Attribute Name (key): %s, Attribute Value (value): %s" % (key, greatgrandchild.attrib[key]))

            if len(greatgrandchild) >= 1:
                writeLog.info("This item %s has %s children" % (actualTag(greatgrandchild.tag), len(greatgrandchild)))

            for greatgreatgrandchild in greatgrandchild:
                if greatgreatgrandchild.attrib == {} or greatgreatgrandchild.attrib == {'{http://www.w3.org/2001/XMLSchema-instance}nil': 'true'}:
                    writeLog.info("./%s/%s/%s/%s: %s" % (actualTag(child.tag), actualTag(grandchild.tag), actualTag(greatgrandchild.tag), actualTag(greatgreatgrandchild.tag), greatgreatgrandchild.text))
                else:
                    tagsWithAttributes[actualTag(greatgreatgrandchild.tag)] = actualTag(greatgreatgrandchild.tag)
                    writeLog.info("./%s/%s/%s/%s: %s - %s" % (actualTag(child.tag), actualTag(grandchild.tag), actualTag(greatgrandchild.tag), actualTag(greatgreatgrandchild.tag), greatgreatgrandchild.text, greatgreatgrandchild.attrib))
                    for key in greatgreatgrandchild.attrib.keys():
                        writeLog.info("Attributes are:  Attribute Name (key): %s, Attribute Value (value): %s" %(key, greatgreatgrandchild.attrib[key]))

# "size" at L4 has attributes "value" and "unit"
# "storageHandlingHigh" at L4 has attributes "value" and "unit"
# "storageHandlingLow" at L4 has attributes "value" and "unit"

writeLog.info("Tags with Attributes in them:")
writeLog.info(tagsWithAttributes)

# for elem in root.iter():
#    print("elem.tag: %s" %(elem.tag))

# print(ET.tostring(root, encoding='utf8').decode('utf8'))
# Not sure what all the "ns0" prefixes have to do with anything, they're not in the original xml file

#emailList = {}
#for email in root.iter(fullTag('email')):
#    emailList[email.text] = email.text

#print(emailList)
