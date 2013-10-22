from collections import defaultdict

import utilities
import docreader
from docreader import Doc # needed for pickling call
import document_counter
import clustering
import similaritiesWriter


collectionDir = "Data_dummy/collection"
topicFile = "Data_dummy/original_topics.txt"
docFileNames  = utilities.getFileNames(collectionDir)
stopwordsFile = "stopwords.txt"
similaritiesFileName = 'similarities2.csv'

def getDocs(loadFileName=None, saveFileName=None):
  
  drm = docreader.DocReaderManager(docFileNames , stopwordsFile)
  docList = drm.getDocs(loadFileName)
  
  if saveFileName != None: 
    drm.saveDocs(saveFileName)

  queries = docreader.readQueries(topicFile)
  queryWords = docreader.queriesToTermList(queries)
  queriesList = docreader.processedQueries(queries)
   
  return (docList, queryWords, queriesList, queries)


def makeVectors(queryWords, docList):
  
  
  dcm = document_counter.DocCounter(queryWords=queryWords, docList=docList)
  
  queryDict = dcm.getQuerySensesDict()
  docDict =  dcm.getDocInstancesDict()
  contextWords = dcm.finalContextWords
  
  return (queryDict, docDict, contextWords)


def clusterQueryVectors(queryWords, allContextWords, queryVectorDict):
  
  k_values = range(1,4)
  
  scm = clustering.SenseClusterManager(queryWords, queryVectorDict, allContextWords)
  
  scm.cluster()
  
  queriesSensesDict = scm.getResult()
  
  return queriesSensesDict


 

if __name__ == '__main__': #if this file is the argument to python
  
  (docList, queryWords, queries, raw_queries) = getDocs(saveFileName="alldocs.dat")
  
  print "%d docs. " % len(docList)
  
  (queryVectorDict, docVectorDict, contextWords) = makeVectors(queryWords, docList)
  
  queriesSensesDict = clusterQueryVectors(queryWords, contextWords, queryVectorDict)
  
  #print utilities.getDictString(queriesSensesDict)
  #print queriesSensesDict.keys()
  
  print "%d docs in docVectorList" % len(docVectorDict.keys())
  
  similaritiesWriter.write_similarities_to_CSV(similaritiesFileName, queriesSensesDict, docVectorDict, queries, contextWords, raw_queries)
