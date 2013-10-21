from collections import defaultdict

import utilities
import docreader
from docreader import Doc # needed for pickling call
import document_counter
import clustering


collectionDir = "Data_dummy/collection2"
topicFile = "Data_dummy/original_topics.txt"
docFileNames  = utilities.getFileNames(collectionDir)
stopwordsFile = "stopwords.txt"

def getDocs(loadFileName=None, saveFileName=None):
  
  drm = docreader.DocReaderManager(docFileNames , stopwordsFile)
  docList = drm.getDocs(loadFileName)
  
  if saveFileName != None: 
    drm.saveDocs(saveFileName)

  queries = docreader.readQueries(topicFile)
  queryWords = docreader.queriesToTermList(queries)
   
  return (docList, queryWords)


def makeVectors(queryWords, docList):
  
  dcm = document_counter.DocCounter(queryWords=queryWords, docList=docList)
  
  queryDict = dcm.getQuerySensesDict()
  docDict =  dcm.getDocInstancesDict()
  contextWords = dcm.finalContextWords
  
  return (queryDict, docDict, contextWords)


# TODO fix buckshot clustering fails with sparse data
def clusterQueryVectors(queryWords, allContextWords, queryVectorDict):
  
  k_values = range(1,4)
  
  scm = clustering.SenseClusterManager(queryWords, queryVectorDict, allContextWords)
  
  scm.cluster()
  
  queriesSensesDict = scm.getResult()
  
  return queriesSensesDict



def writeToCSV(queriesSensesDict, docVectorDict):
  
  # write query senses and document instances to csv file
  
  pass
  
  

if __name__ == '__main__': #if this file is the argument to python
  
  (docList, queryWords) = getDocs(loadFileName="alldocs.dat")
  
  (queryVectorDict, docVectorDict, contextWords) = makeVectors(queryWords, docList)
  
  queriesSensesDict = clusterQueryVectors(queryWords, contextWords, queryVectorDict)
  
  print utilities.getDictString(queriesSensesDict)
  
  writeToCSV(queriesSensesDict, docVectorDict)
