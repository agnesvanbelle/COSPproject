from collections import defaultdict
import threading
import time
import multiprocessing
import sys
import heapq
import copy
import pprint

import docreader
import utilities
from docreader import Doc # needed for pickling call

# Extract term counts from a given set of documents
#
# The counts are of types:
# w_i -> q_j_k -> count
# d_i -> q_j -> w_l -> count
# and
# w_i -> q_j-> count (added for the computation of the variance per w_i, in DocCounter)
#
# Note: this class inherits the thread class and is intended to be evoked as
# a thread by DocCounter
class DocCounterWorker(threading.Thread):

  docCount = 0

  def __init__(self, documents, query_words, document_window_size=10, dsm_window_size=10):

    threading.Thread.__init__(self)

    self.documents = documents
    self.q_words = query_words
    self.d_window = document_window_size
    self.q_window = dsm_window_size
    self.q_word_instances = defaultdict(lambda : defaultdict(lambda : defaultdict(int))) # w_i -> q_j -> k -> count
    self.doc_representations = defaultdict(lambda : defaultdict(lambda : defaultdict(int))) # d_i -> q_j -> w_l -> count
    self.totalOccurrencePerQueryWord = defaultdict(lambda: defaultdict(int)) # wi -> qj -> count

  def run(self):
    self.make_representations()

  def make_representations(self):

    for doc in self.documents:
      content = doc.mainContent
      doc_id = doc.ID
      d_length = len(content)
      for i in range(d_length):
        word = content[i]
        # If a query word is encountered
        if word in self.q_words:
          # Process context
          d_context = content[max(0, i-self.d_window):i] + content[i+1: min(i+1+self.d_window, d_length+1)]
          q_context = content[max(0, i-self.q_window):i] + content[i+1: min(i+1+self.q_window, d_length+1)]
          for w in d_context:
            self.doc_representations[doc_id][word][w] +=1 # d_i -> q_j -> w_l -> count

          occurrence_id = len(self.q_word_instances[w][word]) #occurance instance of query word
          for w in q_context:
            self.q_word_instances[w][word][occurrence_id]+=1    # w_i -> q_j -> k -> count
            self.totalOccurrencePerQueryWord[w][word] += 1 # wi -> qj -> count

      DocCounterWorker.docCount += 1
      if DocCounterWorker.docCount % 1000 == 0:
        print "%d docs  processed." % (DocCounterWorker.docCount + 1)

  def get_representations(self):
    return (self.q_word_instances, self.doc_representations, self.totalOccurrencePerQueryWord)


