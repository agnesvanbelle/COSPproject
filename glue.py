from collections import defaultdict

import utilities
import docreader
from docreader import Doc # needed for pickling call
import document_counter
import clustering
import similaritiesWriter
import supervised
import argparse

collectionDir = "Data_dummy/collection"
topicFile = "../data1/original_topics.txt"
docFileNames  = utilities.getFileNames(collectionDir)
stopwordsFile = "stopwords.txt"

def getDocs(loadFileName=None, saveFileName=None):

  drm = docreader.DocReaderManager(docFileNames , stopwordsFile)
  docList = drm.getDocs(loadFileName)

  if saveFileName != None:
    drm.saveDocs(saveFileName)

  queries = docreader.readQueries(topicFile)
  queryWords = docreader.queriesToTermList(queries)
  queriesList = docreader.processedQueries(queries)

  return (docList, queryWords, queriesList, queries)


def makeVectors(queryWords, docList, vpt):


  dcm = document_counter.DocCounter(queryWords=queryWords, docList=docList, maxContextWords=50, variancePerTerm=vpt)

  queryDict = dcm.getQuerySensesDict()
  docDict =  dcm.getDocInstancesDict()
  contextWords = dcm.finalContextWords

  print " len(queryDict): %s" % len(queryDict)
  
  return (queryDict, docDict, contextWords)


def clusterQueryVectors(queryWords, allContextWords, queryVectorDict, variancePerTerm):

  k_values = range(2,7)

  scm = clustering.SenseClusterManager(queryWords, queryVectorDict, allContextWords, k_values, variancePerTerm)

  scm.cluster()

  queriesSensesDict = scm.getResult()

  return queriesSensesDict


def writeStatsOccurrences(queryVectorDict) :
  try:
    f = open("occstats.txt", "w")
    try:
      totalOcc = 0
      for query in queryVectorDict:
        nrOcc = len(queryVectorDict[query])
        totalOcc += nrOcc

        f.write(query + '\n') # Write a string to a file
        f.write('\t' + str(nrOcc) + '\n')

      f.write('Average:\n') # Write a string to a file
      f.write('\t' + str(totalOcc/float(len(queryVectorDict))) + '\n')
    finally:
      f.close()
  except IOError:
    pass

def writeStatsClustering(queriesSensesDict) :
  try:
    f = open("clusterstats.txt", "w")
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

def printAvgLen(docList):
  total=0.0
  for d in docList:
    total += len(d.mainContent)

  avgLen = total / float(len(docList))

  print "avgLen: %2.2f" % avgLen


def automatic_similarities(variancePerTerm=False):
  similaritiesFileName = 'similarities.csv'

  (docList, queryWords, queries, raw_queries) = getDocs(loadFileName="alldocs.dat")

  print "%d docs. " % len(docList)

  (queryVectorDict, docVectorDict, contextWords) = makeVectors(queryWords, docList, variancePerTerm)

  print "len queryVectorDict: %d" % len(queryVectorDict)
  
  #print "contextWords: %s" % contextWords
  #print "queryWords: %s" % queryWords
  
  writeStatsOccurrences(queryVectorDict)


  for q in queryVectorDict:
    for k in queryVectorDict[q]:
      for w in queryVectorDict[q][k]:
        print "%s:%s - %2.2f" % (q,w,queryVectorDict[q][k][w])
      
  queriesSensesDict = clusterQueryVectors(queryWords, contextWords, queryVectorDict, variancePerTerm)

  """
  print "queriesSensesDict: " 
  for  q in queriesSensesDict:
    print q
    print len( queriesSensesDict[q])
    for s in queriesSensesDict[q]:
      print queriesSensesDict[q][s]
      print
  """
  
  writeStatsClustering(queriesSensesDict)

  #print utilities.getDictString(queriesSensesDict)
  #print queriesSensesDict.keys()

  print "%d docs in docVectorList" % len(docVectorDict.keys())

  similaritiesWriter.write_similarities_to_CSV(similaritiesFileName, queriesSensesDict, docVectorDict, queries, contextWords, raw_queries, variancePerTerm)
 

def supervised_similarities(variancePerTerm=False):

  similaritiesFileName = 'similarities.csv'

  (docList, queryWords, queries, raw_queries) = getDocs(loadFileName="alldocs.dat")

  (queryVectorDict, docVectorDict, contextWords) = makeVectors(queryWords, docList, variancePerTerm)

  print "%d docs in docVectorDict" % len(docVectorDict.keys())

  writeStatsOccurrences(queryVectorDict)

  (queriesSensesDict, contextWords) = supervised.get_senses(queryWords)

  
  """
  for  q in queriesSensesDict:
    print q
    print len( queriesSensesDict[q])
    
    for s in queriesSensesDict[q]:
       print queriesSensesDict[q][s]
    #  print
  """
  writeStatsClustering(queriesSensesDict)


  similaritiesWriter.write_similarities_to_CSV(similaritiesFileName, queriesSensesDict, docVectorDict, queries, contextWords, raw_queries, True)


if __name__ == '__main__': #if this file is the argument to python
  parser = argparse.ArgumentParser(description='get the data for WSD', version='%(prog)s 1.0')
  parser.add_argument('automatic', type=str, help='get the data for WSD automatic or supervised. values: auto - supervised')
  parser.add_argument('variancePerTerm', type=str, help='Calculate variance per queryterm or not. values: true - false')

  args = parser.parse_args()
  kwargs = vars(args)
  auto = kwargs['automatic']
  variance = kwargs['variancePerTerm']



  if auto == 'auto':
    if variance == 'true':
      automatic_similarities(True)
    elif variance == 'false':
      automatic_similarities(False)
    else:
      print 'invalid input for the parameter for using variance per term or not'
  elif auto == 'supervised':
    supervised_similarities()
  else:
    print 'invalid input for automatic vs supervised parameter'






