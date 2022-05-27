###############################
# AttributeLookupFrom
# Creates a drop-down of available Minor Purchase Class values
# Created 20201209 JvS
###############################

runEditRuleWithName("_Custom_MDM_Functions")

def _getPicklistFromURC(URCGroupName, URCParentName):
    from jarray import array
    from java.lang import String

    attrLOV = []
    URCMap = cmf_getURCList(URCGroupName, URCParentName)

    for key in URCMap.keys():
        # Append the descriptions for lookups
        lookupValue = '%s (%s)' % (key, URCMap[key])
        attrLOV.append(lookupValue)

    attrLOV.sort()
    return attrLOV

#    setCellEditorDefaultValue(attrname, array(attrLOV, String))