# Extract term counts from all documents
# that the given DocReader object can read (optional maxLimit in constructor)
#
# The steps are:
# 1. extract count dictionaries
#       w_i -> q_j_k -> count
#       d_i -> q_j -> w_l -> count
#       and
#       w_i -> q_j-> count (added for the computation of the variance per w_i)
#
# 2. let only k (`maxContextWords', can be given in constructor) context words w_i remain
#     the k ones with the highest variance over queries (per query, NOT per query *instance*)
#     in
#     w_i -> q_j_k -> count
#     d_i -> q_j -> w_l -> count
#
# 3. convert:
#     w_i -> q_j_k -> count  to q_j_k -> w_i -> count
#
class DocCounter(object):

  def __init__(self,  queryWords, variancePerTerm = False, maxContextWords = 50, nrDocsToReadLimit=sys.maxint, docReaderManager=None, docFileName=None, docList=None):
    self.nrProcessors = multiprocessing.cpu_count()
    self.threads = [None]*self.nrProcessors
    self.docReaderManager = docReaderManager
    self.queryWords =  list(set(queryWords))
    self.nrDocsToReadLimit = nrDocsToReadLimit
    self.maxContextWords = maxContextWords # for dim. reduction
    self.docFileName = docFileName
    self.docList = docList
    self.variancePerTerm = variancePerTerm
    
    self.querySensesDict = None
    self.docInstancesDict = None
    self.finalContextWords = None

    
    
  # return the query sense dict
  # q_j -> k -> w_i -> count  (k = occurrance nr. of query word)
  def getQuerySensesDict(self):

    if self.querySensesDict == None:
      self.calcCounts()

    return self.querySensesDict

  # return query instances dict (per doc)
  # d_i -> q_j -> w_k -> count
  def getDocInstancesDict(self):
    if self.docInstancesDict == None:
      self.calcCounts()

    return self.docInstancesDict

  # calculate
  #
  # d_i -> q_j -> w_k -> count (query instances dict (per doc))
  # and
  # q_j -> k -> w_i -> count (query sense dict)
  #
  # get raw counts per thread
  # merge  the results of the threads
  # dimensionality reduction
  # re-representing the w->q format of contexWordDict to q->w format
  # normalize each vector per query sense/instance to probability distribution
  #
  # finally, makes attributes of them
  # @see self.getQuerySensesDict and self.getDocInstancesDict
  def calcCounts(self):

    (contextWordDictsList, docRepresentationsDictList, totalContextWordCountsDictList) = self.getRawCounts()

    (contextWordDict, contextWordTotalDict, docRepresentationsDict) = self.mergeContextWordDicts(contextWordDictsList, totalContextWordCountsDictList, docRepresentationsDictList)

    # cwList =  list of context words remained
    if not self.variancePerTerm:
      (contextWordDict, docRepresentationsDict, cwList) =  self.dimReduction(contextWordDict, contextWordTotalDict, docRepresentationsDict)
    else:
      (contextWordDict, docRepresentationsDict, cwList_all) =  self.dimReduction_separate(contextWordDict, contextWordTotalDict, docRepresentationsDict)
    
    
    #print "len(contextWordDict): %d " % len(contextWordDict)
    
    
    
    contextWordDict = self.turnAround(contextWordDict)

    print "len(contextWordDict): %d " % len(contextWordDict)
    
    self.normalizeToProbs(contextWordDict, docRepresentationsDict)
         
    self.querySensesDict = contextWordDict
    self.docInstancesDict = docRepresentationsDict
    
    if not self.variancePerTerm:
      self.finalContextWords = cwList
    else:
      self.finalContextWords = cwList_all
      
  # get list of documents (limit = self.nrDocsToReadLimit)
  # using DocReader attribute object
  def getSomeDocs(self) :
    
    if self.docList != None:
      return self.docList
    elif self.docReaderManager != None:
      return self.docReaderManager.getDocs(self.docFileName)
    else:
      return []


  # get the raw counts needed to later
  # compute the query sense vectors
  # and the document instances vectors
  # using DocCounterWorker attribute object
  # as thread, returns a list with results per thread
  #
  # w_i -> q_j_k -> count (contextWordDictsList)
  # d_i -> q_j -> w_l -> count (docRepresentationsDict)
  # and
  # w_i -> q_j-> count (totalContextWordCountsDictList) (added for the computation of the variance per w_i)
  #
  # !returned as a list the size of the number of threads!
  def getRawCounts(self):

    docList = self.getSomeDocs()

    print "len(docList): %d " % len(docList)

    contextWordDictsList = []
    totalContextWordCountsDictList = []
    docRepresentationsDictList = []

    nrDocs = len(docList)
    start = 0
    interval = nrDocs / self.nrProcessors
    end = start + interval

    print "Start counting. Using %d threads." % self.nrProcessors

    for i in range(0, self.nrProcessors) :
      if (i == (self.nrProcessors-1)):
        end = nrDocs

      docsSubset = docList[start:end+1]

      print "len(docsSubset): %d " % len(docsSubset)

      self.threads[i] = DocCounterWorker( docsSubset, self.queryWords)

      start = end + 1
      end = end + interval

    for t in self.threads:
      t.start()

    for t in self.threads:
      t.join()

    print "Done counting."

    for t in self.threads:
      (contextWordsToQueries, docRepresentationsDict, totalOccurrencePerQueryWord) = t.get_representations()
      print "contextWordsToQueries len: %d" % len(contextWordsToQueries)
      print "docrepr. len: %s" % len(docRepresentationsDict)
      print "totalOccurrencePerQueryWord len: %s " % len(totalOccurrencePerQueryWord)
      
      contextWordDictsList.append(contextWordsToQueries)
      totalContextWordCountsDictList.append(totalOccurrencePerQueryWord)
      docRepresentationsDictList.append(docRepresentationsDict)

    return (contextWordDictsList, docRepresentationsDictList, totalContextWordCountsDictList)


  # normalize counts per query sense/instance to probabilities
  def normalizeToProbs(self, contextWordDict, docRepresentationsDict):

    for q in contextWordDict:
      for occurrence in contextWordDict[q]:
        counter = 0
        for w in contextWordDict[q][occurrence]:
          counter += contextWordDict[q][occurrence][w]

        for w in contextWordDict[q][occurrence]:
          contextWordDict[q][occurrence][w] = contextWordDict[q][occurrence][w] / float(counter)

      for d in docRepresentationsDict:
        if q in docRepresentationsDict[d]:
          counter = 0
          for w in docRepresentationsDict[d][q]:
            counter += docRepresentationsDict[d][q][w]
          if counter > 0:
            for w in docRepresentationsDict[d][q]:
              docRepresentationsDict[d][q][w] = docRepresentationsDict[d][q][w] / float(counter)

 
              
  # re-representing the w->q format of contexWordDict to q->w format
  # for the query sense dict
  def turnAround(self, contextWordDict):

    newContextWordDict  = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))

    for w in contextWordDict:
      for q in contextWordDict[w]:
        for occurrence in contextWordDict[w][q]:
          newContextWordDict[q][occurrence][w] = contextWordDict[w][q][occurrence]

    del contextWordDict

    return newContextWordDict

  
  # merge raw counts divided over threads
  # @see self.getRawCounts
  def mergeContextWordDicts(self, listDicts, listDictsTotal, listDocDicts):
    smallestLen = sys.maxint
    smallest = -1
    smallestDict = None

    # find smallest dict to loop over
    for i in range(0, len(listDicts)):
      d = listDicts[i]
      l = len(d)
      if l > 0 and l < smallestLen:
        smallesLen = l
        smallest = i

    smallestDict = listDicts[smallest]
    smallestDictTotal = listDictsTotal[smallest]

    listDicts.pop(smallest)

    # merge them
    newDict = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    newTotalDict = defaultdict(lambda: defaultdict(int)) # wi -> qj -> count
    newDocDict = defaultdict(lambda : defaultdict(lambda : defaultdict(int))) # d_i -> q_j -> w_l -> count

    for wi, qj_k_count in smallestDict.iteritems():
      newDict[wi] = smallestDict[wi]
      newTotalDict[wi] = smallestDictTotal[wi]

      for otherDict in listDicts:

        for queryWord, occurrence_id_dict in otherDict[wi].iteritems():
          for occurrence_id, value in occurrence_id_dict.iteritems():

            start_new_occ = len(newDict[wi][queryWord])

            newDict[wi][queryWord][start_new_occ] += value

            newTotalDict[wi][queryWord] += value


    for docDict in listDocDicts:
      print "len docDict in listDocDicts: %d" %  len(docDict)
      for docKey in docDict:
        newDocDict[docKey] = docDict[docKey]

    return (newDict, newTotalDict, newDocDict)

  # same as dimReduction but contextwords with highest varaiance
  # are determined per query term
  def dimReduction_separate(self, contextWordDict, contextWordTotalDict, docRepresentationsDict):
    
    print "dimReduction_separate"
    
    cwList_all = self.getContextWordsLargestVariance_separate( contextWordDict)

    print "got cwList_all"
    
    newContextWordDict  = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    newDocRepresentationsDict = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))

    #print utilities.getDictString(cwList_all)
    
    
    for query in cwList_all:
      
      print query
      print len(cwList_all[query])
      
      for k in cwList_all[query]:

        newContextWordDict[k][query] = copy.deepcopy(contextWordDict[k][query])

        # perhaps this will be slow
        for doc in docRepresentationsDict:
          for queryWord in docRepresentationsDict[doc]:
            newDocRepresentationsDict[doc][queryWord][k] = copy.deepcopy(docRepresentationsDict[doc][queryWord][k])

    del contextWordDict
    del docRepresentationsDict

    return (newContextWordDict, newDocRepresentationsDict, cwList_all)


  #@see self.dimReduction_seperate
  def getContextWordsLargestVariance_separate(self, contextWordDict):
    
    cwList = defaultdict(list)
    
    for queryWord in self.queryWords:
      
      print queryWord
      
      heap = []
      
      smallestVariance = sys.maxint
      
      #print "\n\nqueryWord: %s" % queryWord
      
      for contextWord in contextWordDict:
        l = []
        nr_occ = len(contextWordDict[contextWord][queryWord])
        
        #if nr_occ == 1:
        #   sys.stdout.write(contextWord + ':' + ('%1.4f' % 1) + ', ')
        
        if nr_occ > 0:
          
          #print "contextWord:%s, queryWord:%s, nr_occ: %d" % (contextWord, queryWord, nr_occ)
          
          for occ, freq in contextWordDict[contextWord][queryWord].iteritems():
            l.append(freq)

          total = sum(l)
          avg = total / float(nr_occ)
          variance = utilities.variance(avg, l, nr_occ)
          #print variance

          if len(heap) < self.maxContextWords:
            heapq.heappush(heap, (variance, contextWord))
            if variance < smallestVariance :
              smallestVariance = variance

          else :
            if variance > smallestVariance:
              heapq.heappushpop(heap, (variance, contextWord))
              smallestVariance = heap[0][0]
  
      #print "len(heap): %d" % len(heap)
      
      while heap:
        cw = heapq.heappop(heap) # order: small to large
        #sys.stdout.write(cw[1] + ':' + ('%1.4f' % cw[0]) + ', ')
        cwList[queryWord].append( cw[1] )

    return cwList


  # dimensionality reduction of the nr. of context words
  # keep the self.maxContextWords ones with highes variance
  #
  # currently for both query sense vectors (contextWordDict) as well as
  # document instance vectors (docRepresentationsDict)
  def dimReduction(self, contextWordDict, contextWordTotalDict, docRepresentationsDict):
    cwList = self.getContextWordsLargestVariance( contextWordTotalDict)

    newContextWordDict  = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    newDocRepresentationsDict = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))

    for k in cwList:

      newContextWordDict[k] = copy.deepcopy(contextWordDict[k])

      # perhaps this will be slow
      for doc in docRepresentationsDict:
        for queryWord in docRepresentationsDict[doc]:
          newDocRepresentationsDict[doc][queryWord][k] = copy.deepcopy(docRepresentationsDict[doc][queryWord][k])

    del contextWordDict
    del docRepresentationsDict

    return (newContextWordDict, newDocRepresentationsDict, cwList)


  #@see self.dimReduction
  def getContextWordsLargestVariance(self, contextWordTotalDict):
    heap = []
    cwList = []

    nrQueryWords = len(self.queryWords)
    smallestVariance = sys.maxint

    for contextWord, queryDict in contextWordTotalDict.iteritems():
      l = []
      for queryWord in self.queryWords:
        l.append(queryDict[queryWord])

      total = sum(l)
      avg = total / float( nrQueryWords)
      variance = utilities.variance(avg, l, nrQueryWords)
      #print variance

      if len(heap) < self.maxContextWords:
        heapq.heappush(heap, (variance, contextWord))
        if variance < smallestVariance :
          smallestVariance = variance

      else :
        if variance > smallestVariance:
          heapq.heappushpop(heap, (variance, contextWord))
          smallestVariance = heap[0][0]

    while heap:
      cw = heapq.heappop(heap) # order: small to large
      cwList.append( cw[1] )

    return cwList

