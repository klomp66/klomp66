###################################
# B. Braun GDSN Trigger Rule
# Created Jan 15, 2020 - Jeff van't Slot
# Relies on composite attribute, "GDSN_Message" containing four attributes:
#	GDSN_MessageType
#	GDSN_MessageEvent
#	GDSN_MessageDate
#	GDSN_MessageDetail
###################################

#Message Types:  "CR", "CIN" "CIP"
#Message Events CR: "MODIFIED", "MODIFY_FAILED", "ADDED", "ADD_FAILED"
#Message Events CIN:  "CHANGED", "CHANGE_FAILED", "CORRECTED", "CORRECT_FAILED"
#Message Events CIP:  "PUBLISHED_NEW"

#Process ID is retrieved from server.properties file in the dataModificationTracker line
PROCESS_ID = 'gs1'

from java.util import Date

def flagItems():
	# loop through each of the nodes and flag it for email if not already set
	nodeIds = getCurrentNodeIds()
	for nodeId in nodeIds:

		messageType = '%s' % (getGDSNMessageType())
		messageEvent = '%s' %(getGDSNMessageEvent(nodeId))
		messageDetail = '%s' %(getGDSNMessageDetail(nodeId))

		if messageDetail != None:
			# make sure it's not longer than 400 char
			trimMessageDetail = messageDetail[:400]

		# Update the GDSN Message attributes
		setAttributeValue(nodeId, ["GDSN_Message", "GDSN_MessageType"], messageType)
		setAttributeValue(nodeId, ["GDSN_Message", "GDSN_MessageEvent"], messageEvent)
		setAttributeValue(nodeId, ["GDSN_Message", "GDSN_MessageDate"], Date().getTime())
		setAttributeValue(nodeId, ["GDSN_Message", "GDSN_MessageDetail"], trimMessageDetail)

		resetAttributesUpdateState(nodeId, PROCESS_ID, ['GDSN_MessageType', 'GDSN_MessageEvent', 'GDSN_MessageDate', 'GDSN_MessageDetail'])

		#Set customer attributes per whatever criteria

		# restrict this update only to confirmation of upload message types
		if messageType in ['CR', 'CIN'] and messageEvent not in ['CHANGE_FAILED', 'CORRECT_FAILED']:
			setAttributeValue(nodeId, "GDSN Status", "UNCHANGED")

		# Reset any updateState so the record won't automatically get selected again for upload due to these changes
		resetAttributesUpdateState(nodeId, PROCESS_ID, ['GDSN Status'])
		resetUpdateState(nodeId, PROCESS_ID)
	return None

# trigger the rule now
flagItems()
