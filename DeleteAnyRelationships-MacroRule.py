###########################################
# BBG_DeleteAnyRelationships-MacroRule
# Created Dec 19, 2019 Jeff van't Slot
# Identify any SAP_MASTER-GDSN relationships with a given nodeID in Submission view, and whack it
##########################################

#runEditRuleWithName('Innovit_MDM_Functions')

from java.awt import Cursor
from com.innovit.ice.client.ui import AdminController

glassPane = AdminController.getIceFrame().getGlassPane();

nodeList = getCurrentNodeIds()
nCounter = 0

glassPane.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
glassPane.setVisible(True)

relNameList = ['SAP_MASTER-GDSN', 'SAP_MASTER-GUDID', 'SAP_MASTER-ATWRT_TEXT', 'SAP_MASTER-CLASSIF_MARA', 'SAP_MASTER-MAKT', \
			   'SAP_MASTER-MARA', 'SAP_MASTER-MARKETING_TEXT', 'SAP_MASTER-MARM', 'SAP_MASTER-MVKE', 'SAP_MASTER-TARGETMARKET', \
			   'GDSN Packaging Hierarchy', 'GUDID Packaging Hierarchy', 'CLASSIF_MARA-ATWRT_TEXT', 'MARA-CLASSIF_MARA', 'MARA-MAKT', \
			   'MARA-MARKETING_TEXT', 'MARA-MARM', 'MARA-MVKE', 'MARA-TARGETMARKET', 'GUDID_MAINT_TO_GUDID_SUBMISSION']

for nodeId in nodeList:

	for relName in relNameList:
		# retrieve a list of relationships for this node
		relIdList = getExistingRelationships(nodeId, relName)

		# Delete these relationships
		if len(relIdList) >= 1:
			removeExistingRelationships(relIdList)
			nCounter += 1

		if nCounter >= 1000:
			nCounter = 0
			forceSave(True)

glassPane.setCursor(Cursor.getDefaultCursor());
glassPane.setVisible(false)

forceSave(True)

