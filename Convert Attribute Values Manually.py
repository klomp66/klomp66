#############################################
# Created April 17, 2020 Jeff van't Slot
# In case automated conversion fails
# resetAttributesUpdateState only works on server level.  This cannot be executed as a client-side macro
# This edit rule needs to be executed as a scheduled task.
#############################################

#OPER_EQUALS = 1;
#OPER_LT = 2;
#OPER_GT = 3;
#OPER_CONTAINS = 4;
#OPER_LE = 5;
#OPER_GE = 6;
#OPER_NE = 7;
#OPER_NOT_CONTAINS = 8;
#OPER_STARTS_WITH = 9;
#OPER_ENDS_WITH = 10;
#OPER_KEYWORD_SEARCH = 11;
#OPER_IS_EMPTY = 12;
#OPER_BETWEEN = 13;
#OPER_NOT_EXISTS = 14;
#OPER_EXISTS = 15;


# Search Criteria Specifications
PERSPECTIVE_NAME = '<Enter the perspective (System View) name for the attribute(s) to change>'
DATA_TYPE_NAME = '<Enter the Data Type for the attribute(s) to change>'
ATTRIBUTE_NAME = '<Enter the Attribute Name to be searching for>'
ATTRIBUTE_VALUE = '<Enter the search value for this attribute>'

PROCESS_ID_GDSN = 'gs1'
PROCESS_ID_GUDID = 'udi'

orgId = getCurrentOrganisationId()
persId = getOrgPerspectiveByName(PERSPECTIVE_NAME, orgId)
dntTypeId = getDataNodeTypeIdByName(DATA_TYPE_NAME)
cValueToSearch = ATTRIBUTE_VALUE

nCounter = 0

criteriaNodeList = searchForNodes(dntTypeId,[getAttributeId(ATTRIBUTE_NAME)], None, [cValueToSearch], [nodeLibrary.OPER_EQUALS], [persId], orgId)

if len(criteriaNodeList) >= 1:

	for nodeId in criteriaNodeList:

		# Actual update logic goes here.  Example below
		attrName = 'isTradeItemAService'

		if (getAttributeValue(nodeId, attrName) == "true") or (getAttributeValue(nodeId, attrName) == "True"):
			setAttributeValue(nodeId, attrName, 'Y')
			print('Changed %s to Y' %(attrName))
			# double check the PROCESS_ID depending on whether it's a GDSN or GUDID item
			resetAttributesUpdateState(nodeId, PROCESS_ID, [attrName])
			nCounter += 1

		elif (getAttributeValue(nodeId, attrName) == "false") or (getAttributeValue(nodeId, attrName) == "False"):
			setAttributeValue(nodeId, attrName, 'N')
			print('Changed %s to N' % (attrName))
			# double check the PROCESS_ID depending on whether it's a GDSN or GUDID item
			resetAttributesUpdateState(nodeId, PROCESS_ID, [attrName])
			nCounter += 1

else:
	print('No search items were found to update')

print('Updated %s records' %(nCounter))
