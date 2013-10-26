from collections import defaultdict

import utilities
import docreader
from docreader import Doc # needed for pickling call
import document_counter
import clustering
import similaritiesWriter


collectionDir = "data1/docs"
topicFile = "data1/original_topics.txt"
docFileNames  = utilities.getFileNames(collectionDir)
stopwordsFile = "stopwords.txt"
similaritiesFileName = 'similarities.csv'

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


  dcm = document_counter.DocCounter(queryWords=queryWords, docList=docList, maxContextWords=150)

  queryDict = dcm.getQuerySensesDict()
  docDict =  dcm.getDocInstancesDict()
  contextWords = dcm.finalContextWords

  return (queryDict, docDict, contextWords)


def clusterQueryVectors(queryWords, allContextWords, queryVectorDict):

  k_values = range(1,7)

  scm = clustering.SenseClusterManager(queryWords, queryVectorDict, allContextWords)

  scm.cluster()

  queriesSensesDict = scm.getResult()

  return queriesSensesDict


def writeStatsOccurrences(queryVectorDict) :
  try:
    f = open("occstats2.txt", "w")
    try:
      totalOcc = 0
      for query in queryVectorDict:
        nrOcc = len(queryVectorDict[query])
        totalOcc += nrOcc

        f.write(query + '\n') # Write a string to a file
        f.write('\t' + str(nrOcc) + '\n')

      f.write('Average:\n') # Write a string to a file
      f.write('\t' + str(nrOcc/float(len(queryVectorDict))) + '\n')
    finally:
      f.close()
  except IOError:
    pass

def writeStatsClustering(queriesSensesDict) :
  try:
    f = open("clusterstats2.txt", "w")
    try:
      nrTotal = 0
      for query in queriesSensesDict:
        nrSenses  = len(queriesSensesDict[query])
        nrTotal += nrSenses

        f.write(query + '\n') # Write a string to a file
        f.write('\t' + str(nrSenses) + '\n')

      f.write('Average:\n') # Write a string to a file
      f.write('\t' + str(nrTotal/float(len(queriesSensesDict))) + '\n')
    finally:
      f.close()
  except IOError:
    pass

if __name__ == '__main__': #if this file is the argument to python

 # (docList, queryWords, queries, raw_queries) = getDocs(loadFileName="alldocs2.dat")

  #print "%d docs. " % len(docList)
  #print "queries: %s " % queries

  queries = docreader.readQueries(topicFile)
  queryWords = docreader.queriesToTermList(queries)
  queriesList = docreader.processedQueries(queries)

  print queriesList

  total = 0
  for q in queriesList:
    total += len(q)

  print total/float(len(queriesList))

  #print "avg doc len: %2.2f" % avgLen

  """
  (queryVectorDict, docVectorDict, contextWords) = makeVectors(queryWords, docList)

  writeStatsOccurrences(queryVectorDict)

  print "clustering query vectors"
  queriesSensesDict = clusterQueryVectors(queryWords, contextWords, queryVectorDict)

  writeStatsClustering(queriesSensesDict)

  #print utilities.getDictString(queriesSensesDict)
  print queriesSensesDict.keys()

  print "%d docs in docVectorList" % len(docVectorDict.keys())

  print "writing similarities to csv"
  similaritiesWriter.write_similarities_to_CSV(similaritiesFileName, queriesSensesDict, docVectorDict, queries, contextWords, raw_queries)
  """
