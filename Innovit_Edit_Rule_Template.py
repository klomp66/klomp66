#######################################
# <<<EDIT RULE NAME>>>
# Created 12/29/2020 JvS
# <<<EDIT RULE DESCRIPTION>>>
########################################
#<<<IMPORTS>
#runEditRuleWithName('')

# CONSTANTS DECLARATION
PERSPECTIVE_NAME = ""
ITEM_DATA_TYPE = ""
PROCEDURE_NAME = ""

def _processRetrievedRecords(nodeBatch):
    ### CONSULTANT:  Describe the process that will occur here

    return #<<whatever>>


def _getRecordsToBeProcessed():
    ### This forms the data selection to be used for processing
    orgId = getCurrentOrganisationId()
    persId = getOrgPerspectiveByName(PERSPECTIVE_NAME, orgId)
    dataTypeId = getDataNodeTypeIdByName(ITEM_DATA_TYPE)

    attrIds = []
    attrOperators = []
    attrValues = []

    # Selection criteria
    attrIds.append(getAttributeId("<<ATTR_NAME>>"))
    attrOperators.append(nodeLibrary.OPER_EQUALS)
    attrValues.append("<<<VALUE OF ATTR_NAME>>>")

    #<<<REPEAT AS NEEDED>>>

    nodeList = searchForNodes(dataTypeId, attrIds, None, attrValues, attrOperators, [persId], orgId)

    cmf_printDebug("%s searchForNodes returned %s records." % (PROCEDURE_NAME, len(nodeList)))

    return nodeList


# rule begins here
try:
    BATCH_SIZE = 60
    startTime = Date().getTime()
    nodeIds = _getRecordsToBeProcessed()
    numRecs = len(nodeIds)
    nodeBatches = chunks(nodeIds, BATCH_SIZE)
    batchCounter = 0
    for nodeBatch in nodeBatches:
        batchTimer = Date().getTime()
        ensureDataNodesLoaded(nodeBatch)
        cmf_print("Now Processing Batch %s of total %s batches.." %(batchCounter, len(nodeBatches)))
        batchCounter += 1
        _processRetrievedRecords(nodeBatch)

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

    jobTime = float((Date().getTime() - startTime) / 1000)
    cmf_print("%s STATS:  TOTAL TIME taken for job: %s seconds" %(PROCEDURE_NAME, jobTime))

    cmf_print("%s Complete" %(PROCEDURE_NAME))
except:
    cmf_print('PROBLEM running %s' %(PROCEDURE_NAME))
    traceback.print_exc()
    pass
