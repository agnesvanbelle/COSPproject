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

statsDir = 'stats'

'''
Writes clusters to file
'''
def writeClusters(queriesSensesDict):
  try:
    f = open(statsDir + "/clusterresults.txt", "w")
    try:
      for  q in queriesSensesDict:
        f.write( '\n'+ q + '\n')
        f.write (str(len( queriesSensesDict[q])) + '\n')
        for s in queriesSensesDict[q]:
          f.write( str(queriesSensesDict[q][s])  + '\n\n')
     
    finally:
      f.close()
  except IOError:
    pass

'''
write statistics about occurrences to file
'''    
def writeStatsOccurrences(queryVectorDict) :
  try:
    f = open(statsDir + "/occstats.txt", "w")
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

'''
Writes statistics about the resulting automatically generated word senses to file
'''    
def writeStatsClustering(queriesSensesDict) :
  try:
    f = open(statsDir + "/clusterstats.txt", "w")
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

'''
Writes statistics about the document to a file
'''    
def writeDocStats(docList, queryWords):
  total=0.0
  for d in docList:
    total += len(d.mainContent)
  avgLen = total / float(len(docList))

  try:
    f = open(statsDir + "/avgdoclen.txt", "w")
    try:
      f.write('nr docs: ' + str(len(docList)) + '\n')
      f.write('avgdoclen: ' + str(avgLen) + '\n')
      
      f.write('nr queries: ' + str(len(queryWords)) + '\n')

      for q in queryWords:        
        f.write( str(q) + '\n')
    finally:
      f.close()
  except IOError:
    pass
  print "avgLen: %2.2f" % avgLen


'''
Calls the right functions to parse the documents
'''
def getDocs(loadFileName=None, saveFileName=None):

  drm = docreader.DocReaderManager(docFileNames , stopwordsFile)
  docList = drm.getDocs(loadFileName)

  if saveFileName != None:
    drm.saveDocs(saveFileName)

  queries = docreader.readQueries(topicFile)
  queryWords = docreader.queriesToTermList(queries)
  queriesList = docreader.processedQueries(queries)

  return (docList, queryWords, queriesList, queries)

'''
Calls the right functions to get the vector representations of documents, query occurrences and the used context words
'''
def makeVectors(queryWords, docList, vpt):


  dcm = document_counter.DocCounter(queryWords=queryWords, docList=docList, maxContextWords=50, variancePerTerm=vpt)

  queryDict = dcm.getQuerySensesDict()
  docDict =  dcm.getDocInstancesDict()
  contextWords = dcm.finalContextWords
  
  return (queryDict, docDict, contextWords)

'''
Calls the right clustering functions
'''
def clusterQueryVectors(queryWords, allContextWords, queryVectorDict, variancePerTerm):

  k_values = range(2,7)

  scm = clustering.SenseClusterManager(queryWords, queryVectorDict, allContextWords, k_values, variancePerTerm)

  scm.cluster()

  queriesSensesDict = scm.getResult()

  return queriesSensesDict
  
'''
Calculates query term - document similarities using automatically generated word senses
'''
def automatic_similarities(variancePerTerm=False):
  similaritiesFileName = 'similarities.csv'

  (docList, queryWords, queries, raw_queries) = getDocs(loadFileName="alldocs2.dat")

  writeDocStats(docList, queryWords)

  (queryVectorDict, docVectorDict, contextWords) = makeVectors(queryWords, docList, variancePerTerm)

  
  writeStatsOccurrences(queryVectorDict)

      
  queriesSensesDict = clusterQueryVectors(queryWords, contextWords, queryVectorDict, variancePerTerm)

  
  writeStatsClustering(queriesSensesDict)
  writeClusters(queriesSensesDict)

  similaritiesWriter.write_similarities_to_CSV(similaritiesFileName, queriesSensesDict, docVectorDict, queries, contextWords, raw_queries, variancePerTerm)
 
'''
Calculates query term - document similarities using supervised word senses
'''
def supervised_similarities(variancePerTerm=False):

  similaritiesFileName = 'similarities.csv'

  (docList, queryWords, queries, raw_queries) = getDocs(loadFileName="alldocs2.dat")

  writeDocStats(docList, queryWords)
  
  (queryVectorDict, docVectorDict, contextWords) = makeVectors(queryWords, docList, variancePerTerm)


  writeStatsOccurrences(queryVectorDict)

  (queriesSensesDict, contextWords) = supervised.get_senses(queryWords)


  writeStatsClustering(queriesSensesDict)
  writeClusters(queriesSensesDict)

  similaritiesWriter.write_similarities_to_CSV(similaritiesFileName, queriesSensesDict, docVectorDict, queries, contextWords, raw_queries, True)

'''
Parses arguments and calls the right functions according to parameters
'''
if __name__ == '__main__': #if this file is the argument to python
  parser = argparse.ArgumentParser(description='get the data for WSD', version='%(prog)s 1.0')
  parser.add_argument('automatic', type=str, help='get the data for WSD automatic or supervised. values: auto - supervised')
  parser.add_argument('variancePerTerm', type=str, help='Calculate variance per queryterm or not. values: true - false')

  args = parser.parse_args()
  kwargs = vars(args)
  auto = kwargs['automatic']
  variance = kwargs['variancePerTerm']

  utilities.makeDir(statsDir)

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






