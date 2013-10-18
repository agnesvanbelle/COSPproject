from collections import defaultdict
import threading
import time
import multiprocessing
import sys
import heapq
import copy


import docreader
import utilities

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
    self.q_word_instances = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    self.doc_representations = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
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
          #print "word: %s" % word
          d_context = content[max(0, i-self.d_window):i] + content[i+1: min(i+1+self.d_window, d_length+1)]
          #print "d_context: %s" % d_context
          q_context = content[max(0, i-self.q_window):i] + content[i+1: min(i+1+self.q_window, d_length+1)]
          #print "q_context: %s " % q_context
          for w in d_context:        
            self.doc_representations[doc_id][word][w] +=1 # d_i -> q_j -> w_l -> count
            
          occurrence_id = len(self.q_word_instances[w][word])
          for w in q_context:            
            self.q_word_instances[w][word][occurrence_id]+=1    # w_i -> q_j -> k -> count     
            self.totalOccurrencePerQueryWord[w][word] += 1 
          
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
#     d_i -> q_j -> w_l -> count (!!!! TODO)
#
# 3. convert: (!!!! TODO)
#     w_i -> q_j_k -> count  to q_j_k -> w_i -> count
#     
class DocCounter(object):
  
  def __init__(self, docReader, queryWords, maxContextWords = 50, nrDocsToReadLimit=sys.maxint):
    self.nrProcessors = multiprocessing.cpu_count()   
    self.threads = [None]*self.nrProcessors
    self.docReader = docReader
    self.queryWords = queryWords
    self.nrDocsToReadLimit = nrDocsToReadLimit
    self.maxContextWords = maxContextWords # for dim. reduction
    
  def getSomeDocs(self, limit = 10) :    
    d =  'meaningless init value'
    docList = []
    while d != None and limit > 0:
      d =  self.docReader.getNextDocFromFiles()
      if d != None:
        limit -= 1
        #print getDictString(d.fieldContents)
        #print d.mainContentnt
        #print d.ID
        docList.append(d)
    print "docReader.docCounter: %d" % self.docReader.docCounter
    return docList
  
  def getCounts(self):
    
    docList = self.getSomeDocs(self.nrDocsToReadLimit)
    contextWordDictsList = []
    totalContextWordCountsDictList = []
    
    nrDocs = len(docList)
    
    start = 0
    interval = nrDocs / self.nrProcessors
    end = start + interval    
    
    for i in range(0, self.nrProcessors) :
      if (i == (self.nrProcessors-1)):
        end = nrDocs
    
      docsSubset = docList[start:end]
      print "start: %d, end: %d" % (start,end)
      
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
      
      #print "\nqwordinstances: %s" % utilities.getDictString(contextWordsToQueries)
      #print "\ndocrepr: %s" % utilities.getDictString(docRepresentations)
      contextWordDictsList.append(contextWordsToQueries)
      totalContextWordCountsDictList.append(totalOccurrencePerQueryWord)
      
      #print contextWordsToQueries['year']['world']
      #print contextWordsToQueries['year']['franc']

    (contextWordDict, contextWordTotalDict) = self.mergeContextWordDicts(contextWordDictsList, totalContextWordCountsDictList)
    
    #print "contextWordDict len: %d " % len(contextWordDict)    
    print contextWordDict['year']['world']
    print contextWordDict['year']['franc']
    
    print contextWordTotalDict['year']['world']
    print contextWordTotalDict['year']['franc']
    
    self.dimReduction(contextWordDict, contextWordTotalDict, docRepresentationsDict)
    
    
    
  def mergeContextWordDicts(self, listDicts, listDictsTotal):
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
    
    for wi, qj_k_count in smallestDict.iteritems():
      newDict[wi] = smallestDict[wi]
      newTotalDict[wi] = smallestDictTotal[wi]
      
      for otherDict in listDicts:        
        
        for queryWord, occurrence_id_dict in otherDict[wi].iteritems():
          for occurrence_id, value in occurrence_id_dict.iteritems():
            
            start_new_occ = len(newDict[wi][queryWord])
            
            newDict[wi][queryWord][start_new_occ] += value
            
            newTotalDict[wi][queryWord] += value            
    
    return (newDict, newTotalDict)
    
  
  # TODO hier was ik gebleven
  def dimReduction(self, contextWordDict, contextWordTotalDict, docRepresentationsDict):
    cwList = self.getContextWordsLargestVariance( contextWordTotalDict)
    
    newContextWordDict  = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    
    for k in cwList:
      
      newContextWordDict[k] = copy.deepcopy(contextWordDict[k])
      
    del(contextWordDict)
     
    print len(newContextWordDict)
    
    print utilities.getDictString(newContextWordDict)
    
  
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
          smallestVariance = variance
          
    while heap:
      cw = heapq.heappop(heap) # order: small to large
      cwList.append( cw[1] ) 
    
    return cwList
    
    
#169 478 docs
def run() :
  docFileNames  = utilities.getFileNames("Data_dummy/collection")
  
  pp = docreader.Preprocessor("stopwords.txt")
  dr = docreader.DocReader(docFileNames , pp)
  
  
  queries = docreader.readQueries("Data_dummy/original_topics.txt")
  queryWords = docreader.queriesToTermList(queries)
  
  print queryWords
  
  

  dcm = DocCounter(dr, queryWords)
  dcm.getCounts()
  
if __name__ == '__main__': #if this file is the argument to python
  run()
