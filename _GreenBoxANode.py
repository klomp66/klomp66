###################################################################
# _GreenBoxANode
# Created 2012/04/23 JvS
# Take any node, check each attribute for changes, and put a green box around it
# NOTE THIS ONLY WORKS IN A CLIENT WORKSPACE, not a server background job.
# "getPreviousValue()" compares client value with server value.  That's not possible in a server task.
##################################################################

def _greenBoxANode(nodeId, ontologyName, processName='gs1'):

    attrNameList = getOntologyAttributeNames(ontologyName)

    for attrName in attrNameList:
        previousVal = ""
        attrUpdateState = getAttributeUpdateState(nodeId, processName, attrName)
        if attrUpdateState == "C": #Changed
            previousVal = getPreviousValue(attrName)
            message = "Attribute %s has changed from %s to %s" %(attrName, previousVal, getAttributeValue(nodeId, attrName))
            addInfoMessage(nodeId, attrName, message, 0)

    return None

def _removeGreenBoxes(nodeId, ontologyName):

    attrNameList = getOntologyAttributeNames(ontologyName)

    for attrName in attrNameList:
        messages = getInfoMessages(nodeId, attrName, 0)

        if messages != None and len(messages) > 0:
            for message in messages:
                removeInfoMessages(nodeId, attrName, message, 0)

    return None