def getQueriesAndQuerySensesDictAndCW():
  docFileNames  = utilities.getFileNames("Data_dummy/collection2")

  drm = docreader.DocReaderManager(docFileNames , "stopwords.txt")


  queries = docreader.readQueries("Data_dummy/original_topics.txt")
  print queries
  queryWords = docreader.queriesToTermList(queries)



  dcm = DocCounter(docReaderManager=drm, queryWords=queryWords, docFileName="alldocs.dat")
  queryDict = dcm.getQuerySensesDict()
  cw = dcm.finalContextWords

  return (queryWords, queryDict, cw)

#169 478 docs
def run() :
  docFileNames  = utilities.getFileNames("Data_dummy/collection2")

  drm = docreader.DocReaderManager(docFileNames , "stopwords.txt")


  queries = docreader.readQueries("Data_dummy/original_topics.txt")
  queryWords = docreader.queriesToTermList(queries)

  print queryWords



  dcm = DocCounter(queryWords, docReaderManager=drm, docFileName="alldocs.dat")
  queryDict = dcm.getQuerySensesDict()
  docDict =  dcm.getDocInstancesDict()

  print utilities.getDictString( queryDict)
  #print utilities.getDictString( docDict)

if __name__ == '__main__': #if this file is the argument to python
  run()
