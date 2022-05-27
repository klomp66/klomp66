################################################
# Innovit_SYS_Maintenance_Purge_Reindex_Stats
#
################################################

sys.add_package('java.lang')
sys.add_package('java.sql')
sys.add_package('java.util')

from javax.naming import InitialContext
from java.lang import Long
from java.lang import Class
from java.lang import System
from java.sql import Timestamp
from java.sql import DriverManager
from java.util import ArrayList

from java.util import Collections
from com.innovit.ice.common import NodeType
from com.innovit.id import ObjId
from com.innovit.util import ObjectTuple

print('Running System Maintenance')
totalRuntime = 240*60*1000
startTime = System.currentTimeMillis()

def maintainDatabase(runtime):
    if(System.currentTimeMillis() - startTime > runtime):
        return;

    print('Running Database Maintenance')
    ## Start database maintenance
    # SQL Query to select all indexes of any type except HEAP, where the fragmentation is greater than 5%

    indexStatsQuery = '''select schema_name(t.schema_id)      AS [Schema],
           object_name(ps.object_id)                          AS [Table],
           i.name                                             AS [Index],
           ps.Index_type_desc                                 AS IndexType,
           convert(TINYINT,ps.avg_fragmentation_in_percent)   AS [AvgFrag],
           convert(TINYINT,ps.avg_page_space_used_in_percent) AS [AvgSpaceUsed],
           ps.record_count                                    AS [RecordCnt],
           ps.fragment_count                                  AS [FragmentCnt],
           ps.page_count * ps.avg_fragmentation_in_percent    AS [Weighting]
    FROM sys.dm_db_index_physical_stats(db_id(db_name()),NULL,NULL,NULL,'SAMPLED') ps
    INNER JOIN sys.indexes i
        ON ps.object_id = i.object_id
        AND ps.index_id = i.index_id
    INNER JOIN sys.tables t 
        ON ps.object_id = t.object_id
    WHERE t.is_ms_shipped = 0
    AND ps.Index_type_desc <> 'HEAP'
    AND convert(TINYINT,ps.avg_fragmentation_in_percent) > 5
    ORDER BY [Weighting] DESC'''

    # Setup database connection
    ctx = InitialContext()
    configEJB = ctx.lookup("ejb/ac").create()

    # Query fragmented indexes ordered by a weighting factor
    indexesToProcess = []

    # result is String[][]
    fragmentedIndexes = configEJB.runQuery(indexStatsQuery)
    for fragmentedIndex in fragmentedIndexes[1:]:
        schema = str(fragmentedIndex[0])
        table = str(fragmentedIndex[1])
        index = str(fragmentedIndex[2])
        indexType = str(fragmentedIndex[3])
        fragPct = float(fragmentedIndex[4])
        spaceUsed = float(fragmentedIndex[5])
        weighting = float(fragmentedIndex[8])
        indexesToProcess.append([schema,table,index,fragPct,weighting])
        print('Index '+schema+'.'+table+'.'+index+' type: '+indexType+' is fragmented '+str(fragPct)+' pct. weighting '+str(weighting)+' space used '+str(spaceUsed))

    # Loop thru indexes either REBUILDING or REORGANISING (Until a timelimit is reached)
    for indexToProcess in indexesToProcess:
        if(System.currentTimeMillis() - startTime > runtime):
            break;
        schema = indexToProcess[0]
        table = indexToProcess[1]
        index = indexToProcess[2]
        fragPct = indexToProcess[3]
        weighting = indexToProcess[4]
        if fragPct > -1:
            rebuildQuery = 'ALTER INDEX '+index+' ON '+schema+'.'+table+' REBUILD WITH (FILLFACTOR = 95)'
            print(rebuildQuery)
            configEJB.runQuery(rebuildQuery)
        else: ## Reorganise
            reorgQuery = 'ALTER INDEX '+index+' ON '+schema+'.'+table+' REORGANIZE'
            print(reorgQuery)
            configEJB.runQuery(reorgQuery)
            statsUpdateQuery = 'UPDATE STATISTICS '+schema+'.'+table+' WITH SAMPLE 30 PERCENT'
            print(statsUpdateQuery)
            configEJB.runQuery(statsUpdateQuery)


def purgeOldData(runtime):
    ## Purge any data deleted (If time is available)
    print('Checking purge candidates')

    ctx = InitialContext()
    databasePurge = ctx.lookup("ejb/ak").create()

    # Loop thru Data Node Types and Purge
    relationshipTypeList = ctx.lookup("ejb/as").getRelationshipNodeTypes()
    for relationshipType in relationshipTypeList:
        if(System.currentTimeMillis() - startTime > runtime):
            break;
        candidateTuple = ObjectTuple(NodeType.RELATIONSHIP,relationshipType.getId())
        candidatesAll = databasePurge.getPurgeCandidates(candidateTuple, 0)
        candidates = databasePurge.getPurgeCandidates(candidateTuple, 0)#, Timestamp(0), Timestamp(System.currentTimeMillis()-365*24*60*1000))
        print('Found '+str(candidatesAll.size())+' relationship purge candidates of type '+str(relationshipType.getSrcToDestName()))
        #Collections.sort(candidates)
        #Collections.reverse(candidates)
        while not candidates.isEmpty() :
            if(System.currentTimeMillis() - startTime > runtime):
                break;
            batch = ArrayList()
            while batch.size() < 900 and not candidates.isEmpty() :
                   batch.add(Long(candidates.remove(candidates.size()-1)))
            databasePurge.purgeRecords(batch, candidateTuple, ObjId(getCurrentUserId()), None, False, None, None)
            print('Purged '+str(batch.size())+' records. '+str(candidates.size())+' remaining')

    # Loop thru Data Node Types and Purge
    nodeTypeDataList = ctx.lookup("ejb/be").getDataNodeTypes(False)
    for nodeTypeData in nodeTypeDataList:
        if(System.currentTimeMillis() - startTime > runtime):
            break;
        candidateTuple = ObjectTuple(NodeType.DATA,nodeTypeData.getId())
        candidatesAll = databasePurge.getPurgeCandidates(candidateTuple, 0)
        candidates = databasePurge.getPurgeCandidates(candidateTuple, 0)#, Timestamp(0), Timestamp(System.currentTimeMillis()-365*24*60*1000))
        print('Found '+str(candidatesAll.size())+' data purge candidates of type '+str(nodeTypeData.getName()))
        print('Found '+str(candidates.size())+' data purge candidates of type '+str(nodeTypeData.getName())+' over 1 year old')
        #Collections.sort(candidates)
        #Collections.reverse(candidates)
        while not candidates.isEmpty() :
            if(System.currentTimeMillis() - startTime > runtime):
                break;
            batch = ArrayList()
            while batch.size() < 900 and not candidates.isEmpty() :
                   batch.add(Long(candidates.remove(candidates.size()-1)))
            databasePurge.purgeRecords(batch, candidateTuple, ObjId(getCurrentUserId()), None, False, None, None)
            print('Purged '+str(batch.size())+' records. '+str(candidates.size())+' remaining')

purgeOldData(long(totalRuntime/2))
maintainDatabase(totalRuntime)
purgeOldData(totalRuntime)

if(System.currentTimeMillis() - startTime > totalRuntime):
    print('Time limit reached. Exiting System Maintenance')
