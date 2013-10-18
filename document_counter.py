from collections import defaultdict
import threading
import time
import multiprocessing
import sys

import docreader
import utilities

class DocCounter(threading.Thread):
  
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
            self.doc_representations[doc_id][word][w] +=1 # d_i -> q_j -> count
            
          occurrence_id = len(self.q_word_instances[w][word])
          for w in q_context:            
            self.q_word_instances[w][word][occurrence_id]+=1    # w_i -> q_j -> k -> count     
            self.totalOccurrencePerQueryWord[w][word] += 1 
          
      DocCounter.docCount += 1
      if DocCounter.docCount % 1000 == 0:
        print "%d docs  processed." % (DocCounter.docCount + 1)
        
  def get_representations(self):
    return (self.q_word_instances, self.doc_representations, self.totalOccurrencePerQueryWord)
    
    
class DocCounterManager(object):
  
  def __init__(self, docReader, queryWords, nrDocsToReadLimit=sys.maxint):
    self.nrProcessors = multiprocessing.cpu_count()   
    self.threads = [None]*self.nrProcessors
    self.docReader = docReader
    self.queryWords = queryWords
    self.nrDocsToReadLimit = nrDocsToReadLimit
   
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
      
      self.threads[i] = DocCounter( docsSubset, self.queryWords)    
            
      start = end + 1
      end = end + interval

    for t in self.threads:
      t.start()
        
    for t in self.threads:
      t.join()
      
    print "Done counting."
    
    
    for t in self.threads:
      (contextWordsToQueries, docRepresentations, totalOccurrencePerQueryWord) = t.get_representations()
      print "contextWordsToQueries len: %d" % len(contextWordsToQueries)
      print "docrepr. len: %s" % len(docRepresentations)
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
    
    
    self.dimensionalityReduction(contextWordDict, contextWordTotalDict)
    
  def mergeContextWordDicts(self, listDicts, listDictsTotal):
    smallestLen = sys.maxint
    smallest = -1
    smallestDict = None
    
    for i in range(0, len(listDicts)):
      d = listDicts[i]
      l = len(d)
      if l > 0 and l < smallestLen:
        smallesLen = l
        smallest = i
    
    smallestDict = listDicts[smallest]
    smallestDictTotal = listDictsTotal[smallest]
    
    listDicts.pop(smallest)
    
    
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
            
            """
            #if value > 0 and wi == 'polic':
            if True:
              print "queryWord: %s" % queryWord
              print "newDict[wi][queryWord]: %s" % newDict[wi][queryWord]              
              print "start_new_occ: %d" % start_new_occ
              print "occurrence_id otherDict: %s"  % occurrence_id
              #print "otherDict[wi][queryWord]: %s " % otherDict[wi][queryWord]
            """
            
          
        
    
    return (newDict, newTotalDict)
    
  # TODO: keep track of k largest-variance-having contetx words
  def dimensionalityReduction(self, contextWordDict, contextWordTotalDict):
    variancePerContextWord = defaultdict(float)
    
    nrQueryWords = len(self.queryWords)
    
    for contextWord, queryDict in contextWordTotalDict.iteritems():
      l = []
      for queryWord in self.queryWords:
        l.append(queryDict[queryWord])
        
      total = sum(l)
      avg = total / float( nrQueryWords)
      
      variance = utilities.variance(avg, l, nrQueryWords) 
      #print variance
      
  
    
#169 478 docs
def run() :
  docFileNames  = utilities.getFileNames("Data_dummy/collection")
  
  pp = docreader.Preprocessor("stopwords.txt")
  dr = docreader.DocReader(docFileNames , pp)
  
  
  queries = docreader.readQueries("Data_dummy/original_topics.txt")
  queryWords = docreader.queriesToTermList(queries)
  
  print queryWords
  
  

  dcm = DocCounterManager(dr, queryWords)
  dcm.getCounts()
  
if __name__ == '__main__': #if this file is the argument to python
  run()
