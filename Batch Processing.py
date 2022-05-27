################################################
# Example of using batches to improve performance
# All elements of how to use it are in here.
# Nodes are kept in the database.  Whenever you process a node, it has to check first to see if that nodeId is
# loaded into the execution workspace.  If not, and usually not, it has to first be retrieved
# from the database and loaded into the workspace.  This takes time, so by batching, you can ensure
# that the batch of nodeIds to be processed are all loaded into memory first, then do them all at the same time.
################################################

BATCH_SIZE = 50

def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


nodeList = getCurrentNodeIds()

# Break out the probably large node list into batches of 50, to process 50 at a time in batch, performance improves
nodeBatches = chunks(nodeIds, BATCH_SIZE)

# So each list item of nodeBatches will contain a list of (n=BATCH_SIZE) nodeIds
# Cycle through these, each time ensuring that the smaller list is loaded.

for nodeBatch in nodeBatches:
    # Make sure each batch of 50 is loaded
    ensureDataNodesLoaded(nodeBatch)  #subsequent options def True: LoadStates, loadDeleted, loadParentOrgIds, LoadMessages

    # Now process them without having to do separate reads from database each time
    for nodeId in nodeBatch:
        if not isItemChanged(nodeId, attrList, GS1_PROCESS_ID):
            continue
        setAttributeValue(nodeId, "View_Created_Date", Date().getTime())
        setAttributeValue(nodeId, ["Approval Status", "approvalStatus"], "Not Approved")
        setAttributeValue(nodeId, ["Approval Status", "approvalDate"], Date().getTime())
        setAttributeValue(nodeId, ["Approval Status", "approvalUser"], None)

    # This takes both a list or individual node Id so send in the batch of nodes to reset
    resetUpdateState(nodeBatch, GS1_PROCESS_ID)
